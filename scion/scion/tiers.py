"""The checkout architecture: scion-daemon → scion-cache → scion-server.

All three answer the identical ``get_objects`` RPC, so a client never needs to know the cache
topology.  Each tier accepts object requests only from the tier directly below it, which isolates
failure domains: a misbehaving regional cache cannot be bypassed by thousands of daemons hitting
the servers directly.

* ``scion-daemon``: one per node.  Clients reach it over a Unix socket.  It keeps a bounded
  on-disk store shared by every job on the node, starts from a periodically refreshed snapshot,
  and talks only to its regional caches.
* ``scion-cache``: regional, in memory.  It serves stored bytes as-is, with no negotiation
  ("what does the client already have?") and no delta compression.  Misses go to the
  authoritative servers.
* ``scion-server``: authoritative.  It reads blob storage and enforces directory ACLs.

Objects under read-restricted directories are flagged by the server and never cached by
intermediate tiers.  Every request for them reaches the server, which checks the end user's
permissions.
"""
from __future__ import annotations

import itertools
import json
import os
import threading
from collections import Counter

from .objects import decode_stored
from .repo import F_DENIED, F_MISSING, F_RESTRICTED
from .rpc import RemoteError, RpcClient, Service, pack_objects
from .snapshot import latest_snapshot, load_snapshot
from .storage import BoundedFileObjectStore, MemoryObjectStore, ObjectStore

MAX_IDS_PER_REQUEST = 2000


class ObjectSource:
    def fetch(self, ids: list[str], user: str | None) -> list[tuple[str, int, bytes]]:
        raise NotImplementedError


class RepositorySource(ObjectSource):
    def __init__(self, repo):
        self.repo = repo

    def fetch(self, ids, user):
        return self.repo.fetch_objects(ids, user)


class RemoteSource(ObjectSource):
    """Talks to one or more upstream endpoints of the next tier, with round-robin and failover."""

    def __init__(self, urls: list[str], principal: str, tier: str, token: str | None = None):
        if not urls:
            raise ValueError("at least one upstream is required")
        self.clients = [RpcClient(u, user=principal, token=token, tier=tier, retries=1) for u in urls]
        self._rr = itertools.count()
        self.failovers = 0

    def fetch(self, ids, user):
        out = []
        for i in range(0, len(ids), MAX_IDS_PER_REQUEST):
            out.extend(self._fetch_batch(ids[i:i + MAX_IDS_PER_REQUEST], user))
        return out

    def _fetch_batch(self, ids, user):
        start = next(self._rr)
        last_exc: Exception | None = None
        for k in range(len(self.clients)):
            client = self.clients[(start + k) % len(self.clients)]
            try:
                return client.get_objects(ids, on_behalf=user)
            except RemoteError as e:
                if e.status < 500:
                    raise
                last_exc = e
            except OSError as e:
                last_exc = e
            self.failovers += 1
        raise last_exc  # type: ignore[misc]


class CachingSource(ObjectSource):
    """A read-through cache in front of an upstream source.  Concurrent misses for the same
    object are collapsed into a single upstream request (single-flight)."""

    def __init__(self, store: ObjectStore, upstream: ObjectSource, verify: bool = False):
        self.store = store
        self.upstream = upstream
        self.verify = verify
        self.restricted: set[str] = set()
        self._inflight: dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self.counters: Counter = Counter()

    def fetch(self, ids, user):
        result: dict[str, tuple[int, bytes]] = {}
        owned: list[str] = []
        forward: list[str] = []
        waits: list[tuple[str, threading.Event]] = []
        for oid in dict.fromkeys(ids):
            if oid in self.restricted:
                forward.append(oid)
                self.counters["restricted_passthrough"] += 1
                continue
            stored = self.store.get_stored(oid)
            if stored is not None:
                result[oid] = (0, stored)
                self.counters["hits"] += 1
                self.counters["bytes_served"] += len(stored)
                continue
            self.counters["misses"] += 1
            with self._lock:
                ev = self._inflight.get(oid)
                if ev is None:
                    self._inflight[oid] = threading.Event()
                    owned.append(oid)
                else:
                    waits.append((oid, ev))
        try:
            if owned or forward:
                self.counters["upstream_requests"] += 1
                for oid, flags, stored in self.upstream.fetch(owned + forward, user):
                    if flags & (F_MISSING | F_DENIED):
                        result[oid] = (flags, b"")
                        continue
                    if self.verify:
                        decode_stored(stored, expected_id=oid)
                    if flags & F_RESTRICTED:
                        self.restricted.add(oid)  # never cache, always re-authorize upstream
                    else:
                        self.store.put_stored(oid, stored, verify=False)
                    result[oid] = (flags, stored)
                    self.counters["bytes_fetched"] += len(stored)
        finally:
            with self._lock:
                for oid in owned:
                    ev = self._inflight.pop(oid, None)
                    if ev is not None:
                        ev.set()
        retry = []
        for oid, ev in waits:
            ev.wait(60)
            stored = self.store.get_stored(oid)
            if stored is not None:
                result[oid] = (0, stored)
                self.counters["coalesced"] += 1
            else:
                retry.append(oid)
        if retry:
            for oid, flags, stored in self.upstream.fetch(retry, user):
                result[oid] = (flags, stored)
        return [(oid, *result[oid]) for oid in ids]

    COUNTERS = ("hits", "misses", "coalesced", "upstream_requests", "restricted_passthrough",
                "bytes_served", "bytes_fetched")

    def stats(self) -> dict:
        c = {k: self.counters.get(k, 0) for k in self.COUNTERS}
        lookups = c.get("hits", 0) + c.get("misses", 0)
        c["hit_rate"] = round(c.get("hits", 0) / lookups, 5) if lookups else None
        c["objects_cached"] = len(self.store) if hasattr(self.store, "__len__") else None
        c["bytes_cached"] = getattr(self.store, "size_bytes", None)
        c["evictions"] = getattr(self.store, "evictions", 0)
        c["restricted_ids"] = len(self.restricted)
        return c


def _ids_cost(params) -> float:
    try:
        return float(len(params.get("ids", [])))
    except AttributeError:
        return 1.0


class ObjectTierService(Service):
    """A cache or daemon: serves ``get_objects`` from a CachingSource."""

    def __init__(self, tier: str, source: CachingSource, allowed_callers: tuple[str, ...], policy=None,
                 verbose: bool = False):
        super().__init__(policy=policy, verbose=verbose)
        self.tier = tier
        self.source = source
        self.register("get_objects", self._get_objects, klass="objects", binary_out=True,
                      tiers=allowed_callers, cost=_ids_cost)
        self.register("tier_info", lambda c, p: {"tier": self.tier, "allowed_callers": list(allowed_callers)})

    def _get_objects(self, caller, params):
        ids = params["ids"]
        if len(ids) > MAX_IDS_PER_REQUEST:
            raise ValueError(f"at most {MAX_IDS_PER_REQUEST} ids per request")
        return pack_objects(self.source.fetch(ids, caller.user))

    def stats(self) -> dict:
        s = super().stats()
        s["cache"] = self.source.stats()
        return s


def make_cache_service(upstreams: list[str], max_bytes: int, token: str | None = None,
                       policy=None, allowed_callers=("daemon",), verbose=False) -> ObjectTierService:
    upstream = RemoteSource(upstreams, principal="scion-cache", tier="cache", token=token)
    source = CachingSource(MemoryObjectStore(max_bytes), upstream)
    return ObjectTierService("cache", source, tuple(allowed_callers), policy=policy, verbose=verbose)


class DaemonService(ObjectTierService):
    def __init__(self, store_dir: str, upstreams: list[str], max_bytes: int,
                 snapshot_dir: str | None = None, refresh_seconds: float = 300.0,
                 token: str | None = None, policy=None, allowed_callers=("client",), verbose=False):
        upstream = RemoteSource(upstreams, principal="scion-daemon", tier="daemon", token=token)
        store = BoundedFileObjectStore(store_dir, max_bytes)
        # The daemon verifies every object it receives: it is what jobs consume.
        source = CachingSource(store, upstream, verify=True)
        super().__init__("daemon", source, tuple(allowed_callers), policy=policy, verbose=verbose)
        self.snapshot_dir = snapshot_dir
        self.refresh_seconds = refresh_seconds
        self.snapshot_loaded: str | None = None
        self.snapshot_objects = 0
        self._stop = threading.Event()
        if snapshot_dir:
            self.refresh_snapshot()
            threading.Thread(target=self._refresh_loop, daemon=True, name="snapshot-refresh").start()

    def refresh_snapshot(self) -> int:
        info = latest_snapshot(self.snapshot_dir) if self.snapshot_dir else None
        if not info or info["file"] == self.snapshot_loaded:
            return 0
        n = load_snapshot(os.path.join(self.snapshot_dir, info["file"]), self.source.store)
        self.snapshot_loaded = info["file"]
        self.snapshot_objects += n
        self.metrics.incr("snapshot.imported", n)
        return n

    def _refresh_loop(self):
        while not self._stop.wait(self.refresh_seconds):
            try:
                self.refresh_snapshot()
            except Exception as e:  # pragma: no cover - keep serving on a bad snapshot
                self.metrics.incr("snapshot.errors")
                print(f"scion-daemon: snapshot refresh failed: {e}")

    def stop(self):
        self._stop.set()

    def stats(self) -> dict:
        s = super().stats()
        s["snapshot"] = {"loaded": self.snapshot_loaded, "objects_imported": self.snapshot_objects}
        return s


def tier_stats_summary(stats: dict) -> str:
    c = stats.get("cache", {})
    return json.dumps({"tier": stats.get("tier"), "hit_rate": c.get("hit_rate"),
                       "hits": c.get("hits"), "misses": c.get("misses")})


__all__ = [
    "CachingSource",
    "DaemonService",
    "ObjectTierService",
    "RemoteSource",
    "RepositorySource",
    "make_cache_service",
]

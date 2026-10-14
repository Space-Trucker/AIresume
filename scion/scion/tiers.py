"""The checkout tiers: scion-daemon → scion-cache → scion-server (FR-TIER-*, ADR-05/06).

All three answer the identical ``get_objects`` RPC (FR-FP-05), so a client never needs to know the
topology. Each tier accepts object requests only from the tier directly below it (strict tiering,
FR-TIER-07), which keeps one tier's failure from overloading the next (NFR-08).

* ``scion-daemon``: one per node, reached over a Unix socket. A bounded on-disk store shared by
  every job on the node; warm-started from snapshots; talks only to regional caches.
* ``scion-cache``: regional and in memory. Serves stored bytes as they are, with no negotiation and
  no recompression (FR-FP-06). Misses go to the authoritative servers.

Objects are keyed by (repository, id) (ADR-13). Objects the server flags restricted are passed
through and never stored (ADR-06, FR-IAM-05); every request for them reaches the server, which
re-authorizes the end user. When a policy change makes objects a tier already holds uncacheable,
the repository's ACL epoch changes, and each tier purges that repository's objects the next time
it checks the epoch, at most ``epoch_seconds`` after the last check (ADR-20).
"""
from __future__ import annotations

import itertools
import json
import os
import threading
import time
from collections import Counter, OrderedDict

from .iam import Identity
from .objects import F_DENIED, F_MISSING, F_RESTRICTED, ObjectError, decode_stored, validate_repo_name
from .rpc import MAX_IDS_PER_REQUEST, ClientTls, RemoteError, RpcClient, RpcError, Service, ids_cost, pack_objects
from .snapshot import latest_snapshot, load_snapshot
from .storage import BoundedFileObjectStore, MemoryObjectStore, ObjectStore, ns_key

UPSTREAM_TIER = {"daemon": "cache", "cache": "server"}


class ObjectSource:
    def fetch(self, repo: str, ids: list[str], user: str | None) -> list[tuple[str, int, bytes]]:
        raise NotImplementedError


class RemoteSource(ObjectSource):
    """The next tier up: several endpoints with round-robin and failover (FR-TIER-09). Each
    endpoint must really be of the expected tier (FR-TIER-04): a daemon pointed at a server
    refuses to use it."""

    def __init__(self, urls: list[str], principal: str, tier: str, token: str | None = None,
                 tls: ClientTls | None = None, timeout: float = 60.0):
        if not urls:
            raise ValueError("at least one upstream endpoint is required")
        self.expect = UPSTREAM_TIER[tier]
        self.clients = [RpcClient(u, user=principal, token=token, tier=tier, tls=tls, timeout=timeout, retries=1)
                        for u in urls]
        self._checked: set[int] = set()
        self._rr = itertools.count()
        self.failovers = 0
        self.requests = 0

    def close(self) -> None:
        for c in self.clients:
            c.close_all()

    def _check_tier(self, i: int, client: RpcClient) -> None:
        if i in self._checked:
            return
        tier = client.call("tier_info").get("tier")
        if tier != self.expect:
            raise RpcError(502, "bad_upstream", f"upstream {client.url} is a {tier}, not a {self.expect}")
        self._checked.add(i)

    def fetch(self, repo, ids, user):
        out = []
        for i in range(0, len(ids), MAX_IDS_PER_REQUEST):
            out.extend(self._fetch_batch(repo, ids[i:i + MAX_IDS_PER_REQUEST], user))
        return out

    def _fetch_batch(self, repo, ids, user):
        return self._each(lambda client: client.get_objects(repo, ids, on_behalf=user))

    def acl_epochs(self, repos: list[str]) -> dict:
        return self._each(lambda client: client.call("acl_epochs", repos=repos))

    def _each(self, fn):
        start = next(self._rr)
        last: Exception | None = None
        for k in range(len(self.clients)):
            i = (start + k) % len(self.clients)
            client = self.clients[i]
            try:
                self._check_tier(i, client)
                self.requests += 1
                return fn(client)
            except RemoteError as e:
                if e.status < 500:
                    raise RpcError(e.status, e.code, str(e), e.data) from None
                last = e
            except OSError as e:
                last = e
            self.failovers += 1
        raise RpcError(503, "upstream_unavailable", f"no {self.expect} answered: {last}")


class EpochGuard:
    """Keeps what a tier holds consistent with each repository's ACL epoch (ADR-20).

    Before a tier serves a repository's objects, the epoch must have been checked upstream within
    ``interval`` seconds. When it changed, every object of that repository is purged first: some
    may no longer be cacheable. The last epochs seen can be saved, so a daemon restarted on its old
    disk store purges what it held under another epoch. If the upstream can't be reached, the tier
    keeps serving what it has and checks again a second later."""

    def __init__(self, fetch_epochs, purge, interval: float = 10.0, state_path: str | None = None):
        self.fetch_epochs, self.purge, self.interval, self.state_path = fetch_epochs, purge, interval, state_path
        self.epochs: dict[str, str | None] = {}
        if state_path and os.path.exists(state_path):
            try:
                with open(state_path) as f:
                    self.epochs = json.load(f)
            except (OSError, ValueError):
                self.epochs = {}  # unknown: everything held is purged at the first check
        self._checked: dict[str, float] = {}
        self._lock = threading.Lock()
        self.purges = 0
        self.check_failures = 0

    def ensure(self, repo: str) -> str | None:
        last = self._checked.get(repo)
        if last is not None and time.monotonic() - last < self.interval:
            return self.epochs.get(repo)
        with self._lock:  # one check at a time; the others then find it fresh
            last = self._checked.get(repo)
            if last is not None and time.monotonic() - last < self.interval:
                return self.epochs.get(repo)
            try:
                current = self.fetch_epochs([repo]).get(repo)
            except (RpcError, OSError):
                self.check_failures += 1
                self._checked[repo] = time.monotonic() - self.interval + min(1.0, self.interval)
                return self.epochs.get(repo)
            if repo not in self.epochs or current != self.epochs[repo]:
                self.purge(repo)
                self.purges += 1
                self.epochs[repo] = current
                self._save()
            self._checked[repo] = time.monotonic()
            return current

    def _save(self) -> None:
        if not self.state_path:
            return
        tmp = self.state_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.epochs, f)
        os.replace(tmp, self.state_path)


class CachingSource(ObjectSource):
    """A read-through cache in front of an upstream source (06 §6.7, object in a cache tier).
    Concurrent misses for one object become one upstream request (single flight, FR-TIER-10)."""

    COUNTERS = ("hits", "misses", "coalesced", "upstream_requests", "restricted_passthrough",
                "bytes_served", "bytes_fetched", "rejected_objects", "purged")

    MAX_RESTRICTED = 1_000_000

    def __init__(self, store: ObjectStore, upstream: ObjectSource, verify: bool = False,
                 guard: EpochGuard | None = None):
        self.store, self.upstream, self.verify, self.guard = store, upstream, verify, guard
        # Keys known to be restricted are always forwarded. The memory is bounded: a forgotten key
        # just takes one more ordinary miss, which the server flags restricted again.
        self.restricted: OrderedDict[str, None] = OrderedDict()
        self._inflight: dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self.counters: Counter = Counter()

    def _count(self, key: str, n: int = 1) -> None:
        with self._lock:
            self.counters[key] += n

    def purge(self, repo: str) -> None:
        """Forget everything held for one repository (ADR-20)."""
        prefix = repo + "/"
        with self._lock:
            for k in [k for k in self.restricted if k.startswith(prefix)]:
                del self.restricted[k]
        purge = getattr(self.store, "purge_namespace", None)
        if purge:
            self._count("purged", purge(repo))

    def fetch(self, repo, ids, user):
        if self.guard is not None:
            self.guard.ensure(repo)
        result: dict[str, tuple[int, bytes]] = {}
        owned, forward, waits = [], [], []
        for oid in dict.fromkeys(ids):
            key = ns_key(repo, oid)
            if key in self.restricted:
                forward.append(oid)
                self._count("restricted_passthrough")
                continue
            stored = self.store.get_stored(key)
            if stored is not None:
                result[oid] = (0, stored)
                self._count("hits")
                self._count("bytes_served", len(stored))
                continue
            self._count("misses")
            with self._lock:
                ev = self._inflight.get(key)
                if ev is None:
                    self._inflight[key] = threading.Event()
                    owned.append(oid)
                else:
                    waits.append((oid, ev))
        try:
            if owned or forward:
                self._count("upstream_requests")
                self._absorb(repo, self.upstream.fetch(repo, owned + forward, user), result)
        finally:
            with self._lock:
                for oid in owned:
                    ev = self._inflight.pop(ns_key(repo, oid), None)
                    if ev is not None:
                        ev.set()
        retry = []
        for oid, ev in waits:
            ev.wait(60)
            stored = self.store.get_stored(ns_key(repo, oid))
            if stored is not None:
                result[oid] = (0, stored)
                self._count("coalesced")
            else:
                retry.append(oid)  # restricted, denied or failed for the owner: ask for ourselves
        if retry:
            self._count("upstream_requests")
            self._absorb(repo, self.upstream.fetch(repo, retry, user), result)
        return [(oid, *result[oid]) for oid in ids]

    def _absorb(self, repo, items, result) -> None:
        for oid, flags, stored in items:
            if flags & (F_MISSING | F_DENIED):
                result[oid] = (flags, b"")
                continue
            if self.verify:
                try:
                    decode_stored(stored, expected_id=oid)  # FR-OBJ-04: every object is checked
                except ObjectError as e:
                    self._count("rejected_objects")
                    raise RpcError(502, "integrity", f"upstream sent a bad object {oid[:12]}: {e}") from None
            key = ns_key(repo, oid)
            if flags & F_RESTRICTED:
                with self._lock:  # never stored; every request is re-authorized upstream
                    self.restricted[key] = None
                    if len(self.restricted) > self.MAX_RESTRICTED:
                        self.restricted.popitem(last=False)
            else:
                self.store.put_stored(key, stored, verify=False)
            result[oid] = (flags, stored)
            self._count("bytes_fetched", len(stored))

    def stats(self) -> dict:
        with self._lock:
            c = {k: self.counters.get(k, 0) for k in self.COUNTERS}
        lookups = c["hits"] + c["misses"]
        c["hit_rate"] = round(c["hits"] / lookups, 5) if lookups else None
        c["objects_cached"] = len(self.store) if hasattr(self.store, "__len__") else None
        c["bytes_cached"] = getattr(self.store, "size_bytes", None)
        c["evictions"] = getattr(self.store, "evictions", 0)
        c["restricted_ids"] = len(self.restricted)
        if self.guard is not None:
            c["epoch_purges"] = self.guard.purges
            c["epoch_check_failures"] = self.guard.check_failures
        return c


class ObjectTierService(Service):
    """A cache or daemon: serves ``get_objects`` to the tier directly below it."""

    def __init__(self, tier: str, source: CachingSource, allowed_callers: tuple, identity: Identity | None = None,
                 verbose: bool = False):
        super().__init__(identity, verbose=verbose)
        self.tier, self.source, self.allowed_callers = tier, source, tuple(allowed_callers)
        self.register("get_objects", self._get_objects, klass="objects", binary_out=True,
                      tiers=self.allowed_callers, cost=ids_cost)
        self.register("tier_info", lambda c, p: {"tier": self.tier, "object_callers": list(self.allowed_callers)})
        self.register("acl_epochs", self._acl_epochs, tiers=self.allowed_callers)

    def _acl_epochs(self, caller, params):
        repos = params.get("repos")
        if not isinstance(repos, list) or len(repos) > 1000:
            raise ValueError("repos must be a list of at most 1000 names")
        guard = self.source.guard
        return {validate_repo_name(r): guard.ensure(r) if guard else None for r in repos}

    def _get_objects(self, caller, params):
        ids = params.get("ids")
        if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
            raise ValueError("ids must be a list of strings")
        if len(ids) > MAX_IDS_PER_REQUEST:
            raise ValueError(f"at most {MAX_IDS_PER_REQUEST} ids per request")
        repo = validate_repo_name(params.get("repo"))
        return pack_objects(self.source.fetch(repo, ids, caller.user))

    def stats(self) -> dict:
        s = super().stats()
        s["cache"] = self.source.stats()
        return s

    def close(self) -> None:
        close = getattr(self.source.upstream, "close", None)
        if close:
            close()


def make_cache_service(upstreams: list[str], max_bytes: int, identity: Identity | None = None,
                       token: str | None = None, tls: ClientTls | None = None, verbose: bool = False,
                       epoch_seconds: float = 10.0) -> ObjectTierService:
    """scion-cache: in memory, misses to the servers (FR-TIER-05/06)."""
    upstream = RemoteSource(upstreams, principal="scion-cache", tier="cache", token=token, tls=tls)
    source = CachingSource(MemoryObjectStore(max_bytes), upstream)
    source.guard = EpochGuard(upstream.acl_epochs, source.purge, epoch_seconds)
    return ObjectTierService("cache", source, ("daemon",), identity, verbose=verbose)


class DaemonService(ObjectTierService):
    """scion-daemon: a bounded node store (FR-TIER-01/02), warm-started from snapshots and
    refreshed periodically (FR-TIER-03); it verifies every object it receives (FR-OBJ-04)."""

    def __init__(self, store_dir: str, upstreams: list[str], max_bytes: int, snapshot_dir: str | None = None,
                 refresh_seconds: float = 300.0, identity: Identity | None = None, token: str | None = None,
                 tls: ClientTls | None = None, verbose: bool = False, epoch_seconds: float = 10.0):
        upstream = RemoteSource(upstreams, principal="scion-daemon", tier="daemon", token=token, tls=tls)
        source = CachingSource(BoundedFileObjectStore(store_dir, max_bytes), upstream, verify=True)
        # the store survives restarts, so the epochs it was filled under are saved beside it
        source.guard = EpochGuard(upstream.acl_epochs, source.purge, epoch_seconds,
                                  os.path.join(store_dir, "epochs.json"))
        super().__init__("daemon", source, ("client",), identity, verbose=verbose)
        self.snapshot_dir, self.refresh_seconds = snapshot_dir, refresh_seconds
        self.snapshots_loaded: dict[str, str] = {}
        self.snapshot_objects = 0
        self._stop = threading.Event()
        if snapshot_dir:
            self.refresh_snapshots()
            threading.Thread(target=self._refresh_loop, daemon=True, name="snapshot-refresh").start()

    def refresh_snapshots(self) -> int:
        """Import each repository's latest snapshot if it is new; returns the objects imported."""
        total = 0
        if not self.snapshot_dir or not os.path.isdir(self.snapshot_dir):
            return 0
        for repo in sorted(os.listdir(self.snapshot_dir)):
            d = os.path.join(self.snapshot_dir, repo)
            info = latest_snapshot(d) if os.path.isdir(d) else None
            if not info or self.snapshots_loaded.get(repo) == info["file"]:
                continue
            epoch = self.source.guard.ensure(repo)
            if epoch is None or info.get("epoch") != epoch:
                self.metrics.incr("snapshot.stale")  # taken under another ACL epoch: may hold uncacheable objects
                continue
            n = load_snapshot(os.path.join(d, info["file"]), self.source.store, repo, expect_epoch=epoch)
            self.snapshots_loaded[repo] = info["file"]
            self.snapshot_objects += n
            self.metrics.incr("snapshot.imported", n)
            total += n
        return total

    def _refresh_loop(self):
        while not self._stop.wait(self.refresh_seconds):
            try:
                self.refresh_snapshots()
            except (OSError, ValueError, ObjectError) as e:  # keep serving on a bad snapshot
                self.metrics.incr("snapshot.errors")
                if self.verbose:
                    print(f"scion-daemon: snapshot refresh failed: {e}")

    def stop(self):
        self._stop.set()
        self.close()

    def stats(self) -> dict:
        s = super().stats()
        s["snapshot"] = {"loaded": dict(self.snapshots_loaded), "objects_imported": self.snapshot_objects}
        return s


def summarize(stats: dict) -> str:
    c = stats.get("cache", {})
    return json.dumps({"tier": stats.get("tier"), "hit_rate": c.get("hit_rate"), "hits": c.get("hits"),
                       "misses": c.get("misses")})

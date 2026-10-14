"""Object stores (FR-OBJ-02, FR-OBJ-03, FR-TIER-02, FR-CL-02).

One compressed file per object; no packfiles, so nothing ever needs repacking or gc. Bounded stores
evict least-recently-used objects, which is always safe because any object can be fetched again.
"""
from __future__ import annotations

import os
import shutil
import tempfile
import threading
from collections import OrderedDict

from .objects import decode_stored, encode_stored, object_id


def ns_key(repo: str | None, oid: str) -> str:
    """Cache key for an object of a repository (ADR-13). Plain ids are used where there is one repository."""
    return f"{repo}/{oid}" if repo else oid


def key_oid(key: str) -> str:
    return key.rsplit("/", 1)[-1]


class ObjectStore:
    """Interface (06 §6.5): has / get_stored / put_stored, plus typed helpers."""

    def has(self, oid: str) -> bool:
        raise NotImplementedError

    def get_stored(self, oid: str) -> bytes | None:
        raise NotImplementedError

    def put_stored(self, oid: str, stored: bytes, verify: bool = True) -> None:
        raise NotImplementedError

    def put(self, otype: str, payload: bytes) -> str:
        oid = object_id(otype, payload)
        if not self.has(oid):
            self.put_stored(oid, encode_stored(otype, payload), verify=False)
        return oid

    def get(self, oid: str) -> tuple[str, bytes]:
        stored = self.get_stored(oid)
        if stored is None:
            raise KeyError(oid)
        return decode_stored(stored)

    def get_payload(self, oid: str, otype: str) -> bytes:
        t, payload = self.get(oid)
        if t != otype:
            raise KeyError(f"{oid[:12]} is a {t}, not a {otype}")
        return payload


class MemoryObjectStore(ObjectStore):
    """In-memory LRU (the regional cache's store). ``max_bytes=None`` means unbounded."""

    def __init__(self, max_bytes: int | None = None):
        self.max_bytes = max_bytes
        self._d: OrderedDict[str, bytes] = OrderedDict()
        self._size = 0
        self._lock = threading.Lock()
        self.evictions = 0

    def has(self, oid):
        with self._lock:
            return oid in self._d

    def get_stored(self, oid):
        with self._lock:
            v = self._d.get(oid)
            if v is not None:
                self._d.move_to_end(oid)
            return v

    def put_stored(self, oid, stored, verify=True):
        if verify:
            decode_stored(stored, key_oid(oid))
        with self._lock:
            if oid in self._d:
                self._d.move_to_end(oid)
                return
            self._d[oid] = stored
            self._size += len(stored)
            while self.max_bytes is not None and self._size > self.max_bytes and len(self._d) > 1:
                _, old = self._d.popitem(last=False)
                self._size -= len(old)
                self.evictions += 1

    @property
    def size_bytes(self):
        return self._size

    def __len__(self):
        return len(self._d)

    def purge_namespace(self, ns: str) -> int:
        """Drop every object of one repository (ADR-20)."""
        prefix = ns + "/"
        with self._lock:
            keys = [k for k in self._d if k.startswith(prefix)]
            for k in keys:
                self._size -= len(self._d.pop(k))
        return len(keys)


class FileObjectStore(ObjectStore):
    """Blob storage stand-in: ``root/ab/cd/<rest>`` (CON-02)."""

    def __init__(self, root: str):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def path(self, key: str) -> str:
        ns, _, oid = key.rpartition("/")
        return os.path.join(self.root, *([ns] if ns else []), oid[:2], oid[2:4], oid[4:])

    def has(self, oid):
        return os.path.exists(self.path(oid))

    def get_stored(self, oid):
        try:
            with open(self.path(oid), "rb") as f:
                return f.read()
        except (FileNotFoundError, NotADirectoryError):
            return None

    def put_stored(self, oid, stored, verify=True):
        if verify:
            decode_stored(stored, key_oid(oid))
        p = self.path(oid)
        if os.path.exists(p):
            return
        d = os.path.dirname(p)
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(stored)
            os.replace(tmp, p)  # atomic; concurrent writers of one id are harmless
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    def iter_ids(self, _base: str | None = None, _ns: str = ""):
        """Every stored key: plain ids, plus "<repo>/<id>" for namespaced objects."""
        base = _base or self.root
        for a in sorted(os.listdir(base)):
            pa = os.path.join(base, a)
            if not os.path.isdir(pa):
                continue
            if len(a) != 2 and not _ns:
                yield from self.iter_ids(pa, a)  # a repository namespace
                continue
            for b in sorted(os.listdir(pa)):
                pb = os.path.join(pa, b)
                if os.path.isdir(pb):
                    for rest in os.listdir(pb):
                        if not rest.startswith(".tmp-"):
                            yield ns_key(_ns, a + b + rest)


class BoundedFileObjectStore(FileObjectStore):
    """Disk store with a size bound and LRU eviction (node daemon, client cache)."""

    def __init__(self, root: str, max_bytes: int):
        super().__init__(root)
        self.max_bytes = max_bytes
        self._lru: OrderedDict[str, int] = OrderedDict()
        self._size = 0
        self._lock = threading.Lock()
        self.evictions = 0
        found = []
        for oid in self.iter_ids():
            try:
                st = os.stat(self.path(oid))
                found.append((st.st_atime_ns, oid, st.st_size))
            except FileNotFoundError:
                pass
        for _, oid, size in sorted(found):
            self._lru[oid] = size
            self._size += size
        with self._lock:
            self._evict()

    def get_stored(self, oid):
        data = super().get_stored(oid)
        if data is not None:
            with self._lock:
                if oid in self._lru:
                    self._lru.move_to_end(oid)
        return data

    def put_stored(self, oid, stored, verify=True):
        super().put_stored(oid, stored, verify)
        with self._lock:
            if oid not in self._lru:
                self._lru[oid] = len(stored)
                self._size += len(stored)
            self._lru.move_to_end(oid)
            self._evict()

    def _evict(self):
        while self._size > self.max_bytes and len(self._lru) > 1:
            oid, size = self._lru.popitem(last=False)
            self._size -= size
            self.evictions += 1
            try:
                os.unlink(self.path(oid))
            except FileNotFoundError:
                pass

    @property
    def size_bytes(self):
        return self._size

    def __len__(self):
        return len(self._lru)

    def purge_namespace(self, ns: str) -> int:
        """Drop every object of one repository, on disk and in the LRU (ADR-20)."""
        prefix = ns + "/"
        with self._lock:
            keys = [k for k in self._lru if k.startswith(prefix)]
            for k in keys:
                self._size -= self._lru.pop(k)
            shutil.rmtree(os.path.join(self.root, ns), ignore_errors=True)
        return len(keys)


class LRUCache:
    """Thread-safe LRU for decoded immutable values."""

    def __init__(self, capacity: int = 200_000):
        self.capacity = capacity
        self._d: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            v = self._d.get(key)
            if v is not None:
                self._d.move_to_end(key)
            return v

    def put(self, key, value):
        with self._lock:
            self._d[key] = value
            self._d.move_to_end(key)
            while len(self._d) > self.capacity:
                self._d.popitem(last=False)

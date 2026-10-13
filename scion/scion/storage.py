"""Object storage ("blob storage" in the article).

Objects are stored one-per-file, zlib-compressed, addressed by SHA-256.  There are no packfiles,
so there is nothing to repack, gc or otherwise maintain.  Because objects are immutable, every
layer may cache them forever without invalidation.
"""
from __future__ import annotations

import os
import tempfile
import threading
from collections import OrderedDict
from typing import Iterable

from .objects import decode_stored, encode_stored, object_id


class ObjectStore:
    """Interface for a content-addressed store of compressed objects."""

    def has(self, oid: str) -> bool:
        raise NotImplementedError

    def get_stored(self, oid: str) -> bytes | None:
        raise NotImplementedError

    def put_stored(self, oid: str, stored: bytes, verify: bool = True) -> None:
        raise NotImplementedError

    # Convenience helpers -----------------------------------------------------------------
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
            raise KeyError(f"{oid} is a {t}, not a {otype}")
        return payload

    def missing(self, oids: Iterable[str]) -> list[str]:
        return [o for o in oids if not self.has(o)]


class MemoryObjectStore(ObjectStore):
    """An in-memory LRU store.  ``max_bytes=None`` means unbounded."""

    def __init__(self, max_bytes: int | None = None):
        self.max_bytes = max_bytes
        self._data: OrderedDict[str, bytes] = OrderedDict()
        self._size = 0
        self._lock = threading.Lock()
        self.evictions = 0

    def has(self, oid: str) -> bool:
        with self._lock:
            return oid in self._data

    def get_stored(self, oid: str) -> bytes | None:
        with self._lock:
            v = self._data.get(oid)
            if v is not None:
                self._data.move_to_end(oid)
            return v

    def put_stored(self, oid: str, stored: bytes, verify: bool = True) -> None:
        if verify:
            decode_stored(stored, expected_id=oid)
        with self._lock:
            if oid in self._data:
                self._data.move_to_end(oid)
                return
            self._data[oid] = stored
            self._size += len(stored)
            if self.max_bytes is not None:
                while self._size > self.max_bytes and len(self._data) > 1:
                    _, old = self._data.popitem(last=False)
                    self._size -= len(old)
                    self.evictions += 1

    @property
    def size_bytes(self) -> int:
        return self._size

    def __len__(self) -> int:
        return len(self._data)


class FileObjectStore(ObjectStore):
    """Objects on a filesystem: ``root/ab/cd/<rest-of-id>``."""

    def __init__(self, root: str):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def _path(self, oid: str) -> str:
        return os.path.join(self.root, oid[:2], oid[2:4], oid[4:])

    def has(self, oid: str) -> bool:
        return os.path.exists(self._path(oid))

    def get_stored(self, oid: str) -> bytes | None:
        try:
            with open(self._path(oid), "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def put_stored(self, oid: str, stored: bytes, verify: bool = True) -> None:
        if verify:
            decode_stored(stored, expected_id=oid)
        path = self._path(oid)
        if os.path.exists(path):
            return
        d = os.path.dirname(path)
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(stored)
            os.replace(tmp, path)  # atomic; concurrent writers of the same id are harmless
        except BaseException:
            try:
                os.unlink(tmp)
            except FileNotFoundError:
                pass
            raise

    def iter_ids(self) -> Iterable[str]:
        for a in sorted(os.listdir(self.root)):
            pa = os.path.join(self.root, a)
            if len(a) != 2 or not os.path.isdir(pa):
                continue
            for b in sorted(os.listdir(pa)):
                pb = os.path.join(pa, b)
                if not os.path.isdir(pb):
                    continue
                for rest in os.listdir(pb):
                    if not rest.startswith(".tmp-"):
                        yield a + b + rest


class BoundedFileObjectStore(FileObjectStore):
    """A disk store with an upper size bound and LRU eviction.

    This is the client's "bounded local object cache" and the daemon's node-wide store.  Because
    every object can always be fetched again, evicting is always safe.
    """

    def __init__(self, root: str, max_bytes: int):
        super().__init__(root)
        self.max_bytes = max_bytes
        self._lock = threading.Lock()
        self._lru: OrderedDict[str, int] = OrderedDict()
        self._size = 0
        self.evictions = 0
        entries = []
        for oid in self.iter_ids():
            try:
                st = os.stat(self._path(oid))
            except FileNotFoundError:
                continue
            entries.append((st.st_atime_ns, oid, st.st_size))
        for _, oid, size in sorted(entries):
            self._lru[oid] = size
            self._size += size
        self._evict_locked()

    def get_stored(self, oid: str) -> bytes | None:
        data = super().get_stored(oid)
        if data is not None:
            with self._lock:
                if oid in self._lru:
                    self._lru.move_to_end(oid)
        return data

    def put_stored(self, oid: str, stored: bytes, verify: bool = True) -> None:
        super().put_stored(oid, stored, verify)
        with self._lock:
            if oid not in self._lru:
                self._lru[oid] = len(stored)
                self._size += len(stored)
            self._lru.move_to_end(oid)
            self._evict_locked()

    def _evict_locked(self) -> None:
        while self._size > self.max_bytes and len(self._lru) > 1:
            oid, size = self._lru.popitem(last=False)
            self._size -= size
            self.evictions += 1
            try:
                os.unlink(self._path(oid))
            except FileNotFoundError:
                pass

    @property
    def size_bytes(self) -> int:
        return self._size

    def __len__(self) -> int:
        return len(self._lru)


class LRUCache:
    """A tiny thread-safe LRU for decoded immutable values (trees, changesets)."""

    def __init__(self, capacity: int = 100_000):
        self.capacity = capacity
        self._d: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            v = self._d.get(key)
            if v is not None:
                self._d.move_to_end(key)
            return v

    def put(self, key, value) -> None:
        with self._lock:
            self._d[key] = value
            self._d.move_to_end(key)
            while len(self._d) > self.capacity:
                self._d.popitem(last=False)

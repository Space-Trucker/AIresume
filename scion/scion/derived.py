"""The generic derived-data mechanism.

Everything that isn't part of a changeset itself is derived data.  Each type is defined
recursively: its value for a changeset is computed from the changeset and the values of the same
type for that changeset's parents.  That buys three things, as in the article:

1. A new data structure can be added by registering a new ``DerivedType``.
2. Each type is computed eagerly (when the changeset is created) or deferred until first use.
3. Clients never see these structures, only query APIs, so they can be changed at any time.

Values are short strings (usually an object id or a small JSON document) written back to the
metadata store.  Because every value is a deterministic function of immutable inputs, servers
compute and write values without coordinating with each other.

Invariant: if a value exists for a changeset, values exist for all of its ancestors.  Computation
therefore walks parents until it finds stored values, then derives forward in topological order.
"""
from __future__ import annotations

import threading
from collections import Counter
from typing import TYPE_CHECKING

from .changeset import Changeset
from .storage import LRUCache

if TYPE_CHECKING:  # pragma: no cover
    from .repo import Repository


class DerivedType:
    name: str = ""
    eager: bool = False
    #: other derived types that must exist for the same changeset (and hence its ancestors)
    depends_on: tuple[str, ...] = ()

    def derive(self, repo: "Repository", cs_id: str, cs: Changeset, parent_values: list[str]) -> str:
        raise NotImplementedError


class DerivedDataManager:
    def __init__(self, repo: "Repository"):
        self.repo = repo
        self.types: dict[str, DerivedType] = {}
        self.cache = LRUCache(500_000)
        self.stats: Counter = Counter()
        self._locks: dict[tuple[str, str], threading.Lock] = {}
        self._locks_guard = threading.Lock()

    def register(self, dtype: DerivedType) -> None:
        if dtype.name in self.types:
            raise ValueError(f"derived type {dtype.name} already registered")
        for dep in dtype.depends_on:
            if dep not in self.types:
                raise ValueError(f"{dtype.name} depends on unregistered type {dep}")
        self.types[dtype.name] = dtype

    @property
    def eager_types(self) -> list[str]:
        return [t.name for t in self.types.values() if t.eager]

    def peek(self, name: str, cs_id: str) -> str | None:
        key = (name, cs_id)
        v = self.cache.get(key)
        if v is None:
            v = self.repo.meta.derived_get(name, cs_id)
            if v is not None:
                self.cache.put(key, v)
        return v

    def put(self, name: str, cs_id: str, value: str) -> None:
        self.repo.meta.derived_put(name, cs_id, value)
        self.cache.put((name, cs_id), value)

    def get(self, name: str, cs_id: str) -> str:
        v = self.peek(name, cs_id)
        if v is not None:
            self.stats[f"{name}.hit"] += 1
            return v
        lock = self._lock_for(name, cs_id)
        with lock:  # single-flight within this process
            v = self.peek(name, cs_id)
            if v is not None:
                return v
            self._derive_missing(name, cs_id)
        v = self.peek(name, cs_id)
        assert v is not None
        return v

    def _lock_for(self, name: str, cs_id: str) -> threading.Lock:
        with self._locks_guard:
            if len(self._locks) > 10_000:
                self._locks.clear()
            return self._locks.setdefault((name, cs_id), threading.Lock())

    def _derive_missing(self, name: str, cs_id: str) -> None:
        dtype = self.types[name]
        # Iterative post-order walk over parents that are missing a value.
        order: list[str] = []
        visited: set[str] = set()
        stack: list[tuple[str, bool]] = [(cs_id, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                order.append(node)
                continue
            if node in visited:
                continue
            visited.add(node)
            if self.peek(name, node) is not None:
                continue
            stack.append((node, True))
            for p in reversed(self.repo.get_changeset(node).parents):
                if p not in visited:
                    stack.append((p, False))
        for node in order:
            if self.peek(name, node) is not None:
                continue
            for dep in dtype.depends_on:
                self.get(dep, node)
            cs = self.repo.get_changeset(node)
            parent_values = []
            for p in cs.parents:
                pv = self.peek(name, p)
                assert pv is not None, f"derived invariant broken: {name} missing for {p}"
                parent_values.append(pv)
            value = dtype.derive(self.repo, node, cs, parent_values)
            self.put(name, node, value)
            self.stats[f"{name}.derived"] += 1

    def derive_eager(self, cs_id: str) -> None:
        for name in self.eager_types:
            self.get(name, cs_id)

    def backfill(self, name: str, cs_id: str) -> int:
        """Derive ``name`` for ``cs_id`` and all ancestors; return how many values were computed."""
        before = self.stats[f"{name}.derived"]
        self.get(name, cs_id)
        return self.stats[f"{name}.derived"] - before

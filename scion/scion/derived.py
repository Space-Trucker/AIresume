"""The generic derived-data mechanism (FR-DD-01…06; activity diagram 06 §6.8).

Everything that is not part of a changeset is derived data. A type is defined recursively: its value
for a changeset is computed from the changeset and the type's values for the changeset's parents.
Each type is eager (computed when the changeset is created) or deferred (computed on first use).
Values are deterministic, so any server computes and writes them back without coordinating with
other servers.

Invariant: if a value exists for a changeset, values exist for all of its ancestors. To derive, walk
the parents until values are found, then compute forward in topological order.
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
    depends_on: tuple[str, ...] = ()

    def derive(self, repo: "Repository", cs_id: str, cs: Changeset, parent_values: list[str]) -> str:
        raise NotImplementedError


class DerivedDataManager:
    def __init__(self, repo: "Repository"):
        self.repo = repo
        self.types: dict[str, DerivedType] = {}
        self.cache = LRUCache(500_000, max_bytes=16 << 20)
        self.stats: Counter = Counter()
        self._locks: dict[tuple[str, str], list] = {}  # key -> [lock, users]: removed when unused
        self._guard = threading.Lock()

    def register(self, dtype: DerivedType) -> None:
        if dtype.name in self.types:
            raise ValueError(f"derived type {dtype.name} is already registered")
        missing = [d for d in dtype.depends_on if d not in self.types]
        if missing:
            raise ValueError(f"{dtype.name} depends on unregistered types {missing}")
        self.types[dtype.name] = dtype

    @property
    def eager_types(self) -> list[str]:
        return [t.name for t in self.types.values() if t.eager]

    def peek(self, name: str, cs_id: str) -> str | None:
        v = self.cache.get((name, cs_id))
        if v is None:
            v = self.repo.meta.derived_get(name, cs_id)
            if v is not None:
                self.cache.put((name, cs_id), v, len(v))
        return v

    def put(self, name: str, cs_id: str, value: str) -> None:
        self.repo.meta.derived_put(name, cs_id, value)
        self.cache.put((name, cs_id), value, len(value))

    def get(self, name: str, cs_id: str) -> str:
        v = self.peek(name, cs_id)
        if v is not None:
            return v
        key = (name, cs_id)
        with self._guard:  # single flight within this process; the lock is dropped when unused
            entry = self._locks.get(key)
            if entry is None:
                entry = self._locks[key] = [threading.Lock(), 0]
            entry[1] += 1
        try:
            with entry[0]:
                if self.peek(name, cs_id) is None:
                    self._derive_missing(name, cs_id)
        finally:
            with self._guard:
                entry[1] -= 1
                if entry[1] == 0:
                    self._locks.pop(key, None)
        v = self.peek(name, cs_id)
        assert v is not None
        return v

    def _derive_missing(self, name: str, cs_id: str) -> None:
        dtype = self.types[name]
        order: list[str] = []
        visited: set[str] = set()
        stack = [(cs_id, False)]
        while stack:  # iterative post-order over parents that lack a value
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
                if pv is None:
                    raise RuntimeError(f"derived invariant broken: {name} missing for parent {p[:12]}")
                parent_values.append(pv)
            self.put(name, node, dtype.derive(self.repo, node, cs, parent_values))
            self.stats[f"{name}.derived"] += 1

    def derive_eager(self, cs_id: str) -> None:
        for name in self.eager_types:
            self.get(name, cs_id)

    def backfill(self, name: str, cs_id: str) -> int:
        """Derive ``name`` for ``cs_id`` and every ancestor still missing it (FR-DD-06)."""
        before = self.stats[f"{name}.derived"]
        self.get(name, cs_id)
        return self.stats[f"{name}.derived"] - before

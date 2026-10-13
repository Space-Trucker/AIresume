"""Trees: lookup, incremental update, diff and walk (FR-CS-08/09, FR-OBJ-05, FR-QRY-03; TreeOps 06 §6.5).

``apply_augmented`` rewrites only the tree nodes on changed paths, so applying a changeset costs
O(size of change × path depth), independent of repository size (FR-CS-09). The same routine
maintains every tree-shaped piece of derived data through a ``TreeCodec``: plain trees, history
trees and search trees.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Iterator

from .objects import KIND_DIR, decode_tree, encode_tree, join, split_path
from .storage import LRUCache, ObjectStore


class PathConflict(Exception):
    """A file would sit where a directory is (or the reverse), or a deleted path does not exist."""


class TreeCodec:
    """How one kind of tree is read, written and built."""

    def read(self, node_id: str) -> dict: ...
    def write(self, entries: dict, path: str) -> str: ...
    def child(self, entry) -> str: ...
    def file_entry(self, path: str, change: tuple, old_entry): ...
    def dir_entry(self, path: str, child_id: str, child_entries: dict, old_entry): ...

    def is_dir(self, entry) -> bool:
        return entry[0] == KIND_DIR


def apply_augmented(codec: TreeCodec, root: str | None, changes: dict) -> str:
    """Apply ``changes`` (path -> (kind, blob), or None to delete) and return the new root id.
    An empty result is written as an empty root."""
    new_root, _ = _apply(codec, root, changes, "")
    return codec.write({}, "") if new_root is None else new_root


def _apply(codec: TreeCodec, node: str | None, changes: dict, prefix: str):
    entries = dict(codec.read(node)) if node else {}
    direct: dict = {}
    nested: dict = defaultdict(dict)
    for rel, ch in changes.items():
        head, sep, rest = rel.partition("/")
        if sep:
            nested[head][rest] = ch
        else:
            direct[head] = ch
    # 1. deletions first, so a file can become a directory within one changeset
    for name, ch in direct.items():
        if ch is None:
            old = entries.get(name)
            if old is None or codec.is_dir(old):
                raise PathConflict(f"cannot delete {join(prefix, name)}: no such file")
            del entries[name]
    # 2. subdirectories
    for name, sub in nested.items():
        old = entries.get(name)
        if old is not None and not codec.is_dir(old):
            raise PathConflict(f"{join(prefix, name)} is a file; cannot add paths beneath it")
        new_child, child_entries = _apply(codec, codec.child(old) if old is not None else None, sub, join(prefix, name))
        if new_child is None:
            entries.pop(name, None)  # the directory became empty
        else:
            entries[name] = codec.dir_entry(join(prefix, name), new_child, child_entries, old)
    # 3. writes, so a directory emptied in step 2 can become a file
    for name, ch in direct.items():
        if ch is None:
            continue
        old = entries.get(name)
        if old is not None and codec.is_dir(old):
            raise PathConflict(f"{join(prefix, name)} is a directory; cannot write a file there")
        entries[name] = codec.file_entry(join(prefix, name), ch, old)
    if not entries:
        return None, {}
    return codec.write(entries, prefix), entries


class PlainTreeCodec(TreeCodec):
    def __init__(self, ops: "TreeOps", on_write: Callable[[str, str, str], None] | None = None):
        self.ops, self.on_write = ops, on_write

    def read(self, node_id):
        return self.ops.read(node_id)

    def write(self, entries, path):
        tid = self.ops.write(entries)
        if self.on_write:
            self.on_write(path, KIND_DIR, tid)
        return tid

    def child(self, entry):
        return entry[1]

    def file_entry(self, path, change, old_entry):
        if self.on_write:
            self.on_write(path, change[0], change[1])
        return (change[0], change[1])

    def dir_entry(self, path, child_id, child_entries, old_entry):
        return (KIND_DIR, child_id)


class TreeOps:
    def __init__(self, store: ObjectStore, cache: LRUCache | None = None):
        self.store = store
        self.cache = cache if cache is not None else LRUCache()
        self.writes = 0  # tree objects written (incrementality is measured on this, T-CORE-08)

    def read(self, tid: str) -> dict:
        hit = self.cache.get(("tree", tid))
        if hit is None:
            payload = self.store.get_payload(tid, "tree")
            hit = decode_tree(payload)
            self.cache.put(("tree", tid), hit, len(payload))
        return hit

    def write(self, entries: dict) -> str:
        self.writes += 1
        return self.store.put("tree", encode_tree(entries))

    def lookup(self, root: str | None, path: str):
        if root is None:
            return None
        node = (KIND_DIR, root)
        for part in split_path(path):
            if node[0] != KIND_DIR:
                return None
            node = self.read(node[1]).get(part)
            if node is None:
                return None
        return node

    def apply(self, root: str | None, changes: dict, on_write=None) -> str:
        return apply_augmented(PlainTreeCodec(self, on_write), root, changes)

    def diff(self, a: str | None, b: str | None, prefix: str = "") -> Iterator[tuple]:
        """Yield (path, old_entry|None, new_entry|None) for every file that differs. Identical
        subtrees are skipped without being read."""
        if a == b:
            return
        ea = self.read(a) if a else {}
        eb = self.read(b) if b else {}
        for name in sorted(set(ea) | set(eb)):
            x, y = ea.get(name), eb.get(name)
            if x == y:
                continue
            path = join(prefix, name)
            xd = x is not None and x[0] == KIND_DIR
            yd = y is not None and y[0] == KIND_DIR
            if xd or yd:
                yield from self.diff(x[1] if xd else None, y[1] if yd else None, path)
            xf = None if x is None or xd else x
            yf = None if y is None or yd else y
            if xf != yf:
                yield (path, xf, yf)

    def walk(self, root: str, prefix: str = "", want_dir: Callable[[str], bool] | None = None):
        """Yield (path, kind, id) for every file beneath ``root``, in path order."""
        for name, (kind, oid) in sorted(self.read(root).items()):
            path = join(prefix, name)
            if kind == KIND_DIR:
                if want_dir is None or want_dir(path):
                    yield from self.walk(oid, path, want_dir)
            else:
                yield path, kind, oid

"""Tree operations: lookup, incremental update, diff and walk.

``apply_augmented`` is the core of "commits must be cheap and incremental": applying a changeset
rewrites only the tree nodes on changed paths, so its cost grows with the size of the change and
the depth of the paths, not with the size of the repository.  The same routine maintains every
tree-shaped piece of derived data (plain trees, history trees, search trees) through a codec.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Iterator

from .objects import (
    EMPTY_TREE_ID,
    KIND_DIR,
    TreeEntries,
    decode_tree,
    encode_tree,
    split_path,
)
from .storage import LRUCache, ObjectStore


class PathConflict(Exception):
    """A change would turn a file into a directory (or vice versa) without deleting it first."""


Change = tuple  # (kind, blob) for a write, None for a delete


class TreeCodec:
    """How to read, write and build entries for one kind of tree."""

    def read(self, node_id: str) -> dict:
        raise NotImplementedError

    def write(self, entries: dict, path: str) -> str:
        raise NotImplementedError

    def is_dir(self, entry) -> bool:
        return entry[0] == KIND_DIR

    def child(self, entry) -> str:
        raise NotImplementedError

    def file_entry(self, path: str, change: Change, old_entry):
        raise NotImplementedError

    def dir_entry(self, path: str, child_id: str, child_entries: dict, old_entry):
        raise NotImplementedError


def _join(prefix: str, name: str) -> str:
    return f"{prefix}/{name}" if prefix else name


def apply_augmented(codec: TreeCodec, root: str | None, changes: dict[str, Change]) -> str:
    """Apply ``changes`` (path -> (kind, blob) or None) to ``root`` and return the new root id.
    An empty result is written as an empty root tree."""
    new_root, entries = _apply(codec, root, changes, "")
    if new_root is None:
        return codec.write({}, "")
    return new_root


def _apply(codec: TreeCodec, node: str | None, changes: dict[str, Change], prefix: str):
    entries = dict(codec.read(node)) if node else {}
    direct: dict[str, Change] = {}
    nested: dict[str, dict[str, Change]] = defaultdict(dict)
    for rel, ch in changes.items():
        head, sep, rest = rel.partition("/")
        if sep:
            nested[head][rest] = ch
        else:
            direct[head] = ch

    # 1. Deletions first, so a file may be replaced by a directory in one changeset.
    for name, ch in direct.items():
        if ch is None:
            old = entries.get(name)
            if old is None or codec.is_dir(old):
                raise PathConflict(f"cannot delete {_join(prefix, name)}: not a file")
            del entries[name]
    # 2. Recurse into subdirectories.
    for name, sub in nested.items():
        old = entries.get(name)
        if old is not None and not codec.is_dir(old):
            raise PathConflict(f"{_join(prefix, name)} is a file, cannot add paths beneath it")
        child_id = codec.child(old) if old is not None else None
        new_child, child_entries = _apply(codec, child_id, sub, _join(prefix, name))
        if new_child is None:
            entries.pop(name, None)  # directory became empty
        else:
            entries[name] = codec.dir_entry(_join(prefix, name), new_child, child_entries, old)
    # 3. Writes.
    for name, ch in direct.items():
        if ch is None:
            continue
        old = entries.get(name)
        if old is not None and codec.is_dir(old):
            raise PathConflict(f"{_join(prefix, name)} is a directory, cannot write a file there")
        entries[name] = codec.file_entry(_join(prefix, name), ch, old)

    if not entries:
        return None, {}
    return codec.write(entries, prefix), entries


class PlainTreeCodec(TreeCodec):
    def __init__(self, ops: "TreeOps", on_write: Callable[[str, str, str], None] | None = None):
        self.ops = ops
        self.on_write = on_write

    def read(self, node_id: str) -> dict:
        return self.ops.read(node_id)

    def write(self, entries: dict, path: str) -> str:
        tid = self.ops.write(entries)
        if self.on_write:
            self.on_write(path, KIND_DIR, tid)
        return tid

    def child(self, entry) -> str:
        return entry[1]

    def file_entry(self, path, change, old_entry):
        kind, blob = change
        if self.on_write:
            self.on_write(path, kind, blob)
        return (kind, blob)

    def dir_entry(self, path, child_id, child_entries, old_entry):
        return (KIND_DIR, child_id)


class TreeOps:
    def __init__(self, store: ObjectStore, cache: LRUCache | None = None):
        self.store = store
        self.cache = cache or LRUCache(200_000)

    def read(self, tid: str) -> TreeEntries:
        hit = self.cache.get(("tree", tid))
        if hit is not None:
            return hit
        entries = decode_tree(self.store.get_payload(tid, "tree"))
        self.cache.put(("tree", tid), entries)
        return entries

    def write(self, entries: TreeEntries) -> str:
        return self.store.put("tree", encode_tree(entries))

    def empty(self) -> str:
        return self.store.put("tree", b"")

    def lookup(self, root: str, path: str) -> tuple[str, str] | None:
        node: tuple[str, str] = (KIND_DIR, root)
        for part in split_path(path):
            if node[0] != KIND_DIR:
                return None
            nxt = self.read(node[1]).get(part)
            if nxt is None:
                return None
            node = nxt
        return node

    def apply(self, root: str | None, changes: dict[str, Change],
              on_write: Callable[[str, str, str], None] | None = None) -> str:
        return apply_augmented(PlainTreeCodec(self, on_write), root or None, changes)

    def diff(self, a: str | None, b: str | None, prefix: str = "") -> Iterator[tuple]:
        """Yield (path, old_entry|None, new_entry|None) for every file that differs.
        Identical subtrees are skipped without being read, which is what makes diffs between
        nearby changesets cheap even in an enormous repository."""
        if a == b:
            return
        ea = self.read(a) if a else {}
        eb = self.read(b) if b else {}
        for name in sorted(set(ea) | set(eb)):
            x, y = ea.get(name), eb.get(name)
            if x == y:
                continue
            path = _join(prefix, name)
            xd = x is not None and x[0] == KIND_DIR
            yd = y is not None and y[0] == KIND_DIR
            if xd or yd:
                yield from self.diff(x[1] if xd else None, y[1] if yd else None, path)
            xf = x if x is not None and not xd else None
            yf = y if y is not None and not yd else None
            if xf != yf:
                yield (path, xf, yf)

    def walk(self, root: str, prefix: str = "",
             want_dir: Callable[[str], bool] | None = None) -> Iterator[tuple[str, str, str]]:
        """Yield (path, kind, id) for every file under ``root``."""
        stack = [(root, prefix)]
        while stack:
            tid, pfx = stack.pop()
            for name, (kind, oid) in sorted(self.read(tid).items(), reverse=True):
                path = _join(pfx, name)
                if kind == KIND_DIR:
                    if want_dir is None or want_dir(path):
                        stack.append((oid, path))
                else:
                    yield path, kind, oid


def empty_tree_id() -> str:
    return EMPTY_TREE_ID

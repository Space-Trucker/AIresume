"""The derived data types registered by default.

  tree      root tree id                                        eager
  graph     generation number + first-parent skip list           eager
  history   history tree: last changeset to touch each path      eager
  copies    copy and rename detection for added files            eager
  search    search tree: trigram bloom filters for path search   eager
  blame     per-file line attribution                            deferred (computed on first use)
"""
from __future__ import annotations

import difflib
import hashlib
import json
from typing import TYPE_CHECKING

from .changeset import OP_ADD, OP_DELETE, Changeset
from .derived import DerivedType
from .objects import (
    KIND_DIR,
    decode_htree,
    encode_htree,
    is_binary,
    split_path,
)
from .trees import TreeCodec, apply_augmented

if TYPE_CHECKING:  # pragma: no cover
    from .repo import Repository


def _changes_map(cs: Changeset) -> dict:
    return {c.path: (None if c.op == OP_DELETE else (c.kind, c.blob)) for c in cs.changes}


# =============================================================================================
# tree
# =============================================================================================
class RootTreeType(DerivedType):
    name = "tree"
    eager = True

    def derive(self, repo, cs_id, cs, parent_values):
        base = parent_values[0] if parent_values else None
        return repo.apply_to_tree(base, _changes_map(cs))


# =============================================================================================
# graph: generation numbers and skip lists
# =============================================================================================
class GraphType(DerivedType):
    """``{"g": generation, "l": linear_run, "s": [first-parent ancestors at distance 2**k]}``

    * ``g`` is 1 + the maximum parent generation; every ancestor has a strictly lower one, which
      lets ancestry walks prune anything below the generation of the target.
    * ``l`` counts how many first-parent steps can be taken from here while passing only through
      single-parent changesets.  Inside such a run there is exactly one path to any ancestor, so
      the run can be skipped in O(log n) with the skip list instead of walked step by step.
    * ``s[k]`` is the first-parent ancestor 2**k steps away.
    """

    name = "graph"
    eager = True

    def derive(self, repo, cs_id, cs, parent_values):
        if not cs.parents:
            return json.dumps({"g": 1, "l": 0, "s": []}, separators=(",", ":"))
        pvals = [json.loads(v) for v in parent_values]
        gen = 1 + max(p["g"] for p in pvals)
        linear = 1 + pvals[0]["l"] if len(cs.parents) == 1 else 0
        skips = [cs.parents[0]]
        k = 0
        while True:
            hop = repo.graph(skips[k])["s"]
            if len(hop) <= k:
                break
            skips.append(hop[k])
            k += 1
        return json.dumps({"g": gen, "l": linear, "s": skips}, separators=(",", ":"))


# =============================================================================================
# history: path history
# =============================================================================================
class _HistoryCodec(TreeCodec):
    def __init__(self, repo: "Repository", cs_id: str, cs: Changeset, parent_values: list[str]):
        self.repo = repo
        self.cs_id = cs_id
        self.cs = cs
        self.other_parents = parent_values[1:]

    def read(self, node_id):
        return self.repo.read_htree(node_id)

    def write(self, entries, path):
        return self.repo.objects.put("htree", encode_htree(entries))

    def child(self, entry):
        return entry[3]

    def file_entry(self, path, change, old_entry):
        kind, blob = change
        # Footnote 1: changesets record changes relative to the first parent.  When a merge
        # brings in a file exactly as it exists in another parent, keep that parent's history
        # so "last changed by" names the changeset that actually wrote it.
        for proot in self.other_parents:
            e = self.repo.htree_lookup(proot, path)
            if e is not None and e[0] == kind and e[1] == blob:
                return (kind, blob, e[2], "")
        return (kind, blob, self.cs_id, "")

    def dir_entry(self, path, child_id, child_entries, old_entry):
        return (KIND_DIR, "", self.cs_id, child_id)


class HistoryTreeType(DerivedType):
    name = "history"
    eager = True

    def derive(self, repo, cs_id, cs, parent_values):
        base = parent_values[0] if parent_values else None
        codec = _HistoryCodec(repo, cs_id, cs, parent_values)
        return apply_augmented(codec, base, _changes_map(cs))


# =============================================================================================
# copies: copy and rename detection
# =============================================================================================
class CopyInfoType(DerivedType):
    """``{dest_path: {"from": src_path, "type": "rename"|"copy"}}`` for files added by the
    changeset whose contents already existed at another path in the first parent."""

    name = "copies"
    eager = True
    depends_on = ("tree",)

    def derive(self, repo, cs_id, cs, parent_values):
        result: dict[str, dict] = {}
        parent = cs.first_parent
        parent_root = repo.root_tree(parent) if parent else None
        deleted: dict[str, str] = {}
        if parent_root:
            for c in cs.changes:
                if c.op == OP_DELETE:
                    e = repo.trees.lookup(parent_root, c.path)
                    if e is not None:
                        deleted.setdefault(e[1], c.path)
        for c in cs.changes:
            if c.op != OP_ADD or parent_root is None:
                continue
            if c.blob in deleted:
                result[c.path] = {"from": deleted[c.blob], "type": "rename"}
                continue
            for cand in repo.meta.blob_index_paths(c.blob):
                if cand == c.path:
                    continue
                e = repo.trees.lookup(parent_root, cand)
                if e is not None and e[0] != KIND_DIR and e[1] == c.blob:
                    result[c.path] = {"from": cand, "type": "copy"}
                    break
        repo.meta.blob_index_add((c.blob, c.path) for c in cs.changes if c.op != OP_DELETE)
        return json.dumps(result, sort_keys=True, separators=(",", ":"))


# =============================================================================================
# search: bloom-filtered trigram tree for path search
# =============================================================================================
BLOOM_BITS = 2048


def name_trigrams(name: str) -> set[str]:
    s = name.lower()
    if len(s) < 3:
        return {s}
    return {s[i:i + 3] for i in range(len(s) - 2)}


def _bloom_bits(gram: str) -> tuple[int, int]:
    h = hashlib.blake2b(gram.encode(), digest_size=8).digest()
    return int.from_bytes(h[:4], "big") % BLOOM_BITS, int.from_bytes(h[4:], "big") % BLOOM_BITS


def bloom_of(grams) -> int:
    v = 0
    for g in grams:
        a, b = _bloom_bits(g)
        v |= (1 << a) | (1 << b)
    return v


def bloom_may_contain(bloom: int, grams) -> bool:
    for g in grams:
        a, b = _bloom_bits(g)
        if not (bloom >> a) & 1 or not (bloom >> b) & 1:
            return False
    return True


class _SearchCodec(TreeCodec):
    def __init__(self, repo: "Repository"):
        self.repo = repo

    def read(self, node_id):
        return self.repo.read_stree(node_id)

    def write(self, entries, path):
        rows = [[n, e[0], e[1], format(e[2], "x")] for n, e in sorted(entries.items())]
        return self.repo.objects.put("stree", json.dumps(rows, separators=(",", ":")).encode())

    def child(self, entry):
        return entry[1]

    def file_entry(self, path, change, old_entry):
        return (change[0], change[1], 0)

    def dir_entry(self, path, child_id, child_entries, old_entry):
        bloom = 0
        for name, e in child_entries.items():
            bloom |= bloom_of(name_trigrams(name))
            if e[0] == KIND_DIR:
                bloom |= e[2]
        return (KIND_DIR, child_id, bloom)


class SearchTreeType(DerivedType):
    name = "search"
    eager = True

    def derive(self, repo, cs_id, cs, parent_values):
        base = parent_values[0] if parent_values else None
        return apply_augmented(_SearchCodec(repo), base, _changes_map(cs))


# =============================================================================================
# blame
# =============================================================================================
def split_lines(data: bytes) -> list[bytes]:
    return data.splitlines(keepends=True)


def expand_runs(runs: list) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for cs, start, count in runs:
        out.extend((cs, start + i) for i in range(count))
    return out


def compress_runs(attr: list[tuple[str, int]]) -> list:
    runs: list = []
    for cs, line in attr:
        if runs and runs[-1][0] == cs and runs[-1][1] + runs[-1][2] == line:
            runs[-1][2] += 1
        else:
            runs.append([cs, line, 1])
    return runs


class BlameType(DerivedType):
    """``{path: blame_object_id | "binary"}`` for every file the changeset adds or modifies.

    A blame object is ``{"runs": [[changeset, origin_line, count], ...]}``: line *i* of the file
    was introduced as line ``origin_line`` of ``changeset``.  A file's blame is computed from the
    blame of its previous version (on the first parent, or the copy source) plus a line diff,
    so the cost is proportional to the size of the change.  The type is deferred: it is computed
    the first time someone asks, then stored forever.
    """

    name = "blame"
    eager = False
    depends_on = ("history", "copies")

    def derive(self, repo, cs_id, cs, parent_values):
        result: dict[str, str] = {}
        copies = json.loads(repo.derived.get("copies", cs_id))
        for c in cs.changes:
            if c.op == OP_DELETE:
                continue
            data = repo.read_blob(c.blob)
            if is_binary(data):
                result[c.path] = "binary"
                continue
            # Merges: a file taken verbatim from another parent keeps that parent's blame.
            reused = None
            for p in cs.parents[1:]:
                e = repo.htree_lookup(repo.history_root(p), c.path)
                if e is not None and e[1] == c.blob and e[0] == c.kind:
                    reused = repo.blame_object_for(e[2], c.path)
                    break
            if reused is not None:
                result[c.path] = reused
                continue
            prev = None
            if cs.first_parent:
                src = copies.get(c.path, {}).get("from", c.path)
                prev = repo.previous_version(cs.first_parent, src)
            new_lines = split_lines(data)
            attr = [(cs_id, i + 1) for i in range(len(new_lines))]
            if prev is not None:
                attr = self._carry(repo, cs_id, prev, new_lines, attr)
            # Merge resolutions: lines still unattributed may come from another parent.
            for p in cs.parents[1:]:
                other = repo.previous_version(p, c.path)
                if other is not None and other[1] != "binary":
                    attr = self._carry(repo, cs_id, other, new_lines, attr)
            payload = json.dumps({"runs": compress_runs(attr)}, separators=(",", ":")).encode()
            result[c.path] = repo.objects.put("blame", payload)
        return json.dumps(result, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _carry(repo, cs_id, prev, new_lines, attr):
        """Copy attributions from a previous version onto lines of the new version that are
        unchanged from it and still attributed to ``cs_id``."""
        prev_blob, prev_blame_id = prev
        old_lines = split_lines(repo.read_blob(prev_blob))
        if prev_blame_id == "binary":
            return attr
        old_attr = expand_runs(repo.read_blame(prev_blame_id))
        out = list(attr)
        sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    if out[j1 + k][0] == cs_id:
                        out[j1 + k] = old_attr[i1 + k]
        return out


def register_default_types(manager) -> None:
    manager.register(RootTreeType())
    manager.register(GraphType())
    manager.register(HistoryTreeType())
    manager.register(CopyInfoType())
    manager.register(SearchTreeType())
    manager.register(BlameType())


__all__ = [
    "register_default_types",
    "name_trigrams",
    "bloom_may_contain",
    "expand_runs",
    "split_path",
]

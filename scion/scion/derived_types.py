"""The built-in derived-data types (FR-DD-07…12; 07 §7.6).

  tree     root tree id                                          eager    FR-DD-07
  graph    generation number + first-parent skip list            eager    FR-DD-10
  history  history tree: last changeset to touch each path       eager    FR-DD-08
  copies   copy and rename detection for added files             eager    FR-DD-11
  search   search tree: trigram bloom filters for path search    eager    FR-DD-12
  blame    per-file line attribution                             deferred FR-DD-09

History and blame follow the first parent only (BR-06, ADR-19): a merge's changes are relative to
its first parent, so whatever a merge brings in is attributed to the merge itself.
"""
from __future__ import annotations

import functools
import hashlib
import json

from . import linediff
from .changeset import OP_ADD, OP_DELETE, Changeset
from .derived import DerivedType
from .objects import KIND_DIR, KIND_LINK, encode_htree, is_binary
from .trees import TreeCodec, apply_augmented


def changes_map(cs: Changeset) -> dict:
    return {c.path: (None if c.op == OP_DELETE else (c.kind, c.blob)) for c in cs.changes}


class RootTreeType(DerivedType):
    name, eager = "tree", True

    def derive(self, repo, cs_id, cs, parent_values):
        return repo.apply_to_tree(parent_values[0] if parent_values else None, changes_map(cs))


class GraphType(DerivedType):
    """``{"g": generation, "l": single-parent run length, "s": [first-parent ancestor at 2**k]}``.

    Generations let ancestry walks prune everything below the target. Inside a run of single-parent
    changesets there is exactly one path to each ancestor, so the run is crossed with skip-list
    hops in O(log n) instead of step by step (ADR-12)."""

    name, eager = "graph", True

    def derive(self, repo, cs_id, cs, parent_values):
        if not cs.parents:
            value = {"g": 1, "l": 0, "s": []}
        else:
            pv = [json.loads(v) for v in parent_values]
            skips = [cs.parents[0]]
            while True:
                hop = repo.graph(skips[-1])["s"]
                k = len(skips) - 1
                if len(hop) <= k:
                    break
                skips.append(hop[k])
            value = {"g": 1 + max(p["g"] for p in pv), "l": 1 + pv[0]["l"] if len(cs.parents) == 1 else 0, "s": skips}
        return json.dumps(value, separators=(",", ":"))


class _HistoryCodec(TreeCodec):
    """History-tree entries: (kind, content_id, last_changeset, child_htree)."""

    def __init__(self, repo, cs_id):
        self.repo, self.cs_id = repo, cs_id

    def read(self, node_id):
        return self.repo.read_htree(node_id)

    def write(self, entries, path):
        payload = encode_htree(entries)
        oid = self.repo.objects.put("htree", payload)
        self.repo.cache.put(("htree", oid), dict(entries), len(payload))  # write-through, as TreeOps.write
        return oid

    def child(self, entry):
        return entry[3]

    def file_entry(self, path, change, old_entry):
        return (change[0], change[1], self.cs_id, "")

    def dir_entry(self, path, child_id, child_entries, old_entry):
        return (KIND_DIR, "", self.cs_id, child_id)


class HistoryTreeType(DerivedType):
    name, eager = "history", True

    def derive(self, repo, cs_id, cs, parent_values):
        return apply_augmented(_HistoryCodec(repo, cs_id), parent_values[0] if parent_values else None, changes_map(cs))


class CopyInfoType(DerivedType):
    """``{dest: {"from": src, "type": "rename"|"copy"}}`` for added files whose exact contents
    existed at another path in the first parent."""

    name, eager, depends_on = "copies", True, ("tree",)

    def derive(self, repo, cs_id, cs, parent_values):
        result = {}
        root = repo.root_tree(cs.first_parent) if cs.first_parent else None
        if root is not None:
            deleted = {}
            for c in cs.changes:
                if c.op == OP_DELETE:
                    e = repo.trees.lookup(root, c.path)
                    if e is not None:
                        deleted.setdefault(e[1], c.path)
            for c in cs.changes:
                if c.op != OP_ADD:
                    continue
                if c.blob in deleted:
                    result[c.path] = {"from": deleted[c.blob], "type": "rename"}
                    continue
                for cand in repo.meta.blob_index_paths(c.blob):
                    e = repo.trees.lookup(root, cand) if cand != c.path else None
                    if e is not None and e[0] != KIND_DIR and e[1] == c.blob:
                        result[c.path] = {"from": cand, "type": "copy"}
                        break
        repo.meta.blob_index_add((c.blob, c.path) for c in cs.changes if c.op != OP_DELETE)
        return json.dumps(result, sort_keys=True, separators=(",", ":"))


# -- path search -------------------------------------------------------------------------------
BLOOM_BITS = 2048


def name_trigrams(name: str) -> set[str]:
    s = name.lower()
    return {s} if len(s) < 3 else {s[i:i + 3] for i in range(len(s) - 2)}


def _bits(gram: str) -> tuple[int, int]:
    h = hashlib.blake2b(gram.encode(), digest_size=8).digest()
    return int.from_bytes(h[:4], "big") % BLOOM_BITS, int.from_bytes(h[4:], "big") % BLOOM_BITS


def bloom_of(grams) -> int:
    v = 0
    for g in grams:
        a, b = _bits(g)
        v |= (1 << a) | (1 << b)
    return v


@functools.lru_cache(maxsize=16384)
def name_bloom(name: str) -> int:
    """The bloom bits of one file or directory name; names recur in every commit that rewrites
    their directory, so they are hashed once."""
    return bloom_of(name_trigrams(name))


def bloom_may_contain(bloom: int, grams) -> bool:
    for g in grams:
        a, b = _bits(g)
        if not (bloom >> a) & 1 or not (bloom >> b) & 1:
            return False
    return True


class _SearchCodec(TreeCodec):
    """Search-tree entries: (kind, id, bloom). A directory's bloom holds the trigrams of every
    name beneath it, so a search can skip whole subtrees without reading them."""

    def __init__(self, repo):
        self.repo = repo

    def read(self, node_id):
        return self.repo.read_stree(node_id)

    def write(self, entries, path):
        rows = [[n, e[0], e[1], format(e[2], "x")] for n, e in sorted(entries.items())]
        payload = json.dumps(rows, separators=(",", ":")).encode()
        oid = self.repo.objects.put("stree", payload)
        self.repo.cache.put(("stree", oid), dict(entries), len(payload))  # write-through, as TreeOps.write
        return oid

    def child(self, entry):
        return entry[1]

    def file_entry(self, path, change, old_entry):
        return (change[0], change[1], 0)

    def dir_entry(self, path, child_id, child_entries, old_entry):
        bloom = 0
        for name, e in child_entries.items():
            bloom |= name_bloom(name) | (e[2] if e[0] == KIND_DIR else 0)
        return (KIND_DIR, child_id, bloom)


class SearchTreeType(DerivedType):
    name, eager = "search", True

    def derive(self, repo, cs_id, cs, parent_values):
        return apply_augmented(_SearchCodec(repo), parent_values[0] if parent_values else None, changes_map(cs))


# -- blame ----------------------------------------------------------------------------------------
def split_lines(data: bytes) -> list[bytes]:
    return data.splitlines(keepends=True)


def expand_runs(runs) -> list[tuple[str, int]]:
    return [(cs, start + i) for cs, start, count in runs for i in range(count)]


def compress_runs(attr) -> list:
    runs: list = []
    for cs, line in attr:
        if runs and runs[-1][0] == cs and runs[-1][1] + runs[-1][2] == line:
            runs[-1][2] += 1
        else:
            runs.append([cs, line, 1])
    return runs


class BlameType(DerivedType):
    """``{path: blame_object_id | "binary"}`` for every file the changeset adds or modifies.

    A blame object is ``{"runs": [[changeset, origin_line, count], ...]}``. A file's blame comes
    from the blame of its previous version on the first parent (or of its copy source) plus a line
    diff, so the cost is proportional to the change. Deferred: computed on first use (FR-DD-03)."""

    name, eager, depends_on = "blame", False, ("history", "copies")

    def derive(self, repo, cs_id, cs, parent_values):
        result = {}
        copies = json.loads(repo.derived.get("copies", cs_id))
        for c in cs.changes:
            if c.op == OP_DELETE:
                continue
            data = repo.read_blob(c.blob)
            if is_binary(data):
                result[c.path] = "binary"
                continue
            new_lines = split_lines(data)
            attr = [(cs_id, i + 1) for i in range(len(new_lines))]
            prev = None
            if cs.first_parent:
                prev = repo.previous_version(cs.first_parent, copies.get(c.path, {}).get("from", c.path))
            if prev is not None and prev[1] != "binary":
                old_lines = split_lines(repo.read_blob(prev[0]))
                old_attr = expand_runs(repo.read_blame(prev[1]))
                for tag, i1, i2, j1, j2 in linediff.opcodes(old_lines, new_lines):
                    if tag == "equal":
                        attr[j1:j2] = old_attr[i1:i2]
            payload = json.dumps({"runs": compress_runs(attr)}, separators=(",", ":")).encode()
            result[c.path] = repo.objects.put("blame", payload)
        return json.dumps(result, sort_keys=True, separators=(",", ":"))


# -- content search -----------------------------------------------------------------------------------
CONTENT_MAX_BYTES = 1 << 20


def text_trigrams(text: str) -> set[str]:
    s = text.lower()
    return {s[i:i + 3] for i in range(len(s) - 2)}


class ContentIndexType(DerivedType):
    """``{"indexed": n}``: the trigrams of every text blob the changeset adds or modifies are recorded
    once (ADR-16), so content search reads only blobs that can match (FR-SR-03). Binary blobs are not
    indexed; text blobs over 1 MiB are marked and always read. Deferred: built on the first search at
    a revision, or by a backfill."""

    name, eager, depends_on = "content", False, ("copies",)  # copies fills the blob → path index

    def derive(self, repo, cs_id, cs, parent_values):
        n = 0
        for c in cs.changes:
            if c.op == OP_DELETE or c.kind == KIND_LINK or repo.meta.content_status(c.blob) is not None:
                continue
            data = repo.read_blob(c.blob)
            if is_binary(data):
                repo.meta.content_add(c.blob, "b", ())
            elif len(data) > CONTENT_MAX_BYTES:
                repo.meta.content_add(c.blob, "l", ())
            else:
                repo.meta.content_add(c.blob, "i", text_trigrams(data.decode("utf-8", "replace")))
            n += 1
        return json.dumps({"indexed": n})


def register_default_types(manager) -> None:
    for t in (RootTreeType(), GraphType(), HistoryTreeType(), CopyInfoType(), SearchTreeType(), BlameType(),
              ContentIndexType()):
        manager.register(t)

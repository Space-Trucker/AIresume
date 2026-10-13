"""The authoritative, server-side repository.

The server, not the client, answers history and blame queries, creates commits, and performs
merges, rebases and reverts.  Nothing here materializes the whole repository.  Every operation
touches only the paths and changesets it needs.
"""
from __future__ import annotations

import difflib
import heapq
import json
import os
import re
import time
import zlib
from collections import Counter

from .changeset import OP_ADD, OP_DELETE, OP_MODIFY, Changeset, FileChange
from .derived import DerivedDataManager
from .derived_types import expand_runs, register_default_types, split_lines
from .iam import PermissionDenied, Policy
from .merge3 import merge3
from .meta import MetaStore
from .objects import (
    EMPTY_TREE_ID,
    FILE_KINDS,
    KIND_DIR,
    decode_htree,
    is_binary,
    is_object_id,
    normalize_path,
    split_path,
)
from .storage import FileObjectStore, LRUCache
from .trees import PathConflict, TreeOps

# Flags used by the object protocol.
F_RESTRICTED = 0x1   # served, but must not be cached by intermediate tiers
F_MISSING = 0x2      # unknown object
F_DENIED = 0x4       # exists but the caller may not read it

PUBLIC_OBJECT_TYPES = (b"blob", b"tree")

REF_NAME_RE = re.compile(r"^[A-Za-z0-9._/-]+$")


class NotFound(Exception):
    pass


class MergeConflict(Exception):
    def __init__(self, conflicts: list[dict], at: str | None = None):
        self.conflicts = conflicts
        self.at = at
        paths = ", ".join(c["path"] for c in conflicts[:5])
        super().__init__(f"conflicts in {len(conflicts)} file(s): {paths}")


def _entry_api(e):
    return None if e is None else {"kind": e[0], "id": e[1]}


class Repository:
    def __init__(self, root: str, policy: Policy | None = None):
        self.root = root
        os.makedirs(root, exist_ok=True)
        self.objects = FileObjectStore(os.path.join(root, "objects"))
        self.meta = MetaStore(os.path.join(root, "meta.db"))
        self.cache = LRUCache(300_000)
        self.trees = TreeOps(self.objects, self.cache)
        self.policy = policy or Policy()
        self.derived = DerivedDataManager(self)
        register_default_types(self.derived)
        self.stats: Counter = Counter()
        self.objects.put("tree", b"")  # the empty tree always exists

    # =========================================================================================
    # Objects
    # =========================================================================================
    def put_blob(self, data: bytes) -> str:
        return self.objects.put("blob", data)

    def read_blob(self, oid: str) -> bytes:
        return self.objects.get_payload(oid, "blob")

    def _cached(self, kind: str, oid: str, loader):
        v = self.cache.get((kind, oid))
        if v is None:
            v = loader()
            self.cache.put((kind, oid), v)
        return v

    def read_htree(self, oid: str) -> dict:
        return self._cached("htree", oid, lambda: decode_htree(self.objects.get_payload(oid, "htree")))

    def read_stree(self, oid: str) -> dict:
        def load():
            rows = json.loads(self.objects.get_payload(oid, "stree"))
            return {r[0]: (r[1], r[2], int(r[3], 16)) for r in rows}
        return self._cached("stree", oid, load)

    def read_blame(self, oid: str) -> list:
        return self._cached("blame", oid, lambda: json.loads(self.objects.get_payload(oid, "blame"))["runs"])

    def htree_lookup(self, root: str, path: str):
        node = (KIND_DIR, "", None, root)
        for part in split_path(path):
            if node[0] != KIND_DIR:
                return None
            node = self.read_htree(node[3]).get(part)
            if node is None:
                return None
        return node

    def apply_to_tree(self, base: str | None, changes: dict) -> str:
        restricted = self.policy.restricted_prefixes()
        if not restricted:
            return self.trees.apply(base, changes)
        written: list[tuple[str, str]] = []
        root = self.trees.apply(base, changes, on_write=lambda p, k, o: written.append((p, o)))
        self._record_acl(written)
        return root

    def _record_acl(self, written: list[tuple[str, str]]) -> None:
        rows, public = [], []
        for path, oid in written:
            prefix = self.policy.restricted_prefix(path)
            if prefix is not None:
                rows.append((oid, prefix))
            else:
                public.append(oid)
        if public:
            # Identical bytes at a public path are public, whether the restricted copy was
            # recorded earlier or in this same batch.
            restricted_now = {oid for oid, _ in rows}
            known = self.meta.acl_known(public) | (restricted_now & set(public))
            rows.extend((oid, "") for oid in known)
        for oid in {oid for oid, prefix in rows if prefix}:
            # ...and so are bytes that already appeared at a public path in earlier changesets.
            if any(self.policy.restricted_prefix(p) is None for p in self.meta.blob_index_paths(oid, 50)):
                rows.append((oid, ""))
        if rows:
            self.meta.acl_add(rows)

    def reindex_acl(self, rev: str = "main") -> int:
        """Record ACLs for every object reachable from ``rev`` (run after a policy change)."""
        root = self.root_tree(self.resolve(rev))
        written: list[tuple[str, str]] = [("", root)]
        stack = [(root, "")]
        while stack:
            tid, prefix = stack.pop()
            for name, (kind, oid) in self.trees.read(tid).items():
                path = f"{prefix}/{name}" if prefix else name
                written.append((path, oid))
                if kind == KIND_DIR:
                    stack.append((oid, path))
        self._record_acl(written)
        return len(written)

    def fetch_objects(self, ids: list[str], user: str | None) -> list[tuple[str, int, bytes]]:
        """The authoritative end of the object protocol."""
        known = self.meta.acl_known(ids)
        out = []
        for oid in ids:
            stored = self.objects.get_stored(oid) if is_object_id(oid) else None
            if stored is None or _stored_type(stored) not in PUBLIC_OBJECT_TYPES:
                out.append((oid, F_MISSING, b""))
                self.stats["objects.missing"] += 1
                continue
            flags = 0
            if oid in known:
                prefixes = self.meta.acl_prefixes(oid)
                if "" in prefixes:
                    flags = 0
                elif any(self.policy.can_read_prefix(user, p) for p in prefixes):
                    flags = F_RESTRICTED
                else:
                    out.append((oid, F_DENIED, b""))
                    self.stats["objects.denied"] += 1
                    continue
            out.append((oid, flags, stored))
            self.stats["objects.served"] += 1
        return out

    # =========================================================================================
    # Changesets and revisions
    # =========================================================================================
    def get_changeset(self, cs_id: str) -> Changeset:
        hit = self.cache.get(("cs", cs_id))
        if hit is not None:
            return hit
        data = self.meta.get_changeset_data(cs_id)
        if data is None:
            raise NotFound(f"unknown changeset {cs_id}")
        cs = Changeset.decode(data)
        self.cache.put(("cs", cs_id), cs)
        return cs

    def resolve(self, rev: str) -> str:
        """Resolve a ref name, full id, unique id prefix, with optional ``~N`` / ``^N`` suffixes."""
        if not rev:
            raise NotFound("empty revision")
        m = re.match(r"^(.*?)((?:[~^]\d*)*)$", rev)
        base, suffix = m.group(1), m.group(2)
        ref = self.meta.get_ref(base)
        if ref is not None:
            cs = ref[0]
        elif is_object_id(base) and self.meta.has_changeset(base):
            cs = base
        elif len(base) >= 4 and re.fullmatch(r"[0-9a-fA-F]+", base):
            matches = self.meta.resolve_prefix(base)
            if not matches:
                raise NotFound(f"unknown revision {rev}")
            if len(matches) > 1:
                raise NotFound(f"ambiguous revision prefix {base}")
            cs = matches[0]
        else:
            raise NotFound(f"unknown revision {rev}")
        for op, num in re.findall(r"([~^])(\d*)", suffix):
            n = int(num) if num else 1
            if op == "~":
                nxt = self.fp_ancestor(cs, n)
            else:
                parents = self.get_changeset(cs).parents
                nxt = parents[n - 1] if 0 < n <= len(parents) else None
            if nxt is None:
                raise NotFound(f"revision {rev} does not exist")
            cs = nxt
        return cs

    def root_tree(self, cs_id: str | None) -> str:
        if cs_id is None:
            return EMPTY_TREE_ID
        return self.derived.get("tree", cs_id)

    def history_root(self, cs_id: str) -> str:
        return self.derived.get("history", cs_id)

    def search_root(self, cs_id: str) -> str:
        return self.derived.get("search", cs_id)

    def graph(self, cs_id: str) -> dict:
        hit = self.cache.get(("graph", cs_id))
        if hit is None:
            hit = json.loads(self.derived.get("graph", cs_id))
            self.cache.put(("graph", cs_id), hit)
        return hit

    def generation(self, cs_id: str) -> int:
        return self.graph(cs_id)["g"]

    def changeset_api(self, cs_id: str) -> dict:
        d = self.get_changeset(cs_id).to_api(cs_id)
        d["generation"] = self.generation(cs_id)
        d["copies"] = json.loads(self.derived.get("copies", cs_id))
        return d

    # =========================================================================================
    # Writes: changesets are created on the server
    # =========================================================================================
    def create_changeset(self, parents: list[str], files: list[dict], author: str, message: str,
                         timestamp: int | None = None, extra: dict | None = None,
                         user: str | None = None) -> str:
        """Create a changeset from a list of file updates relative to the first parent.

        Each entry of ``files`` is one of
            {"path": p, "delete": True}
            {"path": p, "kind": "f"|"x"|"l", "blob": <id of an uploaded blob>}
            {"path": p, "kind": "f"|"x"|"l", "content": <bytes>}

        This does not take locks or move refs: the changeset is appended to the log under its
        content hash, its tree is computed incrementally, and eager derived data is filled in.
        """
        parents = [self.resolve(p) for p in parents]
        if len(set(parents)) != len(parents):
            raise ValueError("duplicate parents")
        base_root = self.root_tree(parents[0]) if parents else None
        changes: list[FileChange] = []
        tree_changes: dict = {}
        for f in files:
            path = normalize_path(f["path"])
            if not path:
                raise ValueError("empty path")
            if path in tree_changes or any(c.path == path for c in changes):
                raise ValueError(f"duplicate path {path}")
            if user is not None and not self.policy.can_write(user, path):
                raise PermissionDenied(f"{user} may not write {path}")
            old = self.trees.lookup(base_root, path) if base_root else None
            old_file = old if old is not None and old[0] != KIND_DIR else None
            if f.get("delete"):
                if old_file is None:
                    raise ValueError(f"cannot delete {path}: no such file")
                changes.append(FileChange(path, OP_DELETE))
                tree_changes[path] = None
                continue
            kind = f.get("kind", "f")
            if kind not in FILE_KINDS:
                raise ValueError(f"bad kind {kind!r} for {path}")
            if f.get("blob"):
                blob = f["blob"]
                if not self.objects.has(blob):
                    raise ValueError(f"blob {blob} for {path} has not been uploaded")
            else:
                blob = self.put_blob(f.get("content", b""))
            if old_file == (kind, blob):
                continue  # no-op
            op = OP_MODIFY if old_file else OP_ADD
            changes.append(FileChange(path, op, kind, blob))
            tree_changes[path] = (kind, blob)
        try:
            new_root = self.apply_to_tree(base_root, tree_changes)
        except PathConflict as e:
            raise ValueError(str(e)) from None
        cs = Changeset(
            parents=tuple(parents),
            author=author,
            message=message,
            timestamp=int(timestamp if timestamp is not None else time.time()),
            changes=tuple(sorted(changes, key=lambda c: c.path)),
            extra=extra or {},
        )
        cs_id = cs.id
        if self.meta.insert_changeset(cs_id, cs.encode()):
            self.stats["changesets.created"] += 1
        self.derived.put("tree", cs_id, new_root)
        self.derived.derive_eager(cs_id)
        return cs_id

    # =========================================================================================
    # Refs: optional, and moved only by compare-and-swap
    # =========================================================================================
    def get_ref(self, name: str) -> str | None:
        r = self.meta.get_ref(name)
        return r[0] if r else None

    def update_ref(self, name: str, old: str | None, new: str | None, user: str | None = None) -> bool:
        if not REF_NAME_RE.match(name) or ".." in name:
            raise ValueError(f"invalid ref name {name!r}")
        if user is not None and not self.policy.can_update_ref(user, name):
            raise PermissionDenied(f"{user} may not move {name}")
        if new is not None:
            new = self.resolve(new)
        if old is not None:
            old = self.resolve(old) if not is_object_id(old) else old
        return self.meta.cas_ref(name, old, new, who=user or "")

    # =========================================================================================
    # Reads
    # =========================================================================================
    def lookup(self, cs_id: str, path: str):
        return self.trees.lookup(self.root_tree(cs_id), normalize_path(path))

    def read_file(self, cs_id: str, path: str, user: str | None = None) -> tuple[str, str, bytes]:
        path = normalize_path(path)
        if user is not None and not self.policy.can_read(user, path):
            raise PermissionDenied(f"{user} may not read {path}")
        e = self.lookup(cs_id, path)
        if e is None or e[0] == KIND_DIR:
            raise NotFound(f"{path}: no such file at {cs_id[:12]}")
        return e[0], e[1], self.read_blob(e[1])

    def list_dir(self, cs_id: str, path: str = "", user: str | None = None) -> list[dict]:
        path = normalize_path(path)
        e = self.lookup(cs_id, path)
        if e is None or e[0] != KIND_DIR:
            raise NotFound(f"{path}: not a directory")
        out = []
        for name, (kind, oid) in sorted(self.trees.read(e[1]).items()):
            child = f"{path}/{name}" if path else name
            if user is not None and not self.policy.can_read(user, child):
                continue
            out.append({"name": name, "path": child, "kind": kind, "id": oid})
        return out

    def diff(self, a: str | None, b: str, paths: list[str] | None = None,
             user: str | None = None) -> list[dict]:
        ra = self.root_tree(a)
        rb = self.root_tree(b)
        out = []
        for path, x, y in self._scoped_diff(ra, rb, paths):
            if user is not None and not self.policy.can_read(user, path):
                continue
            status = "A" if x is None else "D" if y is None else "M"
            out.append({"path": path, "status": status, "old": _entry_api(x), "new": _entry_api(y)})
        return out

    def _scoped_diff(self, ra: str, rb: str, paths: list[str] | None):
        if not paths:
            yield from self.trees.diff(ra, rb)
            return
        for p in sorted({normalize_path(p) for p in paths}):
            ea = self.trees.lookup(ra, p)
            eb = self.trees.lookup(rb, p)
            da = ea[1] if ea and ea[0] == KIND_DIR else None
            db = eb[1] if eb and eb[0] == KIND_DIR else None
            if da or db:
                yield from self.trees.diff(da, db, p)
            fa = ea if ea and ea[0] != KIND_DIR else None
            fb = eb if eb and eb[0] != KIND_DIR else None
            if fa != fb:
                yield (p, fa, fb)

    def diff_text(self, a: str | None, b: str, paths: list[str] | None = None,
                  user: str | None = None, context: int = 3) -> str:
        chunks = []
        for f in self.diff(a, b, paths, user):
            old = self.read_blob(f["old"]["id"]) if f["old"] else b""
            new = self.read_blob(f["new"]["id"]) if f["new"] else b""
            a_name = f"a/{f['path']}" if f["old"] else "/dev/null"
            b_name = f"b/{f['path']}" if f["new"] else "/dev/null"
            if is_binary(old) or is_binary(new):
                chunks.append(f"Binary files {a_name} and {b_name} differ\n")
                continue
            lines = difflib.unified_diff(
                old.decode("utf-8", "replace").splitlines(keepends=True),
                new.decode("utf-8", "replace").splitlines(keepends=True),
                a_name, b_name, n=context,
            )
            chunks.append("".join(l if l.endswith("\n") else l + "\n\\ No newline at end of file\n" for l in lines))
        return "".join(chunks)

    def log(self, rev: str, limit: int = 50, first_parent: bool = True, path: str | None = None,
            skip: int = 0) -> list[str]:
        start = self.resolve(rev)
        if path:
            return [h["cs"] for h in self.file_history(start, path, limit + skip)][skip:]
        out: list[str] = []
        if first_parent:
            cur: str | None = start
            while cur and len(out) < limit + skip:
                out.append(cur)
                cur = self.get_changeset(cur).first_parent
        else:
            seen = {start}
            heap = [(-self.generation(start), start)]
            while heap and len(out) < limit + skip:
                _, x = heapq.heappop(heap)
                out.append(x)
                for p in self.get_changeset(x).parents:
                    if p not in seen:
                        seen.add(p)
                        heapq.heappush(heap, (-self.generation(p), p))
        return out[skip:]

    def file_history(self, rev: str, path: str, limit: int = 100, follow_copies: bool = True,
                     user: str | None = None) -> list[dict]:
        """Changesets that changed ``path`` (a file or a directory), newest first.

        Each step is a lookup in a history tree, so the cost is O(path depth) per result,
        independent of how many unrelated changesets sit in between."""
        cur: str | None = self.resolve(rev)
        path = normalize_path(path)
        if user is not None and not self.policy.can_read(user, path):
            raise PermissionDenied(f"{user} may not read {path}")
        if not path:
            return [{"cs": c, "path": ""} for c in self.log(cur, limit)]
        out: list[dict] = []
        is_dir: bool | None = None
        while cur and len(out) < limit:
            e = self.htree_lookup(self.history_root(cur), path)
            if e is None:
                break
            if is_dir is None:
                is_dir = e[0] == KIND_DIR
            elif is_dir != (e[0] == KIND_DIR):
                break  # the path was a directory before it was a file (or vice versa)
            last = e[2]
            out.append({"cs": last, "path": path})
            if follow_copies and e[0] != KIND_DIR:
                copies = json.loads(self.derived.get("copies", last))
                if path in copies:
                    path = copies[path]["from"]
            cur = self.get_changeset(last).first_parent
        return out

    def blame_object_for(self, cs_id: str, path: str) -> str:
        return json.loads(self.derived.get("blame", cs_id))[path]

    def previous_version(self, parent: str, path: str):
        e = self.htree_lookup(self.history_root(parent), path)
        if e is None or e[0] == KIND_DIR:
            return None
        return e[1], self.blame_object_for(e[2], path)

    def blame(self, rev: str, path: str, user: str | None = None) -> dict:
        cs_id = self.resolve(rev)
        path = normalize_path(path)
        if user is not None and not self.policy.can_read(user, path):
            raise PermissionDenied(f"{user} may not read {path}")
        e = self.htree_lookup(self.history_root(cs_id), path)
        if e is None or e[0] == KIND_DIR:
            raise NotFound(f"{path}: no such file")
        blame_id = self.blame_object_for(e[2], path)
        data = self.read_blob(e[1])
        if blame_id == "binary":
            return {"path": path, "binary": True, "lines": []}
        attr = expand_runs(self.read_blame(blame_id))
        lines = split_lines(data)
        info: dict[str, dict] = {}
        out = []
        for i, (line, (c, origin)) in enumerate(zip(lines, attr)):
            if c not in info:
                cs = self.get_changeset(c)
                info[c] = {"author": cs.author, "timestamp": cs.timestamp, "summary": cs.summary()}
            out.append({"line": i + 1, "cs": c, "origin_line": origin,
                        "text": line.decode("utf-8", "replace")})
        return {"path": path, "binary": False, "lines": out, "changesets": info}

    # =========================================================================================
    # Ancestry: generation numbers + skip lists
    # =========================================================================================
    def fp_ancestor(self, cs_id: str, n: int) -> str | None:
        """The first-parent ancestor ``n`` steps away, in O(log n) skip-list hops."""
        cur = cs_id
        while n > 0:
            skips = self.graph(cur)["s"]
            if not skips:
                return None
            k = min(n.bit_length() - 1, len(skips) - 1)
            cur = skips[k]
            n -= 1 << k
            self.stats["ancestry.hops"] += 1
        return cur

    def is_ancestor(self, a: str, b: str) -> bool:
        """Is ``a`` an ancestor of (or equal to) ``b``?"""
        a, b = self.resolve(a), self.resolve(b)
        ga = self.generation(a)
        seen: set[str] = set()
        stack = [b]
        while stack:
            x = stack.pop()
            if x == a:
                return True
            if x in seen:
                continue
            seen.add(x)
            g = self.graph(x)
            self.stats["ancestry.visits"] += 1
            if g["g"] <= ga:
                continue
            steps = min(g["l"], g["g"] - ga)
            if steps > 1:
                stack.append(self.fp_ancestor(x, steps))
                continue
            stack.extend(self.get_changeset(x).parents)
        return False

    def merge_bases(self, a: str, b: str) -> list[str]:
        a, b = self.resolve(a), self.resolve(b)
        if a == b:
            return [a]
        if self.is_ancestor(a, b):
            return [a]
        if self.is_ancestor(b, a):
            return [b]
        PA, PB, STALE = 1, 2, 4
        flags = {a: PA, b: PB}
        heap = [(-self.generation(a), a), (-self.generation(b), b)]
        heapq.heapify(heap)
        results: list[str] = []
        while heap and any(not flags[x] & STALE for _, x in heap):
            ng, x = heapq.heappop(heap)
            f = flags[x]
            self.stats["ancestry.visits"] += 1
            if f & (PA | PB) == (PA | PB):
                if not f & STALE:
                    results.append(x)
                    f |= STALE
                    flags[x] = f
            elif not f & STALE:
                # Skip through a single-parent run that the other side cannot reach.
                other = PB if f & PA else PA
                g = self.graph(x)
                gmax_other = max((-h for h, y in heap if flags[y] & other), default=0)
                steps = min(g["l"], g["g"] - gmax_other)
                if steps >= 2:
                    y = self.fp_ancestor(x, steps)
                    nf = flags.get(y, 0) | f
                    if nf != flags.get(y, 0):
                        flags[y] = nf
                        heapq.heappush(heap, (-self.generation(y), y))
                    continue
            for p in self.get_changeset(x).parents:
                pf = flags.get(p, 0)
                nf = pf | (f & (PA | PB | STALE))
                if nf != pf:
                    flags[p] = nf
                    heapq.heappush(heap, (-self.generation(p), p))
        results = [r for r in results if not any(r != s and self.is_ancestor(r, s) for s in results)]
        return sorted(results, key=lambda r: -self.generation(r))

    def merge_base(self, a: str, b: str) -> str | None:
        bases = self.merge_bases(a, b)
        return bases[0] if bases else None

    # =========================================================================================
    # Merge, rebase, revert: all server-side
    # =========================================================================================
    def _file_at(self, root: str, path: str):
        return self.trees.lookup(root, path)

    def _three_way(self, paths, base_root: str, ours_root: str, theirs_root: str):
        """Apply the base→theirs change at each path on top of ours."""
        changes: dict[str, tuple | None] = {}
        conflicts: list[dict] = []
        for path in paths:
            b = self._file_at(base_root, path)
            if b is not None and b[0] == KIND_DIR:
                b = None  # no file here in the base (it was a directory)
            o = self._file_at(ours_root, path)
            t = self._file_at(theirs_root, path)
            if t == b:
                continue
            if o is not None and o[0] == KIND_DIR or t is not None and t[0] == KIND_DIR:
                conflicts.append({"path": path, "reason": "file/directory conflict"})
                continue
            if o == b:
                changes[path] = t
                continue
            if o == t:
                continue
            reason = "both sides changed"
            if o is not None and t is not None and "l" not in (o[0], t[0]) and (b is None or b[0] != "l"):
                base_data = self.read_blob(b[1]) if b is not None else b""
                od, td = self.read_blob(o[1]), self.read_blob(t[1])
                if not (is_binary(base_data) or is_binary(od) or is_binary(td)):
                    merged, n = merge3(base_data, od, td)
                    if n == 0:
                        kind = t[0] if b is None or t[0] != b[0] else o[0]
                        changes[path] = (kind, self.put_blob(merged))
                        continue
                    reason = f"{n} conflicting hunk(s)"
                else:
                    reason = "binary file changed on both sides"
            elif o is None or t is None:
                reason = "modified on one side, deleted on the other"
            conflicts.append({"path": path, "reason": reason, "base": _entry_api(b),
                              "ours": _entry_api(o), "theirs": _entry_api(t)})
        return changes, conflicts

    @staticmethod
    def _files_from(changes: dict) -> list[dict]:
        out = []
        for path, e in sorted(changes.items()):
            if e is None:
                out.append({"path": path, "delete": True})
            else:
                out.append({"path": path, "kind": e[0], "blob": e[1]})
        return out

    def _create_or_conflict(self, parents, changes, author, message, timestamp=None, extra=None,
                            user=None, at=None):
        files = [f for f in self._files_from(changes)
                 if not (f.get("delete") and self._file_at(self.root_tree(parents[0]), f["path"]) is None)]
        try:
            return self.create_changeset(parents, files, author, message, timestamp, extra, user)
        except ValueError as e:
            raise MergeConflict([{"path": "", "reason": str(e)}], at=at) from None

    def merge(self, ours: str, theirs: str, author: str, message: str | None = None,
              ff: bool = False, user: str | None = None) -> str:
        ours, theirs = self.resolve(ours), self.resolve(theirs)
        if self.is_ancestor(theirs, ours):
            return ours
        if ff and self.is_ancestor(ours, theirs):
            return theirs
        base = self.merge_base(ours, theirs)
        base_root = self.root_tree(base)
        paths = [p for p, _, _ in self.trees.diff(base_root, self.root_tree(theirs))]
        changes, conflicts = self._three_way(paths, base_root, self.root_tree(ours), self.root_tree(theirs))
        if conflicts:
            raise MergeConflict(conflicts)
        msg = message or f"Merge {theirs[:12]} into {ours[:12]}"
        return self._create_or_conflict([ours, theirs], changes, author, msg, user=user)

    def rebase(self, head: str, onto: str, base: str | None = None, user: str | None = None) -> dict:
        """Rebase the stack of changesets between ``base`` (default: the merge base) and
        ``head`` onto ``onto``.  Returns ``{"head": new_head, "rebased": {old: new}}``."""
        head, onto = self.resolve(head), self.resolve(onto)
        if self.is_ancestor(head, onto):
            return {"head": onto, "rebased": {}}
        mb = self.resolve(base) if base else self.merge_base(head, onto)
        if mb is None:
            raise ValueError("no common ancestor")
        if mb == onto:
            return {"head": head, "rebased": {}}
        stack = []
        cur = head
        while cur != mb:
            cs = self.get_changeset(cur)
            if len(cs.parents) != 1:
                raise ValueError(f"cannot rebase merge changeset {cur[:12]}")
            stack.append(cur)
            cur = cs.parents[0]
        stack.reverse()
        new_parent = onto
        mapping: dict[str, str] = {}
        for c in stack:
            cs = self.get_changeset(c)
            changes, conflicts = self._three_way(
                [ch.path for ch in cs.changes],
                self.root_tree(cs.parents[0]), self.root_tree(new_parent), self.root_tree(c),
            )
            if conflicts:
                raise MergeConflict(conflicts, at=c)
            if not changes and cs.changes:
                mapping[c] = new_parent  # already applied upstream: drop it
                continue
            new = self._create_or_conflict(
                [new_parent], changes, cs.author, cs.message, cs.timestamp,
                {**cs.extra, "rebased_from": c}, user=user, at=c,
            )
            mapping[c] = new
            new_parent = new
        return {"head": new_parent, "rebased": mapping}

    def revert(self, cs_id: str, onto: str, author: str, message: str | None = None,
               user: str | None = None) -> str:
        cs_id, onto = self.resolve(cs_id), self.resolve(onto)
        cs = self.get_changeset(cs_id)
        changes, conflicts = self._three_way(
            [c.path for c in cs.changes],
            self.root_tree(cs_id), self.root_tree(onto), self.root_tree(cs.first_parent),
        )
        if conflicts:
            raise MergeConflict(conflicts, at=cs_id)
        msg = message or f'Revert "{cs.summary()}"\n\nThis reverts changeset {cs_id}.'
        return self._create_or_conflict([onto], changes, author, msg,
                                        extra={"reverts": cs_id}, user=user)

    # =========================================================================================
    def close(self) -> None:
        self.meta.close()

    def info(self) -> dict:
        return {
            "changesets": self.meta.count_changesets(),
            "refs": {name: target for name, target, _ in self.meta.list_refs()},
            "derived": {t: self.meta.derived_count(t) for t in self.derived.types},
            "eager": self.derived.eager_types,
        }


def _stored_type(stored: bytes) -> bytes:
    head = zlib.decompressobj().decompress(stored, 8)
    return head.split(b"\0", 1)[0]

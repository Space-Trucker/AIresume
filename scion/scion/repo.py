"""The authoritative, server-side repository (Repository, 06 §6.5).

The server, not the client, creates commits and answers history, blame, ancestry and diff queries;
it also performs merges, rebases and reverts (FR-CS-01, FR-QRY-*, FR-WR-02…04). Nothing here
materializes the whole repository (FR-OBJ-05): every operation touches only the paths and
changesets it needs.
"""
from __future__ import annotations

import difflib
import hashlib
import heapq
import json
import os
import re
import time
from collections import Counter

from .changeset import OP_ADD, OP_DELETE, OP_MODIFY, Changeset, FileChange
from .derived import DerivedDataManager
from .derived_types import expand_runs, register_default_types, split_lines
from .iam import PermissionDenied
from .merge3 import merge3
from .meta import MetaStore, SqliteMetaStore
from .objects import (EMPTY_TREE_ID, F_DENIED, F_MISSING, F_RESTRICTED, FILE_KINDS, KIND_DIR, KIND_LINK,
                      PUBLIC_TYPES, ObjectTooLarge, blob_id, decode_htree, decode_limited, is_binary,
                      is_object_id,
                      normalize_path, split_path, stored_type)
from .storage import FileObjectStore, LRUCache
from .trees import PathConflict, TreeOps

REF_NAME = re.compile(r"^[A-Za-z0-9._/-]+$")
CACHE_BYTES = 64 << 20  # decoded trees, history and search trees, changesets (by encoded size)


class NotFound(Exception):
    pass


class MergeConflict(Exception):
    def __init__(self, conflicts: list[dict], at: str | None = None):
        self.conflicts, self.at = conflicts, at
        super().__init__(f"conflicts in {len(conflicts)} path(s): " + ", ".join(c["path"] for c in conflicts[:5]))


class OpenPolicy:
    """Allow-everything policy used until IAM is configured (iam.Policy implements the same interface)."""

    def can_read(self, user, path=""):
        return True

    def can_read_repo(self, user):
        return True

    def can_write(self, user, path=""):
        return True

    def can_update_ref(self, user, ref):
        return True

    def restricted_prefix(self, path):
        return None

    def restricted_prefixes(self):
        return []

    def acl_entry(self, path):
        return ""


def _api_entry(e):
    return None if e is None else {"kind": e[0], "id": e[1]}


class Repository:
    def __init__(self, root: str, policy=None, name: str = "main", meta: MetaStore | None = None):
        """``meta`` is the repository's metadata store; by default a SQLite file in ``root``."""
        self.root, self.name = root, name
        os.makedirs(root, exist_ok=True)
        self.objects = FileObjectStore(os.path.join(root, "objects"))
        self.meta = meta if meta is not None else SqliteMetaStore(os.path.join(root, "meta.db"))
        self.cache = LRUCache(300_000, max_bytes=CACHE_BYTES)
        self.trees = TreeOps(self.objects, self.cache)
        self.policy = policy or OpenPolicy()
        self.audit = None  # an audit.AuditLog, set by the deployment (FR-IAM-10)
        self.derived = DerivedDataManager(self)
        register_default_types(self.derived)
        self.stats: Counter = Counter()
        self.objects.put("tree", b"")  # the empty tree always exists

    def close(self) -> None:
        self.meta.close()

    # ================================================================================== objects
    def put_blob(self, data: bytes) -> str:
        return self.objects.put("blob", data)

    def read_blob(self, oid: str) -> bytes:
        return self.objects.get_payload(oid, "blob")

    def _cached(self, otype: str, oid: str, decode):
        v = self.cache.get((otype, oid))
        if v is None:
            payload = self.objects.get_payload(oid, otype)
            v = decode(payload)
            self.cache.put((otype, oid), v, len(payload))
        return v

    def read_htree(self, oid: str) -> dict:
        return self._cached("htree", oid, decode_htree)

    def read_stree(self, oid: str) -> dict:
        return self._cached("stree", oid, lambda p: {r[0]: (r[1], r[2], int(r[3], 16)) for r in json.loads(p)})

    def read_blame(self, oid: str) -> list:
        return self._cached("blame", oid, lambda p: json.loads(p)["runs"])

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
        """Build a new root tree, recording in the object index where every new tree and file
        object appears (FR-IAM-04/05)."""
        if not self.policy.restricted_prefixes():
            return self.trees.apply(base, changes)  # nothing is restricted: nothing to record
        rows = []
        entry = self.policy.acl_entry
        root = self.trees.apply(base, changes, lambda path, kind, oid: rows.append((oid, entry(path))))
        self.meta.acl_add(rows)
        return root

    # ======================================================== object protocol (FR-FP, ADR-06/13)
    def _acl(self, ids) -> dict[str, set[str]]:
        """The restricting directories of each restricted object; objects anyone may read are left out."""
        return {oid: ps for oid, ps in self.meta.acl_get(ids).items() if "" not in ps}

    def restricted_objects(self, ids: list[str]) -> set[str]:
        """Objects that shared tiers must not cache: all of a private repository's (ADR-13), plus
        objects that appear only under read-restricted directories (FR-IAM-05/11)."""
        if not getattr(self.policy, "public", True):
            return set(ids)
        return set(self._acl(ids))

    def can_read_object(self, oid: str, user=None, acl=None) -> bool:
        """Anyone who may read some place the object appears may read the object (FR-IAM-11)."""
        prefixes = (acl if acl is not None else self._acl([oid])).get(oid)
        return not prefixes or any(self.policy.can_read(user, p) for p in prefixes)

    def fetch_objects(self, ids: list[str], user=None) -> list[tuple[str, int, bytes]]:
        """``get_objects`` on the authoritative tier: stored bytes as they are, flagged
        ``F_RESTRICTED`` when shared tiers must not cache them. Restricted objects are authorized
        for the end user on every request (ADR-06). Only blobs and trees are served; derived
        structures stay internal."""
        if not self.policy.can_read_repo(user):  # the repository; its directories are checked per object
            return [(oid, F_DENIED, b"") for oid in ids]
        private = not getattr(self.policy, "public", True)
        acl = self._acl(ids)
        out = []
        for oid in ids:
            stored = self.objects.get_stored(oid) if is_object_id(oid) else None
            if stored is None or stored_type(stored) not in PUBLIC_TYPES:
                out.append((oid, F_MISSING, b""))
            elif oid in acl and not self.can_read_object(oid, user, acl):
                out.append((oid, F_DENIED, b""))
                self.stats["objects.denied"] += 1
            else:
                out.append((oid, F_RESTRICTED if private or oid in acl else 0, stored))
        self.stats["objects.served"] += len(out)
        return out

    def missing_objects(self, ids: list[str], user=None) -> list[str]:
        """``has_objects``: the ids this repository does not have, so uploads skip known
        content (FR-WR-06). Only writers may ask, and objects the caller may not read are
        reported missing, so the answer reveals nothing about restricted content."""
        if not self.policy.can_write(user, ""):
            raise PermissionDenied(f"{user} may not write to {self.name}")
        acl = self._acl([oid for oid in ids if is_object_id(oid)])
        return [oid for oid in ids if not (is_object_id(oid) and self.objects.has(oid))
                or (oid in acl and not self.can_read_object(oid, user, acl))]

    def acl_epoch(self) -> str:
        """Changes whenever objects shared tiers already hold may have stopped being cacheable:
        when the repository stops being readable by everyone, and at every re-index of the object
        index. Tiers compare it and purge the repository's objects when it changes (ADR-20)."""
        public = getattr(self.policy, "public", True)
        marker = self.meta.kv_get("acl_reindexed") or ""
        return hashlib.sha256(f"public={public};reindexed={marker}".encode()).hexdigest()[:16]

    def reindex_acl(self) -> dict:
        """Rebuild the object index under the current policy (FR-IAM-09, UC-22 step 3): every
        object every changeset wrote, at every place it appeared. Run it after a policy change; tiers
        purge what they hold when the ACL epoch changes (ADR-20).

        Commits go on meanwhile, on any server. A commit writes its objects' entries before its
        changeset exists, so the scan can miss them: the replace therefore only touches objects the
        scan saw, and the scan then continues over the changesets created while it ran."""
        rows: set[tuple[str, str]] = {(EMPTY_TREE_ID, "")}
        changesets, after = 0, None
        while batch := self.meta.tail(after, 1000):
            for after, cs_id in batch:
                changesets += 1
                rows |= self._acl_rows(cs_id)
        self.meta.acl_replace(sorted(rows))
        while batch := self.meta.tail(after, 1000):  # created during the scan
            for after, cs_id in batch:
                changesets += 1
                new = self._acl_rows(cs_id)
                self.meta.acl_add(sorted(new - rows))
                rows |= new
        self.meta.kv_set("acl_reindexed", f"{time.time()}:{os.getpid()}")  # a new ACL epoch (ADR-20)
        restricted = sum(1 for _, p in rows if p)
        return {"changesets": changesets, "entries": len(rows), "restricted_entries": restricted,
                "epoch": self.acl_epoch()}

    def _acl_rows(self, cs_id: str) -> set[tuple[str, str]]:
        """The object index's entries for the objects a changeset wrote, under the current policy."""
        entry = self.policy.acl_entry
        root = self.root_tree(cs_id)
        rows, dirs = {(root, entry(""))}, set()
        for ch in self.get_changeset(cs_id).changes:
            if ch.blob:
                rows.add((ch.blob, entry(ch.path)))
            parts = ch.path.split("/")
            dirs.update("/".join(parts[:k]) for k in range(1, len(parts)))
        for d in dirs:
            e = self.trees.lookup(root, d)
            if e is not None and e[0] == KIND_DIR:
                rows.add((e[1], entry(d)))
        return rows

    def put_objects(self, items, user=None) -> int:
        """Store uploaded blobs after verifying each against its id. Trees are always derived on
        the server (threat T4). Nothing is stored unless every object is valid and within the
        per-file limit (FR-WR-07)."""
        if not self.policy.can_write(user, ""):
            raise PermissionDenied(f"{user} may not write to {self.name}")
        limit = getattr(self.policy, "max_file_bytes", None)
        checked = []
        for oid, _flags, stored in items:
            if not is_object_id(oid):
                raise ValueError(f"bad object id {oid!r}")
            otype, _ = decode_limited(stored, oid, limit)
            if otype != "blob":
                raise ValueError("only blobs may be uploaded; trees are derived on the server")
            checked.append((oid, stored))
        acl = self._acl([oid for oid, _ in checked])
        for oid, stored in checked:
            self.objects.put_stored(oid, stored, verify=False)
            if oid in acl and user is not None and not self.can_read_object(oid, user, acl):
                # the uploader proved they hold these bytes, so they may commit them by id
                self.meta.grant_add(oid, user, time.time())
        self.stats["objects.uploaded"] += len(checked)
        return len(checked)

    # ============================================================================== changesets
    def get_changeset(self, cs_id: str) -> Changeset:
        cs = self.cache.get(("cs", cs_id))
        if cs is None:
            data = self.meta.get_changeset_data(cs_id)
            if data is None:
                raise NotFound(f"unknown changeset {cs_id}")
            cs = Changeset.decode(data)
            self.cache.put(("cs", cs_id), cs, len(data))
        return cs

    def resolve(self, rev: str) -> str:
        """A ref name, a full id or a unique prefix (≥ 4 hex), then any ``~N`` / ``^N`` (FR-CS-07)."""
        if not rev or not isinstance(rev, str):
            raise NotFound("empty revision")
        m = re.match(r"^(.*?)((?:[~^]\d*)*)$", rev)
        base, suffix = m.group(1), m.group(2)
        ref = self.meta.get_ref(base)
        if ref is not None:
            cs = ref[0]
        elif is_object_id(base) and self.meta.has_changeset(base):
            cs = base
        elif len(base) >= 4 and re.fullmatch(r"[0-9a-fA-F]+", base):
            hits = self.meta.resolve_prefix(base)
            if not hits:
                raise NotFound(f"unknown revision {rev}")
            if len(hits) > 1:
                raise NotFound(f"ambiguous revision prefix {base}")
            cs = hits[0]
        else:
            raise NotFound(f"unknown revision {rev}")
        for op, num in re.findall(r"([~^])(\d*)", suffix):
            n = int(num) if num else 1
            if op == "~":
                nxt = self.fp_ancestor(cs, n)
            else:
                ps = self.get_changeset(cs).parents
                nxt = ps[n - 1] if 0 < n <= len(ps) else None
            if nxt is None:
                raise NotFound(f"revision {rev} does not exist")
            cs = nxt
        return cs

    def root_tree(self, cs_id: str | None) -> str:
        return EMPTY_TREE_ID if cs_id is None else self.derived.get("tree", cs_id)

    def history_root(self, cs_id: str) -> str:
        return self.derived.get("history", cs_id)

    def search_root(self, cs_id: str) -> str:
        return self.derived.get("search", cs_id)

    def graph(self, cs_id: str) -> dict:
        g = self.cache.get(("graph", cs_id))
        if g is None:
            raw = self.derived.get("graph", cs_id)
            g = json.loads(raw)
            self.cache.put(("graph", cs_id), g, len(raw))
        return g

    def generation(self, cs_id: str) -> int:
        return self.graph(cs_id)["g"]

    def changeset_api(self, cs_id: str, user=None) -> dict:
        d = self.get_changeset(cs_id).to_api(cs_id)
        d["changes"] = [c for c in d["changes"] if self.policy.can_read(user, c["path"])]
        d["generation"] = self.generation(cs_id)
        d["copies"] = {k: v for k, v in json.loads(self.derived.get("copies", cs_id)).items()
                       if self.policy.can_read(user, k)}
        return d

    # ======================================================================= writes (FR-CS-*)
    def create_changeset(self, parents: list[str], files: list[dict], author: str, message: str,
                         timestamp: int | None = None, extra: dict | None = None, user=None) -> str:
        """Create a changeset from file updates relative to the first parent. Each entry is
        ``{"path", "delete": True}``, ``{"path", "kind", "blob"}`` or ``{"path", "kind", "content"}``.
        No lock is taken and no ref moves (FR-CS-05); the tree is built incrementally (FR-CS-09)."""
        parents = [self.resolve(p) for p in parents]
        if len(set(parents)) != len(parents):
            raise ValueError("duplicate parents")
        base = self.root_tree(parents[0]) if parents else None
        changes, tree_changes, seen, pending = [], {}, set(), []
        inline = {blob_id(f["content"]) for f in files if not f.get("blob") and isinstance(f.get("content"), bytes)}
        for f in files:
            path = normalize_path(f.get("path", ""))
            if not path:
                raise ValueError("empty path")
            if path in seen:
                raise ValueError(f"duplicate path {path}")
            seen.add(path)
            if user is not None and not self.policy.can_write(user, path):
                raise PermissionDenied(f"{user} may not write {path}")
            old = self.trees.lookup(base, path)
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
                if blob in inline:
                    pass  # the bytes come with this very request
                elif not self.objects.has(blob):
                    raise ValueError(f"blob {blob[:12]} for {path} has not been uploaded")
                elif (user is not None and not self.can_read_object(blob, user)
                      and not self.meta.grant_has(blob, user, time.time())):
                    # an object you may not read can't be republished somewhere else by its id,
                    # unless you uploaded its bytes yourself
                    raise PermissionDenied(f"{user} may not use object {blob[:12]}")
            else:
                data = f.get("content", b"")
                limit = getattr(self.policy, "max_file_bytes", None)
                if limit is not None and len(data) > limit:
                    raise ObjectTooLarge(f"{path} is larger than the {limit}-byte limit")
                pending.append((path, data))
                blob = blob_id(data)
            if old_file == (kind, blob):
                continue  # no-op
            changes.append(FileChange(path, OP_MODIFY if old_file else OP_ADD, kind, blob))
            tree_changes[path] = (kind, blob)
        try:
            new_root = self.apply_to_tree(base, tree_changes)
        except PathConflict as e:
            raise ValueError(str(e)) from None
        for _, data in pending:  # inline contents are stored once every entry has been validated
            self.put_blob(data)
        cs = Changeset(tuple(parents), author, message, int(time.time() if timestamp is None else timestamp),
                       tuple(sorted(changes, key=lambda c: c.path)), dict(extra or {}))
        for c in cs.changes:
            c.validate()
        cs_id = cs.id
        new = self.meta.insert_changeset(cs_id, cs.encode())
        if new:
            self.stats["changesets.created"] += 1
        self.derived.put("tree", cs_id, new_root)
        self.derived.derive_eager(cs_id, new)
        return cs_id

    # ============================================================================ refs (FR-REF)
    def get_ref(self, name: str) -> str | None:
        r = self.meta.get_ref(name)
        return r[0] if r else None

    def update_ref(self, name: str, old: str | None, new: str | None, user=None, landing: tuple | None = None) -> bool:
        """Compare-and-swap ``name`` from ``old`` to ``new``; ``landing`` (MetaStore.cas_ref) is
        recorded with the move, atomically."""
        if not REF_NAME.match(name or "") or ".." in name:
            raise ValueError(f"invalid ref name {name!r}")
        if user is not None and not self.policy.can_update_ref(user, name):
            raise PermissionDenied(f"{user} may not move {name}")
        if new is not None:
            new = self.resolve(new)
        if old is not None and not is_object_id(old):
            old = self.resolve(old)
        moved = self.meta.cas_ref(name, old, new, who=user or "", landing=landing)
        if moved and self.audit is not None:
            self.audit.append("ref.update", user, name, {"old": old, "new": new})
        return moved

    # =================================================================================== reads
    def lookup(self, cs_id: str, path: str):
        return self.trees.lookup(self.root_tree(cs_id), normalize_path(path))

    def read_file(self, cs_id: str, path: str, user=None) -> tuple[str, str, bytes]:
        path = normalize_path(path)
        if not self.policy.can_read(user, path):
            raise PermissionDenied(f"{user} may not read {path}")
        e = self.lookup(cs_id, path)
        if e is None or e[0] == KIND_DIR:
            raise NotFound(f"{path}: no such file at {cs_id[:12]}")
        return e[0], e[1], self.read_blob(e[1])

    def list_dir(self, cs_id: str, path: str = "", user=None) -> list[dict]:
        path = normalize_path(path)
        if not self.can_list(user, path):
            raise PermissionDenied(f"{user} may not read {path}")
        e = self.lookup(cs_id, path)
        if e is None or e[0] != KIND_DIR:
            raise NotFound(f"{path or '/'}: not a directory")
        out = []
        for name, (kind, oid) in sorted(self.trees.read(e[1]).items()):
            child = f"{path}/{name}" if path else name
            if self.policy.can_read(user, child) or (kind == KIND_DIR and self.can_list(user, child)):
                out.append({"name": name, "path": child, "kind": kind, "id": oid})
        return out

    def can_list(self, user, path: str) -> bool:
        """A directory can be listed if it is readable, or if some readable directory lies beneath it
        (a public folder inside a private one stays reachable). The second test is the policy's."""
        if self.policy.can_read(user, path):
            return True
        beneath = getattr(self.policy, "readable_beneath", None)
        return bool(beneath and beneath(user, path))

    def diff(self, a: str | None, b: str, paths: list[str] | None = None, user=None) -> list[dict]:
        out = []
        for path, x, y in self._scoped_diff(self.root_tree(a), self.root_tree(b), paths):
            if self.policy.can_read(user, path):
                out.append({"path": path, "status": "A" if x is None else "D" if y is None else "M",
                            "old": _api_entry(x), "new": _api_entry(y)})
        return out

    def _scoped_diff(self, ra, rb, paths):
        if not paths:
            yield from self.trees.diff(ra, rb)
            return
        for p in sorted({normalize_path(p) for p in paths}):
            ea, eb = self.trees.lookup(ra, p), self.trees.lookup(rb, p)
            da = ea[1] if ea and ea[0] == KIND_DIR else None
            db = eb[1] if eb and eb[0] == KIND_DIR else None
            if da or db:
                yield from self.trees.diff(da, db, p)
            fa = ea if ea and ea[0] != KIND_DIR else None
            fb = eb if eb and eb[0] != KIND_DIR else None
            if fa != fb:
                yield (p, fa, fb)

    def diff_text(self, a: str | None, b: str, paths=None, user=None, context: int = 3) -> str:
        chunks = []
        for f in self.diff(a, b, paths, user):
            old = self.read_blob(f["old"]["id"]) if f["old"] else b""
            new = self.read_blob(f["new"]["id"]) if f["new"] else b""
            an = f"a/{f['path']}" if f["old"] else "/dev/null"
            bn = f"b/{f['path']}" if f["new"] else "/dev/null"
            if is_binary(old) or is_binary(new):
                chunks.append(f"Binary files {an} and {bn} differ\n")
                continue
            for line in difflib.unified_diff(old.decode("utf-8", "replace").splitlines(keepends=True),
                                             new.decode("utf-8", "replace").splitlines(keepends=True), an, bn, n=context):
                chunks.append(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n")
        return "".join(chunks)

    def log(self, rev: str, limit: int = 50, first_parent: bool = True, path: str | None = None,
            skip: int = 0, user=None) -> list[str]:
        start = self.resolve(rev)
        if path:
            return [h["cs"] for h in self.file_history(start, path, limit + skip, user=user)][skip:]
        out: list[str] = []
        if first_parent:
            cur = start
            while cur and len(out) < limit + skip:
                out.append(cur)
                cur = self.get_changeset(cur).first_parent
        else:
            seen, heap = {start}, [(-self.generation(start), start)]
            while heap and len(out) < limit + skip:
                _, x = heapq.heappop(heap)
                out.append(x)
                for p in self.get_changeset(x).parents:
                    if p not in seen:
                        seen.add(p)
                        heapq.heappush(heap, (-self.generation(p), p))
        return out[skip:]

    def file_history(self, rev: str, path: str, limit: int = 100, follow_copies: bool = True, user=None) -> list[dict]:
        """Changesets that changed a file or directory, newest first, along the first parent
        (BR-06). Each step is one history-tree lookup: O(path depth) per result (NFR-06)."""
        cur = self.resolve(rev)
        path = normalize_path(path)
        if not self.policy.can_read(user, path):
            raise PermissionDenied(f"{user} may not read {path}")
        if not path:
            return [{"cs": c, "path": ""} for c in self.log(cur, limit)]
        out, is_dir = [], None
        while cur and len(out) < limit:
            e = self.htree_lookup(self.history_root(cur), path)
            if e is None:
                break
            if is_dir is None:
                is_dir = e[0] == KIND_DIR
            elif is_dir != (e[0] == KIND_DIR):
                break  # the path changed between file and directory: a different object
            out.append({"cs": e[2], "path": path})
            if follow_copies and not is_dir:
                src = json.loads(self.derived.get("copies", e[2])).get(path)
                if src:
                    path = src["from"]
            cur = self.get_changeset(e[2]).first_parent
        return out

    def blame_object_for(self, cs_id: str, path: str) -> str:
        return json.loads(self.derived.get("blame", cs_id))[path]

    def previous_version(self, parent: str, path: str):
        e = self.htree_lookup(self.history_root(parent), path)
        if e is None or e[0] == KIND_DIR:
            return None
        return e[1], self.blame_object_for(e[2], path)

    def blame(self, rev: str, path: str, user=None) -> dict:
        cs_id = self.resolve(rev)
        path = normalize_path(path)
        if not self.policy.can_read(user, path):
            raise PermissionDenied(f"{user} may not read {path}")
        e = self.htree_lookup(self.history_root(cs_id), path)
        if e is None or e[0] == KIND_DIR:
            raise NotFound(f"{path}: no such file")
        bid = self.blame_object_for(e[2], path)
        if bid == "binary":
            return {"path": path, "binary": True, "lines": [], "changesets": {}}
        info, lines = {}, []
        for i, (text, (c, origin)) in enumerate(zip(split_lines(self.read_blob(e[1])), expand_runs(self.read_blame(bid)))):
            if c not in info:
                cs = self.get_changeset(c)
                info[c] = {"author": cs.author, "timestamp": cs.timestamp, "summary": cs.summary()}
            lines.append({"line": i + 1, "cs": c, "origin_line": origin, "text": text.decode("utf-8", "replace")})
        return {"path": path, "binary": False, "lines": lines, "changesets": info}

    # ============================================================ ancestry (FR-QRY-05/09, ADR-12)
    def fp_ancestor(self, cs_id: str, n: int) -> str | None:
        """The first-parent ancestor ``n`` steps back, in O(log n) skip-list hops."""
        cur = cs_id
        while n > 0:
            skips = self.graph(cur)["s"]
            if not skips:
                return None
            k = min(n.bit_length() - 1, len(skips) - 1)
            cur, n = skips[k], n - (1 << k)
            self.stats["ancestry.hops"] += 1
        return cur

    def is_ancestor(self, a: str, b: str) -> bool:
        """Is ``a`` an ancestor of (or equal to) ``b``?"""
        a, b = self.resolve(a), self.resolve(b)
        ga, seen, stack = self.generation(a), set(), [b]
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
            steps = min(g["l"], g["g"] - ga)  # nodes skipped have generation > ga, so none is ``a``
            if steps > 1:
                stack.append(self.fp_ancestor(x, steps))
            else:
                stack.extend(self.get_changeset(x).parents)
        return False

    def merge_bases(self, a: str, b: str) -> list[str]:
        a, b = self.resolve(a), self.resolve(b)
        if a == b or self.is_ancestor(a, b):
            return [a]
        if self.is_ancestor(b, a):
            return [b]
        PA, PB, STALE = 1, 2, 4
        flags = {a: PA, b: PB}
        heap = [(-self.generation(a), a), (-self.generation(b), b)]
        heapq.heapify(heap)
        found: list[str] = []
        while heap and any(not flags[x] & STALE for _, x in heap):
            _, x = heapq.heappop(heap)
            f = flags[x]
            self.stats["ancestry.visits"] += 1
            if f & (PA | PB) == (PA | PB):
                if not f & STALE:
                    found.append(x)
                    f |= STALE
                    flags[x] = f
            elif not f & STALE:
                # cross a single-parent run the other side cannot reach (it is above the other
                # side's highest generation) in one skip
                other = PB if f & PA else PA
                g = self.graph(x)
                top_other = max((-h for h, y in heap if flags[y] & other), default=0)
                steps = min(g["l"], g["g"] - top_other)
                if steps >= 2:
                    y = self.fp_ancestor(x, steps)
                    if flags.get(y, 0) | f != flags.get(y, 0):
                        flags[y] = flags.get(y, 0) | f
                        heapq.heappush(heap, (-self.generation(y), y))
                    continue
            for p in self.get_changeset(x).parents:
                pf = flags.get(p, 0)
                nf = pf | (f & (PA | PB | STALE))
                if nf != pf:
                    flags[p] = nf
                    heapq.heappush(heap, (-self.generation(p), p))
        found = [r for r in found if not any(r != s and self.is_ancestor(r, s) for s in found)]
        return sorted(found, key=lambda r: (-self.generation(r), r))

    def merge_base(self, a: str, b: str) -> str | None:
        bases = self.merge_bases(a, b)
        return bases[0] if bases else None

    # ============================================================ merge / rebase / revert (FR-WR)
    def _three_way(self, paths, base_root: str, ours_root: str, theirs_root: str):
        """Apply the base→theirs change at each path on top of ours: (changes, conflicts)."""
        changes, conflicts = {}, []
        for path in paths:
            b = self.trees.lookup(base_root, path)
            if b is not None and b[0] == KIND_DIR:
                b = None  # no file here in the base
            o, t = self.trees.lookup(ours_root, path), self.trees.lookup(theirs_root, path)
            if t == b:
                continue
            if (o is not None and o[0] == KIND_DIR) or (t is not None and t[0] == KIND_DIR):
                conflicts.append({"path": path, "reason": "file/directory conflict"})
                continue
            if o == b:
                changes[path] = t
                continue
            if o == t:
                continue
            reason = "both sides changed"
            if o is not None and t is not None and KIND_LINK not in (o[0], t[0]) and (b is None or b[0] != KIND_LINK):
                bd = self.read_blob(b[1]) if b else b""
                od, td = self.read_blob(o[1]), self.read_blob(t[1])
                if is_binary(bd) or is_binary(od) or is_binary(td):
                    reason = "binary file changed on both sides"
                else:
                    merged, n = merge3(bd, od, td)
                    if n == 0:
                        changes[path] = (t[0] if b is None or t[0] != b[0] else o[0], self.put_blob(merged))
                        continue
                    reason = f"{n} conflicting hunk(s)"
            elif o is None or t is None:
                reason = "modified on one side, deleted on the other"
            conflicts.append({"path": path, "reason": reason, "base": _api_entry(b), "ours": _api_entry(o),
                              "theirs": _api_entry(t)})
        return changes, conflicts

    def _commit_changes(self, parents, changes, author, message, timestamp=None, extra=None, user=None, at=None):
        root = self.root_tree(parents[0])
        files = []
        for path, e in sorted(changes.items()):
            if e is None:
                if self.trees.lookup(root, path) is not None:
                    files.append({"path": path, "delete": True})
            else:
                files.append({"path": path, "kind": e[0], "blob": e[1]})
        try:
            return self.create_changeset(parents, files, author, message, timestamp, extra, user)
        except ValueError as e:
            raise MergeConflict([{"path": "", "reason": str(e)}], at=at) from None

    def merge(self, ours: str, theirs: str, author: str, message: str | None = None, ff: bool = False, user=None) -> str:
        ours, theirs = self.resolve(ours), self.resolve(theirs)
        if self.is_ancestor(theirs, ours):
            return ours
        if ff and self.is_ancestor(ours, theirs):
            return theirs
        base_root = self.root_tree(self.merge_base(ours, theirs))
        paths = [p for p, _, _ in self.trees.diff(base_root, self.root_tree(theirs))]
        changes, conflicts = self._three_way(paths, base_root, self.root_tree(ours), self.root_tree(theirs))
        if conflicts:
            raise MergeConflict(conflicts)
        return self._commit_changes([ours, theirs], changes, author, message or f"Merge {theirs[:12]} into {ours[:12]}", user=user)

    def rebase(self, head: str, onto: str, base: str | None = None, user=None) -> dict:
        """Replay ``head``'s first-parent chain onto ``onto``: the changesets from ``head`` back to
        ``base``, by default back to the first one ``onto`` contains. Changesets whose first parent
        doesn't move stay as they are, so the result always has ``onto`` on its first-parent chain
        (BR-06): when ``onto`` is already there, ``head`` comes back unchanged. A merge is replayed as
        its change list, which is relative to its first parent (FR-CS-02), so what it brought in that
        ``onto`` already has drops out. Changesets already applied upstream are dropped.
        Returns ``{"head", "rebased": {old: new}}``."""
        head, onto = self.resolve(head), self.resolve(onto)
        if self.is_ancestor(head, onto):
            return {"head": onto, "rebased": {}}
        if base:
            stop = self.resolve(base)
            low = self.generation(stop)
            done = lambda c: c == stop or self.generation(c) <= low  # noqa: E731
        else:
            if self.merge_base(head, onto) is None:
                raise ValueError("no common ancestor")
            stop = None
            done = lambda c: self.is_ancestor(c, onto)  # noqa: E731
        stack, cur = [], head
        while not done(cur):
            stack.append(cur)
            cur = self.get_changeset(cur).first_parent
            if cur is None:
                raise ValueError(f"{head[:12]}'s first-parent chain doesn't meet {onto[:12]}")
        if stop is not None and cur != stop:
            raise ValueError(f"{stop[:12]} is not on the first-parent chain of {head[:12]}")
        new_parent, mapping = onto, {}
        for c in reversed(stack):
            cs = self.get_changeset(c)
            if cs.first_parent == new_parent:
                new_parent = c  # nothing beneath it moved
                continue
            changes, conflicts = self._three_way([ch.path for ch in cs.changes], self.root_tree(cs.first_parent),
                                                 self.root_tree(new_parent), self.root_tree(c))
            if conflicts:
                raise MergeConflict(conflicts, at=c)
            if not changes and (cs.changes or len(cs.parents) > 1):
                mapping[c] = new_parent  # already applied upstream
                continue
            new_parent = mapping[c] = self._commit_changes([new_parent], changes, cs.author, cs.message, cs.timestamp,
                                                           {**cs.extra, "rebased_from": c}, user=user, at=c)
        return {"head": new_parent, "rebased": mapping}

    def revert(self, cs_id: str, onto: str, author: str, message: str | None = None, user=None) -> str:
        cs_id, onto = self.resolve(cs_id), self.resolve(onto)
        cs = self.get_changeset(cs_id)
        changes, conflicts = self._three_way([c.path for c in cs.changes], self.root_tree(cs_id),
                                             self.root_tree(onto), self.root_tree(cs.first_parent))
        if conflicts:
            raise MergeConflict(conflicts, at=cs_id)
        return self._commit_changes([onto], changes, author,
                                    message or f'Revert "{cs.summary()}"\n\nThis reverts changeset {cs_id}.',
                                    extra={"reverts": cs_id}, user=user)

    # ==================================================================================== info
    def info(self) -> dict:
        return {"name": self.name, "changesets": self.meta.count_changesets(),
                "refs": {n: t for n, t, _ in self.meta.list_refs()},
                "derived": {t: self.meta.derived_count(t) for t in self.derived.types},
                "eager": self.derived.eager_types}

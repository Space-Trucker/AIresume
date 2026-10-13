"""The scn client.

The client can compute very little on its own, and in exchange it needs very little data
locally.  It

* keeps a bounded local object cache (and, in the fleet, shares the node's ``scion-daemon``),
* lays out working-copy files on disk: full, sparse (only the requested directories) or virtual
  (files appear only when something reads them),
* monitors the filesystem for changes (``fsmonitor``), and
* hands everything else to the server: commits, history, blame, diffs between changesets,
  merges and rebases.

Fetching never tells the server what the client already has.  Starting from a root tree, the
client checks its local store, requests the missing trees level by level, then the missing blobs.
Every request names immutable objects, so any cache tier can answer it.
"""
from __future__ import annotations

import difflib
import fnmatch
import json
import os
import shutil
import sqlite3
import stat as statmod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from . import fsmonitor
from .objects import (
    KIND_DIR,
    KIND_EXEC,
    KIND_FILE,
    KIND_LINK,
    blob_id,
    decode_stored,
    decode_tree,
    encode_stored,
    is_binary,
    normalize_path,
    split_path,
)
from .repo import F_DENIED, F_MISSING
from .rpc import RemoteError, RpcClient
from .storage import BoundedFileObjectStore

SCN_DIR = ".scn"
DEFAULT_CACHE_BYTES = 2 * 1024 ** 3
FETCH_BATCH = 500
FETCH_PARALLEL = 8
UPLOAD_CHUNK_BYTES = 32 * 1024 ** 2


class ClientError(Exception):
    pass


# =============================================================================================
# Talking to the services
# =============================================================================================
class ServerApi:
    """Metadata API.  Exactly the RPCs any CI job or tool can use without a checkout."""

    def __init__(self, url: str, user: str | None = None, token: str | None = None):
        self.rpc = RpcClient(url, user=user, token=token, tier="client")

    def __getattr__(self, name):
        method = name.replace("__", ".")

        def call(**params):
            return self.rpc.call(method, **params)
        return call

    def call(self, method: str, **params):
        return self.rpc.call(method, **params)


class ObjectFetcher:
    """Want-only object fetching through the node's daemon (or any tier) into a bounded cache."""

    def __init__(self, url: str, local: BoundedFileObjectStore, user: str | None = None,
                 token: str | None = None):
        self.rpc = RpcClient(url, user=user, token=token, tier="client")
        self.local = local
        self.counters = {"requested": 0, "local_hits": 0, "fetched": 0, "bytes": 0, "requests": 0}
        self._tree_cache: dict[str, dict] = {}
        self.denied: set[str] = set()  # objects under directories this user may not read

    def _remote(self, ids: list[str], allow_denied: bool = False) -> list[tuple[str, bytes]]:
        self.counters["requests"] += 1
        out = []
        for oid, flags, stored in self.rpc.get_objects(ids):
            if flags & F_DENIED:
                if allow_denied:
                    self.denied.add(oid)
                    continue
                raise ClientError(f"permission denied for object {oid[:12]}")
            if flags & F_MISSING:
                raise ClientError(f"object {oid[:12]} is missing upstream")
            decode_stored(stored, expected_id=oid)  # trust nothing: verify integrity
            self.local.put_stored(oid, stored, verify=False)
            self.counters["fetched"] += 1
            self.counters["bytes"] += len(stored)
            out.append((oid, stored))
        return out

    def fetch_stream(self, ids: list[str], allow_denied: bool = False):
        """Yield (id, stored) for every id: local hits first, then remote batches in parallel.
        With ``allow_denied``, objects the user may not read are skipped (and recorded)."""
        ids = list(dict.fromkeys(ids))
        self.counters["requested"] += len(ids)
        missing = []
        for oid in ids:
            stored = self.local.get_stored(oid)
            if stored is None:
                missing.append(oid)
            else:
                self.counters["local_hits"] += 1
                yield oid, stored
        batches = [missing[i:i + FETCH_BATCH] for i in range(0, len(missing), FETCH_BATCH)]
        if len(batches) <= 1:
            for b in batches:
                yield from self._remote(b, allow_denied)
            return
        with ThreadPoolExecutor(max_workers=FETCH_PARALLEL) as pool:
            for result in pool.map(lambda b: self._remote(b, allow_denied), batches):
                yield from result

    def get_many(self, ids: list[str], allow_denied: bool = False) -> dict[str, bytes]:
        return {oid: decode_stored(stored)[1] for oid, stored in self.fetch_stream(ids, allow_denied)}

    def tree(self, tid: str) -> dict:
        t = self._tree_cache.get(tid)
        if t is None:
            for _, stored in self.fetch_stream([tid]):
                t = decode_tree(decode_stored(stored)[1])
            self._tree_cache[tid] = t
        return t

    def trees(self, tids: list[str], allow_denied: bool = False) -> dict[str, dict]:
        need = [t for t in tids if t not in self._tree_cache]
        for oid, payload in self.get_many(need, allow_denied).items():
            self._tree_cache[oid] = decode_tree(payload)
        return {t: self._tree_cache[t] for t in tids if t in self._tree_cache}

    def blob(self, oid: str) -> bytes:
        return self.get_many([oid])[oid]


# =============================================================================================
# Sparse profiles
# =============================================================================================
@dataclass
class SparseProfile:
    prefixes: list[str] = field(default_factory=list)  # empty = everything

    def __post_init__(self):
        self.prefixes = sorted({normalize_path(p) for p in self.prefixes if normalize_path(p)})

    @property
    def full(self) -> bool:
        return not self.prefixes

    def includes(self, path: str) -> bool:
        if self.full:
            return True
        return any(path == p or path.startswith(p + "/") for p in self.prefixes)

    def wants_dir(self, path: str) -> bool:
        """Should the client descend into this directory?"""
        if self.includes(path):
            return True
        return any(p.startswith(path + "/") for p in self.prefixes)


# =============================================================================================
# The working copy
# =============================================================================================
@dataclass
class Status:
    modified: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)
    scanned: int = 0
    used_fsmonitor: bool = False

    @property
    def dirty(self) -> bool:
        return bool(self.modified or self.added or self.removed)

    def to_dict(self) -> dict:
        return {"modified": self.modified, "added": self.added, "removed": self.removed,
                "untracked": self.untracked, "scanned": self.scanned, "used_fsmonitor": self.used_fsmonitor}


def _file_kind_and_data(path: str) -> tuple[str, bytes]:
    st = os.lstat(path)
    if statmod.S_ISLNK(st.st_mode):
        return KIND_LINK, os.readlink(path).encode()
    with open(path, "rb") as f:
        data = f.read()
    return (KIND_EXEC if st.st_mode & 0o111 else KIND_FILE), data


class WorkingCopy:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.dot = os.path.join(self.root, SCN_DIR)
        with open(os.path.join(self.dot, "config.json")) as f:
            self.config = json.load(f)
        self.state = self._load_state()
        self.api = ServerApi(self.config["server"], self.config.get("user"), self.config.get("token"))
        cache_dir = self.config.get("cache_dir") or os.path.join(self.dot, "objects")
        self.local = BoundedFileObjectStore(cache_dir, int(self.config.get("cache_bytes", DEFAULT_CACHE_BYTES)))
        self.fetcher = ObjectFetcher(self.config.get("objects") or self.config["server"], self.local,
                                     self.config.get("user"), self.config.get("token"))
        self.db = sqlite3.connect(os.path.join(self.dot, "dirstate.db"), isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, kind TEXT, blob TEXT, "
                        "size INTEGER, mtime_ns INTEGER, state TEXT NOT NULL)")
        self._ignore = self._load_ignore()

    # -- construction ----------------------------------------------------------------------
    @classmethod
    def clone(cls, dest: str, server: str, objects: str | None = None, rev: str = "main",
              mode: str = "full", sparse: list[str] | None = None, user: str | None = None,
              token: str | None = None, cache_bytes: int = DEFAULT_CACHE_BYTES,
              cache_dir: str | None = None) -> "WorkingCopy":
        if mode not in ("full", "sparse", "virtual"):
            raise ClientError(f"bad mode {mode}")
        if mode == "sparse" and not sparse:
            raise ClientError("a sparse checkout needs at least one directory")
        dest = os.path.abspath(dest)
        if os.path.exists(os.path.join(dest, SCN_DIR)):
            raise ClientError(f"{dest} is already a working copy")
        os.makedirs(os.path.join(dest, SCN_DIR), exist_ok=True)
        config = {"server": server, "objects": objects, "user": user, "token": token, "mode": mode,
                  "sparse": sparse or [], "track": rev, "cache_bytes": cache_bytes, "cache_dir": cache_dir}
        with open(os.path.join(dest, SCN_DIR, "config.json"), "w") as f:
            json.dump(config, f, indent=2)
        wc = cls(dest)
        cs = wc.api.resolve(rev=rev)
        wc._set_base(cs)
        if mode != "virtual":
            wc._materialize_all()
        return wc

    @classmethod
    def find(cls, start: str = ".") -> "WorkingCopy":
        cur = os.path.abspath(start)
        while True:
            if os.path.isdir(os.path.join(cur, SCN_DIR)):
                return cls(cur)
            parent = os.path.dirname(cur)
            if parent == cur:
                raise ClientError("not inside a scn working copy")
            cur = parent

    # -- state ---------------------------------------------------------------------------------
    def _load_state(self) -> dict:
        try:
            with open(os.path.join(self.dot, "state.json")) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_state(self) -> None:
        tmp = os.path.join(self.dot, "state.json.tmp")
        with open(tmp, "w") as f:
            json.dump(self.state, f, indent=2)
        os.replace(tmp, os.path.join(self.dot, "state.json"))

    def _set_base(self, cs: str) -> None:
        self.state["base"] = cs
        self.state["root"] = self.api.root_tree(rev=cs)
        self._save_state()

    @property
    def base(self) -> str:
        return self.state["base"]

    @property
    def mode(self) -> str:
        return self.config["mode"]

    @property
    def profile(self) -> SparseProfile:
        return SparseProfile(self.config.get("sparse") or [])

    def _save_config(self) -> None:
        with open(os.path.join(self.dot, "config.json"), "w") as f:
            json.dump(self.config, f, indent=2)

    def _load_ignore(self) -> list[str]:
        try:
            with open(os.path.join(self.root, ".scnignore")) as f:
                return [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except FileNotFoundError:
            return []

    def _ignored(self, path: str) -> bool:
        base = os.path.basename(path)
        if base.startswith(fsmonitor.COOKIE_PREFIX):
            return True
        return any(fnmatch.fnmatch(path, p) or fnmatch.fnmatch(base, p) for p in self._ignore)

    # -- tree access (on demand) ---------------------------------------------------------------
    def tree_lookup(self, path: str, root: str | None = None):
        node = (KIND_DIR, root or self.state["root"])
        for part in split_path(path):
            if node[0] != KIND_DIR:
                return None
            node = self.fetcher.tree(node[1]).get(part)
            if node is None:
                return None
        return node

    def _collect_files(self, root: str, prefix: str = "", profile: SparseProfile | None = None):
        """Breadth-first: fetch each level's missing trees in one round trip."""
        profile = profile or self.profile
        files = []
        level = [(root, prefix)]
        while level:
            trees = self.fetcher.trees([t for t, _ in level], allow_denied=True)
            nxt = []
            for tid, pfx in level:
                entries = trees.get(tid)
                if entries is None:
                    # This tree object is restricted.  The server's filtered listing still
                    # reveals the readable subdirectories (e.g. a public folder inside a private one).
                    try:
                        entries = {e["name"]: (e["kind"], e["id"])
                                   for e in self.api.list_dir(rev=self.base, path=pfx)}
                    except RemoteError:
                        continue
                for name, (kind, oid) in entries.items():
                    path = f"{pfx}/{name}" if pfx else name
                    if kind == KIND_DIR:
                        if profile.wants_dir(path):
                            nxt.append((oid, path))
                    elif profile.includes(path):
                        files.append((path, kind, oid))
            level = nxt
        return files

    # -- writing files ---------------------------------------------------------------------------
    def _abs(self, path: str) -> str:
        return os.path.join(self.root, *path.split("/"))

    def _write_file(self, path: str, kind: str, data: bytes) -> None:
        full = self._abs(path)
        parent = os.path.dirname(full)
        # A file may sit where a directory must go (or vice versa) after an update.
        probe = self.root
        for part in split_path(path)[:-1]:
            probe = os.path.join(probe, part)
            if os.path.lexists(probe) and not os.path.isdir(probe):
                os.unlink(probe)
        os.makedirs(parent, exist_ok=True)
        if os.path.isdir(full) and not os.path.islink(full):
            shutil.rmtree(full)
        elif os.path.lexists(full):
            os.unlink(full)
        if kind == KIND_LINK:
            os.symlink(data.decode(), full)
        else:
            with open(full, "wb") as f:
                f.write(data)
            os.chmod(full, 0o755 if kind == KIND_EXEC else 0o644)

    def _record(self, path: str, kind: str, blob: str) -> None:
        st = os.lstat(self._abs(path))
        self.db.execute("INSERT OR REPLACE INTO files (path, kind, blob, size, mtime_ns, state) "
                        "VALUES (?, ?, ?, ?, ?, 'n')", (path, kind, blob, st.st_size, st.st_mtime_ns))

    def _materialize(self, files: list[tuple[str, str, str]]) -> int:
        by_blob: dict[str, list[tuple[str, str]]] = {}
        for path, kind, oid in files:
            by_blob.setdefault(oid, []).append((path, kind))
        n = 0
        self.db.execute("BEGIN")
        try:
            for oid, stored in self.fetcher.fetch_stream(list(by_blob), allow_denied=True):
                data = decode_stored(stored)[1]
                for path, kind in by_blob[oid]:
                    self._write_file(path, kind, data)
                    self._record(path, kind, oid)
                    n += 1
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return n

    def _materialize_all(self) -> int:
        return self._materialize(self._collect_files(self.state["root"]))

    # -- virtual checkouts: materialize on demand --------------------------------------------
    def materialize(self, paths: list[str]) -> int:
        files = []
        for p in paths:
            p = normalize_path(p)
            e = self.tree_lookup(p)
            if e is None:
                raise ClientError(f"{p}: not in the checked-out revision")
            if e[0] == KIND_DIR:
                files.extend(self._collect_files(e[1], p, SparseProfile([])))
            else:
                files.append((p, e[0], e[1]))
        known = {r[0] for r in self.db.execute("SELECT path FROM files")}
        return self._materialize([f for f in files if f[0] not in known])

    def read(self, path: str) -> bytes:
        """Read a file, materializing it first if this is a virtual checkout."""
        path = normalize_path(path)
        full = self._abs(path)
        if not os.path.lexists(full):
            if self.mode == "full" or not self.profile.includes(path) and self.mode == "sparse":
                raise FileNotFoundError(path)
            self.materialize([path])
        return _file_kind_and_data(full)[1]

    def listdir(self, path: str = "") -> list[dict]:
        e = self.tree_lookup(path)
        if e is None or e[0] != KIND_DIR:
            raise ClientError(f"{path}: not a directory")
        return [{"name": n, "kind": k} for n, (k, _) in sorted(self.fetcher.tree(e[1]).items())]

    # -- status ------------------------------------------------------------------------------------
    def _walk_disk(self) -> list[str]:
        out = []
        profile = self.profile
        for dirpath, dirnames, filenames in os.walk(self.root):
            rel = os.path.relpath(dirpath, self.root)
            rel = "" if rel == "." else rel.replace(os.sep, "/")
            if rel == "":
                dirnames[:] = [d for d in dirnames if d != SCN_DIR]
            if self.mode == "sparse":
                dirnames[:] = [d for d in dirnames if profile.wants_dir(f"{rel}/{d}" if rel else d)]
            for d in list(dirnames):
                p = os.path.join(dirpath, d)
                if os.path.islink(p):  # symlinks to directories are files to us
                    dirnames.remove(d)
                    filenames.append(d)
            for name in filenames:
                path = f"{rel}/{name}" if rel else name
                if self.mode == "sparse" and not profile.includes(path):
                    continue
                out.append(path)
        return out

    def _candidates_from_fsmonitor(self):
        info = fsmonitor.query(self.root, self.state.get("fsmon"))
        if info is None:
            return None
        token, paths, rescan = info
        self.state["fsmon"] = token
        if rescan:
            return None
        cands = set(paths) | set(self.state.get("dirty", []))
        expanded = set()
        for p in cands:
            full = self._abs(p)
            if os.path.isdir(full) and not os.path.islink(full):
                for dp, _, fns in os.walk(full):
                    rel = os.path.relpath(dp, self.root).replace(os.sep, "/")
                    expanded.update(f"{rel}/{f}" for f in fns)
            else:
                expanded.add(p)
            # A deleted or moved directory: every tracked file beneath it is a candidate.
            expanded.update(r[0] for r in self.db.execute(
                "SELECT path FROM files WHERE path >= ? AND path < ?", (p + "/", p + "0")))
        return {c for c in expanded if not c.startswith(SCN_DIR + "/") and c != SCN_DIR}

    def status(self, use_fsmonitor: bool = True) -> Status:
        st = Status()
        rows = {r[0]: r for r in self.db.execute("SELECT path, kind, blob, size, mtime_ns, state FROM files")}
        candidates = self._candidates_from_fsmonitor() if use_fsmonitor else None
        if candidates is not None:
            st.used_fsmonitor = True
            on_disk = {c for c in candidates if os.path.lexists(self._abs(c))}
            check_rows = {p: r for p, r in rows.items() if p in candidates}
        else:
            on_disk = set(self._walk_disk())
            check_rows = rows
        updates = []
        for path, (_, kind, blob, size, mtime, state) in check_rows.items():
            if state == "a":
                if path in on_disk:
                    st.added.append(path)
                continue
            if state == "r" or path not in on_disk:
                st.removed.append(path)
                continue
            s = os.lstat(self._abs(path))
            st.scanned += 1
            if s.st_size == size and s.st_mtime_ns == mtime:
                k2 = KIND_LINK if statmod.S_ISLNK(s.st_mode) else (KIND_EXEC if s.st_mode & 0o111 else KIND_FILE)
                if k2 == kind:
                    continue
            k2, data = _file_kind_and_data(self._abs(path))
            if k2 == kind and blob_id(data) == blob:
                updates.append((s.st_size, s.st_mtime_ns, path))  # touched but unchanged
            else:
                st.modified.append(path)
        for path in sorted(on_disk - set(rows)):
            if self._ignored(path):
                continue
            if self.mode == "virtual":
                e = self.tree_lookup(path)
                if e is not None and e[0] != KIND_DIR:
                    k2, data = _file_kind_and_data(self._abs(path))
                    if (k2, blob_id(data)) == (e[0], e[1]):
                        self._record(path, e[0], e[1])
                    else:
                        st.modified.append(path)
                        self.db.execute("INSERT OR REPLACE INTO files (path, kind, blob, size, mtime_ns, state) "
                                        "VALUES (?, ?, ?, -1, -1, 'n')", (path, e[0], e[1]))
                    continue
            st.untracked.append(path)
        if updates:
            self.db.executemany("UPDATE files SET size = ?, mtime_ns = ? WHERE path = ?", updates)
        for lst in (st.modified, st.added, st.removed, st.untracked):
            lst.sort()
        self.state["dirty"] = sorted(set(st.modified + st.added + st.removed + st.untracked))
        self._save_state()
        return st

    # -- local edits -----------------------------------------------------------------------------
    def add(self, paths: list[str]) -> list[str]:
        added = []
        for p in paths:
            p = normalize_path(os.path.relpath(os.path.abspath(p), self.root).replace(os.sep, "/")) \
                if os.path.isabs(p) else normalize_path(p)
            full = self._abs(p)
            targets = []
            if os.path.isdir(full) and not os.path.islink(full):
                for dp, _, fns in os.walk(full):
                    rel = os.path.relpath(dp, self.root).replace(os.sep, "/")
                    targets.extend(f"{rel}/{f}" for f in fns)
            elif os.path.lexists(full):
                targets.append(p)
            else:
                raise ClientError(f"{p}: no such file")
            for t in targets:
                if self.db.execute("SELECT 1 FROM files WHERE path = ?", (t,)).fetchone() is None:
                    self.db.execute("INSERT INTO files (path, state) VALUES (?, 'a')", (t,))
                    added.append(t)
        if self.mode == "sparse":
            # A file added outside the sparse profile becomes part of it, so it stays visible.
            outside = [t for t in added if not self.profile.includes(t)]
            if outside:
                self.config["sparse"] = SparseProfile(self.profile.prefixes + outside).prefixes
                self._save_config()
        self.state.setdefault("dirty", [])
        self.state["dirty"] = sorted(set(self.state["dirty"]) | set(added))
        self._save_state()
        return added

    def remove(self, paths: list[str], keep: bool = False) -> None:
        for p in paths:
            p = normalize_path(p)
            if not keep and os.path.lexists(self._abs(p)):
                os.unlink(self._abs(p))
            self.db.execute("UPDATE files SET state = 'r' WHERE path = ?", (p,))
        self.state["dirty"] = sorted(set(self.state.get("dirty", [])) | {normalize_path(p) for p in paths})
        self._save_state()

    def revert_local(self, paths: list[str]) -> None:
        """Discard local changes to ``paths``."""
        for p in paths:
            p = normalize_path(p)
            e = self.tree_lookup(p)
            row = self.db.execute("SELECT state FROM files WHERE path = ?", (p,)).fetchone()
            if e is None or e[0] == KIND_DIR:
                if row and row[0] == "a":
                    self.db.execute("DELETE FROM files WHERE path = ?", (p,))
                continue
            self._write_file(p, e[0], self.fetcher.blob(e[1]))
            self._record(p, e[0], e[1])

    # -- commit: the server creates the changeset; there is nothing to push --------------------
    def commit(self, message: str, paths: list[str] | None = None, addremove: bool = False) -> str:
        st = self.status()
        prefixes = [normalize_path(p) for p in paths] if paths else None

        def wanted(p):
            return prefixes is None or any(p == x or p.startswith(x + "/") for x in prefixes)

        writes = [p for p in st.modified + st.added + (st.untracked if addremove else []) if wanted(p)]
        deletes = [p for p in st.removed if wanted(p)]
        if not writes and not deletes:
            raise ClientError("nothing to commit")
        files, uploads = [], {}
        meta = {}
        for p in writes:
            kind, data = _file_kind_and_data(self._abs(p))
            oid = blob_id(data)
            uploads[oid] = data
            meta[p] = (kind, oid)
            files.append({"path": p, "kind": kind, "blob": oid})
        for p in deletes:
            files.append({"path": p, "delete": True})
        self._upload(uploads)
        result = self.api.create_changeset(parents=[self.base], files=files, message=message)
        cs = result["id"]
        self.db.execute("BEGIN")
        for p, (kind, oid) in meta.items():
            self._record(p, kind, oid)
        for p in deletes:
            self.db.execute("DELETE FROM files WHERE path = ?", (p,))
        self.db.execute("COMMIT")
        self._set_base(cs)
        self.status()
        return cs

    def _upload(self, blobs: dict[str, bytes]) -> int:
        if not blobs:
            return 0
        missing = set()
        ids = list(blobs)
        for i in range(0, len(ids), 2000):
            missing.update(self.api.has_objects(ids=ids[i:i + 2000]))
        chunk, size = [], 0
        for oid in missing:
            stored = encode_stored("blob", blobs[oid])
            self.local.put_stored(oid, stored, verify=False)
            chunk.append((oid, 0, stored))
            size += len(stored)
            if size >= UPLOAD_CHUNK_BYTES:
                self.api.rpc.put_objects(chunk)
                chunk, size = [], 0
        if chunk:
            self.api.rpc.put_objects(chunk)
        return len(missing)

    # -- moving between changesets --------------------------------------------------------------
    def update(self, rev: str, clean: bool = False) -> dict:
        target = self.api.resolve(rev=rev)
        if target == self.base:
            return {"base": target, "changed": 0}
        paths = self.profile.prefixes or None
        d = self.api.diff(a=self.base, b=target, paths=paths)
        st = self.status()
        local = set(st.modified + st.added + st.removed)
        overlap = sorted(local & {f["path"] for f in d["files"]})
        if overlap and not clean:
            raise ClientError("local changes would be overwritten: " + ", ".join(overlap[:10]))
        tracked = {r[0] for r in self.db.execute("SELECT path FROM files")}
        writes, deletes = [], []
        for f in d["files"]:
            p = f["path"]
            if self.mode == "virtual" and p not in tracked:
                continue  # never materialized: nothing on disk to change
            if not self.profile.includes(p):
                continue
            if f["new"] is None:
                deletes.append(p)
            else:
                writes.append((p, f["new"]["kind"], f["new"]["id"]))
        for p in deletes:
            full = self._abs(p)
            if os.path.lexists(full):
                os.unlink(full)
                _prune_empty_dirs(os.path.dirname(full), self.root)
            self.db.execute("DELETE FROM files WHERE path = ?", (p,))
        self._set_base(target)
        n = self._materialize(writes)
        return {"base": target, "changed": n + len(deletes)}

    def rebase(self, onto: str | None = None) -> dict:
        onto = onto or self.config.get("track", "main")
        r = self.api.rebase(head=self.base, onto=onto)
        self.update(r["head"])
        return r

    # -- sparse profile management ---------------------------------------------------------------
    def sparse_add(self, dirs: list[str]) -> int:
        old = self.profile
        new = SparseProfile(old.prefixes + list(dirs))
        self.config["sparse"] = new.prefixes
        if self.mode == "full":
            self.config["mode"] = "sparse"
        self._save_config()
        files = [f for f in self._collect_files(self.state["root"], profile=new) if not old.includes(f[0])]
        return self._materialize(files)

    def sparse_remove(self, dirs: list[str]) -> int:
        drop = {normalize_path(d) for d in dirs}
        new = SparseProfile([p for p in self.profile.prefixes if p not in drop])
        if new.full:
            raise ClientError("cannot remove the last sparse directory")
        st = self.status()
        dirty = [p for p in st.modified + st.added if not new.includes(p)]
        if dirty:
            raise ClientError("local changes in directories being removed: " + ", ".join(dirty[:10]))
        removed = 0
        for (path,) in self.db.execute("SELECT path FROM files").fetchall():
            if not new.includes(path):
                full = self._abs(path)
                if os.path.lexists(full):
                    os.unlink(full)
                    _prune_empty_dirs(os.path.dirname(full), self.root)
                self.db.execute("DELETE FROM files WHERE path = ?", (path,))
                removed += 1
        self.config["sparse"] = new.prefixes
        self._save_config()
        return removed

    # -- local diff --------------------------------------------------------------------------------
    def diff_local(self, paths: list[str] | None = None) -> str:
        st = self.status()
        out = []
        for p in sorted(st.modified + st.added + st.removed):
            if paths and not any(p == x or p.startswith(x.rstrip("/") + "/") for x in paths):
                continue
            e = self.tree_lookup(p)
            old = self.fetcher.blob(e[1]) if e and e[0] != KIND_DIR else b""
            new = _file_kind_and_data(self._abs(p))[1] if os.path.lexists(self._abs(p)) else b""
            if is_binary(old) or is_binary(new):
                out.append(f"Binary file {p} differs\n")
                continue
            out.extend(difflib.unified_diff(old.decode("utf-8", "replace").splitlines(keepends=True),
                                            new.decode("utf-8", "replace").splitlines(keepends=True),
                                            f"a/{p}" if e else "/dev/null",
                                            f"b/{p}" if os.path.lexists(self._abs(p)) else "/dev/null"))
        return "".join(l if l.endswith("\n") else l + "\n" for l in out)

    def stack(self, onto: str | None = None) -> list[str]:
        """The local changesets not yet in ``onto`` (default: the tracked ref)."""
        onto = onto or self.config.get("track", "main")
        mb = self.api.merge_base(a=self.base, b=onto)["base"]
        out = []
        cur = self.base
        while cur and cur != mb:
            out.append(cur)
            cur = self.api.get_changeset(rev=cur)["parents"][0] if cur else None
        return out


def _prune_empty_dirs(path: str, stop: str) -> None:
    while os.path.abspath(path) != os.path.abspath(stop):
        try:
            os.rmdir(path)
        except OSError:
            return
        path = os.path.dirname(path)


__all__ = ["WorkingCopy", "ServerApi", "ObjectFetcher", "SparseProfile", "ClientError", "RemoteError"]

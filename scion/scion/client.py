"""The ``scn`` client (FR-CL-*; 06 §6.5 Client).

The client computes very little, and in exchange needs very little data locally. It keeps a bounded
object cache (FR-CL-02), lays out working-copy files in full, sparse or virtual mode (FR-CL-01),
watches the filesystem (FR-CL-04) and hands everything else to the server: commits, history, blame,
diffs, merges and rebases. There is nothing to push (FR-CL-06).

Fetching is want-only (FR-FP-01/02): from the root tree the client asks for the missing trees one
level at a time, then for the missing blobs, through one object endpoint (normally the node's
scion-daemon, FR-CL-12). Responses are per object, so an interrupted clone resumes with the objects
it already has (FR-FP-03).

Working-copy state lives in ``.scn/``: ``config.json`` and ``state.db`` (the base changeset and,
for every tracked file, its kind, blob and last-seen size and mtime).
"""
from __future__ import annotations

import difflib
import fnmatch
import json
import os
import sqlite3
import stat as statmod
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from . import fsmonitor
from .objects import (F_DENIED, F_MISSING, F_RESTRICTED, KIND_DIR, KIND_EXEC, KIND_FILE, KIND_LINK, ObjectError,
                      blob_id, decode_stored, decode_tree, encode_stored, is_binary, join, normalize_path,
                      split_path)
from .rpc import MAX_IDS_PER_REQUEST, ClientTls, FailoverClient, RemoteError, RpcClient
from .storage import BoundedFileObjectStore, LRUCache, ns_key

SCN_DIR = ".scn"
DEFAULT_CACHE_BYTES = 2 << 30
FETCH_BATCH = 500
FETCH_PARALLEL = 8
UPLOAD_CHUNK_BYTES = 32 << 20
WRITE_BATCH = 500


class ClientError(Exception):
    pass


# ============================================================================= talking to Scion
class ServerApi:
    """The metadata API: exactly the RPCs any job can use without a checkout (FR-QRY-10). Every
    call names the working copy's repository."""

    def __init__(self, url, repo: str, user: str | None = None, token: str | None = None,
                 tls: ClientTls | None = None):
        self.repo = repo
        self.rpc = FailoverClient(url, user=user, token=token, tier="client", tls=tls)

    def call(self, method: str, **params):
        return self.rpc.call(method, repo=self.repo, **params)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return lambda **params: self.call(name, **params)

    def put_objects(self, items) -> dict:
        return self.rpc.put_objects(self.repo, items)


class ObjectFetcher:
    """Want-only fetching into a bounded local cache. Every object received is verified against
    its id (FR-OBJ-04). Restricted objects are used but never cached (FR-IAM-05)."""

    def __init__(self, url: str, repo: str, local, user: str | None = None, token: str | None = None,
                 tls: ClientTls | None = None):
        self.repo, self.local = repo, local
        self.rpc = RpcClient(url, user=user, token=token, tier="client", tls=tls)
        self.counters: Counter = Counter()
        self.log: list[tuple[str, int]] = []  # (stage, ids) per request: trees by level, then blobs
        self._trees = LRUCache(50_000)
        self.denied: set[str] = set()

    def _remote(self, ids: list[str], stage: str, allow_denied: bool) -> dict[str, bytes]:
        self.counters["requests"] += 1
        self.log.append((stage, len(ids)))
        out = {}
        for oid, flags, stored in self.rpc.get_objects(self.repo, ids):
            if flags & F_DENIED:
                if not allow_denied:
                    raise ClientError(f"permission denied for object {oid[:12]}")
                self.denied.add(oid)
                self.counters["denied"] += 1
                continue
            if flags & F_MISSING:
                raise ClientError(f"object {oid[:12]} is missing")
            try:
                decode_stored(stored, expected_id=oid)
            except ObjectError as e:
                raise ClientError(f"rejected object {oid[:12]}: {e}") from None
            if flags & F_RESTRICTED:
                self.counters["restricted"] += 1
            else:
                self.local.put_stored(ns_key(self.repo, oid), stored, verify=False)
            self.counters["fetched"] += 1
            self.counters["bytes"] += len(stored)
            out[oid] = stored
        return out

    def fetch_batches(self, ids, stage: str = "blob", allow_denied: bool = False):
        """Yield ``{id: stored}`` batches: local hits first, then remote batches in parallel."""
        ids = list(dict.fromkeys(ids))
        self.counters["requested"] += len(ids)
        hits, missing = {}, []
        for oid in ids:
            stored = self.local.get_stored(ns_key(self.repo, oid))
            if stored is None:
                missing.append(oid)
            else:
                hits[oid] = stored
        self.counters["local_hits"] += len(hits)
        if hits:
            yield hits
        size = min(FETCH_BATCH, MAX_IDS_PER_REQUEST)
        batches = [missing[i:i + size] for i in range(0, len(missing), size)]
        if len(batches) <= 1:
            for b in batches:
                yield self._remote(b, stage, allow_denied)
            return
        with ThreadPoolExecutor(max_workers=FETCH_PARALLEL) as pool:
            yield from pool.map(lambda b: self._remote(b, stage, allow_denied), batches)

    def payloads(self, ids, stage: str = "blob", allow_denied: bool = False) -> dict[str, bytes]:
        out = {}
        for batch in self.fetch_batches(ids, stage, allow_denied):
            for oid, stored in batch.items():
                out[oid] = decode_stored(stored)[1]
        return out

    def trees(self, tids, level: int = 0, allow_denied: bool = False) -> dict[str, dict]:
        out, need = {}, []
        for t in dict.fromkeys(tids):
            v = self._trees.get(t)
            if v is None:
                need.append(t)
            else:
                out[t] = v
        for oid, payload in self.payloads(need, f"tree:{level}", allow_denied).items():
            entries = decode_tree(payload)
            self._trees.put(oid, entries)
            out[oid] = entries
        return out

    def tree(self, tid: str) -> dict:
        return self.trees([tid])[tid]

    def blob(self, oid: str) -> bytes:
        return self.payloads([oid])[oid]


# ============================================================================= sparse profiles
@dataclass
class SparseProfile:
    """The directories (or single files) a sparse checkout includes; empty means everything."""
    prefixes: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.prefixes = sorted({p for p in (normalize_path(x) for x in self.prefixes) if p})

    @property
    def full(self) -> bool:
        return not self.prefixes

    def includes(self, path: str) -> bool:
        return self.full or any(path == p or path.startswith(p + "/") for p in self.prefixes)

    def wants_dir(self, path: str) -> bool:
        """Should a checkout descend into this directory?"""
        return self.includes(path) or any(p.startswith(path + "/") for p in self.prefixes)


@dataclass
class Status:
    modified: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)
    examined: int = 0  # paths looked at on disk
    hashed: int = 0  # files whose contents were read
    used_fsmonitor: bool = False

    @property
    def dirty(self) -> bool:
        return bool(self.modified or self.added or self.removed)

    def changed(self) -> set[str]:
        return set(self.modified) | set(self.added) | set(self.removed)

    def to_dict(self) -> dict:
        return {"modified": self.modified, "added": self.added, "removed": self.removed,
                "untracked": self.untracked, "examined": self.examined, "hashed": self.hashed,
                "used_fsmonitor": self.used_fsmonitor}


def reserved(path: str) -> bool:
    """Repository content may never land in the working copy's own state directory."""
    return path == SCN_DIR or path.startswith(SCN_DIR + "/")


def read_disk(path: str) -> tuple[str, bytes]:
    """A file's kind and content: a symlink's content is its target (FR-CL-03)."""
    st = os.lstat(path)
    if statmod.S_ISLNK(st.st_mode):
        return KIND_LINK, os.fsencode(os.readlink(path))
    with open(path, "rb") as f:
        data = f.read()
    return (KIND_EXEC if st.st_mode & 0o111 else KIND_FILE), data


def _stat_kind(st) -> str:
    if statmod.S_ISLNK(st.st_mode):
        return KIND_LINK
    return KIND_EXEC if st.st_mode & 0o111 else KIND_FILE


def _prune_empty_dirs(path: str, stop: str) -> None:
    while os.path.abspath(path) != os.path.abspath(stop):
        try:
            os.rmdir(path)
        except OSError:
            return
        path = os.path.dirname(path)


def _token(config: dict) -> str | None:
    if os.environ.get("SCION_TOKEN"):
        return os.environ["SCION_TOKEN"]
    tf = config.get("token_file")
    if tf:
        with open(os.path.expanduser(tf)) as f:
            return f.read().strip()
    return None


# ================================================================================ working copy
class WorkingCopy:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.dot = os.path.join(self.root, SCN_DIR)
        try:
            with open(os.path.join(self.dot, "config.json")) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise ClientError(f"{self.root} is not a scn working copy") from None
        self.db = sqlite3.connect(os.path.join(self.dot, "state.db"), isolation_level=None, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(
            "CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, kind TEXT, blob TEXT, size INTEGER, "
            "mtime_ns INTEGER, state TEXT NOT NULL);"
            "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);")
        c = self.config
        tls = ClientTls(c["tls_ca"], c.get("tls_cert"), c.get("tls_key")) if c.get("tls_ca") else None
        token = _token(c)
        self.api = ServerApi(c["server"], c["repo"], c.get("user"), token, tls)
        self.local = BoundedFileObjectStore(c.get("cache_dir") or os.path.join(self.dot, "objects"),
                                            int(c.get("cache_bytes", DEFAULT_CACHE_BYTES)))
        self.fetcher = ObjectFetcher(c.get("objects") or c["server"], c["repo"], self.local, c.get("user"), token,
                                     tls)
        self._ignore = self._load_ignore()

    def close(self) -> None:
        self.db.close()
        self.api.rpc.close()
        self.fetcher.rpc.close_all()

    # -- construction ------------------------------------------------------------------------------
    @classmethod
    def clone(cls, dest: str, server: str, repo: str, objects: str | None = None, rev: str = "main",
              mode: str = "full", sparse: list[str] | None = None, user: str | None = None,
              token_file: str | None = None, tls_ca: str | None = None, cache_bytes: int = DEFAULT_CACHE_BYTES,
              cache_dir: str | None = None, tls_cert: str | None = None, tls_key: str | None = None) -> "WorkingCopy":
        """Check out ``rev`` (UC-01). Running it again on an interrupted clone resumes it. A service
        principal (such as a post-merge worker) presents ``tls_cert`` where the server requires
        client certificates of services (ADR-14)."""
        if mode not in ("full", "sparse", "virtual"):
            raise ClientError(f"unknown mode {mode!r}")
        if mode == "sparse" and not sparse:
            raise ClientError("a sparse checkout needs at least one directory")
        dest = os.path.abspath(dest)
        cfg_path = os.path.join(dest, SCN_DIR, "config.json")
        if os.path.exists(cfg_path):
            wc = cls(dest)
            if wc.get_meta("pending") is None or wc.config["server"] != server or wc.config["repo"] != repo:
                wc.close()
                raise ClientError(f"{dest} is already a working copy")
            return wc._finish_or_close()
        if os.path.isdir(dest) and os.listdir(dest):
            raise ClientError(f"{dest} exists and is not empty")
        os.makedirs(os.path.join(dest, SCN_DIR), exist_ok=True)
        config = {"server": server, "repo": repo, "objects": objects, "user": user, "token_file": token_file,
                  "tls_ca": tls_ca, "tls_cert": tls_cert, "tls_key": tls_key, "mode": mode, "sparse": SparseProfile(sparse or []).prefixes, "track": rev,
                  "cache_bytes": cache_bytes, "cache_dir": cache_dir}
        with open(cfg_path, "w") as f:
            json.dump(config, f, indent=2)
        wc = cls(dest)
        try:
            wc.set_meta("pending", wc.api.resolve(rev=rev))
        except BaseException:
            wc.close()
            raise
        return wc._finish_or_close()

    def _finish_or_close(self) -> "WorkingCopy":
        try:
            self.finish_checkout()
        except BaseException:
            self.close()  # the clone can be resumed later; this handle is done
            raise
        return self

    @classmethod
    def find(cls, start: str = ".") -> "WorkingCopy":
        cur = os.path.abspath(start)
        while True:
            if os.path.isfile(os.path.join(cur, SCN_DIR, "config.json")):
                return cls(cur)
            parent = os.path.dirname(cur)
            if parent == cur:
                raise ClientError("not inside a scn working copy")
            cur = parent

    def finish_checkout(self) -> dict:
        """Complete a clone: write every wanted file not already written (FR-FP-03)."""
        target = self.get_meta("pending")
        if target is None:
            return {"base": self.base, "written": 0}
        root = self.api.root_tree(rev=target)
        written = 0
        if self.mode != "virtual":
            written = self._write_files(self._collect_files(root, target))
        self._set_base(target, root)
        return {"base": target, "written": written}

    # -- state -------------------------------------------------------------------------------------
    def get_meta(self, key: str):
        row = self.db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def set_meta(self, key: str, value) -> None:
        if value is None:
            self.db.execute("DELETE FROM meta WHERE key = ?", (key,))
        else:
            self.db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, json.dumps(value)))

    def _set_base(self, cs: str, root: str) -> None:
        self.db.execute("BEGIN")
        self.set_meta("base", cs)
        self.set_meta("root", root)
        self.set_meta("pending", None)
        self.db.execute("COMMIT")

    @property
    def base(self) -> str | None:
        return self.get_meta("base")

    @property
    def root_tree(self) -> str:
        return self.get_meta("root")

    @property
    def mode(self) -> str:
        return self.config["mode"]

    @property
    def profile(self) -> SparseProfile:
        return SparseProfile(self.config.get("sparse") or []) if self.mode == "sparse" else SparseProfile([])

    def _save_config(self) -> None:
        tmp = os.path.join(self.dot, "config.json.tmp")
        with open(tmp, "w") as f:
            json.dump(self.config, f, indent=2)
        os.replace(tmp, os.path.join(self.dot, "config.json"))

    def _require_settled(self) -> None:
        pending = self.get_meta("pending")
        if pending:
            raise ClientError(f"an update to {pending[:12]} was interrupted; run `scn update {pending}` first")

    def _load_ignore(self) -> list[str]:
        try:
            with open(os.path.join(self.root, ".scnignore")) as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except FileNotFoundError:
            return []

    def _ignored(self, path: str) -> bool:
        base = path.rsplit("/", 1)[-1]
        return any(fnmatch.fnmatch(path, p) or fnmatch.fnmatch(base, p) for p in self._ignore)

    def rel(self, path: str) -> str:
        """A path given on the command line, relative to the working-copy root."""
        full = os.path.abspath(path)
        if full != self.root and not full.startswith(self.root + os.sep):
            raise ClientError(f"{path} is outside the working copy")
        return normalize_path(os.path.relpath(full, self.root).replace(os.sep, "/"))

    # -- trees ---------------------------------------------------------------------------------------
    def tree_lookup(self, path: str, root: str | None = None):
        node = (KIND_DIR, root or self.root_tree)
        for part in split_path(path):
            if node[0] != KIND_DIR:
                return None
            node = self.fetcher.tree(node[1]).get(part)
            if node is None:
                return None
        return node

    def _collect_files(self, root: str, rev: str, prefix: str = "", profile: SparseProfile | None = None):
        """Every file the profile wants, fetching each level's missing trees in one round trip
        (FR-FP-02). A tree the caller may not read is listed by the server instead, which shows the
        readable entries (UC-01 3b)."""
        profile = profile or self.profile
        files, level, depth = [], [(root, prefix)], prefix.count("/") + (1 if prefix else 0)
        while level:
            trees = self.fetcher.trees([t for t, _ in level], depth, allow_denied=True)
            nxt = []
            for tid, pfx in level:
                entries = trees.get(tid)
                if entries is None:
                    try:
                        listing = self.api.list_dir(rev=rev, path=pfx, probe=True)
                    except RemoteError:
                        continue
                    if listing is None:
                        continue  # nothing beneath is readable
                    entries = {e["name"]: (e["kind"], e["id"]) for e in listing}
                for name, (kind, oid) in entries.items():
                    path = join(pfx, name)
                    if reserved(path):
                        continue
                    if kind == KIND_DIR:
                        if profile.wants_dir(path):
                            nxt.append((oid, path))
                    elif profile.includes(path):
                        files.append((path, kind, oid))
            level, depth = nxt, depth + 1
        return files

    # -- writing files -------------------------------------------------------------------------------
    def _abs(self, path: str) -> str:
        return os.path.join(self.root, *path.split("/"))

    def _write_file(self, path: str, kind: str, data: bytes) -> None:
        full = self._abs(path)
        probe = self.root
        for part in split_path(path)[:-1]:
            probe = os.path.join(probe, part)
            if os.path.islink(probe):
                raise ClientError(f"cannot write {path}: {os.path.relpath(probe, self.root)} is a symlink")
            if os.path.lexists(probe) and not os.path.isdir(probe):
                os.unlink(probe)  # a tracked file is becoming a directory
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if os.path.isdir(full) and not os.path.islink(full):
            try:
                os.rmdir(full)
            except OSError:
                raise ClientError(f"cannot write {path}: a directory with untracked files is in the way") from None
        elif os.path.lexists(full):
            os.unlink(full)
        if kind == KIND_LINK:
            os.symlink(os.fsdecode(data), full)
            return
        fd = os.open(full, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                     0o755 if kind == KIND_EXEC else 0o644)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(full, 0o755 if kind == KIND_EXEC else 0o644)

    def _record(self, path: str, kind: str, blob: str, state: str = "n") -> None:
        st = os.lstat(self._abs(path))
        self.db.execute("INSERT OR REPLACE INTO files (path, kind, blob, size, mtime_ns, state) VALUES (?, ?, ?, ?, ?, ?)",
                        (path, kind, blob, st.st_size, st.st_mtime_ns, state))

    def _row(self, path: str):
        return self.db.execute("SELECT kind, blob, size, mtime_ns, state FROM files WHERE path = ?", (path,)).fetchone()

    def _unchanged_on_disk(self, path: str, row) -> bool:
        try:
            st = os.lstat(self._abs(path))
        except FileNotFoundError:
            return False
        return st.st_size == row[2] and st.st_mtime_ns == row[3] and _stat_kind(st) == row[0]

    def _write_files(self, files) -> int:
        """Write files, skipping any already written by an earlier, interrupted run. Rows are
        committed batch by batch, so progress survives an interruption."""
        todo: dict[str, list[tuple[str, str]]] = {}
        for path, kind, oid in files:
            row = self._row(path)
            if row and row[0] == kind and row[1] == oid and row[4] == "n" and self._unchanged_on_disk(path, row):
                continue
            todo.setdefault(oid, []).append((path, kind))
        written = 0
        for batch in self.fetcher.fetch_batches(list(todo), "blob", allow_denied=True):
            self.db.execute("BEGIN")
            try:
                for oid, stored in batch.items():
                    data = decode_stored(stored)[1]
                    for path, kind in todo[oid]:
                        self._write_file(path, kind, data)
                        self._record(path, kind, oid)
                        written += 1
                        if written % WRITE_BATCH == 0:
                            self.db.execute("COMMIT")
                            self.db.execute("BEGIN")
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("COMMIT")  # keep what was written
                raise
        return written

    # -- virtual checkouts: materialize on demand (FR-CL-10, UC-02) -----------------------------------
    def materialize(self, paths: list[str]) -> int:
        self._require_settled()
        files = []
        for p in paths:
            p = normalize_path(p)
            e = self.tree_lookup(p)
            if e is None:
                raise ClientError(f"{p}: not in the checked-out revision")
            if e[0] == KIND_DIR:
                files.extend(self._collect_files(e[1], self.base, p, SparseProfile([])))
            else:
                files.append((p, e[0], e[1]))
        known = {r[0] for r in self.db.execute("SELECT path FROM files")}
        return self._write_files([f for f in files if f[0] not in known])

    def read(self, path: str) -> bytes:
        """A file's content, materialized first in a virtual checkout."""
        path = normalize_path(path)
        full = self._abs(path)
        if not os.path.lexists(full):
            if self.mode != "virtual" or self._row(path):
                raise FileNotFoundError(path)
            self.materialize([path])
        return read_disk(full)[1]

    def listdir(self, path: str = "") -> list[dict]:
        e = self.tree_lookup(normalize_path(path))
        if e is None or e[0] != KIND_DIR:
            raise ClientError(f"{path or '/'}: not a directory")
        return [{"name": n, "kind": k, "id": oid} for n, (k, oid) in sorted(self.fetcher.tree(e[1]).items())]

    # -- status (UC-03) ------------------------------------------------------------------------------
    def _walk_disk(self) -> set[str]:
        out, profile = set(), self.profile
        for dirpath, dirnames, filenames in os.walk(self.root):
            rel = os.path.relpath(dirpath, self.root)
            rel = "" if rel == "." else rel.replace(os.sep, "/")
            if rel == "":
                dirnames[:] = [d for d in dirnames if d != SCN_DIR]
            for d in list(dirnames):
                if os.path.islink(os.path.join(dirpath, d)):  # a symlink to a directory is a file to us
                    dirnames.remove(d)
                    filenames.append(d)
            if not profile.full:
                dirnames[:] = [d for d in dirnames if profile.wants_dir(join(rel, d))]
            out.update(join(rel, f) for f in filenames)
        return out

    def _fsmonitor_candidates(self) -> set[str] | None:
        if not self.config.get("fsmonitor", True):
            return None
        info = fsmonitor.query(self.root, self.get_meta("fsmonitor"))
        if info is None:
            return None
        token, paths, rescan = info
        self.set_meta("fsmonitor", token)
        if rescan:
            return None
        cands = set(paths) | set(self.get_meta("dirty") or [])
        expanded = set()
        for p in cands:
            full = self._abs(p)
            if os.path.isdir(full) and not os.path.islink(full):
                for dp, dns, fns in os.walk(full):
                    r = os.path.relpath(dp, self.root).replace(os.sep, "/")
                    expanded.update(join(r, f) for f in fns)
                    expanded.update(join(r, d) for d in dns if os.path.islink(os.path.join(dp, d)))
            else:
                expanded.add(p)
            # a deleted or moved directory: every tracked file beneath it is a candidate
            expanded.update(r[0] for r in self.db.execute("SELECT path FROM files WHERE path > ? AND path < ?",
                                                          (p + "/", p + "0")))
        return {c for c in expanded if c != SCN_DIR and not c.startswith(SCN_DIR + "/")}

    def status(self, use_fsmonitor: bool = True) -> Status:
        st = Status()
        candidates = self._fsmonitor_candidates() if use_fsmonitor else None
        if candidates is not None:
            st.used_fsmonitor = True
            profile = self.profile
            on_disk = {c for c in candidates if profile.includes(c) and os.path.lexists(self._abs(c))}
            rows = {}
            for c in candidates:
                r = self._row(c)
                if r:
                    rows[c] = r
        else:
            on_disk = self._walk_disk()
            rows = {r[0]: r[1:] for r in self.db.execute("SELECT path, kind, blob, size, mtime_ns, state FROM files")}
        refresh = []
        for path, (kind, blob, size, mtime, state) in rows.items():
            st.examined += 1
            if state == "a":
                if path in on_disk:
                    st.added.append(path)
                else:
                    self.db.execute("DELETE FROM files WHERE path = ?", (path,))  # added, then deleted again
                continue
            if state == "r" or path not in on_disk:
                st.removed.append(path)
                continue
            s = os.lstat(self._abs(path))
            if s.st_size == size and s.st_mtime_ns == mtime and _stat_kind(s) == kind:
                continue
            k2, data = read_disk(self._abs(path))
            st.hashed += 1
            if k2 == kind and blob_id(data) == blob:
                refresh.append((s.st_size, s.st_mtime_ns, path))  # touched but unchanged
            else:
                st.modified.append(path)
        for path in sorted(on_disk - set(rows)):
            st.examined += 1
            if self._ignored(path):
                continue
            if self.mode == "virtual":
                e = self.tree_lookup(path)
                if e is not None and e[0] != KIND_DIR:  # written without being read (UC-03 2a)
                    k2, data = read_disk(self._abs(path))
                    st.hashed += 1
                    if (k2, blob_id(data)) == (e[0], e[1]):
                        self._record(path, e[0], e[1])
                    else:
                        self.db.execute("INSERT OR REPLACE INTO files (path, kind, blob, size, mtime_ns, state) "
                                        "VALUES (?, ?, ?, -1, -1, 'n')", (path, e[0], e[1]))
                        st.modified.append(path)
                    continue
            st.untracked.append(path)
        if refresh:
            self.db.executemany("UPDATE files SET size = ?, mtime_ns = ? WHERE path = ?", refresh)
        for lst in (st.modified, st.added, st.removed, st.untracked):
            lst.sort()
        self.set_meta("dirty", sorted(st.changed() | set(st.untracked)))
        return st

    # -- local edits (FR-CL-05) ----------------------------------------------------------------------
    def add(self, paths: list[str]) -> list[str]:
        self._require_settled()
        added = []
        for p in paths:
            p = normalize_path(p)
            if reserved(p):
                raise ClientError(f"{p}: the working copy's state directory can't be tracked")
            full = self._abs(p)
            targets = []
            if os.path.isdir(full) and not os.path.islink(full):
                for dp, dns, fns in os.walk(full):
                    r = os.path.relpath(dp, self.root).replace(os.sep, "/")
                    dns[:] = [d for d in dns if not (r == "" and d == SCN_DIR)]
                    targets.extend(join(r, f) for f in fns)
            elif os.path.lexists(full):
                targets.append(p)
            else:
                raise ClientError(f"{p}: no such file")
            for t in targets:
                row = self._row(t)
                if row is None:
                    self.db.execute("INSERT INTO files (path, state) VALUES (?, 'a')", (t,))
                    added.append(t)
                elif row[4] == "r":
                    self.db.execute("UPDATE files SET state = 'n', size = -1 WHERE path = ?", (t,))
        if self.mode == "sparse":
            outside = [t for t in added if not self.profile.includes(t)]
            if outside:  # a file added outside the profile joins it, so it stays visible (T-CL-12)
                self.config["sparse"] = SparseProfile(self.profile.prefixes + outside).prefixes
                self._save_config()
        self.set_meta("dirty", sorted(set(self.get_meta("dirty") or []) | set(added)))
        return added

    def remove(self, paths: list[str], keep: bool = False) -> list[str]:
        self._require_settled()
        removed = []
        for p in paths:
            p = normalize_path(p)
            row = self._row(p)
            if row is None:
                raise ClientError(f"{p}: not tracked")
            if not keep and os.path.lexists(self._abs(p)):
                os.unlink(self._abs(p))
                _prune_empty_dirs(os.path.dirname(self._abs(p)), self.root)
            if row[4] == "a":
                self.db.execute("DELETE FROM files WHERE path = ?", (p,))
            else:
                self.db.execute("UPDATE files SET state = 'r' WHERE path = ?", (p,))
            removed.append(p)
        self.set_meta("dirty", sorted(set(self.get_meta("dirty") or []) | set(removed)))
        return removed

    def restore(self, paths: list[str]) -> list[str]:
        """Discard local changes: files go back to the base content (FR-CL-05)."""
        self._require_settled()
        restored = []
        for p in paths:
            p = normalize_path(p)
            e = self.tree_lookup(p)
            row = self._row(p)
            if e is None or e[0] == KIND_DIR:
                if row and row[4] == "a":
                    self.db.execute("DELETE FROM files WHERE path = ?", (p,))
                    restored.append(p)
                    continue
                raise ClientError(f"{p}: not in the base revision")
            self._write_file(p, e[0], self.fetcher.blob(e[1]))
            self._record(p, e[0], e[1])
            restored.append(p)
        return restored

    def diff_local(self, paths: list[str] | None = None) -> str:
        st = self.status()
        prefixes = [normalize_path(p) for p in paths] if paths else None
        out = []
        for p in sorted(st.changed()):
            if prefixes and not any(p == x or p.startswith(x + "/") for x in prefixes):
                continue
            e = self.tree_lookup(p)
            old = self.fetcher.blob(e[1]) if e and e[0] != KIND_DIR else None
            exists = os.path.lexists(self._abs(p)) and self._row(p)[4] != "r"
            new = read_disk(self._abs(p))[1] if exists else None
            if is_binary(old or b"") or is_binary(new or b""):
                out.append(f"Binary file {p} differs\n")
                continue
            lines = difflib.unified_diff((old or b"").decode("utf-8", "replace").splitlines(keepends=True),
                                         (new or b"").decode("utf-8", "replace").splitlines(keepends=True),
                                         f"a/{p}" if old is not None else "/dev/null",
                                         f"b/{p}" if new is not None else "/dev/null")
            out.extend(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n" for line in lines)
        return "".join(out)

    # -- commit: the server creates the changeset; there is nothing to push (UC-04) -------------------
    def commit(self, message: str, paths: list[str] | None = None, addremove: bool = False) -> str:
        self._require_settled()
        st = self.status()
        prefixes = [normalize_path(p) for p in paths] if paths else None

        def wanted(p):
            return prefixes is None or any(p == x or p.startswith(x + "/") for x in prefixes)

        writes = [p for p in st.modified + st.added + (st.untracked if addremove else []) if wanted(p)]
        deletes = [p for p in st.removed if wanted(p)]
        if not writes and not deletes:
            raise ClientError("nothing to commit")
        files, uploads, written = [], {}, {}
        for p in writes:
            kind, data = read_disk(self._abs(p))
            oid = blob_id(data)
            uploads[oid] = data
            written[p] = (kind, oid)
            files.append({"path": p, "kind": kind, "blob": oid})
        files.extend({"path": p, "delete": True} for p in deletes)
        self.upload(uploads)
        cs = self.api.create_changeset(parents=[self.base], files=files, message=message)["id"]
        root = self.api.root_tree(rev=cs)
        self.db.execute("BEGIN")
        for p, (kind, oid) in written.items():
            self._record(p, kind, oid)
        for p in deletes:
            self.db.execute("DELETE FROM files WHERE path = ?", (p,))
        self.set_meta("base", cs)
        self.set_meta("root", root)
        self.db.execute("COMMIT")
        self.set_meta("dirty", sorted((set(self.get_meta("dirty") or []) - set(written) - set(deletes))))
        return cs

    def upload(self, blobs: dict[str, bytes]) -> int:
        """Upload the blobs the server lacks (FR-WR-06), in bounded chunks."""
        if not blobs:
            return 0
        ids, missing = list(blobs), []
        for i in range(0, len(ids), MAX_IDS_PER_REQUEST):
            missing.extend(self.api.has_objects(ids=ids[i:i + MAX_IDS_PER_REQUEST]))
        chunk, size = [], 0
        for oid in missing:
            stored = encode_stored("blob", blobs[oid])
            chunk.append((oid, 0, stored))
            size += len(stored)
            if size >= UPLOAD_CHUNK_BYTES:
                self.api.put_objects(chunk)
                chunk, size = [], 0
        if chunk:
            self.api.put_objects(chunk)
        return len(missing)

    # -- moving between revisions (UC-05, UC-06) -------------------------------------------------------
    def update(self, rev: str, clean: bool = False) -> dict:
        """Move to ``rev``, applying only the diff (FR-CL-07). Local changes to paths the diff
        touches are protected unless ``clean``. An interrupted update is finished by running it
        again."""
        if self.base is None:
            raise ClientError("the clone was interrupted; run the same `scn clone` again to finish it")
        target = self.api.resolve(rev=rev)
        pending = self.get_meta("pending")
        if pending and pending != target:
            raise ClientError(f"an update to {pending[:12]} was interrupted; run `scn update {pending}` first")
        if target == self.base and not pending:
            return {"base": target, "written": 0, "deleted": 0}
        profile = self.profile
        d = self.api.diff(a=self.base, b=target, paths=profile.prefixes or None)
        st = self.status()
        local = st.changed() | set(st.untracked)
        touched = {f["path"] for f in d["files"]}
        overlap = sorted(p for p in local if p in touched or any(t.startswith(p + "/") or p.startswith(t + "/")
                                                                    for t in touched))
        if overlap and not clean:
            raise ClientError("local changes would be overwritten: " + ", ".join(overlap[:10]))
        tracked = {r[0] for r in self.db.execute("SELECT path FROM files")}
        self.set_meta("pending", target)
        writes, deleted = [], 0
        for f in sorted(d["files"], key=lambda f: f["path"]):
            p = f["path"]
            if reserved(p) or not profile.includes(p) or (self.mode == "virtual" and p not in tracked):
                continue  # outside the profile, or never materialized: nothing on disk changes
            if f["new"] is None:
                full = self._abs(p)
                if os.path.lexists(full):
                    os.unlink(full)
                    _prune_empty_dirs(os.path.dirname(full), self.root)
                self.db.execute("DELETE FROM files WHERE path = ?", (p,))
                deleted += 1
            else:
                writes.append((p, f["new"]["kind"], f["new"]["id"]))
        written = self._write_files(writes)
        self._set_base(target, self.api.root_tree(rev=target))
        return {"base": target, "written": written, "deleted": deleted}

    def rebase(self, onto: str | None = None) -> dict:
        """Rebase the local stack onto ``onto`` on the server, then update to it (FR-CL-08)."""
        self._require_settled()
        r = self.api.rebase(head=self.base, onto=onto or self.config.get("track") or "main")
        self.update(r["head"])
        return r

    def stack(self, onto: str | None = None) -> list[str]:
        """The changesets on the working copy's base that ``onto`` doesn't contain, newest first."""
        onto = onto or self.config.get("track") or "main"
        mb = self.api.merge_base(a=self.base, b=onto)["base"]
        out, cur = [], self.base
        while cur and cur != mb:
            out.append(cur)
            parents = self.api.get_changeset(rev=cur)["parents"]
            cur = parents[0] if parents else None
        return out

    # -- sparse profiles (FR-CL-09) ----------------------------------------------------------------------
    def sparse_add(self, dirs: list[str]) -> int:
        self._require_settled()
        if self.mode != "sparse":
            raise ClientError("not a sparse checkout")
        old = self.profile
        new = SparseProfile(old.prefixes + list(dirs))
        self.config["sparse"] = new.prefixes
        self._save_config()
        files = [f for f in self._collect_files(self.root_tree, self.base, profile=new) if not old.includes(f[0])]
        return self._write_files(files)

    def sparse_remove(self, dirs: list[str]) -> int:
        self._require_settled()
        if self.mode != "sparse":
            raise ClientError("not a sparse checkout")
        drop = {normalize_path(d) for d in dirs}
        new = SparseProfile([p for p in self.profile.prefixes if p not in drop])
        if new.full:
            raise ClientError("cannot remove the last directory of a sparse checkout")
        st = self.status()
        dirty = sorted(p for p in st.changed() | set(st.untracked) if not new.includes(p))
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

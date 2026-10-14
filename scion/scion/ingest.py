"""git → Scion ingestion (FR-MG-*, UC-23; 06 §6.6 git ingestion).

* **Streaming, bounded memory (FR-MG-04).** Commits stream from one ``git rev-list`` process, and
  commits, trees and blobs from one long-lived ``git cat-file --batch`` process. Each commit is
  diffed against its first parent by walking the two git trees and skipping identical subtrees, so
  only changed directories are read. Caches are bounded.
* **Changes relative to the first parent (FR-MG-01).** Exactly Scion's changeset format; merges keep
  all their parents.
* **Ordering invariant (FR-MG-02).** Before anything is written, every boundary commit of the range
  (a parent outside it) must already be ingested; and every commit's parents are checked again as it
  is written. A bad range is refused with nothing written.
* **Incremental (FR-MG-03).** The git ↔ changeset map is persisted, so a re-run ingests only new
  commits; it maps both ways (FR-MG-07).
* **Verification (FR-MG-05)** compares every file of a revision with git's, kind and bytes.
"""
from __future__ import annotations

import codecs
import subprocess
import time

from .objects import blob_id
from .repo import Repository
from .storage import LRUCache
from .trees import TreeOps

MODE_KIND = {"100644": "f", "100664": "f", "100755": "x", "120000": "l"}
TREE_MODE, SUBMODULE_MODE = "40000", "160000"
class IngestError(Exception):
    pass


class CatFile:
    """One long-lived ``git cat-file --batch`` process."""

    def __init__(self, git_dir: str):
        self.p = subprocess.Popen(["git", "-C", git_dir, "cat-file", "--batch"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

    def read(self, sha: str) -> tuple[str, bytes]:
        self.p.stdin.write(sha.encode() + b"\n")
        self.p.stdin.flush()
        header = self.p.stdout.readline().split()
        if len(header) < 3:
            raise IngestError(f"git cat-file: missing object {sha}")
        size = int(header[2])
        data = self.p.stdout.read(size)
        self.p.stdout.read(1)  # the newline after the object
        return header[1].decode(), data

    def close(self) -> None:
        try:
            self.p.stdin.close()
        finally:
            self.p.wait()
            self.p.stdout.close()


def parse_commit(raw: bytes) -> dict:
    """A git commit's fields. The author and message are decoded with the commit's ``encoding``
    header when it has one, as ``git log`` does; UTF-8 otherwise."""
    head, _, message = raw.partition(b"\n\n")
    encoding = "utf-8"
    for line in head.split(b"\n"):
        if line.startswith(b"encoding "):
            try:
                encoding = codecs.lookup(line[9:].decode("ascii").strip()).name
            except (LookupError, UnicodeDecodeError):
                pass  # an encoding Python doesn't know: read it as UTF-8
    info = {"tree": None, "parents": [], "author": "unknown", "timestamp": 0,
            "message": message.decode(encoding, "replace")}
    for line in head.split(b"\n"):
        if line.startswith(b"tree "):
            info["tree"] = line[5:].decode()
        elif line.startswith(b"parent "):
            info["parents"].append(line[7:].decode())
        elif line.startswith(b"author "):
            text = line[7:].decode(encoding, "replace")
            ident, _, rest = text.rpartition(">")
            info["author"] = ident + ">"
            parts = rest.split()
            if parts and parts[0].lstrip("-").isdigit():
                info["timestamp"] = int(parts[0])
    return info


def parse_tree(raw: bytes) -> dict[str, tuple[str, str]]:
    """git's binary tree format: ``<mode> <name>\\0<20-byte sha>``, repeated."""
    out, i, n = {}, 0, len(raw)
    while i < n:
        sp = raw.index(b" ", i)
        nul = raw.index(b"\0", sp)
        mode = raw[i:sp].decode()
        try:
            name = raw[sp + 1:nul].decode("utf-8")
        except UnicodeDecodeError:
            raise IngestError(f"a path that is not UTF-8: {raw[sp + 1:nul]!r}") from None
        out[name] = (mode, raw[nul + 1:nul + 21].hex())
        i = nul + 21
    return out


class GitIngester:
    def __init__(self, repo: Repository, git_dir: str, verbose: bool = False, cache_bytes: int = 16 << 20):
        """``cache_bytes`` bounds every cache used while ingesting, so memory does not grow with
        the history (FR-MG-04)."""
        self.repo, self.git_dir, self.verbose, self.cache_bytes = repo, git_dir, verbose, cache_bytes
        self._trees = LRUCache(100_000, max_bytes=cache_bytes // 4)  # parsed git trees
        self._blobs = LRUCache(100_000, max_bytes=cache_bytes // 8)  # git blob sha -> Scion blob id
        self.stats = self._new_stats()

    @staticmethod
    def _new_stats() -> dict:
        return {"commits": 0, "skipped": 0, "files": 0, "blobs_read": 0, "trees_read": 0, "submodules_skipped": 0}

    # -- the map (FR-MG-07) -------------------------------------------------------------------------
    def changeset_for(self, git_sha: str) -> str | None:
        row = self.repo.meta.git_map_lookup(git=git_sha)
        return row[1] if row else None

    def git_for(self, cs: str) -> str | None:
        row = self.repo.meta.git_map_lookup(cs=cs)
        return row[0] if row else None

    # -- git plumbing --------------------------------------------------------------------------------
    def _git(self, *args) -> bytes:
        r = subprocess.run(["git", "-C", self.git_dir, *args], capture_output=True)
        if r.returncode != 0:
            raise IngestError(f"git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
        return r.stdout

    def _tree(self, cat: CatFile, sha: str) -> dict:
        tree = self._trees.get(sha)
        if tree is None:
            self.stats["trees_read"] += 1
            kind, raw = cat.read(sha)
            if kind != "tree":
                raise IngestError(f"{sha} is a {kind}, not a tree")
            tree = parse_tree(raw)
            self._trees.put(sha, tree, 2 * len(raw))
        return tree

    def _blob(self, cat: CatFile, sha: str) -> str:
        bid = self._blobs.get(sha)
        if bid is None:
            self.stats["blobs_read"] += 1
            bid = self.repo.put_blob(cat.read(sha)[1])
            self._blobs.put(sha, bid, 128)
        return bid

    def _diff(self, cat: CatFile, old: str | None, new: str | None, prefix: str, out: list) -> None:
        """Changes between two git trees as Scion file entries, skipping identical subtrees."""
        if old == new:
            return
        a = self._tree(cat, old) if old else {}
        b = self._tree(cat, new) if new else {}
        for name in sorted(set(a) | set(b)):
            x, y = a.get(name), b.get(name)
            if x == y:
                continue
            path = f"{prefix}/{name}" if prefix else name
            xd = x is not None and x[0] == TREE_MODE
            yd = y is not None and y[0] == TREE_MODE
            if xd or yd:
                self._diff(cat, x[1] if xd else None, y[1] if yd else None, path, out)
            xf = x if x is not None and not xd else None
            yf = y if y is not None and not yd else None
            if (xf and xf[0] == SUBMODULE_MODE) or (yf and yf[0] == SUBMODULE_MODE):
                self.stats["submodules_skipped"] += 1  # submodules are not monorepo content (UC-23 2b)
                if xf and xf[0] == SUBMODULE_MODE:
                    xf = None
                if yf and yf[0] == SUBMODULE_MODE:
                    yf = None
            if xf == yf:
                continue
            if yf is None:
                if xf is not None:
                    out.append({"path": path, "delete": True})
                continue
            kind = MODE_KIND.get(yf[0])
            if kind is None:
                raise IngestError(f"unsupported mode {yf[0]} for {path}")
            out.append({"path": path, "kind": kind, "blob": self._blob(cat, yf[1])})

    # -- ingestion -----------------------------------------------------------------------------------
    def check_boundary(self, rev: str) -> int:
        """The ordering invariant for a range, before anything is written (FR-MG-02): every commit
        just outside it must already be ingested."""
        missing, boundary = [], 0
        proc = subprocess.Popen(["git", "-C", self.git_dir, "rev-list", "--boundary", rev], stdout=subprocess.PIPE)
        try:
            for line in proc.stdout:
                if line.startswith(b"-"):
                    boundary += 1
                    sha = line[1:].strip().decode()
                    if self.changeset_for(sha) is None:
                        missing.append(sha)
        finally:
            proc.stdout.close()
            if proc.wait() != 0:
                raise IngestError(f"git rev-list {rev} failed")
        if missing:
            raise IngestError(f"ordering invariant: {len(missing)} commit(s) just outside {rev} are not ingested, "
                              f"e.g. {missing[0][:12]}; ingest them first (nothing was written)")
        return boundary

    def ingest(self, rev: str = "HEAD", ref: str | None = "main", limit: int | None = None) -> dict:
        """Ingest ``rev``'s history; returns this run's counts (``stats``)."""
        t0 = time.time()
        self.stats = self._new_stats()
        self.check_boundary(rev)
        # the repository's caches help ingestion only for the previous few commits: bound them
        restore = (self.repo.cache.limit(max_bytes=self.cache_bytes // 2),
                   self.repo.derived.cache.limit(max_bytes=self.cache_bytes // 8))
        cat = CatFile(self.git_dir)
        proc = subprocess.Popen(["git", "-C", self.git_dir, "rev-list", "--topo-order", "--reverse", rev],
                                stdout=subprocess.PIPE)
        tip = None
        try:
            for line in proc.stdout:
                sha = line.strip().decode()
                done = self.changeset_for(sha)
                if done is not None:
                    tip = done
                    self.stats["skipped"] += 1
                    continue
                kind, raw = cat.read(sha)
                if kind != "commit":
                    raise IngestError(f"{sha} is a {kind}, not a commit")
                info = parse_commit(raw)
                parents = []
                for p in info["parents"]:
                    mapped = self.changeset_for(p)
                    if mapped is None:  # can't happen after check_boundary, unless git changed underneath
                        raise IngestError(f"ordering invariant: parent {p[:12]} of {sha[:12]} is not ingested")
                    parents.append(mapped)
                first_tree = None
                if info["parents"]:
                    first_tree = parse_commit(cat.read(info["parents"][0])[1])["tree"]
                files: list = []
                self._diff(cat, first_tree, info["tree"], "", files)
                try:
                    cs = self.repo.create_changeset(parents, files, info["author"], info["message"],
                                                    info["timestamp"], extra={"git": sha})
                except ValueError as e:
                    raise IngestError(f"{sha[:12]}: {e}") from None
                self.repo.meta.git_map_put(sha, cs)
                self.stats["commits"] += 1
                self.stats["files"] += len(files)
                tip = cs
                if self.verbose and self.stats["commits"] % 1000 == 0:
                    print(f"ingested {self.stats['commits']} commits", flush=True)
                if limit and self.stats["commits"] >= limit:
                    break
        finally:
            proc.stdout.close()
            proc.terminate()
            proc.wait()
            cat.close()
            self.repo.cache.limit(*restore[0])
            self.repo.derived.cache.limit(*restore[1])
        if ref and tip:
            old = self.repo.get_ref(ref)
            if old != tip and not self.repo.update_ref(ref, old, tip):
                raise IngestError(f"{ref} moved during ingestion; run it again")
        self.stats["seconds"] = round(time.time() - t0, 3)
        self.stats["tip"] = tip
        return dict(self.stats)

    def verify(self, rev: str = "HEAD") -> dict:
        """Compare every file of ``rev`` with git's, kind and bytes (FR-MG-05). The trees are read
        back from storage, as another process would see them, not from the cache their writes
        filled."""
        sha = self._git("rev-parse", "--verify", f"{rev}^{{commit}}").decode().strip()
        cs = self.changeset_for(sha)
        if cs is None:
            raise IngestError(f"{rev} has not been ingested")
        stored = TreeOps(self.repo.objects, LRUCache(100_000, max_bytes=self.cache_bytes // 4))
        ours = {p: (k, oid) for p, k, oid in stored.walk(self.repo.root_tree(cs))}
        theirs = {}
        cat = CatFile(self.git_dir)
        try:
            for entry in self._git("ls-tree", "-r", "-z", sha).split(b"\0"):
                if not entry:
                    continue
                meta, path = entry.split(b"\t", 1)
                mode, otype, osha = meta.decode().split()
                if otype != "blob":
                    continue  # submodules
                theirs[path.decode("utf-8")] = (MODE_KIND.get(mode, "?"), blob_id(cat.read(osha)[1]))
        finally:
            cat.close()
        mismatches = sorted(p for p in set(ours) | set(theirs) if ours.get(p) != theirs.get(p))
        return {"ok": not mismatches, "files": len(theirs), "mismatches": mismatches[:50], "changeset": cs, "git": sha}

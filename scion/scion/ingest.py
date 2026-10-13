"""git → Scion ingestion.

* Streaming: commits are read one at a time from ``git rev-list`` and blob contents from a single
  long-lived ``git cat-file --batch`` process, so memory stays flat whatever the history size.
* Ordering invariant: commits are ingested in topological order, so every parent exists before
  its children.  This is asserted for every commit.
* Changes relative to the first parent: each changeset is built from
  ``git diff-tree <first-parent> <commit>``, matching Scion's changeset format.
* Incremental: the git→changeset map is persisted, so re-running ingests only new commits
  (which is how the monorepo was kept in sync while the migration was in progress).
* ``verify`` compares the final tree with ``git ls-tree`` byte for byte.
"""
from __future__ import annotations

import subprocess
import sys
import time
from collections import OrderedDict

from .objects import blob_id

MODE_KIND = {"100644": "f", "100755": "x", "120000": "l", "100664": "f"}


class IngestError(Exception):
    pass


class CatFile:
    def __init__(self, git_path: str):
        self.p = subprocess.Popen(["git", "-C", git_path, "cat-file", "--batch"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read(self, sha: str) -> tuple[str, bytes]:
        self.p.stdin.write(sha.encode() + b"\n")
        self.p.stdin.flush()
        header = self.p.stdout.readline().split()
        if len(header) < 3:
            raise IngestError(f"git cat-file: missing object {sha}")
        size = int(header[2])
        data = self.p.stdout.read(size)
        self.p.stdout.read(1)
        return header[1].decode(), data

    def close(self) -> None:
        self.p.stdin.close()
        self.p.wait()


def _parse_commit(raw: bytes) -> dict:
    head, _, message = raw.partition(b"\n\n")
    info = {"message": message.decode("utf-8", "replace"), "author": "unknown", "timestamp": 0}
    for line in head.split(b"\n"):
        if line.startswith(b"author "):
            text = line[7:].decode("utf-8", "replace")
            name, _, rest = text.rpartition(">")
            info["author"] = name + ">"
            parts = rest.split()
            if parts:
                info["timestamp"] = int(parts[0])
    return info


class GitIngester:
    def __init__(self, repo, git_path: str, verbose: bool = False):
        self.repo = repo
        self.git_path = git_path
        self.verbose = verbose
        self.blob_map: OrderedDict[str, str] = OrderedDict()  # git blob sha -> scion blob id
        self.stats = {"commits": 0, "skipped": 0, "files": 0, "blobs_read": 0, "submodules_skipped": 0}

    def _git(self, *args) -> bytes:
        return subprocess.run(["git", "-C", self.git_path, *args], check=True, capture_output=True).stdout

    def _diff_tree(self, parent: str | None, sha: str):
        args = ["diff-tree", "-r", "-z", "--no-renames", "--no-commit-id"]
        args += [parent, sha] if parent else ["--root", sha]
        out = self._git(*args).split(b"\0")
        i = 0
        while i < len(out) - 1:
            meta = out[i].decode()
            if not meta.startswith(":"):
                i += 1
                continue
            old_mode, new_mode, old_sha, new_sha, status = meta[1:].split(" ")
            path = out[i + 1].decode("utf-8", "surrogateescape")
            i += 2
            yield old_mode, new_mode, old_sha, new_sha, status[0], path

    def _scion_blob(self, cat: CatFile, sha: str) -> str:
        hit = self.blob_map.get(sha)
        if hit is not None:
            self.blob_map.move_to_end(sha)
            return hit
        _, data = cat.read(sha)
        self.stats["blobs_read"] += 1
        bid = self.repo.put_blob(data)
        self.blob_map[sha] = bid
        if len(self.blob_map) > 200_000:
            self.blob_map.popitem(last=False)
        return bid

    def ingest(self, rev: str = "HEAD", target_ref: str | None = "main", limit: int | None = None) -> dict:
        t0 = time.time()
        meta = self.repo.meta
        cat = CatFile(self.git_path)
        proc = subprocess.Popen(["git", "-C", self.git_path, "rev-list", "--topo-order", "--reverse", "--parents", rev],
                                stdout=subprocess.PIPE)
        tip_cs = None
        try:
            for line in proc.stdout:
                sha, *parents = line.decode().split()
                existing = meta.git_map_get(sha)
                if existing:
                    tip_cs = existing
                    self.stats["skipped"] += 1
                    continue
                parent_cs = []
                for p in parents:
                    m = meta.git_map_get(p)
                    if m is None:
                        raise IngestError(f"ordering invariant violated: parent {p} of {sha} not ingested")
                    parent_cs.append(m)
                _, raw = cat.read(sha)
                info = _parse_commit(raw)
                files = []
                for old_mode, new_mode, _old_sha, new_sha, status, path in self._diff_tree(
                        parents[0] if parents else None, sha):
                    if "160000" in (old_mode, new_mode):
                        # Submodules are not part of the monorepo's content.
                        self.stats["submodules_skipped"] += 1
                        if new_mode == "160000" and old_mode not in ("160000", "000000"):
                            files.append({"path": path, "delete": True})  # file replaced by submodule
                            continue
                        if status == "D" or new_mode == "160000":
                            continue
                        if old_mode == "160000":
                            status = "A"
                    if status == "D":
                        files.append({"path": path, "delete": True})
                        continue
                    kind = MODE_KIND.get(new_mode)
                    if kind is None:
                        raise IngestError(f"{sha}: unsupported mode {new_mode} for {path}")
                    files.append({"path": path, "kind": kind, "blob": self._scion_blob(cat, new_sha)})
                try:
                    cs = self.repo.create_changeset(parent_cs, files, info["author"], info["message"],
                                                    info["timestamp"], extra={"git": sha})
                except ValueError as e:
                    raise IngestError(f"{sha}: {e}") from None
                meta.git_map_put(sha, cs)
                self.stats["commits"] += 1
                self.stats["files"] += len(files)
                tip_cs = cs
                if self.verbose and self.stats["commits"] % 500 == 0:
                    print(f"ingested {self.stats['commits']} commits", file=sys.stderr)
                if limit and self.stats["commits"] >= limit:
                    break
        finally:
            proc.stdout.close()
            proc.terminate()
            proc.wait()
            cat.close()
        if target_ref and tip_cs:
            old = self.repo.get_ref(target_ref)
            if old != tip_cs and not self.repo.update_ref(target_ref, old, tip_cs):
                raise IngestError(f"{target_ref} moved concurrently; re-run ingestion")
        self.stats["seconds"] = round(time.time() - t0, 3)
        self.stats["tip"] = tip_cs
        return self.stats

    def verify(self, rev: str = "HEAD") -> dict:
        """Compare the ingested tree of ``rev`` with git's, file by file."""
        sha = self._git("rev-parse", rev).decode().strip()
        cs = self.repo.meta.git_map_get(sha)
        if cs is None:
            raise IngestError(f"{rev} has not been ingested")
        ours = {p: (k, oid) for p, k, oid in self.repo.trees.walk(self.repo.root_tree(cs))}
        theirs = {}
        cat = CatFile(self.git_path)
        try:
            for entry in self._git("ls-tree", "-r", "-z", sha).split(b"\0"):
                if not entry:
                    continue
                meta, path = entry.decode("utf-8", "surrogateescape").split("\t", 1)
                mode, otype, osha = meta.split()
                if otype != "blob":
                    continue
                _, data = cat.read(osha)
                theirs[path] = (MODE_KIND.get(mode, "f"), blob_id(data))
        finally:
            cat.close()
        mismatches = sorted(p for p in set(ours) | set(theirs) if ours.get(p) != theirs.get(p))
        return {"files": len(theirs), "mismatches": mismatches[:50], "ok": not mismatches, "changeset": cs}

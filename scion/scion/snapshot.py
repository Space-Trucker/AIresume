"""Daemon snapshots (FR-TIER-03/11, UC-24).

A snapshot holds every public tree and blob of one revision (usually the tip of main), in the same
framing as the object protocol. Operators publish snapshots to blob storage under
``<snapshots>/<repo>/`` and switch the ``LATEST`` pointer atomically. A daemon imports the objects
it lacks, verifying each one, and fetches anything newer through the cache tier as usual.
Restricted objects are never included (threat I3).
"""
from __future__ import annotations

import json
import os
import struct
import tempfile
import time

from .objects import KIND_DIR, decode_stored
from .storage import ns_key

_FRAME = struct.Struct(">32sBI")


def create_snapshot(repo, rev: str, out_dir: str) -> dict:
    """Write a snapshot of ``rev`` into ``out_dir`` (one repository's directory) and point
    ``LATEST`` at it. Returns the pointer."""
    if not getattr(repo.policy, "public", True):
        raise ValueError(f"repository {repo.name} is private: its objects are never put in snapshots")
    cs = repo.resolve(rev)
    root = repo.root_tree(cs)
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".snap-")
    count, seen = 0, set()
    try:
        with os.fdopen(fd, "wb") as f:
            epoch = repo.acl_epoch()  # daemons import a snapshot only under the same ACL epoch (ADR-20)
            f.write(json.dumps({"repo": repo.name, "cs": cs, "root": root, "created": time.time(),
                                "epoch": epoch}).encode() + b"\n")
            level = [root]
            while level:  # breadth first, so a partial import still holds whole upper levels
                restricted = repo.restricted_objects(level)
                nxt = []
                for tid in level:
                    if tid in seen or tid in restricted:
                        continue
                    seen.add(tid)
                    _write(f, tid, repo.objects.get_stored(tid))
                    count += 1
                    entries = repo.trees.read(tid)
                    blobs = [oid for kind, oid in entries.values() if kind != KIND_DIR and oid not in seen]
                    hidden = repo.restricted_objects(blobs)
                    for kind, oid in entries.values():
                        if kind == KIND_DIR:
                            nxt.append(oid)
                        elif oid not in seen and oid not in hidden:
                            seen.add(oid)
                            _write(f, oid, repo.objects.get_stored(oid))
                            count += 1
                level = nxt
        name = f"snap-{int(time.time() * 1000)}-{cs[:12]}.snap"
        os.replace(tmp, os.path.join(out_dir, name))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    pointer = {"file": name, "cs": cs, "objects": count, "epoch": epoch}
    ptmp = os.path.join(out_dir, ".LATEST.tmp")
    with open(ptmp, "w") as f:
        json.dump(pointer, f)
    os.replace(ptmp, os.path.join(out_dir, "LATEST"))  # atomic switch (FR-TIER-11)
    return pointer


def _write(f, oid: str, stored: bytes) -> None:
    f.write(_FRAME.pack(bytes.fromhex(oid), 0, len(stored)))
    f.write(stored)


def latest_snapshot(repo_snapshot_dir: str) -> dict | None:
    try:
        with open(os.path.join(repo_snapshot_dir, "LATEST")) as f:
            return json.load(f)
    except (FileNotFoundError, NotADirectoryError, json.JSONDecodeError):
        return None


def load_snapshot(path: str, store, repo: str | None, expect_epoch: str | None = None) -> int:
    """Import a snapshot's objects that ``store`` lacks, verifying each (FR-OBJ-04). Returns how
    many were new. With ``expect_epoch``, a snapshot taken under another ACL epoch is refused."""
    imported = 0
    with open(path, "rb") as f:
        header = json.loads(f.readline() or b"{}")
        if repo is not None and header.get("repo") not in (None, repo):
            raise ValueError(f"{path} is a snapshot of {header.get('repo')}, not {repo}")
        if expect_epoch is not None and header.get("epoch") != expect_epoch:
            raise ValueError(f"{path} was taken under another ACL epoch")
        while True:
            head = f.read(_FRAME.size)
            if not head:
                break
            if len(head) < _FRAME.size:
                raise ValueError(f"{path}: truncated snapshot")
            raw, _flags, length = _FRAME.unpack(head)
            stored = f.read(length)
            if len(stored) < length:
                raise ValueError(f"{path}: truncated snapshot")
            oid = raw.hex()
            key = ns_key(repo, oid)
            if not store.has(key):
                decode_stored(stored, expected_id=oid)
                store.put_stored(key, stored, verify=False)
                imported += 1
    return imported

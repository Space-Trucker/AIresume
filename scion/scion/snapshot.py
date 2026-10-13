"""Snapshots: the periodically refreshed starting point for every scion-daemon.

A snapshot holds every public tree and blob reachable from one changeset (usually the tip of
main), written in the same compressed framing the object protocol uses.  It is kept in blob
storage, and a daemon imports whichever objects it does not already have.  The snapshot is only
a warm start: anything newer is fetched through the cache tier as usual.
"""
from __future__ import annotations

import json
import os
import struct
import tempfile
import time

from .objects import KIND_DIR

_HEADER = struct.Struct(">32sBI")


def create_snapshot(repo, rev: str, out_dir: str) -> str:
    cs = repo.resolve(rev)
    root = repo.root_tree(cs)
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".snap-")
    count = 0
    seen: set[str] = set()
    with os.fdopen(fd, "wb") as f:
        header = {"cs": cs, "root": root, "created": time.time()}
        f.write(json.dumps(header).encode() + b"\n")
        stack = [root]
        while stack:
            batch = []
            while stack and len(batch) < 500:
                batch.append(stack.pop())
            restricted = _restricted(repo, batch)
            for tid in batch:
                if tid in restricted or tid in seen:
                    continue
                seen.add(tid)
                _write(f, tid, repo.objects.get_stored(tid))
                count += 1
                entries = repo.trees.read(tid)
                blobs = [oid for _, (k, oid) in entries.items() if k != KIND_DIR and oid not in seen]
                blob_restricted = _restricted(repo, blobs)
                for name, (kind, oid) in entries.items():
                    if kind == KIND_DIR:
                        stack.append(oid)
                    elif oid not in seen and oid not in blob_restricted:
                        seen.add(oid)
                        _write(f, oid, repo.objects.get_stored(oid))
                        count += 1
    name = f"snap-{int(time.time() * 1000)}-{cs[:12]}.snap"
    final = os.path.join(out_dir, name)
    os.replace(tmp, final)
    latest_tmp = os.path.join(out_dir, ".LATEST.tmp")
    with open(latest_tmp, "w") as f:
        json.dump({"file": name, "cs": cs, "objects": count}, f)
    os.replace(latest_tmp, os.path.join(out_dir, "LATEST"))
    return final


def _restricted(repo, ids: list[str]) -> set[str]:
    known = repo.meta.acl_known(ids)
    return {oid for oid in known if "" not in repo.meta.acl_prefixes(oid)}


def _write(f, oid: str, stored: bytes) -> None:
    f.write(_HEADER.pack(bytes.fromhex(oid), 0, len(stored)))
    f.write(stored)


def latest_snapshot(snapshot_dir: str) -> dict | None:
    try:
        with open(os.path.join(snapshot_dir, "LATEST")) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_snapshot(path: str, store, verify: bool = True) -> int:
    """Import objects from a snapshot file into ``store``; return how many were new."""
    imported = 0
    with open(path, "rb") as f:
        f.readline()  # header
        while True:
            head = f.read(_HEADER.size)
            if not head:
                break
            raw, _flags, length = _HEADER.unpack(head)
            stored = f.read(length)
            oid = raw.hex()
            if not store.has(oid):
                store.put_stored(oid, stored, verify=verify)
                imported += 1
    return imported

"""Content-addressed objects.

Every piece of source-control data that is not a changeset is an immutable object identified by
the SHA-256 of its *uncompressed stored form* ``type + b"\\0" + payload``.  On disk and on the wire
the object travels zlib-compressed ("the disk format that the daemon will consume"), so tiers can
pass bytes through without ever recompressing or re-encoding them.

Object types:
  blob   raw file contents
  tree   a directory listing (name, kind, id)
  htree  history tree: a tree whose entries also carry the last changeset that changed them
  stree  search tree: a tree whose directory entries carry a bloom filter of names beneath them
  blame  line attribution for one file version
"""
from __future__ import annotations

import hashlib
import json
import zlib
from typing import Iterable

KIND_FILE = "f"
KIND_EXEC = "x"
KIND_LINK = "l"
KIND_DIR = "d"
FILE_KINDS = (KIND_FILE, KIND_EXEC, KIND_LINK)

ID_HEX_LEN = 64


class ObjectError(Exception):
    pass


def object_id(otype: str, payload: bytes) -> str:
    h = hashlib.sha256()
    h.update(otype.encode())
    h.update(b"\0")
    h.update(payload)
    return h.hexdigest()


def encode_stored(otype: str, payload: bytes, level: int = 6) -> bytes:
    """Return the compressed on-disk/on-wire representation."""
    return zlib.compress(otype.encode() + b"\0" + payload, level)


def decode_stored(stored: bytes, expected_id: str | None = None) -> tuple[str, bytes]:
    raw = zlib.decompress(stored)
    if expected_id is not None:
        actual = hashlib.sha256(raw).hexdigest()
        if actual != expected_id:
            raise ObjectError(f"object integrity failure: wanted {expected_id}, got {actual}")
    nul = raw.index(b"\0")
    return raw[:nul].decode(), raw[nul + 1:]


def blob_id(data: bytes) -> str:
    return object_id("blob", data)


def is_object_id(s: str) -> bool:
    if len(s) != ID_HEX_LEN:
        return False
    try:
        int(s, 16)
    except ValueError:
        return False
    return True


# ---------------------------------------------------------------------------------------------
# Trees
# ---------------------------------------------------------------------------------------------
# A tree entry is (name, kind, id).  Trees are encoded as one line per entry, sorted by name:
#     "<kind> <id> <name>\n"
# Names may not contain "/" or "\n" or "\0", which keeps the encoding canonical.

TreeEntries = dict[str, tuple[str, str]]  # name -> (kind, id)


def validate_name(name: str) -> None:
    if not name or name in (".", "..") or "/" in name or "\n" in name or "\0" in name:
        raise ObjectError(f"invalid path component: {name!r}")


def encode_tree(entries: TreeEntries) -> bytes:
    out = []
    for name in sorted(entries):
        kind, oid = entries[name]
        out.append(f"{kind} {oid} {name}\n")
    return "".join(out).encode()


def decode_tree(payload: bytes) -> TreeEntries:
    entries: TreeEntries = {}
    for line in payload.decode().splitlines():
        kind, oid, name = line.split(" ", 2)
        entries[name] = (kind, oid)
    return entries


EMPTY_TREE_PAYLOAD = b""
EMPTY_TREE_ID = object_id("tree", EMPTY_TREE_PAYLOAD)


# ---------------------------------------------------------------------------------------------
# History trees (path history derived data)
# ---------------------------------------------------------------------------------------------
# An htree entry is (name, kind, content_id, last_changeset, child_htree_or_empty).
# For files content_id is the blob id; for directories content_id is the plain tree id and
# child_htree is the id of the nested htree.

HTreeEntries = dict[str, tuple[str, str, str, str]]  # name -> (kind, content_id, last_cs, child)


def encode_htree(entries: HTreeEntries) -> bytes:
    rows = [[name, *entries[name]] for name in sorted(entries)]
    return json.dumps(rows, separators=(",", ":")).encode()


def decode_htree(payload: bytes) -> HTreeEntries:
    return {r[0]: (r[1], r[2], r[3], r[4]) for r in json.loads(payload)}


# ---------------------------------------------------------------------------------------------
# Path utilities
# ---------------------------------------------------------------------------------------------

def normalize_path(path: str) -> str:
    path = path.strip("/")
    if not path:
        return ""
    parts = path.split("/")
    for p in parts:
        validate_name(p)
    return "/".join(parts)


def split_path(path: str) -> list[str]:
    path = normalize_path(path)
    return path.split("/") if path else []


def parent_dirs(path: str) -> Iterable[str]:
    """Yield every ancestor directory of ``path`` (excluding the root), shallowest first."""
    parts = split_path(path)
    for i in range(1, len(parts)):
        yield "/".join(parts[:i])


def is_binary(data: bytes) -> bool:
    return b"\0" in data[:8000]

"""Content-addressed objects (FR-OBJ-01, FR-OBJ-04, FR-CS-03; 07 §7.6).

An object's id is ``sha256(type || 0x00 || payload)``. It is stored and sent as
``zlib(type || 0x00 || payload)``, so every tier passes bytes through unchanged (FR-FP-06).

Object types: ``blob`` (file bytes), ``tree`` (directory listing), and the internal types used by
derived data: ``htree`` (history tree), ``stree`` (search tree), ``blame``.
"""
from __future__ import annotations

import hashlib
import json
import re
import zlib

KIND_FILE, KIND_EXEC, KIND_LINK, KIND_DIR = "f", "x", "l", "d"
FILE_KINDS = (KIND_FILE, KIND_EXEC, KIND_LINK)
PUBLIC_TYPES = ("blob", "tree")  # derived internals are never served to clients (FR-DD-04)


# Object protocol flags (07 §7.7): restricted objects are never cached by shared tiers.
F_RESTRICTED, F_MISSING, F_DENIED = 0x1, 0x2, 0x4


class ObjectError(Exception):
    """An object failed integrity verification or is malformed."""


class ObjectTooLarge(ObjectError):
    """An uploaded object exceeds the configured per-file limit (FR-WR-07)."""


def object_id(otype: str, payload: bytes) -> str:
    return hashlib.sha256(otype.encode() + b"\0" + payload).hexdigest()


def blob_id(data: bytes) -> str:
    return object_id("blob", data)


def encode_stored(otype: str, payload: bytes) -> bytes:
    """zlib, tuned per type (ADR-21): level 6 for file contents; level 1 for trees and the other
    derived nodes, which are mostly hashes and are rewritten on every commit (NFR-05); and Huffman
    coding alone for search trees, whose bloom filters LZ77 can't shorten but whose hex digits
    Huffman coding halves at the same speed however full the filters are. Every form is ordinary
    zlib, and the id covers the uncompressed bytes, so none of this changes an object's identity."""
    raw = otype.encode() + b"\0" + payload
    if otype == "stree":
        z = zlib.compressobj(1, zlib.DEFLATED, 15, 9, zlib.Z_HUFFMAN_ONLY)
        return z.compress(raw) + z.flush()
    return zlib.compress(raw, 6 if otype == "blob" else 1)


def decode_stored(stored: bytes, expected_id: str | None = None) -> tuple[str, bytes]:
    """Decompress; with ``expected_id``, verify the content hash (FR-OBJ-04)."""
    try:
        raw = zlib.decompress(stored)
    except zlib.error as e:
        raise ObjectError(f"corrupt object: {e}") from None
    if expected_id is not None and hashlib.sha256(raw).hexdigest() != expected_id:
        raise ObjectError(f"integrity failure for {expected_id[:12]}")
    nul = raw.find(b"\0")
    if nul < 0:
        raise ObjectError("malformed object")
    return raw[:nul].decode(), raw[nul + 1:]


def decode_limited(stored: bytes, expected_id: str, max_payload: int | None) -> tuple[str, bytes]:
    """``decode_stored`` for untrusted uploads: decompression stops once the payload passes
    ``max_payload``, so a small compressed upload cannot expand without bound (threat D3)."""
    if max_payload is None:
        return decode_stored(stored, expected_id)
    d = zlib.decompressobj()
    try:
        raw = d.decompress(stored, max_payload + 64)
    except zlib.error as e:
        raise ObjectError(f"corrupt object: {e}") from None
    nul = raw.find(b"\0")
    if d.unconsumed_tail or (nul >= 0 and len(raw) - nul - 1 > max_payload):
        raise ObjectTooLarge(f"object {expected_id[:12]} is larger than the {max_payload}-byte limit")
    return decode_stored(stored, expected_id)


def stored_type(stored: bytes) -> str:
    head = zlib.decompressobj().decompress(stored, 16)
    return head.split(b"\0", 1)[0].decode(errors="replace")


def is_object_id(s: str) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)


# -- trees: one line per entry "<kind> <id> <name>\n", sorted by name -------------------------
def validate_name(name: str) -> None:
    if not name or name in (".", "..") or any(c in name for c in "/\n\0"):
        raise ObjectError(f"invalid path component {name!r}")


# Repository names are path components and cache-key prefixes (ADR-13). Three or more characters
# keep them apart from the two-character fan-out directories of object stores.
REPO_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{2,62}$")


def validate_repo_name(name) -> str:
    if not isinstance(name, str) or not REPO_NAME.match(name) or ".." in name:
        raise ValueError(f"invalid repository name {name!r}: use 3-63 of a-z 0-9 . _ -")
    return name


def encode_tree(entries: dict[str, tuple[str, str]]) -> bytes:
    return "".join(f"{entries[n][0]} {entries[n][1]} {n}\n" for n in sorted(entries)).encode()


def decode_tree(payload: bytes) -> dict[str, tuple[str, str]]:
    out = {}
    for line in payload.decode().splitlines():
        kind, oid, name = line.split(" ", 2)
        out[name] = (kind, oid)
    return out


EMPTY_TREE_ID = object_id("tree", b"")


# -- history trees: rows [name, kind, content_id, last_changeset, child_htree] ---------------
def encode_htree(entries: dict) -> bytes:
    return json.dumps([[n, *entries[n]] for n in sorted(entries)], separators=(",", ":")).encode()


def decode_htree(payload: bytes) -> dict:
    return {r[0]: tuple(r[1:]) for r in json.loads(payload)}


# -- paths --------------------------------------------------------------------------------------
def normalize_path(path: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p] if path else []
    for p in parts:
        validate_name(p)
    return "/".join(parts)


def split_path(path: str) -> list[str]:
    p = normalize_path(path)
    return p.split("/") if p else []


def join(prefix: str, name: str) -> str:
    return f"{prefix}/{name}" if prefix else name


def is_binary(data: bytes) -> bool:
    return b"\0" in data[:8000]

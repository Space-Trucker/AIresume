"""Changesets: the unit of work (FR-CS-02/03/04; domain model 06 §6.1).

A changeset is an entry in the write-ahead log. It records parents, author, message and time, and
the files changed **relative to its first parent** (merges included, footnote 1), each with a
content-addressed pointer to its compressed contents. It does not point at a root tree: trees and
every other index are derived data (FR-DD-01). Its id is the hash of its canonical encoding, so
creating the same changeset twice yields the same id (FR-CS-04).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from .objects import FILE_KINDS, normalize_path

OP_ADD, OP_MODIFY, OP_DELETE = "A", "M", "D"


@dataclass(frozen=True)
class FileChange:
    path: str
    op: str                  # A, M or D
    kind: str | None = None  # f, x or l; None for a deletion
    blob: str | None = None  # content id; None for a deletion

    def validate(self) -> None:
        if not self.path or normalize_path(self.path) != self.path:
            raise ValueError(f"invalid path {self.path!r}")
        if self.op == OP_DELETE:
            if self.kind is not None or self.blob is not None:
                raise ValueError("a deletion carries no content")
        elif self.op in (OP_ADD, OP_MODIFY):
            if self.kind not in FILE_KINDS or not self.blob:
                raise ValueError(f"bad change for {self.path}")
        else:
            raise ValueError(f"bad op {self.op!r}")


@dataclass(frozen=True)
class Changeset:
    parents: tuple[str, ...]
    author: str
    message: str
    timestamp: int
    changes: tuple[FileChange, ...]
    extra: dict = field(default_factory=dict, compare=False, hash=False)

    def encode(self) -> bytes:
        return json.dumps({
            "parents": list(self.parents), "author": self.author, "message": self.message,
            "timestamp": self.timestamp, "extra": self.extra,
            "changes": [[c.path, c.op, c.kind, c.blob] for c in self.changes],
        }, sort_keys=True, separators=(",", ":")).encode()

    @staticmethod
    def decode(data: bytes) -> "Changeset":
        d = json.loads(data)
        return Changeset(tuple(d["parents"]), d["author"], d["message"], d["timestamp"],
                         tuple(FileChange(*r) for r in d["changes"]), d.get("extra") or {})

    @property
    def id(self) -> str:
        return hashlib.sha256(b"changeset\0" + self.encode()).hexdigest()

    @property
    def first_parent(self) -> str | None:
        return self.parents[0] if self.parents else None

    def summary(self) -> str:
        return self.message.splitlines()[0] if self.message else ""

    def to_api(self, cs_id: str | None = None) -> dict:
        return {
            "id": cs_id or self.id, "parents": list(self.parents), "author": self.author,
            "message": self.message, "timestamp": self.timestamp, "extra": self.extra,
            "changes": [{"path": c.path, "op": c.op, "kind": c.kind, "blob": c.blob} for c in self.changes],
        }

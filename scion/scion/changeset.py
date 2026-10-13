"""Changesets: the unit of work.

A changeset is an entry in a write-ahead log.  It records what you would expect from a git commit
(parents, author, message, time) but, instead of a pointer to a root tree, it stores the list of
files that changed **relative to its first parent** together with content-addressed pointers to
the compressed contents in blob storage.  Everything else (trees, history, blame, the commit-graph
index, ...) is *derived data*.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from .objects import FILE_KINDS, normalize_path

OP_ADD = "A"
OP_MODIFY = "M"
OP_DELETE = "D"


@dataclass(frozen=True)
class FileChange:
    path: str
    op: str                   # A, M or D
    kind: str | None = None   # f, x or l (None for deletions)
    blob: str | None = None   # content id (None for deletions)

    def to_json(self) -> list:
        return [self.path, self.op, self.kind, self.blob]

    @staticmethod
    def from_json(row: list) -> "FileChange":
        return FileChange(row[0], row[1], row[2], row[3])

    def validate(self) -> None:
        if normalize_path(self.path) != self.path or not self.path:
            raise ValueError(f"invalid path {self.path!r}")
        if self.op == OP_DELETE:
            if self.kind is not None or self.blob is not None:
                raise ValueError("deletions carry no content")
        elif self.op in (OP_ADD, OP_MODIFY):
            if self.kind not in FILE_KINDS or not self.blob:
                raise ValueError(f"bad file change for {self.path}")
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
        return json.dumps(
            {
                "parents": list(self.parents),
                "author": self.author,
                "message": self.message,
                "timestamp": self.timestamp,
                "changes": [c.to_json() for c in self.changes],
                "extra": self.extra,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

    @staticmethod
    def decode(data: bytes) -> "Changeset":
        d = json.loads(data)
        return Changeset(
            parents=tuple(d["parents"]),
            author=d["author"],
            message=d["message"],
            timestamp=d["timestamp"],
            changes=tuple(FileChange.from_json(r) for r in d["changes"]),
            extra=d.get("extra") or {},
        )

    @property
    def id(self) -> str:
        return hashlib.sha256(b"changeset\0" + self.encode()).hexdigest()

    @property
    def first_parent(self) -> str | None:
        return self.parents[0] if self.parents else None

    def change_map(self) -> dict[str, FileChange]:
        return {c.path: c for c in self.changes}

    def summary(self) -> str:
        return self.message.splitlines()[0] if self.message else ""

    def to_api(self, cs_id: str | None = None) -> dict:
        return {
            "id": cs_id or self.id,
            "parents": list(self.parents),
            "author": self.author,
            "message": self.message,
            "timestamp": self.timestamp,
            "changes": [
                {"path": c.path, "op": c.op, "kind": c.kind, "blob": c.blob} for c in self.changes
            ],
            "extra": self.extra,
        }

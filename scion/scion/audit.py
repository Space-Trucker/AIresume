"""The audit log (FR-IAM-10, ADR-15).

An append-only, hash-chained log per repository of access-relevant events: policy loads, denials,
ref moves and administrative actions (force-lands, releases, re-indexing, backups). Each entry's
hash covers its content and the previous entry's hash, so changing or removing an entry in the
middle of the history is detected by ``verify()``. Appends from several servers are serialized by the
metadata store (a write lock on SQLite, a read-write transaction on Spanner), which keeps the chain
linear.
"""
from __future__ import annotations

import hashlib
import json
import time

from .meta import AUDIT_FIELDS as FIELDS

GENESIS = "0" * 64


def _digest(seq: int, at: float, actor, action: str, target: str, detail: str, prev: str) -> str:
    body = json.dumps([seq, at, actor, action, target, detail, prev], separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()


class AuditLog:
    def __init__(self, meta):
        self.meta = meta

    def append(self, action: str, actor: str | None, target: str = "", detail: dict | None = None) -> dict:
        detail_s = json.dumps(detail or {}, sort_keys=True, separators=(",", ":"))

        def make(seq: int, last: str | None) -> tuple:
            prev, at = last or GENESIS, time.time()
            return at, actor, action, target, detail_s, prev, _digest(seq, at, actor, action, target, detail_s, prev)

        seq, h = self.meta.audit_append(make)
        return {"seq": seq, "hash": h}

    def entries(self, limit: int = 100, action: str | None = None, before: int | None = None) -> list[dict]:
        """Newest first."""
        out = []
        for row in self.meta.audit_entries(limit, action, before):
            d = dict(zip(FIELDS, row))
            d["detail"] = json.loads(d["detail"])
            out.append(d)
        return out

    def last(self, action: str) -> dict | None:
        rows = self.entries(1, action)
        return rows[0] if rows else None

    def verify(self) -> dict:
        """Recompute the chain: ``{"ok", "entries", "first_bad", "head"}``."""
        prev, n = GENESIS, 0
        for seq, at, actor, action, target, detail, p, h in self.meta.audit_iter():
            n += 1
            if seq != n or p != prev or _digest(seq, at, actor, action, target, detail, p) != h:
                return {"ok": False, "entries": n, "first_bad": seq, "head": prev}
            prev = h
        return {"ok": True, "entries": n, "first_bad": None, "head": prev}

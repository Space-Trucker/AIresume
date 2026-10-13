"""The audit log (FR-IAM-10, ADR-15).

An append-only, hash-chained log per repository of access-relevant events: policy loads, denials,
ref moves and administrative actions (force-lands, releases, re-indexing, backups). Each entry's
hash covers its content and the previous entry's hash, so changing or removing an entry in the
middle of the history is detected by ``verify()``. Appends from several servers are serialized by the
metadata store's write lock, which keeps the chain linear.
"""
from __future__ import annotations

import hashlib
import json
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit (
    seq    INTEGER PRIMARY KEY,
    at     REAL NOT NULL,
    actor  TEXT,
    action TEXT NOT NULL,
    target TEXT NOT NULL,
    detail TEXT NOT NULL,
    prev   TEXT NOT NULL,
    hash   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS audit_action ON audit(action, seq);
"""
GENESIS = "0" * 64
FIELDS = ("seq", "at", "actor", "action", "target", "detail", "prev", "hash")


def _digest(seq: int, at: float, actor, action: str, target: str, detail: str, prev: str) -> str:
    body = json.dumps([seq, at, actor, action, target, detail, prev], separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()


class AuditLog:
    def __init__(self, meta):
        self.meta = meta
        meta.ensure(SCHEMA)

    def append(self, action: str, actor: str | None, target: str = "", detail: dict | None = None) -> dict:
        detail_s = json.dumps(detail or {}, sort_keys=True, separators=(",", ":"))
        with self.meta.transaction() as c:  # BEGIN IMMEDIATE: one appender at a time
            last = c.execute("SELECT seq, hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
            seq, prev = (last[0] + 1, last[1]) if last else (1, GENESIS)
            at = time.time()
            h = _digest(seq, at, actor, action, target, detail_s, prev)
            c.execute("INSERT INTO audit (seq, at, actor, action, target, detail, prev, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (seq, at, actor, action, target, detail_s, prev, h))
        return {"seq": seq, "hash": h}

    def entries(self, limit: int = 100, action: str | None = None, before: int | None = None) -> list[dict]:
        """Newest first."""
        q, args = "SELECT seq, at, actor, action, target, detail, prev, hash FROM audit WHERE 1 = 1", []
        if action:
            q += " AND action = ?"
            args.append(action)
        if before:
            q += " AND seq < ?"
            args.append(int(before))
        q += " ORDER BY seq DESC LIMIT ?"
        args.append(int(limit))
        out = []
        for row in self.meta.execute(q, args):
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
        for seq, at, actor, action, target, detail, p, h in self.meta.execute(
                "SELECT seq, at, actor, action, target, detail, prev, hash FROM audit ORDER BY seq"):
            n += 1
            if seq != n or p != prev or _digest(seq, at, actor, action, target, detail, p) != h:
                return {"ok": False, "entries": n, "first_bad": seq, "head": prev}
            prev = h
        return {"ok": True, "entries": n, "first_bad": None, "head": prev}

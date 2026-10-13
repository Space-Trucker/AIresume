"""Metadata store: the stand-in for Spanner.

It holds the changeset write-ahead log, refs (each one a single row moved by compare-and-swap),
derived-data values, and a few indexes.  SQLite in WAL mode lets several ``scion-server``
processes share one store on one machine.  Every method is a small single-row or single-key
operation, which is the access pattern that would map onto a distributed database.
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from typing import Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS changesets (
    seq     INTEGER PRIMARY KEY AUTOINCREMENT,
    id      TEXT UNIQUE NOT NULL,
    data    BLOB NOT NULL,
    created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS refs (
    name    TEXT PRIMARY KEY,
    target  TEXT NOT NULL,
    version INTEGER NOT NULL,
    updated REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS ref_log (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    old   TEXT,
    new   TEXT,
    who   TEXT,
    at    REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS derived (
    type  TEXT NOT NULL,
    cs    TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (type, cs)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS blob_index (
    blob TEXT NOT NULL,
    path TEXT NOT NULL,
    PRIMARY KEY (blob, path)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS object_acl (
    object TEXT NOT NULL,
    prefix TEXT NOT NULL,
    PRIMARY KEY (object, prefix)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS git_map (
    git TEXT PRIMARY KEY,
    cs  TEXT NOT NULL
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS kv (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
) WITHOUT ROWID;
"""


class MetaStore:
    def __init__(self, path: str):
        self.path = path
        d = os.path.dirname(os.path.abspath(path))
        os.makedirs(d, exist_ok=True)
        self._local = threading.local()
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.path, isolation_level=None, timeout=60)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=60000")
            self._local.conn = conn
        return conn

    def close(self) -> None:
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    def execute(self, sql: str, args: Iterable = ()) -> sqlite3.Cursor:
        return self._conn().execute(sql, tuple(args))

    # -- changeset log ------------------------------------------------------------------------
    def insert_changeset(self, cs_id: str, data: bytes) -> bool:
        cur = self.execute(
            "INSERT OR IGNORE INTO changesets (id, data, created) VALUES (?, ?, ?)",
            (cs_id, data, time.time()),
        )
        return cur.rowcount == 1

    def get_changeset_data(self, cs_id: str) -> bytes | None:
        row = self.execute("SELECT data FROM changesets WHERE id = ?", (cs_id,)).fetchone()
        return row[0] if row else None

    def has_changeset(self, cs_id: str) -> bool:
        return self.execute("SELECT 1 FROM changesets WHERE id = ?", (cs_id,)).fetchone() is not None

    def changeset_seq(self, cs_id: str) -> int | None:
        row = self.execute("SELECT seq FROM changesets WHERE id = ?", (cs_id,)).fetchone()
        return row[0] if row else None

    def resolve_prefix(self, prefix: str, limit: int = 2) -> list[str]:
        prefix = prefix.lower()
        rows = self.execute(
            "SELECT id FROM changesets WHERE id >= ? AND id < ? LIMIT ?",
            (prefix, prefix + "g", limit),
        ).fetchall()
        return [r[0] for r in rows]

    def count_changesets(self) -> int:
        return self.execute("SELECT COUNT(*) FROM changesets").fetchone()[0]

    def tail(self, after_seq: int = 0, limit: int = 1000) -> list[tuple[int, str]]:
        return self.execute(
            "SELECT seq, id FROM changesets WHERE seq > ? ORDER BY seq LIMIT ?", (after_seq, limit)
        ).fetchall()

    # -- refs ----------------------------------------------------------------------------------
    def get_ref(self, name: str) -> tuple[str, int] | None:
        row = self.execute("SELECT target, version FROM refs WHERE name = ?", (name,)).fetchone()
        return (row[0], row[1]) if row else None

    def list_refs(self) -> list[tuple[str, str, int]]:
        return self.execute("SELECT name, target, version FROM refs ORDER BY name").fetchall()

    def cas_ref(self, name: str, expected: str | None, new: str | None, who: str = "") -> bool:
        """Compare-and-swap a single ref row.  ``expected=None`` means "must not exist";
        ``new=None`` deletes."""
        now = time.time()
        if expected is None and new is None:
            return self.get_ref(name) is None
        if expected is None:
            cur = self.execute(
                "INSERT INTO refs (name, target, version, updated) VALUES (?, ?, 1, ?) "
                "ON CONFLICT(name) DO NOTHING",
                (name, new, now),
            )
        elif new is None:
            cur = self.execute("DELETE FROM refs WHERE name = ? AND target = ?", (name, expected))
        else:
            cur = self.execute(
                "UPDATE refs SET target = ?, version = version + 1, updated = ? "
                "WHERE name = ? AND target = ?",
                (new, now, name, expected),
            )
        ok = cur.rowcount == 1
        if ok:
            self.execute(
                "INSERT INTO ref_log (name, old, new, who, at) VALUES (?, ?, ?, ?, ?)",
                (name, expected, new, who, now),
            )
        return ok

    def ref_log(self, name: str, limit: int = 50) -> list[tuple]:
        return self.execute(
            "SELECT old, new, who, at FROM ref_log WHERE name = ? ORDER BY id DESC LIMIT ?",
            (name, limit),
        ).fetchall()

    # -- derived data --------------------------------------------------------------------------
    def derived_get(self, dtype: str, cs_id: str) -> str | None:
        row = self.execute(
            "SELECT value FROM derived WHERE type = ? AND cs = ?", (dtype, cs_id)
        ).fetchone()
        return row[0] if row else None

    def derived_put(self, dtype: str, cs_id: str, value: str) -> None:
        # Derived values are deterministic, so two servers racing to compute the same value
        # need no coordination: whoever writes first wins and both values are identical.
        self.execute(
            "INSERT OR IGNORE INTO derived (type, cs, value) VALUES (?, ?, ?)", (dtype, cs_id, value)
        )

    def derived_count(self, dtype: str) -> int:
        return self.execute("SELECT COUNT(*) FROM derived WHERE type = ?", (dtype,)).fetchone()[0]

    # -- copy-detection index ---------------------------------------------------------------
    def blob_index_add(self, rows: Iterable[tuple[str, str]]) -> None:
        self._conn().executemany(
            "INSERT OR IGNORE INTO blob_index (blob, path) VALUES (?, ?)", list(rows)
        )

    def blob_index_paths(self, blob: str, limit: int = 20) -> list[str]:
        return [
            r[0]
            for r in self.execute(
                "SELECT path FROM blob_index WHERE blob = ? LIMIT ?", (blob, limit)
            ).fetchall()
        ]

    # -- object ACL index ----------------------------------------------------------------------
    def acl_add(self, rows: Iterable[tuple[str, str]]) -> None:
        self._conn().executemany(
            "INSERT OR IGNORE INTO object_acl (object, prefix) VALUES (?, ?)", list(rows)
        )

    def acl_prefixes(self, oid: str) -> list[str]:
        return [
            r[0]
            for r in self.execute("SELECT prefix FROM object_acl WHERE object = ?", (oid,)).fetchall()
        ]

    def acl_known(self, oids: list[str]) -> set[str]:
        out: set[str] = set()
        for i in range(0, len(oids), 500):
            chunk = oids[i:i + 500]
            q = "SELECT DISTINCT object FROM object_acl WHERE object IN (%s)" % ",".join("?" * len(chunk))
            out.update(r[0] for r in self.execute(q, chunk).fetchall())
        return out

    # -- git ingestion map -------------------------------------------------------------------
    def git_map_get(self, sha: str) -> str | None:
        row = self.execute("SELECT cs FROM git_map WHERE git = ?", (sha,)).fetchone()
        return row[0] if row else None

    def git_map_put(self, sha: str, cs_id: str) -> None:
        self.execute("INSERT OR IGNORE INTO git_map (git, cs) VALUES (?, ?)", (sha, cs_id))

    # -- misc ----------------------------------------------------------------------------------
    def kv_get(self, key: str) -> str | None:
        row = self.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def kv_set(self, key: str, value: str) -> None:
        self.execute(
            "INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

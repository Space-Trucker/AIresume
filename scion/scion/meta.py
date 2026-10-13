"""Metadata store: the Spanner stand-in (CON-02, ADR-10; ER diagram 06 §6.9).

Holds the changeset write-ahead log (FR-CS-05), refs moved only by compare-and-swap (FR-REF-02)
with their log (FR-REF-04), derived-data values (FR-DD-05) and small indexes. Every operation is a
single-row or single-key access, the pattern that maps onto a distributed database. SQLite in WAL
mode lets several server processes on one host share a store. Other modules add their tables with
``ensure()``.
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from contextlib import contextmanager
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
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    old  TEXT,
    new  TEXT,
    who  TEXT,
    at   REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_log_by_name ON ref_log(name, id);
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
CREATE TABLE IF NOT EXISTS kv (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS object_acl (
    oid    TEXT NOT NULL,
    prefix TEXT NOT NULL,
    PRIMARY KEY (oid, prefix)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS content_blobs (
    blob   TEXT PRIMARY KEY,
    status TEXT NOT NULL
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS content_trigrams (
    trigram TEXT NOT NULL,
    blob    TEXT NOT NULL,
    PRIMARY KEY (trigram, blob)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS object_grants (
    oid  TEXT NOT NULL,
    user TEXT NOT NULL,
    at   REAL NOT NULL,
    PRIMARY KEY (oid, user)
) WITHOUT ROWID;
"""
GRANT_SECONDS = 24 * 3600


class MetaStore:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self._local = threading.local()
        self._lock = threading.Lock()
        self._conns: list[tuple[threading.Thread, sqlite3.Connection]] = []
        self._gen = 0
        self.ensure(SCHEMA)

    # -- connections ------------------------------------------------------------------------------
    def conn(self) -> sqlite3.Connection:
        """This thread's connection. Connections of finished threads are closed as new ones open."""
        st = getattr(self._local, "st", None)
        if st is not None and st[0] == self._gen:
            return st[1]
        c = sqlite3.connect(self.path, isolation_level=None, timeout=60, check_same_thread=False)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=NORMAL")
        c.execute("PRAGMA busy_timeout=60000")
        with self._lock:
            live = []
            for t, old in self._conns:
                if t.is_alive():
                    live.append((t, old))
                else:
                    old.close()
            live.append((threading.current_thread(), c))
            self._conns = live
            self._local.st = (self._gen, c)
        return c

    def close(self) -> None:
        """Close every thread's connection; later calls reconnect."""
        with self._lock:
            self._gen += 1
            conns, self._conns = self._conns, []
        for _, c in conns:
            try:
                c.close()
            except sqlite3.Error:
                pass

    def ensure(self, schema_sql: str) -> None:
        self.conn().executescript(schema_sql)

    def execute(self, sql: str, args: Iterable = ()) -> sqlite3.Cursor:
        return self.conn().execute(sql, tuple(args))

    def executemany(self, sql: str, rows) -> None:
        self.conn().executemany(sql, list(rows))

    @contextmanager
    def transaction(self):
        """An atomic multi-statement unit (BEGIN IMMEDIATE takes the write lock up front)."""
        c = self.conn()
        c.execute("BEGIN IMMEDIATE")
        try:
            yield c
        except BaseException:
            c.execute("ROLLBACK")
            raise
        c.execute("COMMIT")

    # -- changeset log (FR-CS-04/05/06) --------------------------------------------------------
    def insert_changeset(self, cs_id: str, data: bytes) -> bool:
        cur = self.execute("INSERT OR IGNORE INTO changesets (id, data, created) VALUES (?, ?, ?)",
                           (cs_id, data, time.time()))
        return cur.rowcount == 1

    def get_changeset_data(self, cs_id: str) -> bytes | None:
        row = self.execute("SELECT data FROM changesets WHERE id = ?", (cs_id,)).fetchone()
        return row[0] if row else None

    def has_changeset(self, cs_id: str) -> bool:
        return self.execute("SELECT 1 FROM changesets WHERE id = ?", (cs_id,)).fetchone() is not None

    def resolve_prefix(self, prefix: str, limit: int = 2) -> list[str]:
        p = prefix.lower()
        return [r[0] for r in self.execute(
            "SELECT id FROM changesets WHERE id >= ? AND id < ? ORDER BY id LIMIT ?", (p, p + "g", limit))]

    def count_changesets(self) -> int:
        return self.execute("SELECT COUNT(*) FROM changesets").fetchone()[0]

    def tail(self, after_seq: int = 0, limit: int = 1000) -> list[tuple[int, str]]:
        return self.execute("SELECT seq, id FROM changesets WHERE seq > ? ORDER BY seq LIMIT ?",
                            (after_seq, limit)).fetchall()

    # -- refs (FR-REF-02/04) ---------------------------------------------------------------------
    def get_ref(self, name: str) -> tuple[str, int] | None:
        row = self.execute("SELECT target, version FROM refs WHERE name = ?", (name,)).fetchone()
        return (row[0], row[1]) if row else None

    def list_refs(self) -> list[tuple[str, str, int]]:
        return self.execute("SELECT name, target, version FROM refs ORDER BY name").fetchall()

    def cas_ref(self, name: str, expected: str | None, new: str | None, who: str = "") -> bool:
        """Compare-and-swap one ref row and log it, atomically. ``expected=None``: the ref must not
        exist. ``new=None``: delete it."""
        if expected is None and new is None:
            return self.get_ref(name) is None
        now = time.time()
        with self.transaction() as c:
            if expected is None:
                cur = c.execute("INSERT INTO refs (name, target, version, updated) VALUES (?, ?, 1, ?) "
                                "ON CONFLICT(name) DO NOTHING", (name, new, now))
            elif new is None:
                cur = c.execute("DELETE FROM refs WHERE name = ? AND target = ?", (name, expected))
            else:
                cur = c.execute("UPDATE refs SET target = ?, version = version + 1, updated = ? "
                                "WHERE name = ? AND target = ?", (new, now, name, expected))
            ok = cur.rowcount == 1
            if ok:
                c.execute("INSERT INTO ref_log (name, old, new, who, at) VALUES (?, ?, ?, ?, ?)",
                          (name, expected, new, who, now))
        return ok

    def ref_log(self, name: str, limit: int = 100) -> list[tuple]:
        """Newest first: (old, new, who, at)."""
        return self.execute("SELECT old, new, who, at FROM ref_log WHERE name = ? ORDER BY id DESC LIMIT ?",
                            (name, limit)).fetchall()

    # -- derived data (FR-DD-05) -----------------------------------------------------------------
    def derived_get(self, dtype: str, cs_id: str) -> str | None:
        row = self.execute("SELECT value FROM derived WHERE type = ? AND cs = ?", (dtype, cs_id)).fetchone()
        return row[0] if row else None

    def derived_put(self, dtype: str, cs_id: str, value: str) -> None:
        # Values are deterministic: whichever server writes first wins, and both are identical.
        self.execute("INSERT OR IGNORE INTO derived (type, cs, value) VALUES (?, ?, ?)", (dtype, cs_id, value))

    def derived_count(self, dtype: str) -> int:
        return self.execute("SELECT COUNT(*) FROM derived WHERE type = ?", (dtype,)).fetchone()[0]

    # -- copy-detection index (FR-DD-11) ------------------------------------------------------
    def blob_index_add(self, rows) -> None:
        self.executemany("INSERT OR IGNORE INTO blob_index (blob, path) VALUES (?, ?)", rows)

    # -- content index (FR-SR-03, ADR-16) -------------------------------------------------------------
    def content_status(self, blob: str) -> str | None:
        row = self.execute("SELECT status FROM content_blobs WHERE blob = ?", (blob,)).fetchone()
        return row[0] if row else None

    def content_add(self, blob: str, status: str, grams) -> None:
        with self.transaction() as c:
            c.executemany("INSERT OR IGNORE INTO content_trigrams (trigram, blob) VALUES (?, ?)",
                          ((g, blob) for g in grams))
            c.execute("INSERT OR IGNORE INTO content_blobs (blob, status) VALUES (?, ?)", (blob, status))

    def content_count(self, gram: str) -> int:
        return self.execute("SELECT COUNT(*) FROM content_trigrams WHERE trigram = ?", (gram,)).fetchone()[0]

    def content_postings(self, gram: str) -> set[str]:
        return {r[0] for r in self.execute("SELECT blob FROM content_trigrams WHERE trigram = ?", (gram,))}

    def content_unindexed(self) -> list[str]:
        """Text blobs too large to index: content search always reads them."""
        return [r[0] for r in self.execute("SELECT blob FROM content_blobs WHERE status = 'l'")]

    def blob_index_paths(self, blob: str, limit: int = 50) -> list[str]:
        return [r[0] for r in self.execute("SELECT path FROM blob_index WHERE blob = ? ORDER BY path LIMIT ?",
                                           (blob, limit))]

    # -- object ACL index (FR-IAM-04/05/09/11) --------------------------------------------------------
    # One row per (object, directory that restricts a place it appears); "" marks a place everyone
    # may read, which makes the object public (FR-IAM-11).
    def acl_add(self, rows) -> None:
        self.executemany("INSERT OR IGNORE INTO object_acl (oid, prefix) VALUES (?, ?)", rows)

    def acl_get(self, ids) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        ids = list(dict.fromkeys(ids))
        for i in range(0, len(ids), 500):
            chunk = ids[i:i + 500]
            q = f"SELECT oid, prefix FROM object_acl WHERE oid IN ({','.join('?' * len(chunk))})"
            for oid, prefix in self.execute(q, chunk):
                out.setdefault(oid, set()).add(prefix)
        return out

    def grant_add(self, oid: str, user: str) -> None:
        """Record that ``user`` uploaded the exact bytes of an object they may not otherwise read."""
        now = time.time()
        self.execute("INSERT OR REPLACE INTO object_grants (oid, user, at) VALUES (?, ?, ?)", (oid, user, now))
        self.execute("DELETE FROM object_grants WHERE at < ?", (now - GRANT_SECONDS,))

    def grant_has(self, oid: str, user: str) -> bool:
        return self.execute("SELECT 1 FROM object_grants WHERE oid = ? AND user = ? AND at >= ?",
                            (oid, user, time.time() - GRANT_SECONDS)).fetchone() is not None

    def acl_replace(self, rows) -> None:
        with self.transaction() as c:
            c.execute("DELETE FROM object_acl")
            c.executemany("INSERT OR IGNORE INTO object_acl (oid, prefix) VALUES (?, ?)", rows)

    # -- small key/value settings ------------------------------------------------------------------
    def kv_get(self, key: str) -> str | None:
        row = self.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def kv_set(self, key: str, value: str) -> None:
        self.execute("INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                     (key, value))

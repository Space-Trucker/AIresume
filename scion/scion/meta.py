"""The metadata store (ER diagram 06 §6.9; Spanner keys 06 §6.10; ADR-24).

Holds the changeset write-ahead log (FR-CS-05), refs moved only by compare-and-swap (FR-REF-02)
with their log (FR-REF-04), derived-data values (FR-DD-05), the indexes, the audit log, change
requests, landings, the post-merge queue and the git map. ``MetaStore`` is the contract: every
other module reaches the metadata through its methods, never through SQL, so the two
implementations keep the same semantics (FR-ST-01):

* ``SqliteMetaStore``: one SQLite file per repository, in WAL mode so several server processes on
  one host can share it;
* ``spanner.SpannerMetaStore``: Cloud Spanner, one database per deployment (ADR-24).

``open_metastore`` picks one from the deployment's configuration (FR-ST-02).
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Callable, Iterable, Iterator

GRANT_SECONDS = 24 * 3600
CR_COLUMNS = ("id", "title", "description", "author", "target", "head", "state", "created", "updated",
              "landed_cs", "landed_at", "conflict")
AUDIT_FIELDS = ("seq", "at", "actor", "action", "target", "detail", "prev", "hash")
LANDING_FIELDS = ("cs", "source", "cr", "ref", "landed_at", "head")


class MetaStore:
    """The operations every backend provides. Times are seconds since the epoch, passed in by the
    caller where they decide an outcome (leases, grants), so both backends judge them alike."""

    def close(self) -> None:
        """Release connections; later calls reconnect."""
        raise NotImplementedError

    # -- changeset log (FR-CS-04/05/06) ------------------------------------------------------------
    def insert_changeset(self, cs_id: str, data: bytes) -> bool:
        """Store a changeset once; True if it was new. Changesets never change."""
        raise NotImplementedError

    def get_changeset_data(self, cs_id: str) -> bytes | None:
        raise NotImplementedError

    def has_changeset(self, cs_id: str) -> bool:
        raise NotImplementedError

    def resolve_prefix(self, prefix: str, limit: int = 2) -> list[str]:
        """Changeset ids starting with a lower-case hex prefix, in id order."""
        raise NotImplementedError

    def count_changesets(self) -> int:
        raise NotImplementedError

    def tail(self, after=None, limit: int = 1000, data: bool = False) -> list[tuple]:
        """Changesets in the order they were stored, after the opaque cursor ``after`` (None: from
        the first): ``(cursor, id)``, or ``(cursor, id, data)`` with ``data``."""
        raise NotImplementedError

    # -- refs (FR-REF-02/04) -------------------------------------------------------------------------
    def get_ref(self, name: str) -> tuple[str, int] | None:
        """``(target, version)``; the version counts the moves since the ref was created."""
        raise NotImplementedError

    def list_refs(self) -> list[tuple[str, str, int]]:
        """``(name, target, version)`` by name."""
        raise NotImplementedError

    def cas_ref(self, name: str, expected: str | None, new: str | None, who: str = "") -> bool:
        """Compare-and-swap one ref and log the move, atomically. ``expected=None``: the ref must not
        exist. ``new=None``: delete it."""
        raise NotImplementedError

    def ref_log(self, name: str, limit: int = 100) -> list[tuple]:
        """Newest first: ``(old, new, who, at)``."""
        raise NotImplementedError

    # -- derived data (FR-DD-05) ---------------------------------------------------------------------
    def derived_get(self, dtype: str, cs_id: str) -> str | None:
        raise NotImplementedError

    def derived_put(self, dtype: str, cs_id: str, value: str) -> None:
        """Values are deterministic: whichever server writes first wins, and both are identical."""
        raise NotImplementedError

    def derived_count(self, dtype: str) -> int:
        raise NotImplementedError

    # -- copy-detection index (FR-DD-11) ------------------------------------------------------------
    def blob_index_add(self, rows: Iterable[tuple[str, str]]) -> None:
        """``(blob, path)`` pairs."""
        raise NotImplementedError

    def blob_index_paths(self, blob: str, limit: int = 50) -> list[str]:
        raise NotImplementedError

    # -- content index (FR-SR-03, ADR-16) ------------------------------------------------------------
    def content_status(self, blob: str) -> str | None:
        """``i`` indexed, ``b`` binary, ``l`` text too large to index; None: not seen yet."""
        raise NotImplementedError

    def content_add(self, blob: str, status: str, grams) -> None:
        raise NotImplementedError

    def content_count(self, gram: str) -> int:
        raise NotImplementedError

    def content_postings(self, gram: str) -> set[str]:
        raise NotImplementedError

    def content_unindexed(self) -> list[str]:
        """Text blobs too large to index: content search always reads them."""
        raise NotImplementedError

    # -- object ACL index (FR-IAM-04/05/09/11) ---------------------------------------------------------
    # One row per (object, directory that restricts a place it appears); "" marks a place everyone
    # may read, which makes the object public (FR-IAM-11).
    def acl_add(self, rows: Iterable[tuple[str, str]]) -> None:
        raise NotImplementedError

    def acl_get(self, ids) -> dict[str, set[str]]:
        raise NotImplementedError

    def acl_replace(self, rows: Iterable[tuple[str, str]]) -> None:
        """Replace the whole index (a re-index, FR-IAM-09)."""
        raise NotImplementedError

    def grant_add(self, oid: str, user: str, now: float) -> None:
        """Record that ``user`` uploaded the exact bytes of an object they may not otherwise read;
        grants older than GRANT_SECONDS lapse."""
        raise NotImplementedError

    def grant_has(self, oid: str, user: str, now: float) -> bool:
        raise NotImplementedError

    # -- small key/value settings ---------------------------------------------------------------------
    def kv_get(self, key: str) -> str | None:
        raise NotImplementedError

    def kv_set(self, key: str, value: str) -> None:
        raise NotImplementedError

    # -- the git map (FR-MG-07) ----------------------------------------------------------------------
    def git_map_put(self, git: str, cs: str) -> None:
        raise NotImplementedError

    def git_map_lookup(self, git: str | None = None, cs: str | None = None) -> tuple[str, str] | None:
        """``(git, cs)`` for a git commit, or for a changeset."""
        raise NotImplementedError

    # -- the audit log (FR-IAM-10, ADR-15) -------------------------------------------------------------
    def audit_append(self, make: Callable[[int, str | None], tuple]) -> tuple[int, str]:
        """Append one entry. ``make(seq, last_hash)`` builds the row ``(at, actor, action, target,
        detail, prev, hash)`` for the next sequence number, given the hash of the last entry (None
        before the first). Appends are serialized, so the chain stays linear. Returns ``(seq, hash)``."""
        raise NotImplementedError

    def audit_entries(self, limit: int = 100, action: str | None = None, before: int | None = None) -> list[tuple]:
        """Newest first, as AUDIT_FIELDS tuples."""
        raise NotImplementedError

    def audit_iter(self) -> Iterator[tuple]:
        """Every entry, oldest first, as AUDIT_FIELDS tuples."""
        raise NotImplementedError

    # -- change requests (FR-RV-01…04) ------------------------------------------------------------------
    def cr_create(self, title: str, description: str, author: str, target: str, head: str, state: str,
                  now: float) -> int:
        """A new CR with its first revision; returns its id (ids increase)."""
        raise NotImplementedError

    def cr_get(self, cr_id: int) -> dict | None:
        """The CR row, keyed by CR_COLUMNS."""
        raise NotImplementedError

    def cr_update(self, cr_id: int, **cols) -> None:
        """Set columns of CR_COLUMNS."""
        raise NotImplementedError

    def cr_add_revision(self, cr_id: int, head: str, state: str, now: float) -> int:
        """A new revision: the CR moves to ``head`` and ``state`` and loses its conflict. Returns its
        number."""
        raise NotImplementedError

    def cr_latest_rev(self, cr_id: int) -> int | None:
        raise NotImplementedError

    def cr_revisions(self, cr_id: int) -> list[tuple]:
        """``(rev, head, created)`` by revision."""
        raise NotImplementedError

    def cr_approve(self, cr_id: int, rev: int, user: str, now: float) -> None:
        """Idempotent per (CR, revision, user)."""
        raise NotImplementedError

    def cr_approvals(self, cr_id: int) -> list[tuple]:
        """``(rev, user)`` in the order given."""
        raise NotImplementedError

    def cr_approvers(self, cr_id: int, rev: int) -> set[str]:
        raise NotImplementedError

    def cr_comment(self, cr_id: int, rev: int, user: str, path: str | None, line: int | None, body: str,
                   now: float) -> int:
        """Returns the comment's id (ids increase)."""
        raise NotImplementedError

    def cr_comments(self, cr_id: int) -> list[tuple]:
        """``(id, rev, user, path, line, body, created)`` by id."""
        raise NotImplementedError

    def cr_list(self, state: str | None = None, author: str | None = None, limit: int = 50) -> list[int]:
        """CR ids, newest first."""
        raise NotImplementedError

    # -- landings and the post-merge queue (FR-LD-05/07, FR-PM-01…03, ADR-22) ----------------------------
    def record_landings(self, rows: list[tuple], jobs: list[tuple], cr_updates: list[tuple]) -> None:
        """One landing, atomically: index ``rows`` (LANDING_FIELDS; the first record of a changeset
        stays), queue ``jobs`` (``(cs, cr, ref, status, created)``), and apply ``cr_updates``
        (``(cr_id, {column: value})``)."""
        raise NotImplementedError

    def landing_find(self, cs: str) -> dict | None:
        """The landing of a changeset, by its landed id or its pre-rebase id (LANDING_FIELDS)."""
        raise NotImplementedError

    def landing_members(self, head: str) -> set[str]:
        """Every changeset indexed with the landing whose new tip was ``head``."""
        raise NotImplementedError

    def postmerge_requeue(self, started_before: float) -> int:
        """Return running jobs claimed before ``started_before`` to the queue; how many."""
        raise NotImplementedError

    def postmerge_claim(self, claim: str, now: float) -> dict | None:
        """Move the oldest queued job to running under ``claim``: ``{id, cs, cr, ref}``, or None when
        the queue is empty. Concurrent claims never take the same job."""
        raise NotImplementedError

    def postmerge_report(self, job_id: int, status: str, now: float, log: str, claim: str | None = None) -> bool:
        """Finish a running job (under ``claim``, if given); False if it isn't running so."""
        raise NotImplementedError

    def postmerge_mark_reverted(self, job_id: int, note: str) -> bool:
        """A failed job whose landing was reverted: the note is appended to its log."""
        raise NotImplementedError

    def postmerge_counts(self) -> dict[str, int]:
        """Jobs queued and running."""
        raise NotImplementedError

    def postmerge_job_for(self, cs: str) -> dict | None:
        """The newest job of a changeset: ``{id, cs, cr, ref, status}``."""
        raise NotImplementedError

    def postmerge_list(self, ref: str, limit: int = 50) -> list[dict]:
        """Newest first: ``{id, cs, cr, status, created, finished}``."""
        raise NotImplementedError

    # -- backup (FR-AD-06, FR-ST-04) -------------------------------------------------------------------
    def is_empty(self) -> bool:
        """True when the store holds no metadata for this repository yet."""
        raise NotImplementedError

    def load(self, path: str) -> None:
        """Load a backup's metadata (a SQLite file written by ``export``) into this store, which must
        be empty: a restore never overwrites metadata."""
        raise NotImplementedError

    def export(self, path: str, at=None):
        """Write a consistent copy of this repository's metadata, as of one moment, to a new SQLite
        database at ``path`` (the backup format). A Spanner store reads at ``at`` when given, so all
        the repositories of a deployment can be copied as of one timestamp; returns the moment used
        (None for SQLite)."""
        raise NotImplementedError


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
CREATE TABLE IF NOT EXISTS git_map (git TEXT PRIMARY KEY, cs TEXT NOT NULL) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS git_map_cs ON git_map(cs);
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
CREATE TABLE IF NOT EXISTS crs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL, description TEXT NOT NULL, author TEXT NOT NULL, target TEXT NOT NULL,
    head TEXT NOT NULL, state TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL,
    landed_cs TEXT, landed_at REAL, conflict TEXT
);
CREATE INDEX IF NOT EXISTS crs_state ON crs(state, id);
CREATE TABLE IF NOT EXISTS cr_revisions (
    cr INTEGER NOT NULL, rev INTEGER NOT NULL, head TEXT NOT NULL, created REAL NOT NULL,
    PRIMARY KEY (cr, rev)
);
CREATE TABLE IF NOT EXISTS cr_approvals (
    cr INTEGER NOT NULL, rev INTEGER NOT NULL, user TEXT NOT NULL, created REAL NOT NULL,
    PRIMARY KEY (cr, rev, user)
);
CREATE TABLE IF NOT EXISTS cr_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, cr INTEGER NOT NULL, rev INTEGER NOT NULL, user TEXT NOT NULL,
    path TEXT, line INTEGER, body TEXT NOT NULL, created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS landings (
    cs TEXT PRIMARY KEY, source TEXT NOT NULL, cr INTEGER, ref TEXT NOT NULL, landed_at REAL NOT NULL,
    head TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS landings_source ON landings(source);
CREATE INDEX IF NOT EXISTS landings_head ON landings(head);
CREATE TABLE IF NOT EXISTS postmerge (
    id INTEGER PRIMARY KEY AUTOINCREMENT, cs TEXT NOT NULL, cr INTEGER, ref TEXT NOT NULL,
    status TEXT NOT NULL, created REAL NOT NULL, started REAL, finished REAL, worker TEXT, log TEXT
);
CREATE INDEX IF NOT EXISTS postmerge_status ON postmerge(status, id);
CREATE INDEX IF NOT EXISTS postmerge_cs ON postmerge(cs);
"""


def check_cr_columns(cols: dict) -> None:
    bad = set(cols) - set(CR_COLUMNS[1:])
    if bad:
        raise ValueError(f"unknown change request columns {sorted(bad)}")


def _cr_sets(cols: dict) -> tuple[str, list]:
    check_cr_columns(cols)
    return ", ".join(f"{k} = ?" for k in cols), list(cols.values())


class SqliteMetaStore(MetaStore):
    """One repository's metadata in a SQLite file. Every operation is a single-row or single-key
    access, the pattern that maps onto Spanner; multi-row units run in one transaction."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self._local = threading.local()
        self._lock = threading.Lock()
        self._conns: list[tuple[threading.Thread, sqlite3.Connection]] = []
        self._gen = 0
        self.conn().executescript(SCHEMA)

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
        with self._lock:
            self._gen += 1
            conns, self._conns = self._conns, []
        for _, c in conns:
            try:
                c.close()
            except sqlite3.Error:
                pass

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

    def _one(self, sql: str, args: Iterable = ()):
        row = self.execute(sql, args).fetchone()
        return row[0] if row else None

    # -- changeset log ----------------------------------------------------------------------------
    def insert_changeset(self, cs_id, data):
        cur = self.execute("INSERT OR IGNORE INTO changesets (id, data, created) VALUES (?, ?, ?)",
                           (cs_id, data, time.time()))
        return cur.rowcount == 1

    def get_changeset_data(self, cs_id):
        return self._one("SELECT data FROM changesets WHERE id = ?", (cs_id,))

    def has_changeset(self, cs_id):
        return self._one("SELECT 1 FROM changesets WHERE id = ?", (cs_id,)) is not None

    def resolve_prefix(self, prefix, limit=2):
        p = prefix.lower()
        return [r[0] for r in self.execute(
            "SELECT id FROM changesets WHERE id >= ? AND id < ? ORDER BY id LIMIT ?", (p, p + "g", limit))]

    def count_changesets(self):
        return self._one("SELECT COUNT(*) FROM changesets")

    def tail(self, after=None, limit=1000, data=False):
        cols = "seq, id, data" if data else "seq, id"
        return self.execute(f"SELECT {cols} FROM changesets WHERE seq > ? ORDER BY seq LIMIT ?",
                            (after or 0, limit)).fetchall()

    # -- refs ---------------------------------------------------------------------------------------
    def get_ref(self, name):
        row = self.execute("SELECT target, version FROM refs WHERE name = ?", (name,)).fetchone()
        return (row[0], row[1]) if row else None

    def list_refs(self):
        return self.execute("SELECT name, target, version FROM refs ORDER BY name").fetchall()

    def cas_ref(self, name, expected, new, who=""):
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

    def ref_log(self, name, limit=100):
        return self.execute("SELECT old, new, who, at FROM ref_log WHERE name = ? ORDER BY id DESC LIMIT ?",
                            (name, limit)).fetchall()

    # -- derived data -------------------------------------------------------------------------------
    def derived_get(self, dtype, cs_id):
        return self._one("SELECT value FROM derived WHERE type = ? AND cs = ?", (dtype, cs_id))

    def derived_put(self, dtype, cs_id, value):
        self.execute("INSERT OR IGNORE INTO derived (type, cs, value) VALUES (?, ?, ?)", (dtype, cs_id, value))

    def derived_count(self, dtype):
        return self._one("SELECT COUNT(*) FROM derived WHERE type = ?", (dtype,))

    # -- copy-detection index -------------------------------------------------------------------------
    def blob_index_add(self, rows):
        self.executemany("INSERT OR IGNORE INTO blob_index (blob, path) VALUES (?, ?)", rows)

    def blob_index_paths(self, blob, limit=50):
        return [r[0] for r in self.execute("SELECT path FROM blob_index WHERE blob = ? ORDER BY path LIMIT ?",
                                           (blob, limit))]

    # -- content index ------------------------------------------------------------------------------
    def content_status(self, blob):
        return self._one("SELECT status FROM content_blobs WHERE blob = ?", (blob,))

    def content_add(self, blob, status, grams):
        with self.transaction() as c:
            c.executemany("INSERT OR IGNORE INTO content_trigrams (trigram, blob) VALUES (?, ?)",
                          ((g, blob) for g in grams))
            c.execute("INSERT OR IGNORE INTO content_blobs (blob, status) VALUES (?, ?)", (blob, status))

    def content_count(self, gram):
        return self._one("SELECT COUNT(*) FROM content_trigrams WHERE trigram = ?", (gram,))

    def content_postings(self, gram):
        return {r[0] for r in self.execute("SELECT blob FROM content_trigrams WHERE trigram = ?", (gram,))}

    def content_unindexed(self):
        return [r[0] for r in self.execute("SELECT blob FROM content_blobs WHERE status = 'l'")]

    # -- object ACL index and grants -----------------------------------------------------------------
    def acl_add(self, rows):
        self.executemany("INSERT OR IGNORE INTO object_acl (oid, prefix) VALUES (?, ?)", rows)

    def acl_get(self, ids):
        out: dict[str, set[str]] = {}
        ids = list(dict.fromkeys(ids))
        for i in range(0, len(ids), 500):
            chunk = ids[i:i + 500]
            q = f"SELECT oid, prefix FROM object_acl WHERE oid IN ({','.join('?' * len(chunk))})"
            for oid, prefix in self.execute(q, chunk):
                out.setdefault(oid, set()).add(prefix)
        return out

    def acl_replace(self, rows):
        with self.transaction() as c:
            c.execute("DELETE FROM object_acl")
            c.executemany("INSERT OR IGNORE INTO object_acl (oid, prefix) VALUES (?, ?)", rows)

    def grant_add(self, oid, user, now):
        self.execute("INSERT OR REPLACE INTO object_grants (oid, user, at) VALUES (?, ?, ?)", (oid, user, now))
        self.execute("DELETE FROM object_grants WHERE at < ?", (now - GRANT_SECONDS,))

    def grant_has(self, oid, user, now):
        return self._one("SELECT 1 FROM object_grants WHERE oid = ? AND user = ? AND at >= ?",
                         (oid, user, now - GRANT_SECONDS)) is not None

    # -- settings --------------------------------------------------------------------------------------
    def kv_get(self, key):
        return self._one("SELECT value FROM kv WHERE key = ?", (key,))

    def kv_set(self, key, value):
        self.execute("INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                     (key, value))

    # -- git map ---------------------------------------------------------------------------------------
    def git_map_put(self, git, cs):
        self.execute("INSERT OR REPLACE INTO git_map (git, cs) VALUES (?, ?)", (git, cs))

    def git_map_lookup(self, git=None, cs=None):
        where, key = ("git", git) if git is not None else ("cs", cs)
        row = self.execute(f"SELECT git, cs FROM git_map WHERE {where} = ?", (key,)).fetchone()
        return (row[0], row[1]) if row else None

    # -- audit log ---------------------------------------------------------------------------------------
    def audit_append(self, make):
        with self.transaction() as c:  # BEGIN IMMEDIATE: one appender at a time
            last = c.execute("SELECT seq, hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
            seq = last[0] + 1 if last else 1
            row = make(seq, last[1] if last else None)
            c.execute(f"INSERT INTO audit ({', '.join(AUDIT_FIELDS)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (seq, *row))
        return seq, row[-1]

    def audit_entries(self, limit=100, action=None, before=None):
        q, args = f"SELECT {', '.join(AUDIT_FIELDS)} FROM audit WHERE 1 = 1", []
        if action:
            q += " AND action = ?"
            args.append(action)
        if before:
            q += " AND seq < ?"
            args.append(int(before))
        q += " ORDER BY seq DESC LIMIT ?"
        args.append(int(limit))
        return self.execute(q, args).fetchall()

    def audit_iter(self):
        return iter(self.execute(f"SELECT {', '.join(AUDIT_FIELDS)} FROM audit ORDER BY seq"))

    # -- change requests ---------------------------------------------------------------------------------
    def cr_create(self, title, description, author, target, head, state, now):
        with self.transaction() as c:
            cr_id = c.execute("INSERT INTO crs (title, description, author, target, head, state, created, updated) "
                              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (title, description, author, target, head, state, now, now)).lastrowid
            c.execute("INSERT INTO cr_revisions (cr, rev, head, created) VALUES (?, 1, ?, ?)", (cr_id, head, now))
        return cr_id

    def cr_get(self, cr_id):
        row = self.execute(f"SELECT {', '.join(CR_COLUMNS)} FROM crs WHERE id = ?", (int(cr_id),)).fetchone()
        return dict(zip(CR_COLUMNS, row)) if row else None

    def cr_update(self, cr_id, **cols):
        sets, args = _cr_sets(cols)
        self.execute(f"UPDATE crs SET {sets} WHERE id = ?", (*args, int(cr_id)))

    def cr_add_revision(self, cr_id, head, state, now):
        with self.transaction() as c:
            rev = c.execute("SELECT MAX(rev) FROM cr_revisions WHERE cr = ?", (cr_id,)).fetchone()[0] + 1
            c.execute("INSERT INTO cr_revisions (cr, rev, head, created) VALUES (?, ?, ?, ?)", (cr_id, rev, head, now))
            c.execute("UPDATE crs SET head = ?, state = ?, conflict = NULL, updated = ? WHERE id = ?",
                      (head, state, now, cr_id))
        return rev

    def cr_latest_rev(self, cr_id):
        return self._one("SELECT MAX(rev) FROM cr_revisions WHERE cr = ?", (cr_id,))

    def cr_revisions(self, cr_id):
        return self.execute("SELECT rev, head, created FROM cr_revisions WHERE cr = ? ORDER BY rev",
                            (cr_id,)).fetchall()

    def cr_approve(self, cr_id, rev, user, now):
        self.execute("INSERT OR IGNORE INTO cr_approvals (cr, rev, user, created) VALUES (?, ?, ?, ?)",
                     (cr_id, rev, user, now))

    def cr_approvals(self, cr_id):
        return self.execute("SELECT rev, user FROM cr_approvals WHERE cr = ? ORDER BY created", (cr_id,)).fetchall()

    def cr_approvers(self, cr_id, rev):
        return {u for (u,) in self.execute("SELECT user FROM cr_approvals WHERE cr = ? AND rev = ?", (cr_id, rev))}

    def cr_comment(self, cr_id, rev, user, path, line, body, now):
        return self.execute("INSERT INTO cr_comments (cr, rev, user, path, line, body, created) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?)", (cr_id, rev, user, path, line, body, now)).lastrowid

    def cr_comments(self, cr_id):
        return self.execute("SELECT id, rev, user, path, line, body, created FROM cr_comments WHERE cr = ? "
                            "ORDER BY id", (cr_id,)).fetchall()

    def cr_list(self, state=None, author=None, limit=50):
        q, args = "SELECT id FROM crs WHERE 1 = 1", []
        if state:
            q += " AND state = ?"
            args.append(state)
        if author:
            q += " AND author = ?"
            args.append(author)
        q += " ORDER BY id DESC LIMIT ?"
        args.append(int(limit))
        return [r[0] for r in self.execute(q, args).fetchall()]

    # -- landings and the post-merge queue ------------------------------------------------------------
    def record_landings(self, rows, jobs, cr_updates):
        with self.transaction() as c:
            c.executemany(f"INSERT OR IGNORE INTO landings ({', '.join(LANDING_FIELDS)}) VALUES (?, ?, ?, ?, ?, ?)",
                          rows)
            c.executemany("INSERT INTO postmerge (cs, cr, ref, status, created) VALUES (?, ?, ?, ?, ?)", jobs)
            for cr_id, cols in cr_updates:
                sets, args = _cr_sets(cols)
                c.execute(f"UPDATE crs SET {sets} WHERE id = ?", (*args, int(cr_id)))

    def landing_find(self, cs):
        cols = ", ".join(LANDING_FIELDS)
        row = self.execute(f"SELECT {cols} FROM landings WHERE cs = ? "
                           f"UNION ALL SELECT {cols} FROM landings WHERE source = ? LIMIT 1", (cs, cs)).fetchone()
        return dict(zip(LANDING_FIELDS, row)) if row else None

    def landing_members(self, head):
        return {r[0] for r in self.execute("SELECT cs FROM landings WHERE head = ?", (head,))}

    def postmerge_requeue(self, started_before):
        return self.execute("UPDATE postmerge SET status = 'queued', started = NULL, worker = NULL "
                            "WHERE status = 'running' AND started < ?", (started_before,)).rowcount

    def postmerge_claim(self, claim, now):
        while True:
            row = self.execute("SELECT id, cs, cr, ref FROM postmerge WHERE status = 'queued' ORDER BY id LIMIT 1"
                               ).fetchone()
            if row is None:
                return None
            cur = self.execute("UPDATE postmerge SET status = 'running', started = ?, worker = ? "
                               "WHERE id = ? AND status = 'queued'", (now, claim, row[0]))
            if cur.rowcount == 1:  # a lost race moves on to the next job (D-01)
                return dict(zip(("id", "cs", "cr", "ref"), row))

    def postmerge_report(self, job_id, status, now, log, claim=None):
        sql, args = "UPDATE postmerge SET status = ?, finished = ?, log = ? WHERE id = ? AND status = 'running'", \
            [status, now, log, int(job_id)]
        if claim is not None:
            sql, args = sql + " AND worker = ?", args + [claim]
        return self.execute(sql, args).rowcount == 1

    def postmerge_mark_reverted(self, job_id, note):
        return self.execute("UPDATE postmerge SET status = 'reverted', log = COALESCE(log, '') || ? "
                            "WHERE id = ? AND status = 'failed'", (note, int(job_id))).rowcount == 1

    def postmerge_counts(self):
        return dict(self.execute("SELECT status, COUNT(*) FROM postmerge WHERE status IN ('queued', 'running') "
                                 "GROUP BY status").fetchall())

    def postmerge_job_for(self, cs):
        row = self.execute("SELECT id, cs, cr, ref, status FROM postmerge WHERE cs = ? ORDER BY id DESC LIMIT 1",
                           (cs,)).fetchone()
        return dict(zip(("id", "cs", "cr", "ref", "status"), row)) if row else None

    def postmerge_list(self, ref, limit=50):
        rows = self.execute("SELECT id, cs, cr, status, created, finished FROM postmerge WHERE ref = ? "
                            "ORDER BY id DESC LIMIT ?", (ref, int(limit))).fetchall()
        return [dict(zip(("id", "cs", "cr", "status", "created", "finished"), r)) for r in rows]

    # -- backup ---------------------------------------------------------------------------------------
    def is_empty(self):
        tables = [r[0] for r in self.execute("SELECT name FROM sqlite_master WHERE type = 'table' "
                                             "AND name NOT LIKE 'sqlite_%'")]
        return all(self._one(f"SELECT 1 FROM {t} LIMIT 1") is None for t in tables)

    def load(self, path):
        if not self.is_empty():
            raise ValueError(f"{self.path} already holds metadata")
        source = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            source.backup(self.conn())
        finally:
            source.close()
        self.conn().executescript(SCHEMA)  # tables added since the backup was taken

    def export(self, path, at=None):
        """SQLite's online backup API: a snapshot of one moment, as a single self-contained file."""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        source = sqlite3.connect(self.path, timeout=60)
        target = sqlite3.connect(path)
        try:
            source.backup(target)
            target.execute("PRAGMA journal_mode=DELETE")  # no -wal file beside the copy
        finally:
            target.close()
            source.close()
        return None


def open_metastore(config: dict | None, repo_dir: str, name: str) -> MetaStore:
    """The store for one repository, from the ``metadata`` section of deployment.json (FR-ST-02):
    absent or ``{"backend": "sqlite"}`` keeps ``meta.db`` in the repository's directory;
    ``{"backend": "spanner", ...}`` uses the deployment's Spanner database (spanner.SpannerConfig)."""
    backend = (config or {}).get("backend", "sqlite")
    if backend == "sqlite":
        return SqliteMetaStore(os.path.join(repo_dir, "meta.db"))
    if backend == "spanner":
        from .spanner import SpannerMetaStore, client_for
        return SpannerMetaStore(client_for(config), name)
    raise ValueError(f"unknown metadata backend {backend!r} (use sqlite or spanner)")

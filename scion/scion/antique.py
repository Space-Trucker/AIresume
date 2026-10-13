"""Antique: code review and landing.

* Change requests (CRs) point at a changeset (``head``).  No branch or ref is needed, because
  changesets are addressable by id.
* Approval rules are semantic.  Each changed file is classified as docs, comment-only or logic,
  and each directory rule says how many approvals (and how many from owners) each category
  needs.  Human reviewers can then spend their attention on consequential changes.
* Landing is lock-free and has no merge queue.  The server rebases the CR onto the current tip
  of the target and moves the ref with a single compare-and-swap.  If someone else landed in
  between, it retries against the new tip.  Conflicts are reported in a structured form so an
  agent can fix them.
* Every landed changeset is indexed, so "when did this change merge to main?" is a single lookup
  rather than a linear scan of the commit log.
* Landing enqueues post-merge testing (see ``postmerge.py``) in place of pre-merge serialization.

Review policy (``policy.review``):

    {"rules": [
       {"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0}, "docs": {"approvals": 0}},
       {"prefix": "secrets", "owners": ["sec-team"],
        "logic": {"approvals": 2, "owner_approvals": 1}, "comment_only": {"approvals": 1}}
    ]}
"""
from __future__ import annotations

import json
import random
import threading
import time

from .classify import RANK, classify_diff
from .iam import PermissionDenied
from .repo import MergeConflict, NotFound, Repository

SCHEMA = """
CREATE TABLE IF NOT EXISTS crs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL, description TEXT NOT NULL, author TEXT NOT NULL,
    target TEXT NOT NULL, head TEXT NOT NULL, state TEXT NOT NULL,
    created REAL NOT NULL, updated REAL NOT NULL,
    landed_cs TEXT, landed_at REAL, conflict TEXT
);
CREATE TABLE IF NOT EXISTS cr_revisions (
    cr INTEGER NOT NULL, rev INTEGER NOT NULL, head TEXT NOT NULL, created REAL NOT NULL,
    PRIMARY KEY (cr, rev)
);
CREATE TABLE IF NOT EXISTS cr_approvals (
    cr INTEGER NOT NULL, rev INTEGER NOT NULL, user TEXT NOT NULL, created REAL NOT NULL,
    PRIMARY KEY (cr, rev, user)
);
CREATE TABLE IF NOT EXISTS cr_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, cr INTEGER NOT NULL, rev INTEGER NOT NULL,
    user TEXT NOT NULL, path TEXT, line INTEGER, body TEXT NOT NULL, created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS landings (
    cs TEXT PRIMARY KEY, source TEXT, cr INTEGER, ref TEXT NOT NULL, landed_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS landings_source ON landings(source);
CREATE TABLE IF NOT EXISTS postmerge (
    id INTEGER PRIMARY KEY AUTOINCREMENT, cs TEXT NOT NULL, cr INTEGER, ref TEXT NOT NULL,
    status TEXT NOT NULL, created REAL NOT NULL, started REAL, finished REAL,
    worker TEXT, log TEXT
);
CREATE INDEX IF NOT EXISTS postmerge_status ON postmerge(status, id);
"""

DEFAULT_RULES = [
    {"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0}, "docs": {"approvals": 0}}
]

OPEN, LANDED, ABANDONED, CONFLICT = "open", "landed", "abandoned", "conflict"


class _LandRequest:
    def __init__(self, cr_id: int | None, head: str):
        self.cr_id = cr_id
        self.head = head
        self.done = threading.Event()
        self.error: Exception | None = None
        self.landed: str | None = None

    def finish(self, landed: str) -> None:
        self.landed = landed
        self.done.set()

    def fail(self, error: Exception) -> None:
        self.error = error
        self.done.set()


class Antique:
    def __init__(self, repo: Repository, service_principal: str = "antique"):
        self.repo = repo
        self.meta = repo.meta
        self.principal = service_principal
        self.meta._conn().executescript(SCHEMA)
        self.counters = {"land.attempts": 0, "land.retries": 0, "land.success": 0, "land.conflicts": 0,
                         "land.batches": 0, "land.max_batch": 0}
        self._queues: dict[str, list[_LandRequest]] = {}
        self._leaders: dict[str, threading.Lock] = {}
        self._queue_lock = threading.Lock()

    # -- helpers -----------------------------------------------------------------------------
    def _row(self, cr_id: int) -> dict:
        row = self.meta.execute(
            "SELECT id, title, description, author, target, head, state, created, updated, "
            "landed_cs, landed_at, conflict FROM crs WHERE id = ?", (cr_id,)).fetchone()
        if row is None:
            raise NotFound(f"no change request {cr_id}")
        keys = ["id", "title", "description", "author", "target", "head", "state", "created",
                "updated", "landed_cs", "landed_at", "conflict"]
        d = dict(zip(keys, row))
        d["conflict"] = json.loads(d["conflict"]) if d["conflict"] else None
        return d

    def _latest_rev(self, cr_id: int) -> int:
        return self.meta.execute("SELECT MAX(rev) FROM cr_revisions WHERE cr = ?", (cr_id,)).fetchone()[0]

    def _rules(self) -> list[dict]:
        rules = self.repo.policy.review.get("rules") or DEFAULT_RULES
        return sorted(rules, key=lambda r: len(r.get("prefix", "").strip("/")))

    def _rule_for(self, path: str) -> dict:
        chosen = None
        for r in self._rules():
            p = r.get("prefix", "").strip("/")
            if p == "" or path == p or path.startswith(p + "/"):
                chosen = r
        return chosen or DEFAULT_RULES[0]

    # -- CR lifecycle --------------------------------------------------------------------------
    def create(self, user: str, title: str, head: str, description: str = "", target: str = "main") -> dict:
        head = self.repo.resolve(head)
        tip = self.repo.get_ref(target)
        if tip is not None and self.repo.is_ancestor(head, tip):
            raise ValueError(f"{head[:12]} is already part of {target}")
        now = time.time()
        cur = self.meta.execute(
            "INSERT INTO crs (title, description, author, target, head, state, created, updated) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (title, description, user, target, head, OPEN, now, now))
        cr_id = cur.lastrowid
        self.meta.execute("INSERT INTO cr_revisions (cr, rev, head, created) VALUES (?, 1, ?, ?)",
                          (cr_id, head, now))
        return self.get(cr_id)

    def update(self, user: str, cr_id: int, head: str) -> dict:
        cr = self._row(cr_id)
        if user != cr["author"] and not self.repo.policy.is_admin(user):
            raise PermissionDenied("only the author can upload new revisions")
        if cr["state"] not in (OPEN, CONFLICT):
            raise ValueError(f"change request is {cr['state']}")
        head = self.repo.resolve(head)
        rev = self._latest_rev(cr_id) + 1
        now = time.time()
        self.meta.execute("INSERT INTO cr_revisions (cr, rev, head, created) VALUES (?, ?, ?, ?)",
                          (cr_id, rev, head, now))
        self.meta.execute("UPDATE crs SET head = ?, state = ?, conflict = NULL, updated = ? WHERE id = ?",
                          (head, OPEN, now, cr_id))
        return self.get(cr_id)

    def approve(self, user: str, cr_id: int) -> dict:
        cr = self._row(cr_id)
        if cr["state"] not in (OPEN, CONFLICT):
            raise ValueError(f"change request is {cr['state']}")
        self.meta.execute("INSERT OR IGNORE INTO cr_approvals (cr, rev, user, created) VALUES (?, ?, ?, ?)",
                          (cr_id, self._latest_rev(cr_id), user, time.time()))
        return self.get(cr_id)

    def comment(self, user: str, cr_id: int, body: str, path: str | None = None,
                line: int | None = None) -> dict:
        self._row(cr_id)
        self.meta.execute(
            "INSERT INTO cr_comments (cr, rev, user, path, line, body, created) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cr_id, self._latest_rev(cr_id), user, path, line, body, time.time()))
        return self.get(cr_id)

    def abandon(self, user: str, cr_id: int) -> dict:
        cr = self._row(cr_id)
        if user != cr["author"] and not self.repo.policy.is_admin(user):
            raise PermissionDenied("only the author can abandon")
        self.meta.execute("UPDATE crs SET state = ?, updated = ? WHERE id = ?", (ABANDONED, time.time(), cr_id))
        return self.get(cr_id)

    # -- reads -----------------------------------------------------------------------------------
    def get(self, cr_id: int, with_requirements: bool = True) -> dict:
        cr = self._row(cr_id)
        rev = self._latest_rev(cr_id)
        cr["revision"] = rev
        cr["revisions"] = [
            {"rev": r, "head": h, "created": c}
            for r, h, c in self.meta.execute(
                "SELECT rev, head, created FROM cr_revisions WHERE cr = ? ORDER BY rev", (cr_id,)).fetchall()
        ]
        cr["approvals"] = [
            {"user": u, "rev": r}
            for r, u in self.meta.execute(
                "SELECT rev, user FROM cr_approvals WHERE cr = ? ORDER BY created", (cr_id,)).fetchall()
        ]
        cr["comments"] = [
            {"id": i, "rev": r, "user": u, "path": p, "line": l, "body": b, "created": c}
            for i, r, u, p, l, b, c in self.meta.execute(
                "SELECT id, rev, user, path, line, body, created FROM cr_comments WHERE cr = ? ORDER BY id",
                (cr_id,)).fetchall()
        ]
        if with_requirements and cr["state"] in (OPEN, CONFLICT):
            cr["requirements"] = self.requirements(cr_id)
        return cr

    def list(self, state: str | None = None, author: str | None = None, limit: int = 50) -> list[dict]:
        q = "SELECT id FROM crs WHERE 1=1"
        args: list = []
        if state:
            q += " AND state = ?"
            args.append(state)
        if author:
            q += " AND author = ?"
            args.append(author)
        q += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        return [self.get(r[0], with_requirements=False) for r in self.meta.execute(q, args).fetchall()]

    def _base(self, cr: dict) -> str | None:
        tip = self.repo.get_ref(cr["target"])
        return self.repo.merge_base(cr["head"], tip) if tip else None

    def requirements(self, cr_id: int) -> dict:
        cr = self._row(cr_id)
        rev = self._latest_rev(cr_id)
        approvers = {u for (u,) in self.meta.execute(
            "SELECT user FROM cr_approvals WHERE cr = ? AND rev = ?", (cr_id, rev)).fetchall()}
        approvers.discard(cr["author"])  # self-approval never counts
        files = classify_diff(self.repo, self._base(cr), cr["head"])
        groups: dict[str, dict] = {}
        for f in files:
            rule = self._rule_for(f["path"])
            prefix = rule.get("prefix", "").strip("/")
            g = groups.setdefault(prefix, {"prefix": prefix, "owners": rule.get("owners", []),
                                           "files": [], "category": "docs", "rule": rule})
            g["files"].append(f)
            if RANK[f["category"]] > RANK[g["category"]]:
                g["category"] = f["category"]
        satisfied = True
        out_groups = []
        for prefix, g in sorted(groups.items()):
            need = {"approvals": 0, "owner_approvals": 0}
            for f in g["files"]:
                req = g["rule"].get(f["category"], {"approvals": 1})
                for k in need:
                    need[k] = max(need[k], int(req.get(k, 0)))
            owners = g["owners"]
            owner_approvers = {u for u in approvers if owners and self.repo.policy._matches(u, owners)}
            have = {"approvals": len(approvers), "owner_approvals": len(owner_approvers)}
            ok = all(have[k] >= need[k] for k in need)
            satisfied &= ok
            out_groups.append({"prefix": prefix, "category": g["category"], "files": g["files"],
                               "owners": owners, "need": need, "have": have, "satisfied": ok})
        return {"satisfied": satisfied, "revision": rev, "approvers": sorted(approvers), "groups": out_groups}

    # -- landing -------------------------------------------------------------------------------
    def land(self, user: str, cr_id: int, timeout: float = 300.0, force: bool = False) -> dict:
        cr = self._row(cr_id)
        if cr["state"] == LANDED:
            return self.get(cr_id)
        if cr["state"] not in (OPEN, CONFLICT):
            raise ValueError(f"change request is {cr['state']}")
        if user != cr["author"] and not self.repo.policy.is_admin(user) and not self.repo.policy.is_service(user):
            raise PermissionDenied("only the author can land")
        if force and not self.repo.policy.is_admin(user):
            raise PermissionDenied("only admins can force-land")
        if not force:
            reqs = self.requirements(cr_id)
            if not reqs["satisfied"]:
                raise PermissionDenied("approval requirements are not satisfied: " + json.dumps(
                    [{k: g[k] for k in ("prefix", "category", "need", "have")}
                     for g in reqs["groups"] if not g["satisfied"]]))
        deadline = time.time() + timeout
        # Group commit: whichever request holds this server's per-target leader slot lands every
        # request queued here as one rebased chain with one compare-and-swap.  This is not a
        # repository lock: other servers never wait on it, and the ref row's CAS is the only
        # cross-server synchronization.
        self._submit(cr["target"], _LandRequest(cr_id, cr["head"]), deadline)
        return self.get(cr_id)

    def land_changeset(self, user: str, cs: str, target: str = "main", timeout: float = 300.0) -> dict:
        """Land a changeset that has no CR (e.g. an automated revert) through the same
        group-commit path: rebased onto the current tip and published with one CAS."""
        if not (self.repo.policy.is_admin(user) or self.repo.policy.is_service(user)):
            raise PermissionDenied("only services and admins may land without review")
        req = _LandRequest(None, self.repo.resolve(cs))
        self._submit(target, req, time.time() + timeout)
        return {"landed_cs": req.landed, "ref": target}

    def _submit(self, target: str, req: "_LandRequest", deadline: float) -> None:
        with self._queue_lock:
            self._queues.setdefault(target, []).append(req)
            leader = self._leaders.setdefault(target, threading.Lock())
        while not req.done.is_set():
            if leader.acquire(blocking=False):
                try:
                    self._drain(target, deadline)
                finally:
                    leader.release()
            else:
                req.done.wait(0.02)
        if req.error is not None:
            raise req.error

    def _drain(self, target: str, deadline: float) -> None:
        while True:
            with self._queue_lock:
                batch = self._queues.get(target, [])
                self._queues[target] = []
            if not batch:
                return
            self._land_batch(target, batch, deadline)

    def _land_batch(self, target: str, pending: list["_LandRequest"], deadline: float) -> None:
        attempt = 0
        while pending:
            attempt += 1
            self.counters["land.attempts"] += 1
            tip = self.repo.get_ref(target)
            new_head = tip
            planned = []
            for req in pending:
                try:
                    if new_head is None or self.repo.is_ancestor(new_head, req.head):
                        head, mapping = req.head, {}
                    else:
                        r = self.repo.rebase(req.head, new_head)
                        head, mapping = r["head"], r["rebased"]
                except MergeConflict as e:
                    self.counters["land.conflicts"] += 1
                    if req.cr_id is not None:
                        self.meta.execute("UPDATE crs SET state = ?, conflict = ?, updated = ? WHERE id = ?",
                                          (CONFLICT, json.dumps({"conflicts": e.conflicts, "at": e.at,
                                                                 "onto": new_head}), time.time(), req.cr_id))
                    req.fail(e)
                    continue
                planned.append((req, new_head, head, mapping))
                new_head = head
            pending = [p[0] for p in planned]
            if not pending:
                return
            if self.repo.update_ref(target, tip, new_head, user=self.principal):
                for req, base, head, mapping in planned:
                    self._record_landing(req.cr_id, target, base, head, mapping)
                    self.counters["land.success"] += 1
                    req.finish(head)
                self.counters["land.batches"] += 1
                self.counters["land.max_batch"] = max(self.counters["land.max_batch"], len(planned))
                return
            # Someone else landed first.  Rebase the whole batch onto the new tip and retry,
            # backing off with jitter so contending servers do not keep colliding.
            self.counters["land.retries"] += 1
            if time.time() > deadline:
                for req in pending:
                    req.fail(RuntimeError("could not land before the deadline (contention)"))
                return
            time.sleep(random.uniform(0, min(0.25, 0.004 * 2 ** min(attempt, 6))))

    def _record_landing(self, cr_id, target, old_tip, new_head, mapping) -> None:
        now = time.time()
        reverse = {v: k for k, v in mapping.items()}
        landed = []
        cur = new_head
        while cur and cur != old_tip:
            landed.append(cur)
            cur = self.repo.get_changeset(cur).first_parent
        rows = [(cs, reverse.get(cs, cs), cr_id, target, now) for cs in landed]
        self.meta._conn().executemany(
            "INSERT OR IGNORE INTO landings (cs, source, cr, ref, landed_at) VALUES (?, ?, ?, ?, ?)", rows)
        if cr_id is not None:
            self.meta.execute("UPDATE crs SET state = ?, head = ?, landed_cs = ?, landed_at = ?, conflict = NULL, "
                              "updated = ? WHERE id = ?", (LANDED, new_head, new_head, now, now, cr_id))
        self.meta.execute("INSERT INTO postmerge (cs, cr, ref, status, created) VALUES (?, ?, ?, 'queued', ?)",
                          (new_head, cr_id, target, now))

    def record_direct_landing(self, cs: str, ref: str, old_tip: str | None) -> None:
        """Index changesets landed outside a CR (e.g. by the revert pipeline)."""
        self._record_landing_rows(cs, ref, old_tip)

    def _record_landing_rows(self, new_head, ref, old_tip):
        now = time.time()
        cur = new_head
        rows = []
        while cur and cur != old_tip:
            rows.append((cur, cur, None, ref, now))
            cur = self.repo.get_changeset(cur).first_parent
        self.meta._conn().executemany(
            "INSERT OR IGNORE INTO landings (cs, source, cr, ref, landed_at) VALUES (?, ?, ?, ?, ?)", rows)
        self.meta.execute("INSERT INTO postmerge (cs, cr, ref, status, created) VALUES (?, NULL, ?, 'queued', ?)",
                          (new_head, ref, now))

    def find_landing(self, cs: str) -> dict | None:
        """When did this change land, and through which CR?  An indexed lookup that accepts the
        landed id or the pre-rebase id."""
        cs = self.repo.resolve(cs) if not self.meta.has_changeset(cs) else cs
        row = self.meta.execute(
            "SELECT cs, source, cr, ref, landed_at FROM landings WHERE cs = ? OR source = ? LIMIT 1",
            (cs, cs)).fetchone()
        if row is None:
            return None
        return {"cs": row[0], "source": row[1], "cr": row[2], "ref": row[3], "landed_at": row[4]}

    # -- post-merge queue --------------------------------------------------------------------
    def postmerge_claim(self, worker: str) -> dict | None:
        for _ in range(10):
            row = self.meta.execute(
                "SELECT id, cs, cr, ref FROM postmerge WHERE status = 'queued' ORDER BY id LIMIT 1").fetchone()
            if row is None:
                return None
            cur = self.meta.execute(
                "UPDATE postmerge SET status = 'running', started = ?, worker = ? WHERE id = ? AND status = 'queued'",
                (time.time(), worker, row[0]))
            if cur.rowcount == 1:
                return {"id": row[0], "cs": row[1], "cr": row[2], "ref": row[3]}
        return None

    def postmerge_report(self, job_id: int, passed: bool, log: str = "") -> None:
        self.meta.execute("UPDATE postmerge SET status = ?, finished = ?, log = ? WHERE id = ?",
                          ("passed" if passed else "failed", time.time(), log[-20000:], job_id))

    def postmerge_status(self, ref: str = "main", limit: int = 50) -> list[dict]:
        rows = self.meta.execute(
            "SELECT id, cs, cr, status, created, finished FROM postmerge WHERE ref = ? ORDER BY id DESC LIMIT ?",
            (ref, limit)).fetchall()
        return [{"id": i, "cs": c, "cr": cr, "status": s, "created": t, "finished": f}
                for i, c, cr, s, t, f in rows]

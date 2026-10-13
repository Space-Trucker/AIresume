"""Antique: code review and landing (FR-RV-*, FR-LD-*; 06 §6.5–6.8).

* A change request (CR) points at a changeset; no branch or ref is needed (FR-RV-01). Each upload
  is a new revision, and approvals belong to one revision (FR-RV-02, BR-02).
* Approval rules are semantic (ADR-09): every changed file is classified as docs, comment-only or
  logic, and the most specific directory rule says how many approvals each category needs, and how
  many must come from owners (FR-RV-05/06). The author's own approval never counts (BR-01).
* Landing has no global lock and no merge queue (ADR-07, FR-LD-02). The server rebases the CR onto
  the target's tip and moves the ref with one compare-and-swap. Concurrent landings on one server are
  group-committed: the request holding the per-target leader slot lands the whole queue as one
  rebased chain with one CAS; a lost CAS is retried with jittered backoff until a deadline (FR-LD-03).
* Every landed changeset is indexed to its CR, ref, time and pre-rebase id (FR-LD-05), and every
  landing queues a post-merge job (FR-LD-07).

Review policy, in the repository's ``policy.json``::

    "review": {
      "rules": [
        {"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0}, "docs": {"approvals": 0}},
        {"prefix": "secrets", "owners": ["sec-team"],
         "logic": {"approvals": 2, "owner_approvals": 1}, "comment_only": {"approvals": 1}}
      ],
      "webhooks": ["https://chat.example/hooks/review"]
    }
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
    cs TEXT PRIMARY KEY, source TEXT NOT NULL, cr INTEGER, ref TEXT NOT NULL, landed_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS landings_source ON landings(source);
CREATE TABLE IF NOT EXISTS postmerge (
    id INTEGER PRIMARY KEY AUTOINCREMENT, cs TEXT NOT NULL, cr INTEGER, ref TEXT NOT NULL,
    status TEXT NOT NULL, created REAL NOT NULL, started REAL, finished REAL, worker TEXT, log TEXT
);
CREATE INDEX IF NOT EXISTS postmerge_status ON postmerge(status, id);
"""

DEFAULT_RULES = [{"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0},
                  "docs": {"approvals": 0}}]
OPEN, LANDING, LANDED, CONFLICT, ABANDONED = "open", "landing", "landed", "conflict", "abandoned"
LANDABLE = (OPEN, CONFLICT)
CR_COLUMNS = ("id", "title", "description", "author", "target", "head", "state", "created", "updated",
              "landed_cs", "landed_at", "conflict")


class Retryable(Exception):
    """The landing could not finish before its deadline because of contention; try again."""
    http_status, code = 503, "retry"


class _LandRequest:
    def __init__(self, cr_id: int | None, head: str):
        self.cr_id, self.head = cr_id, head
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
    def __init__(self, repo: Repository, principal: str = "antique", notify=None, audit=None):
        self.repo, self.meta, self.principal = repo, repo.meta, principal
        self.notify = notify or (lambda event, repo, payload: None)
        self.audit = audit
        self.meta.ensure(SCHEMA)
        self.counters = {"land.requests": 0, "land.attempts": 0, "land.retries": 0, "land.landed": 0,
                         "land.conflicts": 0, "land.batches": 0, "land.max_batch": 0, "land.deadline": 0}
        self._queues: dict[str, list[_LandRequest]] = {}
        self._leaders: dict[str, threading.Lock] = {}
        self._lock = threading.Lock()

    @property
    def policy(self):
        return self.repo.policy

    # -- helpers ---------------------------------------------------------------------------------
    def _row(self, cr_id: int) -> dict:
        row = self.meta.execute(f"SELECT {', '.join(CR_COLUMNS)} FROM crs WHERE id = ?", (int(cr_id),)).fetchone()
        if row is None:
            raise NotFound(f"no change request {cr_id}")
        d = dict(zip(CR_COLUMNS, row))
        d["conflict"] = json.loads(d["conflict"]) if d["conflict"] else None
        return d

    def _latest_rev(self, cr_id: int) -> int:
        return self.meta.execute("SELECT MAX(rev) FROM cr_revisions WHERE cr = ?", (cr_id,)).fetchone()[0]

    def _set_state(self, cr_id: int, state: str, **cols) -> None:
        sets = ", ".join(f"{k} = ?" for k in cols)
        self.meta.execute(f"UPDATE crs SET state = ?, updated = ?{', ' + sets if sets else ''} WHERE id = ?",
                          (state, time.time(), *cols.values(), cr_id))

    def _rules(self) -> list[dict]:
        rules = getattr(self.policy, "review", {}).get("rules") or DEFAULT_RULES
        return sorted(rules, key=lambda r: len(r.get("prefix", "").strip("/")))

    def _rule_for(self, path: str) -> dict:
        chosen = DEFAULT_RULES[0]
        for r in self._rules():
            p = r.get("prefix", "").strip("/")
            if p == "" or path == p or path.startswith(p + "/"):
                chosen = r
        return chosen

    def _need_author_or_admin(self, user: str, cr: dict, what: str) -> None:
        if user != cr["author"] and not self.policy.is_admin(user):
            raise PermissionDenied(f"only the author or an administrator can {what}")

    def _event(self, event: str, cr_id: int, actor: str, **extra) -> None:
        cr = self._row(cr_id)
        payload = {"cr": {k: cr[k] for k in ("id", "title", "author", "target", "head", "state")}, "actor": actor,
                   **extra}
        self.notify(event, self.repo.name, payload)

    # -- the CR lifecycle (UC-13, UC-14) -------------------------------------------------------------
    def create(self, user: str, title: str, head: str, description: str = "", target: str = "main") -> dict:
        head = self.repo.resolve(head)
        tip = self.repo.get_ref(target)
        if tip is not None and self.repo.is_ancestor(head, tip):
            raise ValueError(f"{head[:12]} is already part of {target}")
        now = time.time()
        with self.meta.transaction() as c:
            cr_id = c.execute("INSERT INTO crs (title, description, author, target, head, state, created, updated) "
                              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (title, description, user, target, head, OPEN, now, now)).lastrowid
            c.execute("INSERT INTO cr_revisions (cr, rev, head, created) VALUES (?, 1, ?, ?)", (cr_id, head, now))
        self._event("cr.created", cr_id, user)
        return self.get(cr_id)

    def update(self, user: str, cr_id: int, head: str) -> dict:
        cr = self._row(cr_id)
        self._need_author_or_admin(user, cr, "upload a new revision")
        if cr["state"] not in LANDABLE:
            raise ValueError(f"change request {cr_id} is {cr['state']}")
        head = self.repo.resolve(head)
        now = time.time()
        with self.meta.transaction() as c:
            rev = c.execute("SELECT MAX(rev) FROM cr_revisions WHERE cr = ?", (cr_id,)).fetchone()[0] + 1
            c.execute("INSERT INTO cr_revisions (cr, rev, head, created) VALUES (?, ?, ?, ?)", (cr_id, rev, head, now))
            c.execute("UPDATE crs SET head = ?, state = ?, conflict = NULL, updated = ? WHERE id = ?",
                      (head, OPEN, now, cr_id))
        self._event("cr.updated", cr_id, user, revision=rev)
        return self.get(cr_id)

    def approve(self, user: str, cr_id: int) -> dict:
        cr = self._row(cr_id)
        if cr["state"] not in LANDABLE:
            raise ValueError(f"change request {cr_id} is {cr['state']}")
        self.meta.execute("INSERT OR IGNORE INTO cr_approvals (cr, rev, user, created) VALUES (?, ?, ?, ?)",
                          (cr_id, self._latest_rev(cr_id), user, time.time()))
        self._event("cr.approved", cr_id, user)
        return self.get(cr_id)

    def comment(self, user: str, cr_id: int, body: str, path: str | None = None, line: int | None = None) -> dict:
        self._row(cr_id)
        if not body or not body.strip():
            raise ValueError("an empty comment")
        if line is not None and (path is None or int(line) < 1):
            raise ValueError("a line comment needs a path and a line number from 1")
        self.meta.execute("INSERT INTO cr_comments (cr, rev, user, path, line, body, created) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (cr_id, self._latest_rev(cr_id), user, path, None if line is None else int(line), body,
                           time.time()))
        self._event("cr.commented", cr_id, user, path=path, line=line)
        return self.get(cr_id)

    def abandon(self, user: str, cr_id: int) -> dict:
        cr = self._row(cr_id)
        self._need_author_or_admin(user, cr, "abandon a change request")
        if cr["state"] not in LANDABLE:
            raise ValueError(f"change request {cr_id} is {cr['state']}")
        self._set_state(cr_id, ABANDONED)
        self._event("cr.abandoned", cr_id, user)
        return self.get(cr_id)

    # -- reads ---------------------------------------------------------------------------------------
    def get(self, cr_id: int, with_requirements: bool = True) -> dict:
        cr = self._row(cr_id)
        cr["revision"] = self._latest_rev(cr_id)
        cr["revisions"] = [{"rev": r, "head": h, "created": c} for r, h, c in self.meta.execute(
            "SELECT rev, head, created FROM cr_revisions WHERE cr = ? ORDER BY rev", (cr_id,))]
        cr["approvals"] = [{"user": u, "rev": r} for r, u in self.meta.execute(
            "SELECT rev, user FROM cr_approvals WHERE cr = ? ORDER BY created", (cr_id,))]
        cr["comments"] = [{"id": i, "rev": r, "user": u, "path": p, "line": ln, "body": b, "created": c}
                          for i, r, u, p, ln, b, c in self.meta.execute(
                              "SELECT id, rev, user, path, line, body, created FROM cr_comments WHERE cr = ? "
                              "ORDER BY id", (cr_id,))]
        if with_requirements and cr["state"] in LANDABLE:
            cr["requirements"] = self.requirements(cr_id)
        return cr

    def list(self, state: str | None = None, author: str | None = None, limit: int = 50) -> list[dict]:
        q, args = "SELECT id FROM crs WHERE 1 = 1", []
        if state:
            q += " AND state = ?"
            args.append(state)
        if author:
            q += " AND author = ?"
            args.append(author)
        q += " ORDER BY id DESC LIMIT ?"
        args.append(int(limit))
        return [self.get(r[0], with_requirements=False) for r in self.meta.execute(q, args).fetchall()]

    def base_of(self, cr: dict) -> str | None:
        """Where the CR's changes start: its merge base with the target."""
        tip = self.repo.get_ref(cr["target"])
        return self.repo.merge_base(cr["head"], tip) if tip else None

    def requirements(self, cr_id: int) -> dict:
        """Evaluate the approval rules for the latest revision (FR-RV-06/07)."""
        cr = self._row(cr_id)
        rev = self._latest_rev(cr_id)
        approvers = {u for (u,) in self.meta.execute("SELECT user FROM cr_approvals WHERE cr = ? AND rev = ?",
                                                     (cr_id, rev))}
        approvers.discard(cr["author"])  # BR-01
        groups: dict[str, dict] = {}
        for f in classify_diff(self.repo, self.base_of(cr), cr["head"]):
            rule = self._rule_for(f["path"])
            prefix = rule.get("prefix", "").strip("/")
            g = groups.setdefault(prefix, {"rule": rule, "files": [], "category": "docs"})
            g["files"].append(f)
            if RANK[f["category"]] > RANK[g["category"]]:
                g["category"] = f["category"]
        out, satisfied = [], True
        identity = self.policy.identity
        for prefix, g in sorted(groups.items()):
            need = {"approvals": 0, "owner_approvals": 0}
            for f in g["files"]:
                req = g["rule"].get(f["category"], {"approvals": 1})  # an unconfigured category needs one
                for k in need:
                    need[k] = max(need[k], int(req.get(k, 0)))
            owners = g["rule"].get("owners", [])
            have = {"approvals": len(approvers),
                    "owner_approvals": sum(1 for u in approvers if owners and identity.matches(u, owners))}
            ok = all(have[k] >= need[k] for k in need)
            satisfied &= ok
            out.append({"prefix": prefix, "category": g["category"], "owners": owners, "need": need, "have": have,
                        "satisfied": ok, "files": g["files"]})
        return {"satisfied": satisfied, "revision": rev, "approvers": sorted(approvers), "groups": out}

    # -- landing (UC-15) -------------------------------------------------------------------------------
    def land(self, user: str, cr_id: int, force: bool = False, timeout: float = 300.0) -> dict:
        cr = self._row(cr_id)
        if cr["state"] == LANDED:
            return self.get(cr_id)  # idempotent
        if cr["state"] not in LANDABLE:
            raise ValueError(f"change request {cr_id} is {cr['state']}")
        if user != cr["author"] and not (self.policy.is_admin(user) or self.policy.is_service(user)):
            raise PermissionDenied("only the author, a service or an administrator can land a change request")
        if force:
            if not self.policy.is_admin(user):
                raise PermissionDenied("only administrators can force-land")
            if self.audit:
                self.audit("cr.force_land", user, f"cr/{cr_id}", {"head": cr["head"]})
        else:
            reqs = self.requirements(cr_id)
            if not reqs["satisfied"]:
                unmet = [{k: g[k] for k in ("prefix", "category", "need", "have")}
                         for g in reqs["groups"] if not g["satisfied"]]
                raise PermissionDenied("approval requirements are not satisfied: " + json.dumps(unmet))
        self._set_state(cr_id, LANDING)  # visible while queued (D-02)
        req = _LandRequest(cr_id, cr["head"])
        try:
            self._submit(cr["target"], req, time.time() + timeout)
        except Retryable:
            self._set_state(cr_id, OPEN)
            raise
        return self.get(cr_id)

    def land_changeset(self, user: str, cs: str, target: str = "main", timeout: float = 300.0) -> dict:
        """Land a changeset without a CR, for automation such as reverts (FR-LD-06)."""
        if not (self.policy.is_admin(user) or self.policy.is_service(user)):
            raise PermissionDenied("only services and administrators may land without review")
        req = _LandRequest(None, self.repo.resolve(cs))
        self._submit(target, req, time.time() + timeout)
        if self.audit:
            self.audit("land_changeset", user, target, {"cs": req.head, "landed": req.landed})
        return {"landed_cs": req.landed, "ref": target}

    def _submit(self, target: str, req: _LandRequest, deadline: float) -> None:
        self.counters["land.requests"] += 1
        with self._lock:
            self._queues.setdefault(target, []).append(req)
            leader = self._leaders.setdefault(target, threading.Lock())
        # Whoever holds this server's leader slot for the target lands every queued request as one
        # batch. The slot is not a repository lock: other servers never wait for it, and the ref's
        # compare-and-swap is the only coordination between servers.
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
            with self._lock:
                batch, self._queues[target] = self._queues.get(target, []), []
            if not batch:
                return
            self._land_batch(target, batch, deadline)

    def _land_batch(self, target: str, pending: list[_LandRequest], deadline: float) -> None:
        attempt = 0
        while pending:
            attempt += 1
            self.counters["land.attempts"] += 1
            tip = self.repo.get_ref(target)
            head, planned = tip, []
            for req in pending:
                try:
                    if head is None or self.repo.is_ancestor(head, req.head):
                        new = req.head  # fast-forward
                    else:
                        # the changesets were permission-checked when they were created; the rebase
                        # replays them as they are, so it runs without a user
                        new = self.repo.rebase(req.head, head)["head"]
                except MergeConflict as e:
                    self.counters["land.conflicts"] += 1
                    if req.cr_id is not None:
                        self._set_state(req.cr_id, CONFLICT, conflict=json.dumps(
                            {"conflicts": e.conflicts, "at": e.at, "onto": head}))
                        self._event("cr.conflict", req.cr_id, self.principal)
                    req.fail(e)
                    continue
                planned.append((req, head, new))
                head = new
            pending = [p[0] for p in planned]
            if not pending:
                return
            if self.repo.update_ref(target, tip, head, user=self.principal):
                self._record(target, planned)
                self.counters["land.batches"] += 1
                self.counters["land.max_batch"] = max(self.counters["land.max_batch"], len(planned))
                for req, _, new in planned:
                    req.finish(new)
                return
            # Another server landed first: rebase the whole batch onto the new tip and retry, with
            # jittered backoff so contending servers stop colliding (FR-LD-03).
            self.counters["land.retries"] += 1
            if time.time() > deadline:
                self.counters["land.deadline"] += 1
                for req in pending:
                    req.fail(Retryable(f"could not land on {target} before the deadline; try again"))
                return
            time.sleep(random.uniform(0, min(0.25, 0.004 * 2 ** min(attempt, 6))))

    def _record(self, target: str, planned) -> None:
        """Index every landed changeset (FR-LD-05), mark CRs landed, queue post-merge jobs (FR-LD-07)."""
        now = time.time()
        rows, jobs = [], []
        for req, old_head, new in planned:
            cur = new
            while cur and cur != old_head:
                cs = self.repo.get_changeset(cur)
                rows.append((cur, cs.extra.get("rebased_from", cur), req.cr_id, target, now))
                cur = cs.first_parent
            jobs.append((new, req.cr_id, target, "queued", now))
        with self.meta.transaction() as c:
            c.executemany("INSERT OR IGNORE INTO landings (cs, source, cr, ref, landed_at) VALUES (?, ?, ?, ?, ?)", rows)
            c.executemany("INSERT INTO postmerge (cs, cr, ref, status, created) VALUES (?, ?, ?, ?, ?)", jobs)
            for req, _, new in planned:
                if req.cr_id is not None:
                    c.execute("UPDATE crs SET state = ?, head = ?, landed_cs = ?, landed_at = ?, conflict = NULL, "
                              "updated = ? WHERE id = ?", (LANDED, new, new, now, now, req.cr_id))
        self.counters["land.landed"] += len(planned)
        for req, _, new in planned:
            if req.cr_id is not None:
                self._event("cr.landed", req.cr_id, self.principal, landed_cs=new)

    def record_landing(self, cs: str, ref: str, old_tip: str | None) -> None:
        """Index changesets that reached ``ref`` outside Antique (for example an authorized direct
        compare-and-swap) and queue their post-merge job."""
        self._record(ref, [(_LandRequest(None, cs), old_tip, cs)])

    def find_landing(self, cs: str) -> dict | None:
        """When did this change land, and through which CR? An indexed lookup by the landed id or
        the pre-rebase id (FR-LD-05, UC-17)."""
        if not self.meta.has_changeset(cs):
            cs = self.repo.resolve(cs)
        row = self.meta.execute("SELECT cs, source, cr, ref, landed_at FROM landings WHERE cs = ? "
                                "UNION ALL SELECT cs, source, cr, ref, landed_at FROM landings WHERE source = ? "
                                "LIMIT 1", (cs, cs)).fetchone()
        if row is None:
            return None
        return dict(zip(("cs", "source", "cr", "ref", "landed_at"), row))

    # -- the post-merge queue (FR-LD-07; the worker is UC-18) ---------------------------------------------
    def postmerge_claim(self, worker: str) -> dict | None:
        """Claim the oldest queued job. A lost race moves on to the next job until the queue is
        empty, so concurrent workers never give up early (D-01)."""
        while True:
            row = self.meta.execute("SELECT id, cs, cr, ref FROM postmerge WHERE status = 'queued' ORDER BY id LIMIT 1"
                                    ).fetchone()
            if row is None:
                return None
            cur = self.meta.execute("UPDATE postmerge SET status = 'running', started = ?, worker = ? "
                                    "WHERE id = ? AND status = 'queued'", (time.time(), worker, row[0]))
            if cur.rowcount == 1:
                return {"id": row[0], "cs": row[1], "cr": row[2], "ref": row[3]}

    def postmerge_report(self, job_id: int, passed: bool, log: str = "") -> dict:
        cur = self.meta.execute("UPDATE postmerge SET status = ?, finished = ?, log = ? WHERE id = ? AND status = 'running'",
                                ("passed" if passed else "failed", time.time(), log[-20000:], int(job_id)))
        if cur.rowcount != 1:
            raise ValueError(f"post-merge job {job_id} is not running")
        return {"id": int(job_id), "status": "passed" if passed else "failed"}

    def postmerge_status(self, ref: str = "main", limit: int = 50) -> list[dict]:
        rows = self.meta.execute("SELECT id, cs, cr, status, created, finished FROM postmerge WHERE ref = ? "
                                 "ORDER BY id DESC LIMIT ?", (ref, int(limit))).fetchall()
        return [dict(zip(("id", "cs", "cr", "status", "created", "finished"), r)) for r in rows]

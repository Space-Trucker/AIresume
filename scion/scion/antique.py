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
import secrets
import threading
import time

from .classify import RANK, classify_diff
from .iam import PermissionDenied
from .repo import MergeConflict, NotFound, Repository

POSTMERGE_LEASE = 7200.0  # the default; a repository's policy may set review.postmerge_lease_seconds

DEFAULT_RULES = [{"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0},
                  "docs": {"approvals": 0}}]
OPEN, LANDING, LANDED, CONFLICT, ABANDONED = "open", "landing", "landed", "conflict", "abandoned"
LANDABLE = (OPEN, CONFLICT)


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
    SLOW_ATTEMPTS = 8  # a batch needing this many compare-and-swap attempts is logged as contention

    def __init__(self, repo: Repository, principal: str = "antique", notify=None, audit=None, log=None):
        self.repo, self.meta, self.principal = repo, repo.meta, principal
        self.notify = notify or (lambda event, repo, payload: None)
        self.audit = audit
        self.log = log or (lambda level, message, **fields: None)
        self.counters = {"land.requests": 0, "land.attempts": 0, "land.retries": 0, "land.landed": 0,
                         "land.conflicts": 0, "land.batches": 0, "land.max_batch": 0, "land.deadline": 0}
        self._queues: dict[str, list[_LandRequest]] = {}
        self._leaders: dict[str, threading.Lock] = {}
        self._lock = threading.Lock()

    def _count(self, key: str, n: int = 1) -> None:
        with self._lock:
            self.counters[key] += n

    def queue_depth(self) -> int:
        """Landing requests waiting on this server, over all targets (for the landing-queue superfan)."""
        with self._lock:
            return sum(len(q) for q in self._queues.values())

    @property
    def policy(self):
        return self.repo.policy

    # -- helpers ---------------------------------------------------------------------------------
    def _row(self, cr_id: int) -> dict:
        d = self.meta.cr_get(int(cr_id))
        if d is None:
            raise NotFound(f"no change request {cr_id}")
        d["conflict"] = json.loads(d["conflict"]) if d["conflict"] else None
        return d

    def _latest_rev(self, cr_id: int) -> int:
        return self.meta.cr_latest_rev(cr_id)

    def _set_state(self, cr_id: int, state: str, **cols) -> None:
        self.meta.cr_update(cr_id, state=state, updated=time.time(), **cols)

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
        cr_id = self.meta.cr_create(title, description, user, target, head, OPEN, time.time())
        self._event("cr.created", cr_id, user)
        return self.get(cr_id)

    def update(self, user: str, cr_id: int, head: str) -> dict:
        cr = self._row(cr_id)
        self._need_author_or_admin(user, cr, "upload a new revision")
        if cr["state"] not in LANDABLE:
            raise ValueError(f"change request {cr_id} is {cr['state']}")
        head = self.repo.resolve(head)
        rev = self.meta.cr_add_revision(cr_id, head, OPEN, time.time())
        self._event("cr.updated", cr_id, user, revision=rev)
        return self.get(cr_id)

    def approve(self, user: str, cr_id: int) -> dict:
        cr = self._row(cr_id)
        if cr["state"] not in LANDABLE:
            raise ValueError(f"change request {cr_id} is {cr['state']}")
        self.meta.cr_approve(cr_id, self._latest_rev(cr_id), user, time.time())
        self._event("cr.approved", cr_id, user)
        return self.get(cr_id)

    def comment(self, user: str, cr_id: int, body: str, path: str | None = None, line: int | None = None) -> dict:
        self._row(cr_id)
        if not body or not body.strip():
            raise ValueError("an empty comment")
        if line is not None and (path is None or int(line) < 1):
            raise ValueError("a line comment needs a path and a line number from 1")
        self.meta.cr_comment(cr_id, self._latest_rev(cr_id), user, path, None if line is None else int(line), body,
                             time.time())
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
        cr["revisions"] = [{"rev": r, "head": h, "created": c} for r, h, c in self.meta.cr_revisions(cr_id)]
        cr["approvals"] = [{"user": u, "rev": r} for r, u in self.meta.cr_approvals(cr_id)]
        cr["comments"] = [{"id": i, "rev": r, "user": u, "path": p, "line": ln, "body": b, "created": c}
                          for i, r, u, p, ln, b, c in self.meta.cr_comments(cr_id)]
        if with_requirements and cr["state"] in LANDABLE:
            cr["requirements"] = self.requirements(cr_id)
        return cr

    def list(self, state: str | None = None, author: str | None = None, limit: int = 50) -> list[dict]:
        return [self.get(i, with_requirements=False) for i in self.meta.cr_list(state, author, int(limit))]

    def base_of(self, cr: dict) -> str | None:
        """Where the CR's changes start: its merge base with the target."""
        tip = self.repo.get_ref(cr["target"])
        return self.repo.merge_base(cr["head"], tip) if tip else None

    def requirements(self, cr_id: int) -> dict:
        """Evaluate the approval rules for the latest revision (FR-RV-06/07)."""
        cr = self._row(cr_id)
        rev = self._latest_rev(cr_id)
        approvers = self.meta.cr_approvers(cr_id, rev)
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
        self._count("land.requests")
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
            self._count("land.attempts")
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
                    self._count("land.conflicts")
                    self.log("info", f"a landing on {target} conflicts: {e}", repo=self.repo.name,
                             cr=req.cr_id, onto=head)
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
                with self._lock:
                    self.counters["land.batches"] += 1
                    self.counters["land.max_batch"] = max(self.counters["land.max_batch"], len(planned))
                if attempt >= self.SLOW_ATTEMPTS:
                    self.log("warning", f"landing on {target} needed {attempt} attempts: other servers keep "
                                        f"moving it first", repo=self.repo.name, batch=len(planned))
                for req, _, new in planned:
                    req.finish(new)
                return
            # Another server landed first: rebase the whole batch onto the new tip and retry, with
            # jittered backoff so contending servers stop colliding (FR-LD-03).
            self._count("land.retries")
            if time.time() > deadline:
                self._count("land.deadline")
                self.log("warning", f"landing on {target} gave up at the deadline after {attempt} attempts; "
                                    f"{len(pending)} request(s) were told to retry", repo=self.repo.name)
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
                rows.append((cur, cs.extra.get("rebased_from", cur), req.cr_id, target, now, new))
                cur = cs.first_parent
            jobs.append((new, req.cr_id, target, "queued", now))
        landed = [(req.cr_id, {"state": LANDED, "head": new, "landed_cs": new, "landed_at": now, "conflict": None,
                               "updated": now}) for req, _, new in planned if req.cr_id is not None]
        self.meta.record_landings(rows, jobs, landed)
        self._count("land.landed", len(planned))
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
        return self.meta.landing_find(cs)

    def landing_stack(self, cs: str) -> list[str]:
        """Every changeset of the landing that produced ``cs``, newest first (UC-18 3a)."""
        found = self.find_landing(cs)
        if found is None:
            return []
        members = self.meta.landing_members(found["head"])
        out, cur = [], found["head"]
        while cur in members:
            out.append(cur)
            cur = self.repo.get_changeset(cur).first_parent
        return out

    # -- the post-merge queue (FR-LD-07; the worker is UC-18) ---------------------------------------------
    @property
    def postmerge_lease(self) -> float:
        """Seconds a claimed job may run without a report before it is queued again."""
        return float(self.policy.review.get("postmerge_lease_seconds", POSTMERGE_LEASE)) \
            if hasattr(self.policy, "review") else POSTMERGE_LEASE

    def postmerge_claim(self, worker: str) -> dict | None:
        """Claim the oldest queued job. A lost race moves on to the next job until the queue is
        empty, so concurrent workers never give up early (D-01). A job whose worker hasn't reported
        within the lease goes back to the queue, so a crashed worker can't leave a landing untested;
        the returned ``claim`` goes with the report, so a worker whose lease ran out can't overwrite
        the result of the worker that took the job over."""
        now = time.time()
        requeued = self.meta.postmerge_requeue(now - self.postmerge_lease)
        if requeued:
            self.log("warning", f"{requeued} post-merge job(s) went back to the queue: no report within "
                                f"{self.postmerge_lease:.0f} s", repo=self.repo.name)
        claim = f"{worker} {secrets.token_hex(8)}"
        job = self.meta.postmerge_claim(claim, now)
        return None if job is None else {**job, "claim": claim}

    def postmerge_report(self, job_id: int, passed: bool, log: str = "", claim: str | None = None) -> dict:
        if not self.meta.postmerge_report(int(job_id), "passed" if passed else "failed", time.time(), log[-20000:],
                                          claim):
            raise ValueError(f"post-merge job {job_id} is not running under this claim (its lease may have run out)")
        return {"id": int(job_id), "status": "passed" if passed else "failed"}

    def queue_stats(self) -> dict:
        """Gauges of the landing queue and the post-merge queue, for the landing-queue superfan."""
        rows = self.meta.postmerge_counts()
        return {"land.queue_depth": self.queue_depth(), "postmerge.queued": rows.get("queued", 0),
                "postmerge.running": rows.get("running", 0)}

    def postmerge_reverted(self, job_id: int, reverts: list[str]) -> dict:
        """A failed job whose landing has been reverted (06 §6.7, post-merge job)."""
        if not self.meta.postmerge_mark_reverted(int(job_id), "\nreverted by " + ", ".join(reverts)):
            raise ValueError(f"post-merge job {job_id} has not failed")
        return {"id": int(job_id), "status": "reverted", "reverts": reverts}

    def job_for(self, cs: str) -> dict | None:
        return self.meta.postmerge_job_for(cs)

    def deploy_gate(self, ref: str = "main", limit: int = 10_000) -> dict | None:
        """The newest changeset on ``ref`` whose post-merge tests passed (FR-PM-05, UC-19): it walks
        the main line from the tip and never returns a failed, reverted or untested changeset."""
        cur, steps = self.repo.get_ref(ref), 0
        while cur and steps < limit:
            job = self.job_for(cur)
            if job is not None and job["status"] == "passed":
                return {"cs": cur, "job": job["id"], "cr": job["cr"], "behind_tip": steps}
            cur = self.repo.get_changeset(cur).first_parent
            steps += 1
        return None

    def postmerge_status(self, ref: str = "main", limit: int = 50) -> list[dict]:
        return self.meta.postmerge_list(ref, int(limit))

"""Post-merge and pre-deploy testing in place of a merge queue (FR-PM-*, UC-18/19; ADR-08).

Changes land as soon as their review requirements are met. Testing happens in two places:

* **post-merge:** workers claim landed changesets from the queue atomically (FR-PM-01), test each in
  one reusable checkout that ``update`` moves by the diff (FR-PM-02), report the result with the log
  (FR-PM-03) and, optionally, revert the whole landed stack through the landing path (FR-PM-04);
* **pre-deploy:** the deploy gate returns the newest changeset on a ref whose tests passed (FR-PM-05).

A failure is reverted automatically only when the landing's base passed: on top of a failing or
untested base, the failure is not necessarily this landing's, and reverting it would be a guess.
When the base is still being tested, the decision waits for its result. A revert that can't land
(it conflicts with later work) leaves the job failed for a person to resolve; the worker goes on.
"""
from __future__ import annotations

import os
import socket
import subprocess
import time

from .client import ServerApi, WorkingCopy
from .rpc import ClientTls, RemoteError
from .tools.revert import landed_stack, revert_and_land


class PostMergeWorker:
    def __init__(self, server: str, repo: str, workdir: str, cmd: str, user: str = "postmerge",
                 objects: str | None = None, token_file: str | None = None, tls_ca: str | None = None,
                 sparse: list[str] | None = None, auto_revert: bool = False, timeout: float = 3600, log=print,
                 tls_cert: str | None = None, tls_key: str | None = None):
        token = None
        if token_file:
            with open(token_file) as f:
                token = f.read().strip()
        elif os.environ.get("SCION_TOKEN"):
            token = os.environ["SCION_TOKEN"]
        self.api = ServerApi(server, repo, user, token, ClientTls(tls_ca, tls_cert, tls_key) if tls_ca else None)
        self.server, self.repo, self.workdir, self.cmd = server, repo, workdir, cmd
        self.user, self.objects, self.token_file, self.tls_ca = user, objects, token_file, tls_ca
        self.tls_cert, self.tls_key = tls_cert, tls_key
        self.sparse, self.auto_revert, self.timeout, self.log = sparse, auto_revert, timeout, log
        self.name = f"{user}@{socket.gethostname()}:{os.getpid()}"
        self.wc: WorkingCopy | None = None
        self.undecided: list[tuple[dict, float]] = []  # failed jobs waiting on their base's result

    def close(self) -> None:
        if self.wc is not None:
            self.wc.close()
        self.api.rpc.close()

    def _checkout(self, cs: str) -> WorkingCopy:
        """One reusable checkout: later jobs fetch only what changed (FR-PM-02)."""
        if self.wc is None and os.path.isfile(os.path.join(self.workdir, ".scn", "config.json")):
            self.wc = WorkingCopy(self.workdir)
        if self.wc is None:
            self.wc = WorkingCopy.clone(self.workdir, self.server, self.repo, objects=self.objects, rev=cs,
                                        mode="sparse" if self.sparse else "full", sparse=self.sparse, user=self.user,
                                        token_file=self.token_file, tls_ca=self.tls_ca, tls_cert=self.tls_cert,
                                        tls_key=self.tls_key)
        else:
            self.wc.update(cs, clean=True)
        return self.wc

    def run_once(self) -> dict | None:
        """Claim, test and report one job; None when the queue is empty. Failures whose base has
        since been tested are decided first."""
        self._decide()
        job = self.api.call("antique.postmerge_claim")
        if job is None:
            return None
        wc = self._checkout(job["cs"])
        t0 = time.time()
        try:
            r = subprocess.run(self.cmd, shell=True, cwd=wc.root, capture_output=True, timeout=self.timeout)
            passed, output = r.returncode == 0, (r.stdout + r.stderr).decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            passed, output = False, f"timed out after {self.timeout} s"
        result = {"job": job["id"], "cs": job["cs"], "cr": job["cr"], "passed": passed,
                  "seconds": round(time.time() - t0, 3)}
        try:
            self.api.call("antique.postmerge_report", id=job["id"], passed=passed, log=output[-20000:],
                          claim=job.get("claim"))
        except RemoteError as e:
            if e.status != 400:
                raise
            self.log(f"post-merge {job['cs'][:12]}: result discarded: {e}")  # the lease ran out
            result["discarded"] = str(e)
            return result
        self.log(f"post-merge {job['cs'][:12]}: {'pass' if passed else 'FAIL'}")
        if not passed and self.auto_revert:
            self._consider_revert(job, result)
        return result

    def _consider_revert(self, job: dict, result: dict) -> bool:
        """Revert a failed landing if its base passed; wait for the base's result while it is
        being tested. Whether the job is decided."""
        base = self._base_status(job["cs"])
        if base in ("queued", "running"):
            self.undecided.append((job, time.time() + 2 * self.timeout))
            result["revert_pending"] = "its base is still being tested"
            return False
        if base != "passed":
            result["not_reverted"] = "its base had not passed post-merge testing"
            return True
        stack = landed_stack(self.api, job["cs"])
        reverts = []
        try:
            for cs in stack:  # newest first, each through the landing path
                reverts.append(revert_and_land(self.api, cs, job["ref"]))
        except RemoteError as e:  # e.g. later work conflicts with the revert: a person must resolve it
            result["revert_failed"] = str(e)
            result["reverted_with"] = reverts
            self.log(f"could not revert {job['cs'][:12]}: {e}"
                     + (f" (reverted {len(reverts)} of {len(stack)} changesets)" if reverts else ""))
            return True
        self.api.call("antique.postmerge_reverted", id=job["id"], reverts=reverts)
        result["reverted_with"] = reverts
        self.log(f"reverted {job['cs'][:12]} with {', '.join(x[:12] for x in reverts)}")
        return True

    def _decide(self) -> list[dict]:
        """Decide the failures that waited on their base, once the base has a result."""
        out, waiting, self.undecided = [], self.undecided, []
        for job, deadline in waiting:
            current = self.api.call("antique.job_for", cs=job["cs"])
            if current is None or current["id"] != job["id"] or current["status"] != "failed":
                continue  # reverted or retested meanwhile
            if self._base_status(job["cs"]) in ("queued", "running"):
                if time.time() <= deadline:
                    self.undecided.append((job, deadline))
                else:
                    self.log(f"post-merge {job['cs'][:12]}: not reverted: its base's test never finished")
                continue
            result = {"job": job["id"], "cs": job["cs"], "cr": job["cr"], "passed": False}
            self._consider_revert(job, result)
            out.append(result)
        return out

    def _base_status(self, cs: str, limit: int = 1000) -> str:
        """The post-merge status of the newest tested changeset below this landing ("passed" when
        nothing below was ever tested: the failure starts here)."""
        stack = landed_stack(self.api, cs)
        parents = self.api.get_changeset(rev=stack[-1])["parents"]
        cur = parents[0] if parents else None
        for _ in range(limit):
            if cur is None:
                return "passed"
            job = self.api.call("antique.job_for", cs=cur)
            if job is not None:
                return job["status"]
            parents = self.api.get_changeset(rev=cur)["parents"]
            cur = parents[0] if parents else None
        return "unknown"

    def run(self, once: bool = False, poll: float = 2.0) -> list[dict]:
        """Work the queue; ``once``: until it is empty and no failure waits on its base."""
        results = []
        while True:
            r = self.run_once()
            if r is not None:
                results.append(r)
                continue
            results += self._decide()
            if once and not self.undecided:
                return results
            time.sleep(poll)


def deploy_gate(api: ServerApi, ref: str = "main") -> dict | None:
    """The newest changeset on ``ref`` that passed post-merge testing (FR-PM-05)."""
    return api.call("antique.deploy_gate", ref=ref)

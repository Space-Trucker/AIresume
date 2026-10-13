"""Post-merge and pre-deploy testing in place of a merge queue.

When hundreds of changes can merge while one test run is in flight, serializing merges behind a
global lock no longer works.  Changes land as soon as review rules are satisfied (lock-free, see
``antique.land``), and testing moves to two places:

* post-merge: workers claim landed changesets from a queue, test them in a reusable checkout
  (``update`` applies only the diff since the previous job), report results, and optionally
  revert the whole landed stack through the revert pipeline;
* pre-deploy: ``deploy_gate`` picks the newest changeset whose post-merge run passed.
"""
from __future__ import annotations

import os
import socket
import subprocess
import time

from .client import ServerApi, WorkingCopy
from .tools.revert import revert_landing


def run_worker(server: str, workdir: str, cmd: str, user: str = "postmerge", objects: str | None = None,
               token: str | None = None, sparse: list[str] | None = None, once: bool = False,
               auto_revert: bool = False, poll: float = 2.0, timeout: float = 3600, log=print) -> list[dict]:
    api = ServerApi(server, user, token)
    worker = f"{user}@{socket.gethostname()}:{os.getpid()}"
    wc: WorkingCopy | None = None
    results = []
    while True:
        job = api.antique__postmerge_claim()
        if job is None:
            if once:
                return results
            time.sleep(poll)
            continue
        if wc is None:
            if os.path.isdir(os.path.join(workdir, ".scn")):
                wc = WorkingCopy(workdir)
                wc.update(job["cs"], clean=True)
            else:
                wc = WorkingCopy.clone(workdir, server, objects, rev=job["cs"],
                                       mode="sparse" if sparse else "full", sparse=sparse, user=user, token=token)
        else:
            wc.update(job["cs"], clean=True)
        t0 = time.time()
        try:
            r = subprocess.run(cmd, shell=True, cwd=wc.root, capture_output=True, timeout=timeout)
            passed = r.returncode == 0
            output = (r.stdout + r.stderr).decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            passed, output = False, f"timed out after {timeout}s"
        api.antique__postmerge_report(id=job["id"], passed=passed, log=output)
        result = {"job": job["id"], "cs": job["cs"], "passed": passed, "seconds": round(time.time() - t0, 2)}
        log(f"post-merge {job['cs'][:12]}: {'PASS' if passed else 'FAIL'}")
        if not passed and auto_revert:
            result["reverted_with"] = revert_landing(api, job["cs"], job["ref"])
            log(f"reverted {job['cs'][:12]} with {', '.join(c[:12] for c in result['reverted_with'])}")
        results.append(result)


def deploy_gate(api: ServerApi, ref: str = "main") -> dict | None:
    """The newest changeset on ``ref`` that passed post-merge testing."""
    for job in api.antique__postmerge_status(ref=ref, limit=500):
        if job["status"] == "passed" and api.is_ancestor(a=job["cs"], b=ref):
            return job
    return None

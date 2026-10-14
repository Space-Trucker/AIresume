"""The migration pilot (M4, WP-M4.1; T-PILOT-01): a real repository's history ingested in order,
verified file by file at checkpoints, and served with no client while it grows.

The checkpoints are evenly spaced commits of the main line. At each one the pilot records:

* ingestion: the commits ingested since the last checkpoint, and their rate (FR-MG-01/04);
* verification: every file of the checkpoint compared with git, kind and bytes (FR-MG-05);
* storage: the objects (count and bytes on disk) and the metadata store;
* serving with no client, from a scion-server process (M4's metadata-only service for CI): the
  latency of a log, a file's history, a blame, ancestry queries, a git lookup and a file read, with
  the steps the ancestry queries took and the server's memory;

so that the cost of each operation can be read against the size of the history (NFR-03, NFR-05,
NFR-06). It stops at the end of the history or before the disk budget runs out (R-20).

    python3 -m scion.tools.pilot --git cpython.git --root /data/pilot --checkpoints 10 --disk-budget-gb 12
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import statistics
import subprocess
import sys
import tempfile
import time

from ..deployment import Deployment
from ..ingest import GitIngester
from ..rpc import RpcClient
from .bench import _free_port, _proc

REPO = "pilot"
PROBES = ("Python/ceval.c", "Objects/object.c", "Lib/os.py", "Modules/posixmodule.c", "README")


def _git(git_dir: str, *args) -> str:
    return subprocess.run(["git", "-C", git_dir, *args], check=True, capture_output=True).stdout.decode()


def _disk(path: str) -> tuple[int, int]:
    """Files under ``path`` and the bytes they occupy on disk (blocks, not lengths)."""
    n = size = 0
    for d, _, names in os.walk(path):
        for name in names:
            n += 1
            size += os.lstat(os.path.join(d, name)).st_blocks * 512
    return n, size


def _timed(fn, runs: int = 3) -> dict:
    """The first call (it may compute and store derived data) and the median of the rest."""
    t0 = time.perf_counter()
    result = fn()
    first = time.perf_counter() - t0
    rest = []
    for _ in range(runs - 1):
        t0 = time.perf_counter()
        fn()
        rest.append(time.perf_counter() - t0)
    return {"first_ms": round(1000 * first, 2), "ms": round(1000 * statistics.median(rest or [first]), 2),
            "result": result}


def run(git_dir: str, root: str, rev: str = "main", checkpoints: int = 10, disk_budget_gb: float = 12.0,
        mainline: int | None = None, out=None) -> dict:
    """Ingest ``rev``'s history into a deployment at ``root`` (resuming what is already there),
    measuring at each checkpoint; ``mainline`` keeps only that many main-line commits. Returns the
    summary and writes one JSON line per checkpoint."""
    out = out or sys.stdout
    root = os.path.abspath(root)
    line = _git(git_dir, "rev-list", "--first-parent", "--reverse", rev).split()[:mainline or None]
    marks = sorted({line[max(0, len(line) * k // checkpoints - 1)] for k in range(1, checkpoints + 1)},
                   key=line.index)
    dep = Deployment(root)
    if REPO not in dep.names():
        dep.create_repo(REPO)
    repo = dep.repo(REPO)
    ing = GitIngester(repo, git_dir)
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    top = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log = open(os.path.join(root, "server.log"), "ab")
    server = subprocess.Popen([sys.executable, "-m", "scion", "scion-server", "--root", root, "--listen",
                               f"127.0.0.1:{port}"], stdout=log, stderr=log, env={**os.environ, "PYTHONPATH": top})
    api = RpcClient(url, user="ci", retries=3, timeout=600)
    deadline = time.time() + 30
    while True:
        try:
            api.get_json("/healthz")
            break
        except Exception:  # noqa: BLE001 - not up yet
            if time.time() > deadline or server.poll() is not None:
                raise RuntimeError("scion-server did not start; see server.log") from None
            time.sleep(0.1)
    results, stopped = [], None
    first_cs = None
    try:
        for i, sha in enumerate(marks, 1):
            t0 = time.perf_counter()
            stats = ing.ingest(sha, "main")
            seconds = time.perf_counter() - t0
            first_cs = first_cs or ing.changeset_for(line[0])
            verified = ing.verify(sha)
            tip = ing.changeset_for(sha)
            objects, object_bytes = _disk(os.path.join(dep.repo_dir(REPO), "objects"))
            meta_bytes = sum(os.path.getsize(os.path.join(dep.repo_dir(REPO), f))
                             for f in os.listdir(dep.repo_dir(REPO)) if f.startswith("meta.db"))
            n = line.index(sha) + 1

            def call(method, **p):
                return api.call(method, repo=REPO, **p)
            q = {"log_50": _timed(lambda: len(call("log", rev=tip, limit=50))),
                 "is_ancestor_first_tip": _timed(lambda: call("is_ancestor", a=first_cs, b=tip)),
                 "fp_ancestor_half": _timed(lambda: call("fp_ancestor", rev=tip, n=n // 2)),
                 "git_lookup": _timed(lambda: call("git_lookup", git=sha)["cs"] == tip)}
            for path in PROBES:
                if repo.lookup(tip, path) is None:
                    continue
                q[f"read_file {path}"] = _timed(lambda: len(call("read_file", rev=tip, path=path)["content_b64"]))
                q[f"file_history {path}"] = _timed(lambda: len(call("file_history", rev=tip, path=path, limit=20)))
                q[f"blame {path}"] = _timed(lambda: len(call("blame", rev=tip, path=path)["lines"]))
                break  # one probe file per checkpoint: the first that exists
            steps = repo.stats["ancestry.visits"] + repo.stats["ancestry.hops"]
            repo.is_ancestor(first_cs, tip)
            cpu, peak = _proc(server.pid)
            r = {"checkpoint": i, "mainline_commits": n, "commits": repo.meta.count_changesets(),
                 "ingested": stats["commits"], "ingest_s": round(seconds, 1),
                 "commits_per_s": round(stats["commits"] / seconds, 1) if seconds else None,
                 "verified": verified["ok"], "files": verified["files"], "mismatches": verified["mismatches"],
                 "objects": objects, "objects_mb": round(object_bytes / 2 ** 20, 1), "meta_mb": round(meta_bytes / 2 ** 20, 1),
                 "is_ancestor_steps": repo.stats["ancestry.visits"] + repo.stats["ancestry.hops"] - steps,
                 "ingest_peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
                 "server_peak_rss_mb": round(peak, 1), "server_cpu_s": round(cpu, 1),
                 "queries": {k: {"first_ms": v["first_ms"], "ms": v["ms"]} for k, v in q.items()}}
            results.append(r)
            print(json.dumps(r), file=out, flush=True)
            if not verified["ok"]:
                stopped = "verification failed"
                break
            if object_bytes + meta_bytes > disk_budget_gb * 2 ** 30 * (i / (i + 1)):
                stopped = f"the disk budget of {disk_budget_gb} GB would run out before the next checkpoint"
                break
    finally:
        server.terminate()
        try:
            server.wait(10)
        except subprocess.TimeoutExpired:
            server.kill()
        log.close()
        api.close_all()
        dep.close()
    return {"git": os.path.abspath(git_dir), "rev": rev, "mainline_length": len(line), "checkpoints": results,
            "stopped": stopped, "complete": stopped is None and len(results) == len(marks)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python3 -m scion.tools.pilot", description=__doc__.split("\n\n")[0])
    p.add_argument("--git", required=True, help="the git repository (a bare clone will do)")
    p.add_argument("--root", help="the pilot's deployment (default: a new temporary directory)")
    p.add_argument("--rev", default="main")
    p.add_argument("--checkpoints", type=int, default=10)
    p.add_argument("--disk-budget-gb", type=float, default=12.0)
    p.add_argument("--mainline", type=int, help="only the first N commits of the main line (and what they merged)")
    p.add_argument("--summary", help="also write the summary as JSON to this file")
    a = p.parse_args(argv)
    root = a.root or tempfile.mkdtemp(prefix="scion-pilot-")
    summary = run(a.git, root, a.rev, a.checkpoints, a.disk_budget_gb, a.mainline)
    if a.summary:
        with open(a.summary, "w") as f:
            json.dump(summary, f, indent=2)
    print(f"{len(summary['checkpoints'])} checkpoints; " + (f"stopped: {summary['stopped']}" if summary["stopped"]
                                                           else "complete"), file=sys.stderr)
    return 0 if all(c["verified"] for c in summary["checkpoints"]) else 1


if __name__ == "__main__":
    sys.exit(main())

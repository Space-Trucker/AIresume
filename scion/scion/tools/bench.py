"""Benchmarks for the scaling claims that can be reproduced on one machine (FR-OP-07; T-PERF-01).

* **Commit scaling (NFR-05):** a one-file commit, and the rebase of one onto ten newer commits, in
  repositories of 10² to 10⁴ files. Their cost follows the size of the change, so the time stays
  flat and the number of trees written is the same at every size.
* **Ancestry (NFR-06):** ``is_ancestor``, ``fp_ancestor`` and ``merge_base`` on a long linear
  history take O(log n) steps through the skip lists, where a naive walk takes n.
* **Checkouts through the tiers (NFR-02, NFR-04):** a full clone through a cold daemon and cache;
  a second clone on the same node, which the daemon answers without a single cache request; and a
  sparse checkout of one project from the warm daemon.

The numbers are measured in one process over real sockets, so they show how costs scale, not what
a fleet of machines would do.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import statistics
import sys
import tempfile
import time

from ..client import WorkingCopy
from ..deployment import Deployment
from ..repo import Repository
from ..rpc import RpcServer
from ..server import ScionService
from ..tiers import DaemonService, make_cache_service

REPO = "bench"


def _tree_path(i: int) -> str:
    return f"d{i % 100:03d}/sub{i % 7}/f{i}.txt"


def commit_scaling(root: str, sizes=(100, 1_000, 10_000), commits: int = 30) -> dict:
    """Median one-file commit and rebase times per repository size. Measurements are interleaved
    across the repositories, so background load affects every size alike."""
    repos, heads = {}, {}
    for n in sizes:
        r = repos[n] = Repository(os.path.join(root, f"commit-{n}"))
        heads[n] = r.create_changeset([], [{"path": _tree_path(i), "content": f"{i}\n".encode()} for i in range(n)],
                                      "bench", "import")
    samples = {n: {"commit": [], "rebase": [], "writes": []} for n in sizes}
    try:
        for k in range(commits):
            for n, r in repos.items():
                w = r.trees.writes
                t0 = time.perf_counter()
                heads[n] = r.create_changeset([heads[n]], [{"path": "d001/sub1/hot.txt", "content": f"{k}".encode()}],
                                              "bench", "edit")
                samples[n]["commit"].append(time.perf_counter() - t0)
                samples[n]["writes"].append(r.trees.writes - w)
        for k in range(max(3, commits // 5)):
            for n, r in repos.items():
                change = r.create_changeset([heads[n]], [{"path": f"d002/sub2/mine{k}.txt", "content": b"mine\n"}],
                                            "bench", "mine")
                tip = heads[n]
                for j in range(10):
                    tip = r.create_changeset([tip], [{"path": f"d003/sub3/theirs{k}-{j}.txt", "content": b"t\n"}],
                                             "bench", "theirs")
                heads[n] = tip
                t0 = time.perf_counter()
                r.rebase(change, tip)
                samples[n]["rebase"].append(time.perf_counter() - t0)
    finally:
        for r in repos.values():
            r.close()
    out = {}
    for n in sizes:
        s = samples[n]
        out[str(n)] = {"commit_ms": round(1000 * statistics.median(s["commit"]), 3),
                       "rebase_ms": round(1000 * statistics.median(s["rebase"]), 3),
                       "trees_written_per_commit": max(s["writes"])}
    small, large = out[str(sizes[0])], out[str(sizes[-1])]
    return {"sizes": out, "commit_ratio": round(large["commit_ms"] / max(small["commit_ms"], 1e-6), 3),
            "rebase_ratio": round(large["rebase_ms"] / max(small["rebase_ms"], 1e-6), 3)}


def ancestry(root: str, length: int = 10_000) -> dict:
    """Steps taken by ancestry queries on a linear history of ``length`` commits, against the
    ``length`` steps a parent-by-parent walk takes."""
    r = Repository(os.path.join(root, "ancestry"))
    try:
        chain = [r.create_changeset([], [{"path": "f", "content": b"0"}], "bench", "0")]
        for i in range(1, length):
            chain.append(r.create_changeset([chain[-1]], [{"path": "f", "content": str(i).encode()}], "bench", str(i)))
        side = r.create_changeset([chain[length // 2]], [{"path": "g", "content": b"side"}], "bench", "side")

        def steps(fn):
            before = r.stats["ancestry.visits"] + r.stats["ancestry.hops"]
            t0 = time.perf_counter()
            result = fn()
            return result, r.stats["ancestry.visits"] + r.stats["ancestry.hops"] - before, time.perf_counter() - t0

        anc, anc_steps, anc_t = steps(lambda: r.is_ancestor(chain[0], chain[-1]))
        not_anc, not_steps, _ = steps(lambda: r.is_ancestor(side, chain[-1]))
        back, back_steps, _ = steps(lambda: r.fp_ancestor(chain[-1], length - 1))
        base, base_steps, base_t = steps(lambda: r.merge_base(side, chain[-1]))
        if not (anc and not not_anc and back == chain[0] and base == chain[length // 2]):
            raise AssertionError("ancestry benchmark returned wrong answers")
        return {"length": length, "naive_steps": length, "log2_length": round(math.log2(length), 1),
                "is_ancestor_steps": anc_steps, "is_ancestor_ms": round(1000 * anc_t, 3),
                "not_ancestor_steps": not_steps, "fp_ancestor_steps": back_steps,
                "merge_base_steps": base_steps, "merge_base_ms": round(1000 * base_t, 3)}
    finally:
        r.close()


def checkout(root: str, files: int = 2_000, projects: int = 20) -> dict:
    """Clones through server → cache → daemon over real sockets: cold, then a second clone on the
    same node, then a sparse checkout of one project from the warm daemon."""
    dep_root = os.path.join(root, "deployment")
    setup = Deployment(dep_root)
    setup.create_repo(REPO)
    setup.close()
    sock = tempfile.mkdtemp(prefix="scn-bench-", dir="/tmp" if os.path.isdir("/tmp") else None)
    dep = Deployment(dep_root)
    svc = ScionService(dep)
    server = RpcServer(svc, "http://127.0.0.1:0").start()
    cache = make_cache_service([server.url], 256 << 20)
    cache_srv = RpcServer(cache, "http://127.0.0.1:0").start()
    daemon = DaemonService(os.path.join(root, "daemon"), [cache_srv.url], 1 << 30, refresh_seconds=3600)
    daemon_srv = RpcServer(daemon, f"unix:{sock}/d.sock").start()
    wcs = []
    try:
        repo = dep.repo(REPO)
        content = [{"path": f"project{i % projects:02d}/src/m{i // projects}/f{i}.py",
                    "content": (f"def f{i}():\n    return {i}\n" * 4).encode()} for i in range(files)]
        cs = repo.create_changeset([], content, "bench", "import")
        repo.update_ref("main", None, cs)

        def clone(name, **kw):
            served = cache.metrics.counters.get("rpc.get_objects", 0)
            t0 = time.perf_counter()
            wc = WorkingCopy.clone(os.path.join(root, name), server.url, REPO, objects=daemon_srv.url, user="bench", **kw)
            seconds = time.perf_counter() - t0
            wcs.append(wc)
            return {"seconds": round(seconds, 3), "objects": wc.fetcher.counters["fetched"],
                    "cache_requests": cache.metrics.counters.get("rpc.get_objects", 0) - served}

        cold = clone("cold")
        warm = clone("warm")
        sparse = clone("sparse", mode="sparse", sparse=["project07"])
        return {"files": files, "cold_clone": cold, "warm_clone": warm, "sparse_checkout": sparse,
                "daemon_hit_rate": daemon.source.stats()["hit_rate"],
                "clones_identical": _same_tree(wcs[0].root, wcs[1].root) and not wcs[1].status().dirty}
    finally:
        for wc in wcs:
            wc.close()
        for s in (daemon_srv, cache_srv, server):
            s.stop()
        daemon.stop()
        cache.close()
        dep.close()
        shutil.rmtree(sock, ignore_errors=True)


def _same_tree(a: str, b: str) -> bool:
    def listing(root):
        out = {}
        for d, dirs, names in os.walk(root):
            dirs[:] = [x for x in dirs if x != ".scn"]
            for n in names:
                p = os.path.join(d, n)
                with open(p, "rb") as f:
                    out[os.path.relpath(p, root)] = f.read()
        return out
    return listing(a) == listing(b)


def run(quick: bool = False, root: str | None = None) -> dict:
    """Every benchmark; ``quick`` uses sizes small enough for the test suite."""
    own = root is None
    root = root or tempfile.mkdtemp(prefix="scion-bench-")
    try:
        t0 = time.time()
        result = {
            "commit_scaling": commit_scaling(os.path.join(root, "commit"),
                                             (100, 1_000) if quick else (100, 1_000, 10_000), 15 if quick else 40),
            "ancestry": ancestry(os.path.join(root, "ancestry"), 1_000 if quick else 10_000),
            "checkout": checkout(os.path.join(root, "checkout"), 400 if quick else 5_000, 8 if quick else 20),
        }
        result["seconds"] = round(time.time() - t0, 1)
        result["quick"] = quick
        return result
    finally:
        if own:
            shutil.rmtree(root, ignore_errors=True)


def report(result: dict) -> str:
    c, a, k = result["commit_scaling"], result["ancestry"], result["checkout"]
    lines = ["Commit scaling (NFR-05): one-file commit and rebase over 10 commits, by repository size"]
    for n, v in c["sizes"].items():
        lines.append(f"  {int(n):>7,} files: commit {v['commit_ms']:8.3f} ms   rebase {v['rebase_ms']:8.3f} ms   "
                     f"trees written {v['trees_written_per_commit']}")
    lines.append(f"  largest/smallest: commit x{c['commit_ratio']}, rebase x{c['rebase_ratio']}")
    lines += [f"Ancestry (NFR-06) on a {a['length']:,}-commit line (log2 = {a['log2_length']}; a naive walk "
              f"takes {a['naive_steps']:,} steps)",
              f"  is_ancestor(root, tip): {a['is_ancestor_steps']} steps, {a['is_ancestor_ms']} ms",
              f"  is_ancestor(side branch, tip): {a['not_ancestor_steps']} steps",
              f"  fp_ancestor(tip, n-1): {a['fp_ancestor_steps']} hops",
              f"  merge_base(side branch, tip): {a['merge_base_steps']} steps, {a['merge_base_ms']} ms",
              f"Checkout through daemon → cache → server ({k['files']:,} files)"]
    for name in ("cold_clone", "warm_clone", "sparse_checkout"):
        v = k[name]
        lines.append(f"  {name.replace('_', ' '):16} {v['seconds']:7.3f} s   {v['objects']:6,} objects   "
                     f"{v['cache_requests']} cache requests")
    lines.append(f"  daemon hit rate {k['daemon_hit_rate']}; clones identical: {k['clones_identical']}")
    lines.append(f"({result['seconds']} s{', quick sizes' if result['quick'] else ''})")
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="scion-admin bench")
    p.add_argument("--quick", action="store_true", help="small sizes, for a fast check")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    result = run(quick=a.quick)
    print(json.dumps(result, indent=2) if a.json else report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

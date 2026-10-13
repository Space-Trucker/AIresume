"""Benchmarks for the scaling claims that can be reproduced locally.

1. Commit cost scales with the size of the change, not the size of the repository.
2. Ancestry queries with generation numbers + skip lists vs. a naive walk.
3. Checkout through daemon → cache → server: hit rates per tier and a warm re-checkout.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from collections import deque

from ..repo import Repository


def _naive_is_ancestor(repo: Repository, a: str, b: str) -> tuple[bool, int]:
    seen, q, visits = set(), deque([b]), 0
    while q:
        x = q.popleft()
        visits += 1
        if x == a:
            return True, visits
        for p in repo.get_changeset(x).parents:
            if p not in seen:
                seen.add(p)
                q.append(p)
    return False, visits


def bench_commit_scaling(tmp: str, sizes=(100, 1000, 10000)) -> list[dict]:
    out = []
    for n in sizes:
        repo = Repository(os.path.join(tmp, f"scale-{n}"))
        files = [{"path": f"d{i % 100:03d}/sub{i % 7}/f{i}.txt", "content": f"file {i}\n".encode()} for i in range(n)]
        root = repo.create_changeset([], files, "bench", "big initial import")
        t0 = time.perf_counter()
        cur = root
        for k in range(50):
            cur = repo.create_changeset([cur], [{"path": f"d001/sub1/f{k}.txt", "content": f"edit {k}\n".encode()}],
                                        "bench", f"edit {k}")
        dt = (time.perf_counter() - t0) / 50
        out.append({"repo_files": n, "avg_one_file_commit_ms": round(dt * 1000, 2)})
    return out


def bench_ancestry(tmp: str, length: int = 3000) -> dict:
    repo = Repository(os.path.join(tmp, "ancestry"))
    cur = repo.create_changeset([], [{"path": "f", "content": b"0"}], "bench", "root")
    root = cur
    for i in range(length):
        cur = repo.create_changeset([cur], [{"path": "f", "content": str(i).encode()}], "bench", str(i))
    repo.stats.clear()
    t0 = time.perf_counter()
    assert repo.is_ancestor(root, cur)
    fast_ms = (time.perf_counter() - t0) * 1000
    fast_visits = repo.stats["ancestry.visits"] + repo.stats["ancestry.hops"]
    t0 = time.perf_counter()
    ok, naive_visits = _naive_is_ancestor(repo, root, cur)
    naive_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    mid = repo.fp_ancestor(cur, length // 2)
    nth_ms = (time.perf_counter() - t0) * 1000
    return {"history_length": length + 1, "skiplist_ms": round(fast_ms, 3), "skiplist_steps": fast_visits,
            "naive_ms": round(naive_ms, 3), "naive_steps": naive_visits,
            "nth_ancestor_ms": round(nth_ms, 3), "nth_ok": mid is not None}


def bench_checkout(tmp: str, files: int = 2000) -> dict:
    from ..client import WorkingCopy
    from ..rpc import RpcServer
    from ..server import ScionService
    from ..tiers import DaemonService, make_cache_service

    repo = Repository(os.path.join(tmp, "co-repo"))
    cs = repo.create_changeset([], [{"path": f"pkg{i % 50}/m{i}.py", "content": (f"# module {i}\n" * 20).encode()}
                                    for i in range(files)], "bench", "import")
    repo.update_ref("main", None, cs)
    server = RpcServer(ScionService(repo), "127.0.0.1:0").start()
    cache_svc = make_cache_service([server.url], 512 * 1024 ** 2)
    cache = RpcServer(cache_svc, "127.0.0.1:0").start()
    sock = os.path.join(tmp, "daemon.sock")
    daemon_svc = DaemonService(os.path.join(tmp, "daemon-store"), [cache.url], 512 * 1024 ** 2)
    daemon = RpcServer(daemon_svc, f"unix:{sock}").start()
    try:
        res = {}
        for label in ("cold", "warm-node", "warm-node-2"):
            dest = os.path.join(tmp, f"wc-{label}")
            t0 = time.perf_counter()
            WorkingCopy.clone(dest, server.url, f"unix:{sock}", cache_bytes=10 * 1024 ** 2,
                              cache_dir=os.path.join(tmp, f"client-cache-{label}"))
            res[f"{label}_checkout_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        res["daemon"] = daemon_svc.source.stats()
        res["cache"] = cache_svc.source.stats()
        res["files"] = files
        return res
    finally:
        daemon.stop()
        cache.stop()
        server.stop()


def main() -> None:
    tmp = tempfile.mkdtemp(prefix="scion-bench-")
    try:
        print(json.dumps({"commit_scaling": bench_commit_scaling(tmp)}, indent=2))
        print(json.dumps({"ancestry": bench_ancestry(tmp)}, indent=2))
        print(json.dumps({"checkout": bench_checkout(tmp)}, indent=2))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

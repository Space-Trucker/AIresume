"""Benchmarks for the scaling claims that can be reproduced on one machine (FR-OP-07; T-PERF-01).

* **Commit scaling (NFR-05):** a one-file commit, and the rebase of one onto ten newer commits, in
  repositories of 10² to 10⁴ files. Their cost follows the size of the change, so the number of
  trees written is the same at every size and the time stays flat. Commits are timed twice: with
  objects on disk, and with objects in memory, which leaves the algorithm without the disk (whose
  speed, on a shared machine, varies with how full and busy it is).
* **Ancestry (NFR-06):** ``is_ancestor``, ``fp_ancestor`` and ``merge_base`` on a long linear
  history take O(log n) steps through the skip lists, where a naive walk takes n.
* **Checkouts through the tiers (NFR-02, NFR-04):** a full clone through a cold daemon and cache;
  a second clone on the same node, which the daemon answers without a single cache request; and a
  sparse checkout of one project from the warm daemon.
* **Against git (FR-OP-11, ADR-26; ``--vs-git``):** one git repository served both ways on this host.
  git serves it as a git server does, through ``git upload-pack`` (from a bare copy repacked with
  bitmaps, as servers keep them); Scion serves its ingested history through a server, a cache and a
  daemon, each its own process. For each checkout: the serving side's CPU time and peak memory (of
  upload-pack and pack-objects; of the Scion processes, from /proc), the wall time, and what each
  side keeps on disk. Both checkouts must produce the same files.

The numbers are measured on one machine, so they show how costs scale, not what a fleet of machines
would do.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import socket
import stat
import statistics
import subprocess
import sys
import tempfile
import time

from ..client import WorkingCopy
from ..deployment import Deployment
from ..repo import Repository
from ..rpc import RpcClient, RpcServer
from ..server import ScionService
from ..tiers import DaemonService, make_cache_service

REPO = "bench"


def _tree_path(i: int) -> str:
    return f"d{i % 100:03d}/sub{i % 7}/f{i}.txt"


def _in_memory(r: Repository) -> Repository:
    from ..storage import MemoryObjectStore
    from ..trees import TreeOps

    r.objects = MemoryObjectStore(None)
    r.trees = TreeOps(r.objects, r.cache)
    r.objects.put("tree", b"")
    return r


def commit_scaling(root: str, sizes=(100, 1_000, 10_000), commits: int = 30, memory: bool = False) -> dict:
    """Median one-file commit and rebase times per repository size. Measurements are interleaved
    across the repositories, so background load affects every size alike."""
    repos, heads = {}, {}
    for n in sizes:
        r = repos[n] = Repository(os.path.join(root, f"commit-{n}{'-mem' if memory else ''}"))
        if memory:
            _in_memory(r)
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


UPLOAD_PACK = """#!{python}
# git upload-pack as a git server runs it, with the CPU time and peak memory of it and of the
# pack-objects it starts (the waited-for children), appended to $SCION_BENCH_RUSAGE.
import json, os, resource, subprocess, sys, time
t0 = time.monotonic()
code = subprocess.call(["git", "upload-pack"] + sys.argv[1:])
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
with open(os.environ["SCION_BENCH_RUSAGE"], "a") as f:
    f.write(json.dumps({{"cpu_s": ru.ru_utime + ru.ru_stime, "peak_rss_mb": ru.ru_maxrss / 1024,
                         "seconds": time.monotonic() - t0}}) + "\\n")
sys.exit(code)
"""


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _proc(pid: int) -> tuple[float, float]:
    """CPU seconds (user + system) and peak resident memory (MB) of a running process (Linux)."""
    with open(f"/proc/{pid}/stat") as f:
        fields = f.read().rsplit(")", 1)[1].split()
    cpu = (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")
    peak = 0.0
    with open(f"/proc/{pid}/status") as f:
        for line in f:
            if line.startswith("VmHWM:"):
                peak = int(line.split()[1]) / 1024
    return cpu, peak


def _du(path: str) -> int:
    return sum(os.lstat(os.path.join(d, n)).st_size for d, _, names in os.walk(path) for n in names)


def _files(root: str, skip: str) -> dict:
    """path → (kind, SHA-256 of the bytes or the link target, executable) for a working copy,
    without its metadata."""
    out = {}
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x != skip]
        for n in names + [x for x in dirs if os.path.islink(os.path.join(d, x))]:
            p = os.path.join(d, n)
            st = os.lstat(p)
            if stat.S_ISLNK(st.st_mode):
                out[os.path.relpath(p, root)] = ("link", os.readlink(p), False)
            else:
                with open(p, "rb") as f:
                    out[os.path.relpath(p, root)] = ("file", hashlib.sha256(f.read()).hexdigest(),
                                                     bool(st.st_mode & 0o111))
    return out


def _committed(git_dir: str, rev: str) -> dict:
    """``_files`` of the tree committed at ``rev``, read from git's objects: a git checkout may
    differ from it, since .gitattributes can convert line endings and expand keywords."""
    out = {}
    listing = subprocess.run(["git", "-C", git_dir, "ls-tree", "-r", "-z", rev], check=True, capture_output=True).stdout
    cat = subprocess.Popen(["git", "-C", git_dir, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for entry in listing.split(b"\0"):
            if not entry:
                continue
            meta, path = entry.split(b"\t", 1)
            mode, otype, sha = meta.decode().split()
            if otype != "blob":
                continue  # a submodule: not monorepo content
            cat.stdin.write(sha.encode() + b"\n")
            cat.stdin.flush()
            size = int(cat.stdout.readline().split()[2])
            data = cat.stdout.read(size)
            cat.stdout.read(1)
            out[path.decode()] = ("link", data.decode(), False) if mode == "120000" else \
                ("file", hashlib.sha256(data).hexdigest(), mode == "100755")
    finally:
        cat.stdin.close()
        cat.wait()
        cat.stdout.close()
    return out


def vs_git(git_dir: str, root: str, rev: str = "HEAD", deployment: str | None = None,
           repo_name: str = REPO) -> dict:
    """Scion and git serving one repository on this host (FR-OP-11, ADR-26). ``deployment`` may
    hold the repository already ingested (as the pilot leaves it); otherwise its history is
    ingested into a new deployment first."""
    from ..ingest import GitIngester

    root = os.path.abspath(root)
    os.makedirs(root, exist_ok=True)
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}

    def git(*args, cwd=None, extra=None):
        return subprocess.run(["git", *args], cwd=cwd, env={**env, **(extra or {})}, check=True,
                              capture_output=True).stdout.decode().strip()

    # git's side: a bare copy holding the history of ``rev`` alone, as its only branch, packed with
    # bitmaps as git servers keep their repositories
    served = os.path.join(root, "served.git")
    git("clone", "-q", "--bare", "--no-local", os.path.abspath(git_dir), served)
    tip = git("-C", served, "rev-parse", f"{rev}^{{commit}}")
    for ref in git("-C", served, "for-each-ref", "--format=%(refname)").splitlines():
        git("-C", served, "update-ref", "-d", ref)
    git("-C", served, "update-ref", "refs/heads/main", tip)
    git("-C", served, "symbolic-ref", "HEAD", "refs/heads/main")
    git("-C", served, "reflog", "expire", "--expire=now", "--all")
    git("-C", served, "repack", "-q", "-a", "-d", "-b")
    wrapper = os.path.join(root, "upload-pack")
    with open(wrapper, "w") as f:
        f.write(UPLOAD_PACK.format(python=sys.executable))
    os.chmod(wrapper, 0o755)

    def git_clone(name, *flags):
        usage = os.path.join(root, f"{name}.rusage")
        t0 = time.perf_counter()
        git("clone", "-q", "--no-local", "--upload-pack", wrapper, *flags, f"file://{served}",
            os.path.join(root, name), extra={"SCION_BENCH_RUSAGE": usage})
        seconds = time.perf_counter() - t0
        with open(usage) as f:
            server = [json.loads(line) for line in f]
        return {"seconds": round(seconds, 3), "server_cpu_s": round(sum(x["cpu_s"] for x in server), 3),
                "server_peak_mb": round(max(x["peak_rss_mb"] for x in server), 1)}

    # Scion's side: the history ingested, then served by three processes
    ingested = None
    dep_root = os.path.abspath(deployment or os.path.join(root, "deployment"))
    dep = Deployment(dep_root)
    try:
        if repo_name not in dep.names():
            dep.create_repo(repo_name)
        repo = dep.repo(repo_name)
        ing = GitIngester(repo, served)
        t0 = time.perf_counter()
        if ing.changeset_for(tip) is None:
            ingested = {**ing.ingest(tip, "main"), "seconds": round(time.perf_counter() - t0, 1)}
        cs = ing.changeset_for(tip)
        if repo.get_ref("main") != cs:
            repo.update_ref("main", repo.get_ref("main"), cs)
    finally:
        dep.close()
    sock = tempfile.mkdtemp(prefix="scn-vsgit-", dir="/tmp" if os.path.isdir("/tmp") else None)
    sp, cp = _free_port(), _free_port()
    procs = {}
    logs = open(os.path.join(root, "components.log"), "ab")

    def start(name, *args, url):
        top = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # holds the package
        procs[name] = subprocess.Popen([sys.executable, "-m", "scion", *args], stdout=logs, stderr=logs,
                                       env={**os.environ, "PYTHONPATH": top})
        deadline = time.time() + 30
        while True:
            try:
                RpcClient(url, retries=0, timeout=2).get_json("/healthz")
                return
            except Exception:  # noqa: BLE001 - not up yet
                if time.time() > deadline or procs[name].poll() is not None:
                    raise RuntimeError(f"{name} did not start; see {logs.name}") from None
                time.sleep(0.1)

    wcs = []
    try:
        server_url, cache_url, daemon_url = f"http://127.0.0.1:{sp}", f"http://127.0.0.1:{cp}", f"unix:{sock}/d.sock"
        start("server", "scion-server", "--root", dep_root, "--listen", f"127.0.0.1:{sp}", url=server_url)
        start("cache", "scion-cache", "--listen", f"127.0.0.1:{cp}", "--upstream", server_url, url=cache_url)
        start("daemon", "scion-daemon", "--socket", f"{sock}/d.sock", "--store", os.path.join(root, "node"),
              "--upstream", cache_url, url=daemon_url)

        def cache_requests():
            return RpcClient(cache_url, retries=0).get_json("/stats")["counters"].get("rpc.get_objects", 0)

        def scion_clone(name, **kw):
            served = cache_requests()
            before = {n: _proc(p.pid)[0] for n, p in procs.items()}
            t0 = time.perf_counter()
            wc = WorkingCopy.clone(os.path.join(root, name), server_url, repo_name, objects=daemon_url, user="bench",
                                   **kw)
            seconds = time.perf_counter() - t0
            wcs.append(wc)
            cpu = {n: round(_proc(p.pid)[0] - before[n], 3) for n, p in procs.items()}
            return {"seconds": round(seconds, 3), "server_cpu_s": round(cpu["server"] + cpu["cache"], 3),
                    "cpu_s": cpu, "objects": wc.fetcher.counters["fetched"], "cache_requests": cache_requests() - served}

        result = {"repository": os.path.abspath(git_dir), "rev": tip,
                  "commits": int(git("-C", served, "rev-list", "--count", tip)),
                  "files": len(git("-C", served, "ls-tree", "-r", "--name-only", tip).splitlines()),
                  "ingested": ingested,
                  "git": {"full_clone": git_clone("git-full"), "shallow_clone": git_clone("git-shallow", "--depth", "1"),
                          "second_full_clone": git_clone("git-full-2"),
                          "server_disk_mb": round(_du(served) / 2 ** 20, 3)},
                  "scion": {"cold_clone": scion_clone("scion-cold"), "warm_clone": scion_clone("scion-warm")}}
        stats = {n: RpcClient(u, retries=0).get_json("/stats") for n, u in
                 (("cache", cache_url), ("daemon", daemon_url))}
        result["scion"]["peak_mb"] = {n: round(_proc(p.pid)[1], 1) for n, p in procs.items()}
        result["scion"]["cache_mb"] = round((stats["cache"]["cache"].get("bytes_cached") or 0) / 2 ** 20, 3)
        result["scion"]["daemon_disk_mb"] = round(_du(os.path.join(root, "node")) / 2 ** 20, 3)
        committed = _committed(served, tip)  # what both should hold: the bytes committed
        result["identical"] = all(_files(wc.root, ".scn") == committed for wc in wcs)
        converted = sorted(p for p, v in _files(os.path.join(root, "git-full"), ".git").items() if committed.get(p) != v)
        result["git_checkout_converted"] = {"files": len(converted), "examples": converted[:5]}  # by .gitattributes
        g, sc = result["git"], result["scion"]
        result["ratios"] = {
            "server_cpu_full_clone": _ratio(g["full_clone"]["server_cpu_s"], sc["cold_clone"]["server_cpu_s"]),
            "server_cpu_shallow_clone": _ratio(g["shallow_clone"]["server_cpu_s"], sc["cold_clone"]["server_cpu_s"]),
            "seconds_full_clone": _ratio(g["full_clone"]["seconds"], sc["warm_clone"]["seconds"]),
            "server_disk": _ratio(g["server_disk_mb"], sc["cache_mb"])}
        return result
    finally:
        for wc in wcs:
            wc.close()
        for p in procs.values():
            p.terminate()
        for p in procs.values():
            try:
                p.wait(10)
            except subprocess.TimeoutExpired:
                p.kill()
        logs.close()
        shutil.rmtree(sock, ignore_errors=True)


def _ratio(a: float, b: float):
    """How many times ``a`` is ``b`` (None when ``b`` is too small to measure)."""
    return round(a / b, 1) if b and b > 0.001 else None


def report_vs_git(r: dict) -> str:
    g, s = r["git"], r["scion"]
    lines = [f"Scion against git on {r['repository']} at {r['rev'][:12]} ({r['commits']:,} commits, "
             f"{r['files']:,} files)"]
    if r["ingested"]:
        lines.append(f"  ingested {r['ingested']['commits']:,} commits in {r['ingested']['seconds']} s")
    lines.append("  checkout               wall s   serving CPU s   serving peak MB")
    for name, v in (("git clone", g["full_clone"]), ("git clone --depth 1", g["shallow_clone"]),
                    ("git clone, again", g["second_full_clone"])):
        lines.append(f"  {name:22} {v['seconds']:7.3f}   {v['server_cpu_s']:13.3f}   {v['server_peak_mb']:15.1f}")
    peak = s["peak_mb"]
    for name, v in (("scn clone, cold", s["cold_clone"]), ("scn clone, warm node", s["warm_clone"])):
        lines.append(f"  {name:22} {v['seconds']:7.3f}   {v['server_cpu_s']:13.3f}   "
                     f"{peak['server'] + peak['cache']:15.1f}  (daemon {v['cpu_s']['daemon']:.3f} CPU s)")
    lines.append(f"  kept on disk to serve it: git {g['server_disk_mb']} MB of history; Scion cache "
                 f"{s['cache_mb']} MB in memory, node daemon {s['daemon_disk_mb']} MB")
    lines.append(f"  peak memory of the Scion processes: server {peak['server']} MB, cache {peak['cache']} MB, "
                 f"daemon {peak['daemon']} MB")
    lines.append(f"  same files both ways: {r['identical']}; git/Scion ratios: {r['ratios']}")
    return "\n".join(lines)


def run(quick: bool = False, root: str | None = None) -> dict:
    """Every benchmark; ``quick`` uses sizes small enough for the test suite."""
    own = root is None
    root = root or tempfile.mkdtemp(prefix="scion-bench-")
    try:
        t0 = time.time()
        sizes = (100, 1_000) if quick else (100, 1_000, 10_000)
        result = {
            "commit_scaling": commit_scaling(os.path.join(root, "commit"), sizes, 15 if quick else 40),
            "commit_scaling_in_memory": commit_scaling(os.path.join(root, "commit"), sizes, 15 if quick else 40,
                                                       memory=True),
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
    m = result.get("commit_scaling_in_memory")
    if m:
        lines.append("  with objects in memory (the algorithm alone): commit "
                     + " / ".join(f"{v['commit_ms']:.3f}" for v in m["sizes"].values())
                     + f" ms, largest/smallest x{m['commit_ratio']}")
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


def run_vs_git(git_dir: str, rev: str = "HEAD", deployment: str | None = None, repo_name: str = REPO) -> dict:
    """``vs_git`` in a temporary directory, removed afterwards (a given deployment is kept)."""
    root = tempfile.mkdtemp(prefix="scion-vs-git-")
    try:
        return vs_git(git_dir, root, rev, deployment, repo_name)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="scion-admin bench")
    p.add_argument("--quick", action="store_true", help="small sizes, for a fast check")
    p.add_argument("--vs-git", metavar="GIT_DIR", help="compare with git serving this repository (FR-OP-11)")
    p.add_argument("--rev", default="HEAD")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    if a.vs_git:
        result = run_vs_git(a.vs_git, a.rev)
        print(json.dumps(result, indent=2) if a.json else report_vs_git(result))
        return 0
    result = run(quick=a.quick)
    print(json.dumps(result, indent=2) if a.json else report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

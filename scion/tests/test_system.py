"""System verification of the non-functional requirements (WP-B5.1): T-SYS-01 steady-state hit rates
per tier within bounded memory (NFR-02, NFR-17), T-SYS-02 losing any tier loses no data (NFR-13), and
T-SYS-03 no component materializes the whole repository (NFR-03)."""
import base64
import os
import shutil
import tempfile
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.client import WorkingCopy
from scion.deployment import Deployment
from scion.repo import Repository
from scion.rpc import RpcServer
from scion.server import ScionService
from scion.tiers import DaemonService, make_cache_service


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def all_ids(repo, cs):
    """Every tree and blob of a revision: what a full checkout asks for."""
    ids, stack = [], [repo.root_tree(cs)]
    while stack:
        tid = stack.pop()
        ids.append(tid)
        for _, (kind, oid) in repo.trees.read(tid).items():
            (stack.append if kind == "d" else ids.append)(oid)
    return ids


class TestSteadyState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-sys-")
        self.c = Cluster(self.tmp, caches=1, daemons=0, cache_bytes=8 << 20)
        files = [{"path": f"p{i % 12}/m{i % 5}/f{i}.py", "content_b64": b64(f"v = {i}\n".encode() * 8)}
                 for i in range(300)]
        api = self.c.client("root")
        self.v1 = api.call("create_changeset", repo=REPO, parents=[], message="v1", files=files,
                           update_ref={"name": "main", "old": None})["id"]
        # a small change, as main moves on between checkouts
        self.v2 = api.call("create_changeset", repo=REPO, parents=[self.v1], message="v2",
                           files=[{"path": "p3/m1/f3.py", "content_b64": b64(b"v = 'changed'\n")}],
                           update_ref={"name": "main", "old": self.v1})["id"]
        self.daemons = []

    def tearDown(self):
        for d in self.daemons:
            d.stop()
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def daemon(self, i, max_bytes=4 << 20):
        d = DaemonService(os.path.join(self.tmp, f"node{i}"), self.c.cache_urls, max_bytes, refresh_seconds=3600)
        self.daemons.append(d)
        return d

    def test_T_SYS_01_steady_state_hit_rates_per_tier_within_bounded_memory(self):
        repo = self.c.repo()
        v1, v2 = all_ids(repo, self.v1), all_ids(repo, self.v2)
        # one node, 100 jobs: each checks out v1, then main moves and each updates to v2
        node = self.daemon(0)
        for _ in range(100):
            node.source.fetch(REPO, v1, "job")
        for _ in range(100):
            node.source.fetch(REPO, v2, "job")
        s = node.source.stats()
        self.assertGreaterEqual(s["hit_rate"], 0.99, s)  # NFR-02: the node serves its jobs
        self.assertEqual(s["misses"], len(set(v1) | set(v2)))  # each object crossed the node boundary once
        # 100 more nodes behind the same regional cache, one checkout each: over its whole life, cold
        # start included, the cache fetched each object from the servers once
        cache = self.c.cache_services[0].source
        for i in range(1, 101):
            self.daemon(i).source.fetch(REPO, v2, "job")
        hits, misses = cache.counters["hits"], cache.counters["misses"]
        self.assertEqual(misses, len(set(v1) | set(v2)))
        self.assertGreaterEqual(hits / (hits + misses), 0.99, (hits, misses))  # NFR-02 at the cache tier
        # NFR-17: every store stays within its configured size, in MB, however many objects pass through
        self.assertLessEqual(cache.store.size_bytes, 8 << 20)
        self.assertTrue(all(d.source.store.size_bytes <= 4 << 20 for d in self.daemons))
        small = self.daemon(999, max_bytes=20_000)
        small.source.fetch(REPO, v1, "job")
        self.assertLessEqual(small.source.store.size_bytes, 20_000)
        self.assertGreater(small.source.stats()["evictions"], 0)
        print(f"\n  steady state: node hit rate {s['hit_rate']:.4f} over 200 checkouts of {len(v1)} objects; "
              f"cache hit rate {hits / (hits + misses):.4f} over 100 nodes; cache {cache.store.size_bytes:,} bytes")


class TestDurability(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-dur-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T_SYS_02_losing_any_tier_loses_no_data(self):
        c = Cluster(self.tmp, servers=2)
        try:
            api = c.client("root")
            files = [{"path": f"d{i % 7}/f{i}.txt", "content_b64": b64(f"{i}\n".encode())} for i in range(120)]
            tip = api.call("create_changeset", repo=REPO, parents=[], message="m", files=files,
                           update_ref={"name": "main", "old": None})["id"]
            first = WorkingCopy.clone(os.path.join(self.tmp, "wc1"), ",".join(c.server_urls), REPO,
                                      objects=c.daemon_urls[0], user="u")
            first.close()
            # lose the node daemon with its disk store, the regional cache with its memory, and a server
            c.daemons[0].stop()
            c.daemon_services[0].stop()
            shutil.rmtree(os.path.join(self.tmp, "daemon0"))
            c.caches[0].stop()
            c.cache_services[0].close()
            c.servers[0].stop()
            cache = make_cache_service([c.server_urls[1]], 64 << 20)
            cache_srv = RpcServer(cache, "http://127.0.0.1:0").start()
            daemon = DaemonService(os.path.join(self.tmp, "daemon-new"), [cache_srv.url], 64 << 20)
            daemon_srv = RpcServer(daemon, f"unix:{c.sockdir}/new.sock").start()
            try:
                second = WorkingCopy.clone(os.path.join(self.tmp, "wc2"), c.server_urls[1], REPO,
                                           objects=daemon_srv.url, user="u")
                second.close()
                self.assertEqual(self.tree(os.path.join(self.tmp, "wc1")), self.tree(os.path.join(self.tmp, "wc2")))
                self.assertEqual(c.client("u", url=c.server_urls[1]).call("resolve", repo=REPO, rev="main"), tip)
            finally:
                daemon_srv.stop()
                daemon.stop()
                cache_srv.stop()
                cache.close()
            # a server process holds nothing either: a new one on the same storage serves everything
            dep = Deployment(c.dep_root)
            fresh = RpcServer(ScionService(dep), "http://127.0.0.1:0").start()
            try:
                self.assertEqual(c.client("u", url=fresh.url).call("resolve", repo=REPO, rev="main"), tip)
                self.assertEqual(c.client("u", url=fresh.url).call("read_file", repo=REPO, rev="main",
                                                                   path="d3/f3.txt")["content_b64"], b64(b"3\n"))
            finally:
                fresh.stop()
                dep.close()
        finally:
            c.close()

    @staticmethod
    def tree(root):
        out = {}
        for d, dirs, names in os.walk(root):
            dirs[:] = [x for x in dirs if x != ".scn"]
            for n in names:
                with open(os.path.join(d, n), "rb") as f:
                    out[os.path.relpath(os.path.join(d, n), root)] = f.read()
        return out


def count_reads(store) -> list:
    """Count every object read from ``store`` (all reads go through ``get_stored``)."""
    reads, original = [0], store.get_stored

    def counting(oid):
        reads[0] += 1
        return original(oid)

    store.get_stored = counting
    return reads


class TestNothingMaterializesEverything(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-size-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def reads_for_queries(self, n):
        """Storage reads to answer path queries on a repository of ``n`` files, with cold caches."""
        root = os.path.join(self.tmp, f"r{n}")
        r = Repository(root)
        head = r.create_changeset([], [{"path": f"d{i % 50:02d}/s{i % 9}/f{i}.txt", "content": f"{i}\n".encode()}
                                       for i in range(n)], "a", "import")
        for k in range(5):  # history for the file the queries are about
            head = r.create_changeset([head], [{"path": "d07/s3/hot.txt", "content": f"line {k}\n".encode() * (k + 1)}],
                                      "a", f"edit {k}")
        r.blame(head, "d07/s3/hot.txt")  # derive once; the measurement is of answering, not deriving
        r.close()
        r = Repository(root)  # cold: nothing decoded in memory
        try:
            reads = count_reads(r.objects)
            r.read_file(head, "d07/s3/hot.txt")
            r.list_dir(head, "d07/s3")
            r.file_history(head, "d07/s3/hot.txt")
            r.blame(head, "d07/s3/hot.txt")
            r.diff(r.get_changeset(head).first_parent, head)
            return reads[0]
        finally:
            r.close()

    def test_T_SYS_03_query_cost_does_not_grow_with_the_repository(self):
        """NFR-03: no component needs the whole repository. A server answers path queries by reading
        the objects along the path, so a repository 20 times larger costs the same reads; a sparse
        checkout fetches its directories and the trees above them, not the rest."""
        small, large = self.reads_for_queries(500), self.reads_for_queries(10_000)
        self.assertLessEqual(large, small + 5, (small, large))
        self.assertLess(large, 100)
        print(f"\n  path queries: {small} object reads at 500 files, {large} at 10,000 files")

        c = Cluster(os.path.join(self.tmp, "cluster"))
        try:
            files = [{"path": f"proj{i % 40:02d}/src/f{i}.py", "content_b64": b64(f"x = {i}\n".encode())}
                     for i in range(4000)]
            c.client("root").call("create_changeset", repo=REPO, parents=[], message="m", files=files,
                                  update_ref={"name": "main", "old": None})
            wc = WorkingCopy.clone(os.path.join(self.tmp, "sparse"), c.server_urls[0], REPO,
                                   objects=c.daemon_urls[0], user="u", mode="sparse", sparse=["proj07"])
            try:
                fetched = wc.fetcher.counters["fetched"]
                self.assertEqual(sum(1 for _ in os.scandir(os.path.join(wc.root, "proj07", "src"))), 100)
                self.assertLessEqual(fetched, 100 + 3)  # 100 files plus the root, proj07 and src trees
                print(f"  sparse checkout of 1 of 40 projects: {fetched} objects of {4000 + 81}")
            finally:
                wc.close()
        finally:
            c.close()


if __name__ == "__main__":
    unittest.main()

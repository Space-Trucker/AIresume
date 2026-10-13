"""T-TIER-01…08: the object protocol through scion-daemon → scion-cache → scion-server (WP-B2.3)."""
import base64
import os
import shutil
import tempfile
import threading
import time
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.client import ClientError, WorkingCopy
from scion.objects import F_MISSING, F_RESTRICTED, encode_stored, object_id
from scion.rpc import RemoteError, RpcClient, RpcServer
from scion.snapshot import create_snapshot, latest_snapshot
from scion.tiers import CachingSource, DaemonService, ObjectSource, ObjectTierService
from scion.storage import MemoryObjectStore, ns_key


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def seed(cluster, n_dirs=4, n_files=6, user="alice", rev=None, tag="v1"):
    api = cluster.client(user)
    files = [{"path": f"src/d{i}/f{j}.txt", "content_b64": b64(f"{tag} {i} {j}\n")}
             for i in range(n_dirs) for j in range(n_files)]
    parents = [rev] if rev else []
    old = rev
    r = api.call("create_changeset", repo=REPO, parents=parents, message=tag, files=files,
                 update_ref={"name": "main", "old": old})
    assert r["ref_updated"], r
    return r["id"]


class TierTest(unittest.TestCase):
    cluster_args: dict = {}

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-tiers-")
        self.c = Cluster(self.tmp, **self.cluster_args)

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def clone(self, name, daemon=0, **kw):
        return WorkingCopy.clone(os.path.join(self.tmp, name), self.c.server_urls[0], REPO,
                                 objects=self.c.daemon_urls[daemon], user=kw.pop("user", "alice"), **kw)

    def server_object_requests(self):
        return sum(s.metrics.counters.get("rpc.get_objects", 0) for s in self.c.services)


class TestThroughTheTiers(TierTest):
    cluster_args = {"daemons": 2}

    def test_T_TIER_01_second_job_on_a_node_needs_no_cache_traffic(self):
        seed(self.c)
        cache = self.c.cache_services[0].source
        a = self.clone("job-a")
        self.assertEqual(len(os.listdir(os.path.join(self.tmp, "job-a", "src"))), 4)
        after_a = dict(cache.counters)
        server_after_a = self.server_object_requests()
        # FR-TIER-06: each cache miss batch is one upstream request
        self.assertEqual(after_a["upstream_requests"], server_after_a)
        self.assertEqual(server_after_a, len(a.fetcher.log))

        b = self.clone("job-b")  # FR-TIER-01: a second job on the same node
        self.assertEqual(dict(cache.counters), after_a, "the second checkout must not reach the cache")
        self.assertEqual(b.fetcher.counters["fetched"], a.fetcher.counters["fetched"])
        self.assertEqual(self.c.daemon_services[0].source.stats()["hit_rate"], 0.5)

        c = self.clone("job-c", daemon=1)  # FR-TIER-05: another node is served from the cache's memory
        self.assertEqual(self.server_object_requests(), server_after_a)
        self.assertEqual(cache.counters["hits"], after_a["misses"])
        self.assertEqual(c.fetcher.counters["fetched"], a.fetcher.counters["fetched"])
        for wc in (a, b, c):
            wc.close()

    def test_T_TIER_02_identical_rpc_on_every_tier(self):
        seed(self.c)
        repo = self.c.repo()
        root = repo.root_tree(repo.resolve("main"))
        ids = [root] + [oid for _, (k, oid) in repo.trees.read(root).items()]
        daemon = self.c.client("alice", url=self.c.daemon_urls[0])
        cache = self.c.client("scion-daemon", url=self.c.cache_urls[0], tier="daemon")
        server = self.c.client("scion-cache", tier="cache")
        answers = [x.get_objects(REPO, ids, on_behalf=None) for x in (daemon, cache, server)]
        self.assertEqual(answers[0], answers[1])
        self.assertEqual(answers[1], answers[2])
        # FR-FP-06: stored bytes travel unchanged, exactly as blob storage holds them
        for oid, flags, stored in answers[0]:
            self.assertEqual(flags, 0)
            self.assertEqual(stored, repo.objects.get_stored(oid))
        # FR-FP-01: the request format has no "have" field; asking twice is the same request
        self.assertEqual(daemon.get_objects(REPO, ids), answers[0])

    def test_T_TIER_03_strict_tiering(self):
        seed(self.c)
        root = self.c.repo().root_tree(self.c.repo().resolve("main"))
        refusals = {
            "client to cache": self.c.client("alice", url=self.c.cache_urls[0]),
            "daemon to server": self.c.client("scion-daemon", tier="daemon"),
            "client to server": self.c.client("alice"),
        }
        for what, client in refusals.items():
            with self.subTest(what), self.assertRaises(RemoteError) as e:
                client.get_objects(REPO, [root])
            self.assertEqual(e.exception.status, 403, what)
        with self.assertRaises(RemoteError) as e:  # a user claiming to be the cache tier
            self.c.client("mallory", tier="cache").get_objects(REPO, [root])
        self.assertEqual((e.exception.status, e.exception.code), (403, "bad_tier"))
        # FR-TIER-04: a daemon pointed at a server instead of a cache refuses to use it
        bad = DaemonService(os.path.join(self.tmp, "bad"), self.c.server_urls, 1 << 20)
        srv = RpcServer(bad, f"unix:{self.c.sockdir}/bad.sock").start()
        try:
            with self.assertRaises(RemoteError) as e:
                self.c.client("alice", url=srv.url).get_objects(REPO, [root])
            self.assertEqual((e.exception.status, e.exception.code), (502, "bad_upstream"))
        finally:
            srv.stop()
        self.assertGreaterEqual(self.c.cache_services[0].metrics.counters["tiering.rejected"], 1)

    def test_T_TIER_04_derived_objects_are_not_served(self):
        seed(self.c)
        repo = self.c.repo()
        cs = repo.resolve("main")
        internal = [repo.history_root(cs), repo.search_root(cs)]
        got = self.c.client("alice", url=self.c.daemon_urls[0]).get_objects(REPO, internal)
        self.assertEqual([f for _, f, _ in got], [F_MISSING, F_MISSING])
        self.assertTrue(all(repo.objects.has(i) for i in internal))


class TestSnapshots(TierTest):
    cluster_args = {"daemons": 0}

    def test_T_TIER_05_snapshot_warm_start_and_refresh(self):
        v1 = seed(self.c)
        snaps = os.path.join(self.tmp, "snapshots")
        p1 = create_snapshot(self.c.repo(), "main", os.path.join(snaps, REPO))
        self.assertEqual(latest_snapshot(os.path.join(snaps, REPO))["file"], p1["file"])
        daemon = DaemonService(os.path.join(self.tmp, "fresh"), self.c.cache_urls, 64 << 20, snapshot_dir=snaps,
                               refresh_seconds=3600)
        srv = RpcServer(daemon, f"unix:{self.c.sockdir}/fresh.sock").start()
        try:
            self.assertEqual(daemon.snapshot_objects, p1["objects"])
            wc = WorkingCopy.clone(os.path.join(self.tmp, "wc"), self.c.server_urls[0], REPO, objects=srv.url,
                                   user="alice")
            self.assertEqual(daemon.source.counters["upstream_requests"], 0, "served entirely from the snapshot")
            self.assertEqual(self.c.cache_services[0].source.counters["misses"], 0)
            # a newer snapshot is imported by the refresh, and only the new objects are added
            r = self.c.client("alice").call("create_changeset", repo=REPO, parents=[v1], message="v2",
                                            files=[{"path": "src/d0/f0.txt", "content_b64": b64("changed\n")},
                                                   {"path": "src/new.txt", "content_b64": b64("new\n")}],
                                            update_ref={"name": "main", "old": v1})
            self.assertTrue(r["ref_updated"])
            p2 = create_snapshot(self.c.repo(), "main", os.path.join(snaps, REPO))
            self.assertNotEqual(p2["file"], p1["file"])
            imported = daemon.refresh_snapshots()
            self.assertGreater(imported, 0)
            self.assertLess(imported, p2["objects"])
            self.assertEqual(daemon.refresh_snapshots(), 0)
            wc.update("main")
            self.assertEqual(daemon.source.counters["upstream_requests"], 0)
            wc.close()
        finally:
            srv.stop()
            daemon.stop()

    def test_private_repositories_are_never_snapshotted(self):
        dep = self.c.deployment
        dep.create_repo("secret-repo", {"read": ["alice"], "write": ["alice"]})
        repo = dep.repo("secret-repo")
        repo.create_changeset([], [{"path": "x", "content": b"x"}], "alice", "m")
        repo.update_ref("main", None, repo.resolve(repo.meta.tail()[-1][1]))
        with self.assertRaises(ValueError):
            create_snapshot(repo, "main", os.path.join(self.tmp, "s"))


class TestFailover(TierTest):
    cluster_args = {"servers": 2, "caches": 2}

    def test_T_TIER_06_failover_between_servers_and_caches(self):
        seed(self.c)
        self.c.servers[0].stop()
        self.c.caches[0].stop()
        # FR-TIER-09: one of two servers and one of two caches down; the client knows both servers
        wc = WorkingCopy.clone(os.path.join(self.tmp, "wc"), ",".join(self.c.server_urls), REPO,
                               objects=self.c.daemon_urls[0], user="alice")
        self.assertEqual(len(wc.status().to_dict()["modified"]), 0)
        self.assertEqual(sum(len(os.listdir(os.path.join(self.tmp, "wc", "src", d)))
                             for d in os.listdir(os.path.join(self.tmp, "wc", "src"))), 24)
        self.assertGreaterEqual(self.c.daemon_services[0].source.upstream.failovers, 1)
        self.assertGreaterEqual(sum(c.source.upstream.failovers for c in self.c.cache_services), 1)
        self.assertGreaterEqual(wc.api.rpc.failovers, 1)
        wc.close()


class _SlowSource(ObjectSource):
    def __init__(self, objects, delay=0.2):
        self.objects, self.delay, self.calls = objects, delay, 0
        self.lock = threading.Lock()

    def fetch(self, repo, ids, user):
        with self.lock:
            self.calls += 1
        time.sleep(self.delay)
        return [(oid, 0, self.objects[oid]) for oid in ids]


class TestSingleFlightAndIntegrity(unittest.TestCase):
    def test_T_TIER_07_single_flight(self):
        payload = b"hot object"
        oid = object_id("blob", payload)
        upstream = _SlowSource({oid: encode_stored("blob", payload)})
        cache = CachingSource(MemoryObjectStore(), upstream)
        results, barrier = [], threading.Barrier(10)

        def worker():
            barrier.wait()
            results.append(cache.fetch(REPO, [oid], "alice"))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(upstream.calls, 1, "ten concurrent misses for one id must be one upstream call")
        self.assertEqual(len(results), 10)
        self.assertTrue(all(r[0][2] == encode_stored("blob", payload) for r in results))
        self.assertEqual(cache.counters["coalesced"], 9)

    def test_restricted_objects_are_passed_through_not_cached(self):
        payload = b"secret"
        oid = object_id("blob", payload)

        class Restricted(_SlowSource):
            def fetch(self, repo, ids, user):
                return [(o, F_RESTRICTED, b) for o, _, b in super().fetch(repo, ids, user)]

        upstream = Restricted({oid: encode_stored("blob", payload)}, delay=0)
        store = MemoryObjectStore()
        cache = CachingSource(store, upstream)
        for _ in range(3):
            self.assertEqual(cache.fetch(REPO, [oid], "alice")[0][1], F_RESTRICTED)
        self.assertFalse(store.has(ns_key(REPO, oid)))
        self.assertEqual(upstream.calls, 3, "every request for a restricted object reaches upstream")

    def test_T_TIER_08_forged_objects_are_rejected(self):
        real = encode_stored("blob", b"real content")
        forged = encode_stored("blob", b"forged content")
        oid = object_id("blob", b"real content")
        evil_cache = ObjectTierService("cache", CachingSource(MemoryObjectStore(), _SlowSource({oid: forged}, 0)),
                                       ("daemon",))
        tmp = tempfile.mkdtemp(prefix="scion-forge-")
        sock = helpers.short_tmpdir()
        evil = RpcServer(evil_cache, "http://127.0.0.1:0").start()
        evil_cache.register("tier_info", lambda c, p: {"tier": "cache"})
        daemon = DaemonService(os.path.join(tmp, "d"), [evil.url], 1 << 20)
        dsrv = RpcServer(daemon, f"unix:{sock}/d.sock").start()
        try:
            with self.assertRaises(RemoteError) as e:
                RpcClient(dsrv.url, user="alice").get_objects(REPO, [oid])
            self.assertEqual((e.exception.status, e.exception.code), (502, "integrity"))
            self.assertFalse(daemon.source.store.has(ns_key(REPO, oid)))
            self.assertEqual(daemon.source.counters["rejected_objects"], 1)
            # the client verifies too (FR-OBJ-04): an object endpoint that lies is caught there
            from scion.client import ObjectFetcher
            fetcher = ObjectFetcher(evil.url, REPO, MemoryObjectStore(), user="scion-daemon")
            fetcher.rpc.tier = "daemon"
            with self.assertRaises(ClientError):
                fetcher.blob(oid)
            self.assertNotEqual(real, forged)
        finally:
            dsrv.stop()
            evil.stop()
            shutil.rmtree(tmp, ignore_errors=True)
            shutil.rmtree(sock, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

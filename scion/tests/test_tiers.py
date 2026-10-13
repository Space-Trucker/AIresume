import os
import threading
import time
import unittest

from helpers import MB, Cluster, read
from scion.objects import encode_stored, object_id
from scion.rpc import RemoteError, RpcClient
from scion.snapshot import create_snapshot
from scion.storage import MemoryObjectStore
from scion.tiers import CachingSource, ObjectSource


class TestCheckoutArchitecture(unittest.TestCase):
    def setUp(self):
        self.c = Cluster()
        files = {f"pkg{i % 5}/mod{i}.py": f"# module {i}\nx = {i}\n".encode() for i in range(60)}
        files["README.md"] = b"hello\n"
        self.c.seed(files)

    def tearDown(self):
        self.c.close()

    def test_clone_through_daemon_cache_server(self):
        wc = self.c.clone("wc1")
        self.assertEqual(read(wc, "pkg3/mod3.py"), b"# module 3\nx = 3\n")
        d = self.c.daemon_svc.source.stats()
        self.assertGreater(d["misses"], 0)
        # A second job on the same node is served entirely by the daemon.
        before = dict(self.c.cache_svc.source.counters)
        wc2 = self.c.clone("wc2")
        self.assertEqual(read(wc2, "README.md"), b"hello\n")
        self.assertEqual(dict(self.c.cache_svc.source.counters), before)
        self.assertGreater(self.c.daemon_svc.source.stats()["hit_rate"], 0.45)
        # A second node misses its daemon but hits the regional cache.
        _, url = self.c.add_daemon()
        upstream_before = self.c.service.metrics.counters.get("rpc.get_objects", 0)
        self.c.clone("wc3", daemon=1)
        self.assertEqual(self.c.service.metrics.counters.get("rpc.get_objects", 0), upstream_before)
        self.assertGreater(self.c.cache_svc.source.stats()["hits"], 0)

    def test_identical_rpc_on_every_tier(self):
        oid = self.c.repo.trees.lookup(self.c.repo.root_tree(self.c.repo.resolve("main")), "README.md")[1]
        daemon = RpcClient(self.c.objects_url, user="alice")
        cache = RpcClient(self.c.cache.url, user="scion-daemon", tier="daemon")
        server = RpcClient(self.c.server.url, user="scion-cache", tier="cache")
        results = [cl.get_objects([oid], on_behalf="alice" if cl is not daemon else None)
                   for cl in (daemon, cache, server)]
        self.assertTrue(all(r == results[0] for r in results))

    def test_tiering_is_enforced(self):
        oid = self.c.repo.root_tree(self.c.repo.resolve("main"))
        with self.assertRaises(RemoteError) as cm:  # client skipping its daemon
            RpcClient(self.c.cache.url, user="alice").get_objects([oid])
        self.assertEqual(cm.exception.status, 403)
        with self.assertRaises(RemoteError) as cm:  # daemon skipping the cache
            RpcClient(self.c.server.url, user="scion-daemon", tier="daemon").get_objects([oid])
        self.assertEqual(cm.exception.status, 403)
        with self.assertRaises(RemoteError) as cm:  # a user pretending to be a cache
            RpcClient(self.c.server.url, user="mallory", tier="cache").get_objects([oid])
        self.assertEqual(cm.exception.status, 403)
        self.assertGreater(self.c.service.metrics.counters["tiering.rejected"], 0)

    def test_internal_derived_objects_are_not_served(self):
        cs = self.c.repo.resolve("main")
        htree = self.c.repo.history_root(cs)
        res = RpcClient(self.c.objects_url, user="alice").get_objects([htree])
        self.assertTrue(res[0][1] & 0x2)  # missing: clients never see derived internals

    def test_snapshot_warm_start(self):
        snapdir = os.path.join(self.c.tmp, "snapshots")
        create_snapshot(self.c.repo, "main", snapdir)
        svc, url = self.c.add_daemon(snapshot_dir=snapdir)
        self.assertGreater(svc.snapshot_objects, 60)
        before = self.c.cache_svc.source.counters.get("upstream_requests", 0) + \
            self.c.cache_svc.source.counters.get("hits", 0)
        from scion.client import WorkingCopy
        WorkingCopy.clone(os.path.join(self.c.tmp, "wcs"), self.c.server.url, url, user="alice",
                          cache_dir=os.path.join(self.c.tmp, "cc"))
        after = self.c.cache_svc.source.counters.get("upstream_requests", 0) + \
            self.c.cache_svc.source.counters.get("hits", 0)
        self.assertEqual(before, after, "a snapshot-seeded daemon should not need the cache for main")
        # The snapshot is periodically refreshed: a newer one gets imported.
        self.c.seed({"new.txt": b"new\n"})
        create_snapshot(self.c.repo, "main", snapdir)
        self.assertGreater(svc.refresh_snapshot(), 0)

    def test_failover_between_servers(self):
        c = Cluster(servers=2)
        try:
            c.seed({"a.txt": b"a\n", "b/c.txt": b"c\n"})
            c.servers[0].stop()  # the cache must fail over to the second server
            from scion.client import WorkingCopy
            wc = WorkingCopy.clone(os.path.join(c.tmp, "wcf"), c.servers[1].url, c.objects_url, user="alice")
            self.assertEqual(read(wc, "b/c.txt"), b"c\n")
            self.assertGreater(c.cache_svc.source.upstream.failovers, 0)
        finally:
            c.close()


class SlowSource(ObjectSource):
    def __init__(self, objects):
        self.objects = objects
        self.calls = 0

    def fetch(self, ids, user):
        self.calls += 1
        time.sleep(0.2)
        return [(i, 0, self.objects[i]) for i in ids]


class TestCachingSource(unittest.TestCase):
    def test_single_flight(self):
        stored = encode_stored("blob", b"x")
        oid = object_id("blob", b"x")
        up = SlowSource({oid: stored})
        cache = CachingSource(MemoryObjectStore(MB), up)
        threads = [threading.Thread(target=cache.fetch, args=([oid], None)) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(up.calls, 1)
        self.assertEqual(cache.counters["coalesced"], 9)

    def test_integrity_verification(self):
        oid = object_id("blob", b"real")
        up = SlowSource({oid: encode_stored("blob", b"forged")})
        cache = CachingSource(MemoryObjectStore(MB), up, verify=True)
        with self.assertRaises(Exception):
            cache.fetch([oid], None)
        self.assertFalse(cache.store.has(oid))


if __name__ == "__main__":
    unittest.main()

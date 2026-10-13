import base64
import os
import shutil
import tempfile
import threading
import time
import unittest

from helpers import Cluster
from scion.client import ServerApi
from scion.ratelimit import RateLimited, RateLimiter
from scion.repo import Repository
from scion.rpc import RemoteError, RpcClient
from scion.search import grep, search_paths
from scion.superfan import Superfan
from scion.tools.bisect import bisect, file_matches
from scion.tools.revert import revert_and_land


class TestRateLimiting(unittest.TestCase):
    def test_token_bucket_and_concurrency(self):
        rl = RateLimiter({"default": {"heavy": {"rate": 1, "burst": 1, "concurrency": 1}}})
        with rl.acquire("u", "heavy"):
            with self.assertRaises(RateLimited):  # second concurrent heavy request
                with rl.acquire("u", "heavy"):
                    pass
        with self.assertRaises(RateLimited) as cm:
            with rl.acquire("u", "heavy"):
                pass
        self.assertGreater(cm.exception.retry_after, 0)
        with rl.acquire("v", "heavy"):  # other principals are unaffected
            pass

    def test_server_returns_429_and_client_backs_off(self):
        c = Cluster(policy={"rate_limits": {"default": {"heavy": {"rate": 5, "burst": 1}}}})
        try:
            c.seed({"a.py": b"x = 1\n"})
            api = ServerApi(c.server.url, "busy")
            t0 = time.time()
            for _ in range(4):
                api.search_paths(rev="main", query="a")  # the client honors Retry-After and succeeds
            self.assertGreater(time.time() - t0, 0.4)
            self.assertGreater(c.service.limiter.rejections, 0)
            raw = RpcClient(c.server.url, user="busy2")
            raw.call("search_paths", rev="main", query="a")
            status, headers, _ = raw.request("POST", "/rpc/search_paths", b'{"params":{"rev":"main","query":"a"}}')
            self.assertEqual(status, 200)  # the client retried transparently after a 429
        finally:
            c.close()


class TestSuperfan(unittest.TestCase):
    def test_detects_novel_regressions_and_thresholds(self):
        fan = Superfan("scion-cache", "http://127.0.0.1:1", rules=[{"metric": "cache.hit_rate_interval", "below": 0.9}])
        hits = misses = 0
        findings = []
        for i in range(30):
            hits += 990
            misses += 10
            findings += fan.observe({"cache": {"hits": hits, "misses": misses}}, now=1000 + i)
        self.assertEqual(findings, [])
        hits += 500
        misses += 500  # the hit rate collapses
        f = fan.observe({"cache": {"hits": hits, "misses": misses}}, now=1031)
        kinds = {(x["kind"], x["metric"]) for x in f}
        self.assertIn(("threshold", "cache.hit_rate_interval"), kinds)
        self.assertIn(("novel", "cache.hit_rate_interval"), kinds)

    def test_watches_a_live_component(self):
        c = Cluster()
        try:
            c.seed({"x": b"1"})
            fan = Superfan("scion-server", c.server.url)
            self.assertEqual(fan.poll(), [])
            dead = Superfan("ghost", "http://127.0.0.1:9")
            self.assertEqual(dead.poll()[0]["kind"], "unreachable")
        finally:
            c.close()


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = Repository(os.path.join(self.tmp, "r"))
        files = {f"area{a}/team{t}/mod{m}.py": f"# {a} {t} {m}\nVALUE = {m}\n".encode()
                 for a in range(8) for t in range(8) for m in range(4)}
        files["area3/team5/special_handler.py"] = b"def handle(): pass  # NEEDLE\n"
        self.cs = self.repo.create_changeset([], [{"path": p, "content": c} for p, c in files.items()], "u", "m")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_path_search_prunes_with_bloom_filters(self):
        r = search_paths(self.repo, self.cs, "special_hand")
        self.assertEqual(r["paths"], ["area3/team5/special_handler.py"])
        self.assertLess(r["trees_visited"], 20)  # out of 1 + 8 + 64 trees

    def test_grep(self):
        r = grep(self.repo, self.cs, "NEEDLE")
        self.assertEqual([(m["path"], m["line"]) for m in r["matches"]], [("area3/team5/special_handler.py", 1)])
        self.assertEqual(r["files_scanned"], 257)
        r = grep(self.repo, self.cs, "value = 3", path_prefix="area1", ignore_case=True)
        self.assertEqual(len(r["matches"]), 8)


class TestApiTools(unittest.TestCase):
    def setUp(self):
        self.c = Cluster(policy={"admins": ["root"]})
        self.c.seed({"app.py": b"def ok():\n    return True\n"})
        self.api = ServerApi(self.c.server.url, "root")
        repo = self.c.repo
        cur = repo.get_ref("main")
        self.good = cur
        for i in range(40):
            content = b"def ok():\n    return True\n" if i < 23 else b"def ok():\n    return False\n"
            cur = repo.create_changeset([cur], [{"path": "app.py", "content": content},
                                                {"path": f"log/{i}.txt", "content": str(i).encode()}], f"dev{i}", f"step {i}")
            if i == 23:
                self.culprit = cur
        repo.update_ref("main", repo.get_ref("main"), cur)

    def tearDown(self):
        self.c.close()

    def test_bisect_without_checkout(self):
        r = bisect(self.api, self.good, "main", file_matches(self.api, "app.py", "return True", True), log=lambda m: None)
        self.assertEqual(r["first_bad"], self.culprit)
        self.assertLessEqual(r["probes"], 6)  # log2(41)

    def test_revert_pipeline_under_contention(self):
        stop = threading.Event()

        def noise():
            i = 0
            while not stop.is_set():
                tip = self.c.repo.get_ref("main")
                cs = self.c.repo.create_changeset([tip], [{"path": f"noise/{i}", "content": b"n"}], "noise", "n")
                self.c.repo.update_ref("main", tip, cs)
                i += 1
                time.sleep(0.005)  # ~200 landings per second from other actors

        t = threading.Thread(target=noise)
        t.start()
        try:
            new = revert_and_land(self.api, self.culprit)
        finally:
            stop.set()
            t.join()
        self.assertTrue(self.c.repo.is_ancestor(new, "main"))
        content = base64.b64decode(self.api.read_file(rev="main", path="app.py")["content_b64"])
        self.assertIn(b"return True", content)

    def test_api_errors_are_structured(self):
        with self.assertRaises(RemoteError) as cm:
            self.api.resolve(rev="does-not-exist")
        self.assertEqual((cm.exception.status, cm.exception.code), (404, "not_found"))


if __name__ == "__main__":
    unittest.main()

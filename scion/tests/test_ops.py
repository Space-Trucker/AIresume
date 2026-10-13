"""Operations: rate limits (T-OPS-01), health and stats (FR-OP-01/02), upload limits (T-LIM-01) and the
standard-library-only constraint (NFR-19)."""
import ast
import base64
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
import zlib

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.client import WorkingCopy
from scion.objects import blob_id, encode_stored, object_id
from scion.ratelimit import RateLimited, RateLimiter, TokenBucket
from scion.rpc import RemoteError, RpcClient

PKG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scion")


class TestRateLimits(unittest.TestCase):
    def test_token_bucket(self):
        b = TokenBucket(rate=10, burst=2)
        self.assertEqual((b.take(1), b.take(1)), (0.0, 0.0))
        wait = b.take(1)
        self.assertGreater(wait, 0)
        self.assertLessEqual(wait, 0.1 + 1e-6)
        time.sleep(wait)
        self.assertEqual(b.take(1), 0.0)

    def test_concurrency_cap_and_exemptions(self):
        lim = RateLimiter({"default": {"heavy": {"concurrency": 1}}}, exempt={"scion-cache"})
        with lim.acquire("alice", "heavy"):
            with self.assertRaises(RateLimited):
                with lim.acquire("alice", "heavy"):
                    pass
            with lim.acquire("bob", "heavy"):  # per principal
                pass
            with lim.acquire("scion-cache", "heavy"), lim.acquire("scion-cache", "heavy"):
                pass
        with lim.acquire("alice", "heavy"):  # released again
            pass
        self.assertEqual(lim.rejected["concurrency"], 1)

    def test_T_OPS_01_429_with_retry_after_and_client_backoff(self):
        tmp = tempfile.mkdtemp(prefix="scion-rl-")
        c = Cluster(tmp, caches=0, identity={"rate_limits": {
            "default": {"read": {"rate": 20, "burst": 3}},
            "principals": {"ci-bot": {"read": {"rate": 1000, "burst": 1000}}}}})
        try:
            impatient = c.client("alice", max_throttle=0)
            codes = []
            for _ in range(8):
                try:
                    impatient.call("whoami")
                    codes.append(200)
                except RemoteError as e:
                    codes.append(e.status)
                    self.assertGreater(e.data["retry_after"], 0)
            self.assertEqual(codes[:3], [200, 200, 200])
            self.assertIn(429, codes)
            status, headers, _ = impatient.request("POST", "/rpc/whoami", b'{"params": {}}')
            self.assertEqual(status, 429)
            self.assertGreaterEqual(int(headers["Retry-After"]), 1)
            patient = c.client("bob")  # the client backs off and retries
            for _ in range(10):
                patient.call("whoami")
            self.assertGreater(patient.throttled, 0)
            bot = c.client("ci-bot")  # limits per principal
            for _ in range(50):
                bot.call("whoami")
            self.assertEqual(bot.throttled, 0)
            stats = c.client().get_json("/stats")
            self.assertGreater(stats["rate_limiter"]["rejected"]["rate"], 0)
            self.assertGreater(stats["errors"]["429"], 0)
        finally:
            c.close()
            shutil.rmtree(tmp, ignore_errors=True)


class TestHealthAndStats(unittest.TestCase):
    def test_FR_OP_01_02_every_tier_reports_health_and_stats(self):
        tmp = tempfile.mkdtemp(prefix="scion-stats-")
        c = Cluster(tmp)
        try:
            api = c.client("alice")
            api.call("create_changeset", repo=REPO, parents=[], message="m",
                     files=[{"path": "a", "content_b64": base64.b64encode(b"a\n").decode()}],
                     update_ref={"name": "main", "old": None})
            wc = WorkingCopy.clone(os.path.join(tmp, "wc"), c.server_urls[0], REPO, objects=c.daemon_urls[0],
                                   user="alice")
            wc.close()
            with self.assertRaises(RemoteError):
                api.call("resolve", repo=REPO, rev="nope")
            for tier, url in (("server", c.server_urls[0]), ("cache", c.cache_urls[0]), ("daemon", c.daemon_urls[0])):
                probe = RpcClient(url)
                self.assertEqual(probe.get_json("/healthz"), {"ok": True, "tier": tier})
                s = probe.get_json("/stats")
                self.assertEqual(s["tier"], tier)
                self.assertIn("uptime_s", s)
                if tier == "server":
                    self.assertEqual(s["errors"]["404"], 1)
                    lat = s["latency"]["resolve"]
                else:
                    self.assertIsNotNone(s["cache"]["hit_rate"])
                    self.assertEqual(s["cache"]["hits"] + s["cache"]["misses"], 2 if tier == "daemon" else 2)
                    lat = s["latency"]["get_objects"]
                self.assertTrue({"count", "p50_ms", "p90_ms", "p99_ms"} <= set(lat))
                probe.close_all()
        finally:
            c.close()
            shutil.rmtree(tmp, ignore_errors=True)


class TestUploadLimits(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-lim-")
        self.c = Cluster(self.tmp, caches=0, allow_direct_objects=True,
                         repos={REPO: {"read": ["*"], "write": ["*"], "limits": {"max_file_bytes": 1000}}})
        self.api = self.c.client("alice")
        self.base = self.api.call("create_changeset", repo=REPO, parents=[], message="m",
                                  files=[{"path": "small", "content_b64": base64.b64encode(b"ok\n").decode()}],
                                  update_ref={"name": "main", "old": None})["id"]

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T_LIM_01_oversized_uploads_get_413_and_store_nothing(self):
        repo = self.c.repo()
        small, big = b"x" * 10, b"y" * 1001
        items = [(blob_id(small), 0, encode_stored("blob", small)), (blob_id(big), 0, encode_stored("blob", big))]
        with self.assertRaises(RemoteError) as e:
            self.api.put_objects(REPO, items)
        self.assertEqual(e.exception.status, 413)
        self.assertFalse(repo.objects.has(blob_id(small)) or repo.objects.has(blob_id(big)), "nothing is stored")
        # a small compressed upload that would expand enormously is refused without expanding it
        bomb_payload = b"\0" * (50 << 20)
        bomb = zlib.compress(b"blob\0" + bomb_payload, 9)
        self.assertLess(len(bomb), 100_000)
        with self.assertRaises(RemoteError) as e:
            self.api.put_objects(REPO, [(object_id("blob", bomb_payload), 0, bomb)])
        self.assertEqual(e.exception.status, 413)
        # inline content over the limit: no changeset is created
        before = repo.meta.count_changesets()
        with self.assertRaises(RemoteError) as e:
            self.api.call("create_changeset", repo=REPO, parents=[self.base], message="big",
                          files=[{"path": "big", "content_b64": base64.b64encode(big).decode()}])
        self.assertEqual(e.exception.status, 413)
        self.assertEqual(repo.meta.count_changesets(), before)
        self.assertFalse(repo.objects.has(blob_id(big)))
        # within the limit is fine
        self.assertEqual(self.api.put_objects(REPO, items[:1]), {"stored": 1})
        # from a working copy: the commit fails cleanly and the change stays local
        wc = WorkingCopy.clone(os.path.join(self.tmp, "wc"), self.c.server_urls[0], REPO,
                               objects=self.c.server_urls[0], user="alice")
        with open(os.path.join(wc.root, "huge.bin"), "wb") as f:
            f.write(big)
        with self.assertRaises(RemoteError) as e:
            wc.commit("too big", addremove=True)
        self.assertEqual(e.exception.status, 413)
        self.assertEqual(wc.base, self.base)
        self.assertEqual(wc.status().untracked, ["huge.bin"])
        wc.close()

    def test_request_body_cap(self):
        host, port = self.c.server_urls[0][7:].split(":")
        with socket.create_connection((host, int(port))) as s:
            s.sendall(b"POST /rpc/whoami HTTP/1.1\r\nHost: x\r\nContent-Length: 999999999999\r\n\r\n")
            head = s.recv(4096).decode()
        self.assertTrue(head.startswith("HTTP/1.1 413"), head)


class TestStandardLibraryOnly(unittest.TestCase):
    def test_NFR_19_no_third_party_imports(self):
        stdlib = set(sys.stdlib_module_names)
        for dirpath, _, files in os.walk(PKG):
            for name in files:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(dirpath, name)
                with open(path) as f:
                    tree = ast.parse(f.read(), path)
                for node in ast.walk(tree):
                    mods = []
                    if isinstance(node, ast.Import):
                        mods = [a.name for a in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.level == 0:
                        mods = [node.module]
                    for m in mods:
                        top = m.split(".")[0]
                        self.assertTrue(top in stdlib or top == "scion", f"{path}: imports {m}")


if __name__ == "__main__":
    unittest.main()

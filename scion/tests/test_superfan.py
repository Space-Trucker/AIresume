"""Superfans (WP-B4.4): T-OPS-02 (novel, threshold and unreachable findings), T-OPS-03 (findings
reach a chat webhook) and T-OPS-04 (findings carry the component's log lines)."""
import base64
import http.server
import io
import json
import shutil
import tempfile
import threading
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.superfan import PROFILES, Baseline, Rule, Superfan, Watch, extract


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


class TestJudgement(unittest.TestCase):
    """The baseline and the rules, on synthetic metrics: deterministic."""

    def fan(self, **kw):
        return Superfan("http://127.0.0.1:9", "daemon", out=io.StringIO(), **kw)

    def test_novel_findings_need_a_baseline_and_fire_once(self):
        fan = self.fan(warmup=5, default_rules=False)
        for x in (0.99, 0.995, 0.991, 0.993, 0.99, 0.992):
            self.assertEqual(fan._judge({"hit_rate": x}), [])
        found = fan._judge({"hit_rate": 0.62})
        self.assertEqual([(f.kind, f.metric) for f in found], [("novel", "hit_rate")])
        self.assertIn("down from its usual 0.99", found[0].message)
        self.assertEqual(fan._judge({"hit_rate": 0.6}), [], "an ongoing anomaly is reported once")
        resolved = fan._judge({"hit_rate": 0.99})
        self.assertEqual([(f.kind, f.metric) for f in resolved], [("resolved", "hit_rate")])
        self.assertEqual(fan._judge({"hit_rate": 1.0}), [], "a rise in hit rate is not a problem")
        self.assertEqual(fan._judge({"hit_rate": None}), [], "an interval without lookups has no hit rate")

    def test_noise_within_the_usual_range_is_not_novel(self):
        fan = self.fan(warmup=5, default_rules=False)
        series = [100, 140, 90, 130, 110, 95, 150, 105, 120, 135, 98, 145]  # requests per second
        self.assertEqual([f for x in series for f in fan._judge({"requests_per_s": x})], [])
        self.assertEqual([f.kind for f in fan._judge({"requests_per_s": 900})], ["novel"])

    def test_a_lasting_shift_becomes_the_new_normal(self):
        b, w = Baseline(), Watch("up", 1.0, 1.0)
        for _ in range(10):
            b.update(10, 0.1)
        self.assertTrue(b.judge(40, w, 4.0))
        for _ in range(400):  # anomalies teach the baseline slowly
            b.update(40, 0.01)
        self.assertFalse(b.judge(40, w, 4.0))

    def test_rules(self):
        self.assertEqual(Rule.parse("hit_rate < 0.99 for 3 critical"), Rule("hit_rate", "<", 0.99, 3, "critical"))
        self.assertEqual(Rule.parse({"metric": "x", "op": ">=", "value": 2}), Rule("x", ">=", 2.0))
        for bad in ("hit_rate ~ 1", "for 3", {"metric": "x", "op": "<", "value": 1, "severity": "loud"}):
            with self.assertRaises((ValueError, KeyError)):
                Rule.parse(bad)
        fan = self.fan(rules=["land_queue_depth >= 10 for 2"], default_rules=False)
        self.assertEqual(fan._judge({"land_queue_depth": 12}), [], "breached once: not yet")
        found = fan._judge({"land_queue_depth": 15})
        self.assertEqual([(f.kind, f.severity, f.rule) for f in found],
                         [("threshold", "warning", "land_queue_depth >= 10 for 2 polls")])
        self.assertEqual(fan._judge({"land_queue_depth": 30}), [])
        self.assertEqual([f.kind for f in fan._judge({"land_queue_depth": 2})], ["resolved"])

    def test_metrics_are_rates_over_the_interval(self):
        prev = {"uptime_s": 10, "counters": {"rpc.get_objects": 100}, "errors": {"503": 1, "404": 5},
                "cache": {"hits": 1000, "misses": 10}}
        cur = {"uptime_s": 20, "counters": {"rpc.get_objects": 300}, "errors": {"503": 3, "404": 5},
               "cache": {"hits": 1090, "misses": 20, "bytes_cached": 4096},
               "latency": {"get_objects": {"p99_ms": 2.5}}}
        m = extract(PROFILES["daemon"], prev, cur, 10.0)
        self.assertEqual((m["requests_per_s"], m["server_errors_per_s"], m["client_errors_per_s"]), (20.0, 0.2, 0.0))
        self.assertAlmostEqual(m["hit_rate"], 0.9)  # 90 of this interval's 100 lookups, not 1090 of 1110
        self.assertEqual((m["misses_per_s"], m["bytes_cached"], m["p99_ms.get_objects"]), (1.0, 4096, 2.5))
        self.assertIsNone(extract(PROFILES["daemon"], cur, cur, 10.0)["hit_rate"])


class SuperfanCluster(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-fan-")
        self.c = Cluster(self.tmp)
        files = [{"path": f"d{i % 10}/f{i}.txt", "content_b64": b64(f"file {i}\n".encode() * 3)} for i in range(240)]
        cs = self.c.client("root").call("create_changeset", repo=REPO, parents=[], message="m", files=files,
                                        update_ref={"name": "main", "old": None})["id"]
        repo = self.c.repo()
        self.blobs = [oid for _, _, oid in repo.trees.walk(repo.root_tree(cs))]
        self.client = self.c.client("alice", url=self.c.daemon_urls[0])
        self.out = io.StringIO()

    def tearDown(self):
        self.client.close_all()
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def warm(self, fan, polls=6):
        self.client.get_objects(REPO, self.blobs[:20])
        fan.poll_once()
        for _ in range(polls):
            self.client.get_objects(REPO, self.blobs[:20])  # all hits
            self.assertEqual([f for f in fan.poll_once() if f.metric == "hit_rate"], [])


class TestSuperfansOnTheTiers(SuperfanCluster):
    def test_T_OPS_02_novel_threshold_and_unreachable_findings(self):
        fan = Superfan(self.c.daemon_urls[0], "daemon", rules=["hit_rate < 0.5"], warmup=4, out=self.out)
        try:
            self.warm(fan)
            self.assertEqual(fan.metrics["hit_rate"], 1.0)
            self.client.get_objects(REPO, self.blobs[20:140])  # a burst of new objects: all misses
            found = {(f.kind, f.metric) for f in fan.poll_once()}
            self.assertIn(("novel", "hit_rate"), found)
            self.assertIn(("threshold", "hit_rate"), found)
            self.assertIn(("novel", "misses_per_s"), found)
            self.client.get_objects(REPO, self.blobs[:140])  # all hits again
            resolved = {f.metric for f in fan.poll_once() if f.kind == "resolved"}
            self.assertTrue({"hit_rate"} <= resolved, resolved)
            self.c.daemon_services[0].metrics.started += 10_000  # uptime goes backwards: a restart
            self.assertIn("restarted", [f.kind for f in fan.poll_once()])
            self.c.daemons[0].stop()
            down = fan.poll_once()
            self.assertEqual([(f.kind, f.severity) for f in down], [("unreachable", "critical")])
            self.assertEqual(fan.poll_once(), [], "an ongoing outage is reported once")
            self.assertIn("scion-daemon* unreachable", self.out.getvalue())
        finally:
            fan.close()

    def test_the_cache_and_landing_queue_superfans(self):
        cache = Superfan(self.c.cache_urls[0], "cache", warmup=2, out=self.out)
        queue = Superfan(self.c.server_urls[0], "antique", rules=["landed_per_s > 0 info"], warmup=2, out=self.out)
        try:
            cache.poll_once()
            queue.poll_once()
            self.client.get_objects(REPO, self.blobs[200:210])  # daemon misses become cache misses
            alice = self.c.client("alice")
            for i in range(3):
                head = alice.call("create_changeset", repo=REPO, parents=[alice.call("resolve", repo=REPO, rev="main")],
                                  message=f"c{i}", files=[{"path": f"docs/n{i}.md", "content_b64": b64(b"x\n")}])["id"]
                cr = alice.call("antique.create", repo=REPO, title=f"c{i}", head=head)
                alice.call("antique.land", repo=REPO, id=cr["id"])  # docs need no approval
            cache.poll_once()
            self.assertEqual(cache.metrics["hit_rate"], 0.0)
            self.assertGreater(cache.metrics["upstream_requests_per_s"], 0)
            found = queue.poll_once()
            self.assertEqual([(f.kind, f.severity, f.metric) for f in found], [("threshold", "info", "landed_per_s")])
            m = queue.metrics
            self.assertGreater(m["landed_per_s"], 0)
            self.assertEqual((m["land_queue_depth"], m["postmerge_queued"]), (0, 3))
            self.assertIn("p99_ms.antique.land", m)
        finally:
            cache.close()
            queue.close()


class TestFindingsAndLogs(SuperfanCluster):
    def test_T_OPS_04_findings_carry_the_log_lines_around_them(self):
        fan = Superfan(self.c.daemon_urls[0], "daemon", warmup=4, out=self.out)
        try:
            self.warm(fan, polls=4)
            self.assertTrue(fan.logs_available)
            self.c.caches[0].stop()  # the daemon's only upstream goes away
            with self.assertRaises(Exception):
                self.client.get_objects(REPO, self.blobs[150:160])
            found = fan.poll_once()
            errors = [f for f in found if f.kind == "threshold" and f.metric == "server_errors_per_s"]
            self.assertEqual(len(errors), 1, [f.to_dict() for f in found])
            lines = [e["message"] for e in errors[0].logs]
            self.assertTrue(any("upstream" in m and "failed" in m for m in lines), lines)
            self.assertTrue(any("no cache answered" in m for m in lines), lines)
            self.assertIn("> warning: upstream", errors[0].text())
        finally:
            fan.close()

    def test_logs_need_an_administrator_or_a_service_principal(self):
        with self.assertRaises(Exception) as e:
            self.c.client("alice", url=self.c.server_urls[0]).get_json("/logs")
        self.assertEqual(e.exception.status, 403)
        fan = Superfan(self.c.server_urls[0], "server", user="alice", out=self.out)
        try:
            fan.poll_once()
            fan.poll_once()
            self.assertFalse(fan.logs_available)  # telemetry only
            self.assertIn("requests_per_s", fan.metrics)
        finally:
            fan.close()


class _Hook(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.received.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *a):
        pass


class TestWebhook(SuperfanCluster):
    def test_T_OPS_03_findings_reach_a_chat_webhook(self):
        hook = http.server.HTTPServer(("127.0.0.1", 0), _Hook)
        hook.received = []
        threading.Thread(target=hook.serve_forever, daemon=True).start()
        fan = Superfan(self.c.daemon_urls[0], "daemon", rules=["requests_per_s >= 0 critical"],
                       webhook=f"http://127.0.0.1:{hook.server_port}/hook", out=self.out)
        try:
            fan.poll_once()
            fan.poll_once()
            fan.notifier.flush()
            self.assertEqual(len(hook.received), 1)
            payload = hook.received[0]
            self.assertTrue(payload["text"].startswith(":rotating_light: *scion-daemon* threshold: requests_per_s"))
            self.assertEqual((payload["finding"]["kind"], payload["finding"]["rule"]),
                             ("threshold", "requests_per_s >= 0"))
        finally:
            fan.close()
            hook.shutdown()
            hook.server_close()


if __name__ == "__main__":
    unittest.main()

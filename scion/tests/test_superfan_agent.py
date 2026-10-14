"""Superfan agents against a fake Claude API (WP-B6.2): T-OPS-06 (a finding leads to tool calls
and an analysis in chat) and T-OPS-07 (limits and failure paths; no credential leaks)."""
import http.server
import io
import json
import shutil
import tempfile
import threading
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.superfan import Finding, Superfan
from scion.superfan_agent import FALLBACK_BETA, AgentConfig, AgentError, ClaudeApi, Investigator

KEY = "sk-ant-test-0123456789-SECRET"


class FakeClaude(http.server.ThreadingHTTPServer):
    """Answers POST /v1/messages from a script: each entry is a response dict, an (HTTP status,
    body, headers) tuple, or a function of the request body returning either."""

    def __init__(self, script):
        super().__init__(("127.0.0.1", 0), _ClaudeHandler)
        self.script, self.requests, self.lock = list(script), [], threading.Lock()
        threading.Thread(target=self.serve_forever, daemon=True).start()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server_port}/v1/messages"

    def stop(self):
        self.shutdown()
        self.server_close()


class _ClaudeHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with self.server.lock:
            self.server.requests.append({"body": body, "headers": {k.lower(): v for k, v in self.headers.items()}})
            step = self.server.script.pop(0) if len(self.server.script) > 1 else self.server.script[0]
        if callable(step):
            step = step(body)
        status, payload, headers = (step if isinstance(step, tuple) else (200, step, {}))
        data = json.dumps(payload).encode()
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


class _Hook(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.received.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *a):
        pass


def reply(*blocks, stop="end_turn", out=40):
    return {"id": "msg_1", "type": "message", "role": "assistant", "model": "claude-opus-5-5",
            "content": list(blocks), "stop_reason": stop, "usage": {"input_tokens": 900, "output_tokens": out}}


def thinking(sig):
    return {"type": "thinking", "thinking": "", "signature": sig}


def tool_use(i, name, **inp):
    return {"type": "tool_use", "id": i, "name": name, "input": inp}


def text(t):
    return {"type": "text", "text": t}


ANALYSIS = ("What happened: requests rose above the rule. Evidence: requests_per_s and the access log. "
            "Likely cause: a burst of checkouts. Next step: check the busiest client.")


class TestInvestigationOnATier(unittest.TestCase):
    def test_T_OPS_06_a_finding_is_investigated_and_explained_in_chat(self):
        tmp = tempfile.mkdtemp(prefix="scion-agent-")
        c = Cluster(tmp)
        hook = http.server.HTTPServer(("127.0.0.1", 0), _Hook)
        hook.received = []
        threading.Thread(target=hook.serve_forever, daemon=True).start()
        api = FakeClaude([reply(thinking("sig-1"), tool_use("tu1", "get_stats"),
                                tool_use("tu2", "get_logs", level="info", limit=20), stop="tool_use"),
                          reply(thinking("sig-2"), text(ANALYSIS))])
        out = io.StringIO()
        fan = Superfan(c.daemon_urls[0], "daemon", rules=["requests_per_s >= 0 critical"],
                       webhook=f"http://127.0.0.1:{hook.server_port}/hook", out=out)
        fan.agent = Investigator(fan, fan.webhook, AgentConfig(), ClaudeApi(KEY, api.url), out=out)
        try:
            fan.poll_once()
            found = fan.poll_once()  # the rule fires: the finding is posted, then investigated
            self.assertEqual([f.kind for f in found], ["threshold"])
            fan.agent.close()
            fan.notifier.flush()
            self.assertEqual(len(hook.received), 2)
            self.assertEqual(hook.received[0]["finding"]["kind"], "threshold")  # the finding first, at once
            post = hook.received[1]
            self.assertEqual(post["analysis"], ANALYSIS)
            self.assertTrue(post["text"].startswith(":mag: *scion-daemon* on the threshold finding"))
            self.assertEqual(post["finding"]["rule"], "requests_per_s >= 0")

            first, second = api.requests[0], api.requests[1]
            self.assertEqual(first["headers"]["x-api-key"], KEY)
            self.assertEqual(first["headers"]["anthropic-version"], "2023-06-01")
            self.assertEqual(first["headers"]["anthropic-beta"], FALLBACK_BETA)
            b = first["body"]
            self.assertEqual((b["model"], b["thinking"], b["output_config"], b["fallbacks"]),
                             ("claude-opus-5-5", {"type": "adaptive"}, {"effort": "high"}, "default"))
            self.assertEqual([t["name"] for t in b["tools"]],
                             ["get_stats", "get_logs", "get_metrics", "get_recent_findings"])
            self.assertNotIn("tool_choice", b)
            self.assertIn("superfan of scion-daemon", b["system"])
            self.assertIn("<finding>", b["messages"][0]["content"][0]["text"])
            self.assertIn("requests_per_s is", b["messages"][0]["content"][0]["text"])
            # preserved thinking: the assistant turn goes back unchanged, then every tool result at once
            m = second["body"]["messages"]
            self.assertEqual(m[1], {"role": "assistant", "content": [
                thinking("sig-1"), tool_use("tu1", "get_stats"), tool_use("tu2", "get_logs", level="info", limit=20)]})
            results = m[2]["content"]
            self.assertEqual([(r["type"], r["tool_use_id"], r["is_error"]) for r in results],
                             [("tool_result", "tu1", False), ("tool_result", "tu2", False)])
            self.assertIn("uptime_s", json.loads(results[0]["content"]))
            self.assertIsInstance(json.loads(results[1]["content"]), list)
            self.assertEqual(second["body"]["system"], b["system"])
            self.assertEqual(second["body"]["tools"], b["tools"])
            self.assertIn(ANALYSIS, out.getvalue())
        finally:
            fan.close()
            api.stop()
            hook.shutdown()
            hook.server_close()
            c.close()
            shutil.rmtree(tmp, ignore_errors=True)


class _Client:
    def __init__(self, fail=False):
        self.fail = fail

    def get_json(self, path):
        if self.fail:
            raise OSError("connection refused")
        return {"uptime_s": 12.5, "path": path, "entries": [{"level": "error", "message": "disk full"}]}


class _Fan:
    """What the agent's tools read from a superfan."""

    def __init__(self, fail=False):
        self.client, self.metrics, self.baselines, self.findings = _Client(fail), {"hit_rate": 0.5}, {}, []
        self.notifier = None


def finding(metric="hit_rate", kind="novel"):
    return Finding(kind, "scion-cache", "http://cache:1", "warning", f"{metric} is 0.5, down from its usual 0.99",
                   metric=metric, value=0.5, baseline=0.99, logs=[{"level": "warning", "message": "upstream slow"}])


class TestLimitsAndFailures(unittest.TestCase):
    def setUp(self):
        self.apis = []

    def tearDown(self):
        for a in self.apis:
            a.stop()

    def agent(self, script, fail=False, retries=2, **config):
        api = FakeClaude(script)
        self.apis.append(api)
        out = io.StringIO()
        inv = Investigator(_Fan(fail), None, AgentConfig(**config), ClaudeApi(KEY, api.url, retries=retries),
                           out=out)
        return inv, api, out

    def assertNoKey(self, api, out, *more):
        for r in api.requests:
            self.assertNotIn(KEY, json.dumps(r["body"]))
        self.assertNotIn(KEY, out.getvalue())
        for m in more:
            self.assertNotIn(KEY, str(m))

    def test_T_OPS_07_retries_then_answers(self):
        inv, api, out = self.agent([(529, {"type": "error", "error": {"type": "overloaded_error"}}, {"retry-after": "0"}),
                                    (500, {"type": "error", "error": {"type": "api_error"}}, {"retry-after": "0"}),
                                    reply(text(ANALYSIS))])
        self.assertEqual(inv.investigate(finding()), ANALYSIS)
        self.assertEqual(len(api.requests), 3)
        self.assertNoKey(api, out)

    def test_T_OPS_07_a_bad_request_is_not_retried_and_the_finding_gets_a_note(self):
        inv, api, out = self.agent([(400, {"type": "error", "error": {"type": "invalid_request_error",
                                                                        "message": "bad tools"}}, {})])
        self.assertIsNone(inv.submit(finding()).result(10))
        self.assertEqual(len(api.requests), 1)
        self.assertIn("no analysis of the novel finding (the Claude API answered HTTP 400: bad tools)", out.getvalue())
        self.assertNoKey(api, out)

    def test_T_OPS_07_a_refusal_gets_a_note(self):
        inv, api, out = self.agent([reply(stop="refusal")])
        with self.assertRaises(AgentError) as e:
            inv.investigate(finding())
        self.assertIn("declined", str(e.exception))

    def test_T_OPS_07_the_last_turn_cannot_call_tools(self):
        def step(body):
            if body.get("tool_choice") == {"type": "none"}:
                return reply(text("final " + ANALYSIS))
            return reply(thinking("s"), tool_use(f"t{len(body['messages'])}", "get_metrics"), stop="tool_use")
        inv, api, out = self.agent([step], max_turns=3)
        self.assertEqual(inv.investigate(finding()), "final " + ANALYSIS)
        self.assertEqual(len(api.requests), 3)
        self.assertEqual([r["body"].get("tool_choice") for r in api.requests], [None, None, {"type": "none"}])
        self.assertEqual(inv.counters["tool_calls"], 2)

    def test_T_OPS_07_the_token_budget_ends_the_investigation(self):
        def step(body):
            if body.get("tool_choice") == {"type": "none"}:
                return reply(text(ANALYSIS), out=500)
            return reply(tool_use("t", "get_stats"), stop="tool_use", out=40_000)
        inv, api, out = self.agent([step], max_turns=6, token_budget=60_000)
        self.assertEqual(inv.investigate(finding()), ANALYSIS)
        self.assertEqual(len(api.requests), 3)  # 40k, 80k spent: the third call must answer

    def test_T_OPS_07_a_repeated_finding_is_investigated_once(self):
        inv, api, out = self.agent([reply(text(ANALYSIS))])
        first = inv.submit(finding())
        self.assertIsNone(inv.submit(finding()))  # the same problem again
        other = inv.submit(finding("misses_per_s"))
        self.assertIsNone(inv.submit(finding(kind="resolved")))  # resolutions are not investigated
        first.result(10)
        other.result(10)
        self.assertEqual((inv.counters["deduplicated"], len(api.requests)), (1, 2))

    def test_T_OPS_07_a_failing_tool_is_reported_to_the_model(self):
        inv, api, out = self.agent([reply(tool_use("t1", "get_stats"), stop="tool_use"), reply(text(ANALYSIS))],
                                   fail=True)
        self.assertEqual(inv.investigate(finding()), ANALYSIS)
        result = api.requests[1]["body"]["messages"][2]["content"][0]
        self.assertTrue(result["is_error"])
        self.assertIn("connection refused", result["content"])

    def test_T_OPS_07_an_unreachable_api_and_a_full_queue(self):
        api = ClaudeApi(KEY, "http://127.0.0.1:9/v1/messages", retries=0)
        out = io.StringIO()
        inv = Investigator(_Fan(), None, AgentConfig(queue=0), api, out=out)
        self.assertIsNone(inv.submit(finding()))
        self.assertIn("too many investigations are waiting", out.getvalue())
        with self.assertRaises(AgentError) as e:
            Investigator(_Fan(), None, AgentConfig(), api, out=out).investigate(finding())
        self.assertIn("unreachable", str(e.exception))
        self.assertNotIn(KEY, str(e.exception) + out.getvalue())
        with self.assertRaises(AgentError):
            ClaudeApi("")  # no key, no agent


if __name__ == "__main__":
    unittest.main()

"""Superfans: one tireless watcher per component.

In the article, a superfan is a Claude agent in a Slack channel that is obsessively focused on
the health of a single component.  It reads telemetry and flags anything strange, alongside
traditional alerts.  This module is the telemetry side of that idea.  Each superfan polls one
component's ``/stats``, learns an adaptive baseline for every metric (an exponentially weighted
mean and variance of per-interval rates and gauges), and reports deviations from it ("novel"
findings).  It also evaluates fixed thresholds (traditional alerts).  Findings go to stdout and,
optionally, to a webhook such as a Slack incoming webhook, where an agent or a person can pick
them up.
"""
from __future__ import annotations

import json
import math
import time
import urllib.request

from .rpc import RpcClient


def flatten(d, prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(d, (int, float)) and not isinstance(d, bool):
        out[prefix] = float(d)
    return out


GAUGE_HINTS = ("hit_rate", "p50_ms", "p99_ms", "bytes_cached", "objects_cached", "uptime_s", "restricted_ids")


class Baseline:
    def __init__(self, alpha: float):
        self.alpha = alpha
        self.mean: float | None = None
        self.var = 0.0
        self.n = 0

    def update(self, x: float) -> float:
        """Return the z-score of x against the baseline *before* learning from it."""
        if self.mean is None:
            self.mean, self.n = x, 1
            return 0.0
        # The floor keeps perfectly flat metrics from alerting on rounding noise, while a
        # metric that sat at zero and suddenly moves still produces a large score.
        z = (x - self.mean) / max(math.sqrt(self.var), 0.05 * abs(self.mean), 1e-3)
        d = x - self.mean
        self.mean += self.alpha * d
        self.var = (1 - self.alpha) * (self.var + self.alpha * d * d)
        self.n += 1
        return z


class Superfan:
    def __init__(self, component: str, url: str, rules: list[dict] | None = None, alpha: float = 0.2,
                 z_threshold: float = 6.0, warmup: int = 8, webhook: str | None = None):
        self.component = component
        self.client = RpcClient(url, retries=1, timeout=10)
        self.rules = rules or []
        self.alpha = alpha
        self.z = z_threshold
        self.warmup = warmup
        self.webhook = webhook
        self.baselines: dict[str, Baseline] = {}
        self.prev: dict[str, float] | None = None
        self.prev_t: float | None = None
        self.findings: list[dict] = []

    def _derived(self, cur: dict[str, float], dt: float) -> dict[str, float]:
        out = {}
        for k, v in cur.items():
            if any(h in k for h in GAUGE_HINTS):
                out[k] = v
            elif self.prev is not None and k in self.prev:
                out[k + "/s"] = max(0.0, v - self.prev[k]) / dt
        # Interval hit rate for caches: much more sensitive than the lifetime ratio.
        if self.prev is not None:
            h = cur.get("cache.hits", 0) - self.prev.get("cache.hits", 0)
            m = cur.get("cache.misses", 0) - self.prev.get("cache.misses", 0)
            if h + m > 0:
                out["cache.hit_rate_interval"] = h / (h + m)
        return out

    def observe(self, stats: dict, now: float | None = None) -> list[dict]:
        now = now or time.time()
        cur = flatten(stats)
        dt = max(1e-3, now - self.prev_t) if self.prev_t else 1.0
        metrics = self._derived(cur, dt)
        findings = []
        for k, v in metrics.items():
            b = self.baselines.setdefault(k, Baseline(self.alpha))
            z = b.update(v)
            if b.n > self.warmup and abs(z) >= self.z:
                findings.append({"component": self.component, "kind": "novel", "metric": k, "value": round(v, 6),
                                 "baseline": round(b.mean, 6), "z": round(z, 2)})
        for rule in self.rules:
            v = metrics.get(rule["metric"])
            if v is None:
                continue
            if "below" in rule and v < rule["below"] or "above" in rule and v > rule["above"]:
                findings.append({"component": self.component, "kind": "threshold", "metric": rule["metric"],
                                 "value": round(v, 6), "rule": rule})
        self.prev, self.prev_t = cur, now
        self.findings.extend(findings)
        return findings

    def poll(self) -> list[dict]:
        try:
            stats = self.client.get_json("/stats")
        except Exception as e:
            f = [{"component": self.component, "kind": "unreachable", "error": str(e)}]
            self.findings.extend(f)
            return f
        return self.observe(stats)

    def notify(self, findings: list[dict]) -> None:
        for f in findings:
            print(json.dumps(f), flush=True)
        if self.webhook and findings:
            text = "\n".join(f"[{f['component']}] {f['kind']}: {f.get('metric', f.get('error'))} = {f.get('value')}"
                             for f in findings)
            req = urllib.request.Request(self.webhook, data=json.dumps({"text": text}).encode(),
                                         headers={"Content-Type": "application/json"})
            try:
                urllib.request.urlopen(req, timeout=10)
            except Exception as e:  # pragma: no cover
                print(json.dumps({"component": self.component, "kind": "webhook_error", "error": str(e)}))

    def run(self, interval: float = 10.0, iterations: int | None = None) -> None:
        i = 0
        while iterations is None or i < iterations:
            self.notify(self.poll())
            i += 1
            time.sleep(interval)


DEFAULT_RULES = {
    "daemon": [{"metric": "cache.hit_rate_interval", "below": 0.9}],
    "cache": [{"metric": "cache.hit_rate_interval", "below": 0.9}],
    "server": [{"metric": "counters.errors.internal/s", "above": 0.0}],
}

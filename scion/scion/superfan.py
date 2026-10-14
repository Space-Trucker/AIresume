"""Superfans: one monitor per component, watching its telemetry and its logs (FR-OP-03…05,
FR-OP-08; UC-26).

At Anthropic each superfan is a Claude agent in Slack, obsessively focused on one component: a
scion-daemon superfan, a scion-cache superfan and an Antique landing-queue superfan, each with
access to telemetry and logs. This module is the watcher the agent works from; the agent itself,
which investigates each finding and explains it in chat, is superfan_agent.Investigator (FR-OP-09).
Every poll the watcher

1. reads the component's ``/stats`` and its new log entries (``GET /logs``, ADR-18);
2. turns counters into rates over the interval (the hit rate too is the interval's, not the
   lifetime's) and reads gauges and latency percentiles as they are;
3. compares each watched metric with a baseline it keeps learning (an exponentially weighted mean
   and deviation) and raises a **novel** finding when the metric leaves its usual range in the
   direction that matters;
4. evaluates the threshold rules, the traditional alerts (FR-OP-04);
5. raises an **unreachable** finding when the component doesn't answer, a **restarted** finding
   when its uptime goes backwards, and a **resolved** finding when a condition clears.

A condition raises one finding when it starts, not one per poll. Every finding carries the log
entries around it (FR-OP-08) and goes to stdout and, when configured, to a chat webhook as a
Slack-compatible ``{"text": ...}`` payload (FR-OP-05), and then to the agent, when there is one.
"""
from __future__ import annotations

import http.client
import json
import math
import operator
import re
import sys
import time
from collections import deque
from dataclasses import asdict, dataclass, field

from .notify import Notifier
from .rpc import ClientTls, RemoteError, RpcClient

RESTART_SLACK = 1.0  # seconds, plus 10% of the interval: polling jitter, not a restart

SEVERITIES = ("info", "warning", "critical")
OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq,
       "!=": operator.ne}
RULE_TEXT = re.compile(r"^\s*([\w.]+)\s*(<=|>=|==|!=|<|>)\s*(-?[0-9.]+(?:[eE][-+]?\d+)?)"
                       r"(?:\s+for\s+(\d+))?(?:\s+(info|warning|critical))?\s*$")


# ================================================================================ configuration
@dataclass(frozen=True)
class Watch:
    """How a metric is judged against its baseline: the direction that is bad, and the smallest
    changes that count, absolutely and relative to the baseline's mean."""
    direction: str = "up"  # up, down or both
    floor: float = 0.0
    relative: float = 1.0


@dataclass(frozen=True)
class Rule:
    """A traditional alert: ``metric op value``, breached for ``for_polls`` polls in a row."""
    metric: str
    op: str
    value: float
    for_polls: int = 1
    severity: str = "warning"

    def __post_init__(self):
        if self.op not in OPS:
            raise ValueError(f"unknown operator {self.op!r}")
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {', '.join(SEVERITIES)}")
        if self.for_polls < 1:
            raise ValueError("for must be at least 1")

    @classmethod
    def parse(cls, spec) -> "Rule":
        """From ``{"metric", "op", "value", "for", "severity"}`` or text such as
        ``"hit_rate < 0.99 for 3 critical"``."""
        if isinstance(spec, Rule):
            return spec
        if isinstance(spec, dict):
            return cls(str(spec["metric"]), str(spec["op"]), float(spec["value"]), int(spec.get("for", 1)),
                       str(spec.get("severity", "warning")))
        m = RULE_TEXT.match(str(spec))
        if not m:
            raise ValueError(f"bad rule {spec!r}: expected 'metric op value [for N] [severity]'")
        return cls(m.group(1), m.group(2), float(m.group(3)), int(m.group(4) or 1), m.group(5) or "warning")

    def breached(self, value: float) -> bool:
        return OPS[self.op](value, self.value)

    def describe(self) -> str:
        return f"{self.metric} {self.op} {self.value:g}" + (f" for {self.for_polls} polls" if self.for_polls > 1 else "")


@dataclass(frozen=True)
class Profile:
    """What one kind of component's superfan reads from ``/stats`` and watches."""
    name: str
    rates: dict = field(default_factory=dict)    # metric → path of a counter; reported per second
    ratios: dict = field(default_factory=dict)   # metric → (numerator path, denominator paths) per interval
    gauges: dict = field(default_factory=dict)   # metric → path of a value reported as it is
    latency: tuple = ()                          # methods whose p99 becomes "p99_ms.<method>"
    watches: dict = field(default_factory=dict)  # metric → Watch: the metrics with novel detection
    rules: tuple = ()                            # default threshold rules


COMMON_WATCHES = {
    "server_errors_per_s": Watch("up", 0.05, 1.0),
    "rate_limited_per_s": Watch("up", 1.0, 1.0),
    "requests_per_s": Watch("both", 1.0, 0.8),
}

TIER_RATES = {
    "misses_per_s": ("cache", "misses"),
    "upstream_requests_per_s": ("cache", "upstream_requests"),
    "bytes_fetched_per_s": ("cache", "bytes_fetched"),
    "bytes_served_per_s": ("cache", "bytes_served"),
    "rejected_objects_per_s": ("cache", "rejected_objects"),
    "evictions_per_s": ("cache", "evictions"),
    "purged_per_s": ("cache", "purged"),
    "epoch_check_failures_per_s": ("cache", "epoch_check_failures"),
}
TIER_RATIOS = {"hit_rate": (("cache", "hits"), (("cache", "hits"), ("cache", "misses")))}
TIER_GAUGES = {"bytes_cached": ("cache", "bytes_cached"), "objects_cached": ("cache", "objects_cached")}
TIER_WATCHES = {
    **COMMON_WATCHES,
    "hit_rate": Watch("down", 0.05, 0.0),
    "misses_per_s": Watch("up", 1.0, 1.0),
    "upstream_requests_per_s": Watch("up", 1.0, 1.0),
    "bytes_fetched_per_s": Watch("up", float(1 << 20), 1.0),
    "evictions_per_s": Watch("up", 1.0, 1.0),
    "p99_ms.get_objects": Watch("up", 5.0, 1.0),
}
TIER_RULES = (
    Rule("rejected_objects_per_s", ">", 0, severity="critical"),  # corrupt objects from upstream
    Rule("server_errors_per_s", ">", 0),
    Rule("epoch_check_failures_per_s", ">", 0, for_polls=3),      # can't learn of policy changes
)

PROFILES = {
    "daemon": Profile(
        "scion-daemon",
        rates={**TIER_RATES, "snapshot_errors_per_s": ("counters", "snapshot.errors"),
               "snapshot_stale_per_s": ("counters", "snapshot.stale")},
        ratios=TIER_RATIOS, gauges=TIER_GAUGES, latency=("get_objects",), watches=TIER_WATCHES,
        rules=TIER_RULES + (Rule("snapshot_errors_per_s", ">", 0),)),
    "cache": Profile("scion-cache", rates=TIER_RATES, ratios=TIER_RATIOS, gauges=TIER_GAUGES,
                     latency=("get_objects",), watches=TIER_WATCHES, rules=TIER_RULES),
    "antique": Profile(
        "antique-landing-queue",
        rates={"land_requests_per_s": ("antique", "land.requests"), "landed_per_s": ("antique", "land.landed"),
               "land_retries_per_s": ("antique", "land.retries"), "land_conflicts_per_s": ("antique", "land.conflicts"),
               "land_deadline_per_s": ("antique", "land.deadline")},
        ratios={"retries_per_landing": (("antique", "land.retries"), (("antique", "land.landed"),))},
        gauges={"land_queue_depth": ("antique", "land.queue_depth"),
                "postmerge_queued": ("antique", "postmerge.queued"),
                "postmerge_running": ("antique", "postmerge.running")},
        latency=("antique.land",),
        watches={**COMMON_WATCHES, "land_retries_per_s": Watch("up", 0.5, 1.0),
                 "retries_per_landing": Watch("up", 1.0, 1.0), "land_queue_depth": Watch("up", 5.0, 1.0),
                 "land_conflicts_per_s": Watch("up", 0.5, 1.0), "postmerge_queued": Watch("up", 10.0, 1.0),
                 "p99_ms.antique.land": Watch("up", 50.0, 1.0)},
        rules=(Rule("land_deadline_per_s", ">", 0, severity="critical"),  # landings gave up (R-01)
               Rule("server_errors_per_s", ">", 0))),
    "server": Profile(
        "scion-server",
        latency=("get_objects", "create_changeset", "read_file", "log"),
        watches={**COMMON_WATCHES, "p99_ms.get_objects": Watch("up", 5.0, 1.0),
                 "p99_ms.create_changeset": Watch("up", 20.0, 1.0)},
        rules=(Rule("server_errors_per_s", ">", 0),)),
}


# ================================================================================ measurement
def _at(d, path, default=0):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return default
        d = d[p]
    return d if isinstance(d, (int, float)) and not isinstance(d, bool) else default


def _common(stats: dict) -> dict:
    """Totals every component reports: requests, errors by class, rate limiting."""
    errors = stats.get("errors", {}) or {}
    counters = stats.get("counters", {}) or {}
    return {"requests": sum(v for k, v in counters.items() if k.startswith("rpc.")),
            "server_errors": sum(v for k, v in errors.items() if str(k).startswith("5")),
            "client_errors": sum(v for k, v in errors.items() if str(k).startswith("4")),
            "rate_limited": counters.get("rate_limited", 0)}


def extract(profile: Profile, prev: dict, cur: dict, seconds: float) -> dict:
    """The metrics of one interval: rates per second and ratios from the counters' growth, gauges
    and latency percentiles as reported. ``prev`` is empty after a restart: counters start at 0."""
    seconds = max(seconds, 1e-6)

    def delta(path):
        return max(0, _at(cur, path) - _at(prev, path))

    m: dict[str, float | None] = {}
    pc, cc = _common(prev), _common(cur)
    for k in cc:
        m[f"{k}_per_s"] = max(0, cc[k] - pc.get(k, 0)) / seconds
    for name, path in profile.rates.items():
        m[name] = delta(path) / seconds
    for name, (num, dens) in profile.ratios.items():
        d = sum(delta(p) for p in dens)
        m[name] = delta(num) / d if d else None  # nothing happened: no ratio this interval
    for name, path in profile.gauges.items():
        m[name] = _at(cur, path, None)
    for method in profile.latency:
        p99 = _at(cur, ("latency", method, "p99_ms"), None)
        if p99 is not None:
            m[f"p99_ms.{method}"] = p99
    return m


class Baseline:
    """An exponentially weighted mean and variance (West's incremental form)."""

    def __init__(self):
        self.n, self.mean, self.var = 0, 0.0, 0.0

    def update(self, x: float, alpha: float) -> None:
        if self.n == 0:
            self.mean, self.var = x, 0.0
        else:
            diff = x - self.mean
            incr = alpha * diff
            self.mean += incr
            self.var = (1 - alpha) * (self.var + diff * incr)
        self.n += 1

    @property
    def std(self) -> float:
        return math.sqrt(max(self.var, 0.0))

    def judge(self, x: float, watch: Watch, z: float) -> bool:
        """Is ``x`` outside the usual range, in the direction that matters?"""
        dev = x - self.mean
        if (watch.direction == "up" and dev <= 0) or (watch.direction == "down" and dev >= 0):
            return False
        return abs(dev) > max(z * self.std, watch.floor, watch.relative * abs(self.mean))


@dataclass
class Finding:
    kind: str  # novel, threshold, unreachable, restarted or resolved
    component: str
    target: str
    severity: str
    message: str
    metric: str | None = None
    value: float | None = None
    baseline: float | None = None
    rule: str | None = None
    at: float = field(default_factory=time.time)
    logs: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def text(self) -> str:
        """Slack-style text: one line for the finding, then the log lines around it."""
        mark = {"critical": ":rotating_light:", "warning": ":warning:", "info": ":white_check_mark:"}[self.severity]
        lines = [f"{mark} *{self.component}* {self.kind}: {_esc(self.message)} ({_esc(self.target)})"]
        for e in self.logs[-10:]:
            times = f" (x{e['repeats']})" if e.get("repeats", 1) > 1 else ""
            lines.append(f"> {_esc(e.get('level', '?'))}: {_esc(e.get('message', ''))}{times}")
        return "\n".join(lines)


def _esc(text) -> str:
    """Shown as itself in Slack: a log line can't mention @channel or carry markup (threat T5)."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(v) -> str:
    return "n/a" if v is None else f"{v:.4g}"


# ================================================================================ the watcher
class Superfan:
    def __init__(self, url: str, profile: str | Profile = "daemon", rules=(), default_rules: bool = True,
                 user: str = "superfan", token: str | None = None, tls: ClientTls | None = None,
                 webhook: str | None = None, z: float = 4.0, warmup: int = 5, alpha: float = 0.1,
                 log_level: str = "info", out=None, timeout: float = 10.0, as_json: bool = False):
        self.profile = PROFILES[profile] if isinstance(profile, str) else profile
        self.url = url
        # one retry: a keep-alive connection the component closed while idle is not an outage
        self.client = RpcClient(url, user=user, token=token, tls=tls, timeout=timeout, retries=1, max_throttle=0)
        self.rules = (list(self.profile.rules) if default_rules else []) + [Rule.parse(r) for r in rules]
        self.z, self.warmup, self.alpha, self.log_level = z, warmup, alpha, log_level
        self.out = out if out is not None else sys.stdout
        self.as_json = as_json
        self.webhook = webhook
        self.notifier = Notifier(lambda _: []) if webhook else None
        self.baselines: dict[str, Baseline] = {}
        self.active: dict[tuple, Finding] = {}
        self.breaches: dict[str, int] = {}
        self.prev: tuple[float, dict] | None = None
        self.metrics: dict = {}
        self.findings: deque = deque(maxlen=1000)
        self.polls = 0
        self.log_seq = 0
        self.logs: deque = deque(maxlen=500)  # (poll that fetched it, entry)
        self.logs_available: bool | None = None
        self.down_since: float | None = None
        self.unknown_rule_metrics: list[str] | None = None
        self.agent = None  # a superfan_agent.Investigator: Claude investigates each finding (FR-OP-09)

    def close(self) -> None:
        if self.agent is not None:
            self.agent.close()  # let running investigations post their analyses
        if self.notifier is not None:
            self.notifier.flush()
        self.client.close_all()

    # -- one poll ---------------------------------------------------------------------------------
    def poll_once(self) -> list[Finding]:
        """Read the component once; returns the findings raised (also printed and posted)."""
        self.polls += 1
        now = time.monotonic()
        try:
            stats = self.client.get_json("/stats")
        except (OSError, http.client.HTTPException, RemoteError, ValueError) as e:
            return self._emit(self._unreachable(e))
        found = []
        if ("unreachable", None) in self.active:
            del self.active[("unreachable", None)]
            found.append(self._finding("resolved", "info", f"reachable again after {time.time() - self.down_since:.0f} s"))
            self.down_since = None
        prev = restarted = None
        if self.prev is not None:
            t0, prev = self.prev
            # uptime grows by the time between polls; less means a new process, even one that has
            # already lived longer than its predecessor had at the last poll (a fast crash loop)
            grown = _at(prev, ("uptime_s",)) + (now - t0) * 0.9 - RESTART_SLACK
            if _at(stats, ("uptime_s",)) < max(_at(prev, ("uptime_s",)), grown):
                restarted = f"restarted: uptime {_at(prev, ('uptime_s',)):.0f} s → {_at(stats, ('uptime_s',)):.0f} s"
                prev, self.log_seq = {}, 0  # counters and log sequence numbers start again
        self._fetch_logs()
        if restarted:  # with the component's first log lines since the restart
            found.append(self._finding("restarted", "warning", restarted))
        if prev is not None:
            self.metrics = extract(self.profile, prev, stats, now - t0)
            if self.unknown_rule_metrics is None:
                self.unknown_rule_metrics = sorted({r.metric for r in self.rules} - set(self.metrics))
                for m in self.unknown_rule_metrics:
                    print(f"superfan: no metric {m!r} in {self.profile.name}; known: {', '.join(sorted(self.metrics))}",
                          file=sys.stderr)
            found += self._judge(self.metrics)
        self.prev = (now, stats)
        return self._emit(found)

    def _fetch_logs(self) -> None:
        """New log entries since the last poll (FR-OP-08). Without permission to read logs, the
        superfan works from telemetry alone and asks again every tenth poll."""
        if self.logs_available is False and self.polls % 10:
            return
        for _ in range(2):
            try:
                r = self.client.get_json(f"/logs?since={self.log_seq}&level={self.log_level}&limit=500")
            except RemoteError as e:
                if e.status in (401, 403):
                    self.logs_available = False
                return
            except (OSError, http.client.HTTPException, ValueError):
                return
            self.logs_available = True
            if r.get("last_seq", 0) < self.log_seq:  # the component restarted between polls
                self.log_seq = 0
                continue
            for e in r.get("entries", []):
                self.logs.append((self.polls, e))
                self.log_seq = max(self.log_seq, e.get("seq", 0))
            return

    def _recent_logs(self, limit: int = 20) -> list[dict]:
        """The entries fetched by this poll and the one before, so logged during the last two
        intervals: the lines around the anomaly. A repeated message appears once, at its latest count."""
        latest: dict[tuple, dict] = {}
        for poll, e in self.logs:
            if poll >= self.polls - 1:
                latest.pop((e.get("level"), e.get("message")), None)
                latest[(e.get("level"), e.get("message"))] = e
        return list(latest.values())[-limit:]

    # -- judgement --------------------------------------------------------------------------------
    def _judge(self, metrics: dict) -> list[Finding]:
        found = []
        for name, watch in self.profile.watches.items():
            x = metrics.get(name)
            if x is None:
                continue  # nothing to judge this interval (no lookups, no landings)
            b = self.baselines.setdefault(name, Baseline())
            key = ("novel", name)
            if b.n < self.warmup:
                b.update(x, self.alpha)
                continue
            novel = b.judge(x, watch, self.z)
            if novel and key not in self.active:
                way = "up" if x > b.mean else "down"
                found.append(self._raise(key, self._finding(
                    "novel", "warning", f"{name} is {_fmt(x)}, {way} from its usual {_fmt(b.mean)} "
                                        f"(± {_fmt(b.std)})", metric=name, value=x, baseline=b.mean)))
            elif not novel and key in self.active:
                del self.active[key]
                found.append(self._finding("resolved", "info", f"{name} is back to {_fmt(x)} "
                                                               f"(usual {_fmt(b.mean)})", metric=name, value=x,
                                           baseline=b.mean))
            # Anomalies teach the baseline slowly: a lasting new level becomes the new normal.
            b.update(x, self.alpha * (0.1 if novel else 1.0))
        for rule in self.rules:
            x = metrics.get(rule.metric)
            if x is None:
                continue
            key = ("threshold", rule.describe())
            if rule.breached(x):
                self.breaches[key[1]] = self.breaches.get(key[1], 0) + 1
                if self.breaches[key[1]] >= rule.for_polls and key not in self.active:
                    found.append(self._raise(key, self._finding(
                        "threshold", rule.severity, f"{rule.metric} is {_fmt(x)}: {rule.describe()}",
                        metric=rule.metric, value=x, rule=rule.describe())))
            else:
                self.breaches[key[1]] = 0
                if key in self.active:
                    del self.active[key]
                    found.append(self._finding("resolved", "info", f"{rule.metric} is {_fmt(x)}: no longer "
                                                                   f"{rule.describe()}", metric=rule.metric,
                                               value=x, rule=rule.describe()))
        return found

    def _unreachable(self, error) -> list[Finding]:
        key = ("unreachable", None)
        if key in self.active:
            return []
        self.down_since = time.time()
        f = self._finding("unreachable", "critical", f"does not answer: {error}")
        f.logs = [e for _, e in self.logs][-10:]  # the last things it logged before going quiet
        return [self._raise(key, f)]

    def _raise(self, key, finding: Finding) -> Finding:
        self.active[key] = finding
        return finding

    def _finding(self, kind, severity, message, **kw) -> Finding:
        f = Finding(kind, self.profile.name, self.url, severity, message, **kw)
        if kind != "unreachable":
            f.logs = self._recent_logs()
        return f

    def _emit(self, found: list[Finding]) -> list[Finding]:
        for f in found:
            self.findings.append(f)
            print(json.dumps(f.to_dict(), default=str) if self.as_json else f.text(), file=self.out, flush=True)
            if self.notifier is not None:
                self.notifier.send([self.webhook], {"text": f.text(), "finding": f.to_dict()})
            if self.agent is not None:
                self.agent.submit(f)  # off this thread: the watcher never waits for the agent
        return found

    # -- the loop ---------------------------------------------------------------------------------
    def run(self, interval: float = 30.0, polls: int | None = None) -> None:
        n = 0
        while polls is None or n < polls:
            started = time.monotonic()
            try:
                self.poll_once()
            except Exception as e:  # noqa: BLE001 - a monitor must keep watching
                print(f"superfan: poll failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            n += 1
            if polls is None or n < polls:
                time.sleep(max(0.0, interval - (time.monotonic() - started)))


def load_rules(path: str) -> list[Rule]:
    """Threshold rules from a JSON file: a list of rule objects or rule strings."""
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a list of rules")
    return [Rule.parse(r) for r in data]

"""Rate limiting per principal and request class, with concurrency caps (FR-OP-06, threat D1).

Request classes (API.md): ``read`` cheap metadata, ``heavy`` expensive reads (blame, search, text
diffs), ``write`` anything that creates data, ``objects`` the object protocol, whose cost is the
number of objects requested. Limits come from ``rate_limits`` in ``deployment.json`` and can be
set per principal::

    {"default": {"heavy": {"rate": 20, "burst": 40, "concurrency": 8}},
     "principals": {"ci-bot": {"write": {"rate": 500, "burst": 1000}}}}

A refused request raises ``RateLimited``; the RPC layer answers 429 with ``Retry-After``. Limits
are per server process, not global (08 §8.3, D1).
"""
from __future__ import annotations

import threading
import time
from contextlib import contextmanager

DEFAULT_LIMITS = {
    "read": {"rate": 500.0, "burst": 1000.0, "concurrency": 64},
    "heavy": {"rate": 20.0, "burst": 40.0, "concurrency": 8},
    "write": {"rate": 100.0, "burst": 200.0, "concurrency": 32},
    "objects": {"rate": 200_000.0, "burst": 400_000.0, "concurrency": 64},
}
UNLIMITED = {"rate": float("inf"), "burst": float("inf"), "concurrency": 1 << 30}


class RateLimited(Exception):
    def __init__(self, retry_after: float, reason: str):
        self.retry_after = retry_after
        super().__init__(reason)


class TokenBucket:
    def __init__(self, rate: float, burst: float):
        self.rate, self.burst = float(rate), float(burst)
        self.tokens, self.last = self.burst, time.monotonic()

    def take(self, n: float) -> float:
        """Take ``n`` tokens: 0 on success, otherwise the seconds until they are available."""
        now = time.monotonic()
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= n:
            self.tokens -= n
            return 0.0
        return (n - self.tokens) / self.rate if self.rate > 0 else 60.0


class RateLimiter:
    def __init__(self, config: dict | None = None, exempt=()):
        config = config or {}
        self.default = {k: dict(v) for k, v in DEFAULT_LIMITS.items()}
        for klass, v in config.get("default", {}).items():
            self.default.setdefault(klass, {}).update(v)
        self.per_principal: dict = config.get("principals", {})
        self.exempt = set(exempt)
        self._buckets: dict[tuple[str, str], TokenBucket] = {}
        self._inflight: dict[tuple[str, str], int] = {}
        self._lock = threading.Lock()
        self.rejected = {"rate": 0, "concurrency": 0}

    MAX_BUCKETS = 10_000

    def _prune(self) -> None:
        """Forget principals with a full bucket and nothing in flight: a new bucket starts full, so
        nothing changes for them (called with the lock held)."""
        now = time.monotonic()
        for key, b in list(self._buckets.items()):
            if not self._inflight.get(key) and b.tokens + (now - b.last) * b.rate >= b.burst:
                del self._buckets[key]
                self._inflight.pop(key, None)

    def limits(self, principal: str, klass: str) -> dict:
        lim = dict(self.default.get(klass, UNLIMITED))
        lim.update(self.per_principal.get(principal, {}).get(klass, {}))
        return lim

    @contextmanager
    def acquire(self, principal: str | None, klass: str, cost: float = 1.0):
        principal = principal or "anonymous"
        if principal in self.exempt:
            yield
            return
        key = (principal, klass)
        lim = self.limits(principal, klass)
        with self._lock:
            inflight = self._inflight.get(key, 0)
            if inflight >= lim.get("concurrency", UNLIMITED["concurrency"]):
                self.rejected["concurrency"] += 1
                raise RateLimited(0.05, f"too many concurrent {klass} requests for {principal}")
            bucket = self._buckets.get(key)
            if bucket is None:
                if len(self._buckets) >= self.MAX_BUCKETS:
                    self._prune()
                bucket = self._buckets[key] = TokenBucket(lim["rate"], lim["burst"])
            wait = bucket.take(min(cost, bucket.burst))  # one request never needs more than a full bucket
            if wait > 0:
                self.rejected["rate"] += 1
                raise RateLimited(wait, f"{klass} rate limit exceeded for {principal}")
            self._inflight[key] = inflight + 1
        try:
            yield
        finally:
            with self._lock:
                self._inflight[key] -= 1

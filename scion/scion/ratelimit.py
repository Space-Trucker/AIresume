"""Rate limiting: per-principal token buckets per request class, plus concurrency caps.

Request classes:
  read     cheap metadata reads (resolve, get_changeset, list_dir, ...)
  heavy    expensive reads (blame, grep, search, text diffs)
  write    anything that creates data (create_changeset, merge, rebase, put_objects, land)
  objects  the object protocol; cost is weighted by the number of objects requested

Limits come from the policy's "rate_limits" section and can be overridden per principal:

    "rate_limits": {
      "default": {"read": {"rate": 200, "burst": 400, "concurrency": 32}, ...},
      "principals": {"scion-cache": {"objects": {"rate": 1e6, "burst": 1e6}}}
    }
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


class RateLimited(Exception):
    def __init__(self, retry_after: float, reason: str):
        self.retry_after = retry_after
        super().__init__(reason)


class TokenBucket:
    def __init__(self, rate: float, burst: float):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last = time.monotonic()
        self.lock = threading.Lock()

    def take(self, n: float = 1.0) -> float:
        """Take ``n`` tokens; return 0 on success, or seconds to wait."""
        with self.lock:
            now = time.monotonic()
            self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= n:
                self.tokens -= n
                return 0.0
            return (n - self.tokens) / self.rate if self.rate > 0 else 60.0


class RateLimiter:
    def __init__(self, config: dict | None = None, exempt: set[str] | None = None):
        config = config or {}
        self.default = {k: dict(v) for k, v in DEFAULT_LIMITS.items()}
        for klass, v in config.get("default", {}).items():
            self.default.setdefault(klass, {}).update(v)
        self.per_principal: dict = config.get("principals", {})
        self.exempt = exempt or set()
        self._buckets: dict[tuple[str, str], TokenBucket] = {}
        self._inflight: dict[tuple[str, str], int] = {}
        self._lock = threading.Lock()
        self.rejections = 0

    def _limits(self, principal: str, klass: str) -> dict:
        lim = dict(self.default.get(klass, {"rate": 1e9, "burst": 1e9, "concurrency": 1 << 30}))
        lim.update(self.per_principal.get(principal, {}).get(klass, {}))
        return lim

    @contextmanager
    def acquire(self, principal: str | None, klass: str, cost: float = 1.0):
        principal = principal or "anonymous"
        if principal in self.exempt:
            yield
            return
        key = (principal, klass)
        lim = self._limits(principal, klass)
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = self._buckets[key] = TokenBucket(lim["rate"], lim["burst"])
            inflight = self._inflight.get(key, 0)
            if inflight >= lim.get("concurrency", 1 << 30):
                self.rejections += 1
                raise RateLimited(0.05, f"too many concurrent {klass} requests for {principal}")
            wait = bucket.take(min(cost, bucket.burst))
            if wait > 0:
                self.rejections += 1
                raise RateLimited(wait, f"{klass} rate limit exceeded for {principal}")
            self._inflight[key] = inflight + 1
        try:
            yield
        finally:
            with self._lock:
                self._inflight[key] -= 1

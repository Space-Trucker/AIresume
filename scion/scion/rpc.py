"""RPC transport shared by every Scion component.

* JSON RPCs: ``POST /rpc/<method>`` with ``{"params": {...}}`` → ``{"result": ...}``.
* The object protocol (``get_objects``) uses a compact binary framing so caches can stream
  stored (compressed) bytes straight from memory:

      repeated:  [32-byte raw id][1-byte flags][4-byte big-endian length][compressed object]

* ``GET /healthz`` and ``GET /stats`` are served by every tier (the superfans watch ``/stats``).
* Transports: TCP (``http://host:port``) or a Unix socket (``unix:/path/to.sock``), which is how a
  client talks to its node's ``scion-daemon``.
"""
from __future__ import annotations

import http.client
import json
import os
import socket
import socketserver
import struct
import threading
import time
import traceback
from collections import Counter, deque
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .iam import PermissionDenied
from .ratelimit import RateLimited, RateLimiter

_OBJ_HEADER = struct.Struct(">32sBI")
MAX_BODY = 512 * 1024 * 1024


# =============================================================================================
# Object framing
# =============================================================================================
def pack_objects(items) -> bytes:
    out = bytearray()
    for oid, flags, stored in items:
        out += _OBJ_HEADER.pack(bytes.fromhex(oid), flags, len(stored))
        out += stored
    return bytes(out)


def unpack_objects(data: bytes) -> list[tuple[str, int, bytes]]:
    out = []
    pos = 0
    n = len(data)
    while pos < n:
        raw, flags, length = _OBJ_HEADER.unpack_from(data, pos)
        pos += _OBJ_HEADER.size
        out.append((raw.hex(), flags, data[pos:pos + length]))
        pos += length
    return out


# =============================================================================================
# Errors
# =============================================================================================
class RpcError(Exception):
    def __init__(self, status: int, code: str, message: str, data=None):
        self.status = status
        self.code = code
        self.data = data
        super().__init__(message)


class RemoteError(Exception):
    def __init__(self, status: int, code: str, message: str, data=None):
        self.status = status
        self.code = code
        self.data = data
        super().__init__(f"{code}: {message}")


# =============================================================================================
# Metrics
# =============================================================================================
class Metrics:
    def __init__(self):
        self.counters: Counter = Counter()
        self.latency: dict[str, deque] = {}
        self.started = time.time()
        self._lock = threading.Lock()

    def incr(self, key: str, n: int = 1) -> None:
        with self._lock:
            self.counters[key] += n

    def observe(self, method: str, seconds: float) -> None:
        with self._lock:
            self.latency.setdefault(method, deque(maxlen=2000)).append(seconds)

    def snapshot(self) -> dict:
        with self._lock:
            lat = {}
            for m, d in self.latency.items():
                s = sorted(d)
                if s:
                    lat[m] = {
                        "count": len(s),
                        "p50_ms": round(1000 * s[len(s) // 2], 3),
                        "p99_ms": round(1000 * s[min(len(s) - 1, int(len(s) * 0.99))], 3),
                    }
            return {"uptime_s": round(time.time() - self.started, 1),
                    "counters": dict(self.counters), "latency": lat}


# =============================================================================================
# Server side
# =============================================================================================
TIER_PRINCIPALS = {"cache": "scion-cache", "daemon": "scion-daemon"}


@dataclass
class Caller:
    principal: str | None
    tier: str
    on_behalf: str | None = None

    @property
    def user(self) -> str | None:
        """The identity whose permissions apply to this request."""
        return self.on_behalf if self.on_behalf is not None else self.principal


@dataclass
class Method:
    fn: object
    klass: str = "read"
    binary_in: bool = False
    binary_out: bool = False
    tiers: tuple[str, ...] | None = None  # allowed caller tiers; None = any
    cost: object = None


class Service:
    """Base class for anything served over RPC."""

    tier = "service"

    def __init__(self, policy=None, limiter: RateLimiter | None = None, verbose: bool = False):
        from .iam import Policy

        self.policy = policy or Policy()
        self.limiter = limiter or RateLimiter(self.policy.rate_limits,
                                              exempt=set(self.policy.service_principals))
        self.methods: dict[str, Method] = {}
        self.metrics = Metrics()
        self.verbose = verbose

    def register(self, name: str, fn, klass: str = "read", binary_in: bool = False,
                 binary_out: bool = False, tiers=None, cost=None) -> None:
        self.methods[name] = Method(fn, klass, binary_in, binary_out, tuple(tiers) if tiers else None, cost)

    def authenticate(self, headers) -> Caller:
        principal = headers.get("X-Scion-User") or None
        auth = headers.get("Authorization") or ""
        token = auth[7:] if auth.startswith("Bearer ") else None
        if not self.policy.authenticate(principal, token):
            raise RpcError(401, "unauthenticated", "bad or missing credentials")
        tier = headers.get("X-Scion-Tier") or "client"
        expected = TIER_PRINCIPALS.get(tier)
        if expected is not None and principal != expected:
            raise RpcError(403, "bad_tier", f"tier {tier!r} requires principal {expected!r}")
        on_behalf = headers.get("X-Scion-On-Behalf-Of") or None
        if on_behalf is not None and not self.policy.is_service(principal):
            raise RpcError(403, "forbidden", "only service principals may act on behalf of users")
        return Caller(principal, tier, on_behalf)

    def dispatch(self, name: str, body: bytes, caller: Caller) -> tuple[bytes, str]:
        m = self.methods.get(name)
        if m is None:
            raise RpcError(404, "unknown_method", f"no such method {name}")
        if m.tiers is not None and caller.tier not in m.tiers:
            self.metrics.incr("tiering.rejected")
            raise RpcError(403, "tiering", f"{self.tier} does not serve {name} to tier {caller.tier!r}; "
                                           f"allowed: {', '.join(m.tiers)}")
        if m.binary_in:
            params = body
        else:
            params = json.loads(body or b"{}").get("params", {}) if body else {}
        cost = m.cost(params) if m.cost else 1.0
        t0 = time.perf_counter()
        with self.limiter.acquire(caller.principal if caller.on_behalf is None else caller.on_behalf,
                                  m.klass, cost):
            result = m.fn(caller, params)
        self.metrics.observe(name, time.perf_counter() - t0)
        self.metrics.incr(f"rpc.{name}")
        if m.binary_out:
            return result, "application/octet-stream"
        return json.dumps({"result": result}).encode(), "application/json"

    def handle_get(self, path: str, query: dict, caller: Caller):
        return None

    def stats(self) -> dict:
        return {"tier": self.tier, **self.metrics.snapshot()}

    def health(self) -> dict:
        return {"ok": True, "tier": self.tier}


def _error_body(code: str, message: str, data=None) -> bytes:
    return json.dumps({"error": {"code": code, "message": message, "data": data}}).encode()


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "scion/1"

    def address_string(self):
        ca = self.client_address
        return str(ca[0]) if isinstance(ca, tuple) and ca else "unix"

    def log_message(self, fmt, *args):
        if self.server.service.verbose:
            super().log_message(fmt, *args)

    def _send(self, status: int, body: bytes, ctype: str = "application/json", headers=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        service: Service = self.server.service
        u = urlparse(self.path)
        try:
            if u.path == "/healthz":
                return self._send(200, json.dumps(service.health()).encode())
            if u.path == "/stats":
                return self._send(200, json.dumps(service.stats()).encode())
            caller = service.authenticate(self.headers)
            r = service.handle_get(u.path, parse_qs(u.query), caller)
            if r is None:
                return self._send(404, b"not found", "text/plain")
            status, ctype, body = r
            return self._send(status, body, ctype)
        except RpcError as e:
            return self._send(e.status, _error_body(e.code, str(e)))
        except Exception as e:  # pragma: no cover - defensive
            traceback.print_exc()
            return self._send(500, _error_body("internal", str(e)))

    def do_POST(self):
        service: Service = self.server.service
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            return self._send(413, _error_body("too_large", "request body too large"))
        body = self.rfile.read(length) if length else b""
        if not u.path.startswith("/rpc/"):
            return self._send(404, _error_body("not_found", u.path))
        method = u.path[len("/rpc/"):]
        from .repo import MergeConflict, NotFound  # local import avoids a cycle

        try:
            caller = service.authenticate(self.headers)
            out, ctype = service.dispatch(method, body, caller)
            return self._send(200, out, ctype)
        except RpcError as e:
            return self._send(e.status, _error_body(e.code, str(e), e.data))
        except RateLimited as e:
            service.metrics.incr("rate_limited")
            return self._send(429, _error_body("rate_limited", str(e)),
                              headers={"Retry-After": f"{e.retry_after:.3f}"})
        except PermissionDenied as e:
            service.metrics.incr("denied")
            return self._send(403, _error_body("permission_denied", str(e)))
        except NotFound as e:
            return self._send(404, _error_body("not_found", str(e)))
        except MergeConflict as e:
            return self._send(409, _error_body("conflict", str(e), {"conflicts": e.conflicts, "at": e.at}))
        except (ValueError, KeyError, TypeError) as e:
            service.metrics.incr("errors.bad_request")
            return self._send(400, _error_body("bad_request", f"{type(e).__name__}: {e}"))
        except Exception as e:
            service.metrics.incr("errors.internal")
            traceback.print_exc()
            return self._send(500, _error_body("internal", f"{type(e).__name__}: {e}"))


class _ThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 256


class _UnixHTTPServer(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True
    request_queue_size = 256


class RpcServer:
    def __init__(self, service: Service, address: str):
        self.service = service
        self.address = address
        if address.startswith("unix:"):
            path = address[5:]
            if os.path.exists(path):
                os.unlink(path)
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            self.httpd = _UnixHTTPServer(path, _Handler)
            self.url = address
        else:
            u = urlparse(address if "://" in address else f"http://{address}")
            self.httpd = _ThreadingHTTPServer((u.hostname or "127.0.0.1", u.port or 0), _Handler)
            host, port = self.httpd.server_address[:2]
            self.url = f"http://{host}:{port}"
        self.httpd.service = service
        self._thread: threading.Thread | None = None

    def start(self) -> "RpcServer":
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True,
                                        name=f"rpc-{self.service.tier}")
        self._thread.start()
        return self

    def serve_forever(self) -> None:
        self.httpd.serve_forever()

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        if self.address.startswith("unix:"):
            try:
                os.unlink(self.address[5:])
            except FileNotFoundError:
                pass


# =============================================================================================
# Client side
# =============================================================================================
class _UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, path: str, timeout: float):
        super().__init__("localhost", timeout=timeout)
        self.unix_path = path

    def connect(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect(self.unix_path)
        self.sock = s


class RpcClient:
    def __init__(self, url: str, user: str | None = None, token: str | None = None,
                 tier: str = "client", timeout: float = 120.0, retries: int = 4):
        self.url = url
        self.user = user
        self.token = token
        self.tier = tier
        self.timeout = timeout
        self.retries = retries
        self._local = threading.local()
        if url.startswith("unix:"):
            self._unix = url[5:]
            self._host = None
        else:
            u = urlparse(url)
            self._unix = None
            self._host = (u.hostname, u.port or 80)

    def _conn(self) -> http.client.HTTPConnection:
        c = getattr(self._local, "conn", None)
        if c is None:
            if self._unix:
                c = _UnixHTTPConnection(self._unix, self.timeout)
            else:
                c = http.client.HTTPConnection(self._host[0], self._host[1], timeout=self.timeout)
            self._local.conn = c
        return c

    def _reset(self) -> None:
        c = getattr(self._local, "conn", None)
        if c is not None:
            c.close()
        self._local.conn = None

    def _headers(self, ctype: str, on_behalf: str | None) -> dict:
        h = {"Content-Type": ctype, "X-Scion-Tier": self.tier}
        if self.user:
            h["X-Scion-User"] = self.user
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if on_behalf:
            h["X-Scion-On-Behalf-Of"] = on_behalf
        return h

    def request(self, verb: str, path: str, body: bytes = b"", ctype: str = "application/json",
                on_behalf: str | None = None) -> tuple[int, dict, bytes]:
        attempt = 0
        throttled = 0
        while True:
            try:
                conn = self._conn()
                conn.request(verb, path, body=body, headers=self._headers(ctype, on_behalf))
                resp = conn.getresponse()
                data = resp.read()
                if resp.status == 429 and throttled < 8:
                    throttled += 1
                    time.sleep(min(2.0, float(resp.getheader("Retry-After") or 0.1)))
                    continue
                return resp.status, dict(resp.getheaders()), data
            except (ConnectionError, http.client.HTTPException, socket.timeout, OSError):
                self._reset()
                attempt += 1
                if attempt > self.retries:
                    raise
                time.sleep(min(2.0, 0.05 * (2 ** attempt)))

    def call(self, method: str, **params):
        status, _, data = self.request("POST", f"/rpc/{method}", json.dumps({"params": params}).encode())
        payload = json.loads(data) if data else {}
        if status != 200:
            err = payload.get("error", {})
            raise RemoteError(status, err.get("code", "error"), err.get("message", ""), err.get("data"))
        return payload["result"]

    def get_objects(self, ids: list[str], on_behalf: str | None = None) -> list[tuple[str, int, bytes]]:
        status, _, data = self.request("POST", "/rpc/get_objects", json.dumps({"params": {"ids": ids}}).encode(),
                                       on_behalf=on_behalf)
        if status != 200:
            err = json.loads(data).get("error", {})
            raise RemoteError(status, err.get("code", "error"), err.get("message", ""))
        return unpack_objects(data)

    def put_objects(self, items: list[tuple[str, int, bytes]]) -> dict:
        status, _, data = self.request("POST", "/rpc/put_objects", pack_objects(items),
                                       ctype="application/octet-stream")
        payload = json.loads(data)
        if status != 200:
            err = payload.get("error", {})
            raise RemoteError(status, err.get("code", "error"), err.get("message", ""))
        return payload["result"]

    def get_json(self, path: str):
        status, _, data = self.request("GET", path)
        if status != 200:
            raise RemoteError(status, "http", data[:200].decode("utf-8", "replace"))
        return json.loads(data)

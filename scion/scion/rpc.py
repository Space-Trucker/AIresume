"""The RPC transport every Scion component shares (07 §7.7, API.md).

* JSON RPCs: ``POST /rpc/<method>`` with ``{"params": {...}}`` returns ``{"result": ...}``; errors
  return ``{"error": {"code", "message", "data"}}`` with a stable HTTP status.
* The object protocol frames stored (compressed) objects so caches stream bytes as they hold them:
  ``[32-byte id][1-byte flags][4-byte big-endian length][stored bytes]``, repeated.
* ``GET /healthz`` and ``GET /stats`` are served by every tier (FR-OP-01/02).
* Endpoints: ``unix:/path`` (the node daemon), ``http://host:port`` (development) and
  ``https://host:port``: TLS on every TCP hop, with mutual TLS between tiers, where the client
  certificate's common name is the service principal (ADR-14).
"""
from __future__ import annotations

import http.client
import json
import math
import os
import socket
import socketserver
import ssl
import struct
import sys
import threading
import time
import traceback
from collections import Counter, deque
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote, urlparse

from .iam import TIER_PRINCIPALS, Identity, PermissionDenied
from .objects import ObjectError, ObjectTooLarge
from .ratelimit import RateLimited, RateLimiter
from .repo import MergeConflict, NotFound

_OBJ = struct.Struct(">32sBI")
MAX_BODY = 512 * 1024 * 1024
MAX_IDS_PER_REQUEST = 2000
TIERS = ("client", "daemon", "cache")
NON_IDEMPOTENT = {"update_ref"}  # never resent once the request may have reached the server


# ============================================================================== object framing
def pack_objects(items) -> bytes:
    out = bytearray()
    for oid, flags, stored in items:
        out += _OBJ.pack(bytes.fromhex(oid), flags, len(stored))
        out += stored
    return bytes(out)


def unpack_objects(data: bytes) -> list[tuple[str, int, bytes]]:
    out, pos, n = [], 0, len(data)
    while pos < n:
        if pos + _OBJ.size > n:
            raise ValueError("truncated object frame")
        raw, flags, length = _OBJ.unpack_from(data, pos)
        pos += _OBJ.size
        if pos + length > n:
            raise ValueError("truncated object frame")
        out.append((raw.hex(), flags, data[pos:pos + length]))
        pos += length
    return out


def ids_cost(params) -> float:
    ids = params.get("ids") if isinstance(params, dict) else None
    return float(len(ids)) if isinstance(ids, list) else 1.0


# ===================================================================================== errors
class RpcError(Exception):
    def __init__(self, status: int, code: str, message: str, data=None):
        self.status, self.code, self.data = status, code, data
        super().__init__(message)


class Unreachable(ConnectionError):
    """No connection could be made, so the request was never sent: any endpoint may take it."""


class RemoteError(Exception):
    """An error response from another component."""

    def __init__(self, status: int, code: str, message: str, data=None):
        self.status, self.code, self.data = status, code, data
        super().__init__(f"{code}: {message}")


# ==================================================================================== metrics
class Metrics:
    """Counters, error counts by status and latency percentiles per method (FR-OP-02)."""

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
                pick = lambda q: round(1000 * s[min(len(s) - 1, int(len(s) * q))], 3)  # noqa: E731
                lat[m] = {"count": len(s), "p50_ms": pick(0.5), "p90_ms": pick(0.9), "p99_ms": pick(0.99)}
            errors = {k.split(".", 1)[1]: v for k, v in self.counters.items() if k.startswith("errors.")}
            return {"uptime_s": round(time.time() - self.started, 1), "counters": dict(self.counters),
                    "errors": errors, "latency": lat}


# ======================================================================================= logs
class LogRing:
    """Recent structured log entries of one component, for operators and superfans (FR-OP-08,
    ADR-18). Recent-only by design: the ring keeps the last ``capacity`` entries. A message repeated
    back to back updates the last entry (its ``repeats``, time and sequence number) instead of
    adding one, so a burst of one warning can't push everything else out of the ring."""

    LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}
    MERGE_WINDOW = 60.0  # seconds within which a repeated message is merged into the last entry

    def __init__(self, capacity: int = 2000):
        self._d: deque = deque(maxlen=capacity)
        self._seq = 0
        self._lock = threading.Lock()

    def add(self, level: str, message: str, **fields) -> None:
        now = time.time()
        with self._lock:
            self._seq += 1
            last = self._d[-1] if self._d else None
            if (last is not None and last["level"] == level and last["message"] == message
                    and now - last["at"] < self.MERGE_WINDOW):
                last.update(seq=self._seq, at=now, fields=fields, repeats=last["repeats"] + 1)
                return
            self._d.append({"seq": self._seq, "at": now, "level": level, "message": message,
                            "fields": fields, "repeats": 1})

    def since(self, seq: int = 0, limit: int = 500, level: str = "info") -> list[dict]:
        """Entries after ``seq`` at ``level`` or above: the newest ``limit`` of them, oldest first."""
        if level not in self.LEVELS:
            raise ValueError(f"level must be one of {', '.join(self.LEVELS)}")
        floor = self.LEVELS[level]
        with self._lock:
            out = [dict(e) for e in self._d if e["seq"] > seq and self.LEVELS.get(e["level"], 20) >= floor]
        return out[-max(1, min(int(limit), 2000)):]

    @property
    def last_seq(self) -> int:
        return self._seq


# ================================================================================ server side
@dataclass
class Caller:
    principal: str | None
    tier: str = "client"
    on_behalf: str | None = None
    via: str = "trusted"  # how the principal was established: token, cert or trusted (development)

    @property
    def user(self) -> str | None:
        """The identity whose permissions apply (FR-IAM-08)."""
        return self.on_behalf if self.on_behalf is not None else self.principal


@dataclass
class Method:
    fn: object
    klass: str = "read"
    binary_in: bool = False
    binary_out: bool = False
    tiers: tuple | None = None  # caller tiers allowed; None means any
    cost: object = None


@dataclass
class TlsConfig:
    """Server-side TLS. With ``client_ca`` set, client certificates are verified when presented and
    service principals must authenticate with one (mutual TLS between tiers, ADR-14)."""
    cert: str
    key: str
    client_ca: str | None = None

    def context(self) -> ssl.SSLContext:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(self.cert, self.key)
        if self.client_ca:
            ctx.load_verify_locations(self.client_ca)
            ctx.verify_mode = ssl.CERT_OPTIONAL  # users present tokens; tiers present certificates
        return ctx


@dataclass
class ClientTls:
    """Client-side TLS: the CA that signed the servers' certificates, plus this component's own
    certificate when it is a tier (mutual TLS)."""
    ca: str
    cert: str | None = None
    key: str | None = None

    def context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context(cafile=self.ca)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        if self.cert:
            ctx.load_cert_chain(self.cert, self.key)
        return ctx


class Service:
    """Anything served over RPC: authentication, strict tiering, rate limits and metrics."""

    tier = "service"

    def __init__(self, identity: Identity | None = None, limiter: RateLimiter | None = None,
                 verbose: bool = False):
        self._identity = identity or Identity()
        self.limiter = limiter or self.make_limiter()
        self.methods: dict[str, Method] = {}
        self.metrics = Metrics()
        self.logs = LogRing()
        self.verbose = verbose
        self.mtls = False  # set by RpcServer when client certificates are verified

    def log(self, level: str, message: str, **fields) -> None:
        self.logs.add(level, message, **fields)
        if self.verbose:
            print(f"{self.tier} {level}: {message} {fields if fields else ''}", file=sys.stderr, flush=True)

    @property
    def identity(self) -> Identity:
        return self._identity

    def make_limiter(self) -> RateLimiter:
        return RateLimiter(self.identity.rate_limits, exempt=self.identity.service_principals)

    def register(self, name: str, fn, klass: str = "read", binary_in: bool = False, binary_out: bool = False,
                 tiers=None, cost=None) -> None:
        self.methods[name] = Method(fn, klass, binary_in, binary_out, tuple(tiers) if tiers else None, cost)

    # -- identity -------------------------------------------------------------------------------
    def authenticate(self, headers, peer_cn: str | None = None) -> Caller:
        ident = self.identity
        claimed = headers.get("X-Scion-User") or None
        tier = headers.get("X-Scion-Tier") or "client"
        if tier not in TIERS:
            raise RpcError(400, "bad_tier", f"unknown tier {tier!r}")
        auth = headers.get("Authorization") or ""
        token = auth[7:] if auth.startswith("Bearer ") else None
        if peer_cn is not None:
            # a verified client certificate names a service principal (ADR-14)
            if not ident.is_service(peer_cn):
                raise RpcError(401, "unauthenticated", "client certificates identify service principals only")
            if claimed not in (None, peer_cn):
                raise RpcError(401, "unauthenticated", "X-Scion-User does not match the client certificate")
            principal, via = peer_cn, "cert"
        elif self.mtls and ident.is_service(claimed):
            raise RpcError(401, "unauthenticated", f"{claimed} must authenticate with its client certificate")
        elif ident.tokens_required:
            if not ident.check_token(claimed, token):
                raise RpcError(401, "unauthenticated", "missing or invalid credentials")
            principal, via = claimed, "token"
        else:
            principal, via = claimed, "trusted"  # development mode: identities are not verified (08, S1)
        expected = TIER_PRINCIPALS.get(tier)
        if expected is not None and principal != expected:
            raise RpcError(403, "bad_tier", f"tier {tier!r} requires principal {expected!r}")
        on_behalf = headers.get("X-Scion-On-Behalf-Of") or None
        if on_behalf is not None and not ident.is_service(principal):
            raise RpcError(403, "forbidden", "only service principals may act on behalf of users")
        return Caller(principal, tier, on_behalf, via)

    # -- dispatch -------------------------------------------------------------------------------
    def dispatch(self, name: str, body: bytes, query: dict, caller: Caller) -> tuple[bytes, str]:
        m = self.methods.get(name)
        if m is None:
            raise RpcError(404, "unknown_method", f"no such method {name}")
        if m.tiers is not None and caller.tier not in m.tiers:
            self.metrics.incr("tiering.rejected")
            raise RpcError(403, "tiering", f"{self.tier} serves {name} only to tier(s) {', '.join(m.tiers)}, "
                                           f"not {caller.tier!r}")
        if m.binary_in:
            params = {k: v[-1] for k, v in query.items()}
            params["_body"] = body
        else:
            try:
                params = json.loads(body).get("params", {}) if body else {}
            except (ValueError, AttributeError):
                raise RpcError(400, "bad_request", "the body must be a JSON object") from None
            if not isinstance(params, dict):
                raise RpcError(400, "bad_request", "params must be an object")
        cost = m.cost(params) if m.cost else 1.0
        t0 = time.perf_counter()
        with self.limiter.acquire(caller.user, m.klass, cost):
            result = m.fn(caller, params)
        self.metrics.observe(name, time.perf_counter() - t0)
        self.metrics.incr(f"rpc.{name}")
        if m.binary_out:
            return result, "application/octet-stream"
        return json.dumps({"result": result}).encode(), "application/json"

    def handle_http(self, method: str, path: str, query: dict, headers, body: bytes, secure: bool):
        """Pages outside ``/rpc/`` (such as the review UI): return ``(status, content_type, body,
        headers)`` or None for 404. The page handler authenticates its own users."""
        return None

    def stats(self) -> dict:
        return {"tier": self.tier, **self.metrics.snapshot(),
                "rate_limiter": {"rejected": dict(self.limiter.rejected)}}

    def health(self) -> dict:
        return {"ok": True, "tier": self.tier}


def _error_body(code: str, message: str, data=None) -> bytes:
    return json.dumps({"error": {"code": code, "message": message, "data": data}}).encode()


def _peer_cn(conn) -> str | None:
    getpeercert = getattr(conn, "getpeercert", None)
    cert = getpeercert() if getpeercert else None
    for rdn in (cert or {}).get("subject", ()):
        for key, value in rdn:
            if key == "commonName":
                return value
    return None


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "scion/2"
    timeout = 300  # idle keep-alive connections are closed
    # Buffer each response so its headers and body leave in one write: separate small writes meet
    # delayed ACKs and Nagle's algorithm and cost ~40 ms per request.
    wbufsize = 1 << 16

    def setup(self):
        super().setup()
        if self.connection.family in (socket.AF_INET, socket.AF_INET6):
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server.track(self.connection, True)

    def finish(self):
        try:
            super().finish()
        finally:
            self.server.track(self.connection, False)

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
        if status >= 400:
            self.server.service.metrics.incr(f"errors.{status}")

    def _caller(self) -> Caller:
        return self.server.service.authenticate(self.headers, _peer_cn(self.connection))

    def _page(self, method: str, u, body: bytes = b""):
        service: Service = self.server.service
        try:
            r = service.handle_http(method, u.path, parse_qs(u.query), self.headers, body,
                                    isinstance(self.connection, ssl.SSLSocket))
            if r is None:
                return self._send(404, _error_body("not_found", u.path))
            status, ctype, payload = r[:3]
            return self._send(status, payload, ctype, r[3] if len(r) > 3 else None)
        except Exception as e:  # pragma: no cover - defensive
            traceback.print_exc(file=sys.stderr)
            return self._send(500, _error_body("internal", f"{type(e).__name__}: {e}"))

    def do_GET(self):
        service: Service = self.server.service
        u = urlparse(self.path)
        if u.path == "/healthz":
            return self._send(200, json.dumps(service.health()).encode())
        if u.path == "/stats":
            return self._send(200, json.dumps(service.stats()).encode())
        if u.path == "/logs":
            return self._logs(u)
        return self._page("GET", u)

    def _logs(self, u):
        """``GET /logs?since=SEQ&limit=N&level=warning``: for administrators, services and log readers."""
        service: Service = self.server.service
        try:
            caller = self._caller()
            if not service.identity.can_read_logs(caller.user):
                raise RpcError(403, "permission_denied", "logs are for administrators, services and log readers")
            q = parse_qs(u.query)
            entries = service.logs.since(int((q.get("since") or ["0"])[0]), int((q.get("limit") or ["500"])[0]),
                                         (q.get("level") or ["info"])[0])
            return self._send(200, json.dumps({"tier": service.tier, "entries": entries,
                                               "last_seq": service.logs.last_seq}, default=str).encode())
        except RpcError as e:
            return self._send(e.status, _error_body(e.code, str(e), e.data))
        except ValueError as e:
            return self._send(400, _error_body("bad_request", str(e)))

    def do_POST(self):
        service: Service = self.server.service
        u = urlparse(self.path)
        if self.headers.get("Transfer-Encoding"):
            self.close_connection = True  # the body is not read, so the connection cannot be reused
            return self._send(411, _error_body("length_required", "send a Content-Length, not a chunked body"))
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self.close_connection = True
            if length < 0:
                return self._send(400, _error_body("bad_request", "invalid Content-Length"))
            return self._send(413, _error_body("too_large", "request body too large"))
        body = self.rfile.read(length) if length else b""
        if not u.path.startswith("/rpc/"):
            return self._page("POST", u, body)
        method = u.path[len("/rpc/"):]
        try:
            out, ctype = service.dispatch(method, body, parse_qs(u.query), self._caller())
            return self._send(200, out, ctype)
        except RpcError as e:
            if e.status >= 500:
                service.log("error" if e.code == "integrity" else "warning", str(e), method=method, code=e.code)
            return self._send(e.status, _error_body(e.code, str(e), e.data))
        except RateLimited as e:
            service.metrics.incr("rate_limited")
            service.log("info", "rate limited", method=method, reason=str(e))
            return self._send(429, _error_body("rate_limited", str(e), {"retry_after": e.retry_after}),
                              headers={"Retry-After": str(max(1, math.ceil(e.retry_after)))})
        except PermissionDenied as e:
            service.metrics.incr("denied")
            service.log("info", "permission denied", method=method, reason=str(e)[:300])
            return self._send(403, _error_body("permission_denied", str(e)))
        except NotFound as e:
            return self._send(404, _error_body("not_found", str(e)))
        except MergeConflict as e:
            return self._send(409, _error_body("conflict", str(e), {"conflicts": e.conflicts, "at": e.at}))
        except ObjectTooLarge as e:
            return self._send(413, _error_body("too_large", str(e)))
        except ObjectError as e:
            return self._send(400, _error_body("integrity", str(e)))
        except (ValueError, KeyError, TypeError) as e:
            return self._send(400, _error_body("bad_request", f"{type(e).__name__}: {e}"))
        except Exception as e:
            status = getattr(e, "http_status", None)  # errors that carry their own status and code
            if status:
                service.log("warning", str(e), method=method, code=getattr(e, "code", "error"))
                return self._send(status, _error_body(getattr(e, "code", "error"), str(e)))
            traceback.print_exc(file=sys.stderr)
            service.log("error", f"{type(e).__name__}: {e}", method=method,
                        traceback=traceback.format_exc(limit=8)[-2000:])
            return self._send(500, _error_body("internal", f"{type(e).__name__}: {e}"))


class _ServerMixin:
    """Thread per connection (07 §7.4), TLS handshakes off the accept loop, and tracking of open
    connections so that ``stop()`` really takes the endpoint down."""

    daemon_threads = True
    request_queue_size = 256
    ssl_context: ssl.SSLContext | None = None
    handshake_timeout = 10.0

    def init_tracking(self):
        self._conns: set = set()
        self._conns_lock = threading.Lock()

    def track(self, conn, add: bool):
        with self._conns_lock:
            (self._conns.add if add else self._conns.discard)(conn)

    def get_request(self):
        sock, addr = super().get_request()
        if self.ssl_context is not None:
            sock = self.ssl_context.wrap_socket(sock, server_side=True, do_handshake_on_connect=False)
        return sock, addr

    def finish_request(self, request, client_address):
        if self.ssl_context is not None:
            try:
                request.settimeout(self.handshake_timeout)
                request.do_handshake()
                request.settimeout(None)
            except (ssl.SSLError, OSError):
                self.service.metrics.incr("tls.handshake_failures")
                return
        super().finish_request(request, client_address)

    def close_connections(self):
        with self._conns_lock:
            conns, self._conns = list(self._conns), set()
        for c in conns:
            try:
                c.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


class _TCPServer(_ServerMixin, socketserver.ThreadingMixIn, HTTPServer):
    pass


class _UnixServer(_ServerMixin, socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    pass


class RpcServer:
    """Serve a ``Service`` on ``unix:/path``, ``http://host:port`` or ``https://host:port``."""

    def __init__(self, service: Service, address: str, tls: TlsConfig | None = None, socket_mode: int = 0o660):
        self.service, self.address = service, address
        if address.startswith("unix:"):
            path = address[5:]
            if os.path.exists(path):
                os.unlink(path)
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            self.httpd = _UnixServer(path, _Handler)
            os.chmod(path, socket_mode)  # the daemon's socket relies on file permissions (ADR-14)
            self.url = address
        else:
            u = urlparse(address if "://" in address else f"http://{address}")
            if (u.scheme == "https") != (tls is not None):
                raise ValueError("https:// endpoints need a TLS configuration, and only they take one")
            self.httpd = _TCPServer((u.hostname or "127.0.0.1", u.port or 0), _Handler)
            host, port = self.httpd.server_address[:2]
            self.url = f"{u.scheme or 'http'}://{host}:{port}"
            if tls is not None:
                self.httpd.ssl_context = tls.context()
                service.mtls = tls.client_ca is not None
        self.httpd.init_tracking()
        self.httpd.service = service
        self._thread: threading.Thread | None = None

    def start(self) -> "RpcServer":
        self._thread = threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True,
                                        name=f"rpc-{self.service.tier}")
        self._thread.start()
        return self

    def serve_forever(self) -> None:
        self.httpd.serve_forever()

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.httpd.close_connections()
        if self.address.startswith("unix:"):
            try:
                os.unlink(self.address[5:])
            except FileNotFoundError:
                pass


# ================================================================================ client side
class _UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, path: str, timeout: float):
        super().__init__("localhost", timeout=timeout)
        self.unix_path = path

    def connect(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect(self.unix_path)
        except OSError:
            s.close()
            raise
        self.sock = s


class RpcClient:
    """A keep-alive client for one endpoint. Connection failures are retried with backoff (for
    requests that are safe to resend) and 429 responses are honored by waiting (FR-OP-06); a kept
    connection that the server closed while idle is replaced at once."""

    def __init__(self, url: str, user: str | None = None, token: str | None = None, tier: str = "client",
                 tls: ClientTls | None = None, timeout: float = 120.0, retries: int = 3, max_throttle: int = 8):
        self.url, self.user, self.token, self.tier = url, user, token, tier
        self.timeout, self.retries, self.max_throttle = timeout, retries, max_throttle
        self._local = threading.local()
        self._conns: list[tuple[threading.Thread, http.client.HTTPConnection]] = []
        self._lock = threading.Lock()
        self.throttled = 0
        if url.startswith("unix:"):
            self._unix, self._host, self._ctx = url[5:], None, None
        else:
            u = urlparse(url)
            if u.scheme not in ("http", "https"):
                raise ValueError(f"unsupported endpoint {url!r}")
            if u.scheme == "https" and tls is None:
                raise ValueError(f"{url} needs a TLS configuration (a CA certificate)")
            self._unix = None
            self._host = (u.hostname, u.port or (443 if u.scheme == "https" else 80))
            self._ctx = tls.context() if u.scheme == "https" else None

    def _new_conn(self) -> http.client.HTTPConnection:
        if self._unix:
            return _UnixHTTPConnection(self._unix, self.timeout)
        if self._ctx is not None:
            return http.client.HTTPSConnection(self._host[0], self._host[1], timeout=self.timeout, context=self._ctx)
        return http.client.HTTPConnection(self._host[0], self._host[1], timeout=self.timeout)

    def _conn(self, fresh: bool):
        """This thread's keep-alive connection. Connections of finished threads are closed as new
        ones open, so a client shared by short-lived request threads doesn't accumulate them."""
        c = getattr(self._local, "conn", None)
        if c is not None and fresh:
            self.close()
            c = None
        if c is None:
            c = self._local.conn = self._new_conn()
            with self._lock:
                live = []
                for t, x in self._conns:
                    if t.is_alive():
                        live.append((t, x))
                    else:
                        x.close()
                live.append((threading.current_thread(), c))
                self._conns = live
        return c

    def close(self) -> None:
        """Close this thread's connection."""
        c = getattr(self._local, "conn", None)
        if c is not None:
            c.close()
            self._local.conn = None
            with self._lock:
                self._conns = [(t, x) for t, x in self._conns if x is not c]

    def close_all(self) -> None:
        with self._lock:
            conns, self._conns = self._conns, []
        for _, c in conns:
            c.close()

    def __del__(self):
        try:
            self.close_all()
        except Exception:  # pragma: no cover - interpreter shutdown
            pass

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
                on_behalf: str | None = None, idempotent: bool = True) -> tuple[int, dict, bytes]:
        attempt = throttled = 0
        while True:
            # A request that must not be resent gets a fresh connection, so a stale keep-alive
            # connection can't fail it after it may have reached the server.
            conn = self._conn(fresh=not idempotent)
            reused, sent = conn.sock is not None, False
            try:
                if conn.sock is None:
                    conn.connect()
                sent = True
                conn.request(verb, path, body=body, headers=self._headers(ctype, on_behalf))
                resp = conn.getresponse()
                data = resp.read()
            except (OSError, http.client.HTTPException) as e:
                self.close()
                if reused:  # the server closed it while idle (after 300 s): reconnect at once
                    continue
                attempt += 1
                if (sent and not idempotent) or attempt > self.retries:
                    if not sent and not isinstance(e, ssl.SSLError):
                        raise Unreachable(f"{self.url}: {e}") from e
                    raise
                time.sleep(min(2.0, 0.05 * 2 ** attempt))
                continue
            if resp.status == 429 and throttled < self.max_throttle:
                throttled += 1
                self.throttled += 1
                time.sleep(min(5.0, self._retry_after(resp, data)))
                continue
            return resp.status, dict(resp.getheaders()), data

    @staticmethod
    def _retry_after(resp, data: bytes) -> float:
        try:
            return float(json.loads(data)["error"]["data"]["retry_after"])
        except (ValueError, KeyError, TypeError):
            try:
                return float(resp.getheader("Retry-After") or 1)
            except ValueError:
                return 1.0

    @staticmethod
    def _raise(status: int, data: bytes):
        try:
            err = json.loads(data).get("error", {})
        except ValueError:
            err = {"message": data[:200].decode("utf-8", "replace")}
        raise RemoteError(status, err.get("code", "error"), err.get("message", ""), err.get("data"))

    def call(self, method: str, **params):
        idempotent = method not in NON_IDEMPOTENT and not (method == "create_changeset" and params.get("update_ref"))
        status, _, data = self.request("POST", f"/rpc/{method}", json.dumps({"params": params}).encode(),
                                       idempotent=idempotent)
        if status != 200:
            self._raise(status, data)
        return json.loads(data)["result"]

    def get_objects(self, repo: str, ids: list[str], on_behalf: str | None = None) -> list[tuple[str, int, bytes]]:
        body = json.dumps({"params": {"repo": repo, "ids": ids}}).encode()
        status, _, data = self.request("POST", "/rpc/get_objects", body, on_behalf=on_behalf)
        if status != 200:
            self._raise(status, data)
        return unpack_objects(data)

    def put_objects(self, repo: str, items: list[tuple[str, int, bytes]]) -> dict:
        status, _, data = self.request("POST", f"/rpc/put_objects?repo={quote(repo)}", pack_objects(items),
                                       ctype="application/octet-stream")
        if status != 200:
            self._raise(status, data)
        return json.loads(data)["result"]

    def get_json(self, path: str):
        status, _, data = self.request("GET", path)
        if status != 200:
            self._raise(status, data)
        return json.loads(data)


class FailoverClient:
    """The same calls as ``RpcClient`` over several equivalent endpoints (NFR-09): an endpoint
    that can't be reached is skipped, and requests that are safe to resend also move on after
    other connection failures or a 5xx answer."""

    def __init__(self, urls, **kw):
        urls = [u for u in (urls.split(",") if isinstance(urls, str) else urls) if u]
        if not urls:
            raise ValueError("at least one endpoint is required")
        self.clients = [RpcClient(u, **kw) for u in urls]
        self._next = 0
        self.failovers = 0

    @property
    def url(self) -> str:
        return self.clients[self._next].url

    def __getattr__(self, name):  # user, token, tier ... are shared settings
        if name in ("user", "token", "tier", "throttled"):
            return getattr(self.clients[0], name)
        raise AttributeError(name)

    def _each(self, fn, idempotent: bool):
        last = None
        n = len(self.clients)
        for k in range(n):
            i = (self._next + k) % n
            try:
                out = fn(self.clients[i])
                self._next = i
                return out
            except Unreachable as e:
                last = e
            except (OSError, http.client.HTTPException) as e:
                if not idempotent:
                    raise
                last = e
            except RemoteError as e:
                if e.status < 500 or not idempotent:
                    raise
                last = e
            self.failovers += 1
        raise last

    def call(self, method: str, **params):
        idempotent = method not in NON_IDEMPOTENT and not (method == "create_changeset" and params.get("update_ref"))
        return self._each(lambda c: c.call(method, **params), idempotent)

    def get_objects(self, repo, ids, on_behalf=None):
        return self._each(lambda c: c.get_objects(repo, ids, on_behalf), True)

    def put_objects(self, repo, items):
        return self._each(lambda c: c.put_objects(repo, items), True)

    def get_json(self, path):
        return self._each(lambda c: c.get_json(path), True)

    def close(self) -> None:
        for c in self.clients:
            c.close_all()

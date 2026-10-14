"""Cloud Spanner as the metadata store (ADR-24; keys and indexes 06 §6.10; FR-ST-01…04).

The article keeps Scion's metadata in Spanner: moving a ref "is a compare-and-swap on a single
Spanner row", and servers "write the results back to Spanner". This module reaches Spanner through
its REST API with the standard library (CON-01):

* ``SpannerClient``: pools of sessions and HTTP connections, strong reads, read-write transactions
  rerun when Spanner aborts them (FR-ST-03), reads at one timestamp, and the schema;
* ``SpannerMetaStore``: the MetaStore contract (meta.py) for one repository. One database holds all
  the repositories of a deployment, and every key starts with the repository's name.

The ``metadata`` section of deployment.json chooses it (FR-ST-02)::

    {"backend": "spanner", "project": "my-project", "instance": "scion", "database": "scion",
     "endpoint": "https://spanner.googleapis.com",
     "token_command": ["gcloud", "auth", "print-access-token"]}

``endpoint`` may be the emulator's REST port instead (``http://127.0.0.1:9020``), which takes no
credentials. Otherwise the access token comes from ``token_command`` or, without one, from the GCE
metadata server for the machine's service account. Key files are not read: signing their tokens
needs RSA, which the standard library lacks. With ``"create": true`` a missing database (and, on the
emulator, a missing instance) is created; missing tables and indexes are always added.
"""
from __future__ import annotations

import base64
import http.client
import json
import os
import random
import re
import sqlite3
import ssl
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone

from .meta import AUDIT_FIELDS, CR_COLUMNS, GRANT_SECONDS, LANDING_FIELDS, SCHEMA, MetaStore, check_cr_columns

ABORTED, NOT_FOUND, ALREADY_EXISTS, UNAVAILABLE, RESOURCE_EXHAUSTED = 10, 5, 6, 14, 8
COMMIT_TS = "spanner.commit_timestamp()"
ROWS_PER_COMMIT = 2000  # mutations count cells: well under Spanner's 80,000 per commit
PAGE = 2000
METADATA_TOKEN_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"

DDL = [
    """CREATE TABLE changesets (repo STRING(MAX) NOT NULL, id STRING(64) NOT NULL, data BYTES(MAX) NOT NULL,
       created TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)) PRIMARY KEY (repo, id)""",
    "CREATE INDEX changesets_created ON changesets(repo, created, id)",
    """CREATE TABLE refs (repo STRING(MAX) NOT NULL, name STRING(MAX) NOT NULL, target STRING(64) NOT NULL,
       version INT64 NOT NULL, updated FLOAT64 NOT NULL) PRIMARY KEY (repo, name)""",
    """CREATE TABLE ref_log (repo STRING(MAX) NOT NULL, name STRING(MAX) NOT NULL,
       moved TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true), old STRING(64), `new` STRING(64),
       who STRING(MAX), `at` FLOAT64 NOT NULL) PRIMARY KEY (repo, name, moved DESC)""",
    """CREATE TABLE derived (repo STRING(MAX) NOT NULL, type STRING(MAX) NOT NULL, cs STRING(64) NOT NULL,
       value STRING(MAX) NOT NULL) PRIMARY KEY (repo, type, cs)""",
    """CREATE TABLE blob_index (repo STRING(MAX) NOT NULL, blob STRING(64) NOT NULL, path STRING(MAX) NOT NULL)
       PRIMARY KEY (repo, blob, path)""",
    """CREATE TABLE kv (repo STRING(MAX) NOT NULL, key STRING(MAX) NOT NULL, value STRING(MAX) NOT NULL)
       PRIMARY KEY (repo, key)""",
    """CREATE TABLE object_acl (repo STRING(MAX) NOT NULL, oid STRING(64) NOT NULL, prefix STRING(MAX) NOT NULL)
       PRIMARY KEY (repo, oid, prefix)""",
    """CREATE TABLE content_blobs (repo STRING(MAX) NOT NULL, blob STRING(64) NOT NULL, status STRING(1) NOT NULL)
       PRIMARY KEY (repo, blob)""",
    "CREATE INDEX content_blobs_status ON content_blobs(repo, status)",
    """CREATE TABLE content_trigrams (repo STRING(MAX) NOT NULL, trigram STRING(MAX) NOT NULL,
       blob STRING(64) NOT NULL) PRIMARY KEY (repo, trigram, blob)""",
    """CREATE TABLE object_grants (repo STRING(MAX) NOT NULL, oid STRING(64) NOT NULL, user STRING(MAX) NOT NULL,
       `at` FLOAT64 NOT NULL) PRIMARY KEY (repo, oid, user)""",
    """CREATE TABLE git_map (repo STRING(MAX) NOT NULL, git STRING(MAX) NOT NULL, cs STRING(64) NOT NULL)
       PRIMARY KEY (repo, git)""",
    "CREATE INDEX git_map_cs ON git_map(repo, cs)",
    """CREATE TABLE audit (repo STRING(MAX) NOT NULL, seq INT64 NOT NULL, `at` FLOAT64 NOT NULL, actor STRING(MAX),
       action STRING(MAX) NOT NULL, target STRING(MAX) NOT NULL, detail STRING(MAX) NOT NULL,
       prev STRING(64) NOT NULL, `hash` STRING(64) NOT NULL) PRIMARY KEY (repo, seq)""",
    "CREATE INDEX audit_action ON audit(repo, action, seq)",
    """CREATE TABLE crs (repo STRING(MAX) NOT NULL, id INT64 NOT NULL, title STRING(MAX) NOT NULL,
       description STRING(MAX) NOT NULL, author STRING(MAX) NOT NULL, target STRING(MAX) NOT NULL,
       head STRING(64) NOT NULL, state STRING(MAX) NOT NULL, created FLOAT64 NOT NULL, updated FLOAT64 NOT NULL,
       landed_cs STRING(64), landed_at FLOAT64, conflict STRING(MAX)) PRIMARY KEY (repo, id)""",
    "CREATE INDEX crs_state ON crs(repo, state, id)",
    """CREATE TABLE cr_revisions (repo STRING(MAX) NOT NULL, cr INT64 NOT NULL, rev INT64 NOT NULL,
       head STRING(64) NOT NULL, created FLOAT64 NOT NULL) PRIMARY KEY (repo, cr, rev)""",
    """CREATE TABLE cr_approvals (repo STRING(MAX) NOT NULL, cr INT64 NOT NULL, rev INT64 NOT NULL,
       user STRING(MAX) NOT NULL, created FLOAT64 NOT NULL) PRIMARY KEY (repo, cr, rev, user)""",
    """CREATE TABLE cr_comments (repo STRING(MAX) NOT NULL, cr INT64 NOT NULL, id INT64 NOT NULL,
       rev INT64 NOT NULL, user STRING(MAX) NOT NULL, path STRING(MAX), line INT64, body STRING(MAX) NOT NULL,
       created FLOAT64 NOT NULL) PRIMARY KEY (repo, cr, id)""",
    """CREATE TABLE landings (repo STRING(MAX) NOT NULL, cs STRING(64) NOT NULL, source STRING(64) NOT NULL,
       cr INT64, ref STRING(MAX) NOT NULL, landed_at FLOAT64 NOT NULL, head STRING(64) NOT NULL)
       PRIMARY KEY (repo, cs)""",
    "CREATE INDEX landings_source ON landings(repo, source)",
    "CREATE INDEX landings_head ON landings(repo, head)",
    """CREATE TABLE postmerge (repo STRING(MAX) NOT NULL, id INT64 NOT NULL, cs STRING(64) NOT NULL, cr INT64,
       ref STRING(MAX) NOT NULL, status STRING(MAX) NOT NULL, created FLOAT64 NOT NULL, started FLOAT64,
       finished FLOAT64, worker STRING(MAX), log STRING(MAX)) PRIMARY KEY (repo, id)""",
    "CREATE INDEX postmerge_status ON postmerge(repo, status, id)",
    "CREATE INDEX postmerge_cs ON postmerge(repo, cs, id)",
    "CREATE INDEX postmerge_ref ON postmerge(repo, ref, id)",
    """CREATE TABLE counters (repo STRING(MAX) NOT NULL, name STRING(MAX) NOT NULL, value INT64 NOT NULL)
       PRIMARY KEY (repo, name)""",
]
# every table but the counters, with its key columns (for paging) and its other columns, as in SQLite
TABLES = {
    "changesets": (("id",), ("data", "created")),
    "refs": (("name",), ("target", "version", "updated")),
    "ref_log": (("name", "moved"), ("old", "new", "who", "at")),
    "derived": (("type", "cs"), ("value",)),
    "blob_index": (("blob", "path"), ()),
    "kv": (("key",), ("value",)),
    "object_acl": (("oid", "prefix"), ()),
    "content_blobs": (("blob",), ("status",)),
    "content_trigrams": (("trigram", "blob"), ()),
    "object_grants": (("oid", "user"), ("at",)),
    "git_map": (("git",), ("cs",)),
    "audit": (("seq",), AUDIT_FIELDS[1:]),
    "crs": (("id",), CR_COLUMNS[1:]),
    "cr_revisions": (("cr", "rev"), ("head", "created")),
    "cr_approvals": (("cr", "rev", "user"), ("created",)),
    "cr_comments": (("cr", "id"), ("rev", "user", "path", "line", "body", "created")),
    "landings": (("cs",), LANDING_FIELDS[1:]),
    "postmerge": (("id",), ("cs", "cr", "ref", "status", "created", "started", "finished", "worker", "log")),
}
RESERVED = {"new", "at", "hash"}  # GoogleSQL keywords used as column names (quoted in SQL)
COLUMN_TYPES = {m.group(1): {c.strip("`"): t for c, t in re.findall(
    r"(`?\w+`?)\s+(STRING|BYTES|INT64|FLOAT64|TIMESTAMP|BOOL)\b", m.group(2))}
    for m in (re.match(r"CREATE TABLE (\w+) \((.*)\)\s+PRIMARY KEY", st, re.S) for st in DDL) if m}


def q(column: str) -> str:
    return f"`{column}`" if column in RESERVED else column


def _after(order, values, typed=()) -> tuple[str, dict]:
    """The keyset-pagination condition "(order...) > (values...)", spelled out: GoogleSQL has no
    row-value comparison. Columns in ``typed`` are timestamps."""
    ors, params = [], {}
    for i, c in enumerate(order):
        eqs = [f"{q(o)} = @k{j}" for j, o in enumerate(order[:i])]
        ors.append("(" + " AND ".join(eqs + [f"{q(c)} > @k{i}"]) + ")")
        params[f"k{i}"] = Typed(values[i], "TIMESTAMP") if c in typed else values[i]
    return " AND (" + " OR ".join(ors) + ")", params


class SpannerError(Exception):
    http_status = 503
    code = "metadata_unavailable"

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status  # the google.rpc code


class Aborted(SpannerError):
    """Spanner aborted a read-write transaction (a conflict); it must run again from the start."""


class Typed:
    """A parameter whose type can't be told from its value: a null, a timestamp, or a list of rows
    (``fields`` is ``[(name, code), ...]``)."""

    def __init__(self, value, code: str, fields=None):
        self.value, self.code, self.fields = value, code, fields


def _ptype(v) -> dict:
    if isinstance(v, Typed):
        if v.fields is not None:
            return {"code": "ARRAY", "arrayElementType": {"code": "STRUCT", "structType": {"fields": [
                {"name": n, "type": {"code": c}} for n, c in v.fields]}}}
        return {"code": v.code}
    if isinstance(v, bool):
        return {"code": "BOOL"}
    if isinstance(v, int):
        return {"code": "INT64"}
    if isinstance(v, float):
        return {"code": "FLOAT64"}
    if isinstance(v, (bytes, bytearray)):
        return {"code": "BYTES"}
    if isinstance(v, (list, tuple)):
        return {"code": "ARRAY", "arrayElementType": _ptype(v[0]) if v else {"code": "STRING"}}
    return {"code": "STRING"}


def _value(v):
    """A Python value as Spanner's JSON encoding: INT64 as strings, BYTES as base64."""
    if isinstance(v, Typed):
        if v.fields is not None:
            return [[_value(x) for x in row] for row in v.value]
        return v.value
    if v is None or isinstance(v, (bool, str)):
        return v
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return v if v == v and abs(v) != float("inf") else ("NaN" if v != v else ("Infinity" if v > 0 else "-Infinity"))
    if isinstance(v, (bytes, bytearray)):
        return base64.b64encode(bytes(v)).decode()
    if isinstance(v, (list, tuple)):
        return [_value(x) for x in v]
    raise TypeError(f"no Spanner encoding for {type(v).__name__}")


def _cell(t: str, v):
    """A mutation value for a column of type ``t``."""
    if v is None or v == COMMIT_TS:
        return v
    if t == "FLOAT64":
        return _value(float(v))
    if t == "INT64":
        return str(int(v))
    if t == "BOOL":
        return bool(v)
    return _value(v)


def _decode(v, t: dict):
    if v is None:
        return None
    code = t["code"]
    if code == "INT64":
        return int(v)
    if code == "FLOAT64":
        return float(v)
    if code == "BYTES":
        return base64.b64decode(v)
    if code == "ARRAY":
        return [_decode(x, t["arrayElementType"]) for x in v]
    if code == "STRUCT":
        return tuple(_decode(x, f["type"]) for x, f in zip(v, t["structType"]["fields"]))
    return v  # STRING, BOOL, TIMESTAMP (RFC 3339 text)


def _rows(result: dict) -> list[tuple]:
    fields = result.get("metadata", {}).get("rowType", {}).get("fields", [])
    return [tuple(_decode(v, f["type"]) for v, f in zip(row, fields)) for row in result.get("rows", [])]


def ts_to_float(ts: str) -> float:
    """An RFC 3339 timestamp (Spanner's, with up to nanoseconds) as seconds since the epoch."""
    m = re.match(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?Z$", ts)
    if not m:
        raise ValueError(f"bad timestamp {ts!r}")
    whole = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
    return whole + (int(m.group(2)) / 10 ** len(m.group(2)) if m.group(2) else 0.0)


def float_to_ts(t: float) -> str:
    whole = int(t // 1)
    micros = int(round((t - whole) * 1_000_000))
    if micros == 1_000_000:
        whole, micros = whole + 1, 0
    return datetime.fromtimestamp(whole, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + f".{micros:06d}Z"


class _Token:
    """Access tokens for real Spanner; none for an http:// endpoint (the emulator)."""

    def __init__(self, config: dict, endpoint: str):
        self.command = config.get("token_command")
        self.mode = "command" if self.command else ("gce" if endpoint.startswith("https://") else None)
        self.value, self.expires = None, 0.0
        self._lock = threading.Lock()

    def header(self, refresh: bool = False) -> dict:
        if self.mode is None:
            return {}
        with self._lock:
            if refresh or self.value is None or time.time() > self.expires - 60:
                self._fetch()
            return {"Authorization": f"Bearer {self.value}"}

    def _fetch(self) -> None:
        try:
            if self.mode == "command":
                out = subprocess.run(self.command, capture_output=True, text=True, timeout=60, check=True)
                self.value, self.expires = out.stdout.strip(), time.time() + 45 * 60  # gcloud tokens last an hour
            else:
                req = urllib.request.Request(METADATA_TOKEN_URL, headers={"Metadata-Flavor": "Google"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.load(r)
                self.value, self.expires = data["access_token"], time.time() + int(data["expires_in"])
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
            # the reason only: a command's output may hold a token
            raise SpannerError(f"no Spanner access token ({self.mode}): {type(e).__name__}") from None
        if not self.value:
            raise SpannerError(f"no Spanner access token ({self.mode}): empty")


class _Results:
    """What a transaction function uses: queries, DML, and mutations applied at commit."""

    def __init__(self, client: "SpannerClient", session: str, selector: dict):
        self.client, self.session, self.selector = client, session, selector
        self.id: str | None = None
        self.seqno = 0
        self.mutations: list[dict] = []
        self.wrote = False

    def _execute(self, sql: str, params: dict | None) -> dict:
        self.seqno += 1
        body = {"sql": sql, "seqno": str(self.seqno),
                "transaction": {"id": self.id} if self.id else self.selector}
        if params:
            body["params"] = {k: _value(v) for k, v in params.items()}
            body["paramTypes"] = {k: _ptype(v) for k, v in params.items()}
        r = self.client.request("POST", f"{self.session}:executeSql", body)
        if self.id is None:
            self.id = r.get("metadata", {}).get("transaction", {}).get("id")
        return r

    def query(self, sql: str, params: dict | None = None) -> list[tuple]:
        return _rows(self._execute(sql, params))

    def execute(self, sql: str, params: dict | None = None) -> int:
        """DML: the number of rows it changed."""
        self.wrote = True
        return int(self._execute(sql, params).get("stats", {}).get("rowCountExact", 0))

    def _mutate(self, op: str, table: str, columns, rows) -> None:
        if rows:
            types = [COLUMN_TYPES[table][c] for c in columns]
            self.wrote = True
            self.mutations.append({op: {"table": table, "columns": list(columns),
                                        "values": [[_cell(t, v) for t, v in zip(types, row)] for row in rows]}})

    def insert(self, table, columns, rows):
        self._mutate("insert", table, columns, rows)

    def upsert(self, table, columns, rows):
        self._mutate("insertOrUpdate", table, columns, rows)

    def delete(self, table, keys):
        if keys:
            self.wrote = True
            self.mutations.append({"delete": {"table": table,
                                              "keySet": {"keys": [[_value(v) for v in k] for k in keys]}}})


class SpannerClient:
    """One Spanner database over REST: pooled sessions and connections, retried transactions."""

    def __init__(self, config: dict):
        for k in ("project", "instance", "database"):
            if not config.get(k):
                raise ValueError(f"the Spanner metadata configuration needs {k!r}")
        self.config = dict(config)
        self.endpoint = config.get("endpoint", "https://spanner.googleapis.com").rstrip("/")
        u = urllib.parse.urlsplit(self.endpoint)
        if u.scheme not in ("http", "https") or not u.hostname:
            raise ValueError(f"bad Spanner endpoint {self.endpoint!r}")
        self._https, self._host, self._port = u.scheme == "https", u.hostname, u.port
        self.instance = f"projects/{config['project']}/instances/{config['instance']}"
        self.database = f"{self.instance}/databases/{config['database']}"
        self.deadline = float(config.get("transaction_deadline", 60.0))
        self._token = _Token(config, self.endpoint)
        self._lock = threading.Lock()
        self._conns: list[tuple[http.client.HTTPConnection, float]] = []
        self._sessions: list[tuple[str, float]] = []
        self.users = 0
        self.stats: Counter = Counter()
        self.ensure_schema(bool(config.get("create")))

    # -- HTTP --------------------------------------------------------------------------------------
    def _conn(self) -> http.client.HTTPConnection:
        with self._lock:
            while self._conns:
                c, used = self._conns.pop()
                if time.monotonic() - used < 20:  # servers drop idle keep-alive connections
                    return c
                c.close()
        if self._https:
            return http.client.HTTPSConnection(self._host, self._port, timeout=60,
                                               context=ssl.create_default_context())
        return http.client.HTTPConnection(self._host, self._port, timeout=60)

    def request(self, method: str, path: str, body: dict | None = None) -> dict:
        """One REST call; unavailable or overloaded calls are retried with backoff, and a refused
        token is fetched again once. Errors raise SpannerError (Aborted for ABORTED)."""
        payload = None if body is None else json.dumps(body).encode()
        refresh = False
        for attempt in range(1, 7):
            headers = {"Content-Type": "application/json", **self._token.header(refresh)}
            c = self._conn()
            try:
                c.request(method, f"/v1/{path}", payload, headers)
                resp = c.getresponse()
                data = resp.read()
            except (OSError, http.client.HTTPException) as e:
                c.close()
                if attempt < 3:
                    continue  # a dropped keep-alive connection: the request never ran
                raise SpannerError(f"cannot reach Spanner at {self.endpoint}: {e}") from None
            with self._lock:
                self._conns.append((c, time.monotonic()))
            self.stats["requests"] += 1
            if resp.status == 200:
                return json.loads(data or b"{}")
            try:
                err = json.loads(data)
                err = err.get("error", err)
                code, message = err.get("code"), err.get("message", "")
            except ValueError:
                code, message = None, data[:200].decode("utf-8", "replace")
            status = code if isinstance(code, int) and code < 100 else None
            if resp.status == 401 and not refresh and self._token.mode:
                refresh = True
                continue
            if status == ABORTED or resp.status == 409 and "abort" in message.lower():
                raise Aborted(message, ABORTED)
            if (status in (UNAVAILABLE, RESOURCE_EXHAUSTED) or resp.status in (429, 503)) and attempt < 6:
                self.stats["retries"] += 1
                time.sleep(random.uniform(0, min(2.0, 0.05 * 2 ** attempt)))
                continue
            raise SpannerError(f"Spanner {method} {path.rsplit('/', 1)[-1]}: HTTP {resp.status}: {message[:300]}",
                               status)
        raise SpannerError("Spanner kept refusing the request")

    # -- sessions ------------------------------------------------------------------------------------
    def _take_session(self) -> str:
        with self._lock:
            while self._sessions:
                s, used = self._sessions.pop()
                if time.monotonic() - used < 1800:  # Spanner deletes sessions idle for an hour
                    return s
        return self.request("POST", f"{self.database}/sessions", {})["name"]

    def _give_session(self, s: str) -> None:
        with self._lock:
            self._sessions.append((s, time.monotonic()))

    @contextmanager
    def session(self):
        s = self._take_session()
        ok = False
        try:
            yield s
            ok = True
        finally:
            if ok:
                self._give_session(s)
            else:  # it may be gone (NOT_FOUND) or mid-transaction: don't reuse it
                try:
                    self.request("DELETE", s)
                except SpannerError:
                    pass

    # -- reads -----------------------------------------------------------------------------------------
    def query(self, sql: str, params: dict | None = None) -> list[tuple]:
        """A strong read: it sees every transaction committed before it started."""
        for attempt in range(2):
            try:
                with self.session() as s:
                    return _Results(self, s, {"singleUse": {"readOnly": {"strong": True}}}).query(sql, params)
            except SpannerError as e:
                if not _session_gone(e) or attempt:
                    raise

    @contextmanager
    def snapshot(self, at: str | None = None):
        """Reads at one timestamp (``at``, RFC 3339, or now); ``.read_timestamp`` tells which."""
        with self.session() as s:
            opts = {"readTimestamp": at} if at else {"strong": True}
            tx = self.request("POST", f"{s}:beginTransaction",
                              {"options": {"readOnly": {**opts, "returnReadTimestamp": True}}})
            snap = _Results(self, s, {})
            snap.id, snap.read_timestamp = tx["id"], tx["readTimestamp"]
            yield snap

    # -- writes ----------------------------------------------------------------------------------------
    def run_in_transaction(self, fn):
        """Run ``fn(tx)`` in a read-write transaction and commit it; when Spanner aborts it, run it
        again from the start, with jittered backoff, until the deadline (FR-ST-03)."""
        start, attempt = time.monotonic(), 0
        while True:
            attempt += 1
            try:
                with self.session() as s:
                    tx = _Results(self, s, {"begin": {"readWrite": {}}})
                    try:
                        result = fn(tx)
                        if tx.id is None:
                            if tx.mutations:  # blind writes: one round trip
                                self.request("POST", f"{s}:commit", {"singleUseTransaction": {"readWrite": {}},
                                                                     "mutations": tx.mutations})
                        elif tx.wrote:
                            self.request("POST", f"{s}:commit", {"transactionId": tx.id, "mutations": tx.mutations})
                        else:
                            self.request("POST", f"{s}:rollback", {"transactionId": tx.id})
                    except Aborted:
                        raise
                    except BaseException:
                        if tx.id is not None:
                            try:
                                self.request("POST", f"{s}:rollback", {"transactionId": tx.id})
                            except SpannerError:
                                pass
                        raise
                self.stats["transactions"] += 1
                return result
            except SpannerError as e:
                if not isinstance(e, Aborted) and not _session_gone(e):
                    raise
                self.stats["aborts"] += 1
                if time.monotonic() - start > self.deadline:
                    raise SpannerError(f"a metadata transaction was aborted {attempt} times in "
                                       f"{self.deadline:.0f} s") from None
                time.sleep(random.uniform(0, min(0.2, 0.002 * 2 ** min(attempt, 7))))

    def write(self, mutations_fn) -> None:
        """Blind writes (insert-or-update, delete): ``mutations_fn(tx)`` only buffers mutations."""
        self.run_in_transaction(mutations_fn)

    # -- schema --------------------------------------------------------------------------------------
    def _wait(self, op: dict) -> None:
        deadline = time.monotonic() + 600
        while not op.get("done"):
            if time.monotonic() > deadline:
                raise SpannerError(f"Spanner operation {op.get('name')} did not finish")
            time.sleep(0.05)
            op = self.request("GET", op["name"])
        if op.get("error"):
            raise SpannerError(f"Spanner operation failed: {op['error'].get('message', op['error'])}")

    def ensure_schema(self, create: bool) -> None:
        """Create the database when it is missing and allowed; add any table or index it lacks."""
        try:
            have = self.request("GET", f"{self.database}/ddl").get("statements", [])
        except SpannerError as e:
            if e.status != NOT_FOUND or not create:
                raise SpannerError(f"cannot open the metadata database {self.database}: {e}") from None
            if not self._https:  # the emulator: make the instance too
                try:
                    self.request("GET", self.instance)
                except SpannerError as e2:
                    if e2.status != NOT_FOUND:
                        raise
                    project = self.instance.split("/instances/")[0]
                    self._wait(self.request("POST", f"{project}/instances", {
                        "instanceId": self.config["instance"],
                        "instance": {"config": f"{project}/instanceConfigs/emulator-config",
                                     "displayName": self.config["instance"], "nodeCount": 1}}))
            self._wait(self.request("POST", f"{self.instance}/databases", {
                "createStatement": f"CREATE DATABASE `{self.config['database']}`", "extraStatements": DDL}))
            return
        names = {m.group(1).lower() for st in have for m in [re.match(r"CREATE (?:TABLE|INDEX) (\w+)", st)] if m}
        missing = [st for st in DDL if re.match(r"CREATE (?:TABLE|INDEX) (\w+)", st).group(1).lower() not in names]
        if missing:
            self._wait(self.request("PATCH", f"{self.database}/ddl", {"statements": missing}))

    def close(self) -> None:
        """Delete the pooled sessions, then close the connections (deleting uses them)."""
        with self._lock:
            sessions, self._sessions = self._sessions, []
        for s, _ in sessions:
            try:
                self.request("DELETE", s)
            except SpannerError:
                pass
        with self._lock:
            conns, self._conns = self._conns, []
        for c, _ in conns:
            c.close()


def _session_gone(e: SpannerError) -> bool:
    return e.status == NOT_FOUND and "session" in str(e).lower()


_clients: dict[tuple, SpannerClient] = {}
_clients_lock = threading.Lock()


def client_for(config: dict) -> SpannerClient:
    """The process's client for one database, shared by its repositories' stores."""
    key = (config.get("endpoint", ""), config.get("project"), config.get("instance"), config.get("database"))
    with _clients_lock:
        c = _clients.get(key)
        if c is None:
            c = _clients[key] = SpannerClient(config)
        c.users += 1
        return c


def release_client(c: SpannerClient) -> None:
    with _clients_lock:
        c.users -= 1
        if c.users > 0:
            return
        for k, v in list(_clients.items()):
            if v is c:
                del _clients[k]
    c.close()


def _chunks(rows: list, n: int = ROWS_PER_COMMIT):
    for i in range(0, len(rows), n):
        yield rows[i:i + n]


class SpannerMetaStore(MetaStore):
    """One repository's metadata in the deployment's Spanner database (keys 06 §6.10). Reads are
    strong; units that read before they write run as transactions rerun on abort (FR-ST-03); blind
    writes of deterministic rows go in one round trip."""

    def __init__(self, client: SpannerClient, repo: str):
        self.client, self.repo = client, repo
        self._closed = False

    def close(self):
        if not self._closed:
            self._closed = True
            release_client(self.client)

    def _q(self, sql: str, **params) -> list[tuple]:
        return self.client.query(sql, {"repo": self.repo, **params})

    def _one(self, sql: str, **params):
        rows = self._q(sql, **params)
        return rows[0][0] if rows else None

    def _tx(self, fn):
        return self.client.run_in_transaction(fn)

    def _upsert(self, table: str, columns, rows) -> None:
        rows = [(self.repo, *r) for r in rows]
        for chunk in _chunks(rows):
            self.client.write(lambda tx, chunk=chunk: tx.upsert(table, ("repo", *columns), chunk))

    def _paged(self, sql: str, order: tuple, read=None, typed=(), **params):
        """Yield the rows of ``sql`` (whose WHERE clause ends at ``{after}`` and which selects the
        ``order`` columns first) in that order, a page at a time."""
        read = read or (lambda sql, params: self.client.query(sql, params))
        after = None
        while True:
            where, keys = _after(order, after, typed) if after is not None else ("", {})
            rows = read(sql.format(after=where) + f" ORDER BY {', '.join(map(q, order))} LIMIT {PAGE}",
                        {"repo": self.repo, **params, **keys})
            yield from rows
            if len(rows) < PAGE:
                return
            after = rows[-1][:len(order)]

    # -- changeset log -----------------------------------------------------------------------------
    def insert_changeset(self, cs_id, data):
        return self._tx(lambda tx: tx.execute(
            "INSERT OR IGNORE INTO changesets (repo, id, data, created) "
            "VALUES (@repo, @id, @data, PENDING_COMMIT_TIMESTAMP())",
            {"repo": self.repo, "id": cs_id, "data": bytes(data)}) == 1)

    def get_changeset_data(self, cs_id):
        return self._one("SELECT data FROM changesets WHERE repo = @repo AND id = @id", id=cs_id)

    def has_changeset(self, cs_id):
        return self._one("SELECT 1 FROM changesets WHERE repo = @repo AND id = @id", id=cs_id) is not None

    def resolve_prefix(self, prefix, limit=2):
        p = prefix.lower()
        return [r[0] for r in self._q("SELECT id FROM changesets WHERE repo = @repo AND id >= @lo AND id < @hi "
                                      "ORDER BY id LIMIT @n", lo=p, hi=p + "g", n=int(limit))]

    def count_changesets(self):
        return self._one("SELECT COUNT(*) FROM changesets WHERE repo = @repo")

    def tail(self, after=None, limit=1000, data=False):
        """The cursor is (commit timestamp, id): the order of the changesets_created index."""
        where, params = "", {}
        if after is not None:
            where = " AND (created > @ts OR (created = @ts AND id > @id))"
            params = {"ts": Typed(after[0], "TIMESTAMP"), "id": after[1]}
        rows = self._q(f"SELECT created, id{', data' if data else ''} FROM changesets@{{FORCE_INDEX=changesets_created}} "
                       f"WHERE repo = @repo{where} ORDER BY created, id LIMIT @n", n=int(limit), **params)
        return [((r[0], r[1]), *r[1:]) for r in rows]

    # -- refs ---------------------------------------------------------------------------------------
    def get_ref(self, name):
        rows = self._q("SELECT target, version FROM refs WHERE repo = @repo AND name = @name", name=name)
        return (rows[0][0], rows[0][1]) if rows else None

    def list_refs(self):
        return self._q("SELECT name, target, version FROM refs WHERE repo = @repo ORDER BY name")

    def cas_ref(self, name, expected, new, who="", landing=None):
        if expected is None and new is None:
            return self.get_ref(name) is None
        now = time.time()

        def move(tx):
            rows = tx.query("SELECT target, version FROM refs WHERE repo = @repo AND name = @name",
                            {"repo": self.repo, "name": name})
            if (rows[0][0] if rows else None) != expected:
                return False  # the compare failed: someone else moved it first
            if new is None:
                tx.delete("refs", [(self.repo, name)])
            else:
                tx.upsert("refs", ("repo", "name", "target", "version", "updated"),
                          [(self.repo, name, new, rows[0][1] + 1 if rows else 1, now)])
            tx.insert("ref_log", ("repo", "name", "moved", "old", "new", "who", "at"),
                      [(self.repo, name, COMMIT_TS, expected, new, who, now)])
            if landing is not None:
                self._record_landings(tx, *landing)
            return True
        return self._tx(move)

    def ref_log(self, name, limit=100):
        return self._q("SELECT old, `new`, who, `at` FROM ref_log WHERE repo = @repo AND name = @name "
                       "ORDER BY moved DESC LIMIT @n", name=name, n=int(limit))

    # -- derived data -------------------------------------------------------------------------------
    def derived_get(self, dtype, cs_id):
        return self._one("SELECT value FROM derived WHERE repo = @repo AND type = @t AND cs = @cs", t=dtype, cs=cs_id)

    def derived_put(self, dtype, cs_id, value):
        self._upsert("derived", ("type", "cs", "value"), [(dtype, cs_id, value)])  # deterministic: same bytes

    def derived_count(self, dtype):
        return self._one("SELECT COUNT(*) FROM derived WHERE repo = @repo AND type = @t", t=dtype)

    # -- copy-detection index -------------------------------------------------------------------------
    def blob_index_add(self, rows):
        self._upsert("blob_index", ("blob", "path"), list(dict.fromkeys(rows)))

    def blob_index_paths(self, blob, limit=50):
        out = []
        for (path,) in self._paged("SELECT path FROM blob_index WHERE repo = @repo AND blob = @b{after}", ("path",),
                                   b=blob):
            out.append(path)
            if len(out) >= limit:
                break
        return out

    # -- content index ------------------------------------------------------------------------------
    def content_status(self, blob):
        return self._one("SELECT status FROM content_blobs WHERE repo = @repo AND blob = @b", b=blob)

    def content_add(self, blob, status, grams):
        # the postings first, the status last: a blob is never marked indexed without its postings
        self._upsert("content_trigrams", ("trigram", "blob"), [(g, blob) for g in dict.fromkeys(grams)])
        self._upsert("content_blobs", ("blob", "status"), [(blob, status)])

    def content_count(self, gram):
        return self._one("SELECT COUNT(*) FROM content_trigrams WHERE repo = @repo AND trigram = @g", g=gram)

    def content_postings(self, gram):
        return {r[0] for r in self._paged("SELECT blob FROM content_trigrams WHERE repo = @repo AND trigram = @g"
                                          "{after}", ("blob",), g=gram)}

    def content_unindexed(self):
        return [r[0] for r in self._paged("SELECT blob FROM content_blobs@{{FORCE_INDEX=content_blobs_status}} "
                                          "WHERE repo = @repo AND status = 'l'{after}", ("blob",))]

    # -- object ACL index and grants -----------------------------------------------------------------
    def acl_add(self, rows):
        self._upsert("object_acl", ("oid", "prefix"), list(dict.fromkeys(rows)))

    def acl_get(self, ids):
        out: dict[str, set[str]] = {}
        ids = list(dict.fromkeys(ids))
        for i in range(0, len(ids), 1000):
            for oid, prefix in self._q("SELECT oid, prefix FROM object_acl WHERE repo = @repo AND oid IN UNNEST(@ids)",
                                       ids=ids[i:i + 1000]):
                out.setdefault(oid, set()).add(prefix)
        return out

    def acl_replace(self, rows):
        """Not one transaction (a large index exceeds a commit's limits): the new rows are written
        first, then the stale ones deleted, so a reader sees the old index, then both, then the new."""
        new = set(rows)
        oids = {oid for oid, _ in new}
        self._upsert("object_acl", ("oid", "prefix"), sorted(new))
        stale = [(self.repo, oid, p) for oid, p in self._paged(
            "SELECT oid, prefix FROM object_acl WHERE repo = @repo{after}", ("oid", "prefix"))
            if oid in oids and (oid, p) not in new]
        for chunk in _chunks(stale):
            self.client.write(lambda tx, chunk=chunk: tx.delete("object_acl", chunk))

    def grant_add(self, oid, user, now):
        def add(tx):
            tx.execute("DELETE FROM object_grants WHERE repo = @repo AND `at` < @cutoff",
                       {"repo": self.repo, "cutoff": float(now) - GRANT_SECONDS})
            tx.upsert("object_grants", ("repo", "oid", "user", "at"), [(self.repo, oid, user, now)])
        self._tx(add)

    def grant_has(self, oid, user, now):
        return self._one("SELECT 1 FROM object_grants WHERE repo = @repo AND oid = @o AND user = @u AND `at` >= @t",
                         o=oid, u=user, t=float(now) - GRANT_SECONDS) is not None

    # -- settings --------------------------------------------------------------------------------------
    def kv_get(self, key):
        return self._one("SELECT value FROM kv WHERE repo = @repo AND key = @k", k=key)

    def kv_set(self, key, value):
        self._upsert("kv", ("key", "value"), [(key, value)])

    # -- git map ---------------------------------------------------------------------------------------
    def git_map_put(self, git, cs):
        self._upsert("git_map", ("git", "cs"), [(git, cs)])

    def git_map_lookup(self, git=None, cs=None):
        if git is not None:
            rows = self._q("SELECT git, cs FROM git_map WHERE repo = @repo AND git = @g", g=git)
        else:
            rows = self._q("SELECT git, cs FROM git_map@{FORCE_INDEX=git_map_cs} WHERE repo = @repo AND cs = @c "
                           "ORDER BY git LIMIT 1", c=cs)
        return (rows[0][0], rows[0][1]) if rows else None

    # -- audit log ---------------------------------------------------------------------------------------
    def audit_append(self, make):
        def append(tx):
            last = tx.query("SELECT seq, `hash` FROM audit WHERE repo = @repo ORDER BY seq DESC LIMIT 1",
                            {"repo": self.repo})
            seq = last[0][0] + 1 if last else 1
            row = make(seq, last[0][1] if last else None)
            tx.insert("audit", ("repo",) + AUDIT_FIELDS, [(self.repo, seq, *row)])
            return seq, row[-1]
        return self._tx(append)

    def audit_entries(self, limit=100, action=None, before=None):
        where, params = "", {"n": int(limit)}
        if action:
            where += " AND action = @action"
            params["action"] = action
        if before:
            where += " AND seq < @before"
            params["before"] = int(before)
        hint = "@{FORCE_INDEX=audit_action}" if action else ""
        return self._q(f"SELECT {', '.join(map(q, AUDIT_FIELDS))} FROM audit{hint} WHERE repo = @repo{where} "
                       f"ORDER BY seq DESC LIMIT @n", **params)

    def audit_iter(self):
        return self._paged(f"SELECT {', '.join(map(q, AUDIT_FIELDS))} FROM audit WHERE repo = @repo{{after}}", ("seq",))

    # -- change requests ---------------------------------------------------------------------------------
    def _next(self, tx, name: str, n: int = 1) -> int:
        """Reserve ``n`` ids from a counter; returns the first."""
        rows = tx.query("SELECT value FROM counters WHERE repo = @repo AND name = @name",
                        {"repo": self.repo, "name": name})
        first = (rows[0][0] if rows else 0) + 1
        tx.upsert("counters", ("repo", "name", "value"), [(self.repo, name, first + n - 1)])
        return first

    def cr_create(self, title, description, author, target, head, state, now):
        def create(tx):
            cr_id = self._next(tx, "cr")
            tx.insert("crs", ("repo", "id", "title", "description", "author", "target", "head", "state", "created",
                              "updated"),
                      [(self.repo, cr_id, title, description, author, target, head, state, now, now)])
            tx.insert("cr_revisions", ("repo", "cr", "rev", "head", "created"), [(self.repo, cr_id, 1, head, now)])
            return cr_id
        return self._tx(create)

    def cr_get(self, cr_id):
        rows = self._q(f"SELECT {', '.join(CR_COLUMNS)} FROM crs WHERE repo = @repo AND id = @id", id=int(cr_id))
        return dict(zip(CR_COLUMNS, rows[0])) if rows else None

    def _cr_update(self, tx, cr_id, cols: dict, states=None, head=None) -> bool:
        check_cr_columns(cols)
        types = COLUMN_TYPES["crs"]
        params = {f"v{i}": Typed(None, types[c]) if v is None else float(v) if types[c] == "FLOAT64" else v
                  for i, (c, v) in enumerate(cols.items())}
        sets = ", ".join(f"{c} = @v{i}" for i, c in enumerate(cols))
        guard = ""
        if states is not None:
            guard += " AND state IN UNNEST(@states)"
            params["states"] = list(states)
        if head is not None:
            guard += " AND head = @head"
            params["head"] = head
        return tx.execute(f"UPDATE crs SET {sets} WHERE repo = @repo AND id = @id{guard}",
                          {"repo": self.repo, "id": int(cr_id), **params}) == 1

    def cr_update(self, cr_id, expect_states=None, expect_head=None, **cols):
        return self._tx(lambda tx: self._cr_update(tx, cr_id, cols, expect_states, expect_head))

    def cr_add_revision(self, cr_id, head, state, now, expect_states=None):
        def add(tx):
            if not self._cr_update(tx, cr_id, {"head": head, "state": state, "conflict": None, "updated": now},
                                   expect_states):
                return None
            rev = tx.query("SELECT MAX(rev) FROM cr_revisions WHERE repo = @repo AND cr = @cr",
                           {"repo": self.repo, "cr": int(cr_id)})[0][0] + 1
            tx.insert("cr_revisions", ("repo", "cr", "rev", "head", "created"), [(self.repo, cr_id, rev, head, now)])
            return rev
        return self._tx(add)

    def cr_latest_rev(self, cr_id):
        return self._one("SELECT MAX(rev) FROM cr_revisions WHERE repo = @repo AND cr = @cr", cr=int(cr_id))

    def cr_revisions(self, cr_id):
        return self._q("SELECT rev, head, created FROM cr_revisions WHERE repo = @repo AND cr = @cr ORDER BY rev",
                       cr=int(cr_id))

    def cr_approve(self, cr_id, rev, user, now):
        self._tx(lambda tx: tx.execute(
            "INSERT OR IGNORE INTO cr_approvals (repo, cr, rev, user, created) VALUES (@repo, @cr, @rev, @u, @t)",
            {"repo": self.repo, "cr": int(cr_id), "rev": int(rev), "u": user, "t": float(now)}))

    def cr_approvals(self, cr_id):
        return self._q("SELECT rev, user FROM cr_approvals WHERE repo = @repo AND cr = @cr ORDER BY created, rev, user",
                       cr=int(cr_id))

    def cr_approvers(self, cr_id, rev):
        return {r[0] for r in self._q("SELECT user FROM cr_approvals WHERE repo = @repo AND cr = @cr AND rev = @rev",
                                      cr=int(cr_id), rev=int(rev))}

    def cr_comment(self, cr_id, rev, user, path, line, body, now):
        def add(tx):
            cid = self._next(tx, "comment")
            tx.insert("cr_comments", ("repo", "cr", "id", "rev", "user", "path", "line", "body", "created"),
                      [(self.repo, cr_id, cid, rev, user, path, line, body, now)])
            return cid
        return self._tx(add)

    def cr_comments(self, cr_id):
        return self._q("SELECT id, rev, user, path, line, body, created FROM cr_comments WHERE repo = @repo "
                       "AND cr = @cr ORDER BY id", cr=int(cr_id))

    def cr_list(self, state=None, author=None, limit=50):
        where, params = "", {"n": int(limit)}
        if state:
            where += " AND state = @state"
            params["state"] = state
        if author:
            where += " AND author = @author"
            params["author"] = author
        hint = "@{FORCE_INDEX=crs_state}" if state else ""
        return [r[0] for r in self._q(f"SELECT id FROM crs{hint} WHERE repo = @repo{where} ORDER BY id DESC LIMIT @n",
                                      **params)]

    # -- landings and the post-merge queue ------------------------------------------------------------
    def record_landings(self, rows, jobs, cr_updates):
        self._tx(lambda tx: self._record_landings(tx, rows, jobs, cr_updates))

    def _record_landings(self, tx, rows, jobs, cr_updates) -> None:
        fields = [("cs", "STRING"), ("source", "STRING"), ("cr", "INT64"), ("ref", "STRING"),
                  ("landed_at", "FLOAT64"), ("head", "STRING")]
        if rows:
            tx.execute("INSERT OR IGNORE INTO landings (repo, cs, source, cr, ref, landed_at, head) "
                       "SELECT @repo, x.cs, x.source, x.cr, x.ref, x.landed_at, x.head FROM UNNEST(@rows) AS x",
                       {"repo": self.repo, "rows": Typed([(cs, src, cr, ref, float(at), head)
                                                          for cs, src, cr, ref, at, head in rows], "", fields)})
        if jobs:
            first = self._next(tx, "postmerge", len(jobs))
            tx.insert("postmerge", ("repo", "id", "cs", "cr", "ref", "status", "created"),
                      [(self.repo, first + i, *job) for i, job in enumerate(jobs)])
        for cr_id, cols in cr_updates:
            self._cr_update(tx, cr_id, cols)

    def landing_find(self, cs):
        cols = ", ".join(LANDING_FIELDS)
        rows = self._q(f"SELECT {cols} FROM landings WHERE repo = @repo AND cs = @cs", cs=cs) or \
            self._q(f"SELECT {cols} FROM landings@{{FORCE_INDEX=landings_source}} WHERE repo = @repo AND source = @cs "
                    f"ORDER BY cs LIMIT 1", cs=cs)
        return dict(zip(LANDING_FIELDS, rows[0])) if rows else None

    def landing_members(self, head):
        return {r[0] for r in self._q("SELECT cs FROM landings@{FORCE_INDEX=landings_head} WHERE repo = @repo "
                                      "AND head = @h", h=head)}

    def postmerge_requeue(self, started_before):
        expired = "repo = @repo AND status = 'running' AND started < @t"
        if not self._q(f"SELECT id FROM postmerge@{{FORCE_INDEX=postmerge_status}} WHERE {expired} LIMIT 1",
                       t=float(started_before)):
            return 0  # the usual case, without a read-write transaction
        return self._tx(lambda tx: tx.execute(
            f"UPDATE postmerge SET status = 'queued', started = NULL, worker = NULL WHERE {expired}",
            {"repo": self.repo, "t": float(started_before)}))

    def postmerge_claim(self, claim, now):
        oldest = "SELECT id, cs, cr, ref FROM postmerge@{FORCE_INDEX=postmerge_status} " \
                 "WHERE repo = @repo AND status = 'queued' ORDER BY id LIMIT 1"
        if not self._q(oldest):
            return None  # an empty queue, without a read-write transaction

        def claim_one(tx):  # concurrent claims conflict on the job's row: Spanner aborts all but one
            rows = tx.query(oldest, {"repo": self.repo})
            if not rows:
                return None
            tx.execute("UPDATE postmerge SET status = 'running', started = @now, worker = @claim "
                       "WHERE repo = @repo AND id = @id AND status = 'queued'",
                       {"repo": self.repo, "id": rows[0][0], "now": float(now), "claim": claim})
            return dict(zip(("id", "cs", "cr", "ref"), rows[0]))
        return self._tx(claim_one)

    def postmerge_report(self, job_id, status, now, log, claim=None):
        sql = "UPDATE postmerge SET status = @s, finished = @now, log = @log " \
              "WHERE repo = @repo AND id = @id AND status = 'running'"
        params = {"repo": self.repo, "id": int(job_id), "s": status, "now": float(now), "log": log}
        if claim is not None:
            sql += " AND worker = @claim"
            params["claim"] = claim
        return self._tx(lambda tx: tx.execute(sql, params)) == 1

    def postmerge_mark_reverted(self, job_id, note):
        return self._tx(lambda tx: tx.execute(
            "UPDATE postmerge SET status = 'reverted', log = CONCAT(COALESCE(log, ''), @note) "
            "WHERE repo = @repo AND id = @id AND status = 'failed'",
            {"repo": self.repo, "id": int(job_id), "note": note})) == 1

    def postmerge_counts(self):
        return dict(self._q("SELECT status, COUNT(*) FROM postmerge@{FORCE_INDEX=postmerge_status} "
                            "WHERE repo = @repo AND status IN ('queued', 'running') GROUP BY status"))

    def postmerge_job_for(self, cs):
        rows = self._q("SELECT id, cs, cr, ref, status FROM postmerge@{FORCE_INDEX=postmerge_cs} "
                       "WHERE repo = @repo AND cs = @cs ORDER BY id DESC LIMIT 1", cs=cs)
        return dict(zip(("id", "cs", "cr", "ref", "status"), rows[0])) if rows else None

    def postmerge_list(self, ref, limit=50):
        rows = self._q("SELECT id, cs, cr, status, created, finished FROM postmerge@{FORCE_INDEX=postmerge_ref} "
                       "WHERE repo = @repo AND ref = @ref ORDER BY id DESC LIMIT @n", ref=ref, n=int(limit))
        return [dict(zip(("id", "cs", "cr", "status", "created", "finished"), r)) for r in rows]

    # -- backup ---------------------------------------------------------------------------------------
    def is_empty(self):
        return all(not self._q(f"SELECT 1 FROM {t} WHERE repo = @repo LIMIT 1") for t in (*TABLES, "counters"))

    def export(self, path, at=None):
        """Every table at one timestamp, into the SQLite schema: changesets in commit order (their
        ``seq``), the ref log in the order of the moves."""
        if os.path.exists(path):
            raise FileExistsError(path)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        db = sqlite3.connect(path)
        try:
            db.executescript(SCHEMA)
            with self.client.snapshot(at) as snap:
                for table, (keys, cols) in TABLES.items():
                    order = {"changesets": ("created", "id"), "ref_log": ("moved", "name")}.get(table, keys)
                    select = list(dict.fromkeys(order + keys + cols))
                    out = [c for c in keys + cols if c != "moved"]
                    hint = "@{{FORCE_INDEX=changesets_created}}" if table == "changesets" else ""
                    for row in self._paged(f"SELECT {', '.join(map(q, select))} FROM {table}{hint} "
                                           f"WHERE repo = @repo{{after}}", order, snap.query,
                                           typed=("created", "moved") if table in ("changesets", "ref_log") else ()):
                        d = dict(zip(select, row))
                        if table == "changesets":
                            d["created"] = ts_to_float(d["created"])
                        db.execute(f"INSERT INTO {table} ({', '.join(out)}) VALUES ({', '.join('?' * len(out))})",
                                   [d[c] for c in out])
            db.commit()
            return snap.read_timestamp
        finally:
            db.close()

    def load(self, path):
        if not self.is_empty():
            raise ValueError(f"the Spanner database already holds metadata for {self.repo}")
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            have = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            for table, (keys, cols) in TABLES.items():
                if table not in have:
                    continue
                if table == "changesets":
                    rows = [(i, d, float_to_ts(c)) for i, d, c in
                            db.execute("SELECT id, data, created FROM changesets ORDER BY seq")]
                    self._upsert("changesets", ("id", "data", "created"), _increasing(rows, 2))
                elif table == "ref_log":
                    rows = [(n, float_to_ts(at), old, new, who, at) for n, old, new, who, at in
                            db.execute("SELECT name, old, new, who, at FROM ref_log ORDER BY id")]
                    self._upsert("ref_log", ("name", "moved", "old", "new", "who", "at"), _increasing(rows, 1, by=0))
                else:
                    names = [c for c in keys + cols]
                    self._upsert(table, names, db.execute(f"SELECT {', '.join(names)} FROM {table}").fetchall())
            counters = [(name, n) for name, table, col in (("cr", "crs", "id"), ("comment", "cr_comments", "id"),
                                                           ("postmerge", "postmerge", "id"))
                        if table in have for (n,) in db.execute(f"SELECT MAX({col}) FROM {table}") if n]
            self._upsert("counters", ("name", "value"), counters)
        finally:
            db.close()


def _increasing(rows: list[tuple], col: int, by: int | None = None) -> list[tuple]:
    """Make the timestamps in ``col`` strictly increase (per value of column ``by``), so that rows
    keyed by them stay distinct and keep their order."""
    last: dict = {}
    out = []
    for r in rows:
        k = r[by] if by is not None else None
        t = r[col]
        if k in last and t <= last[k]:
            t = float_to_ts(ts_to_float(last[k]) + 0.000001)
        last[k] = t
        out.append(r[:col] + (t,) + r[col + 1:])
    return out

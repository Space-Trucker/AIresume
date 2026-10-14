"""Shared test setup, including the hermetic ``Cluster``: servers, caches and daemons in one
process over real sockets (10 §10.2).

With ``SCION_TEST_SPANNER`` set to the REST endpoint of Google's Spanner emulator (for example
``http://127.0.0.1:9020``), every cluster and every repository the tests make keep their metadata on
the emulator, each in a database of its own (10 §10.1, "Metadata backends")."""
from __future__ import annotations

import atexit
import itertools
import json
import os
import shutil
import sys
import tempfile
import urllib.request
import warnings

warnings.simplefilter("ignore", ResourceWarning)  # per-thread SQLite connections close at exit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scion.deployment import Deployment  # noqa: E402
from scion.meta import open_metastore  # noqa: E402
from scion.repo import Repository  # noqa: E402
from scion.rpc import ClientTls, RpcClient, RpcServer, TlsConfig  # noqa: E402
from scion.server import ScionService  # noqa: E402
from scion.tiers import DaemonService, make_cache_service  # noqa: E402

REPO = "monorepo"
SPANNER = os.environ.get("SCION_TEST_SPANNER", "").rstrip("/")
_databases: list[str] = []
_numbers = itertools.count(1)
_repo_configs: dict[str, dict] = {}


def spanner_config() -> dict | None:
    """A new, empty database on the emulator; None when the tests run on SQLite."""
    if not SPANNER:
        return None
    name = f"t{os.getpid()}-{next(_numbers)}"
    _databases.append(name)
    return {"backend": "spanner", "endpoint": SPANNER, "project": "scion-test", "instance": "test",
            "database": name, "create": True}


def metadata_config() -> dict:
    """The metadata backend the tests run on (the ``metadata`` section of deployment.json)."""
    return spanner_config() or {"backend": "sqlite"}


def repository(path: str, **kw) -> Repository:
    """A repository outside a deployment, on the backend the tests run on; the same path reopens
    the same metadata."""
    if not SPANNER:
        return Repository(path, **kw)
    config = _repo_configs.setdefault(os.path.abspath(path), spanner_config())
    return Repository(path, meta=open_metastore(config, path, kw.get("name", "main")), **kw)


def tamper(meta, sql: str) -> None:
    """Change stored metadata behind the store's back, as an attacker with database access would:
    ``sql`` is an UPDATE ending in a WHERE clause, which on Spanner also selects the repository."""
    if SPANNER:
        meta.client.run_in_transaction(lambda tx: tx.execute(sql + " AND repo = @repo", {"repo": meta.repo}))
    else:
        meta.execute(sql)


@atexit.register
def _drop_databases() -> None:
    for name in _databases:
        req = urllib.request.Request(f"{SPANNER}/v1/projects/scion-test/instances/test/databases/{name}",
                                     method="DELETE")
        try:
            urllib.request.urlopen(req, timeout=10).close()
        except OSError:
            pass


def short_tmpdir(prefix: str = "scn-") -> str:
    """Unix socket paths are limited to about 100 bytes, so sockets live in a short /tmp path."""
    return tempfile.mkdtemp(prefix=prefix, dir="/tmp" if os.path.isdir("/tmp") else None)


class Cluster:
    """servers → caches → daemons over real sockets, sharing one deployment root.

    ``identity`` is written to deployment.json; ``repos`` maps repository names to policies.
    With ``pki`` (from ``tools.certs.make_dev_pki``) every TCP hop uses TLS and the tiers
    authenticate with client certificates (ADR-14)."""

    def __init__(self, root: str, servers: int = 1, caches: int = 1, daemons: int = 1,
                 identity: dict | None = None, repos: dict | None = None, allow_direct_objects: bool = False,
                 cache_bytes: int = 64 << 20, daemon_bytes: int = 64 << 20, snapshot_dir: str | None = None,
                 pki: dict | None = None, tokens: dict | None = None, epoch_seconds: float = 10.0):
        self.root, self.pki, self.tokens = root, pki, tokens or {}
        self.dep_root = os.path.join(root, "deployment")
        os.makedirs(self.dep_root, exist_ok=True)
        if SPANNER:
            identity = {**(identity or {}), "metadata": spanner_config()}
        if identity is not None:
            with open(os.path.join(self.dep_root, "deployment.json"), "w") as f:
                json.dump(identity, f)
        setup = Deployment(self.dep_root)
        for name, policy in (repos if repos is not None else {REPO: None}).items():
            setup.create_repo(name, policy)
        setup.close()
        self.sockdir = short_tmpdir()
        scheme = "https" if pki else "http"
        server_tls = TlsConfig(*pki["server"], client_ca=pki["ca"]) if pki else None
        cache_tls = TlsConfig(*pki["cache"], client_ca=pki["ca"]) if pki else None
        self.deployments, self.services, self.servers = [], [], []
        for _ in range(servers):
            dep = Deployment(self.dep_root)
            svc = ScionService(dep, allow_direct_objects=allow_direct_objects)
            self.deployments.append(dep)
            self.services.append(svc)
            self.servers.append(RpcServer(svc, f"{scheme}://127.0.0.1:0", tls=server_tls).start())
        self.server_urls = [s.url for s in self.servers]
        self.cache_services, self.caches = [], []
        for _ in range(caches):
            svc = make_cache_service(self.server_urls, cache_bytes, identity=self._identity(),
                                     token=self.tokens.get("scion-cache"),
                                     tls=ClientTls(pki["ca"], *pki["cache"]) if pki else None,
                                     epoch_seconds=epoch_seconds)
            self.cache_services.append(svc)
            self.caches.append(RpcServer(svc, f"{scheme}://127.0.0.1:0", tls=cache_tls).start())
        self.cache_urls = [c.url for c in self.caches]
        self.daemon_services, self.daemons = [], []
        for i in range(daemons if caches else 0):
            svc = DaemonService(os.path.join(root, f"daemon{i}"), self.cache_urls, daemon_bytes,
                                snapshot_dir=snapshot_dir, refresh_seconds=3600,
                                token=self.tokens.get("scion-daemon"),
                                tls=ClientTls(pki["ca"], *pki["daemon"]) if pki else None,
                                epoch_seconds=epoch_seconds)
            self.daemon_services.append(svc)
            self.daemons.append(RpcServer(svc, f"unix:{self.sockdir}/d{i}.sock").start())
        self.daemon_urls = [d.url for d in self.daemons]

    def _identity(self):
        return self.deployments[0].identity if self.deployments else None

    @property
    def deployment(self) -> Deployment:
        return self.deployments[0]

    def repo(self, name: str = REPO):
        return self.deployment.repo(name)

    def client(self, user: str | None = "alice", url: str | None = None, tier: str = "client",
               token: str | None = None, cert: tuple | None = None, **kw) -> RpcClient:
        url = url or self.server_urls[0]
        tls = ClientTls(self.pki["ca"], *(cert or ())) if self.pki and url.startswith("https") else None
        return RpcClient(url, user=user, token=token if token is not None else self.tokens.get(user), tier=tier,
                         tls=tls, **kw)

    def close(self) -> None:
        for s in self.daemons + self.caches + self.servers:
            try:
                s.stop()
            except OSError:
                pass
        for d in self.daemon_services:
            d.stop()
        for c in self.cache_services:
            c.close()
        for dep in self.deployments:
            dep.close()
        shutil.rmtree(self.sockdir, ignore_errors=True)

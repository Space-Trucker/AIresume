"""Hermetic in-process clusters for tests: scion-server(s) → scion-cache → scion-daemon."""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import warnings

warnings.simplefilter("ignore", ResourceWarning)  # per-thread SQLite connections close at exit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scion.client import WorkingCopy  # noqa: E402
from scion.iam import Policy  # noqa: E402
from scion.repo import Repository  # noqa: E402
from scion.rpc import RpcServer  # noqa: E402
from scion.server import ScionService  # noqa: E402
from scion.tiers import DaemonService, make_cache_service  # noqa: E402

MB = 1024 ** 2


def short_tmpdir(prefix: str) -> str:
    """Unix socket paths are limited to ~107 bytes, so keep socket directories short."""
    d = tempfile.mkdtemp(prefix=prefix)
    if len(d) > 70:
        d = tempfile.mkdtemp(prefix=prefix, dir="/tmp")
    return d


class Cluster:
    def __init__(self, policy: dict | None = None, servers: int = 1, direct_objects: bool = False,
                 snapshot_dir: str | None = None, cache_bytes: int = 64 * MB):
        self.tmp = tempfile.mkdtemp(prefix="scion-test-")
        self.sockdir = short_tmpdir("scn")
        self.policy_data = policy or {}
        self.repo_path = os.path.join(self.tmp, "repo")
        self.repos = [Repository(self.repo_path, Policy(self.policy_data)) for _ in range(servers)]
        self.repo = self.repos[0]
        self.services = [ScionService(r, allow_direct_objects=direct_objects) for r in self.repos]
        self.servers = [RpcServer(s, "127.0.0.1:0").start() for s in self.services]
        self.server = self.servers[0]
        self.service = self.services[0]
        self.cache_svc = make_cache_service([s.url for s in self.servers], cache_bytes, policy=Policy(self.policy_data))
        self.cache = RpcServer(self.cache_svc, "127.0.0.1:0").start()
        self.daemons: list[tuple[DaemonService, RpcServer, str]] = []
        self.add_daemon(snapshot_dir=snapshot_dir)

    def add_daemon(self, snapshot_dir: str | None = None, name: str | None = None):
        idx = len(self.daemons)
        sock = os.path.join(self.sockdir, f"d{idx}.sock")
        svc = DaemonService(os.path.join(self.tmp, name or f"daemon{idx}"), [self.cache.url], 64 * MB,
                            snapshot_dir=snapshot_dir, refresh_seconds=3600, policy=Policy(self.policy_data))
        srv = RpcServer(svc, f"unix:{sock}").start()
        self.daemons.append((svc, srv, sock))
        return svc, f"unix:{sock}"

    @property
    def daemon_svc(self) -> DaemonService:
        return self.daemons[0][0]

    @property
    def objects_url(self) -> str:
        return f"unix:{self.daemons[0][2]}"

    def clone(self, name: str, user: str = "alice", daemon: int = 0, **kw) -> WorkingCopy:
        return WorkingCopy.clone(os.path.join(self.tmp, name), self.server.url, f"unix:{self.daemons[daemon][2]}",
                                 user=user, cache_bytes=kw.pop("cache_bytes", 32 * MB), **kw)

    def seed(self, files: dict[str, bytes], message: str = "seed", author: str = "alice") -> str:
        parent = self.repo.get_ref("main")
        cs = self.repo.create_changeset([parent] if parent else [],
                                        [{"path": p, "content": c} for p, c in files.items()], author, message)
        assert self.repo.update_ref("main", parent, cs)
        return cs

    def close(self) -> None:
        for svc, srv, _ in self.daemons:
            svc.stop()
            srv.stop()
        self.cache.stop()
        for s in self.servers:
            try:
                s.stop()
            except Exception:
                pass
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.sockdir, ignore_errors=True)


def read(wc: WorkingCopy, path: str) -> bytes:
    with open(os.path.join(wc.root, path), "rb") as f:
        return f.read()


def write(wc: WorkingCopy, path: str, data: bytes) -> None:
    full = os.path.join(wc.root, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(data)

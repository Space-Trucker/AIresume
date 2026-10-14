"""A deployment hosts many named repositories (ADR-13, FR-IAM-02).

Layout of a deployment root::

    deployment.json          principals, tokens, services, groups, admins, limits (iam.Identity),
                             and where the metadata lives (``metadata``, FR-ST-02)
    repos/<name>/objects/    the repository's objects (blob storage)
    repos/<name>/meta.db     its metadata store, when the metadata is in SQLite
    repos/<name>/policy.json the repository's access policy (iam.Policy)

With ``"metadata": {"backend": "spanner", ...}`` the metadata of every repository lives in one
Cloud Spanner database instead (ADR-24). The backend is read when the deployment opens; changing it
needs a restart. Servers are stateless over this root: any number of them may serve it (NFR-07).
"""
from __future__ import annotations

import hashlib
import json
import os
import threading

from .audit import AuditLog
from .iam import Identity, Policy
from .meta import open_metastore
from .objects import REPO_NAME, validate_repo_name
from .repo import NotFound, Repository


def _stamp(path: str):
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return None
    return (st.st_mtime_ns, st.st_size, st.st_ino)


def _file_hash(path: str) -> str | None:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


class Deployment:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        os.makedirs(os.path.join(self.root, "repos"), exist_ok=True)
        self._lock = threading.RLock()
        self._repos: dict[str, Repository] = {}
        self._policy_stamps: dict[str, tuple] = {}
        self._identity_stamp = _stamp(self.identity_path)
        self.identity = Identity.load(self.identity_path)
        self.metadata: dict = dict(self.identity.raw.get("metadata") or {"backend": "sqlite"})
        self.log = lambda level, message, **fields: None  # the serving component's log (ADR-18)

    @property
    def identity_path(self) -> str:
        return os.path.join(self.root, "deployment.json")

    def repo_dir(self, name: str) -> str:
        return os.path.join(self.root, "repos", validate_repo_name(name))

    def policy_path(self, name: str) -> str:
        return os.path.join(self.repo_dir(name), "policy.json")

    def names(self) -> list[str]:
        base = os.path.join(self.root, "repos")
        return sorted(n for n in os.listdir(base)
                      if REPO_NAME.match(n) and os.path.exists(os.path.join(base, n, "policy.json")))

    def policy_for(self, name: str) -> Policy:
        return Policy.load(self.policy_path(name), self.identity)

    def repo(self, name: str | None) -> Repository:
        """The named repository (or the deployment's default one); NotFound if it doesn't exist.
        A changed policy file takes effect here, on the next request (FR-IAM-06)."""
        name = name or self.identity.default_repo
        if not name:
            raise ValueError("the request must name a repository (repo)")
        with self._lock:
            r = self._repos.get(name)
            if r is not None:
                if _stamp(self.policy_path(name)) != self._policy_stamps.get(name):
                    self._load_policy(r)
                return r
            d = self.repo_dir(name)
            if not os.path.exists(os.path.join(d, "policy.json")):
                raise NotFound(f"unknown repository {name}")
            r = Repository(d, self.policy_for(name), name=name, meta=open_metastore(self.metadata, d, name))
            r.audit = AuditLog(r.meta)
            self._repos[name] = r
            self._load_policy(r)
            return r

    def _load_policy(self, r: Repository) -> None:
        """(Re)load a repository's policy and audit it when its content changed (ADR-15). A policy
        file that doesn't parse leaves the last good policy in force, audited and logged as an error,
        until the file changes again; only a repository's first load fails outright."""
        path = self.policy_path(r.name)
        self._policy_stamps[r.name] = _stamp(path)
        try:
            policy = self.policy_for(r.name)
        except (OSError, ValueError) as e:
            if getattr(r.policy, "identity", None) is None:  # never loaded: nothing to fall back on
                raise
            r.audit.append("policy.invalid", None, "policy.json", {"error": str(e)[:500]})
            self.log("error", f"the policy of {r.name} is invalid; the last good one stays in force: {e}",
                     repo=r.name)
            return
        r.policy = policy
        hashes = {"policy": _file_hash(path), "identity": _file_hash(self.identity_path)}
        last = r.audit.last("policy.load")
        if last is None or last["detail"] != hashes:
            r.audit.append("policy.load", None, "policy.json", hashes)
            self.log("info", f"loaded the policy of {r.name}", repo=r.name, sha256=(hashes["policy"] or "")[:16])

    def maybe_reload(self) -> None:
        """Pick up a changed deployment.json: groups, tokens, admins and services (FR-IAM-06)."""
        if _stamp(self.identity_path) != self._identity_stamp:
            self.reload()

    def create_repo(self, name: str, policy: dict | None = None) -> Repository:
        d = self.repo_dir(name)
        path = os.path.join(d, "policy.json")
        if os.path.exists(path):
            raise ValueError(f"repository {name} already exists")
        os.makedirs(d, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(policy if policy is not None else {"read": ["*"], "write": ["*"]}, f, indent=2)
        os.replace(tmp, path)
        return self.repo(name)

    def reload(self) -> None:
        """Re-read deployment.json and every open repository's policy (UC-22 step 2)."""
        with self._lock:
            self._identity_stamp = _stamp(self.identity_path)
            try:
                self.identity = Identity.load(self.identity_path)
            except (OSError, ValueError) as e:  # keep serving with the last good identity document
                self.log("error", f"deployment.json is invalid; the last good one stays in force: {e}")
                return
            self.log("info", "loaded deployment.json")
            for r in self._repos.values():
                self._load_policy(r)

    def close(self) -> None:
        with self._lock:
            for r in self._repos.values():
                r.close()
            self._repos.clear()

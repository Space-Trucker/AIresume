"""A deployment hosts many named repositories (ADR-13, FR-IAM-02).

Layout of a deployment root::

    deployment.json          principals, tokens, services, groups, admins, limits (iam.Identity)
    repos/<name>/objects/    blob storage stand-in
    repos/<name>/meta.db     metadata store stand-in
    repos/<name>/policy.json the repository's access policy (iam.Policy)

Servers are stateless over this root: any number of them may serve it (NFR-07).
"""
from __future__ import annotations

import hashlib
import json
import os
import threading

from .audit import AuditLog
from .iam import Identity, Policy
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
            r = Repository(d, self.policy_for(name), name=name)
            r.audit = AuditLog(r.meta)
            self._repos[name] = r
            self._load_policy(r)
            return r

    def _load_policy(self, r: Repository) -> None:
        """(Re)load a repository's policy and audit it when its content changed (ADR-15)."""
        path = self.policy_path(r.name)
        self._policy_stamps[r.name] = _stamp(path)
        r.policy = self.policy_for(r.name)
        hashes = {"policy": _file_hash(path), "identity": _file_hash(self.identity_path)}
        last = r.audit.last("policy.load")
        if last is None or last["detail"] != hashes:
            r.audit.append("policy.load", None, "policy.json", hashes)

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
            self.identity = Identity.load(self.identity_path)
            for r in self._repos.values():
                self._load_policy(r)

    def close(self) -> None:
        with self._lock:
            for r in self._repos.values():
                r.close()
            self._repos.clear()

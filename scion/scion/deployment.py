"""A deployment hosts many named repositories (ADR-13, FR-IAM-02).

Layout of a deployment root::

    deployment.json          principals, tokens, services, groups, admins, limits (iam.Identity)
    repos/<name>/objects/    blob storage stand-in
    repos/<name>/meta.db     metadata store stand-in
    repos/<name>/policy.json the repository's access policy (iam.Policy)

Servers are stateless over this root: any number of them may serve it (NFR-07).
"""
from __future__ import annotations

import json
import os
import threading

from .iam import Identity, Policy
from .objects import REPO_NAME, validate_repo_name
from .repo import NotFound, Repository


class Deployment:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        os.makedirs(os.path.join(self.root, "repos"), exist_ok=True)
        self.identity = Identity.load(self.identity_path)
        self._repos: dict[str, Repository] = {}
        self._lock = threading.Lock()

    @property
    def identity_path(self) -> str:
        return os.path.join(self.root, "deployment.json")

    def repo_dir(self, name: str) -> str:
        return os.path.join(self.root, "repos", validate_repo_name(name))

    def names(self) -> list[str]:
        base = os.path.join(self.root, "repos")
        return sorted(n for n in os.listdir(base)
                      if REPO_NAME.match(n) and os.path.exists(os.path.join(base, n, "policy.json")))

    def policy_for(self, name: str) -> Policy:
        return Policy.load(os.path.join(self.repo_dir(name), "policy.json"), self.identity)

    def repo(self, name: str | None) -> Repository:
        """The named repository (or the deployment's default one); NotFound if it doesn't exist."""
        name = name or self.identity.default_repo
        if not name:
            raise ValueError("the request must name a repository (repo)")
        with self._lock:
            r = self._repos.get(name)
            if r is not None:
                return r
            d = self.repo_dir(name)
            if not os.path.exists(os.path.join(d, "policy.json")):
                raise NotFound(f"unknown repository {name}")
            r = self._repos[name] = Repository(d, self.policy_for(name), name=name)
            return r

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
        identity = Identity.load(self.identity_path)
        with self._lock:
            self.identity = identity
            for name, r in self._repos.items():
                r.policy = self.policy_for(name)

    def close(self) -> None:
        with self._lock:
            for r in self._repos.values():
                r.close()
            self._repos.clear()

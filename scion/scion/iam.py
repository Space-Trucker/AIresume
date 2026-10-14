"""Identity and access management (FR-IAM-*, 08 §8.3).

A deployment (ADR-13) has two kinds of policy document:

* ``deployment.json`` says who the principals are and how they authenticate: bearer tokens
  (FR-IAM-07), service principals that may act on behalf of users (FR-IAM-08), groups,
  deployment-wide administrators, rate limits (FR-OP-06) and default limits::

      {"tokens": {"alice": "sha256:<hex>", "ci": "<plain token>"},
       "service_principals": ["scion-cache", "scion-daemon", "antique", "postmerge"],
       "groups": {"eng": ["alice", "bob"]},
       "admins": ["root"],
       "rate_limits": {...},
       "limits": {"max_file_bytes": 104857600},
       "default_repo": "monorepo"}

* each repository's ``policy.json`` says who may read and write that repository (FR-IAM-01/02)::

      {"read": ["eng"], "write": ["eng"], "admins": ["alice"], "limits": {"max_file_bytes": 1048576}}

``"*"`` matches any principal (and the anonymous caller in development mode, when no tokens are
configured). Without tokens, identities sent in headers are trusted, which is for development only
(08 §8.3, S1).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os

ANY = "*"
DEFAULT_SERVICE_PRINCIPALS = ("scion-cache", "scion-daemon", "antique", "postmerge")
TIER_PRINCIPALS = {"cache": "scion-cache", "daemon": "scion-daemon"}
DEFAULT_LIMITS = {"max_file_bytes": 100 * 1024 * 1024}


class PermissionDenied(Exception):
    pass


def hash_token(token: str) -> str:
    """The stored form of a token: ``deployment.json`` may hold this instead of the token itself."""
    return "sha256:" + hashlib.sha256(token.encode()).hexdigest()


def _load_json(path: str | None) -> dict:
    if not path or not os.path.exists(path):
        return {}
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


class Identity:
    """Deployment-wide principals: authentication, services, groups and administrators."""

    def __init__(self, data: dict | None = None):
        data = data or {}
        self.raw = data
        self.tokens: dict[str, str] = dict(data.get("tokens", {}))
        self.service_principals: set[str] = set(data.get("service_principals", DEFAULT_SERVICE_PRINCIPALS))
        self.groups: dict[str, set[str]] = {k: set(v) for k, v in data.get("groups", {}).items()}
        self.admins: set[str] = set(data.get("admins", []))
        self.rate_limits: dict = data.get("rate_limits", {})
        self.limits: dict = {**DEFAULT_LIMITS, **data.get("limits", {})}
        self.default_repo: str | None = data.get("default_repo")

    @staticmethod
    def load(path: str | None) -> "Identity":
        return Identity(_load_json(path))

    @property
    def tokens_required(self) -> bool:
        return bool(self.tokens)

    def check_token(self, principal: str | None, token: str | None) -> bool:
        """True when the token is the principal's. Stored tokens may be plain or ``sha256:<hex>``."""
        if principal is None or token is None:
            return False
        stored = self.tokens.get(principal)
        if stored is None:
            return False
        offered = hash_token(token) if stored.startswith("sha256:") else token
        return hmac.compare_digest(stored.encode(), offered.encode())

    def is_service(self, principal: str | None) -> bool:
        return principal is not None and principal in self.service_principals

    def is_admin(self, principal: str | None) -> bool:
        return principal is not None and principal in self.admins

    def matches(self, user: str | None, principals) -> bool:
        """Does ``user`` match a list of principals and group names?"""
        if ANY in principals:
            return True
        if user is None:
            return False
        return user in principals or any(user in self.groups.get(p, ()) for p in principals)


class Policy:
    """One repository's access rules, evaluated against the deployment's identities.

    The repository-level rules decide who may use the repository at all (FR-IAM-01). When reads
    are not open to everyone the repository is private, and every object it serves is flagged
    restricted so shared tiers never cache it (ADR-13).
    """

    def __init__(self, data: dict | None = None, identity: Identity | None = None):
        data = data or {}
        self.raw = data
        self.identity = identity or Identity()
        self.read: list[str] = list(data.get("read", [ANY]))
        self.write: list[str] = list(data.get("write", [ANY]))
        self.admins: set[str] = set(data.get("admins", []))
        self.limits: dict = {**self.identity.limits, **data.get("limits", {})}

    @staticmethod
    def load(path: str | None, identity: Identity | None = None) -> "Policy":
        return Policy(_load_json(path), identity)

    # -- principals --------------------------------------------------------------------------
    def is_admin(self, user: str | None) -> bool:
        return self.identity.is_admin(user) or (user is not None and user in self.admins)

    def is_service(self, user: str | None) -> bool:
        return self.identity.is_service(user)

    # -- repository level (FR-IAM-01/02) -------------------------------------------------------
    @property
    def public(self) -> bool:
        """Readable by everyone: only then may shared tiers cache this repository's objects."""
        return ANY in self.read

    def can_read_repo(self, user: str | None) -> bool:
        return self.is_admin(user) or self.identity.matches(user, self.read)

    def can_write_repo(self, user: str | None) -> bool:
        return self.is_admin(user) or self.identity.matches(user, self.write)

    # -- the interface Repository uses ------------------------------------------------------------
    def can_read(self, user: str | None, path: str = "") -> bool:
        return self.can_read_repo(user)

    def can_write(self, user: str | None, path: str = "") -> bool:
        return self.can_write_repo(user)

    def can_update_ref(self, user: str | None, ref: str) -> bool:
        return self.can_write_repo(user)

    def restricted_prefix(self, path: str) -> str | None:
        return None

    def restricted_prefixes(self) -> list[str]:
        return []

    @property
    def max_file_bytes(self) -> int | None:
        v = self.limits.get("max_file_bytes")
        return int(v) if v else None

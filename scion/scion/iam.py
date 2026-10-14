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

* each repository's ``policy.json`` says who may read and write that repository (FR-IAM-01/02) and
  its directories (FR-IAM-03), who may move protected refs (FR-REF-03/05) and how changes are
  reviewed (``review``, see antique.py)::

      {"read": ["eng"], "write": ["eng"], "admins": ["alice"], "limits": {"max_file_bytes": 1048576},
       "paths": [{"prefix": "secrets", "read": ["sec-team"], "write": ["sec-team"]},
                 {"prefix": "secrets/public", "read": ["*"]}],
       "protected_refs": {"main": ["antique"], "release/*": ["release-managers"]}}

  The most specific directory rule decides; a rule that leaves out ``read`` or ``write`` inherits it.
  Objects stored under a directory that not everyone may read are restricted: the object index
  records where each object appears, and shared tiers never cache restricted objects (FR-IAM-05).

``"*"`` matches any principal (and the anonymous caller in development mode, when no tokens are
configured). Without tokens, identities sent in headers are trusted, which is for development only
(08 §8.3, S1).
"""
from __future__ import annotations

import fnmatch
import hashlib
import hmac
import json
import os
from dataclasses import dataclass

ANY = "*"
DEFAULT_SERVICE_PRINCIPALS = ("scion-cache", "scion-daemon", "antique", "postmerge", "superfan")
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


def _under(path: str, prefix: str) -> bool:
    return prefix == "" or path == prefix or path.startswith(prefix + "/")


@dataclass
class PathRule:
    prefix: str
    read: list | None = None
    write: list | None = None


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
        rules = [PathRule("/".join(p for p in str(r["prefix"]).split("/") if p), r.get("read"), r.get("write"))
                 for r in data.get("paths", [])]
        self.rules: list[PathRule] = sorted(rules, key=lambda r: len(r.prefix))  # general to specific
        self.protected_refs: dict[str, list] = dict(data.get("protected_refs", {}))
        self.review: dict = data.get("review", {})

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

    # -- directories (FR-IAM-03/04) ------------------------------------------------------------------
    def _effective(self, path: str, attr: str):
        """The principals of the most specific rule covering ``path`` that sets ``attr``; None if no
        rule does (the repository-level rule applies)."""
        found = None
        for rule in self.rules:
            if _under(path, rule.prefix) and getattr(rule, attr) is not None:
                found = getattr(rule, attr)
        return found

    def can_read(self, user: str | None, path: str = "") -> bool:
        if self.is_admin(user):
            return True
        if not self.identity.matches(user, self.read):
            return False
        perm = self._effective(path, "read")
        return perm is None or self.identity.matches(user, perm)

    def can_write(self, user: str | None, path: str = "") -> bool:
        if self.is_admin(user):
            return True
        if not self.identity.matches(user, self.write):
            return False
        perm = self._effective(path, "write")
        return perm is None or self.identity.matches(user, perm)

    def readable_beneath(self, user: str | None, path: str) -> bool:
        """Is some directory strictly beneath ``path`` readable (a public folder inside a private one)?"""
        return any(r.read is not None and r.prefix != path and _under(r.prefix, path) and self.can_read(user, r.prefix)
                   for r in self.rules)

    def restricted_prefix(self, path: str) -> str | None:
        """The directory whose read rule restricts ``path``, or None if everyone may read it."""
        found = None
        for rule in self.rules:
            if rule.read is not None and _under(path, rule.prefix):
                found = None if ANY in rule.read else rule.prefix
        return found

    def restricted_prefixes(self) -> list[str]:
        return [r.prefix for r in self.rules if r.read is not None and ANY not in r.read]

    def acl_entry(self, path: str) -> str:
        """The object index's entry for an object at ``path`` (FR-IAM-04/11): "" where everyone may
        read it, else the directory that restricts it, "/" for a rule on the repository's root (whose
        prefix is also "", which must not read as public)."""
        prefix = self.restricted_prefix(path)
        return "" if prefix is None else prefix or "/"

    # -- refs (FR-REF-03/05, BR-04) -----------------------------------------------------------------------
    def can_update_ref(self, user: str | None, ref: str) -> bool:
        if self.is_admin(user):
            return True
        for pattern, principals in self.protected_refs.items():
            if fnmatch.fnmatchcase(ref, pattern):
                return self.identity.matches(user, principals)
        return self.can_write_repo(user)

    def is_protected(self, ref: str) -> bool:
        return any(fnmatch.fnmatchcase(ref, p) for p in self.protected_refs)

    @property
    def max_file_bytes(self) -> int | None:
        v = self.limits.get("max_file_bytes")
        return int(v) if v else None

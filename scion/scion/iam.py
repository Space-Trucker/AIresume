"""Source-control IAM: repository access, per-directory permissions, protected refs.

Policy document (JSON):

    {
      "admins": ["alice"],
      "groups": {"sec-team": ["bob", "carol"]},
      "repo": {"read": ["*"], "write": ["*"]},
      "paths": [
        {"prefix": "secrets", "read": ["sec-team"], "write": ["alice"]},
        {"prefix": "infra/prod", "write": ["sre"]}
      ],
      "protected_refs": {"main": ["antique", "alice"], "release/*": ["release-bot"]},
      "tokens": {"alice": "s3cret"},
      "service_principals": ["antique", "scion-cache", "scion-daemon"],
      "review": {...},                      # see antique.py
      "rate_limits": {...}                  # see ratelimit.py
    }

``"*"`` means any principal.  The most specific (longest) path rule wins.  A rule that omits
``read`` or ``write`` inherits that permission from the enclosing rule (or the repo).

Directory read restrictions are enforced end to end.  Objects written beneath a read-restricted
directory are recorded in the ``object_acl`` index.  The object protocol checks that index and
caches never store restricted objects, so a restricted file cannot be read by id through any tier.
"""
from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass

ANY = "*"


class PermissionDenied(Exception):
    pass


@dataclass
class PathRule:
    prefix: str
    read: list[str] | None = None
    write: list[str] | None = None


class Policy:
    def __init__(self, data: dict | None = None):
        data = data or {}
        self.raw = data
        self.admins: set[str] = set(data.get("admins", []))
        self.groups: dict[str, set[str]] = {k: set(v) for k, v in data.get("groups", {}).items()}
        repo = data.get("repo", {})
        self.repo_read: list[str] = repo.get("read", [ANY])
        self.repo_write: list[str] = repo.get("write", [ANY])
        self.rules: list[PathRule] = sorted(
            (
                PathRule(r["prefix"].strip("/"), r.get("read"), r.get("write"))
                for r in data.get("paths", [])
            ),
            key=lambda r: len(r.prefix),
        )
        self.protected_refs: dict[str, list[str]] = data.get("protected_refs", {})
        self.tokens: dict[str, str] = data.get("tokens", {})
        self.service_principals: set[str] = set(
            data.get("service_principals", ["antique", "scion-cache", "scion-daemon", "postmerge"])
        )
        self.review: dict = data.get("review", {})
        self.rate_limits: dict = data.get("rate_limits", {})

    @staticmethod
    def load(path: str | None) -> "Policy":
        if not path:
            return Policy()
        with open(path) as f:
            return Policy(json.load(f))

    # -- principal resolution -----------------------------------------------------------------
    def _matches(self, user: str | None, principals: list[str]) -> bool:
        if ANY in principals:
            return True
        if user is None:
            return False
        if user in principals:
            return True
        return any(user in self.groups.get(p, ()) for p in principals)

    def is_admin(self, user: str | None) -> bool:
        return user is not None and user in self.admins

    def is_service(self, user: str | None) -> bool:
        return user is not None and user in self.service_principals

    def authenticate(self, user: str | None, token: str | None) -> bool:
        if not self.tokens:
            return True  # development mode: identities are trusted
        if user is None:
            return False
        return self.tokens.get(user) == token

    # -- path rules ----------------------------------------------------------------------------
    @staticmethod
    def _under(path: str, prefix: str) -> bool:
        return prefix == "" or path == prefix or path.startswith(prefix + "/")

    def _effective(self, path: str, attr: str) -> list[str]:
        perm = self.repo_read if attr == "read" else self.repo_write
        for rule in self.rules:  # sorted shortest -> longest, so later rules refine earlier ones
            if self._under(path, rule.prefix):
                v = getattr(rule, attr)
                if v is not None:
                    perm = v
        return perm

    def can_read(self, user: str | None, path: str = "") -> bool:
        if self.is_admin(user) or self.is_service(user):
            return True
        return self._matches(user, self.repo_read) and self._matches(user, self._effective(path, "read"))

    def can_write(self, user: str | None, path: str = "") -> bool:
        if self.is_admin(user):
            return True
        return self._matches(user, self.repo_write) and self._matches(user, self._effective(path, "write"))

    def restricted_prefix(self, path: str) -> str | None:
        """Return the prefix of the most specific read-restricting rule covering ``path``."""
        found = None
        for rule in self.rules:
            if rule.read is not None and self._under(path, rule.prefix):
                found = None if ANY in rule.read else rule.prefix
        return found

    def restricted_prefixes(self) -> list[str]:
        return [r.prefix for r in self.rules if r.read is not None and ANY not in r.read]

    def can_read_prefix(self, user: str | None, prefix: str) -> bool:
        return prefix == "" or self.can_read(user, prefix)

    # -- refs ----------------------------------------------------------------------------------
    def can_update_ref(self, user: str | None, ref: str) -> bool:
        if self.is_admin(user):
            return True
        for pattern, principals in self.protected_refs.items():
            if fnmatch.fnmatchcase(ref, pattern):
                return self._matches(user, principals)
        return self.can_write(user, "")

    def require(self, ok: bool, what: str) -> None:
        if not ok:
            raise PermissionDenied(what)

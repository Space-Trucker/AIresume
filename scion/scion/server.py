"""scion-server: the authoritative source-control API (API.md).

Every query the ``scn`` client makes is one of these public RPCs (FR-QRY-10), so CI jobs and
agents can ask questions and write changesets without a checkout (FR-WR-01). Every RPC names its
repository (ADR-13); the repository-level rules decide who may use it at all (FR-IAM-01/02).
"""
from __future__ import annotations

import base64
import binascii

from .deployment import Deployment
from .iam import PermissionDenied
from .repo import Repository
from .rpc import MAX_IDS_PER_REQUEST, Service, ids_cost, pack_objects, unpack_objects
from .search import search_paths

MAX_LIMIT = 10_000


def _int(p: dict, key: str, default: int, lo: int = 0, hi: int = MAX_LIMIT) -> int:
    v = p.get(key, default)
    if isinstance(v, bool) or not isinstance(v, (int, str)):
        raise ValueError(f"{key} must be an integer")
    return max(lo, min(hi, int(v)))


def _str(p: dict, key: str, default: str | None = None) -> str:
    v = p.get(key, default)
    if not isinstance(v, str):
        raise ValueError(f"{key} must be a string")
    return v


def _ids(p: dict) -> list[str]:
    ids = p.get("ids")
    if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
        raise ValueError("ids must be a list of strings")
    if len(ids) > MAX_IDS_PER_REQUEST:
        raise ValueError(f"at most {MAX_IDS_PER_REQUEST} ids per request")
    return ids


class ScionService(Service):
    tier = "server"

    def __init__(self, deployment: Deployment, allow_direct_objects: bool = False, verbose: bool = False):
        self.deployment = deployment
        super().__init__(verbose=verbose)
        self.object_callers = ("cache", "client") if allow_direct_objects else ("cache",)
        r = self.register
        # -- identity and discovery -------------------------------------------------------------
        r("whoami", self._whoami)
        r("list_repos", self._list_repos)
        r("server_info", self._server_info)
        r("tier_info", lambda c, p: {"tier": self.tier, "object_callers": list(self.object_callers)})
        # -- metadata reads (FR-QRY-*) -----------------------------------------------------------
        r("resolve", lambda c, p: self._repo(c, p).resolve(_str(p, "rev")))
        r("get_changeset", lambda c, p: self._changeset(c, self._repo(c, p), _str(p, "rev")))
        r("get_changesets", self._get_changesets)
        r("log", self._log)
        r("root_tree", lambda c, p: self._with_cs(c, p, lambda repo, cs: repo.root_tree(cs)))
        r("list_dir", lambda c, p: self._with_cs(c, p, lambda repo, cs: repo.list_dir(cs, _str(p, "path", ""), c.user)))
        r("read_file", self._read_file)
        r("diff", self._diff)
        r("merge_base", self._merge_base)
        r("is_ancestor", lambda c, p: self._repo(c, p).is_ancestor(_str(p, "a"), _str(p, "b")))
        r("fp_ancestor", lambda c, p: self._with_cs(c, p, lambda repo, cs: repo.fp_ancestor(cs, _int(p, "n", 1, 0, 1 << 40))))
        r("file_history", self._file_history, klass="heavy")
        r("blame", lambda c, p: self._repo(c, p).blame(_str(p, "rev"), _str(p, "path"), c.user), klass="heavy")
        r("search_paths", lambda c, p: search_paths(self._repo(c, p), _str(p, "rev"), _str(p, "query"),
                                                    _int(p, "limit", 100, 1), c.user), klass="heavy")
        r("list_refs", lambda c, p: [{"name": n, "target": t, "version": v}
                                     for n, t, v in self._repo(c, p).meta.list_refs()])
        r("get_ref", lambda c, p: self._repo(c, p).get_ref(_str(p, "name")))
        r("ref_log", lambda c, p: [{"old": o, "new": n, "who": w, "at": a} for o, n, w, a in
                                   self._repo(c, p).meta.ref_log(_str(p, "name"), _int(p, "limit", 50, 1))])
        # -- object protocol (FR-FP-*) and uploads (FR-WR-06/07) ---------------------------------
        r("get_objects", self._get_objects, klass="objects", binary_out=True, tiers=self.object_callers,
          cost=ids_cost)
        r("has_objects", lambda c, p: self._repo(c, p).missing_objects(_ids(p), c.user), klass="objects",
          cost=ids_cost)
        r("put_objects", self._put_objects, klass="write", binary_in=True)
        # -- writes (FR-WR-*) ----------------------------------------------------------------------
        r("create_changeset", self._create_changeset, klass="write")
        r("merge", self._merge, klass="write")
        r("rebase", lambda c, p: self._repo(c, p, write=True).rebase(_str(p, "head"), _str(p, "onto"),
                                                                     p.get("base"), user=c.user), klass="write")
        r("revert", self._revert, klass="write")
        r("update_ref", self._update_ref, klass="write")
        r("derive", self._derive, klass="heavy")

    @property
    def identity(self):
        return self.deployment.identity

    def reload(self) -> None:
        """Re-read the identity and policy documents (UC-22)."""
        self.deployment.reload()
        self.limiter = self.make_limiter()

    # -- helpers ---------------------------------------------------------------------------------
    def _repo(self, c, p, write: bool = False) -> Repository:
        repo = self.deployment.repo(p.get("repo"))
        if not repo.policy.can_read_repo(c.user):
            raise PermissionDenied(f"{c.user or 'anonymous'} may not read repository {repo.name}")
        if write and not repo.policy.can_write_repo(c.user):
            raise PermissionDenied(f"{c.user or 'anonymous'} may not write to repository {repo.name}")
        return repo

    def _with_cs(self, c, p, fn):
        repo = self._repo(c, p)
        return fn(repo, repo.resolve(_str(p, "rev")))

    @staticmethod
    def _changeset(c, repo: Repository, rev: str) -> dict:
        return repo.changeset_api(repo.resolve(rev), c.user)

    def _whoami(self, c, p):
        out = {"principal": c.principal, "user": c.user, "tier": c.tier, "via": c.via,
               "admin": self.identity.is_admin(c.user)}
        if p.get("repo"):
            out["repo_admin"] = self.deployment.repo(p["repo"]).policy.is_admin(c.user)
        return out

    def _list_repos(self, c, p):
        out = []
        for name in self.deployment.names():
            pol = self.deployment.policy_for(name)
            if pol.can_read_repo(c.user):
                out.append({"name": name, "public": pol.public, "writable": pol.can_write_repo(c.user)})
        return out

    def _server_info(self, c, p):
        if p.get("repo"):
            return {**self._repo(c, p).info(), "tier": self.tier}
        return {"tier": self.tier, "repos": [r["name"] for r in self._list_repos(c, p)]}

    def _get_changesets(self, c, p):
        repo = self._repo(c, p)
        return [self._changeset(c, repo, x) for x in _ids(p)]

    def _log(self, c, p):
        repo = self._repo(c, p)
        ids = repo.log(_str(p, "rev", "main"), _int(p, "limit", 50, 1), bool(p.get("first_parent", True)),
                       p.get("path"), _int(p, "skip", 0), user=c.user)
        if p.get("ids_only"):
            return ids
        out = []
        for i in ids:
            cs = repo.get_changeset(i)
            out.append({"id": i, "parents": list(cs.parents), "author": cs.author, "timestamp": cs.timestamp,
                        "summary": cs.summary(), "files": len(cs.changes)})
        return out

    def _read_file(self, c, p):
        repo = self._repo(c, p)
        kind, blob, data = repo.read_file(repo.resolve(_str(p, "rev")), _str(p, "path"), user=c.user)
        return {"kind": kind, "blob": blob, "content_b64": base64.b64encode(data).decode()}

    def _diff(self, c, p):
        repo = self._repo(c, p)
        b = repo.resolve(_str(p, "b"))
        a = p.get("a")
        if p.get("merge_base"):
            a = repo.merge_base(a or "main", b)
        elif a:
            a = repo.resolve(a)
        else:
            a = repo.get_changeset(b).first_parent
        paths = p.get("paths")
        if paths is not None and not (isinstance(paths, list) and all(isinstance(x, str) for x in paths)):
            raise ValueError("paths must be a list of strings")
        out = {"a": a, "b": b, "files": repo.diff(a, b, paths, user=c.user)}
        if p.get("text"):
            out["text"] = repo.diff_text(a, b, paths, user=c.user, context=_int(p, "context", 3, 0, 1000))
        return out

    def _merge_base(self, c, p):
        bases = self._repo(c, p).merge_bases(_str(p, "a"), _str(p, "b"))
        return {"base": bases[0] if bases else None, "all": bases}

    def _file_history(self, c, p):
        return self._repo(c, p).file_history(_str(p, "rev"), _str(p, "path"), _int(p, "limit", 100, 1),
                                             bool(p.get("follow_copies", True)), user=c.user)

    def _get_objects(self, c, p):
        repo = self.deployment.repo(p.get("repo"))  # unreadable repositories come back DENIED per object
        return pack_objects(repo.fetch_objects(_ids(p), c.user))

    def _put_objects(self, c, p):
        repo = self._repo(c, p, write=True)
        return {"stored": repo.put_objects(unpack_objects(p["_body"]), c.user)}

    def _author(self, c, p) -> str:
        """The author is the caller; only admins and services may name someone else (threat S3)."""
        author = p.get("author") or c.user or "anonymous"
        if author != c.user and not (self.identity.is_admin(c.user) or self.identity.is_service(c.user)):
            raise PermissionDenied("only admins and services may set a different author")
        return author

    def _create_changeset(self, c, p):
        repo = self._repo(c, p, write=True)
        files = []
        for f in p.get("files") or []:
            if not isinstance(f, dict):
                raise ValueError("each file must be an object")
            f = dict(f)
            if "content_b64" in f:
                try:
                    f["content"] = base64.b64decode(f.pop("content_b64"), validate=True)
                except (binascii.Error, TypeError):
                    raise ValueError(f"content_b64 of {f.get('path')!r} is not base64") from None
            files.append(f)
        parents = p.get("parents") or []
        if not isinstance(parents, list):
            raise ValueError("parents must be a list")
        ts = p.get("timestamp")
        cs_id = repo.create_changeset(parents, files, self._author(c, p), _str(p, "message", ""),
                                      None if ts is None else int(ts), p.get("extra"), user=c.user)
        moved = None
        ref = p.get("update_ref")
        if ref:
            moved = repo.update_ref(_str(ref, "name"), ref.get("old"), cs_id, user=c.user)
        return {"id": cs_id, "ref_updated": moved}

    def _merge(self, c, p):
        repo = self._repo(c, p, write=True)
        return repo.merge(_str(p, "ours"), _str(p, "theirs"), self._author(c, p), p.get("message"),
                          bool(p.get("ff", False)), user=c.user)

    def _revert(self, c, p):
        repo = self._repo(c, p, write=True)
        return repo.revert(_str(p, "cs"), _str(p, "onto"), self._author(c, p), p.get("message"), user=c.user)

    def _update_ref(self, c, p):
        repo = self._repo(c, p)
        return repo.update_ref(_str(p, "name"), p.get("old"), p.get("new"), user=c.user)

    def _derive(self, c, p):
        repo = self._repo(c, p)
        if not repo.policy.is_admin(c.user):
            raise PermissionDenied("derive is for administrators")
        cs = repo.resolve(_str(p, "rev", "main"))
        return {"type": _str(p, "type"), "computed": repo.derived.backfill(p["type"], cs)}

    def stats(self) -> dict:
        s = super().stats()
        s["repos"] = {name: dict(r.stats) for name, r in list(self.deployment._repos.items())}
        return s

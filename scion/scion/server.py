"""scion-server: the authoritative source-control API (API.md).

Every query the ``scn`` client makes is one of these public RPCs (FR-QRY-10), so CI jobs and
agents can ask questions and write changesets without a checkout (FR-WR-01). Every RPC names its
repository (ADR-13); the repository-level rules decide who may use it at all (FR-IAM-01/02), and
directory rules filter what each caller sees (FR-IAM-03/04). The server also hosts Antique, the
code review and landing service, and its review pages.
"""
from __future__ import annotations

import base64
import binascii
import json
import re
import threading
from collections import Counter

from .antique import Antique
from .deployment import Deployment
from .iam import PermissionDenied
from .notify import Notifier
from .objects import normalize_path
from .repo import NotFound, Repository
from .rpc import MAX_IDS_PER_REQUEST, Service, ids_cost, pack_objects, unpack_objects
from .search import grep, search_paths
from .ui import ReviewUI

RELEASE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")

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


def _rev(p: dict) -> int | None:
    """The CR revision an action is for (the one its caller saw); None: the latest."""
    return None if p.get("rev") is None else _int(p, "rev", 1, 1, 1 << 31)


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
        deployment.log = self.log
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
        r("list_dir", self._list_dir)
        r("read_file", self._read_file)
        r("diff", self._diff)
        r("merge_base", self._merge_base)
        r("is_ancestor", lambda c, p: self._repo(c, p).is_ancestor(_str(p, "a"), _str(p, "b")))
        r("fp_ancestor", lambda c, p: self._with_cs(c, p, lambda repo, cs: repo.fp_ancestor(cs, _int(p, "n", 1, 0, 1 << 40))))
        r("file_history", self._file_history, klass="heavy")
        r("blame", lambda c, p: self._repo(c, p).blame(_str(p, "rev"), _str(p, "path"), c.user), klass="heavy")
        r("search_paths", lambda c, p: search_paths(self._repo(c, p), _str(p, "rev"), _str(p, "query"),
                                                    _int(p, "limit", 100, 1), c.user), klass="heavy")
        r("grep", lambda c, p: grep(self._repo(c, p), _str(p, "rev"), _str(p, "pattern"), _str(p, "path", ""),
                                    _int(p, "limit", 200, 1), bool(p.get("regex", True)), bool(p.get("ignore_case")),
                                    c.user), klass="heavy")
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
        r("acl_epochs", self._acl_epochs, tiers=self.object_callers)
        r("git_lookup", self._git_lookup)
        r("put_objects", self._put_objects, klass="write", binary_in=True)
        # -- writes (FR-WR-*) ----------------------------------------------------------------------
        r("create_changeset", self._create_changeset, klass="write")
        r("merge", self._merge, klass="write")
        r("rebase", lambda c, p: self._repo(c, p, write=True).rebase(_str(p, "head"), _str(p, "onto"),
                                                                     p.get("base"), user=c.user), klass="write")
        r("revert", self._revert, klass="write")
        r("update_ref", self._update_ref, klass="write")
        r("derive", self._derive, klass="heavy")
        # -- refs, audit and administration (FR-REF-05, FR-IAM-09/10) ------------------------------
        r("create_release", self._create_release, klass="write")
        r("audit_log", self._audit_log)
        r("audit_verify", lambda c, p: self._admin_repo(c, p).audit.verify(), klass="heavy")
        r("reindex_acl", self._reindex_acl, klass="heavy")
        # -- Antique (FR-RV-*, FR-LD-*) ----------------------------------------------------------------
        r("antique.create", self._cr_create, klass="write")
        r("antique.update", lambda c, p: self._cr(c, p, lambda a: a.update(self._need_user(c), _int(p, "id", 0, 1, 1 << 62),
                                                                           _str(p, "head"))), klass="write")
        r("antique.get", lambda c, p: self._cr(c, p, lambda a: a.get(_int(p, "id", 0, 1, 1 << 62))))
        r("antique.list", self._cr_list)
        r("antique.approve", lambda c, p: self._cr(c, p, lambda a: a.approve(self._need_user(c), _int(p, "id", 0, 1, 1 << 62),
                                                                             _rev(p))), klass="write")
        r("antique.comment", self._cr_comment, klass="write")
        r("antique.requirements", lambda c, p: self._cr(c, p, lambda a: {"requirements": a.requirements(
            _int(p, "id", 0, 1, 1 << 62))})["requirements"], klass="heavy")
        r("antique.land", lambda c, p: self._cr(c, p, lambda a: a.land(self._need_user(c), _int(p, "id", 0, 1, 1 << 62),
                                                                       force=bool(p.get("force", False)), rev=_rev(p))),
          klass="write")
        r("antique.abandon", lambda c, p: self._cr(c, p, lambda a: a.abandon(self._need_user(c),
                                                                             _int(p, "id", 0, 1, 1 << 62))), klass="write")
        r("antique.land_changeset", lambda c, p: self._antique(c, p).land_changeset(
            self._need_user(c), _str(p, "cs"), _str(p, "ref", "main")), klass="write")
        r("antique.find_landing", lambda c, p: self._antique(c, p).find_landing(_str(p, "cs")))
        r("antique.landing_stack", lambda c, p: self._antique(c, p).landing_stack(_str(p, "cs")))
        r("antique.postmerge_claim", lambda c, p: self._postmerge(c, p).postmerge_claim(self._need_user(c)),
          klass="write")
        r("antique.postmerge_report", lambda c, p: self._postmerge(c, p).postmerge_report(
            _int(p, "id", 0, 1, 1 << 62), bool(p.get("passed")), _str(p, "log", ""),
            p.get("claim") if isinstance(p.get("claim"), str) else None), klass="write")
        r("antique.postmerge_status", lambda c, p: self._antique(c, p).postmerge_status(
            _str(p, "ref", "main"), _int(p, "limit", 50, 1)))
        r("antique.postmerge_reverted", lambda c, p: self._postmerge(c, p).postmerge_reverted(
            _int(p, "id", 0, 1, 1 << 62), [x for x in p.get("reverts", []) if isinstance(x, str)]), klass="write")
        r("antique.deploy_gate", lambda c, p: self._antique(c, p).deploy_gate(_str(p, "ref", "main")))
        r("antique.job_for", lambda c, p: self._antique(c, p).job_for(_str(p, "cs")))
        self._antiques: dict[str, Antique] = {}
        self._antiques_lock = threading.Lock()
        self.notifier = Notifier(self._webhooks)
        self.ui = ReviewUI(self)

    @property
    def identity(self):
        return self.deployment.identity

    # -- requests: live policies and audited denials --------------------------------------------------
    def dispatch(self, name, body, query, caller):
        self.deployment.maybe_reload()  # group, token and admin changes apply to the next request
        try:
            return super().dispatch(name, body, query, caller)
        except PermissionDenied as e:
            self._audit_denial(name, body, query, caller, e)
            raise

    def _audit_denial(self, method, body, query, caller, error) -> None:
        """Audit a denial in the repository the method used: named in the query for methods with a
        binary body, in the JSON params otherwise (as dispatch reads them), never in a query
        parameter a JSON method ignores."""
        try:
            m = self.methods.get(method)
            repo_name = (query.get("repo") or [None])[-1] if m is not None and m.binary_in else \
                (json.loads(body or b"{}").get("params") or {}).get("repo")
            repo = self.deployment.repo(repo_name)
        except Exception:  # an unknown or unnamed repository has no audit log to write to
            return
        repo.audit.append("denied", caller.user, method, {"principal": caller.principal, "tier": caller.tier,
                                                         "message": str(error)[:500]})

    def handle_http(self, method, path, query, headers, body, secure):
        self.deployment.maybe_reload()  # as for the RPCs: revoked tokens and new groups apply at once
        return self.ui.handle(method, path, query, headers, body, secure)

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

    def readable_repos(self, user) -> list[dict]:
        out = []
        for name in self.deployment.names():
            pol = self.deployment.policy_for(name)
            if pol.can_read_repo(user):
                out.append({"name": name, "public": pol.public, "writable": pol.can_write_repo(user)})
        return out

    def _list_repos(self, c, p):
        return self.readable_repos(c.user)

    def _server_info(self, c, p):
        if p.get("repo"):
            return {**self._repo(c, p).info(), "tier": self.tier}
        return {"tier": self.tier, "repos": [r["name"] for r in self._list_repos(c, p)]}

    def _get_changesets(self, c, p):
        repo = self._repo(c, p)
        return [self._changeset(c, repo, x) for x in _ids(p)]

    def _log(self, c, p):
        repo = self._repo(c, p)
        if _int(p, "skip", 0, 0, 1 << 62) > MAX_LIMIT:  # refused, not capped: a capped offset is the wrong page
            raise ValueError(f"skip is at most {MAX_LIMIT}: page from the last changeset seen instead")
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

    def _list_dir(self, c, p):
        """A directory's readable entries. With ``probe``, a directory the caller can't list returns
        None instead of 403: checkouts probe every directory whose tree they were denied, in case
        something beneath is readable (UC-01 3b), and those routine probes are not denials worth an
        audit entry. The answer reveals no more than the 403 would."""
        repo = self._repo(c, p)
        cs, path = repo.resolve(_str(p, "rev")), normalize_path(_str(p, "path", ""))
        if p.get("probe") and not repo.can_list(c.user, path):
            return None
        return repo.list_dir(cs, path, c.user)

    def _git_lookup(self, c, p):
        """Map a git commit to its changeset or back (FR-MG-07): ``{git, cs}``, or None."""
        repo = self._repo(c, p)
        if p.get("git"):
            row = repo.meta.git_map_lookup(git=_str(p, "git"))
        else:
            row = repo.meta.git_map_lookup(cs=repo.resolve(_str(p, "cs")))
        return {"git": row[0], "cs": row[1]} if row else None

    def _acl_epochs(self, c, p):
        """Each repository's ACL epoch, for the tiers (ADR-20); unknown repositories map to None."""
        repos = p.get("repos")
        if not isinstance(repos, list) or len(repos) > 1000 or not all(isinstance(x, str) for x in repos):
            raise ValueError("repos must be a list of at most 1000 names")
        out = {}
        for name in repos:
            try:
                out[name] = self.deployment.repo(name).acl_epoch()
            except (NotFound, ValueError):
                out[name] = None
        return out

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
            name, old = _str(ref, "name"), ref.get("old")
            landing = None
            if ref.get("record_landing"):  # index a direct landing (FR-LD-05), atomically with the move
                landing = self.antique(repo.name).landing(cs_id, name, repo.resolve(old) if old else None)
            moved = repo.update_ref(name, old, cs_id, user=c.user, landing=landing)
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

    def _admin_repo(self, c, p) -> Repository:
        repo = self._repo(c, p)
        if not repo.policy.is_admin(c.user):
            raise PermissionDenied("this operation is for administrators")
        return repo

    def _derive(self, c, p):
        repo = self._admin_repo(c, p)
        cs = repo.resolve(_str(p, "rev", "main"))
        computed = repo.derived.backfill(_str(p, "type"), cs)
        repo.audit.append("derive", c.user, p["type"], {"cs": cs, "computed": computed})
        return {"type": p["type"], "computed": computed}

    def _reindex_acl(self, c, p):
        repo = self._admin_repo(c, p)
        result = repo.reindex_acl()
        repo.audit.append("acl.reindex", c.user, repo.name, result)
        return result

    def _audit_log(self, c, p):
        repo = self._admin_repo(c, p)
        return repo.audit.entries(_int(p, "limit", 100, 1), p.get("action"), p.get("before"))

    def _create_release(self, c, p):
        """Create ``release/<name>`` at a changeset (FR-REF-05): the ref must not exist, and only
        principals allowed to move ``release/*`` may do it."""
        repo = self._repo(c, p)
        name = _str(p, "name")
        if not RELEASE_NAME.match(name):
            raise ValueError(f"invalid release name {name!r}")
        ref = f"release/{name}"
        if not repo.policy.can_update_ref(c.user, ref):
            raise PermissionDenied(f"{c.user or 'anonymous'} may not create {ref}")
        cs = repo.resolve(_str(p, "rev", "main"))
        if not repo.update_ref(ref, None, cs, user=c.user):
            raise ValueError(f"{ref} already exists")
        repo.audit.append("release.create", c.user, ref, {"cs": cs})
        return {"ref": ref, "target": cs}

    # -- Antique ---------------------------------------------------------------------------------------
    @staticmethod
    def _need_user(c) -> str:
        if not c.user:
            raise PermissionDenied("this operation needs an identity (X-Scion-User)")
        return c.user

    def _webhooks(self, repo_name: str) -> list[str]:
        try:
            return list(self.deployment.repo(repo_name).policy.review.get("webhooks", []))
        except Exception:
            return []

    def antique(self, repo_name: str) -> Antique:
        repo = self.deployment.repo(repo_name)
        with self._antiques_lock:
            a = self._antiques.get(repo.name)
            if a is None:
                a = self._antiques[repo.name] = Antique(repo, notify=self.notifier, audit=repo.audit.append,
                                                          log=self.log)
            return a

    def _antique(self, c, p, write: bool = False) -> Antique:
        return self.antique(self._repo(c, p, write=write).name)

    def _postmerge(self, c, p) -> Antique:
        """Post-merge results feed the deploy gate, so only services and administrators report them."""
        a = self._antique(c, p)
        if not (a.policy.is_service(c.user) or a.policy.is_admin(c.user)):
            raise PermissionDenied("post-merge jobs are claimed and reported by services and administrators")
        return a

    def _cr(self, c, p, fn):
        a = self._antique(c, p)
        return a.view(fn(a), c.user)

    def _cr_create(self, c, p):
        a = self._antique(c, p, write=True)
        return a.view(a.create(self._need_user(c), _str(p, "title"), _str(p, "head"), _str(p, "description", ""),
                               _str(p, "target", "main")), c.user)

    def _cr_list(self, c, p):
        a = self._antique(c, p)
        return [a.view(cr, c.user) for cr in a.list(p.get("state"), p.get("author"), _int(p, "limit", 50, 1))]

    def _cr_comment(self, c, p):
        a = self._antique(c, p)
        path = p.get("path")
        if path is not None and not a.repo.policy.can_read(c.user, _str(p, "path")):
            raise PermissionDenied(f"{c.user} may not read {path}")
        line = p.get("line")
        return a.view(a.comment(self._need_user(c), _int(p, "id", 0, 1, 1 << 62), _str(p, "body"), path,
                                None if line is None else _int(p, "line", 1, 1, 1 << 31)), c.user)

    def stats(self) -> dict:
        """Totals over all repositories: /stats is unauthenticated, so it names none of them."""
        s = super().stats()
        repos, antique = Counter(), Counter()
        for r in list(self.deployment._repos.values()):
            repos.update(r.stats)
        for a in list(self._antiques.values()):
            antique.update({k: v for k, v in a.counters.items() if k != "land.max_batch"})
            antique["land.max_batch"] = max(antique["land.max_batch"], a.counters["land.max_batch"])
            try:
                antique.update(a.queue_stats())
            except Exception as e:  # noqa: BLE001 - stats must answer even when a store is unwell
                self.log("warning", f"queue stats unavailable: {e}")
        s["repos"] = {"open": len(self.deployment._repos), **repos}
        clients = {id(c): c for r in list(self.deployment._repos.values())
                   if (c := getattr(r.meta, "client", None)) is not None}  # Spanner: shared by the repositories
        s["metadata"] = {"backend": self.deployment.metadata.get("backend", "sqlite"),
                         **sum((Counter(c.stats) for c in clients.values()), Counter())}
        s["antique"] = dict(antique)
        s["notify"] = dict(self.notifier.counters)
        return s

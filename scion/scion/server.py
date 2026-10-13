"""scion-server: the authoritative source-control API.

Every query the ``scn`` client uses is an RPC here, so CI jobs and tools can ask questions
(history, blame, ancestry, diffs, search) and even write changesets without any local checkout.
"""
from __future__ import annotations

import base64
import html
import json

from .antique import Antique
from .iam import PermissionDenied, Policy
from .objects import decode_stored
from .repo import Repository
from .rpc import Service, unpack_objects
from .search import grep, search_paths
from .tiers import MAX_IDS_PER_REQUEST, _ids_cost
from .rpc import pack_objects


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


class ScionService(Service):
    tier = "server"

    def __init__(self, repo: Repository, allow_direct_objects: bool = False, verbose: bool = False):
        super().__init__(policy=repo.policy, verbose=verbose)
        self.repo = repo
        self.antique = Antique(repo)
        object_callers = ("cache", "client") if allow_direct_objects else ("cache",)
        r = self.register
        # -- metadata reads --------------------------------------------------------------------
        r("whoami", lambda c, p: {"principal": c.principal, "user": c.user, "tier": c.tier,
                                  "admin": self.policy.is_admin(c.user)})
        r("server_info", lambda c, p: {**repo.info(), "tier": self.tier, "object_callers": list(object_callers)})
        r("resolve", lambda c, p: repo.resolve(p["rev"]))
        r("get_changeset", self._get_changeset)
        r("get_changesets", lambda c, p: [self._cs(c, x) for x in p["ids"]])
        r("log", self._log)
        r("root_tree", lambda c, p: repo.root_tree(repo.resolve(p["rev"])))
        r("list_dir", lambda c, p: repo.list_dir(repo.resolve(p["rev"]), p.get("path", ""), user=c.user))
        r("read_file", self._read_file)
        r("diff", self._diff)
        r("merge_base", self._merge_base)
        r("is_ancestor", lambda c, p: repo.is_ancestor(p["a"], p["b"]))
        r("fp_ancestor", lambda c, p: repo.fp_ancestor(repo.resolve(p["rev"]), int(p["n"])))
        r("file_history", lambda c, p: repo.file_history(p["rev"], p["path"], int(p.get("limit", 100)),
                                                         p.get("follow_copies", True), user=c.user), klass="heavy")
        r("blame", lambda c, p: repo.blame(p["rev"], p["path"], user=c.user), klass="heavy")
        r("search_paths", lambda c, p: search_paths(repo, p["rev"], p["query"], int(p.get("limit", 100)),
                                                    user=c.user), klass="heavy")
        r("grep", lambda c, p: grep(repo, p["rev"], p["pattern"], p.get("path", ""), int(p.get("limit", 200)),
                                    p.get("regex", True), p.get("ignore_case", False), user=c.user), klass="heavy")
        r("list_refs", lambda c, p: [{"name": n, "target": t, "version": v} for n, t, v in repo.meta.list_refs()])
        r("get_ref", lambda c, p: repo.get_ref(p["name"]))
        r("ref_log", lambda c, p: [{"old": o, "new": n, "who": w, "at": a}
                                   for o, n, w, a in repo.meta.ref_log(p["name"], int(p.get("limit", 50)))])
        # -- object protocol -------------------------------------------------------------------
        r("get_objects", self._get_objects, klass="objects", binary_out=True, tiers=object_callers, cost=_ids_cost)
        r("has_objects", lambda c, p: [o for o in p["ids"] if not repo.objects.has(o)], cost=_ids_cost)
        r("put_objects", self._put_objects, klass="write", binary_in=True)
        # -- writes ----------------------------------------------------------------------------
        r("create_changeset", self._create_changeset, klass="write")
        r("merge", lambda c, p: repo.merge(p["ours"], p["theirs"], c.user or "anonymous", p.get("message"),
                                           p.get("ff", False), user=c.user), klass="write")
        r("rebase", lambda c, p: repo.rebase(p["head"], p["onto"], p.get("base"), user=c.user), klass="write")
        r("revert", lambda c, p: repo.revert(p["cs"], p["onto"], c.user or "anonymous", p.get("message"),
                                             user=c.user), klass="write")
        r("update_ref", lambda c, p: repo.update_ref(p["name"], p.get("old"), p.get("new"), user=c.user),
          klass="write")
        # -- admin -----------------------------------------------------------------------------
        r("derive", self._derive, klass="heavy")
        # -- Antique ---------------------------------------------------------------------------
        a = self.antique
        r("antique.create", lambda c, p: a.create(self._need_user(c), p["title"], p["head"],
                                                  p.get("description", ""), p.get("target", "main")), klass="write")
        r("antique.update", lambda c, p: a.update(self._need_user(c), int(p["id"]), p["head"]), klass="write")
        r("antique.get", lambda c, p: a.get(int(p["id"])))
        r("antique.list", lambda c, p: a.list(p.get("state"), p.get("author"), int(p.get("limit", 50))))
        r("antique.approve", lambda c, p: a.approve(self._need_user(c), int(p["id"])), klass="write")
        r("antique.comment", lambda c, p: a.comment(self._need_user(c), int(p["id"]), p["body"],
                                                    p.get("path"), p.get("line")), klass="write")
        r("antique.requirements", lambda c, p: a.requirements(int(p["id"])), klass="heavy")
        r("antique.land", lambda c, p: a.land(self._need_user(c), int(p["id"]), force=p.get("force", False)),
          klass="write")
        r("antique.abandon", lambda c, p: a.abandon(self._need_user(c), int(p["id"])), klass="write")
        r("antique.find_landing", lambda c, p: a.find_landing(p["cs"]))
        r("antique.land_changeset", lambda c, p: a.land_changeset(self._need_user(c), p["cs"], p.get("ref", "main")),
          klass="write")
        r("antique.postmerge_claim", lambda c, p: a.postmerge_claim(self._need_user(c)), klass="write")
        r("antique.postmerge_report", lambda c, p: a.postmerge_report(int(p["id"]), bool(p["passed"]),
                                                                      p.get("log", "")), klass="write")
        r("antique.postmerge_status", lambda c, p: a.postmerge_status(p.get("ref", "main"), int(p.get("limit", 50))))
        r("antique.record_landing", self._record_landing, klass="write")

    # -----------------------------------------------------------------------------------------
    @staticmethod
    def _need_user(c) -> str:
        if not c.user:
            raise PermissionDenied("this operation requires an identity (X-Scion-User)")
        return c.user

    def _cs(self, c, rev):
        cs_id = self.repo.resolve(rev)
        d = self.repo.changeset_api(cs_id)
        d["changes"] = [ch for ch in d["changes"] if self.policy.can_read(c.user, ch["path"])]
        return d

    def _get_changeset(self, c, p):
        return self._cs(c, p["rev"])

    def _log(self, c, p):
        ids = self.repo.log(p.get("rev", "main"), int(p.get("limit", 50)), p.get("first_parent", True),
                            p.get("path"), int(p.get("skip", 0)))
        if p.get("ids_only"):
            return ids
        out = []
        for i in ids:
            cs = self.repo.get_changeset(i)
            out.append({"id": i, "parents": list(cs.parents), "author": cs.author, "timestamp": cs.timestamp,
                        "summary": cs.summary(), "files": len(cs.changes)})
        return out

    def _read_file(self, c, p):
        kind, blob, data = self.repo.read_file(self.repo.resolve(p["rev"]), p["path"], user=c.user)
        return {"kind": kind, "blob": blob, "content_b64": _b64(data)}

    def _diff(self, c, p):
        b = self.repo.resolve(p["b"])
        a = p.get("a")
        if p.get("merge_base"):
            a = self.repo.merge_base(a or "main", b)
        elif a:
            a = self.repo.resolve(a)
        else:
            a = self.repo.get_changeset(b).first_parent
        files = self.repo.diff(a, b, p.get("paths"), user=c.user)
        out = {"a": a, "b": b, "files": files}
        if p.get("text"):
            out["text"] = self.repo.diff_text(a, b, p.get("paths"), user=c.user, context=int(p.get("context", 3)))
        return out

    def _merge_base(self, c, p):
        bases = self.repo.merge_bases(p["a"], p["b"])
        return {"base": bases[0] if bases else None, "all": bases}

    def _get_objects(self, c, p):
        ids = p["ids"]
        if len(ids) > MAX_IDS_PER_REQUEST:
            raise ValueError(f"at most {MAX_IDS_PER_REQUEST} ids per request")
        return pack_objects(self.repo.fetch_objects(ids, c.user))

    def _put_objects(self, c, body: bytes):
        if not self.policy.can_write(c.user, ""):
            raise PermissionDenied(f"{c.user} may not write")
        stored = 0
        for oid, _flags, data in unpack_objects(body):
            otype, _ = decode_stored(data, expected_id=oid)  # verify integrity
            if otype != "blob":
                raise ValueError("clients may only upload blobs; trees are derived on the server")
            self.repo.objects.put_stored(oid, data, verify=False)
            stored += 1
        return {"stored": stored}

    def _create_changeset(self, c, p):
        files = []
        for f in p["files"]:
            f = dict(f)
            if "content_b64" in f:
                f["content"] = base64.b64decode(f.pop("content_b64"))
            files.append(f)
        author = p.get("author") or c.user or "anonymous"
        if author != c.user and not (self.policy.is_admin(c.user) or self.policy.is_service(c.user)):
            raise PermissionDenied("only admins and services may set a different author")
        cs_id = self.repo.create_changeset(p.get("parents", []), files, author, p.get("message", ""),
                                           p.get("timestamp"), p.get("extra"), user=c.user)
        moved = None
        if p.get("update_ref"):
            ref = p["update_ref"]
            moved = self.repo.update_ref(ref["name"], ref.get("old"), cs_id, user=c.user)
            if moved and ref.get("record_landing"):
                self.antique.record_direct_landing(cs_id, ref["name"], ref.get("old"))
        return {"id": cs_id, "ref_updated": moved}

    def _record_landing(self, c, p):
        if not (self.policy.is_admin(c.user) or self.policy.is_service(c.user)):
            raise PermissionDenied("services only")
        self.antique.record_direct_landing(self.repo.resolve(p["cs"]), p["ref"], p.get("old"))
        return True

    def _derive(self, c, p):
        if not self.policy.is_admin(c.user) and self.policy.admins:
            raise PermissionDenied("admins only")
        cs = self.repo.resolve(p.get("rev", "main"))
        return {"type": p["type"], "computed": self.repo.derived.backfill(p["type"], cs)}

    # -- stats & UI --------------------------------------------------------------------------------
    def stats(self) -> dict:
        s = super().stats()
        s["repo"] = dict(self.repo.stats)
        s["derived"] = dict(self.repo.derived.stats)
        s["antique"] = dict(self.antique.counters)
        s["rate_limiter"] = {"rejections": self.limiter.rejections}
        return s

    def handle_get(self, path, query, caller):
        if path in ("/", "/antique", "/antique/"):
            return 200, "text/html; charset=utf-8", self._page_list().encode()
        if path.startswith("/antique/cr/"):
            try:
                cr_id = int(path.rsplit("/", 1)[1])
            except ValueError:
                return None
            return 200, "text/html; charset=utf-8", self._page_cr(cr_id, caller).encode()
        return None

    # A deliberately small, read-only HTML view of Antique.
    _CSS = """
    :root{--bg:#fbfaf7;--fg:#1f1e1c;--muted:#6b675f;--line:#e4e0d6;--accent:#b4541a;--ok:#2f7a3d;--bad:#a8322a}
    @media (prefers-color-scheme:dark){:root{--bg:#191817;--fg:#ecebe6;--muted:#a29d92;--line:#34322e;--accent:#e08a4d;--ok:#6cc27c;--bad:#ef7b70}}
    body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:980px;padding:24px 16px}
    a{color:var(--accent)} table{border-collapse:collapse;width:100%} td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}
    .muted{color:var(--muted)} .ok{color:var(--ok)} .bad{color:var(--bad)} pre{overflow-x:auto;background:rgba(127,127,127,.08);padding:12px;border-radius:6px;font-size:13px}
    code{font-size:13px}
    """

    def _page(self, title: str, body: str) -> str:
        return (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                f"<title>{html.escape(title)}</title><style>{self._CSS}</style></head><body>{body}</body></html>")

    def _page_list(self) -> str:
        rows = []
        for cr in self.antique.list(limit=200):
            rows.append(f"<tr><td><a href='/antique/cr/{cr['id']}'>#{cr['id']}</a></td><td>{html.escape(cr['title'])}</td>"
                        f"<td>{html.escape(cr['author'])}</td><td>{cr['state']}</td><td><code>{cr['head'][:12]}</code></td></tr>")
        return self._page("Antique", "<h1>Antique</h1><p class=muted>Change requests</p><table><tr><th>CR</th><th>Title</th>"
                                     "<th>Author</th><th>State</th><th>Head</th></tr>" + "".join(rows) + "</table>")

    def _page_cr(self, cr_id: int, caller) -> str:
        cr = self.antique.get(cr_id)
        req = cr.get("requirements")
        parts = [f"<p><a href='/antique'>&larr; all change requests</a></p><h1>#{cr['id']} {html.escape(cr['title'])}</h1>",
                 f"<p class=muted>{html.escape(cr['author'])} &middot; {cr['state']} &middot; target {html.escape(cr['target'])}"
                 f" &middot; revision {cr['revision']}</p><p>{html.escape(cr['description'])}</p>"]
        if req:
            parts.append("<h2>Approval requirements</h2><table><tr><th>Scope</th><th>Category</th><th>Need</th><th>Have</th><th></th></tr>")
            for g in req["groups"]:
                cls = "ok" if g["satisfied"] else "bad"
                parts.append(f"<tr><td><code>{html.escape(g['prefix'] or '/')}</code></td><td>{g['category']}</td>"
                             f"<td>{g['need']}</td><td>{g['have']}</td><td class={cls}>{'✓' if g['satisfied'] else '✗'}</td></tr>")
            parts.append("</table>")
        if cr.get("conflict"):
            parts.append(f"<h2 class=bad>Conflicts</h2><pre>{html.escape(json.dumps(cr['conflict'], indent=2))}</pre>")
        parts.append("<h2>Approvals</h2><ul>" + "".join(
            f"<li>{html.escape(a['user'])} (rev {a['rev']})</li>" for a in cr["approvals"]) + "</ul>")
        parts.append("<h2>Comments</h2>" + "".join(
            f"<p><b>{html.escape(cm['user'])}</b> <span class=muted>{html.escape(cm['path'] or '')}"
            f"{':' + str(cm['line']) if cm['line'] else ''}</span><br>{html.escape(cm['body'])}</p>" for cm in cr["comments"]))
        try:
            base = self.repo.merge_base(cr["head"], self.repo.get_ref(cr["target"])) if cr["state"] != "landed" else \
                self.repo.get_changeset(cr["head"]).first_parent
            text = self.repo.diff_text(base, cr["head"], user=caller.user)
        except Exception as e:  # pragma: no cover
            text = f"(diff unavailable: {e})"
        parts.append(f"<h2>Diff</h2><pre>{html.escape(text)}</pre>")
        return self._page(f"CR {cr_id}", "".join(parts))


def make_server(repo_path: str, policy_path: str | None = None, allow_direct_objects: bool = False,
                verbose: bool = False) -> ScionService:
    return ScionService(Repository(repo_path, Policy.load(policy_path)), allow_direct_objects, verbose)

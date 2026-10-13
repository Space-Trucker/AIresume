"""Command-line programs: ``scn`` and the services (FR-CL-11).

``python -m scion <program> ...`` runs any of them; after installation the console scripts
``scn``, ``scion-server``, ``scion-cache``, ``scion-daemon`` and ``scion-admin`` do the same.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import signal
import sys
import threading
import time

from . import fsmonitor
from .client import ClientError, ServerApi, WorkingCopy
from .iam import Identity, hash_token
from .rpc import ClientTls, RemoteError, RpcServer, TlsConfig


def _print_json(v) -> None:
    print(json.dumps(v, indent=2, sort_keys=True))


def _read_token(path: str | None) -> str | None:
    if not path:
        return os.environ.get("SCION_TOKEN")
    with open(os.path.expanduser(path)) as f:
        return f.read().strip()


# ========================================================================================= scn
def _scn_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="scn", description="Scion client")
    p.add_argument("--server", help="server URL (default: the working copy's)")
    p.add_argument("--repo", help="repository name (default: the working copy's)")
    p.add_argument("--user", help="your principal (default: the working copy's, or $USER)")
    p.add_argument("--token-file", help="file holding your bearer token (or set $SCION_TOKEN)")
    p.add_argument("--ca", help="CA certificate for https:// servers")
    p.add_argument("-C", dest="cwd", default=".", help="run as if started in this directory")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("clone", help="check out a revision")
    s.add_argument("dest")
    s.add_argument("--rev", default="main")
    s.add_argument("--objects", help="object endpoint, normally the node daemon (unix:/path)")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--sparse", nargs="+", metavar="DIR", help="check out only these directories")
    g.add_argument("--virtual", action="store_true", help="materialize files only when read")
    s.add_argument("--cache-bytes", type=int, default=2 << 30)

    s = sub.add_parser("status", help="show local changes")
    s.add_argument("--json", action="store_true")
    s.add_argument("--no-fsmonitor", action="store_true")
    for name, helptext in (("add", "track new files"), ("restore", "discard local changes"),
                           ("materialize", "write files of a virtual checkout")):
        s = sub.add_parser(name, help=helptext)
        s.add_argument("paths", nargs="+")
    s = sub.add_parser("rm", help="remove tracked files")
    s.add_argument("--keep", action="store_true", help="stop tracking but keep the file on disk")
    s.add_argument("paths", nargs="+")
    s = sub.add_parser("diff", help="local changes, or a diff between revisions with -r")
    s.add_argument("-r", "--rev", action="append", default=[], help="one (against its first parent) or two revisions")
    s.add_argument("--merge-base", action="store_true", help="diff -r B against its merge base with -r A")
    s.add_argument("--stat", action="store_true")
    s.add_argument("paths", nargs="*")
    s = sub.add_parser("commit", help="create a changeset on the server (nothing to push)")
    s.add_argument("-m", "--message", required=True)
    s.add_argument("-A", "--addremove", action="store_true", help="include untracked files")
    s.add_argument("paths", nargs="*")
    s = sub.add_parser("update", help="move the working copy to a revision")
    s.add_argument("rev", nargs="?")
    s.add_argument("--clean", action="store_true", help="overwrite conflicting local changes")
    s = sub.add_parser("rebase", help="rebase the local stack on the server, then update")
    s.add_argument("--onto")
    s = sub.add_parser("stack", help="local changesets not in the tracked revision")
    s.add_argument("--onto")
    s = sub.add_parser("sparse", help="show or change the sparse profile")
    s.add_argument("action", choices=["show", "add", "remove"])
    s.add_argument("dirs", nargs="*")
    s = sub.add_parser("watch", help="the filesystem monitor")
    s.add_argument("action", choices=["start", "stop", "status"])

    s = sub.add_parser("log", help="changesets, newest first")
    s.add_argument("path", nargs="?")
    s.add_argument("-r", "--rev")
    s.add_argument("-n", "--limit", type=int, default=20)
    s.add_argument("--all-parents", action="store_true")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("show", help="one changeset")
    s.add_argument("rev", nargs="?")
    s.add_argument("--json", action="store_true")
    for name in ("blame", "history", "cat"):
        s = sub.add_parser(name)
        s.add_argument("path")
        s.add_argument("-r", "--rev")
        if name == "history":
            s.add_argument("-n", "--limit", type=int, default=50)
    s = sub.add_parser("ls", help="list a directory")
    s.add_argument("path", nargs="?", default="")
    s.add_argument("-r", "--rev")
    s = sub.add_parser("search", help="find paths")
    s.add_argument("query")
    s.add_argument("-r", "--rev")
    s.add_argument("-n", "--limit", type=int, default=100)
    for name in ("merge-base", "is-ancestor"):
        s = sub.add_parser(name)
        s.add_argument("a")
        s.add_argument("b")
    sub.add_parser("refs", help="list refs")
    s = sub.add_parser("ref-log", help="a ref's compare-and-swap history")
    s.add_argument("name")
    sub.add_parser("whoami")
    sub.add_parser("repos", help="repositories you can read")
    s = sub.add_parser("review", help="change requests in Antique")
    rv = s.add_subparsers(dest="action", required=True)
    x = rv.add_parser("create", help="open a change request for a changeset (default: the working copy's)")
    x.add_argument("--title", required=True)
    x.add_argument("--description", default="")
    x.add_argument("--head")
    x.add_argument("--target", default="main")
    x = rv.add_parser("update", help="upload a new revision (approvals reset)")
    x.add_argument("id", type=int)
    x.add_argument("--head")
    x = rv.add_parser("list")
    x.add_argument("--state", default="open", help="open, landing, conflict, landed, abandoned or all")
    x.add_argument("--author")
    for name in ("show", "approve", "abandon", "requirements"):
        rv.add_parser(name).add_argument("id", type=int)
    x = rv.add_parser("comment")
    x.add_argument("id", type=int)
    x.add_argument("body")
    x.add_argument("--path")
    x.add_argument("--line", type=int)
    x = rv.add_parser("land", help="rebase onto the target and publish it with one compare-and-swap")
    x.add_argument("id", type=int)
    x.add_argument("--force", action="store_true", help="administrators: land without the approvals (audited)")
    x = rv.add_parser("landing", help="when and how a changeset landed (by landed or original id)")
    x.add_argument("cs")
    s = sub.add_parser("release", help="release branches")
    s.add_argument("action", choices=["create"])
    s.add_argument("name")
    s.add_argument("--rev", default="main")
    s = sub.add_parser("audit", help="the repository's audit log (administrators)")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--action")
    s.add_argument("--verify", action="store_true", help="check the hash chain")
    s = sub.add_parser("api", help="call any RPC: `scn api METHOD key=value ...`, or `scn api commit ...`")
    s.add_argument("method")
    s.add_argument("args", nargs=argparse.REMAINDER)
    return p


def _api_commit_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="scn api commit", description="create a changeset without a checkout")
    p.add_argument("--parent", action="append", default=[], help="parent revision (repeatable)")
    p.add_argument("-m", "--message", required=True)
    p.add_argument("--file", action="append", default=[], metavar="PATH=LOCAL", help="set PATH to LOCAL's content")
    p.add_argument("--exec", action="append", default=[], metavar="PATH=LOCAL", help="the same, as an executable")
    p.add_argument("--delete", action="append", default=[], metavar="PATH")
    p.add_argument("--ref", help="compare-and-swap this ref to the new changeset")
    p.add_argument("--old", help="the ref's expected value (default: the first parent)")
    return p


def _parse_value(v: str):
    try:
        return json.loads(v)
    except ValueError:
        return v


class _Ctx:
    def __init__(self, args):
        self.args = args
        self._wc: WorkingCopy | None = None
        self._api: ServerApi | None = None

    def wc(self) -> WorkingCopy:
        if self._wc is None:
            self._wc = WorkingCopy.find(self.args.cwd)
        return self._wc

    def api(self) -> ServerApi:
        if self._api is not None:
            return self._api
        a = self.args
        if a.server:
            tls = ClientTls(a.ca) if a.ca else None
            self._api = ServerApi(a.server, a.repo, a.user or os.environ.get("USER"), _read_token(a.token_file), tls)
        else:
            self._api = self.wc().api
        return self._api

    def default_rev(self) -> str:
        try:
            return self.wc().base or "main"
        except ClientError:
            return "main"


def scn_main(argv=None) -> int:
    args = _scn_parser().parse_args(argv)
    ctx = _Ctx(args)
    try:
        return _scn(ctx, args) or 0
    except (ClientError, RemoteError, FileNotFoundError, ValueError) as e:
        print(f"scn: {e}", file=sys.stderr)
        return 1
    finally:
        if ctx._wc is not None:
            ctx._wc.close()


def _scn(ctx: _Ctx, a) -> int | None:  # noqa: C901 - one branch per command
    cmd = a.command
    if cmd == "clone":
        if not (a.server and a.repo):
            raise ClientError("clone needs --server and --repo")
        mode = "virtual" if a.virtual else "sparse" if a.sparse else "full"
        wc = WorkingCopy.clone(os.path.join(a.cwd, a.dest), a.server, a.repo, objects=a.objects, rev=a.rev,
                               mode=mode, sparse=a.sparse, user=a.user or os.environ.get("USER"),
                               token_file=a.token_file, tls_ca=a.ca, cache_bytes=a.cache_bytes)
        c = wc.fetcher.counters
        print(f"checked out {wc.base[:12]} ({mode}): {c['fetched']} objects fetched, {c['local_hits']} from cache")
        wc.close()
        return 0
    if cmd == "status":
        st = ctx.wc().status(use_fsmonitor=not a.no_fsmonitor)
        if a.json:
            _print_json(st.to_dict())
        else:
            for tag, lst in (("M", st.modified), ("A", st.added), ("R", st.removed), ("?", st.untracked)):
                for p in lst:
                    print(f"{tag} {p}")
        return 0
    if cmd in ("add", "rm", "restore"):
        wc = ctx.wc()
        paths = [wc.rel(os.path.join(a.cwd, p)) for p in a.paths]
        if cmd == "add":
            done = wc.add(paths)
        elif cmd == "rm":
            done = wc.remove(paths, keep=a.keep)
        else:
            done = wc.restore(paths)
        for p in done:
            print(p)
        return 0
    if cmd == "materialize":
        wc = ctx.wc()
        print(f"{wc.materialize([wc.rel(os.path.join(a.cwd, p)) for p in a.paths])} files written")
        return 0
    if cmd == "diff":
        if not a.rev:
            wc = ctx.wc()
            sys.stdout.write(wc.diff_local([wc.rel(os.path.join(a.cwd, p)) for p in a.paths] or None))
            return 0
        if len(a.rev) > 2:
            raise ClientError("give one or two revisions")
        params = {"b": a.rev[-1], "text": not a.stat, "paths": a.paths or None}
        if len(a.rev) == 2:
            params["a"] = a.rev[0]
        if a.merge_base:
            params["merge_base"] = True
        d = ctx.api().diff(**params)
        if a.stat:
            for f in d["files"]:
                print(f"{f['status']} {f['path']}")
        else:
            sys.stdout.write(d.get("text", ""))
        return 0
    if cmd == "commit":
        wc = ctx.wc()
        cs = wc.commit(a.message, [wc.rel(os.path.join(a.cwd, p)) for p in a.paths] or None, a.addremove)
        print(f"created {cs} (nothing to push)")
        return 0
    if cmd == "update":
        wc = ctx.wc()
        r = wc.update(a.rev or wc.config.get("track") or "main", clean=a.clean)
        print(f"at {r['base'][:12]}: {r['written']} written, {r['deleted']} deleted")
        return 0
    if cmd == "rebase":
        r = ctx.wc().rebase(a.onto)
        print(f"rebased {len(r['rebased'])} changeset(s); now at {r['head'][:12]}")
        return 0
    if cmd == "stack":
        for cs in ctx.wc().stack(a.onto):
            info = ctx.api().get_changeset(rev=cs)
            print(f"{cs[:12]} {info['message'].splitlines()[0] if info['message'] else ''}")
        return 0
    if cmd == "sparse":
        wc = ctx.wc()
        if a.action == "show":
            print("\n".join(wc.profile.prefixes) if wc.mode == "sparse" else f"({wc.mode} checkout)")
        elif a.action == "add":
            print(f"{wc.sparse_add(a.dirs)} files written")
        else:
            print(f"{wc.sparse_remove(a.dirs)} files removed")
        return 0
    if cmd == "watch":
        root = ctx.wc().root
        if a.action == "start":
            print(f"fsmonitor running (pid {fsmonitor.start(root)})")
        elif a.action == "stop":
            print("stopped" if fsmonitor.stop(root) else "not running")
        else:
            pid = fsmonitor.running(root)
            print(f"running (pid {pid})" if pid else "not running")
        return 0
    api = ctx.api()
    if cmd == "log":
        rows = api.log(rev=a.rev or ctx.default_rev(), limit=a.limit, path=a.path, first_parent=not a.all_parents)
        if a.json:
            _print_json(rows)
        else:
            for r in rows:
                print(f"{r['id'][:12]} {r['author']:<12} {r['summary']}")
        return 0
    if cmd == "show":
        cs = api.get_changeset(rev=a.rev or ctx.default_rev())
        if a.json:
            _print_json(cs)
            return 0
        print(f"changeset {cs['id']}\nauthor    {cs['author']}\nparents   {' '.join(cs['parents'])}\n\n{cs['message']}\n")
        for ch in cs["changes"]:
            print(f"  {ch['op']} {ch['path']}")
        return 0
    if cmd == "blame":
        r = api.blame(rev=a.rev or ctx.default_rev(), path=a.path)
        if r.get("binary"):
            print(f"{a.path}: binary file")
        for line in r["lines"]:
            who = r["changesets"][line["cs"]]["author"]
            print(f"{line['cs'][:12]} {who:<12} {line['line']:>5}: {line['text']}", end="" if line["text"].endswith("\n") else "\n")
        return 0
    if cmd == "history":
        for h in api.file_history(rev=a.rev or ctx.default_rev(), path=a.path, limit=a.limit):
            info = api.get_changeset(rev=h["cs"])
            print(f"{h['cs'][:12]} {info['author']:<12} {h['path']}  {info['message'].splitlines()[0] if info['message'] else ''}")
        return 0
    if cmd == "cat":
        if a.rev is None:
            try:
                wc = ctx.wc()
                sys.stdout.buffer.write(wc.read(wc.rel(os.path.join(a.cwd, a.path))))
                return 0
            except (ClientError, FileNotFoundError):
                pass  # not in this working copy: ask the server
        r = api.read_file(rev=a.rev or ctx.default_rev(), path=a.path)
        sys.stdout.buffer.write(base64.b64decode(r["content_b64"]))
        return 0
    if cmd == "ls":
        for e in api.list_dir(rev=a.rev or ctx.default_rev(), path=a.path):
            print(f"{e['kind']} {e['path']}{'/' if e['kind'] == 'd' else ''}")
        return 0
    if cmd == "search":
        r = api.search_paths(rev=a.rev or ctx.default_rev(), query=a.query, limit=a.limit)
        print("\n".join(r["paths"]))
        return 0
    if cmd == "merge-base":
        print(api.merge_base(a=a.a, b=a.b)["base"] or "(none)")
        return 0
    if cmd == "is-ancestor":
        yes = api.is_ancestor(a=a.a, b=a.b)
        print("yes" if yes else "no")
        return 0 if yes else 1
    if cmd == "refs":
        for r in api.list_refs():
            print(f"{r['target'][:12]} {r['name']}")
        return 0
    if cmd == "ref-log":
        for r in api.ref_log(name=a.name):
            print(f"{(r['old'] or '-')[:12]} -> {(r['new'] or '-')[:12]} by {r['who']}")
        return 0
    if cmd == "whoami":
        _print_json(api.rpc.call("whoami", repo=api.repo))
        return 0
    if cmd == "repos":
        for r in api.rpc.call("list_repos"):
            print(f"{r['name']}{'' if r['public'] else ' (private)'}")
        return 0
    if cmd == "review":
        return _review(ctx, api, a)
    if cmd == "release":
        _print_json(api.create_release(name=a.name, rev=a.rev))
        return 0
    if cmd == "audit":
        if a.verify:
            r = api.audit_verify()
            print(f"{'ok' if r['ok'] else 'BROKEN at entry ' + str(r['first_bad'])}: {r['entries']} entries")
            return 0 if r["ok"] else 1
        for e in reversed(api.audit_log(limit=a.limit, action=a.action)):
            print(f"{e['seq']:>6} {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(e['at']))} {e['actor'] or '-':<12} "
                  f"{e['action']:<16} {e['target']} {json.dumps(e['detail'], sort_keys=True)}")
        return 0
    if cmd == "api":
        if a.method == "commit":
            return _api_commit(api, a.args)
        params = {}
        for kv in a.args:
            k, sep, v = kv.partition("=")
            if not sep:
                raise ClientError(f"expected key=value, got {kv!r}")
            params[k] = _parse_value(v)
        _print_json(api.call(a.method, **params))
        return 0
    raise ClientError(f"unknown command {cmd}")


def _review(ctx: _Ctx, api: ServerApi, a) -> int:
    """``scn review ...`` (FR-CL-11 for FR-RV-*)."""
    act = a.action
    if act == "create":
        head = a.head or ctx.wc().base
        cr = api.call("antique.create", title=a.title, head=head, description=a.description, target=a.target)
        print(f"created change request {cr['id']} ({cr['state']})")
        return 0
    if act == "update":
        cr = api.call("antique.update", id=a.id, head=a.head or ctx.wc().base)
        print(f"change request {cr['id']} is at revision {cr['revision']}")
        return 0
    if act == "list":
        for cr in api.call("antique.list", state=None if a.state == "all" else a.state, author=a.author):
            print(f"{cr['id']:>5} {cr['state']:<10} {cr['author']:<12} {cr['title']}")
        return 0
    if act == "show":
        cr = api.call("antique.get", id=a.id)
        print(f"#{cr['id']} {cr['title']}\n{cr['author']} · {cr['state']} · target {cr['target']} · revision "
              f"{cr['revision']} · head {cr['head'][:12]}\n")
        if cr["description"]:
            print(cr["description"] + "\n")
        for g in (cr.get("requirements") or {}).get("groups", []):
            mark = "ok" if g["satisfied"] else "needs"
            print(f"  /{g['prefix']:<20} {g['category']:<13} {mark}: {g['need']} have {g['have']}")
        if cr.get("conflict"):
            for c in cr["conflict"]["conflicts"]:
                print(f"  conflict: {c['path']}: {c['reason']}")
        for c in cr["comments"]:
            where = f" {c['path']}:{c['line']}" if c["path"] else ""
            print(f"  [{c['user']}{where}] {c['body']}")
        return 0
    if act in ("approve", "abandon"):
        cr = api.call(f"antique.{act}", id=a.id)
        print(f"change request {cr['id']}: {cr['state']}")
        return 0
    if act == "requirements":
        r = api.call("antique.requirements", id=a.id)
        _print_json({k: r[k] for k in ("satisfied", "revision", "approvers")} |
                    {"groups": [{k: g[k] for k in ("prefix", "category", "need", "have", "satisfied")} for g in r["groups"]]})
        return 0 if r["satisfied"] else 1
    if act == "comment":
        api.call("antique.comment", id=a.id, body=a.body, path=a.path, line=a.line)
        print("commented")
        return 0
    if act == "land":
        cr = api.call("antique.land", id=a.id, force=a.force)
        print(f"landed {cr['landed_cs']} on {cr['target']}")
        return 0
    if act == "landing":
        r = api.call("antique.find_landing", cs=a.cs)
        if r is None:
            print("not landed")
            return 1
        when = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(r["landed_at"]))
        print(f"{r['cs']} on {r['ref']} at {when}" + (f" through change request {r['cr']}" if r["cr"] else "")
              + (f" (originally {r['source']})" if r["source"] != r["cs"] else ""))
        return 0
    raise ClientError(f"unknown review action {act}")


def _api_commit(api: ServerApi, argv) -> int:
    """Write a changeset with API calls only (FR-WR-01/05)."""
    a = _api_commit_parser().parse_args(argv)
    files = []
    for spec, kind in [(s, "f") for s in a.file] + [(s, "x") for s in a.exec]:
        path, sep, local = spec.partition("=")
        if not sep:
            raise ClientError(f"expected PATH=LOCAL, got {spec!r}")
        with open(local, "rb") as f:
            files.append({"path": path, "kind": kind, "content_b64": base64.b64encode(f.read()).decode()})
    files.extend({"path": p, "delete": True} for p in a.delete)
    parents = [api.resolve(rev=p) for p in a.parent]
    params = {"parents": parents, "files": files, "message": a.message}
    if a.ref:
        params["update_ref"] = {"name": a.ref, "old": a.old or (parents[0] if parents else None)}
    _print_json(api.create_changeset(**params))
    return 0


# ==================================================================================== services
def _serve(server: RpcServer, on_stop=None) -> int:
    print(f"{server.service.tier} listening on {server.url}", flush=True)
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    server.start()
    stop.wait()
    server.stop()
    if on_stop:
        on_stop()
    return 0


def _tls_server_args(p) -> None:
    p.add_argument("--tls-cert", help="serve https with this certificate")
    p.add_argument("--tls-key")
    p.add_argument("--client-ca", help="verify client certificates (mutual TLS between tiers)")


def _tls_client_args(p) -> None:
    p.add_argument("--ca", help="CA certificate of the upstream tier")
    p.add_argument("--cert", help="this tier's client certificate (mutual TLS)")
    p.add_argument("--key")


def _server_tls(a) -> TlsConfig | None:
    return TlsConfig(a.tls_cert, a.tls_key, a.client_ca) if a.tls_cert else None


def _listen(a) -> str:
    if "://" in a.listen or a.listen.startswith("unix:"):
        return a.listen
    return f"{'https' if a.tls_cert else 'http'}://{a.listen}"


def server_main(argv=None) -> int:
    from .deployment import Deployment
    from .server import ScionService

    p = argparse.ArgumentParser(prog="scion-server")
    p.add_argument("--root", required=True, help="deployment root (deployment.json, repos/)")
    p.add_argument("--listen", default="127.0.0.1:7070")
    p.add_argument("--allow-direct-objects", action="store_true", help="development: serve objects to clients")
    p.add_argument("-v", "--verbose", action="store_true")
    _tls_server_args(p)
    a = p.parse_args(argv)
    dep = Deployment(a.root)
    svc = ScionService(dep, allow_direct_objects=a.allow_direct_objects, verbose=a.verbose)
    signal.signal(signal.SIGHUP, lambda *_: svc.reload())  # re-read policies (UC-22)
    return _serve(RpcServer(svc, _listen(a), tls=_server_tls(a)), dep.close)


def cache_main(argv=None) -> int:
    from .tiers import make_cache_service

    p = argparse.ArgumentParser(prog="scion-cache")
    p.add_argument("--listen", default="127.0.0.1:7080")
    p.add_argument("--upstream", action="append", required=True, help="server URL (repeat for failover)")
    p.add_argument("--max-bytes", type=int, default=8 << 30)
    p.add_argument("--identity", help="deployment.json: tokens of the daemons that may connect")
    p.add_argument("--token-file", help="this cache's token for the servers (without mutual TLS)")
    p.add_argument("-v", "--verbose", action="store_true")
    _tls_server_args(p)
    _tls_client_args(p)
    a = p.parse_args(argv)
    tls = ClientTls(a.ca, a.cert, a.key) if a.ca else None
    svc = make_cache_service(a.upstream, a.max_bytes, Identity.load(a.identity), _read_token(a.token_file), tls,
                             verbose=a.verbose)
    return _serve(RpcServer(svc, _listen(a), tls=_server_tls(a)))


def daemon_main(argv=None) -> int:
    from .tiers import DaemonService

    p = argparse.ArgumentParser(prog="scion-daemon")
    p.add_argument("--socket", required=True, help="Unix socket path for the jobs on this node")
    p.add_argument("--socket-mode", default="660", help="permissions of the socket (octal)")
    p.add_argument("--upstream", action="append", required=True, help="regional cache URL (repeat for failover)")
    p.add_argument("--store", required=True, help="directory of the bounded node store")
    p.add_argument("--max-bytes", type=int, default=32 << 30)
    p.add_argument("--snapshots", help="snapshot directory to warm-start from and refresh")
    p.add_argument("--refresh", type=float, default=300.0, help="seconds between snapshot checks")
    p.add_argument("--token-file", help="this daemon's token for the caches (without mutual TLS)")
    p.add_argument("-v", "--verbose", action="store_true")
    _tls_client_args(p)
    a = p.parse_args(argv)
    tls = ClientTls(a.ca, a.cert, a.key) if a.ca else None
    svc = DaemonService(a.store, a.upstream, a.max_bytes, a.snapshots, a.refresh, token=_read_token(a.token_file),
                        tls=tls, verbose=a.verbose)
    return _serve(RpcServer(svc, f"unix:{a.socket}", socket_mode=int(a.socket_mode, 8)), svc.stop)


def admin_main(argv=None) -> int:
    import getpass

    from .deployment import Deployment
    from .iam import PermissionDenied
    from .repo import NotFound
    from .snapshot import create_snapshot

    p = argparse.ArgumentParser(prog="scion-admin")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("init", help="create a deployment root")
    s.add_argument("--root", required=True)
    s = sub.add_parser("create-repo", help="create a repository")
    s.add_argument("--root", required=True)
    s.add_argument("name")
    s.add_argument("--read", nargs="+", default=["*"], help="principals and groups that may read")
    s.add_argument("--write", nargs="+", default=["*"], help="principals and groups that may write")
    s.add_argument("--admin", nargs="*", default=[])
    s = sub.add_parser("repos", help="list repositories")
    s.add_argument("--root", required=True)
    s = sub.add_parser("snapshot", help="publish a daemon snapshot of a revision (FR-TIER-11)")
    s.add_argument("--root", required=True)
    s.add_argument("--repo", required=True)
    s.add_argument("--rev", default="main")
    s.add_argument("--out", required=True, help="snapshot directory (the repository's subdirectory is used)")
    s = sub.add_parser("derive", help="backfill a derived-data type (FR-DD-06)")
    s.add_argument("--root", required=True)
    s.add_argument("--repo", required=True)
    s.add_argument("type")
    s.add_argument("rev", nargs="?", default="main")
    s = sub.add_parser("gen-certs", help="development CA and certificates (needs the openssl tool)")
    s.add_argument("dir")
    s = sub.add_parser("hash-token", help="the form of a token to store in deployment.json")
    s.add_argument("token")
    s = sub.add_parser("set-ref", help="move a ref by compare-and-swap, as an explicit identity (FR-AD-05)")
    s.add_argument("--root", required=True)
    s.add_argument("--repo", required=True)
    s.add_argument("--ref", required=True)
    s.add_argument("--to", required=True, help="the new target revision ('-' deletes the ref)")
    s.add_argument("--old", help="the expected current value (default: the current value)")
    s.add_argument("--as", dest="as_user", required=True,
                   help="the principal whose permissions apply; protected refs are enforced for it")
    s = sub.add_parser("reindex-acl", help="rebuild the object ACL index after a policy change (FR-IAM-09)")
    s.add_argument("--root", required=True)
    s.add_argument("--repo", required=True)
    s = sub.add_parser("audit", help="show or verify a repository's audit log")
    s.add_argument("--root", required=True)
    s.add_argument("--repo", required=True)
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--verify", action="store_true")
    a = p.parse_args(argv)
    if a.command == "gen-certs":
        from .tools.certs import make_dev_pki

        _print_json(make_dev_pki(a.dir))
        return 0
    if a.command == "hash-token":
        print(hash_token(a.token))
        return 0
    dep = Deployment(a.root)
    try:
        if a.command == "init":
            print(f"deployment at {dep.root}")
        elif a.command == "create-repo":
            dep.create_repo(a.name, {"read": a.read, "write": a.write, "admins": a.admin})
            print(f"created {a.name}")
        elif a.command == "repos":
            for n in dep.names():
                print(n)
        elif a.command == "snapshot":
            repo = dep.repo(a.repo)
            _print_json(create_snapshot(repo, a.rev, os.path.join(a.out, a.repo)))
        elif a.command == "derive":
            repo = dep.repo(a.repo)
            cs = repo.resolve(a.rev)
            n = repo.derived.backfill(a.type, cs)
            repo.audit.append("derive", f"scion-admin:{getpass.getuser()}", a.type, {"cs": cs, "computed": n})
            print(f"{n} values computed")
        elif a.command == "set-ref":
            repo = dep.repo(a.repo)
            old = a.old if a.old is not None else repo.get_ref(a.ref)
            new = None if a.to == "-" else repo.resolve(a.to)
            repo.audit.append("admin.set_ref", a.as_user, a.ref, {"old": old, "new": new, "os_user": getpass.getuser()})
            if not repo.update_ref(a.ref, old, new, user=a.as_user):  # protections apply to a.as_user (D-03)
                print(f"{a.ref} was not {old}: nothing changed", file=sys.stderr)
                return 1
            print(f"{a.ref}: {(old or '-')[:12]} -> {(new or '-')[:12]}")
        elif a.command == "reindex-acl":
            repo = dep.repo(a.repo)
            r = repo.reindex_acl()
            repo.audit.append("acl.reindex", f"scion-admin:{getpass.getuser()}", repo.name, r)
            _print_json(r)
        elif a.command == "audit":
            repo = dep.repo(a.repo)
            if a.verify:
                r = repo.audit.verify()
                _print_json(r)
                return 0 if r["ok"] else 1
            for e in reversed(repo.audit.entries(a.limit)):
                print(f"{e['seq']:>6} {e['actor'] or '-':<14} {e['action']:<16} {e['target']} "
                      f"{json.dumps(e['detail'], sort_keys=True)}")
    except (PermissionDenied, NotFound, ValueError) as e:
        print(f"scion-admin: {e}", file=sys.stderr)
        return 1
    finally:
        dep.close()
    return 0


PROGRAMS = {"scn": scn_main, "scion-server": server_main, "scion-cache": cache_main, "scion-daemon": daemon_main,
            "scion-admin": admin_main}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in PROGRAMS:
        print("usage: python -m scion {" + ",".join(PROGRAMS) + "} ...", file=sys.stderr)
        return 2
    return PROGRAMS[argv[0]](argv[1:])

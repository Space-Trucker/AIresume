"""Command-line entry points: scn, scion-server, scion-cache, scion-daemon, scion-admin.

Run them as ``python -m scion <tool> ...`` (e.g. ``python -m scion scn status``) or through the
console scripts installed by ``pip install -e .``.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import signal
import sys
import threading

from .rpc import RemoteError

ENV_SERVER, ENV_OBJECTS, ENV_USER, ENV_TOKEN = "SCION_SERVER", "SCION_OBJECTS", "SCION_USER", "SCION_TOKEN"


def _die(msg: str, code: int = 1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def _fmt_time(ts: int) -> str:
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def _serve(server, label: str) -> None:
    print(f"{label} listening on {server.url}", flush=True)
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    server.start()
    stop.wait()
    server.stop()


# =============================================================================================
# scn
# =============================================================================================
def _wc():
    from .client import WorkingCopy
    return WorkingCopy.find(os.getcwd())


def _api(args):
    """A ServerApi from the working copy if we are in one, otherwise from flags/env."""
    from .client import ClientError, ServerApi
    try:
        wc = _wc()
        return wc.api
    except ClientError:
        server = getattr(args, "server", None) or os.environ.get(ENV_SERVER)
        if not server:
            _die(f"not in a working copy; pass --server or set {ENV_SERVER}")
        return ServerApi(server, getattr(args, "user", None) or os.environ.get(ENV_USER),
                         os.environ.get(ENV_TOKEN))


def cmd_clone(a):
    from .client import WorkingCopy
    server = a.server or os.environ.get(ENV_SERVER)
    if not server:
        _die("--server is required")
    mode = "virtual" if a.virtual else ("sparse" if a.sparse else "full")
    wc = WorkingCopy.clone(a.dest, server, a.objects or os.environ.get(ENV_OBJECTS), a.rev, mode,
                           a.sparse.split(",") if a.sparse else None, a.user or os.environ.get(ENV_USER),
                           os.environ.get(ENV_TOKEN), int(a.cache_mb) * 1024 ** 2)
    f = wc.fetcher.counters
    print(f"checked out {wc.base[:12]} into {wc.root} ({mode}); objects: {f['fetched']} fetched, "
          f"{f['local_hits']} from local cache, {f['requests']} requests")


def cmd_status(a):
    st = _wc().status(use_fsmonitor=not a.no_fsmonitor)
    if a.json:
        return _print(st.to_dict())
    for code, lst in (("M", st.modified), ("A", st.added), ("R", st.removed), ("?", st.untracked)):
        for p in lst:
            print(f"{code} {p}")


def cmd_add(a):
    for p in _wc().add(a.paths):
        print(f"added {p}")


def cmd_rm(a):
    _wc().remove(a.paths, keep=a.keep)


def cmd_restore(a):
    _wc().revert_local(a.paths)


def cmd_diff(a):
    if a.rev:
        api = _api(a)
        revs = a.rev
        r = api.diff(a=revs[0] if len(revs) == 2 else None, b=revs[-1], paths=a.paths or None, text=True,
                     merge_base=a.merge_base)
        sys.stdout.write(r["text"])
    else:
        sys.stdout.write(_wc().diff_local(a.paths or None))


def cmd_commit(a):
    wc = _wc()
    cs = wc.commit(a.message, a.paths or None, addremove=a.addremove)
    print(f"created changeset {cs[:12]} (on the server; nothing to push)")


def cmd_log(a):
    api = _api(a)
    rev = _default_rev(a)
    entries = api.log(rev=rev, limit=a.limit, path=a.path, first_parent=not a.all)
    for e in entries:
        if a.oneline:
            print(f"{e['id'][:12]} {e['summary']}")
        else:
            print(f"changeset {e['id']}\nauthor    {e['author']}\ndate      {_fmt_time(e['timestamp'])}\n"
                  f"parents   {' '.join(p[:12] for p in e['parents'])}\n\n    {e['summary']}\n")


def _default_rev(a) -> str:
    """Inside a working copy, commands default to the checked-out changeset."""
    return a.rev or (_wc().base if _in_wc() else "main")


def _in_wc() -> bool:
    from .client import ClientError
    try:
        _wc()
        return True
    except ClientError:
        return False


def cmd_show(a):
    api = _api(a)
    cs = api.get_changeset(rev=a.rev)
    print(f"changeset {cs['id']}\nauthor    {cs['author']}\ndate      {_fmt_time(cs['timestamp'])}\n"
          f"parents   {' '.join(cs['parents'])}\ngeneration {cs['generation']}\n\n{cs['message']}\n")
    for c in cs["changes"]:
        extra = f"  (from {cs['copies'][c['path']]['from']})" if c["path"] in cs["copies"] else ""
        print(f"  {c['op']} {c['path']}{extra}")
    if a.patch:
        sys.stdout.write(api.diff(b=cs["id"], text=True)["text"])


def cmd_blame(a):
    api = _api(a)
    rev = _default_rev(a)
    r = api.blame(rev=rev, path=a.path)
    if r["binary"]:
        return print("binary file")
    for line in r["lines"]:
        info = r["changesets"][line["cs"]]
        print(f"{line['cs'][:10]} {info['author'][:18]:<18} {line['line']:>5}: {line['text']}", end="")
    print()


def cmd_history(a):
    api = _api(a)
    rev = _default_rev(a)
    for h in api.file_history(rev=rev, path=a.path, limit=a.limit):
        cs = api.get_changeset(rev=h["cs"])
        print(f"{h['cs'][:12]} {_fmt_time(cs['timestamp'])} {cs['author'][:24]:<24} {h['path']}  "
              f"{cs['message'].splitlines()[0] if cs['message'] else ''}")


def cmd_cat(a):
    if a.rev or not _in_wc():
        api = _api(a)
        r = api.read_file(rev=a.rev or "main", path=a.path)
        sys.stdout.buffer.write(base64.b64decode(r["content_b64"]))
    else:
        sys.stdout.buffer.write(_wc().read(a.path))


def cmd_ls(a):
    if _in_wc() and not a.rev:
        for e in _wc().listdir(a.path):
            print(f"{e['kind']} {e['name']}")
    else:
        for e in _api(a).list_dir(rev=a.rev or "main", path=a.path):
            print(f"{e['kind']} {e['name']}")


def cmd_materialize(a):
    print(f"materialized {_wc().materialize(a.paths)} file(s)")


def cmd_update(a):
    r = _wc().update(a.rev, clean=a.clean)
    print(f"now at {r['base'][:12]} ({r['changed']} file(s) changed)")


def cmd_rebase(a):
    r = _wc().rebase(a.onto)
    print(f"rebased {len(r['rebased'])} changeset(s); now at {r['head'][:12]}")


def cmd_stack(a):
    for cs in _wc().stack(a.onto):
        print(cs[:12])


def cmd_sparse(a):
    wc = _wc()
    if a.action == "show":
        print("\n".join(wc.profile.prefixes) or "(full checkout)")
    elif a.action == "add":
        print(f"materialized {wc.sparse_add(a.dirs)} file(s)")
    elif a.action == "remove":
        print(f"removed {wc.sparse_remove(a.dirs)} file(s)")


def cmd_search(a):
    api = _api(a)
    r = api.search_paths(rev=_default_rev(a), query=a.query, limit=a.limit)
    print("\n".join(r["paths"]))


def cmd_grep(a):
    api = _api(a)
    r = api.grep(rev=_default_rev(a), pattern=a.pattern, path=a.path or "", limit=a.limit,
                 ignore_case=a.ignore_case, regex=not a.fixed)
    for m in r["matches"]:
        print(f"{m['path']}:{m['line']}: {m['text']}")
    if r["truncated"]:
        print("(results truncated)", file=sys.stderr)


def cmd_merge_base(a):
    print(_api(a).merge_base(a=a.a, b=a.b)["base"])


def cmd_watch(a):
    from . import fsmonitor
    wc = _wc()
    if a.action == "start":
        print(f"fsmonitor running (pid {fsmonitor.start(wc.root)})")
    elif a.action == "stop":
        print("stopped" if fsmonitor.stop(wc.root) else "not running")
    else:
        print("running" if fsmonitor.is_running(wc.root) else "not running")


def cmd_review(a):
    api = _api(a)
    act = a.action
    if act == "create":
        head = a.head or _wc().base
        cr = api.antique__create(title=a.title, head=head, description=a.description or "", target=a.target)
    elif act == "update":
        cr = api.antique__update(id=a.id, head=a.head or _wc().base)
    elif act == "list":
        for cr in api.antique__list(state=a.state):
            print(f"#{cr['id']:<5} {cr['state']:<9} {cr['author']:<12} {cr['title']}")
        return
    elif act == "show":
        cr = api.antique__get(id=a.id)
    elif act == "approve":
        cr = api.antique__approve(id=a.id)
    elif act == "comment":
        cr = api.antique__comment(id=a.id, body=a.body, path=a.path, line=a.line)
    elif act == "land":
        try:
            cr = api.antique__land(id=a.id, force=a.force)
        except RemoteError as e:
            if e.status == 409:
                _print(e.data)
                _die("conflicts: rebase onto the target, resolve, and upload a new revision", 2)
            raise
        print(f"landed #{cr['id']} as {cr['landed_cs'][:12]}")
        return
    elif act == "abandon":
        cr = api.antique__abandon(id=a.id)
    elif act == "landing":
        return _print(api.antique__find_landing(cs=a.cs))
    else:
        _die(f"unknown action {act}")
    _print(cr)


def cmd_revert(a):
    api = _api(a)
    if a.land:
        from .tools.revert import revert_and_land
        print(revert_and_land(api, a.cs, a.ref))
    else:
        print(api.revert(cs=a.cs, onto=a.onto or "main"))


def cmd_bisect(a):
    from .tools.bisect import bisect, command_predicate, file_matches
    api = _api(a)
    if a.file:
        path, _, pattern = a.file.partition(":")
        pred = file_matches(api, path, pattern, good_if_present=not a.bad_if_present)
    elif a.cmd:
        pred = command_predicate(_wc(), a.cmd)
    else:
        _die("pass --file PATH:REGEX (API-only) or --cmd COMMAND")
    _print(bisect(api, a.good, a.bad, pred, log=lambda m: print(m, file=sys.stderr)))


def cmd_api(a):
    """Call any RPC directly: scn api blame rev=main path=README.md"""
    from .client import ServerApi
    api = _api(a)
    if a.method == "commit":
        # Checkout-less write: scn api commit parent=main message=... path=@localfile ...
        params = dict(kv.split("=", 1) for kv in a.params)
        files = []
        for spec in a.files or []:
            path, _, src = spec.partition("=")
            if src == "-delete":
                files.append({"path": path, "delete": True})
            else:
                with open(src, "rb") as f:
                    files.append({"path": path, "content_b64": base64.b64encode(f.read()).decode()})
        ref = params.get("update_ref")
        update = None
        if ref:
            update = {"name": ref, "old": api.get_ref(name=ref)}
        return _print(api.create_changeset(parents=[params.get("parent", "main")], files=files,
                                           message=params.get("message", ""), update_ref=update))
    params = {}
    for kv in a.params:
        k, _, v = kv.partition("=")
        try:
            params[k] = json.loads(v)
        except json.JSONDecodeError:
            params[k] = v
    assert isinstance(api, ServerApi)
    _print(api.call(a.method, **params))


def scn_main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="scn", description="Scion client")
    p.add_argument("--server", help=f"server URL (default ${ENV_SERVER}) when not in a working copy")
    p.add_argument("--user", help=f"identity (default ${ENV_USER})")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("clone", help="check out a revision (full, --sparse or --virtual)")
    s.add_argument("dest")
    s.add_argument("--objects", help="object endpoint: unix:/path/to/daemon.sock or a URL")
    s.add_argument("--rev", default="main")
    s.add_argument("--sparse", help="comma-separated directories")
    s.add_argument("--virtual", action="store_true", help="materialize files on demand")
    s.add_argument("--cache-mb", default=2048, help="bounded local object cache size")
    s.set_defaults(fn=cmd_clone)

    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")
    s.add_argument("--no-fsmonitor", action="store_true")
    s.set_defaults(fn=cmd_status)

    for name, fn, help_ in (("add", cmd_add, "track new files"), ("restore", cmd_restore, "discard local changes")):
        s = sub.add_parser(name, help=help_)
        s.add_argument("paths", nargs="+")
        s.set_defaults(fn=fn)
    s = sub.add_parser("rm")
    s.add_argument("paths", nargs="+")
    s.add_argument("--keep", action="store_true")
    s.set_defaults(fn=cmd_rm)

    s = sub.add_parser("diff", help="local changes, or between changesets with -r A -r B (server-side)")
    s.add_argument("-r", "--rev", action="append")
    s.add_argument("--merge-base", action="store_true", help="diff against the merge base with A (default main)")
    s.add_argument("paths", nargs="*")
    s.set_defaults(fn=cmd_diff)

    s = sub.add_parser("commit", help="create a changeset on the server")
    s.add_argument("-m", "--message", required=True)
    s.add_argument("-A", "--addremove", action="store_true", help="include untracked files")
    s.add_argument("paths", nargs="*")
    s.set_defaults(fn=cmd_commit)

    s = sub.add_parser("log")
    s.add_argument("path", nargs="?")
    s.add_argument("-r", "--rev")
    s.add_argument("-n", "--limit", type=int, default=20)
    s.add_argument("--all", action="store_true", help="all ancestors, not just the first-parent chain")
    s.add_argument("--oneline", action="store_true")
    s.set_defaults(fn=cmd_log)

    s = sub.add_parser("show")
    s.add_argument("rev")
    s.add_argument("-p", "--patch", action="store_true")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("blame")
    s.add_argument("path")
    s.add_argument("-r", "--rev")
    s.set_defaults(fn=cmd_blame)

    s = sub.add_parser("history", help="changesets that touched a file or directory")
    s.add_argument("path")
    s.add_argument("-r", "--rev")
    s.add_argument("-n", "--limit", type=int, default=50)
    s.set_defaults(fn=cmd_history)

    s = sub.add_parser("cat")
    s.add_argument("path")
    s.add_argument("-r", "--rev")
    s.set_defaults(fn=cmd_cat)

    s = sub.add_parser("ls")
    s.add_argument("path", nargs="?", default="")
    s.add_argument("-r", "--rev")
    s.set_defaults(fn=cmd_ls)

    s = sub.add_parser("materialize", help="virtual checkouts: bring files onto disk")
    s.add_argument("paths", nargs="+")
    s.set_defaults(fn=cmd_materialize)

    s = sub.add_parser("update", help="move the working copy to another revision")
    s.add_argument("rev")
    s.add_argument("--clean", action="store_true", help="discard conflicting local changes")
    s.set_defaults(fn=cmd_update)

    s = sub.add_parser("rebase", help="rebase your stack on the server")
    s.add_argument("--onto")
    s.set_defaults(fn=cmd_rebase)

    s = sub.add_parser("stack", help="list changesets not yet in the tracked ref")
    s.add_argument("--onto")
    s.set_defaults(fn=cmd_stack)

    s = sub.add_parser("sparse")
    s.add_argument("action", choices=["show", "add", "remove"])
    s.add_argument("dirs", nargs="*")
    s.set_defaults(fn=cmd_sparse)

    s = sub.add_parser("search", help="path search")
    s.add_argument("query")
    s.add_argument("-r", "--rev")
    s.add_argument("-n", "--limit", type=int, default=100)
    s.set_defaults(fn=cmd_search)

    s = sub.add_parser("grep", help="server-side content search")
    s.add_argument("pattern")
    s.add_argument("path", nargs="?")
    s.add_argument("-r", "--rev")
    s.add_argument("-i", "--ignore-case", action="store_true")
    s.add_argument("-F", "--fixed", action="store_true")
    s.add_argument("-n", "--limit", type=int, default=200)
    s.set_defaults(fn=cmd_grep)

    s = sub.add_parser("merge-base")
    s.add_argument("a")
    s.add_argument("b")
    s.set_defaults(fn=cmd_merge_base)

    s = sub.add_parser("watch", help="filesystem monitor")
    s.add_argument("action", choices=["start", "stop", "status"])
    s.set_defaults(fn=cmd_watch)

    s = sub.add_parser("review", help="Antique code review")
    s.add_argument("action", choices=["create", "update", "list", "show", "approve", "comment", "land",
                                      "abandon", "landing"])
    s.add_argument("id", nargs="?", type=int)
    s.add_argument("--title")
    s.add_argument("--description")
    s.add_argument("--head")
    s.add_argument("--target", default="main")
    s.add_argument("--state")
    s.add_argument("--body")
    s.add_argument("--path")
    s.add_argument("--line", type=int)
    s.add_argument("--cs")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_review)

    s = sub.add_parser("revert", help="server-side revert")
    s.add_argument("cs")
    s.add_argument("--onto")
    s.add_argument("--land", action="store_true", help="land on --ref with compare-and-swap")
    s.add_argument("--ref", default="main")
    s.set_defaults(fn=cmd_revert)

    s = sub.add_parser("bisect", help="automated bisect over the API")
    s.add_argument("--good", required=True)
    s.add_argument("--bad", required=True)
    s.add_argument("--file", help="PATH:REGEX, checked with read_file (no checkout)")
    s.add_argument("--bad-if-present", action="store_true")
    s.add_argument("--cmd", help="command run in this working copy at each probe")
    s.set_defaults(fn=cmd_bisect)

    s = sub.add_parser("api", help="call any RPC: scn api blame rev=main path=README.md")
    s.add_argument("method")
    s.add_argument("params", nargs="*")
    s.add_argument("--file", dest="files", action="append", help="for 'commit': PATH=LOCALFILE or PATH=-delete")
    s.set_defaults(fn=cmd_api)

    a = p.parse_args(argv)
    try:
        a.fn(a)
    except RemoteError as e:
        _die(f"server: {e}")
    except Exception as e:
        from .client import ClientError
        if isinstance(e, ClientError):
            _die(str(e))
        raise


# =============================================================================================
# Services
# =============================================================================================
def server_main(argv=None) -> None:
    from .rpc import RpcServer
    from .server import make_server
    p = argparse.ArgumentParser(prog="scion-server")
    p.add_argument("--repo", required=True, help="repository directory (blob storage + metadata DB)")
    p.add_argument("--listen", default="127.0.0.1:7070")
    p.add_argument("--policy", help="IAM / review / rate-limit policy (JSON)")
    p.add_argument("--allow-direct-objects", action="store_true",
                   help="development: let clients fetch objects without a cache tier")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    svc = make_server(a.repo, a.policy, a.allow_direct_objects, a.verbose)
    _serve(RpcServer(svc, a.listen), "scion-server")


def cache_main(argv=None) -> None:
    from .iam import Policy
    from .rpc import RpcServer
    from .tiers import make_cache_service
    p = argparse.ArgumentParser(prog="scion-cache")
    p.add_argument("--listen", default="127.0.0.1:7080")
    p.add_argument("--upstream", action="append", required=True, help="scion-server URL (repeatable)")
    p.add_argument("--max-mb", type=int, default=4096)
    p.add_argument("--policy", help="policy file (for tokens and rate limits)")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    svc = make_cache_service(a.upstream, a.max_mb * 1024 ** 2, os.environ.get(ENV_TOKEN),
                             Policy.load(a.policy), verbose=a.verbose)
    _serve(RpcServer(svc, a.listen), "scion-cache")


def daemon_main(argv=None) -> None:
    from .iam import Policy
    from .rpc import RpcServer
    from .tiers import DaemonService
    p = argparse.ArgumentParser(prog="scion-daemon")
    p.add_argument("--socket", default="/tmp/scion/daemon.sock")
    p.add_argument("--upstream", action="append", required=True, help="scion-cache URL (repeatable)")
    p.add_argument("--store", default=os.path.expanduser("~/.cache/scion-daemon"))
    p.add_argument("--max-mb", type=int, default=20480)
    p.add_argument("--snapshot-dir", help="blob-storage directory holding snapshots")
    p.add_argument("--refresh-seconds", type=float, default=300)
    p.add_argument("--policy", help="policy file (for tokens and rate limits)")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    svc = DaemonService(a.store, a.upstream, a.max_mb * 1024 ** 2, a.snapshot_dir, a.refresh_seconds,
                        os.environ.get(ENV_TOKEN), Policy.load(a.policy), verbose=a.verbose)
    _serve(RpcServer(svc, f"unix:{a.socket}"), "scion-daemon")


def admin_main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="scion-admin")
    sub = p.add_subparsers(dest="cmd", required=True)

    def repo_arg(s):
        s.add_argument("--repo", required=True)
        s.add_argument("--policy")

    s = sub.add_parser("init", help="create an empty repository")
    repo_arg(s)
    s = sub.add_parser("info")
    repo_arg(s)
    s = sub.add_parser("ingest", help="import (or incrementally sync) a git repository")
    repo_arg(s)
    s.add_argument("--git", required=True, help="path to a git repository")
    s.add_argument("--rev", default="HEAD")
    s.add_argument("--ref", default="main")
    s.add_argument("--limit", type=int)
    s.add_argument("--verify", action="store_true")
    s = sub.add_parser("snapshot", help="write a daemon snapshot of a revision")
    repo_arg(s)
    s.add_argument("--rev", default="main")
    s.add_argument("--out", required=True)
    s = sub.add_parser("derive", help="backfill a deferred derived-data type")
    repo_arg(s)
    s.add_argument("--type", required=True)
    s.add_argument("--rev", default="main")
    s = sub.add_parser("reindex-acl", help="re-record directory ACLs after a policy change")
    repo_arg(s)
    s.add_argument("--rev", default="main")
    s = sub.add_parser("set-ref")
    repo_arg(s)
    s.add_argument("name")
    s.add_argument("rev")
    s = sub.add_parser("postmerge-worker", help="run post-merge tests for landed changes")
    s.add_argument("--server", required=True)
    s.add_argument("--objects")
    s.add_argument("--workdir", required=True)
    s.add_argument("--cmd", dest="test_cmd", required=True, help="test command; exit status 0 = pass")
    s.add_argument("--sparse")
    s.add_argument("--once", action="store_true")
    s.add_argument("--auto-revert", action="store_true")
    s = sub.add_parser("deploy-gate", help="newest changeset that passed post-merge testing")
    s.add_argument("--server", required=True)
    s.add_argument("--ref", default="main")
    s = sub.add_parser("superfan", help="watch one component's telemetry")
    s.add_argument("component", choices=["server", "cache", "daemon"])
    s.add_argument("url")
    s.add_argument("--interval", type=float, default=10)
    s.add_argument("--webhook")
    s.add_argument("--iterations", type=int)
    sub.add_parser("bench", help="run local benchmarks")
    a = p.parse_args(argv)

    if a.cmd in ("init", "info", "ingest", "snapshot", "derive", "reindex-acl", "set-ref"):
        from .iam import Policy
        from .repo import Repository
        repo = Repository(a.repo, Policy.load(a.policy))
        if a.cmd == "init":
            print(f"initialized empty Scion repository in {os.path.abspath(a.repo)}")
        elif a.cmd == "info":
            _print(repo.info())
        elif a.cmd == "ingest":
            from .ingest import GitIngester
            ing = GitIngester(repo, a.git, verbose=True)
            _print(ing.ingest(a.rev, a.ref, a.limit))
            if a.verify:
                _print(ing.verify(a.rev))
        elif a.cmd == "snapshot":
            from .snapshot import create_snapshot
            print(create_snapshot(repo, a.rev, a.out))
        elif a.cmd == "derive":
            n = repo.derived.backfill(a.type, repo.resolve(a.rev))
            print(f"derived {a.type} for {n} changeset(s)")
        elif a.cmd == "reindex-acl":
            print(f"indexed {repo.reindex_acl(a.rev)} objects")
        elif a.cmd == "set-ref":
            old = repo.get_ref(a.name)
            ok = repo.update_ref(a.name, old, a.rev)
            print("ok" if ok else "ref moved concurrently; retry")
    elif a.cmd == "postmerge-worker":
        from .postmerge import run_worker
        _print(run_worker(a.server, a.workdir, a.test_cmd, objects=a.objects,
                          sparse=a.sparse.split(",") if a.sparse else None, once=a.once,
                          auto_revert=a.auto_revert))
    elif a.cmd == "deploy-gate":
        from .client import ServerApi
        from .postmerge import deploy_gate
        _print(deploy_gate(ServerApi(a.server, os.environ.get(ENV_USER) or "deployer"), a.ref))
    elif a.cmd == "superfan":
        from .superfan import DEFAULT_RULES, Superfan
        Superfan(a.component, a.url, DEFAULT_RULES.get(a.component), webhook=a.webhook).run(a.interval, a.iterations)
    elif a.cmd == "bench":
        from .tools.bench import main as bench
        bench()


TOOLS = {"scn": scn_main, "scion-server": server_main, "scion-cache": cache_main,
         "scion-daemon": daemon_main, "scion-admin": admin_main}


def main(argv=None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in TOOLS:
        _die(f"usage: python -m scion {{{','.join(TOOLS)}}} ...")
    TOOLS[argv[0]](argv[1:])

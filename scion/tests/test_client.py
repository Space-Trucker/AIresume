"""T-CL-01…13: the scn client and CLI against a hermetic cluster (WP-B2.4)."""
import base64
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion import cli, client as client_mod, fsmonitor
from scion.client import ClientError, WorkingCopy
from scion.rpc import RemoteError


def b64(data) -> str:
    return base64.b64encode(data if isinstance(data, bytes) else data.encode()).decode()


def write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as f:
        f.write(text)


def read(path):
    with open(path) as f:
        return f.read()


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-client-")
        self.c = Cluster(self.tmp)
        self.api = self.c.client("alice")
        self.v1 = self.commit_api([], {f"src/d{i}/f{j}.txt": f"line {i}.{j}\n" for i in range(3) for j in range(3)},
                                  "v1", ref_old=None)
        self.wcs = []

    def tearDown(self):
        for wc in self.wcs:
            fsmonitor.stop(wc.root)
            wc.close()
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit_api(self, parents, files, message, ref="main", ref_old="__parent__", user="alice"):
        entries = [{"path": p, "delete": True} if c is None else {"path": p, "content_b64": b64(c)}
                   for p, c in files.items()]
        params = {"repo": REPO, "parents": parents, "files": entries, "message": message}
        if ref:
            params["update_ref"] = {"name": ref, "old": parents[0] if ref_old == "__parent__" else ref_old}
        r = self.c.client(user).call("create_changeset", **params)
        if ref:
            self.assertTrue(r["ref_updated"])
        return r["id"]

    def clone(self, name, **kw):
        wc = WorkingCopy.clone(os.path.join(self.tmp, name), self.c.server_urls[0], REPO,
                               objects=self.c.daemon_urls[0], user=kw.pop("user", "alice"), **kw)
        self.wcs.append(wc)
        return wc

    def p(self, wc, path):
        return os.path.join(wc.root, path)


class TestWorkingCopy(ClientTest):
    def test_T_CL_01_edit_status_add_commit_nothing_to_push(self):
        wc = self.clone("wc")
        write(self.p(wc, "src/d0/f0.txt"), "changed\n")
        write(self.p(wc, "src/new.txt"), "brand new\n")
        os.unlink(self.p(wc, "src/d1/f1.txt"))
        st = wc.status()
        self.assertEqual((st.modified, st.removed, st.untracked), (["src/d0/f0.txt"], ["src/d1/f1.txt"], ["src/new.txt"]))
        wc.add(["src/new.txt"])
        self.assertEqual(wc.status().added, ["src/new.txt"])
        server_before = self.c.repo().meta.count_changesets()
        cs = wc.commit("edit")
        self.assertEqual(wc.base, cs)
        self.assertFalse(wc.status().dirty)
        # the changeset is on the server at once, visible to anyone; no ref moved (FR-CS-05)
        info = self.c.client("bob").call("get_changeset", repo=REPO, rev=cs)
        self.assertEqual(info["parents"], [self.v1])
        self.assertEqual({c["path"]: c["op"] for c in info["changes"]},
                         {"src/d0/f0.txt": "M", "src/new.txt": "A", "src/d1/f1.txt": "D"})
        self.assertEqual(self.c.repo().meta.count_changesets(), server_before + 1)
        self.assertEqual(self.api.call("get_ref", repo=REPO, name="main"), self.v1)
        # there is no push command at all
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            cli._scn_parser().parse_args(["push"])
        # FR-WR-06: uploads skip content the server already has
        write(self.p(wc, "src/copy.txt"), "brand new\n")
        wc.add(["src/copy.txt"])
        with mock.patch.object(wc.api, "put_objects", wraps=wc.api.put_objects) as put:
            wc.commit("same bytes again")
        put.assert_not_called()

    def test_T_CL_02_kinds_round_trip(self):
        wc = self.clone("wc")
        write(self.p(wc, "bin/run.sh"), "#!/bin/sh\necho hi\n")
        os.chmod(self.p(wc, "bin/run.sh"), 0o755)
        os.symlink("../src/d0/f0.txt", self.p(wc, "bin/link"))
        wc.add(["bin"])
        cs = wc.commit("kinds")
        changes = {c["path"]: c["kind"] for c in self.api.call("get_changeset", repo=REPO, rev=cs)["changes"]}
        self.assertEqual(changes, {"bin/run.sh": "x", "bin/link": "l"})
        self.api.call("update_ref", repo=REPO, name="main", old=self.v1, new=cs)
        other = self.clone("other")
        self.assertTrue(os.access(self.p(other, "bin/run.sh"), os.X_OK))
        self.assertTrue(os.path.islink(self.p(other, "bin/link")))
        self.assertEqual(os.readlink(self.p(other, "bin/link")), "../src/d0/f0.txt")
        self.assertFalse(os.access(self.p(other, "src/d0/f0.txt"), os.X_OK))
        self.assertFalse(other.status().dirty)
        os.chmod(self.p(other, "src/d0/f0.txt"), 0o755)  # a mode change alone is a modification
        self.assertEqual(other.status().modified, ["src/d0/f0.txt"])

    def test_T_CL_03_update_fetches_only_the_diff_and_protects_local_changes(self):
        wc = self.clone("wc")
        v2 = self.commit_api([self.v1], {"src/d2/f2.txt": "upstream edit\n", "src/d0/f1.txt": None}, "v2")
        write(self.p(wc, "src/d1/f0.txt"), "my unrelated edit\n")
        before = wc.fetcher.counters["fetched"]
        r = wc.update("main")
        self.assertEqual((r["base"], r["written"], r["deleted"]), (v2, 1, 1))
        self.assertEqual(wc.fetcher.counters["fetched"] - before, 1, "only the changed blob is fetched")
        self.assertEqual(read(self.p(wc, "src/d2/f2.txt")), "upstream edit\n")
        self.assertFalse(os.path.exists(self.p(wc, "src/d0/f1.txt")))
        self.assertEqual(read(self.p(wc, "src/d1/f0.txt")), "my unrelated edit\n")
        self.assertEqual(wc.status().modified, ["src/d1/f0.txt"])
        # a local edit to a path the update would change is protected
        self.commit_api([v2], {"src/d1/f0.txt": "their edit\n"}, "v3")
        with self.assertRaises(ClientError):
            wc.update("main")
        self.assertEqual(read(self.p(wc, "src/d1/f0.txt")), "my unrelated edit\n")
        self.assertEqual(wc.base, v2)
        wc.update("main", clean=True)
        self.assertEqual(read(self.p(wc, "src/d1/f0.txt")), "their edit\n")
        self.assertFalse(wc.status().dirty)
        # an untracked file where the update creates one is protected too
        self.commit_api([wc.base], {"src/fresh.txt": "theirs\n"}, "v4")
        write(self.p(wc, "src/fresh.txt"), "mine\n")
        with self.assertRaises(ClientError):
            wc.update("main")
        # file <-> directory swaps
        os.unlink(self.p(wc, "src/fresh.txt"))
        base = self.api.call("resolve", repo=REPO, rev="main")
        self.commit_api([base], {"src/d0": "now a file\n", **{f"src/d0/f{j}.txt": None for j in (0, 2)}}, "swap")
        wc.update("main")
        self.assertEqual(read(self.p(wc, "src/d0")), "now a file\n")
        self.assertFalse(wc.status().dirty)

    def test_T_CL_04_server_side_rebase(self):
        wc = self.clone("wc")
        write(self.p(wc, "src/d0/f0.txt"), "mine\n")
        mine = wc.commit("my change")
        theirs = self.commit_api([self.v1], {"src/d2/f2.txt": "theirs\n"}, "their change")
        r = wc.rebase()
        self.assertEqual(list(r["rebased"]), [mine])
        head = self.api.call("get_changeset", repo=REPO, rev=r["head"])
        self.assertEqual(head["parents"], [theirs])
        self.assertEqual(wc.base, r["head"])
        self.assertEqual(read(self.p(wc, "src/d2/f2.txt")), "theirs\n")
        self.assertEqual(read(self.p(wc, "src/d0/f0.txt")), "mine\n")
        self.assertEqual(wc.stack(), [r["head"]])
        # a conflicting rebase changes nothing
        write(self.p(wc, "src/d2/f2.txt"), "conflicting\n")
        wc.commit("conflict")
        self.commit_api([theirs], {"src/d2/f2.txt": "upstream again\n"}, "upstream")
        base = wc.base
        with self.assertRaises(RemoteError) as e:
            wc.rebase()
        self.assertEqual(e.exception.status, 409)
        self.assertEqual(e.exception.data["conflicts"][0]["path"], "src/d2/f2.txt")
        self.assertEqual(wc.base, base)

    def test_T_CL_05_local_diff_restore_remove(self):
        wc = self.clone("wc")
        write(self.p(wc, "src/d0/f0.txt"), "line 0.0\nadded\n")
        d = wc.diff_local()
        self.assertIn("--- a/src/d0/f0.txt", d)
        self.assertIn("+added", d)
        wc.restore(["src/d0/f0.txt"])
        self.assertEqual(read(self.p(wc, "src/d0/f0.txt")), "line 0.0\n")
        self.assertFalse(wc.status().dirty)
        wc.remove(["src/d1/f1.txt"])
        self.assertFalse(os.path.exists(self.p(wc, "src/d1/f1.txt")))
        self.assertEqual(wc.status().removed, ["src/d1/f1.txt"])
        self.assertIn("+++ /dev/null", wc.diff_local(["src/d1"]))
        wc.restore(["src/d1/f1.txt"])
        self.assertFalse(wc.status().dirty)

    def test_T_CL_06_sparse_checkout(self):
        wc = self.clone("wc", mode="sparse", sparse=["src/d1"])
        self.assertEqual(os.listdir(self.p(wc, "src")), ["d1"])
        self.assertEqual(sorted(os.listdir(self.p(wc, "src/d1"))), ["f0.txt", "f1.txt", "f2.txt"])
        # FR-FP-02: trees level by level, then blobs; only the wanted subtrees
        self.assertEqual(wc.fetcher.log, [("tree:0", 1), ("tree:1", 1), ("tree:2", 1), ("blob", 3)])
        wc.sparse_add(["src/d2"])
        self.assertEqual(sorted(os.listdir(self.p(wc, "src"))), ["d1", "d2"])
        self.assertEqual(wc.sparse_remove(["src/d1"]), 3)
        self.assertEqual(os.listdir(self.p(wc, "src")), ["d2"])
        self.assertFalse(wc.status().dirty)
        # an update outside the profile fetches and writes nothing
        before = wc.fetcher.counters["fetched"]
        self.commit_api([self.v1], {"src/d0/f0.txt": "elsewhere\n"}, "outside")
        r = wc.update("main")
        self.assertEqual((r["written"], wc.fetcher.counters["fetched"] - before), (0, 0))
        self.assertFalse(os.path.exists(self.p(wc, "src/d0")))
        # FR-FP-04: nothing but the plain object request reached the object endpoint
        daemon_rpcs = {k for k in self.c.daemon_services[0].metrics.counters if k.startswith("rpc.")}
        self.assertEqual(daemon_rpcs, {"rpc.get_objects"})

    def test_T_CL_07_virtual_checkout(self):
        wc = self.clone("wc", mode="virtual")
        self.assertEqual(os.listdir(wc.root), [".scn"])
        self.assertEqual(wc.fetcher.counters["fetched"], 0)
        self.assertEqual(wc.read("src/d2/f1.txt"), b"line 2.1\n")  # FR-CL-10
        self.assertEqual(wc.fetcher.counters["fetched"], 4, "the root, src and src/d2 trees and one blob")
        self.assertEqual(sorted(os.listdir(wc.root)), [".scn", "src"])
        self.assertEqual(os.listdir(self.p(wc, "src/d2")), ["f1.txt"])
        self.assertEqual(wc.materialize(["src/d0"]), 3)
        self.assertFalse(wc.status().dirty)
        # writes without reading: compared with the tree entry, not reported as untracked
        write(self.p(wc, "src/d1/f0.txt"), "written blind\n")
        write(self.p(wc, "src/d1/f1.txt"), "line 1.1\n")
        st = wc.status()
        self.assertEqual((st.modified, st.untracked), (["src/d1/f0.txt"], []))
        cs = wc.commit("blind write")
        self.assertEqual([c["path"] for c in self.api.call("get_changeset", repo=REPO, rev=cs)["changes"]],
                         ["src/d1/f0.txt"])
        # update rewrites only what was materialized
        self.commit_api([self.v1], {"src/d2/f1.txt": "new 2.1\n", "src/d2/f0.txt": "new 2.0\n"}, "v2")
        wc.update("main", clean=True)
        self.assertEqual(read(self.p(wc, "src/d2/f1.txt")), "new 2.1\n")
        self.assertFalse(os.path.exists(self.p(wc, "src/d2/f0.txt")))
        self.assertEqual(wc.read("src/d2/f0.txt"), b"new 2.0\n")

    def test_T_CL_08_tiny_bounded_cache(self):
        wc = self.clone("wc", cache_bytes=600)
        self.assertLessEqual(wc.local.size_bytes, 600)
        self.assertGreater(wc.local.evictions, 0)
        self.assertEqual(read(self.p(wc, "src/d2/f2.txt")), "line 2.2\n")
        self.assertFalse(wc.status().dirty)
        write(self.p(wc, "src/d0/f0.txt"), "x\n")
        wc.restore(["src/d0/f0.txt"])  # needs an object that was evicted: fetched again
        self.assertEqual(read(self.p(wc, "src/d0/f0.txt")), "line 0.0\n")

    def test_T_CL_09_fsmonitor_journal_and_sync_cookie(self):
        if not fsmonitor.supported():
            self.skipTest("inotify is Linux only")
        wc = self.clone("wc")
        fsmonitor.start(wc.root)
        first = wc.status()  # the first query of a session scans everything once
        self.assertFalse(first.used_fsmonitor)
        quiet = wc.status()
        self.assertTrue(quiet.used_fsmonitor)
        self.assertEqual(quiet.examined, 0)
        write(self.p(wc, "src/d0/f0.txt"), "edited\n")  # no sleep: the sync cookie orders the query
        st = wc.status()
        self.assertTrue(st.used_fsmonitor)
        self.assertEqual(st.modified, ["src/d0/f0.txt"])
        self.assertLessEqual(st.examined, 2)
        shutil.rmtree(self.p(wc, "src/d1"))
        write(self.p(wc, "src/newdir/a.txt"), "a\n")
        st = wc.status()
        self.assertEqual(st.removed, ["src/d1/f0.txt", "src/d1/f1.txt", "src/d1/f2.txt"])
        self.assertEqual(st.untracked, ["src/newdir/a.txt"])
        self.assertEqual(st.modified, ["src/d0/f0.txt"])
        full = wc.status(use_fsmonitor=False)
        self.assertEqual((full.modified, full.removed, full.untracked), (st.modified, st.removed, st.untracked))
        self.assertGreater(full.examined, st.examined)
        self.assertTrue(fsmonitor.stop(wc.root))
        self.assertFalse(wc.status().used_fsmonitor)  # no watcher: a full scan

    def test_T_CL_10_checkout_less_write_and_merge_base_diff(self):
        r = self.api.call("create_changeset", repo=REPO, parents=[self.v1], message="feature",
                          files=[{"path": "src/feature.txt", "content_b64": b64("feature\n")}],
                          update_ref={"name": "feature", "old": None})
        self.assertTrue(r["ref_updated"])
        stale = self.api.call("create_changeset", repo=REPO, parents=[self.v1], message="late",
                              files=[{"path": "src/late.txt", "content_b64": b64("late\n")}],
                              update_ref={"name": "feature", "old": self.v1})
        self.assertFalse(stale["ref_updated"])  # the changeset exists; the ref did not move
        self.assertIsNotNone(self.api.call("get_changeset", repo=REPO, rev=stale["id"]))
        self.commit_api([self.v1], {"src/d0/f0.txt": "main moved\n"}, "main moves on")
        d = self.api.call("diff", repo=REPO, b="feature", a="main", merge_base=True)
        self.assertEqual([f["path"] for f in d["files"]], ["src/feature.txt"])
        plain = self.api.call("diff", repo=REPO, b="feature", a="main")
        self.assertEqual(sorted(f["path"] for f in plain["files"]), ["src/d0/f0.txt", "src/feature.txt"])

    def test_T_CL_12_adding_a_file_outside_the_sparse_profile(self):
        wc = self.clone("wc", mode="sparse", sparse=["src/d1"])
        write(self.p(wc, "src/d2/new.txt"), "outside\n")
        self.assertEqual(wc.status().untracked, [])  # outside the profile: not scanned
        self.assertEqual(wc.add(["src/d2/new.txt"]), ["src/d2/new.txt"])
        self.assertIn("src/d2/new.txt", wc.profile.prefixes)
        self.assertEqual(wc.status().added, ["src/d2/new.txt"])
        cs = wc.commit("add outside")
        self.assertEqual([c["path"] for c in self.api.call("get_changeset", repo=REPO, rev=cs)["changes"]],
                         ["src/d2/new.txt"])
        self.assertEqual(sorted(os.listdir(self.p(wc, "src/d2"))), ["new.txt"], "the rest of d2 stays out")
        self.assertFalse(wc.status().dirty)

    def test_T_CL_13_interrupted_clone_resumes(self):
        files = {f"big/d{i}/f{j}.txt": f"content {i} {j}\n" for i in range(4) for j in range(10)}
        self.commit_api([self.v1], files, "many files")
        real = client_mod.ObjectFetcher._remote
        calls = {"n": 0}

        def flaky(fetcher, ids, stage, allow_denied):
            if stage == "blob":
                calls["n"] += 1
                if calls["n"] == 3:
                    raise ConnectionError("network went away")
            return real(fetcher, ids, stage, allow_denied)

        dest = os.path.join(self.tmp, "wc")
        with mock.patch.object(client_mod, "FETCH_BATCH", 8), mock.patch.object(client_mod, "FETCH_PARALLEL", 1), \
                mock.patch.object(client_mod.ObjectFetcher, "_remote", flaky):
            with self.assertRaises(ConnectionError):
                WorkingCopy.clone(dest, self.c.server_urls[0], REPO, objects=self.c.daemon_urls[0], user="alice")
        partial = WorkingCopy(dest)
        written_before = partial.db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        cached_before = len(partial.local)
        partial.close()
        self.assertGreater(written_before, 0)
        unfinished = WorkingCopy(dest)
        with self.assertRaises(ClientError):
            unfinished.update("main")  # the working copy knows it is unfinished
        unfinished.close()
        with mock.patch.object(client_mod, "FETCH_BATCH", 8):
            wc = WorkingCopy.clone(dest, self.c.server_urls[0], REPO, objects=self.c.daemon_urls[0], user="alice")
        self.wcs.append(wc)
        # every object received before the interruption is reused: files already written are skipped,
        # and the cached objects still needed are local hits; only the rest is fetched
        n_trees, n_blobs = 10, 49
        self.assertEqual(wc.fetcher.counters["local_hits"], cached_before - written_before)
        self.assertEqual(wc.fetcher.counters["fetched"], n_trees + n_blobs - cached_before)
        total = wc.db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        self.assertEqual(total, 49)
        self.assertFalse(wc.status().dirty)
        self.assertEqual(wc.base, self.api.call("resolve", repo=REPO, rev="main"))


class TestCli(ClientTest):
    """T-CL-11: the CLI end to end; every query it makes is a public RPC (FR-QRY-10)."""

    def scn(self, *args, cwd=None):
        out = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        err = io.StringIO()
        argv = (["-C", cwd] if cwd else []) + [str(a) for a in args]
        with mock.patch.object(sys, "stdout", out), contextlib.redirect_stderr(err):
            code = cli.scn_main(argv)
        out.flush()
        text = out.buffer.getvalue().decode()
        return code, text, err.getvalue()

    def ok(self, *args, cwd=None):
        code, out, err = self.scn(*args, cwd=cwd)
        self.assertEqual(code, 0, f"scn {' '.join(map(str, args))} failed: {err}")
        return out

    def test_T_CL_11_cli_end_to_end(self):
        server = self.c.server_urls[0]
        dest = os.path.join(self.tmp, "wc")
        self.ok("--server", server, "--repo", REPO, "--user", "alice", "clone", dest, "--objects", self.c.daemon_urls[0])
        write(os.path.join(dest, "src/d0/f0.txt"), "line 0.0\ncli edit\n")
        write(os.path.join(dest, "src/cli.txt"), "new\n")
        self.assertEqual(self.ok("status", cwd=dest), "M src/d0/f0.txt\n? src/cli.txt\n")
        self.assertEqual(json.loads(self.ok("status", "--json", cwd=dest))["modified"], ["src/d0/f0.txt"])
        self.ok("add", "src/cli.txt", cwd=dest)
        self.assertIn("+cli edit", self.ok("diff", cwd=dest))
        out = self.ok("commit", "-m", "from the cli", cwd=dest)
        cs = out.split()[1]
        self.assertIn("nothing to push", out)
        self.assertIn("from the cli", self.ok("log", "-n", "1", cwd=dest))
        self.assertIn("src/cli.txt", self.ok("show", cwd=dest))
        self.assertIn("cli edit", self.ok("blame", "src/d0/f0.txt", cwd=dest))
        self.assertIn("from the cli", self.ok("history", "src/d0/f0.txt", cwd=dest))
        self.assertEqual(self.ok("cat", "src/d0/f0.txt", "-r", self.v1, cwd=dest), "line 0.0\n")
        self.assertIn("d src/d0/", self.ok("ls", "src", cwd=dest))
        self.assertEqual(self.ok("search", "cli", cwd=dest), "src/cli.txt\n")
        self.assertEqual(self.ok("merge-base", "main", cs, cwd=dest).strip(), self.v1)
        self.assertEqual(self.ok("is-ancestor", "main", cs, cwd=dest).strip(), "yes")
        self.assertEqual(self.scn("is-ancestor", cs, "main", cwd=dest)[0], 1)
        self.assertIn("main", self.ok("refs", cwd=dest))
        self.assertIn("by alice", self.ok("ref-log", "main", cwd=dest))
        self.assertEqual(json.loads(self.ok("whoami", cwd=dest))["user"], "alice")
        self.assertEqual(self.ok("repos", cwd=dest), f"{REPO}\n")
        self.assertIn("M src/d0/f0.txt", self.ok("diff", "-r", self.v1, "-r", cs, "--stat", cwd=dest))
        self.assertEqual(self.ok("stack", cwd=dest).split()[0], cs[:12])
        self.assertEqual(json.loads(self.ok("api", "fp_ancestor", f"rev={cs}", "n=1", cwd=dest)), self.v1)
        # writes without a checkout, from anywhere
        local = os.path.join(self.tmp, "payload.txt")
        write(local, "api write\n")
        r = json.loads(self.ok("--server", server, "--repo", REPO, "--user", "bob", "api", "commit",
                               "--parent", "main", "-m", "no checkout", "--file", f"docs/x.txt={local}", "--ref", "main"))
        self.assertTrue(r["ref_updated"])
        self.assertEqual(self.ok("update", cwd=dest).split()[1].rstrip(":"), r["id"][:12])
        self.ok("rebase", cwd=dest)
        self.assertEqual(read(os.path.join(dest, "docs/x.txt")), "api write\n")
        # sparse and virtual from the CLI
        sp = os.path.join(self.tmp, "sp")
        self.ok("--server", server, "--repo", REPO, "clone", sp, "--objects", self.c.daemon_urls[0], "--sparse", "src/d1")
        self.assertEqual(self.ok("sparse", "show", cwd=sp), "src/d1\n")
        self.ok("sparse", "add", "docs", cwd=sp)
        self.assertTrue(os.path.exists(os.path.join(sp, "docs/x.txt")))
        vt = os.path.join(self.tmp, "vt")
        self.ok("--server", server, "--repo", REPO, "clone", vt, "--objects", self.c.daemon_urls[0], "--virtual")
        self.assertEqual(self.ok("cat", "docs/x.txt", cwd=vt), "api write\n")
        self.ok("materialize", "src/d2", cwd=vt)
        self.assertEqual(len(os.listdir(os.path.join(vt, "src/d2"))), 3)
        if fsmonitor.supported():
            self.assertIn("running", self.ok("watch", "start", cwd=dest))
            self.assertIn("running", self.ok("watch", "status", cwd=dest))
            self.assertEqual(self.ok("watch", "stop", cwd=dest).strip(), "stopped")
        code, _, err = self.scn("update", "no-such-rev", cwd=dest)
        self.assertEqual(code, 1)
        self.assertIn("not_found", err)
        # every request the CLI made to the server was a public, registered RPC
        served = {k[4:] for s in self.c.services for k in s.metrics.counters if k.startswith("rpc.")}
        self.assertTrue(served <= set(self.c.services[0].methods), served - set(self.c.services[0].methods))

    def test_T_CL_14_review_from_the_cli(self):
        server = self.c.server_urls[0]
        dest = os.path.join(self.tmp, "wc")
        self.ok("--server", server, "--repo", REPO, "--user", "alice", "clone", dest, "--objects", self.c.daemon_urls[0])
        write(os.path.join(dest, "src/tool.py"), "print('reviewed')\n")  # code: it needs an approval
        cs = self.ok("commit", "-A", "-m", "for review", cwd=dest).split()[1]
        out = self.ok("review", "create", "--title", "Please look", cwd=dest)
        cr = int(out.split()[3])
        self.assertIn("Please look", self.ok("review", "list", cwd=dest))
        code, out, _ = self.scn("review", "requirements", cr, cwd=dest)
        self.assertEqual((code, json.loads(out)["satisfied"]), (1, False))
        bob = ["--server", server, "--repo", REPO, "--user", "bob"]
        self.ok(*bob, "review", "comment", cr, "looks fine", "--path", "src/tool.py", "--line", "1")
        self.ok(*bob, "review", "approve", cr)
        show = self.ok("review", "show", cr, cwd=dest)
        self.assertIn("[bob src/tool.py:1] looks fine", show)
        landed = self.ok("review", "land", cr, cwd=dest).split()[1]
        self.assertEqual(self.api.call("resolve", repo=REPO, rev="main"), landed)
        self.assertIn(f"through change request {cr}", self.ok("review", "landing", cs, cwd=dest))
        self.assertIn("landed", self.ok("review", "list", "--state", "landed", cwd=dest))


if __name__ == "__main__":
    unittest.main()

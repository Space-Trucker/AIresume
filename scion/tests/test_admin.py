"""The admin toolkit (WP-B4.4): backup and restore (T-BAK-01), the scion-admin commands end to end
(T-ADM-02) and the benchmark invariants (T-PERF-01)."""
import base64
import contextlib
import io
import json
import math
import os
import shutil
import subprocess
import tempfile
import threading
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion import cli
from scion.backup import BackupError, backup, check_backup, restore, verify
from scion.deployment import Deployment
from scion.rpc import RemoteError, RpcClient, RpcServer
from scion.server import ScionService

POLICY = {"read": ["*"], "write": ["*"], "paths": [{"prefix": "secrets", "read": ["sec-team"]}]}


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def run_cli(*argv) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(list(argv))
    return code, out.getvalue() + err.getvalue()


class TestBackupAndRestore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-backup-")
        self.c = Cluster(self.tmp, caches=0, repos={REPO: POLICY, "tools": None},
                         identity={"admins": ["root"], "groups": {"sec-team": ["sam"]}})
        self.alice = self.c.client("alice")
        self.base = self.alice.call("create_changeset", repo=REPO, parents=[], message="seed",
                                    files=[{"path": "src/app.py", "content_b64": b64("app = 1\n")},
                                           {"path": "secrets/key.txt", "content_b64": b64("KEY\n")}],
                                    update_ref={"name": "main", "old": None})["id"]
        self.c.client("bob").call("create_changeset", repo="tools", parents=[], message="t",
                                  files=[{"path": "t.sh", "content_b64": b64("echo\n")}],
                                  update_ref={"name": "main", "old": None})

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def land(self, i):
        head = self.alice.call("create_changeset", repo=REPO, parents=[self.alice.call("resolve", repo=REPO, rev="main")],
                               message=f"doc {i}", files=[{"path": f"docs/d{i}.md", "content_b64": b64(f"{i}\n")}])["id"]
        cr = self.alice.call("antique.create", repo=REPO, title=f"doc {i}", head=head)
        return self.alice.call("antique.land", repo=REPO, id=cr["id"])["landed_cs"]  # docs need no approval

    def test_T_BAK_01_backup_under_load_then_restore(self):
        stop, errors, landed = threading.Event(), [], []

        def writer():
            i = 0
            while not stop.is_set():
                try:
                    landed.append(self.land(i))
                except Exception as e:  # noqa: BLE001
                    errors.append(e)
                    return
                i += 1

        t = threading.Thread(target=writer)
        t.start()
        try:
            for i in range(3):
                self.land(1000 + i)
            out = os.path.join(self.tmp, "backup")
            manifest = backup(self.c.dep_root, out, actor="ops")
        finally:
            stop.set()
            t.join(30)
        self.assertEqual(errors, [])
        self.assertGreater(len(landed), 0)  # the servers kept landing while the backup ran
        live = self.c.repo()
        self.assertGreaterEqual(live.meta.count_changesets(), manifest["repos"][REPO]["changesets"])
        self.assertEqual(sorted(manifest["repos"]), ["monorepo", "tools"])
        self.assertEqual(live.audit.last("backup")["actor"], "ops")

        restored = os.path.join(self.tmp, "restored")
        report = restore(out, restored, actor="ops")
        self.assertTrue(report["ok"], report)
        self.assertIsNone(report["moved_aside"])
        dep = Deployment(restored)
        try:
            repo = dep.repo(REPO)
            want = manifest["repos"][REPO]
            self.assertEqual({n: t for n, t, _ in repo.meta.list_refs()}, want["refs"])  # NFR-13
            self.assertEqual(repo.meta.count_changesets(), want["changesets"])
            for (cs,) in repo.meta.execute("SELECT id FROM changesets"):
                self.assertEqual(repo.get_changeset(cs).id, cs)
                self.assertTrue(live.meta.has_changeset(cs))
            self.assertTrue(repo.audit.verify()["ok"])  # the chain survives, with a "restore" entry
            self.assertEqual(repo.audit.last("restore")["actor"], "ops")
            self.assertTrue(repo.meta.execute("SELECT COUNT(*) FROM crs").fetchone()[0] >= 3)
        finally:
            dep.close()
        # a server on the restored root serves the data, with the same permissions
        dep = Deployment(restored)
        srv = RpcServer(ScionService(dep), "http://127.0.0.1:0").start()
        try:
            def call(user, method, **p):
                return RpcClient(srv.url, user=user).call(method, repo=REPO, **p)
            main = manifest["repos"][REPO]["refs"]["main"]
            self.assertEqual(call("carol", "resolve", rev="main"), main)
            self.assertEqual(base64.b64decode(call("carol", "read_file", rev="main", path="src/app.py")["content_b64"]),
                             b"app = 1\n")
            with self.assertRaises(RemoteError) as e:
                call("carol", "read_file", rev="main", path="secrets/key.txt")
            self.assertEqual(e.exception.status, 403)
            self.assertEqual(call("sam", "read_file", rev="main", path="secrets/key.txt")["content_b64"], b64("KEY\n"))
        finally:
            srv.stop()
            dep.close()

    def test_restore_refuses_damaged_backups_and_keeps_existing_data(self):
        out = os.path.join(self.tmp, "backup")
        backup(self.c.dep_root, out)
        with self.assertRaises(BackupError):  # the destination isn't empty
            backup(self.c.dep_root, out)
        restored = os.path.join(self.tmp, "restored")
        restore(out, restored)
        with self.assertRaises(BackupError):  # nor is the restore target
            restore(out, restored)
        report = restore(out, restored, force=True, deep=True)
        self.assertTrue(report["ok"])
        self.assertTrue(os.path.isdir(report["moved_aside"]))  # moved aside, never deleted
        with open(os.path.join(out, "repos", REPO, "policy.json"), "w") as f:
            json.dump({"read": ["*"], "write": ["*"]}, f)  # someone edits the backup: secrets would open up
        with self.assertRaises(BackupError) as e:
            check_backup(out)
        self.assertIn("policy.json", str(e.exception))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "elsewhere")))
        with self.assertRaises(BackupError):
            restore(out, os.path.join(self.tmp, "elsewhere"))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "elsewhere")), "nothing restored from a damaged backup")

    def test_verify_finds_missing_and_corrupt_objects(self):
        self.assertTrue(verify(self.c.dep_root, deep=True)["ok"])
        repo = self.c.repo()
        blob = repo.trees.lookup(repo.root_tree(self.base), "src/app.py")[1]
        path = repo.objects.path(blob)
        with open(path, "rb") as f:
            good = f.read()
        with open(path, "wb") as f:
            f.write(good[:-4] + b"oops")
        r = verify(self.c.dep_root, deep=True)
        self.assertFalse(r["ok"])
        self.assertEqual(r["repos"][REPO]["corrupt"], [blob])
        os.unlink(path)
        r = verify(self.c.dep_root)
        self.assertIn("main:src/app.py", r["repos"][REPO]["missing"])
        os.unlink(repo.objects.path(repo.trees.lookup(repo.root_tree(self.base), "src")[1]))  # a whole tree
        r = verify(self.c.dep_root)
        self.assertFalse(r["ok"])
        self.assertTrue(any("incomplete tree" in m for m in r["repos"][REPO]["missing"]), r)


class TestAdminToolkit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-admin-")
        self.root = os.path.join(self.tmp, "dep")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    @unittest.skipUnless(shutil.which("git"), "needs git")
    def test_T_ADM_02_the_admin_commands_end_to_end(self):
        g = os.path.join(self.tmp, "git")
        os.makedirs(os.path.join(g, "src"))
        env = {**os.environ, "GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "dev@example.com", "GIT_COMMITTER_NAME": "Dev",
               "GIT_COMMITTER_EMAIL": "dev@example.com", "GIT_CONFIG_GLOBAL": "/dev/null"}
        for args in (["init", "-q", "-b", "main"],):
            subprocess.run(["git", *args], cwd=g, check=True, env=env)
        for i in range(3):
            with open(os.path.join(g, "src", "app.py"), "a") as f:
                f.write(f"step = {i}\n")
            subprocess.run(["git", "add", "-A"], cwd=g, check=True, env=env)
            subprocess.run(["git", "commit", "-qm", f"step {i}"], cwd=g, check=True, env=env)

        def ok(*argv):
            code, out = run_cli("scion-admin", *argv)
            self.assertEqual(code, 0, out)
            return out

        ok("init", "--root", self.root)
        ok("create-repo", "--root", self.root, "monorepo", "--read", "*", "--write", "*")
        self.assertEqual(ok("repos", "--root", self.root).split(), ["monorepo"])
        stats = json.loads(ok("ingest", "--root", self.root, "--repo", "monorepo", "--git", g, "--rev", "main",
                              "--ref", "main", "--verify").split("\n}\n")[0] + "\n}")
        self.assertEqual(stats["commits"], 3)
        self.assertIn("values computed", ok("derive", "--root", self.root, "--repo", "monorepo", "blame"))
        snap = json.loads(ok("snapshot", "--root", self.root, "--repo", "monorepo", "--out",
                             os.path.join(self.tmp, "snapshots")))
        self.assertGreater(snap["objects"], 0)
        ok("reindex-acl", "--root", self.root, "--repo", "monorepo")
        self.assertIn('"ok": true', ok("audit", "--root", self.root, "--repo", "monorepo", "--verify"))
        backup_dir = os.path.join(self.tmp, "backup")
        self.assertIn("4 changesets" if False else "3 changesets",
                      ok("backup", "--root", self.root, "--out", backup_dir))
        restored = os.path.join(self.tmp, "restored")
        self.assertTrue(json.loads(ok("restore", "--backup", backup_dir, "--root", restored, "--deep"))["ok"])
        self.assertTrue(json.loads(ok("verify", "--root", restored, "--deep"))["ok"])
        actions = ok("audit", "--root", restored, "--repo", "monorepo", "--limit", "100")
        for action in ("policy.load", "ingest", "derive", "acl.reindex", "restore"):
            self.assertIn(action, actions)
        code, out = run_cli("scion-admin", "restore", "--backup", backup_dir, "--root", restored)
        self.assertEqual(code, 1)
        self.assertIn("not empty", out)


class TestBenchmarks(unittest.TestCase):
    def test_T_PERF_01_benchmark_invariants(self):
        from scion.tools import bench

        r = bench.run(quick=True)
        c, a, k = r["commit_scaling"], r["ancestry"], r["checkout"]
        self.assertEqual({v["trees_written_per_commit"] for v in c["sizes"].values()}, {3})  # NFR-05
        log2 = math.log2(a["length"])
        self.assertLessEqual(a["fp_ancestor_steps"], math.ceil(log2) + 1)  # NFR-06: O(log n)
        self.assertLessEqual(a["is_ancestor_steps"], 2 * math.ceil(log2) + 2)
        self.assertLessEqual(a["merge_base_steps"], 4 * math.ceil(log2) + 4)
        self.assertGreater(k["cold_clone"]["cache_requests"], 0)
        self.assertEqual(k["warm_clone"]["cache_requests"], 0)  # NFR-02: the daemon answers the node
        self.assertEqual(k["sparse_checkout"]["cache_requests"], 0)
        self.assertLess(k["sparse_checkout"]["objects"], k["cold_clone"]["objects"] / 4)
        self.assertLess(k["sparse_checkout"]["seconds"], 10)  # NFR-04: a project in seconds from a warm daemon
        self.assertTrue(k["clones_identical"])
        self.assertIn("Commit scaling", bench.report(r))


if __name__ == "__main__":
    unittest.main()

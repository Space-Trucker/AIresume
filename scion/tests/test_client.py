import base64
import os
import subprocess
import sys
import time
import unittest

from helpers import Cluster, read, write
from scion import fsmonitor
from scion.client import ClientError, ServerApi, WorkingCopy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.c = Cluster()
        files = {f"pkg{i}/m{j}.py": f"# pkg {i} module {j}\nVALUE = {j}\n".encode() for i in range(4) for j in range(5)}
        files["README.md"] = b"readme\n"
        self.c.seed(files)

    def tearDown(self):
        self.c.close()


class TestWorkflow(ClientTestCase):
    def test_edit_commit_status(self):
        wc = self.c.clone("wc")
        self.assertFalse(wc.status().dirty)
        write(wc, "pkg0/m0.py", b"# changed\n")
        write(wc, "new/file.txt", b"new\n")
        os.unlink(os.path.join(wc.root, "pkg1/m1.py"))
        st = wc.status()
        self.assertEqual(st.modified, ["pkg0/m0.py"])
        self.assertEqual(st.removed, ["pkg1/m1.py"])
        self.assertEqual(st.untracked, ["new/file.txt"])
        wc.add(["new"])
        self.assertEqual(wc.status().added, ["new/file.txt"])
        cs = wc.commit("my change")
        self.assertEqual(wc.base, cs)
        self.assertFalse(wc.status().dirty)
        changes = {c.path: c.op for c in self.c.repo.get_changeset(cs).changes}
        self.assertEqual(changes, {"pkg0/m0.py": "M", "pkg1/m1.py": "D", "new/file.txt": "A"})
        self.assertIsNone(self.c.repo.meta.git_map_get("x"))  # nothing was pushed: there is no push

    def test_modes_and_symlinks_roundtrip(self):
        wc = self.c.clone("wc")
        script = os.path.join(wc.root, "run.sh")
        write(wc, "run.sh", b"#!/bin/sh\necho hi\n")
        os.chmod(script, 0o755)
        os.symlink("README.md", os.path.join(wc.root, "link"))
        cs = wc.commit("modes", addremove=True)
        kinds = {c.path: c.kind for c in self.c.repo.get_changeset(cs).changes}
        self.assertEqual(kinds, {"run.sh": "x", "link": "l"})
        wc2 = self.c.clone("wc2", rev=cs)
        self.assertTrue(os.access(os.path.join(wc2.root, "run.sh"), os.X_OK))
        self.assertEqual(os.readlink(os.path.join(wc2.root, "link")), "README.md")

    def test_update_fetches_only_the_diff_and_protects_local_changes(self):
        wc = self.c.clone("wc")
        start = wc.base
        other = self.c.clone("other")
        write(other, "pkg2/m2.py", b"# upstream edit\n")
        up = other.commit("upstream")
        before = dict(wc.fetcher.counters)
        r = wc.update(up)
        self.assertEqual(r["changed"], 1)
        self.assertEqual(wc.fetcher.counters["requested"] - before["requested"], 1)
        self.assertEqual(read(wc, "pkg2/m2.py"), b"# upstream edit\n")
        write(wc, "pkg2/m2.py", b"# my local edit\n")
        with self.assertRaises(ClientError):
            wc.update(start)
        write(wc, "pkg2/m2.py", b"# upstream edit\n")
        write(wc, "pkg3/m3.py", b"# unrelated local edit\n")
        wc.update(start)
        self.assertEqual(read(wc, "pkg3/m3.py"), b"# unrelated local edit\n")  # preserved

    def test_rebase_on_server(self):
        wc = self.c.clone("wc")
        write(wc, "pkg0/m0.py", b"# mine\n")
        wc.commit("mine")
        upstream = self.c.seed({"pkg1/m1.py": b"# theirs\n"})
        r = wc.rebase("main")
        self.assertTrue(self.c.repo.is_ancestor(upstream, wc.base))
        self.assertEqual(read(wc, "pkg1/m1.py"), b"# theirs\n")
        self.assertEqual(read(wc, "pkg0/m0.py"), b"# mine\n")
        self.assertEqual(len(r["rebased"]), 1)
        self.assertEqual(wc.stack(), [wc.base])

    def test_local_diff(self):
        wc = self.c.clone("wc")
        write(wc, "README.md", b"readme\nmore\n")
        d = wc.diff_local()
        self.assertIn("+more", d)
        self.assertIn("a/README.md", d)


class TestSparseAndVirtual(ClientTestCase):
    def test_sparse_checkout(self):
        wc = self.c.clone("sp", mode="sparse", sparse=["pkg1"])
        on_disk = sorted(p for p in os.listdir(wc.root) if p != ".scn")
        self.assertEqual(on_disk, ["pkg1"])
        self.assertEqual(wc.fetcher.counters["requested"], 5 + 2)  # 5 blobs + root and pkg1 trees
        write(wc, "pkg1/m0.py", b"# sparse edit\n")
        cs = wc.commit("sparse commit")
        self.assertEqual([c.path for c in self.c.repo.get_changeset(cs).changes], ["pkg1/m0.py"])
        self.assertEqual(wc.sparse_add(["pkg2"]), 5)
        self.assertTrue(os.path.exists(os.path.join(wc.root, "pkg2/m4.py")))
        self.assertEqual(wc.sparse_remove(["pkg1"]), 5)
        self.assertFalse(os.path.exists(os.path.join(wc.root, "pkg1")))
        # Upstream changes outside the profile cost nothing on update.
        self.c.seed({"pkg3/m0.py": b"# far away\n"})
        before = wc.fetcher.counters["requested"]
        wc.update("main")
        self.assertEqual(wc.fetcher.counters["requested"], before)

    def test_adding_outside_the_sparse_profile(self):
        wc = self.c.clone("sp2", mode="sparse", sparse=["pkg1"])
        write(wc, "notes/new.md", b"note\n")
        wc.add(["notes"])
        self.assertEqual(wc.status().added, ["notes/new.md"])
        cs = wc.commit("note")
        self.assertEqual([c.path for c in self.c.repo.get_changeset(cs).changes], ["notes/new.md"])
        self.assertFalse(wc.status().dirty)  # still tracked after the commit
        self.assertIn("notes/new.md", wc.profile.prefixes)

    def test_virtual_checkout_materializes_on_demand(self):
        wc = self.c.clone("virt", mode="virtual")
        self.assertEqual([p for p in os.listdir(wc.root) if p != ".scn"], [])
        self.assertEqual(wc.fetcher.counters["fetched"], 0)
        self.assertEqual(wc.read("pkg2/m3.py"), b"# pkg 2 module 3\nVALUE = 3\n")
        self.assertEqual(wc.fetcher.counters["fetched"], 3)  # root tree, pkg2 tree, one blob
        self.assertEqual([e["name"] for e in wc.listdir("")][:2], ["README.md", "pkg0"])
        write(wc, "pkg2/m3.py", b"# edited\n")
        write(wc, "pkg0/m0.py", b"# written without reading\n")  # unmaterialized path
        st = wc.status()
        self.assertEqual(st.modified, ["pkg0/m0.py", "pkg2/m3.py"])
        cs = wc.commit("virtual edit")
        self.assertEqual(len(self.c.repo.get_changeset(cs).changes), 2)
        self.assertEqual(wc.materialize(["pkg1"]), 5)

    def test_bounded_local_cache(self):
        wc = self.c.clone("tiny", cache_bytes=600)
        self.assertLessEqual(wc.local.size_bytes, 600 + 400)
        self.assertGreater(wc.local.evictions, 0)
        self.assertEqual(read(wc, "pkg3/m4.py"), b"# pkg 3 module 4\nVALUE = 4\n")


@unittest.skipUnless(fsmonitor.supported(), "inotify is Linux-only")
class TestFsmonitor(ClientTestCase):
    def test_status_uses_journal(self):
        wc = self.c.clone("watched")
        fsmonitor.start(wc.root)
        try:
            self.assertTrue(fsmonitor.is_running(wc.root))
            wc.status()  # first query establishes the session (full scan)
            write(wc, "pkg1/m2.py", b"# watched edit\n")
            os.makedirs(os.path.join(wc.root, "newdir"))
            write(wc, "newdir/a.txt", b"a\n")
            st = wc.status()
            self.assertTrue(st.used_fsmonitor)
            self.assertEqual(st.modified, ["pkg1/m2.py"])
            self.assertEqual(st.untracked, ["newdir/a.txt"])
            self.assertLessEqual(st.scanned, 2)  # not the whole working copy
            os.unlink(os.path.join(wc.root, "newdir/a.txt"))
            write(wc, "pkg1/m2.py", b"# pkg 1 module 2\nVALUE = 2\n")  # back to clean
            st = wc.status()
            self.assertFalse(st.dirty)
            self.assertEqual(st.untracked, [])
        finally:
            fsmonitor.stop(wc.root)
            time.sleep(0.1)


class TestCheckoutlessAndCli(ClientTestCase):
    def test_write_without_checkout(self):
        api = ServerApi(self.c.server.url, "ci-bot")
        tip = api.get_ref(name="main")
        r = api.create_changeset(parents=["main"], message="generated",
                                 files=[{"path": "gen/out.txt", "content_b64": base64.b64encode(b"generated\n").decode()}],
                                 update_ref={"name": "bot/generated", "old": None})
        self.assertTrue(r["ref_updated"])
        self.assertEqual(api.get_changeset(rev="bot/generated")["parents"], [tip])
        d = api.diff(b=r["id"], merge_base=True, text=True)  # diff against the merge base, no checkout
        self.assertIn("+generated", d["text"])

    def scn(self, cwd, *args, check=True):
        env = {**os.environ, "PYTHONPATH": ROOT}
        r = subprocess.run([sys.executable, "-m", "scion", "scn", *args], cwd=cwd, env=env,
                           capture_output=True, text=True, timeout=60)
        if check and r.returncode != 0:
            self.fail(f"scn {' '.join(args)} failed:\n{r.stdout}\n{r.stderr}")
        return r.stdout

    def test_cli_end_to_end(self):
        dest = os.path.join(self.c.tmp, "cli")
        out = self.scn(self.c.tmp, "--server", self.c.server.url, "--user", "dana", "clone", dest,
                       "--objects", self.c.objects_url, "--sparse", "pkg0,pkg1")
        self.assertIn("checked out", out)
        with open(os.path.join(dest, "pkg0/m1.py"), "a") as f:
            f.write("EXTRA = 1\n")
        self.assertIn("M pkg0/m1.py", self.scn(dest, "status"))
        self.assertIn("created changeset", self.scn(dest, "commit", "-m", "cli change"))
        self.assertIn("cli change", self.scn(dest, "log", "--oneline", "-n", "3"))
        self.assertIn("EXTRA = 1", self.scn(dest, "blame", "pkg0/m1.py"))
        self.assertIn("pkg0/m1.py", self.scn(dest, "history", "pkg0/m1.py"))
        self.assertIn("pkg1/m3.py", self.scn(dest, "search", "m3"))
        self.assertIn("pkg0/m1.py:3", self.scn(dest, "grep", "EXTRA"))
        self.assertIn("pkg1", self.scn(dest, "sparse", "show"))
        out = self.scn(dest, "review", "create", "--title", "cli review")
        self.assertIn('"state": "open"', out)


if __name__ == "__main__":
    unittest.main()

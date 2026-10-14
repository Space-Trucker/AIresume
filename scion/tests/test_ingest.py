"""git ingestion (WP-B4.1): T-MG-01…05."""
import os
import shutil
import subprocess
import tempfile
import tracemalloc
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster, repository
from scion.ingest import GitIngester, IngestError


GIT_ENV = {"GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "dev@example.com", "GIT_COMMITTER_NAME": "Dev",
           "GIT_COMMITTER_EMAIL": "dev@example.com", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


def git(cwd, *args, stdin=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, input=stdin, env={**os.environ, **GIT_ENV})
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode())
    return r.stdout.decode()


def put(cwd, path, data):
    full = os.path.join(cwd, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(data)


@unittest.skipUnless(shutil.which("git"), "needs git")
class TestIngest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-ingest-")
        self.g = os.path.join(self.tmp, "git")
        os.makedirs(self.g)
        git(self.g, "init", "-q", "-b", "main")
        put(self.g, "src/app.py", "def a():\n    return 1\n\ndef b():\n    return 2\n")
        put(self.g, "README.md", "readme\n")
        put(self.g, "tools/run.sh", "#!/bin/sh\necho run\n")
        os.chmod(os.path.join(self.g, "tools/run.sh"), 0o755)
        os.symlink("README.md", os.path.join(self.g, "LINK"))
        git(self.g, "add", "-A")
        git(self.g, "commit", "-qm", "initial")
        git(self.g, "checkout", "-qb", "feature")
        put(self.g, "src/feature.py", "FEATURE = 1\n")
        put(self.g, "src/app.py", "def a():\n    return 1\n\ndef b():\n    return 20\n")
        git(self.g, "add", "-A")
        git(self.g, "commit", "-qm", "feature work")
        git(self.g, "checkout", "-q", "main")
        put(self.g, "src/app.py", "def a():\n    return 10\n\ndef b():\n    return 2\n")
        git(self.g, "commit", "-qam", "main work")
        git(self.g, "merge", "-q", "--no-edit", "feature")
        os.makedirs(os.path.join(self.g, "lib"))
        git(self.g, "mv", "src/feature.py", "lib/feature.py")
        git(self.g, "commit", "-qm", "rename")
        os.unlink(os.path.join(self.g, "README.md"))
        put(self.g, "README.md/index.md", "now a directory\n")
        git(self.g, "add", "-A")
        git(self.g, "commit", "-qm", "file becomes directory")
        self.repo = repository(os.path.join(self.tmp, "scion"))

    def tearDown(self):
        self.repo.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def sha(self, rev):
        return git(self.g, "rev-parse", rev).strip()

    def test_T_MG_01_ingest_verify_incremental_and_map(self):
        ing = GitIngester(self.repo, self.g)
        stats = ing.ingest("main", "main")
        self.assertEqual(stats["commits"], 6)
        v = ing.verify("main")
        self.assertTrue(v["ok"], v["mismatches"])
        self.assertEqual(v["files"], 5)
        tip = self.repo.get_ref("main")
        self.assertEqual(ing.changeset_for(self.sha("main")), tip)  # FR-MG-07: both ways
        self.assertEqual(ing.git_for(tip), self.sha("main"))
        self.assertEqual(self.repo.get_changeset(tip).extra["git"], self.sha("main"))
        # FR-MG-01: the commit graph and first parents are preserved
        merge = ing.changeset_for(self.sha("main~2"))
        self.assertEqual(self.repo.get_changeset(merge).parents,
                         (ing.changeset_for(self.sha("main~3")), ing.changeset_for(self.sha("feature"))))
        self.assertEqual(self.repo.get_changeset(tip).author, "Dev <dev@example.com>")
        self.assertEqual({p: k for p, k, _ in self.repo.trees.walk(self.repo.root_tree(tip))},
                         {"LINK": "l", "README.md/index.md": "f", "lib/feature.py": "f", "src/app.py": "f",
                          "tools/run.sh": "x"})
        hist = self.repo.file_history("main", "lib/feature.py")  # history follows the rename
        self.assertEqual(hist[-1]["path"], "src/feature.py")
        # FR-MG-03: a re-run ingests only the new commits
        put(self.g, "src/new.py", "NEW = 1\n")
        git(self.g, "add", "-A")
        git(self.g, "commit", "-qm", "new")
        again = GitIngester(self.repo, self.g)
        stats2 = again.ingest("main", "main")
        self.assertEqual((stats2["commits"], stats2["skipped"]), (1, 6))
        self.assertTrue(again.verify("main")["ok"])

    def test_T_MG_02_blame_matches_git_blame_first_parent(self):
        for i in range(6):
            with open(os.path.join(self.g, "src/app.py")) as f:
                text = f.read() + f"# step {i}\nX{i} = {i}\n"
            if i % 2:
                text = text.replace(f"X{i - 1} = {i - 1}", f"X{i - 1} = -{i}")
            put(self.g, "src/app.py", text)
            git(self.g, "commit", "-qam", f"step {i}")
        ing = GitIngester(self.repo, self.g)
        ing.ingest("main", "main")
        out = git(self.g, "blame", "--first-parent", "-l", "-s", "main", "--", "src/app.py")
        theirs = [line.split()[0].lstrip("^") for line in out.splitlines()]
        ours = [ing.git_for(line["cs"]) for line in self.repo.blame("main", "src/app.py")["lines"]]
        # git prints a boundary commit as "^" plus its hash shortened by one character
        self.assertEqual(len(ours), len(theirs))
        self.assertEqual([o for o, t in zip(ours, theirs) if not o.startswith(t)], [])
        merge = self.sha("main~8")  # "return 20" came in with the merge: main line only (BR-06)
        line = next(x for x in self.repo.blame("main", "src/app.py")["lines"] if x["text"].strip() == "return 20")
        self.assertEqual(ing.git_for(line["cs"]), merge)

    def test_T_MG_03_ordering_invariant(self):
        with self.assertRaises(IngestError) as e:
            GitIngester(self.repo, self.g).ingest("main~1..main", None)
        self.assertIn("nothing was written", str(e.exception))
        self.assertEqual(self.repo.meta.count_changesets(), 0)
        GitIngester(self.repo, self.g).ingest("main~1", "main")  # in order, the range then works
        stats = GitIngester(self.repo, self.g).ingest("main~1..main", "main")
        self.assertEqual(stats["commits"], 1)

    def test_T_MG_05_metadata_queries_without_a_client(self):
        c = Cluster(os.path.join(self.tmp, "cluster"), caches=0)
        try:
            ing = GitIngester(c.repo(), self.g)
            ing.ingest("main", "main")
            api = c.client("ci")
            tip = api.call("resolve", repo=REPO, rev="main")
            found = api.call("git_lookup", repo=REPO, git=self.sha("main~3"))
            self.assertEqual(api.call("git_lookup", repo=REPO, cs=found["cs"])["git"], self.sha("main~3"))
            self.assertTrue(api.call("is_ancestor", repo=REPO, a=found["cs"], b=tip))
            blame = api.call("blame", repo=REPO, rev="main", path="src/app.py")
            self.assertEqual(len(blame["lines"]), 5)
        finally:
            c.close()


@unittest.skipUnless(shutil.which("git"), "needs git")
class TestIngestMemory(unittest.TestCase):
    def history(self, commits: int) -> str:
        """A linear history with fast-import: a few directories, one file edited per commit."""
        d = tempfile.mkdtemp(prefix="scion-fi-")
        git(d, "init", "-q", "-b", "main")
        lines = []
        for i in range(commits):
            data = f"commit {i}\n" * 3
            lines += ["commit refs/heads/main", f"mark :{i + 1}", f"committer Dev <dev@example.com> {1700000000 + i} +0000",
                      "data 2", "m"]
            if i:
                lines.append(f"from :{i}")
            lines += [f"M 100644 inline d{i % 20}/f{i % 7}.txt", f"data {len(data)}", data.rstrip("\n")]
        git(d, "fast-import", "--quiet", stdin="\n".join(lines).encode() + b"\n")
        return d

    def test_T_MG_04_memory_stays_flat_as_history_grows(self):
        """Every cache is bounded (here at 256 KiB, so the bound is reached quickly): five times the
        history costs no more memory once the caches are full."""
        peaks = {}
        for n in (240, 1200):
            g = self.history(n)
            tmp = tempfile.mkdtemp(prefix="scion-mem-")
            repo = repository(tmp)
            try:
                tracemalloc.start()
                stats = GitIngester(repo, g, cache_bytes=256 << 10).ingest("main", "main")
                peaks[n] = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                self.assertEqual(stats["commits"], n)
            finally:
                repo.close()
                shutil.rmtree(tmp, ignore_errors=True)
                shutil.rmtree(g, ignore_errors=True)
        self.assertLess(peaks[1200], peaks[240] * 1.3, peaks)


if __name__ == "__main__":
    unittest.main()

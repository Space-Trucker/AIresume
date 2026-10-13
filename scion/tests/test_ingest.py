import os
import shutil
import subprocess
import tempfile
import unittest

import helpers  # noqa: F401
from scion.ingest import GitIngester, IngestError
from scion.repo import Repository


def git(cwd, *args, env=None):
    e = {**os.environ, "GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "dev@example.com",
         "GIT_COMMITTER_NAME": "Dev", "GIT_COMMITTER_EMAIL": "dev@example.com", **(env or {})}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=e).stdout.decode()


def put(cwd, path, data):
    full = os.path.join(cwd, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(data)


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
        git(self.g, "commit", "-qam", "feature work")
        git(self.g, "add", "-A")
        git(self.g, "commit", "-qm", "feature file")
        git(self.g, "checkout", "-q", "main")
        put(self.g, "src/app.py", "def a():\n    return 10\n\ndef b():\n    return 2\n")
        git(self.g, "commit", "-qam", "main work")
        git(self.g, "merge", "-q", "--no-edit", "feature")
        os.makedirs(os.path.join(self.g, "lib"))
        git(self.g, "mv", "src/feature.py", "lib/feature.py")
        git(self.g, "commit", "-qm", "rename")
        os.unlink(os.path.join(self.g, "README.md"))
        os.makedirs(os.path.join(self.g, "README.md"))
        put(self.g, "README.md/index.md", "now a directory\n")
        git(self.g, "add", "-A")
        git(self.g, "commit", "-qm", "file becomes directory")
        self.repo = Repository(os.path.join(self.tmp, "scion"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ingest_verify_and_incremental(self):
        ing = GitIngester(self.repo, self.g)
        stats = ing.ingest("main", "main")
        self.assertEqual(stats["commits"], 7)
        self.assertTrue(ing.verify("main")["ok"])
        tip = self.repo.get_ref("main")
        cs = self.repo.get_changeset(tip)
        self.assertEqual(cs.extra["git"], git(self.g, "rev-parse", "main").strip())
        merge = self.repo.resolve("main~2")
        self.assertEqual(len(self.repo.get_changeset(merge).parents), 2)
        # history follows the rename; blame credits both branches through the merge
        hist = self.repo.file_history("main", "lib/feature.py")
        self.assertEqual(hist[-1]["path"], "src/feature.py")
        authors = {l["text"].strip(): self.repo.get_changeset(l["cs"]).message.strip()
                   for l in self.repo.blame("main", "src/app.py")["lines"]}
        self.assertEqual(authors["return 10"], "main work")
        self.assertEqual(authors["return 20"], "feature work")
        # incremental: only new commits are ingested
        put(self.g, "src/new.py", "NEW = 1\n")
        git(self.g, "add", "-A")
        git(self.g, "commit", "-qm", "new")
        stats2 = GitIngester(self.repo, self.g).ingest("main", "main")
        self.assertEqual((stats2["commits"], stats2["skipped"]), (1, 7))
        self.assertTrue(GitIngester(self.repo, self.g).verify("main")["ok"])

    def test_blame_matches_git_on_linear_history(self):
        for i in range(6):
            with open(os.path.join(self.g, "src/app.py"), "a") as f:
                f.write(f"# step {i}\nX{i} = {i}\n")
            if i % 2:
                txt = open(os.path.join(self.g, "src/app.py")).read().replace(f"X{i - 1} = {i - 1}", f"X{i - 1} = -1")
                put(self.g, "src/app.py", txt)
            git(self.g, "commit", "-qam", f"step {i}")
        GitIngester(self.repo, self.g).ingest("main", "main")
        porcelain = git(self.g, "blame", "--first-parent", "-l", "-s", "main", "--", "src/app.py")
        theirs = [line.split()[0].lstrip("^") for line in porcelain.splitlines()]
        ours = [self.repo.get_changeset(l["cs"]).extra["git"] for l in self.repo.blame("main", "src/app.py")["lines"]]
        # Lines that came from the merge's second parent are credited to the original commit
        # by Scion and to the merge by `git blame --first-parent`; compare everything else.
        merge_sha = git(self.g, "rev-list", "--merges", "-n1", "main").strip()
        # (git prints boundary commits as "^" plus a hash truncated by one character)
        diffs = [(o, t) for o, t in zip(ours, theirs) if not o.startswith(t) and t != merge_sha]
        self.assertEqual(len(ours), len(theirs))
        self.assertEqual(diffs, [])

    def test_ordering_invariant_is_enforced(self):
        # A range whose parents were never ingested must be refused, not silently re-parented.
        with self.assertRaises(IngestError):
            GitIngester(self.repo, self.g).ingest("main~1..main", None)
        self.assertEqual(self.repo.meta.count_changesets(), 0)


if __name__ == "__main__":
    unittest.main()

"""Code search (WP-B4.3): T-SR-01 (path search and grep, filtered by permissions) and T-SR-02 (the
indexed content search reads only candidate blobs and matches a full scan)."""
import base64
import random
import shutil
import tempfile
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster, repository
from scion.search import grep, required_literals, search_paths


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


class TestSearchThroughTheApi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-search-")
        self.c = Cluster(self.tmp, caches=0, identity={"groups": {"sec-team": ["sam"]}},
                         repos={REPO: {"read": ["*"], "write": ["*"],
                                       "paths": [{"prefix": "secrets", "read": ["sec-team"]}]}})
        files = {f"pkg{i}/mod{j}.py": f"def handler_{i}_{j}():\n    return {i * j}\n" for i in range(8) for j in range(6)}
        files["pkg3/special_needle.py"] = "NEEDLE = 'found me'\n"
        files["secrets/keys.py"] = "NEEDLE = 'secret value'\n"
        files["docs/notes.md"] = "the needle is in pkg3\n"
        self.cs = self.c.client("root").call("create_changeset", repo=REPO, parents=[], message="m",
                                             files=[{"path": p, "content_b64": b64(t)} for p, t in files.items()],
                                             update_ref={"name": "main", "old": None})["id"]

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def call(self, user, method, **p):
        return self.c.client(user).call(method, repo=REPO, **p)

    def test_T_SR_01_path_search_and_grep_filtered_by_permissions(self):
        r = self.call("bob", "search_paths", rev="main", query="needle")
        self.assertEqual(r["paths"], ["pkg3/special_needle.py"])
        self.assertLess(r["trees_visited"], 6, "bloom filters skip directories that can't match")
        hits = self.call("bob", "grep", rev="main", pattern=r"NEEDLE = '(\w+)")
        self.assertEqual([(m["path"], m["line"]) for m in hits["matches"]], [("pkg3/special_needle.py", 1)])
        self.assertEqual(hits["matches"][0]["text"], "NEEDLE = 'found me'")
        self.assertTrue(hits["indexed"])
        sam = self.call("sam", "grep", rev="main", pattern="NEEDLE")
        self.assertEqual(sorted(m["path"] for m in sam["matches"]), ["pkg3/special_needle.py", "secrets/keys.py"])
        self.assertNotIn("secret value", str(self.call("bob", "grep", rev="main", pattern="secret")))  # FR-SR-04
        with self.assertRaises(Exception):
            self.call("bob", "grep", rev="main", pattern="NEEDLE", path="secrets")
        ci = self.call("bob", "grep", rev="main", pattern="needle", ignore_case=True, path="docs")
        self.assertEqual([m["path"] for m in ci["matches"]], ["docs/notes.md"])
        fixed = self.call("bob", "grep", rev="main", pattern="return 4", regex=False)
        self.assertEqual(sorted(m["path"] for m in fixed["matches"]), ["pkg1/mod4.py", "pkg2/mod2.py", "pkg4/mod1.py"])
        capped = self.call("bob", "grep", rev="main", pattern="def ", limit=5)
        self.assertEqual((len(capped["matches"]), capped["truncated"]), (5, True))


class TestIndexedContentSearch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-index-")
        self.repo = repository(self.tmp)
        rng = random.Random(7)
        words = ["alpha", "beta", "gamma", "delta", "omega", "lambda", "kappa", "sigma", "theta", "zeta"]
        files = {}
        for i in range(600):
            files[f"d{i % 30}/f{i}.txt"] = "".join(f"{rng.choice(words)} {rng.choice(words)} {i}\n" for _ in range(8))
        for i in (17, 233, 599):
            files[f"d{i % 30}/f{i}.txt"] += "rare_token_xyzzy here\n"
        self.files = files
        self.v1 = self.repo.create_changeset([], [{"path": p, "content": t.encode()} for p, t in files.items()], "a", "v1")
        self.v2 = self.repo.create_changeset([self.v1], [{"path": "d5/f5.txt", "content": b"new rare_token_xyzzy\n"},
                                                         {"path": "d17/f17.txt", "delete": True}], "a", "v2")

    def tearDown(self):
        self.repo.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def scan(self, cs, pattern):
        import re
        rx = re.compile(pattern)
        out = []
        for p, k, oid in self.repo.trees.walk(self.repo.root_tree(cs)):
            for i, line in enumerate(self.repo.read_blob(oid).decode().split("\n")[:-1], 1):  # git's lines
                if rx.search(line):
                    out.append({"path": p, "line": i, "text": line})
        return out

    def test_T_SR_02_indexed_search_reads_only_candidates_and_matches_a_full_scan(self):
        for cs in (self.v1, self.v2):
            r = grep(self.repo, cs, "rare_token_xyzzy", limit=1000)
            self.assertTrue(r["indexed"])
            self.assertEqual(r["matches"], self.scan(cs, "rare_token_xyzzy"))
            self.assertLessEqual(r["files_scanned"], 4)  # the candidates, not 600 files
        self.assertNotIn("d17/f17.txt", [m["path"] for m in grep(self.repo, self.v2, "rare_token_xyzzy")["matches"]])
        for pattern in (r"omega \d+5$", r"kappa (zeta|beta) 4", r"lambda lambda"):
            r = grep(self.repo, self.v1, pattern, limit=10_000)
            self.assertEqual(r["matches"], self.scan(self.v1, pattern), pattern)
        no_literal = grep(self.repo, self.v1, r"\d\d\d$", limit=10_000)  # no 3-character literal: a full scan
        self.assertFalse(no_literal["indexed"])
        self.assertEqual(no_literal["files_scanned"], 600)
        self.assertEqual(no_literal["matches"], self.scan(self.v1, r"\d\d\d$"))
        indexed_scans = grep(self.repo, self.v1, "omega omega", limit=10_000)["files_scanned"]
        self.assertLess(indexed_scans, 600)

    def test_T_SR_02_non_ascii_and_line_breaks_match_git(self):
        """Review findings I-04 and I-05: case folding has no context (a final sigma, a dotted
        capital I), and a form feed or a lone carriage return is part of a line, as git counts."""
        files = {"i18n/el.json": "ΚΟΣΜΟΣ\n", "i18n/tr.json": "İptal\nİSTANBUL\n",
                 "src/x.c": "a\n\x0cint needle_value = 1;\n", "src/crlf.txt": "one\r\r\ntwo needle\r\r\n"}
        cs = self.repo.create_changeset([self.v2], [{"path": p, "content": t.encode()} for p, t in files.items()], "a", "v3")
        r = grep(self.repo, cs, "ΚΟΣ")
        self.assertTrue(r["indexed"])
        self.assertEqual([(m["path"], m["line"]) for m in r["matches"]], [("i18n/el.json", 1)])
        for query in ("iptal", "istanbul"):
            r = grep(self.repo, cs, query, ignore_case=True)
            self.assertEqual([m["path"] for m in r["matches"]], ["i18n/tr.json"], query)
        r = grep(self.repo, cs, "needle")
        self.assertEqual([(m["path"], m["line"]) for m in r["matches"]], [("src/crlf.txt", 2), ("src/x.c", 2)])
        self.assertEqual(r["matches"], self.scan(cs, "needle"))

    def test_required_literals(self):
        self.assertEqual(required_literals(r"foo\(\d+\)"), ["foo(", ")"])
        self.assertEqual(required_literals("abc?d"), ["ab", "d"])
        self.assertEqual(required_literals("a|bcd"), [])
        with self.assertRaises(ValueError):
            required_literals("(")

    def test_path_search_visits_few_trees(self):
        r = search_paths(self.repo, self.v1, "f599")
        self.assertEqual(r["paths"], ["d29/f599.txt"])
        self.assertLess(r["trees_visited"], 31)


if __name__ == "__main__":
    unittest.main()

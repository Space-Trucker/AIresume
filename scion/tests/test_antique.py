import base64
import os
import unittest

from helpers import Cluster, write
from scion.classify import classify_file
from scion.client import ServerApi
from scion.postmerge import deploy_gate, run_worker
from scion.rpc import RemoteError

REVIEW = {
    "review": {"rules": [
        {"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0}, "docs": {"approvals": 0}},
        {"prefix": "core", "owners": ["core-team"], "logic": {"approvals": 2, "owner_approvals": 1},
         "comment_only": {"approvals": 1}},
    ]},
    "groups": {"core-team": ["olga"]},
    "admins": ["root"],
}


class TestClassify(unittest.TestCase):
    def test_python(self):
        old = b"def f(x):\n    # add one\n    return x + 1\n"
        self.assertEqual(classify_file("a.py", old, b"def f(x):\n    # add 1 to x\n    return x + 1\n"), "comment_only")
        self.assertEqual(classify_file("a.py", old, b"def f(x):\n    return x + 1  # inc\n"), "comment_only")
        self.assertEqual(classify_file("a.py", old, b"def f(x):\n    # add one\n    return x + 2\n"), "logic")
        self.assertEqual(classify_file("a.py", old, b"def f(x):\n  # add one\n  return x + 1\n"), "logic")  # indent
        self.assertEqual(classify_file("a.py", b"s = '# not a comment'\n", b"s = '# changed'\n"), "logic")

    def test_c_like(self):
        old = b"int f() {\n  /* block */\n  return 1; // one\n}\n"
        self.assertEqual(classify_file("a.c", old, b"int f() {\n  /* new block\n  spanning */\n  return 1;\n}\n"),
                         "comment_only")
        self.assertEqual(classify_file("a.ts", b'const s = "// x";\n', b'const s = "// y";\n'), "logic")
        self.assertEqual(classify_file("a.go", old, b"int f() { return 1; }\n"), "comment_only")  # whitespace only

    def test_docs_binary_unknown(self):
        self.assertEqual(classify_file("README.md", b"a", b"b"), "docs")
        self.assertEqual(classify_file("docs/x.py", b"a", b"b"), "docs")
        self.assertEqual(classify_file("blob.bin", b"\0", b"\1"), "logic")
        self.assertEqual(classify_file("a.py", b"x=1\n", b"x=1\n", "f", "x"), "logic")  # mode change


class AntiqueCase(unittest.TestCase):
    def setUp(self):
        self.c = Cluster(policy=REVIEW)
        self.c.seed({"app/main.py": b"def main():\n    return 1\n", "core/engine.py": b"X = 1\n",
                     "README.md": b"hello\n"})
        self.alice = ServerApi(self.c.server.url, "alice")
        self.bob = ServerApi(self.c.server.url, "bob")
        self.olga = ServerApi(self.c.server.url, "olga")

    def tearDown(self):
        self.c.close()

    def change(self, api, files, parent="main", msg="change"):
        return api.create_changeset(parents=[parent], message=msg, files=[
            {"path": p, "content_b64": base64.b64encode(c).decode()} for p, c in files.items()])["id"]


class TestReviewRules(AntiqueCase):
    def test_comment_and_docs_changes_need_no_approval(self):
        head = self.change(self.alice, {"app/main.py": b"def main():\n    # entry point\n    return 1\n",
                                        "README.md": b"hello world\n"})
        cr = self.alice.antique__create(title="comments", head=head)
        req = cr["requirements"]
        self.assertTrue(req["satisfied"])
        self.assertEqual({f["category"] for g in req["groups"] for f in g["files"]}, {"comment_only", "docs"})
        landed = self.alice.antique__land(id=cr["id"])
        self.assertEqual(landed["state"], "landed")

    def test_logic_changes_need_approval_and_self_approval_does_not_count(self):
        head = self.change(self.alice, {"app/main.py": b"def main():\n    return 2\n"})
        cr = self.alice.antique__create(title="logic", head=head)
        self.assertFalse(cr["requirements"]["satisfied"])
        self.alice.antique__approve(id=cr["id"])
        with self.assertRaises(RemoteError) as cm:
            self.alice.antique__land(id=cr["id"])
        self.assertEqual(cm.exception.status, 403)
        self.bob.antique__approve(id=cr["id"])
        self.assertEqual(self.alice.antique__land(id=cr["id"])["state"], "landed")

    def test_owners_for_sensitive_directories(self):
        head = self.change(self.alice, {"core/engine.py": b"X = 2\n"})
        cr = self.alice.antique__create(title="core", head=head)
        self.bob.antique__approve(id=cr["id"])
        ServerApi(self.c.server.url, "carl").antique__approve(id=cr["id"])
        req = self.alice.antique__requirements(id=cr["id"])
        self.assertFalse(req["satisfied"])  # two approvals, but none from an owner
        self.olga.antique__approve(id=cr["id"])
        self.assertTrue(self.alice.antique__requirements(id=cr["id"])["satisfied"])

    def test_new_revision_resets_approvals(self):
        head = self.change(self.alice, {"app/main.py": b"def main():\n    return 2\n"})
        cr = self.alice.antique__create(title="r", head=head)
        self.bob.antique__approve(id=cr["id"])
        head2 = self.change(self.alice, {"app/main.py": b"def main():\n    return 3\n"}, parent=head)
        cr = self.alice.antique__update(id=cr["id"], head=head2)
        self.assertFalse(cr["requirements"]["satisfied"])


class TestLanding(AntiqueCase):
    def test_lock_free_landing_rebases_and_indexes(self):
        h1 = self.change(self.alice, {"app/a.py": b"A = 1\n"})
        h2 = self.change(self.bob, {"app/b.py": b"B = 1\n"})
        cr1 = self.alice.antique__create(title="a", head=h1)
        cr2 = self.bob.antique__create(title="b", head=h2)
        for cr, other in ((cr1, self.bob), (cr2, self.alice)):
            other.antique__approve(id=cr["id"])
        self.alice.antique__land(id=cr1["id"])
        landed2 = self.bob.antique__land(id=cr2["id"])  # main moved: rebased on the server
        self.assertNotEqual(landed2["landed_cs"], h2)
        main = self.c.repo.get_ref("main")
        self.assertEqual(main, landed2["landed_cs"])
        files = {p for p, _, _ in self.c.repo.trees.walk(self.c.repo.root_tree(main))}
        self.assertTrue({"app/a.py", "app/b.py"} <= files)
        # "When did this merge?" is an index lookup, by landed id or by original id.
        by_new = self.alice.antique__find_landing(cs=landed2["landed_cs"])
        by_old = self.alice.antique__find_landing(cs=h2)
        self.assertEqual(by_new["cr"], cr2["id"])
        self.assertEqual(by_old["cs"], landed2["landed_cs"])
        self.assertIsNone(self.alice.antique__find_landing(cs=self.c.repo.resolve("main~2")))

    def test_conflicts_are_structured(self):
        h1 = self.change(self.alice, {"app/main.py": b"def main():\n    return 10\n"})
        h2 = self.change(self.bob, {"app/main.py": b"def main():\n    return 20\n"})
        cr1 = self.alice.antique__create(title="a", head=h1)
        cr2 = self.bob.antique__create(title="b", head=h2)
        self.bob.antique__approve(id=cr1["id"])
        self.alice.antique__approve(id=cr2["id"])
        self.alice.antique__land(id=cr1["id"])
        with self.assertRaises(RemoteError) as cm:
            self.bob.antique__land(id=cr2["id"])
        self.assertEqual(cm.exception.status, 409)
        self.assertEqual(cm.exception.data["conflicts"][0]["path"], "app/main.py")
        self.assertEqual(self.bob.antique__get(id=cr2["id"])["state"], "conflict")
        # The author (or an agent) resolves on top of the new main and uploads a revision.
        fixed = self.change(self.bob, {"app/main.py": b"def main():\n    return 30\n"}, parent="main")
        self.bob.antique__update(id=cr2["id"], head=fixed)
        self.alice.antique__approve(id=cr2["id"])
        self.assertEqual(self.bob.antique__land(id=cr2["id"])["state"], "landed")

    def test_html_view(self):
        h = self.change(self.alice, {"app/x.py": b"x = 1\n"})
        cr = self.alice.antique__create(title="<b>escaped</b>", head=h)
        status, _, body = self.alice.rpc.request("GET", f"/antique/cr/{cr['id']}")
        self.assertEqual(status, 200)
        self.assertIn(b"&lt;b&gt;escaped&lt;/b&gt;", body)
        self.assertIn(b"+x = 1", body)


class TestPostMergePipeline(AntiqueCase):
    def land(self, api, files, title):
        head = self.change(api, files)
        cr = api.antique__create(title=title, head=head)
        (self.bob if api is self.alice else self.alice).antique__approve(id=cr["id"])
        return api.antique__land(id=cr["id"])

    def test_worker_auto_revert_and_deploy_gate(self):
        ok1 = self.land(self.alice, {"app/feature.py": b"FEATURE = True\n"}, "feature")
        bad = self.land(self.bob, {"BROKEN": b"1\n"}, "breaks the build")
        workdir = os.path.join(self.c.tmp, "pm")
        results = run_worker(self.c.server.url, workdir, "test ! -e BROKEN", objects=self.c.objects_url,
                             once=True, auto_revert=True, log=lambda m: None)
        # feature passes, the breaking change fails and is reverted, and the revert (which was
        # itself queued for post-merge testing when it landed) passes.
        self.assertEqual([r["passed"] for r in results], [True, False, True])
        self.assertEqual(results[0]["cs"], ok1["landed_cs"])
        self.assertEqual(len(results[1]["reverted_with"]), 1)
        main = self.c.repo.get_ref("main")
        self.assertEqual(results[2]["cs"], main)
        files = {p for p, _, _ in self.c.repo.trees.walk(self.c.repo.root_tree(main))}
        self.assertNotIn("BROKEN", files)
        self.assertIn("app/feature.py", files)
        self.assertEqual(self.c.repo.get_changeset(main).extra["reverts"], bad["landed_cs"])
        self.assertEqual(deploy_gate(self.alice)["cs"], main)
        self.assertEqual(self.alice.antique__find_landing(cs=main)["ref"], "main")


if __name__ == "__main__":
    unittest.main()

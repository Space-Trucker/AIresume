"""Antique: classification (T-RV-01), review rules (T-RV-02…05), landing (T-LD-01…03), the review
pages (T-RV-06/07) and notifications (T-RV-08). WP-B3.2…B3.4."""
import base64
import http.client
import json
import re
import shutil
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import mock
from urllib.parse import urlencode, urlparse

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.classify import COMMENT_ONLY, DOCS, LOGIC, classify_file
from scion.rpc import RemoteError


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


class TestClassify(unittest.TestCase):
    """T-RV-01 (FR-RV-05): Python, C-like, docs, binary, mode, and the conservative cases."""

    def check(self, path, old, new, want, kinds=("f", "f")):
        self.assertEqual(classify_file(path, old, new, *kinds), want, f"{path}: {old!r} -> {new!r}")

    def test_T_RV_01_classifier(self):
        self.check("a.py", b"x = 1  # one\n", b"x = 1  # uno\n", COMMENT_ONLY)
        self.check("a.py", b"x = 1\n", b"# a new comment\nx = 1\n\n", COMMENT_ONLY)
        self.check("a.py", b"x = '#not a comment'\n", b"x = '#changed'\n", LOGIC)
        self.check("a.py", b"def f():\n    return 1\n", b"def f():\n  return 1\n", LOGIC)  # indentation matters
        self.check("a.py", b'"""doc"""\n', b'"""changed doc"""\n', LOGIC)  # docstrings are values
        self.check("a.c", b"int x; // a\n", b"int x; // b\n", COMMENT_ONLY)
        self.check("a.c", b"int x; /* a */\n", b"int x; /* b\n   c */\n", COMMENT_ONLY)
        self.check("a.c", b'char *s = "/* no */";\n', b'char *s = "/* yes */";\n', LOGIC)
        self.check("a.go", b"x := 1\n", b"x := 2\n", LOGIC)
        self.check("a.js", b"// header\nf()\n", b"// another header\nf()\n", COMMENT_ONLY)
        # a "//" after code may be a regular expression in JavaScript: unsure means logic
        self.check("a.js", b"const r = /\\/\\//; a()\n", b"const r = /\\/\\//; b()\n", LOGIC)
        self.check("a.sh", b"echo hi  # c1\n", b"echo hi  # c2\n", COMMENT_ONLY)
        self.check("a.sh", b"echo $# args\n", b"echo $# other\n", LOGIC)  # "$#" is not a comment
        self.check("docs/guide.md", b"a", b"b", DOCS)
        self.check("docs/guide.html", b"<p>a</p>", b"<p>b</p>", LOGIC)  # not docs because of its directory
        self.check("README.md", b"a", b"b", DOCS)
        self.check("a.py", b"\x00\x01", b"\x00\x02", LOGIC)  # binary
        self.check("a.py", b"x = 1\n", b"x = 1\n", LOGIC, kinds=("f", "x"))  # a mode change
        self.check("a.py", None, b"# only comments\n", LOGIC)  # an added file
        self.check("a.unknown", b"a", b"b", LOGIC)
        self.check("a.py", b"x = '''open\n", b"x = '''open more\n", LOGIC)  # unterminated: unsure

    def test_T_RV_10_comments_that_tools_read_are_code(self):
        """Review finding A-05: comments a compiler, interpreter or parser reads, whitespace that is
        structure, and manifests that live next to documentation."""
        self.check("auth.c", b"int f(int u) {\n  // admins only\n  if (!u) return 1;\n}\n",
                   b"int f(int u) {\n  // admins only \\\n  if (!u) return 1;\n}\n", LOGIC)  # the comment swallows a line
        self.check("deploy.yml", b"a:\n  auth: true\nc: 1\n", b"a:\nauth: true\nc: 1\n", LOGIC)  # YAML structure
        self.check("deploy.yml", b"a:  # x\n  auth: true\n", b"a:  # y\n  auth: true\n", COMMENT_ONLY)
        self.check("setup.cfg", b"[x]\nk = a\n  b\n", b"[x]\nk = a\nb\n", LOGIC)  # a continuation line
        self.check("Makefile", b"all:\n\techo hi\n", b"all:\n    echo hi\n", LOGIC)  # recipes start with a tab
        self.check("tools/release.sh", b"#!/bin/sh\nmake\n", b"#!/usr/bin/env -S sh -c 'curl x | sh'\nmake\n", LOGIC)
        self.check("tools/release.sh", b"#!/bin/sh\n# a\nmake\n", b"#!/bin/sh\n# b\nmake\n", COMMENT_ONLY)
        self.check("a.py", b"# -*- coding: utf-8 -*-\nx = 1\n", b"# -*- coding: latin-1 -*-\nx = 1\n", LOGIC)
        self.check("Dockerfile", b"# syntax=docker/dockerfile:1\nFROM python\n", b"# syntax=evil/frontend\nFROM python\n",
                   LOGIC)  # a parser directive picks the build frontend
        self.check("Dockerfile", b"FROM python\n# install\nRUN make\n", b"FROM python\n# build\nRUN make\n", COMMENT_ONLY)
        self.check("Dockerfile", b"FROM python\nENV A=b # c\n", b"FROM python\nENV A=b # d\n", LOGIC)  # part of the value
        self.check("a.go", b"//go:build linux\npackage a\n", b"//go:build windows\npackage a\n", LOGIC)
        self.check("a.go", b'// #include <a.h>\nimport "C"\n', b'// #include <b.h>\nimport "C"\n', LOGIC)  # cgo
        self.check("a.go", b"// doc\npackage a\n", b"// docs\npackage a\n", COMMENT_ONLY)
        self.check("a.c", b'puts("a  b");\n', b'puts("a b");\n', LOGIC)  # whitespace inside a string
        self.check("a.py", b'x = """a\n\nb"""\n', b'x = """a\nb"""\n', LOGIC)
        self.check("a.c", b"int/**/x;\n", b"intx;\n", LOGIC)  # a comment separates tokens
        for path in ("requirements.txt", "docs/requirements.txt", "docs/conf.py", "src/api/docs/views.py", "notes.txt"):
            self.assertNotEqual(classify_file(path, b"a = 1\n", b"a = 2\n", "f", "f"), DOCS, path)
        self.check("LICENSE", b"a", b"b", DOCS)
        self.check("docs/CHANGES.txt", b"a", b"b", DOCS)


class AntiqueTest(unittest.TestCase):
    policy = {"read": ["*"], "write": ["*"], "protected_refs": {"main": ["antique"]},
              "review": {"rules": [
                  {"prefix": "", "logic": {"approvals": 1}, "comment_only": {"approvals": 0}, "docs": {"approvals": 0}},
                  {"prefix": "secure", "owners": ["sec-team"], "logic": {"approvals": 2, "owner_approvals": 1},
                   "comment_only": {"approvals": 1}}]}}
    identity = {"groups": {"sec-team": ["sam"]}, "admins": ["root"]}

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-antique-")
        self.c = Cluster(self.tmp, caches=0, repos={REPO: self.policy}, identity=self.identity)
        self.base = self.write("root", [], {"src/app.py": "def main():\n    return 1  # one\n",
                                           "secure/key.py": "KEY = 1\n", "docs/readme.md": "hello\n"}, ref_old=None)

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def api(self, user="alice"):
        return self.c.client(user)

    def call(self, user, method, **params):
        return self.api(user).call(method, repo=REPO, **params)

    def write(self, user, parents, files, message="m", ref_old="__no_ref__"):
        params = {"parents": parents, "message": message,
                  "files": [{"path": p, "delete": True} if c is None else {"path": p, "content_b64": b64(c)}
                            for p, c in files.items()]}
        if ref_old != "__no_ref__":  # only the initial import moves main directly, as an admin
            params["update_ref"] = {"name": "main", "old": ref_old}
            user = "root"
        r = self.call(user, "create_changeset", **params)
        return r["id"]

    def cr(self, user, files, title="change", parent=None):
        head = self.write(user, [parent or self.call(user, "resolve", rev="main")], files, title)
        return self.call(user, "antique.create", title=title, head=head)


class TestReviewRules(AntiqueTest):
    def test_T_RV_02_comment_and_docs_changes_need_no_approval(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 1  # uno\n", "docs/readme.md": "hi\n"})
        req = cr["requirements"]
        self.assertTrue(req["satisfied"])
        self.assertEqual({g["prefix"]: g["category"] for g in req["groups"]}, {"": "comment_only"})
        logic = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        self.assertFalse(logic["requirements"]["satisfied"])
        self.assertEqual(logic["requirements"]["groups"][0]["need"], {"approvals": 1, "owner_approvals": 0})

    def test_T_RV_03_self_approval_does_not_count(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        cr = self.call("alice", "antique.approve", id=cr["id"])
        self.assertFalse(cr["requirements"]["satisfied"])
        self.assertEqual(cr["requirements"]["approvers"], [])
        cr = self.call("bob", "antique.approve", id=cr["id"])
        self.assertTrue(cr["requirements"]["satisfied"])

    def test_T_RV_04_owner_approvals(self):
        cr = self.cr("alice", {"secure/key.py": "KEY = 2\n"})
        for user in ("bob", "carol"):
            cr = self.call(user, "antique.approve", id=cr["id"])
        g = cr["requirements"]["groups"][0]
        self.assertEqual((g["prefix"], g["category"], g["need"]), ("secure", "logic", {"approvals": 2, "owner_approvals": 1}))
        self.assertFalse(cr["requirements"]["satisfied"])
        cr = self.call("sam", "antique.approve", id=cr["id"])  # sam is in sec-team
        self.assertTrue(cr["requirements"]["satisfied"])
        self.assertEqual(cr["requirements"]["groups"][0]["have"], {"approvals": 3, "owner_approvals": 1})

    def test_T_RV_05_new_revision_resets_approvals(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        cr = self.call("bob", "antique.approve", id=cr["id"])
        self.assertTrue(cr["requirements"]["satisfied"])
        head2 = self.write("alice", [cr["head"]], {"src/app.py": "def main():\n    return 3\n"})
        cr = self.call("alice", "antique.update", id=cr["id"], head=head2)
        self.assertEqual(cr["revision"], 2)
        self.assertFalse(cr["requirements"]["satisfied"])
        with self.assertRaises(RemoteError) as e:  # only the author uploads revisions
            self.call("bob", "antique.update", id=cr["id"], head=head2)
        self.assertEqual(e.exception.status, 403)

    def test_T_RV_09_comments_are_stored_with_revision_path_and_line(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        cr = self.call("bob", "antique.comment", id=cr["id"], body="why 2?", path="src/app.py", line=2)
        self.assertEqual({k: cr["comments"][0][k] for k in ("rev", "user", "path", "line", "body")},
                         {"rev": 1, "user": "bob", "path": "src/app.py", "line": 2, "body": "why 2?"})


    def test_T_RV_12_approving_and_landing_are_for_the_revision_seen(self):
        """Review finding A-04: an approval or a landing for a revision that has been replaced is
        refused, and a revision that arrives while a CR lands stops the landing."""
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        head2 = self.write("alice", [cr["head"]], {"src/app.py": "def main():\n    return True\n"})
        self.call("alice", "antique.update", id=cr["id"], head=head2)
        with self.assertRaises(RemoteError) as e:  # bob reviewed revision 1
            self.call("bob", "antique.approve", id=cr["id"], rev=1)
        self.assertEqual(e.exception.status, 400)
        self.assertIn("replaced by revision 2", str(e.exception))
        self.assertEqual(self.call("bob", "antique.get", id=cr["id"])["approvals"], [])
        self.call("bob", "antique.approve", id=cr["id"], rev=2)
        with self.assertRaises(RemoteError):
            self.call("alice", "antique.land", id=cr["id"], rev=1)
        # a revision that arrives after the approvals were checked: the landing stops
        a = self.c.services[0].antique(REPO)
        real = a.requirements
        head3 = self.write("alice", [head2], {"src/app.py": "def main():\n    return 3\n"})

        def racing(cr_id):
            out = real(cr_id)
            if a.meta.cr_get(cr_id)["head"] != head3:  # once
                a.meta.cr_add_revision(cr_id, head3, "open", time.time())
            return out
        with mock.patch.object(a, "requirements", racing):
            with self.assertRaises(ValueError):
                a.land("alice", cr["id"])
        got = self.call("alice", "antique.get", id=cr["id"])
        self.assertEqual((got["state"], got["revision"], got["head"]), ("open", 3, head3))
        self.assertEqual(self.call("alice", "resolve", rev="main"), self.base)


class TestRestrictedReview(AntiqueTest):
    """Review findings A-01 and A-10: the approval rules see the files their readers can't; an
    approval counts for a scope only from someone who can read it; restricted paths stay hidden."""
    policy = {"read": ["*"], "write": ["*"], "protected_refs": {"main": ["antique"]},
              "paths": [{"prefix": "secrets", "read": ["sec-team"], "write": ["sec-team"]}],
              "review": {"rules": [{"prefix": "", "logic": {"approvals": 1}},
                                   {"prefix": "secrets", "owners": ["sec-team"],
                                    "logic": {"approvals": 2, "owner_approvals": 1}}]}}
    identity = {"groups": {"sec-team": ["sam", "sue"]}, "admins": ["root"]}

    def setUp(self):
        super().setUp()
        self.base = self.write("root", [self.base], {"secrets/keys.py": "ALLOW = []\n"}, ref_old=self.base)

    def test_T_RV_11_rules_see_restricted_files_and_count_only_readers(self):
        cr = self.cr("sam", {"secrets/keys.py": "ALLOW = ['sam']\n"})
        req = cr["requirements"]
        self.assertFalse(req["satisfied"])  # A-01: the server's own view of the diff is not filtered
        self.assertEqual([(g["prefix"], g["category"]) for g in req["groups"]], [("secrets", "logic")])
        bob_view = self.call("bob", "antique.get", id=cr["id"])["requirements"]["groups"]
        self.assertEqual([f["path"] for g in bob_view for f in g["files"]], [])  # bob can't read secrets/
        self.call("sue", "antique.approve", id=cr["id"])
        got = self.call("bob", "antique.approve", id=cr["id"])["requirements"]
        self.assertEqual(got["groups"][0]["have"], {"approvals": 1, "owner_approvals": 1})  # bob's doesn't count
        self.assertFalse(got["satisfied"])
        with self.assertRaises(RemoteError) as e:
            self.call("sam", "antique.land", id=cr["id"])
        self.assertEqual(e.exception.status, 403)
        self.assertTrue(self.call("root", "antique.approve", id=cr["id"])["requirements"]["satisfied"])
        self.call("sam", "antique.land", id=cr["id"])
        # A-10: a conflict under secrets/ shows bob no path, only how many are hidden
        other = self.cr("sue", {"secrets/keys.py": "ALLOW = ['sue']\n"}, parent=self.base)
        for user in ("sam", "root"):
            self.call(user, "antique.approve", id=other["id"])
        with self.assertRaises(RemoteError):
            self.call("sue", "antique.land", id=other["id"])
        self.assertEqual(self.call("sue", "antique.get", id=other["id"])["conflict"]["conflicts"][0]["path"],
                         "secrets/keys.py")
        seen = self.call("bob", "antique.get", id=other["id"])["conflict"]
        self.assertEqual((seen["conflicts"], seen["hidden"]), ([], 1))

    def test_T_RV_11_a_private_repository(self):
        tmp = tempfile.mkdtemp(prefix="scion-private-")
        policy = {"read": ["eng"], "write": ["eng"], "protected_refs": {"main": ["antique"]}}
        c = Cluster(tmp, caches=0, repos={REPO: policy}, identity={"admins": ["root"], "groups": {"eng": ["alice", "bob"]}})
        try:
            api = c.client("alice")
            base = c.client("root").call("create_changeset", repo=REPO, parents=[], message="m",
                                         update_ref={"name": "main", "old": None},
                                         files=[{"path": "app.py", "content_b64": b64("x = 1\n")}])["id"]
            head = api.call("create_changeset", repo=REPO, parents=[base], message="m",
                            files=[{"path": "app.py", "content_b64": b64("x = 2\n")}])["id"]
            cr = api.call("antique.create", repo=REPO, title="t", head=head)
            self.assertFalse(cr["requirements"]["satisfied"])  # was satisfied: nobody "could read" app.py
            with self.assertRaises(RemoteError):
                api.call("antique.land", repo=REPO, id=cr["id"])
        finally:
            c.close()
            shutil.rmtree(tmp, ignore_errors=True)


class TestLanding(AntiqueTest):
    def test_T_LD_01_lock_free_landing_and_landing_index(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        other = self.cr("bob", {"src/other.py": "x = 1\n"})
        self.call("carol", "antique.approve", id=other["id"])
        landed_other = self.call("bob", "antique.land", id=other["id"])
        self.assertEqual(landed_other["state"], "landed")
        tip = self.call("alice", "resolve", rev="main")
        self.assertEqual(tip, landed_other["landed_cs"])
        with self.assertRaises(RemoteError) as e:  # requirements not met: 403 listing the unmet scopes
            self.call("alice", "antique.land", id=cr["id"])
        self.assertEqual(e.exception.status, 403)
        self.assertIn('"prefix": ""', str(e.exception))
        self.call("bob", "antique.approve", id=cr["id"])
        landed = self.call("alice", "antique.land", id=cr["id"])
        self.assertEqual(landed["state"], "landed")
        new_tip = self.call("alice", "resolve", rev="main")
        self.assertEqual(new_tip, landed["landed_cs"])
        self.assertTrue(self.call("alice", "is_ancestor", a=tip, b=new_tip))  # rebased onto the old tip
        self.assertNotEqual(new_tip, cr["head"])
        log = self.call("alice", "ref_log", name="main", limit=2)
        self.assertEqual([(r["old"], r["new"], r["who"]) for r in log][0], (tip, new_tip, "antique"))
        # FR-LD-05: indexed by the landed id and by the pre-rebase id
        for key in (new_tip, cr["head"]):
            found = self.call("alice", "antique.find_landing", cs=key)
            self.assertEqual((found["cs"], found["source"], found["cr"], found["ref"]), (new_tip, cr["head"], cr["id"], "main"))
        self.assertIsNone(self.call("alice", "antique.find_landing", cs=self.base))
        # FR-LD-07: every landing queues post-merge testing
        jobs = self.call("alice", "antique.postmerge_status", ref="main")
        self.assertEqual([(j["cs"], j["status"]) for j in jobs], [(new_tip, "queued"), (tip, "queued")])
        # landing is idempotent
        self.assertEqual(self.call("alice", "antique.land", id=cr["id"])["landed_cs"], new_tip)
        # main is protected: nobody else can move it directly (FR-REF-03)
        with self.assertRaises(RemoteError) as e:
            self.call("alice", "update_ref", name="main", old=new_tip, new=cr["head"])
        self.assertEqual(e.exception.status, 403)

    def test_T_LD_05_land_changeset_is_for_services_and_admins(self):
        head = self.write("alice", [self.base], {"src/fix.py": "fixed = True\n"})
        with self.assertRaises(RemoteError) as e:
            self.call("alice", "antique.land_changeset", cs=head, ref="main")
        self.assertEqual(e.exception.status, 403)
        r = self.call("root", "antique.land_changeset", cs=head, ref="main")
        self.assertEqual(self.call("alice", "resolve", rev="main"), r["landed_cs"])
        self.assertEqual(self.call("alice", "antique.find_landing", cs=head)["cr"], None)

    def test_T_PM_03_postmerge_jobs_are_for_services(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        self.call("bob", "antique.approve", id=cr["id"])
        landed = self.call("alice", "antique.land", id=cr["id"])
        with self.assertRaises(RemoteError) as e:
            self.call("alice", "antique.postmerge_claim")
        self.assertEqual(e.exception.status, 403)
        job = self.call("postmerge", "antique.postmerge_claim")
        self.assertEqual(job["cs"], landed["landed_cs"])
        self.assertIsNone(self.call("postmerge", "antique.postmerge_claim"))
        with self.assertRaises(RemoteError):
            self.call("alice", "antique.postmerge_report", id=job["id"], passed=True)
        self.assertEqual(self.call("postmerge", "antique.postmerge_report", id=job["id"], passed=True)["status"], "passed")

    def test_T_LD_02_structured_conflicts_and_resolution(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 'alice'\n"})
        theirs = self.cr("bob", {"src/app.py": "def main():\n    return 'bob'\n"})
        for x, approver in ((cr, "carol"), (theirs, "carol")):
            self.call(approver, "antique.approve", id=x["id"])
        self.call("bob", "antique.land", id=theirs["id"])
        with self.assertRaises(RemoteError) as e:
            self.call("alice", "antique.land", id=cr["id"])
        self.assertEqual((e.exception.status, e.exception.code), (409, "conflict"))
        self.assertEqual(e.exception.data["conflicts"][0]["path"], "src/app.py")
        self.assertIn("reason", e.exception.data["conflicts"][0])
        state = self.call("alice", "antique.get", id=cr["id"])
        self.assertEqual(state["state"], "conflict")
        self.assertEqual(state["conflict"]["conflicts"][0]["path"], "src/app.py")
        # the author resolves on top of main and uploads a new revision
        fixed = self.write("alice", [self.call("alice", "resolve", rev="main")],
                           {"src/app.py": "def main():\n    return 'alice and bob'\n"})
        state = self.call("alice", "antique.update", id=cr["id"], head=fixed)
        self.assertEqual(state["state"], "open")
        self.call("carol", "antique.approve", id=cr["id"])
        self.assertEqual(self.call("alice", "antique.land", id=cr["id"])["state"], "landed")
        self.assertEqual(base64.b64decode(self.call("alice", "read_file", rev="main", path="src/app.py")["content_b64"]),
                         b"def main():\n    return 'alice and bob'\n")

    def test_T_LD_03_landing_state_while_queued(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        self.call("bob", "antique.approve", id=cr["id"])
        repo = self.c.repo()
        entered, release = threading.Event(), threading.Event()
        real = repo.update_ref

        def slow_update_ref(*a, **kw):
            entered.set()
            release.wait(10)
            return real(*a, **kw)

        result = {}
        with mock.patch.object(repo, "update_ref", slow_update_ref):
            t = threading.Thread(target=lambda: result.update(self.call("alice", "antique.land", id=cr["id"])))
            t.start()
            self.assertTrue(entered.wait(10))
            self.assertEqual(self.call("bob", "antique.get", id=cr["id"])["state"], "landing")
            self.assertEqual([x["id"] for x in self.call("bob", "antique.list", state="landing")], [cr["id"]])
            release.set()
            t.join(10)
        self.assertEqual(result["state"], "landed")

    def test_T_LD_04_concurrent_landings_on_one_server_group_commit(self):
        crs = [self.cr(f"user{i}", {f"src/f{i}.py": f"x = {i}\n"}) for i in range(8)]
        for x in crs:
            self.call("reviewer", "antique.approve", id=x["id"])
        results, threads = [], []
        for x in crs:
            t = threading.Thread(target=lambda x=x: results.append(self.call(x["author"], "antique.land", id=x["id"])))
            threads.append(t)
            t.start()
        for t in threads:
            t.join(30)
        self.assertEqual(sorted(r["state"] for r in results), ["landed"] * 8)
        tree = {e["name"] for e in self.call("alice", "list_dir", rev="main", path="src")}
        self.assertTrue({f"f{i}.py" for i in range(8)} <= tree)
        counters = self.c.services[0].antique(REPO).counters
        self.assertLessEqual(counters["land.batches"], 8)
        self.assertEqual(counters["land.landed"], 8)

    def test_T_LD_06_merging_the_target_into_a_change_keeps_the_main_line(self):
        """Review finding A-02: a CR whose head merges the target in (the tip is its second parent)
        is replayed, not fast-forwarded: main's first-parent chain keeps every landing, and the
        landing index holds only the CR's own changesets."""
        mine = self.write("alice", [self.base], {"src/app.py": "def main():\n    return 'alice'\n"})
        cr = self.call("alice", "antique.create", title="alice", head=mine)
        bob = self.cr("bob", {"src/b.py": "b = 1\n"})
        self.call("carol", "antique.approve", id=bob["id"])
        bob_cs = self.call("bob", "antique.land", id=bob["id"])["landed_cs"]
        merged = self.call("alice", "merge", ours=mine, theirs="main", message="merge main into my change")
        self.call("alice", "antique.update", id=cr["id"], head=merged)
        self.call("carol", "antique.approve", id=cr["id"])
        landed = self.call("alice", "antique.land", id=cr["id"])["landed_cs"]
        self.assertNotEqual(landed, merged)
        self.assertEqual(self.call("x", "log", rev="main", ids_only=True), [landed, bob_cs, self.base])
        self.assertEqual(self.call("x", "get_changeset", rev=landed)["parents"], [bob_cs])
        self.assertEqual(self.call("x", "antique.landing_stack", cs=landed), [landed])
        self.assertIsNone(self.call("x", "antique.find_landing", cs=self.base))
        self.assertEqual(self.call("x", "antique.find_landing", cs=mine)["cs"], landed)  # by its pre-rebase id
        names = {e["name"] for e in self.call("x", "list_dir", rev="main", path="src")}
        self.assertEqual(names, {"app.py", "b.py"})
        # a merge whose first parent is the tip is a fast-forward
        side = self.write("dave", [self.base], {"src/d.py": "d = 1\n"})
        ff = self.call("dave", "merge", ours=landed, theirs=side, message="merge my side branch")
        cr2 = self.call("dave", "antique.create", title="dave", head=ff)
        self.call("carol", "antique.approve", id=cr2["id"])
        self.assertEqual(self.call("dave", "antique.land", id=cr2["id"])["landed_cs"], ff)
        # P-06: landing onto a new ref indexes only the CR's head, not the history beneath it
        fix = self.write("alice", [ff], {"src/fix.py": "fix = 1\n"})
        cr3 = self.call("alice", "antique.create", title="fix", head=fix, target="release-1")
        self.call("root", "antique.land", id=cr3["id"], force=True)
        self.assertEqual(self.call("x", "antique.landing_stack", cs=fix), [fix])
        self.assertEqual(self.call("x", "antique.find_landing", cs=landed)["ref"], "main")

    def test_T_LD_07_a_failing_request_does_not_stall_its_batch(self):
        """Review finding A-03: a request whose landing fails with something other than a conflict
        fails alone; the rest of its batch lands, no thread is left waiting, and the CR can be
        landed again."""
        crs = [self.cr(f"user{i}", {f"src/f{i}.py": f"x = {i}\n"}) for i in range(3)]
        for x in crs:
            self.call("reviewer", "antique.approve", id=x["id"])
        a, repo = self.c.services[0].antique(REPO), self.c.repo()
        entered, release, real_ref, real_rebase = threading.Event(), threading.Event(), repo.update_ref, repo.rebase

        def slow_update_ref(*args, **kw):  # the first landing holds the leader slot until the others queue
            entered.set()
            release.wait(10)
            return real_ref(*args, **kw)

        def broken_rebase(head, onto, *args, **kw):
            if head == crs[1]["head"]:
                raise OSError("disk trouble")
            return real_rebase(head, onto, *args, **kw)

        results = {}

        def land(x):
            try:
                results[x["id"]] = a.land(x["author"], x["id"], timeout=10)["state"]
            except Exception as e:  # noqa: BLE001
                results[x["id"]] = type(e).__name__

        with mock.patch.object(repo, "update_ref", slow_update_ref), mock.patch.object(repo, "rebase", broken_rebase):
            threads = [threading.Thread(target=land, args=(crs[0],))]
            threads[0].start()
            self.assertTrue(entered.wait(10))
            threads += [threading.Thread(target=land, args=(x,)) for x in crs[1:]]
            for t in threads[1:]:
                t.start()
            deadline = time.time() + 10
            while a.queue_depth() < 2 and time.time() < deadline:
                time.sleep(0.01)
            release.set()
            for t in threads:
                t.join(15)
        self.assertFalse(any(t.is_alive() for t in threads))
        self.assertEqual(results, {crs[0]["id"]: "landed", crs[1]["id"]: "OSError", crs[2]["id"]: "landed"})
        self.assertEqual(self.call("x", "antique.get", id=crs[1]["id"])["state"], "open")
        self.assertEqual(self.call(crs[1]["author"], "antique.land", id=crs[1]["id"])["state"], "landed")

    def test_T_LD_08_the_ref_moves_with_its_landing_records_or_not_at_all(self):
        """The ref's compare-and-swap, the landing index, the post-merge job and the CR's state are
        one transaction: when it fails, nothing changed and the CR can land again."""
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        self.call("bob", "antique.approve", id=cr["id"])
        meta = self.c.repo().meta
        with mock.patch.object(meta, "_record_landings", side_effect=OSError("metadata store failure")):
            with self.assertRaises(RemoteError):
                self.call("alice", "antique.land", id=cr["id"])
        self.assertEqual(self.call("x", "resolve", rev="main"), self.base)
        self.assertEqual(self.call("x", "antique.postmerge_status", ref="main"), [])
        self.assertEqual(self.call("x", "antique.get", id=cr["id"])["state"], "open")
        self.assertIsNone(self.call("x", "antique.find_landing", cs=cr["head"]))
        landed = self.call("alice", "antique.land", id=cr["id"])
        self.assertEqual(self.call("x", "antique.postmerge_status", ref="main")[0]["cs"], landed["landed_cs"])

    def test_T_LD_09_targets_antique_may_not_move_and_stale_landings(self):
        tmp = tempfile.mkdtemp(prefix="scion-release-")
        policy = {"read": ["*"], "write": ["*"], "protected_refs": {"main": ["antique"], "release/*": ["rel"]}}
        c = Cluster(tmp, caches=0, repos={REPO: policy}, identity={"admins": ["root"], "groups": {"rel": ["rita"]}})
        try:
            api = c.client("rita")
            base = c.client("root").call("create_changeset", repo=REPO, parents=[], message="m",
                                         update_ref={"name": "main", "old": None},
                                         files=[{"path": "app.py", "content_b64": b64("x = 1\n")}])["id"]
            api.call("create_release", repo=REPO, name="1.0", rev=base)
            fix = api.call("create_changeset", repo=REPO, parents=[base], message="fix",
                           files=[{"path": "app.py", "content_b64": b64("x = 2\n")}])["id"]
            cr = api.call("antique.create", repo=REPO, title="fix for 1.0", head=fix, target="release/1.0")
            c.client("carol").call("antique.approve", repo=REPO, id=cr["id"])
            with self.assertRaises(RemoteError) as e:  # refused up front, not stuck in "landing"
                api.call("antique.land", repo=REPO, id=cr["id"])
            self.assertEqual(e.exception.status, 403)
            self.assertEqual(api.call("antique.get", repo=REPO, id=cr["id"])["state"], "open")
            # a CR left "landing" by a server that stopped can be landed or abandoned again
            cr2 = api.call("antique.create", repo=REPO, title="stuck", head=fix)
            c.client("carol").call("antique.approve", repo=REPO, id=cr2["id"])
            meta = c.repo().meta
            meta.cr_update(cr2["id"], state="landing", updated=time.time() - 60)
            with self.assertRaises(RemoteError):  # not yet stale
                api.call("antique.abandon", repo=REPO, id=cr2["id"])
            meta.cr_update(cr2["id"], updated=time.time() - 3600)
            self.assertEqual(api.call("antique.land", repo=REPO, id=cr2["id"])["state"], "landed")
        finally:
            c.close()
            shutil.rmtree(tmp, ignore_errors=True)


class TestReviewPages(AntiqueTest):
    """T-RV-06/07: the review pages, with escaping, inline comments and CSRF."""

    def http(self, method, path, body=None, cookie=None):
        u = urlparse(self.c.server_urls[0])
        conn = http.client.HTTPConnection(u.hostname, u.port, timeout=30)
        headers = {}
        if body is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            body = urlencode(body)
        if cookie:
            headers["Cookie"] = cookie
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read().decode()
        conn.close()
        return resp.status, dict(resp.getheaders()), data

    def login(self, user):
        status, headers, _ = self.http("POST", "/antique/login", {"user": user})
        self.assertEqual(status, 303)
        cookie = headers["Set-Cookie"].split(";")[0]
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", headers["Set-Cookie"])
        return cookie

    def test_T_RV_06_cr_page_escapes_and_shows_the_diff(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return '<b>2</b>'\n"}, title="<script>alert(1)</script>")
        self.assertEqual(self.http("GET", f"/antique/{REPO}/cr/{cr['id']}")[0], 303)  # sign in first
        cookie = self.login("bob")
        status, headers, page = self.http("GET", f"/antique/{REPO}/cr/{cr['id']}", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("+    return &#x27;&lt;b&gt;2&lt;/b&gt;&#x27;", page)
        self.assertIn("Approval requirements", page)
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        status, _, index = self.http("GET", f"/antique?repo={REPO}", cookie=cookie)
        self.assertIn(f"/antique/{REPO}/cr/{cr['id']}", index)

    def test_T_RV_07_approve_comment_and_land_from_the_pages(self):
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        bob = self.login("bob")
        page = self.http("GET", f"/antique/{REPO}/cr/{cr['id']}", cookie=bob)[2]
        csrf = re.search(r"name=csrf value='([^']+)'", page).group(1)
        base = f"/antique/{REPO}/cr/{cr['id']}"
        self.assertEqual(self.http("POST", base + "/approve", {"csrf": "forged"}, cookie=bob)[0], 403)
        self.assertEqual(self.http("POST", base + "/approve", {}, cookie=bob)[0], 403)
        self.assertEqual(self.http("POST", base + "/approve", {"csrf": csrf})[0], 401)  # no session
        self.assertEqual(self.call("alice", "antique.get", id=cr["id"])["approvals"], [])
        self.assertEqual(self.http("POST", base + "/approve", {"csrf": csrf}, cookie=bob)[0], 303)
        self.assertEqual(self.http("POST", base + "/comment",
                                   {"csrf": csrf, "body": "inline <note>", "path": "src/app.py", "line": "2"},
                                   cookie=bob)[0], 303)
        page = self.http("GET", base, cookie=bob)[2]
        row = page.index("+    return 2")
        self.assertGreater(page.index("inline &lt;note&gt;"), row, "the line comment sits under its line (D-04)")
        alice = self.login("alice")
        alice_csrf = re.search(r"name=csrf value='([^']+)'", self.http("GET", base, cookie=alice)[2]).group(1)
        self.assertEqual(self.http("POST", base + "/land", {"csrf": csrf}, cookie=alice)[0], 403)  # bob's token
        self.assertEqual(self.http("POST", base + "/land", {"csrf": alice_csrf}, cookie=alice)[0], 303)
        self.assertEqual(self.call("alice", "antique.get", id=cr["id"])["state"], "landed")

    def form(self, page: str, action: str) -> dict:
        """The hidden fields of the page's form posting to ``action``, as a browser would send them."""
        m = re.search(r"<form[^>]*action='[^']*/" + action + r"'>(.*?)</form>", page, re.S)
        return dict(re.findall(r"name=(\w+) value='([^']*)'", m.group(1)))

    def test_T_RV_12_the_pages_act_on_the_revision_they_show(self):
        """Review finding A-04 through the pages: bob's approve button is for the revision he read."""
        cr = self.cr("alice", {"src/app.py": "def main():\n    return 2\n"})
        bob = self.login("bob")
        base = f"/antique/{REPO}/cr/{cr['id']}"
        approve = self.form(self.http("GET", base, cookie=bob)[2], "approve")
        self.assertEqual(approve["rev"], "1")
        head2 = self.write("alice", [cr["head"]], {"src/app.py": "def main():\n    return True\n"})
        self.call("alice", "antique.update", id=cr["id"], head=head2)  # while bob reads revision 1
        status, _, page = self.http("POST", base + "/approve", approve, cookie=bob)
        self.assertEqual(status, 400)
        self.assertIn("replaced by revision 2", page)
        self.assertEqual(self.call("alice", "antique.get", id=cr["id"])["approvals"], [])

    def test_T_RV_13_a_landed_page_shows_the_whole_landing(self):
        """Review finding A-10: the diff of a landed CR covers every changeset it landed."""
        first = self.write("alice", [self.base], {"src/auth.py": "ok = 1\n"})
        second = self.write("alice", [first], {"src/app.py": "def main():\n    return 2\n"})
        cr = self.call("alice", "antique.create", title="two changesets", head=second)
        self.call("bob", "antique.approve", id=cr["id"])
        other = self.cr("carol", {"src/other.py": "o = 1\n"})  # main moves on: the landing is a rebase
        self.call("bob", "antique.approve", id=other["id"])
        self.call("carol", "antique.land", id=other["id"])
        self.call("alice", "antique.land", id=cr["id"])
        page = self.http("GET", f"/antique/{REPO}/cr/{cr['id']}", cookie=self.login("bob"))[2]
        self.assertIn("src/auth.py", page)
        self.assertIn("src/app.py", page)
        self.assertNotIn("src/other.py", page)


class TestReviewPageSessions(unittest.TestCase):
    def test_T_RV_14_a_revoked_token_ends_the_session(self):
        """Review finding A-10: removing a user's token from deployment.json ends their review
        sessions at the next request, as it refuses their RPCs."""
        tmp = tempfile.mkdtemp(prefix="scion-revoke-")
        tokens = {"root": "root-token", "mallory": "mallory-token"}
        c = Cluster(tmp, caches=0, repos={REPO: {"read": ["*"], "write": ["*"]}},
                    identity={"admins": ["root"], "tokens": dict(tokens)}, tokens=tokens)
        try:
            u = urlparse(c.server_urls[0])

            def req(method, path, body=None, cookie=None):
                conn = http.client.HTTPConnection(u.hostname, u.port, timeout=30)
                headers = {"Content-Type": "application/x-www-form-urlencoded"} if body is not None else {}
                if cookie:
                    headers["Cookie"] = cookie
                conn.request(method, path, body=None if body is None else urlencode(body), headers=headers)
                r = conn.getresponse()
                r.read()
                conn.close()
                return r.status, dict(r.getheaders())

            status, headers = req("POST", "/antique/login", {"user": "mallory", "token": "mallory-token"})
            self.assertEqual(status, 303)
            cookie = headers["Set-Cookie"].split(";")[0]
            self.assertEqual(req("GET", "/antique", cookie=cookie)[0], 200)
            with open(c.deployment.identity_path) as f:
                ident = json.load(f)
            del ident["tokens"]["mallory"]
            time.sleep(0.05)
            with open(c.deployment.identity_path, "w") as f:
                json.dump(ident, f)
            status, headers = req("GET", "/antique", cookie=cookie)
            self.assertEqual((status, headers.get("Location")), (303, "/antique/login"))
        finally:
            c.close()
            shutil.rmtree(tmp, ignore_errors=True)


class _Hook(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.events.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *a):
        pass


class _CutOff(BaseHTTPRequestHandler):
    """Promises a body it never sends: the client gets http.client.IncompleteRead."""

    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        self.send_response(200)
        self.send_header("Content-Length", "100")
        self.end_headers()
        self.wfile.write(b"abc")
        self.close_connection = True

    def log_message(self, *a):
        pass


class TestNotifications(unittest.TestCase):
    def test_T_RV_08_a_broken_endpoint_does_not_stop_notifications(self):
        """Review finding A-07: a reply cut short is a failed delivery, not the end of the thread."""
        from scion.notify import Notifier
        bad, good = HTTPServer(("127.0.0.1", 0), _CutOff), HTTPServer(("127.0.0.1", 0), _Hook)
        good.events = []
        for srv in (bad, good):
            threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            n = Notifier(lambda repo: [], attempts=1, timeout=5)
            n.send([f"http://127.0.0.1:{bad.server_address[1]}/"], {"n": 1})
            n.send([f"http://127.0.0.1:{good.server_address[1]}/"], {"n": 2})
            self.assertTrue(n.flush(10))
            self.assertEqual((n.counters["failed"], n.counters["delivered"], good.events), (1, 1, [{"n": 2}]))
            self.assertTrue(n._thread.is_alive())
        finally:
            for srv in (bad, good):
                srv.shutdown()
                srv.server_close()

    def test_T_RV_08_cr_events_reach_a_webhook(self):
        hook = HTTPServer(("127.0.0.1", 0), _Hook)
        hook.events = []
        threading.Thread(target=hook.serve_forever, daemon=True).start()
        tmp = tempfile.mkdtemp(prefix="scion-hook-")
        url = f"http://127.0.0.1:{hook.server_address[1]}/hook"
        c = Cluster(tmp, caches=0, repos={REPO: {"read": ["*"], "write": ["*"], "review": {"webhooks": [url]}}})
        try:
            api = c.client("alice")
            base = api.call("create_changeset", repo=REPO, parents=[], message="m",
                            files=[{"path": "a.py", "content_b64": b64("x = 1\n")}],
                            update_ref={"name": "main", "old": None})["id"]
            head = api.call("create_changeset", repo=REPO, parents=[base], message="m2",
                            files=[{"path": "a.py", "content_b64": b64("x = 2\n")}])["id"]
            cr = api.call("antique.create", repo=REPO, title="Please review", head=head)
            c.client("bob").call("antique.approve", repo=REPO, id=cr["id"])
            self.assertTrue(c.services[0].notifier.flush(10))
            events = [(e["event"], e["cr"]["id"]) for e in hook.events]
            self.assertEqual(events, [("cr.created", cr["id"]), ("cr.approved", cr["id"])])
            self.assertIn("Please review", hook.events[0]["text"])
            self.assertEqual(hook.events[0]["repo"], REPO)
        finally:
            c.close()
            hook.shutdown()
            hook.server_close()
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

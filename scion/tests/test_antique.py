"""Antique: classification (T-RV-01), review rules (T-RV-02…05), landing (T-LD-01…03), the review
pages (T-RV-06/07) and notifications (T-RV-08). WP-B3.2…B3.4."""
import base64
import http.client
import json
import re
import shutil
import tempfile
import threading
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
        self.check("docs/guide.html", b"<p>a</p>", b"<p>b</p>", DOCS)
        self.check("README.md", b"a", b"b", DOCS)
        self.check("a.py", b"\x00\x01", b"\x00\x02", LOGIC)  # binary
        self.check("a.py", b"x = 1\n", b"x = 1\n", LOGIC, kinds=("f", "x"))  # a mode change
        self.check("a.py", None, b"# only comments\n", LOGIC)  # an added file
        self.check("a.unknown", b"a", b"b", LOGIC)
        self.check("a.py", b"x = '''open\n", b"x = '''open more\n", LOGIC)  # unterminated: unsure


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


class _Hook(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.events.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *a):
        pass


class TestNotifications(unittest.TestCase):
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

"""IAM: tokens and delegation (B2); directory permissions, refs, re-indexing and audit (B3)."""
import base64
import json
import os
import shutil
import tempfile
import time
import unittest
import zlib

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.iam import Identity, hash_token
from scion.objects import F_DENIED, F_RESTRICTED, blob_id
from scion.rpc import RemoteError


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-iam-")
        self.c = Cluster(self.tmp, caches=0, identity={
            "tokens": {"alice": "alice-plain", "bob": hash_token("bob-secret"), "scion-cache": "cache-token"}},
            repos={REPO: {"read": ["alice", "scion-cache"], "write": ["alice"]}})

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T_IAM_08_token_authentication(self):
        self.assertEqual(self.c.client("alice", token="alice-plain").call("whoami")["via"], "token")
        self.assertEqual(self.c.client("bob", token="bob-secret").call("whoami")["user"], "bob")  # stored hashed
        for user, token in (("alice", ""), ("alice", "bob-secret"), ("bob", hash_token("bob-secret")),
                            ("", "alice-plain"), ("mallory", "anything")):
            with self.subTest(user=user, token=token), self.assertRaises(RemoteError) as e:
                self.c.client(user or None, token=token).call("whoami")
            self.assertEqual((e.exception.status, e.exception.code), (401, "unauthenticated"))

    def test_identity_checks(self):
        ident = Identity({"tokens": {"a": "t"}, "groups": {"g": ["b"]}, "admins": ["root"]})
        self.assertTrue(ident.check_token("a", "t"))
        self.assertFalse(ident.check_token("a", None))
        self.assertTrue(ident.matches("b", ["g"]))
        self.assertFalse(ident.matches(None, ["g"]))
        self.assertTrue(ident.matches(None, ["*"]))
        self.assertTrue(ident.is_service("scion-daemon"))
        self.assertFalse(ident.is_service("a"))

    def test_FR_IAM_08_service_principals_act_for_users(self):
        api = self.c.client("alice", token="alice-plain")
        api.call("create_changeset", repo=REPO, parents=[], message="m",
                 files=[{"path": "a.txt", "content_b64": base64.b64encode(b"private\n").decode()}],
                 update_ref={"name": "main", "old": None})
        oid = blob_id(b"private\n")
        cache = self.c.client("scion-cache", tier="cache", token="cache-token")
        [(_, flags, data)] = cache.get_objects(REPO, [oid], on_behalf="alice")
        self.assertEqual(flags, F_RESTRICTED)
        self.assertEqual(data[:2], b"x\x9c")
        [(_, flags, data)] = cache.get_objects(REPO, [oid], on_behalf="bob")  # bob's view, not the cache's
        self.assertEqual((flags, data), (F_DENIED, b""))
        # only service principals may act on behalf of someone else
        with self.assertRaises(RemoteError) as e:
            self.c.client("alice", token="alice-plain").get_objects(REPO, [oid], on_behalf="bob")
        self.assertEqual(e.exception.status, 403)


# ================================================================================================ B3
POLICY = {"read": ["*"], "write": ["*"],
          "paths": [{"prefix": "secrets", "read": ["sec-team"], "write": ["sec-team"]},
                    {"prefix": "secrets/public", "read": ["*"]},
                    {"prefix": "infra", "write": ["sre"]}],
          "protected_refs": {"main": ["antique", "maintainers"], "release/*": ["release-managers"]}}
IDENTITY = {"groups": {"sec-team": ["sam"], "sre": ["sally"], "maintainers": ["mona"], "release-managers": ["rita"]},
            "admins": ["root"]}
SECRET = "TOP-SECRET-KEY"


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


class DirectoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-iam3-")
        self.c = Cluster(self.tmp, repos={REPO: POLICY}, identity=IDENTITY)
        self.seed = self.commit("root", None, {"src/app.py": "print('app')\n", "secrets/key.txt": SECRET + "\n",
                                               "secrets/public/readme.txt": "public inside secrets\n",
                                               "infra/deploy.sh": "deploy\n"}, move_main=True)
        self.wcs = []

    def tearDown(self):
        for wc in self.wcs:
            wc.close()
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def call(self, user, method, **params):
        return self.c.client(user).call(method, repo=REPO, **params)

    def commit(self, user, parent, files, move_main=False, **extra):
        params = {"parents": [parent] if parent else [], "message": "m", **extra,
                  "files": [{"path": p, "content_b64": b64(c)} for p, c in files.items()]}
        if move_main:
            params["update_ref"] = {"name": "main", "old": parent}
        r = self.call(user, "create_changeset", **params)
        if move_main:
            self.assertTrue(r["ref_updated"])
        return r["id"]

    def clone(self, name, user, **kw):
        from scion.client import WorkingCopy
        wc = WorkingCopy.clone(os.path.join(self.tmp, name), self.c.server_urls[0], REPO,
                               objects=self.c.daemon_urls[0], user=user, **kw)
        self.wcs.append(wc)
        return wc

    def files(self, wc):
        out = set()
        for dp, dns, fns in os.walk(wc.root):
            dns[:] = [d for d in dns if d != ".scn"]
            out.update(os.path.relpath(os.path.join(dp, f), wc.root) for f in fns)
        return out

    def denied(self, fn):
        with self.assertRaises(RemoteError) as e:
            fn()
        self.assertEqual(e.exception.status, 403)
        return e.exception


class TestDirectoryPermissions(DirectoryTest):
    def test_T_IAM_01_clone_skips_unreadable_directories(self):
        bob = self.clone("bob", "bob")
        self.assertEqual(self.files(bob), {"src/app.py", "infra/deploy.sh", "secrets/public/readme.txt"})
        self.assertFalse(bob.status().dirty)
        sam = self.clone("sam", "sam")
        self.assertEqual(self.files(sam), {"src/app.py", "infra/deploy.sh", "secrets/public/readme.txt",
                                           "secrets/key.txt"})
        with open(os.path.join(sam.root, "secrets/key.txt")) as f:
            self.assertEqual(f.read(), SECRET + "\n")

    def test_T_IAM_02_public_bytes_stay_public_in_both_orders(self):
        daemon = lambda user: self.c.client(user, url=self.c.daemon_urls[0])  # noqa: E731
        first_secret = self.commit("sam", self.seed, {"secrets/a.txt": "shared bytes one\n"})
        oid_a = blob_id(b"shared bytes one\n")
        self.assertEqual(daemon("bob").get_objects(REPO, [oid_a])[0][1], F_DENIED)
        self.commit("alice", first_secret, {"src/a.txt": "shared bytes one\n"})  # the same bytes, now public
        self.assertEqual(daemon("bob").get_objects(REPO, [oid_a])[0][1], 0)
        first_public = self.commit("alice", self.seed, {"src/b.txt": "shared bytes two\n"})
        self.commit("sam", first_public, {"secrets/b.txt": "shared bytes two\n"})
        self.assertEqual(daemon("bob").get_objects(REPO, [blob_id(b"shared bytes two\n")])[0][1], 0)

    def test_T_IAM_03_every_read_path_is_filtered(self):
        self.denied(lambda: self.call("bob", "read_file", rev="main", path="secrets/key.txt"))
        self.denied(lambda: self.call("bob", "blame", rev="main", path="secrets/key.txt"))
        self.denied(lambda: self.call("bob", "file_history", rev="main", path="secrets/key.txt"))
        self.denied(lambda: self.call("bob", "log", rev="main", path="secrets/key.txt"))
        self.assertEqual([e["name"] for e in self.call("bob", "list_dir", rev="main", path="secrets")], ["public"])
        self.assertIn("secrets", [e["name"] for e in self.call("bob", "list_dir", rev="main", path="")])
        self.assertEqual(self.call("bob", "search_paths", rev="main", query="key")["paths"], [])
        self.assertEqual(self.call("sam", "search_paths", rev="main", query="key")["paths"], ["secrets/key.txt"])
        cs = self.call("bob", "get_changeset", rev=self.seed)
        self.assertNotIn("secrets/key.txt", [c["path"] for c in cs["changes"]])
        self.assertIn("secrets/public/readme.txt", [c["path"] for c in cs["changes"]])
        d = self.call("bob", "diff", b=self.seed, text=True)
        self.assertNotIn("secrets/key.txt", [f["path"] for f in d["files"]])
        # NFR-10: no response to bob contains the secret, whichever read path he tries
        responses = [self.call("bob", m, **p) for m, p in (
            ("get_changeset", {"rev": "main"}), ("diff", {"b": "main", "text": True}), ("log", {"rev": "main"}),
            ("list_dir", {"rev": "main", "path": "secrets"}), ("search_paths", {"rev": "main", "query": "secret"}),
            ("get_changesets", {"ids": [self.seed]}), ("grep", {"rev": "main", "pattern": "TOP-SECRET"}),
            ("grep", {"rev": "main", "pattern": r"[A-Z]+-\w+"}))]  # indexed and full-scan grep
        self.assertNotIn(SECRET, json.dumps(responses))
        self.assertEqual(self.call("sam", "grep", rev="main", pattern="TOP-SECRET")["matches"][0]["path"], "secrets/key.txt")
        self.assertIn(SECRET, json.dumps(self.call("sam", "diff", b="main", text=True)))

    def test_T_IAM_04_restricted_objects_through_every_tier(self):
        sam = self.clone("sam", "sam")
        repo = self.c.repo()
        secret_blob = blob_id((SECRET + "\n").encode())
        secret_tree = repo.lookup(repo.resolve("main"), "secrets")[1]
        daemon = self.c.daemon_services[0].source
        cache = self.c.cache_services[0].source
        for oid in (secret_blob, secret_tree):
            self.assertFalse(daemon.store.has(f"{REPO}/{oid}"), "the daemon must not keep restricted objects")
            self.assertFalse(cache.store.has(f"{REPO}/{oid}"), "the cache must not keep restricted objects")
            self.assertIn(f"{REPO}/{oid}", cache.restricted)
        self.assertTrue(cache.store.has(f"{REPO}/{blob_id(b'public inside secrets' + bytes([10]))}"))
        bob_view = self.c.client("bob", url=self.c.daemon_urls[0]).get_objects(REPO, [secret_blob, secret_tree])
        self.assertEqual([f for _, f, _ in bob_view], [F_DENIED, F_DENIED])
        sam_view = self.c.client("sam", url=self.c.daemon_urls[0]).get_objects(REPO, [secret_blob])
        self.assertEqual(sam_view[0][1], F_RESTRICTED)
        self.assertGreater(cache.counters["restricted_passthrough"], 0)
        # an object denied to anyone is never public: after one denial, tiers forward it without
        # counting a miss or touching their store (the hit rate superfans watch is about public objects)
        self.commit("sam", self.seed, {"secrets/only-sam.txt": "never fetched by sam\n"})
        fresh = blob_id(b"never fetched by sam\n")
        bob_daemon = self.c.client("bob", url=self.c.daemon_urls[0])
        before = daemon.counters["misses"], daemon.counters["restricted_passthrough"]
        self.assertEqual(bob_daemon.get_objects(REPO, [fresh])[0][1], F_DENIED)
        self.assertEqual(bob_daemon.get_objects(REPO, [fresh])[0][1], F_DENIED)
        self.assertEqual((daemon.counters["misses"], daemon.counters["restricted_passthrough"]),
                         (before[0] + 1, before[1] + 1))
        self.assertIn(f"{REPO}/{fresh}", daemon.restricted)
        store = self.c.daemon_services[0].source.store
        stored = b"".join(zlib.decompress(store.get_stored(key)) for key in store.iter_ids())
        self.assertTrue(stored)
        self.assertNotIn(SECRET.encode(), stored)

    def test_T_IAM_11_restricted_bytes_can_be_committed_by_someone_who_has_them(self):
        secret_blob = blob_id((SECRET + "\n").encode())
        # without the bytes, a restricted object can't be republished by its id
        self.denied(lambda: self.call("bob", "create_changeset", parents=[self.seed], message="m",
                                      files=[{"path": "src/leak.txt", "blob": secret_blob}]))
        # with them (an identical file, or an empty one), the client's upload proves possession
        bob = self.clone("bob", "bob")
        with open(os.path.join(bob.root, "src/same.txt"), "w") as f:
            f.write(SECRET + "\n")
        cs = bob.commit("bob has the same bytes", addremove=True)
        self.assertEqual(self.call("bob", "get_changeset", rev=cs)["changes"][0]["blob"], secret_blob)
        self.assertEqual(self.c.client("bob", url=self.c.daemon_urls[0]).get_objects(REPO, [secret_blob])[0][1], 0)

    def test_T_IAM_12_snapshots_leave_out_restricted_objects(self):
        from scion.snapshot import create_snapshot, load_snapshot
        from scion.storage import MemoryObjectStore
        out = os.path.join(self.tmp, "snaps")
        pointer = create_snapshot(self.c.repo(), "main", out)
        store = MemoryObjectStore()
        load_snapshot(os.path.join(out, pointer["file"]), store, REPO)
        repo = self.c.repo()
        secret_tree = repo.lookup(repo.resolve("main"), "secrets")[1]
        public_tree = repo.lookup(repo.resolve("main"), "secrets/public")[1]
        self.assertFalse(store.has(f"{REPO}/{blob_id((SECRET + chr(10)).encode())}"))
        self.assertFalse(store.has(f"{REPO}/{secret_tree}"))
        self.assertFalse(store.has(f"{REPO}/{public_tree}"), "beneath a restricted tree: not reachable by walking")
        self.assertTrue(store.has(f"{REPO}/{blob_id(b'deploy' + bytes([10]))}"))

    def test_T_IAM_05_write_permissions(self):
        before = self.c.repo().meta.count_changesets()
        self.commit("bob", self.seed, {"src/x.py": "x\n"})
        for user, path in (("bob", "secrets/x"), ("bob", "infra/x"), ("sam", "infra/x"), ("sally", "secrets/x")):
            with self.subTest(user=user, path=path):
                self.denied(lambda: self.commit(user, self.seed, {path: "x\n"}))
        self.commit("sally", self.seed, {"infra/x": "x\n"})
        self.commit("sam", self.seed, {"secrets/x": "x\n"})
        self.assertEqual(self.c.repo().meta.count_changesets(), before + 3)

    def test_T_IAM_06_protected_refs(self):
        head = self.commit("alice", self.seed, {"src/x.py": "x\n"})
        self.denied(lambda: self.call("alice", "update_ref", name="main", old=self.seed, new=head))
        self.assertTrue(self.call("mona", "update_ref", name="main", old=self.seed, new=head))  # a maintainer
        self.assertTrue(self.call("root", "update_ref", name="main", old=head, new=self.seed))  # an administrator
        self.assertTrue(self.call("alice", "update_ref", name="feature/x", old=None, new=head))  # unprotected

    def test_T_IAM_07_the_author_cannot_be_spoofed(self):
        self.denied(lambda: self.commit("alice", self.seed, {"src/y.py": "y\n"}, author="bob"))
        mine = self.commit("alice", self.seed, {"src/y.py": "y\n"})
        self.assertEqual(self.call("alice", "get_changeset", rev=mine)["author"], "alice")
        for privileged in ("root", "postmerge"):
            cs = self.commit(privileged, self.seed, {"src/z.py": privileged + "\n"}, author="bob")
            self.assertEqual(self.call("alice", "get_changeset", rev=cs)["author"], "bob")

    def test_T_IAM_09_repository_level_read_restriction(self):
        dep = self.c.deployment
        dep.create_repo("private-repo", {"read": ["alice"], "write": ["alice"]})
        alice, bob = self.c.client("alice"), self.c.client("bob")
        cs = alice.call("create_changeset", repo="private-repo", parents=[], message="m",
                        files=[{"path": "p.txt", "content_b64": b64("private\n")}],
                        update_ref={"name": "main", "old": None})["id"]
        for call in (lambda: bob.call("get_changeset", repo="private-repo", rev=cs),
                     lambda: bob.call("create_changeset", repo="private-repo", parents=[cs], message="x", files=[])):
            self.denied(call)
        oid = blob_id(b"private\n")
        daemon = lambda user: self.c.client(user, url=self.c.daemon_urls[0])  # noqa: E731
        self.assertEqual(daemon("bob").get_objects("private-repo", [oid])[0][1], F_DENIED)
        self.assertEqual(daemon("alice").get_objects("private-repo", [oid])[0][1], F_RESTRICTED)
        self.assertFalse(any(k.startswith("private-repo/") for k in self.c.daemon_services[0].source.store.iter_ids()))


class TestPolicyChanges(DirectoryTest):
    def write_policy(self, policy):
        path = os.path.join(self.c.dep_root, "repos", REPO, "policy.json")
        with open(path + ".tmp", "w") as f:
            json.dump(policy, f)
        os.replace(path + ".tmp", path)

    def test_T_IAM_10_reindexing_restricts_existing_objects(self):
        plan = self.commit("alice", self.seed, {"classified/plan.txt": "the plan\n"}, move_main=False)
        oid = blob_id(b"the plan\n")
        as_cache = lambda user: self.c.client("scion-cache", tier="cache").get_objects(REPO, [oid], on_behalf=user)  # noqa: E731
        self.assertEqual(as_cache("bob")[0][1], 0)
        self.write_policy({**POLICY, "paths": POLICY["paths"] + [{"prefix": "classified", "read": ["sec-team"]}]})
        # the new rule applies to paths at once (FR-IAM-06), but existing objects need a re-index (R-07)
        self.denied(lambda: self.call("bob", "read_file", rev=plan, path="classified/plan.txt"))
        self.assertEqual(as_cache("bob")[0][1], 0)
        self.denied(lambda: self.call("bob", "reindex_acl"))
        result = self.call("root", "reindex_acl")
        self.assertGreater(result["restricted_entries"], 0)
        self.assertEqual(as_cache("bob")[0][1], F_DENIED)
        self.assertEqual(as_cache("sam")[0][1], F_RESTRICTED)

    def test_T_IAM_13_membership_changes_take_effect_on_the_next_request(self):
        self.denied(lambda: self.call("bob", "read_file", rev="main", path="secrets/key.txt"))
        ident_path = os.path.join(self.c.dep_root, "deployment.json")
        groups = {**IDENTITY["groups"], "sec-team": ["sam", "bob"]}
        with open(ident_path + ".tmp", "w") as f:
            json.dump({**IDENTITY, "groups": groups}, f)
        os.replace(ident_path + ".tmp", ident_path)
        content = self.call("bob", "read_file", rev="main", path="secrets/key.txt")["content_b64"]
        self.assertEqual(base64.b64decode(content), (SECRET + "\n").encode())

    def test_checkout_probes_of_unreadable_directories_are_not_audited_denials(self):
        """A clone probes each directory whose tree it was denied, in case something beneath is
        readable (UC-01 3b). Those routine probes must not flood the audit log; explicit requests
        still get 403 and an audit entry."""
        self.write_policy({**POLICY, "paths": POLICY["paths"] + [{"prefix": "vault", "read": ["sec-team"]}]})
        self.commit("root", self.call("root", "resolve", rev="main"), {"vault/v.txt": "private\n"}, move_main=True)
        repo = self.c.repo()

        def denials():
            return len([e for e in repo.audit.entries(1000) if e["action"] == "denied"])

        before = denials()
        wc = self.clone("bob-probe", "bob")
        self.assertFalse(os.path.exists(os.path.join(wc.root, "vault")))
        self.assertTrue(os.path.exists(os.path.join(wc.root, "secrets", "public", "readme.txt")))
        self.assertEqual(denials(), before)
        self.assertIsNone(self.call("bob", "list_dir", rev="main", path="vault", probe=True))
        self.assertEqual([e["name"] for e in self.call("bob", "list_dir", rev="main", path="secrets", probe=True)],
                         ["public"])
        self.denied(lambda: self.call("bob", "list_dir", rev="main", path="vault"))
        self.assertEqual(denials(), before + 1)

    def test_an_invalid_policy_or_identity_keeps_the_last_good_one(self):
        """A typo in policy.json or deployment.json must neither open nor close the repository: the
        last good document stays in force, and the error is audited and logged (UC-22)."""
        path = os.path.join(self.c.dep_root, "repos", REPO, "policy.json")
        with open(path, "w") as f:
            f.write('{"read": ["*"], "paths": [')  # truncated
        self.denied(lambda: self.call("bob", "read_file", rev="main", path="secrets/key.txt"))
        self.assertEqual(self.call("bob", "resolve", rev="main"), self.call("root", "resolve", rev="main"))
        invalid = [e for e in self.call("root", "audit_log", limit=100) if e["action"] == "policy.invalid"]
        self.assertEqual(len(invalid), 1)  # once per change of the file, not once per request
        logs = self.c.client("root").get_json("/logs?level=error")["entries"]
        self.assertTrue(any("invalid" in e["message"] and REPO in e["message"] for e in logs), logs)
        ident = os.path.join(self.c.dep_root, "deployment.json")
        with open(ident, "w") as f:
            f.write("[]")  # valid JSON, but not an identity document
        self.denied(lambda: self.call("bob", "read_file", rev="main", path="secrets/key.txt"))
        self.assertTrue(self.call("root", "audit_verify")["ok"])  # root is still an administrator
        self.write_policy({**POLICY, "paths": [{"prefix": "secrets", "read": ["sec-team", "bob"]}]})
        self.call("bob", "read_file", rev="main", path="secrets/key.txt")  # a valid file applies at once

    def test_T_AUD_01_audit_log(self):
        self.denied(lambda: self.call("bob", "read_file", rev="main", path="secrets/key.txt"))
        self.call("root", "derive", type="blame", rev="main")
        self.call("rita", "create_release", name="1.0", rev="main")
        self.write_policy({**POLICY, "admins": ["ada"]})
        self.call("ada", "resolve", rev="main")  # any request picks up the new policy
        self.denied(lambda: self.call("bob", "audit_log"))
        entries = self.call("root", "audit_log", limit=100)
        actions = [e["action"] for e in entries]
        for action in ("policy.load", "denied", "ref.update", "derive", "release.create"):
            self.assertIn(action, actions)
        self.assertEqual(actions.count("policy.load"), 2)
        denial = next(e for e in entries if e["action"] == "denied" and e["target"] == "read_file")
        self.assertEqual(denial["actor"], "bob")
        self.assertGreater(denial["at"], 0)
        self.assertEqual(self.call("root", "audit_verify")["ok"], True)
        # tampering with any entry breaks the chain
        self.c.repo().meta.execute("UPDATE audit SET actor = 'mallory' WHERE seq = 2")
        check = self.call("root", "audit_verify")
        self.assertEqual((check["ok"], check["first_bad"]), (False, 2))

    def test_T_REF_01_release_branches(self):
        r = self.call("rita", "create_release", name="1.0", rev="main")
        self.assertEqual(r, {"ref": "release/1.0", "target": self.seed})
        self.denied(lambda: self.call("alice", "create_release", name="2.0", rev="main"))
        with self.assertRaises(RemoteError) as e:
            self.call("rita", "create_release", name="1.0", rev="main")
        self.assertEqual(e.exception.status, 400)
        fix = self.commit("alice", self.seed, {"src/fix.py": "fix\n"})
        self.denied(lambda: self.call("alice", "update_ref", name="release/1.0", old=self.seed, new=fix))
        self.assertTrue(self.call("rita", "update_ref", name="release/1.0", old=self.seed, new=fix))
        log = self.call("rita", "ref_log", name="release/1.0")
        self.assertEqual([(x["old"], x["new"], x["who"]) for x in log], [(self.seed, fix, "rita"), (None, self.seed, "rita")])


class TestPolicyChangesReachTheTiers(unittest.TestCase):
    """T-IAM-14 (FR-IAM-05/09, ADR-20): objects a tier cached while they were public are purged
    within the epoch interval after the repository turns private or a re-index restricts them,
    including from a restarted daemon's disk store and from snapshots."""

    EPOCH = 0.3

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-epoch-")
        self.c = Cluster(self.tmp, repos={REPO: {"read": ["*"], "write": ["*"],
                                                 "paths": [{"prefix": "vault", "read": ["sec-team"]}]}},
                         identity={"groups": {"sec-team": ["sam"]}, "admins": ["root"]}, epoch_seconds=self.EPOCH)
        self.api = self.c.client("root")
        self.cs = self.api.call("create_changeset", repo=REPO, parents=[], message="m",
                                files=[{"path": "open/a.txt", "content_b64": b64("cached while public\n")},
                                       {"path": "plans/p.txt", "content_b64": b64("plans\n")}],
                                update_ref={"name": "main", "old": None})["id"]
        self.oid = blob_id(b"cached while public\n")

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fetch(self, user, oid, url=None):
        return self.c.client(user, url=url or self.c.daemon_urls[0]).get_objects(REPO, [oid])[0]

    def policy(self, policy):
        path = os.path.join(self.c.dep_root, "repos", REPO, "policy.json")
        with open(path + ".tmp", "w") as f:
            json.dump(policy, f)
        os.replace(path + ".tmp", path)

    def held(self, oid):
        key = f"{REPO}/{oid}"
        return (self.c.daemon_services[0].source.store.has(key), self.c.cache_services[0].source.store.has(key))

    def test_T_IAM_14_a_repository_turning_private_is_purged_from_the_tiers(self):
        self.assertEqual(self.fetch("bob", self.oid)[1], 0)
        self.assertEqual(self.held(self.oid), (True, True))
        self.policy({"read": ["alice"], "write": ["alice"]})
        time.sleep(2 * self.EPOCH + 0.1)
        self.assertEqual(self.fetch("bob", self.oid)[1:], (F_DENIED, b""))
        self.assertEqual(self.held(self.oid), (False, False))
        self.assertEqual(self.fetch("alice", self.oid)[1], F_RESTRICTED)
        self.assertEqual(self.held(self.oid), (False, False))

    def test_T_IAM_14_a_restarted_daemon_purges_its_disk_store(self):
        from scion.rpc import RpcServer
        from scion.tiers import DaemonService
        store = os.path.join(self.tmp, "node")
        d1 = DaemonService(store, self.c.cache_urls, 1 << 20, epoch_seconds=self.EPOCH)
        s1 = RpcServer(d1, f"unix:{self.c.sockdir}/n1.sock").start()
        self.assertEqual(self.fetch("bob", self.oid, s1.url)[1], 0)
        s1.stop()
        d1.stop()
        self.policy({"read": ["alice"], "write": ["alice"]})  # while the daemon is down
        time.sleep(self.EPOCH + 0.1)
        d2 = DaemonService(store, self.c.cache_urls, 1 << 20, epoch_seconds=self.EPOCH)
        s2 = RpcServer(d2, f"unix:{self.c.sockdir}/n2.sock").start()
        try:
            self.assertTrue(d2.source.store.has(f"{REPO}/{self.oid}"))  # still on disk ...
            self.assertEqual(self.fetch("bob", self.oid, s2.url)[1:], (F_DENIED, b""))  # ... but not served
            self.assertFalse(d2.source.store.has(f"{REPO}/{self.oid}"))
        finally:
            s2.stop()
            d2.stop()

    def test_T_IAM_14_a_reindex_purges_newly_restricted_objects_and_stale_snapshots(self):
        from scion.rpc import RpcServer
        from scion.snapshot import create_snapshot
        from scion.tiers import DaemonService
        plans = blob_id(b"plans\n")
        self.assertEqual(self.fetch("bob", plans)[1], 0)
        snaps = os.path.join(self.tmp, "snaps")
        create_snapshot(self.c.repo(), "main", os.path.join(snaps, REPO))
        self.policy({"read": ["*"], "write": ["*"], "paths": [{"prefix": "vault", "read": ["sec-team"]},
                                                             {"prefix": "plans", "read": ["sec-team"]}]})
        self.api.call("reindex_acl", repo=REPO)
        time.sleep(2 * self.EPOCH + 0.1)
        self.assertEqual(self.fetch("bob", plans)[1:], (F_DENIED, b""))
        self.assertEqual(self.held(plans), (False, False))
        self.assertEqual(self.fetch("bob", self.oid)[1], 0)  # still public, cached again
        # a snapshot taken under the old epoch is not imported
        fresh = DaemonService(os.path.join(self.tmp, "fresh"), self.c.cache_urls, 1 << 20, snapshot_dir=snaps,
                              refresh_seconds=3600, epoch_seconds=self.EPOCH)
        try:
            self.assertEqual(fresh.snapshot_objects, 0)
            self.assertEqual(fresh.metrics.counters["snapshot.stale"], 1)
            self.assertFalse(fresh.source.store.has(f"{REPO}/{plans}"))
        finally:
            fresh.stop()


if __name__ == "__main__":
    unittest.main()

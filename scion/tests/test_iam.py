"""IAM tests. B2: token authentication (T-IAM-08) and delegation by service principals (FR-IAM-08)."""
import base64
import shutil
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()

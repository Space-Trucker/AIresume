"""T-MR-01: several repositories with different policies on one deployment (FR-IAM-02, ADR-13)."""
import base64
import os
import shutil
import tempfile
import unittest

import helpers  # noqa: F401
from helpers import Cluster
from scion.client import WorkingCopy
from scion.objects import F_DENIED, F_RESTRICTED, blob_id
from scion.rpc import RemoteError

OPEN, PRIVATE = "open-repo", "private-repo"


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


class TestMultiRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-mr-")
        self.c = Cluster(self.tmp, repos={OPEN: {"read": ["*"], "write": ["*"]},
                                          PRIVATE: {"read": ["alice", "sec-team"], "write": ["alice"]}},
                         identity={"groups": {"sec-team": ["carol"]}})
        alice = self.c.client("alice")
        for repo in (OPEN, PRIVATE):
            alice.call("create_changeset", repo=repo, parents=[], message=f"init {repo}",
                       files=[{"path": "shared.txt", "content_b64": b64("identical bytes in both\n")},
                              {"path": f"only/{repo}.txt", "content_b64": b64(f"{repo} only\n")}],
                       update_ref={"name": "main", "old": None})

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def clone(self, name, repo, user="alice"):
        return WorkingCopy.clone(os.path.join(self.tmp, name), self.c.server_urls[0], repo,
                                 objects=self.c.daemon_urls[0], user=user)

    def test_T_MR_01_policies_are_per_repository(self):
        bob, carol = self.c.client("bob"), self.c.client("carol")
        self.assertTrue(bob.call("resolve", repo=OPEN, rev="main"))
        for call in (lambda: bob.call("resolve", repo=PRIVATE, rev="main"),
                     lambda: bob.call("read_file", repo=PRIVATE, rev="main", path="shared.txt"),
                     lambda: carol.call("create_changeset", repo=PRIVATE, parents=[], message="x", files=[])):
            with self.assertRaises(RemoteError) as e:
                call()
            self.assertEqual(e.exception.status, 403)
        self.assertTrue(carol.call("resolve", repo=PRIVATE, rev="main"))  # through the group
        self.assertEqual([r["name"] for r in bob.call("list_repos")], [OPEN])
        self.assertEqual({r["name"]: r["public"] for r in self.c.client("alice").call("list_repos")},
                         {OPEN: True, PRIVATE: False})
        with self.assertRaises(RemoteError) as e:
            bob.call("resolve", repo="no-such-repo", rev="main")
        self.assertEqual(e.exception.status, 404)
        # the same ref name means different things in each repository
        self.assertNotEqual(bob.call("resolve", repo=OPEN, rev="main"),
                            self.c.client("alice").call("resolve", repo=PRIVATE, rev="main"))

    def test_T_MR_01_caches_key_by_repository_and_never_hold_private_objects(self):
        a = self.clone("open", OPEN)
        b = self.clone("private", PRIVATE)
        with open(os.path.join(b.root, "only", f"{PRIVATE}.txt")) as f:
            self.assertEqual(f.read(), f"{PRIVATE} only\n")
        daemon_keys = set(self.c.daemon_services[0].source.store.iter_ids())
        cache_store = self.c.cache_services[0].source.store
        cache_keys = set(cache_store._d)
        for keys in (daemon_keys, cache_keys):
            self.assertTrue(keys, "the open repository's objects are cached")
            self.assertTrue(all(k.startswith(OPEN + "/") for k in keys), keys)
        self.assertTrue(all(k.startswith(PRIVATE + "/") for k in self.c.cache_services[0].source.restricted))
        # identical bytes have one id in both repositories, but a cached copy is never served across them
        shared = blob_id(b"identical bytes in both\n")
        self.assertIn(f"{OPEN}/{shared}", daemon_keys)
        daemon_as = lambda user: self.c.client(user, url=self.c.daemon_urls[0])  # noqa: E731
        [(oid, flags, data)] = daemon_as("bob").get_objects(PRIVATE, [shared])
        self.assertEqual((flags, data), (F_DENIED, b""))
        # FR-IAM-08: the tiers fetch on behalf of the user, whose permissions apply
        [(oid, flags, data)] = daemon_as("alice").get_objects(PRIVATE, [shared])
        self.assertEqual(flags, F_RESTRICTED)
        self.assertTrue(data)
        [(oid, flags, data)] = daemon_as("bob").get_objects(OPEN, [shared])
        self.assertEqual(flags, 0)
        self.assertFalse(any(k.startswith(PRIVATE) for k in self.c.daemon_services[0].source.store.iter_ids()))
        a.close()
        b.close()


if __name__ == "__main__":
    unittest.main()

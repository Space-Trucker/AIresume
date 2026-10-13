import os
import unittest

from helpers import Cluster, read, write
from scion.client import ServerApi
from scion.rpc import RemoteError, RpcClient

POLICY = {
    "admins": ["root"],
    "groups": {"sec": ["alice"], "sre": ["carol"]},
    "repo": {"read": ["*"], "write": ["*"]},
    "paths": [
        {"prefix": "secrets", "read": ["sec"], "write": ["sec"]},
        {"prefix": "secrets/public", "read": ["*"]},
        {"prefix": "infra/prod", "write": ["sre"]},
    ],
    "protected_refs": {"main": ["antique", "root"], "release/*": ["root"]},
}


class TestDirectoryPermissions(unittest.TestCase):
    def setUp(self):
        self.c = Cluster(policy=POLICY)
        self.c.seed({"app/main.py": b"print('hi')\n", "secrets/key.txt": b"TOP SECRET\n",
                     "secrets/public/readme.md": b"public\n", "infra/prod/deploy.sh": b"deploy\n",
                     "shared.txt": b"TOP SECRET\n"})  # same bytes as a secret, at a public path

    def tearDown(self):
        self.c.close()

    def test_clone_skips_unreadable_directories(self):
        bob = self.c.clone("bob", user="bob")
        self.assertFalse(os.path.exists(os.path.join(bob.root, "secrets/key.txt")))
        self.assertEqual(read(bob, "secrets/public/readme.md"), b"public\n")
        self.assertEqual(read(bob, "shared.txt"), b"TOP SECRET\n")  # public copy of identical bytes
        alice = self.c.clone("alice", user="alice")
        self.assertEqual(read(alice, "secrets/key.txt"), b"TOP SECRET\n")

    def test_bytes_public_earlier_stay_public(self):
        self.c.seed({"notes.txt": b"later secret\n"})
        self.c.seed({"secrets/later.txt": b"later secret\n"})
        bob = self.c.clone("bob2", user="bob")
        self.assertEqual(read(bob, "notes.txt"), b"later secret\n")
        self.assertFalse(os.path.exists(os.path.join(bob.root, "secrets/later.txt")))

    def test_api_reads_are_filtered(self):
        bob = ServerApi(self.c.server.url, "bob")
        with self.assertRaises(RemoteError) as cm:
            bob.read_file(rev="main", path="secrets/key.txt")
        self.assertEqual(cm.exception.status, 403)
        with self.assertRaises(RemoteError):
            bob.blame(rev="main", path="secrets/key.txt")
        names = [e["name"] for e in bob.list_dir(rev="main", path="secrets")]
        self.assertEqual(names, ["public"])
        self.assertNotIn("secrets/key.txt", [m["path"] for m in bob.grep(rev="main", pattern="SECRET")["matches"]])
        self.assertNotIn("secrets/key.txt", bob.search_paths(rev="main", query="key")["paths"])
        cs = bob.get_changeset(rev="main")
        self.assertNotIn("secrets/key.txt", [c["path"] for c in cs["changes"]])

    def test_object_protocol_enforces_acls_through_every_tier(self):
        repo = self.c.repo
        root = repo.root_tree(repo.resolve("main"))
        secret_tree = repo.trees.lookup(root, "secrets")[1]
        # alice may read the restricted tree through the daemon; the caches must not keep it
        res = RpcClient(self.c.objects_url, user="alice").get_objects([secret_tree])
        self.assertEqual(res[0][1] & 0x1, 0x1)  # restricted flag
        self.assertFalse(self.c.cache_svc.source.store.has(secret_tree))
        self.assertFalse(self.c.daemon_svc.source.store.has(secret_tree))
        # bob, on the same node and through the same caches, is denied
        res = RpcClient(self.c.objects_url, user="bob").get_objects([secret_tree])
        self.assertEqual(res[0][1] & 0x4, 0x4)
        self.assertEqual(res[0][2], b"")

    def test_write_permissions(self):
        bob = ServerApi(self.c.server.url, "bob")
        with self.assertRaises(RemoteError) as cm:
            bob.create_changeset(parents=["main"], files=[{"path": "infra/prod/deploy.sh", "content_b64": "eA=="}],
                                 message="nope")
        self.assertEqual(cm.exception.status, 403)
        carol = ServerApi(self.c.server.url, "carol")
        r = carol.create_changeset(parents=["main"], files=[{"path": "infra/prod/deploy.sh", "content_b64": "eA=="}],
                                   message="ok")
        self.assertTrue(r["id"])

    def test_protected_refs(self):
        bob = ServerApi(self.c.server.url, "bob")
        r = bob.create_changeset(parents=["main"], files=[{"path": "app/x.py", "content_b64": "eA=="}], message="x")
        with self.assertRaises(RemoteError) as cm:
            bob.update_ref(name="main", old=self.c.repo.get_ref("main"), new=r["id"])
        self.assertEqual(cm.exception.status, 403)
        self.assertTrue(bob.update_ref(name="bob/scratch", old=None, new=r["id"]))  # unprotected refs are fine

    def test_author_cannot_be_spoofed(self):
        bob = ServerApi(self.c.server.url, "bob")
        with self.assertRaises(RemoteError):
            bob.create_changeset(parents=["main"], files=[{"path": "a", "content_b64": ""}], message="x",
                                 author="alice")

    def test_commit_from_client_respects_acls(self):
        bob = self.c.clone("bobw", user="bob")
        write(bob, "infra/prod/deploy.sh", b"hacked\n")
        with self.assertRaises(RemoteError):
            bob.commit("try")


class TestAuthentication(unittest.TestCase):
    def test_tokens_required_when_configured(self):
        policy = dict(POLICY, tokens={"alice": "a-token", "scion-cache": "c", "scion-daemon": "d"})
        c = Cluster(policy=policy)
        try:
            with self.assertRaises(RemoteError) as cm:
                ServerApi(c.server.url, "alice").resolve(rev="main")
            self.assertEqual(cm.exception.status, 401)
            with self.assertRaises(RemoteError):
                ServerApi(c.server.url, "alice", "wrong").resolve(rev="main")
            self.assertTrue(ServerApi(c.server.url, "alice", "a-token").whoami()["principal"] == "alice")
        finally:
            c.close()


if __name__ == "__main__":
    unittest.main()

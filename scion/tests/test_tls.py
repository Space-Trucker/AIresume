"""T-TLS-01: TLS on every TCP hop; mutual TLS identifies the tiers (NFR-20, ADR-14)."""
import http.client
import os
import shutil
import ssl
import tempfile
import unittest
import base64

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.client import WorkingCopy
from scion.iam import hash_token
from scion.rpc import ClientTls, RemoteError, RpcClient
from scion.tools.certs import make_ca, make_cert, make_dev_pki


@unittest.skipUnless(shutil.which("openssl"), "needs the openssl tool to make test certificates")
class TestTls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pki_dir = tempfile.mkdtemp(prefix="scion-pki-")
        cls.pki = make_dev_pki(cls.pki_dir)
        rogue = os.path.join(cls.pki_dir, "rogue")
        make_ca(rogue, subject="Rogue CA")
        cls.rogue_ca = os.path.join(rogue, "ca.pem")
        cls.rogue_daemon = make_cert(rogue, "daemon", "scion-daemon")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.pki_dir, ignore_errors=True)

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-tls-")
        identity = {"tokens": {"alice": hash_token("alice-token"), "bob": "bob-token",
                               "scion-daemon": "daemon-token"}}
        self.c = Cluster(self.tmp, identity=identity, pki=self.pki, tokens={"alice": "alice-token"})

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T_TLS_01_tls_everywhere_and_tiers_by_certificate(self):
        self.assertTrue(all(u.startswith("https://") for u in self.c.server_urls + self.c.cache_urls))
        alice = self.c.client("alice")
        self.assertEqual(alice.call("whoami")["via"], "token")
        alice.call("create_changeset", repo=REPO, parents=[], message="init",
                   files=[{"path": "a.txt", "content_b64": base64.b64encode(b"over tls\n").decode()}],
                   update_ref={"name": "main", "old": None})
        # a checkout through daemon -> cache -> server: every TCP hop is TLS, the tiers present certificates
        token_file = os.path.join(self.tmp, "token")
        with open(token_file, "w") as f:
            f.write("alice-token")
        wc = WorkingCopy.clone(os.path.join(self.tmp, "wc"), self.c.server_urls[0], REPO, objects=self.c.daemon_urls[0],
                               user="alice", token_file=token_file, tls_ca=self.pki["ca"])
        with open(os.path.join(wc.root, "a.txt")) as f:
            self.assertEqual(f.read(), "over tls\n")
        wc.close()
        self.assertGreater(self.c.services[0].metrics.counters["rpc.get_objects"], 0)
        as_cache = self.c.client(None, tier="cache", cert=self.pki["cache"])
        self.assertEqual(as_cache.call("whoami"), {"principal": "scion-cache", "user": "scion-cache", "tier": "cache",
                                                   "via": "cert", "admin": False})

    def test_T_TLS_01_plaintext_and_wrong_certificates_are_refused(self):
        server = self.c.server_urls[0]
        plain = RpcClient(server.replace("https://", "http://"), user="alice", token="alice-token", retries=0)
        with self.assertRaises((OSError, http.client.HTTPException)):
            plain.call("whoami")
        self.assertGreaterEqual(self.c.services[0].metrics.counters["tls.handshake_failures"], 1)
        # a server whose certificate does not chain to the CA we trust
        wrong_ca = RpcClient(server, user="alice", token="alice-token", tls=ClientTls(self.rogue_ca), retries=0)
        with self.assertRaises(ssl.SSLCertVerificationError):
            wrong_ca.call("whoami")
        # a client certificate from another CA is refused in the handshake
        rogue = RpcClient(self.c.cache_urls[0], tier="daemon", tls=ClientTls(self.pki["ca"], *self.rogue_daemon),
                          retries=0)
        with self.assertRaises((ssl.SSLError, OSError, http.client.HTTPException)):
            rogue.get_objects(REPO, ["0" * 64])

    def test_T_TLS_01_mutual_tls_identifies_the_tiers(self):
        cache = self.c.cache_urls[0]
        # with mutual TLS a tier must prove itself with its certificate: a token is not enough
        with self.assertRaises(RemoteError) as e:
            self.c.client("scion-daemon", url=cache, tier="daemon", token="daemon-token").get_objects(REPO, ["0" * 64])
        self.assertEqual(e.exception.status, 401)
        # one tier's certificate can't claim another tier
        with self.assertRaises(RemoteError) as e:
            self.c.client(None, url=cache, tier="daemon", cert=self.pki["cache"]).get_objects(REPO, ["0" * 64])
        self.assertEqual((e.exception.status, e.exception.code), (403, "bad_tier"))
        # nor can a user claim to be a tier
        with self.assertRaises(RemoteError) as e:
            self.c.client("alice", tier="cache").get_objects(REPO, ["0" * 64])
        self.assertEqual(e.exception.status, 403)
        # the daemon's own certificate works
        ok = self.c.client(None, url=cache, tier="daemon", cert=self.pki["daemon"]).get_objects(REPO, ["0" * 64])
        self.assertEqual(len(ok), 1)

    def test_tokens_over_tls(self):
        """FR-IAM-07: a missing or wrong credential is 401 once tokens are configured."""
        for user, token in (("alice", None), ("alice", "wrong"), (None, None), ("bob", "alice-token")):
            with self.subTest(user=user, token=token), self.assertRaises(RemoteError) as e:
                self.c.client(user, token=token or "").call("whoami")
            self.assertEqual(e.exception.status, 401)
        self.assertEqual(self.c.client("bob", token="bob-token").call("whoami")["user"], "bob")


if __name__ == "__main__":
    unittest.main()

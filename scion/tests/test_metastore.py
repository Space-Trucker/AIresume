"""The metadata store on SQLite and on Cloud Spanner (FR-ST-01…04, 10 §10.4: T-ST-01…04).

The conformance tests run on both backends; the Spanner ones need Google's Spanner emulator, named
by SCION_TEST_SPANNER (helpers), and skip without it."""
import json
import os
import shutil
import sqlite3
import tempfile
import threading
import time
import unittest

import helpers  # noqa: F401
from helpers import REPO, SPANNER, Cluster, metadata_config, spanner_config
from scion import backup
from scion.antique import Antique
from scion.audit import AuditLog
from scion.deployment import Deployment
from scion.meta import GRANT_SECONDS, SqliteMetaStore, open_metastore

ON_SPANNER = unittest.skipUnless(SPANNER, "needs the Spanner emulator: set SCION_TEST_SPANNER")
H = [f"{i:02x}" * 32 for i in range(40)]  # stand-in changeset and object ids


class Conformance:
    """T-ST-01: the MetaStore contract, test for test the same on every backend."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.m = self.make(self.tmp)

    def tearDown(self):
        self.m.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T_ST_01_changeset_log(self):
        m = self.m
        self.assertTrue(m.insert_changeset(H[2], b"two"))
        self.assertFalse(m.insert_changeset(H[2], b"two"))  # stored once
        for i in (5, 1, 3):
            m.insert_changeset(H[i], bytes([i]))
        self.assertEqual(m.get_changeset_data(H[5]), b"\x05")
        self.assertIsNone(m.get_changeset_data(H[9]))
        self.assertTrue(m.has_changeset(H[1]))
        self.assertFalse(m.has_changeset(H[9]))
        self.assertEqual(m.count_changesets(), 4)
        self.assertEqual(m.resolve_prefix(H[3][:6]), [H[3]])
        self.assertEqual(m.resolve_prefix("0", limit=10), sorted([H[1], H[2], H[3], H[5]]))
        ids, after = [], None
        while batch := m.tail(after, 3):  # in the order they were stored, a page at a time
            ids += [i for _, i in batch]
            after = batch[-1][0]
        self.assertEqual(ids, [H[2], H[5], H[1], H[3]])
        self.assertEqual([(i, d) for _, i, d in m.tail(None, 10, data=True)][1], (H[5], b"\x05"))

    def test_T_ST_01_refs_and_ref_log(self):
        m = self.m
        self.assertTrue(m.cas_ref("main", None, H[1], who="alice"))
        self.assertFalse(m.cas_ref("main", None, H[2]))  # must not exist
        self.assertFalse(m.cas_ref("main", H[2], H[3]))  # wrong expected value
        self.assertTrue(m.cas_ref("main", H[1], H[2], who="bob"))
        self.assertEqual(m.get_ref("main"), (H[2], 2))
        self.assertTrue(m.cas_ref("dev", None, H[1]))
        self.assertEqual(m.list_refs(), [("dev", H[1], 1), ("main", H[2], 2)])
        self.assertTrue(m.cas_ref("dev", H[1], None))  # delete
        self.assertIsNone(m.get_ref("dev"))
        self.assertTrue(m.cas_ref("dev", None, H[4]))  # and create again
        self.assertEqual(m.get_ref("dev"), (H[4], 1))
        self.assertTrue(m.cas_ref("gone", None, None))  # "absent stays absent" holds
        self.assertEqual([r[:3] for r in m.ref_log("main")], [(H[1], H[2], "bob"), (None, H[1], "alice")])
        self.assertEqual([r[:2] for r in m.ref_log("dev")], [(None, H[4]), (H[1], None), (None, H[1])])
        self.assertEqual(len(m.ref_log("dev", limit=1)), 1)
        self.assertIsInstance(m.ref_log("main")[0][3], float)

    def test_T_ST_01_derived_and_indexes(self):
        m = self.m
        self.assertIsNone(m.derived_get("tree", H[1]))
        m.derived_put("tree", H[1], "t1")
        m.derived_put("tree", H[1], "t1")  # deterministic: written twice, stored once
        m.derived_put("graph", H[1], "g1")
        self.assertEqual(m.derived_get("tree", H[1]), "t1")
        self.assertEqual(m.derived_count("tree"), 1)
        m.blob_index_add([(H[7], "b.txt"), (H[7], "a.txt"), (H[7], "a.txt"), (H[8], "c.txt")])
        self.assertEqual(m.blob_index_paths(H[7]), ["a.txt", "b.txt"])
        self.assertEqual(m.blob_index_paths(H[7], limit=1), ["a.txt"])
        self.assertIsNone(m.content_status(H[7]))
        m.content_add(H[7], "i", ["abc", "bcd", "abc"])
        m.content_add(H[8], "i", ["abc"])
        m.content_add(H[9], "l", [])
        m.content_add(H[10], "b", [])
        self.assertEqual(m.content_status(H[7]), "i")
        self.assertEqual(m.content_count("abc"), 2)
        self.assertEqual(m.content_postings("abc"), {H[7], H[8]})
        self.assertEqual(m.content_postings("zzz"), set())
        self.assertEqual(m.content_unindexed(), [H[9]])
        m.kv_set("k", "v1")
        m.kv_set("k", "v2")
        self.assertEqual(m.kv_get("k"), "v2")
        self.assertIsNone(m.kv_get("nope"))
        m.git_map_put("a" * 40, H[1])
        m.git_map_put("b" * 40, H[2])
        self.assertEqual(m.git_map_lookup(git="a" * 40), ("a" * 40, H[1]))
        self.assertEqual(m.git_map_lookup(cs=H[2]), ("b" * 40, H[2]))
        self.assertIsNone(m.git_map_lookup(git="c" * 40))

    def test_T_ST_01_object_acl_and_grants(self):
        m = self.m
        m.acl_add([(H[1], ""), (H[2], "secret"), (H[2], "other"), (H[3], "secret")])
        self.assertEqual(m.acl_get([H[1], H[2], H[2], H[9]]), {H[1]: {""}, H[2]: {"secret", "other"}})
        m.acl_replace([(H[2], ""), (H[4], "secret")])
        self.assertEqual(m.acl_get([H[1], H[2], H[3], H[4]]), {H[2]: {""}, H[4]: {"secret"}})
        many = [(f"{i:064x}", "p") for i in range(1000, 3500)]  # more ids than one query takes
        m.acl_add(many)
        self.assertEqual(len(m.acl_get([oid for oid, _ in many])), 2500)
        now = time.time()
        m.grant_add(H[5], "alice", now)
        self.assertTrue(m.grant_has(H[5], "alice", now + 10))
        self.assertFalse(m.grant_has(H[5], "bob", now))
        self.assertFalse(m.grant_has(H[5], "alice", now + GRANT_SECONDS + 1))  # it lapses
        m.grant_add(H[6], "bob", now + GRANT_SECONDS + 5)  # and is purged by a later grant
        self.assertFalse(m.grant_has(H[5], "alice", now))

    def test_T_ST_01_audit_chain(self):
        log = AuditLog(self.m)
        for i in range(5):
            log.append("ref.update" if i % 2 else "policy.load", f"user{i}", f"t{i}", {"i": i, "at": time.time()})
        self.assertEqual([e["seq"] for e in log.entries()], [5, 4, 3, 2, 1])
        self.assertEqual([e["seq"] for e in log.entries(action="ref.update")], [4, 2])
        self.assertEqual([e["seq"] for e in log.entries(before=3)], [2, 1])
        self.assertEqual(log.last("policy.load")["detail"]["i"], 4)
        v = log.verify()  # recomputing every hash proves the stored values round-trip exactly
        self.assertTrue(v["ok"], v)
        self.assertEqual(v["entries"], 5)
        self.assertEqual([r[0] for r in self.m.audit_iter()], [1, 2, 3, 4, 5])

    def test_T_ST_01_change_requests(self):
        m = self.m
        a = m.cr_create("first", "", "alice", "main", H[1], "open", 100.0)
        b = m.cr_create("second", "why", "bob", "main", H[2], "open", 101.0)
        self.assertGreater(b, a)
        cr = m.cr_get(a)
        self.assertEqual((cr["title"], cr["author"], cr["head"], cr["state"], cr["conflict"]),
                         ("first", "alice", H[1], "open", None))
        self.assertIsNone(m.cr_get(999))
        m.cr_update(a, state="conflict", conflict=json.dumps({"x": 1}), updated=102.0)
        self.assertEqual(m.cr_get(a)["state"], "conflict")
        with self.assertRaises(ValueError):
            m.cr_update(a, nonsense=1)
        self.assertEqual(m.cr_add_revision(a, H[3], "open", 103.0), 2)
        cr = m.cr_get(a)
        self.assertEqual((cr["head"], cr["state"], cr["conflict"], cr["updated"]), (H[3], "open", None, 103.0))
        self.assertEqual(m.cr_latest_rev(a), 2)
        self.assertEqual(m.cr_revisions(a), [(1, H[1], 100.0), (2, H[3], 103.0)])
        m.cr_approve(a, 2, "carol", 104.0)
        m.cr_approve(a, 2, "carol", 105.0)  # once per revision and user
        m.cr_approve(a, 1, "dave", 104.5)
        self.assertEqual(m.cr_approvals(a), [(2, "carol"), (1, "dave")])
        self.assertEqual(m.cr_approvers(a, 2), {"carol"})
        c1 = m.cr_comment(a, 2, "carol", "x.py", 3, "why?", 106.0)
        c2 = m.cr_comment(b, 1, "dave", None, None, "lgtm", 107.0)
        self.assertGreater(c2, c1)
        self.assertEqual(m.cr_comments(a), [(c1, 2, "carol", "x.py", 3, "why?", 106.0)])
        self.assertEqual(m.cr_list(), [b, a])
        self.assertEqual(m.cr_list(state="open", author="bob"), [b])
        self.assertEqual(m.cr_list(limit=1), [b])

    def test_T_ST_01_landings_and_postmerge(self):
        m = self.m
        a = m.cr_create("t", "", "alice", "main", H[1], "landing", 1.0)
        m.record_landings([(H[2], H[1], a, "main", 10.0, H[3]), (H[3], H[4], a, "main", 10.0, H[3])],
                          [(H[3], a, "main", "queued", 10.0)],
                          [(a, {"state": "landed", "landed_cs": H[3], "landed_at": 10.0, "conflict": None})])
        m.record_landings([(H[3], H[9], None, "release", 11.0, H[3]), (H[5], H[5], None, "main", 12.0, H[5])],
                          [(H[5], None, "main", "queued", 12.0), (H[6], None, "release", "queued", 12.5)], [])
        self.assertEqual(m.cr_get(a)["state"], "landed")
        self.assertEqual(m.landing_find(H[3])["source"], H[4])  # the first record stays
        self.assertEqual(m.landing_find(H[1])["cs"], H[2])  # by the pre-rebase id
        self.assertIsNone(m.landing_find(H[8]))
        self.assertEqual(m.landing_members(H[3]), {H[2], H[3]})
        self.assertEqual(m.postmerge_counts(), {"queued": 3})
        first = m.postmerge_claim("w1 a", 20.0)
        self.assertEqual((first["cs"], first["cr"], first["ref"]), (H[3], a, "main"))
        second = m.postmerge_claim("w2 b", 21.0)
        self.assertGreater(second["id"], first["id"])
        self.assertEqual(m.postmerge_counts(), {"queued": 1, "running": 2})
        self.assertFalse(m.postmerge_report(first["id"], "passed", 30.0, "log", claim="w9 z"))
        self.assertTrue(m.postmerge_report(first["id"], "failed", 30.0, "boom", claim="w1 a"))
        self.assertFalse(m.postmerge_report(first["id"], "passed", 31.0, "again"))  # not running any more
        self.assertTrue(m.postmerge_mark_reverted(first["id"], "\nreverted by x"))
        self.assertFalse(m.postmerge_mark_reverted(second["id"], "x"))  # only a failed job
        self.assertEqual(m.postmerge_job_for(H[3])["status"], "reverted")
        self.assertEqual(m.postmerge_requeue(started_before=21.5), 1)  # the second claim's lease ran out
        self.assertFalse(m.postmerge_report(second["id"], "passed", 40.0, "", claim="w2 b"))
        self.assertEqual(m.postmerge_claim("w3 c", 50.0)["id"], second["id"])
        third = m.postmerge_claim("w4 d", 51.0)
        self.assertIsNone(m.postmerge_claim("w5 e", 52.0))
        self.assertTrue(m.postmerge_report(third["id"], "passed", 53.0, "ok"))
        self.assertEqual([j["id"] for j in m.postmerge_list("main")], [second["id"], first["id"]])
        self.assertEqual(m.postmerge_list("release")[0]["status"], "passed")

    def test_T_ST_01_export_and_load(self):
        m = self.m
        m.insert_changeset(H[2], b"b")
        m.insert_changeset(H[1], b"a")
        m.cas_ref("main", None, H[2], who="alice")
        m.cas_ref("main", H[2], H[1], who="bob")
        AuditLog(m).append("backup", "admin", "x", {})
        cr = m.cr_create("t", "", "alice", "main", H[1], "open", 1.0)
        m.cr_comment(cr, 1, "bob", None, None, "hi", 2.0)
        m.record_landings([], [(H[1], cr, "main", "queued", 3.0)], [])
        m.derived_put("tree", H[1], "t")
        m.acl_add([(H[1], "")])
        path = os.path.join(self.tmp, "export", "meta.db")
        m.export(path)
        db = sqlite3.connect(path)
        self.assertEqual(db.execute("SELECT id FROM changesets ORDER BY seq").fetchall(), [(H[2],), (H[1],)])
        self.assertEqual(db.execute("SELECT name, target, version FROM refs").fetchall(), [("main", H[1], 2)])
        self.assertEqual(db.execute("SELECT who FROM ref_log ORDER BY id").fetchall(), [("alice",), ("bob",)])
        db.close()
        for fresh in (SqliteMetaStore(os.path.join(self.tmp, "on-sqlite", "meta.db")), self.make(self.tmp, "same")):
            self.assertTrue(fresh.is_empty())
            fresh.load(path)
            self.assertFalse(fresh.is_empty())
            self.assertEqual([i for _, i in fresh.tail()], [H[2], H[1]])
            self.assertEqual(fresh.get_ref("main"), (H[1], 2))
            self.assertEqual([r[2] for r in fresh.ref_log("main")], ["bob", "alice"])
            self.assertTrue(AuditLog(fresh).verify()["ok"])
            self.assertEqual(fresh.cr_comments(cr)[0][5], "hi")
            self.assertEqual(fresh.cr_create("next", "", "a", "main", H[1], "open", 4.0), cr + 1)  # ids continue
            self.assertEqual(fresh.postmerge_claim("w", 5.0)["cs"], H[1])
            self.assertEqual(fresh.derived_get("tree", H[1]), "t")
            with self.assertRaises(ValueError):
                fresh.load(path)  # never over existing metadata
            fresh.close()


class SqliteConformance(Conformance, unittest.TestCase):
    def make(self, tmp, name="r"):
        return SqliteMetaStore(os.path.join(tmp, name, "meta.db"))


@ON_SPANNER
class SpannerConformance(Conformance, unittest.TestCase):
    def make(self, tmp, name="r"):
        return open_metastore(spanner_config(), tmp, name)


@ON_SPANNER
class SpannerDeployment(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T_ST_02_a_deployment_on_spanner_serves_the_api(self):
        """The deployment's configuration alone puts the metadata on Spanner: clone, commit,
        review, land, search and audit work as on SQLite, and no meta.db is written."""
        from scion.client import WorkingCopy
        c = Cluster(self.tmp, servers=2, identity={"admins": ["admin"]})
        try:
            self.assertEqual(c.deployment.metadata["backend"], "spanner")
            api = c.client("alice")
            api.call("create_changeset", repo=REPO, parents=[], message="init", update_ref={"name": "main"},
                     files=[{"path": "src/app.py", "content_b64": "cHJpbnQoMSkK"}])
            wc = WorkingCopy.clone(os.path.join(self.tmp, "wc"), c.server_urls[0], REPO, objects=c.daemon_urls[0],
                                   user="alice")
            with open(os.path.join(wc.root, "src", "app.py"), "a") as f:
                f.write("print(2)\n")
            head = wc.commit("more")
            cr = api.call("antique.create", repo=REPO, title="more", head=head)
            c.client("bob").call("antique.approve", repo=REPO, id=cr["id"])
            landed = c.client("alice", url=c.server_urls[1]).call("antique.land", repo=REPO, id=cr["id"])
            self.assertEqual(landed["state"], "landed")
            self.assertEqual(api.call("grep", repo=REPO, rev="main", pattern="print\\(2\\)")["matches"][0]["path"],
                             "src/app.py")
            self.assertEqual(api.call("resolve", repo=REPO, rev="main"), landed["landed_cs"])
            self.assertTrue(c.repo().audit.verify()["ok"])
            self.assertFalse(os.path.exists(os.path.join(c.deployment.repo_dir(REPO), "meta.db")))
        finally:
            c.close()

    def test_T_ST_03_contention(self):
        """Concurrent compare-and-swaps have one winner; concurrent claims take every job once."""
        m = open_metastore(spanner_config(), self.tmp, "r")
        try:
            m.cas_ref("main", None, H[1])
            wins = []

            def move(i):
                if m.cas_ref("main", H[1], f"{100 + i:064x}"):
                    wins.append(i)
            threads = [threading.Thread(target=move, args=(i,)) for i in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(len(wins), 1)
            self.assertEqual(len(m.ref_log("main")), 2)
            m.record_landings([], [(H[i], None, "main", "queued", float(i)) for i in range(1, 25)], [])
            claimed, lock = [], threading.Lock()

            def work(w):
                while (job := m.postmerge_claim(f"w{w}", time.time())) is not None:
                    with lock:
                        claimed.append(job["id"])
            threads = [threading.Thread(target=work, args=(w,)) for w in range(6)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(sorted(claimed), sorted(set(claimed)))
            self.assertEqual(len(claimed), 24)
            self.assertGreater(m.client.stats["aborts"], 0)  # the conflicts really happened, and were retried
        finally:
            m.close()

    def test_T_ST_04_backup_restores_to_either_backend(self):
        """A backup of a Spanner deployment, taken while landings go on, restores to SQLite and to
        another Spanner database with identical refs, changesets and audit chain."""
        c = Cluster(self.tmp, servers=1, caches=0, identity={"admins": ["admin"]})
        try:
            api = c.client("alice")
            tip = api.call("create_changeset", repo=REPO, parents=[], message="init", update_ref={"name": "main"},
                           files=[{"path": "a.txt", "content_b64": "YQo="}])["id"]
            stop = threading.Event()

            def land():
                n, head = 0, tip
                while not stop.is_set():
                    n += 1
                    head = api.call("create_changeset", repo=REPO, parents=[head], message=f"c{n}",
                                    update_ref={"name": "main", "old": head},
                                    files=[{"path": f"f{n}.txt", "content_b64": "eAo="}])["id"]
            t = threading.Thread(target=land)
            t.start()
            time.sleep(0.5)
            out = os.path.join(self.tmp, "backup")
            manifest = backup.backup(c.dep_root, out, actor="admin")
            stop.set()
            t.join()
            self.assertEqual(manifest["metadata_backend"], "spanner")
            want = manifest["repos"][REPO]
            for target, config in (("sqlite", {"backend": "sqlite"}), ("spanner", spanner_config())):
                root = os.path.join(self.tmp, f"restored-{target}")
                report = backup.restore(out, root, metadata=config, deep=True)
                self.assertTrue(report["ok"], report)
                dep = Deployment(root)
                try:
                    repo = dep.repo(REPO)
                    self.assertEqual({n: t for n, t, _ in repo.meta.list_refs()}, want["refs"])
                    self.assertEqual(repo.meta.count_changesets(), want["changesets"])
                    chain = repo.audit.verify()
                    self.assertTrue(chain["ok"], chain)
                    # the backup's chain, then this deployment's own entries (its policy load, the restore)
                    restored = repo.audit.entries(1, before=want["audit_seq"] + 1)[0]
                    self.assertEqual(restored["hash"], c.repo().audit.entries(1, before=want["audit_seq"] + 1)[0]["hash"])
                    self.assertGreater(repo.audit.last("restore")["seq"], want["audit_seq"])
                finally:
                    dep.close()
                if target == "spanner":
                    with self.assertRaises(backup.BackupError):  # never over metadata already there
                        backup.restore(out, os.path.join(self.tmp, "again"), metadata=config)
                    self.assertFalse(os.path.exists(os.path.join(self.tmp, "again")))
        finally:
            c.close()


class Configuration(unittest.TestCase):
    def test_T_ST_02_backend_is_configuration(self):
        """The default is SQLite; an unknown backend is refused; the suite's backend comes from
        metadata_config() (Spanner with SCION_TEST_SPANNER)."""
        tmp = tempfile.mkdtemp()
        try:
            dep = Deployment(tmp)
            dep.create_repo("rrr")
            self.assertEqual(dep.metadata, {"backend": "sqlite"})
            self.assertTrue(os.path.exists(os.path.join(dep.repo_dir("rrr"), "meta.db")))
            dep.close()
            with self.assertRaises(ValueError):
                open_metastore({"backend": "nope"}, tmp, "r")
            self.assertEqual(metadata_config()["backend"], "spanner" if SPANNER else "sqlite")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

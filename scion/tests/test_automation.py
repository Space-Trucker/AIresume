"""Post-merge testing, the deploy gate, bisect and the revert pipeline (WP-B4.2):
T-PM-01/02, T-AUT-01/02."""
import base64
import json
import math
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.client import ServerApi
from scion.postmerge import PostMergeWorker
from scion.rpc import RemoteError
from scion.tools.bisect import bisect, file_matches
from scion.tools.revert import revert_and_land

POLICY = {"read": ["*"], "write": ["*"], "protected_refs": {"main": ["antique"]}}
TEST_CMD = f"{sys.executable} -c \"import sys; sys.exit('BROKEN' in open('src/app.py').read())\""


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


class AutomationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-auto-")
        self.c = Cluster(self.tmp, repos={REPO: POLICY}, identity={"admins": ["root"]})
        self.seed = self.c.client("root").call("create_changeset", repo=REPO, parents=[], message="seed",
                                               files=[{"path": "src/app.py", "content_b64": b64("ok = True\n")}],
                                               update_ref={"name": "main", "old": None})["id"]

    def tearDown(self):
        self.c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def api(self, user):
        return ServerApi(self.c.server_urls[0], REPO, user)

    def land(self, author, files, title="change"):
        api = self.api(author)
        head = api.create_changeset(parents=[api.resolve(rev="main")], message=title,
                                    files=[{"path": p, "content_b64": b64(t)} for p, t in files.items()])["id"]
        cr = api.call("antique.create", title=title, head=head)
        self.api("reviewer").call("antique.approve", id=cr["id"])
        return api.call("antique.land", id=cr["id"])["landed_cs"]


class TestPostMerge(AutomationTest):
    def test_T_PM_01_worker_auto_revert_and_deploy_gate(self):
        api = self.api("release-manager")
        self.assertIsNone(api.call("antique.deploy_gate", ref="main"))  # nothing tested yet
        c1 = self.land("alice", {"src/a.py": "a = 1\n"}, "good")
        c2 = self.land("bob", {"src/app.py": "BROKEN\n", "src/b.py": "b = 1\n"}, "breaks the tests")
        c3 = self.land("carol", {"src/c.py": "c = 1\n"}, "innocent, on a broken base")
        worker = PostMergeWorker(self.c.server_urls[0], REPO, os.path.join(self.tmp, "worker"), TEST_CMD,
                                 objects=self.c.daemon_urls[0], auto_revert=True, log=lambda *_: None)
        try:
            r1 = worker.run_once()
            self.assertEqual((r1["cs"], r1["passed"]), (c1, True))
            fetched = worker.wc.fetcher.counters["fetched"]
            r2 = worker.run_once()
            # FR-PM-02: the reused checkout fetched only the two files the landing changed
            self.assertEqual(worker.wc.fetcher.counters["fetched"] - fetched, 2)
            self.assertEqual((r2["cs"], r2["passed"]), (c2, False))
            self.assertEqual(len(r2["reverted_with"]), 1)  # its base passed: it broke the tests
            r3 = worker.run_once()
            self.assertEqual((r3["cs"], r3["passed"]), (c3, False))
            self.assertNotIn("reverted_with", r3)  # its base had failed: not necessarily its fault
            r4 = worker.run_once()  # the revert was queued for testing too
            self.assertEqual((r4["cs"], r4["passed"]), (r2["reverted_with"][0], True))
            self.assertIsNone(worker.run_once())
        finally:
            worker.close()
        main = base64.b64decode(api.read_file(rev="main", path="src/app.py")["content_b64"])
        self.assertEqual(main, b"ok = True\n")  # FR-PM-04: main no longer contains the change
        self.assertTrue(api.is_ancestor(a=c3, b="main"))
        statuses = {j["cs"]: j["status"] for j in api.call("antique.postmerge_status", ref="main")}
        self.assertEqual([statuses[x] for x in (c1, c2, c3)], ["passed", "reverted", "failed"])
        gate = api.call("antique.deploy_gate", ref="main")
        self.assertEqual(gate["cs"], r4["cs"])  # FR-PM-05: the newest changeset that passed
        self.assertEqual(api.call("antique.find_landing", cs=r4["cs"])["cr"], None)  # an automation landing

    def test_deploy_gate_never_returns_failed_or_untested_changesets(self):
        api = self.api("release-manager")
        c1 = self.land("alice", {"src/a.py": "a\n"})
        c2 = self.land("bob", {"src/b.py": "b\n"})
        a = self.c.services[0].antique(REPO)
        j1, j2 = a.postmerge_claim("w"), a.postmerge_claim("w")
        a.postmerge_report(j1["id"], True)
        self.assertEqual(api.call("antique.deploy_gate", ref="main")["cs"], c1)  # c2 is still running
        a.postmerge_report(j2["id"], False)
        self.assertEqual(api.call("antique.deploy_gate", ref="main")["cs"], c1)  # c2 failed
        self.assertEqual(api.call("antique.deploy_gate", ref="main")["behind_tip"], 1)
        self.assertEqual(c2, api.resolve(rev="main"))

    def test_T_PM_02_concurrent_workers_claim_every_job_exactly_once(self):
        a = self.c.services[0].antique(REPO)
        repo = self.c.repo()
        cur = self.seed
        for i in range(40):  # 40 landings, each with a queued job
            nxt = repo.create_changeset([cur], [{"path": f"f{i}", "content": b"x"}], "bot", f"c{i}")
            a.record_landing(nxt, "main", cur)
            cur = nxt
        claimed, lock = [], threading.Lock()

        def worker(n):
            api = self.api("postmerge")
            while True:
                job = api.call("antique.postmerge_claim")
                if job is None:
                    return
                with lock:
                    claimed.append(job["id"])

        threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(60)
        self.assertEqual(len(claimed), 40)
        self.assertEqual(len(set(claimed)), 40)
        self.assertEqual({j["status"] for j in a.postmerge_status("main", 100)}, {"running"})

    def test_T_PM_04_a_lost_workers_job_returns_to_the_queue(self):
        with open(self.c.deployment.policy_path(REPO), "w") as f:  # a short lease, from the policy (ADR-22)
            json.dump({**POLICY, "review": {"postmerge_lease_seconds": 1.0}}, f)
        c1 = self.land("alice", {"src/a.py": "a\n"})
        api = self.api("postmerge")
        lost = api.call("antique.postmerge_claim")  # this worker then crashes
        self.assertEqual(lost["cs"], c1)
        self.assertIsNone(api.call("antique.postmerge_claim"), "within the lease, the job stays claimed")
        time.sleep(1.2)
        again = api.call("antique.postmerge_claim")  # the lease ran out: the job is queued again
        self.assertEqual((again["id"], again["cs"]), (lost["id"], c1))
        self.assertNotEqual(again["claim"], lost["claim"])
        with self.assertRaises(RemoteError) as e:  # the lost worker comes back: its result is refused
            api.call("antique.postmerge_report", id=lost["id"], passed=False, claim=lost["claim"])
        self.assertEqual(e.exception.status, 400)
        api.call("antique.postmerge_report", id=again["id"], passed=True, claim=again["claim"])
        self.assertEqual(api.call("antique.deploy_gate", ref="main")["cs"], c1)
        logs = self.c.client("root").get_json("/logs?level=warning")["entries"]
        self.assertTrue(any("went back to the queue" in x["message"] for x in logs), logs)


    def worker(self, name: str) -> PostMergeWorker:
        w = PostMergeWorker(self.c.server_urls[0], REPO, os.path.join(self.tmp, name), TEST_CMD,
                            objects=self.c.daemon_urls[0], auto_revert=True, log=lambda *_: None)
        self.addCleanup(w.close)
        return w

    def test_T_PM_05_a_revert_that_cannot_land_leaves_the_worker_running(self):
        """Review finding A-06: when later work conflicts with the revert, the job stays failed for
        a person and the worker goes on with the queue."""
        api = self.api("release-manager")
        c1 = self.land("alice", {"src/a.py": "a = 1\n"})
        c2 = self.land("bob", {"src/app.py": "BROKEN\n"})
        c3 = self.land("bob", {"src/app.py": "BROKEN, a first attempt at a fix\n"})  # the revert of c2 conflicts
        results = self.worker("w").run(once=True)
        by_cs = {r["cs"]: r for r in results}
        self.assertTrue(by_cs[c1]["passed"])
        self.assertIn("conflict", by_cs[c2]["revert_failed"])
        self.assertEqual(by_cs[c2]["reverted_with"], [])
        self.assertIn("not_reverted", by_cs[c3])
        statuses = {j["cs"]: j["status"] for j in api.call("antique.postmerge_status", ref="main")}
        self.assertEqual([statuses[x] for x in (c1, c2, c3)], ["passed", "failed", "failed"])

    def test_T_PM_06_a_failure_waits_for_its_base_to_be_tested(self):
        """Review finding A-09: worker B finds c2 broken while worker A is still testing c1; the
        revert decision waits for c1's result instead of being skipped."""
        api = self.api("postmerge")
        c1 = self.land("alice", {"src/a.py": "a = 1\n"})
        c2 = self.land("bob", {"src/app.py": "BROKEN\n"})
        job_a = api.call("antique.postmerge_claim")  # worker A starts on c1
        self.assertEqual(job_a["cs"], c1)
        b = self.worker("b")
        r = b.run_once()
        self.assertEqual((r["cs"], r["passed"], r["revert_pending"]), (c2, False, "its base is still being tested"))
        api.call("antique.postmerge_report", id=job_a["id"], passed=True, claim=job_a["claim"])
        b.run(once=True)  # decides c2 now that c1 passed
        self.assertEqual(base64.b64decode(api.read_file(rev="main", path="src/app.py")["content_b64"]), b"ok = True\n")
        statuses = {j["cs"]: j["status"] for j in api.call("antique.postmerge_status", ref="main")}
        self.assertEqual([statuses[x] for x in (c1, c2)], ["passed", "reverted"])


class TestPipelines(AutomationTest):
    def test_T_AUT_01_bisect_without_a_checkout(self):
        root = self.api("root")
        chain = [self.seed]
        for i in range(1, 26):
            text = "ok = True\n" + ("BUG = 1\n" if i >= 17 else "") + f"step = {i}\n"
            chain.append(root.create_changeset(parents=[chain[-1]], message=f"step {i}",
                                               files=[{"path": "src/app.py", "content_b64": b64(text)}],
                                               update_ref={"name": "main", "old": chain[-1]})["id"])
        api = self.api("ci")
        r = bisect(api, chain[0], chain[-1], file_matches(api, "src/app.py", r"BUG", good_if_present=False))
        self.assertEqual(r["first_bad"], chain[17])
        self.assertEqual(r["range"], 26)
        self.assertLessEqual(r["probes"], math.ceil(math.log2(26)))
        self.assertEqual(r["author"], "root")
        self.assertEqual(r["summary"], "step 17")
        with self.assertRaises(ValueError):  # good must be an ancestor of bad
            bisect(api, chain[-1], chain[0], lambda cs: True)

    def test_T_AUT_01_bisect_pages_by_changeset_not_by_offset(self):
        """Review finding A-08: the range is read page by page from the last changeset seen; an
        offset beyond the server's cap is refused, never silently capped."""
        repo = self.c.repo()
        chain = [self.seed]
        for i in range(1, 2100):
            chain.append(repo.create_changeset([chain[-1]], [{"path": "src/n", "content": b"%d" % i}], "bot", f"c{i}"))
        repo.update_ref("main", self.seed, chain[-1])
        api = self.api("ci")
        r = bisect(api, chain[0], chain[-1], lambda cs: chain.index(cs) < 1777)
        self.assertEqual((r["first_bad"], r["range"]), (chain[1777], 2100))
        with self.assertRaises(RemoteError) as e:
            api.log(rev="main", limit=10, skip=10_001, ids_only=True)
        self.assertEqual(e.exception.status, 400)

    def test_T_AUT_02_revert_pipeline_under_contention(self):
        target = self.land("alice", {"src/feature.py": "FEATURE = 1\n"}, "to be reverted")
        errors, landed = [], []

        def agent(i):
            try:
                for r in range(3):
                    landed.append(self.land(f"agent{i}", {f"src/agent{i}.py": f"x = {r}\n"}, f"agent {i} round {r}"))
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [threading.Thread(target=agent, args=(i,)) for i in range(6)]
        for t in threads:
            t.start()
        revert = revert_and_land(self.api("postmerge"), target, "main")  # lands while the others land
        for t in threads:
            t.join(60)
        self.assertEqual(errors, [])
        self.assertEqual(len(landed), 18)
        api = self.api("ci")
        self.assertTrue(api.is_ancestor(a=revert, b="main"))
        names = {e["name"] for e in api.list_dir(rev="main", path="src")}
        self.assertNotIn("feature.py", names)
        self.assertTrue({f"agent{i}.py" for i in range(6)} <= names)
        self.assertEqual(api.get_changeset(rev=revert)["extra"]["reverts"], target)


if __name__ == "__main__":
    unittest.main()

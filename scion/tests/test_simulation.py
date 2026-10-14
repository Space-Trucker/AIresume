"""T-SIM-01: a swarm of agents cloning, committing, getting reviewed and landing concurrently on two
servers (FR-LD-02/03, FR-REF-04, FR-CS-05/06, NFR-01). No lost updates; the ref log of main is a
chain of compare-and-swaps; no agent starves. At stress size the swarm, which also clones, commits,
gets reviewed and updates, must land faster than NFR-01's design rate of 3.5 landings a second.

SCION_SIM_AGENTS and SCION_SIM_ROUNDS scale it (the stress run is 32 × 5). With SCION_TEST_SPANNER
the swarm's metadata is on the Spanner emulator, whose transactions conflict and are retried: T-ST-03
(FR-ST-03)."""
import base64
import os
import shutil
import statistics
import tempfile
import threading
import time
import unittest

import helpers  # noqa: F401
from helpers import REPO, Cluster
from scion.client import WorkingCopy

AGENTS = int(os.environ.get("SCION_SIM_AGENTS", "4"))
ROUNDS = int(os.environ.get("SCION_SIM_ROUNDS", "2"))


class TestSwarm(unittest.TestCase):
    def test_T_SIM_01_swarm_of_agents_on_two_servers(self):
        tmp = tempfile.mkdtemp(prefix="scion-sim-")
        c = Cluster(tmp, servers=2, repos={REPO: {"read": ["*"], "write": ["*"], "protected_refs": {"main": ["antique"]}}},
                    identity={"admins": ["root"]})
        try:
            files = [{"path": f"agents/a{i}/work.py", "content_b64": base64.b64encode(b"x = 0\n").decode()}
                     for i in range(AGENTS)]
            root = c.client("root").call("create_changeset", repo=REPO, parents=[], message="seed", files=files,
                                         update_ref={"name": "main", "old": None})["id"]
            errors, landed, waits, lock = [], [], [], threading.Lock()

            def agent(i):
                me = f"agent{i}"
                peer = c.client(f"agent{(i + 1) % AGENTS}", url=c.server_urls[(i + 1) % 2])
                wc = WorkingCopy.clone(os.path.join(tmp, me), c.server_urls[i % 2], REPO, objects=c.daemon_urls[0],
                                       user=me, mode="sparse", sparse=[f"agents/a{i}"])
                try:
                    for r in range(ROUNDS):
                        with open(os.path.join(wc.root, f"agents/a{i}/work.py"), "w") as f:
                            f.write(f"x = {r + 1}\n")
                        head = wc.commit(f"{me} round {r}")
                        cr = wc.api.call("antique.create", title=f"{me} round {r}", head=head)
                        peer.call("antique.approve", repo=REPO, id=cr["id"])
                        t0 = time.time()
                        done = wc.api.call("antique.land", id=cr["id"])
                        with lock:
                            waits.append(time.time() - t0)
                            landed.append((cr["id"], head, done["landed_cs"], done["state"]))
                        wc.update("main")
                except Exception as e:  # noqa: BLE001 - collected and reported below
                    with lock:
                        errors.append(f"{me}: {type(e).__name__}: {e}")
                finally:
                    wc.close()

            started = time.time()
            threads = [threading.Thread(target=agent, args=(i,)) for i in range(AGENTS)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(600)
            elapsed = time.time() - started
            self.assertEqual(errors, [])
            self.assertEqual(len(landed), AGENTS * ROUNDS)
            self.assertTrue(all(state == "landed" for *_, state in landed))
            api = c.client("observer")
            tip = api.call("resolve", repo=REPO, rev="main")
            # no lost updates: every agent's last change is on main
            for i in range(AGENTS):
                content = api.call("read_file", repo=REPO, rev="main", path=f"agents/a{i}/work.py")["content_b64"]
                self.assertEqual(base64.b64decode(content), f"x = {ROUNDS}\n".encode(), f"agent {i}")
            # every landing is on main and indexed by its original id
            for cr_id, head, landed_cs, _ in landed:
                self.assertTrue(api.call("is_ancestor", repo=REPO, a=landed_cs, b=tip))
                found = api.call("antique.find_landing", repo=REPO, cs=head)
                self.assertEqual((found["cs"], found["cr"]), (landed_cs, cr_id))
            # the ref log is a chain of compare-and-swaps, oldest move from the seed
            log = api.call("ref_log", repo=REPO, name="main", limit=10_000)
            self.assertEqual(log[0]["new"], tip)
            for newer, older in zip(log, log[1:]):
                self.assertEqual(newer["old"], older["new"])
            self.assertEqual((log[-1]["old"], log[-1]["new"]), (None, root))
            moves = len(log) - 1
            self.assertLessEqual(moves, AGENTS * ROUNDS)  # group commit: never more CAS than landings
            self.assertTrue(all(x["who"] == "antique" for x in log[:-1]))
            jobs = api.call("antique.postmerge_status", repo=REPO, ref="main", limit=10_000)
            self.assertEqual(len(jobs), AGENTS * ROUNDS)
            stats = [s.antique(REPO).counters for s in c.services]
            rate = AGENTS * ROUNDS / elapsed
            print(f"\n  swarm: {AGENTS} agents x {ROUNDS} rounds on 2 servers in {elapsed:.1f}s ({rate:.1f} landings/s); "
                  f"{moves} ref moves for {AGENTS * ROUNDS} landings; "
                  f"retries {sum(x['land.retries'] for x in stats)}, max batch {max(x['land.max_batch'] for x in stats)}; "
                  f"time to land median {statistics.median(waits):.2f}s, max {max(waits):.2f}s")
            # no starvation: every landing finished well inside the landing deadline (300 s)
            self.assertLess(max(waits), 60)
            if AGENTS * ROUNDS >= 100:  # NFR-01 at stress size
                self.assertGreater(rate, 3.5)
        finally:
            c.close()
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

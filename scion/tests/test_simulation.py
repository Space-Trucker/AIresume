"""Hermetic simulation: a swarm of agents working against two servers, one cache and two node
daemons.  Every agent checks out sparsely, commits on the server, opens a review, gets it
approved by a peer and lands, all concurrently and without any global lock."""
import os
import random
import threading
import unittest

from helpers import Cluster, read, write
from scion.client import ServerApi, WorkingCopy

AGENTS = int(os.environ.get("SCION_SIM_AGENTS", "12"))
ROUNDS = int(os.environ.get("SCION_SIM_ROUNDS", "3"))


class TestSwarm(unittest.TestCase):
    def test_concurrent_agents_land_without_a_global_lock(self):
        c = Cluster(servers=2)
        try:
            c.seed({f"team{i}/README.md": f"team {i}\n".encode() for i in range(AGENTS)} |
                   {"shared/config.py": b"# shared\nFLAGS = {}\n"})
            _, second_daemon = c.add_daemon()
            errors: list[BaseException] = []
            landed: list[dict] = []
            lock = threading.Lock()

            def agent(i: int):
                try:
                    rng = random.Random(i)
                    server = c.servers[i % 2].url
                    objects = c.objects_url if i % 2 == 0 else second_daemon
                    wc = WorkingCopy.clone(os.path.join(c.tmp, f"agent{i}"), server, objects, user=f"agent{i}",
                                           mode="sparse", sparse=[f"team{i}", "shared"])
                    api = ServerApi(server, f"agent{i}")
                    peer = ServerApi(c.servers[(i + 1) % 2].url, f"agent{(i + 1) % AGENTS}")
                    for r in range(ROUNDS):
                        wc.rebase("main")
                        write(wc, f"team{i}/work_{r}.py", f"RESULT = {rng.random()}\n".encode())
                        wc.commit(f"agent {i} round {r}", addremove=True)
                        cr = api.antique__create(title=f"agent {i} round {r}", head=wc.base)
                        peer.antique__approve(id=cr["id"])
                        out = api.antique__land(id=cr["id"])
                        with lock:
                            landed.append({"agent": i, "round": r, "cs": out["landed_cs"], "cr": cr["id"]})
                except BaseException as e:  # pragma: no cover - surfaced below
                    errors.append(e)

            threads = [threading.Thread(target=agent, args=(i,)) for i in range(AGENTS)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=300)
            self.assertEqual(errors, [])
            self.assertEqual(len(landed), AGENTS * ROUNDS)

            repo = c.repo
            main = repo.get_ref("main")
            files = {p for p, _, _ in repo.trees.walk(repo.root_tree(main))}
            for i in range(AGENTS):
                for r in range(ROUNDS):
                    self.assertIn(f"team{i}/work_{r}.py", files)  # no lost updates
            # main is a linear first-parent history containing every landing exactly once
            chain = repo.log(main, limit=10_000)
            for entry in landed:
                self.assertIn(entry["cs"], chain)
                self.assertEqual(c.service.antique.find_landing(entry["cs"])["cr"], entry["cr"])
            self.assertTrue(all(len(repo.get_changeset(x).parents) <= 1 for x in chain))
            counters = {k: sum(s.antique.counters[k] for s in c.services) for k in c.services[0].antique.counters}
            self.assertEqual(counters["land.success"], AGENTS * ROUNDS)
            # every ref move went through a single-row compare-and-swap, so the ref log is a chain
            log = list(reversed(repo.meta.ref_log("main", 10_000)))
            for prev, nxt in zip(log, log[1:]):
                self.assertEqual(prev[1], nxt[0])
            # caches did their job
            cache_stats = c.cache_svc.source.stats()
            self.assertGreater(cache_stats["hits"] + cache_stats["coalesced"], 0)
            # a fresh agent sees the final state
            final = c.clone("final", user="observer", mode="sparse", sparse=["team0"])
            self.assertTrue(read(final, "team0/work_0.py").startswith(b"RESULT"))
        finally:
            c.close()


if __name__ == "__main__":
    unittest.main()

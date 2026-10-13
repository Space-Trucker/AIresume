"""Fuzzing: random histories with edits, renames, file/directory swaps and merges, checked
against a naive model and against algorithm-independent invariants of the derived data."""
import os
import random
import shutil
import tempfile
import unittest

import helpers  # noqa: F401
from scion.repo import MergeConflict, Repository
from scion.search import search_paths

DIRS = ["a", "b", "a/c", "b/c/d", "e"]
NAMES = ["x", "y", "z", "w.py", "v"]
VOCAB = [f"line {i}\n".encode() for i in range(12)]
SEEDS = int(os.environ.get("SCION_FUZZ_SEEDS", "6"))
STEPS = int(os.environ.get("SCION_FUZZ_STEPS", "70"))


def valid_state(state: dict) -> bool:
    for p in state:
        parts = p.split("/")
        for i in range(1, len(parts)):
            if "/".join(parts[:i]) in state:
                return False
    return True


def random_content(rng, old: bytes | None) -> bytes:
    lines = old.splitlines(keepends=True) if old else []
    for _ in range(rng.randint(1, 3)):
        op = rng.random()
        if op < 0.4 or not lines:
            lines.insert(rng.randint(0, len(lines)), rng.choice(VOCAB))
        elif op < 0.7:
            lines[rng.randrange(len(lines))] = rng.choice(VOCAB)
        else:
            del lines[rng.randrange(len(lines))]
    return b"".join(lines)


def mutate(rng, state: dict) -> dict:
    new = dict(state)
    for _ in range(rng.randint(1, 4)):
        r = rng.random()
        if r < 0.45 and new:
            p = rng.choice(sorted(new))
            new[p] = random_content(rng, new[p])
        elif r < 0.65 and new:
            del new[rng.choice(sorted(new))]
        elif r < 0.8 and new:  # rename / copy
            src = rng.choice(sorted(new))
            dst = f"{rng.choice(DIRS)}/{rng.choice(NAMES)}"
            if dst != src and not any(q.startswith(dst + "/") or dst.startswith(q + "/") for q in new):
                new[dst] = new[src]
                if rng.random() < 0.5:
                    del new[src]
        else:
            path = f"{rng.choice(DIRS)}/{rng.choice(NAMES)}" if rng.random() < 0.85 else rng.choice(["a", "b/c", "e"])
            new[path] = random_content(rng, None)
            # make the state consistent: drop files that collide with the new path
            for q in list(new):
                if q != path and (q.startswith(path + "/") or path.startswith(q + "/")):
                    del new[q]
    return new


def changes_between(old: dict, new: dict) -> list[dict]:
    files = []
    for p in sorted(set(old) | set(new)):
        if p not in new:
            files.append({"path": p, "delete": True})
        elif old.get(p) != new[p]:
            files.append({"path": p, "content": new[p]})
    return files


class TestFuzz(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-fuzz-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def files(self, repo, cs):
        return {p: repo.read_blob(o) for p, k, o in repo.trees.walk(repo.root_tree(cs))}

    def ancestors(self, repo, cs):
        seen, stack = set(), [cs]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(repo.get_changeset(x).parents)
        return seen

    def test_random_histories(self):
        for seed in range(SEEDS):
            with self.subTest(seed=seed):
                self._run(seed)

    def _run(self, seed):
        rng = random.Random(seed)
        repo = Repository(os.path.join(self.tmp, f"r{seed}"))
        model: dict[str, dict] = {}
        initial = {f"{d}/{n}": random_content(rng, None) for d in ("a", "b/c/d", "e") for n in NAMES[:3]}
        root = repo.create_changeset([], changes_between({}, initial), "u0", "root")
        model[root] = initial
        order = [root]
        for step in range(STEPS):
            pick = lambda: order[-1 - min(int(rng.expovariate(0.3)), len(order) - 1)]  # noqa: E731
            r = rng.random()
            if r < 0.7:
                parent = pick()
                new = mutate(rng, model[parent])
                cs = repo.create_changeset([parent], changes_between(model[parent], new), f"u{step % 4}", f"s{step}")
                model[cs] = new
            elif r < 0.85:
                a, b = pick(), rng.choice(order)
                if a == b:
                    continue
                merged = {}
                for p in set(model[a]) | set(model[b]):
                    src = rng.choice([model[a], model[b]])
                    if p in src:
                        merged[p] = src[p]
                if not valid_state(merged):
                    continue
                cs = repo.create_changeset([a, b], changes_between(model[a], merged), "merger", f"m{step}")
                model[cs] = merged
            else:
                a, b = pick(), rng.choice(order)
                if a == b:
                    continue
                try:
                    cs = repo.merge(a, b, "merger")
                except MergeConflict:
                    continue
                model[cs] = self.files(repo, cs)
                bases = repo.merge_bases(a, b)
                if cs not in (a, b) and len(bases) == 1:
                    base = model.get(bases[0]) or self.files(repo, bases[0])
                    for p in set(model[a]) | set(model[b]) | set(base):
                        if model[a].get(p) == base.get(p):
                            self.assertEqual(model[cs].get(p), model[b].get(p), p)
                        elif model[b].get(p) == base.get(p):
                            self.assertEqual(model[cs].get(p), model[a].get(p), p)
            if cs not in order:
                order.append(cs)
            self.assertEqual(self.files(repo, cs), model[cs], f"tree mismatch at step {step}")
        self._check_invariants(repo, rng, order, model)
        repo.close()

    def _check_invariants(self, repo, rng, order, model):
        anc = {cs: self.ancestors(repo, cs) for cs in order}
        for _ in range(60):
            a, b = rng.choice(order), rng.choice(order)
            self.assertEqual(repo.is_ancestor(a, b), a in anc[b])
            common = anc[a] & anc[b]
            best = {c for c in common if not any(c != d and c in anc[d] for d in common)}
            self.assertEqual(set(repo.merge_bases(a, b)), best)
            # Diffs against the naive model
            got = {f["path"]: f["status"] for f in repo.diff(a, b)}
            want = {}
            for p in set(model[a]) | set(model[b]):
                if model[a].get(p) != model[b].get(p):
                    want[p] = "A" if p not in model[a] else "D" if p not in model[b] else "M"
            self.assertEqual(got, want)
        for cs in rng.sample(order, min(15, len(order))):
            # first-parent skip lists
            chain = [cs]
            while repo.get_changeset(chain[-1]).parents:
                chain.append(repo.get_changeset(chain[-1]).parents[0])
            for n in {0, min(1, len(chain) - 1), len(chain) // 2, len(chain) - 1}:
                self.assertEqual(repo.fp_ancestor(cs, n), chain[n])
            for path in rng.sample(sorted(model[cs]), min(3, len(model[cs]))):
                self._check_history(repo, cs, path, model, anc)
                self._check_blame(repo, cs, path, model, anc)
                base = path.rsplit("/", 1)[-1]
                q = base[: rng.randint(1, len(base))]
                found = search_paths(repo, cs, q, limit=1000)["paths"]
                self.assertIn(path, found)
                self.assertTrue(all(q.lower() in p.lower() for p in found))

    def _check_history(self, repo, cs, path, model, anc):
        hist = repo.file_history(cs, path, limit=1000)
        self.assertTrue(hist)
        first = hist[0]
        self.assertIn(first["cs"], anc[cs])
        self.assertEqual(model[first["cs"]].get(first["path"]), model[cs][path])
        prev = cs
        for h in hist:
            changed = {c.path for c in repo.get_changeset(h["cs"]).changes}
            self.assertIn(h["path"], changed, "history entry must have changed the path")
            self.assertIn(h["cs"], anc[prev])
            prev = h["cs"]

    def _check_blame(self, repo, cs, path, model, anc):
        b = repo.blame(cs, path)
        lines = model[cs][path].splitlines(keepends=True)
        self.assertEqual([l["text"].encode() for l in b["lines"]], lines)
        for l in b["lines"]:
            origin = l["cs"]
            self.assertIn(origin, anc[cs])
            ocs = repo.get_changeset(origin)
            ok = False
            for c in ocs.changes:
                if c.op == "D":
                    continue
                olines = model[origin][c.path].splitlines(keepends=True)
                if l["origin_line"] <= len(olines) and olines[l["origin_line"] - 1] == l["text"].encode():
                    ok = True
                    break
            self.assertTrue(ok, f"blame says {l['text']!r} came from line {l['origin_line']} of {origin[:8]}")


if __name__ == "__main__":
    unittest.main()

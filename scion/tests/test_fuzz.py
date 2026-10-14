"""T-FUZZ-01: random histories (edits, deletions, renames and copies, file↔directory swaps, merges)
checked against a naive model and an independent oracle for history and blame (BR-06: main line).

SCION_FUZZ_SEEDS and SCION_FUZZ_STEPS scale the run."""
import json
import os
import random
import shutil
import tempfile
import unittest

import helpers  # noqa: F401
from helpers import repository
from scion.derived_types import line_opcodes
from scion.repo import MergeConflict
from scion.search import search_paths

DIRS = ["a", "b", "a/c", "b/c/d", "e"]
NAMES = ["x", "y", "z", "w.py", "v"]
VOCAB = [f"line {i}\n".encode() for i in range(12)]
SEEDS = int(os.environ.get("SCION_FUZZ_SEEDS", "8"))
STEPS = int(os.environ.get("SCION_FUZZ_STEPS", "70"))


def collides(path, state):
    return any(q != path and (q.startswith(path + "/") or path.startswith(q + "/")) for q in state)


def content(rng, old=None):
    lines = old.splitlines(keepends=True) if old else []
    for _ in range(rng.randint(1, 3)):
        r = rng.random()
        if r < 0.4 or not lines:
            lines.insert(rng.randint(0, len(lines)), rng.choice(VOCAB))
        elif r < 0.7:
            lines[rng.randrange(len(lines))] = rng.choice(VOCAB)
        else:
            del lines[rng.randrange(len(lines))]
    return b"".join(lines)


def mutate(rng, state):
    new = dict(state)
    for _ in range(rng.randint(1, 4)):
        r = rng.random()
        if r < 0.45 and new:
            p = rng.choice(sorted(new))
            new[p] = content(rng, new[p])
        elif r < 0.6 and new:
            del new[rng.choice(sorted(new))]
        elif r < 0.78 and new:  # rename or copy
            src, dst = rng.choice(sorted(new)), f"{rng.choice(DIRS)}/{rng.choice(NAMES)}"
            if dst != src and not collides(dst, new):
                new[dst] = new[src]
                if rng.random() < 0.5:
                    del new[src]
        else:  # add, sometimes swapping a file and a directory
            path = f"{rng.choice(DIRS)}/{rng.choice(NAMES)}" if rng.random() < 0.85 else rng.choice(["a", "b/c", "e"])
            new[path] = content(rng)
            for q in [q for q in new if collides(path, {q: 1})]:
                del new[q]
    return new


def changes(old, new):
    out = []
    for p in sorted(set(old) | set(new)):
        if p not in new:
            out.append({"path": p, "delete": True})
        elif old.get(p) != new[p]:
            out.append({"path": p, "content": new[p]})
    return out


class TestFuzz(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-fuzz-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T_FUZZ_01_random_histories(self):
        for seed in range(SEEDS):
            with self.subTest(seed=seed):
                self.run_seed(seed)

    # ------------------------------------------------------------------------------------------
    def run_seed(self, seed):
        rng = random.Random(seed)
        repo = repository(os.path.join(self.tmp, f"r{seed}"))
        self.repo, self.model, self.fp = repo, {}, {}
        init = {f"{d}/{n}": content(rng) for d in ("a", "b/c/d", "e") for n in NAMES[:3]}
        root = repo.create_changeset([], changes({}, init), "u0", "root")
        self.model[root], self.fp[root] = init, None
        order = [root]
        for step in range(STEPS):
            pick = lambda: order[-1 - min(int(rng.expovariate(0.3)), len(order) - 1)]  # noqa: E731
            r = rng.random()
            if r < 0.7:
                parent = pick()
                new = mutate(rng, self.model[parent])
                cs = repo.create_changeset([parent], changes(self.model[parent], new), f"u{step % 4}", f"s{step}")
                self.model[cs], self.fp[cs] = new, parent
            else:
                a, b = pick(), rng.choice(order)
                if a == b:
                    continue
                if r < 0.85:  # a hand-resolved merge
                    merged = {}
                    for p in set(self.model[a]) | set(self.model[b]):
                        src = rng.choice([self.model[a], self.model[b]])
                        if p in src:
                            merged[p] = src[p]
                    if any(collides(p, merged) for p in merged):
                        continue
                    cs = repo.create_changeset([a, b], changes(self.model[a], merged), "merger", f"m{step}")
                    self.model[cs] = merged
                else:  # a server-side three-way merge
                    try:
                        cs = repo.merge(a, b, "merger")
                    except MergeConflict:
                        continue
                    self.model[cs] = self.tree(cs)
                    bases = repo.merge_bases(a, b)
                    if cs not in (a, b) and len(bases) == 1:
                        base = self.model[bases[0]]
                        for p in set(self.model[a]) | set(self.model[b]) | set(base):
                            if self.model[a].get(p) == base.get(p):
                                self.assertEqual(self.model[cs].get(p), self.model[b].get(p), p)
                            elif self.model[b].get(p) == base.get(p):
                                self.assertEqual(self.model[cs].get(p), self.model[a].get(p), p)
                self.fp[cs] = repo.get_changeset(cs).first_parent
            if cs not in order:
                order.append(cs)
            self.assertEqual(self.tree(cs), self.model[cs], f"seed {seed} step {step}: tree differs from model")
        self.check(rng, order)
        repo.close()

    def tree(self, cs):
        return {p: self.repo.read_blob(o) for p, _, o in self.repo.trees.walk(self.repo.root_tree(cs))}

    def ancestors(self, cs):
        seen, stack = set(), [cs]
        while stack:
            x = stack.pop()
            if x not in seen:
                seen.add(x)
                stack.extend(self.repo.get_changeset(x).parents)
        return seen

    # -- the independent oracle (main line, BR-06) -------------------------------------------
    def oracle_history(self, cs, path):
        out, cur = [], cs
        while cur:
            state = self.model[cur]
            if path not in state:
                break  # absent, or a directory here: history stops
            x = cur
            while self.fp[x] is not None and self.model[self.fp[x]].get(path) == state[path]:
                x = self.fp[x]
            out.append((x, path))
            src = json.loads(self.repo.derived.get("copies", x)).get(path)
            if src and self.fp[x] is not None and src["from"] in self.model[self.fp[x]]:
                path = src["from"]
            cur = self.fp[x]
        return out

    def oracle_blame(self, cs, path):
        versions = list(reversed(self.oracle_history(cs, path)))
        attr = None
        for x, p in versions:
            lines = self.model[x][p].splitlines(keepends=True)
            if attr is None:
                attr, old = [(x, i + 1) for i in range(len(lines))], lines
                continue
            new_attr = [(x, j + 1) for j in range(len(lines))]
            for tag, i1, i2, j1, j2 in line_opcodes(old, lines):  # the alignment blame defines
                if tag == "equal":
                    new_attr[j1:j2] = attr[i1:i2]
            attr, old = new_attr, lines
        return attr or []

    def check(self, rng, order):
        repo = self.repo
        anc = {cs: self.ancestors(cs) for cs in order}
        for _ in range(60):
            a, b = rng.choice(order), rng.choice(order)
            self.assertEqual(repo.is_ancestor(a, b), a in anc[b])
            common = anc[a] & anc[b]
            best = {c for c in common if not any(c != d and c in anc[d] for d in common)}
            self.assertEqual(set(repo.merge_bases(a, b)), best)
            want = {p: ("A" if p not in self.model[a] else "D" if p not in self.model[b] else "M")
                    for p in set(self.model[a]) | set(self.model[b]) if self.model[a].get(p) != self.model[b].get(p)}
            self.assertEqual({f["path"]: f["status"] for f in repo.diff(a, b)}, want)
        for cs in rng.sample(order, min(15, len(order))):
            chain = [cs]
            while self.fp[chain[-1]] is not None:
                chain.append(self.fp[chain[-1]])
            for n in {0, min(1, len(chain) - 1), len(chain) // 2, len(chain) - 1}:
                self.assertEqual(repo.fp_ancestor(cs, n), chain[n])
            for path in rng.sample(sorted(self.model[cs]), min(4, len(self.model[cs]))):
                got = [(h["cs"], h["path"]) for h in repo.file_history(cs, path, limit=1000)]
                self.assertEqual(got, self.oracle_history(cs, path), f"history of {path}")
                blame = repo.blame(cs, path)
                self.assertEqual([l["text"].encode() for l in blame["lines"]], self.model[cs][path].splitlines(keepends=True))
                self.assertEqual([(l["cs"], l["origin_line"]) for l in blame["lines"]], self.oracle_blame(cs, path),
                                 f"blame of {path}")
                base = path.rsplit("/", 1)[-1]
                q = base[: rng.randint(1, len(base))]
                found = search_paths(repo, cs, q, limit=1000)["paths"]
                self.assertIn(path, found)
                self.assertTrue(all(q.lower() in p.lower() for p in found))


if __name__ == "__main__":
    unittest.main()

"""B1 acceptance tests: objects, changesets, refs, trees, derived data, queries, merge/rebase/revert.
Test IDs follow docs/design/10-test-plan.md §10.4."""
import json
import os
import shutil
import statistics
import tempfile
import threading
import time
import unittest

import helpers  # noqa: F401
from scion.changeset import Changeset
from scion.derived import DerivedType
from scion.merge3 import merge3
from scion.objects import EMPTY_TREE_ID, ObjectError, blob_id, decode_stored, encode_stored
from scion.repo import MergeConflict, NotFound, Repository
from scion.search import search_paths
from scion.storage import BoundedFileObjectStore, MemoryObjectStore


class RepoCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-core-")
        self.repo = Repository(os.path.join(self.tmp, "r"))

    def tearDown(self):
        self.repo.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit(self, parents, files, author="ann", msg="m", repo=None):
        spec = [{"path": p, "delete": True} if c is None else {"path": p, "content": c} for p, c in files.items()]
        return (repo or self.repo).create_changeset(parents, spec, author, msg)

    def files(self, cs):
        return {p: self.repo.read_blob(o) for p, _, o in self.repo.trees.walk(self.repo.root_tree(cs))}


class TestObjects(unittest.TestCase):
    def test_T_CORE_01_round_trip_and_integrity(self):
        stored = encode_stored("blob", b"hello")
        self.assertEqual(decode_stored(stored, blob_id(b"hello")), ("blob", b"hello"))
        with self.assertRaises(ObjectError):
            decode_stored(stored, blob_id(b"other"))
        with self.assertRaises(ObjectError):
            decode_stored(b"not zlib", None)

    def test_T_CORE_02_bounded_stores_evict_and_rebuild(self):
        m = MemoryObjectStore(max_bytes=300)
        ids = [m.put("blob", os.urandom(100)) for _ in range(10)]
        self.assertTrue(m.has(ids[-1]) and not m.has(ids[0]))
        d = tempfile.mkdtemp()
        try:
            s = BoundedFileObjectStore(d, max_bytes=2500)
            ids = [s.put("blob", os.urandom(500)) for _ in range(20)]
            self.assertLessEqual(s.size_bytes, 2500)
            self.assertGreater(s.evictions, 0)
            self.assertTrue(s.has(ids[-1]) and not s.has(ids[0]))
            again = BoundedFileObjectStore(d, max_bytes=2500)  # state rebuilt from disk
            self.assertEqual(len(again), len(s))
        finally:
            shutil.rmtree(d)


class TestChangesets(RepoCase):
    def test_T_CORE_03_changes_relative_to_first_parent(self):
        c1 = self.commit([], {"a": b"1", "d/b": b"2"})
        c2 = self.commit([c1], {"a": b"1", "d/b": b"3", "c": b"new"})  # "a" unchanged → no-op
        cs = self.repo.get_changeset(c2)
        self.assertEqual([(c.path, c.op) for c in cs.changes], [("c", "A"), ("d/b", "M")])
        self.assertEqual(Changeset.decode(cs.encode()).id, c2)
        # FR-QRY-01: the API view carries changes, generation and copies
        api = self.repo.changeset_api(c2)
        self.assertEqual((api["id"], api["generation"], api["parents"]), (c2, 2, [c1]))

    def test_T_CORE_04_idempotent(self):
        a = self.repo.create_changeset([], [{"path": "a", "content": b"x"}], "u", "m", timestamp=7)
        b = self.repo.create_changeset([], [{"path": "a", "content": b"x"}], "u", "m", timestamp=7)
        self.assertEqual(a, b)
        self.assertEqual(self.repo.meta.count_changesets(), 1)

    def test_T_CORE_05_refs_optional_cas_and_log(self):
        c1 = self.commit([], {"a": b"1"})
        c2 = self.commit([c1], {"a": b"2"})
        self.assertEqual(self.repo.meta.list_refs(), [])  # creating changesets moved no ref
        self.assertTrue(self.repo.update_ref("main", None, c1))
        self.assertFalse(self.repo.update_ref("main", None, c2))
        self.assertFalse(self.repo.update_ref("main", c2, c2))
        self.assertTrue(self.repo.update_ref("main", c1, c2))
        self.assertEqual([(o, n) for o, n, _, _ in self.repo.meta.ref_log("main")], [(c1, c2), (None, c1)])
        # NFR-12: concurrent compare-and-swaps with the same expected value → exactly one wins
        cands = [self.commit([c2], {"a": f"{i}".encode()}) for i in range(8)]
        wins = []
        threads = [threading.Thread(target=lambda c=c: wins.append(self.repo.update_ref("main", c2, c))) for c in cands]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(wins.count(True), 1)
        log = list(reversed(self.repo.meta.ref_log("main")))
        for prev, nxt in zip(log, log[1:]):
            self.assertEqual(prev[1], nxt[0])  # FR-REF-04: an unbroken chain

    def test_T_CORE_06_revision_syntax(self):
        c1 = self.commit([], {"a": b"1"})
        c2 = self.commit([c1], {"a": b"2"})
        c3 = self.commit([c2], {"a": b"3"})
        self.repo.update_ref("main", None, c3)
        self.assertEqual(self.repo.resolve("main~2"), c1)
        self.assertEqual(self.repo.resolve(c3[:10] + "^"), c2)
        self.assertEqual(self.repo.resolve("main^^"), c1)
        self.assertEqual(self.repo.resolve(c2), c2)
        for bad in ("main~3", "nope", "", "zzzz"):
            with self.assertRaises(NotFound):
                self.repo.resolve(bad)

    def test_T_CORE_07_validation(self):
        c1 = self.commit([], {"a": b"1", "dir/x": b"2"})
        for bad in ({"missing": None}, {"a/b": b"x"}, {"dir": b"x"}):
            with self.assertRaises(ValueError):
                self.commit([c1], bad)
        with self.assertRaises(ValueError):
            self.repo.create_changeset([c1], [{"path": "a", "content": b"1"}, {"path": "a", "content": b"2"}], "u", "m")
        with self.assertRaises(ValueError):
            self.repo.create_changeset([c1], [{"path": "q", "blob": "0" * 64}], "u", "m")
        with self.assertRaises(Exception):
            self.repo.create_changeset([c1], [{"path": "../x", "content": b""}], "u", "m")
        # replacing a file with a directory (and the reverse) in one changeset is valid
        c2 = self.commit([c1], {"a": None, "a/b": b"x", "dir/x": None, "dir": b"file"})
        self.assertEqual(self.files(c2), {"a/b": b"x", "dir": b"file"})
        c3 = self.commit([c2], {"a/b": None, "dir": None})
        self.assertEqual(self.repo.root_tree(c3), EMPTY_TREE_ID)

    def test_T_CORE_08_only_changed_subtrees_are_rewritten(self):
        c1 = self.commit([], {f"d{i}/f{j}": f"{i}{j}".encode() for i in range(10) for j in range(10)})
        before = self.repo.trees.writes
        c2 = self.commit([c1], {"d3/f3": b"changed"})
        self.assertEqual(self.repo.trees.writes - before, 2)  # the root and d3 only
        t1, t2 = self.repo.trees.read(self.repo.root_tree(c1)), self.repo.trees.read(self.repo.root_tree(c2))
        self.assertEqual(sum(1 for n in t1 if t1[n] == t2[n]), 9)

    def test_T_CORE_09_scoped_and_text_diffs(self):
        c1 = self.commit([], {"a/x": b"1\n", "b/y": b"2\n"})
        c2 = self.commit([c1], {"a/x": b"3\n", "b/y": b"4\n", "b/z": b"5\n"})
        self.assertEqual({f["path"]: f["status"] for f in self.repo.diff(c1, c2)}, {"a/x": "M", "b/y": "M", "b/z": "A"})
        self.assertEqual({f["path"] for f in self.repo.diff(c1, c2, paths=["b"])}, {"b/y", "b/z"})
        text = self.repo.diff_text(c1, c2, paths=["a/x"])
        self.assertIn("-1\n", text)
        self.assertIn("+3\n", text)

    def test_T_CORE_10_commit_cost_is_flat_in_repository_size(self):
        timings = {}
        for n in (100, 10_000):
            r = Repository(os.path.join(self.tmp, f"s{n}"))
            root = r.create_changeset([], [{"path": f"d{i % 100:03d}/sub{i % 7}/f{i}.txt", "content": f"{i}\n".encode()}
                                           for i in range(n)], "b", "import")
            meds, cur = [], root
            for _ in range(3):  # best of three medians absorbs scheduler noise
                samples = []
                for k in range(15):
                    w = r.trees.writes
                    t0 = time.perf_counter()
                    cur = r.create_changeset([cur], [{"path": "d001/sub1/hot.txt", "content": f"{k}{time.time()}".encode()}], "b", "e")
                    samples.append(time.perf_counter() - t0)
                    self.assertEqual(r.trees.writes - w, 3)  # root, d001, d001/sub1: independent of n
                meds.append(statistics.median(samples))
            timings[n] = min(meds)
            r.close()
        self.assertLessEqual(timings[10_000], timings[100] * 1.25 + 0.002, timings)


class TestDerived(RepoCase):
    def test_T_DD_01_eager_deferred_and_ancestors_first(self):
        c1 = self.commit([], {"f": b"1\n"})
        c2 = self.commit([c1], {"f": b"1\n2\n"})
        for t in ("tree", "graph", "history", "copies", "search"):
            self.assertIsNotNone(self.repo.meta.derived_get(t, c2), t)
        self.assertIsNone(self.repo.meta.derived_get("blame", c2))
        self.repo.blame(c2, "f")
        self.assertIsNotNone(self.repo.meta.derived_get("blame", c1))  # ancestors derived first
        # FR-DD-05: two servers on one store derive concurrently without coordination
        c3 = self.commit([c2], {"f": b"1\n2\n3\n"})
        other = Repository(self.repo.root)
        out = []
        threads = [threading.Thread(target=lambda r=r: out.append(r.derived.get("blame", c3))) for r in (self.repo, other)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(len(set(out)), 1)
        other.close()

    def test_T_DD_02_new_type_without_client_changes(self):
        class FileCount(DerivedType):
            name, depends_on = "filecount", ("tree",)

            def derive(self, repo, cs_id, cs, pv):
                base = int(pv[0]) if pv else 0
                return str(base + sum({"A": 1, "D": -1}.get(c.op, 0) for c in cs.changes))
        self.repo.derived.register(FileCount())
        c1 = self.commit([], {"a": b"1", "b": b"2"})
        c2 = self.commit([c1], {"a": None, "c": b"3", "d": b"4"})
        self.assertEqual(self.repo.derived.get("filecount", c2), "3")
        with self.assertRaises(ValueError):
            self.repo.derived.register(FileCount())

    def test_T_DD_03_copies_renames_and_history_across_them(self):
        c1 = self.commit([], {"src/a.py": b"A\n", "src/b.py": b"B\n"})
        c2 = self.commit([c1], {"src/a.py": None, "lib/a.py": b"A\n", "lib/b2.py": b"B\n"})
        copies = json.loads(self.repo.derived.get("copies", c2))
        self.assertEqual(copies, {"lib/a.py": {"from": "src/a.py", "type": "rename"},
                                  "lib/b2.py": {"from": "src/b.py", "type": "copy"}})
        hist = self.repo.file_history(c2, "lib/a.py")
        self.assertEqual([(h["cs"], h["path"]) for h in hist], [(c2, "lib/a.py"), (c1, "src/a.py")])

    def test_T_DD_04_history_of_files_and_directories(self):
        c1 = self.commit([], {"a/x": b"1", "b/y": b"1"})
        c2 = self.commit([c1], {"b/y": b"2"})
        c3 = self.commit([c2], {"a/x": b"2"})
        c4 = self.commit([c3], {"b/y": b"3"})
        self.assertEqual([h["cs"] for h in self.repo.file_history(c4, "a/x")], [c3, c1])
        self.assertEqual([h["cs"] for h in self.repo.file_history(c4, "b")], [c4, c2, c1])
        self.assertEqual(self.repo.log(c4, path="a"), [c3, c1])
        # FR-QRY-02: pagination is contiguous and duplicate-free
        self.assertEqual(self.repo.log(c4, limit=2) + self.repo.log(c4, limit=2, skip=2), [c4, c3, c2, c1])
        # a path that changed between file and directory is a different object
        c5 = self.commit([c4], {"a/x": None, "a": b"file now"})
        self.assertEqual([h["cs"] for h in self.repo.file_history(c5, "a")], [c5])

    def test_T_DD_05_blame(self):
        c1 = self.commit([], {"f": b"a\nb\nc\n"}, author="ann")
        c2 = self.commit([c1], {"f": b"a\nB\nc\nd\n"}, author="bob")
        c3 = self.commit([c2], {"g": b"a\nB\nc\nd\n", "f": None}, author="cat")  # rename
        lines = self.repo.blame(c3, "g")["lines"]
        self.assertEqual([(l["cs"], l["origin_line"]) for l in lines], [(c1, 1), (c2, 2), (c1, 3), (c2, 4)])
        self.assertEqual(self.repo.blame(c3, "g")["changesets"][c2]["author"], "bob")
        c4 = self.commit([c3], {"bin": b"\0\1\2"})
        self.assertTrue(self.repo.blame(c4, "bin")["binary"])

    def test_T_DD_07_backfill(self):
        cur = None
        for i in range(12):
            cur = self.commit([cur] if cur else [], {"f": f"{i}\n".encode() * (i + 1)})
        self.assertEqual(self.repo.derived.backfill("blame", cur), 12)
        self.assertEqual(self.repo.derived.backfill("blame", cur), 0)

    def test_T_DD_08_history_and_blame_follow_the_main_line(self):
        base = self.commit([], {"f": b"1\n2\n3\n"})
        left = self.commit([base], {"f": b"1\nL\n3\n"}, author="left")
        right = self.commit([base], {"f": b"1\n2\n3\nR\n", "only_right": b"r\n"}, author="right")
        m = self.repo.merge(left, right, "merger")
        self.assertEqual(self.files(m)["f"], b"1\nL\n3\nR\n")
        by_line = {l["text"]: l["cs"] for l in self.repo.blame(m, "f")["lines"]}
        self.assertEqual(by_line, {"1\n": base, "L\n": left, "3\n": base, "R\n": m})  # BR-06
        self.assertEqual([h["cs"] for h in self.repo.file_history(m, "only_right")], [m])
        self.assertEqual([h["cs"] for h in self.repo.file_history(m, "f")], [m, left, base])


class TestQueries(RepoCase):
    def test_T_CORE_11_read_file_and_list_dir(self):
        c1 = self.commit([], {"a/x": b"1", "a/y": b"2", "top": b"t"})
        self.assertEqual(self.repo.read_file(c1, "a/x")[2], b"1")
        self.assertEqual([e["name"] for e in self.repo.list_dir(c1, "a")], ["x", "y"])
        self.assertEqual([e["kind"] for e in self.repo.list_dir(c1, "")], ["d", "f"])
        with self.assertRaises(NotFound):
            self.repo.read_file(c1, "a")
        with self.assertRaises(NotFound):
            self.repo.list_dir(c1, "top")

    def test_T_CORE_12_path_search_prunes(self):
        files = {f"area{a}/team{t}/mod{m}.py": b"x" for a in range(6) for t in range(6) for m in range(3)}
        files["area2/team4/special_handler.py"] = b"y"
        c = self.commit([], files)
        r = search_paths(self.repo, c, "special_hand")
        self.assertEqual(r["paths"], ["area2/team4/special_handler.py"])
        self.assertLess(r["trees_visited"], 12)  # of 1 + 6 + 36 trees


class TestAncestry(RepoCase):
    def chain(self, start, n, tag):
        out, cur = [], start
        for i in range(n):
            cur = self.commit([cur], {tag: f"{tag}{i}".encode()})
            out.append(cur)
        return out

    def test_T_DD_06_skip_lists_generations_merge_bases(self):
        root = self.commit([], {"f": b"0"})
        chain = self.chain(root, 100, "f")
        tip = chain[-1]
        self.assertEqual(self.repo.generation(tip), 101)
        self.assertEqual(self.repo.fp_ancestor(tip, 37), chain[-38])
        self.assertEqual(self.repo.fp_ancestor(tip, 100), root)
        self.assertIsNone(self.repo.fp_ancestor(tip, 101))
        self.repo.stats.clear()
        self.assertTrue(self.repo.is_ancestor(root, tip))
        self.assertLess(self.repo.stats["ancestry.visits"] + self.repo.stats["ancestry.hops"], 20)  # NFR-06
        self.assertFalse(self.repo.is_ancestor(tip, root))
        main = self.chain(root, 30, "m")
        branch = self.chain(main[9], 20, "b")
        m = self.repo.merge(main[-1], branch[-1], "x")
        after = self.chain(m, 5, "m")
        self.assertEqual(self.repo.merge_base(branch[-1], main[-1]), main[9])
        self.assertEqual(self.repo.merge_base(after[-1], branch[-1]), branch[-1])
        self.assertTrue(self.repo.is_ancestor(branch[5], after[-1]))
        side = self.chain(main[20], 3, "s")
        self.assertEqual(self.repo.merge_base(side[-1], after[-1]), main[20])


class TestMergeRebaseRevert(RepoCase):
    def test_T_WR_01(self):
        b = b"a\nb\nc\nd\n"
        self.assertEqual(merge3(b, b"A\nb\nc\nd\n", b"a\nb\nc\nD\n"), (b"A\nb\nc\nD\n", 0))
        out, n = merge3(b, b"a\nX\nc\nd\n", b"a\nY\nc\nd\n")
        self.assertEqual(n, 1)
        self.assertIn(b"<<<<<<< ours", out)
        # rebase a stack, dropping already-applied changes
        base = self.commit([], {"f": b"1\n2\n3\n", "g": b"x\n"})
        up = self.commit([base], {"f": b"1\n2\n3\n4\n"})
        s1 = self.commit([base], {"f": b"0\n1\n2\n3\n"})
        s2 = self.commit([s1], {"h": b"new\n"})
        dup = self.commit([s2], {"f": b"0\n1\n2\n3\n4\n"})  # already equals upstream after rebase
        r = self.repo.rebase(dup, up)
        self.assertEqual(set(r["rebased"]), {s1, s2, dup})
        self.assertEqual(r["rebased"][dup], r["rebased"][s2])  # dropped
        self.assertEqual(self.files(r["head"]), {"f": b"0\n1\n2\n3\n4\n", "g": b"x\n", "h": b"new\n"})
        self.assertEqual(self.repo.get_changeset(r["head"]).extra["rebased_from"], s2)
        # conflicts are structured
        clash = self.commit([base], {"g": b"y\n"})
        up2 = self.commit([up], {"g": b"z\n"})
        with self.assertRaises(MergeConflict) as cm:
            self.repo.rebase(clash, up2)
        self.assertEqual((cm.exception.conflicts[0]["path"], cm.exception.at), ("g", clash))
        # revert on top of later work
        c2 = self.commit([up], {"f": b"1\nTWO\n3\n4\n", "new": b"n"})
        c3 = self.commit([c2], {"f": b"1\nTWO\n3\n4\n5\n"})
        rv = self.repo.revert(c2, c3, "bot")
        self.assertEqual(self.files(rv), {"f": b"1\n2\n3\n4\n5\n", "g": b"x\n"})
        self.assertEqual(self.repo.get_changeset(rv).extra["reverts"], c2)
        # modify/delete conflict; base-directory case (both sides turned dir "k" into a file)
        a = self.commit([base], {"f": None})
        with self.assertRaises(MergeConflict):
            self.repo.merge(a, up, "x")
        kd = self.commit([base], {"k/x": b"1\n"})
        k1 = self.commit([kd], {"k/x": None, "k": b"one\n"})
        k2 = self.commit([kd], {"k/x": None, "k": b"two\n"})
        with self.assertRaises(MergeConflict) as cm:
            self.repo.merge(k1, k2, "x")
        self.assertEqual(cm.exception.conflicts[0]["path"], "k")


if __name__ == "__main__":
    unittest.main()

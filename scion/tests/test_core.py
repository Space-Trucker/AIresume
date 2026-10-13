import json
import os
import shutil
import tempfile
import unittest

import helpers  # noqa: F401  (sets sys.path)
from scion.changeset import Changeset
from scion.merge3 import merge3
from scion.objects import EMPTY_TREE_ID, blob_id, decode_stored, encode_stored
from scion.repo import MergeConflict, NotFound, Repository
from scion.storage import BoundedFileObjectStore, MemoryObjectStore


class RepoTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scion-core-")
        self.repo = Repository(os.path.join(self.tmp, "repo"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit(self, parents, files, author="alice", msg="m"):
        spec = []
        for p, c in files.items():
            spec.append({"path": p, "delete": True} if c is None else {"path": p, "content": c})
        return self.repo.create_changeset(parents, spec, author, msg)

    def tree_files(self, cs):
        return {p: self.repo.read_blob(oid) for p, k, oid in self.repo.trees.walk(self.repo.root_tree(cs))}


class TestObjects(unittest.TestCase):
    def test_roundtrip_and_integrity(self):
        stored = encode_stored("blob", b"hello")
        oid = blob_id(b"hello")
        self.assertEqual(decode_stored(stored, oid), ("blob", b"hello"))
        with self.assertRaises(Exception):
            decode_stored(stored, "0" * 64)

    def test_memory_lru_bound(self):
        s = MemoryObjectStore(max_bytes=200)
        ids = [s.put("blob", os.urandom(80)) for _ in range(10)]
        self.assertLessEqual(s.size_bytes, 200 + 120)
        self.assertTrue(s.has(ids[-1]))
        self.assertFalse(s.has(ids[0]))

    def test_bounded_disk_store_evicts(self):
        d = tempfile.mkdtemp()
        try:
            s = BoundedFileObjectStore(d, max_bytes=2000)
            ids = [s.put("blob", os.urandom(500)) for _ in range(20)]
            self.assertLessEqual(s.size_bytes, 2000)
            self.assertTrue(s.has(ids[-1]))
            self.assertFalse(s.has(ids[0]))
            self.assertGreater(s.evictions, 0)
            s2 = BoundedFileObjectStore(d, max_bytes=2000)  # state is rebuilt from disk
            self.assertEqual(len(s2), len(s))
        finally:
            shutil.rmtree(d)


class TestChangesets(RepoTestCase):
    def test_changes_are_relative_to_first_parent(self):
        c1 = self.commit([], {"a": b"1", "d/b": b"2"})
        c2 = self.commit([c1], {"a": b"1", "d/b": b"3", "c": b"new"})  # "a" unchanged: a no-op
        cs = self.repo.get_changeset(c2)
        self.assertEqual([(c.path, c.op) for c in cs.changes], [("c", "A"), ("d/b", "M")])
        self.assertEqual(cs.parents, (c1,))
        self.assertEqual(Changeset.decode(cs.encode()).id, c2)

    def test_idempotent_content_addressing(self):
        c1 = self.repo.create_changeset([], [{"path": "a", "content": b"x"}], "u", "m", timestamp=5)
        c1b = self.repo.create_changeset([], [{"path": "a", "content": b"x"}], "u", "m", timestamp=5)
        self.assertEqual(c1, c1b)
        self.assertEqual(self.repo.meta.count_changesets(), 1)

    def test_no_refs_needed_and_cas(self):
        c1 = self.commit([], {"a": b"1"})
        c2 = self.commit([c1], {"a": b"2"})
        self.assertEqual(self.repo.meta.list_refs(), [])  # creating changesets moved nothing
        self.assertTrue(self.repo.update_ref("main", None, c1))
        self.assertFalse(self.repo.update_ref("main", None, c2))  # must not exist
        self.assertFalse(self.repo.update_ref("main", c2, c2))  # wrong expected value
        self.assertTrue(self.repo.update_ref("main", c1, c2))
        self.assertEqual(self.repo.get_ref("main"), c2)

    def test_resolve(self):
        c1 = self.commit([], {"a": b"1"})
        c2 = self.commit([c1], {"a": b"2"})
        c3 = self.commit([c2], {"a": b"3"})
        self.repo.update_ref("main", None, c3)
        self.assertEqual(self.repo.resolve("main~2"), c1)
        self.assertEqual(self.repo.resolve(c3[:10] + "^"), c2)
        self.assertEqual(self.repo.resolve("main^^"), c1)
        with self.assertRaises(NotFound):
            self.repo.resolve("main~3")
        with self.assertRaises(NotFound):
            self.repo.resolve("nope")

    def test_validation(self):
        c1 = self.commit([], {"a": b"1", "dir/x": b"2"})
        with self.assertRaises(ValueError):
            self.commit([c1], {"missing": None})  # delete of a non-existent file
        with self.assertRaises(ValueError):
            self.commit([c1], {"a/b": b"x"})  # "a" is a file
        with self.assertRaises(ValueError):
            self.commit([c1], {"dir": b"x"})  # "dir" is a directory
        # ...but replacing in one changeset is fine, both ways
        c2 = self.commit([c1], {"a": None, "a/b": b"x", "dir/x": None, "dir": b"file"})
        self.assertEqual(self.tree_files(c2), {"a/b": b"x", "dir": b"file"})

    def test_empty_dirs_disappear_and_empty_tree(self):
        c1 = self.commit([], {"a/b/c": b"1"})
        c2 = self.commit([c1], {"a/b/c": None})
        self.assertEqual(self.repo.root_tree(c2), EMPTY_TREE_ID)

    def test_incremental_trees_share_structure(self):
        files = {f"d{i}/f{j}": f"{i}{j}".encode() for i in range(10) for j in range(10)}
        c1 = self.commit([], files)
        c2 = self.commit([c1], {"d3/f3": b"changed"})
        r1, r2 = self.repo.root_tree(c1), self.repo.root_tree(c2)
        t1, t2 = self.repo.trees.read(r1), self.repo.trees.read(r2)
        same = [n for n in t1 if t1[n] == t2[n]]
        self.assertEqual(len(same), 9)  # only d3 was rewritten

    def test_diff_scoped(self):
        c1 = self.commit([], {"a/x": b"1", "b/y": b"2"})
        c2 = self.commit([c1], {"a/x": b"3", "b/y": b"4", "b/z": b"5"})
        self.assertEqual({f["path"] for f in self.repo.diff(c1, c2)}, {"a/x", "b/y", "b/z"})
        self.assertEqual({f["path"] for f in self.repo.diff(c1, c2, paths=["b"])}, {"b/y", "b/z"})
        text = self.repo.diff_text(c1, c2, paths=["a/x"])
        self.assertIn("-1", text)
        self.assertIn("+3", text)


class TestDerived(RepoTestCase):
    def test_generic_mechanism_and_eager_vs_deferred(self):
        c1 = self.commit([], {"f": b"1\n"})
        c2 = self.commit([c1], {"f": b"1\n2\n"})
        for t in ("tree", "graph", "history", "copies", "search"):
            self.assertIsNotNone(self.repo.meta.derived_get(t, c2), t)
        self.assertIsNone(self.repo.meta.derived_get("blame", c2))  # deferred until asked
        self.repo.blame(c2, "f")
        self.assertIsNotNone(self.repo.meta.derived_get("blame", c2))
        self.assertIsNotNone(self.repo.meta.derived_get("blame", c1))  # ancestors derived first

    def test_new_derived_type_can_be_registered(self):
        from scion.derived import DerivedType

        class FileCount(DerivedType):
            name = "filecount"
            depends_on = ("tree",)

            def derive(self, repo, cs_id, cs, parent_values):
                base = int(parent_values[0]) if parent_values else 0
                return str(base + sum(1 if c.op == "A" else -1 if c.op == "D" else 0 for c in cs.changes))

        self.repo.derived.register(FileCount())
        c1 = self.commit([], {"a": b"1", "b": b"2"})
        c2 = self.commit([c1], {"a": None, "c": b"3", "d": b"4"})
        self.assertEqual(self.repo.derived.get("filecount", c2), "3")

    def test_copy_and_rename_detection(self):
        c1 = self.commit([], {"src/a.py": b"print('a')\n", "src/b.py": b"print('b')\n"})
        c2 = self.commit([c1], {"src/a.py": None, "lib/a.py": b"print('a')\n", "lib/b2.py": b"print('b')\n"})
        copies = json.loads(self.repo.derived.get("copies", c2))
        self.assertEqual(copies["lib/a.py"], {"from": "src/a.py", "type": "rename"})
        self.assertEqual(copies["lib/b2.py"], {"from": "src/b.py", "type": "copy"})
        hist = self.repo.file_history(c2, "lib/a.py")
        self.assertEqual([h["cs"] for h in hist], [c2, c1])
        self.assertEqual(hist[1]["path"], "src/a.py")

    def test_history_of_files_and_directories(self):
        c1 = self.commit([], {"a/x": b"1", "b/y": b"1"})
        c2 = self.commit([c1], {"b/y": b"2"})
        c3 = self.commit([c2], {"a/x": b"2"})
        c4 = self.commit([c3], {"b/y": b"3"})
        self.assertEqual([h["cs"] for h in self.repo.file_history(c4, "a/x")], [c3, c1])
        self.assertEqual([h["cs"] for h in self.repo.file_history(c4, "b")], [c4, c2, c1])
        self.assertEqual(self.repo.log(c4, path="a"), [c3, c1])

    def test_blame_linear_and_copy(self):
        c1 = self.commit([], {"f": b"a\nb\nc\n"}, author="ann")
        c2 = self.commit([c1], {"f": b"a\nB\nc\nd\n"}, author="bob")
        c3 = self.commit([c2], {"g": b"a\nB\nc\nd\n", "f": None}, author="cat")  # rename
        lines = self.repo.blame(c3, "g")["lines"]
        self.assertEqual([l["cs"] for l in lines], [c1, c2, c1, c2])
        self.assertEqual([l["origin_line"] for l in lines], [1, 2, 3, 4])

    def test_blame_across_merges_credits_true_authors(self):
        base = self.commit([], {"f": b"1\n2\n3\n"})
        left = self.commit([base], {"f": b"1\nL\n3\n"})
        right = self.commit([base], {"f": b"1\n2\n3\nR\n"})
        m = self.repo.merge(left, right, "merger")
        self.assertEqual(self.repo.read_file(m, "f")[2], b"1\nL\n3\nR\n")
        by_line = {l["text"]: l["cs"] for l in self.repo.blame(m, "f")["lines"]}
        self.assertEqual(by_line, {"1\n": base, "L\n": left, "3\n": base, "R\n": right})

    def test_merge_takes_other_parents_history(self):
        base = self.commit([], {"f": b"1\n", "g": b"1\n"})
        left = self.commit([base], {"f": b"2\n"})
        right = self.commit([base], {"g": b"2\n"})
        m = self.repo.merge(left, right, "merger")
        self.assertEqual(self.repo.file_history(m, "g")[0]["cs"], right)


class TestAncestry(RepoTestCase):
    def _chain(self, start, n, tag):
        cur = start
        out = []
        for i in range(n):
            cur = self.commit([cur], {f"{tag}": f"{tag}{i}".encode()})
            out.append(cur)
        return out

    def test_skip_lists_and_generations(self):
        root = self.commit([], {"f": b"0"})
        chain = self._chain(root, 100, "f")
        tip = chain[-1]
        self.assertEqual(self.repo.generation(tip), 101)
        self.assertEqual(self.repo.fp_ancestor(tip, 37), chain[-38])
        self.assertEqual(self.repo.fp_ancestor(tip, 100), root)
        self.assertIsNone(self.repo.fp_ancestor(tip, 101))
        self.repo.stats.clear()
        self.assertTrue(self.repo.is_ancestor(root, tip))
        self.assertLess(self.repo.stats["ancestry.visits"] + self.repo.stats["ancestry.hops"], 20)
        self.assertFalse(self.repo.is_ancestor(tip, root))

    def test_merge_base_through_merges(self):
        root = self.commit([], {"f": b"0"})
        main = self._chain(root, 30, "m")
        branch = self._chain(main[9], 20, "b")
        m = self.repo.merge(main[-1], branch[-1], "x")
        more = self._chain(m, 5, "m")
        self.assertEqual(self.repo.merge_base(branch[-1], main[-1]), main[9])
        self.assertEqual(self.repo.merge_base(more[-1], branch[-1]), branch[-1])
        self.assertTrue(self.repo.is_ancestor(branch[5], more[-1]))
        side = self._chain(main[20], 3, "s")
        self.assertEqual(self.repo.merge_base(side[-1], more[-1]), main[20])


class TestMergeRebaseRevert(RepoTestCase):
    def test_merge3(self):
        base = b"a\nb\nc\nd\n"
        self.assertEqual(merge3(base, b"A\nb\nc\nd\n", b"a\nb\nc\nD\n"), (b"A\nb\nc\nD\n", 0))
        out, n = merge3(base, b"a\nX\nc\nd\n", b"a\nY\nc\nd\n")
        self.assertEqual(n, 1)
        self.assertIn(b"<<<<<<<", out)
        self.assertEqual(merge3(base, b"a\nb\nc\nd\ne\n", b"a\nb\nc\nd\ne\n"), (b"a\nb\nc\nd\ne\n", 0))

    def test_rebase_stack_and_conflicts(self):
        base = self.commit([], {"f": b"1\n2\n3\n", "g": b"x\n"})
        upstream = self.commit([base], {"f": b"1\n2\n3\n4\n"})
        s1 = self.commit([base], {"f": b"0\n1\n2\n3\n"})
        s2 = self.commit([s1], {"h": b"new\n"})
        r = self.repo.rebase(s2, upstream)
        self.assertEqual(set(r["rebased"]), {s1, s2})
        self.assertEqual(self.tree_files(r["head"]), {"f": b"0\n1\n2\n3\n4\n", "g": b"x\n", "h": b"new\n"})
        self.assertEqual(self.repo.get_changeset(r["head"]).extra["rebased_from"], s2)
        clash = self.commit([base], {"g": b"y\n"})
        upstream2 = self.commit([upstream], {"g": b"z\n"})
        with self.assertRaises(MergeConflict) as cm:
            self.repo.rebase(clash, upstream2)
        self.assertEqual(cm.exception.conflicts[0]["path"], "g")

    def test_rebase_drops_already_applied(self):
        base = self.commit([], {"f": b"1\n"})
        up = self.commit([base], {"f": b"2\n"})
        mine = self.commit([base], {"f": b"2\n"})
        r = self.repo.rebase(mine, up)
        self.assertEqual(r["head"], up)

    def test_revert(self):
        c1 = self.commit([], {"f": b"1\n2\n3\n"})
        c2 = self.commit([c1], {"f": b"1\nTWO\n3\n", "new": b"n"})
        c3 = self.commit([c2], {"f": b"1\nTWO\n3\n4\n"})
        rv = self.repo.revert(c2, c3, "bot")
        self.assertEqual(self.tree_files(rv), {"f": b"1\n2\n3\n4\n"})
        self.assertEqual(self.repo.get_changeset(rv).extra["reverts"], c2)

    def test_modify_delete_conflict(self):
        b = self.commit([], {"f": b"1\n"})
        a = self.commit([b], {"f": None})
        c = self.commit([b], {"f": b"2\n"})
        with self.assertRaises(MergeConflict):
            self.repo.merge(a, c, "x")


if __name__ == "__main__":
    unittest.main()

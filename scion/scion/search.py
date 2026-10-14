"""Code search (FR-SR-*). Path search over the derived search tree (FR-DD-12, FR-SR-01)."""
from __future__ import annotations

from .derived_types import bloom_may_contain, name_trigrams
from .objects import KIND_DIR, join


def search_paths(repo, rev: str, query: str, limit: int = 100, user=None) -> dict:
    """Files whose path contains ``query`` (case-insensitive). Every directory entry carries a bloom
    filter of the trigrams of all names beneath it, so a subtree that cannot contain a match is
    skipped without being read. Returns the paths and how many search-tree nodes were read."""
    cs = repo.resolve(rev)
    q = query.lower()
    last = q.rsplit("/", 1)[-1]
    grams = name_trigrams(last) if len(last) >= 3 else set()
    results, visited, stack = [], 0, [(repo.search_root(cs), "")]
    while stack and len(results) < limit:
        node, prefix = stack.pop()
        visited += 1
        entries = repo.read_stree(node)
        for name in sorted(entries, reverse=True):
            kind, oid, bloom = entries[name]
            path = join(prefix, name)
            if kind == KIND_DIR:
                if not grams or q in path.lower() or bloom_may_contain(bloom, grams):
                    stack.append((oid, path))
            elif q in path.lower() and repo.policy.can_read(user, path):
                results.append(path)
                if len(results) >= limit:
                    break
    return {"paths": sorted(results), "trees_visited": visited}

"""Code search: path search over the derived search tree, and server-side grep."""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor

from .derived_types import bloom_may_contain, name_trigrams
from .objects import KIND_DIR, is_binary, normalize_path


def search_paths(repo, rev: str, query: str, limit: int = 100, user: str | None = None) -> dict:
    """Find files whose path contains ``query`` (case-insensitive).

    Every directory entry in the search tree carries a bloom filter of the trigrams of all names
    beneath it, so whole subtrees that cannot contain a match are skipped without being read."""
    cs = repo.resolve(rev)
    q = query.lower()
    last = q.rsplit("/", 1)[-1]
    grams = name_trigrams(last) if len(last) >= 3 else set()
    root = repo.search_root(cs)
    results: list[str] = []
    visited = 0
    stack = [(root, "")]
    while stack and len(results) < limit:
        sid, prefix = stack.pop()
        visited += 1
        entries = repo.read_stree(sid)
        for name in sorted(entries, reverse=True):
            kind, oid, bloom = entries[name]
            path = f"{prefix}/{name}" if prefix else name
            if user is not None and not repo.policy.can_read(user, path):
                continue
            if kind == KIND_DIR:
                if not grams or bloom_may_contain(bloom, grams) or q in path.lower():
                    stack.append((oid, path))
            elif q in path.lower():
                results.append(path)
                if len(results) >= limit:
                    break
    return {"paths": sorted(results), "trees_visited": visited}


def grep(repo, rev: str, pattern: str, path_prefix: str = "", limit: int = 200,
         regex: bool = True, ignore_case: bool = False, user: str | None = None) -> dict:
    """Search file contents on the server, so callers need no checkout."""
    cs = repo.resolve(rev)
    flags = re.IGNORECASE if ignore_case else 0
    rx = re.compile(pattern if regex else re.escape(pattern), flags)
    prefix = normalize_path(path_prefix)
    e = repo.lookup(cs, prefix)
    if e is None:
        return {"matches": [], "files_scanned": 0, "truncated": False}
    if e[0] == KIND_DIR:
        files = [(p, oid) for p, kind, oid in repo.trees.walk(e[1], prefix) if kind != "l"]
    else:
        files = [(prefix, e[1])]
    if user is not None:
        files = [(p, oid) for p, oid in files if repo.policy.can_read(user, p)]
    matches: list[dict] = []
    truncated = False

    def scan(item):
        path, oid = item
        data = repo.read_blob(oid)
        if is_binary(data):
            return []
        found = []
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines()):
            if rx.search(line):
                found.append({"path": path, "line": i + 1, "text": line[:500]})
        return found

    with ThreadPoolExecutor(max_workers=8) as pool:
        for found in pool.map(scan, files):
            for m in found:
                if len(matches) >= limit:
                    truncated = True
                    break
                matches.append(m)
            if truncated:
                break
    return {"matches": matches, "files_scanned": len(files), "truncated": truncated}

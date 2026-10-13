"""Code search (FR-SR-*): path search over the derived search tree (FR-SR-01, FR-DD-12) and content
search on the server, with no checkout (FR-SR-02), backed by the trigram content index (FR-SR-03,
ADR-16). Every result is filtered by the caller's permissions (FR-SR-04).
"""
from __future__ import annotations

import re

from .derived_types import bloom_may_contain, name_trigrams, text_trigrams
from .objects import KIND_DIR, KIND_LINK, is_binary, join, normalize_path

try:  # the regular-expression parser: re._parser from Python 3.11, sre_parse before
    from re import _parser as sre_parse
except ImportError:  # pragma: no cover
    import sre_parse

MAX_POSTINGS = 200_000  # a trigram this common prunes little: leave it out of the intersection


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


def required_literals(pattern: str) -> list[str]:
    """Literal strings every match of ``pattern`` must contain: the runs of plain characters in its
    top-level sequence. An alternation at the top level requires nothing."""
    try:
        parsed = sre_parse.parse(pattern)
    except re.error as e:
        raise ValueError(f"bad regular expression: {e}") from None
    runs, cur = [], []
    for op, arg in parsed:
        if op is sre_parse.LITERAL:
            cur.append(chr(arg))
            continue
        if op is sre_parse.BRANCH:
            return []
        if cur:  # anything else ends a run of required characters
            runs.append("".join(cur))
            cur = []
    if cur:
        runs.append("".join(cur))
    return runs


def _under(path: str, prefix: str) -> bool:
    return not prefix or path == prefix or path.startswith(prefix + "/")


def grep(repo, rev: str, pattern: str, path: str = "", limit: int = 200, regex: bool = True,
         ignore_case: bool = False, user=None) -> dict:
    """Lines matching ``pattern`` in the files under ``path`` at ``rev``.

    When the pattern contains literal text of three or more characters, the content index narrows
    the blobs to those containing all of its trigrams; the blob → path index then finds where those
    blobs are, so only candidate files are read, whatever the repository's size (ADR-16). Otherwise
    every file under ``path`` is read."""
    cs = repo.resolve(rev)
    try:
        rx = re.compile(pattern if regex else re.escape(pattern), re.IGNORECASE if ignore_case else 0)
    except re.error as e:
        raise ValueError(f"bad regular expression: {e}") from None
    prefix = normalize_path(path)
    if prefix and not repo.policy.can_read(user, prefix) and not getattr(repo.policy, "readable_beneath",
                                                                           lambda u, p: False)(user, prefix):
        from .iam import PermissionDenied
        raise PermissionDenied(f"{user} may not read {prefix}")
    literals = required_literals(pattern) if regex else [pattern]
    grams = set()
    for lit in literals:
        if len(lit) >= 3:
            grams |= text_trigrams(lit)
    root = repo.root_tree(cs)
    if grams:
        locations = _indexed_locations(repo, cs, root, grams, prefix)
    else:
        start = repo.trees.lookup(root, prefix) if prefix else ("d", root)
        if start is None:
            locations = []
        elif start[0] != KIND_DIR:
            locations = [(prefix, start[0], start[1])]
        else:
            locations = list(repo.trees.walk(start[1], prefix))
    matches, scanned, truncated = [], 0, False
    for p, kind, blob in locations:
        if kind == KIND_LINK or not repo.policy.can_read(user, p):
            continue
        data = repo.read_blob(blob)
        scanned += 1
        if is_binary(data):
            continue
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            if rx.search(line):
                if len(matches) >= limit:
                    truncated = True
                    break
                matches.append({"path": p, "line": i, "text": line})
        if truncated:
            break
    return {"matches": matches, "files_scanned": scanned, "indexed": bool(grams), "truncated": truncated}


def _indexed_locations(repo, cs: str, root: str, grams: set[str], prefix: str) -> list[tuple]:
    repo.derived.get("content", cs)  # every blob written up to cs is indexed
    counts = sorted((repo.meta.content_count(g), g) for g in grams)
    usable = [g for n, g in counts if n <= MAX_POSTINGS] or [counts[0][1]]
    candidates: set[str] | None = None
    for g in usable:
        postings = repo.meta.content_postings(g)
        candidates = postings if candidates is None else candidates & postings
        if not candidates:
            break
    candidates = set(candidates or ()) | set(repo.meta.content_unindexed())
    out = []
    for blob in candidates:
        for p in repo.meta.blob_index_paths(blob, limit=1_000_000):
            if _under(p, prefix):
                e = repo.trees.lookup(root, p)
                if e is not None and e[0] != KIND_DIR and e[1] == blob:
                    out.append((p, e[0], blob))
    return sorted(set(out))

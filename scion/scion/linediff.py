"""Line diffs whose cost follows the change, not the file (blame, FR-DD-09; merges, FR-WR-02/03).

Myers' O((N+M)·D) algorithm runs after the common prefix and suffix are matched. Most changes
touch a small part of a large file, so a diff costs about the size of the change: the CPython pilot
found whole-file difflib matching taking minutes per hot file. An edit of more than MAX_EDIT lines
(a rewrite) falls back to difflib.
"""
from __future__ import annotations

import difflib

MAX_EDIT = 2000  # insertions plus deletions beyond which a diff falls back to difflib


def matching_blocks(old: list, new: list) -> list[tuple]:
    """``(i, j, size)`` runs where ``old[i:i+size] == new[j:j+size]``, in order, ending with the
    ``(len(old), len(new), 0)`` sentinel, as difflib's ``get_matching_blocks`` returns them; together
    they are a longest common subsequence."""
    n = min(len(old), len(new))
    p = 0
    while p < n and old[p] == new[p]:
        p += 1
    s = 0
    while s < n - p and old[-1 - s] == new[-1 - s]:
        s += 1
    a, b = old[p:len(old) - s], new[p:len(new) - s]
    blocks = _myers(a, b, MAX_EDIT)
    if blocks is None:
        blocks = [m for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks() if m[2]]
    return ([(0, 0, p)] if p else []) + [(i + p, j + p, k) for i, j, k in blocks] \
        + ([(len(old) - s, len(new) - s, s)] if s else []) + [(len(old), len(new), 0)]


def opcodes(old: list, new: list) -> list[tuple]:
    """The edit from ``old`` to ``new`` as difflib-style opcodes."""
    ops, i, j = [], 0, 0
    for bi, bj, size in matching_blocks(old, new):
        tag = "replace" if i < bi and j < bj else "delete" if i < bi else "insert" if j < bj else None
        if tag:
            ops.append((tag, i, bi, j, bj))
        if size:
            ops.append(("equal", bi, bi + size, bj, bj + size))
        i, j = bi + size, bj + size
    return ops


def _myers(a: list, b: list, max_d: int):
    """Matching blocks ``(i, j, size)`` of a shortest edit script from ``a`` to ``b`` (Myers 1986), or
    None when it needs more than ``max_d`` insertions and deletions."""
    n, m = len(a), len(b)
    off = max_d + 1
    v = [0] * (2 * max_d + 3)
    trace = []
    for d in range(max_d + 1):
        trace.append(v[off - d - 1:off + d + 2])  # the furthest x on each diagonal k, before round d
        for k in range(-d, d + 1, 2):
            x = v[off + k + 1] if k == -d or (k != d and v[off + k - 1] < v[off + k + 1]) else v[off + k - 1] + 1
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[off + k] = x
            if x >= n and y >= m:
                return _myers_blocks(trace, d, n, m)
    return None


def _myers_blocks(trace: list, d_end: int, n: int, m: int) -> list[tuple]:
    blocks, x, y = [], n, m
    for d in range(d_end, 0, -1):
        prev, k = trace[d], x - y  # prev[k + d + 1] is diagonal k after round d - 1
        down = k == -d or (k != d and prev[k + d] < prev[k + d + 2])
        pk = k + 1 if down else k - 1
        px = prev[pk + d + 1]
        py = px - pk
        sx = px if down else px + 1  # where the snake after this round's one insertion or deletion starts
        if x > sx:
            blocks.append((sx, sx - k, x - sx))
        x, y = px, py
    if x:
        blocks.append((0, 0, x))
    blocks.reverse()
    return blocks

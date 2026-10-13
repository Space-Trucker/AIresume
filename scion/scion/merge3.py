"""Line-based three-way merge (diff3 semantics) used by server-side merge, rebase and revert."""
from __future__ import annotations

from difflib import SequenceMatcher


def _intersect(ra: tuple[int, int], rb: tuple[int, int]):
    lo = max(ra[0], rb[0])
    hi = min(ra[1], rb[1])
    return (lo, hi) if lo < hi else None


def _sync_regions(base, a, b):
    amatches = SequenceMatcher(None, base, a, autojunk=False).get_matching_blocks()
    bmatches = SequenceMatcher(None, base, b, autojunk=False).get_matching_blocks()
    ia = ib = 0
    out = []
    while ia < len(amatches) and ib < len(bmatches):
        abase, amatch, alen = amatches[ia]
        bbase, bmatch, blen = bmatches[ib]
        i = _intersect((abase, abase + alen), (bbase, bbase + blen))
        if i:
            intbase, intend = i
            intlen = intend - intbase
            asub = amatch + (intbase - abase)
            bsub = bmatch + (intbase - bbase)
            out.append((intbase, intend, asub, asub + intlen, bsub, bsub + intlen))
        if abase + alen < bbase + blen:
            ia += 1
        else:
            ib += 1
    out.append((len(base), len(base), len(a), len(a), len(b), len(b)))
    return out


def merge_regions(base, a, b):
    """Yield ('unchanged'|'a'|'b'|'same', lines) or ('conflict', (base, a, b))."""
    iz = ia = ib = 0
    for zmatch, zend, amatch, aend, bmatch, bend in _sync_regions(base, a, b):
        if amatch - ia or bmatch - ib:
            a_part, b_part, z_part = a[ia:amatch], b[ib:bmatch], base[iz:zmatch]
            if a_part == b_part:
                yield "same", a_part
            else:
                eq_a = z_part == a_part
                eq_b = z_part == b_part
                if eq_a and not eq_b:
                    yield "b", b_part
                elif eq_b and not eq_a:
                    yield "a", a_part
                else:
                    yield "conflict", (z_part, a_part, b_part)
            ia, ib = amatch, bmatch
        iz = zmatch
        if zend > zmatch:
            yield "unchanged", base[zmatch:zend]
            iz, ia, ib = zend, aend, bend


def merge3_lines(base: list, a: list, b: list, labels=("ours", "theirs")) -> tuple[list, int]:
    out: list = []
    conflicts = 0
    for kind, payload in merge_regions(base, a, b):
        if kind == "conflict":
            conflicts += 1
            _, pa, pb = payload
            out.append(f"<<<<<<< {labels[0]}\n".encode())
            out.extend(_terminated(pa))
            out.append(b"=======\n")
            out.extend(_terminated(pb))
            out.append(f">>>>>>> {labels[1]}\n".encode())
        else:
            out.extend(payload)
    return out, conflicts


def _terminated(lines: list) -> list:
    if lines and not lines[-1].endswith(b"\n"):
        return lines[:-1] + [lines[-1] + b"\n"]
    return lines


def merge3(base: bytes, ours: bytes, theirs: bytes) -> tuple[bytes, int]:
    """Merge bytes; return (result, number_of_conflicts)."""
    if ours == theirs:
        return ours, 0
    if base == ours:
        return theirs, 0
    if base == theirs:
        return ours, 0
    lines, conflicts = merge3_lines(
        base.splitlines(keepends=True), ours.splitlines(keepends=True), theirs.splitlines(keepends=True)
    )
    return b"".join(lines), conflicts

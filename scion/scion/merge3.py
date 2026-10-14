"""Line-based three-way merge with diff3 semantics (FR-WR-02/03/04)."""
from __future__ import annotations

from difflib import SequenceMatcher


def _sync_regions(base, a, b):
    """Regions where base, a and b all agree: (zstart, zend, astart, aend, bstart, bend)."""
    am = SequenceMatcher(None, base, a, autojunk=False).get_matching_blocks()
    bm = SequenceMatcher(None, base, b, autojunk=False).get_matching_blocks()
    ia = ib = 0
    out = []
    while ia < len(am) and ib < len(bm):
        abase, amatch, alen = am[ia]
        bbase, bmatch, blen = bm[ib]
        lo, hi = max(abase, bbase), min(abase + alen, bbase + blen)
        if lo < hi:
            asub, bsub = amatch + (lo - abase), bmatch + (lo - bbase)
            out.append((lo, hi, asub, asub + hi - lo, bsub, bsub + hi - lo))
        if abase + alen < bbase + blen:
            ia += 1
        else:
            ib += 1
    out.append((len(base), len(base), len(a), len(a), len(b), len(b)))
    return out


def merge_regions(base, a, b):
    """Yield ("unchanged"|"a"|"b"|"same", lines) or ("conflict", (base, a, b))."""
    iz = ia = ib = 0
    for zm, ze, am, ae, bm, be in _sync_regions(base, a, b):
        if am > ia or bm > ib:
            pa, pb, pz = a[ia:am], b[ib:bm], base[iz:zm]
            if pa == pb:
                yield "same", pa
            elif pz == pa:
                yield "b", pb
            elif pz == pb:
                yield "a", pa
            else:
                yield "conflict", (pz, pa, pb)
            ia, ib = am, bm
        iz = zm
        if ze > zm:
            yield "unchanged", base[zm:ze]
            iz, ia, ib = ze, ae, be


def _terminated(lines):
    if lines and not lines[-1].endswith(b"\n"):
        return lines[:-1] + [lines[-1] + b"\n"]
    return lines


def merge3(base: bytes, ours: bytes, theirs: bytes, labels=("ours", "theirs")) -> tuple[bytes, int]:
    """Return (merged bytes, number of conflicting hunks). Conflicts are marked diff3-style."""
    if ours == theirs:
        return ours, 0
    if base == ours:
        return theirs, 0
    if base == theirs:
        return ours, 0
    out, conflicts = [], 0
    for kind, payload in merge_regions(base.splitlines(keepends=True), ours.splitlines(keepends=True),
                                       theirs.splitlines(keepends=True)):
        if kind == "conflict":
            conflicts += 1
            _, pa, pb = payload
            out += [f"<<<<<<< {labels[0]}\n".encode(), *_terminated(pa), b"=======\n", *_terminated(pb),
                    f">>>>>>> {labels[1]}\n".encode()]
        else:
            out += payload
    return b"".join(out), conflicts

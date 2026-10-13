"""Automated bisect over the source-control API.

The first-parent range between ``good`` and ``bad`` comes from the server (no clone).  Each probe
runs a predicate.  A predicate can be API-only (``file_matches``: no checkout at all) or run a
command in one reusable sparse checkout that ``update`` moves between probes, which costs only
the diff between them.
"""
from __future__ import annotations

import base64
import re
import subprocess
from typing import Callable

from ..client import ServerApi, WorkingCopy


def first_parent_range(api: ServerApi, good: str, bad: str, max_len: int = 1_000_000) -> list[str]:
    """[bad, ..., good] along the first-parent chain."""
    good = api.resolve(rev=good)
    bad = api.resolve(rev=bad)
    if not api.is_ancestor(a=good, b=bad):
        raise ValueError("good must be an ancestor of bad")
    chain: list[str] = []
    skip = 0
    while True:
        page = api.log(rev=bad, limit=1000, skip=skip, ids_only=True)
        if not page:
            raise ValueError("good is not on the first-parent chain of bad")
        for cs in page:
            chain.append(cs)
            if cs == good:
                return chain
        skip += len(page)
        if skip > max_len:
            raise ValueError("range too large")


def bisect(api: ServerApi, good: str, bad: str, is_good: Callable[[str], bool], log=print) -> dict:
    chain = first_parent_range(api, good, bad)
    lo, hi = 0, len(chain) - 1  # chain[lo] is bad, chain[hi] is good
    probes = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        probes += 1
        ok = is_good(chain[mid])
        log(f"probe {probes}: {chain[mid][:12]} is {'good' if ok else 'bad'}")
        if ok:
            hi = mid
        else:
            lo = mid
    culprit = chain[lo]
    cs = api.get_changeset(rev=culprit)
    return {"first_bad": culprit, "author": cs["author"], "summary": cs["message"].splitlines()[0] if cs["message"] else "",
            "probes": probes, "range": len(chain)}


def file_matches(api: ServerApi, path: str, pattern: str, good_if_present: bool) -> Callable[[str], bool]:
    rx = re.compile(pattern)

    def check(cs: str) -> bool:
        try:
            data = base64.b64decode(api.read_file(rev=cs, path=path)["content_b64"]).decode("utf-8", "replace")
            present = bool(rx.search(data))
        except Exception:
            present = False
        return present if good_if_present else not present
    return check


def command_predicate(wc: WorkingCopy, cmd: str, timeout: float = 3600) -> Callable[[str], bool]:
    def check(cs: str) -> bool:
        wc.update(cs, clean=True)
        return subprocess.run(cmd, shell=True, cwd=wc.root, timeout=timeout,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    return check

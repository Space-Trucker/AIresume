"""Automated bisect over the API (FR-AUT-01, UC-20).

The first-parent range between ``good`` and ``bad`` comes from the server, with no clone. Each probe
runs a predicate: API-only (``file_matches`` reads one file through the API) or a command run in a
reusable checkout that ``update`` moves between probes, fetching only the diff.
"""
from __future__ import annotations

import base64
import re
import subprocess
from typing import Callable

from ..rpc import RemoteError


def first_parent_range(api, good: str, bad: str, max_len: int = 1_000_000) -> list[str]:
    """``[bad, ..., good]`` along the first-parent chain."""
    good, bad = api.resolve(rev=good), api.resolve(rev=bad)
    if not api.is_ancestor(a=good, b=bad):
        raise ValueError("good must be an ancestor of bad")
    chain, skip = [], 0
    while skip <= max_len:
        page = api.log(rev=bad, limit=1000, skip=skip, ids_only=True)
        if not page:
            break
        for cs in page:
            chain.append(cs)
            if cs == good:
                return chain
        skip += len(page)
    raise ValueError("good is not on the first-parent chain of bad")


def bisect(api, good: str, bad: str, is_good: Callable[[str], bool], log=None) -> dict:
    """Find the first bad changeset: ⌈log2(n)⌉ probes or fewer for a range of n changesets."""
    chain = first_parent_range(api, good, bad)
    lo, hi, probes = 0, len(chain) - 1, 0  # chain[lo] is bad, chain[hi] is good
    while hi - lo > 1:
        mid = (lo + hi) // 2
        probes += 1
        ok = is_good(chain[mid])
        if log:
            log(f"probe {probes}: {chain[mid][:12]} is {'good' if ok else 'bad'}")
        if ok:
            hi = mid
        else:
            lo = mid
    culprit = api.get_changeset(rev=chain[lo])
    return {"first_bad": chain[lo], "author": culprit["author"],
            "summary": culprit["message"].splitlines()[0] if culprit["message"] else "",
            "probes": probes, "range": len(chain)}


def file_matches(api, path: str, pattern: str, good_if_present: bool = True) -> Callable[[str], bool]:
    """A predicate that reads one file through the API: no checkout at all."""
    rx = re.compile(pattern)

    def check(cs: str) -> bool:
        try:
            data = base64.b64decode(api.read_file(rev=cs, path=path)["content_b64"]).decode("utf-8", "replace")
            present = bool(rx.search(data))
        except RemoteError as e:
            if e.status != 404:
                raise
            present = False
        return present == good_if_present
    return check


def command_predicate(wc, cmd: str, timeout: float = 3600) -> Callable[[str], bool]:
    """A predicate that runs a command in a reusable checkout."""
    def check(cs: str) -> bool:
        wc.update(cs, clean=True)
        return subprocess.run(cmd, shell=True, cwd=wc.root, timeout=timeout, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL).returncode == 0
    return check

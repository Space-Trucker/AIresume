"""Automated revert pipeline: revert a changeset on the server and land it through Antique's
lock-free landing path.  It works entirely through the API, with no checkout."""
from __future__ import annotations

from ..client import ServerApi


def revert_and_land(api: ServerApi, cs: str, ref: str = "main", message: str | None = None) -> str:
    """Create the revert on top of the current tip, then hand it to the server's landing path,
    which rebases it if the tip has moved and publishes it with a compare-and-swap."""
    cs = api.resolve(rev=cs)
    tip = api.get_ref(name=ref)
    revert = api.revert(cs=cs, onto=tip, message=message)
    return api.antique__land_changeset(cs=revert, ref=ref)["landed_cs"]


def revert_landing(api: ServerApi, cs: str, ref: str = "main") -> list[str]:
    """Revert every changeset that landed together with ``cs`` (a whole stack), newest first."""
    landing = api.antique__find_landing(cs=cs)
    stack = [api.resolve(rev=cs)]
    if landing and landing.get("cr") is not None:
        cur = api.get_changeset(rev=stack[0])["parents"]
        while cur:
            parent = cur[0]
            info = api.antique__find_landing(cs=parent)
            if not info or info.get("cr") != landing["cr"]:
                break
            stack.append(parent)
            cur = api.get_changeset(rev=parent)["parents"]
    return [revert_and_land(api, c, ref) for c in stack]

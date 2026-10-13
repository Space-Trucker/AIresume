"""The revert pipeline over the API (FR-AUT-02, UC-21).

The server builds each revert on top of the current tip, and Antique's landing path publishes it:
if the tip moved meanwhile, the revert is rebased and the ref is compare-and-swapped, so a revert
lands while others are landing concurrently. No checkout is needed.
"""
from __future__ import annotations


def revert_and_land(api, cs: str, ref: str = "main", message: str | None = None) -> str:
    """Revert one changeset on top of ``ref`` and land it; returns the landed revert."""
    params = {"cs": cs, "onto": ref}
    if message:
        params["message"] = message
    revert = api.revert(**params)
    return api.call("antique.land_changeset", cs=revert, ref=ref)["landed_cs"]


def landed_stack(api, cs: str) -> list[str]:
    """Every changeset of the landing that produced ``cs``, newest first (an indexed lookup)."""
    return api.call("antique.landing_stack", cs=cs) or [cs]


def revert_landing(api, cs: str, ref: str = "main") -> list[str]:
    """Revert a whole landed stack, newest first, each through the landing path (UC-18 3a)."""
    return [revert_and_land(api, x, ref) for x in landed_stack(api, cs)]

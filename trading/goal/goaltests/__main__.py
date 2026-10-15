"""Run every test of a goal file: python3 -m goaltests [goal.toml] [--json results.json]

Exit status 0 when every check passes, 1 otherwise. Informational lines (no verdict) are shown with
'·'. Simulations use fixed seeds, so a run repeats exactly."""
from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
import time

from . import (gt01_quality, gt02_consistency, gt03_costs, gt04_power, gt05_null_real, gt06_goodhart,
               gt07_controls, gt08_outside, gt10_mutation)
from .spec import HERE, KINDS, load

TESTS = [("GT-1 statement quality (ISO/IEC/IEEE 29148)", gt01_quality),
         ("GT-2 internal consistency", gt02_consistency),
         ("GT-3 cost feasibility by horizon", gt03_costs),
         ("GT-4 do the gates tell skill from luck", gt04_power),
         ("GT-5 random strategies on real prices", gt05_null_real),
         ("GT-6 metric gaming", gt06_goodhart),
         ("GT-7 control coverage", gt07_controls),
         ("GT-8 outside view", gt08_outside),
         ("GT-10 deliberate defects", gt10_mutation)]
# GT-9, the independent review, is done by people and other models, not by this program


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python3 -m goaltests")
    p.add_argument("spec", nargs="?", default=os.path.join(HERE, "goal.toml"))
    p.add_argument("--json", help="also write the results here")
    p.add_argument("--only", help="comma-separated test numbers, e.g. 1,2,7")
    a = p.parse_args(argv)
    spec = load(a.spec)
    only = {int(x) for x in a.only.split(",")} if a.only else None
    ctx: dict = {}
    results, failed = [], 0
    print(f"goal: {os.path.relpath(spec['_path'])} (version {spec.get('meta', {}).get('version', '?')})")
    for title, mod in TESTS:
        i = int(title.split()[0].split("-")[1])
        if only and i not in only:
            continue
        t0 = time.time()
        kwargs = {"ctx": ctx} if "ctx" in inspect.signature(mod.run).parameters else {}
        checks = mod.run(spec, **kwargs)
        bad = sum(1 for c in checks if c.passed is False)
        failed += bad
        print(f"\n{title}: {'pass' if not bad else f'{bad} failing'} ({time.time() - t0:.0f}s)")
        for c in checks:
            mark = "·" if c.passed is None else ("✓" if c.passed else "✗")
            kind = "" if c.passed is None else (c.kind or getattr(mod, "KIND", "presence"))
            print(f"  {mark} {c.name}" + (f": {c.detail}" if c.detail else ""))
            results.append({"test": c.test, "check": c.name, "passed": c.passed, "detail": c.detail, "kind": kind})
    total = sum(1 for r in results if r["passed"] is not None)
    print(f"\n{total - failed}/{total} checks pass")
    by_kind = []
    for kind in KINDS:
        rows = [r for r in results if r["kind"] == kind]
        if rows:
            by_kind.append(f"{kind} {sum(1 for r in rows if r['passed'])}/{len(rows)}")
    print("by what they rest on: " + "; ".join(by_kind) + " (external: the answer and the bar both from outside the goal)")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"spec": os.path.relpath(spec["_path"], HERE), "version": spec.get("meta", {}).get("version"),
                       "passed": total - failed, "total": total, "results": results}, f, indent=1)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

"""Thin wrapper over goaltests: runs the chosen test modules in order exactly as goaltests/__main__.py
does (same run() calls, same shared ctx), but can save GT-4's context to a file or load it, so GT-8
can be scored against real GT-4 results without rerunning GT-4.

usage: run_ctx.py GOAL.toml TESTS(e.g. 4,8) OUT.json [--save-ctx F] [--load-ctx F]"""
import inspect
import json
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/frozen")
from goaltests import (gt01_quality, gt02_consistency, gt03_costs, gt04_power, gt05_null_real,  # noqa: E402
                       gt06_goodhart, gt07_controls, gt08_outside)
from goaltests.spec import load  # noqa: E402

MODS = {1: gt01_quality, 2: gt02_consistency, 3: gt03_costs, 4: gt04_power, 5: gt05_null_real,
        6: gt06_goodhart, 7: gt07_controls, 8: gt08_outside}


def main() -> None:
    path, tests, out = sys.argv[1], [int(x) for x in sys.argv[2].split(",")], sys.argv[3]
    save = sys.argv[sys.argv.index("--save-ctx") + 1] if "--save-ctx" in sys.argv else None
    load_ctx = sys.argv[sys.argv.index("--load-ctx") + 1] if "--load-ctx" in sys.argv else None
    spec = load(path)
    ctx: dict = {}
    if load_ctx:
        g = json.load(open(load_ctx))
        g["curve"] = {float(k): v for k, v in g["curve"].items()}
        ctx["gt4"] = g
    results = []
    for i in tests:
        mod = MODS[i]
        kwargs = {"ctx": ctx} if "ctx" in inspect.signature(mod.run).parameters else {}
        for c in mod.run(spec, **kwargs):
            results.append({"test": c.test, "check": c.name, "passed": c.passed, "detail": c.detail})
    json.dump({"spec": path, "results": results}, open(out, "w"), indent=1)
    if save and "gt4" in ctx:
        g = dict(ctx["gt4"])
        g["curve"] = {str(k): v for k, v in g.get("curve", {}).items()}
        json.dump(g, open(save, "w"), indent=1)
    bad = [r for r in results if r["passed"] is False]
    print(f"{path}: {len(results)} checks, {len(bad)} failing")
    for r in bad:
        print("  FAIL", r["test"], r["check"], "|", r["detail"])


if __name__ == "__main__":
    main()

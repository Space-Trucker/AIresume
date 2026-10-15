"""Diff every mutant's results against the baseline's: which checks newly fail (caught), which
newly pass, and whether the only new failures are GOAL.md text-sync checks (a comparison of the goal
with itself, which a consistent edit of both files would not trip).

usage: compare.py RESULTFILE_NAME (fast.json, slow.json, gt8ctx.json ...) BASELINE_RESULTFILE"""
import json
import os
import sys

SCRATCH = "/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/mutations"
DOC_SYNC = ("GOAL.md names every key result", "GOAL.md shows every number goal.toml sets")


def key(r):
    return (r["test"], r["check"])


def load(path):
    return {key(r): r for r in json.load(open(path))["results"]}


def main():
    name, base_name = sys.argv[1], sys.argv[2]
    base = load(os.path.join(SCRATCH, "baseline", base_name))
    index = json.load(open(os.path.join(SCRATCH, "index.json")))
    only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
    for m in index:
        if only and m["id"] not in only:
            continue
        p = os.path.join(SCRATCH, m["id"], name)
        if not os.path.exists(p):
            continue
        res = load(p)
        new_fail, new_pass, gone = [], [], []
        for k, r in res.items():
            b = base.get(k)
            if r["passed"] is False and (b is None or b["passed"] is not False):
                new_fail.append(r)
            if r["passed"] is True and b is not None and b["passed"] is False:
                new_pass.append(r)
        for k, b in base.items():
            if k not in res and b["passed"] is not None:
                gone.append(b)
        substantive = [r for r in new_fail if not r["check"].startswith(DOC_SYNC)]
        sync = [r for r in new_fail if r["check"].startswith(DOC_SYNC)]
        verdict = "CAUGHT" if substantive else ("doc-sync only" if sync else "MISSED")
        print(f"{m['id']} [{verdict}] {m['desc']}  (expected: {m['expected']})")
        for r in substantive:
            print(f"    new fail {r['test']}: {r['check']} | {r['detail'][:200]}")
        for r in sync:
            print(f"    doc-sync {r['test']}: {r['check']} | {r['detail'][:200]}")
        for r in new_pass:
            print(f"    now passes {r['test']}: {r['check']} | {r['detail'][:160]}")
        if gone:
            print(f"    checks no longer run: {len(gone)} (" + "; ".join(f"{g['test']} {g['check'][:60]}" for g in gone[:6]) + ")")


if __name__ == "__main__":
    main()

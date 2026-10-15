"""One line per mutant, from the runs on the frozen (reviewed) code: substantive new failures in the
fast run (GT-1,2,3,6,7), in GT-8 scored on the baseline GT-4 context, in GT-4+GT-8 on the mutant's own
GT-4 context, and in GT-5, each against the matching baseline; GOAL.md-sync-only failures flagged."""
import json
import os

SCRATCH = "/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/mutations"
DOC_SYNC = ("GOAL.md names every key result", "GOAL.md shows every number goal.toml sets")


def load(path):
    return {(r["test"], r["check"]): r for r in json.load(open(path))["results"]} if os.path.exists(path) else None


def new_failures(res, base):
    if res is None:
        return None
    return [r for k, r in res.items() if r["passed"] is False and (base.get(k) is None or base[k]["passed"] is not False)]


B = lambda name: load(os.path.join(SCRATCH, "baseline", name))  # noqa: E731
base_fast, base_gt8, base_slow, base_gt5 = B("fast_f.json"), B("gt8ctx_f.json"), B("slowf.json"), B("gt5f.json")
rows = []
for m in json.load(open(os.path.join(SCRATCH, "index.json"))):
    d = os.path.join(SCRATCH, m["id"])
    fast = new_failures(load(os.path.join(d, "fast_f.json")), base_fast)
    subst = [r for r in fast if not r["check"].startswith(DOC_SYNC) and r["test"] != "GT-8"]
    sync = [r for r in fast if r["check"].startswith(DOC_SYNC)]
    gt8 = new_failures(load(os.path.join(d, "gt8ctx_f.json")), base_gt8) or []
    slow = new_failures(load(os.path.join(d, "slowf.json")), base_slow)
    gt5 = new_failures(load(os.path.join(d, "gt5f.json")), base_gt5)
    fmt = lambda rs: [f"{r['test']}: {r['check'][:80]} ({r['detail'][:70]})" for r in rs]  # noqa: E731
    rows.append({"id": m["id"], "desc": m["desc"], "expected": m["expected"], "fast": fmt(subst), "gt8": fmt(gt8),
                 "slow": None if slow is None else fmt(slow), "gt5": None if gt5 is None else fmt(gt5),
                 "sync": bool(sync)})
json.dump(rows, open(os.path.join(SCRATCH, "summary.json"), "w"), indent=1)
caught = [r for r in rows if r["fast"] or r["gt8"] or r["slow"] or r["gt5"]]
print(f"{len(rows)} mutants; caught {len(caught)}; missed {len(rows) - len(caught)} "
      f"(missed but tripping the GOAL.md text check: {sum(1 for r in rows if r not in caught and r['sync'])})")
for r in rows:
    tag = "CAUGHT" if r in caught else ("missed*" if r["sync"] else "missed")
    parts = [f"fast: {'; '.join(r['fast']) or '-'}", f"gt8(base ctx): {'; '.join(r['gt8']) or '-'}"]
    if r["slow"] is not None:
        parts.append(f"gt4+8: {'; '.join(r['slow']) or 'passes'}")
    if r["gt5"] is not None:
        parts.append(f"gt5: {'; '.join(r['gt5']) or 'passes'}")
    print(f"{r['id']} {tag:8s} | " + " | ".join(parts))

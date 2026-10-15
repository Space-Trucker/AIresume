"""GT-10: does the suite catch a broken goal? Oracle: deliberate defects. Each mutant changes one thing
in the goal under test, in memory, that a careful reviewer would call wrong, judged from outside the
goal: against the owner's own words, a rule or a broker limit, the price data, or the method. The fast
tests (GT-1, GT-2, GT-3, GT-6, GT-7, GT-8 and GT-4's input checks) run on each mutant; it is caught
when a check that passes on the unchanged goal fails on the mutant. GOAL.md is not changed with it, so
a check that compares GOAL.md with goal.toml (kind "hygiene") never counts as a catch: an author who
edited both consistently would pass it.

A test suite is only as good as the defects it catches. This test fails when any mutant passes
unnoticed, except the known gaps, which are listed with the reason no outside anchor exists for them.
Mutants that only the slow simulations can catch, GT-4 and GT-5, run with
``python3 -m goaltests.gt10_mutation --slow``; REPORT.md records their result.

The mutants started from the 56 the independent review of version 4 built (reviews/v4/tests-
circularity.md), adapted to version 5's settings, plus defects in what version 5 added."""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

from . import gt01_quality, gt02_consistency, gt03_costs, gt04_power, gt05_null_real, gt06_goodhart, gt07_controls, gt08_outside
from .spec import HERE, Check, load

TEST = "GT-10"
KIND = "external"
DELETE = "<delete>"          # a plain string, so it survives the trip to a worker process

# (id, the defect, what it changes, the new value). Targets: "section.key", "G1.key" for a gate rule,
# "KR3.1.field" for a key result, "C6.statement" for a control; DELETE removes the target
MUTANTS = [
    ("M01", "overnight stock cap 4% to 8%", "risk.max_position_overnight_pct", 8),
    ("M02", "the drawdown room margin deleted", "risk.drawdown_room_margin_pct", DELETE),
    ("M04", "G1 counts at least 5 variants, not 30", "G1.min_trials", 5),
    ("M05", "an event-prone jump of 30%, not a total loss", "risk.jump_overnight_event_prone_pct", 30),
    ("M06", "daily loss limit 2% to 4%", "risk.daily_loss_limit_pct", 4.0),
    ("M07", "open risk 2% to 5%", "risk.max_open_risk_pct", 5.0),
    ("M08", "a rotation need not clear its cost", "activity.rotation_margin_to_cost", 0),
    ("M09", "no cost stress (multiplier 1)", "costs.stress_cost_multiplier", 1.0),
    ("M10", "round trip 8 bps to 2", "costs.round_trip_cost_bps", 2),
    ("M11", "G2 runs 40 days, not 120", "G2.min_days", 40),
    ("M12", "the live test stops at -0.5, not -2.3", "live.test_stop_llr", -0.5),
    ("M13", "the key result for stops at the broker deleted", "KR2.5", DELETE),
    ("M14", "the control with the throttles (C13) deleted", "C13", DELETE),
    ("M15", "overnight jump 50% to 20%", "risk.jump_overnight_pct", 20),
    ("M16", "overnight net 15% to 60%", "risk.max_overnight_net_pct", 60),
    ("M17", "volatility budget 0.2% to 1% a day", "risk.vol_target_daily_pct", 1.0),
    ("M18", "gross exposure 100% to 300% (3 times leverage)", "risk.max_gross_exposure_pct", 300),
    ("M19", "KR3.1 allows 10 entries below twice their cost", "KR3.1.threshold", 10),
    ("M20", "G1 without the lag audit", "G1.require_lag_audit", False),
    ("M21", "G1 may pass 20% of no-edge strategies", "evaluation.max_false_pass_g1", 0.2),
    ("M22", "a prior of 50% that a candidate is real", "evaluation.prior_edge_probability", 0.5),
    ("M23", "the floor on a position's risk deleted", "risk.min_position_risk_pct", DELETE),
    ("M24", "100 rotations a day", "activity.max_rotations_per_day", 100),
    ("M25", "the halt at the 10% line itself", "risk.max_drawdown_halt_pct", 10.0),
    ("M26", "holds through earnings", "constraints.hold_through_earnings", True),
    ("M27", "holds 20 trading days", "constraints.max_holding_trading_days", 20),
    ("M28", "G1 judged on raw profit", "G1.metric", "net"),
    ("M29", "G2 judged on raw profit", "G2.metric", "net"),
    ("M30", "no stop required", "risk.stop_required", False),
    ("M31", "drawdown line 10% to 20%", "risk.max_drawdown_pct", 20.0),
    ("M32", "risk per position 0.5% to 2%", "risk.risk_per_position_pct", 2.0),
    ("M33", "entry at 1 times cost, not 2", "activity.entry_min_gain_to_cost", 1),
    ("M34", "spreads up to 50 bps", "constraints.universe_max_spread_bps", 50),
    ("M35", "$1M a day of volume, not $20M", "constraints.universe_min_dollar_volume_usd", 1_000_000),
    ("M36", "real money starts with all the capital", "G3.max_initial_capital_fraction", 1.0),
    ("M37", "the live test without its cap", "live.test_cap_llr", 1000.0),
    ("M38", "a cost drag of 0.001% a day, not the plan's", "evaluation.assumed_cost_drag_daily_pct", 0.001),
    ("M39", "5 simulated variants while the budget allows 30", "evaluation.assumed_trials", 5),
    ("M40", "a position may be 1% of a name's daily volume", "constraints.max_position_adv_pct", 1.0),
    ("M41", "published effects counted in full", "evaluation.published_edge_multiplier", 1.0),
    ("M42", "intraday jump 20% to 5%", "risk.jump_intraday_pct", 5),
    ("M43", "G2 no longer requires a profit", "G2.require_net_profit", False),
    ("M44", "an order may be 50% of the volume while it works", "order_limits.max_order_participation_pct", 50),
    ("M45", "G1's Deflated Sharpe threshold 0.95 to 0.5", "G1.dsr_min", 0.5),
    ("M46", "joint power 50% to 20%", "evaluation.min_joint_power", 0.2),
    ("M47", "the kill switch control reduced to a sentence", "C6.statement", "There is a kill switch."),
    ("M48", "a budget of 100 variants", "kill_criteria.max_variants", 100),
    ("M49", "G1 needs 4,000 days, more than the data holds", "G1.min_days", 4000),
    ("M50", "the clock control deleted", "C14", DELETE),
    ("M51", "a single jump may lose 10%", "risk.max_jump_loss_pct", 10),
    ("M52", "a passing strategy need be real only 30% of the time", "evaluation.min_posterior", 0.3),
    ("M53", "real edges up to Sharpe 4 in the prior", "evaluation.prior_edge_sr_max", 4.0),
    ("M54", "G2 needs 100 risk-bearing trades, not 300", "G2.min_risk_trades", 100),
    ("M55", "KR4.1 made vague", "KR4.1.statement", "The system is running about all day."),
    ("M56", "the marking rule made vague", "measurement.mark_text", "positions are marked at a realistic price"),
    # defects in what version 5 added
    ("M57", "the plan's positions risk 0.2% each", "risk.typical_position_risk_pct", 0.2),
    ("M58", "a worst-day bound of 2%, the daily limit itself", "risk.max_day_loss_pct", 2.0),
    ("M59", "orders outside the regular session", "constraints.order_session", "extended"),
    ("M60", "overnight dollar net 30% to 60%", "risk.max_overnight_dollar_net_pct", 60),
    ("M61", "paper may trail the rerun by 3 Sharpe", "G2.fidelity_noninferiority_sr", 3.0),
    ("M62", "80% of trades matched, not 98%", "G2.min_trade_match", 0.80),
    ("M63", "rotation shipped without its comparison", "G1.rotation_gain_confidence", DELETE),
    ("M64", "capital grows at even odds", "live.test_grow_llr", 0.0),
    ("M65", "a clock error of 500 ms", "order_limits.max_clock_error_ms", 500),
    ("M66", "250 requests a minute, more than the broker allows", "order_limits.max_requests_per_minute", 250),
    ("M67", "a 20% price collar", "order_limits.price_collar_pct", 20),
    ("M68", "shorts with $500 of equity", "constraints.min_equity_for_shorts_usd", 500),
    ("M69", "real money from $1,000", "G3.min_initial_capital_usd", 1000),
    ("M70", "the live test stops a real edge 12% of the time", "evaluation.max_false_stop_3y", 0.12),
    ("M71", "the overnight industry cap 8% to 20%", "risk.max_overnight_industry_pct", 20),
]
# defects no test can catch without a slow simulation: their settings are used only there, and the
# goal restates them nowhere else
SLOW = {"M37": "GT-4: the cap must make a decay show sooner than without it"}
# defects with no outside anchor yet: reported as missed, with the reason, and never counted as caught
KNOWN_GAPS = {"M44": "no published bound on an order's share of the volume while it works; the square-root law "
                     "prices the position's size against daily volume, which GT-3 checks"}

FAST = [gt01_quality, gt02_consistency, gt03_costs, gt06_goodhart, gt07_controls, gt08_outside]


def _apply(spec: dict, target: str, value) -> dict | None:
    """The mutated goal, or None when the goal has nothing at the target (the mutant doesn't apply)."""
    s = copy.deepcopy(spec)
    parts = target.split(".")
    if parts[0].startswith("KR"):
        kid, field = ".".join(parts[:2]), parts[2] if len(parts) > 2 else None
        krs = s.get("key_results", [])
        k = next((x for x in krs if x.get("id") == kid), None)
        if k is None or (field is not None and field not in k):
            return None
        if field is None:
            krs.remove(k)
        elif k[field] == value:
            return None
        else:
            k[field] = value
        return s
    if parts[0].startswith("C") and parts[0][1:].isdigit():
        controls = s.get("controls", [])
        c = next((x for x in controls if x.get("id") == parts[0]), None)
        if c is None:
            return None
        if len(parts) == 1:
            controls.remove(c)
        else:
            c[parts[1]] = value
        return s
    if parts[0].startswith("G") and parts[0][1:].isdigit():
        g = next((x for x in s.get("gates", []) if x.get("id") == parts[0]), None)
        values = g.get("rule") if g else None
    else:
        values = s.get(parts[0])
    if values is None or parts[1] not in values or values[parts[1]] == value:
        return None                       # nothing there, or already so: no defect to plant
    if value == DELETE:
        del values[parts[1]]
    else:
        values[parts[1]] = value
    return s


def _fast(spec: dict) -> dict:
    """(test, check) -> passed, over the fast tests; hygiene checks left out."""
    out = {}
    for mod in FAST:
        for c in mod.run(spec) + (gt04_power.input_checks(spec) if mod is gt08_outside else []):
            if (c.kind or getattr(mod, "KIND", "")) != "hygiene" and c.passed is not None:
                out[(c.test, c.name)] = c.passed
    return out


def _one(args: tuple) -> tuple[str, str, str, list[str]]:
    spec, base, (mid, what, target, value) = args
    m = _apply(spec, target, value)
    if m is None:
        return mid, what, "not applicable", []
    after = _fast(m)
    # a check that fails on the mutant and not on the goal; one that merely disappears with a deleted
    # setting is no catch: the suite must say no
    caught = [f"{t} {name}" for (t, name), ok in after.items() if ok is False and base.get((t, name)) is not False]
    if caught:
        return mid, what, "caught", caught
    if mid in KNOWN_GAPS:
        return mid, what, "gap", [KNOWN_GAPS[mid]]
    if mid in SLOW:
        return mid, what, "slow", [SLOW[mid]]
    return mid, what, "missed", []


def mutate(spec: dict) -> list[tuple[str, str, str, list[str]]]:
    """(id, defect, status, catching checks) per mutant: status "caught", "missed", "slow", "gap" or
    "not applicable"."""
    base = _fast(spec)
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        return list(pool.map(_one, [(spec, base, m) for m in MUTANTS]))


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    results = mutate(spec)
    applied = [r for r in results if r[2] != "not applicable"]
    for mid, what, status, why in results:
        if status == "not applicable":
            continue
        if status == "caught":
            first = why[0] if len(why) == 1 else f"{why[0]}; and {len(why) - 1} more"
            out.append(Check(TEST, f"catches {mid} ({what})", True, first))
        elif status == "missed":
            out.append(Check(TEST, f"catches {mid} ({what})", False, "no fast check fails"))
        else:
            out.append(Check(TEST, f"{mid} ({what})", None,
                             ("needs a slow simulation: " if status == "slow" else "known gap: ") + why[0]))
    counts = {k: sum(1 for r in applied if r[2] == k) for k in ("caught", "missed", "slow", "gap")}
    out.append(Check(TEST, "deliberate defects caught by the fast tests", None,
                     f"{counts['caught']} of {len(applied)} caught; {counts['missed']} missed; {counts['slow']} left to the "
                     f"slow simulations; {counts['gap']} known gaps; {len(results) - len(applied)} not applicable to this goal"))
    return out


def main(argv=None) -> int:
    """Run the slow mutants through GT-4, GT-5 and GT-8, as REPORT.md records them."""
    p = argparse.ArgumentParser(prog="python3 -m goaltests.gt10_mutation")
    p.add_argument("spec", nargs="?", default=os.path.join(HERE, "goal.toml"))
    p.add_argument("--slow", action="store_true", help="also run the slow mutants through GT-4 and GT-5")
    p.add_argument("--only", help="comma-separated mutant ids for --slow")
    p.add_argument("--json", help="write the slow results here")
    a = p.parse_args(argv)
    spec = load(a.spec)
    for mid, what, status, why in mutate(spec):
        print(f"{mid} {status:14} {what}: {'; '.join(why[:2])}")
    if not a.slow:
        return 0
    wanted = set(a.only.split(",")) if a.only else set(SLOW)
    base_ctx: dict = {}
    base = {(c.test, c.name): c.passed for c in gt04_power.run(spec, ctx=base_ctx) + gt05_null_real.run(spec)
            + gt08_outside.run(spec, ctx=base_ctx) if c.passed is not None}
    report = {}
    for mid, what, target, value in MUTANTS:
        if mid not in wanted:
            continue
        m = _apply(spec, target, value)
        if m is None:
            continue
        ctx: dict = {}
        after = {(c.test, c.name): c.passed for c in gt04_power.run(m, ctx=ctx) + gt05_null_real.run(m)
                 + gt08_outside.run(m, ctx=ctx) if c.passed is not None}
        caught = [f"{t} {n}" for (t, n), ok in after.items() if ok is False and base.get((t, n)) is True]
        report[mid] = {"defect": what, "caught": caught}
        print(f"{mid} slow: {'caught by ' + '; '.join(caught[:3]) if caught else 'MISSED'}", flush=True)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(report, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

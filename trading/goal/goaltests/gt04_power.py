"""GT-4: do the gates tell skill from luck? Oracle: simulated track records whose true edge we set.
A researcher tries the goal's budget of variants and takes the best out-of-sample one to the gates.
For each gate rule as the goal writes it:
* false pass: no variant has a net edge (each one's gross edge just pays its costs, the hardest case
  for a gate); how often does the best of them pass G1?
* program: how often does such a strategy then pass G2 too, and so reach real money?
* power: one variant has the edge the goal targets, the rest have none; how often does the real one
  pass G1, and then G2?
* the drawdown halt: how often it stops a strategy that really has the targeted edge, in a year.
Under four noise shapes: normal, fat tails, volatility clustering, autocorrelation. When the goal
measures its volatility budget over 5-day periods, positions are sized so 5-day volatility meets it."""
from __future__ import annotations

import math
import random
from concurrent.futures import ProcessPoolExecutor

from . import gates, sim, stats
from .spec import Check, rule

TEST = "GT-4"
# what version 1 leaves unsaid, assumed here so its rules can be run at all
V1_DEFAULTS = {"vol_daily": 0.010, "vol_days": 1, "drag_daily": 0.0007, "stress_mult": 2.0, "trials": 10,
               "oos_days": 252, "paper_days": 20, "paper_trades": 300, "target_sr": 2.0, "claimed_sr": 2.0}


def _setup(spec: dict) -> dict:
    ev, r, ret = spec.get("evaluation", {}), spec.get("risk", {}), spec.get("returns", {})
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    s = dict(V1_DEFAULTS)
    if "vol_target_daily_pct" in r:
        s["vol_daily"] = r["vol_target_daily_pct"] / 100
    s["vol_days"] = r.get("vol_measured_over_days", 1)
    if "assumed_cost_drag_daily_pct" in ev:
        s["drag_daily"] = ev["assumed_cost_drag_daily_pct"] / 100
    s["stress_mult"] = spec.get("costs", {}).get("stress_cost_multiplier", s["stress_mult"])
    s["trials"] = ev.get("assumed_trials", s["trials"])
    s["oos_days"] = g1.get("min_days", s["oos_days"])
    s["paper_days"] = g2.get("min_days", s["paper_days"])
    s["extend_days"] = g2.get("extend_days", 0)
    s["paper_trades"] = max(g2.get("min_trades", 0), g2.get("min_risk_trades", 0), s["paper_trades"])
    s["target_sr"] = ret.get("target_net_excess_sharpe", s["target_sr"])
    s["min_sr"] = ret.get("min_net_excess_sharpe", None)
    s["max_false_pass_g1"] = ev.get("max_false_pass_g1", 0.05)
    s["max_false_real_money"] = ev.get("max_false_real_money", 0.01)
    s["min_power"] = ev.get("min_power", 0.80)
    s["max_false_halt"] = ev.get("max_false_halt_per_year", 0.10)
    s["reps"] = ev.get("simulation_reps", 400)
    s["halt"] = r.get("max_drawdown_halt_pct", 10.0)
    s["daily_limit"] = r.get("daily_loss_limit_pct", None)
    return s


def _sigma(s: dict, model: str) -> float:
    """Daily volatility of the simulated P&L: the budget, or less when the budget is measured over 5
    days and the noise is autocorrelated (5-day volatility then grows faster than the square root)."""
    return s["vol_daily"] / math.sqrt(sim.five_day_factor(model)) if s["vol_days"] == 5 else s["vol_daily"]


def _g1_record(s: dict, mus: list[float], sigma: float, model: str,
               rng: random.Random) -> tuple[gates.Record, int]:
    best, srs, chosen = sim.best_of(mus, s["oos_days"], sigma, model, rng)
    extra = (s["stress_mult"] - 1) * s["drag_daily"]   # the stress raises every cost by this much a day
    rec = gates.Record(daily=best, excess=best, trades=10_000, n_trials=len(mus), trial_srs=srs,
                       stressed=[x - extra for x in best], conservative_fills=True)
    return rec, chosen


def _g2_record(s: dict, mu: float, sigma: float, model: str, rng: random.Random,
               oos: list[float]) -> gates.Record:
    r = sim.returns(s["paper_days"] + s["extend_days"], mu, sigma, model, rng)
    return gates.Record(daily=r, excess=r, trades=s["paper_trades"], risk_trades=s["paper_trades"], oos=oos,
                        claimed_sr=stats.sharpe(oos), conservative_fills=True)


def _one_model(args: tuple) -> dict:
    """Every rate for one noise model; runs in its own process."""
    s, g1, g2, model = args
    rng = random.Random(f"gt4-{model}")
    sigma = _sigma(s, model)
    mu1 = stats.daily_sr(s["target_sr"]) * sigma
    reps = s["reps"]
    null = [0.0] * s["trials"]
    # no variant has a net edge; the best goes to G1, and if it passes, on to paper trading (G2)
    passed, tries = [], 0
    while tries < reps or (len(passed) < 25 and tries < 10 * reps):
        tries += 1
        rec, _ = _g1_record(s, null, sigma, model, rng)
        if gates.evaluate(g1, rec)[0]:
            passed.append(rec.excess)
    reached = sum(1 for oos in passed if gates.evaluate(g2, _g2_record(s, 0.0, sigma, model, rng, oos))[0])
    # one variant has the targeted edge; power counts passes of that one
    real = [mu1] + [0.0] * (s["trials"] - 1)
    found, wrong = [], 0
    for _ in range(reps):
        rec, chosen = _g1_record(s, real, sigma, model, rng)
        if gates.evaluate(g1, rec)[0]:
            if chosen == 0:
                found.append(rec.excess)
            else:
                wrong += 1
    confirmed = sum(1 for oos in found if gates.evaluate(g2, _g2_record(s, mu1, sigma, model, rng, oos))[0])
    halts = sum(1 for _ in range(reps)
                if stats.max_drawdown(sim.returns(252, mu1, sigma, model, rng)) * 100 >= s["halt"])
    return {"model": model, "tries": tries, "fp1": len(passed) / tries, "passed": len(passed), "reached": reached,
            "reps": reps, "pw1": len(found) / reps, "wrong": wrong, "found": len(found), "confirmed": confirmed,
            "pw2": confirmed / len(found) if found else 0.0, "halt": halts / reps}


def run(spec: dict, ctx: dict | None = None) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    s = _setup(spec)
    summary = ctx.setdefault("gt4", {"program": 0.0, "power1": 1.0, "power2": 1.0}) if ctx is not None else {}
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    add("simulation setup", None,
        f"volatility {s['vol_daily']:.2%}/day (measured over {s['vol_days']} day{'s' if s['vol_days'] > 1 else ''}), "
        f"cost drag {s['drag_daily']:.3%}/day, stress x{s['stress_mult']:g}, {s['trials']} variants, "
        f"G1 {s['oos_days']} days, G2 {s['paper_days']}+{s['extend_days']} days, target Sharpe {s['target_sr']}")
    with ProcessPoolExecutor(max_workers=len(sim.NOISE_MODELS)) as pool:
        results = list(pool.map(_one_model, [(s, g1, g2, m) for m in sim.NOISE_MODELS]))
    for res in results:
        model = res["model"]
        program = res["fp1"] * (res["reached"] / res["passed"] if res["passed"] else 0.0)
        add(f"G1 lets the best of {s['trials']} no-edge variants through at most {s['max_false_pass_g1']:.0%} ({model})",
            res["fp1"] <= s["max_false_pass_g1"], f"{res['fp1']:.2%} of {res['tries']}")
        add(f"a no-edge strategy reaches real money at most {s['max_false_real_money']:.1%} of the time ({model})",
            program <= s["max_false_real_money"],
            f"G1 {res['fp1']:.2%} x G2 {res['reached']}/{res['passed']} = {program:.2%}")
        add(f"G1 passes the targeted edge at least {s['min_power']:.0%} of the time ({model})",
            res["pw1"] >= s["min_power"],
            f"{res['pw1']:.1%} of {res['reps']}" + (f"; a no-edge variant was chosen and passed {res['wrong']} times"
                                                    if res["wrong"] else ""))
        add(f"G2 passes the targeted edge at least {s['min_power']:.0%} of the time after G1 ({model})",
            res["pw2"] >= s["min_power"], f"{res['confirmed']}/{res['found']} = {res['pw2']:.1%}")
        add(f"the {s['halt']:g}% drawdown halt stops the targeted edge at most {s['max_false_halt']:.0%} of years ({model})",
            res["halt"] <= s["max_false_halt"], f"{res['halt']:.1%}")
        if summary:
            summary["program"] = max(summary["program"], program)
            summary["power1"] = min(summary["power1"], res["pw1"])
            summary["power2"] = min(summary["power2"], res["pw2"])
    if s["daily_limit"]:
        rng = random.Random("gt4-daily")
        days = sim.returns(252 * 40, stats.daily_sr(s["target_sr"]) * s["vol_daily"], s["vol_daily"], "garch", rng)
        hits = sum(1 for d in days if d * 100 <= -s["daily_limit"]) / 40
        add("daily loss limit hits per year at the volatility budget (clustered, fat-tailed)", None, f"{hits:.2f}")
    # what the statistics allow: track record needed at the targeted Sharpe
    for sr in sorted({s["target_sr"], s["min_sr"] or s["target_sr"]}):
        need = stats.min_track_record(stats.daily_sr(sr), 0.0, 0.99)
        add(f"days of track record to show a Sharpe {sr:g} at 99% confidence", None, f"{need:.0f} days")
    return out

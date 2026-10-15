"""GT-4: do the gates tell skill from luck? Oracle: simulated track records whose true edge we set.
For each gate rule as the goal writes it:
* false pass: how often a strategy with no edge (it loses its costs) passes;
* power: how often a strategy with the edge the goal targets passes;
* program: how often a no-edge strategy reaches real money (G1 then G2);
* the drawdown halt: how often it stops a strategy that really has the targeted edge.
Under four noise shapes (normal, fat tails, volatility clustering, autocorrelation)."""
from __future__ import annotations

import random

from . import gates, sim, stats
from .spec import Check, rule

TEST = "GT-4"
# what version 1 leaves unsaid, assumed here so its rules can be run at all
V1_DEFAULTS = {"vol_daily": 0.010, "drag_daily": 0.0007, "trials": 10, "oos_days": 252, "paper_days": 20,
               "paper_trades": 300, "target_sr": 2.0, "claimed_sr": 2.0}


def _setup(spec: dict) -> dict:
    ev, r, ret = spec.get("evaluation", {}), spec.get("risk", {}), spec.get("returns", {})
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    s = dict(V1_DEFAULTS)
    if "vol_target_daily_pct" in r:
        s["vol_daily"] = r["vol_target_daily_pct"] / 100
    if "assumed_cost_drag_daily_pct" in ev:
        s["drag_daily"] = ev["assumed_cost_drag_daily_pct"] / 100
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


def _g1_record(s: dict, mu: float, model: str, rng: random.Random) -> gates.Record:
    best, srs = sim.best_of(s["trials"], s["oos_days"], mu, s["vol_daily"], model, rng)
    stressed = [x - s["drag_daily"] for x in best]  # doubling costs subtracts the drag once more
    return gates.Record(daily=best, excess=best, trades=10_000, n_trials=s["trials"], trial_srs=srs,
                        stressed=stressed, conservative_fills=True)


def _g2_record(s: dict, mu: float, model: str, rng: random.Random, oos: list[float]) -> gates.Record:
    r = sim.returns(s["paper_days"] + s["extend_days"], mu, s["vol_daily"], model, rng)
    return gates.Record(daily=r, excess=r, trades=s["paper_trades"], risk_trades=s["paper_trades"], oos=oos,
                        claimed_sr=stats.sharpe(oos) if oos else stats.daily_sr(V1_DEFAULTS["claimed_sr"]),
                        conservative_fills=True)


def _rate(fn, reps: int) -> float:
    return sum(1 for _ in range(reps) if fn()) / reps


def run(spec: dict, ctx: dict | None = None) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    s = _setup(spec)
    summary = ctx.setdefault("gt4", {"program": 0.0, "power1": 1.0, "power2": 1.0}) if ctx is not None else {}
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    h0 = -s["drag_daily"]                       # no edge: pays its costs
    h1 = stats.daily_sr(s["target_sr"]) * s["vol_daily"]
    add("simulation setup", None,
        f"daily vol {s['vol_daily']:.2%}, cost drag {s['drag_daily']:.3%}/day, {s['trials']} variants tried, "
        f"G1 {s['oos_days']} days, G2 {s['paper_days']} days, target Sharpe {s['target_sr']}, {s['reps']} runs each")
    for model in sim.NOISE_MODELS:
        rng = random.Random(f"gt4-{model}")
        reps = s["reps"] if model in ("normal", "garch") else max(100, s["reps"] // 2)
        # no-edge strategies through G1; those that pass go on to paper trading (G2)
        passed_oos, tries = [], 0
        while tries < reps or (len(passed_oos) < 20 and tries < 6 * reps):
            tries += 1
            rec = _g1_record(s, h0, model, rng)
            if gates.evaluate(g1, rec)[0]:
                passed_oos.append(rec.excess)
        fp1 = len(passed_oos) / tries
        pw1 = _rate(lambda: gates.evaluate(g1, _g1_record(s, h1, model, rng))[0], reps)
        add(f"G1 lets a no-edge strategy through at most {s['max_false_pass_g1']:.0%} ({model})",
            fp1 <= s["max_false_pass_g1"], f"{fp1:.1%} of {tries}")
        add(f"G1 passes the targeted edge at least {s['min_power']:.0%} of the time ({model})",
            pw1 >= s["min_power"], f"{pw1:.1%}")
        reached = sum(1 for oos in passed_oos if gates.evaluate(g2, _g2_record(s, h0, model, rng, oos))[0])
        p_g2 = reached / len(passed_oos) if passed_oos else 0.0
        program = fp1 * p_g2
        if summary:
            summary["program"] = max(summary["program"], program)
            summary["power1"] = min(summary["power1"], pw1)
        add(f"a no-edge strategy reaches real money at most {s['max_false_real_money']:.1%} of the time ({model})",
            program <= s["max_false_real_money"],
            f"G1 {fp1:.1%} x G2 {reached}/{len(passed_oos)} of those = {program:.2%}")
        pw2 = _rate(lambda: gates.evaluate(g2, _g2_record(s, h1, model, rng,
                                                          sim.returns(s["oos_days"], h1, s["vol_daily"], model, rng)))[0], reps)
        add(f"G2 passes the targeted edge at least {s['min_power']:.0%} of the time ({model})",
            pw2 >= s["min_power"], f"{pw2:.1%}")
        if summary:
            summary["power2"] = min(summary["power2"], pw2)
        # the drawdown halt on a strategy that really has the targeted edge, over a year
        halt = _rate(lambda: stats.max_drawdown(sim.returns(252, h1, s["vol_daily"], model, rng)) * 100 >= s["halt"], reps)
        add(f"the {s['halt']:g}% drawdown halt stops the targeted edge at most {s['max_false_halt']:.0%} of years ({model})",
            halt <= s["max_false_halt"], f"{halt:.1%}")
    if s["daily_limit"]:
        rng = random.Random("gt4-daily")
        days = sim.returns(252 * 40, h1, s["vol_daily"], "garch", rng)
        hits = sum(1 for d in days if d * 100 <= -s["daily_limit"]) / 40
        add("daily loss limit hits per year at the volatility budget (clustered, fat-tailed)", None, f"{hits:.1f}")
    # what the statistics allow: track record needed at the targeted Sharpe
    for sr in sorted({s["target_sr"], s["min_sr"] or s["target_sr"]}):
        need = stats.min_track_record(stats.daily_sr(sr), 0.0, 0.99)
        add(f"days of track record to show a Sharpe {sr:g} at 99% confidence", None, f"{need:.0f} days")
    return out

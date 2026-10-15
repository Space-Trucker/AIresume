"""GT-4: do the gates tell skill from luck? Oracle: simulated track records whose true edge we set.
A researcher tries the goal's budget of variants and takes the best out-of-sample one to the gates.
For each gate rule as the goal writes it:
* false pass: no variant has a net edge (each one's gross edge just pays its costs, the hardest case
  for a gate); how often does the best of them pass G1?
* program: how often does such a strategy then pass G2 too, and so reach real money?
* power: one variant has the edge the goal targets, the rest have none; how often does the real one
  pass G1, and then G2?
* fidelity: does G2's comparison with a rerun of the frozen strategy pass an honest implementation,
  and catch one that loses a Sharpe unit to execution?
* the drawdown halt, and the live test: how often do they stop a strategy that really has the
  targeted edge, and how fast does the live test stop one whose edge is gone?
Under four noise shapes: normal, fat tails, volatility clustering, autocorrelation. When the goal
measures its volatility budget over 5-day periods, positions are sized so 5-day volatility meets it.
Under autocorrelated noise, the shape that binds, it also maps how often a strategy passes both
gates for a range of true edges, which GT-8 weighs by the goal's prior."""
from __future__ import annotations

import math
import random
from concurrent.futures import ProcessPoolExecutor

from . import gates, sim, stats
from .spec import Check, rule

TEST = "GT-4"
# what version 1 leaves unsaid, assumed here so its rules can be run at all
V1_DEFAULTS = {"vol_daily": 0.010, "vol_days": 1, "drag_daily": 0.0007, "stress_mult": 2.0, "trials": 10,
               "oos_days": 252, "paper_days": 20, "paper_trades": 300, "target_sr": 2.0}
CURVE_SRS = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)
CURVE_MODEL = "ar1"   # the curve GT-8 weighs uses the noise shape that binds (autocorrelated P&L)


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
    s["max_paper_days"] = max(g2.get("max_days", 0), s["paper_days"] + s["extend_days"])
    s["paper_trades"] = max(g2.get("min_trades", 0), g2.get("min_risk_trades", 0), s["paper_trades"])
    s["target_sr"] = ret.get("target_net_excess_sharpe", s["target_sr"])
    s["min_sr"] = ret.get("min_net_excess_sharpe", None)
    s["max_false_pass_g1"] = ev.get("max_false_pass_g1", 0.05)
    s["max_false_real_money"] = ev.get("max_false_real_money", 0.01)
    s["min_power"] = ev.get("min_power")
    s["min_joint_power"] = ev.get("min_joint_power")
    s["max_false_halt"] = ev.get("max_false_halt_per_year", 0.10)
    s["reps"] = ev.get("simulation_reps", 400)
    s["halt"] = r.get("max_drawdown_halt_pct", 10.0)
    s["daily_limit"] = r.get("daily_loss_limit_pct", None)
    s["impl_noise"] = ev.get("assumed_implementation_noise", 0.15)
    s["fidelity_detect_sr"] = ev.get("fidelity_detect_sr", 1.0)
    s["min_fidelity_power"] = ev.get("min_fidelity_power", s["min_power"])
    live = spec.get("live", {})
    s["live"] = ({"h1_sr": live["test_h1_sr"], "cap": live["test_cap_llr"], "stop_at": live["test_stop_llr"],
                  "halve_at": live["test_halve_llr"], "grow_at": live.get("test_grow_llr", 0.0),
                  "look_every_days": live.get("retire_check_every_trading_days", 21)}
                 if "test_h1_sr" in live else None)
    s["max_false_stop_3y"] = ev.get("max_false_stop_3y", 0.10)
    s["min_dead_halve_1y"] = ev.get("min_dead_halve_1y", 0.5)
    s["min_dead_stop_3y"] = ev.get("min_dead_stop_3y", 0.75)
    return s


def _sigma(s: dict, model: str) -> float:
    """Daily volatility of the simulated P&L: the budget, or less when the budget is measured over 5
    days and the noise is autocorrelated (5-day volatility then grows faster than the square root)."""
    return s["vol_daily"] / math.sqrt(sim.five_day_factor(model)) if s["vol_days"] == 5 else s["vol_daily"]


def _g1_record(s: dict, mus: list[float], sigma: float, model: str,
               rng: random.Random) -> tuple[gates.Record, int]:
    best, _, chosen = sim.best_of(mus, s["oos_days"], sigma, model, rng)
    # the stress raises every cost by this much a day; costs scale with position size, and positions
    # shrink when the volatility budget is measured over 5 days and the P&L is autocorrelated
    extra = (s["stress_mult"] - 1) * s["drag_daily"] * sigma / s["vol_daily"]
    rec = gates.Record(daily=best, excess=best, trades=10_000, n_trials=len(mus),
                       stressed=[x - extra for x in best], conservative_fills=True, lag_audit_ok=True)
    return rec, chosen


def _g2_record(s: dict, mu: float, sigma: float, model: str, rng: random.Random,
               shortfall_sr: float = 0.0) -> gates.Record:
    """Paper trading: the frozen strategy's returns on the paper days (what a rerun shows), plus
    implementation noise, minus any execution shortfall, in Sharpe units a year. Long enough for G2
    to run on to its longest; ``_g2`` judges it at the minimum first."""
    n = s["max_paper_days"]
    strategy = sim.returns(n, mu, sigma, model, rng)
    cut = shortfall_sr / math.sqrt(252) * sigma
    paper = [x + s["impl_noise"] * sigma * rng.gauss(0, 1) - cut for x in strategy]
    return gates.Record(daily=paper, excess=paper, trades=s["paper_trades"], risk_trades=s["paper_trades"],
                        days_to_min_trades=s["paper_days"], rerun=strategy, rerun_match=0.98,
                        conservative_fills=True)


def _g2(g2: dict, s: dict, rec: gates.Record) -> tuple[bool | None, str]:
    """G2 as the goal runs it: judged after its minimum days; when the rule says to continue (the
    fidelity test not yet decisive), judged again at its longest."""
    first = s["paper_days"] + s["extend_days"]
    cut = lambda k: gates.Record(**{**rec.__dict__, "daily": rec.daily[:k], "excess": rec.excess[:k],  # noqa: E731
                                    "rerun": rec.rerun[:k] if rec.rerun is not None else None})
    ok, why = gates.evaluate(g2, cut(first))
    if ok is None and len(rec.daily) > first:
        ok, why = gates.evaluate(g2, rec)
    return bool(ok), why


def _one_model(args: tuple) -> dict:
    """Every rate for one noise model; runs in its own process."""
    s, g1, g2, model = args
    rng = random.Random(f"gt4-{model}")
    sigma = _sigma(s, model)
    mu1 = stats.daily_sr(s["target_sr"]) * sigma
    reps = s["reps"]
    null = [0.0] * s["trials"]
    # no variant has a net edge; the best goes to G1, and if it passes, on to paper trading (G2)
    passed = tries = reached = 0
    while tries < reps or (passed < 25 and tries < 10 * reps):
        tries += 1
        rec, _ = _g1_record(s, null, sigma, model, rng)
        if gates.evaluate(g1, rec)[0]:
            passed += 1
            reached += _g2(g2, s, _g2_record(s, 0.0, sigma, model, rng))[0]
    # one variant has the targeted edge; power counts passes of that one
    real = [mu1] + [0.0] * (s["trials"] - 1)
    found = wrong = confirmed = 0
    for _ in range(reps):
        rec, chosen = _g1_record(s, real, sigma, model, rng)
        if gates.evaluate(g1, rec)[0]:
            if chosen == 0:
                found += 1
                confirmed += _g2(g2, s, _g2_record(s, mu1, sigma, model, rng))[0]
            else:
                wrong += 1
    out = {"model": model, "tries": tries, "fp1": passed / tries, "passed": passed, "reached": reached,
           "reps": reps, "pw1": found / reps, "wrong": wrong, "found": found, "confirmed": confirmed,
           "pw2": confirmed / found if found else 0.0}
    # G2's fidelity test: an honest implementation, and one that loses Sharpe units to execution
    if "fidelity_margin_sr" in g2 or "fidelity_noninferiority_sr" in g2:
        def fidelity_fails(cut: float) -> bool:
            ok, why = _g2(g2, s, _g2_record(s, mu1, sigma, model, rng, cut))
            return not ok and "rerun" in why
        out["fid_false"] = sum(fidelity_fails(0.0) for _ in range(reps)) / reps
        out["fid_power"] = sum(fidelity_fails(s["fidelity_detect_sr"]) for _ in range(reps)) / reps
    out["halt"] = sum(1 for _ in range(reps)
                      if stats.max_drawdown(sim.returns(252, mu1, sigma, model, rng)) * 100 >= s["halt"]) / reps
    if s["live"]:
        def live(sr: float, years: int) -> list[tuple[int, str]]:
            return gates.sequential(s["live"], sim.returns(252 * years, stats.daily_sr(sr) * sigma, sigma, model, rng))
        live_reps = 2 * reps      # cheap next to G1's simulations, and the rates sit near their bounds
        false_stop = sum(any(a == "stop" for _, a in live(s["target_sr"], 3)) for _ in range(live_reps))
        dead_stop = dead_halve = 0
        for _ in range(live_reps):
            acts = live(0.0, 3)
            dead_stop += any(a == "stop" for _, a in acts)
            dead_halve += any(a in ("halve", "stop") and d <= 252 for d, a in acts)
        out.update(live_false_stop=false_stop / live_reps, dead_stop3=dead_stop / live_reps,
                   dead_halve1=dead_halve / live_reps)
        # capital: 10% of the intended at first, doubling at most every 60 days while the latest look
        # allows growth, halving on a look at or below the halving line; how often does a dead strategy
        # reach full capital within 3 years, and how often is the targeted edge halved within a year?
        def capital(sr: float) -> tuple[bool, bool]:
            acts = live(sr, 3)
            cap, last, halved_1y, full = 0.1, "hold", False, False
            by_day = dict(acts)
            for day in range(1, 252 * 3 + 1):
                if day in by_day:
                    last = by_day[day]
                    if last == "stop":
                        return full, halved_1y
                    if last == "halve":
                        cap /= 2
                        halved_1y |= day <= 252
                if day % 60 == 0 and last == "grow":
                    cap = min(1.0, cap * 2)
                full |= cap >= 1.0
            return full, halved_1y
        dead_full = sum(capital(0.0)[0] for _ in range(live_reps)) / live_reps
        target_halved = sum(capital(s["target_sr"])[1] for _ in range(live_reps)) / live_reps
        out.update(dead_full3=dead_full, target_halved1=target_halved)
    return out


def _curve(args: tuple) -> dict:
    """How often a strategy passes both gates, by true edge (autocorrelated noise): one real variant among
    the budget, the best taken to G1, and if it passes, to G2."""
    s, g1, g2 = args
    rng = random.Random("gt4-curve")
    sigma = _sigma(s, CURVE_MODEL)
    reps = max(100, s["reps"] // 2)
    out = {}
    for sr in CURVE_SRS:
        mu = stats.daily_sr(sr) * sigma
        both = 0
        for _ in range(reps):
            rec, chosen = _g1_record(s, [mu] + [0.0] * (s["trials"] - 1), sigma, CURVE_MODEL, rng)
            if gates.evaluate(g1, rec)[0]:
                both += _g2(g2, s, _g2_record(s, mu if chosen == 0 else 0.0, sigma, CURVE_MODEL, rng))[0]
        out[sr] = both / reps
    return out


def run(spec: dict, ctx: dict | None = None) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    s = _setup(spec)
    summary = ctx.setdefault("gt4", {"program": 0.0, "power1": 1.0, "power2": 1.0}) if ctx is not None else {}
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    add("simulation setup", None,
        f"volatility {s['vol_daily']:.2%}/day (measured over {s['vol_days']} day{'s' if s['vol_days'] > 1 else ''}), "
        f"cost drag {s['drag_daily']:.3%}/day, stress x{s['stress_mult']:g}, {s['trials']} variants, "
        f"G1 {s['oos_days']} days, G2 {s['paper_days'] + s['extend_days']} days, target Sharpe {s['target_sr']}, "
        f"{s['reps']} runs each")
    with ProcessPoolExecutor(max_workers=len(sim.NOISE_MODELS) + 1) as pool:
        curve_job = pool.submit(_curve, (s, g1, g2))
        results = list(pool.map(_one_model, [(s, g1, g2, m) for m in sim.NOISE_MODELS]))
        curve = curve_job.result()
    for res in results:
        model = res["model"]
        p2 = res["reached"] / res["passed"] if res["passed"] else 0.0
        program = res["fp1"] * p2
        add(f"G1 lets the best of {s['trials']} no-edge variants through at most {s['max_false_pass_g1']:.0%} ({model})",
            res["fp1"] <= s["max_false_pass_g1"], f"{res['fp1']:.2%} of {res['tries']}")
        add(f"a no-edge strategy reaches real money at most {s['max_false_real_money']:.1%} of the time ({model})",
            program <= s["max_false_real_money"],
            f"G1 {res['fp1']:.2%} x G2 {res['reached']}/{res['passed']} = {program:.2%}")
        def interval(k: int, n: int) -> str:
            p = k / n if n else 0.0
            h = 1.96 * math.sqrt(p * (1 - p) / n) if n else 0.0
            return f"{p:.1%} (95% interval {max(0.0, p - h):.1%} to {min(1.0, p + h):.1%})"
        if s["min_power"] is not None:      # a goal that sets a floor for each gate
            add(f"G1 passes the targeted edge at least {s['min_power']:.0%} of the time ({model})",
                res["pw1"] >= s["min_power"],
                f"{res['pw1']:.1%} of {res['reps']}" + (f"; a no-edge variant was chosen and passed {res['wrong']} times"
                                                        if res["wrong"] else ""))
            add(f"G2 passes the targeted edge at least {s['min_power']:.0%} of the time after G1 ({model})",
                res["pw2"] >= s["min_power"], f"{res['confirmed']}/{res['found']} = {res['pw2']:.1%}")
        else:
            add(f"G1 and G2 power at the targeted edge, reported ({model})", None,
                f"G1 {interval(res['found'], res['reps'])}; G2 after G1 {interval(res['confirmed'], res['found'])}")
        if s["min_joint_power"] is not None:
            joint = res["confirmed"] / res["reps"]
            add(f"a real edge at the target passes both gates more often than not ({model})",
                joint > s["min_joint_power"], interval(res["confirmed"], res["reps"]))
        if "fid_false" in res:
            add(f"G2's fidelity test passes an honest implementation at least 95% of the time ({model})",
                res["fid_false"] <= 0.05, f"fails {res['fid_false']:.1%}")
            add(f"G2's fidelity test catches an execution shortfall of {s['fidelity_detect_sr']:g} Sharpe "
                f"at least {s['min_fidelity_power']:.0%} of the time ({model})",
                res["fid_power"] >= s["min_fidelity_power"], f"{res['fid_power']:.1%}")
        add(f"the {s['halt']:g}% drawdown halt stops the targeted edge at most {s['max_false_halt']:.0%} of years ({model})",
            res["halt"] <= s["max_false_halt"], f"{res['halt']:.1%}")
        if "live_false_stop" in res:
            add(f"the live test stops the targeted edge within 3 years at most {s['max_false_stop_3y']:.0%} of the time ({model})",
                res["live_false_stop"] <= s["max_false_stop_3y"], f"{res['live_false_stop']:.1%}")
            add(f"the live test halves a dead strategy within a year at least {s['min_dead_halve_1y']:.0%} of the time, "
                f"and stops it within 3 years at least {s['min_dead_stop_3y']:.0%} ({model})",
                res["dead_halve1"] >= s["min_dead_halve_1y"] and res["dead_stop3"] >= s["min_dead_stop_3y"],
                f"halved {res['dead_halve1']:.0%}, stopped {res['dead_stop3']:.0%}")
            if "dead_full3" in res:
                add(f"capital under the live test, reported ({model})", None,
                    f"a dead strategy reaches full capital within 3 years {res['dead_full3']:.0%} of the time; "
                    f"the targeted edge is halved within a year {res['target_halved1']:.0%} of the time")
        if summary:
            summary["program"] = max(summary["program"], program)
            summary["power1"] = min(summary["power1"], res["pw1"])
            summary["power2"] = min(summary["power2"], res["pw2"])
            summary["p2_null"] = max(summary.get("p2_null", 0.0), p2)
            summary["fp1"] = max(summary.get("fp1", 0.0), res["fp1"])
    if summary:
        summary["curve"] = curve
    add(f"share passing G1 and G2, by true Sharpe ({CURVE_MODEL} noise)", None,
        ", ".join(f"{k:g}: {v:.0%}" for k, v in curve.items()))
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

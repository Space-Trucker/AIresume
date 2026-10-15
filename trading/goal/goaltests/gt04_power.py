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

from . import anchors, gates, gt03_costs, sim, stats
from .spec import Check, rule

TEST = "GT-4"
KIND = "external"
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
    # the simulated search covers the whole variant budget, whichever of the two the goal states is larger
    s["trials"] = max(ev.get("assumed_trials", s["trials"]), spec.get("kill_criteria", {}).get("max_variants", 0))
    s["oos_days"] = g1.get("min_days", s["oos_days"])
    s["paper_days"] = g2.get("min_days", s["paper_days"])
    s["extend_days"] = g2.get("extend_days", 0)
    s["max_paper_days"] = max(g2.get("max_days", 0), s["paper_days"] + s["extend_days"])
    s["paper_trades"] = max(g2.get("min_trades", 0), g2.get("min_risk_trades", 0), s["paper_trades"])
    s["target_sr"] = ret.get("target_net_excess_sharpe", s["target_sr"])
    s["min_sr"] = ret.get("min_net_excess_sharpe", None)
    # every bar is the tests' own (anchors.py); a goal that claims a stricter one is held to its claim
    s["max_false_pass_g1"] = min(ev.get("max_false_pass_g1", 1.0), anchors.FALSE_PASS_G1)
    s["max_false_real_money"] = min(ev.get("max_false_real_money", 1.0), anchors.FALSE_REAL_MONEY)
    s["min_joint_power"] = max(ev.get("min_joint_power", ev.get("min_power", 0.0)), anchors.JOINT_POWER)
    s["max_false_halt"] = min(ev.get("max_false_halt_per_year", 1.0), anchors.FALSE_HALT_PER_YEAR)
    s["reps"] = ev.get("simulation_reps", 400)
    s["halt"] = r.get("max_drawdown_halt_pct", 10.0)
    s["daily_limit"] = r.get("daily_loss_limit_pct", None)
    s["impl_noise"] = ev.get("assumed_implementation_noise", 0.15)
    s["fidelity_detect_sr"] = ev.get("fidelity_detect_sr", 1.0)
    s["min_fidelity_power"] = max(ev.get("min_fidelity_power", 0.0), anchors.FIDELITY_POWER)
    live = spec.get("live", {})
    s["live"] = ({"h1_sr": live["test_h1_sr"], "cap": live["test_cap_llr"], "stop_at": live["test_stop_llr"],
                  "halve_at": live["test_halve_llr"], "grow_at": live.get("test_grow_llr", 0.0),
                  "look_every_days": live.get("retire_check_every_trading_days", 21)}
                 if "test_h1_sr" in live else None)
    s["max_false_stop_3y"] = min(ev.get("max_false_stop_3y", 1.0), anchors.LIVE_FALSE_STOP_3Y)
    s["min_dead_halve_1y"] = max(ev.get("min_dead_halve_1y", 0.0), anchors.LIVE_DEAD_HALVE_1Y)
    s["min_dead_stop_3y"] = max(ev.get("min_dead_stop_3y", 0.0), anchors.LIVE_DEAD_STOP_3Y)
    # a strategy whose gross edge goes keeps paying its costs: its net excess Sharpe becomes minus the
    # cost drag over the volatility budget
    s["decay_sr"] = -s["drag_daily"] / s["vol_daily"] * math.sqrt(252)
    return s


# the goal's stated tolerances, against the tests' bars: a tolerance looser than the bar is a claim the
# tests won't accept (version 4's tests read these as their bars, so loosening one passed)
TOLERANCES = [("max_false_pass_g1", "<=", anchors.FALSE_PASS_G1, "G1's false passes"),
              ("max_false_real_money", "<=", anchors.FALSE_REAL_MONEY, "a strategy with no edge reaching real money"),
              ("max_false_pass_g2", "<=", anchors.G2_CHANCE, "G2's passes of a strategy with no edge"),
              ("min_joint_power", ">=", anchors.JOINT_POWER, "a real edge at the target passing both gates"),
              ("min_power", ">=", anchors.JOINT_POWER, "a real edge at the target passing a gate"),
              ("min_fidelity_power", ">=", anchors.FIDELITY_POWER, "G2 catching an execution shortfall"),
              ("max_false_halt_per_year", "<=", anchors.FALSE_HALT_PER_YEAR, "the halt stopping a real edge"),
              ("max_false_stop_3y", "<=", anchors.LIVE_FALSE_STOP_3Y, "the live test stopping a real edge"),
              ("min_dead_halve_1y", ">=", anchors.LIVE_DEAD_HALVE_1Y, "the live test halving a dead strategy"),
              ("min_dead_stop_3y", ">=", anchors.LIVE_DEAD_STOP_3Y, "the live test stopping a dead strategy")]


def input_checks(spec: dict) -> list[Check]:
    """What GT-4 takes from the goal, checked before it simulates anything: the tolerances the goal
    states against the tests' bars, and the simulation's inputs against the rest of the goal and the
    data, so a goal can't pass by describing an easier search than it plans."""
    out: list[Check] = []
    add = lambda name, ok, detail="", kind="consistency": out.append(Check(TEST, name, ok, detail, kind))  # noqa: E731
    ev, kill, a = spec.get("evaluation", {}), spec.get("kill_criteria", {}), spec.get("activity", {})
    r, costs, g1 = spec.get("risk", {}), spec.get("costs", {}), rule(spec, "G1")
    for key, op, bar, what in TOLERANCES:
        if key in ev:
            ok = ev[key] <= bar if op == "<=" else ev[key] >= bar
            add(f"the goal's tolerance for {what} is no looser than the tests' bar", ok,
                f"{key} {ev[key]:g} vs {bar:g}", kind="external")
    if g1.get("kind") == "dsr":
        add("G1's Deflated Sharpe threshold is at least the 5% convention", g1.get("dsr_min", 0) >= anchors.DSR_MIN,
            f"{g1.get('dsr_min')} vs {anchors.DSR_MIN}", kind="external")
        days = g1.get("min_days", 0)
        add("G1's out-of-sample history fits the data the project can reach", days <= anchors.HISTORY_DAYS_AVAILABLE,
            f"{days} days vs about {anchors.HISTORY_DAYS_AVAILABLE} trading days of Alpaca history from 2016", kind="external")
    if "assumed_trials" in ev and "max_variants" in kill:
        add("the simulated search is at least the variant budget", ev["assumed_trials"] >= kill["max_variants"],
            f"{ev['assumed_trials']} simulated vs a budget of {kill['max_variants']}")
    plan = [a.get("planned_risk_trades_per_week"), r.get("typical_position_pct"), costs.get("round_trip_cost_bps")]
    if "assumed_cost_drag_daily_pct" in ev and None not in plan:
        drag = plan[0] * 52 * plan[1] / 100 * plan[2] / 1e4 / 252 * 100
        add("the simulated cost drag is the plan's", abs(ev["assumed_cost_drag_daily_pct"] - drag) <= 0.1 * drag,
            f"{ev['assumed_cost_drag_daily_pct']:g}% a day vs {plan[0]:g} trades a week x {plan[1]:g}% x {plan[2]:g} bps "
            f"= {drag:.4f}% a day")
    # the implementation noise KR1.6's tolerance allows: the unmatched share of the planned open positions,
    # each a typical position moving with a real stock's daily volatility, over the volatility budget
    match = rule(spec, "G2").get("min_trade_match")
    need = [match, a.get("planned_risk_trades_per_week"), a.get("typical_holding_minutes"), r.get("typical_position_pct"),
            r.get("vol_target_daily_pct")]
    if "assumed_implementation_noise" in ev and None not in need:
        try:
            vol = gt03_costs.daily_vol()
        except Exception as e:  # noqa: BLE001
            add("the simulated implementation noise is what KR1.6's tolerance allows", None, f"no data: {e}")
        else:
            stock = (vol["goog"] + vol["msft"]) / 2
            open_avg = need[1] / 5 * need[2] / 390
            implied = math.sqrt((1 - match) * open_avg) * need[3] / 100 * stock / (need[4] / 100)
            add("the simulated implementation noise is what KR1.6's tolerance allows",
                ev["assumed_implementation_noise"] >= 0.9 * implied,
                f"{ev['assumed_implementation_noise']:g} vs {implied:.3f}: {1 - match:.0%} of {open_avg:.0f} positions unmatched, "
                f"each {need[3]:g}% x {stock:.2%} a day, over a {need[4]:g}% budget", kind="external")
    return out


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
        out["fid_false_k"] = sum(fidelity_fails(0.0) for _ in range(reps))
        out["fid_power_k"] = sum(fidelity_fails(s["fidelity_detect_sr"]) for _ in range(reps))
        out["fid_false"], out["fid_power"] = out["fid_false_k"] / reps, out["fid_power_k"] / reps
    out["halt_k"] = sum(1 for _ in range(reps)
                        if stats.max_drawdown(sim.returns(252, mu1, sigma, model, rng)) * 100 >= s["halt"])
    out["halt"] = out["halt_k"] / reps
    if s["live"]:
        def live(sr: float, years: int) -> list[tuple[int, str]]:
            return gates.sequential(s["live"], sim.returns(252 * years, stats.daily_sr(sr) * sigma, sigma, model, rng))
        live_reps = 4 * reps      # cheap next to G1's simulations, and the rates sit near their bars
        out["live_reps"] = live_reps
        false_stop = sum(any(a == "stop" for _, a in live(s["target_sr"], 3)) for _ in range(live_reps))
        dead_stop = dead_halve = 0
        for _ in range(live_reps):
            acts = live(0.0, 3)
            dead_stop += any(a == "stop" for _, a in acts)
            dead_halve += any(a in ("halve", "stop") and d <= 252 for d, a in acts)
        out.update(live_false_stop=false_stop / live_reps, dead_stop3=dead_stop / live_reps,
                   dead_halve1=dead_halve / live_reps)
        # a decay: the targeted edge for some years, then gone, judged from the day it goes. "costs": the
        # gross edge gone, the costs remaining (what an edge that stops working leaves); "zero": exactly no
        # net edge, the hardest case to detect and one that loses nothing in expectation. Each run is
        # judged again without the cap, on the same returns, to test what the cap is for
        drng = random.Random(f"gt4-decay-{model}")
        good = 252 * anchors.DECAY_YEARS_GOOD
        no_cap = {**s["live"], "cap": math.inf}
        out["decay"] = {}
        for kind, sr_after in (("costs", s["decay_sr"]), ("zero", 0.0)):
            n = halve = stop = stop_no_cap = 0
            for _ in range(live_reps // 2):
                x = (sim.returns(good, mu1, sigma, model, drng)
                     + sim.returns(756, stats.daily_sr(sr_after) * sigma, sigma, model, drng))
                acts = gates.sequential(s["live"], x)
                if any(a == "stop" and d <= good for d, a in acts):
                    continue
                n += 1
                halve += any(a in ("halve", "stop") and good < d <= good + 252 for d, a in acts)
                stop += any(a == "stop" and good < d <= good + 756 for d, a in acts)
                stop_no_cap += any(a == "stop" and good < d <= good + 756 for d, a in gates.sequential(no_cap, x))
            out["decay"][kind] = (n, halve, stop, stop_no_cap)
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
    out: list[Check] = input_checks(spec)
    add = lambda name, ok, detail="", kind="": out.append(Check(TEST, name, ok, detail, kind))  # noqa: E731
    s = _setup(spec)
    summary = ctx.setdefault("gt4", {"program": 0.0, "program_upper": 0.0, "power1": 1.0, "power2": 1.0}) if ctx is not None else {}
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    add("simulation setup", None,
        f"volatility {s['vol_daily']:.2%}/day (measured over {s['vol_days']} day{'s' if s['vol_days'] > 1 else ''}), "
        f"cost drag {s['drag_daily']:.3%}/day, stress x{s['stress_mult']:g}, {s['trials']} variants, "
        f"G1 {s['oos_days']} days, G2 {s['paper_days'] + s['extend_days']} days, target Sharpe {s['target_sr']}, "
        f"{s['reps']} runs each. Bars from the tests (anchors.py), or the goal's claim where it is stricter")
    with ProcessPoolExecutor(max_workers=len(sim.NOISE_MODELS) + 1) as pool:
        curve_job = pool.submit(_curve, (s, g1, g2))
        results = list(pool.map(_one_model, [(s, g1, g2, m) for m in sim.NOISE_MODELS]))
        curve = curve_job.result()

    def interval(k: int, n: int, digits: int = 1) -> str:
        lo, hi = stats.wilson(k, n)
        return f"{k / n if n else 0.0:.{digits}%} (95% interval {lo:.{digits}%} to {hi:.{digits}%})"
    for res in results:
        model = res["model"]
        # safety bars, where a miss costs money: judged at the 95% upper bound of the rate
        hi = stats.wilson(res["passed"], res["tries"])[1]
        add(f"G1 lets the best of {s['trials']} no-edge variants through at most {s['max_false_pass_g1']:.0%} "
            f"({model}; judged at the upper bound)", hi <= s["max_false_pass_g1"],
            f"{interval(res['passed'], res['tries'], 2)} of {res['tries']}")
        program = res["reached"] / res["tries"]
        hi = stats.wilson(res["reached"], res["tries"])[1]
        add(f"a no-edge strategy reaches real money at most {s['max_false_real_money']:.1%} of the time "
            f"({model}; judged at the upper bound)", hi <= s["max_false_real_money"],
            f"G1 passed {res['passed']}, then G2 {res['reached']}: {interval(res['reached'], res['tries'], 2)}")
        # power, a trade-off against the false passes above: judged on the estimate, its interval shown
        pw1 = res["found"] / res["reps"]
        add(f"G1 and G2 power at the targeted edge, against the {anchors.COHEN_POWER:.0%} convention ({model})", None,
            f"G1 {interval(res['found'], res['reps'])}; G2 after G1 {interval(res['confirmed'], res['found'])}"
            + (f"; G1 is below the {anchors.COHEN_POWER:.0%} convention" if pw1 < anchors.COHEN_POWER else ""))
        joint = res["confirmed"] / res["reps"]
        add(f"a real edge at the target passes both gates more often than not ({model})",
            joint > s["min_joint_power"], interval(res["confirmed"], res["reps"]))
        if "fid_false" in res:
            add(f"G2's fidelity test passes an honest implementation at least {1 - anchors.FIDELITY_FALSE_FAIL:.0%} "
                f"of the time ({model})", res["fid_false"] <= anchors.FIDELITY_FALSE_FAIL,
                f"fails {interval(res['fid_false_k'], res['reps'])}")
            add(f"G2's fidelity test catches an execution shortfall of {s['fidelity_detect_sr']:g} Sharpe "
                f"at least {s['min_fidelity_power']:.0%} of the time ({model})",
                res["fid_power"] >= s["min_fidelity_power"], interval(res["fid_power_k"], res["reps"]))
        hi = stats.wilson(res["halt_k"], res["reps"])[1]
        add(f"the {s['halt']:g}% drawdown halt stops the targeted edge at most {s['max_false_halt']:.0%} of years "
            f"({model}; judged at the upper bound)", hi <= s["max_false_halt"], interval(res["halt_k"], res["reps"]))
        if "live_false_stop" in res:
            n = res["live_reps"]
            add(f"the live test stops the targeted edge within 3 years at most {s['max_false_stop_3y']:.0%} of the time ({model})",
                res["live_false_stop"] <= s["max_false_stop_3y"], interval(round(res["live_false_stop"] * n), n))
            add(f"the live test halves a dead strategy within a year at least {s['min_dead_halve_1y']:.0%} of the time, "
                f"and stops it within 3 years at least {s['min_dead_stop_3y']:.0%} ({model})",
                res["dead_halve1"] >= s["min_dead_halve_1y"] and res["dead_stop3"] >= s["min_dead_stop_3y"],
                f"halved {interval(round(res['dead_halve1'] * n), n)}; stopped {interval(round(res['dead_stop3'] * n), n)}")
            k, halve, stop, stop_no_cap = res["decay"]["costs"]
            add(f"after {anchors.DECAY_YEARS_GOOD} good years and a decay (the edge gone, the costs remaining), the live test "
                f"halves within a year at least {anchors.DECAY_HALVE_1Y:.0%} of the time and stops within 3 years at least "
                f"{anchors.DECAY_STOP_3Y:.0%} ({model})",
                halve / k >= anchors.DECAY_HALVE_1Y and stop / k >= anchors.DECAY_STOP_3Y,
                f"halved {interval(halve, k)}; stopped {interval(stop, k)}; of {k} runs not stopped while the edge was real")
            add(f"the cap on the evidence makes a decay show sooner, as the goal says it does ({model})",
                stop > stop_no_cap, f"stopped within 3 years of the decay {stop / k:.1%} with the cap, {stop_no_cap / k:.1%} without")
            k0, halve0, stop0, stop0_no_cap = res["decay"]["zero"]
            add(f"a decay to exactly no net edge, the hardest case, reported ({model})", None,
                f"halved within a year {halve0 / k0:.0%}, stopped within 3 years {stop0 / k0:.0%} "
                f"({stop0_no_cap / k0:.0%} without the cap)")
            if "dead_full3" in res:
                add(f"capital under the live test, reported ({model})", None,
                    f"a dead strategy reaches full capital within 3 years {res['dead_full3']:.0%} of the time; "
                    f"the targeted edge is halved within a year {res['target_halved1']:.0%} of the time")
        if summary:
            summary["program"] = max(summary["program"], program)
            summary["program_upper"] = max(summary["program_upper"], stats.wilson(res["reached"], res["tries"])[1])
            summary["power1"] = min(summary["power1"], res["pw1"])
            summary["power2"] = min(summary["power2"], res["pw2"])
            summary["p2_null"] = max(summary.get("p2_null", 0.0), res["reached"] / res["passed"] if res["passed"] else 0.0)
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

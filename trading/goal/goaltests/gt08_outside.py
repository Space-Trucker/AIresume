"""GT-8: the outside view. Oracle: published base rates for traders and strategies.

* Barber, Lee, Liu, Odean (2014): fewer than 1% of day traders earn predictable, reliable returns net
  of fees.
* Chague, De-Losso, Giovannetti (2019): 97% of those who day-traded more than 300 days lost money.
* McLean & Pontiff (2016): anomaly returns fall 26% out of sample and 58% after publication, so 42%
  of a published effect remains.
* Harvey, Liu & Zhu (2016): after a field's multiple testing, a new finding needs t > 3, not 2.

From these, a candidate strategy is unlikely to have a real edge before testing, and a real edge is
more likely small than large. The verdict uses the tests' own reference (anchors.py), not the goal's:
a 5% prior, real edges exponential with mean Sharpe 0.75, and the upper 95% bound of GT-4's rate of
no-edge strategies reaching real money. At that reference, is a strategy that passes both gates more
likely real than not, and more likely worth running than not? The goal's own prior must stay within
the base rates, and its own claims (a higher posterior, at its own prior) are checked as arithmetic.
It also reports how likely the program is to get there, and checks that the goal plans for nothing
passing."""
from __future__ import annotations

import math

from . import anchors
from .spec import Check, rule

TEST = "GT-8"
KIND = "external"
PRIORS = (0.02, 0.05, 0.10)   # chance a candidate strategy has a real net edge before testing


def posterior(prior: float, power: float, false_pass: float) -> float:
    return power * prior / (power * prior + false_pass * (1 - prior)) if prior > 0 else 0.0


def _average(curve: dict, lo: float, hi: float) -> float:
    """Average pass rate for true Sharpe ratios spread evenly over (lo, hi], from GT-4's curve
    (linear between its points, and zero pass rate at Sharpe 0)."""
    pts = sorted([(0.0, 0.0)] + list(curve.items()))

    def at(x: float) -> float:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return pts[-1][1]
    steps = 200
    return sum(at(lo + (hi - lo) * (i + 0.5) / steps) for i in range(steps)) / steps


def _point(curve: dict, x: float) -> float:
    """GT-4's pass rate at one true Sharpe ratio (linear between points; flat beyond the last)."""
    pts = sorted([(0.0, 0.0)] + list(curve.items()))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def _exponential(curve: dict, mean: float, worth: float) -> tuple[float, float]:
    """(pass rate of real edges, pass rate of real edges worth running, weighted by their share) for
    real edges exponential with the given mean Sharpe ratio."""
    pts = [(i + 0.5) * 0.01 for i in range(400)]
    weights = [math.exp(-x / mean) / mean for x in pts]
    norm = sum(weights)
    p_all = sum(w * _point(curve, x) for w, x in zip(weights, pts)) / norm
    p_worth = sum(w * _point(curve, x) for w, x in zip(weights, pts) if x >= worth) / norm
    return p_all, p_worth


def run(spec: dict, ctx: dict | None = None) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="", kind="": out.append(Check(TEST, name, ok, detail, kind))  # noqa: E731
    ev, ret, kill = spec.get("evaluation", {}), spec.get("returns", {}), spec.get("kill_criteria", {})
    prior = ev.get("prior_edge_probability")
    worth = ret.get("min_net_excess_sharpe", 1.0)

    # the goal's own assumptions, within the outside view
    add(f"the goal's prior is within the base rates (at most {anchors.PRIOR_CEILING:.0%}, ten times the share of "
        "reliably profitable day traders)", prior is not None and prior <= anchors.PRIOR_CEILING,
        f"{prior}" if prior is not None else "no prior is stated")
    for key in ("min_posterior", "min_posterior_worth_running"):
        if key in ev:
            add(f"the goal asks a passing strategy to be more likely real than not ({key})",
                ev[key] >= anchors.POSTERIOR_FLOOR, f"{ev[key]:g} vs {anchors.POSTERIOR_FLOOR:g}")
    smax, ceiling = ev.get("prior_edge_sr_max"), rule(spec, "G1").get("plausibility_sr_max")
    if smax is not None and ceiling is not None:
        add("the goal's prior puts no real edge where G1 suspects a leak", smax < ceiling,
            f"edges up to Sharpe {smax:g} vs a leak audit above {ceiling:g}", kind="consistency")

    gt4 = (ctx or {}).get("gt4")
    if gt4 and gt4.get("curve"):
        curve = gt4["curve"]
        false_pass, upper = max(gt4["program"], 1e-4), max(gt4.get("program_upper", gt4["program"]), 1e-4)
        # the verdict: the tests' reference, the false-pass rate at its upper bound
        p_all, p_worth = _exponential(curve, anchors.REF_EDGE_MEAN_SR, worth)
        real = posterior(anchors.REF_PRIOR, p_all, upper)
        good = anchors.REF_PRIOR * p_worth / (anchors.REF_PRIOR * p_all + (1 - anchors.REF_PRIOR) * upper)
        add(f"at the tests' reference, a strategy that passes G1 and G2 is more likely real than not, and more likely "
            f"worth running (Sharpe {worth:g} or more) than not", real > anchors.POSTERIOR_FLOOR and good > anchors.POSTERIOR_FLOOR,
            f"prior {anchors.REF_PRIOR:.0%}; real edges exponential, mean Sharpe {anchors.REF_EDGE_MEAN_SR:g}; GT-4 passes "
            f"{p_all:.0%} of them, and {upper:.2%} of no-edge strategies at the upper bound ({false_pass:.2%} measured): "
            f"real {real:.0%}, worth running {good:.0%}")
        # the goal's own claims, at its own prior: arithmetic on the goal's assumptions
        if prior is not None and smax:
            power_all = _average(curve, 0.0, smax)
            post = posterior(prior, power_all, false_pass)
            share_worth = max(smax - worth, 0) / smax
            post_worth = prior * share_worth * _average(curve, worth, smax) / (prior * power_all + (1 - prior) * false_pass)
            need, need_worth = ev.get("min_posterior", 0.80), ev.get("min_posterior_worth_running", ev.get("min_posterior", 0.80))
            add(f"the goal's claim: at its prior ({prior:.0%}, edges up to Sharpe {smax:g}), a passing strategy is real with "
                f"probability at least {need:.0%} and worth running at least {need_worth:.0%}",
                post >= need and post_worth >= need_worth,
                f"real {post:.0%}, worth running {post_worth:.0%}; " +
                ", ".join(f"prior {p:.0%}: {posterior(p, power_all, false_pass):.0%}" for p in PRIORS), kind="consistency")
            harsh = ev.get("prior_edge_sr_max_harsh")
            if harsh:
                ph = _average(curve, 0.0, harsh)
                hw = max(harsh - worth, 0) / harsh * _average(curve, worth, harsh) if harsh > worth else 0.0
                add(f"the same with edges no larger than Sharpe {harsh:g}", None,
                    f"real {posterior(prior, ph, false_pass):.0%}, worth running "
                    f"{prior * hw / (prior * ph + (1 - prior) * false_pass):.0%}")
            # the prior read two ways: per distinct idea, or per program (the base rates are per trader)
            trials = max(ev.get("assumed_trials", 10), kill.get("max_variants", 0))
            ideas = max(1, kill.get("max_variants", trials) // max(1, kill.get("max_variants_per_idea", 1)))
            add("chance the program reaches real money with a real edge, both readings of the prior", None,
                f"per idea, with at least {ideas} distinct ideas: about {1 - (1 - prior * power_all) ** ideas:.0%}; per "
                f"program, as the outside view's base rates are measured: about {prior * power_all:.1%}. With no real "
                f"edge, a false one reaches real money {false_pass:.2%} of the time. Most likely nothing passes and the "
                "kill criteria stop the program")
            # hindsight: the builder already knows the history, which can act like variants nobody counted
            per_variant = 1 - (1 - gt4.get("fp1", false_pass)) ** (1 / max(trials, 1))
            p2_null = gt4.get("p2_null", 0.5)
            rows = []
            for uncounted in (100, 1000):
                fp_m = (1 - (1 - per_variant) ** (trials + uncounted)) * p2_null
                rows.append(f"{uncounted} uncounted: a false edge reaches real money {fp_m:.1%}, "
                            f"a passing strategy is real {posterior(prior, power_all, max(fp_m, 1e-4)):.0%}")
            add("if hindsight acts like variants nobody counted (the figures above assume none)", None, "; ".join(rows))
        for mean in (0.75, 0.5):
            pa, pw = _exponential(curve, mean, worth)
            p = prior if prior is not None else anchors.REF_PRIOR
            add(f"with real edges exponential, mean Sharpe {mean:g}, at the measured rate and the goal's prior", None,
                f"a passing strategy is real {posterior(p, pa, false_pass):.0%}, worth running "
                f"{p * pw / (p * pa + (1 - p) * false_pass):.0%}")
    elif gt4:
        false_pass, power = max(gt4["program"], 1e-4), gt4["power1"] * gt4["power2"]
        p = prior if prior is not None else anchors.REF_PRIOR
        post = posterior(p, power, false_pass)
        add("a strategy that passes G1 and G2 is more likely real than not", post > anchors.POSTERIOR_FLOOR,
            f"prior {p:.0%}, power {power:.0%}, false pass {false_pass:.2%} (GT-4): {post:.0%}; the goal's prior says "
            "nothing about how large a real edge is")
    else:
        add("posterior that a passing strategy is real", None, "needs GT-4's rates: run GT-4 first")
    add("the goal says when to stop if nothing passes (research budget)", "max_research_cycles" in kill or "max_research_months" in kill,
        kind="presence")
    g3 = rule(spec, "G3")
    add("real money starts small and grows only with evidence", "max_initial_capital_fraction" in g3,
        "" if "max_initial_capital_fraction" in g3 else "'starting small' has no size or growth rule", kind="presence")
    if "max_initial_capital_fraction" in g3:
        add(f"the first real money is small: at most {anchors.OWNER_SMALL_START:.0%} of the intended capital (the owner's word)",
            g3["max_initial_capital_fraction"] <= anchors.OWNER_SMALL_START, f"{g3['max_initial_capital_fraction']:g}")
    shorts = spec.get("constraints", {}).get("min_equity_for_shorts_usd")
    if shorts is not None:
        add("the goal knows the broker's minimum equity for short sales ($2,000)", shorts >= anchors.BROKER_MIN_EQUITY_SHORTS,
            f"${shorts:,}")
    line = spec.get("risk", {}).get("max_drawdown_pct")
    if "min_initial_capital_usd" in g3 and line is not None:
        need = anchors.BROKER_MIN_EQUITY_SHORTS / (1 - line / 100)
        add("the first real money keeps the right to short through a full drawdown", g3["min_initial_capital_usd"] >= need,
            f"${g3['min_initial_capital_usd']:,} vs $2,000 / (1 - {line:g}%) = ${need:,.0f}")
    mult = ev.get("published_edge_multiplier")
    add(f"published edges count at most at what remains after publication (McLean-Pontiff: {anchors.PUBLISHED_EDGE_MULTIPLIER:.0%})",
        mult is not None and mult <= anchors.PUBLISHED_EDGE_MULTIPLIER, "not stated" if mult is None else f"{mult:g}")
    add("the evidence bar accounts for every variant tried (Harvey-Liu-Zhu, Bailey-López de Prado)",
        rule(spec, "G1").get("kind") == "dsr"
        and rule(spec, "G1").get("min_trials", 0) >= max(ev.get("assumed_trials", 1), kill.get("max_variants", 0)),
        f"G1 counts at least {rule(spec, 'G1').get('min_trials')} variants; the budget is {kill.get('max_variants')}",
        kind="consistency")
    return out

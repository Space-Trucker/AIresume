"""GT-8: the outside view. Oracle: published base rates for traders and strategies.

* Barber, Lee, Liu, Odean (2014): fewer than 1% of day traders earn predictable, reliable returns net
  of fees.
* Chague, De-Losso, Giovannetti (2019): 97% of those who day-traded more than 300 days lost money.
* McLean & Pontiff (2016): anomaly returns fall 26% out of sample and 58% after publication, so 42%
  of a published effect remains.
* Harvey, Liu & Zhu (2016): after a field's multiple testing, a new finding needs t > 3, not 2.

From these, a candidate strategy is unlikely to have a real edge before testing, and a real edge is
more likely small than large. The goal states its prior as a share of candidates with a real net
edge, and the size of such an edge as uniform up to a stated Sharpe. Weighing GT-4's pass rates by
that prior, the test asks: is a strategy that passes both gates probably real, and probably worth
running? It also reports how likely the program is to get there, and checks that the goal plans for
nothing passing."""
from __future__ import annotations

from .spec import Check, rule

TEST = "GT-8"
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


def run(spec: dict, ctx: dict | None = None) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    ev = spec.get("evaluation", {})
    ret = spec.get("returns", {})
    gt4 = (ctx or {}).get("gt4")
    prior = ev.get("prior_edge_probability", 0.05)
    need = ev.get("min_posterior", 0.80)
    smax = ev.get("prior_edge_sr_max")
    if gt4 and gt4.get("curve") and smax:
        curve, false_pass = gt4["curve"], max(gt4["program"], 1e-4)
        power_all = _average(curve, 0.0, smax)
        post = posterior(prior, power_all, false_pass)
        worth = ret.get("min_net_excess_sharpe", 1.0)
        share_worth = (smax - worth) / smax
        power_worth = _average(curve, worth, smax)
        post_worth = prior * share_worth * power_worth / (prior * power_all + (1 - prior) * false_pass)
        table = ", ".join(f"prior {p:.0%}: {posterior(p, power_all, false_pass):.0%}" for p in PRIORS)
        add(f"a strategy that passes G1 and G2 has a real edge with probability at least {need:.0%}", post >= need,
            f"prior {prior:.0%} with edges up to Sharpe {smax:g}; passes {power_all:.0%} of real edges and "
            f"{false_pass:.2%} of no-edge strategies (GT-4): {post:.0%}; {table}")
        need_worth = ev.get("min_posterior_worth_running", need)
        add(f"a strategy that passes G1 and G2 is worth running (Sharpe {worth:g} or more) with probability at least {need_worth:.0%}",
            post_worth >= need_worth, f"{post_worth:.0%}")
        harsh = ev.get("prior_edge_sr_max_harsh")
        if harsh:
            ph = _average(curve, 0.0, harsh)
            hw = max(harsh - worth, 0) / harsh * _average(curve, worth, harsh) if harsh > worth else 0.0
            add(f"the same with edges no larger than Sharpe {harsh:g}", None,
                f"real {posterior(prior, ph, false_pass):.0%}, worth running "
                f"{prior * hw / (prior * ph + (1 - prior) * false_pass):.0%}")
        trials = ev.get("assumed_trials", 10)
        any_real = 1 - (1 - prior) ** trials
        add("chance the program reaches real money with a real edge, on these assumptions", None,
            f"some variant of {trials} is real: at most {any_real:.0%}; it then passes both gates: {power_all:.0%}; "
            f"together at most {any_real * power_all:.0%}. With no real edge, a false one reaches real money "
            f"{false_pass:.2%} of the time. Most likely nothing passes and the kill criteria stop the program")
    else:
        if gt4:
            false_pass, power, source = max(gt4["program"], 1e-4), gt4["power1"] * gt4["power2"], "measured by GT-4"
        else:
            false_pass, power, source = 0.05, 0.8, "assumed"
        post = posterior(prior, power, false_pass)
        table = ", ".join(f"prior {p:.0%}: {posterior(p, power, false_pass):.0%}" for p in PRIORS)
        add(f"a strategy that passes G1 and G2 has a real edge with probability at least {need:.0%}", post >= need,
            f"prior {prior:.0%}, power {power:.0%}, false pass {false_pass:.2%} ({source}): {post:.0%}; {table}"
            + ("" if smax else "; the prior says nothing about how large a real edge is"))
    kill = spec.get("kill_criteria", {})
    add("the goal says when to stop if nothing passes (research budget)", "max_research_cycles" in kill or "max_research_months" in kill)
    g3 = rule(spec, "G3")
    add("real money starts small and grows only with evidence", "max_initial_capital_fraction" in g3,
        "" if "max_initial_capital_fraction" in g3 else "'starting small' has no size or growth rule")
    mult = ev.get("published_edge_multiplier")
    add("published edges count at most at what remains after publication (McLean-Pontiff: 42%)",
        mult is not None and mult <= 0.42, "not stated" if mult is None else f"{mult:g}")
    add("the evidence bar accounts for every variant tried (Harvey-Liu-Zhu, Bailey-López de Prado)",
        rule(spec, "G1").get("kind") == "dsr" and rule(spec, "G1").get("min_trials", 0) >= ev.get("assumed_trials", 1))
    return out

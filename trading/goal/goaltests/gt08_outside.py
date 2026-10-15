"""GT-8: the outside view. Oracle: published base rates for traders and strategies.

* Barber, Lee, Liu, Odean (2014): fewer than 1% of day traders earn predictable, reliable returns net
  of fees.
* Chague, De-Losso, Giovannetti (2019): 97% of those who day-traded more than 300 days lost money.
* McLean & Pontiff (2016): anomaly returns fall 26% out of sample and 58% after publication.
* Harvey, Liu & Zhu (2016): after a field's multiple testing, a new finding needs t > 3, not 2.

From these, a candidate short-horizon strategy is unlikely to have a real edge before testing. The
test asks whether a strategy that passes every gate is then probably real (posterior at least 80%),
and whether the goal plans for the common case: nothing passes."""
from __future__ import annotations

from .spec import Check, rule

TEST = "GT-8"
PRIORS = (0.02, 0.05, 0.10)   # chance a candidate strategy has a real net edge before testing


def posterior(prior: float, power: float, false_pass: float) -> float:
    return power * prior / (power * prior + false_pass * (1 - prior)) if prior > 0 else 0.0


def run(spec: dict, ctx: dict | None = None) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    ev = spec.get("evaluation", {})
    gt4 = (ctx or {}).get("gt4")
    if gt4:
        false_pass = max(gt4["program"], 1e-4)
        power = gt4["power1"] * gt4["power2"]
        source = "measured by GT-4"
    else:
        false_pass, power, source = 1 - rule(spec, "G2").get("combined_psr_min", 0.5), 0.8, "from the rules"
    prior = ev.get("prior_edge_probability", 0.05)
    need = ev.get("min_posterior", 0.80)
    post = posterior(prior, power, false_pass)
    table = ", ".join(f"prior {p:.0%}: {posterior(p, power, false_pass):.0%}" for p in PRIORS)
    add(f"a strategy that passes G1 and G2 is real with probability at least {need:.0%}", post >= need,
        f"prior {prior:.0%}, power {power:.0%}, false pass {false_pass:.2%} ({source}): {post:.0%}; {table}")
    # the chance the whole program ends at real money with a real edge, if each registered variant
    # independently has the prior chance of one (variants of one idea are less independent, so this
    # is an upper bound); GT-4's rates are already for the best of the whole variant budget
    trials = ev.get("assumed_trials", 10)
    any_real = 1 - (1 - prior) ** trials
    add("chance the program reaches real money with a real edge, on these assumptions", None,
        f"some variant of {trials} is real: at most {any_real:.0%}; it passes both gates: {power:.0%}; "
        f"together at most {any_real * power:.0%}. With no real edge, a false one reaches real money "
        f"{false_pass:.2%} of the time. Most likely nothing passes and the kill criteria stop the program")
    kill = spec.get("kill_criteria", {})
    add("the goal says when to stop if nothing passes (research budget)", "max_research_cycles" in kill or "max_research_months" in kill)
    g3 = rule(spec, "G3")
    add("real money starts small and grows only with evidence", "max_initial_capital_fraction" in g3,
        "" if "max_initial_capital_fraction" in g3 else "'starting small' has no size or growth rule")
    add("published edges are discounted for decay after publication (McLean-Pontiff: 58%)",
        ev.get("published_edge_haircut", 0) >= 0.5)
    add("the evidence bar accounts for every variant tried (Harvey-Liu-Zhu, Bailey-López de Prado)",
        rule(spec, "G1").get("kind") == "dsr")
    return out

"""GT-6: metric gaming (Goodhart's law: a measure that becomes a target stops measuring). Oracle:
strategies built to satisfy the goal's numbers while having no edge, or an edge only on paper, or
risk the numbers don't show. We know each should be rejected, because we built it that way. Each one
is shown at its best: a window in which its hidden flaw did not show.

A probe is caught if the goal's risk limits forbid what it does, or a gate rejects it. A probe that
is caught by neither means the goal can be met in letter and missed in intent."""
from __future__ import annotations

import random

from . import gates, sim, stats
from .spec import Check, constraints, risk, rule

TEST = "GT-6"


def _lucky(n: int, daily_sr_annual: float, vol: float, rng: random.Random) -> list[float]:
    """A track record that looks like a good strategy in this window: drawn until its own Sharpe is
    at least the one it is meant to show, so only the flaw can get it rejected, never chance."""
    for _ in range(1000):
        r = sim.returns(n, stats.daily_sr(daily_sr_annual) * vol, vol, "normal", rng)
        if stats.annualize_sr(stats.sharpe(r)) >= daily_sr_annual:
            return r
    raise RuntimeError("could not draw a lucky window")


def probes(spec: dict) -> list[tuple[str, str, str, gates.Record]]:
    """(name, flaw, gate, record)."""
    rng = random.Random("gt6")
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    d1, d2 = max(g1.get("min_days", 252), 252), max(g2.get("min_days", 20), 20)
    vol = spec.get("risk", {}).get("vol_target_daily_pct", 1.0) / 100
    trades = max(g2.get("min_trades", 0), g2.get("min_risk_trades", 0), 300)
    good = lambda n: _lucky(n, 3.0, vol, rng)  # noqa: E731
    # a paper record: what paper trading shows, with a rerun of the frozen strategy that matches it
    base = dict(trades=trades, risk_trades=trades, days_to_min_trades=d2, rerun_match=0.98, conservative_fills=True,
                max_risk_per_trade_pct=0.25, max_risk_per_position_pct=0.25, max_open_risk_pct=1.0, max_gross_pct=50,
                max_position_pct=10, max_holding_days=1)
    paper = lambda p, **kw: gates.Record(daily=p, excess=p, rerun=list(p), **{**base, **kw})  # noqa: E731
    out = []
    p = good(d2)
    out.append(("averaging down", "adds to losers in steps each inside the per-trade limit, so one position "
                "risks 4x that limit", "G2",
                paper(p, max_risk_per_trade_pct=0.5, max_risk_per_position_pct=2.0, max_position_pct=20)))
    p = good(d2)
    out.append(("selling tails without a stop", "many small wins, a rare crash not yet seen", "G2",
                paper(p, every_position_has_stop=False)))
    rng2 = random.Random("gt6-beta")
    mkt = _lucky(d2, 3.0, 0.01, rng2)                                       # a rising market
    noise = [0.002 * rng2.gauss(0, 1) for _ in mkt]
    beyond = [n - sum(noise) / len(noise) - 0.0002 for n in noise]         # nothing beyond the market but costs
    out.append(("riding the market", "fully long in a rising market: profit with no edge", "G2",
                gates.Record(daily=[m + b for m, b in zip(mkt, beyond)], excess=beyond, rerun=list(beyond),
                             **{**base, "max_gross_pct": 100, "max_position_pct": 10})))
    p = good(d2)
    out.append(("padding the trade count", "a few lucky trades plus hundreds of scratch trades", "G2",
                paper(p, risk_trades=20)))
    best, _, _ = sim.best_of([0.0] * 50, d1, vol, "normal", rng)
    out.append(("best of 50", "the luckiest of 50 strategies with no net edge", "G1",
                gates.Record(daily=best, excess=best, trades=5000, n_trials=50, lag_audit_ok=True,
                             stressed=[b - 0.0001 for b in best], conservative_fills=True)))
    p = good(d2)
    out.append(("paper's generous fills", "earns only because paper fills limit orders the moment price touches",
                "G2", paper(p, conservative_fills=False)))
    leak = _lucky(d1, 8.0, vol, rng)
    out.append(("look-ahead leak", "uses tomorrow's data today: a Sharpe of 8", "G1",
                gates.Record(daily=leak, excess=leak, trades=5000, n_trials=1, stressed=leak, conservative_fills=True,
                             lag_audit_ok=False)))
    p = good(d2)
    out.append(("big overnight positions", "holds full-size positions overnight, where a gap jumps past the stop",
                "G2", paper(p, max_overnight_long_pct=20, max_position_pct=20, max_overnight_gross_pct=60,
                            max_overnight_net_pct=20, max_holding_days=3)))
    churn = _lucky(d1, 3.0, vol, rng)
    rot = [0.0002 * rng.gauss(0, 1) for _ in range(400)]
    rot = [v - sum(rot) / len(rot) - 0.00002 for v in rot]                 # each switch loses 0.2 bp of equity
    out.append(("churning", "replaces held positions whenever a fresh forecast looks higher, on forecasts "
                "inflated by picking the highest of many: each switch pays two costs and loses on average", "G1",
                gates.Record(daily=churn, excess=churn, trades=5000, n_trials=1, lag_audit_ok=True, stressed=churn,
                             conservative_fills=True, rotations=len(rot), rotation_values=rot)))
    p = good(d2)
    out.append(("big overnight shorts", "holds 10% short positions overnight, where a takeover bid gaps one up "
                "50% (Yahoo, 1 February 2008)", "G2",
                paper(p, max_overnight_short_pct=10, max_overnight_gross_pct=20, max_overnight_net_pct=20,
                      max_holding_days=3)))
    return out


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    r, c = risk(spec), constraints(spec)
    for name, flaw, gate_id, rec in probes(spec):
        why = gates.risk_rule_violations(r, rec)
        if rec.max_holding_days > c.get("max_holding_trading_days", 1e9):
            why.append("held past the holding limit")
        if not why:
            ok, reason = gates.evaluate(rule(spec, gate_id), rec)
            if ok is False:
                why.append(f"{gate_id}: {reason}")
        out.append(Check(TEST, f"rejects '{name}' ({flaw})", bool(why), "; ".join(why) or "passes the goal"))
    return out

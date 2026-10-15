"""GT-6: metric gaming (Goodhart's law: a measure that becomes a target stops measuring). Oracle:
strategies built to satisfy the goal's numbers while having no edge, or an edge only on paper, or
risk the numbers don't show. We know each should be rejected, because we built it that way. Each one
is shown at its best: a window in which its hidden flaw did not show.

A probe is caught if the goal's risk limits forbid what it does, or a gate rejects it. A probe that
is caught by neither means the goal can be met in letter and missed in intent."""
from __future__ import annotations

import random

from . import anchors, gates, sim, stats
from .spec import Check, constraints, risk, rule

TEST = "GT-6"
KIND = "external"


def _lucky(n: int, daily_sr_annual: float, vol: float, rng: random.Random) -> list[float]:
    """A track record that looks like a good strategy in this window: drawn until its own Sharpe is
    at least the one it is meant to show, so only the flaw can get it rejected, never chance."""
    for _ in range(1000):
        r = sim.returns(n, stats.daily_sr(daily_sr_annual) * vol, vol, "normal", rng)
        if stats.annualize_sr(stats.sharpe(r)) >= daily_sr_annual:
            return r
    raise RuntimeError("could not draw a lucky window")


def _window(n: int, lo: float, hi: float, vol: float, rng: random.Random) -> list[float]:
    """A track record whose own Sharpe ratio lies in [lo, hi] and is positive in each half and in the
    calmer and the more turbulent days: one that clears every clause near the bar, so only the flaw a
    probe targets can stop it."""
    for _ in range(5000):
        r = sim.returns(n, stats.daily_sr((lo + hi) / 2) * vol, vol, "normal", rng)
        sr = stats.annualize_sr(stats.sharpe(r))
        halves = [stats.annualize_sr(stats.sharpe(p)) for p in (r[:n // 2], r[n // 2:])]
        regime = gates.regime_proxy(r)
        parts = [sum(x for x, g in zip(r, regime) if g == flag) for flag in (0, 1)]
        if lo <= sr <= hi and min(halves) >= 0.3 and min(parts) > 0:
            return r
    raise RuntimeError("could not draw a window")


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
                max_position_pct=4, max_holding_days=1)
    paper = lambda p, **kw: gates.Record(daily=p, excess=p, rerun=list(p), **{**base, **kw})  # noqa: E731
    out = []
    p = good(d2)
    out.append(("averaging down", "adds to losers in steps each inside the per-trade limit and every size limit, so "
                "one position risks twice the owner's 0.5%", "G2",
                paper(p, max_risk_per_trade_pct=0.5, max_risk_per_position_pct=1.0)))
    p = good(d2)
    out.append(("selling tails without a stop", "many small wins, a rare crash not yet seen", "G2",
                paper(p, every_position_has_stop=False)))
    rng2 = random.Random("gt6-beta")
    mkt = _lucky(d2, 3.0, 0.01, rng2)                                       # a rising market
    noise = [0.002 * rng2.gauss(0, 1) for _ in mkt]
    beyond = [n - sum(noise) / len(noise) - 0.0002 for n in noise]         # nothing beyond the market but costs
    out.append(("riding the market", "fully long in a rising market: profit with no edge", "G2",
                gates.Record(daily=[m + b for m, b in zip(mkt, beyond)], excess=beyond, rerun=list(beyond),
                             **{**base, "max_gross_pct": 100, "max_position_pct": 4})))
    p = good(d2)
    out.append(("padding the trade count", "lucky trades plus scratch trades: one risk-bearing round trip short of the "
                "owner's 300", "G2", paper(p, trades=5000, risk_trades=anchors.OWNER_MIN_PAPER_TRADES - 1)))
    # the luckiest of 50 no-edge strategies, shown at a Sharpe ratio that clears every other clause of G1:
    # only the correction for the variants tried can stop it, once with an honest count and once with a
    # count of one (the floor on the count must catch it)
    lucky = _window(d1, 1.05, 1.12, vol, rng)
    stressed = [x - 0.02 * vol for x in lucky]
    out.append(("best of 50", "the luckiest of 50 strategies with no net edge, its 50 variants reported", "G1",
                gates.Record(daily=lucky, excess=lucky, trades=5000, n_trials=50, lag_audit_ok=True,
                             stressed=stressed, conservative_fills=True)))
    out.append(("best of 50, reported as one", "the same record, with only the winning variant reported", "G1",
                gates.Record(daily=lucky, excess=lucky, trades=5000, n_trials=1, lag_audit_ok=True,
                             stressed=stressed, conservative_fills=True)))
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
    # churning, at realistic noise: about one rotation every two days, each a 4% position whose result
    # over the rest of its hold differs from the replaced one's by about 356 bps (168 bps a day over
    # 4.5 days), so the daily difference in returns has a standard deviation of about 10 bp of equity;
    # each rotation loses 2 bp of equity on average (two costs on inflated forecasts)
    churn = _lucky(d1, 3.0, vol, rng)
    gain = [(-0.0002 + 0.0014 * rng.gauss(0, 1)) if rng.random() < 0.5 else 0.0 for _ in churn]
    out.append(("churning", "replaces held positions whenever a fresh forecast looks higher, on forecasts "
                "inflated by picking the highest of many: each switch pays two costs and loses on average", "G1",
                gates.Record(daily=churn, excess=churn, trades=5000, n_trials=1, lag_audit_ok=True, stressed=churn,
                             conservative_fills=True, rotations=d1 // 2, rotation_gain=gain)))
    # a subtle leak: the signal sees part of the next bar's return, enough for a Sharpe of about 2.5,
    # below the ceiling that triggers an audit; the lag audit, run as the goal defines it, must catch it
    nxt = [rng.gauss(0, vol) for _ in range(d1 + 1)]
    signal_now = [nxt[t + 1] + 6 * vol * rng.gauss(0, 1) for t in range(d1)]
    leaky = [(1 if signal_now[t] > 0 else -1) * nxt[t + 1] for t in range(d1)]
    lagged = [(1 if signal_now[t - 1] > 0 else -1) * nxt[t + 1] if t else 0.0 for t in range(d1)]
    audit_ok, _ = gates.lag_audit(leaky, lagged)
    out.append(("a subtle look-ahead leak", f"sees part of tomorrow's return: a Sharpe of "
                f"{stats.annualize_sr(stats.sharpe(leaky)):.1f}, below the audit ceiling", "G1",
                gates.Record(daily=leaky, excess=leaky, trades=5000, n_trials=1, stressed=leaky,
                             conservative_fills=True, lag_audit_ok=audit_ok)))
    # riding the market in research: always long through a long rising market, so the raw Sharpe clears
    # G1 while nothing is earned beyond the market
    rng3 = random.Random("gt6-long-only")
    market = _window(d1, 1.55, 1.7, 0.01, rng3)
    noise = [0.0005 * rng3.gauss(0, 1) for _ in market]
    beyond = [x - sum(noise) / len(noise) - 0.00002 for x in noise]        # nothing beyond the market but costs
    raw = [m + b for m, b in zip(market, beyond)]
    out.append(("long through a bull market", "always long in a rising market: a raw Sharpe above the bar, no excess "
                "return", "G1", gates.Record(daily=raw, excess=beyond, trades=5000, n_trials=1, lag_audit_ok=True,
                                             stressed=[x - 0.00001 for x in raw], conservative_fills=True)))
    # an excess return, but a loss: 15% net long, the most the overnight limit allows, through a crash
    excess = good(d2)
    crash = [0.02 * rng3.gauss(0, 1) for _ in excess]
    shift = (-(sum(excess) + 0.01) / 0.15 - sum(crash)) / len(crash)     # the window ends 1% down
    crash = [m + shift for m in crash]
    out.append(("excess return but a loss", "beats the market while the account loses money in a crash", "G2",
                gates.Record(daily=[x + 0.15 * m for x, m in zip(excess, crash)], excess=excess, rerun=list(excess),
                             **{**base, "max_overnight_net_pct": 15, "max_overnight_dollar_net_pct": 15})))
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

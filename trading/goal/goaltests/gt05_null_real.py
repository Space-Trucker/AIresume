"""GT-5: random strategies on real price history. Oracle: a strategy that enters at random has no edge
by construction, whatever the data does. Run under the goal's own rules (holding limit, stop, size by
risk, costs) on real prices, it shows how often each gate would pass a strategy with no edge when
returns have real fat tails, volatility clustering and drift.

Two random strategies:
* balanced: long or short at random, so the market's drift cancels;
* long-only: always long, so it earns the market's drift. A gate that judges raw profit passes it
  in rising markets; a gate that judges excess return should not.
Daily data: S&P 500, Alphabet and Microsoft, 1999-2018. Entries at a day's close; a stop at 2 x the
14-day average true range fills at the stop, or at the open after a gap through it."""
from __future__ import annotations

import math
import random

from . import data, gates, stats
from .spec import Check, constraints, risk, rule

TEST = "GT-5"


def _atr(b: list[dict], i: int, n: int = 14) -> float:
    trs = [max(b[j]["high"] - b[j]["low"], abs(b[j]["high"] - b[j - 1]["close"]), abs(b[j]["low"] - b[j - 1]["close"]))
           / b[j - 1]["close"] for j in range(max(1, i - n + 1), i + 1)]
    return sum(trs) / len(trs)


def random_strategy(series: dict, market: dict, start: int, days: int, long_only: bool, spec: dict,
                    rng: random.Random) -> tuple[list[float], list[float], int, list[float]]:
    """Daily net returns, daily excess returns (market exposure removed), trades and the costs paid
    each day, over ``days`` trading days from ``start`` (indices into the aligned bars)."""
    r, c = risk(spec), constraints(spec)
    per = r.get("risk_per_position_pct", r.get("risk_per_trade_pct", 0.5)) / 100
    cap = r.get("max_position_pct", 20) / 100
    max_hold = int(c.get("max_holding_trading_days", 5))
    cost = spec.get("costs", {}).get("round_trip_cost_bps", 7.0) / 1e4
    open_pos: dict[str, dict] = {}
    daily, paid, trades = [], [], 0
    for t in range(start, start + days):
        pnl = fee = 0.0
        for name, b in series.items():
            pos = open_pos.get(name)
            if pos is not None:
                prev, bar = b[t - 1]["close"], b[t]
                if pos["dir"] > 0 and bar["low"] <= pos["stop"]:
                    exit_px = min(bar["open"], pos["stop"])
                elif pos["dir"] < 0 and bar["high"] >= pos["stop"]:
                    exit_px = max(bar["open"], pos["stop"])
                elif t - pos["entry_t"] >= pos["hold"]:
                    exit_px = bar["close"]
                else:
                    exit_px = None
                px = exit_px if exit_px is not None else bar["close"]
                pnl += pos["size"] * pos["dir"] * (px / prev - 1)
                if exit_px is not None:
                    pnl -= pos["size"] * cost
                    fee += pos["size"] * cost
                    trades += 1
                    del open_pos[name]
            if name not in open_pos and len(open_pos) < r.get("max_positions", 5) and rng.random() < 0.2:
                stop_dist = 2 * _atr(b, t)
                direction = 1 if long_only else rng.choice((1, -1))
                close = b[t]["close"]
                open_pos[name] = {"dir": direction, "size": min(per / stop_dist, cap), "entry_t": t,
                                  "hold": rng.randint(1, max_hold),
                                  "stop": close * (1 - direction * stop_dist)}
        daily.append(pnl)
        paid.append(fee)
    mkt = [market[t]["close"] / market[t - 1]["close"] - 1 for t in range(start, start + days)]
    _, _, excess = stats.ols_alpha_beta(daily, mkt)
    return daily, excess, trades, paid


def _aligned() -> tuple[dict, list[dict]]:
    names = ("sp500", "goog", "msft")
    raw = {n: {r["date"]: r for r in data.bars(n)} for n in names}
    dates = sorted(set.intersection(*(set(v) for v in raw.values())))
    return {n: [raw[n][d] for d in dates] for n in names}, [raw["sp500"][d] for d in dates]


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    try:
        series, market = _aligned()
    except Exception as e:  # noqa: BLE001
        add("real data", None, f"no data: {e}")
        return out
    ev = spec.get("evaluation", {})
    limit = ev.get("max_false_pass_g1", 0.05)
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    n = len(market)
    add("real data", None, f"{n} aligned days, {market[0]['date']:%Y-%m-%d} to {market[-1]['date']:%Y-%m-%d}")
    g1_days = max(g1.get("min_days", 252), 252)
    trials = ev.get("assumed_trials", 10)
    for long_only in (False, True):
        label = "long-only random" if long_only else "balanced random"
        rng = random.Random(f"gt5-{label}")
        passes = tries = 0
        for start in range(15, n - g1_days, 63):           # windows a quarter apart
            best, best_sr, srs = None, -math.inf, []
            for _ in range(trials):
                d, x, k, paid = random_strategy(series, market, start, g1_days, long_only, spec, rng)
                s = stats.sharpe(x if g1.get("metric") == "excess" else d)
                srs.append(s)
                if s > best_sr:
                    best_sr, best = s, (d, x, k, paid)
            d, x, k, paid = best
            rec = gates.Record(daily=d, excess=x, trades=k, n_trials=trials, trial_srs=srs,
                               stressed=[v - f for v, f in zip(x, paid)], conservative_fills=True)
            ok, _ = gates.evaluate(g1, rec)
            passes += bool(ok)
            tries += 1
        rate = passes / tries if tries else 0.0
        add(f"G1 passes the best of {trials} {label} strategies at most {limit:.0%} of the time (real data)",
            rate <= limit, f"{passes}/{tries} windows of {g1_days} days = {rate:.0%}")
        # paper-length windows, judged by G2 as written; trade-count clauses are left out because three
        # instruments on daily bars can't make hundreds of trades, which would fail every window
        rng = random.Random(f"gt5-paper-{label}")
        g2_days = max(g2.get("min_days", 20), 20)
        rule2 = {k: v for k, v in g2.items() if k not in ("min_trades", "min_risk_trades")}
        passes = tries = 0
        for start in range(15 + g1_days, n - g2_days, 21):
            d, x, k, _ = random_strategy(series, market, start, g2_days, long_only, spec, rng)
            _, oos_x, _, _ = random_strategy(series, market, start - g1_days, g1_days, long_only, spec, rng)
            rec = gates.Record(daily=d, excess=x, trades=k, risk_trades=k, oos=oos_x,
                               claimed_sr=stats.sharpe(oos_x), conservative_fills=True)
            ok, _ = gates.evaluate(rule2, rec)
            passes += bool(ok)
            tries += 1
        rate = passes / tries if tries else 0.0
        cap2 = ev.get("max_false_pass_g2", 0.20)
        add(f"G2 passes a {label} strategy at most {cap2:.0%} of the time (real data)", rate <= cap2,
            f"{passes}/{tries} windows of {g2_days} days = {rate:.0%}")
    return out

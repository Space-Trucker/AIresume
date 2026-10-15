"""GT-5: random strategies on real price history. Oracle: a strategy that enters at random has no edge
by construction, whatever the data does. Run under the goal's own rules (holding limit, stop, size by
risk, costs) on real prices, it shows how often each gate would pass a strategy with no edge when
returns have real fat tails, volatility clustering and drift.

Two random strategies:
* balanced: long or short at random, so the market's drift cancels;
* long-only: always long, so it earns the market's drift. A gate that judges raw profit passes it
  in rising markets; a gate that judges excess return should not.
Daily data, 1999-2014: the S&P 500 (traded as an index fund would be) and four large stocks,
Microsoft, Oracle, NVIDIA and Yahoo. Entries at a day's close; a stop at 2 x the 14-day average true
range fills at the stop, or at the open after a gap through it. Positions are sized by risk and held
overnight, so they also respect the goal's overnight limits for their direction.

Excess return follows the goal's own definition: each position's return less its weight times its
stock's 252-day beta to the market, as of the previous close, times the market's return (daily bars
can't split overnight from intraday). A definition that let the market's drift through would show here
as long-only random strategies passing more often than balanced ones.

What it can and can't show: G1's windows overlap almost entirely (about 1.6 independent ones), so no
rate near 1% can be measured here; GT-4 measures it. Here any pass at all is the alarm. G2's windows
are short, so G2 is also judged on synthetic histories made of real days: blocks of 20 consecutive
real days drawn at random, the same days for every instrument (a block bootstrap), enough of them to
judge the bar at its upper bound."""
from __future__ import annotations

import math
import random
from concurrent.futures import ProcessPoolExecutor

from . import anchors, data, gates, stats
from .spec import Check, constraints, risk, rule

TEST = "GT-5"
KIND = "external"
BETA_DAYS = 252
BLOCK_DAYS = 20
BOOTSTRAP_WINDOWS = 1000


def _atr(b: list[dict], i: int, n: int = 14) -> float:
    trs = [max(b[j]["high"] - b[j]["low"], abs(b[j]["high"] - b[j - 1]["close"]), abs(b[j]["low"] - b[j - 1]["close"]))
           / b[j - 1]["close"] for j in range(max(1, i - n + 1), i + 1)]
    return sum(trs) / len(trs)


def betas(series: dict, market: list[dict]) -> dict:
    """Each instrument's 252-day beta to the market as of the previous close, by day index."""
    m = [0.0] + [market[t]["close"] / market[t - 1]["close"] - 1 for t in range(1, len(market))]
    out = {}
    for name, b in series.items():
        y = [0.0] + [b[t]["close"] / b[t - 1]["close"] - 1 for t in range(1, len(b))]
        out[name] = stats.rolling_beta(y, m, BETA_DAYS)
    return out


def random_strategy(series: dict, market: list[dict], start: int, days: int, long_only: bool, spec: dict,
                    rng: random.Random, beta: dict) -> tuple[list[float], list[float], int, list[float]]:
    """Daily net returns, daily excess returns (each position's market exposure removed with its
    stock's beta as of the previous close, the goal's definition), trades and the costs paid each day,
    over ``days`` trading days from ``start`` (indices into the aligned bars, at least 252 in)."""
    r, c = risk(spec), constraints(spec)
    per = r.get("risk_per_position_pct", r.get("risk_per_trade_pct", 0.5)) / 100
    either = r.get("max_position_overnight_pct", r.get("max_position_pct", 20))
    caps = {1: r.get("max_overnight_long_pct", either) / 100, -1: r.get("max_overnight_short_pct", either) / 100}
    max_hold = int(c.get("max_holding_trading_days", 5))
    slots = r.get("max_positions") or len(series)   # at most one position per instrument
    cost = spec.get("costs", {}).get("round_trip_cost_bps", 7.0) / 1e4
    open_pos: dict[str, dict] = {}
    daily, excess, paid, trades = [], [], [], 0
    for t in range(start, start + days):
        pnl = fee = hedge = 0.0
        mkt = market[t]["close"] / market[t - 1]["close"] - 1
        for name, b in series.items():
            pos = open_pos.get(name)
            if pos is not None:
                hedge += pos["size"] * pos["dir"] * (beta[name][t] if beta[name][t] is not None else 1.0) * mkt
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
            if name not in open_pos and len(open_pos) < slots and rng.random() < 0.2:
                stop_dist = 2 * _atr(b, t)
                direction = 1 if long_only else rng.choice((1, -1))
                close = b[t]["close"]
                open_pos[name] = {"dir": direction, "size": min(per / stop_dist, caps[direction]), "entry_t": t,
                                  "hold": rng.randint(1, max_hold),
                                  "stop": close * (1 - direction * stop_dist)}
        daily.append(pnl)
        excess.append(pnl - hedge)
        paid.append(fee)
    return daily, excess, trades, paid


NAMES = ("sp500", "msft", "orcl", "nvda", "yhoo")


def _aligned() -> tuple[dict, list[dict]]:
    raw = {n: {r["date"]: r for r in data.bars(n)} for n in NAMES}
    dates = sorted(set.intersection(*(set(v) for v in raw.values())))
    return {n: [raw[n][d] for d in dates] for n in NAMES}, [raw["sp500"][d] for d in dates]


def _bootstrap(series: dict, n_days: int, rng: random.Random) -> tuple[dict, list[dict]]:
    """A synthetic history of real days: blocks of BLOCK_DAYS consecutive days drawn at random, the same
    days for every instrument, each day keeping its real open, high, low and close relative to the
    previous close."""
    total = len(series["sp500"])
    picks: list[int] = []
    while len(picks) < n_days:
        start = rng.randrange(1, total - BLOCK_DAYS)
        picks.extend(range(start, start + BLOCK_DAYS))
    picks = picks[:n_days]
    out = {}
    for name, b in series.items():
        close, bars = 100.0, [{"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0}]
        for i in picks[1:]:
            prev = b[i - 1]["close"]
            bars.append({k: close * b[i][k] / prev for k in ("open", "high", "low", "close")})
            close = bars[-1]["close"]
        out[name] = bars
    return out, out["sp500"]


def _one_kind(args: tuple) -> dict:
    """G1 and G2 pass counts for one kind of random strategy; runs in its own process."""
    spec, long_only = args
    series, market = _aligned()
    beta = betas(series, market)
    ev = spec.get("evaluation", {})
    g1, g2 = rule(spec, "G1"), rule(spec, "G2")
    n = len(market)
    label = "long-only random" if long_only else "balanced random"
    g1_days = max(g1.get("min_days", 252), 252)
    trials = ev.get("assumed_trials", 10)
    extra = spec.get("costs", {}).get("stress_cost_multiplier", 2.0) - 1
    rng = random.Random(f"gt5-{label}")
    passes = tries = 0
    for start in range(BETA_DAYS, n - g1_days, 63):     # windows a quarter apart, once a year of betas is known
        best, best_sr = None, -math.inf
        for _ in range(trials):
            d, x, k, paid = random_strategy(series, market, start, g1_days, long_only, spec, rng, beta)
            sr = stats.sharpe(x if g1.get("metric") == "excess" else d)
            if sr > best_sr:
                best_sr, best = sr, (d, x, k, paid)
        d, x, k, paid = best
        rec = gates.Record(daily=d, excess=x, trades=k, n_trials=trials, lag_audit_ok=True,
                           stressed=[v - extra * f for v, f in zip(x, paid)], conservative_fills=True)
        passes += bool(gates.evaluate(g1, rec)[0])
        tries += 1
    # paper-length windows, judged by G2 as written; trade-count clauses are left out because five
    # instruments on daily bars can't make hundreds of trades, which would fail every window. Paper
    # matches the frozen strategy's rerun exactly: the question here is the edge, not the execution
    rng = random.Random(f"gt5-paper-{label}")
    g2_days = max(g2.get("min_days", 20), 20) + g2.get("extend_days", 0)
    rule2 = {k: v for k, v in g2.items() if k not in ("min_trades", "min_risk_trades", "max_days_to_trades")}
    passes2 = tries2 = 0
    for start in range(BETA_DAYS + g1_days, n - g2_days, 21):
        d, x, k, _ = random_strategy(series, market, start, g2_days, long_only, spec, rng, beta)
        rec = gates.Record(daily=d, excess=x, trades=k, risk_trades=k, rerun=list(x), rerun_match=1.0,
                           conservative_fills=True)
        passes2 += bool(gates.evaluate(rule2, rec)[0])
        tries2 += 1
    # the same on synthetic histories of real days, enough to judge G2's bar at its upper bound
    brng = random.Random(f"gt5-bootstrap-{label}")
    passes3 = 0
    for _ in range(BOOTSTRAP_WINDOWS):
        s_series, s_market = _bootstrap(series, BETA_DAYS + g2_days + 1, brng)
        d, x, k, _ = random_strategy(s_series, s_market, BETA_DAYS + 1, g2_days, long_only, spec, brng,
                                     betas(s_series, s_market))
        rec = gates.Record(daily=d, excess=x, trades=k, risk_trades=k, rerun=list(x), rerun_match=1.0,
                           conservative_fills=True)
        passes3 += bool(gates.evaluate(rule2, rec)[0])
    return {"label": label, "g1_days": g1_days, "trials": trials, "passes": passes, "tries": tries,
            "g2_days": g2_days, "passes2": passes2, "tries2": tries2, "passes3": passes3, "tries3": BOOTSTRAP_WINDOWS,
            "span1": (n - g1_days - BETA_DAYS) + g1_days, "span2": (n - g2_days - BETA_DAYS - g1_days) + g2_days}


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="", kind="": out.append(Check(TEST, name, ok, detail, kind))  # noqa: E731
    try:
        _, market = _aligned()
    except Exception as e:  # noqa: BLE001
        add("real data", None, f"no data: {e}")
        return out
    ev = spec.get("evaluation", {})
    cap2 = min(ev.get("max_false_pass_g2", 1.0), anchors.G2_CHANCE)
    add("real data", None, f"{len(market)} aligned days of {', '.join(NAMES)}, "
        f"{market[0]['date']:%Y-%m-%d} to {market[-1]['date']:%Y-%m-%d}")
    with ProcessPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(_one_kind, [(spec, False), (spec, True)]))
    for res in results:
        independent = res["span1"] / res["g1_days"] if res["tries"] else 0.0
        add(f"G1 never passes the best of {res['trials']} {res['label']} strategies on the real history",
            res["tries"] > 0 and res["passes"] == 0,
            (f"{res['passes']}/{res['tries']} windows of {res['g1_days']} days, about {independent:.1f} independent: "
             "an alarm, not a rate (GT-4 measures the rate)") if res["tries"] else
            f"no window: {res['g1_days']} days is longer than the data after a year of betas")
        independent = res["span2"] / res["g2_days"] if res["tries2"] else 0.0
        rate = res["passes2"] / res["tries2"] if res["tries2"] else 0.0
        add(f"G2 on a {res['label']} strategy, real windows (reported)", None,
            f"{res['passes2']}/{res['tries2']} windows of {res['g2_days']} days, about {independent:.0f} independent: {rate:.0%}")
        lo, hi = stats.wilson(res["passes3"], res["tries3"])
        add(f"G2 passes a {res['label']} strategy at most {cap2:.0%} of the time "
            f"(synthetic histories of real days; judged at the upper bound)", res["tries2"] > 0 and hi <= cap2,
            f"{res['passes3']}/{res['tries3']} = {res['passes3'] / res['tries3']:.1%} (95% interval {lo:.1%} to {hi:.1%})")
    return out

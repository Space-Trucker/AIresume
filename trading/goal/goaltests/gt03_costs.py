"""GT-3: cost feasibility by holding horizon. Oracles: published fee schedules and spread data for the
cost of a round trip, volatility measured on real prices, and Grinold & Kahn's rule of thumb for how
predictive a signal can plausibly be (information coefficient 0.05 good, 0.10 great, 0.15 too good to
be true).

The question: at each horizon the goal allows, how large must the average gross gain per trade be,
as a fraction of the typical price move over that horizon, just to pay the costs? A signal with
information coefficient IC earns about 0.8 x IC of a standard deviation per trade when it bets on
the sign, so break-even needs IC = cost / (0.8 x move)."""
from __future__ import annotations

import math

from . import data, stats
from .spec import Check, rule

TEST = "GT-3"

# external cost inputs (see TESTS.md for sources)
SEC_FEE_PER_MILLION = 20.60        # SEC Section 31, from 2026-04-04, on sales
FINRA_TAF_PER_SHARE = 0.000195     # FINRA TAF from 2026-01-01, on sales, capped at $9.79
TYPICAL_PRICE = 50.0               # for the per-share fee in basis points
SPREAD_LARGE_CAP_BPS = 3.7         # average spread across the 100 largest US stocks (Nasdaq)
SLIPPAGE_PER_SIDE_BPS = 1.5        # latency and small-order slippage, an assumption per side
IC_GOOD, IC_GREAT, IC_TOO_GOOD = 0.05, 0.10, 0.15
SIGN_BET_EFFICIENCY = math.sqrt(2 / math.pi)  # E[return x sign(forecast)] / sigma per unit IC

HORIZONS_MIN = [("10 seconds", 10 / 60), ("1 minute", 1), ("5 minutes", 5), ("30 minutes", 30),
                ("1 hour", 60), ("1 day", 390), ("5 days", 5 * 390)]


def external_round_trip_bps() -> float:
    fees = SEC_FEE_PER_MILLION / 1e6 * 1e4 + FINRA_TAF_PER_SHARE / TYPICAL_PRICE * 1e4
    return SPREAD_LARGE_CAP_BPS + 2 * SLIPPAGE_PER_SIDE_BPS + fees


def daily_vol() -> dict:
    """Median daily standard deviation of close-to-close returns, single stocks and the index."""
    out = {}
    for name, start in (("goog", 2005), ("msft", 1999), ("sp500", 1999)):
        b = [r for r in data.bars(name) if r["date"].year >= start]
        rets = [math.log(b[i]["close"] / b[i - 1]["close"]) for i in range(1, len(b))]
        # by year, so one crisis does not decide it
        years = {}
        for i in range(1, len(b)):
            years.setdefault(b[i]["date"].year, []).append(rets[i - 1])
        out[name] = stats.quantile([stats.moments(v)[1] for v in years.values() if len(v) > 100], 0.5)
    return out


def ic_needed(cost_bps: float, move_bps: float) -> float:
    return cost_bps / (SIGN_BET_EFFICIENCY * move_bps)


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    ext = external_round_trip_bps()
    costs = spec.get("costs", {})
    stated = costs.get("round_trip_cost_bps")
    add("the cost model is not cheaper than published costs", stated is not None and stated >= ext,
        f"stated {stated} bps vs {ext:.2f} bps (spread {SPREAD_LARGE_CAP_BPS}, slippage 2 x {SLIPPAGE_PER_SIDE_BPS}, fees)"
        if stated is not None else f"no cost is stated; published costs come to {ext:.2f} bps per round trip")
    cost = stated if stated is not None else ext
    try:
        vol = daily_vol()
    except Exception as e:  # noqa: BLE001
        add("horizon feasibility", None, f"no data: {e}")
        return out
    stock_d = (vol["goog"] + vol["msft"]) / 2 * 1e4  # bps per day
    rows = []
    for label, minutes in HORIZONS_MIN:
        move = stock_d * math.sqrt(minutes / 390)
        rows.append((label, minutes, move, ic_needed(cost, move)))
    table = "; ".join(f"{l}: move {m:.0f} bps, IC {ic:.3f}" for l, _, m, ic in rows)
    add("typical stock moves by horizon (real data)", None,
        f"daily {stock_d:.0f} bps (GOOG, MSFT), index {vol['sp500'] * 1e4:.0f} bps; break-even IC at {cost:.1f} bps: {table}")
    feasible = [l for l, _, _, ic in rows if ic <= IC_GREAT]
    infeasible = [l for l, _, _, ic in rows if ic > IC_TOO_GOOD]
    add("horizons where costs need an implausible signal (IC > 0.15)", None, ", ".join(infeasible) or "none")

    ret = spec.get("returns", {})
    edge_min = ret.get("edge_min_horizon_minutes")
    if edge_min is None:
        add("the goal says which horizons the edge must come from", False,
            f"holding from seconds is allowed, but only {', '.join(feasible)} can pay costs with at most a 'great' signal")
    else:
        move = stock_d * math.sqrt(min(edge_min, 5 * 390) / 390)
        ic = ic_needed(cost, move)
        add("at the edge's shortest horizon, costs need at most a 'great' signal (IC <= 0.10)", ic <= IC_GREAT,
            f"{edge_min:g} min: move {move:.0f} bps, break-even IC {ic:.3f}")

    # the return objective at the stated activity: the gross edge each trade needs
    a, r = spec.get("activity", {}), spec.get("risk", {})
    need = [k for k in ("min_net_excess_sharpe",) if k not in ret] + \
           [k for k in ("vol_target_daily_pct",) if k not in r] + \
           [k for k in ("planned_risk_trades_per_week", "typical_holding_minutes") if k not in a] + \
           [k for k in ("typical_position_pct",) if k not in r]
    if need:
        add("the return objective is achievable at the stated activity", False, "unspecified: " + ", ".join(need))
        return out
    sigma_annual = r["vol_target_daily_pct"] / 100 * math.sqrt(252)
    trades = a["planned_risk_trades_per_week"] * 52
    size = r["typical_position_pct"] / 100
    drag = trades * size * cost / 1e4
    move = stock_d * math.sqrt(min(a["typical_holding_minutes"], 5 * 390) / 390)
    target = ret.get("target_net_excess_sharpe", ret["min_net_excess_sharpe"])
    for label, sr in (("targeted", target), ("minimum", ret["min_net_excess_sharpe"])):
        net = sr * sigma_annual
        gross_per_trade_bps = (net + drag) / (trades * size) * 1e4
        ic = gross_per_trade_bps / (SIGN_BET_EFFICIENCY * move)
        detail = (f"Sharpe {sr:g}: net {net:.1%}/yr + costs {drag:.2%}/yr over {trades} trades of {size:.1%}: "
                  f"{gross_per_trade_bps:.1f} bps gross per trade vs a {move:.0f} bps move: IC {ic:.3f}")
        if label == "targeted":
            add("the targeted return needs at most a 'great' signal at the planned activity", ic <= IC_GREAT, detail)
        else:
            add("the minimum return at the planned activity", None, detail)
    # the cost stress (KR1.3) at the planned activity: the targeted edge must survive it, or G1 would
    # reject the very strategy the goal aims for
    mult = costs.get("stress_cost_multiplier")
    floor = rule(spec, "G1").get("stress_sr_min")
    if mult and floor is not None:
        stressed = (target * sigma_annual - (mult - 1) * drag) / sigma_annual
        add("the targeted edge survives the cost stress at the planned activity", stressed >= floor,
            f"Sharpe {target:g} - {mult - 1:g} x costs {drag:.2%}/yr / volatility {sigma_annual:.1%}/yr = {stressed:.2f} "
            f"vs a floor of {floor:g}")
    return out

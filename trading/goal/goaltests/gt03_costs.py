"""GT-3: cost feasibility by holding horizon. Oracles: published fee schedules and spread data for the
cost of a round trip, volatility measured on real prices, and practitioners' labels for how
predictive a signal can plausibly be (information coefficient 0.05 good and 0.10 very good, MSCI Barra;
0.15 exceptional).

The question: at each horizon the goal allows, how large must the average gross gain per trade be,
as a fraction of the typical price move over that horizon, just to pay the costs? A signal with
information coefficient IC earns about 0.8 x IC of a standard deviation per trade when it bets on
the sign, so break-even needs IC = cost / (0.8 x move)."""
from __future__ import annotations

import functools
import math

from . import data, stats
from .spec import Check, rule

TEST = "GT-3"
KIND = "external"

# external cost inputs (see TESTS.md for sources)
SEC_FEE_PER_MILLION = 20.60        # SEC Section 31, from 2026-04-04, on sales
FINRA_TAF_PER_SHARE = 0.000195     # FINRA TAF from 2026-01-01, on sales, capped at $9.79
TYPICAL_PRICE = 50.0               # for the per-share fee in basis points
SPREAD_LARGE_CAP_BPS = 3.7         # average spread across the 100 largest US stocks (Nasdaq)
IMPACT_Y = (0.5, 0.75, 1.0)        # the square-root law's coefficient: low, central, high (Almgren et al. 2005,
                                   # Toth et al. 2011); impact per side = Y x daily volatility x sqrt(size / volume)
SLIPPAGE_NO_DATA_BPS = 1.5         # per side, used only when the price data can't be read, and then said so
IC_GOOD, IC_GREAT, IC_TOO_GOOD = 0.05, 0.10, 0.15
SIGN_BET_EFFICIENCY = math.sqrt(2 / math.pi)  # E[return x sign(forecast)] / sigma per unit IC

HORIZONS_MIN = [("10 seconds", 10 / 60), ("1 minute", 1), ("5 minutes", 5), ("30 minutes", 30),
                ("1 hour", 60), ("1 day", 390), ("5 days", 5 * 390)]


def fees_bps() -> float:
    return SEC_FEE_PER_MILLION / 1e6 * 1e4 + FINRA_TAF_PER_SHARE / TYPICAL_PRICE * 1e4


def impact_bps(daily_vol_bps: float, size_pct_of_volume: float, y: float) -> float:
    """Market impact per side by the square-root law."""
    return y * daily_vol_bps * math.sqrt(size_pct_of_volume / 100)


@functools.lru_cache(maxsize=1)
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
    add = lambda name, ok, detail="", kind="": out.append(Check(TEST, name, ok, detail, kind))  # noqa: E731
    costs = spec.get("costs", {})
    stated = costs.get("round_trip_cost_bps")
    adv = spec.get("constraints", {}).get("max_position_adv_pct")
    try:
        vol = daily_vol()
    except Exception as e:  # noqa: BLE001
        vol, note = None, f"no data ({e}): slippage {SLIPPAGE_NO_DATA_BPS} bps a side assumed"
    stock_d = (vol["goog"] + vol["msft"]) / 2 * 1e4 if vol else None  # bps per day
    # slippage from outside the goal: the square-root law at the goal's participation limit, the
    # central coefficient (a name trading at the universe's minimum volume, a full-size position)
    if stock_d is not None and adv is not None:
        side = impact_bps(stock_d, adv, IMPACT_Y[1])
        note = f"impact {side:.2f} bps a side at {adv:g}% of daily volume (square-root law, Y {IMPACT_Y[1]})"
    else:
        side = SLIPPAGE_NO_DATA_BPS
        note = note if vol is None else f"no participation limit: slippage {SLIPPAGE_NO_DATA_BPS} bps a side assumed"
    ext = SPREAD_LARGE_CAP_BPS + 2 * side + fees_bps()
    add("the cost model is not cheaper than published costs", stated is not None and stated >= ext,
        (f"stated {stated} bps vs {ext:.2f} bps: spread {SPREAD_LARGE_CAP_BPS} (the 100 largest stocks), {note}, fees"
         if stated is not None else f"no cost is stated; published costs come to {ext:.2f} bps per round trip"))
    # the stress must cover the plan's own worst case within its limits: every trade in a name at the
    # universe's spread limit, full size at the participation limit. A milder stress tests less than
    # the limits allow; KR1.3's check below bounds it from the other side
    spread_cap, mult = spec.get("constraints", {}).get("universe_max_spread_bps"), costs.get("stress_cost_multiplier")
    if stated is not None and spread_cap is not None:
        at_limits = spread_cap + 2 * side + fees_bps()
        stressed_cost = stated * (mult or 1)
        add("the stressed cost covers a round trip at the universe's limits", at_limits <= stressed_cost,
            f"{spread_cap:g} bps spread + 2 x {side:.2f} impact + {fees_bps():.2f} fees = {at_limits:.2f} bps vs "
            f"{stated:g} x {mult or 1:g} = {stressed_cost:.2f} bps")
    # a full-size position in the least liquid name the universe admits must fit the participation limit
    c = spec.get("constraints", {})
    if adv is not None and "universe_min_dollar_volume_usd" in c and spec.get("risk", {}).get("typical_position_pct"):
        dollars = c.get("starting_equity_usd", 100000) * spec["risk"]["typical_position_pct"] / 100
        room = adv / 100 * c["universe_min_dollar_volume_usd"]
        add("a typical position fits the participation limit in the least liquid name the universe admits", dollars <= room,
            f"${dollars:,.0f} vs {adv:g}% of ${c['universe_min_dollar_volume_usd']:,} = ${room:,.0f}", kind="consistency")
    cost = stated if stated is not None else ext
    if vol is None:
        add("horizon feasibility", None, note)
        return out
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
    edge_min = ret.get("planned_edge_horizon_minutes", ret.get("edge_min_horizon_minutes"))
    if edge_min is None:
        add("the goal says which horizons the planned edge comes from", False,
            f"holding from seconds is allowed, but only {', '.join(feasible)} can pay costs with at most a 'great' signal")
    else:
        # a trade opens only when its expected gain is a multiple of its cost (the entry rule), so the
        # planned edge must clear that multiple, not just break even
        add("the goal names the horizon the planned edge comes from", True, f"{edge_min:g} minutes")
        # two models of the gain per trade, and neither decides the horizon: betting the sign of every
        # forecast (gain = 0.8 x IC x move), and trading only the forecasts the entry rule admits, the
        # tail of a joint-normal forecast (gain = IC x move x |z| for |z| above the entry threshold)
        entry = spec.get("activity", {}).get("entry_min_gain_to_cost", 1)
        rows = []
        for label, minutes in (("2.5 hours", 150), ("1 day", 390), ("2 days", 780), ("3 days", 1170)):
            move = stock_d * math.sqrt(minutes / 390)
            ic_sign = ic_needed(cost * entry, move)
            z = cost * entry / (IC_GREAT * move)
            share = 2 * (1 - stats.N01.cdf(z))
            rows.append(f"{label}: every-forecast IC {ic_sign:.3f}; at IC 0.10, {share:.1%} of forecasts clear the entry rule")
        add(f"the entry rule (gain at least {entry:g} x cost) by horizon, two models", None, "; ".join(rows))

    # market impact at the participation limit (the square-root law) against the slippage the cost model
    # charges, at its stress level: the central estimate must fit
    slip = costs.get("slippage_bps_per_side")
    if adv is not None and slip is not None:
        lo, mid, hi = (impact_bps(stock_d, adv, y) for y in IMPACT_Y)
        add("market impact at the participation limit fits the slippage charged at the stress level",
            mid <= slip * (mult or 1),
            f"{adv:g}% of daily volume: {lo:.1f} to {hi:.1f} bps a side, central {mid:.1f}, vs {slip:g} x {mult or 1:g} "
            f"= {slip * (mult or 1):.2f} bps")

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

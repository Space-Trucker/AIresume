"""GT-2: internal consistency. Oracle: arithmetic on the stated limits, plus the size of real overnight
price gaps (S&P 500 and two large stocks) for the limits that must hold across a night."""
from __future__ import annotations

from . import data, stats
from .spec import Check, constraints, risk

TEST = "GT-2"
STOP_SLIPPAGE = 1.25   # a stop in a fast market fills worse than its price; 25% worse is assumed
# stress gaps from outside the goal: the largest non-earnings overnight gap in the data (Microsoft,
# 24 April 2000, -14.8% on the antitrust ruling), and a market-wide fall of 7%, the level at which US
# exchanges halt all trading (market-wide circuit breaker, level 1)
STRESS_SINGLE_GAP = 0.148
STRESS_MARKET_GAP = 0.07


def overnight_gaps() -> dict:
    """|open / previous close - 1| quantiles. For single stocks, the 2% largest gaps are dropped as a
    proxy for earnings nights, which the goal forbids holding through."""
    out = {}
    for name in ("sp500", "goog", "msft"):
        b = [r for r in data.bars(name) if r["date"].year >= 1999]
        gaps = sorted(abs(b[i]["open"] / b[i - 1]["close"] - 1) for i in range(1, len(b)))
        if name != "sp500":
            gaps = gaps[: int(len(gaps) * 0.98)]
        out[name] = {"q99": stats.quantile(gaps, 0.99), "q999": stats.quantile(gaps, 0.999), "n": len(gaps)}
    return out


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    r, c = risk(spec), constraints(spec)
    daily = r.get("daily_loss_limit_pct")

    # 1. every open position stopped out at once, with slippage, must fit inside the daily loss limit
    per = r.get("risk_per_position_pct", r.get("risk_per_trade_pct"))
    if daily and per and r.get("max_positions"):
        open_risk = min(r.get("max_open_risk_pct", per * r["max_positions"]), per * r["max_positions"])
        worst = open_risk * STOP_SLIPPAGE
        add("all stops hit at once stays inside the daily loss limit", worst <= daily,
            f"{open_risk:g}% open risk x {STOP_SLIPPAGE} slippage = {worst:.2f}% vs {daily:g}%")
    else:
        add("all stops hit at once stays inside the daily loss limit", False, "a limit is unspecified")

    # 2. positions held overnight: a gap jumps past the stop
    if c.get("max_holding_trading_days", 0) > 1 or c.get("max_holding_calendar_days", 0) > 1:
        try:
            gaps = overnight_gaps()
        except Exception as e:  # noqa: BLE001
            add("overnight gaps fit inside the daily loss limit", None, f"no data: {e}")
        else:
            stock_q99 = max(gaps["goog"]["q99"], gaps["msft"]["q99"])
            index_q99 = gaps["sp500"]["q99"]
            per_pos = r.get("max_position_overnight_pct", r.get("max_position_pct"))
            gross = r.get("max_overnight_gross_pct", (per_pos or 0) * r.get("max_positions", 0))
            if per_pos is None or daily is None:
                add("overnight gaps fit inside the daily loss limit", False, "a limit is unspecified")
            else:
                single = per_pos * stock_q99
                book = gross * max(index_q99, stock_q99 * 0.5)  # a market-wide gap moves every name
                add("one position's 1-in-100 overnight gap fits inside the daily loss limit", single <= daily,
                    f"{per_pos:g}% x {stock_q99:.2%} = {single:.2f}% vs {daily:g}%")
                add("the overnight book's 1-in-100 market gap fits inside the daily loss limit", book <= daily,
                    f"{gross:g}% gross x {max(index_q99, stock_q99 * 0.5):.2%} = {book:.2f}% vs {daily:g}%")
                worst = per_pos * STRESS_SINGLE_GAP
                add("one position through the worst real non-earnings gap (-14.8%) fits inside the daily loss limit",
                    worst <= daily, f"{per_pos:g}% x 14.8% = {worst:.2f}% vs {daily:g}%")
                crash = gross * STRESS_MARKET_GAP
                add("the overnight book through a 7% market-wide gap fits inside the daily loss limit",
                    crash <= daily, f"{gross:g}% gross x 7% = {crash:.2f}% vs {daily:g}%")
            add("overnight exposure limited separately from intraday", "max_position_overnight_pct" in r,
                "" if "max_position_overnight_pct" in r else "positions may be held for days, but only intraday sizes are set")

    # 3. gross exposure from the position limits
    if r.get("max_positions") and r.get("max_position_pct") and r.get("max_gross_exposure_pct"):
        full = r["max_positions"] * r["max_position_pct"]
        add("position limits and the gross exposure limit", None,
            f"{r['max_positions']} x {r['max_position_pct']:g}% = {full:g}% vs {r['max_gross_exposure_pct']:g}%: "
            + ("the gross limit binds first" if full > r["max_gross_exposure_pct"] else "the position limits bind first"))

    # 4. short selling borrows shares: "no borrowed money" contradicts it unless leverage is a number
    shorts = "short" in c.get("directions", [])
    text = (r.get("leverage_text", "") or "").lower()
    add("short selling is consistent with the leverage rule",
        not (shorts and "borrow" in text),
        "a short sale is borrowed stock; state leverage as gross exposure instead" if shorts and "borrow" in text else "")

    # 5. drawdown halt above the daily limit, and how many limit days reach it
    dd = r.get("max_drawdown_halt_pct")
    if daily and dd:
        add("drawdown halt is above the daily loss limit", dd > daily, f"halt after {dd / daily:.0f} days at the limit")

    # 6. a volatility budget, and the daily limit far enough above ordinary days
    vol = r.get("vol_target_daily_pct")
    if vol and daily:
        add("daily loss limit is at least 3 ordinary days of volatility", daily >= 3 * vol, f"{daily:g}% vs 3 x {vol:g}%")
    else:
        add("volatility budget stated", False, "without it, drawdown and loss limits can't be judged")

    # 7. activity and costs: the cost budget must allow the minimum activity
    a, costs = spec.get("activity", {}), spec.get("costs", {})
    need = ("min_risk_trades_per_week", "cost_budget_pct_per_year")
    if all(k in a for k in need) and "round_trip_cost_bps" in costs and r.get("max_position_pct"):
        typical = r.get("typical_position_pct", r["max_position_pct"])
        yearly = a["min_risk_trades_per_week"] * 52 * typical / 100 * costs["round_trip_cost_bps"] / 100
        add("the minimum activity fits the cost budget", yearly <= a["cost_budget_pct_per_year"],
            f"{a['min_risk_trades_per_week']}/week x {typical:g}% x {costs['round_trip_cost_bps']:g} bps "
            f"= {yearly:.2f}%/yr vs {a['cost_budget_pct_per_year']:g}%")
    else:
        add("activity bounds and a cost budget stated", False, "constant trading has no upper or lower bound")

    # 8. returns objective consistent with the drawdown halt: a good strategy should rarely be halted
    ret = spec.get("returns", {})
    add("a return objective is stated", "min_net_excess_sharpe" in ret,
        "" if "min_net_excess_sharpe" in ret else "'makes money' has no size")
    return out

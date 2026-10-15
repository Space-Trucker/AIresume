"""GT-2: internal consistency. Oracles: arithmetic on the stated limits; queueing theory (Little's law
and the Erlang loss formula) for whether the planned activity fits the position limit; and the size of
real overnight price gaps for the limits that must hold across a night. The gap data are daily prices
of the S&P 500 and five large stocks, 1999-2018 (``data.py``)."""
from __future__ import annotations

import math

from . import data, stats
from .spec import Check, constraints, risk

TEST = "GT-2"
STOP_SLIPPAGE = 1.25   # a stop in a fast market fills worse than its price; 25% worse is assumed
SESSION_MINUTES = 390
STOCKS = ("goog", "msft", "orcl", "nvda", "yhoo")
# Stress gaps from outside the goal, each checked against the price data below:
# * a long held overnight: NVIDIA opened 28.0% down on 3 July 2008 after an unscheduled revenue warning
#   and a charge for faulty chips, announced after the previous close (not an earnings release, so the
#   earnings blackout would not have avoided it);
# * a short held overnight: Yahoo opened 49.5% up on 1 February 2008 on Microsoft's unsolicited bid,
#   a 62% premium to the previous close;
# * the whole book: see STRESS_MARKET_GAP below.
LONG_GAP = ("nvda", "2008-07-03", -0.280, "NVIDIA, 3 July 2008, unscheduled revenue warning")
SHORT_GAP = ("yhoo", "2008-02-01", 0.495, "Yahoo, 1 February 2008, takeover bid")
# beyond the data, from public records: SVB Financial (S&P 500) fell 60% on 9 March 2023, was halted
# before the next open and never traded on Nasdaq again; on 13 March 2023 First Republic and Western
# Alliance fell 60-75% together; US exchanges halt all trading for 15 minutes at a 13% market fall
# (level 2) before 15:25, but no breaker bounds an overnight gap
SVB_EVENT = "SVB, 10 March 2023"
CONTAGION_EVENT = "regional banks, 13 March 2023"
STRESS_MARKET_GAP = 0.13


def _gap_on(name: str, day: str) -> float:
    b = data.bars(name)
    i = next(i for i, r in enumerate(b) if r["date"].strftime("%Y-%m-%d") == day)
    return b[i]["open"] / b[i - 1]["close"] - 1


def overnight_gaps() -> dict:
    """|open / previous close - 1| quantiles of single stocks from 1999, with the 2% largest gaps
    dropped as a proxy for earnings nights, which the goal forbids holding through. (The index's
    opening prices in this data are not reliable, so it is not used for gaps.)"""
    out = {}
    for name in STOCKS:
        b = [r for r in data.bars(name) if r["date"].year >= 1999]
        gaps = sorted(abs(b[i]["open"] / b[i - 1]["close"] - 1) for i in range(1, len(b)))
        gaps = gaps[: int(len(gaps) * 0.98)]
        out[name] = {"q99": stats.quantile(gaps, 0.99), "n": len(gaps)}
    return out


def residual_vol() -> float:
    """Median over years and stocks of the daily volatility left after removing the market (S&P 500),
    the volatility a long-short book of single names carries."""
    market = {r["date"]: r["close"] for r in data.bars("sp500")}
    vols = []
    for name in ("goog", "msft"):
        b = [r for r in data.bars(name) if r["date"] in market and r["date"].year >= 1999]
        for year in sorted({r["date"].year for r in b}):
            rows = [r for r in b if r["date"].year == year]
            if len(rows) < 200:
                continue
            y = [rows[i]["close"] / rows[i - 1]["close"] - 1 for i in range(1, len(rows))]
            x = [market[rows[i]["date"]] / market[rows[i - 1]["date"]] - 1 for i in range(1, len(rows))]
            _, _, resid = stats.ols_alpha_beta(y, x)
            vols.append(stats.moments(resid)[1])
    return stats.quantile(vols, 0.5)


def erlang_b(load: float, servers: int) -> float:
    """Share of arrivals that find every server busy (Erlang's loss formula)."""
    b = 1.0
    for k in range(1, servers + 1):
        b = load * b / (k + load * b)
    return b


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731
    r, c = risk(spec), constraints(spec)
    a, costs = spec.get("activity", {}), spec.get("costs", {})
    daily = r.get("daily_loss_limit_pct")

    # 1. stops hit together, with slippage, must fit inside the daily loss limit. A market-wide move
    #    stops out one side of the book; a goal that caps only the total must survive all of it.
    per = r.get("risk_per_position_pct", r.get("risk_per_trade_pct"))
    if daily and per and r.get("max_positions"):
        if "max_open_risk_per_side_pct" in r:
            side = min(r["max_open_risk_per_side_pct"], per * r["max_positions"])
            worst = side * STOP_SLIPPAGE
            add("every stop on one side hit at once (a market-wide move) stays inside the daily loss limit",
                worst <= daily, f"{side:g}% open risk per side x {STOP_SLIPPAGE} slippage = {worst:.2f}% vs {daily:g}%")
            total = min(r.get("max_open_risk_pct", 2 * side), 2 * side)
            bound = r.get("max_day_loss_pct", daily)
            add("every stop on both sides hit in one day (a whipsaw) stays inside the worst-day bound",
                total * STOP_SLIPPAGE <= bound,
                f"{total:g}% total open risk x {STOP_SLIPPAGE} = {total * STOP_SLIPPAGE:.2f}% vs {bound:g}%")
        else:
            total = min(r.get("max_open_risk_pct", per * r["max_positions"]), per * r["max_positions"])
            worst = total * STOP_SLIPPAGE
            add("every stop hit at once stays inside the daily loss limit", worst <= daily,
                f"{total:g}% open risk x {STOP_SLIPPAGE} slippage = {worst:.2f}% vs {daily:g}%")
    else:
        add("every stop hit at once stays inside the daily loss limit", False, "a limit is unspecified")

    # 2. jumps: a gap or a halt moves the price past the stop, so the loss is set by the position's
    #    size and the jump, not by the stop
    if c.get("max_holding_trading_days", 0) > 1 or c.get("max_holding_calendar_days", 0) > 1:
        try:
            gaps = overnight_gaps()
            long_gap, short_gap = _gap_on(*LONG_GAP[:2]), _gap_on(*SHORT_GAP[:2])
        except Exception as e:  # noqa: BLE001
            add("overnight gaps fit inside the daily loss limit", None, f"no data: {e}")
        else:
            add("stress gaps match the price data", abs(long_gap - LONG_GAP[2]) < 0.001 and abs(short_gap - SHORT_GAP[2]) < 0.001,
                f"{LONG_GAP[3]}: {long_gap:+.1%}; {SHORT_GAP[3]}: {short_gap:+.1%}")
            either = r.get("max_position_overnight_pct", r.get("max_position_pct"))
            long_cap = r.get("max_overnight_long_pct", either)
            short_cap = r.get("max_overnight_short_pct", either)
            stock_q99 = max(gaps[n]["q99"] for n in STOCKS)
            jump = r.get("jump_overnight_pct")
            if long_cap is None or short_cap is None or daily is None:
                add("overnight gaps fit inside the daily loss limit", False, "a limit is unspecified")
            elif jump is not None:
                worst_seen = max(abs(LONG_GAP[2]), SHORT_GAP[2]) * 100
                add("the overnight jump assumption covers the largest gaps in the data", jump >= worst_seen,
                    f"{jump:g}% vs {SHORT_GAP[3]} {SHORT_GAP[2]:+.1%} and {LONG_GAP[3]} {LONG_GAP[2]:+.1%}")
                one = max(long_cap, short_cap) * jump / 100
                add("one position held overnight through the assumed jump fits inside the daily loss limit", one <= daily,
                    f"{max(long_cap, short_cap):g}% x {jump:g}% = {one:.2f}% vs {daily:g}%")
                j_in = r.get("jump_intraday_pct")
                if j_in is not None and r.get("max_position_pct"):
                    intraday = r["max_position_pct"] * j_in / 100
                    add("one position through an intraday jump (a halt, two price bands) fits inside the daily loss limit",
                        intraday <= daily, f"{r['max_position_pct']:g}% x {j_in:g}% = {intraday:.2f}% vs {daily:g}%")
                bound = r.get("max_jump_loss_pct")
                if bound is not None:
                    total = max(long_cap, short_cap)
                    add(f"a total loss in one name held overnight stays within the jump-loss bound ({SVB_EVENT})",
                        total <= bound, f"{total:g}% vs {bound:g}%")
                    if "max_overnight_industry_pct" in r:
                        industry = r["max_overnight_industry_pct"] * jump / 100
                        add(f"an industry-wide jump stays within the jump-loss bound ({CONTAGION_EVENT})", industry <= bound,
                            f"{r['max_overnight_industry_pct']:g}% x {jump:g}% = {industry:.2f}% vs {bound:g}%")
                    else:
                        add("overnight exposure to one industry is limited", False, "a jump that hits a whole industry is unbounded")
            else:
                single = max(long_cap, short_cap) * stock_q99
                add("one position's 1-in-100 overnight gap fits inside the daily loss limit", single <= daily,
                    f"{max(long_cap, short_cap):g}% x {stock_q99:.2%} = {single:.2f}% vs {daily:g}%")
                worst_long = long_cap * abs(LONG_GAP[2])
                add("one long held overnight through the worst unscheduled gap down fits inside the daily loss limit",
                    worst_long <= daily, f"{long_cap:g}% x {abs(LONG_GAP[2]):.1%} ({LONG_GAP[3]}) = {worst_long:.2f}% vs {daily:g}%")
                worst_short = short_cap * SHORT_GAP[2]
                add("one short held overnight through a takeover gap fits inside the daily loss limit",
                    worst_short <= daily, f"{short_cap:g}% x {SHORT_GAP[2]:.1%} ({SHORT_GAP[3]}) = {worst_short:.2f}% vs {daily:g}%")
            # the whole book: a market gap moves every name; with a net limit, longs and shorts offset.
            # Circuit breakers pause trading but do not bound an overnight gap, so the stress is the
            # level-2 breaker (13%), not the level-1 pause (7%)
            net = r.get("max_overnight_net_pct", r.get("max_overnight_gross_pct",
                                                        (long_cap or 0) * r.get("max_positions", 0)))
            if daily is not None:
                crash = net * STRESS_MARKET_GAP
                add("the overnight book through a 13% market-wide gap fits inside the daily loss limit", crash <= daily,
                    f"{net:g}% {'net' if 'max_overnight_net_pct' in r else 'gross'} x 13% = {crash:.2f}% vs {daily:g}%")
            add("overnight exposure limited separately from intraday",
                any(k in r for k in ("max_position_overnight_pct", "max_overnight_long_pct")),
                "" if any(k in r for k in ("max_position_overnight_pct", "max_overnight_long_pct"))
                else "positions may be held for days, but only intraday sizes are set")
            add("jumps sized as jumps (a gap or a halt is not a slipped stop)", jump is not None,
                "" if jump is not None else "the limits assume a stop bounds the loss; across a gap or a halt it doesn't")

    # 3. the planned activity must fit the position limit and the exposure limits (Little's law:
    #    average open positions = trades a day x days held; Erlang: how often every slot is full)
    plan = ("planned_risk_trades_per_week", "typical_holding_minutes")
    if all(k in a for k in plan) and r.get("max_positions"):
        open_avg = a["planned_risk_trades_per_week"] / 5 * a["typical_holding_minutes"] / SESSION_MINUTES
        blocked = erlang_b(open_avg, int(r["max_positions"]))
        add("the planned activity fits the position limit (a new trade finds every slot full at most 10% of the time)",
            blocked <= 0.10, f"{a['planned_risk_trades_per_week']}/week held {a['typical_holding_minutes'] / SESSION_MINUTES:.1f} days "
            f"= {open_avg:.1f} open on average; {r['max_positions']} slots full {blocked:.1%} of the time")
        size = r.get("typical_position_pct")
        if size:
            gross = open_avg * size
            cap = r.get("max_gross_exposure_pct", math.inf)
            add("the planned book fits the gross exposure limit", gross <= cap,
                f"{open_avg:.1f} x {size:g}% = {gross:.0f}% vs {cap:g}%")
            if a["typical_holding_minutes"] > SESSION_MINUTES:
                on_cap = r.get("max_overnight_gross_pct", math.inf)
                add("the planned book can be held overnight (typical holds span nights)", gross <= on_cap,
                    f"{gross:.0f}% held overnight vs an overnight gross limit of {on_cap:g}%")
                caps = [v for v in (r.get("max_overnight_long_pct"), r.get("max_overnight_short_pct"),
                                    r.get("max_position_overnight_pct")) if v]
                if caps:
                    add("a typical position fits the overnight position limits", size <= max(caps),
                        f"{size:g}% vs {', '.join(f'{v:g}%' for v in caps)}")
            vol = r.get("vol_target_daily_pct")
            if vol:
                try:
                    resid = residual_vol()
                except Exception as e:  # noqa: BLE001
                    add("the volatility budget is within reach of the planned book", None, f"no data: {e}")
                else:
                    book = size / 100 * resid * math.sqrt(open_avg) * 100
                    add("the volatility budget is within reach of the planned book (0.5 to 1.5 times what it produces)",
                        0.5 <= vol / book <= 1.5,
                        f"{open_avg:.1f} positions x {size:g}% x {resid:.2%} market-neutral daily volatility per stock "
                        f"= {book:.2f}%/day vs a budget of {vol:g}%")
    else:
        add("the planned activity fits the position limit", False, "no planned activity or holding time")

    # 4. gross exposure from the position limits
    if r.get("max_positions") and r.get("max_position_pct") and r.get("max_gross_exposure_pct"):
        full = r["max_positions"] * r["max_position_pct"]
        add("position limits and the gross exposure limit", None,
            f"{r['max_positions']} x {r['max_position_pct']:g}% = {full:g}% vs {r['max_gross_exposure_pct']:g}%: "
            + ("the gross limit binds first" if full > r["max_gross_exposure_pct"] else "the position limits bind first"))

    # 5. short selling borrows shares: "no borrowed money" contradicts it unless leverage is a number
    shorts = "short" in c.get("directions", [])
    text = (r.get("leverage_text", "") or "").lower()
    add("short selling is consistent with the leverage rule",
        not (shorts and "borrow" in text),
        "a short sale is borrowed stock; state leverage as gross exposure instead" if shorts and "borrow" in text else "")

    # 6. drawdown halt above the daily limit, and how many limit days reach it
    dd = r.get("max_drawdown_halt_pct")
    if daily and dd:
        add("drawdown halt is above the daily loss limit", dd > daily, f"halt after {dd / daily:.0f} days at the limit")

    # 7. a volatility budget, and the daily limit far enough above ordinary days
    vol = r.get("vol_target_daily_pct")
    if vol and daily:
        add("daily loss limit is at least 3 ordinary days of volatility", daily >= 3 * vol, f"{daily:g}% vs 3 x {vol:g}%")
    else:
        add("volatility budget stated", False, "without it, drawdown and loss limits can't be judged")

    # 8. activity and costs: the cost budget must allow the minimum and the planned activity
    need = ("min_risk_trades_per_week", "cost_budget_pct_per_year")
    if all(k in a for k in need) and "round_trip_cost_bps" in costs and r.get("max_position_pct"):
        typical = r.get("typical_position_pct", r["max_position_pct"])
        for label, key in (("minimum", "min_risk_trades_per_week"), ("planned", "planned_risk_trades_per_week")):
            if key not in a:
                continue
            yearly = a[key] * 52 * typical / 100 * costs["round_trip_cost_bps"] / 100
            add(f"the {label} activity fits the cost budget", yearly <= a["cost_budget_pct_per_year"],
                f"{a[key]}/week x {typical:g}% x {costs['round_trip_cost_bps']:g} bps "
                f"= {yearly:.2f}%/yr vs {a['cost_budget_pct_per_year']:g}%")
    else:
        add("activity bounds and a cost budget stated", False, "constant trading has no upper or lower bound")

    # 9. a return objective, stated as a return too (the IPS asks for one), consistent with the
    #    Sharpe ratio at the volatility budget
    ret = spec.get("returns", {})
    add("a return objective is stated", "min_net_excess_sharpe" in ret,
        "" if "min_net_excess_sharpe" in ret else "'makes money' has no size")
    if vol and "min_net_excess_sharpe" in ret:
        yearly = vol * math.sqrt(252)
        for sr_key, pct_key in (("min_net_excess_sharpe", "min_net_excess_return_pct"),
                                ("target_net_excess_sharpe", "target_net_excess_return_pct")):
            if sr_key in ret and pct_key in ret:
                implied = ret[sr_key] * yearly
                add(f"the stated return matches the Sharpe ratio at the volatility budget ({pct_key})",
                    abs(implied - ret[pct_key]) <= 0.5,
                    f"Sharpe {ret[sr_key]:g} x {yearly:.2f}%/yr = {implied:.1f}%/yr vs {ret[pct_key]:g}%")
    return out

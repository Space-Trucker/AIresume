"""GT-2: internal consistency. Oracles: arithmetic on the stated limits; queueing theory (Little's law
and the Erlang loss formula) for whether the planned activity fits the position limit; and the size of
real overnight price gaps for the limits that must hold across a night. The gap data are daily prices
of the S&P 500 and five large stocks, 1999-2018 (``data.py``)."""
from __future__ import annotations

import functools
import math
import random

from . import anchors, data, stats
from .spec import Check, constraints, risk, rule

TEST = "GT-2"
KIND = "consistency"
STOP_SLIPPAGE_NO_DATA = 1.25   # used only when the price data can't be read, and then said so
STRESS_DAY_MOVE = 0.03         # a market-wide stress day: the S&P 500 closes 3% or more against the side
MIN_STOPS_PER_DAY = 5          # stress days with fewer stops hit say little about a book's average fill
DEFAULT_STOP_ATR = 2.0         # the stop distance when the goal plans none (GT-5's random strategies use it)
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
# adverse single-name jumps for the drawdown simulation, as a fraction of the position: NVIDIA's
# opening gap, Yahoo's against a short, First Republic's fall on 13 March 2023, SVB's total loss
JUMPS = (0.280, 0.495, 0.618, 1.0)
# how often a stock gaps 20% or more overnight away from earnings: 2 of 14,953 stock-nights in the
# five stocks' prices, rounded up to 1.5 in 10,000 (the research notes on overnight sizing)
JUMP_RATE = 1.5e-4


def _gap_on(name: str, day: str) -> float:
    b = data.bars(name)
    i = next(i for i, r in enumerate(b) if r["date"].strftime("%Y-%m-%d") == day)
    return b[i]["open"] / b[i - 1]["close"] - 1


@functools.lru_cache(maxsize=1)
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


def _atr(b: list[dict], i: int, n: int = 14) -> float:
    trs = [max(b[j]["high"] - b[j]["low"], abs(b[j]["high"] - b[j - 1]["close"]), abs(b[j]["low"] - b[j - 1]["close"]))
           / b[j - 1]["close"] for j in range(max(1, i - n + 1), i + 1)]
    return sum(trs) / len(trs)


@functools.lru_cache(maxsize=1)
def typical_atr() -> float:
    """Median 14-day average true range of Google and Microsoft from 1999, as a fraction of price: a
    typical liquid stock's daily range (GT-3 measures their volatility the same way)."""
    out = []
    for name in ("goog", "msft"):
        b = [r for r in data.bars(name) if r["date"].year >= 1999]
        out.append(stats.quantile([_atr(b, i) for i in range(15, len(b))], 0.5))
    return sum(out) / len(out)


@functools.lru_cache(maxsize=8)
def stop_slippage(k_atr: float) -> tuple[float, float, int, str]:
    """How much worse than planned stops fill on market-wide stress days, on real prices: the five stocks
    from 1999, a stop k_atr average true ranges from each day's close, long and short, held up to 5
    days; a stop fills at its price, or at the open when the price gaps through it. For each stress day
    (the S&P 500 closing 3% or more against the side) with at least 5 stops hit, the day's average loss
    over the planned loss. Returns its 95th percentile, its worst, the number of such days, and the
    worst day."""
    market = {r["date"]: r["close"] for r in data.bars("sp500")}
    dates = sorted(market)
    move = {dates[i]: market[dates[i]] / market[dates[i - 1]] - 1 for i in range(1, len(dates))}
    days: dict[tuple, list[float]] = {}
    for name in STOCKS:
        b = [r for r in data.bars(name) if r["date"].year >= 1999]
        for i in range(15, len(b) - 6):
            dist = k_atr * _atr(b, i)
            for side in (1, -1):
                entry = b[i]["close"]
                stop = entry * (1 - side * dist)
                for j in range(i + 1, i + 6):
                    bar = b[j]
                    if (bar["low"] <= stop) if side > 0 else (bar["high"] >= stop):
                        fill = min(bar["open"], stop) if side > 0 else max(bar["open"], stop)
                        days.setdefault((bar["date"], side), []).append(side * (entry - fill) / (entry * dist))
                        break
    stress = sorted(((sum(v) / len(v), f"{d:%Y-%m-%d} ({'longs' if side > 0 else 'shorts'}, {len(v)} stops)")
                     for (d, side), v in days.items()
                     if d in move and side * move[d] <= -STRESS_DAY_MOVE and len(v) >= MIN_STOPS_PER_DAY), reverse=True)
    ratios = sorted(r for r, _ in stress)
    return (stats.quantile(ratios, anchors.STRESS_SLIPPAGE_PERCENTILE), stress[0][0], len(stress), stress[0][1])


@functools.lru_cache(maxsize=1)
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


def drawdown_sim(r: dict, room: bool, years: int = 4000, seed: str = "gt2-drawdown") -> tuple[float, float]:
    """See ``_drawdown_sim``; cached on the numbers it reads, since the mutation test (GT-10) runs it often."""
    return _drawdown_sim(r["vol_target_daily_pct"], r["max_drawdown_halt_pct"], r["max_drawdown_pct"],
                         r.get("max_position_overnight_pct", 4), r.get("drawdown_room_margin_pct", 0.0), room, years, seed)


@functools.lru_cache(maxsize=64)
def _drawdown_sim(vol_pct: float, halt: float, line: float, cap_pct: float, margin: float, room: bool,
                  years: int, seed: str) -> tuple[float, float]:
    """Share of simulated years in which equity falls past max_drawdown_pct below its peak, and share
    halted, with and without positions shrinking as the drawdown deepens. Each day: the book's
    ordinary P&L at the volatility budget and the targeted Sharpe ratio (t-distributed, 4 degrees of
    freedom), plus single-name jumps on the planned 15 overnight positions at the empirical rate, each
    an adverse move drawn from the named events; the halt flattens the book once the drawdown reaches
    max_drawdown_halt_pct. Starting drawdowns are spread from 0 to the halt, so the dangerous zone is
    visited often."""
    rng = random.Random(seed)
    vol, cap = vol_pct / 100, cap_pct / 100
    mu = 1.5 / math.sqrt(252) * vol
    worst = max(JUMPS)
    crossed = halted = 0
    for _ in range(years):
        dd0 = rng.uniform(0.0, halt) / 100
        equity, peak = 1.0 - dd0, 1.0
        for _ in range(252):
            dd = (1 - equity / peak) * 100
            if dd >= halt:
                halted += 1
                break
            size = cap if not room else max(0.0, min(cap, (line - margin - dd) / 100 / worst))
            scale = size / cap
            t = rng.gauss(0, 1) / math.sqrt(sum(rng.gauss(0, 1) ** 2 for _ in range(4)) / 2)   # t, 4 d.f., unit variance
            pnl = scale * (mu + vol * t)
            for _ in range(15):
                if rng.random() < JUMP_RATE:
                    pnl -= size * rng.choice(JUMPS)
            equity *= 1 + pnl
            peak = max(peak, equity)
            if (1 - equity / peak) * 100 > line:
                crossed += 1
                break
    return crossed / years, halted / years


def capacity(r: dict, a: dict) -> tuple[int, str]:
    """How many positions of the planned kind the book can hold: the fixed count if the goal sets one,
    otherwise the tightest of the exposure and open-risk limits at the planned sizes."""
    if r.get("max_positions"):
        return int(r["max_positions"]), f"{r['max_positions']} slots"
    if "min_position_risk_pct" not in r:
        return 0, "no fixed count and no floor on the risk a position carries: the book has no bound"
    bounds = []
    size = r.get("typical_position_pct")
    if size:
        nights = a.get("typical_holding_minutes", 0) > SESSION_MINUTES and "max_overnight_gross_pct" in r
        key = "max_overnight_gross_pct" if nights else "max_gross_exposure_pct"
        if key in r:
            bounds.append((int(r[key] // size), f"{r[key]:g}% {'overnight ' if nights else ''}gross / {size:g}% each"))
    # the open-risk cap holds as many positions as the plan's risk per position allows; without a planned
    # risk, as many as the floor allows, the most favourable case, and the detail says so
    each = r.get("typical_position_risk_pct", r["min_position_risk_pct"])
    if r.get("max_open_risk_pct") and each:
        bounds.append((int(r["max_open_risk_pct"] / each + 1e-9),
                       f"{r['max_open_risk_pct']:g}% open risk / {each:g}% each"
                       + ("" if "typical_position_risk_pct" in r else " (the floor: no planned risk per position)")))
    if not bounds:
        return 0, "neither a position count nor exposure limits at a planned size bound the book"
    n, why = min(bounds)
    return n, f"at most {n} positions ({'; '.join([why] + [w for _, w in bounds if w != why])})"


def erlang_b(load: float, servers: int) -> float:
    """Share of arrivals that find every server busy (Erlang's loss formula)."""
    b = 1.0
    for k in range(1, servers + 1):
        b = load * b / (k + load * b)
    return b


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="", kind="": out.append(Check(TEST, name, ok, detail, kind))  # noqa: E731
    r, c = risk(spec), constraints(spec)
    a, costs = spec.get("activity", {}), spec.get("costs", {})
    daily = r.get("daily_loss_limit_pct")

    # 0. the owner's own limits (goal_v1.toml): the goal may be stricter, never looser
    line = r.get("max_drawdown_pct", r.get("max_drawdown_halt_pct"))
    per_owner = r.get("risk_per_position_pct", r.get("risk_per_trade_pct"))
    session = c.get("order_session", c.get("session"))
    for what, ok, detail in (
            ("holds at most 5 trading days and 7 calendar days",
             c.get("max_holding_trading_days", math.inf) <= anchors.OWNER_MAX_HOLD_TRADING_DAYS
             and c.get("max_holding_calendar_days", 0) <= anchors.OWNER_MAX_HOLD_CALENDAR_DAYS,
             f"{c.get('max_holding_trading_days', 'unspecified')} trading, {c.get('max_holding_calendar_days', 'unspecified')} calendar days"),
            ("risks at most 0.5% of equity on one position at its stop",
             per_owner is not None and per_owner <= anchors.OWNER_RISK_PER_POSITION_PCT, f"{per_owner}%"),
            ("stops for the day at a loss of at most 2%", daily is not None and daily <= anchors.OWNER_DAILY_LOSS_LIMIT_PCT,
             f"{daily}%"),
            ("never falls more than 10% below its peak", line is not None and line <= anchors.OWNER_MAX_DRAWDOWN_PCT,
             f"{line}%"),
            ("uses no borrowed money: gross exposure at most 100%",
             r.get("max_gross_exposure_pct", math.inf) <= anchors.OWNER_MAX_GROSS_PCT, f"{r.get('max_gross_exposure_pct')}%"),
            ("trades the regular session only", session == anchors.OWNER_SESSION, f"{session}"),
            ("holds no position through an earnings release",
             c.get("hold_through_earnings") is anchors.OWNER_HOLD_THROUGH_EARNINGS, f"{c.get('hold_through_earnings')}"),
            ("trades long and short", set(anchors.OWNER_DIRECTIONS) <= set(c.get("directions", [])),
             ", ".join(c.get("directions", [])))):
        add(f"the owner's limit: {what}", ok, detail, kind="external")

    # 0b. the limits in order: the daily limit, then the worst day it allows, then the halt, then the line
    #     the owner set; the margin and the largest single event fit between the halt and the line
    halt, worst_day, margin = r.get("max_drawdown_halt_pct"), r.get("max_day_loss_pct"), r.get("drawdown_room_margin_pct")
    if "max_drawdown_pct" in r and halt is not None:
        chain = [x for x in (daily, worst_day, halt, r["max_drawdown_pct"]) if x is not None]
        add("the limits are in order: daily limit < worst day < drawdown halt < drawdown line",
            all(x < y for x, y in zip(chain, chain[1:])), " < ".join(f"{x:g}%" for x in chain))
        if margin is not None:
            add("the halt leaves the margin below the drawdown line", halt + margin <= r["max_drawdown_pct"],
                f"{halt:g}% + {margin:g}% vs {r['max_drawdown_pct']:g}%")
        if "max_jump_loss_pct" in r:
            room = r["max_drawdown_pct"] - (margin or 0)
            add("the largest single event the goal allows can't cross the drawdown line from the peak",
                r["max_jump_loss_pct"] <= room, f"{r['max_jump_loss_pct']:g}% vs {room:g}%")

    # 1. stops hit together, with slippage, must fit inside the daily loss limit. A market-wide move
    #    stops out one side of the book; a goal that caps only the total must survive all of it. The
    #    open-risk caps bound this whether or not the number of positions is fixed. How much worse than
    #    planned the stops fill is measured on real stress days, at the plan's stop distance: a 1-in-20
    #    stress day for one side against the daily limit; the worst day in the data for a whipsaw
    #    against the worst-day bound
    per = r.get("risk_per_position_pct", r.get("risk_per_trade_pct"))
    count = r.get("max_positions")
    by_count = per * count if per and count else math.inf
    planned_stop = (r["typical_position_risk_pct"] / r["typical_position_pct"]
                    if r.get("typical_position_risk_pct") and r.get("typical_position_pct") else None)
    try:
        k = planned_stop / typical_atr() if planned_stop else DEFAULT_STOP_ATR
        p95, worst_slip, n_days, worst_when = stop_slippage(round(k, 2))
        basis = (f"stops {k:.2f} average true ranges away ({'the plan' if planned_stop else 'assumed'}); on {n_days} "
                 f"stress days stops filled {p95:.2f} times the planned loss at the 95th percentile and {worst_slip:.2f} "
                 f"at worst ({worst_when})")
    except Exception as e:  # noqa: BLE001
        p95 = worst_slip = STOP_SLIPPAGE_NO_DATA
        basis = f"no data ({e}): stops assumed to fill 25% worse"
    if daily and per and ("max_open_risk_per_side_pct" in r or "max_open_risk_pct" in r or count):
        if "max_open_risk_per_side_pct" in r:
            side = min(r["max_open_risk_per_side_pct"], by_count)
            worst = side * p95
            add("every stop on one side hit at once (a market-wide move) stays inside the daily loss limit",
                worst <= daily, f"{side:g}% open risk per side x {p95:.2f} = {worst:.2f}% vs {daily:g}%; {basis}",
                kind="external")
            total = min(r.get("max_open_risk_pct", 2 * side), 2 * side)
            bound = r.get("max_day_loss_pct", daily)
            whip = side * worst_slip + (total - side) * p95
            add("every stop on both sides hit in one day (a gap, then a reversal) stays inside the worst-day bound",
                whip <= bound, f"{side:g}% x {worst_slip:.2f} + {total - side:g}% x {p95:.2f} = {whip:.2f}% vs {bound:g}%",
                kind="external")
        else:
            total = min(r.get("max_open_risk_pct", by_count), by_count)
            worst = total * p95
            add("every stop hit at once stays inside the daily loss limit", worst <= daily,
                f"{total:g}% open risk x {p95:.2f} = {worst:.2f}% vs {daily:g}%; {basis}", kind="external")
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
            add("stress gaps match the price data (the test's own constants)",
                abs(long_gap - LONG_GAP[2]) < 0.001 and abs(short_gap - SHORT_GAP[2]) < 0.001,
                f"{LONG_GAP[3]}: {long_gap:+.1%}; {SHORT_GAP[3]}: {short_gap:+.1%}", kind="hygiene")
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
                    f"{jump:g}% vs {SHORT_GAP[3]} {SHORT_GAP[2]:+.1%} and {LONG_GAP[3]} {LONG_GAP[2]:+.1%}", kind="external")
                one = max(long_cap, short_cap) * jump / 100
                add("one position held overnight through the assumed jump fits inside the daily loss limit", one <= daily,
                    f"{max(long_cap, short_cap):g}% x {jump:g}% = {one:.2f}% vs {daily:g}%")
                j_in = r.get("jump_intraday_pct")
                if j_in is not None and r.get("max_position_pct"):
                    biggest = max(r["max_position_pct"], r.get("max_position_etf_pct", 0))
                    intraday = biggest * j_in / 100
                    add("one position through an intraday jump (several price bands) fits inside the daily loss limit",
                        intraday <= daily, f"{biggest:g}% x {j_in:g}% = {intraday:.2f}% vs {daily:g}%")
                if r.get("max_position_pct"):
                    halt_gap = r["max_position_pct"] * jump / 100
                    add("one stock through a news halt in the session, which reopens like an overnight gap, fits inside "
                        "the daily loss limit", halt_gap <= daily,
                        f"{r['max_position_pct']:g}% x {jump:g}% = {halt_gap:.2f}% vs {daily:g}%")
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
                # each tier's jump against an outside anchor: a market rule or a named event
                for key, floor, why in (("jump_intraday_pct", anchors.JUMP_INTRADAY_MIN_PCT,
                                         "the 10% Limit Up-Limit Down band near the open and the close"),
                                        ("jump_overnight_etf_pct", anchors.JUMP_ETF_MIN_PCT,
                                         "a 13% market fall, the level-2 circuit breaker"),
                                        ("jump_overnight_event_prone_pct", anchors.JUMP_EVENT_PRONE_MIN_PCT,
                                         "a total loss (SVB, 2023) or a doubling against a short")):
                    if key in r:
                        label = {"jump_intraday_pct": "intraday", "jump_overnight_etf_pct": "index-fund overnight",
                                 "jump_overnight_event_prone_pct": "event-prone overnight"}[key]
                        add(f"the {label} jump is at least {why}",
                            r[key] >= floor, f"{r[key]:g}% vs {floor:g}%", kind="external")
                # positions whose jump differs from an ordinary stock's: each tier's cap through its own
                # jump must fit the daily limit, as the ordinary cap does
                for kind, cap_key, jump_key in (("broad index fund", "max_overnight_etf_pct", "jump_overnight_etf_pct"),
                                                ("event-prone position", "max_overnight_event_prone_pct",
                                                 "jump_overnight_event_prone_pct")):
                    if cap_key in r or jump_key in r:
                        tier_cap, tier_jump = r.get(cap_key), r.get(jump_key)
                        ok = tier_cap is not None and tier_jump is not None and tier_cap * tier_jump / 100 <= daily
                        add(f"one {kind} held overnight through its own jump fits inside the daily loss limit", ok,
                            f"{tier_cap:g}% x {tier_jump:g}% = {tier_cap * tier_jump / 100:.2f}% vs {daily:g}%"
                            if tier_cap is not None and tier_jump is not None else "a cap or its jump is unspecified")
                # the drawdown line: the halt fires at max_drawdown_halt_pct, but a jump can land on a book
                # already near it. Unless positions shrink as the drawdown deepens, the worst jump the
                # assumptions allow, added to a drawdown just short of the halt, crosses the line
                dd, halt = r.get("max_drawdown_pct"), r.get("max_drawdown_halt_pct")
                if dd is not None and halt is not None:
                    worst = max([bound or 0.0, max(long_cap, short_cap) * jump / 100,
                                 r.get("max_overnight_industry_pct", 0) * jump / 100,
                                 r.get("max_overnight_net_pct", 0) * STRESS_MARKET_GAP,
                                 (r.get("max_position_pct") or 0) * (r.get("jump_intraday_pct") or 0) / 100])
                    margin = r.get("drawdown_room_margin_pct")
                    room = margin is not None and "vol_target_daily_pct" in r
                    with_rule, _ = drawdown_sim(r, room)
                    without, _ = drawdown_sim(r, False)
                    add("equity stays above the drawdown line in at least 99.9% of simulated years, jumps included",
                        with_rule <= anchors.DRAWDOWN_CROSS_MAX, kind="external", detail=
                        (f"crossed in {with_rule:.2%} of years{' with positions shrinking as the drawdown deepens' if room else ''}; "
                         f"{without:.2%} at full size; the worst event the jump assumptions allow at full size is {worst:.2f}%"))
                    if margin is not None:
                        gross, rt = r.get("max_gross_exposure_pct", 100), costs.get("round_trip_cost_bps", 0)
                        closing = gross * rt / 2 / 1e4 * costs.get("stress_cost_multiplier", 1)
                        add("the drawdown margin covers closing the whole book at the halt, at stressed costs", margin >= closing,
                            f"{margin:g}% vs {gross:g}% x {rt / 2:g} bps x {costs.get('stress_cost_multiplier', 1):g} = {closing:.2f}%")
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
            if "max_overnight_dollar_net_pct" in r or "max_overnight_net_pct" in r:
                dollars = r.get("max_overnight_dollar_net_pct", r.get("max_overnight_gross_pct", 100))
                bound = r.get("max_jump_loss_pct", daily)
                add("the overnight book through a 13% gap with every beta at 1 stays within the jump-loss bound",
                    dollars * STRESS_MARKET_GAP <= bound,
                    f"{dollars:g}% {'dollar net' if 'max_overnight_dollar_net_pct' in r else 'gross'} x 13% = "
                    f"{dollars * STRESS_MARKET_GAP:.2f}% vs {bound:g}%: beta-adjusted limits trust betas measured in calmer times")
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

    # 3. the planned activity must fit the book (Little's law: average open positions = trades a day x
    #    days held; Erlang's loss formula: how often a new trade finds the book full). With a fixed
    #    count the book holds that many; without one, as many as the exposure and open-risk limits allow
    #    at the planned sizes, and a full book is resolved by the rotation rule (check 10)
    plan = ("planned_risk_trades_per_week", "typical_holding_minutes")
    slots, basis = capacity(r, a)
    if all(k in a for k in plan) and slots:
        open_avg = a["planned_risk_trades_per_week"] / 5 * a["typical_holding_minutes"] / SESSION_MINUTES
        blocked = erlang_b(open_avg, slots)
        add("the planned activity fits the book (a new trade finds it full at most 10% of the time)",
            blocked <= anchors.BOOK_FULL_MAX, f"{a['planned_risk_trades_per_week']}/week held {a['typical_holding_minutes'] / SESSION_MINUTES:.1f} days "
            f"= {open_avg:.1f} open on average; {basis}: full {blocked:.1%} of the time")
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
        add("the planned activity fits the book (a new trade finds it full at most 10% of the time)", False,
            "no planned activity or holding time" if not all(k in a for k in plan) else basis)

    # 4. gross exposure from the position limits
    if r.get("max_positions") and r.get("max_position_pct") and r.get("max_gross_exposure_pct"):
        full = r["max_positions"] * r["max_position_pct"]
        add("position limits and the gross exposure limit", None,
            f"{r['max_positions']} x {r['max_position_pct']:g}% = {full:g}% vs {r['max_gross_exposure_pct']:g}%: "
            + ("the gross limit binds first" if full > r["max_gross_exposure_pct"] else "the position limits bind first"))
    elif slots:
        add("no fixed number of positions: the limits bound the book", None, basis)

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
        entry, mult = a.get("entry_min_gain_to_cost"), costs.get("stress_cost_multiplier")
        if entry is not None and mult is not None:
            add("an entry the rule admits still pays its costs at the stress level", entry >= mult,
                f"expected gain at least {entry:g} x cost vs costs raised {mult:g} x")
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

    # 10. without a fixed count, a full book needs a rule for what may take a held position's place: a
    #     switch must clear its cost at least as an entry clears its own, rotations are capped inside the
    #     planned activity, and enough of them are judged to tell whether they pay
    if not r.get("max_positions"):
        need = ("rotation_margin_to_cost", "rotation_min_hold_minutes", "max_rotations_per_day", "max_rotation_share")
        missing = [k for k in need if k not in a] + \
                  [f"G1 {k}" for k in ("rotation_gain_confidence",) if k not in rule(spec, "G1")]
        add("a full book is resolved by a stated rotation rule", not missing,
            "unspecified: " + ", ".join(missing) if missing else "")
        if not missing:
            entry = a.get("entry_min_gain_to_cost", 1)
            add("a rotation clears its switching cost at least as an entry clears its own cost",
                1 + a["rotation_margin_to_cost"] >= entry,
                f"advantage at least {1 + a['rotation_margin_to_cost']:g} x the candidate's round-trip cost vs entry at {entry:g} x")
            if "planned_risk_trades_per_week" in a:
                add("the daily rotation cap allows no more rotations a week than the planned round trips",
                    a["max_rotations_per_day"] * 5 <= a["planned_risk_trades_per_week"] and 0 < a["max_rotation_share"] <= 1,
                    f"{a['max_rotations_per_day']:g} a day x 5 vs {a['planned_risk_trades_per_week']:g} a week; "
                    f"share {a['max_rotation_share']:g}")
            if slots and all(k in a for k in plan):
                week = a["planned_risk_trades_per_week"]
                load = week / 5 * a["typical_holding_minutes"] / SESSION_MINUTES
                full = erlang_b(load, slots) * week
                cap = min(a["max_rotation_share"] * week, a["max_rotations_per_day"] * 5)
                add("rotation opportunities and the cap, within the planned round trips", None,
                    f"about {full:.1f} candidates a week meet a full book; at most {cap:g} rotations a week, "
                    f"counted inside the {week} planned round trips and so inside the cost budget")
    return out

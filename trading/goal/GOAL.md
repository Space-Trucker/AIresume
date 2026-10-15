# The goal

**Version 3, 2026-10-15.** This version was revised after the goal tests and after an independent review
of version 2 (`REPORT.md`). It awaits the owner's decisions, listed at the end. The method behind it is in
`METHOD.md`. Every number here comes from `goal.toml`, which the tests read. This document sets what
the system must achieve and how that will be judged. How it is built comes next, top-down.

## On one page

**Mission.** An autonomous system that trades liquid US stocks and ETFs, long and short, holding each
position from seconds up to five trading days. It makes money after every cost, earns a return beyond
what the market's moves and chance would give, and never breaks its risk limits. It proves this on
history it was not built on, then on a paper account, before any real money. Real money starts with a
fraction of the intended capital and grows only while the evidence holds.

| Objective | Headline key results |
|---|---|
| **O1 Edge** (achieve): money made after every cost, beyond the market, and not luck | on at least 2,400 days of history not used to build it: Deflated Sharpe Ratio ≥ 0.95 counting every variant (KR1.1), Sharpe ≥ 1.0, aiming for 1.5 (KR1.2), a profit (KR1.4), holding in both halves (KR1.9); on paper: a profit (KR1.7), the live system doing what the tested strategy does (KR1.5, KR1.6) |
| **O2 Capital protection** (maintain): every loss inside fixed limits | no order beyond a limit (KR2.1); halt at a 9% drawdown, so 10% is never reached (KR2.2, KR2.7); worst day 2.5% (KR2.3); kill switch 60 s (KR2.4); stops that work while the system is down (KR2.5) |
| **O3 Active within the horizon** (maintain): watching all session, trading when the gain pays | the universe evaluated every minute (KR3.3); every entry's expected gain at least twice its cost (KR3.1); nothing held past 5 days (KR3.2) |
| **O4 Autonomy and resilience** (maintain): runs unattended, fails safe | up 99.5% of the session (KR4.1); reconciled with the broker (KR4.2, KR4.3); safe within 60 s of a fault (KR4.4) |
| **O5 Lawful conduct** (avoid): no forbidden order | no self-trades (KR5.1); at most 10 orders per fill (KR5.2); no short without easy-to-borrow status (KR5.3) |
| **O6 Honest evidence** (maintain): results that can't fool us | every variant registered (KR6.1); an independent reviewer before every gate (KR6.2); no model judged on data it learned from (KR6.3); point-in-time history (KR6.4) |
| **O7 Accountability** (maintain): the owner sees what it did and why | a reason for every order (KR7.1); live profit and loss (KR7.2); a daily report by 17:00 (KR7.3) |
| **O8 Improve and retire** (maintain): better without self-deception | a weekly review, and every change re-proven on paper (KR8.1); a sequential live test that halves, then stops, a fading strategy (KR8.2) |

## What to expect

- **Return.** The goal aims for a net excess Sharpe ratio of 1.5 at its volatility budget of about
  3.2% a year: about 5% a year above what the market's moves explain, after costs. The minimum, a
  Sharpe of 1.0, is about 3% a year. On $100,000 that is about $3,000 to $5,000 a year.

  That ceiling is set by three of your own rules:
  - no borrowed money (gross exposure at most 100%);
  - the 2% daily loss limit;
  - a stop can't protect a position through a gap or a trading halt.

  The third means each position must be small enough that a jump costs at most 2%. Real jumps reach
  50% (Yahoo, +49.5% overnight on a takeover bid), so a position held overnight is at most 4%. A book of
  about 15 such positions moves about 3.2% a year. Decision 1 is how to aim higher.
- **What it takes.** At the planned activity, costs take about 1.3 Sharpe units a year. A strategy
  needs a gross Sharpe of about 2.8, and a signal with an information coefficient of about 0.07 per
  trade, to net the aim. That is ambitious, not implausible.
- **Odds.** On the goal's own assumptions, the chance that the program ends with a real edge trading
  real money is at most about one in seven (14%, GT-8). The most likely outcome is that no strategy
  passes research. In that case the program stops within its budget, having risked no money. If a
  strategy does pass both gates, it has a real edge with probability 85%, and one worth running with
  probability 79%. Both figures fall if real edges are smaller than assumed (63% and 40% if none is
  above a Sharpe of 1.25).
- **Time.** The stages run in sequence:

  | Stage | Duration |
  |---|---|
  | Research (G1) | at most 9 months |
  | Paper trading (G2) | 120 to 150 trading days, about 6 to 7 months |
  | Real money, first step (G3) | at least 60 trading days at 10% of the intended capital |
  | Real money, scaling | capital at most doubles every 60 trading days: at least 240 trading days, about 11 months, from the first real dollar to full capital |

  If everything passes, full capital is more than two years away. Confirming the edge with live data
  takes longer still. The live test needs one to two years of real results to tell a real edge from a
  dead one, and capital grows only while it favors the edge.
- **Money before real money.** Consolidated market data from G2 on: Alpaca's paid plan is $99 a month.
  Intraday history back to 2016, which Alpaca may already include (see the last section). The
  reviewer's costs, if the reviewer is not a person.
- **If nothing passes.** The program stops. It restarts only if you decide so, and only on data newer
  than the last research test.

## What changed from what you asked for

Each row is a value you stated in conversation (`goal_v1.toml`), the value the goal now has, and why.
Where the goal departs from what you said, the last column names the decision that settles it.

| You asked for | The goal now says | Why | Your call |
|---|---|---|---|
| holds of seconds, minutes, hours or days, up to about 5 days, never weeks | the same: any hold from seconds to 5 trading days and 7 calendar days | as you defined it | none |
| long and short | the same, with short-sale safeguards: easy to borrow, never under the Rule 201 price test, short interest at most 15% of the float and 5 days to cover, closed within 30 minutes of the next open if it loses easy-to-borrow status | a takeover can gap a short up 50% overnight; squeezes and buy-ins | none |
| whatever budget the paper account has | $100,000, the paper default; every limit a percentage of equity | as you said | none |
| at most 5 positions | at most 20 | the planned activity keeps about 15 open; the jump limit makes positions small, so the book needs many | decision 2 |
| at most 20% in one position | 10% within the session, 4% held overnight | a position must survive a jump: 20% intraday (a halt, two price bands) and 50% overnight, each costing at most 2% | decision 1 |
| lose at most 0.5% on a trade if its stop is hit | the same, for a position with all its fills together, plus 1.5% at the stops on each side and 2% in total | adding to a loser can't multiply the risk; every stop on one side hit at once stays inside the daily limit | none |
| stop for the day at -2% | the same, counted from the previous close, so an overnight gap counts | otherwise a gap leaves a fresh 2% to lose | none |
| never more than 10% below the peak | halt at 9%, so 10% is never reached | a halt at 10% would fire only after the line was crossed | none |
| no borrowed money to start | gross exposure at most 100% of equity | a short sale is borrowed stock, so "no borrowed money" can't be literal; this is the closest meaning | none |
| a kill switch | the same, plus a second path that doesn't depend on the system, drills every 20 days, and a rule for positions that can't be traded (a halted stock) | a kill switch can't sell a halted stock | none |
| regular hours only | the same: no orders outside 09:30–16:00 New York time | as you said, but it means positions can't be cut when news breaks at night | decision 8 |
| don't hold through earnings | no position through any scheduled company event (earnings, FDA dates, trial readouts, votes, lockup expiries) or corporate action other than an ordinary dividend | the same jump risk; splits and mergers also corrupt paper records | none |
| heavily traded stocks and ETFs, no penny stocks | operating companies and stock ETFs at $5 or more, $20,000,000 a day, spreads of 10 bps or less; no leveraged, inverse, volatility, commodity or crypto products | "heavily traded" and "penny" had no number; those products carry jumps the limits don't cover | none |
| realistic costs | 8 bps a round trip on average, each trade charged its own spread, slippage, fees, borrow and dividends; tested at 1.5 times | "realistic" had no number; published costs come to 6.95 bps | none |
| constant trading, only when the gain beats the cost | the whole universe evaluated every minute; a trade only when its expected gain is at least twice its cost; about 25 a week planned, 10 a week a review trigger | the activity floor never forces a trade | none |
| makes money after costs on history it wasn't tuned on | makes money, and beats the market by more than luck: Deflated Sharpe Ratio ≥ 0.95 over at least 2,400 days, counting every variant ever evaluated (never fewer than 10), in both halves of the history | a profit over one history passes the best of 10 strategies with no edge 85–100% of the time (GT-4, GT-5) | none |
| 4–8 weeks of paper trading, 300+ trades, profitable | at least 120 trading days and 300 trades, fixed in advance; profitable; and the live system must do what the tested strategy does on the same days | a strategy at the target loses money over 60 days nearly a quarter of the time, and a strategy with no edge makes money half the time over any window; paper can check the system, not prove the edge | decision 4 |
| review every week; adjust or drop strategies, never mid-day | the same (O8): every change re-proven on paper for 60 days, and a sequential live test that halves, then stops, a fading strategy | changes judged on the same history would fool you | none |
| log every decision and why; live profit and loss; a daily report | the same (O7) | | none |
| an AI model for the slower thinking, fast code for split-second calls | kept as your design wishes for the architecture stage; no model trained on data after the research window starts may shape the forecast that G1 judges | how, not what; a model trained on the past can't be tested on that past | decision 9 |
| real money starting small | at most 10% of the intended capital, at least $2,000, for at least 60 trading days, then at most doubling every 60 trading days | "small" had no size or growth rule | decision 10 |

## Scope

**In scope.** US-listed operating-company stocks and stock ETFs, long and short, during the regular
session. The system looks for trades, decides, sizes, places and exits orders, controls risk, and
keeps records and reports, without a person in the loop. A paper account comes first.

**Out of scope (non-goals).**
- Market making and latency arbitrage: competing on speed with firms that sit next to the exchange.
- Options, futures, crypto, currencies, OTC securities, and leveraged or inverse ETFs.
- Short sales of hard-to-borrow stocks.
- Orders outside the regular session, 09:30 to 16:00 New York time.
- Positions held longer than 5 trading days or 7 calendar days.
- Leverage: gross exposure above 100% of equity.
- A promised return. The goal fixes how results are judged, not what they will be.
- The system's architecture, data sources and code, decided after this goal.
- Tax optimization.

**Stakeholders.**

| Who | Needs |
|---|---|
| S1 Owner | a system that trades by itself all day; money made after costs; no real money until paper trading proves it; a daily account of what was done and why, and live profit and loss; a way to stop everything at once; strategies reviewed every week and changed only outside trading hours |
| S2 Broker (Alpaca) | orders within its margin, short-sale and rate rules; positions reconciled with its records |
| S3 Market and regulators | orderly markets; no manipulative orders; accurate records |
| S4 Independent reviewer | evidence that can be reproduced; every strategy variant tried, logged; a say before each gate |

**Your design wishes, for the architecture stage.** They say how, not what, so they are not part of the
goal. The architecture starts from them, within the goal:
- an AI model does the slower thinking, and fast code makes the split-second calls;
- the system scans the whole market all day and watches a shortlist live;
- a risk manager with fixed limits can block any trade, and nothing overrides it;
- live profit and loss is shown.

## Constraints

These follow the headings of an investment policy statement.

| Heading | Constraint |
|---|---|
| Return objective | net excess Sharpe ratio at least 1, aiming for 1.5: about 3% a year, aiming for 5%, at the volatility budget; and a net profit, not only a return beyond the market |
| Risk objective | no day loses more than 2.5% (2% by rule, plus gaps and slippage); no single jump event more than 4%; equity never 10% below its peak (halt at 9%) |
| Horizon | a position closes within 5 trading days and 7 calendar days; no minimum, so exits can be immediate |
| Planned edge horizon | the plan expects the profit from holds of 150 minutes (2.5 hours) or more; shorter holds are allowed (decision 3) |
| Direction | long and short; shorts as in the change table above |
| Universe | US-listed operating-company common stocks (not ADRs, SPACs, closed-end funds, units, rights or warrants) and ETFs registered under the Investment Company Act that hold listed stocks. Each priced at least **$5**, with a 20-day median daily dollar volume of at least **$20,000,000** and a 20-day median quoted spread of at most **10** bps. Leveraged and inverse ETFs, commodity pools, crypto trusts, volatility-linked products and ETNs are excluded |
| Liquidity | one position at most **0.02**% of its stock's 20-day median daily dollar volume; one order at most **10**% of the volume expected while it works |
| Session | orders only in the regular session; positions may be held overnight within the overnight limits |
| Events | no position held through a scheduled company event (earnings, FDA action dates, trial readouts, shareholder votes, lockup expiries), or through the ex-date or effective date of any corporate action other than an ordinary cash dividend; no short held over an ex-date of a distribution of **0.5**% of the price or more |
| Account | the paper account's default equity, **$100,000** (confirmed on day one). Every limit is a percentage of equity, but liquidity limits are in dollars, so capacity grows only with the universe's volume |
| Legal and regulatory | a short only with a current easy-to-borrow status, which is a locate, re-checked for every held short each day; never a short under the Rule 201 short-sale price test; no spoofing, layering, wash trades or marking the close. Alpaca dropped the pattern-day-trader rule on 2026-06-04 and applies FINRA's intraday margin rule; at 100% gross the account stays far from any margin call. Short sales need at least **$2,000** of equity |
| Taxes | out of scope while on paper; confirmed by the owner before G3 |
| Unique | a paper account first; the broker is Alpaca; no person in the loop during the session |

## Risk limits

Each limit resolves an obstacle in the goal tree below.

| Limit | Value | Why |
|---|---|---|
| Loss at the stop, one position, all fills together | **0.5**% | adding to a loser can't multiply the risk of one name (GT-6, "averaging down") |
| Every share held covered by a stop for its quantity, from the moment it is bought or sold short | required | a strategy without stops looks perfect until its one bad day (GT-6, "selling tails") |
| Sum of losses at the stops, all longs; the same for all shorts | **1.5**% each side | a market-wide move stops out one side at once; filling 25% worse, it costs 1.88%, inside the daily limit (GT-2) |
| Sum of losses at the stops, every position | **2**% | a whipsaw that stops out both sides in one day, filling 25% worse, costs 2.5%, the worst-day bound (GT-2) |
| Open positions | at most **20** | the plan keeps about 15 open; with 20 slots a new trade finds them all full 4.6% of the time (GT-2) |
| One position's value, within the session | at most **10**% | a jump of **20**% within the session (a news halt, or two 10% price bands) costs 2%, the daily limit (GT-2) |
| One position held overnight, long or short | at most **4**% | a jump of **50**% overnight costs 2%. That covers Yahoo's +49.5% takeover gap (2008) and NVIDIA's -28.0% warning gap (2008) (GT-2) |
| Any single jump event, one name or one industry | at most **4**% | a total loss of one overnight position (SVB, halted and delisted in 2023) costs 4%, inside the drawdown halt (GT-2, KR2.8) |
| Held overnight in one industry, long plus short | at most **8**% | a 50% jump across an industry (US regional banks, 13 March 2023) costs 4% (GT-2) |
| All positions held overnight, gross | at most **75**% | the planned book, about 60%, fits with room (GT-2) |
| Held overnight, beta-adjusted net (long minus short) | at most **15**% | a 13% market-wide gap costs 1.95%. Circuit breakers pause trading but don't bound an overnight gap, so the stress is the level-2 breaker, not the 7% level-1 pause (GT-2) |
| Gross exposure, long plus short, at every moment | at most **100**% | no leverage |
| Daily loss, from the previous session's closing equity | **2**%: flat, and no new entries until the next session | a gap counts against it |
| Worst day, gaps within the jump assumptions and slippage while closing included | **2.5**% | KR2.3 |
| Drawdown from the highest close | halt at **9**%: flat until the owner decides; equity never **10**% below its peak | the halt leaves room to close before the 10% line (KR2.2, KR2.7) |
| Volatility that sizing aims for | **0.2**% of equity a day, about 3.2% a year, measured on **5**-day P&L | what the planned book produces (GT-2). Measured over 5 days so that trending P&L counts in full (GT-4). Realized volatility stays within **1.5** times it (KR2.6) |

A position that can't be traded at the moment is **trapped**: its stock is halted or paused, no session
is open, or the broker is unreachable. It gets an exit order at the first chance, and the owner is
alerted. After a market-wide trading halt, gross exposure is cut to the overnight limits as soon as
trading resumes, before any new entry. The **safe state** is: no new orders, open entry orders
cancelled, every position keeping a stop that works without the system, and the owner alerted.

## How losses and limits are measured

- **Equity of record.** The paper or live account revalued with the conservative fill model and
  corrected for any corporate action the broker's paper account did not apply, computed every minute.
- **Marks.** Positions are marked at the consolidated mid-price. A quote older than 5 seconds keeps its
  last valid mid. A halted name is marked at its last trade and flagged.
- **Daily loss.** Counted from the previous session's closing equity.
- **Drawdown.** Counted from the highest close of the equity of record.
- **Overnight limits.** Measured **15** minutes before the close: 15:45, or 12:45 on early-close days.
- **Breaches.**
  - An order that would exceed a limit is a breach (KR2.1).
  - A limit exceeded by price moves alone must be back within it inside **15** minutes, or it counts as a
    breach.

## Costs and fills

Every simulated and paper trade is charged from the mid-price at the decision time:
- a market order pays the half-spread plus **1.5** bps of slippage;
- a limit order pays the distance from that mid to its limit;
- sales pay the SEC fee ($20.60 per $1 million) and FINRA's fee ($0.000195 per share, capped at $9.79);
- a short held overnight pays the broker's borrow fee (zero today for easy-to-borrow names);
- dividends are credited on longs and charged on shorts at the ex-date.

In G1, shorts are allowed only in names that a stated historical proxy shows as borrowable at the time,
and they are charged a borrow cost of **0.5**% a year.

The planning average is **8** bps a round trip, above the 6.95 bps that published spreads and fees add
up to (GT-3). For stress, every cost is raised by half (×**1.5**). At the planned activity, costs take
about 1.3 Sharpe units. Doubling them would leave the targeted strategy a Sharpe of about 0.2, so G1
would reject the very strategy the goal aims for (GT-3). The live cost check (KR1.8) covers the rest.

Fills are judged conservatively:
- a limit order fills only when the price trades through its limit;
- a market order fills at the far side of the quote at the decision time, plus slippage.

Paper accounts fill more generously than this, so paper results are revalued with this model. At the
liquidity limit, market impact by the square-root law is 1.2 to 2.4 bps a side, about the 1.5 bps charged
(GT-3).

## Activity: what "constant trading" means

The system evaluates the whole eligible universe every minute of the regular session. It opens a
position only when the expected gain is at least **2** times its expected cost. The activity floor
never overrides that rule.

The plan is about **25** risk-bearing round trips a week, held about **1,170** minutes (three trading
days), at about **4**% of equity each:
- about 15 positions open on average;
- about 60% gross exposure, most of it held overnight;
- costs of about 4.2% of equity a year.

Costs are budgeted at no more than **4.5**% of equity a year, just above the plan, because a strategy
that trades much more would fail the cost stress (KR1.3) even at the target. Fewer than **10**
risk-bearing trades a week (each risking at least **0.1**% of equity) over 4 weeks triggers a review,
never a forced trade.

**The planned edge horizon is a finding, not a limit.** On real prices a stock moves about 19 bps in 5
minutes and 168 bps in a day, and a round trip costs about 8 bps. A signal's information coefficient
(IC) is the correlation between its forecasts and what follows. A common rule of thumb, attributed to
Grinold and Kahn, rates 0.05 good and 0.10 great; MSCI Barra calls 0.10 "very good". Rates above 0.15
are rarely sustained. The IC needed:

| Hold | IC needed just to pay costs | IC needed to reach the aim, at the planned activity |
|---|---|---|
| 5 minutes | 0.53 | |
| 2.5 hours | 0.096 | |
| 3 days | 0.03 | 0.074 |

So the plan expects the profit from holds of **150** minutes or more. Shorter holds remain allowed, and
G1 judges any strategy on its net results (decision 3).

## Objectives and key results

**Return objective.** The annualized net excess Sharpe ratio must be at least **1** (about **3**% a year
at the volatility budget), aiming for **1.5** (about **5**% a year), and the account must also make
money. "Excess" removes what the market's moves explain. Start from the net daily return: it includes
dividends and borrow fees, but not interest on cash or on short proceeds. For each position, subtract
its weight times its 252-day beta to SPY (as of the previous close) times SPY's total return over the
same interval the position was held. Overnight and intraday are counted separately, so a tilt toward
the market's overnight drift doesn't count as skill. No risk-free rate is subtracted.

KPP marks a key result whose failure stops the program until the owner decides.

| KR | Statement | Threshold | Window | Data | Method | Gate |
|---|---|---|---|---|---|---|
| KR1.1 (KPP) | the out-of-sample net excess return has a Deflated Sharpe Ratio of at least 0.95, counting every variant tried | ≥ 0.95 | ≥ 2,400 trading days of walk-forward out-of-sample history | historical consolidated bars and quotes; trial log | analysis | G1 |
| KR1.2 (KPP) | the out-of-sample annualized net excess Sharpe ratio is at least 1.0 (aim 1.5) | ≥ 1.0 | the G1 history | historical bars and quotes | analysis | G1 |
| KR1.3 | with every cost 50% higher, the net excess Sharpe ratio stays at or above 0.5 | ≥ 0.5 | the G1 history | historical bars and quotes | analysis | G1 |
| KR1.4 (KPP) | the out-of-sample history makes money after every cost | > 0 | the G1 history | historical bars and quotes | analysis | G1 |
| KR1.5 (KPP) | paper results track a rerun of the frozen G1 strategy on the same days: the mean daily gap is not significantly worse than 0.3 Sharpe units a year (one-sided, 5%) | ≥ −0.3 | the paper period | paper fills revalued conservatively; the frozen G1 code rerun on each paper day's data | analysis | G2 |
| KR1.6 (KPP) | at least 95% of the rerun's round trips are made on paper too, in the same stock and direction | ≥ 95% | the paper period | paper and rerun trade logs | analysis | G2 |
| KR1.7 (KPP) | the paper account makes money after every cost, and its net excess return is above zero, over the whole paper period | > 0 | at least 120 trading days and 300 risk-bearing round trips, fixed in advance | paper fills, revalued conservatively | analysis | G2 |
| KR1.8 (KPP) | live costs are not significantly above the cost model: the lower one-sided 95% bound of live minus modeled cost is at most zero | ≤ 0 bps | ≥ 300 live round trips | live fills and decision-time quotes | analysis | G3 |
| KR1.9 | the edge holds across the history: Sharpe at least 0.25 in each chronological half, and above zero in both the calmer and the more turbulent half of the days (split at the median VIX) | ≥ 0.25 | the G1 history | historical bars and quotes; the VIX | analysis | G1 |
| KR2.1 (KPP) | no order is sent that would break a limit in the risk section | 0 | every paper and live day | order, fill and position logs | inspection | G2 |
| KR2.2 (KPP) | when the equity of record falls 9% below its highest close, trading halts within 60 seconds | ≤ 60 s | every occurrence, and a drill before G2 ends | equity of record; halt log | demonstration | G2 |
| KR2.3 | no day loses more than 2.5% of the previous close's equity, except through a jump beyond the jump assumptions (KR2.8 bounds those) | ≤ 2.5% | every paper and live day | equity of record | analysis | G2 |
| KR2.4 (KPP) | the kill switch cancels every order and closes every tradable position within 60 seconds; a trapped position gets its exit order within 60 seconds of becoming tradable; the owner is alerted within 60 seconds | ≤ 60 s | a drill every 20 trading days on paper, and one before G3 | broker records | demonstration | G2 |
| KR2.5 (KPP) | every share held is covered by a stop for its quantity, partial fills included, and the stop works while the system is stopped or disconnected | 0 uncovered | a drill every 20 trading days on paper, and one before G3 | broker records | demonstration | G2 |
| KR2.6 | realized volatility (5-day P&L, scaled to a day) stays within 1.5 times the budget | ≤ 0.3% a day | every rolling 60 trading days | equity of record | analysis | G2 |
| KR2.7 | over the paper period, equity stays less than 10% below its peak | < 10% | the paper period | equity of record | analysis | G2 |
| KR2.8 | no single jump event, in one name or one industry, loses more than 4% of equity | ≤ 4% | every paper and live day | equity of record; event log | analysis | G2 |
| KR3.1 | every entry's recorded expected gain is at least twice its recorded expected cost | 0 below | every entry | order log | inspection | G2 |
| KR3.2 | every position is closed within 5 trading days and 7 calendar days, unless trapped, which is reported | 0 late | every day | position logs | inspection | G2 |
| KR3.3 | the eligible universe is evaluated in at least 99% of session minutes, on data under 5 seconds old | ≥ 99% | every day | evaluation log | analysis | G2 |
| KR3.4 | paper trading reaches 300 risk-bearing round trips within 150 trading days | ≤ 150 days | the paper period | fill logs | analysis | G2 |
| KR4.1 | running, connected and able to trade in at least 99.5% of session minutes | ≥ 99.5% | each month | health and connection logs | analysis | G2 |
| KR4.2 | after any restart, positions and open orders match the broker within 60 seconds | ≤ 60 s | every restart | broker records against the system's | test | G2 |
| KR4.3 | at every close, positions, orders and cash match the broker's | 0 differences | every close | broker records against the system's | inspection | G2 |
| KR4.4 | within 60 seconds of a lost connection, data older than 30 seconds, or a failed limit check, the system is in the safe state and the owner is alerted | ≤ 60 s | every fault, and a monthly drill | event and alert logs | demonstration | G2 |
| KR5.1 (KPP) | no order trades against the system's own orders | 0 | each day | order and fill logs | inspection | G2 |
| KR5.2 (KPP) | orders sent per fill stay at 10 or fewer | ≤ 10 | each day | order and fill logs | inspection | G2 |
| KR5.3 (KPP) | no short sale without a current easy-to-borrow status | 0 | every short | order log and broker asset status | inspection | G2 |
| KR6.1 (KPP) | every variant registered before it is tested, and G1 counts every variant ever evaluated on its history, never fewer than 10. A variant is any run on the G1 history whose results anyone sees and that differs from earlier runs in its program logic, data, features, parameters or their ranges, universe, cost, fill or borrow model, walk-forward schedule or excess method, re-runs after bug fixes included. Paper days used to diagnose a failed G2 become part of the history for every later variant | 0 missing | the whole program | a trial log the research system writes itself: append-only, hashed, timestamped outside the author's control | inspection | G1 |
| KR6.2 (KPP) | an independent reviewer challenges the evidence before each gate; every finding resolved | 0 unresolved | before G1, G2 and G3 | review records | inspection | G1, G2, G3 |
| KR6.3 (KPP) | no model trained on data after the start of the G1 window, including a pre-trained language model, shapes G1's return forecast; such a model may serve monitoring, operations and explanation | 0 | the G1 history | trial log; each model's documented cutoff | inspection | G1 |
| KR6.4 (KPP) | the G1 history is point-in-time and the simulation obeys the goal. Every stock that met the universe limits on each date is included, delisted ones with their delisting returns, and every input is as known at each decision. The borrow proxy is registered with the variant. Every simulated order stays within every limit, event blackout and short-sale rule. With every input lagged one more bar, the net Sharpe keeps at least half its value and rises no more than 10%. A run that breaks one is void | 0 | the G1 history | simulation order log; membership and delisting records; the lag audit | inspection | G1 |
| KR7.1 | every order records its strategy version, signal, expected gain, expected cost and risk when sent | 0 missing | every order | order log | inspection | G2 |
| KR7.2 | the owner can see profit and loss and open positions, no more than 60 seconds old, at any moment of the session | ≤ 60 s | every session, checked monthly | the owner's view against broker records | demonstration | G2 |
| KR7.3 | a daily report reaches the owner by 17:00 New York time | 0 missed | every trading day | delivery log | inspection | G2 |
| KR8.1 | strategies reviewed every 5 trading days; every change registered and run 60 trading days on paper before it replaces the live version | 0 missed | from G2 on | review, trial and deployment records | inspection | G3 |
| KR8.2 (KPP) | from the first live day, a sequential test weighs "no edge" against "the targeted edge" and is acted on at every monthly look: stop when the evidence for no edge reaches 12 to 1, halve capital at 3 to 1, grow capital only while the evidence favors the edge | 0 not run or not acted on | from G3 on | live fills; the test's log | inspection | G3 |

## Goal tree and obstacles

The top goal holds only if all eight objectives hold. Each objective asks one question, and its key
results answer it:

| Objective | Question |
|---|---|
| O1 | does the strategy, judged on data it was not built on, earn more than its costs and more than the market's moves would give, by more than chance explains? |
| O2 | do the limits hold on every order and every day, through gaps, outages and the kill switch? |
| O3 | does the system watch the universe all session, trade when and only when the entry rule says so, and close within the holding limits? |
| O4 | does it run without a person, agree with the broker, and fail into the safe state? |
| O5 | does any order break a market rule, the broker's rules, or the system's own message limits? |
| O6 | is every variant counted, every result reproducible, and every gate challenged by someone independent? |
| O7 | can the owner see, at any moment and afterwards, what the system did and why? |
| O8 | does the system get better without fooling itself, and stop a strategy whose edge has gone? |

```mermaid
flowchart TD
  G["Trade autonomously, make money beyond the market and luck, never break a limit"]
  G --> O1["O1 Edge (achieve)"]
  G --> O2["O2 Capital protection (maintain)"]
  G --> O3["O3 Active within the horizon (maintain)"]
  G --> O4["O4 Autonomy and resilience (maintain)"]
  G --> O5["O5 Lawful conduct (avoid)"]
  G --> O6["O6 Honest evidence (maintain)"]
  G --> O7["O7 Accountability (maintain)"]
  G --> O8["O8 Improve and retire (maintain)"]
  O1 --> K1["KR1.1–KR1.9: DSR, Sharpe, stress, profit, fidelity, live cost, stability"]
  O2 --> K2["KR2.1–KR2.8: no breach, halt, worst day, kill switch, stops, volatility, drawdown, jumps"]
  O3 --> K3["KR3.1–KR3.4: entry rule, holding limit, watching, trade count"]
  O4 --> K4["KR4.1–KR4.4: uptime, reconciliation, safe state"]
  O5 --> K5["KR5.1–KR5.3: no self-trades, message rate, borrow"]
  O6 --> K6["KR6.1–KR6.4: registration, review, model cutoff, point-in-time"]
  O7 --> K7["KR7.1–KR7.3: reasons, live P&L, daily report"]
  O8 --> K8["KR8.1–KR8.2: weekly review, sequential live test"]
```

| Goal | Obstacle (how it could fail) | Resolution |
|---|---|---|
| O1 | no real edge exists at these horizons and costs | research budget and stop rule; the planned edge horizon |
| O1 | the backtest flatters: overfitting, look-ahead, survivorship, the best of many variants | every run logged by the research system and counted (KR6.1); Deflated Sharpe Ratio (KR1.1); point-in-time history and a lag audit on every candidate (KR6.4); conservative fills; a Sharpe above 4 audited for leaks |
| O1 | a model has already seen the history it is tested on | no model trained past the window's start shapes G1's forecast (KR6.3) |
| O1 | costs higher than modeled | per-trade costs from quotes; stress at ×1.5 (KR1.3); live cost check (KR1.8); the liquidity limit |
| O1 | the edge decays or the regime changes | ≥ 2,400 days out of sample, holding in both halves and in calm and turbulent days (KR1.9); the sequential live test (KR8.2). The history from 2016 has no 2008-like crisis; the jump and drawdown limits are the protection there |
| O1 | the live system doesn't do what the tested strategy does | the paired fidelity test (KR1.5, KR1.6) |
| O1 | profit from riding the market, not from skill | excess return as the measure, and a profit required as well |
| O1 | short-side profit that can't be captured: dividends on shorts, the Rule 201 test, names not borrowable then | dividends charged; no short under Rule 201; a historical borrowability proxy and borrow cost in G1 |
| O2 | a gap, halt or takeover jumps past the stop | positions sized for jumps (4% overnight, 10% intraday); industry and net limits; the jump-loss bound (KR2.8) |
| O2 | a position can't be closed: halted, no session, broker down | the trapped rule; exits at the first chance; a second kill path (C6) |
| O2 | a runaway loop sends orders without limit | rate limits, duplicate blocking, per-name and daily throttles, kill switch (C3, C6, C13) |
| O2 | the system's view of its positions drifts from the broker's | continuous reconciliation; unknown order states never resent blind (C5) |
| O2 | a split or merger corrupts paper equity and fires a false halt | no position through corporate actions; the equity of record corrected |
| O3 | overtrading eats the edge | entry only at twice the cost (KR3.1); the cost budget |
| O3 | too few trades for evidence | 300 trades within 150 days (KR3.4); a review below 10 a week |
| O4 | data feed stale, connection lost, process restarts | freshness in KR3.3; reconciliation (KR4.2, KR4.3); safe state (KR4.4) |
| O5 | an order that looks manipulative, or a short without a borrow | C9 surveillance; KR5.1; KR5.3; the Rule 201 check |
| O6 | results reported selectively, or hindsight changes to the rules | registration with outside timestamps; gates fixed before the data; independent challenge |
| O8 | changes judged on history that is already used up | every change runs 60 days on paper first (KR8.1) |

## Gates

| Gate | Question | Passes when |
|---|---|---|
| **G1 Research on history** | is there an edge, net of costs, on history not used to find it? | ≥ 2,400 trading days of walk-forward out-of-sample results, point-in-time, with a clean lag audit (KR6.4). DSR ≥ 0.95, counting every variant ever evaluated and never fewer than 10 (KR1.1, KR6.1). Sharpe ≥ 1.0 (KR1.2), and ≥ 0.25 in each half (KR1.9). Sharpe ≥ 0.5 at 1.5 times the costs (KR1.3). A profit (KR1.4). Significance counts autocorrelation (Newey-West, 5 lags). A Sharpe above 4 is audited for look-ahead leaks before it counts. Conservative fills. No model trained past the window's start shapes the forecast (KR6.3). Review resolved (KR6.2) |
| **G2 Paper trading** | does the live system do what the tested strategy does, unattended and within every limit, and does it make money on paper? It can't prove the edge: 120 days are too few | at least 120 trading days and 300 risk-bearing round trips, fixed in advance, the trades within 150 days (KR3.4). Paper tracks a rerun of the frozen strategy (KR1.5) and makes 95% of its trades (KR1.6). A profit, and excess return above zero, over the whole period (KR1.7). Every O2–O7 key result met. Review resolved (KR6.2) |
| **G3 Real money, small first** | do real fills match the cost model, with money at risk? | the owner decides. It starts with at most 10% of the intended capital, at least $2,000, for at least 60 trading days. Before it starts, the owner confirms the tax treatment and that whole-share shorts keep to the percentage limits. Capital at most doubles every 60 trading days, and only while the live test allows growth (KR8.2), every G2 criterion holds, live costs match the model (KR1.8), and no liquidity limit binds on more than 5% of trades. Review resolved (KR6.2) |

**Kill criteria.**
- The program has at most **4** research cycles of at most **3** registered variants each, within a
  total of **10** variants on one data history, and at most **9** months.
- If no strategy passes G1 within that budget, the program stops instead of trading anyway. It
  restarts only if the owner decides, and only on data after the last G1 test.
- A 9% drawdown halts trading until the owner decides.

**Running live (O8).**
- The owner reviews strategies every **5** trading days.
- A changed strategy runs **60** trading days on paper before it replaces the live one.
- From the first live day, a sequential test weighs "no edge" against "the targeted edge" (a Sharpe of
  **1.5**) on the live excess returns. It is a Wald-type test, its log-likelihood ratio capped at **2.89**
  (ln 18), so a long good run can't hide a later decay. Every **21** trading days it
  decides:
  - at or below **-2.5** (12 to 1 for "no edge"), the strategy stops and returns to research;
  - at or below **-1.1** (3 to 1), capital halves;
  - capital may grow only at or above **0**.

  GT-4 checks its design. It should stop a strategy with the targeted edge by mistake within 3 years at
  most 12% of the time. It should halve a strategy whose edge is gone within a year at least half the
  time, and stop it within 3 years at least 65% of the time. Fewer false stops would mean slower
  detection; halving within the first year, and the drawdown halt behind it, are the faster
  protections.

## Controls

These cover what SEC Rule 15c3-5, FINRA Notice 15-09, EU RTS 6, MiFID II's record and clock rules, Fed
SR 11-7 and the Knight Capital order expect of an algorithmic trader (GT-7). One deviation is stated:
the alert time (C7).

| Control | Statement |
|---|---|
| C1 | Before every order, limits are computed on the positions the broker has confirmed plus every open or unconfirmed order as if filled. The checked limits are buying power, gross, overnight and industry exposure, open risk, and the daily loss limit: new open risk is at most the day's remaining loss budget divided by 1.25. An order that would exceed one is blocked. |
| C2 | A risk-increasing order must meet all of these, or it is not sent: <ul><li>a limit order at most **1**% through the consolidated best bid or offer;</li><li>a quote at most 5 seconds old, neither crossed nor locked;</li><li>a spread at most **3** times the name's median;</li><li>within the position, liquidity and participation limits.</li></ul> A risk-reducing order is never blocked by a price, universe or event check, and is limited only to the exchange's price band. |
| C3 | An order identical to one sent in the last **5** seconds is blocked. The system sends at most **2** orders a second and **120** a minute, and keeps **30**% of the broker's request budget for exits and reconciliation. |
| C4 | Before every session and every risk-increasing order, the system checks the event and corporate-action calendar, the short-sale rules (easy-to-borrow status, the Rule 201 test, the short-interest limits) and the universe limits. |
| C5 | Every fill is recorded as it arrives. Positions, orders and cash are reconciled with the broker:<ul><li>continuously, from its trade-update stream;</li><li>by a poll at least every 60 seconds;</li><li>after any disconnect and every restart;</li><li>at every close.</li></ul> A mismatch, an order of unknown state, or an order the system did not send blocks risk-increasing orders and alerts the owner. An order of unknown state is never sent again blind. Records are kept at least 5 years, append-only and hash-chained, with a copy off the host. |
| C6 | A kill switch cancels all orders and closes all positions. The owner can use it at any time, and the drawdown halt triggers it automatically. A second way to do the same does not depend on the trading process (the broker's own controls) and is drilled. The broker account's margin multiplier is set to the lowest value that allows the planned shorts, so the broker itself caps a runaway. Only one instance of the system trades at a time. Every order carries the strategy version that sent it. |
| C7 | Real-time monitoring alerts the owner within **60** seconds of: <ul><li>a blocked or rejected order;</li><li>a data gap longer than **30** seconds;</li><li>a lost connection;</li><li>a reconciliation mismatch;</li><li>a limit reaching **0.8** of its threshold.</li></ul> An alert not acknowledged within **15** minutes stops new entries; within **60** minutes, it closes every position. This relaxes RTS 6 Article 16 (alerts within 5 seconds, a person monitoring) because the owner wants an unattended system. |
| C8 | Changes are versioned, registered, tested on history and then on paper for 60 trading days before use. They are deployed only outside the session and can be rolled back; nothing changes during a trading day. Before each open, every component is checked to run the approved version. A written runbook covers every incident the alerts name. |
| C9 | Orders never cross the system's own orders, are never sent without intent to trade, and are not used to move the closing price; surveillance checks the logs daily. |
| C10 | The obstacle table above is reviewed monthly, and the controls' effectiveness is reviewed in writing every quarter. |
| C11 | Broker credentials are kept outside the code and repository. Paper and live keys are separate, and only the trading process can read them. Keys are rotated every 90 days and at once on any suspicion. The broker account uses multi-factor sign-in. An order the system did not send triggers the kill switch. |
| C12 | An independent reviewer challenges the evidence before each gate (effective challenge), and the sequential live test weighs the live results every month (KR8.2). |
| C13 | At most **4** round trips in one name a day, and at most **300**% of equity traded in a day. Reaching either stops new entries until the owner allows them again. |
| C14 | The host clock stays within **50** ms of UTC and is monitored; beyond it, no risk-increasing orders. |

## How results are judged (evaluation assumptions)

These numbers set how sure the gates must be. GT-4 and GT-8 check the gates against them:
- a new candidate strategy has a 5% chance of a real net edge before testing. A real edge is equally
  likely to be any Sharpe up to 2; GT-8 also shows edges no larger than 1.25;
- a strategy that passes G1 and G2 should have a real edge with probability at least 80%, and be worth
  running (Sharpe 1 or more) with probability at least 70%;
- G1 should pass the best of the variant budget, when none has an edge, at most 1% of the time;
- G2 passes a strategy with no edge about half the time: over 120 days, half of them make money by
  luck. So G1 carries the evidence, and G2 checks the system;
- a strategy with no edge should reach real money at most 0.5% of the time;
- each gate should pass the targeted edge at least 80% of the time;
- G2's fidelity test should pass an honest implementation at least 95% of the time and catch one that
  loses a Sharpe unit to execution at least 80% of the time. This assumes paper and the rerun differ
  by 15% of the strategy's daily volatility;
- the drawdown halt should stop a strategy that has the targeted edge in at most 10% of years;
- published effects count at most at 42% of their reported size, what remains after publication
  (McLean and Pontiff).

## Decisions for the owner

Each can be answered yes or no. The goal holds as written if the answer is yes; the default is in
brackets.

1. **The return it aims for.** About 3% a year at the minimum and 5% at the aim, set by sizing every
   position for a jump. Accept [yes]. If not: allow overnight positions of 8% and accept that one bad
   night can cost 4%, which doubles the aim to about 10% a year. That is a change to your 2% daily
   limit.
2. **Positions: 20 instead of 5.** With jump-safe sizes, 5 positions would hold about 20% of the account.
   Accept [yes].
3. **The planned edge horizon.** The plan expects profit from holds of 2.5 hours or more, because the
   cost arithmetic rules out minute-level profits at 8 bps. Holds remain open from seconds. Accept the
   planning basis [yes], or ask for a study of a cheaper universe.
4. **Paper trading takes at least 120 trading days (about 6 months), not 4 to 8 weeks.** Paper can check
   that the live system does what was tested, but it can't prove the edge in any short window. Accept
   [yes].
5. **The research budget.** At most 10 variants and 9 months. Every run on the history counts as a
   variant, and a stop is final for that history. Accept [yes].
6. **The independent reviewer.** Who challenges the evidence before each gate, and who rules on the
   findings. [An AI reviewer that sees only the evidence, as in this review; you rule on the findings.]
7. **Alerts when you are away.** An alert unacknowledged for 15 minutes stops new entries; at 60 minutes
   the system closes everything. Accept [yes].
8. **Extended hours.** No orders outside 09:30–16:00, even to cut risk when news breaks at night
   [yes, as you said]. If not: allow risk-reducing limit orders in the extended sessions, within a
   collar.
9. **The AI model.** A model trained on recent data, such as a current language model, has seen the
   history G1 would test it on. So it may not shape the forecast G1 judges; it can still help with
   monitoring, operations and explanations. Proving a model-driven forecast forward, on paper, would
   take years, not months. Accept [yes].
10. **Real money and taxes.** Before G3: the intended capital (G3 starts at 10% of it, at least $2,000,
    and enough for whole-share shorts), and the tax treatment of the account. At larger capital, the
    liquidity limit narrows the universe. [Decide before G3.]

## Before the API key can be used

These are actions, not decisions:
- **Network.** This environment blocks Alpaca's hosts (`api.alpaca.markets`,
  `paper-api.alpaca.markets`, `data.alpaca.markets`, `stream.data.alpaca.markets`). Add them to the
  environment's allowed domains.
- **Market data.** The free plan carries one exchange's quotes (IEX, about 2.5% of volume) and 30 symbols
  at a time. The goal needs consolidated quotes for the whole universe every minute (KR3.3) and real
  spreads for costs from G2 on. That means Alpaca's Algo Trader Plus plan ($99 a month) or another
  consolidated source. Confirm that a paper-only account can use it.
- **History.** G1 needs 2,400 trading days out of sample after an initial training window. That means
  consolidated intraday history from the start of 2016 or earlier; Alpaca's appears to start on
  2016-01-01, about 2,700 trading days to now. That leaves about 15 months for the first training
  window, no further holdout, and no 2008-like crisis in the data. Confirm the start date, or plan for a
  longer paid history. The history must also include delisted stocks (KR6.4).
- **The key itself.** A paper key only, stored outside the repository (C11).

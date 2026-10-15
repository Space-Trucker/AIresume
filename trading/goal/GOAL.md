# The goal

**Version 5, 2026-10-15.** Version 4 settled the open decisions on researched evidence
(`../reports/Trading goal decisions research.md`) and on the owner's answers: no fixed number of
positions, and 120 days of paper trading. Version 5 answers an independent review of version 4 by four
reviewers who saw only the goal: a fact check, a check against Alpaca's actual interface, a statistics
review, and an audit of the tests for circularity (`reviews/v4/`, `REPORT.md`). The last found the tests
judging the goal by its own numbers; since round 5 the tests hold their own bars, and those found five
more things to fix here: a key result that contradicted its gate, a worst-day bound real stop fills
exceed, a plan the book couldn't hold, a spread limit the cost stress didn't cover, and a live test
slower than the bar set for it before any results. The goal is now frozen: it changes only if building
or testing shows it wrong. The decisions, with what the research found, are
at the end; the owner can still overturn any of them. The method behind the goal is in `METHOD.md`. Every number here comes from `goal.toml`, which the tests read. This document sets what
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
| **O2 Capital protection** (maintain): every loss inside fixed limits | no order beyond a limit (KR2.1); halt at a 9% drawdown, so 10% is never reached (KR2.2, KR2.7); worst day 3.5% (KR2.3); kill switch 60 s (KR2.4); stops that work while the system is down (KR2.5) |
| **O3 Active within the horizon** (maintain): watching all session, trading when the gain pays | the universe evaluated every minute (KR3.3); every entry's expected gain at least twice its cost (KR3.1), and those gains not inflated (KR3.7); nothing held past 5 days (KR3.2); a better candidate replaces a held position only when the switch pays, and rotation proves it does (KR3.5, KR3.6) |
| **O4 Autonomy and resilience** (maintain): runs unattended, fails safe | up 99.5% of the session (KR4.1); reconciled with the broker (KR4.2, KR4.3); safe within 60 s of a fault (KR4.4) |
| **O5 Lawful conduct** (avoid): no forbidden order | no self-trades (KR5.1); at most 10 orders per fill (KR5.2); no short without easy-to-borrow status (KR5.3) |
| **O6 Honest evidence** (maintain): results that can't fool us | every variant registered (KR6.1); a panel of independent AI reviewers before every gate (KR6.2), tested on planted flaws (KR6.5); no model judged on data it learned from (KR6.3); point-in-time history (KR6.4) |
| **O7 Accountability** (maintain): the owner sees what it did and why | a reason for every order (KR7.1); live profit and loss (KR7.2); a daily report by 17:00 (KR7.3) |
| **O8 Improve and retire** (maintain): better without self-deception | a weekly review, and every change re-proven on paper (KR8.1); a sequential live test that halves, then stops, a fading strategy (KR8.2) |

## What to expect

- **Return.** The goal aims for a net excess Sharpe ratio of 1.5 at its volatility budget of about
  3.2% a year: about 5% a year above what the market's moves explain, after costs. The minimum, a
  Sharpe of 1.0, is about 3% a year. On $100,000 that is about $3,000 to $5,000 a year.

  The volatility budget sets that level, not the size of single positions. A budget of 0.2% a day
  keeps your 10% drawdown line far from ordinary losing streaks, and puts the 2% daily limit ten
  ordinary days away. A position held overnight stays at most 4%, because a stop can't protect it
  through a gap: real gaps reach 50% (Yahoo, +49.5% on a takeover bid), and 4% times 50% is the 2%
  daily limit. Allowing 8% would not double the return, as version 3 said. Under the open-risk,
  overnight-gross and volatility limits, the same budget would be spread over half as many names, for
  at most a quarter more return and twice the loss from one gap (decision 1). Aiming higher means a
  larger volatility budget, and with it a larger chance of reaching the drawdown line.
- **What it takes.** At the planned activity, costs take about 1.3 Sharpe units a year. A strategy
  needs a gross Sharpe of about 2.8 to net the aim: about 17 bps of gross gain on each of about 1,300
  trades a year at 4% each. That is ambitious, not implausible.
- **Fixed costs.** Consolidated market data costs $99 a month from paper trading on, $1,188 a year:
  1.2% of $100,000, about a third of the minimum target's return. Below about $40,000 of capital the data
  plan takes most of the expected return. Returns are measured without subtracting a risk-free rate, so
  if idle cash earns nothing at the broker, a cash yield above the minimum target's 3% a year beats the
  strategy. US short-term gains are taxed as ordinary income.
- **Odds.** The goal assumes 5% of ideas have a real net edge. Read per idea, with at least 15
  distinct ideas tested, the chance that the program ends with a real edge trading real money is about
  20%. Read per program, the way the outside view's base rates are measured (fewer than 1% of
  day traders are reliably profitable), it is about 1.5%. Either way, the most likely
  outcome is that no strategy passes research; the program then stops within its budget, having risked
  no money. If a strategy does pass both gates, it has a real edge with probability 87%, and
  one worth running with probability 83%, on the goal's prior over edge sizes; both fall if
  real edges are smaller than assumed (62% and 41% if none is above a Sharpe of
  1.25). At the tests' own reference, where small edges are commoner and the rate at which a strategy
  with no edge reaches real money is taken at its upper bound, they are 67% and 61%. Every one of these figures assumes the history is out of sample for the researcher. It isn't
  quite: the builder, a person or an AI model, already knows 2016 to 2026. That is why the live test
  starts on the first paper day, the first data no one has seen, and capital grows only when that
  evidence favors the edge 3 to 1.
- **Time.** The stages run in sequence:

  | Stage | Duration |
  |---|---|
  | Research (G1) | at most 12 months, in four stages of 3 months |
  | Paper trading (G2) | 120 to 250 trading days, about 6 to 12 months: it runs on until paper is shown to keep up with the tested strategy |
  | Real money, first step (G3) | at least 60 trading days at 10% of the intended capital, or at the minimum for faithful sizes if that is more (decision 10) |
  | Real money, scaling | capital at most doubles every 60 trading days: at least 240 trading days, about 11 months, from the first real dollar to full capital |

  If everything passes, full capital is more than two years away. Confirming the edge with live data
  takes longer still. The live test needs one to two years of real results to tell a real edge from a
  dead one, and capital grows only while it favors the edge.
- **Money before real money.** Consolidated market data from G2 on: Alpaca's paid plan is $99 a month.
  Intraday history back to 2016, which Alpaca may already include (see the last section). The review
  panel's model costs before each gate, and a paid human review of the G1 statistics before real money
  passes $100,000.
- **If nothing passes.** The program stops. It restarts only if you decide so, and only on data newer
  than the last research test. A fresh 2,400-day test needs 9.5 years of new data, so in practice a
  stop is final for this approach.

## What changed from what you asked for

Each row is a value you stated in conversation (`goal_v1.toml`), the value the goal now has, and why.
Where the goal departs from what you said, the last column names the decision that settles it.

| You asked for | The goal now says | Why | Your call |
|---|---|---|---|
| holds of seconds, minutes, hours or days, up to about 5 days, never weeks | the same: any hold from seconds to 5 trading days and 7 calendar days | as you defined it | none |
| long and short | the same, with short-sale safeguards: easy to borrow, never under the Rule 201 price test, short interest at most 15% of the float and 5 days to cover, closed within 30 minutes of the next open if it loses easy-to-borrow status | a takeover can gap a short up 50% overnight; squeezes and buy-ins | none |
| whatever budget the paper account has | $100,000, the paper default; every limit a percentage of equity | as you said | none |
| at most 5 positions | no fixed number: as many as the risk and exposure limits allow, about 15 open as planned. When a better candidate meets a full book, it replaces the lowest-valued position only if the switch pays after its cost | you asked for a dynamic book; a count would block good trades, and the limits already bound the risk | settled (decision 2) |
| at most 20% in one position | 4% for a stock at any moment, 10% for a broad index fund, 2% for an event-prone position; all shrinking as the drawdown deepens | a position must survive a jump at a cost of at most 2%: 50% for a stock, overnight or through a news halt in the session, which reopens like an overnight gap; 20% for a broad index fund; 100% for a biotech short or a bank under a run. Near the halt, a jump must not carry equity past the 10% line | settled (decision 1) |
| lose at most 0.5% on a trade if its stop is hit | the same, for a position with all its fills together, plus 1.5% at the stops on each side and 2% in total | adding to a loser can't multiply the risk; every stop on one side hit at once stays inside the daily limit | none |
| stop for the day at -2% | the same, counted from the previous close, so an overnight gap counts. A day can still lose up to 3.5%: stops that gap through their price fill worse, up to 1.9 times the planned loss on the worst stress day in the price data | otherwise a gap leaves a fresh 2% to lose; no limit can stop a gap | none |
| never more than 10% below the peak | halt at 9%, so 10% is never reached | a halt at 10% would fire only after the line was crossed | none |
| no borrowed money to start | gross exposure at most 100% of equity | a short sale is borrowed stock, so "no borrowed money" can't be literal; this is the closest meaning | none |
| a kill switch | the same, plus a second path that doesn't depend on the system, drills every 20 days, and a rule for positions that can't be traded (a halted stock) | a kill switch can't sell a halted stock | none |
| regular hours only | the same: no orders outside 09:30–16:00 New York time | as you said. An order after hours trades at the price the news has already set, at spreads measured at 1.4 to 4 times the session's, so little is lost | settled (decision 8) |
| don't hold through earnings | no position through any scheduled company event (earnings, FDA dates, trial readouts, votes, lockup expiries) or corporate action other than an ordinary dividend | the same jump risk; splits and mergers also corrupt paper records | none |
| heavily traded stocks and ETFs, no penny stocks | operating companies and stock ETFs at $5 or more, $20,000,000 a day, spreads of 8 bps or less; no leveraged, inverse, volatility, commodity or crypto products | "heavily traded" and "penny" had no number; those products carry jumps the limits don't cover | none |
| realistic costs | 8 bps a round trip on average, each trade charged its own spread, slippage, fees, borrow and dividends; tested at 1.5 times | "realistic" had no number; published spreads, market impact and fees come to 7.5 bps | none |
| constant trading, only when the gain beats the cost | the whole universe evaluated every minute; a trade only when its expected gain is at least twice its cost; about 25 a week planned, 10 a week a review trigger | the activity floor never forces a trade | none |
| makes money after costs on history it wasn't tuned on | makes money, and beats the market by more than luck: Deflated Sharpe Ratio ≥ 0.95 over at least 2,400 days, counting every variant ever evaluated (never fewer than 30), in both halves of the history | a profit over one history passes the best of 10 strategies with no edge 85–100% of the time (GT-4, GT-5) | none |
| 4–8 weeks of paper trading, 300+ trades, profitable | at least 120 trading days and 300 trades, fixed in advance, and up to 250 days until paper is shown to keep up with the tested strategy; profitable; and the live system must do what the tested strategy does on the same days | a strategy at the target loses money over 60 days nearly a quarter of the time, and a strategy with no edge makes money half the time over any window; paper can check the system, not prove the edge | accepted (decision 4) |
| review every week; adjust or drop strategies, never mid-day | the same (O8): every change re-proven on paper for 60 days, and a sequential live test that halves, then stops, a fading strategy | changes judged on the same history would fool you | none |
| log every decision and why; live profit and loss; a daily report | the same (O7) | | none |
| an AI model for the slower thinking, fast code for split-second calls | kept as your design wishes for the architecture stage. A model shapes the forecast G1 judges only if it was trained on data from before each decision it informs, which a current language model wasn't; its ideas count as variants | how, not what; a model that has seen the history can't be tested on it | settled (decision 9) |
| real money starting small | at most 10% of the intended capital, for at least 60 trading days, then at most doubling every 60 trading days; at least $2,500, and enough for a typical position to hold 10 shares of the universe's median-priced stock; a paid human review before $100,000 | "small" had no size or growth rule; at $2,000 a 4% position is $80, which whole shares can't match | decision 10, before G3 |
| no Fable model, of any kind | the same: no Fable model in any role, in the system or in the work that builds and reviews it | as you said | none |

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
- live profit and loss is shown;
- never a Fable model, in any role. This one binds the whole program, not only the architecture.

## Constraints

These follow the headings of an investment policy statement.

| Heading | Constraint |
|---|---|
| Return objective | net excess Sharpe ratio at least 1, aiming for 1.5: about 3% a year, aiming for 5%, at the volatility budget; and a net profit, not only a return beyond the market |
| Risk objective | no day loses more than 3.5% (2% by rule, plus gaps and stops filling worse than their price); no single jump event more than 4%; equity never 10% below its peak (halt at 9%) |
| Horizon | a position closes within 5 trading days and 7 calendar days; no minimum, so exits can be immediate |
| Planned edge horizon | the plan expects the profit from holds of 780 minutes (2 trading days) or more, held overnight: a judgment from the research, not a result of arithmetic; shorter holds are allowed (decision 3) |
| Direction | long and short; shorts as in the change table above |
| Universe | US-listed operating-company common stocks (not ADRs, SPACs, closed-end funds, units, rights or warrants) and ETFs registered under the Investment Company Act that hold listed stocks. Each priced at least **$5**, with a 20-day median daily dollar volume of at least **$20,000,000** and a 20-day median quoted spread of at most **8** bps, so a round trip in a name at the limits, with market impact and fees, stays within the stressed cost (GT-3; version 5 allowed 10 bps, which the stress did not cover). Leveraged and inverse ETFs, commodity pools, crypto trusts, volatility-linked products and ETNs are excluded |
| Liquidity | one position at most **0.02**% of its stock's 20-day median daily dollar volume; one order at most **10**% of the volume expected while it works |
| Session | orders only in the regular session; positions may be held overnight within the overnight limits |
| Events | no position held through a scheduled company event (earnings, FDA action dates, trial readouts, shareholder votes, lockup expiries), or through the ex-date or effective date of any corporate action other than an ordinary cash dividend; no short held over an ex-date of a distribution of **0.5**% of the price or more |
| Account | the paper account's default equity, **$100,000** (confirmed on day one). Every limit is a percentage of equity, but liquidity limits are in dollars, so capacity grows only with the universe's volume |
| Legal and regulatory | a short only with a current easy-to-borrow status, which is a locate, re-checked for every held short each day; never a short under the Rule 201 short-sale price test; no spoofing, layering, wash trades or marking the close. Alpaca dropped the pattern-day-trader rule on 2026-06-04 and applies FINRA's intraday margin rule; at 100% gross the account stays far from any margin call. Short sales need at least **$2,000** of equity |
| Taxes | out of scope while on paper; settled with an adviser before G3 (decision 10) |
| Unique | a paper account first; the broker is Alpaca; no person in the loop during the session; no Fable model (claude-fable-*) in any role: the system's decisions, research, the independent review, monitoring, operations, or building the system |

## Risk limits

Each limit resolves an obstacle in the goal tree below.

| Limit | Value | Why |
|---|---|---|
| Loss at the stop, one position, all fills together | at most **0.5**%, and at least **0.1**% when it opens | adding to a loser can't multiply the risk of one name (GT-6, "averaging down"). The floor bounds the book: the 2% open-risk cap holds at most 20 positions at entry. The plan's positions risk about **0.11**% each: a 4% position with its stop 2.75% away, about 1.3 average true ranges of a typical stock |
| Every share held covered by a stop at the broker for its quantity, within **2** seconds of each fill, partial fills included | required | a strategy without stops looks perfect until its one bad day (GT-6, "selling tails") |
| Sum of losses at the stops, all longs; the same for all shorts | **1.5**% each side | a market-wide move stops out one side at once. On real stress days (the S&P 500 down 3% or more against the side), stops at the plan's distance filled 1.19 times their planned loss on a 1-in-20 day: 1.78%, inside the daily limit (GT-2) |
| Sum of losses at the stops, every position | **2**% | a gap that stops out one side as badly as the worst stress day in the data (1.9 times the planned loss, 19 October 2000), then a reversal that stops the other side, costs 3.45%, inside the worst-day bound (GT-2) |
| Open positions | no fixed number; **50** open stops new entries, as a check against a malfunction | the limits bound the book: at the planned 4% size, 18 positions overnight (75% / 4%), and 18 at the plan's risk (2% / 0.11%). The plan keeps about 15 open, so a new trade finds the book full 8.6% of the time (GT-2); the rotation rule then decides (see Activity) |
| One stock, at any moment, long or short | at most **4**% | a jump of **50**% overnight costs 2%. That covers Yahoo's takeover gap (opened +49.5% in the project's data and closed +48%, 1 February 2008) and NVIDIA's warning gap (opened −28.0%, closed −30.7%, 3 July 2008) (GT-2) |
| One broad index fund, at any moment | at most **10**% | a jump of **20**% costs 2%: four of the 5% price bands within the session, or an overnight gap beyond the 13% level-2 circuit breaker, which a broad index has not had (GT-2) |
| One event-prone position, at any moment | at most **2**% | a jump of **100**% costs 2%: a biotech short can double on a regulatory decision or a takeover, and a bank under a run can be wiped out (SVB, 2023) (GT-2) |
| Any single jump event, one name or one industry | at most **4**% | a total loss of one overnight position (SVB, halted and delisted in 2023) costs 4%, inside the drawdown halt (GT-2, KR2.8) |
| Held overnight in one industry, long plus short | at most **8**% | a 50% jump in an industry book concentrated in a few names costs 4%. On 13 March 2023 First Republic fell 62% while the regional-bank fund fell 12% (GT-2) |
| All positions held overnight, gross | at most **75**% | the planned book, about 60%, fits with room (GT-2) |
| Held overnight, beta-adjusted net (long minus short) | at most **15**% | a 13% market-wide gap costs 1.95%. Circuit breakers pause trading but don't bound an overnight gap, so the stress is the level-2 breaker, not the 7% level-1 pause (GT-2) |
| Held overnight, dollar net (long minus short) | at most **30**% | betas measured in calmer times move toward 1 in a crash: a 13% gap with every beta at 1 costs 3.9%, inside the jump-loss bound (GT-2) |
| Gross exposure, long plus short, at every moment | at most **100**% | no leverage |
| Daily loss, from the previous session's closing equity | **2**%: flat, and no new entries until the next session | a gap counts against it |
| Worst day, gaps within the jump assumptions and slippage while closing included | **3.5**% | the daily limit can't stop a gap: stops that gap through fill worse than their price, measured on real stress days (KR2.3, GT-2). Version 5 promised 2.5%, assuming stops fill 25% worse; the data showed 1.9 times on the worst day |
| Drawdown from the highest close | halt at **9**%: flat until the owner decides; equity never **10**% below its peak | the halt leaves room to close before the 10% line (KR2.2, KR2.7) |
| Room for a jump near the halt | at every moment, the worst single jump the assumptions allow is at most the room left to the 10% line, less **0.5**% | positions shrink as the drawdown deepens. Without this, a jump just before the halt could end at 13% (9% plus the 4% jump bound). Simulated with jumps at their observed rate, equity crosses the 10% line in 0.025% of stress years with the rule and 2.3% without it (GT-2) |
| Volatility that sizing aims for | **0.2**% of equity a day, about 3.2% a year, measured on **5**-day P&L | what the planned book produces (GT-2). Measured over 5 days so that trending P&L counts in full (GT-4). Realized volatility stays within **1.5** times it (KR2.6) |

A position that can't be traded at the moment is **trapped**: its stock is halted or paused, no session
is open, or the broker is unreachable. It gets an exit order at the first chance, and the owner is
alerted. After a market-wide trading halt, gross exposure is cut to the overnight limits as soon as
trading resumes, before any new entry. After the drawdown halt, trading restarts only on the owner's
decision, which states whether the peak is reset; without a reset, positions stay within the drawdown
room measured from the old peak. The **safe state** is: no new orders, open entry orders
cancelled, every position keeping a stop that works without the system, and the owner alerted.

A **broad index fund** is an unleveraged ETF tracking a broad US equity index (the S&P 500, the
Nasdaq-100, the Russell 2000 or a total-market index); a leveraged, inverse, sector or single-stock fund
counts as a stock. An **event-prone** position is a short in a biotechnology or pharmaceutical company,
or a long in a bank or other deposit-funded lender whose stock or industry has fallen 20% or more over
the last 5 trading days.

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
- sales pay the SEC fee ($20.60 per $1 million) and FINRA's fee ($0.000195 per share, capped at $9.79;
  paused for trades from 1 October to 31 December 2026, and kept in the model, which errs high);
- a short held overnight pays the broker's borrow fee (zero today for easy-to-borrow names);
- dividends are credited on longs and charged on shorts at the ex-date.

In G1, shorts are allowed only in names that a stated historical proxy shows as borrowable at the time,
and they are charged a borrow cost of **0.5**% a year.

The planning average is **8** bps a round trip, above the 7.5 bps that published spreads, market impact
at the participation limit and fees add up to (GT-3). A round trip in a name at the universe's limits
(8 bps of spread, full size at the participation limit) costs about 11.8 bps, inside the stressed
12 bps (GT-3). For stress, every cost is raised by half (×**1.5**). At the planned activity, costs take
about 1.3 Sharpe units. Doubling them would leave the targeted strategy a Sharpe of about 0.2, so G1
would reject the very strategy the goal aims for (GT-3). The live cost check (KR1.8) covers the rest.

Fills are judged conservatively:
- a limit order fills only when the price trades through its limit;
- a market order fills at the far side of the quote at the decision time, plus slippage.

Paper accounts fill more generously than this, so paper results are revalued with this model. At the
liquidity limit, market impact by the square-root law is 1.2 to 2.4 bps a side, 1.8 at the central
estimate, within the 1.5 bps charged once stressed to 2.25 (GT-3).

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

**No fixed number of positions: rotation.** The book holds every position the limits allow. When a
candidate can't open because a limit is full, it may take the place of held positions, whole or in
part, the lowest-valued first. It does so only when its value, on calibrated expected gains (KR3.7),
beats theirs by at least **1** times its own round-trip cost, so a switch clears its cost twice, as an
entry does, and has done so at two consecutive evaluations:
- a candidate's value is its expected gain, less its round-trip cost, less what a typical new entry
  would earn on the risk and time it would occupy;
- a held position's value is its expected remaining gain, re-estimated from its signal now and never
  from its profit or loss since entry, less the same charge for its remaining time, less any extra cost
  of closing it early. Its own closing cost isn't counted: it is paid either way.

Against churning:
- a position is not replaced within **15** minutes of opening, or within 20% of its planned holding
  time, whichever is longer;
- at most **3** rotations a day, and at most 20% of the round trips of the last 5 trading days.
  Rotations count inside the planned 25 round trips a week, so inside the cost budget;
- a name replaced is not re-entered the same day, and no rotation closes and reopens the same name in
  the same direction;
- no rotation while the market's median spread or volatility is above its 90th percentile of the last
  year, when switching costs most;
- the expected gains are calibrated on the trades the rules actually select, because the highest of
  1,000 to 2,000 forecasts is inflated by its own selection (KR3.7).

Rotation is an add-on that must earn its place. G1 runs each strategy twice, with rotation and
without it, registered together as two variants, and rotation ships only if the strategy's daily return
with it less without it has a one-sided 95% lower bound above zero (KR3.6). Otherwise the strategy ships
without rotation and is judged on its own. On paper and live, rotation stays as frozen; switching it is
a change (KR8.1). A single rotation earns little next to the noise in its outcome, about 8 to 16 bps
against a spread of several hundred, so only the strategy-level comparison can show whether rotation
helps, and only if it helps clearly. The research found the rule's form standard
(Gârleanu and Pedersen's aim portfolio; the no-trade bands of proportional costs) and the evidence that
investors' own switches lose money (Odean, 1999) a reason for the safeguards.

**The planned edge horizon is a judgment, not a limit.** On real prices a stock moves about 19 bps in 5
minutes and 168 bps in a day, and a round trip costs about 8 bps. A signal's information coefficient
(IC) is the correlation between its forecasts and what follows. Practitioners call 0.05 good and 0.10
very good (MSCI Barra); 0.15 is exceptional and rarely sustained. The IC needed:

| Hold | IC needed just to pay costs | IC needed to meet the entry rule (gain at least twice the cost) | IC needed to reach the aim, at the planned activity |
|---|---|---|---|
| 5 minutes | 0.53 | 1.06 | |
| 2.5 hours | 0.096 | 0.19 | |
| 1 day | 0.060 | 0.12 | |
| 2 days | 0.042 | 0.084 | |
| 3 days | 0.034 | 0.069 | 0.074 |

The arithmetic alone doesn't decide the horizon. Betting the sign of every forecast, a great signal
meets the entry rule from about 1.4 trading days; trading only the forecasts the rule admits, about 12%
of them clear it at 2.5 hours (GT-3). So the plan expects the profit from holds of **780** minutes (2
trading days) or more, held overnight, as a judgment from the research:
minute-level predictability lasts milliseconds to minutes and belongs to the fastest firms, intraday
effects earn about 2.6 to 5 bps a trade before costs, and the effects that survive costs span days
and accrue partly overnight. Shorter holds remain allowed, and G1 judges any strategy on its net results
(decision 3).

## Objectives and key results

**Return objective.** The annualized net excess Sharpe ratio must be at least **1** (about **3**% a year
at the volatility budget), aiming for **1.5** (about **5**% a year), and the account must also make
money. "Excess" removes what the market's moves explain. Start from the net daily return: it includes
dividends and borrow fees, but not interest on cash or on short proceeds. For each position, subtract
its weight times its 252-day beta to SPY (as of the previous close) times SPY's total return over the
same interval the position was held. Overnight and intraday are counted separately, so a tilt toward
the market's overnight drift doesn't count as skill. No risk-free rate is subtracted.

Every key result must hold at its gate. KPP marks one whose failure later, in operation, also stops the program until the owner decides.

| KR | Statement | Threshold | Window | Data | Method | Gate |
|---|---|---|---|---|---|---|
| KR1.1 (KPP) | the out-of-sample net excess return has a Deflated Sharpe Ratio of at least 0.95, counting every variant tried | ≥ 0.95 | ≥ 2,400 trading days of walk-forward out-of-sample history | historical consolidated bars and quotes; trial log | analysis | G1 |
| KR1.2 (KPP) | the out-of-sample annualized net excess Sharpe ratio is at least 1.0 (aim 1.5) | ≥ 1.0 | the G1 history | historical bars and quotes | analysis | G1 |
| KR1.3 | with every cost 50% higher, the net excess Sharpe ratio stays at or above 0.5 | ≥ 0.5 | the G1 history | historical bars and quotes | analysis | G1 |
| KR1.4 (KPP) | the out-of-sample history makes money after every cost | > 0 | the G1 history | historical bars and quotes | analysis | G1 |
| KR1.5 (KPP) | paper results keep up with a rerun of the frozen G1 strategy on the same days: the one-sided 95% lower bound of the mean daily gap (Newey-West) is above −1 Sharpe unit a year; G2 runs on past 120 days until this is shown, up to 250 | > −1 | the paper period | paper fills revalued conservatively; the frozen G1 code rerun on each paper day's data | analysis | G2 |
| KR1.6 (KPP) | at least 98% of round trips are matched between paper and the rerun, counted over both logs, in the same stock and direction; for matching, the rerun fills orders by the paper account's own rule | ≥ 98% | the paper period | paper and rerun trade logs | analysis | G2 |
| KR1.7 (KPP) | the paper account makes money after every cost, and its net excess return is above zero, over the whole paper period | > 0 | at least 120 trading days and 300 risk-bearing round trips, fixed in advance | paper fills, revalued conservatively | analysis | G2 |
| KR1.8 (KPP) | live costs are not significantly above the cost model: the lower one-sided 95% bound of live minus modeled cost is at most zero | ≤ 0 bps | ≥ 300 live round trips | live fills and decision-time quotes | analysis | G3 |
| KR1.9 | the edge holds across the history: Sharpe at least 0.25 in each chronological half, and above zero in both the calmer and the more turbulent half of the days (split at the median VIX) | ≥ 0.25 | the G1 history | historical bars and quotes; the VIX | analysis | G1 |
| KR2.1 (KPP) | no order is sent that would break a limit in the risk section | 0 | every paper and live day | order, fill and position logs | inspection | G2 |
| KR2.2 (KPP) | when the equity of record falls 9% below its highest close, trading halts within 60 seconds | ≤ 60 s | every occurrence, and a drill before G2 ends | equity of record; halt log | demonstration | G2 |
| KR2.3 | no day loses more than 3.5% of the previous close's equity, except through a jump beyond the jump assumptions (KR2.8 bounds those) | ≤ 3.5% | every paper and live day | equity of record | analysis | G2 |
| KR2.4 (KPP) | the kill switch cancels every order and closes every tradable position within 60 seconds; a trapped position gets its exit order within 60 seconds of becoming tradable; the owner is alerted within 60 seconds | ≤ 60 s | a drill every 20 trading days on paper, and one before G3 | broker records | demonstration | G2 |
| KR2.5 (KPP) | every share held is covered by a stop at the broker for its quantity within 2 seconds of each fill, partial fills included, and within 60 seconds of any restart; every uncovered interval is recorded; no share is uncovered at an overnight check; and the stop works while the system is stopped or disconnected | 0 uncovered beyond those times | a drill every 20 trading days on paper, and one before G3 | broker records | demonstration | G2 |
| KR2.6 | realized volatility (5-day P&L, scaled to a day) stays within 1.5 times the budget | ≤ 0.3% a day | every rolling 60 trading days | equity of record | analysis | G2 |
| KR2.7 | over the paper period, equity stays less than 10% below its peak | < 10% | the paper period | equity of record | analysis | G2 |
| KR2.8 | no single jump event, in one name or one industry, loses more than 4% of equity | ≤ 4% | every paper and live day | equity of record; event log | analysis | G2 |
| KR3.1 | every entry's recorded expected gain is at least twice its recorded expected cost | 0 below | every entry | order log | inspection | G2 |
| KR3.2 | every position is closed within 5 trading days and 7 calendar days, unless trapped, which is reported | 0 late | every day | position logs | inspection | G2 |
| KR3.3 | the eligible universe is evaluated in at least 99% of session minutes, on data under 5 seconds old | ≥ 99% | every day | evaluation log | analysis | G2 |
| KR3.4 | paper trading reaches 300 risk-bearing round trips within 150 trading days | ≤ 150 days | the paper period | fill logs | analysis | G2 |
| KR3.5 | every rotation follows every clause of the rotation rule: the book full on a limit; the lowest-valued positions replaced; the advantage, on calibrated gains, clearing the margin at two consecutive evaluations; the minimum hold; the daily and 5-day caps; no same-day re-entry; no close-and-reopen in the same name and direction; none above the 90th percentile of spread or volatility | 0 breaking it | every rotation | order and rotation logs | inspection | G2 |
| KR3.6 | rotation ships only if it clearly pays: G1 runs the strategy with rotation and without it (two variants), and rotation ships only if the daily return with it less without it has a one-sided 95% lower bound above zero; otherwise the strategy ships without rotation. On paper and live, rotation stays as frozen | > 0 | the G1 history | both runs' daily returns | analysis | G1 |
| KR3.7 | expected gains are calibrated before use: realized excess gain over expected gain, measured on the training data for each fifth of entries and the top tenth, scales every expected gain the entry and rotation rules use; G1's report shows the same out of sample, with 90% intervals | 0 uncalibrated decisions | every G1 run, and every decision on paper and live | trade log; calibration table | inspection | G1 |
| KR4.1 | running, connected and able to trade in at least 99.5% of session minutes, counting the unavailability the system causes itself; the broker's outages are reported separately | ≥ 99.5% | each month | health and connection logs | analysis | G2 |
| KR4.2 | after any restart, positions and open orders match the broker within 60 seconds | ≤ 60 s | every restart | broker records against the system's | test | G2 |
| KR4.3 | at every close, positions, orders and cash match the broker's | 0 differences | every close | broker records against the system's | inspection | G2 |
| KR4.4 | within 60 seconds of a fault (see C7) or a failed limit check, the system is in the safe state, every position's stop is confirmed at the broker or the position closed, and the owner is alerted | ≤ 60 s | every fault, and a monthly drill | event and alert logs | demonstration | G2 |
| KR5.1 (KPP) | no order trades against the system's own orders | 0 | each day | order and fill logs | inspection | G2 |
| KR5.2 (KPP) | order messages per fill (submissions, replacements and cancellations together) stay at 10 or fewer | ≤ 10 | each day | order and fill logs | inspection | G2 |
| KR5.3 (KPP) | no short sale without a current easy-to-borrow status | 0 | every short | order log and broker asset status | inspection | G2 |
| KR6.1 (KPP) | every variant registered before it is tested, and G1 counts every variant ever evaluated on its history, never fewer than 30. An idea or feature a pre-trained model proposes is registered like any other, and a G1 run shows the researcher only whether it passed, its DSR and the count. A variant is any run on the G1 history whose results anyone sees and that differs from earlier runs in its program logic, data, features, parameters or their ranges, universe, cost, fill or borrow model, walk-forward schedule or excess method, re-runs after bug fixes included. Paper days used to diagnose a failed G2 become part of the history for every later variant | 0 missing | the whole program | a trial log the research system writes itself: append-only, hashed, timestamped outside the author's control | inspection | G1 |
| KR6.2 (KPP) | before each gate, at least two independent AI reviewers from different model families, never a Fable model, challenge the evidence after scripts have recomputed its headline numbers; each sees only the evidence and the criteria set in advance. Every finding gets a written disposition (fixed, accepted with a reason, or rejected with evidence); a finding marked blocking closes only with a fix the reviewers confirm or a second independent review | 0 open | before G1, G2 and G3 | review records | inspection | G1, G2, G3 |
| KR6.3 (KPP) | every model that shapes G1's forecast was trained only on data from before each decision it informs (pre-training, fine-tuning, instruction data and any teacher model included), and a cutoff audit checks it. A model whose training data can't be shown to predate each decision, such as a current language model or a time-series foundation model, serves only monitoring, operations and explanation; data it extracts or labels for the forecast counts as shaping it | 0 | the G1 history | trial log; each model's documented training data; the cutoff audit | inspection | G1 |
| KR6.4 (KPP) | the G1 history is point-in-time and the simulation obeys the goal. Every stock that met the universe limits on each date is included, delisted ones with their delisting returns, and every input is as known at each decision. The borrow proxy is registered with the variant. Every simulated order stays within every limit, event blackout and short-sale rule. With every input lagged one more minute, the net Sharpe neither falls below half its value nor rises more than 10%, each judged against the paired standard error at 1%. A run that breaks one is void | 0 | the G1 history | simulation order log; membership and delisting records; the lag audit | inspection | G1 |
| KR6.5 | before G1, the review panel finds at least 2 of 3 flaws planted in a copy of the evidence without its knowledge (such as a one-bar look-ahead, an unregistered variant, or delisted stocks left out); a panel that finds fewer is strengthened, a human expert added, and tested again | ≥ 2 of 3 | before G1, and after any change to the panel | review records; the sealed key of planted flaws | demonstration | G1 |
| KR7.1 | every order records its strategy version, signal, expected gain, expected cost and risk when sent | 0 missing | every order | order log | inspection | G2 |
| KR7.2 | the owner can see profit and loss and open positions, no more than 60 seconds old, at any moment of the session | ≤ 60 s | every session, checked monthly | the owner's view against broker records | demonstration | G2 |
| KR7.3 | a daily report reaches the owner by 17:00 New York time | 0 missed | every trading day | delivery log | inspection | G2 |
| KR8.1 | strategies reviewed every 5 trading days; every change registered and run 60 trading days on paper before it replaces the live version | 0 missed | from G2 on | review, trial and deployment records | inspection | G3 |
| KR8.2 (KPP) | from the first paper day, a sequential test weighs "no edge" against "the targeted edge", paper days included; from G3 on it is acted on at every monthly look: stop when the evidence for no edge reaches 10 to 1, halve capital at 3 to 1 (once per crossing), grow capital only while the evidence favors the edge 3 to 1 or more | 0 not run or not acted on | from the first paper day | live fills; the test's log | inspection | G3 |

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
  O3 --> K3["KR3.1–KR3.7: entry rule, holding limit, watching, trade count, rotation, honest forecasts"]
  O4 --> K4["KR4.1–KR4.4: uptime, reconciliation, safe state"]
  O5 --> K5["KR5.1–KR5.3: no self-trades, message rate, borrow"]
  O6 --> K6["KR6.1–KR6.5: registration, review panel, model cutoff, point-in-time, planted flaws"]
  O7 --> K7["KR7.1–KR7.3: reasons, live P&L, daily report"]
  O8 --> K8["KR8.1–KR8.2: weekly review, sequential live test"]
```

| Goal | Obstacle (how it could fail) | Resolution |
|---|---|---|
| O1 | no real edge exists at these horizons and costs | research budget and stop rule; the planned edge horizon |
| O1 | the backtest flatters: overfitting, look-ahead, survivorship, the best of many variants | every run logged by the research system and counted (KR6.1); Deflated Sharpe Ratio (KR1.1); point-in-time history and a lag audit on every candidate (KR6.4); conservative fills; a Sharpe above 4 audited for leaks |
| O1 | a model has already seen the history it is tested on | only models trained on data from before each decision shape G1's forecast, with a cutoff audit (KR6.3) |
| O1 | the builder, a person or an AI model, already knows the history, so ideas are chosen with hindsight | every idea counted as a variant, those an AI model proposes included (KR6.1); each G1 run shows the researcher only pass or fail, its DSR and the count; the budget is final; the live test judges what the history can't (KR8.2) |
| O1 | costs higher than modeled | per-trade costs from quotes; stress at ×1.5 (KR1.3); live cost check (KR1.8); the liquidity limit |
| O1 | the edge decays or the regime changes | ≥ 2,400 days out of sample, holding in both halves and in calm and turbulent days (KR1.9); the sequential live test (KR8.2). The history from 2016 has no 2008-like crisis; the jump and drawdown limits are the protection there |
| O1 | the live system doesn't do what the tested strategy does | the paired fidelity test (KR1.5, KR1.6) |
| O1 | profit from riding the market, not from skill | excess return as the measure, and a profit required as well |
| O1 | short-side profit that can't be captured: dividends on shorts, the Rule 201 test, names not borrowable then | dividends charged; no short under Rule 201; a historical borrowability proxy and borrow cost in G1 |
| O2 | a gap, halt or takeover jumps past the stop | positions sized for jumps (4% overnight for a stock, 2% if event-prone, 10% intraday); industry and net limits; the jump-loss bound (KR2.8) |
| O2 | a jump lands on a book already near the drawdown halt | the worst jump kept within the room left to the 10% line: positions shrink as the drawdown deepens |
| O2 | a position can't be closed: halted, no session, broker down | the trapped rule; exits at the first chance; a second kill path (C6) |
| O2 | a runaway loop sends orders without limit | rate limits, duplicate blocking, per-name and daily throttles, kill switch (C3, C6, C13) |
| O2 | the system's view of its positions drifts from the broker's | continuous reconciliation; unknown order states never resent blind (C5) |
| O2 | a split or merger corrupts paper equity and fires a false halt | no position through corporate actions; the equity of record corrected |
| O3 | overtrading eats the edge | entry only at twice the cost (KR3.1); the cost budget |
| O3 | rotation churns: switching on noisy forecasts, inflated by picking the highest of many | a margin of one more round-trip cost; a minimum hold; daily and 5-day caps; calibrated forecasts (KR3.7); rotation on only while it pays (KR3.6) |
| O3 | too few trades for evidence | 300 trades within 150 days (KR3.4); a review below 10 a week |
| O4 | data feed stale, connection lost, process restarts | freshness in KR3.3; reconciliation (KR4.2, KR4.3); safe state (KR4.4) |
| O5 | an order that looks manipulative, or a short without a borrow | C9 surveillance; KR5.1; KR5.3; the Rule 201 check |
| O6 | results reported selectively, or hindsight changes to the rules | registration with outside timestamps; gates fixed before the data; independent challenge |
| O6 | the reviewers miss what the builder missed: one model family shares its blind spots, or defers to the builder's story | reviewers from different model families who see only the evidence; scripts recompute the numbers first; tested on planted flaws (KR6.5); a paid human review before real money passes $100,000 |
| O8 | changes judged on history that is already used up | every change runs 60 days on paper first (KR8.1) |

## Gates

| Gate | Question | Passes when |
|---|---|---|
| **G1 Research on history** | is there an edge, net of costs, on history not used to find it? | ≥ 2,400 trading days of walk-forward out-of-sample results, point-in-time, with a clean lag audit (KR6.4). DSR ≥ 0.95, counting every variant ever evaluated and never fewer than 30 (KR1.1, KR6.1), with the variance a Sharpe ratio has under no edge, so a real edge does not raise its own bar. Sharpe ≥ 1.0 (KR1.2), ≥ 0.25 in each half, and excess return above zero in the calmer and the more turbulent half of the days (KR1.9). Sharpe ≥ 0.5 at 1.5 times the costs (KR1.3). A profit (KR1.4). Significance counts autocorrelation (Newey-West, 8 lags). A Sharpe above 4 is audited for look-ahead leaks before it counts. Conservative fills. Only models trained on data from before each decision shape the forecast (KR6.3). Rotation ships only if it clearly beats the same strategy without it (KR3.6); expected gains calibrated (KR3.7). Review resolved (KR6.2), by a panel that caught at least 2 of 3 planted flaws (KR6.5) |
| **G2 Paper trading** | does the live system do what the tested strategy does, unattended and within every limit, and does it make money on paper? It can't prove the edge: 120 days are too few | at least 120 trading days and 300 risk-bearing round trips, fixed in advance, the trades within 150 days (KR3.4), and up to 250 days until paper is shown to keep up with a rerun of the frozen strategy (KR1.5), with 98% of trades matched between them (KR1.6). A breach of a KPP key result fails G2; any other is fixed, recorded, and G2 continues. After a failure that isn't the strategy's, G2 restarts with the same frozen strategy, counting no variant. A profit, and excess return above zero, over the whole period (KR1.7). Every O2–O7 key result met. Review resolved (KR6.2) |
| **G3 Real money, small first** | do real fills match the cost model, with money at risk? | the owner decides. It starts with 10% of the intended capital for at least 60 trading days, but never below the minimum for faithful sizes: $2,500, and enough for a typical position to hold 10 shares of the universe's median-priced stock. If 10% is less than that, the first step starts at the minimum, and the owner accepts a first step larger than 10% of the intended capital. Before it starts, the owner settles the tax treatment with an adviser (decision 10). Capital at most doubles every 60 trading days, and only while the live test allows growth (KR8.2), every G2 criterion holds, live costs match the model on the latest 300 round trips at the current size (KR1.8), and no liquidity limit binds on more than 5% of trades. It grows past $100,000 only after a paid human expert has reviewed the G1 statistics. Review resolved (KR6.2) |

**Kill criteria.**
- The program has at most **4** research stages of 3 months, each with at most **8** variants
  registered before its G1 runs, at most **2** variants of any one idea, so at least 15 distinct ideas,
  within a total of **30** variants on one data history and at most **12** months.
- If no strategy passes G1 within that budget, the program stops instead of trading anyway. It
  restarts only if the owner decides, and only on data after the last G1 test: 9.5 years for a
  fresh 2,400-day test. The budget is final; it is never extended because a variant nearly passed.
- A 9% drawdown halts trading until the owner decides.

**Running live (O8).**
- The owner reviews strategies every **5** trading days.
- A changed strategy runs **60** trading days on paper before it replaces the live one.
- From the first paper day, a sequential test weighs "no edge" against "the targeted edge" (a Sharpe
  of **1.5**) on the excess returns. Paper days count, because they are the first data the builder has
  not seen. It is a Wald-type test, its log-likelihood ratio capped at **2.89** (ln 18), so a long good
  run can't hide a later decay. From G3 on, every **21** trading days it decides:
  - at or below **-2.3** (10 to 1 for "no edge"), the strategy stops and returns to research;
  - at or below **-1.1** (3 to 1), capital halves, once per crossing;
  - capital may grow only at or above **1.1** (3 to 1 for the edge).

  GT-4 checks its design against bars the tests fixed in round 3, before any results: it should stop a
  strategy with the targeted edge by mistake within 3 years at most 10% of the time, halve a strategy
  whose edge is gone within a year at least half the time, and stop it within 3 years at least 75% of
  the time. Version 4 had set its own bars at 12% and 65% after seeing the results; the review of
  version 4 found that circular, and at -2.5 the dead strategy was stopped only 72 to 74% of the time,
  so the stop moved to -2.3. The same bars hold for an edge that works for 2 years and then goes, its
  costs remaining: the cap is what makes that decay show (GT-4). Fewer false stops would mean slower
  detection; halving within the first year, and the drawdown halt behind it, are the faster
  protections. Simulated with the capital schedule, a strategy with no edge reaches full capital within 3
  years 6 to 10% of the time (about a quarter with growth at even odds, as in version 4), and the
  targeted edge is halved within its first year 12 to 23% of the time.

## Controls

These cover what SEC Rule 15c3-5, FINRA Notice 15-09, EU RTS 6, MiFID II's record and clock rules, the
Fed's model-risk guidance (SR 26-2, which replaced SR 11-7 on 17 April 2026) and the Knight Capital order
expect of an algorithmic trader (GT-7). Two deviations are stated: the alert time (C7), and the clock
tolerance (C14 follows the US audit trail's 50 ms, not MiFID II's 1 ms).

| Control | Statement |
|---|---|
| C1 | Before every order, limits are computed on the positions the broker has confirmed plus every open or unconfirmed order as if filled. The checked limits are buying power, gross, overnight and industry exposure, open risk, and the daily loss limit: new open risk is at most the day's remaining loss budget divided by 1.25. An order that would exceed one is blocked. |
| C2 | A risk-increasing order must meet all of these, or it is not sent: <ul><li>a limit order at most **1**% through the consolidated best bid or offer;</li><li>a quote at most 5 seconds old, neither crossed nor locked;</li><li>a spread at most **3** times the name's median;</li><li>within the position and liquidity limits, and at most **10**% of the volume expected while it works.</li></ul> A risk-reducing order is never blocked by the system's own price, universe or event checks, and is limited only to the exchange's price band. When the broker rejects one (an open order holding the shares, an opposite order), the system clears the conflict, sends it again at once and alerts the owner. No order carries an extended-hours flag, and the exit of a position trapped outside the session is sent at the next open, never queued overnight. |
| C3 | An order identical to one sent in the last **5** seconds is blocked. The system sends at most **2** orders a second, and makes at most **100** requests of the broker in any minute (orders, replacements, cancellations and polls together): half of Alpaca's 200 a minute per account, the rest kept for exits, reconciliation and the independent kill path. Once a day's order messages reach **10** per fill, no new entries are sent that day. |
| C4 | Before every session and every risk-increasing order, the system checks the event and corporate-action calendar, the short-sale rules (easy-to-borrow status, the Rule 201 test, the short-interest limits) and the universe limits. |
| C5 | Every fill is recorded as it arrives. Positions, orders and cash are reconciled with the broker:<ul><li>continuously, from its trade-update stream;</li><li>by a poll at least every 60 seconds;</li><li>after any disconnect and every restart;</li><li>at every close.</li></ul> A mismatch, an order of unknown state, or an order the system did not send blocks risk-increasing orders and alerts the owner. An order of unknown state is never sent again blind. Records are kept at least 5 years, append-only and hash-chained, with a copy off the host. A daily report reaches the owner by 17:00 New York time. |
| C6 | A kill switch cancels all orders and closes all positions. The owner can use it at any time, and the drawdown halt triggers it automatically. A second way to do the same depends neither on the trading process, nor on its host, nor on a person being there: it first suspends trading at the broker, then cancels and closes everything, when the trading process stops reporting for 60 seconds or the owner asks. The broker's own controls are a third way, and both are drilled; Alpaca cancels nothing by itself when a client disconnects. The broker account's margin multiplier is set to the lowest value that allows the planned shorts, so the broker itself caps a runaway. Only one instance of the system trades at a time. Every order carries the strategy version that sent it. |
| C7 | Real-time monitoring alerts the owner within **60** seconds of: <ul><li>a blocked or rejected order;</li><li>a data gap longer than **30** seconds;</li><li>a lost connection;</li><li>a reconciliation mismatch;</li><li>a limit reaching **0.8** of its threshold.</li></ul> An alert not acknowledged within **5** minutes is repeated through a second channel. A **fault**, an alert that the system itself may be wrong, puts it in the safe state at once: an order or fill it did not send (the kill switch fires), a reconciliation mismatch, an order of unknown state, stale data, a lost connection, a restart, or repeated rejections. Within **60** seconds every stop is confirmed from the broker's records, and a position without a working stop is closed. Unacknowledged, a fault closes every position after **60** minutes or 15 minutes before the close (**15:45**, or 12:45 on early-close days), whichever comes first, and the system stays stopped until the owner acknowledges. A **warning** (a limit near its threshold, a single rejected order, a market event) stops new entries once unacknowledged for **15** minutes; exits, stops and the loss limits keep working. This relaxes RTS 6 Article 16(5) (alerts within 5 seconds, staff to act on them) because the owner wants an unattended system. |
| C8 | Changes are versioned, registered, tested on history and then on paper for 60 trading days before use. They are deployed only outside the session and can be rolled back; nothing changes during a trading day. Before each open, every component is checked to run the approved version. A written runbook covers every incident the alerts name. |
| C9 | Orders never cross the system's own orders, are never sent without intent to trade, and are not used to move the closing price; surveillance checks the logs daily. |
| C10 | The obstacle table above is reviewed monthly, and the controls' effectiveness is reviewed in writing every quarter. |
| C11 | Broker credentials are kept outside the code and repository. Paper and live keys are separate, and only the trading process and the independent kill path, on separate hosts, can read them. Keys are rotated every 90 days and at once on any suspicion. The broker account uses multi-factor sign-in. An order the system did not send triggers the kill switch. |
| C12 | A panel of independent AI reviewers challenges the evidence before each gate (effective challenge, KR6.2), tested on planted flaws (KR6.5), with a paid human review before real money passes $100,000; the sequential live test weighs the live results every month (KR8.2). |
| C13 | At most **4** round trips in one name a day, at most **300**% of equity traded in a day, and at most **50** open positions, a check against a malfunction rather than a limit on the strategy. Reaching any of them stops new entries until the owner allows them again. |
| C14 | The host clock stays within **50** ms of UTC and is monitored; beyond it, no risk-increasing orders. This follows the US consolidated audit trail's tolerance, not MiFID II's 1 ms for algorithmic trading: the system is not subject to MiFID II and decides on a scale of seconds. |

## How results are judged (evaluation assumptions)

These numbers set how sure the gates must be. Since round 5 they are the goal's claims, not the tests'
bars: the tests hold their own bars (`goaltests/anchors.py`), each from your own words, a rule, a
published figure, or a judgment that says when it was set. A claim must be at least as strict as the
tests' bar, and GT-4 and GT-8 judge the measured rates against the stricter of the two:
- a new idea has a 5% chance of a real net edge before testing; the tests allow at most 10%, ten times
  the share of day traders who are reliably profitable. A real edge is equally likely to be any Sharpe
  up to 2, below G1's leak ceiling of 4. GT-8's verdict doesn't rest on this: it judges at its own
  reference, a 5% prior with real edges exponential around a Sharpe of 0.75, so small edges are commoner,
  and at the upper bound of the rate at which a strategy with no edge reaches real money;
- a strategy that passes G1 and G2 should have a real edge with probability at least 80%, and be worth
  running (Sharpe 1 or more) with probability at least 70%, at the goal's prior; at the tests' reference
  it must be more likely real than not, and more likely worth running than not;
- G1 should pass the best of the variant budget, when none has an edge, at most 1% of the time; the
  tests' bar is 5%, what a Deflated Sharpe Ratio of 0.95 claims, judged at the upper 95% bound;
- G2 passes a strategy with no edge about half the time: over 120 days, half of them make money by
  luck. So G1 carries the evidence, and G2 checks the system. The tests' bar is 50%, chance: above it, G2
  would reward something other than an edge;
- a strategy with no edge should reach real money at most 0.5% of the time; the tests' bar is 1%,
  judged at the upper bound;
- a real edge at the target should pass both gates more often than not. That bar is the tests' own, set
  in round 5 after version 5's power was known, and said so; each gate's own pass rate is reported
  against the 80% convention for a test's power, which G1 misses under autocorrelated returns (decision 5);
- G2's fidelity test should pass an honest implementation at least 95% of the time and catch one that
  loses a Sharpe unit to execution at least 80% of the time. This assumes paper and the rerun differ by
  18% of the strategy's daily volatility, what KR1.6's 2% of unmatched trades allows on a real stock's
  volatility (GT-4 checks it). Noise makes the test harder to pass, and G2 runs on until it is decisive.
  At 5% unmatched, as version 4 allowed, the noise would be 29%, and an honest implementation would
  fail up to 11% of the time;
- the live test should stop the targeted edge by mistake within 3 years at most 10% of the time, halve
  a strategy whose edge is gone within a year at least half the time, and stop it within 3 years at
  least 75% of the time, whether the edge was never there or went after 2 years; bars the tests fixed
  in round 3;
- GT-4 simulates the whole budget of 30 variants and charges the plan's costs, 0.017% of equity a day
  (25 trades a week x 4% x 8 bps = 4.2% a year); GT-4 checks both against the rest of the goal;
- every one of these figures assumes the history is out of sample for the researcher. GT-8 shows how
  they move if the builder's knowledge of the history acts like 100 or 1,000 variants nobody counted;
- the drawdown halt should stop a strategy that has the targeted edge in at most 10% of years;
- published effects count at most at 42% of their reported size, what remains after publication
  (McLean and Pontiff).

## Decisions, settled with the evidence

You asked for each open decision to be settled on researched, cross-checked evidence. The research is in
`../reports/Trading goal decisions research.md`, with its notes beside it. Most of its sources could
be read only as search-result extracts, because this environment blocks direct page fetches, so each
finding there carries a label saying how well it was checked. The goal now holds the choices below, and
you can overturn any of them; the goal and its tests change with you.

1. **Overnight size per name: 4%, not 8%** (about 80% confidence). Under the goal's other limits (2%
   open risk, 75% overnight gross, a volatility budget of 0.2% a day), 8% spreads the same risk over half
   as many names: at most about a quarter more return, not double, and twice the loss from one gap. An
   8% position lost in full costs 8%, twice the single-jump bound. In the project's own price data,
   gaps of 20% or more away from earnings came about 1.3 times in 10,000 stock-nights; the one fund
   limit the research found caps a single position at 5% (single source). Three refinements are now
   in the goal: the jump assumed by type of position (20% for a broad index fund, so up to 10%; 100% for
   a biotech short or a bank under a run, so 2%); room for a jump near the drawdown halt; and, since the
   statistics review, the same 4% within the session, because a news halt reopens like an overnight gap
   (version 4 allowed 10% within the session, which a 50% reopening would turn into a 5% loss). The real
   lever for return is the volatility budget, which trades against your 10% drawdown line.
2. **No fixed number of positions** (your decision; the research confirms it). The book holds what the
   limits allow, and a better candidate replaces the lowest-valued positions only when the switch beats
   them by its own round-trip cost after paying it (see Activity). Theory: trade toward an aim
   portfolio, weighing each signal by how fast it decays (Gârleanu and Pedersen, 2013); with costs
   proportional to size, as here, the best policy has a band in which it doesn't trade (Constantinides,
   1986; Davis and Norman, 1990), which the margin provides. Practice: systematic managers let the count
   follow from risk, exposure and cost limits, and a buy/hold band is the most effective simple way to
   cut costs (Novy-Marx and Velikov, 2016). Caution: investors' own switches lost money even before
   costs (Odean, 1999), and the highest of 1,000 to 2,000 forecasts is inflated by about three
   standard deviations of its error. So forecasts are calibrated (KR3.7), and rotation ships only if it
   clearly beats the same strategy without it (KR3.6). Version 4 judged rotation trade by trade, which
   the statistics review showed could not tell a useful rule from a useless one (13 to 19% power) and
   would have failed the whole strategy with it. Confidence: about 85% in allocating by budget, 80% in
   the rule's form, 55 to 60% that rotation adds value here, which is why it must prove it.
3. **The planned edge horizon: holds of 2 trading days or more, held overnight** (about 70%; about 90%
   that minute-level holds can't pay their costs). This is a judgment from the research, not a result
   of arithmetic: the cost arithmetic depends on how forecasts are traded (GT-3). Predictability at the scale of minutes lasts milliseconds and belongs to the fastest
   firms; intraday momentum earned about 2.6 to 5 bps a trade before costs; the effects that survive
   costs span days (Novy-Marx and Velikov, 2016), momentum's profits accrue overnight (Lou, Polk and
   Skouras, 2019), and published effects have decayed since publication. Holds from seconds stay allowed. A later option, as its own study: a cheaper universe of
   the largest stocks and index funds, at about 1 to 2 bps a round trip, could make holds of 30 minutes
   to a few hours viable.
4. **Paper trading for at least 120 trading days** (your answer).
5. **The research budget: 30 variants, at most 2 per idea, so at least 15 distinct ideas, within 12
   months in four 3-month stages** (moderate confidence that 10 was too few; low confidence in the exact
   number). With 10 variants spent 3 to an idea, only 3 or 4 ideas get tested, and on the goal's own
   prior the program would rarely find a real edge. The research suggested about 30 (20 to 50). Every
   variant is counted and the Deflated Sharpe Ratio's bar rises with the count, so false passes stay
   rare, while each gate's own pass rate falls (G1, under autocorrelated returns: 81.5% at 10 variants,
   75.8% at 20, 70.5% at 30). Version 4 chose 20 by setting a 75% floor for each gate after seeing
   those numbers, and said the floor came first. It didn't: the statistics review found the choice
   circular, and right. The goal now judges the budget on what you care about: the program's chance of
   ending with a real edge, with a false edge reaching real money rarely and a passing strategy more
   likely real than not. On those, 30 beats 20 on every count. Those bars, and the one that a real edge
   at the target pass both gates more often than not, were also set after results were known; since
   round 5 they live in the tests, which say so, and G1's power is reported against the 80% convention it
   misses. Distinct ideas count
   more than variants of one idea, hence at most 2 per idea. Ideas are registered before each stage's G1
   runs; a G1 run shows the researcher only pass or fail, its DSR and the count; the budget is final,
   with no top-up after a near miss. A stop is in practice permanent: a fresh 2,400-day test needs about
   9.5 years of new data.
6. **The independent reviewer: a panel of AI reviewers from different model families, never Fable, and
   a paid human before real money passes $100,000** (about 65%). One reviewer from the builder's own
   model family was the weakest defensible choice: models favor their own outputs and those of similar
   models, and their errors are correlated, more so within one developer. AI reviewers agree with
   experts about as often as experts agree with each other on general review, but the best model found
   only 21% of the real errors in published papers (SPOT, 2025), and panels from different families
   were less biased (Verga and others, 2024). So scripts recompute the headline numbers first, the
   reviewers see only the evidence, every finding gets a written disposition, a blocking finding can't
   be waived alone, and the panel must catch 2 of 3 planted flaws (KR6.5). You rule on the findings.
   **Your call:** a reviewer from another company (a GPT or Gemini model, say) means sending it the
   evidence. If you'd rather not, the panel can use different non-Fable Claude models, and the
   planted-flaw test shows whether that is good enough.
7. **Alerts when you are away: faults and warnings handled apart** (high confidence in the direction,
   medium in the numbers). A fault, which says the system itself may be wrong, puts it in the safe
   state at once and has every stop confirmed at the broker within 60 seconds; the alert repeats through
   a second channel after 5 minutes; unacknowledged, everything closes at 60 minutes or 15:45, whichever
   comes first, so the closing orders go out while the market is open. A warning only stops new entries
   after 15 minutes. RTS 6 Article 16(5) asks for alerts within 5 seconds and action as soon as possible;
   Knight Capital lost about $460 million in 45 minutes in 2012 after 97 automated emails no one acted
   on. Alpaca has no automatic cancel when a client disconnects, but its stop orders stay live at the
   broker if the system dies.
8. **Extended hours: none, as you said** (the research leans the same way, about 60%). An order after
   hours can't avoid a news gap: prices reprice within milliseconds of a release, and after-hours spreads
   have been measured at 1.4 to 4 times the session's, and far wider right after news, so an exit there
   pays more for the same gapped price. The overnight
   session (20:00 to 04:00) is ruled out: its main venue cancelled every trade in one stretch of the
   night of 5 August 2024, and the exchanges' own overnight sessions are only planned to start on 6
   December 2026. A narrow exception, closing-only limit orders before the open or after the close on
   news about a held name, can be reconsidered after G2, with evidence from paper.
9. **The AI model in the forecast: only models trained before each decision** (about 85%). A current
   language model has absorbed the history G1 tests on, and its advantage fades after its training
   cutoff: language-model trading agents lost about half or more of their Sharpe ratio after it (2025).
   A GPT-4 news signal tested entirely after its cutoff also faded, from a Sharpe of 6.5 in late 2021 to
   1.2 in early 2024, as such models spread. Hiding names and
   dates helps only partly, instructions not to use hindsight don't work, and vendors' stated cutoffs
   can be off by months. So a model shapes G1's forecast only if it was trained on data from before each
   decision, with an audit (KR6.3, now worded by the decision date, so the system's own walk-forward
   retraining is allowed); current models serve monitoring, operations and explanation, and their ideas
   count as variants. Proving a forecast driven by a current model forward would take 3 to 4 years at the
   targeted Sharpe ratio.
10. **Real money and taxes: settle before G3** (information, not tax advice):
    - **Fixed costs.** The $99-a-month data plan, from G2 on, costs about a third of the minimum
      target's return at $100,000; below about $40,000 of capital it takes most of it.
    - **Capital.** At least $2,500: short sales need $2,000 of equity, kept through a 10% drawdown. And
      enough for a typical position to hold 10 shares of the universe's median-priced stock: at $2,000 a
      4% position is $80, which whole shares can't match. With a median price of $50 to $100 (not yet
      measured), that is $12,500 to $25,000. G3 starts at that minimum when 10% of the intended capital
      is less, so with less than about ten times the minimum the first step can't be both faithful and
      small. At larger capital the liquidity limit (0.02% of a stock's daily dollar volume) narrows the
      universe: a 4% position needs $50 million a day at $250,000, and $200 million a day at $1 million.
      Capital is squeezed from both ends.
    - **A US taxpayer.** Short-term gains are taxed as ordinary income. The wash-sale rule spans all your
      accounts and IRAs, while the broker applies it only within one account. Payments for dividends on
      shorts held 45 days or less are added to cost, not deducted. Trader status is a facts-and-
      circumstances test; the section 475(f) election, which removes wash sales and the $3,000 loss cap,
      must be made by the original due date of the previous year's return (15 April 2027 for 2027), and
      revoking it within 5 years needs the IRS's consent.
    - **A taxpayer elsewhere.** US capital gains are generally not taxed unless you spend 183 days or
      more in the US; dividends are withheld at 30% or the treaty rate (form W-8BEN); US stocks above
      $60,000 are exposed to US estate tax. How your country taxes frequent trading decides the rest.
    - **Alpaca.** The pattern-day-trader rule gave way to intraday margin on 2026-06-04 (FINRA
      Regulatory Notice 26-10, approved by the SEC on 2026-04-14). Shorting needs $2,000 of equity, and
      easy-to-borrow names carry no borrow fee for Trading API users (Alpaca's own pages). FINRA fined
      Alpaca $300,000 in March 2026 for late trade reporting.

## Before the API key can be used

These are actions, not decisions. The Alpaca review (`reviews/v4/readiness-alpaca.md`) found that
nothing can be connected, probed or drilled until the first two are done:
- **Access.** An Alpaca account with two-factor sign-in, and a paper key only, stored outside the
  repository in the environment's secrets (C11). This environment's network policy refuses every Alpaca
  host: allow `paper-api.alpaca.markets` (orders and the trade stream), `data.alpaca.markets` and
  `stream.data.alpaca.markets`, and for checking documentation `docs.alpaca.markets`. Leave
  `api.alpaca.markets`, the live host, out until G3.
- **A place to run.** This development environment lasts only for a session, so the system needs a
  persistent host, a second independent one for the kill path (C6), and two alert channels.
- **Market data.** The free plan carries one exchange's quotes (IEX, about 4% of volume) and 30 symbols
  at a time. The goal needs consolidated quotes for the whole universe every minute (KR3.3) and real
  spreads for costs from G2 on: Alpaca's Algo Trader Plus plan ($99 a month), which allows one data
  connection per account, so one process must feed the rest. Confirm that the paper key gets it.
- **Data Alpaca doesn't provide.** Earnings and other scheduled events, a security master with delisted
  names and delisting returns, short interest and float, the Rule 201 state, industry classifications
  and the VIX. They come from other vendors before a strategy is researched; the plumbing doesn't need
  them.
- **The broker's own rules, probed on paper first.** Alpaca can't attach a stop to a partly filled
  entry, rejects an exit while a stop holds the shares or an opposite order is open, has no automatic
  cancel when a client disconnects, shares one budget of 200 requests a minute between every process on
  the account, and its Python library resends orders after some errors and sets no timeouts. Each of
  these is designed around in the requirements, and checked on day one.
- **History.** G1 needs 2,400 trading days out of sample after an initial training window. That means
  consolidated intraday history from the start of 2016 or earlier; Alpaca's appears to start on
  2016-01-01, about 2,700 trading days to now. That leaves about 15 months for the first training
  window, no further holdout, and no 2008-like crisis in the data. Confirm the start date, or plan for a
  longer paid history. The history must also include delisted stocks (KR6.4).

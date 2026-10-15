# GT-9 review: risk limits, controls, broker mechanics and regulation

An independent reviewer, given only `METHOD.md`, `GOAL.md` and `goal.toml`, reviewed the goal as it
stood at commit `dbc6b77`. The reviewer did not see the tests. Alpaca's, FINRA's and Cboe's sites were
blocked, so the broker and rule facts come from search excerpts and are marked where they could not be
confirmed. This is the reviewer's report, lightly condensed. The response to each finding is in
`REPORT.md`.

## Findings

**R-1 (blocker). Stops don't bound the losses that matter: jumps.**

The limits treated a stop as a loss bound that slips at most 25% of its distance. Overnight gaps, news
halts and limit-up/limit-down pauses fill at the reopening price, or not at all.

| Event | Move | Loss under the old limits |
|---|---|---|
| Biogen, 2021-06-07 (FDA decision, halted) | +64% intraday, +38% at the close | a 20% short loses 7.6–12% |
| Activision, 2022-01-18 (cash bid) | +37% premarket | a 10% overnight short loses 3.6% |
| SVB, 2023-03-10 (halted before the open after a −60% day; never traded on Nasdaq again) | about −100% | a 10% overnight long loses about 10%, and it can't be sold |
| First Republic and Western Alliance, 2023-03-13 | −60% to −75% | a 25% overnight book in one industry loses over 10% |

- A 7% market-wide circuit breaker is a 15-minute pause, and only before 15:25. It caps neither an
  overnight gap nor a single stock.
- A long-short book is mostly hedged against the market. Its tail is single-name jumps, sector contagion
  and short squeezes.
- Alpaca's older documents describe buy stops converted to stop-limits, which may not fill on a gap.

Proposed:
- A jump-loss limit: a 50% jump for positions held overnight or through a halt, and 20% intraday (two
  limit-up/limit-down bands). The jump loss in any one name is at most 2% of equity.
- An industry cap and a net cap overnight.
- No position through any scheduled company event: FDA dates, trial readouts, votes, lockup expiries.
- A separate key result for jump losses.

**R-2 (blocker). The activity plan, typical size, volatility target, overnight caps and cost budget
can't all hold.**
- By Little's law, 25 trades a week held two days means about 10 open positions: at the cap, and 50–100%
  gross overnight against a 25% cap.
- Trimming to 25% at every close would cost about 15% a year more.
- 1.5% stops on 10% positions would be touched within two days 53% of the time.
- G1 was not bound by the limits.

Proposed:
- A feasibility rule with at least 20% headroom.
- One consistent set of numbers, chosen by the owner.
- In G1, every simulated order obeys every limit, or the run is void.

**R-3 (major). Short-sale mechanics were missing.**
- **Rule 201:** after a 10% fall, shorts sell only above the bid.
- **Dividends:** payments in lieu are owed on shorts, and Alpaca's paper account doesn't simulate them.
  A model could learn to profit from the ex-date drop.
- **Borrow status:** a held short can turn hard to borrow, be recalled, or be bought in.
- **History:** borrowability can't be known from current status.
- **Squeezes:** there was no limit on squeeze risk.

Proposed:
- Dividends charged to shorts and credited to longs in every simulation.
- No new short under Rule 201.
- No short over a large ex-date.
- Close a short that loses easy-to-borrow status.
- A historical borrowability proxy and a borrow charge in G1.
- Short-interest and days-to-cover limits.

**R-4 (major). Corporate actions were not mentioned.**

Splits, special dividends, spin-offs, mergers, delistings and ticker changes are all missing. Alpaca's
paper account applies neither splits nor dividends, so one held split can trigger a false drawdown halt
(a 20-for-1 split shows a 10% long as −9.5%).

Proposed:
- No position held through any corporate action other than an ordinary cash dividend.
- A calendar check before every order.
- Positions and stops re-verified after the open on every ex-date.
- Equity corrected for actions the paper account did not apply.

**R-5 (major). The controls check limits against the system's own view of its positions, and compare it
with the broker only at restarts and the close.** Knight Capital failed this way.

Missing:
- Open and unconfirmed orders counted in every limit.
- Continuous reconciliation, with new risk blocked on any mismatch.
- No blind resending after a timeout.
- Broker-initiated changes handled.
- Stops for partial fills.
- A per-symbol and daily-notional throttle.
- One active instance.
- A kill path outside the trading process.
- Escalation of alerts no one acknowledges.
- A pre-open version check and an incident runbook.
- Headroom in the broker's 200-requests-a-minute limit.

**R-6 (major). Loss measurement was undefined.**
- The starting equity for the day.
- The marks used for prices.
- Which equity counts: the broker's paper equity or the revalued one.
- When the drawdown is checked, and from which peak.
- When the overnight caps are measured, including early-close days.
- How long a passive excess has to be cured.
- Whether C1 nets the day's realized loss.
- "Never" over the whole record eventually fails even for a real edge. At Sharpe 1.0 and the old
  0.5%/day volatility, the expected time to a first 10% drawdown is 4.5 years.

Proposed: a measurement section, and KR2.2 split into "the halt fires" and "the halt rate matches GT-4".

**R-7 (major). Positions can't always be closed now.**

Single-stock halts, limit-up/limit-down pauses, a level-3 circuit breaker, broker outages, and the
hours outside the session all prevent it. SVB was halted and never reopened. As a result:
- KR2.4 (kill switch within 60 s) can't be met as worded.
- KR3.2 (holding limit) breaks over a weekend halt.
- Paper drills fill at once, so they prove nothing.

Proposed:
- Define a "trapped" position.
- Time only tradable positions in KR2.4. For trapped ones, an exit works at the first reopening and an
  alert goes out within 60 s.
- Decide on risk-reducing orders in the extended sessions.
- A manual way to flatten during an outage.

**R-8 (major). The price checks have gaps.**
- Only limit prices were collared.
- Exits could be blocked by the price, universe and event checks.
- No definition of a bad quote.
- No requirement on clocks.
- C7 claimed RTS 6 Art. 16, which requires alerts within 5 s and a person monitoring. That is a
  deliberate deviation, not coverage.

Proposed:
- Risk-increasing orders are limit orders within 1% of the national best bid and offer (NBBO), sent
  only on a fresh, uncrossed quote that is not abnormally wide.
- Risk-reducing orders are never blocked.
- Consolidated quotes from G2 on.
- Clocks within 50 ms of UTC.
- The RTS 6 deviation stated.

**R-9 (major). Liquidity is an absolute number, so "the goal holds for any amount" is false.**

There was no participation limit, no ceiling on G3's doubling, and slippage stayed fixed at any size. A
20% position in the least liquid eligible name equals 39 minutes of its average volume at $10 million of
equity.

Proposed:
- A position at most 0.1% of the name's daily dollar volume.
- An order at most 10% of the volume over its working time.
- G3 scaling stops when the participation limits bind.

**R-10 (minor). The universe was ambiguous.**

Crypto funds, volatility products, commodity pools, ETNs, ADRs, SPACs and closed-end funds were not
clearly in or out.

**R-11 (minor). Record keeping and credentials had gaps.**
- No retention period, no tamper evidence, and trial registrations whose timestamps the author can edit.
- No key rotation and no MFA.
- No detection of orders the system did not send.

**R-12 (minor). The facts about Alpaca were out of date in places.**
- Alpaca dropped the pattern-day-trader rule on 2026-06-04 and applies FINRA's intraday margin rule.
- Easy-to-borrow status is a locate, not a borrow.
- Alpaca's borrow fee for easy-to-borrow names is $0.
- Margin is no material risk at 100% gross.
- G3's capital must allow whole-share shorts.

## Reviewer's overall judgment

"Not yet fit to go to requirements and architecture, though the fix is a bounded revision, not a
rethink." The structure is sound, and the owner's fixed points are honored. Two blockers would mislead
decisions:
- the loss limits don't bound the jump losses that dominate this universe (R-1);
- the plan contradicts the limits, so the tests were calibrated on a book the limits forbid (R-2).

Fix those, re-run the tests, add the measurement definitions and the short-sale and corporate-action
rules. The control gaps can then be carried into requirements as stated.

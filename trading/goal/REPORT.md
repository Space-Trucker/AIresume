# Goal test report

This report records how the goal was tested, what failed, what changed and why, and where the goal
stands now. The tests and their oracles are in `TESTS.md`. The goal is in `GOAL.md` and `goal.toml`.
The full output of the latest runs is in `results/`.

## Summary

| Version | What it is | Checks passing | Main problems |
|---|---|---|---|
| 1 | the goal as agreed in conversation (`goal_v1.toml`) | 41 of 152 | vague, inconsistent and statistically blind; see below |
| 2 | the first revision, after the first round of tests; reviewed independently | (superseded) | stricter tests and three reviewers found 35 problems |
| 3 | the current goal (`goal.toml`), after the stricter tests and the review | 387 of 387 | none open; 10 decisions wait for the owner |

The goal went through three rounds:
- **Round 1.** The first tests found version 1 vague, inconsistent and statistically blind. Version 2
  fixed what they found.
- **Round 2.** Stricter tests found that version 2 still contradicted itself, and that its research
  gate would pass a real edge only 20% of the time.
- **Round 3.** Three independent reviewers, who saw only the goal documents, found 35 more problems.
  Version 3 responds to all of them: 29 accepted as proposed, 6 accepted with a different number or
  design. One sub-proposal was not adopted, with the reason given, and none was declined outright.
  Each is recorded below.

What the owner most needs to know is in `GOAL.md`, under "What to expect":
- At the aim, the goal is about 5% a year above the market, after costs.
- The chance of reaching real money with a real edge is at most about one in seven.
- If everything passes, full capital is more than two years away.

## How the goal was tested

Nine tests, each with an oracle outside the goal. The goal is never evidence for itself.

| Test | Oracle |
|---|---|
| GT-1 statement quality | ISO/IEC/IEEE 29148 |
| GT-2 internal consistency | arithmetic; queueing theory; real price gaps; named market events |
| GT-3 cost feasibility | published fees and spreads; volatility measured on real prices; information-coefficient rules of thumb; the square-root law of market impact |
| GT-4 skill or luck | simulations whose true edge we set |
| GT-5 random strategies on real prices | random entries on real prices |
| GT-6 metric gaming | strategies built to game the goal |
| GT-7 control coverage | regulators' checklists |
| GT-8 outside view | published base rates and a stated prior |
| GT-9 effective challenge | independent reviewers |

Simulations use fixed seeds, so every run repeats. The real price data are pinned by version or commit
and checked against a SHA-256.

```bash
cd trading/goal
python3 -m goaltests                  # the current goal, about 4 minutes
python3 -m goaltests goal_v1.toml     # the goal as first agreed
```

## Version 1: the goal as agreed

Version 1 wrote down what was agreed in conversation: holds up to 5 days, long and short, $100,000 on
paper, 0.5% risk per trade, 5 positions, 20% per position, a 2% daily stop, a 10% drawdown limit, a kill
switch, constant trading, realistic costs, profitable on history and over 4–8 weeks of paper.

Run through the final tests, it passes 41 of 152 checks (`results/goal_v1.txt`). What fails, by test:

| Test | What fails in version 1 |
|---|---|
| GT-1 (30 failing) | <ul><li>key results with no metric, window, data or method ("no crashes", "realistic costs")</li><li>design in an objective ("AI model", "fast code")</li><li>no non-goals, no kill criteria</li><li>limits left as words</li><li>no goal kinds or questions</li></ul> |
| GT-2 (11 failing) | <ul><li>all stops hit at once cost 3.1% against a 2% daily limit</li><li>a 20% position held overnight through NVIDIA's −28% gap costs 5.6%</li><li>jumps not sized at all</li><li>"no borrowed money" contradicts short selling</li><li>no volatility budget, activity plan or return objective</li></ul> |
| GT-3 (3 failing) | <ul><li>no cost model</li><li>holds from seconds allowed, with nothing said about where the edge comes from; below about 2.5 hours costs need a signal beyond "great"</li></ul> |
| GT-4 (20 failing) | <ul><li>"profitable on history" passes the best of 10 no-edge variants 99.5–100% of the time</li><li>a no-edge strategy reaches real money 48–53% of the time</li><li>when one variant is real, a lucky no-edge one is chosen and passes instead in a quarter to two-fifths of runs</li><li>the 10% drawdown limit stops a real edge in 29–51% of years</li></ul> |
| GT-5 (4 failing) | on real prices, the best of 10 random strategies passes the history gate in 85–98% of windows, and paper in 43–52% |
| GT-6 (9 failing) | none of 9 ways to game the goal is caught |
| GT-7 (29 failing) | none of 29 control items is covered to the checklists' standard. Version 1 did name a kill switch and a risk manager; neither was specified enough to count |
| GT-8 (5 failing) | a strategy that passes is real with probability 4%; no research budget, no capital staging, no correction for variants tried, no discount on published effects |

## Round 1: from version 1 to version 2

The first round of tests drove these changes. Version 2 is kept in the history (commit `dbc6b77`):
- Every key result got a metric, unit, threshold, window, data source, verification method and gate.
- Design left the objectives.
- Limits became numbers.
- Overnight limits were added.
- Leverage was stated as gross exposure.
- A cost model was stated.
- An edge horizon was introduced, from the cost arithmetic.
- The history gate became a Deflated Sharpe Ratio over 2,000 out-of-sample days.
- Paper trading was given a combined significance test.
- Controls were added for every checklist item.
- A research budget and capital staging were added.

## Round 2: stricter tests on version 2

The first tests were too gentle, so they were made stricter before the review:

| Test | Was | Now |
|---|---|---|
| GT-4 no-edge case | a strategy that lost its costs | one whose gross edge just pays its costs (the hardest case) |
| GT-4 power | all 10 variants shared the edge | one real variant among 10 |
| GT-4 paper power | measured on its own | measured only after a G1 pass |
| Gates | | count effective observations under autocorrelation |
| GT-2 | | checks the planned activity against the position limits by queueing theory, and overnight gaps on more stocks |
| GT-5 history | 3 windows of real history | 32 |

What they found in version 2:
- **G1 would pass the targeted edge only 20% of the time.** Doubling every cost removed 1.3 Sharpe
  units from a strategy at the planned activity. A strategy at the target then failed the 0.5 floor.
  GT-3 confirmed it: 0.19 against 0.5.
- **The activity plan contradicted the limits:**
  - 25 trades a week held 2 days keeps 10 positions open, and with 10 slots a new trade finds them all
    full 21.5% of the time (Erlang);
  - that book is 100% gross held overnight, against a 25% overnight limit;
  - one 10% position through NVIDIA's −28.0% gap (2008), or Yahoo's +49.5% takeover gap (2008), broke
    the 2% daily limit.
- **G1 power under autocorrelated P&L** was 69.5% at 2,000 days.

What changed:
- overnight limits by direction;
- 15 slots, a 5% typical position, a 0.25%/day volatility budget;
- open risk capped per side and in total;
- the cost stress set at ×1.5;
- G1 at 2,250 days.

Commit `8cb9382`.

## Round 3: the independent review (GT-9)

Three reviewers, each given only the goal documents and a different lens, reviewed version 2. The
statistics reviewer worked while round 2's changes were landing, and reviewed that later state. Their
reports are in `reviews/`:

| Reviewer | Lens | Findings |
|---|---|---|
| Owner intent | owner intent and goal quality | 12: 5 blockers, 7 major |
| Risk and controls | risk limits, controls, broker mechanics, regulation | 12: 2 blockers, 7 major, 3 minor |
| Statistics | quantitative evidence and statistics | 11: 2 blockers, 8 major, 1 minor |

The statistics reviewer also simulated the gate code directly. The reviewers found what the tests
could not:
- the goal had quietly overridden what the owner asked for;
- stops don't bound jumps;
- paper trading carried no evidence about the edge;
- the variant count could be gamed.

### Responses

"Accepted" means the change was made as proposed. "Accepted, changed" means the problem was fixed with a
different number or design, for the reason given.

#### Owner intent and goal quality (`reviews/owner-intent.md`)

| ID | Finding | Response |
|---|---|---|
| O-1 | paper trading no longer had to make money | Accepted. KR1.7 (KPP) requires a net profit and an excess return above zero over the whole paper period. G2 states plainly that it checks the system and can't prove the edge |
| O-2 | eight of the owner's values changed without being flagged | Accepted. `GOAL.md` has a change table, "What changed from what you asked for": the owner's value, the new one, why, and the decision that settles it. The claim that version 1 missed every control is restated above |
| O-3 | the owner's holding periods were overridden | Accepted. The mission says "from seconds" again. The 150-minute horizon is a planning basis, not a limit or a non-goal (decision 3). Limit orders are charged from the decision mid, so passive execution is allowed |
| O-4 | the activity plan broke the overnight limits | Accepted (GT-2 found it too). There is one consistent plan. The entry rule overrides the activity floor, which is now a review trigger |
| O-5 | no odds, time, money or what-if-nothing-passes | Accepted. "What to expect" in `GOAL.md`, with the odds from GT-8 |
| O-6 | "excess return" undefined; no absolute profit | Accepted. The excess return has a formula. Net profit is required at G1 (KR1.4) and G2 (KR1.7). S1's needs are in the owner's words |
| O-7 | the AI model vanished, and a model trained on the past can't be tested on it | Accepted. The owner's design wishes are recorded for the architecture stage. KR6.3 bars models trained past the research window from G1's forecast. A model or prompt change is a new variant (KR6.1). Decision 9 explains |
| O-8 | the weekly improvement loop was dropped | Accepted. O8 sets a weekly review and requires every change to run 60 days on paper (KR8.1). A sequential live test halves, then stops, a fading strategy (KR8.2). The variant budget renews only on new data |
| O-9 | several KPPs couldn't be judged without guessing | Accepted: <ul><li>KR1.8 is a paired test of live minus modeled cost.</li><li>KR2.1 counts orders that would break a limit.</li><li>The halt is at 9%, so 10% is never reached (KR2.2, KR2.7).</li><li>The kill switch handles trapped positions (KR2.4).</li><li>The safe state is defined.</li><li>The daily loss counts from the previous close.</li></ul> |
| O-10 | decisions only the owner can make were missing | Accepted: <ul><li>decisions 5–10 cover the research budget, the reviewer, alert handling, extended hours, the AI model, and capital and taxes;</li><li>G3 needs at least $2,000 and whole-share shorts;</li><li>the pattern-day-trader note is updated (Alpaca dropped the rule on 2026-06-04);</li><li>network and data are listed as actions, not decisions.</li></ul> |
| O-11 | the goal didn't follow its own method | Accepted, changed. Every objective now has a KAOS kind and a GQM question, and GT-1 checks both. `METHOD.md` says GQM applies at the objective level, so the 37 key results carry no separate GQM fields; they would repeat the question. The return objective is stated as a return a year, with a risk objective. O5, KR4.2 and KR5.1 are split |
| O-12 | `GOAL.md` and `goal.toml` disagreed; numbers lived in prose | Accepted. KR5.1 and KR4.2 are split. KR6.2 belongs to every gate. The false-pass bounds are published. G2's window and trade deadline are defined. Order limits, the live test and costs moved into `goal.toml`, and GT-1 checks that `GOAL.md` shows every number in eight sections |

#### Risk limits, controls, broker mechanics, regulation (`reviews/risk-controls.md`)

| ID | Finding | Response |
|---|---|---|
| R-1 | stops don't bound jumps; one event could cost 2–6 times the daily limit | Accepted: <ul><li>positions sized for a 50% jump overnight and a 20% jump intraday: 4% overnight, 10% intraday;</li><li>any single jump, in one name or one industry, bounded at 4% (KR2.8);</li><li>8% per industry overnight;</li><li>15% beta-adjusted net, stressed with a 13% market gap;</li><li>no position through any scheduled company event;</li><li>GT-2 checks every jump against named events: Yahoo and NVIDIA in the data, SVB and the regional banks beyond it.</li></ul> |
| R-2 | the activity plan, size, volatility target, overnight caps and cost budget couldn't all hold; G1 not bound by the limits | Accepted. The plan is re-derived: 25 trades a week held 3 days at 4%, 20 slots (full 4.6% of the time), about 60% overnight, 0.2%/day volatility. GT-2 checks it by Little's law and Erlang's formula. G1's simulation must obey every limit (KR6.4) |
| R-3 | short-sale mechanics missing | Accepted, changed: <ul><li>no new short under Rule 201;</li><li>dividends charged on shorts;</li><li>no short over an ex-date of 0.5% or more;</li><li>a short that loses easy-to-borrow status is closed within 30 minutes of the next open;</li><li>G1 uses a historical borrowability proxy and a 0.5% borrow charge;</li><li>short interest at most 15% of the float, at most 5 days to cover.</li></ul> Not adopted: a separate 15% cap on overnight short gross. With 4% per name, the industry cap and the short-interest filters, it would only force the book net long |
| R-4 | corporate actions not mentioned; paper accounts don't apply splits | Accepted. No position through any corporate action other than an ordinary cash dividend. The calendar is checked before every order (C4). The equity of record is corrected for actions the paper account didn't apply |
| R-5 | controls compared the system's view with the broker's only at restarts and the close (Knight Capital's failure) | Accepted: <ul><li>open orders count in every limit (C1);</li><li>continuous reconciliation, with no blind resends (C5);</li><li>a second kill path, one instance, and the lowest margin multiplier (C6);</li><li>alert escalation, with entries stopped at 15 minutes and positions closed at 60 (C7);</li><li>a pre-open version check and a runbook (C8);</li><li>an API reserve (C3);</li><li>per-name and daily throttles (C13);</li><li>stops for the exact quantity, partial fills included (KR2.5).</li></ul> |
| R-6 | loss measurement undefined | Accepted. A measurement section defines the equity of record, marks, the daily loss from the previous close, the drawdown from the highest close, the time overnight limits are measured, and how long a passive excess may last before it counts. KR2.2 is split into "the halt fires" and "drawdown over the paper period". C1 nets the day's loss |
| R-7 | positions can't always be closed now | Accepted. A "trapped" position is defined, and KR2.4 and KR3.2 handle it. Gross is cut to the overnight limits after a market-wide halt. The second kill path covers outages. Extended hours stay closed unless the owner decides otherwise (decision 8) |
| R-8 | only limit prices collared; exits could be blocked; no clock rule; RTS 6 Art. 16 claimed but relaxed | Accepted: <ul><li>C2 rewritten: risk-increasing orders are collared and need a fresh, sane quote; risk-reducing orders are never blocked;</li><li>consolidated quotes are required from G2 on;</li><li>clocks within 50 ms of UTC (C14);</li><li>the RTS 6 deviation is stated in C7, and GT-7 reports it.</li></ul> |
| R-9 | liquidity is absolute, so "holds for any amount" was false | Accepted, changed. A position is at most 0.02% of its stock's daily volume, not the 0.1% proposed. By the square-root law of market impact, 0.02% keeps impact near the 1.5 bps the cost model charges (GT-3 checks it). An order is at most 10% of the volume while it works. G3 stops scaling when liquidity limits bind. The false claim is gone |
| R-10 | universe ambiguous (crypto trusts, volatility products, ADRs) | Accepted. The universe is defined by instrument type; ADRs are excluded |
| R-11 | no record retention, tamper evidence, key rotation or MFA | Accepted. Records are kept 5 years, append-only and hash-chained, off the host (C5). The trial log is written by the research system and timestamped outside the author's control (KR6.1). Keys rotate every 90 days, the account uses MFA, and an order the system didn't send triggers the kill switch (C11) |
| R-12 | facts about Alpaca out of date | Accepted. The pattern-day-trader rule is gone and FINRA's intraday margin rule applies. Easy-to-borrow status is a locate, not a borrow. The borrow fee for easy-to-borrow names is $0. Shorting needs $2,000 of equity. G3's capital must allow whole-share shorts |

#### Quantitative evidence and statistics (`reviews/quant-statistics.md`)

| ID | Finding | Response |
|---|---|---|
| Q-1 | G2 carried almost no evidence. Its two significance tests never bound; its loss-triggered extension passed 62% of no-edge strategies | Accepted, changed. G2 is redesigned: <ul><li>a window fixed in advance, with no extension: at least 120 days and 300 trades;</li><li>a paired fidelity test against a rerun of the frozen strategy (KR1.5, KR1.6);</li><li>a profit over the whole window (KR1.7).</li></ul> G2's false-pass rate is stated as it is, 50%, and G1 carries the evidence. The window is 120 days, not 60, so that "makes money" has at least 80% power at the target. The fidelity margin is 0.3 Sharpe units of the rerun's volatility, not 20% of G1's mean, so it doesn't depend on a noisy 120-day mean |
| Q-2 | the variant count N, now the main guard, was undefined and gameable | Accepted. G1 counts every variant ever evaluated on its history, never fewer than 10, and a missing count fails the gate. KR6.1's definition of a variant is widened. The research system writes the trial log itself. The "observed variance" option is deleted. Paper days used to diagnose a failed G2 become in-sample |
| Q-3 | a strategy driven by a language model can't pass G1 for years | Accepted. KR6.3 bars models trained past the window's start from G1's forecast. Decision 9 states that the forward route takes years |
| Q-4 | the live test's error rates were unstated and uncorrected | Accepted, changed. A sequential likelihood-ratio test of "no edge" against the target edge, capped so that a long good run can't hide decay. It stops at 12 to 1 and halves at 3 to 1, and capital grows only while it favors the edge. Its rates are tested in GT-4 (see the note below). H1 is the target Sharpe of 1.5, fixed in advance, rather than G1's deflated estimate |
| Q-5 | excess return let interest and overnight market exposure count as skill; KR1.3 used raw returns | Accepted. Interest is excluded. Betas are each position's, over its own holding interval, overnight and intraday apart. The overnight net limit is beta-adjusted. The stress series is in excess returns |
| Q-6 | nothing tested regime stability; 2007–09 not in the history | Accepted, changed. KR1.9 requires a Sharpe of at least 0.25 in each chronological half, and above zero on the calmer and the more turbulent days. The proposed 0.5 cost too much power when P&L is autocorrelated: G1's power fell to 75–81%, against 80% required. The missing 2008-like regime is stated, with the jump and drawdown limits as the protection |
| Q-7 | no point-in-time requirement; borrow proxy choosable afterwards; audit only above a Sharpe of 4 | Accepted. KR6.4 requires point-in-time, survivorship-free history with delisting returns, the borrow proxy registered with the variant, and a lag audit on every candidate: with inputs lagged one bar, the Sharpe keeps at least half its value and rises at most 10% |
| Q-8 | the information coefficients quoted were break-even, not the target; the cost budget conflicted with the stress | Accepted. `GOAL.md` shows both: 0.03 to break even at 3 days, 0.074 to reach the aim, a gross Sharpe of about 2.8. The Grinold and Kahn attribution is softened, since the reviewer could not verify it either, and MSCI Barra's "0.10 is very good" is cited. The cost budget falls to 4.5%, where G1's power still holds |
| Q-9 | the prior said nothing about edge size; G2's real false-pass rate unstated; the haircut too mild | Accepted. Real edges are uniform up to a Sharpe of 2, with a harsher case up to 1.25 for sensitivity. GT-8 requires P(real \| passed) ≥ 80% and P(worth running \| passed) ≥ 70%. G2's 50% is stated. Published effects count at most 42% |
| Q-10 | `GOAL.md` stale against `goal.toml` | Accepted. `GOAL.md` is regenerated as version 3, and GT-1 checks the two agree |
| Q-11 | gate inputs that were missing defaulted to passing | Accepted. A missing trial count, stress series, fill-model statement, rerun, trade deadline or lag audit now fails the gate |

**Note on the live test (Q-4).** The first targets were at most 10% false stops within 3 years and at
least 75% of dead strategies stopped within 3 years. They could not both hold under every noise shape;
fewer false stops means slower detection. The frontier, from 600 simulated runs of each case:

| Stop boundary | Real edge stopped by mistake within 3 years | Dead strategy halved within a year | Dead strategy stopped within 3 years |
|---|---|---|---|
| −2.25 (9.5 to 1) | 7–11% | 62–67% | 76–78% |
| −2.5 (12 to 1), chosen | 4–10% | 60–66% | 72–76% |
| −2.75 (16 to 1) | 3–8% | 63–66% | 68–72% |

Halving within the first year is the fast protection, and the drawdown halt is behind it. So the goal
takes −2.5 and states what it achieves, with margin for simulation noise:
- a real edge is stopped by mistake within 3 years at most 12% of the time;
- a dead strategy is halved within a year at least half the time;
- a dead strategy is stopped within 3 years at least 65% of the time.

## Version 3: results

All 387 checks pass (`results/goal.txt`). The figures that matter, across the four noise shapes:

| Test | Result |
|---|---|
| GT-1 | every statement verifiable, unambiguous, free of design, traced to one of 8 objectives; every objective has a goal kind and a question; `GOAL.md` agrees with `goal.toml` |
| GT-2 | <ul><li>**Stops:** every stop on one side, filling 25% worse, costs 1.88% against the 2% daily limit; both sides cost 2.5%, the worst-day bound.</li><li>**Jumps:** one position through its assumed jump costs 2.00% overnight or within the session; a total loss of one overnight position, or a 50% jump across an industry, costs 4%, the jump-loss bound; a 13% market gap costs 1.95%.</li><li>**The plan:** 15 positions open on average, and 20 slots are all full 4.6% of the time; 60% held overnight against a 75% limit; volatility 0.20%/day against a 0.2% budget; costs 4.2% a year against a 4.5% budget.</li></ul> |
| GT-3 | <ul><li>costs 8 bps against 6.95 bps published;</li><li>an IC of 0.096 needed at 2.5 hours, and 0.074 for the aim at the plan;</li><li>the target survives the cost stress at 0.84 against 0.5;</li><li>market impact at the liquidity limit is 1.2–2.4 bps against 1.5 charged.</li></ul> |
| GT-4 | <ul><li>**False passes:** G1 passes the best of 10 no-edge variants 0.10–0.76% of the time, against a 1% limit; a no-edge strategy reaches real money 0.05–0.33% of the time, against 0.5%.</li><li>**Power:** G1 passes the target 81.5–85.8% of the time and G2 82.5–85.3%, both against 80%.</li><li>**Fidelity:** the test never fails an honest implementation, and catches a one-Sharpe execution shortfall 90.5–95.2% of the time.</li><li>**Halts:** the 9% halt stops a real edge in at most 0.8% of years.</li><li>**Live test:** it stops a real edge by mistake within 3 years 3.6–9.0% of the time; it halves a dead strategy within a year 62–66% of the time and stops it within 3 years 73–76% of the time.</li></ul> |
| GT-5 | on real prices, G1 passes the best of 10 random strategies in 0 of 26 windows, balanced or always long; paper passes 42–44% of them, against the stated 50% |
| GT-6 | all 9 ways to game the goal are caught: by the risk limits (averaging down, no stops, big overnight longs or shorts), G1 (the best of 50, a look-ahead leak), or G2 (riding the market, padding trades, paper's generous fills) |
| GT-7 | all 29 items covered; one stated deviation, the 60-second alert instead of RTS 6's 5 seconds |
| GT-8 | <ul><li>a strategy that passes both gates has a real edge with probability 85%, and is worth running with probability 79%;</li><li>with real edges no larger than a Sharpe of 1.25, those fall to 63% and 40%;</li><li>the program reaches real money with a real edge at most 14% of the time;</li><li>a false edge reaches real money 0.33% of the time.</li></ul> |

GT-4 also maps how often a strategy passes both gates by its true Sharpe:

| True Sharpe | 0.5 | 0.75 | 1.0 | 1.25 | 1.5 | 1.75 | 2.0 |
|---|---|---|---|---|---|---|---|
| Passes both gates | 2% | 6% | 22% | 46% | 73% | 86% | 94% |

The gates are built to find edges near the target and above. A real edge with a Sharpe near 1, worth
running but no more, passes only about one time in five.

## What the tests can't show

- **Rule versus wording.** The gates are judged as `goaltests/gates.py` writes them. The tests check
  that the goal's rules do what they should, not that a future system will follow them. That is what
  the key results and the G2 inspections are for.
- **Simulation assumptions.** Simulated P&L follows four noise shapes. A real strategy's P&L may
  differ. The rates near their bounds (G1 power, the live test) have a few points of simulation noise.
- **Price data.** GT-5's real prices are daily and from five large technology stocks, not intraday or
  the whole universe.
- **Jump assumptions.** The jumps come from named events. A larger jump can happen. The goal bounds
  one by the jump-loss limit and accepts that it can exceed the daily limit.
- **The prior.** It is a judgment. GT-8 shows how the answer moves with it.
- **Control coverage.** GT-7 checks that every checklist item is claimed by a control, not that the
  control is enough. The independent review judged that.

## What remains for the owner

The ten decisions at the end of `GOAL.md`, each with a default. Before the API key is used:
- allow Alpaca's hosts in this environment's network settings;
- arrange consolidated market data;
- confirm the intraday history from 2016;
- keep the key out of the repository.

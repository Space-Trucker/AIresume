# Statistics review of the goal, version 4

- **Reviewer:** independent quantitative reviewer, Claude Opus 5.5 (`claude-opus-5-5`). No Fable model and no subagent was used.
- **Date:** 2026-10-15.
- **Evidence:** `GOAL.md`, `goal.toml`, `METHOD.md`, `TESTS.md` and `goaltests/`, and nothing else.
- **Runs:** `python3 -m goaltests` passes 418 of 418 checks. GT-4 took 742 s on this machine.
- **Reproductions:** a numpy re-implementation of the G1 rule, closed forms, and `goaltests.gates.sequential` with the goal's own numbers. Scripts and outputs are listed at the end.

## Summary verdict

**Not yet fit to govern G1. 22 findings: 1 blocking, 13 major, 8 minor.**

**What holds.** The core G1 device controls false passes from the variants it counts. That device is a Deflated Sharpe Ratio measured against the expected best of 20 no-edge Sharpe ratios, with a Newey-West correction and a cost stress. I reproduce the following:

- GT-4's power under AR(1) noise: 76.0% in 24,000 runs, against GT-4's 75.8% in 400 runs.
- G1's false pass: about 0.66% in 39,061 simulated programs, against the 1% bound.
- GT-8's 85%, 78%, 22%, 66% and 40%, exactly.
- The cost drag: 25 × 52 × 4% × 8 bps = 4.16% a year, which is 1.31 Sharpe units.
- The IC table.
- The live test's three stated bounds.

**What does not hold.**

1. **The power floor.** The 75% floor is not met once G1's own conditions are counted (S-1, blocking). It was also placed just under the measured value, after the result (S-2).
2. **The odds.** The 22% odds and the 85% posterior read the 5% prior in two incompatible ways (S-3). Per-gate power at a single edge size is the wrong target. On the goal's own model, a different budget or allocation does better on every program-level criterion (S-4).
3. **Hindsight.** The largest false-positive risk sits outside every number: the researcher already knows 2016–2026 (S-5).
4. **Rotation.** KR3.6 has 13–19% power at its 50-rotation minimum, and it fails the whole of G1 when it fails (S-6). The rotation margin is undefined at the start, prohibitive once measured, or set by the system itself (S-7). KR3.7 measures market drift rather than calibration (S-8).
5. **Paper and live tests.** G2's fidelity test rewards noise, and its power assumption contradicts KR1.6's own tolerance (S-9). The live test lets a strategy with no edge reach full capital within 3 years 23–28% of the time (S-10).
6. **Assumptions and claims.** The posterior bounds hold only under the most favorable edge-size prior (S-11). The 2-day "finding" about the edge horizon ignores the entry rule's selection of trades (S-12). The jump tier within the session treats a news halt as a 20% move (S-13). "What to expect" leaves out fixed costs, which exceed the expected return of the first real-money stage (S-14).

## Findings

### S-1 · blocking · G1's power leaves out conditions that G1 imposes; with them, the 75% floor is not met

**What GT-4 measures.** GT-4 judges G1 with the `dsr` rule in `gates.py`. That rule checks:

- the DSR;
- Sharpe ≥ 1;
- Sharpe ≥ 0.25 in each half;
- a profit;
- the cost stress;
- the Sharpe ceiling of 4.

The lag audit is passed in as `lag_audit_ok=True`. KR3.6 runs only when `rotations > 0`, and `gt04_power._g1_record` sets 0. GOAL.md's G1 row also requires KR3.7, KR1.9's split at the median VIX, and, for a strategy that rotates, KR3.6. None of these enters the 75.8%.

**KR3.7 alone, for a perfectly calibrated strategy at the target:**

- The plan's 25 round trips a week give 25 × 480 = 12,000 entries in 2,400 days, so 2,400 entries in the lowest fifth.
- Their expected gain is about 16.25 bps. The entry threshold is 16 bps and the plan's average is 17.2 bps (GT-3). The bar is half of that: 8.1 bps.
- The standard deviation of one trade over a 3-day hold is 168 × √3 = 291 bps raw, or 128 × √3 = 222 bps on residual returns (GT-2's 1.28% a day).
- The standard error is then 291/√2,400 = 5.94 bps raw, or 222/√2,400 = 4.53 bps residual. With a design effect of 1.5 for overlapping trades, it is 7.27 or 5.54 bps.
- P(fail) = Φ(−8.1/SE) = 8.6% or 3.6%, and 13.2% or 7.1% with the design effect.
- The lowest fifth correlates with the whole record at √0.2 = 0.45. Given that the strategy has passed the DSR, the failure rates fall to 5.1% or 1.8%, and 8.5% or 4.1% with the design effect (simulated in `kr37_cond_out.txt`).

**G1 power at the target under AR(1) noise, the binding case:** 0.760 (my 24,000 runs) × 0.915 to 0.982 = **0.695 to 0.745**. That is below 75% in every reading.

**Two further conditions can only lower it:**

- **The VIX split.** P(Sharpe estimate ≤ 0 in a half of 1,200 days) = Φ(−S/0.507). That is 0.15% if the half's Sharpe S is 1.5, and 2.4% if the turbulent half's Sharpe is 1.0.
- **The lag audit,** which GT-4 assumes always passes.

**A strategy that rotates:** multiply by KR3.6's pass rate of 0.13 to 0.72 (S-6). G1 power is then 0.10 to 0.55.

**GT-8 inherits the omission,** because its curve comes from the same G1 rule. So 22%, 85% and 78% are upper bounds even on the goal's own assumptions.

**Why this is blocking.** The goal states that "each gate should pass the targeted edge at least 75% of the time", and METHOD.md says the goal "is revised until every test passes". GT-4 passes only because it leaves out conditions that the goal imposes.

**Fix.**

- Add KR3.7, the VIX split and a lag-audit rule to `gates.py`, and simulate them in GT-4. KR3.7 needs a simulation at the level of trades.
- Redesign KR3.6 and KR3.7 so that noise alone cannot fail G1 (S-6, S-8).
- Then decide the floor or the budget again, on the complete gate.

### S-2 · major · The floor was fitted to the result, not fixed first

**The documents disagree with each other.**

- Decision 5 says: "The goal fixes the floor at 75% first, then takes the largest budget that keeps it: 20."
- GOAL.md's evaluation assumptions say: "It was 80% with a budget of 10 variants; the research budget doubled, and the bar rises with every variant counted."
- `goal.toml` says: `min_power = 0.75  # ... 5 points of power traded for twice as many ideas`.
- So the floor moved because the budget moved.
- TESTS.md still fails the goal when a gate passes the targeted edge "less than 80% of the time".

**The pattern repeats.** Twice the floor sits just under its own measurement: 80% against 81.5% with 10 variants, and 75% against 75.8% with 20 variants.

**GT-4 could not have shown the floor was met.** It uses 400 runs:

- The standard error is √(0.758 × 0.242 / 400) = 2.1 points.
- The 95% interval is 71.6% to 80.0%.
- 75.8% is only 0.37 standard errors above 75%.
- Telling 75.8% from 75.0% at 2 standard errors needs about 11,500 runs.

**With 24,000 runs (AR(1)), power by budget N is:**

| N | Power |
|---|---|
| 10 | 81.9% |
| 20 | 76.0% |
| 21 | 75.4% |
| 22 | 74.8% |
| 25 | 73.0% |
| 30 | 70.6% |

The standard error is 0.28 points. In closed form, with the cost stress included, the largest budget at an 80% floor is 14, and at 75% it is 21. So the budget of 20 comes from 4 stages × 5 variants, and the floor was then placed under it.

**The same pattern in the live test.** `min_dead_stop_3y = 0.65`, while GT-4's built-in default is 0.75. GT-4 measures 72–75%, so the default would fail in at least three of the four noise models.

**Fix.**

- Either derive the floor from a program-level objective that is fixed before any run (S-4), or state plainly that it is a judgment made together with the budget.
- Compute power in closed form or with at least 10,000 runs, report confidence intervals, and judge floors against the lower bound.
- Update TESTS.md.

### S-3 · major · The odds and the posterior use the 5% prior in two incompatible ways

**Two readings in one test.** GT-8 (`gt08_outside.py`) computes two numbers from the same 5% prior:

- **The posterior,** as π·P / (π·P + (1−π)·FP), with π = 5% and FP = 0.33%. Here FP is the chance that the best of 20 no-edge variants passes both gates. This treats 5% as the chance that *the program's* candidate is real.
- **The odds,** as (1 − 0.95^20)·P = 0.6415 × 0.35 = 22%. This treats 5% as an independent chance for each of 20 variants.

**Each reading, applied consistently** (AR(1), closed form, with the simulated false pass):

| What the 5% applies to | P(real money with a real edge) | P(real \| passes both) |
|---|---|---|
| Each of 20 variants, independently | 19.9% (22.4% under normal noise) | 99.4% |
| Each idea, using the minimum of 10 ideas × 2 variants (correlation within an idea from 0 to 1) | 12.5–15.6% | about 98.5% |
| The program as a whole | 0.05 × 0.311 = 1.6% | 83–85% |

"What to expect" pairs the posterior from the third row (85%) with the odds from the first row (22%).

**Which reading fits the outside view.** The base rate GT-8 cites is that fewer than 1% of day traders are reliably profitable. That is a rate per person, so per program, which is closest to the third row.

**The budget's justification depends on the reading.** The budget rule allows 10 ideas used twice. Then the odds are about 14%, which is version 3's "one in seven". Decision 5's rise from 14% to 22% needs 20 distinct ideas, which the rule does not require. Bug-fix re-runs also count as variants under KR6.1.

**Mixed noise models.** GT-8 takes its curve from normal noise, where power averaged over the prior is 0.35. Under AR(1), the binding case, it is 0.311, and the odds are 19.9%.

**Fix.**

- Define the prior per idea.
- State how variants of one idea correlate, and how the prior falls with an idea's rank.
- Compute the odds and the posterior from that one model, under the binding noise model.
- Replace "about one in five" with the consistent range: about 14% with 10 ideas, about 20% with 20 distinct ideas, on the goal's own prior.

### S-4 · major · Per-gate power at one edge size is the wrong criterion, and on the goal's own model another choice is better

**What the owner needs to know** is the program-level answer: the chance of reaching real money with a real edge, and how sure we are when it happens. Per-gate power at Sharpe 1.5 is neither.

**A number the goal never states.** A real edge exactly at the target passes both gates 63.5% of the time under AR(1) (75.8% × 83.8%, GT-4), or 69.5% under normal noise.

**The goal's own model, by budget** (AR(1), GT-8's formula, false pass from the same simulated histories for every N):

| Budget N | G1 power at target | G1 and G2 at target | G1 false pass | Posterior real / worth running | P(real money with a real edge), N distinct ideas |
|---|---|---|---|---|---|
| 10 | 81.8% | 67.3% | 0.48% | 88.1% / 81.6% | 13.6% |
| 20 | 75.8% | 62.4% | 0.57% | 85.2% / 80.3% | 19.9% |
| 30 | 70.3% | 57.8% | 0.46% | 86.7% / 82.7% | 22.6% |

**A budget of 30 beats 20 on every program-level criterion the goal states:**

- odds 2.7 points higher;
- posterior 1.5 points higher;
- worth running 2.4 points higher;
- a lower false pass.

It fails only the per-gate floor. Under normal noise the gap is wider: 22.4% against 26.1%.

**Distinct ideas matter more than variants.** At a fixed budget, the goal's own model says the number of distinct ideas drives the odds: 20 ideas × 1 variant give 19.9%, and 10 ideas × 2 variants give 12.5–15.6% (S-3).

**So the floor stands in for constraints the model leaves out:**

- the supply of genuinely distinct ideas;
- the 12-month limit;
- hindsight (S-5).

All three argue for fewer variants, not more. Because the model says nothing about them, neither the budget of 20 nor the floor is derived from it.

**Fix.**

- Replace "each gate ≥ 75%" with a program-level objective: maximize P(real money with net Sharpe ≥ 1), subject to P(no edge reaches real money) ≤ 0.5% and P(Sharpe ≥ 1 | pass) ≥ 70%.
- Compute it with a prior per idea that falls with the idea's rank, a stated correlation within an idea, and a hindsight sensitivity (S-5).
- Require distinct ideas rather than allowing pairs, for example at least 15 distinct ideas among the 20 variants.
- Keep per-gate power, and the joint G1-and-G2 power, as reported diagnostics.

### S-5 · major · The history is not out of sample for the researcher, and every false-pass number assumes it is

**The threat.** The builder and researcher are AI models whose training covers most of the G1 window, 2016–2026. The goal's own obstacle table says the builder "already knows the history". KR6.1 counts registered variants, but which ideas get registered is chosen from that memory first.

**How it changes the numbers.** Suppose that memory acts like M uncounted trials. Then the G1 false pass grows as 1 − (1 − q)^M, with q = 0.000335 per variant (my AR(1) simulation: 134 passes in 400,000 no-edge variants). GT-8's posterior falls with it:

| M | G1 false pass | No edge reaches real money | Posterior real (GT-8 formula) |
|---|---|---|---|
| 20 (as assumed) | 0.67% | 0.33% | 84.7% |
| 50 | 1.66% | 0.83% | 68.9% |
| 100 | 3.30% | 1.65% | 52.8% |
| 200 | 6.48% | 3.24% | 36.2% |
| 1,000 | 28.5% | 14.2% | 11.5% |

At M = 50, that is with only 30 ideas left uncounted, both the 0.5% real-money bound and the 80% posterior bound fail.

**Paper trading adds little.** It is the first data the researcher has not seen, but its likelihood ratio is only 0.84/0.50 ≈ 1.65: P(G2 pass) under the targeted edge against under no edge (GT-4). The obstacle table names the threat, yet the stated probabilities leave it out.

**Fix.**

- Start the KR8.2 sequential test on the first paper day, and carry its log-likelihood ratio into G3. Over 120 paper days the expected LLR is +0.54 under the target and −0.54 under no edge, with a standard deviation of 1.04.
- Require LLR ≥ 0 at the end of G2, or lengthen G2.
- State the false-pass and posterior claims as conditional on no uncounted search, and show them for M = 100 and M = 1,000.
- Consider counting ideas proposed with knowledge of the period at a multiple.

### S-6 · major · KR3.6 cannot tell a useful rotation rule from a useless one, fails G1 when it fails, and credits rotation with the exit rule's work

**The noise in one rotation.** A rotation's realized value is the new position's result less the replaced position's result to its planned exit. Take 3 days for the new position and about 1.5 days left on the old one:

- the standard deviation is 168 × √4.5 = 356 bps of the position raw, or 128 × √4.5 = 272 bps residual;
- the value the rule targets is at least one round-trip cost, 8 bps, and say 8–16 bps.

**The test's power.** The probability of passing "one-sided 90% lower bound > 0" is Φ(δ√n/σ − 1.2816):

| Rotations n | True value δ | Pass rate, raw | Pass rate, residual |
|---|---|---|---|
| 50 | 8 bps | 13% | 14% |
| 50 | 16 bps | 17% | 19% |
| 1,000 | 16 bps | 56% | 72% |

- A worthless rule passes 10% of the time. It passes more often when rotations on the same day share market moves, because `gates.py` uses an independent-trials standard error.
- 80% power needs (2.123σ/δ)² = 1,298 to 8,946 rotations.
- Only about 2.2 candidates a week meet a full book (GT-2), which is about 1,056 in 2,400 days.

**The code and the prose disagree on what failure means.**

- `gates.py` fails G1 when rotation doesn't clearly pay, and also when there are 1–49 rotations ("too few to judge").
- GOAL.md's Activity section says rotation "stays on only if it pays in G1", that is, it is switched off.
- **Under the code,** KR3.6 alone fails a strategy with a real edge and a useful rotation rule 28–87% of the time.
- **Under the prose,** the strategy deployed without rotation is not the one G1 judged, and G2's "rerun of the frozen G1 strategy" becomes ambiguous.
- Either way, the researcher's best response is never to rotate, because zero rotations skip the check. Decision 2's rotation is dead on arrival.

**The counterfactual flatters rotation.** The replaced position is followed "to its planned exit". The rule replaces the lowest-valued positions, whose expected remaining gain may be negative. If the system's own exit logic would have closed them anyway, rotation is credited with the value of that exit, an upward bias.

**On paper and live:**

- With 30 rotations, P(t < −1) at each independent look is 16% for a worthless rule and 11–13% for one worth 8–16 bps.
- Weekly looks over overlapping windows make this a random off-switch.
- Switching rotation off on paper changes the strategy relative to the frozen rerun (KR1.5, KR1.6). It is also a change under KR6.1 and KR8.1.
- The goal does not say how any of these is handled.

**Fix.**

- Make rotation a pre-registered nested comparison that cannot fail G1. Run the rotation-on and rotation-off paths, compare their daily P&L difference with standard errors robust to autocorrelation (HAC), and report the power at a realistic δ. Ship the off path unless the difference is significant.
- Follow replaced positions under the system's own exit rules, not to their planned exit.
- Treat any switch on paper or live as a registered change, and have the rerun apply it.
- Alternatively, keep rotation off until a dedicated study.

### S-7 · major · The rotation margin is undefined at the start, prohibitive once measured, self-set if read loosely, and KR3.5 does not check it

**The rule's wording** is "at least one standard deviation of the error such comparisons have shown on past rotations". Each reading of it fails:

- **At the start.** Before any rotation, there is no error to measure.
- **Measured on realized outcomes.** The error's standard deviation is about 272–356 bps of the position (S-6). That is 17–45 times the advantages at stake: 8–16 bps, where the whole entry threshold is 16 bps. No candidate clears it, so rotation never fires.
- **Read as the model's own forecast error.** The system then sets its own margin, which opens a route to gaming.

**KR3.5 checks only part of the rule.** It inspects the cost margin, the minimum hold, the caps and same-day re-entry. It does not check:

- this margin;
- the two consecutive evaluations;
- the condition on the 90th percentile of spread and volatility;
- the rule against closing and reopening the same name in the same direction;
- "lowest-valued first".

**Fix.**

- Define the margin as k times the forecast's standard error, as estimated by a registered model and audited in G1. Or drop it in favour of calibrated forecasts (S-8).
- List every clause of the rule in KR3.5.

### S-8 · major · KR3.7 measures market drift, not calibration; it is a point estimate; it checks the wrong tail

**It measures drift.** The metric is "realized gross gain over recorded expected gain", which is raw, not excess.

- Assume the market rose about 12–14% a year over 2016–2026 (my assumption). A long with a beta of 1 then gains (1.12 to 1.14)^(3/252) − 1 = 13.5–15.6 bps over a 3-day hold from drift alone.
- Compare that with a 16 bps expected gain at the threshold, and an 8.1 bps bar.
- A lowest fifth that is mostly long, with no skill, passes about Φ((14 − 8.1)/5.94) = 84% of the time.
- A lowest fifth that is mostly short, perfectly calibrated, passes about Φ((2 − 8.1)/5.94) = 15% of the time.

**It is a point estimate at 0.5.**

- A forecaster whose forecasts are inflated exactly twofold passes 50% of the time. Its trades at the threshold net zero after cost.
- One inflated fourfold passes Φ((4.1 − 8.1)/5.94) = 25% of the time.
- So the claim "so a trade at the entry threshold pays its cost" is not ensured.

**It checks the wrong tail.** It tests the lowest fifth. The inflation that rotation worries about is at the top: the highest of 1,000–2,000 forecasts, inflated by about 3 standard deviations (the expected maximum of 1,000 normal draws is 3.24). Nothing tests that tail.

**It is not in `gates.py` or in GT-4** (S-1).

**Fix.**

- Measure it on excess returns, using the goal's own beta adjustment.
- Test the calibration slope across forecast quintiles, with a one-sided bound sized for power. For example: the 90% lower bound of realized/expected in the lowest fifth is at least 0.5, with HAC errors.
- Add a check on the top decile, for the forecasts that drive rotation.
- Simulate it in GT-4.

### S-9 · major · G2's fidelity test rewards noise, and its power rests on an assumption that KR1.6's own tolerance contradicts

**The test's direction rewards noise.** `gates.py` fails KR1.5 only when the gap is significantly worse than −0.3 Sharpe (z < −1.645). More noise widens the standard error and makes passing easier.

**The assumed noise is too low for KR1.6's own tolerance.**

- The 15% implementation noise is assumed (`assumed_implementation_noise`), and GT-4 fixes `rerun_match = 0.98`.
- KR1.6 accepts 5% of the rerun's trades missing. With 15 open positions, that is 15 × 5% = 0.75 mismatched positions.
- Each has a daily P&L standard deviation of 4% × 168 = 6.7 bps raw, or 4% × 128 = 5.1 bps residual.
- The gap's standard deviation is then √0.75 × 6.7 = 5.8 bps, which is 29% of the 20 bps daily budget (22% residual).

**Power to catch a 1-Sharpe shortfall** (a mean gap of −20/√252 = −1.26 bps a day, against a margin of 0.3 × 20/√252 = 0.38 bps):

| Noise | Closed form | Simulated (GT-4's G2 builder, 4,000 runs) |
|---|---|---|
| 15% | 94% | 92.7% |
| 22.5% | 69% | 67.8% |
| 29% | 51% | 49.0% |

At KR1.6's boundary, the test falls well short of the goal's 80% requirement.

**KR1.6 counts in one direction only.** It counts the rerun's trades found on paper. Paper trades that the rerun didn't make are not counted. So an implementation that adds unintended trades passes KR1.6, and by adding noise it also makes KR1.5 easier to pass.

**Fix.**

- Measure the noise ν during G2, and run G2 until the test has 80% power at that noise: n ≥ ((1.645 + 0.842) × 20ν / (1.26 − 0.38))² = (56.4ν)². That is 72 days at 15%, 161 days at 22.5% and 267 days at 29%.
- Or recast KR1.5 as a non-inferiority test: pass only if the 95% lower bound of the gap is above −1 Sharpe.
- Make KR1.6 symmetric, matching trades over the union of both logs, with a stated tolerance for time and size.
- Simulate the match rate in GT-4.

### S-10 · major · The live test and the capital schedule let a strategy with no edge run real capital for years

**Set-up.** `gates.sequential` with the goal's [live] numbers, 2,000 three-year runs per case. Capital:

- starts at 10% of the intended amount;
- doubles at each 60-day checkpoint whose latest monthly look allows growth (LLR ≥ 0);
- halves at each look at or below −1.1.

Results are in `live_test_out.txt`. Each cell shows normal noise / AR(1) noise.

| True net excess Sharpe | Stopped within 3 years | Halved within 1 year | Full capital within 3 years | Mean capital at 1 year |
|---|---|---|---|---|
| 1.5 (target) | 5.0% / 8.5% | 16.6% / 21.9% | 86% / 82% | 69% / 66% |
| 1.0 | 18.5% / 24.2% | 30.6% / 38.3% | 67% / 64% | 54% / 50% |
| 0.75 | 30.0% / 32.7% | 36.5% / 42.1% | 58% / 57% | 48% / 46% |
| 0 (no edge) | 75.1% / 73.6% | 64.1% / 62.6% | 23% / 28% | 26% / 28% |

**What this shows:**

- The goal's three stated bounds hold.
- But a strategy with no edge reaches full capital within 3 years 23–28% of the time.
- The test's log-likelihood drifts each day by sr₁·s/√252 − sr₁²/2, with sr₁ = 1.5/√252. That drift is zero at s = 0.75, so capital grows for strategies below the Sharpe of 1.0 that the goal calls worth running.
- The goal does not report the chance of halving the targeted edge within a year (17–22%).
- At the first step, P(grow at day 60) is 64% under the target and 36% under no edge, a likelihood ratio of only 1.8.
- One point is ambiguous: does capital halve once per crossing of −1.1, or at every look below it?

**An alternative: grow only at LLR ≥ ln 3 = 1.1** (`live_test_alt_out.txt`):

- a strategy with no edge reaches full capital 7–12% of the time, with a mean capital of 9–11% at 1 year;
- the targeted edge reaches full capital within 3 years 70–73% of the time, with a median of day 480 instead of 300.

**Fix.**

- Start the test on the first paper day (S-5).
- Grow only at LLR ≥ ln 3, or test H0: Sharpe 0.5 against H1: Sharpe 1.5, so that the indifference point is 1.0.
- Report the false-halve rate.
- Define halving per crossing.

### S-11 · major · The edge-size prior is the most favorable one considered, and the posterior criteria fail under plausible alternatives

**Why uniform up to 2 is generous.** A uniform prior on (0, 2] puts half of all real edges at a net Sharpe of 1 or more. Under the goal's own McLean–Pontiff multiplier (0.42) and cost drag (1.31), a published effect nets a Sharpe of 1 only if its in-sample gross Sharpe is (1 + 1.31)/0.42 = 5.5.

**The posterior under other priors** (GT-8's formula, AR(1), N = 20, simulated false pass, from `priors_out.txt`):

| Prior over real edges | P(real \| pass) | P(worth running \| pass) |
|---|---|---|
| Uniform (0, 2], the goal's | 85.2% | 80.3% |
| Exponential, mean 0.75 (26% of edges ≥ 1) | 76.5% | 69.4% |
| Uniform (0, 1.25], GT-8's "harsh" case | 61.1% | 40.3% |
| Exponential, mean 0.5 (13.5% of edges ≥ 1) | 61.3% | 51.0% |

Both bounds (80% and 70%) fail under every alternative shown.

**The multiplier is decorative.** `published_edge_multiplier` enters no calculation; GT-8 only checks that it is at most 0.42.

**Fix.**

- Justify the prior from the reference class.
- Make the posterior bounds hold under a central prior. If they don't, tighten G1 or extend G2 or the capital staging.
- Use the multiplier where ideas' priors are set, or remove it.

### S-12 · major · The 2-day edge horizon and "IC about 0.07" rest on arithmetic that ignores the entry rule's selection

**The model mismatch.** GT-3 converts IC to gain per trade with √(2/π) = 0.80, which assumes a bet on every forecast's sign. The entry rule trades only forecasts whose expected gain is at least twice the cost, that is, the tail. In GT-3's own joint-normal model, E[r | z] = IC·σ·z.

**At 3 days.** Pick the planned 25 trades from about 7,500 stock-days a week (my assumption: 1,500 names):

- that means |z| > 2.94, with a mean |z| of 3.22;
- so 17.2 bps a trade at 3 days (σ = 290 bps) needs IC = 17.2/(290 × 3.22) = 0.018, not 0.074.

**At 2.5 hours.** σ = 168 × √(150/390) = 104 bps.

- A "great" IC of 0.10 clears the 16 bps entry bar whenever |z| ≥ 16/(0.10 × 104) = 1.54.
- That is 12.5% of stock-windows, not "from about 1.4 trading days".

**What this means.** The 2-day conclusion may still be right: signals' tails may decay, and short-horizon effects are crowded and costlier in practice. But GT-3 does not show it, and GOAL.md calls it "a finding".

**The plan sits just above the entry bar.**

- A calibrated strategy at the planned activity that obeys the entry rule earns at least (16 − 8) bps × 1,300 × 4% = 4.16% a year, a Sharpe of at least 1.31.
- So the "minimum" Sharpe of 1.0, which is 14.1 bps a trade (GT-3), implies forecasts inflated by at least 13%.

**Fix.**

- Derive the horizon from tail-conditional returns, meaning the realized gain by forecast decile on training data. Or restate decision 3 as a judgment drawn from the literature.
- Replace "IC 0.07" with the gain per trade needed (about 17 bps at 3 days) and the breadth assumed.

### S-13 · major · Jump tiers: a news halt in the session is treated as a 20% move, the tiers come from five mega-caps, and the overnight net limit trusts 252-day betas

**A news halt is not a 20% move.** The 10% cap within the session rests on "a jump of 20% within the session (a news halt, or two 10% price bands)". But a news-pending halt during the session reopens at the post-news price, exactly as an overnight gap does. It is the same takeover that sets the 50% overnight tier.

- A 10% position through a 50% reopen loses 10% × 50% = 5%. That is above KR2.8's 4% and KR2.3's 2.5%.
- An event-prone biotech short is capped at 2% overnight but may be 10% within the session. Through a 100% reopen it loses 10% × 100% = 10%.
- A 10% position that is halted and never reopens, as SVB was, loses 10%.

**The tiers rest on a thin sample.**

- The 50% stock tier is the largest gap among five large technology stocks, 1999–2014 (TESTS.md), plus named events.
- The universe ($5 and up, $20M a day) includes small and mid caps, where takeover premiums above 50% are common enough that a five-stock maximum is not a tail estimate.
- A 4% short through a +100% bid loses 4%, which is the whole jump-loss bound.

**The overnight net limit is adjusted by beta only.**

- Take longs of 50% at beta 0.5 and shorts of 25% at beta 1.5.
- The beta-weighted net is 25 − 37.5 = −12.5%, which is allowed. The dollar net is +25%.
- If betas move toward 1 in a 13% gap, the loss is about 25% × 13% = 3.25%.

**Fix.**

- Measure the distributions of overnight gaps and of reopenings after halts from the G1 universe, by tier and direction.
- Apply the event-prone and jump caps within the session as well, or cap any single name at 4–5% at all times.
- Add a dollar-net overnight limit, or stress betas toward 1.
- Restate KR2.8 as a frequency bound if a certainty cannot be met.

### S-14 · major · "What to expect" omits fixed costs, the cash hurdle and the first stage's scale

**Fixed costs.**

- The $99-a-month data plan costs $1,188 a year, from G2 on.
- That is 1.19% of $100,000, or 0.37 Sharpe units at the volatility budget of 3.17% a year.
- The review panel and the paid human review come on top.

**Break-even capital for the data plan alone:**

- $1,188 / (1.0 × 3.17%) = $37,400 at a Sharpe of 1.0;
- $25,000 at a Sharpe of 1.5.

**The first real-money step.** At decision 10's minimum for faithful sizes ($12,500–25,000), it earns $400–1,190 a year at Sharpe 1.0–1.5. That is at or below the data fee.

**The cash hurdle.** The minimum target of 3.2% a year is measured with no risk-free rate subtracted. If idle cash and short proceeds earn nothing at the broker, any cash yield above about 3% beats it.

**Taxes.** US short-term gains are taxed as ordinary income.

**Fix.**

- State expected results net of fixed costs at each capital stage.
- Set the minimum intended capital at which the program is worth running.
- State the cash-yield hurdle.

### S-15 · minor · The drawdown-room rule: the restart after a halt is undefined, and its cost isn't counted

**How positions shrink.** At drawdown d, the worst single event must be at most 9.5 − d. So an overnight stock may be:

- 4% up to d = 5.5%;
- 2.5% at 7%;
- 0.5% at 9%, one eighth of full size.

**The restart.** If the peak is not reset when the owner restarts after a halt, the book trades at (9.5 − d)/4 of full size. At the targeted edge of 4.76% a year, the expected climb from 9% back to 5.5% takes ln 8 / (4.76%/4 per point) ≈ 1.75 years.

**Not counted anywhere.** Neither GT-4's halt check nor "What to expect" includes the rule. GT-2's check of the rule is tautological (S-22).

**Fix.**

- Define the restart: a peak reset, or a fresh drawdown budget.
- Simulate the rule in GT-4's halt check and in the expected returns.

### S-16 · minor · G2's pass probability ignores about 20 zero-tolerance operational key results, and there is no restart rule

**Zero tolerance over a long window.** G2 requires "every O2–O7 key result met". That includes results that must have no defects over at least 120 days, for example KR2.1, KR3.1, KR3.2, KR3.5, KR4.3, KR5.1–5.3, KR7.1 and KR7.3.

- If 20 such results each fail on 0.1% of days, P(all pass) = 0.999^(20 × 120) = 9%.
- At 0.01% of days, it is 79%.
- GT-4's 84% G2 power counts none of them.

**No restart rule.** After an operational failure, the goal doesn't say whether G2 restarts with the same strategy without using up a variant.

**Fix.**

- Classify breaches as disqualifying or remediable.
- Define a restart that keeps the G1 evidence when the strategy is unchanged.

### S-17 · minor · Contradictions between and within the documents

- **Stale thresholds in TESTS.md.** It says GT-4 fails at power below 80%, and GT-5 fails at a G1 false pass above 5% and a G2 false pass above 20%. `goal.toml` and the code use 75%, 1% and 50%.
- **Stale status in `goal.toml`.** [meta] says the goal was "revised after ... an independent review of version 2; awaiting the owner's decisions". GOAL.md says version 4 "settles the open decisions".
- **Rotation that does not pay.** GOAL.md switches it off; `gates.py` fails G1 (S-6).
- **The floor.** Decision 5 says the floor was fixed first; the evaluation assumptions tell a different story (S-2).
- **KPP status.** KR1.3, KR1.9, KR3.6 and KR3.7 are not KPP, yet each fails G1.
  - KR1.3 is in fact the binding G1 condition under normal noise for N ≤ 22.
  - It needs a realized Sharpe of 0.5 + 0.5 × 0.017/0.2 × √252 = 1.175, which the targeted edge reaches 84.2% of the time.
- **The VIX split.** KR1.9's split appears in the key result, but not in the G1 rule or in `gates.py`.
- **KR1.2's "minimum" Sharpe of 1.0 never binds.**
  - The stress needs 1.175, and the DSR needs about 1.16 under normal noise to 1.25 under AR(1).
  - An edge of exactly 1.0 passes both gates 24% of the time (GT-4's curve).

**Fix.**

- Align TESTS.md, [meta] and GOAL.md.
- Put every G1 condition in the G1 rule.
- Make KPP mean "fails its gate".

### S-18 · minor · GT-5 cannot test a 1% false-pass rate

**Evidence.**

- GT-5 uses 26 windows of 2,400 days, 63 days apart, inside 4,011 days.
- Neighbouring windows share (2,400 − 63)/2,400 = 97% of their days.
- The whole span holds only 4,011/2,400 = 1.7 independent windows.
- So "0/26 = 0%" is compatible with almost any rate.
- Even 26 independent windows would give a 95% upper bound of 1 − 0.05^(1/26) = 10.9%.

**Fix.**

- Present GT-5 as a smoke test.
- Take G1's false pass from simulation, with confidence intervals.

### S-19 · minor · Newey-West with a fixed 5 lags under-corrects, and its noise adds to the false pass

**Under AR(1) with ρ = 0.1:**

- NW(5) with Bartlett weights is 1 + 2Σ(1 − k/6)·0.1^k = 1.181, against the true 1.222.
- The simulated G1 false pass with the estimated factor is about 0.66% (259 of 39,061 programs, pooling GT-4's runs and mine).
- With the true factor it is about 0.5%.

**Under ρ = 0.2:**

- NW(5) is 1.396 against the true 1.500.
- The effective bar is 3.42 standard deviations instead of 3.55.
- The false pass is about 0.62% with the factor at its expected value, before any estimation noise. Under AR(1) 0.1, estimation noise raised the rate from about 0.5% to 0.66%; a similar rise here would bring it close to the 1% bound.

**One reassurance:** judging "any of the 20 passes" instead of the best gives the same rate (98 = 98 in 12,000).

**Fix.**

- Use an automatic bandwidth (about 4(n/100)^(2/9) = 8 lags for 2,400 days) or a block bootstrap.
- Report the false pass with its interval.

### S-20 · minor · KR1.8's live-cost check is one-shot and blind to position size

**Evidence.**

- Square-root impact at the liquidity cap (0.02% of daily volume) is 0.5–1 × 168 × √0.0002 = 1.2–2.4 bps a side.
- At a tenth of that size it is 0.4–0.75 bps.
- So 300 round trips at the first step's small sizes understate full-size costs by 1.6–3.3 bps a round trip. That is 20–40% of the 8 bps model.
- KR1.8 passes unless excess cost is significant, so it would pass.
- The scaling rule says "live costs match the model" without saying over which trades.

**Fix.**

- Re-test KR1.8 on the latest 300 round trips at the current size before each doubling.
- Include a term for size.

### S-21 · minor · The lag audit has no error model, and "bar" is undefined

**Evidence.** The rule is: "With every input lagged one more bar, the net Sharpe keeps at least half its value and rises no more than 10%."

- On daily bars, one bar is a day, which can legitimately halve the Sharpe of a 2-day signal.
- Reversal signals often improve when lagged, because there is less bid-ask bounce.
- A failure voids the run (KR6.4, KPP), and GT-4 assumes the audit always passes.

**Fix.**

- Define the bar as one minute.
- Express both thresholds in standard errors of the paired Sharpe difference.

### S-22 · minor · Several tests judge the goal by itself

**Evidence.**

- **GT-2's drawdown check is tautological.** It sets allowed = min(worst, 10 − 0.5 − 9), then tests 9 + allowed ≤ 10, which is true whenever a margin exists.
- **GT-6's churning probe is caught by construction.**
  - It subtracts its own sample mean and 0.2 bp, so its mean is exactly −0.2 bp of equity.
  - Its noise is 2 bps of equity per rotation, against a realistic 356 bps × 4% ≈ 14 bps.
  - With realistic noise, the same probe passes KR3.6 8.4% of the time with 50 rotations, and 5.9% with 400.
- **GT-6's look-ahead probe** is caught by the Sharpe ceiling of 4 and by a hand-set `lag_audit_ok=False`. A leak that produced a Sharpe of 2.5 would be caught only by the lag audit, which no test exercises.
- **GT-4's fidelity power** uses the goal's own assumed noise (15%) and match rate (98%) (S-9).

**Fix.**

- Replace the tautological check with a simulation.
- Draw probe noise from realistic sizes, and report pass rates rather than a single run.
- Test the lag audit on a planted leak below the ceiling.

## Reproduction

All files are in `/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/stats/`.

| Files | What they reproduce |
|---|---|
| `full_run.txt`, `full_results.json` | The goal tests as shipped (418/418 pass) |
| `g1_sim.py`, `g1_sweep.py` → `sweep_ar1.txt`, `sweep_ar1_b.txt`, `sweep_normal.txt` | A numpy re-implementation of the `gates.py` G1 rule: power and false pass by budget and DSR threshold, 12,000 runs each |
| `g1_any.py` → `any_ar1.txt`, and `diag_ar1.py` | The program-level false pass, and the false pass with the true long-run variance factor |
| `analytic.py`, `program_level.py`, `program_level2.py`, `priors.py`, `ideas.py`, `extras.py`, `kr37_cond.py` → `*_out.txt` | The closed forms behind S-1 to S-6, S-8, S-11, S-12, S-14 and S-15 |
| `live_test.py`, `live_test_alt.py` → `live_test_out.txt`, `live_test_alt_out.txt` | The sequential test and the capital staging (S-10) |
| `fidelity_check.py` | KR1.5 at higher noise, with GT-4's own record builder (S-9) |

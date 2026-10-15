# GT-9 review: quantitative evidence and statistics

An independent reviewer was given `METHOD.md`, `GOAL.md`, `goal.toml`, and the gate definitions
(`goaltests/gates.py`, `goaltests/stats.py`). The reviewer did not see the other tests or their
results. The goal was being revised while the review ran, so the findings are against the state at
02:35 UTC on 2026-10-15, between commits `8cb9382` and the next. The reviewer simulated the gate code
directly. This is the reviewer's report, lightly condensed. The response to each finding is in
`REPORT.md`.

Fixed by the revision already in flight, relative to the reviewer's first read:
- KR1.2 is enforced in the gate.
- Effective observations are counted under autocorrelation.
- The trial variance is the null variance.
- KR1.3's text and rule agree.
- The activity plan fits the overnight limits.
- Dividends are charged on shorts.
- G1 uses a historical borrow proxy.
- KR1.8 is a paired test.
- The excess-return benchmark is named.
- G1's false-pass bound is 1%.

## Findings

**Q-1 (blocker). G2 carries almost no evidence about the edge, but it is presented as confirming G1.**
- **Combined PSR (KR1.5).** About 2,250 history days swamp about 60 paper days. After a G1 pass, the
  combined PSR falls below 0.99 only if the paper Sharpe is below about −10. Removing KR1.5 changed 0
  of 15,000 simulated outcomes.
- **Shortfall test (KR1.6).** It can bind only for claims above a Sharpe of 2.4–3.4. Removing it
  changed 0 of 15,000.
- **What actually decides G2.** Only "paper excess return above zero over 60 days, extended to 120
  only after a loss" decides it, and that is optional stopping. A no-edge strategy passes 62.5% of the
  time, against the stated 20%. One at the target passes 90% of the time, a likelihood ratio of only
  1.44.
- **Why.** Over 60 or 120 days, the standard error of an annualized Sharpe is 2.05 or 1.45. Proving a
  Sharpe of 1.5 against zero takes about 305 days at 95% confidence, and about 690 days with 80% power.
- **Power.** Joint power at the target is 0.82 × 0.90 = 0.74.

Proposed:
- **(a)** A paired fidelity test. Rerun the frozen G1 code on each paper day's data. The mean daily gap
  between paper and the rerun must not be significantly negative beyond a pre-registered margin, and at
  least 95% of the rerun's round trips must appear in paper.
- **(b)** A paper window fixed in advance: 60 days and 300 trades, capped at 150 days, with no
  loss-triggered extension.
- **(c)** `max_false_pass_g2` set to the rule's real rate, with G1's bound re-derived from it.
- **(d)** A sequential live test (Q-4).

**Q-2 (blocker). The trial count N is undefined and gameable.** With G2 uninformative, N is the only
guard against false real money.
- The code treats N as a running count, defaulting to 1.
- KR6.1's "variant" leaves out:
  - features and input data;
  - the cost, fill and borrow-proxy models;
  - the walk-forward schedule and the beta method;
  - re-runs after bug fixes;
  - exploratory looks.
- Up to four cycles reuse the same out-of-sample days.
- The optional "observed" trial variance collapses the hurdle when variants are near-duplicates.

| Scenario | G1 false-pass rate |
|---|---|
| Honest, N fixed at 10 | 0.30–0.43% |
| 20 unlogged looks, then 10 registered near-duplicates | 1.1–3.7% |
| 100 unlogged looks, same | 7.3–14.3% |

Proposed:
- N is every variant ever evaluated on this history, never below the assumed 10, and the same at every
  evaluation; it is a required input.
- Widen the definition of a variant.
- The backtester writes the trial log itself: append-only, hashed.
- Delete the "observed" option.
- Paper days used to diagnose a G2 failure become in-sample.

**Q-3 (major). A strategy whose forecast uses a current language model can't pass G1 for years.**

KR6.3 is right: a model counts only after its training cutoff. Combined with the 2,250-day minimum, a
2025–2026 cutoff leaves 80–450 usable days, and power at a Sharpe of 1.5 is then about 4%.

Proposed:
- Either G1's return forecast may use no model trained after the out-of-sample window starts (models
  may still serve monitoring and operations),
- or a forward-test route with sequential boundaries, which takes more than a year.

**Q-4 (major). The live retirement test has unstated error rates.**
- It tests against G1's raw estimate, which is inflated by selection.
- It looks 12 times a year with no correction for the repeated looks.
- Its null is "as good as claimed", not "worth running".
- Capital may double just because no halving has fired.

| True edge | Halved within 3 years | Stopped within 3 years |
|---|---|---|
| exactly as claimed | 25% | 7% |
| edge gone | 94% | 78% (median 84 days to the first halving) |

Proposed:
- A pre-registered sequential test of "no edge" or "not worth running" against G1's deflated estimate,
  with boundaries that spread the error budget over the monthly looks.
- Doubling only after the test favors the edge.
- The designed rates stated.

**Q-5 (major). Gaps remain in the definition of excess return.**
- Interest on cash and short proceeds is not excluded. At the 3.2% volatility budget, 3–4% interest
  adds 0.95–1.26 to the Sharpe.
- A single close-to-close beta counts an overnight market tilt as skill: a true Sharpe of 1.0 measures
  1.06–1.15 (Cliff, Cooper and Gulen; Lou, Polk and Skouras).
- Market timing counts as alpha.
- The overnight net limit has no defined beta.
- KR1.3 is computed on raw returns.

Proposed:
- Exclude interest.
- Use betas over each position's actual holding interval, overnight and intraday separately: each
  name's 252-day beta as of the prior close.
- Compute KR1.3 on excess returns.

**Q-6 (major). Nothing tests whether the edge holds across regimes.**

An edge present only on the most volatile quarter of days passes G1 74.5% of the time at low turnover,
and reversal returns rise with the VIX (Nagel 2012). Alpaca's consolidated history starts on
2016-01-01: about 2,711 days, covering 2018, 2020, 2022 and 2025, but not 2007–09.

Proposed:
- A net excess Sharpe of at least 0.5 in each chronological half, and in each half split at the median
  VIX, at a cost of about 5 points of power.
- State that 2007–09 is missing.

**Q-7 (major). Data integrity has gaps.**
- No point-in-time, survivorship-free requirement.
- A borrow proxy that can be chosen after seeing results.
- A look-ahead audit only above a Sharpe of 4, so leaks worth +1 Sharpe go unaudited.

Proposed:
- A data-integrity KPP.
- The borrow proxy registered with the variant.
- A one-bar-lag audit on every candidate: results must not improve when every input lags one more
  bar.

**Q-8 (major). The information coefficients quoted are break-even values, not what the target needs.**
- The target needs about twice as much: IC 0.07–0.09 at 2–3 days, a gross Sharpe of about 2–3.
- The plan's costs take about 1.35 Sharpe units. At the 6% cost budget they take 1.89, so the cost
  stress implies a net Sharpe of at least 1.45, and power at the target drops to about 56%.
- MSCI Barra calls an IC of 0.10 "very good". The "0.15, too good to be true" attribution to Grinold
  and Kahn could not be verified.

Proposed:
- Restate the paragraph.
- Cap the cost budget near the plan, or state the power at the budget.

**Q-9 (major). The prior says nothing about the size of the edge.**

By program-level simulation through the gate code, P(true Sharpe ≥ 1 | reached G3) is:

| Prior on the size of a real edge | P(true Sharpe ≥ 1 \| reached G3) |
|---|---|
| exactly 1.5 | 0.997 |
| uniform on 0.25–2 | 0.93 |
| uniform on 0.25–1.25 | 0.64 |
| with 90 unlogged looks | 0.54–0.88 |

- P(reaching G3) is 7–32%.
- G2's real false-pass rate is 0.62, so G1 at its 1% bound gives 0.62% false real money, above the
  0.5% limit.
- McLean and Pontiff's 58% decline leaves 42% of a published effect, less than the 0.5 the goal uses.

Proposed:
- A prior over edge sizes.
- P(Sharpe ≥ 1 | G1 and G2) ≥ 0.8 by simulation.
- G2's real false-pass rate.
- A published-effect multiplier of 0.42 or less.

**Q-10 (major). GOAL.md (01:54) disagreed with goal.toml (02:35) on more than 20 numbers and on the key
result numbering.**

Proposed: regenerate GOAL.md, bump the version, and make a passing GT-1 a precondition for the owner's
review.

**Q-11 (minor). The gate code passes when an input is missing, instead of failing.**
- The trial count defaults to 1.
- A missing stress series skips KR1.3, overstating power from 0.82 to 0.90.
- Conservative fills default to true.
- A missing claim skips KR1.6.
- Days to the minimum trades default to 0.

Proposed: every input a rule uses is required.

## Reviewer's overall judgment

"Not yet ready on its evidence side (O1, O6, G1–G3), but close." The structure is sound, and G1 as
coded has about 82% power at a Sharpe of 1.5 with a 0.3–0.4% no-edge false-pass rate, if the trial count
is honest. Two blockers remain: G2 gives no evidence about the edge, and the trial count is undefined.
Both are fixable with small, concrete changes.

The owner should be told:
- roughly a one-in-five to one-in-three chance of reaching G3 within budget;
- a gross Sharpe of about 2–3 needed at the planned turnover;
- about 2,700 days of history, enough for G1 but with no holdout and no 2007–09;
- one to two years to confirm the edge live;
- an edge driven by a pre-trained language model can't pass G1 for years.

The control and operations objectives are not blocked.

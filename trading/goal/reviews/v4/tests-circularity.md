# Are the goal tests circular? Review of goaltests for goal version 4

Independent review, 2026-10-15, by Claude (Opus 5.5; no Fable model used). It covers commit `18e3e74`
(goal version 4). File and line references are to that commit. I read only `goal.toml`,
`goal_v1.toml`, `GOAL.md`, `METHOD.md`, `TESTS.md` and `goaltests/`. I did not open `REPORT.md`, the other
reviews, `../reports/`, `../research_notes/`, `results/` or any transcript. Nothing in the repository was
changed except this file. The goal copies and mutants lived in the scratch directory. The test code
ran first from the repository, read-only and with bytecode writing turned off, and then from a frozen
copy (see step 6 below).

## Summary verdict

**Not yet non-circular in the owner's sense.**

The answers mostly come from outside the goal:

- simulated track records whose edge is set by construction;
- random entries on real prices;
- real overnight gaps;
- published fees;
- the square-root law of market impact.

That part is sound.

The verdicts mostly do not. Of the 418 checks, only 13 (3%) take both the right answer and the
pass/fail bar from outside the goal, and 309 (74%) are presence or wording checks. The rest fall into
four groups:

- **Statistical bars set by the goal.** In GT-4, GT-5 and GT-8 the bar that decides pass or fail is the
  goal's own number (T-1). Three of those bars sit just on the passing side of results the goal already had: G1
  power at 75%, against 75.8% measured; G2 passing random strategies at 50%, against 42% and 44%; and
  stopping a dead strategy at 65%, against 72–75% (T-2). Under the bars TESTS.md itself documents (80%
  power, 20% for G2), or the code's own default for the dead-strategy bar (75%), the goal fails.
- **A tautology.** GT-2's drawdown-room check passes by construction once a key exists (T-3).
- **A self-declared map.** GT-7's coverage is the goal's own `covers` list (T-5).
- **An outside view from the goal's own prior.** GT-8 is computed from the goal's prior and edge-size
  prior, not from the base rates it cites (T-4).

Mutation testing makes the same point. Of 56 single-defect mutants, the suite detects 19 and misses 36;
one more fails a check only by chance.

It catches large changes to:

- the risk numbers;
- the cost model;
- the planned horizon;
- the live test's stop.

It misses:

- **contradictions between sections:** a daily limit above the worst-day bound; 3x leverage while the
  text says 100%; 20-day holds; a halt at the drawdown line itself; a 10% single-jump bound;
- **loosened bars and priors:** a 20% false-pass tolerance; a 50% prior;
- **unanchored assumptions:** no cost stress at all; a 5% intraday jump;
- **G1 judged on raw profit;**
- **edits the tests read only as presence:** a hollowed kill-switch control; a deleted key result;
  100 rotations a day.

The most serious findings:

- **T-1 to T-4 (blocking):** bars and priors taken from the goal; bars moved to the results; the
  drawdown tautology; an outside view without outside data.
- **T-7:** the live test, in the decay case its cap was designed for, misses both of the goal's own
  bars (halves capital within a year 25% of the time against 50%; stops within 3 years 50% against
  65%), and GT-4 never simulates that case.
- **T-9:** the capacity check passes only because it assumes the least risk per position; at the
  plan's own 0.13% the book is full 18% of the time, against a 10% bar.

## How the review was done

1. **Baseline.** Full suite on an unmodified copy: 418 of 418 checks pass, and GT-4 took 584 s on a
   shared 4-CPU machine. A thin wrapper that calls each test module's `run()` exactly as `__main__.py`
   does, but saves GT-4's context, reproduced GT-4, GT-5 and GT-8 identically.
2. **Mutants.** 56 single-defect copies of goal.toml. Each sits in its own folder as `goal.toml` beside
   an unchanged `GOAL.md`, so GT-1's GOAL.md checks run as they would after a real edit. Every edit was
   asserted to match exactly once, and every mutant parses.
3. **Fast tests.** I ran the fast tests (`--only 1,2,3,6,7,8`) on every mutant and diffed the results
   against the baseline's fast run. GT-8 needs GT-4's results, and without them it fails even the
   unmodified goal, so I also scored GT-8 for every mutant against the baseline's GT-4 context. That is
   valid for mutants that change no GT-4 input.
4. **Slow tests.** GT-4, with GT-8 on that run's own GT-4 context, ran on 7 mutants; GT-5 ran on
   7. For two mutants whose key GT-4 uses only as a bar (M21 and M46), I did not rerun the
   simulation: it is deterministic and identical to the baseline's, so the verdict follows from the
   baseline rates.
5. **Additional runs.** The live test in a decay scenario (T-7), using the suite's own
   `gates.sequential` and `sim.returns`. Erlang and impact figures from the suite's own functions
   (T-9, T-11).
6. **The repository changed during the review.** From about 15:00, the builder's version 5 work
   edited `goal.toml`, `GOAL.md`, `TESTS.md`, `gates.py`, `gt02`, `gt03`, `gt04`, `gt06` and `gt08`. It
   was committed as `984cdcb` ("review fixes applied") and `dd2f2ba`. This review covers `18e3e74`, and
   three checks confirm that is what I reviewed:
   - `18e3e74`'s `goal.toml` and `GOAL.md` are byte-identical to the copies I took at 14:11;
   - all 15 of its `goaltests` files are byte-identical to the frozen copy;
   - that frozen copy reproduces the official baseline run exactly.
   I redid every slow run on the frozen copy. One earlier run that overlapped the edits (M37) gave
   impossible fidelity results and was discarded. All 57 fast runs were identical on the frozen copy.
   I did not review version 5; each finding below should be rechecked against it.

Scripts and raw outputs are in
`/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/`
(`scripts/`, `mutations/<id>/`). They are scratch files, not part of the repository.

## Classification of every check

Categories: **a** external oracle (real data, published numbers or events, or a simulation whose true
answer is set by construction); **b** internal arithmetic between the goal's own numbers; **c** presence
or wording; **d** circular (passes by construction once a key exists, compares the goal with itself,
or is judged against a bar the goal set where the result was already known). The column "bar" says
who sets the pass/fail threshold: **T** the test or an external source, **G** the goal itself.

Counts over the 418 verdict checks of the baseline run (informational lines excluded):

| Category | GT-1 | GT-2 | GT-3 | GT-4 | GT-5 | GT-6 | GT-7 | GT-8 | Total |
|---|---|---|---|---|---|---|---|---|---|
| a, bar from the test or outside | | 3 | 4 | 4 | | 1 | | 1 | **13** |
| a, bar from the goal | | | | 24 | 2 | | | | **26** |
| b internal arithmetic | | 20 | 1 | | | 3 | | 1 | **25** |
| c presence or wording | 296 | 5 | | | | 6 | | 2 | **309** |
| d circular | 2 | 2 | | 8 | 2 | | 29 | 2 | **45** |
| total | 298 | 30 | 5 | 36 | 4 | 10 | 29 | 6 | **418** |

Only 13 of the 418 checks (3%) take both the answer and the bar from outside the goal, and one of
those (GT-2 "stress gaps match the price data") checks the test's own constants and cannot fail any
goal.

### GT-1 statement quality (`goaltests/gt01_quality.py`), 298 checks

| Check | Lines | Cat. | Bar | Why |
|---|---|---|---|---|
| mission, viewpoint, non-goals, stakeholders stated (4) | 47–51 | c | – | non-empty key |
| per objective: has a key result; states what, not how; KAOS kind; GQM question (32) | 56–64 | c | – | membership; DESIGN keyword list (20–21) |
| per KR: verifiable, i.e. eight fields present (41) | 66–71 | c | – | fields must be non-empty; their values are never read. M19 (KR3.1 allows 10 entries below twice their cost) passes |
| per KR: traces to an objective, ISO method, gate exists (123) | 72–77 | c | – | membership |
| per KR: unambiguous, free of design (82) | 78–81 | c | – | keyword scan of `statement` only; M55 (vague KR wording) caught |
| limits are numbers (5) | 83–88 | c | – | type check on 19 named keys |
| no vague limits (4) | 89–92 | c | – | only `*_text` of four sections; `[measurement]`, `[order_limits]`, `[returns]`, gate texts and controls are not scanned (M56 missed) |
| gate has a machine-checkable rule (3) | 94–96 | c | – | passes when `kind` exists; G3's `owner_decision` passes although it is no rule |
| every KPP decided at a gate; kill criteria stated (2) | 97–99 | c | – | membership, presence |
| GOAL.md names every key result | 108–109 | d | – | the goal against itself, one direction only (toml to md): a key result deleted from goal.toml is invisible (M13) |
| GOAL.md shows every number goal.toml sets | 110–117 | d | – | the goal against itself, as a substring anywhere in 70 KB of text ("8" is found for M01's 8%); `[evaluation]` and `[[gates]]` are never compared, so every mutant in those sections bypasses it (M04, M11, M20–M22, M28, M29, M36, M38, M39, M41, M43, M45, M46, M49, M52–M54) |

### GT-2 internal consistency (`goaltests/gt02_consistency.py`), 30 checks

| # | Check (baseline result) | Lines | Cat. | Why |
|---|---|---|---|---|
| 1 | one side's stops x 1.25 within the daily limit (1.88 vs 2) | 115–119 | b | `STOP_SLIPPAGE = 1.25` (13) is the test's own unsourced constant |
| 2 | both sides' stops x 1.25 within the worst-day bound (2.50 vs 2.5) | 120–124 | d | the bound `max_day_loss_pct = 2.5` is exactly 2.0 x the test's 1.25 (GOAL.md:165 cites GT-2 for it): an identity with zero slack |
| 3 | stress gaps match the price data | 142–143 | a | validates the test's hard-coded gaps (23–24); cannot fail any goal |
| 4 | overnight jump covers the largest gaps in the data (50 vs 49.5) | 152–154 | a | real data; I confirmed +49.5% (YHOO) is the largest absolute gap of the five stocks from 1999 |
| 5 | one overnight position through the jump within the daily limit (2.00 vs 2) | 155–157 | b | re-derives goal.toml:88's own comment; anchored by #4 |
| 6 | one position through an intraday jump (2.00 vs 2) | 158–162 | b | `jump_intraday_pct` has no external anchor (M42 at 5% passes) |
| 7 | total loss of one overnight name within the jump-loss bound (4 vs 4) | 163–167 | b | uses the stock cap only; the 10% index-fund cap is never compared with the bound |
| 8 | industry-wide jump within the jump-loss bound (4.00 vs 4) | 168–171 | b | |
| 9 | one broad index fund through its own jump (2.00 vs 2) | 174–184 | b | the 20% index jump is unanchored; goal.toml:93 says it is "above the 13% level-2 gap", which no check tests |
| 10 | one event-prone position through its own jump (2.00 vs 2) | 174–184 | b | the 100% jump is unanchored (M05 at 30% passes) |
| 11 | worst jump at a drawdown just short of the halt stays inside the drawdown line (9.5 vs 10) | 185–200 | d | tautology: with `drawdown_room_margin_pct` present, `allowed = min(worst, dd - margin - halt)` (195), so `halt + allowed <= dd` holds for any margin >= 0. M25 (halt at 10%) passes as "10% + 0.00%"; M51 (jump-loss bound 10%) passes as "9% + 0.50%". Only deleting the key fails it (M02) |
| 12 | margin covers closing the whole book at stressed costs (0.5 vs 0.06) | 201–205 | b | |
| 13 | overnight net book through a 13% market gap (1.95 vs 2) | 216–224 | b | 13% is the level-2 circuit breaker, an external rule |
| 14 | overnight exposure limited separately from intraday | 225–228 | c | key presence |
| 15 | jumps sized as jumps | 229–230 | c | key presence |
| 16 | planned activity fits the book: full at most 10% of the time (8.6%) | 236–243 | b | Little and Erlang on the goal's plan; capacity uses the most favourable risk per position, the 0.1% floor (83), not the plan's ~0.13% (GOAL.md:162). At 0.13% the open-risk cap holds 15 positions and Erlang B(15, 15) = 18.0%, which fails. With the floor deleted the test silently uses `risk_bearing_min_risk_pct` instead (M23 passes) |
| 17 | planned book within gross (60 vs 100) | 244–249 | b | |
| 18 | planned book within overnight gross (60 vs 75) | 250–253 | b | |
| 19 | typical position within the overnight caps (4 vs 4) | 254–258 | b | |
| 20 | volatility budget within 0.5–1.5x what the planned book produces (0.20 vs 0.2) | 259–270 | a | residual volatility of GOOG and MSFT on real data; assumes uncorrelated positions |
| 21 | short selling consistent with the leverage rule | 284–289 | c | looks for the word "borrow" in `leverage_text`; the number `max_gross_exposure_pct` is never compared with the text or the non-goals (M18 at 300% passes) |
| 22 | drawdown halt above the daily limit | 291–294 | b | |
| 23 | daily limit at least 3 ordinary days of volatility | 296–301 | b | |
| 24–25 | minimum and planned activity fit the cost budget (4.16 vs 4.5) | 303–315 | b | the budget is set "just above the planned 4.2%" (goal.toml:130) |
| 26 | a return objective is stated | 320–321 | c | |
| 27–28 | stated returns match Sharpe x volatility budget | 322–330 | b | |
| 29 | a full book is resolved by a stated rotation rule | 335–340 | c | four keys present; their values are never judged (M24: 100 rotations a day passes) |
| 30 | a rotation clears its cost at least as an entry does (2 vs 2) | 341–345 | b | |

### GT-3 cost feasibility (`goaltests/gt03_costs.py`), 5 checks

| Check | Lines | Cat. | Bar | Why |
|---|---|---|---|---|
| the cost model is not cheaper than published costs (8 vs 6.95 bps) | 58–63 | a (not fully independent) | T | 3.0 of the 6.95 bps is `SLIPPAGE_PER_SIDE_BPS = 1.5` (24), "an assumption", equal to the goal's own `slippage_bps_per_side`; the 3.7 bps spread is the top-100 stocks' average, while the goal's universe admits spreads up to 10 bps and $20M a day. The universe limits are never read (M34, M35 missed) |
| entry rule at the planned edge horizon needs IC <= 0.10 (0.085) | 87–95 | a | T | real volatility, Grinold–Kahn bound; caught M03 |
| market impact at the participation limit vs the slippage charged | 101–109 | a | T (lenient) | passes if the *optimistic* end of the square-root range (1.2 bps) is within 1.5x the charge; the central estimate (1.8) exceeds the 1.5 bps charged and the high end (2.4) exceeds even 2.25 |
| the targeted return needs IC <= 0.10 at the planned activity (0.074) | 111–135 | a | T | |
| the targeted edge survives the cost stress (0.84 vs 0.5) | 136–144 | b | G | one-sided: fails a stress too harsh for the goal's own target, never one too lenient. M09 (multiplier 1.0) passes. goal.toml:120 justifies 1.5 by the target failing at 2x, the test's own default (gt04:28) |

### GT-4 gate power and false passes (`goaltests/gt04_power.py`), 36 checks (9 kinds x 4 noise models)

The rates come from simulations whose truth is set by construction (category a). The bars, and
several inputs that decide the rates (variant count, cost drag, implementation noise, target edge),
are read from the goal (lines 33–68).

| Check (baseline: normal / t4 / garch / ar1) | Lines | Cat. | Bar | Why |
|---|---|---|---|---|
| G1 passes the best no-edge variant <= `max_false_pass_g1` (0.25 / 0.30 / 0.10 / 0.82% vs 1%) | 193–194 | a | G | the goal's bar is stricter than the test default (5%), but relaxing it is invisible (M21) |
| no-edge reaches real money <= `max_false_real_money` (0.17 / 0.18 / 0.07 / 0.33%) | 195–197 | a | G | the G2 share rests on 4 to 25 G1 passes per model (garch 3/4, normal 7/10) |
| G1 passes the targeted edge >= `min_power` (84.5 / 81.0 / 82.5 / 75.8% vs 75%) | 198–201 | **d** | G | the bar was 80% (the code default at 52 and TESTS.md:25) and was lowered to 75% in the revision where ar1 power fell to 75.8% (GOAL.md:492–493, 545–547); 75.8% is 0.4 standard errors above 75% at 400 runs; under TESTS.md's 80% it fails |
| G2 passes the targeted edge after G1 >= `min_power` (82–88%) | 202–203 | a | G | |
| fidelity test passes an honest implementation >= 95% | 205–206 | a | T | but the size of the paper-versus-rerun noise is the goal's own `assumed_implementation_noise` |
| fidelity test catches a 1-Sharpe shortfall >= `min_fidelity_power` (94–96%) | 207–209 | a | G | same noise assumption |
| drawdown halt stops the targeted edge <= `max_false_halt_per_year` (0–0.5%) | 210–211 | a | G | |
| live test stops the targeted edge within 3 years <= `max_false_stop_3y` (3.2–8.9% vs 12%) | 213–214 | a | G | the goal's 12% is looser than the code default 10% (65), though results pass either |
| live test halves a dead strategy within a year >= 50% and stops it within 3 years >= `min_dead_stop_3y` (stopped 73 / 72 / 75 / 72% vs 65%) | 215–218 | **d** | G | the goal's 65% is 10 points below the code default 75% (67), under which 3 of 4 noise models fail; and only a strategy dead from day one is simulated, never the decay the cap exists for (see T-7) |

### GT-5 random strategies on real prices (`goaltests/gt05_null_real.py`), 4 checks

| Check (baseline) | Lines | Cat. | Bar | Why |
|---|---|---|---|---|
| G1 passes the best of 20 balanced / long-only random strategies <= `max_false_pass_g1` (0/26 windows each) | 146–148 | a | G | real prices, no edge by construction; but 26 windows of 2,400 days a quarter apart overlap by 97%, about 1.6 independent samples, so 0/26 cannot resolve a 1% bar. Zero windows pass by default (146), e.g. M49 |
| G2 passes a balanced / long-only random strategy <= `max_false_pass_g2` (42% and 44% vs 50%) | 149–151 | **d** | G | TESTS.md:26 says the test fails the goal above 20%; the code uses the goal's 0.50 (140), which goal.toml:159 justifies as "half of no-edge strategies make money". Under the documented 20% both checks fail |

### GT-6 metric gaming (`goaltests/gt06_goodhart.py`), 10 checks

Each probe is built to have a flaw (a), but most are placed where one key alone decides them, so
the verdict reduces to that key's presence.

| Probe | Lines | Cat. | What actually rejects it |
|---|---|---|---|
| averaging down | 43–45 | b | position size 20% > 10% as well as risk per position; M32 (risk per position 2%) still rejected by the size cap |
| selling tails without a stop | 46–48 | c | `stop_required` only (M30 caught) |
| riding the market | 49–55 | c | G2 `metric = "excess"` only (M29 caught); the probe's excess series is supplied by the test, so the goal's definition of excess is not exercised |
| padding the trade count | 56–58 | c | `min_risk_trades` > 20 only; 100 passes (M54) |
| best of 50 | 59–62 | a | the plain Sharpe floor ("Sharpe 0.54 < 1.0"), not the Deflated Sharpe Ratio; and `n_trials` is reported honestly, so the `min_trials` floor is never exercised (GT-6 misses M45; GT-4 catches it under one noise model) |
| paper's generous fills | 63–65 | c | `require_conservative_fills`, which also defaults to true (gates.py:76) |
| look-ahead leak | 66–69 | c | the Sharpe-4 plausibility ceiling, before the lag audit is reached (M20 missed) |
| big overnight positions | 70–73 | b | caps |
| churning | 74–80 | c | presence of `min_rotations_judged` |
| big overnight shorts | 81–85 | b | caps |

### GT-7 control coverage (`goaltests/gt07_controls.py`), 29 checks: all **d**

The checklist (12–42) is external, but an item passes when any control lists its ID in `covers`
(48–52, 56–58). The mapping is the goal's own claim and the control's text is never read. TESTS.md:49–50
says so. M47 (the kill-switch control reduced to "There is a kill switch.") and M14 (control C13
deleted, its items listed by other controls) pass.

### GT-8 outside view (`goaltests/gt08_outside.py`), 6 checks

| Check (baseline) | Lines | Cat. | Bar | Why |
|---|---|---|---|---|
| a strategy that passes G1 and G2 has a real edge >= `min_posterior` (85% vs 80%) | 48–62 | **d** | G | prior (5%), edge-size prior (uniform to Sharpe 2) and bar all from the goal; the base rates the docstring cites (1–15) are not used in any computation. M22 (prior 50%), M53 (edges to Sharpe 4), M52 (bar 30%) pass. The harsh edge prior the goal itself reports (1.25) gives 66%, which fails |
| ... and is worth running >= `min_posterior_worth_running` (78% vs 70%) | 63–65 | **d** | G | same; 40% at the harsh edge prior |
| the goal says when to stop | 89–90 | c | – | presence |
| real money starts small | 91–93 | c | – | presence of `max_initial_capital_fraction`; 1.0 passes (M36) |
| published edges count at most 42% | 94–96 | a | T | McLean–Pontiff; the multiplier is not used by any gate |
| the evidence bar accounts for every variant tried | 97–98 | b | G | the goal's `min_trials` against the goal's `assumed_trials`; caught M04, but not M39 (assumed 5 while the budget allows 20) or M48 (budget 100) |

Run without GT-4 (any `--only` set that includes 8 but not 4), GT-8 falls back to assumed rates
(79–88) and fails the unmodified goal. That is fail-safe, but it means GT-8's verdict in a fast run
says nothing.

### The gate logic (`goaltests/gates.py`)

gates.py defines what each rule means (TESTS.md:47–48), so its clauses are judged by whichever test
exercises them:

| Clause | Lines | Exercised by | Cat. of that oracle |
|---|---|---|---|
| G1 Deflated Sharpe Ratio, Sharpe floor, both halves, stress floor | 112–132 | GT-4 simulations, GT-5 real prices | a, bars from the goal |
| G1 minimum days | 101–102 | GT-4 (power) | a |
| G1 `min_trials` floor, `max(n_trials, min_trials)` | 121–123 | nothing: every simulated record reports its true count (gt04:83, gt05:110, gt06:61, 68, 79); only GT-8's internal comparison | b |
| G1 lag audit | 110–111 | nothing in effect: GT-4 and GT-5 set `lag_audit_ok=True`; GT-6's leak is stopped by the ceiling first | – |
| G1 plausibility ceiling | 107–109 | GT-6 leak probe | c |
| G1 conservative fills | 103–104 | GT-6 (on G2); defaults to required (76) | c |
| G1 net profit, `metric` | 99, 119–120 | nothing: GT-4 sets `daily = excess` (gt04:83); GT-5's random strategies cannot reach the bar on raw returns | – |
| G1 rotation clause | 133–143 | GT-6 churning (key presence) | c |
| G2 minimum days, fidelity z-test | 149–150, 165–178 | GT-4 (with the goal's implementation-noise assumption) | a |
| G2 risk-bearing trades | 151–153 | GT-6 padding (value > 20) | c |
| G2 trade match (`min_trade_match`, KR1.6) | 168–169 | nothing: records set it to 0.98 or 1.0 (gt04:97, gt05:123, gt06:37) | – |
| G2 days to the trades | 154–158 | nothing: every record sets it to the minimum, and GT-5 removes the clause (gt05:119) | – |
| G2 excess > 0 | 179–181 | GT-4, GT-5, GT-6 riding the market | a / c |
| G2 net profit | 182–183 | nothing (M43 missed) | – |
| live test (sequential) | 188–217 | GT-4, dead-from-day-one only; the LLR cap is never exercised | a, bars from the goal |
| risk-rule violations | 220–241 | GT-6 | b / c; the per-side open-risk limit is compared with total open risk (228) |

Parts of the key results that gates.py does not implement, so no test can see them: KR1.9's split at
the median VIX, KR6.4's lag-audit thresholds (half the Sharpe kept, no more than a 10% rise; the record
supplies only a boolean), KR3.7's calibration ratio, and KR1.8 (G3 is `owner_decision`).

### Post-hoc thresholds, self-comparisons and oracles that are not independent

**Thresholds that look chosen after the result:**

- `min_power` 0.80 to 0.75, against a measured 75.8% (T-2);
- `max_false_pass_g2` 0.50, against 42% and 44%, where TESTS.md documents 20% (T-2);
- `min_dead_stop_3y` 0.65, against 72–75%, where the code default is 0.75 (T-2);
- `stress_cost_multiplier` set at 1.5 because the goal's target fails at 2x, the test's default (T-2);
- `max_day_loss_pct` 2.5, which is 2.0 times the test's own 1.25 (T-2);
- `cost_budget_pct_per_year` 4.5, "just above the planned 4.2%" (goal.toml:130);
- in the test code, the impact tolerance, which compares the optimistic end of the range with 1.5
  times the charge (T-11).

**The goal compared with itself, presented as evidence:**

- GOAL.md's risk-limit table cites "(GT-2)" as the reason for each limit (GOAL.md:164–179). For nine of
  those limits, GT-2 re-derives the goal's own arithmetic and passes with exactly zero slack: 2.00 vs
  2 five times, 4 vs 4 three times, and 2.50 vs 2.5. That catches an edit to one side, but says
  nothing about whether the limits are enough. Only the 50% overnight jump and the 13% market gap come
  from outside.
- GOAL.md:46–51 presents "a real edge with probability 85%" as the outside view (T-4).
- GT-8's "the evidence bar accounts for every variant tried (Harvey-Liu-Zhu, Bailey-López de Prado)"
  compares two goal numbers under the literature's names (gt08:97–98).
- GT-1's GOAL.md checks are presented as statement quality (T-13).
- GT-7 accepts the goal's own coverage map (T-5).
- GT-2's drawdown-room check assumes the goal's own shrink rule (T-3).

**Oracles described as independent that are not, or not fully:**

- GT-3's published costs include the goal's own slippage figure and a spread not drawn from the
  goal's universe (T-11).
- GT-8's base rates never enter the calculation (T-4).
- GT-4's simulations take their variant count, cost drag, implementation noise and target edge from
  the goal (T-6).
- GT-7's external checklist is mapped by the goal itself (T-5).
- GT-5's real prices are judged against the goal's bars (T-1). Its long-only check cannot tell excess
  from raw profit on 1999–2014 prices (M28), and it removes market exposure by an in-sample regression,
  not by the goal's definition (T-17).
- GT-2's named events beyond the data (SVB, the regional banks, the level-2 breaker for index funds)
  label arithmetic on the goal's caps; only the 13% market gap enters a check (T-15).

## Mutation testing

Each mutant changes one thing in goal.toml that a careful reviewer would call a defect. The letter
after each catching check is that check's category from the table above.

- **Caught** means a check that passed on the baseline fails on the mutant.
- **GOAL.md text only** means the only new failure is GT-1's substring search of GOAL.md. That
  compares the goal with itself, and an author who edited both files consistently would pass it, so
  I count these as missed.

**Result.** Of the 56 mutants, the suite detects 19 and misses 36. One more (M39) fails a check by
chance (see T-2).

- Of the 24 mutants the brief suggested (M01–M24), it detects 12 and misses 12.
- Of the 32 I added, it detects 7, misses 24, and flags M39 by chance.
- GT-4 detected 3 of the 7 mutants it ran on (M11, M12, and M45 under one noise model only).
- GT-5 detected none of its 7.
- One missed mutant (M35) trips only the GOAL.md text check.
- The 19 detections came from checks in category a (9), b (4), c (3) and d (3); the d detections
  include the tautology's only failing branch (M02) and a GT-7 presence check (M50).

| Mutant | Defect | Expected catcher | Caught by | Missed |
|---|---|---|---|---|
| M01 | overnight stock cap 4% to 8% | GT-2 | GT-2 one position through the 50% jump, 4% > 2% (b); total loss of one name, 8% > 4% (b) | |
| M02 | `drawdown_room_margin_pct` deleted | GT-2 | GT-2 worst jump at the halt, 13% > 10% (d: the only way that check fails) | |
| M03 | `planned_edge_horizon_minutes` 780 to 150 | GT-3 | GT-3 entry rule needs IC 0.193 > 0.10 (a) | |
| M04 | G1 `min_trials` 20 to 5 | GT-8, GT-4 | GT-8 `min_trials` < `assumed_trials` (b). GT-4 cannot see it: its records report 20 variants | |
| M05 | event-prone overnight jump 100% to 30% | GT-2 | | **missed** |
| M06 | daily loss limit 2% to 4%, above the 2.5% worst-day bound | GT-2 | | **missed** |
| M07 | `max_open_risk_pct` 2 to 5 | GT-2 | GT-2 whipsaw 3.75% > 2.5% (d) | |
| M08 | `rotation_margin_to_cost` 1 to 0 | GT-2 | GT-2 rotation clears 1x vs entry 2x (b) | |
| M09 | `stress_cost_multiplier` 1.5 to 1.0 (no stress) | GT-3, GT-4 | GT-3 passes ("1.50 vs a floor of 0.5"); GT-4 passes, though false passes rise (t4 0.30% to 0.50%, GARCH 0.10% to 0.35%); GT-5 and GT-8 pass | **missed** |
| M10 | `round_trip_cost_bps` 8 to 2 | GT-3 | GT-3 cost below published 6.95 bps (a) | |
| M11 | G2 `min_days` 120 to 40 | GT-4 | GT-4 G2 power 71.4–74.3% < 75% in 3 of 4 models; fidelity power 56–61% < 80% in all 4 (a) | |
| M12 | live `test_stop_llr` -2.5 to -0.5 | GT-4 | GT-4 live test stops the targeted edge within 3 years 34–52% of the time > 12% (a); also GOAL.md text | |
| M13 | key result KR2.5 deleted (stops that work while the system is down) | GT-1 | | **missed** |
| M14 | control C13 deleted (per-name, daily-notional, open-position throttles) | GT-7 | | **missed** |
| M15 | `jump_overnight_pct` 50 to 20 | GT-2 | GT-2 jump below the 49.5% Yahoo gap (a) | |
| M16 | `max_overnight_net_pct` 15 to 60 | GT-2 | GT-2 13% market gap costs 7.8% > 2% (b) | |
| M17 | `vol_target_daily_pct` 0.2 to 1.0 | GT-2 | GT-2 budget out of reach of the book (a), 3 days of volatility and returns vs Sharpe (b); GT-3 target needs IC 0.23 (a) | |
| M18 | `max_gross_exposure_pct` 100 to 300 (3x leverage; text still says 100%) | GT-2 | | **missed** |
| M19 | KR3.1 allows 10 entries below twice their cost | GT-1 | | **missed** |
| M20 | G1 `require_lag_audit` false | GT-6 | | **missed** (the leak probe is stopped by the Sharpe ceiling first) |
| M21 | `max_false_pass_g1` 0.01 to 0.2 | GT-4, GT-5 | GT-5 passes ("at most 20%: 0/26"); GT-4 not rerun: the key is only its bar, and the baseline rates are 0.10–0.82% | **missed** |
| M22 | `prior_edge_probability` 0.05 to 0.5 | GT-8 | GT-8 passes (posterior 99%) | **missed** |
| M23 | `min_position_risk_pct` floor deleted | GT-2 | GT-2 silently uses `risk_bearing_min_risk_pct` instead | **missed** |
| M24 | `max_rotations_per_day` 3 to 100 | GT-2 | | **missed** |
| M25 | drawdown halt 9% to 10%, at the line itself | GT-2 | GT-2 passes "10% + 0.00% = 10.00% vs 10%" | **missed** |
| M26 | `hold_through_earnings` true | GT-2 | key never read | **missed** |
| M27 | `max_holding_trading_days` 5 to 20 | GT-1, GT-2, GT-5 | GT-5 passes (G2 random pass rate 35% and 49% vs 50%) | **missed** |
| M28 | G1 judged on raw profit (`metric = "net"`) | GT-5, GT-6 | GT-5 passes (long-only random strategies 0/26 even on raw returns); GT-4 sets `daily = excess` | **missed** |
| M29 | G2 judged on raw profit (`metric = "net"`) | GT-6 | GT-6 "riding the market" passes the goal (c) | |
| M30 | `stop_required` false | GT-6 | GT-6 "selling tails" passes the goal (c) | |
| M31 | `max_drawdown_pct` 10 to 20 (KR2.7 still 10) | GT-2 | | **missed** |
| M32 | risk per position 0.5% to 2% | GT-2, GT-6 | GT-6 averaging-down probe still rejected, by the 10% size cap | **missed** |
| M33 | entry rule 2x to 1x cost (KR3.1 still "twice") | GT-2, GT-3 | | **missed** |
| M34 | universe spread limit 10 to 50 bps | GT-3 | | **missed** |
| M35 | universe dollar volume $20M to $1M a day | GT-3 | GOAL.md text only | **missed** |
| M36 | G3 starts with all the capital (fraction 1.0) | GT-8 | presence only | **missed** |
| M37 | live test without its cap (2.89 to 1000) | GT-4 | GT-4 passes: its live-test rates move by at most one point (t4 stopped 71% vs 72%), because no simulated strategy is good first and then decays | **missed** |
| M38 | `assumed_cost_drag_daily_pct` 0.017 to 0.001 (no longer the plan's 4.2%) | GT-4, GT-2 | GT-4 and GT-8 pass; the rates match M09's (the stress clause is gone in effect) | **missed** |
| M39 | `assumed_trials` 20 to 5 while the budget allows 20 | GT-4, GT-8 | flagged by chance: GT-4 ar1 G1 power 74.5% < 75%, a fall the change cannot cause (the bar stays at 20 variants and fewer rivals raise power). Everything else improved: false passes 0.82% to 0.25%, posterior 85% to 96%. GT-5 passes | **missed** (flagged by chance) |
| M40 | `max_position_adv_pct` 0.02 to 1.0 | GT-3 | GT-3 impact 8.4–16.8 bps vs 1.5 charged (a) | |
| M41 | `published_edge_multiplier` 0.42 to 1.0 | GT-8 | GT-8 above McLean–Pontiff's 0.42 (a) | |
| M42 | `jump_intraday_pct` 20 to 5 | GT-2 | | **missed** |
| M43 | G2 no longer requires a profit | GT-6, GT-5 | GT-5 passes (45%, 45% vs 50%) | **missed** |
| M44 | `max_order_participation_pct` 10 to 50 | GT-3 | key never read | **missed** |
| M45 | G1 `dsr_min` 0.95 to 0.5 | GT-4 | GT-4 under ar1 noise only: false passes 1.51% > 1%, real money 0.72% > 0.5% (a); GT-8 posterior 73% < 80% (d). Under normal and t4 noise the rates are identical to the baseline | |
| M46 | `min_power` 0.75 to 0.5 | GT-4 | not rerun: the key is only GT-4's bar, and baseline power is 75.8% to 88% | **missed** |
| M47 | kill-switch control C6 reduced to "There is a kill switch." | GT-7 | | **missed** |
| M48 | `max_variants` 20 to 100 | GT-8, GT-4 | key never read | **missed** |
| M49 | G1 `min_days` 2400 to 4000 (more history than exists from 2016) | GT-5, GT-4 | GT-5 passes on "0/0 windows" for all four checks; GT-4 not run (longer records only raise power) | **missed** |
| M50 | control C14 (clock) deleted | GT-7 | GT-7 RT-10 not covered (d) | |
| M51 | single-jump bound 4% to 10% | GT-2 | GT-2 passes "9% + 0.50%" | **missed** |
| M52 | `min_posterior` 0.80 to 0.30 | GT-8 | | **missed** |
| M53 | edge-size prior up to Sharpe 4 | GT-8 | GT-8 passes (posterior 91%) | **missed** |
| M54 | G2 `min_risk_trades` 300 to 100 (KR1.7 still 300) | GT-6, GT-4 | GT-6 padding probe still rejected (20 < 100) | **missed** |
| M55 | KR4.1 statement made vague ("about all day") | GT-1 | GT-1 KR4.1 unambiguous (c) | |
| M56 | `[measurement]` text made vague ("a realistic price") | GT-1 | section not scanned | **missed** |

## Findings

### T-1. The statistical tests are judged against the goal's own bars (blocking)

**Evidence.** TESTS.md:3–4 says every oracle "lies outside the goal, so the goal is never used as
evidence for itself". That holds for how the rates are produced, not for how they are judged:

- GT-4 reads eight of its nine bars from `[evaluation]`: `max_false_pass_g1`, `max_false_real_money`,
  `min_power`, `max_false_halt_per_year`, `min_fidelity_power`, `max_false_stop_3y`,
  `min_dead_halve_1y` and `min_dead_stop_3y` (gt04_power.py:50–67). Only the fidelity false-alarm bar
  (5%, line 206) is the test's own. GT-4 also takes its inputs from the goal: the variant count, the
  cost drag, the implementation noise and the target edge (37–58).
- GT-5 reads its bars from the goal (gt05_null_real.py:140).
- GT-8 reads its prior, its edge-size prior and both bars from the goal (gt08_outside.py:48–50, 63).

So loosening the goal's tolerance passes the goal. The mutants show it: `max_false_pass_g1 = 0.2`
(M21), `min_power = 0.5` (M46), `prior_edge_probability = 0.5` (M22), `min_posterior = 0.30` (M52) and
`prior_edge_sr_max = 4.0` (M53) all pass every test. For M21 and M46 this follows from the code: those
keys are used only as bars, so the simulation is the same as the baseline's and every rate clears the
looser bar.

**Fix.** Put the acceptance bars in the tests, fixed before results and taken from the owner's
requirements or the literature, as TESTS.md already documents them (power at least 80%, GT-5 false
passes at most 5% and 20%). Treat the goal's `[evaluation]` values as claims: the test fails when the
goal's tolerance is looser than the test's bar. Read the simulation inputs from the goal only where
another test checks them (see T-6).

### T-2. Bars that sit where the results already were (blocking)

**Evidence.**

- **G1 power.** `min_power` was 80% (the code default, gt04:52; still 80% in TESTS.md:25). It was
  lowered to 75% in the same revision that doubled the variant budget (GOAL.md:492–493). Under
  autocorrelated noise, G1 power is 75.8% at 400 runs, which is 0.4 standard errors (2.1 points) above
  the new bar. Decision 5 (GOAL.md:545–547) says the floor was fixed first and the budget then chosen to
  meet it. That is still a bar and a design parameter chosen together, with the result known. Under
  the documented 80%, the goal fails. The bar sits so close to the result that a change to the random
  stream flips it. M39 can only raise power (fewer competing variants, the same 20-variant floor), yet
  it fails this check at 74.5%.
- **G2 on random strategies.** `max_false_pass_g2 = 0.50` (goal.toml:159: "half of no-edge strategies
  make money"). GT-5 measures 42% and 44% and passes. TESTS.md:26 says GT-5 fails the goal above 20%,
  and under that bar both checks fail.
- **Dead-strategy stop rate.** `min_dead_stop_3y = 0.65`, against the test's own default of 0.75
  (gt04:67). GT-4 measures 73%, 72%, 75% and 72% (normal, t4, GARCH, AR(1)). Under the default, three
  of the four noise models fail, and the fourth sits at the bar.
- **Cost stress.** goal.toml:120 and GOAL.md:221–223 justify the 1.5 multiplier by GT-3's finding that
  at 2x, the test's own default (gt04:28), the targeted strategy would fail. The stress was set where
  the goal's target passes. The GT-3 check behind it (gt03:136–144) only fails a stress that is too
  harsh for the goal's own target. It can never fail one that is too lenient: M09
  (multiplier 1.0) passes.
- **Worst-day bound.** `max_day_loss_pct = 2.5` is exactly `max_open_risk_pct` 2.0 times GT-2's
  unsourced `STOP_SLIPPAGE = 1.25` (gt02:13). The check passes as "2.50% vs 2.5%", and GOAL.md:165 cites
  GT-2 as the reason for the bound.

**Fix.** Freeze every bar in TESTS.md and the test code before the run it judges, and keep the history
of bar changes. Report each rate with a confidence interval and judge the bound, not the point
estimate. Lowering a bar is an owner decision recorded against the test, never a goal edit the test
then reads. Make the stress check two-sided: require a stress multiplier at least an external floor,
such as 2x, or the upper end of published cost ranges.

### T-3. The drawdown-room check is a tautology (blocking)

**Evidence.** In gt02_consistency.py:194–200, once `drawdown_room_margin_pct` exists the allowed jump is
`min(worst, dd - margin - halt)` (195). So `halt + allowed <= dd` holds for any margin of zero or more.
The check assumes the goal's prose rule ("positions shrink as the drawdown deepens") works and then
confirms it. Two mutants show it:

- M25 moves the halt to the 10% line itself. GOAL.md:86 says a halt there "would fire only after the
  line was crossed". The check still passes, as "10% + 0.00% = 10.00% vs 10%".
- M51 raises the single-jump bound to 10%. The check passes as "9% + 0.50%". The 10% worst event never
  enters the sum.

Only deleting the key (M02) fails the check.

**Fix.** Make the shrink rule a number in goal.toml, for example the size multiplier as a function of
drawdown. Then test `halt + worst_event(sizes allowed at the halt) <= max_drawdown_pct` with the event
sizes computed from the caps. Separately, test `max_drawdown_halt_pct < max_drawdown_pct` and
`max_jump_loss_pct <= max_drawdown_pct - max_drawdown_halt_pct`, unless the shrink rule provably
covers the gap.

### T-4. The outside view does not use the outside view (blocking)

**Evidence.** GT-8's docstring cites base rates (gt08_outside.py:1–15): under 1% of day traders
reliably profitable, 97% losing, 58% decay after publication, t > 3. Only the 42% McLean–Pontiff figure
enters any computation (94–96). The posterior (51–62) comes from three things, all inputs the goal
supplies: its prior of 5%, its edge-size prior (uniform up to Sharpe 2) and its bars (80% and 70%).
GOAL.md:46–51 presents the resulting "real edge with probability 85%" as a finding. M22, M52 and M53
pass. The goal itself shows what a less generous edge-size prior gives: 66% real and 40% worth
running (GOAL.md:51), both failing its own bars. The pass also sits inside sampling error. The
no-edge rate that feeds it (0.33%) rests on 10 of 25 G2 passes in one noise model, and the posterior
falls to 80% at 0.46%, below the 95% upper bound of that estimate. That estimate is my calculation
from GT-4's counts.

**Fix.** Bound the prior and the edge-size distribution in the test from the cited base rates. For
example, fail the goal when its prior exceeds the test's, or when the edge distribution puts more
than a set share of mass above Sharpe 1.25. Judge the posterior at the harsher distribution and at
the upper confidence bound of the false-pass rate. Report the 85% as a consequence of the goal's
assumptions, not as an outside view.

### T-5. Control coverage is self-declared (major)

**Evidence.** gt07_controls.py:48–58 passes an item when any control lists its ID in `covers`, and no
control text is read. M47 reduces the kill-switch control C6 to "There is a kill switch." and passes.
M14 deletes control C13, the per-name, daily-notional and open-position throttles, and passes because
other controls also list RT-2, RT-9 and KC-2. TESTS.md:49–50 discloses the limit, but the 29 checks
are counted in the "418/418" headline as passes.

**Fix.** For each checklist item, list the required elements and the goal keys that implement them.
RT-2, for example, needs a price collar (`price_collar_pct`), a maximum order size and message limits
(`max_orders_per_second`). Check that each covering control names those keys, and that the keys
exist with values inside reference ranges. Report items covered by a single control, so a deletion
shows up. Until then, report GT-7 as presence, outside the pass count.

### T-6. The simulations' inputs come from the goal and nothing checks them (major)

**Evidence.** GT-4 sizes its no-edge search by `assumed_trials`, its cost stress by
`assumed_cost_drag_daily_pct` and its fidelity noise by `assumed_implementation_noise`
(gt04:40–43, 57). No test ties these to the rest of the goal:

- M39 (`assumed_trials = 5` while `max_variants = 20`) makes GT-4 simulate a smaller search than the
  budget allows. Its false passes fall (AR(1): 0.82% to 0.25%) and GT-8's posterior rises from 85% to
  96%.
  The only check it fails, it fails by chance (see T-2).
- M48 (`max_variants = 100`) passes. `max_variants` is never read.
- M38 (`assumed_cost_drag_daily_pct = 0.001` instead of the plan's 0.017) passes every test, GT-4
  included.
- The cost-stress clause, not the Deflated Sharpe Ratio, decides G1's false passes in three of GT-4's
  four noise models. The clause needs a raw Sharpe of at least 1.175, and its strength comes from the
  goal's own `assumed_cost_drag_daily_pct`; the Deflated Sharpe Ratio at 0.95 needs 1.15, or 1.25
  under AR(1) noise. My calculation with the suite's `stats.dsr`. Lowering `dsr_min` to 0.5 (M45)
  leaves the normal and t4 false-pass rates exactly as before (0.25% and 0.30%). Only the
  autocorrelated model catches it (1.51%).
- The `min_trials` floor (gates.py:121–123) never decides a verdict. Every simulated record reports
  its true count (gt04:83, gt05:110, gt06:61), so M04 is caught only by GT-8's comparison of two goal
  numbers (gt08:97–98).

**Fix.** Derive GT-4's cost drag from the plan, as GT-3 already does (trades x size x cost). Use
`max(assumed_trials, max_variants)` and fail when `assumed_trials < max_variants`. Add a GT-6 probe
that reports one variant for the best of 20, so the floor is exercised. Bound the implementation noise
by an external figure, or report results across a range.

### T-7. The live test is never shown a decay (major)

**Evidence.** KR8.2 and goal.toml:217 cap the log-likelihood ratio "so a long good run can't hide a
decay". GT-4 simulates only a strategy that has the targeted edge throughout, and one dead from day one
(gt04:140–151). I ran the decay case with the suite's own `gates.sequential` and `sim.returns`
(scripts/decay.py; normal noise; 2 years at Sharpe 1.5, then no edge; 2,000 runs, of which 1,907
were not stopped while the edge was real):

| Case (times from the decay, or from day one) | Halved within 1 year | Stopped within 3 years |
|---|---|---|
| Edge for 2 years, then none (goal's cap ln 18) | 25% | 50% |
| Same, without the cap (M37) | 20% | 38% |
| Dead from day one (GT-4's case; GT-4 itself measures 63% and 73%) | 64% | 75% |
| Goal's bar | 50% | 65% |

In the case it was designed for, the goal's live test misses both of its own bars, and GT-4 cannot
see it. M37, which removes the cap, passes GT-4 as well: GT-4's live-test rates move by at most one
point (t4: stopped 71% against 72%).

**Fix.** Add decay scenarios to GT-4, such as 1 and 2 years of the targeted edge followed by none, with
bars on halving and stopping measured from the decay. Then size the cap and thresholds against them.

### T-8. GT-6's probes are placed where one key decides them (major)

**Evidence.** Each probe is rejected by the first clause it meets, so several gate clauses are never
reached:

- **Look-ahead leak.** The leak has a Sharpe of 8 and is stopped by the plausibility ceiling of 4
  before the lag audit is reached (gates.py:107–111). M20 (`require_lag_audit = false`) passes. A
  subtle leak at Sharpe 2.5 would pass G1.
- **Best of 50.** The probe is stopped by the plain Sharpe floor ("Sharpe 0.54 < 1.0"), not by the
  deflated bar. M45 (`dsr_min = 0.5`) passes GT-6, and the multiple-testing correction is untested
  here.
- **Padding the trade count.** The probe hard-codes 20 risk-bearing trades, so any minimum above 20
  passes. M54 (100 instead of 300) passes.
- **Gate clauses with no probe.** No probe has positive excess return and a net loss (M43, G2
  `require_net_profit = false`). None judges G1 on raw profit (M28, G1 `metric = "net"`). GT-4 cannot
  see M28 either, because it sets `daily = excess` (gt04:83).
- **Averaging down.** The probe is rejected by the 10% position cap as well as the risk limit, so
  raising risk per position to 2% (M32) passes.

**Fix.** Place each probe just inside every limit except the one it targets:

- a leak with Sharpe 2.5 and a failed lag audit;
- the best of 50 with a raw Sharpe of about 1.3, reported as one variant;
- 150 risk-bearing trades;
- a long-only G1 record whose raw Sharpe clears the bar with zero excess;
- a paper record with positive excess and a net loss;
- averaging down within the position cap but at 1% risk.

### T-9. The capacity check uses the most favourable assumption (major)

**Evidence.** GT-2 sizes the open-risk capacity at the 0.1% floor, `min_position_risk_pct`
(gt02:83–86), and gets 20 positions. Overnight gross allows 18, so the book is full 8.6% of the time,
inside the 10% bar. GOAL.md:162 says the plan's positions risk about 0.13% each. At that risk the
open-risk cap holds 15 positions, and Erlang B(15, 15) = 18.0%, which fails. If the floor is deleted
(M23), the test silently falls back to `risk_bearing_min_risk_pct`, an unrelated threshold with the
same value, and passes.

**Fix.** Add the planned risk per position to goal.toml and use it in the capacity check. Fail when
`min_position_risk_pct` is missing, rather than substituting another key.

### T-10. Contradictions between sections are not checked (major)

**Evidence.** These single defects pass every test:

- the daily limit above the worst-day bound (M06: 4% against 2.5%);
- 300% gross exposure while `leverage_text` and the non-goals say 100% (M18);
- 20-day holds against the non-goals and KR3.2 (M27);
- `max_drawdown_pct = 20` while KR2.7 says 10 (M31);
- the halt at 10% while KR2.2 says 9% (M25);
- 2% risk per position against the owner's 0.5% (M32);
- an entry multiple of 1 while KR3.1 says "twice" (M33);
- G2 trades 100 while KR1.7 and KR3.4 say 300 (M54);
- holding through earnings (M26), a key no test reads.

GT-1 checks that key-result fields exist, never their values (M19). 41 of the goal's 146 numeric or
boolean settings are never read by name by any test, including all 20 numbers in `[order_limits]`.
Some of those numbers are touched only by GT-1's GOAL.md substring search.

**Fix.** Map each key result that restates a limit to its key and require equality. Check orderings
(daily limit < worst day < halt < drawdown line; gross limit = leverage text). Treat the owner's stated
values in goal_v1.toml as invariants that may be loosened only with a cited decision. Report keys no
test reads.

### T-11. The cost oracle is partly the goal's own and not tied to its universe (major)

**Evidence.** GT-3's "published costs", 6.95 bps (gt03:32–34), include 3.0 bps of the test's own
slippage assumption (gt03:24, "an assumption"). That assumption equals the goal's
`slippage_bps_per_side`. The 3.7 bps spread is the average of the 100 largest stocks, while the goal
admits names with spreads up to 10 bps and $20M a day. GT-3 never reads the universe limits: M34
(50 bps spreads) passes, and M35 ($1M a day) is caught only by GOAL.md's text. The impact check
(gt03:107–109) passes if the optimistic end of the square-root range (1.2 bps) is within 1.5 times
the 1.5 bps charged. The central estimate (1.8) and the high end (2.4) both exceed the charge.

**Fix.** Derive the benchmark spread from the universe limits, for example a spread distribution for
names at the limits, and source the slippage externally. Compare the central impact estimate with the
charge. Fail when the universe limits allow names whose quoted spread alone exceeds the planning
average.

### T-12. GT-5 cannot resolve its bar, and passes with no data (major)

**Evidence.** The G1 check judges 26 windows of 2,400 days spaced 63 days apart (gt05:102). Each window
shares about 97% of its days with the next, so they carry roughly 1.6 independent samples. "0/26 = 0%"
cannot show a rate below 1%. With zero windows, the rate defaults to 0 and passes (gt05:146): M49
(G1 `min_days = 4000`, more history than exists from 2016) passes all four GT-5 checks on no data:
"0/0 windows of 4000 days = 0%". Because the paper windows start after the first research window
(gt05:121), the paper checks also report "0/0 windows of 120 days = 0%".

**Fix.** Fail on zero windows. Report the effective sample size and an upper confidence bound, and
judge the bound. Add instruments, or use a block bootstrap, until the bar can be resolved.

### T-13. GT-1's GOAL.md checks compare the goal with itself (minor)

**Evidence.** gt01:108–117 checks that each key-result ID and each number appears somewhere in GOAL.md,
as a substring. For example, M01's "8" is found among dozens of 8s. The key-result check runs one way
only, so a key result deleted from goal.toml is invisible (M13). `[evaluation]` and `[[gates]]` are
never compared. TESTS.md:22 lists this as statement quality.

**Fix.** Present it as document hygiene, not evidence. Compare table rows to keys by parsing GOAL.md's
tables, check both directions, and include `[evaluation]` and the gate rules.

### T-14. Wording checks are partial, and presence checks inflate the headline (minor)

**Evidence.** The vague-word scan reads key-result statements and the `*_text` of four sections only
(gt01:78–92). M56 ("a realistic price" in `[measurement]`) passes. Presence or wording checks make up
309 of the 418 checks (GT-1 alone has 298), and 45 more are circular. "418/418 checks pass" therefore
says little about whether the goal is right.

**Fix.** Scan every text field. Report three counts separately: presence checks, consistency checks,
and checks with an external oracle and bar.

### T-15. Jump tiers and the stop slippage have no external anchor (minor)

**Evidence.** The ordinary overnight jump is checked against real gaps (gt02:152–154). The intraday,
index-fund and event-prone jumps are not: M42 (5% intraday) and M05 (30% event-prone) pass.
goal.toml:93 claims the index-fund jump is "above the 13% market gap of the level-2 circuit breaker",
but nothing tests that claim. The named events (SVB, 13 March 2023) are labels on arithmetic over the
goal's caps. Separately, the stop slippage of 1.25 is unsourced and defines the worst-day bound
(see T-2).

**Fix.** Anchor each tier:

- the index-fund jump to at least 13%, or the largest index gap in the data;
- the event-prone jump to 100%;
- the intraday jump to a sourced statistic on halt reopenings or LULD moves.

Source the slippage, and check `max_overnight_etf_pct` and `max_overnight_event_prone_pct` against
`max_jump_loss_pct` too.

### T-16. The gate code is narrower than the key results, and no test notices (minor)

**Evidence.** gates.py has none of the following:

- KR1.9's split at the median VIX;
- KR6.4's thresholds (half the Sharpe kept, a rise of no more than 10%); the record supplies only a
  boolean;
- KR3.7's calibration ratio;
- a rule for KR1.8 (G3 is `owner_decision`).

It also compares the per-side open-risk limit with total open risk (gates.py:228). GT-1's "gate has a
machine-checkable rule" passes G3 although `owner_decision` is no rule.

**Fix.** Implement these clauses, or list them as untested in TESTS.md.

### T-17. No test exercises the goal's definition of excess return (minor)

**Evidence.** The goal defines excess return position by position: each position's 252-day beta to
SPY as of the previous close, with overnight and intraday counted separately (goal.toml:149). Neither
test that judges excess return uses that definition:

- GT-5 removes market exposure with an in-sample regression on the same window (gt05:76). That takes
  out the market's drift exactly, so the long-only random strategy cannot pass on drift, whatever the
  goal's definition would let through.
- GT-6's "riding the market" probe receives an excess series built by the test (gt06:49–55).

A goal whose excess definition leaked drift, for example through a stale beta or no
overnight/intraday split, would pass both.

**Fix.** Compute GT-5's excess with the goal's own rule: a rolling 252-day beta as of the previous
close, applied to the next day. Add a GT-6 probe whose beta drifts during the window.

## Reproducing this review

All paths are under
`/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/`.

| Path | What it holds |
|---|---|
| `frozen/` | commit `18e3e74`'s `goaltests/`, `goal.toml` and `GOAL.md`, plus a copy of the price cache: the version reviewed here |
| `scripts/make_mutants.py` | writes `mutations/M01` to `M56`; each edit must match exactly once, and each mutant must parse |
| `scripts/run_ctx.py` | runs chosen test modules as `__main__.py` does; saves or loads GT-4's context for GT-8 |
| `scripts/compare.py`, `scripts/summarize.py` | diff each mutant's results against the matching baseline |
| `scripts/decay.py` | the live test after a decay (T-7) |
| `scripts/probe_data.py` | gaps, Erlang, residual volatility and impact figures (T-9, T-11) |
| `mutations/<id>/` | each mutant's `goal.toml`, its `MUTATION.txt`, and its results: `fast_f.json` for fast tests on the frozen code, `slowf.json` for GT-4 and GT-8, `gt5f.json` for GT-5, `gt8ctx_f.json` for GT-8 against the baseline GT-4 context |

Fast tests (from `frozen/`):

```bash
python3 -m goaltests <mutant>/goal.toml --only 1,2,3,6,7,8 --json <mutant>/fast_f.json
```

GT-4 with GT-8:

```bash
python3 -I scripts/run_ctx.py <mutant>/goal.toml 4,8 out.json --save-ctx ctx.json
```

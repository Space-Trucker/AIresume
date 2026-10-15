# Evidence behind the decisions

These are the side calculations and records behind numbers that `GOAL.md` and `REPORT.md` quote but the
test suite doesn't reproduce. They were run in the cloud session where the goal was written, and they are
kept here so nothing lives only there.

They are records, not part of the tests. Paths inside them point to that session's folders
(`/home/user/AIresume/...`, `/tmp/claude-0/...`). To rerun one, point it at your own clone first.

| File | What it is | What it supports |
|---|---|---|
| `decisions/dsr_budget.py`, `dsr_budget_output.txt` | Deflated Sharpe Ratio thresholds, power and the program's chance of success against the number of variants. It is first checked against the worked example in Bailey and López de Prado's paper | decision 5, the research budget |
| `decisions/dsr_addendum.py`, `dsr_addendum_output.txt` | the same program-level figures under other priors, other sizes of real edges, and other conventions | decision 5 |
| `decisions/undercount.py`, `undercount_output.txt` | how often G1 passes a strategy with no edge when fewer variants are counted than were run, how noisy a half-history Sharpe ratio is, and a 189-day forward window | KR6.1, KR1.9 |
| `decisions/budget/` | the version 3 goal run with 20 and with 30 variants (`goal_n20.toml`, `goal_n30.toml`, their outputs, the script) | decision 5: 30 against 20 |
| `decisions/calc_dynalloc.py` | Little's law, the risk budget, notional against stop distance at the 4% overnight cap, and costs | decision 2, no fixed number of positions; decision 1, overnight size |
| `decisions/exp_ar1.py` | G1's power with 2,250 or 2,400 days of history and a floor on each half's Sharpe of 0.5, 0.25 or none, under normal and autocorrelated returns | KR1.1's 2,400 days and KR1.9's 0.25 floor |
| `decisions/seq_sim.py`, `decisions/exp_live.py` | the sequential live test's first design (its target, stop, halving line and cap) and its stop at −2.5 or −2.75 | KR8.2 in versions 3 and 4; round 5 moved the stop to −2.3 (below) |
| `decisions/mintrl.py` | how long a forward test must run to confirm a Sharpe of 1.5 (minimum track record length) | "the live test needs one to two years" |
| `round5/live.py`, `live.txt` | the live test at stops from −2.0 to −2.5, with and without the cap, under four noise shapes: false stops, dead strategies, and decays | round 5's move of the stop from −2.5 to −2.3, the only setting that met every bar fixed in round 3 |
| `round5/slow_m37.json`, `slow_m37.txt` | GT-10's slow run: the live test without its cap | the cap check, caught by GT-4 in all four noise shapes |
| `review-v4-circularity/scripts/` | the scripts the circularity reviewer used against version 4 (commit 18e3e74): mutant generation, comparison, the decay simulation, the price-data probes | `reviews/v4/tests-circularity.md` |
| `review-v4-circularity/mutants.txt` | the 56 defects that reviewer planted in version 4, one per entry | the same review; GT-10 now runs them, adapted, on every test run |

Not kept here:
- the papers, pages and software packages downloaded during the research and reviews. They are
  third-party material and were read only as data; the reports cite where each came from;
- intermediate test runs from rounds 1 to 4. `REPORT.md` gives their figures, and git history keeps the
  final output of each round in `results/`.

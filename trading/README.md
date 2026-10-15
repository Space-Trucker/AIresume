# Trading

An autonomous trading system for US stocks and ETFs, built top-down: the goal first, then the
requirements, then the architecture, then the code. It is independent of everything else in this
repository.

**Status: requirements and design, slice A (the plumbing paper bot); goal frozen.** The goal is defined, tested and independently reviewed twice.
Version 5 answers the review of version 4, and its tests hold their own bars, fixed outside the goal,
and must catch 70 deliberately broken copies of it. Any decision can still be overturned (the end of
`GOAL.md`). The requirements and design for slice A, a paper bot that proves only the plumbing, are written;
no code exists yet. Nothing can reach Alpaca from here until the owner allows its hosts and adds a paper
key as an environment secret (`goal/REPORT.md`, last section).

| File | What it is |
|---|---|
| [`requirements/REQUIREMENTS.md`](requirements/REQUIREMENTS.md) | slice A's requirements: what the plumbing paper bot must do, each traced to the goal and verified by a test, a drill, a probe or an inspection |
| [`design/DESIGN.md`](design/DESIGN.md) | slice A's design: two hosts, the broker adapter, the order state machine, the kill path, the ledger, testing, and the day-one probes with their fallbacks |
| [`goal/GOAL.md`](goal/GOAL.md) | the goal: mission, what to expect, what changed from what was asked, scope, constraints, risk limits, objectives and key results, gates, controls, and the decisions with their evidence |
| [`goal/goal.toml`](goal/goal.toml) | the same goal, machine-readable; every number in `GOAL.md` comes from here |
| [`goal/METHOD.md`](goal/METHOD.md) | how the goal is defined: the methods combined, and why |
| [`goal/TESTS.md`](goal/TESTS.md) | how the goal is tested: each test's independent oracle, and the bars the tests hold themselves |
| [`goal/REPORT.md`](goal/REPORT.md) | the test results: the goal as first agreed, what failed, each revision and why, the independent review and the response to every finding |
| [`goal/reviews/`](goal/reviews) | the independent reviews: three of version 2 (owner intent, risk and controls, statistics) and four of version 4 (`v4/`: facts, Alpaca readiness, statistics, the tests' circularity) |
| [`goal/results/`](goal/results) | the full output of the latest test runs |
| [`goal/goal_v1.toml`](goal/goal_v1.toml) | the goal as first agreed in conversation, kept for comparison |
| [`goal/goaltests/`](goal/goaltests) | the tests (Python 3.11+, standard library only) |
| [`reports/`](reports) | research reports: the evidence behind each decision in `GOAL.md` |
| [`research_notes/`](research_notes) | the researchers' notes behind each report, every fact labeled by how well it was checked, and `ideas.md`: research ideas not yet in the plan |

```bash
cd trading/goal
python3 -m goaltests                 # test the current goal (about 10 minutes on 4 CPUs)
python3 -m goaltests goal_v1.toml    # test the goal as first agreed
```

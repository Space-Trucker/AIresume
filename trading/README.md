# Trading

An autonomous trading system for US stocks and ETFs, built top-down: the goal first, then the
requirements, then the architecture, then the code. It is independent of everything else in this
repository.

**Status: goal stage.** The goal is defined, tested and independently reviewed. Version 4 settles the
open decisions on researched evidence and the owner's answers; any of them can still be overturned
(the end of `GOAL.md`). No architecture or code exists yet.

| File | What it is |
|---|---|
| [`goal/GOAL.md`](goal/GOAL.md) | the goal: mission, what to expect, what changed from what was asked, scope, constraints, risk limits, objectives and key results, gates, controls, and the decisions with their evidence |
| [`goal/goal.toml`](goal/goal.toml) | the same goal, machine-readable; every number in `GOAL.md` comes from here |
| [`goal/METHOD.md`](goal/METHOD.md) | how the goal is defined: the methods combined, and why |
| [`goal/TESTS.md`](goal/TESTS.md) | how the goal is tested, and each test's independent oracle |
| [`goal/REPORT.md`](goal/REPORT.md) | the test results: the goal as first agreed, what failed, each revision and why, the independent review and the response to every finding |
| [`goal/reviews/`](goal/reviews) | the three independent reviews (owner intent, risk and controls, statistics) |
| [`goal/results/`](goal/results) | the full output of the latest test runs |
| [`goal/goal_v1.toml`](goal/goal_v1.toml) | the goal as first agreed in conversation, kept for comparison |
| [`goal/goaltests/`](goal/goaltests) | the tests (Python 3.11+, standard library only) |
| [`reports/`](reports) | research reports: the evidence behind each decision in `GOAL.md` |
| [`research_notes/`](research_notes) | the researchers' notes behind each report, every fact labeled by how well it was checked |

```bash
cd trading/goal
python3 -m goaltests                 # test the current goal (about 7 minutes)
python3 -m goaltests goal_v1.toml    # test the goal as first agreed
```

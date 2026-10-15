# Trading

An autonomous trading system for US stocks and ETFs, built top-down: the goal first, then the
requirements, then the architecture, then the code. It is independent of everything else in this
repository.

**Status: goal stage.** The goal is defined, tested and independently reviewed (version 3). It awaits
the owner's decisions, listed at the end of `GOAL.md`. No architecture or code exists yet.

| File | What it is |
|---|---|
| [`goal/GOAL.md`](goal/GOAL.md) | the goal: mission, what to expect, what changed from what was asked, scope, constraints, risk limits, objectives and key results, gates, controls, decisions for the owner |
| [`goal/goal.toml`](goal/goal.toml) | the same goal, machine-readable; every number in `GOAL.md` comes from here |
| [`goal/METHOD.md`](goal/METHOD.md) | how the goal is defined: the methods combined, and why |
| [`goal/TESTS.md`](goal/TESTS.md) | how the goal is tested, and each test's independent oracle |
| [`goal/REPORT.md`](goal/REPORT.md) | the test results: the goal as first agreed, what failed, each revision and why, the independent review and the response to every finding |
| [`goal/reviews/`](goal/reviews) | the three independent reviews (owner intent, risk and controls, statistics) |
| [`goal/results/`](goal/results) | the full output of the latest test runs |
| [`goal/goal_v1.toml`](goal/goal_v1.toml) | the goal as first agreed in conversation, kept for comparison |
| [`goal/goaltests/`](goal/goaltests) | the tests (Python 3.11+, standard library only) |

```bash
cd trading/goal
python3 -m goaltests                 # test the current goal (about 4 minutes)
python3 -m goaltests goal_v1.toml    # test the goal as first agreed
```

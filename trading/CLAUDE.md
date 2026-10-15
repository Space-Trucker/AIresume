# Trading project

## The owner's standing rules

- Never use a Fable model (claude-fable-*) for anything in this project. That covers the trading
  system's decisions, research, reviews, monitoring, operations, subagents and workflows, and writing
  the code. The owner asked for this; use another Claude model.
- Keep the scope tight and follow the plan below. Don't add reviews, research or long simulation runs
  unless a decision depends on them.
- The Alpaca key never goes into the repository, the code or a chat. It lives in environment variables
  (`APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`), and it is a paper key until G3.
- Work only in this `trading/` folder. It is independent of the rest of the repository.
- Don't read other sessions or their transcripts. Work from this folder's files.

## Where things stand (2026-10-15)

The plan, top-down:
1. the goal (done);
2. requirements and design (done for slice A);
3. the plumbing paper bot (next);
4. the research harness and its data;
5. G1;
6. G2.

What exists:
- **The goal, version 5, frozen.** `goal/GOAL.md` and `goal/goal.toml`. It changes only if building or
  testing shows it wrong.
- **The goal's tests.** Run `cd goal && python3 -m goaltests`: 585 of 585 checks pass. A run takes
  about 10 minutes on 4 CPUs and downloads its price data once, pinned and hash-checked. Their bars are
  in `goal/goaltests/anchors.py`. `goal/REPORT.md` records every round and every review.
- **The research.** `reports/` and `research_notes/` hold the evidence behind each decision in the goal.
- **Research ideas.** `research_notes/ideas.md`, none of them in the plan yet: a news-reading model fenced
  by date (a candidate for step 4), removing a model's knowledge after a date (parked), and a frontier
  model pruned down to finance (not pursued).
- **Slice A.** The plumbing paper bot: `requirements/REQUIREMENTS.md` (SR-A-01 to SR-A-40) and
  `design/DESIGN.md`. It trades a fixed test pattern in five index ETFs and claims no edge.

Next, slice A's build order (`design/DESIGN.md`):
- against a fake broker, no network needed: the adapter and the ledger, then the order manager, risk
  checks, reconciler and supervisor, then the watchdog and lease, then the status page, alerts and daily
  report, then the fault-injection tests;
- then, with access: the day-one probes, and a paper burn-in of at least 20 trading days.

The owner still has to provide:
- the paper key, in environment variables;
- two always-on machines, one for the bot and one for the independent kill path;
- two alert channels;
- a bucket for the off-host log copy;
- the market data plan: consolidated data at $99 a month, or free IEX data for the plumbing only.

There is also an open question for the owner: whether the review panel may use another company's model.

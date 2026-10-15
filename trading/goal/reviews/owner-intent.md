# GT-9 review: owner intent and goal quality

An independent reviewer, given only `METHOD.md`, `GOAL.md`, `goal.toml`, `goal_v1.toml` and the owner's
instruction, reviewed the goal as it stood at commit `dbc6b77`. The reviewer did not see the tests or
their results. This is the reviewer's report, lightly condensed. The response to each finding is in
`REPORT.md`.

## Findings

**O-1 (blocker). Paper trading no longer has to make money, but the mission says it does.**
- The owner said: "It has to prove on a paper account that it makes money after realistic costs." G2
  passed on combined PSR, a shortfall test and the O2–O5 key results.
- With at least 2,000 history days pooled with 60–120 paper days, paper is 3–6% of the sample. A paper
  Sharpe of −0.5 after a G1 Sharpe of 1.5 still passes (combined PSR 0.99997, shortfall p = 0.084).
- The meaning of "lose" in the extension rule was undefined.

Proposed:
- A G2 key result: net absolute P&L over the paper period, after costs and conservative revaluation,
  above zero.
- Define "lose" the same way.
- Put it to the owner, or rewrite the mission.

**O-2 (blocker). At least eight values the owner stated were changed without being flagged.**
- Positions went from 5 to 10.
- Overnight caps were added.
- Paper trading went from 4–8 weeks to 12–24 weeks.
- The weekly "improves" objective was dropped.
- Live profit and loss was dropped.
- "Beats the cost" became "twice the cost".
- "No borrowed money to start" became a permanent non-goal.
- "Watches a shortlist" became the whole universe every minute.
- The AI model and fast code were removed.
- The claim that "22 of 22 controls were missing" overstated version 1's gaps: version 1 did name a kill
  switch and a risk manager.

Proposed: a change table (owner's value, new value, reason, decision), copied into the owner's decisions.

**O-3 (blocker). The owner's holding periods were overridden.**
- "Seconds" disappeared.
- The 150-minute edge horizon became a constraint and a non-goal, although the gates already reject
  strategies that can't pay their costs. It only decides where research is spent, which is the owner's
  call.
- The rule that a fill pays the half-spread, applied to limit orders, ruled out passive execution.
- The horizon rule had no metric.

Proposed:
- Restore "from seconds" in the mission.
- Make the edge horizon a recommendation, and offer "keep my holding periods; let G1 judge".
- If the horizon is kept, make it measurable.

**O-4 (blocker). The activity plan breaks the goal's own overnight limits.**
- 25 trades a week held two days keeps about 10 positions open: all ten slots, about 100% gross, nearly
  all of it overnight, against a 25% overnight cap.
- The cost drag, required signal and owner decision 3 all rest on that plan.
- The 10-a-week activity floor collides with the entry rule and rewards forcing marginal trades.

Proposed:
- One consistent plan, put to the owner.
- The entry rule overrides the floor, which becomes a review trigger.

**O-5 (blocker). The goal never says how likely success is, how long it takes, or what it costs.**

On the goal's own numbers:
- **Odds:** about a one-in-three chance (an upper bound) of a real edge reaching real money.
- **Time:** roughly 5–16 months to the first real dollar, and about two years to full capital.
- **Money:** the data plan, the history, the reviewer and model costs are never totalled.

Proposed: a "what to expect" section, derived from `goal.toml` and checked by a test.

**O-6 (major). "Excess return" is not defined well enough to compute, and no gate required absolute
profit.**

A net-short book in a rising market can show excess return while the account loses money.

Proposed:
- A formula: net return minus beta times SPY, with beta stated.
- Net absolute return above zero at G1 and G2.

**O-7 (major). The AI model vanished.**
- A pre-trained language model has seen the history up to its training cutoff. A walk-forward G1 over
  2016–2026 would therefore be contaminated.
- A change of model or prompt was not counted as a variant.

Proposed:
- Record the owner's design wish.
- Count a model's results in G1 only after its training cutoff.
- Make every model or prompt change a new variant.

**O-8 (major). The owner's weekly improvement loop was dropped.**
- There was no rule for retiring a strategy whose live edge decays.
- There was no way to validate a change once the history is used up.

Proposed:
- An "improve and retire" objective.
- A monthly test against G1's estimate that halves, then stops, a strategy.
- Forward validation of changes.
- A rule for when the variant budget renews.

**O-9 (major). Several key performance parameters (KPPs) can't be judged without guessing.**
- **Live cost:** KR1.6's threshold was the planning average, not the per-trade model.
- **Breaches:** KR2.1 counted gap losses as breaches.
- **Drawdown:** the halt fired at the KR2.2 level, so the KPP failed before the halt could act.
- **Kill switch:** KR2.4 promised to close positions outside the session and in halted names.
- **Safe state:** "fail safe" was undefined.
- **Daily loss:** the day's starting equity was undefined.

Proposed fixes for each.

**O-10 (major). Decisions only the owner can make were missing.**
- The research budget, and whether a stop is final.
- Who the independent reviewer is.
- The owner's availability for alerts.
- The intended capital: Alpaca requires $2,000 of equity to sell short; capacity grows with capital;
  taxes.
- The note on the pattern-day-trader rule was out of date: Alpaca dropped it on 2026-06-04.

**O-11 (major). The goal did not follow its own method.**
- **GQM:** the questions were missing.
- **KAOS:** goal kinds were missing below the objectives.
- **IPS:** the return objective was not stated as a return, and there was no risk objective.
- **ISO 29148 singularity:** O5, KR4.2 and KR5.1 each held two requirements.
- **Vague words:** "about", "fail safe", "near its threshold", "lose".

**O-12 (major). GOAL.md and goal.toml disagreed, and goal.toml was not the single source of every
number.**
- KR5.1 had two metrics but one threshold.
- KR4.2's "no difference at the close" was not encoded.
- KR6.2 applied to every gate but was assigned only to G1.
- The per-gate false-pass bounds were not published.
- The outcome was undefined if G2 had fewer than 300 trades after 120 days.
- Many numbers appeared only in prose: slippage, fees, variants per cycle, the twice-cost factor, the
  order limits.

## Reviewer's overall judgment

"Not yet fit to go to requirements and architecture, but close; it mostly needs edits and one conversation
with the owner rather than a redesign." The method is sound, and the evidence standards are a large step
up from version 1. Four things had to be fixed first: the paper gate (O-1), the activity plan (O-4), the
undefined excess return (O-6) and the KPPs that can't be judged (O-9). "The owner would recognize the
risk rules but not the system." The goal told the owner only part of what its own numbers imply about
the odds and the timeline.

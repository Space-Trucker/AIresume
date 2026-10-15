"""The tests' own bars and reference values, fixed outside the goal.

Added in round 5, after the independent review of version 4 found the statistical tests judged by the
goal's own numbers: loosening a tolerance in goal.toml loosened the test. Every number here belongs to
the tests. A goal tolerance looser than the bar here fails as a claim, and the measured rates are
judged against these bars, never against the goal's.

Three kinds of number:

* OWNER: what the owner said in conversation on 2026-10-15, recorded in goal_v1.toml. The goal may be
  stricter, never looser, unless the owner changes it.
* EXTERNAL: a regulation, a published figure or convention, or a property of real prices, with its
  source.
* JUDGMENT: a bar with no outside source. Each says when it was set and what results were known then,
  as METHOD.md's first honesty rule asks. A judgment bar moves only with a reason recorded in
  REPORT.md, and never because a goal fails it.
"""
from __future__ import annotations

# --- OWNER (goal_v1.toml) -------------------------------------------------------------------------
OWNER_MAX_HOLD_TRADING_DAYS = 5      # "minutes up to about 5 days"
OWNER_MAX_HOLD_CALENDAR_DAYS = 7     # "never weeks"
OWNER_RISK_PER_POSITION_PCT = 0.5    # "lose at most 0.5% of the account on any one trade if its stop-loss is hit"
OWNER_DAILY_LOSS_LIMIT_PCT = 2.0     # "stop trading for the day once the account is down 2%"
OWNER_MAX_DRAWDOWN_PCT = 10.0        # "never falls more than 10% below its peak"
OWNER_MAX_GROSS_PCT = 100            # "no borrowed money to start"
OWNER_SESSION = "regular"            # "trade regular market hours only (9:30am-4:00pm New York time)"
OWNER_HOLD_THROUGH_EARNINGS = False
OWNER_MIN_PAPER_TRADES = 300         # "300+ trades" on paper
OWNER_DIRECTIONS = ("long", "short")
OWNER_SMALL_START = 0.25             # "real money, starting small": at most a quarter of the intended capital
                                     # (a judgment on the owner's word, set in round 5 before any check used it)

# --- EXTERNAL --------------------------------------------------------------------------------------
# Statistics
FALSE_PASS_G1 = 0.05       # the conventional 5% level; a Deflated Sharpe Ratio of 0.95 claims exactly this
                           # (Bailey and Lopez de Prado, 2014)
DSR_MIN = 0.95             # the same convention, for the gate's own threshold
FIDELITY_FALSE_FAIL = 0.05  # the 5% level, for failing an honest implementation
COHEN_POWER = 0.80         # the convention for a test's power (J. Cohen, 1988); reported, see JOINT_POWER
G2_CHANCE = 0.50           # a gate that requires a positive excess return passes a strategy with no edge and
                           # costs of zero or more at most half the time; above that it rewards something
                           # other than edge, such as the market's drift
# Base rates (GT-8's sources)
PRIOR_CEILING = 0.10       # ten times the share of day traders who are reliably profitable, under 1%
                           # (Barber, Lee, Liu and Odean, 2014); a prior above it ignores the base rates
PUBLISHED_EDGE_MULTIPLIER = 0.42  # what remains of a published anomaly after publication (McLean and Pontiff, 2016)
# Markets and regulation
JUMP_EVENT_PRONE_MIN_PCT = 100   # a total loss (SVB, March 2023) or a doubling against a short
JUMP_ETF_MIN_PCT = 13            # the level-2 market-wide circuit breaker (NYSE Rule 7.12): a fall the rules
                                 # expect, and no breaker bounds an overnight gap
JUMP_INTRADAY_MIN_PCT = 10       # the Limit Up-Limit Down band of a Tier 1 stock is 5%, doubled to 10% near the
                                 # open and the close; a pause can reopen beyond the band
MAX_PRICE_COLLAR_PCT = 5         # wider than the Tier 1 LULD band, a collar never binds
MAX_CLOCK_ERROR_MS = 50          # the consolidated audit trail's clock tolerance for industry members (CAT NMS Plan)
BROKER_REQUESTS_PER_MINUTE = 200  # Alpaca's limit per account (readiness review)
BROKER_MIN_EQUITY_SHORTS = 2000   # Alpaca allows margin and short sales only from $2,000 of equity
HISTORY_DAYS_AVAILABLE = 2700    # Alpaca's consolidated history starts in 2016: about 2,700 trading days by October
                                 # 2026 (readiness review); G1's out-of-sample window can't be longer
STRESS_SLIPPAGE_PERCENTILE = 0.95  # a 1-in-20 stress day, for stops on one side and the daily limit (GT-2)

# --- JUDGMENT --------------------------------------------------------------------------------------
# Each: the bar, then when it was set and what was known.
FALSE_REAL_MONEY = 0.01    # round 2, as GT-4's default, before any version's rates were measured
FALSE_HALT_PER_YEAR = 0.10  # round 2, before results
BOOK_FULL_MAX = 0.10       # round 2 (Erlang loss), before results
FIDELITY_POWER = COHEN_POWER  # round 3, when the fidelity test was added; the convention above
LIVE_FALSE_STOP_3Y = 0.10  # round 3, GT-4's default when the live test was added, before results;
                           # version 4 loosened its own claim to 12%, which no longer counts
LIVE_DEAD_HALVE_1Y = 0.50  # round 3, as above
LIVE_DEAD_STOP_3Y = 0.75   # round 3, as above; version 4 set its own claim at 65% after measuring 72-75%
DECAY_HALVE_1Y = 0.50      # round 5, before the decay simulation was first run: a strategy whose gross edge goes
DECAY_STOP_3Y = 0.75       # after 2 good years, its costs remaining, is caught as often as a dead one
DECAY_YEARS_GOOD = 2
DRAWDOWN_CROSS_MAX = 0.001  # round 5, before the drawdown simulation's first run: 1 simulated year in 1,000
JOINT_POWER = 0.50         # round 5, AFTER version 4's and version 5's power was known (version 5: 55.5% to
                           # 70.8%). The reason is not the result: a pair of gates that rejects its own target
                           # more often than it passes it is mis-sized. Per-gate power is reported against
                           # COHEN_POWER, which version 5 misses for G1 under autocorrelated noise (69%)
POSTERIOR_FLOOR = 0.50     # round 5: a strategy that passes every gate must be more likely real than not
REF_PRIOR = 0.05           # round 5, the goal's own prior since round 2, now frozen here so the goal can't move it
REF_EDGE_MEAN_SR = 0.75    # round 5: real edges exponential with this mean, so small edges are commoner (most
                           # published effects are small, and shrink after publication); version 5's posterior
                           # under it (79%) was known when it was chosen

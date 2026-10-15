# Requirements, slice A: the plumbing paper bot

The goal (`../goal/GOAL.md`) says what the system must achieve. This file says what the first part of
it must do: a paper bot that proves the plumbing on Alpaca. It is work package a2 of the Alpaca review
(`../goal/reviews/v4/readiness-alpaca.md`, path a).

**What slice A is.** The bot connects to an Alpaca paper account, places small orders, keeps every
position covered by a stop at the broker, reconciles with the broker, runs the kill paths and raises
alerts, all within the goal's limits. It trades a fixed test pattern, not a strategy, and claims no
edge. Its results are not evidence for G1 or G2.

**What slice A is not.** It does not evaluate the universe every minute (KR3.3) or apply the entry
rule (KR3.1). It has no calibrated gains (KR3.7) and no rotation (KR3.5, KR3.6). It doesn't revalue the
equity of record conservatively, so KR1.5 to KR1.7 and KR2.6 are out. C4's event, short-interest and
industry checks need data Alpaca doesn't provide, and research (G1) needs its own platform. Those are
slice B. Slice A trades only broad index ETFs, which have no earnings and no industry to classify, so it
needs none of that data.

Every number here is read from `../goal/goal.toml`, never copied into code: the system reads its limits
from that file and refuses to start if its version is not the approved one. Values are quoted below for
reading only.

Each requirement says where it comes from (a key result, a control, or an Alpaca review finding A-n)
and how it is verified:
- **T:** an automated test against the fake broker (see `../design/DESIGN.md`);
- **D:** a drill on the paper account;
- **P:** a day-one probe of Alpaca's behaviour, which decides between the design and its fallback;
- **I:** inspection of the records.

## The broker connection

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-01 | Every call to the broker has a timeout: at most 3 s to connect and 10 s to read. | KR2.4, KR4.4 budgets; A-6 | T |
| SR-A-02 | No request that creates, replaces or cancels an order is ever resent automatically. After a timeout or a server error, the order is looked up by its client order id before anything else is sent for that symbol. | C5; A-6 | T, P |
| SR-A-03 | The system makes at most 60 broker requests a minute in normal running and never more than `max_requests_per_minute` (100) in any minute, counting orders, replaces, cancels and polls. After a 429 response it waits until the reset time the broker gives. | C3; A-5, A-16 | T |
| SR-A-04 | The trade-update stream and the market-data stream are wrapped by the system. A drop or reconnect raises an event that triggers reconciliation (SR-A-25), and a fault if not restored within `data_gap_seconds` (30). The stream heartbeat times out in at most 20 s. Every message is parsed by the system, and a message that fails to parse is a fault. | C5, C7; A-6 | T |
| SR-A-05 | Market data comes through one consolidated (SIP) connection, shared by everything that needs quotes. A quote older than `data_max_age_seconds` (5) is stale, and no risk-increasing order uses it. | C2; A-8 | T, P |
| SR-A-06 | The broker library is pinned by version and hash. Before each open, a contract check confirms the fields the system reads; a mismatch blocks trading for the day. | C8; A-6 | T |

## Orders the system owns

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-07 | Every order carries a client order id of the form `<instance epoch>-<strategy version>-<sequence>`, at most 48 characters. An order counts as the system's own when its id, or its chain of replaced or parent orders, leads back to one of the system's ids. Any other order is foreign and fires the kill switch. A change the broker makes to the system's own order (a corporate-action or dividend adjustment) is recorded and alerted, and doesn't count as foreign. | C6, C11; A-11 | T, P |
| SR-A-08 | Only one instance trades at a time. An instance sends orders only while it holds the trading lease, whose fencing epoch the kill path can revoke. | C6; A-5, A-11 | T, D |

## Entering, covering and exiting

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-09 | For each symbol, at most one order change is in flight. The next one waits until the stream or a lookup confirms the last. | A-4 | T |
| SR-A-10 | An entry is an immediate-or-cancel limit order, at most `price_collar_pct` (1%) through the consolidated best bid or offer. It is sent only on a fresh quote that is neither crossed nor locked, with a spread at most `max_spread_multiple` (3) times the name's median. | C2; A-3 | T |
| SR-A-11 | Within `stop_after_fill_seconds` (2) of every fill, partial fills included, the position's whole quantity is covered by a good-till-cancelled stop at the broker. The stop is the stop leg of a one-cancels-other exit with a distant limit leg, or a lone stop if the probe shows that unsuitable. Every uncovered share-second is recorded. | KR2.5; A-3 | T, D, P |
| SR-A-12 | Slice A never adds to an open position. | A-3 | T |
| SR-A-13 | A position is closed by replacing its exit order's limit leg with a marketable price, never by a second order the broker would reject for held shares or as a possible wash trade. A position is never reversed in one step: it is closed, and the close confirmed, first. | C2; A-4 | T, P |
| SR-A-14 | Every stop is good-till-cancelled. Before each open and after every restart, each position's stop is checked at the broker for side, quantity and status, and a missing one is placed again. A stop that was triggered but did not fill is escalated to a marketable close. | KR2.5; A-9 | T, D |
| SR-A-15 | A risk-reducing order is never blocked by the system's own price, universe or event checks. When the broker rejects one, the system clears the conflicting order, sends it again at once and alerts the owner. | C2; A-4 | T |
| SR-A-16 | Orders go out only in the regular session, by the broker's calendar, early closes included. No order carries an extended-hours flag, and the account's overnight trading is switched off. A position trapped outside the session gets its exit at the next open, never queued overnight. | C2; `order_session`; A-13 | T, P |
| SR-A-17 | A position is closed within `max_holding_trading_days` (5) and `max_holding_calendar_days` (7). Slice A's test pattern holds at most 2 trading days, and every position risks at least `min_position_risk_pct` (0.1%) at its stop when it opens, as the goal requires of every position. | KR3.2; risk | T, I |
| SR-A-18 | An order identical to one sent in the last `duplicate_window_seconds` (5) is blocked. At most `max_orders_per_second` (2) orders go out each second. Once a day's order messages reach `max_orders_per_fill` (10) per fill, no new entry is sent that day. | C3; KR5.2 | T |
| SR-A-19 | No order trades against the system's own orders, and a short is sent only on the broker's current easy-to-borrow status. A held short that loses that status is closed within `etb_loss_close_minutes` (30) of the next open. | KR5.1, KR5.3; A-17 | T, I |

## Limits checked before every order

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-20 | Before every order, every limit in the goal's risk section is computed on the positions the broker has confirmed plus every open or unconfirmed order as if filled. That covers buying power, gross exposure, the position caps (`max_position_etf_pct`, the overnight caps), open risk per side and in total, overnight gross, net and dollar net, the drawdown room, and the day's remaining loss budget: new open risk is at most that budget divided by 1.25. An order that would break one is blocked and alerted. | C1; KR2.1 | T |
| SR-A-21 | At most `max_round_trips_per_symbol_per_day` (4) round trips in one name a day, at most `max_traded_pct_per_day` (300%) of equity traded in a day, and at most `max_open_positions_guard` (50) open positions. Reaching one stops new entries until the owner allows them. | C13 | T |
| SR-A-22 | At a loss of `daily_loss_limit_pct` (2%) from the previous session's closing equity, the system goes flat and makes no new entries until the next session. | risk; KR2.3 | T |
| SR-A-23 | When equity falls `max_drawdown_halt_pct` (9%) below its highest close, trading halts within 60 s: the kill switch fires, and the system stays halted until the owner decides, stating whether the peak is reset. In slice A, equity is the broker's own figure; slice B adds the conservative revaluation. | KR2.2; `restart_text` | T, D |
| SR-A-24 | Overnight limits are measured `overnight_check_minutes_before_close` (15) minutes before the close and enforced by then. A limit exceeded by price moves alone is back within it in `passive_cure_minutes` (15), or it counts as a breach. | measurement | T |

## Reconciliation and records

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-25 | Positions, orders and cash are reconciled with the broker continuously from its trade-update stream, by a poll at least every 60 s, after any disconnect, within 60 s of every restart, and at every close. Fills are confirmed against the broker's account activities. A mismatch, an order of unknown state, or a foreign order blocks risk-increasing orders and alerts the owner. An order of unknown state is never sent again blind. | C5; KR4.2, KR4.3; A-6 | T, D |
| SR-A-26 | Every order records, when it is sent, its strategy version, signal, expected gain, expected cost and risk. In slice A the signal is the test pattern's step and the expected gain is "none: a test order". | KR7.1 | I |
| SR-A-27 | Every order, fill, decision, alert, acknowledgement and state change goes to an append-only log in which each entry carries the hash of the one before. The log is copied off the host every day and kept at least 5 years. | C5; RT-11 | T, I |

## Kill switch, kill path and faults

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-28 | The kill switch, available to the owner at any time and fired by the drawdown halt, cancels every order within 60 s and closes every tradable position within 60 s. It asks the broker to close all positions with their orders, then polls every 2 to 5 s and retries each remaining symbol (cancel, confirm, close) until flat or 60 s have passed. A trapped position gets its exit within 60 s of becoming tradable. The owner is alerted within 60 s. | KR2.4; C6; A-4 | T, D |
| SR-A-29 | A second kill path runs on a separate host and doesn't depend on the trading process or its host. When the trading process stops reporting for `alert_seconds` (60), or the owner asks, it revokes the trading lease, suspends trading at the broker, then cancels and closes everything. Outside the session it suspends, alerts, and closes at the next open. It keeps its share of the request budget. | C6; A-5 | D, P |
| SR-A-30 | A fault, as `fault_text` defines it, puts the system in the safe state at once: no new orders, open entry orders cancelled, the owner alerted. Within `stop_check_seconds` (60), every position's stop is confirmed from the broker's own records, and a position without a working stop is closed. A fault left unacknowledged closes every position after `unacknowledged_flatten_minutes` (60), or at `flatten_cutoff_new_york` (15:45, 12:45 on early closes) if that comes first. The system stays stopped until the owner acknowledges. | C7; KR4.4 | T, D |
| SR-A-31 | The owner is alerted within `alert_seconds` (60) of a blocked or rejected order, a data gap, a lost connection, a reconciliation mismatch, or a limit at `limit_warning_fraction` (80%) of its threshold. An alert not acknowledged within `alert_repeat_minutes` (5) is repeated on a second channel. A warning left unacknowledged for `unacknowledged_alert_minutes` (15) stops new entries. Exits and stops keep running, and the daily loss limit and the drawdown halt still apply. | C7 | T, D |
| SR-A-32 | The host clock stays within `max_clock_error_ms` (50) of UTC and is monitored; beyond it, no risk-increasing order is sent. | C14 | T |
| SR-A-33 | The account's margin multiplier is set to the lowest value that still allows the test pattern's shorts. | C6; A-12 | P |

## The owner's view

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-34 | The owner can see profit and loss and open positions, no more than 60 s old, at any moment of the session. | KR7.2 | D |
| SR-A-35 | A daily report reaches the owner by `report_deadline_new_york` (17:00) every trading day. It covers orders, fills, positions, profit and loss, each limit's peak use, alerts and their acknowledgements, uncovered share-seconds, reconciliation results, and drills. | KR7.3 | I |

## Operation

| ID | Requirement | From | Verified |
|---|---|---|---|
| SR-A-36 | Broker keys stay outside the code and the repository, in each host's secret store. Paper and live keys are separate, and only the trading process and the kill path can read them. Keys are rotated every 90 days outside the session, following the runbook. The account uses two-factor sign-in. | C11 | I |
| SR-A-37 | Changes are versioned, tested against the fake broker, deployed only outside the session, and can be rolled back. Before each open, every component is checked to run the approved version. | C8 | I |
| SR-A-38 | A written runbook covers every alert and fault the system can raise, and every drill. | C8; KC-4 | I |
| SR-A-39 | The system is running, connected and able to place orders in at least 99.5% of session minutes each month. The broker's own outages are counted apart. | KR4.1 | I |
| SR-A-40 | Drills on paper: the kill switch on both paths, a stop acting while the system is stopped, a restart, alert repetition, and the safe state. Each runs before the burn-in ends and then every 20 trading days. The burn-in runs at least 20 trading days. | KR2.4, KR2.5, KR4.4; A-9 | D |

## Coverage of the goal

Slice A meets these in full on paper: KR2.1 for the limits it trades under, KR2.2, KR2.3, KR2.4,
KR2.5, KR3.2, KR4.1 to KR4.4, KR5.1 to KR5.3, KR7.1 to KR7.3, and controls C1 to C3, C5 to C8, C11,
C13 and C14.

Left to slice B: KR1.x and KR6.x (research and the paper record), KR2.6 to KR2.8 on the revalued
equity, KR3.1 and KR3.3 to KR3.7, KR8.x, C4 (outside data), C9 surveillance of a strategy's orders,
C10 and C12 (reviews), and stocks.

What slice A proves is that the plumbing works on Alpaca's paper simulator. It doesn't prove that live
stops behave the same (A-9), and it proves nothing about an edge.

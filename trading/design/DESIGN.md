# Design, slice A: the plumbing paper bot

How slice A meets `../requirements/REQUIREMENTS.md` (SR-A-nn below). It follows the Alpaca review's
fixes (A-n, `../goal/reviews/v4/readiness-alpaca.md`). Where a fix depends on how Alpaca really behaves,
a day-one probe decides between the design and its fallback (the last table).

## Layout

Two always-on hosts, in different places, so that one failure can't take out both:

| Host | Runs | Why apart |
|---|---|---|
| **T, trading** | one Python process, `trader`: the broker adapter, the data gateway, the order manager, the risk checks, the reconciler, the test pattern, the safety supervisor, the ledger, the owner's status page and the daily report | one process has the fewest moving parts. If it crashes, the stops at the broker and the kill path on host K still act |
| **K, kill path** | `watchdog`: the trading lease, the heartbeat watch, the kill path, and the owner's kill command | C6: a way to stop everything that depends neither on the trading process nor on its host |

Both hosts read the broker key from their own secret store (SR-A-36). Outside services: the Alpaca paper
account, an off-host bucket for the log, and two alert channels.

**Language and libraries.** Python 3.12 with `httpx` and `websockets`, both pinned with hashes. The
system talks to Alpaca's REST and streaming endpoints directly, through its own small models, not
through Alpaca's SDK. The SDK resends orders on errors, sets no timeouts and hides stream reconnects
(A-6), and the system uses only about fifteen endpoints. A contract check before each open confirms the
fields it reads (SR-A-06).

**Configuration.** Every limit is read from `goal/goal.toml` when the process starts, and the process
refuses to start unless that file's version is the approved one. There is no second copy of a limit.

## The trading lease and the kill path (SR-A-08, SR-A-29)

- The watchdog on host K grants one lease. It lasts 30 s and carries an epoch. The trader renews it
  every 10 s over an authenticated connection, and every client order id starts with the epoch
  (SR-A-07).
- Before each order, the trader checks that its lease is current. If it can't renew, because host K is
  down or unreachable, it goes to the safe state and alerts the owner. Without its independent kill
  path, the system doesn't trade.
- The renewals are the heartbeat. If none arrives for `alert_seconds` (60), or the owner sends the kill
  command, the watchdog acts in this order:
  1. revoke the lease by raising the epoch;
  2. suspend trading at the broker;
  3. cancel every order and close every position;
  4. poll every 2 to 5 s until flat, retrying each remaining symbol;
  5. alert the owner.

  Outside the session it does steps 1, 2 and 5, and closes at the next open.
- The watchdog's requests come from the same per-account budget as the trader's. The trader stays at or
  below 100 a minute (SR-A-03), which leaves at least 100 for the watchdog.
- The broker's dashboard, with its own liquidate button, is the third way.

## The broker adapter (SR-A-01 to SR-A-06)

- **Timeouts.** Every call has them: 3 s to connect, 10 s to read.
- **No blind resends.** A request that creates, replaces or cancels an order is never retried. After a
  timeout or a server error, its symbol is marked unknown and the order is looked up by client order id.
  Nothing else is sent for that symbol until the lookup resolves.
- **Read retries.** A read is retried at most twice, with backoff.
- **Request budget.** A token bucket holds the rate to 60 a minute in normal running and 100 at most.
  Exits and kill-switch calls go first. After a 429, the adapter waits for the reset time the broker
  gives.
- **Streams.** Two wrappers, one for trade updates and one for market data, each with a heartbeat that
  times out within 20 s, and with connect and disconnect hooks. A disconnect starts a reconciliation,
  and a fault if it lasts `data_gap_seconds`. The system parses every message itself, and a message it
  can't parse is a fault.
- **Fills.** They come from the trade-update stream and are checked against the account activities at
  every reconciliation.
- **Data gateway.** It holds the one consolidated data connection the account allows (A-8) and keeps
  the latest quote per symbol with its age. A quote older than `data_max_age_seconds` is stale.

## The order manager (SR-A-09 to SR-A-19)

One state machine per symbol. A state changes only on an event the broker has confirmed, and only one
order change per symbol is in flight at a time.

| State | Means | Leaves on |
|---|---|---|
| FLAT | no position, no order | an entry the risk checks allow: an immediate-or-cancel limit order is sent → ENTERING |
| ENTERING | the entry order is live | it ends: the filled quantity, if any, gets a one-cancels-other exit with the stop leg and a distant limit leg → COVERING; nothing filled → FLAT. An entry still live after 1 s is cancelled first |
| COVERING | shares held, the exit order sent | the broker confirms the exit for the whole quantity → COVERED. Uncovered share-seconds are counted from the first fill; the budget is 2 s |
| COVERED | shares held, every share under a broker stop | the exit time, the holding limit, the daily loss limit, the flatten cutoff or the kill switch: the exit's limit leg is replaced with a marketable price → EXITING |
| EXITING | the closing order is live | all shares sold or bought back → FLAT. On a partial fill, the stop leg shrinks with the position |
| UNKNOWN | an order request timed out or failed | the lookup by client order id resolves it → the matching state |
| TRAPPED | the symbol is halted, the session is closed, or the broker can't be reached | the first moment it can be traded: the exit goes out → EXITING |

Slice A never adds to a position (SR-A-12) and never reverses one in a single order (SR-A-13). A stop
that has triggered without filling is escalated to a marketable close (SR-A-14). Before each open and
after every restart, every position's stop is checked at the broker and placed again if it is missing.

## Risk checks (SR-A-20 to SR-A-24)

Pure functions of the confirmed positions, the open and unconfirmed orders counted as filled, the latest
quotes, the equity, the previous close's equity, the highest close, and the day's counters. For slice
A's ETFs:
- the drawdown room is the larger of two events. One is a position through `jump_overnight_etf_pct`
  (20%) overnight, or `jump_intraday_pct` (20%) during the session. The other is the overnight dollar
  net through a 13% gap. The larger of the two must fit below the line, after the current drawdown and
  the margin;
- every other limit is checked as the goal states it.

The checks run before every order, and a blocked order is recorded and alerted. The highest close, the
previous close and the counters live in the ledger, so a restart keeps them.

## The test pattern

Slice A trades a fixed pattern, so that every path runs, with no edge claimed:
- **Names.** SPY, QQQ, IWM, DIA and VTI: broad, unleveraged index ETFs, normally easy to borrow, with
  no earnings and no industry. The pattern needs no outside data.
- **Entries.** Three to six a session, at random times between 09:45 and 15:30, in a random name and
  direction. A short goes only on a current easy-to-borrow status.
- **Size.** Each position is 5% of equity with its stop 2% away, so it risks 0.1%, the goal's floor. At
  most 3 are open at once: gross exposure at most 15%, open risk at most 0.3%.
- **Holds.** From 5 minutes to 2 trading days. Some positions are held overnight, so the overnight
  checks and the stop audit before the open both run.
- **Records.** Every order records the strategy version `plumbing-1`, the pattern step as its signal, "none:
  a test order" as its expected gain, and its risk.

## The ledger (SR-A-26, SR-A-27)

- **Format.** One JSON line per event, one file per trading day. Each line holds a sequence number, the
  UTC time, the kind, the content, and the hash of the previous line. Each write is flushed to disk
  before the system acts on it.
- **Restart.** The state is rebuilt from the broker and the ledger together. The broker wins on what is
  held; the ledger supplies the history.
- **Copy.** Every evening the day's file is copied to the off-host bucket and its chain checked. Kept 5
  years.

## Alerts, the owner's view and the report (SR-A-31, SR-A-34, SR-A-35)

- **Alerts.** Sent on two channels. An alert not acknowledged in 5 minutes repeats on the second
  channel. The owner acknowledges with an authenticated link, and the acknowledgement is recorded in
  the ledger.
- **Status page.** A read-only page on host T, behind a password, refreshing every 15 s. It shows
  equity and profit and loss, the positions and their stops, each limit's use, the alerts, and the
  system's state. Its kill button calls the watchdog, not the trader, so it works even when the trader
  is stuck.
- **Daily report.** Built after the close and its reconciliation, and sent by 17:00 New York time.

## Faults and the safe state (SR-A-30)

A supervisor sorts every event into faults and warnings as `fault_text` defines them:
- **On a fault.** It enters the safe state and confirms the stops within 60 s. It flattens at the
  earlier of 60 minutes unacknowledged and 15:45 (12:45 on early closes).
- **On a warning.** It stops new entries after 15 minutes unacknowledged.
- **What never stops.** Exits, stops, the daily loss limit and the halt keep working in every state.

## The clock (SR-A-32)

Both hosts keep time with `chrony`. Each minute the trader reads its offset. Beyond 50 ms it sends no
risk-increasing order and raises a warning.

## Testing

- **A fake broker.** An in-process stand-in for the REST endpoints and streams the system uses. It
  reproduces the behaviours the design depends on:
  - entries that fill in part;
  - exits whose stop shrinks with partial fills;
  - a second sell rejected while a stop holds the shares, and the possible wash-trade rejection;
  - cancels confirmed late;
  - 429s with a reset time, and 504s on submit, both when the order was accepted and when it wasn't;
  - dropped streams, stale and crossed quotes, halts and early closes;
  - an order adjusted for a dividend.

  Every requirement marked T has tests against it, and they run on every change without a network.
- **Fault injection.** Killing the trader in the middle of an order, cutting the network, a 429 storm,
  a 504 on submit, clock drift, and stale data.
- **On paper.** After access come the day-one probes below, then a burn-in of at least 20 trading days
  with the drills in SR-A-40.

## Day-one probes and fallbacks

| Probe on paper | If Alpaca behaves as reported | If not |
|---|---|---|
| an immediate-or-cancel entry, then a one-cancels-other exit; the stop leg shrinks on a partial exit | as designed | a lone stop. To exit, cancel it, confirm the cancel, then close, counting the time uncovered |
| client order ids: length 48, duplicates rejected, lookup after a forced timeout | as designed | shorter ids; resolve unknowns by listing recent orders |
| a second sell rejected for held shares, and the wash-trade rejection | as designed | the one-change rule stays; only the error handling changes |
| cancels and closes while trading is suspended | the watchdog suspends first | revoke the lease, lift the suspension to close, then suspend again |
| buy stops (protecting shorts) not capped into stop-limits; market orders not collared | as designed | buy trailing stops for shorts, or no overnight shorts in slice A; an unfilled elected stop is escalated |
| a margin multiplier of 1 still allows shorts | 1 | the lowest value that does |
| overnight trading can be switched off for the account | switched off | every order is checked for the session flag before it goes |
| consolidated data on the paper key, one connection, reconnect after a killed socket | as designed | IEX data for slice A only, said in the report |
| a position held over an ex-date | the adjusted stop is recognized as the system's own | as designed: the adjustment is recorded and alerted |

## What the owner decides before the build can connect

These are in addition to the access steps in `../goal/REPORT.md`, last section:
1. **Hosts.** Two small always-on machines in different places, for example two cloud servers with
   different providers or zones.
2. **Alerts.** Two alert channels, for example a phone push service and email.
3. **Log copy.** A bucket for the off-host copy of the log.
4. **Market data.** The data plan: consolidated data at $99 a month from slice A on, recommended so
   nothing is built twice, or Alpaca's free IEX data for the plumbing only.

## Build order

1. The fake broker, the adapter and the ledger. None of these needs a network.
2. The order manager, the risk checks, the reconciler and the supervisor.
3. The watchdog and the lease.
4. The status page, the alerts and the daily report.
5. The fault-injection tests.
6. After access: the day-one probes, then the paper burn-in.

The Alpaca review estimates 3 to 5 weeks of building, with fault testing overlapping it. The burn-in
takes at least 20 trading days after access: about 8 to 12 weeks from access to a drilled plumbing bot.

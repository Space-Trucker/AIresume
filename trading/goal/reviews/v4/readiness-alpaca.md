# Readiness review: running the goal on Alpaca

**Independent review of operational readiness, goal version 4, 2026-10-15.** Scope: `GOAL.md` and
`goal.toml` (version 4) checked against what Alpaca provides today. No requirements, architecture or
code exist yet, so this review covers the goal's assumptions and what building to them will take. It
does not review a system.

## Summary verdict

**No, it is not ready. Nothing can be launched yet.** Today there is no Alpaca key. This environment's
network policy refuses every Alpaca host. There is no host that can run unattended, and there is no
code. Alpaca itself is a workable broker for this goal: almost everything the controls need is in its
API. Five points in the goal don't fit how Alpaca works, and each needs a decision before architecture:

1. **Stops on partial fills (KR2.5) can't be met as written** (A-3). Alpaca only activates a
   bracket's stop once the entry has filled completely. It rejects a separate stop placed next to a
   working entry as a potential wash trade, and an open stop holds the shares, which blocks any other
   exit. The fix is an entry and exit pattern (IOC entries, then OCO exits) plus a stated tolerance in
   KR2.5.
2. **The independent kill path (C6) collides with Alpaca's account model** (A-5). Its requests come
   out of the same 200-a-minute account budget a runaway primary can exhaust. It appears to need the
   same key as the trading process, which contradicts C11. And its only fence, `suspend_trade`, is
   undocumented for cancels and liquidations.
3. **Alpaca has no event, short-interest, Rule 201, security-type or industry data** (A-7), all of
   which C4 and the universe definition need. That blocks a strategy under G2, not a plumbing bot.
4. **Consolidated (SIP) data is required, not optional** (A-8). Alpaca also allows one data connection
   per user.
5. **The official Python SDK's defaults break C5 and C7** (A-6). It sets no HTTP timeout, it
   automatically resends a POST after a 504, its stream allows 180 seconds before declaring a
   connection dead, and it reconnects silently and drops messages it can't parse.

**(a) A plumbing-only paper bot** (connects, trades small, keeps stops at the broker, reconciles,
drills the kill switch, alerts) is about **8 to 12 weeks** away once access exists. It could take 6
weeks if every day-one probe confirms the design, and up to about 16 weeks if one overturns it.

**(b) A paper bot trading a strategy under G2** can start at the earliest about **6 months** after
access, more realistically **8 to 15 months**. G2 then needs another 6 to 7 months to run. On the
goal's own odds, the chance that any strategy reaches G2 at all is only about **3 in 10**.

**What the goal already gets right.**
- The pattern-day-trader rule is gone: Alpaca has applied the Intraday Margin Rule since 2026-06-04,
  and it removed the PDT fields on 2026-07-06.
- Shorting needs $2,000 of equity, and easy-to-borrow shorts cost no fee.
- Stops stay live at the broker when the client is gone, and Alpaca has no cancel-on-disconnect. Stops
  can't protect a position through a gap, which the overnight sizing already assumes.
- Paper fills are more generous than the goal's fill model, and paper ignores dividends and corporate
  actions. The equity of record already corrects for both.
- SIP data costs $99 a month, and history goes back to early 2016.
- The hosts the goal lists are the right ones.

**Decisions the owner needs to make before architecture.** These are taken from the findings.

| # | Decision | Finding |
|---|---|---|
| 1 | Accept a reworded KR2.5: every share stopped within seconds of its fill, not "from the moment" | A-3 |
| 2 | Choose how the kill path gets credentials: amend C11, or try an OAuth credential | A-5 |
| 3 | Buy Algo Trader Plus ($99 a month) from the start | A-8 |
| 4 | Provide a persistent host, plus a separate host for the watchdog | A-2 |
| 5 | For (b) only: budget outside data vendors | A-7 |
| 6 | Accept the small wording fixes: early-close flatten, KR2.6 data source, C3 as a request budget, exits outside the session | A-13 to A-16 |

## How this was checked

- **SDK.** The SDK is alpaca-py 0.44.0, the latest on PyPI, uploaded 2026-08-11. The wheel's SHA-256
  (`b54673f967c0c814a5e0223cbb0211a5d9d75a8d107e792872b14e5bae957c03`) matches PyPI's record. It was
  downloaded with `pip download alpaca-py --no-deps --only-binary=:all:` into an empty scratch
  directory, unzipped, and read as plain text. It was never imported, installed or run. SDK paths below
  are relative to the wheel's root, for example `alpaca/trading/models.py:492`.
- **Documentation.** At 14:08 UTC on 2026-10-15, the shell's proxy refused `docs.alpaca.markets`,
  `alpaca.markets`, `paper-api.alpaca.markets`, `api.alpaca.markets` and `data.alpaca.markets`
  (HTTP 403 on CONNECT). The fetch tool could not resolve `docs.alpaca.markets` either. Evidence about
  the docs therefore comes from four other sources:
  - web-search extracts of `docs.alpaca.markets` and `alpaca.markets` pages, marked **[Docs*]**. These
    are the search tool's summaries, not verbatim reads.
  - Alpaca's archived docs repository on GitHub (`alpacahq/alpaca-docs`, read through
    `raw.githubusercontent.com`), marked **[Archived]**. It is older and may be stale.
  - Alpaca forum posts, marked **[Forum]**. Staff replies are noted as such.
  - Status pages and third-party sources, marked **[Status]** and **[3rd party]**.
- **Not tested.** No Alpaca endpoint was called, because no key exists and the hosts are blocked. Every
  behavior marked "unverified" belongs in the day-one probe suite (work package a1).
- **Not read.** Following the brief, this review did not read `REPORT.md`, `../reports/`,
  `../research_notes/` or any session transcript.

## What Alpaca provides today

| Topic | What Alpaca does | Evidence |
|---|---|---|
| Order types and time in force | **Order types for stocks:** market, limit, stop, stop-limit and trailing stop.<br>**Time in force:** day, gtc, opg, cls, ioc and fok.<br>A day order trades only in regular hours and is cancelled after the close. opg and cls orders go to the opening and closing auctions; cls orders are rejected between 15:50 and 19:00.<br>Non-marketable GTC limit orders are price-adjusted for corporate actions. There is no "do not reduce" option. | SDK `alpaca/trading/enums.py:121-136, 228-250` |
| Bracket, OCO and OTO orders | **Support:** all three exist for stocks (`enums.py:103-118`). Bracket and OCO orders need both a take-profit and a stop leg; OTO takes one (`requests.py:255-280`). Time in force is day or gtc only, with no extended hours.<br>**Leg behavior:** the exit legs "won't be active until the first order is completely filled". A partly filled take-profit shrinks the stop to the remaining quantity. Cancelling one order cancels the group.<br>**OCO and replacement:** OCO is exit-only (a limit plus a stop or stop-limit). Bracket and OCO leg prices can be replaced. OTO legs reportedly can't: "only simple orders can be replaced at this time".<br>**Trailing stops:** available only as single orders. | [Docs*] orders-at-alpaca; [Archived] orders.md; [Forum] 1252 |
| Stops when the client is gone, and when they trigger | **Persistence:** orders live at the broker. No cancel-on-disconnect exists in any source found. A day stop dies at the close, so overnight protection needs gtc. Alpaca can cancel GTC orders on reverse splits, mergers and delistings.<br>**Triggering:** stops are "elected on the consolidated print" and then become market orders. Sell stops are not converted to stop-limits. Older docs said buy stops become stop-limits 4% above the stop (below $50) or 2.5% above it; current docs drop that sentence (unverified).<br>**Sessions:** trailing stops "will not trigger outside of the regular market hours". Only limit orders can be eligible for extended hours, so stops act only from 09:30 to 16:00.<br>**Paper vs live:** live stops go to Alpaca's execution partners; paper stops are simulated. | [Docs*] orders-at-alpaca; [Archived] orders.md; [Forum] 6022, 5542; [3rd party] heygotrade |
| Extended hours and 24/5 | **Sessions:** pre-market 04:00 to 09:30, after-hours 16:00 to 20:00, and overnight 20:00 to 04:00, Sunday to Friday, through Blue Ocean ATS.<br>**Eligible orders:** limit orders with `extended_hours=true` and time in force day or gtc. A day order sent after 16:00 without the flag queues for the next session.<br>**Account setting:** 24/5 is on by default for Trading API accounts, and the overnight session can be turned off. Assets carry `overnight_tradable` and `overnight_halted`.<br>**SDK:** the flag is at `requests.py:364`, and the feeds `boats` and `overnight` at `data/enums.py:64-73`. `AccountConfiguration` has no overnight setting (`models.py:582-590`). | [Docs*] 245-trading-for-trading-api, 245-trading |
| Paper versus live | **Fills:** paper fills against the live NBBO, buying at the ask and selling at the bid. There is no price improvement and no market impact, size is not checked against the quote, and random partial fills happen 10% of the time. Opening and closing auction orders fill at the quote, not in the auction.<br>**Not simulated:** regulatory fees, dividends, borrow fees and corporate actions (a split leaves a stale share count).<br>**Delays:** fill delays of 50 to 260 seconds have been reported.<br>**Account:** the default balance is $100,000. A reset wipes history and needs a new key. | [Archived] paper-trading.md; [Docs*] paper-trading; [Forum] 14412, 18223, 14303 |
| API rate limits | **Trading API:** 200 requests a minute per account. Every call counts: orders, cancels, replaces and polls. Over the limit, Alpaca returns 429 with code 42910000 and rate-limit headers. A paid data plan doesn't raise the limit. 1,000 a minute is possible only as a non-retail account, at $0.004 a share.<br>**Market data:** 200 calls a minute on Basic, 10,000 on Algo Trader Plus.<br>**SDK:** retries 429 and 504 three times, 3 seconds apart (`common/constants.py:11-13`, `common/rest.py:127-135, 200-202`). | [Forum] staff 9743, 14120; support increase-api-rate-limit |
| Trade-update stream | **Connection:** `wss://paper-api.alpaca.markets/stream`, stream `trade_updates`.<br>**Events:** new, fill, partial_fill, canceled, expired, done_for_day and replaced. Rarer ones include rejected, pending_*, stopped, calculated, suspended, order_replace_rejected and order_cancel_rejected. Partial fills carry the quantity and price.<br>**Gaps:** no replay of missed events is documented. The fill ledger at `/v2/account/activities` (FILL) has no client order id. | [Archived] streaming.md; [Docs*] websocket-streaming, account-activities; [Forum] 9647 |
| Market-data stream | **Feeds:** `v2/iex`, `v2/sip` and `v2/delayed_sip`.<br>**Channels:** trades, quotes, minute, updated and daily bars, statuses (halts), LULD, imbalances and corrections. `*` subscribes to every symbol.<br>**Connections:** one per user on most plans, including Algo Trader Plus; a second gets error 406. A half-dead connection holds the slot for about 90 seconds.<br>**SDK:** has no LULD subscribe method and defaults to IEX (`data/live/stock.py:22, 63-133`). | [Docs*] streaming-market-data, real-time-stock-pricing-data; [Forum] 10896 |
| Data plans and history | **Basic ($0):** IEX in real time (one venue), 30 symbols on the socket, and SIP history older than 15 minutes.<br>**Algo Trader Plus ($99 a month):** SIP in real time, unlimited symbols, and 10,000 calls a minute. Staff say a paper account with this plan gets SIP.<br>**History:** stocks from 2016-01-04 on both plans, about 2,700 trading days. There is no historical asset list. Delisted tickers may still be queryable, but coverage isn't confirmed. The `asof` parameter links renames (`data/requests.py:101-107`). | alpaca.markets/data; [Docs*] about-market-data-api, market-data-faq; [Forum] 18227, 8493, 19208 |
| Account and configuration | **`/v2/account` fields:** `buying_power`, `regt_buying_power`, `multiplier`, `shorting_enabled`, `trading_blocked`, `trade_suspended_by_user`, `equity` and `last_equity` (equity at 16:00 on the previous trading day) (`models.py:477-561`).<br>**PDT removal:** the PDT fields were deprecated on 2026-06-03 and removed on 2026-07-06. This covers `pattern_day_trader`, `daytrade_count`, `daytrading_buying_power` and the `pdt_check` and `dtbp_check` settings (`models.py:492-493, 501-502, 519-521, 569-575`).<br>**Intraday Margin Rule, since 2026-06-04:** buying power updates in real time, and orders that would create a deficit are rejected before they are sent. A margin call is due within 2 business days. A deficit unmet by the fifth day freezes increases in shorts for 90 days.<br>**`/v2/account/configurations`:** `no_shorting`, `suspend_trade`, `max_margin_multiplier` (documented as "1" or "2"; the SDK says 1 to 4), `fractional_trading`, `trade_confirm_email` and `ptp_no_exception_entry`. | [Docs*] changelog 2026-06-03 and 2026-07-06, the-intraday-margin-rule, margin-and-short-selling; blog |
| Borrow flags | **Asset fields:** `shortable` and `easy_to_borrow` (`models.py:48-49, 63-64`). There is no borrow rate and no Rule 201 flag.<br>**Easy-to-borrow shorts:** Alpaca arranges the locate and charges no borrow or locate fee to Trading API users. Status can change, so check it daily.<br>**Hard-to-borrow shorts:** possible since about mid-2026 through a Locates API (100-share lots, single-use, with fees). SDK 0.44.0 doesn't support it.<br>**Minimum equity:** margin and shorting need $2,000. | [Docs*] margin-and-short-selling; blog htb-trading-api-locates; fee schedule |
| Close-all and cancel-all | **Endpoints:** `DELETE /v2/orders` returns a status per order. `DELETE /v2/positions?cancel_orders=true` returns a status per position, and a 500 when an order can't be cancelled. `DELETE /v2/positions/{symbol}` takes a quantity or percentage (`client.py:203-215, 271-324`).<br>**Constraints:** open orders hold shares, so a sell beyond `qty_available` fails with "insufficient qty available" (`models.py:152, 269-286`). Cancels are asynchronous and can take tens of seconds live. One order can't flip a position from long to short. | [Docs*] deleteallopenpositions; [Forum] 17712, 6024, 11395 |
| Client order ids and idempotency | **Support:** every order takes a `client_order_id` (`requests.py:365`) and can be read back by it through `GET /v2/orders:by_client_order_id` (`client.py:157-174`).<br>**Unconfirmed:** whether Alpaca enforces uniqueness, and the maximum length (48 or 128 characters).<br>**Other ids:** bracket child legs get ids Alpaca generates, and a replace creates a new order id (`models.py:223-224`). | [Docs*] working-with-orders; [Forum] 11405, 11641 |
| Self-trade check | Alpaca rejects an order when an opposite-side order is open in the same symbol. The error is "potential wash trade detected. use complex orders", with reasons such as "opposite side market/stop order exists". | [Forum] 13817, 13689, 18200 |
| Market-order collar | A 2023 support article says market orders become limits 2% beyond the last quote. Whether this applies today to stop-triggered and liquidation orders is unverified. | support article (notional discrepancy) |

## Controls, order limits and key results checked against Alpaca

**Verdicts:**
- **Yes:** works on Alpaca as written.
- **Work:** works, but needs the specific engineering noted.
- **Partly:** needs data or services Alpaca doesn't provide, or part of it can't be done as written.
- **No:** contradicts how Alpaca works, as written.

| Item | On Alpaca | What it takes; what conflicts | Findings |
|---|---|---|---|
| **C1** Limits computed on confirmed positions plus every open or unconfirmed order as if filled | Work | Positions, open orders and buying power are all in the API. Query orders nested to see held legs. Use `buying_power` and `regt_buying_power`, since the day-trading fields are gone. Industry exposure needs an outside classification. Alpaca's own margin check rejects orders that would create a deficit, but that is only a backstop. | A-6, A-7, A-12 |
| **C2** Risk-increasing orders: limit at most 1% through the NBBO, quote at most 5 s old and not crossed or locked, spread at most 3 times the median. Risk-reducing orders never blocked | Partly | Needs SIP: IEX is one venue, not the NBBO. The rule for risk-reducing orders is not in the system's power. Alpaca rejects an exit when an open stop holds the shares, when an opposite-side order is open, or when the stock is halted, and it may collar market orders. | A-4, A-8, A-9 |
| **C3** Duplicates blocked for 5 s; at most 2 orders a second and 120 a minute; 30% of the broker's budget kept | Work | Alpaca's budget is 200 requests a minute per account, counting every call. At 120 orders a minute plus a 30% reserve, only about 20 requests a minute are left for cancels, replaces and polls. The SDK's fixed 3-second retries must go. | A-6, A-16 |
| **C4** Event and corporate-action calendar, easy-to-borrow, Rule 201, short interest and universe limits, checked before the session and before every risk-increasing order | Partly | Alpaca provides corporate actions (dividends, splits, mergers, spin-offs) and the easy-to-borrow flag. It has no earnings, FDA, trial, vote or lockup dates, no short interest or float, no Rule 201 state, and no security-type or industry classification. | A-7, A-17 |
| **C5** Fills recorded; reconciliation from the stream, by a poll at least every 60 s, after a disconnect or restart and at the close; an order of unknown state never resent blind; records kept 5 years | Work | The endpoints are enough: the stream, orders, positions, account, activities and lookup by client id. The SDK defaults are not: no HTTP timeout, automatic resend of a POST after a 504, a stream that reconnects silently and drops messages it can't parse. The records are the system's own. | A-6, A-11 |
| **C6** Kill switch; an independent second path; the broker's controls as a third; margin multiplier as a cap; one instance; strategy version on every order | Partly | The endpoints exist. The second path shares the 200-a-minute budget with a primary that may be running away. It needs a key the primary also holds (C11), and its only fence (`suspend_trade`) is undocumented for exits. Alpaca has no lease for "one instance". It's unverified whether a multiplier of 1 allows shorts, and the broker's cap may be 2 to 4 times equity, far above 100% gross. "Alpaca cancels nothing on disconnect" is correct, though day orders still expire at the close. | A-4, A-5, A-11, A-12 |
| **C7** Alerts within 60 s; a second channel; faults put the system in the safe state; stops confirmed within 60 s; an unacknowledged fault flattens after 60 minutes or at 15:45 | Work | Alerting is the system's own. Detection must be faster than the SDK's 180-second ping timeout and its disabled data timeout. Stops are confirmed from `GET /v2/orders?status=open&nested=true`. On early-close days, 15:45 is after the close. | A-6, A-14 |
| **C8** Change control; the approved version checked before the open | Yes | Doesn't depend on the broker. Pin the SDK and add a broker contract check before each open, because Alpaca changed the account schema twice in 2026. | A-6 |
| **C9** No crossing own orders, intent to trade, no marking the close; daily surveillance | Yes | Alpaca's wash-trade check rejects potential self-crosses. Design so that it never fires. | A-4 |
| **C10** Monthly and quarterly reviews | Yes | Doesn't depend on the broker. | none |
| **C11** Keys outside the code; separate paper and live keys; only the trading process can read them; rotated every 90 days; multi-factor sign-in; an order the system didn't send fires the kill switch | Partly | Paper and live use separate keys and hosts. Rotation is a manual regeneration in the dashboard, which kills the old key at once. Dashboard sign-in has SMS two-factor. "Only the trading process" conflicts with C6's second path unless a second credential (OAuth) works. Orders the broker adjusts can look like orders the system didn't send. | A-5, A-11 |
| **C12** Review panel | Yes | Doesn't depend on the broker. | none |
| **C13** At most 4 round trips in a name a day, 300% of equity a day, 50 positions | Yes | Counters in the system. Alpaca has had no day-trade limits since 2026-06-04. | none |
| **C14** Host clock within 50 ms of UTC, monitored | Work | Needs NTP (chrony) on a persistent host. Alpaca's clock endpoint is only a coarse cross-check. | A-2 |
| **Order limits:** price collar 1%, spread multiple 3, participation 10% | Work | Needs SIP quotes and volume, and each name's median spread from history. | A-8 |
| **Order limits:** duplicate window 5 s, 2 a second, 120 a minute, at most 10 orders per fill, 30% API reserve | Work | Restate as requests against 200 a minute. Count cancels and replaces, since a replace is a new order. | A-16 |
| **Order limits:** alert within 60 s, data gap 30 s, data age 5 s | Work | Change the SDK settings (ping timeout 20 s or less, data timeout about 10 s during the session). Compare SIP timestamps against a disciplined clock. | A-6 |
| **Order limits:** unacknowledged 15 and 60 minutes, flatten at 15:45, stop check 60 s | Work | Needs a variant for early closes, which Alpaca's calendar provides. | A-14 |
| **Order limits:** guards (4 round trips, 300%, 50 positions), clock 50 ms, report by 17:00 | Yes | All in the system. | none |
| **KR2.1** No order breaks a limit | Work | Pre-trade checks in the system. Some limits need outside industry and event data. | A-7 |
| **KR2.2** Halt within 60 s at a 9% drawdown | Work | The kill switch, plus the equity of record computed every minute from SIP marks. | A-4 |
| **KR2.3** Worst day at most 2.5% | Work | Depends on how stops fill. They act in regular hours only, buy stops may be capped by a limit, and market orders may be collared. | A-9 |
| **KR2.4** Kill switch within 60 s; trapped exits; alert | Work | Close all with cancel first, then poll and retry per symbol until flat. Cancels can take tens of seconds live, so paper timing isn't live timing. Halted names are trapped. | A-4, A-5 |
| **KR2.5** Every share stopped for its quantity, partial fills included, and the stop works while the system is down | No, as written | GTC stops do persist and act during regular hours. But partial fills can't be covered "from the moment": bracket and OTO legs wait for a complete fill, and a separate stop next to a working entry is rejected. Needs IOC entries with an immediate OCO or stop, and a stated tolerance. | A-3, A-9 |
| **KR2.6** Realized volatility | Yes | The data source differs between GOAL.md and goal.toml. | A-15 |
| **KR2.7, KR2.8** Drawdown, single jump | Yes | Analysis of the equity of record. | none |
| **KR4.1** Up 99.5% of session minutes | Partly | Needs a persistent host. Alpaca's own outages count unless split out. A crash costs up to about 90 s of market data. | A-2, A-8, A-18 |
| **KR4.2** Matches the broker within 60 s of a restart | Work | A few REST calls, so feasible. | A-6 |
| **KR4.3** Positions, orders and cash match at the close | Work | Paper cash omits dividends, fees and corporate actions. Reconcile the broker's raw state, and keep the corrections in a separate ledger. | A-10 |
| **KR4.4** Safe state within 60 s, with stops confirmed | Work | Detection must be faster than the SDK defaults allow. Confirm stops from nested open orders. | A-6 |
| **KR5.1** No self-trades | Yes | Alpaca enforces this with its wash-trade check. The design should avoid triggering it. | A-4 |
| **KR5.2** At most 10 orders per fill | Yes | Define what counts. | A-16 |
| **KR5.3** No short without easy-to-borrow status | Yes | Read the asset's flag just before the order. Alpaca's list changes daily. | A-17 |

## Findings

Severity: **blocking** prevents a launch, or makes a key result fail by construction. **Major** needs
design or rework before the path in question is credible. **Minor** is a clarification or a small fix.

### A-1 · Blocking (paths a and b) · No access to Alpaca from here, and no key

**Finding.** At 14:08 UTC on 2026-10-15, this environment's network policy refused every Alpaca host
(HTTP 403 on CONNECT). The refused hosts were `paper-api.alpaca.markets`, `api.alpaca.markets`,
`data.alpaca.markets`, `docs.alpaca.markets` and `alpaca.markets`. No Alpaca account or key exists.
Nothing can be connected, probed or drilled until both change.

**Evidence.** The proxy's relay log at 2026-10-15T14:08:12Z to 14:08:18Z. The hosts the SDK uses, in
`alpaca/common/enums.py:9-16`:
- `https://paper-api.alpaca.markets`
- `https://api.alpaca.markets`
- `https://data.alpaca.markets`
- `wss://stream.data.alpaca.markets`
- `wss://paper-api.alpaca.markets/stream`

Also GOAL.md:614-617.

**Fix.** The owner, in this order:
1. Open an Alpaca account, turn on two-factor sign-in, create a paper key, and store it in a secret
   store outside the repository (C11).
2. Open this environment's settings: the cloud environment menu in the session's title bar, then
   Edit, then Network access. Leave package managers allowed, and add these under Allowed domains:
   - `paper-api.alpaca.markets`, which serves both REST and the trade stream
   - `data.alpaca.markets`
   - `stream.data.alpaca.markets`
   - for checking documentation: `docs.alpaca.markets`, `alpaca.markets` and `status.alpaca.markets`

   Leave `api.alpaca.markets` (live trading) out until G3.
3. Subscribe to Algo Trader Plus (see A-8).

This takes under a day of the owner's time.

### A-2 · Blocking (paths a and b) · No host that can run unattended

**Finding.** This development environment lasts only for a session: a new session starts on a fresh
machine. That rules it out for three things:
- running through every session (KR4.1 asks for 99.5% of session minutes);
- keeping a disciplined, monitored clock (C14);
- hosting C6's second kill path, which must depend "neither on the trading process, nor on its host".

The goal names a broker but no place to run.

**Evidence.** GOAL.md:343 (KR4.1), :471 (C6), :479 (C14). The environment documentation says a
session's machine is replaced when a new session starts.

**Fix.** Decide this in architecture:
- a persistent cloud VM with a process supervisor, chrony and off-host log shipping;
- a second, independent small host or scheduled function for the watchdog;
- two alert channels.

Keep this environment for development and day-one probes once the hosts are allowed.

### A-3 · Blocking (KR2.5 as written; the core of path a) · Partial fills can't be stopped "from the moment" on Alpaca

**Finding.** KR2.5 asks that every share be covered by a stop at the broker "for its quantity, partial
fills included". The risk table adds "from the moment it is bought or sold short". Alpaca offers no
way to do that for a partly filled entry:
- Bracket and OTO exit legs "won't be active until the first order is completely filled". Their time in
  force can only be day or gtc, so there is no IOC or FOK entry with an attached stop.
- A separate stop next to a still-working entry is an order on the opposite side, and Alpaca rejects it
  as a potential wash trade.
- OTO legs reportedly can't be replaced: "only simple orders can be replaced at this time".
- A third-party report says that when a bracket's entry fills partly and is then cancelled, the filled
  shares are left with no resting stop. A forum question asking for a gap-free workflow for exactly
  this case (thread 19417) has no answer in the extracts.

So a share from a partial fill is uncovered until the system acts. Adding to an open position has the
same problem: the add, a buy, is rejected while the position's sell stop is open, so the stop has to be
cancelled first.

**Evidence.**
- [Docs*] https://docs.alpaca.markets/us/docs/orders-at-alpaca: legs inactive until the entry is
  completely filled; time in force day or gtc; no extended hours; a partly filled take-profit shrinks
  the stop.
- [Archived] https://raw.githubusercontent.com/alpacahq/alpaca-docs/master/content/trading/orders.md:
  "If any one of the orders is canceled, any remaining open order in the group is canceled"; for OTO,
  "order replacement is not supported yet".
- SDK: `alpaca/trading/requests.py:255-280` and `alpaca/trading/enums.py:228-250`.
- [Forum] https://forum.alpaca.markets/t/i-am-getting-a-error-for-when-trying-to-sell-using-my-api/13689
  ("opposite side market/stop order exists").
- [Forum] https://forum.alpaca.markets/t/patching-a-leg-of-oto-order-not-working/1252
- [Forum] https://forum.alpaca.markets/t/supported-protective-stop-workflow-for-a-partially-filled-day-entry-order/19417
- [3rd party] https://github.com/dd-jp/samurai-trading-system/issues/1938
- GOAL.md:163, :332; goal.toml:464-476.

**Fix.**
1. Enter with a simple IOC limit order, within C2's collar. It fills at once, partly or fully, and the
   rest is cancelled, so no entry stays working.
2. On each fill event, send at once a GTC OCO exit for the position's whole quantity: a take-profit
   limit set far away plus the stop. Use a GTC stop alone if OCO proves unsuitable. To exit, replace
   the OCO's limit price with a marketable one. The stop leg stays in place and shrinks with partial
   fills, as documented.
3. Don't add to an open position while its stop is live. If adds are needed: cancel the stop, confirm
   the cancel, add, then stop again. Do this only while the system is healthy, and count the time
   uncovered.
4. Reword KR2.5: "every share is covered by a GTC stop at the broker within 2 seconds of its fill, and
   within 60 seconds after any restart; uncovered share-seconds are recorded and reported; at every
   15:45 check no share is uncovered". Drill it.
5. Confirm each rejection and the OCO behavior on paper on day one (work package a1).

### A-4 · Major · Exits and the kill switch must work around held shares, wash-trade rejections and slow cancels

**Finding.** Alpaca's own checks can reject a risk-reducing order, so C2's promise that a
risk-reducing order "is never blocked" is not in the system's power:
- An open stop holds the position's shares. Any other sell is rejected with "insufficient qty
  available" until the stop is cancelled or replaced (`qty_available`, `held_for_orders`).
- A new order opposite an open order is rejected as a potential wash trade.
- Cancels are asynchronous. A moderator warns that confirmation "can take tens of seconds" in live
  trading.
- Close-all returns a status per position: "if an order can no longer be cancelled, the server will
  respond with status 500".
- One order can't take a position from long to short.
- A halted stock doesn't trade.

**Evidence.**
- SDK: `alpaca/trading/models.py:152` (`qty_available`), `:269-286` (`held_for_orders` in a failed
  close), and `alpaca/trading/client.py:203-215, 271-324`.
- [Docs*] https://docs.alpaca.markets/reference/deleteallopenpositions-1
- [Forum] https://forum.alpaca.markets/t/alpaca-py-apierror-insufficient-qty-available-for-order/17712
  and related "insufficient qty" threads, including the moderator's reply on cancel delays.
- [Forum] https://forum.alpaca.markets/t/bogus-rule-potential-trade-wash-detected/13817
- [Forum] https://forum.alpaca.markets/t/switching-from-long-to-short-position-at-market-close/11395
- [Forum] https://forum.alpaca.markets/t/sell-stop-order-was-not-filled-after-halt/5940
- GOAL.md:467.

**Fix.**
1. Exit by replacing the OCO's limit leg (A-3), never with a second sell.
2. Allow one change in flight per symbol, each confirmed by the stream or a lookup before the next is
   sent.
3. Make the kill switch `DELETE /v2/positions?cancel_orders=true`. Then poll every 2 to 5 seconds and
   retry each remaining symbol (cancel, confirm, close) until flat or until 60 seconds pass. Report
   trapped names in an alert.
4. Reword C2: "never blocked by the system's own price, universe or event checks".
5. When a rotation reverses direction in the same name, close and confirm before opening.

### A-5 · Major · The independent kill path (C6) collides with Alpaca's account model

**Finding.** C6 wants a second path that depends neither on the trading process nor on its host, and
that closes everything once the process has been silent for 60 seconds. On Alpaca:
- **Shared budget.** The 200-requests-a-minute budget is per account and shared by both paths. A
  runaway primary, which is the case C6 exists for, can starve the kill path with 429 errors.
- **One key.** An account appears to have one key pair: regenerating it invalidates the old one, and
  the secret is shown once. The kill path would then hold the same key as the trading process,
  contradicting C11's "only the trading process can read them". OAuth could give a second credential,
  but an OAuth app needs Alpaca's approval to trade, and its token covers one paper and one live
  account.
- **Fencing.** To stop a primary that is alive but cut off from the watchdog, the only API control is
  `suspend_trade`, which makes the account "unable to submit new orders". Whether cancels and close-all
  still work while it is set is undocumented.
- **Outside the session.** Close-all sends day orders, which queue for the next open. The goal's
  session rule doesn't cover this.
- **Key rotation.** C11's 90-day rotation is a manual dashboard action that kills the old key at once.
- **Third path.** The dashboard's "liquidate all positions" button, the third way, is described only by
  users.

**Evidence.**
- [Forum] staff on 200 a minute per account:
  https://forum.alpaca.markets/t/trading-api-limitations/9743 and
  https://forum.alpaca.markets/t/429-rate-limit-exceeded-when-creating-orders/14120
- Keys: https://alpaca.markets/learn/api-key-security-best-practices-for-alpaca-builders (paper and
  live keys and hosts are separate), and user guides that say regenerating invalidates the old keys and
  shows the secret once (https://alpaca.markets/learn/trading-stocks-postman/,
  https://forum.alpaca.markets/t/how-to-get-the-apca-api-key-id-and-then-apca-api-secret-key/4055).
- [Docs*] https://docs.alpaca.markets/docs/using-oauth2-and-trading-api
- SDK: `alpaca/trading/models.py:576` (`suspend_trade`: "Account becomes unable to submit new orders")
  and `alpaca/trading/client.py:496-513`.
- [Forum] https://forum.alpaca.markets/t/unable-to-close-positions/6024 (the dashboard button).
- GOAL.md:471, :476.

**Fix.**
1. The watchdog first sets `suspend_trade=true`, then cancels and closes. Test on paper on day one
   whether cancels and liquidations go through while trading is suspended. If they don't, fence the
   primary with the lease (A-11) and lift the suspension for the close.
2. Cap the primary well below the budget (A-16) so that at least 100 requests a minute stay free. Have
   the watchdog respect `X-Ratelimit-Reset`.
3. Either amend C11 to "the trading process and the independent kill path, on separate hosts", or get
   an OAuth credential for the kill path if Alpaca allows one for a personal app.
4. Define what happens outside the session: suspend and alert, queue no orders, and close at the next
   open.
5. Rotate keys outside the session, following a runbook.
6. Drill all three paths on paper, and once on the live account before G3.

### A-6 · Major · The official SDK's defaults break C5 and C7

**Finding.** The following hold for alpaca-py 0.44.0.
- **No HTTP timeout.** Requests are sent without a `timeout` (`alpaca/common/rest.py:195`). A hung
  connection blocks the caller with no limit, which defeats the 60-second budgets for the kill switch
  and the safe state.
- **Automatic resend.** Responses of 429 and 504 are retried up to 3 times, 3 seconds apart, for every
  method, including `POST /v2/orders` (`alpaca/common/constants.py:11-13`;
  `alpaca/common/rest.py:127-135, 200-202`).
  - A 504 can mean the order was accepted. Resending breaks C5's "an order of unknown state is never
    sent again blind", unless Alpaca rejects a duplicate client id, which is unconfirmed.
  - `TradingClient` exposes no retry settings (`alpaca/trading/client.py:53-86`).
  - The fixed 3-second sleep ignores `X-Ratelimit-Reset`.
- **Trade stream.**
  - It pings every 10 seconds but waits 180 seconds for an answer (`alpaca/trading/stream.py:55-59`),
    three times the 60-second alert budget.
  - It reconnects without telling the application (`:204-241`), so C5's "reconcile after any
    disconnect" has no trigger.
  - A message that fails to parse is logged and dropped (`:126-139`, with the catch-all at `:227-239`).
  - Its comments mention a single-connection slot on this stream too (`:232-234`).
- **Data stream.**
  - The staleness timeout is off by default (`alpaca/data/live/websocket.py:83, 93-99`).
  - The stock stream defaults to IEX (`alpaca/data/live/stock.py:22`) and supports only IEX and SIP
    (`:47-48`).
  - There is no LULD subscribe method.
- **No fill ledger.** `TradingClient` has no account-activities (fill ledger) method; only
  `BrokerClient` does (`alpaca/broker/client.py:530`).
- **Missing events.** `TradeEvent` lacks done_for_day, stopped, calculated, suspended,
  order_replace_rejected and order_cancel_rejected (`alpaca/trading/enums.py:321-333`). They arrive as
  plain strings (`alpaca/trading/models.py:640`).
- **Configuration call.** `set_account_configurations` sends the whole model, including nulls for the
  removed `dtbp_check` and `pdt_check` (`alpaca/trading/client.py:507`;
  `alpaca/trading/models.py:582-590`). Response models silently drop fields the SDK doesn't know, which
  is pydantic's default.

**Evidence.** The SDK lines above.

**Fix.** Write a thin broker adapter of the system's own. It can reuse the SDK's request and model
classes. It needs:
- a timeout on every call (for example, 3 seconds to connect and 10 to read);
- no automatic resend of POST, PATCH or DELETE: after a timeout, look the order up by client id;
- 429 handling that follows the reset header;
- a stream wrapper with connect and disconnect hooks that trigger reconciliation;
- a ping timeout of 20 seconds or less;
- raw messages parsed by the system, with an alert on any parse failure;
- a data staleness timeout of about 10 seconds during the session;
- fills taken from `/v2/account/activities`.

Pin `alpaca-py==0.44.0` (SHA-256 `b54673f9…957c03`), and run a schema contract check before each open
(C8).

### A-7 · Blocking for path (b), minor for (a) · Data the controls need that Alpaca doesn't provide

**Finding.** Alpaca provides corporate actions (dividends, splits, mergers, spin-offs and some
reorganizations) and borrow flags. It does not provide:
- **Scheduled company events:** earnings, FDA dates, trial readouts, shareholder votes and lockup
  expiries (the Events constraint, C4 and KR6.4).
- **Short interest, float and days to cover:** C4's 15% and 5-day limits.
- **Rule 201 state:** the asset has no such field. It must be computed from SIP (a 10% fall from the
  prior close triggers it for the rest of that day and the next) or bought.
- **Security type for the universe:** common stock versus ADR, SPAC, closed-end fund, unit, right or
  warrant; ETFs registered under the Investment Company Act versus ETNs, commodity pools and crypto
  trusts; leveraged and inverse flags.
- **Industry classification:** needed for the 8% overnight industry limit and the industry jump bound.
- **The VIX:** needed for KR1.9.
- **A point-in-time security master for G1:** with delisted names and their delisting returns. Alpaca
  has no historical asset list (staff), and its announcements API excludes delistings and tender
  offers.

**Evidence.**
- SDK: `alpaca/trading/models.py:54-70` (the asset's only fields), plus `alpaca/data/enums.py:151-184`
  and `alpaca/trading/enums.py:253-281` (corporate-action types, no earnings).
- https://alpaca.markets/blog/introducing-corporate-actions-api-announcements/
- [Forum] https://forum.alpaca.markets/t/delisted-tickers/18227 and
  https://forum.alpaca.markets/t/are-alpaca-historical-tick-data-point-in-time/8493
- GOAL.md:147, :150, :469; goal.toml:72-76.

**Fix.** In architecture, choose and budget vendors:
- an earnings and events calendar;
- a security master with history;
- short interest and float;
- a Rule 201 feed, or a computed flag;
- an industry scheme.

Until then, the plumbing bot trades a fixed list (broad index ETFs and a few of the largest stocks) and
closes before known events.

### A-8 · Major · Consolidated data is required, and Alpaca allows one data connection

**Finding.** The free plan can't meet C2 (NBBO, quote age, spreads) or KR3.3 (the whole universe every
minute). It offers IEX, one venue, with 30 symbols on the socket and 200 calls a minute.

Algo Trader Plus ($99 a month) gives SIP, unlimited symbols and 10,000 calls a minute. Staff say it
works with a paper-only account; one third-party tool needed a live key to stream SIP.

Most plans, Algo Trader Plus included, allow one data connection per user, and a second gets error 406.
A half-dead connection holds the slot for about 90 seconds. Three consequences:
- a crash costs up to about 1.5 minutes of data;
- a second instance can't open its own stream;
- the paper and live systems that KR8.1 later runs in parallel can't each open their own stream either.

**Evidence.**
- https://alpaca.markets/data (through search).
- [Docs*] https://docs.alpaca.markets/us/docs/streaming-market-data ("in most subscriptions (including
  Algo Trader Plus) this limit is 1"; error 406).
- [Forum] https://forum.alpaca.markets/t/t-error-code-406-msg-connection-limit-exceeded/10896 (staff:
  90-second timeout for partially dead connections).
- [Forum] https://forum.alpaca.markets/t/free-account-paper-trading-iex-sip-questions/19208
- [3rd party] https://wealth-lab.com/Discussion/Use-Alpaca-SIP-live-data-with-Paper-account-13072
- SDK: `alpaca/data/live/stock.py:22, 47-48` and `alpaca/data/live/websocket.py:462-467, 482-486`.
- GOAL.md:618-621.

**Fix.**
1. Buy Algo Trader Plus at the start of path (a).
2. Run one market-data gateway process, separate from the trading engine, that fans data out to paper
   and later to live.
3. Fall back to REST snapshots, well inside 10,000 a minute, whenever the stream is down.
4. Check on day one that the paper key gets SIP.

### A-9 · Major · What a broker stop does and doesn't do on Alpaca

**Finding.** GTC stops persist when the system is gone, as the goal assumes, but with six caveats:
- **Regular session only.** Stops act only in the regular session. They are elected on the consolidated
  print and become market orders. A gap is filled at the open, as the goal's sizing already assumes.
- **Buy stops may be capped.** Older docs said buy stops, which protect shorts, become stop-limits 4%
  above the stop (below $50) or 2.5% above it. Current docs say only that sell stops aren't converted.
  If the cap still applies, a short's stop won't fill through a gap above its limit, and the short
  stays open after the gap.
- **Market orders may be collared.** A 2023 support article says market orders become limits 2% beyond
  the quote. If that applies to elected stops and liquidations, a fast market can leave them resting.
- **Some stops get cancelled.** Day stops, and day bracket legs, are cancelled at the close. Alpaca can
  cancel GTC orders on reverse splits, mergers and delistings.
- **Paper isn't live.** Live stops are routed to execution partners, while paper stops are simulated. A
  paper drill tests the simulator, not the live path.
- **Halts.** After a halt, a stop may not elect before the next halt (a forum case).

**Evidence.**
- [Docs*] https://docs.alpaca.markets/us/docs/orders-at-alpaca: "Sell stop orders are not converted into
  stop limit orders"; trailing stops "will not trigger outside of the regular market hours"; only limit
  orders can be eligible for extended hours.
- [Archived] orders.md (as above): election on the consolidated print, buy-stop conversion.
- https://alpaca.markets/support/why-do-i-see-a-discrepancy-between-the-notional-value-requested-and-the-order-value-ultimately-filled
  (the 2% collar).
- [Forum] https://forum.alpaca.markets/t/when-is-a-stop-order-triggered/6022
- [Forum] https://forum.alpaca.markets/t/is-gtc-really-gtc-or-do-they-get-cancelled-after-60-days/5542
- [Forum] https://forum.alpaca.markets/t/sell-stop-order-was-not-filled-after-halt/5940
- [3rd party] https://help.heygotrade.com/en/articles/5985234-what-are-the-different-order-types
- SDK: `alpaca/trading/enums.py:237-238`.
- GOAL.md:37-39, :332.

**Fix.**
1. Probe the buy-stop and collar behavior on day one.
2. Watch for stops that were elected but not filled, and escalate them to a marketable close.
3. Make every stop GTC, and audit stops before each open, re-placing any the broker cancelled.
4. Run KR2.5's drill before G3 on the live account, with a minimal position.
5. If buy stops are capped, test a buy trailing stop as a replacement, since Alpaca holds and triggers
   those itself.

### A-10 · Minor · Paper isn't live: what G2 measures needs handling

**Finding.** The goal already revalues paper fills and corrects for corporate actions. Three things
remain:
1. Alpaca's paper account fills a limit order when the quote touches it, fills random partial sizes 10%
   of the time, and has reported fill delays of 50 to 260 seconds. The rerun behind KR1.5 and KR1.6
   should model the paper fill rule when matching trades, and use the conservative model only for
   profit and loss.
2. Paper cash omits dividends, regulatory fees and corporate actions. KR4.3 should reconcile the
   broker's raw state and keep the corrections in a separate ledger.
3. A paper reset wipes the history and needs a new key. It must never happen during G2.

**Evidence.**
- [Archived] https://raw.githubusercontent.com/alpacahq/alpaca-docs/master/content/trading/paper-trading.md
- [Docs*] https://docs.alpaca.markets/us/docs/paper-trading
- [Forum] https://forum.alpaca.markets/t/paper-account-nvda-stock-split-issue/14412
- [Forum] https://forum.alpaca.markets/t/corporate-actions-handeling/19325
- [Forum] https://forum.alpaca.markets/t/paper-trading-fill-delays-of-50-260-seconds-limit-orders-filled-minutes-after-price-crossed/18223
- [Forum] https://forum.alpaca.markets/t/does-a-paid-account-give-more-accurate-paper-market-fills/14303
- GOAL.md:196-199, :229, :345.

**Fix.** As stated in the finding; write all three into the G2 runbook.

### A-11 · Major · Knowing which orders are the system's

**Finding.** Two controls depend on telling the system's own orders apart: C6's "only one instance of
the system trades" and C11's "an order the system did not send triggers the kill switch". On Alpaca:
- There is no lease, and the client order id is the only tag.
- Bracket child legs get ids Alpaca generates.
- Every replace creates a new order id.
- Alpaca adjusts non-marketable GTC limit orders for corporate actions. FINRA Rule 5330 reduces sell
  stops for cash dividends, and Alpaca has no "do not reduce" option.
- The id's maximum length, and whether Alpaca rejects duplicates, weren't confirmed.

The goal allows holding through ordinary dividends. If Alpaca applies Rule 5330 to stops, a held long's
stop changes on an ex-date about every week or two at the planned activity. Treated as foreign, each
such change would fire the kill switch.

**Evidence.**
- SDK: `alpaca/trading/requests.py:365`, `alpaca/trading/client.py:157-174`,
  `alpaca/trading/models.py:223-224, 241` and `alpaca/trading/enums.py:238`.
- [Forum] https://forum.alpaca.markets/t/feature-request-assignable-client-order-ids-for-bracket-sub-orders/11405
- [Forum] https://forum.alpaca.markets/t/updating-profit-and-stoploss/11641
- [3rd party] Rule 5330 summary:
  https://app.certfuel.com/series6/learn/processing-transactions/transaction-processing-and-settlement/adjustment-of-open-orders-rule-5330
- GOAL.md:471, :476.

**Fix.**
1. Use an id scheme of the form `<instance epoch>-<strategy version>-<sequence>`, kept to 48 characters
   or fewer until the limit is confirmed.
2. Treat as the system's own any order whose `replaces` chain or parent leads back to one of its
   orders.
3. Keep a lease with a fencing epoch in a store that both the system and the watchdog can reach.
4. Probe a held long over an ex-date.

### A-12 · Minor · The margin facts are right; two settings need testing

**Finding.** The goal's statements hold:
- Alpaca adopted the Intraday Margin Rule on 2026-06-04.
- The PDT and day-trading fields, including `pdt_check` and `dtbp_check`, were deprecated on 2026-06-03
  and removed on 2026-07-06.
- Shorting needs $2,000 of equity.

Under the new rule, buying power updates in real time, and Alpaca rejects any order that would create a
deficit before sending it. A margin call is due within 2 business days, and a deficit still unmet on the
fifth day freezes increases in shorts for 90 days. At 100% gross, none of this binds.

Two points remain open:
- `max_margin_multiplier` is documented as "1" or "2" (the SDK says 1 to 4). Whether 1 still allows
  short sales is undocumented.
- Accounts above $2,000 may get up to 4 times equity in intraday buying power. The broker's cap on a
  runaway would then be 2 to 4 times equity, far above the goal's 100%.

**Evidence.**
- [Docs*] https://docs.alpaca.markets/us/changelog/2026-06-03-pdt-651df23
- [Docs*] https://docs.alpaca.markets/us/changelog/2026-07-06-pdt-db49dba
- [Docs*] https://docs.alpaca.markets/us/docs/the-intraday-margin-rule
- [Docs*] https://docs.alpaca.markets/us/docs/margin-and-short-selling
- https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/
- SDK: `alpaca/trading/models.py:492-493, 501-502, 519-521, 569-575` (the 2026-07-06 removal) and `:572`
  ("between 1-4").
- [Forum] https://forum.alpaca.markets/t/can-i-avoid-margin-by-trading-available-cash-only/14342
- GOAL.md:152, :471.

**Fix.**
1. Probe on day one: set the multiplier to 1 and place a small short. Record the caps observed.
2. Set `no_shorting=true` during long-only phases.
3. Read only `buying_power` and `regt_buying_power`.
4. Change configurations with a raw PATCH containing only the fields that change.

### A-13 · Minor · 24/5 trading is on by default

**Finding.** Trading API accounts have 24/5 trading on by default. Any limit order with
`extended_hours=true` (day or gtc) can then trade pre-market, after hours or overnight (20:00 to 04:00,
on Blue Ocean ATS). A day order sent after 16:00 without the flag queues for the next session. The goal
forbids orders outside 09:30 to 16:00, but doesn't say how queued exits fit the trapped rule.

**Evidence.**
- [Docs*] https://docs.alpaca.markets/us/docs/245-trading-for-trading-api ("enabled for 24/5 trading by
  default ... you can disable trading in the overnight session").
- [Docs*] https://docs.alpaca.markets/us/docs/245-trading
- SDK: `alpaca/trading/requests.py:364`, and `alpaca/trading/models.py:582-590` (no overnight setting).
- GOAL.md:89, :112, :182-184.

**Fix.**
1. Turn off the overnight session on the account. The setting's name is still to be confirmed; it isn't
   in SDK 0.44.0.
2. Have the risk manager reject any order with `extended_hours=true`, and any order sent outside
   09:30:00 to 15:59:59.
3. State that a trapped position's exit is sent at 09:30, not queued the night before.

### A-14 · Minor · The flatten deadline ignores early closes

**Finding.** C7 flattens an unacknowledged fault "after 60 minutes or at 15:45, whichever comes first"
(goal.toml:203). The overnight limits, by contrast, use 12:45 on early-close days (GOAL.md:203,
goal.toml:185). On a day that closes at 13:00, a fault at 12:30 would schedule the flatten for 13:30.
That is after the close, so the orders would queue for the next day.

**Evidence.**
- GOAL.md:472; goal.toml:185, :203.
- SDK: `alpaca/trading/client.py:438-461` (the calendar gives each day's close) and
  `alpaca/trading/enums.py:240` (closing-auction orders are rejected after 15:50).

**Fix.** Reword the deadline as "15 minutes before the close: 15:45, or 12:45 on early-close days",
taken from Alpaca's calendar.

### A-15 · Minor · KR2.6's data source differs between the two files

**Finding.** GOAL.md measures realized volatility on the equity of record. goal.toml says "account
equity from the broker", which on paper leaves out dividends and corporate actions.

**Evidence.** GOAL.md:333; goal.toml:488.

**Fix.** In goal.toml, use "the equity of record, computed every minute".

### A-16 · Minor · Order caps should be stated as a request budget

**Finding.** Alpaca allows 200 Trading API requests a minute per account, counting orders, cancels,
replaces and polls. A data plan doesn't raise it; 1,000 a minute is possible only as a non-retail
account, at $0.004 a share. C3's 120 orders a minute plus a 30% reserve leaves about 20 requests a minute
for everything else, while the plan needs a few orders a minute at most. KR5.2's "orders sent per fill"
doesn't say whether cancels and replaces count, and on Alpaca a replace is a new order.

**Evidence.**
- [Forum] staff threads 9743 and 14120 (as in A-5).
- https://alpaca.markets/support/increase-api-rate-limit
- goal.toml:193-195, :209.
- SDK: `alpaca/trading/models.py:223-224`.

**Fix.**
1. Restate C3: the trading process makes at most 60 requests a minute in normal running, and at most 100
   in any one minute. That leaves at least 100 for exits, reconciliation and the kill path.
2. Count submissions, replaces and cancels in "orders per fill".

### A-17 · Minor · Easy-to-borrow is a daily broker list, and hard-to-borrow shorts are now possible

**Finding.** KR5.3's "current easy-to-borrow status" maps to the asset's `easy_to_borrow` flag. Alpaca
says that status can change and should be checked daily. For easy-to-borrow names Alpaca arranges the
locate and charges no fee, which matches the goal.

Since about mid-2026, eligible accounts can also short hard-to-borrow names after a paid locate. The
goal excludes those, so the system must never request a locate. Alpaca doesn't close a short that turns
hard-to-borrow (an older staff post), and the short starts paying daily fees. The goal's 30-minute rule
covers that case.

**Evidence.**
- SDK: `alpaca/trading/models.py:48-49, 63-64`.
- [Docs*] https://docs.alpaca.markets/us/docs/margin-and-short-selling
- https://alpaca.markets/blog/htb-trading-api-locates/
- https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf
- [Forum] https://forum.alpaca.markets/t/shortable-stock-vs-easy-to-borrow/3824
- GOAL.md:80, :152, :349.

**Fix.**
1. Read the flag no more than 60 seconds before every short.
2. Check every held short before each open.
3. Put no locate calls in the code.

### A-18 · Minor · Alpaca's own outages count against KR4.1

**Finding.** KR4.1 counts minutes "running, connected and able to place orders". Half a percent of a
month's session is about 41 minutes. Alpaca's status page lists:
- a paper outage of about 8 minutes in July 2024;
- brief partial Trading API outages on 2026-05-22 and over 2026-05-29 and 30.

A third-party tracker counts 68 incidents since September 2025, about 66 hours in total across all of
Alpaca's components.

**Evidence.**
- [Status] https://status.alpaca.markets/incidents/fgk0tg9h0krk
- [Status] https://status.alpaca.markets/incidents/d5kj1t9g42qc
- [3rd party] https://pingoru.io/providers/alpaca/outage-history
- GOAL.md:343.

**Fix.** Report unavailability caused by the system and by the broker separately. KR4.1 judges the
first, and the trapped rule covers the second.

## Readiness paths

### (a) A paper bot that only tests the plumbing

**What it covers.** It connects, places small orders, keeps stops at the broker, reconciles, drills the
kill switch and raises alerts. It makes no claim of an edge.

**Blockers today.**
- Access: the network policy and the missing key (A-1).
- A host (A-2).
- Design decisions on the stop pattern (A-3), the kill path (A-5) and the broker adapter (A-6).
- A data plan (A-8). It's optional for plumbing alone, but recommended so nothing is built twice.

**Work packages, in order.**

| # | Work package | Who | Elapsed time |
|---|---|---|---|
| a0 | **Access.**<br>An Alpaca account with two-factor sign-in.<br>A paper key in a secret store.<br>The hosts allowed in this environment.<br>Algo Trader Plus.<br>A persistent host, plus a separate host for the watchdog.<br>Two alert channels. | owner; set-up help from the builder | 1 to 3 days |
| a1 | **Day-one probes on paper.**<br>Order ids: client id length and duplicate rejection; lookup after a forced timeout.<br>Rejections: wash-trade and held-quantity.<br>Entry and exit: IOC entry, then OCO exit, then replace-to-exit and the stop shrinking; bracket and OTO behavior on partial entries.<br>Fills: the buy-stop cap and the market-order collar.<br>Kill switch: close-all with orders open; `suspend_trade` against cancel and close.<br>Account: a multiplier of 1 with a short; turning off the overnight session; fields after the PDT removal.<br>Data: SIP on the paper key; error 406 after a killed data socket; the trade stream on a dropped connection.<br>Dividends: a held long over an ex-date. | builder | 1 to 2 weeks (ex-date and halt cases are opportunistic) |
| a2 | **Requirements and architecture for this slice.**<br>A per-symbol order state machine.<br>The entry and exit pattern (A-3).<br>The adapter (A-6).<br>The data gateway (A-8).<br>The ledger.<br>The kill paths and fencing (A-5).<br>Alerting and host layout.<br>The wording fixes in A-3 and A-13 to A-16, put to the owner. | builder and owner | about 1 week, overlapping a1 |
| a3 | **Build.**<br>The broker adapter and stream wrappers.<br>The order manager.<br>The reconciler (stream, 60-second poll, restart, close).<br>A subset of risk checks: gross, position size, open risk, daily loss, order caps, duplicate window.<br>The kill switch and the watchdog.<br>Alerts on two channels, with acknowledgement.<br>An append-only, hash-chained log with a copy off the host.<br>A clock monitor.<br>The owner's view of profit and loss (no more than 60 s old).<br>The daily report. | builder | 3 to 5 weeks |
| a4 | **Fault-injection tests.**<br>`kill -9` in the middle of an order.<br>A cut network and a dropped stream.<br>A storm of 429s.<br>A 504 on submit.<br>Clock drift.<br>Stale data.<br>A fake broker for continuous integration. | builder | 1 to 2 weeks, overlapping a3 |
| a5 | **Paper burn-in.**<br>Tiny orders in a fixed list of liquid names, long and short (easy-to-borrow only), with stops at the broker.<br>Daily reconciliation.<br>Drills: the kill switch on both paths, a stop acting while the system is down, a restart, alert repetition and the safe state. | system and owner | at least 20 trading days (4 to 5 weeks) |

**Duration.**
- **Realistic:** about 8 to 12 weeks from access to a drilled plumbing bot.
- **Best case:** about 6 weeks, if every probe confirms the design.
- **Worst case:** up to about 16 weeks, if a probe overturns the stop pattern or the kill path's
  fencing.
- **First script:** one that connects, places an order, sets a stop and reconciles is possible within
  a few days of access.

**Reasoning.** There isn't much code. Market hours set the calendar. The probes, the drills and the
goal's own cadences (a drill every 20 trading days, uptime judged monthly) all need trading days. Some
behaviors (ex-dates, halts, gaps) can only be tested when they happen. Defects hide in the order state
machine and the recovery paths, so fault injection gets real time.

**What it proves.** That the plumbing works on Alpaca's paper simulator. It doesn't prove live stop
behavior (A-9), and it proves nothing about an edge.

### (b) A paper bot trading a strategy under G2

**Blockers.**
- Everything in path (a).
- A strategy that passed G1.
- The data Alpaca doesn't provide (A-7).
- SIP (A-8).
- The wording fixes, above all A-3, because G2's criteria are fixed in advance.
- The review panel and its planted-flaw test (KR6.5) before G1.
- The gate reviews (KR6.2).

**Work packages, in order.**

| # | Work package | Elapsed time |
|---|---|---|
| b1 | **Research data.**<br>Alpaca SIP bars and quotes from 2016-01-04, about 2,700 trading days.<br>An outside point-in-time security master, with delisted names and delisting returns.<br>Corporate actions and historical event dates.<br>A borrow proxy, industry history and the VIX.<br>Storage and validation. | 1 to 3 months, starting with a0 |
| b2 | **Research platform.**<br>A walk-forward simulator that obeys every limit, event blackout and short-sale rule.<br>Conservative fills and the cost model.<br>A trial log that is append-only, hashed and timestamped outside the author's control.<br>The DSR gate, the lag audit and rotation accounting. | 1 to 2 months, overlapping b1 |
| b3 | **Review panel.**<br>Set-up, and the planted-flaw test (KR6.5). | 2 to 4 weeks |
| b4 | **Research stages.**<br>Up to four stages of 3 months each, with at most 5 variants per stage, registered first. | 3 to 12 months |
| b5 | **The G2 system, built on path (a).**<br>Evaluation of the whole universe every minute (KR3.3).<br>The equity of record, with conservative revaluation and corrections.<br>C4's checks, using outside data, and all the risk limits.<br>Rotation and its logs.<br>Reason records (KR7.1).<br>The frozen-strategy rerun for KR1.5 and KR1.6. | 2 to 4 months after (a), in parallel with b4 |
| b6 | **Freeze.**<br>Freeze the strategy, hold the G1 review, and get the owner's decision. | 2 to 4 weeks |
| b7 | **G2 itself.**<br>At least 120 trading days and 300 round trips, within 150 days.<br>Then the G2 review. | 6 to 7 months |

**Duration.**
- **Starting G2:** at the earliest about 6 months from access. The data and the platform take about 2.5
  to 3 months, the first 3-month stage has to pass, and a review follows. Realistically, 8 to 15 months.
- **Finishing G2:** 6 to 7 months after it starts. That's about a year from now at the earliest, and
  realistically 14 to 22 months.
- **Odds.** The goal's numbers give a 22% chance of reaching real money with a real edge. G2 passes a
  real edge about 75 to 80% of the time, and G1's false-pass rate is at most 1%. Together these put the
  chance that any strategy reaches G2 at about 3 in 10.

**Reasoning.** G1's stages are fixed at 3 months each, and they must follow the data, the platform and
the panel test. The production system can be built while research runs, so it rarely sets the pace. If
no strategy passes, path (b) never happens, and the plumbing from (a) is the only lasting result. That
is one reason to start (a) now, alongside b1.

## Sources

**Alpaca documentation.** These were read through web-search extracts; the hosts were blocked from this
environment.
- https://docs.alpaca.markets/us/docs/orders-at-alpaca
- https://docs.alpaca.markets/us/docs/working-with-orders
- https://docs.alpaca.markets/reference/deleteallopenpositions-1
- https://docs.alpaca.markets/us/docs/paper-trading
- https://docs.alpaca.markets/us/docs/websocket-streaming
- https://docs.alpaca.markets/us/docs/account-activities.md
- https://docs.alpaca.markets/us/docs/streaming-market-data
- https://docs.alpaca.markets/us/docs/real-time-stock-pricing-data
- https://docs.alpaca.markets/us/docs/about-market-data-api
- https://docs.alpaca.markets/us/docs/market-data-faq
- https://docs.alpaca.markets/us/docs/245-trading-for-trading-api
- https://docs.alpaca.markets/us/docs/245-trading
- https://docs.alpaca.markets/us/docs/the-intraday-margin-rule
- https://docs.alpaca.markets/us/docs/margin-and-short-selling
- https://docs.alpaca.markets/us/changelog/2026-06-03-pdt-651df23
- https://docs.alpaca.markets/us/changelog/2026-07-06-pdt-db49dba
- https://docs.alpaca.markets/docs/using-oauth2-and-trading-api

**Alpaca site, blog and support.**
- https://alpaca.markets/data
- https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/
- https://alpaca.markets/blog/htb-trading-api-locates/
- https://alpaca.markets/blog/introducing-corporate-actions-api-announcements/
- https://alpaca.markets/support/increase-api-rate-limit
- https://alpaca.markets/support/why-do-i-see-a-discrepancy-between-the-notional-value-requested-and-the-order-value-ultimately-filled
- https://alpaca.markets/support/difference-paper-live-trading
- https://alpaca.markets/learn/api-key-security-best-practices-for-alpaca-builders
- https://alpaca.markets/learn/trading-stocks-postman/
- https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf

**Archived Alpaca docs.** These may be stale.
- https://raw.githubusercontent.com/alpacahq/alpaca-docs/master/content/trading/orders.md
- https://raw.githubusercontent.com/alpacahq/alpaca-docs/master/content/trading/paper-trading.md
- https://raw.githubusercontent.com/alpacahq/alpaca-docs/master/content/api-references/trading-api/streaming.md

**Forum.** Thread numbers are as cited above, each at `https://forum.alpaca.markets/t/<slug>/<number>`:
1252, 3824, 4055, 5542, 5940, 6022, 6024, 8493, 9647, 9743, 10896, 11395, 11405, 11641, 13689, 13817,
14120, 14303, 14342, 14412, 17712, 18200, 18223, 18227, 19208, 19325, 19417.

**Status and third parties.**
- https://status.alpaca.markets/incidents/fgk0tg9h0krk
- https://status.alpaca.markets/incidents/d5kj1t9g42qc
- https://pingoru.io/providers/alpaca/outage-history
- https://github.com/dd-jp/samurai-trading-system/issues/1938
- https://help.heygotrade.com/en/articles/5985234-what-are-the-different-order-types
- https://wealth-lab.com/Discussion/Use-Alpaca-SIP-live-data-with-Paper-account-13072
- https://app.certfuel.com/series6/learn/processing-transactions/transaction-processing-and-settlement/adjustment-of-open-orders-rule-5330

**SDK.**
- alpaca-py 0.44.0 (https://pypi.org/project/alpaca-py/0.44.0/), read as text. The source used for this
  review is at
  `/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/alpaca/src/alpaca/`.

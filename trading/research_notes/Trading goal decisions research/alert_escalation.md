# Alert escalation for an unattended, single-owner trading system: what to do when alerts go unacknowledged, and how fast

*Research conditions (2026-10-15). WebFetch failed for every host with a DNS error, including Wikipedia. The shell's egress proxy blocks the regulator, broker and vendor sites (403). So no primary web page could be opened in full. The evidence comes from four places: (a) web-search extracts of the cited pages, meaning the search tool's quotes and summaries of them; (b) Alpaca's own SDKs, downloaded from the package registries: alpaca-py 0.44.0 (PyPI, uploaded 2026-08-11) and @alpacahq/alpaca-trade-api 5.0.0 (npm, published 2026-10-01, with types generated from Alpaca's OpenAPI spec); (c) the CCXT library 4.5.88 (PyPI, 2026-10-14); and (d) the goal spec in this repository. The shared web-search budget (200 calls per turn, across all agents) ran out after this researcher's 8th search. Some facts therefore could not be verified: the on-call vendor defaults, the Google SRE figures, the exchange kill-switch specifics, some Knight Capital details and the exact paragraph of the RTS 6 five-second rule. They appear under "Gaps" as background knowledge, not as findings. "Search extract" marks a fact read from a search result rather than from the full page.*

## 1. EU RTS 6 (Delegated Regulation (EU) 2017/589) and ESMA: what they require of staffing, reachability and response

### Takeaway
RTS 6 treats real-time monitoring as work done by staff:
- **Article 16 (real-time monitoring)** requires real-time alerts. Staff must "respond ... in a timely manner" and "initiate remedial action". The firm needs a process to act "as soon as possible after an alert ... including, where necessary, an orderly withdrawal from the market".
- **Article 12 (kill functionality)** requires the ability to "immediately" cancel any or all unexecuted orders.

The regulatory kill function cancels orders. It does not require closing positions. One point could not be settled this session: whether the five-second alert limit is in RTS 6 Article 16 or only in RTS 7 (2017/584, for trading venues).

### Cited Findings
- Article 16 of 2017/589 is titled "Real-time monitoring", and Article 12 is "Kill functionality". The coordinator's "15/16" for real-time monitoring should read **16**. — [Better Regulation, Art 16](https://service.betterregulation.com/document/370444); [legislation.gov.uk, Art 12](https://legislation.gov.uk/eur/2017/589/article/12/2020-12-31?view=plain) (search extracts)
- Art 16 says: "An investment firm shall have a process in place to take remedial action as soon as possible after an alert has been generated, including, where necessary, an orderly withdrawal from the market." — [legislation.gov.uk 2017/589](https://www.legislation.gov.uk/eur/2017/589/body); [EUR-Lex PDF](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32017R0589&from=IT); [Better Regulation, Art 16](https://service.betterregulation.com/document/370444) (search extracts)
- Art 16 says: "staff members in charge of the real-time monitoring shall respond to operational and regulatory issues in a timely manner and shall initiate remedial action where necessary." — same sources as above (search extracts)
- **Five-second alerts: the sources conflict.**
  - For RTS 6: a search extract of the legislation.gov.uk copy of 2017/589 contains the words "five seconds after the relevant event".
  - Against: the same search attributed the five-second rule to Delegated Regulation 2017/584 (RTS 7, trading venues). Its recital says alerts should be generated within no more than five seconds, and its operative text says real-time alerts "shall be generated within five seconds of the relevant event". The search also said that RTS 6's recital asks only that alerts be generated "as instantaneously as technically possible", and it suggested the UK copy's sentence might come from 2017/584. That suggestion is speculation by the search tool, not a cited fact.
  - Sources: [legislation.gov.uk 2017/589](https://www.legislation.gov.uk/eur/2017/589/body); [EUR-Lex 2017/584](https://eur-lex.europa.eu/eli/reg_del/2017/584/oj/eng). **Unresolved.**
- Art 12 (kill functionality) has three parts, cross-checked in two copies:
  - a firm must be able, as an emergency measure, to immediately cancel any or all of its unexecuted orders at any or all venues it is connected to;
  - unexecuted orders include those from individual traders, trading desks or, where applicable, clients;
  - the firm must be able to identify which algorithm and which trader, desk or client is responsible for each order.
  - Sources: [legislation.gov.uk, Art 12](https://legislation.gov.uk/eur/2017/589/article/12/2020-12-31?view=plain); [Better Regulation](https://service.betterregulation.com/document/273576) (search extracts)
- ESMA's Q&A on MiFID II/MiFIR market structures (Q&A 3.16, 7 July 2017; an older fact) gives two points:
  - the rule obliges a firm to have "the ability as an emergency measure to immediately pull any or all outstanding orders from any or all trading venues";
  - "effective kill functionality is essential for adequate risk management and safeguarding the orderly functioning of the market".
  - Sources: [ESMA Q&A, copy hosted by MFA](http://www.mfaalts.org/wp-content/uploads/2017/09/ESMA-QA-on-MiFID-II-and-MiFIR-Market-Structures-Topics.pdf); [ESMA Q&A page](https://www.esma.europa.eu/publications-data/questions-answers/1612) (search extracts)
- ESMA published a Supervisory Briefing on Algorithmic Trading in the EU on 26 February 2026. It is current and cross-checked in five sources:
  - it is a non-binding "convergence tool" for national competent authorities;
  - it focuses on pre-trade controls, governance, testing frameworks and outsourcing;
  - it draws on ESMA's 2022 Common Supervisory Action on pre-trade controls, and it adds considerations on AI.
  - Sources: [ESMA](https://esma.europa.eu/press-news/esma-news/esma-issues-supervisory-briefing-algorithmic-trading); [Central Bank of Ireland](https://www.centralbank.ie/regulation/markets-update/article/issue-4-2026/central-bank-of-ireland/esma-supervisory-briefing-on-algorithmic-trading-in-the-eu); [Regulation Tomorrow](https://www.regulationtomorrow.com/2026/02/esma-supervisory-briefing-on-algorithmic-trading/); [Hogan Lovells](https://www.hlc.com/en/publications/esma-publishes-supervisory-briefing-on-algorithmic-trading-under-mifid-ii-what-firms-need-to-know); [Markets Media](https://www.marketsmedia.com/esma-issues-supervisory-briefing-on-algo-trading/)
- The briefing PDF is at [ESMA74-1505669079-10311](https://www.esma.europa.eu/sites/default/files/2026-02/ESMA74-1505669079-10311_Supervisory_Briefing_on_Algorithmic_Trading_in_the_EU.pdf). It was not opened.
- RTS 6 is the regulation on "organisational requirements of investment firms engaged in algorithmic trading", which sets its scope. — [legislation.gov.uk 2017/589](https://www.legislation.gov.uk/eur/2017/589/body)
- The goal currently says C7 "relaxes RTS 6 Article 16 (alerts within 5 seconds, a person monitoring) because the owner wants an unattended system". — [GOAL.md, C7](/home/user/AIresume/trading/goal/GOAL.md) (line 409)

### Inferences
- RTS 6 does not bind this owner, who is not an EU investment firm. It is a benchmark. Its model is people watching automated alerts, then remedial action "as soon as possible". An unattended system can meet the intent only by automating the first remedial action. What matters is the time from alert to action, not the time from alert to acknowledgement. Fifteen minutes to stop new entries is far from "as soon as possible".
- The regulatory kill function cancels unexecuted orders. This supports making "stop entries and cancel working entry orders" the immediate automatic step. Flattening is then a separate, conditional "orderly withdrawal".
- "Orderly withdrawal" argues against liquidating with market orders at a moment set by a timer, such as in the middle of a sell-off or at the open.
- The goal's C7 says RTS 6 Article 16 requires five-second alerts. That claim should be checked against EUR-Lex before it stays in the goal. If the five seconds is only in RTS 7, the stated deviation narrows to "no person monitoring".

### Gaps
- The full text of Article 16 paragraphs (2) and (5) was not retrieved, nor any wording such as monitoring "during the hours" orders are sent. Background knowledge, not verified this session: Art 16(2) requires monitoring by the trader in charge of the algorithm and by a risk-control function.
- Article 15 is "pre-trade controls on order entry" and Article 4 covers staffing. Both are background knowledge, not retrieved.
- The briefing's specific expectations on the kill function and real-time monitoring are not confirmed.
- Whether the EU has amended RTS 6 since 2017 was not checked. ESMA's MiFID II review proposed changes. The legislation.gov.uk copy is the UK's onshored version.

## 2. SEC Rule 15c3-5, FINRA Regulatory Notice 15-09 and FIA practice on monitoring, kill switches and staff who can intervene

### Takeaway
The US rules place real-time controls on the broker-dealer that has market access, here Alpaca, not on its API customer:
- Rule 15c3-5 requires pre-trade controls, and that surveillance staff receive "immediate post-trade execution reports".
- FINRA 15-09 (2015) is guidance on supervising algorithms.
- FINRA's 2024 oversight report asks whether firms use kill switches to respond to aberrant algorithm behaviour.

FIA papers treat cancel-on-disconnect (CoD) and kill switches as standard safeguards. In them, both cancel orders. CoD is optional, because whether it helps depends on the firm's business.

### Cited Findings
- Rule 15c3-5(c)(2)(iv) says: "Assure that appropriate surveillance personnel receive immediate post-trade execution reports that result from market access." — [govinfo, 75 FR 69826](https://www.govinfo.gov/link/fr/75/69826); [rule text, Nasdaq copy](https://nasdaqtrader.com/content/productsservices/trading/ften/SECRule_15c3_5.pdf); [SEC small entity compliance guide](https://www.sec.gov/files/rules/final/2010/34-63241-secg.htm) (search extracts)
- The rule's controls are duties of broker-dealers with market access. Adopted 3 November 2010; compliance date 14 July 2011 (older facts). — [SEC adopting release 34-63241](https://www.sec.gov/rules/final/2010/34-63241.pdf); [Mondaq](https://webiis06.mondaq.com/unitedstates/financial-services/115938/sec-adopts-new-rule-concerning-risk-management-controls-for-broker-dealers-with-market-access) (search extracts)
- In its adopting release, the SEC said the rule's "regulatory requirements" include "post-trade obligations to monitor for manipulation and other illegal activity". — [Cboe BYX disciplinary decision, 2012](https://cdn.cboe.com/resources/regulation/disciplinary/2012/20120347345-USRI-2820-BYX_Redacted.pdf). Single source: the adopting release was not opened.
- FINRA Regulatory Notice 15-09 (March 2015; an older fact) gives guidance on effective supervision and control practices for firms engaging in algorithmic strategies. It is organised in five areas: General Risk Assessment and Response; Software/Code Development and Implementation; Software Testing and System Validation; Trading Systems; and Compliance. — [National Law Review](https://natlawreview.com/article/finra-issues-guidance-effective-supervision-firms-engaging-algorithmic-trading-strat); [FINRA notice PDF](https://www.finra.org/sites/default/files/notice_doc_file_ref/Notice_Regulatory_15-09.pdf) (search extracts)
- FINRA's 2024 Annual Regulatory Oversight Report asks firms whether they use controls "such as kill switches to monitor and respond to aberrant behavior by trading algorithms or other impactful market-wide events". — [FINRA 2024 report, Market Access Rule](https://www.finra.org/rules-guidance/guidance/reports/2024-finra-annual-regulatory-oversight-report/market-access-rule). Single source.
- FINRA expects supervision to cover every stage of developing an algorithmic strategy, not only the strategy once it is in production. — [Guidehouse](https://guidehouse.com/insights/financial-crimes/2023/manipulative-trading). Single secondary source.
- The CFTC's 2013 Concept Release grouped "kill switches" under "system safeguards" for automated trading (an older fact). — [Federal Register, 2013 concept release](https://www.federalregister.gov/documents/2013/09/12/2013-22185/concept-release-on-risk-controls-and-system-safeguards-for-automated-trading-environments); [CFTC Reg AT NPRM PDF, 2015](https://www.cftc.gov/sites/default/files/idc/groups/public/@newsroom/documents/file/federalregister112415.pdf)
- FIA published "Best Practices for Automated Trading Risk Controls and System Safeguards" in July 2024. Its contents list covers pre-trade controls, including cancel-on-disconnect and kill switches. — [FIA PDF](https://www.fia.org/sites/default/files/2024-07/FIA_WP_AUTOMATED%20TRADING%20RISK%20CONTROLS_FINAL_0.pdf). Single source; only the contents list was seen.
- FIA's March 2015 guide (an older fact) says two things:
  - "COD is a service provided by exchanges that monitors for a loss of connectivity between a participant's trading session and the exchange's trading platform. If a loss of connection is detected, COD initiates a best-effort attempt to cancel all resting orders for the disconnected session."
  - Kill switches need a registration and entitlement process that names the staff authorised to use them.
  - Source: [FIA Guide to the Development and Operation of Automated Trading Systems (copy hosted by Matba Rofex)](https://matbarofex.com.ar/documentos/mpi/fia-guide). Single source.
- FIA Europe's MiFID II recommendations for exchange-traded derivatives e-trading (2019) say:
  - CoD should be optional rather than mandatory alongside "Cancel All", because it depends on the firm's business and risk procedures;
  - kill switches should have formal conformance testing, a clear statement of whether they do more than cancel open orders, a process to re-enable trading, and availability per firm and per session.
  - Source: [FIA Europe PDF](https://www.fia.org/sites/default/files/2019-05/FIA-Europe-MiFID-II-Minimum-Standard-Recs-for-ETD-eTrading-Algo-Conformance-Statement-on-Materiality-Included-0.pdf). Single source.
- FIA's executing-broker guidance says "when an executing broker trading platform disconnects from the exchange for any reason, the client may lose control of their working orders". Brokers that use CoD should have procedures for it (items 7-5 and 7-6). — [FIA documentation](https://www.fiadocumentation.org/fia/operational-and-technology-guidance_1/best-practices-guide-to-executing-brokers_2). Single source.

### Inferences
- Alpaca, as the broker-dealer, applies its own 15c3-5 pre-trade controls to the owner's orders. That is an outer cap on a runaway, independent of the owner's code. It supports the goal's choice in C6 to rely on broker-side caps, such as the lowest margin multiplier.
- In industry practice, a kill switch or CoD cancels working orders and blocks new ones. Liquidation is a separate, usually human, decision. In this system, resting stop orders are what protects the positions. A response that "cancels everything" removes that protection. So "cancel" must exclude protective stops, or be followed at once by flattening.
- The regulatory model assumes people see executions in real time ("immediate post-trade execution reports"). An unattended system has to put automated surveillance in their place: continuous reconciliation, anomaly checks and a broker-side check of stop coverage.
- FIA's call for a documented process to re-enable trading supports latching: after an unacknowledged alert, the system does not resume entries by itself.

### Gaps
- The exact text of FINRA 15-09 on kill switches, real-time monitoring and staff availability was not retrieved.
- No recommended timings (heartbeat intervals, timeouts) from the FIA 2024 paper were retrieved.
- The SEC staff FAQ on 15c3-5 was not checked.

## 3. Knight Capital (SEC Release No. 34-70694, 2013): timing lessons for alerts and escalation

### Takeaway
Knight had machine-generated warnings for about 89 minutes before the open: 97 emails, starting at 8:01 a.m. ET. They were not designed as alerts and nobody acted on them. After the 9:30 open, the malfunction lost about $461 million in about 45 minutes, roughly $10 million a minute on average. The lessons:
- a warning that changes nothing until someone reads it is useless;
- a malfunction must be contained by automatic controls within seconds;
- any human acknowledgement timer measured in minutes protects nothing against a runaway.

### Cited Findings
- On 1 August 2012, Knight's system generated 97 automated emails before the 9:30 open, beginning at about 8:01 a.m. ET. Each referred to SMARS and an error described as "Power Peg disabled". — [Docsumo newsletter](https://newsletter.docsumo.com/p/97-emails-nobody-read); [Socialvik](https://www.socialvik.com/blog/how-trading-bots-work-components); [DEV Community](https://dev.to/axrisi/knight-capital-how-a-reused-feature-flag-lost-460-million-133j); [Sound of Development](https://soundofdevelopment.substack.com/p/the-knight-capital-disaster-how-a). These are secondary sources citing the [SEC order](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf), which was not opened.
- The messages "were not designed to be system alerts", and Knight staff "generally did not review them" when they arrived. — [Docsumo](https://newsletter.docsumo.com/p/97-emails-nobody-read); [Socialvik](https://www.socialvik.com/blog/how-trading-bots-work-components). Both quote the SEC order.
- Secondary sources disagree on where the emails went: "a generic inbox" in one, "a shared mailbox" in another, and simply "not recognized as the alarm they were" in a third. — [Sound of Development](https://soundofdevelopment.substack.com/p/the-knight-capital-disaster-how-a); [zof.ai](https://zof.ai/pointoffailure/knight-capital-45-minutes)
- The cause: the new RLP code repurposed a flag that had once activated the retired "Power Peg" code. That code was still present and callable on the eighth server, which missed the deployment. — [SEC order](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf) (search extract); [DEV Community](https://dev.to/axrisi/knight-capital-how-a-reused-feature-flag-lost-460-million-133j)
- In about 45 minutes there were about 4 million executions in 154 stocks, for more than 397 million shares. — [SEC order](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf) (search extract); [zof.ai](https://zof.ai/pointoffailure/knight-capital-45-minutes)
- The trading loss was about $461.1 million. — [Knight Form 425 exhibit, SEC EDGAR](https://www.sec.gov/Archives/edgar/data/0001060749/000119312512513608/d457296dex21.htm). It is "$460 million" in [DEV Community](https://dev.to/axrisi/knight-capital-how-a-reused-feature-flag-lost-460-million-133j) and [Wikipedia](https://en.wikipedia.org/wiki/Knight_Capital_Group).

### Inferences
- **Lead time.** The warnings began about 89 minutes before the open (8:01 to 9:30). A pre-open gate that refuses to start trading while any error alert is unacknowledged would have prevented the whole loss. The goal's pre-open version check (C8) is the right kind of control. Extending it to "no open while a critical alert is unacknowledged" is cheap.
- **Speed.** $461.1 million over about 45 minutes is about $10 million a minute on average. At that rate, a 15-minute acknowledgement window allows about $150 million, and a 60-minute window is longer than the whole event. Timers keyed to acknowledgement cannot be what contains a malfunction. Only automatic controls that act in seconds can.
- **Design.** Knight's messages existed but were not alerts. The point of an escalation rule is to make an unacknowledged alert matter. For faults where the system itself may be wrong, the consequence has to be automatic and immediate, not delayed by 15 minutes.
- **Scale.** This system's loss rate is capped by its own pre-trade limits and the broker's margin settings, if those work. Knight shows that a deployment fault can bypass controls inside the trading system. That is why the broker-side caps (C6) and a broker-side check of the positions matter.

### Gaps
The following is background knowledge of the SEC order, not re-verified this session; check it against the order before use:
- Knight's response was to uninstall the new code from the seven correctly deployed servers, which made things worse.
- Net long of about $3.5 billion in 80 stocks and net short of about $3.15 billion in 74 stocks.
- A $12 million penalty.
- No written incident-response procedures.
- Its monitoring tool (PMON) did not generate automated alerts.
- No automated control compared orders with capital thresholds.

## 4. On-call practice: acknowledgement timeouts, escalation steps and a realistic response time for one person

### Takeaway
On-call defaults could not be checked this session: the search budget was spent and the vendors' sites were unreachable. From background knowledge (not verified), 15 minutes sits between Google SRE's 5-minute response for critical services and the common 30-minute escalation default. Either way, one owner who is not on a formal rota cannot be relied on to acknowledge within any fixed time during the 6.5-hour session, every day. So acknowledgement should decide when trading resumes. It should not be what protects the capital.

### Cited Findings
- The current goal defines these alerts and responses:
  - **C7 alerts:** the owner is alerted within 60 seconds of a blocked or rejected order, a data gap over 30 seconds, a lost connection, a reconciliation mismatch, or a limit reaching 0.8 of its threshold. Unacknowledged for 15 minutes, new entries stop; at 60 minutes, every position is closed.
  - **KR4.4:** within 60 seconds of a lost connection, data older than 30 seconds or a failed limit check, the system is already in the safe state: no new orders, open entry orders cancelled, every position keeping a stop that works without the system, and the owner alerted.
  - **C5:** a mismatch or an order of unknown state blocks orders that increase risk.
  - **C11:** an order the system did not send triggers the kill switch.
  - **C2:** an order that reduces risk "is never blocked by a price, universe or event check, and is limited only to the exchange's price band".
  - **Decision 8:** no orders outside 09:30–16:00.
  - Source: [GOAL.md](/home/user/AIresume/trading/goal/GOAL.md) (lines 178, 290, 407–413, 458)

### Inferences
- **Overlap in the current spec.** KR4.4 and C5 already stop entries automatically, within 60 seconds, for most of the alert types C7 lists. So the 15-minute step in effect only governs two kinds: a single rejected order, and a limit at 0.8. The spec should say explicitly that the escalation timers come on top of the automatic containment.
- **Response times for one person.** Without data, the reasoning is this. One person's time to acknowledge has a long tail: meetings, driving, flights, illness, and sleep if the owner is in Asia-Pacific during US hours. Any fixed acknowledgement time will sometimes be missed. If missing it forces a liquidation, unnecessary liquidations will happen.
- **Alert fatigue.** Frequent forced liquidations would push the owner to loosen alerts, which defeats the purpose.
- **Escalation for one person.** The practical equivalent of an escalation policy is several channels in a row: push notification, then SMS, then a phone call, then a repeated call. A backup person who is allowed only to press the kill switch is optional. These are standard features of paging tools, but their defaults were not verified here.

### Gaps
None of the following was verified this session (search budget spent, sites unreachable). It is background knowledge only:
- **Google SRE book, "Being On-Call":** typical response times are 5 minutes for user-facing or otherwise highly time-critical services and 30 minutes for less time-sensitive systems; at most two incidents per 12-hour shift.
- **PagerDuty:** the default escalation timeout in the UI is 30 minutes; the default service acknowledgement timeout is 30 minutes; the default auto-resolve is 4 hours.
- **Opsgenie:** end of sale on 4 June 2025 and end of support on 5 April 2027, with migration to Jira Service Management or Compass. If true, Opsgenie is a poor choice for a new system in October 2026.
- **Splunk On-Call (VictorOps):** no defaults were found.
- No data was found on how fast solo operators or retail algorithmic traders actually acknowledge alerts.

## 5. Automated fail-safes when nobody responds: cancel-on-disconnect, dead-man's switches, and what Alpaca offers

### Takeaway
Exchanges and crypto venues offer cancellation of orders on disconnect, or on a timer that the client must keep resetting (a dead-man's switch). Alpaca's current API, as described in its SDKs of August and October 2026, shows no such feature. Open orders at Alpaca, including GTC stop orders and the stop legs of bracket orders, stay in place if the client dies. Alpaca does offer:
- one call to cancel all orders;
- one call to close all positions, optionally cancelling orders first;
- one call to close a single position;
- an account switch that blocks new orders.

Stop orders cannot execute outside the regular session, because only limit orders can trade in extended hours.

### Cited Findings
- **Exchanges.** CoD is an exchange service that, on loss of connection, makes "a best-effort attempt to cancel all resting orders for the disconnected session". — [FIA guide, 2015](https://matbarofex.com.ar/documentos/mpi/fia-guide). Single source; an older fact.
- **Crypto venues.** CCXT 4.5.88 implements these timers; each is single-sourced to CCXT, and the venues' own pages were not opened:
  - **Kraken spot:** "dead man's switch, cancel all orders after the given timeout"; timeout in milliseconds; 0 cancels the timer; CCXT rejects values above 86,400,000 ms (24 hours). CCXT links [Kraken's docs](https://docs.kraken.com/api-reference/trading/cancel-all-orders-after-x).
  - **Kraken Futures:** the same. CCXT links [Kraken Futures' docs](https://docs.kraken.com/api/docs/futures-api/trading/cancel-all-orders-after).
  - **Bybit:** "disconnect cancel protection". CCXT links [Bybit's docs](https://bybit-exchange.github.io/docs/v5/order/dcp).
  - **OKX:** "cancel all after". CCXT links [OKX's docs](https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-cancel-all-after).
  - **Binance futures and options:** `countdownCancelAll`.
  - **Deribit:** `enable_cancel_on_disconnect`, `disable_cancel_on_disconnect` and `get_cancel_on_disconnect`.
  - Source: [CCXT 4.5.88 on PyPI](https://pypi.org/project/ccxt/4.5.88/) (files `ccxt/kraken.py`, `krakenfutures.py`, `bybit.py`, `okx.py`, `abstract/binance.py`, `abstract/deribit.py`).
- **Alpaca facts below come from two Alpaca-published SDKs.** They agree with each other but are not independent of Alpaca, which publishes both. Sources: [alpaca-py 0.44.0](https://pypi.org/project/alpaca-py/0.44.0/) and [@alpacahq/alpaca-trade-api 5.0.0](https://www.npmjs.com/package/@alpacahq/alpaca-trade-api/v/5.0.0).
- **Cancel all orders.** `DELETE /v2/orders` "Attempts to cancel all open orders. A response will be provided for each order that is attempted to be cancelled. If an order is no longer cancelable, the server will respond with status 500 and reject the request." In alpaca-py, `cancel_orders()` "Cancels all orders".
- **Close all positions.** `DELETE /v2/positions` "Closes (liquidates) all of the account's open long and short positions". In alpaca-py: "Liquidates all positions for an account. Places an order for each open position to liquidate." With `cancel_orders=true`, it will "cancel all open orders before liquidating all positions".
- **Close one position.** `DELETE /v2/positions/{symbol}` "Closes (liquidates) the account's open position for the given symbol. Works for both long and short positions." (JS SDK only)
- **Account switches.** The setting `suspend_trade` means "If true, new orders are blocked" (JS) and "If true Account becomes unable to submit new orders" (alpaca-py). Other settings: `no_shorting` ("Account becomes long-only mode") and `max_margin_multiplier` ("A number between 1-4"). The account object also shows `trading_blocked`, `account_blocked` and `trade_suspended_by_user`.
- **Order types for equities.** Order classes are simple, oco, oto and bracket. Order types are market, limit, stop, stop_limit and trailing_stop. A bracket order is "entry plus take-profit and stop-loss legs ... Both legs are required". A stop loss without a limit price "will execute as a market order".
- **Time in force:**
  - a `day` order "is only valid during Regular Trading Hours (9:30am - 4:00pm ET). If unfilled after the closing auction, it is automatically canceled. If submitted after the close, it is queued and submitted the following trading day."
  - `gtc` lasts until cancelled, and "Non-marketable GTC limit orders are subject to price adjustments to offset corporate actions".
  - `cls` (market or limit on close) orders "submitted after 3:50pm but before 7:00pm ET will be rejected".
  - `opg` orders submitted after 9:28am are rejected.
- **Extended hours.** `extended_hours` "(default) false. If true, order will be eligible for execution in the pre-market, after-hours, and overnight sessions. Only works with type `limit` and time_in_force set to either `day` or `gtc`." Single Alpaca source (the JS SDK's OpenAPI description). alpaca-py's docstring is consistent but less specific.
- **Order states.** "replaced" covers an order "updated due to a market event such as corporate action". "canceled" can be "by the exchanges due to its time-in-force". A "held" state exists. "An order may be canceled through the API up until the point it reaches a state of either filled, canceled, or expired."
- **No dead-man's switch at Alpaca.** Neither Alpaca SDK contains a cancel-on-disconnect, heartbeat-timeout or "cancel all after" endpoint (searched terms: disconnect, heartbeat, dead man, cancel_after). This is evidence of absence from the current API surface, not a statement by Alpaca.

### Inferences
- **An independent watchdog is needed.** Alpaca has no dead-man's switch, so an unattended set-up needs its own: a watchdog on another host with its own API key. It reads the broker's positions and orders. If the trading process is silent or cut off, it runs the coverage check and the close-all call described in section 7. The goal's "second way" in C6 is currently "the broker's own controls", which at Alpaca means the owner acting by hand. That does not work when nobody responds.
- **No CoD helps this design.** Stops survive the client's death. A CoD that cancelled resting stop orders would leave positions naked exactly when the system is blind. This fits FIA's view that CoD should be optional.
- **Never cancel all orders on its own.** For a book protected by resting stops, `DELETE /v2/orders` alone is dangerous because it cancels the stops too. Use it only as part of liquidation: `DELETE /v2/positions?cancel_orders=true`. That call cancels first and then liquidates, which also avoids a double exit, where a stop fills and the liquidation order fills as well. Calls can partly fail, because orders that are no longer cancellable return 500. So the system must re-read the broker's positions and repeat.
- **`suspend_trade` as a fence.** It gives a "no new orders" switch at the broker that does not depend on the trading process. By its wording it blocks all new orders, exits included. Use it to fence off a suspect system once stops are verified, and expect to unset it before flattening (unverified; see Gaps).
- **Overnight gaps.** Stop orders cannot execute outside 09:30–16:00, and the goal also forbids extended-hours orders (decision 8). An overnight gap therefore passes through the stops. They trigger at or after the next open, as market orders unless they carry a limit.
- **Timing flaw in the current rule.** A flatten order sent after 16:00 is queued for the next trading day. Under a 60-minute timer, any alert raised after about 15:00 ET has its liquidation fall after the close. The result is liquidation at the next open, the worst time for spreads, instead of either closing before the close or holding with stops.

### Gaps
- **Exchange controls.** CME's iLink CoD and the kill switches of CME, Nasdaq and NYSE were not retrieved. Background, unverified: they cancel orders and block new ones; they do not liquidate.
- **BitMEX.** `cancelAllAfter` was not verified; BitMEX is not in this CCXT build.
- **Alpaca details, unverified:**
  - which order type close-all uses (background: market orders);
  - whether `suspend_trade` blocks close-all, and whether existing stops keep working while it is set;
  - whether Alpaca holds stop orders internally or rests them at a venue;
  - how a partly filled bracket parent resizes its legs, and whether cancelling the parent cancels the legs;
  - whether GTC orders expire (background: 90 days);
  - Alpaca's handling of orders during trading halts and corporate actions, beyond the status text quoted above.

## 6. Is closing everything after 60 minutes safer than holding with stops?

### Takeaway
Neither is safer in every case.
- **Flattening** is the only state that is safe against faults nobody has detected. But a fixed 60-minute timer liquidates at arbitrary moments: in a sell-off, near the close, or, for alerts after about 15:00 ET, at the next day's open. It also adds cost for alerts that are market events.
- **Holding with stops** is acceptable when two things are true: the broker's own records confirm that every share is covered by a working stop of the right side and quantity, and the alert does not suggest the system is malfunctioning.

Stops do not protect against overnight gaps (they cannot execute outside regular hours) or against trading halts.

### Cited Findings
- **Alpaca mechanics:**
  - a stop loss without a limit executes as a market order;
  - only limit orders can trade outside regular hours;
  - day orders submitted after the close are queued for the next day;
  - close-all with `cancel_orders` cancels and then liquidates, and orders that cannot be cancelled return 500.
  - Sources: [alpaca-py 0.44.0](https://pypi.org/project/alpaca-py/0.44.0/); [@alpacahq/alpaca-trade-api 5.0.0](https://www.npmjs.com/package/@alpacahq/alpaca-trade-api/v/5.0.0)
- **RTS 6:** remedial action "as soon as possible ... including, where necessary, an orderly withdrawal from the market". — [legislation.gov.uk 2017/589](https://www.legislation.gov.uk/eur/2017/589/body); [Better Regulation, Art 16](https://service.betterregulation.com/document/370444)
- **Knight:** about $461 million lost in about 45 minutes while a malfunctioning system kept trading. — [Knight Form 425](https://www.sec.gov/Archives/edgar/data/0001060749/000119312512513608/d457296dex21.htm); [SEC order](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf)
- **The goal's existing limits:**
  - a daily loss of 2% means flat, and no entries until the next session;
  - a 9% drawdown halts and goes flat;
  - the worst day is 2.5%, including gaps within the jump assumptions;
  - overnight positions are sized for jumps;
  - there are no orders outside 09:30–16:00;
  - the plan assumes costs of 8 bps a round trip;
  - orders that reduce risk are never blocked by price, universe or event checks (C2);
  - every share must be covered by a stop that works while the system is down (KR2.5).
  - Source: [GOAL.md](/home/user/AIresume/trading/goal/GOAL.md) (lines 170–179, 279, 438–450)

### Inferences
- **When the system is healthy (market-type alerts).** The positions were opened within the risk limits and sized for gaps. Holding them with their stops is the planned risk. A forced liquidation turns a warning into a stricter, unplanned limit. It pays spread and impact on the whole gross exposure, against an edge planned around 8 bps of cost. And it may sell into a disorderly market, the opposite of "orderly withdrawal". The hard limits (2% daily, 9% drawdown) already flatten automatically when breached.
- **When the system may be wrong (integrity alerts).** The system's own view of positions and orders is suspect. Any flatten must use the broker's close-all, which works from the broker's position records, not from the system's own order logic. Orders built from a corrupted internal state could add to positions or reverse them, the "fix makes it worse" pattern. If the broker's records show any share without a working stop, that exposure has no cap. It should be closed within a minute or two, not after 60 minutes.
- **Risk while held in the safe state.** In the safe state the system sends no orders, so the risk per minute while holding verified stops is market risk inside the stops. That is the same as a healthy hold. So the intraday timer matters less than the overnight boundary. The real question is whether to carry an unacknowledged fault into the next session, and the answer should be no. Close before the close, or at the latest after the next open settles.
- **Overnight risk.** The goal forbids orders outside regular hours, so an owner who is awake overnight could not trade either. For a healthy system, unmonitored overnight risk equals monitored overnight risk. What matters is the system's health at the next open. That calls for a latch: no automatic resumption of entries.
- **Long absences.** If the owner is away for days, the two cases differ:
  - after a market-type alert, a "wind-down" mode (no entries; normal exits and stops continue, as C2 already allows) runs the book down within its holding period of about 5 days, with no forced liquidation;
  - after an integrity alert, the book is closed the same day.
- **The case for keeping the fixed 60-minute rule.** It is simple, deterministic and easy to test and drill. It does not depend on classifying alerts correctly or on a correct coverage checker, and either of those could be buggy. Faults nobody has detected are covered only by being flat. And the owner wants a rule they can understand.
- **The case against it.** It is too slow when coverage is unverified. It is unnecessary and costly for market events. It can fire mid-crash or after the close. And it says nothing about the case where the close itself cannot execute, such as a lost connection or a halted stock.

### Gaps
- No data on how often overnight gaps exceed the stop distance in this universe.
- No measurement of the slippage of Alpaca's close-all.
- The SEC and FINRA investor guidance on stop orders in gaps was not retrieved.
- The cost of a liquidation at the opening auction against one at 15:45 was not quantified.

## 7. Overall: is 15 minutes then 60 minutes right, and what should replace it?

### Takeaway
Partly.
- **15 minutes is a reasonable time to stop entries after a warning nobody acknowledges.** It is far too slow for a malfunction, where entries must stop automatically within seconds. The goal's KR4.4 and C5 already do this for most fault types.
- **A blanket "close everything at 60 minutes" is too slow when stops cannot be confirmed at the broker, and unnecessary when they can.** It is also harmful whenever it lands after the close.

**Recommendation:** tier the response by alert type; act without waiting for acknowledgement; verify stops from the broker's own records; close conditionally, with a 15:45 ET cutoff; and latch until the owner acknowledges.

**Confidence:**
- **High** on the direction: immediate automatic containment, conditional liquidation through the broker, and no liquidation outside regular hours.
- **Medium** on keeping 60 minutes as the intraday limit for verified holds.
- **Low to medium** on the other exact numbers.

### Cited Findings
- **Act at once:**
  - RTS 6 asks for remedial action "as soon as possible" after an alert (Art 16) and a kill function that cancels orders "immediately" (Art 12). — [legislation.gov.uk 2017/589](https://www.legislation.gov.uk/eur/2017/589/body); [legislation.gov.uk, Art 12](https://legislation.gov.uk/eur/2017/589/article/12/2020-12-31?view=plain)
  - Knight's warnings came about 89 minutes before the open, and the loss then accrued at about $10 million a minute. — [SEC order](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf) via [Docsumo](https://newsletter.docsumo.com/p/97-emails-nobody-read); [Knight Form 425](https://www.sec.gov/Archives/edgar/data/0001060749/000119312512513608/d457296dex21.htm)
- **Industry practice:** a kill switch or CoD cancels orders, CoD is optional, and there is a documented process to re-enable trading. — [FIA guide, 2015](https://matbarofex.com.ar/documentos/mpi/fia-guide); [FIA Europe, 2019](https://www.fia.org/sites/default/files/2019-05/FIA-Europe-MiFID-II-Minimum-Standard-Recs-for-ETD-eTrading-Algo-Conformance-Statement-on-Materiality-Included-0.pdf)
- **Alpaca:**
  - stops persist without the client, since there is no CoD or dead-man's switch;
  - stops cannot trade outside regular hours;
  - day orders sent after the close are queued for the next day;
  - there are broker-side calls to close all positions (cancelling orders first), close one position, and block new orders.
  - Sources: [alpaca-py 0.44.0](https://pypi.org/project/alpaca-py/0.44.0/); [@alpacahq/alpaca-trade-api 5.0.0](https://www.npmjs.com/package/@alpacahq/alpaca-trade-api/v/5.0.0)
- **The goal already has:** the safe state within 60 seconds for lost connection, stale data or a failed limit check (KR4.4); risk-increasing orders blocked on a mismatch (C5); the kill switch for foreign orders (C11); risk-reducing orders never blocked by price, universe or event checks (C2). — [GOAL.md](/home/user/AIresume/trading/goal/GOAL.md)

### Inferences

**Proposed rule.** The numbers are judgment calls, marked "(J)".

| Alert class | Examples | At once, with no acknowledgement needed | If unacknowledged | Next session |
|---|---|---|---|---|
| **Foreign activity** | an order or fill the system did not send (C11) | kill switch: the broker's close-all with `cancel_orders=true`, then re-read and repeat until flat | — | locked until the owner acknowledges and keys are rotated |
| **Integrity**: the system may be wrong | a reconciliation mismatch, an order of unknown state, data older than 30 s, a lost connection, a restart mid-session, a failed pre-open check, a burst of rejected orders (J: 3 or more in 5 minutes) | (1) safe state within 60 s (target 5 s): entries blocked, entry orders cancelled, protective stops and bracket legs left alone. (2) Within 60 s, check from the broker's own positions and open orders that every share has a working stop of the right side and quantity. (3) Close any uncovered position at once with the broker's per-symbol close. (4) Page the owner. | Close everything with the broker's close-all (`cancel_orders=true`) at the earlier of 60 minutes and **15:45 ET** (J). Call by phone after 5 minutes, and repeat every 10 minutes (J). | If the alert came after 15:45, or the close could not run, hold overnight with broker-verified stops. If still unacknowledged, close everything after the open settles (J: 09:45 ET). No entries until the owner acknowledges and reconciliation is clean. |
| **Warning or market event** | a limit at 0.8 of its threshold, a single rejected order, a halt or volatility alert | nothing beyond the existing limits and stops | **after 15 minutes, stop new entries** (keep the owner's number); exits and stops continue (C2), so the book winds down; no forced liquidation (the 2% daily and 9% drawdown limits still flatten automatically) | entries stay stopped until the owner acknowledges |

**Order of steps for any alert:**
1. Stop entries.
2. Cancel working entry orders, never protective stops.
3. Verify stop coverage from the broker's records, and close anything uncovered.
4. Escalate the paging: push, then SMS, then phone.
5. Hold with verified stops, or wind down.
6. Withdraw only through the broker's close-all, never through the system's own order logic, and never by "cancel all" alone.
7. Latch until the owner acknowledges.

**Supporting controls:**
- An independent watchdog (another host, its own key) that runs steps 3 and 6 when the trading process is dead or cut off. Alpaca offers no dead-man's switch.
- A pre-open gate: no trading while a critical alert is unacknowledged (the Knight lesson).
- A drill of the "no acknowledgement" path alongside the existing kill-switch drill every 20 trading days (FIA: conformance testing of kill switches).
- Optional, at the owner's choice: one automatic resumption per session for data or connection faults that clear within 5 minutes (J) with a clean broker reconciliation.

**Evidence for the proposal:**
- Regulators and the industry expect remedial action at once and treat kill functions as order cancellation.
- Knight shows that minutes-scale human timers cannot contain a malfunction.
- Alpaca's stops persist without the client but cannot trade outside regular hours, and orders sent after the close queue for the next open. Together these make the 15:45 cutoff, not the 60-minute delay, the decision that matters.
- Forced liquidation after market-type alerts adds cost and may sell into disorder.

**Evidence against, and residual risk:**
- More branches mean more ways to fail. A wrong classification, or a buggy coverage checker, could leave a dangerous fault in "hold". Mitigations: send any unclassified alert to the integrity class, and test the coverage checker against broker data in drills.
- Stops give poor protection in gaps and halts.
- The owner's preference for a simple rule is legitimate.

If the owner wants to keep a single timer, the smallest fix is to add three things to 15/60:
1. stop entries at once for integrity alerts;
2. close at once anything not covered by a stop the broker confirms;
3. a 15:45 ET cutoff, with no close orders outside the session.

**Confidence by part:**
- **High:** stopping entries immediately and automatically for integrity faults (RTS 6 wording, Knight's timing, FIA practice, and consistency with KR4.4 and C5).
- **Medium-high:** replacing the unconditional 60-minute close with a conditional close plus a pre-close cutoff (Alpaca's mechanics and the cost logic).
- **Medium:** keeping 60 minutes as the intraday limit for verified holds. No evidence favours another number.
- **Low to medium:** the 5- and 10-minute paging intervals, the 15:45 and 09:45 times, and the threshold for a burst of rejected orders. These are judgment calls, informed by on-call norms that could not be verified this session.

### Gaps
- **RTS 6's five-second rule.** Confirm whether it is in Art 16 of 2017/589 or only in RTS 7 (2017/584). The goal's C7 deviation statement depends on it.
- **On-call defaults.** PagerDuty, Opsgenie (including its end-of-support dates), Splunk On-Call and the Google SRE response times are all unverified this session.
- **Knight.** The remediation that made things worse, the net positions and the penalty are unverified this session.
- **Alpaca behaviour to confirm on paper before go-live:**
  - the order type close-all uses, and how it behaves after hours;
  - whether `suspend_trade` interacts with close-all and with existing stops;
  - how bracket legs behave on a partial fill and on cancellation;
  - the expiry of GTC stops, and their handling through corporate actions and halts.
  - All of these can be tested on Alpaca's paper account.

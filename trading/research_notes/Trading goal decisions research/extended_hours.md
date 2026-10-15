# Extended-hours risk-reducing orders for an autonomous US-equity system on Alpaca (status as of 2026-10-15)

Method and evidence-quality note. The facts below were gathered on 2026-10-15 through web-search result summaries only. WebFetch failed with DNS errors for every host. The session proxy also refused CONNECT (HTTP 403) to alpaca.markets, docs.alpaca.markets, sec.gov, finra.org, wilmerhale.com, skadden.com and marketsmedia.com. So the full pages were never read; quoted phrases are as the search tool reported them. The session's web-search budget ran out (a limit of 200 per turn, shared by all agents) before every item could be cross-checked. Labels: **[2+]** means confirmed by two or more independent sources. **[Alpaca-only]** means stated only on Alpaca's own pages: primary for Alpaca's rules, but not independently confirmed. **[single-source]** means found in one source only. **[conflict]** means the sources disagree.

## 1. Alpaca's current rules for pre-market, after-hours and overnight (24/5) trading

### Takeaway
Alpaca now offers US-equity trading from 20:00 ET Sunday to 20:00 ET Friday, in paper as well as live. The sessions are:
- pre-market, 04:00–09:30
- regular, 09:30–16:00
- after-hours, 16:00–20:00
- overnight, 20:00–04:00, executed on Blue Ocean ATS (BOATS).

Outside the regular session Alpaca accepts only limit orders, with time-in-force `day` or `gtc` and `extended_hours=true`. Stop and bracket protection does not work outside the regular session. Overnight market data is limited to indicative quotes and trades delayed 15 minutes. 24/5 reached the Broker API in May 2025, and the Trading API and paper accounts in about January–February 2026. Alpaca says it is preparing for exchange-based overnight trading from 6 December 2026.

### Cited Findings
- **Pre-market and after-hours windows.** Alpaca offers stock trading from 04:00 to 20:00 ET, covering pre-market 04:00–09:30 and after-hours 16:00–20:00. Sources: [Alpaca blog: Alpaca Introduces Stock Trading from 4 am to 8 pm ET](https://alpaca.markets/blog/alpaca-introduces-stock-trading-from-4-am-to-8-pm-et/), [Alpaca Learn: How to Enable Stock Market Trading from 4 am to 8 pm ET](https://alpaca.markets/learn/how-to-enable-stock-market-trading-from-4-am-to-8-pm-et), [Alpaca forum: Full extended hours!](https://forum.alpaca.markets/t/full-extended-hours/8484). **[Alpaca-only]** This is an older feature. The search tool described these blog posts as one to five years old; the exact launch date was not captured.
- **Overnight and 24/5 windows.**
  - Alpaca's overnight session runs 20:00–04:00 ET. 24/5 means 20:00 ET Sunday to 20:00 ET Friday. Sources: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading), [Alpaca on X, 2026-01-28](https://x.com/AlpacaHQ/status/2016526691892670801).
  - BOATS lists its own session as Sunday–Thursday 20:00–04:00 ET, only on days when the NYSE TRF is open: [Blue Ocean FAQ](https://blueocean-tech.io/faq/).
  - **[2+]** for the window.
- **Overnight venue.**
  - Alpaca's docs say overnight executions and market data go through Blue Ocean ATS (BOATS). Alpaca routes overnight orders there; API users cannot choose an overnight venue such as Blue Ocean or Nasdaq. Source: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading).
  - Alpaca's data guide uses `feed=boats` for overnight history: [Alpaca Learn: Fetch historical data](https://alpaca.markets/learn/fetch-historical-data).
  - **[Alpaca-only]** for Alpaca's routing. That BOATS dominates the overnight session is confirmed independently; see section 3.
- **Exchange routing from December.**
  - The 24/5 docs page was updated about three days before 2026-10-15, according to the search tool. It mentions that exchange-based overnight trading may go live.
  - Alpaca says it is "building toward industry go-live on December 6, 2026". Source: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading). **[Alpaca-only]**
- **Launch dates.**
  - Broker API 24/5 launched in May 2025: [Crowdfund Insider, May 2025](https://www.crowdfundinsider.com/2025/05/239982-alpaca-introduces-24-5-trading-for-broker-api-enabling-global-access-to-us-markets/). Alpaca lists 24/5 among its 2025 launches: [Alpaca's 2025 in Review](https://alpaca.markets/blog/alpacas-2025-in-review/). **[2+]**
  - Trading API 24/5 launched in early 2026. Sources:
    - [Alpaca blog: Alpaca Launches 24/5 Trading for Stocks for Trading API](https://alpaca.markets/blog/introducing-stocks-24_5-overnight-with-alpaca-trading-api/)
    - [Crowdfund Insider, URL dated 2026/02](https://www.crowdfundinsider.com/2026/02/259268-alpaca-introduces-24-5-trades-for-trading-api-providing-almost-round-the-clock-access/)

    One search summary put the launch around January 2026; the search tool described the blog and learn guide as about eight to nine months old. **[2+ that it happened; exact day not captured]**
- **Paper trading.**
  - "24/5 paper trading is now available via Alpaca's Trading API and dashboard … from 8:00 PM ET Sunday to 8:00 PM ET Friday." Source: [Alpaca on X, 2026-01-28](https://x.com/AlpacaHQ/status/2016526691892670801). The date was decoded from the post ID; the post was repeated on 2026-02-25: [Alpaca on X](https://x.com/AlpacaHQ/status/2026674931379921181).
  - A search summary of Alpaca's pages adds "up to 2x overnight buying power … for eligible accounts".
  - **[Alpaca-only]**
- **Live availability caveat.** An Alpaca community thread reported live orders not taking effect overnight. Staff replied that "live accounts are always up-to-date with the current features". Source: [Alpaca forum: Live 24/5 trading](https://forum.alpaca.markets/t/live-24-5-trading/18393). **[single-source]**
- **Order types outside the regular session.**
  - `extended_hours=true` works only with `type=limit` and `time_in_force` `day` or `gtc`. Market orders are not accepted outside regular hours. Source: [Alpaca API reference: Create an Order](https://docs.alpaca.markets/us/reference/postorder).
  - "Market orders and other unsupported order types are not eligible for extended-hours trading and will be rejected": [Alpaca docs: SpaceX trading FAQ](https://docs.alpaca.markets/us/docs/spacex-trading-availability-and-faqs).
  - Two third-party write-ups describe the same limit-only rule: [AlgoMax blog](https://algomax.ai/blog/alpaca-extended-hours-trading-bots), [GitHub alpaca-news ALPACA-TRADING.md](https://github.com/davidsvaughn/alpaca-news/blob/trader/docs/ALPACA-TRADING.md).
  - **[2+]**
- **Overnight order rules.**
  - Only limit orders, with TIF `day` and `gtc`. "Orders placed during the overnight session will remain active through the regular and after-hours sessions of the upcoming trading day. If unfilled, the order is canceled at 8:00 PM ET." Sources: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading), [Alpaca Learn: How to Trade 24/5](https://alpaca.markets/learn/how-to-trade-us-stocks-24_5-overnight-with-python-and-alpaca). **[Alpaca-only]**
  - BOATS itself "accepts only Limit Day orders … does not accept IOC orders": [Blue Ocean FAQ](https://blueocean-tech.io/faq/), [BOATS Trading Rules, 2021](https://irp.cdn-website.com/815393a4/files/uploaded/BOATS%20Trading%20Rules%20DTG%20210520.pdf). **[conflict]** Alpaca's overnight `gtc` is not explained by BOATS' rules; it is presumably an Alpaca-side construct.
- **Stops and brackets.**
  - Extended hours are not supported for bracket orders, so bracket stop-loss legs give no protection outside 09:30–16:00. Source: [Alpaca docs: Placing Orders](https://docs.alpaca.markets/us/docs/orders-at-alpaca).
  - Stop orders cannot carry `extended_hours`; they are accepted but trigger only in the regular session. Sources: [GitHub alpaca-news ALPACA-TRADING.md](https://github.com/davidsvaughn/alpaca-news/blob/trader/docs/ALPACA-TRADING.md), [AlgoMax blog](https://algomax.ai/blog/alpaca-extended-hours-trading-bots). **[secondary only; not found in Alpaca's docs]**
- **Shorting.**
  - "All symbols supported during regular market hours are also supported during extended hours. Short selling is also treated the same." Source: [Alpaca docs: Placing Orders](https://docs.alpaca.markets/us/docs/orders-at-alpaca).
  - Overnight eligibility is the asset attribute `overnight_tradable`. Separate fields show `overnight_halted`, `shortable` and `easy_to_borrow`. Source: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading).
  - **[Alpaca-only]**
- **Overnight buying power.**
  - Day-trading buying power does not apply overnight; 2x is the maximum margin buying power for overnight trades.
  - Orders that rely on day-trading buying power "may be rejected at 8 PM ET".
  - The short-sale buying-power check uses the greater of the limit price or 3% above the current ask, times quantity.
  - Source: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading). **[Alpaca-only]**
- **Fractional shares.** Fractional limit orders are supported in extended hours: [Alpaca blog: Fractional shares support limit orders and extended hours](https://alpaca.markets/blog/fractional-shares-trading-supports-limit-orders-and-extended-hours/). **[Alpaca-only]**
- **Overnight market data.**
  - `feed=overnight` gives latest bars, latest quotes ("real-time indicative"), latest trades (15-minute delayed) and snapshots.
  - `feed=boats` gives 15-minute-delayed historical BOATS bars, quotes and trades.
  - Sources: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading), [Alpaca Learn: Fetch historical data](https://alpaca.markets/learn/fetch-historical-data).
  - Real-time data comes with the Algo Trader Plus subscription: [Alpaca blog: 24/5 for Trading API](https://alpaca.markets/blog/introducing-stocks-24_5-overnight-with-alpaca-trading-api/).
  - **[Alpaca-only]**
- **Fees.** Alpaca markets API stock and ETF trading as commission-free: [Alpaca: Algorithmic Trading API, Commission-Free](https://alpaca.markets/algotrading), [Alpaca blog: 4 am to 8 pm ET](https://alpaca.markets/blog/alpaca-introduces-stock-trading-from-4-am-to-8-pm-et/). No overnight-specific fee was found. **[Alpaca-only]**
- **Alpaca's risk disclosures.**
  - Alpaca says trading outside regular hours "poses risks such as lower liquidity, wider bid-ask spreads, higher volatility, and potential discontinuities in price". It also says thinner overnight books can cause partial fills.
  - Sources: [Alpaca blog: 24/5 for Trading API](https://alpaca.markets/blog/introducing-stocks-24_5-overnight-with-alpaca-trading-api/), [Alpaca Learn: How to Trade 24/5](https://alpaca.markets/learn/how-to-trade-us-stocks-24_5-overnight-with-python-and-alpaca).
- **FINRA Rule 2265 disclosures.**
  - Broker-dealers give an extended-hours risk disclosure under FINRA Rule 2265. Firms' versions list:
    - lower liquidity: "your order may only be partially executed, or not at all"
    - higher volatility
    - changing prices that may not reflect the prior close or the next open
    - unlinked markets
  - Sources: [Citi FINRA Rule 2265 disclosure](https://www.citigroup.com/rcs/icgPublic/storage/public/disclosures/FINRA-Rule-2265.pdf), [Instinet](https://www.instinet.com/extended-hours-trading-risk-disclosure-statement), [Hilltop Securities](https://www.hilltopsecurities.com/disclosures/extended-hours-disclosure/), [Morgan Stanley](https://www.morganstanley.com/disclosures/extended-hours-trading-risk-disclosure). **[2+]**

### Inferences
- At Alpaca, nothing automatic protects an overnight position between 16:00 and 09:30. Any protection outside the regular session must come from the system placing its own limit orders.
- The system must enforce "reduce-only" itself. Short selling is "treated the same" in extended hours, so a sell larger than the long position could open a short. Whether Alpaca would reject such an order depends on shortability; this was not verified.
- An overnight `day` order stays live through the next regular and after-hours sessions until 20:00. Any extended-hours order therefore needs explicit cancel and hand-over logic, or it may collide with regular-session logic. Using `gtc` with `extended_hours` would keep orders alive across days, so a risk-reducing path should use `day` only.
- The overnight data limits (indicative quotes, trades delayed 15 minutes, one venue) make the 20:00–04:00 session a poor place for automated, quote-collared exits.
- Paper accounts support all sessions, so the trigger and collar logic can be tested in paper before going live.

### Gaps
- The Alpaca pages could not be read in full (blocked). The rules above come from search summaries of those pages.
- The exact Trading API 24/5 launch day was not captured.
- That stop orders trigger only in the regular session is confirmed only by third-party sources.
- Not verified:
  - regulatory fees (SEC Section 31, FINRA TAF, CAT) on extended-hours sells
  - whether extended-hours `day` orders placed in the pre-market join the opening auction
  - whether Alpaca applies its own price collar or "limit too far from market" rejections in extended hours
  - how realistic paper fills are in thin books
  - the full text of Alpaca's 24/5 risk disclosure
  - how Alpaca will route overnight orders, and how it will define "day", after the 6 December 2026 exchange launch

## 2. Market quality outside the regular session: spreads, depth, price impact, volatility, price discovery

### Takeaway
Every source agrees that trading outside 09:30–16:00 is thinner and costlier:
- **Barclay & Hendershott 2004:** after-hours spreads about 3–4 times regular-hours spreads (a later summary says 4–5 times).
- **Eaton, Shkilko & Werner, via a Nasdaq summary:** overnight retail effective spreads about 3 times regular hours, and price impact about 6 times.
- **IOSCO 2026:** off-hours trading worldwide is retail-driven, with lower liquidity and wider spreads.

Off-hours price discovery is nonetheless real. Individual after-hours trades are informative, and after earnings news prices reprice through quotes almost instantly, while actual trades are sparse.

### Cited Findings
- **Barclay & Hendershott (2003), "Price Discovery and Trading After Hours", RFS 16(4).**
  - Trading outside regular hours is sparse, concentrated in the most liquid stocks and clustered on select days.
  - Individual after-hours trades are more informative than daytime trades, but prices are less efficient after hours.
  - Sources: [Hendershott working-paper PDF](https://faculty.haas.berkeley.edu/hender/after_hours_price_discovery.pdf), [ResearchGate](https://www.researchgate.net/publication/238193552_Price_Discovery_and_Trading_Costs_After_Hours), summarised in [Eaton–Shkilko–Werner, Nocturnal Trading (AFA listing)](https://afajof.org/management/viewp.php?n=162176). **[2+ via secondary summaries; late-1990s Nasdaq data, old]**
  - Secondary summaries also report the highest information asymmetry (PIN) of the day in the pre-open, and over 90% of pre-open trades on ECNs. **[secondary; old]**
- **Barclay & Hendershott (2004), "Liquidity Externalities and Adverse Selection: Evidence from Trading after Hours", JF.**
  - After-hours quoted and effective spreads are "three to four times larger than during the trading day": [Wiley JF abstract page](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2004.00646.x), via search summary.
  - A later summary puts Hendershott and Barclay's extended-hours costs at "roughly 4 to 5 times regular hours": [Nasdaq: Looking at all-day data](https://www.nasdaq.com/articles/looking-all-day-data-24-hour-trading).
  - **[conflict on magnitude: 3–4x versus 4–5x]**
- **Jiang, Likitapiwat & McInish (2012), JFQA 47(6) 1303–1330.**
  - Sample: S&P 500 stocks, 2004–2008. After-hours trading is heightened on earnings-announcement days.
  - "A significant portion of the price change and price discovery occurs immediately after the earnings releases" in after-hours trading, and after-hours prices show "a large degree of informational efficiency".
  - Sources: [Cambridge JFQA abstract](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/information-content-of-earnings-announcements-evidence-from-afterhours-trading/39171BF13B8D5EE4890B930F2FF4E19C), [Univ. of Memphis Digital Commons](https://digitalcommons.memphis.edu/facpubs/11594/), [ResearchGate](https://www.researchgate.net/publication/228429973_Information_Content_of_Earnings_Announcements_Evidence_from_After_Hours_Trading). **[2+]**
- **Grégoire & Martineau (2022), JAR 60(1) 261–297.**
  - Sample: S&P 1500, 2011–2015; after-hours defined as 16:00–09:30.
  - After-hours price discovery after earnings works "mainly through quotes rather than trades". After good news the ask adjusts quickly and the bid lags, and the reverse after bad news. Returns computed from trades understate the speed and size of the reaction.
  - The median number of after-hours trades following an announcement is only 16.
  - Sources: [Wiley JAR](https://onlinelibrary.wiley.com/doi/full/10.1111/1475-679X.12394), [SSRN 3060094](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3060094). **[one study, two listings; also cited as the closest prior work by Christensen et al.]**
- **Christensen, Timmermann & Veliyev, "Warp Speed Price Moves: Jumps after Earnings Announcements" (later in JFE, per Aarhus University).**
  - Prices almost always jump immediately after earnings announcements, most of which are released after hours. The announcing firm's price jumps in more than 90% of after-hours sessions with an announcement.
  - For the largest stocks prices move "within literally milliseconds".
  - Returns from post-announcement trading are consistent with efficient price formation after 2016.
  - Sources: [arXiv 2601.08962](https://arxiv.org/html/2601.08962v1), [UC San Diego news](https://today.ucsd.edu/story/earnings-news-cause-immediate-stock-price-jumps-sometimes-moving-whole-market), [Aarhus University news](https://law.au.dk/en/current/allnews/news/artikel/reagerer-med-lynets-hast-regnskabsmeddelelsers-afsmitning-paa-markedet). **[2+]**
- **Eaton, Shkilko & Werner, "Nocturnal Trading" (SSRN 5181159, version of 19 Dec 2025; AEA 2026).**
  - Trading between 20:00 and 04:00 has grown rapidly, is mostly retail, and is concentrated in a small subset of securities.
  - One platform dominates the session, with liquidity from only two market makers.
  - Effective spreads are wider than in regular hours, but realized spreads are about the same or better; "trading costs remain relatively low".
  - Nocturnal trading makes an economically significant contribution to price discovery, especially for non-US firms and macro ETFs. One version puts the nocturnal weighted price contribution for ETFs at more than 17% of 24-hour price discovery.
  - Average net profitability is close to zero after costs, unless positions are held longer.
  - Sources: [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5181159), [AFA listing](https://afajof.org/management/viewp.php?n=162176), [AEA 2026 program](https://www.aeaweb.org/conference/2026/program/paper/kRz7yE6Q). **[one study, several listings]**
- **Nasdaq's summary of that research.** Overnight retail effective spreads are about 3 times regular hours and price impact about 6 times. Extended-hours trading is about 11% of total daily volume. Source: [Nasdaq: Looking at all-day data](https://www.nasdaq.com/articles/looking-all-day-data-24-hour-trading). **[single-source, secondary]** It reads as more negative than the paper's "relatively low" costs; the two framings were not reconciled.
- **SIFMA roundtable debrief (Feb 2026).** Overnight realized spreads for liquidity providers turn negative within 10 seconds, a sign of adverse selection: [SIFMA debrief](https://www.sifma.org/wp-content/uploads/2026/02/SIFMA-Roundtable-Building-the-Roadmap-to-24.7-Trading-Debrief.pdf). **[single-source; the summary's reading of who is adversely selected was unclear]**
- **IOSCO, Report on Extended Trading Hours (OR/06/26, published 21 May 2026).**
  - Off-hours trading is mostly retail-driven, with limited institutional participation.
  - It shows "lower liquidity, wider bid-ask spreads, and adjusted execution conditions" compared with regular hours.
  - Sources: [IOSCO PDF](https://www.iosco.org/library/pubdocs/pdf/IOSCOPD820.pdf), [A&O Shearman summary](https://finreg.aoshearman.com/iosco-reports-on-market-liquidity-and-extended-trading-hours-for-equity-markets), [Mondo Visione](https://mondovisione.com/media-and-resources/news/iosco-publishes-reports-on-the-evolution-of-market-liquidity-during-the-trading-2026521/). **[2+]**
  - One search summary also said that a US venue reported post-close and pre-open spreads much wider than regular hours in Q3 2025, and that a Brazilian venue reported a 45.8% volatility gap: [IOSCO PDF](https://www.iosco.org/library/pubdocs/pdf/IOSCOPD820.pdf). **[single-source; could not be re-confirmed; no US figures captured]**
- **WFE.** The February 2026 paper is mostly about post-trade infrastructure: [WFE, Extending Exchange Trading Hours](https://wfe-live.lon1.cdn.digitaloceanspaces.com/org_focus/storage/media/WFE%20-%20Extending%20Exchange%20Trading%20Hours%20wCover.pdf). The September 2025 paper notes that retail investors may face "slightly wider spreads" overnight: [WFE, 24/7 paper](https://wfe-live.lon1.cdn.digitaloceanspaces.com/org_focus/storage/media/Cally%20Billimore/WFE%20-%2024.7%20Final%20September%202025.pdf).
- **Perreten (working paper, Feb 2026 version).**
  - Sample: one-minute data for S&P 500 stocks, 2008–2023.
  - The close-to-open return is split into after-market, pre-market and "dark" components.
  - Dark returns tend to be positive and pre-market returns negative. This reversal is strongest when pre-market liquidity is thin.
  - Cross-sectional explanatory power for the close-to-open return rises smoothly through the pre-market.
  - Source: [MFC conference listing](https://mfc3.eventsadmin.com/Papers/ViewContribution?cid=14387&h=34E9F3229E21B084DE4A06E94CD0FC5F). **[single-source; working paper]**

### Inferences
- The system's universe has regular-session spreads of 10 bps or less. Applying the 3–4x (Barclay & Hendershott) and about 3x (overnight) multipliers suggests typical extended-hours spreads of roughly 30–60 bps for these names, and much wider just after news. This is an extrapolation, not a measurement for this universe.
- Depth outside the regular session is thin: few trades (a median of 16 after earnings) and few liquidity providers (two overnight). Order size must be small relative to displayed size, and partial fills should be expected.
- Quotes lead trades after hours. A collar or trigger keyed to the last trade, or to the last regular-session close, will be stale; it must key to the live quote.

### Gaps
- No 2024–2026 measurement was found of pre-market and after-hours spreads, depth or volatility by time of day (for example 04:00–07:00 versus 08:00–09:30) for liquid US large caps. This would be needed to calibrate the gate.
- The volatility ratio between extended and regular hours was not captured. Nasdaq's "Just how volatile are US stocks overnight" exists, but its content was not retrieved.
- The IOSCO US-venue figures were not captured.

## 3. The 2025–2026 move to 23/5 exchange trading and the SIP: status on 2026-10-15

### Takeaway
As of 15 October 2026 no US exchange runs an overnight session. Nasdaq, NYSE Arca, Cboe EDGX and 24X all target the SIP's 23x5 go-live on 6 December 2026:
- **Nasdaq:** SEC approval on 10 April 2026.
- **NYSE Arca:** rule amended from 22 to 23 hours in May 2026.
- **Cboe EDGX:** target December 2026.
- **24X:** trading 04:00–20:00 since 14 October 2025.

The common pattern is an overnight session from 21:00 to 04:00 ET after a 20:00–21:00 pause. Two protections are due to start the same day:
- **LULD Overnight Price Bands:** initially static ±20%, with no automatic pauses.
- **Clearly-erroneous trade rules:** adapted for the overnight session.

Until then, overnight trading happens only on ATSs, where BOATS has about 80–95% of volume. Launch dates have slipped before.

### Cited Findings
- **Nasdaq.**
  - The SEC approved Nasdaq's 23/5 proposal on 10 April 2026: [Simpson Thacher memo](https://www.stblaw.com/about-us/publications/view/2026/04/29/looking-ahead-to-extended-trading-sec-approves-nasdaq-s-23-5-trading-proposal), [TheCorporateCounsel.net](https://www.thecorporatecounsel.net/blog/2026/04/extended-trading-sec-okays-nasdaqs-23-5-trading-proposal.html), [Markets Media](https://www.marketsmedia.com/nasdaq-aims-to-debut-23-5-trading-on-6-december-2026/). **[2+]**
  - The target launch is 6 December 2026: [Markets Media](https://www.marketsmedia.com/nasdaq-aims-to-debut-23-5-trading-on-6-december-2026/), [Massive](https://massive.com/blog/us-equities-move-to-23-5-trading), [WilmerHale, 29 Sep 2026](https://www.wilmerhale.com/en/insights/client-alerts/20260929-23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch), [Jones Day, Sep 2026](https://www.jonesday.com/en/insights/2026/09/nyse-and-nasdaq-move-to-23hour-trading-day-overnight-session-is-an-evolution-but-not-yet-a-revolution). **[2+]**
  - Older guidance of "early Q3 2026" is out of date: [Alston & Bird, May 2026](https://www.alston.com/en/insights/publications/2026/05/looking-ahead-to-nasdaqs-extended-trading-hours).
  - The overnight "Night Session" runs 21:00–04:00 ET, with a one-hour pause 20:00–21:00 on weeknights: [Simpson Thacher](https://www.stblaw.com/docs/default-source/memos/firmmemo_04_29_26), [Massive](https://massive.com/blog/us-equities-move-to-23-5-trading), [Navnoor Bawa commentary](https://www.navnoorbawaresearch.com/p/nasdaqs-night-session-enters-a-market). **[2+]**
- **Trade-date convention.** Trade dates move to a futures-style convention, so Monday's trading day begins on Sunday evening: [Massive](https://massive.com/blog/us-equities-move-to-23-5-trading). **[single-source]**
- **Not yet live.** Exchange overnight trading "has not yet commenced", because the SEC approvals were conditioned on the SIPs being ready. Exchange representatives expected to start on the SIP-ready date of 6 December. Sources: [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260929-23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch), [Mondaq repost](https://www.mondaq.com/unitedstates/commoditiesderivativesstock-exchanges/1854424/23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch). These are one publisher; [Skadden, Oct 2026](https://www.skadden.com/insights/publications/2026/10/nyse-arca-and-nasdaq-to-launch-extended-trading) and Jones Day are consistent.
- **SIP.**
  - The SEC approved the SIP plan amendments on 26 June 2026 according to [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260929-23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch), and on 7 July 2026 according to [SapInover](https://sapinover.com/insights/sip-23x5-second-domino). **[conflict on the date]** Both give 6 December 2026 as the SIP launch.
  - The SIPs plan a 24-hour model with a one-hour pause at 20:00 ET, which they expect to shorten over time: [Cboe Insights](https://www.cboe.com/insights/posts/what-does-it-take-to-offer-around-the-clock-equities-trading).
- **NYSE Arca.**
  - NYSE first proposed 01:30–23:30 ET (22 hours), and the SEC approved it on an accelerated basis.
  - An amended filing of 12 May 2026 adds a fourth "Overnight Session" from 21:00 to 04:00.
  - Launch depends on SEC approvals, SIP availability and DTCC's modernization work.
  - A Federal Register notice of 18 September 2026 says several exchanges, including NYSE Arca, intend to offer overnight sessions on 6 December 2026.
  - Sources: [NYSE Extended-Hours FAQ](https://www.nyse.com/publicdocs/nyse/NYSE_Extended_Hours_Trading_FAQ.pdf), [Liquidity Finder](https://liquidityfinder.com/news/nyse-moves-to-launch-22-hour-trading-day-2eefc), [Federal Register 2026-19124](https://www.federalregister.gov/documents/2026/09/18/2026-19124/self-regulatory-organizations-nyse-american-llc-notice-of-filing-and-immediate-effectiveness-of), [Jones Day](https://www.jonesday.com/en/insights/2026/09/nyse-and-nasdaq-move-to-23hour-trading-day-overnight-session-is-an-evolution-but-not-yet-a-revolution). **[2+]**
- **Cboe EDGX.**
  - Near-24x5 trading from Sunday 21:00 to Friday 20:00 ET, with a 20:00–21:00 pause Monday to Thursday. The target is December 2026, subject to approval and readiness.
  - Sources: [Global Trading](https://www.globaltrading.net/?p=41649), [FTF News](https://www.ftfnews.com/cboe-seeks-near-24x5-u-s-equities-trading/), [Cboe 2025 announcement](https://ir.cboe.com/news/news-details/2025/Cboe-Announces-Plans-to-Launch-24x5-U.S.-Equities-Trading-2025-NwujmKvsxb/default.aspx). **[2+]**
  - An older report gave a 14 October launch: [The TRADE](https://thetradenews.com/cboe-to-launch-24-hour-us-equities-trading). **[conflict; superseded by the December target]**
  - Cboe's separate plan for extended hours in equity options was postponed to "TBD": [Finance Magnates](https://www.financemagnates.com/forex/cboe-delays-early-trading-for-nvidia-and-tesla-options-again/).
- **24X National Exchange.**
  - It opened on 14 October 2025, postponed from 29 September, trading 04:00–20:00 ET.
  - 23/5 trading (Sunday 20:00 to Friday 20:00, with a daily one-hour pause) is expected in the second half of 2026. It depends on SIP 23x5, which 24X's FAQ expects in December 2026.
  - Sources: [Markets Media](https://www.marketsmedia.com/24x-national-exchange-opens-for-trading/), [Wikipedia](https://en.wikipedia.org/wiki/24X_National_Exchange), [WilmerHale news, Oct 2025](https://www.wilmerhale.com/en/insights/news/20251028-wilmerhale-advises-24x-national-exchange-in-the-opening-of-sec-approved-23-5-exchange), [24X FAQ](https://equities.24exchange.com/faqs). **[2+]**
- **LULD overnight bands.**
  - The SEC approved LULD Plan Amendment 27 on 5 August 2026. It creates "Overnight Price Bands" for "Overnight Protected Hours".
  - The bands are initially static, 20% above and below two reference prices: the listing market's official close, and the consolidated last round-lot sale as of 19:45 ET.
  - Amendment 29, which changes the timing of the consolidated price, took effect on a temporary basis (up to 120 days) by Federal Register notice of 13 October 2026.
  - The protections are expected to start on 6 December 2026.
  - Sources: [SEC Release 34-106042](https://www.sec.gov/files/rules/sro/nms/2026/34-106042.pdf), [LULD Plan overnight amendment](https://cdn.luldplan.com/plan-amendments/LULD_Overnight_Amendment_Final.pdf), [SEC Release 34-106624](https://www.sec.gov/files/rules/sro/nms/2026/34-106624.pdf), [Federal Register 2026-20799](https://www.federalregister.gov/documents/2026/10/13/2026-20799/joint-industry-plan-notice-of-filing-and-order-of-summary-effectiveness-on-a-temporary-basis-not-to). **[primary documents, but the details come from one search summary]**
- **No automatic overnight pauses.**
  - Hitting an overnight band does not trigger an automatic trading pause. The primary listing exchange can call a regulatory halt, including when orders are consistently placed outside the bands. A halted stock will not reopen during overnight hours.
  - The 23x5 exchanges will apply their clearly-erroneous rules overnight with the same standards as other extended-hours sessions.
  - Sources: [Mondaq/WilmerHale](https://www.mondaq.com/unitedstates/commoditiesderivativesstock-exchanges/1854424/23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch), [Nasdaq rule filing SR-NASDAQ-2025-106](https://listingcenter.nasdaq.com/assets/rulebook/nasdaq/filings/SR-NASDAQ-2025-106.pdf).
  - Nasdaq will have a dedicated night surveillance team, and halts a security across all sessions until the primary listing market resumes it.
- **Clearly-erroneous rule changes.** Filings of about 12 October 2026 by Nasdaq, PHLX, Nasdaq Texas and Cboe BYX amend the clearly-erroneous rules for the overnight period. They aim to "provide greater certainty … that trades executed within the Overnight Price Bands will stand". Sources: [Federal Register 2026-20806](https://thefederalregister.org/documents/2026-20806/self-regulatory-organizations-the-nasdaq-stock-market-llc-notice-of-filing-and-immediate-effectiveness-of-proposed-rule-), [2026-20805](https://thefederalregister.org/documents/2026-20805/self-regulatory-organizations-nasdaq-phlx-llc-notice-of-filing-and-immediate-effectiveness-of-proposed-rule-change-to-am), [2026-20807](https://thefederalregister.org/documents/2026-20807/self-regulatory-organizations-nasdaq-texas-llc-notice-of-filing-and-immediate-effectiveness-of-proposed-rule-change-to-a), [2026-20798](https://thefederalregister.org/documents/2026-20798/self-regulatory-organizations-cboe-byx-exchange-inc-notice-of-filing-and-immediate-effectiveness-of-a-proposed-rule-chan). **[2+]**
- **BOATS' overnight share.**
  - FINRA's settlement says BOATS has had about 95% of overnight volume since inception: [FINRA AWC](https://www.finra.org/sites/default/files/fda_documents/2024080158101%20Blue%20Ocean%20ATS%20CRD%20306512%20AWC%20vrp.pdf).
  - The Nocturnal Trading paper's snippet indicated about 80% (text cut off): [AFA listing](https://afajof.org/management/viewp.php?n=162176).
  - **[conflict on the share; agreement that one venue dominates]**

### Inferences
- **Before 6 December 2026,** an Alpaca overnight order depends on one ATS, with:
  - no SIP-consolidated overnight quotes
  - no LULD bands
  - no exchange clearly-erroneous regime
- **After 6 December,** exchange overnight sessions with SIP data and LULD bands should be more robust, but the bands come with no automatic pauses.
- The dates have already slipped: Nasdaq moved from early Q3 to December 2026, and 24X from September to October 2025 for its first phase. The new regime has no track record, which argues for re-evaluating overnight orders only after some months of live operation.
- The futures-style trade date would affect the system's daily bookkeeping (P&L day, "day" time-in-force, day-trade counting). Check this against Alpaca's documentation before December.

### Gaps
- Not determined:
  - whether the SEC has approved Cboe EDGX's 24x5 filing
  - the exact date of NYSE Arca's original 22-hour approval
  - which order types exchanges will accept overnight
  - DTCC/NSCC 24x5 clearing dates
  - whether and when Alpaca will route overnight orders to exchanges instead of BOATS
- The LULD band details (20%, 19:45 ET) rest on one search summary of SEC documents that could not be opened.

## 4. News timing, and whether an extended-hours order can avoid the overnight gap

### Takeaway
About 95–96% of earnings releases come outside regular hours (48% before the open, 52% after the close), and M&A news clusters on Monday mornings. After a release, prices reprice through quotes within milliseconds to seconds. An extended-hours order from this system therefore cannot avoid a news gap. It can only trade at the already-gapped price, paying spreads 3–6 times wider than in the regular session. Its only possible value is to cut exposure to later moves before the open: further news, macro drift, or a disorderly open. No data were found on the timing of FDA decisions, guidance or offerings.

### Cited Findings
- **Earnings timing.**
  - About 96% of firms report earnings outside regular hours, 48% before the open and 52% after the close (2006–2015 data): [Lyle, Rigsby, Stephen & Yohn (Columbia PDF)](https://business.columbia.edu/sites/default/files-efs/imce-uploads/LYLE%20LRSY_April_18_2018.pdf), [Wall Street Horizon copy](https://www.wallstreethorizon.com/upload/SSRN-id3064160.pdf).
  - About 95% according to [Kellogg Insight](https://insight.kellogg.northwestern.edu/article/traders-are-surprisingly-slow-to-respond-to-off-hours-earnings-announcements) and [CFO.com](https://www.cfo.com/news/whats-the-best-time-to-announce-earnings/659462/).
  - Papers citing Jiang et al. say more than 95% of US firms release outside the regular session: [Univ. of Memphis listing](https://digitalcommons.memphis.edu/facpubs/11594/), via search summary.
  - **[2+; data a decade old]**
  - A one-week snapshot for 12–16 October 2026 shows 38 of 51 reporters releasing before the open: [247wallst](https://247wallst.com/cards/sixteen-straight-quarters-of-eps-beats-go-on-the-line-at-6-0-blk-earnings-calendar-01m4wt9x67p9x2csdeqkz3khgg). **[single-source; not representative]**
- **Slower absorption of pre-open releases.**
  - Pre-open earnings releases are absorbed more slowly: "it takes a full four days" for early-morning news to be fully priced. Pre-open releases also show more abnormal volatility and volume afterwards. Sources: [Kellogg Insight](https://insight.kellogg.northwestern.edu/article/traders-are-surprisingly-slow-to-respond-to-off-hours-earnings-announcements), [Lyle et al.](https://business.columbia.edu/sites/default/files-efs/imce-uploads/LYLE%20LRSY_April_18_2018.pdf). **[2]**
  - Friday announcements also get a more delayed response: 60% of the total response is delayed on Fridays versus 40% on other days. Source: [NBER w11683](https://www.nber.org/papers/w11683.pdf). **[single-source]**
- **M&A timing.**
  - About 26% of M&A announcements come on a Monday, falling to 14% on Fridays: [Filipović thesis, Univ. of Fribourg](https://folia.unifr.ch/documents/319037/files/2018ECO012.pdf).
  - Firms are more likely to announce M&A on Mondays: [Penn State news](https://www.psu.edu/news/research/story/business-mergers-announced-fridays-draw-less-investor-attention).
  - Deals are released on Monday mornings "typically before the stock market opens", per the Financial Times as cited by [AJC](https://www.ajc.com/news/the-news/Q93AuQuDISyvKDbMwYV4KL).
  - **[2 for Monday clustering; pre-open timing is a single secondhand source]**
- **Speed of repricing.**
  - Prices jump immediately after after-hours earnings releases, within milliseconds for the largest stocks. More than 90% of after-hours announcement sessions show a jump. After 2016, post-announcement trading returns are consistent with efficient pricing. Sources: [arXiv 2601.08962](https://arxiv.org/html/2601.08962v1), [UC San Diego](https://today.ucsd.edu/story/earnings-news-cause-immediate-stock-price-jumps-sometimes-moving-whole-market). **[2+]**
  - After hours, quotes reprice first while trades are sparse (median 16): [Grégoire & Martineau, JAR](https://onlinelibrary.wiley.com/doi/full/10.1111/1475-679X.12394).
  - "A significant portion of the price change … occurs immediately after the earnings releases" in after-hours trading: [Jiang et al., JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/information-content-of-earnings-announcements-evidence-from-afterhours-trading/39171BF13B8D5EE4890B930F2FF4E19C).
- **Where the overnight move is priced.**
  - Barclay & Hendershott argue that the large overnight weighted price contribution of high-volume stocks reflects pre-open trading rather than informed late-night trading, and that pre-open prices include the overnight return: [Hendershott PDF](https://faculty.haas.berkeley.edu/hender/after_hours_price_discovery.pdf). **[single-source]**
  - Pre-market returns partly reverse the "dark" overnight component, most strongly when the pre-market is thin. Explanatory power for the close-to-open return builds through the pre-market: [Perreten](https://mfc3.eventsadmin.com/Papers/ViewContribution?cid=14387&h=34E9F3229E21B084DE4A06E94CD0FC5F). **[single-source]**
  - The 20:00–04:00 session adds meaningful price discovery for non-US firms and macro ETFs: [Nocturnal Trading, SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5181159).

### Inferences
- The system does not hold through earnings, which removes the most common scheduled gap. What remains is mostly unscheduled single-name news (M&A, guidance, offerings, legal or regulatory news, FDA surprises) and macro shocks.
- **Single-name news:** the jump completes on the quote before an API client could react. The after-hours price is, on average, an unbiased estimate of the next open (efficient after 2016), so an extended-hours exit has roughly zero expected gain and a certain extra cost of 3–6 times wider spreads plus price impact.
- **Where an exit could help:**
  - macro events that unfold over hours, such as the 2024-08-05 Japan selloff (see section 5)
  - follow-on news after the first release
  - disorderly opens

  None of these benefits has been quantified.
- Thin pre-market trading tends to reverse (Perreten). Selling aggressively into a thin pre-market risks selling at a temporarily depressed price. This argues for collars, patience and leaving any remainder for the open.
- The only reliable way to avoid a scheduled gap is not to hold through it. The "no holding through earnings" rule could be extended to other scheduled binary events, such as FDA PDUFA dates. This is a design suggestion.

### Gaps
- No statistics were found on the timing of FDA decisions, guidance changes or offerings outside regular hours.
- No 2020–2026 study was found that measures, for liquid US stocks, what share of the close-to-open gap is already priced by 16:30, 20:00, 08:00 or 09:25.
- No study was found comparing an after-hours or pre-market exit with an exit at the open for positions hit by news, net of costs.

## 5. Risks: overnight venue failures (Blue Ocean, 5 August 2024), erroneous-trade rules, thin books, LULD and halts

### Takeaway
The overnight venue failed in the one large stress event so far. On 5 August 2024 BOATS cancelled every trade between 01:45 and 03:06 ET and halted; brokers suspended overnight trading, and service was restored only partially over the following week. In 2026 FINRA fined BOATS $550,000 for manipulation- and AML-surveillance failures. No later trade-cancellation incident was found, but the search was cut short.

Outside regular hours today:
- there is no LULD; overnight bands start on 6 December 2026, without automatic pauses
- clearly-erroneous thresholds are twice the regular-hours ones (20/10/6% versus 10/5/3%)
- books are thin
- stop orders do not trigger
- halts persist across sessions

### Cited Findings
- **The 5 August 2024 incident.**
  - BOATS cited capacity problems during a volume surge. The surge followed the Bank of Japan rate rise, weak US jobs data and the Nikkei crash.
  - BOATS first said "a small percentage of trades" had to be cancelled. It then said it cancelled all trades between 01:45 and 03:06 ET and halted trading. It promised a new technology system by the end of the month.
  - Sources: [Blue Ocean ATS on X](https://x.com/BlueOceanATS/status/1820851212717068719), [CNBC](https://www.cnbc.com/2024/08/05/robinhood-no-24-hour-trading-monday-due-to-issue-at-third-party-venue.html), [BNN Bloomberg](https://www.bnnbloomberg.ca/investing/2024/08/06/biggest-overnight-stock-venue-suspends-trading-after-volatility/), [Markets Media](https://www.marketsmedia.com/blue-ocean-ats-resumes-after-cancelling-trades/). **[2+]**
- **Effect on brokers.** Robinhood suspended its 24 Hour Market. Trades during the suspension were cancelled, and users reported reversed trades. Sources: [CNBC](https://www.cnbc.com/2024/08/05/robinhood-no-24-hour-trading-monday-due-to-issue-at-third-party-venue.html), [Cointelegraph](https://cointelegraph.com/news/robinhood-24-hour-trade-suspend-8-hours). **[2]**
- **Resumption.**
  - BOATS resumed on 6 August for the 7 August session with a limited set of symbols: [Markets Media](https://www.marketsmedia.com/blue-ocean-ats-resumes-after-cancelling-trades/), via search summary.
  - It "shut down its system on August 5, 2024 and partially reopen[ed] on August 12": [Nocturnal Trading (AFA listing)](https://afajof.org/management/viewp.php?n=162176).
  - **[2; dates partly differ]**
- **Korea.**
  - Korean brokerages halted daytime US-share trading: [Korea JoongAng Daily](https://www.koreajoongangdaily.com/business/korean-brokerages-halt-us-market-access-after-platform-crashes/12431745).
  - About KRW 630 billion of orders were cancelled: [Korea Herald](https://m.koreaherald.com/article/10423915). **[single-source for the figure]**
  - Blue Ocean's CEO apologised to Korean investors in February 2025: [Korea Times](https://www.koreatimes.co.kr/business/banking-finance/20250206/interview-blue-ocean-ceo-apologizes-to-korean-investors-vows-to-rebuild-trust).
- **Litigation.** Fundamental Interactions sued Blue Ocean in 2024, alleging the outages breached its service-level agreements: [PRWeb](https://www.prweb.com/releases/fundamental-interactions-files-lawsuit-against-blue-ocean-technologies-over-trading-system-failures-302258154.html), [The Investor](https://www.theinvestor.co.kr/article/10425289). **[2]** Its current status was not found.
- **FINRA fine.** FINRA fined and censured BOATS for $550,000 in 2026 (reported in May 2026). The case covers AML and manipulation-surveillance failures (spoofing, layering, wash trading) dating back to at least January 2023. Sources: [FINRA news release](https://www.finra.org/media-center/newsreleases/2026/finra-fines-pictet-overseas-and-blue-ocean-ats-aml-and-supervisory), [FinanceFeeds](https://financefeeds.com/finra-fines-blue-ocean-ats-550000-over-overnight-manipulation-surveillance-failures/), [ACAMS](https://www.acams.org/en/enforcement-action/finra-fines-blue-ocean-ats-550000-aml-market-manipulation-surveillance-failures). **[2+]**
- **January 2025 record session.** A headline reports a record BOATS session on the DeepSeek selloff: [Markets Media](https://www.marketsmedia.com/deepseek-triggers-record-trading-session-at-blue-ocean-ats/). **[title only; no details on whether it ran cleanly]**
- **Clearly-erroneous numerical guidelines.**

  | Price band | Regular hours | Pre-opening and after-hours |
  |---|---|---|
  | Up to $25 | 10% | 20% |
  | $25–50 | 5% | 10% |
  | Over $50 | 3% | 6% |

  - Events covering 5 or more securities use 10%, and events covering 20 or more use 30%. The thresholds are multiplied for leveraged ETFs.
  - The reference price is normally the consolidated last sale.
  - Sources: [SEC exhibit 5 (exchange CE rule)](https://www.sec.gov/file/exhibit-5-8012), [Cboe BZX 2022 exhibit](https://www.sec.gov/files/rules/sro/cboebzx/2022/34-95259-ex5.pdf), [NYSE Arca 2009 filing](https://www.sec.gov/files/rules/sro/nysearca/2009/34-60706.pdf). **[2+; that these thresholds are still current was not re-verified]**
- **LULD hours.**
  - The LULD Plan operates only 09:30–16:00: [industry member poll on investor protections for 24-hour trading (publisher not identified)](https://cdn.craft.cloud/9fb2ef98-fcc6-431d-b09d-d12ff28cf0f0/assets/comment-letters-exemption-letters-whitepapers/Member-Poll_Evolving-Investor-Protections-for-24-Hour-Trading_05a.pdf), [LegalClarity](https://legalclarity.org/limit-up-limit-down-price-bands-limit-states-and-pauses/). **[2; weak sources]**
  - About three quarters of poll respondents favour extending LULD to all hours. **[single-source]**
- **Thin books.**
  - Disclosures warn of partial or no executions: [Citi Rule 2265 disclosure](https://www.citigroup.com/rcs/icgPublic/storage/public/disclosures/FINRA-Rule-2265.pdf), [Alpaca Learn: How to Trade 24/5](https://alpaca.markets/learn/how-to-trade-us-stocks-24_5-overnight-with-python-and-alpaca).
  - Only two overnight market makers: [Nocturnal Trading](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5181159).
  - A median of 16 after-hours trades following an earnings release: [Grégoire & Martineau](https://onlinelibrary.wiley.com/doi/full/10.1111/1475-679X.12394).
- **Halts.** Primary-market halts apply across all sessions, and a halted stock does not reopen overnight: [Mondaq/WilmerHale](https://www.mondaq.com/unitedstates/commoditiesderivativesstock-exchanges/1854424/23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch). Alpaca exposes an `overnight_halted` flag on assets: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading).

### Inferences
- The scenario where an overnight exit is most valuable is a macro crash that unfolds over hours. That is exactly when the overnight venue proved fragile.
- An overnight fill can be cancelled hours later. The system must re-read positions from the broker after any venue incident and must never assume a fill is final overnight.
- The exchange-run pre-market and after-hours sessions (04:00–09:30 and 16:00–20:00) have SIP-reported quotes and trades and many venues. They are more robust than the single-ATS overnight session, but they still lack LULD and have double the clearly-erroneous thresholds.
- Keeping limit prices close to the live quote keeps fills well inside the thresholds, so they are unlikely to be broken.
- The SIP's current 04:00–20:00 hours are inferred, not verified this session.

### Gaps
- Incidents at BOATS or other overnight venues after August 2024 (for example during the April 2025 tariff selloff) could not be searched; the budget was exhausted.
- FINRA's clearly-erroneous rule for OTC and ATS trades (Rule 11892) was not checked.
- Whether Alpaca customers' overnight fills were cancelled on 2024-08-05 is unknown. Alpaca's Trading API did not offer overnight trading then; its Broker API 24/5 launched in May 2025.
- No Alpaca-specific extended-hours incident reports were found.

## 6. What a prudent professional system would do: recommendation

### Takeaway
**Recommendation (inference from the evidence above):** replace "orders only 09:30–16:00" with the following rule.
- New positions are still opened only 09:30–16:00.
- Reduce-only limit orders are also allowed in the pre-market (04:00–09:30 ET) and after-hours (16:00–20:00 ET) sessions. They fire only on defined triggers, pass a quote-quality gate, are collared to the live quote, and are sized to a fraction of displayed size.
- No orders at all from 20:00 to 04:00 ET. Re-evaluate after the exchange and SIP 23x5 overnight sessions (due 6 December 2026) have run cleanly for at least about three months and Alpaca routes overnight orders to exchanges.
- Build and test the capability in paper and shadow mode first; switch it on live only after acceptance tests.

**Confidence:**
- About 60% (moderate) that this narrow exception beats "never".
- About 80% that the overnight session should stay closed for now.
- About 90% that, if extended-hours orders are allowed, they must be limit-only, reduce-only and collared to the live quote.

The deciding evidence is that an extended-hours exit cannot avoid a news gap. Its value is limited to cutting exposure to later moves, at 3–6 times regular-session costs.

### Cited Findings
- **Alpaca constraints the design must fit:**
  - Limit orders only, `day` or `gtc`, with `extended_hours=true`.
  - Stops and brackets give no protection outside regular hours.
  - Overnight `day` orders persist until 20:00 the next day.
  - Overnight quotes are indicative and overnight trades delayed 15 minutes.
  - Paper accounts support 24/5.
  - Sources: [Alpaca docs: 24/5 Trading](https://docs.alpaca.markets/us/docs/245-trading), [Alpaca API reference](https://docs.alpaca.markets/us/reference/postorder), [Alpaca docs: Placing Orders](https://docs.alpaca.markets/us/docs/orders-at-alpaca), [Alpaca on X](https://x.com/AlpacaHQ/status/2016526691892670801).
- **Gap timing.** Prices jump within milliseconds and are efficient after 2016, and quotes lead trades after hours. So the gap cannot be avoided, and collars must reference quotes. Sources: [Christensen et al.](https://arxiv.org/html/2601.08962v1), [Grégoire & Martineau](https://onlinelibrary.wiley.com/doi/full/10.1111/1475-679X.12394).
- **Costs:** spreads 3–4 times regular hours, and overnight retail spreads about 3 times with price impact about 6 times: [Barclay & Hendershott 2004](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2004.00646.x), [Nasdaq](https://www.nasdaq.com/articles/looking-all-day-data-24-hour-trading).
- **Pre-market reversal** when liquidity is thin: [Perreten](https://mfc3.eventsadmin.com/Papers/ViewContribution?cid=14387&h=34E9F3229E21B084DE4A06E94CD0FC5F).
- **Clearly-erroneous thresholds** outside regular hours are 20/10/6%: [SEC exhibit](https://www.sec.gov/file/exhibit-5-8012). LULD overnight bands of ±20% with no automatic pause start on 6 December 2026: [SEC Rel. 34-106042](https://www.sec.gov/files/rules/sro/nms/2026/34-106042.pdf), [Mondaq](https://www.mondaq.com/unitedstates/commoditiesderivativesstock-exchanges/1854424/23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch).
- **Overnight venue fragility:** the August 2024 cancellations and the 2026 FINRA fine: [CNBC](https://www.cnbc.com/2024/08/05/robinhood-no-24-hour-trading-monday-due-to-issue-at-third-party-venue.html), [FINRA](https://www.finra.org/media-center/newsreleases/2026/finra-fines-pictet-overseas-and-blue-ocean-ats-aml-and-supervisory).
- **Few institutions trade off-hours.** Off-hours trading is mostly retail, with limited institutional participation: [IOSCO 2026](https://www.iosco.org/library/pubdocs/pdf/IOSCOPD820.pdf).
- **Most news arrives outside regular hours:** about 95% of earnings, and M&A clusters on Monday mornings: [Lyle et al.](https://business.columbia.edu/sites/default/files-efs/imce-uploads/LYLE%20LRSY_April_18_2018.pdf), [Filipović](https://folia.unifr.ch/documents/319037/files/2018ECO012.pdf).

### Inferences
**Options compared.**

| Option | Description | Assessment |
|---|---|---|
| A | Never trade outside the regular session (the owner's rule) | A close second |
| B | Reduce-only, triggered limit orders in pre-market and after-hours | Recommended |
| C | B plus the 20:00–04:00 overnight session | Rejected for now |

Option C is rejected for now because overnight trading today means:
- one ATS (BOATS) that failed in the 2024 stress event and was fined in 2026
- indicative quotes and delayed trades at Alpaca
- no SIP data and no LULD
- a regime change due on 6 December 2026

**Evidence for B over A:**
- Material news mostly arrives outside 09:30–16:00, and stops do not work there. Under A the system cannot act for 17.5 hours a day while holding up to 75% gross overnight.
- After-hours prices are informationally efficient (Jiang et al.; Christensen et al.). An exit at the after-hours quote is fair minus the spread, not a systematically bad price.
- Alpaca supports it with limit orders and a 24/5 paper environment.
- It caps exposure to developments that unfold over hours, such as macro selloffs, follow-on news or disorderly opens.

**Evidence for A over B:**
- An exit cannot beat the jump, so its expected gain over exiting at the open is about zero, while its cost is 3–6 times higher.
- Liquidity providers are adversely selected (SIFMA), and thin pre-markets tend to reverse (Perreten).
- Operational risk: busted or cancelled fills, no LULD, wider clearly-erroneous thresholds, thin books, and an autonomous system acting while nobody watches.
- The owner's sizing already caps the loss from a 50% gap on one name at 2% of equity, and earnings are excluded.
- Institutions largely stay out of off-hours trading (IOSCO).

**Proposed policy for B.** Every number below is a design suggestion to calibrate on Alpaca's historical extended-hours quotes for the system's universe. None is a sourced fact.

1. **Scope.**
   - Only orders that reduce the absolute size of an existing position.
   - Enforce that order quantity is at most the position minus pending reducing orders. Never flip a position, never open one, never increase gross exposure.
   - No new hedges.
2. **Order specification.**
   - `type=limit`, `time_in_force=day`, `extended_hours=true`. Never `gtc`; never stop or bracket orders.
   - Allowed windows are 04:00–09:28 and 16:00–20:00 ET, and an order is placed only when the quote gate passes.
   - Cancel all extended-hours orders at 09:28 and at 20:00. Hand any remainder to the regular-session logic or the opening auction.
3. **Triggers (any one).**
   - **T1, news:** material news on a held name from a primary source (press release, 8-K, exchange notice) or from two or more independent feeds, *and* the strategy marks the position's thesis as invalid. News alone is not a trigger.
   - **T2, gap versus risk budget (consistent with the owner's sizing):**
     - Fire when the loss on a position at the live midpoint, measured from the last regular-session close, reaches about 0.5% of equity.
     - Then reduce until loss-so-far + 50% × remaining notional ≤ 2% of equity.
     - Example, long at 4% of equity that falls 25%: the loss is 1% and the position is now 3% of equity. The rule allows at most 2% remaining, so sell about a third.
     - At a 50% drop the rule closes the whole position.
     - For shorts the same formula applies to the adverse rise.
   - **T3, portfolio:** the book's live-midpoint loss since the close reaches a set level (for example 1.5% of equity), or a broad-market ETF (SPY or QQQ) quote moves a set amount (for example 3%) against net exposure. Then reduce the largest-risk and least-liquid positions first, down to an owner-set lower gross.
   - **T4, halts:** never place orders while a name is halted (asset status or `overnight_halted`). After a halt lifts in extended hours, wait until the quote gate has passed continuously for several minutes (for example 5–10).
4. **Quote-quality gate.** All of these must hold:
   - a two-sided quote less than about 5–10 seconds old
   - a quoted spread of no more than about 100 bps (versus the 10 bps entry filter), or no more than a calibrated multiple of the name's typical extended-hours spread
   - displayed size at the touch of at least twice the child order
   - a second, independent data source agreeing on the midpoint to within a small tolerance
5. **Collar.**
   - Price passively at or near the midpoint first, then step toward the touch over a few minutes.
   - Never sell below `max(bid, mid × (1 − c))` and never buy above `min(ask, mid × (1 + c))`, with c around 0.5–1%. Never sweep deeper levels.
   - Do not reference the last trade or the last regular-session close for pricing; quotes lead and trades lag.
   - Sanity band: if the midpoint is more than 20% from the last regular-session close, or beyond the clearly-erroneous guideline from the last sale, require a second source to confirm it before acting. The 20% mirrors the LULD overnight band and the clearly-erroneous threshold for stocks of $25 or less.
6. **Size.**
   - Each child order is at most about 50% of displayed size at the touch, and at most about 25% of the original position per 5 minutes.
   - Accept partial completion; the remainder goes to the open.
7. **Kill switches.** Stop all extended-hours activity and alert the owner after any of the following:
   - a cancelled or busted fill
   - a broker or venue incident, or a halt
   - stale or diverging data
   - more than a few rejects
   - reaching a daily cap on extended-hours notional

   Re-read positions from Alpaca after every incident. Report every extended-hours action to the owner.
8. **Validation before going live.**
   - Run in shadow mode on live quotes, with order placement in paper, for a set number of trigger events or months.
   - Score each action against the next opening-auction price and the first 15 minutes' VWAP.
   - Enable live trading only if the mechanics are error-free and costs are within expectations. Paper fills are not realistic in thin books.
9. **When to revisit the overnight session.**
   - Exchange overnight sessions with SIP data and LULD overnight bands live since 6 December 2026, with at least about three months free of major incidents.
   - Alpaca routing overnight orders to exchanges with real-time quotes.
   - If both hold, consider extending the same policy to 21:00–04:00 with smaller size caps.

### Gaps
- No source was found describing how institutional or proprietary desks actually govern extended-hours exits; the search budget ran out. IOSCO's "limited institutional participation" is the only indirect evidence.
- All numeric parameters in the policy are uncalibrated. Calibrating them needs Alpaca's historical pre-market and after-hours quotes for the universe: spread and displayed size by time of day, and how often T2 and T3 would have fired.
- No empirical comparison was found between an extended-hours exit and an exit at the open for news-hit positions, net of costs. That comparison would settle the A-versus-B question; the shadow-mode trial is designed to produce it.
- Not verified:
  - whether Alpaca applies its own limit-price collars in extended hours
  - whether pre-market `day` orders join the opening auction
  - regulatory fees
  - Alpaca's day boundary after 6 December 2026

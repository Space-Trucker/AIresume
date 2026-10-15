# Fact-check of the trading goal, version 4

Checked on 2026-10-15 against `GOAL.md` and `goal.toml` (both version 4, dated 2026-10-15). Only
those two files were read. `REPORT.md`, `../reports/`, `../research_notes/` and the session
transcripts were not opened, so every claim was checked independently of the builder's sources. No
Fable model was used.

## Summary

- **64 external claims checked**: 48 confirmed, 10 partly right, 2 contradicted, 4 not verifiable
  here. Three more figures come from the project's own data and can't be checked from outside; they
  are listed at the end.
- **No blocking or major findings.** None of the external facts behind a risk limit, a cost or a
  decision is wrong in a way that would loosen the goal. The 12 findings are all minor. They correct
  examples, a citation's wording, two dated figures and two statements.
- **The corrections that matter most:**
  1. **F-1, F-2.** The two gaps behind the 50% overnight jump are misstated. Yahoo closed +48.0% on
     1 February 2008 (about +49% in morning trading), and NVIDIA closed −30.7% on 3 July 2008. No
     source gives +49.5% or −28.0%. The 50% assumption still covers both regular-session moves.
  2. **F-3.** 13 March 2023 was not a 50% industry-wide jump. The regional-bank ETF fell 12.3%,
     while First Republic fell 61.8%. The 8% industry limit can stay, but its rationale needs new
     wording.
  3. **F-12.** The controls claim only one deviation from the checklists they cite. In fact C14's
     50 ms is the US audit-trail standard, while MiFID II asks for 1 ms in algorithmic trading.
  4. **F-11.** `goal.toml` says the 475(f) election "must be made before the tax year it applies
     to". The election is actually due by the original due date of the previous year's return,
     which falls inside the year it applies to. `GOAL.md` states this correctly.
  5. **F-5, F-7.** FINRA has paused its trading activity fee for trades from 1 October to
     31 December 2026. IEX now carries about 4% of US volume, not 2.5%.
- **Caveats on confirmed claims** (see Observations):
  - Real single-name jumps have exceeded the stated sizes. First Republic fell 62% against an
    assumed 50%, and a biotech takeover target more than tripled against an assumed 100%. The
    event-prone rule and the universe filters cover the cases found.
  - Alpaca's stops survive a client crash only as GTC orders, and bracket stop legs wait for a
    complete fill.
  - The new model-risk guidance (SR 26-2) puts generative and agentic AI outside its scope.
- **How sure.** Direct page fetches failed: WebFetch got DNS errors for arxiv.org, stooq.com and
  hexus.net, and the proxy refused downloads. So every figure here comes from search-result extracts
  of the pages cited, not from reading them in full. Rows that rest on one source, or only on the
  broker's own pages, say so.

## Method

- **Searching.** About 65 web searches, two of them in extended mode, run highest-impact first
  (limits, then costs, then decisions, then citations). Each claim was searched until two
  independent sources agreed or the search ran out.
- **Counting sources.** A primary source counts as one source, and two copies of the same release
  count as one. For Alpaca's own terms, Alpaca's pages are authoritative but still count as one
  source.
- **Verdicts:**
  - *Confirmed*: two independent sources agree, or a primary source and an independent report agree.
  - *Partly right*: the substance holds, but a number, a date or the reading differs.
  - *Contradicted*: the sources say otherwise.
  - *Not verifiable here*: no source settles it.
- **Ranking.** Claims are ranked by what would change in the goal if they were wrong:
  - **L**: a risk limit, constraint or gate number;
  - **C**: a cost;
  - **D**: a decision or a control;
  - **Cit**: only a citation.

  Within each tier, the claims closest to a number come first.
- **Recomputed arithmetic.** Wherever the goal's arithmetic rests on an external fact, it was
  recomputed: trading days since 2016, the expected maximum of many forecasts, square-root impact,
  and the price moves.

## Claims, ranked by what would change if they were wrong

Line numbers refer to `GOAL.md`. Keys in backticks are in `goal.toml`.

| # | Claim | Where | Verdict | Sources | If wrong, what changes |
|---|---|---|---|---|---|
| 1 | Yahoo gapped +49.5% on 1 Feb 2008 on Microsoft's bid | 38, 168; `jump_overnight_pct` | **Partly right (F-1).** It closed +48.0% ($19.18 to $28.38), was about +49% in morning trading and +56% pre-market. No source gives +49.5% | [SEC Form 425 ($19.18 close)](https://www.sec.gov/Archives/edgar/data/0001011006/000095012308001038/y47867exv99w1.htm); [Felix Salmon ($28.38)](https://www.felixsalmon.com/2008/02/the-arithmetic-of-the-microsoft-yahoo-bid/); [CNNMoney (+48%)](https://money.cnn.com/2008/02/01/technology/microsoft_yahoo/index.htm); [AP via Meridian Star (+49%, $28.59)](https://meridianstar.com/2008/02/01/microsoft-makes-unexpected-44-6b-bid-for-yahoo/) | L: the 50% overnight jump behind the 4% overnight cap per stock |
| 2 | NVIDIA gapped −28.0% on 3 Jul 2008 after its warning | 168 | **Partly right (F-2).** It closed −30.7% ($18.03 to $12.49), and Fortune reported −31%. No source gives −28.0% | [Fortune](https://fortune.com/2008/07/03/miss-by-chipmaker-nvidia-rattles-investors); [Motley Fool](https://www.fool.com/investing/general/2008/07/08/nvidia-explodes.aspx); [HEXUS ($12.49, −30.73%)](https://HEXUS.net/qan3r); [The Register (after hours $14.08)](https://www.theregister.com/2008/07/03/nvidia_forecast_glitch/) | L: same (corroborates the 50% jump) |
| 3 | Short sales and margin need $2,000 of equity | 152, 590, 608; `min_equity_for_shorts_usd`, `min_initial_capital_usd` | **Confirmed** | [Alpaca support](https://alpaca.markets/support/determine-margin-account); [Alpaca docs](https://docs.alpaca.markets/docs/margin-and-short-selling); [Schwab](https://advisorservices.schwab.com/story/introduction-to-pattern-day-trader-rules) | L: the G3 floor of $2,500 |
| 4 | FINRA's intraday margin standard replaced the pattern-day-trader rule on 2026-06-04 (Regulatory Notice 26-10; SEC approval 2026-04-14), and Alpaca applies it | 152, 607–608 | **Confirmed.** The notice was published 20 Apr 2026. One law firm dates the SEC approval to 15 Apr. Firms may phase it in until 20 Oct 2027; Alpaca switched over on 4 Jun 2026 | [FINRA RN 26-10](https://www.finra.org/rules-guidance/notices/26-10/); [WilmerHale (approved 14 Apr)](https://wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard); [King & Spalding](https://www.kslaw.com/insights/articles/finra-adopts-sweeping-changes-to-margin-requirements-for-day-trading); [ACA Group](https://www.acaglobal.com/industry-insights/finra-ends-the-pattern-day-trader-rule/); [Alpaca blog](https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/) | L: under the old rule, a G3 account below $25,000 could not day trade, so the G3 floor would rise to $25,000 |
| 5 | Market-wide circuit breakers trigger at 7%, 13% and 20%. Levels 1 and 2 only pause trading before 15:25, so they don't bound an overnight gap | 169, 174; `jump_overnight_etf_pct`, `max_overnight_net_pct` | **Confirmed** | [NYSE filing 34-88402](https://www.sec.gov/files/rules/sro/nyse/2020/34-88402.pdf); [NYSE Arca filing 34-88414](https://www.sec.gov/files/rules/sro/nysearca/2020/34-88414.pdf); [futures.io](https://futures.io/articles/trading/Circuit-Breaker) | L: the 15% net overnight limit and the 20% index-fund jump |
| 6 | A broad index has never gapped 20% | 169 | **Confirmed.** The worst SPY opening gaps were about 8.3% (24 Oct 2008) and 8.2% (after 9/11). March 2020's worst gap was not separately confirmed | [CNBC with Bespoke data](https://www.cnbc.com/2020/03/09/sp-500-etf-just-has-its-third-worst-open-ever-behind-only-the-financial-crisis-and-911.html); [SentimenTrader](https://sentimentrader.com/blog/the-morning-after) | L: the 10% overnight cap for a broad index fund |
| 7 | SVB was halted (10 Mar 2023) and delisted, a total loss | 170–171; `event_prone_text` | **Confirmed.** Halted 08:35 ET on 10 Mar; suspended 28 Mar; delisted 12 May. Its first over-the-counter trade was $0.53, against a last Nasdaq price of $106.04 (−99.5%) | [Nasdaq halt notice](https://www.tipranks.com/news/press-releases/nasdaq-halts-svb-financial-group); [SEC Form 25-NSE](https://www.sec.gov/Archives/edgar/data/719739/000135445723000327/sivbdelistreason.txt); [InvestorPlace](https://investorplace.com/2023/03/delisted-bank-stocks-signature-and-svb-financial-start-trading-otc/) | L: the 4% single-jump bound and the 2% cap for a bank under a run |
| 8 | US regional banks jumped 50% across the industry on 13 Mar 2023 | 172 | **Partly right (F-3).** First Republic fell 61.8%, but the regional-bank ETF fell only 12.3% | [S&P Global](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2023/3/us-bank-stocks-rally-recover-some-losses-74764380); [Motley Fool](https://www.fool.com/investing/2023/03/20/first-republic-pacwest-western-alliance-sold-off/) | L: the 8% overnight industry cap |
| 9 | A biotech short can double on a regulatory decision or a takeover | 170; `event_prone_text` | **Confirmed, and exceeded.** Provention Bio more than tripled on 13 Mar 2023 (a 273% premium); CinCor rose 135% pre-market on 9 Jan 2023 (O-1) | [STAT](https://www.statnews.com/2023/03/13/french-pharma-sanofi-buys-maker-of-diabetes-treatment-for-2-9-billion/); [Barchart](https://www.barchart.com/story/news/15037397/monday-merger-mania-just-made-these-2-biotech-stocks-big-winners); [TipRanks (CinCor)](https://www.tipranks.com/news/cinc-snapped-up-by-azn-for-1-8-billion) | L: the 2% event-prone cap (100% jump) |
| 10 | A 20% intraday jump means a news halt, or two 10% price bands | 167; `jump_intraday_pct` | **Partly right (F-4).** Limit-up/limit-down bands are 5% for Tier 1 stocks (S&P 500, Russell 1000) and 10% only for Tier 2 stocks above $3 | [LULD Plan](https://www.luldplan.com); [SEC 34-101036 (Tier 2: 10%)](https://sec.gov/files/rules/other/2024/34-101036.pdf); [Gotrade (Tier 1: 5%)](https://www.heygotrade.com/en/blog/limit-up-limit-down-rules-luld-trading-halts/) | L: the 10% intraday position cap |
| 11 | McLean and Pontiff: returns are 58% lower after publication, so 42% remains | 498–499; `published_edge_multiplier` | **Confirmed.** Across 97 predictors, returns were 26% lower out of sample and 58% lower after publication | [Paper (JF 2016)](https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf); [Boston College summary](https://bc.edu/bc-web/schools/carroll-school/news/2017/pontiff-paper.html) | L: the 0.42 multiplier on published effects |
| 12 | The Rule 201 short-sale price test | 80, 152; C4 | **Confirmed.** A 10% fall from the prior close allows short sales only above the national best bid, for the rest of that day and the next | [WilmerHale](https://www.wilmerhale.com/insights/publications/the-return-of-a-short-sale-price-test-sec-adopts-alternative-uptick-rule-in-split-vote-february-25-2010); [Morgan Lewis](https://www.morganlewis.com/pubs/sec-imposes-new-short-sale-price-limitation-on-circuit-breaker-basis) | L: the short-sale rule (O5) |
| 13 | A current easy-to-borrow status serves as a locate | 152; KR5.3 | **Confirmed.** Reg SHO Rule 203(b)(1) requires "reasonable grounds"; easy-to-borrow lists under 24 hours old qualify | [SEC Reg SHO guide](https://sec.gov/investor/pubs/regsho.htm); [GlobalCapital](https://www.globalcapital.com/article/28mssnrew086objkx3idi/derivatives/sec-short-sale-regulations-part-one) | L: KR5.3 |
| 14 | The SEC's Section 31 fee is $20.60 per $1 million (from 2026-04-04) | 213 | **Confirmed.** It was $0.00 until 3 Apr 2026. The $20.60 rate runs from 4 Apr until 60 days after the FY2027 appropriation is enacted | [SEC advisory 2026-2](https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2); [SEC order 34-104909](https://www.sec.gov/files/rules/other/2026/34-104909.pdf); [FINRA notice 3/17/26](https://www.finra.org/rules-guidance/notices/information-notice-20260317) | C: 0.21 bps on each sale |
| 15 | FINRA's trading activity fee is $0.000195 a share, capped at $9.79 | 213 | **Partly right (F-5).** The 2026 rate and cap are right, but the fee is paused for trades from 1 Oct to 31 Dec 2026 | [Investrade](https://www.investrade.com/fees/); [Brokerage-Review](https://www.brokerage-review.com/account-fee/taf-fee.aspx); [SR-FINRA-2026-021](https://www.finra.org/sites/default/files/2026-09/SR-FINRA-2026-021.pdf) | C: about 0.04 bps on a sale |
| 16 | Alpaca charges no borrow fee on easy-to-borrow shorts for Trading API users | 214, 609 | **Confirmed**, but only on the broker's own pages, and the announcement's year isn't shown | [Alpaca blog](https://alpaca.markets/blog/zero-borrow-fees-on-short-selling-etb-stock-shares-alpaca-trading-api/); [Alpaca support](https://alpaca.markets/support/short-selling-fees) | C: the cost of overnight shorts |
| 17 | Square-root impact at the liquidity limit is 1.2–2.4 bps a side | 229–231 | **Confirmed.** The literature puts the prefactor Y at about 1. Recomputed: 1.19–2.38 bps for Y = 0.5–1, with σ = 168 bps and 0.02% of daily volume | [Bouchaud review (Y ≈ 1)](https://arxiv.org/pdf/2105.00521); [Tóth et al. 2011](https://doaj.org/article/aa335a8de8954ff386b6bb094d176225) | C: the 1.5 bps slippage charge |
| 18 | Alpaca's Algo Trader Plus plan costs $99 a month | 64, 620 | **Confirmed** | [Alpaca docs](https://docs.alpaca.markets/docs/about-market-data-api); [apis.io](https://apis.io/plans/alpaca-markets/alpaca-markets-plans-pricing/); [TradersPost](https://blog.traderspost.io/article/alpaca-paper-trading) | C: running cost from G2 on |
| 19 | After-hours spreads are 3 to 4 times the regular session's | 89, 573–574 | **Partly right (F-6).** The 3–4× figure comes from 1999–2000 data. Recent measures range from about 1.4–2.4× overnight to about 7× after earnings | [Barclay & Hendershott 2004](https://academicnewsletter.sufe.edu.cn/info/361191); [Nasdaq overnight study](https://www.nasdaq.com/articles/looking-all-day-data-24-hour-trading); [arXiv 2601.08962](https://arxiv.org/pdf/2601.08962) | C/D: the cost of an after-hours exit (decision 8) |
| 20 | Alpaca's intraday history starts in 2016 (2016-01-01), about 2,700 trading days ago | 65, 622–626 | **Confirmed**, with nuances: consolidated (SIP) bars start 2016-01-04, the first trading day, while IEX-feed history starts only in 2020. Recomputed: 2,711 trading days, 311 beyond 2,400 (about 15 months). The sources are the broker's forum only | [Alpaca forum (from 2016)](https://forum.alpaca.markets/t/alpaca-data-api-does-not-have-data-earlier-than-2016/2332); [Alpaca forum (SIP 2016, IEX 2020)](https://forum.alpaca.markets/t/cannot-get-historical-bar-data-before-2020/12415) | D: whether G1's 2,400 out-of-sample days fit, or longer history must be bought |
| 21 | The free plan carries IEX only, about 2.5% of volume | 618 | **Partly right (F-7).** IEX-only is confirmed, but IEX's share in 2026 is 3.6–4.4% | [Alpaca docs (2.5%)](https://alpaca.markets/docs/stock-pricing-api); [Rosenblatt Jul 2026 (4.43%)](https://www.rblt.com/market-structure-reports/us-securities-volumes-july-2026); [Rosenblatt Feb 2026 (3.89%)](https://www.rblt.com/market-structure-reports/us-securities-volumes-february-2026); [IEX via Markets Media](https://www.marketsmedia.com/outlook-2026-bryan-harkins-iex-group/) | D: the data plan (unchanged) |
| 22 | The free plan streams 30 symbols at a time | 618–619 | **Confirmed** in Alpaca's versioned docs only; the current overview page doesn't restate it | [Alpaca docs v1.4.2](https://docs.alpaca.markets/us/v1.4.2/docs/about-market-data-api); [Alpaca real-time docs](https://alpaca.markets/deprecated/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/real-time) | D: the data plan |
| 23 | Alpaca cancels nothing when a client disconnects | 471, 570; C6 | **Not verifiable here.** No source describes a cancel-on-disconnect feature, and the documented tools (cancel all, liquidate) are calls the client makes. No source states the claim outright | [Alpaca blog (cancel all, liquidate)](https://alpaca.markets/blog/position-liquidation-cancel-orders/); [Alpaca forum](https://forum.alpaca.markets/t/cancellation-of-limiti-orders-and-disconnection/171) | D: C6's independent kill path. The goal already assumes the worse case |
| 24 | Alpaca's stop orders stay live at the broker if the system dies | 570–571; KR2.5 | **Confirmed, with caveats (O-2).** Live stops go to Alpaca's execution partners. Only GTC stops outlast the day, and bracket stop legs wait for a complete fill. The sources are the broker's forum only | [Staff answer (stops at execution partners)](https://forum.alpaca.markets/t/how-alpaca-handle-implemented-stop-price-functionality-in-stop-limit-order/5115); [GTC legs](https://forum.alpaca.markets/t/bracket-orders-and-take-profit-stop-loss-price/14375); [partial fills](https://forum.alpaca.markets/t/supported-protective-stop-workflow-for-a-partially-filled-day-entry-order/19417) | D: the KR2.5 design |
| 25 | Alpaca's margin multiplier can be set lower | 471 (C6) | **Confirmed.** The `max_margin_multiplier` setting takes "1", "2" or "4" | [Alpaca changelog 2026-07-07](https://docs.alpaca.markets/us/changelog/2026-07-07-admin-configurations-ad3805b); [py-alpaca-api](https://py-alpaca-api.readthedocs.io/en/stable/api/py_alpaca_api/models/account_config_model/index.html) | D: C6's broker-side cap on a runaway |
| 26 | A paper account starts with $100,000 of equity | 151; `starting_equity_usd` | **Confirmed** by the broker's forum only (staff and users) | [Alpaca forum](https://forum.alpaca.markets/t/paper-trading-balance/17970); [Alpaca forum](https://forum.alpaca.markets/t/paper-account-goes-from-100k-to-0-overnight-no-transactions/18410) | D: the starting equity, which the goal confirms on day one |
| 27 | RTS 6 Article 16(5) requires alerts within 5 seconds and remedial action as soon as possible | 472, 568; C7 `deviations` | **Confirmed** on the UK-retained text; the EU text was not retrieved | [legislation.gov.uk, Art. 16](https://www.legislation.gov.uk/eur/2017/589/article/16/data.htm); [Eventus](https://www.eventus.com/algo-monitoring/) | D: the deviation C7 states |
| 28 | Knight Capital lost about $460 million in 45 minutes in 2012, after 97 automated emails no one acted on | 569–570 | **Confirmed.** The SEC says "more than $460 million" and over 4 million orders in 45 minutes. The 97 emails came before the open and were not acted on | [SEC 2013-222](https://www.sec.gov/news/press-release/2013-222); [SEC digest 16 Oct 2013](https://www.sec.gov/news/digest/2013/dig101613.htm); [WilmerHale](https://www.wilmerhale.com/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million) | D: decision 7 |
| 29 | The overnight session's (20:00–04:00) main venue cancelled every trade in one stretch on 5 Aug 2024 | 575–576 | **Confirmed.** Blue Ocean cancelled all trades from 01:45 to 03:06 ET (brokers said 01:45 to 04:00) and suspended trading | [Markets Media](https://www.marketsmedia.com/blue-ocean-ats-resumes-after-cancelling-trades); [BNN Bloomberg](https://www.bnnbloomberg.ca/investing/2024/08/06/biggest-overnight-stock-venue-suspends-trading-after-volatility/) | D: decision 8 |
| 30 | The exchanges' own overnight sessions are planned from 6 Dec 2026 | 576–577 | **Confirmed.** On 26 Jun 2026 the SEC approved the SIP changes with a 6 Dec 2026 start. Nasdaq's 23/5 plan was approved on 10 Apr 2026, and Cboe aims for December | [Waters Technology](https://www.waterstechnology.com/data-management/7953016/equity-data-plans-eye-dec-6-for-overnight-trading-launch); [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260929-23x5-trading-comes-to-us-exchanges-what-firms-should-know-before-launch); [Sidley](https://www.sidley.com/en/insights/newsupdates/2026/09/sec-roundtable-highlights-key-considerations-for-24-hour-trading); [Cboe](https://ir.cboe.com/news/news-details/2026/Cboe-Files-Proposal-with-the-SEC-to-Launch-Near-24x5-U-S--Equities-Trading/default.aspx) | D: decision 8 |
| 31 | Prices reprice within milliseconds of a release | 573; also 300, 533 | **Confirmed.** SPY and E-mini futures react to macro surprises within about 5 ms | [Chordia, Green & Kottimukkalur 2018](https://ideas.repec.org/a/oup/rfinst/v31y2018i12p4650-4687..html); [Scinapse](https://www.scinapse.io/papers/2767247404) | D: decisions 3 and 8 |
| 32 | Language-model trading agents lost about half or more of their Sharpe ratio after their training cutoff (2025) | 581 | **Confirmed as worded.** In Profit Mirage (Oct 2025) the best agent's performance drops by about half, and a 2026 paper cites QuantAgent's Sharpe falling 51.5%. The "62%" in the brief was not found | [Profit Mirage](https://arxiv.org/pdf/2510.07920); [The Alpha Illusion](https://www.alphaxiv.org/abs/2605.16895); [McCombs commentary](https://news.mccombs.utexas.edu/research/keeping-humans-in-the-loop/) | D: decision 9 and KR6.3 |
| 33 | A GPT-4 news signal fell from Sharpe 6.5 to 1.2 between late 2021 and 2024, cited as a sign that an edge fades after the cutoff | 581–582 | **Partly right (F-8).** The path 6.54 (2021Q4), 3.68, 2.33, 1.22 (Jan–May 2024) is confirmed, but all of it falls after GPT-4's cutoff, and the authors tie the fall to adoption | [arXiv 2304.07619 v6](https://arxiv.org/html/2304.07619v6); [JFE version](https://www.sciencedirect.com/science/article/abs/pii/S0304405X26001066) | D: decision 9 |
| 34 | Hiding names and dates helps only partly | 583 | **Confirmed in substance.** Anonymizing headlines changed GPT's results, and look-ahead persists without names | [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322); [Detecting Lookahead Bias](https://huggingface.co/papers/2512.23847) | D: decision 9 |
| 35 | Telling a model not to use hindsight doesn't work | 583–584 | **Confirmed.** Models used future values even when instructed to ignore them | [Federal Reserve FEDS 2025-044](https://www.federalreserve.gov/econres/feds/files/2025044pap.pdf); [ABFER 2026 discussion](https://abfer.org/media/abfer-events-2026/annual-conference/slides-tech-ai/260518-AI-A-Test-of-Lookahead-Bias-in-LLM-Forecasts-disc.pdf) | D: decision 9 |
| 36 | Vendors' stated training cutoffs can be off by months | 584 | **Confirmed.** Effective cutoffs often differ drastically from the reported ones | [Dated Data (COLM 2024)](https://arxiv.org/html/2403.12958v2); [Ai2 summary](https://allenai.org/olmo-testimonial-tracing-knowledge-cutoffs) | D: KR6.3's cutoff audit |
| 37 | SPOT (2025): the best model found only 21% of the real errors in published papers | 555–556 | **Confirmed.** o3 reached 21.1% recall and 6.1% precision on 91 errors in 83 papers | [SPOT](https://arxiv.org/pdf/2505.11855); [Hugging Face](https://huggingface.co/papers/2505.11855); [Google paper citing SPOT](https://arxiv.org/pdf/2606.28277) | D: decision 6 and KR6.5 |
| 38 | Panels from different model families are less biased (Verga et al., 2024) | 556–557 | **Confirmed.** A panel of smaller models from disjoint families beat a single large judge, with less self-bias | [arXiv 2404.18796](https://arxiv.org/abs/2404.18796v2); [Cohere](https://cohere.com/research/papers/replacing-judges-with-juries-evaluating-llm-generations-with-a-panel-of-diverse-models-2024-04-29) | D: decision 6 and KR6.2 |
| 39 | AI reviewers agree with experts about as often as experts agree with each other | 554–555 | **Confirmed.** On Nature journals, GPT-4's overlap with human reviewers was 30.9%, against 28.6% between two humans | [Liang et al.](https://arxiv.org/abs/2310.01783v1); [2 Minute Medicine](https://www.2minutemedicine.com/large-language-models-show-potential-to-provide-feedback-on-research-papers-on-a-large-scale/) | D: decision 6 |
| 40 | Models favor their own outputs, and their errors are correlated, more so within one developer | 553–554 | **Confirmed** | [Panickssery et al., NeurIPS 2024](https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html); [Kim et al., ICML 2025](https://proceedings.mlr.press/v267/kim25e.html) | D: decision 6 |
| 41 | Gârleanu and Pedersen (2013): trade toward an aim portfolio, weighting each signal by its decay | 280, 520–521 | **Confirmed** | [NBER w15205](https://www.nber.org/papers/w15205); [accepted manuscript](https://research-api.cbs.dk/ws/portalfiles/portal/60191441/lasse_heje_pedersen_et_al_dynamic_trading_acceptedmanuscript.pdf) | D: decision 2 (rotation) |
| 42 | Constantinides (1986) and Davis and Norman (1990): proportional costs give a no-trade band | 280, 522–523 | **Confirmed** | [Transaction-costs user's guide](https://arxiv.org/pdf/1207.7330); [Cambridge reference](https://www.cambridge.org/core/product/A571DCCBABD9748D6A4E0B819666D6CC) | D: decision 2 |
| 43 | Novy-Marx and Velikov (2016): a buy/hold band is the most effective simple way to cut costs | 524–525 | **Confirmed** | [NBER w20721](https://www.nber.org/papers/w20721); [Alpha Architect](https://alphaarchitect.com/2017/05/trading-costs-destroy-factor-investing/) | D: decision 2 |
| 44 | Odean (1999): investors' own switches lost money even before costs | 281, 525–526 | **Confirmed.** The stocks investors bought underperformed the ones they sold | [Odean, AER 1999](https://econweb.ucsd.edu/~jandreon/Econ264/papers/Odean%20AER%201999.pdf); [Odean's research page](https://faculty.haas.berkeley.edu/odean/behavior.html) | D: decision 2 |
| 45 | The highest of 1,000 to 2,000 forecasts is inflated by about three standard deviations | 271, 526–527 | **Confirmed by computation.** The expected maximum is 3.24 for 1,000 draws and 3.43 for 2,000 | computed | D: KR3.7 calibration |
| 46 | Lou, Polk and Skouras (2019): the effects that survive costs span days and accrue partly overnight | 301–302, 534–536 | **Partly right (F-9).** The paper splits anomaly returns into overnight and intraday parts; it says nothing about costs | [LSE eprint](https://eprints.lse.ac.uk/87481/); [paper](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf); [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/) | D: decision 3 |
| 47 | Intraday momentum earned about 2.6 to 5 bps a trade before costs | 301, 534 | **Not verifiable here.** The 2.6 bps matches Gao et al. (6.3–6.7% a year from one trade a day), but no source for 5 bps was found | [CXO Advisory](https://cxoadvisory.com/calendar-effects/first-and-last-half-hours-of-trading-linked); [Alpha Architect](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/) | D: decision 3 |
| 48 | Information-coefficient rule of thumb: 0.05 good and 0.10 great (Grinold and Kahn); 0.10 "very good" (MSCI Barra); above 0.15 rarely sustained | 285–287 | **Partly right (F-10).** MSCI Barra's wording is confirmed. The only Grinold–Kahn citation found uses different labels | [MSCI Barra](https://www.msci.com/documents/10199/1645561/PI_Converting_Scores_Into_Alphas.pdf/7adf1f42-10aa-40eb-9e8c-ecc11eeba2d4); [M6 paper](https://arxiv.org/pdf/2310.13357) | D: the IC table in decision 3 (thresholds unchanged) |
| 49 | The 475(f) election is due by the original due date of the previous year's return (15 April 2027 for 2027) | 601–603 | **Confirmed** (Rev. Proc. 99-17) | [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [Rev. Proc. 99-17](https://webharvest.gov/peth04/20041017131721/http:/www.irs.gov/pub/irs-drop/rp-99-17.pdf); [Current Federal Tax Developments](https://www.currentfederaltaxdevelopments.com/blog/2020/3/6/irs-not-willing-to-grant-relief-to-taxpayer-who-attempted-to-make-a-late-475f-election) | D: decision 10 |
| 50 | `goal.toml`: the 475(f) election "must be made before the tax year it applies to" | G3 `entry_conditions` | **Contradicted (F-11)** | as row 49 | D: the wording of a G3 entry condition |
| 51 | The 475(f) election removes wash sales and the $3,000 loss cap | 601 | **Confirmed** | [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [Journal of Accountancy](https://www.journalofaccountancy.com/issues/2022/jun/tax-advice-clients-day-trade-stocks/) | D: decision 10 |
| 52 | Revoking 475(f) within 5 years needs the IRS's consent | 603 | **Not verifiable here.** Since 2015 a revocation can be filed automatically by statement. One practitioner says revoking within five years needs consent (Rev. Proc. 2025-23); another puts the five-year bar on re-electing | [TS CPA](https://tscpatax.com/glossary/section-475-election); [Kaufman Rossin](https://kaufmanrossin.com/blog/irs-makes-it-easier-for-hedge-fund-traders-to-revoke-section-475f-election/) | D: decision 10 (left to the adviser) |
| 53 | Trader status is a facts-and-circumstances test, and short-term gains are ordinary income | 598–601 | **Confirmed** | [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [IRS Topic 409](https://www.irs.gov/taxtopics/tc409); [Journal of Accountancy](https://www.journalofaccountancy.com/issues/2022/jun/tax-advice-clients-day-trade-stocks/) | D: decision 10 |
| 54 | The wash-sale rule spans all accounts and IRAs, while the broker applies it only within one account | 598–600; G3 `entry_conditions` | **Confirmed.** Rev. Rul. 2008-5 covers IRAs; brokers report only same-account, same-CUSIP matches | [Kitces](https://www.kitces.com/blog/irs-shuts-down-wash-sale-evasion-technique/); [The Tax Adviser](https://www.thetaxadviser.com/issues/2012/mar/casestudy-mar2012.html); [KPMG](https://kpmg.com/kpmg-us/content/dam/kpmg/taxnewsflash/pdf/2022/07/22208.pdf) | D: decision 10 |
| 55 | IRC 263(h): payments for dividends on shorts held 45 days or less are added to cost | 600–601 | **Confirmed.** The period is one year for extraordinary dividends | [26 USC 263](https://www.law.cornell.edu/uscode/text/26/263); [Marcum](https://marcumllp.com/insights/tax-consequences-of-short-selling-stock) | D: decision 10 |
| 56 | IRC 871(a)(2): a non-resident's US capital gains are taxed only after 183 days in the US | 604–605 | **Confirmed.** The tax is 30% of net US-source gains | [26 USC 871](https://www.law.cornell.edu/uscode/text/26/871); [IRS information letter](https://www.stayexempt.irs.gov/pub/irs-wd/16-0025.pdf); [The Tax Adviser](https://www.thetaxadviser.com/issues/2017/apr/planning-nonresident-entering-us-tax-system/) | D: decision 10 |
| 57 | Dividends are withheld at 30% or the treaty rate (form W-8BEN) | 605 | **Confirmed** | [IRS W-8BEN instructions](https://www.irs.gov/pub/irs-pdf/iw8ben.pdf); [Interactive Brokers](https://ibkb.interactivebrokers.com/node/938) | D: decision 10 |
| 58 | A non-resident's US stocks above $60,000 are exposed to US estate tax | 605–606 | **Confirmed.** The exemption comes from a $13,000 credit, and treaties can change it | [Taxes for Expats](https://www.taxesforexpats.com/articles/non-us-citizens/nonresident-alien-estate-tax-exemption-us-situs-assets.html); [Private Law wiki](https://wiki.private.law/en/us-estate-tax) | D: decision 10 |
| 59 | SR 26-2 replaced SR 11-7 on 17 April 2026, issued by the Fed, OCC and FDIC (OCC Bulletin 2026-13) | 461 | **Confirmed.** It also supersedes SR 21-8, and OCC Bulletin 2026-13 rescinds OCC 2011-12 | [Fed SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/sr2602.htm); [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html); [Sia Partners](https://www.sia-partners.com/en/insights/publications/sr-11-7-vs-sr-26-2-model-risk-management-modernization) | Cit: the model-risk checklist |
| 60 | The controls cover MiFID II's record and clock rules with one stated deviation (the alert time), while C14 keeps the clock within 50 ms | 460–462, 479 | **Contradicted (F-12).** RTS 25 allows 1 ms for algorithmic trading and 100 µs for high-frequency trading; 50 ms is the US audit-trail standard | [Timebeat](https://timebeat.app/blog/mifid-ii-finra-clock-sync); [Meinberg](https://blog.meinbergglobal.com/2016/07/26/mifid-ii-faq-meinberg); [GARP](https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054xFiUAI.pdf) | Cit: the deviation statement (C14 can stay) |
| 61 | SEC Rule 15c3-5, FINRA Notice 15-09 and the Knight Capital order set what's expected of an algorithmic trader | 460–461 | **Confirmed** | [FINRA RN 15-09](https://www.finra.org/rules-guidance/notices/15-09); [Skadden](https://www.skadden.com/-/media/files/publications/2015/05/finraprovidesguidanceoneffectivesupervisionandcont.pdf); [SEC 2013-222](https://www.sec.gov/news/press-release/2013-222) | Cit |
| 62 | FINRA fined Alpaca $300,000 in March 2026 for late trade reporting | 609–610 | **Confirmed** in amount and cause: 1.87 million late reports from 2021 to 2025, plus inaccurate reports and supervision failures. The month was not found | [FX News Group](https://fxnewsgroup.com/?p=39754); [FINRA AWC listing](https://finra.org/node?page=11) | Cit |
| 63 | Harvey, Liu and Zhu: a new factor needs t > 3 | not cited in either file | **Confirmed** (RFS 2016) | [NBER w20592](https://www.nber.org/papers/w20592); [SSRN](https://papers.ssrn.com/abstract=2513152) | Cit. Nothing changes, since the goal uses the Deflated Sharpe Ratio |
| 64 | "The one fund limit the research found caps a single position at 5%" | 513–514 | **Not verifiable here.** The fund limit isn't named | — | Cit (decision 1) |

## Findings

All twelve findings are minor. Ten are partly right and two are contradicted. They are ordered as in
the table.

### F-1 (minor): Yahoo rose 48% on 1 February 2008, not 49.5%

- **Where:** `GOAL.md` lines 38 and 168; the comment on `jump_overnight_pct` in `goal.toml`
  (line 91).
- **Sources:**
  - Yahoo closed at $19.18 on 31 January 2008 (Microsoft's offer, SEC Form 425).
  - It closed at $28.38 on 1 February, a rise of 48.0% (Felix Salmon; CNNMoney: "ended the day 48%
    higher").
  - AP reported +49% ($28.59) in morning trading, and pre-market reports had +56% ($29.95).
  - No source gives +49.5%, which would need an opening price of $28.67.
- **Correction:** write "Yahoo, +48% on a takeover bid (1 February 2008; about +49% in morning
  trading)". If +49.5% is the opening gap in the project's own data, call it an opening gap and cite
  that data.
- **Limits:** the 50% overnight jump still covers the regular-session move. The pre-market high
  doesn't matter while the system's orders act only in the regular session.

### F-2 (minor): NVIDIA fell 31% on 3 July 2008, not 28.0%

- **Where:** line 168.
- **Sources:**
  - After hours on 2 July the stock fell 21.9% to $14.08, from a $18.03 close (The Register).
  - On 3 July it closed at $12.49, down 30.7% (HEXUS). Fortune reported "down 31%" and Motley Fool
    "more than 30%".
  - −28.0% would need an open near $12.98, and no source gives one.
- **Correction:** write "NVIDIA's −31% warning gap (2008)", or label −28.0% as the opening gap from
  the project's own data.
- **Limits:** no change.

### F-3 (minor): 13 March 2023 was not a 50% industry-wide jump

- **Where:** line 172, the overnight industry limit.
- **Sources:** First Republic fell 61.8% that day. The SPDR S&P Regional Banking ETF fell 12.3%, its
  worst day since March 2020, and at least a dozen bank stocks were halted (S&P Global; Motley
  Fool).
- **Correction:** write "a 50% jump in an industry book concentrated in a few names costs 4%
  (13 March 2023: First Republic −62%, while the regional-bank ETF fell 12%)".
- **Limits:** the 8% limit can stay, since it is conservative for an industry average. Note that the
  worst single name fell more than the 50% the goal assumes for a stock. The 2% event-prone cap
  protects a bank long only if the bank or its industry had already fallen 20% over the previous
  five days.

### F-4 (minor): the price bands are 5% for most of this universe

- **Where:** line 167; the comment on `jump_intraday_pct` in `goal.toml` (line 92).
- **Sources:**
  - Limit-up/limit-down bands are 5% for Tier 1 securities above $3 (the S&P 500, the Russell 1000
    and many ETPs) and 10% for Tier 2 securities above $3.
  - Bands double in the opening period, and for Tier 1 also at the close (LULD Plan; SEC 34-101036).
  - A pause or a news halt doesn't bound the price at which trading reopens.
  - A universe of $20 million a day and spreads of 10 bps or less is mostly Tier 1.
- **Correction:** write "a jump of 20% within the session (a news halt, whose reopening no band
  bounds, or four Tier 1 or two Tier 2 price bands)".
- **Limits:** the 20% assumption can stay.

### F-5 (minor): FINRA's trading activity fee is paused for the rest of 2026

- **Where:** line 213, the cost model.
- **Sources:**
  - The 2026 rate is $0.000195 a share, with a $9.79 cap (Investrade; Brokerage-Review).
  - FINRA's SR-FINRA-2026-021 took effect on filing in September 2026. It pauses the fee for trades
    from 1 October to 31 December 2026, and the fee resumes on 1 January 2027.
- **Correction:** add "(paused for trades from 1 October to 31 December 2026)".
- **Costs:** keeping the charge is conservative and immaterial, about 0.04 bps on a $4,000 sale of
  80 shares.

### F-6 (minor): "3 to 4 times the spread" is a 1999–2000 figure

- **Where:** lines 89 and 573–574 (decision 8).
- **Sources:**
  - Barclay and Hendershott (Journal of Finance, 2004) found after-hours quoted and effective
    spreads 3 to 4 times the day's, on 1999–2000 data.
  - A recent study reported by Nasdaq found overnight quoted spreads 40% to 144% wider, depending on
    the set of stocks.
  - Around earnings, spreads are about 7 times wider (58.1 against 8.4 bps; arXiv 2601.08962).
- **Correction:** write "after-hours spreads have been measured at about 1.4 to 4 times the
  session's, and far wider right after news".
- **Decision 8:** stands.

### F-7 (minor): IEX's share of volume is now about 4%

- **Where:** line 618.
- **Sources:** Alpaca's pages still say about 2.5%. Rosenblatt's monthly reports put IEX at 3.57%
  (January 2026), 3.89% (February), 3.97% (May) and 4.43% (July) of consolidated volume, and IEX
  said about 4% for the second quarter of 2026.
- **Correction:** write "IEX, about 4% of volume".
- **Data plan:** the decision is unchanged.

### F-8 (minor): the GPT-4 signal's decline is not a training-cutoff effect

- **Where:** lines 581–582 (decision 9).
- **Sources:**
  - Lopez-Lira and Tang report the GPT-4 strategy's annualized Sharpe ratio at 6.54 in 2021Q4, 3.68
    in 2022, 2.33 in 2023 and 1.22 over January–May 2024.
  - The whole test period lies after GPT-4's training data end (September 2021, per OpenAI's GPT-4
    technical report; not re-checked here).
  - The authors link the decline to models growing more capable and more widely adopted (arXiv v6;
    Journal of Financial Economics version).
- **Correction:** write "and a GPT-4 news signal, tested entirely after its training cutoff, lost
  most of its edge as such models spread: a Sharpe of 6.5 in late 2021, 1.2 in early 2024".
- **Decision 9:** it still rests on the trading-agent study, the Fed's instruction test and the
  cutoff study (rows 32, 35 and 36).

### F-9 (minor): Lou, Polk and Skouras is about overnight versus intraday returns, not costs

- **Where:** lines 301–302 and 534–536.
- **Sources:** the paper (JFE 2019) decomposes 14 anomaly strategies. Momentum and reversal profits
  accrue almost entirely overnight; most other strategies' profits accrue intraday, often with the
  opposite sign overnight. It doesn't study which effects survive costs, nor holds of a few days.
- **Correction:** write "anomaly profits split between overnight and intraday: momentum's accrue
  overnight, most others' intraday (Lou, Polk and Skouras, 2019)". Cite Novy-Marx and Velikov (2016)
  for which effects survive costs.

### F-10 (minor): the Grinold–Kahn labels are not confirmed

- **Where:** lines 285–287.
- **Sources:**
  - MSCI Barra says many managers see an information coefficient of 0.05 as "good" and 0.10 as
    "very good" (confirmed).
  - The only source found that cites Grinold and Kahn for labels, the M6 competition paper, calls
    0.05 moderate, 0.10 good and 0.15 exceptional.
  - Grinold and Kahn's own wording was not found.
- **Correction:** write "practitioners call an information coefficient of 0.05 good and 0.10 very
  good (MSCI Barra); 0.15 is exceptional", or check the book before keeping the attribution.
- **Decision 3:** the thresholds, and so the IC table, are unchanged.

### F-11 (minor, contradicted): `goal.toml` misstates the 475(f) deadline

- **Where:** `goal.toml`, G3 `[gates.rule]`, `entry_conditions` (line 910).
- **Sources:** under Rev. Proc. 99-17, a taxpayer files the election statement by the original due
  date, without extensions, of the previous year's return. That is 15 April of the year the election
  applies to, so the deadline falls inside that year (IRS Topic 429; Rev. Proc. 99-17; IRS rulings
  refusing late elections). `GOAL.md` lines 601–603 say this correctly.
- **Correction:** replace "which must be made before the tax year it applies to" with "which must be
  made by the original due date of the previous year's return (15 April of the year it applies
  to)".
- **Consistency:** the two files disagree on this point today.

### F-12 (minor, contradicted): the clock tolerance is a second, unstated deviation

- **Where:** lines 460–462 and C14 (line 479).
- **Sources:** MiFID II's RTS 25 limits divergence from UTC to 1 millisecond for algorithmic trading
  that isn't high-frequency, and to 100 microseconds for high-frequency trading. 50 ms is the
  tolerance of the US consolidated audit trail for broker-dealers (Timebeat; Meinberg; GARP).
- **Correction:** in the Controls preamble, state two deviations: "the alert time (C7) and the clock
  tolerance (C14 follows the US audit trail's 50 ms, not RTS 25's 1 ms)". Alternatively, drop
  "clock" from the claim that the controls cover MiFID II.
- **Limits:** C14's 50 ms can stay, since the system is not subject to MiFID II. MiFID II's
  five-year record retention matches C5.

## Observations on confirmed claims

None of these contradicts the goal. Each is a caveat that bears on a limit, a control or a later
check.

- **O-1. The jump sizes are not ceilings.**
  - First Republic fell 61.8% on 13 March 2023, more than the 50% assumed for a stock.
  - Provention Bio more than tripled on 13 March 2023 (Sanofi's $25 bid, 273% over a $6.70 close),
    and CinCor rose 135% pre-market on 9 January 2023. Both exceed the 100% assumed for a biotech
    short. A 2% short through +273% would lose 5.5%, beyond the 4% single-jump bound (KR2.8).
  - Both biotechs were small caps that the universe filters ($20 million a day, spreads of 10 bps or
    less) would probably exclude: a 1-cent tick on a $6.70 stock is 15 bps.
  - GT-2 could add a "tripling" case for an event-prone short in a name at the edge of the universe.
- **O-2. Alpaca's stops have three caveats** (the broker's forum and docs):
  - Live stops go to Alpaca's execution partners, so they survive a client crash. But only GTC
    stops outlast the day.
  - Bracket and OTO stop legs activate only once the entry is completely filled, so a partial fill
    can sit uncovered. KR2.5 ("partial fills included") needs a separate stop for each partial fill.
  - Fractional-share orders must be DAY orders, so a fractional position can't hold a GTC stop
    overnight. This supports the whole-share premise behind the G3 floor (10 shares of the
    median-priced stock).
- **O-3. SR 26-2 and OCC Bulletin 2026-13 put generative and agentic AI models outside their scope**
  (per the OCC bulletin as summarized by secondary sources). The goal's model-risk controls (C12)
  draw on guidance that doesn't cover its AI components, so KR6.2 and KR6.3 carry that load alone.
- **O-4. Two fees will change.** The SEC will reset the Section 31 rate 60 days after the FY2027
  appropriation is enacted, and FINRA's fee resumes on 1 January 2027. Re-check both before G2.
- **O-5. Gaps in Alpaca's history.** IEX-feed history starts in 2020; only the consolidated feed
  goes back to 2016. Whether that history includes delisted stocks was not established here, and
  the goal already asks for it to be confirmed.
- **O-6. The $2,000 floor survives the new margin rule.** Under the intraday margin standard, the
  $2,000 minimum for margin and short accounts remains. Firms may phase the standard in until
  20 October 2027, and Alpaca applied it on 4 June 2026.
- **O-7. The overnight-trading dates are approved targets.** The SIPs start on 6 December 2026, and
  the 24X exchange has conditional relief to start on 24 January 2027. Decision 8's planned review
  after G2 should use the first months of exchange overnight data.
- **O-8. Knight's loss.** Knight's own first estimate was $440 million before tax. The SEC's "more
  than $460 million", which the goal uses, is the better citation.
- **O-9. Harvey, Liu and Zhu.** The brief lists them, but neither goal file cites them. Their
  claim (t > 3) is confirmed. The goal's guard against multiple testing is the Deflated Sharpe
  Ratio.
- **O-10. The FINRA fine covered more than late reports.** The settlement also covered inaccurate
  reports (2.2 million missing modifiers and 6,700 wrong quantities) and supervision failures up to
  February 2026. "For late trade reporting" is incomplete.

## Not verifiable here, and internal figures

- **Not verifiable here:**
  - **Row 23.** That Alpaca cancels nothing on disconnect. It is consistent with every source, but
    no source states it. The goal already designs for the worse case.
  - **Row 47.** The upper end (5 bps) of the intraday-momentum range.
  - **Row 52.** The 475(f) revocation rule; the sources conflict, and the adviser should settle it.
  - **Row 64.** The unnamed single-fund 5% limit.
- **Internal figures, from the project's own data or tests, not external:**
  - "a stock moves about 19 bps in 5 minutes and 168 bps in a day" (line 283). These are internally
    consistent: 168 × √(5/390) = 19.0.
  - "published spreads and fees add up to 6.95 bps" (lines 92 and 220, GT-3).
  - "gaps of 20% or more away from earnings came about 1.3 times in 10,000 stock-nights" (line 513).

  These would need the underlying data and GT-3 to check, which this review did not read.

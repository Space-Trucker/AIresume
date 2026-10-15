# Edge horizon: minute-level holds vs holds of hours to days (small, non-colocated US-equity system)

*Method note (2026-10-15). WebFetch could not resolve any host in this session (sec.gov, finra.org, alpaca.markets, files.alpaca.markets, docs.alpaca.markets, arxiv, alphaarchitect.com, globaltrading.net all failed with DNS errors). The shell proxy also refused these hosts. The WebSearch budget shared by all agents ran out after about 30 searches. So every cited finding below comes from search-result extracts of abstracts, notices and pages, not from full texts I could read. Tags: **[2 sources]** means two independent sources agreed; **[same paper, 2 hosts]** means two copies of one primary source; **[single-source]** means only one source was found. Values marked "assumption" are inputs I chose for the arithmetic, not facts. I computed all break-even arithmetic locally in Python and show the inputs. Many specific numbers (2024-2026 quoted spreads by size, CAT fee rates, Alpaca latency, practitioner cost studies) could not be retrieved. They are listed under Gaps and were not filled from memory.*

## Overall question: which edge horizon should the plan assume?

### Takeaway
Plan the edge on holds of about **1 to 5 trading days, held overnight** (the plan's typical hold of 1,170 minutes, or 3 days, already fits this). Do not plan it on minutes, or mainly on intraday holds of 2.5 hours. The 150-minute basis is where the best-documented intraday effect, at a per-trade information ratio of about 0.068, **breaks even** at 8 bps. The plan's own **2x-cost entry rule** moves that same accuracy out to about 1.5 trading days, or about 3.5 days under the x1.5 cost stress.

Confidence:
- **High (~90%)** that minute-level holds cannot clear costs for this system.
- **Moderate (~70%)** that 1-5 days is the right planning horizon.
- **Low to moderate (~40-50%)** that any single published 1-5 day effect, after its documented decay, will by itself reach net Sharpe 1.0.

### Cited Findings
- The best-known intraday effect, SPY's first half-hour predicting its last half-hour, has an out-of-sample R² of 1.4% (in-sample 1.6%), sample 1993-2013. A timing strategy earned 6.67%/yr with a standard deviation of 6.19%/yr (Sharpe 1.08), before costs — [Gao-Han-Li-Zhou paper PDF](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf); [ResearchGate record, JFE 2018](https://www.researchgate.net/publication/325364670_Market_Intraday_Momentum). **[same paper, 2 hosts; magnitude corroborated by an independent summary, see Q1]**
- High-frequency predictability is "large, systematic and pervasive over short horizons". It sits in the most recent ~10 milliseconds or ~10 transactions, and it drops sharply once a small delay is introduced — [NBER w30366, Aït-Sahalia-Fan-Xue-Zhou 2022](https://www.nber.org/papers/w30366); [seminar summary](https://lists.dm.unipi.it/hyperkitty/list/random@lists.dm.unipi.it/thread/TGUUFLBMCV5CDK4PPZVXITGRA43XLZIW/). **[2 sources]**
- Intraday serial dependence driven by order imbalance takes more than 5 but less than 60 minutes to disappear — [CFA Institute digest of Chordia-Roll-Subrahmanyam 2005](https://rpc.cfainstitute.org/en/research/cfa-digest/2005/11/evidence-on-the-speed-of-convergence-to-market-efficiency-digest-summary). For large NYSE stocks it takes 5-15 minutes — [Chung & Hrazdil 2012, IDEAS](https://ideas.repec.org/a/eee/empfin/v19y2012i5p702-720.html). **[2 sources]**
- Latency-arbitrage races are decided by margins of 5-10 microseconds — [NBER w29011, Aquilina-Budish-O'Neill](https://www.nber.org/system/files/working_papers/w29011/w29011.pdf); [Harvard Law School Forum summary](https://corpgov.law.harvard.edu/2021/11/05/quantifying-the-high-frequency-trading-arms-race). HFT performance is ranked by relative latency — [Baron-Brogaard-Hagströmer-Kirilenko, JFQA 2019, IDEAS](https://ideas.repec.org/a/cup/jfinqa/v54y2019i03p993-1024_00.html). **[2 sources]**
- Weekly short-term reversal restricted to large caps earned 30-50 bps per week net of trading costs (sample ends before 2010) — [de Groot-Huij-Zhou 2012, IDEAS](https://ideas.repec.org/a/eee/jbfina/v36y2012i2p371-382.html); [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks). **[2 sources]**
- News-driven returns drift in the same direction for several days without reversal, and a strategy on this drift "remains profitable after transaction costs" — [Jiang-Li-Wang JFE 2021, SSRN](https://papers.ssrn.com/abstract=2679614); [IDEAS](https://ideas.repec.org/a/eee/jfinec/v141y2021i2p573-599.html). **[same paper, 2 hosts]**
- Momentum profits, and per the abstract wording reversal profits too, are earned overnight; most other anomalies are earned intraday, often with opposite signs — [Lou-Polk-Skouras JFE 2019, LSE](https://researchonline.lse.ac.uk/id/eprint/87481); [Alpha Architect summary](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/). **[2 sources]**
- Anomaly returns roughly halved after decimalization — [Chordia-Subrahmanyam-Tong 2014, SMU](https://ink.library.smu.edu.sg/lkcsb_research/4735). Predictor returns are 26% lower out of sample and 58% lower after publication — [McLean-Pontiff 2016 PDF](https://www.gwern.net/doc/economics/2016-mclean.pdf); [Ivey copy](https://ivey.uwo.ca/media/3775549/pontiff.pdf). **[2 sources each]**
- Alpaca paper trading fills market buys at the ask and sells at the bid, with no price improvement. It applies random partial fills to 10% of orders, does not check depth, and fills limit orders when price touches, with no queue — [Alpaca community forum, staff answer](https://forum.alpaca.markets/t/slippage-paper-trading-vs-real-trading/2801); [TradersPost blog](https://blog.traderspost.io/article/alpaca-paper-trading). **[2 sources; official doc page not retrieved]**

### Inferences
- **Recommendation.** Restate the planning basis roughly as follows: *"The plan expects its profit from holds of about one to five trading days, held overnight. Intraday holds, including those of 2.5 hours or more, are allowed but are not expected to clear the 2x-cost entry rule at 8 bps unless the instrument costs about 2 bps a round trip or less. Holds of seconds to minutes stay allowed for exits, risk control and execution, not as a source of edge. Intraday patterns are used to time the entries and exits of multi-day trades."*
- **Why 150 minutes is too short as a basis under the plan's own rule.** Assume a stock with 30% annualized volatility (an assumption), so σ ≈ 189 bps a day, scaled by √time. A per-trade IR of 0.068 (the Gao et al. timing strategy) breaks even (1x cost, 8 bps) at about 151 minutes. That matches the goal's 150 minutes, and the goal's REPORT.md quotes "an IC of 0.096 needed at 2.5 hours", which my arithmetic reproduces as the gross IR needed for net Sharpe 1.0 at 150 minutes. The 2x-cost entry rule needs the same IR to hold about 605 minutes (1.55 days), or 1,360 minutes (3.5 days) at the 12 bps stress cost. The 2x rule is consistent with a 150-minute floor only if the real cost is about 4 bps. Details are in Q3.
- **Evidence for 1-5 days:**
  1. The accuracy needed falls with √horizon. Under the 2x rule at 8 bps, per-trade IR is ~0.085 at 1 day (53.4% hit rate), ~0.05 at 3 days (51.9%) and ~0.04 at 5 days, against ~0.14 (55.4%) at 150 minutes and ~0.75 (77%) at 5 minutes.
  2. The documented after-cost successes are at daily-to-weekly horizons: large-cap weekly reversal and multi-day news drift.
  3. Several premia accrue overnight (Lou-Polk-Skouras), which intraday-only holds forgo.
  4. Minute-level predictability lives in milliseconds and belongs to colocated firms.
  5. Alpaca paper fills cannot validate minute-level strategies.
- **Evidence against, or caveats:**
  1. Decay. The contrarian daily return fell from ~1.38%/day (1995) to 0.13% (2006-07) per Khandani-Lo. Anomalies halved after decimalization. Returns fall 58% after publication. De Groot's net 30-50 bps/week predates 2010.
  2. Reversal is strongest in illiquid stocks, which the universe filters out (Avramov-Chordia-Goyal 2006).
  3. Under a 0.2% daily volatility target and ~25 round trips a week, longer holds mean more, smaller positions. So the needed net edge per trade in bps rises: ~8-14 bps net at 3 days and ~11-18 bps at 5 days, against ~3-5 bps at 150 minutes (Q3). The signal must persist for days.
  4. Overnight gap risk; short-borrow costs were not researched.
  5. Hour-level intraday edges in SPY appear to survive costs where costs are about 1 bp. Gao et al. gross ≈ 2.6-5 bps per trade, and Zarattini-Aziz-Barbon report net Sharpe 1.33 for 2007-2024 (single source). This supports a cheap-universe intraday sleeve, not minute-level holds.
  6. If Alpaca's live execution matches industry-median price improvement (median E/Q ~0.3), real costs in liquid names could be ~4-6 bps rather than 8. That would halve the intraday hurdles.
- **What would change the recommendation:** live measurement (not paper) of Alpaca round-trip cost of 3-4 bps or less in the traded names, or a cheap universe at 2 bps or less. Either would make a 150-minute-plus intraday sleeve credible as a secondary source, but would not make minute-level holds credible (Q4).
- **On the owner's alternative.** A cheaper-universe study is worth doing as a secondary track for intraday holds of 30 minutes to a few hours in index ETFs and mega-caps. It also cuts costs for the multi-day trades. It is not a way to rescue minute-level holds, given latency (Q4, Q5).

### Gaps
- No full texts were read (tool failures, see the method note). Effect sizes rest on abstracts and summaries.
- Post-2013 out-of-sample evidence for intraday momentum, apart from one practitioner working paper, and post-2010 evidence for weekly reversal in large caps were not retrieved. This is the largest uncertainty for both horizons.
- Alpaca's live execution quality (its Rule 605 report and E/Q) and API latency were not retrieved.

## Q1: Gross return per trade, after-cost profitability and decay of intraday effects vs 1-5 day effects

### Takeaway
The documented intraday effects are small per trade:
- Market intraday momentum gives ≈2.6-5 bps gross per trade, and only in SPY-like instruments.
- Intraday reversal is mostly bid-ask bounce and liquidity imbalances lasting under an hour.
- Order-imbalance predictability is gone within 5-60 minutes.
- Intraday periodicity is about the size of one effective spread.

None of these clears 8 bps, let alone the 16 bps entry hurdle, in a typical stock. The 1-5 day effects are larger per trade, and some are reported profitable after costs: weekly large-cap reversal at 30-50 bps/week net before 2010, and multi-day news drift. All of them have decayed, and reversal is weakest in the liquid names this system trades.

### Cited Findings
**Intraday momentum (Gao, Han, Li, Zhou 2018)**
- *Market Intraday Momentum*, Journal of Financial Economics 129 (2018) 394-414. SPY's first half-hour return, measured from the previous close, predicts its last half-hour return. Sample 1993-2013. In-sample R² 1.6%; out-of-sample R² 1.4% (2.0% when combined with the 12th half-hour return) — [paper PDF](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf); [ResearchGate](https://www.researchgate.net/publication/325364670_Market_Intraday_Momentum). **[same paper, 2 hosts]**
- The timing strategy on the sign of the first half-hour return earned 6.67%/yr with a standard deviation of 6.19%/yr, Sharpe 1.08, against 0.29 for daily buy-and-hold — [paper PDF](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf). An earlier version (1999-2012) is reported as out-of-sample R² ~1.8% and **6.3%/yr gross**, against -0.5%/yr for holding SPY in every last half-hour — [CXO Advisory](https://www.cxoadvisory.com/calendar-effects/first-and-last-half-hours-of-trading-linked/); [Alpha Architect](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/). **[2 sources; the published figures are before costs]**
- The effect is stronger on volatile, high-volume, recession and macro-news days. It is attributed to infrequent rebalancing (Bogousslavsky 2016) and late-informed trading — [WUSTL profile](https://profiles.wustl.edu/en/publications/market-intraday-momentum/); [CXO Advisory](https://www.cxoadvisory.com/calendar-effects/first-and-last-half-hours-of-trading-linked/). **[2 sources]**
- The US first half-hour return also predicts last-half-hour returns in other markets — [Li et al., Intraday Time Series Momentum: International Evidence (FoFI 2020)](http://wp.lancs.ac.uk/fofi2020/files/2020/04/FoFI-2020-092-Zeming-Li.pdf). **[single-source]**
- Zarattini, Aziz, Barbon, *Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)*, Swiss Finance Institute WP 24-97 (2024). It enters on early intraday supply/demand imbalance and uses dynamic trailing stops. Over 2007 to early 2024 it reports **Sharpe 1.33 net of commissions and slippage**. The cost assumptions were not retrieved, and a LinkedIn listing also cites "Sharpe 2.1, max drawdown 9.4%" without saying what they measure — [SFI](https://www.sfi.ch/fr/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy); [IDEAS](https://ideas.repec.org/p/chf/rpseri/rp2497.html). It took 4th place in the Quantpedia Awards 2025 — [FSI-HSG](https://fsi.unisg.ch/de/newsdetail/news/quantpedia-awards-2025-fsis-barbon-and-team-secure-4th-place-with-intraday-momentum-strategy/). **[single primary source; a working paper, not peer-reviewed]**

**Intraday periodicity and intraday reversal (Heston, Korajczyk, Sadka 2010)**
- Journal of Finance 65(4) 1369-1407. The authors split the day into 13 half-hours and used all NYSE trades for 2001-2005 (more than 16,000 intervals). Returns continue at lags that are exact multiples of a trading day, for at least 40 trading days. The effect is more pronounced in, but not limited to, the first and last half-hours — [Kellogg research page](https://www.kellogg.northwestern.edu/academics-research/research/detail/2010/intraday-patterns-in-the-cross-section-of-stock-returns); [arXiv/ar5iv version](https://ar5iv.arxiv.org/html/1005.3535). **[same paper, 2 hosts]** *(Old sample: 2001-2005.)*
- Short-term intraday reversal is attributed to "temporary liquidity imbalances lasting less than an hour and bid-ask bounce". Volume, order imbalance and volatility show similar patterns but do not explain the returns — [ar5iv](https://ar5iv.arxiv.org/html/1005.3535); [Kellogg Insight](https://insight.kellogg.northwestern.edu/article/picking_up_pennies_for_profit). **[same paper + press summary]**
- The authors say timing trades with these patterns can reduce execution costs "by the equivalent of the effective spread". The Kellogg article cautions that the findings are not a day-trading playbook for retail investors — [Kellogg Insight](https://insight.kellogg.northwestern.edu/article/picking_up_pennies_for_profit); [UH working paper](https://www.bauer.uh.edu/departments/finance/documents/Heston_Korajczyk_Sadka_paper_UH.pdf). **[2 hosts]**

**Order-flow imbalance and speed of adjustment**
- Chordia, Roll, Subrahmanyam (JFE 2005): intraday serial dependence from order imbalances lasts more than 5 and less than 60 minutes. Daily returns show no serial correlation despite persistent imbalances, because sophisticated traders counter imbalances within the day — [CFA digest](https://rpc.cfainstitute.org/en/research/cfa-digest/2005/11/evidence-on-the-speed-of-convergence-to-market-efficiency-digest-summary); [SUFE abstract](https://academicnewsletter.sufe.edu.cn/info/357606). **[2 sources]**
- Chung & Hrazdil (J. Empirical Finance 2012): price adjustment takes 5-15 minutes on average for large NYSE stocks, and about 20 minutes longer for small ones — [IDEAS](https://ideas.repec.org/a/eee/empfin/v19y2012i5p702-720.html). **[single-source]**
- Aït-Sahalia, Fan, Xue, Zhou (NBER w30366, 2022; Management Science): predictability sits in the last ~10 ms, 10 transactions or 10 lots, and drops sharply with small delays. For the median stock, out-of-sample R² is 10.5% for 5-second returns, with ~64% correct direction (seminar summary) — [NBER](https://www.nber.org/papers/w30366); [seminar summary](https://lists.dm.unipi.it/hyperkitty/list/random@lists.dm.unipi.it/thread/TGUUFLBMCV5CDK4PPZVXITGRA43XLZIW/). A truncated database snippet says predictability falls to about zero after roughly 5 minutes — [causalclaims entry](https://causalclaims.trfetzer.com/paper/w30366.html). **[R² single-source; the 5-minute figure is unverified]** The author lists differ between the NBER version (Zhou) and the Management Science supplement (Zhu) — [INFORMS supplement](https://pubsonline.informs.org/doi/suppl/10.1287/mnsc.2022.02435).

**1-5 day effects**
- de Groot, Huij, Zhou (J. Banking & Finance 36(2), 2012, 371-382): most of the erosion of reversal profits by costs comes from trading small caps. Restricting to large caps and building cost-aware portfolios with lower turnover leaves **30-50 bps per week net of trading costs** — [IDEAS](https://ideas.repec.org/a/eee/jbfina/v36y2012i2p371-382.html); [EUR repository](https://repub.eur.nl/pub/25718); [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks). **[2 sources]** A CXO summary of a 1990-2009 sample reports that reversal underperformed after costs except among the largest stocks. It may or may not be this paper — [CXO Advisory](https://www.cxoadvisory.com/?p=6251).
- Avramov, Chordia, Goyal (JF 61(5), 2006, 2365-2394): reversals are strongest in high-turnover, **low-liquidity** stocks, as price pressure from non-informational demand for immediacy is absorbed. Contrarian profits are smaller than likely trading costs. The violation of market efficiency "is not so egregious after all" — [IDEAS](https://ideas.repec.org/a/bla/jfinan/v61y2006i5p2365-2394.html); [HUJI record](https://cris.huji.ac.il/en/publications/liquidity-and-autocorrelations-in-individual-stock-returns/). Reversals occur mainly in losers — [NBER 2004 draft](https://users.nber.org/~confer/2004/mmsu04/goyal.pdf). **[2 hosts]**
- Khandani & Lo (*What Happened to the Quants in August 2007?*): a daily contrarian strategy's average daily return fell as assets in the category grew, to a low of **0.13%/day in 2006** — [NBER w14465](https://nber.org/system/files/working_papers/w14465/w14465.pdf); [QuantNet abstract copy](https://quantnet.com/threads/what-happened-to-the-quants-in-august-2007.834/latest). A secondary summary gives **1.38%/day in 1995 falling to 0.13% by 2007**, with daily volatility rising from 0.40% to 0.72% — [summary](https://brunch.co.kr/@@70EQ/22). **[2 sources; endpoint year 2006 vs 2007 differs; gross of costs; old data]**
- Jiang, Li, Wang (JFE 141, 2021, 573-599), using high-frequency data: news-driven returns drift for several days without reversal. A strategy on this drift earns high abnormal returns and "remains profitable after transaction costs". The drift is stronger when investors are distracted — [SSRN](https://papers.ssrn.com/abstract=2679614); [IDEAS](https://ideas.repec.org/a/eee/jfinec/v141y2021i2p573-599.html). In the 2018 draft, non-news returns tend to reverse — [2018 draft](https://www1.villanova.edu/dam/villanova/VSB/assets/marc/marc2018/SSRN-id2667658.pdf). **[same paper, several hosts; magnitudes not retrieved]**

**Overnight vs intraday**
- Lou, Polk, Skouras (JFE 134, 2019, 192-213): "Profits are either earned entirely overnight (for reversal and a variety of momentum strategies) or entirely intraday, typically with profits of opposite signs." The patterns are stronger for large-cap and high-price stocks. Conditional variation in the overnight-minus-intraday spread is about 2% a month — [LSE Research Online](https://researchonline.lse.ac.uk/id/eprint/87481); [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/). **[2 sources; the "reversal overnight" wording is from the abstract extract, full text not checked]**
- Alpha Architect cites Cliff, Cooper and Gulen as showing that all stock returns come from holding overnight risk. Its in-house backtests did not support a related intraday-momentum result — [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/). **[single-source, secondary]**

**Decay**
- Chordia, Subrahmanyam, Tong (J. Accounting & Economics 58(1), 2014, 41-58): most anomalies attenuated, and returns from a portfolio of prominent anomalies roughly halved after decimalization. They tie this to hedge fund assets, short interest and turnover — [SMU](https://ink.library.smu.edu.sg/lkcsb_research/4735); [Emory summary](https://goizueta.emory.edu/research-spotlight/increased-trading-activity-and-declining-returns). **[2 sources]** Partly contradicted by Auer & Rottmann (CESifo WP 7204, 2018): across 21 developed markets they find the US result not fully robust and no persuasive link between liquidity and anomaly decline — [CESifo](https://www.cesifo.org/en/publications/2018/working-paper/have-capital-market-anomalies-worldwide-attenuated-recent-era-high).
- McLean & Pontiff (JF 2016), 97 predictors: returns are 26% lower out of sample and 58% lower after publication. Declines are larger for predictors with higher in-sample returns — [PDF](https://www.gwern.net/doc/economics/2016-mclean.pdf); [Ivey](https://ivey.uwo.ca/media/3775549/pontiff.pdf); [Hedge Fund Alpha](https://hedgefundalpha.com/?p=521337). **[2 sources]**

### Inferences
- **Per-trade gross of intraday momentum.** 6.67%/252 ≈ **2.6 bps a day**. The per-trade standard deviation is 6.19%/√252 ≈ 39 bps, so the per-trade IR ≈ 0.068. If the strategy trades on only about half of the days (the earlier "long or cash" variant), that is ≈5 bps per trade. Either way it is far below 8 bps, and it is viable only where a round trip costs about 1-2 bps or less (SPY-like). That fits Zarattini et al.'s net result being in SPY.
- **Intraday reversal measured on trade prices is partly bid-ask bounce.** A spread-crossing trader pays that bounce rather than earning it. Capturing it requires passive liquidity provision with queue priority, which is the HFT market-maker's game (Q4).
- **Order-flow and imbalance predictability** decays within minutes and is concentrated in milliseconds. At ≥100 ms it is essentially gone.
- **Intraday periodicity** is about the size of an effective spread, so it pays best as an **execution-timing overlay**: when to enter or exit a multi-day position. It does not pay as a standalone round trip that must cross two spreads.
- **1-5 days.** Weekly large-cap reversal cleared costs before 2010 by 30-50 bps/week. Haircutting by McLean-Pontiff (-58%) or Chordia et al. (halving) suggests roughly 13-25 bps/week might remain. That is speculative, and Khandani-Lo show steep decay in daily reversal. The universe filters (spread ≤10 bps, ADV ≥$20M) remove the stocks where reversal is strongest (Avramov et al.). So plan for news and event drift, plus residual reversal with cost-aware construction, and expect a modest edge.
- **Overnight accrual** of reversal and momentum premia (Lou-Polk-Skouras) is a structural reason to hold across the close. A plan built on intraday holds would forgo it.

### Gaps
- Heston-Korajczyk-Sadka magnitudes in bps were not retrieved.
- **Open/close auction effects** were not researched: Bogousslavsky (2021) on the cross-section of intraday and overnight returns, Baltussen-Da-Lammers-Martens (2021) on hedging demand and intraday momentum, Bogousslavsky-Muravyev (2023) on the close.
- Post-earnings drift decay (e.g., Martineau 2022) was not checked.
- Post-2013 out-of-sample performance of Gao et al. was not checked, except via Zarattini et al.
- Not retrieved: the sample period, turnover and gross returns of de Groot et al.; the sample and bps magnitudes of Jiang-Li-Wang; the size of the reversal component in Lou-Polk-Skouras.
- Post-2010 evidence on daily or weekly reversal in large caps (e.g., Nagel 2012 "Evaporating liquidity") was not checked.

## Q2: Realistic round-trip costs in 2024-2026 for a small Alpaca account

### Takeaway
Explicit costs are now tiny:
- Alpaca charges no commission on US equities.
- The SEC Section 31 fee has been $20.60 per million on sales since 2026-04-04, about 0.21 bp a round trip.
- The FINRA TAF is $0.000195 a share on sales (cap $9.79) in 2026, but a FINRA filing pauses it for October-December 2026.
- A CAT fee applies to both sides; its rate was not found.

So a round trip costs mainly the spread paid, less price improvement, plus slippage. Rule 605-based industry data put the median E/Q of top wholesalers at ~0.30-0.34 in 2025, so retail market orders pay about a third of the quoted spread. But a controlled study found average round-trip costs of 7 to 46 bps for identical orders at different brokers.

8 bps is a reasonable, probably slightly conservative, planning average for small marketable orders in names with spreads ≤10 bps, if Alpaca's routing gets industry-median price improvement. That must be measured live, because Alpaca paper trading gives no price improvement. For the most liquid names, the arithmetic suggests ~1-2 bps all-in.

### Cited Findings
**Regulatory fees (current as of 2026-10-15)**
- **SEC Section 31.** $20.60 per million, effective **2026-04-04**; $0.00 per million until then. It remains until 60 days after enactment of the FY2027 SEC appropriation. It was set after the Consolidated Appropriations Act 2026, which appropriated $2,149,000,000 to the SEC — [SEC Fee Rate Advisory 2026-2](https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2); [FINRA Information Notice 3/17/26](https://www.finra.org/rules-guidance/notices/information-notice-20260317); [Federal Register 2026-04233](https://www.govinfo.gov/content/pkg/FR-2026-03-04/pdf/2026-04233.pdf). **[2 sources: SEC and FINRA]**
- **FINRA TAF on covered equity sales.** $0.000195 a share, $0.01 minimum, **$9.79 maximum per trade**, effective **2026-01-01** (it was $0.000166 and $8.30) — [Revolut help](https://help.revolut.com/en-IS/help/wealth/order-execution-fees-and-limits/trading-regulatory-fees/); [Investrade fee schedule](https://www.investrade.com/fees/). **[2 sources, both brokers; FINRA's primary notice not retrieved]**
- **TAF pause.** FINRA filing SR-FINRA-2026-021 pauses TAF assessment for transactions from **2026-10-01 to 2026-12-31**. It was filed for immediate effectiveness, with assessment resuming 2027-01-01 — [SR-FINRA-2026-021](https://www.finra.org/sites/default/files/2026-09/SR-FINRA-2026-021.pdf). **[single-source]**
- **Alpaca regulatory fees.** SEC and FINRA fees apply on sells; the TAF on sells only; the CAT fee on **buys and sells**. Fees accrue intraday and are charged at end of day. Alpaca says it does not benefit from them. Current rates are on alpaca.markets/disclosures — [Alpaca docs](https://docs.alpaca.markets/docs/regulatory-fees); [Alpaca support](https://alpaca.markets/support/regulatory-fees). **[2 Alpaca pages]** Older figures on Alpaca pages are outdated: a 2021 blog quotes TAF $0.000166 with an $8.30 cap, and a forum post quotes SEC $22.90 per million and TAF $0.000119 with a $5.95 cap — [Alpaca blog](https://alpaca.markets/blog/reg-taf-fees/); [Alpaca forum](https://forum.alpaca.markets/t/pricing-and-fees/2309).
- **Commissions.** "For U.S. equity trades, there are no commissions charged and all clearing fees are paid by Alpaca Securities LLC to our clearing firm Velox Clearing" — [Alpaca docs](https://docs.alpaca.markets/docs/regulatory-fees). **[single-source]**

**Routing and payment for order flow**
- Alpaca's Rule 606 reports for 2026 Q1 and Q2 list non-directed equity orders routed to **Virtu Americas, Citadel Securities, Jane Street and GTS Securities**. Alpaca "earns revenue from third-party liquidity providers" based on executions — [606 report 2026 Q1](https://files.alpaca.markets/disclosures/library/SEC+606a1+-+2026Q1.pdf); [606 report 2026 Q2](https://files.alpaca.markets/disclosures/library/SEC+606a1+-+2026Q2.pdf). **[single-source: Alpaca's own reports. The venue percentages in the search extract were internally inconsistent ("rose from about 56% to about 35%") and are not used]**

**Execution quality**
- Amended Rule 605 adds E/Q (effective over quoted spread). It measures price improvement against the NBBO and against a new "best available displayed price". It requires summary reports split by S&P 500 vs non-S&P 500 and by order type — [National Law Review](https://natlawreview.com/article/effective-spread-order-execution-quality-reporting); [Katten](https://quickreads.ext.katten.com/post/102j23y/the-effective-spread-of-order-execution-quality-reporting). **[2 sources]**
- In January-July 2025, Susquehanna and HRT improved their **median E/Q** by 39% and 33%, to **0.299 and 0.341**. Citadel Securities executed 27.7bn retail shares with about $153m of net price improvement; Virtu gave $101.8m on 17.6bn shares (period unclear). In June 2025 the six largest retail market makers executed 68.1bn shares with $395.3m of price improvement — [Global Trading](https://www.globaltrading.net/?p=39575); [Global Trading, June 2025](https://www.globaltrading.net/?p=39430). **[single publisher; the medians are across all securities, not S&P 500 only]**
- Schwarz, Barber, Huang, Jorion, Odean, *The "Actual Retail Price" of Equity Trades* (JF 80(5), 2025, 2507-2541). Over nearly six months they placed 85,000 simultaneous identical market orders through six accounts at five brokers. **Mean round-trip execution cost, excluding commissions, ranged from 0.07% to 0.46% across accounts.** The gaps come from wholesalers pricing the same trades differently for different brokers, not from payment for order flow. Each basis point is worth about $2.8bn a year to retail traders — [IDEAS](https://ideas.repec.org/a/bla/jfinan/v80y2025i5p2507-2541.html); [SSRN](https://papers.ssrn.com/abstract=4189239); [WashU Olin](https://olin.washu.edu/about/news-and-media/news/2022/10/study-finds-astonishing-differences-in-brokers-pricing-of-stock-trades.php). **[2 sources]**
- Huang, Jorion, Lee, Schwarz (Federal Reserve FEDS, 2024) find similar dispersion of execution costs across wholesalers within brokers — [Federal Reserve](https://www.federalreserve.gov/econres/feds/who-is-minding-the-store-order-routing-and-competition-in-retail-trade-execution.htm). **[single-source]**

**Alpaca paper-trading fill model**
- Paper market buys fill at the ask and sells at the bid, with no price improvement; staff call this "pessimistic". When an order becomes eligible to fill, it gets a random partial fill 10% of the time. Order size is not checked against depth. Limit orders fill when price touches the limit, with no queue modelling. Fill timing depends on quote updates — [Alpaca forum (staff)](https://forum.alpaca.markets/t/slippage-paper-trading-vs-real-trading/2801); [Alpaca forum, fill delays](https://forum.alpaca.markets/t/paper-trading-fill-delays-of-50-260-seconds-limit-orders-filled-minutes-after-price-crossed/18223); [TradersPost](https://blog.traderspost.io/article/alpaca-paper-trading). **[2 sources; the official page [alpaca.markets/support/difference-paper-live-trading](https://alpaca.markets/support/difference-paper-live-trading) was not retrieved]**

### Inferences
- **Fee arithmetic.**
  - Section 31 is 0.206 bp of sale value.
  - The TAF is 0.39 bp of sale value at $5, 0.10 bp at $20, 0.04 bp at $50 and 0.02 bp at $100. The $9.79 cap binds only above ~50,200 shares.
  - Regulatory fees therefore total **≈0.2-0.6 bp per round trip**, plus CAT. That is about 3-7% of the 8 bps budget, so no plausible fee change alters the horizon decision.
  - Through 2026-12-31 the TAF is paused (if the filing is in effect). The Section 31 rate could change after the FY2027 appropriation; that is unknown.
- **Spread arithmetic.** A 1-cent spread is 10 bps at $10, 5 bps at $20, 2 bps at $50, 1 bp at $100 and 0.2 bp at $500. If the minimum quoted spread is one cent, the universe's "median quoted spread ≤10 bps" filter excludes most stocks under ~$10. The "price ≥ $5" filter then rarely binds.
- **Price improvement per share** from the Global Trading figures: ≈$0.0055 (Citadel) to $0.0058 (Virtu). That is ≈2.8 bps a side at $20, 1.1 bps at $50 and 0.55 bp at $100.
- **Is 8 bps reasonable?** Consider a stock at the 10 bps spread cap:
  - Crossing the full spread on both legs, plus 1.5 bps slippage a side, plus ~0.3 bp fees, gives ≈13 bps. That is what Alpaca paper fills would show, with no price improvement.
  - With E/Q 0.3-0.5 it gives ≈6-8 bps.
  - At a 3 bps spread, it is ≈4-6 bps.

  So 8 bps is a plausible-to-conservative average for small live marketable orders, **if** Alpaca's wholesaler execution matches industry medians. The Schwarz et al. range (7-46 bps by broker, for their stock sample) shows that routing quality can dominate, so it must be measured. Even the best account's 7 bps mean was near 8, though their sample may include smaller and wider-spread stocks than this universe (unverified). The goal's REPORT.md records a published comparison of "8 bps against 6.95 bps", which is consistent.
- **The most liquid names** are mega-caps priced ≥$100 with 1-cent spreads (≤1 bp) and the major index ETFs (well under 1 bp at their prices). There, a round trip probably costs ≈1-2 bps all-in, and the goal's flat 1.5 bps-a-side slippage allowance would dominate the cost model. This is low-to-moderate confidence: 2026 spreads for specific tickers were not retrieved.
- **Paper-trading bias** grows as holds shorten:
  - It overstates the cost of marketable orders, because there is no price improvement.
  - It understates the cost of passive orders, because there is no queue, no adverse selection and no depth check.

  A minute-level strategy cannot be validated on Alpaca paper. Multi-day strategies are far less sensitive, since cost is a small share of σ over the hold.
- **A discrepancy for the coordinator.** The brief says "a position ≤ 2% of ADV". The goal file has `max_position_adv_pct = 0.02`, a percent, i.e. **0.02%** of 20-day median dollar volume, and REPORT.md (R-9) says "at most 0.02% of its stock's daily volume" — [goal.toml](/home/user/AIresume/trading/goal/goal.toml). At $20M ADV that caps a position at about $4,000; in a $1bn-ADV mega-cap, at about $200,000.

### Gaps
- No 2024-2026 effective-spread figures in bps for S&P 500 vs mid caps (Rule 605 summary reports) were retrieved.
- Not retrieved: Alpaca's own Rule 605 or E/Q statistics; the CAT fee rate per executed equivalent share; the FINRA primary notice for the 2026 TAF rate; the compliance status of amended Rule 605; the status of the SEC's 2024 half-penny tick amendment.
- Practitioner cost studies were not retrieved: AQR's Frazzini-Israel-Moskowitz "Trading Costs", Virtu/ITG and Abel Noser cost reviews, Bloomberg.
- Not checked: Alpaca's API latency; its Elite/DMA routing options and per-share pricing; short-borrow fees for 1-5 day shorts; whether wholesalers class algorithmic API flow as retail for price improvement.
- Market impact for $2-10k orders was not sourced. The goal's own REPORT.md cites 1.2-2.4 bps at its liquidity limit, by the square-root law.

## Q3: Break-even arithmetic: the accuracy a trade needs at each horizon, against published ICs

### Takeaway
At a fixed 8 bps, the accuracy needed per trade falls with √horizon. For a 30%-volatility stock, the 2x-cost entry rule needs a per-trade IR (≈ the IC for a 1-sigma signal) of:

| Horizon | IR needed | Hit rate |
|---|---|---|
| 5 min | 0.75 | 77% |
| 30 min | 0.31 | 62% |
| 150 min | 0.14 | 55.4% |
| 1 day | 0.085 | 53.4% |
| 3 days | 0.05 | 51.9% |
| 5 days | 0.04 | 51.5% |

Published out-of-sample predictability reaches the short-horizon levels only within milliseconds: R² ≈10% at 5 seconds, which drops sharply with any delay. The best-known half-hour effect has an out-of-sample R² of 1.4% (correlation ≈0.12) and a per-trade IR ≈0.068. That is enough for 1-5 day holds at 8 bps, or for intraday holds only at ~1-2 bps cost.

### Cited Findings
- Gao et al.: out-of-sample R² 1.4% (in-sample 1.6%). The timing strategy returned 6.67%/yr with a standard deviation of 6.19%/yr and Sharpe 1.08 — [paper PDF](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf); [ResearchGate](https://www.researchgate.net/publication/325364670_Market_Intraday_Momentum).
- Aït-Sahalia et al.: median-stock out-of-sample R² 10.5% for 5-second returns, with 64% correct direction. Predictability sits in the most recent ~10 ms and drops sharply with delay — [NBER](https://www.nber.org/papers/w30366); [seminar summary](https://lists.dm.unipi.it/hyperkitty/list/random@lists.dm.unipi.it/thread/TGUUFLBMCV5CDK4PPZVXITGRA43XLZIW/).
- Chinco, Clark-Joseph, Ye (JF 74(1), 2019, 449-492): LASSO forecasts of one-minute-ahead returns, using all lagged returns, raise out-of-sample fit and forecast-implied Sharpe ratios. The predictors are "unexpected, short-lived, and sparse" and often stocks with fundamental news. Magnitudes were not retrieved — [vLex / JF](https://law-journals-books.vlex.com/vid/sparse-signals-crosssection-returns-855623649); [NBER w23933](https://www.nber.org/papers/w23933.ack). **[same paper, 2 hosts]**
- Order-imbalance predictability is gone in 5-60 minutes, or 5-15 minutes for large NYSE stocks — [CFA digest](https://rpc.cfainstitute.org/en/research/cfa-digest/2005/11/evidence-on-the-speed-of-convergence-to-market-efficiency-digest-summary); [IDEAS, Chung & Hrazdil](https://ideas.repec.org/a/eee/empfin/v19y2012i5p702-720.html).

### Inferences
**Assumptions.** Annualized volatility of 20%, 30% or 40%, so daily σ is 126, 189 or 252 bps. σ scales with √time. All daily variance is assumed to accrue evenly within the session, which overstates intraday σ and so is *favourable* to short horizons. Returns are normal and trades independent. IR = expected gross return / σ over the hold. Hit rate = Φ(IR). With a z-scored signal, E[r|z] = IC·σ·z, so the IC needed at |z|=1 equals the IR, and at |z|=2 it is half of it.

**Table A — base cost 8 bps, 30% volatility.** The last column is the gross IR needed for net Sharpe 1.0 / 1.5 at ~1,300 round trips a year (25 a week), where the net per-trade IR needed is S/√1300 = 0.028 / 0.042.

| Hold | σ (bps) | Break-even IR (hit) | 2x-cost IR (hit) | Gross IR for net Sharpe 1.0 / 1.5 |
|---|---|---|---|---|
| 5 min | 21 | 0.37 (64.6%) | 0.75 (77.3%) | 0.40 / 0.42 |
| 30 min | 52 | 0.15 (56.1%) | 0.31 (62.0%) | 0.18 / 0.19 |
| 150 min | 117 | 0.068 (52.7%) | 0.14 (55.4%) | 0.096 / 0.11 |
| 1 day | 189 | 0.042 (51.7%) | 0.085 (53.4%) | 0.070 / 0.084 |
| 3 days | 327 | 0.024 (51.0%) | 0.049 (51.9%) | 0.052 / 0.066 |
| 5 days | 423 | 0.019 (50.8%) | 0.038 (51.5%) | 0.047 / 0.061 |

**Stress, 12 bps, 30% volatility.** The 2x-rule IR is 1.12 (87% hit) at 5 minutes, 0.46 at 30 minutes, 0.205 (58%) at 150 minutes, 0.127 at 1 day, 0.073 at 3 days and 0.057 at 5 days. A 20%-volatility stock at 8 bps needs exactly the same as the 30%-volatility stock at 12 bps.

**Minimum hold so that cost ≤ IR·σ_h** (30% volatility):

| Cost | IR | Break-even hold | 2x-rule hold |
|---|---|---|---|
| 8 bps | 0.05 | 280 min | 1,118 min (2.9 days) |
| 8 bps | 0.068 | **151 min** | **605 min (1.55 days)** |
| 8 bps | 0.10 | 70 min | 280 min |
| 8 bps | 0.15 | 31 min | 124 min |
| 12 bps | 0.068 | 340 min | 1,360 min (3.5 days) |
| 4 bps | 0.068 | 38 min | **151 min** |
| 2 bps | 0.068 | 9 min | 38 min |

The goal's 150-minute basis therefore matches **break-even at 8 bps**, or **the 2x rule at 4 bps**. It does not match the 2x rule at the planned 8 bps.

**The goal's own check.** REPORT.md quotes "an IC of 0.096 needed at 2.5 hours". That equals my gross IR for net Sharpe 1.0 at 150 minutes, so the two calculations agree. REPORT.md also cites "MSCI Barra's '0.10 is very good'", which I could not verify. At 150 minutes the plan needs a "very good" IC on every trade; at 1-5 days it needs 0.05-0.085.

**Comparison with published effects:**
- Gao et al.'s per-trade IR ≈0.068 roughly equals the 2x-rule requirement at about 1.5 days (8 bps) or 150 minutes (4 bps).
- On SPY's own last half-hour (σ ≈39 bps, implied by the 6.19%/yr standard deviation), the 2x rule at 8 bps would need IR 0.41, six times what the effect delivers. At 1 bp it needs 0.051, which the effect clears.
- The 5-second R² of 10.5% (correlation ≈0.32) would meet the short-horizon requirement only at millisecond latency, which this system lacks (Q4).

**Sizing under the volatility target** (30% volatility, independent positions, ~5 new round trips a day). A daily P&L standard deviation of 0.2% is $200. The implied position and net edge per round trip needed for 3% / 5% a year:

| Hold | Concurrent positions | Position size | Net edge needed, 3% / 5% a year |
|---|---|---|---|
| 150 min | ~2-5 | ~$7.6k | 3.0 / 5.0 bps |
| 1 day | ~5 | ~$4.7k | 4.9 / 8.1 bps |
| 3 days | ~15 | ~$2.7k | 8.4 / 14.1 bps |
| 5 days | ~25 | ~$2.1k | 10.9 / 18.2 bps |

The net Sharpe target fixes the per-trade *net IR* at about 0.028-0.042 whatever the horizon. Cost/σ is the part that explodes at short horizons, at 0.38 at 5 minutes against 0.024 at 3 days. The 2x rule's implied minimum (expected net ≥ 8 bps) roughly delivers the 3%/yr target at 3-day holds.

### Gaps
- No published rule-of-thumb IC levels were retrieved: the Grinold-Kahn and MSCI Barra benchmarks quoted in the goal's REPORT.md were not verified here.
- No published daily cross-sectional IC for 1-5 day reversal or news signals was retrieved.
- No 2024-2026 single-stock volatility statistics (typical annualized volatility of S&P 500 or mid-cap names) were retrieved, hence the 20/30/40% assumptions.
- No source was retrieved for the overnight share of daily variance or the U-shape of intraday volatility. Both would raise the IR needed intraday.
- The independence assumption flatters multi-day books, which share factor exposure unless hedged.

## Q4: Who earns minute-level profits, and can a retail-API system with ~100+ ms latency compete?

### Takeaway
Short-horizon trading profits go to the fastest firms:
- HFT performance is ranked by relative latency.
- Revenue concentration is high and is not declining.
- New entrants earn less and exit more often.
- Latency-arbitrage races are won by 5-10 microseconds.
- Return predictability sits in the most recent ~10 ms.

A retail-API system at ≥100 ms is about four orders of magnitude slower than the margin of victory. It cannot compete at horizons of seconds to minutes. As a liquidity taker it pays the spread those firms earn, and its orders are filled by those same wholesalers.

### Cited Findings
- Baron, Brogaard, Hagströmer, Kirilenko (JFQA 54(3), 2019, 993-1024):
  - Differences in relative latency account for large differences in HFT firms' trading performance.
  - Firms that move up the latency ranking through colocation upgrades improve their performance.
  - Speed works through short-lived information and risk-management channels, helping market making and cross-market arbitrage.
  - Concentration of HFT revenue and volume is high and non-declining over the five-year sample.

  [IDEAS](https://ideas.repec.org/a/cup/jfinqa/v54y2019i03p993-1024_00.html); [Imperial repository](https://spiral.imperial.ac.uk/entities/publication/314ff61c-b583-44e9-b508-01aac9fa0e43). **[same paper, 2 hosts]**
- The 2014 CFTC draft of the same work, on E-mini S&P 500 futures over two years, found a median HFT annualized Sharpe of **4.3** and a four-factor alpha of 22.02%. Revenue accumulated to the top performers, and new entrants were less profitable and more likely to exit — [CFTC draft](https://www.cftc.gov/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf). **[single-source; old: about 2010-2012 data]**
- Aquilina, Budish, O'Neill (QJE 2022; FTSE 100 message data):
  - About 537 races per symbol per day, roughly one a minute.
  - The modal race is decided by **5-10 microseconds**.
  - Races are about 22% of volume and 21% of trades.
  - The top six firms take more than 80% of race wins and losses.
  - The average race is worth about half a tick.
  - Latency arbitrage acts as a ≈0.5 bp tax on trading, and eliminating it would cut the cost of liquidity by 17%.
  - About $5bn a year is at stake in global equities.

  [NBER w29011](https://www.nber.org/system/files/working_papers/w29011/w29011.pdf); [BIS WP 955](https://www.bis.org/publ/work955.pdf); [FCA Occasional Paper 50](https://www.fca.org.uk/publications/occasional-papers/occasional-paper-no-50-quantifying-high-frequency-trading-arms-race-new-methodology); [Harvard Law School Forum](https://corpgov.law.harvard.edu/2021/11/05/quantifying-the-high-frequency-trading-arms-race). **[2+ sources]**
- High-frequency predictability sits in the last ~10 ms and drops sharply with small delays — [NBER w30366](https://www.nber.org/papers/w30366); [seminar summary](https://lists.dm.unipi.it/hyperkitty/list/random@lists.dm.unipi.it/thread/TGUUFLBMCV5CDK4PPZVXITGRA43XLZIW/).
- Alpaca routes non-directed orders to Virtu, Citadel Securities, Jane Street and GTS, which are HFT market makers and wholesalers, and is paid by them — [Alpaca 606 2026 Q2](https://files.alpaca.markets/disclosures/library/SEC+606a1+-+2026Q2.pdf). **[single-source]**

### Inferences
- 100 ms is 100,000 µs, about 10,000-20,000 times the 5-10 µs margins by which races are won. At seconds-to-minutes horizons the system's signals would be stale relative to the firms that set the quotes.
- A taker with stale signals faces adverse selection. Its fills come mostly when the faster side is happy to trade with it.
- The minute-level edge that exists, liquidity provision and bounce capture, needs queue priority and fast cancels. Retail API orders do not have these, and wholesalers internalize retail flow instead of letting it rest.
- This argument is independent of the 8 bps cost figure. Even at ~1 bp cost (Q5), minute-level predictability is not reachable at retail latency.
- The system's speed is adequate where the edge decays over hours to days: news drift over several days, overnight-accruing premia, weekly reversal. There, 100 ms costs a negligible share of the expected move.

### Gaps
- No measured Alpaca order-to-fill latency was retrieved.
- No US-equity HFT profitability figures after 2020 were retrieved.
- It was not checked whether Alpaca's API flow gets "retail" price improvement or is segmented as professional.
- Budish-Cramton-Shim (2015) itself was not retrieved; only the later Aquilina-Budish-O'Neill quantification was.

## Q5: Would a cheaper universe (top ~100-300 stocks and major ETFs, ~1-2 bp spreads) make shorter horizons viable, and at what cost to breadth?

### Takeaway
Cutting the round trip from 8 to ~1-2 bps cuts the hurdle 4-8x:
- **30-150-minute holds become arithmetically plausible.** The 2x-rule IR is 0.05-0.11 at 2 bps for a 20%-volatility mega-cap, and the documented SPY intraday-momentum edge appears to survive costs there.
- **Minute-level holds still do not work.** At 5 minutes the 2x rule needs IR 0.28 at 2 bps, or 0.14 at 1 bp, and the latency evidence still rules this out.

The price is less breadth: a few hundred of the most efficiently priced names, where reversal is weakest. So a cheap-universe study is worth doing as a secondary track for intraday holds of 30 minutes to a few hours in ETFs and mega-caps. It also lowers costs for multi-day trades. It is not a basis for minute-level holds.

### Cited Findings
- Restricting reversal strategies to large caps cut costs enough to leave 30-50 bps/week net. Most of the cost erosion came from small caps — [IDEAS](https://ideas.repec.org/a/eee/jbfina/v36y2012i2p371-382.html); [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks). **[2 sources]**
- Reversals, and potential contrarian profits, are largest in high-turnover, low-liquidity stocks — [IDEAS](https://ideas.repec.org/a/bla/jfinan/v61y2006i5p2365-2394.html). **[same paper, 2 hosts]**
- Intraday momentum is documented in SPY: 6.67%/yr gross, Sharpe 1.08, 1993-2013 — [paper PDF](https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf). A related SPY intraday strategy reports net Sharpe 1.33 for 2007-2024 — [SFI WP 24-97](https://www.sfi.ch/fr/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy). **[single-source for the net figure]**
- Lou-Polk-Skouras's overnight and intraday patterns are "stronger for large-cap and high-price stocks" — [LSE](https://researchonline.lse.ac.uk/id/eprint/87481). **[single-source extract]**
- The goal allows positions of at most 0.02% of 20-day median dollar volume — [goal.toml](/home/user/AIresume/trading/goal/goal.toml) (local file).

### Inferences
- **Hurdle arithmetic** (20% volatility; my break-even runs, see Q3). The 2x-rule IR at 2 bps is 0.28 (61% hit) at 5 minutes, 0.114 (54.6%) at 30 minutes, 0.051 (52.0%) at 150 minutes and 0.032 at 1 day. At 1 bp it is 0.14, 0.057, 0.026 and 0.016. The 30-150-minute requirements fall into the range of the documented SPY effect (per-trade IR ≈0.068). The 5-minute requirement does not, and it would also need sub-second speed.
- **The cost to breadth.** For independent bets, aggregate Sharpe scales with √(number of independent bets). Shrinking from roughly a thousand eligible names to ~200 (both counts unverified) cuts the attainable cross-sectional IR by about √5 ≈ 2.2 at the same IC, unless more trades per name make up for it. The goal caps this at 4 round trips per symbol per day.
- Mega-caps and index ETFs are also where reversal is weakest (Avramov et al.) and where professional competition is presumably densest (unsourced). So IC per name is likely lower there.
- **The cheap universe helps multi-day trading too.** De Groot et al. show that a large-cap universe preserved net reversal profits. Larger ADV also lifts the 0.02%-of-ADV position cap from ~$4k (at $20M ADV) to ~$200k (at $1bn), which removes sizing friction.
- **A sensible design** is a two-sleeve study:
  - (a) a core of 1-5 day holds across the full eligible universe;
  - (b) an optional intraday sleeve of 30 minutes to a few hours in index ETFs and the most liquid mega-caps, judged at their measured live costs.

  Neither sleeve should plan on minute-level holds.

### Gaps
- Not retrieved: 2026 quoted or effective spreads for the top 100-300 names and the major ETFs; the number of US names that pass the base filters (ADV ≥$20M, spread ≤10 bps); evidence on HFT competition intensity by stock size.
- Not retrieved: the cost assumptions behind Zarattini et al.'s net Sharpe; post-2013 out-of-sample evidence on intraday momentum in single mega-cap stocks, as opposed to SPY.

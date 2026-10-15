# Overnight single-name position sizing under jump (gap) risk: 4% vs 8% cap

> **Process caveat (read first).** This session lost web access after 6 searches. The WebSearch budget is shared by every agent in the turn and ran out. WebFetch failed on all 13 domains tried (DNS `ENOTFOUND`), and the egress proxy refused direct downloads (403 for Yahoo, Stooq, Wikipedia and federalreserve.gov). So:
> 1. The external facts below come from 6 search-result summaries. The pages themselves were not opened, so most of these facts are **single-source**.
> 2. The gap frequencies were **computed in this session** from the project's cached daily prices: YHOO, NVDA, MSFT, ORCL and GOOG in `goal/.data-cache/`, Yahoo-format OHLC files.
> 3. The return-trade-off analysis is **arithmetic on the goal's own limits** (GOAL.md).
> 4. Several well-known facts are listed under *Gaps* as **UNVERIFIED background**, with approximate values: takeover-premium statistics, the 2015–2026 cases, '40 Act and UCITS rules, and Kelly/drawdown theory. They need a verification pass before anyone relies on them.
>
> "Today" is 2026-10-15. The local price data ends in 2013–2017.

## 1. How often do liquid US stocks gap overnight by ≥10/20/30/50%? Earnings vs non-earnings, causes, and takeover premia

### Takeaway
The sample is five large, very liquid tech stocks over 59 stock-years (2003 to each file's end). In it, overnight gaps of ≥10% happened 0.57 times per stock-year (≈23 per 10,000 stock-nights). Gaps of ≥20% happened 0.05 times per stock-year (2 per 10,000), gaps of ≥30% 0.03 times, and gaps of ≥50% never.

About three quarters of the ≥10% gaps were earnings nights (my attribution, not verified). Even so, two of the three gaps of ≥20% were non-earnings: Yahoo +49.5% on Microsoft's bid and NVIDIA −28.0% on a revenue warning. That makes non-earnings gaps of ≥20% about 1.3 per 10,000 stock-nights. A book with about 15 names overnight runs about 3,300–3,800 position-nights a year, which works out to about 0.5 such gaps a year, roughly half of them against the position. That rate is from mega-caps; mid-caps, biotech and banks are likely worse.

Gaps of ≥50% come from two places: takeovers of (mostly biotech) targets on the upside, and failures or frauds on the downside (banks in 2023, Luckin in 2020). I could not verify their frequency in this session.

### Cited Findings
- **Pooled local sample, 2003 to file end.** The sample is 14,953 overnight periods (59.3 stock-years) of YHOO, NVDA, MSFT, ORCL and GOOG, with gap = open ÷ previous close − 1 — [computed from local files yhoo/nvda/msft/orcl/goog.csv](/home/user/AIresume/trading/goal/.data-cache/). This is one dataset of survivors, so treat it as single-source.

  | Gap size | Count | Per stock-year | Per 10,000 stock-nights |
  |---|---|---|---|
  | ≥10% | 34 (21 up, 13 down) | 0.573 | 22.7 |
  | ≥15% | 11 (7 up, 4 down) | 0.185 | 7.4 |
  | ≥20% | 3 (1 up, 2 down) | 0.051 | 2.0 |
  | ≥30% | 2 (1 up, 1 down) | 0.034 | 1.3 |
  | ≥50% | 0 | 0 | 0 |

- **Full history, all nights, including the dot-com years** — [local files](/home/user/AIresume/trading/goal/.data-cache/):

  | Stock | Years | Gaps ≥10% | ≥20% | ≥30% | Largest gap |
  |---|---|---|---|---|---|
  | YHOO | 1996–2014 (18.7 yrs) | 22 | 2 | 1 | +49.5% |
  | NVDA | 1999–2014 (15.9 yrs) | 22 | 4 | 1 | −30.6% (2004-08-06) |
  | MSFT | 1986–2017 (31.7 yrs) | 9 | 0 | 0 | −14.8% (2000-04-24) |
  | ORCL | 1995–2014 (20.0 yrs) | 19 | 3 | 1 | +30.1% (1999-06-16) |
  | GOOG | 2004–2013 (8.5 yrs) | 7 | 0 | 0 | +19.1% (2008-04-18) |

  No stock in the sample ever gapped 50% overnight.
- **The three gaps of ≥20% since 2003:**
  - NVDA 2004-08-06: −30.6% (4.853 → 3.370). By my attribution this was the night after earnings.
  - YHOO 2008-02-01: +49.5% (19.18 → 28.68), on Microsoft's unsolicited bid at a 62% premium to the previous close.
  - NVDA 2008-07-03: −28.0% (18.03 → 12.98), on an unscheduled revenue warning and a chip-failure charge announced after the close.

  Sources: [local nvda.csv](/home/user/AIresume/trading/goal/.data-cache/nvda.csv) and [local yhoo.csv](/home/user/AIresume/trading/goal/.data-cache/yhoo.csv). The causes of the 2008 events come from the project's GT-2 annotation, which notes "an unscheduled revenue warning … not an earnings release" — [gt02_consistency.py](/home/user/AIresume/trading/goal/goaltests/gt02_consistency.py). That gives two sources for each gap: the data and the annotation.
- **Yahoo opened below the offer.** The open of $28.68 was about 85% of the $31 offer: the gap was +49.5% against a +62% premium. The market discounts deal risk, so a short's overnight loss on a bid is usually smaller than the headline premium — [local yhoo.csv](/home/user/AIresume/trading/goal/.data-cache/yhoo.csv); [GT-2](/home/user/AIresume/trading/goal/goaltests/gt02_consistency.py).
- **Kapadia & Zekhnini (JFE 2019, 131:666–692).** "Ex post, the entire annual average return of a typical stock accrues on the four days on which its price jumps." That implies about 4 jump days per stock-year, including earnings. I did not see the paper's jump definition — [RePEc](https://ideas.repec.org/a/eee/jfinec/v131y2019i3p666-692.html); [SUFE abstract](https://academicnewsletter.sufe.edu.cn/info/355909). Both are copies of the same abstract, so this is one primary source.
- **Jeon, McCurdy & Zhao (JFE 2022, 145(2):1–17).** The sample is 21 million news articles on more than 9,000 firms, 1980–2012. Jumps in stock returns track both how often news arrives and what it says, and the link has strengthened over the decades. Jump sensitivity to news is greater for firms with more media visibility, analyst coverage and institutional ownership, and it varies by news category — [RePEc](https://ideas.repec.org/a/eee/jfinec/v145y2022i2p1-17.html); [Rotman Insights](https://www-2.rotman.utoronto.ca/insightshub/finance-investing-accounting/news-stock-swings). These are two descriptions from search summaries.
- **Which news causes jumps.** One secondary blog summary of that paper ranks earnings/revenue, analyst ratings, capital-structure changes and M&A as the most jump-relevant of ten categories — [whatworksintrading](https://whatworksintrading.substack.com/p/in-depth-blog-summary-news-as-sources). This is weak and single-source: the blog misattributes the paper's authors.
- **Contrary evidence on intraday jumps.** Joulin et al. find that neither firm news nor market-wide news explains most high-frequency (intraday) price jumps — [arXiv 0803.1769](https://arxiv.org/pdf/0803.1769), search summary. This concerns intraday jumps, not overnight gaps.
- **Takeover premia, which are a short's risk:**
  - An M&A event-study guide puts the target's announcement-window abnormal return at "commonly 15 to 30 percent" — [EventStudyTools](https://www.eventstudytools.com/ma-event-study-example). Single-source.
  - A KPMG comparison (publication year unclear) puts average control premia highest in the US at 37%, then Asia 32%, the UK 29% and developed EU 28% — [KPMG](https://kpmg.com/pl/en/insights/business-transformation/control-premium-in-poland-2020-2024.html). Single-source, search summary.
- **Takeovers are a recurring feature of returns.** Easterwood et al. (2022) build a "takeover factor" from acquisition announcements in 1990–2020. Its premium is substantially larger than the size factor's — [Quantpedia](https://quantpedia.com/takeover-factor-explains-the-size-effect/). Search summary.

### Inferences
- **Earnings dominate the ≥10% gaps.** By the companies' usual reporting calendars (my attribution, not verified), about 26 of the 34 gaps of ≥10% fell the morning after earnings. That leaves about 8 non-earnings gaps of ≥10%: about 0.13 per stock-year, or about 5.4 per 10,000 nights. Most of them are Yahoo's 2007–08 Microsoft saga, the October 2008 market gaps, and NVIDIA's 2008 warning. Of the non-earnings gaps, 2 were ≥20% (about 1.3 per 10,000 nights), 1 was ≥30% and none was ≥50%.
- **The non-earnings rate is very uncertain.** Two events in 59.3 stock-years gives a 95% Poisson interval of about 0.4%–12% per stock-year for non-earnings gaps of ≥20%.
- **What this means for the planned book.** With about 15 positions held overnight (about 3,300–3,800 position-nights a year), mega-cap rates give:
  - about 2 non-earnings gaps of ≥10% a year, about 1 of them adverse, costing 0.4% each at a 4% cap and 0.8% at an 8% cap;
  - about 0.5 non-earnings gaps of ≥20% a year, about 0.25 of them adverse.

  A universe that includes mid-caps, biotech and banks will have higher rates.
- **Ordinary overnight volatility is modest; the jump tail is the problem.** With the largest 2% of gap nights dropped (GT-2's proxy for earnings nights), overnight variance was only 18–21% of daily variance, against 33–42% with all nights — [computed from local files](/home/user/AIresume/trading/goal/.data-cache/).
- **Takeover drag on shorts depends on short gross, not on the per-name cap.** The expected annual cost is short gross × annual bid rate × average announcement gap. Assuming a bid rate of 2–5% of firms a year (unverified, see Gaps) and an average gap of 15–30%, a short gross of about 30% costs **≈0.1–0.45% a year whatever the cap**. Against a 3–5% a year target that is material.

  The cap changes only the size of the worst single hit. At an average 15–30% gap that is 0.6–1.2% at 4% and 1.2–2.4% at 8%; on a Yahoo-sized gap it is 2% at 4% and 4% at 8%. A backtest on survivor-only data leaves out acquired targets, so it understates this drag.
- **Expected bids against the book.** About 7.5 shorts held overnight is about 1,900 short-nights a year. At a 2–5% annual bid rate, that is roughly 0.15–0.4 bids a year against the shorts, or one every 2.5–7 years.

### Gaps
- **No CRSP-wide gap table.** I found no published per-stock-year table of overnight gaps by threshold, split into earnings and non-earnings, for a CRSP-wide liquid universe; the search budget ran out first. Candidates to check:
  - Kapadia & Zekhnini (2019): jump definition and frequency tables;
  - Jeon-McCurdy-Zhao (2022): jump frequency by news type;
  - Savor (2012, JFE) and Chan (2003, JFE): large price moves with and without news;
  - Boudoukh, Feldman, Kogan & Richardson (2019, RFS).

  A point-in-time universe that includes delisted stocks is needed. A current-constituents sample misses both acquired targets and failed firms, which are exactly the tail events in question.
- **UNVERIFIED takeover background (approximate):**
  - Betton, Eckbo & Thorburn (2008): average initial offer premium about 45% over the price 2 months before.
  - Schwert (1996): the pre-bid runup is about a third of the total premium.
  - The annual bid rate for US listed firms is about 2–5%. S&P 500 deletions caused by acquisitions suggest about 2–4% a year for large caps.
  - Most US deals are announced outside the regular session, so the jump arrives as an overnight gap.
- **UNVERIFIED cause list for large non-earnings gaps:** takeover bids and leaks; pre-announcements and guidance withdrawals; FDA and clinical outcomes; auditor resignations, filing delays, fraud and short-seller reports; deposit runs and seizures; strategic deals and investments; S&P 500 inclusion (usually under 15%).

## 2. What single-name limits do professional market-neutral, stat-arb and long/short managers use?

### Takeaway
I could gather only thin documentary evidence:
- One BNY Mellon market-neutral fund caps any single long *or short* at 5% of net assets at the time of purchase or short sale.
- Other market-neutral fund documents limit net exposure (Steward: −20% to +40%) or total shorts (a Fidelity Canada fund: up to 100% of NAV), not single names.

Regulatory diversification rules and practitioner norms, which I could not verify this session, point the same way: single issuers at about 5–10%; stat-arb books with hundreds to thousands of names at under 1% each; and in fundamental long/short books, shorts sized smaller than longs.

### Cited Findings
- **BNY Mellon market-neutral fund.** Its 2010 summary prospectus (497K) says: "No purchase or short sale of any individual equity security will be made if it causes the position to exceed 5% of the net assets of the fund, at the time of purchase or short sale." — [SEC EDGAR 497K](https://www.sec.gov/Archives/edgar/data/787623/000093041310005104/c63023_497k.htm). Quote from the search summary; the page was not opened; single-source.
- **Steward Equity Market Neutral (Crossmark).** Its summary prospectus of 28 Aug 2023 lets net long exposure (long market value minus short market value) range from −20% to +40% — [Crossmark](https://www.crossmarkglobal.com/stewardfunds/steward-funds-08-28-23-summary-prospectus-emn/). Single-source.
- **Fidelity Canada market-neutral fund.** It may use leverage through short selling of up to 100% of NAV and through derivatives — [Fidelity Canada MRFP](https://fidelity.ca/content/dam/fidelity/en/documents/mrfp-annual/FICL_MNA_MRFPA.pdf). Single-source.

### Inferences
- **The one per-name cap found sits between 4% and 8%.** It is 5% of NAV *at entry*, the same for longs and shorts. Positions can drift above an entry limit, while the goal's 4% is a hard limit checked daily at 15:45. A 4% hard cap is therefore about as strict as a 5% entry cap.
- **The goal's book is concentrated by quant standards.** About 15 names is far more concentrated than stat-arb (hundreds of names) and closer to a fundamental long/short book. Per-name jump limits matter more for it than for a typical stat-arb book. That argues for professional-style per-name caps of ≤5%, not 8%.

### Gaps
- **Not verified (EDGAR and fund sites unreachable):** per-name and short-side caps in the prospectuses of AQR Equity Market Neutral, Vanguard Market Neutral, JPMorgan Research Market Neutral, Boston Partners Long/Short Research, Diamond Hill Long-Short and Gotham, and in UCITS long/short KIIDs.
- **UNVERIFIED regulatory background:**
  - US Investment Company Act §5(b)(1): a "diversified" fund has at least 75% of assets in positions of ≤5% of assets each and ≤10% of an issuer's voting securities.
  - UCITS Directive 2009/65/EC Art. 52: ≤5% per issuer, raised to 10% provided holdings above 5% total ≤40%.
- **Practitioner texts not checked:**
  - Grinold & Kahn: breadth and risk budgeting.
  - Paleologo, *Advanced Portfolio Management* (2021) and *The Elements of Quantitative Investing*: max-position and idiosyncratic-risk limits.
  - Isichenko (2021): ADV-based limits.
  - Chan: Kelly sizing.
- **UNVERIFIED market folklore:** stat-arb weights well under 1% of GMV with ADV participation caps; fundamental long/short top longs at 5–10% of NAV and shorts at 2–5%; multi-manager pods cut capital after about a 5% drawdown and stop the PM at about 7.5% (press reports).

## 3. What does sizing theory say about jump risk? Kelly with jumps, ES/CVaR, stress limits, and the daily loss limit

### Takeaway
Growth-optimal (Kelly) sizing is not what binds here. At 4–8% per name, a 50% jump costs almost no log-growth, and both caps are only a few percent of a plausible Kelly fraction. What binds is the hard guardrails: the 2% daily loss, the ≤4% single event (KR2.8), and the 9% drawdown halt with its never-10% rule.

A gap realizes before any stop or daily limit can act, so the right tool is a stress-loss (scenario) limit:
- **Per-name cap = loss budget ÷ design jump.**
- **Drawdown scaling:** current drawdown + worst single-event loss must stay below 10%.

VaR and ES at the usual 97.5–99% levels can't see events with a nightly probability of about 10⁻⁴, so they can't replace the stress limit.

### Cited Findings
- **The goal's rules.** The daily loss is counted from the previous session's close, "so an overnight gap counts". No single jump event may cost more than 4% (KR2.8). The worst day is 2.5% "except through a jump beyond the jump assumptions". Equity must never fall 10% below its peak, with a halt at 9% — [GOAL.md](/home/user/AIresume/trading/goal/GOAL.md).
- **Jump risk is priced.** In Kapadia & Zekhnini (2019), a long-short portfolio sorted on predicted jump probability earned about 9.4% a year, which the authors read as investor aversion to idiosyncratic jump risk — [RePEc](https://ideas.repec.org/a/eee/jfinec/v131y2019i3p666-692.html). From the search summary; its alpha figure came through garbled.

### Inferences
These are my own derivations, using the goal's parameters.
- **Kelly with a jump.**
  - Per-night log growth of a position f is g(f) ≈ fμ − ½f²σ² + p·[ln(1 − fJ) + fJ].
  - For f = 8% and J = 50%, the jump term is ln(0.96) + 0.04 = −0.0008 per event. At p ≈ 10⁻⁴ per night that is about 10⁻⁷ of growth per night: negligible.
  - Single-name Kelly f* ≈ μ/σ². At a 5 bp/day edge and 2% daily volatility that is 0.0005 / 0.0004 ≈ 125% of equity, so 4% and 8% are about 3% and 6% of Kelly.
  - The ruin condition f < 1/J allows 200% at a 50% jump and 100% at a total loss.

  So Kelly doesn't decide between 4% and 8%; the guardrails do.
- **Drawdown consistency.** To keep "never 10%" safe against a single event at the design jump J, a cap must satisfy **cap ≤ (10% − buffer − current drawdown) ÷ J**. With a 0.5% buffer:

  | Current drawdown | Max cap, J = 50% | Max cap, J = 100% |
  |---|---|---|
  | 0% | 19% | 9.5% |
  | 5% | 9% | 4.5% |
  | 6% | 7% | 3.5% |
  | 7% | 5% | 2.5% |
  | 8% | 3% | 1.5% |
  | 8.9% | 1.2% | 0.6% |

  - A **4%** cap is safe against a 50% gap until a drawdown of about 7.5%, and against a total loss until about 5.5%.
  - An **8%** cap is safe against a 50% gap only until about 5.5%, and against a total loss only until about 1.5%.

  Under the current rules (4% fixed, halt at 9%), a 4% position that loses 50% at an 8.9% drawdown ends at 10.9%. Scaling overnight caps with drawdown is therefore needed **whichever cap is chosen**. Exposure proportional to the cushion above a floor is the structure of drawdown-constrained optimal policies (Grossman–Zhou 1993; not verified).
- **Single-event loss by cap.**

  | Event | 4% cap | 8% cap |
  |---|---|---|
  | 25% gap | 1.0% | 2.0%, the whole daily limit |
  | 28–30% gap (NVIDIA 2008) | 1.1–1.2% | 2.2–2.4% |
  | 49.5% gap (Yahoo 2008) | 2.0% | 4.0%, exactly the KR2.8 bound |
  | 75–80% (biotech bid, Luckin-type fraud) | 3.0–3.2% | 6.0–6.4% |
  | 100% (bank seized after a halt) | 4.0%, at KR2.8 | 8.0%: breaches KR2.8 and nearly uses the whole drawdown budget |

  An 8% cap is consistent with KR2.8 only if total-loss names are excluded or capped separately.
- **The daily loss limit can't stop a gap; it can only react.** The gap is realized at the open. If it already exceeds 2% of the previous close, the rule forces the **whole book flat at the open**, the most expensive time to trade.
  - At a 4% cap, a single name triggers this only on a gap beyond 50%. At 8%, a gap beyond 25% does it.
  - At the mega-cap non-earnings rate above (2 events, about 1.3 per 10,000 nights for ≥20–25%, about half adverse), an 8% book would hit a gap-driven daily stop about once every 4 years. The 95% Poisson interval runs from about once a year to about once in 35 years, and a broader universe would be worse.
  - At 4%, the trigger needs a ≥50% gap, of which the sample had none. That is plausibly an order of magnitude rarer, except in biotech shorts and banks under stress.
- **Why VaR and ES miss it.**
  - With a nightly jump probability p ≈ 10⁻⁴ ≪ 1 − α, a 97.5% or 99% VaR ignores the jump entirely.
  - A 97.5% ES weights it by only p ÷ (1 − α) ≈ 0.4%. A 50% jump on an 8% position then adds about 0.016% to ES.

  Event risk needs a separate scenario or stress limit (in banking terms, a jump-to-default style charge; not verified).

### Gaps
- Not verified, as no access:
  - Liu, Longstaff & Pan (2003, JF), "Dynamic asset allocation with event risk": unhedgeable jumps sharply reduce optimal risky exposure;
  - Aït-Sahalia, Cacho-Diaz & Hurd (2009): closed-form portfolio choice with jumps;
  - Grossman & Zhou (1993): drawdown constraint;
  - MacLean, Thorp & Ziemba: fractional Kelly;
  - Basel FRTB default-risk charge (jump-to-default) for equities;
  - CFA and PRMIA material on stress-loss limits.

## 4. Is the claimed trade-off plausible? Does 4% vs 8% halve the return, what binds, and how much return accrues overnight?

### Takeaway
**No.** Under the goal's other limits, raising the overnight cap from 4% to 8% does not double the return at the planned ~15 concurrent positions:
- With hard limits only, it changes the return by **×1.00–1.25**, because the 2% open-risk budget or the 75% overnight gross binds first.
- With the 0.2%/day volatility target kept, it changes it by **×1.00**.

Doubling to about 10% a year needs about 120% gross (or 4% open risk) and twice the volatility budget. That is a decision to double risk, not a free effect of the per-name cap.

The cap matters a lot only when signals are scarce, at about 8 or fewer concurrent overnight names. Holding overnight itself is valuable: studies place momentum (and reportedly reversal) profits overnight and most other anomalies' profits intraday.

### Cited Findings
- **The goal's own arithmetic.** About 25 round trips a week held about 3 trading days gives about 15 positions open, about 60% gross at about 4% each. GOAL.md says "a book of about 15 such positions moves about 3.2% a year". Decision 1 says 8% "doubles the aim to about 10% a year" — [GOAL.md](/home/user/AIresume/trading/goal/GOAL.md).
- **Lou, Polk & Skouras (JFE 2019, 134:192–213).**
  - Across 14 strategies, "all of the abnormal returns on momentum strategies remarkably occur overnight while the abnormal profits on the other trading strategies we consider occur intraday".
  - The 2019 summary describes profits "either earned entirely overnight (for reversal and a variety of momentum strategies) or entirely intraday", usually with the two components of opposite sign.
  - The effect is stronger for large-cap, high-price stocks, and the spread between the components varies on the order of 2% a month.
  - The authors' explanation: individuals trade at the open, institutions during the day.

  Sources: [LSE Research Online](https://researchonline.lse.ac.uk/id/eprint/119010); [paper PDF](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf); review by [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/). Two sources (search summaries).
- **Cliff, Cooper & Gulen.** Alpha Architect's review says they find that all of the return to holding stocks comes from holding overnight risk — [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/). Secondary; the original was not opened.
- **Bogousslavsky (JFE 2021, 141:172–194).**
  - Size and illiquidity premia show up in the last part of the trading day.
  - Profitability and idiosyncratic-volatility premia build up during the day but tend to lose money overnight.
  - A mispricing factor earns returns during the day but does poorly at the close; the pattern is stronger in the second half of the sample.

  Sources: [SUFE abstract](https://academicnewsletter.sufe.edu.cn/info/355295); [working paper](https://finance.unibocconi.eu/sites/default/files/files/media/attachments/The%2520Cross-Section%2520of%2520Intraday%2520and%2520Overnight%2520Returns_21Dec1620170112151545.pdf).
- **Local data, 2003 to file end** — [computed from local files](/home/user/AIresume/trading/goal/.data-cache/):

  | Stock | Overnight log return a year | Intraday log return a year |
  |---|---|---|
  | GOOG | +33.9% | −9.4% |
  | NVDA | +25.4% | −11.7% |
  | YHOO | +19.9% | −4.7% |
  | MSFT | +1.7% | +8.1% |
  | ORCL | −0.3% | +12.2% |

  This is noisy, but in 3 of the 5 stocks nearly all of the return came overnight.

### Inferences
- **How the book is sized in this analysis.** Every concurrent signal N is held at equal weight. Each position is sized at the tightest of:
  - the overnight cap;
  - 10% intraday;
  - 0.5% stop risk ÷ stop distance d;
  - 75% ÷ N (overnight gross);
  - 2% ÷ (N·d) (open risk).

  Idiosyncratic volatility is 1.29% a day, the figure implied by the goal's 15 × 4% → 0.2%/day. The return ratio equals the size ratio, assuming the same edge per unit of gross. This was computed in this session from GOAL.md's limits.

  | Concurrent names N | Stop distance d | 4% cap: size / gross (binds) | 8% cap: size / gross (binds) | Return 8%÷4%, hard limits only | Return 8%÷4%, 0.2%/day vol target kept |
  |---|---|---|---|---|---|
  | 6 | 2–3.3% | 4.0% / 24% (cap) | 8.0% / 48% (cap) | ×2.00 | ×1.58 |
  | 8 | 2% | 4.0% / 32% (cap) | 8.0% / 64% (cap) | ×2.00 | ×1.37 |
  | 8 | 3.3% | 4.0% / 32% (cap) | 7.5% / 60% (open risk) | ×1.88 | ×1.37 |
  | 10 | 2% | 4.0% / 40% (cap) | 7.5% / 75% (overnight gross) | ×1.88 | ×1.23 |
  | 10 | 3.3% | 4.0% / 40% (cap) | 6.0% / 60% (open risk) | ×1.50 | ×1.23 |
  | 10 | 5% | 4.0% / 40% (cap) | 4.0% / 40% (open risk) | ×1.00 | ×1.00 |
  | **15 (plan)** | 2% | 4.0% / 60% (cap) | 5.0% / 75% (overnight gross) | **×1.25** | **×1.00** |
  | **15 (plan)** | 3.3% | 4.0% / 60% (cap) | 4.0% / 60% (open risk) | **×1.00** | **×1.00** |
  | 15 | 5% | 2.7% / 40% (open risk) | 2.7% / 40% (open risk) | ×1.00 | ×1.00 |
  | 20 | 2–5% | 2.0–3.8% (open risk or gross) | same as 4% | ×1.00 | ×1.00 |

- **The planned book already fills the open-risk budget.** 15 × 4% stays within the 2% open-risk budget only if the average stop is within about 3.3%, or about 0.13% risk per position. So the stated "0.5% at each stop" can only be a per-position maximum. At about 3.3% stops, 8% caps just halve the number of names (15 → 7.5) at the same 60% gross.
- **Concentration raises volatility, not return.** Expected return ≈ gross × edge per unit of gross. Volatility ∝ gross ÷ √N, so fewer, larger positions raise volatility and lower the Sharpe ratio, in line with the fundamental law: IR ∝ IC·√breadth. The goal's 3.2% a year volatility ceiling is set jointly by the 2% open-risk budget, the 75% overnight gross and the number of concurrent signals, not by the 4% cap alone.
- **Where 8% would help.** Only in a signal-scarce book of about 8 or fewer overnight names with the volatility budget raised. Then 8% roughly doubles both return and volatility.
- **Ways to raise return without raising per-name jump loss:**
  - more concurrent names (breadth);
  - overnight gross from 75% toward 100% at 4% caps, which needs about 19–25 names;
  - a larger open-risk budget;
  - more intraday-only trades at up to 10%;
  - broad ETFs, which have smaller jumps, for part of the overnight book.
- **Capital scaling.** The rule "a position ≤ 2% of ADV" makes caps moot for the thinnest names at larger capital: 2% × $20M ADV is $400k. An 8% position hits it once equity exceeds $5M, and a 4% position once equity exceeds $10M.
- **What the overnight evidence means for the decision.** If the signals are momentum- or reversal-type, Lou-Polk-Skouras suggests their profit accrues overnight. Holding overnight should then be kept, and the lever is the number of overnight names, not their size.

### Gaps
- **Not opened:** Kelly & Clark (2011, J. Asset Management), Cliff, Cooper & Gulen (2008), Akbas et al. (2022, JFE) and Barardehi, Bogousslavsky & Muravyev, all on overnight vs intraday returns.
- **Model limitations.** The table assumes equal edge per position and uncorrelated idiosyncratic risk. If signal strength varies widely, concentrating in the best signals could raise edge per unit of gross; that is not quantified.

## 5. Concrete large non-earnings overnight moves in large, liquid stocks, and whether 50% is the right design jump

### Takeaway
Verified in data: Yahoo +49.5% (2008 bid) and NVIDIA −28.0% (2008 warning), both very liquid mega-caps. The 2015–2026 record, from recollection and **not verified this session**, includes many liquid-stock, non-earnings moves:
- **≥50%:** PG&E, Luckin, Silvergate, PacWest and First Republic (down); SVB and Signature total losses after a halt or closure; biotech targets at +70–80%.
- **20–47%:** Super Micro, Centene, Biogen, Activision, Twitter, U.S. Steel, Karuna, AMD and Intel.

So **50% is about right for ordinary operating companies**, too lenient for bank and fragile-financial longs (up to −100%) and for biotech and small/mid healthcare shorts (+50–100%), and harsh for broad ETFs.

### Cited Findings
- **Yahoo, 2008-02-01.** Open 28.68 vs previous close 19.18, +49.5%; the bid was a 62% premium — [local yhoo.csv](/home/user/AIresume/trading/goal/.data-cache/yhoo.csv); [GT-2](/home/user/AIresume/trading/goal/goaltests/gt02_consistency.py).
- **NVIDIA, 2008-07-03.** Open 12.98 vs previous close 18.03, −28.0%, on an unscheduled revenue warning — [local nvda.csv](/home/user/AIresume/trading/goal/.data-cache/nvda.csv); [GT-2](/home/user/AIresume/trading/goal/goaltests/gt02_consistency.py).
- **Yahoo, 2008-05-05.** −19.6% (28.67 → 23.05) on the first trading day after Microsoft withdrew its bid. The cause is my attribution, not verified — [local yhoo.csv](/home/user/AIresume/trading/goal/.data-cache/yhoo.csv).
- **SVB and the 2023 bank failures.** SVB Financial (S&P 500) "fell 60% on 9 March 2023, was halted before the next open and never traded on Nasdaq again". On 13 March 2023, First Republic and Western Alliance "fell 60–75% together" — [GT-2 annotation](/home/user/AIresume/trading/goal/goaltests/gt02_consistency.py). This is the project's record from public sources; single-source this session.
- **No index gap statistics.** The cached S&P 500 index has unreliable opens: 2,004 of 5,030 days open at the previous close — [local sp500.csv](/home/user/AIresume/trading/goal/.data-cache/sp500.csv).

### Inferences
- **Proposed design jumps by type:**
  - broad equity ETFs: about 15–20% (market gaps are already bounded separately by the 15% beta-adjusted net and the 13% stress);
  - sector ETFs: about 25–30%;
  - ordinary operating companies: 50%;
  - small/mid-cap biotech and pharma **shorts**: 100%;
  - **longs** in banks, brokers and other run-prone financials when funding is under stress: 100%.
- **Long/short asymmetry is mostly a sector question.**
  - Longs have a bounded but real total-loss tail, concentrated in financials and fraud cases.
  - Shorts have an unbounded tail. In practice it means takeover gaps of about 15–50% outside biotech and 50–100%+ in biotech, plus squeezes.
  - The goal's short filters (short interest ≤15% of float, ≤5 days to cover, easy-to-borrow) address squeezes, but not takeovers: targets are often low-short-interest names.

### Gaps
**UNVERIFIED candidate events (from model background knowledge; magnitudes approximate, ≈ one-day closes unless noted). Verify before use.**
- **Down, non-earnings:**
  - PG&E −52% (2019-01-14, bankruptcy plan);
  - Luckin Coffee ADR −76% (2020-04-02, fabricated sales);
  - Silvergate −58% (2023-03-02, 10-K delay);
  - SVB −60% (2023-03-09), then halted and seized on 03-10: total loss for holders at the 03-09 close;
  - Signature Bank: closed on Sunday 2023-03-12, total loss;
  - First Republic −62% (2023-03-13);
  - Western Alliance ≈−47% (2023-03-13);
  - PacWest −51% (2023-05-04);
  - New York Community Bancorp ≈−26% (2024-03-01, material weakness; its −38% on 2024-01-31 was earnings);
  - Super Micro −33% (2024-10-31, auditor EY resigned) and ≈−19% (2024-08-28, 10-K delay);
  - Biogen −29% (2019-03-21, aducanumab futility);
  - Novo Nordisk ADR ≈−18 to −20% (2024-12-20, CagriSema data);
  - UnitedHealth ≈−18% (2025-05-13, CEO exit and guidance suspended);
  - Centene ≈−40% (2025-07-02, guidance withdrawn);
  - NVIDIA −17% close and ≈−12% opening gap (2025-01-27, DeepSeek);
  - CrowdStrike ≈−11% (2024-07-19, outage).
- **Up, non-earnings:**
  - Activision +26% (2022-01-18, Microsoft bid, about 45% premium);
  - Twitter +27% (2022-04-04, Musk stake);
  - U.S. Steel ≈+26% (2023-12-18, Nippon Steel, about 40% premium);
  - Splunk ≈+21% (2023-09-21, Cisco);
  - Juniper ≈+22% (2024-01-09, HPE report);
  - Karuna ≈+47% (2023-12-22, BMS, about 53% premium);
  - ImmunoGen ≈+80% (2023-11-30, AbbVie, about 95% premium);
  - Prometheus ≈+70% (2023-04-17, Merck, about 75% premium);
  - Morphic ≈+75% (2024-07-08, Lilly, about 79% premium);
  - Constellation Energy ≈+22% (2024-09-20, Three Mile Island/Microsoft deal);
  - Intel ≈+23% (2025-09-18, NVIDIA investment);
  - AMD ≈+24% (2025-10-06, OpenAI deal);
  - GameStop +93% and +135% (2021-01-26 and 01-27; high short interest, which the goal's filters exclude).
- **Earnings-night counterexamples, excluded by the goal's rule but useful for scale:** Fiserv ≈−44% (2025-10-29), First Republic ≈−49% (2023-04-25), UnitedHealth ≈−22% (2025-04-17).
- **Other unverified background:**
  - SVB lost about $42B of deposits on 2023-03-09 with about $100B queued for 03-10 (Federal Reserve review, April 2023).
  - US market-wide circuit breakers are 7%, 13% and 20%; levels 1 and 2 halt trading for 15 minutes before 15:25.
  - Limit Up-Limit Down bands and news-pending halts stop trading, but stops cannot fill during a halt.
- **Largest overnight gaps in broad ETFs (SPY/QQQ/IWM)** were not obtained; the cached index opens are unreliable.

## 6. Recommendation: 4%, 8%, or another rule?

### Takeaway
**Keep 4% as the default overnight cap for single stocks.** I am about **80% confident** this beats a uniform 8% under the goal's current limits. Refine it into a **tiered stress-loss rule**, about 60–65% confidence that tiers add value:
- **Cap = 2% ÷ design jump by type:**
  - broad ETFs and ETF hedges: up to 8–10%;
  - ordinary stocks, long or short: 4%;
  - small/mid-cap biotech and pharma shorts: 2%, or no overnight shorts there;
  - long positions in run-prone financials under stress: 2%.
- **Drawdown scaling:** overnight caps shrink once drawdown passes about 5–6%, so that drawdown + worst single-event loss stays below 10%. I am about 75% confident this is needed whichever cap is chosen.

Under the other limits, 8% raises return by ×1.00–1.25 at the planned activity, not ×2. A ~10% a year aim needs a larger volatility, open-risk and gross budget spread over more names, not more single-name jump exposure.

### Cited Findings
- **Gap sizes (local sample).** Non-earnings gaps of ≥25%, the size that makes an 8% position breach the 2% daily limit, happened about 1.3 times per 10,000 stock-nights (2 events). Counting all nights it was 2.0 (3 events). The sample had no gap of ≥50% in 59 stock-years. The largest non-earnings gap was +49.5% (Yahoo, 2008) — [computed from local files](/home/user/AIresume/trading/goal/.data-cache/).
- **A professional reference point.** One market-neutral fund caps single longs and shorts at 5% of net assets at entry — [SEC 497K](https://www.sec.gov/Archives/edgar/data/787623/000093041310005104/c63023_497k.htm). Single-source.
- **Overnight is where momentum and reversal profits accrue, so keep overnight capacity and spread it** — [LSE](https://researchonline.lse.ac.uk/id/eprint/119010); [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/).
- **The goal's limits that bind before the per-name cap:** 2% open risk, 75% overnight gross, gross ≤100%, a 0.2%/day volatility budget, and a single jump event ≤4% (KR2.8) — [GOAL.md](/home/user/AIresume/trading/goal/GOAL.md).

### Inferences
- **For 4% (and against 8%):**
  1. The return case for 8% disappears at about 15 names: ×1.00, or ×1.25 at most.
  2. At 8%, an adverse gap of ≥25% hits the 2% daily limit and forces the whole book flat at the open. At mega-cap rates that happens every few years; at 4% it takes a gap beyond 50%.
  3. A total loss (SVB or Signature type) costs 8% at an 8% cap, which breaches KR2.8 and nearly uses up the 10% drawdown budget. At 4% it costs 4%, exactly the KR2.8 bound.
  4. The one documented professional cap found is 5% at entry.
  5. Concentration lowers the Sharpe ratio at the same gross (fundamental law).
- **Against 4% (and for a higher cap):**
  1. If the real strategy turns out signal-scarce (about 8 or fewer overnight names), 8% with a larger volatility budget could add 37–100% to return.
  2. Mega-cap, non-biotech, non-bank stocks rarely gap 50% overnight (none did in the local sample). A 5–6% cap for them would mostly cost a rare overshoot of the daily limit.
  3. Concentrating in the strongest signals may raise edge per unit of gross, which the model above does not capture.
  4. The daily limit is a trigger, not a guarantee. The owner could accept a "single event ≤4%" bound in place of the 2% daily limit for gap days.
- **Rule text to consider:**
  - overnight cap per name = min(4%, 2% ÷ J_type, (9.5% − drawdown) ÷ J_type);
  - J_type is 15–20% for broad ETFs, 50% for operating companies, and 100% for small/mid biotech and pharma shorts and for fragile-financial longs;
  - keep the 8% industry cap;
  - keep the expected takeover drag (≈0.1–0.45% a year at ~30% short gross) in the cost budget, and backtest on survivor-free data.
- **What would change the recommendation:**
  - point-in-time, survivor-free gap statistics showing non-earnings adverse gaps of ≥25% below about 1 per 100 stock-years in large caps (that would support 6% for large caps);
  - evidence that the strategy runs fewer than about 8 concurrent overnight names;
  - the owner choosing a higher volatility budget explicitly.

### Gaps
- **The confidence figures are judgment**, based mostly on arithmetic on the goal's limits. The external evidence is thin because web access failed this session.
- **A follow-up verification pass should check:**
  - the Section 5 event list;
  - takeover premium statistics and the annual bid rate;
  - market-neutral and long/short prospectus caps;
  - '40 Act and UCITS rules;
  - Liu-Longstaff-Pan and Grossman-Zhou.

  None of these changes the core mechanism result, which follows from the goal's own limits.

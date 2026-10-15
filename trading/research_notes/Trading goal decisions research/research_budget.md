# Research budget for a one-history strategy program: counting trials, correcting for multiple tests, and setting the variant budget, time budget and stopping rule (as of 2026-10-15)

> **Method and limits.** I ran 31 web searches. Then the turn's shared web-search allowance ran out. Direct downloads of papers were refused (egress proxy HTTP 403 for people.duke.edu, ssrn.com, arxiv.org, nber.org, davidhbailey.com, wikipedia.org and others; WebFetch failed on DNS). **I did not open the full text of any paper.** Facts below come from abstracts, publisher and repository listings, and search-result summaries and snippets. I cross-checked them across results. "(single-source)" marks a fact I saw in only one source. Where several sources are secondary summaries of one paper, the cross-check is a listing of the paper plus an independent summary, not two readings of the full text.
>
> Every number labelled **computed** is my own work (Python standard library plus numpy). The formulas and inputs are shown in section 2. The scripts are `dsr_budget.py`, `dsr_addendum.py` and `undercount.py` in `/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/calc/`. That folder belongs to this session and may not persist.
>
> **Validation.** My implementation reproduces two published anchors:
> - the DSR paper's worked example (DSR = 0.9004);
> - the minimum backtest length (MinBTL) claim that 5 years of data supports 45 trials (f(45)² = 5.00 years).
>
> **Dates.** The core papers date from 2014 to 2023 and are older facts. The searches surfaced nothing that replaces them as of 2026-10-15.

---

## Overall question: is the current budget right? (≤10 variants in total, 9 months, ≤4 cycles of ≤3 variants, every run counts, a stop is final for this history)

### Takeaway
The current budget is safe against false discoveries. It is too small to give the program a reasonable chance of finding a real edge under its own 5% prior:
- **10 distinct ideas** (one counted run each): about a 26–38% chance of finding a real net Sharpe 1.5 edge.
- **10 runs spent as parameter variants of 3–4 ideas:** about 4–18%.
- **False passes:** below 1% in every case.

**Recommendation:** about **30 counted trials** (acceptable range 20–50), spent on **at least 10–15 distinct ideas**, with these rules:
- count trials cumulatively, with N = max(cumulative count, 10);
- fix the variance convention (V) and the Newey-West effective sample size (T_eff) in advance;
- keep a **final, pre-committed budget** for this history.

At 30 trials the DSR hurdle rises only from Sharpe ≈1.04 to ≈1.21, and the chance of finding a real edge roughly doubles to about 52–72%.

The owner should know that "restart only on data after the last G1" means about **9.5 years** before a fresh 2,400-day G1 is possible. A stop is therefore in effect the end of the program for this design.

No source found sets a research time budget. Treat 9 months as staged go/no-go checkpoints with a hard end, not as an evidence-based number.

**Confidence:**
- moderate that 10 is too few;
- moderate on about 30 as the order of magnitude;
- low on the exact number and on the time budget.

### Cited Findings
- The DSR tests the best Sharpe ratio against the expected maximum Sharpe ratio of N unskilled trials. N is the *effective number of independent* trials, and V is the variance of the trials' Sharpe estimates. — [Wikipedia: Deflated Sharpe ratio](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio); [LuxAlgo: DSR](https://www.luxalgo.com/library/concept/deflated-sharpe-ratio.md); [endgame-ml DSR source code](https://endgame-ml.readthedocs.io/en/latest/_modules/endgame/utils/sharpe.html)
- With 5 years of data, no more than 45 independent configurations should be tried. At 45 trials the expected best in-sample Sharpe is 1 while the expected out-of-sample Sharpe is 0. — [Bailey, Borwein, López de Prado, Zhu 2014, Notices of the AMS](https://www.ams.org/notices/201405/rnoti-p458.pdf); [preprint (carmamaths.org)](https://carmamaths.org/resources/jon/backtest.pdf); [Bailey talk slides](https://www.davidhbailey.com/dhbtalks/battle-quants.pdf)
- Harvey, Liu and Zhu set a t-ratio hurdle of 3.0 for a new factor, not 2.0. — [NBER w20592](https://www.nber.org/papers/w20592); [SSRN 2513152](https://papers.ssrn.com/abstract=2513152)
- Harvey and Liu (2020) set test thresholds that weigh missed discoveries against false ones. They show a standard method (Fama-French 2010) lacks the power to find outperforming funds. — [Journal of Finance (Wiley)](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12951); [arXiv 2006.04269](https://arxiv.org/abs/2006.04269)
- Arnott, Harvey and Markowitz say to track every model and variable tried, and that "iterated out-of-sample is not out-of-sample". — [Duke PDF of the paper](https://people.duke.edu/~charvey/Research/Published_Papers/P138_A_backtesting_protocol.pdf); [Hudson & Thames summary](https://hudsonthames.org/experimental-design-and-common-pitfalls-of-machine-learning-in-finance/)
- In the Quantopian study, backtest Sharpe predicted out-of-sample Sharpe with R² < 0.025, and more backtesting widened the gap between in-sample and out-of-sample results. — [Quantpedia summary](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/); [CXO Advisory summary](https://www.cxoadvisory.com/big-ideas/in-sample-vs-out-of-sample-performance-of-888-trading-strategies)

### Inferences
**Recommendation.** These are my judgments, built on the computations in section 2.

1. **Variant budget: raise the counted-trial cap from 10 to about 30 (range 20–50).**
   - Evidence *for* (computed: T = 2,400 days; V = the null sampling variance; normal returns; independent ideas; 5% prior; real edge has a true net Sharpe of 1.5):

     | Counted trials N | Sharpe needed for DSR ≥ 0.95 | Chance of finding a real edge | Chance of a false pass |
     |---|---|---|---|
     | 10 | 1.04 | 0.38 | <0.6% |
     | 20 | 1.15 | 0.58 | <0.6% |
     | 30 | 1.21 | 0.71 | <0.6% |
     | 50 | 1.27 | 0.86 | <0.6% |

     - The share of passes that are real (positive predictive value) is ≥98.7% throughout.
     - When every trial is counted, the false-pass rate *falls* as N rises.
     - The gain holds under every sensitivity I ran: a lower prior, a weaker true Sharpe, a smaller T_eff, and a different V.
   - Evidence *against*:
     - The Quantopian evidence of real-world overfitting beyond counted trials.
     - The Arnott-Harvey-Markowitz contamination point.
     - The likely fall in the per-idea prior as the best ideas are used first. This is unquantified; no source found.
     - Power per real edge falls: 0.92 at N = 10, 0.82 at N = 30, 0.76 at N = 50.
     - The supply of distinct, well-founded ideas may bind long before 30.
   - Why not 100 or more:
     - diminishing returns;
     - power per real edge falls to 0.67 at N = 100;
     - more temptation to leave trials uncounted.
2. **Count ideas, not only runs.** The 5% prior applies per candidate idea. Under the current cycle structure (≤3 variants per cycle), 10 runs are about 3–4 ideas.
   - That leaves only a 14–18% chance that a real idea is among them, even before the gate is applied.
   - Parameterize each idea once or twice, from economic reasoning fixed before the G1 run.
3. **Fix V and T_eff before any G1 run.** These two drive power more than N does.
   - **T_eff.** If Newey-West halves the effective sample to 1,200, power at N = 10 falls from 0.92 to 0.52, and the chance of finding a real edge from 0.38 to 0.23.
   - **V.**
     - If V is the sample variance across trials, a real edge inflates its own hurdle. Power at N = 10 falls to about 0.61, and parameter variants of a real idea make this worse.
     - Suggested convention: V = max(the null sampling variance at T_eff, the cross-trial variance excluding the candidate). Computed results: a 36% chance of finding a real edge at N = 10 and 66% at N = 30; a global-null false-pass rate of 0.47% and 0.25%.
     - Excluding the candidate departs from the paper's literal definition and must be an explicit owner decision.
4. **Keep the floor N = max(trials, 10).**
   - It makes the first 10 trials free in hurdle terms, so a budget below 10 wastes draws.
   - It gives margin for trials that were run but not counted. With 10 counted, the global-null false-pass rate stays below 5% even if about 50 independent trials were really run (3.2%).
5. **Stopping rule: keep a finite budget that is final for this history.**
   - The literature permits continuing on the same history if trials are counted cumulatively. But researcher memory and adaptive design leak information that counting cannot capture (Arnott-Harvey-Markowitz; Dwork et al.).
   - Restate the rule as "the budget is final": no top-ups after seeing results.
   - Make the restart path explicit. Either a stop ends the program for about 9.5 years, or define a restart on genuinely new data (another market, or newly obtained older history) with its own pre-committed budget.
6. **Time budget: keep 9 months as three staged checkpoints with a pre-committed hard end** (≤12 months including at most one pre-registered extension). Extend only on process criteria, never on near-miss G1 results. Low confidence; no source found.

**What would change the recommendation:**
- the owner's estimate of how fast distinct, well-founded ideas arrive;
- a measured T_eff and the cross-trial correlation of the planned strategies;
- whether the 5% prior is per idea or per run;
- the cost of a false deployment versus a missed edge. Harvey and Liu (2020) argue both errors must be weighed.

### Gaps
- No source found on research **time** budgets or kill dates for strategy searches (section 5).
- No Man AHL or Two Sigma publication on trial budgets found.
- Full texts not opened. Details such as Harvey and Liu's handling of correlation among tests, and the exact ONC procedure, are unverified.
- The program spec as described does not say how V is computed or how T_eff enters the DSR. The answer depends materially on both.

---

## 1. What do the key papers say about what counts as a trial, how to count correlated trials, and how many trials are acceptable?

### Takeaway
The sources agree on five points:
- Every configuration evaluated on the data is a trial: failures, parameter changes and variables tried all count. All trials must be recorded and reported.
- Correlated trials should be collapsed into an effective number of independent trials (López de Prado: clustering/ONC; also hierarchical clustering or eigenvalue methods).
- The cross-trial variance V carries the remaining dependence.
- None gives a universal maximum. The acceptable number depends on the length of the sample and the target Sharpe (MinBTL: 5 years supports about 45 independent trials before the expected best null Sharpe reaches 1.0).
- Harvey, Liu and Zhu's hurdle for the whole field is t > 3.0.

### Cited Findings
**Harvey, Liu & Zhu (2016, RFS), "…and the Cross-Section of Expected Returns" (older fact)**
- A new factor should clear a t-ratio above 3.0. The usual t > 2.0 "makes no economic or statistical sense" given extensive data mining. "Most claimed research findings in financial economics are likely false." — [NBER w20592](https://www.nber.org/papers/w20592); [SSRN 2513152](https://papers.ssrn.com/abstract=2513152); [Marginal Revolution 2014](https://marginalrevolution.com/marginalrevolution/2014/10/and-the-cross-section-of-expected-returns.html); [CXO: measuring snooping bias](https://www.cxoadvisory.com/big-ideas/measuring-investment-strategy-snooping-bias/)
- Counterpoint from a later critique: a hurdle of 3.39 corresponds to a 1% false discovery rate in the paper's Figure 3, and its preferred estimate implies a hurdle of 2.27 at a 5% false discovery rate. The critique argues "most findings false" conflicts with the paper's own estimates. — [arXiv 2206.15365](https://arxiv.org/pdf/2206.15365) (single-source; the critic's reading)

**Harvey & Liu (2015, JPM 41(1):13–28), "Backtesting" (older fact)**
- The paper gives a method to compute a "haircut" for any reported Sharpe ratio and a "profit hurdle" a strategy must clear to count as significant. — [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF); [quantstrat profitHurdle docs](https://rdrr.io/github/braverock/quantstrat/man/profitHurdle.html)
- The common 50% haircut rule of thumb is "a serious mistake". The haircut is nonlinear: the highest Sharpe ratios are only moderately penalized and marginal ones heavily. — [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF); [Advisor Perspectives 2016](https://www.advisorperspectives.com/articles/2016/04/28/special-edition-can-you-trust-investment-research)
- For annualized Sharpe below 0.4 the haircut is almost always above 50%. Above 1.0 it is at most about 25%. — [CXO: Navigating the data snooping icebergs](https://www.cxoadvisory.com/big-ideas/navigating-the-data-snooping-icebergs/) (single-source)
- The adjustment is "highly affected by the number of trials, and the method of adjustment". The paper applies three adjustment approaches to E/P, momentum and betting-against-beta. — [CXO: measuring snooping bias](https://www.cxoadvisory.com/big-ideas/measuring-investment-strategy-snooping-bias/); [quantstrat Haircut_SR code](https://rdrr.io/github/braverock/quantstrat/src/sandbox/Harvey_Liu_Backtesting/50a170e4e37da951ea1192888418c82a/Haircut_SR%20with%20sample_random_multests.R)

**Harvey & Liu (2020, Journal of Finance 75(5)), "False (and Missed) Discoveries in Financial Economics" (older fact)**
- A double bootstrap sets a t-statistic hurdle for a chosen false discovery rate (e.g., 5%). It also sets a hurdle for an acceptable ratio of misses to false discoveries, so the two errors can be weighted differently. — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12951); [arXiv 2006.04269](https://arxiv.org/abs/2006.04269); [SSRN 3073799](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3073799)
- The Fama-French (2010) method lacks the power to detect outperforming funds. It may declare zero alpha for all funds even when a significant fraction outperform. — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12951); [arXiv 2006.04269](https://arxiv.org/abs/2006.04269)

**Bailey & López de Prado (2014, JPM 40(5):94–107), "The Deflated Sharpe Ratio" (older fact)**
- The DSR is the probabilistic Sharpe ratio evaluated at a hurdle equal to the expected maximum Sharpe of N unskilled trials. — [Wikipedia](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio); [LuxAlgo](https://www.luxalgo.com/library/concept/deflated-sharpe-ratio.md)
- The hurdle is SR* = √V·[(1−γ)Φ⁻¹(1−1/N) + γΦ⁻¹(1−1/(N·e))], where γ is the Euler-Mascheroni constant. — [LuxAlgo](https://www.luxalgo.com/library/concept/deflated-sharpe-ratio.md); [endgame-ml code](https://endgame-ml.readthedocs.io/en/latest/_modules/endgame/utils/sharpe.html)
- The DSR corrects for selection bias under multiple testing and for non-normal returns. — [DSR paper PDF (listing)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf); [Wikipedia](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio)
- N is the effective number of independent trials, not the raw count. It can be estimated by clustering (hierarchical clustering gives a conservative lower bound; ONC) or from the eigenvalues of the correlation matrix. — [Wikipedia](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio); [CAIA summary of López de Prado & Lewis](https://caia.org/node/5858)
- V is the cross-sectional variance of the trials' Sharpe estimates, and more dispersion raises the hurdle. — [search listing of the DSR paper](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf); [interactiveml.org close reading](https://interactiveml.org/blog/deflated-sharpe-ratio)
- The paper's worked example: best annualized Sharpe 2.5 over 1,250 daily observations, N = 100, V = 0.5, skewness −3, kurtosis 10. The strategy is rejected at 95%; the blog says "rejected at N ≥ 88". — [interactiveml.org](https://interactiveml.org/blog/deflated-sharpe-ratio) (single-source; see the conflict noted under Inferences)
- The expected maximum grows roughly with √(log N), and treating 275 correlated variants as 275 independent trials is too harsh. — [quantt.co.uk](https://www.quantt.co.uk/resources/sharpe-ratio-of-pure-noise) (single-source)
- An implementation docstring reads "DSR < 0.95 … may be a statistical fluke". — [endgame-ml](https://endgame-ml.readthedocs.io/en/latest/_modules/endgame/utils/sharpe.html) (single-source; I could not confirm that the paper prescribes 0.95)

**Bailey, Borwein, López de Prado & Zhu (2014, Notices of the AMS; PBO paper 2017, J. Computational Finance 20(4)) (older facts)**
- Minimum backtest length: "if only five years of data are available, no more than forty-five independent model configurations should be tried". At that N the expected best in-sample Sharpe is 1 while the expected out-of-sample Sharpe is 0. — [Notices of the AMS](https://www.ams.org/notices/201405/rnoti-p458.pdf); [carmamaths preprint](https://carmamaths.org/resources/jon/backtest.pdf); [Bailey talk](https://www.davidhbailey.com/dhbtalks/battle-quants.pdf); [EurekAlert](https://www.eurekalert.org/news-releases/817304)
- A backtest that omits the number of trials cannot be assessed for overfitting. "Not reporting the number of trials involved in identifying a successful backtest is a similar kind of fraud." — [Notices of the AMS](https://www.ams.org/notices/201405/rnoti-p458.pdf); [mathinvestor.org FAQ](https://mathinvestor.org/2014/04/faqs-on-backtest-overfitting/)
- Standard hold-out methods "tend to be unreliable and inaccurate" for investment backtests. Combinatorially symmetric cross-validation (CSCV) is a model-free estimator of the probability of backtest overfitting (PBO) with small errors. — [Risk.net (JCF)](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting); [WMU ScholarWorks](https://scholarworks.wmich.edu/math_pubs/42); [CRAN pbo](https://packages.oit.ncsu.edu/cran/web/packages/pbo/readme/README.html)
- The probability of selecting an overfit strategy grows rapidly with the number of trials. — [mathinvestor.org FAQ](https://mathinvestor.org/2014/04/faqs-on-backtest-overfitting/) (single-source as summarized)

**López de Prado (2018 *Advances in Financial Machine Learning*; 2019 JFDS 1(1):99–110) and López de Prado & Lewis (2019, Quantitative Finance 19(9):1555–1565) (older facts)**
- "Backtesting is not a research tool. Feature importance is." — [GitHub AFML study notes](https://github.com/blazecolby/Financial-Machine-Learning); [book table of contents (Lehmanns)](https://www.lehmanns.de/isbn/978-1-119-48208-6)
- Most published backtests do not report how many trials were run, and journals often do not know how many experiments a researcher ran. — [IAQF event summary](https://iaqf.org/event-813217); [Benefits Canada](https://benefitscanada.com/tag/backtesting)
- The 2019 paper reduces selection bias to two quantities: the number of essentially independent trials and the variance across them. It urges journals and investors to require reported performance to include the multiple-testing-adjusted false-positive probability. It notes most papers and proposals don't report the number of trials. — [JFDS](https://jfds.pm-research.com/content/1/1/99.short); [Semantic Scholar](https://www.semanticscholar.org/paper/A-Data-Science-Solution-to-the-Multiple-Testing-in-Prado/2a56cd3d9b611b320a26980c05f21e4bfaca4484); [2018 working version](https://lncohn.com/finance/Prado-APracticalSolutionToMultiTestingCrisis.pdf)
- López de Prado & Lewis use an unsupervised algorithm that clusters trials into correlation clusters to estimate the number of effectively uncorrelated trials. The estimate feeds the familywise false-positive probability. The method does not assume normal returns or a constant average correlation. — [RePEc (QF 2019)](https://ideas.repec.org/a/taf/quantf/v19y2019i9p1555-1565.html); [CAIA](https://caia.org/node/5858); [SSRN 3167017 mirror](https://smallake.kr/wp-content/uploads/2020/04/SSRN-id3167017.pdf)
- The "False Strategy Theorem" (Bailey & López de Prado, American Mathematical Monthly) gives the expected maximum Sharpe as a function of N, so no fixed Sharpe threshold works regardless of N. — [quantresearch.org publications list](https://quantresearch.org/Publications.htm) (single-source, via search summary)

**Arnott, Harvey & Markowitz (2019, JFDS 1(1):64–74), "A Backtesting Protocol in the Era of Machine Learning" (older fact)**
- The protocol asks:
  - whether there is an economic foundation that predates the research;
  - whether the researcher tracked every model and variable tried, successful or not;
  - whether the researcher is aware of multiple testing;
  - for an ex-ante hypothesis and how many variables and combinations were tried.
  — [Hudson & Thames](https://hudsonthames.org/experimental-design-and-common-pitfalls-of-machine-learning-in-finance/); [Alpha Architect](https://alphaarchitect.com/protocol-to-prevent-quants-gone-wild/); [SSRN 3275654](https://papers.ssrn.com/abstract=3275654)
- Document all trials, and define samples and transformations in advance. — [Palomar slides (secondary)](https://portfoliooptimizationbook.com/slides/slides-backtesting.pdf); [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P138_A_backtesting_protocol.pdf)
- "Iterated out-of-sample is not out-of-sample": fixing a model after it fails out of sample and retesting it is overfitting. A strong research culture reduces, but cannot remove, the winner's curse. — [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P138_A_backtesting_protocol.pdf); [Hudson & Thames](https://hudsonthames.org/experimental-design-and-common-pitfalls-of-machine-learning-in-finance/)

### Inferences
- **The program's counting rule matches the strictest reading** ("every run on the history counts, parameter changes included"; supported by Arnott-Harvey-Markowitz, Bailey et al. and López de Prado). I would also count, as an extension that should be pre-registered:
  - reruns after a bug fix, unless the bug was found by a test independent of G1 output (bug hunting prompted by results is a selection channel);
  - runs on sub-periods of the history;
  - runs generated by automated agents;
  - exploratory analyses that look at forward returns on the history ("every model and variable tried").

  Robustness checks that can only reject a fixed candidate are not trials. Examples: the cost-stress test and the half-sample Sharpe check.
- **How correlation enters the DSR** (my derivation): correlation enters twice, through N and through V.
  - Take null trials with equal pairwise correlation ρ. In standard-error units, Sᵢ = √ρ·Z₀ + √(1−ρ)·Zᵢ.
  - Then E[max] = √(1−ρ)·E[max Zᵢ] = (cross-sectional s.d.) × f(N).
  - So the raw count N combined with the sample V already credits correlation through a smaller V. Clustering (ONC) also cuts N. Raw N with the null V is the most conservative pairing.
- **Use the Bailey–López de Prado approximation, not √(2 ln N).** The bound √(2 ln N) is asymptotic and overstates the expected maximum at small N. Computed values of E[max of N standard normals]:

  | N | √(2 ln N) | Exact | Bailey–López de Prado formula |
  |---|---|---|---|
  | 10 | 2.15 | 1.54 | 1.57 |
  | 100 | 3.03 | 2.51 | 2.53 |

  The formula is slightly conservative.
- **How many trials are acceptable?** No fixed number. By the MinBTL formula, years ≈ f(N)²/E[max SR]². This reproduces exactly: f(45)² = 5.00 years. Computed for the program's 2,400-day window (s.e. 0.324):

  | Expected best null annual Sharpe | Independent trials needed |
  |---|---|
  | 0.5 | ≈9 |
  | 0.75 | ≈55 |
  | 1.0 (the program's floor) | ≈558 |

  So overfitting in the MinBTL sense does not bind at 10–50 trials. Power and the supply of ideas do (section 2).
- **Conflict.** The blog says the DSR paper's example is "rejected at N ≥ 88". My implementation reproduces the example's DSR of 0.9004 at N = 100 (with 250 trading days a year), but crosses below 0.95 at N ≥ 46–47 and below 0.90 at N ≥ 100–101. I cannot reconcile the blog's 88 without the paper.

### Gaps
- Full texts were not read. I could not verify:
  - whether Harvey and Liu (2015) assume an average correlation among tests (I believe they model it; unverified);
  - Harvey, Liu and Zhu's count of 316 factors (background knowledge; unverified);
  - whether the DSR paper prescribes 0.95;
  - whether López de Prado (2019) computes V across cluster-level Sharpe ratios (background knowledge; unverified);
  - the exact wording in *Advances in Financial Machine Learning* about recording all trials (and the "drinking and driving" analogy).

---

## 2. Quantified: how the Sharpe needed for DSR ≥ 0.95 rises with N at 2,400 daily observations, the power to detect a true Sharpe of 1.5, and whether 10 is too few

### Takeaway
At T = 2,400 daily observations, the standard error of an annualized Sharpe ratio under the null is 0.324.
- **Hurdle.** The observed net Sharpe needed for DSR ≥ 0.95 rises only from 1.04 (N = 10) to 1.15 (20), 1.27 (50) and 1.35 (100).
- **Power.** Power for a true Sharpe of 1.5 falls more gently: 0.92, 0.86, 0.76, 0.67.
- **Program success.** Under the 5% prior, the chance of finding a real edge rises much faster than power falls: 0.38, 0.58, 0.86, 0.97 for N = 10, 20, 50, 100.
- **False passes** stay below 0.6%. The DSR ≥ 0.95 gate is far stricter than a 5% familywise test: about 0.6% at N = 10.

**10 is too few** if the trials are distinct ideas, and far too few if they are parameter variants. The biggest threats to power are the Newey-West T_eff and the choice of V, not N.

### Cited Findings
- The DSR formula and the expected-maximum formula. — [Wikipedia](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio); [LuxAlgo](https://www.luxalgo.com/library/concept/deflated-sharpe-ratio.md); [endgame-ml](https://endgame-ml.readthedocs.io/en/latest/_modules/endgame/utils/sharpe.html)
- The DSR corrects for non-normality (skewness, kurtosis). — [Wikipedia](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio); [DSR paper listing](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- MinBTL anchor: 5 years supports 45 trials (used to validate my code). — [Notices of the AMS](https://www.ams.org/notices/201405/rnoti-p458.pdf); [carmamaths preprint](https://carmamaths.org/resources/jon/backtest.pdf)
- DSR worked-example inputs (used to validate my code). — [interactiveml.org](https://interactiveml.org/blog/deflated-sharpe-ratio) (single-source)
- Harvey, Liu and Zhu's t > 3.0 hurdle (used for comparison). — [NBER w20592](https://www.nber.org/papers/w20592); [SSRN 2513152](https://papers.ssrn.com/abstract=2513152)

### Inferences
All results in this section are **computed**. The formulas and inputs are given so they can be reproduced.

**Formulas**
- f(N) = (1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e)), with γ = 0.5772. f(1) = 0.
- SR0_ann = √V_ann · f(N), with N = max(counted trials, 10) as in the program.
- DSR = Φ( (ŝ − s₀)·√(T−1) / √(1 − γ₃·ŝ + (γ₄−1)/4·ŝ²) ), with ŝ = SR̂_ann/√252 and s₀ = SR0_ann/√252 (daily units). γ₃ is skewness and γ₄ is non-excess kurtosis.
- The required Sharpe solves DSR = 0.95, by bisection.
- Sampling s.e. of the annual Sharpe at a true value SR: √252·√((1 − γ₃·s + (γ₄−1)/4·s²)/(T−1)), with s = SR/√252.
- Power = 1 − Φ((SR_req − SR_true)/s.e.(SR_true)).

**Inputs**
- T = 2,400, plus T_eff = 1,800, 1,200 and 800 as sensitivities.
- 252 trading days a year.
- The baseline uses the null V: V_ann = 252/(T−1), so s.e. = 0.3241.
- (skewness, kurtosis) = (0, 3), (−0.5, 6) and (−1, 10).

**Validation**
- The DSR paper's example inputs give DSR = 0.9004.
- f(45)² = 5.00 years.

**A. Hurdle and power by N** (T = 2,400, null V, normal returns unless stated)

| N | f(N) | SR0 (annual) | Sharpe needed: normal | skew −0.5, kurt 6 | skew −1, kurt 10 | Power at true SR 1.0 | at 1.25 | at 1.5 | at 2.0 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 0.533 | 0.538 | 0.543 | 0.925 | 0.986 | 0.999 | 1.000 |
| 5 | 1.193 | 0.387 | 0.920 | 0.928 | 0.937 | 0.597 | 0.845 | 0.963 | 1.000 |
| **10** | 1.575 | 0.510 | **1.044** | 1.054 | 1.064 | 0.446 | 0.737 | **0.920** | 0.998 |
| 15 | 1.771 | 0.574 | 1.108 | 1.118 | 1.129 | 0.370 | 0.670 | 0.886 | 0.997 |
| **20** | 1.901 | 0.616 | **1.150** | 1.161 | 1.172 | 0.322 | 0.621 | **0.859** | 0.996 |
| 30 | 2.073 | 0.672 | 1.206 | 1.217 | 1.229 | 0.263 | 0.554 | 0.817 | 0.993 |
| **50** | 2.276 | 0.738 | **1.272** | 1.284 | 1.296 | 0.201 | 0.473 | **0.759** | 0.987 |
| **100** | 2.531 | 0.820 | **1.354** | 1.367 | 1.380 | 0.137 | 0.374 | **0.673** | 0.976 |
| 1000 | 3.255 | 1.055 | 1.589 | 1.605 | 1.621 | 0.035 | 0.148 | 0.392 | 0.896 |

- Non-normality at these daily Sharpe levels adds only 0.01–0.03 to the hurdle. Power at a true Sharpe of 1.5 with skew −1 and kurtosis 10: 0.899 (N = 10), 0.831 (20), 0.786 (30), 0.724 (50), 0.637 (100).
- At N = 10 the DSR hurdle (1.044) already exceeds the program's net Sharpe ≥ 1.0 floor. With the null V, the floor never binds. It binds only if V is small, e.g. with highly correlated trials.
- The half-sample check (each half ≥ 0.25) barely binds:
  - true Sharpe 1.5: P(either 1,200-day half < 0.25) ≈ 0.65%;
  - true Sharpe 1.0: ≈ 10%.

**B. Newey-West T_eff dominates** (null V at T_eff): Sharpe needed / power at a true Sharpe of 1.5

| T_eff | s.e. | N = 10 | N = 20 | N = 50 | N = 100 |
|---|---|---|---|---|---|
| 2,400 | 0.324 | 1.04 / 0.92 | 1.15 / 0.86 | 1.27 / 0.76 | 1.35 / 0.67 |
| 1,800 | 0.374 | 1.21 / 0.78 | 1.33 / 0.68 | 1.47 / 0.53 | 1.56 / 0.43 |
| 1,200 | 0.458 | 1.48 / 0.52 | 1.63 / 0.39 | 1.80 / 0.26 | 1.92 / 0.18 |
| 800 | 0.562 | 1.81 / 0.29 | 1.99 / 0.19 | 2.21 / 0.10 | 2.35 / 0.07 |

Halving T_eff costs more power than going from 10 to 100 trials. Multi-day holding periods (up to 5 days) make serial correlation in daily P&L likely, so measure T_eff early.

**C. The V convention matters as much as N.** Cross-trial s.d. of annual Sharpe estimates: SR0 / Sharpe needed / power at 1.5

| Cross-trial s.d. | N = 10 | N = 50 |
|---|---|---|
| 0.145 (null × √0.2; e.g. trials with pairwise correlation 0.8) | 0.23 / 0.76 / 0.99 | 0.33 / 0.86 / 0.97 |
| 0.324 (null) | 0.51 / 1.04 / 0.92 | 0.74 / 1.27 / 0.76 |
| 0.45 | 0.71 / 1.24 / 0.79 | 1.02 / 1.56 / 0.43 |
| 0.55 | 0.87 / 1.40 / 0.62 | 1.25 / 1.79 / 0.19 |
| 0.75 | 1.18 / 1.72 / 0.25 | 1.71 / 2.24 / 0.01 |

**A real edge raises its own hurdle under the sample V.** With one true-Sharpe-1.5 trial among N nulls, the expected cross-trial s.d. is 0.555 (N = 10), 0.460 (20), 0.386 (50) and 0.357 (100). The hurdle then sits at about 1.41 for every N from 10 to 50, and power at 1.5 is about 0.61. Under the sample V, adding trials barely raises the bar for a strong strategy.

**D. The DSR ≥ 0.95 gate is very conservative as a familywise test** (global null, independent trials, null V)

| N | Threshold z* = f(N) + 1.645 | Equivalent annual Sharpe | False-pass probability | Bonferroni at 5% familywise error: z / annual Sharpe |
|---|---|---|---|---|
| 10 | 3.22 | 1.04 | 0.64% | 2.58 / 0.84 |
| 20 | 3.55 | 1.15 | 0.39% | 2.81 / 0.91 |
| 50 | 3.92 | 1.27 | 0.22% | 3.09 / 1.00 |
| 100 | 4.18 | 1.35 | 0.15% | 3.29 / 1.07 |

- The false-pass probability is 1 − Φ(z*)^N.
- Harvey, Liu and Zhu's t = 3.0 corresponds to an annual Sharpe of 0.97 at T = 2,400. The gate at N = 10 (z ≈ 3.22) is already stricter.
- **Robustness to trials run but not counted:**

  | N counted | N actually run | False-pass probability |
  |---|---|---|
  | 10 | 20 | 1.3% |
  | 10 | 50 | 3.2% |
  | 10 | 100 | 6.2% |
  | 30 | 100 | 1.0% |
  | 30 | 200 | 2.0% |

  A higher counted N buys margin against uncounted search.

**E. Program-level Monte Carlo**
- Model:
  - each trial is an independent idea, real with probability π = 0.05 (true Sharpe 1.5) and otherwise Sharpe 0;
  - the Sharpe estimate is normal with the s.e. above;
  - a trial passes if DSR ≥ 0.95 with N = max(N, 10);
  - 200,000 replications.

| N | Null V: P(find real edge) | Null V: P(any false pass) | Null V: share of passes that are real | Sample V: P(find) | Sample V: P(false) | P(a real idea exists) |
|---|---|---|---|---|---|---|
| **10** | **0.375** | 0.59% | 0.987 | **0.256** | 0.03% | 0.401 |
| 20 | 0.584 | 0.35% | 0.996 | 0.414 | 0.03% | 0.640 |
| **30** | **0.712** | 0.27% | 0.998 | **0.523** | 0.01% | 0.784 |
| 50 | 0.855 | 0.22% | 0.999 | 0.657 | 0.01% | 0.923 |
| 100 | 0.968 | 0.14% | 1.000 | 0.788 | 0.00% | 0.994 |

- The analytic check 1 − (1 − π·power)^N matches the null-V column: 0.376, 0.585, 0.714, 0.855, 0.967.
- Convention V = max(null, cross-trial variance excluding the best trial): P(find) = 0.357, 0.547, 0.661, 0.783, 0.879. Global-null false-pass rate: 0.47%, 0.31%, 0.25%, 0.17%, 0.11%.

**Sensitivities of P(find)** (null V; N = 10 / 20 / 30 / 50)

| Scenario | N = 10 | N = 20 | N = 30 | N = 50 |
|---|---|---|---|---|
| True Sharpe 1.0 | 0.20 | 0.28 | 0.33 | 0.39 |
| True Sharpe 1.25 | 0.32 | 0.47 | 0.57 | 0.70 |
| True Sharpe 2.0 | 0.40 | 0.64 | 0.78 | 0.92 |
| Prior 2.5% | 0.21 | 0.35 | 0.47 | 0.62 |
| Prior 10% | 0.62 | 0.83 | 0.92 | 0.98 |
| T_eff = 1,200 | 0.23 | 0.33 | 0.39 | 0.48 |

**Parameter variants instead of ideas** (3 variants per idea, within-idea correlation 0.8)

| Runs | Ideas | P(find), raw N + null V | P(find), raw N + sample V | P(find), clustered N + sample V |
|---|---|---|---|---|
| 9 | 3 | 0.137 | 0.035 | 0.035 |
| 12 | 4 | 0.179 | 0.046 | 0.071 |
| 30 | 10 | 0.372 | 0.142 | 0.347 |
| 51 | 17 | 0.530 | 0.258 | 0.493 |

**Answer to "is 10 too few?"** Yes, in every modelled case.
- The DSR penalty for more trials is mild: about +0.1 Sharpe per doubling of N.
- When all trials are counted, the false-pass probability falls as N grows.
- The program's chance of success roughly doubles from 10 to 30 trials.
- The N = 10 floor makes any budget below 10 strictly wasteful.

What limits N is not statistics:
- the supply of distinct ideas;
- a likely decline in the per-idea prior as the best ideas are used first;
- falling power per real edge;
- the risk of trials run but not counted.

That points to about 30 trials (range 20–50).

### Gaps
- The program's real T_eff, cross-trial correlation, return skewness and kurtosis, and the distribution of true Sharpe ratios among real edges are unknown. All are assumptions above.
- The model treats ideas as independent draws with a constant 5% prior. No source quantifies how the prior declines over a research program.
- The Monte Carlo uses the asymptotic normal distribution of Sharpe estimates, not simulated daily returns.

---

## 3. Data reuse: is a stop rightly final for that history? What do CPCV, the reusable holdout, and alpha-investing or LORD allow, and what does forward testing offer?

### Takeaway
Nothing in the DSR and haircut literature requires abandoning a dataset after a failed search. If every trial is counted cumulatively, the hurdle simply rises, slowly.
- The protocol literature warns that iterated out-of-sample testing is not out-of-sample, and that researchers who lived through the period carry knowledge that counting cannot remove.
- The adaptive-data-analysis literature (Dwork et al.) shows a holdout can be reused safely only through mechanisms that limit what each query reveals. Its guarantees scale with holdout size and assume independent, identically distributed (i.i.d.) samples.
- CPCV and CSCV improve the estimate of overfitting but create no new data.
- Online false-discovery-rate procedures (alpha-investing, LORD) control the false discovery rate over a stream of mostly independent tests. They do not license more trials on one reused history.
- Forward data is the only clean out-of-sample test, and it is slow. 120 paper days cannot validate a Sharpe of 1.5, so G2 is rightly a fidelity check. A fresh 2,400-day G1 window takes about 9.5 years.
- **A final stop is defensible as a commitment device, not required by statistics.** Its cost (about 9.5 years to a new G1) must be explicit.

### Cited Findings
**Reusable holdout (Dwork, Feldman, Hardt, Pitassi, Reingold, Roth; Science 349(6248):636–638, 2015; NeurIPS 2015 companion paper) (older fact)**
- Thresholdout checks whether an analyst's function overfits the holdout. If it does not, the analyst learns only about one bit. If it does, the analyst gets a noisy answer.
- It can answer a number of queries that grows exponentially in the holdout size n, provided the analyst overfits no more than about n² times.
- The talk slides use overfitting = |training mean − true mean| > 0.01.
— [arXiv 1506.02629](https://arxiv.org/pdf/1506.02629); [NeurIPS 2015 paper](https://proceedings.neurips.cc/paper_files/paper/2015/file/bad5f33780c42f2588878a9d07405083-Paper.pdf); [Hardt slides](https://rsrg.cms.caltech.edu/netecon/privacy2015/slides/hardt.pdf); [Science record (ResearchGate)](https://www.researchgate.net/publication/281367205_STATISTICS_The_reusable_holdout_Preserving_validity_in_adaptive_data_analysis)

**Alpha-investing (Foster & Stine, JRSS-B 2008) (older fact)**
- Alpha-investing controls the marginal false discovery rate (mFDR, the ratio of expected false rejections to expected rejections). That is a weaker criterion than the false discovery rate itself.
- Each test spends "alpha-wealth", and each rejection earns wealth back. This overcomes the conservatism of alpha-spending methods such as Bonferroni.
- Control holds at any stopping time. Initial wealth is often α(1−α).
- Generalized alpha-investing (Aharoni & Rosset 2014) sets each test's level optimally given the history of results.
— [Penn repository record](https://repository.upenn.edu/handle/20.500.14332/47482); [Zhao et al., arXiv 1612.01040](https://arxiv.org/pdf/1612.01040); [cost-aware generalized alpha-investing, arXiv 2210.17514](https://ar5iv.labs.arxiv.org/html/2210.17514)

**LORD (Javanmard & Montanari, Annals of Statistics 2018, 526–554, DOI 10.1214/17-AOS1559) (older fact)**
- LORD controls the false discovery rate online for **independent** p-values. One version is proven given w₀ + b₀ ≤ α; another is supported only by simulation.
- Later work extends LORD and SAFFRON to positive or local dependence.
— [arXiv 1502.06197](https://arxiv.org/abs/1502.06197); [Bioconductor onlineFDR theory](https://bioconductor.statistik.tu-dortmund.de/packages/3.21/bioc/vignettes/onlineFDR/inst/doc/theory.html); [Robertson et al., arXiv 1809.07292](https://arxiv.org/pdf/1809.07292); [Fisher, arXiv 2110.08161](https://ar5iv.labs.arxiv.org/html/2110.08161)

**CSCV / PBO (older fact)**
- Hold-out methods are unreliable for investment backtests. CSCV estimates the probability of backtest overfitting. — [Risk.net (JCF)](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting); [CRAN pbo](https://packages.oit.ncsu.edu/cran/web/packages/pbo/readme/README.html)

**Holdout misuse**
- The hold-out method does not control for the number of trials attempted. Repeatedly tuning against the same holdout until its Sharpe looks good is itself backtest overfitting. — [mathinvestor.org FAQ](https://mathinvestor.org/2014/04/faqs-on-backtest-overfitting/); [mathinvestor.org: post-hoc probability fallacy](https://mathinvestor.org/2022/02/backtest-overfitting-and-the-post-hoc-probability-fallacy/); [Palomar, Portfolio Optimization §8.3](https://bookdown.org/palomar/portfoliooptimizationbook/8.3-dangers-backtesting.html)

**Out-of-sample data (Arnott, Harvey & Markowitz)**
- Iterated out-of-sample testing is not out-of-sample. — [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P138_A_backtesting_protocol.pdf); [Hudson & Thames](https://hudsonthames.org/experimental-design-and-common-pitfalls-of-machine-learning-in-finance/)
- Researchers who lived through a holdout period know how markets behaved, so no truly out-of-sample history exists. Live trading is the real test. Freshly uncovered historical data, such as fundamentals backfilled to the 1920s, is a better out-of-sample check. — [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P138_A_backtesting_protocol.pdf) (single-source within the paper, via search summary)

### Inferences
- **Continuing on the same history is statistically valid if N counts every trial ever run on it.**
  - The cost is only the slow rise of the hurdle (section 2): 30 cumulative trials need a Sharpe of 1.21 versus 1.04 at 10.
  - The real argument for a final stop is contamination that counting misses: the researcher's knowledge of 2016–2026 events, and variants designed after reading earlier G1 output.
  - So the rule should be framed as "the **budget** is final for this history" (pre-committed, no top-ups after results) rather than "a stop is final". The two coincide if the budget is fixed in advance.
- **Thresholdout is not a practical way to add trials here.**
  - Its guarantees assume i.i.d. samples and bounded statistics. Daily P&L is serially correlated and non-stationary, and Sharpe is a ratio.
  - It would also require carving a holdout out of a history the G1 window already uses: about 2,716 trading days from 2016-01-04 to 2026-10-15, of which the 2,400-day window takes about 88% (computed).
  - Its usable lesson: limit what each G1 run reveals to the researcher (pass/fail, the DSR and a few summary statistics, not the full equity curve). This reduces adaptive leakage and keeps the raw run count closer to the true number of trials.
- **Online FDR methods do not fit this program well.**
  - They control the share of false discoveries across many deployments, not the chance that one deployed strategy is false.
  - Their proofs need independent (or positively dependent) and conditionally valid p-values. Variants chosen adaptively on one reused history violate this.
  - They suit a long-running program across fresh, independent data epochs or many independent markets. They are not a way to extend testing on one history.
- **CPCV** (*Advances in Financial Machine Learning*, ch. 12, background knowledge) gives a distribution of out-of-sample Sharpe ratios across paths and supports PBO estimates. Every configuration evaluated still counts as a trial, and CPCV does not reset N.
- **Forward testing arithmetic (computed)**

  | Forward window | s.e. of annual Sharpe (true 1.5) | What a true Sharpe-1.5 strategy shows |
  |---|---|---|
  | G2, 120 days | 1.46 | negative Sharpe 15% of the time; below 1.0 37% of the time |
  | 9 months of new data (189 trading days) | 1.16 | negative Sharpe about 10% of the time |

  Forward data needed to confirm a Sharpe of 1.5: about 303 trading days (1.2 years) for t = 1.645, 448 days (1.8 years) for t = 2, and 1,008 days (4.0 years) for t = 3.
- **What this means for G2 and restarts.**
  - G2 rightly tests fidelity, not edge. A Sharpe-based G2 gate would reject many real edges.
  - "Restart only on data after the last G1" plus "G1 needs ≥2,400 days" means the next possible G1 is about **9.5 years** after a stop.
  - Make this explicit, or define an alternative restart:
    - a different market or universe, with its own pre-committed budget;
    - newly obtained older history (Arnott-Harvey-Markowitz's "freshly uncovered historical data");
    - a pre-registered cumulative-N continuation, with the contamination risk accepted and documented.

### Gaps
- I found no finance-specific application or evaluation of Thresholdout or online FDR for strategy research.
- The CPCV details from *Advances in Financial Machine Learning* were not verified this session (search allowance used up).
- I found no source quantifying how much researcher memory of a period inflates the effective number of trials.

---

## 4. What do practitioners do (AQR, Man AHL, Two Sigma, WorldQuant, Quantopian), and what do they say about research time budgets and kill criteria?

### Takeaway
The main large-sample public evidence is Quantopian's 2016 study of 888 algorithms. It found backtest Sharpe nearly useless for predicting out-of-sample Sharpe (R² < 0.025), and that more backtesting widened the gap. This supports strict trial counting, not a particular cap.

Industrial researchers run very many trials, but inside a disciplined production process:
- López de Prado: the "meta-strategy paradigm" versus the "Sisyphus paradigm".
- WorldQuant BRAIN, as described in community reports: Sharpe and fitness filters, plus a self-correlation limit of about 0.7 against existing alphas.

AQR-affiliated academics (Jensen, Kelly & Pedersen, 2023) take a Bayesian view in which most factors replicate and the evidence strengthens with the number of factors. That tempers the Harvey-Liu-Zhu pessimism.

I found **no** Man AHL or Two Sigma publication on trial budgets, and **no** practitioner source on research time budgets or kill dates.

### Cited Findings
**Quantopian: Wiecki, Campbell, Lent & Stauth (2016), "All that glitters is not gold" (older fact)**
- 888 algorithms, each with at least 6 months of out-of-sample performance. Backtest Sharpe offered "little value in predicting out of sample performance (R² < 0.025)"; the blog version reports R² = 0.02. — [paper PDF mirror](https://c.mql5.com/forextsd/forum/208/All%20that%20Glitters%20Is%20Not%20Gold%20-%20Comparing%20Backtest%20and%20Out-of-Sample%20Performance%20on%20a%20Large%20Cohort%20o.pdf); [Quantpedia](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/); [Wiecki guest blog](https://cur.at/nG81N76)
- The more backtesting a quant did on a strategy, the larger the gap between backtest and out-of-sample performance. — [Quantpedia](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/); [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/comparing-backtest-sample-performance-large-cohort-trading-algorithms/)
- Higher moments (volatility, maximum drawdown) and portfolio features (hedging) had significant predictive value. Nonlinear classifiers reached R² = 0.17 on hold-out data. — [Quantpedia](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/); [CXO](https://www.cxoadvisory.com/big-ideas/in-sample-vs-out-of-sample-performance-of-888-trading-strategies)
- The in-sample period ran from 2010 to deployment in early 2015; the out-of-sample period from June 2015 to February 2016. Tests used minute-level prices and estimated frictions. — [CXO](https://www.cxoadvisory.com/big-ideas/in-sample-vs-out-of-sample-performance-of-888-trading-strategies) (single-source)

**López de Prado (2018, JPM 44(6)), "The 10 Reasons Most Machine Learning Funds Fail" (older fact)**
- Error #1 is the "Sisyphus paradigm". It takes "almost as much effort to produce one true investment strategy as to produce a hundred", and "every successful quantitative firm I am aware of applies the meta-strategy paradigm". — [GARP](https://www.garp.org/white-paper/the-10-reasons-most-machine-learning-funds-fail); [Quantpedia](https://quantpedia.com/why-machine-learning-funds-fail/); [SSRN 3031282 mirror](https://smallake.kr/wp-content/uploads/2017/10/SSRN-id3031282.pdf)

**WorldQuant BRAIN (community-reported, not official)**
- Submissions reportedly need self-correlation below 0.7 against the user's submitted alphas. In-sample pass criteria are reportedly Sharpe > 1.25 and fitness ≥ 1, and may vary. Further checks cover turnover, weight concentration, sub-universe and competition matching. — [quantt.co.uk](https://www.quantt.co.uk/resources/worldquant-brain); [GitHub alpha-mining](https://github.com/zl3311/alpha-mining); [GitHub WQ-Brain](https://github.com/RussellDash332/WQ-Brain); [arXiv 2608.11250](https://arxiv.org/pdf/2608.11250). No official WorldQuant documentation found; thresholds may differ by region or universe.

**Jensen, Kelly & Pedersen (2023, Journal of Finance 78(5):2465–2518), "Is There a Replication Crisis in Finance?" (older fact)**
- A Bayesian model finds most factors replicate. They cluster into 13 themes, work out of sample across 93 countries, and their evidence is "strengthened (not weakened) by the large number of observed factors". — [NBER w28432](https://www.nber.org/papers/w28432); [CBS publisher's version](https://research-api.cbs.dk/ws/portalfiles/portal/95651880/theis_ingerslev_jensen_et_al_is_there_a_replication_crisis_in_finance_publishersversion.pdf); [Alpha Architect](https://alphaarchitect.com/is-there-a-replication-crisis-in-finance/)
- Over 80% of US equity factors stay significant after standardizing construction and accounting for multiple testing. — [Alpha Architect](https://alphaarchitect.com/is-there-a-replication-crisis-in-finance/) (single-source)

**Man AHL / Two Sigma**
- Searches aimed at their publications returned only the academic literature. — (no firm source found; see Gaps)

### Inferences
- **Large-scale searches pair volume with production discipline.** The common pattern (López de Prado's meta-strategy and the WorldQuant model) is many cheap trials inside a process that logs everything, filters hard, de-duplicates correlated signals, and validates on data the researcher did not tune on.
  - For a one-person automated program, this argues for investing in the logging and counting machinery so a larger counted budget (about 30) is safe. It does not argue for a small cap.
- **A practical clustering rule.** WorldQuant's reported self-correlation cap of about 0.7 is an industrial analogue of clustering trials. Treat two variants whose daily P&L correlation exceeds a pre-set level (e.g. 0.7) as the same idea when counting ideas, while still counting every run in N.
- **Weigh the Bayesian counterpoint.** Jensen-Kelly-Pedersen versus Harvey-Liu-Zhu shows that how strict to be depends on priors. The program's explicit 5% prior is the right lever, and section 2 shows how results vary with it (2.5% to 10%).
- **Quantopian's lesson for G1.** Volatility, drawdown and hedging predicted out-of-sample results better than Sharpe. G1 could add pre-registered non-Sharpe diagnostics. That reduces false passes without spending trials.

### Gaps
- No Man AHL, Two Sigma or AQR internal research-process documents found (search allowance used up). Leads from background knowledge, **unverified**:
  - Man AHL / Man Institute articles on overfitting;
  - AQR essays by Asness on data mining and out-of-sample tests across countries and asset classes;
  - Kelly and Pedersen's AQR affiliation.
- No practitioner kill criteria for research programs found. Lead (**unverified**): Bailey & López de Prado's drawdown-based "triple penance rule" for stopping live strategies (Journal of Risk, about 2015). It concerns live strategies, not research budgets.
- The current official WorldQuant BRAIN thresholds are unverified.

---

## 5. Time budget: is there guidance on how long to research before stopping, and is 9 months reasonable for a one-person program with automated research?

### Takeaway
I found **no source** giving an evidence-based duration or kill date for a strategy search. The search allowance ran out before I could look in depth, so this is a gap, not proof of absence.

On the quantitative side:
- Calendar time does not use up statistical budget; counted trials and T_eff do.
- With automation, running about 30 trials in 9 months is not the constraint. The supply of well-founded ideas and the researcher's review time are.
- The time cap's legitimate roles are limiting opportunity cost and sunk-cost drift, and forcing a decision.

Recommendation (low confidence): keep about 9 months, split into three staged go/no-go checkpoints, with a pre-committed hard end (≤12 months including at most one pre-registered extension). Never extend because a variant "nearly passed".

### Cited Findings
- It takes "almost as much effort to produce one true investment strategy as to produce a hundred" (the case for an industrialized pipeline over one-at-a-time research). — [GARP](https://www.garp.org/white-paper/the-10-reasons-most-machine-learning-funds-fail); [Quantpedia](https://quantpedia.com/why-machine-learning-funds-fail/)
- Iterated out-of-sample testing is not out-of-sample, and live trading is the real test. Near-miss-driven iteration is therefore a form of overfitting. — [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P138_A_backtesting_protocol.pdf); [Hudson & Thames](https://hudsonthames.org/experimental-design-and-common-pitfalls-of-machine-learning-in-finance/)
- Missed discoveries are a real cost that thresholds should weigh against false ones. This argues against a budget so tight that real edges are likely missed. — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12951); [arXiv 2006.04269](https://arxiv.org/abs/2006.04269)

### Inferences
- **What the 9 months buy.** New data arrives at about 21 trading days a month: about 189 trading days over 9 months (computed). That is too short to confirm an edge (s.e. 1.16), but a true Sharpe-1.5 strategy would show a negative Sharpe over it only about 10% of the time.
  - Option: freeze the G1 window at research start and keep the post-start data untouched as a small forward sanity holdout, used once at the end.
- **Suggested stage design** (my construction, not from a source):

  | Stage | Months | Work | Counted trials |
  |---|---|---|---|
  | 1 | 0–3 | Data, cost model and G1 harness validated on synthetic or known strategies; T_eff and the V convention fixed; an idea backlog pre-registered | none or few |
  | 2 | 3–6 | About 15 counted trials on distinct pre-registered ideas | ≈15 |
  | 3 | 6–9 | About 15 more | ≈15 |

  - The decision at month 9 is final unless a pre-registered process criterion triggers one extension of up to 3 months. Examples: the harness is validated, the backlog of untested pre-registered ideas is non-empty, and the trial budget is not exhausted.
  - Within each stage, register the ideas before any G1 run of that stage, and reveal only minimal G1 output (section 3).
- **How to tell whether 9 months is right for this owner.** Measure in stage 1 the real throughput of distinct, economically motivated ideas per month.
  - If it is well below about 3 a month, 30 trials will not fit in 9 months. The binding question becomes whether to extend time or accept fewer ideas. Section 2 shows success probability is driven by ideas tested, not by months.
- **The current cycle structure invites iterated out-of-sample testing.** Four cycles of three variants, each informed by the last cycle's G1 output, is exactly what Arnott-Harvey-Markowitz warn about. Pre-registering per stage and minimizing what G1 reveals mitigate this.

### Gaps
- No literature found on optimal research duration, opportunity cost or kill dates for quant strategy research. Background-knowledge leads, **unverified this session**:
  - Weitzman (1979), "Optimal Search for the Best Alternative" (Pandora's-box stopping rule with search costs);
  - stage-gate project governance (Cooper);
  - sunk-cost research (Arkes & Blumer 1985);
  - Robert Carver's practitioner writing on implicit fitting and how many years are needed to tell Sharpe ratios apart.
- The owner's opportunity cost, research hours available and idea throughput are unknown. They decide the time budget more than any statistic does.

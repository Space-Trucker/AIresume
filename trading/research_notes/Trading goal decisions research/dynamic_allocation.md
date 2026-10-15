# Dynamic allocation without a fixed position count, and the rule for rotating into a better candidate

Notes for the trading goal: a $100,000 Alpaca paper account, with limits as read from the local [goal.toml](/home/user/AIresume/trading/goal/goal.toml) on 2026-10-15.

**Labels.** **[2+ sources]** means at least two independent sources confirm the fact. **[single-source]** means one source, or several copies of one abstract. **[secondary only]** means only secondary summaries confirm it. **[local]** means the project's own files. **[computed]** means arithmetic done for these notes.

**Limits on this session's research.** These limits apply to every section below:
- WebFetch failed with a DNS error on every host.
- The egress proxy refused direct PDF downloads with 403 errors (nber.org, ssrn.com, arxiv.org, github.io, stern.nyu.edu, rochester.edu).
- The shared per-turn web-search budget ran out after 16 searches.

Every finding below therefore comes from search-engine extracts of the cited pages. I could not check formulas, tables or numbers inside the papers against their full text. Each such case is listed under Gaps.

Dates: most of the core literature is from 1986 to 2020, so every finding is older than today (2026-10-15) and is dated. I found no later result that supersedes these sources. One 2026 paper turned up by title only.

---

## 1. What do Gârleanu & Pedersen (2013) and the related theory prescribe: the aim portfolio, partial trading, signal decay, and no-trade regions?

### Takeaway
- **Gârleanu-Pedersen (GP) policy.** Each period, move only part of the way from current holdings toward an "aim" portfolio. The aim is a weighted average of today's Markowitz portfolio and the Markowitz portfolios expected in the future.
- **Signal decay.** Signals whose alpha decays slowly get more weight in the aim; fast-decaying signals are discounted.
- **Cost assumption.** GP assume quadratic (impact-type) costs. With proportional (spread-type) costs the theory gives a no-trade band instead (Constantinides 1986; Davis-Norman 1990; Liu 2004; de Lataillade et al. 2012): keep anything inside the band and trade only to its edge.
- **This system's costs are close to proportional.** So hysteresis, not fractional trading, is the operative lesson.
- **Common ground.** Every one of these models says never jump all the way to the frictionless target.

### Cited Findings
- **Publication.** Gârleanu & Pedersen, "Dynamic Trading with Predictable Returns and Transaction Costs", Journal of Finance 68(6):2309–2340 (2013); first circulated as NBER WP 15205 (2009). **[2+ sources]** — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12080); [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:68:y:2013:i:6:p:2309-2340); [NBER](https://www.nber.org/papers/w15205)
- **Two principles.** The optimal policy is to "aim in front of the target" and to "trade partially toward the current aim". The updated portfolio is a linear combination of the existing portfolio and the aim portfolio. **[2+ sources]** — [Wiley abstract](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12080); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1444706); [Univ. of Copenhagen thesis summary](https://www.math.ku.dk/english/calendar/events/speciale-plk/)
- **The aim portfolio.** It is a weighted average of the current Markowitz portfolio (the moving target) and the Markowitz portfolios expected on all future dates. **[2+ sources]** — [NBER WP](https://www.nber.org/system/files/working_papers/w15205/w15205.pdf); [Copenhagen thesis summary](https://www.math.ku.dk/english/calendar/events/speciale-plk/)
- **Decay weighting.** Predictors with slower mean reversion (slower alpha decay) get more weight in the aim. **[2+ sources]** — [SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1444706); [Copenhagen thesis summary](https://www.math.ku.dk/english/calendar/events/speciale-plk/)
- **Hedegaard's restatement (AQR working paper).** The aim is the Markowitz portfolio computed as if the signals were scaled down by their mean-reversion factor. **[single-source; independent of GP]** — [Hedegaard, AQR](https://www.aqr.com/-/media/AQR/Documents/Insights/Working-Papers/Robust-Dynamic-Asset-Allocation-With-Model-Misspecification.pdf)
- **Why trade only partway.** GP: trading all the way to the aim "entails excessively high transaction costs". It is better to hold a smoother portfolio that moves toward the aim while limiting turnover. **[single-source, from a search extract of the paper]** — [SSRN](https://www.ssrn.com/abstract=1444706); [ResearchGate copy](https://www.researchgate.net/publication/228141114_Dynamic_Trading_with_Predictable_Returns_and_Transaction_Costs)
- **Empirical test.** On commodity futures, the policy earns superior returns net of trading costs compared with more naive benchmarks. I recovered no Sharpe-ratio numbers. **[single-source: the authors' abstract]** — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12080); [NBER](https://www.nber.org/papers/w15205)
- **Model assumptions and a replication.** The framework uses quadratic transaction costs and linear return predictors. A Copenhagen thesis replicated it on stock-index data from 2009–2024 and found the aim to be a scaled-down Markowitz portfolio that the investor trades toward partially. **[single-source]** — [Copenhagen thesis (Stenderup)](https://www.math.ku.dk/english/calendar/specialeforsvar/speciale-mdsten)
- **Gârleanu & Pedersen (2016).** "Dynamic Portfolio Choice with Frictions", Journal of Economic Theory, pp. 487–516, doi 10.1016/j.jet.2016.06.001 (working paper dated November 2013).
  - Model: continuous time, with transitory and persistent transaction costs, multiple assets and multiple return-predicting signals.
  - The objective is derived as the limit of discrete-time models in which dealers create the costs.
  - The solution is explicit and equals the limit of the discrete-time solutions.
  - **[2+ sources]** — [SUFE newsletter abstract](https://academicnewsletter.sufe.edu.cn/info/299955); [AEA 2014 conference copy](https://aeaweb.org/conference/2014/retrieve.php?pdfid=1147)
- **Collin-Dufresne, Daniel & Sağlam (2020).** "Liquidity regimes and optimal dynamic asset allocation", Journal of Financial Economics 136(2):379–406.
  - Trading speed toward the target depends on the state. It is faster when the regime is more persistent, when risk is higher, and when trading costs are lower.
  - The target blends each state's mean-variance portfolio, weighted by transition probabilities.
  - Realized trading costs, estimated from a large institutional order dataset, are significantly higher when volatility is high.
  - Out of sample, the dynamic strategy beats a myopic one. Most of the gain comes from timing changes in volatility and trading costs, not expected returns.
  - **[single-source: the authors' abstract, reproduced on several sites]** — [NBER w24222](https://www.nber.org/papers/w24222); [SFI](https://www.sfi.ch/en/publications/n-18-43-liquidity-regimes-and-optimal-dynamic-asset-allocation-p.-collin-dufresne-k.-daniel-and-m.-saglam-2018.); [EPFL news](https://actu.epfl.ch/news/new-paper-in-journal-of-financial-economics-for--2)
- **Constantinides (1986).** With proportional costs, the optimal policy is a no-trade region. When the portfolio leaves it, the investor trades back to the nearer boundary. **[2+ sources]** — [Lynch & Tan, NYU](https://archive.nyu.edu/bitstream/2451/26507/2/02-63.pdf); [MPRA paper](https://mpra.ub.uni-muenchen.de/117162/1/Sweep_paper-4.pdf)
- **Davis & Norman (1990).** They solved the same problem exactly, without restrictions on consumption. The no-trade region is a convex cone around the Merton line. **[single-source for the cone description]** — [MPRA paper](https://mpra.ub.uni-muenchen.de/117162/1/Sweep_paper-4.pdf); [Lynch & Tan](https://pages.stern.nyu.edu/~alynch/pdfs/MultiRFSAll.pdf)
- **Liu (2004).** With CARA utility and uncorrelated assets, the policy separates asset by asset, with an analytical solution (up to a constant) under fixed plus proportional costs. **[single-source]** — [Lynch & Tan / MPRA, from search extract](https://archive.nyu.edu/bitstream/2451/26507/2/02-63.pdf)
- **Correlated assets.** The shape of the no-trade region depends on correlations:
  - Balduzzi & Lynch (1999): two assets, solved numerically.
  - Chen & Dai (2013): n correlated assets.
  - Muthuraman & Zha (2008): computed cases with k ≥ 3 assets.
  - **[single-source]** — [Lynch & Tan](https://archive.nyu.edu/bitstream/2451/26507/2/02-63.pdf); [Balduzzi-Lynch, JFE](https://www.sciencedirect.com/science/article/abs/pii/S0304405X99000045)
- **Multi-period, many assets, general costs.** Inside the no-trade region it is optimal not to trade at all, and the region grows with the level of proportional costs. **[single-source; attributed via search extract]** — [Mei, DeMiguel & Nogales, Optimization Online](https://optimization-online.org/wp-content/uploads/2013/07/3962.pdf)
- **The band is wide.** The no-trade region is wide even for small transaction costs, so investors should accept wide swings around the frictionless target. **[single-source; attribution from search extract]** — [Guasoni & Muhle-Karbe, "Portfolio Choice with Transaction Costs: a User's Guide"](https://arxiv.org/pdf/1207.7330)
- **de Lataillade, Deremble, Potters & Bouchaud (2012).** With linear costs and a cap on position size, the optimal policy is a threshold rule. For an Ornstein-Uhlenbeck predictor the threshold has an exact equation, and it links to the optimal no-trade band when a quadratic risk penalty is added. Published in J. Investment Strategies 1(3). **[single-source: the authors' paper]** — [arXiv 1203.5957](https://arxiv.org/abs/1203.5957); [IDEAS](https://ideas.repec.org/p/arx/papers/1203.5957.html)
- **Rej, Benichou, de Lataillade, Zérah & Bouchaud (2015).** With linear plus small quadratic costs, the no-trade band narrows by an amount that scales as the one-third power of the quadratic cost. Published in Risk 30(3). **[single-source]** — [ResearchGate](https://www.researchgate.net/publication/284579388_Optimal_Trading_with_Linear_and_small_Non-Linear_Costs); [IDEAS](https://ideas.repec.org/p/arx/papers/1511.07359.html)
- **Recent work.** A 2026 Quantitative Finance paper applies approximate dynamic programming to high-dimensional portfolio choice with transaction costs. Title only; content not verified. **[single-source]** — [Taylor & Francis](https://www.tandfonline.com/doi/full/10.1080/14697688.2026.2708220)

### Inferences
- **This system's costs are proportional, so the band (hysteresis) result is the one to implement.**
  - Orders are at most 10% of equity ($10,000) in names trading at least $20M a day, which is at most 0.05% of ADV. Cost is then essentially half-spread plus slippage plus fees per share, linear in size.
  - GP's quadratic impact term is second order here. So the prescription is hysteresis: open above a threshold, hold until value falls below a lower threshold, and when trading, trade only to the band edge.
  - GP's fractional rule ("trade a/λ of the way each period") is not the practical answer for this account.
- **GP's decay lesson does carry over.** A candidate's value should be its expected gain integrated over its decay and net of costs, not its instantaneous signal strength. A fast-decaying signal has less total gain to pay a round trip, so it deserves less weight. "Aim in front of the target" here means preferring persistent signals.
- **Mapping GP's terms onto a stop-based book:**
  - "Aim" = the positions, and the risk in each, that the model would choose if it started fresh, valuing each by its decay-integrated expected gain.
  - "Trade partially" = act only when the gap between the current book and the aim exceeds a band set by costs and forecast uncertainty.
- **Market state.** CDS (2020) implies the band should widen when spreads widen or volatility rises (costs are regime-dependent), and narrow when liquidity is good.

### Gaps
- **Exact GP formulas not verified in this session (full text unreachable).** From my memory of the paper, to verify before quoting:
  - Optimal portfolio: x_t = (1 − a/λ)·x_{t−1} + (a/λ)·aim_t.
  - Aim: aim_t = (γΣ)⁻¹·B·(I + aΦ/γ)⁻¹·f_t, i.e. each factor's Markowitz weight scaled by 1/(1 + a·φ_k/γ), where φ_k is that factor's decay rate.
  - Rate: a = [−(γ(1−ρ)+λρ) + √((γ(1−ρ)+λρ)² + 4γλ(1−ρ)²)] / (2(1−ρ)).
  - The trading rate a/λ falls as the cost λ rises and rises with risk aversion γ.
  - Costs take the form (λ/2)·Δx′ΣΔx.
  - The commodity-futures signals were, I believe, 5-day, 12-month and 5-year past returns.
- **GP's net Sharpe ratios** against the Markowitz benchmarks were not recovered.
- **The small-cost "cube-root law"** was not verified: band width ∝ (proportional cost)^(1/3), utility loss ∝ cost^(2/3) (Rogers 2004; Janeček & Shreve 2004; Guasoni & Muhle-Karbe).
- **The Isichenko, Paleologo, Kakushadze and Bouchaud et al. ("Trades, Quotes and Prices") books** were not consulted (search budget exhausted).

---

## 2. How do stat-arb and systematic equity managers handle capacity: fixed count or risk budget, turnover penalties, break-even alpha, banding, cost-aware rebalancing?

### Takeaway
- **The count is an output, not an input.** Systematic managers maximize expected alpha minus a risk penalty minus (amortized) trading cost, subject to risk, exposure, liquidity and turnover limits. The number of names falls out of that.
- **Turnover tools:**
  - a cost penalty;
  - a buy/hold band (hysteresis), which Novy-Marx & Velikov (2016) found to be the single most effective simple cost-mitigation technique;
  - netting trades across signals (DeMiguel et al. 2020).
- **Grinold & Kahn's frontier is concave:** about 75% of the value added comes with 50% of the turnover.
- **Live institutional costs** are about an order of magnitude below academic estimates (Frazzini-Israel-Moskowitz 2018). Cost models should be measured on one's own fills.

### Cited Findings
- **Grinold & Kahn's framework** (via study notes on *Active Portfolio Management*):
  - Value added = α − λ·ψ (alpha minus a risk-aversion penalty on active risk).
  - With costs, maximize value added minus cost × turnover; the optimum is where the slope of the value-added/turnover frontier equals the cost per unit of turnover.
  - "You can achieve at least 75% of the incremental value added with 50% of the turnover."
  - **[single-source: study notes on the book]** — [Zhipeng Yan, study notes](https://people.brandeis.edu/~yanzp/Study%20Notes/Active%20Portfolio%20Management.pdf)
- **Kahn (2018, CFA Institute Research Foundation):** poor estimation of transaction costs and slipshod trading are a substantial drain on active returns. **[single-source]** — [Kahn, The Future of Investment Management](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2018/future-of-investment-management-kahn.pdf)
- **Novy-Marx & Velikov (2016)**, "A Taxonomy of Anomalies and Their Trading Costs", Review of Financial Studies 29(1):104–147 (NBER WP 20721, December 2014):
  - A buy/hold spread, which "allows investors to continue to hold stocks that they would not actively trade into", is the single most effective simple cost-mitigation strategy.
  - Most anomalies with monthly turnover below 50% still earn significant net spreads when designed to mitigate costs; few with higher turnover do.
  - Capacity is inversely related to turnover.
  - Costs reduce profitability and statistical significance in every case, which heightens data-snooping concerns.
  - **[2+ sources]** — [NBER](https://nber.org/papers/w20721); [IDEAS/RFS](https://ideas.repec.org/a/oup/rfinst/v29y2016i1p104-147..html); [SUFE newsletter](https://academicnewsletter.sufe.edu.cn/info/353667)
- **Novy-Marx & Velikov's cost measure.** They use Hasbrouck's effective bid-ask spread, which ignores the price impact of large trades, so it reflects the cost to a small liquidity demander. They cover 23 strategies. **[single-source, secondary]** — [Alpha Architect summary](https://alphaarchitect.com/trading-costs-destroy-factor-investing/)
- **Frazzini, Israel & Moskowitz (2018), "Trading Costs":**
  - Data: $1.7 trillion of live executions by a large institutional manager, across 21 developed equity markets over 19 years.
  - Real costs are an order of magnitude smaller than earlier studies suggest.
  - A cost model calibrated to actual costs beats literature models out of sample, against broker-reported costs and the realized costs of index funds.
  - **[2+ sources]** — [AQR](https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs); [SSRN 3229719](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719)
- **Caveat on Frazzini-Israel-Moskowitz (2018).** The study measures price impact only; it leaves out shorting costs and lending revenue. **[single-source]** — [Institutional Investor](https://www.institutionalinvestor.com/article/2bsxq9yadiccew11t8idc/portfolio/aqr-investor-worries-over-trading-costs-may-be-overblown)
- **The predecessor paper, "Trading Costs of Asset Pricing Anomalies" (Frazzini, Israel & Moskowitz, 2012/2015):**
  - Cost estimates are many times smaller, and break-even fund sizes more than an order of magnitude larger, than the literature claims.
  - Value and momentum scale better than size.
  - Short-term reversal is the strategy most constrained by trading costs.
  - **[single-source: the authors' paper]** — [AQR](https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs-of-Asset-Pricing-Anomalies); [SSRN 2294498](https://ssrn.com/abstract=2294498)
- **DeMiguel, Martín-Utrera, Nogales & Uppal (2020)**, "A Transaction-Cost Perspective on the Multitude of Firm Characteristics", Review of Financial Studies 33(5):2180–2222:
  - Transaction costs increase the number of jointly significant characteristics from 6 to 15.
  - The reason is netting: the stock trades needed to rebalance different characteristics often cancel out.
  - **[2+ sources]** — [Lancaster manuscript](https://eprints.lancs.ac.uk/id/eprint/133724/1/DMNU_Manuscript_InternetAppendix_2019_01_08.pdf); [ResearchGate](https://www.researchgate.net/publication/344722323_A_Transaction-Cost_Perspective_on_the_Multitude_of_Firm_Characteristics); [UC3M portal](https://researchportal.uc3m.es/display/act524892)
- **DeMiguel et al., working-paper turnover numbers:**
  - Average monthly turnover is 24.09% for one characteristic traded alone and 6.71% for an equally weighted combination, a 72.15% reduction.
  - Turnover of an equal-weighted combination of K characteristics is about 1/√K of the single-characteristic level.
  - **[single-source: manuscript draft; the published numbers may differ]** — [Lancaster manuscript](https://eprints.lancs.ac.uk/id/eprint/133724/1/DMNU_Manuscript_InternetAppendix_2019_01_08.pdf)

### Inferences
- **The practice converges on "budget plus bands plus a cost-aware target", which is what the owner asked for.** A fixed count is not how optimizer-based managers allocate. Where a count exists, it is a guard or an operational constraint (see question 5).
- **Break-even alpha for this system** (computed from goal.toml: 8 bps round trip, stress ×1.5, typical hold 3 days):
  - A trade must earn at least its round trip over its life: 8 bps of notional, or 12 bps stressed.
  - Amortized, that is about 2.7 bps of notional per day (4 bps stressed) over a 3-day hold.
  - The goal's entry rule (gain ≥ 2× cost) asks for 16 bps (24 stressed) over the trade's life.
  - **[computed]**
- **Netting at the single-name level.** If a rotation would close one name and open the same name, or if two signals disagree on a name, keep the position rather than paying two round trips. This is DeMiguel et al.'s mechanism applied to the system.
- **Measure costs on our own fills.** Frazzini-Israel-Moskowitz show that model-based cost estimates can be badly off. Paper and live fills should calibrate the cost each trade is charged before the rotation hurdle is trusted.
- **This system's turnover is very high.** 25 round trips a week at about 4% of equity is 2 × 25 × 4% = 200% of equity traded per week, roughly 100× equity a year. Novy-Marx & Velikov's 50%-per-month threshold is about 6× a year. The system lives entirely in the regime where costs decide viability, so every extra round trip from rotation must be justified. **[computed]**

### Gaps
- **Grinold & Kahn's no-trade condition and amortization rule were not retrieved** (book text unreachable). From memory, unverified:
  - With linear costs, hold an asset while −(sell cost) ≤ marginal contribution to value added ≤ (purchase cost).
  - A swap of i for j pays only if MCVA_j − MCVA_i > (purchase cost of j + sell cost of i).
  - Costs are amortized by dividing the round-trip cost by the expected holding period.
- **No practitioner documents were retrieved** from Man AHL, Two Sigma, MSCI Barra or Axioma on turnover penalties, cost amortization, or "max names" (cardinality) and "min holding" (threshold) constraints. I believe commercial optimizers support both constraint types, but this is unverified.
- **Novy-Marx & Velikov's exact band thresholds are unverified.** I recall "buy in the top decile, hold while in the top two deciles".

---

## 3. Is the replacement rule the standard form? How should estimation error be handled, and how is a held position's remaining gain estimated as its signal ages?

### Takeaway
- **Yes in structure.** "No swap of a held position for an excluded candidate adds value net of switching cost" is the discrete optimality condition for a book whose binding constraint is a budget. It is also what a cost-penalized optimizer and a buy/hold band enforce.
- **The precise form:** rotate when (candidate's expected gain − its own round-trip cost − the opportunity cost of the risk-days it uses) exceeds (the held position's expected remaining gain − the opportunity cost of its remaining risk-days), by a margin that covers forecast error.
- **The held position's exit cost cancels.** It is paid whether the system switches now or exits later, so the owner's version, which subtracts it, is a mildly conservative variant.
- **Real protection against churn comes from four things:**
  - calibrated, shrunk forecasts;
  - an explicit margin;
  - persistence, minimum-hold and rotation-count limits;
  - a counterfactual test of every rotation.
- **The held position's remaining gain** is re-estimated from its signal's decay curve, updated with current data. P&L since entry is ignored.

### Cited Findings
- **The buy/hold spread is hysteresis.** It sets a stricter bar to open a position than to keep it, and it is the most effective simple cost mitigation. **[2+ sources]** — [NBER](https://nber.org/papers/w20721); [IDEAS/RFS](https://ideas.repec.org/a/oup/rfinst/v29y2016i1p104-147..html)
- **Decay matters.** Slower-decaying signals deserve more weight once costs are included. **[2+ sources]** — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1444706); [Hedegaard, AQR](https://www.aqr.com/-/media/AQR/Documents/Insights/Working-Papers/Robust-Dynamic-Asset-Allocation-With-Model-Misspecification.pdf)
- **The band grows with cost.** With proportional costs, not trading inside the no-trade region is optimal, and the region grows with the cost level. **[single-source]** — [Mei-DeMiguel-Nogales](https://optimization-online.org/wp-content/uploads/2013/07/3962.pdf)
- **Odean (1999), on 10,000 discount-brokerage accounts.** The securities investors bought underperformed those they sold. This held even for trades not apparently driven by liquidity needs, tax-loss selling, rebalancing or a move to lower risk. In other words, switching into "better" opportunities on the investor's own forecasts destroyed value even before costs. **[2+ sources for the finding]** — [Odean, AER paper](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/doinvestors.pdf); [SSRN 94143](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=94143)
- **Size of Odean's gap.** About 3.3 percentage points over one year. **[secondary only; verify against the paper's tables]** — [StudyCorgi summary](https://studycorgi.com/do-investors-trade-too-much-by-odean/); [EssaySauce summary](https://www.essaysauce.com/finance-essays/do-investors-trade-too-much-summary/)
- **Regime-dependent costs.** Trading speed and costs depend on the state: costs are higher in high volatility, so trading should slow then. **[single-source: abstract]** — [NBER w24222](https://www.nber.org/papers/w24222); [SFI](https://www.sfi.ch/en/publications/n-18-43-liquidity-regimes-and-optimal-dynamic-asset-allocation-p.-collin-dufresne-k.-daniel-and-m.-saglam-2018.)

### Inferences
- **The exact switching algebra (why the held position's exit cost cancels).** All amounts are expected values in % of equity.
  - Hold: the book earns g_i (the held position's gain from now to its planned exit) and later pays its exit cost X_i.
  - Switch: the book pays X_i now (plus ΔX_i if exiting now costs more than the planned exit, e.g. crossing the spread instead of a passive exit), then earns g_j and pays the candidate's round trip C_j.
  - Switch minus hold = (g_j − C_j) − g_i − ΔX_i. X_i cancels.
  - So "candidate's net gain − cost to open it − cost to close the held position > held position's remaining gain" is exact only if the held position's remaining gain is stated net of its own exit cost. If both sides are stated gross, it double-counts one exit cost.
  - The double count is small (one 4 bps one-way on the closed position's notional; at 4% of equity that is 0.0016% of equity). It is better replaced by an explicit margin. **[computed]**
- **The opportunity cost of the budget (the risk-days term).**
  - If the held position would exit soon anyway, holding it frees its risk budget soon, and that budget can be redeployed. A naive comparison overstates the gain from switching.
  - Correct this by charging each side κ·R·H, where:
    - R is the loss at the stop (% of equity);
    - H is the remaining holding time in days;
    - κ is the net expected gain per unit of risk per day that the marginal new entry earns, estimated as the trailing 20-session median of entries' (g − C)/(R·H), floored at 0.
  - This is standard capital budgeting: value net of a capital charge. Both sides of the comparison:

    v_j = g_j − C_j − κ·R_j·H_j
    v_i = g_i − κ·R_i·H_i(remaining) − ΔX_i

    Rotate only if v_j − v_i ≥ m.

  **[inference]**
- **Worked example (assumed numbers; illustrative only).** The book is full on open risk.

  | Quantity | Value | Basis |
  |---|---|---|
  | Held position: notional, stop | 4% of equity, 3.75% stop | R = 0.15% of equity |
  | Held position: expected gain at entry | 40 bps of notional | half-life 1 day, 3-day horizon |
  | Held position: remaining gain at age 1.5 days | 0.26 × 40 = 10.4 bps | decay table below |
  | Candidate: expected gain, round trip, stop | 40 bps over 3 days, 12 bps stressed RT, same R | assumed |
  | Naive advantage | 28 − 10.4 = 17.6 bps of notional | |
  | κ (typical entry: 28 bps net over 3 days on R = 375 bps) | ≈ 0.025 R per day | trailing-median estimate |
  | Charge for the candidate's 1.5 extra days of the risk slot | ≈ 14 bps | κ·R·1.5 days |
  | True advantage | ≈ 3.6 bps of notional (0.00014% of equity) | 17.6 − 14 |

  The value of a single rotation is small next to typical forecast error. The margin and the counterfactual test therefore decide whether rotation helps at all. **[computed]**
- **Use the binding resource as the denominator.** The scarce resource is whichever limit binds:
  - Open risk binds when the average stop distance exceeds max_open_risk / gross limit: 2.0/100 = 2% intraday, and 2.0/75 ≈ 2.67% overnight.
  - With tighter stops, gross or overnight gross binds, and value should be ranked per unit of notional.
  - If several limits bind, a small linear program decides.
  - For divisible positions, ranking by value per unit of the binding resource and freeing it from the lowest-ranked positions first is the greedy fractional-knapsack solution, which is optimal for divisible items.
  - So "trim the weakest positions just enough to fund the candidate" beats "always close one whole position".

  **[computed / inference]**
- **Gain per unit of risk depends on the stop.** A tighter stop makes R smaller but raises the chance of being stopped out. g must therefore be the expected gain under the position's actual stop and exit rules, or rotation will favour tight-stop candidates mechanically. **[inference]**
- **The winner's curse (the optimizer's curse) when picking the best of many noisy forecasts.**
  - If each forecast = truth + independent noise with standard deviation σ_e, the top-ranked forecast is biased upward by roughly E[max of N standard normals] × σ_e: 1.54σ_e for N = 10, 2.51σ_e for N = 100, 3.24σ_e for N = 1,000, 3.44σ_e for N = 2,000. **[computed]** (Only the share of variance that is noise is biased, so the true bias is smaller when forecasts are informative.)
  - The universe (≥ $5, ≥ $20M ADV, ≤ 10 bps spread) is plausibly 1,000–2,000 names. The best candidate's raw forecast is therefore systematically too high, while the held position's forecast is not selected from N in the same way.
  - A naive rotation rule is thus biased toward switching. This is the model version of Odean's finding.
  - Remedy: calibrate expected gains on the realized outcomes of the top-ranked candidates only (decile or isotonic calibration done on the same selection process), which removes the selection bias. Then add the margin m.
- **The margin.**
  - m = max(C_j, z·σ_S), with z = 1 as a starting value.
  - σ_S is the standard deviation of (realized − predicted) switch value, taken from calibration residuals.
  - The floor C_j means a rotation must clear its switching cost twice, mirroring the goal's entry rule (expected gain ≥ 2× cost).
  - **[inference; parameter values are judgment]**
- **The remaining gain of an aging position.**
  1. For each signal, measure from history the average cumulative forward return in event time after entry (the decay curve) and fit a half-life h.
  2. The prior for the remaining gain at age t over a planned horizon T is f(t) = (e^(−φt) − e^(−φT)) / (1 − e^(−φT)) times the entry-time expected gain, where φ = ln 2 / h.
  3. Update the prior by re-scoring the held name with the live model on current data. For a mean-reversion signal, also use how much of the gap has already closed.
  4. Never use P&L since entry; it is sunk. Using it creates the disposition effect.

  Remaining fraction f(t) of a trade's total expected gain, for T = 3 days **[computed]**:

  | half-life h | t = 0.25 d | 0.5 d | 1 d | 1.5 d | 2 d | 2.5 d |
  |---|---|---|---|---|---|---|
  | 0.5 d | 0.70 | 0.49 | 0.24 | 0.11 | 0.05 | 0.02 |
  | 1 d | 0.82 | 0.67 | 0.43 | 0.26 | 0.14 | 0.06 |
  | 2 d | 0.87 | 0.75 | 0.55 | 0.37 | 0.23 | 0.10 |
  | 3 d | 0.89 | 0.78 | 0.59 | 0.41 | 0.26 | 0.12 |
  | 6 d | 0.90 | 0.81 | 0.63 | 0.46 | 0.30 | 0.14 |

  As the held position ages, its v_i falls and rotation becomes attractive on its own. That is the dynamic behaviour the owner wants, delivered without any count.
- **Minimum hold.** Just after entry, the held and candidate forecasts rest on almost the same information, so score changes within minutes are mostly noise. Propose a minimum hold before voluntary rotation of max(15 minutes, 20% of the position's planned holding time). Stops and the position's own exit rules always apply. **[inference; judgment]**
- **Persistence.** Require the candidate's advantage to hold at two consecutive one-minute evaluations, which filters quote noise. **[inference; judgment]**
- **Rotation caps and the cost budget.**
  - At 25 round trips a week and 4% notional, costs are 25 × 52 × 0.0032% = 4.16% of equity a year, against goal.toml's cost_budget_pct_per_year = 4.5.
  - The headroom is 0.34% a year, about 2 extra round trips a week. Stressed ×1.5, costs are 6.24% a year, already over budget.
  - Rotations must therefore count inside the planned round trips and the cost budget, not on top of them.
  - Proposed caps: ≤ 3 rotations a day, and at most 20% of the week's round trips.
  - **[computed from [goal.toml](/home/user/AIresume/trading/goal/goal.toml)]**

### Gaps
- **No source retrieved for the optimizer's curse or error maximization.** The known references, not verified this session, are Smith & Winkler (2006), "The Optimizer's Curse", Management Science, and Michaud (1989), "The Markowitz Optimization Enigma".
- **No source retrieved for the claim that a proportional-cost (L1) penalty works as a robust estimator.** The likely reference, unverified, is DeMiguel & Olivares-Nadal (2018), Operations Research.
- **Alpha-decay methods not consulted:** Isichenko, *Quantitative Portfolio Management*; Di Mascio, Lines & Naik (2017), "Alpha Decay".
- **No empirical source on minimum-hold length, persistence filters or rotation caps for intraday-to-5-day equity books.** The proposed values are judgment and must be tuned in G1.

---

## 4. Is there evidence that cost-aware rotation or rebalancing improves net returns, and evidence of harm from overtrading and the winner's curse?

### Takeaway
- **The evidence is consistent in two directions:**
  - Cost-aware trading (bands, decay-weighted targets, netting, regime-aware speed) raises net results.
  - Trading on overconfident forecasts destroys value. Odean found that switching into "better" stocks lost about 3 points a year even before costs.
- **No retrieved study tests "rotate when the budget is full" for short-horizon US equity books.** The system has to prove it on its own data with a counterfactual ledger.

### Cited Findings
- **For:**
  - **Gârleanu-Pedersen.** Their policy beat naive benchmarks net of costs in commodity futures. **[single-source: abstract]** — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12080); [NBER](https://www.nber.org/papers/w15205)
  - **Novy-Marx & Velikov.** A buy/hold spread is the most effective simple cost mitigation. **[2+ sources]** — [NBER](https://nber.org/papers/w20721); [IDEAS](https://ideas.repec.org/a/oup/rfinst/v29y2016i1p104-147..html)
  - **DeMiguel et al. (2020).** Cost-aware combining nets trades and keeps 15 characteristics useful instead of 6. **[2+ sources]** — [Lancaster](https://eprints.lancs.ac.uk/id/eprint/133724/1/DMNU_Manuscript_InternetAppendix_2019_01_08.pdf); [ResearchGate](https://www.researchgate.net/publication/344722323_A_Transaction-Cost_Perspective_on_the_Multitude_of_Firm_Characteristics)
  - **Collin-Dufresne, Daniel & Sağlam (2020).** Out of sample, the dynamic cost-aware strategy beats a myopic one. **[single-source: abstract]** — [NBER w24222](https://www.nber.org/papers/w24222); [EPFL](https://actu.epfl.ch/news/new-paper-in-journal-of-financial-economics-for--2)
  - **Grinold & Kahn.** At least 75% of the incremental value added comes with 50% of the turnover. **[single-source: study notes]** — [Yan notes](https://people.brandeis.edu/~yanzp/Study%20Notes/Active%20Portfolio%20Management.pdf)
- **Against, or cautionary:**
  - **Barber & Odean (2000), "Trading Is Hazardous to Your Wealth".**
    - Sample: 66,465 households at a discount broker, 1991–1996 (old data, from the era of commissions).
    - The households that traded most earned 11.4% a year net, against 17.9% for the market. The least-active group earned 18.5%.
    - Gross returns were similar across groups; the gap came from costs.
    - The average household turned over about 75% of its portfolio a year (one secondary source says 70%).
    - The authors attribute the high trading to overconfidence.
    - **[2+ sources]** — [Barber & Odean, paper](https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf); [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:55:y:2000:i:2:p:773-806); [blog summary](https://darksideofthenudge.wordpress.com/2013/05/01/trading-is-hazardous-to-your-wealth-barber-odean-2000/)
  - **Odean (1999).** Stocks bought underperformed stocks sold, even excluding liquidity, tax, rebalancing and risk-reduction trades. **[2+ sources]** — [paper](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/doinvestors.pdf); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=94143). The gap is about 3.3 points over one year **[secondary only]** — [StudyCorgi](https://studycorgi.com/do-investors-trade-too-much-by-odean/). The average round-trip cost at the time is put at about 5% **[secondary only; verify]** — [search extract of summaries](https://www.essaysauce.com/finance-essays/do-investors-trade-too-much-summary/)
  - **Novy-Marx & Velikov.** Strategies turning over more than 50% a month rarely survive costs, and costs weaken statistical significance, which raises data-snooping risk. **[2+ sources]** — [NBER](https://nber.org/papers/w20721); [SUFE](https://academicnewsletter.sufe.edu.cn/info/353667)
  - **Frazzini, Israel & Moskowitz.** Short-term reversal is the strategy most constrained by trading costs. **[single-source]** — [AQR](https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs-of-Asset-Pricing-Anomalies)
  - **Kahn (2018).** Poor cost estimation and slipshod trading are a substantial drain. **[single-source]** — [CFA Institute RF](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2018/future-of-investment-management-kahn.pdf)

### Inferences
- **Two separate harms, and only one is gone.**
  - Barber-Odean's harm was mainly cost, in an era of commissions. Today's 8 bps round trip makes a single switch cheap.
  - Odean (1999) is a before-cost harm: the forecasts behind switches were wrong on average. That mechanism (forecast noise plus selection, as computed in question 3) applies fully to a model that picks the best of 1,000+ names.
  - So low costs do not make rotation safe. Calibration and a margin are what make it safe.
- **Rotation must be proven on the system's own data.** A rotation rule should be enabled only if G1 history shows a positive mean realized switch value: the candidate's realized net P&L minus the closed position's shadow P&L over its planned remainder, both under their own exit rules. This is Odean's test applied to the system's own decisions.

### Gaps
- **No study was found on budget-full rotation for intraday-to-5-day US equity systems.**
- **Unverified numbers:** GP's net Sharpe ratios, Odean's 3.3-point gap and the ~5% cost figure, and the published (rather than draft) DeMiguel turnover numbers.
- **The winner's-curse literature** (Smith & Winkler 2006; Harvey-Liu; Bailey-López de Prado) was not retrieved this session. The goal's [METHOD.md](/home/user/AIresume/trading/goal/METHOD.md) already cites Bailey & López de Prado's deflated Sharpe and backtest-overfitting papers for strategy selection **[local]**.

---

## 5. Is a hard cap on the number of positions still useful as an operational guard? What do risk managers use instead?

### Takeaway
- **Keep a count limit as a runaway guard, not as the allocator.** Set it from the budget arithmetic (about 25) so that it never binds in normal operation, and alert whenever it does.
- **What actually bounds and shapes the book:**
  - the open-risk budget, per side and in total;
  - a minimum position size;
  - per-position notional caps;
  - gross, overnight, industry and net limits;
  - order-rate throttles and the kill switch (already in the goal);
  - a concentration metric such as the effective number of positions on risk.
- **Without a minimum position size, the count is unbounded.** That is the real reason a cap or floor is still needed.

### Cited Findings
- **Throttles already in the goal.**
  - At most 2 orders a second and 120 a minute.
  - At most 4 round trips per name a day.
  - At most 300% of equity traded a day.
  - Pre-trade checks of every limit on confirmed positions plus open orders as if filled.
  - A kill switch, including a second path through the broker that does not depend on the trading process.
  - **[local]** — [goal.toml](/home/user/AIresume/trading/goal/goal.toml) (keys max_orders_per_second, max_orders_per_minute, max_round_trips_per_symbol_per_day, max_traded_pct_per_day; controls C13 and the kill-switch control)
- **The goal treats "a runaway loop sends orders without limit" as obstacle O2.** It is mitigated by rate limits, duplicate blocking, per-name and daily throttles, and the kill switch. **[local]** — [GOAL.md](/home/user/AIresume/trading/goal/GOAL.md)
- **The goal's regulatory control baseline** is SEC Rule 15c3-5, FINRA Notice 15-09 and EU RTS 6: pre-trade limits, kill switch, monitoring, testing and change management. **[local; the regulations themselves were not re-read this session]** — [METHOD.md](/home/user/AIresume/trading/goal/METHOD.md)

### Inferences
- **The open-risk budget limits the sum of risk, not the count.** 2% could be split into 200 positions risking 0.01% each. The count is bounded only by a minimum size, so the goal should state one:
  - min_position_risk_pct = 0.1 (equal to the "risk-bearing" threshold, so every position counts as evidence);
  - optionally, a minimum notional (e.g. 1% of equity) so whole-share rounding and monitoring overhead stay small relative to each position's expected dollar gain.
- **With a 0.1% floor, the natural maximum is 20 positions** (2.0/0.1), and 15 per side (1.5/0.1). A guard of max_positions_guard = 25 allows for positions being closed, trapped or below the floor after partial fills. It should never bind in G1 or on paper; if it binds, new entries are blocked and the owner is alerted.
- **Concentration measures:**
  - The effective number of positions on risk is N_eff = (ΣR_i)² / ΣR_i², the inverse Herfindahl of risk shares.
  - With a 0.5% per-position cap and a full 2% budget, N_eff ≥ 4 automatically.
  - Correlated positions are really one bet. The goal's overnight industry limit (8%) and beta-adjusted net limit (15%) cover that. An effective-number-of-bets measure (Meucci) on factor exposures is optional reporting.
- **Order load.** A rotation takes about 4 orders: cancel the old stop, close, open, place the new stop. At 120 orders a minute that is not binding. But capping rotations keeps the API reserve for exits and reconciliation, which the goal already requires (api_reserve_pct).

### Gaps
- **Alpaca broker limits were not verified this session.** I believe the API rate limit is 200 requests per minute per account, and any limit on open orders per account is unknown. Check Alpaca's current documentation.
- **Not retrieved:** Meucci's "Managing Diversification" (effective number of bets), and any survey of how often managers use max-names constraints.

---

## 6. With these limits, how many positions can the book hold at most, and what bounds it naturally?

### Takeaway
- **By risk at the stop:**
  - at 0.5% per position, only 4 positions fit (3 per side);
  - at the 0.1% "risk-bearing" floor, 20 fit (15 per side).
- **The goal's own activity plan does not fit 0.5% sizing.** 25 round trips a week with a typical 3-day hold implies about 15 positions open on average (Little's law). That forces an average risk near 0.13% per position.
- **Overnight, the 4% notional cap sets risk = 4% × stop distance.** So the binding limit switches from overnight gross to open risk once stops exceed about 2.67%.

### Cited Findings
- **The relevant limits in goal.toml** **[local]** — [goal.toml](/home/user/AIresume/trading/goal/goal.toml):

  | Limit | Value |
  |---|---|
  | risk_per_position_pct | 0.5 |
  | max_open_risk_pct | 2.0 |
  | max_open_risk_per_side_pct | 1.5 |
  | max_positions | 20 |
  | max_position_pct | 10 |
  | max_position_overnight_pct | 4 |
  | typical_position_pct | 4 |
  | max_overnight_gross_pct | 75 |
  | max_gross_exposure_pct | 100 |
  | risk_bearing_min_risk_pct | 0.1 |
  | planned_risk_trades_per_week | 25 |
  | typical_holding_minutes | 1170 (3 trading days) |
  | cost_budget_pct_per_year | 4.5 |
  | entry_min_gain_to_cost | 2 |
  | max_position_adv_pct | 0.02 |

### Inferences
- **Capacity by risk per position.** Throughput is the round trips a week the book can sustain at a 3-day hold. **[computed]**

  | Risk per position | Max positions (total) | Max per side | Throughput at 3-day hold |
  |---|---|---|---|
  | 0.5% | 4 | 3 | 6.7 round trips a week |
  | 0.25% | 8 | 6 | 13.3 |
  | 0.2% | 10 | 7 | 16.7 |
  | 0.15% | 13 | 10 | 21.7 |
  | 0.133% | 15 | 11 | 25.0 |
  | 0.1% | 20 | 15 | 33.3 |

- **Little's law** (open positions = arrival rate × holding time): 5 round trips a day × 3 days = 15 open on average. So the plan only fits if positions average about 0.13% risk.
  - Either "risk_per_position_pct = 0.5" is a maximum and most positions are smaller, or the plan's activity and holding time conflict with full-size positions.
  - The goal should say which. Recommended: make 0.5% the per-position maximum and size by value per unit of risk between 0.1% and 0.5%.
  - **[computed]**
- **Overnight positions at the 4% notional cap.** Risk = 4% × stop distance, so the stop width decides which limit binds. **[computed]**

  | Stop distance | Risk per position | Positions in 2% open risk | Gross used | Binding limit |
  |---|---|---|---|---|
  | 2% | 0.08% (below "risk-bearing") | 25 | 100% | overnight gross caps the book at 18 positions (72%) |
  | 2.5% | 0.10% | 20 | 80% | overnight gross (75%) still caps it at 18 |
  | 3% | 0.12% | 16 | 64% | open risk |
  | 4% | 0.16% | 12 | 48% | open risk |
  | 5% | 0.20% | 10 | 40% | open risk |
  | 12.5% | 0.50% | 4 | 16% | open risk (full 0.5% risk overnight needs a 12.5% stop) |

  The crossover is max_open_risk / gross limit: 2.0/75 ≈ 2.67% overnight and 2.0/100 = 2% intraday.
- **ADV does not bind at this size.** 2% of the $20M minimum ADV is $400,000, far above the $10,000 maximum position. **[computed]**
- **The natural bound** is therefore min(floor(2.0 / minimum risk), floor(1.5 / minimum risk) per side, the gross and overnight-gross limits ÷ notional). With a 0.1% floor that gives at most 20, and 15 to 20 in practice. A hard cap of 20 equals the risk-budget bound exactly, so as an allocator it is redundant; it only adds value as a guard set above the bound.

### Gaps
- **Little's law is a standard queueing identity** (L = λW); no web source was retrieved this session.
- **Whether risk_per_position_pct = 0.5 is a fixed size or a cap** is a decision for the owner. The arithmetic above shows the plan needs it to be a cap.

---

## 7. What concrete, testable rule should the goal state? (Recommended rule, confidence, and evidence for and against)

### Takeaway
- **Replace max_positions = 20 as the allocator with four parts:**
  1. Budget-based allocation with a minimum position size. Every limit is checked as if filled, and the count falls out.
  2. A rotation rule that compares value net of switching cost and of the opportunity cost of the binding budget, with an uncertainty margin.
  3. Anti-churn safeguards: calibrated forecasts, persistence, a minimum hold, rotation caps, no same-day re-entry, and counting rotations inside the round-trip and cost budgets.
  4. A derived count guard of 25, plus a counterfactual ledger that switches rotation off if it does not pay.
- **Confidence:**
  - High (about 85%) that budget-based allocation with a size floor is right.
  - High (about 80%) that the rotation rule has the right economic form.
  - Medium (about 55–60%) that rotation adds net value for this system at all. A single rotation's value is small next to forecast noise, so it must pass the G1 test before it is switched on.

### Cited Findings
- **Hysteresis and bands are the most effective simple cost control.** **[2+ sources]** — [Novy-Marx & Velikov, NBER](https://nber.org/papers/w20721); [IDEAS](https://ideas.repec.org/a/oup/rfinst/v29y2016i1p104-147..html)
- **Proportional costs give a no-trade region.** **[2+ sources]** — [Lynch & Tan](https://archive.nyu.edu/bitstream/2451/26507/2/02-63.pdf); [MPRA](https://mpra.ub.uni-muenchen.de/117162/1/Sweep_paper-4.pdf)
- **Value signals by their decay and trade only partway toward the aim.** **[2+ sources]** — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1444706); [Hedegaard, AQR](https://www.aqr.com/-/media/AQR/Documents/Insights/Working-Papers/Robust-Dynamic-Asset-Allocation-With-Model-Misspecification.pdf)
- **Switching on one's own forecasts lost value before costs.** **[2+ sources]** — [Odean](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/doinvestors.pdf); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=94143)
- **High turnover destroys net returns.** **[2+ sources]** — [Barber & Odean](https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf); [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:55:y:2000:i:2:p:773-806)
- **Netting avoids paying two round trips.** **[2+ sources]** — [DeMiguel et al.](https://eprints.lancs.ac.uk/id/eprint/133724/1/DMNU_Manuscript_InternetAppendix_2019_01_08.pdf); [UC3M](https://researchportal.uc3m.es/display/act524892)
- **Costs are regime-dependent, so bands should widen in high volatility.** **[single-source]** — [NBER w24222](https://www.nber.org/papers/w24222)

### Inferences
**Proposed goal text.** Statements first; parameter values are starting points to be tuned in G1.

1. **Allocation (replaces max_positions as an allocator).** "There is no fixed number of positions. A position opens when it passes the entry rule and every limit holds after it as if filled: open risk in total and per side, gross, overnight gross, per-position notional, industry, net and the daily-loss budget. Each position risks between min_position_risk_pct (0.1) and risk_per_position_pct (0.5, now a maximum), sized by its expected gain per unit of risk."
   - Test: count of positions opened below the floor or above the cap = 0.
2. **Rotation.** "When a candidate passes the entry rule but a limit blocks it, the system may close or trim held positions to make room, lowest value per unit of the binding limit first. It does so only when v_j − Σv_i ≥ m."
   - Definitions:
     - v_j = g_j − C_j − κ·R_j·H_j
     - v_i = g_i − κ·R_i·H_i − ΔX_i
     - g = calibrated expected gain under the position's own stop and exit rules: from entry to planned exit for the candidate, from now to planned exit for a held position. P&L to date is never used.
     - C_j = the candidate's stressed round-trip cost (×1.5).
     - ΔX_i = the extra cost of exiting now rather than as planned.
     - κ = trailing 20-session median of entries' (g − C)/(R·H), floored at 0.
     - R = loss at stop, or notional when gross binds.
     - m = max(C_j, z·σ_S), with z = 1.
   - Every rotation records g_j, C_j, g_i, ΔX_i, κ, the R and H of both sides, m, and the decision.
   - Test: rotations with v_j − Σv_i < m = 0.
3. **Safeguards.**
   - Minimum hold: no voluntary rotation out of a position younger than max(15 min, 20% of its planned holding time).
   - Persistence: the candidate's advantage must hold at two consecutive evaluations.
   - Caps: at most max_rotations_per_day = 3, and rotations at most 20% of the week's round trips.
   - Re-entry: a name rotated out is not re-entered in the same session, and a rotation never closes and reopens the same name and direction (netting).
   - Budgets: rotations count as round trips for C13, for planned_risk_trades_per_week and for cost_budget_pct_per_year.
   - Market state: when the market-wide median spread or volatility is above its 90th percentile, rotation is suspended.
   - Test: violations = 0.
4. **Proof that rotation pays.**
   - For every rotation, a shadow ledger follows the closed position from the rotation to its planned exit under its own stop and exit rules.
   - Realized switch value = (candidate's realized net P&L) − (shadow P&L of the closed positions) − ΔX.
   - Rotation stays enabled only if, over at least 50 rotations in G1, the mean realized switch value is positive with a one-sided bootstrap 90% lower bound above 0.
   - On paper, if the first 30 rotations show a mean below 0 at t < −1, rotation switches off until the owner reviews it.
   - Calibration: the calibration of g on top-ranked candidates (realized vs predicted by decile) is reported each review.
5. **Guard.** "max_positions_guard = 25. It never binds in normal operation. Reaching it blocks new entries and alerts the owner."
   - Test: binding events in G1 and on paper = 0.
   - Also report N_eff = (ΣR)²/ΣR² daily.
6. **Consistency fix.** State that risk_per_position_pct = 0.5 is a maximum, since the activity plan implies about 15 open positions averaging about 0.13% risk. Alternatively, revise planned_risk_trades_per_week or typical_holding_minutes.

**Evidence for this design:**
- Bands and hysteresis cut costs most effectively (Novy-Marx & Velikov).
- Optimal policies under proportional costs are no-trade regions (Constantinides; Davis-Norman; Liu; de Lataillade et al.).
- Decay-aware targets beat naive ones net of costs (Gârleanu-Pedersen).
- Netting saves round trips (DeMiguel et al.).
- Regime-aware speed helps out of sample (Collin-Dufresne, Daniel & Sağlam).
- The κ-adjusted comparison is ordinary capital budgeting.
- The greedy per-unit-resource ranking is optimal for divisible positions.

**Evidence against, or risks:**
- A single rotation's value is small (the worked example: about 3.6 bps of notional) next to forecast noise.
- Best-of-N selection biases forecasts upward by roughly 3 noise standard deviations for 1,000–2,000 names (computed).
- Odean's "bought underperformed sold" and Barber-Odean's turnover harm show that switching on one's own forecasts tends to lose.
- Rotation raises turnover in a system already far above the turnover levels where anomalies survive costs (Novy-Marx & Velikov).
- The cost budget has only about 2 round trips a week of headroom (computed).
- So rotation is worth having only if the ledger proves it. The default should be "implemented, enabled only after the G1 test passes".

### Gaps
- **Parameter values are judgment, not sourced:** z, the minimum hold, the caps, the 90th-percentile suspension, the 50/30-rotation test sizes and the guard of 25. They should be set in G1 with walk-forward tuning and registered before paper trading.
- **Unverified in this session** (no source retrieved; checks needed before the final report cites them):
  - the exact GP formulas and empirical numbers;
  - Grinold & Kahn's no-trade and amortization equations;
  - the Novy-Marx & Velikov thresholds;
  - Smith & Winkler (optimizer's curse);
  - Meucci (effective number of bets);
  - Alpaca's API limits;
  - Odean's 3.3-point and 5%-cost figures.

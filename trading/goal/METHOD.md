# How the goal is defined (the method)

We define the goal before any architecture or code, then work top-down. No single standard covers
"define the goal of an autonomous trading system", so we combine established methods, each for the
part it was built for. Every one of them is in use in large organizations: requirements engineering,
systems engineering, investment management, and supervision of algorithmic trading.

| Layer | Method | What it gives the goal |
|---|---|---|
| 1. Intent and scope | ISO/IEC/IEEE 29148 stakeholder needs | why the system exists, for whom, and what is out of scope |
| 2. Goal tree | KAOS goal-oriented requirements engineering (van Lamsweerde) | the top goal refined into sub-goals until each is measurable and assignable; *obstacles* to each goal with their resolutions |
| 3. Objectives and constraints | CFA Institute Investment Policy Statement (IPS) | return and risk objectives; constraints on horizon, liquidity, legal and regulatory matters, taxes, unique circumstances |
| 4. Measures | INCOSE technical measurement (MOE, MOP, KPP) with GQM (Basili) | each objective measured from the owner's viewpoint (MOE), what the system must achieve (MOP), and the few parameters whose failure stops the program (KPP), each with a threshold |
| 5. Statement quality | ISO/IEC/IEEE 29148 characteristics | every statement necessary, unambiguous, singular, feasible, verifiable, and free of design |
| 6. Evidence | Fed SR 11-7 model risk management; *A Backtesting Protocol* (Arnott, Harvey, Markowitz); the Deflated Sharpe Ratio, the Probabilistic Sharpe Ratio and minimum track record length (Bailey, López de Prado); the probability of backtest overfitting | how we will know the goal is met without fooling ourselves: pre-registration, out-of-sample data, correction for every strategy tried, effective challenge |
| 7. Control baseline | SEC Rule 15c3-5 (Market Access), FINRA Regulatory Notice 15-09, EU RTS 6 (Delegated Regulation 2017/589) | the controls regulators expect of any algorithmic trader: pre-trade limits, kill switch, monitoring, testing, change management |
| 8. Decision gates | stage gates with pre-registered decision rules | research, then paper trading, then live trading with a small amount; entry and exit criteria for each, and when to stop |
| 9. Outside view | reference class forecasting (Kahneman, Lovallo, Flyvbjerg) | how ambitious the goal can be, judged from how similar efforts turned out, not from our own plans |

OKRs (objectives and key results) are used only as the one-page summary at the top of `GOAL.md`.

## How each layer is applied

**Intent and scope.** One mission sentence, the stakeholders and what each needs, and explicit
non-goals. The viewpoint is the owner's.

**Goal tree (KAOS).** The top goal is AND-refined: it is met only if all its sub-goals, the objectives,
are. Each objective is one of three kinds: *achieve* (reach a state), *maintain* (keep a property
always) or *avoid* (never reach a state). Its key results are the measures that decide it. Each
objective lists its *obstacles*, the ways it could fail, and the resolution for each. Most of the risk
rules come from obstacles.

**Objectives and constraints (IPS).** The investment part of the goal uses the IPS headings:
- return objective, stated both as a Sharpe ratio and as a return a year, and risk objective, stated
  as the largest losses the owner accepts;
- time horizon, here the holding period;
- liquidity, here the tradable universe;
- legal and regulatory;
- taxes;
- unique circumstances: a paper account first, a broker API, an autonomous decision-maker.

**Measures (INCOSE, GQM).** Each objective is the goal in GQM's sense, seen from the owner's
viewpoint, and states the question its key results answer: the object measured, the purpose and the
quality focus. Every key result is a metric that answers it, and names:
- the metric, its unit, a threshold value and, where useful, a better objective value;
- the measurement window and the data;
- the verification method (test, analysis, inspection or demonstration, as ISO 29148 lists them);
- the gate it belongs to.

A few are marked KPP: failing one stops the program until the owner decides.

**Statement quality (ISO 29148).** Each statement must be:
- necessary: it traces to an objective;
- unambiguous: no vague words such as "fast", "robust" or "constantly";
- singular: one thing per statement;
- feasible: tested, see below;
- verifiable: it has a metric, a threshold and a method;
- free of design: it says what, not how.

The set of statements must be complete, consistent and possible to validate.

**Evidence (SR 11-7 and the backtest literature).** SR 11-7 asks for three things:
- conceptual soundness;
- outcomes analysis, including back-testing;
- ongoing monitoring, all under *effective challenge* by competent, independent people.

The backtest literature adds:
- hypotheses written down before they are tested;
- untouched out-of-sample data;
- every variant tried counted, so the Sharpe ratio can be deflated for selection bias;
- track records long enough to tell skill from luck.

**Control baseline.** The goal adopts the controls those rules require, even though on paper and as a
customer the broker is the regulated party:
- limits on credit, size and price before each order;
- detection of duplicate orders;
- a kill switch;
- real-time monitoring and alerts;
- reconciliation after trading;
- testing and controlled deployment of changes;
- protection of credentials;
- regular review.

Knight Capital's 2012 loss came from failures of exactly these kinds: a deployment error, alerts no one
treated as alerts, and no control to halt its own runaway orders.

**Decision gates.** Each stage tests a different hypothesis, so none repeats another:
- **G1, research on history:** is there an edge, net of costs, on data not used to find it? Only a
  long history can answer this.
- **G2, paper trading:** does the live system do what the tested strategy does, unattended and within
  every limit, and does it make money once paper's flattering fills are corrected? A few months of
  paper can't prove an edge, so G2 checks the system, not the edge.
- **G3, live with a small amount:** do real fills match the cost model? From then on a sequential test
  keeps weighing the live record, and capital grows only while it favors the edge.

The pass and fail rules for each gate are fixed before its data exists.

**Outside view.** We place the project in its reference class:
- systematic short-horizon trading by a small participant;
- most retail day traders lose money;
- published anomalies decay after publication;
- high-speed firms own the shortest horizons.

From that class we set how likely a new strategy is to have a real edge, and we choose gate thresholds
so that a strategy that passes is probably real.

## Testing the goal non-circularly

A test is circular when it uses the goal's own claims as evidence for the goal. Each test of the goal
therefore has an *oracle*, the source of the right answer, that lies outside the goal:

| Test | Oracle (where the right answer comes from) |
|---|---|
| GT-1 statement quality | the characteristics in ISO/IEC/IEEE 29148, applied as rules |
| GT-2 internal consistency | arithmetic and logic on the stated limits; queueing theory (Little's law, Erlang's loss formula); real price gaps and named market events |
| GT-3 cost feasibility | published fee schedules (SEC, FINRA, Alpaca) and spread data, with volatility measured on real prices |
| GT-4 gate power and false passes | simulated strategies whose true edge is known because we set it |
| GT-5 null strategies on real data | random strategies, which have no edge by construction, run on real price history |
| GT-6 metric gaming (Goodhart) | strategies built to look good while having no edge, or hidden risk |
| GT-7 control coverage | the checklists in SEC 15c3-5, FINRA 15-09, RTS 6, MiFID II record and clock rules, SR 11-7, and the Knight Capital order |
| GT-8 outside view | published base rates for traders and trading strategies |
| GT-9 effective challenge | independent reviewers who see only the goal documents |

A test fails the goal when the goal would let a no-edge strategy through too often, would stop a
real edge too often, contradicts itself, cannot be measured, or misses a control the checklists
require. The goal is revised until every test passes, and `REPORT.md` records each revision.

## Sources

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements
  engineering* (summaries: [IREB/CFTL slides](https://cftl.fr/wp-content/uploads/2023/12/Telecharger-la-presentation-complete-10.pdf), [arXiv 2408.10886](https://arxiv.org/pdf/2408.10886))
- A. van Lamsweerde, KAOS: [goal-oriented RE overview](https://webperso.info.ucl.ac.be/~avl/files/avl-markt07.pdf); van Lamsweerde & Letier, "Handling Obstacles in Goal-Oriented Requirements Engineering", IEEE TSE 2000
- INCOSE, *Technical Measurement Guide* (INCOSE-TP-2003-020-01): [summary](https://www.psmsc.com/Downloads/TWGMarch06/02_TechnicalMeasurementGuide_Roedler.pdf)
- V. Basili et al., "The Goal Question Metric Approach" (1994): [Basili's GQM slides](https://www.cs.umd.edu/users/basili/qip/tsld025.htm)
- CFA Institute, *Elements of an Investment Policy Statement*: [institutional](https://rpc.cfainstitute.org/-/media/documents/article/position-paper/investment-policy-statement-institutional-investors.pdf), [individual](https://rpc.cfainstitute.org/-/media/documents/article/position-paper/investment-policy-statement-individual-investors.pdf)
- Federal Reserve, [SR 11-7, Guidance on Model Risk Management](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm) (2011)
- SEC, [Rule 15c3-5 adopting release 34-63241](https://www.sec.gov/rules/final/2010/34-63241.pdf) and [small entity guide](https://www.sec.gov/rules/final/2010/34-63241-secg.htm); SEC, [Knight Capital order](https://www.sec.gov/news/press-release/2013-222) (2013)
- FINRA, [Regulatory Notice 15-09](https://www.finra.org/rules-guidance/notices/15-09) (2015)
- EU, [Delegated Regulation 2017/589 (RTS 6)](https://www.legislation.gov.uk/eur/2017/589/data.html)
- D. Bailey, M. López de Prado, ["The Deflated Sharpe Ratio"](https://papers.ssrn.com/abstract=2460551), JPM 2014; ["The Sharpe Ratio Efficient Frontier"](https://www.risk.net/journal-risk/2223785/sharpe-ratio-efficient-frontier) (PSR, minimum track record length), J. of Risk 2012
- D. Bailey, J. Borwein, M. López de Prado, Q. Zhu, ["The Probability of Backtest Overfitting"](https://papers.ssrn.com/abstract=2326253), J. Computational Finance 2017
- R. Arnott, C. Harvey, H. Markowitz, ["A Backtesting Protocol in the Era of Machine Learning"](https://papers.ssrn.com/abstract=3275654), J. Financial Data Science 2019
- C. Harvey, Y. Liu, H. Zhu, ["…and the Cross-Section of Expected Returns"](https://www.nber.org/papers/w20592), RFS 2016
- R. D. McLean, J. Pontiff, ["Does Academic Research Destroy Stock Return Predictability?"](https://Www.Gwern.net/doc/economics/2016-mclean.pdf), J. Finance 2016
- B. Barber, Y.-T. Lee, Y.-J. Liu, T. Odean, ["The Cross-Section of Speculator Skill"](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf), J. Financial Markets 2014
- F. Chague, R. De-Losso, B. Giovannetti, ["Day Trading for a Living?"](https://econpapers.repec.org/RePEc:fgv:eesptd:525) (2019)
- Reference class forecasting: [PMI, "Planning for the planning fallacy"](https://www.pmi.org/learning/library/planning-fallacy-causes-solutions-project-expectations-6374)

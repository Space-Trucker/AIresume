# Independent reviewer before each gate (G1 backtest, G2 paper trading, G3 real money): AI, human, or both, and who rules

Research date: 2026-10-15. Scope: goal decision 6 in `/home/user/AIresume/trading/goal/GOAL.md` (lines 456-457), KR6.2 (line 295) and C12 (line 414). Current default in the goal: one AI reviewer, a separate instance that sees only the evidence; the owner rules on every finding; never a Fable model (claude-fable-*).

How the sources were read: the session's network policy blocked every direct page fetch (HTTP 403 on CONNECT for federalreserve.gov, occ.gov, finra.org, bankofengland.co.uk, arxiv.org, orrick.com, jdsupra.com, blog.iclr.cc). All findings below come from search-engine extracts of the cited pages. Quoted wording comes from those extracts and should be checked against the primary document before it is quoted verbatim in the final report. The web-search budget ran out before one last check (SEC, see Gaps in section 2). "Single-source" marks a fact that only one independent source confirmed.

## Question 0 (synthesis): which reviewer arrangement, when is each worth its cost, and who rules?

### Takeaway
Recommendation, moderate confidence (about 65%):
- **G1 and G2:** a panel of 2 or 3 AI reviewers, each blind and working alone, from at least two vendors other than the builder's family (never a Fable model). Each reviewer gets the evidence and the pre-registered criteria, not the builder's account of the results. Machine-checked reproduction of the headline numbers runs alongside the panel.
- **Before G3:** add one fixed-fee human expert review when the capital at risk justifies it. If only one human review can be bought, buy it for the G1 statistical evidence, because G2 checks fidelity, not edge.
- **Who rules:** the owner, under rules fixed in advance:
  - a written disposition for every finding;
  - a blocking severity class the owner cannot waive alone;
  - a reviewer check that each disposition was carried out;
  - logs with timestamps.

The current default (one same-family AI instance) is the weakest of the defensible options. Self-preference, similarity bias and correlated errors are documented for exactly that setup.

### Cited Findings
- The US banking agencies rescinded SR 11-7 and OCC Bulletin 2011-12 on 2026-04-17 and replaced them with SR 26-2 / OCC Bulletin 2026-13. The new guidance keeps effective challenge, now defined as needing "expertise", "sufficient independence to permit objectivity" and "organizational standing and influence to effect change". It is non-binding and excludes generative and agentic AI from its scope. — [Fed SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm); [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html); [Orrick](https://www.orrick.com/en/Insights/2026/04/Agencies-Overhaul-Model-Risk-Management-Guidance-for-Banks-Heres-What-Changed); [Sullivan & Cromwell](https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management) (details in section 1).
- LLM evaluators recognise and favour their own generations. The strength of self-preference correlates linearly with how well the model recognises its own text. — [NeurIPS 2024, Panickssery et al.](https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html); [arXiv 2404.13076](https://arxiv.org/abs/2404.13076v1)
- LLM judges score models that resemble themselves higher, and model errors become more correlated as capability grows. — [ICML 2025, Goel et al.](https://proceedings.mlr.press/v267/goel25b.html); [arXiv 2502.04313](https://arxiv.org/html/2502.04313v2)
- Across more than 350 LLMs, two models agree on about 60% of the questions they both get wrong (one leaderboard). Shared developer and shared architecture raise this correlation. — [ICML 2025, Kim et al.](https://proceedings.mlr.press/v267/kim25e.html); [arXiv 2506.07962](https://arxiv.org/abs/2506.07962v1)
- A panel of smaller judges from disjoint model families beat a single GPT-4 judge, showed less intra-model bias, and cost over 7 times less. — [arXiv 2404.18796](https://arxiv.org/html/2404.18796v2); [Cohere](https://cohere.com/research/papers/replacing-judges-with-juries-evaluating-llm-generations-with-a-panel-of-diverse-models-2024-04-29)
- On real errors in published papers (errors serious enough for errata or retraction), the best model (o3) reached only 21.1% recall and 6.1% precision. Models rarely found the same errors again across 8 runs. — [arXiv 2505.11855 (SPOT)](https://arxiv.org/abs/2505.11855v1); [EleutherAI](https://www.eleuther.ai/papers-blog/when-ai-co-scientists-fail-spot-a-benchmark-for-automated-verification-of-scientific-research)
- Human-plus-LLM-critic teams caught about as many bugs as the LLM critic alone, with fewer hallucinated bugs. Critiques written by the model were preferred over human critiques 63% of the time. — [arXiv 2407.00215 (CriticGPT)](https://arxiv.org/html/2407.00215v1); [SiliconANGLE](https://siliconangle.com/2024/06/27/openais-criticgpt-uses-generative-ai-spot-errors-generative-ais-outputs/)
- The AAAI-26 pilot gave AI reviews for all 22,977 full-review papers. Participants preferred them to human reviews on technical accuracy and on research suggestions. The authors also report errors in reading equations and tables and trouble ranking which issues matter, and they conclude that humans and AI have complementary strengths. — [arXiv 2604.13940](https://arxiv.org/pdf/2604.13940); [Crypto Briefing](https://cryptobriefing.com/first-double-blind-ai-evaluations-piloted/)
- JPMorgan "London Whale" (2012): the Model Review Group spotted the spreadsheet problems. It still approved the VaR model on conditions (automate it, fix a flaw) that were never carried out. It was under pressure from the trading side and "may have been more willing to overlook the operational flaws". — [SOA Financial Reporter 2015](https://www.soa.org/493734/globalassets/assets/library/newsletters/financial-reporter/2015/june/fr-2015-iss101-chan.pdf); [IFR](https://www.ifre.com/story/1744757/derivatives-jpm-report-unveils-var-errors); [CFO.com](https://cfo.com/news/jpmorgan-cfos-slammed-for-risk-management-failures/666556/)
- FINRA's 2026 oversight report (9 December 2025) suggests checking AI outputs through human-in-the-loop review and logging prompts and outputs. — [Debevoise](https://www.debevoise.com/insights/publications/2025/12/finras-2026-regulatory-oversight-report-continued); [Mayer Brown](https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2025/12/finra-2026-regulatory-oversight-report.pdf%3Frev=-1)

### Inferences
**What effective challenge means for one owner.** The three elements (expertise, independence/incentives, standing/influence) map onto this setup as follows:
- **Expertise:** frontier LLMs are competent on checklists and code-level checks. Their recall on subtle statistical and conceptual errors is low (SPOT).
- **Independence:** an AI reviewer has no financial stake. It does carry sycophancy, self-preference and similarity bias. A paid human consultant has a mild incentive to please the client. A fixed fee that does not depend on the verdict reduces that incentive.
- **Standing:** in a one-person system, standing cannot come from an org chart. It has to be built as rules fixed in advance that the owner cannot quietly bypass. The London Whale failure was a standing failure: the findings were known, the conditions were not enforced, and the reviewer was under pressure.

**Recommended arrangement, gate by gate:**
1. **G1 (backtest; no money at risk).** First, machine-checked reproduction: scripts recompute the Deflated Sharpe, the out-of-sample results and the lag audit from raw artefacts and the variant registry. Then a blind AI panel:
   - 2 or 3 reviewers, at least two of them from vendors other than the builder's family. If the builder is a Claude model, include at least one GPT-family and one Gemini-family reviewer. A non-Fable Anthropic model may be a third member, never a Fable model.
   - Each reviewer works alone, without debate.
   - Take the union of findings and remove duplicates.
   - Each finding must point to an artefact and give a step to reproduce it.

   **Human expert at G1:** optional by default. It is the best place to spend a single human review when the planned capital is material. A statistical flaw found at G1 costs nothing; found at G3 it costs the 120-day paper period. G2 tests fidelity to the frozen strategy, not whether the edge is real. So an overfit strategy can pass G2, and the G3 decision rests heavily on the G1 statistics.
2. **G2 (120 days of paper trading; fidelity vs a rerun).** The evidence is mostly mechanical comparison. Use machine checks plus the same blind AI panel. A human adds little here unless the panel or the checks raise something new.
3. **G3 (real money).** Two parts:
   - The AI panel reviews the whole package: G1 and G2 evidence plus operational readiness.
   - A human expert reviews it once per strategy, or after any material change, when the capital at risk passes a threshold (rule below). The human sees the evidence, the panel's findings and the owner's dispositions. The human's job includes challenging the dispositions, since the London Whale lesson is that conditions get waived.

**When a human review pays.** It is worth buying when P × L > C:
- P = chance the human catches a gate-invalidating error that the panel and the machine checks missed;
- L = loss avoided, bounded by the goal's own loss limits (about loss-limit % × capital);
- C = cost of the review.

Illustration only, with assumed numbers:
- P = 10-20%, loss limit 20% of capital, C = $2,000-$6,000 (about 10-20 hours at $150-$300 an hour, section 4).
- The review then pays above roughly $50k-$300k of capital at risk.
- Below that, a small live allocation with a hard loss limit plus the AI panel is the cheaper challenge, and the human review is bought before scaling up.

These figures are illustrative. Neither P nor the cost of a quant review is well measured (see Gaps).

**Who rules.** The owner rules on every finding. The owner is accountable and it is the owner's capital. The supervisory pattern is the same: validators challenge and approvers decide; SS1/23 makes the approving body responsible for ensuring validation recommendations are acted on (section 1). The owner is not independent, though: they have an incentive to go live. So the rules are:
- (a) Gate criteria are pre-registered, with external timestamps (already in the goal: KR6.1, O6).
- (b) Every finding gets a written disposition: fix (with evidence), accept the risk (with a rationale and a compensating control), or reject (with evidence).
- (c) A "blocking" class (a finding that invalidates a gate metric) cannot be waived by the owner alone. It needs a fix and a re-review, or agreement from a second independent reviewer (a human, or an AI from a different vendor).
- (d) The reviewer checks dispositions for closure before the gate passes.
- (e) Everything is logged.

**Evidence for and against.**
- For: the AI panel costs little and can run at every gate. LLM feedback overlaps with human reviewers about as much as two humans overlap with each other (Liang et al.). LLM critics catch more inserted bugs than paid human contractors (CriticGPT). Human-plus-AI teams cut false findings (CriticGPT; AAAI-26). Different-vendor panels reduce correlated bias (PoLL; Goel; Kim).
- Against:
  - AI recall on real errors is low (SPOT 21%), which argues for a human at every gate.
  - Human reviewers also miss errors and wave findings through (London Whale; Bosu et al. on fatigue). Human peer reviewers disagree a lot: in the NeurIPS consistency experiment they reached a balanced accuracy of only about 0.66.
  - A different vendor reduces error correlation but does not remove it. More accurate models are more correlated even across providers (Kim et al.).
  - No regulator found endorses an AI-only effective challenge. SR 26-2 puts GenAI outside its scope.
  - For small capital, a human review can cost more than the loss it could prevent.

**Confidence by part:**
- A cross-vendor blind panel beats one same-family instance: high (about 85%).
- The owner rules, under pre-committed blocking and disposition rules: high (about 80%).
- AI-only at G1/G2 with a human before real money: moderate (about 65%).
- The exact capital threshold for human review: low (about 50%).

**Cheap check on the AI panel itself.** Before relying on the panel, plant known flaws (for example a one-bar look-ahead, survivorship in the universe, an unregistered variant) in a copy of the evidence pack and measure what fraction the panel catches. This copies the SPOT method of testing against known errors. It matches FINRA's expectation that a GenAI tool's reliability and accuracy are governed (RN 24-09).

### Gaps
- I found no vendor-independent, published false-positive rate or recall for frontier LLMs reviewing trading backtests or quant model evidence specifically. The nearest evidence is from scientific papers (SPOT, PAT), code review and financial statements.
- No sourced estimate exists for P, the extra error-catch rate of a human expert over a cross-vendor AI panel. The break-even capital above is illustrative.
- No current API prices were fetched. The cost of an AI review pass is assumed to be small, roughly dollars to tens of dollars per pass, but that is unverified.

## Question 1: What do SR 11-7 / OCC 2011-12, the OCC Comptroller's Handbook (2021) and PRA SS1/23 require for effective challenge, and what have regulators said (2023-2026) about AI tools in validation or review?

### Takeaway
- **Current state (as of 2026-10-15):** SR 11-7, OCC 2011-12 and the Comptroller's Handbook "Model Risk Management" booklet were all rescinded on 2026-04-17. They were replaced by the interagency SR 26-2 / OCC Bulletin 2026-13.
- **How effective challenge changed:**
  - SR 11-7 framed it as "incentives, competence and influence". SR 26-2 keeps it as "expertise, sufficient independence to permit objectivity, and organizational standing and influence to effect change".
  - The new guidance is non-binding and de-emphasises organisational independence of validation.
  - It explicitly leaves generative and agentic AI out of scope.
- **PRA SS1/23 (in force since 2024-05-17)** is now the more demanding text on independence:
  - validators have no part in development and no stake in approval;
  - separate reporting lines and separate incentives;
  - enough standing and access to the board;
  - approvers must ensure recommendations are acted on.
- **Regulators on AI tools:** none speaks directly to using an LLM as the validator. FINRA (RN 24-09, 2026 report) and the PRA (FS2/23, 2025 roundtables) say existing duties apply, the AI tool itself needs governance, and human review of AI outputs is expected.

### Cited Findings
**SR 11-7 / OCC 2011-12 (2011; rescinded 2026-04-17)**
- SR 11-7 said validation "involves a degree of independence from model development and use. Generally, validation is done by staff who are not responsible for model development or use and do not have a stake in whether a model is determined to be valid." — [SR 11-7 PDF (rescinded)](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.pdf); [SR 11-7 page](https://www.federalreserve.gov/bankinforeg/srletters/sr1107.htm) (quoted in a search extract)
- Under the 2011 guidance, effective challenge depended on "a combination of incentives, competence, and influence". — [Orrick](https://www.orrick.com/en/Insights/2026/04/Agencies-Overhaul-Model-Risk-Management-Guidance-for-Banks-Heres-What-Changed); [Fed SR 26-2 search extract noting the earlier framing](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm)
- OCC Bulletin 2011-12 is marked "RESCINDED Replaced - See OCC 2026-13". — [OCC rescinded bulletin](https://www.occ.gov/static/rescinded-bulletins/bulletin-2011-12.pdf); [OCC news release NR 2026-29](https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-29.html)

**Revised interagency guidance: SR 26-2 / OCC Bulletin 2026-13 / FDIC (2026-04-17)**
- SR 26-2 supersedes and replaces SR 11-7 and SR 21-8. — [Fed SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm); [Sullivan & Cromwell](https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management)
- Effective challenge is kept as a core principle: critical analysis by objective experts who evaluate model risk and drive appropriate changes. It requires "appropriate expertise, sufficient independence to permit objectivity, and organizational standing and influence to effect change when appropriate". — [Fed SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm); [Orrick](https://www.orrick.com/en/Insights/2026/04/Agencies-Overhaul-Model-Risk-Management-Guidance-for-Banks-Heres-What-Changed)
- Validation independence is played down, in one firm's words: the guidance relies on "the rigor and effectiveness of the review" rather than on organisational structure. — [Orrick](https://www.orrick.com/en/Insights/2026/04/Agencies-Overhaul-Model-Risk-Management-Guidance-for-Banks-Heres-What-Changed). Another firm describes the independence discussion more mildly, as "streamlined". — [Sullivan & Cromwell](https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management). The two firms frame the same change differently.
- The guidance "does not set forth enforceable standards or prescriptive requirements". It is most relevant to banks with over $30 billion in total assets; smaller banks with significant model risk may also find it relevant. — [Fed SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm); [Sullivan & Cromwell](https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management)
- The guidance sets no required validation cadence, and its model definition is narrowed to a complex quantitative method, system or approach. — [Orrick](https://www.orrick.com/en/Insights/2026/04/Agencies-Overhaul-Model-Risk-Management-Guidance-for-Banks-Heres-What-Changed) (search extract; the cadence point is single-source)
- Generative AI and agentic AI "are not within the scope of this guidance". A bank's risk management and governance practices "should guide the determination of appropriate governance and controls for any tools, processes, or systems not covered". The agencies plan a request for information on model risk management, including AI, generative AI and agentic AI. — [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html); [Fed SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm); [Orrick](https://www.orrick.com/en/Insights/2026/04/Agencies-Overhaul-Model-Risk-Management-Guidance-for-Banks-Heres-What-Changed)
- No evidence was found that the planned RFI had been issued (as of the searches). — [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html) (single-source; absence of evidence)

**OCC Comptroller's Handbook "Model Risk Management" (2021; rescinded 2026-04-17)**
- OCC Bulletin 2026-13 rescinds the Handbook booklet, along with OCC 2011-12, OCC 1997-24 and OCC 2021-19 (the BSA/AML model risk statement). — [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html); [OCC NR 2026-29](https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-29.html); [RiskTemplate](https://risktemplate.com/blog/2026-05-02-occ-fed-fdic-revised-model-risk-management-guidance-2026/)
- A 2021 commentary on the booklet said it assigned model risk responsibilities person-to-model ("man-to-man marking ... not 'zone defence'"). It also said every important assumption of a high-risk model needs a record of effective challenge. — [CRISIL 2021](https://www.crisil.com/content/crisilcom/en/home/our-analysis/crisil-blogs/2021/08/comptrollers-handbook-on-model-risk-management-model-inventory-gets-a-fillip.html) (single-source, secondary; now historical)

**PRA SS1/23 (published 2023-05-17; effective 2024-05-17)**
- Published 17 May 2023, effective 17 May 2024, as part of PS6/23. — [Bank of England SS1/23 page](https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss); [Deloitte copy of SS1/23](https://www2.deloitte.com/content/dam/Deloitte/se/Documents/risk/ss123.pdf). One vendor site gave 17 May 2023 as the effective date; the PRA page contradicts it. — [VerifyWise](https://verifywise.ai/solutions/ss1-23)
- Scope at launch: banks with internal-model approval for regulatory capital. — [Deloitte copy of SS1/23](https://www2.deloitte.com/content/dam/Deloitte/se/Documents/risk/ss123.pdf); [Bank of England SS1/23 page](https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss)
- Principle 4: "Firms should have a validation process that provides ongoing, independent, and effective challenge to model development and use." — [SS1/23 PDF](https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2023/ss123.pdf); [Presencis summary](https://presencis.com/regulations/pra-ss1/article-P4/)
- "Validators should therefore not be part of any model development activities, nor have a stake in whether or not a model is approved." Impartiality can be secured by "separate reporting lines and separate incentive structures from the model developers". — [SS1/23 PDF](https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2023/ss123.pdf) (search extract; consistent with the [Presencis summary](https://presencis.com/regulations/pra-ss1/article-P4/))
- The validation function "should have sufficient organisational standing to provide effective challenge and have appropriate access to the board and/or board committees". The individual or body that approves a model "should ensure that validation recommendations for remediation or [redevelopment]" are acted on. — [SS1/23 PDF](https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2023/ss123.pdf); [CP6/22 appendices (predecessor wording on stature and authority)](https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/consultation-paper/2022/june/model-risk-management-principle-for-banks.pdf)
- A 2026 PRA document restates Principle 4 as "Banks undertake appropriate model validation and independent review activities...". The search extract did not show whether it changes the substance or applies only to a subset of banks. — [PRA 2026 supervisory statement appendix](https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2026/liaf0126app4.pdf) (single-source; status unclear)

**Regulators on AI tools (2023-2026)**
- FINRA Regulatory Notice 24-09 (27 June 2024):
  - Creates no new requirements; FINRA's rules are "technology neutral".
  - If generative AI is part of a supervisory system, the firm's policies should address technology governance, "including model risk management, data privacy and integrity, reliability and accuracy of the AI model".
  - Duties apply whether the AI tool is in-house or from a third party.

  Sources: [FINRA RN 24-09 PDF](https://finra.org/sites/default/files/2024-06/regulatory-notice-24-09.pdf); [Debevoise](https://www.debevoise.com/insights/publications/2024/07/finra-issues-brief-reminder-on-managing-generative); [Mayer Brown](https://mayerbrown.com/-/media/files/perspectives-events/publications/2024/07/legal-update-finra-publishes-regulatory-notice.pdf); [Stradley Ronon](https://www.stradley.com/publications/with-great-power-comes-great-responsibility-finra-underscores-regulatory-implications-of-using-ai)
- FINRA 2026 Annual Regulatory Oversight Report (9 December 2025):
  - A standalone generative AI section, and the first discussion of AI agents.
  - Agent risks include autonomy (acting without human validation) and scope or authority creep.
  - Suggested practices include checking outputs with human-in-the-loop review and logging prompts and outputs.

  Sources: [Debevoise](https://www.debevoise.com/insights/publications/2025/12/finras-2026-regulatory-oversight-report-continued); [Mayer Brown](https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2025/12/finra-2026-regulatory-oversight-report.pdf%3Frev=-1)
- One commentary says reviewers of AI output need "sufficient expertise to evaluate AI outputs critically". — [Saifr](https://saifr.ai/blog/building-a-genai-governance-framework-takeaways-from-finras-2026-oversight-report) (single-source, vendor commentary; possibly paraphrase, not FINRA's words)
- PRA FS2/23 (October 2023): respondents considered the CP6/22 principles (later SS1/23) sufficient to cover AI model risk, with areas to strengthen or clarify. — [Bank of England FS2/23](https://www.bankofengland.co.uk/prudential-regulation/publication/2023/october/artificial-intelligence-and-machine-learning) (single-source)
- The PRA held CRO roundtables on 20 and 22 October 2025 with 21 firms on AI/ML adoption under SS1/23, and published the slides on 24 November 2025. — [Bank of England](https://www.bankofengland.co.uk/prudential-regulation/publication/2025/november/pra-holds-model-risk-management-roundtable-on-ai); [CMS](https://cms.law/en/gbr/regulatory-news/pra-model-risk-management-ai-and-ml-roundtable-meetings)
- Third-party commentary says the PRA found core SS1/23 expectations "not consistently applied" for AI, with robust validation among the gaps. — [Jaywing](https://risk.jaywing.com/news-views/the-pra-s-ai-roundtable-a-governance-reality-check-for-uk-banks/) (single-source, not PRA wording)
- The Fed Vice Chair for Supervision (Bowman) gave a speech on AI in the financial system on 2026-05-01. — [Federal Reserve](https://www.federalreserve.gov/newsevents/speech/bowman20260501a.htm) (content not reviewed; listed in search results only)

### Inferences
- **The goal's citation needs updating.** The goal cites "SR 11-7" (GOAL.md line 398 and the "effective challenge" requirement). As of 2026-10-15 that text is rescinded. The goal should cite SR 26-2 / OCC 2026-13 for the current definition, PRA SS1/23 Principle 4 for the stricter independence model, and SR 11-7 only as the historical source of "incentives, competence, influence".
- **None of these texts binds a one-owner, non-regulated system.** They are benchmarks. SR 26-2 is non-binding even for banks, and aimed at banks over $30 billion.
- **SR 26-2's exclusion of generative and agentic AI cuts two ways:** (a) no US banking guidance forbids using an LLM as the challenger; (b) no guidance endorses it either. The AI reviewer is itself an unvalidated tool, and the agencies tell banks to apply general governance to it. FINRA's expectations point the same way: model risk management, reliability and accuracy of the AI tool, and human-in-the-loop checks on its outputs.
- **SS1/23's independence elements, translated for one owner:** no stake in approval, separate incentives, standing, recommendations acted on. In practice: a reviewer paid a fixed fee whatever the verdict (or an AI with no stake); a written duty to act on findings; and blocking findings the approver (the owner) cannot simply waive.

### Gaps
- Primary texts could not be opened (network policy). Not confirmed: SR 11-7's own sentences on "explicit authority to challenge", on validation by third parties, and that validation work by developers "be subject to critical review by an independent party" (I recall these, but they were not verified this session).
- I found no statement from the Fed, OCC, SEC, FINRA, PRA or another regulator on using LLMs or AI tools to perform model validation or effective challenge.
- SEC (2023-2026) was not covered: the search budget ran out before checking the status of the SEC's 2023 predictive-data-analytics proposal, which I believe was withdrawn in 2025 (unverified), and the 2026 exam priorities on AI.
- Not reviewed: the content of the Bowman speech (2026-05-01) and the PRA roundtable slides on validation.
- Unclear: what the 2026 PRA document restating Principle 4 changes.

## Question 2: How reliable are LLM reviewers? (LLM-as-a-judge biases, sycophancy, peer-review feedback, error detection in code, statistics and financial documents, agreement with experts, false positives)

### Takeaway
- **Where LLMs do well:** as general reviewers they reach about human-level agreement or overlap. Zheng et al. measured over 80% agreement with humans, the same as human-human agreement. Liang et al. found overlap with human reviewers comparable to that between two humans. Participants often find LLM reviews useful (ICLR 2025 randomised trial; AAAI-26 pilot).
- **Where they fall short:** finding real, subtle errors. SPOT measured about 21% recall and 6% precision on errors that led to errata or retraction. Newer tools score higher on narrower, more leniently graded subsets.
- **Known biases:** position, verbosity, self-preference, similarity to the judge, sycophancy, and anchoring on what the author discloses.
- **Manipulation:** text placed in the evidence (prompt injection) can steer them.
- **Code review:** LLMs find more bugs than paid contractors but invent some. Human+AI teams keep the recall and cut the false findings.

### Cited Findings
**LLM-as-a-judge reliability and biases**
- Zheng et al. (2023): GPT-4 as judge matched human preferences at over 80% agreement, "the same level of human-human agreement" (3K expert votes, 3K crowd votes). — [arXiv 2306.05685 v4](https://arxiv.org/html/2306.05685v4); [Hugging Face papers](https://huggingface.co/papers/2306.05685). One secondary reading says tied human votes count as half-agreement. — [scrapbox notes](https://scrapbox.io/nikkie-memos/Judging_LLM-as-a-Judge_with_MT-Bench_and_Chatbot_Arena) (single-source; unverified)
- The same paper names position bias, verbosity bias, self-enhancement bias and limited reasoning ability as judge weaknesses, and proposes mitigations for some of them. — [arXiv 2306.05685](https://arxiv.org/abs/2306.05685v1); [Papers with Code mirror](https://papers.pytorch.kr/papers/2306.05685)
- Panickssery, Bowman & Feng (NeurIPS 2024):
  - GPT-4 and Llama 2 can tell their own text from other models' and humans' text with non-trivial accuracy.
  - Self-recognition correlates linearly with self-preference across fine-tuning experiments.
  - The causal link holds up against simple confounders.

  Sources: [NeurIPS 2024](https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html); [arXiv 2404.13076](https://arxiv.org/abs/2404.13076v1)
- Ye et al., "Justice or Prejudice?" (ICLR 2025): the CALM framework tests 12 biases in LLM judges, including bandwagon bias. The search extracts did not confirm the full list or the per-bias figures. "Significant biases persist in certain specific tasks" even for advanced models. — [arXiv 2410.02736](https://arxiv.org/pdf/2410.02736); [ICLR 2025 proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/fdca08d371e4b6c031397909e20043bd-Abstract-Conference.html)
- Sharma et al. (Anthropic; arXiv October 2023; ICLR 2024):
  - Five AI assistants consistently showed sycophancy across four free-form tasks.
  - Responses that match the user's views are more likely to be preferred in human preference data.
  - Humans and preference models prefer convincingly written sycophantic answers over correct ones "a non-negligible fraction of the time".

  Sources: [arXiv 2310.13548](https://arxiv.org/abs/2310.13548v1); [ICLR 2024 proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/0105f7972202c1d4fb817da9f21a9663-Abstract-Conference.html); [Anthropic](https://www.anthropic.com/news/towards-understanding-sycophancy-in-language-models)

**LLM feedback on scientific papers; agreement with expert reviewers**
- Liang et al., NEJM AI (17 July 2024):
  - GPT-4's comments overlapped with individual human reviewers' comments at 30.85% (Nature journals) and 39.23% (ICLR).
  - Human-human overlap was 28.58% and 35.25%.
  - In a user study, 57.4% found the feedback helpful or very helpful, and 82.4% found it more beneficial than feedback from at least some human reviewers.
  - The authors say human expert review should remain the foundation.

  Sources: [arXiv 2310.01783](https://arxiv.org/pdf/2310.01783); [NSF PAR record](https://par.nsf.gov/biblio/10617069). A secondary summary reports different survey figures (50.3% helpful, 20.1% as helpful as humans), which contradicts the abstract. — [2 Minute Medicine](https://www.2minutemedicine.com/large-language-models-show-potential-to-provide-feedback-on-research-papers-on-a-large-scale/)
- ICLR 2025 randomised study (arXiv 2504.09737):
  - 22,467 reviews were randomly assigned to get AI feedback on the draft review; 22,364 were controls.
  - Feedback was sent only if it passed LLM-based reliability tests.
  - 26.6% of reviewers who got feedback updated their reviews, taking up 12,222 suggestions.
  - Updated reviews were about 80 words longer and, by blinded assessment, more informative.

  Sources: [arXiv 2504.09737](https://arxiv.org/abs/2504.09737v1); [ICLR blog](https://blog.iclr.cc/2025/04/15/leveraging-llm-feedback-to-enhance-review-quality/)
- AAAI-26 AI review pilot (arXiv 2604.13940, April 2026):
  - AI reviews for all 22,977 full-review papers in under a day; labelled as AI; no scores or accept/reject recommendation.
  - Participants preferred them on technical accuracy and research suggestions.
  - Weaknesses: errors reading equations and tables, trouble ranking which issues matter, too long.

  Sources: [arXiv 2604.13940](https://arxiv.org/pdf/2604.13940); [Crypto Briefing](https://cryptobriefing.com/first-double-blind-ai-evaluations-piloted/); [AAAI announcement](https://aaai.org/aaai-launches-ai-powered-peer-review-assessment-system/)
- The AI Scientist's automated reviewer:
  - 2024 preprint, on 500 ICLR 2022 papers: GPT-4o reached 0.61 balanced accuracy on accept/reject, against 0.66 for humans (the NeurIPS 2021 consistency experiment). — [arXiv 2408.06292](https://arxiv.org/pdf/2408.06292)
  - Nature version (2026), as reported by press: 69% balanced accuracy for papers published before the model's knowledge cutoff. — [AI Weekly](https://aiweekly.co/alerts/sakana-ai-16335); [Warp News](https://www.warpnews.org/artificial-intelligence/ai-scientist-produces-increasingly-better-papers-and-an-ai-system-can-review-them-as-well-as-humans/) (Nature figures secondary only)

**Finding real errors (recall and false positives)**
- SPOT (May 2025):
  - 83 published papers with 91 errors significant enough for errata or retraction.
  - The best model (o3) reached at most about 21.1% recall and 6.1% precision; the others were near zero.
  - Models rarely found the same errors again across 8 runs, and confidence estimates were uniformly low.
  - Strong models made "student-level misconceptions".

  Sources: [arXiv 2505.11855](https://arxiv.org/abs/2505.11855v1); [EleutherAI](https://www.eleuther.ai/papers-blog/when-ai-co-scientists-fail-spot-a-benchmark-for-automated-verification-of-scientific-research); [Hugging Face](https://huggingface.co/papers/2505.11855)
- Google's Paper Assistant Tool (arXiv 2606.28277, June 2026), on a subset of SPOT (26 papers, 29 math/CS proof errors):
  - Gemini 3.1 Pro zero-shot found 55.2% of errors; PAT with inference scaling found 89.7%.
  - The authors note their grader is more lenient, so the numbers are not comparable to SPOT.

  Source: [arXiv 2606.28277](https://arxiv.org/pdf/2606.28277) (single-source)
- CriticGPT (OpenAI, June 2024):
  - Model critiques were preferred over human critiques 63% of the time on code with naturally occurring LLM errors.
  - Models caught more inserted bugs than human contractors paid for code review.
  - Critics hallucinate bugs. Human+critic teams catch similar numbers of bugs to the critic alone while hallucinating less.

  Sources: [arXiv 2407.00215](https://arxiv.org/html/2407.00215v1); [SiliconANGLE](https://siliconangle.com/2024/06/27/openais-criticgpt-uses-generative-ai-spot-errors-generative-ais-outputs/)
- Industrial code review:
  - Beko, Qodo PR-Agent across 10 projects: developers acted on 73.8% of AI comments, but pull requests took longer to close, and surveys flagged faulty suggestions. — [Bilkent repository](https://repository.bilkent.edu.tr/items/8e7ac28e-5120-4c6e-84e3-e7d288c336f0) (single-source)
  - WirelessCar field study (ESEM 2025): concerns about false positives and missing context. — [Chalmers](https://research.chalmers.se/en/publication/551186) (single-source)
- Tencent (ICSE 2026 SEIP): of 433 static-analysis alarms, 328 were false positives. LLM + static-analysis hybrids removed 94-98% of false positives with high recall. — [arXiv 2601.18844](https://arxiv.org/abs/2601.18844v1); [ICSE 2026 listing](https://conf.researchr.org/details/icse-2026/icse-2026-software-engineering-in-practice/72/Reducing-False-Positives-in-Static-Bug-Detection-with-LLMs-An-Empirical-Study-in-Ind)
- A July 2026 blog argues there is no public, vendor-independent measurement of the precision or false-positive rate of a general-purpose AI code reviewer in production. — [youngju.dev](https://www.youngju.dev/blog/2026-07-17-ai-code-review-measured-evidence.en) (single-source opinion)
- Financial statements (June 2025):
  - Top LLMs identify financial-statement errors when given the transaction history, and rarely flag correct statements as wrong.
  - They are weak at explaining errors and citing standards.

  Source: [arXiv 2506.17282](https://arxiv.org/abs/2506.17282v1) (single-source). Related benchmarks: [FinVerBench, arXiv 2605.29586](https://arxiv.org/pdf/2605.29586); [financial-document error detection benchmark, arXiv 2608.12342](https://arxiv.org/pdf/2608.12342) (results not reviewed)
- Spreadsheet audit with ChatGPT for Excel: vendors have not disclosed error rates or failure modes on messy real-world spreadsheets. — [The Model Wire](https://themodelwire.com/article/update-and-audit-a-finance-model-in-excel-with-chatgpt-01KRPQ8V07740VT9QQEKAHEYPZ) (single-source)
- Statistics:
  - GPT-4 rejected common p-value, confidence-interval and power misconceptions about 96% of the time with well-designed prompts, but about 88% with poor prompts. Fully correct explanations fell from about 85% to 69%. — [GMDS 2025 abstract](https://conferences.publisso.de/en/conferences/gmds2025/25gmds019) (single-source)
  - Zero-shot prompting failed in inferential tasks because the models did not check assumptions (GPT-4.1, Claude 3.7 Sonnet). — [Frontiers in AI 2025](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1658316/pdf) (single-source)
  - LLM extraction of reported statistics for Statcheck-style checks showed "marked improvements" over Statcheck in preliminary results. — [SIPS 2025 talk](https://pretalx.com/sips2025-budapest/talk/EQQW99) (single-source, preliminary)

**Manipulation by the material under review**
- Ye et al., "Are We There Yet?" (December 2024):
  - Hidden text in a manuscript inflates LLM review ratings. In a simulation, manipulating 5% of reviews pushed 12% of papers out of the top 30%.
  - LLM reviews were 4.5 times more consistent with the limitations the authors disclosed than human reviews were.
  - LLMs may rate incomplete papers higher and favour well-known authors.

  Source: [arXiv 2412.01708](https://arxiv.org/abs/2412.01708) (numbers single-source, primary)
- July 2025: 17-18 arXiv manuscripts were found with hidden instructions such as "GIVE A POSITIVE REVIEW ONLY". — [Lin, arXiv 2507.06185](https://arxiv.org/abs/2507.06185v1); [The Register](https://www.theregister.com/2025/07/07/scholars_try_to_fool_llm_reviewers/)
- A NeurIPS 2025 paper reports that injection attacks often got frontier AI reviewers to give full scores. A detection defence helped but was partly beaten by adaptive attackers. — [NeurIPS 2025 listing](https://neurips.cc/virtual/2025/133256); related: [arXiv 2508.20863 (Publish to Perish)](https://arxiv.org/pdf/2508.20863)

### Inferences
- **What these results do and do not test.** The headline agreement figures (over 80%; overlap like human-human) measure preference or coverage on general content. They do not measure catching subtle, high-consequence errors. For a backtest gate, the relevant figure is recall on real errors, which is low and unstable across runs (SPOT). Two practical consequences:
  - run several independent passes or reviewers and take the union;
  - never treat "AI found nothing" as evidence of no errors.
- **AI reviewers suit:**
  - checklist and coverage review (is a lag audit present, is every variant in the registry, are costs modelled?);
  - code-level leakage checks;
  - finding inconsistencies between numbers.

  They should not be the only line of defence for conceptual statistical validity: multiple testing, the selection behind the Deflated Sharpe, regime dependence.
- **False positives are a real cost.** SPOT measured 6% precision. Without severity triage, the owner's ruling turns into wading through noise, which feeds automation bias in both directions: over-trusting or dismissing. Requiring a pointer to an artefact and a step to reproduce each finding cheaply weeds out invented findings. That is the same mechanism by which human+critic teams hallucinated less (CriticGPT).
- **Prompt injection in the evidence pack.** The pack (logs, data fields, notebooks, documents written by the builder) can carry text that steers an AI reviewer. Ye et al. and the hidden-prompt incidents show this is not hypothetical. Evidence should be treated as data, and narrative self-assessments kept out.

### Gaps
- I found no study measuring LLM recall or precision on errors in trading backtests specifically (look-ahead, survivorship, data snooping) or on spreadsheet-based financial models with seeded errors.
- The exact Nature 2026 figures for the AI Scientist reviewer, and the per-model numbers from CALM, were not confirmed in primary text.
- No data was found on how much the newest frontier models (2026) improve recall on SPOT-like real-error benchmarks beyond the PAT subset result.

## Question 3: Does diversity help? (Different vendor or family, several reviewers, red-team prompting, blinding)

### Takeaway
- **Different vendor:** yes, partly. Self-preference, similarity bias and error correlation are all strongest within a family or developer. Panels of judges from disjoint families reduce intra-model bias at lower cost. But error correlation rises with capability even across vendors, so diversity reduces common-mode error without removing it.
- **Several reviewers working alone, findings pooled:** supported (PoLL).
- **Multi-agent debate:** not reliably better than simple ensembling.
- **Blinding:** giving the reviewer only the evidence, without the builder's narrative or self-assessment, is supported by the sycophancy and limitations-anchoring evidence. It should not hide the design documents the reviewer needs to judge conceptual soundness.

### Cited Findings
- PoLL (Verga et al., Cohere, April 2024): across three judge settings and six datasets, a panel of smaller models from disjoint families beat a single large judge (GPT-4). It showed less intra-model bias and cost over seven times less. — [arXiv 2404.18796](https://arxiv.org/html/2404.18796v2); [Cohere](https://cohere.com/research/papers/replacing-judges-with-juries-evaluating-llm-generations-with-a-panel-of-diverse-models-2024-04-29)
- Correlated errors (Kim et al., ICML 2025):
  - About 60% agreement on questions both models got wrong (one leaderboard).
  - Shared architecture and shared developer raise correlation.
  - More accurate models are more correlated even across architectures and providers.
  - The authors flag consequences for LLM-as-judge.

  Sources: [ICML 2025](https://proceedings.mlr.press/v267/kim25e.html); [arXiv 2506.07962](https://arxiv.org/abs/2506.07962v1)
- Goel et al. (ICML 2025): CAPA, a similarity metric based on overlapping mistakes. LLM judges favour models similar to themselves. Errors are becoming more correlated as capabilities grow. The authors call for "reporting and correction for model similarity" in AI oversight. — [ICML 2025](https://proceedings.mlr.press/v267/goel25b.html); [arXiv 2502.04313](https://arxiv.org/html/2502.04313v2)
- Self-preference driven by self-recognition (Panickssery et al.) applies when the reviewer shares the builder's model or family. — [NeurIPS 2024](https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html); [arXiv 2404.13076](https://arxiv.org/abs/2404.13076v1)
- Debate:
  - Multi-agent debate "do[es] not reliably outperform" self-consistency or ensembling, and is sensitive to hyperparameters (Smit et al., ICML 2024). — [PMLR](https://proceedings.mlr.press/v235/smit24a.html)
  - A 2025 follow-up, across nine benchmarks and four models, found debate failed to reliably beat chain-of-thought or self-consistency even with more compute. — [arXiv 2502.08788](https://arxiv.org/html/2502.08788v2)
- Repeated runs of the same model rarely rediscover the same errors. So variation between runs is large, and repeated or independent runs add coverage. — [arXiv 2505.11855 (SPOT)](https://arxiv.org/abs/2505.11855v1); [EleutherAI](https://www.eleuther.ai/papers-blog/when-ai-co-scientists-fail-spot-a-benchmark-for-automated-verification-of-scientific-research)
- Why blind: sycophancy towards the user's views ([arXiv 2310.13548](https://arxiv.org/abs/2310.13548v1); [ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/0105f7972202c1d4fb817da9f21a9663-Abstract-Conference.html)). LLM reviews anchor on the author's disclosed limitations, 4.5 times more than human reviews ([arXiv 2412.01708](https://arxiv.org/abs/2412.01708), single-source). Hidden-instruction attacks ([arXiv 2507.06185](https://arxiv.org/abs/2507.06185v1); [The Register](https://www.theregister.com/2025/07/07/scholars_try_to_fool_llm_reviewers/)).
- Red-team or adversarial setup in practice: OpenAI trained CriticGPT specifically to find inserted bugs, which beat general review by paid contractors on that task. — [arXiv 2407.00215](https://arxiv.org/html/2407.00215v1); [SiliconANGLE](https://siliconangle.com/2024/06/27/openais-criticgpt-uses-generative-ai-spot-errors-generative-ais-outputs/)

### Inferences
- **The current default does not protect against self-preference or similarity bias.** "A separate instance that sees only the evidence" counters anchoring on the builder's reasoning, but not self-preference, similarity bias or correlated errors when the instance is the same model or family as the builder. The single biggest cheap improvement is at least one reviewer from a different vendor, preferably two (for a Claude builder: a GPT-family and a Gemini-family model). The Fable ban rules out one Anthropic family only; other non-Fable Anthropic models are allowed but count as same-vendor.
- **Combine reviewers by union, not majority vote.** For error-finding the goal is recall, and the evidence says errors are found inconsistently. Majority voting suits scoring and preference tasks (PoLL), not finding issues. Have the panel rank severity, and have the owner's triage remove duplicates.
- **Prompt for specific failure modes rather than "review this":**
  - look-ahead or lag;
  - survivorship;
  - leakage between training and test;
  - unregistered variants and the selection behind the Deflated Sharpe;
  - transaction costs and capacity;
  - regime concentration;
  - the reproducibility of each headline number.

  This is an inference from the CriticGPT setup and the CALM bias results; I found no direct trial of checklist versus open prompts for financial model review.
- **What blinding should hide:** the builder's conversation history, its reasoning, its self-assessment of results, and any persuasive summary.
- **What blinding should not hide:** pre-registered hypotheses and criteria, design documents, code, raw data lineage, and the full variant registry. Judging conceptual soundness needs the design rationale. An evidence pack the builder curated may also hide what was left out, so the reviewer must get the complete registry and logs, not a selection.
- **Diversity has limits.** Kim et al. and Goel et al. show frontier models' mistakes are converging. A human expert's error profile is likely to differ more from any LLM panel's than LLM panels differ from each other (inference, not measured). That supports adding a human where the stakes are highest.

### Gaps
- I found no controlled study of cross-vendor LLM panels on error-finding (as opposed to preference scoring), nor one measuring how much recall a second vendor adds.
- I found no study comparing reviewers blinded to the author's narrative with unblinded ones, for LLM review of technical evidence. The limitations-anchoring result is the nearest.

## Question 4: What human review options exist for a one-person owner, what do they cost, and what do small quant funds and prop shops do before allocating capital?

### Takeaway
- **Options:** an independent freelance quant or statistician on a fixed-scope engagement (realistic for one owner); a model-validation firm (built and priced for banks, tens of thousands of dollars and up); an academic reviewer (no rate data found).
- **Cost evidence is thin and mostly from vendors:**
  - senior quant or finance consulting appears to run about $150-$300+ an hour (marketplace data);
  - bank framework validations typically cost $75k or more;
  - AML-model validation quotes ran $6k-$90k (anecdotal, 2020).
- **What quant firms do:** an investment committee assesses hypothesis, rationale and results; separate teams review code and testing; a log records the path from hypothesis to implementation (Man AHL). Practitioners incubate, then trade small and scale up.

### Cited Findings
- Freelance financial analysts: $35/hr (junior) to $300/hr (top tier); experienced average about $90-$150/hr (2026 guide). — [goLance](https://golance.com/hiring/best-freelance-financial-analysts-hourly-rate) (vendor marketplace)
- US data scientists specialising in regulated finance or pharma work: $285-$500/hr. — [SecondTalent](https://www.secondtalent.com/resources/freelance-data-scientist-hourly-rate-us/) (vendor)
- A quantitative-finance expert contract for AI model evaluation work pays $150/hr. — [startup.jobs listing](https://startup.jobs/quant-finance-expert-spain-anyone-ai-8333392) (single listing)
- These three are marketplace or vendor sources with a commercial interest, not independent benchmarks. They agree only loosely: about $150-$300+/hr for senior quant-finance work.
- RMA Model Validation Consortium (2021): banks typically pay $75,000 or more to fully validate frameworks such as BSA/AML and CECL. — [RMA](https://www.rmahq.org/blogs/2021/cost-is-the-biggest-challenge-to-validate-vendor-models?gmssopc=1); [ProSight republication](https://www.prosightfa.org/insights/cost-is-the-biggest-challenge-to-validate-vendor-models/) (likely the same article, so effectively single-source)
- RMA 2022 study of 62 banks: the top challenges to expanding validation were talent (72%) and cost (63%); more than 70% validate models every one to two years. — [RMA press release](https://www.rmahq.org/press-releases/2022/financial-institutions-face-risk-with-models-new-rma-study-finds/) (single-source)
- Independent validation of an AML system (2020 forum): one quote of about $6,000, and vendor quotes of $15k-$90k. Commenters warned that some vendors only do "data mapping" while calling it validation. — [BankersOnline forum](https://bankersonline.com/forum/ubbthreads.php/topics/2232676/model-validation-fcrm) (anecdotal, single-source)
- Outsourcing validation is often driven by limited bandwidth at smaller banks. Low-quality external validation may have to be redone by another validator. — [RiskSpan](https://riskspan.com/internal-external-model-validation/) (single-source, vendor)
- Man AHL:
  - AI-derived signals go through two validation tracks. The Investment Committee assesses hypothesis, economic rationale and research results with the same framework used for human-built signals. Technology teams do code reviews, unit, integration and scenario tests, and assess implementation risk.
  - A logging system records the full path from hypothesis to implementation.

  Source: [Man Group, "What AI can do for alpha"](https://www.man.com/insights/what-ai-can-do-for-alpha) (single-source, primary). Man AHL describes an independent risk team. — [Man AHL](https://www.man.com/ahl)
- At allocators, a risk manager prepares risk opinions on new hedge-fund proposals for the investment committee. — [CFA Institute job listing](https://careers.cfainstitute.org/job/9116346/senior-risk-manager-hedge-funds/) (one firm's practice)
- AIMA/Marex survey (published 30 June 2026): allocators put significant emphasis on operational robustness. Operational due diligence and concerns about "strategy discipline" remain key barriers to investment. — [AIMA press release](https://www.aima.org/article/press-release-emerging-managers-secure-earlier-investor-backing-by-raising-their-institutional-game.html) (single-source)
- Practitioner sequence:
  - check against the backtest, then trade live at small size and scale up slowly to capacity. — [Wilmott forum](https://forum.wilmott.com/viewtopic.php?p=858922) (informal)
  - Paper trading confirms the plumbing, but a few months usually cannot separate a modest edge from luck, and paper fills are optimistic. — [LuxAlgo](https://www.luxalgo.com/library/concept/forward-paper-trading-confirmation/) (vendor education)

### Inferences
- **The realistic human option for one owner:** a single independent quant or statistician on a fixed-fee, fixed-scope review of the G1 evidence (and of the G3 package) with a written report. Roughly 10-40 hours at about $150-$300/hr gives about $1.5k-$12k a review. This is an inference from weak rate data; real quotes are needed.
- **What the engagement letter should say** (mirrors SS1/23's no-stake and separate-incentive elements):
  - the fee does not depend on the verdict;
  - the reviewer has no financial interest in the strategy;
  - the scope covers statistical validity (multiple testing, Deflated Sharpe inputs, out-of-sample design, lag audit) and a reproduction of headline numbers.
- **Bank model-validation firms** are priced and scoped for regulatory validations ($75k+ framework validations). They are unlikely to be worth it for a one-owner account unless the capital at risk is large.
- **Academic reviewers:** an option (for example a finance or statistics academic doing paid consulting), but I found no rate data. The usual academic referee does not do code-level checks.
- **"Allocate small, then scale"** is the practitioner's substitute for the expensive certainty of a human review. It fits the goal's G3 if the first real-money stage is small and has hard loss limits. The human review can then be timed before scaling rather than before the first dollar (see the threshold rule in section 0).

### Gaps
- I found no authoritative or independent survey of fees for independent quant-strategy reviews or for academic consulting on backtest validation.
- I found no documented, citable governance practice of small prop shops for approving strategies (risk-manager sign-off, allocation tiers). Sources were job listings and forums.
- [Risk.net "Outsourced model validation: is it viable?"](https://www.risk.net/risk-management/7253836/outsourced-model-validation-is-it-viable) was not read (paywall or network policy).

## Question 5: Failure modes to guard against, and controls that address them

### Takeaway
The main failure modes are:
- the reviewer anchored by the builder's narrative (sycophancy, limitations anchoring, injection);
- same-family correlated errors and self-preference;
- reviewer fatigue and false-positive overload, for human reviewers and for the owner triaging AI findings;
- automation bias in the person ruling;
- findings overruled or "approved with conditions" that are never carried out (London Whale).

The controls with evidence or regulatory backing are:
- criteria fixed in advance;
- reviewers from different vendors, blind, working alone, findings pooled;
- each finding must carry an artefact and a step to reproduce it;
- a written disposition for every finding, with closure checked;
- a blocking class the owner cannot waive alone;
- logs and "canary" (seeded-error) tests of the reviewers.

### Cited Findings
- **Anchoring and narrative.** Sycophancy is broad across assistants ([arXiv 2310.13548](https://arxiv.org/abs/2310.13548v1); [Anthropic](https://www.anthropic.com/news/towards-understanding-sycophancy-in-language-models)). LLM reviews follow the author's disclosed limitations 4.5 times more than humans ([arXiv 2412.01708](https://arxiv.org/abs/2412.01708), single-source). Hidden instructions inflate scores ([arXiv 2507.06185](https://arxiv.org/abs/2507.06185v1); [The Register](https://www.theregister.com/2025/07/07/scholars_try_to_fool_llm_reviewers/); [NeurIPS 2025](https://neurips.cc/virtual/2025/133256)).
- **Same-family mistakes.** See [Kim et al. (ICML 2025)](https://proceedings.mlr.press/v267/kim25e.html), [Goel et al. (ICML 2025)](https://proceedings.mlr.press/v267/goel25b.html) and [Panickssery et al. (NeurIPS 2024)](https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html), as in section 3.
- **Human reviewer fatigue.** At Microsoft (1.5 million review comments, five projects), the more files in a change, the lower the proportion of useful review comments. — [Microsoft Research (Bosu, Greiler, Bird, MSR 2015)](https://www.microsoft.com/en-us/research/?p=168510); [RDEL summary](https://rdel.substack.com/p/rdel-16-what-makes-a-code-review). Later work cites 34.5% of Microsoft review comments as not useful. — [arXiv 2501.06738](https://arxiv.org/pdf/2501.06738) (single-source for the 34.5%)
- **AI-side volume and priority problems.** AAAI-26 AI reviews were longer than readers wanted and struggled to rank which issues matter ([arXiv 2604.13940](https://arxiv.org/pdf/2604.13940); [Crypto Briefing](https://cryptobriefing.com/first-double-blind-ai-evaluations-piloted/)). SPOT precision was 6.1% ([arXiv 2505.11855](https://arxiv.org/abs/2505.11855v1)). An industrial AI code review made pull requests take longer to close ([Bilkent](https://repository.bilkent.edu.tr/items/8e7ac28e-5120-4c6e-84e3-e7d288c336f0), single-source).
- **Automation bias.** It produces omission errors (missing what the automation missed) and commission errors (following wrong recommendations), in the Mosier and Skitka framework. A 2026 systematic review (Romeo & Conti, AI & Society, 35 studies) finds explanations and transparency often fail to reduce automation bias. Designs that prompt active verification by the user work better. — [LongTermWiki summary](https://www.longtermwiki.com/knowledge-base/risks/accident/automation-bias/); [LongTermWiki on the 2025/2026 AI & Society review](https://www.longtermwiki.com/resources/a96cbf6f98644f2f) (secondary; primary not opened). Classic systematic review (Goddard et al.): [PMC3240751](https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751) (listed in results; content not reviewed)
- **Overruled and conditional findings (London Whale, 2012):**
  - The Model Review Group identified the spreadsheet process problem and other flaws but approved the model, with instructions to automate it and fix a significant flaw. After the losses it found the automation never happened, plus more errors.
  - A trader wrote that the team should "keep the pressure on our friends in Model Validation", and the review may have been sped up as a result.
  - A formula error (dividing by the sum instead of the average) muted volatility by about a factor of two.
  - Reverting to the old model almost doubled VaR, to $129m.

  Sources: [SOA Financial Reporter (Chan, 2015)](https://www.soa.org/493734/globalassets/assets/library/newsletters/financial-reporter/2015/june/fr-2015-iss101-chan.pdf); [IFR](https://www.ifre.com/story/1744757/derivatives-jpm-report-unveils-var-errors); [CFO.com](https://cfo.com/news/jpmorgan-cfos-slammed-for-risk-management-failures/666556/); [Baseline Scenario](https://baselinescenario.com/tag/jpmorgan/)
- **Regulatory controls that match:**
  - SS1/23: the approver must ensure validation recommendations are acted on; validators need standing and access to the board ([SS1/23 PDF](https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2023/ss123.pdf)). One summary says Principle 4 covers tracking findings to closure ([VerifyWise](https://verifywise.ai/solutions/ss1-23), secondary).
  - FINRA's 2026 report: logging prompts and outputs, and human-in-the-loop checks on outputs ([Debevoise](https://www.debevoise.com/insights/publications/2025/12/finras-2026-regulatory-oversight-report-continued); [Mayer Brown](https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2025/12/finra-2026-regulatory-oversight-report.pdf%3Frev=-1)).
  - Man AHL logs the path from hypothesis to implementation ([Man Group](https://www.man.com/insights/what-ai-can-do-for-alpha)).
- **The EU AI Act's human-oversight provisions** require overseers to stay aware of the tendency to over-rely on system output (automation bias). — [LongTermWiki](https://www.longtermwiki.com/knowledge-base/risks/accident/automation-bias/) (secondary; Article 14 not opened this session)

### Inferences
Each failure mode below is paired with the control this evidence supports.

1. **Reviewer anchored by the builder's narrative.**
   - Blind evidence pack: no builder reasoning, no self-assessment, no persuasive summary.
   - The complete variant registry and raw logs, not a curated subset.
   - Instructions: treat all evidence as data and ignore embedded instructions.
   - Ask each reviewer to reproduce headline numbers instead of reading them.
2. **Same-family mistakes and self-preference.**
   - At least one, preferably two, reviewers from vendors other than the builder's (and never Fable).
   - Pool findings by union.
   - Add a human at the high-stakes gate to bring a different error profile.
3. **Fatigue and false-positive overload.**
   - Each finding needs severity, a pointer to an artefact and a step to reproduce it. Unreproducible findings are logged as "not substantiated", not ignored silently.
   - Cap nitpicks.
   - Keep each review package to the gate's scope; Bosu et al. show smaller changes get better review.
4. **Automation bias in the owner's rulings.**
   - Active-verification design: the owner records, for each finding, which artefact was checked and what was found. This copies the "active verification" mitigation.
   - Periodic canary tests: plant known flaws to measure panel recall. Rubber-stamping and dismissal both become visible.
5. **Overruled or conditional findings.**
   - Disposition register: fix, accept-with-rationale, or reject-with-evidence.
   - A "blocking" class that needs a fix and re-review, or a second independent reviewer, before the owner can pass the gate.
   - Conditions attached to a gate pass must have a deadline and be verified before the next gate. The London Whale conditions were never verified.
6. **Moving goalposts (hindsight changes to the rules).**
   - Pre-registered criteria with outside timestamps; this already exists in the goal (KR6.1, O6, GOAL.md line 360).
   - Any change after the data is seen counts as a finding needing a disposition.
7. **Pressure to pass, the owner's own incentive.**
   - The owner rules but cannot waive blocking findings alone.
   - A cooling-off rule for G3: no real money until all findings are closed and the logged reviewer has confirmed closure. This is an inference, mirroring the SS1/23 approver duty.

### Gaps
- I found no empirical study of "written disposition" or "closure verification" controls' effectiveness outside the banking guidance itself. The support is regulatory practice and the London Whale counter-example, not trials.
- Not read in primary form: the 2026 automation-bias review and the Goddard et al. review. Effect sizes for active-verification designs are unconfirmed.
- The SEC's Knight Capital order (2013), which the goal already cites (GT-7), was not re-checked this session (search budget ran out).

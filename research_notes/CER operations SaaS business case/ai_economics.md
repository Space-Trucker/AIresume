# AI economics evidence for an AI-native vertical SaaS administering Italian renewable energy communities (CER)

How far each figure was checked (the tags apply throughout):
- **[V]** means I fetched the primary page (anthropic.com) and read the figure there. The text came back through a summarising fetch tool, so the report writer should spot-check any number that carries a headline.
- **[S]** means the figure is attributed to the primary source only in a search-engine summary. I could not fetch the full text because the network egress policy blocked arxiv.org, nber.org, hbs.edu, economics.mit.edu, ec.europa.eu, istat.it, bvp.com, huggingface.co and assets.anthropic.com.
- **[2nd]** means the figure comes from a secondary or aggregator source.

Research date: 28 Sep 2026.

---

## Q1. What do the Anthropic Economic Index reports (Feb 2025 to Jun 2026) show about automation vs augmentation, occupations and tasks, enterprise API use, cost-insensitivity, context bottlenecks, and geography (Italy and EU)?

### Takeaway
Across 2025, Claude usage moved toward delegation. Directive automation on Claude.ai rose from 27% to 39% between Dec 2024 and Aug 2025. Enterprise API traffic is overwhelmingly automation: 77% of business uses in Sep 2025 and 75% in Nov 2025. By late 2025 augmentation had edged back to 52% on Claude.ai. Businesses deploying through the API are not very sensitive to price (elasticity -0.29). Anthropic names curating context and data as the main barrier to complex enterprise deployments. Italy's usage-index value could not be confirmed from a primary source. One secondary source puts it at 1.70.

### Cited Findings

**Initial report (published 10 Feb 2025; about 1M Claude.ai Free/Pro conversations from Dec 2024 to Jan 2025)**
- Augmentation was 57.4% and automation 42.6% of tasks. Within augmentation: task iteration 31.3%, learning 23.3%, validation 2.8%. Within automation: directive 27.8%, feedback loop 14.8%. [V] — [Anthropic, "Introducing the Anthropic Economic Index"](https://www.anthropic.com/news/the-anthropic-economic-index)
- About 36% of occupations used AI for at least 25% of their tasks. About 4% used it for at least 75%. [V] — [Anthropic, Feb 2025](https://www.anthropic.com/news/the-anthropic-economic-index)
- Shares of Claude usage by occupational category:

  | Category | Share |
  |---|---|
  | Computer & Mathematical | 37.2% |
  | Arts/Design/Media | 10.3% |
  | Education & Library | 9.3% |
  | Office & Administrative Support | 7.9% |
  | Life Sciences | 6.4% |
  | Business & Financial Operations | 5.9% |

  [V] — [Anthropic, Feb 2025](https://www.anthropic.com/news/the-anthropic-economic-index)
- Both low-paying and very-high-paying jobs showed very low AI use. Use peaked in mid-to-high-wage occupations. [V] — [Anthropic, Feb 2025](https://www.anthropic.com/news/the-anthropic-economic-index)

**Update (published 27 Mar 2025; data Feb to Mar 2025, after the Claude 3.7 Sonnet launch)**
- Augmentation stayed at about 57%, unchanged from the first report. The fetch tool rendered "learning" interactions as rising from about 23% to about 28%. [V] — [Anthropic, Mar 2025](https://www.anthropic.com/news/anthropic-economic-index-insights-from-claude-sonnet-3-7)
- Community and social service tasks were close to 75% augmentation. Computer and mathematical occupations were closer to 50/50. Translators and interpreters showed the most directive (hands-off) behaviour. [V] — [Anthropic, Mar 2025](https://www.anthropic.com/news/anthropic-economic-index-insights-from-claude-sonnet-3-7)
- A bottom-up taxonomy of 630 granular clusters was released. It includes energy-adjacent clusters such as "Help with water management systems" and "Provide guidance on battery technologies". [V] — [Anthropic, Mar 2025](https://www.anthropic.com/news/anthropic-economic-index-insights-from-claude-sonnet-3-7)

**"Uneven geographic and enterprise AI adoption" (published 15 Sep 2025; Aug 2025 data, first release with first-party API/enterprise traffic)**
- Directive automation on Claude.ai rose from 27% (Dec 2024 to Jan 2025) to 39% (Aug 2025). This was the first report in which automation usage exceeded augmentation. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- In API use, 77% of business uses showed automation patterns, compared with about 50% for Claude.ai users. 97% of API tasks were automation-dominant, compared with 47% on Claude.ai. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- Coding was about 36% of Claude.ai use and about 44% of API use. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- Office and administrative tasks were about 10% of API traffic. Other non-coding API uses included creating marketing materials (4.7%) and processing business and recruitment data (1.9%). The fetch tool summarised that Business & Financial Operations tasks were a smaller share on the API than on Claude.ai. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- **Cost-insensitivity.** "Capabilities seem to matter more than cost in shaping business deployment." Each 1% rise in cost was associated with only a 0.29% fall in usage frequency, after controlling for task characteristics. Higher-cost tasks were used more, not less. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- **Context bottleneck.** "Context constrains sophisticated use. Our analysis suggests that curating the right context for models will be important for high-impact deployments of AI in complex domains." Each 1% increase in input length was associated with only a 0.38% increase in output length. Anthropic says firms may face "costly data modernization and organizational investments to elicit contextual information." [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- **Anthropic AI Usage Index (AUI).** AUI is a country's share of Claude.ai use divided by its share of working-age population, so values above 1 mean usage higher than population alone would predict. Top countries:

  | Country | AUI |
  |---|---|
  | Israel | 7.0 |
  | Singapore | 4.57 |
  | Australia | 4.10 |
  | New Zealand | 4.05 |
  | South Korea | 3.73 |
  | United States | 3.62 |
  | Canada | 2.91 |

  Bottom: India 0.27, Nigeria 0.2. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report); [Anthropic geography page](https://anthropic.com/research/economic-index-geography)
- **European AUI values, conflicting.** A targeted fetch of the Sep 2025 report page returned France 1.94, Germany 1.84 and UK 2.67, with no Italy value. A separate fetch of the geography page said it contains no values for European countries. I could not cross-check against the full PDF, which was blocked. [V, conflicting] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report); [PDF, not accessible](https://assets.anthropic.com/m/218c82b858610fac/original/Economic-Index.pdf); [arXiv version, not accessible](https://arxiv.org/pdf/2511.15080)
- **Italy AUI, secondary only.** Search snippets from an Italian consultancy blog give "Anthropic index 1.70 in Italy vs 3.97 in France". The same blog says Italy uses Claude "in a more office-like way than Germany and France". It also reports Italy's May 2026 Claude.ai mix as 53.6% augmentation and 46.4% automation, with a work share of 42.9% (higher than Germany, France and the UK). The blog appears to draw on Economic Index data from 2026. Its France value (3.97) conflicts with the 1.94 above, so the two probably come from different releases or periods. The June 2026 report text does not mention Italy. Treat all of these as unverified. [2nd] — [Zendata blog (search snippet only; site blocked)](https://zendata.it/en/blog/uso-ai-aziende-dati-italia-anthropic); another aggregator gives other EU values (France 2.66, UK 2.59, Ireland 2.39, Estonia 3.05, Portugal 2.23, Luxembourg 3.07, Poland 1.41, Greece 1.21) from an unspecified release [2nd, unverified].
- Globally, a 1% higher GDP per capita was associated with a 0.7% higher AUI. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- A 1% increase in population-adjusted Claude use correlated with about a 3% reduction in automation. "People in lower-use countries use Claude to automate work more frequently." [V] — [Anthropic geography page](https://anthropic.com/research/economic-index-geography)

**"Economic primitives" (published 15 Jan 2026; data 13 to 20 Nov 2025; 1M Claude.ai conversations plus 1M API records)**
- On Claude.ai, augmentation was 52% (up 5 pp since August) and automation 45% (down 4 pp). [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- On the API, 75% of use was automation and 64% was directive. 74% of API use was work-related, compared with 46% on Claude.ai. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Office & Administrative Support on the API** rose from 10% in Aug 2025 to 13% in Nov 2025 (the fetch rendered this as "rose 3pp in August to 13% in November 2025"). Examples were email management, invoice processing and appointment scheduling. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Task success, as judged by Claude.** Claude.ai 67% and API 49%. Simple (high-school-level) tasks 70%, complex (college-level) tasks 66%. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Task horizon at 50% success.** About 3.5 hours for the API versus about 19 hours for multi-turn Claude.ai. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Speedup.** About 9x for high-school-level prompts and 12x for college-level prompts. More complex tasks save more time but succeed less often. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Implied US labour productivity growth.** Unadjusted, 1.8 pp per year for a decade. Adjusted for success rates, 1.2 pp (Claude.ai) and 1.0 pp (API). Adjusted also for task complementarity (σ=0.5), 0.7 to 0.9 pp. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Deskilling.** "Removing AI-covered tasks would deskill most jobs." The tasks Claude handles average 14.4 years of required education. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)

**"Learning curves" (published 24 Mar 2026; data 5 to 12 Feb 2026)**
- Augmentation on Claude.ai rose slightly, driven by validation and learning patterns. Use cases diversified: the top 10 tasks fell from 24% to 19% of conversations. Personal use rose from 35% to 42%. [V] — [Anthropic, Mar 2026](https://www.anthropic.com/research/economic-index-march-2026-report)
- Users with 6+ months of tenure had about 10% higher conversation success. After controls, the advantage was about 3 to 4 pp. [V] — [Anthropic, Mar 2026](https://www.anthropic.com/research/economic-index-march-2026-report)
- Two automation categories at least doubled on the API: "Business sales & outreach automation" and "Automated trading & market ops". [V] — [Anthropic, Mar 2026](https://www.anthropic.com/research/economic-index-march-2026-report)
- Geographic concentration increased: the top 20 countries' share of per-capita usage rose from 45% to 48%. [V] — [Anthropic, Mar 2026](https://www.anthropic.com/research/economic-index-march-2026-report)

**"Cadences" (published 26 Jun 2026; Economic Index Survey launched Apr 2026; about 9,700 linked respondents; usage linked mid-May to early Jun 2026)**
- Respondents reported gains in speed (86%), scope (82%) and quality (69%). 27% reported cost savings on services they would otherwise buy. [V] — [Anthropic, Jun 2026](https://www.anthropic.com/research/economic-index-june-2026-report)
- 10% rated losing their own job as likely or very likely. [V] — [Anthropic, Jun 2026](https://www.anthropic.com/research/economic-index-june-2026-report)
- Tax-related conversations were 8x more common on 14 Apr than on the average May day. This is evidence of deadline-driven paperwork use. [V] — [Anthropic, Jun 2026](https://www.anthropic.com/research/economic-index-june-2026-report)
- Among respondents coded to management occupations: 24.4% were business owners with employees and 21.7% were self-employed or contractors. [V] — [Anthropic, Jun 2026](https://www.anthropic.com/research/economic-index-june-2026-report)
- Italy is not mentioned in this report. The main text gives no API automation share or office/admin share for this period. [V] — [Anthropic, Jun 2026](https://www.anthropic.com/research/economic-index-june-2026-report)
- **Other 2026 releases** listed on Anthropic's economics team page:
  - "Labor market impacts of AI" (5 Mar)
  - "How Australia uses Claude" (31 Mar)
  - "What 81,000 people told us about the economics of AI" (22 Apr)
  - "Agentic coding and persistent returns to expertise" (16 Jun)
  - "How Canada uses Claude" (14 Jul)
  - "Reviewing the evidence on worker retraining programs" (12 Aug)
  - "Project Swap" (24 Sep 2026)

  None is Italy- or EU-specific. [V] — [Anthropic Economics team](https://www.anthropic.com/research/team/economics)

### Inferences
- **Two usage patterns.** Enterprise API integrations are mostly automation (75 to 77%), while chat is mostly augmentation (about 52 to 57%). An AI-native CER platform will mostly look like the API pattern: directive, automated pipelines. The success-rate gap (49% API vs 67% Claude.ai) suggests automated flows need explicit verification, exception handling and human sign-off where tasks are high-stakes.
- **Relevant task categories are growing on the API.** Office & admin tasks rose from about 10% to 13% of API traffic (Aug to Nov 2025), with invoice processing, email management and scheduling as examples. That growth, plus Italy's reportedly "office-like" usage (unverified), is consistent with document-heavy administration being a mainstream, growing automation category.
- **Moat and pricing.** The context-bottleneck finding supports a moat built on curated, structured regulatory and member context: GSE rules, member PODs, metering data, contracts. It also suggests value-based rather than cost-plus pricing, because enterprise use is price-inelastic (-0.29).
- **Italy is not an early-adopter market.** Italy likely sits below leading EU peers per capita (unverified 1.70 AUI), and lower-AUI countries automate more rather than collaborate. Italian CER administrators may therefore prefer "just do it for me" products over copilots, though this is not directly tested.

### Gaps
- Italy's AUI could not be verified from any primary Anthropic source. The Sep 2025 PDF, arXiv and Hugging Face data were all blocked by egress policy. Neither the Jun 2026 report text nor the Nov 2025 Europe announcement gives Italy data.
- No Anthropic report breaks out energy-sector, utility or energy-community administration tasks specifically.
- The Mar 2025 "learning ~23% to ~28%" figure and the Jan 2026 "office & admin 10% to 13%" wording come from the fetch tool's rendering and should be spot-checked.

---

## Q2. What other Anthropic outputs matter here (Economic Futures, policy, agents in business operations, productivity and time-savings estimates, labour-market measures)?

### Takeaway
Anthropic's own estimates show large time savings per task: about 80% faster, on tasks averaging about 90 minutes. They also imply 1.0 to 1.8 pp of added US productivity growth per year. Anthropic flags that these are model-estimated and larger than what RCTs find. Its agent experiments (Project Vend, Project Swap) show autonomous business agents become profitable only with structured procedures, tools, role separation and oversight. They remain prone to manipulation and legal errors.

### Cited Findings
- **"Estimating AI productivity gains from Claude conversations" (25 Nov 2025; 100,000 Claude.ai conversations)**
  - Tasks would take on average about 90 minutes without AI, and Claude speeds individual tasks by about 80% [S]. The fetch tool rendered the page as "1.4 hours" and "median time savings 84%", so the exact phrasing needs checking. — [Anthropic](https://www.anthropic.com/research/estimating-productivity-gains); [PDF](https://assets.anthropic.com/m/28fda2ad148e2bf5/original/Estimating-AI-productivity-gains-from-Claude-conversations.pdf)
  - Estimated labour cost per task (fetch rendering): management $133, legal $119, computer/math $82, business/financial operations $69, median across all tasks $54. [V] — [Anthropic](https://www.anthropic.com/research/estimating-productivity-gains)
  - Extrapolated, this implies about 1.8% added annual US labour productivity growth over a decade ("roughly twice the run rate in recent years"). Adjusting for task reliability reduces it to about 1.0%. [S/V] — [Anthropic](https://www.anthropic.com/research/estimating-productivity-gains)
  - Validation: self-consistency r = 0.89 to 0.93. On software-engineering tasks, Claude's time estimates correlated with actual completion times at Spearman ρ = 0.44, versus 0.50 for developers' own estimates. [V] — [Anthropic](https://www.anthropic.com/research/estimating-productivity-gains)
  - Caveats: the method cannot count time humans spend validating output outside the conversation. RCTs cited in the paper show smaller gains (56%, 40%, 26%, 14%, and some negative results). [V] — [Anthropic](https://www.anthropic.com/research/estimating-productivity-gains)
- **"Labor market impacts of AI: A new measure and early evidence" (5 Mar 2026)**
  - Introduces "observed exposure", which combines theoretical LLM feasibility with actual work usage and weights automated use more heavily. [V] — [Anthropic](https://www.anthropic.com/research/labor-market-impacts)
  - Coverage: Computer Programmers 75%, Data Entry Keyers 67%. Computer & Math observed coverage is 33% against 94% theoretical. Office & Admin coverage is "significantly below theoretical potential". 30% of workers have zero coverage. [V] — [Anthropic](https://www.anthropic.com/research/labor-market-impacts)
  - "No systematic increase in unemployment for highly exposed workers since late 2022." For ages 22 to 25 in exposed occupations, the job-finding rate fell 14% compared with 2022, "just barely statistically significant". [V] — [Anthropic](https://www.anthropic.com/research/labor-market-impacts)
- **"What 81,000 people told us about the economics of AI" (22 Apr 2026; 80,508 completed responses)**
  - Mean self-rated productivity was 5.1 on a 1 to 7 scale. 48% cited scope expansion as the main benefit and 40% cited speed. [V] — [Anthropic](https://www.anthropic.com/research/81k-economics)
  - About 20% worried about displacement. People in high-exposure occupations were 3x as likely to worry. [V] — [Anthropic](https://www.anthropic.com/research/81k-economics)
- **"Agentic coding and persistent returns to expertise" (16 Jun 2026; about 400,000 Claude Code sessions from about 235,000 users, Oct 2025 to Apr 2026)**
  - Verified success was 15% for novice sessions versus 28 to 33% for intermediate and expert sessions. [V] — [Anthropic](https://www.anthropic.com/research/claude-code-expertise)
  - Users made about 70% of planning decisions but only 20% of execution decisions. [V] — [Anthropic](https://www.anthropic.com/research/claude-code-expertise)
  - "The more understanding a worker brings to an agent, the more quality work the agent is able to do." Domain expertise, not coding background, drives success. [V] — [Anthropic](https://www.anthropic.com/research/claude-code-expertise)
- **Project Vend, Phase 2 (18 Dec 2025)**
  - Setup: an AI shopkeeper was upgraded from Sonnet 3.7 to Sonnet 4/4.5. It was given a CRM, inventory tooling with costs, web search, and a mandatory procedure to double-check prices and delivery times. A separate "CEO" agent and a merchandise agent were added. [V] — [Anthropic](https://www.anthropic.com/research/project-vend-2)
  - Result: "weeks with negative profit margin were largely eliminated." [V] — [Anthropic](https://www.anthropic.com/research/project-vend-2)
  - Lessons stated: "Bureaucracy matters". Roles should be clearly separated. Models act "from something more like the perspective of a friend who just wants to be nice." [V] — [Anthropic](https://www.anthropic.com/research/project-vend-2)
  - Failures persisted. Staff manipulated the agent into accepting an "imposter CEO". It nearly entered an onion futures contract that would have violated the 1958 Onion Futures Act. It proposed below-minimum-wage hiring. [V] — [Anthropic](https://www.anthropic.com/research/project-vend-2)
- **Project Swap (24 Sep 2026; 201 employees; agents negotiating book trades)**
  - Claude's preference rankings matched participants on 61% of pairs (50% is chance). [V] — [Anthropic](https://www.anthropic.com/research/project-swap)
  - Achieved allocation scored 0.55 against an optimum of 0.89. 85% of the shortfall came from how preferences were represented and 15% from trading design. [V] — [Anthropic](https://www.anthropic.com/research/project-swap)
  - Efficiency by model: Haiku 0.75, Sonnet 0.80, Opus 0.88. [V] — [Anthropic](https://www.anthropic.com/research/project-swap)
  - Participants would delegate about 30% of their yearly book budget to agents. [V] — [Anthropic](https://www.anthropic.com/research/project-swap)
- **Claude for Financial Services (15 Jul 2025)**
  - Anthropic claims Claude Opus 4 reached 83% accuracy on complex Excel tasks and passed 5 of 7 Financial Modeling World Cup levels. [V] — [Anthropic](https://www.anthropic.com/news/claude-for-financial-services)
  - Ships MCP connectors (Box, Databricks, FactSet, S&P Global, Snowflake and others). [V] — [Anthropic](https://www.anthropic.com/news/claude-for-financial-services)
  - Vendor-reported customer claim: AIG "compressed the timeline to review business by more than 5x" and improved "data accuracy from 75% to over 90%". [V, vendor claim] — [Anthropic](https://www.anthropic.com/news/claude-for-financial-services)
- **Economic Futures, UK & Europe (5 Nov 2025)**
  - Offers grants and API credits for European researchers and runs an LSE symposium. [V] — [Anthropic](https://www.anthropic.com/news/economic-futures-uk-europe)
  - Commits to "expanding the Anthropic Economic Index to provide more granular, Europe-specific information". [V] — [Anthropic](https://www.anthropic.com/news/economic-futures-uk-europe)
  - Country examples given for the UK (academic research), Germany (equipment calibration and repair) and France (tourism and culture). No Italy data. [V] — [Anthropic](https://www.anthropic.com/news/economic-futures-uk-europe)
- **Economic Futures research awards** are $10,000 to $50,000 grants. [S] — [Anthropic Economic Futures program](https://www.anthropic.com/economic-futures/program)
- **Policy responses (14 Oct 2025)**
  - Ideas are grouped by scenario: workforce training grants, tax-incentive reform, faster infrastructure permitting, trade-adjustment assistance for AI, compute/token taxes, sovereign wealth funds, VAT, and a business wealth tax. [V] — [Anthropic](https://www.anthropic.com/research/economic-policy-responses)
  - Most ideas came from the Economic Advisory Council, symposia and independent researchers. [S] — [Anthropic policy](https://www.anthropic.com/research/economic-policy-responses)

### Inferences
- **Size of the prize.** The 80% per-task speedup is an upper bound. The Humlum-Vestergaard 2.8% (Q3) is a realised, workforce-wide lower bound. A CER product that performs the task end-to-end, rather than handing admins a chatbot, is the way to capture something closer to the per-task gain.
- **Design for agents.** Project Vend's lesson ("bureaucracy matters": procedures, tools, CRM, separated roles, supervisor agent) maps directly onto CER operations. Encode GSE procedures as explicit workflows with checklists and verification steps. Do not rely on free-form agent judgement, especially for anything legal or financial.
- **Data capture drives agent quality.** Project Swap found 85% of lost value came from poor preference representation. Structured intake at member onboarding (documents, POD, consumption profile, payout preferences) likely matters more than the sophistication of downstream agents.
- **Domain expertise is a moat.** Returns to expertise in agentic coding favour founders and operators with deep CER and GSE knowledge. AI lowers build cost but does not remove the value of expertise.

### Gaps
- Membership of the Economic Advisory Council and the Economic Futures program launch date were not verified in this session.
- The Project Vend Phase 1 (Jun 2025) details were not fetched. Phase 2 summarises them.
- There is no Anthropic study on energy, utility or public-sector administration workflows specifically.

---

## Q3. What does academic evidence say about generative AI productivity in business and administrative tasks, including effect sizes and where AI fails?

### Takeaway
Controlled studies find large gains on tasks within AI's capability: +14% in customer support, with +34% for novices; -40% time and +18% quality in professional writing; +12.2% tasks completed, 25.1% faster and more than 40% higher quality at BCG. The largest gains go to less-experienced workers. Just outside the capability "frontier", AI makes correct answers much less likely. Realised economy-wide effects so far are small: 2.8% time savings in Denmark, and no earnings or hours effects. Macro estimates range from Acemoglu's at most 0.66% TFP over 10 years up to Anthropic's 1 to 1.8 pp per year.

### Cited Findings
- **Brynjolfsson, Li & Raymond, "Generative AI at Work", QJE 140(2): 889–942 (2025); NBER w31161 (2023)**
  - 5,179 customer-support agents. AI assistance raised productivity (issues resolved per hour) by about 14% on average and 34% for novice and low-skilled workers, with minimal impact on experienced and highly skilled workers. [S] — [QJE](https://academic.oup.com/qje/article/140/2/889/7990658); [NBER](https://www.nber.org/papers/w31161)
  - The authors interpret this as AI disseminating the best practices of more able workers. [S] — [NBER](https://www.nber.org/papers/w31161)
- **Noy & Zhang, Science (2023), "Experimental evidence on the productivity effects of generative artificial intelligence"**
  - College-educated professionals doing mid-level writing tasks with ChatGPT (GPT-3.5): time fell 40% and quality rose 18%. Inequality between writers narrowed. [S] — [Science](https://www.science.org/doi/10.1126/science.adh2586); [MIT News](https://news.mit.edu/2023/study-finds-chatgpt-boosts-worker-productivity-writing-0714)
- **Dell'Acqua et al., HBS Working Paper 24-013 (Sep 2023), "Navigating the Jagged Technological Frontier"**
  - 758 BCG consultants (about 7% of individual contributors) on 18 tasks inside the frontier: 12.2% more tasks completed, 25.1% faster, more than 40% higher quality. [S] — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4573321)
  - On a task deliberately chosen to be outside the frontier, AI users were 19 percentage points less likely to produce correct solutions. The snippet said "19%", and the paper's wording is believed to be "percentage points". [S] — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4573321)
- **Eloundou, Manning, Mishkin & Rock, "GPTs are GPTs", Science 384 (2024)**
  - About 80% of the US workforce could have at least 10% of their tasks affected by LLMs. About 19% could have at least 50% affected. [S] — [Science](https://www.science.org/doi/10.1126/science.adj0998)
  - Counting complementary software, the share of jobs with more than half their tasks affected rises to "just over 46%". [S] — [Science](https://www.science.org/doi/10.1126/science.adj0998)
- **Acemoglu, "The Simple Macroeconomics of AI", Economic Policy 40(121), Jan 2025 (NBER w32487, 2024)**
  - A task-based, Hulten's-theorem approach implies "no more than a 0.66% increase in TFP over 10 years". Adjusted for hard-to-learn tasks, the estimate is "less than 0.53%". [S] — [Economic Policy](https://academic.oup.com/economicpolicy/article-abstract/40/121/13/7728473); [NBER PDF](https://www.nber.org/system/files/working_papers/w32487/w32487.pdf)
- **Humlum & Vestergaard, "Large Language Models, Small Labor Market Effects" (BFI WP 2025-56, Apr 2025; NBER w33777)**
  - Denmark, surveys in late 2023 and 2024: 25,000 workers in 7,000 workplaces across 11 AI-exposed occupations (including accountants, customer support, HR, legal and marketing), linked to register data. [S] — [BFI WP](https://bfi.uchicago.edu/wp-content/uploads/2025/04/BFI_WP_2025-56-1.pdf)
  - Average time savings were 2.8% of work hours. There was no significant effect on earnings or recorded hours, and confidence intervals rule out effects larger than 1%. [S] — [BFI WP](https://bfi.uchicago.edu/wp-content/uploads/2025/04/BFI_WP_2025-56-1.pdf)
  - Adoption was 83% with employer encouragement versus 47% without. 8.4% of workers reported new AI-created tasks, such as reviewing AI output. [2nd] — [ODSC summary](https://opendatascience.com/ai-chatbots-show-minimal-impact-on-jobs-and-wages-new-study-finds/)
  - The NBER listing for w33777 now appears under the title "Still Waters, Rapid Currents: Early Labor Market Transformation under Generative AI", apparently a 2026 revision. I did not review what changed. [S] — [NBER w33777](https://www.nber.org/papers/w33777)
- **Brynjolfsson, Chandar & Chen, "Canaries in the Coal Mine?" (Stanford Digital Economy Lab, Aug 2025; an Aug 2026 version exists)**
  - ADP payroll data show a 13% relative decline in employment for workers aged 22 to 25 in the most AI-exposed occupations. The decline is concentrated where AI automates rather than augments. [S] — [Stanford DEL](https://digitaleconomy.stanford.edu/publication/canaries-in-the-coal-mine-six-facts-about-the-recent-employment-effects-of-artificial-intelligence/)

### Inferences
- **Where AI fails.** The jagged-frontier result (-19 pp outside the frontier) is the key design risk for "compliance with changing rules" and clawback forecasting. These tasks look like document work but can hinge on the correct reading of new decrees, GSE operating rules or edge cases. Keep AI in validation and augmentation mode there, with human review and citations to source rules.
- **Where AI helps most.** Gains are largest for novices (+34%) and for writing and communication (-40% time), which favours automating member communications and first-line support. Many CER admins (volunteers, municipal staff, small ESCOs) are non-experts, which is exactly where AI assistance helps most.
- **Selling the product.** The Denmark evidence (2.8% realised savings; adoption driven by employer encouragement) suggests "AI features" alone will not deliver ROI. The product should own the workflow end-to-end ("services-as-software") so value does not depend on user skill or effort.

### Gaps
- I could not verify from full text:
  - Acemoglu's intermediate figures (share of tasks exposed, cost savings, GDP range).
  - Dell'Acqua's split between below-average and above-average performers.
  - Noy & Zhang's exact sample size.
- No academic RCT was found on AI for regulatory filings or energy-community administration specifically.
- I did not review the 2026 revisions of Humlum & Vestergaard or the "Canaries" paper.

---

## Q4. How does AI change vertical SaaS economics and defensibility (lower build costs, services-as-software, outcome-based pricing)?

### Takeaway
Credible venture-capital sources (a16z, Bessemer, Foundation Capital) argue that AI lets vertical software capture labour and services spend, not just software budgets. That makes small niches viable, and pricing shifts from seats toward outcomes. These are investor opinions rather than peer-reviewed evidence. AI-heavy products also show much lower gross margins, and cheaper building raises competitive pressure. Anthropic's findings on price-insensitivity and the context bottleneck give the most rigorous support: pricing on value and building a moat from proprietary context.

### Cited Findings
- **a16z, "'AI Inside' Opens New Markets for Vertical SaaS" (Dec 2024; opinion/VC)**
  - US software spend ($313bn) was only 3% of US labour spend ($10.5T) in 2022. [S] — [a16z](https://a16z.com/vsaas-vertical-saas-ai-opens-new-markets/)
  - Illustration: a market of 10k customers paying $1k/month grows from $120M to $1.2B when AI enables service offerings such as marketing, customer support and back-office invoicing and data entry. [S] — [a16z](https://a16z.com/vsaas-vertical-saas-ai-opens-new-markets/)
  - AI makes niches previously dismissed as too small viable. [S] — [a16z](https://a16z.com/vsaas-vertical-saas-ai-opens-new-markets/)
- **Foundation Capital, "service-as-software" (opinion/VC)**
  - A $4.6T opportunity, based on the claim that "for every dollar businesses spend on software, they spend about six on services". [S] — [Foundation Capital](https://foundationcapital.com/the-4-6t-service-as-software-opportunity-lessons-from-year-one/)
  - Pricing is moving along a spectrum from access-based to usage-, workflow- and outcome-based. [S] — [Foundation Capital](https://foundationcapital.com/ideas/ai-leads-a-service-as-software-paradigm-shift)
  - Example: Intercom's Fin charges $0.99 per successful resolution. [S] — [Foundation Capital](https://foundationcapital.com/ideas/ai-leads-a-service-as-software-paradigm-shift)
- **Bessemer, "State of AI 2025" (Aug 2025; VC)**
  - "Supernova" AI startups average about 25% gross margin and $1.13M ARR per FTE (4 to 5x typical SaaS). "Shooting Stars" average about 60% gross margin and $164K ARR per FTE. [S] — [Bessemer](https://www.bvp.com/atlas/the-state-of-ai-2025)
  - Bessemer describes vertical AI as targeting "high cost repetitive language-based tasks", delivered as copilots, agents or AI-enabled services. [S] — [Bessemer](https://www.bvp.com/atlas/the-state-of-ai-2025)
  - Incumbent vertical SaaS vendors must "evolve or become obsolete". [S] — [Bessemer](https://www.bvp.com/atlas/the-state-of-ai-2025)
  - Vertical SaaS firms such as Toast and ServiceTitan monetise payments as well as software. [S] — [Bessemer](https://www.bvp.com/atlas/the-state-of-ai-2025)
  - Bessemer published a "Building Vertical AI" book in Jan 2026, which I did not review. — [Bessemer PDF](https://www.bvp.com/assets/uploads/2026/01/BUILDING-VERTICAL-AI_PDF_BESSEMER_VENTURE_PARTNERS_BOOK_JANUARY_2026.pdf)
- **Anthropic evidence relevant to defensibility**
  - Enterprise deployment is price-inelastic: "Capabilities seem to matter more than cost". [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
  - Context curation is the constraint in complex domains. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
  - Domain expertise persistently raises agent output quality. [V] — [Anthropic, Jun 2026](https://www.anthropic.com/research/claude-code-expertise)
  - 27% of surveyed users report saving money on services they would otherwise buy, which is direct substitution of services spend. [V] — [Anthropic, Jun 2026](https://www.anthropic.com/research/economic-index-june-2026-report)

### Inferences
- **Bigger pool, more competitors.** For a CER platform, the addressable spend is the consultant and administrator fees CERs pay, plus internal volunteer or municipal time, not just software licences. Services-as-software with outcome-linked pricing becomes plausible, for example per completed GSE application, per reconciled period, or a share of incentives administered. Lower build costs (agentic coding) also mean more entrants, including consultancies productising their own services.
- **Defensibility.** The durable assets are:
  - proprietary, structured context: a curated GSE/CER rules corpus kept current, and historical reconciliation data per CER;
  - workflow embedding as the system of record for member registries and payouts;
  - payments and payout flows, following the Toast/ServiceTitan pattern;
  - domain expertise encoded into procedures.

  Model capability itself is not defensible.
- **Margins.** Bessemer's 25% vs 60% gross margins warn that inference-heavy automation compresses margins. Use deterministic code for calculations and reserve LLM calls for unstructured documents and communications.

### Gaps
- No peer-reviewed academic study was found on how AI changes vertical SaaS unit economics or competition. Available sources are VC or opinion pieces, and they have an incentive to promote the thesis.
- Bessemer "State of the Cloud 2025/2026" and the "Building Vertical AI" (Jan 2026) contents were not reviewed because bvp.com was blocked.
- No evidence was found on how outcome-based pricing is adopted in EU or Italian B2B markets.

---

## Q5. What is EU and Italy AI adoption among SMEs and public administration, and which EU AI Act and Italian obligations apply to such a product?

### Takeaway
In 2025, 20.0% of EU enterprises with 10+ employees used AI, up from 13.5% in 2024. Italy was at 16.4% (up from 8.2%), and Italian SMEs at 15.7% against 53.1% for large firms. The size gap is widening, and a lack of skills is the main barrier. Italian public administration is at an early, project-based stage: 45 of 108 responding entities had AI projects in AgID's 2025 survey. A CER-administration SaaS is very likely outside the AI Act's high-risk categories. Annex III obligations are in any case deferred to 2 Dec 2027. Italy's Law 132/2025 applies alongside the AI Act, and public-sector customers bring localisation requirements.

### Cited Findings
- **Eurostat, enterprise AI use (news release 11 Dec 2025)**
  - 20.0% of EU enterprises (10+ employees) used AI in 2025, up 6.5 pp from 13.5% in 2024. [S] — [Eurostat](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2)
  - By size: small 17.0%, medium 30.4%, large 55.0%. [S] — [Eurostat](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2)
  - Highest: Denmark 42.0%, Finland 37.8%, Sweden 35.0%. Lowest: Romania 5.2%, Poland 8.4%, Bulgaria 8.5%. [S] — [Eurostat](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2)
  - By technology: text mining 11.75%, generation of images, video or audio 9.55%, generation of written or spoken language or code 8.76%. [S] — [Eurostat](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2)
- **Eurostat, purposes of AI use among EU AI-using enterprises (Statistics Explained; reference year not confirmed in the snippet)**
  - Marketing and sales 34.7%, organising business administration or management 31.1%, accounting, controlling or finance management 23.1%. [S] — [Eurostat Statistics Explained](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises)
- **Istat, "Imprese e ICT – Anno 2025" (15 Dec 2025)**
  - 16.4% of Italian enterprises with 10+ employees used at least one AI technology in 2025, up from 8.2% in 2024 and 5.0% in 2023. [S] — [Istat](https://www.istat.it/comunicato-stampa/imprese-e-ict-anno-2025/); [Istat PDF](https://www.istat.it/wp-content/uploads/2025/12/Statreport_ICT2025.pdf)
  - SMEs rose from 7.7% to 15.7% and large firms from 32.5% to 53.1%. The large-vs-SME gap widened from about 20 pp (2023) to about 25 pp. [S] — [Istat](https://www.istat.it/comunicato-stampa/imprese-e-ict-anno-2025/)
  - Lack of skills blocks adoption in almost 60% of firms that considered AI but did not adopt it. 83.6% of enterprises still use no AI. [S] — [Istat](https://www.istat.it/comunicato-stampa/imprese-e-ict-anno-2025/); [key4biz](https://www.key4biz.it/ai-raddoppia-luso-nelle-imprese-italiane-dall82-del-2024-al-164-del-2025-i-dati-istat/559811/)
  - Among Italian AI users, the top functions are marketing and sales (33.1%), organising administrative processes (25.7%) and R&D (20.0%). [S] — [Istat](https://www.istat.it/comunicato-stampa/imprese-e-ict-anno-2025/) (attributed via search snippet)
- **AgID, "L'Intelligenza Artificiale nella Pubblica Amministrazione" (report dated 10 Jun 2025)**
  - 142 central administrations and public service operators were surveyed, and 108 responded (76%). The survey recorded 120 AI projects across 45 entities. [S] — [AgID](https://www.agid.gov.it/sites/agid/files/2025-06/AGID_Ricognizione_Progetti_AI_Rapporto_2025_V_2_2_10giu25.pdf)
  - The Piano Triennale ICT 2024–2026 (2025 update) includes a "Strumento 5" on AI in public administration. [S] — [Piano Triennale](https://docs.italia.it/italia/piano-triennale-ict/pianotriennale-ict-doc/it/2024-2026-agg-2025/strumenti/strumento-5_intelligenza-artificiale-nella-pubblica-amministrazione.html)
- **Italian Law 132/2025 (Legge 23 Sep 2025 n.132)**
  - In force since 10 Oct 2025, it is the first comprehensive national AI law in the EU. [S] — [Norton Rose Fulbright](https://www.nortonrosefulbright.com/en/knowledge/publications/9bfedfea/italy-enacts-law-no-132-2025-on-artificial-intelligence-sector-rules-and-next-steps)
  - AgID and ACN are the national AI authorities. [S] — [Norton Rose Fulbright](https://www.nortonrosefulbright.com/en/knowledge/publications/9bfedfea/italy-enacts-law-no-132-2025-on-artificial-intelligence-sector-rules-and-next-steps)
  - It is to be applied consistent with the AI Act without extra obligations beyond it. [S] — [Norton Rose Fulbright](https://www.nortonrosefulbright.com/en/knowledge/publications/9bfedfea/italy-enacts-law-no-132-2025-on-artificial-intelligence-sector-rules-and-next-steps)
  - It reportedly mandates server localisation for public-sector systems. [S] — [Cleary Gottlieb](https://www.clearygottlieb.com/news-and-insights/publication-listing/italy-adopts-the-first-national-ai-law-in-europe-complementing-the-eu-ai-act)
- **EU AI Act timing after the Digital Omnibus**
  - Political agreement on 7 May 2026 postponed Annex III (stand-alone high-risk) obligations from 2 Aug 2026 to 2 Dec 2027. Annex I (product-embedded) obligations move to 2 Aug 2028. [S] — [Travers Smith](https://www.traverssmith.com/knowledge/knowledge-container/eu-agrees-to-delay-key-ai-act-compliance-deadlines/); [Morgan Lewis, Jun 2026](https://www.morganlewis.com/pubs/2026/06/eu-approves-delays-and-other-amendments-to-certain-eu-ai-act-obligations-what-businesses-should-know)
  - One source states the Digital Omnibus on AI entered into force on 27 Jul 2026. [2nd] — [regulation-ai.eu](https://www.regulation-ai.eu/en/annex-iii/)
- **Energy-related high-risk category.** Annex III's critical-infrastructure category covers AI "as a safety component in the management and operation of critical digital infrastructure, road traffic, or the supply of water, gas, heating or electricity". [S] — [Baker Botts, May 2026](https://www.bakerbotts.com/thought-leadership/publications/2026/may/ai-regulatory-update-for-energy-new-timelines-in-the-eu-new-standards-in-the-us); [McCann FitzGerald](https://www.mccannfitzgerald.com/knowledge/construction-and-infrastructure/critical-infrastructure-spotlight-eu-ai-act-draft-guidelines-on-high-risk-ai-classification)

### Inferences
- **Market readiness.** Italy is below the EU average, and Italian SMEs are far behind large firms, with skills as the main barrier. A product that requires AI skills from CER administrators will struggle. One that hides AI behind done-for-you workflows fits the adoption gap. EU firms already apply AI mostly to administration (31.1%) and accounting/finance (23.1%), the CER platform's core functions, so the use case is familiar.
- **Municipal CERs.** Many CERs involve municipalities. Italian public administration is still at the pilot or project stage (45 of 108 AgID respondents), and Law 132/2025 adds localisation expectations for public-sector systems. EU or Italy data residency and clear AgID/ACN-aligned documentation will likely matter in procurement.
- **AI Act classification.** Back-office administration software (paperwork, reconciliation, payouts, communications) is not a "safety component" in the operation of electricity supply. It is therefore very likely not high-risk under the critical-infrastructure category. Two edge cases need legal review:
  1. Annex III point 5 covers systems used by or on behalf of public authorities to assess eligibility for public benefits or services. This could arise if the product were used by GSE, or by a municipality acting as a public authority, to decide eligibility.
  2. Any feature that scores individuals' creditworthiness.

  Limited-risk transparency duties (disclosing that a chatbot is AI in member communications) are likely to apply. I did not re-verify the Annex III point 5 wording or the Article 50 dates in this session.

### Gaps
- Eurostat and Istat pages were blocked, so figures come from search-engine summaries of those official pages. The reference year for the EU "purposes" percentages is unconfirmed.
- I found no Eurostat or Istat statistic on the share of public administrations using AI. Eurostat's enterprise survey excludes the public sector, and only the AgID survey (central administrations) was found. There is no data on municipalities.
- I found no data on AI adoption by energy communities, ESCOs or the Italian energy-services sector specifically.
- Not verified:
  - whether the Digital Omnibus changed the dates for Article 50 transparency obligations or Article 4 AI literacy;
  - the exact final legal status and Official Journal date of the Omnibus;
  - the exact Law 132/2025 localisation article.

---

## Q6. What does this mean for the CER product: (a) automate vs augment, (b) SaaS economics and defensibility, (c) adoption by geography and firm size, (d) risks?

### Takeaway
The evidence supports two modes. Fully automate high-volume, document-centric office work: onboarding and document collection, form preparation, first-line member communications. Augment, with human verification, rule interpretation and anything financially or legally binding. Implement reconciliation and payout calculations as deterministic code rather than LLM output. Defensibility comes from curated regulatory context, workflow ownership and payments, not model access. Italian SME and public-sector adoption lags, which favours a done-for-you, services-as-software offer.

### Cited Findings
- **Reliability.** Automated (API) flows succeed less often than interactive ones: 49% vs 67%. The 50%-success horizon is about 3.5 hours on the API versus about 19 hours on Claude.ai. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Office work is being automated.** Office/admin automation on the API is growing (from about 10% to 13%, Aug to Nov 2025), with invoice processing and email management as examples. [V] — [Anthropic, Jan 2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)
- **Data entry is highly exposed.** Data Entry Keyers have 67% observed exposure. [V] — [Anthropic, Mar 2026](https://www.anthropic.com/research/labor-market-impacts)
- **Customer support.** Support agents saw +14% productivity, +34% for novices. [S] — [QJE 2025](https://academic.oup.com/qje/article/140/2/889/7990658)
- **Outside the frontier.** Accuracy fell 19 pp on the out-of-frontier task. [S] — [Dell'Acqua et al. 2023](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4573321)
- **Agents need structure.** Business agents needed procedures and oversight, and still made legal errors. [V] — [Project Vend 2](https://www.anthropic.com/research/project-vend-2)
- **Pricing and moat signals.** Enterprise use is price-inelastic (-0.29), and context is the bottleneck. [V] — [Anthropic, Sep 2025](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report)
- **Italian adoption.** 16.4% AI adoption in Italy in 2025, SMEs 15.7%, skills cited by about 60% of non-adopters. [S] — [Istat 2025](https://www.istat.it/comunicato-stampa/imprese-e-ict-anno-2025/)
- **Realised gains are small without employer push.** Realised time savings were 2.8%, and adoption depended on employer encouragement (83% vs 47%). [S/2nd] — [Humlum & Vestergaard](https://bfi.uchicago.edu/wp-content/uploads/2025/04/BFI_WP_2025-56-1.pdf)

### Inferences
**(a) Automate vs augment, by task:**

| Task | Mode | Why |
|---|---|---|
| Member onboarding and document collection | Automate | Extraction, completeness checks, reminders, data entry (Data Entry Keyers 67% exposure; office/admin API growth). Route exceptions to a human queue. |
| GSE paperwork | Automate drafting and assembly; human sign-off before submission | Directive, office-like work, but consequential. The jagged frontier and Vend's legal naïveté argue against unsupervised submission. |
| Incentive reconciliation and clawback forecasting | Deterministic engine; AI to augment | AI explains variances, flags anomalies, drafts scenario narratives, and helps build and maintain rule code. Numbers must not come from free-form generation (API success 49%). |
| Member payouts and accounting | Deterministic automation; AI for exceptions and communications only | Financial and legal exposure. |
| Member communications | Automate first-line and templated messages; augment sensitive ones | Strongest evidence base (writing -40% time; support +14 to 34%). Disclose AI use. |
| Compliance with changing rules | Augment | AI monitors and summarises new rules and proposes rule-engine changes. Experts validate. This is where value and risk are both highest (context bottleneck; outside the frontier). |

**(b) Economics.**
- Price on outcomes or value (per application filed, per period reconciled, or a share of administered incentives) rather than seats. Demand is price-inelastic and the substituted spend is services and labour.
- Build competition will be intense, so the moat should be proprietary context and data, embedded workflow, payments, and verified accuracy.
- Watch gross margins: Bessemer's 25% vs 60% contrast.

**(c) Adoption.**
- Italy and SMEs lag the EU and are skills-constrained. Sell outcomes, not tools, and bundle onboarding and training.
- Municipal members bring public-administration procurement, localisation and AgID/ACN expectations.

**(d) Risks.**
- Unreliability of automated flows and errors outside the frontier, especially regulatory interpretation.
- Manipulation of agents (Vend).
- Over-trust and deskilling of human reviewers (Jan 2026 deskilling finding).
- Inference-cost margin compression.
- Commoditisation from lower build costs.
- Regulatory shifts: AI Act dates moving via the Omnibus, Law 132/2025 and possible high-risk edge cases.
- Realised productivity may be far below per-task estimates (2.8% vs 80%).

### Gaps
- There is no direct empirical evidence on AI performance on Italian-language regulatory filings, GSE portal workflows or energy-community accounting. Every task mapping above is an inference from adjacent evidence.
- No data was found on the current cost of CER administration (consultant fees, hours per CER), which would anchor outcome-based pricing.

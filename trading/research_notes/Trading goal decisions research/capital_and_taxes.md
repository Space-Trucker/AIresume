# Capital, account and tax matters before moving the Alpaca system from paper to real money

*Research date 2026-10-15. This is information, not tax, legal or investment advice. Items marked "adviser" need a professional.*

*Method and limits (read first):*
- *Page fetches were blocked in this environment: WebFetch failed DNS for every host, and the proxy refused direct downloads. Every fact below therefore comes from web-search extracts of the cited pages, not from reading each page in full.*
- *The shared web-search budget ran out before every planned cross-check was done. Open items are listed under each Gaps heading.*

*Tags used:*
- ***[2+]*** *two or more independent sources agree.*
- ***[issuer-only]*** *several pages from one issuer agree (for example Alpaca's docs, blog and support pages, or two copies of a statute) but nothing independent was found. Treat these as single-source.*
- ***[single-source]***
- ***[secondary]*** *practitioner or blog summary; the primary text was not seen.*
- ***[conflict]*** *sources disagree.*
- ***[dated]*** *the source may be stale.*

---

## 1. US resident, default treatment: short-term gains, wash sales (other accounts, IRAs, shorts), broker 1099-B versus the taxpayer's duty, and the short-sale rules (§§1233, 263(h), 1259, 1092)

### Takeaway
**Default treatment.** Without trader tax status (TTS) and a §475(f) election, every closed trade is a short-term capital gain or loss, because positions are held for seconds to about 5 days. Net capital losses are capped at $3,000 a year against other income.

**Wash sales.**
- The rule will defer many losses, because the system keeps re-trading the same symbols.
- It follows the taxpayer across all accounts, the spouse's accounts and IRAs. A repurchase in an IRA loses the loss permanently.
- Alpaca's Form 1099-B applies the rule only within one account and one CUSIP, so tracking across accounts is the owner's job.
- As the statute is commonly read, the rule also covers losses on closing short sales (§1091(e)). That was not verified this session.

**Short-sale rules.** These mostly become design constraints:
- In-lieu dividend payments on shorts held 45 days or less are added to basis rather than deducted.
- Shorting a symbol the owner holds long at a gain anywhere can be a constructive sale.

### Cited Findings
#### Character of gains and the loss limit
- Property held one year or less produces short-term gain or loss; property held more than one year produces long-term gain or loss. — [IRS Pub. 550 (2025)](https://www.irs.gov/publications/p550) [single-source, primary; standard rule]
- Without a valid §475(f) election, the capital-loss limits and the wash-sale rules apply to a trader just as to an investor. With a timely election they do not. — [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [IRS Pub. 550 (2025)](https://www.irs.gov/publications/p550); [IRS 2025 Instructions for Form 4797](https://www.irs.gov/pub/irs-pdf/i4797.pdf) [2+, IRS]
- The capital-loss cap is $3,000 of net capital loss per year against ordinary income. — [Beancount.io trader-tax guide, May 2026](https://beancount.io/blog/2026/05/11/trader-tax-status-section-475f-mark-to-market-election-wash-sale-rule-3000-capital-loss-cap-day-traders-guide) [single-source, secondary]
- Self-employment tax:
  - Investment income is not subject to self-employment tax (Topic 429).
  - Gains from selling securities as a trader are not subject to it either, whether or not §475(f) is elected (Pub. 550).
  - Sources: [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [IRS Pub. 550 (2025)](https://www.irs.gov/publications/p550) [2+, IRS]

#### Wash sales (IRC §1091)
- A loss is disallowed if substantially identical stock is acquired within 30 days before or after the loss sale (a 61-day window). The disallowed loss is normally added to the basis of the replacement shares. — [Jupid wash-sale guide 2026](https://jupid.com/blog/wash-sale-rule-guide-2026); [National Tax Tools guide](https://nationaltaxtools.com/guides/wash-sale-rule/) [2+, secondary; statute text not seen]
- The rule applies across the taxpayer's whole portfolio, not account by account. Pub. 550 extends it to purchases made for the taxpayer's IRA or Roth IRA, by the spouse, and by a corporation the taxpayer controls. — [National Tax Tools](https://nationaltaxtools.com/guides/wash-sale-rule/); [CPA Validated wash-sale guide](https://cpavalidated.com/wash-sale-guide.html) [2+, secondary]
- Rev. Rul. 2008-5: buying in an IRA or Roth IRA within the window disallows the loss in the taxable account. The IRA basis is not increased under §1091(d), so the loss is lost permanently. — [Kitces](https://www.kitces.com/blog/irs-shuts-down-wash-sale-evasion-technique/); [Lexology](https://www.lexology.com/library/detail.aspx?g=1faaa7b8-d054-420c-a910-8bbe8540bf6c) [2+]

#### Broker Form 1099-B versus the taxpayer's obligation
- Under Treas. Reg. §1.6045-1, a broker must apply §1091 only when both the sale and the purchase are covered securities with the same CUSIP (or other designated identifier). The broker reports the disallowed loss on the sale that triggered it. — [26 CFR §1.6045-1, GovInfo 2012 edition](https://www.govinfo.gov/content/pkg/CFR-2012-title26-vol13/pdf/CFR-2012-title26-vol13-sec1-6045-1.pdf) [primary, but a 2012 edition; confirm against the current eCFR]
- Brokers must report only when the transactions occur in the same account. They are not required to report IRA repurchases (the Rev. Rul. 2008-5 case), so the investor "may not be aware". — [KPMG TaxNewsFlash, July 2022](https://kpmg.com/kpmg-us/content/dam/kpmg/taxnewsflash/pdf/2022/07/22208.pdf) [single-source; consistent with the regulation]
- What the 1099-B misses:
  - It generally does not identify a replacement purchase in another account, even another account at the same firm.
  - Losses washed by a purchase in a spouse's account, at another broker or in an IRA never appear on any 1099-B.
  - Those are the taxpayer's responsibility.
  - Sources: [GreenTraderTax: why broker 1099-B reporting is not taxpayer compliance](https://greentradertax.com/wash-sale-accounting-why-broker-form-1099-b-reporting-is-not-taxpayer-compliance/); [TradeLog: Form 1099-B brokerage reporting](https://tradelog.com/education/irs-form-1099-b-brokerage-reporting/) [2+, secondary]
- Practitioner practice is to report broker-flagged wash sales on Form 8949 with adjustment code W, so the return ties to the 1099-B. — [TaxShark FAQ](https://taxsharkinc.com/why-does-your-1099-b-show-a-wash-sale-w-examples-faqs/) [single-source, secondary]

#### Payments in lieu of dividends on shorts (§263(h))
- §263(h) rules:
  - No deduction is allowed for a payment in lieu of a dividend on stock used in a short sale if the short is closed within 45 days.
  - The window is one year when the payment relates to an extraordinary dividend.
  - The disallowed amount is added to the basis of the stock used to close the short.
  - Hedging transactions under §1256(e) are excepted.
  - Sources: [26 U.S.C. §263 (Cornell LII)](https://www.law.cornell.edu/uscode/text/26/263); [26 U.S.C. §263 (GovInfo, 2023)](https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleA-chap1-subchapB-partIX-sec263.htm) [issuer-only: two copies of the statute]

#### Short sales (§1233)
- §1233 sets an anti-abuse rule for short sales against substantially identical property:
  - The holding period of that property is treated as beginning on the date the short is closed, or on its earlier sale, gift or other disposition.
  - The rule applies in order of acquisition and only to the quantity sold short.
  - A loss on closing the short is long-term if substantially identical property had been held more than one year on the short-sale date.
  - Sources: [IRC §1233 (Bloomberg Tax)](https://irc.bloombergtax.com/public/uscode/doc/irc/1233); [26 CFR §1.1233-1 (eCFR)](https://www.ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1/subject-group-ECFR56edfa33b27e3cf/section-1.1233-1) [2+, primary]

#### Constructive sales (§1259)
- A constructive sale happens when someone holding an appreciated position enters into one of these:
  - a short sale of the same or substantially identical property;
  - an offsetting notional principal contract;
  - a futures or forward contract to deliver the property.
- The consequences:
  - Gain is recognized as if the position were sold at fair market value that day.
  - A new holding period starts.
  - Transactions by a related person made to avoid the rule can count.
  - Sources: [IRS Pub. 550 (2025)](https://www.irs.gov/publications/p550); [IRS Pub. 550 (2020)](https://www.irs.gov/pub/irs-prior/p550--2020.pdf) [issuer-only: IRS, two editions]
- There is a closed-transaction exception. It requires that the hedge is closed by the 30th day after the end of the tax year, and that the appreciated position is then held unhedged for 60 days. — [IRS Pub. 550 (2020)](https://www.irs.gov/pub/irs-prior/p550--2020.pdf) [single-source, primary, older edition]

### Inferences
- **Scale of the wash-sale problem.** About 25 round trips a week is roughly 1,300 a year, concentrated in repeat symbols, so without §475(f) washed losses will be routine. Most are deferrals into the replacement lot. Losses sitting in lots still open on 31 December move into the next tax year, so taxable income in the first live year can exceed economic profit.
- **Decision: keep the bot's symbols out of other accounts.** Either keep the bot's symbols (and substantially identical ETFs) out of the owner's and spouse's other accounts and IRAs, or track every such purchase.
  - An IRA purchase of a symbol the bot just sold at a loss destroys that loss permanently, and nothing on Alpaca's 1099-B will show it.
  - Index ETFs bought automatically in retirement accounts are the likeliest accidental overlap.
- **Decision: choose cross-account wash-sale accounting.** Use software or a CPA that applies §1091 across all accounts, and to short sales, rather than relying on the 1099-B.
- **Decision: filter shorts by ex-dividend date.** With holds of 5 days or less, every in-lieu dividend paid on a short falls inside §263(h)'s 45-day window. It is added to basis instead of deducted, on top of its economic cost. A filter that avoids holding shorts over ex-dividend dates removes both effects.
- **Decision: add a constructive-sale check.** The bot must never short a symbol, or one substantially identical to it, that the owner holds long at a gain in any account. Doing so would be a §1259 constructive sale unless the closed-transaction exception is met.
- **Decision (adviser): straddles.** If the system will hold offsetting long and short positions in related securities (for example long a stock while short its sector ETF), ask whether the §1092 straddle rules defer the losses. See Gaps.

### Gaps
- **§1091(e) and short sales: not verified this session.** As the statute is commonly read, rules similar to §1091(a) apply to a loss on closing a short sale if, within 30 days before or after the closing, substantially identical stock is sold or another short sale of it is opened. Verify at [26 U.S.C. §1091](https://www.law.cornell.edu/uscode/text/26/1091) and in the short-sale paragraph of Pub. 550's wash-sale section.
- **§1092 straddles: not retrieved.** Pub. 550 (2025) lists a "Mixed straddles" heading, but the text was not seen. Two points still need checking:
  - losses are deferred up to the unrecognized gain in offsetting positions;
  - stock counts as part of a straddle only against an option or against "substantially similar or related property" (Reg. §1.246-5).
- **ETFs on the same index.** No authoritative source was found on when two ETFs that track the same index are "substantially identical".
- **Not retrieved this session; all need confirmation:**
  - the statement that net short-term gains are taxed at ordinary rates (IRS Topic 409);
  - the 3.8% net investment income tax;
  - state income tax;
  - quarterly estimated-tax duties;
  - qualified-dividend treatment. With holds of 5 days or less, dividends are unlikely to meet the holding period, and payments in lieu on margin shares that the broker has lent out are generally not qualified dividends.

---

## 2. Trader tax status and the §475(f) mark-to-market election: criteria, case law, automated trading, deadlines, effects, entities, and the 2025–2026 law changes

### Takeaway
**What TTS is.** TTS is a facts-and-circumstances status, not an election. It requires substantial, frequent, regular and continuous trading that aims at short-term price swings. Only a trader who has TTS can benefit from a §475(f) election.

**What the election does.** It makes gains and losses ordinary and switches off the wash-sale rule and the $3,000 loss cap, with no self-employment tax.

**The election is unforgiving:**
- An existing individual must make it by the original due date of the prior year's return. The 2026 deadline passed on 15 April 2026; for 2027 the deadline is 15 April 2027.
- A new entity has 75 days from its start.
- Late elections are generally refused; this is the point Poppe lost on.
- Since Rev. Proc. 2025-23, revoking within five years needs non-automatic IRS consent.

**Automated trading.** No IRS guidance or court case was found on whether trades placed by an algorithm the taxpayer built count as the taxpayer's own activity. Practitioners say they can, if the taxpayer designed the system and stays involved.

**The 2025 budget law (OBBBA).**
- It made the excess-business-loss cap permanent; the cap is $256k single / $512k joint for 2026, per secondary sources.
- It made permanent the ban on investors deducting investment expenses, which makes TTS more valuable for costs such as data feeds.
- It made §199A permanent, but trading income generally does not qualify.

### Cited Findings
#### What TTS is, and who can elect §475(f)
- TTS is a facts-and-circumstances determination, not an election, and the IRS can challenge it on audit. The §475(f) election is available only to taxpayers who already qualify for TTS. — [Beancount.io trader-tax guide](https://beancount.io/blog/2026/05/11/trader-tax-status-section-475f-mark-to-market-election-wash-sale-rule-3000-capital-loss-cap-day-traders-guide); [TSCPA: TTS and §475](https://tscpatax.com/articles/trader-tax-status-mark-to-market-election) [2+, secondary]
- There is no statutory objective test. Case law requires trading that is substantial, regular, frequent and continuous, and that seeks profit from short-term swings rather than long-term appreciation. — [GreenTraderTax: How to be eligible](https://greentradertax.com/how-to-be-eligible-for-substantial-tax-savings-as-a-trader/); [GreenTraderTax/Interactive Brokers webinar](https://www.interactivebrokers.com/webinars/2020-WB-3479_GreenTraderTax_HowToBeEligibleForSubstantialTaxSavingsAsTrader.pdf) [single-source: same author; secondary]
- No IRS form grants TTS and no court has set a minimum trade count. Courts weigh volume, frequency, continuity, holding periods, time spent and the intent to profit from short-term swings. Practitioners cite planning heuristics, which are not law:
  - about 60 trades a month, or 720 a year;
  - an average hold of 31 days or less;
  - some cite about 1,000 trades a year.
  - Sources: [GreenTraderTax: How to qualify](https://greentradertax.com/trader-tax-center/trader-tax-status/how-to-qualify/); [Prestige Tax CPA: How to qualify for TTS](https://www.prestigetaxcpa.com/wp-content/uploads/2022/02/How-to-Qualify-for-TTS.pdf) [2+, secondary]

#### Case law (from practitioner summaries; the opinions themselves were not retrieved)
- **Holsinger (2008):** trading on 110 days was "not frequent, continuous, or regular enough". Trade counts of 289 (2001) and 372 (2002) did not reach substantial trading activity. — [ProTraderTax: IRS court cases](https://www.protradertax.com/irs-court-cases/); [Prestige Tax CPA](https://www.prestigetaxcpa.com/wp-content/uploads/2022/02/How-to-Qualify-for-TTS.pdf) [secondary]
- **Chen (2004):** 323 trades were substantial but not continuous, and trader status was denied. — [GreenTraderTax/Interactive Brokers webinar](https://www.interactivebrokers.com/webinars/2020-WB-3479_GreenTraderTax_HowToBeEligibleForSubstantialTaxSavingsAsTrader.pdf) [single-source, secondary]
- **Assaderaghi (2014):** 535 trades, but the activity was too irregular and not continuous enough. The court weighed his full-time engineering job and weak evidence on holding periods. — [GreenTraderTax](https://greentradertax.com/how-to-be-eligible-for-substantial-tax-savings-as-a-trader/); [ProTraderTax](https://www.protradertax.com/irs-court-cases/) [secondary]
- **Endicott (2013):** the taxpayer was held to be an investor, not a trader, and accuracy-related penalties were sustained. — [Tax Notes, 29 Aug 2013](https://www.taxnotes.com/court-opinions-ustax-court/individual-income-taxation/tax-court-holds-individual-wasnt-trader-securities-penalties-sustained/2013/08/29/1ps68) [single-source]
  - Practitioners say the IRS argued that the average holding period must be 31 days or less. That is the IRS's argument as reported, not the holding. — [GreenTraderTax: How to qualify](https://greentradertax.com/trader-tax-center/trader-tax-status/how-to-qualify/) [secondary]
- **Poppe (2015):** about 60 trades a month (around 720 a year) were frequent, regular and continuous enough, so he was a trader. He still lost on §475:
  - he made no timely election;
  - the court held the substantial-compliance doctrine does not apply to §475(f);
  - he failed many Rev. Proc. 99-17 requirements.
  - Sources: [Forbes, 11 Nov 2015](https://www.forbes.com/sites/greatspeculations/2015/11/11/traders-find-mixed-in-poppe-tax-ruling/); [GreenTraderTax](https://greentradertax.com/how-to-be-eligible-for-substantial-tax-savings-as-a-trader/) [2+, secondary]

#### Automated trading built by the taxpayer
- A computerized trading service with little involvement from the trader generally does not qualify. If the trader is heavily involved in creating the system and hands only execution to the program, the IRS may count those trades. Examples of heavy involvement are writing the code or algorithms and setting the entry and exit signals. — [GreenTraderTax: How to qualify](https://greentradertax.com/trader-tax-center/trader-tax-status/how-to-qualify/) [single-source, secondary]
- Automated systems or trade-copying services may not qualify unless the trader is actively involved in developing the strategy and in execution. — [Anderson Advisors](https://andersonadvisors.com/blog/trader-tax-status/) [single-source, secondary; consistent with the above]

#### Election mechanics and deadlines
- **Existing taxpayers:** the election is due by the original due date (without extensions) of the return for the year before the election year. — [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [KAS CPAs](https://kascpas.com/blog/section-475-mark-to-market-trader-tax) [2+]
  - For tax year 2026 that date was 15 April 2026. — [KAS CPAs](https://kascpas.com/blog/section-475-mark-to-market-trader-tax) [single-source, secondary]
- **Late elections:** late §475(f) elections are generally not allowed, and the IRS has denied relief requests. — [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [Current Federal Tax Developments, 25 Jun 2023](https://www.currentfederaltaxdevelopments.com/blog/2023/6/25/irs-denies-request-by-a-taxpayer-to-make-a-late-475f-election) [2+]
- **New taxpayers** (no prior-year return required, for example a new entity): the election statement goes into the books and records within 2 months and 15 days of the first day of the first tax year, and a copy is attached to that year's return (Rev. Proc. 99-17 §5.03(2)). — [Tax Notes: Rev. Proc. 99-17](https://www.taxnotes.com/research/federal/irs-guidance/revenue-procedures/irs-outlines-procedures-for-electing-mark-to-market-accounting-method/dldc); [Morkel Financial](https://morkelfinancial.com/blog/missed-mark-to-market-election-deadline); [LegalClarity](https://legalclarity.org/section-475-election-statement-example-and-requirements/) [2+, secondary on the primary]
- **PLR 201623005:** a taxpayer that became a corporation overlooked the need for new §475(e)/(f) elections within 75 days. It had to request late-election relief under Treas. Reg. §301.9100-3. — [IRS PLR 201623005](https://irs.gov/pub/irs-wd/201623005.pdf) [single-source, primary]
- **Revocation:**
  - The taxpayer files a notification statement under Rev. Proc. 2025-23 §24.02, plus Form 3115 to change back to a realization method.
  - Revoking within five years of electing, or re-electing within five years of revoking, needs Form 3115 under the non-automatic procedures (Rev. Proc. 2015-13), which carry a user fee.
  - Sources: [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [GreenTraderTax: §475 revocation locked for 5 years](https://greentradertax.com/new-irs-rules-section-475-mtm-revocation-now-locked-for-5-years-planning-options-for-traders/) [2+]

#### Effects of TTS and §475(f)
- With the election, the wash-sale rules and the capital-loss limits do not apply. The Form 4797 instructions say the wash-sale rule does not apply to securities held in connection with the trading business. — [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [IRS Form 4797 instructions](https://www.irs.gov/pub/irs-pdf/i4797.pdf) [2+, IRS]
- Results become ordinary income or loss, and long-term capital-gain rates are given up. — [Beancount.io trader-tax guide](https://beancount.io/blog/2026/05/11/trader-tax-status-section-475f-mark-to-market-election-wash-sale-rule-3000-capital-loss-cap-day-traders-guide) [single-source, secondary]
- A trader's gains are not subject to self-employment tax. — [IRS Pub. 550](https://www.irs.gov/publications/p550) [single-source, primary]
  - Consequences cited: trading profits cannot fund a SEP or solo 401(k), and trading income generally does not qualify for the §199A (QBI) deduction. — [Beancount.io trader-tax guide](https://beancount.io/blog/2026/05/11/trader-tax-status-section-475f-mark-to-market-election-wash-sale-rule-3000-capital-loss-cap-day-traders-guide) [single-source, secondary]
- **Expenses:**
  - TTS traders may deduct the ordinary and necessary expenses of the trading business, such as platforms, data services and software.
  - Investors cannot. OBBBA made permanent the §67(g) bar on miscellaneous itemized deductions, which covers investment advisory fees, tax-preparation fees and the like.
  - Sources: [GreenTraderTax: trading business expenses](https://greentradertax.com/trader-tax-center/trader-tax-status/trading-business-expenses/); [Cozen O'Connor](https://www.cozen.com/news-resources/publications/2025/changes-to-itemized-deductions-in-the-obbba); [Barnes Dennig](https://www.barnesdennig.com/obbba-reshapes-itemized-deductions/) [2+]

#### 2025–2026 law changes
- **Excess-business-loss limit.** OBBBA (enacted July 2025) made the §461(l) limit permanent; it had been due to expire after 2028. Any disallowed excess becomes a net operating loss carried forward. — [Covington, July 2025](https://www.cov.com/en/news-and-insights/insights/2025/07/key-provisions-of-the-one-big-beautiful-bill-act); [Godfrey & Kahn](https://www.gklaw.com/Insights/Key-Business-Tax-Changes-in-the-One-Big-Beautiful-Bill-Act.htm); [Gould + Ratner](https://www.gouldratner.com/publication/your-guide-to-the-tax-implications-of-the-one-big-beautiful-bill); [Instead](https://webflow.instead.com/resources/blog/excess-business-loss-limitation-becomes-permanent) [2+]
- **2026 threshold.** $256,000 single / $512,000 joint, per Rev. Proc. 2025-32 as quoted by secondary sources. The 2025 threshold was $313,000 / $626,000.
  - Sources: [Hiltzik CPA](https://hiltzikcpa.com/excess-business-loss-limitation-2026/); [Morkel Financial](https://morkelfinancial.com/blog/excess-business-loss-limitation-2026); [IRS Instructions for Form 461 (2025)](https://www.irs.gov/instructions/i461)
  - Strength: [2+ secondary for 2026; IRS primary for 2025] [conflict: a minority of sources give older or projected figures]
- **§199A.** OBBBA made §199A permanent. — [Covington](https://www.cov.com/en/news-and-insights/insights/2025/07/key-provisions-of-the-one-big-beautiful-bill-act); [Kitces](https://www.kitces.com/blog/obbba-one-big-beautiful-bill-act-tax-planning-salt-cap-senior-deduction-qbi-deduction-tax-cut-and-jobs-act-tcja-amt-trump-accounts/); [Steven J. Cashiola CPA](https://www.stevenjcpa.com/insights/section-199a-obbba-qualified-business-income) [2+] [conflict: one source says the rate rose to 23%; others keep 20%, so treat 23% as likely wrong]
- **Itemized-deduction limit.** A new limit applies to top-bracket itemizers: itemized deductions are reduced by 2/37 of the lesser of the deductions or the taxable income above the start of the 37% bracket. — [Cozen O'Connor](https://www.cozen.com/news-resources/publications/2025/changes-to-itemized-deductions-in-the-obbba); [Barnes Dennig](https://www.barnesdennig.com/obbba-reshapes-itemized-deductions/) [secondary]
- **Revocation lock.** Rev. Proc. 2025-23 (2025) created the five-year lock on revoking §475(f) through the automatic procedures (see "Election mechanics" above). — [IRS Topic 429](https://www.irs.gov/taxtopics/tc429); [GreenTraderTax](https://greentradertax.com/new-irs-rules-section-475-mtm-revocation-now-locked-for-5-years-planning-options-for-traders/) [2+]

#### Entity options
- A newly formed entity is a "new taxpayer" and can make the §475(f) election internally within 75 days of its start. Missing this when an entity is formed or converted is a known trap. — [IRS PLR 201623005](https://irs.gov/pub/irs-wd/201623005.pdf); [Tax Notes: Rev. Proc. 99-17](https://www.taxnotes.com/research/federal/irs-guidance/revenue-procedures/irs-outlines-procedures-for-electing-mark-to-market-accounting-method/dldc) [2+]

### Inferences
- **How the system compares with the case law.** About 25 round trips a week is roughly 1,300 round trips, or about 2,600 executions, a year. Holds run from seconds to 5 days, and trading happens every week. That is far above the roughly 720 trades a year found sufficient in Poppe, and far more regular than in Holsinger, Chen or Assaderaghi. The weak points are elsewhere:
  - whether trades placed by the owner's own algorithm count as the owner's activity (no authority was found);
  - the time-devoted and livelihood factors, if the owner has a full-time job, as in Assaderaghi.
  - Development logs, monitoring hours and records of parameter changes would be the evidence (adviser).
- **Paper trading does not count.** Paper trades are not trades, so TTS can begin only when G3 starts real-money trading. A start part-way through a year limits what can be claimed for that year.
- **Timing decision for §475(f).**
  - An existing individual can no longer elect §475(f) for 2026.
  - For 2027 the statement is due by 15 April 2027, attached to the 2026 return or an extension request. That is before the owner knows whether 2027 trading will qualify.
  - The election has no effect without TTS, and since Rev. Proc. 2025-23 it is costly to undo within five years.
  - The alternative is a new entity that elects within 75 days of formation. That entity must then qualify for TTS on its own facts.
- **What §475(f) would buy this system:**
  - It removes wash-sale tracking. This is the biggest operational gain, given how often the system re-trades the same symbols.
  - It turns losses in a bad first year into ordinary losses that can offset other income, up to the §461(l) cap ($256k / $512k in 2026). Any excess carries forward as a net operating loss.
  - It gives up only long-term rates, which a system holding positions for 5 days or less never earns.
- **Expenses.** The Alpaca SIP data plan ($99 a month, see Section 4), hosting and software are deductible only with TTS. Investor expenses are permanently non-deductible after OBBBA.
- **Entity choice (adviser).** Weigh the cost of a separate return and any state fees against possible health-insurance and retirement-plan deductions through an S-corporation salary, and mind the 75-day election clock.

### Gaps
- **Automated trading.** No IRS ruling, regulation or Tax Court case was found on whether trades generated by an automated system the taxpayer built count toward TTS. A possible analogy is Mayer v. Commissioner (1994), on trades made by discretionary managers, which was not verified this session.
- **Topic 429 text not seen in the extracts:**
  - the IRS's own list of factors (typical holding periods; frequency and dollar amount of trades; pursuit as a livelihood; time devoted);
  - the rule that open positions are treated as sold at year-end under §475;
  - the requirement to identify investment positions separately.
- **Form 3115 for a new taxpayer** adopting §475 from inception: sources conflict. One says no Form 3115 is needed; another describes a duplicate filed with the IRS National Office.
- **User fee for a non-automatic revocation:** secondary figures conflict ($13,225 vs $12,600). Check the current annual user-fee revenue procedure.
- **IRS approval step.** One secondary source claims the IRS must acknowledge TTS in writing before a §475(f) election. No such IRS step appeared in the IRS material found, so treat the claim as unsupported.
- **Not found this session:**
  - trade-offs between S-corporations and partnerships for trading entities (health insurance, retirement plans, reasonable salary, state taxes);
  - whether electing traders are exempt from §1092 and §263(g) (via §475(d)/(f)(1)(D));
  - whether capital-loss carryovers from before the election can offset §475 ordinary income;
  - the net investment income tax on trading income.
- **Case citations to verify.** These memo numbers are from memory: Endicott T.C. Memo 2013-199, Poppe T.C. Memo 2015-205, Assaderaghi T.C. Memo 2014-33, Holsinger T.C. Memo 2008-191, Chen T.C. Memo 2004-132.
- **Other OBBBA changes.** No source said OBBBA changed §§475, 1091, 1233, 1259 or 1092. None surfaced, but this was not checked exhaustively.

---

## 3. Non-US resident (general): US tax on gains, dividends and substitute payments; home-country taxation; questions for a local adviser

### Takeaway
**US tax on gains.** The US generally does not tax a nonresident alien's gains from trading US stocks for their own account. The exception is physical presence in the US for 183 days or more in the year; then 30%, or a lower treaty rate, applies to net US-source gains.

**US tax on dividends.** Dividends on long positions, and dividend-equivalent or substitute payments, bear 30% withholding unless a treaty rate is claimed on Form W-8BEN.

**Home-country tax is the real question.** Some countries treat frequent or intraday trading as business or speculative income: India explicitly, and Canada and Australia on the facts.

**Other risks.**
- US stocks are US-situs assets for estate tax, with only a $60,000 exemption for non-domiciliaries.
- Whether Alpaca lets a given non-US resident trade on margin and short was not confirmed (see Section 4).

### Cited Findings
- **§871(a)(2).** A nonresident alien present in the US for 183 days or more in the year pays 30% on the excess of US-source capital gains over US-source capital losses. A treaty can lower the rate. — [26 U.S.C. §871 (Cornell LII)](https://www.law.cornell.edu/uscode/text/26/871); [The Tax Adviser, Apr 2017](https://www.thetaxadviser.com/issues/2017/apr/planning-nonresident-entering-us-tax-system/); [Taxes for Expats](https://www.taxesforexpats.com/articles/foreign-nationals/do-non-residents-pay-capital-gains-tax-us.html) [2+]
- **How days are counted.** The 183-day count for this rule is physical presence. It is different from the substantial-presence test used to decide US residency. — [Our Tax Partner](https://ourtaxpartner.com/nonresident-capital-gains-183-day-rule/); [Taxes for Expats](https://www.taxesforexpats.com/articles/foreign-nationals/do-non-residents-pay-capital-gains-tax-us.html) [2+, secondary]
- **Below the threshold.** If the gain is not effectively connected with a US trade or business, gains on portfolio stocks are generally not taxable in the US. — [Taxes for Expats](https://www.taxesforexpats.com/articles/foreign-nationals/do-non-residents-pay-capital-gains-tax-us.html); [Our Tax Partner](https://ourtaxpartner.com/nonresident-capital-gains-183-day-rule/) [2+, secondary]
- **Dividends.** US dividends bear 30% withholding unless a treaty reduces it. Withholding documentation (W-8BEN) lets the payer apply the treaty rate. — [IRS Pub. 515 (2026)](https://www.irs.gov/publications/p515); [IG: US stocks and IRS tax forms](https://www.ig.com/en/us-stocks-irs-tax-forms); [IRS Instructions for Form W-8BEN](https://www.irs.gov/pub/irs-pdf/iw8ben.pdf) [2+]
- **Substitute dividends and dividend equivalents (§871(m)).** Substitute dividends paid under securities-lending or sale-repurchase transactions, and dividend equivalents, are treated as US-source dividends, with 30% withholding unless a treaty reduces it. — [Federal Register, 18 Sep 2015 (final regulations)](https://www.federalregister.gov/documents/2015/09/18/2015-21759/dividend-equivalents-from-sources-within-the-united-states); [Cummings Law](https://www.cummings.law/tax-consequences-of-dividend-equivalent-payments-under-irc-%C2%A7-871m/); [Forvis Mazars](https://www.forvismazars.us/forsights/2022/06/understanding-section-871-m-impacts-on-schedule-k-2) [2+]
- **Reporting codes.** Pub. 515 has income codes for substitute dividends that are dividend equivalents (34 or 53) and for §871(m) combined transactions (56). — [IRS Pub. 515 (2026)](https://www.irs.gov/publications/p515) [single-source, primary]
- **US estate tax:**
  - Shares of US companies are US-situs property for a non-domiciled non-citizen, even if held through a non-US broker.
  - The exemption is $60,000; it has not been indexed since 1988, and rates reach 40%.
  - An estate must file once US-situs assets exceed $60,000, even if a treaty removes the tax.
  - Accounts can be frozen until the IRS issues a transfer certificate.
  - Only a limited number of countries have estate-tax treaties with the US.
  - Sources: [Bloomberg Law](https://news.bloomberglaw.com/tax-insights-and-commentary/foreign-residents-must-consider-us-estate-tax-when-they-invest); [Private.law wiki](https://wiki.private.law/en/us-estate-tax); [myStockOptions](https://www.mystockoptions.com/content/tax-nonresident-alien-company-stock-upon-death-would-heirs-outside-US-owe-estate-tax) [2+, secondary]
- **Home-country examples:**
  - *India.* Intraday equity trades are generally speculative business income under s.43(5) of the Income Tax Act 1961. Speculative losses offset only speculative gains and carry forward for four years. Delivery-based trades and futures-and-options trades are classified differently. — [Bajaj AMC](https://www.bajajamc.com/knowledge-centre/tax-implication-on-intraday-trading); [ClearTax](https://cleartax.in/s/income-tax-on-intraday-trading); [TaxGuru](https://taxguru.in/income-tax/business-income-capital-gains-tax-treatment-share-trading.html) [2+, secondary]
  - *Canada.* If day trading is the primary activity, the CRA may treat it as business income taxed at full rates rather than as capital gains. — [DayTrading.com](https://www.daytrading.com/taxes); [DayTraderBusiness](https://daytraderbusiness.com/regulations/taxation/tax-implications-of-day-trading-in-different-countries/) [single-source, secondary; which of the two pages makes this point was not resolved]
  - *Australia.* A share-trading business's profits are ordinary income, and the ATO looks at whether the person carries on "business-like activities". — [DayTrading.com](https://www.daytrading.com/taxes); [DayTraderBusiness](https://daytraderbusiness.com/regulations/taxation/tax-implications-of-day-trading-in-different-countries/) [secondary]

### Inferences
- **US cost for a non-US owner.** It is mostly withholding on dividends from longs held over an ex-dividend date. With holds of 5 days or less that is uncommon, and an ex-dividend filter can avoid it.
- **What drops away and what decides.** The TTS, §475 and wash-sale questions are US-person issues and largely do not apply. Two questions decide the outcome:
  - how the home country classifies the activity;
  - whether Alpaca will open a margin account with short selling for that country.
- **US residence.** Staying under 183 days of US presence a year keeps §871(a)(2)'s 30% tax off the gains. Becoming a US resident switches the owner to the rules in Sections 1 and 2 (adviser).
- **Estate-tax exposure** starts above $60,000 of US-situs assets, which includes the trading account's positions. Even the G3 starting capital (10% of intended) passes that if the intended capital is above about $600k. Check whether a treaty applies (adviser).
- **Questions to ask a local adviser:**
  1. Will automated, high-turnover trading of US stocks be taxed as capital gains, as business or trading income, or as speculative income? Which tests decide: frequency, holding period, automation, leverage, organisation, time spent?
  2. What rates apply, and are social-security contributions due? Can losses offset other income or be carried forward, and with what limits?
  3. Is there a tax treaty with the US? What dividend withholding rate does it give, how is it claimed on W-8BEN, and how is US withholding credited at home?
  4. How are short sales treated, and are the in-lieu dividend payments made on shorts deductible?
  5. Are currency gains and losses on USD balances and conversions taxable, and which exchange rates must be used?
  6. What foreign-account or foreign-asset reporting applies to a US brokerage account?
  7. Is there a home-country equivalent of the wash-sale ("bed-and-breakfast") rule?
  8. Would a home-country company be better, and would it change US withholding or create a US trade or business?
  9. What is the US estate-tax exposure, does a treaty apply, and how should succession be planned?
  10. What record-keeping format does the tax authority require (trade by trade, in local currency)?
  11. How many days can be spent in the US without triggering US tax or residency?

### Gaps
- **§864(b)(2) trading safe harbor: not retrieved.** It provides that trading stocks for one's own account through a US broker is not a US trade or business (dealers are excepted). Verify the text and its exceptions.
- **Alpaca's non-US eligibility** for margin and short selling, by country, was not confirmed (see Section 4).
- **Forms:** how long a W-8BEN stays valid and when it must be renewed, and Alpaca's Form 1042-S reporting, were not retrieved.
- **§871(m) transition relief:** its current status was not checked; the source found is from 2022.
- **Official home-country sources** (CRA, ATO, HMRC, German BMF) were not retrieved. For Germany, secondary sources conflict on whether frequent trading becomes business income. For the UK, nothing usable was found.

---

## 4. Alpaca account rules, current as of October 2026

### Takeaway
All three earlier notes hold, with qualifiers:
- **Intraday margin replaced PDT.** Alpaca moved from the pattern-day-trader rule to FINRA's intraday-margin framework on 4 June 2026, the rule's effective date.
- **$2,000 to short.** Margin and any short sale still need at least $2,000 of equity, under both FINRA's rule and Alpaca's policy.
- **$0 on easy-to-borrow.** Easy-to-borrow shorts carry $0 locate and borrow fees for Trading API users.

Other current terms:
- Hard-to-borrow shorts need paid locates in 100-share lots and incur a daily borrow fee.
- Fractional shares cannot be shorted.
- Protection is SIPC plus Lloyd's excess cover of $75M in securities and $75M in cash per customer.
- FINRA fined Alpaca $300,000 in March 2026 for late trade reporting, after a 2024 SEC recordkeeping penalty.
- Live decisions need the $99-a-month SIP data plan; the free feed is IEX-only.

Still unresolved:
- Alpaca's own pages disagree on the deadline to meet an intraday margin call (2 or 5 business days).
- Margin and short eligibility for non-US residents is unconfirmed.

### Cited Findings
#### Verification of the three earlier claims
1. **"Intraday margin framework instead of PDT from 2026-06-04": confirmed.**
   - The SEC approved FINRA's amendments to Rule 4210 (SR-FINRA-2025-017) on 14 April 2026. — [FINRA weekly update, 15 Apr 2026](https://www.finra.org/compliance-tools/weekly-archive/04152026); [WilmerHale alert, 23 Apr 2026](https://www.wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard) [2+]
   - FINRA Regulatory Notice 26-10 (20 April 2026) set the effective date at 4 June 2026, 45 days after publication. Member firms may phase in over 18 months, to 20 October 2027. — [FINRA Regulatory Notice 26-10](https://www.finra.org/rules-guidance/notices/26-10); [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard); [Wikipedia: Pattern day trader](https://en.wikipedia.org/wiki/Pattern_day_trader) [2+]
   - Alpaca says it implemented its new Intraday Margin Framework on 4 June 2026 and lifted restrictions based on PDT status. — [Alpaca blog](https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/); [Alpaca on X: "The day has come!"](https://x.com/AlpacaHQ/status/2062566639325917446); [Alpaca on X: announcement](https://x.com/AlpacaHQ/status/2049111388581191772); [Alpaca community forum](https://forum.alpaca.markets/t/pdt-change-approved-when-will-changes-take-effect/18701) [issuer-only]
     - The blog post's displayed date is internally inconsistent, according to the search extract.
   - Alpaca's customer agreement lets Alpaca phase the change in, or keep applying the former day-trading rules, at its discretion, and apply stricter house requirements. — [Alpaca Customer Agreement](https://files.alpaca.markets/disclosures/library/AcctAppMarginAndCustAgmt.pdf) [issuer-only]
2. **"$2,000 of equity to short": confirmed.**
   - FINRA's interpretation /021 of Rule 4210 says every short sale is subject to the $2,000 minimum equity requirement regardless of the amount involved, apart from narrow exceptions. — [FINRA Interpretations of Rule 4210](https://www.finra.org/rules-guidance/guidance/interps-4210) [primary]
   - Alpaca says margin trading and short selling require $2,000 or more of equity; below that an account has 1x buying power and cannot short. — [Alpaca docs: Margin and Short Selling](https://docs.alpaca.markets/us/docs/margin-and-short-selling); [Alpaca support: What determines the margin for my account?](https://alpaca.markets/support/determine-margin-account)
   - A third party notes that the separate $2,000 margin minimum survived the PDT repeal. — [StockTitan](https://www.stocktitan.net/articles/pattern-day-trader-rule-eliminated-2026)
   - Overall strength: [2+]
3. **"$0 borrow fees on easy-to-borrow names": confirmed, with qualifiers.**
   - Alpaca states "$0 locate and borrow fees on all ETB shares for Trading API users", with 5,000+ easy-to-borrow (ETB) securities approved for zero-fee locates. — [Alpaca docs: Margin and Short Selling](https://docs.alpaca.markets/us/docs/margin-and-short-selling); [Alpaca support: Short selling fees](https://alpaca.markets/support/short-selling-fees) [issuer-only]
   - Hard-to-borrow names are not free (see below).
   - The wording is limited to Trading API users, so Broker API arrangements may differ.

#### The FINRA intraday margin rule
- **What was removed:** the pattern-day-trader designation, the four-day-trades-in-five-days count, the $25,000 minimum equity and day-trading buying power.
- **What replaced it:** intraday margin standards in Rule 4210(a)(17)–(19) and (d)(2). Maintenance margin under Rule 4210(c) is unchanged.
- Sources: [FINRA Regulatory Notice 26-10](https://www.finra.org/rules-guidance/notices/26-10); [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard); [ACA Group](https://www.acaglobal.com/industry-insights/finra-ends-the-pattern-day-trader-rule/); [King & Spalding](https://www.kslaw.com/news-and-insights/finra-adopts-sweeping-changes-to-margin-requirements-for-day-trading) [2+]
- **How the deficit is measured.** The intraday margin level (IML) is the cash the customer could withdraw, or would have to deposit, and still meet maintenance margin.
  - Firms check for a deficit on any day with an IML-reducing transaction, such as a short sale or a purchase other than one that covers a short.
  - The deficit is the most negative IML reached after such a transaction.
  - Sources: [FINRA Regulatory Notice 26-10](https://www.finra.org/rules-guidance/notices/26-10); [King & Spalding](https://www.kslaw.com/news-and-insights/finra-adopts-sweeping-changes-to-margin-requirements-for-day-trading) [2+]
- **Curing a deficit:**
  - It must be met "as promptly as possible".
  - If it is unmet by the fifth business day, the firm deducts it from net capital from the sixth business day, for up to ten business days.
  - The deficit lapses after the close of the fifteenth business day.
  - A customer who fails to meet deficits as a practice faces a 90-day freeze on new credit and new short positions; closing trades are still allowed.
  - Sources: [King & Spalding](https://www.kslaw.com/news-and-insights/finra-adopts-sweeping-changes-to-margin-requirements-for-day-trading); [SEC filing 34-105226 on SR-FINRA-2025-017](https://www.sec.gov/files/rules/sro/finra/2026/34-105226.pdf); [Alpaca Customer Agreement](https://files.alpaca.markets/disclosures/library/AcctAppMarginAndCustAgmt.pdf) [2+, secondary; the final rule text was not seen]
- **Which accounts it covers:** all margin accounts except good-faith and portfolio-margin accounts. — [QuantInsti](https://www.quantinsti.com/articles/finra-pdt-rule-removal-2026/) [single-source, secondary]
- **Still current:** law-firm guidance from September 2026 still describes the regime as current. — [WSGR alert, 8 Sep 2026](https://www.wsgr.com/print/v2/content/49076200/FINRA-Adopts-New-Intraday-Margin-Requirements.pdf) [title-level only]

#### How Alpaca applies it
- **Alpaca's mechanics:**
  - Pre-trade checks reject orders that would create or increase an intraday margin deficit.
  - Mark-to-market losses alone do not create a deficit.
  - A call is generally not issued if the unmet deficit is below the lesser of $1,000 or 5% of equity.
  - Intraday profit and loss feeds into available margin during the day, and intraday margin calls replace day-trade calls.
  - For non-leverage (1x) margin accounts, the "4-trade limit" and the PDT designation are gone.
  - Sources: [Alpaca: The Intraday Margin Rule](https://docs.alpaca.markets/us/docs/the-intraday-margin-rule); [Alpaca: Understanding FINRA's new intraday margin rule](https://docs.alpaca.markets/us/docs/understanding-finras-new-intraday-margin-rule-and-the-end-of-pdt); [Alpaca: Intraday Margin Rule for Non-Leverage Margin Accounts](https://docs.alpaca.markets/us/docs/intraday-margin-rule-for-non-leverage-margin-accounts); [Alpaca blog](https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/) [issuer-only]
- **Conflict on the deadline.** One Alpaca page says an intraday margin call must be met within two business days; Alpaca's Broker API material says five. Both say the account may be restricted for up to 90 calendar days if the customer makes a practice of not meeting calls. — [Alpaca: The Intraday Margin Rule](https://docs.alpaca.markets/us/docs/the-intraday-margin-rule); [Alpaca: Understanding FINRA's new intraday margin rule](https://docs.alpaca.markets/us/docs/understanding-finras-new-intraday-margin-rule-and-the-end-of-pdt) [conflict, issuer-only]

#### Margin accounts, the $2,000 floor and margin interest
- All Alpaca accounts are opened as margin accounts. — [Alpaca docs: Trading account](https://docs.alpaca.markets/us/docs/account-plans) [single-source]
- **FINRA:** under interpretation /022, if equity falls below $2,000 because of a market decline and no new commitments are made, no deposit or liquidation is required. — [FINRA Interpretations of Rule 4210](https://www.finra.org/rules-guidance/guidance/interps-4210) [primary]
- **Alpaca (unofficial):** a community reply says the status is dynamic, so an account under $2,000 reverts to 1x and cannot open new shorts. It does not say what happens to open shorts. — [Alpaca community forum](https://forum.alpaca.markets/t/how-to-apply-for-margin-and-pdt-in-alpaca-trading-api-account/14361) [single-source, unofficial]
- **Margin interest.** Alpaca's fee schedule lists a default margin rate of 6.25%. BrokerChooser cites a flat 6.5%, or 5% for the Elite tier. — [Alpaca Brokerage Fee Schedule](https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf); [BrokerChooser review 2026](https://brokerchooser.com/broker-reviews/alpaca-trading-review) [conflict]

#### Short-selling mechanics
- **Hard-to-borrow (HTB) shorts:**
  - They are supported, with locates requested through the API; assets carry a `borrow_status` field.
  - They are restricted to eligible margin accounts and need an approved locate before the order is submitted.
  - Locates come in round lots of 100 shares, cannot be reused, and their fees are non-refundable.
  - The daily HTB fee is the position's market value times the HTB rate divided by 360, charged on the nearest 100-share round lot.
  - Sources: [Alpaca blog: HTB trading with API locates](https://alpaca.markets/blog/htb-trading-api-locates/); [Alpaca docs: Margin and Short Selling](https://docs.alpaca.markets/us/docs/margin-and-short-selling) [issuer-only; the launch post is undated]
- **HTB rates.** No current HTB rate table was found. A Scribd copy of an older fee schedule lists rates of 3% (S&P 500) and 4% (other ETB). It is unverified and probably superseded. — [Scribd copy of fee schedule](https://www.scribd.com/document/938779036/Brok-Fee-Sched) [single-source, dated]
- **Daily status changes:**
  - Borrow status changes daily.
  - Open short orders in a name that turns from ETB to HTB overnight are cancelled before the open.
  - Alpaca does not force-close a short that turns HTB unless the lender recalls the shares.
  - An older support page said HTB was not supported; it has been superseded.
  - Sources: [Alpaca docs: Margin and Short Selling](https://docs.alpaca.markets/us/docs/margin-and-short-selling); [Alpaca support: Short selling fees](https://alpaca.markets/support/short-selling-fees) [issuer-only]
- **Fractional shares:**
  - Fractional trading is long-only: "short selling fractional shares is not supported".
  - Fractional orders are limited to market, limit, stop and stop-limit orders with time-in-force DAY.
  - Not every asset is fractionable.
  - Sources: [Alpaca support: What is fractional trading](https://alpaca.markets/support/what-is-fractional-trading); [Alpaca docs: Fractional Trading](https://docs.alpaca.markets/us/docs/fractional-trading); [Alpaca forum: shorting fractional shares](https://forum.alpaca.markets/t/shorting-fractional-shares/11668) [issuer-only; consistent across versions]

#### Account minimums and non-US residents
- **Non-US residents:**
  - Alpaca supports live accounts for many non-US residents, depending on country.
  - The earlier $30,000 minimum for non-US applicants was lifted, and accounts can be funded with as little as $1.
  - KYC requires a tax ID from the country of residence, a photo ID with address, and a selfie.
  - Sources: [Alpaca support: Who can apply](https://alpaca.markets/support/requirements-alpaca-brokerage-account); [Alpaca Learn: live account for non-US residents](https://alpaca.markets/learn/live-trading-account-non-us) [issuer-only; dated, about 5 years old]
- **Conflicting reviews.** Some third-party reviews say Alpaca Trading serves only US residents and runs an international beta for business clients. — [BrokerChooser](https://brokerchooser.com/broker-reviews/alpaca-trading-review); [AlgoTrading101](https://algotrading101.com/learn/alpaca-trading-review/) [conflict; older and less reliable]
- **No non-US restriction found.** No Alpaca statement restricting margin or short selling for non-US accounts was found; the $2,000 rule is stated for all accounts. — [Alpaca support: What determines the margin for my account?](https://alpaca.markets/support/determine-margin-account) [single-source; absence of evidence only]

#### Custody protection
- **SIPC** protects up to $500,000, including $250,000 for cash claims. — [Alpaca support: Is my account insured?](https://alpaca.markets/support/is-my-account-insured-what-is-sipc); [BrokerChooser: investor protection](https://brokerchooser.com/broker-reviews/alpaca-trading-review/alpaca-trading-investor-protection-availability) [2+, secondary; sipc.org not retrieved]
- **Excess SIPC cover.** Alpaca Securities LLC (dba Alpaca Clearing) bought a Lloyd's of London policy that pays once SIPC limits are exhausted.
  - Current limits: up to $75M in securities and $75M in cash per customer, with a $250M aggregate.
  - Earlier limits: $30M in securities, $1M in cash, $150M aggregate. Some 2026 reviews still show these.
  - The expansion appears to date from about February 2026.
  - Sources: [Alpaca support](https://alpaca.markets/support/is-my-account-insured-what-is-sipc); [Alpaca blog: Alpaca Clearing expands excess SIPC](https://alpaca.markets/blog/alpaca-clearing-expands-excess-sipc-coverage-strengthening-commitment-towards-enhanced-protection/); [Alpaca blog: introduces excess SIPC](https://alpaca.markets/blog/alpaca-introduces-excess-sipc-coverage-bolstering-commitment-towards-enhanced-protection/); [Crowdfund Insider, Feb 2026](https://www.crowdfundinsider.com/2026/02/260793-alpaca-markets-bolsters-offerings-with-fixed-income-expansion-and-enhanced-investor-protections/) [issuer-only for the figures; the February 2026 timing is title-level from a third party]

#### Regulatory history (BrokerCheck firm report; CRD 288202 per the report URL)
- **FINRA settlement, March 2026.** Letter of Acceptance, Waiver and Consent (AWC) No. 2021072094901, resolved 17 March 2026: censure and a $300,000 fine, paid in full on 30 March 2026. — [FINRA BrokerCheck report](https://files.brokercheck.finra.org/firm/firm_288202.pdf); [FX News Group](https://fxnewsgroup.com/forex-news/regulatory/finra-imposes-300k-fine-on-alpaca-securities-for-alleged-trade-reporting-deficiencies/) [2+]
  - The conduct: about 1.87 million transactions not reported on time between April 2021 and June 2025, plus supervisory failures (FINRA Rules 6380A, 3110 and 2010). — [FX News Group](https://fxnewsgroup.com/forex-news/regulatory/finra-imposes-300k-fine-on-alpaca-securities-for-alleged-trade-reporting-deficiencies/) [single-source]
- **SEC order, September 2024.** On 24 September 2024 the SEC imposed a $400,000 civil penalty for recordkeeping violations (Exchange Act §17(a) and Rule 17a-4). — [SEC press release 2024-144](https://www.sec.gov/newsroom/press-releases/2024-144); [FINRA BrokerCheck report](https://files.brokercheck.finra.org/firm/firm_288202.pdf) [2+]
- **Statutory disqualification, March 2025.** FINRA's notice SD-2436 (6 March 2025) says the SEC order made the firm subject to statutory disqualification. The firm was not expelled or suspended, no limits were placed on its securities activities, and FINRA kept it as a member. — [FINRA SD-2436](https://www.finra.org/sites/default/files/2025-03/SD-2436-Alpaca-03-06-2025.pdf) [single-source, primary]

#### Market data
- **Free plan** (formerly "Basic"):
  - Real-time data from IEX only.
  - 30 symbols per websocket and 200 historical API calls a minute.
  - The latest 15 minutes of SIP (consolidated tape) data cannot be queried. A `delayed_sip` feed gives SIP quotes 15 minutes late.
  - Sources: [Alpaca docs: About Market Data API](https://docs.alpaca.markets/us/docs/about-market-data-api); [Alpaca docs (older version)](https://docs.alpaca.markets/docs/about-market-data-api); [Alpaca community forum](https://forum.alpaca.markets/t/alcapa-current-quote-price-is-way-off-from-market-price/18063) [issuer-only]
- **Algo Trader Plus, $99 a month:**
  - Real-time data from all US exchanges (SIP) plus OPRA options data.
  - Unlimited symbols and 10,000 historical calls a minute.
  - Broker API partners have a separate Broker Professional plan at $99 per month per device.
  - Sources: [Alpaca docs: About Market Data API](https://docs.alpaca.markets/us/docs/about-market-data-api); [APIs.io: Alpaca plans and pricing](https://apis.io/plans/alpaca-markets/alpaca-markets-plans-pricing/) [2+]
- **IEX coverage.** A forum reply says IEX carries only about 2–3% of trades, and Alpaca staff describe the free feed as mainly for testing, not for live decisions. — [Alpaca community forum](https://forum.alpaca.markets/t/alcapa-current-quote-price-is-way-off-from-market-price/18063) [single-source]

### Inferences
- **A G3 start at exactly $2,000 is a knife edge.**
  - Any net loss takes equity below $2,000, which stops new shorts and so halts the long/short strategy until cash is added.
  - FINRA /022 means open positions need not be liquidated after a market decline, but Alpaca's handling of open shorts is unconfirmed.
  - Decision: fund G3 with a buffer, for example $2,000 / (1 − the drawdown at which G3 halts).
  - Decision: write an explicit halt-or-top-up rule for when equity falls below $2,000.
- **Intraday margin.** With gross exposure at or below 100% and no leverage, maintenance requirements stay a fraction of equity, so the IML should stay positive in normal conditions and intraday margin calls should be rare. The system should still:
  - handle pre-trade rejections caused by an intraday margin deficit;
  - never rely on more than 1x intraday buying power;
  - alert on any intraday margin call. A 90-day freeze on new shorts would stop half the strategy.
- **Short only easy-to-borrow names.**
  - Refresh the `shortable` and `easy_to_borrow` flags every morning.
  - Expect open short orders to be cancelled overnight when a name turns hard to borrow.
  - At small capital, HTB names are uneconomic: locates come in 100-share lots with non-refundable fees.
- **Order sizing.** Size shorts in whole shares. Fractional longs only allow DAY orders of a few types, so whole-share sizing on both sides may be simpler and keeps paper and live results comparable.
- **Market data.** Buy the SIP data plan ($99 a month) before real money.
  - Decisions made on IEX-only quotes would differ from paper results built on fuller data.
  - Count the $99 a month in the G3 profitability test.
- **Counterparty risk.** SIPC plus Alpaca's excess cover far exceeds the planned capital. The disciplinary history concerns trade reporting and recordkeeping; no customer-asset findings surfaced in these searches. Re-check BrokerCheck before G3 and periodically.
- **Non-US owner.** Before G3, get written confirmation from Alpaca that it will open a margin account with short selling for the owner's country of residence. The long/short design depends on it.

### Gaps
- **Intraday margin call terms.** Check the deadline to meet a call (2 or 5 business days on different Alpaca pages) and the exact de minimis test in Alpaca's current margin disclosure.
- **Open shorts below $2,000.** What Alpaca does with them is unknown; FINRA requires no liquidation after market declines, but Alpaca's house rules may differ.
- **US account minimums.** No explicit minimum deposit for opening an account, and no minimum notional for fractional orders, surfaced for US residents.
- **Non-US eligibility.** Margin and short-selling eligibility for non-US residents, by country, was not confirmed.
- **Fees and house requirements.** Not found: current HTB rates, and Alpaca's house maintenance requirements for volatile or leveraged ETFs.
- **Pass-through fees.** Regulatory fees passed through on sales (the SEC Section 31 fee and the FINRA trading activity fee) were not researched. They matter at high turnover.
- **2022 FINRA AWC.** A June 2022 FINRA AWC surfaced in a search for Alpaca, but its subject and whether it concerns Alpaca were not confirmed: [FINRA AWC No. 2019061652404](https://www.finra.org/sites/default/files/2022-06/finra-letter-of-acceptance-waiver-and-consent-no-2019061652404.pdf).

---

## 5. Capital level: how the liquidity cap and per-position risk interact with capital

### Takeaway
At G3-sized capital, the binding constraints are the $2,000 short-sale floor and whole-share sizing under the 0.5%-of-equity risk budget, not liquidity.

**At $2,000:** a full-risk position with a 2% stop is about $500. Shorts are possible only in names priced under about $500, and sizing stays within 10% of target only for names under about $50.

**The 2%-of-ADV cap:**
- It first binds on the thinnest eligible names ($20M ADV) when a single position exceeds $400,000. That happens at roughly $0.8M to $4M of equity, depending on stop width.
- It narrows the universe materially only in the multi-million range. For example, at a 2% stop, names under $50M ADV drop out from about $4M of equity.

### Cited Findings
- **Whole shares only for shorts.** Fractional trading is long-only and limited to DAY orders of a few types. — [Alpaca support: What is fractional trading](https://alpaca.markets/support/what-is-fractional-trading); [Alpaca docs: Fractional Trading](https://docs.alpaca.markets/us/docs/fractional-trading) [issuer-only]
- **$2,000 floor.** Any short sale needs at least $2,000 of account equity. — [FINRA Interpretations of Rule 4210](https://www.finra.org/rules-guidance/guidance/interps-4210); [Alpaca docs: Margin and Short Selling](https://docs.alpaca.markets/us/docs/margin-and-short-selling) [2+]
- **HTB lot size.** HTB locates come in 100-share lots, and HTB fees are charged on the nearest 100-share round lot. More than 5,000 ETB names are pre-approved for zero-fee locates. — [Alpaca docs: Margin and Short Selling](https://docs.alpaca.markets/us/docs/margin-and-short-selling) [issuer-only]

### Inferences
*All figures in this section are the researcher's arithmetic from the system's stated parameters, not sourced facts. Notation:*
- *E = equity*
- *d = stop distance as a fraction of price*
- *P = share price*
- *N = position notional at full risk = 0.005·E / d*

**Position size from the risk rule.** With gross exposure capped at 100%, the number of concurrent full-risk positions is 200·d. That count does not depend on capital; capital matters only through rounding and the floors.

| Stop d | N at E = $2,000 | N as % of equity | Max concurrent full-risk positions (gross ≤ 100%) |
|---|---|---|---|
| 1% | $1,000 | 50% | 2 |
| 2% | $500 | 25% | 4 |
| 3% | $333 | 16.7% | 6 |
| 5% | $200 | 10% | 10 |

**Whole-share rounding.**
- Shares = floor(N / P), so a position is undersized by up to P/N.
- A name is tradable at all only if P ≤ N. To stay within 10% of the target risk, P must be at most 0.1·N.
- At a 2% stop (N = 0.25·E):

| Equity E | N (2% stop) | Max price for ≥ 1 share | Max price for ≤ 10% undersizing |
|---|---|---|---|
| $2,000 | $500 | $500 | $50 |
| $2,500 | $625 | $625 | $62.50 |
| $5,000 | $1,250 | $1,250 | $125 |
| $10,000 | $2,500 | $2,500 | $250 |
| $25,000 | $6,250 | $6,250 | $625 |
| $50,000 | $12,500 | $12,500 | $1,250 |
| $100,000 | $25,000 | $25,000 | $2,500 |

  - With a 1% stop the price limits double. With a 5% stop they are 0.4 times these values.
  - So at small capital, whole-share sizing narrows the universe by price, and it stops mattering for most price ranges somewhere around $25k–$50k of equity.
  - Rounding always goes down, so realised risk is at or below target. A G3 run at $2,000 would therefore under-size high-priced names systematically compared with fractional paper trading.
  - Decision: apply the same whole-share rounding to the paper results used in the G3 comparison.
  - Decision: limit or flag names priced above 0.1·N.

**The 2%-of-ADV liquidity cap.**
- A full-size position needs ADV ≥ 50·N, which is 0.25·E/d (12.5·E at a 2% stop).
- The $20M ADV floor dominates until N exceeds $400,000.
- The equity at which a given ADV level stops supporting a full-size position is E = 4·ADV·d:

| Stop d | Cap first binds on $20M-ADV names | Names under $50M ADV fall short | Names under $100M ADV fall short |
|---|---|---|---|
| 1% | $0.8M | $2M | $4M |
| 2% | $1.6M | $4M | $8M |
| 3% | $2.4M | $6M | $12M |
| 5% | $4M | $10M | $20M |

  - "Fall short" means the position must be scaled down (and carry less than the target risk) or the name skipped.
  - At any plausible G3 size (10% of intended capital), the ADV cap does not bind unless intended capital is in the tens of millions.
  - It becomes material only when the full intended capital reaches the low millions or more.

**Smallest sensible capital, as a decision.** The G3 floor should be the larger of two amounts:
- $2,000 plus a drawdown buffer: for example $2,500 if G3 halts at −20%, so that shorting stays available until the halt.
- The equity at which whole-share rounding stays within tolerance for the price range the strategy actually trades:
  - about $2,000–$2,500 for names under about $50–60 (2% stop);
  - about $10,000 for names under about $250;
  - about $25,000 to trade names up to about $600 within 10%.

The current G3 rule ("10% of intended capital, at least $2,000, and enough for whole-share shorts") needs a stated price range and rounding tolerance to be testable.

**HTB at small capital.** At G3 sizes, a 100-share HTB locate on a $20 stock is $2,000 of notional, the whole account. Exclude HTB names at small capital.

### Gaps
- **Universe size.** No source was found for how many US stocks and ETFs trade at least $20M ADV, or for their price distribution. The tables above cannot be turned into "percentage of universe lost" without the system's own market data, so measure them during goal refinement.
- **Fractional minimum.** The minimum notional for fractional orders at Alpaca was not confirmed.
- **Costs at small size.** Per-trade costs at small notional values were not researched: spread, slippage, and pass-through regulatory fees on sales. They decide whether a $10 risk unit (0.5% of $2,000) is economically meaningful.
- **Alpaca position limits.** Alpaca house limits such as a maximum position as a percentage of equity, or concentration add-ons, were not researched.

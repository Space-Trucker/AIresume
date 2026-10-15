# Testing the goal

These tests check the goal itself, before there is any system. Each test has an **oracle**, the source of the
right answer, that lies outside the goal, so the goal is never used as evidence for itself. Run them
from this folder (Python 3.11 or later, standard library only):

```bash
python3 -m goaltests                      # tests goal.toml (the current goal)
python3 -m goaltests goal_v1.toml         # tests the goal as first agreed in conversation
python3 -m goaltests --only 1,2,7         # a subset
python3 -m goaltests --json results.json  # also writes the results
```

Simulations use fixed seeds, so every run repeats exactly. GT-2, GT-3 and GT-5 need real prices. Those
come from data files that public Python projects ship for their tests and examples, downloaded once:
three packages from PyPI, pinned by version and checked against PyPI's SHA-256, and three files from
GitHub, pinned by commit and checked against a recorded SHA-256. Only their CSV text is read
(`goaltests/data.py`). Without network access those checks report "no data" instead of a verdict.

| Test | Question | Oracle | Fails the goal when |
|---|---|---|---|
| GT-1 statement quality | is every statement verifiable, unambiguous, free of design, and traced to an objective? | ISO/IEC/IEEE 29148 characteristics, applied as rules | a key result lacks a metric, threshold, window, data, method or gate; uses a word with no agreed measure ("realistic", "constantly", "no crashes"); describes design ("AI model", "fast code"); or a limit is left as words |
| GT-2 internal consistency | do the limits contradict each other, or the planned activity? | arithmetic; queueing theory (Little's law, Erlang's loss formula); real overnight gaps of five large stocks, 1999–2014: the largest gap up (Yahoo, +49.5%, 1 February 2008, Microsoft's takeover bid) and the worst unscheduled gap down (NVIDIA, -28.0%, 3 July 2008, a revenue warning after the close); named events beyond the data: SVB's halt and delisting (10 March 2023), the regional-bank falls of 13 March 2023, the 13% level-2 market circuit breaker; residual volatility of real stocks | the stops on one side of the book, hit at once and filling 25% worse, exceed the daily limit, or on both sides exceed the worst-day bound; the jump assumption is smaller than a gap in the data; one position through the assumed jump, held overnight or within the session, exceeds the daily limit; a total loss in one name, or a jump across one industry, exceeds the jump-loss bound; the overnight net exposure through a 13% market gap exceeds the daily limit; the planned trades, held as long as planned, would find every position slot full more than 10% of the time, or need more exposure than the limits allow by day or overnight; the volatility budget is beyond what the planned book can produce; the stated return does not match the Sharpe ratio at the budget; shorting is called "no borrowed money" |
| GT-3 cost feasibility | at each holding horizon the goal allows, can a plausible signal pay the costs? | fee schedules (SEC Section 31: $20.60 per $1M sold from 2026-04-04; FINRA TAF: $0.000195 per share sold, capped at $9.79, from 2026-01-01); spreads (about 3.7 bps averaged over the 100 largest US stocks, Nasdaq); volatility measured on real prices; Grinold and Kahn's rule of thumb for information coefficients (0.05 good, 0.10 great, 0.15 too good to be true); the square-root law of market impact | the goal's cost model is cheaper than published costs; it does not say which horizons the planned edge comes from; at that horizon, or at the planned activity, the targeted return needs a signal beyond "great"; at the planned activity the targeted edge fails the goal's own cost stress, so G1 would reject the strategy the goal aims for; market impact at the goal's participation limit is well beyond the slippage it charges |
| GT-4 skill or luck | do the gates pass real edges and stop false ones, and does the live test stop dead strategies without stopping real ones? | simulated track records whose true edge we set, under four noise shapes: normal, fat-tailed (t, 4 degrees of freedom), volatility clustering (GARCH) and autocorrelated (AR(1), 0.1). The researcher tries the goal's budget of variants and takes the best. A false pass is a variant with no net edge (its gross edge just pays its costs, the hardest case); power is measured with one variant holding the targeted edge and the rest none. Paper trading is simulated with a rerun of the frozen strategy and an implementation noise of the size the goal assumes | G1 passes the best of the no-edge variants more often than the goal allows; a no-edge strategy reaches real money more than 0.5% of the time; G1, or G2 after G1, passes the targeted edge less than 80% of the time; G2's fidelity test fails an honest implementation more than 5% of the time, or misses an execution shortfall of a Sharpe unit more than 20% of the time; the drawdown halt stops the targeted edge in more than 10% of years; the live test stops the targeted edge within 3 years too often, or is too slow to halve and stop a dead one |
| GT-5 random strategies on real prices | do the gates pass strategies with no edge when returns have real fat tails, clustering and drift? | random entries, long or short, which have no edge whatever the data does, run under the goal's own rules (stops at 2× average true range, holding limit, size by risk, overnight limits, costs) on 1999–2014 prices of the S&P 500 and four large stocks; the best of the variant budget per window, as a researcher would pick | G1 passes the best random strategy more than 5% of the time, for balanced or for always-long random strategies; G2 passes more than 20% of the time |
| GT-6 metric gaming | can the goal be met in letter and missed in intent? | eight strategies built to look good with no edge, or with hidden risk: averaging down, selling tails without stops, riding a rising market, padding the trade count, the best of 50, paper's generous fills, a look-ahead leak, big overnight positions. Each is shown at its best, in a window where its flaw did not show | any of them passes both the risk limits and the gates |
| GT-7 control coverage | does the goal have the controls regulators expect of algorithmic trading? | SEC Rule 15c3-5; FINRA Regulatory Notice 15-09; EU RTS 6 (Delegated Regulation 2017/589); MiFID II's rules on records and clock synchronization; Fed SR 11-7; the SEC's Knight Capital order (29 items, seven of them added after the independent review) | an item is neither covered by a control nor declared not applicable with a reason; a control that covers an item only in part must state the deviation, which is reported |
| GT-8 outside view | if a strategy passes every gate, is it probably real and worth running, how likely is the program to get there, and does the goal plan for nothing passing? | base rates: Barber, Lee, Liu, Odean (2014), under 1% of day traders reliably profitable; Chague, De-Losso, Giovannetti (2019), 97% of persistent day traders lost money; McLean and Pontiff (2016), anomaly returns -58% after publication; Harvey, Liu and Zhu (2016), t > 3 for new findings. GT-4's pass rates for a range of true edges, weighed by the goal's prior over edge sizes | the chance that a passing strategy is real, or worth running, is below the goal's bound at its prior; the prior says nothing about how large an edge is; there is no research budget, no capital staging, no discount on published effects to what remains after publication, or no minimum count of variants |
| GT-9 effective challenge | what did the tests above not think of? | independent reviewers who see only the goal documents (`METHOD.md`, `GOAL.md`, `goal.toml`), each with a different lens | a finding survives the response in `REPORT.md` |

## Limits of these tests

- Volatility by horizon scales the daily volatility of two large stocks by the square root of time.
  Real intraday volatility is U-shaped through the day and noisier at very short horizons, which
  would make short horizons look worse, not better.
- GT-5's real prices are daily, so its strategies hold for days. Intraday dynamics enter through
  GT-4's simulations, not through intraday history: this environment cannot reach an intraday data
  vendor.
- The real stocks are five large technology names, more volatile than a typical stock in the
  universe. Their gaps make the overnight checks stricter, not looser.
- Without an earnings calendar, GT-2 drops each stock's 2% largest gaps as a stand-in for earnings
  nights in its 1-in-100 gap. The two named stress gaps were checked by hand: neither was a scheduled
  earnings release.
- The prior (5%) is a judgment anchored on the base rates above. GT-8 shows the result at 2%, 5% and
  10%.
- The gate rules are evaluated as written in `goaltests/gates.py`. That file defines what each rule
  means, and it is part of the goal's precision.
- GT-7 checks that every checklist item is claimed by a control, not that the control's wording is
  enough to meet it. That judgment is GT-9's.
- The jump assumptions (50% overnight, 20% within the session) come from named events. Larger jumps
  have happened: SVB lost its whole value. The goal bounds those by the jump-loss limit, not by the
  daily loss limit.

## Sources

- SEC, [Section 31 fee rate advisory, fiscal 2026](https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2)
- FINRA TAF from 2026-01-01: [Investrade fee notice](https://www.investrade.com/fees/), [Brokerage Review](https://www.brokerage-review.com/account-fee/taf-fee.aspx)
- Spreads: [Nasdaq, "Sampling the S&P 500 to minimize spreads"](https://www.nasdaq.com/articles/sampling-sp-500-minimize-spreads)
- R. Grinold, R. Kahn, *Active Portfolio Management*, 2nd ed. (2000), information coefficient rules of thumb
- Market-wide circuit breakers: NYSE Rule 7.12 and Nasdaq Rule 4121 (level 1 at -7%)
- NVIDIA's warning of 2 July 2008: [Fortune, 3 July 2008](https://fortune.com/2008/07/03/miss-by-chipmaker-nvidia-rattles-investors); Yahoo and Microsoft's bid of 1 February 2008: [PBS NewsHour](https://www.pbs.org/newshour/economy/business-jan-june08-yahoo_02-01)
- Queueing: J. D. C. Little (1961), "A proof for the queuing formula L = λW"; A. K. Erlang (1917), the loss formula
- Price data from the example files of [backtrader](https://github.com/mementum/backtrader/tree/b853d7c90b6721476eb5a5ea3135224e33db1f14/datas) (commit b853d7c)
- Alpaca: [margin and short selling](https://docs.alpaca.markets/us/docs/margin-and-short-selling), [market data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq), [paper trading behavior (forum)](https://forum.alpaca.markets/t/paper-trading-fill-delays-of-50-260-seconds-limit-orders-filled-minutes-after-price-crossed/18223)
- FINRA Rule 4210 intraday margin amendments (pattern day trader rule removed, effective 2026-06-04, phase-in to 2027-10-20): [ACA Group](https://www.acaglobal.com/industry-insights/finra-ends-the-pattern-day-trader-rule/)
- Everything else as listed in `METHOD.md`

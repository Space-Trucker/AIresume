# Research ideas

*Ideas for the research harness (plan step 4) and later. None of them is part of the goal or the plan until
the owner decides. Recorded 2026-10-15.*

*Labels: [full text] checked against the source's full text; [extract] from search-result extracts, because
this environment blocks arXiv, SSRN and the publishers' sites; [secondary] from someone else's account of the
source; [rule] quoted from `goal/goal.toml`; [computed] worked out here.*

The evidence on look-ahead bias behind decision 9 is in
`Trading goal decisions research/ai_model_lookahead.md`. This file adds the ideas that came after it, and
the checks made on them.

## 1. A news-reading model fenced by date

**The idea.** A language model trained only on text from before each decision reads the news and feeds G1's
forecast.

**Why it might work.**
- In the Chrono paper's test, news portfolios built with small date-fenced models did about as well as a
  much larger current model. Their Sharpe ratios were 4.80 for ChronoBERT, 4.92 for ChronoGPT and 4.90 for
  Llama 3.1. The authors conclude that look-ahead bias is modest for this use. How the test treats trading
  costs wasn't checked. [extract]
- Used to generate answers rather than to feed a model trained on top, a date-fenced model gives up more:
  ChronoGPT-Instruct's Sharpe ratio is 0.95, against 1.53 and 1.76 for larger models without date fencing.
  [extract]

**Models that exist.** [extract]
- ChronoBERT and ChronoGPT, by Songrun He, Linying Lv, Asaf Manela and Jimmy Wu (Washington University in
  St. Louis): a pair of models for each year from 1999. ScienceDirect lists the paper under a Journal of
  Financial Economics article id, dated 2026; the page itself wasn't opened. ChronoBERT's yearly models are
  on Hugging Face.
- DatedGPT: twelve 1.3-billion-parameter models with yearly cutoffs from 2013 to 2024, each trained on about
  100 billion tokens. Listed at NeurIPS 2026.
- "Scaling Point-in-Time Language Models": models of up to 4 billion parameters, trained on 1 trillion
  date-filtered tokens.

**Against the goal.** KR6.3: every model that shapes G1's return forecast "was trained only on data from
before each decision it informs (pre-training, fine-tuning, instruction data and any teacher model
included), and a cutoff audit checks it." [rule]
- The base models fit, once our own cutoff audit passes.
- DatedGPT's instruction-tuned models may not. A review says a teacher model sorted time-sensitive examples
  and wrote finance question-and-answer pairs for their tuning. If that teacher is a current model, KR6.3
  bars them. Not confirmed in the paper. [secondary, the review not identified]
- Chrono's instruction-tuned models: the authors say both their pre-training and fine-tuning data are
  filtered by date. Whether a teacher model was used wasn't checked. [extract]

**Where it goes.** One candidate input to the research harness (step 4). Each model or prompt change is a
new variant (KR6.1).

## 2. Removing what a current model knows after a date

**The idea.** Find the neurons inside a current model that hold its knowledge of events after a date, and
remove them, so that the model can be backtested honestly.

**Why it might work.** Goodfire's essay "Neural Networks Are Already Clean" (Cammarata, 2026) estimates that
roughly 90% of neuron poles in Qwen3-32B have one main job. In one saved Qwen3.6 run, zeroing any neuron's
output whenever its gate rose above that neuron's 99.9th percentile on ordinary text made the model go from
reciting Psalm 23 exactly to insisting it doesn't exist. Random cuts of the same number or size kept the
verse. [full text]

**Against it.**
- That is one saved example, not a measured rate, and the cut was broad: coding and other answers degraded
  too. It shows that recall rides on rare, extreme activations, not that one year's events can be removed
  alone. [full text]
- TEMPO (Zeyu Zhang and Bradly Stadie, Northwestern; NeurIPS 2026) argues that removing knowledge can't fix
  look-ahead, because what is allowed depends on each question's date. Their own date-aware training cut
  leakage from about 2–13% to 0.6–3.7%, not to zero. [extract]
- Removal methods tend to hide knowledge rather than delete it. Fine-tuning on some of the "removed" facts
  brought back about 88% of the original accuracy on the rest (Deeb and Roger). [extract]
- KR6.3 as written bars it, because the model was still trained on later data. It would need the owner to
  change the rule, and an audit able to prove a removal, which doesn't exist yet.

**Status.** No published work was found doing this for trading backtests (searches of October 2026). The
nearest work doesn't touch the neurons: Merchant and Levy adjust a model's output at answer time with two
small models, one for what to forget and one for what to keep (NeurIPS 2025); FinCAD corrects the output
while it is generated; another paper detects the bias without removing it. [extract]

**Where it goes.** Parked. Worth another look only if a removal can be audited.

## 3. A frontier model pruned down to finance

*The owner's idea. Considered on 2026-10-15 and not pursued.*

**The idea.** Take an open-weight frontier model, cut the neurons for everything except math, finance,
market history and trading algorithms, and use what is left as the forecaster.

**What is possible.**
- Cerebras's REAP removed half the experts (groups of neurons) of the 480-billion-parameter Qwen3-Coder.
  By the authors' count, it kept 97.6% of its coding score and 96.7% on the SWE-Bench agent benchmark
  (ICLR 2026). No independent replication was found. [extract]
- D-Pruner (NAACL 2024 Findings) prunes a model for one field, healthcare or law, and deliberately keeps the
  weights that general language ability and multi-task solving need. [extract]

**Why not for us.**
1. **The market history it would keep is the look-ahead leak.** A model that has read how the years in our
   test turned out can't be tested on them: it predicts what it remembers. KR6.3 is about what a model was
   trained on, and pruning changes only what it keeps. A pruned frontier model is barred from G1's forecast,
   just as the full one is.
2. **Pruning removes; it doesn't add.** At best the pruned model matches the original on finance; the gain
   is speed and cost. And stored facts go first: shrinking a model by more than 30% clearly hurt its recall
   of facts from training, while its use of what it is given in the prompt held up to a 60–70% cut (Jin et
   al., ICLR 2024; six models of up to 33 billion parameters). [extract]
3. **The "other things" move stocks.** Drug trials, court rulings, wars, weather and product launches all
   move prices, so a finance-only model reads market news worse. Bloomberg's 50-billion-parameter finance
   model, BloombergGPT, beat the open models it was compared with on finance tasks. A later study found
   GPT-4 as good or better on public finance benchmarks. [extract; the GPT-4 study secondary]
4. **Size.** The 480-billion-parameter model above takes about 480 GB at 8 bits per weight, and about half
   that after pruning. That needs several data-center GPUs to run, against the plan's two small machines.
   [computed]

**What a current model may do.** Under KR6.3: monitoring, operations and explanation, with no pruning
needed. A forecast driven by one could be proven only forward, live, which the decisions research puts at
about 4 to 5 years (`../reports/Trading goal decisions research.md`, decision 9).

**The useful core.** A model that knows only what we choose. Choose by date, not by topic: that is idea 1,
and those models are already small.

## Sources

- [Neural Networks Are Already Clean (Goodfire)](https://already-clean.goodfire.com)
- Chrono: [arXiv 2502.21206](https://arxiv.org/abs/2502.21206);
  [ScienceDirect listing](https://www.sciencedirect.com/science/article/pii/S0304405X26001455);
  [the authors' slides](http://asaf.manela.org/papers/hlmw/chronollm/slides.pdf);
  [ChronoBERT on Hugging Face](https://huggingface.co/manelalab/chrono-bert-v1-20181231)
- [Instruction Tuning Chronologically Consistent Language Models](https://arxiv.org/abs/2510.11677)
- DatedGPT: [arXiv 2603.11838](https://arxiv.org/abs/2603.11838); on the teacher model's cutoff,
  [Pith](https://pith.science/paper/2603.11838)
- [Scaling Point-in-Time Language Models](https://arxiv.org/abs/2607.11889)
- [TEMPO](https://arxiv.org/abs/2605.18843) and its
  [NeurIPS 2026 poster](https://neurips.cc/virtual/2026/poster/148926)
- [Deeb and Roger, Do Unlearning Methods Remove Information from Language Model Weights?](https://arxiv.org/abs/2410.08827)
- [Merchant and Levy, A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs](https://arxiv.org/abs/2512.06607)
- [Summoning the Oracle to Slay It (FinCAD)](https://arxiv.org/abs/2605.24564)
- [Detecting Lookahead Bias in LLM Forecasts](https://arxiv.org/abs/2512.23847)
- REAP: [arXiv 2510.13999](https://arxiv.org/abs/2510.13999);
  [Cerebras's blog](https://www.cerebras.ai/blog/reap);
  [ICLR 2026 poster](https://iclr.cc/virtual/2026/poster/10006871)
- [D-Pruner, Pruning as a Domain-specific LLM Extractor](https://arxiv.org/abs/2405.06275)
- [Jin et al., The Cost of Down-Scaling Language Models](https://arxiv.org/abs/2310.04680)
- [BloombergGPT](https://arxiv.org/abs/2303.17564); the GPT-4 study,
  [arXiv 2305.05862](https://arxiv.org/abs/2305.05862), seen only through a secondary account

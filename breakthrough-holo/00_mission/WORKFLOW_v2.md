# Lab protocol v2 (adopted 2026-09-30 after the owner shared Buehler's "AI builds its own instrument" post)

v1 rules 1–12 (`WORKFLOW.md`) still apply. v2 adds the parts of Buehler's workflow that survived fact-checking (`06_buehler_factcheck/`), plus fixes for weaknesses that the post itself shows and that our own run showed.

## Adopted from the post
1. **Instrument-first.** When a conclusion hinges on unknown physics, build a simulation instrument for that physics (force engine, generators, loading/probing procedures, analysis, experiment database) instead of guessing coefficients. Our case: `06_spark_instrument/`, a laser micro-spark simulator.
2. **Validation gate.** The instrument must pass a registered suite of validation tests before any design result counts, and every run prints the suite status.
3. **Predictions before results.** Before each campaign, commit to git (so it is timestamped and can't be quietly edited) what the instrument will show, with an interval. Score the predictions afterwards. A failed prediction is a lead, not an embarrassment: log the missing mechanism.
4. **Atlas.** Explore the design space systematically and publish the whole atlas, not just the winners.

## Improvements over the post
5. **Two kinds of validation, both required.** Agreement with a reference implementation (the post's 10⁻¹³ eV/atom) proves the *code* implements the model. It says nothing about whether the *model* matches nature. Every instrument therefore needs:
   - (a) implementation tests: analytic solutions and reference libraries;
   - (b) physics tests against published measurements.
   A result may only claim what the weakest relevant test supports.
6. **Model-form uncertainty is explicit.** Every assumption that no test covers (for example LTE and 1D spherical symmetry) goes in a ledger with an estimated effect. Results are reported as bands, not points.
7. **Adversarial review before any verdict** (our lesson from red team 1). An independent agent attacks the instrument and results before the verdict is written.
8. **Value of information.** The sensitivity of the final decision to each uncertain input picks which physical lab measurement comes first. "Go to the lab" is decided by what simulation *cannot* settle.
9. **No claim exceeds its medium.** Simulated results are called simulated, never "discovered in a material" (a caution the fact-check raised about the post).

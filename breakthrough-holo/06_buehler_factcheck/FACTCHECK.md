# Fact-check: Markus J. Buehler's post (29 Sep 2026) on an AI-built graphene instrument

**Source found:** github.com/lamm-mit/graphene-agent, "A model builds a model: an AI agent constructs a validated atomistic instrument and uses it to discover what sets the strength of architected graphene" (released 2026-09-23; M. J. Buehler, MIT LAMM).
- The agent was **Claude Fable 5.1 in Claude Code**.
- Agent's source report: `FACTCHECK_sources.md`.
- I verified the lines quoted below myself from the repository README (rule 12 double validation).

## Verdict: real, transparent work, with a post that overstates it

| Claim in the post | Verdict | What the source says (verified by me in the README) |
|---|---|---|
| AI built the atomistic instrument "from scratch" | **True, with context** | It wrote a PyTorch implementation of the screened REBO2 potential and the full platform. But the human's one prompt (~46,000 characters) "fixed the physics and the discipline": the potential, the 20 tests, the stages and the holdout rules. |
| "Ran for multiple days without scientific intervention" | **Overstated** | "about 30 hours without intervention". A second, human-directed phase followed. |
| Passed 20 validation tests; reference energies to ~10⁻¹³ eV/atom | **True, but easily misread** | 6×10⁻¹⁴ eV/atom against the published *Fortran implementation of the same potential*. This proves the code is correct, not that the physics is. Production runs used a float32 mode (~7×10⁻⁶ eV/atom). |
| "First-principles" / "quantum mechanical ground truth" | **Misleading** | "mechanics only from the published screened REBO2 potential": an empirical classical potential, with no quantum calculation. |
| Predictions committed before results | **True** | Holdout predictions hashed 2026-09-05 21:20; first holdout run 21:52; 30 hashed predictions in total; median strength error 14 %. |
| Strength varied more than sixfold | **True (in the model)** | 6.6× (4.9–32.5 N/m) at matched density. The weak end is slits across the load. |
| Angled slits: three regimes | **True (in the model)** | Tip linking (strength minimum at 20°), ligament rotation (25–45°), bridge bending (> 60°). |
| Hierarchical designs ~25 % stronger than same-mass controls | **Not found; the source's headline says the opposite** | "Hierarchy is not a free lunch": nested meshes sit 1.6 ± 1.4 N/m *below* single-level ones at equal alignment. |
| Material "extremely lightweight yet strong, far better performing than existing structures" | **Not supported** | "Everything here is a model result … No claim is made about real materials." Pristine graphene (38.8 N/m) beats every porous design. |
| "Discovered how a material … keeps carrying load … preventing catastrophic failure" | **Overstated** | Simulations of ~3,000-atom sheets only. Nothing was fabricated or physically tested. |
| "Atlas of hundreds of thousands of structures" | **Partly true** | Generated geometries are released as datasets (64k and 256k); only 132 structures were simulated. |

## What is genuinely valuable and adopted in our lab (`00_mission/WORKFLOW_v2.md`)
- An AI agent building and validating its own simulation instrument before using it.
- Predictions hashed before runs, with failures treated as mechanism clues ("the misses are the mechanisms").
- A full public record: the prompt, human messages, database and negative results.

## Lessons we apply beyond it
1. **Code-correctness tests and physics tests are different things.** 10⁻¹³ eV agreement says nothing about how well the model matches nature. Its own potential is ~30 % off experiment in stiffness, a fact the post omits. We require both kinds of test.
2. **Say which medium a result lives in.** A simulated result is a model result, not a material.
3. **The human prompt set the tests.** Self-chosen tests can be too easy, so our validation suite gets an independent adversarial review.

# breakthrough-holo: Iron Man holograms, researched to the physical limit

An overnight research lab, run autonomously, answering one question:

> Can a single "very sophisticated projector" make Iron Man-style holograms in open room air, with no glasses, fog or screens, touchable with at most a glove, and safe for everyday use?

**Short answer (verdict v4, after four red teams): not solved, but there is now a physics-allowed route. Its first unknown is a new material, not physics.**

- **Phase 3, MOTE (`07_mote_route/`):** the projector's heads hold micro-motes (1–4 µm) in invisible 1550 nm beams and sweep them along the image; each mote glows cyan under a µW violet pump.
  - No ozone, UV, noise, fog or screen. Every trap beam is ≤ 10 mW.
  - After red team 4, it works only in a *designed lab*: a quiet-air zone, a 12-head room rig, and an engineered aerogel or core–shell mote that has never been made.
  - It then needs ~1 000 steered beams for accents, ~3 000–4 000 for an Iron-Man sketch and ~10⁴ for film density.
  - Ordinary drafty rooms are ruled out. Bench item 1: measure force per absorbed watt on a real mote.

**Phases 1–2 (plasma), unchanged:**

The only way to put light at a point in open air is to spark that point with a focused laser pulse (proved in T1). Sparks are dim lamps, and each one makes noise, NO₂/O₃ and UV-C through an open Class 4 laser focus.

The room-safe light budget therefore allows only sparse glowing sketches:
- **P(safe in a home) = 0.**
- **Supervised venue:** 0.71 for sparse accents, 0.36 for a ~5 m "Iron-Man sketch", 0.08 for film density, 0 for film-exact (E10b).

The solid contributions are:
- the impossibility theorem;
- the governing budget;
- a new quiet-drawing method (subsonic multi-channel tracing);
- **SPARK** (`06_spark_instrument/`): a laser-spark physics instrument built and validated here (22/24 tests), after the owner asked for Buehler's "AI builds its own instrument" workflow (fact-check in `06_buehler_factcheck/`);
- a bench plan ranked by which measurement would change the answer most.

Verdict v3: home use is ruled out by spark noise and regulation; a supervised dim-venue "sketch" has an open probability of 0–0.6 that only a bench can settle.

Full grading: [`05_reviews/FINAL_VERDICT.md`](05_reviews/FINAL_VERDICT.md).

| Start here | What it is |
|---|---|
| [`00_mission/GOAL.md`](00_mission/GOAL.md) | The request, the reference frames and requirements R1–R10, frozen before any result |
| [`NOTEBOOK.md`](NOTEBOOK.md) | Dated lab notebook: every hypothesis, kill and correction (including my own mistakes) |
| [`02_theory/`](02_theory) | T1: what physics allows (theorem + kills). T2: the light–chemistry–noise trilemma. T3: grey-zone routes. |
| [`03_simulations/`](03_simulations) | 15 simulation scripts. Every model is calibrated against a published number where one exists; the red-team corrections are in E10b (`python3 run_all.py --fast`) |
| [`04_engineering/`](04_engineering) | Aether-1 architecture, roadmap and experiments, and the runnable `holo_engine` pipeline |
| [`05_reviews/`](05_reviews) | Independent idea rounds (three other models), red team, final verdict |
| [`06_spark_instrument/`](06_spark_instrument) | SPARK: EOS, radiation, hydro and chemistry; validation suite; prediction registry; 40-format atlas |
| [`06_buehler_factcheck/`](06_buehler_factcheck) | Claim-by-claim fact-check of the post the owner shared |
| [`07_mote_route/`](07_mote_route) | Phase 3: MOTE instrument (physics, budget v1/v2, feedback, room head arrays), atlases M1–M5, research notes R5–R8, `RESULTS.md` |
| [`02_theory/T5_mote_theory.md`](02_theory/T5_mote_theory.md) | MOTE theory: heat–force identity, speed, lateral, focus, feedback and steering laws (with the v2 correction box) |
| [`01_research/`](01_research) | Literature notes with sources: plasma displays, particle displays and haptics, safety limits, film analysis, research methods |

## Key figures (`03_simulations/results/`)

- `e10_feasibility_map.png`: where a pure-air plasma display is safe, against the film target
- `e6c_subsonic_tracing.png`: the drawing method that removes ~20 dB of noise in every direction
- `e11_plasma_color.png`: which colours air plasma can make
- `e7_hazard_zone.png`: laser hazard confined to millimetres around each spark
- `../04_engineering/holo_engine/out/`: previews of the hologram, a hand inside it, and room comparisons

## Reproduce

```bash
pip install numpy scipy matplotlib pillow
cd 03_simulations && python3 run_all.py --fast      # ~3 min (add no flag for the 15-min E6b optimisation)
cd ../04_engineering/holo_engine && python3 demo.py 4 0.5 9 1.8 && python3 compare_rooms.py
```

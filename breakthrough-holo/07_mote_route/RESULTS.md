# MOTE route: results (instrument v1, before red team 4)

**Status:** draft. Red team 4 (`05_reviews/red_team_4_mote.md`) is reviewing it; its corrections will be applied to this file.

**Code:** `mote/` (physics, safety, budget, feedback, dynamics). **Validation:** `validation/validate_mote.py`, 26/26 pass. **Theory:** `../02_theory/T5_mote_theory.md`.

## 1. What the route is

A projector holds microscopic motes (radius ≈ 1–5 µm, micrograms in total) in invisible 1550 nm photophoretic beams. It moves them along the strokes of the image at ≈ 0.4–1.1 m/s, 30 times a second. Each mote is a composite: a low-conductivity carrier, an absorber for 1550 nm, and an Eu²⁺ phosphor. It glows cyan (Iron Man blue) or orange under a µW violet pump beam.

There is no plasma, so no ozone, NO₂, UV or clicks. Motes are dark and far below visibility when not pumped; lost motes are a negligible dust load (R7: ~0.1 µg per day).

## 2. Best designs per content target (M1 atlas, 576 designs per target)

Settings: 1550 nm trap, 1.5 m throw, 1 m field, T_mote ≤ 450 K, 0.2 m/s air margin, 30 Hz. All rows are Class 1 per beam and at every head's exit window. Stray light on the walls is ≤ 5 % of the image flux.

| Target | Design | Motes | Steering channels | Mote ΔT | 1550 nm total | Per trap beam | Per pump beam (AEL) |
|---|---|---|---|---|---|---|---|
| Accent (3 cd/m², 1 m) | push4, a = 1 µm, k_p = 0.02, 300 mm heads, cyan phosphor | 38 | 151 | 146 K | 0.06 W | 0.88 mW | 27 µW (39) |
| Iron-Man sketch (3 cd/m², 5 m) | same | 188 | 754 | 146 K | 0.30 W | 0.88 mW | 27 µW (39) |
| Film contrast (4 cd/m², 9 m) | same | 339 | 1 357 | 149 K | 0.54 W | 0.87 mW | 36 µW (39) |
| **Film density (4 cd/m², 30 m)** | same | **1 131** | **4 524** | 149 K | **1.8 W** | 0.87 mW | 36 µW (39) |
| Film-exact, lit lab (50 cd/m², 30 m) | push6, a = 5 µm, Yb/Er upconversion (980 nm pump) | 5 393 | 32 356 | 142 K | 1.6 W | 0.20 mW | 1.24 mW (1.43) |

Other results from the atlas:
- **Scatter motes fail everywhere.** Forward diffraction lights the walls as much as the image.
- **Incandescent motes** were rejected by R6.
- **Upconversion motes** work up to film density, with lateral2 traps: 2 761 motes and 5 522 channels.
- **Single head** (BYU-type trap, 600 mm aperture, a = 5 µm, η = 0.5 *assumed*): film density needs 3 451 channels. Treat this as a hypothesis until a bench measures η at room throw.
- **Real Iron Man content** (`04_engineering/holo_engine/mote_plan.py`): the chained stroke tour of the procedural armor has duty 0.57 (5 m), 0.72 (9 m) and 0.83 (30 m). That gives 231 / 328 / 950 motes at 1.14 m/s and 30 Hz, and twice as many at 60 Hz.

## 3. Feedback (M2) and focus tracking (M1c, M3)

- **Loop rate.** The push trap needs a ≥ 15–20 kHz control loop at room gusts (σ = 0.1 m/s) and 20–30 kHz at 2× gusts, with ≤ 0.5 µm position sensing (T5 §9).
- **Focus tracking.** Trap beams need 2–4 kHz of focus bandwidth. The 405 nm pump needs ≈ 17 kHz, because its tight focus has z_R ≈ 22 µm.
- **5 kHz focus scenario (MEMS varifocal).** The optimum shifts to lateral2 with a = 2.5 µm, costing ≈ 20 % more channels (film density 5 522).

## 4. Steering wall (M3)

Each channel needs:
- ≈ 78 000 resolvable positions per axis over a 1 m field (or tiling with hand-over);
- 0.3–0.6 µrad pointing precision;
- 2–17 kHz focus tracking;
- 20 kHz intensity control and sensing.

Every function exists in some device today. Thousands of integrated channels do not. **This is the binding problem, and it is engineering, not physics.**

## 5. Prediction scores (registered before the runs)

| ID | Prediction | Result | Score |
|---|---|---|---|
| P15 | 5 µm mote at ΔT ≤ 150 K: 0.3–1.5 m/s | push4 0.38–0.78, push6 0.65–1.36 (k_p 0.1–0.02); lateral at 100 mm heads 0.23 | ✓ for push; ✗ for lateral |
| P16 | Sketch 100–600 / film 600–3000 motes | 188 / 1 131 (push4); 460 / 2 761 (lateral2) | ✓ |
| P17 | Film-density IR power 1–30 W | 1.8 W (push4); 0.98 W (lateral2) | ✓ (best design) |
| P18 | 0.05–2 lm per W of total IR (green UC) | 0.99 lm/W | ✓ |
| P19 | 5 µm mote at ≥ 0.7 m/s with ≤ 10 mW per beam | push6 1.36 m/s at ≈ 0.9 mW per beam | ✓ |
| P20 | A 0.2 m/s draft gives > 1 %/s loss unless the force margin is ≥ 2× | Not tested as stated. For push traps, loss is set by loop bandwidth versus gusts, not force margin | inconclusive (superseded by P23) |
| P21 | Film-exact: < 5 W absorbed emitter power, zero gases, zero audible noise | 0.25 W absorbed; no chemistry; silent | ✓ (but 32k channels) |
| P22 | Single-head lateral trap at 100 mm aperture: 0.1–0.5 m/s | 0.25 m/s | ✓ |
| P23 | Loop rate for < 1 %/min: 2–20 kHz | 15–20 kHz at room gusts; 20–30 kHz at 2× gusts; < 1 %/min not certifiable in 6.4 mote-s | ~ partial |
| P24 | Film density Class 1 with ≤ 300 mm heads; 2–15 W | Class 1 yes; 1.8 W | ~ partial (power below the interval) |
| P25 | UC Class 1 at 980 nm needs ≥ 200 mm heads | infeasible at 100 mm, feasible at 200 and 300 mm | ✓ |
| P26 | BYU 1.83 m/s implies ΔT 250–700 K | 160–400 K | ~ partial (the low end falls below the interval) |

**Tally:** 8 ✓, 3 partial, 1 inconclusive, 0 ✗. The ✓ rate is high, and that is a warning sign: the predictions were made from the same first-principles scaling the instrument encodes. Only P22–P26 test anything outside that scaling. Red team 4 is the real test.

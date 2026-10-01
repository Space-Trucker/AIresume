# Final verdict (v4: MOTE route added; red team 4 applied)

*Graded against the requirements frozen in `00_mission/GOAL.md`. History:*
- *v1 over-graded; red team 1 corrected it (v2).*
- *v3 added the SPARK instrument (red teams 2–3).*
- *v4 adds Phase 3, the MOTE route: light-held self-emitting micro-motes. It includes red team 4, my independent checks of its claims, and the owner's direction that many discreet heads in the room are acceptable.*

## Answer

**Not solved. No ping, per the owner's rule.** The two routes that physics allows (T1: light made at the point) now stand as follows.

**1. Plasma (laser sparks, v3, unchanged).**
- **Home:** ruled out by spark noise and consumer laser rules.
- **Supervised dim venue:** a "sketch" has an open probability of 0–0.6 that only a bench can settle.

**2. MOTE (Phase 3, v2 after red team 4).** The projector's heads hold micro-motes in invisible 1550 nm beams and sweep them along the image; each mote glows cyan under a µW violet pump.
- No law of physics is violated.
- No ozone, UV, noise, fog or screen.
- Trap beams are ≤ 10 mW each.

But after correcting my own errors (red team 4), it is a **conditional** design:

| Condition | Status |
|---|---|
| A mote with FOM = (J₁/A)/(k_eff + 2k_g) ≳ 4 m·K/W plus a strongly absorbing emitter core | **Not made or measured anywhere.** Validated (M7): passes only with an **ITO-class plasmonic NIR skin** (α ≳ 3×10⁵ cm⁻¹; FOM ≈ 5). The safer Cs_xWO₃ skin fails or is marginal (FOM 0.4–3.9). ITO needs a toxicology study (~ng/m³ exposure estimated). Plausible-optimistic motes (FOM ≈ 2) make everything 3–5× bigger; dense motes make nothing feasible |
| A designed room: quiet-air zone (≤ 0.15 m/s), non-fluorescent surfaces, a 12-head "lab rig" (ceiling ring + low ring + ceiling spot + floor head, 1.2–2.3 m throws) | Architectural; fits the owner's "heads set gracefully in the room" |
| Steering engine | **~10³ channels for an accent, ~3–4×10³ for an Iron-Man sketch, ~10⁴ for film density** (étendue-tiled, with hand-over). Push beams also need ≥ 20–50 kHz control; passive doughnut pairs need none |
| Class 1 as a product | Needs scheduler-enforced no-overlap of foci (the workload manager as a safety function) plus a certified fault shutdown. A new safety argument, not yet accepted by any notified body |
| Ordinary home room | **Ruled out:** 0.3 m/s drafts consume the whole heat-limited speed budget; stray violet pump lights optical brighteners |

## The floor: every known lever pulled together (M8, corrected for summed trap beams at a focus)

Levers: ITO-skin mote (FOM ≈ 5.3), hot face ≤ 600 K, heat-tolerant phosphor, a laminar quiet zone whose mean flow is cancelled by feed-forward (0.05 m/s fluctuation), 45 Hz, 12-head rig.

**Self-found correction.** At 1550 nm the hazard is to the cornea. The trap beams converging on one mote cross at its focus, so an eye there receives their **sum**, which must be ≤ 10 mW. Passive doughnut pairs (2 beams) now beat push (3).

| Target | Fewest steered trap beams |
|---|---|
| Accents | **~490** |
| Iron-Man sketch | **~2 100** |
| Film density (dim lab) | **~8 800** |
| Film-exact, lit room (50 cd/m²) | **~8 800 (green motes) to ~10 500 (cyan)**, with 2.5–4 µm motes and 2–6 pump beams per mote at 405 nm (M8c) |

**Hypothetical perfect materials** (k = 0.01, 900 K; M12 before the focus-sum fix): only ~30 % fewer beams. The binding limit then becomes the 10 mW Class 1 trap cap, not heat.

These are model floors, cross-checked for one design point (M8b). **The bench (`08_bench/BENCH_PLAN.md`) is the critical path**, with gates:
- G1: the force law (C_ph);
- G2: the mote FOM;
- G3: a passive pair at room distance;
- G4: the first glowing stroke.

Bench code is ready and self-tested.

**Demonstrator ladder (M11, corrected; passive pairs; conditional on G1–G2):**

| Demo | Content | Beams | Cost today |
|---|---|---|---|
| D1 first glyph | 10 cm circle | 79 | $0.06–0.4 M |
| D2 arc-reactor UI | 1 m of strokes | 404 | $0.3–2 M |
| D3 desk Jarvis panel | 3 m of strokes | ~1 100 | $0.8–5.6 M |
| D4 Iron-Man sketch | 5 m of strokes | ~2 400 modules | $1.7–12 M |

With integrated 2-axis MEMS arrays (R10, 5–10 yr): D3 ~$56–280 k.

## Scorecard for the best route (MOTE, designed lab, engineered mote *if it can be made*)

| ID | Requirement | Grade | Evidence |
|---|---|---|---|
| R1 | Free-space image | MET | Motes emit at the point, in open air |
| R2 | No eyewear | MET | Isotropic phosphor emission |
| R3 | No added media | **PARTIAL** | µg of projector-supplied, recovered motes; micro-dust, not fog. Needs the owner's ruling. 1–2.5 µm motes are respirable; composite toxicology unknown |
| R4 | Projector only | PARTIAL | A 12-head room rig plus a quiet-air zone. The owner accepts many heads |
| R5 | All-around, many viewers | MET | Isotropic |
| R6 | 3D models, animation, video | PARTIAL | Wireframes; motion limited by mote speed (0.2–0.5 m/s strokes) |
| R7 | Touch | PARTIAL | Glove haptics. Hands shadow beams and push motes; redundant heads help (1 % of cases lose the mote with one head blocked in the 12-head rig). Motes themselves cannot be felt |
| R8 | Safe for everyday use | **PARTIAL** | No chemistry, no noise; beams Class 1 per beam. Product Class 1 depends on scheduling and fault shutdown. Normal (drafty) rooms don't work |
| R9 | Iron Man quality | PARTIAL | Dim-lab film density at ~10⁴ channels; sketch at ~3×10³. Cyan ✓; orange via a second phosphor |
| R10 | Buildable by a startup | NOT MET | Needs a new mote material, then a 10³–10⁴-channel beam engine. R10 cost estimate today: accent room $0.5–5 M, film-density room $4–40 M. With a 4–8× étendue analog MEMS mirror array plus integrated photonics (5–10 yr): film density ~$0.4–2 M |

**4 MET, 5 PARTIAL, 1 NOT MET.** v3 had 4 / 4 / 2. MOTE converts R8 from NOT MET to PARTIAL, but only in a designed room, and only if the mote exists.

## What would move the verdict (bench, ordered by value of information)

| # | Measurement | Why |
|---|---|---|
| **1** | **Photophoretic force per absorbed watt, and k_eff, on a real engineered mote** (aerogel or core–shell with island NIR skin), 1–3 µm, in air at 1 atm | Decides whether the MOTE route exists at all (FOM ≳ 4, or C_ph near 1). Also resolves M22 (BYU consistency) |
| 2 | Cyan phosphor on a hot mote: 405 nm absorption of a µm core, quench at 450–500 K, lumens per absorbed W | Pump Class 1 margin and wall light |
| 3 | One mote, two opposed LG01 heads at 1.5–2 m (passive pair): lateral η, escape speed against absorbed power | The passive (no fast loop) architecture |
| 4 | One mote, four heads, closed loop ≥ 20–50 kHz, fans on | The push architecture |
| 5 | Plasma X4/X5 (subsonic tracing, fume capture) | The venue sketch route (v3) |

---

## Plasma route (v3 content, unchanged)

## What the SPARK campaign established (and how firmly)

| Result | Firmness |
|---|---|
| Laser-spark hydrodynamics, energy closure and implosions work numerically | Implementation-validated: Sod, Sedov, Noh, conservation, convergence (22/24 validation tests pass) |
| ns-spark radiated share 25 % (measured 22–34 %), NO 7.4–7.9×10¹⁶ /J (measured 4.6×10¹⁶–1.5×10¹⁷), cooling at 10 µs, shock pressure at 1 mm | Physics-validated against published measurements |
| Micro-spark light per watt 0.016–0.4 lm/W, rising with spark size (P5 ✓; P10 coefficient ✗) | Model result, ±3× (Biberman factor, conductivity, LTE deposition) |
| A second pulse *reduces* light (P9 ✗) | Model result, robust in sign |
| A line focus triples light per watt, with the same UV and chemistry per unit light | Model result, robust (like-for-like comparison) |
| UV and O₃ rise in step with light (T4) | Model property, not a law. The UV ratio is set by the continuum model (±×3); 30–54 % of the reactive total is an ad hoc EUV rule |
| Deep-UV lines make sparks ozone-rich | Model result; the line strengths are from memory (±3×) |
| Honest fails | V16 (noise-law cross-check, ill-conditioned) and V18 (early temperature at 1 µs) |

## What would move the verdict (bench experiments, ordered by value of information)

| # | Measurement | Why it matters |
|---|---|---|
| 1 | Subsonic multi-channel tracing on real sparks (X4): audible spectrum of a regular click train moving slower than sound, with UI-like content | Venue sketch probability 0 without it, ~0.2–0.6 with it |
| 2 | Source capture of spark fumes with a heated manikin and hands in the volume (X5) | Capture 0.3 → 0.9 moves the air cap ~10× |
| 3 | Calibrated 180–900 nm spectrum and lumens per absorbed joule for ps micro-sparks, time-resolved over the first 50 ns (X1) | Tests SPARK's η and the UV-per-lumen value (P14b), and the instantaneous-LTE assumption |
| 4 | O₃, NO and NO₂ per joule and per lumen (X2/X7), versus Cook 2000's "no detectable O₃" for long sparks | Tests the ozone-rich prediction |

None of the plausible outcomes makes a home Iron Man projector. They decide whether a supervised, dim-venue "hologram sketch" product exists.

**Other routes to the owner's goals (T3):**
- **Helmet visor:** exact film look now; it is eyewear, which a helmet can have.
- **Contained particle displays:** colour at desk scale.

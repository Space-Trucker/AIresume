# Final verdict (v6: home routes T9, idea round 4, red team 9; v5 below)

## v6 summary (2026-10-05)

**Answer: not solved. No ping.** The scorecard stays at **4 MET, 5 PARTIAL, 1 NOT MET**.

**What round 9 did.** It took the owner's "buildable at home" instruction and tried every route in which the air, not the light, carries the motes.

| Route | Source | Best claim | Outcome |
|---|---|---|---|
| FLOW-X: a targeted mote stream in a laminar column, lit by POV | m20, brief | No IR; visible Class 1 | **Fails at home** (opus round 4, double-checked). It needs Tu ≤ 0.2 % and a 2D on-demand injector, and content lags 1.2–5 s |
| AIR-SV: beads hover in an upward column, and light only trims | m21, m21b | Trims of 0.04–0.4 mW, skin-safe | **Dead in open rooms.** Cross-drafts must stay ≤ 8–21 mm/s; hand plumes are 10–400× the trims; vertical strokes exceed the skin cap; content moves at 22 s per 10 cm |
| E-AIR-SV: AIR-SV plus a fixed per-bead charge and a weak field | m22 G | Static wakes and size spread compensated at 76–231 V/m | **Enclosed sculpture only.** Drafts, hands (9–31 mm/s at 10 cm) and content speed remain |
| FLOW-R: a uniform food-grade mote rain, gated visible spots, tracking | opus round 4 | One-frame content, survives hand wakes, no IR | Desk-scale demo (0.2 m, ~$5–12k) that bends "no gas" and "not a table". 3D tracking blocks room scale |
| FLOW-R2: FLOW-R plus crossed-probe gating (an IR pencil projector and 2–3 cameras) | m23, m23b | Room scale without tracking; ghosts ≤ 0.6 % | **Refuted as specified by RT9** (re-checked by the main session). The probe voxel starves the rain (C1: 62–71 % of samples dark); heads are Class 1 per beam, not per product (C2: 11–133× at 10 cm); open-loop shots miss (C3: 0.2–0.7 % hit). Fixes are non-commodity: about $50–120k for an installation, not a projector |

**New results that stand** (m22 and m23b, reproduced by RT9 and the main session's fresh check):
- **Laplace low-pass.** Fields from sources outside the image cannot address mm structure. Only propagating waves address single motes in open air.
- **Photo-charge is one-way in air.** Light can only lower |q|, and per-bead charge control ratchets out within seconds. Charge is a static setting.
- **Thermal kick theorem.** Time-shared trims peak at T_rev/τ_th × the steady heating.
- **Self-addressing intracavity motes** need ≥ 5.5 kW–0.8 MW of pump (gain étendue).
- **Coulomb crystals** of charged motes are 10²–10⁵× too soft against drafts.
- **Rain rendering law:**
  - fill F ≈ n·U·d_s²·t_eye(|cos θ| + |sin θ|) for any stroke angle;
  - simultaneous lit motes = F·S/(U·t_eye);
  - mass and haze ∝ F/(U·d_s²).
- **The full-vision tetralemma.** No fog + occupied open air + child-safe light + commodity addressing cannot all hold: at 3 cm/s the skin rule needs w ≤ 22 µm, 7.7×10⁷ modes per head and 14 kHz loops. Every escape found relaxes at least one of the four (column, interlock, rain medium, smaller image).
- **Safety corrections:**
  - mannitol is the Aridol bronchial challenge agent;
  - lactose carries milk protein, so trehalose is the default mote sugar;
  - 99.97 % capture is needed for the WHO PM10 figure.

**What would move it** (RT9's value-of-information list):
1. a rate-matched probe voxel with ≤ 1–2 % ghosts;
2. a Class 1 distributed launch for the heads;
3. a ≤ 5–6 ms velocity-predicting aim with ≥ 90 % hits;
4. 99.97 % capture, measured with people present;
5. a viewing study of dotted and streaky lines;
6. the owner's rulings on the mote medium, ceiling and floor hardware, and line texture.

Items 1–4 passing would make a room FLOW-R2 a credible installation. It would still not be "just a projector".

---

# Final verdict (v5: unlock program T6–T8 and red teams 6–8 applied; v4 below)

## v5 summary (2026-10-01)

**Answer: not solved. No ping.** The scorecard stays at **4 MET, 5 PARTIAL, 1 NOT MET**. The unlock program sharpened *why*.

**Three architectures were tried after v4. Each was refuted or narrowed by an independent red team that the main session checked:**

| Round | Architecture | Best claim | Red team verdict |
|---|---|---|---|
| T6 (m15–m17) | Light-curtain static voxels (holographic flat-top spots, DMD fast plane) | Film density, normal room, passive Class 1 | **RT6:** drafts need authority U + 5.4σ (still rooms only); flat-tops need 12–150× the modes; DMD plane fails on étendue and depth; aerogel motes barely scatter sideways |
| T7 (m18) | Gaussian static voxels, forward-scatter illumination, hologram-rate (5 kHz) spot-following loop | Still-room sketch and film at 12–48 W, ~10¹⁰ IR modes | **RT7:** visible engine needs 66–220 wall emitters and 10¹¹–10¹² modes; a real thin skin gives J₁ ≈ 0.24, so the force needs twice the light; fixed-spot loop sims omitted the mean wind (spot-following fixes it). **Only the still-room sketch survives,** at w 30 µm with 5 kHz spot-following and ~2–4×10¹⁰ IR modes plus the visible engine |
| T8 (m19) | POV motes under the crossing-rate rule (moving focus = pulse train) | Sketch in office drafts, ~3 200 channels, 4 W, passive Class 1 | **RT8:** pupil load 2.7–9.1× the AEL (beams run along strokes); the loop loses motes once the force is resolved inside the frame (confirmed by the main session); channels need a mode multiplexer. **Refuted as specified** |

**New results that stand (each double-validated):**
- **B9.** Under passive Class 1, a *static* photophoretic voxel's mean speed relative to the air is capped at ~2–10 cm/s for buildable spots. In mode terms it is ~7.5×10⁻¹¹ m/s per pixel per head (RT7). That is why static designs need still air and slow content.
- **The crossing-rate framework.** At 1400–4000 nm a moving focus is a pulse train at any fixed aperture (rules 1 and 2; C5 does not apply). The energy per unit path is speed-independent, so B9 does not bound moving foci (opus round 3, R7, sonnet, RT8).
- **Physics floors** (opus round 3): no light-to-force mechanism in air beats thermal creep's force per watt (~×2 headroom at best); ~10 mW per pupil is physiological at 1.4–1.8 µm; and s, h ≥ 1, plus étendue.
- **EN 50689 (child-appealing consumer products):** skin MPE through 1 mm over 10 s, i.e. ~0.785 mW per focus. This is snippet-verified by sonnet and reproduced by RT8, and it is 12× tighter than the eye.
- **Mote absorber:** a thin skin absorbs ≤ ~0.5–0.6 per pass, with J₁ ≈ 0.24 (RT7). The FOM 5.3 "ideal ITO skin" was optimistic.
- **Touch stirs the air:** a moving hand clears 1–8 cm of motes. A warm hand's plume (0.1–0.4 m/s) exceeds static budgets, and an isothermal glove helps (m18d).

**Requirements after v5:**
- **R3:** unchanged, and sharper: 1 µm ITO motes are respirable, and RT8 puts indium in room air at 4–180 % of Japan's worker limit at simulated loss rates.
- **R6:** fast animation is excluded for static voxels by B9 × B8; it is open only for POV, which needs a new loop and allocation.
- **R8:** passive Class 1 static voxels need still air. Consumer (EN 50689) skin limits tighten everything ~4–12×.
- **R10:** NOT MET, with 10¹⁰–10¹² hologram modes or 10³–10⁴ channels with 20–40 kHz loops.

**What would move it** (value of information):
1. Bench B2 on a real 1 µm skinned mote: A, J₁ and k_eff.
2. A single-mote 1550 nm trap at w 25–50 µm with a fast steering stage and camera feedback, measuring the profile instability and loss rate.
3. Draft statistics (U, σ_u) at a hologram position in a real home, with people present.
4. A notified-body pre-opinion on the crossing-rate classification, EN 50689 skin, and the stall cut.

**Where the research points next.**
- POV remains the only route that is not bounded by B9. It needs:
  - a stacking-aware, dose-map-governed allocation shown on real content;
  - heads with R ≳ 0.25 m;
  - a loop whose delay is ≪ w²/(4vδ) (passive-pair dark-core spots, idea round 3 sonnet, would remove the loop);
  - a named mode multiplexer.
- None of these is ruled out by physics. None is shown.

---

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

## Corrected floor after red team 5 (M13, budget v2.1). Counts trap and pump steered beams

Red team 5 found:
- **Pump beams were left out of the counts.** They are the hardest beams to steer.
- **The "laminar zone" lever was a physics error.** Feed-forward removes position error, not drag.
- **The pair heat factor was too low:** 1.35/η, not 1.02/η.
- **A regression of mine:** core–shell pump absorption had been overwritten in code.
- **Several levers sat at their optimistic ends.**

I verified each item before accepting it. The beams-sum-at-the-cornea correction I had found independently, which cross-validates it.

Steered beams = trap + pump; 405 nm pump; dim lab:

| Target | Optimistic (errors fixed) | **Best estimate** (60 Hz, ≤ 573 K, C_ph 0.85, 1 µm pump jitter, 3 kHz pump focus) | R9-consistent materials |
|---|---|---|---|
| Accent (1 m) | 1 500 | **2 800** | 4 800 |
| Iron-Man sketch (5 m) | 6 600 | **12 200** | 21 000 |
| Film density (30 m) | 27 000 | **50 000** | 87 000 |
| Film-exact, lit room | 27 000 (green) | **50 000–60 000** | none |

**Every column assumes certified safety scheduling**: no two foci of one head on one line of sight. Without it (overlap factor 2 on the summed focus), **nothing is feasible, not even the accent.** Holding a mote still against 0.15 m/s air already needs more than 5 mW summed at its focus.

**Demonstrators (best estimate, M11 `--best`).** Motes run only ~0.2 m/s, so one mote draws only ~7 mm per frame at 30 Hz.

| Demo | Content | Steered beams | Cost today | Integrated (5–10 yr) |
|---|---|---|---|---|
| D1 first glyph | 10 cm circle | 455 | $0.3–2.3 M | $23–114 k |
| D2 arc-reactor UI | 1 m of strokes | 2 300 | $1.6–12 M | — |
| D3 desk Jarvis panel | 3 m of strokes | 6 400 | $4.5–32 M | $0.3–1.6 M |
| D4 Iron-Man sketch | 5 m of strokes | 12 200 | $8.6–61 M | — |

**Hypothetical perfect materials** (k = 0.01, 900 K) cut beams by only ~30 % (M12). The Class 1 trap cap then binds.

**Regulatory lever (M14).** If a certified obstruction interlock earns 30 mW per focus:
- accent ~1 350, sketch ~5 900, film density ~20 300 steered beams;
- this saturates at ~2–2.5× (heat binds above it).

**All levers stacked** (integrated MEMS steering at $50–250 per channel): a sketch room is ~$0.3–1.5 M and a film-density room ~$1–5 M.

**The bench is the critical path** (`08_bench/BENCH_PLAN.md`, gates G1–G4). B1 was re-planned after red team 5:
- skin-absorbing reference spheres;
- a J₁/A input;
- per-track intensity;
- tracer convection subtraction;
- a ΔT series.

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

**4 MET, 5 PARTIAL, 1 NOT MET** (unchanged by red team 5, but R8/R9/R10 now rest on a certified safety-scheduling argument and on ~10³–10⁴-beam machines). v3 had 4 / 4 / 2. MOTE converts R8 from NOT MET to PARTIAL, but only in a designed room, and only if the mote exists.

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

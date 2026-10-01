# Red team 6: light-curtain static voxels (LCSV, M15) and fast POV with the curtain (LCSV-P, M16)

**Scope.** Reviewed on 2026-10-01:
- `09_unlock/T6_unlock_theory.md` (sections 1–3c);
- `09_unlock/m15_lightcurtain_static.py` (`design2`, `optimise`, `main3`, `main4`) with `results/m15*.json`;
- `09_unlock/m16_fast_pov.py` with `results/m16_fast_pov.json` (scope addition from the main session);
- background: T5, `07_mote_route/mote/physics.py`, `results/m4_room_heads.json`, red team 5.

**Method.** All numbers marked *[RT6]* come from `09_unlock/rt6_check.py` (one file, one section per task). Results are in `09_unlock/results/rt6_*.json`, and the full console log is in `results/rt6_run.log`.
- No m15/m16 function is called. Their outputs are read from JSON only for comparison.
- Air properties, drag, heat balance, J₁/A and the design arithmetic are re-implemented independently:
  - Sutherland C1 form;
  - tabulated k_air;
  - Allen–Raabe slip;
  - Gauss–Legendre and Monte-Carlo J₁/A;
  - a continuous optimiser.
- `physics.py` is imported only to cross-check the force law, heat balance and J₁/A.
- **Double validation:**

| Check | Agreement |
|---|---|
| Force law | 0.99–1.00 |
| Mote ΔT | 0.998 |
| Drag | 1.000–1.007 |
| J₁/A: three methods | ≤ 0.6 % |
| Own BHMIE vs Bohren–Huffman test case | Q_ext 3.1050 vs 3.1054; Q_back 2.9242 vs 2.9253 |
| H10 push LP re-derived from the M4 head coordinates | h_worst 2.13 vs 2.14; h_mean 1.355 vs 1.38 |
| Loop model: frequency domain vs time-domain simulation | σ within 1–20 % on the 6 unsaturated configurations |
| Max loop bandwidth: numeric vs analytic 1/(8τ) | within 8–26 % |

Facts from recall are marked **[memory]**. Web sources are listed at the end.

**Severity counts:** 3 critical, 10 major, 9 minor.

---

## Summary

**Arithmetic.** It reproduces: every task-1 quantity is within 5 % of m15, and M16 within 2 %.

**Physics and hardware assumptions.** Three of them fail. Each is decisive on its own.

1. **"Room speed u" is used as the force authority (1.3·drag(u)), but a turbulent draft needs authority ≥ 5.2–5.75 σ_u for < 10⁻⁴ loss/s.**
   - In simulation, motes with 1.3× or 2× authority are lost within seconds.
   - m15's "quiet 0.1 m/s" therefore describes a *still* room, σ_u ≲ 0.024 m/s.
   - At σ_u = 0.1 m/s the heat at gust peaks breaks both motes:
     - white carbon: ΔT 779 K;
     - coated ITO: ΔT 362 K, i.e. 655 K, above its 573 K limit.
2. **The split-control optics do not exist as specified.**
   - **Mode count.** M = A_f/(πr_c²) under-counts the modes a flat-top spot needs by 12× (ρ = 1 λ/NA, η_shape 0.56) to 150× (η_shape 0.8, as m15 assumes).
   - **One DMD per head.** This falls short of the étendue by 75–5 800×.
   - **Crosstalk.** At one intermediate plane, 72–99 % of motes share DMD mirrors with a neighbour's out-of-focus cone, so per-spot amplitude control over ±0.4 m depth fails.
   - **DMD speed.** f_fast = 20 kHz exceeds the only NIR DMD (DLP650LNIR, 12.5 kHz).
3. **Visible side scatter.**
   - Both ITO-on-silica-aerogel and 5 %-carbon aerogel are near index-matched to air (n ≈ 1.04). Their side-scatter efficiency at 90° is q ≈ 1.0–1.3×10⁻³, not the 0.3 and 0.05 used in m15.
   - Without a real white coat, the visible spots must be 18–74 mW, far above the 0.39 mW Class 1 limit.
   - A coat that reaches q ≈ 0.3 costs the ITO mote its FOM edge: 5.3 → about 4.1.

**Corrected outlook** (corrected table at the end):
- **Sketch** with a white-coated ITO-class mote: feasible at 100 W **only in a still room**, and at 1.4–2.7×10¹⁰ hologram modes, not 5×10⁸.
- **Film density:** not feasible at 100 W.
- **Carbon motes:** fail on heat at gust peaks.

**M16.**
- The arithmetic is right.
- The steered-beam saving is overstated:
  - it needs 6–7 beams per mote, not 4;
  - its spot radius is below the diffraction limit at H10's corner throws, so IR power rises 4.5×;
  - its 1 µm motes cannot reach q = 0.3.
- T6 §3c's "holds with a head blocked" entries for normal rooms contradict m16's own output.

### Verdict per claim

| Claim (T6 / m15 / m16) | Verdict | One-line reason |
|---|---|---|
| B2 I_hold formula; size independence | **CONFIRMED** | Model vs closed form 1.068 (hot-gas properties); a skin absorber is size-free |
| B3 ΔT = A·a·I/(4k_g) | **CONFIRMED** | Heat balance reproduces to 0.2 % |
| B4/B5 invariant P·M = N·h·I·A_f/η | **PARTLY** | Algebra right. M counts 1 mode per spot area; a flat-top needs 1.2π²ρ² ≈ 12–150 modes per spot area |
| B6 / jitter = u/(2π·0.1·f_fast) | **REFUTED** (mechanism) | See the bullets below |
| "Drafts enter cubed" (×27 at 0.3 m/s) | **PARTLY** | Holds only when r_c is set by a jitter ∝ u. Loss is set by authority (∝ u, plus peaks); at σ 0.3 the turbulent error grows faster than linear |
| I1 curtain: undetected-intercept and cut-dose arithmetic | **CONFIRMED** | ≥ 10× margin even with the 1 mm limiting aperture [memory] |
| I1 curtain: system behaviour | **PARTLY** | See the bullets below |
| I3 terminated scattering + new stray-light criterion | **PARTLY** | 0.01 cd/m² is a reasonable criterion and is met at leak 10⁻³. Caveats below |
| Carbon-aerogel mote (α, k, FOM, T_max) | **PARTLY** | α 1.2–4.9×10⁵ m⁻¹ and k plausible; FOM band 1.0–3.4 (10 µm, white). Hot face 562 K vs ~623 K mild-oxidation onset |
| I4 split control: DMD at an intermediate field plane | **REFUTED** as specified | Étendue (75–5 800 DMDs per head) and depth crosstalk (72–99 % of motes) |
| Slow LCoS: 10³–10⁴ flat-top spots, efficiency 0.6 | **PARTLY** | See the bullets below |
| Task-1 numbers (the three cases) | **CONFIRMED** (arithmetic) | All within 5 % (table below) |
| T6 4th-pass feasibility: ITO sketch / film in quiet rooms | **REFUTED** as stated | They become still-room-only (sketch) or infeasible (film) once C1–C3 are applied |
| M16 arithmetic | **CONFIRMED** | ≤ 2 % on four rows |
| M16 "~6× fewer steered beams; normal rooms feasible" | **PARTLY** | 1.6× more beams per mote; P_IR ×4.5; q impossible at 1 µm; normal rooms overheat at gust peaks |
| M16 err = (u + 0.02v)/(2π·5 kHz) | **PARTLY** | 5 kHz needs ≤ 15–20 µs total latency. Camera sensing gives 0.45–1 kHz. With PI control, smooth errors shrink, so diffraction binds first |
| M16 "heat is the binding limit" | **PARTLY** | Heat binds only in normal rooms (at gust peaks). Elsewhere, spot diffraction (IR power) and visible scatter bind first |
| T6 §3c occlusion column ("✓ at 1–1.5 µm" in normal rooms) | **REFUTED** | m16's own JSON flags `heat` for every normal-room row at 0.5 m/s, 1–2.5 µm |

Expanded reasons for the longer verdicts:
- **B6 / jitter (REFUTED, mechanism).**
  - With 100–250 µs total latency, the loop's crossover is 0.2–0.7 kHz, not 2 kHz.
  - Drafts are slow (ν₀ 1–23 Hz), so a PID loop holds them to 1–2 µm.
  - Binary DMD pulse-width quantisation (PWM) dominates the jitter, at 3–8 µm.
  - Loss is set by force saturation, not by jitter.
- **I1 curtain, system behaviour (PARTLY).**
  - A single bystander 1.2 m from the image trips 25–30 % of motes into one-head-lost operation, because of beam cuts downstream of the focus.
  - About 3.3 visible spots fall in a 7 mm pupil, together 0.27–1.09 mW.
  - The receivers must cover 2.8–8.9 m² per head.
- **I3 terminated scattering and stray light (PARTLY).**
  - The rule change carries the result: the old 5 % rule fails by 4–21×.
  - Air and aerosol haze equals 3–48 % of the image flux.
  - Dust sparkles appear.
  - The receivers glow.
- **Slow LCoS (PARTLY).**
  - An ideal phase-only multi-spot MRAF hologram puts 0.74–0.78 of the light in the signal region.
  - Within each spot the rms is 24–39 %, with dark points (min/mean 0–0.3).
  - Strong fringing (σ 0.6 px) gives 33 % zero order and 0.26 efficiency.
  - The aperture at 4.75 m reaches 0.25–0.75 m for η 0.8.

---

## Task 1: independent recomputation (H10, cap 100 W, δ = 3 mm)

*[RT6 `repro`.]* The comparison uses m15's chosen spot radii (r_c, r_v). My continuous optimum is given in brackets: m15's 12 %-step grid stops just below the 100 W cap, while the true optimum sits on the cap.

| Quantity | (a) sketch, ITO 5 µm: m15 | (a) RT6 | (b) film, ITO 5 µm: m15 | (b) RT6 | (c) sketch, white carbon 10 µm: m15 | (c) RT6 |
|---|---|---|---|---|---|---|
| FOM (m·K/W) | 5.317 | 5.311 | 5.317 | 5.311 | 2.475 | 2.473 (αa = 3, J₁/A 0.293, A 0.945) |
| I_hold (W/m²), η = 1 unit force | 7.72×10⁵ | 7.77×10⁵ | 7.72×10⁵ | 7.77×10⁵ | 1.61×10⁶ | 1.54×10⁶ (−4.0 %) |
| Mote ΔT (K) / T_m | 74.0 | 73.8 / 367 K | 74.0 | 73.8 / 367 K | 239 | 228 / 521 K (−4.6 %) |
| Jitter (µm) | 7.96 | 7.96 | 7.96 | 7.96 | 7.96 | 7.96 |
| r_c / r_v (µm) | 86.1 / 61.9 | same [92 / 68] | 34.8 / 26.8 | same [38 / 27] | 61.3 / 108 | same [66 / 135] |
| P_focus (mW) | 48.2 | 48.4 | 7.85 | 7.90 | 50.7 | 48.7 |
| 1550 nm total (W) | 86.2 | 86.7 [99.9] | 84.4 | 84.9 [99.9] | 90.9 | 87.2 [99.9] |
| Visible spot / total | 327 µW / 0.909 W | same [390 µW / 1.08 W] | 81.5 µW / 1.36 W | same [1.43 W] | 250 µW / 0.695 W | same [1.08 W] |
| Modes per direction | 4.29×10⁷ | 4.29×10⁷ | 2.63×10⁸ | 2.63×10⁸ | 8.47×10⁷ | 8.47×10⁷ |
| Visible-hologram modes | 8.31×10⁷ | same | 4.45×10⁸ | same | 2.72×10⁷ | same |
| Pixels, all heads | 5.12×10⁸ | 5.12×10⁸ [4.4×10⁸] | 3.08×10⁹ | 3.08×10⁹ [2.7×10⁹] | 8.74×10⁸ | 8.74×10⁸ [7.6×10⁸] |
| ΔT with one head occluded (h 4.47) | 141 | 140 | 141 | 140 | 413 → heat | 397 → heat |

**No discrepancy exceeds 15 %.**
- The largest are −4.6 % (ΔT) and −4.0 % (I_hold, power) in case (c).
- The root cause is the air conductivity at the film temperature: m15's 0.82 power law against the tabulated values, about 2–4 % at 400–530 K, plus slip constants.

**Small items.**
- The T6 B2 closed form under-reads the full model by 6.8 %, because the full model evaluates μ and k at the hot film temperature. This is inside the self-test's 12 % tolerance.
- My H10 occluded p95 is 3.70 (40 random points plus 8 corners) against M4's 4.47 (27-point grid). m15's value is the more conservative one.

---

## Critical

### C1. The draft model: a force authority of 1.3·drag(u) cannot hold a mote in a turbulent draft of rms u

**Evidence.**
- `design2` sizes every beam for F = 1.3·drag(a, u) and treats u as the jitter driver as well.
- The required force tracks the *instantaneous* air velocity: the mote's inertial time is 47 µs (ITO 5 µm) or 136 µs (white carbon 10 µm), against draft time scales of 10–1000 ms.
- When |u(t)| exceeds the authority, the mote drifts at the excess speed for the length of the excursion. At σ 0.1 m/s that is ~10 ms × 0.02 m/s ≈ 200 µm, which is more than r_c, so the mote is lost.

**Rice upcrossing rates** *[RT6 `loop`]*, for an isotropic Kolmogorov (von Kármán + Pao) draft at a fixed point (T5's χ₃ level-crossing form):

| σ_u | L | ν₀ | Required authority for 10⁻⁴ loss/s per mote |
|---|---|---|---|
| 0.03 m/s | 1–10 cm | 0.4–1 Hz | 4.8–5.1 σ |
| 0.1 m/s | 1–10 cm | 1.4–4.5 Hz | 5.2–5.4 σ |
| 0.3 m/s | 1–10 cm | 7–23 Hz | 5.5–5.75 σ |

The loss target is per mote. At 10⁴ motes, 10⁻⁴ /s per mote is still one mote per second, and gusts are correlated over L, so a loss removes a patch of the image, not one dot.

**Time-domain check** (ITO 5 µm, 150 µs latency, σ 0.1, L 1 cm):

| Authority | Frames saturated | Mote motion |
|---|---|---|
| 1.3 σ | 34 % | Wander of tens of mm (lost) |
| 2 σ | 7.8 % | Wander up to 34 mm (lost) |
| 3 σ | 0.44 % | ~12 % of motes per second pass 100 µm (lost) |
| 4.5 σ | ≤ 3×10⁻⁵ | Held: maximum radial error 6 µm (64 levels) / 55 µm (binary) over 580 mote-s |

An earlier, non-deterministic seed showed one 150–440 µm excursion per 580 mote-s at 4.5σ. This is consistent with the per-axis Rice rate, ≈ 0.6 expected events.

**What m15's "quiet 0.10 m/s" can hold.**
- Its authority, 0.13 m/s, holds a draft of σ ≤ 0.024 m/s with zero mean.
- That is a still room, not a "quiet office":
  - offices run a mean of 0.1–0.35 m/s with a turbulence intensity of 20–80 %;
  - the survey average is ~30 % (sources below).

**Consequences** *[RT6 `table`]*.
- The heat has to be checked at the gust peak.
- The laser power can be provisioned near the mean need, because the 360 Hz hologram can follow 1–23 Hz drafts. The DMD then only needs headroom of ~1.5σ. Power-equivalent speed ≈ U + 3.1σ [ESTIMATE].

| Room | White-coated ITO, ΔT at peak | White carbon 10 µm, ΔT at peak |
|---|---|---|
| Still (U 0, σ 0.03) | 139 K | 329 K → **fails** (T_m 622 K > 600 K) |
| Quiet office (U 0.1, σ 0.03) | 207 K | 468 K → **fails** |
| σ 0.1 (the task's draft) | 362 K → **fails** 573 K | 779 K → **fails** |

**Fix.**
- Define each room by (U, σ_u, L). Measure them at the image volume, including a person's thermal plume (0.1–0.25 m/s; T6).
- Size the force for U + 5.3σ and check the heat there.
- Provision power at U + 3σ and count the DMD dump.
- Report the patch-loss rate, not only per-mote loss.

### C2. Split control: the mode count, "one DMD per head" and per-spot amplitude control do not survive étendue and depth

**(a) Flat-top spots need many modes per spot.**
- Model: a band-limited coherent flat-top with plateau radius ρ in units of λ/NA, optimised over soft-edged targets. m15's quantity is η_eq = I_min·πr_p²/P_total *[RT6 `holo`]*.

| ρ | 0.4 | 0.6 | 1.0 | 1.5 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|---|---|
| η_eq | 0.39 | 0.48 | 0.56 | 0.66 | 0.70 | 0.78 | 0.82 |

- m15's η_shape = 0.8 therefore needs ρ ≈ 3.6, i.e. NA = 3.6 λ/r_c.
- Modes per head = A_field·πNA²/λ² = 1.2π²ρ²·(m15's M_dir) = **150× m15** at ρ 3.6 and **11.8×** at ρ 1.0 (where η 0.56 costs 1.43× power).
- The aperture radius at H10's corner throws (3.95–4.75 m) for ρ 3.6:

| Case | Aperture radius |
|---|---|
| Sketch, ITO | 0.25–0.30 m |
| Carbon | 0.36–0.43 m |
| Film | 0.63–0.75 m (larger than the 0.3 m head) |

- **4K LCoS panels (8.8 Mpx), all ten heads, trap holograms only:**

| Case | m15 | RT6 at ρ = 1 (η 0.56) | RT6 at ρ = 3.6 (η 0.8) |
|---|---|---|---|
| Sketch, ITO | ~58 | ~580 | ~7 300 |
| Carbon sketch | ~100 | ~1 140 | ~14 500 |
| Film | ~350 | ~3 500 | ~45 000 |

**(b) One DMD per head cannot carry the étendue.**
- The DLP650LNIR is 1280×800 at 10.8 µm with ±12° tilt, so NA ≈ 0.2 and its étendue is 1.6×10⁻⁵ m²·sr.
- A head addressing ~1.2 m² of field at NA ρλ/r_c needs:

| Case | ρ = 1 | ρ = 3.6 |
|---|---|---|
| Sketch, ITO | 75 DMDs per head | 960 |
| Carbon | 150 | 1 900 |
| Film | 460 | 5 800 |

- Used the other way round: with one DMD per head, the room-side NA is 0.2/85, which forces a plateau radius ≥ ~0.66 mm, i.e. ~60× the IR power at fixed modes.

**(c) Depth crosstalk at the intermediate plane.**
- Synthetic strokes were used: random 3D arcs at δ = 3 mm with N = 1 808 / 10 070, viewed from an H10 corner head and the floor head.
- A spot focused Δz from the plane conjugate to the DMD has a footprint of radius NA·Δz + r_c there.

| Depth planes | Motes whose footprint overlaps another's | Mean overlaps | Median footprint |
|---|---|---|---|
| 1 | 72–99 % | 4–290 | 2–26 mm (each mirror = 0.94 mm in room units) |
| 16 separately relayed planes | 2–80 % | — | — |

- Masking part of a defocused cone also **apodises** that spot's pupil. It reshapes the spot and adds a lateral gradient force; it is not a pure amplitude change.
- T6's own estimate ("~10 px blur at 1/50") is the blur only. It omits the overlap, which is what breaks per-mote independence.

**(d) Speed.**
- The only NIR DMD reaches 12.5 kHz in binary mode [TI], not 20 kHz.
- At 12.5 kHz the binary-PWM jitter is 6–8 µm (C1 and M1 below).

**Fix.**
- Count modes as A·πNA²/λ² with NA from the required flat-top.
- Budget DMDs by étendue, or drop the DMD and modulate per beam group.
- If a DMD remains, show a per-mote control law that works with shared footprints, or restrict content depth to |Δz| ≲ δ/(2NA) per relayed plane, i.e. 16+ planes with their own relays.

### C3. Side scatter: the motes as specified are nearly invisible from the side

**Mie results** *[RT6 `mie`]*. Own BHMIE at 500 nm. q_iso(θ) = 4π(dC/dΩ)/(πa²), averaged over ±5°:

| Mote | n at 500 nm | q at 30° | q at 90° | q at 150° | m15 q_side |
|---|---|---|---|---|---|
| ITO on silica aerogel, 5 µm | 1.04 + 10⁻⁴i | 0.30 | **1.3×10⁻³** | 8×10⁻⁴ | **0.3** |
| ITO aerogel, 1 / 1.5 µm (M16) | 1.04 + 10⁻⁴i | 0.24–0.27 | **2.9–3.2×10⁻³** | 1.6×10⁻³ | **0.3** |
| 5 % carbon aerogel (MG of 1.95 + 0.79i), 5–10 µm | 1.043 + 0.019i | 0.09–0.15 | **1.0×10⁻³** | 5×10⁻⁴ | **0.05** |
| Dense black carbon, 5–10 µm (reference) | 1.95 + 0.79i | 0.42–0.47 | 0.18 | 0.16 | — |
| Solid TiO₂ 1 µm (reference) | 2.6 | 1.8 | 0.84 | 0.83 | — |

**Why.**
- The ITO-aerogel mote was *designed* to be visible-transparent, for the v4 phosphor.
- A 95 %-porous carbon aerogel is index-matched to air within 4 %.
- Both throw their light forward, into the receiver.

**Consequences.**
- Keeping m15's luminance with the uncoated ITO mote needs visible spots of **74 mW (sketch) / 18 mW (film)** each, 50–190× the 0.39 mW Class 1 limit.
- The visible totals then reach **~200–300 W** (1 667 × 74 mW or 10 000 × 18 mW, divided by efficiency 0.6), failing the exit window and the wall-light criterion by two orders of magnitude.

**The white coat.**
- A diffuse coat of albedo R gives a Lambertian-sphere phase function:
  - q = 0.85R at 90° phase;
  - q = 0.29R at 120°;
  - q = 0.04R at 150°.
- q ≈ 0.3 at side angles therefore needs R ≈ 0.35. In Kubelka–Munk terms, a coat of 0.6 × the transport mean free path:
  - ~0.5 µm of dense TiO₂ (l* ≈ 0.5–1 µm, [memory]);
  - 2–6 µm of porous silica, so m15's "thin porous white silica shell" is optimistic.
- Viewers on the far side of the illumination see 3–25× less light. **Each mote needs two roughly opposed illumination beams.** This doubles the visible spot count and M_vis.
- **For the ITO mote the coat costs its advantage.** Applying m15's own coat penalty (J₁ ×0.9, k +0.015) gives FOM 5.3 → 4.1, and it adds a coat that must survive 573 K.

**Fix.**
- Replace q_side with q(θ) from Mie, or from a measured coated sphere.
- Give the ITO mote the coat penalty, or a phosphor.
- Carry two illumination beams per mote.

---

## Major

### M1. Jitter: the right mechanism is quantisation plus latency, not u/(2π·0.1·f_fast)

The loop model *[RT6 `loop`]*:
- **Mote:** overdamped, with inertial time τ_p = 47 µs (ITO 5 µm) or 136 µs (white carbon 10 µm).
- **Force lag:** first-order, from the l = 1 thermal mode of the sphere (gas-side flux 2k_g/a): 9 µs and 19 µs. This matches the brief's 10–30 µs.
- **Loop:** a discrete PID tuned for each case (modulus margin ≤ 2, closed-loop poles checked) with 2–5 frames of total latency.
- **Actuator:** ternary or 64-level DMD force with first-order error feedback, saturating at 4.5σ.
- **Turbulence:** von Kármán + Pao drafts.

The frequency-domain result is checked by a time-domain simulation (100 motes × 3 axes × 6 s per case; σ agrees within 1–20 %).

**Findings.**

1. **Achievable crossover.**
   - 0.2–0.7 kHz for 100–250 µs latency, not the 2 kHz that m15's formula uses.
   - The maximum P-loop crossover at ≤ 2 margin is 1.05 / 0.70 / 0.45 kHz at 100 / 150 / 250 µs, and the analytic 1/(8τ) agrees.
   - 2 kHz needs ≤ ~50 µs total latency.
   - Event-camera pixel latency alone is 100–220 µs (IMX636).
2. **Draft-driven error is small.** The draft spectrum dies above 40–200 Hz (Kolmogorov scale η = 0.2–1.7 mm). With integral action, σ_turb is:
   - 1–2 µm at σ_u 0.1;
   - 4–34 µm at σ_u 0.3 with L = 1 cm and 150–250 µs latency.
3. **Binary PWM dominates at σ_u 0.1.** It contributes 3–4 µm at 20 kHz and 6–8 µm at 12.5 kHz. It scales with the authority, so C1's larger authority makes it worse.
4. **Flat-top radius for < 10⁻⁴/s jitter loss** (r_c ≥ a + b·σ, with b from Rice at ν ≈ f_c):

| Case | 20 kHz binary | 12.5 kHz NIR DMD, binary | 64 levels | m15 |
|---|---|---|---|---|
| ITO 5 µm, σ_u 0.1 | 30–34 µm | 50–55 µm | 8–17 µm | 24 µm |
| ITO 5 µm, σ_u 0.3 | 91–206 µm | 159–245 µm | 17–193 µm | 72 µm |
| White carbon 10 µm, σ_u 0.1 | 28–34 µm | 45–51 µm | 13–25 µm | 30 µm |

**Verdict.** The jitter formula is wrong in mechanism. Its σ_u 0.1 number happens to fall within 2× of the binary-DMD result. The real limits are authority (C1), quantisation and diffraction (C2).

### M2. Multi-spot flat-top holography: efficiency 0.6 is plausible, flatness is not

*[RT6 `holo`; MRAF (Pasienski–DeMarco) with 40 soft flat-top spots on a 256² phase-only SLM, 8-bit.]*

| Spot size | Fringing σ | Light into signal regions | Into plateaus | Rms within a spot | Min/mean | Zero order |
|---|---|---|---|---|---|---|
| 7–28 resolution cells | none | 0.74–0.78 | 0.50 | 24–39 % | 0.0–0.3 | ~10⁻⁵ |
| 7–28 resolution cells | 0.3 px | 0.74–0.77 | 0.50 | — | — | 1.6×10⁻⁴ |
| 7–28 resolution cells | 0.6 px | 0.26–0.28 | — | — | — | 33 % |

- With no fringing, there are vortex-like dark points inside spots, with random or smooth initial phase.
- 0.6 px of fringing (fly-back of the wrapped phase) gives 33 % zero order and 37–39 % spot-to-spot spread, until it is compensated.
- **Literature:** high-accuracy continuous MRAF patterns reach ~0.6 % rms only at a few % efficiency (a ring trap at 3 %).

**Consequences.**
- m15's η_shape 0.8 at 3a ≤ r_c needs ρ ≈ 3.6 and conjugate-gradient-class holograms. Expect a usable η_shape of 0.4–0.6 with 0.6 overall efficiency, or the reverse.
- **Zero order.** At 100 W total and 1–5 % zero order per tile, 0.1–0.5 W per head is focused near the axis. It must be blocked in a Fourier plane, and blocking it also removes the field near the axis.
- **Higher orders** from the pixel grid land at d·λ/p ≈ 1.6 m (3.74 µm pitch, 3.95 m throw), on walls and people. Each head needs a hard field stop.

### M3. Carbon-aerogel mote: the absorption is right, the margins are thin

| Property | Value | Notes |
|---|---|---|
| α at 1550 nm, 5 % carbon | 1.2×10⁵ (Maxwell–Garnett, isolated grains) to 3.2–4.9×10⁵ m⁻¹ (linear 5 % × bulk, connected network) | Literature IR mass extinction 2.6 m²/g at 3–5 µm, i.e. 2.6×10⁵ m⁻¹ at 100 kg/m³. m15's 3×10⁵ is central |
| FOM band, white-coated | **1.0–3.4** (10 µm), **0.5–2.4** (5 µm) | Over α 1.2–4.5×10⁵ and k 0.03–0.08. m15: 2.5 and 1.6 |
| k_eff | Bulk 0.015–0.03 W/m/K at room temperature; 0.026 at 200 °C; ~0.054 at 300 °C (literature) | m15's 0.045 (+0.01 coat) is mid-band at the mote's 400–530 K. The micron-scale value is unmeasured (T6 agrees) |
| Oxidation | Carbon aerogels show mild oxidation in air from ~350 °C (623 K) in TGA | Hot face (T_m + 1.33·T₁): see below |

**Hot-face temperatures for case (c).**

| Condition | Mean T_m | Hot face |
|---|---|---|
| Normal operation | 521 K | **562 K** |
| One head occluded | 690 K | **731 K** |
| Still-room gust peaks | ~622 K | ~660 K |

Hours-long life at ≥ 560 K for a 500 m²/g carbon in air is not established. It belongs in bench B2.

**ITO.**
- Air annealing at 250–350 °C fills oxygen vacancies and kills the plasmon (literature).
- m15 uses T_max = 600 K for ITO, m16 uses 573 K. Use ≤ 573 K at the hot face.

### M4. Curtain receivers and bystanders

**Landing zones.** Beams that pass through the 1 × 1 × 0.8 m volume from each H10 head end on walls, floor or ceiling over a bounding box of **2.8–8.9 m² per head** *[RT6 `stray`]*. "Every beam ends on a receiver" therefore means large black receiver patches, not head-sized ones.

**Bystanders.**
- The curtain sees a person *downstream* of a focus as a beam drop. With people standing 1.2 m from the image centre (head sphere plus torso):

| People | Trap beams cut downstream | Motes that lose ≥ 1 head |
|---|---|---|
| 1 | 4–5 % | **25–30 %** |
| 2 | 8–10 % | **55–66 %** |
| 6 | 24–30 % | 78–85 % |

- These motes run in the occluded state (h up to 4.47). That is fine for ITO in still air, but **carbon motes overheat** (T6's own "local dropout near hands", now caused by every viewer).
- **Fix.** A downstream intercept is harmless: the beam has diverged to tens of mm. Telling upstream from downstream intercepts needs a second, safety-rated person-location sensor in the safety case.

### M5. Per-spot visible power summed in the pupil

- With δ = 3 mm, a 7 mm pupil inside a stroke intercepts ~3.3 illumination beams.
- Together that is **1.09 mW (a) / 0.27 mW (b) / 0.83 mW (c)**, so (a) and (c) exceed the 0.39 mW Class 1 limit. m15's per-spot `vis_spot_class1` check is not sufficient.
- The visible beams therefore also depend on the curtain. The cut dose is fine: ~1.5 µJ against ~5 µJ.

### M6. Missing optical efficiencies

- m15 divides only by the hologram efficiency (0.6). The fast amplitude plane is a DMD:
  - window 0.93 [TI];
  - fill and diffraction efficiency ~0.7 [ESTIMATE];
  - relay ~0.9.
  The extra factor is ≈ 0.6, so IR and visible powers rise **×1.7**.
- m16 sets P_IR = N·h_mean·P_unit with **no optical efficiency at all**. Steered channels (AOD/galvo plus relays) run 0.5–0.8.

### M7. T6 §3c misreads m16 on occlusion

- T6 §3c says "✓ at 1–1.5 µm" (sketch, 0.5 m/s, quiet/calm/**normal**) and "✓ at 1.5 µm" (film, **normal**).
- `m16_run.log` shows otherwise:
  - occluded ΔT 282–347 K → `heat` for every normal-room row (my recomputation: 283–348 K);
  - calm 1.5 µm also fails (293 K).
- Only quiet rooms (1–1.5 µm) and calm at 1 µm hold with a head blocked.

### M8. M16: the spot radius is below the diffraction limit at H10's throws

- H10's eight corner heads throw 3.9–4.75 m (my geometry: 0.90–4.75 m over the volume).
- With R_head = 0.3 m, a plateau of ρ = 1 λ/NA (η 0.56) needs r_c ≥ ρλd/R:

| Throw | ρ = 1 | ρ = 3 (η ≈ 0.78) |
|---|---|---|
| 1.25 m | 6 µm | 19 µm |
| 3.95 m | 20 µm | 61 µm |
| 4.75 m | 25 µm | 74 µm |

- m16 uses r_c = 11.5 µm (quiet, v = 1 m/s).
- Corrected to 20 µm at η 0.56 *[RT6 `m16`]*:
  - sketch: P_IR 4.0 → **18 W**, P_focus 12 → 54 mW;
  - film quiet: 16.6 → **75 W**;
  - film normal (a = 1.5, v = 0.5): 147 → **209 W**.

### M9. M16: beams per mote and the tracking loop

**Beams per mote.**
- "3 active pushes + 1 light" is the LP vertex. Gust rejection in any direction needs a positively spanning set, ≥ 4 beams (RT5 M2), plus make-before-break hand-over.
- The forward-peaked 1 µm scatter (q(30°)/q(90°) ≈ 90) needs two illumination beams per mote.
- Total ≈ 6–7 per mote, **×1.6**:

| Content | m16 steered beams | RT6 |
|---|---|---|
| Sketch, 1 m/s | 2.1k | 3.4k |
| Film, 1 m/s | 8.7k | 14k |
| Film normal, 0.5 m/s | 17k | 28k |

**Tracking loop.**
- err = (u + 0.02v)/(2π·5 kHz) is a P-loop steady error.
- 5 kHz needs ≤ 15–20 µs total latency: maximum crossover 4.4 kHz at 20 µs, 2.0 kHz at 50 µs. That is per-channel analog sensing (quadrant detectors), not cameras.
- With camera latency (150 µs → 0.70 kHz), the same formula gives r_c 82–210 µm and P_IR 0.3–10 kW.
- With integral action, smooth errors (drafts at 1–23 Hz, a 2 % feedforward residual rotating at v/(2πR) ≈ 2–8 Hz) are rejected far better. My static-voxel analysis gives 1–2 µm. So diffraction (M8) binds first.
- The latency still has to be designed: event-camera pixel latency is 100–220 µs.

### M10. M16: heat is not the only, or even the first, binding limit

**Normal rooms.** If "normal 0.3 m/s" is σ_u = 0.3, the gust peaks (5.4σ) push T_m to:
- 641 K (sketch, 1 µm, v = 0.5);
- 717 K (film, 1.5 µm).
Both exceed 573 K. Heat does bind here, and it fails.

**Quiet rooms.** Gust peaks add only ~60 K (491 → 557 K at v = 1). The motion dominates the drag, which is a genuine strength of POV.

**The visible side binds first.** At q = 3×10⁻³ (uncoated 1 µm ITO aerogel) a tracked spot needs **65–217 mW**. A 1 µm mote cannot carry a meaningful diffuse coat (the coat would have to be thinner than the transport length). A dense high-index scatterer (TiO₂ q 0.84) has k ≫ 1 W/m/K and destroys the FOM.

**Visible versus the curtain** (taking m16's own 0.69–2.31 mW at q = 0.3):

| Check | Result | Verdict |
|---|---|---|
| Undetected 2 % | 14–46 µW | Below 0.39 mW, OK |
| Cut dose | 1.0–3.2 µJ vs 5.0 µJ | OK |
| At 3 mW | 4.2 µJ | 85 % of the limit |
| Exit window as m16 computes it (P_vis/10 heads) | — | Assumes every head illuminates. With 1–2 illumination heads, film normal (5.9 W) fails the 1.43 W limit |

---

## Minor

1. **Stray-light criterion (I3).** The change from "≤ 5 % of image flux" to "≤ 0.01 cd/m² added" carries the result *[RT6 `stray`]*.

   | Case | Leak (10⁻³) as % of image flux | Old rule | Added wall luminance |
   |---|---|---|---|
   | (a) | 106 % | Fails 21× | 1.0×10⁻³ cd/m² |
   | (b) | 20 % | Fails 4× | 1.5×10⁻³ cd/m² |
   | (c) | 81 % | Fails 16× | 0.8×10⁻³ cd/m² |

   - The new numbers are comparable to the wall light the image's own flux adds (1–8×10⁻³). I accept the new criterion for a lit room.
   - Three items are unaccounted for:
     - **Air and aerosol haze.** Rayleigh 1.4×10⁻⁵ m⁻¹ plus indoor aerosol 2×10⁻⁵–10⁻⁴ m⁻¹ [memory], over 4 m paths, gives 3–48 % of the image flux as a cyan haze along the beam bundles (0.5–2.7×10⁻³ cd/m²).
     - **Dust sparkles.** Particles > 1 µm at 10⁵–10⁷ m⁻³ [memory] crossing the bright part of the spots give ~1–100 concurrent sparkles for ITO spots, and 10–1 000 for the carbon case's 108 µm spots. They are as bright as motes.
     - **Receiver glow.** 0.17–0.34 cd/m² on a 0.6 m receiver, or 0.012–0.024 cd/m² spread over 4 m².
   - A leak of 10⁻³ over multi-m² patches needs light-trap-grade black (Vantablack-class 4×10⁻⁴, black velvet ~10⁻²) [memory].
2. **Dotted lines.** δ = 3 mm subtends 10.3 arcmin at 1 m, well above the ~1 arcmin acuity, so static-voxel "lines" look beaded within ~3–10 m. Each dot is ~10⁻⁵ cd, i.e. bright points. This is a perception issue that the luminance bookkeeping (4π·L·1 mm·S) hides.
3. **The mote's own extinction against θ_det.** Extinction (Q ≈ 2, with the diffraction lobe wider than the beam) is 2×0.8(a/r_c)²:
   - 0.5 % (a), 3.3 % (b), 4.3 % (c);
   - 18 % for 10 µm carbon at r_c 30 µm.
   A 2 % trip threshold needs per-beam baselines that track mote jitter and motes passing through other beams' cones.
4. **Corneal aperture.** For t < 0.35 s the 1400 nm–100 µm limiting aperture is 1 mm, not 3.5 mm [memory]. The cut-dose limit at 0.1 J/cm² becomes 0.785 mJ instead of 9.6 mJ. The design (≤ 0.068 mJ) still has ≥ 11× margin. The standards question belongs to the other agent.
5. **Optimiser.** The cost optimum sits on the 100 W cap; m15's 12 % grid lands 9–16 % below it. This is harmless, but "86 W" is a grid artefact. The cost optimum is "at the cap".
6. **Inconsistent T_max for ITO:** 600 K in m15, 573 K in m16.
7. **Hologram compute.** 10⁹–10¹⁰ pixels at 360 Hz with 10³–10⁴ flat-top spots and iterative (MRAF/CG) refinement is unbudgeted. It is a GPU-cluster-class load [ESTIMATE].
8. **Visible-exit-window check.** m15 compares the total P_vis with one head's limit (1.43 W); m16 divides by 10 heads. Pick one, according to which heads illuminate.
9. **"Drafts enter cubed".** This holds only while r_c is set by a jitter ∝ u. With fine amplitude levels, r_c is set by 3a or by diffraction, and power scales ∝ u (plus the peak factor of C1).

---

## Corrected design table

**Assumptions** *[RT6 `table`, `m16`]*. Each is the most favourable defensible choice:
- flat-top ρ = 1 (η_shape 0.56, modes ×11.8);
- extra DMD and relay efficiency 0.6;
- white-coated ITO: FOM 4.1, T_max 573 K, q 0.3;
- r_c floor from the binary 12.5 kHz NIR-DMD loop model, scaled with the authority;
- heat at U + 5.4σ;
- power at U + 3.1σ;
- H10, 100 W cap, cost-optimised;
- prices as m15 [ASSUMPTION].

### LCSV (static voxels)

| Case / room | r_c | ΔT at peak | 1550 nm | Visible | Hologram modes, all heads | Cost, volume / lab | Verdict |
|---|---|---|---|---|---|---|---|
| (a) sketch, m15 as published | 86 µm | 74 K | 86 W | 0.91 W | 5.1×10⁸ | $37k / $0.78M | (as claimed) |
| (a) sketch, still room (U 0, σ 0.03) | 55 µm | 139 K | 100 W | 1.43 W | **1.4×10¹⁰** | $0.45M / $16M | Feasible, at 27× the modes |
| (a) sketch, quiet office (U 0.1, σ 0.03) | 38 µm | 207 K | 100 W | 1.43 W | 2.7×10¹⁰ | $0.84M / $30M | Feasible, at 53× the modes |
| (a) sketch, σ 0.1 | 65 µm | 362 K | 460 W | 1.43 W | 1.0×10¹⁰ | — | **Fails** (cap, heat) |
| (b) film, m15 as published | 35 µm | 74 K | 84 W | 1.36 W | 3.1×10⁹ | $114k / $3.6M | (as claimed) |
| (b) film, still room | 23 µm (floor) | 139 K | 106 W | 1.43 W | 8×10¹⁰ | $2.5M / $92M | **Fails** cap (just) |
| (b) film, quiet office | 23 µm | 207 K | 217 W | 1.43 W | 8×10¹⁰ | — | **Fails** cap |
| (b) film, σ 0.1 | 65 µm | 362 K | 2.8 kW | 8.6 W | — | — | **Fails** |
| (c) carbon sketch, m15 as published | 61 µm | 228 K (RT6) | 87 W | 0.69 W | 8.7×10⁸ | $48k / $1.2M | (as claimed) |
| (c) carbon sketch, still room | 44 µm | 329 K | 100 W | 1.43 W | 2.0×10¹⁰ | — | **Fails** heat at peaks (622 K > 600 K) |
| (c) carbon sketch, quiet office / σ 0.1 | — | 468–779 K | 100–585 W | — | — | — | **Fails** |

### LCSV-P (M16, ITO 1–1.5 µm)

| Case | M16 claims | RT6 corrected (diffraction ρ 1 at 3.95 m, 6.5 beams per mote; q 0.3 assumed achievable) | If q = Mie value for the uncoated mote |
|---|---|---|---|
| Sketch, quiet, 1 µm, 1 m/s | 2.1k beams, 4 W IR, 0.69 mW visible spots | **3.4k beams, 18 W, P_focus 54 mW**; gust peaks 557 K, OK | Visible spots 65 mW, **fails** |
| Film, quiet, 1 µm, 1 m/s | 8.7k beams, 17 W | **14k beams, 75 W** | Spots 87 mW, **fails** |
| Sketch, normal, 1 µm, 0.5 m/s | 4.2k beams, 39 W | 6.8k beams, 55 W; **641 K at gust peaks (σ 0.3), fails** | Fails |
| Film, normal, 1.5 µm, 0.5 m/s | 17k beams, 146 W | 28k beams, 209 W; **717 K at peaks, fails** | Fails |

**Bottom line.**
- LCSV-H reaches the Iron-Man sketch only with all three of the following:
  - a still (σ ≲ 0.03 m/s) zone;
  - a coated ITO-class mote that has never been made;
  - ~10¹⁰ hologram modes.
- Film density does not fit 100 W in any room.
- LCSV-P is the more promising half. It keeps a ~3.5× beam reduction against v4 (rather than 6×) in quiet rooms, but only if a 1 µm mote can be made visible from the side. That is the new gating material question.

---

## What to fix first (value of information)

1. **Draft characterisation** at the image volume: U, σ_u and L, including people. This decides C1 for every variant.
2. **A side-scatter measurement** on a coated mote, both a 1 µm and a 5–10 µm candidate. q(θ) and the coat's ΔFOM decide C3 and M10.
3. **A spot-forming bench:** one LCoS tile with 100 flat-top spots at 4 m. Measure η_shape, dark points, zero order and fringing efficiency (C2, M2).
4. **The DMD question.** Either show a per-mote control law that tolerates shared footprints, or drop the intermediate-plane DMD in favour of per-beam-group modulation and count the channels honestly.

## Sources (web, this review)

- Carbon aerogel oxidation onset in air (~350 °C mild oxidation; coated carbon to ~600 °C): USPTO 10008338 "High temperature oxygen treated carbon aerogels" (https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10008338).
- Carbon aerogel thermal conductivity and IR mass extinction:
  - https://link.springer.com/article/10.1007/s10934-011-9504-7
  - https://link.springer.com/article/10.1007/s10765-009-0595-1
  - https://www.sciencedirect.com/science/article/abs/pii/S0022309324000760 (MEC 2.62 m²/g at 3–5 µm)
- Indoor air speed and turbulence intensity (0.1–0.5 m/s mean, TI 20–80 %, survey mean ~30 %):
  - https://www.researchgate.net/publication/13555630_A_Survey_of_Wind_Speeds_in_Indoor_Workplaces
  - https://www.sciencedirect.com/science/article/abs/pii/S0360132317305279
- ITO plasmon loss on air annealing:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC13425322/
  - https://arxiv.org/pdf/2211.04144
- DLP650LNIR (800–2000 nm, 1280×800, 10.8 µm, ±12°, 12.5 kHz binary, window > 93 %): https://www.ti.com/product/DLP650LNIR
- 1550 nm LCoS (Hamamatsu X15213, Holoeye GAEA-2.1 TELCO):
  - https://www.hamamatsu.com/us/en/product/optical-components/lcos-slm/high_power_laser_type/X15213-15L.html
  - https://holoeye.com/products/spatial-light-modulators/gaea-2-phase-only/
- MRAF accuracy against efficiency (0.6 % rms at 3 % of light in the trap, ring trap):
  - https://arxiv.org/html/1008.2140
  - https://ar5iv.labs.arxiv.org/html/1408.0188
- Event-camera latency (IMX636, 100–220 µs): https://www.prophesee.ai/event-based-sensor-imx636-sony-prophesee/

# Red team 5: MOTE v2, the R12 room rig and the "floor" claims

**Scope.** Reviewed on 2026-10-01:
- `mote/physics.py` (v2) and `mote/budget2.py`
- `safety.py`, which has not changed since red team 4 reviewed it (Sep 30 16:44)
- the M4, M5, M7, M8, M8b and M8c scripts with their results and logs
- RESULTS.md, the T5 v2 box, FINAL_VERDICT v4 with the floor table, and R8/R9
- BENCH_PLAN, `analyze_b1.py` and `track_b1.py`
- red team 4's report, item by item

**Method.** Numbers marked *[RT5]* were computed for this review. The scripts are in the session scratchpad (`…/scratchpad/rt5/`) and are not committed:

| Script | What it does |
|---|---|
| `r1_repro.py` | Reproduces the floor points with every intermediate value |
| `r2_hotface.py` | Full spherical-harmonic surface temperature |
| `r3_m4.py` | R12 pairs, hemisphere sums, 4-channel push |
| `r5_pairs_v.py` | Exact cost of a misaligned pair |
| `r4_sens.py` | Single-factor sensitivities |
| `r6`, `r8`, `r11` | Combined scenarios |
| `r9_bench.py` | B1 checks |
| `r10_occl.py` | Occlusion and the workbench |

`b2x.py` is a copy of `budget2.py` with extra parameters added for the sensitivity runs (pair-cost fit, throw, convergent sum, focus-tracking bandwidth, quench law, gas temperature, pump core model, k_eff offset) and a 5 % speed grid. With the default arguments it reproduces `budget2` exactly. Facts from recall are marked **[memory]**.

**Reproduction.** `budget2` reproduces every M8/M8c floor point exactly:
- accent, pairs: 340 channels;
- sketch, pairs: 1 490;
- film density, pairs: 6 138;
- film-exact green ×4: 6 138 + 12 276 pump;
- film-exact cyan ×4: 10 508.

Validation still gives 31/32, and both bench self-tests pass.

**Severity counts:** 2 critical, 10 major, 10 minor.

---

## Summary verdict on the floor claims

The FINAL_VERDICT floor reads "fewest steered beams":
- accents 340–420;
- sketch 1 500–1 800;
- film density 6 100–7 600;
- film-exact 6 100 green / 10 500 cyan.

**Is the arithmetic right?** Yes. Under the lab's own assumptions the numbers are even ~7 % pessimistic, because the speed grid is coarse (20 % steps). On a 5 % grid they become 314–387 / 1 377–1 699 / 5 673–7 001 / 5 957 / 9 704.

**Are they floors?** No, and they are not steered-beam counts:
1. They count trap channels only. Pump channels add 1–3 × N more, and these are the hardest beams in the system (critical C1).
2. They stack the favourable end of every uncertain input:
   - C_ph = 1.0;
   - 45 Hz;
   - T_face 600 K on an ITO skin;
   - scheduler-enforced no-overlap;
   - 405 nm absorption of 1 500 cm⁻¹ in a dispersed aerogel;
   - k_eff 0.04.
3. They contain modelling errors:
   - mean flow treated as free;
   - misaligned-pair cost;
   - convergent 1550 nm power for push;
   - core–shell pump model never used.

**My corrected ranges** are in §"Floors: corrected ranges". In short, the claims are **optimistic by 1.4–5× in trap channels and 3–10× in steered beams**. The upper end of each range applies if the mote's material numbers regress to R9's own estimates.

---

## Critical

### C1. The "steered beams" floor omits the pump channels, which outnumber the trap channels

**Evidence.**
- `budget2` reports `channels = N × beams` (trap only) and `pump_channels = N × n_pump` separately.
- M8 and M8c print both. FINAL_VERDICT quotes only the first, under the heading "Fewest steered beams".

**Counts** *[RT5, r1/r6]*:

| Target | Trap channels | Pump channels | Steered beams | Ratio to the claim |
|---|---|---|---|---|
| Film-exact green (×4) | 6 138 | 12 276 | **18 400** | 3× |
| Film-exact cyan ×6 (the lab's pick) | 10 508 | 31 523 | **42 000** | 4× |
| Film-exact cyan ×2 | – | – | 21 000 | – |
| Film density | 6 138 | 6 138 | **12 300** | 2× |

The cyan ×2 option runs 38.5 µW per pump beam, 99 % of the 39 µW AEL.

**The pump channels are also the hard ones.**
- w_p = 2.2 µm, z_R = 30 µm (with M²), at 2 m.
- Pointing must hold ≤ 0.5 µm jitter, i.e. ≈ 0.25 µrad rms per axis per channel.
- Focus must track the mote within ±z_R/2 over a ±0.5 m depth: B_focus ≥ v/(π z_R) ≈ 5–6 kHz at v = 0.5 m/s.
- Each channel aims at the mote itself, which in a doughnut sits 0–3 µm off the trap axis depending on load. Pump beams therefore cannot simply ride on the trap channel.

**Fix.** Report trap + pump. If the floor table means "trap beams", say so, and add a pump-channel column with its pointing, focus and turbulence specification.

### C2. The floors are presented as a "physics floor" but are an optimistic design point; several levers are errors, not levers

NOTEBOOK Entry 18 says: "This is the physics floor. It is set by the heat-force identity." The numbers in fact depend on the items below. Majors M1–M10 give the evidence for each.

| Lever or input | Status | Effect on channels *[RT5, single factor, fine grid]* |
|---|---|---|
| Laminar zone with mean-flow feed-forward (u_air = 0.05) | **Physics error.** Feed-forward cancels position error, not drag (M3) | +10 % (U = 0.05 counted) to +27 % (U = 0.1) |
| C_ph = 1.0 | Top of the lab's own range [0.67, 1.04] | 0.85 → +28 %; 0.67 → +55 % |
| 45 Hz | No psychophysics; RT4 Major 9 and `budget2`'s own docstring say 60 Hz | +33 % |
| T_face 600 K on an ITO skin | Inside R9's degradation band, 573–623 K (M8) | +10–16 % |
| No overlap (k = 1) by scheduling | Not certifiable as stated; conflicts with stroke-aligned pairs (M6) | +55 % at R = 0.15 m, or 0.4 m optics |
| α₄₀₅ = 1 500 cm⁻¹ through an aerogel mote | Above R9's dense-phosphor estimate (M4) | Film-exact green +63 %; cyan becomes infeasible |
| k_eff 0.04 | Ignores phosphor loading, skin conduction and the micron-aerogel risk R9 names (M4) | +0.03 → +22 % |
| Gas properties at T_film in the force | Untested at ΔT ≈ 220–300 K (M10) | Ambient-property bound: +71 % |

**Fix.** Rename the M8 output "optimistic design point (lab levers)". Report the band defined in the next section.

---

## Floors: corrected ranges

Scenario definitions:
- **A.** The lab's model on a 5 % speed grid.
- **B.** Errors fixed, everything else kept:
  - exact misaligned-pair cost 1.175/η;
  - P_beam at the longest R12 throw (2.25 m);
  - convergent 1550 nm power summed for push (1.87×);
  - push needs 4 channels per mote;
  - focus tracking at 3 kHz;
  - core–shell pump model switched on.
- **B1.** B plus a mean flow U = 0.10 m/s counted (u_air = 0.15).
- **B4.** B1 plus T_face ≤ 573 K, 60 Hz and C_ph = 0.85.
- **C (central).** B4 plus:
  - k_eff + 0.02;
  - α₄₀₅ 500 cm⁻¹ for a dispersed-phosphor aerogel, or 2 000 cm⁻¹ for a dense core;
  - Arrhenius quench (Ea 0.4 eV, fitted to −4.2 % at 150 °C);
  - 0.85 µm pump jitter.

Cells give trap channels, with total steered beams (trap + pump) in brackets. *[RT5: r6, r8]*

| Target | Lab claim | A | B | B1 | B4 | C |
|---|---|---|---|---|---|---|
| Accent | 340–420 | 314 | 382 (763) | 487 (974) | 959 (1 919) | 1 723 (3 446) |
| Sketch | 1 500–1 800 | 1 377 | 1 674 (3 347) | 2 136 (4 272) | 4 208 (8 416) | 7 557 (15 113) |
| Film density | 6 100–7 600 | 5 673 | 6 896 (13 792) | 8 801 (17 603) | 17 338 (34 677) | 17 338 (34 677) |
| Film-exact, green | 6 100 | 5 957 | 7 241 (21 723 at ×4) | 9 242 (18 483) | 17 338 (34 677) | 32 694 (65 388) |
| Film-exact, cyan | 10 500 | 9 704 | 10 698 (21 396) | 15 053 (30 107) | 32 694 (65 388) | **infeasible** |

The pessimistic-plausible set adds:
- C_ph 0.67;
- 550 K;
- u_air 0.15;
- k_eff + 0.04;
- α 300 / 1 000 cm⁻¹;
- the pair cost at full coverage (1.35/η).

With it, nothing is feasible except film density through green motes, at about 150 k trap channels.

**My best corrected ranges** (B1 to C):

| Target | Trap channels | Steered beams |
|---|---|---|
| Accent | ~0.5–1.7 k | ~1–3.4 k |
| Sketch | ~2.1–7.6 k | ~4.3–15 k |
| Film density | ~9–17 k | ~18–35 k |
| Film-exact, green | ~9–33 k | ~18–65 k |
| Film-exact, cyan | ~15–33 k, or infeasible | ~30–65 k |

---

## Major

### M1. The pair heat factor h_worst = 1.02/η is optimistic. It ignores beam misalignment and pair coverage, and the rig loses 8 % of motes, not 1 %, when one head is blocked

**The fit vs M4 itself.** The M4 JSON for R12 already reports `lateral_pairs_worst: Infinity`, so some positions have no pair at all. The fit silently used the finite points. At the design η = 0.3656 (a = 2.5 µm, w = 8.55 µm), M4's own cost gives *[RT5, r3]*:

| Quantity | M4 at η = 0.3656 | `budget2` fit | Fit error |
|---|---|---|---|
| Worst | 1.065/η | 1.02/η | 4 % optimistic |
| Mean | 2.27 | 0.5 + 0.58/η = 2.09 | 8.6 % optimistic |

**Misalignment.** M4 accepts pairs up to 25° from antiparallel, but its cost |u·e| + |u⊥|/η assumes exact opposition.
- Non-antiparallel beams leave a net "V" push of 2 sin(δ/2) per unit power, which the doughnut gradient must cancel.
- The lateral cost toward the V's apex is therefore 1/(η cos(δ/2) − sin(δ/2)).
- Example: at the centre, the four ring pairs are 12.8° off antiparallel. Their worst cost is 3.97 instead of 2.73 (+45 %).

**Exact cost.** I computed it as the gauge of the conic hull of the two beams' force discs, d_k + η·w (LP over rim points; *[RT5, r5]*):

| Pair tolerance | Uncovered grid points | Exact worst cost | Budget fit |
|---|---|---|---|
| 25° | 2/27 (top edge, x = ±0.5 m, z = +0.4 m) | **1.175/η** | 1.02/η |
| 35° (full coverage) | 0/27 | **1.35/η** | 1.02/η |

The exact *mean* is lower (1.53), so total power is not hurt, but heat-limited speed is.

**Pairs available per grid point:** 0, 0, 1, 2, 2, 2, 2, 3 ×8, 4 ×10, 5 ×2. Seven of 27 points have ≤ 2 pairs.

**Occlusion.** With one head blocked, **8.0 % of (position, head) cases have no pair left**. The "1 %" in FINAL_VERDICT R7 is the push figure; the floor's low ends use pairs.

**Effect.** +5 % (25°) to about +20 % (35°) channels on every pair floor.

**Fix.**
- Replace the fit with the exact cost, evaluated per position.
- Shrink the image volume or add heads so that every point has ≥ 2 pairs.
- Report pair occlusion.

### M2. Push beams: the convergent 1550 nm power at a mote breaks Class 1, and three channels per mote is too few

**Convergent power.**
- At 1550 nm the limit is corneal, an irradiance averaged over 3.5 mm, with no angular-acceptance discount [memory: ICNIRP/IEC t > 10 s, 100 mW/cm², 3.5 mm].
- The active push beams on one mote converge within µm. A cornea within ~2 mm of the mote receives every active beam whose source lies in its forward hemisphere.
- The LP allocation gives a hemisphere sum of up to **2.22 F, i.e. 1.87 × P_beam** *[RT5, r3]*.
- At the push floor points (P_beam 9.6 mW) that is **18 mW, 1.8 × AEL**.
- Capping P_beam at 10/1.87 = 5.35 mW gives push accent 731, sketch 3 204 and film density 13 200 channels.
- Pairs are unaffected: opposed beams cannot both reach one cornea.

**Channels per mote.** "3 active beams" is the generic LP vertex. Gust and parasitic-force rejection in any direction needs a positively spanning set already aimed at the mote.
- The best *fixed* 4-head subset per position gives h_worst 5.41 (median 4.25), against 2.22 when all 12 heads are re-assigned freely *[RT5, r3]*.
- Keeping h ≈ 2.2 therefore needs ≥ 4 channels per mote plus make-before-break hand-over: **+33 % push channels**.

**Push upper ends rest on unshown beams and loops (C2 of RT4 not closed).**
- `budget2` uses R_ft = 20 µm at R_head = 0.10 m (film-density push, 7 601 channels), where w_t = 12.8 µm. The realisable 10–90 % edge (~0.86 w_t) is ≈ 11 µm.
- M2c's order-8 super-Gaussian at R_ft = 20 µm has a 6.6 µm edge, so it is not realisable at that aperture.
- M2c ran a = 1 µm only, with force authority 1.5 × drag(v + 0.3). That is about 1.6× what the L3 design allows (1.3 × drag(v + 0.05)).
- Its statistics are still 32 motes × 0.2 s.
- `feedback.py` still uses the super-Gaussian (RT4 C2's fix was "band-limited profile from the pupil").

**Hot face (minor here).** For a uniform push beam the pole excess is 1.33 × T₁ (all-l spherical harmonics, *[RT5, r2]*), so push T_face is under-read by ~15 K. It does not bind at the floor points (487 K).

### M3. The "laminar zone with mean-flow feed-forward" lever is physically wrong unless the mean flow is zero

**The physics.**
- In M8, u_air = 0.05 m/s is "the fluctuation", on the argument that "the swarm measures the mean flow and the controller cancels it".
- Feed-forward removes *tracking error*. It does not remove the *drag* of the mean flow U, which photophoresis must supply continuously.
- The mote's heat is set within µs (thermal time ≈ 5 µs at a = 1.5 µm), so the upstream legs set the speed limit. Required force is 1.3 × drag(v + U + u′).

**Effect.** If the zone needs a gentle laminar flow of U = 0.1 m/s, then u_air = 0.15 *[RT5, r8]*:

| Target | u_air 0.05 | u_air 0.15 | Increase |
|---|---|---|---|
| Accent | 382 | 487 | +27 % |
| Sketch | 1 674 | 2 136 | +28 % |
| Film density | 6 896 | 8 801 | +28 % |

The full scan over u_air = 0.05 / 0.10 / 0.15 / 0.20 / 0.30 gives film density 6 896 / 7 603 / 8 801 / 10 189 / 14 337.

**Realism near people.** Occupied-zone air runs 0.05–0.25 m/s with 20–60 % turbulence intensity. A person's thermal plume is ~0.2 m/s, and hand wakes are 0.5–1 m/s [memory: ISO 7730 / ASHRAE 55 practice]. A still zone (U ≈ 0) with only 0.05 m/s fluctuation, right where viewers touch the image, is not established.

**Credit to the lab.** With the ITO mote and a 600 K face, even u_air = 0.3 stays feasible (accent 793, film density 14 300). This contradicts M5's "normal room: nothing feasible", which was for the 450 K engineered mote.

**Fix.** Set u_air = U + 3σ_u′, and measure U and σ_u′ in the target room.

### M4. Mote consistency (RT4 C1) is documented, not implemented, on the pump side; α₄₀₅ and k_eff are optimistic

**The pump model in code.**
- `design()` computes `A_pump = absorptance(alpha_pump * a)` with a **global** α_pump = 1.5×10⁵ m⁻¹ (1 500 cm⁻¹) through the **whole mote radius**, for every mote class.
- `MOTES["ito_coreshell"]` defines `core_frac` and `alpha_core`, but nothing reads them (grep confirms).

**Why 1 500 cm⁻¹ is too high for `ito_aerogel`.**
- R9 puts dense Eu²⁺-nitride at α₄₀₅ ≈ 3×10²–3×10³ cm⁻¹ and allows ≤ 30 vol % phosphor in the aerogel.
- The effective value is then ≈ 90–900 cm⁻¹.
- 1 500 cm⁻¹ through the aerogel implies a dense-phosphor α ≥ 5 000 cm⁻¹.

**Effects of α₄₀₅ alone** *[RT5, r4]*: at 500 cm⁻¹, film-exact green goes from 5 957 to 9 704 channels (a = 4 µm), and cyan becomes **infeasible** (pump AEL and exit window).

**k_eff.**
- Thirty vol % of dense phosphor grains raises k_eff about 2.3× (Maxwell: 0.03 → 0.069).
- An ITO-nanocrystal skin at the 30–60 % loading of the M7 recipes is at or above 3D percolation. If it percolates, k_eff + 2k_s·t/a ≈ +0.05 for k_s = 0.3 [memory: NC-film conductivity 0.1–1 W/m/K].
- R9 itself says a micron aerogel may run 1.5–2× above monolith k ("Recipe A FOM falls to ~3.3–4.0").
- k_eff + 0.03 adds +22 % channels.

**A_trap = 1.0 for the ITO motes.** There is no Fresnel loss (≥ 4 % from the silica overcoat) and no plasmonic reflection from dense ITO-NC islands. A = 0.85 adds +10 %.

**Fix.**
- Compute A_pump, J₁/A, k_eff and A_trap per mote with `mote_material` and the core model.
- Carry α₄₀₅ as a band.
- Add α₄₀₅ (micron core and loaded aerogel) to bench B2 alongside k_eff.

### M5. Pump optics: jitter and focus tracking are under-specified; turbulence near people is not modelled

**Pointing.** `budget2` assumes 0.5 µm rms pump jitter at 2 m (0.25 µrad).
- Indoor turbulence tilt through a 0.3 m aperture over 2 m: 0.59 / 1.9 / 5.9 µm rms at C_n² = 10⁻¹⁴ / 10⁻¹³ / 10⁻¹² [memory for indoor C_n²].
- Tilt-removed Strehl at 405 nm: 0.96 / 0.69 / **0.03**. At 1550 nm it is 1.0 / 0.98 / 0.78 *[RT5]*.
- So near a person's plume the 405 nm focus is destroyed (seeing blur ≈ 6 µm against w_p = 2.2 µm), while the trap doughnut survives.
- 0.5 µm needs per-pump-channel closed-loop tip/tilt, referenced to the mote, at about 0.1–1 kHz, plus C_n² ≲ 10⁻¹³ along the path.

**Focus.** `budget2` dropped v1's `B_focus`.
- At 1 kHz per-channel focus bandwidth, pump power per beam rises about 75 % (film density 8.0 → 14 µW; film-exact green 23.5 → 30.4 µW, close to the AEL) and trap channels rise about 5 %.
- At 3 kHz the effect is small.

The floors therefore implicitly require ≥ 3–6 kHz focus tracking over ±0.5 m, a sag of ~3 mm at 405 nm across a 0.3 m aperture, on 12–40 k channels.

**Fix.** Restore B_focus. Add a turbulence-limited pump spot, w_eff² = w_p² + (λL/πr₀)². Put the pump pointing loop into the steering specification (R10).

### M6. "k_overlap = 1 by safety-aware scheduling" is not yet a defensible Class 1 argument, and it fights the pair scheduler

**Certification.** Class 1 must hold under reasonably foreseeable single faults [memory: IEC 60825-1]. A software scheduler that guarantees no two same-head foci within a 3.5 or 7 mm line-of-sight tube is a safety function. It needs an independent, certified monitor (as in scanned-laser products), which is not designed.

**Conflict with heat-optimal pair assignment.**
- The heat-optimal assignment aligns the pair axis with the motion. Successive motes on a straight stroke (~1 cm apart at film density) then lie on the **same line of sight of both pair heads**.
- A same-head beam whose focus is within ±23 mm along the line of sight still has a radius below 1.75 mm, so most of its power passes the aperture.
- In the seven of 27 positions with ≤ 2 pairs there is no alternative pair.

**Cost without the lever** (k = 2, the lab's own S0–S3 baseline) *[RT5, r11]*: accent 592, sketch 2 596, film density 10 698. Allowing R_head = 0.20 m restores 363 / 1 594 / 6 568, but needs ~0.5–0.6 m clear optics per head.

**Pump beams from different heads converging on one mote.**
- They do enter one pupil together; all n_pump beams fit within 7 mm for |Δz| ≲ 10 mm.
- But R12 heads are ≥ 602 mrad apart as seen from anywhere in the volume *[RT5]*. That is ≫ the photochemical acceptance angle γ_ph (11–110 mrad) [memory].
- So they are separate sources for the 39 µW photochemical limit. Their sum (≤ 6 × 39 µW = 0.23 mW) meets the ~0.39 mW thermal limit.
- **Per-beam assessment of converging pumps is defensible**, but the lab never states this argument; it should.

**The 405 nm exit-window check is pessimistic** (in the lab's favour). It sums all of a head's beams through 7 mm and ignores γ_ph. With it relaxed, cyan film-exact may open up.

**Single fault.**
- `safety.py` is unchanged since RT4. There is no point-sum code and no single-fault or shutdown section.
- A stalled head now focuses ~2.4 W at 1550 nm (240 × AEL) or 8–23 mW at 405 nm (200–600 × AEL).

### M7. The 45 Hz lever has no evidence

- RT4 Major 9 asked for 60 Hz or a psychophysics check.
- `budget2`'s own docstring says "Refresh 60 Hz by default (Major 9)".
- M8 uses 45 Hz, below the typical flicker-fusion rate for bright, peripheral, moving point sources [memory: about 60–90 Hz].
- At 60 Hz every count rises +33 %.

**Fix.** Default to 60 Hz. Make 45 Hz a lever only after a bench flicker test (B4 can do it).

### M8. ITO at a 575–593 K hot face is in its degradation band; the B2 recipe contains a polymer that pyrolyses

- R9's own table: "ITO NC air-anneal: ≤ 300 °C little effect, worst ~350 °C" (573 / 623 K, snippet).
- M8 paraphrases this as "loses carriers above ~620 K" and runs the pair floors at T_face 575–593 K, continuously for hours.
- B2's layer-by-layer primer (polyelectrolyte) and any organic nanocrystal ligands pyrolyse at about 250–400 °C [memory]. That could char, which raises A_vis and dims the phosphor, and changes k_eff.
- Capping T_face at 573 K costs +10–16 % (B1 → B2: film density 8 801 → 10 189).

**Fix.** Use T_max ≤ 573 K until a long-term (≥ 100 h) anneal of the ITO-NC skin with a silica overcoat is measured. Use an inorganic primer.

### M9. The R12 geometry and aperture are not physically consistent with the room description

**The workbench.**
- M4 places the image "above a workbench", yet the R12 floor head sits at (3.0, 2.5, 0.05), directly under the image.
- The low ring is at 0.25 m, "in the workbench skirt". A bench top occludes the floor head and grazes the low-ring lines to the lower image.
- Without the floor head: push h_worst rises from 2.22 to 2.65. Without the floor head and low ring: **no upward force at all** (6 664 of 8 100 directions infeasible) *[RT5, r10]*.
- M4 has no obstacle model.

**Aperture.**
- R_head = 0.15 m is a 1/e² radius, so the clear aperture is ≈ 0.4–0.45 m per head (RT4 Minor 8, unaddressed). That is not "small fixtures in coves and baseboards".
- Each head shares that aperture among 500–2 500 trap and pump channels. RT4 Major 5 (étendue tiling) has no code; channels still equal N × beams.
- Opposed pair heads also receive each other's diverging trap power (RT4 Minor 7, unaddressed).

### M10. Bench B1 cannot deliver G1 as designed: C_ph is confounded with J₁/A, intensity and convection, and the design's hot regime is untested

**J₁/A confound.**
- `analyze_b1.py` compares against `force_per_absorbed_watt(a, kp, C_ph=1)`, i.e. J₁/A = 0.5 fixed. So "implied C_ph" really measures C_ph × (J₁/A)/0.5 × A_true/A_input.
- Black-dyed or carbon-loaded polymer spheres absorb through the volume. At a = 2.5 µm *[RT5, r9]*:

| α (cm⁻¹) | J₁/A | Implied "C_ph" |
|---|---|---|
| 10³ | 0.04 | 0.02 |
| 3×10³ | 0.10 | 0.14 |
| 10⁴ | 0.26 | 0.54 |

- So the plan's G1 gate ("C_ph < 0.3: route likely uneconomic") would trip spuriously on the very particles it names.
- The k-ratio test (glassy carbon vs polymer) is confounded the same way. Refractive focusing (n ≈ 1.5–1.6) can even reverse the sign for weak absorbers.

**Intensity.**
- The analysis uses the on-axis value 2P/(πw²) for every particle.
- At 0.3 / 0.6 / 1.0 mm off-axis (w = 1.75 mm) the true value is 0.94 / 0.79 / 0.52 of that, and the depth offset is unknown from one camera.
- Cuvette entry Fresnel loss (~8 %) is not corrected.

**Convection.**
- Beam-tied convection (absorbing deposits on the windows, window absorption at 808/1064 nm) exists only with the beam on, so beam-off subtraction cannot remove it.
- Turning the cuvette 180° reverses that convection along with the beam, so it does not cancel. The expected flows are 0.1–1 mm/s [order-of-magnitude estimate], comparable to glassy carbon's 0.24 mm/s drift.

**Settling.** Glassy carbon settles at 1.16 mm/s, 5× its drift. It leaves a 1 mm field in ~1 s and a 10 mm cuvette in < 10 s, so the "30 s beam-off record" does not work for it.

**Hot regime.** B1 runs at ΔT ≈ 2.2 K; the pair floor runs at ΔT ≈ 220–300 K.
- The force uses μ(T_f)², which is 1.59× μ(T₀)² at the design point.
- With ambient-temperature gas properties the channel count rises 71 %; a surface-temperature evaluation goes the other way.
- B1 cannot see this non-linear regime.

**The self-test is tautological.** Synthetic data are generated from the same model, so none of the confounders above are exercised.

**Fix.**
- Give `run.json` a `j1A` input. Use skin-absorbing references (glassy carbon, carbon- or metal-coated hollow silica).
- Compute local I per track from the measured beam profile, with the focal plane at the beam axis.
- Add non-absorbing tracer spheres, measured *with the beam on*, as the convection reference.
- Use short beam-on/off cycles for heavy particles.
- Add a hot series (focused beam, 1–10 kW/cm², ΔT 100–300 K) using B2's Er thermometer.

---

## Minor

1. **Coarse speed grid.** The 20 % V_GRID makes the M8/M8c floors ~7 % pessimistic (lab-favourable). Use a 5 % grid.
2. **Cyan `_hiT` quench.** T50 = 650 K rests on an ambiguous snippet ("450 °C/450 K"). The −4.2 % at 150 °C point fits T50 ≈ 550–680 K for Ea 0.5–0.3 eV, and the Arrhenius tail is broader than the logistic with dT = 40 K. At 590 K the pump power rises ~60 %; this binds only for film-exact. The β-SiAlON `_hiT` preset (80 % retained at 300 °C) *is* supported.
3. **Wall light** is energy-conserving (M32 ✓), but:
   - It uses photopic V(405). In a dim, mesopic lab the violet stray is up to ~8× more visible relative to the cyan image (V′/V ≈ 30–70 at 405 nm against ≈ 8 at 497 nm) [memory: CIE V′]. At the film-density floor the wall ratio goes from 0.011 to as much as 0.09 at full scotopic weighting.
   - whitener_gain = 1 ignores viewers' brightened clothing on the far side of the beams.
4. **Hot-face formula.** Exact for pairs (ratio 1.006, *[RT5, r2]*), but 1.33× low for push. Not binding.
5. **M7 shell model.** Homogenising islands at 60 % fill is valid only for sub-λ islands (R9: 150–250 nm, OK). If islands reach ≳ λ/2, gap transmission drops J₁/A to ≈ 0.21 (front 0.6, back 0.24).
   - The ITO α = 5.7×10⁵ cm⁻¹ is an extinction at the LSPR peak (1 600–2 200 nm, dispersed NCs). At 1550 nm, in dense islands, it may be lower and partly reflective.
   - The Cs_xWO₃ α (9.5×10³ cm⁻¹) comes from broadband 780–2500 nm shielding, not from 1550 nm. "Only ITO passes" is not robust in either direction.
6. **M8b** re-implements the push point with identical inputs (h_worst 2.22, single 1.19, margin 1.3). It checks arithmetic, not assumptions. The pair path (lg01, f_I, the h fit), which sets every floor's lower bound, was not re-checked.
7. **FINAL_VERDICT wording.** "4–6 µW-class 405 nm pump beams" should read "4–6 pump beams of 11–22 µW". "1 % of cases lose the mote" is the push figure (pairs: 8 %).
8. **`intercept()`.** The form (1 − e^{−2a²/w²}) · w²/(w² + 4σ²) is pessimistic for a > w. Use 1 − exp(−2a²/(w² + 4σ²)). Lab-favourable, about +14 % icp at a = 2.5 µm.
9. **Dispensing and loss.** Not modelled (M9 claims zero touch losses with avoidance). Pair occlusion loss (8 %) and re-capture need a channel budget.
10. **Open RT4 items** that are documented but not implemented:
    - C3: point-sum and single-fault code;
    - Major 5: étendue tiling;
    - C2: band-limited beam and ≥ 10⁴ mote-s statistics;
    - Minors 7 and 8.

---

## RT4 implementation audit

| RT4 item | In code? | Note |
|---|---|---|
| C1 consistent mote | **Partly** | J₁/A from M7 for the ITO motes. Pump absorptance is still global; `core_frac`/`alpha_core` unused; k_eff hard-coded (M4) |
| C2 realisable push beam and loop | **No** | R_ft ≥ 20 µm in the budget; the sim still uses a super-Gaussian, a = 1 µm, 6.4 mote-s (M2) |
| C3 Class 1 | **No** | k_overlap is a scalar; `safety.py` unchanged; no convergent sum, no single fault (M2, M6) |
| Major 1 ρT | Yes | |
| Major 2 LG01 exact | Yes | η and f_I correct. The heat-factor fit is not (M1) |
| Major 3 J₁(αa) | Yes | |
| Major 4 C_ph range | Yes | Floors use 1.0, the top of the range |
| Major 5 étendue | **No** | |
| Major 6 drop single | Yes | |
| Major 7 force margin | Yes | Applied consistently: heat, P_beam and T₁ all use 1.3 × drag(v + u) |
| Major 8 occlusion | Push only | Pairs lose 8 % (M1) |
| Major 9 60 Hz | Default only | Floors use 45 Hz (M7) |
| Major 11 hot face | Yes | Exact for pairs; push 1.33× low |
| Minor 1 wall light | Yes | Photopic only |
| Minor 10 u_air | Yes | Then undone by the "laminar" lever (M3) |

---

## Top 5 fixes

1. **Report steered beams honestly (C1, M5).**
   - Count trap + pump channels.
   - Restore B_focus and add a turbulence-limited pump spot.
   - State the pump-channel spec: 0.25 µrad, ≥ 3–6 kHz focus over ±0.5 m, mote-referenced.
2. **Finish RT4 C1 in code (M4).**
   - Per-mote A_pump (core model, loaded aerogel), k_eff with loading and skin conduction, A_trap with Fresnel.
   - Carry α₄₀₅ = 300–3 000 cm⁻¹ and k_core = 0.03–0.06 as bands.
   - Move α₄₀₅ and k_eff to the top of B2.
3. **Fix the room models (M1, M3, M9).**
   - u_air = U + 3σ.
   - Exact misaligned-pair cost per position, with P_beam at the longest throw.
   - Pair coverage and occlusion.
   - An obstacle model (workbench, people).
4. **Write `safety.py` v2 (M2, M6).**
   - Convergent 1550 nm sum: push ≤ 5.3 mW per beam.
   - γ_ph treatment of converging pumps from different heads (separate, and say so) and of the exit window.
   - Same-head overlap: k = 2 until an independent certified monitor exists.
   - Single-fault shutdown times.
5. **Re-plan bench B1 (M10).**
   - `j1A` input and skin-absorbing reference spheres.
   - Per-track intensity.
   - Beam-on tracer convection reference.
   - A hot-regime series (ΔT 100–300 K).
   - B3/B4: an enclosure with HEPA for open-air respirable ITO motes (the plan's "seal in the cuvette" cannot apply there), isolators against opposed-beam back-coupling into fibre amplifiers, and eyewear covering 405 nm and 1064/1550 nm together. In B1, block the ~4 % specular reflections from the cuvette faces (40–80 mW, Class 3B).

Then rename the M8 numbers "optimistic design point", default to 60 Hz and T_face ≤ 573 K, and re-run M8/M8c.

## Bottom line

**The floor claims are optimistic.** They reproduce exactly under the lab's assumptions, and are even 7 % pessimistic on grid, but they are not physics floors. They count only trap beams and rest on several errors and unsupported levers.

| Target | Claim | Corrected trap channels | Corrected steered beams |
|---|---|---|---|
| Accent | 340–420 | ~0.5–1.7 k | ~1–3.4 k |
| Sketch | 1.5–1.8 k | ~2.1–7.6 k | ~4.3–15 k |
| Film density | 6.1–7.6 k | ~9–17 k | ~18–35 k |
| Film-exact, green | 6.1 k | ~9–33 k | ~18–65 k |
| Film-exact, cyan | 10.5 k | ~15–33 k, or infeasible | ~30–65 k |

All of these assume an ITO-skin mote that has not been made. With R9's pessimistic material values almost nothing is feasible, so bench items B1 (done right) and B2 (FOM, k_eff and α₄₀₅) remain the critical path.

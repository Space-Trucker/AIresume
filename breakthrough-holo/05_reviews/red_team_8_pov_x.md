# Red team 8: POV-X, fast POV motes under passive Class 1 by the crossing-rate rule (T8, m19, m19b)

**Scope.** Reviewed on 2026-10-01:
- `09_unlock/T8_pov_crossing.md` as committed in 2182f4c, with `m19_pov_crossing.py`, `m19b_pov_track.py`, `results/m19_run.log` and `results/m19b_pov_track.json`;
- the edits made during this review (m19: A and the EN 50689 skin rule; m19b: mean wind; T8's update box in commits c989502, 0c37dcc and f7c83fe) are noted where they change a verdict, and are checked in their own section;
- the inputs T8 builds on: T7 (B9, forward-scatter illumination, follow mode), idea round 3 (opus, idea 2), R7 rows K6/K7 and "Moving and scanned traps", red team 6, `m17_exposure_field.py`, `m18*.py`;
- at the coordinator's request, red team 7 (`red_team_7_gaussian.md`, C1–C3) and idea round 3 (sonnet) are folded in where they bear on T8. I re-derived only what decides a T8 verdict, and say so where I reuse their result.

**Method.** All numbers marked *[RT8]* come from `09_unlock/rt8_check.py`, one section per attack:
- `std`: standards arithmetic;
- `expo`, `expo2`, `expo3`, `expo4`, `m17x`: moving-beam exposure field;
- `loop_key`, `loop_sens`, `loop_attrib`, `loop_attrib2`, `loop_attrib3`, `loop_conv`, `loop_upd`, `nsub`: tracking loop;
- `xm19b`: m19b's own simulator, run longer;
- `phys`: heat, Mie, bookkeeping;
- `chan`: channels and sensing;
- `misc`: indium release and flicker.

Results are in `09_unlock/results/rt8_*.json`, and the console output is in `results/rt8_run.log`. The first-pass `expo` runs with θ_min 30° had no cap on the LP cost and picked near-degenerate facets; they are superseded by `expo2` and `expo4`. The first-pass loop runs used ≤ 2 substeps and an end-of-substep actuator amplitude; the `attrib3`, `nsub` and `conv` runs correct both.

Written here, independently of the T8 code:
- LP allocation by enumerating head triples, and an own hull-facet enumerator;
- POV tours (greedy chaining with blanked jumps, as `mote_plan.py` defines N and duty);
- the time-averaged exposure of moving beams: each tour element is crossed f_r times per second and occupied for dl/v each time, with Gaussian beams including the Rayleigh range, and exact non-central-χ² capture through the 3.5 mm disc;
- a 3D von Kármán–Pao turbulence field from random Fourier modes, which the mote moves *through*, with a mean wind;
- a PID tuner (exact ZOH discretisation, modulus margin ≤ 2, plus an optional short 3D gain search);
- a vectorised 3D tracking simulator with a per-beam amplitude lag and per-revolution head-usage statistics.

Project, RT6 and RT7 code is imported only in lines marked XCHECK.

**Double validation**

| Check | RT8 | Reference | Agreement |
|---|---|---|---|
| LP allocation (own triple enumeration) | 300 random cases | scipy `linprog`; m18c hull facets | 4×10⁻¹⁶; 2×10⁻¹⁶ |
| Exposure function on identical static beams | own | `m17.exposure` | 1×10⁻⁹ |
| One stroke, beam ⟂ stroke: time-mean pupil power / (f_r·d_ap·E/L) | 1.000 | T8's own-path term | exact |
| Same stroke, beam at 20° to it | 2.92 | 1/sin 20° = 2.92 | exact |
| m17 closed-form capture vs exact χ² | max error 0.62 per beam; −11 % on a perpendicular crossing | | worst *static* pupil only +1.3 % |
| T8's s′ recipe (M17, H14, random heads) on M17 random segments | s′ 2.73 | T8 3.0 | 0.91 |
| I_unit, 1 µm ITO mote, v 0.5 / 0.8 m/s | m18.hold 7.317 / 7.343 ×10⁶ | rt7.hold_I 7.336 / 7.347 ×10⁶ | 1.003 / 1.000 |
| Hot face, office gust peak, v 0.5 m/s | rt7 507 K | m18 521 K (T8 521 K) | 2.7 % |
| Turbulence field (σ 0.1, L 3 cm) | σ 0.101 / 0.098 / 0.099, L₁₁ 3.2 cm, η 0.67 mm | targets 0.1 m/s, 3 cm | ≤ 7 % |
| Tracking loop, still air, w 35 µm, 20 kHz, m19b assumptions (Eulerian, no mean wind) | 0/20 lost in 36 mote-s; draw error p50 14, p99.9 26 µm; offset p99.9 19.5 µm | m19b: 0/20; 16.8 / 27.2 / 16.7 µm | agree |
| Tracking loop, office, w 35 µm, m19b assumptions | 64/100 lost in 605 mote-s (0.11 /s; exact lag 0.15 /s) | m19b's own code: 3/20 in 110 mote-s (0.027 /s, 95 % ≤ 0.059) | ×4 harsher; both ≫ 10⁻⁴ /s |
| Loop integration | 1/2/4 substeps identical without noise; 16 = 32 substeps with noise | — | converged |
| EN 50689 skin margin; ICNIRP strict margin (T8 sketch, w 34.3 µm) | 0.75; 1.29 | sonnet 0.79; 1.39 | ≤ 8 % |
| Mie q_iso(10°), a 1 µm, ±2.5° (rt6 BHMIE) | 24.5 | RT7's own Mie 24.6 | 0.4 % |
| Heads per mote: dynamic loop count vs static LP union | 3.3–3.9 per 33 ms (straight strokes) | union over gust draws: 5.0 (still), 9.1–9.3 (office) | consistent (union ≥ instantaneous) |

Facts from recall are marked **[memory]**. 8 of 8 web searches were used; the sources are at the end. icnirp.org and seibersdorf-laboratories.at are blocked by the egress proxy, so no standard was read in full.

**Severity counts:** 3 critical, 11 major, 8 minor.

---

## Summary

**What T8 gets right.**
- The standards framework holds. At 1400–4000 nm a focus that moves past a fixed aperture is a pulse train. Rule 1 (single pass) and rule 2 (mean over every window) apply. C5/C_P is a retinal-thermal 400–1400 nm factor that is not applied to the cornea or skin, and it is 1 for point sources.
- The invariant E/L = h·I_unit·πw²/2 is correct, and so is its consequence: the mean pupil load of a moving focus does not depend on the mote's speed.
- Rule 1 holds with a 270–420× margin through 1 mm. Rule 2 binds only at windows ≥ 10 s (ratios 0.13 / 0.24 / 0.47 / 1.00 at 0.35 / 1 / 3 / 10 s).
- B9 is therefore not a bound on moving foci, which confirms opus idea 2.

**What fails.** Each of the three findings below is decisive on its own.

1. **The pupil load is set by beams that run along the strokes, not by T8's s′ (critical).**
   - The minimum-power LP that m19b's controller uses pushes a mote with the beams whose directions lie closest to its motion. That is what "minimum power" means, so a stroke's beams run along the stroke, and one aperture on the stroke collects the beams of every mote within the beam's ~12 cm divergence length.
   - Time-averaged exposure of POV tours (own code, exact capture, H10, LP heads, 30 Hz, v 0.5 m/s), at T8's own sketch waist of 34.3 µm in still air:
     - **26–31 mW on random arcs;**
     - **39–45 mW on random 10 cm segments;**
     - **61 mW on content with one arm-like vertical line;**
     - **57–88 mW on the project's own Iron-Man outline** (`content.procedural_armor_budget`, 5 m);
     - **32 mW on the same outline rotated 30° and moved 15 cm.**
   - That is **2.7–9.1× the 9.6 mW AEL.** T8's s′ = 3.0 is reproduced only for random heads on random segments spread through the whole volume (s′_eff 3.6). Even T8's own recipe gives s′ = 10.5 on the outline.
   - With the plain LP, Class 1 at T8's other inputs needs **w ≈ 11–21 µm**. For the project's own outline it needs 16–23 µm even with scheduling. Both are below the 26.6–32 µm diffraction floor of 0.11 m heads, and below any waist shown to hold (m19b: 25 µm loses 39/40 at 20 kHz).
   - A stacking-aware allocation (no beam within 20° of the motion; LP cost h ≤ 3–4) restores random segments, arcs and the arm-line: 8.3–9.9 mW at h_mean 1.5–1.6.
   - It does not restore the project's compact outline: 40–43 mW (×4.2–4.5) in the head plane, 21–24 mW (×2.2–2.4) rotated off it. That residual is stroke density, which random-segment stacking never sees.
2. **The 20 kHz loop does not keep the motes (critical).**
   - T8's evidence is quick runs of 20 motes × 1.8 s. "0/20" in 36 mote-s only bounds the loss rate at ≤ 0.083 /s, which is 830× the 10⁻⁴ /s target.
   - **m19b's own simulator, run longer:**
     - office σ 0.1 at w 35 µm: 0.027–0.038 /s;
     - **at T8's office waist of 31 µm: 0.27–0.37 /s**, a point T8 tabulates but never simulated;
     - still air at w 35: ≤ 0.013 /s (0/40, the main session's grid).
   - **My independent model** reproduces m19b's still-air numbers when it holds the Gaussian force over each 50 µs frame, as m19b does. In an office it is ×4 harsher.
   - But the photophoretic force follows the mote's position within ~2 µs. With the force resolved inside the frame (converged at 16 substeps):
     - office w 35: **3.6–9.9 /s**;
     - still w 34 at 4 µm sensing: **0.2–0.7 /s**.
   - The cause is a profile instability at rate ≈ 4·v·δ/w² ≈ 11 000 /s. It is faster than the 155 µs loop delay because the beam force is ~v, not ~σ_u.
   - The carry holds only in two cases:
     - ≈ 2 µm sensing in still air at w 34 (0 losses in 92–980 mote-s);
     - w ≥ 50 µm, including the office (0/100 in 980 mote-s with the force held per frame; 1/40 in 92 with it resolved).
   - w ≥ 50 µm is far above the Class 1 waist (C1). Real content needs 16–23 µm, where the instability is 2–4× faster still.
   - At 526 motes, even 10⁻² /s is 5 dropouts per second.
3. **"~3 200 channels, no hologram engine" and "content at 0.5–0.8 m/s" are incompatible (critical).**
   - On straight strokes the controller uses 3.3–3.9 heads per 33 ms (p90 4–5), so T8's 3 + 1 holds on average.
   - But a tour mote crosses the whole field. A full-field single-mode channel needs 46–52 mm·rad per axis (T8's "25 mm, ±0.5 rad" is 12.5), and one H10 head has the étendue of ~2 such channels with separate optics.
   - Sharing a head among ~300–500 channels therefore needs a mode-selective multiplexer: a hologram (excluded by T8) or an image-plane positioner array (T8's patch idea).
   - A positioner array cannot follow animated content (DESI-class: ≥ 45 s per reconfiguration). On the project's outline it needs ×4.5–6.8 the beams in use (T8: ×1.5–3).
   - The "patrol only 1–1.5 cm" premise contradicts the tour model that gives N and the duty.

**Inherited from RT7 and sonnet, confirmed here** (each one alone would break the table):
- **The realistic skin** (A ≤ 0.6, J₁ ≈ 0.24) doubles E/L. w falls to 19–24 µm, below the floor at R 0.11 m. With J₁/A 0.30 the hot face at the office gust peak reaches 593 K, against the 573 K limit.
- **The EN 50689 child-appealing skin rule**: margin 0.75 at the sketch point.
- **The ICNIRP strict small-beam reading**: margin 1.2–1.6, and a stall cut within 0.6–1.0 ms.
- **RT7 C1, visible illumination**: free-standing viewers need emitters (here, steered visible channels) behind the image for each viewer.

**Bookkeeping.**
- m19 charges IR power only while a mote is lit, but every mote moves all the time: **4.4 → 7.7 W** (sketch), **17 → 21 W** (film).
- The étendue figure "≈ 24 mm·rad, about a 25 mm ±0.5 rad mirror" is internally ×1.9 short.
- The diffraction floor at the farthest head-to-image throw (4.75 m) is **32 µm**, above T8's 31 µm office waist.

**Verdict.**
- **T8's "physics-consistent full-vision candidate" does not survive.**
- What survives is the crossing-rate *framework*. Moving foci are judged per crossing, so B9 is not their bound. POV remains the only route found so far with a passive-Class-1 path to content speed.
- But no consistent design point exists yet. Making one needs:
  - a per-pupil dose-map governor and stacking-aware allocation that is shown on real content;
  - heads with R ≳ 0.2–0.3 m, or a head layout without coaxial heads;
  - a loop proven at ≤ 10⁻⁴ /s;
  - channel hardware that matches the simulated controller;
  - and, for a child-appealing product, the EN 50689 skin rule.

### Verdict per claim

| Claim (T8 / m19 / m19b) | Verdict | One-line reason |
|---|---|---|
| §1 A moving focus is a pulse train: rules 1 and 2, no C5 above 1400 nm | **CONFIRMED** (framework) | ICNIRP: C_P only for retinal thermal, = 1 for α < 5 mrad and pulses > T_i; not for cornea/skin [snippets]. R7 K6 |
| §1 E/L invariant; pupil bound independent of v | **CONFIRMED** | Algebra; own one-stroke crossing check 1.000 |
| §1 s′ = 1 + (s_static − 1)·δ/d_ap ≈ 3.0 (sketch) / 4.6 (film) | **REFUTED** | LP beams run along strokes: 2.7–9.1× the AEL at T8's w; T8's own recipe gives 10.5 on the project's outline |
| §1 rule 1 margin > 70× | **CONFIRMED** | 270–420× through 1 mm (T8 compared a 3.5 mm pass with the 1 mm limit) |
| §1 stall reaches the rule-1 dose in 0.25–0.76 s; a ≤ 100 ms cut is easy | **PARTLY** | Stall to AEL 0.28–1.7 s (at the authority cap 0.28–0.77 s): OK. Strict ICNIRP reading 0.6–1.0 ms. A convergence fault (20–100 channels to one point) reaches 8 mJ in 25–5 ms and is not a stall |
| §1 "C5 does not apply; passive Class 1 by crossing rate" for a consumer product | **PARTLY** | EN 50689 child-appealing skin rule (1 mm, 10 s): margin 0.75 (sonnet, reproduced) |
| §2 sketch 526 motes, 3 158 channels, 4.4 W IR, w 31–35 µm | **REFUTED** | w(Class 1) 11–21 µm with the plain LP, 16–23 µm on the project's outline even with scheduling; IR ×1/duty = 7.7 W; channels need a multiplexer (C3) |
| §2 hot face ≤ 521 K at gust peaks | **PARTLY** | 507–521 K for T8's mote with all heads clear; 593 K with a realistic skin; 655 K with one head blocked by a hand |
| §2 total IR independent of v | **CONFIRMED** (algebra), ×1/duty | |
| §2 visible 35–43 µW per pupil within Class 1 | **PARTLY** | Fine at ≥ 500 nm (390 µW). The photochemical Class 1 limit at the 30 000 s display time base is 39 µW at ≤ 450 nm [memory]; lit room fails ×10 (T8's own statement) |
| §3 m19b: plan feedforward, latency prediction, follow, LP, caps | **CONFIRMED** (implementation) | Reproduced in still air. Omissions: mean wind (as committed), motion through the field, actuator pointing lag and noise |
| §3 "20 kHz carries w 35 µm at 0.5 m/s up to office drafts" | **REFUTED** | Office: 0.027–0.038 /s (m19b's own code), 3.6–9.9 /s (RT8, force resolved within the frame). Still: ≤ 0.013 /s (m19b) vs 0.2–0.7 /s (RT8). Target 10⁻⁴ /s |
| §3 "20 kHz carries the eye-limited 31–35 µm spots" | **REFUTED** | 31 µm office: 15/20 in 56 mote-s with m19b's own code |
| §4 touchable; office drafts OK | **REFUTED** | Loop losses; a hand blocking a head raises the office hot face to 655 K |
| §4 fast animation 0.5–0.8 m/s | **REFUTED** for the stated hardware | Allowed by the eye framework. Not by patch hardware (positioners ≥ 45 s). Full-field channels need 46–52 mm·rad each, ~2 per head without a hologram-class multiplexer |
| §4 safe for everyday use: passive Class 1 plus stall cut | **REFUTED** as designed | Stacking ×3–9; EN 50689; convergence fault. Possibly restorable with a certified dose-map governor |
| §5.2 sensing 4 µm at 20 kHz, ≤ 100 µs | **PARTLY** | Descanned backscatter gives 900–8 200 photons per 50 µs (shot-noise σ 0.2–0.6 µm). Unbuilt; latency and background unassessed |
| §5.3 D·θ ≈ 24 mm·rad "about a 25 mm, ±0.5 rad mirror" | **PARTLY** | 23–26 mm·rad is D × the half-field angle. The quoted mirror gives 12.5 (×1.9 short); the head aperture is 167–189 mm |
| §5.3 patch channels, overhead ×1.5–3 | **REFUTED** | Patrol vs tour inconsistency; ×4.5–6.8 on the outline; positioners cannot animate |
| §2 6 beams per mote (3 LP + 1 hand-over + 2 illumination) | **PARTLY** | Straight strokes: 3.3–3.9 heads per 33 ms (p90 4–5, max 7) plus chattering; patrol loops ~10; visible scales with viewer clusters (RT7 C1) |
| §5.6 a scheduler cuts s′ to ~1.5 | **PARTLY** | Works on random segments and arcs (θ_min 20°: 8.3–9.9 mW, h_mean 1.54–1.58) and, if h ≤ 4 is allowed, on a vertical arm-line (8.6 mW). Not on the project's compact outline: ×4.2–4.5 in the head plane, ×2.2–2.4 rotated |
| §6 "physics-consistent full-vision candidate" | **REFUTED** | No consistent design point: C1–C3 plus the inherited RT7 C2 and EN 50689 |

---

## Independent recomputation of T8's key numbers

| Quantity | T8 / m19 | RT8 | Note |
|---|---|---|---|
| I_unit (1 µm, slip), v 0.5 m/s | 7.32×10⁶ | 7.34×10⁶ (rt7), 7.32×10⁶ (m18) | — |
| E/L at w 34.3 µm (h 2.14) | 29.0 mJ/m | 29.0 mJ/m | LP-weighted h along tours is 1.2–1.4, so the actual E/L is 14–16 mJ/m |
| Per pass through 1 mm; rule-1 margin | 0.10 mJ (3.5 mm); > 70× | 0.029 mJ; 276× | — |
| Rule-2 ratio at 0.35 / 1 / 3 / 10 s (T8's load) | — | 0.13 / 0.24 / 0.47 / 1.00 | the ≥ 10 s window binds |
| Stall to AEL at P_focus 15.9 mW / at the cap | 0.49 s (7.85 mJ) | 1.65 s / 0.77 s (still); 0.30 s at the office cap | T8 is conservative |
| EN 50689 skin (1 mm, 10 s) | — | 1.05 mW vs 0.785 (margin 0.75) | as sonnet |
| ICNIRP strict, H in 0.35 s on the track | — | 7 760 J/m² vs 10⁴ (margin 1.29); office 1.17 | as sonnet |
| s′ (sketch) | 3.0 | random heads: 3.6 (segments), 4.5 (arcs), 9.7 (outline); LP: 8.6–28.9 | s′_eff = worst / (f_r·d_ap·E/L_T8) |
| Worst pupil at T8's w (still air) | 10 mW | 26–88 mW | Table C1 |
| P_IR (sketch / film) | 4.4 / 17.1 W | 7.7 / 20.6 W | ×1/duty |
| D·θ per axis, full-field channel (w 35 µm) | 23.6 mm·rad | 23.2 (half field), 46.3 (full); D = 167 mm | the stated mirror is ×1.9 short |
| Diffraction floor, R_head 0.11 m | 26.6 µm (3.95 m) | 26.6 at 3.95 m; **32.0 at 4.75 m** | farthest head-to-image throw |
| Hot face, office gust peak, 0.5 m/s | 521 K | 507 K (rt7), 521 K (m18) | 593 K with realistic skin; 655 K with a head blocked |
| Loss rate, 20 kHz, w 35, office | "1/20" | 0.027–0.038 /s (m19b's own code, 104–110 mote-s); RT8 0.11–0.68 /s with the force held per frame, 3.6–9.9 /s with it resolved | Table C2 |

---

## Critical

### C1. Minimum-power beams run along the strokes, so one pupil collects whole strokes: 2.7–9.1× the AEL at T8's waist

**Mechanism.**
- The time-mean power through a fixed aperture is linear in the tour's power-per-length, so T8 is right that POV is "equivalent" to a static pattern.
- But T8 takes s′ from M17's *random-head* static stacking. A POV mote is pushed by the LP minimum along its velocity (f = v·t̂ − u), and the cheapest facet is the one whose beams are most nearly parallel to t̂.
- A narrow beam at angle θ to its stroke crosses an aperture on the stroke over d_ap/sin θ of travel, not d_ap. Own check: ×2.92 at 20°, exactly 1/sin 20°.
- When θ → 0 the beam stays inside the 3.5 mm aperture while w(z) < 1.75 mm, i.e. for |z| ≲ 1.75 mm·πw/λ ≈ 12 cm at w = 35 µm.
- So an aperture at the end of a straight stroke collects f_r·E/L·(stroke length up to ~25 cm). For h ≈ 1 at w 34 µm that is ~40–100 mW from a single line.

**Simulation** *[RT8 `expo`, `expo2`, `expo3`; tour model with jumps; still air unless noted; w = 34.3 µm (T8 still) or 31 µm (T8 office); v 0.5 m/s; 30 Hz; exact capture]*

| Content (5 m of strokes) | Duty | Random heads (T8/M17 convention) | LP heads, no jumps | LP heads with jumps | LP, office (w 31) |
|---|---|---|---|---|---|
| Random 10 cm segments (m17-style) | 0.31 | 11.1 mW (s′_eff 3.6) | 39.0 | **44.6** | 32.8 |
| Random arcs, R 3–20 cm (RT7-style) | 0.61 | 13.6 (4.5) | 26.1 | **31.4** | 20.9 |
| Project Iron-Man outline, planar, room centre | 0.67 | 29.4 (9.7) | 57.1 | **87.9** | 64.7 |
| Same outline rotated 30°, moved 15 cm | — | 21.6 | — | **32.0** | — |
| 4.4 m of segments + one 30 cm vertical line 3 cm off axis + one line aimed at a corner head | 0.35 | 35.7 | 61.4 | **61.5** | 45.3 |

AEL 9.62 mW in every case.

- The worst pupils are dominated by one head each:
  - for near-vertical strokes, the ceiling or floor head gives 39–60 mW (segments, arm-line, outline; the outline with jumps adds 27 mW from the opposite axis head);
  - for the arcs, a corner head gives 26–31 mW.
- Because one direction dominates, the result does not depend on the aperture-orientation convention.
- 85–94 % of the worst pupil's power comes from elements more than 5 mm away. This is stacking along beams, not the own crossing.
- The blanked jumps add 0–54 % (segments +14 %, arcs +20 %, outline +54 %): they are tubes too, and m19 ignores them.
- **T8's own recipe** (M17: static voxels at 3 mm, 3 random heads of H14, m17 capture) gives *[RT8 `m17x`]*:

| Content | s′ |
|---|---|
| M17 random segments | **2.73** |
| Outline, rotated | 3.79 |
| Outline, planar, room centre | **10.5** |

  The outline is planar and contains the ceiling/floor-head axis. That is a natural placement for a drawing at the room centre. Its silhouette sides are vertical lines that those heads see end-on. RT7 found the same alignment effect for static voxels (34–50 P_unit).

**Stacking-aware allocation** *[RT8 `expo2`, `expo4`]*. Beams within θ_min of the motion are forbidden unless the constrained LP cost exceeds h_cap.

| Content | θ_min / h_cap | Worst pupil | h_mean | Fallback to aligned |
|---|---|---|---|---|
| Segments | 20° / 3 | **9.9 mW (×1.03)** | 1.58 | 4 % |
| Segments | 40° / 3 | 32.9 mW | 1.79 | 31 % |
| Outline (planar) | 20–40° / 3 | 62.7–62.8 mW | 1.61–1.87 | 26–32 % |
| Aligned lines | 20° / 3 | 60.0 mW | 1.56 | 3 % |
| Aligned lines | 20° / **4** | **8.6 mW (×0.90)** | 1.63 (max 3.9) | 0.1 % |
| Outline (planar) | 20–30° / **4** | 40.2–43.3 mW (×4.2–4.5) | 2.11–2.26 (max 3.95) | 4–5 % |
| Outline, rotated 30° / 45° and moved | 20° / 3 | 23.5 / 21.4 mW (×2.4 / ×2.2) | 1.68 / 1.79 | — |

With random heads the rotated outline gives 19.9–21.6 mW, so the compact figure is ×2 over the AEL whatever the allocation.

- The scheduler works where an alternative facet is cheap. With θ_min 20°:
  - random segments: 9.9 mW, h_mean 1.58;
  - random arcs: 8.3 mW, h_mean 1.54.
- At h_cap 3 it fails for vertical strokes near the room axis. There the only non-coaxial pushes come from corner heads ~70° away, at h ≈ 3–3.3.
- At h_cap 4 the arm-line passes, but the compact outline does not:
  - ×4.2–4.5 in the head plane;
  - ×2.2–2.4 rotated off it, where even random heads give ×2.1–2.2.
- That residual is stroke *density*: 5 m packed in a 0.35 × 0.75 m figure, against random segments spread through 0.8 m³.
- θ_min 40° is worse than 20° (more fallbacks to aligned beams).

**Consequences.**
- At T8's inputs (A = 1, T8's mote, 30 Hz) the Class 1 waist is:
  - **11–21 µm** with the plain LP;
  - **34–37 µm** with the scheduler on random segments, arcs and the arm-line (T8's number survives there);
  - **16–23 µm** for the project's outline, even with the scheduler.
- For realistic content that is **below the 26.6–32 µm diffraction floor** of R = 0.11 m heads, and below any waist shown to hold. m19b's 25 µm loses 39/40 at 20 kHz, and C2 needs w ≥ 50 µm or ≤ 2 µm sensing at 34 µm.
- Raising the head radius to ~0.25–0.3 m gives an 11–13 µm floor at 4.75 m but multiplies the head étendue and the loop difficulty.

**Fix.**
- Replace s′ by a **computed worst-pupil time-mean over the actual content and allocation**: a dose-map governor per 3.5 mm cell (and per 1 mm cell for EN 50689) that re-allocates, slows or blanks strokes before any cell exceeds the AEL. It has to be part of the certified safety function.
- Report the price on the project's own content, not on random segments.
- Consider head layouts with no head on the image's vertical axis, or tilted ceiling/floor heads.

### C2. The 20 kHz per-channel loop loses motes at 0.03–10 /s at T8's waists, not < 10⁻⁴ /s

**T8's evidence.**
- Quick runs of 20 motes × 2 s, i.e. 36 mote-s per point.
- Zero losses bounds the rate only at 3/36 = 0.083 /s (95 %). One loss is ~0.03 /s.
- T7's own target, ≤ 10⁻⁴ /s, needs ≥ 3×10⁴ mote-s per point.

**m19b's own simulator** *[RT8 XCHECK, 20 kHz, 2 frames latency, 30 µs actuator, 4 µm noise, v 0.5, office σ 0.1, 20 motes × 6 s]*

| w | Mean wind | Lost | Mote-s | Rate | 95 % upper |
|---|---|---|---|---|---|
| 35 µm | no (as committed) | 3/20 | 110 | 0.027 /s | 0.059 /s |
| 35 µm | yes (working tree) | 4/20 | 104 | 0.038 /s | 0.077 /s |
| **31 µm (T8's office waist)** | no | **15/20** | 56 | **0.27 /s** | 0.41 /s |
| **31 µm** | yes | **17/20** | 45 | **0.37 /s** | 0.56 /s |

The main session's full grid (40 × 6 s, no mean wind) adds:
- 20 kHz still, w 35: 0/40 in 232 mote-s (≤ 0.013 /s);
- 20 kHz still, w 25: 39/40 lost.

**Independent model, first pass** *[RT8 `loop` key/sens]*

Settings: 20 kHz, 2 frames of latency, 30 µs actuator, 4 µm noise per axis, v 0.5 m/s, mean wind on unless noted, 100 motes × 10 s, 95 % Poisson intervals. Rows marked "fixed point" use 1 substep per frame; the others use 2. So the force is held per frame or only partly resolved within it, and the actuator lag is integrated with the end-of-substep amplitude. Both are optimistic; see the attribution.

| Case | w | Turbulence | Gains | Lost | Mote-s | Rate /s (95 % CI) | Heads per 33 ms |
|---|---|---|---|---|---|---|---|
| Office, circle, no mean wind (m19b as committed) | 35 | fixed point | 1D tuner | 64/100 | 605 | 0.11 (0.081–0.14) | 9.4 |
| Office, circle | 35 | fixed point | 1D tuner | 79/100 | 415 | 0.19 (0.15–0.24) | 9.3 |
| Office, circle | 35 | through field | 3D search | 97/100 | 174 | 0.56 (0.45–0.68) | 9.6 |
| **Office, circle (T8's office waist)** | **31** | through field | 3D search | **100/100** | 16 | **6.4** (5.2–7.8) | 9.0 |
| Office, straight tour stroke | 35 | through field | 3D search | 98/100 | 145 | 0.68 (0.55–0.82) | 3.9 |
| Quiet office, circle | 35 | through field | 3D search | 47/100 | 673 | 0.070 (0.051–0.093) | 9.8 |
| **Still, circle (T8's still waist)** | **34** | through field | 3D search | 32/100 | 801 | **0.040** (0.027–0.056) | 9.7 |
| Still, straight tour stroke | 34 | through field | 3D search | 44/100 | 682 | 0.065 (0.047–0.087) | 3.3 |
| Still, sensor noise 6 µm | 34 | through field | 3D search | 98/100 | 112 | 0.88 (0.71–1.1) | 9.6 |
| Still, latency 3 frames | 34 | through field | 3D search | 99/100 | 52 | 1.9 (1.5–2.3) | 9.4 |
| Still, 10 kHz loop (50 µs actuator) | 34 | through field | 3D search | 100/100 | ~0 | all lost at start | — |
| Still, sensor noise 2 µm | 34 | through field | 3D search | 0/100 | 980 | ≤ 3.8×10⁻³ | 9.6 |
| Office, larger spot | 50 | through field | 3D search | 0/100 | 980 | ≤ 3.8×10⁻³ | 9.5 |
| Office, v 0.8 m/s | 35 | through field | 3D search | 100/100 | — | all lost | — |

**Attribution** (office, w 35 µm, same gains and seed, 60 motes × 4 s) *[RT8 `loop` attrib, attrib3; `nsub`]*

| Change | Rate (/s) |
|---|---|
| m19b-like baseline: fixed-point turbulence, no mean wind, force held per frame | 0.13 |
| + mean wind | 0.14 |
| + motion through the field | 0.16 |
| Force updated within the frame, exact actuator lag: 1 / 2 / 4 / 8 substeps | 0.15 / 0.70 / 1.3 / 2.5 |
| Same, 40 motes × 1 s: 4 / 8 / 16 / 32 substeps | 2.1 / 3.1 / **3.6 / 3.6** (converged) |
| Still air, w 34, same gains: 1 → 4 substeps | 0.003 → 0.19 |

Checks:
- Without sensor noise the 1/2/4-substep runs are identical: no losses, offset p99.9 0.27 µm.
- A single frame of the Gaussian force converges to ≤ 0.6 µm between 1 and 256 substeps.
- So the effect is the noise-seeded profile instability evolving inside the frame, not an integration error.

**Converged force model** (16 substeps, exact lag, through-field turbulence with mean wind, 1D-tuned gains, 40 motes × 2.5 s) *[RT8 `loop` conv]*

| Case | Lost | Mote-s | Rate /s (95 % CI) | Draw error p50 / p99.9 |
|---|---|---|---|---|
| Still, w 34, 4 µm noise (T8's still point) | 30/40 | 43 | **0.70** (0.47–1.0) | 5.6 / 40 µm |
| Still, w 34, **2 µm** noise | 0/40 | 92 | ≤ 0.040 | 2.1 / 5.8 µm |
| Still, w 50 | 0/40 | 92 | ≤ 0.040 | 3.3 / 9.8 µm |
| Still, w 70 | 0/40 | 92 | ≤ 0.040 | 2.6 / 7.0 µm |
| Office, w 50 | 1/40 | 92 | 0.011 (0.0003–0.061) | 4.1 / 14 µm |
| **Office, w 35** | **40/40** | 4 | **9.9** (7.1–14) | — |

The waist and noise needed for a stable carry (w ≥ 50 µm, or ≤ 2 µm noise) sit against the Class 1 waist on real content (16–23 µm, C1). With fixed gains, the converged office rate at w 35 is 3.6 /s (attribution table).

**Confidence bounds at T8's design points** (20 kHz, 2 frames, 4 µm, v 0.5):

| Point | m19b's own model (most favourable) | RT8 first pass (≤ 2 substeps) | RT8, force resolved within the frame (physical) |
|---|---|---|---|
| Still, w 34–35 µm | ≤ 0.013 /s (0/40 in 232 mote-s) | 0.003–0.065 /s | 0.2–0.7 /s at 4 µm; ≤ 0.04 /s at 2 µm (0 events) |
| Office, w 35 µm | 0.027–0.038 /s | 0.11–0.68 /s | 3.6–9.9 /s |
| Office, w 31 µm (T8's waist) | 0.27–0.37 /s | 6.4 /s | worse than w 35 (3.6–9.9 /s) |

Against these:
- **The target is ≤ 10⁻⁴ /s.** At 526 motes, 10⁻² /s is already 5 dropouts per second.
- **The office claim fails in every model.**
- **The still-air claim is unproven** in m19b's own model (its statistics bound only ≤ 0.013 /s). It fails at the physical force response unless sensing reaches ~2 µm per axis (0 losses in 92–980 mote-s at 2 µm).
- **A per-channel descanned detector is photon-capable of that** (M11).

**Why it loses motes.**
- At 0.5 m/s the spot must be placed (latency + ½ frame)·v ≈ 60–75 µm ahead of the last measurement, using the *plan*.
- When the force falls short (a few % deficit from the Gaussian profile at sensor-noise offsets; gusts; facet switches), the mote lags. The plan-based prediction then puts the spot further ahead, the Gaussian force falls further, and the mote is lost.
- This is T7's profile instability, made ~10× faster because the beam force is ~v, not ~σ_u.
  - The growth rate is γ ≈ 4·F·δ/w². At F 0.5 m/s, w 35 µm and δ ≈ 7 µm (the 3D sensor noise) that is ≈ 11 000 /s, an e-folding time of ~90 µs.
  - That is *shorter* than the loop's total delay (2 frames + ½ frame + 30 µs ≈ 155 µs at 20 kHz).
  - A stable carry needs a delay ≪ w²/(4·v·δ). That favours larger spots, slower motes, lower noise or ≥ 50–100 kHz, which is the opposite of what the eye budget asks for (C1).
- This is also why the result depends on how the force is integrated within a frame (attribution above). m19b holds the Gaussian factor at its frame-start value for the whole 50 µs, so the instability cannot grow within a frame. The physical force follows the mote's position within microseconds (thermal lag 0.36 µs, τ_p 2 µs).

**Other model gaps.**
- **Mean wind.** Omitted as committed; RT7 C3; now added in the working tree. Effect ×1.1 here.
- **Turbulence.** Sampled at a fixed point (Eulerian), while the mote moves through the field at 0.5 m/s. Effect ×1.1 here: the seen field has ×4.5 the rms du/dt, but little energy above the loop bandwidth.
- **Steering actuator.** Its pointing lag is not modelled: v·τ = 15 µm at 30 µs unless pre-compensated. Pointing noise is not modelled either.
- **Lateral photophoretic force.** Omitted (RT7: minor).

**Fix.**
- Run ≥ 3×10⁴ mote-s per design point at T8's *own* waists (31 µm office, 34 µm still), with the mean wind, through-field turbulence and the actuator.
- Add a model-based predictor (use the commanded force over the latency, not the plan) and a recapture mode.
- Report loss as dropouts per second for the whole image.

### C3. "~3 200 single-mode channels, no hologram engine" and "content at 0.5–0.8 m/s" cannot both hold

**Heads per mote.**

| Path *[RT8 `loop`]* | Heads used per 33 ms (mean / p90 / max) | New-head events per mote |
|---|---|---|
| Straight tour stroke, still | 3.3 / 4 / 7 | ~550–800 /s |
| Straight tour stroke, office | 3.9 / 5 / 7 | ~550–800 /s |
| m19b's patrol circle | 9.0–9.8 | — |

- On straight tour strokes T8's "3 LP + 1 hand-over" is right on average. Covering p90/max needs 5–7.
- The 550–800 new-head events per second are facet chattering at near-equal LP costs. Hysteresis can damp it, at an LP-cost price.
- On curved strokes and in gusts the union is larger: along the outline and segment tours *[RT8 `chan`, gust-level drafts]*, 5.0 heads per refresh window in still air and 9.1–9.3 in an office.
- m19b's circle (a patrol model) uses all ten.

**The real problem: sharing a head aperture without a hologram.**
- A channel that carries a tour mote must follow it across the whole field. In `mote_plan.py`, which sets N and the duty, a mote crosses the field in (S+J)/v ≈ 15–17 s. "Patrol only v·duty/f_r ≈ 1–1.5 cm per refresh" is the distance travelled per refresh, not a patrol range.
- A full-field single-mode channel needs aperture × field ≈ 167–189 mm × 0.28 rad, i.e. 46–52 mm·rad per axis (m19 prints the half-angle product, 23–26; "a 25 mm, ±0.5 rad mirror" gives only 12.5).
- The whole H10 head (0.22 m × 0.28 rad ≈ 62 mm·rad) therefore has the étendue of **~2 full-field channels if each channel has its own optics**. Putting ~300–500 channels through one head requires a *mode-selective* multiplexer:
  - **A hologram/SLM.** T8 says it has none.
  - **An image-plane positioner array behind a shared objective** (T8's patch idea). Positioners cannot cross one another and move slowly: DESI-class has a 10.4 mm pitch and a 6 mm patrol radius, and repositions 5 000 fibres in < 45 s [search].
  - **Multi-tone AODs.** Their spots form grids, and power is shared among them.
- **A patch array does not serve the tour model.** Each patch (fine stage ±1 cm) hands a passing mote to the next patch every 2–4 cm (40–80 ms) with make-before-break.
- **Density on real content.** On the project's outline *[RT8 `chan`]*, a patch grid sized for the densest cell needs 23–32 channels per cell per head:

  | Cell | Channels needed | Beams in use | Overhead |
  |---|---|---|---|
  | 2 cm | 11 994 | 1 766 | ×6.8 |
  | 4 cm | 8 017 | 1 766 | ×4.5 |

  T8 assumed ×1.5–3.
- **Animation.** Content moving at 0.5–0.8 m/s moves the patches themselves, which positioners cannot follow.
- **A true patrol model is no escape.** Each mote looping on its own ~1 cm segment keeps patch channels local. But it needs a dark return leg (not budgeted; ~1.1 m/s on the return to keep duty 0.57 on straight strokes) and ~10 heads per mote (the m19b circle).

**Consequence.** Pick one:
- the fast animation needs a hologram-class mode multiplexer (T8's "no hologram engine" falls);
- or the patch array gives static content only, at ×4.5–6.8 channels on real content.

**Fix.**
- Name the multiplexer.
- Count channels per head from the simulated allocator (p90 heads per refresh window, plus make-before-break, plus visible channels per viewer cluster).
- Simulate the loop with only the beams that architecture can deliver, e.g. a mote limited to the patches it is in.

---

## Major

### M1. The consumer rules (inherited from sonnet, reproduced): EN 50689 skin and the ICNIRP strict reading

*[RT8 `std`]* The sketch point (w 34.3 µm, s′ 3, still) gives:
- **EN 50689 child-appealing skin criterion** (skin MPE through 1 mm, 10 s: 0.785 mW): 1.05 mW, **margin 0.75**. Office 0.75; film 1.15.
- **ICNIRP small-beam footnote** (cornea > 1400 nm, beam < 1 mm, pulses < 0.35 s: compare the non-averaged H; search-verified scope): 7 760 J/m² in 0.35 s against 10⁴, margin 1.29. Office 1.17; film 1.61.
  - A stalled focus at the authority cap reaches 10⁴ J/m² peak in **0.57–0.98 ms**.
  - Under this reading the stall cut must be a per-head hardware shutter in < 1 ms, not a ≤ 100 ms watchdog.
- An Iron-Man hologram is almost certainly "child-appealing". At A = 1 the EN rule caps w at ~30 µm (m19 working tree: 26.6–29.7 µm). With the realistic skin it caps w at 19–21 µm.

**Fix:** design to the EN 50689 skin limit from the start, and get a test-house opinion on the ICNIRP footnote's scope for moving µm foci.

### M2. The single-fault case is wider than a stall

- A stall of one channel: 0.28–1.7 s to the AEL. A 100 ms cut is enough.
- A **convergence fault** is a common-mode fault in the coordinate pipeline, calibration or planner that drives K foci to one point. At 15.9 mW per focus it reaches 8 mJ in 252 / 101 / 25 / 5 ms for K = 2 / 5 / 20 / 100 *[RT8 `std`]*.
- A per-channel motion monitor does not detect it, because every channel is moving correctly toward the wrong target.
- Class 1 under single fault needs an **independent** exposure monitor: per-head power plus independent position sensing of every focus, with a pairwise-convergence check and a ≤ 5–25 ms cut, all functional-safety rated. This sits on the same critical path as C1's dose-map governor.

### M3. IR power is counted only while motes are lit

- m19: `P_ir = N·duty·(h_mean/h_worst)·P_focus/η`. In the tour model every mote moves (and needs force) on blanked jumps too, so P_IR = N·(h_mean/h_worst)·P_focus/η.
- Sketch 4.4 → **7.7 W**; film 17.1 → **20.6 W** *[RT8 `phys`]*.
- The jumps also carry beams that stack (C1: +0–54 %).

### M4. The realistic mote (RT7 C2), checked against T8's design

- RT7: a ≤ 150 nm skin gives A ≤ 0.61 and J₁ ≈ 0.24–0.26. E/L doubles, so w_eye ÷ √2.
- The m19 working tree: sketch w 21.6–24.2 µm (34 → 24 still, 31 → 21.6 office). Below the 26.6 µm floor at R 0.11, so it needs R ≥ 0.15 m. EN 50689 brings it to 18.8–21 µm.
- m19's "A = 0.5" keeps J₁/A = 0.486, so the mote's heat does not rise. With RT7's J₁/A ≈ 0.30 *[RT8 `phys`, rt7.hold_I]* the hot face at the gust peak is:

  | Room, v 0.5 m/s | Hot face |
  |---|---|
  | Still | 478 K |
  | Quiet office | 503 K |
  | **Office** | **593 K (> 573 K)** |
  | Office, v 0.8 | 662 K |

  So "office drafts OK" fails on heat as well.

### M5. Occlusion by the touching hand overheats the mote

- A hand in the image blocks beams from 1–2 heads. With one head lost the LP overhead rises to h ≈ 4.47 (M4/RT6 "occ").
- Hot face at the gust peak *[RT8 `phys`]*:

  | Room, v 0.5 m/s | T8's mote | Realistic skin |
  |---|---|---|
  | Still | 517 K | 620 K |
  | Quiet office | 547 K | 662 K |
  | **Office** | **655 K** | 819 K |

- Touch happens exactly where heads are blocked. In an office the strokes near a hand fail on heat, in addition to T7's 1–8 cm wake.

### M6. The diffraction floor is quoted at the centre throw

- m19 uses d = 3.95 m. The farthest head-to-image distance in H10 is **4.75 m**, giving 32.0 µm at R 0.11 m and 23.4 µm at R 0.15 m *[RT8 `phys`].*
- The office waist of 31 µm sits below the floor for the far heads. The LP needs those heads for some directions (C3).
- Real channels (M² 1.1–1.3, a wide-field objective) raise the floor further [ESTIMATE].

### M7. The loop model omissions, beyond the statistics in C2

- Mean wind: omitted as committed (×1.1).
- Eulerian sampling: the mote moves through eddies at 0.5 m/s (×1.1).
- Actuator: no pointing lag or noise.
- Gains: tuned for a 1D linear plant, while the loss is a 3D nonlinear profile effect.
- m19b's intra-frame assumption is unstated: the Gaussian factor is held over the frame while the mote moves 25 µm, which assumes the spot is swept continuously along the plan velocity.
- **The force-update model.** m19b applies the Gaussian factor at its frame-start value and passes it through the 30 µs modulator lag. The photophoretic force actually follows the mote's position in the beam within ~2 µs (τ_p 2 µs, thermal lag 0.36 µs). Resolving that raises the office loss rate ~25× (C2 attribution). It is the largest single model correction found here, ahead of the mean wind (×1.1) and motion through the field (×1.1).

### M8. The visible channel: RT7 C1 applies, plus blue content and glints

- **Viewer geometry.** T8's 2 illumination beams per mote serve one viewer direction, because the 1 µm forward lobe is usable to ~15° (RT7). For "several heads in the room", the visible channels per mote scale with the number of separated viewers (×1–2 per viewer), and the emitters must sit behind the image for every viewer, i.e. all round the room (RT7: 66–220 wall positions).
- **Brightness at 10°.** The lobe is fragile *[RT8 `phys`, rt6 BHMIE]*:
  - q = 13–46 over 8–12° and a ±10 % size spread;
  - d ln q/dθ ≈ −0.23 per degree at 10°;
  - so per-mote calibration is needed.
- **Direct beams.** They continue toward the audience. At ~17–35 µW each they are eye-safe, but a bystander in a beam sees a bright glint that sweeps as the motes move.
- **Blue content.** Iron-Man holograms are blue-cyan. At the 30 000 s display time base the photochemical Class 1 limit is 3.9×10⁻⁵·C3 W [memory, IEC Table 3]: **39 µW at ≤ 450 nm**, 98 µW at 470 nm, 390 µW from 500 nm. T8's 35–43 µW per pupil (sketch) and ~46–59 µW (film) are at or over the limit for deep blue.
- **Lit rooms.** These need ~10× more light (T8's own statement), so visible Class 1 fails.

### M9. Flicker: 30 Hz POV is below fusion at these duty cycles

- Each point of a 1 mm line is lit for 1 mm/v = 2 ms (0.5 m/s) to 1.2 ms (0.8 m/s) per refresh: **duty 3.8–6 % at 30 Hz** *[RT8 `misc`]*.
- That is a 100 % modulated 30 Hz train. Critical fusion rises with log luminance (Ferry–Porter) and reaches ~90 Hz in the periphery [search].
- 30 Hz with 4–6 % duty will flicker visibly, and phantom-array breakup appears during saccades.
- T8 lists flicker as an open item, but its own m19 table fails at 60 Hz (diffraction). The design sits between visible flicker and the diffraction floor.

### M10. Indium release scales with the loss rate, and the loss rate is not small

- An ITO-island skin of 100–150 nm at 60 % fill on a 1 µm mote carries **4–6 pg of In**.
- Steady state in a 30 m³ room (0.5 ACH plus 0.2 /h deposition), sketch with 526 motes *[RT8 `misc`]*:

  | Loss rate per mote | Indium in room air |
  |---|---|
  | 0.03 /s | 0.011–0.016 µg/m³ |
  | 0.11 /s | 0.040–0.060 µg/m³ |
  | 0.19 /s | 0.069–0.10 µg/m³ |
  | 1 /s | 0.36–0.54 µg/m³ |
  | 10⁻⁴ /s | ~10⁻⁴ µg/m³ |

- Japan's acceptable occupational concentration is 0.3 µg In/m³ (respirable, 8 h workers [search]). The simulated rates of 0.03–1 /s give **4–180 % of that limit**, and more for 24 h home exposure.
- At the 10⁻⁴ /s target it is negligible. The toxicology item is therefore not separable from C2.
- This assumes every "lost" mote leaves the system. A recapture mode would lower it.

### M11. Sensing at 20 kHz is photon-feasible but unbuilt, and its latency is not budgeted

- *[RT8 `chan`, rt6 BHMIE]* A descanned (confocal) quadrant detector in each channel collects the mote's backscatter through the 0.22 m head aperture. At 5 mW per beam and w 35 µm that is **890–8 200 photons per 50 µs frame** (weak to strong absorber), a shot-noise σ of 0.2–0.6 µm.
- So T6 I6's "far-side quadrant" is not needed, which is good. A far-side detector cannot follow a sweeping beam anyway.
- Not shown:
  - background from the beam's own optics, air, dust and other motes in the confocal volume;
  - 3D fusion of 3–10 channels per mote;
  - a ≤ 100 µs end-to-end latency (exposure, readout, centroid, LP, steering command) in 3 000–6 000 channels.
- RT7: a camera at 90° to visible light gets ~2 photoelectrons, so cameras must sit in the forward lobes.
- C2 shows the converged loop needs ~2 µm per axis at w 34. The descanned shot-noise floor allows that, so sensing is not the first wall; the force instability is.

---

## Minor

1. **Rule-1 bookkeeping.** m19 compares a 3.5 mm pass (0.10 mJ) with the 1 mm limit (7.85 mJ). The 1 mm pass is 0.029 mJ (276×). The conclusion is unchanged.
2. **Stall time.** T8 uses 7.85 mJ for all t. Against the t-dependent AEL a 15.9 mW stall takes 1.65 s (0.3–0.8 s at the authority cap). T8 is conservative.
3. **(1 + u/v).** It uses mean |u|, which over-counts (E|v·t̂ − u|/v ≈ 1.06 in an office). The windowed draft (RT7 M2) adds ≤ 13 %. Net: slightly conservative.
4. **h_worst in E/L.** m19 uses h_worst = 2.14 everywhere. Along real tours the LP-weighted h is 1.2–1.4, so T8's E/L is ~1.6× pessimistic per focus. This is more than cancelled by C1.
5. **M17 inputs.** M17's stacking uses H14 (14 heads), not H10, and an approximate capture (−11 % on a crossing). Both bias s′ low.
6. **Visible per-pupil formula.** m19 uses the IR stacking s′, but visible beam directions are set by viewer geometry, not by the force LP.
7. **m19's "A = 0.5".** It holds J₁/A fixed, so it understates heat (M4).
8. **The circle path.** m19b's 2.7 mm circle exercises every force direction each refresh. It is a stress test, not a stroke.
   - Straight tour strokes use 3.3–3.9 heads per 33 ms (p90 4–5).
   - The union over gust directions along a tour is 5 heads in still air and 9 in an office.
   - Loss rates on straight strokes are about the same as on the circle (still 0.065 vs 0.040 /s; office 0.68 vs 0.56 /s, first-pass model).

---

## T8's update box (commits 0c37dcc, f7c83fe, added during this review), checked

| Update claim | Verdict | Evidence |
|---|---|---|
| "Mean wind holds for POV": office 2/20 lost at w 35 µm, 0/20 at 50 µm | **REFUTED** at w 35, **PARTLY** at 50 | 20 motes × 3 s cannot show this. m19b's own code, longer: 4/20 in 104 mote-s (0.038 /s). RT8 converged force: 3.6–9.9 /s at 35 µm; at 50 µm 0/100 in 980 mote-s (force held per frame) and 1/40 in 92 (resolved) |
| Realistic mote → 21–24 µm sketch spots, R ≥ 0.15 m | **CONFIRMED** (arithmetic), but optimistic | With C1's content stacking the outline needs a further ÷2–3 in power, so ~11–16 µm |
| 20 µm spots hold at **40 kHz with 2 µm** sensing | **PARTLY** | RT8 converged force: still 0/40 in 72 mote-s (≤ 0.05 /s, unbounded below); quiet office 3/40 in 69 mote-s (0.044 /s, 95 % 0.009–0.13) |
| 20 µm spots hold at **20 kHz with 1 µm** sensing | **REFUTED** | RT8 converged force, still: 19/40 in 51 mote-s (0.37 /s) |
| 25 µm spots hold at 20 kHz with 2 µm sensing | **REFUTED** | RT8 converged force, still: 35/40 in 17 mote-s (2.1 /s) |
| EN 50689 skin rule; strict-reading stall cut ~0.7 ms | **CONFIRMED** | M1 (margins 0.75 and 1.29; cut 0.57–0.98 ms) |
| Visible illumination (RT7 C1) applies to T8 | **CONFIRMED** | M8 |
| "Strokes that move along themselves" need an Eulerian assignment | **PARTLY**: it is broader | C1 applies to *static* content too. Every POV mote moves along its stroke, and the minimum-power beams run along it. The dose map is needed for all POV content, not only for self-moving strokes |

So the update's new requirement ("~40 kHz with ≤ 2 µm, or 20 kHz with ≤ 1 µm") survives only as 40 kHz with ≤ 2 µm in still air. Even that is bounded only at ≤ 5×10⁻² /s, and real content under Class 1 needs ~11–16 µm, not 20 µm (C1).

## Corrected design table (sketch, 5 m, 30 Hz, v 0.5 m/s, H10)

Each row adds corrections to the one above. Losses are per mote.

| Case | Class-1 w | Diffraction floor (R 0.11 / 0.15 m) | IR power | IR + visible channels | Loop at that w (20 kHz) | Verdict |
|---|---|---|---|---|---|---|
| T8 as published | 34.3 µm (still), 31 (office) | 26.6 / 19.5 (centre throw) | 4.4 W | 3 158 (6 per mote) | "0/20" (36 mote-s) | (as claimed) |
| + IR ×1/duty, far-throw floor | same | **32.0** / 23.4 | 7.7 W | — | — | Office w 31 < 32: fails at R 0.11 |
| + LP-allocated beams, random arcs or segments | 19–21 µm | 32.0 / 23.4 | ~7.7 W | — | w 25: 39/40 lost | **Fails** (diffraction, loop) |
| + stacking-aware scheduler (θ_min 20°), random content | 33.9 µm | 32.0 / 23.4 | ~9 W (h 1.58) | 526 × (4–5 IR + 2 vis) ≈ 3 200–3 700, plus a multiplexer (C3) | still 34 µm: 0.2–0.7 /s at 4 µm sensing; ≤ 0.04 /s at 2 µm (0 events) | Marginal: diffraction at R 0.11; loop unproven |
| + the project's outline: planar at centre / rotated off the head plane | 16–17 µm / 22–23 µm (best scheduler) | 32.0 / 23.4 | — | — | w 25: 39/40 lost | **Fails** at R 0.11; R 0.15 borderline at the far throw |
| + realistic skin (RT7 C2) | ÷ √2 of each row | — | — | — | — | **Fails** at R 0.11, needs R ≥ 0.2–0.3 m |
| + EN 50689 child-appealing | ≤ 30 µm (A 1), 19–21 (A 0.5) | — | — | — | — | Binds once stacking is scheduled away |
| Office drafts | — | — | — | 526 × (5–7 IR + 2 vis) plus a multiplexer (C3) | 0.03–10 /s at w 31–35; 0.011 /s at w 50 | **Fails** (loop, heat with realistic skin or occlusion) |

**What a consistent POV design would need** (none of it shown to exist):
- **Still air** (σ_u ≲ 0.03 m/s).
- **A certified dose-map governor** with stacking-aware allocation. Head layouts without heads on the image axis, or sparse content.
- **Heads with R ≳ 0.25 m** (a floor ≤ 13 µm at 4.75 m), to reach the 15–20 µm waists that compact content needs under Class 1, and ~2× smaller with the realistic skin.
- **A carry loop whose total delay is ≪ w²/(4·v·δ).** That is ≈ 60 µs at w 16 µm, δ 2 µm, v 0.5 m/s: ≥ 50–100 kHz with sub-frame latency and ≤ 2 µm sensing. Nothing here simulates it.
- **A mode-selective multiplexer in every head:** hologram-class, or a positioner array that gives up animation.
- **Visible channels per viewer cluster** (RT7 C1).

---

## What T8 should say instead

> The crossing-rate rule (rules 1 + 2 at a fixed aperture, no C5 above 1400 nm) is the right framework for moving foci, so B9 does not bound POV. But the time-mean pupil load must be computed on the actual content with the actual allocation: minimum-power beams run along their strokes and stack 3–9× above a random-head estimate. No design point yet combines Class 1 on real content, a waist above the head diffraction floor, a loop with < 10⁻⁴ /s losses, and a channel count matched to the controller. POV-X is a research direction, not a physics-consistent full-vision candidate.

## What to fix first (value of information)

1. **The dose-map governor plus stacking-aware allocation, on real content.**
   - Make the exposure computation (`rt8_check.expo_case`) the design constraint.
   - Find, for the project's armor and an animated scene, the largest w and the LP-cost price at which every 3.5 mm and 1 mm cell passes over 10 s windows.
   - Try head layouts without a head on the image axis.
   - This decides C1, which is the cheapest item to settle (software only).
2. **Long loop runs at T8's own waists** (31 µm office, 34 µm still): ≥ 3×10⁴ mote-s, with the Gaussian force resolved within the frame (≥ 16 substeps), mean wind, actuator lag, a model-based predictor and recapture. Report image dropouts per second, and map the stable region in (w, sensing noise, loop delay). The scaling to test is delay ≪ w²/(4·v·δ). This decides C2.
3. **Channel architecture.** Name the mode multiplexer that puts ~300–500 independently steered single-mode channels through one 0.22 m head: a hologram/SLM, a positioner array, or AODs. Simulate the loop with the beams that multiplexer can deliver. Count channels per head at the p90 heads-per-window. This decides C3 and whether animation survives.
4. **Standards opinion** from a test house on three points: the crossing-rate classification of moving µm foci; the scope of the ICNIRP small-beam footnote; and the EN 50689 skin criterion for a mote display.
5. **Bench**: opus's Test B (galvo rig, E/L invariance, stall cut). Add a straight 20 cm stroke aligned with its own beam, and measure the time-mean power in a 3.5 mm aperture at the stroke's end. Prediction: f_r·(E/L)·~0.2 m, against T8's f_r·(E/L)·3.5 mm.

---

## Sources

**Web (this review, 8 of 8 searches)**
- ICNIRP 2013, cornea > 1400 nm: "for beam diameters less than 1 mm and pulse durations less than 0.35 s, the actual (non-averaged) radiant exposure should be compared" (search summary of the 2020 Health Physics comments and the guideline):
  - [Comments on the 2013 ICNIRP Laser Guidelines, Health Physics 2020](https://journals.lww.com/health-physics/Fulltext/2020/05000/Comments_on_the_2013_ICNIRP_Laser_Guidelines.5.aspx)
  - [ICNIRP 2013 laser guidelines (ResearchGate)](https://www.researchgate.net/publication/286515036_ICNIRP_Guidelines_on_Limits_of_Exposure_to_Laser_Radiation_of_Wavelengths_between_180_nm_and_1000_mm)
- C_P = 1 for α < 5 mrad for pulses longer than T_i; C_P applies only to retinal thermal limits, not skin or cornea:
  - [Health Physics comments (Ovid)](https://www.ovid.com/jnls/health-physics/fulltext/10.1097/hp.0000000000001154~comments-on-the-2013-icnirp-laser-guidelines)
  - [Multiple-pulse retinal explant thresholds, PMC7747910](https://pmc.ncbi.nlm.nih.gov/articles/PMC7747910/)
- IEC 60825-1 multiple-pulse and scanned-emission evaluation (search snippets only; the full text was blocked):
  - [Seibersdorf white paper](https://www.seibersdorf-laboratories.at/fileadmin/user_upload/docs/le/las/publ/whitepaper_iec-60825-1_v1d.pdf)
  - [DTIC ADA614650](https://apps.dtic.mil/sti/pdfs/ADA614650.pdf)
- EN 50689:2021 consumer laser products; skin-accessible emission through a 1 mm aperture with a 10 s time base (> 400 nm) (snippets):
  - [Nemko](https://www.nemko.com/blog/new-european-standard-for-safety-of-lasers-in-consumer-products)
  - [BACL](https://baclcorp.com.cn/show.asp?para=en_2_49_4794)
  - [ILSC 2023 abstract](https://pubs.aip.org/lia/ilsc/proceedings-abstract/ILSC2023/2023/L0602/3298026)
- Japan's ITO guideline: target 10 µg In/m³ respirable, acceptable 0.3 µg In/m³; indium lung disease:
  - [NCBI Bookshelf NBK543196](https://www.ncbi.nlm.nih.gov/books/NBK543196/)
  - [Ind. Health 2018-0116](https://www.jstage.jst.go.jp/article/indhealth/57/3/57_2018-0116/_article)
  - [PMC6258755](https://pmc.ncbi.nlm.nih.gov/articles/PMC6258755/)
- Critical flicker fusion: Ferry–Porter; peripheral CFF saturating at ~90 Hz:
  - [PMC10057432](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10057432/)
  - [Scholarpedia](http://www.scholarpedia.org/article/User:Eugene_M._Izhikevich/Proposed/Flicker_fusion)
- DESI fibre positioners: 10.4 mm pitch, 6 mm patrol radius, 5 000 fibres in < 45 s:
  - [MNRAS 450, 794](https://academic.oup.com/mnras/article/450/1/794/998008)
  - [AJ, DESI focal plane](https://iopscience.iop.org/article/10.3847/1538-3881/ac9ab1)
- Photochemical Class 1 limit (3.9×10⁻⁵·C3 W for t > 100 s): **[memory]**. The search did not return the table.

**Repository (read-only)**
- `09_unlock/`: `T8_pov_crossing.md`, `m19_pov_crossing.py`, `m19b_pov_track.py`, `T7_gaussian_voxels.md`, `idea_round_3_opus.md` §2.2 and §4, `idea_round_3_sonnet.md` §1, `m17_exposure_field.py`, `m18*.py`, `rt6_check.py`, `rt7_check.py`;
- `07_mote_route/R7_mote_safety.md` (K4–K7, S2–S3, "Moving and scanned traps");
- `04_engineering/holo_engine/mote_plan.py` and `content.py`;
- `05_reviews/red_team_6_lcsv.md` and `red_team_7_gaussian.md`.

# Red team 7: Gaussian static voxels, forward-scatter illumination, bound B9 and the hologram-rate loop (T7, M18)

**Scope.** Reviewed on 2026-10-01:
- `09_unlock/T7_gaussian_voxels.md`, including the later additions (spot-following, §5.7 touch and air);
- `m18_gaussian_lcsv.py`, `m18b_holo_loop.py`, `m18c_vector_pin.py` (fixed spots and `follow=True`), `m18d_touch_air.py`, with `results/m18*.log/json`;
- background: red team 6, `rt6_check.py`, `m17_exposure_field.py`, `07_mote_route/mote/physics.py`, R9, idea round 3 (opus) and T8 only where they change a T7 statement.

**Method.** All numbers marked *[RT7]* come from `09_unlock/rt7_check.py` (one section per claim). Results are in `09_unlock/results/rt7_*.json` and the console log is `results/rt7_run.log`.
- Written here, independently of the T7/RT6 code:
  - air properties (Sutherland; the US-Standard-Atmosphere conductivity; the Kim et al. slip correction);
  - the photophoretic force, re-derived from thermal creep (a "squirmer" with creep slip), with temperature jump and velocity slip;
  - the heat balance, a thin-film/skin absorber model (characteristic matrix, s and p) and a straight-ray volume absorber;
  - Mie (own code) plus an anomalous-diffraction cross-check;
  - LP allocation by hull equations;
  - a 3D von Kármán–Pao turbulence model with longitudinal and transverse spectra **and a mean wind**;
  - a PID tuner (closed-loop eigenvalues plus modulus margin);
  - a vectorised 3D pinning simulator (Gaussian profile with Rayleigh range, lateral photophoretic force, gain scheduling, per-beam authority, fixed or followed spots, exposure-averaged or instantaneous sensing);
  - an exact (non-central χ²) pupil-capture code for stacking;
  - an I9 layer-crosstalk model on stroke content.
- T7/RT6 code is imported only in marked cross-check lines. T7's own simulator was also run once with the mean wind patched in memory (no file edited).
- **Double validation:**

| Check | RT7 | T7 / RT6 / project | Agreement |
|---|---|---|---|
| I_unit, 1 µm ITO mote, slip, C_ph 0.85 | 7.34×10⁶ W/m² per m/s | m18.hold 7.30×10⁶ | 1.006 |
| Mie self-test (Bohren–Huffman case) | Q_ext 3.1054 | 3.1054 | exact |
| Mie q_iso, a 1 µm, 10/15/20/90° (±2.5°) | 24.6 / 5.00 / 0.258 / 3.67×10⁻³ | RT6 BHMIE 24.5 / 4.96 / 0.249 / 3.68×10⁻³ | ≤ 4 % |
| Anomalous diffraction vs Mie, a ≤ 1 µm, 10–15° | | | 1–12 % |
| Volume absorber, αa = 2 | A 0.887, J₁/A 0.229 | physics.py 0.886 / 0.229 | ≤ 0.1 % |
| LP allocation vs scipy linprog | | | 4×10⁻¹⁶ |
| PID tuner, MEMS 5 kHz, 2 frames, 4 µm | σ 1.28 µm, M_s 1.30 | rt6.tune σ 1.44 µm, M_s 1.38 | 12 % |
| Loop, MEMS 5 kHz, w 50 µm, still | 0/200 lost in 11 940 mote-s, r_p99.9 6.9 µm | m18c long 0/60 in 8 988, 6.5 µm | agree |
| Loop, MEMS 5 kHz, w 50 µm, quiet office **without** mean wind | 1/200 in 11 913 | m18c 0/60 in 1 188 | agree |
| Mean-wind effect (U 0.1 m/s), MEMS 5 kHz w 50 / PLM w 70 | 122/200 / 163/200 lost | m18c patched: 2/30 / 24/30 lost (0/30 without) | same sign, both fail |
| Pupil capture, same motes, beams and probes | worst 3.78 | m17 3.32 | +14 % (m17's capture approximation) |
| Class 1 waist at T7's conventions | 50 / 42 / 33 µm (sketch), 40 / 33 / 26 (film) | m18 51 / 43 / 33, 40 / 34 / 27 | ≤ 4 % |
| Hot face at gust peaks (still, home, quiet office, office) | 327 / 337 / 348 / 419 K | 330 / 341 / 352 / 429 K | ≤ 3 % |

Facts from recall are marked **[memory]**. Six web searches were used; the sources are at the end.

**Severity counts:** 3 critical, 10 major, 12 minor.

---

## Summary

**T7's arithmetic and its core physics reproduce.**
- B2/I_unit, the slip penalty, the heat at gust peaks, the forward-scatter Mie table, the Gaussian mode-count rule, the B9 algebra and the Class 1 numbers at 1500–1800 nm all reproduce.
- The still-room loop result (MEMS 5 kHz, 2 frames, w = 50 µm) reproduces: 0/200 lost in 11 940 mote-s, so the rate is < 2.5×10⁻⁴ /s.

**Three findings change the bottom line.**

1. **The visible side does not scale (critical).**
   - The forward lobe of a 1 µm mote is usable only to ~15° (first null at 20.2°; a ±10 % size spread drops q below 2 beyond 15.4°), not "10–25°".
   - Every viewer needs emitters behind the image within that cone. For viewers anywhere on a ring, that takes **66 wall emitters (95–98 % of viewer–mote pairs covered) to 220 (99.7 %)**, not ~15.
   - Each emitter needs (2·clip·os·L/(π w_v))² = **1.4×10⁹ (w_v 34 µm) to 7.6×10⁹ (w_v 14.4 µm, T7's choice)** modes.
   - The visible engine is therefore **0.9×10¹¹–1.7×10¹² modes**, 7–125× the corrected IR engine, not "×1–2".
   - Each active emitter sits in its viewer's view, 2–10° from the image point it lights. A GS-level non-signal fraction (25 %) makes it glow at ~370 cd/m², so the non-signal light must be held to ≲ 10⁻³.
   - The direct beams terminate on the audience and the wall behind it, so T7's stray-light number (leak 10⁻²) does not apply.
2. **The mote's A ≈ 1 with J₁/A = 0.486 is not a physical skin (critical).**
   - A homogeneous absorbing skin ≤ 150 nm thick on a 1 µm sphere reaches at most **A 0.61 and J₁ = A·(J₁/A) 0.26**, against the assumed 0.486. The cause is the thin-film absorption ceiling (≤ 50–56 % per pass) and back-side heating.
   - A continuous Drude-ITO skin gives J₁ ≤ 0.1.
   - With a realistic J₁ ≈ 0.24, I_unit doubles (1.49×10⁷). This is exactly T7's own "A = 0.5" case, which T7's table shows failing almost everywhere.
3. **The fixed-spot loop simulations leave out the mean wind (critical).**
   - In m18b/m18c, "home" and "quiet office" differ from "still" only by the Taylor convection speed. The drafts have zero mean, and the authority is capped at 5.4σ.
   - With U = 0.05–0.10 m/s included (and the authority raised to U + 5.4σ), MEMS 5 kHz at w = 50 µm loses **6×10⁻³ /s (home) and 1.7×10⁻² /s (quiet office)**. PLM 1-frame at w = 70 µm loses 3.7×10⁻² /s.
   - T7's own simulator agrees when patched: 2/30 and 24/30 lost, against 0/30 without the mean wind.
   - **Spot-following fixes the first of these:** MEMS 5 kHz, follow, w = 50 µm, quiet office with mean wind: 0/200 in 11 940 mote-s.

**Major corrections.**
- **B9 is a mode-count/aperture bound, not a physics bound.** v_max·M_head is invariant: 7.5×10⁻¹¹ m/s per pixel per head at T7's conventions. This agrees with opus round 3.
- **"Only mean power counts" needs a window rule.** The 10 s running mean of the holding power reaches 1.45–1.83× its long-term mean (p99.9, still and home rooms). T7's use of h_worst happens to cancel this; the time-mean h proposed by opus and T8 does not.
- **Stacking depends on content.** Lines aimed at a head stack 34–50 P_unit in one pupil, against T7's 7.1. A stacking-aware allocation fixes this at an LP-cost price.
- **The real H10 field needs 2.2× T7's mode count:** 1.34×10¹⁰ at w = 51 µm.
- **I9 crosstalk is heavy-tailed.** On strokes, 23–28 % of a head's sketch motes share their own modulating pixel with another mote (4 layers), and 36–49 % in film. That is not 0.1–0.5 %.
- **The sensing photon budget holds only in a forward lobe.** A camera at 90° to visible light collects 2 photoelectrons per frame. Infrared scatter from the trap beams at 20–40° works (0.4–2.7 µm).
- **Loop margins are thin:**
  - +½ frame of latency raises losses to 1.2×10⁻³ /s;
  - 8 µm sensor noise loses 98 % of motes in 15 s;
  - the MEMS 10 kHz loop floors that two of T7's three passing rows rely on were never simulated (RT7: home w 40 µm 8.4×10⁻⁵ /s; still w 35 µm 2.5×10⁻⁴ /s).

**Corrected outlook** (table at the end).
- Random content in a still room (sketch, and film density) stays physically consistent **with an ideal (A ≈ 1) mote and a ≥ 5 kHz spot-following loop**. A 10 kHz fixed-spot loop also works for the sketch, and marginally for film.
- With a realistic thin-skin mote, the Class 1 waist falls to 30 µm (sketch, still). Only 5 kHz spot-following holds it among the cases tested (1/200 lost in 11 891 mote-s, rate ≤ 4.7×10⁻⁴ /s at 95 %).
- With the realistic mote, film density and every non-still room need waists of 18–26 µm, below every loop RT7 verified, so they are unverified or failing. The quiet office fails even with the ideal mote.
- In every case the engine is ~2–4×10¹⁰ IR modes **plus 10¹¹–10¹² visible modes**.

### Verdict per claim

| Claim (T7 / m18*) | Verdict | One-line reason |
|---|---|---|
| §1.2 q_iso table (n 1.04 + 10⁻⁴i, 500 nm) | **CONFIRMED** | Own Mie within 0–4 %; ADA within 1–12 % at 10–15° |
| §1.2 15° operating point; ±10 % spread or 8–10° as remedies | **PARTLY** | 15° is on the steep flank (d ln q/dθ = −0.44 per degree), not at the null (20.2°). The spread does not smooth per-mote brightness (2.6–5.5 at 15°). 8–10° works (±15 %) |
| §1.2 illumination 10–25° from behind; ~15 emitters; visible modes ×1–2 IR | **REFUTED** | Window ≤ 15° for 1 µm; 66–220 wall emitters for a ring of viewers; 0.9×10¹¹–1.7×10¹² visible modes |
| §1.2 visible spots 10–20 µW within Class 1 with 3.3× stacking | **CONFIRMED** | 10.7 µW × 3.3 × 2 = 71 µW ≤ 390 µW; holds up to ~10 viewer beams per mote |
| §1.2 little stray light (0.07 W, 0.0008 cd/m²) | **REFUTED** as stated | Leak 10⁻² assumes receivers, but the direct beams land on the audience. Wall light is 0.079 cd/m² (sketch), 8× the criterion, plus emitter glow |
| §1.1 M_head = (2·clip·os·L/(πw))², 4.1× the étendue minimum | **PARTLY** | Right for a paraxial L×L field. The real H10 field needs 2.2× (1.34×10¹⁰ at 51 µm) |
| §1.1 "~8× fewer modes than RT6 flat-tops at equal conventions" | **CONFIRMED** | 6.9× (T7's os and square aperture) to 9.9× (bare), at w = r_c and ρ = 1. At the design points the gain is ~1× after the geometry fix |
| §1.1 clip 1.2, os 1.5, envelope 0.65 | **PARTLY** | Clip passes 0.967. os 1.5 puts replicas ≥ θ_half outside the field. The envelope is 0.79 (0.77 harmonic), not 0.65 (the code uses 0.79). The zero order is not addressed |
| §2 B9 algebra, I_unit 7.3×10⁶ (slip) / 5–6×10⁶ (no slip) | **CONFIRMED** | 7.34 / 5.31×10⁶. The creep coefficient spans ±25 % (K 0.75–1.17 gives 9.4–6.0×10⁶) |
| §2 Class 1 basis (10⁴ J/m² to 10 s, 1 mm < 0.35 s; 1000 W/m² over 3.5 mm) | **CONFIRMED** | [memory] plus search: MPE 0.1 W/cm² and a 1.5·t^0.375 mm aperture at 0.35–10 s; AEL = MPE × aperture |
| §2 "only mean power counts; ms surges harmless" | **PARTLY** | ms surges are harmless (≤ 0.35 s: 7.85 mJ). Every duration must pass: the 10 s window reaches 1.45–1.83× the mean |
| §2 stacking s 3.3 / 5.2 (M17) | **PARTLY** | Random content, LP-weighted time-mean: 6.3 P_unit against T7's h·s 7.1 (OK). Lines aimed at a head: 34–50 (×5–7). m17 uses H14 and an approximate capture |
| §2 B9 independent of mote size | **CONFIRMED** (slip aside) | I_unit 9.0 / 7.3 / 6.3 / 5.95×10⁶ at 0.5 / 1 / 2.5 / 5 µm |
| §2/§5 "B9 is a physics bound; fast animation excluded under passive Class 1" | **REFUTED** as framed | v_max ∝ 1/w² ∝ modes: 1 m/s needs ~1.3×10¹⁰ px/head (w 11 µm, ~0.5 m apertures) plus B8. For holographic static voxels B8 binds; for POV see T8 |
| §2 FOM ceiling 7–11, lever ×1.4–2 | **PARTLY** | Ceiling 6.8–13.9 m·K/W. But a realistic skin has J₁ ≈ 0.24, so today's mote sits 2× below T7's |
| §1.3 hot face 330–430 K; slip ×1.39 | **CONFIRMED** | 327–419 K (occluded 355–511 K); slip penalty on the force ×1.37 |
| §1.3/§4 A ≈ 1 plausible; A = 0.5 a side case | **REFUTED** | Skins ≤ 150 nm: A ≤ 0.61, J₁ ≤ 0.26. A = 0.5 (J₁ 0.243) is the realistic case. With J₁/A 0.30 the office, occluded, reaches 610 K > 573 K |
| §3 profile-instability rate F·4r/w² | **CONFIRMED** | Derivative of the Gaussian deficit. This is also why the mean wind matters |
| §3 facet = LP optimum | **CONFIRMED** | Hull-equation allocation equals linprog to 4×10⁻¹⁶ |
| §3 MEMS 5 kHz (2 frames) holds w 50 µm in still air | **CONFIRMED** | 0/200 in 11 940 mote-s (< 2.5×10⁻⁴ /s); lateral force included |
| §3 fixed spots hold in home / quiet office (MEMS 3–5 kHz, PLM 1 frame) | **REFUTED** | Mean wind omitted. With it: 6.0×10⁻³ /s (home), 1.7×10⁻² /s (quiet office), PLM 3.7×10⁻² /s |
| §3 spot-following (later addition) | **PARTLY** | Holds MEMS 5 kHz at w 50 (quiet office, mean wind) and w 30 (still), and PLM 1 frame at w 50 in still air. MEMS 3 kHz loses 4.9×10⁻³ /s (w 35, still) and 9.3×10⁻³ /s (w 50, quiet office). Failure modes in M6 |
| §3 MEMS 10 kHz loop floors (35 / 40 µm) used in §4 | **UNVERIFIED in T7 → PARTLY** | RT7: home w 40 µm 8.4×10⁻⁵ /s (OK); still w 35 µm 2.5×10⁻⁴ /s (marginal) |
| §3 PLM 1.44 kHz as a candidate | **PARTLY** | It holds w 70 µm in still air (1/200). But TI's PLM reaches 2π only for 405–650 nm (T7 now says ~30 % efficiency at 1550 nm) |
| §3 sensing 4 µm at 5 kHz; photon budget 4 500 per frame | **PARTLY** | True only in a forward lobe (visible 15°: 3 200 photoelectrons) or with IR trap-beam scatter (1.1–6.6×10⁴). A visible camera at 90° gets 2.3 |
| §3 lateral force | **omitted, minor** | F_lat/F_ax = 1.5·a·ρ/w² outward. It changes r_p99.9 from 6.9 to 7.3 µm at w 50 |
| §3 I9 geometry (m², 0.9 mm layers) | **PARTLY** | Algebra right for 0.8 m. Corner heads see 1.6 m of depth (7.4 mm intermediate); m varies 12–18× (10–22× for near heads) |
| §3 I9 crosstalk 0.1–0.5 % | **REFUTED** for strokes | Median ~0, but 24–26 % of motes > 1 %, 13–16 % > 10 %, and 23–28 % own-pixel conflicts (sketch, 4 layers); film 36–49 % |
| §3 I9 étendue and speed | **PARTLY** | The real field has 2.8× T7's étendue. DHF-FLC at ~100–235 µs is plausible; π-cells (∝ d²) are not at 1550 nm. A 5–10 kHz transmissive active matrix (≤ 0.1–0.2 µs row time) does not exist |
| §4 "design points that pass every check" | **REFUTED** as complete | Missing: visible modes, mean wind, realistic mote, aligned stacking, H10 field ×2.2, latency margin. Unsimulated: the 10 kHz floors |
| §5.7 touch and air | **CONFIRMED** (order of magnitude) | Potential flow and plume numbers check. A warm-hand plume is a *mean* wind, so fixed spots fail there as well (C3) |
| §5 walls ranking | **PARTLY** | The visible engine and the mote absorber move above B9. B9 becomes a modes × content bound |

---

## Independent recomputation of T7's key numbers

| Quantity | T7 | RT7 | Note |
|---|---|---|---|
| I_unit (1 µm, slip / no slip) | 7.3 / 5–6 ×10⁶ | 7.34 / 5.31 ×10⁶ | K 0.75–1.17 gives 9.4–6.0 ×10⁶ |
| Slip penalty on F_ph at 1 µm | ×1.39 | ×1.37 (s = 0.728) | Cc(1 µm) 1.074 |
| Hot face (still / home / quiet office / office) | 330 / 341 / 352 / 429 K | 327 / 337 / 348 / 419 K | Occluded: 355 / 373 / 390 / 511 vs T7 368 / 390 / 411 / 555 |
| B9 v_max at w 15 / 20 / 35 / 50 / 70 µm (h·s 7.1) | 53 / 30 / 10 / 4.9 / 2.5 cm/s | 52 / 29 / 9.6 / 4.7 / 2.4 cm/s | Realistic skin: 26 / 15 / 4.7 / 2.3 / 1.2 |
| q_iso(15°), a 0.75 / 1.0 / 1.5 µm | 5.7 / 5.0 / 2.0 | 5.74 / 5.00 / 2.00 | First minima at 27.1 / 20.2 / 13.4° |
| Modes per head, w 51 µm | 6.06×10⁸ | 1.25–1.67×10⁹ (H10 geometry) | ×2.1–2.8 by head |
| Class 1 waist, sketch, still (T7 stacking) | 51 µm | 50 µm | RT7 stacking + window: 43 µm |
| Loop, MEMS 5 kHz w 50 still | 0/60 in 8 988 mote-s | 0/200 in 11 940 mote-s | Together < 1.4×10⁻⁴ /s |

---

## Critical

### C1. Forward-scatter illumination does not scale to several free-standing viewers, and its visible engine is 10¹¹–10¹² modes

**The usable angular window is narrower than stated** *[RT7 `mie`]*.

| a | q(5°) | q(10°) | q(15°) | q(17°) | q(20°) | First minimum | q(15°) over ±10 % radius | q(17°) over ±10 % |
|---|---|---|---|---|---|---|---|---|
| 0.75 µm | 19.9 | 12.8 | 5.7 | 3.7 | 1.5 | 27.1° | 4.9–5.8 | 3.1–3.5 |
| 1.0 µm | 54.5 | 24.6 | 5.0 | 1.8 | 0.26 | 20.2° | **2.6–5.5** | **0.42–2.4** |
| 1.5 µm | 186 | 27.5 | 2.0 | 2.5 | 1.4 | 13.4° | **0.47–4.5** | 1.4–3.5 |

- At 15°, a 1 µm mote sits on the steep flank: d ln q/dθ = −0.44 per degree and d ln q/d ln a = −2.4. A 1° geometry error changes its brightness by 55 %.
- Each mote has *one* size, so a ±10 % batch spread shows up as a ×2 (15°) to ×6 (17°) mote-to-mote brightness variation, not as a smoothed lobe. Correcting it needs a per-mote, per-viewer calibration (sizing each mote from its scatter).
- For the worst size in ±10 %, q ≥ 2 holds only up to **15.4°** (1 µm) or 18.3° (0.75 µm). T7's "within 10–25°" in its costs paragraph is outside the lobe: q(20°) = 0.26 and q(25°) = 0.49 for a = 1 µm.
- **T7's second remedy is the right one:** 5–10° gives q 24–55, stable to ±15 % over the spread.

**Geometry for several viewers** *[RT7 `vis`]*.
- Setup: emitters on a wall grid, viewers on a ring at 1.6–2.4 m from the image centre (eye height 1.6 m, ≥ 40° apart), motes random in the 1 × 1 × 0.8 m volume.
- An emitter serves a (viewer, mote) pair if the scattering angle falls in the window and its direct beam beyond the mote misses every viewer's eye by > 2°.

| Window | Wall spacing (emitters) | Pairs covered, 1 viewer | 3 viewers | Emitters useful per viewer |
|---|---|---|---|---|
| 10–20° (T7) | 1.0 m (66) | 97.5 % | 98.4 % | 17 |
| 10–20° (T7) | 0.5 m (220) | 99.9 % | 100 % | 55 |
| 3–15° | 1.0 m (66) | 95.2 % | 96.1 % | 14 |
| 3–15° | 0.5 m (220) | 99.7 % | 99.7 % | 49 |
| 4–10° (stable q) | 0.5 m (220) | 96.0 % | 96.7 % | 41 |
| 4–10° (stable q) | 0.3 m (666) | 98.8 % | 98.4 % | 111 |

- T7's "~15" is the number *one fixed viewer* uses. Viewers who may stand anywhere around the image need emitters installed all round the walls, from floor height to ~1.9 m. The lines from eye to mote reach the far wall at −0.15 to 1.85 m.
- That is **66–220 emitters** at T7's window, and up to ~670 at the stable 4–10° window.

**Modes.**
- T7's own counting rule gives modes per visible emitter (independent of throw): **7.6×10⁹** at w_v = 14.4 µm (T7: twice the pinning residual), 2.5×10⁹ at 25 µm, and 1.4×10⁹ at 34 µm.
- 34 µm is the largest waist that keeps 3.3 × 2 stacked spots within 0.39 mW.
- Installed visible modes are therefore **9×10¹⁰ (66 emitters at 34 µm) to 1.7×10¹² (220 at 14.4 µm)**, against 1.3×10¹⁰ for the IR heads (H10 geometry, M4).
- The visible pixels can be slow (static content), but they must exist. If spot-following is used (M6), the visible spots must follow the mote too, at the loop rate.

**Glow and stray light.**
- Each active emitter lies 3–15° (seen from the mote) behind the image, i.e. 2–10° from the image point as the viewer sees it. The viewer is therefore inside the emitter's own projection cone.
- Non-signal hologram light (speckle, ghosts) heads straight at the viewer. At T7's 4.7 mW per emitter, 0.11 sr field and 80 mm aperture:

| Non-signal fraction | Emitter luminance as seen by its viewer |
|---|---|
| 25 % (GS-level) | 370 cd/m² (2.3 cd) |
| 10⁻² | 15 cd/m² |
| 10⁻³ | 1.5 cd/m² |

- For scale, a whole sketch is 0.015 cd at 3 cd/m² line luminance. The holograms need ≲ 10⁻³ non-signal light in the directions of tracked eyes, a dark-region constraint per eye of ~10⁴ modes. That is feasible in principle but unbudgeted.
- The direct beams continue towards the audience. No black receivers can sit there, so the leak is the room albedo (~0.8), not 10⁻²:
  - wall luminance **0.079 cd/m² (sketch), ~0.6 cd/m² (film)**, against the 0.01 criterion;
  - ~1 cd/m² dots on viewers' faces and clothes from beams 2–3 cm wide at 2 m.
- Dust sparkles are brighter in forward scatter than at 90° [ESTIMATE].

**Fix.**
- Treat the visible engine as a first-class wall: count emitters for the viewing zone and their modes, and weigh the alternatives:
  - restrict viewers to a zone in front of the image (~15–20 emitters);
  - use a non-holographic visible channel (steered beams per mote and viewer);
  - give up uncoated motes for a coat or phosphor.
- Work at 5–10°.
- Add an eye-direction dark-region constraint to the visible holograms.
- Put the audience-side stray light into the luminance budget.

### C2. The mote's absorber: A ≈ 1 with J₁/A = 0.486 is not a physical skin

**Evidence** *[RT7 `phys`]*. These are straight-ray sphere models with a homogeneous skin (characteristic-matrix s/p transmission at each ray's angle): front pass, back pass, and one internal reflection.

| Absorber on a 1 µm sphere at 1550 nm | A | J₁/A | J₁ = A·J₁/A |
|---|---|---|---|
| T7 / m15 "ITO island skin" (assumed) | 1.0 | 0.486 | **0.486** |
| Best homogeneous skin, 50 nm (n 2.7, k 2.8) | 0.56 | 0.38 | 0.21 |
| Best homogeneous skin, 100 nm | 0.57 | 0.41 | 0.23 |
| Best homogeneous skin, 150 nm | 0.61 | 0.42 | 0.26 |
| Best homogeneous skin, 250 nm (t/a = 0.25, no longer a skin) | 0.68 | 0.47 | 0.32 |
| Continuous Drude ITO (N 10²¹ cm⁻³, ε = −2.15 + 0.75i), 50–150 nm | 0.24–0.30 | 0.10–0.33 | 0.02–0.10 |
| Volume absorber, αa 3 / 5 (k 0.37 / 0.62, reflection < 9 %) | 0.95 / 0.98 | 0.29 / 0.36 | 0.28 / 0.36 |

- A single homogeneous film in air absorbs at most 0.50–0.56 per pass up to 150 nm (0.73 at 300 nm) *[RT7 grid over n, k]*. This matches R9's own "≤ 50 % for a sub-λ film" [R9 snippet].
- The light that crosses the index-matched core heats the back skin, which lowers J₁/A.
- M7's straight-ray Beer–Lambert skin (α ≈ 5.7×10⁷ m⁻¹, i.e. k ≈ 7) has **no Fresnel reflection**. A layer that dense is a metal: a k = 7 surface reflects ~90 %.
- Plasmonic islands are electric-dipole sheets and obey the same ~50 % per-pass ceiling. Beating it needs a Huygens-type (electric plus magnetic) resonant skin, conformal on a 1 µm sphere, which is unproven [ESTIMATE].

**Consequences.**
- With J₁ ≈ 0.24, I_unit = **1.49×10⁷** W/m² per m/s, twice T7's value.
  - This is T7's own A = 0.5 case (1.47×10⁷), which fails "except the sketch in a still room at 10 kHz".
  - B9 halves: 2.3 cm/s at w = 50 µm, 4.7 at 35 µm.
  - The Class 1 waist drops by √2: sketch still 43 → **30 µm**; film still 34 → **24 µm** (RT7 stacking).
- **Heat.** With J₁/A 0.30 (the force needs more absorbed power), hot faces rise to 343–473 K, and the office with one head occluded reaches **610 K > 573 K**.

**Fix.**
- Carry J₁ = A·(J₁/A) as one measured number, with A ≤ 0.6 as the default until a "perfect-absorber" skin is shown on a microsphere.
- Make bench B2 measure A and J₁ separately (force per absorbed watt, and absorbed watt per incident).

### C3. The fixed-spot loop simulations omit the mean wind

**Evidence.**
- `rt6.synth_turb` sets S(0) = 0 and normalises to σ, so every draft has zero mean.
- m18b/m18c use U only as the Taylor convection speed U_c.
- m18c caps the authority at 5.4σ·c_max, not (U + 5.4σ)·c_max.
- "Home" and "quiet office" are therefore still air with faster eddies. The steady force F ≈ U that drives the profile instability (rate ≈ F·4r/w²: 800 s⁻¹ at r = 5 µm, F = 0.1 m/s, w = 50 µm) is absent.
- The tuned loops cross over at only 53–90 Hz (333–565 s⁻¹), because the optimum against 4 µm of noise is a soft loop.

**RT7 runs** (own simulator, 200 motes × 60 s, mean wind along a random horizontal direction, authority (U + 5.4σ)·c_max, lateral force on; exact Poisson 95 % intervals):

| Case | Lost | Rate (95 %) | Comparison |
|---|---|---|---|
| MEMS 5 kHz, w 50, home (U 0.05) | 59/200 | 6.0×10⁻³ [4.5, 7.7]×10⁻³ /s | m18c (no mean): 0/60 |
| — same, stiffest tuning (f_c 214 Hz, M_s 1.98) | 4/200 | 3.4×10⁻⁴ [0.9, 8.7]×10⁻⁴ /s | still > 10⁻⁴ |
| MEMS 5 kHz, w 50, quiet office (U 0.10) | 122/200 | 1.7×10⁻² /s | without mean: 1/200 |
| — same, stiffest tuning | 119/200 | 1.7×10⁻² /s | stiffness does not help |
| PLM 1 frame, w 70, quiet office | 163/200 | 3.7×10⁻² /s | T7: "0/60 at 70 µm" |
| MEMS 10 kHz, w 40, home | 1/200 | 8.4×10⁻⁵ [0.02, 4.7]×10⁻⁴ /s | holds |
| MEMS 10 kHz, w 40, quiet office | 83/200 | 9.5×10⁻³ /s | 10 kHz fixed spots do not fix the mean wind |
| MEMS 5 kHz, **follow**, w 50, quiet office | 0/200 in 11 940 | < 2.5×10⁻⁴ /s | spot-following fixes it |
| MEMS 3 kHz, **follow**, w 50, quiet office | 81/200 | 9.3×10⁻³ /s | m18c follow (no mean): 0/60 |
| MEMS 3 kHz, follow, w 35, quiet office | 200/200 in 174 mote-s | 1.1 /s | |
| PLM 1 frame, follow, w 50, quiet office | 144/200 | 2.7×10⁻² /s | m18c follow (no mean): 0/60 |
| MEMS 5 kHz, follow, w 35, home | 3/200 | 2.5×10⁻⁴ [0.5, 7.4]×10⁻⁴ /s | marginal |

- **Cross-check with T7's own simulator.** m18c.simulate, with only the draft generator patched in memory to add U = 0.1 and auth = (U + 5.4σ)/σ:
  - MEMS 5 kHz at w 50: 0/30 → **2/30 lost** in 283 mote-s;
  - PLM 1 frame at w 70: 0/30 → **24/30 lost** in 107 mote-s.
- m18c's 150 s "home" long run (0/60) is the zero-mean draft.
- The same physics applies to §5.7: a warm hand's 0.1–0.4 m/s plume is a steady mean wind at the image.

**Fix.**
- Add U to the draft generator and to the authority in m18b/m18c.
- Re-run the home and quiet-office grids.
- Use spot-following (or 10 kHz) for any room with a persistent mean flow.
- Measure U at the image (T7 §7 item 2).

---

## Major

### M1. B9 is a modes-and-aperture bound, not a physics bound

- From v_max = 2·AEL/(π w²·h·s·I_unit) and M_head = (2·clip·os·L/(πw))²:
  > **v_max = 7.5×10⁻¹¹ m/s per hologram pixel per head** (T7 conventions; 3.4×10⁻¹¹ with the real H10 field, M4).
- So 1 m/s of mean relative speed under passive Class 1 needs ~1.3×10¹⁰ px/head (3×10¹⁰ with the H10 field), i.e. w ≈ 11 µm. The aperture at 4.75 m is then W = λd/(πw) = 0.21 m, i.e. **~0.5 m heads**.
- The loop must hold a 1 µm mote in an 11 µm spot. Spot-following turns that into a sensing and latency problem (σ_n ≪ w), not the profile instability (M6).
- For *holographic* static voxels, content speed is capped first by B8 (w·f/k), not by B9. This agrees with opus round 3 ("B9 in modes"; "excluded for holographic static voxels").
- T7 §2's "physics bound, not an engineering one" and §6's "fast animation excluded under passive Class 1" should be restated as **"a modes × aperture × content bound for holographic static voxels"**. For POV, T8's crossing-rate rule applies (RT8's job).
- **The physics floors behind it:** FOM ≤ 6.8–13.9 m·K/W (J₁/A 0.5–0.75, k_p 0–0.02), against today's 5.2 per absorbed watt. Per *incident* watt, a realistic skin delivers only half of T7's force (J₁ 0.24 against 0.486; C2). Slip is worth ≤ 1.23× (5 µm motes).

### M2. Eye safety: every exposure window must pass, not only the mean

**Class 1 at 1500–1800 nm** [memory; the MPE of 0.1 W/cm² and the 1.5·t^0.375 mm aperture at 0.35–10 s are confirmed by search]. The power-equivalent AEL is:

| t | 0.1 s | 0.35 s | 1 s | 3 s | 10 s | > 10 s |
|---|---|---|---|---|---|---|
| AEL / t | 78.5 mW | 22.4 mW | 17.7 mW | 13.4 mW | 9.9 mW | 9.6 mW |

- The holding power per focus follows |u(t)|, because the mote has no inertia.
- **Running means of |u|, p99.9 over its long-term mean** *[RT7 `b9`, own turbulence model, 40 motes × 2 000 s]*:

| Room | 0.35 s | 1 s | 3 s | 10 s | 30 s |
|---|---|---|---|---|---|
| Still, L 3 cm | 2.48 | 2.28 | 1.88 | **1.50** | 1.27 |
| Still, L 10 cm | 2.53 | 2.47 | 2.26 | **1.83** | 1.47 |
| Quiet office (U 0.1) | 1.75 | 1.59 | 1.39 | **1.22** | 1.13 |

- The binding window is 10 s. A design whose *long-term* mean sits at the AEL exceeds it by 1.2–1.8× in the worst 0.1 % of 10 s windows.
- T7 uses h_worst (2.14). With the LP-weighted time-mean coefficients (h_mean 1.33), random sketch content gives 6.3 P_unit at the worst pupil. Multiplied by the window factor (1.45–1.50), the effective h·s is **9.1–9.4 against T7's 7.1** (quiet office 7.6).
- So T7's B9 is ~1.3× optimistic for random content in still and home rooms, and about right in the quiet office.
- **Note for T8 / opus:** "use the time-mean h" without this window rule is optimistic by 1.2–1.8× for static voxels.

**Fix.** State B9 for the 10 s windowed mean (p99.9) and the time-mean h, or enforce it with a per-pupil power governor.

### M3. Stacking depends on content: lines aimed at a head

*[RT7 `b9`, `b9fix`; exact pupil capture, w = 50 µm, LP-weighted time-mean beam powers, P_unit = (πw²/2)·I_unit·E|u|.]*

| Content | Worst pupil (P_unit) | ×T7's 7.1 |
|---|---|---|
| Random arcs, sketch (1 659 motes) | 6.3 | 0.9 |
| Vertical line on the central axis (under the ceiling and over the floor head) | **49.5** | 7.0 |
| Same, 1 cm off axis | 36.1 | 5.1 |
| Same, 3 cm off axis | 14.3 | 2.0 |
| Line aimed at a corner head | **33.8** | 4.8 |
| On-axis line at w 25 / 70 µm | 31 / 58 | 4.4 / 8.2 |

- A pupil on such a line collects the co-axial beams of every mote within ~z_R·(R_ap/w) ≈ 18 cm.
- Wireframes are full of vertical lines, and H10 has heads directly above and below the volume centre.
- The co-axial beams also cross neighbouring motes at 3 mm, at ~74 % of their focal intensity. That couples the force on neighbouring motes.
- **Fix (works).** Stacking-aware allocation: for each mote, drop the heads within 2° of its stroke direction.

| Content | Worst pupil | h_mean | h_worst |
|---|---|---|---|
| Vertical line on axis | 2.3 P_unit | 2.08 | 4.95 |
| Line aimed at a corner head | 6.0 P_unit | 1.40 | 2.61 |

- Its cost is up to 1.56× more mean power and occluded-like heat for those motes.
- **Validation of the M17 basis.** m17 uses H14 (14 heads) and an approximate capture. With H10 and exact capture, the random-head, equal-split stacking for a sketch is 4.8–5.1, not 3.3. T7's h_worst factor covers this for random content.

### M4. Modes with the real H10 field: 2.2× T7

*[RT7 `modes`]*: square aperture 2·clip·λd_max/(πw), and pitch set by the direction sines the 1 × 1 × 0.8 m box subtends from each head.

| Heads | d (m) | sin(half field) | Aperture | Pitch at os 1.5 | M at w 51 µm |
|---|---|---|---|---|---|
| Corner, ceiling | 3.15–4.75 | 0.18 × 0.16 | 110 mm | 2.9 µm | 1.31×10⁹ |
| Corner, floor | 3.09–4.67 | 0.18 × 0.16 | 109 mm | 2.8 µm | 1.25×10⁹ |
| Ceiling centre | 1.05–1.98 | 0.43 × 0.43 | 46 mm | 1.2 µm | 1.46×10⁹ |
| Floor centre | 0.85–1.80 | 0.51 × 0.51 | 42 mm | 1.0 µm | 1.67×10⁹ |
| **H10 total** | | | | | **1.34×10¹⁰** (T7: 6.1×10⁹) |

- Data and hologram compute scale the same way: ~270 Tb/s and 3.3×10¹⁶ ops/s for the still sketch.
- That is for one-pass superposition. Weighted GS, needed for few-% spot amplitudes, costs ×10–30 more [ESTIMATE].

### M5. Loop margins: latency, noise, untested 10 kHz floors, and the PLM

*[RT7 `loop`, 200 motes × 60 s each.]*

| Case | Lost / mote-s | Rate (95 % CI) |
|---|---|---|
| MEMS 5 kHz w 50 still, m18c conventions, no lateral force | 0 / 11 940 | < 2.5×10⁻⁴ |
| — with lateral force | 0 / 11 940 | < 2.5×10⁻⁴ |
| — exposure-averaged sensing, 2 frames after exposure (≈ +½ frame) | 14 / 11 501 | **1.2×10⁻³** [0.67, 2.0]×10⁻³ |
| — sensor noise 8 µm (instead of 4) | **196/200** in 2 987 | 6.6×10⁻² |
| MEMS 10 kHz w 35 still | 3 / 11 831 | 2.5×10⁻⁴ [0.5, 7.4]×10⁻⁴ (marginal) |
| MEMS 10 kHz w 40 home, mean wind | 1 / 11 894 | 8.4×10⁻⁵ [0.02, 4.7]×10⁻⁴ |
| PLM 1 frame w 70 still | 1 / 11 907 | 8.4×10⁻⁵ [0.02, 4.7]×10⁻⁴ |

- **Latency.** m18c's "2 frames" samples the position at the start of the frame two frames back, which equals exposure plus ~1.5 frames of readout, compute, load and settle. At 5 kHz that is 300 µs for 3×10¹² operations and 25 Tb per frame.
- The latency must be designed, and a margin of ½ frame costs ×5 in losses.
- **Noise.** The loss rate is extremely sensitive to sensing noise (4 → 8 µm), so the camera system is on the critical path (M9).
- **10 kHz.** W_LOOP["MEMS 10 kHz"] = 35 / 40 / 40 µm in m18 was never simulated in T7 (no 10 kHz rows in m18c). RT7 supports home at 40 µm and still at 35 µm (marginal).
- **PLM.** TI's PLM imparts 2π only for 405–650 nm [search]. At 1550 nm the stroke gives ~0.84π, i.e. ~0.3 first-order efficiency (T7 now notes ~30 %). The PLM rows describe a device that would need a deeper stroke.
- Statistics: m18b/c's upper bound (n + 2√n)/T is below the exact two-sided 95 % Poisson bound (n = 1: 3.0/T vs 5.6/T; n = 2: 4.8/T vs 7.2/T).

### M6. Spot-following (the coordinator's question)

**Is re-centring on a noisy, delayed measurement realistic?** Yes, in the hologram-actuator architecture.
- The hologram is recomputed every frame anyway.
- Moving a spot by a few µm at 4 m is a ~1 µrad tilt (≈ 0.4 rad of phase across a 0.1 m aperture).
- It cannot be done with I9: the slow hologram cannot follow.

**RT7 results** (mean wind included where the room has one):

| Case | Lost | Rate | Notes |
|---|---|---|---|
| MEMS 5 kHz, w 50, quiet office | 0/200 (11 940 mote-s) | < 2.5×10⁻⁴ /s | fixes C3 at 5 kHz |
| MEMS 5 kHz, w 30, still | 1/200 (11 891 mote-s) | 8.4×10⁻⁵ [0.02, 4.7]×10⁻⁴ /s | 17 motes passed r > w transiently |
| MEMS 5 kHz, w 35, home | 3/200 (11 834 mote-s) | 2.5×10⁻⁴ [0.5, 7.4]×10⁻⁴ /s | marginal |
| MEMS 3 kHz, w 50, quiet office | 81/200 (8 709 mote-s) | **9.3×10⁻³ /s** | m18c follow (no mean): 0/60 |
| MEMS 3 kHz, w 35, still | 51/200 | **4.9×10⁻³ /s** | m18c follow: 4/60 (3.5×10⁻³ /s) |
| MEMS 3 kHz, w 35, quiet office | 200/200 | 1.1 /s | |
| PLM 1 frame, w 50, still | 0/200 (11 940 mote-s) | < 2.5×10⁻⁴ /s | confirms T7 (still air only) |
| PLM 1 frame, w 50, quiet office | 144/200 | 2.7×10⁻² /s | |

T7's quick-run table ("MEMS 3 kHz holds w = 35 and 50 µm, still and quiet office"; "PLM holds w = 50 in the quiet office") does not hold at the 10⁻⁴ /s level or with a mean wind. PLM 1-frame following holds w = 50 µm in still air only. MEMS 5 kHz is the slowest following loop that also holds a mean wind.

**Hidden failure modes.**
1. **The loss criterion ignores the home offset.** In m18c follow mode a mote counts as held while |x − spot| < 1.5w, wherever it is. m18c_follow reports r_max of 1.1–15.7 mm for "held" motes (PLM 1 frame, w 25–35 µm): these are visible image defects. RT7 counts |x| > 1 mm as lost and records |x| > 100 µm.
2. **The spot chases the noise.** The beam offset is noise ⊕ motion over the latency (≈ 4√2 µm ⊕ a few µm), so the force has a multiplicative noise exp(−2ρ²/w²). With follow the gain schedule sees no offset, so it cannot correct this. That is why w ≤ 30 µm fails at 3 kHz and why noise sensitivity is high.
3. **Lateral photophoresis.** In follow mode it becomes a zero-mean random kick along the measurement error (~1 µm per frame at w 25 µm). It is small but not zero.
4. **Outliers.** A dust sparkle or a mis-associated mote moves the spot away and loses the mote within one frame, where a fixed spot would mis-push it for one frame. Gating is needed.
5. **Visible illumination.** The visible spots (w_v ≈ 14 µm) must follow too, so the visible holograms run at the loop rate (C1).
6. **Registration.** Spot positions come from camera coordinates, so camera-to-head registration error is a constant beam offset. Ten heads and the cameras must agree to ≲ 0.1–0.2 w: **5–10 µm over 4–5 m, i.e. 1–2.5 µrad**, held over temperature. This is not budgeted.

**Fix.**
- Centre the spots on a *predicted* position (a Kalman filter fed with the commanded force), not the raw delayed sample.
- Count home offset in the loss rate.
- Add gating, and a registration-calibration loop that uses the motes as fiducials.

### M7. I9: crosstalk on real content, depth, and hidden hardware

**Geometry** *[RT7 `i9`]*.

| Heads | Room depth | Intermediate depth at m = 15 | Lateral magnification over the depth |
|---|---|---|---|
| Corner | **1.60 m** | 7.4 mm | 12–18× |
| Ceiling / floor | 0.93–0.94 m | 4.2–4.3 mm | 10–22× |

- T7 assumed 0.8 m of depth and 3.6 mm. Room-unit pixel sizes and layer conjugates are therefore not uniform.
- **Étendue:** the real per-head étendue is 1.4–1.6×10⁻³ m²·sr, ~2.8× T7's 5×10⁻⁴. That means 120 mm layers at NA 0.15, or NA 0.26 at 73 mm.

**Crosstalk on strokes** (own arcs, δ = 3 mm, w = 50 µm, 1 mm room-unit pixels; a mote "owns" the pixels at its nearest layer that carry ≥ 0.5 % of its beam; crosstalk is the fraction of its beam crossing other motes' pixels at any layer):

| Content / head | Layers | Motes served | Median | Mean | > 1 % | > 10 % | Own-pixel conflicts |
|---|---|---|---|---|---|---|---|
| Sketch / corner | 4 | all | 0 % | 9.7 % | 24 % | 13 % | **23 %** |
| Sketch / corner | 4 | ⅓ | 0 % | 3.6 % | 11 % | 5 % | 12 % |
| Sketch / floor | 4 | all | 0 % | 10.7 % | 26 % | 16 % | **28 %** |
| Sketch / corner | 8 | all | 0 % | 6.7 % | 11 % | 8 % | 8.5 % |
| Film / corner | 4 | all | 6 % | 28 % | 60 % | 44 % | **49 %** |
| Film / corner | 8 | ⅓ | 0 % | 6.7 % | 23 % | 11 % | 11 % |

- T7's 0.1–0.5 % is close to the median, but stroke neighbours (3 mm apart, own-layer footprints up to ~1 mm) make the tail heavy.
- A mote whose own pixel is shared cannot be actuated independently.

**Hidden requirements.**
- **Addressing.** A transmissive active matrix at 5–10 kHz: ~1 100 rows means ≤ 90–180 ns per row, against ~10 µs in TFT displays [memory], unless it is split into ~100 segments.
- **Electrodes.** Transparent electrodes at 1550 nm: display ITO is metallic there (ε ≈ −2 + 0.75i), so low-carrier ITO or another conductor is needed.
- **Transmission.** Stack transmission of ~0.5–0.75 for 4 layers [ESTIMATE]. That raises IR power ×1.3–2 and heats the stack.
- **Phase crosstalk.** A layer that changes polarisation also changes the phase of patches of other beams, which shifts their foci.
- **π-cells.** Response ∝ d², so at 1550 nm they are ms-class. DHF-FLC at 100–235 µs is plausible [search].
- **No following.** I9 keeps the fixed-spot floor: w ≥ 50 µm at 5 kHz in still air, and failure with a mean wind (C3).

**Fix.**
- Use 8 layers with ≥ 0.25 mm pixels, and assign heads per mote to avoid conflicts (with 10 heads this is usually possible).
- Count the active-matrix addressing, electrode absorption and phase crosstalk.
- Treat I9 as still-air, fixed-spot only.

### M8. Stray light in the forward geometry

T7's 0.0008 cd/m² uses a receiver leak of 10⁻². As C1 shows, the direct beams after the motes head towards the viewers. The result:
- 0.079 cd/m² on room surfaces (sketch, albedo 0.8), and ~0.6 cd/m² for film density, against the 0.01 cd/m² criterion;
- ~1 cd/m² beam dots on the viewers.

**Fix.** Either accept a lit-room criterion of ~0.1 cd/m², or move the beam terminations off people. The forward geometry forbids receivers in the forward direction.

### M9. Sensing: the photon budget depends on where the camera sits

*[RT7 `vis`; 25 mm lens at 1.5 m, 0.2 ms frames, QE 0.7 visible / 0.8 InGaAs; σ = √((σ_psf² + p²/12)/N).]*

| Signal | Photoelectrons per frame | σ (100 / 500 µm object pixels) |
|---|---|---|
| Visible spot, camera at 90° (q 3.7×10⁻³) | **2.3** | 68 / 190 µm |
| Visible spot, camera in the 15° lobe (q 5.0) | 3 200 | 1.9 / 5.1 µm |
| IR trap beam, 20° forward (q 2.8; mote proxy m = 1.05 + 0.12i, Q_abs 0.80) | 66 000 | 0.4 / 1.1 µm |
| IR trap beam, 40° | 11 000 | 1.0 / 2.7 µm |
| IR trap beam, 60° | 79 | 12 / 32 µm |

- T7's 4 500 photons hold only for a camera in a forward lobe. Visible cameras near the viewers are excluded (no glasses).
- Workable sensing therefore means InGaAs cameras within ~40° of an active trap beam's forward direction (e.g. beside the opposite head), multi-ROI at 5–10 kHz, with ≤ 1 frame of latency. That is plausible but not built.
- M5 shows that 8 µm of noise loses 98 % of motes.

### M10. Hologram amplitude accuracy and compute

- The loop needs each spot's amplitude every frame with errors of a few percent; amplitude error acts as actuator noise.
- T7's compute (6×10⁹ px × ~600 spots × 5 kHz) is one-pass superposition. Phase-only superposition holograms have tens of percent spot-to-spot error and lower efficiency [ESTIMATE; RT6 M2 found 24–39 % within flat-tops].
- Weighted GS (×10–30 iterations) puts the IR compute at ~10¹⁷–10¹⁸ ops/s with the H10 field (M4).

**Fix.** Simulate the loop with a per-frame amplitude-error model taken from an actual CGH algorithm at 600 spots.

---

## Minor

1. **Envelope efficiency.** T7 §1.1 says 0.65; the code uses 0.787 (my value 0.789, harmonic mean 0.769 for uniform spots). Edit the text.
2. **Poisson bounds.** The (n + 2√n)/T upper bound in m18b/c is too low for small n. Use the exact χ² bound (see M5).
3. **Hot-face formula.** m18's formula applies the l = 1 factor to the full h·ΔT. The dipole follows the *net* force, so it is conservative: occluded 368–555 K against RT7 355–511 K.
4. **M17's capture.** Its approximation is ~14 % low at the worst point and it uses H14. Use the exact non-central χ² capture with H10 (M3).
5. **Lateral photophoretic force.** F_lat/F_ax = (3/8)·a·∂ln I/∂r = 1.5·a·ρ/w², pointing away from the axis (physics.py has the law; a Gaussian expels positive-photophoretic absorbers, as with Shvedov-type hollow traps [search]). It is omitted in m18b/c and negligible at w 50 µm (r_p99.9 6.9 → 7.3 µm).
6. **The 1.5 µm mote.** It sits near its own null at 15° (first minimum 13.4°; ±10 % gives q 0.47–4.5). T7's q(15°) = 2.0 is a coincidence of the window.
7. **Zero order.** 1–5 % of each head's light (12–60 mW) is not discussed in T7. It must be defocused (a lens phase), giving < 0.2 mW per pupil at the window, or blocked in a Fourier plane.
8. **Gust surges.** The ≤ 0.35 s dose check passes with ≥ 3× margin. Condition 1 (binoculars; [memory] 7 mm at 2 m for 1400–4000 nm) does not bind for beams diverging at 0.01 rad.
9. **Window inconsistency.** T7 §1.2 says "within 10–25°" in its costs and "10–20°" in its use. Both exceed the lobe of a 1 µm mote (C1).
10. **The long "home" run.** m18c's 150 s home run is a zero-mean draft; label it as such (C3).
11. **m18 office row.** It uses r_p99.9 = 30 µm [ESTIMATE] and W_LOOP 90–120 µm, both unsimulated. The rows fail anyway.
12. **§5.7 touch.** The numbers check (potential flow V(R/r)³; plume 0.10–0.48 m/s). Add that a still warm hand is a *mean* flow, which defeats fixed-spot loops (C3) and exceeds the Class 1 budget locally ×2–8. The "thermally neutral glove" must also not let the arm and body plumes reach the image.

---

## What T8 (POV-X) inherits from T7, and what this review changes there (for red team 8)

- T8 uses **T7's forward illumination at 10° (q = 24.5)**.
  - C1 applies unchanged: emitters behind the image for every viewer, the visible holograms or steering channels, emitter glow, and audience stray light.
  - The 1 µm lobe at 10° is stable to ±15 % over a ±10 % spread, so 10° is the right choice.
- T8's E/L = h·I_unit·πw²/2 inherits **I_unit**. With a realistic skin (C2), E/L doubles, which halves the crossing-rate budget.
- T8's **follow-mode tracking** inherits M6's failure modes (registration, outliers, noise chasing) and C3's mean-wind check.
- **Time-mean h** (opus, T8): for *static* voxels it must be paired with the 10 s window factor (M2). For POV the per-pupil load is set by the crossing rate, so the draft window matters less, but T8's "(1 + u/v)" term should still use windowed u.
- **"Fast animation excluded":** RT7 agrees with opus that the statement is true only for holographic static voxels (via B8 × B9, M1). Whether POV escapes it is RT8's question.

---

## Corrected design table (T7 §4)

**Assumptions** *[RT7 `table`, `loop`]*:
- H10 with the real field (M4);
- random stroke content, with stacking-aware allocation for aligned lines (M3);
- Class 1 with the LP-weighted time-mean stacking × the 10 s window factor (M2);
- η = 0.75 × 0.77 × 0.85;
- loss target 10⁻⁴ /s per mote (an RT7 simulation passes if its 95 % upper bound is ≲ 5×10⁻⁴ /s with ≤ 1 loss);
- mean wind included;
- 4 µm sensing at m18c's latency convention.

| Content / room | T7 claim | Class 1 waist: ideal mote (J₁ 0.49) / thin-skin mote (J₁ 0.24) | A loop that holds it (RT7) | IR power | IR modes (H10) | Visible modes | Verdict |
|---|---|---|---|---|---|---|---|
| Sketch, still | 51 µm, MEMS 5 kHz, 12.5 W, 6.1×10⁹ | **43 / 30 µm** | 43: MEMS 5 kHz follow (holds 30 µm), or MEMS 10 kHz fixed (35 µm: 2.5×10⁻⁴ /s; 40 µm in a home: 8.4×10⁻⁵ /s). 30: MEMS 5 kHz follow (1/200, ≤ 4.7×10⁻⁴ /s). MEMS 5 kHz fixed needs 50 µm, so it **fails** | 9 W | 1.9×10¹⁰ / 3.8×10¹⁰ | 0.9×10¹¹–1.7×10¹² | **Consistent with spot-following at ≥ 5 kHz** (marginal statistics) |
| Sketch, home (U 0.05) | 43 µm, MEMS 10 kHz, 13.7 W | **37 / 26 µm** | 40 µm MEMS 10 kHz fixed holds (8.4×10⁻⁵ /s) but is > 37. 35 µm MEMS 5 kHz follow: 3/200, 2.5×10⁻⁴ /s (marginal) | 10 W | 2.6×10¹⁰ / 5.2×10¹⁰ | same | **Marginal** (ideal mote); **unverified/fails** (realistic: 26 µm untested) |
| Sketch, quiet office (U 0.1) | fails | **32 / 22 µm** | 40 µm MEMS 10 kHz fixed loses 9.5×10⁻³ /s; 50 µm MEMS 5 kHz follow 0/200 (too large) | 10 W | 3.5×10¹⁰ / 7×10¹⁰ | same | **Fails** (Class 1 waist < every verified loop floor) |
| Film density, still | 40 µm, MEMS 10 kHz, 48 W | **34 / 24 µm** | 34: MEMS 5 kHz follow (holds 30 µm in still air); MEMS 10 kHz fixed at 35 µm is marginal (2.5×10⁻⁴ /s). 24 µm untested | 34 W | 3.0×10¹⁰ / 6.0×10¹⁰ | same | **Consistent with 5 kHz following** (ideal mote); **unverified** (realistic) |
| Film density, home / quiet office | fails | 29 / 21, 25 / 18 µm | — | 39 W | 4–11×10¹⁰ | same | **Fails** |

- **IR power at the Class 1 waist does not depend on the mote**, because w² ∝ 1/I_unit. It is ~9–10 W (sketch) and 34–39 W (film). The mote changes the waist, and so the loop floor and the mode count.
- T7's rows with A = 0.5 match the thin-skin column, because J₁ is the same (0.243 against 0.24).

---

## What to fix first (value of information)

1. **The mote's J₁ = A·(J₁/A) on a real 1 µm skinned sphere** (bench B2). This decides whether the waist is 43 or 30 µm, and therefore the loop and the modes. Until it is measured, use J₁ ≈ 0.24.
2. **Re-run m18b/m18c with the mean wind** and the (U + 5.4σ) authority. Adopt spot-following on a *predicted* position. Count home offset as loss. Add 10 kHz rows. Run ≥ 3×10⁴ mote-s at the candidate points (RT7 has ~1.2×10⁴ each).
3. **Budget the visible engine.** Viewing-zone assumptions, the emitter count, visible modes (10¹¹–10¹²), the eye-direction dark regions and the audience-side stray light. This is now the largest hardware number.
4. **Restate B9** in modes, with the 10 s window and time-mean h. Add stacking-aware allocation and test it on wireframes that contain head-aligned lines.
5. **Sensing.** An InGaAs multi-ROI camera at ≥ 5 kHz with ≤ 1 frame of latency and ≤ 4 µm noise, placed in a forward lobe of the trap beams. Plus a registration loop to 1–2.5 µrad.
6. **I9.** Only for still-air, fixed-spot, static content. Re-cost it with 8 layers, finer pixels, conflict-avoiding head assignment, and a 5–10 kHz transmissive active matrix.

## Sources (web, this review)

- IEC 60825-1 / 1550 nm corneal limits (MPE 0.1 W/cm²; limiting aperture 1.5·t^0.375 mm for 0.35–10 s; AEL = MPE × aperture area):
  - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11355963/ (search snippet; the page itself was blocked by the proxy)
  - https://www.osti.gov/servlets/purl/1143358 (search snippet; blocked)
- IEC 60825-1:2014 measurement conditions (Condition 1 at 2000 mm and Condition 3 at 100 mm; Condition 2 removed): https://www.lasermet.com/laser-safety-services/product-testing-laser-led/ (snippet)
- TI PLM (DLP6750, 1358 × 800, 4-bit piston, 1.44 kHz limited by its electronics, 2π only for 405–650 nm):
  - https://arxiv.org/pdf/2409.01289
  - https://github.com/structuredlightlab/plmctrl
- Positive photophoresis pushes absorbing particles out of bright regions; hollow and vortex traps (Shvedov et al.):
  - https://opg.optica.org/abstract.cfm?URI=Photonics-2016-Tu5G.2
  - https://www.nature.com/articles/srep29001
- DHF-FLC response ~100 µs (vertically aligned DHF) and ~235 µs (analog DHF LCoS):
  - https://arxiv.org/pdf/1401.2543
  - https://opg.optica.org/ol/abstract.cfm?uri=ol-20-5-513

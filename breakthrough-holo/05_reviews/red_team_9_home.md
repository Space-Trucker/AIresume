# Red team 9: home routes, the tetralemma and FLOW-R2 crossed-probe gating (T9, m22, m23)

**Scope.** Reviewed on 2026-10-05:
- `09_unlock/T9_home_routes.md`;
- `m22_needles.py` and `m23_flowr2.py`, with `results/m22_run.log` and `results/m23_run.log`;
- `idea_round_4_opus.md` (FLOW-R) and `IDEA_ROUND_4_HOME_BRIEF.md`;
- `FINAL_VERDICT.md` (v5), RT7 and RT8 for style and inherited results;
- the coordinator's mid-review question on stroke fill (§ "The coordinator's fill question").

**Method.** All numbers marked *[RT9]* come from `09_unlock/rt9_check.py`. It imports `m23_flowr2` read-only and reuses its model, geometry and ghost Monte Carlo. Blocks:

| Block | What it checks |
|---|---|
| 1 | aperture, depth of field and photons |
| 2 | look-ahead wander |
| 3 | visible repetitive-pulse rules |
| 5 | particles |
| 6 | coverage |
| 7 | m22 spot-checks |
| 8 | ghosts against eps |
| 9 | probe-gated event rate: exact horizontal projected area of the pencil ∩ camera-tube voxel |
| 10 | fill against stroke angle, 2D Monte Carlo with and without FLOW-R2 gating |
| 11 | beam aggregation at the visible and probe heads (exact Gaussian capture through a 7 mm or 1 mm disc, non-central χ²) |
| 12 | stacking at a pupil inside the column |
| 13 | column buoyancy and width |
| 15 (`--aim`) | flash hit fraction |
| `--addenda` | per-camera depth range, fill at the eye blur |

Outputs are `results/rt9_checks.json`, `rt9_run.log`, `rt9_addenda.json` and `rt9_aim.json`.

**Bug found in my own code during the review.** My first gated-fill run painted each mote's whole lit span, which bridged the gaps between per-sample flashes. It is fixed: each contiguous lit run is now painted separately, and the numbers below are from the fixed run. My first visible-safety pass also wrongly held the beam energy per flash fixed across w_v. The scattered energy is fixed, and the beam energy scales as w_v²: 5.15 µJ at 140 µm, 1.70 µJ at 80 µm, as in m23's rows. This too is fixed below.

**Web searches:** 5 of 12 (sources at the end). Facts from memory are marked **[memory]**.

**Tags:** [MEASURED] documented fact with source; [DERIVED] formula plus numbers here; [ESTIMATE] order-of-magnitude judgement; [SPECULATIVE] untested.

**Severity counts:** 3 critical, 6 major, 10 minor.

---

## Verdict table

| T9 / m22 / m23 claim | Verdict | One-line reason |
|---|---|---|
| §0, §2.8 Full vision not reachable at home | **CONFIRMED, strengthened** | Tetralemma arithmetic exact. FLOW-R2, the nearest escape, has three new decisive problems (C1–C3) |
| §2.8 w_max, modes and loop numbers (h·s = 2.14 × 1.1) | **CONFIRMED** | 37.6 / 21.7 / 11.9 µm; 2.58×10⁷ / 7.73×10⁷ / 2.58×10⁸ modes; 2.66 / 13.8 / 84 kHz all reproduce |
| §2.8 "no route relaxes none of them"; escapes table complete | **PARTLY** | Correct, but three escapes are missing (vitrine, aerial-imaging window, selection instead of placement), and FLOW-R2 relaxes three rules, not two (m9) |
| §2.2 Laplace low-pass | **CONFIRMED** | exp(−2π·0.05/0.006) = 1.8×10⁻²³ |
| §2.3 One-way photo-charge and ratchet | **CONFIRMED** (model-dependent) | Direction robust; lifetimes depend on the OU load model |
| §2.4 Thermal kick theorem | **CONFIRMED** | Closed form 10.1 vs T_rev/τ 10.2 (40 µm); selftest 9.755 vs 9.761 |
| §2.5 Self-addressing cavity pump ≥ 5.5 kW | **CONFIRMED** (as a floor) | Étendue and slab assumptions are fair; even ×100 slack leaves it dead |
| §2.6 Coulomb crystals too soft | **CONFIRMED** | — |
| §3.2 E-AIR-SV hand field 9–31 mm/s at 10 cm | **CONFIRMED, likely an underestimate** | h_off 0.3 m is generous, and the whole grounded body is ignored |
| §3.3 Mannitol is the Aridol agent; use lactose or trehalose | **CONFIRMED / PARTLY** | Aridol is mannitol [MEASURED]. Lactose carries trace milk protein and is contraindicated in milk-protein allergy, so trehalose should be the default (M4) |
| §3.4 "A mote seen by all cameras at once is at P_k⁺" | **CONFIRMED geometrically** | True within the voxel, but see C1 (rate) and M1 (voxel size) |
| §3.4 Ghosts ≤ 0.6 % (2 cams), ≤ 0.05 % (3 cams) | **PARTLY** | Arithmetic reproduced exactly. It holds only if eps ≤ 1 mm, which the 35 mm aperture cannot give (M1). At eps 2 mm: 5.0 % / 1.2 % |
| §3.4 Rain sized for 20 crossings/s per sample; dropouts 13.5 % per 0.1 s | **REFUTED for FLOW-R2** (C1) | The probe voxel admits 3.4–4.8 /s (17–24 %), so 62–71 % of samples are dark per 0.1 s |
| §3.4 13 k e⁻ per crossing | **REFUTED as consistent with the gating** (M1) | 35 mm aperture: circle of confusion ≈ 3 mm across the content. At the 5.7–12 mm needed: 230–1 070 e⁻ |
| §3.4 23 ms look-ahead; "wander 0.6 mm at Tu 10 %" | **REFUTED as specified** (C3) | 0.6 mm wander vs a 40–70 µm aim radius: 0.2–0.7 % of flashes land. Fixable in the core, not in hand wakes |
| §3.4 Visible: half the single-pulse AEL; Class 1 per beam | **CONFIRMED per beam / REFUTED per product** (C2) | Rule 1 0.47 (w140) and 0.16 (w80); rule 2 0.26 / 0.087. Ed. 3 C5 = 1 for point sources. But a head aggregates ~1 000 lines: 11.5–38× the CW AEL at 10 cm |
| §3.4 Probe eye case "still needs checking" | **REFUTED as safe** (C2) | 0.2 W at 850 nm leaves through one lens: 133× the Class 1 AEL at 10 cm, 35× at 50 cm; skin at the exit 24× (EN 50689) |
| §3.4 Vertical strokes 33 % coverage, "the main rendering weakness" | **PARTLY** | Formula right for continuous lighting. Horizontal strokes have the same fill (coordinator confirmed). Vertical strokes differ in gap scale (67 % of length in gaps > 10 mm vs 7 %). FLOW-R2's per-sample flashes cut both to 0.11–0.15 / 0.05–0.09 (M2) |
| §3.4 Room particles 50 µg/m³ at 99.9 % | **CONFIRMED arithmetic; conclusion PARTLY** | 50 µg/m³ is already above the WHO 45 µg/m³ PM10 24 h figure, so 99.97 % is needed; 96 % of escapes land on surfaces (M4) |
| §3.4 Haze 11 % vs a dark wall at 10 lux | **CONFIRMED** | 0.018 vs 0.159 cd/m²; 1.1 % against a ρ 0.5 wall. With C1's fix (×4–6 rain) it is 48–67 %, a visible haze |
| §3.4 Column (implicit: it reaches the image at 0.25 m/s) | **MISSING physics** (M5) | ±0.3 K column–room difference gives 0.19–0.30 m/s at the image; +1 K stalls it; rooms stratify 1–2 K/m |
| §4 Cost $30–60k; visible engine $10–30k, 40–60 galvo channels | **REFUTED low** (M6) | 79 mean, ~107 peak simultaneous spots (173 with vertical-fill flashes), each focus-banded and aimed to 28–48 µrad: ~$50–120k |
| §4 FLOW-R2 "nearest full-vision build" | **NOT SUPPORTED as specified** | C1–C3 are each decisive as written. A redesign path exists (see "What would change the verdict") but is not commodity and not shown |

---

## Summary

**What holds.**
- The m22 bounds (Laplace, thermal kick, cavity pump, Coulomb crystal) and the tetralemma arithmetic are correct.
- The mannitol correction is right.
- The crossed-probe *geometry* is sound: at small eps a 2–3 camera coincidence does localise a mote to P_k⁺, and m23's ghost arithmetic reproduces exactly.
- Per beam and per flash, the visible light is within the Class 1 single-pulse and mean-power rules. Under IEC 60825-1 Ed. 3, C5 = 1 for sources < 5 mrad, so the repetitive-pulse rule 3 does not bind.

**What fails.** Each of the following is decisive as specified.
1. **C1. The probe voxel starves the rain.** m23 sizes the rain for 20 crossings/s through each sample's 3 mm × 1 mm window. A mote is lit only if it passes through the pencil ∩ camera-tube voxel, whose horizontal projected area is 0.51–0.73 mm² at m23's own w_p 0.35 mm and eps 0.5–1 mm. That admits **3.4–4.8 /s per sample (17–24 %)**, so **62–71 % of samples are dark in any 0.1 s** (T9: 13.5 %). Fixing it means one of two things:
   - a voxel ~4× larger, which raises ghosts and blurs localisation;
   - a ×4–6 rain: 234–331 mg/m³, 140–197 g/h, 48–67 % haze contrast against a dark wall. That is no longer sub-visible.
2. **C2. The heads are Class 1 per beam, not per product.** Seen from a ceiling head, the tall armor is foreshortened, so its ~1 000 lines leave one exit in a tight bundle. At the 100 mm evaluation distance one 7 mm pupil collects:
   - **visible:** 396–436 lines, 4.5–15 mW mean, **11.5–38× the 0.39 mW CW AEL** (w80 to w140, events split over 3 heads);
   - **probe:** 518 pencils, **104 mW at 850 nm, 133× the 0.78 mW AEL**; still 35× at 50 cm. At the probe exit through 1 mm (EN 50689 skin) the load is 74 mW against 3.1 mW.
   - **a face inside the column:** 0.69–2.1 mW mean (1.8–5.4×).

   EN 50689 makes Class 1 mandatory for a child-appealing product. A commodity DLP projector and galvo heads cannot meet it as laid out.
3. **C3. The 23 ms open-loop shot misses.** Lateral wander is σ = Tu·U·t, i.e. 0.58 mm at m23's Tu 10 %, against an aim radius of w_v/2 = 40–70 µm. **0.24–0.73 % of flashes land on the mote** (21–52 % even at Tu 1 %). It is fixable:
   - **the fix:** a velocity estimate during the ~10 ms pencil dwell plus Δ ≤ 1.5 mm brings σ to ~17 µm, so 93–99.97 % of flashes land in the column core;
   - **where the fix fails:** in a hand's wake (15–39 %), i.e. exactly where the user touches.

**Coordinator's fill claim: CONFIRMED with qualifications.**
- The fill ≈ n·U·d_s·t_eye·(d_s|cos θ| + b|sin θ|) is the coordinator's formula when the dot width b equals d_s. Vertical and horizontal strokes both fill ≈ 0.33 per 50 ms; the Monte Carlo gives 0.31 / 0.35, and 0.41–0.42 at 30–60°.
- Vertical strokes differ in gap scale: **67 % of their length sits in gaps > 10 mm, against 7 % for horizontal strokes**. So the perceptual weakness is real, but it is texture, not fill.
- d_s ≈ 1.73 mm gives fill 1 at the same mass, at ×3–4 simultaneous spots, ×1.7–2 visible power and 1.7–2 mm lines.
- In FLOW-R2 as gated, per-sample 1 mm flashes and the voxel rate cut the fill to **0.11–0.15 (vertical) and 0.05–0.09 (horizontal)**.

**Net.**
- T9's top-level verdict ("full vision not solved") stands, and is stronger.
- Its framing of FLOW-R2 as "the nearest candidate" with "two bent rules" and a $30–60k cost does not survive as specified.
- FLOW-R2 needs:
  - a rate-matched probe (C1);
  - a non-commodity, distributed head architecture for Class 1 (C2);
  - velocity-predicting aim with ≤ 5–6 ms latency (C3);
  - thermal column control (M5);
  - trehalose instead of lactose;
  - 99.97 % capture.

---

## Independent recomputation of key numbers

| Quantity | T9 / m23 | RT9 | Note |
|---|---|---|---|
| v_s (a 7 µm, ρ 1520) | 9.0 mm/s | 8.97 mm/s | — |
| n, mass, flux, g/h | 2.57×10⁷, 56 mg/m³, —, 33.5 g/h | 2.57×10⁷, 56.2, 4.26×10⁶ /s, 33.5 | — |
| Optical depth; haze vs dark wall | 0.63 %; 11.4 % | 0.63 %; 11.4 % (1.1 % vs ρ 0.5 wall) | — |
| Room at 99.9 / 99.97 / 99 % | 50 / — / 500 µg/m³ | 50.0 / 15.0 / 500 | k_loss is 96 % deposition |
| p_drop per 0.1 s (design rate) | 0.135 | 0.135 | e^(−N_s f_r 0.1) |
| **p_drop per 0.1 s (probe-gated rate)** | — | **0.62–0.71** | rate 3.4–4.8 /s (C1) |
| Vertical coverage per 50 ms | 0.33 | 0.33 (formula), 0.31 (MC, continuous) | **0.11–0.15 gated** (M2) |
| Photo-electrons per crossing | 13 236 (35 mm, 1.6 m) | 13 236 reproduced; **230–1 070** at the aperture the gating needs, at the true 2.0 m range | M1 |
| Probe dwell | 2.7 ms (2w_p/U) | **10.1 ms**: the pencil runs 15.5° from vertical | m3 |
| Look-ahead; wander | 23.2 ms; 0.58 mm | 23.2 ms; 0.58 mm | **hit 0.2–0.7 %** (C3) |
| Ghosts, 2 / 3 cams, eps 1 mm, 2 ms | 0.6 % / 0.05 % | 0.64 % / 0.050 % | exact |
| Ghosts at eps 2 mm | — | 5.0 % / 1.2 % | M1 |
| Single-pulse ratio, w140, 3.9 ms | 0.48 | 0.47 | rule 1 |
| Simultaneous spots | 79 | 79 mean, ~107 at +3σ | — |
| Visible mean power, total | — | 106 mW (w140), 35 mW (w80) | aggregated at heads (C2) |
| Tetralemma w_max at 1 / 3 / 10 cm/s | 37.6 / 21.7 / 11.9 µm | same | h·s 2.354 |

---

## Critical

### C1. The probe voxel admits 17–24 % of the crossings the rain is sized for [DERIVED, RT9 §9]

**The sizing.** m23 sets n = N_s·f_r/(U_f·δ·d_s), so that N_s·f_r = 20 motes/s cross each sample's δ × d_s = 3 mm × 1 mm window. Brightness, dropouts and coverage all use that rate.

**The gating.** A mote is lit only if it is detected. Detection needs it inside:
- the probe pencil B_k (radius R_p);
- camera A's pixel tube;
- camera A′'s pixel tube (half-width eps).

The detected rate is n·U_f·A_proj, where A_proj is the voxel's horizontal projected area. m23 computes this rate itself (`r_vox` 4.5–9 /s) but uses it only for ghosts, never against the 20 /s budget.

**Exact projected area** on m23's geometry (probe at (0.35, 0, 2.45), cameras A and A′, 150 armor samples), from the z-intervals of each vertical line inside the three tubes:

| R_p | eps | A_proj (median) | Rate per sample | Fraction of design | Dark per 0.1 s |
|---|---|---|---|---|---|
| 0.35 mm | 0.5 mm | 0.51 mm² | 3.4 /s | 17 % | 71 % |
| 0.35 mm | 1.0 mm | 0.73 mm² | 4.8 /s | 24 % | 62 % |
| 0.35 mm | 2.0 mm | 1.13 mm² | 7.5 /s | 38 % | 47 % |
| 0.525 mm | 1.0 mm | 1.32 mm² | 8.8 /s | 44 % | 42 % |
| 0.525 mm | 2.0 mm | 1.94 mm² | 12.9 /s | 65 % | 27 % |

Line luminance falls by the same 17–24 % unless the flashes get brighter. At w140 they are already at 0.47 of the single-pulse AEL, so ×4–6 more energy fails rule 1.

**The two fixes, and what each costs:**
1. **Grow the voxel to ≥ 3 mm²** (a sheet pencil 3 mm along the stroke and 1 mm thick, or eps ≳ 1.5–2 mm):
   - ghosts reach 5 % (2 cams) or 1.2 % (3 cams) at eps 2 mm (RT9 §8);
   - P_k⁺ localisation becomes ±1.5 mm, so aiming relies wholly on camera centroiding (C3);
   - ~3× the pencils or a structured sheet, with more probe power (C2).
2. **Make the rain ×4.2–5.9 denser:** 234–331 mg/m³ in the column, 140–197 g/h, optical depth 2.6–3.7 %, **48–67 % contrast against a dark wall**. That is a visible haze column and breaks the "sub-visible" ruling T9 asks the owner for.

Option 1 is the only one compatible with "no fog". It is not modelled or shown.

### C2. Class 1 holds per beam, not per head: the visible and probe heads aggregate ~1 000 lines [DERIVED, RT9 §11–12]

**The geometry.**
- A ceiling head 30° off vertical sees the 0.57 m-tall, 0.23 m-wide armor foreshortened into ~0.12 × 0.19 rad.
- Each sample's beam is still 1.7–3.0 mm in radius at the head (visible w140 / w80) or 1.06 mm (probe).
- So a 7 mm pupil near any head collects hundreds of lines, with exact Gaussian capture.
- Per-line mean power, visible: E_flash·N_s·f_r/3, i.e. 34 µW (w140) or 11 µW (w80) with events split over 3 heads.

| Exposure point | Visible w140 (split / one head per sample) | Visible w80 (split / one head) | Probe 850 nm (0.2 mW per pencil, CW) |
|---|---|---|---|
| 7 mm pupil at the exit | 35 / 106 mW → **90 / 271×** | 10.9 / 32.6 mW → 28 / 84× | 205 mW → **264×** the 0.78 mW AEL |
| 7 mm pupil at 10 cm (condition 3) | 15.0 / 44.9 mW → **38 / 115×** | 4.5 / 13.5 mW → **11.5 / 35×** | 104 mW → **133×** |
| at 20 cm | 8.5 mW → 22× | 2.5 mW → 6.5× | 60 mW → 77× |
| at 50 cm | 3.5 mW → 9× | 1.1 mW → 2.7× | 28 mW → 35× |
| Skin at the exit, 1 mm, 10 s (EN 50689) | 5.5 mW vs 1.57 mW → 3.5× | 0.63 mW → OK | 74 mW vs 3.1 mW → **24×** |
| Pupil inside the column, facing the heads (worst of 3 600 points) | 2.1 mW → 5.4× | 0.69 mW → 1.8× | — |

**Readings.**
- **Rule 2 (mean power), not rule 1 or C5, is what fails.** Per flash, rule 1 is 0.47 (w140) or 0.16 (w80). Rule 2 for one sample's beam is 0.26 / 0.087. The excess comes only from many lines sharing one pupil. This is the visible analogue of RT8 C1 (strokes aimed at a head): the armor's near-vertical strokes collapse into narrow fans seen from the ceiling.
- **The probe is the worse problem.** 850 nm is invisible, gives no aversion response, and carries 0.2 W through one projection lens. T9 left this open ("the eye case still needs checking"). It fails by two orders of magnitude.
- **Standards reading** [MEASURED for EN 50689; ESTIMATE for the access argument]:
  - EN 50689 requires child-appealing consumer laser products to be Class 1, with skin assessed through 1 mm over 10 s at the closest point of human access.
  - IEC classification does not credit mounting height. A ceiling unit is accessible during installation and cleaning, and by a climbing child.
- **What a fix needs.** Lines must be spread before the first accessible plane:
  - visible: ≤ ~11 (w140) or ~35 (w80) lines per 7 mm;
  - probe: ≤ ~4 pencils.

  That means launching from many points over a large aperture (tens of cm), or recessing the emitter behind a window by ≳ 1–5 m-equivalent [ESTIMATE]. This is no longer "a commodity DLP projector stopped down to pencils" or ILDA galvo heads, and it is not discreet.
- **The face in the column (1.8–5.4×)** needs active blanking from face detection, a certified safety function. That is not passive Class 1.

### C3. The 23 ms open-loop shot lands on the mote for 0.2–0.7 % of flashes at m23's own Tu [DERIVED, RT9 §2, §15]

**The miss as specified.**
- σ_lat = Tu·U·t_lead is right: the motion is ballistic, because T_L ~ L/u′ ≈ 1–2 s ≫ 23 ms.
- At Tu 10 % (m23) that is 0.58 mm. The aim needs the mote within w_v/2 (≥ 61 % of peak), i.e. 40–70 µm.
- P(hit) = 1 − exp(−R²/2σ²) = **0.24 % (w80) / 0.73 % (w140)**, and **21 % / 52 % at Tu 1 %**.
- Enlarging the spot to catch the wander costs ×4.6 power at 300 µm and ×18 at 600 µm (eff ∝ 1/w²). That breaks Class 1 per beam.

**The fix exists, but it is not what T9 says.**
1. Shorten the look-ahead to Δ ≤ 1.5 mm (5.8 ms).
2. Estimate each mote's velocity from multi-frame centroids during its ~10 ms dwell in the 15°-tilted pencil (m3).

The residual is then the Lagrangian velocity change, σ ≈ √(C₀ε t)·t/√3 (C₀ ≈ 6 [memory]), plus centroid noise:

| Region | ε | σ | Hit w80 / w140 |
|---|---|---|---|
| Column core (σ_u 25 mm/s, L 4 cm) | 3.9×10⁻⁴ m²/s³ | 17 µm | **93 % / 99.97 %** |
| Hand wake (u′ 0.1 m/s, L 8 cm) | 1.25×10⁻² m²/s³ | 71 µm | **15 % / 39 %** |

**What the fix demands:**
- end-to-end latency ≤ 5–6 ms (1 ms exposure, ROI readout, compute, scanner settle);
- camera centroids of ~10–20 µm, which needs the photon budget of M1;
- camera-to-head registration of ≤ 30–50 µm over ~1 m, which with aluminium mounts at 23 µm/m/K means closed-loop calibration;
- scanner pointing of 28–48 µrad (40–70 µm at 1.45 m) [ESTIMATE].

Even fixed, content just below a touching hand degrades. That is the "touchable" region of the vision.

---

## Major

### M1. Photons vs depth of field: the 13 k e⁻ budget and the ≤ 1 mm eps cannot both hold [DERIVED, RT9 §1, addenda]

**The problem.**
- m23's photon count uses a **35 mm** camera aperture.
- The ghost gating assumes a pixel line-of-sight half-width eps of 0.5–1 mm.
- Along each camera axis, the armor spans ±0.16–0.17 m at a range of 1.94–2.0 m (m23's own camera positions; not 1.6 m).
- The circle of confusion is c = A·Δz/z, i.e. **2.9–3.1 mm at A = 35 mm**. So eps ≈ 3 mm, where m23's own Monte Carlo gives 2-camera ghosts between 5 % (2 mm) and 47 % (4 mm).

**Holding eps ≤ 0.5 mm / 1 mm needs A = 5.7–6.0 / 11.4–12.1 mm.** Photons scale as A²/z²:
- **228–267 e⁻ (eps 0.5 mm);**
- **913–1 068 e⁻ (eps 1 mm).**

That is 12–58× below T9's 13 k.

**Detection still works, at lower margin.** The pencil's 15° tilt gives a ~10 ms dwell (m3), so the count spreads over ~5–10 frames: 25–100 e⁻ per frame against machine-vision read noise of ~2–7 e⁻ [memory], plus the 850 nm ambient background, which is unassessed. The 3-camera case tolerates a larger eps. The "13 k e⁻, no problem" statement does not hold together with the ghost claim.

**Smaller items:**
- the ghost eps should include the pencil radius (eps_eff ≈ eps + R_p ≈ 0.85–1.35 mm), giving 0.6–1.5 % for 2 cameras;
- the m-fold coincidence formula is a small-rate approximation and is not valid when the ratio is ≳ 0.3 (the eps 4 mm row gives 3 cams > 2 cams).

### M2. Fill and texture: the gated flashes cut T9's 33 % to 11–15 % (vertical) and 5–9 % (horizontal) [DERIVED, RT9 §10]

See "The coordinator's fill question" below for the derivation.

**What FLOW-R2 actually delivers.** It lights a mote only for d_s/U_f (1 mm of fall) after it passes each sample P_k (spaced δ = 3 mm). On a vertical stroke, a falling mote therefore paints 1 mm in every 3 mm, not a continuous streak.

| Case (50 ms) | Continuous lighting, b = d_s / b = 0.44 mm | FLOW-R2 gated, b = d_s / 0.44 mm | Share of length in gaps > 10 mm |
|---|---|---|---|
| Vertical (θ 0°) | 0.31 / 0.30 | **0.15 / 0.11** | 67–72 % |
| Horizontal (θ 90°) | 0.35 / 0.21 | **0.09 / 0.05** (rate-limited by the pencil, C1) | 7–9 % continuous; 72–74 % gated |
| 30–60° | 0.41–0.42 | — | 11–22 % |

Note: b is the along-axis width of a crossing dot; 0.44 mm is a 1-arcmin eye blur at 1.5 m.

**Restoring the continuous value on vertical strokes** needs flashes stretched to δ/U_f = 11.6 ms per sample. The energy is ×3 (15.5 µJ at w140), which is 0.63 of the single-pulse AEL and acceptable. The cost is **173 instead of 79 mean simultaneous spots**.

**Where T9 is too harsh.** In a dim display (1.5–3 cd/m²) the eye integrates closer to 100 ms than 50 ms [memory]. That doubles every fill: 0.67 for continuous lighting.

### M3. Visible repetitive pulses: C5 is not the problem in Edition 3; aggregation is [MEASURED + DERIVED, RT9 §3]

- **IEC 60825-1:2014 (Ed. 3) sets C5 = 1 for apparent sources below 5 mrad** (ISH1:2017; Schulmeister, ILSC 2015). A lit mote or a beam focus seen from ≥ 0.1 m is a point source (≤ 1.4 mrad), so rule 3 does not bind.
- **The rules that do bind** (rule 1: single pulse; rule 2: mean power):

  | Case | Rule 1 | Rule 2 | Verdict |
  |---|---|---|---|
  | w140, 3.9 ms | 0.47 | 0.26 | pass |
  | w80, 3.9 ms | 0.16 | 0.087 | pass |
  | w140, 1 ms | **1.31** | — | fails (as m23 says) |
  | w80, 1 ms | 0.43 | — | pass |
  | w140 at 30 Hz | 0.31 | 0.26 | pass |

- **Under the older Ed. 2 reading** (C5 = N^−0.25), rule 3 would fail w140 by 1.8× (10 s) to 3.2× (100 s). Any notified body that applied it, or any evaluation that judged the apparent source > 5 mrad, would fail m23's room point.
- **Stall.** A stalled 1.33 mW beam reaches the rule-1 dose in t = (7×10⁻⁴/P)⁴ = **77 ms** (w140). At w80, 0.44 mW is 1.13× the CW AEL. The scan-fail cut must act in ≲ 50 ms at w140 [DERIVED].
- **The binding issue is C2.**

### M4. Particles: 99.9 % already misses the WHO figure; lactose is an allergen; escapes coat the room [MEASURED + DERIVED, RT9 §5]

1. **Room level.**
   - At 99.9 % capture the room sits at **50 µg/m³**, above the WHO 24 h PM10 guideline of 45 µg/m³. **99.97 %** gives 15 µg/m³.
   - Caveat in FLOW-R2's favour: a 14 µm, ρ 1520 mote has d_ae ≈ 17 µm, so its PM10 sampling fraction is small (~10–20 % [memory]). Inkjet satellite drops, however, make smaller, respirable motes [ESTIMATE].
   - No open 2.5 m column with people walking nearby has demonstrated 99.97 % capture [ESTIMATE]. Opus estimated 95–99.9 %.
2. **Where the escapes go.** k_loss is 96 % floor and surface deposition (v_s/H = 3.6×10⁻³ /s vs ventilation 1.4×10⁻⁴ /s). At 99.9 %, ~0.26 g of sugar settles on surfaces per 8 h day, hygroscopic and feeding microbes.
3. **In-column air.** 56 mg/m³ is 5.6× the ACGIH 10 mg/m³ inhalable nuisance-dust TLV (an occupational 8 h figure). Faces must stay out of the column, which a touch product cannot guarantee. The same need for face detection appears in C2.
4. **Material.**
   - Mannitol is the Aridol agent (capsules of 5–40 mg in an escalating challenge) [MEASURED]. T9's correction stands.
   - **Lactose is the wrong default.** Inhalation-grade lactose carries trace milk proteins. Lactose dry-powder inhalers are contraindicated in cow's-milk-protein allergy, and reactions are documented [MEASURED].
   - Use **trehalose** (non-dairy) as the default.

### M5. Column buoyancy: a ±0.3 K mismatch changes the image-level speed by ±20 %; +1 K stalls the column [DERIVED, RT9 §13]

- **The physics.** A 0.25 m/s downward column falling H = 1.25 m to the image obeys U² = U₀² − 2g′H with g′ = g·ΔT/T.
- **The numbers:**

  | Column minus room | Speed at the image | Ri |
  |---|---|---|
  | −1 K | 0.38 m/s | 0.67 |
  | −0.3 K | 0.30 m/s | 0.20 |
  | +0.3 K | 0.19 m/s | 0.20 |
  | +1 K | **0 (stalls before the image)** | 0.67 |

- **The room.** Occupied rooms stratify 1–2 K/m [memory], i.e. ~1.9 K over the fall.
- **The consequence.** The push air must be actively held ~0.3–1 K *colder* than the room at image height:
  - a warm column spreads and stalls, which ruins capture;
  - a cold one accelerates and necks.
- This is absent from T9 and m23. It is fixable with a small heat exchanger and two thermistors [ESTIMATE].

### M6. Cost: the visible engine is under-counted ~2–4× [MEASURED prices + ESTIMATE]

- **Spot count.** 79 mean simultaneous spots (Poisson +3σ ≈ 107). With vertical flashes stretched (M2), **173 mean**. Each needs:
  - a fixed-focus depth band (z_R 3.9 cm at w80);
  - 28–48 µrad pointing;
  - µs-accurate gating from ~1 000 ROI streams.
- **Per channel.** Commodity 30 kpps ILDA galvo sets cost **$195–455** [MEASURED]. A 520 nm diode, focusing optics, driver and mount add ~$200–450, so ~$400–900 per channel [ESTIMATE]:
  - 60 channels: **$24–54k**;
  - 170–215 channels: **$70–190k**.
- **Other items:**
  - the NIR DLP probe is $2–5k, not $1k [ESTIMATE];
  - an FPGA-class real-time controller is $2–5k;
  - C2's distributed heads add more.
- **Hobby galvo pointing.** Thermal drift and repeatability are likely tens of µrad [memory/ESTIMATE], which forces camera closed-loop calibration.
- **Realistic room FLOW-R2:** **~$50–120k** before C2's redesign, against T9's $30–60k. Desk scale stays ~$8–20k.

---

## Minor

- **m1. Ghost Monte Carlo.** Correctly coded: the coincidence formula 2·g₁·g₂·r_vox·τ_c is right for independent Poisson streams, and the per-sample products are averaged correctly. The `far` exclusion is right: a mote at P_k⁺ lit by any beam is a true event.
- **m2. The coverage formula** n·d_s²·U·t_eye is right for continuous lighting along a vertical stroke. Dimensions check out, and the Monte Carlo gives 0.31 against 0.33; the difference is Poisson overlap.
- **m3. Probe dwell.** The pencils run 15.5° from vertical (probe at x = 0.35 m in the ceiling unit). The dwell is 2R_p/(U·sin φ) = 10.1 ms, not 2.7 ms. This helps the photon count ×3.7, but it also means each pencil lights motes along its whole length; the ghost model includes that.
- **m4. Camera range.** The cameras sit at a ~2.0 m range in m23's own ghost geometry, but the photon budget uses 1.6 m: ×0.64.
- **m5. Column width.** The armor content is 0.23 m wide and 0.035 m deep. A 0.67 m column (content + 2 × (5 cm guard + 14 cm erosion + 3 cm drift)) suffices, so mass, air and haze fall ×0.70. This is in FLOW-R2's favour.
- **m6. Haze.** 11 % vs a dark (ρ 0.05) wall and 1.1 % vs a ρ 0.5 wall. A dim display wants a dark backdrop, which is exactly where the column shows.
- **m7. m22 E (cavity pump).** The étendue-matching and slab non-overlap assumptions are fair. Bulk modes that share inversion would cross-saturate, which defeats self-addressing. Even at w140 (≈1.8×10⁶ modes) the InGaAsP floor is ~10³ W. It stays dead.
- **m8. m22 G (hand field).** h_off 0.3 m is generous: a hand 1.2 m above a ground plane gives ×4 the monopole. The whole grounded body is omitted. The verdict direction (E-AIR-SV is not touchable) is robust.
- **m9. Tetralemma framing.** Three escapes are missing from §2.8's table:
  - an enclosure (vitrine), which relaxes open air and touch;
  - an aerial-imaging plate, which relaxes no screen / no window and is the only thing that works today;
  - **selection instead of placement** (FLOW-R/R2), which also relaxes line solidity and brightness, not only the medium and hardware.

  FLOW-R2 therefore bends three rules, not two. The loop column uses the mean v; gust peaks are 3–4× higher (m22's own docstring).
- **m10. Probe single pencil and E-AIR-SV.** One 0.2 mW pencil is 0.26 of the 850 nm Class 1 AEL, which is fine. The visible skin dose on a bare hand under one content point is 0.1 mW mean (0.07 of the EN 50689 1 mm limit), and a stalled visible beam on skin is 0.85 of it. The black glove as beam dump remains good practice. Visible skin is not a blocker.

---

## The coordinator's fill question

**Claim.** The painted fill of a stroke at angle θ to the flow is ≈ n·U·d_s²·t_eye·(|cos θ| + |sin θ|). That is ≈ 0.33 per 50 ms for vertical and horizontal strokes alike, so vertical strokes differ in texture, not fill. Solid-ish lines at the same mass need d_s ≈ 2 mm, since n ∝ 1/d_s² at fixed fill.

**Derivation [DERIVED].**
- Let the stroke be a tube of thickness d_s about an axis at angle θ from vertical. Motes fall at U_f.
- The rate of motes entering the tube per unit axis length is n·U_f·d_s·|sin θ| (vertical flux through the tube's horizontal projection; depth d_s).
- Each lit mote paints a vertical chord of length d_s/|sin θ|. Its projection on the axis is d_s·|cos θ|/|sin θ| + b, where b is the dot's along-axis width (mote plus eye blur, or d_s by convention).
- Over t_eye the covered fraction of the axis is therefore

  **F(θ) ≈ n·U_f·d_s·t_eye·(d_s·|cos θ| + b·|sin θ|),**

  capped by Poisson overlap (F → 1 − e^(−F)).
- **With b = d_s this is exactly the coordinator's formula.** At θ = 0 it is m23's n·d_s²·U·t_eye. The vertical case can also be obtained directly: the linear mote density in the tube is n·d_s², and each mote paints U_f·t_eye.
- **The general identity:**

  F(0°) = F(90°) = n·U_f·d_s²·t_eye = N_s·f_r·t_eye·(d_s/δ) = 0.33.

  It holds because the rain is sized so that N_s·f_r motes cross each δ × d_s window.

**Monte Carlo** (RT9 §10, 2D, 40 runs, 0.3 m strokes, continuous lighting): 0.31 (0°), 0.41 (30°), 0.42 (45°), 0.41 (60°), 0.35 (90°). Overlap trims the 45° peak from 0.47 to 0.42. **Confirmed.**

**Qualifications.**
1. **Texture is not a detail.**
   - Vertical gaps are exponential with mean 1/(n·d_s²) ≈ 39 mm, minus the 13 mm streak.
   - Horizontal gaps have a mean of about δ ≈ 3 mm.
   - Share of stroke length in gaps > 10 mm (≈ 23 arcmin at 1.5 m): **67 % vertical, 22 % at 30°, 7 % horizontal.**

   So T9's conclusion that vertical strokes look worst survives, for a different reason. At 59 % near-vertical (40 % within 10°) that matters for the armor.
2. **The eye blur sets b.** With b ≈ 0.44 mm (1 arcmin at 1.5 m) the horizontal fill is 0.21, i.e. below vertical (0.30), though with short gaps.
3. **FLOW-R2's gating changes both** (M2, C1): 0.11–0.15 vertical, 0.05–0.09 horizontal per 50 ms.
4. **d_s for fill 1 at the same mass** is √(1/(n·U_f·t_eye)) = **1.73 mm** (≈ 2 mm gives 1.33). **Confirmed.** It costs:
   - simultaneous spots ∝ d_s² (×3–4);
   - visible power ∝ d_s (×1.7–2);
   - flashes of 7.7 ms (0.28 of the single-pulse AEL, fine);
   - lines 1.7–2 mm wide (4–4.6 arcmin at 1.5 m);
   - a probe voxel that must grow to δ × d_s ≈ 6 mm², which sharpens C1.

---

## What survives

1. **The verdict "full vision not reachable with known physics plus commodity parts."** It is stronger now.
2. **The m22 bounds:**
   - the Laplace low-pass (only waves address mm structure);
   - the thermal kick theorem (K ≲ 300 or T_rev ≲ 3τ_th);
   - the self-addressing pump floor (≥ kW);
   - Coulomb-crystal softness;
   - the photo-charge one-way rule (direction robust).
3. **The tetralemma arithmetic** (w_max, modes, loop) with h·s = 2.354.
4. **The FLOW-R principle.** A uniform rain plus gated lighting gives one-frame content latency and tolerance of hand wakes and common-mode drafts. This remains the right structural idea for air-carried displays.
5. **Crossed-probe geometry.** At eps ≤ 1 mm, 2–3 camera coincidence localises to P_k⁺, with ghosts ≤ 0.6 % (2 cams) and ≤ 0.05 % (3 cams). The ghost Monte Carlo is correct.
6. **Per-beam visible safety.** Each flash is within Ed. 3 Class 1 rules 1 and 2. C5 does not apply to point sources.
7. **Materials.** The mannitol exclusion stands. Food-grade non-dairy sugars (trehalose) are the right class.
8. **Desk scale.** Opus's desk FLOW-R (0.3 m column, ~1 m of strokes) shrinks C2 (fewer lines per head) and C1's haze cost (×0.3 column depth). It remains the realistic bench target. It inherits C1, C3, M1 and M5 in reduced form.

---

## What would change the verdict (value of information)

1. **A rate-matched probe (C1).**
   - Simulate a sheet-pencil voxel of ≥ 3 mm² with 3 cameras.
   - Show ghosts ≤ 1–2 % and centroid aim ≤ 20 µm.
   - Bench: one sample, measured rate against n·U·A_proj.
2. **A Class 1 head architecture (C2).**
   - Launch each pencil or visible line from distinct points over a large aperture, so that ≤ 4 probe pencils and ≤ 11–35 visible lines share any 7 mm at the first accessible plane, and ≤ 3 mW of 850 nm or 1.57 mW visible passes any 1 mm at the exit.
   - Compute the minimum launch aperture on the armor and get a notified-body pre-opinion.
3. **A latency-bounded aim (C3).** ≤ 5–6 ms end to end with velocity estimation, ≥ 90 % hits in the core, measured with one camera pair, one galvo and seeded motes. Report the hit fraction under a hand.
4. **Measured capture ≥ 99.97 %** with a person walking, a 0.1 m/s draft and stratification, using a thermally controlled column (M5).
5. **A viewing study** of 0.11–0.33 fill and 39 mm vertical gaps against 1.7–2 mm lines at fill ≈ 1. Is it a "hologram line"?
6. **Owner rulings** on three relaxations, not two: the medium, ceiling and floor hardware, and dotted or streaky lines.

Any one of items 1–3 failing on the bench keeps FLOW-R2 a desk curiosity. All three passing, plus item 4, would make a room FLOW-R2 a credible (non-commodity, ~$50–120k+) installation. It would still not be the owner's "just a projector".

---

## Corrected design table (room FLOW-R2, armor 0.6 m, 20 Hz, δ 3 mm, d_s 1 mm, a 7 µm)

| Item | T9 | RT9 as specified | RT9 with fixes |
|---|---|---|---|
| Detected crossings per sample | 20 /s | **3.4–4.8 /s** | 20 /s with a ≥ 3 mm² voxel (ghosts 1–5 %) |
| Dark per 0.1 s | 13.5 % | **62–71 %** | 13.5 % |
| Fill per 50 ms, vertical / horizontal | 33 % / (implicitly full) | **11–15 % / 5–9 %** | 30–33 % / 21–35 % (stretched vertical flashes) |
| Flashes on target | implied ~100 % | **0.2–0.7 %** (Tu 10 %) | 93–99.97 % core; 15–39 % in hand wakes |
| Photo-electrons per detection | 13 000 | 13 000 at eps ≈ 3 mm (ghosts ≥ 5 %) | 230–1 070 at eps 0.5–1 mm |
| Visible head, pupil at 10 cm | "Class 1 per beam" | **4.5–45 mW (11.5–115×)** | needs distributed launch (not designed) |
| Probe head, pupil at 10 cm / skin at exit | open | **104 mW (133×) / 74 mW (24×)** | needs distributed launch (not designed) |
| Room particles at 99.9 % | 50 µg/m³ | 50 (> WHO 45); 0.26 g/day on surfaces | 15 at 99.97 % (unshown) |
| Simultaneous spots | 79 | 79 (107 peak) | 173 mean (vertical fill) |
| Column speed at the image | 0.25 m/s | 0–0.38 m/s with ±1 K | 0.25 ± 0.05 with ±0.3 K control |
| Cost | $30–60k | — | **~$50–120k** plus C2's heads |

---

## Sources

**Web (this review, 5 searches):**
- C5 = 1 for apparent sources < 5 mrad in IEC 60825-1 Ed. 3 (ISH1:2017): [Schulmeister, "Analysis of pulsed emission under Edition 3 of IEC 60825-1", ILSC 2015](https://laser-led-lamp-safety.seibersdorf-laboratories.at/fileadmin/uploads/intranet/dateien/ilsc_2015_analysis_pulsed_emission_ed_3_iec_60825-1_schulmeister.pdf); [IEC 60825-1:2014 preview](https://webstore.iec.ch/en/iec_catalog/product/preview/?id=L3B1Yi9wZGYvcHJldmlldy9pbmZvX2llYzYwODI1LTF7ZWQzLjB9Yi5wZGY%3D).
- EN 50689: child-appealing consumer laser products must be Class 1; skin through 1 mm over 10 s at the closest point of human access: [SIST EN 50689:2022](https://standards.iteh.ai/catalog/standards/sist/3d8e5fe9-a2ff-4dbe-a38d-438365c3f907/sist-en-50689-2022); [UKHSA laser product information sheet](https://khub.net/documents/135939561/174098625/UKHSA+information+sheet.pdf/a5ba1d9a-6340-83a8-b4cc-65c7594088fd?t=1738154882782); [JJR Lab on EN 50689](https://www.jjrlab.com/news/new-european-standard-for-laser-products-en50689-2021.html); [ILSC 2023 on EN 60825-1 A11 and EN 50689](https://pubs.aip.org/lia/ilsc/proceedings-abstract/ILSC2023/2023/L0602/3298026).
- Aridol is mannitol inhalation powder (5–40 mg capsules, bronchial challenge): [DailyMed Aridol](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=5387a4fb-b894-4cba-88a3-a947217d34da&type=display); [Drugs.com Aridol](https://www.drugs.com/aridol.html).
- Milk-protein traces in lactose dry-powder inhalers; contraindication and reported reactions: [JACI, contamination of DPIs with milk proteins](https://www.jacionline.org/article/S0091-6749(03)02677-0/fulltext); [PMC9785354 survey](https://pmc.ncbi.nlm.nih.gov/articles/PMC9785354/); [PubMed 25309152](https://pubmed.ncbi.nlm.nih.gov/25309152/).
- Commodity ILDA 30 kpps galvo sets at $195–455: [eBay listing](https://www.ebay.com/itm/192257753727); [eBay, bigger mirrors](https://www.ebay.com/itm/365500335927); [SpaceLas PT-30K](http://spacelas.com/en_products/galvo-scanner-systems-PT30K-6.html).

**[memory]** (not re-checked this session):
- WHO PM10 24 h guideline 45 µg/m³ and the ACGIH 10 mg/m³ inhalable TLV, both as used in T9;
- Lagrangian C₀ ≈ 6;
- room stratification of 1–2 K/m;
- machine-vision read noise of 2–7 e⁻;
- eye integration of ~100 ms in dim light;
- hobby-galvo drift.

**Repository (read-only):**
- `09_unlock/T9_home_routes.md`, `m22_needles.py`, `m23_flowr2.py` and their logs;
- `idea_round_4_opus.md`, `IDEA_ROUND_4_HOME_BRIEF.md`;
- `05_reviews/FINAL_VERDICT.md`, `red_team_7_gaussian.md`, `red_team_8_pov_x.md`;
- `07_mote_route/mote/safety.py`, `04_engineering/holo_engine/content.py`, `m21b_bead_wakes.py`.

**Files written:**
- `09_unlock/rt9_check.py`;
- `09_unlock/results/rt9_checks.json`, `rt9_run.log`, `rt9_addenda.json`, `rt9_addenda.log`, `rt9_aim.json`;
- this report.

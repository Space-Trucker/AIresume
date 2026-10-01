# MOTE route: results v2 (after red team 4 and the owner's room head arrays)

**Code:** `mote/physics.py` (v2), `mote/budget2.py` (v2; `budget.py` keeps v1 for reproducibility), `mote/feedback.py`. **Validation:** `validation/validate_mote.py`, **31/32 pass**. M22 fails honestly; see §5.
**Review:** `../05_reviews/red_team_4_mote.md` (3 critical, 11 major). **Theory:** `../02_theory/T5_mote_theory.md` (with its v2 correction box).

## 1. What changed from v1, and why

Red team 4 found that v1 was built on an impossible mote, an unrealisable beam and a per-beam-only safety check. I re-derived or recomputed each claim before accepting it (owner rule 12):

| Red-team item | My independent check | Effect |
|---|---|---|
| Major 1: ρ(T_f) mixed with T₀ | ρT = p/R (identity) | Force −20 to −25 % |
| Major 4: C_ph ∈ [1, 1.56] double-counts | Re-derived F = 4π C_s μ² T₁/(ρT). The code's form is C_s = 9/8. Epstein reproduced (M27, M28) | C_ph ∈ [0.67, 1.04]; default 1.0 |
| Major 2: doughnut model | Exact surface-flux integral (M29): η = 0.250 / 0.370 / 0.117, against RT4's 0.247 / 0.372 / 0.118 | Small motes better, large motes 5× worse; beam power 2.4× higher |
| C1 / Major 3: J₁ = A/2 needs absorption depth ≲ a/30 | Straight-ray model (M30) matches RT4's ray trace within 0.08 | Consistent motes needed (below) |
| C2: 10 µm flat-top edge unrealisable | Accepted. My M2c used R_ft = 20–30 µm, whose edges (6.5–9.8 µm) are realisable at the design NA | Flat-top R_ft ≥ 20 µm; the loop still needs ≥ 20–50 kHz |
| C3: Class 1 only per beam | Accepted | Overlap handled by safety-aware scheduling (k_overlap = 1, enforced by the workload manager); fault shutdown required |
| Majors 7–11 and minors | Accepted | Force margin ×1.3; hot-face temperature limit; 45–60 Hz; energy-conserving wall light; u_air margin |
| Major 6: single head | Accepted, confirmed by R8: no pull toward the source | `single` dropped |

## 2. Consistent motes (the first unknown)

Figure of merit: FOM = (J₁/A)/(k_eff + 2k_g) in m·K/W. Speed, force per kelvin and heat budget all scale with it.

| Mote class | Construction | FOM |
|---|---|---|
| Engineered | Silica-aerogel sphere; a *non-percolating island* skin of visible-transparent NIR absorber (e.g. Cs_xWO₃ / ITO nanocrystals); phosphor nanocrystals dispersed inside | 5.3 |
| Core–shell | Dense Eu²⁺ cyan phosphor core (0.6 a); aerogel shell; island absorber skin. Coated-sphere k_eff = 0.046 | 4.4 |
| Plausible-optimistic (RT4) | k_eff 0.15, J₁/A 0.4 | 2.0 |
| Dense (carbon/crystal) | k ≈ 1 | 0.4 |

**None of these has been made or measured.** The v1 headline mote had FOM 6.1, which was optimistic but not absurd. It was inconsistent because it combined a low-k body with skin-deep absorption and 70 % pump absorption.

### 2a. Concrete recipes (R9 materials search, plus my M6 skin analysis)

**Skin requirement (M6).** J₁/A ≥ 0.43 needs the absorber skin to reach optical depth ≥ 2 at 1550 nm, i.e. ≥ 86 % single-pass absorption at normal incidence. The skin must be non-percolating and thin (≲ 0.1–0.2 a).
- At 63 % absorption, J₁/A = 0.30.
- At 26 %, J₁/A = 0.11.

**Recipe A, "engineered" (a ≈ 1.5 µm).**
- Body: silica-aerogel sphere, k ≈ 0.03.
- Emitter: dispersed Eu²⁺-nitride nanophosphor.
- Skin: Cs_xWO₃ tungsten-bronze nanocrystal islands (visible-transparent, stable to about 470 °C), under a thin silica overcoat.
- Expected: FOM ≈ 5.0, but 405 nm absorptance only ≈ 25–40 %.

**Recipe B, "core–shell" (a ≈ 2.5–4 µm).**
- Core: heavily doped BaSi₂O₂N₂:Eu (0.6 a).
- Shell: aerogel.
- Skin: Cs_xWO₃ islands with a silica overcoat.
- Expected: FOM ≈ 4.1 and 405 nm absorptance ≈ 60–90 %. This is the bright variant.

**Validation of these recipes (M7, `sim_m7_recipe_check.py`; owner asked "validate and confirm").**
- **Model self-tests pass.**
  - A thin opaque shell gives A = 1.00, J₁/A = 0.4996.
  - The whole-sphere case matches `physics.j1_over_A`, an independent implementation, to 3 decimals (0.1339 vs 0.1337; 0.4282 vs 0.4278).
- **Cs_xWO₃ absorption from R9's own snippet** (0.9 mg/cm² gives 70 % shielding): α ≈ 9.5×10³ cm⁻¹.

| Recipe | Absorber | Skin τ | J₁/A | FOM | Verdict |
|---|---|---|---|---|---|
| A (a = 1.5 µm, 0.2 µm islands, 60 %) | Cs_xWO₃, α ≈ 1×10⁴ | 0.11 | 0.04 | 0.4 | **FAIL** |
| A | Cs_xWO₃, α = 5×10⁴ (R9 upper) | 0.60 | 0.19 | 2.0 | **FAIL** |
| A | ITO nanocrystals, α ≈ 5.7×10⁵ | 6.8 | 0.49 | **5.3** | PASS |
| B (a = 3 µm, 0.6 µm loaded shell, 40 %) | Cs_xWO₃, 1×10⁴ / 5×10⁴ | 0.23 / 1.2 | 0.07 / 0.30 | 0.7 / 3.1 | FAIL / marginal |
| B′ (a = 4 µm, 1 µm shell) | Cs_xWO₃, 5×10⁴ | 2.0 | 0.38 | 3.9 | marginal |
| B / B′ | ITO nanocrystals | 14–23 | 0.49 | **5.0** | PASS |

- **"Both recipes clear FOM ≳ 4" is NOT confirmed as written.** With the preferred, safer Cs_xWO₃ skin, recipe A fails (FOM 0.4–2.0) and recipe B is at best marginal (3.1–3.9).
- **Only an ITO-class plasmonic absorber** (α ≳ 3×10⁵ cm⁻¹, e.g. ITO or other doped-oxide nanocrystals tuned to 1550 nm) passes, at FOM ≈ 5.
- **R9 rejected ITO for inhalation toxicity.** My exposure estimate:
  - ~1 µg of ITO per day from lost motes gives ~ng/m³ in a ventilated room, about 10³× below the lowest-effect level R9 cites (0.01 mg/m³, rat);
  - a silica overcoat helps further.

  This makes ITO a toxicology question, not a veto. It still needs a toxicology study.
- **Recipe B's 60–90 % pump absorptance** needs Eu²⁺ α₄₀₅ ≳ 4×10³ cm⁻¹. At 1×10³ cm⁻¹ it is only 21–27 %. This is unverified.

**Rejected materials.**
- ITO is a strong absorber, but inhaled indium causes lung disease.
- TiN and carbon are opaque in the visible.
- QDs, perovskites and dyes die above ~150–200 °C.

**Manufacturability.**
- Emulsion aerogel spheres bottom out near 7 µm diameter.
- Pharmaceutical spray-gel aerogels reach d₅₀ ≈ 2.4 µm, so micron aerogel is makeable.
- Its conductivity at 1–4 µm has not been measured. This is the #1 FOM risk.

**Force calibration.** No absolute force-per-absorbed-watt measurement exists for micron particles at 1 atm.
- The continuum formula is routinely inverted in levitated-droplet photophoretic spectroscopy (Bluvshtein et al. 2020), with ±25–60 % retrievals.
- R9 reports Lewittes 1982 (30 Torr) within ~10 % of our model. My own check: this depends on the assumed particle conductivity (k = 0.3 gives 1.5×10⁻⁵ against 1.6×10⁻⁵ N/W; k = 0.1 gives 3.5×10⁻⁵). The droplet's J₁ is unknown, and 30 Torr is near the Kn ≈ 1 force maximum where the continuum form is not valid.
- **I count Lewittes as order-of-magnitude consistency, not calibration. Bench item 1 stands.**

## 3. Heat-limited speed, corrected

Mote speed relative to the air, with the hot face held at T_face ≤ 450 K, before any draft margin:

| Mote | a | Push (room rig) | Passive pairs |
|---|---|---|---|
| Engineered | 1 µm | 0.93 m/s (1.23 at 500 K) | 0.41 m/s |
| Engineered | 2.5 µm | 0.47 m/s | 0.38 m/s |
| Core–shell | 1 µm | 0.79 m/s | 0.35 m/s |
| Optimistic | 1 µm | 0.39 m/s | 0.17 m/s |

v1 claimed 1.6–2.7 m/s. **Room drafts of 0.15–0.3 m/s now consume most of the available speed.**

## 4. The room (owner's direction: many discreet heads)

M4 studied head layouts in a 6 × 5 × 2.8 m room, with the image above a workbench:

| Layout | Push heat factor h, worst / mean | One head blocked | Throws |
|---|---|---|---|
| 4 corners (room-tetra) | 16.5 / 3.3 | infeasible | 3.9–4.0 m |
| 8 corners | 4.8 / 1.9 | worst 16 | 3.9–4.0 m |
| 8 corners + ceiling spot + floor head | 2.14 / 1.38 | worst 6.6 | 1.2–4.0 m |
| **R12 "lab rig"** (6-head ceiling ring + 4-head low ring + ceiling spot + floor head) | **2.22 / 1.33** | 1 % of cases infeasible | **1.2–2.3 m** |

**Lesson:** corner heads are too far and too shallow. The rig needs heads directly above and below the image and a ring close by. Motes use about 3 beams at a time, and the workload manager chooses the heads.

## 5. Corrected atlas (M5, `sim_m5_atlas_v2.py`; 5 760 cells)

**Normal room** (0.3 m/s drafts, T_face ≤ 450 K, optical brighteners in white fabrics): **nothing is feasible, not even a 1 m accent.**
- The speed budget goes to the drafts.
- Stray 405 nm pump makes white fabrics glow.
- Trap beams cannot stay within Class 1 with overlap.

**Designed lab** has four features:
- a quiet-air zone ≤ 0.15 m/s;
- phosphor tolerant to 500 K;
- safety-aware scheduling, so no two foci of one head share a line of sight;
- non-fluorescent surfaces.

In the designed lab, at 45 Hz, with engineered or core–shell motes:

| Target | Architecture | Motes | Trap channels | 1550 nm total | Notes |
|---|---|---|---|---|---|
| Accent (1 m) | passive pairs, a = 2.5 µm | 420–500 | **840–1 000** | 2.6–3.5 W | No fast loop needed |
| Iron-Man sketch (5 m) | push, a = 1.5 µm | 885–1 060 | 2 660–3 190 | 8–11 W | Needs a ≥ 20–50 kHz loop |
| | passive pairs | 1 840–2 200 | 3 670–4 410 | 15–16 W | |
| Film density (30 m) | push, a = 1.5 µm | 3 040–4 380 | 9 100–13 100 | 33–45 W | |
| | passive pairs | 6 300–7 570 | 12 600–15 100 | 63–85 W | |
| Film-exact, lit (50 cd/m²) | push, a = 4 µm | 13 000–15 700 | 39 000–47 000 | 51–69 W | |

- **At 60 Hz** everything is +33 %.
- **Plausible-optimistic mote:** 3–5× worse. The accent needs 3 750 channels and film density 68 000.
- **Dense mote:** infeasible.

**BYU consistency, v2 (M22 fails).** The corrected force puts BYU's lateral 1.83 m/s at ΔT = 270–745 K across k_p 0.05–0.2 and C_ph 0.67–1.04. The conservative corner exceeds a char particle's tolerance. So either BYU's particle was low-k and near C_ph ≈ 1, or real forces exceed our continuum model. **Only a force-per-absorbed-watt measurement resolves this** (bench item 1).

## 6. What remains true

- **1550 nm trap beams:** each is ≤ 10 mW. Room-wide exposure is ≲ 1 mW/cm² against an MPE of 100 mW/cm².
- **No chemistry, no noise.** Motes run below 500 K; photophoretic motion is silent.
- **Particle load negligible:** µg/day, though 1–2.5 µm motes are respirable and their composite toxicology is unknown.
- **Physics:** no law is violated.

## 7. Verdict for the MOTE route

Not a physics "yes". It is a conditional design. It requires:
1. a mote with FOM ≳ 4 m·K/W and a strongly absorbing emitter core; this is **materials research**;
2. a designed room: quiet air, non-fluorescent surfaces, a 12-head rig;
3. a steering engine of **~10³ channels (accent) to ~10⁴ (film density)**, étendue-tiled with hand-over (RT4 Major 5);
4. a novel **Class 1 safety argument**: scheduler-enforced no-overlap plus certified fault shutdown.

Home use in an ordinary room is ruled out by drafts.

## 8. Prediction scores (P15–P26, registered before the runs; rescored after the corrections)

| ID | Result (v2) | Score |
|---|---|---|
| P15 | 5 µm mote at ≤ 450 K: 0.21–0.47 m/s | ~ partial (optimistic mote below the interval) |
| P16 | Sketch 885–2 200 / film 3 040–7 570 motes | ✗ (above the intervals) |
| P17 | Film-density IR 33–85 W | ✗ (above 1–30 W) |
| P18 | lm per W of total IR: 0.02–0.05 (cyan phosphor; UC was dropped as inconsistent) | ✗ (below 0.05–2) |
| P19 | 5 µm mote at ≥ 0.7 m/s: heat-limited to 0.47 (0.64 at 500 K) | ✗ |
| P20 | Not tested as stated | inconclusive |
| P21 | Film-exact: 0.13 W absorbed emitter, no gases, silent | ✓ (but 40k channels) |
| P22 | Single-head lateral at 100 mm: 0.25 m/s (v1 linear law); exact LG01 lowers it | ✓ (v1 basis) |
| P23 | Loop ≥ 20–50 kHz (20 µm flat-top), 50–100 kHz (narrow beams, RT4) | ✗ |
| P24 | Class 1 not established without scheduling and fault-shutdown design; power 33–45 W | ✗ |
| P25 | UC mote inconsistent (a dense crystal cannot be low-k) | inconclusive |
| P26 | BYU ΔT 270–745 K | ~ partial |

**Tally v2:** 2 ✓, 2 partial, 6 ✗, 2 inconclusive. The v1 tally (8 ✓) was flattered by my own model errors, which is exactly what the red team was for.

## 9. Touch (M9, `sim_m9_touch.py`)

**Setup.** The sketch-density armor (466 motes, L3 push design) and a hand, modelled as a 4.5 cm sphere, sweeping through at 0.3–1 m/s. Air is potential flow plus a crude wake. The beams track the motes (closed loop).

**Without hand avoidance.**
- The hand's air wake displaces motes by ≤ 2 mm (the trap budget of 0.69 m/s copes).
- **6–14 % of the motes it meets are lost by contact** (27–63 per pass); they hit the glove.

**With avoidance.** The workload manager tracks the hand and predicts it 150 ms ahead, then pushes motes sideways out of the hand's path.
- **0 lost.**
- 20–30 % of motes part by up to 5.5 cm around the hand.
- All are back on their strokes as soon as the hand has passed.

The image parts around the hand like smoke and reforms. This is consistent with "touchable", with feel supplied by the haptic glove.

**Caveats.**
- The flow model is crude: a sphere hand and a cartoon wake.
- Beam occlusion by the hand is not included. M4 says the 12-head rig keeps full force authority with one head blocked in 99 % of cases.
- Fingers moving fast (> 1 m/s) close to motes will still strip some.

## 10. Steering engine (R10 survey; M10 coverage; my checks)

**Every beam fills the head's window.** Focusing to w = 10 µm at 1.5 m needs a 1/e² beam diameter of ~148 mm at the head (checked: w_head = λz/(πw₀) = 74 mm radius). Beams cannot each own a patch of the window. The workable layout is one shared large objective, with each steering channel owning one cell of its intermediate field and handing motes over between cells.

**Étendue floor.** A head needs steering modules ≥ f_cov · (G/E)².
- G ≈ 166 mm·rad per axis for the trap (216 with the 405 nm pump).
- E is one steerer's étendue. Checked for a 10 mm galvo (E ≈ 7 mm·rad): ~560 modules at f_cov = 1, against R10's 620–960.
- Modules per film-density head:

  | Steerer | Modules |
  |---|---|
  | 20 mm galvo pairs | 150–240 |
  | 10 mm galvo pairs | 620–960 |
  | 5 mm MEMS | ~15 000 |
  | 4K LCoS | ~2 400 |
  | 1550 nm AODs | ~155 000 |

- **Neutral-atom tweezer arrays** (~10⁴ traps) address only ~10³ spots per axis, 25–300× too few.

**M10 coverage.** Restricting each head of the 12-head rig to a sub-field:

| Coverage f_cov | Worst-case heat factor h (p95) | Infeasible cases |
|---|---|---|
| 1.0 | 2.22 (1.76) | 0 % |
| 0.75 | 3.74 (2.03) | 0 % |
| 0.58 | 8.0 (3.39) | 0 % |
| 0.50 | 16 (5.0) | 0.4 % |

So f_cov ≈ 0.75–1. Partial coverage trades steering hardware for mote speed almost one for one.

**Focus tracking is the least mature function.** ±0.25 m needs 10²–10³ waves of defocus at 0.2–5 kHz.
- Fast devices (AO lens, KTN, deformable mirrors) lack the range.
- Best fit: an optical-disc-pickup voice-coil objective used as a remote-focus unit (3–10 kHz). Its stroke is unverified.

**Cost today** (R10 estimates, ±2–3×), per channel: DFB laser, galvo pair, pickup focus, quad-cell sensor; $0.7–5k each.
- Accent room: $0.5–5 M.
- Film-density room: $4–40 M, with ~1–1.5 m-square module arrays per head.

**With 5–10 years of integration** (2-axis analog MEMS mirror arrays with built-in angle sensing plus integrated photonics): ~$50–250 and 0.1–0.3 W per channel, putting a film-density room at ~$0.4–2 M with ~0.3 m heads.

**The single most valuable engineering development:** a 2-axis analog MEMS mirror array with 4–8× today's étendue per mirror (5–9 mm·rad per axis, ≥ 1 kHz, integrated µrad angle sensing, ideally integrated focus).

# Red team 3: the "lumen-locked pollution law" (T4), NOTEBOOK entries 9–11, and the E10c re-grade

Reviewer roles: plasma spectroscopist, indoor-air and photobiology safety specialist, statistician. The brief was to break T4 and E10c if they are wrong, confirm them if they hold, and be quantitative.

**State reviewed** (2026-09-30, about 15:00 UTC):
- `02_theory/T4_lumen_locked_pollution.md`
- `NOTEBOOK.md` entries 9–11
- `06_spark_instrument/PREDICTIONS.md`
- `results/validation.json`, `results/atlas/*.json` (40 cases), `results/val_*.json`
- `spark/{radiation,chemistry,hydro,run_spark,atlas}.py`, `validation/validate.py`
- `03_simulations/sim_e10c_spark_regrade.py`, `display_budget.py`
- `05_reviews/red_team_2_spark.md`, to check which of its fixes were made

**Method.** Numbers marked *[RT3]* were computed for this review with SPARK's own modules. The scripts are in the session scratchpad and are not committed: `tab1.py`, `xi_sens.py`, `zsplit.py`, `instr_run.py`, `caps.py`, `e10c_var.py`.
- **One SPARK run.** An instrumented re-run of `A_E10uJ_eps3e+08`, the format E10c picks most often for the sketch. It reproduces the atlas file exactly: lm·s 3.798×10⁻⁷, act_J 7.549×10⁻¹⁰, NO/NO₂/O₃ identical. It adds histograms of lumens, actinic energy and VUV/EUV photons by cell T, ρ, phase and time.
- **E10c re-run** as a parametrised copy. Variant V0 reproduces the stored `e10c_spark_regrade.json` exactly.
- **Memory-flagged numbers** are marked [memory] and must be checked before use as pass/fail criteria.

**Severity counts:** 3 critical, 9 major, 7 minor.

**Verified correct:**
- T4's cap arithmetic for the scenario as stated. The UV cap comes out at 0.91–1.10 lm. The strict-air caps come out at 0.034–0.071, 0.060–0.123 and 0.241–0.494 lm for capture 0.3 / 0.6 / 0.9.
- The target fluxes: 4π·L·(1 mm)·S = 0.038 / 0.19 / 0.45 / 1.51 / 18.8 lm.
- The atlas numbers, and the line-focus per-lumen equality (−2 % and +14 %).
- The E10c table in NOTEBOOK entry 11, reproduced exactly.
- VUV line photon counting (E·λ/hc). The Voigt-escape clipping at a = 10 is harmless, because the profile is already Lorentzian there.
- The O-atom fate for VUV photons absorbed in ambient air (Finding 9).

---

## Critical

### 1. Critical: the "UV per lumen invariant" restates SPARK's z = 1 Kramers–Unsöld continuum shape. Its ±13 % is model spread, not uncertainty.

**Evidence [RT3].**

*The ratio is fixed in the emissivity table, before any hydrodynamics.*
- In the table itself, act/lm is:
  - 1.2–1.8×10⁻³ along the 1-atm isobar from 9 to 20 kK;
  - 1.2–2.1×10⁻³ at 10–100× the isobaric density from 9 to 40 kK;
  - (`tab1.py`).
- Any hydro history therefore returns about 2×10⁻³. SPARK's own ns validation sparks (50–200 mJ, r₀ 150–300 µm) give 2.40–2.47×10⁻³, and the inefficient ε = 10⁸ micro-sparks give 1.80–1.84×10⁻³.

*The z = 1 continuum makes both the light and the UV.* In the phase that emits the light (next finding), the singly-charged-ion continuum (free-free plus K-U free-bound) supplies almost all of both quantities (`zsplit.py`):

| T, ρ | z = 1 share of lumens | z = 1 share of actinic | act/lm |
|---|---|---|---|
| 20 kK, 0.3 kg/m³ | 0.98 | 1.00 | 1.92×10⁻³ |
| 30 kK, 1.0 kg/m³ | 0.93 | 0.98 | 2.14×10⁻³ |
| 35 kK, 1.0 kg/m³ | 0.79 | 0.90 | 2.09×10⁻³ |

The atomic line list has no line between 180 and 340 nm, so lines contribute 0 % of the actinic dose.

*The dose sits exactly where the model is least constrained.*
- 87–89 % of the ICNIRP-weighted dose falls in 240–315 nm.
- That band straddles the model's χ_g(z = 1) = 4.0 eV cut (310 nm) and the real N I/O I 3s photo-recombination edges (N 3s ⁴P 295 nm, ²P 318 nm; O 3s ⁵S 277 nm, ³S 302 nm).
- 180–195 nm, which O₂ absorbs within centimetres of air, is only 0.5 % of the dose, so starting S(λ) at 180 nm does not matter.

*Sensitivity at 14–18 kK and 1 atm, with everything else as coded (`xi_sens.py`):*

| Change | act/lm multiplier |
|---|---|
| ξ flat 1.0 or 2.0 instead of 1.5 | ×0.95–1.05. A single ξ multiplies UV and visible alike. |
| ξ_UV/ξ_vis = 0.5 | ×0.51 |
| ξ_UV/ξ_vis = 2 | ×1.97 |
| χ_g(1+) = 3.5 eV | ×0.65–0.72 |
| χ_g(1+) = 4.5 eV | ×1.33–1.6 |
| Molecular bands ×3 | ×1.00 above 9 kK (they only matter below 8 kK, where almost no light is made) |
| Adding C I 247.9 nm (CO₂) | +0–3 % |
| Optically thick limit: blackbody at 20 / 30 / 50 / 100 kK | 4.7 / 6.8 / 8.9 / 10.7×10⁻³, i.e. ×2.4–5.4 |

**Realistic range.**
- The real 3s photo-ionisation cross-sections of N I and O I are probably sub-hydrogenic near threshold [memory], which argues for ξ_UV/ξ_vis < 1.
- Continuum lowering at n_e ≈ 10²⁵–4×10²⁵ m⁻³ is 0.4–0.7 eV [RT3, Debye estimate]. That is comparable to the gap between χ_g and the 270 nm actinic peak.
- Missing N II/O II/N III 3s–4p-type UV lines are weak: ≲ +20 %.
- **Model-form range for LTE, optically thin sparks: ×0.3–2 around 2×10⁻³, i.e. about 0.6–4×10⁻³ J_eff per lm·s.**
- Outside LTE the invariant does not apply at all:
  - Optically thick early phases (real ns sparks: τ ≈ 1 and T_e > 100 kK, Borghese & Merola 1998) push the ratio up ×2–5.
  - Non-thermal fs micro-plasmas emit N₂ 2+ / N₂⁺ 1− bands rather than LTE continuum, which could put act/lm orders of magnitude from 2×10⁻³.

**Effect.** The "±13 %" in T4's table is the spread of one deterministic model over a designed grid. It is not an uncertainty, and a reader will misread it as measurement-grade precision. The real uncertainty is about ×3 each way, and only LTE, thin plasma is covered. Every UV cap inherits this: at T4's own scenario the UV cap is 0.42–3.0 lm, not "1.0 lm".

**Fix.**
- Report the model-form band next to the value.
- Replace constant ξ and χ_g with species- and λ-resolved photo-recombination: Opacity Project/TOPbase cross-sections for N I, O I, N II and O II (RT2 must-fix 6 is still open).
- Test against the absolute UV–visible continuum data the lab already lists: Borghese & Merola 1998 (180–850 nm continuum of a ns spark, in `VALIDATION_DATA.md` but unused), plus air-arc continua at 10–15 kK.
- Restrict every statement to LTE, optically thin thermal sparks.

### 2. Critical: the UV cap "Φ ≤ 1.0 lm, whatever the air handling" is an exposure-scenario artefact, not a hard cap, and "film density exceeds the UV cap" flips under realistic or regulatory scenarios

**Evidence [RT3, `caps.py`].** Isotropic point source, act/lm = 1.9–2.3×10⁻³ nominal, 30 J/m² eff per day (ICNIRP 2004 actinic EL). The model-form band in brackets uses 0.7–5×10⁻³.

| Scenario | Φ_max (lm) |
|---|---|
| IEC 62471 classification at 200 mm (non-GLS lamp distance): exempt, 1 mW/m² eff [memory] | 0.22–0.26 [0.10–0.72] |
| IEC 62471 at 200 mm: RG1 | 0.65–0.79 |
| IEC 62471 at 200 mm: RG2 | 6.5–7.9 |
| T4: 0.4 m, 8 h/day continuous | 0.91–1.10 [0.42–3.0] |
| 0.4 m, 2 h/day | 3.6–4.4 [1.7–12] |
| 1.0 m, 4 h/day | 11–14 [5–37] |
| 1.5 m, 8 h/day | 13–15 [6–42] |
| 1.5 m, 2 h/day (home viewing) | 51–62 [24–170] |
| 3 m, 2 h show (venue) | 204–247 [94–670] |

- The ICNIRP EL is a daily dose limit. Intermittent exposure adds dose, and there is no dose-rate term in this range, so 2 h/day allows 4× the irradiance of 8 h.
- A 30–50 % content duty cycle (not all strokes lit all the time) adds another ×2–3.
- T4's 0.4 m / 8 h case happens to equal the IEC 62471 *exempt* criterion (30 J/m² in 30 000 s), but applied at 0.4 m instead of the standard's 0.2 m. So it is neither the regulatory case (4× stricter) nor the realistic one (50× more lenient).
- For image projectors, IEC 62471-5 is the governing product standard. Its assessment distance must be checked [memory].
- The point-source formula overstates irradiance for a 5 m stroke folded into a roughly 0.5 m image. For a line source seen from 0.4 m, E ≈ (Φ/S)/(4d), about 4× below the point-source value.

**Effect.**
- UV is not the binding limit for any Iron-Man target at normal viewing distances. It binds only for face-close, all-day exposure, or for "exempt" labelling at 0.2 m.
- At 1.5 m and 2 h/day, film density (1.5 lm) passes UV by 34–41×, and film-exact (19 lm) passes by 2.7–3.2×.
- T4's sentence "Film density exceeds the UV cap" is true only for the 0.4 m / 8 h case.
- The sentence "the UV cap alone limits a continuous display to Φ ≤ 1 lm with the user at 0.4 m" is arithmetically right but is presented as a law.

**Fix.** Present UV as Φ_max(d, hours/day) = 30·4πd²/(a·t), in a table or plot, with a ∈ [0.7, 5]×10⁻³. Add the IEC 62471/62471-5 risk-group classification as a separate row.

### 3. Critical: E10c's conclusions are not driven by T4, and the venue probabilities are not robust

**Evidence [RT3, `e10c_var.py`, 800 draws, seed 23; V0 reproduces the stored results].**

**E10c does not implement lumen locking.**
- It multiplies per-J yields by u_Y and u_act, and η by u_η, independently.
- The per-lumen UV then varies as u_act/u_η ∈ [0.17, 9] and the per-lumen air load as u_Y/u_η ∈ [1/9, 9]. That spread is far wider than T4's own ±2–3×.
- E10c's UV failures at film contrast (26 % of draws at 0.45 lm, where T4 says the cap is 1 lm) come entirely from this.
- Lumen-locked sampling (V3) changes P(venue): accents 0.73 → 0.78, sketch 0.23 → 0.16, film contrast 0.05 → 0.01. The sentence "This is why the E10c probabilities fall as they do" is therefore not true of the code.

**P(home) = 0 comes from noise, not from T4.**
- The 48 dB(A) fan alone exceeds the 35 dB(A) home limit, so P(home) = 0 is forced by construction.
- Even with a 30 dB(A) fan (V1), and with the smaller +2.5 dB correction (V2), the spark noise alone exceeds 35 dB(A) in 97–100 % of draws.
- For the sketch with the nominal 10 µJ format (4.96 W absorbed, 5×10⁵ sparks/s), the spark-only level at 0.4 m is 67 / 61 / 54 / 47 dB(A) for 0 / −6 / −13 / −20 dB tracing gain, before the +5.4 dB.
- Under the realistic home scenario (V8: listener at 1.5 m, UV 1.5 m / 2 h, quiet purifier), P(home) for **sparse accents is 0.13, not 0**. It stays 0 from the sketch upward.

**The venue probabilities depend on untested levers and assumptions:**

| Variant | Accents | Sketch | Film contrast |
|---|---|---|---|
| E10c as run (V0) | 0.73 | 0.23 | 0.05 |
| No subsonic-tracing gain (V7) | 0.06 | **0.00** | 0.00 |
| Only claimable formats, ε ≤ 3×10⁸ (V4) | 0.54 | 0.14 | 0.02 |
| Per-format independent η error ×1.4 (V5, winner's-curse check) | 0.78 | 0.30 | 0.06 |
| Capture fixed at 0.9 (V6b) | 0.83 | 0.40 | 0.13 |
| Noise +2.5 dB instead of +5.4 (V2) | 0.84 | 0.32 | 0.08 |
| Realistic geometry and hazard-consistent air (V8) | 0.98 | **0.64** | 0.29 |

**Effect.**
- "P(home) = 0" survives for the sketch and above, but it is a noise result, not a T4 result.
- The venue numbers (0.69–0.73 / 0.15–0.23 / 0.03–0.05) are fractions of an arbitrary prior box. Plausible choices move the sketch between 0.00 and 0.64.
- The single biggest lever is the unvalidated subsonic-tracing gain from E6c: without it, venue feasibility is about 0.

**Fix.**
- Report P conditional on the design levers (capture fraction, tracing gain) as a 2D map, and integrate only over model-form uncertainty.
- Sample per-lumen UV and air directly (T4 bands), independent of η.
- Use only claimable formats.
- Give the noise correction per format (Finding 8).
- State the exposure scenario for each P.

---

## Major

### 4. Major: all light, UV and VUV of an efficient micro-spark is emitted in the first ~50 ns, from dense 20–40 kK plasma, which is the least-validated part of SPARK

**Evidence [RT3, instrumented `A_E10uJ_eps3e+08` run].**
- Timing: 100 % of lm·s, actinic energy and VUV/EUV photons come from phase 1 (compressible); 0 % from the isobaric phase. 10 / 50 / 90 / 99 % of lm·s have been emitted by 1.0 / 3.9 / 18 / 54 ns.
- Density: 70 % of lumens come from cells at ρ ≥ 0.3 kg/m³ (ambient 1.2).
- Temperature: 66 % of lumens come from 20–40 kK; 30 % from 10–20 kK; 4 % from 40–60 kK; < 0.1 % below 10 kK.

This is consistent with NOTEBOOK entry 9's isochoric figure of merit, which peaks at 40–60 kK. But it means the per-lumen ratios are set by the instantaneous, isochoric, LTE Gaussian initial state, which RT2 Finding 14 flagged and which has not been addressed:
- **ns pulses** deposit energy over 5–10 ns, i.e. *during* the emission.
- **fs/ps pulses** leave T_e ≠ T_i and ionisation out of equilibrium for 0.3–3 ns (the fs data in VALIDATION_DATA show non-LTE N₂-band plasmas).
- **Dense plasma:** at n_e of 10²⁵–5×10²⁵ m⁻³, continuum lowering (0.4–0.7 eV) and Stark merging reshape exactly the 250–320 nm region.
- **Atlas axes:** (E, ε) are not laser parameters.

**Effect.** "For any spark format" cannot be carried from SPARK's initial conditions to real laser pulses. The locked ratios apply to one idealised initial state.

**Fix.**
- Record lm·s(t) (RT2 must-fix 5 is still open; this run shows why it matters).
- Add finite-duration deposition, at least a source term over τ_L.
- For fs/ps formats, add a two-temperature or collisional-radiative bound, or state that SPARK does not apply.

### 5. Major: 24–54 % of "reactive per lumen" (and 26–67 % of NO) is the ad hoc EUV channel "1 NO + 1.5 O₃ per < 102 nm photon". Physically those products are thermalised.

**Evidence [RT3].**
- Over the 27 efficient cases, 2.5·ph_ion / (NO + NO₂ + O₃) = 0.24–0.54. For the ε = 3×10⁹ formats, photo-NO is 51–67 % of all NO (26–29 % at ε = 3×10⁸) (e.g. 10 µJ: thermal 4.8×10¹⁶, photo 6.8×10¹⁶ per lm·s).
- EUV absorption: σ(N₂, O₂) at 50–100 nm is about 2–3×10⁻²¹ m², so the mean free path in air is ≈ 16 µm.
- Timing: EUV is emitted mostly at 30–60 kK in the first ~1–20 ns, when the blast front is at 24–60 µm.
- The EUV is therefore absorbed in gas that is shock-heated to thousands of K within nanoseconds. O₃ cannot form or survive there, and its O/N atoms and ions enter the hot-shell chemistry. RT2 Finding 10 / must-fix 2 (absorber-resolved, spatially deposited photolysis) was not done.
- For ns sparks, EUV is 14 % of E_abs: a large unmodelled local heat source. For micro-sparks it is 0.3–1.5 %.

**Effect.**
- If the EUV products are thermalised with no extra NO, reactive per lm·s falls from 1.8–3.7×10¹⁷ to about 1.2–2.0×10¹⁷.
- T4's "~60 % O₃ from VUV photolysis of O₂" is mislabelled: about 40 % of that O₃ is this EUV assumption.
- T4's "NO is set by freeze-out of the same kernel" is false for the high-ε formats, where most of the NO is ad hoc.

**Fix.** Deposit the EUV energy in the adjacent cells (radiative preheat) and let the thermal chemistry handle it. Report the EUV-derived products separately, or drop them, and carry the difference as a band.

### 6. Major: reactive-per-lumen "locking" is a post hoc subset. As registered, P14 is already falsified in-model and is ill-posed.

**Evidence [RT3].**
- Across all completed atlas designs, reactive per lm·s spans **1.8×10¹⁷–4.0×10¹⁸ (22×)**:
  - ε = 10⁸: 1.4–4.0×10¹⁸;
  - double pulse at 30 and 300 ns: 5.5×10¹⁷ and 1.2×10¹⁸.
- The lock appears only after selecting η ≥ 0.016 *after seeing the data*.
- The atlas follows a two-term form: **R/lm ≈ Y_ph + Y_th/η**.
  - Y_ph ≈ 1.0–2.3×10¹⁷ per lm·s: photolytic, proportional to light.
  - Y_th ≈ 0.2–1.5×10¹⁶ thermal NO per J (e.g. 10 µJ at ε = 10⁸: 3.48×10¹⁸ × 0.0024 = 8×10¹⁵/J; 1 µJ at 3×10⁸: 1.9×10¹⁵/J; 1 mJ at 10⁸: 1.5×10¹⁶/J).
  - Selecting high η mechanically selects low R/lm.
- By contrast, UV/lm really is flat across *all* formats (1.80–2.31×10⁻³), because of Finding 1.
- P14 reads: "any spark format ... reactive/lm·s within 1–7×10¹⁷". SPARK's own ε = 10⁸ and double-pulse cases already violate that.
- The quantity "NO + NO₂ + O₃" is not conserved. Each NO + O₃ → NO₂ removes one molecule from the sum, so a chamber measurement after titration reads about 0.6× the at-birth sum. P14 names no measurement time or partition.
- T4's upper end (3.73×10¹⁷) is set by `B_double_5+5uJ_delay3ns`, a case outside the verified envelope (second-pulse absorption assumed 100 %, RT2 Finding 13).
- T4 says "30 designs"; the completed efficient set has 27 (28 including a stalled shell run).

**Effect.** "They do not depend on how the spark is made" is contradicted by the lab's own table. P14 cannot be scored as written.

**Fix.**
- State the two-term law and its domain.
- Re-register P14 with:
  - a domain (LTE thermal sparks with η well above Y_th/Y_ph ≈ 0.01–0.15 lm/W);
  - separate predictions for NO, NO₂ and O₃ at a stated dilution and time;
  - UV predicted separately from the chemistry.

### 7. Major: the O₃ uncertainty is misattributed, and an existing dataset that could test it has not been used

**Evidence [RT3].**

*Stark widths are not the main lever.*
- In the dense emitting phase the VUV lines are nearly optically thin. Stark damping is a ≈ 100–1000 (0.01 nm × n_e/10²³ gives 1–5 nm widths), so line-centre τ₀ ≲ 1–3 and β = 0.55–1.0.
- The dominant emitters are N I 120.0 (24–40 % of line photons at 15–25 kK), N II 108.5, and N II 91.6 and O II 83.4. The last two are EUV (< 102 nm) and feed Finding 5.
- Photolytic O₃ per lumen is therefore about linear in the memory-flagged gA values and the completeness of the line list. It depends only weakly (about ×0.6–1.1) on the Stark widths that T4 cites as the ±3× driver.
- The gA values of the dominant lines look right to ±50 % [memory]. O I 130.4 seems to use one component's A (2×10⁸ s⁻¹) where the upper-level total is about 6×10⁸ [memory], but O I contributes ≤ 5 % in the dense phase.
- The missing metastable-edge VUV continuum (RT2 Finding 16, not fixed) could add +2 % to +75 % to O₃.

*The O-atom recombination route does not make sparks cleaner (Finding 9).*

*Contradicting data are on file.* `VALIDATION_DATA.md` §4 records Cook et al. 2000 (JGR 105): long electrical sparks of 9.8×10⁴ J gave NOx of 1.1×10¹⁶ per J, *all as NO*, with *no detectable O₃*. Since NO₂ would appear if O₃ had formed and been titrated, this means essentially no photolytic O₃ in that configuration. Long sparks have mm–cm channels in which the VUV is more strongly trapped, so this does not falsify micro-spark O₃. But it contradicts "any spark format", and SPARK has not been run on it.

**Effect.**
- The ±3× on O₃ is defensible in size but not in reasoning.
- The only available observation for the O₃ channel is a null result that nobody has confronted.
- Plausible reactive per lm·s for efficient LTE sparks is about 0.8×10¹⁷–7×10¹⁷. Much cleaner than that (≥ ×5 below T4) is implausible for LTE sparks, because the thermal-NO floor Y_th/η plus real VUV lines stay. For non-LTE fs plasmas it is open (O₃ is then made by electron impact: Petit 2010 reports up to 10¹⁴ O₃ with O₃ ≫ NO).

**Fix.**
- Run SPARK in cylindrical geometry at Cook's conditions (about 5×10⁴ J/m, mm radius) and compare O₃ and NO₂.
- Take gA and Stark widths from NIST/Konjević, not memory.
- Register "O₃/NO at birth" as its own prediction.

### 8. Major: the E10c noise correction (+5.4 dB) double-counts, and the V16 measurement is ill-conditioned

**Evidence [RT3].**
- `display_budget` uses dV = (γ − 1)E_heat/(γp₀), which is 1.35–1.56× SPARK's `dV_hot` in every atlas case.
- The V16 ratio (1.86) is computed against SPARK's own `dV_hot`. The ratio of SPARK's waveform to the budget formula is therefore monopole_ratio × dV_hot/dV_budget, which varies by format:

| Format | Net correction |
|---|---|
| 1 µJ | +7.1 dB |
| 3 µJ | +4.5 dB |
| **10 µJ** (E10c's usual choice for the sketch) | **+2.5 dB** |
| 30 µJ | +1.6 dB |
| 100 µJ – 1 mJ | +0.1 to +1.0 dB |

  RT2 minor Finding 20 already gave the +2.5 dB figure.
- The 2–15 kHz amplitude is 40–60 dB below the pulse's spectral peak. It is taken from a probe record that ends about 3 µs after the wave arrives (the switch requires shock_r > 1.3·r_probe) and is then zero-padded to 20 ms. A small net-impulse error then dominates.
- In the mixing runs the "monopole ratio" is 9–20, because the mixing sink removes enthalpy without expanding the entrained air, so `dV_hot` is wrong there (minor Finding 17).

**Effect.** E10c is 2.9 dB too pessimistic for the formats it actually picks, and too optimistic for 1 µJ formats. Switching the correction to +2.5 dB moves P(venue) from 0.73 to 0.84 (accents) and from 0.23 to 0.32 (sketch).

**Fix.**
- Use the net correction per format.
- Re-measure V16 with a probe record long enough to include the full rarefaction, or with a direct volume-history (d²V/dt²) estimator.
- Keep the fan as a separate, placeable source.

### 9. Major: the air caps rest on a metric and a near-field model that are 2–3× off in each direction

**Evidence [RT3, `caps.py`].**

*The "strict" criterion over-counts.*
- It adds NO + NO₂ + O₃ and compares the sum with the NO₂ limit (13 ppb ≈ WHO 24-h 25 µg/m³).
- After complete NO + O₃ titration, the NO₂ formed per lm·s is 0.8–1.6×10¹⁷, which is 43–60 % of the sum. Untitrated, the O₃ is 0.9–2.3×10¹⁷.
- A hazard-consistent test (NO₂ after full titration ≤ 13 ppb, and untitrated O₃ ≤ 20 ppb, each the worst case) raises the caps 2.3–3× over T4's.
- Titration is fast enough to matter near the image: at 0.3 ppm the time constant is about 7 s, against about 50 s for the plume to reach the face.

*The chosen limits suit continuous exposure only.* The 13 ppb and 20 ppb limits correspond to 24-h NO₂ and 8-h O₃ guidelines (Health Canada residential: NO₂ 11 ppb long-term and 90 ppb over 1 h; O₃ 20 ppb over 8 h [memory]). For 2 h/day use, the 1-h NO₂ limit and the 8-h O₃ average apply.

*The near-field term dominates.*
- The plume term S/(4πD_t·r_face) supplies 88 % of the breathing-zone concentration (31.8 of 36.2 s/m³). It rests on D_t = 0.005 m²/s and r_face = 0.5 m (the UV and noise use 0.4 m).
- The caps scale roughly as D_t·r_face, so they are uncertain by ×3 from mixing alone.
- A scrubber efficiency of 0.85 for NO is optimistic: carbon media capture NO poorly.

*Minor:* T4 understates the upper ends of the O₃ caps (the 1 mJ / 3×10⁸ case at 0.91×10¹⁷ per lm·s gives 0.22 / 0.38 / 1.5 lm).

**Effect.** The strict-air caps quoted in T4 (0.035–0.07 lm at capture 0.3) are conservative-case numbers for continuous exposure at 0.5 m, not general caps. See the corrected table below.

**Fix.** Use per-species, time-averaged hazard indices matched to the use pattern. Treat D_t and r_face as uncertain inputs. Present caps as functions of (capture, distance, hours).

### 10. Major: "validated simulator" overstates what has been validated for this claim

**Evidence.**
- No test in `validation.json` covers the UV/visible ratio, VUV line output, O₃ yield, or anything at the µJ scale.
- V17 passes only on the all-band share: 25.1 %, of which about 90 % is EUV + VUV, absorbed within 0.02–0.2 mm of air. The > 200 nm share is **2.2 %**, against Phuoc's 22–34 %. RT2 asked for the definition of Phuoc's quantity to be matched before comparison (must-fix 10); it has not been.
- V18 now fails at 1 µs (30.8 vs 51.5 kK).
- V20 passes inside a 100×-wide band.

**Effect.** "A new result from its validated spark simulator" should read "a model result, unvalidated for spectra and chemistry".

**Fix.** The earliest discriminating tests are X1 (a calibrated 180–900 nm spectrum per absorbed J), the Borghese & Merola continuum, and the Cook 2000 simulation (Finding 7).

### 11. Major: several RT2 must-fix items remain open, and three of them bear directly on T4

| RT2 must-fix | Status in `spark/*.py` | Bearing on T4 |
|---|---|---|
| 1. Chemistry initial condition and clamp | **Fixed**: LTE start at 7 kK, no clamp, atom third-body efficiency ×5, smooth R3, high-T O₃ decomposition. Open: NO⁺/N(²D), N₂O, shock-tube benchmark, rate sweep. | Thermal NO ±×3 remains |
| 2. VUV lines, Voigt escape, absorber-resolved photolysis | Lines **done** (9 lines, memory data, one Stark width for all). Absorber-resolved spatial photolysis **not done** (EUV ad hoc). Thermal and photolytic parts reported separately: **done**. | **Finding 5** |
| 3. Kirchhoff κ | **Fixed** | — |
| 4. EOS 4+/5+ ions, loud error | **Done** (e_max 1.0×10¹⁰ J/kg, raises). Re-validation of the extension **not done**, yet T4 and E10c use ε ≥ 10⁹, which NOTEBOOK entry 10 says is not claimable. | Finding 3 (V4) |
| 5. Mixing; record lm·s(t) | Mixing **added** (calibration point; V18 now fails at 1 µs). lm·s(t) **not recorded**. | **Finding 4** |
| 6. Conductivity D'Angola; species ξ(λ); ±30 % k / ξ band | **Not done**: K_V still [MEMORY], ξ = 1.5 constant, no sensitivity band. | **Finding 1** |
| 7. Molecular bands; ICNIRP from 180 nm | **Done**, crude (NO δ/ε and O₂ Schumann–Runge missing). Irrelevant to micro-spark UV (< 0.1 % of light below 9 kK). | — |
| 8. f_sedov | Withdrawn from claims; still output. | — |
| 9. Geometry; shell and double-pulse | Cylinder **done**; Noh **done**; shells stall; second-pulse absorption **not modelled**, yet B_3ns sets T4's upper bound. | Finding 6 |
| 10. Publish FAILs; V12; V17 definition; physics tests | FAILs published and V12 is now real (**done**). V17 definition **open**. Arc continuum, sound peak, O₃ (Cook/Petit) and conductivity tests **not done**. | Findings 7, 10 |
| Minor 16, 18, 19, 20 | Metastable edges and the 90 nm probe in the edge gap: open. E_residual = 1.36 E_abs: open. VNR Δt limit: open. Audible truncation and switch guard: open. | Findings 7, 8 |

### 12. Major: calling it a "law" is not justified

**Evidence.** Findings 1, 4, 5 and 6:
- the UV "invariance" is a property of one parameterisation;
- the reactive lock is a post hoc subset;
- nothing has been measured;
- it is contradicted in-model for inefficient and double-pulse formats;
- the only field observation on the O₃ channel (Cook 2000) is a null.

The lab did register P14 after the fact, which is good practice. But a post hoc regularity of a single model is a *hypothesis*.

**Suggested wording.**
> *SPARK per-lumen scaling (model result; hypothesis P14, untested).* In SPARK's LTE air-plasma model, efficient laser sparks (η well above Y_th/Y_ph ≈ 0.01–0.15 lm/W, deposition ≥ 3×10⁸ J/m³) emit their light, actinic UV and VUV together from the same dense 15–40 kK plasma within ~50 ns. So actinic UV per lumen (≈ 2×10⁻³ J_eff per lm·s; model-form range 0.6–4×10⁻³) and photolytic O₃ per lumen (≈ 1–2×10¹⁷ per lm·s; range ×0.3–3) vary much less with spark energy, energy density and focal geometry (±15 % and ±40 %) than light per joule does (×25). Thermal NO adds about (0.2–1.5)×10¹⁶ per absorbed joule, i.e. Y_th/η per lumen. It dominates for inefficient sparks, which are up to 20× dirtier per lumen. Not claimed: non-LTE (fs) micro-plasmas, optically thick sparks, or any value to better than ×3 before X1/X2.

---

## Minor

1. **"30 efficient designs" miscount.** It is 27 completed (A: 21, B_3ns, D: 2, M: 3). The stalled `C_shell_E100uJ_R30um` (act/lm 2.58×10⁻³) is correctly excluded.
2. **Chemistry subsampling weight is biased.** `spark_products` subsamples by cell index with a uniform count weight, while hot-cell masses span 7×10⁻¹⁸ to 9×10⁻¹⁴ kg. On the reference run, forcing max_cells = 40 gives thermal NO **+26 %** (total +19 %). The subsampling is inactive there (57 hot cells < 160), but n_hot is not saved, so no other case can be checked. Fix: sample stratified by mass, or use all cells; save n_hot.
3. **Photon bookkeeping.**
   - Line photons at 102–130 nm are counted in `ph_o2` (physically acceptable: O₂ photodissociates there), but the continuum at 102–130 nm is not.
   - The 90 nm κ probe still sits in the N/O edge gap (RT2 Finding 16), so EUV escape is overestimated for larger kernels.
4. **Starting S(λ) at 180 nm is immaterial.** 180–195 nm is 0.5 % of the dose, and O₂ absorbs it within centimetres of air.
5. **Inconsistent receptor distances.** UV and noise use 0.4 m, the air plume uses 0.5 m, and the venue noise is also at 0.4 m, an unusual audience position. The point-source irradiance for an extended image is conservative by ×2–4.
6. **Mixing runs.** The mixing sink removes enthalpy without heating the entrained air, so the kernel volume change and V16 are wrong in the M runs. It does not affect light (emitted before t_v) or T4.
7. **E_residual.** It is still 1.36× E_abs for the 10 µJ case (RT2 Finding 18). It does not affect T4.

Other checks:
- **O-atom recombination in the absorption shell does not reduce O₃ [RT3].** A 10 µJ spark absorbs about 1.5×10¹⁰ VUV photons within about 0.2 mm, giving [O] ≈ 10¹⁵ cm⁻³ (≈ 40 ppm). The loss rates are:
  - O + O + M: about 60 s⁻¹;
  - O + O₃: about 8 s⁻¹;
  - against O + O₂ + M → O₃ at 7.7×10⁴ s⁻¹.
  The loss is < 0.1 %. Humid air (O(¹D) + H₂O) takes off about 4 %. The next spark's UV photolyses less than 10⁻⁶ of the O₃ cloud.
- **Titration** matters for the hazard metric (Finding 9), not for formation.

---

## (a) Which T4 statements survive

| T4 statement | Verdict |
|---|---|
| Actinic UV per lm·s ≈ 2×10⁻³ J_eff across SPARK designs | **Survives as a model-internal result.** The value is model-form ×0.3–2. The ±13 % is spread, not uncertainty (Finding 1). |
| Reactive per lm·s 1.8–3.7×10¹⁷ for efficient designs | **Survives in-model for η ≥ 0.016 only.** It may be 1.2–2.0×10¹⁷ if EUV products are thermalised; model-form ×0.3–3 (Findings 5–7). |
| "They do not depend on how the spark is made" | **Fails.** Reactive/lm spans 22× across the atlas; UV/lm is flat only inside LTE (Findings 1, 4, 6). |
| η varies 25× (0.016–0.41) | Survives (model; absolute η ×3, per RT2). |
| Mechanism: flat continuum makes UV track visible | **Survives, in a stricter form:** the z = 1 K-U continuum dominates both (93–98 % / 90–100 %). The value depends on χ_g and ξ_UV/ξ_vis. |
| "Line focus changes η ×3, not the spectrum" | Survives (−2 % / +14 %). |
| "O₃ ... their wings escape" | **Partly.** In the emitting phase the lines are nearly thin (β 0.55–1); about 40 % of the O₃ comes from the ad hoc EUV channel. |
| "NO is set by freeze-out of the same kernel" | **Fails for ε ≥ 10⁹**, where 51–67 % of NO is ad hoc EUV photo-NO (26–29 % at ε = 3×10⁸). |
| UV cap Φ ≤ 1.0 lm "whatever the air handling" | **Arithmetic survives for 0.4 m / 8 h continuous only.** It is not a general cap (Finding 2). |
| Air caps as tabulated | **Arithmetic survives.** They are over-conservative 2–3× on the metric, ±×3 on mixing, and apply to continuous exposure only (Finding 9). |
| Iron-Man flux targets | Survive. |
| "The only levers are capture, distance/time, less light" | **Survives for LTE air plasmas**, but distance/time is dismissed in the cap table although it is worth ×50 (Finding 2). |
| "This is why the E10c probabilities fall as they do" | **Fails.** E10c does not lock per-lumen costs, and its outcomes are driven by noise and the tracing lever (Finding 3). |
| P14 "any spark format" band | **Already falsified in-model and ill-posed.** Re-register it (Finding 6). |

## (b) Corrected caps table (maximum continuous visible flux Φ, lm)

Nominal per-lumen values from the 27 efficient atlas cases:
- act/lm 1.9–2.3×10⁻³;
- reactive 1.8–3.7×10¹⁷;
- NO₂ after full titration 0.8–1.6×10¹⁷;
- O₃ untitrated 0.9–2.3×10¹⁷.

Every entry carries a further model-form factor: ×0.42–3.0 on UV caps and ×0.33–3 on air caps.

**UV**

| Scenario | Φ_max (lm) |
|---|---|
| IEC 62471 exempt at 0.2 m | 0.22–0.26 |
| IEC 62471 RG1 at 0.2 m | 0.65–0.79 |
| IEC 62471 RG2 at 0.2 m | 6.5–7.9 |
| T4: 0.4 m, 8 h/day | 0.91–1.10 (**arithmetic confirmed**) |
| 0.4 m, 2 h/day | 3.6–4.4 |
| 1.5 m, 8 h/day | 13–15 |
| 1.5 m, 2 h/day | **51–62** |
| 3 m, 2 h show | **204–247** |

**Air** (breathing-zone model of E5/E10c; 50 m³ room unless stated)

| Scenario | capture 0 | capture 0.6 | capture 0.9 |
|---|---|---|---|
| T4 strict: sum ≤ 13 ppb as NO₂, face 0.5 m, CADR 900 m³/h (arithmetic confirmed) | 0.024–0.049 | 0.060–0.123 | 0.24–0.49 |
| Same geometry, hazard-consistent (NO₂ after titration ≤ 13, O₃ ≤ 20 ppb) | 0.06–0.11 | 0.14–0.28 | 0.55–1.1 |
| Home, continuous use: face 1.5 m, CADR 300, NO₂ ≤ 13, O₃ ≤ 20 | 0.09–0.18 | 0.22–0.45 | 0.89–1.8 |
| Home, 2 h/day: face 1.5 m, CADR 300, NO₂ 1-h ≤ 90, O₃ ≤ 50 ppb [memory limits] | **0.24–0.62** | 0.60–1.5 | 2.4–6.2 |
| Home, 2 h/day, no purifier (0.5 ACH) | 0.07–0.17 | 0.16–0.42 | 0.65–1.7 |
| Venue, 2 h: 500 m³ hall, 3000 m³/h ventilation, viewer 3 m, NO₂ 1-h ≤ 90, O₃ ≤ 50 | **0.84–2.2** | 2.1–5.4 | 8.4–22 |

**Targets under realistic viewing (home 1.5 m / 2 h/day; venue 3 m / 2 h):**

| Target | Flux | UV | Air | Binding constraint |
|---|---|---|---|---|
| Accents | 0.04 lm | passes everywhere | passes everywhere | noise; P(home) 0.13 in V8 |
| Sketch | 0.19 lm | passes (IEC-exempt only marginally, at 0.2 m) | home passes without capture | **noise** |
| Film contrast | 0.45 lm | passes (RG1 at 0.2 m) | home needs ≳ 0–50 % capture; venue passes | noise |
| Film density | 1.5 lm | passes (the T4 "UV cap" does not apply) | home needs ≥ 60 % capture; venue needs ~0–40 % | noise |
| Film exact | 19 lm | passes at ≥ 1.5 m / 2 h (2.7–3.2× margin) | home fails even at 90 % capture; venue marginal at 90 % | **air and noise** |

## (c) What the owner should be told

1. **What the lab found is a useful rule of thumb from its own simulator, not a law of nature.** In its model, the UV and the ozone a spark makes rise in step with the light it makes, so clever spark design cannot make the light much "cleaner". That is plausible physics. But the numbers are uncertain by about 3× either way. They come from an assumed plasma model, not a measurement, and they do not cover every kind of laser spark. Bench tests X1 and X2 decide it.
2. **The "1-lumen UV limit" assumes someone sits 40 cm from the image for 8 hours a day.** At a normal viewing distance (1.5 m, 2 h/day), UV allows about 50 lumens, far more than any Iron-Man image needs. The stricter real-world point is labelling: under the lamp-safety standard's 20 cm test, anything above about 0.25 lm is no longer "exempt" and would need a risk-group label.
3. **What really blocks a home product is noise; fumes near the face come second.** The spark crackle stays above the 35 dB(A) home limit in essentially every scenario tried, even with a silent purifier. "Not feasible at home" stands, but for this reason, not because of the UV/pollution "law".
4. **Venue feasibility is open, not low.** For the 5 m sketch the estimate ranges from about 0 to about 0.6, depending mainly on:
   - whether the untested "subsonic tracing" noise trick works (without it, about 0);
   - how much of the fumes can be captured at the source;
   - viewing distance.
   The earlier 15–23 % figure is one arbitrary point in that range.
5. **Next steps that settle this cheaply:**
   - X1: measure the UV-to-visible ratio of real sparks.
   - X2: measure O₃, NO and NO₂ separately.
   - Demonstrate the noise reduction on the bench.
   - Before any bench work, re-run SPARK against two published datasets it has not been compared with: an absolute UV continuum measurement (Borghese & Merola) and a spark-chemistry measurement that found no ozone (Cook 2000).

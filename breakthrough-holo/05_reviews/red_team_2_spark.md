# Red team 2: the SPARK instrument (plasma physics, radiative transfer, combustion kinetics)

Reviewer roles: computational plasma physicist, radiative-transfer specialist and combustion-kinetics specialist. The brief was to find bugs, physics errors, invalid assumptions and weak validation before the design atlas relies on SPARK.

**State reviewed.** `06_spark_instrument/` as of about 09:30 UTC on 2026-09-30:
- `spark/eos.py`, `radiation.py`, `hydro.py`, `chemistry.py`, `run_spark.py`, `atlas.py`, `val_ns_sparks.py`, `val_convergence.py`
- `validation/validate.py`, `exact_riemann.py`
- `PREDICTIONS.md`, `VALIDATION_DATA.md`, NOTEBOOK entry 9
- Results in `results/`:
  - `val_convergence.json` (ref case only)
  - `val_ns50mJ_r300.json`, `val_ns50mJ_r150.json`, `val_ns200mJ_r300.json` (all three finished during the review)
  - `validation.json` (stale: written before the V08 fix and before any physics run)

**Method.** No hydro runs were made. Every number marked *[RT]* was computed for this review by importing SPARK's own modules and evaluating tables, `rates()`, `integrate_history()`, `Spark._conduction` / `step_isobaric` on fixed kernels, and Cantera. The scripts are in the session scratchpad: `bands.py`, `vuvlines.py`, `condtest.py`, `ksens.py`, `bandint.py`; the rest were one-liners. Numbers marked [memory] are reviewer recollection of literature values and must be checked before use as pass/fail criteria.

**Severity counts:** 4 critical, 10 major, 8 minor.

**Verified correct:**
- Kramers constant C = 6.8×10⁻⁵¹ W m⁻³ Hz⁻¹ m⁶ K^½, which is the SI form of R&L 5.14b and 4π-integrated.
- The Kramers–Unsöld form, including the flat spectrum below χ_g.
- The j_ν → j_λ conversion.
- The line emissivity n·(Σg_uA)·e^(−E_u/kT)/Z·hc/λ.
- All ten forward rate constants and their molecule–cm–s units against the cited evaluations (apart from R3's ×2.5 step, Finding 11).
- K_c = e^(−ΔG°/RT)·c₀^Δn with c₀ at 1 bar in cm⁻³.
- The per-parent-molecule ODE basis.
- The VNR predictor–corrector.
- The acoustic flux ∮p′u dA dt.
- The photopic normalisation.
- The energy reference between the Cantera and Saha branches (Finding 15).

The problems are in what the model leaves out, how the pieces are coupled, and in the validation.

---

## Critical

### 1. Critical: the NO chemistry is dominated by an initial-condition/clamp artefact that produces super-equilibrium NO (up to 10 % NO; the equilibrium ceiling is 5.1 %)

**Evidence.**
- `chemistry.py:117-119` starts every Lagrangian cell from ambient N₂/O₂ at the first history record.
- `chemistry.py:170` then clamps T at 6000 K. A core cell that was really at 50–240 kK (fully atomised and ionised) is therefore simulated as *ambient air suddenly heated to 6000 K and held there* for as long as it stays above 6000 K. In the model, N₂ dissociation at 6000 K takes milliseconds, so the Zeldovich chain overshoots [RT]:

| Held at 6000 K, 1 atm, from ambient | x_N | x_NO |
|---|---|---|
| 0.1 µs | 6.7×10⁻⁵ | 1.0×10⁻⁴ |
| 1 µs | 1.4×10⁻³ | 1.3×10⁻² |
| 10 µs | 9.1×10⁻³ | **0.114** |
| equilibrium (Cantera) | 0.170 | 7.9×10⁻³ |

The maximum equilibrium x_NO over all T at 1 atm is **5.06 % at 3500 K** [RT]. Model output above that is unphysical.

Frozen NO after a 6000 K hold of length t_hot, followed by exponential cooling with time constant τ [RT, `integrate_history`, P = 1 atm]:

| τ | t_hot | SPARK as coded (ambient start + clamp) | start from equilibrium at 6000 K | start from atomised air at 6000 K |
|---|---|---|---|---|
| 1 µs | 0.3 µs | 2.2×10⁻³ | 8.7×10⁻⁴ | 3.8×10⁻⁴ |
| 1 µs | 3 µs | 7.2×10⁻² | 8.7×10⁻⁴ | 3.8×10⁻⁴ |
| 10 µs | 0.3 µs | 3.3×10⁻² | 7.8×10⁻⁵ | 1.2×10⁻⁴ |
| 10 µs | 3 µs | 1.0×10⁻¹ | 7.8×10⁻⁵ | 1.2×10⁻⁴ |
| 100 µs | 0.3–3 µs | 4.1–4.7×10⁻² | 1.7×10⁻⁵ | 1.8×10⁻⁵ |

The coded procedure gives 2.5× to 2700× more NO than either physically motivated start.

A plausibility check on the reference run (10 µJ, thermal NO = 1.05×10¹¹) supports this:
- The cells with T_max > 6000 K from deposition hold about 10¹² molecules, taking e > e(6000 K) within about 2 r₀.
- If the core alone produced the 1.05×10¹¹ NO, it would need x_NO ≈ 10 %: the overshoot range above, not a physical freeze-out. If shock-heated shell cells contribute instead, they are also passed through the 6000 K clamp starting from ambient air. Either way, the number carries the artefact.

V09 (relaxation to equilibrium at *constant* T over 5 ms) cannot see this, because the overshoot has decayed by then.

**Effect.**
- NO/J (1.1×10¹⁶ micro; 3.4–5.2×10¹⁶ ns) is not a prediction. The artefact alone could shift it by 1–3 orders of magnitude, most likely downward for the atomised core.
- NO₂/J and "reactive per J" inherit the error.
- There is no effect on η or sound.

**Fix.**
1. Integrate only from the time each cell first falls below T_c (8–10 kK). Initialise with the LTE composition at T_c, or with atomised air if recombination is slower than cooling.
2. Extend the mechanism to at least 10 kK so the clamp can go:
   - Park N₂/O₂/NO dissociation with atom third-body efficiencies (×5 for N, O);
   - NO⁺ + e⁻ → N(²D)/N + O;
   - N(²D) + O₂ → NO + O.
3. Add a regression test: NO overshoot in shock-heated air against published shock-tube profiles, and the equilibrium-start cooling benchmark above.

### 2. Critical: VUV lines are dropped as "trapped", but they are not trapped in 10–300 µm kernels. Total radiation, VUV photon counts and photolytic O₃ are underestimated by 1–2+ orders of magnitude.

**Evidence.**
- `radiation.py:10-11` excludes "VUV resonance lines (treated as trapped)".
- Two of the strongest emitters, N I 149.3 nm and N I 174.3 nm, are not resonance lines. Their lower levels are the metastable ²D and ²P.
- For small kernels, even the resonance lines (N I 120.0, O I 130.4 nm) escape through Stark/Voigt wings.

**Estimate [RT, `vuvlines.py`].** Setup:
- Nine lines: N I 120.0/113.4/149.3/174.3; O I 130.4/102.6/115.2; N II 108.5; O II 83.4.
- NIST-level gA (±50 %), LTE populations from SPARK's own `composition()`.
- Voigt profile (Doppler plus Stark 0.002 nm × n_e/10²³ m⁻³), uniform-sphere escape probability integrated over the profile.

| T (1 atm) | kernel radius | escaping VUV-line power / SPARK's **entire** emission | 130–200 nm photon rate / SPARK `ph_o2` |
|---|---|---|---|
| 12 kK | 10 / 100 / 300 µm | ×7.4 / ×2.4 / ×1.3 | ×460 / ×155 / ×85 |
| 15 kK | 10 / 100 / 300 µm | ×7.0 / ×2.8 / ×1.6 | ×133 / ×68 / ×40 |
| 20 kK | 10 / 100 / 300 µm | ×17 / ×7.4 / ×4.6 | ×27 / ×25 / ×21 |

SPARK's optically thin total at 15 kK is 8.8×10⁹ W m⁻³, or 7×10⁸ W m⁻³ sr⁻¹. The Naghizadeh-Kashani/Cressault NEC at R → 0 is about 10¹⁰ W m⁻³ sr⁻¹ [memory]; SPARK is 10–40× below it for the same reason.

**Effect.**
- Radiated fraction: for micro-sparks f_rad would go from 0.5 % to about 2–6 %. P3 (< 10 %) probably survives, but the kernel cools a little faster (η slightly lower, ≤ 10 %). For ns sparks this is part of the V17a failure (Finding 4).
- O₃/J: photolytic O₃ is 95 % (micro) to 99.9 % (200 mJ) of SPARK's O₃, and it scales with `ph_o2`. So O₃/J (2.6×10¹⁵ micro) is low by roughly ×20–400, bounded above by 2 O₃ per escaping 130–200 nm photon. It could exceed NO/J. This is the opposite of the "3.5× below budget" reading.
- P7 is untestable until this is fixed.

**Fix.**
- Add these lines with Voigt escape per cell, using real Stark widths (Griem/Konjević tables) and the local n_e.
- Book the escaping photons as absorbed in the first ~0.1–5 mm of cold air: O₂ σ(130–175 nm) ≈ 10⁻²²–1.5×10⁻²¹ m².
- Re-derive `ph_o2`.

### 3. Critical: late kernel cooling is 1D conduction only. The ns validation kernels stay 2–4× too hot at 20 µs, and the ns-spark η (0.7–2.25 lm/W) and the η ∝ r₀ law rest on that.

**Evidence.** Kernel T_max from finished SPARK runs against measurements (`VALIDATION_DATA.md` §3c):

| Run | 1 µs | 10 µs | 21 µs | Measured |
|---|---|---|---|---|
| 200 mJ, r₀ 300 µm | 35.3 kK | 17.1 kK | **15.0 kK** | Zhang 2019 (200 mJ): 51.5 kK at 1 µs, **6.9 kK at 21 µs** |
| 50 mJ, r₀ 150 µm | 36.5 kK | 15.3 kK | 12.9 kK | Dumitrache (75 mJ): 12 kK at 10 µs |
| 50 mJ, r₀ 300 µm | 17.0 kK | 13.3 kK | 11.6 kK | Glumac (180 mJ): **4.1 kK at 20 µs** |

- V18's own criterion (factor 1.5) **fails** at 21 µs: 15.0/6.9 = 2.18.
- Between 10 and 21 µs SPARK cools by 12 %; the measurements fall about 2× in T.
- The missing mechanisms are the ones experiments report:
  - baroclinic vortex-ring/torus formation (Zhang: torus by ~18 µs) and the cold-air inflow lobe;
  - VUV-line cooling (Finding 2);
  - molecular-band cooling below 10 kK (Finding 9).
- For a 1–2 mm ns kernel, the mixing time R/u (u ≈ 10–50 m/s) is 20–100 µs. The conduction time R²/χ is about 1–3 ms. Mixing should dominate late cooling by ×10–50.
- In the lumen tables, 1 atm air gives 2.7×10¹⁰ lm m⁻³ at 12 kK against 4.6×10⁶ lm m⁻³ at 7 kK, a factor of 5900 [RT]. Almost every lumen-second SPARK accrues after ~10 µs in a ns kernel is therefore absent in the measured kernels.

**Freeze-out sensitivity.** With physical initial conditions, the frozen x_NO changes about 50× as τ goes from 1 to 100 µs (8.7×10⁻⁴ → 1.7×10⁻⁵, Finding 1). A ×3–10 error in the cooling rate therefore moves NO by up to ×3–10.

**Effect.**
- η for ns-class kernels is likely overestimated by about ×2–10, which inflates P5 and P10 at large r₀.
- NO/J is biased by an unknown factor, in either direction.
- Micro-sparks (R ≈ 100 µm, conduction time ≈ 0.4–1 µs) are less affected, *if* the kernel is spherical (Finding 12).

**Fix.**
- Record lm_s(t) and E_rad(t) so the lab can see when the light is emitted.
- Add a calibrated entrainment/mixing sink (e.g. a volumetric exchange rate u_mix/R), or a 2D axisymmetric run, and tune it to V18: Zhang at 21 µs, Glumac at 20 µs. Then re-register P5 and P10.

### 4. Critical: the instrument currently fails its own physics validation, and the passes are weak

On the runs already finished, re-evaluated with `validate.py`'s criteria [RT]:

| Test | Value | Criterion | Status |
|---|---|---|---|
| V17a radiated share > 200 nm (50 mJ) | **1.38 %** (r₀ 300 µm, which `validate.py:172` picks); 2.65 % (r₀ 150 µm) | 11–68 % | **FAIL** (8× and 4× below the lower bound) |
| V17b Sedov share (50 mJ) | 49.1 % | 36–85 % | PASS, uninformative (Finding 6) |
| V18 kernel T at 21 µs (200 mJ) | **15.0 kK** vs 6.9 kK | ×1.5 | **FAIL** (×2.18); 1 µs passes at 0.686 of 51.5 kK, just inside the ×1.5 band |
| V19 NO/J (200 mJ) | 5.2×10¹⁶ | 2.3×10¹⁶–3×10¹⁷ | PASS, for the wrong reasons: **50.2 %** of that NO is the ad-hoc "1 NO per < 102 nm photon" (5.22×10¹⁵ of 1.04×10¹⁶), and the thermal half carries the Finding 1 artefact |
| V20 visible fraction | 7.3 % | 0.1–10 % | PASS inside a 100×-wide band |
| V16 monopole ratio (ref) | **1.85** | 0.67–1.5 | **FAIL**, reported PENDING only because V13/V14 are still running |
| V12 escape thick limit | — | — | hard-coded `True` (`validate.py:149-150`); not a test |
| V08 | 0.35 % (re-run [RT]) | < 3 % | PASS; `validation.json` still records the stale 3438 % FAIL |

**Effect.** No atlas output may be called physics-validated. At present, "20 registered tests" means 15 code or self-consistency checks and 5 weak or failing physics checks (full classification in §Validation).

**Fix.**
- Re-run `validate.py` and publish the FAILs.
- Make V12 compute something, e.g. the β-integrated loss of a uniform sphere against the exact sphere escape probability.
- Define what Phuoc's "radiation share" measures (total, or detector band?) before comparing it with `f_rad_escaping_gt200nm`.

---

## Major

### 5. Major: the EOS stops at charge 3+, and its table ceiling (1.74×10⁹ J kg⁻¹) lies below the energies the atlas deposits

**Evidence.**
- `eos.py:31,64` limits ionisation to 3+; `eos.py:106` sets T_max = 300 kK.
- At ρ₀, the Saha solver puts 65 % of N in N³⁺ at 100 kK and 99 % at 200 kK. The next ionisation energies are 77.5 eV (N³⁺→N⁴⁺), 97.9 eV (N⁴⁺→N⁵⁺) and 77.4 eV (O³⁺→O⁴⁺). A quick Saha estimate gives n(N⁴⁺)/n(N³⁺) ≈ 0.13 at 100 kK, dominant by about 150 kK.
- U(300 kK) is only **1.74×10⁹ J kg⁻¹** at every density [RT]. `FastEOS` (`eos.py:219`) builds its grid to 3×10⁹ J kg⁻¹ and `np.interp` silently clamps: above 1.74×10⁹ J kg⁻¹, T = 300 kK and **P is frozen at 8102 bar**.
- The deposition energy densities used by the atlas ε grid (1×10⁸ to 3×10⁹ J m⁻³, `atlas.py:22`) map as follows at ρ₀ [RT]:

| ε (J m⁻³) | T at ρ₀ | P at ρ₀ | Status |
|---|---|---|---|
| 1×10⁸ | 20.6 kK | 178 bar | fine |
| 3×10⁸ | 45.9 kK | 669 bar | fine |
| 1×10⁹ | 97 kK | 2354 bar | edge of validity |
| 3×10⁹ | e = 2.56×10⁹ J kg⁻¹ | clamped | outside the table |

- In the ε = 3×10⁹ cases, the central 14 % of E sits where dP/de = 0. P there is low by about 33 % against Γ-extrapolation (P/(ρe) = 0.40 at the top of the table).
- The reference case itself (10 µJ, r₀ 10 µm, ε = 1.8×10⁹ J m⁻³) starts at **240 kK**, with **22 % of E above 100 kK** [RT].

**Effect.**
- The 7 ε = 3×10⁹ atlas cases get wrong early pressure, temperature and radiation.
- ε = 1×10⁹ cases and the reference case get a wrong post-expansion entropy, and so a wrong isobaric kernel T, which drives η (Finding 8). Size about 10–30 %; the sign needs a rerun.

**Fix.** Add 4+ and 5+ (and He-like levels) with their levels, extend T to 10⁶ K, and have `FastEOS` raise an error when e > U_max instead of clamping. Until then, drop ε = 3×10⁹ from the atlas.

### 6. Major: the Sedov-fit "blast share" is about 0.5 for any energy-conserving run with real air. f_sedov is an estimator constant, not an energy partition.

**Evidence.**
- `hydro.py:328` fits E = ρ(R/1.0328)⁵/t², with ξ₀ taken for γ = 1.4.
- Real air behind strong shocks and in the kernel has Γ_eff = 1 + P/(ρe) of **1.13–1.19** in the kernel and **1.28** on the Hugoniot at compression 8 (P₁/P₀ = 107, T = 3.9 kK) [RT, `FastEOS`].
- Taylor's Trinity numbers give E(γ = 1.4)/E(γ = 1.2) = 16.8/34 = **0.49** from the same R(t).
- SPARK's four finished runs span 10 µJ to 200 mJ and give f_sedov = **0.522, 0.491, 0.527, 0.498**.
- The γ = 1.4 ideal-gas check (V06, ξ = 1.0356) implies the estimator returns about 1.01 E when γ really is 1.4.

**Effect.**
- P8 ("blast share 50–80 %, ✓ 52 %") and V17b are satisfied by construction and say nothing about partition.
- The physically meaningful numbers are E_ac/E (3.9–5 %) and the residual heat.
- The "shock 51–70 %" literature values may carry the same γ bias. Compare like with like, or not at all.

**Fix.** Calibrate `sedov_energy()` once on an ideal γ = 1.4 blast with counterpressure (IdealEOS, cheap) and once with the real EOS. Report E_fit/E_fit,ideal and never call it the "blast share".

### 7. Major (bug): Kirchhoff absorption carries an extra (1 − e^(−hν/kT))⁻¹ factor

**Evidence.**
- `radiation.py:120` computes κ = j_ν/(4πB_ν)·(1 − e^(−hν/kT))⁻¹.
- For escape, the stimulated-emission-corrected κ′ = j_ν/(4πB_ν) is the right quantity. The code returns the uncorrected κ, which is too large by the factor below [RT]:

| T | 550 nm | 900 nm |
|---|---|---|
| 10 kK | ×1.08 | ×1.25 |
| 15 kK | ×1.21 | ×1.52 |
| 20 kK | ×1.37 | ×1.81 |
| 50 kK | ×2.46 | — |
| 100 kK | ×4.4 | — |
| 240 kK | ×9.7 | — |

- ns kernel at ρ₀ and 50 kK, R = 300 µm: τ₅₅₀ = 3.7 (code) against 1.5 (correct), so β = 0.27 against 0.52. The early visible escape is **1.9× too low**.
- Micro kernel at 100 kK, 10 µm: β = 0.80 against 0.95.

**Effect.** η is biased low in the thick early phase: under 5 % for micro-sparks, up to about 2× in that phase for ns sparks. The same error affects the UV-A/IR bands.

**Fix.** Delete the factor. The fix is one line.

### 8. Major: η is effectively linear in two unvalidated inputs, the Biberman factor XI and the conductivity table K_V, and the conductivity has no pressure dependence

**Evidence.**
- At 12–15 kK (1 atm), the phase where micro-spark light is made, **96–97 % of lumens are continuum** [RT]:

| T (1 atm) | Continuum share of lumens | Main contributors |
|---|---|---|
| 12–15 kK | 96–97 % | continuum |
| 20 kK | 86 % | continuum |
| 30 kK | 28 % | N II 567.9 and 500.5 nm lines dominate |

- In the continuum at 550 nm (12 kK), 92 % of the bracket [1 + XI(e^(hν/kT) − 1)] comes from XI = 1.5 (`radiation.py:29`). XI is one number used for N, O, molecular ions and all charge states. Measured Biberman factors for N and O in the visible are roughly 1.0–1.6 [memory].
- In the isobaric phase, lumen-seconds scale **exactly as 1/k** [RT, `ksens.py`, Gaussian kernels peaking at 15 and 20 kK, R = 100 µm]:
  - k × 0.5 → lm·s × 2.00;
  - k × 2 → lm·s × 0.50;
  - same ratios for actinic UV.
- K_V (`radiation.py:204`) is typed "[MEMORY, to be checked]", and VALIDATION_DATA did not retrieve D'Angola. Its shape is plausible:
  - O₂ dissociation peak ≈ 0.65 at 3.8 kK;
  - N₂ dissociation peak 2.3 at 7 kK;
  - minimum 1.0 at 10 kK;
  - ionisation peak 3.2 at 15 kK.
  
  But each value is uncertain by ±30–50 % [memory]. K_V is 1 atm only. At fixed T, the electron contribution scales as x_e ∝ p^(−½) and the reactive peaks shift upward by about 15–25 % in T per decade of pressure. This matters during the first µs at 10–1000 atm, and little in the 1-atm isobaric phase.

**Effect.** η ±2× from these two inputs alone. There is no effect on NO beyond cooling time.

**Fix.**
- Replace K_V with the D'Angola 2008 λ(T, p) fits.
- Take XI per species and charge from published Biberman-factor tables.
- Carry a ±30 % k and XI ∈ [1.0, 2.0] sensitivity band on every atlas η.
- Add a physics test: absolute visible continuum of 1 atm air at 9–15 kK from wall-stabilised arc measurements.

### 9. Major: missing molecular bands. Lumens +9 % to ×14 and actinic UV +42 % to ×130, depending on kernel peak temperature.

**Evidence.**
- `radiation.py:10` omits N₂ 1+, N₂ 2+, N₂⁺ 1−, NO γ/β/δ/ε and O₂ Schumann–Runge.
- SPARK's emission in 1 atm air is tiny below 8 kK: 7×10⁻⁴ W m⁻³ at 3 kK, 5.8 at 4 kK, 674 at 5 kK.
- A crude LTE band-system estimate (T_e, g, Qvr, effective A, representative λ; ±3×) [RT, `bands.py`] exceeds SPARK's table as follows:

| T | lumens: bands / SPARK | actinic UV: bands / SPARK |
|---|---|---|
| 4 kK | ×81 | ×2.6×10⁴ |
| 5 kK | ×48 | ×2×10³ |
| 6 kK | ×35 | ×340 |
| 7 kK | ×16 | ×64 |
| 8 kK | ×1.8 | ×5 |
| 10 kK | 0.017 | 0.042 |

  The lumen excess comes from N₂ 1+ at 580–690 nm; the actinic excess mainly from NO γ/δ/ε at 200–260 nm and N₂ 2+.
- Integrated over an isobaric Gaussian kernel cooling from its peak [RT, `bandint.py`]:

| Kernel | Lumens | Actinic |
|---|---|---|
| peak 15 kK, R 100 µm | +9 % | +42 % |
| peak 12 kK, R 100 µm | +95 % | +540 % |
| peak 9 kK, R 1 mm | ×14.8 | ×128 |

**Effect.**
- Actinic dose (`act_per_J`) is underestimated for all kernels.
- η is underestimated for weak or large kernels whose isobaric peak is ≲ 12 kK.
- Colour (the N₂ 1+ red/orange, N₂⁺ 391/428 nm) is wrong late.

**Fix.** Add LTE band-model emissivities, e.g. from Laux's SPECAIR-type Einstein coefficients, over 3–15 kK. Also add the ICNIRP S(λ) from 180 nm (Finding 21).

### 10. Major: photochemistry yields are ad hoc, and they dominate O₃ and up to half of NO

**Evidence.**
- `chemistry.py:175-176` assigns 2 O₃ per 130–200 nm photon and "1 NO + 1.5 O₃" per < 102 nm photon, regardless of absorber.
- A < 102 nm photon absorbed by O₂ ionises it: O₂⁺ + e → 2 O gives 2 O₃ and 0 NO. One absorbed by N₂ (80–100 nm) predissociates: N(⁴S) + N(²D) → up to 2 NO + 2 O.
- Photolytic share of the outputs:

| Run | Photolytic share of O₃ | Photolytic share of NO |
|---|---|---|
| 10 µJ | 95 % | 8.6 % |
| 50 mJ, r₀ 300 µm | 99.5 % | 26 % |
| 50 mJ, r₀ 150 µm | 99.8 % | 45 % |
| 200 mJ | 99.9 % | **50 %** |

- Photo-O₃ is simply added. The code does not:
  - titrate it against the thermal NO (NO + O₃ → NO₂);
  - account for photons absorbed in the hot, NO-rich shocked shell, where O₃ decomposes and O + NO + M → NO₂;
  - include O(¹D) + H₂O (humid room air).

**Effect.** O₃/J and ~10–50 % of NO/J are unmodelled assumptions, not outputs. Finding 2 moves the photon count itself by 1–2 orders.

**Fix.** Tie the yields to the absorber from the N₂/O₂ cross sections (per-wavelength branching), deposit the photons in a spatial absorption shell, and run the photolysis products through `integrate_history` with the local NO. Report the thermal and photolytic parts separately in every result.

### 11. Major: recombination kinetics and third-body treatment are too crude for freeze-out out of atomised air

**Evidence [RT].**
- O₂ dissociation implied by R3 (detailed balance) is **5.5× slower than Park** at 4–8 kK, for molecular M.
- The ×2.5 step at T = 1000 K (`chemistry.py:73`) is discontinuous and points the wrong way: at 300 K, GRI's 1.1×10⁻³³ is already about 2.5× *below* measured O + O + N₂ [memory].
- All third-body efficiencies are 1 (`chemistry.py:101`). For an atomised kernel, Park's ×5 for N and O as M matters most. The table above shows that O₂ re-formation, which the second Zeldovich step N + O₂ → NO + O needs, controls the freeze-out.
- The N₂ dissociation rate is fine (×0.7–2 of Park).
- The R1 reverse, N + NO → N₂ + O via detailed balance, gives 1.4×10⁻¹¹ at 300 K (JPL 2.9×10⁻¹¹) and 5.5–5.8×10⁻¹¹ at 2–3 kK (Baulch 3.5×10⁻¹¹).
- O₃ thermal decomposition, as the reverse of JPL R6 with (T/300)^(−2.4) extrapolated well beyond its 200–300 K range, is about ×2 slow at 1000 K and ×9 slow at 2000 K against a Baulch-type 7×10⁻¹⁰ e^(−11400/T) [memory]. O₃ in warm cells therefore survives too long.
- Missing: N(²D) chemistry, NO⁺/e⁻, and N₂O (O + N₂ + M; N₂O + O → 2NO).

**Effect.** Even with Finding 1 fixed, the freeze-out x_NO from atomised air carries a ×3–10 kinetic uncertainty.

**Fix.** Adopt a vetted high-temperature air mechanism (Park 1990/1993 plus Kossyi for low T), smooth in T, with species-specific efficiencies. Run a sensitivity sweep over the five controlling rates.

### 12. Major: 1D spherical geometry versus real laser foci. Micro-spark η is likely overestimated by ×1.2–3.

**Evidence.**
- The deposition volume of a focused beam is prolate, with aspect ratio about 1/NA, and longer above threshold (moving breakdown).
- The atlas's smallest kernels (r₀ = 3.9 µm for 1 µJ at 3×10⁹ J m⁻³) are near the diffraction limit, so they are certainly not spherical.
- The lowest diffusive mode of a long cylinder, against an equal-volume sphere, gives τ_cyl/τ_sph = 1.71·A^(−2/3):
  - 0.82 at aspect 3;
  - 0.58 at aspect 5;
  - 0.37 at aspect 10;
  - 0.28 at aspect 15.
- η ∝ τ in the conduction phase (Finding 8), and the expansion phase is cylindrical rather than spherical.

**Effect.**
- η: ×0.3–0.8 at aspect 3–15.
- NO/J: cooling-rate dependent, unknown sign.
- Sound: the source is directional.

**Fix.** Run at least a cylindrical (planar-radial) variant with `geometry` extended, or a 2D-axisymmetric check at one point. Make aspect ratio an atlas axis.

### 13. Major: the shell-implosion (C) and double-pulse (B) atlas cases are outside the verified envelope

**Evidence.**
- C cases:
  - Converging shocks with scalar VNR q in a 1D Lagrangian code show the known wall-heating and centre-resolution errors.
  - The Guderley centre temperature is formally singular, so peak T and hence η are grid-dependent.
  - No Noh or Guderley test exists.
  - The ρ table is capped at 30 kg m⁻³ (`eos.py:107`, clip in `_rho_idx`). A reflected converging shock in Γ ≈ 1.2 air exceeds this, so pressure is evaluated at the wrong density.
  - A spherical implosion is 3D-unstable (RT/RM) and in practice asymmetric.
- B cases: the second pulse is deposited with 100 % efficiency into the original Lagrangian mass (`hydro.py:58-63`). In reality, inverse-bremsstrahlung absorption (∝ n_e²) in the rarefied kernel at 3–300 ns delay is much smaller, and it is placed in the dense shell.

**Effect.** P13 (> 3×) and P9/P12 would be tested against model assumptions, not physics.

**Fix.**
- Add a Noh test (spherical, γ = 5/3; analytic post-shock density 64).
- Run the C cases at 2 and 4 resolutions and report the spread.
- Model the second-pulse absorption (at least inverse bremsstrahlung along a ray), or restate B results as "per absorbed J, absorption assumed".

### 14. Major: LTE and instantaneous isochoric deposition are untested assumptions that set the post-expansion state

**Evidence.**
- Electron–ion energy equilibration at n_e = 10²⁶ m⁻³ and T_e = 10 eV takes about 0.3 ns (10× longer at 10²⁵ m⁻³). The hydro time r₀/c_s is about 1 ns for r₀ = 10 µm.
- The first ns, which sets the kernel entropy and so the isobaric T that makes the light, is therefore two-temperature and ionisation-non-equilibrium for fs/ps deposition.
- The only fs data in VALIDATION_DATA show T_e = 0.5–1 eV with n_e = 4×10²¹ m⁻³: a weakly ionised, non-thermal plasma whose light is the N₂ 2+ / N₂⁺ 1− bands, not an LTE continuum.
- In the later µs phase at n_e ≈ 10²³ m⁻³, McWhirter holds for visible transitions (~5×10²¹ needed) but is marginal for 10 eV VUV transitions (~2×10²³).

**Effect.** The atlas axes (E_abs, ε, r₀ of an instantaneous LTE Gaussian) are not laser parameters. The mapping to real µJ fs/ps foci (absorption fraction, shape, non-LTE) is unmodelled, and η could differ in either direction.

**Fix.** State this in every atlas output. Add a two-temperature phase, or at least bound the result with an ε at the isobaric-entropy-equivalent state.

---

## Minor

### 15. Minor: EOS energy reference is consistent; edges and species are minor

**Energy reference.** The Cantera − Saha offset at 16 kK, as a fraction of e [RT]:

| ρ (kg m⁻³) | Offset |
|---|---|
| 10⁻⁴ | −0.04 % |
| 10⁻³ | 0.08 % |
| 10⁻² | 0.28 % |
| 0.1 | 0.47 % |
| 1.2 | 0.31 % |

The references agree (H0_ATOM equals ΔH_f(298) − [H(298) − H(0)], which is correct). At the edges:
- ρ = 30: **−7.3 %** in u and a 6 % P mismatch, because Cantera keeps molecules at 16 kK while Saha has none; the offset is then carried to all T > 18 kK.
- ρ = 10⁻⁵: n_e mismatch 5.5 % at 18 kK, because Cantera lacks N²⁺ (7 % in Saha).

V02 (`validate.py:51`) tests only ρ = 0.01–10 and so misses both.

**Missing species and corrections:**
- Debye lowering: about +4 % n_e at 1 atm and 15 kK; Saha ratio ×1.35 at ρ₀ and 50–100 kK.
- Ar: about 1 %.
- H₂O at 1–1.5 % in room air: Hα is only 1–2 % of lumens at 10–15 kK [RT estimate], but HOx changes the NO₂/HNO₃/O₃ partition on ms–s timescales.

Doubly charged ions below 16 kK are < 10⁻⁴ for ρ ≥ 10⁻³.

**Fix:** extend V02 to the table edges; compute the offset per T in the blend region.

### 16. Minor: VUV metastable edges are missing (the docstring says they are included); the EUV probe sits in an edge gap

- `radiation.py:7` promises "ground/metastable" edges, but `radiation.py:99-104` implements ground edges only.
- Against a cross-section-based estimate [RT], the missing N ²D/²P and O ¹D/¹S edges leave the 102–200 nm band **2–27× low**. EUV (< 102 nm) is fine (SPARK 1.5× low; κ at 80 nm 668 vs 534 m⁻¹ at 10 kK).
- The 90 nm probe (`radiation.py:34`) sits between the O (91.0 nm) and N (85.3 nm) edges: κ₉₀ = 51 against κ₈₀ = 668 m⁻¹. EUV escape is therefore overestimated for thick kernels.
- All EUV is absorbed within about 10–40 µm of cold air (σ ≈ 2×10⁻²¹ m²). It is local heating, not a loss. In the ns runs, 58–74 % of `f_rad` (3.9–13.8 %) is EUV plus VUV.

### 17. Minor: harmonic-mean face conductivity is accurate for smooth profiles only

`hydro.py:143`. On an isobaric 12 kK / 100 µm kernel [RT, `condtest.py`], compared with a Kirchhoff-transform flux (S = ∫k dT):

| Profile | Lumen-seconds error with harmonic mean |
|---|---|
| Gaussian, 8–64 cells | 1.4 % → 0.03 % |
| exp(−(r/R)⁶), 8–64 cells | 5.5 % → 0.2 % |
| top-hat, 5 / 10 / 20 / 40 / 80 / 160 cells | ×7.8 / 4.7 / 3.0 / 2.1 / 1.5 / 1.2 too high |

The Gaussian atlas default is safe. The `profile="flat"` option and steep shell edges are not. V08 uses constant k and cannot detect this.

**Fix:** use the Kirchhoff transform (a few lines).

### 18. Minor: energy bookkeeping after the isobaric switch is not audited

- `E_residual` (`hydro.py:365`) is **1.36, 1.24, 1.16, 1.10 × E_abs** in the four finished runs.
- The cause is the switch remapping acoustic-wave cells from (ρ, e) to T at P₀. That error is first-order in p′: ±852 J kg⁻¹ per ±1 kPa [RT]. Ambient round-off contributes only 1 %.
- `energy_drift_phase1` is always NaN in real runs (`run_spark.py:29-31`), and phase 2 has no closure check.

**Fix:** audit Σm·Δh + E_rad,phase2 over cells inside r_probe, and drop or redefine E_residual.

### 19. Minor: the VNR viscosity time-step limit is not enforced

`hydro.py:201,203`. With quadratic q (c₂ = 2), explicit stability in strong compression needs Δt ≲ Δr/(8|Δu|). CFL 0.3 on c_s + |Δu| allows 0.3 Δr/|Δu|, 2.4× larger. It is stable in the V06 Sedov test, but not guaranteed for implosions (Finding 13).

**Fix:** use c_s + 4|Δu| in the CFL denominator.

### 20. Minor: acoustic details

- `audible()` (`hydro.py:349`) zeroes everything outside 0.9–22.4 kHz. This is harmless for micro-sparks but truncates ns-spark spectra.
- The outer boundary (`hydro.py:210`) is a pressure-release surface, which reflects the wave inverted. It is safe only because the switch happens before the wave arrives (13 µs against about 54 µs for 10 µJ). Add a guard that the switch time is earlier than R_out/c₀.
- The switch requires global |u| < 5 m s⁻¹ (`hydro.py:258`), which is set by far-field wave amplitude rather than the kernel.
- V16: the simulated 2–15 kHz amplitude is **1.85×** (ref) and 1.48–1.56× (ns) the monopole law's prediction. `display_budget.heat_release_band_p2` also uses an ideal-γ dV that is 1.39× SPARK's `dV_hot` for 10 µJ. Combined, display_budget's 2–15 kHz level is about 2.5 dB below SPARK's waveform for micro-sparks (1.85/1.39 = 1.33 in amplitude).
- No test compares peak overpressure with the data already in VALIDATION_DATA §6 (Qin & Attenborough: 22.7 kPa at 3 cm for 800 mJ; Brode fit).

### 21. Minor: actinic function and continuum completeness

- ICNIRP S(λ) is set to 0 below 200 nm (`radiation.py:65`). It is defined from 180 nm, and 180–200 nm photons travel more than 10 cm in air.
- e-neutral bremsstrahlung and O⁻ photodetachment are missing. At 10 kK, O⁻ alone adds about 10 % to κ₅₅₀ [RT estimate], and these continua dominate below about 8 kK. The effect on η is small (Finding 8: the light is made above 10 kK).

### 22. Minor: chemistry numerics

- n_tot = P/(k·T_clamped) (`chemistry.py:133`) overstates the density ×T/6000 while T > 6000 K.
- The T history is recorded only every 40 hydro steps, which can under-sample brief shock heating.
- The 1 ms linear quench to 300 K has no dilution. NO + O₃ → NO₂ runs at kernel concentrations (τ ≈ 0.2 ms at x_NO ≈ 1 %). NO₂/O₃ partitions are therefore not predictive, although total NO is conserved.

---

## Validation adequacy

| Class | Tests | What they establish |
|---|---|---|
| Code correctness against analytic or definitional results | V01, V03, V05, V06, V07, V08, V10, V11, V13, V14, V15 | The solver implements its equations. V10 checks the rate constant against itself. |
| Model self-consistency, model against model | V02 (Cantera against own Saha), V04 (table against Cantera, on the Cantera branch, so 0.00 %), V09 (kinetics against Cantera equilibrium at constant T), V16 (SPARK against display_budget's noise law) | Internal agreement, not physics. |
| Not a test | V12 (hard-coded True) | Nothing. |
| Physics | V17a (**FAIL**), V17b (passes by construction, Finding 6), V18 (**FAIL** at 21 µs), V19 (passes with 50 % ad-hoc photo-NO plus the Finding 1 artefact), V20 (100×-wide band) | At present, **no physics output is validated**. |

**Physics claims that have no test at all:**
1. **Luminous efficacy η**: no absolute spectral emission coefficient of air (arc continuum at 9–15 kK, NEC at R = 0.01–1 mm), and no spark lm/W. This is the headline quantity.
2. **Actinic UV per J.**
3. **O₃ per J.** Data exist: Cook 2000 found no detectable O₃ from large sparks; Petit 2010 measured fs-filament O₃.
4. **Anything at µJ scale.** Validation is at 50–200 mJ, and the extrapolation to micro-sparks spans 3.7–5.3 decades in energy.
5. **Thermal conductivity** (memory table) and **XI** (a single number).
6. **Sound level against measurement.** Peak-pressure data are in VALIDATION_DATA §6 but unused.
7. **NO overshoot and freeze-out chemistry** against shock-tube or arc-quench data.
8. **Implosion and double pulse.**
9. **The LTE and instantaneous-deposition initial state.**

**What the lab should not conclude from SPARK in its present state:**
- Any **NO/J, NO₂/J, O₃/J or "reactive per J"** value. That includes "1.4×10¹⁶ /J, 3.5× below the display budget", P6, P7, P11, and V19 as validation. (Findings 1, 2, 10, 11.)
- That **~50 % of the energy goes into the blast** (P8, V17b). f_sedov is an estimator constant. (Finding 6.)
- **η for ns-class or large kernels**, and the **η ∝ r₀ law beyond small r₀** (P5, P10). (Finding 3.)
- **Absolute η for micro-sparks to better than a factor of about 3.** It carries XI and k (±2×), geometry (×0.3–0.8), molecular bands (+10 % to ×14) and LTE uncertainty. (Findings 8, 9, 12, 14.)
- **Actinic UV** beyond "continuum lower bound". (Finding 9.)
- Any result for **ε ≥ 10⁹ J m⁻³** (Finding 5), or for **shell/implosion and double-pulse** cases (Finding 13).
- **Radiated fraction** as agreement or disagreement with Phuoc 2005, until the definition is matched and VUV lines are included. (Findings 2, 4.)

What SPARK *does* support now:
- The hydro and acoustic machinery is correct (Sod, Sedov, closure 0.996).
- Far-field sound is a few % of E (3.9–5 %). A spectral level check against data is still pending.
- Micro-spark radiated fraction is small (< 10 %, P3). This holds with VUV lines added.
- Visible light is made mostly in the 10–20 kK conduction-cooled phase, as continuum.

---

## Must-fix before the atlas

1. **Chemistry initial condition and clamp** (Finding 1): start each cell from LTE or atomised composition when it first falls below 8–10 kK. Extend the mechanism so no clamp is needed (Finding 11: Park rates, atom efficiencies, NO⁺/N(²D)). Add NO-overshoot and cooling-benchmark tests.
2. **VUV lines with Voigt escape** (Finding 2), photolysis tied to the absorber and spatial absorption (Finding 10). Report thermal and photolytic products separately.
3. **Kirchhoff κ bug** (Finding 7): delete the (1 − e^(−hν/kT))⁻¹ factor.
4. **EOS 4+/5+ ions and T range**, and fail loudly on e > U_max (Finding 5). Otherwise drop the ε = 3×10⁹ J m⁻³ cases.
5. **Late-time cooling**: add a mixing/entrainment model calibrated to V18 (Zhang 21 µs, Glumac 20 µs), or restrict η claims to light emitted before t_mix. Record lm_s(t). (Finding 3.)
6. **Conductivity and XI**: D'Angola λ(T, p), species-resolved Biberman factors, and a ±30 % k / XI ∈ [1, 2] sensitivity band on every η. (Finding 8.)
7. **Molecular bands** (N₂ 1+/2+, N₂⁺ 1−, NO γ/β/δ/ε) and ICNIRP from 180 nm, before any actinic claim. (Findings 9, 21.)
8. **Replace f_sedov** with a calibrated estimator, and stop reporting it as the blast share. (Finding 6.)
9. **Geometry**: add an aspect-ratio (cylindrical) sensitivity case. Exclude or flag the shell and double-pulse cases until a Noh test passes and second-pulse absorption is modelled. (Findings 12, 13.)
10. **Re-run `validate.py`** and publish the V16, V17a and V18 FAILs. Make V12 a real test and extend V02 to the table edges. Match the V17 definition to what Phuoc measured. Add physics tests for the arc continuum, sound peak pressure, O₃ (Cook, Petit) and conductivity.

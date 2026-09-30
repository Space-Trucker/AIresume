# Prediction registry: SPARK instrument (committed before any instrument run)

Rule: each prediction is committed to git before the run that tests it. Scores are appended below, never edited above.

| ID | Prediction (before running) | Interval | Basis |
|---|---|---|---|
| P1 | Sedov–Taylor constant ξ₀ for γ = 1.4 reproduced | within 3 % of 1.033 | analytic |
| P2 | ns-class spark (≈ 50 mJ, kernel r₀ ≈ 150 µm): energy partition | shock 40–70 %, radiated 10–40 % | literature 51–70 % / 22–34 % |
| P3 | µJ micro-spark (10 µJ absorbed, r₀ 10–20 µm): radiated fraction | < 10 % | expansion quench faster than radiation |
| P4 | µJ micro-spark luminous efficacy η | 0.01–0.5 lm per absorbed W | T2 / red team band 0.01–1 |
| P5 | At fixed energy density, η rises with kernel size | monotonic over r₀ 10–150 µm | T2 scaling f_rad ∝ r₀ |
| P6 | NO per absorbed J for micro-sparks is lower than for ns sparks | 10¹⁵–5×10¹⁶ /J (vs ~10¹⁷ /J) | faster conductive quench → earlier freeze-out |
| P7 | VUV (< 200 nm) share of radiated energy for hot kernels is large, making O₃ via O₂ photolysis comparable to NO | O₃-from-VUV 10¹⁵–10¹⁷ /J | red team #10 |
| P8 | Blast-wave share for µJ micro-sparks | 50–80 % | literature ns 51–70 %; less radiation → more shock |
| P9 | Double pulse (reheat the expanded kernel at ~1 atm) raises η vs a single pulse of the same total energy | > 1.5× | reheating a larger, isobaric kernel avoids the hydro quench |

## Scores (appended after runs)

## Round 2 predictions (committed before the design-atlas campaign)

| ID | Prediction | Interval | Basis |
|---|---|---|---|
| P10 | At fixed deposition energy density ε = 3×10⁸ J/m³, η is proportional to kernel radius r₀ | η/r₀ = (5.5 ± 2.5)×10³ lm W⁻¹ m⁻¹ | isochoric figure of merit from the SPARK tables (lm·τ_exp/ε, peak at 40–60 kK) |
| P11 | NO per J rises with spark energy (bigger kernels cool more slowly) | 10 µJ ≈ 1×10¹⁶ /J → 1 mJ ≥ 3×10¹⁶ /J | Zeldovich freeze-out vs conduction time r²/χ |
| P12 | Double pulse (5 + 5 µJ, delay 3–300 ns) gives < 1.2× the η of a single 10 µJ pulse (i.e. P9 will FAIL) | η ratio < 1.2 | reheated kernel is at low density; emission ∝ n² |
| P13 | Shell deposition (converging shock, 1D spherical upper bound) raises η > 3× vs the same-energy Gaussian | η ratio > 3 | Guderley implosion compresses and heats the centre |

### Scores, round 1 (appended 2026-09-30 after the first instrument runs)

| ID | Result | Score |
|---|---|---|
| P1 | ξ₀ = 1.0356 vs 1.0328 (0.27 %) | **PASS** |
| P2 | 50 mJ ns spark (r₀ 300 µm): blast 49 % ✓, but radiated 3.9 % (predicted 10–40 %, literature 22–34 %) | **FAIL** (radiation). Candidate missing mechanisms: emission *during* the ns heating (deposition treated as instantaneous), line wings of trapped VUV resonance lines, ions above 3+. A 2022 simulation also gets 2.3 % against the same experiment, so the discrepancy is known in the literature. |
| P3 | 10 µJ micro-spark radiated 0.53 % | **PASS** |
| P4 | η = 0.085 lm/W | **PASS** (inside 0.01–0.5), but carries the P2 caveat |
| P6 | NO 1.1×10¹⁶ /J (µJ) vs 3.4×10¹⁶ /J (50 mJ) | **PASS** |
| P7 | O₃ from VUV/EUV = 2.5×10¹⁵ /J (18 % of all reactive species, not "comparable") | **PARTIAL** |
| P8 | Sedov-fit blast share 52 % (µJ) | **PASS** under the literature definition; the far-field acoustic share is only 3.9 % |

### Scores, round 1b (SPARK v2, after red team 2 fixes)

| ID | v2 result | Score |
|---|---|---|
| P2 | 50 mJ ns spark radiated 25.1 % (literature 22–34 %) | **PASS on v2.** The v1 miss (3.9 %) pointed at the missing mechanism: VUV line wings escaping. The blast-share half of P2 is withdrawn, because the Sedov estimator gives ~0.5 by construction for real-gas Γ (red team 2 #6). |
| P6 | NO: 1.1×10¹⁶ /J (10 µJ) vs 7.4–7.9×10¹⁶ /J (50–200 mJ) | **PASS** |
| P7 | O₃ from VUV/EUV photolysis: 2.0×10¹⁶ /J (10 µJ) and 1.8×10¹⁷ /J (ns), i.e. larger than NO | **PASS** (exceeds "comparable") |
| P8 | withdrawn (estimator artefact) | — |

### Scores, round 2 (atlas, SPARK v2)

| ID | Result | Score |
|---|---|---|
| P5 | η rises monotonically with r₀ at fixed ε for every ε (e.g. ε = 10⁹: 0.034 → 0.052 → 0.081 → 0.12 → 0.18 → 0.27 → 0.39 lm/W for r₀ 5.6 → 56 µm) | **PASS** |
| P9 | Double pulse 5 + 5 µJ: η 0.028 / 0.013 / 0.006 lm/W at 3 / 30 / 300 ns vs 0.038 single (ratio 0.73 / 0.35 / 0.15) | **FAIL**. Mechanism: the reheated kernel is expanded and dilute; emission ∝ n². |
| P10 | η ∝ r₀ holds, but η/r₀ = 1.9–2.25×10³ lm W⁻¹ m⁻¹ at ε = 3×10⁸ (predicted 3–8×10³) | **FAIL** (proportionality ✓, coefficient 2.5× lower). Mechanism: the isochoric figure of merit ignored the energy that escapes as VUV lines and the time spent cooling below the visible-emitting temperature. |
| P11 | NO/J: 10 µJ 4.9–10×10¹⁵; 1 mJ 1.7–4.0×10¹⁶ (≥ 3×10¹⁶ only for ε ≥ 10⁹) | **PARTIAL** |
| P12 | double pulse < 1.2× | **PASS** |
| P13 | Shell (converging-shock) deposition: all 4 runs stalled numerically (dt collapse at the converging shock; stopped by the wall-clock cap at 2.5–107 ns, before most light is emitted). Partial η 0.0027–0.077 vs 0.038–0.087 Gaussian. | **INCONCLUSIVE** (numerics; the Noh test passes for ideal gas but the real-gas shell stalls) |

### New results outside the registered predictions (flagged as post hoc)
- Line focus (cylindrical, matched peak ε and r₀): η ×2.95–3.02 vs sphere, while reactive gases, O₃ and actinic UV **per lumen** are unchanged (ratio 0.98–1.14).
- Mixing on/off does not change micro-spark η (light is emitted in the first ns) and lowers NO by 20–25 %.
- **Lumen-locked pollution law** (T4): actinic UV per lm·s = 1.8–2.3×10⁻³ J_eff and reactive molecules per lm·s = 1.8–3.7×10¹⁷ across all 30 efficient designs. Post hoc, so it is registered now as a prediction for the bench (X1/X2): **P14**. Any spark format measured on the bench will give actinic UV/lm·s within 1–4.6×10⁻³ J_eff and reactive/lm·s within 1–7×10¹⁷.

### P14 corrected after red team 3 (appended; earlier text left as written)
P14 as registered ("any spark format") is **already violated inside SPARK** by its inefficient formats: reactive/lm·s spans 22× and follows Y_ph + Y_th/η. It is re-registered for the bench in a well-posed form. **P14b:** for spark formats with η ≥ 0.05 lm/W, the actinic UV per lm·s measured with a calibrated 180–900 nm spectroradiometer lies within 0.6–4×10⁻³ J_eff, and O₃ plus NO₂ after 10 s of titration lies within 0.4–4×10¹⁷ molecules per lm·s.

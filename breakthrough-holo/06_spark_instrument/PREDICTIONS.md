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

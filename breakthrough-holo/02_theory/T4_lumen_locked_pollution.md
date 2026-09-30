# T4: SPARK per-lumen scaling of UV and reactive gases (a model result, not a law)

**v2, rewritten after red team 3** (`05_reviews/red_team_3_T4.md`), whose two key claims I re-checked myself (NOTEBOOK Entry 12). v1 called this a "lumen-locked pollution law". That overclaimed, and the name is withdrawn.

## What SPARK says (model result, hypothesis P14, untested)

Domain: LTE, instantaneous deposition, optically thin, µJ–mJ sparks, ε = 3×10⁸–3×10⁹ J/m³.

- **Actinic UV per lumen-second ≈ 2×10⁻³ J_eff.** This is a property of SPARK's *continuum emission model*, not something the hydrodynamics discovered.
  - The emission table alone gives act/lm = 1.1–2.2×10⁻³ from 9 to 40 kK over three decades of density (checked).
  - 87–89 % of the actinic dose sits at 240–315 nm, exactly where the model's χ_g = 4 eV cut-off meets the real N I/O I 3s edges.
  - Realistic model-form range: **×0.3–2, i.e. 0.6–4×10⁻³ J_eff/lm·s.** Optically thick or non-LTE plasmas fall outside this domain.
- **Reactive molecules per lumen-second ≈ Y_ph + Y_th/η:**
  - photolytic O₃ (VUV lines, tied to the visible emission);
  - thermal NO (tied to absorbed energy, so worse for inefficient sparks).
  
  Efficient formats give 1.8–3.7×10¹⁷; inefficient ones go up to 4×10¹⁸. **30–54 % of this comes from an ad hoc rule** (1 NO + 1.5 O₃ per EUV photon), which likely overcounts because EUV is absorbed in shock-heated gas. A plausible range is 1.2–3.7×10¹⁷ for efficient formats, ±3× model form.
- **Spark geometry and format move η (laser power, noise), not UV per lumen.** A line focus gives η ×3 at the same per-lumen UV and chemistry. That part is robust within the model, because it compares like with like.

## The light budget depends on the exposure scenario

Nominal per-lumen values. Apply ×0.42–3 on UV and ×0.33–3 on air (model form). Arithmetic confirmed by red team 3. Regulatory limits are partly from memory and must be checked.

**UV:**

| Scenario | Φ_max (lm) |
|---|---|
| IEC 62471 lamp test at 0.2 m: exempt / RG1 / RG2 | 0.22–0.26 / 0.65–0.79 / 6.5–7.9 |
| Viewer at 0.4 m, 8 h/day (T4 v1 case) | 0.9–1.1 |
| Viewer at 1.5 m, 2 h/day | 51–62 |
| Viewer at 3 m, 2 h/day | 204–247 |

**Air** (capture 0 / 0.6 / 0.9):

| Scenario | Φ_max (lm) |
|---|---|
| Strict (all NOx+O₃ as NO₂ ≤ 13 ppb), 50 m³ room | 0.024–0.049 / 0.06–0.12 / 0.24–0.49 |
| Hazard-consistent (NO₂ after titration ≤ 13 ppb; O₃ ≤ 20 ppb) | 0.06–0.11 / 0.14–0.28 / 0.55–1.1 |
| Home, 1.5 m, 2 h/day, 300 m³/h purifier | 0.24–0.62 / 0.60–1.5 / 2.4–6.2 |
| Venue, 3 m, 500 m³ hall, 3000 m³/h | 0.84–2.2 / 2.1–5.4 / 8.4–22 |

**Targets:**

| Target | Flux needed |
|---|---|
| Sparse accents | 0.04 lm |
| Iron-Man sketch (5 m) | 0.19 lm |
| Film contrast (9 m) | 0.45 lm |
| Film density (30 m) | 1.5 lm |
| Film exact (lit lab) | 19 lm |

**Reading.**
- **UV does not bind** at normal viewing distances. It binds only for a lamp-standard classification at 0.2 m, which does matter for certification.
- **Air binds** for anything beyond a sketch in a home-sized room. In a large, well-ventilated venue it allows up to film density and more.
- **Noise binds first** in every home scenario, and is the main uncertainty for venues (below).

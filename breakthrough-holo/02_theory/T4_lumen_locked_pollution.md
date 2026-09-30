# T4: The lumen-locked pollution law (a SPARK instrument result)

**Statement.** For light made by heating room air into a plasma, the actinic UV and the reactive gases produced per unit of *visible light* are nearly fixed by plasma physics. They do not depend on how the spark is made.

| Across 30 efficient SPARK designs (η ≥ 0.016 lm/W; 1 µJ–1 mJ; deposition energy density 3×10⁸–3×10⁹ J/m³; sphere or line focus; mixing on/off) | Value |
|---|---|
| Actinic UV per lumen-second (ICNIRP-weighted) | 1.8–2.3×10⁻³ J_eff, ±13 % |
| Reactive molecules (NO + NO₂ + O₃) per lumen-second | 1.8–3.7×10¹⁷ (~60 % O₃, from VUV photolysis of O₂) |
| Light per absorbed watt, η (for contrast) | varies 25× (0.016–0.41 lm/W) |

Source: `06_spark_instrument/results/atlas/*.json` and the table in NOTEBOOK Entry 11. Diffuse, inefficient sparks (ε = 10⁸ J/m³, η ≤ 0.012) are worse still: 1.4–4×10¹⁸ reactive molecules per lm·s, because they make NO but little light.

## Why (mechanism)

- **UV is locked to visible light** because the hot-plasma continuum (free–free plus merged free–bound) is flat in frequency below a few eV at every temperature that emits visible light. The UV-to-visible ratio is therefore set by spectral shape, not by temperature or density.
  - A line focus changes how *long* the plasma stays dense (η ×3), not its spectrum. The per-lumen ratios match within 2–14 %.
- **O₃ is locked to visible light** because the same hot, dense plasma that emits visible continuum also emits N/O VUV lines. Their wings escape and photolyse O₂.
- **NO** is set by freeze-out of the same kernel. It varies more (±2×) but stays within the band for efficient sparks.

## Consequence: a hard light budget for any air-plasma display

With the user at 0.4 m for 8 h (ICNIRP actinic limit 30 J/m²), a 50 m³ room with 900 m³/h scrubbing, and breathing-zone plume included:

| Limit | Maximum continuous visible flux |
|---|---|
| Actinic UV | **Φ ≤ 1.0 lm**, whatever the air handling |
| Strict air (NO₂-equivalent ≤ 13 ppb), capture 0.3 / 0.6 / 0.9 | Φ ≤ 0.035–0.07 / 0.06–0.13 / 0.24–0.50 lm |
| O₃ ≤ 20 ppb, capture 0.3 / 0.6 / 0.9 | Φ ≤ 0.09–0.18 / 0.15–0.31 / 0.60–1.24 lm |

| Iron Man target (stroke luminance × length) | Flux needed | Verdict |
|---|---|---|
| Sparse accents (3 cd/m², 1 m) | 0.04 lm | inside all caps |
| Iron-Man sketch (3 cd/m², 5 m) | 0.19 lm | needs ≳ 80 % source capture of fumes (red team 1: implausible from a ceiling sink) |
| Film contrast, dim room (4 cd/m², 9 m) | 0.45 lm | needs ~90 % capture and favourable chemistry |
| Film density (4 cd/m², 30 m) | 1.5 lm | **exceeds the UV cap** |
| Film exact, lit lab (50 cd/m², 30 m) | 19 lm | exceeds the UV cap 19× and the air cap 40–500× |

The only levers left are:
- source capture of the fumes (air);
- the user's distance and exposure time (UV);
- showing less light.

Spark engineering (energy, focus, pulse format, geometry) moves η, and so the laser power and noise, but **not** the UV or air cost of the image. This is why the E10c probabilities fall as they do.

## Validity and uncertainty (model-form, red team 2)

- The UV/visible ratio depends on the Biberman factor's wavelength dependence (constant ξ = 1.5 assumed), so ±2×.
- O₃ per lumen depends on the VUV Stark widths (×0.3–3) and the photolysis yield per photon, so ±3×.
- All of this is simulated. Experiment X1 must measure the calibrated 180–900 nm spectrum per absorbed joule, and X2/X7 the O₃ and NO per joule. **The law makes a sharp, falsifiable prediction for those bench measurements:** about 2×10⁻³ J_eff of actinic UV and about 3×10¹⁷ reactive molecules per lumen-second, for any spark format.

# T2: The air-plasma trilemma (light vs chemistry vs noise)

T1 showed that a projector-only, no-medium, all-around, touchable display must make light by ionising the air at each image point. This note derives the budget that governs *any* such display, whoever builds it.

## 1. Per-voxel energy flow

A laser pulse deposits energy E (absorbed) into a micro-kernel of radius r₀ at the focus. That energy then splits into four channels:

| Channel | Fraction | Consequence |
|---|---|---|
| Light (radiation) | f_rad(r₀) | Visible part × luminous efficacy gives lumens |
| Blast wave | f_ac ≈ 0.5–0.8 | Sound (an N-wave of duration T ∝ E^{1/3}) |
| Chemistry | Y ≈ 10¹⁶–1.5×10¹⁷ reactive molecules per J | O₃, NO, NO₂ |
| Residual heat | small | Harmless |

**Why small sparks radiate poorly.** A hot kernel radiates for as long as it stays hot and dense. It stays hot only for the hydrodynamic time r₀/c_s, because expansion quenches it. The fraction radiated is therefore f_rad ≈ x/(1+x), with x ∝ r₀.

- Calibration: ns sparks (r₀ ≈ 150 µm) radiate 22–34 % of absorbed energy and give 0.7–6 lm/W.
- The model reproduces this: **2.1 lm/W at 50 mJ**.
- It predicts **0.1–0.4 lm/W** for 1–100 µJ micro-sparks.
- Cold femtosecond plasma is far worse, at **~10⁻⁵ lm/W**: quenched N₂ bands, mostly UV.

**Upper bound (corrected after red-team #2).** The ceiling comes from the *visible fraction*: ≲ 1–3 % of absorbed energy lands in 400–700 nm (lightning ≲ 1 %). **No air plasma much exceeds ~1–2 lm per absorbed watt.** The σT⁴ argument in v1 was wrong: it is not a cap, because it rises as T⁴.

**Caveat (red-team #3).** No measured lm/W exists for display-sized sparks. The 0.1–0.4 lm/W model value is an extrapolation, and the defensible band is **0.01–1 lm/W**.

## 2. The three caps on absorbed power P

**Chemistry cap** (E5): P ≤ C_lim · Q_eff · N_air / (Y · (1 − capture)).
- The near-field plume at a viewer's face dominates the well-mixed room term.
- With a built-in push–pull capture airflow (90 %) and a 900 m³/h scrubber: **P ≲ 2–3 W** for ≤ 20 ppb at 0.5 m.
- Without capture: P ≲ 0.3 W.

**Noise cap** (E6).
- With random firing order the audible power is ∝ N·E_ac·(f_audio·T)³ ∝ P·E^{2/3}. Useful brightness gives **50–70 dB(A)**, far above the 35 dB(A) home target.
- Drawing strokes in path order is worse by 6–10 dB: a supersonic voxel string builds coherent Mach waves.
- **Listener phase locking (E6/E6b) is fragile.** It works only for a point ear in free field; in a furnished room it gives ≤ 2 dB (Entries 3 and 7).
- **Subsonic multi-channel tracing (E6c) is the real lever.** It gives −20 to −26 dB for long smooth strokes, but only −3 to −8 dB for UI or video content.

**Laser safety** (E7) is not an energy cap at eye-safe wavelengths. At 1550 nm the single-pulse hazard zone is ≤ 16 mm around each focus (conservative IEC-derived MPE), and the average exposure elsewhere is ≤ 10 mW/cm² (limit 100). Safety instead becomes an **active interlock** problem: keep tracked skin and eyes out of the hazard capsules. This blanks only 1–4 % of a hologram around an inserted hand.

**UV cap (added after red-team #13; E7b).** Hot-plasma continuum and the N₂ 296–316 nm bands give an actinic dose at 0.3–0.5 m of 0.1–5× the ICNIRP 8-h limit at ~3 W absorbed. This is a fourth wall of the same order as chemistry.

## 3. The budget, and what it buys

Total light: Φ = η(E) · P ≤ ~0.3 lm/W × ~2–3 W ≈ **0.5–1 lm** (engineered, nominal).

What the film target needs (R4 analysis, E10): dotted 1 mm strokes at 1 mm pitch need I_pt = L × 10⁻⁶ cd per point, so Φ = 4π · L · 10⁻⁶ · n.

| Target | L (cd/m²) | Points n | Φ needed | vs budget |
|---|---|---|---|---|
| Iron Man film, lit lab | 25–180 | 10⁴–10⁵ | 3–230 lm | **5×–400× over** |
| Iron-Man-style, dim lab | 5 | 10⁴ | 0.63 lm | ≈ at the limit |
| Sparse style, dark room | 3 | 3×10³ | 0.11 lm | inside |

## 4. Conclusion of T2

For a pure-air display (the owner's R3 constraint), light output is capped at ~1 lm by indoor air chemistry, even with aggressive built-in air handling. Noise can be engineered down only for tracked listeners.

- **Feasible:** a *dim-room, Iron Man-*style* hologram, i.e. thousands of blue-white glowing points forming wireframes, visible all around, touchable with a glove, with active laser interlocks.
- **Not feasible:** the *film-exact* holograms (bright in a lit room, 10⁴–10⁵ points, cyan/orange colour). They violate the trilemma by one to two orders of magnitude.

**Breaking this needs physics outside the trilemma:** light that does not come from ionising air. By T1 that means a medium, which is outside R3's no-medium constraint. The grey-zone options (projector-supplied particles) are evaluated in T3/E9.

## 5. Post-red-team status

The trilemma is really a *quadrilemma*: light against chemistry, noise and UV, plus Class 4 laser safety. Numbers are in E10b.
- **Home:** P(safe) = 0 at any useful content.
- **Supervised venue, ≤ 55 dB(A):** 0.71 (sparse accents) → 0.36 (5 m sketch) → 0.21 (9 m) → 0.08 (30 m) → 0 (film-exact).

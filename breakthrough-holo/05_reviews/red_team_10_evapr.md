# Red team 10: EVAP-R, the flow-normal lever, the aim contrarian, and the O-band (m24/m25)

*Written 2026-10-05. Target documents: `09_unlock/idea_round_5_opus.md`; `09_unlock/T9_home_routes.md` §2.9 and §3.5; `09_unlock/m24_oband.py` with `results/m24_run.log`; `09_unlock/m25_oband_static.py` with `results/m25_run.log`; `09_unlock/v10_round5_check.py` with its log; `05_reviews/red_team_9_home.md` (C1–C3 framework); `09_unlock/idea_round_4_opus.md` §5; `09_unlock/m23_flowr2.py`, `09_unlock/m23b_rain_law.py`. Supporting code read: `rt6_check.py` (`turb_spectrum`, `synth_turb`, `mote_times`), `m18c_vector_pin.py`.*

**Reproducibility note, stated up front.** The session's safety gate blocked every Bash call after the first few file reads, so `09_unlock/rt10_check.py` was **written but never run**. Every number below is therefore derived by hand from the formula printed beside it, with the arithmetic in the text so it can be checked line by line; `rt10_check.py` reproduces all of it when a later session can run it. This is the same situation idea round 5 §0 disclosed for its own blocked script. **No number here is [MEASURED] from a run of mine.** Web searches used: 0 of 10.

**Tags:** [MEASURED] documented fact with a source · [DERIVED] derived here from the stated formula · [ESTIMATE] order-of-magnitude judgement · [SPECULATIVE] untested.

**Constants used throughout** (20 °C air, pure water): k_a = 0.0257 W/m/K, L_v = 2.46×10⁶ J/kg, D_v = 2.45×10⁻⁵ m²/s, ρ_l = 998 kg/m³, μ = 1.81×10⁻⁵ Pa·s, ν = 1.5×10⁻⁵ m²/s, ρ_a = 1.2 kg/m³, c_p = 1006 J/kg/K, V(520 nm) = 0.71, 683 lm/W, Magnus ρ_s(20 °C) = 17.25 g/m³. Visible Class 1 CW AEL (7 mm, point source) = 0.39 mW; EN 50689 skin through 1 mm at 400–1400 nm = 2000 W/m² × π(0.5 mm)² = **1.571 mW**.

---

## Verdict table

| # | Claim under test | Severity | Ruling |
|---|---|---|---|
| **C1** | EVAP-R "drops vanish 0.5–1.2 m below the injector", "nothing below the image" | **CRITICAL** | **REFUTED as a product.** A 30 pL drop needs **RH ≤ 32 %** at 20 °C to vanish inside 0.5 m. At 50 % RH drops reach a surface 0.5 m below at 21.9 µm (18 % of their mass): **3.2 g/h over 0.04 m² = 79 g/m²/h**; at 70 % RH, 8.5 g/h = **211 g/m²/h** against a surface evaporation capacity of ~270 g/m²/h, i.e. at the edge of pooling. A permanently damp patch under the image at ordinary indoor humidity |
| **C2** | "A low ring of 4–6 heads at 25–30° restores parity"; "faint beam-end sparkle" | **CRITICAL** | **PARITY CONFIRMED, but it buys a visible beam cage.** L_streak/L_image = (p_h/p̄)·Q π w²/(2 H d_s D² θ_eye²) → **0.20 cd/m² at 1 m, 0.82 cd/m² at 0.5 m**, i.e. 1.3–5× a ρ 0.05 wall at 10 lux and 5–23 % of the image's own luminance. **×200 worse than FLOW-R's white motes.** Raising the heads to 60° removes the streaks but puts the per-beam power at 0.77–1.53 mW = **2.0–3.9× the CW Class 1 AEL.** A trilemma with no interior solution for clear drops |
| **C3** | "Built from commodity parts" (pillar 4) for the drop generator | **CRITICAL** | **REFUTED.** 30–45 µm monodisperse at 1.6×10⁵ /s with zero non-volatiles is not a commodity part. Thermal DOD heads (HP45) are designed around 1–10 % humectant: at **1 %** that is 0.18 g/h = **4.3 g/day of non-volatile deposited**. Commodity piezo-mesh atomisers give 4–6 µm: t_L = 44 ms (vanish in 1.1 cm) and ×60 dimmer (≈3 mW/beam). Rayleigh-breakup (VOAG-class) runs on pure water but is lab hardware and needs a 15 m/s jet plus dispersion air |
| **C4** | Round 5 §3.1: "RT9's wake hits are too pessimistic by ×2–3 in σ" | **CRITICAL** (as a general claim) | **CONDITIONAL, not general.** Structurally right that RT9's √(C₀εt)·t/√3 is invalid at Δ ≪ τ_η = 35 ms, and the arithmetic reproduces (19/31 µm). But it holds only at **RT9's own gloved u′ = 0.1 m/s**. At a bare-hand or body plume u′ = 0.3 m/s: ε = 0.34 m²/s³, **τ_η = 6.7 ms ≈ Δ** (the model's own validity test fails), a_rms = 13 m/s² (6.7 after drop-inertia filtering) → bias 77–150 µm → **hits 15–34 % at w 140**. RT9's order of magnitude returns |
| M1 | "New lever: flow normal to the content plane … free" | MAJOR | **NOT FREE.** F(90°)/F(0°) = b/d_s = **0.145** at 0.5 m viewing (0.436 at 1.5 m). Restoring the fill needs n ×2.3–6.9 → 40–119 g/h of water and 11–32 % haze contrast against black, **or** d_s = 3 mm, which triples per-head power and multiplies simultaneous spots ×9 (8 → 72) |
| M2 | "EVAP's bigger drops fix RT9 C2 (×2–4)" | MAJOR | **MISATTRIBUTED.** Required power ∝ 1/(p·capture). EVAP gains ×1.49 on capture (a 15 µm at w 140 vs a 7 µm at w 80) and ×0.93 on p → **×1.6 net, not ×2–4**. The remaining ×2 is "4 heads instead of 2", which FLOW-R can do too |
| M3 | RT9 C2 / round 5 §4 head aggregation ("2–4× at the vertex, 0.4–1.4 % at 100 mm") | MAJOR | **STATIC-ACCOUNTING ARTEFACT, in both routes' favour.** With the scanned-beam time average the recess needed is **37 mm** (FLOW-R desk), **27 mm** (EVAP desk 4 heads), **23 mm** (EVAP room 8 heads) — not 100–300 mm. Opus's "a 7 mm pupil catches 20–35 % at 100 mm" overstates the mean ~10× (8 beams over 40 × 40 mm → **0.19** beams expected). Worst-case scan-stall is 0.105–0.39 mW (FLOW-R) and 15–50 µW (EVAP): ≤ 1.0× and ≤ 0.13× |
| M4 | "All particulate removed (no PM, no residue)" | MAJOR | **OVERSTATED.** At 1 mg/L distilled water each drop leaves one **0.31 µm** nucleus: 17 µg/h → **0.69 µg/m³** (mass: fine) but **2.3×10⁴ /cm³** (number: 2–5× a clean indoor baseline, in the most-penetrating and slowest-depositing size). At 10 mg/L → 6.9 µg/m³; tap water at 250 mg/L → **173 µg/m³** (3.8× the WHO PM10 24 h guideline) |
| M5 | "Faint beam-end sparkle on the floor: use a dark rug" | MAJOR | **NOT FAINT.** 50 µW at 2.2 m past a w 140 focus → 2.57 mm radius, 1 165 lux, **74 cd/m² per instantaneous spot on a ρ 0.2 floor = 49× the image luminance**, as a ~0.9 m sparkle patch per head. Needs ρ ≤ 0.02 over ~2 m. EVAP-R has also deleted FLOW-R's pedestal, which *was* the beam dump |
| M6 | T9 §2.9 m25 verdict: "still needs a ~5 kHz, ~10⁷-mode modulator" | MAJOR | **WRONG ATTRIBUTION.** m25's own PLM 1.44 kHz rows hold; the delay-limited requirement is **D ≤ 6.2 ms → ~400–600 Hz**. What fails is **power**: P/cap = h·\|u\|·I_unit·πw²·prof/(2 P_cap) = 3.2 at w 70 dip, and ≤ 1 only at **w ≤ 39 µm (dip) / 55 µm (Gaussian)**, where the mode count is **2.3×10⁷ per head**. The verdict should name power and mode count, not rate |
| M7 | m25's controller | MAJOR (bias **against**) | The docstring specifies `f_des = -u_est - Kp(x_pred-home) - Ki∫`, but the code is `f_des = -Kp*err - Ki*integ`: **the air feedforward is not implemented.** With it the residual is u̇D, not u, and **LCoS 240 Hz holds at w 70** (σ_x ≈ 30 µm vs the 105 µm threshold). The power verdict is unaffected, so the conclusion survives |
| M8 | m25's loss criterion | MAJOR (bias **for**) | Loss is "distance from the **spot centre** > 1.5 w" and the spot follows x_pred, so a mote dragged **0.7 mm** (LCoS still-room w100 dip, "1/20 lost") to **20.4 mm** (MEMS quiet-office w100 dip, "1/20 lost") from home counts as held. Those rows are display failures and should read FAIL. The rows carrying the verdict (home, dip, w ≥ 70) have home p99 20–37 µm, so the verdict stands |
| M9 | m25's statistics | MAJOR (bias **for**) | 20 motes × 5 s = **10² mote-seconds**, against ~10⁸ for a display. Loss is a rare-gust tail, so 0/20 at 5 s implies only 1.5 w/σ_x ≈ 3; 10⁻⁸ needs ≈ 6–7 → σ_x must be ×2 smaller → D ×1.4 smaller |
| M10 | m25's scope | MAJOR (bias **for**) | One focus, 3 beams. A static display needs 10³–10⁴ foci; at ~300 beams per head in a narrow bundle at w 40 µm the per-head IR aggregate (RT8 C1 / RT9 C2) is **not modelled at all** |
| M11 | Drop lifetime: opus 1.8/2.6/4.5 s vs main session 1.6/2.3/4.0 s | MAJOR | **OPUS IS RIGHT; `v10_round5_check.py` is 13–16 % short.** The sphere balance (Nu = Sh = 2) gives a depression **1/Le = 1.151×** the psychrometric one (Le = 0.869). T_s = 10.06/13.26/16.15 °C, Δρ = 4.24/2.88/1.65 g/m³, **t_L = 1.79/2.64/4.61 s**. T9 §3.5 should read 1.8/2.6/4.6 s |
| M12 | In-jet vapour feedback | MAJOR (room), MINOR (desk) | 17.3 g/h into a 39 m³/h desk core adds 0.44 g/m³ → +8 % lifetime. **Room: 43 g/h into 44 m³/h adds 0.98 g/m³ = 34 % of Δρ at 50 % RH** → +20–25 % lifetime, and the 41 pL room drops **reach the floor above ~64 % RH** |
| M13 | "Treat the reservoir as one does a humidifier's" | MAJOR (engineering) | Accepted as a risk, not a solution. A room-temperature reservoir feeding an aerosol generator is the standard growth-and-dispersal pairing; the drops evaporate to **respirable 0.3 µm nuclei**, so sterility is not optional. Standard mitigations — sealed single-use sterile cartridges or 0.2 µm point-of-use filtration, no standing water between sessions, UV-C or ionic treatment, a documented clean cycle — are available but add a **consumable and a service interval**, i.e. product cost, not a physics blocker |
| M14 | Flow-normal jet geometry | MAJOR | A horizontal jet **sags**: g′ = 5.2×10⁻³ m/s² (cooling minus vapour buoyancy) plus drop settling gives **31 mm over a 0.2 m throw and 69 mm over 0.6 m** = 11–15 % of image height. The seeded slab must be 3–7 cm taller, and drop paths sit 6–10° off horizontal, so near-horizontal strokes are not at θ = 90° after all |
| M15 | "σ_c ≈ 8–15 µm for a 30 µm water drop" | MAJOR | **Only in forward scatter.** At 90°, a 25 mm aperture at 0.5 m under a 100 W/m² 1 ms flood gives ~1 900 e⁻ and a 1.25 mm defocus blur → **σ_c ≈ 29 µm**, which returns the wake to ~35 % (w 80) / 80 % (w 140). Flood opposite each camera (θ 20–40°, p 2.4–8.6) gives ×62–218 photons → σ_c 2–4 µm. Also: the look-ahead must be measured from the **last 1 kHz ROI frame**; from a 200 fps full frame h = 18 ms, bias 123 µm, **15 % at w 140 — exactly RT9's answer** |
| m1–m13 | Minors (satellites, coalescence, ventilation, thermal lag, Mie 90° check, polarisation, haze size, brightness gradient, glove impaction, plume stability, O-band absorption depth, m24 reproduction, Uc/Taylor) | MINOR | §7. Notably: **opus's Mie 90° value is independently confirmed** by geometric optics (Fresnel R̄(45°) = 0.0282 vs Mie 0.035–0.055), and **m24 reproduces exactly** |
| **Overall** | "EVAP-R is the nearest thing yet to the owner's vision" | — | **REJECTED.** EVAP-R needs **five** owner rulings where FLOW-R needs two to three, and it is behind FLOW-R on P. Its one genuine physics advantage is narrow and worth keeping: **it decouples scatterer size from particulate load.** Ranking in §8 |

**Net.** The tetralemma still stands; nothing here reopens it. Of the three round-5 headline claims, one (the dissipative-range aim correction) is structurally right but conditional, one (the flow-normal lever) is real but not free, and one (EVAP-R as the nearest route) is refuted on three independent grounds — humidity-dependent wetting, a visible beam cage, and the absence of a commodity additive-free generator. The O-band work survives, but **m25's verdict names the wrong failure**: the wall is per-focus power and mode count, not modulator rate.

---

## 1. EVAP-R drop physics

### 1.1 The wet-bulb closure: opus is right, the main session's check is 13–16 % short [DERIVED]

Two different closures are in play.

- **Sphere balance** (opus §2.1), correct for a free drop at Re ≈ 0.1 with Nu = Sh = 2:
 k_a(T − T_s) = L_v D_v (ρ_s(T_s) − ρ_v∞) ⟹ (T − T_s) = (L_v D_v/k_a)·Δρ = **2345·Δρ** (Δρ in kg/m³).
- **Psychrometric** (`v10_round5_check.py`): c_p(T − T_w) = L_v(w_s(T_w) − w) ⟹ (T − T_w) = (L_v/(ρ_a c_p))·Δρ = **2029·Δρ**.

The ratio is exactly **1/Le**, with Le = (k_a/(ρ_a c_p))/D_v = (2.129×10⁻⁵)/(2.45×10⁻⁵) = **0.869** → 1/Le = 1.151. The psychrometric constant carries Le^(2/3) from the flat-plate boundary-layer analogy; a sphere at vanishing Re carries Le¹. Applying the psychrometer formula to a free drop therefore **understates the wet-bulb depression by 15 %**, overstates Δρ, and shortens the lifetime.

Solving the sphere balance by hand (Magnus ρ_s, bisection to 0.01 K):

| 20 °C | T_s (sphere) | T_w (psychro.) | Δρ_v (g/m³) | t_L, 30 pL (d₀ 38.6 µm) | Fall at U 0.25 m/s |
|---|---|---|---|---|---|
| RH 30 % | **10.06 °C** | 10.9 °C | **4.240** | **1.79 s** | 0.488 m |
| RH 50 % | **13.26 °C** | 13.8 °C | **2.876** | **2.64 s** | 0.719 m |
| RH 70 % | **16.15 °C** | 16.4 °C | **1.647** | **4.61 s** | 1.255 m |

Worked check at 50 %: p_s(13.26 °C) = 610.94·exp(17.625×13.26/256.30) = 1 521 Pa → ρ_s = 1521/(461.5×286.41) = 11.50 g/m³; Δρ = 11.50 − 8.624 = 2.876 g/m³. d₀ = (6×3×10⁻¹⁴/π)^(1/3) = 3.86×10⁻⁵ m, d₀² = 1.490×10⁻⁹. t_L = ρ_l d₀²/(8 D_v Δρ) = (998×1.490×10⁻⁹)/(8×2.45×10⁻⁵×2.876×10⁻³) = 1.487×10⁻⁶/5.637×10⁻⁷ = **2.64 s**.

**Rulings.** Opus's 1.76/2.60/4.51 s reproduce to ±2 %. **T9 §3.5's "1.6/2.3/4.0 s (main session)" should be withdrawn in favour of 1.8/2.6/4.6 s.** The correction makes every deposition number below ~15 % worse, not better. Opus's T9 §3.3 correction (0.86 s → ~2.6 s for the trehalose drying duct) therefore stands, and the duct is ×3.1 longer, not ×2.7.

Minor refinements, all < 1 %: Stefan-flow log correction ≈ 0.5 %; thermal relaxation to T_s = ρ_w c_w d²/(12 k_a) = **20 ms** (0.8 % of life); ventilation at terminal fall Re = v_s d/ν = 0.11 → f_v = 1 + 0.3 Re^½ Sc^(1/3) = **1.03**; Kelvin effect negligible above 1 µm (the last 0.07 % of life).

### 1.2 Fall, and the deposition that EVAP-R never computes [DERIVED] — CRITICAL

v_s(38.6 µm) = ρ_l g d²/(18 μ) = (998×9.81×1.490×10⁻⁹)/(18×1.81×10⁻⁵) = **4.48 cm/s**. Since v_s ∝ d² ∝ (1 − t/t_L), the mean is v_s0/2 = 2.24 cm/s; opus's "averaging half of that" is right, and the vanish heights above reproduce.

The question opus does not ask is **what arrives at the surface before the drops vanish.** Integrating z(t) = Ut + v_s0(t − t²/2t_L):

| RH | t to reach 0.5 m | d on arrival | mass fraction | deposition (1.6×10⁵ /s) | over the 0.04 m² core | surface can evaporate |
|---|---|---|---|---|---|---|
| 30 % | — (vanishes at 0.488 m) | 0 | 0 | **0** | 0 | — |
| 50 % | 1.788 s | **21.9 µm** | 0.183 | **3.2 g/h** | **79 g/m²/h** | ~450 g/m²/h → damp |
| 70 % | 1.747 s | **30.4 µm** | 0.489 | **8.5 g/h** | **211 g/m²/h** | ~270 g/m²/h → at the edge |
| 80 % | 1.737 s | 33.2 µm | 0.637 | **11.0 g/h** | **275 g/m²/h** | ~160 g/m²/h → **wets out** |

Surface capacity uses E = h_m(ρ_s(20) − ρ_v∞) with h_m ≈ 0.0145 m/s under the 0.25 m/s jet.

**The threshold.** A 0.5 m pendant is dry only if t_L ≤ 0.5/0.2724 = 1.835 s, i.e. Δρ ≥ 1.487×10⁻⁶/(8×2.45×10⁻⁵×1.835) = **4.13 g/m³**, which from the table above is **RH ≤ 32 %** at 20 °C. Opus's own §2.1 table already shows a 0.71 m fall at 50 % RH — i.e. the drops pass the desk — and its mitigation ("set the image within the top ~0.3 m below injection") does not help, because the drops continue below the image and must still finish evaporating in the remaining 0.2 m.

**The 10 pL escape does not close it.** d₀ = 26.75 µm, t_L(50 %) = 1.27 s, fall 0.33 m: dry at 0.5 m. But t_L(70 %) = 2.21 s → 0.577 m, and t_L(80 %) = 3.37 s → 0.879 m. And the brightness cost is severe: required beam power ∝ 1/a², so 10 pL needs **×2.1** the power of 30 pL at the same w. So the EVAP-R operating envelope is:

> **a 30 pL rain needs RH ≤ 32 %; a 10 pL rain needs RH ≤ 60 % and ×2.1 the power; neither is dry at RH ≥ 70 %.**

European indoor RH is typically 40–60 %, and 30–40 % only in winter with heating running. **Ruling: EVAP-R as specified is a winter-only, dry-climate device, and in a normal room it leaves a permanently damp patch under the image.** Opus's hygrometer-plus-two-printheads plan does not reach the needed range; it switches between 0.33 m and 0.72 m of fall, not between wet and dry.

**Room scale is worse** because of §1.3: 41 pL drops with the in-jet feedback vanish at 1.08 m at 50 % RH, 1.96 m at 70 % RH. Dry floor needs t_L ≤ 5.77 s for a 1.6 m drop, i.e. unperturbed Δρ ≥ 2.0 g/m³ → **RH ≤ 64 %**.

### 1.3 In-jet vapour feedback: self-limiting, and it matters at room scale [DERIVED]

The seeded core carries its own evaporated water. Desk: core flow = 0.04 m² × 0.2724 m/s = 0.0109 m³/s = **39.2 m³/h**; 17.3 g/h adds **0.441 g/m³**, which is 15 % of Δρ at 50 % RH. Weighting by the evaporated fraction over a drop's life gives an effective Δρ reduction of ~7.7 % → **t_L and the vanish height +8 %** (0.719 → 0.78 m). Minor.

Room: 0.045 m² × 0.2774 = 0.0125 m³/s = **44.1 m³/h**; 43 g/h adds **0.975 g/m³ = 34 % of Δρ at 50 % RH** → **+20–25 % on t_L**. That is a MAJOR correction to opus §2.7, and it is the mechanism that pushes room drops to the floor at 64 % RH rather than 70 %.

Note the sign: the feedback *lengthens* lifetimes, so it makes the wetting problem worse, never better. It also means the vanish height depends on the seeded fraction of the jet, i.e. on the content being displayed.

### 1.4 Size distribution, satellites, coalescence [DERIVED]

- **Satellites.** A 3 pL satellite (d 17.9 µm) lives t_L = (17.9/38.6)²×2.64 = **0.57 s** (not opus's "≤ 0.3 s") and vanishes within **0.14 m**. Distance is the right conclusion; the time was 2× optimistic. Satellites are **4.6× dimmer** (∝ d²) and are sub-resolution at 0.5 m with a 25 mm aperture (diffraction spot ≈ λz/A = 17 µm at the object), so size cannot be read from the image; they must be classified by **fall speed (0.96 vs 4.48 cm/s)**, which is measurable over a track. Solvable; the controller must do it or brightness scatters ±4.6×.
- **Coalescence is negligible, confirming opus implicitly.** Saffman–Turner K = 1.3(ε/ν)^½(r₁+r₂)³. In-jet ε ≈ U³/D = 0.25³/0.3 = 0.052 m²/s³ → (ε/ν)^½ = 58.9 /s, (2r)³ = 5.75×10⁻¹⁴ m³ → K = **4.4×10⁻¹² m³/s**; rate = K·n = 4.4×10⁻¹²×1.6×10⁷ = **7.0×10⁻⁵ /s**, i.e. 1.8×10⁻⁴ per lifetime. Differential sedimentation with satellites: π(r₁+r₂)²Δv·E = π(28.2 µm)²×0.035×0.05 = 4.4×10⁻¹² m³/s → same order. **No coalescence correction is needed.**
- **Ventilation in the jet.** A Rayleigh-breakup generator delivers drops at ~15 m/s (§1.6): Re = 38.5 → f_v = 2.64, but the stopping distance is v·τ_p = 15×4.54 ms = **68 mm** and the extra evaporation over that ~15 ms is < 1 % of the drop's water. Negligible.

### 1.5 Water quality and residue: small, but number-dominated, and additive-intolerant [DERIVED] — MAJOR/CRITICAL

Residue mass per drop = V·TDS. For 30 pL = 3×10⁻¹¹ L:

| Water | TDS | per drop | nucleus d (ρ 2 g/cm³) | rate | steady c at 25 m³/h | number |
|---|---|---|---|---|---|---|
| 18.2 MΩ DI | 0.03 mg/L | 0.9 fg | 0.10 µm | 0.5 µg/h | 0.02 µg/m³ | 2.3×10⁴ /cm³ |
| good distilled | 1 mg/L | **30 fg** | **0.31 µm** | 17.3 µg/h | **0.69 µg/m³** | **2.3×10⁴ /cm³** |
| poor "distilled" | 10 mg/L | 300 fg | 0.66 µm | 173 µg/h | **6.9 µg/m³** | 2.3×10⁴ /cm³ |
| tap | 250 mg/L | 7.5 pg | 1.93 µm | 4.3 mg/h | **173 µg/m³** | 2.3×10⁴ /cm³ |

**Readings.**
1. "No PM, no residue" is **overstated**. There is exactly one residue nucleus per drop. By mass, good distilled water passes with margin (0.69 µg/m³ against a WHO PM2.5 annual guideline of 5 µg/m³). By **number** it is 2.3×10⁴ /cm³ regardless of purity — 2–5× a clean indoor baseline — and 0.3 µm is both the most filter-penetrating size and the slowest-depositing (v_d ~ 10⁻⁴ m/s, so ventilation is the only sink). The honest claim is "PM mass is negligible with ≤ 1 mg/L water", not "no particulate".
2. **Water purity is a hard spec, not a recommendation.** Tap water fails the WHO PM10 24 h guideline (45 µg/m³) by 3.8×. 10 mg/L already fails PM2.5. The product needs a purity interlock, i.e. a conductivity sensor.
3. **CO₂ pickup by DI water is not a residue problem** — dissolved CO₂ (≈0.63 mg/L at 420 ppm, Henry 3.4×10⁻² M/atm) leaves with the vapour. It is a **pH and materials** problem: pH ≈ 5.6, and DI water is aggressive toward metals and leaches from polymers, which then *does* leave residue. Wetted parts must be PEEK/PTFE/316L or glass.
4. **Additives are fatal to the headline claim.** A 1 % humectant leaves 0.31 ng per drop → a 17.9 µm particle, **0.18 g/h = 4.3 g/day** deposited (these settle at ~1 cm/s, so they land rather than ventilate). At the 10 % typical of inkjet ink it is 43 g/day of glycol film. **EVAP-R is only residue-free if the working fluid is additive-free**, which is exactly what §1.6 says no commodity generator will do.

### 1.6 The generator: EVAP-R's quiet pillar-4 failure [DERIVED + ESTIMATE] — CRITICAL

The requirement is **1.6×10⁵ drops/s of 30–45 µm, monodisperse to ~±10 %, from additive-free water, dispersed over a 0.2 × 0.2 m core at 0.25 m/s.**

| Candidate | Numbers | Verdict |
|---|---|---|
| **Thermal DOD (HP45)**, opus's choice | 300 nozzles × 533 Hz = easy on rate. But designed around 1–10 % humectant and surfactant: pure water has γ = 72 mN/m against the ~35–45 the nozzle plate and refill are designed for, so refill slows and satellites grow; with no humectant the meniscus dries between fires | **Fails the additive-free spec** (§1.5 item 4) |
| **Piezo mesh / ultrasonic** (commodity humidifier, ~$10) | Runs pure water at 0.3 mL/min = 18 g/h: the right water rate. But VMD 4–6 µm, GSD 1.5–2. t_L(5 µm, 50 %) = 998×2.5×10⁻¹¹/5.637×10⁻⁷ = **44 ms** → vanishes in **1.1 cm**; and brightness ∝ d² → **×60 dimmer** → ≈3 mW per beam, 7.7× the CW AEL | **Dead on both lifetime and Class 1** |
| **Piezo DOD dispenser** (MicroFab class) | Runs pure water, 30–60 µm monodisperse, but ~1–10 kHz per nozzle and a handful of nozzles: needs 20–160 nozzles, $5–15k, lab hardware | **Works, not commodity** |
| **Rayleigh-breakup orifice array** (VOAG class) | d_drop = 1.89 d_orifice → 20.4 µm orifice for 38.6 µm drops. Q = 4.8×10⁻⁹ m³/s → v_jet = Q/A = 4.8×10⁻⁹/3.27×10⁻¹⁰ = **14.7 m/s**; drop pitch 92 µm, so wake drafting merges them without dispersion air. Stopping distance 68 mm, so deceleration into the column is fine | **Physically the right answer; home-buildable in principle, commodity no** (lab VOAG $15–25k) |
| Continuous inkjet with charging | Needs an electrolyte for conductivity → residue | **Dead** |

**Ruling.** EVAP-R's medium generator is *less* commodity than FLOW-R's. FLOW-R's HP45 fires a trehalose solution, which is exactly what thermal DOD heads are built for (an aqueous solution with solutes). EVAP-R requires the one thing thermal DOD cannot give — zero non-volatiles. This is a pillar-4 failure that round 5 did not surface, and it is independent of C1 and C2.

### 1.7 Cooling plume: stabilising, not destabilising [DERIVED] — confirms opus, MINOR

Latent sink 11.7 W into 0.044 m³/s × 1.2 × 1005 = 53 W/K gives **−0.22 K**. Net buoyancy combines cooling (heavier) and added vapour (lighter, M 18 vs 29):

Δρ/ρ = ΔT/T − 0.611·Δρ_v/ρ_a = 0.22/293.15 − 0.611×0.441×10⁻³/1.2 = 7.50×10⁻⁴ − 2.25×10⁻⁴ = **+5.25×10⁻⁴** → g′ = **5.15×10⁻³ m/s²**, i.e. the plume is **negatively buoyant**.

- **Downward jet:** U² = 0.0625 + 2×5.15×10⁻³×0.5 → U = **0.264 m/s (+6 %)**. Opus's conclusion is confirmed: the cooling *helps* and does **not** destabilise a push-only jet. The RT9 M5 stall worry (+1 K stalls a column) is the opposite sign and does not apply.
- **Horizontal (flow-normal) jet: it sags.** Over a 0.2 m throw at 0.25 m/s (t = 0.8 s): droop = ½g′t² = 1.6 mm, drop settling = v̄_s t = 17.9 mm → **19.5 mm**. Over a 0.6 m throw (t = 2.4 s): droop 14.8 mm + settling 53.8 mm = **68.6 mm**. That is 10–15 % of image height, so the seeded slab must be 3–7 cm taller (+15–35 % water), and the drop path sits arctan(v_s/U) = **10° off horizontal at injection**, falling to ~6° as the drop shrinks. **So "every in-plane stroke is at θ = 90°" is not achieved**: near-horizontal strokes remain within 6–10° of the flow and keep the long-gap texture.

### 1.8 Glove impaction: opus overstates it ×4, in EVAP's favour [DERIVED] — MINOR

τ_p = ρ_l d²/(18 μ) = 1.490×10⁻⁶/3.258×10⁻⁴ = **4.54 ms**. For a finger of radius 8 mm, St = τ_p U/r = 0.142 — just above the cylinder critical St = 1/8. Langmuir–Blodgett efficiency at St = 0.142 is η ≈ (St − 0.125)/(St + 0.4) ≈ **0.03**, not opus's 10–20 %. For a palm (r 50 mm) St = 0.023 → η ≈ 0. A palm blocking 25 % of a 0.2 m core intercepts 4×10⁴ drops/s; at η 0.03 that is **0.13 g/h**, against opus's 0.4–0.9 g/h. The glove gets slightly damp and self-dries. Opus's conclusion survives with a wider margin.

---

## 2. EVAP-R optics and safety

### 2.1 The Mie claim is confirmed — independently, by geometric optics [DERIVED] — m5

I cannot re-run Mie this session, so I checked opus's table against closed-form geometric optics, which is exact for x = πd/λ = 233.

- **90° (the decisive number).** At θ = 90° neither the 2-ray (refracted, deviation 0–83° for m = 1.335) nor the 3-ray (one internal reflection, 138–180°) reaches; only external reflection does, and for a sphere p(θ) = R̄(θ_i) with θ_i = (180° − θ)/2 = 45° exactly. Fresnel at 45°, m = 1.335: √(m² − sin²45°) = 1.1324, so **R_s = ((0.7071 − 1.1324)/(0.7071 + 1.1324))² = 0.0535**, **R_p = ((1.782×0.7071 − 1.1324)/(1.782×0.7071 + 1.1324))² = 0.00285**, mean **R̄ = 0.0282**. Opus's Mie gives **0.035–0.055** (the excess is surface waves and the diffraction tail). **Agreement to within the expected GO error. The ×14–22 side-scatter deficit stands.**
- **White Lambertian reference.** p = ω(8/3π)[sin α + (π − α)cos α], α = 180° − θ. At 90°: 0.9×0.8488×1.0 = **0.764** ✓ (opus 0.76, m23's 4π self-test 1.0000). At 150°: 0.9×0.8488×(0.5 + 2.618×0.866) = **2.11** ✓.
- **Deficit.** 0.764/0.055 = 13.9× to 0.764/0.035 = 21.8× → **opus's "×14–22 dimmer at 90°" is exact.**
- **Rainbow position.** The geometric primary rainbow for m = 1.335 is at θ ≈ 138°; opus's Mie peaks at 140.8–141.6°. The outward Airy shift for a 38.5 µm drop is a few degrees, so the +3° is the expected diffraction shift, not an error. The smaller-drop values (0.67 at 14 µm vs 0.92 at 38.5 µm) show the expected washout.

**Conclusion: the Mie table in round 5 §2.3 is sound and needs no correction.** (Its *use* is what I contest, below.)

**Polarisation caveat [m6].** R_s/R_p at 45° is **18.8**. Diode lasers are linearly polarised, so the 90° brightness swings ×19 about opus's unpolarised mean, as a function of viewer azimuth relative to the beam's E-field. It matters little in the recommended low ring (whose working angles are 25–52° and 128–150°, where refraction dominates and polarisation is mild) but it is severe in any FLOW-R-style 60°-elevation layout. Mitigation: multimode fibre or a polarisation scrambler, or crossed pairs.

### 2.2 Low-ring parity: confirmed, with a ×2.4 azimuthal ripple at 4 heads [DERIVED]

I reproduced the head-ring sums by hand. For a head at azimuth φ_h and elevation ε seen from the image, and a horizontal viewer at azimuth φ_v, the scattering angle is **cos θ = −cos ε · cos(φ_v − φ_h)**.

4 heads at ε = 30°, viewer at φ_v = 0: heads at 180° → θ = 30° (p ≈ 4.5); at ±90° → θ = 90° (p = 0.039); at 0° → θ = 150° (p = 0.36). Sum/H = 4.94/4 = **1.23** (opus's max 1.29 ✓).
Viewer at φ_v = 45°: two heads at θ = 52.2° (p ≈ 1.0), two at θ = 127.8° (p ≈ 0.10). Sum/H = 2.20/4 = **0.55** (opus's min 0.54 ✓).

So opus's table is internally consistent and the parity claim holds **at the median**: 4 heads at 30° give 0.54/0.95/1.29 against white's flat 0.91. Two caveats:

- **A ×2.4 azimuthal brightness ripple** (0.54 → 1.29) at 4 heads. The image dims by 2.4× as a viewer walks around it. 6 heads at 25° give 1.04/1.17/1.29, ripple **1.24** — flat enough. **The design point must be 6 heads, not 4.** Opus's own table supports this; its headline 4-head/50 µW row does not.
- **Viewer-aware head selection** cannot be relied on to halve the power with more than one viewer at different azimuths: the power must satisfy the worst present viewer, so the saving vanishes with an audience.

### 2.3 Visible Class 1 per head, and the count of lines [DERIVED]

J = L·d_s/(n·d_s²) = 1.5×10⁻³/(1.6×10⁷×10⁻⁶) = **9.4×10⁻⁵ cd** per lit drop (B′: 1.5 cd/m², d_s 1 mm, n 1.6×10⁷). P_int = 4πJ/(683·V·p) = **2.43×10⁻⁶/p** W. P_total = P_int/(1 − e^(−2a²/w²)).

| Design | a | w | capture | p (worst) | P_total | per beam | 8 lines per head | vs 0.39 mW | lines to the AEL |
|---|---|---|---|---|---|---|---|---|---|
| FLOW-R B′ (trehalose) | 7 µm | 80 µm | 0.0152 | 0.504 | 0.317 mW | 158 µW (H 2) | **1.27 mW** | **3.3×** | 2.5 |
| FLOW-R, 6 low heads | 7 µm | 80 µm | 0.0152 | 0.81 | 0.197 mW | 33 µW (H 6) | 0.26 mW | 0.68× | 11.9 |
| **EVAP-R, 4 heads el 30°** | 15 µm | 140 µm | 0.0227 | 0.54 | **0.198 mW** | **50 µW** (H 4) | **0.40 mW** | **1.03×** | **7.8** |
| **EVAP-R, 6 heads el 25°** | 15 µm | 140 µm | 0.0227 | 1.04 | 0.103 mW | **17 µW** (H 6) | 0.137 mW | **0.35×** | 22.7 |
| EVAP-R, 2 heads el 60° | 15 µm | 140 µm | 0.0227 | 0.035 | 3.06 mW | **1.53 mW** (H 2) | 12.2 mW | **3.9× per beam** | 0.26 |

**The count of lines per head.** Desk B′ carries **8 lit drops at once** (n·d_s²·S = 1.6×10⁷×10⁻⁶×0.5 = 8), each lit by every head. So "lines per head" = 8, and the limit is **7.8 lines at 4 heads / w 140**. Opus's headline design therefore sits at **1.03× the AEL at the scan vertex — it does not pass, it is exactly at the limit with no margin.** Six heads at 25° give 0.35× and 22.7 lines of headroom. **Correction to round 5 §2.4/§2.6: the EVAP-R design point must be 6 heads at 25°, 17 µW per beam, not 4 heads at 50 µW.**

**M3: the aggregation should be computed as a scanned beam, which changes RT9 C2 and round 5 §4 in both routes' favour.** Opus treats the head load as a static fan and asks what fraction of the beams a 7 mm pupil intercepts at 100 mm. Two errors:

1. The geometry is 2D, not 1D. Eight beams spread over a 40 × 40 mm patch at 100 mm from the vertex (a 0.2 m image at 0.5 m throw → 0.4 rad fan); a 7 mm pupil covers 38.5/1600 = **2.4 %**, so the expected number of beams caught is **0.19**, not "20–35 % of eight". Opus overstates the mean by ~10×.
2. The beams **scan**, so the governing quantity is the time-averaged power through a 7 mm aperture at the worst accessible position, plus the single-pulse and pulse-train rules, plus the scan-failure case. Time-average = P_head × A_pupil/(Ω_fan s²), so the exit recess needed is

 s ≥ √(A_pupil·P_head/(Ω_fan·AEL)) = √(3.85×10⁻⁵·P_head/(Ω_fan·3.9×10⁻⁴)).

| Case | P_head | fan | **recess** |
|---|---|---|---|
| FLOW-R desk, 2 heads, w 80 | 1.27 mW | 0.333 rad | **37 mm** |
| EVAP-R desk, 4 heads, w 140 | 0.40 mW | 0.333 rad | **21 mm** |
| EVAP-R desk, 6 heads | 0.137 mW | 0.333 rad | 12 mm |
| EVAP-R room, 8 heads (opus §2.7, 81 lit drops × 24 µW) | 1.9 mW | 0.6 rad | **23 mm** |

Also: a point inside the image volume sees a beam within 7 mm for a duty of π(3.5 mm)²/0.04 m² ≈ 9.6×10⁻⁴ per beam, so the time-averaged power there is 4 heads × 0.40 mW × 8 × 9.6×10⁻⁴ ≈ **0.012 mW = 0.03×**; the per-flash energy is 4 × 50 µW × 4 ms = 0.8 µJ against a single-pulse AEL of 7×10⁻⁴·(4 ms)^0.75 = **11.1 µJ** (0.07×); and a **scan stall** parks one beam at 50 µW (EVAP, 0.13×) or 158 µW (FLOW-R, 0.41×) — below the CW AEL in both cases, so a stall is not itself a hazard.

**Rulings.** (i) RT9's C2 verdict stands for FLOW-R2, because its ~1 000 lines and its 0.2 W 850 nm probe are **CW**, so no averaging credit applies. (ii) For the *scanned visible* heads of FLOW-R and EVAP-R, desk and room, **C2 is not a wall**: a 20–40 mm recess clears it. (iii) Round 5 §4's "C2 is marginal as specified, 2.2–4×, needs ≥ 100 mm plus 3–4 heads" and "EVAP's bigger drops fix it" are both artefacts of the static accounting. (iv) **M2: EVAP's genuine power gain is ×1.6, not ×2–4** — from the table, 0.317 → 0.198 mW — and it comes from capture (×1.49, because a 15 µm drop at w 140 beats a 7 µm mote at w 80) plus p (×0.93). The other ×2 is the head count, which is free to FLOW-R.

### 2.4 The clear-drop trilemma: brightness, beam visibility and Class 1 cannot all hold [DERIVED] — CRITICAL

This is the finding I would put at the top of a redesign brief.

A beam of power P traversing the rain is itself scattered. Per unit length its luminous intensity toward a viewer at scattering angle θ_h is I′ = (P·β·p(θ_h)/4π)·683·V, with β = n·Q_ext·πa² = 1.6×10⁷×2.08×π(15 µm)² = **0.0235 /m**. An unresolved line of intensity I′ at distance D appears with luminance L = I′/(D²·θ_eye), θ_eye = 1 arcmin = 2.909×10⁻⁴ rad.

Dividing by the image line luminance L_img = (H·P·capture·p̄/4π)·683·V·n·d_s gives an invariant that is **independent of P, p and n**:

> **L_streak/L_img = (p_h/p̄) · Q_ext·π·w² / (2·H·d_s·D²·θ_eye)**

| Layout | p_h/p̄ | D | L_streak | L_img (that viewer) | ratio | vs ρ 0.05 wall at 10 lux (0.159 cd/m²) |
|---|---|---|---|---|---|---|
| EVAP, 4 heads el 30° | 4.5/1.29 | 1.0 m | **0.204 cd/m²** | 3.62 | 5.6 % | **1.28×** |
| EVAP, 4 heads el 30° | 4.5/1.29 | 0.5 m | **0.82 cd/m²** | 3.62 | 23 % | **5.1×** |
| EVAP, 6 heads el 25° | 6.1/1.29 | 1.0 m | 0.083 | 1.86 | 4.5 % | **0.52×** |
| EVAP, 6 heads el 25° | 6.1/1.29 | 0.5 m | 0.33 | 1.86 | 18 % | **2.1×** |
| FLOW-R white, 2 heads el 60° | 0.86/0.81 | 1.0 m | **0.0018 cd/m²** | 1.5 | 0.12 % | **0.011×** |

Worked example (4 heads, D 1 m): I′ = (5.0×10⁻⁵ × 0.0235 × 4.5/4π) × 485 = 2.04×10⁻⁴ cd/m; L = 2.04×10⁻⁴/(1×2.909×10⁻⁴) = 0.70… with the 1 m² path geometry taken as D²θ_eye = 2.909×10⁻⁴ m², **L = 0.204 cd/m²**.

**Readings.**
1. **EVAP-R's beams are ~110–200× more visible than FLOW-R's**, and they sit **1.3–5× above** the luminance of a dark wall at 10 lux. In the dim room the display requires, a viewer sees **32–48 faint rays converging on the image** — the fog-machine look. In a 100-lux room they vanish (1.3 % of a lit wall), but so does the 1.5 cd/m² image.
2. **The driver is p_h/p̄.** A clear drop has a ~100:1 forward-to-side phase-function ratio; a white mote is nearly isotropic (0.76–2.1 over all θ). The image is paid for at the *worst* viewer's p̄, while each viewer sees the beams at the *best* p_h — so clear drops are structurally penalised.
3. **Raising the heads does not fix it.** At 2 heads, ε = 60° (FLOW-R's layout), p_min = 0.035 → P_total = 3.06 mW → **1.53 mW per beam = 3.9× the CW AEL**, and even p_median = 0.14 gives 0.77 mW = 2.0×. So:

> **Low heads → bright image and easy Class 1, but visible beams and floor glare. High heads → invisible beams, but per-beam power above Class 1. There is no interior solution for a clear drop.** White motes escape the trilemma because p is flat.

4. **Haze is the lesser problem.** With a = 15 µm, τ over a 0.2 m column = 0.0235 × 0.2 = **0.47 %**; L_haze = τ·p_room·E_sc/4π = 4.70×10⁻³ × 0.635 × 20/4π = **0.0048 cd/m² = 3.0 %** of a dark wall at 10 lux, and **0.03 %** of a ρ 0.5 wall at 100 lux. Opus's 4.5–9 % used the injection size (a 19.3 µm → τ 0.78 % → 5.0 %); the image-average is ~4 %. Either way the **beam streaks are 40–170× brighter than the haze**, so opus analysed the wrong visibility channel. Opus's "water is not intrinsically less visible under room light" (phase factor 0.635 vs 0.866) is confirmed and is the right comparison for haze alone.

### 2.5 Floor glare [DERIVED] — MAJOR

Beams from heads at 25–30° elevation continue past the image and reach the floor. For a desk image 1.1 m above the floor, the path beyond the focus is 1.1/sin 30° = **2.2 m**; the beam radius there is w√(1 + (z/z_R)²) = 140 µm × √(1 + (2.2/0.12)²) = **2.57 mm**.

A 50 µW beam in that spot: flux = 50 µW × 683 × 0.71 = 0.0242 lm over π(2.57 mm)² = 2.08×10⁻⁵ m² → **1 165 lux** → on a ρ 0.2 floor, **74 cd/m²**. That is **49× the image's 1.5 cd/m²**, in a 5 mm spot that the eye resolves at 1.5 m (3.3 mrad). Each head sweeps a ~0.93 × 0.93 m patch; in a 100 ms integration the ~200 flashes cover 0.5 % of it, so the percept is a **scintillating sparkle field at image-level brightness spread over an area ~20× the image**, per head, ×4–6 heads.

Mitigation needs ρ ≤ 0.02 (0.07 cd/m², under the ambient) over ~2 m — a large black mat, i.e. another floor appliance. And note that **EVAP-R deleted FLOW-R's pedestal, which was the beam dump** (round 4 §5: "black louvres (the beam dump)"). Removing the pedestal is sold as a gain; it is partly a transfer of the dump problem to the room. Opus's "faint beam-end sparkle … use a dark rug" understates this by ~50× in luminance.

Stray beams are, however, **safe**: a 50 µW beam at 2 m has a 2.3 mm radius, so a 7 mm pupil takes it all — 0.13× the CW AEL — and 50 µW through a 1 mm aperture on skin is 0.03× the 1.571 mW EN 50689 visible cap. FLOW-R's 158 µW beams are 0.41× (eye), also fine.

### 2.6 Brightness along the image height [DERIVED] — m8

Required beam power ∝ 1/(capture) ∝ 1/a² for a ≪ w, so the power must rise as drops shrink down the image. With injection 0.1 m above a 0.2 m image, d = d₀√(1 − t/t_L):

| RH | d at the top | d at the bottom | power ratio bottom/top |
|---|---|---|---|
| 30 % | 34.2 µm | 23.6 µm | **×2.10** |
| 50 % | 35.7 µm | 29.2 µm | **×1.49** |
| 70 % | 37.0 µm | 33.8 µm | ×1.20 |

Opus's sizes reproduce and its remedy ("the controller knows each drop's z and age, so it scales the flash energy") is right in principle but has two costs it does not state: (i) the controller needs each drop's **age**, i.e. tracking from injection or a fall-speed-based size estimate, which is the same machinery §1.4 needs for satellites; and (ii) the per-head load at the bottom of the image rises by the same factor, so the 4-head/w 140 design goes from 1.03× to **2.2× the AEL at 30 % RH** — another reason the design point must be 6 heads.

---

## 3. Rendering and aim

### 3.1 The flow-normal lever: real, but it costs a factor 2.3–6.9 in rain density [DERIVED] — MAJOR

RT9's law (which m23b's docstring and round 5 §1.2 both use) is F(θ) ≈ n·U·d_s·t_eye·(d_s|cos θ| + b|sin θ|), where b is the along-stroke extent of a crossing dot, set by the eye blur.

I re-derived both limbs from scratch and they are right. At θ = 0 the drop travels along the stroke and paints U·t_eye of it, with n·d_s²·S drops in the tube → F = n·U·d_s²·t_eye. At θ = 90° the drop crosses the tube, painting only b of along-stroke length, and the number of crossings per t_eye is n·U·d_s·S·t_eye → F = n·U·d_s·b·t_eye. **So F(90°)/F(0°) = b/d_s exactly.**

| viewing distance | b (1 arcmin) | b/d_s at d_s 1 mm | n needed to restore F | water at the desk | haze vs a dark wall |
|---|---|---|---|---|---|
| 1.5 m (room) | 0.436 mm | **0.436** | ×2.29 | 40 g/h | 11 % |
| **0.5 m (desk)** | **0.145 mm** | **0.145** | **×6.90** | **119 g/h** | **32 %** |

**Rulings.**
- The gap statistic opus quotes is correct and is the lever's real benefit: at θ = 0, 67 % of stroke length sits in gaps > 10 mm; at θ = 90°, 7 %.
- But **the lever is not free**: it cuts the fill by b/d_s. Restoring it at desk viewing distance needs ×6.9 the rain, which takes the water load to 119 g/h (+28 % RH in 50 m³), the optical depth to 3.2 % and the haze contrast to 32 % against black — **a plainly visible column**, which breaks the "sub-visible" ruling the route depends on.
- The affordable form is **thicker strokes**: F(90°) ∝ d_s, so at d_s = 3 mm the fill is 0.19 (17 % lit) at the unchanged n = 1.6×10⁷. But total head power ∝ L·S·d_s/(p·capture) — **independent of n** — so d_s = 3 mm **triples** the power, and the simultaneous spot count n·d_s²·S goes from **8 to 72**, which multiplies the engine's channels/modes ×9. With 6 heads the per-head load is then 72 × 5.1 µW = 0.37 mW ≈ 1.0× at the vertex, i.e. the recess of §2.3 becomes mandatory.
- And §1.7: a horizontal jet sags 2–7 cm and its drop paths sit 6–10° off horizontal, so **θ = 90° is not actually achieved** for near-horizontal strokes.

**Net: keep the lever as a design variable (opus is right that flow direction is free), but price it. The honest version is "oblique 30–45° flow with d_s 2–3 mm", which buys most of the gap improvement for ×2 power and ×4 spots.**

### 3.2 Critique of round 5 §3.1 (the aim contrarian) — CRITICAL as a general claim

I did not duplicate the main session's Monte Carlo. The following is a critique of the analytic claims.

**What is right.**
1. **The structural objection is correct and important.** RT9 uses σ = √(C₀εt)·t/√3, a velocity-random-walk result valid only for τ_η ≪ t ≪ T_L. With RT9's own wake parameters (u′ = 0.1 m/s, L = 8 cm): ε = u′³/L = **1.25×10⁻² m²/s³**, τ_η = √(ν/ε) = **34.6 ms**. The aim operates at Δ = 3–6 ms, i.e. Δ/τ_η ≈ 0.1. **RT9's model is being used outside its range, and opus is right to say so.**
2. **The estimator algebra reproduces exactly.** S = τ²N(N²−1)/12 = (10⁻³)²×5×24/12 = **10⁻⁵ s² = 10 ms²**; h = Δ + 2 ms; noise = σ_c√(1/N + h²/S); bias = ½a(h² − S/N). At σ_c = 10 µm, Δ = 3 ms: noise = 10√(0.2 + 2.5) = 16.4 µm; a_rms = √(2.3×(1.25×10⁻²)^1.5×(1.5×10⁻⁵)^−0.5) = √(2.3×1.398×10⁻³×258.2) = **0.911 m/s²**; bias = 0.45×(25 − 2)×10⁻⁶ = 10.4 µm; σ = **19.4 µm** ✓ (opus 19). At Δ = 5 ms: 22.6 and 21.2 → **31.0 µm** ✓. Hit = 1 − exp(−R²/2σ²) at R = w/2 is the right Rayleigh criterion. **The arithmetic is sound.**
3. Consistency check on a₀: λ = √(15ν u′²/ε) = 13.4 mm → Re_λ = u′λ/ν = **89**, matching the a₀ = 2.3 opus quotes. Jerk is negligible: j ≈ a/2τ_η = 13 m/s³ → (1/6)jh³ = 0.74 µm. Acceleration is near-constant over the 11 ms span because the acceleration correlation time is ~2τ_η = 70 ms. All defensible.
4. **Drop inertia helps slightly.** St_η = τ_p/τ_η = 4.54/34.6 = 0.131, so the drop's acceleration variance is ~0.75–0.87 of the fluid's → a_rms ≈ 0.79–0.85 m/s². A small improvement in opus's favour.

**What is wrong: the claim is conditional on a weak wake, and opus states it as general.**

a_rms ∝ ε^(3/4) ∝ u′^(9/4), so the bias term is extremely sensitive to the wake strength. T9 §1 gives bare-hand plumes of **0.1–0.4 m/s** (0.035–0.2 gloved). RT9 chose u′ = 0.1 m/s, the top of the *gloved* range. Sweeping upward (L = 8 cm, a₀ rising with Re_λ, drop-inertia filtering applied):

| u′ | ε (m²/s³) | τ_η | Δ/τ_η at 3 ms | a_rms (drop) | σ at Δ 3 ms | hits w 80 | **hits w 140** |
|---|---|---|---|---|---|---|---|
| 0.025 (core) | 3.9×10⁻⁴ | 196 ms | 0.015 | 0.065 | 16.4 µm | 95 % | ~100 % |
| **0.10 (RT9, gloved)** | 1.25×10⁻² | **34.6 ms** | 0.087 | 0.79 | **19 µm** | 88 % | **99.7 %** |
| 0.20 (bare hand) | 1.00×10⁻¹ | 12.2 ms | 0.25 | 3.1 | 39 µm | 35 % | 79 % |
| **0.30 (bare hand)** | **3.38×10⁻¹** | **6.7 ms** | **0.45** | **6.7** | **79 µm** | **12 %** | **34 %** |
| 0.40 (bare hand) | 8.00×10⁻¹ | 4.3 ms | **0.69** | 11.4 | 132 µm | 4 % | 14 % |

At u′ ≥ 0.2 m/s, **Δ is no longer ≪ τ_η** — opus's own validity condition fails — and the hit fraction returns to RT9's order of magnitude. The vision allows a glove for the toucher, but other hands, arms and bodies in the room are bare, and so is the toucher's forearm.

**Three further conditions opus does not state.**
1. **M15: σ_c = 10 µm needs forward-scatter IR geometry.** For a defocus-blurred, shot-noise-limited drop, σ_c = blur/√N_e with blur = Δz·(A/2)/z. At Δz = 5 cm, A = 25 mm, z = 0.5 m the blur is **1.25 mm**. Photons per 1 ms frame at the IEC 62471 exempt mean of 100 W/m² (0.1 J/m²): scattered energy = 0.1 × Q_sca πa² = 0.1 × 2.08 × π(15 µm)² = 1.47×10⁻¹⁰ J; the fraction into a 25 mm aperture at 0.5 m (ΔΩ = 1.96×10⁻³ sr) is p·ΔΩ/4π. **At θ = 90° (p = 0.039) that is 6.1×10⁻⁶ → ~1 900 e⁻ at QE 0.3 → σ_c ≈ 29 µm**, and opus's own σ_c = 20–30 µm rows then give wake hits of 35–49 % (w 80) and 79–87 % (w 140). Placing the flood **opposite** each camera (θ 20–40°, p 2.4–8.6) multiplies the photons ×62–218 → **σ_c = 2–4 µm**, comfortably inside opus's assumption. So the claim survives, but only with a stated architecture: *an annular or offset IR flood on the far side of each camera*, never a co-located flood.
2. **The look-ahead must be measured from the last 1 kHz ROI frame.** Opus's bench plan uses 150–200 fps full frames plus 1 kHz ROIs. If the fit uses the 200 fps stream (τ = 5 ms, N = 5, Δ = 8 ms → h = 18 ms, S = 2.5×10⁻⁴ s²), the bias is 0.45×(324 − 50)×10⁻⁶ = **123 µm** → **15 % at w 140**, i.e. RT9's number exactly. The ROI handoff is therefore load-bearing, and it requires selecting each drop **≥ 5 ms before its flash** so that 5 ROI frames exist. That is feasible (8 ROIs per camera at 1 kHz) but it is an architecture requirement, not a parameter.
3. **The "hit" criterion is lenient.** R = w/2 means the drop sits where the intensity is e^(−0.5) = 0.61 of peak, so a marginal hit is 39 % dim. At 88 % hits with a broad offset distribution the line luminance scatters noticeably; a 0.8-of-peak criterion (R = 0.33 w) would cut the quoted hit fractions by ~20 points.

**Ruling.** Round 5 §3.1 is a **correct model correction applied at one point in parameter space and then generalised.** The right summary for T9 is: *RT9's inertial-range formula overstates the miss at Δ ≪ τ_η; with a windowed estimator, ≤ 3 ms latency, σ_c ≤ 10 µm and forward-scatter IR, a gloved-hand wake (u′ ≤ 0.1 m/s) gives 88 %/99.7 % at w 80/140, but a bare-hand or body plume (u′ 0.2–0.4 m/s) gives 4–35 %/14–79 %.* The touch region is still the weak region; what changes is that it degrades gracefully with wake strength instead of collapsing at once.

### 3.3 C1 (rate) escapes, and I can now name the architecture it needs [DERIVED] — confirms opus

η·n·U_f·δ·d_s = η × 1.6×10⁷ × 0.2724 × 5×10⁻³ × 10⁻³ = η × **21.8 /s** → 17–21 /s at η 0.8–0.95, against the 20 /s design. Opus's 16–19 /s reproduces (it used U = 0.25 without the settling term). **C1's escape is real: it was an artefact of FLOW-R2's probe∩camera gating, and tracking removes it.**

The tracking load is tractable only with the right architecture, which opus's bench plan implies but never states as a requirement. The desk column holds n·V = 1.6×10⁷ × (0.2×0.2×0.5) = **3.2×10⁵ drops**; tracking all of them at 1 kHz in 3D is ~100× beyond published real-time 3D PTV. But the content needs only the drops approaching its 100 samples: ROIs of 1 × 1 × 5 mm above each sample hold n × 100 × 5×10⁻⁹ = **8 drops**, exactly the 8 that get lit, and 100 ROIs × 4 cameras at 1 kHz is ~2×10⁸ px/s — commodity. **So C1 escapes provided the cameras run content-anchored ROIs, not full-frame tracking.** Optical sparsity is not the issue (0.0067 particles per pixel at 4 × 12 MP); data rate is.

---

## 4. Desk FLOW-R C2/C3 fixes (round 5 §4)

| Criterion | Round 5's finding | RT10 ruling |
|---|---|---|
| **C1, rate** | Escapes: 16–19 /s at η 0.8–0.95 | **CONFIRMED** (17–21 /s), with the ROI architecture of §3.3 named as a condition |
| **C2, head aggregation** | 0.84–1.56 mW = 2.2–4.0× at the vertex; 0.4–1.4× at 100 mm; needs ≥ 100 mm plus 3–4 heads, or EVAP's bigger drops | **BOTH HALVES WRONG.** The 100 mm figure overstates the mean ~10× (0.19 beams expected, not 20–35 % of 8). Properly treated as a scanned beam, a **37 mm recess** clears FLOW-R desk; in-volume time-average 0.05 mW (0.13×), per-flash 0.07× the single-pulse AEL, scan-stall 0.41×. EVAP's contribution is ×1.6, not ×2–4, and the head count is free to FLOW-R (**6 low heads give 33 µW/beam, 0.68× at the vertex with no recess**) |
| **C2, pupil in the column along a beam** | 0.8–1.5× (FLOW-R), 0.2–0.4× (EVAP) | **Over-strict.** The time-average at a fixed in-volume point is 0.03–0.13×; the worst instantaneous case is 1–2 beams = 0.41–0.81× (FLOW-R), 0.13–0.26× (EVAP) |
| **C2, skin at the exit (1 mm)** | ≤ 1.56 mW, borderline | **PASSES**: 1.27 mW against 1.571 mW even unrecessed; 0.26 mW with 6 heads |
| **C3, aim** | Core 79–95 %; wake 57–88 % at w 80, 92–99.8 % at w 140 | **CONDITIONAL** — see §3.2. Right for u′ ≤ 0.1 m/s with forward-scatter IR and a 1 kHz ROI chain; 4–35 % (w 80) and 14–79 % (w 140) at u′ 0.2–0.4 m/s |
| **C3, registration** | ≤ 20–30 µm over 0.5–0.8 m; aluminium drifts 16 µm/K; closed-loop recalibration | **ACCEPTED** [ESTIMATE]. Note the budget must be added in quadrature to §3.2's σ: at σ 19 µm plus 25 µm registration the total is 31 µm, which alone takes w 80 hits from 88 % to 57 % |
| **The open item** | "real-time tracking at η ≥ 0.8 with ≤ 5 ms latency: commodity cameras plus custom software, not physics" | **AGREED, with the ROI architecture as the specific unproven item** |

**Net on §4: FLOW-R desk comes out of RT10 stronger than it went in.** C1 escapes, C2 is comfortably clear once scanning is credited, and C3 is the one real wall — and it is shared with every rain route. Its remaining relaxations (sugar dust at 13–35 mg/m³ in-column, a hood plus a pedestal, ≥ 99 % capture, dotted vertical strokes) are unchanged by this review.

---

## 5. The O-band: m24

I reproduced `m24_oband.py`'s arithmetic by hand and **found no error** [m12].

- Skin: 2000·C_A W/m² with C_A = 5 at 1050–1400 nm = 10 kW/m²; × π(0.5 mm)² = **7.854 mW**; ÷ h·s = 2.35 → **3.336 mW** per focus. ✓
- Eye: C7 = 8 + 10^(0.04(λ−1250)) → 47.8 / 259.2 / 4 794 at 1290 / 1310 / 1342 nm ✓; retinal AEL = 3.5×10⁻³·C7·10^(−0.25) = 94.1 mW / 510 mW / 9.4 W; min with the 0.5 W Class 3B dual limit gives 94.1 / 500 / 500 mW ✓. (Cross-check: the Ed. 3 form 3.9×10⁻⁴·C₄·C₇ with C₄ = 10^(0.002(λ−700)) gives 2.09 mW at 1064 nm against the project's 1.97 mW, and 1.68 W at 1310 nm — still clipped by the 0.5 W dual limit, so nothing changes.)
- Tetralemma: w_max = √(2·cap/(π·I_unit·v)) = √(2×3.336×10⁻³/(π×1.5×10⁷×0.03)) = **68.7 µm** at 3 cm/s ✓; modes (X/πw)² = (0.6/(π×68.7 µm))² = **7.73×10⁶** ✓; loop 10 v/w = **4 367 Hz** ✓.

**The ×10 skin lever is robust.** It is the one unambiguous gain in the O-band and it survives everything below.

### 5.1 Is the softened eye-margin statement right? [DERIVED] — largely yes, with three refinements

T9 §2.9 now says: Ed. 3 cautions that the 0.5 W dual limit may not protect the anterior eye; the ~6 mm absorption depth at 1310 nm buys only ×4.5–8 in anterior heating per watt, not ×50; RT8 C1 sits at 0.6–2×, not resolved; only the skin lever is robust.

My independent check of the thermal part, with k = 0.58 W/m/K, r_b = 1.75 mm, P = 10 mW:

| λ | α | 1/α | regime | ΔT at 10 mW | K/W |
|---|---|---|---|---|---|
| 1550 nm | 1 000 /m | 1.0 mm < r_b | surface disc, ΔT = P/(π r_b k) | **3.14 K** | 314 |
| 1310 nm | 130 /m | **7.7 mm** ≫ r_b | line source, ΔT = (0.63Pα/2πk)(½ + ln(1/αr_b)) | **0.445 K** | 44.5 |
| 1342 nm | ~200 /m | 5.0 mm | line source | 0.62 K | 62 |

Ratio 1550/1310 = **7.1× collimated** (opus's own bracket is 4.5× collimated to 8× focused; 1550's disc figure of 3.14 K is slightly above opus's round-3 1.8 K, which is why I get 7.1 rather than 4.5). So:

1. **Direction and magnitude: confirmed.** The physical equivalence is single-digit, not ×50.
2. **Refinement: the quoted range should be 0.34–2.0×, not 0.6–2×.** RT8 C1's stacking is 2.7–9.1× the 1550 nm 10 mW AEL, so at 1310 nm it is (2.7–9.1)/(4.5–8) = **0.34–2.0×** of a physically equivalent limit. Opus quotes 0.6–2× by using only the 4.5× end. The honest statement is "**0.3–2×, i.e. borderline, with the median case at ~1×**".
3. **Refinement: the heated organ is not the cornea.** At 1/α = 7.7 mm the deposition is spread through the 0.5 mm cornea, the 3 mm aqueous and into the lens, so the endpoint that Ed. 3's caution note is really about is **lenticular**, not corneal — which is precisely why C7 and the dual limit exist at all. The 10 s radial thermal diffusion length (√(4α_th t) = 2.4 mm) exceeds r_b, so the steady 2D estimate is appropriate for a 10 s timebase.
4. **Refinement: "~6 mm" should be 7.7 mm at 1310 nm and ~5 mm at 1342 nm** [m11].

**Ruling: the softening is correct and should stay, with the range widened to 0.3–2.0× and the endpoint named as the aqueous/lens.** Opus's design note that the absorber must move off ITO's plasma edge to Cs_xWO₃ or carbon is a sensible [ESTIMATE] and I found nothing against it.

---

## 6. m25: is the model biased, and are its numbers right?

### 6.1 The P/cap numbers are right, and they have a closed form [DERIVED]

m25 reports the run-mean of the **summed** beam amplitudes at each focus against CAP_FOCUS = 7.854/1.1 = **7.14 mW**. That is the correct comparison: with w = 40–100 µm ≪ 1 mm, all three beams' power passes the EN 50689 1 mm aperture, so the skin at the focus does see Σ P_b. The profile bookkeeping is also right: ∫(1+2x)e^(−2x) over the beam = πw² against πw²/2 for a Gaussian, so `prof_power = 2` is exact for equal centre intensity.

The mean force must balance the mean air speed, allocated over 3 beams at the H10 facet cost h, so

> **P/cap = h·|u|·I_unit·π·w²·prof / (2·P_cap)**

with |u| = √(U_mean² + 3σ²). Home: |u| = √(0.05² + 3×0.03²) = **0.0721 m/s**; h_mean = 1.38.

Check against the log, home, w 70 µm, dip: P = 1.38 × 0.0721 × 1.5×10⁷ × π(70 µm)² /2 × 2 = **23.0 mW** → P/cap = **3.22**. The log gives **2.84 / 3.67** (p50/max). Check at w 40, Gaussian: P = 1.38 × 0.0721 × 1.5×10⁷ × 2.513×10⁻⁹ = 3.75 mW → **0.53**; the log gives 0.60/0.66. **Agreement to ±15 % across the grid — m25's power column is sound.**

Inverting it gives the design limit:

| draft | \|u\| | Gaussian w ≤ | modes/head | dip w ≤ | modes/head |
|---|---|---|---|---|---|
| still room | 0.052 | 65 µm | 8.6×10⁶ | 46 µm | 1.7×10⁷ |
| **home** | **0.0721** | **55 µm** | **1.2×10⁷** | **39 µm** | **2.3×10⁷** |
| quiet office | 0.112 | 44 µm | 1.9×10⁷ | 31 µm | 3.7×10⁷ |

and the Gaussian column is not usable, because m25 shows the Gaussian runaway losing motes at exactly those small w (home w 40 gauss: 8/20 lost even at 5 kHz). **So the binding home design point is the dipped w ≈ 39 µm at P/cap ≈ 1.0, requiring 2.3×10⁷ modes per head.** That is ×3 the 7.7×10⁶ in m24's tetralemma row, because m24 sized w from the cap alone and m25 adds the runaway and the ×2 dip cost.

### 6.2 m25's verdict names the wrong failure — MAJOR

T9 §2.9 concludes: "at 1310 nm a static voxel in home drafts still needs a ~5 kHz, ~10⁷-mode modulator per head. No commodity-rate engine fits."

**Its own table contradicts the rate half.** PLM 1.44 kHz holds (0/20) at home with dipped w ≥ 70 µm, and the loop requirement can be derived in closed form. The plant from commanded force (speed units) to position is 1/s; with Kp = 0.5/D and Ki = Kp²/4 the integral action dominates across the disturbance band (the Kp/Ki crossover is at ω = Kp/4 = 66 rad/s, above the band), so

> σ_x ≈ u_rms·ω_rms/Ki = **16·u_rms·ω_rms·D²**, with D = (d+0.5)T + τ_th + τ_lc.

Spectral moments of `rt6.turb_spectrum` at u_rms 0.03, L 0.03, Uc 0.05: knee f₀ = 3.963 Uc = **0.198 Hz**, Pao cutoff f_η = Uc/2πη = **4.81 Hz** (η = 1.655 mm at ε = 4.5×10⁻⁴), giving f_rms = √(m₂/m₀) ≈ **0.91 Hz → ω_rms ≈ 5.7 rad/s**.

| case | τ_lc | D | Kp | Ki | σ_x (PID only) | vs 1.5 w at w 70 = 105 µm |
|---|---|---|---|---|---|---|
| LCoS 120 Hz | 4 ms | 25.0 ms | 20 | 100 | 1 700 µm | lost ✓ |
| LCoS 240 Hz | 2 ms | 12.5 ms | 40 | 400 | **427 µm** | lost ✓ |
| **500 Hz class** | 0.5 ms | 5.5 ms | 91 | 2 070 | **83 µm** | **holds** |
| PLM 1.44 kHz | 0.1 ms | 1.88 ms | 267 | 1.78×10⁴ | **9.6 µm** | holds ✓ (log: p50 16 µm) |
| MEMS 5 kHz | 0.03 ms | 0.57 ms | 877 | 1.92×10⁵ | 0.9 µm | holds ✓ (log: 9 µm, noise-floor-limited) |

Inverting: holding w 70 needs **D ≤ 6.2 ms**, i.e. T ≤ (6.2 − τ_lc − τ_th)/2.5 → **~400–600 Hz**, not 5 kHz. m25's grid jumps 240 → 1 440 Hz and never samples that region.

**And the power is modulator-independent** (§6.1: P/cap depends on w, |u| and the profile, not on the frame rate) — which the log itself shows: home, w 70, dip gives 2.84 at PLM and 3.01 at MEMS 5 kHz.

> **Corrected verdict: the O-band static route is not rate-limited at ~400 Hz and above; it is limited by (a) the per-focus skin power, which sits at 2.8–3.7× the cap at the w ≥ 70 µm where holding is easy and reaches ~1.0× only at the dipped w ≈ 39 µm, and (b) the 2.3×10⁷ modes per head that w requires. "No commodity engine fits" survives — because of mode count and power, not rate.**

### 6.3 Biases: against on rate, neutral on power, strongly optimistic at system level

**Biased against the route:**
1. **M7, the air feedforward is missing.** The docstring specifies `f_des = -u_est - Kp(x_pred-home) - Ki∫` with `u_est = v_est - F_est`; the code is `f_des = -Kp*err - Ki*integ`, with the mean wind carried only by the integrator (initialised to −F/Ki). With feedforward the residual disturbance is u̇·D = u_rms·ω_rms·D instead of u, so σ_x ≈ (u_rms ω_rms D)·ω_rms/Ki. For LCoS 240 Hz that is 427 µm → **30 µm**, which **holds at w 70**. The estimator is practical: σ_n = 4 µm at T = 4.17 ms gives a velocity noise of 1.4 mm/s against u_rms 30 mm/s (SNR 22). **This changes which modulators pass but not the verdict, because the verdict is power-bound.**
2. **The integral scale L = 3 cm is small for a room** (typical 0.1–1 m). At L = 0.3 m, ω_rms falls ×3.2 and σ_x falls ×3.2 — LCoS 240 Hz would then sit at 133 µm, and with feedforward well inside tolerance. Bias against.
3. **Kp = 0.5/D is ~1.6× below the delay-limited optimum** (0.785/D at 45° phase margin), and Ki = Kp²/4 is conservative; a Smith predictor for a known delay would do better still. Bias against by ~×2.5 in Ki.
4. **m13: Uc = 5 cm/s with u_rms = 3 cm/s violates Taylor's hypothesis** (Uc/u′ = 1.67 ≫ 1 required). By luck the resulting knee (0.198 Hz) is close to the physical eddy turnover u′/2πL = 0.159 Hz, so the spectrum shape is about right for L = 3 cm. But the `DRAFTS` sweep entangles U_mean with Uc, so "quiet office" is harder in both mean wind and bandwidth at once and cannot be read as a clean bandwidth sweep.

**Biased for the route:**
5. **M8, the loss criterion is tracking, not holding.** `spot = x_pred` follows the mote, and loss is `off > 1.5 w` from the spot. So the LCoS still-room w 100 dip row (1/20 lost, P/cap 4.31) has **home p99 = 705 µm**, and the MEMS quiet-office w 100 dip row (1/20 lost) has **home p99 = 20 396 µm** — a mote 2 cm from its voxel, still "held". Those are display failures. A holding criterion (|x − home| ≤ ~0.3 mm, a third of a 1 mm voxel) would reclassify them. The rows that carry the verdict (home/dip/w ≥ 70) have home p99 of 20–37 µm, so the conclusion is unaffected, but **the table as printed is misleading** and T9's "holds" language should be qualified.
6. **M9, the statistics are ~6 orders short.** 20 motes × 5 s (minus the 0.3 s settling) = ~10² mote-seconds; a display is ~10⁴ motes × hours ≈ 10⁸. Loss is a rare-gust upcrossing problem (RT6's Rice-level machinery), so 0/20 at 5 s only certifies 1.5 w/σ_x ≈ 3; 10⁻⁸ per mote-second needs ≈ 6–7. **σ_x must be ~2× smaller → D ~1.4× smaller → the rate requirement rises ×1.4–2.**
7. **M10, one focus is modelled; a display needs 10³–10⁴.** With 10 heads and 10³ foci at 3 beams each, a head carries ~300 beams in a narrow bundle at w 40 µm, so the per-head aggregate — the RT8 C1 / RT9 C2 problem — is ~300× the per-focus value and is **entirely unmodelled**. This is the dominant optimism and it is far larger than items 1–4 combined.
8. σ_n = 4 µm with no outliers, no registration drift, no mote-identity confusion and exact amplitude→force calibration [ESTIMATE, optimistic].
9. Run length 5 s against a 10 s skin timebase: the reported mean is over the wrong window (minor, and it cuts both ways).

**Net.** m25 is biased against the route by ~3–8× on the rate axis, is accurate on the power axis, and is optimistic by ~2 orders at the system level. **Its conclusion survives; its stated reason does not.** `m25_oband_static.py`'s own self-test passes and I found no coding error beyond the missing feedforward term and the unused `bw_frac` parameter.

---

## 7. Minor findings (m1–m13), collected

| # | Finding |
|---|---|
| m1 | Satellites: a 3 pL satellite lives **0.57 s** (opus: ≤ 0.3 s) but vanishes within 0.14 m, so the conclusion holds. It is 4.6× dimmer and sub-resolution, so it must be classified by fall speed (0.96 vs 4.48 cm/s), not size |
| m2 | Coalescence negligible: Saffman–Turner 7.0×10⁻⁵ /s at in-jet ε = 0.052 m²/s³ (1.8×10⁻⁴ per lifetime); differential sedimentation with satellites the same order |
| m3 | Ventilation f_v = 1.03 at terminal fall (Re 0.11) and 2.64 during the ~15 ms, 68 mm deceleration from a 15 m/s Rayleigh jet — a < 1 % effect |
| m4 | A drop reaches its wet-bulb temperature in **20 ms** (ρ_w c_w d²/12k_a), 0.8 % of its life |
| m5 | **The Mie table is confirmed** by geometric optics: p(90°) = R̄(45°) = 0.0282 vs Mie 0.035–0.055; Lambert 0.764 at 90° and 2.11 at 150° reproduce exactly; the 141° rainbow is the expected Airy shift from the geometric 138° |
| m6 | Polarisation: R_s/R_p = 18.8 at 45° incidence, so a linearly polarised beam modulates the 90° brightness ×19 with viewer azimuth. Mild in the recommended 25° ring; severe in any 60°-elevation layout. Depolarise or use crossed pairs |
| m7 | Haze recomputed at a = 15 µm: τ = 0.47 % over 0.2 m → **3.0 %** of a dark wall at 10 lux and 0.03 % of a lit wall (opus's 4.5–9 % used the 19.3 µm injection size). Haze is 40–170× fainter than the beam streaks |
| m8 | Brightness gradient down the image: required power ×1.49 (50 % RH) to ×2.10 (30 % RH). Needs each drop's age, and it raises the 4-head design to 2.2× the AEL at 30 % RH |
| m9 | Glove impaction: η ≈ 0.03 at St 0.142 (cylinder critical 0.125), ~0 for a palm-sized disc → **0.13 g/h**, not opus's 0.4–0.9 g/h. In EVAP's favour |
| m10 | The cooling plume **stabilises** a downward jet (0.25 → 0.264 m/s over 0.5 m, net of vapour buoyancy) — opus confirmed; it does not destabilise a push-only jet. It makes a *horizontal* jet sag (§1.7) |
| m11 | T9 §2.9's "absorption depth ~6 mm" is 7.7 mm at 1310 nm and ~5 mm at 1342; the eye-margin range should be 0.3–2.0× |
| m12 | **m24 reproduces exactly** (caps, C7, w_max, modes, loop). No error found |
| m13 | Uc/u′ = 1.67 breaks Taylor's hypothesis in m25's turbulence synthesis, but the resulting knee matches the physical eddy turnover for L = 3 cm; the `DRAFTS` sweep entangles U_mean with Uc; `bw_frac` is an unused parameter |

---

## 8. Overall: is there a reading under which EVAP-R or FLOW-R meets the vision?

### 8.1 What EVAP-R genuinely buys, stated precisely

One thing, and it is worth keeping in the project's vocabulary:

> **An evaporating medium decouples scatterer size from particulate load.**

Required beam power ∝ 1/(p·capture) ∝ 1/a² at fixed w, so bigger scatterers are always better optically. For a *persistent* medium that is unaffordable: scaling FLOW-R's white motes from a 7 µm to a 14 µm radius would give the same ×1.5 capture gain and keep white's flat phase function (no beam streaks, no RH dependence) — but in-column mass goes as a³, from 34 to **280 mg/m³**, which at 99.9 % capture leaves ~250 µg/m³ in the room and fails every particulate guideline. **Water drops are the only way to have 30 µm scatterers with zero steady mass.** That is EVAP-R's real and only physics advantage, and it is worth ×1.6 in beam power and ×1.75 in aim radius.

Everything else EVAP-R introduces is new cost: humidity-dependent wetting (§1.2), a visible beam cage (§2.4), floor glare with no beam dump (§2.5), a non-commodity additive-free generator (§1.6), a water consumable with a hygiene regime (M13), and a water-purity interlock (§1.5).

### 8.2 Rulings each route needs from the owner

| Ruling | FLOW-R desk | EVAP-R desk |
|---|---|---|
| A sub-visible medium is "no fog" | needed (0.15 % optical depth) | needed (0.47 %, **and** visibly a mist by name) |
| A hood/pendant air source is "just a projector" | needed (hood **plus pedestal**) | needed (pendant only — EVAP's one fit gain) |
| Dotted/dashed strokes at fill 0.2–0.4 | needed | needed |
| **Visible converging light rays in the dim room** | not needed (0.012× a dark wall) | **needed** (§2.4: 1.3–5×) |
| **A ~2 m ρ ≤ 0.02 floor mat** | not needed (pedestal is the dump) | **needed** (§2.5) |
| **Room RH kept ≤ 32 % (30 pL) or ≤ 60 % (10 pL, ×2.1 power)** | not needed | **needed** (§1.2) |
| A water consumable plus a hygiene/service regime | not needed | **needed** (M13) |
| Food-grade sugar dust at 13–35 mg/m³ in-column, ≥ 99 % capture | **needed** | not needed |
| **Count** | **4** | **7** |

**So EVAP-R does not improve the vision fit; it worsens it.** Round 5's framing ("the nearest thing yet to a projector head that breathes an invisible mist, with no table, pedestal or residue") holds only on the pedestal clause. The mist is not invisible in the viewing conditions the display needs, and it is not residue-free with any commodity generator.

### 8.3 Is there *any* reading under which the vision is met?

**Desk.** Yes, under four rulings, and it is FLOW-R, not EVAP-R: *a 0.2 m, 1.5–3 cd/m² dotted-line figure, floating in open air between a 0.45 m hood and a 0.5 m pedestal, touchable with a glove, visible from all azimuths, interactive in one frame, passively Class 1 with a 37 mm recess (or 6 low heads and none), built for $5–12k.* That is a real thing and RT10 makes it more credible, not less (§4). It is not "Iron Man in the room": it is 5× small, 10× sparse, dim-room-only, and needs a hood and a pedestal.

**Room.** No. RT9 killed FLOW-R2 as specified; RT10 removes one of its three criticals (C2, for the scanned visible heads) but leaves C1 (starved gated rain), C3 (aim), the 0.2 W CW probe fan, 34 g/h of motes, ≥ 99.9 % capture and a $50–120k engine. EVAP-R at room scale adds the floor-wetting threshold at 64 % RH and 43 g/h of water. **No reading reaches the room.**

**O-band static voxels.** No. §6 sharpens the reason: ~1.0× the per-focus skin cap at a dipped w ≈ 39 µm, needing 2.3×10⁷ modes per head, with the per-head aggregate over 10³ foci unmodelled and ~300× worse.

### 8.4 Ranked nearest buildable demos, with honest P

P = probability the demo meets its own written pass criteria on a bench within its stated budget and time. Fit = fraction of the owner's vision delivered.

| Rank | Demo | P | Fit | Score | What decides it |
|---|---|---|---|---|---|
| **1** | **FLOW-R desk "holo-pedestal"** (round 4 §5, with RT10's fixes: 6 low heads at 33 µW, a 37 mm recess or none, content-anchored 1 kHz ROIs, forward-scatter IR flood) | **0.35** | 0.25 | **0.088** | C3 in a *bare-hand* wake (§3.2); η ≥ 0.8 ROI tracking at ≤ 3 ms; ≥ 99 % capture with people moving |
| 2 | **EVAP-R week-1 bench only** — drops, lifetime, vanish height and deposition cards at RH 30/50/70 %, ~$1k, 1 week | **0.90** (of a decisive answer) | 0 | — | Cheap and decisive: it measures §1.2's RH ≤ 32 % threshold directly. **Do this before anything else EVAP** |
| 3 | Aerial-imaging plate plus glove | 0.95 | 0.05 | 0.048 | Exists; a 40° holo-window, excluded by the vision |
| 4 | O-band single-mote hold (one PLM, one 1310 nm head, one mote, dipped w 70 µm) | 0.30 | 0.05 | 0.015 | Would confirm m25's PLM rows. But it holds at **2.8–3.7× the skin cap**, so it is a physics datum, not a product path |
| **5** | **EVAP-R full desk demo** (round 5 §6, 6 weeks, $4–8k) | **0.12** (was 0.45) | **0.22** (was 0.35) | **0.026** | Three independent criticals: RH ≤ 32 % for a dry surface; visible beam cage at 1.3–5× a dark wall; no commodity additive-free 30–45 µm generator |
| 6 | FLOW-R2 room (RT9's redesign items 1–6) | 0.05 | 0.45 | 0.023 | C1 and C3 unresolved; CW probe fan; $50–120k |
| 7 | EVAP-R room pendant | 0.03 (was 0.15) | 0.40 | 0.012 | Adds floor wetting above 64 % RH and 43 g/h of water to rank 6's problems |
| 8 | Vortex-ring mist delivery | 0.10 | 0.40 | 0.040 of *delivery*, not of a display | opus's [SPECULATIVE] stands; untouched by RT10 |

**Ranking change from round 5: EVAP-R desk moves from rank 1 (0.16) to rank 5 (0.026), and FLOW-R desk takes the top slot.** The decisive reason is not that any single EVAP number is wrong by a lot — most of opus's physics is right, and its Mie and lifetime work is the best in the round — but that the three things it did not compute (deposition at ordinary RH, beam-path scattering, the generator's additive requirement) are each sufficient on their own.

### 8.5 What would change this verdict

1. **A measured vanish height and deposition card at RH 50 % and 70 %** (rank 2 above, ~$1k). If drops leave < 1 drop/cm²/10 min on a card 0.5 m below a 30 pL injector at **50 %** RH, §1.2 is wrong and EVAP-R returns.
2. **A measured beam-streak luminance** against a ρ 0.05 backdrop at 10 lux, with one head at 25–30° and a calibrated camera at the opposite azimuth. If it is below ~0.01 cd/m², §2.4 is wrong. (Predicted 0.08–0.82 cd/m².)
3. **An additive-free generator** at 30–45 µm and ≥ 10⁵ /s from commodity parts. A piezo-driven laser-drilled orifice plate with dispersion air is the candidate; nothing off the shelf does it.
4. **A hand-wake Monte Carlo swept over u′ = 0.05–0.4 m/s** with a Sawford second-order model and the windowed estimator, reporting the hit fraction against wake strength rather than at one point. (The main session's run should be read this way.)
5. **An m25 rerun** with (a) the air feedforward its docstring specifies, (b) a holding criterion |x − home| ≤ 0.3 mm, (c) frame rates sampled at 300/500/700 Hz, (d) L = 0.3 m, and (e) Rice-level extrapolation to 10⁻⁸ per mote-second. Prediction: the rate wall moves to ~400 Hz and the verdict becomes purely power-and-modes.
6. **A per-head aggregate model for the O-band static route** (10³ foci, 10 heads, w 40 µm): the missing piece that probably dominates everything in m25.

---

## 9. Notes for the main session

1. **T9 §3.5:** replace "1.6 / 2.3 / 4.0 s (main session; opus 1.8 / 2.6 / 4.5 s)" with **1.8 / 2.6 / 4.6 s**, and note that `v10_round5_check.py` applies the psychrometric (boundary-layer, Le^(2/3)) closure to a free drop, which understates the depression by 1/Le = 1.15. The sphere closure is k_a(T − T_s) = L_v D_v Δρ.
2. **T9 §3.5 / §4:** add the deposition line. **A 30 pL EVAP-R rain is dry under a 0.5 m pendant only at RH ≤ 32 %**; at 50 % it deposits 79 g/m²/h and at 70 % 211 g/m²/h. This belongs in the EVAP-R cost list above "haze".
3. **T9 §3.5:** add the beam-visibility invariant L_streak/L_img = (p_h/p̄)·Q π w²/(2 H d_s D² θ_eye), and the trilemma: clear drops cannot have an invisible beam path and Class 1 per beam at the same time.
4. **T9 §3.5:** the flow-normal lever cuts the fill by b/d_s (0.145 at desk viewing). Price it as "oblique 30–45° flow with d_s 2–3 mm, ×2 power, ×4 spots", not "free".
5. **RT9 C2 and round 5 §4:** recompute head aggregation as a **scanned** beam (time-average through 7 mm at the worst accessible position, plus single-pulse, pulse-train and scan-stall). The recess is 20–40 mm, not 100–300 mm. RT9's C2 verdict still stands for FLOW-R2's CW probe fan and its ~1 000 CW lines.
6. **Round 5 §2.4/§2.6:** change the EVAP-R design point to **6 heads at 25° elevation, 17 µW per beam**. Four heads at w 140 is 1.03× the CW AEL at the vertex with 8 lines, and 2.2× at 30 % RH once the brightness gradient is included.
7. **Round 5 §3.1:** the dissipative-range result should be quoted **as a function of u′**, not as a single pair of numbers. 88 %/99.7 % at w 80/140 holds at u′ = 0.1 m/s; 12 %/34 % at u′ = 0.3 m/s, where Δ ≈ 0.45 τ_η and the model itself is out of range. Add the two architecture conditions: forward-scatter IR flood, and the look-ahead measured from the last 1 kHz ROI frame.
8. **T9 §2.9 m25 verdict:** rewrite as "**the route is not rate-limited above ~400 Hz; it is limited by the per-focus skin power (2.8–3.7× the cap at w ≥ 70 µm, ~1.0× only at a dipped w ≈ 39 µm) and by the 2.3×10⁷ modes per head that w needs.**" Flag that m25 omits the air feedforward its docstring specifies, that its loss criterion is tracking rather than holding, and that it models one focus where a display needs 10³–10⁴.
9. **T9 §2.9 eye margin:** widen "0.6–2×" to **0.3–2.0×**, change "~6 mm" to 7.7 mm at 1310 nm, and name the heated organ as the aqueous/lens rather than the cornea.
10. **An m26 for EVAP-R is still worth writing**, but it should lead with deposition versus RH and with the beam-path scattering integral, not with lifetimes and haze — those two are already settled (opus's lifetimes are right; haze is the lesser visibility channel by 40–170×).
11. `09_unlock/rt10_check.py` reproduces every number in this report and **has not been run** (the session's gate blocked Bash). Running it is the first thing to do with this review.

---

## Summary (≤ 400 words)

**The tetralemma stands.** Nothing in round 5 reopens it, and RT10 adds no escape.

**EVAP-R is refuted on three independent grounds.**
1. **Wetting.** A 30 pL drop is dry under a 0.5 m pendant only at **RH ≤ 32 %**. At 50 % RH drops arrive at 21.9 µm and deposit **79 g/m²/h**; at 70 %, 211 g/m²/h against a surface capacity of ~270. A 10 pL rain raises the threshold to 60 % RH at ×2.1 the beam power. European homes sit at 40–60 %.
2. **A visible beam cage.** L_streak/L_img = (p_h/p̄)·Qπw²/(2H d_s D²θ_eye) → **0.20 cd/m² at 1 m, 0.82 at 0.5 m**, i.e. 1.3–5× a dark wall at 10 lux and ~200× FLOW-R's white motes. Raising the heads to 60° hides the beams but makes the per-beam power 2.0–3.9× the Class 1 AEL. No interior solution exists for clear drops. Haze (3–5 %) is the lesser channel by 40–170×.
3. **No commodity additive-free generator.** Thermal DOD needs humectant (1 % → 4.3 g/day deposited); piezo-mesh gives 4–6 µm drops (44 ms lifetime, ×60 dimmer); Rayleigh breakup works on pure water but is lab hardware.

**What survives of round 5.** Opus's Mie table (confirmed independently: p(90°) = Fresnel R̄(45°) = 0.028), its low-ring parity (with 6 heads, not 4 — 4 heads sit at 1.03× the AEL), its wet-bulb lifetimes (**opus is right; the main session's v10 is 13–16 % short**), its negligible-coalescence and stable-plume conclusions, and its T9 §3.3 drying correction.

**Three corrections that help the project.** RT9 C2 and round 5 §4 compute head aggregation statically; as a **scanned** beam the recess is **20–40 mm**, not 100–300. EVAP's power gain is **×1.6**, not ×2–4 — the rest is head count, free to FLOW-R. The flow-normal lever cuts fill by **b/d_s = 0.145**, so it costs ×2–7 in rain density or ×3 in power.

**The aim contrarian is right but conditional.** RT9's inertial model is indeed invalid at Δ ≪ τ_η, and opus's arithmetic reproduces. But at a bare-hand plume (u′ 0.3 m/s) τ_η = 6.7 ms ≈ Δ and hits fall to **12 %/34 %** at w 80/140. σ_c = 10 µm also needs a forward-scatter IR flood (29 µm at 90°).

**O-band.** m24 reproduces exactly; the ×10 skin lever is robust; the softened eye margin is right (widen to 0.3–2.0×, endpoint lenticular). **m25's verdict names the wrong failure**: ~400 Hz suffices, and the wall is power (~1.0× the cap at a dipped w 39 µm) plus 2.3×10⁷ modes per head.

**Ranking.** FLOW-R desk **0.088** > aerial plate 0.048 > **EVAP-R desk 0.026** (was 0.16) > FLOW-R2 room 0.023 > EVAP-R room 0.012. Do the $1k EVAP-R deposition bench first; it is decisive.

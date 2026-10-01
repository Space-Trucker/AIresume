# Idea round 2: independent report (Sonnet): mote materials, light generation, 2026 hardware

*Date 2026-10-01. Scope: items 1, 2 and 3 of the brief (materials with measured properties, light generation without per-mote pump focusing, hardware and prices). Items 6 and 7 (other routes, IEC adversarial check) are only touched where a number fell out.*

*Tags: [MEASURED+source] is a number a search result reported. I could read search snippets only: the fetch tool was blocked for arxiv, springer, mdpi and fraunhofer, so any [MEASURED] figure below should be confirmed against the datasheet or paper before it goes in a verdict. [THEORY] is derived here, [ESTIMATE] is an engineering estimate with stated inputs, [SPECULATIVE] is an idea with no supporting number.*

*Scripts (scratchpad, not in repo): `j1.py` (J1(τ) integral), `cand.py` (candidate table), `sys.py` (system numbers).*

---

## 0. Bottom line (read this first)

1. **There is no material "needle" in FOM.** The force on a mote scales with **J1/(k_p + 2k_g)**, and k_g = 0.026 W/m/K is room air. With J1 ≤ 0.5 (front-surface absorber) and the lowest measured aerogel k_p ≈ 0.012–0.017, the ceiling is **FOM·A ≤ 0.5/(2k_g + k_p) ≈ 7.2–8.0 m·K/W**. For an air-filled sealed hollow shell (k_p = k_g) the ceiling is 6.4. [THEORY]
   Realistic made-class materials land at 2.3–4.7. The brief's gate "FOM ≳ 4" is therefore a gate at about half the ceiling.
2. **The lever that is not in T6 is J1, i.e. optical depth τ = αa.** Force depends on J1, not on J1/A. T6's baseline (a = 5 µm, α = 3×10⁵ m⁻¹, τ = 1.5) gives J1 = 0.153, and the mote is *half-transparent*. Making the same carbon aerogel **a = 15 µm (τ = 4.5)** gives J1 = 0.34 and **FOM·A 1.75 → 3.9** from the same bulk numbers. That is 2.2× lower I_hold, and it reaches the FOM ≥ 4 gate with a *measured material class* and no unmade composite. [THEORY on measured-class inputs; the τ-dependence reproduces T6's own J1/A at τ = 1.5 and 3 (0.186, 0.293 vs T6's 0.2, 0.30)]
3. **Bigger motes also fix the light budget.** Scattered visible power per mote scales with a². At a = 15 µm a *black* carbon mote needs 0.14–0.7 W visible total at film density, versus 1.2–6 W at a = 5 µm. That removes the need for the white coat, and the white coat is **thermally harmful** (Section 2.3). [ESTIMATE]
4. **Heat, not laser power, is what stops large motes in drafts.** ΔT = A·a·I/(4k_g) grows with a. The largest tolerable air speed (ΔT ≤ 250 K, oxidation margin) is about 0.17 m/s at a = 15 µm and about 0.36 m/s for a = 5 µm, 0.2 g/cc carbon aerogel. Operating points are in Section 4. [ESTIMATE]
5. **Killed with numbers** (Section 5): Er³⁺ upconversion of the trap light (3 nW vs ≥150 nW needed), visible trap beams (Rayleigh streaks ≈ 25× the image flux), hollow carbon microspheres (shell conduction adds k ≈ 0.2–0.5), Cs_xWO₃/LaB₆/ITO composites at τ ≥ 3 (need ≥ 8 vol%), dense white shells (lateral-conduction shorting), third-harmonic conversion (I² scaling).
6. **Hardware:** nothing in 2026 gives 10⁸–10⁹ modes at kHz in one device. The best single-device rate is about 1.4×10¹⁰ pixel/s (ferroelectric LCoS or DMD, binary), against about 5×10¹² pixel/s for a full 5×10⁸-mode refresh at 10 kHz (400× short). The way out is *fewer modes*, not faster ones: with a curtain-allowed 20–40 mW per focus and a 0.25 m² field per head, M ≈ 1–3×10⁷ per head, i.e. one to four 4K LCoS per head with a DMD doing the kHz gating.

---

## 1. Mote materials

### 1.1 The exact force factor (derivation, used throughout) [THEORY]

For heat source q(r,θ) = q₁(r) cosθ inside a sphere (conductivity k_p) in gas k_g, the l = 1 surface temperature is T_s = B cosθ / a², with

  **B = S_q / (k_p + 2k_g)**, S_q = ∫₀^a q₁ s³ ds = (3/4π) ∫ q z dV.

Define J1 = S_q/(I a³) = 3D/(4π I a³), where D = ∫ q z dV is the heating dipole. An opaque front-surface absorber gives J1 = 0.5. Then I_hold ∝ (k_p + 2k_g)/J1 = 1/(FOM·A). The B2 formula's "FOM·A" is J1/(k_p+2k_g); T6's "FOM" is that divided by A.

For a straight-ray volume absorber (aerogel n ≈ 1.05–1.2, scattering neglected), numerical integration gives:

| τ = αa | 0.5 | 1 | 1.5 | 2 | 3 | 4.5 | 6 | 10 | ∞ |
|---|---|---|---|---|---|---|---|---|---|
| A | 0.47 | 0.70 | 0.82 | 0.89 | 0.95 | 0.98 | 0.99 | 0.995 | 1 |
| J1 | 0.034 | 0.094 | 0.153 | 0.203 | 0.277 | 0.342 | 0.378 | 0.426 | 0.5 |
| J1/A | 0.07 | 0.13 | 0.19 | 0.23 | 0.29 | 0.35 | 0.38 | 0.43 | 0.5 |

**Calibration of I_hold** to the brief's own two worked examples (4×10⁶ and 1×10⁶ W/m²): I_hold ≈ **3.0×10⁷ · h · w / (FOM·A)** W/m², w in m/s. [ESTIMATE; assumes A ≈ 1 in the brief's examples.]

**A shell or skin does not help** (checked, so nobody should chase it): a layer of conductivity k_s and thickness t on a core k_c adds lateral conduction, giving k_eff ≈ k_c + 2k_s t/a. A "carbon-black skin on silica aerogel" with t = 2.7 µm, k_s = 0.1 on a = 5 µm gives k_eff ≈ 0.12 vs 0.05 for uniform 0.2 g/cc carbon aerogel. [THEORY] So a graded or core-shell mote loses to a uniform optically thick aerogel.

### 1.2 Measured data I could find (inputs)

| Quantity | Value | Tag |
|---|---|---|
| Silica aerogel k at 1 atm | 0.017 → 0.0135–0.014 W/m/K with 9 wt% carbon black. One review snippet also says "best aerogels < 4 mW/m/K at atmospheric pressure of air"; I could not verify that and treat it as a vacuum-class number. If it were real the ceiling would be 0.5/(0.0524+0.004) ≈ 8.9. | [MEASURED+Thapliyal 2014 review; carbon-opacified silica aerogel papers; the 4 mW/m/K claim is UNVERIFIED] |
| Carbon aerogel k at room temperature | 0.048 W/m/K (one recent value; density not stated in snippet); fibre-reinforced aerogel composites 0.015–0.030 | [MEASURED+search snippets] |
| Carbon aerogel mass extinction (ultrafine powders) | 2.62 m²/g (3–5 µm band), 1.23 m²/g (8–14 µm); "specific extinction > 1000 m²/kg" | [MEASURED+*J. Non-Cryst. Solids* 2024 (carbon aerogel ultrafine powders), *J. Phys. Chem. C* 2024] |
| Carbon aerogel at 1.55 µm | **no direct value found**. If extinction follows the soot-like λ⁻¹ law, 3–6 m²/g | [ESTIMATE] |
| Black carbon MAC | 7.5 ± 1.2 m²/g at 550 nm (Bond & Bergstrom); recent 8.0 ± 0.7; AAE ≈ 1.1 (diesel) to 2.1 (spark) → **≈ 2.7 m²/g at 1550 nm for AAE = 1** | [MEASURED+ACP / Aerosol Sci. Technol. 2019 review] |
| Carbon aerogel ρ = 0.1 g/cc → α | 3×10⁵ m⁻¹ at e = 3 m²/g; T6 used the same | [ESTIMATE, consistent with T6] |
| Carbon aerogel microspheres, size | emulsion route gives 2–50 µm; RF aerogel microparticles 10–500 µm; organic aerogel microspheres 1 µm–3 mm; aerogel microparticles 0.8–1.5 µm exist | [MEASURED+SciDirect/PMC/patent snippets] |
| Carbon-nanoparticle agglomerates photophoretically trapped in air | 0.1–10 µm agglomerates, laser power < 1 mW, trapped to ±2 µm (transverse and longitudinal) with counter-propagating vortex beams, accelerated to 1 cm/s | [MEASURED+Shvedov, Desyatnikov et al., *Opt. Express* 2009] |
| Cs₀.₃₃WO₃ absorption | "1 mg/cm² shields > 75 % of NIR heat radiation" → effective mass extinction ≈ ln(4)/(0.01 kg/m²) ≈ 140 m²/kg, broad-band; ≈ 3× higher at the peak | [MEASURED+*Nanoscale Res. Lett.* 2013 snippet; the conversion is mine] |
| ITO nanocrystal LSPR | peak tunable 1600–2250 nm with Sn doping; scattering negligible below ≈ 100 nm | [MEASURED+*J. Phys. Chem. C*, Milliron-group snippets] |
| ITO mass extinction at 1550 nm | ≈ 1 m²/g | [ESTIMATE from Drude/Q ≈ 5; **not** a measured value] |
| LaB₆ | absorption peak near 1000 nm, falls toward 1550 nm | [MEASURED+snippet] |

**Cross-check on the force itself (weak):** Shvedov's carbon clusters moved at ~1 cm/s at < 1 mW. If the spot was 25–50 µm (not in the snippet), I ≈ 0.5–1.3×10⁵ W/m², giving FOM·A ≈ K·h·w/I ≈ 0.6–2.3. That is within a factor of ~4 of my soot-aggregate row (FOM·A ≈ 1.95). [ESTIMATE, beam geometry assumed]

### 1.3 Candidate table (computed; k_g = 0.0262, h = 1.38 (M4 layout H10 mean), w = 0.1 m/s)

| Candidate | a (µm) | α (m⁻¹) | τ | J1 | J1/A | k_p | FOM | **FOM·A** | I_hold (W/m²) | ΔT (K) | w_max at ΔT=250 K |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Carbon aerogel 0.1 g/cc (T6 baseline) | 5 | 3×10⁵ | 1.5 | 0.153 | 0.19 | 0.035 | 2.1 | **1.75** | 2.4×10⁶ | 94 | 0.27 |
| same | 10 | 3×10⁵ | 3.0 | 0.277 | 0.29 | 0.035 | 3.4 | **3.2** | 1.3×10⁶ | 119 | 0.21 |
| same | **15** | 3×10⁵ | 4.5 | 0.342 | 0.35 | 0.035 | **4.0** | **3.9** | 1.07×10⁶ | 149 | 0.17 |
| same | 20 | 3×10⁵ | 6.0 | 0.378 | 0.38 | 0.035 | 4.4 | 4.3 | 0.97×10⁶ | 182 | 0.14 |
| Carbon aerogel 0.2 g/cc | **5** | 6×10⁵ | 3.0 | 0.277 | 0.29 | 0.05 | 2.9 | **2.7** | 1.55×10⁶ | 70 | **0.36** |
| same | 10 | 6×10⁵ | 6.0 | 0.378 | 0.38 | 0.05 | 3.8 | 3.7 | 1.13×10⁶ | 106 | 0.23 |
| Carbon aerogel 0.1 g/cc, k_p = 0.02 (optimistic) | 15 | 3×10⁵ | 4.5 | 0.342 | 0.35 | 0.02 | 4.8 | 4.7 | 0.89×10⁶ | 124 | 0.20 |
| Carbon-black silica aerogel, **9 wt% CB** (the measured k = 0.014 material) | 15 | 3.2×10⁴ | 0.48 | 0.031 | 0.07 | 0.014 | 1.0 | **0.47** | 8.8×10⁶ | 579 | 0.04 |
| CB silica aerogel, 25 wt% (k_p ≈ 0.02 assumed) | 15 | 1.1×10⁵ | 1.65 | 0.169 | 0.20 | 0.02 | 2.8 | 2.3 | 1.8×10⁶ | 217 | 0.12 |
| CB silica aerogel, 25 wt% | 20 | 1.1×10⁵ | 2.2 | 0.221 | 0.24 | 0.02 | 3.4 | 3.1 | 1.4×10⁶ | 237 | 0.11 |
| Soot / char open aggregate (k_p ≈ k_g) | 10 | 1.5×10⁵ | 1.5 | 0.153 | 0.19 | 0.026 | 2.4 | 1.95 | 2.1×10⁶ | 168 | 0.15 |
| Cs₀.₃₃WO₃ 5 vol% in aerogel (MEC 400 m²/kg, k_p 0.06 assumed) | 10 | 1.4×10⁵ | 1.4 | 0.137 | 0.17 | 0.06 | 1.5 | 1.2 | 3.4×10⁶ | 260 | 0.10 |
| ITO 8 vol% in aerogel (MEC 1 m²/g, k_p 0.07 assumed) | 5 | 5.7×10⁵ | 2.9 | 0.268 | 0.29 | 0.07 | 2.3 | 2.2 | 1.9×10⁶ | 86 | 0.29 |

Sensitivities that matter more than k_p:
- **α(1.55 µm).** At a = 15 µm, α = 1.5×10⁵ → FOM·A ≈ 2.5; α = 6×10⁵ → 4.6. At a = 5 µm, α = 1.5×10⁵ → FOM·A ≈ 0.7 (the 5 µm mote is the fragile one). [THEORY]
- **k_p** (0.02–0.05) changes FOM·A by only ±15 %.

Ranking by what is already measured:
1. **Carbon aerogel, 0.1–0.2 g/cc, a = 10–15 µm** (all inputs are bulk-measured class; the only unmeasured items are α(1.55 µm) and k_p at µm size, both cheap to measure, Section 6).
2. Carbon-black silica aerogel at ≥ 25 wt% (k stays ≈ 0.02, but needs 3–4× more absorber than the measured 9 wt% grade, and the 9 wt% grade is optically **thin** at µm size: FOM·A = 0.47).
3. Soot or char agglomerate (measured to trap, FOM·A ≈ 2 at a = 10 µm; fragile, fractal, k_p ≈ k_g because pores are > mean free path).
4. ITO / Cs₀.₃₃WO₃ / LaB₆ composites: **no advantage in FOM** (mass extinction 3–20× below carbon, so they need 8–50 vol% filler and a stiffer network). Their only advantage is visible transparency, which matters only if a phosphor is wanted.

### 1.4 Hollow carbon microspheres: killed [THEORY + ESTIMATE]

An air-filled sealed shell has k_p = k_g exactly (ceiling 6.4), which is good. But a shell thick enough to absorb (αt ≈ 3, α ≈ 6.5×10⁶ m⁻¹ for dense amorphous carbon, so t ≈ 0.46 µm) adds lateral conduction 2k_s t/a: for k_s = 1, 3, 0.2 W/m/K that is +0.18, +0.55, +0.037 on a = 5 µm. Only k_s ≲ 0.2 (carbon-black-class porous shell) survives, and then the shell is just a thin aerogel. A thin shell (αt ≈ 1) also absorbs on both front and back walls, so J1 ≈ 0.2.

### 1.5 µm-scale thermal conductivity

No measurement of k for an individual µm aerogel particle in air exists in what I found. Physics: pores are 20–100 nm (Kn_pore ~ 1), so gas conduction inside is already Knudsen-reduced to ~0.006–0.012, the same as in the bulk. A 10–30 µm particle contains ≥ 100 pore diameters, so bulk k_p should carry over to ±30 % [ESTIMATE]. The outside gas film has Kn = λ/a = 0.068/a(µm): the temperature-jump correction to 2k_g is ≲ 15 % at a = 1 µm and ≲ 3 % at 5 µm [THEORY], so no loophole there either.

---

## 2. Light generation without per-mote pump focusing

### 2.1 Terminated visible scatter: the budget depends on a² [ESTIMATE]

Film-density flux (T6/B7): 0.66 lm / 15,000 motes = 44 µlm per mote. Needed scattered flux per mote = ρ_alb · E · πa².

| Mote | albedo | E at mote | visible per mote (r_v = 40 µm) | total, 15,000 motes (555 nm equivalent) |
|---|---|---|---|---|
| a = 5 µm | 0.05 | 1.1×10⁷ lux | 83 µW | **1.2 W** (matches T6's 1.4 W) |
| a = 5 µm | 0.01 (super-black) | 5.6×10⁷ lux | 410 µW | 6.2 W |
| a = 15 µm | 0.05 | 1.2×10⁶ lux | 9 µW | **0.14 W** |
| a = 15 µm | 0.01 | 6.2×10⁶ lux | 46 µW | 0.69 W |

Carbon aerogel is *super-black* (low-density carbon aerogels with subwavelength structure are reported with sub-percent reflectance [MEASURED+*Adv. Mater.* snippet, value not read]), so plan for albedo 0.01–0.05. With a = 15 µm that is still < 1 W total, and each visible beam carries ≤ 46 µW, below the 0.39 mW Class 1 level at 500–700 nm. [ESTIMATE; verify the AEL]

Why there is no streak or wall-glow problem: Rayleigh scatter of a 9–46 µW visible beam over 2 m is β_R·P·L = 1.2×10⁻⁵ m⁻¹ × 46 µW × 2 m ≈ 1 pW per beam; ×10⁴ beams = 10 nW. Dust at 10–100× Rayleigh gives ≤ 1 µW, which is < 10⁻⁵ of the image flux. [ESTIMATE]

### 2.2 Self-aligned pumping options (what is real)

| Option | Verdict |
|---|---|
| **A. Trap light as the visible source** (use a 520 nm trap) | **Killed.** 3500 simultaneous 50 mW visible beams of 2 m path scatter 3500 × 50 mW × 1.2×10⁻⁵ × 2 = **4.2 mW** of Rayleigh light into the room; the whole sketch image flux is 0.11 lm ≈ 0.16 mW. Streaks are ~25× brighter than the image (more with dust). Also Class 1 at 520 nm is ≈ 0.4 mW per focus vs 10 mW at 1550 nm. [ESTIMATE] |
| **B. Upconversion of the 1550 nm trap light** (Er³⁺) | **Killed.** Best measured β-NaYF₄:25 % Er³⁺ external UCQY = 8.6 % at ≥ 3.5×10³ W/m² [MEASURED+Fischer/Goldschmidt/Richards 2014 snippet], and the trap intensity (10⁶ W/m²) is far above saturation, which is good. But the absorption: N_Er ≈ 3×10²¹ cm⁻³, σ(1523 nm) ≈ 2×10⁻²¹ cm² [ESTIMATE, literature order of magnitude] → α = 600 m⁻¹, αa = 3×10⁻³ at a = 5 µm. Visible output ≈ I·πa²·αa·UCQY·(visible fraction ≈ 0.3)·(λ ratio 0.42) ≈ **3 nW per mote, vs ≥ 70–150 nW needed**, and that is for a *pure* UC mote that would absorb 0.3 % and have no photophoretic force. With a carbon absorber present, carbon takes ≈ 10³× more of the 1550 nm photons than Er. [THEORY+MEASURED] |
| **C. Second harmonic / third harmonic of the trap light** | **Killed.** χ⁽³⁾ conversion scales with I²; at 10⁶ W/m² the efficiency is ~10⁻¹⁵ or lower. [THEORY] |
| **D. Thermal glow** | **Killed.** T ≈ 400–450 K; blackbody visible fraction ≈ 10⁻²⁰. [THEORY] |
| **E. Same SLM drives IR and visible** | Real but not a loophole. A hologram computed for 1550 nm puts the visible spot at 0.335× the lateral coordinate; interleave pixels (cost: half the pixels) or use a visible SLM fed with the same mote list. The tracker already supplies the common frame. [THEORY] |

### 2.3 "IR-black, visible-white" coatings: the thermal shorting problem [THEORY]

A dense scattering shell of conductivity k_s and thickness t shorts the asymmetry by k_eff = k_c + 2k_s t/a. For TiO₂ pigment film (k_s ≈ 0.2) a 3 µm shell on a = 8 µm adds 0.15 W/m/K, which kills FOM·A (3.9 → ≈ 1.8). The shell budget is k_s t/a ≲ 0.01–0.02 W/m/K: at k_s = 0.2 that is t ≲ 0.35 µm, which gives albedo ≲ 0.1–0.15. T6's "white-coated carbon mote: FOM 3.4, albedo 0.3" is therefore optimistic unless the coat is itself an aerogel-density TiO₂ foam (k_s ≈ 0.03–0.05 [ESTIMATE], t ≈ 1.5 µm). **The cleaner fix is the a² scaling above: a larger black mote needs no coat.**

### 2.4 One new light-source loophole I could not kill [SPECULATIVE]

A phosphor *shell* is not needed if the illumination can be efficient enough. The residual lever is the **visible spot size r_v**, which is only bounded by wall glow after termination. A larger r_v (100 µm) costs (r_v/40 µm)² = 6× more visible power but lets the visible hologram be coarse (fewer modes, no fast loop). At a = 15 µm, albedo 0.05, r_v = 100 µm: 0.9 W. This is the cheapest way to take the visible channel off the critical path.

---

## 3. Hardware in 2026

All specs below are from search snippets unless marked; pricing for most research SLMs is quote-only.

### 3.1 Phase and amplitude modulators

| Device | Pixels | Pitch | Rate | At 1550 nm | Price / access | Tag |
|---|---|---|---|---|---|---|
| **Holoeye GAEA-2.1 (LCoS 4K, phase)** | 3840×2160 (max 4160×2464 = 10.2 Mpx) | 3.74 µm | 60 Hz native, 180 Hz with colour-field-sequential tricks | "GAEA-2-TELCO-033" covers 1400–1700 nm, 2π at ≥ 1550 nm | quote only (Elliot Scientific, Axiom list "contact us") | [MEASURED+Holoeye/Axiom] |
| 8K phase LCoS | none commercial found | | | | | [MEASURED+search: absence] |
| **TI PLM (DLP6750 EVM, 0.67")** | 1358×800 (1.09 Mpx) | 10.8 µm | 720 Hz (HDMI), 1440 Hz (DisplayPort); 5.76 kHz potential; 95 % fill | 4-bit (16 levels); visible-designed: single-pass phase depth 0.8π at 1550 nm, **double-pass trick gives 1.6π and 30 % diffraction efficiency** demonstrated for beam steering; optics-enhanced design claims ~99 % at ideal quasi-blaze | EVM only by TI email invitation | [MEASURED+Photonics 2022 / *Micromachines* 2022 snippets] |
| **Fraunhofer IPMS MEMS piston SLM** | 2048×512 (1.05 Mpx); 240×200 at 40 µm earlier | 16 µm | analog, up to 2 kHz (3.6 kHz backplane); 2026 press release claims "many millions of pixels at several kHz" for holography | DUV–NIR platform; 1550 nm needs ≈ 775 nm stroke vs 400 nm shown at 40 µm pitch | research / custom | [MEASURED+IPMS snippet; stroke at 1550 is [ESTIMATE]] |
| **ForthDD / Kopin QXGA-3DM (ferroelectric LCoS, binary phase)** | 2048×1536 (3.1 Mpx) | 8.2 µm | 4.5 kHz (1024 bit planes) | optimised 430–750 nm; no 1550 nm part found | quote | [MEASURED+photonics.com] |
| **TI DLP650LNIR (DMD, amplitude)** | 1280×800 (1.02 Mpx) | 10.8 µm, ±12° | **12.5 kHz binary**; 1.56 kHz 8-bit | 850–2000 nm window, > 93 % window transmission; mirror 0.94 × 0.88 × 0.94 at 1064 nm; array rated to ~160 W incident | EVM $2,799–3,709 (the DLPLCR65NEVM listing; check it is the NIR part) | [MEASURED+TI/Mouser/DigiKey snippets] |

Pixel rates (pixels × frame rate; binary hologram pixels carry less than one mode each):

| Device | px/s |
|---|---|
| 4K LCoS at 60 Hz / 180 Hz | 5×10⁸ / 1.5×10⁹ |
| TI PLM at 1.44 kHz / 5.76 kHz | 1.6×10⁹ / 6.3×10⁹ |
| IPMS 2048×512 at 2 kHz | 2.1×10⁹ |
| ForthDD QXGA at 4.5 kHz | 1.4×10¹⁰ |
| DLP650LNIR at 12.5 kHz | 1.3×10¹⁰ |
| **Needed for a full 5×10⁸-mode refresh at 10 kHz** | **5×10¹²** (400× the best) |

Consequences [THEORY]:
- A binary-amplitude DMD hologram sends ≤ 1/π² = 10 % into each first order (binary phase 0/π: 40.5 % into each of ±1, with a twin image to be terminated). The DMD is a **gate**, not a hologram engine, as T6 says.
- LCoS power handling at 1550 nm is not published for GAEA. A 4K panel is 15.6 × 9.2 mm = 1.4 cm²; if the limit is a few W/cm², 75 W of IR needs ≥ 10 panels purely for thermal reasons. That coincides with the pixel-count need, which is a useful coincidence. [ESTIMATE; **must be verified with vendors**]
- The PLM and IPMS parts are the only kHz *phase* modulators with ≥ 1 Mpx; both need 1550-nm-specific stroke (double-pass or custom).

### 3.2 Lasers

| Item | Spec | Tag |
|---|---|---|
| IPG ELM / ELR erbium single-mode CW | 1–100 W class | [MEASURED+IPG page title] |
| Amonics AFL-1550-50-R | up to 50 W; 30 W also listed for the AFL series | [MEASURED+findlight snippet] |
| 50 W 1550 nm fibre laser | listed by laserlabsource | [MEASURED+snippet, price not shown] |
| > 100 W Er fibre | published research (1480 nm Raman core-pumped) | [MEASURED+ResearchGate title] |
| Price per 50–100 W | not found. [ESTIMATE $40–150 k each] | |

A single 100 W SM source is not available off the shelf from what I found. **Plan on 2 × 50 W or 4 × 25 W**, which costs nothing in physics because spots are formed on separate SLMs per head anyway.

### 3.3 Tracking 10⁴ motes at ≥ 20 kHz (the sensing gap)

Required sample rate: 10⁴ × 2×10⁴ = **2×10⁸ position samples/s**, at ~10–20 µm accuracy over a 0.5 m field (5×10⁴ resolvable positions per axis).

| Sensor | Numbers | Verdict |
|---|---|---|
| Sony/Prophesee IMX636 event sensor | 1280×720, 4.86 µm pixel, **1 Gev/s peak**, latency ≤ 100 µs at 1000 lux; LUCID Triton2 EVS ">10,000 fps-equivalent"; Si, so visible/< 1 µm light only | [MEASURED+Prophesee/LUCID] |
| High-speed InGaAs | Sensors Unlimited 640×512 at 880 fps; C-RED 2 Lite 600 fps full frame, 32 kHz in 32×4 window; NiT WiDy 320 at 10 kHz ROI; Raptor OWL 640 from $9,999 | [MEASURED+snippets] |
| SWIR event camera | none found | [MEASURED+absence in search] |

Arithmetic [ESTIMATE]:
- **InGaAs cannot do this**: full-frame pixel rate ≈ 2×10⁸ px/s (600 fps × 3.3×10⁵), but the 10⁴ points are sparse and the windows rectangular, so you get 10 kHz only for a few windows.
- **Event camera on the visible scatter** (the motes are lit by visible light anyway): 10⁴ motes × 2×10⁴ Hz × ~5 events/sample = 10⁹ ev/s, i.e. at the limit of *one* sensor. Splitting the field over 8–12 cameras (each covering 0.15–0.25 m, 0.1–0.2 mm per pixel) brings it down to ~10⁸ ev/s each and sub-pixel centroiding at 1/10 pixel gives ±10–20 µm. Open risks: event latency rises at low light, and the scatter spots are dim (10–46 µW into a 40 µm spot is fine, but the camera sees ~pW per pixel at 0.5 m).
- **Frequency-division tagging** (each spot intensity-modulated at its own carrier, one large photodiode, digital down-conversion): 10⁴ tones × 5 kHz spacing = 50 MHz bandwidth, ~10¹² MAC/s on a Versal-class FPGA. [SPECULATIVE; DMD gating at 12.5 kHz cannot make 50 MHz tones, so this needs a second modulator, e.g. AOM array or direct laser-diode modulation per spot]

---

## 4. System numbers with the new motes (sketch, N = 2500, h = 1.38, field 0.25 m² per head)

I_hold from the calibration in §1.1; total IR = N·I_hold·πr_c²; modes per head M = A_f/(πr_c²). Caps: IR ≤ 100 W, ΔT ≤ 250 K. r_c ≥ 72 µm is the T6 jitter bound at 0.3 m/s with a 2 kHz loop; for 0.1 m/s r_c ≥ ~24 µm is enough.

| Mote | w (m/s) | I_hold (W/m²) | ΔT (K) | r_c (µm) | P per focus (mW) | Total IR (W) | M per head | OK? |
|---|---|---|---|---|---|---|---|---|
| CA 0.1 g/cc, a = 5 (T6 baseline) | 0.10 | 2.4×10⁶ | 94 | 72 | 39 | 97 | 1.5×10⁷ | marginal |
| CA 0.1 g/cc, a = 5 | 0.30 | 7.2×10⁶ | 281 | any | | 141–497 | | **no (heat)** |
| **CA 0.1 g/cc, a = 15** | 0.10 | 1.07×10⁶ | 149 | 94 | 30 | **74** | 9×10⁶ | yes |
| same | 0.10 | | | 72 | 17 | **44** | 1.5×10⁷ | yes |
| same | 0.15 | 1.6×10⁶ | 224 | 72 | 26 | 65 | 1.5×10⁷ | yes (tight heat) |
| same | 0.30 | 3.2×10⁶ | 448 | any | | 63–223 | | **no (heat, oxidation)** |
| **CA 0.2 g/cc, a = 5** | 0.10 | 1.55×10⁶ | 70 | 72 | 25 | 63 | 1.5×10⁷ | yes |
| same | 0.15 | 2.3×10⁶ | 105 | 72 | 38 | 95 | 1.5×10⁷ | yes |
| same | **0.30** | 4.6×10⁶ | **209** | 50 | 37 | **91** | 3.2×10⁷ | **yes, if the fast loop supports r_c = 50 µm (≥ 3 kHz)** |
| same | 0.30 | | | 72 | 76 | 189 | 1.5×10⁷ | no (cap) |
| CA 0.2 g/cc, a = 10 | 0.15 | 1.7×10⁶ | 160 | 72 | 28 | 69 | 1.5×10⁷ | yes |

Reading:
- **Quiet or calm room, sketch:** a made-class carbon aerogel gets 44–95 W and 1–3×10⁷ modes per head, i.e. one to four 4K LCoS per head. T6 reached the same region only with the *unmade* ITO mote (FOM 5.3) and a larger pixel count (5×10⁸ total).
- **Normal room (0.3 m/s):** only the small dense mote (0.2 g/cc, a = 5 µm) fits under the heat cap, at ~90 W with r_c = 50 µm. That is *equal* to T6's unmade ITO result (163–176 W) within the uncertainty on α. It leaves **no margin for hand-occluded heads** (h_worst up to 4.5 would need ΔT ≈ 680 K), so near hands the voxel drops out. The honest statement: normal-room operation is thermally marginal for *any* optically absorbing mote in the 1550 nm photophoretic scheme.
- **Film density (10⁴ motes):** at 0.1 m/s with a = 15 µm: 10⁴ × 17 mW (r_c = 72) = 175 W; at r_c = 94 µm 300 W. Needs the cap raised or δ opened to 3–4 mm.
- **Sedimentation is not an issue:** gravity on a 15 µm, 100 kg/m³ mote is 2.3×10⁻¹¹ N vs 5×10⁻¹⁰ N Stokes drag at 0.1 m/s (~5 %). [THEORY]
- **Respirability:** aerodynamic diameter d_ae = d·√(ρ/ρ₀): 30 µm at 0.1 g/cc → 9.5 µm (PM10 border); 10 µm at 0.2 g/cc → 4.5 µm (respirable fraction). Total mass at film density is 21 µg (a = 15) or 0.8 µg (a = 5). [THEORY] This is a regulatory/health note, not a showstopper.

---

## 5. Things I checked and killed (with the number that kills them)

| Idea | Killer number |
|---|---|
| Er³⁺ upconversion of the trap light into visible | ~3 nW per mote vs ≥ 70–150 nW needed; σ_abs·N·a = 3×10⁻³ |
| Visible-wavelength trap beams | 4.2 mW of Rayleigh scatter vs 0.16 mW of image flux (sketch) |
| 3rd-harmonic of the trap light | ∝ I², ~10⁻¹⁵ at 10⁶ W/m² |
| Hollow carbon microspheres | shell lateral conduction adds +0.04 to +0.55 W/m/K vs 2k_g = 0.052 |
| Core-shell or graded skin-on-aerogel mote | k_eff = k_c + 2k_s t/a; a 2.7 µm carbon skin on a 5 µm mote gives 0.12 vs 0.05 for uniform |
| Dense white (TiO₂) coat on carbon aerogel | k_s t/a must be ≲ 0.02; allows t ≲ 0.35 µm ⇒ albedo ≲ 0.1–0.15 |
| Cs₀.₃₃WO₃ / LaB₆ / ITO as the absorber at τ ≥ 3 | need ≥ 8 vol% (ITO) to ≥ 50 vol% (Cs₀.₃₃WO₃ at 140 m²/kg broad-band) for α = 6×10⁵ m⁻¹ |
| Silica aerogel at 9 wt% carbon black as the µm mote | τ = 0.5, FOM·A = 0.47, ΔT ≈ 580 K |
| Thermal transpiration through mote pores as extra thrust | momentum flux ρv²A ≈ 10⁻¹² N vs drag 10⁻⁹ N |
| Passive dark-core (vortex) traps to drop the fast loop | transverse photophoretic force ≈ F_axial·(a/δ_wall); needs wall sharpness ≈ a ⇒ M ≈ 10²× more. **B6 as stated by the brief is right.** [THEORY] |
| Larger FOM from a better mote alone | ceiling FOM·A ≤ 8.0 (k_p = 0.01) or 6.4 (sealed air shell) |
| Co-moving the mote with the draft | the force needed is drag on the *relative* velocity; the image must stay at fixed lab positions |
| "Mote rain" (flow-carried motes, z set by flash timing) | a top-down beam lights *all* motes in a column; no z selectivity without per-mote spatial gating [SPECULATIVE, abandoned] |

---

## 6. Cheapest decisive measurements (nothing else in this report is as informative per dollar)

1. **Measure FOM·A directly.** Carbon aerogel microspheres from the emulsion RF route are known in the 2–50 µm range. Put them in a still-air cell (the same physics the product uses), push with a 1550 nm diode/fibre laser, record terminal velocity vs intensity:
   FOM·A = K·h·w/I with K ≈ 3×10⁷ (recalibrate with a graphite-flake control). At w = 1 cm/s and FOM·A = 4, I ≈ 7.5×10⁴ W/m²; a 50 µm spot needs ≈ 0.15 mW. Vary a (5, 10, 15, 20 µm) to test the J1(τ) curve in §1.1: if FOM·A rises 1.75 → 3.9 from a = 5 to 15 µm, the main claim of this report is confirmed. [ESTIMATE]
2. **α(1.55 µm)** of the same powder via an integrating sphere on a thin pressed film, or from the transmission of an aerogel monolith at the same density. This is the largest uncertainty (±2× in FOM·A at a = 5 µm).
3. **Visible albedo** of single particles (dark-field scatter at 520 nm), to fix the 0.01–0.05 range in §2.1.
4. **Ceiling check:** repeat with a silica aerogel microsphere carbon-doped to τ ≥ 3 (≥ 40 wt% CB or a ≥ 30 µm sphere), which isolates the k_p effect from the J1 effect.
5. **LCoS power handling at 1550 nm** (vendor call): decides whether 75–100 W of IR needs 10 panels or 40.

---

## 7. Side notes on the safety candidate (not my assignment, one number)

IEC 60825-1 uses a **1 mm** measurement aperture for 1400 nm and above when t < 0.35 s (not 3.5 mm), so the short-exposure corneal limit at 1550 nm is ≈ 10⁴ J/m² × π(0.5 mm)² ≈ **7.9 mJ**, not 9.6 mJ. The 70 µJ curtain dose still has a 100× margin; 140 µJ (100 mW × 1.4 ms) has 56×. [THEORY from memory of the table: please verify against the standard text.]

---

## 8. Top 5 (ranked by expected impact × probability it is real)

| # | Idea | What it fixes | Key number | Probability real | Biggest risk |
|---|---|---|---|---|---|
| 1 | **Optically thick carbon-aerogel mote: choose a and density for τ = αa ≥ 3–4** (a = 10–15 µm at 0.1 g/cc for quiet rooms; a = 5 µm at 0.2 g/cc for normal rooms) | Blocker 1 (material gate) from bulk-class data; B2 (I_hold ÷ 2.2); B7 (a² cross-section); no white coat | **FOM·A 1.75 → 3.9** (a = 5 → 15 µm); sketch in a 0.1 m/s room 44–74 W | **0.50** | α(1.55 µm) of carbon aerogel is not measured (±2×) and k_p at µm size is unmeasured; ΔT ∝ a caps w at 0.17–0.36 m/s; hands and occluded heads overheat the mote |
| 2 | **Right-sized split architecture**: curtain-allowed 20–40 mW per focus, per-head field 0.25 m², IR via 1–4 LCoS 4K per head, DMD (12.5 kHz) as per-spot gate | B5/B6 hardware: M from 5×10⁸ total to 1–3×10⁷ per head; B4 via the curtain | 44–95 W, M = 1.5×10⁷ per head, DMD 1.02 Mpx for 2500 spots (400 px each) | **0.40** | LCoS 1550 nm power density unpublished (maybe 4× more panels); LoS ambiguity when strokes point at a head; curtain latency and certification |
| 3 | **Event-camera tracking on the visible scatter, 8–12 sub-field cameras** (plus per-spot lock-in as a fallback) | The unsolved ≥ 20 kHz per-mote sensing | 2×10⁸ samples/s, ≤ 10⁹ ev/s per sensor; ±10–20 µm at 0.1–0.2 mm px with 1/10-pixel centroiding | **0.35** | Event latency at low light (≤ 100 µs is quoted at 1000 lux); sub-pixel accuracy; calibration across 10 cameras; no SWIR event camera exists |
| 4 | **Large black mote + terminated visible scatter** (no phosphor, no white coat, coarse visible hologram with r_v ≈ 100 µm) | B7 light budget; removes the white-coat FOM penalty; takes the visible channel off the critical path | 0.14–0.9 W visible at film density (vs 1.2–6 W at a = 5 µm); Rayleigh/dust streaks < 10⁻⁵ of image flux | **0.55** | Albedo of µm carbon aerogel may be < 1 % (×5 power); wall glow from receiver leakage (T6's gap 1) is unchanged |
| 5 | **TI PLM or IPMS MEMS piston SLM as the kHz phase engine at 1550 nm** (double-pass 1.6π, 30 % demonstrated) | Content speed of hologram-steered voxels (0.3–2 → ≈ 4.5 cm/s at 1.44 kHz, r_c = 94 µm); partly the POV/discrete-step issue | 1.1 Mpx × 1.44–5.76 kHz = 1.6–6×10⁹ px/s | **0.20** | PLM available only by invitation, 4-bit phase, 30 % efficiency at 1550; IPMS stroke at 1550 nm needs a custom run; still ≥ 100× short of a full-field kHz refresh |

**Honest summary for the verdict.** Materials alone give about 2× (not 10×) on I_hold, and the ceiling FOM·A ≤ 8 is set by room air. The route is plausible for **quiet or calm rooms and sketch-level content**, and still marginal in a normal room because of heat rather than power. The two items I cannot close from desk research are α(1.55 µm) for carbon aerogel and the per-mote sensing architecture; neither is a physics blocker, both are bench measurements.

---

## 9. Sources (search snippets only, not read in full)

- Thapliyal et al., *Aerogels as Promising Thermal Insulating Materials: An Overview*, J. Materials 2014: https://onlinelibrary.wiley.com/doi/10.1155/2014/127049
- Carbon aerogel ultrafine powders, IR extinction: https://www.sciencedirect.com/science/article/abs/pii/S0022309324000760 ; https://pubs.acs.org/doi/10.1021/acs.jpcc.4c07463
- Carbon-aerogel high-temperature insulation (Wiener et al.): https://link.springer.com/article/10.1007/s10765-009-0595-1
- Carbon-black-opacified silica aerogels: https://www.sciencedirect.com/science/article/abs/pii/S0017931017321877 ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9141137/
- Super-black low-density carbon aerogel: https://pubmed.ncbi.nlm.nih.gov/27588433/
- Carbon aerogel microspheres: https://www.sciencedirect.com/science/article/abs/pii/S0022309310008653 ; https://www.sciencedirect.com/science/article/abs/pii/S0008622303004950
- Black carbon MAC and AAE: https://www.tandfonline.com/doi/full/10.1080/02786826.2019.1676878 ; https://acp.copernicus.org/articles/18/6259/2018/
- ITO nanocrystal LSPR: https://arxiv.org/pdf/1306.1077 ; https://www.osti.gov/servlets/purl/1470288
- Cs₀.₃₃WO₃ / LaB₆: https://link.springer.com/article/10.1186/1556-276X-8-57 ; https://www.researchgate.net/publication/231824233
- Photophoretic trapping of carbon clusters in air (Shvedov/Desyatnikov): https://arxiv.org/pdf/0902.1205 ; https://pubmed.ncbi.nlm.nih.gov/19434152/
- Er³⁺ upconversion quantum yield: https://www.sciencedirect.com/science/article/abs/pii/S002223131400194X
- Holoeye GAEA-2.1: https://holoeye.com/products/spatial-light-modulators/gaea-2-phase-only/ ; https://www.axiomoptics.com/products/gaea-2-1-phase-only-lcos-spatial-light-modulator/
- TI PLM: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9501248/ ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9227921/ ; https://github.com/structuredlightlab/plmctrl
- TI DLP650LNIR: https://www.ti.com/product/DLP650LNIR ; https://www.digikey.com/en/products/detail/texas-instruments/DLPLCR65NEVM/296-DLPLCR65NEVM-ND/10434588
- Fraunhofer IPMS SLMs: https://www.ipms.fraunhofer.de/en/press-media/press/2026/Spatial-Light-Modulators.html ; https://www.mdpi.com/2072-666X/12/5/483
- ForthDD QXGA-3DM: https://www.photonics.com/Products/QXGA-3DM_SLM/pr57193
- IPG ELM/ELR: https://www.ipgphotonics.com/en/products/lasers/low-power-cw-fiber-lasers/1-53-1-65-micron/elm-and-elr-1-100-w ; Amonics AFL-1550-50-R: https://www.findlight.net/lasers/fiber-lasers/pulsed-fiber-lasers/amonics-high-power-fiber-laser-afl-1550-50-r
- IMX636 / Triton2 EVS: https://docs.prophesee.ai/stable/hw/sensors/imx636.html ; https://thinklucid.com/triton2-evs/
- InGaAs high-speed: https://www.sensorsinc.com/applications/general/high-speed-swir-imaging ; https://www.axiomoptics.com/products/c-red-2-lite/ ; https://www.raptorphotonics.com/raptor-launches-the-owl-640-t-worlds-first-%C2%BD-vga-sensor-with-10%C2%B5m-vis-swir-response-for-under-10k/

# SPARK validation data — published / reference numbers

Compiled 2026-09-30 for the SPARK instrument (1D spherical hydro + equilibrium air + radiation + NO/O3 + acoustics).

**How to read this file**

- **Access:** every publisher and preprint host (arxiv, osti, ntrs, iopscience, springer, sciencedirect, researchgate, jpldataeval, copernicus, pubmed, stanford, caltech, dtic) was **blocked by the egress proxy** for both WebFetch and curl. **Nothing was read in full.** Each number comes from a web-search result snippet or abstract excerpt (marked `snip`), from my own memory (marked `[MEMORY]`, to be checked before use), or from a local reference computation (marked `calc`).
- **Confidence:** H means an abstract-level number that several snippets agree on. M means one snippet, or a snippet whose attribution is a little unclear. L means memory or plausibility only, so don't use it as a pass/fail test until someone checks it.
- **Units:** SI unless the source used cgs, and then the source unit is kept.

---

## 1. Equilibrium air at 1 atm (LTE)

### 1a. Reference computation (CEA-equivalent), `calc`
This is a local computation with Cantera 3.2 `airNASA9.yaml`. It uses the NASA Glenn 9-coefficient thermo database (McBride, Zehe & Gordon, NASA TP-2002-211556), valid to 20 000 K, the same database NASA CEA uses. It has 11 species (N2, O2, NO, N, O, N2+, O2+, NO+, N+, O+, e-), an ideal gas, **no Debye–Hückel correction, no doubly charged ions**, and air = 79 % N2 / 21 % O2 (no Ar). h is measured relative to 298.15 K air. It is reproducible with `ct.Solution('airNASA9.yaml'); TPX=(T,101325,'N2:0.79,O2:0.21'); equilibrate('TP')`.

| T (K) | rho (kg/m^3) | h − h298 (MJ/kg) | n_e (m^-3) | M (g/mol) | x_N2 | x_O2 | x_NO | x_N | x_O | x_N+ | x_O+ | x_NO+ | x_e |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3000 | 0.1145 | 3.80 | 6.5e16 | 28.2 | 0.752 | 0.162 | 0.0410 | 1.2e-5 | 0.0455 | ~0 | ~0 | 2.7e-8 | 2.7e-8 |
| 5000 | 0.0580 | 10.0 | 6.2e19 | 23.8 | 0.629 | 2.1e-3 | 0.0182 | 0.0263 | 0.324 | 3.6e-9 | 7.7e-8 | 4.2e-5 | 4.2e-5 |
| 7000 | 0.0314 | 26.1 | 7.0e20 | 18.0 | 0.247 | 4.0e-5 | 2.8e-3 | 0.490 | 0.259 | 1.5e-4 | 7.4e-5 | 4.3e-4 | 6.7e-4 |
| 10000 | 0.0172 | 48.1 | 1.73e22 | 14.1 | 2.9e-3 | ~0 | 9.6e-5 | 0.748 | 0.202 | 0.0200 | 3.5e-3 | 9.8e-5 | 0.0236 |
| 15000 | 7.73e-3 | 115 | 1.67e23 | 9.51 | ~0 | ~0 | ~0 | 0.237 | 0.0817 | 0.284 | 0.0567 | 4.9e-6 | 0.341 |
| 20000 | 4.49e-3 | 181 | 1.79e23 | 7.37 | ~0 | ~0 | ~0 | 0.0158 | 6.6e-3 | 0.388 | 0.101 | 6e-8 | 0.489 |

Use these as **code-to-code** targets for the SPARK EOS. At the ≤~2 % level at 10 kK, and ≤~5 % in n_e at 15–20 kK where Debye–Hückel lowering and N++ start to matter, they should match D'Angola 2008 and NASA CEA. That tolerance is [MEMORY]-based, so confidence is M. The **x_NO = 4.1 % at 3000 K** is the equilibrium ceiling relevant to NO freeze-out.

### 1b. Published tabulations to obtain (full text not reachable)

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| Thermo and transport properties of equilibrium air | tables and fits | 0.01–100 atm, 50–60 000 K; Debye–Hückel; higher-order Chapman–Enskog | D'Angola, Colonna, Gorse, Capitelli, EPJ D 46, 129 (2008) https://link.springer.com/article/10.1140/epjd/e2007-00305-4 | snip (abstract) | H (existence), values not retrieved |
| Air mixture used by D'Angola | 79 % N2 / 21 % O2 | — | [MEMORY] | — | L |
| Equilibrium air h, cp, Z, mu, k, Pr + curve fits | tables | 500–30 000 K, 1e-4–1e2 atm, 11 species | Gupta, Yos, Thompson, Lee, NASA RP-1232 (1990) https://ntrs.nasa.gov/citations/19900011981 | snip | H (existence) |
| Air thermo tables with 2nd virial corrections | tables | 1500–15 000 K | Hilsenrath & Klein, AEDC-TDR-63-161 (1963) http://contrails.iit.edu/reports/7843 | snip | H (existence) |
| Laser-spark mole fractions compared with an LTE speciation model | measured within a **factor 2–6** of equilibrium | 1064 nm, 6 ns Nd:YAG spark; 1–200 µs; OH, NH, CN, NO, N2, N2+ | Harilal et al., Phys. Plasmas 25, 083303 (2018) https://pubs.aip.org/aip/pop/article/25/8/083303/1060537 | snip | H |

---

## 2. Net emission coefficient (NEC) of air at 1 atm

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| NEC ε_N(T,R) of air | curves (Fig. 13) | 1 atm, 300–40 000 K, LTE, isothermal sphere or cylinder; atomic and molecular continua, O2/N2/NO/N2+ bands, lines | Naghizadeh-Kashani, Cressault, Gleizes, J. Phys. D 35, 2925 (2002) https://iopscience.iop.org/article/10.1088/0022-3727/35/22/306 | snip | H (existence) |
| NEC of air, radius 0.01–10 cm | curves | 5–30 kK, several pressures | Aubrecht & Bartlova, Plasma Chem. Plasma Proc. 29 (2009) https://link.springer.com/article/10.1007/s11090-008-9163-x | snip | H (existence) |
| Physics check: at high T the NEC is set by N lines; VUV resonance lines dominate the thin case but are strongly self-absorbed; molecular bands dominate below ~10 kK | qualitative | — | same snippets | snip | H |
| NEC, R = 0 (optically thin) | ~1e8–1e9 at 10 kK; ~1e9–1e10 at 15 kK; ~1e10 at 20 kK (W m^-3 sr^-1) | 1 atm | [MEMORY] plus my own Kramers-continuum plausibility estimate. The continuum alone at 15 kK is ~5e8 W m^-3 sr^-1 | — | **L, do not use as pass/fail** |
| NEC, R = 1 mm | lower than R = 0 by roughly 3–10× at 10–15 kK | 1 atm | [MEMORY] | — | L |
| Fraction of optically-thin emission in the visible, η_vis | **0.1 %–10 %** over 3–30 kK; **3 %** adopted to match lightning photometry | Built from Cressault et al. 2011 (Fig. 2) and Naghizadeh-Kashani 2002 (Fig. 13); most escaping radiation is VUV (<200 nm) | da Silva et al., JGR Atmos. 124 (2019) https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019JD030693 | snip | M |

**Action:** the NEC table is the biggest gap. Get the Naghizadeh-Kashani 2002 Fig. 13 or the tabulated data (Cressault / LAPLACE Toulouse) through library access and replace the L rows.

---

## 3. Laser-induced breakdown sparks in air

### 3a. Energy partition

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| Shock-wave share of absorbed E | **51–70 %** | 1064 nm ns Nd:YAG, spark energies 15–50 mJ, 1 atm air; beam deflection + 1D spherical MacCormack model | T. X. Phuoc, Opt. Lasers Eng. 43, 113 (2005) https://ui.adsabs.harvard.edu/abs/2005OptLE..43..113P/abstract | snip | H |
| Radiation share of absorbed E | **22–34 %** | same | same | snip | H |
| Residual hot-gas share | **7–8 %** | same | same | snip | H |
| Shock reach | ~**2 mm within a few µs**; R ∝ t^0.4, p ∝ R^-3 | 15–50 mJ | same | snip | H |
| Deposited / incident | **85 % at 60 mJ → 92 % at 102 mJ** | 1064 nm ns; E_i = 60–273 mJ; Sedov–Taylor estimate of shock energy | Qayyum et al., Appl. Opt. 62, 5189 (2023) https://opg.optica.org/ao/abstract.cfm?uri=ao-62-19-5189 | snip | H |
| Shock / incident | falls linearly **83 % → 48 %** as E_i rises | same | same | snip | H |
| Radiation loss (**simulation**) | **≈2.3 %** of absorbed E, over ~µs | 2D RTE + compressible reacting flow; laser-induced decaying spark in air | Int. J. Heat Mass Transf. (2022) https://www.sciencedirect.com/science/article/abs/pii/S0017931022002599 | snip | H (as a model claim) |
| Absorbed fraction at 193 nm | **40 %** (55±5 mJ of 135 mJ) at 760 Torr; 35 % at 500 Torr, 47 % at 3 atm, 56 % at 5 atm; early mean shock speed 47 km/s | ArF excimer | Thiyagarajan & Scharer (2008) https://legolas.ece.wisc.edu/papers/Thiyagarajan_2008b.pdf | snip | M |
| Absorption vs energy; saturation | qualitative, air vs Ar | 532 nm | Bindhu et al., Appl. Spectrosc. 58, 719 (2004) https://opg.optica.org/as/abstract.cfm?uri=as-58-6-719 | snip | H (qual.) |

Note the **conflict:** radiation is 22–34 % in Phuoc's measurement but 2.3 % in the 2022 simulation. SPARK's radiative-loss fraction is therefore a discriminating output, so report which one it reproduces.

### 3b. Shock kinematics

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| Shock speed history | >25 km/s in the first tens of ns (laser-supported wave); near-hypersonic by 500 ns; supersonic at ~700 ns; **sonic by ~5 µs** | 1064 nm, 6 ns, **55 mJ**, f/5, ~10 µm spot | Harilal, Brumfield, Phillips, Phys. Plasmas 22, 063301 (2015) https://pubs.aip.org/aip/pop/article/22/6/063301/106704 ; https://www.osti.gov/pages/servlets/purl/1454740 | snip | H |
| Post-shock T | ~**5 eV at 30 ns** → ~**0.1 eV at ~1 µs** | same | same | snip | M |
| Shock pressure | **≥500 atm at 30 ns** → **10 atm at 1.1 µs** | same | same | snip | M |
| Shock speed / pressure at r = 1 mm | 1064 nm: **1400–4100 m/s, 0.5–15.74 MPa**; 532 nm: 1000–2222 m/s, 0.37–0.97 MPa | E = 25–140 mJ ns; the 532 nm threshold is ~3.5× lower | Noor et al., Appl. Opt. 64, 4910 (2025) https://opg.optica.org/ao/abstract.cfm?uri=ao-64-17-4910 | snip | H |
| Max shock speed / pressure | **7.4 km/s, 57 MPa**; Sedov–Taylor spherical | 532 nm, 7 ns, f/10 | Leela et al., Laser Part. Beams 31 (2013) https://www.cambridge.org/core/journals/laser-and-particle-beams/article/abs/dynamics-of-laser-induced-microshock-waves-and-hot-core-plasma-in-quiescent-air/2DD31E2A0C59767C2469A3436D5BA226 | snip | H |
| R(t), plus p, T, u from filtered Rayleigh scattering | data (not retrieved) | ns Nd:YAG, quiescent air | Yan, Adelgren, Boguszko, Elliott, Knight, AIAA J. (2003) https://arc.aiaa.org/doi/10.2514/2.1888 | snip | H (existence) |
| Schlieren R(t) → blast energy | data (not retrieved) | ns laser, air | Gebel et al., Shock Waves (2015) https://link.springer.com/article/10.1007/s00193-015-0564-5 | snip | H (existence) |

`calc` Sedov R = 1.033 (E t²/ρ)^(1/5) with ρ = 1.204 kg/m³ gives:

| E | R at 0.1 µs | R at 1 µs | R at 10 µs |
|---|---|---|---|
| 1 µJ | 0.10 mm | 0.25 mm | 0.63 mm |
| 1 mJ | 0.40 mm | 1.0 mm | 2.5 mm |
| 10 mJ | 0.63 mm | 1.58 mm | 3.96 mm |
| 100 mJ | 1.0 mm | 2.5 mm | 6.3 mm |

This is only valid while Δp ≫ p0.

### 3c. Kernel T and n_e vs time

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| Kernel T (Rayleigh) | **≈12 000 K at 10 µs** | 1064 nm ns, **E = 75 mJ**; absorption starts abruptly at 55 mJ | Dumitrache, Limbach, Yalin, Phys. Plasmas 23, 093515 (2016) https://pubs.aip.org/aip/pop/article/23/9/093515/319659 | snip | H |
| Kernel T (Rayleigh) | **400–2000 K at 10 µs** | 266 nm ns, E = 7–35 mJ; gradual onset at ~8 mJ | same | snip | H |
| n_e, T_e (Thomson) at the center | n_e **4.96e23 → 1.1e21 m^-3**; T_e **51 500 → 6900 K** over **1 → 21 µs**; torus by ~18 µs | 1064 nm, **200 mJ**; 532 nm 50 mJ probe | Zhang, Wu, Sun, Yang, Rong, Jiang, Spectrochim. Acta B 157, 6 (2019) https://ui.adsabs.harvard.edu/abs/2019AcSpB.157....6Z/abstract | snip | H |
| n_e, T_e (Thomson) in the core | n_e **7.4e17 → 1.03e17 cm^-3**; T_e **100 900 → 22 700 K** over **150 ns → 1 µs** | 532 nm, 6 ns, **25 mJ** | Dzierżęga et al., J. Phys. Conf. Ser. 227, 012029 (2010) https://www.osti.gov/etdeweb/biblio/21469438 | snip | H (possible probe heating) |
| Early UV–vis continuum | 180–850 nm in the first 200 ns; peak T_e **>100 000 K**; optical depth ~1 | Q-switched Nd:YAG | Borghese & Merola, Appl. Opt. (1998) https://pubmed.ncbi.nlm.nih.gov/18273366/ | snip | M |
| Late peak T | ~**4100 K at 20 µs → 580 K at 1 ms**; triple-exponential decay; N II lines 490–520 nm for 50 ns–1 µs | 532 nm, **180 mJ**, f = 100 mm | Glumac, Elliott, Boguszko, AIAA J. 43, 1984 (2005) https://arc.aiaa.org/doi/10.2514/1.14886 | snip | M (attribution of the 4100/580 K pair not certain) |
| Emission duration; T_e | bright emission up to 30–40 µs; peak n_e ~2e17 cm^-3, T_e ~7 eV | Thomson, laser spark | snippet from a Dumitrache/Yalin-related search (source unclear) | snip | L |

Note the **tension:** 12 000 K at 10 µs (75 mJ, 1064 nm) against 4100 K at 20 µs (180 mJ, 532 nm). Both can be true because the kernel geometry differs. Test SPARK against each case separately.

### 3d. Small-energy, fs and ps sparks

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| fs-LIP n_e | ~**4e21 → ~7e20 m^-3** over 1–10 ns | fs laser, ambient air; Thomson + rotational Raman | Appl. Phys. B (2025/26) https://link.springer.com/article/10.1007/s00340-025-08606-9 ; preprint https://www.researchsquare.com/article/rs-6994468/v1 | snip | M (pulse energy not retrieved) |
| fs-LIP T_e | **0.5–1 eV** throughout 1–10 ns | same | same | snip | M |
| Neutral density on axis | **~2e25 m^-3 for 50 ns → ~1.1e25 m^-3 after 500 ns** (density hole) | same | same | snip | M |
| Breakdown threshold (total electrons) | **~1e6 electrons** at 1 atm | 10 ns pulses; with 100 ps there is no sharp threshold | Wu, Sawyer, Su, Zhang, J. Appl. Phys. 119, 173303 (2016) https://pubs.aip.org/aip/jap/article/119/17/173303/142005 | snip | H |
| Filament energy deposition | measured, spatially resolved | single fs filaments | Rosenthal et al., Opt. Lett. 41, 3908 (2016) https://opg.optica.org/ol/abstract.cfm?uri=ol-41-16-3908 | snip | H (existence) |
| µJ point-spark shock R(t) in air | **none found**. A 130 µJ / 2300 m/s / 240 MPa hit is **in water** (arXiv 1403.6574), not air | — | — | — | gap |

---

## 4. NO / NOx / O3 yields and rate constants

### 4a. Yields per joule

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| NO, laser spark | **4.6e16 NO/J**; **6.7e16 NOx/J**; linear in dissipated energy | 532 nm, 5 ns, 60–180 mJ | Rahman, Cooray et al., Opt. Laser Technol. (2003) https://www.sciencedirect.com/science/article/abs/pii/S003039920300077X | snip | H |
| NOx vs wavelength, energy and pressure | 532 nm gives more NOx than 1064 nm at equal energy; linear over 26–253 mJ (532) and 16–610 mJ (1064); **−3.2 %** for 8 repeated pulses; efficiency rises linearly with p over 16–100 kPa | Nd:YAG | Rahman & Cooray, Opt. Laser Technol. (2008) https://www.academia.edu/29888706 | snip | H |
| NO, laser-simulated lightning | hot channel **(1.5±0.5)e17 NO/J**; shock heating **(3±2)e14 NO/J** | Nd:YAG LIP, 1 atm air | Navarro-González et al., GRL 28 (2001) https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2001GL013170 | snip | H |
| NO, long spark | **(5±2)e16 NO/J** | 1e5–1e6 J/m sparks | Wang et al., JGR 103 (1998) https://www.researchgate.net/publication/248798838 | snip | H |
| NOx, large spark generator | **(1.1±0.2)e16 NOx/J**; all NOx was NO; **no detectable O3 enhancement** | 9.8e4 J sparks; 1.65–2.13 m gaps | Cook et al., JGR 105 (2000) https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/1999JD901138 | snip | H |
| NO, theory | **(9±2)e16 NO/J** | hot-channel cooling-rate model | Borucki & Chameides, Rev. Geophys. 22, 363 (1984) https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/RG022i004p00363 | snip | H |
| Mechanism | NOx forms in the slowly cooling hot channel, not in the shock; lab shocks are too slow to reach ~3000 K | lab discharges | Stark, Harrison, Anastasi, JGR 101, 6963 (1996) https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/95JD03008 | snip | H (qual.) |
| O3 / NO / NO2 from fs filaments | up to **1e14 O3**, **3e12 NO**, **3e13 NO2** molecules; local ppm levels | fs laser filaments | Petit, Henin, Kasparian, Wolf, APL 97, 021108 (2010) https://pubs.aip.org/aip/apl/article-abstract/97/2/021108/339090 | snip | M (per-pulse normalization not confirmed) |
| Review of lab and lightning estimates | compilation | — | Schumann & Huntrieser, ACP 7, 3823 (2007) https://acp.copernicus.org/articles/7/3823/2007/acp-7-3823-2007.pdf ; Cooray, Rahman, Rakov, JASTP 71, 1877 (2009) https://www.sciencedirect.com/science/article/abs/pii/S1364682609002041 | snip | H (existence) |

### 4b. Rate constants (k in cm^3 molecule^-1 s^-1; termolecular in cm^6 molecule^-2 s^-1)

| Reaction | Value | k(300 K) | Source | Read | Conf |
|---|---|---|---|---|---|
| N2 + O → NO + N | **3.0e-10 exp(−38300/T)** ±40 % (2400–4100 K); equivalently 1.8e14 exp(−38370/T) **cm^3 mol^-1 s^-1**. The snippet mislabels this as per molecule; 1.8e14 / N_A = 2.99e-10 | ~0 | Shock-tube results quoted in Koner et al. (2020) https://arxiv.org/html/2002.02310 | snip | H |
| N + O2 → NO + O | **1.5e-11 exp(−3600/T)** | 8.5e-17 | JPL evaluation [MEMORY]; bimolecular table https://jpldataeval.jpl.nasa.gov/pdf/JPL_02-25_2_bimolec_rev02.pdf (not read) | — | L–M |
| N + NO → N2 + O | **2.1e-11 exp(100/T)** (196–400 K, JPL); Baulch: **3.5e-11** flat (210–3700 K) | 2.9e-11 | JPL (snip); Baulch as quoted in Koner et al. https://arxiv.org/html/2002.02310 | snip | H |
| O + O2 + M → O3 + M | JPL k0 = **6.0e-34 (T/300)^−2.4** (M = air) | 6.0e-34 | JPL 02-25/15-10 termolecular https://jpldataeval.jpl.nasa.gov/pdf/JPL_02-25_3_termolec_rev01.pdf | snip | H |
| Same, newer and alternative values | JPL 19-5: 6.1e-34 (T/300)^−2.4 [MEMORY]. IUPAC: 5.6e-34 (T/300)^−2.6 (N2), 6.0e-34 (T/300)^−2.6 (O2) [MEMORY] https://acp.copernicus.org/articles/4/1461/2004/. Discharge models: 6.2e-34 (300/T)^2 (N2), 6.9e-34 (300/T)^1.25 (O2) (snip, arXiv 2210.07782) | 5.6–6.9e-34 | as listed | mixed | M |

`calc` At 300 K in air, 6.0e-34 × [M] 2.46e19 × [O2] 5.2e18 gives an O → O3 conversion rate of ~7.7e4 s^-1, so atomic O lives τ ≈ 13 µs.

---

## 5. Luminous and visible efficiency

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| Optical plus RF share of lightning energy | **~1 %** | natural CG lightning | Krider, Dawson, Uman, JGR 73, 3335 (1968), as cited in secondary snippets https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/JB073i010p03335 | snip (secondary) | M |
| Return-stroke radiance, 0.4–1.1 µm | first strokes **1.3±1.2e6 W/m**; subsequent **3.9±4.9e5 W/m**; radiative efficiency of subsequent strokes ≲**1 %** | Florida lightning | Guo & Krider, JGR 87, 8913 (1982) https://agupubs.onlinelibrary.wiley.com/doi/10.1029/JC087iC11p08913 | snip | H |
| VNIR radiative efficiency | "a few %" at return-stroke onset | calibrated photodiode, 0.4–1.0 µm | Quick & Krider, JGR 118, 1868 (2013) https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/jgrd.50182 | snip | M |
| Optical efficiency of lightning (lab LIP simulation) | **~0.1 %** (1e-3) | Earth air | Borucki & McKay, Nature 328, 509 (1987) https://www.nature.com/articles/328509a0 | snip (secondary) | M |
| η_vis of a hot air channel | 0.1–10 % over 3–30 kK; 3 % adopted | see §2 | da Silva et al. 2019 | snip | M |
| Luminous efficacy (lm/W) of sparks or lightning | **none found** | — | — | — | gap |
| fs "Fairy Lights" voxels | lasers used: 269 fs at ≤50 µJ/pulse and ≤200 kHz; 30–100 fs at ≤7 mJ and 1 kHz. Voxel rates 4 000 and 200 000 dots/s. **No luminance given** | ACM TOG 35(2) (2016) | Ochiai et al. https://arxiv.org/pdf/1506.06668 | snip | H (params) |
| fs voxel emission gain | **1.82×** emission from adaptive pulse shaping | fs air voxels | Tsai, Kumagai, Quan, Luo, Hayasaki, Appl. Opt. 65, G69 (2026) https://opg.optica.org/ao/abstract.cfm?uri=ao-65-15-G69 | snip | H |
| ns aerial display | 100 dots/s (ns laser); later 1000 dots/s (fs) | Burton / Keio | Kimura, Uchiyama, Yoshikawa, SIGGRAPH 2006 https://dl.acm.org/doi/abs/10.1145/1179133.1179154 | snip | M |
| Comparison lamp: xenon flash | up to ~10 lm/W average; pulsed xenon up to ~40 lm/W | vendor-level | https://www.electrical4u.com/xenon-arc-lamp/ | snip | L |

No absolute photometry (cd/m², lm) of fs or ps air-plasma points was found. SPARK luminance predictions currently have **no direct published test**. Only η_vis bounds and lightning efficiencies are available.

---

## 6. Acoustics and blast-wave constants

| Quantity | Value | Conditions | Source | Read | Conf |
|---|---|---|---|---|---|
| Peak pressure at 3 cm | **181 dB re 20 µPa = 22 683 Pa** (1/8" B&K mic); nonlinear to 1.5 m | 1064 nm, **800 mJ**/pulse | Qin & Attenborough, Appl. Acoust. 65, 325 (2004) https://www.sciencedirect.com/science/article/abs/pii/S0003682X03001683 | snip | H |
| Peak pressure at 0.8 m | **~360 Pa**; decays as **r^−6/5** in a scale model. For comparison a 20 mm electric spark gives about the same, and a 5 mm spark gives 90 Pa at 0.8 m (Ayrault 2012) | ns laser (energy not retrieved) | Gómez Bolaños et al., JASA 133, EL221 (2013) https://pubs.aip.org/asa/jasa/article/133/4/EL221/917282 | snip | M |
| Peak level and duration | **98.4 Pa (133.8 dB)**; mean pulse duration **62 µs** | distance and energy not retrieved | Gómez Bolaños et al., JASA 135, EL298 (2014) https://pubs.aip.org/asa/jasa/article/135/6/EL298/607022 | snip | M |
| ns vs ps acoustic spectrum | ps: one peak at 90–120 kHz; ns: 30–70 plus 80–120 kHz; thresholds **10 mJ (ns)** and **3 mJ (ps)**; ns gives more acoustic output | 7 ns vs 30 ps | Manikanta et al., Appl. Opt. 55, 548 (2016) https://opg.optica.org/ao/abstract.cfm?uri=ao-55-3-548 | snip | H |
| p(r) by interferometry | peak p vs r measured over 10–200 mm | ns laser | Hart & Lyons, POMA 48, 045003 (2022) https://pubs.aip.org/asa/poma/article/48/1/045003/2848133 | snip | H (existence) |
| PVDF blast gauge | Friedlander-like profiles; matches TNT-equivalent free-field laws | 1064 nm, ≤2.3 J, 7.5 ns | Shock Waves (2025) https://link.springer.com/article/10.1007/s00193-025-01222-8 | snip | H (qual.) |
| Sedov–Taylor constant ξ0 | **1.033** (exact, γ = 1.4); Chernyi approximation 1.014 | R = ξ0 (E t²/ρ0)^(1/5) | Díaz & Rigby, Shock Waves (2022) https://arxiv.org/pdf/2110.09488 | snip | H |
| Brode point-source fit | Δp/p0 = 0.137 λ^-3 + 0.119 λ^-2 + 0.269 λ^-1 − 0.019, with λ = r (p0/E)^(1/3), for 0.1 < Δp/p0 < 10 | ideal-gas air | Brode (1955/59), coefficients as quoted in https://dspace.mit.edu/bitstream/handle/1721.1/54211/586077698-MIT.pdf | snip | M–H |
| Strong-shock limit | Δp/p0 ≈ 0.157 λ^-3 (from ξ0 = 1.033 and Rankine–Hugoniot) | Δp ≫ p0 | `calc` | — | H |
| Taylor's Trinity yield vs γ | 16.8 kt (γ = 7/5); 22.9 kt (13/10); 34 kt (6/5); modern value 24.8±2 kt | blast-energy inversion sensitivity | https://arxiv.org/pdf/2403.19657 | snip | H |

`calc` cross-check: the Brode fit at r = 3 cm with E_blast = 0.4 J gives 17.8 kPa, against 22.7 kPa measured at 800 mJ incident. That is consistent if ~50–60 % of the incident energy goes into the blast.

---

## 7. Gaps

- The **NEC numbers** (§2) could not be retrieved.
- **µJ-scale point sparks in air** (shock R(t), luminance) have **no published measurement found**.
- **Lightning or spark lm/W** was not found.
- The **D'Angola tables** themselves were not retrieved; §1a is a CEA-equivalent substitute.
- The N + O2 rate and the newer JPL/IUPAC O3 values are [MEMORY].

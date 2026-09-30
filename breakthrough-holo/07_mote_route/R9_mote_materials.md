# R9: Mote materials — photophoretic calibration, aerogel bodies, NIR-absorber skins, 405 nm emitters, prior art, safety

**Question.** Can we build the FOM ≳ 4 m·K/W self-luminous micro-mote the MOTE route needs? A mote of radius 1–4 µm held in a 1550 nm photophoretic trap at 1 atm, whose figure of merit is

> FOM = (J₁/A) / (k_eff + 2 k_gas),  k_gas ≈ 0.03 W/m/K,

with J₁/A → 0.5 only for skin-deep absorption (absorption depth ≲ a/10–a/30), k_eff the mote's effective thermal conductivity, and which must also absorb a 405 nm pump strongly and survive ~450–500 K in air for hours. Two candidate bodies: (a) silica-aerogel sphere with a **non-percolating "island" skin** of a visible-transparent NIR absorber; (b) **core–shell** with a dense Eu²⁺ cyan-phosphor core inside an aerogel shell, same island skin.

**Method and caveats.** Web search only. **WebFetch and all direct scholarly fetches (arXiv, PMC, J-STAGE, Copernicus, ScienceDirect, Nature, RSC/ACS, OSTI, ADS, Crossref/OpenAlex APIs) were blocked by the egress proxy** — every number below comes from search-result snippets/abstracts, my own recall, or my own calculation. Nothing here is [FULL]. Labels:
- **[SNIPPET]** quoted/paraphrased from a search-result abstract or snippet.
- **[MEMORY]** from the model's recall, not re-checked this session.
- **[ESTIMATE]** my calculation (scripts run against `mote/physics.py`).
- Confidence: high / med / low reflects how well the snippet pinned the number.

Definitions as in R6/R7. "Skin-deep" = absorption confined to a surface shell of depth ≲ a/10 so the heat dipole J₁/A approaches its 0.5 ceiling and does not short out through the body. "Non-percolating / island" skin = a discontinuous archipelago of absorber so heat cannot conduct laterally around the mote (k_eff = k_core, not k_core + shell term).

---

## KEY NUMBERS

| Quantity | Value | Conditions | Source | Label | Conf |
|---|---|---|---|---|---|
| **Q1 Photophoresis calibration** | | | | | |
| Continuum PP formula validated to | k (Im n) retrieved to **10⁻⁴–10⁻⁵, ±25–60 %** | single levitated droplet, EDB, 473 nm, near-ambient | Bluvshtein/Krieger/Peter, AMT 13, 3191 (2020) | SNIPPET | high |
| Lewittes absolute force | 20 µm dye-glycerol sphere levitated at **~1 W/cm²**, F = mg = **52 pN**, F/P_inc = **1.6×10⁻⁵ N/W** | air, **30 Torr** (near Kn≈1 max) | Lewittes/Arnold/Oster, APL 40, 455 (1982) | SNIPPET + ESTIMATE | med |
| — model cross-check | continuum F/P_abs (a=10µm,k=0.29,1 atm)=5.9×10⁻⁷ N/W × ~25 (1 atm→30 Torr) ≈ **1.5×10⁻⁵ N/W** | matches Lewittes within ~10 % | this work, `physics.py`, C_ph=1 | ESTIMATE | med |
| Carbon sphere PP force | ~**4×10⁻¹¹ N** (2 µm C, 10 W/mm²=10⁶ W/m²); ~10⁴× radiation pressure | air, 1 atm | review snippet (Pan/Videen paradigm) | SNIPPET | med |
| Chondrule PP force vs model | measured = **~10 % of the "photophoretic strength" used in models**; abs force scatter only 4 %, direction ±3° | 0.3–2.5 mm chondrules, 25 kW/m², low p, microgravity | Loesche/Wurm, "PP Strength on Chondrules 2" (2014) | SNIPPET | high |
| Shvedov giant manipulation speed | few **mm/s**, varies with internal structure/mass | C-coated hollow glass 50–100 µm, vortex beam, air | Shvedov et al., PRL 105, 118103 (2010) | SNIPPET | high |
| Model F/P_abs, target mote | **1.9×10⁻⁵ N/W** (a=1µm), 9.1×10⁻⁶ (2.5µm), 5.9×10⁻⁶ (4µm) | k_eff=0.03, J₁/A=0.5, 1 atm, C_ph=1 | this work | ESTIMATE | med |
| **Q2 Aerogel bodies** | | | | | |
| Smallest silica-aerogel µspheres (emulsion) | **6.8–20 µm** (down to 4 µm tail); pores 6–35 nm | alkali-silica-sol emulsion | "Prep & Char of Silica Aerogel Microspheres" PMC5506966 | SNIPPET | high |
| Microfluidic aerogel µspheres | 50–300 µm (monodisperse), APD | IECR 2024 (Yang et al.) | SNIPPET | high |
| Inhalable aerogel particles (alginate) | **d_aero 1–5 µm (d₅₀≈2.4 µm)** by spray-gel + scCO₂ | pulmonary-delivery aerogels | Pharm Dev Tech 26(5) 2021 | SNIPPET | high |
| Hollow-silica / aerogel nanoparticles | **383–442 nm**, k=0.023–0.026 W/m/K, ρ 0.015–0.033 g/cm³ | gas/liquid-phase hollow silica | ACS ANM 2025 snippet | SNIPPET | med |
| Bulk silica-aerogel k | **0.010–0.021 W/m/K** (0.018 monolith); powder 0.004 at vacuum | 300 K, 1 atm | multiple reviews | SNIPPET | high |
| Micron-aerogel patent props | 5–1500 µm; ρ 0.05–0.2 g/cm³; **k ≈ 0.02 W/m/K** | WO2018124979A2 | SNIPPET | med |
| **Q3 NIR absorbers (vis-transparent)** | | | | | |
| Cs₀.₃₃WO₃ LSPR band | strong **780–2500 nm** (LSPR 1100–2500 + polaron 780–1100); Vis 80 % @550 nm | hexagonal tungsten bronze NCs, 30–40 nm | multiple | SNIPPET | high |
| Cs₀.₃₃WO₃ areal density for shielding | **0.9 mg/cm² → 70 % NIR**, 1 mg/cm² → 75 %; films reach **90.9 % @780–2500 nm, T_vis 70.6 %** | coatings/films | RSC/Elsevier snippets | SNIPPET | high |
| Cs₀.₃₃WO₃ solid absorption coeff @~1.5 µm | **α ≈ 1–5×10⁴ cm⁻¹** (from 0.9 mg/cm²≈1.2 µm-solid giving A≈1.2) | back-out from shielding | this work | ESTIMATE | low-med |
| Cs₀.₃₃WO₃ air-oxidation onset | **~470 °C** (starts to oxidize); silica-coat improves moist-heat | TGA/XRD | Springer/Elsevier snippets | SNIPPET | med |
| ITO NC extinction (NIR) | **up to 56.6 µm⁻¹ = 5.7×10⁵ cm⁻¹** (20 nm, 7.5 at% Sn); LSPR tunable **1600→2200 nm** | dense NC ensemble | Staller/Milliron, Nano Lett 19, 8149 (2019) | SNIPPET | high |
| ITO NC air-anneal | LSPR redshifts / weakens as O fills vacancies; **≤300 °C little effect**, worst ~350 °C | air annealing | arXiv 2211.04144 etc | SNIPPET | med |
| AZO/doped-ZnO LSPR | ENZ **~1.3–1.84 µm** at n=1.2×10²¹ cm⁻³ (best); mostly MWIR/LWIR | Al/Ga/In:ZnO NCs | PNAS 2012; Elsevier 2024 | SNIPPET | med |
| LaB₆ | absorbs 750–1300 nm (peak ~1.3 eV≈950 nm); **oxidizes 450–600 °C in air**, moisture-sensitive | solar-control NCs | Mater. 11, 2473; JMR 2016 | SNIPPET | high |
| TiN | broad NIR/vis LSPR; **oxidizes to TiO₂ ~350–400 °C in air**; not vis-transparent (grey) | plasmonic TiN | multiple | SNIPPET | high |
| Thin-film absorption ceiling | **≤50 %** for a sub-λ film in symmetric medium; broken by asymmetry / NC "perfect absorbers" | fundamental | Hot-carrier absorber refs | SNIPPET | high |
| **Q4 Eu²⁺ phosphors (405 nm pump)** | | | | | |
| BaSi₂O₂N₂:Eu²⁺ | **495 nm, FWHM 32 nm, IQE ~90 %**; QE −4.2 % at 150 °C, **T_quench ≈ 450 °C/450 K** | cyan phosphor | EPJ Plus 2024; JNN 2016 | SNIPPET | high |
| β-SiAlON:Eu²⁺ (540 nm green) | IQE up to **96.5 %** (killer-reduced); retains **>85–93 % at 150 °C, ~80 % at 300 °C** | LCD backlight grade | Chem Mater 2018 | SNIPPET | high |
| CaAlSiN₃:Eu²⁺ (red 650 nm) | IQE ≥50–70 %; thermal quench **−6 % at 150 °C**, strong to 200–300 °C; excit. 350–500 nm (inc. 405) | red nitride | multiple | SNIPPET | high |
| (Ba,Sr)₂SiO₄:Eu²⁺ | retains only **51.8 % at 150 °C** (poor) | orthosilicate | snippet | SNIPPET | med |
| Eu²⁺ nitride α @405 nm | **α ≈ 0.3–3×10³ cm⁻¹** (σ₅d≈10⁻¹⁸–10⁻¹⁷ cm², 1.6 % Eu, N≈3×10²⁰) | heavily doped | this work | ESTIMATE | low-med |
| Smallest good-QE nitride | **Sr₂Si₅N₈:Eu d₅₀=144 nm, IQE 61 %** (82 % of bulk 74 %) | milled nanophosphor | Sci Rep 10, 1613 (2020) | SNIPPET | high |
| **Q5 405 nm emitter alternatives** | | | | | |
| InP intrinsic α @413 nm | **8.5×10⁴ cm⁻¹** (size-independent above gap) | InP QD | BU Dennis lab | SNIPPET | high |
| InP/ZnSe/ZnS QD thermal | retains **~92 % PL at 150 °C**; degrades >100 °C in vacuum (ligand loss) | core/multishell | Coatings 11, 581 (2021) | SNIPPET | med |
| CdSe/CdS(giant) QD thermal | reversible quench 100–180 °C; **irreversible loss up to 60 %** after heating; detectable to 500 °C | core/shell | Zhao/Meijerink, ACS Nano 6, 9058 (2012) | SNIPPET | high |
| CsPbBr₃ NC thermal | **81 % @100 °C, 47 % @150 °C, 20 % @200 °C** (core-shell); glass/Al₂O₃ improves | perovskite NC | multiple | SNIPPET | med |
| Carbon dots in silica | QY 35–83 %; **stable to 350–400 °C in air** | C-dot@SiO₂ µspheres | Nano 10,1063; PMC12828719 | SNIPPET | med |
| PDI dye @silica | high QY, high molar ε, good photostability; **decomposes ~300–400 °C** | dye-doped silica | snippets | SNIPPET/MEMORY | med |
| **Q6 Prior art (engineered PP particles)** | | | | | |
| Keith geoengineering disks | layered Al₂O₃/… disks engineered for PP levitation (concept) | PNAS 107, 16428 (2010) | SNIPPET | high |
| Azadi nanocardboard | Mylar+CNT one-side coat, Al₂O₃ hollow plates; levitate **~10 Pa, 0.5 W/cm²** | Sci Adv 7, eabe1127 (2021) | SNIPPET | high |
| Schäfer perforated flyer | 1 cm structure levitates at **26.7 Pa, 750 W/m²** | Nature 644, 362 (2025) | SNIPPET | high |
| Core-shell capsule PP sim | liquid core + absorbing poly-composite shell + aux NPs; FEM PP motion | Geints/Panina, arXiv 2402.03645 (2024) | SNIPPET | med |
| Janus PP in air | Au-cap Janus lifted/held in doughnut beam; drive ∝ power & 1/p (PP, not rad.press.) | multiple | SNIPPET | high |
| **Q7 Safety (inhaled µg)** | | | | | |
| Amorphous (aerogel) silica | **no fibrosis**; NOAEC ~1 mg/m³ (5-day rat); OEL (DE TRGS 900) **4 mg/m³** inhalable | SAS inhalation | Tox 2007/2018 | SNIPPET | high |
| ITO / indium | **"indium lung" — pulmonary alveolar proteinosis + fibrosis**; rat lesions down to **0.01 mg/m³**; poor prognosis | occupational ITO | multiple PMC | SNIPPET | high |
| WO₃ / tungsten bronze NP | mostly low lung toxicity (transient inflammation), but **W ions cytotoxic**, some COPD-risk signal | WO₃ NP inhalation | PMC9650236; PMC10302912 | SNIPPET | med |
| LED nitride phosphor encaps. | pharyngeal aspiration → inflammatory/lamellar-body response in mice | Eu nitride phosphor | ScienceDirect 2626 | SNIPPET | low-med |

---

## 1. Photophoretic force calibration (Q1): is C_ph ≈ 0.67–1.04 consistent with data?

**Yes, to within a factor ~1.3–1.6, for compact particles whose k is known.** Three independent anchors:

1. **Electrodynamic-balance photophoretic spectroscopy (EDB-PPS), Bluvshtein/Krieger/Peter, AMT 2020** [SNIPPET, high]. A single levitated droplet in an EDB, illuminated at 473 nm, was used to retrieve the imaginary refractive index k down to **10⁻⁴–10⁻⁵ with ±25–60 % uncertainty**. This only works if the *continuum-regime* photophoretic force is predicted from the Yalamov/Reed-type formula to within that uncertainty — i.e. the continuum prefactor is known to tens of percent. This is the strongest quantitative endorsement that the formula the MOTE model uses (with C_ph ≈ 1) is right at ~1 atm. The residual ±25–60 % is exactly the band that C_ph ∈ [0.67, 1.04] plus accommodation-coefficient uncertainty spans. **Continuum photophoresis is a calibrated force, not a guess.**

2. **Lewittes/Arnold/Oster 1982** [SNIPPET + ESTIMATE, med]. A 20 µm dye-impregnated glycerol sphere was radiometrically levitated in air at **30 Torr** at intensity **~1 W/cm²**. Force balance: weight = (4/3)πa³ρg = **52 pN** against an incident power of 3.14 µW over the geometric cross-section → **F/P_inc = 1.6×10⁻⁵ N/W**. Running our own continuum model (`physics.py`, C_ph = 1) for the same sphere at **1 atm** gives F/P_abs = 5.9×10⁻⁷ N/W; the continuum force scales as 1/p up to the Kn≈1 maximum, and 1 atm → 30 Torr is a ×25 enhancement, giving **≈1.5×10⁻⁵ N/W**. That lands within ~10 % of the measured value (assuming near-unity absorption of the dyed sphere). **This is a clean absolute check that C_ph ≈ 1 is correct.** (Caveat: 30 Torr is near the transition-regime peak, not deep continuum, so the ×25 scaling is itself only good to ~1.5×.)

3. **The cautionary anchor — Loesche/Wurm chondrules 2014** [SNIPPET, high]. Force on **bare** mm-scale chondrules was measured at **only ~10 % of the "photophoretic strength" used in earlier models**, even though the absolute force was reproducible (±4 %) and well-aligned (±3°). The shortfall is not a prefactor error — it is that chondrules are **high-k silicate (k ≈ 1–4 W/m/K)** and irregular, so the k_p in the denominator crushes the force. **This is the single most important lesson for the MOTE route: real, dense, high-k particles fall far short of the idealized force, and microstructure/thermal conductivity dominate.** It is precisely why the mote must be engineered low-k with skin-deep absorption, and why the FOM is the right master variable.

Order-of-magnitude anchor for the design: a 2 µm carbon sphere at 10⁶ W/m² feels ~4×10⁻¹¹ N [SNIPPET], ~10⁴× radiation pressure — consistent with continuum photophoresis. Shvedov's carbon-coated hollow glass (50–100 µm) moved at a few mm/s in air [SNIPPET].

**Model output for our target motes** (`physics.py`, C_ph = 1, J₁/A = 0.5, 1 atm) [ESTIMATE, med]:

| a (µm) | k_eff (W/m/K) | F/P_abs (N/W) | FOM |
|---|---|---|---|
| 1.0 | 0.03 | 1.9×10⁻⁵ | 6.1 |
| 2.5 | 0.03 | 9.1×10⁻⁶ | 6.1 |
| 4.0 | 0.03 | 5.9×10⁻⁶ | 6.1 |
| 1.0 | 0.05 | 1.5×10⁻⁵ | 4.9 |
| any | 0.15 | (÷~2.5) | 2.5 |

So the MOTE route's continuum force model is **consistent with the best single-particle measurements to within the ~25–60 % they themselves carry**. The remaining risk is not the prefactor; it is whether a real engineered mote can actually hit k_eff ≈ 0.03–0.05 while absorbing skin-deep. That is a materials question, below.

**What I could not verify:** the exact Rohatschek p* and free-molecular slope for our specific mote; any *1-atm* absolute force-per-absorbed-watt measurement on a micron particle (all clean absolute numbers I found are at reduced pressure — Lewittes 30 Torr, Wurm mbar). A 1-atm bench measurement remains RESULTS §5 bench item 1.

## 2. Aerogel microsphere bodies (Q2)

**Feasibility: the size is at the hard edge of what exists; the low-k survives to ~1 µm only marginally.**

- **Smallest made.** Emulsion/sol-gel silica-aerogel microspheres are routinely **6.8–20 µm**, pore size 6–35 nm [SNIPPET, high; PMC5506966]. Microfluidic routes give beautiful monodisperse spheres but **50–300 µm** [SNIPPET]. The **1–4 µm target is below the demonstrated emulsion floor** — you are asking for the small tail of an emulsion distribution, or a spray/aerosol route.
- **The encouraging analog:** pharmaceutical **aerogel microparticles engineered to d_aero 1–5 µm (d₅₀ ≈ 2.4 µm)** via spray-gelation + supercritical CO₂ drying are a mature inhalation-delivery technology [SNIPPET, high]. These are alginate, not silica, but they prove that sub-5-µm supercritically-dried aerogel particles are manufacturable at scale. A silica or hybrid version at 2–4 µm is plausible; at 1 µm it is unproven.
- **Does micron-scale aerogel keep low k?** The concern is real: pores are 10–50 nm, so a 1 µm particle is only ~20–100 pores across. Bulk silica-aerogel k = **0.010–0.021 W/m/K** [SNIPPET, high]; micron-aerogel patents claim **k ≈ 0.02 W/m/K** for 5–1500 µm particles [SNIPPET, med]; hollow-silica *nanoparticles* (383–442 nm) still measure **k = 0.023–0.026 W/m/K** [SNIPPET, med]. So even at the few-hundred-nm scale the solid-network + Knudsen-suppressed-gas conduction keeps k ≈ 0.02–0.03 W/m/K. **I take k_core ≈ 0.02–0.04 W/m/K for a 1–4 µm silica-aerogel mote as defensible but not directly measured at this size.** The main uncertainty is that a particle only ~50 pores wide has a larger surface-to-volume fraction of denser skin and may run 1.5–2× above monolith k.
- **Thermal survival:** amorphous silica aerogel is stable to ≥600 °C (sinters/shrinks well above our 450–500 K window), so the *body* easily survives the thermal spec. Structural collapse on repeated 450–500 K cycling is the open item, not chemistry.

## 3. NIR-absorber island skins (Q3)

**The core design tension: skin-deep (thin) vs. high absorptance. It is resolvable, but only with a *dense* plasmonic material, not a sparse monolayer.**

Physics limit first: a truly 2-D sub-wavelength layer in a symmetric medium absorbs **≤ 50 %** [SNIPPET, high]. A mote skin beats this because (i) it is a finite shell (100–300 nm), not 2-D; (ii) the sphere gives a double pass (front + back); (iii) the aerogel/air asymmetry breaks the symmetric-radiation condition. So high absorptance is allowed — but you need enough absorber column in the front skin that α·t ≳ 2.

Candidate materials at 1550 nm:

| Material | α (solid) near 1.5 µm | Vis transparency | Air stability | Verdict |
|---|---|---|---|---|
| **ITO NC** | **5.7×10⁵ cm⁻¹** (LSPR 1.6 µm) [SNIPPET] | good (grey-blue tint) | ≤300 °C OK, weakens by 350 °C | **strongest absorber**; LSPR a bit long of 1550, tune with Sn/n. Indium-lung risk. |
| **Cs₀.₃₃WO₃** | **~1–5×10⁴ cm⁻¹** [ESTIMATE] | excellent (T_vis 70–80 %) | **onset ~470 °C** | best vis-transparency + heat tolerance; α lower → needs thicker skin |
| **AZO / doped ZnO** | high but LSPR **1.3–1.84 µm→MWIR** [SNIPPET] | good | ZnO oxidatively stable | LSPR hard to pull to 1550; marginal |
| **LaB₆** | strong 0.95 µm, weaker at 1.55 | greenish | **oxidizes 450–600 °C**, moisture-sensitive | thermally marginal, off-peak |
| **TiN** | broad, strong | **grey/opaque — fails "visible-transparent"** | oxidizes 350–400 °C | rejected for a *display* mote (kills your own emission) |
| Carbon black | very strong, broad | opaque black | oxidizes 400–500 °C, sheds soot | rejected (opaque + soot, see R7) |

**Sizing the skin** [ESTIMATE, low-med]. To absorb 80–90 % single-front-pass you need α·t ≈ 2–2.3.
- With **ITO NC (α ≈ 5×10⁵ cm⁻¹)**: t ≈ **40–50 nm** suffices. For a 1 µm mote that is a/20–a/25 — **comfortably skin-deep**, J₁/A → ~0.45–0.5.
- With **Cs₀.₃₃WO₃ (α ≈ 2×10⁴ cm⁻¹)**: t ≈ **1 µm of solid-equivalent** — too thick to be skin-deep on a 1 µm mote. Only works skin-deep on a **4 µm mote** (t/a ≈ 0.25, marginal) or if the bronze is packed denser / its 1550 nm α is at the high end of my estimate. The 0.9 mg/cm² → 70 % and 90.9 % film data confirm you need roughly a micron of solid-equivalent bronze for high absorptance broadband; at the sharp LSPR peak near 1550 it is better but I could not pin the peak α.

So the **island skin should be ITO (or high-carrier-density Cs_xWO₃ tuned to 1550 nm), deposited as a discontinuous ~40–150 nm archipelago.** "Non-percolating" is essential and achievable: sub-monolayer NC coverage or dewetted islands break lateral conduction so k_eff stays = k_core (the model's `skin='islands'` branch, k_eff = k_core, no +4k_skin/αa term). The islands themselves are dense (high α) but cover, say, 40–70 % of the surface with gaps, so heat cannot run around the sphere.

**Thermal-stability caveat that bites:** ITO LSPR *weakens* on air annealing as O fills vacancies, and the worst case is ~350 °C [SNIPPET, med] — **below our 450–500 K (177–227 °C) operating window it is probably OK, but 500 K is uncomfortably close.** Cs_xWO₃ (onset ~470 °C) has more margin and better vis-transparency, at the cost of needing a thicker, less-skin-deep layer. A **silica overcoat** on the islands (a few nm) both pins the absorber against oxidation (shown to help Cs_xWO₃ moist-heat) and does not percolate heat if kept thin. **Recommendation: Cs_xWO₃ islands for thermal/optical-transparency safety on larger (2.5–4 µm) motes; ITO islands where the 1 µm skin-depth budget is tight, accepting the tighter thermal margin and indium toxicity.**

## 4. Eu²⁺ cyan phosphor core (Q4)

**The emitter chemistry is excellent; the two problems are 405 nm absorption in ~1 µm and nano-size QE loss.**

- **Thermal survival is a solved problem for the right host.** BaSi₂O₂N₂:Eu²⁺ (495 nm, FWHM 32 nm, **IQE ~90 %**) loses only **4.2 % of QE at 150 °C and quenches around 450 °C/450 K** [SNIPPET, high] — it comfortably survives the 450–500 K spec, which is the key R6/R7 requirement. β-SiAlON:Eu (green 540 nm, IQE up to 96.5 %) keeps >85 % at 150 °C and ~80 % at 300 °C [SNIPPET, high]. CaAlSiN₃:Eu (red) is even more robust (−6 % at 150 °C) [SNIPPET]. **Avoid (Ba,Sr)₂SiO₄:Eu — only 51.8 % retained at 150 °C** [SNIPPET]. Nitride/oxynitride hosts, not orthosilicates.
- **405 nm absorption in a micron core is the weak link** [ESTIMATE, low-med]. Eu²⁺ 4f→5d is parity-allowed (σ ≈ 10⁻¹⁸–10⁻¹⁷ cm²) but at practical doping (~1–2 % Eu, N_Eu ≈ 3×10²⁰ cm⁻³) the solid absorption coefficient at 405 nm is only **α ≈ 3×10²–3×10³ cm⁻¹**. Over a 1–2 µm core that is α·d ≈ 0.03–0.6 → **3–45 % single-pass absorption.** Bulk phosphor layers absorb 60–90 % of blue only because they are 15–30 µm thick. **A 1 µm phosphor core will under-absorb the pump** unless you (a) go to a=2.5–4 µm and a 3–5 µm core, (b) push Eu doping to the concentration-quenching limit to lift α toward 10⁴ cm⁻¹, or (c) add a thin dedicated 405 nm absorber (see §5). This is an honest FOM-independent bottleneck and matches R6's "brightness per mote is limited by how much pump each mote absorbs."
- **Nano-size QE penalty is modest for nitrides.** Milled **Sr₂Si₅N₈:Eu at d₅₀ = 144 nm kept IQE 61 % (82 % of the 74 % bulk)** [SNIPPET, high] — the best nitride nanophosphor on record. So a phosphor *core* of 0.6–2.5 µm (well above 144 nm) should retain near-bulk QE; only if you disperse sub-100 nm phosphor grains inside the aerogel (the "engineered" body) do you pay a real QE and surface-oxidation penalty. **Prefer a single dense phosphor core over dispersed nanophosphor.**

## 5. Alternative 405 nm emitters (Q5)

Ranked by fit to "strong 405 nm absorption in ~1 µm + PL survives 450–500 K in air for hours":

- **InP/ZnSe/ZnS QDs** — intrinsic α at 413 nm = **8.5×10⁴ cm⁻¹** [SNIPPET, high], ~30× the Eu-nitride value, so a *thin* QD-loaded shell absorbs 405 nm far better than the phosphor itself. PL retention **~92 % at 150 °C** [SNIPPET, med]. **But 450–500 K in air for hours is beyond QD survival** — ligand loss/oxidation above ~100–150 °C in vacuum, and Cd/In cores oxidize. Usable as a pump-absorbing sensitizer only if the operating temperature is held ≤150 °C, which conflicts with the 450–500 K trap-heat spec. Flag: QDs are the best 405 absorber but the worst thermal survivor.
- **CdSe/CdS "giant" shell QDs** — reversible quench 100–180 °C but **irreversible ≤60 % loss** after heating [SNIPPET]; same thermal disqualifier, plus Cd toxicity.
- **CsPbBr₃ perovskite NCs** — bright, but **47 % at 150 °C, 20 % at 200 °C** and Pb + moisture instability [SNIPPET]; rejected for a 450–500 K open-air mote.
- **Carbon dots in silica** — QY 35–83 %, **stable to 350–400 °C in air** [SNIPPET, med]; these *do* survive the thermal spec and are non-toxic, but emission is broad and blue-green QY at 405-excitation is lower than Eu²⁺. A reasonable fallback emitter where thermal robustness beats color purity.
- **Organic dyes (PDI) in silica** — high ε and QY but decompose ~300–400 °C and photobleach under kW/cm² [SNIPPET/MEMORY]; rejected for a hot, intensely-pumped mote.

**Conclusion for Q4/Q5:** the **Eu²⁺ nitride/oxynitride phosphor is the only emitter that clears the 450–500 K-in-air-for-hours bar with good color**; the price is weak 405 nm absorption in a micron core, best mitigated by a larger mote (a ≥ 2.5 µm) and/or maximal Eu doping rather than by adding a thermally-fragile QD/dye sensitizer.

## 6. Prior art: engineered/composite particles for photophoresis (Q6)

Composite particles designed for photophoretic force are an established (if macroscopic/low-pressure) art — but **nobody has published a micron-scale, self-luminous, 1-atm core-shell mote**; that is genuinely novel.

- **Keith, PNAS 2010** — *Photophoretic levitation of engineered aerosols for geoengineering* [SNIPPET]: explicitly layered/asymmetric engineered disks (with magnetic/electrostatic layers) to exploit and direct photophoresis. The intellectual parent of "design the particle for the force."
- **Azadi et al., Sci Adv 2021** — one-side-CNT-coated Mylar and Al₂O₃ "nanocardboard"; controlled levitation at **~10 Pa, 0.5 W/cm²** [SNIPPET]. Asymmetric absorber = deliberate J₁ engineering.
- **Schäfer et al., Nature 2025** — perforated flyers levitating at **26.7 Pa, 750 W/m²** via Knudsen/thermal-transpiration pumping [SNIPPET]. Confirms macroscopic photophoretic flight but at near-space pressure, not 1 atm.
- **Geints & Panina, arXiv 2024** — FEM of a **core-shell microcapsule** (liquid core + absorbing poly-composite shell + auxiliary NPs) under laser: the closest published analog to our core-shell mote, though for drug-release, not levitation, and by simulation only [SNIPPET, med].
- **Janus particles** (Au-cap silica/PS) are routinely lifted and held in doughnut/bottle beams in air, with the drive confirmed photophoretic (∝ power, ∝ 1/p, not radiation pressure) [SNIPPET]. These validate that an **asymmetric-absorber micro-particle traps stably** — the mechanical premise of the island-skin mote.

**Gap in prior art = our contribution:** a 1–4 µm, low-k, visible-transparent-NIR-absorber-skinned, *self-luminous* particle trapped at **1 atm** (everyone else works ≤ a few kPa or with opaque carbon). No measured FOM for anything like it exists.

## 7. Safety of inhaling µg of these composites (Q7)

Ranking the ingredients by inhalation hazard (context: R7 established the whole display emits µg/day, well-mixed airborne ≈ 0.008 µg/m³, but near-field and composite toxicology were open):

- **Amorphous silica aerogel body — low hazard.** Synthetic amorphous silica does **not cause lung fibrosis**, effects are largely reversible, NOAEC ~1 mg/m³ in 5-day rat studies, OEL 4 mg/m³ inhalable [SNIPPET, high]. It is *not* crystalline silica. The aerogel body is the safe part.
- **ITO skin — the serious concern.** Occupational ITO causes **"indium lung": pulmonary alveolar proteinosis + interstitial fibrosis, poor prognosis**, with rat lesions down to **0.01 mg/m³** — the lowest-hazard-threshold ingredient by far [SNIPPET, high]. Even µg-scale chronic exposure of an engineered indium nanomaterial in a room is a real regulatory and ethical liability. **This is a strong argument to prefer Cs_xWO₃ islands over ITO despite ITO's better skin-depth.**
- **Tungsten bronze (Cs_xWO₃) skin — moderate/uncertain.** WO₃/tungsten-oxide NPs show mostly transient lung inflammation and low histopathology, **but soluble W ions are cytotoxic** and there is a COPD-risk signal [SNIPPET, med]. Cs leaching is an added unknown. Better than ITO, not benign; a silica overcoat reduces dissolution.
- **Eu²⁺ nitride/oxynitride phosphor — data-poor.** LED phosphor encapsulates aspirated into mice gave inflammatory/lamellar-body responses [SNIPPET, low-med]; nitrides are chemically inert and low-solubility (better than the NaYF₄:F⁻-leaching issue in R7), but there is **no inhalation guideline for Eu silicon-nitride micro-particles** — an explicit unknown.
- **Net:** the body (silica aerogel) and emitter (nitride phosphor) are low-to-moderate and inert; **the NIR-absorber skin is the toxicological pivot, and it argues against indium.** Encapsulating every mote in a thin outer silica shell (already wanted for oxidation protection) also minimizes absorber dissolution and is the single most useful safety measure.

---

## RECOMMENDED CONCRETE MOTE RECIPE

Two variants, differing only in how the pump light is absorbed. Both target the FOM ≳ 4 m·K/W gate with honest margin.

### Recipe A — "Engineered" (accent/sketch motes, a = 1.5 µm)
| Layer | Material | Thickness / spec | Purpose |
|---|---|---|---|
| Body | silica aerogel sphere | a = 1.5 µm, ρ ≈ 0.1–0.15 g/cm³, k_core ≈ **0.03 W/m/K** | low-k structure; visible-transparent |
| Emitter | β-SiAlON:Eu²⁺ (green) **or** BaSi₂O₂N₂:Eu²⁺ (cyan) nanophosphor, dispersed OR as a 0.8 µm inner core | ≤ 30 vol %, grains 150–300 nm | visible emission; survives 500 K |
| NIR skin | **Cs_xWO₃ islands**, LSPR tuned toward 1550 nm, silica-overcoated 3–5 nm | **~150–250 nm islands, 50–70 % areal coverage, non-percolating** | skin-deep 1550 nm absorption; vis-transparent; oxidation-safe to ~470 °C |

- **A_trap (1550 nm):** ~0.8–0.95 (islands over most of the front face; some leakage through gaps). J₁/A ≈ **0.43–0.48** (skin depth ≈ a/6–a/10, near but not at the 0.5 ceiling).
- **k_eff = k_core ≈ 0.03 W/m/K** (islands do not conduct laterally). 2k_gas = 0.06.
- **FOM = 0.45 / (0.03 + 0.06) = 5.0 m·K/W** [ESTIMATE]. Clears the gate.
- **405 nm absorptance:** dispersed nitride nanophosphor over a 3 µm chord, α_405 ~ 10³ cm⁻¹ → **~25–40 %** single pass; adequate for a green/cyan accent, weak for film-density.

### Recipe B — "Core–shell" (brightest, a = 2.5–4 µm)
| Layer | Material | Thickness / spec | Purpose |
|---|---|---|---|
| Core | **dense BaSi₂O₂N₂:Eu²⁺ (cyan 497 nm) single crystallite**, heavily Eu-doped | radius 0.6a (1.5–2.4 µm) | strong 405 nm absorber + emitter; near-bulk QE; T_quench 450 °C |
| Shell | silica aerogel | 0.4a (1.0–1.6 µm), k ≈ 0.02 | low-k thermal blanket around the dense core |
| NIR skin | Cs_xWO₃ islands (or ITO islands if skin-depth budget forces it), silica-overcoated | **~150 nm, non-percolating** | skin-deep 1550 nm absorption |

- **k_eff** (coated-sphere, k_core = 5 W/m/K phosphor, k_shell = 0.02, core_frac 0.6) = **0.046 W/m/K** + islands add 0 → **≈ 0.046**. 2k_gas = 0.06.
- **A_trap ≈ 0.95**, **J₁/A ≈ 0.43** (skin on the aerogel shell; the dense core is thermally buried so the heat dipole still sits in the skin).
- **FOM = 0.43 / (0.046 + 0.06) = 4.1 m·K/W** [ESTIMATE]. Clears the gate with less margin than A — the dense core is the price of good pump absorption.
- **405 nm absorptance:** dense Eu core, α_405 pushed to ~3×10³–10⁴ cm⁻¹ over a 3–4.8 µm core → **60–90 %**. This is the variant that can feed film-density brightness.

### Expected F/P_abs (both, C_ph = 1, 1 atm): ~6–9×10⁻⁶ N/W at a = 2.5 µm, ~1.5×10⁻⁵ at a = 1.5 µm [ESTIMATE].

### Honest uncertainty
- **k_eff** is the dominant risk. If a 1–4 µm aerogel runs 1.5–2× above monolith k (surface-densified skin, only ~50 pores wide), k_core → 0.045–0.06 and **Recipe A FOM falls to ~3.3–4.0; Recipe B to ~3.0–3.5 — at or below the gate.** Not yet measured at this size = the #1 unknown.
- **J₁/A** assumes the islands really confine absorption to ≲ a/10. If Cs_xWO₃'s 1550 nm α is at the low end (10⁴ cm⁻¹), the skin must be ~1 µm thick and J₁/A drops toward 0.3 on a 1.5 µm mote (skin no longer thin) — pushing to ITO or larger motes.
- **405 nm absorption** in Recipe A is marginal; Recipe B depends on achieving high Eu doping without concentration-quenching the QE.
- **C_ph = 1 ± ~40 %** per §1; the FOM gate has enough headroom (5.0, 4.1) to survive the low end only for Recipe A.
- **Thermal cycling** of a micron aerogel across 450–500 K for hours is untested; ITO-skin oxidation margin at 500 K is thin.

**Net verdict:** Both recipes are *designed* to clear FOM ≳ 4, and no physical law forbids them, but **every clearing number depends on a material property (micron-aerogel k, island-skin α and skin-depth) that has not been measured at 1–4 µm.** The route is a materials-research bet, exactly as RESULTS §7 states — this report sharpens it from "unknown mote" to "silica-aerogel + Cs_xWO₃ islands + Eu-nitride core, with three specific measurements needed."

---

## GAPS (what must be measured, and what I could not verify this session)

1. **No 1-atm absolute photophoretic-force-per-absorbed-watt measurement on a micron particle** was found — all clean absolute forces are at reduced pressure (Lewittes 30 Torr, Wurm mbar). The EDB-PPS work validates the *continuum formula* to ±25–60 % but does not hand us a 1-atm N/W for a low-k mote. **Bench item 1 (RESULTS §5) stands.**
2. **k_eff of a 1–4 µm aerogel particle is not directly measured** — only bulk/monolith and ~400 nm hollow-silica values exist. The whole FOM hinges on this.
3. **Peak absorption coefficient of Cs_xWO₃ at 1550 nm** (as opposed to broadband-shielding-inferred α) not pinned; needed to fix the island skin thickness and hence J₁/A. Could not read the Milliron ITO paper or any bronze optical-constants paper in full.
4. **Skin "non-percolation" ↔ heat isolation** is asserted from the model's `skin='islands'` branch, not demonstrated; a percolation-threshold + effective-k measurement on an island-skinned microsphere is missing.
5. **405 nm absorption coefficient of heavily-doped Eu²⁺ nitride at micron path** is my estimate (σ₅d assumed 10⁻¹⁸–10⁻¹⁷ cm²); no measured α_405(cm⁻¹) for these hosts was retrievable.
6. **QE of a dense sub-micron BaSi₂O₂N₂:Eu core specifically** (vs. the Sr₂Si₅N₈ 144 nm analog) not found.
7. **Composite-mote inhalation toxicology** (silica-aerogel + Cs_xWO₃/ITO + Eu-nitride, as one particle) has no study; only the separate ingredients. ITO's indium-lung hazard (lesions at 0.01 mg/m³) is the standout reason to avoid indium in a consumer-adjacent device.
8. **All fetches blocked** — every value is snippet/estimate/memory; none is [FULL]. Numbers with "med"/"low" confidence (Cs_xWO₃ α, Eu α_405, the ×25 pressure scaling of the Lewittes check) should be re-verified against the primary PDFs before they enter the budget as anything but placeholders.

---

## Sources (via search snippets; none read in full — fetches blocked)

- Horvath, *Photophoresis – a Forgotten Force?*, KONA 31, 181 (2014) — review.
- Bluvshtein, Krieger, Peter, *Photophoretic spectroscopy in atmospheric chemistry*, AMT 13, 3191 (2020) — EDB-PPS, k to 10⁻⁵ ±25–60 %.
- Lewittes, Arnold, Oster, *Radiometric levitation of micron sized spheres*, APL 40, 455 (1982).
- Pluchino, *Radiometric levitation of spherical carbon aerosol particles*, Appl. Opt. 22, 1861 (1983); *PP force at low Kn*, Appl. Opt. 22, 103 (1983).
- Loesche & Wurm, *Photophoretic Strength on Chondrules 2: Experiment*, arXiv 1408.1813 (2014); Kupper/Wurm, J. Aerosol Sci. 2014 (basalt, microgravity).
- Shvedov et al., *Giant optical manipulation*, PRL 105, 118103 (2010); Desyatnikov et al., Opt. Express 17, 8201 (2009).
- Jovanovic, *Photophoresis—light-induced motion...*, JQSRT 110, 889 (2009); Pahi et al., *Photophoretic Trapping: Fundamentals...*, ChemPhysChem (2026) / arXiv 2512.09401.
- *Prep & Char of Silica Aerogel Microspheres*, PMC5506966; Yang et al., IECR 63, 20925 (2024, microfluidic); pulmonary alginate aerogels, Pharm. Dev. Technol. 26(5) (2021); WO2018124979A2 (micron aerogel patent).
- *Effects of particle size of silica aerogel...*, J. Nanopart. Res. 20, 308 (2018); hollow-silica-NP aerogel, ACS ANM (2025).
- Staller, Gibbs, Cabezas, Milliron, *Quantitative Extinction Coefficients of ITO NC Ensembles*, Nano Lett. 19, 8149 (2019); ITO air-anneal arXiv 2211.04144; AZO PNAS 109 (2012); LaB₆ Materials 11, 2473 & JMR 2016; TiN oxidation refs (Adv. Opt. Mater. 2021; Opt. Mater. Express 9, 4751).
- Cs_xWO₃: NIR shielding films (RSC/Elsevier snippets, 0.9 mg/cm²→70 %, 90.9 % film); oxidation onset ~470 °C snippet; Nano 10, 2295 (2020, monodisperse NCs).
- BaSi₂O₂N₂:Eu EPJ Plus (2024) & JNN 16 (2016); β-SiAlON:Eu Chem. Mater. 30 (2018); CaAlSiN₃:Eu degradation refs; Sr₂Si₅N₈:Eu nanophosphor Sci. Rep. 10, 1613 (2020).
- InP α: BU Dennis lab (Chem. Mater. 2021); InP/ZnSe/ZnS thermal Coatings 11, 581 (2021); Zhao & Meijerink, ACS Nano 6, 9058 (2012); CsPbBr₃ thermal snippets; C-dots@silica Nano 10, 1063 & PMC12828719.
- Keith, PNAS 107, 16428 (2010); Azadi et al., Sci. Adv. 7, eabe1127 (2021); Schäfer et al., Nature 644, 362 (2025); Geints & Panina, arXiv 2402.03645 (2024); Janus PP refs.
- Safety: SAS inhalation (Food Chem. Toxicol. 2007; Inhal. Toxicol. 2018); ITO/indium-lung (PMC4752405, PMC3515663, PubMed 27343753); WO₃ NP (PMC9650236, PMC10302912); LED phosphor aspiration (ScienceDirect S2772416626000835).

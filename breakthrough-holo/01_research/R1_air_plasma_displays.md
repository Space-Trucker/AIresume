# R1: Laser-induced air-plasma volumetric displays: hard numbers

Compiled 2026-09-30 by a research subagent for `breakthrough-holo`. Scope: glowing points drawn in ordinary room air (no fog, no screen, no glasses).

**Access limits in this session (please read first)**
- WebFetch and curl were **blocked by the egress proxy** for every primary host tried: arxiv.org, export.arxiv.org, dl.acm.org, researchgate, semanticscholar, spectrum.ieee.org, the Keio/Tsukuba/univ-mlv PDF hosts, burton-jp.com, history.siggraph.org and wikipedia. The session's WebSearch budget also ran out part-way through.
- So **no primary PDF was opened**. The status tags mean:
  - **[S]** = the number appears in a search-engine snippet or summary of the listed URL. Treat it as secondary until someone re-reads the PDF.
  - **[R]** = recalled from general physics or literature knowledge and NOT verified this session. The URL given is where it should be checked.
  - **[E]** = ESTIMATE by me. The reasoning is shown.
- Confidence: **H** = abstract-level fact seen in 2 or more snippets. **M** = a single snippet, or a snippet from a secondary outlet. **L** = recalled or unverified. **E** = estimate.

---

## KEY NUMBERS

| Quantity | Value | Conditions | Source URL | Conf. |
|---|---|---|---|---|
| Burton/Keio Mark I dot rate | 100 dots/s | Nd:YAG 1064 nm, 100 Hz, 1 dot per pulse, galvo scan | https://www.spiedigitallibrary.org/conference-proceedings-of-spie/6803/680309/Laser-plasma-scanning-3D-display-for-putting-digital-contents-in/10.1117/12.768068.short | M [S] |
| Burton Mark III dot rate | 300 dots/s | 300 Hz source, Aug 2006, SIGGRAPH 2006 ETech | http://hvrl.ics.keio.ac.jp/paper/pdf/international_Conference/2008/EI2008_3D.pdf | M [S] |
| Burton 2011 "SRV-5000" dot rate | 50,000 dots/s (up from 300) | SIGGRAPH 2011 ETech "True 3D display" | https://dl.acm.org/doi/10.1145/2048259.2048279 | M [S] |
| Burton 2011 frame rate / volume | 10–15 fps (target 24–30); 20×20×20 cm | press coverage | https://newatlas.com/burton-true-3d-laser-plasma-display/20499/ | M [S] |
| Burton laser "power" | "1 kW infrared pulse laser", "1 kHz" (units ambiguous) | secondary blog | https://pangolin.com/blogs/news/aerial-3d-display-project | L [S] |
| Fairy Lights, System A | 800 nm, 1 kHz, 30–100 fs adjustable, up to 2 mJ (paper body) / "up to 7 mJ" (abstract) | Coherent amplifier | https://arxiv.org/abs/1506.06668 ; https://displaydaily.com/fairy-lights-holographic-display-under-development/ | H [S] |
| Fairy Lights, System B | 1045 nm, 200 kHz, 269 fs, up to 50 µJ (IMRA FCPA µJewel DE1050) | = 10 W average | https://patents.google.com/patent/US10228653B2/en | H [S] |
| Fairy Lights voxel rate | 4,000 dots/s (1 kHz × up to 4 SLM foci); 200,000 dots/s (200 kHz) | SLM multi-focus + galvo + varifocal lens | https://arxiv.org/abs/1506.06668 | H [S] |
| Fairy Lights power range | 0.05–1.84 W average, 1–4 simultaneous voxels; SLM rated ≤ 2 W | 1 kHz system ⇒ 50 µJ–1.84 mJ/pulse, ≈ 0.46 mJ/voxel at 4 foci [E] | https://arxiv.org/pdf/1506.06668 | M [S] |
| Fairy Lights display volume | ≤ 1 cm³ | "scalable with optics" | https://gizmodo.com/you-can-feel-these-plasma-holograms-made-with-femtoseco-1715036802 | H [S] |
| Plasma onset, 30 fs (Fairy Lights) | from 0.2 mJ pulse energy; spots < 10 µm | their focusing optics | https://digitalnature.slis.tsukuba.ac.jp/wp-content/uploads/2015/06/siggraph2015.pdf (the snippet mixed this PDF with the Keio EI2008 PDF, so attribution is uncertain) | L [S] |
| Skin-proxy (leather) damage | < 2000 ms (= 2000 shots): only ~100 µm holes, no heat damage; > 2000 ms: heat damage; ns laser burned leather in 100 ms | 30 fs and 100 fs at 1 W, 1 kHz; exposure 50–6000 ms | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10228653 | H [S] |
| fs plasma noise level | 77.2 dB SPL (max) | 40 fs pulses, 1 kHz (which paper is uncertain; appears in Fairy Lights snippet context) | https://arxiv.org/pdf/1506.06668 | L [S] |
| Pulse-shaping emission gain | ×1.82 emission intensity | GA-optimised spectral phase on an SLM, fs voxels (Tsai, Kumagai, …, Hayasaki) | https://opg.optica.org/ao/abstract.cfm?uri=ao-65-15-G69 | H [S] |
| SIGGRAPH 2024 dual-path display medium | **Xe-filled** rendering volume (not room air) | 2 × (fs laser + LC-SLM + galvo + varifocal) | https://dl.acm.org/doi/10.1145/3641517.3664387 | H [S] |
| Colour display laser (Kumagai 2021) | 1 kHz, 34 fs | colour via parabolic-mirror re-imaging + LC filter, or scattering | https://www.nature.com/articles/s41598-021-02107-3 | H [S] |
| fs air ionisation threshold vs τ | 8.7×10¹⁴ W/cm² (50 fs) → 2.7×10¹³ W/cm² (22 ps); E_th ∝ τ^x, x = 0.23–0.5 (50–500 fs), ≈ 0.8 (0.7–10 ps) | 800 nm; threshold = detectable fluorescence | https://wulixb.iphy.ac.cn/en/article/doi/10.7498/aps.57.354 | H [S] |
| Filament clamped intensity | ≈ 5–6.4×10¹³ W/cm²; n_e 10¹⁵–10¹⁸ cm⁻³ (typ. 10¹⁶) | 800 nm fs, weak focusing | https://link.springer.com/article/10.1134/S1054660X12010264 | H [S] |
| fs spark threshold power | 5.2 GW; > 85 % of energy absorbed well above threshold | fs, focused, air | https://link.springer.com/article/10.1134/S1063785014010052 | M [S] |
| Min fs energy for breakdown (tight focus) | ≈ 1–5 µJ (NA 0.1), 0.3–1.3 µJ (NA 0.2), 0.04–0.2 µJ (NA 0.5) | 800 nm, 100 fs, I_th = 1–5×10¹⁴ W/cm², Gaussian w₀ = λ/(πNA) | derived from the row above | E |
| ns 1064 nm threshold | 27 GW/cm² (≈ 2 mJ at 20 µm radius, 6 ns [E]) | no UV pre-ionisation | https://www.osti.gov/biblio/22036836 | H [S] |
| ns thresholds vs λ | 3.2×10¹⁰ (248 nm) … 5.1×10¹¹ W/cm²; ∝ λ² (MPI-seeded) | f = 117 mm lens, 50–150 µm spots | https://ui.adsabs.harvard.edu/abs/2019SPIE11063E..05G/abstract | M [S] |
| ns CO₂ vs Nd:YAG | ~10⁹ W/cm² (10.6 µm) vs ~10¹¹ W/cm² (1.06 µm) | ns, avalanche-dominated | https://arxiv.org/pdf/2404.10020 (snippet; attribution uncertain) | M [S] |
| ns plasma onset (moderate focus) | NIR 1064 nm abrupt at ≈ 55 mJ; UV 266 nm gradual from ≈ 8 mJ; NIR T ≈ 12,000 K at 10 µs (75 mJ) | Dumitrache, Limbach, Yalin 2016 | https://pubs.aip.org/aip/pop/article/23/9/093515/319659/Threshold-characteristics-of-ultraviolet-and-near | H [S] |
| Critical power P_cr (air) | 0.27 GW (248 nm); 3–3.3 GW (800 nm; measured 9.6 ± 1 GW for 40 fs); 5.3 GW (1030 nm); ~11 GW (1.5 µm) [E]; ~20 GW (2 µm) [E]; 125–250 GW (3.9 µm); ~0.5 TW (10.6 µm) [E, λ² scaling] | P_cr ∝ λ²/n₂ | https://www.rp-photonics.com/self_focusing.html ; https://ui.adsabs.harvard.edu/abs/2015NatSR...5.8368M/abstract | H/E |
| LWIR megafilament | clamped ~10¹² W/cm²; visible plasma channel above 800 GW; n_e 10¹⁴–10¹⁶ cm⁻³ | ps CO₂, ~10 µm | https://www.nature.com/articles/s41566-018-0315-0 | H [S] |
| ns spark kernel | ~0.3 mm, ~0.02 mm³; T_e peak > 100,000 K; optical depth ~1; broadband UV–vis continuum for the first ~200 ns | Q-switched Nd:YAG, 1 atm | https://opg.optica.org/ao/abstract.cfm?uri=ao-37-18-3977 | H [S] |
| Spark energy budget | radiation 22–34 %, shock 51–70 %, residual hot gas 7–8 % of absorbed energy | ns laser spark, air | https://www.sciencedirect.com/science/article/abs/pii/S0143816604001642 | M [S] |
| Spark energy budget vs E | deposited 85 % (60 mJ) → 92 % (102 mJ); shock share falls 83 % → 48 % (60–273 mJ) | ns 1064 nm | https://opg.optica.org/ao/abstract.cfm?uri=ao-62-19-5189 | H [S] |
| Air fluorescence yield (337 nm band) | 5.61 ph/MeV (AIRFLY 2013) [R]; 5.03 ph/MeV quoted elsewhere [S]; total 300–420 nm ≈ 20 ph/MeV [R] ⇒ radiant efficiency ≈ 7×10⁻⁵ [E] | electron-beam excitation, 1013 hPa, 293 K | https://lss.fnal.gov/archive/2012/pub/fermilab-pub-12-580-e.pdf ; https://arxiv.org/html/1401.4310 | M/L |
| N₂(C) quenching in air | p′(337) ≈ 15.9 hPa ⇒ fluorescence fraction ≈ 1/(1+1013/15.9) ≈ 1.5 %; τ_eff ≈ 0.6 ns (τ_rad ≈ 40 ns) | 1 atm | https://arxiv.org/pdf/astro-ph/0703132 | L [R]/E |
| Luminous efficacy of N₂ band emission | ≈ 0.2–1 lm per radiant W | CIE V(λ): V(380) = 4×10⁻⁵, V(390) = 1.2×10⁻⁴, V(400) = 4×10⁻⁴, V(430) = 1.2×10⁻² | CIE 1924 V(λ) table [R] | E |
| Lightning visible radiant efficiency | ≲ 1 % in 0.4–1.1 µm | return strokes | https://agupubs.onlinelibrary.wiley.com/doi/10.1029/JC087iC11p08913 | M [S] |
| Light output, fs vs ns display | fs: ≈ 1.5–8×10⁻⁵ lm per absorbed W (10 W ⇒ ~10⁻⁴–10⁻³ lm); ns spark: ≈ 0.7–6 lm per absorbed W (45 W ⇒ ~30–300 lm) | built from the fluorescence-yield, quenching, V(λ) and lightning rows | derived in §4 | E (±10×) |
| Filament O₃/NO/NO₂ | 10¹⁴ / 3×10¹² / 3×10¹³ molecules per pulse; local 10¹⁶ / 3×10¹⁴ / 3×10¹⁵ cm⁻³ | 800 nm, 80 fs, 180 mJ, 10 Hz ⇒ 5.6×10¹⁴ O₃ per J incident [E] | https://pubs.aip.org/aip/apl/article/97/2/021108/339090/Production-of-ozone-and-nitrogen-oxides-by-laser | H [S] |
| ns breakdown O₃ | ≈ 2×10¹² O₃ per breakdown (steady state) | ~10¹⁰ W/cm², ~2000 shots in a cell | https://pubmed.ncbi.nlm.nih.gov/14658160/ | M [S] |
| Lightning / spark NO yield | (9 ± 2)×10¹⁶ /J; 15×10¹⁶ /J (1 atm representative); lab spark (1.5 ± 0.5)×10¹⁷ /J; 15×10²⁵ NO per flash (×0.13–2.7) | | https://agupubs.onlinelibrary.wiley.com/doi/10.1029/93JD01018 ; https://acp.copernicus.org/articles/24/41/2024/ | M [S] |
| LIB acoustic peak | up to 181 dB re 20 µPa (22.7 kPa) at 3 cm | ns laser spark | https://www.sciencedirect.com/science/article/abs/pii/S0003682X03001683 | H [S] |
| LIB acoustic spectrum | ns: peaks at 30–70 and 80–120 kHz; ps (30 ps): 90–120 kHz; centre falls with intensity (ns 76 → 48 kHz, ps 111 → 92 kHz) | 7 ns vs 30 ps | https://opg.optica.org/ao/abstract.cfm?uri=ao-55-3-548 ; https://opg.optica.org/ao/abstract.cfm?uri=ao-56-24-6902 | H [S] |
| Ozone accumulation, 10 W fs display | ≈ 0.016 ppm/h (Petit yield) up to ≈ 10 ppm/h (corona-like 100 g/kWh on 10 W absorbed) | 50 m³ room, no removal | derived in §5 | E |
| NO accumulation, ns-spark display | ≈ 1–20 ppm/h | 45 W absorbed, 10¹⁶–1.5×10¹⁷ NO/J, 50 m³ | derived in §5 | E |

---

## 1. Aerial Burton / Keio / AIST (2006–2011)

- **Team and lineage.** AIST, Keio University (H. Saito, A. Asano, I. Fujishiro) and Burton Inc. (H. Kimura, T. Uchiyama). Presented as "Laser produced 3D display in the air" (Kimura, Uchiyama, Yoshikawa; SIGGRAPH 2006 ETech). The AIST press release (Feb 2006) described a "high-quality, high-brightness infrared pulse laser" with galvo XY scanning and a linear-motor Z stage. https://phys.org/news/2006-02-japanese-device-laser-plasma-3d.html [S]
- **Mark I (2D).** Nd:YAG, **1064 nm, 100 Hz ⇒ 100 plasma dots/s**. Drew an "SOS" 2D image. Built from four blocks: source, focusing, scanning, controller. SPIE 6803, 680309 (2008) [S].
- **Mark II.** The first 3D version (2006).
- **Mark III.** **300 Hz ⇒ 300 dots/s**, Aug 2006, SIGGRAPH 2006 ETech (Boston) [S].
- **2011 "True 3D display" (SIGGRAPH 2011 ETech; Kimura, Asano, Fujishiro, Nakatani, Watanabe).** SRV (Super Real Vision)-5000, "300 → **50,000 points/s**". Press reports give **10–15 fps** (target 24–30 fps), a **20×20×20 cm** volume and "colour by combining R, G, B lasers". The colour claim is secondary and physically unexplained, so low confidence. https://newatlas.com/burton-true-3d-laser-plasma-display/20499/ [S]
  - One press piece says "up from ~1,000 dots/s in 2006". That conflicts with 100–300 dots/s in the Keio paper; trust the paper.
- **Laser class.** Secondary sources say "1 kW infrared pulse laser" at "1 kHz". This is probably peak or electrical power; it is not a verified pulse energy. https://pangolin.com/blogs/news/aerial-3d-display-project [S, L]
- **Pulse energy: not found. [E]** For ns 1064 nm breakdown in clean air you need about 2 mJ with a 20 µm-radius focus (27 GW/cm² × π(20 µm)² × 6 ns), and tens of mJ with the moderate focusing needed for a 20 cm throw (Dumitrache 2016 saw abrupt onset at ≈ 55 mJ).
  - A bright visible ns spark therefore implies **~10–100 mJ/pulse, i.e. 10–100 W average at 1 kHz**. Treat this as an order of magnitude.
- **Noise.** Each ns spark is a small blast wave (see §6). With 1 dot per pulse at ≤ 1 kHz, it produces an audible 1 kHz-comb "buzz"; press describes it as loud. No dB figure was found.
- **Physics.** Thermal (avalanche) ns sparks give a white, continuum-plus-line emission. They are much brighter per voxel than fs microplasmas, but they burn skin (the Fairy Lights leather test: ns burned leather in 100 ms) and produce much more NOx (§5).

## 2. Fairy Lights in Femtoseconds (Ochiai, Kumagai, Hoshi, Rekimoto, Hasegawa, Hayasaki)

Published as SIGGRAPH 2015 poster/ETech, ACM TOG 35(2) 2016 (doi 10.1145/2850414), arXiv 1506.06668, patent US10228653B2.

- **Architecture.** fs laser → LCOS-SLM (Hamamatsu; showing a CGH for simultaneously addressed voxels) → XYZ scanner (galvo + varifocal lens) → objective. https://arxiv.org/abs/1506.06668 [S]
- **System A.**
  - Coherent amplifier, **800 nm, 1 kHz, 30–100 fs adjustable**. The paper body gives "up to **2 mJ**"; the abstract gives "up to **7 mJ**/pulse".
  - Hayasaki's lab laser (SPIE Newsroom 2016) is **800 nm, 1 kHz, < 130 fs, 7 W**, which likely explains the 7 mJ figure (possibly a third system). https://www.spie.org/news/6515-volumetric-display-created-by-holographic-laser-drawing [S]
- **System B.** **IMRA FCPA µJewel DE 1050: 1045 nm, 200 kHz, 269 fs, ≤ 50 µJ** (= 10 W average) [S].
- **Voxel rate.**
  - **4,000 dots/s** on the 1 kHz system, via up to 4 SLM foci per pulse.
  - **200,000 dots/s** on the 200 kHz system, 1 voxel per pulse.
  - [E] At 30 fps that is ≈ 133 or ≈ 6,700 voxels per frame.
- **Power and energy per voxel.** Experiments spanned **0.05–1.84 W with 1–4 simultaneous voxels**. At 1 kHz that is 50 µJ to 1.84 mJ per pulse, i.e. **≈ 0.46 mJ per voxel at 4 foci** before optics losses [E]. The SLM is not rated beyond 2 W [S].
  - [E] The number of SLM foci is limited by SLM power handling, not by the physics. With a 7 mJ pulse and roughly 0.2 mJ/voxel (the snippet's 30-fs plasma onset), about 35 foci per pulse would be energetically possible.
- **Volume and resolution.** Workspace **≤ 1 cm³**, "scalable". Snippets mention spots "< 10 µm" [S, L].
- **Brightness and sound.** They measured brightness against input energy; "brighter plasma emission tends to be accompanied by louder sound" [S]. No absolute luminance was found (see gap G1).
  - One snippet gives **max 77.2 dB SPL with 40 fs pulses**, with a spectrum made of **1 kHz comb lines** (1 kHz rep rate) spanning < 20 Hz to about 20 kHz. Which paper this comes from is unverified. https://arxiv.org/pdf/1506.06668 [S, L]
- **Skin-safety experiment (cow leather as a skin proxy).** System A at 30 fs and 100 fs, 1 W (≈ 1 mJ/pulse at 1 kHz), exposures of 50–6000 ms.
  - **< 2000 ms (2000 shots): only ~100 µm holes, no heat damage.**
  - **> 2000 ms: heat effects around the holes.**
  - For comparison, a **ns laser burned the leather within 100 ms**.
  - https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10228653 [S]
  - [E] The implication is that about 1 mJ/shot fs plasma at a fixed spot is tolerable for ≲ 1–2 s. Microscopic ablation (a 100 µm hole) still occurs, so this is **not "harmless"**. It shows only that there is no thermal burn in a brief touch.
- **Haptics.** Touching a voxel gives a perceptible impulse, attributed to the plasma shock wave. The paper and press say "touchable". No force or pressure threshold was found [S].
  - Follow-up [R]: "Cross-Field Aerial Haptics" (Ochiai, Kumagai, Hoshi, Hasegawa, Hayasaki, CHI 2016) combined fs-plasma haptics with ultrasound phased arrays. Verify at dl.acm.org.
- **Audio.** The patent claims "generating spatial audio using femtosecond lasers", i.e. plasma voxels used as aerial speakers [S].
- **Follow-ups by Hayasaki / Kumagai (Utsunomiya), all [S]:**
  - Volumetric display with holographic fs laser accesses (DH 2018).
  - Volumetric bubble display in liquid (CLEO-PR 2018).
  - "Projection of aerial volumetric graphics formed by fs excitation" (DH 2019): re-imaging with parabolic mirrors.
  - Aerial re-imaging with a colour filter (OSA 3D 2021; SPIE 11788 117880K). The native voxel colour is described as "**monochromatic bluish white**".
  - Colour volumetric display using drawing-space separation (Sci Rep 11:22728, 2021; **1 kHz, 34 fs**): colour taken from broadband emission, or from scattering.
  - "Colored voxels…" (DH 2022).
  - **SIGGRAPH 2024 ETech "Dual-path holographic laser rendering"**: centimetre-scale graphics bright enough "under normal room lighting", but in an **Xe-filled volume**, which means room-air brightness is still not demonstrated.
  - **JSID 2025 "Fist-sized aerial volumetric display"**: luminous intensity and size measured against lens focal length; a **100 mm focal-length lens** is enough for a centimetre-scale volume.
  - Springer 2025 chapter "From fingertip to fist-sized graphics and color".
  - **Appl. Opt. 65(15) G69 (2026), Tsai et al.: ×1.82 emission** by adaptive spectral-phase pulse shaping (genetic algorithm on the SLM).
  - Links: https://sid.onlinelibrary.wiley.com/doi/10.1002/jsid.2025 · https://link.springer.com/chapter/10.1007/978-981-96-9782-3_26
- **Pixie Dust Technologies, and Chinese, Korean or European fs aerial-display groups 2018–2026:** nothing found in the searches (see gap G6). The field appears to be led by Utsunomiya (Hayasaki/Kumagai) and Tsukuba (Ochiai).

## 3. Breakdown thresholds, densities, sizes, self-focusing

**Femtosecond / picosecond (multiphoton or tunnel ionisation dominated)**
- 800 nm threshold intensity vs pulse duration: **8.7×10¹⁴ W/cm² at 50 fs, falling to 2.7×10¹³ W/cm² at 22 ps**. Threshold energy scales as E_th ∝ τ^0.23–0.5 for 50–500 fs and τ^0.8 for 0.7–10 ps. Acta Phys. Sin. 57, 354 (2008), https://wulixb.iphy.ac.cn/en/article/doi/10.7498/aps.57.354 [S]
- Clamped intensity in filaments ≈ **5–6.4×10¹³ W/cm²**, largely independent of pressure and power. Filament n_e ≈ **10¹⁵–10¹⁸ cm⁻³** (typically 10¹⁶), filament diameter ~100 µm [S, R].
  - Tight focusing (NA > ~0.08) moves the regime from filamentation to breakdown, with higher n_e. The 2010 study used NA 0.12 and 2.4–47 mJ. https://opg.optica.org/oe/fulltext.cfm?uri=oe-18-25-26007&id=208459 [S]
  - [R] At full single ionisation of air, n_e ≈ 2.5×10¹⁹ cm⁻³, the upper bound for tight-focus fs microplasmas.
- fs spark: threshold **power 5.2 GW**; **> 85 %** of pulse energy absorbed when well above threshold. Tech. Phys. Lett. 2014 [S].
- **[E] Minimum fs energy for breakdown vs NA.** Formula: E_th ≈ I_th·(πw₀²/2)·τ with w₀ = λ/(πNA). This is paraxial, so it is optimistic at NA 0.5.

| λ, τ | I_th assumed | NA 0.1 | NA 0.2 | NA 0.5 |
|---|---|---|---|---|
| 800 nm, 100 fs | 1–5×10¹⁴ W/cm² | 1.0–5.1 µJ | 0.26–1.3 µJ | 0.04–0.2 µJ |
| 1030 nm, 270 fs | 1–3×10¹⁴ W/cm² | 4.5–14 µJ | 1.1–3.4 µJ | 0.2–0.5 µJ |

  - Peak powers of 10–50 MW are far below P_cr, so tight focusing avoids filamentation.
  - "Threshold" means barely detectable. A visible voxel took about 50 µJ (200 kHz) to about 0.2–0.5 mJ (1 kHz) in Fairy Lights, with lower NA and long working distance.
- **Critical power P_cr = 3.77λ²/(8πn₀n₂)** (n₂(air) ≈ 3–5×10⁻¹⁹ cm²/W).
  - Values: 248 nm 0.27 GW; 800 nm ≈ 3–3.3 GW (measured 9.6 ± 1 GW for 40 fs, where rotational Raman is not yet active); 1030 nm 5.3 GW.
  - [E, λ² scaling]: 1.5 µm ≈ 11 GW; 2 µm ≈ 20 GW; 10.6 µm ≈ 0.5 TW.
  - 3.9 µm: 125–250 GW (Mitrofanov 2015, Sci Rep 5, 8368; > 200 GW, > 20 mJ carried in a single filament).
  - 10 µm megafilament (Tochitsky 2019, Nat. Photon. 13, 41): clamped at ~10¹² W/cm²; a visible plasma channel appears above 800 GW, n_e 10¹⁴–10¹⁶.
  - Sources: https://www.rp-photonics.com/self_focusing.html · https://www.nature.com/articles/s41566-018-0315-0 [S]
  - [E] Design corollary: at low NA (long throw), keep the peak power below P_cr or the beam filaments before the intended voxel. At 800 nm/100 fs that means E ≲ 0.3–1 mJ; at 1030 nm/270 fs, E ≲ 1.4 mJ.
- Mid-IR ablation plasmas (2.05 µm vs 800 nm) have lower n_e and T. https://pubs.aip.org/aip/jap/article/118/4/043107/382605 [S]
- At 1.5 µm, air ionisation is tunnel-like. No clean 1.5 or 2 µm fs air-breakdown intensity was found (gap G3).

**Nanosecond (avalanche dominated; seed electrons and aerosols matter)**
- 1064 nm, 6 ns, 20 µm-radius focus: **27 GW/cm²** without UV pre-ionisation (JAP 111, 073302, 2012). [E] That is ≈ 2 mJ. Overlapping 266 nm light lowers it. https://www.osti.gov/biblio/22036836 [S]
- 248–1064 nm at 50–150 µm spots: **3.2×10¹⁰ (248 nm) to 5.1×10¹¹ W/cm²**, scaling ∝ λ² (multiphoton-seeded, SPIE 11063, 2019) [S].
- By contrast, 10.6 µm ns breaks down at **~10⁹ W/cm²** versus ~10¹¹ W/cm² at 1.06 µm, because avalanche is more efficient at long λ; the threshold also falls as the spot gets larger [S].
- 532 nm needs 37 % less energy than 1064 nm (Phuoc, 5.5 ns) [S]. Breakdown intensities of 10¹²–10¹⁴ W/cm² are cited for 150–3000 Torr in combustion gases [S].
- Threshold defined as a total of **~10⁶ electrons** (10 ns, 1 atm). At 100 ps there is no sharp threshold. https://pubs.aip.org/aip/jap/article/119/17/173303/142005 [S]
- Moderate focus: NIR absorption starts abruptly at **≈ 55 mJ** and is always accompanied by intense emission. UV (266 nm) absorption starts at ≈ 8 mJ, and can occur *without* visible emission. https://www.osti.gov/pages/biblio/1468934 [S]
- Plasma size: **~0.3 mm kernel, 0.02 mm³** in the first tens of ns; T_e > 10⁵ K; optical depth ~1 (Borghese & Merola 1998) [S].
  - [R] Later sparks grow to mm size, elongated toward the laser, with n_e ~10¹⁸–10¹⁹ cm⁻³ at tens of ns (Stark broadening). "Lifecycle of laser-produced air sparks": https://www.osti.gov/pages/servlets/purl/1454740

## 4. Emission: spectra, yields, quenching, colour

- **fs microplasma / filament spectrum [R, standard spectroscopy]:**
  - N₂ second positive system C³Πu→B³Πg: **315.9, 337.1, 357.7, 380.5, 399.8, 405.9 nm**.
  - N₂⁺ first negative system B²Σu⁺→X²Σg⁺: **391.4, 427.8 nm**.
  - Weak continuum at high density.
  - The eye sees it as "**bluish white**" (Kumagai, [S]); the emission is almost entirely UV-A or violet.
- **ns spark spectrum [S + R]:** intense structureless UV–vis continuum (bremsstrahlung + recombination) for the first ~100–200 ns. Lines then appear: N II 500.5/567.9 nm, O I 777.4/844.6 nm, N I 742–746/868 nm, Hα 656.3 nm. The spark looks white.
- **Fluorescence yield (electron-excited air; the best-measured proxy):**
  - Y₃₃₇ = **5.61 photons/MeV** at 1013 hPa, 293 K. This is the AIRFLY 2013 result (Astropart. Phys. 42, 90) [R]; a snippet also quotes 5.03 photons/MeV. https://lss.fnal.gov/archive/2012/pub/fermilab-pub-12-580-e.pdf
  - The 337 band is ≈ 25–27 % of the 300–420 nm total ⇒ **≈ 20 photons/MeV** in total [R].
  - [E] Radiant efficiency = 20 × 3.6 eV / 1 MeV ≈ **7×10⁻⁵** of deposited energy.
- **Quenching [R]:**
  - N₂(C) radiative lifetime ≈ 37–42 ns. Air reference pressure p′(337) ≈ 15.9 hPa (AIRFLY; pressure dependence at https://arxiv.org/pdf/astro-ph/0703132).
  - [E] Fluorescence survival fraction at 1 atm ≈ 1/(1+1013/15.9) ≈ **1.5 %**, so τ_eff ≈ 0.6 ns.
  - N₂⁺(B) p′(391) ≈ 3 hPa [R] ⇒ ≈ 0.3 %.
  - Temperature and humidity change the yield by up to 20 % [S].
- **Luminous efficacy [E].** CIE V(λ) [R]: V(380) = 3.9×10⁻⁵, V(390) = 1.2×10⁻⁴, V(400) = 4.0×10⁻⁴, V(410) = 1.2×10⁻³, V(430) = 1.16×10⁻².
  - Weighting N₂/N₂⁺ band intensities gives ≈ **0.2–1 lm per radiant W**, versus ~300 lm/W for a white LED's radiation.
  - ⇒ [E] Luminous yield of fs air microplasma ≈ 7×10⁻⁵ × (0.2–1) ≈ **1.5–8×10⁻⁵ lm·s per J deposited**.
  - A 10 W fs display would emit ≈ **10⁻⁴–10⁻³ lm** in total. That is visible in a dark room (0.5 m from 1×10⁻⁵ cd gives ~4×10⁻⁵ lx, far above scotopic point-source threshold) but lost against room-light backgrounds.
  - Uncertainty is about ±10×: the laser-plasma excitation path differs from electron-beam excitation, and the continuum Kumagai used for colour extraction adds visible light.
- **ns spark light [E].** Radiation is **22–34 %** of absorbed energy [S], mostly UV at T_e > 10⁵ K.
  - Assume ~0.5–3 % of absorbed energy ends up in 400–700 nm. The low end is half of lightning's ≲ 1 % into 0.4–1.1 µm [S]; the high end allows ~10 % of the radiated share landing in the visible.
  - At ~150–200 lm per visible W, that gives ≈ **0.7–6 lm·s per J absorbed**.
  - For a 1 kHz × 50 mJ source (≈ 45 W absorbed), that is **~30–300 lm**, roughly 10⁴–10⁵ × more light per absorbed watt than fs microplasma.
  - This is the core brightness-versus-safety trade-off.
- **Lightning:** upper limit ~**1 %** radiative efficiency in 0.4–1.1 µm for subsequent strokes. https://agupubs.onlinelibrary.wiley.com/doi/10.1029/JC087iC11p08913 [S]
- **Electric sparks:** no luminous-efficiency number found (gap G2).
- **Timing.** fs voxel light is emitted within ~ns (quenched), so there is no afterglow and persistence is only in the eye. ns sparks glow for ~µs.

## 5. Chemistry: O₃, NOx

- **fs filaments (Petit, Henin, Kasparian, Wolf, APL 97, 021108, 2010):**
  - **10¹⁴ O₃, 3×10¹² NO, 3×10¹³ NO₂ per pulse**; local concentrations 10¹⁶, 3×10¹⁴, 3×10¹⁵ cm⁻³.
  - Laser: Teramobile, 800 nm, 80 fs, 180 mJ, 10 Hz.
  - [E] ⇒ **5.6×10¹⁴ O₃ per J** of incident energy (per J *deposited* is much higher, because filaments absorb only a fraction).
  - https://access.archive-ouverte.unige.ch/access/metadata/a25564ff-6166-46e6-98dd-14c3c54ba233/download [S]
- **ns breakdown (Gornushkin et al., Appl. Spectrosc. 57, 1442, 2003):** ≈ **2×10¹² O₃ per single breakdown** (steady state, model-consistent). Measured with ~2000 shots at ~10¹⁰ W/cm². Pulse energy not in the snippet. https://pubmed.ncbi.nlm.nih.gov/14658160/ [S]
- **Lightning / electric spark NO:**
  - (9 ± 2)×10¹⁶ NO/J; "15×10¹⁶ /J at 1 atm representative"; lab discharges **(1.5 ± 0.5)×10¹⁷ /J**.
  - Per flash: 15×10²⁵ molecules (uncertainty factor 0.13–2.7; Schumann & Huntrieser 2007).
  - Sources: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/93JD01018 · https://acp.copernicus.org/articles/24/41/2024/ [S]
- **Corona / DBD ozone [R]:** ~50–100 g/kWh with air feed, ~150–250 g/kWh with O₂ feed (Kogelschatz 2003, Plasma Chem. Plasma Process. 23, 1).
  - [E] 100 g/kWh = **3.5×10¹⁷ O₃/J**.
- **[E] Room-air accumulation**
  - Assumptions: 50 m³ room = 1.23×10²⁷ molecules, so 1 ppm = 1.23×10²¹ molecules; no decay or ventilation.
  - fs display, 10 W incident, Petit yield: 5.6×10¹⁵ O₃/s ⇒ **0.016 ppm/h**.
  - fs display, worst case, 10 W *absorbed* at corona yield: 3.5×10¹⁸/s ⇒ **~10 ppm/h**.
  - ns-spark display, 45 W absorbed, 10¹⁶–1.5×10¹⁷ NO/J ⇒ **~1–20 ppm/h NO**, which oxidises to NO₂.
- **Limits [R]:**
  - O₃: OSHA PEL 0.1 ppm TWA; FDA 21 CFR 801.415 0.05 ppm for devices.
  - NO₂: WHO 1-h 200 µg/m³ ≈ 0.1 ppm; NIOSH STEL 1 ppm.
  - ⇒ ns sparks indoors need strong ventilation or catalytic scrubbing. For fs, the answer hinges on the unknown per-absorbed-J yield of tight-focus microplasmas (gap G4).

## 6. Acoustics

- **Peak pressure:** up to **181 dB re 20 µPa (22.7 kPa) at 3 cm** from a laser spark (Qin & Attenborough, Appl. Acoust. 2004). https://www.sciencedirect.com/science/article/abs/pii/S0003682X03001683 [S]
  - Systematic study at 25–100 mJ: peak pressure and conversion efficiency rise with energy. https://www.sciencedirect.com/science/article/abs/pii/S0022460X23004492 [S]
- **Spectrum:**
  - ns (7 ns) sparks peak at **30–70 kHz and 80–120 kHz**; ps (30 ps) sparks at **90–120 kHz**. ns sparks radiate more acoustic energy. https://opg.optica.org/ao/abstract.cfm?uri=ao-55-3-548 [S]
  - Centre frequency falls with intensity (ns 76 → 48 kHz; ps 111 → 92 kHz): Appl. Opt. 56, 6902 [S].
  - fs filament sources: a first-order high-pass spectrum from < 20 Hz to about 20 kHz and beyond; at 1 kHz rep rate the spectrum is a 1 kHz comb. https://pubs.aip.org/asa/jasa/article/146/3/EL212/995938 [S]
- **Energy fraction to shock:** 83 % → 48 % of incident energy (60 → 273 mJ, ns), and 51–70 % of absorbed energy in another study [S].
  - Blast size scale [E]: R₀ = (E/p₀)^{1/3} ≈ 0.46 mm for 10 µJ and 7.9 mm for 50 mJ. Beyond R₀ the wave is weak and acoustic.
- **Sedov–Taylor:** R(t) = ξ(E/ρ₀)^{1/5} t^{2/5}, ξ ≈ 1.03 for γ = 1.4 [R].
  - Laser-spark studies (e.g. the Appl. Opt. 2023 energy-partition paper; Harilal et al. "Lifecycle of laser-produced air sparks") use ST fits to the shock radius to infer blast energy. Agreement holds in the strong-shock window R ≲ R₀ [R].
  - [E] 10 µJ blast: R ≈ 0.39 mm at 1 µs, so ST is only valid for ≲ 1 µs.
- **Design insight [E].** A uniform pulse train at f_rep > 20 kHz (e.g. 200 kHz) puts its periodic sound in the ultrasound band.
  - Audible sound then comes only from *modulation*: frame rate, voxel on/off patterns, changes in energy per voxel.
  - This is the parametric-speaker mechanism behind the patent's "aerial audio".
  - At ≤ 20 kHz rep rates (Burton 1 kHz; Fairy A 1 kHz) the buzz is directly audible (77.2 dB SPL snippet).
  - Ultrasound exposure limits [R]: ACGIH ceiling ~105–115 dB in 1/3-octave bands 20–100 kHz. Impulse limit: OSHA 140 dB peak.

## 7. Enhancing emission per joule: double pulse, shaping, sustained plasmas

- **fs pulse shaping: ×1.82 voxel emission** (GA-optimised spectral phase; Tsai … Hayasaki, Appl. Opt. 65, G69, 2026) [S]. This is the only display-specific enhancement figure found.
- **Multi-foci per pulse via SLM:** raises voxel rate (×4 in Fairy Lights) but not photons per joule.
- **fs + ns reheating:** a fs filament or spark seeds electrons, so a ns pulse couples efficiently below its own breakdown threshold. Studied in "Characteristics of fs laser-induced filament and energy coupling by ns pulse in air" (JAP 137, 213303, 2025; arXiv 2502.00875); no numbers were retrieved [S].
  - UV (266 nm) pre-ionisation lowers the 1064 nm threshold below 27 GW/cm² [S].
- **Double-pulse LIBS [R]:** signal enhancements of ~2–100× reported for solid targets (Babushok et al., Spectrochim. Acta B 61, 999, 2006). Gas-phase double-pulse gains are smaller and poorly quantified (gap G5).
- **Continuous optical discharge / laser-sustained plasma [R]:**
  - CO₂-laser COD in 1 atm air needs ~kW-class CW power (Raizer, *Laser-Induced Discharge Phenomena*).
  - Commercial LDLS sources sustain Xe plasmas at > 10 bar with ~100 W-class near-IR lasers.
  - "Orthogonal laser-sustained plasma" as a bright broadband source: https://www.nature.com/articles/s41377-024-01602-2 [S]
  - [E] Not viable for scanned, point-addressable room-air voxels at acceptable power.
- **[E] Rep-rate accumulation.** At ≥ 100 kHz, residual heating, density depletion (the "density hole", ms recovery) and long-lived metastables from earlier pulses can alter the threshold at nearby voxels. Rosenthal/Milchberg measured density holes and energy deposition. https://opg.optica.org/ol/abstract.cfm?uri=ol-41-16-3908 [S; no numbers retrieved]

## 8. Safety analyses found

- **Skin:** the Fairy Lights leather test (numbers in §2) is the only quantitative skin-contact data found. Takeaway: fs at 1 mJ/1 kHz causes µ-ablation holes but no heat damage for < 2 s; ns burns within 100 ms.
- **Eye [R]:** the beam beyond the focus diverges toward viewers.
  - The retinal-hazard region is 400–1400 nm, so 800 nm and 1030 nm beams fall in it.
  - 1.4–2.6 µm is cornea/lens-only, with MPE orders of magnitude higher (ANSI Z136.1 / IEC 60825-1).
  - ⇒ 1.5–2 µm drivers are eye-safer, but their fs breakdown needs more energy (gap G3). All such systems are Class 4.
- **UV from the plasma [E]:** emission is mostly 316–400 nm, and the total radiant output is ≪ 1 mW for a 10 W fs display. It is negligible against UV TLVs at > 10 cm.
- **Ozone / NOx / noise:** no dedicated published safety analysis of aerial plasma displays was found. The §5–6 estimates suggest NOx dominates for ns systems and ultrasound or audible modulation for fs systems (gap G7).
- Kumagai et al. claim "full-colour and touchable graphics without damage to the human body" and "user safety" (SIGGRAPH 2024, but in Xe). No exposure data was retrieved [S].

---

## Gaps / unknowns

- **G1.** No absolute luminance, luminous intensity or photons per voxel for any fs air display was found. The JSID 2025 paper has luminous intensity vs focal length; get its PDF. The brightness numbers in §4 are estimates (±10×).
- **G2.** No measured luminous efficiency (lm/W) was found for laser sparks or lab electric sparks. Only a lightning upper limit (~1 %, 0.4–1.1 µm) is available.
- **G3.** No clean fs air-breakdown intensity or energy thresholds at 1.5 µm, 2 µm or 3.9 µm under tight focus (NA 0.1–0.5) were found. The NA-vs-energy table is a paraxial estimate.
- **G4.** No O₃/NOx yield per *absorbed* joule was found for tightly focused fs microplasmas (µJ, 100 kHz). The room estimate spans 0.016 to ~10 ppm/h. This is the key measurement to make.
- **G5.** Double-pulse or fs+ns enhancement factors for *gas-phase* air emission were not retrieved. Only the ×1.82 pulse-shaping result is display-specific.
- **G6.** Pixie Dust Technologies has no plasma-display product or paper found. No Chinese, Korean or European fs aerial-display groups (2018–2026) were identified.
- **G7.** No published integrated safety analysis (eye + skin + O₃ + noise) of aerial plasma displays was found.
  - Burton's pulse energy and noise level are unknown.
  - The 77.2 dB SPL figure is not tied to a verified source.
- **G8.** Discrepancy to resolve: Fairy Lights System A is described as "up to 2 mJ" in one place and "up to 7 mJ" in another, possibly because there were 3 systems. Re-read arXiv 1506.06668 Table 1 when egress allows.
- **G9.** The recalled AIRFLY numbers (5.61 ph/MeV, p′ = 15.9 hPa), ANSI/OSHA limits and corona yields need a first-hand check.

# R6: Emitter particles for IR-trapped, self-luminous motes

**Question.** Which 5–50 µm particles, held in air by an IR trap, can emit visible light in all directions while powered by that same beam or a co-propagating one, so that no visible beam crosses the room? How efficient are they, how long do they last, and how much heat can they take?

**Method and caveats.** Web search only. WebFetch was blocked for every publisher, so figures come from search snippets and abstracts. The session's web-search budget (200 calls) ran out before the micro-LED and photovoltaic numbers could be checked. Labels:
- **[SNIPPET]**: quoted from a search-result abstract or snippet.
- **[MEMORY]**: from the model's recall, not re-checked this session.
- **[ESTIMATE]**: my calculation. Scripts are in the session scratchpad and use `mote/physics.py` (its V(λ) table and its k_air ∝ T^0.82).
- **[FULL]**: read in full. Nothing in this file is [FULL].

**Definitions.** UCQY = emitted photons / absorbed photons. Its ceiling is 50 % for a two-photon process and 33 % for three-photon. Power efficiency (PCE) = UCQY × λ_pump/λ_emit. lm/W_abs means lumens per watt of IR the particle actually absorbs, which is not the same as the power sent into the room.

## KEY NUMBERS

| Quantity | Value | Conditions | Source | Label | Conf. |
|---|---|---|---|---|---|
| Max UCQY, β-NaYF4:Yb,Er micro-particles | **10.5 %** | 3 µm particles; 980 nm; power density varied over 4 decades | Kaiser et al., Nanoscale 2017 | SNIPPET | high |
| UCQY, micro-sized NaYF4:Yb,Er | **10.2 %** at 20 W/cm² (nano: 0.32 %) | 980 nm | Khosh Abady/Rentzepis, Sci Rep 2023 | SNIPPET | high |
| UCQY, 25 nm NaYF4:17Yb,3Er nanoparticles | 0.6 % (powder), 2.1 % (dispersed) | maximum over the power range | Kaiser 2017 | SNIPPET | high |
| Record nanocrystal UCQY (core/shell) | **~9 %** (18 % Yb, 2 % Er); ~7 % at 98 % Yb | ~25 nm core, thick shell, OH-free | Homann/Kraft, Nano Res 2022 | SNIPPET | high |
| Core/shell size penalty | 45 nm ≈ bulk. 15 nm: 3× below bulk at 100 W/cm², ~10× below at 1 W/cm² | 980 nm | Homann, Angew 2018 | SNIPPET | high |
| Older bulk benchmark | 3 % (bulk); 0.005–0.3 % (10–100 nm NPs) | 980 nm; ~150 W/cm² (power from memory) | Boyer & van Veggel, Nanoscale 2010 | SNIPPET | high |
| Early phosphor "efficiency" | green up to 4 %; red and blue 1–2 % | Yb,Er and Yb,Tm crystals/powders, ~980 nm | Page et al., JOSA B 1998 | SNIPPET | med |
| Blue Tm UCQY (nanoparticles) | total ~2 % (mostly 794 nm NIR); **blue 480 nm ~6×10⁻⁵** | LiYF4:Yb,Tm in toluene, 5 W/cm² | Meijer et al., PCCP 2018 | SNIPPET | high |
| LiYF4:Yb,Er core/shell UCQY | 1.25 % max | ~40 nm; 180 W/cm² | Nano Res 2020 | SNIPPET | high |
| Er-only UCQY, 1523 nm pump (mostly NIR out) | **12.0 % internal** (8.6 % external) | β-NaYF4:25 % Er; 0.402 W/cm² | Fischer et al., J Lumin 2014 | SNIPPET | high |
| Er-only UCQY, broadband ~1523 nm | **16.2 ± 0.5 %** | β-NaYF4:10 % Er; 227 W/cm² | MacDougall, Opt Express 2012 | SNIPPET | high |
| Er-sensitised UCQY, 1532 nm (visible, red-rich) | up to **3.71 %** | NaErF4:Tm@NaGdF4 core/active shell | J Lumin 2019 | SNIPPET | med |
| Er nanocrystals at 1490 nm | ~1.2 ± 0.1 % | colloidal LiYF4:Er | ACS Nano 2012 (PMC3430509) | SNIPPET | med |
| Dye-sensitised UC (800 nm) | UCQY 4.8 %; energy efficiency 9.3 %; "UCQE" 19 %; σ = 1.47×10⁻¹⁴ cm² per NP | IR-808-dye / core-shell fluoride | Chen et al., Nano Lett 2015 | SNIPPET | med |
| Yb³⁺ absorption cross-section at ~980 nm | **~0.9–1.2×10⁻²⁰ cm²** | fluoride hosts | snippet (9×10⁻²¹); 1.2×10⁻²⁰ from memory | SNIPPET/MEMORY | med |
| Single-pass absorption of one mote at 976 nm | 20 % Yb: **1.4 % (5 µm) → 5 % (20 µm)**; 98 % Yb: 6.5 % → 24 % | α = N_Yb·σ, path = d (mean chord 2d/3 gives ~1.5× less) | this work | ESTIMATE | med |
| Luminous efficacy, Er green/red at saturation | **60–120 lm/W_abs** | UCQY 9–10 %; 100 % green gives 118 | this work | ESTIMATE | med |
| Luminous efficacy, Tm blue 475 nm | **0.16–1.6 lm/W_abs** | blue UCQY 0.1–1 % | this work | ESTIMATE | low |
| Luminous efficacy, Er under 1532 nm (visible only) | **~3–10 lm/W_abs** | visible UCQY 1–4 % | this work | ESTIMATE | low |
| Heat limit per mote in air (ΔT = 200 K) | 5 µm: 0.21 mW; 20 µm: 0.82 mW; 50 µm: 2.05 mW of heat | continuum conduction, 1 atm | this work | ESTIMATE | high |
| Brightest Er mote under that limit | 20 µm: **0.06–0.11 lm (5–9 mcd)**; 5 µm: 15–28 mlm | assumes 85 % of absorbed power becomes heat; thermal quenching ignored | this work | ESTIMATE | med |
| Intensity at which the heat limit is reached | 20 µm: **~1.3 kW/cm² (98 % Yb) to 5.7 kW/cm² (20 % Yb)** | as above | this work | ESTIMATE | med |
| UC at high temperature | bare NaYF4:Yb,Er NPs emit to 600 K, then fail (ligand oxidation, coalescence); **silica-coated NPs stable 300↔900 K** | thermometry use | Geitenbeek et al., JPCC 2017 | SNIPPET | high |
| NaYF4 thermal limits | cubic→hex 400–450 °C; "melting ~670 °C"; luminescence loss from 625 K (coalescence); β→cubic at 600 °C (other source) | DSC and XRD | Hölsä group; Sci Rep | SNIPPET | med |
| Luminance of UC micropowder | **8×10⁶ cd/m²** | SrF2 and β-NaYF4:Yb,Er; 100 W/cm² each at 980 + 1550 nm | Opt Mater 2021 | SNIPPET | high |
| Blackbody luminous efficacy (per W radiated) | 1500 K 0.08; 2000 K 1.6; 2500 K 8.0; **3000 K 20.7** lm/W | Planck × V(λ) | this work (peak 96 lm/W at 6640 K per Murphy) | ESTIMATE | high |
| Incandescent mote in air: power and efficacy | 20 µm, ε = 0.9: 2500 K needs 28 mW (9 % radiated) → **0.7 lm/W_abs**; 3000 K needs 41 mW (13 %) → **2.7 lm/W_abs** | conduction dominates at 1 atm | this work | ESTIMATE | med |
| Carbon mote lifetime in air | **~1 ms (5 µm), 10–30 ms (20 µm), 60–170 ms (50 µm)** | diffusion-limited d² law, T ≳ 1800 K | this work | ESTIMATE | med |
| Tungsten mote lifetime in air | ~2 ms (5 µm) to ~25–40 ms (20 µm) | diffusion-limited W→WO3; WO3 volatile above 1000 °C | this work, plus snippet on WO3 | ESTIMATE | low-med |
| Laser-induced white emission (graphene foam) | 6.98 lm/W, **in vacuum only** | CW 975 nm | Strek group, Sci Rep 2017 | SNIPPET | high |
| Laser-induced white emission (Yb2O3) vs pressure | efficient at 10⁻⁵–0.1 mbar; quenched at higher pressure | 975 nm | Mater Res Bull 2022 | SNIPPET | high |
| Gas-mantle (Welsbach) efficacy | ~2 lm/W (versus 0.2 lm/W for tungsten at the same temperature) | ThO2 + 1–2 % CeO2 | source page not pinned | SNIPPET | low |
| PV + LED micro-upconverter | **QY ~1.5 %** (810 nm → 630 or 590 nm), linear, 1–100 mW/cm², ~9 µm stack | GaAs double-junction PD + AlGaInP LED | Ding et al., PNAS 2018 | SNIPPET | high |
| Optically powered micro-chip size | 8×75×175 µm, 100 ng | Si PV + AlGaAs LED (OWiC) | Cortese et al., PNAS 2020 | SNIPPET | high |
| Cyan phosphor (needs a violet or blue pump) | BaSi2O2N2:Eu²⁺, 495–500 nm, IQE 90 % | 455 nm excitation | EPJ Plus 2024 | SNIPPET | high |
| CsPbBr3 two-photon cross-section | 10⁴–10⁵ GM per NC | fs pulses | JPCL 2017; PMC7352535 | SNIPPET | high |
| Two-photon PL under CW light | 20 µm NC-filled mote at 1 MW/cm² absorbs **~8 µW of 3.1 W incident** | σ2 = 10⁵ GM | this work | ESTIMATE | med |

## 1. Upconversion (UC) phosphors: the main route

### 1.1 Er/Yb (green 520/540 nm, red 655 nm)
- **Micro-crystals are what matter.** 5–50 µm motes would be single microcrystals (or sintered clusters), not nanoparticles. The measured micro-crystal ceiling is about **10–10.5 % UCQY** [SNIPPET: Kaiser 2017; Sci Rep 2023]. Most particles above ~45 nm behave like bulk [SNIPPET: Homann 2018], so a 5 µm mote has no size penalty.
- **Saturation.** Micro-particles already give 10.2 % at 20 W/cm² [SNIPPET], close to the 10.5 % maximum. Fitting the `s/(1+s)` form in `physics.py` to those points puts I_sat for bulk micro-crystals at roughly **1–10 W/cm²** [ESTIMATE]. The model currently assumes 30 W/cm², which is conservative for bulk and about right for 15–25 nm nanoparticles, whose efficiency is still climbing at 100 W/cm² [SNIPPET: Homann].
- **Heavy Yb doping is the main design lever.** Core/shell nanocrystals lose only 9 % → 7 % UCQY going from 20 % to 98 % Yb [SNIPPET: Nano Res 2022], while absorption rises about 5×. For motes, where absorption is the bottleneck, NaYbF4:Er-type crystals would give about 4× more light per mote at the same intensity. Whether heavily doped *bulk* crystals keep that UCQY is unknown (see Gaps).
- **Colour shifts with power.** With 980 nm pumping alone, the green-to-red ratio and the perceived colour change with luminance. Adding 1550 nm light holds the colour at CIE (0.31, 0.66) and reaches 8×10⁶ cd/m² at 100 W/cm² per wavelength [SNIPPET: Opt Mater 2021]. That result was aimed at persistence-of-vision displays and is directly relevant.
- **Ho/Yb.** Green at 540 nm (⁵S₂→⁵I₈) through a two-photon process [SNIPPET]. No absolute UCQY was found (see Gaps). Ho is generally reported as less efficient than Er [MEMORY, low].

### 1.2 Tm/Yb (blue 450 and 475 nm, NIR 800 nm)
- Blue 475 nm (¹G₄) needs three photons and 450 nm (¹D₂) needs four. In LiYF4:Yb,Tm nanoparticles at 5 W/cm², the total UCQY is ~2 %, but almost all of it is 794 nm light. **Blue is only ~6×10⁻⁵** [SNIPPET: Meijer 2018].
- Bulk blue reaches "1–2 % efficiency" at high intensity [SNIPPET: Page 1998]; that paper's definition of efficiency was not verified.
- Planning range for bulk blue UCQY at ≥1 kW/cm²: **0.1–1 %**, giving **0.16–1.6 lm/W_abs** [ESTIMATE]. Luminous efficacy at 475 nm is only 79 lm/W of light. **Blue is the weakest primary by 50–500×.**
- The `Tm_blue` preset (QY_max 0.02, half of the photons at 475 nm) implies 1 % blue. Treat that as the optimistic end.

### 1.3 Er-sensitised UC pumped at ~1.5 µm (eye-safe band, relevant to P19)
- Er-only β-NaYF4 reaches 12 % internal UCQY at 0.4 W/cm² [SNIPPET: Fischer] and 16.2 % under broadband excitation at 227 W/cm² [SNIPPET: MacDougall]. However, **most of that output is 980 nm and 810 nm NIR** [SNIPPET]. Red needs three photons and green needs four.
- Reported *visible* yields: 3.71 % (red-rich NaErF4:Tm@NaGdF4) and 1.2 % (LiYF4:Er at 1490 nm) [SNIPPET]. Output shifts from red to green as 1530 nm intensity rises from 10 to 10³ W/cm² [SNIPPET; paper not pinned].
- Planning range: visible UCQY **1–4 %**, which is **~3–10 lm/W_abs** [ESTIMATE]. That is about 10× worse than 980 nm Er/Yb, in exchange for the eye-safe pump.
- The `Er_1532` preset (QY 0.05, 70 % of photons visible) implies 3.5 % visible, which is optimistic but inside the reported range.
- Er absorption at 1532 nm is similar to or weaker than Yb at 976 nm (~0.5×10⁻²⁰ cm² [MEMORY, low]). Only fully Er-doped (NaErF4) motes absorb usefully.

### 1.4 Other hosts and sensitisers
- **LiYF4.** Nanocrystal UCQY is lower than NaYF4 (1.25 % at 180 W/cm² [SNIPPET]). Its advantage is purer blue from Tm, not efficiency.
- **Dye sensitisation.** The antenna dye's cross-section per nanoparticle (1.47×10⁻¹⁴ cm²) is vastly larger than a Yb ion's (~10⁻²⁰ cm²); reported figures are UCQY 4.8 % and energy efficiency 9.3 % at ~800 nm [SNIPPET: Chen 2015]. Two concerns remain: NIR cyanine dyes photobleach in air under high intensity [MEMORY], and hot motes will make that worse.
- **Thermally enhanced UC** (Sc2(MoO4)3:Yb/Er, negative thermal expansion). Green emission rises 45× between 298 and 773 K [SNIPPET]. This is the only class that *gains* when a mote runs hot, and it is worth testing (see Gaps).

### 1.5 Absorption, heating and damage (the binding constraints)
- α = N_Yb·σ. β-NaYF4 has N_RE = 1.38×10²² cm⁻³, so α ≈ 25–33 cm⁻¹ at 20 % Yb and 120–160 cm⁻¹ at 98 % Yb [ESTIMATE].

| d (µm) | Absorbed, 20 % Yb | Absorbed, 98 % Yb | Heat for ΔT = 200 K | Intensity at that limit (20 % / 98 % Yb) |
|---|---|---|---|---|
| 5 | 1.2–1.6 % | 5.9–7.8 % | 0.21 mW | 90 / 19 kW/cm² |
| 10 | 2.5–3.3 % | 11–15 % | 0.41 mW | 23 / 4.9 kW/cm² |
| 20 | 4.8–6.4 % | 22–28 % | 0.82 mW | 5.7 / 1.3 kW/cm² |
| 50 | 12–15 % | 46–56 % | 2.05 mW | 0.95 / 0.25 kW/cm² |

*Heat-limit columns assume σ = 1.0×10⁻²⁰ cm² and that 85 % of absorbed power becomes heat. Continuum conduction; radiation is negligible at 500 K. [ESTIMATE]*

- **What this means.** Brightness per mote is *not* the limit: a 20 µm Er mote at the thermal limit emits 0.06–0.11 lm, the luminous intensity of an indicator LED. The limits are (a) how much of the beam each mote absorbs, i.e. lm per W of IR in the room (P18), and (b) the fact that the absorbed heat both drives the photophoretic trap and quenches the emission. The trap and the emitter share one heat budget.
- **Thermal ceilings.**
  - Bare nanoparticles emit up to about 600 K [SNIPPET].
  - Silica-coated nanoparticles survive repeated 300↔900 K cycling [SNIPPET]. This suggests that an oxide-shelled microcrystal could run at 500–700 K, though with reduced green emission (magnitude unknown).
  - The DSC data put phase changes at 400–450 °C and "melting ~670 °C", with luminescence loss starting at 625 K through coalescence [SNIPPET]. Hard ceiling: **mote below ~600–650 K, i.e. ΔT ≤ ~300 K** [ESTIMATE].
  - The model's T_q = 520 K and dT_q = 60 K are plausible but not calibrated.
- **Damage threshold.** No measured optical damage intensity was found. The practical limit is thermal: **~1–20 kW/cm² in air**, depending on size and Yb content (table above) [ESTIMATE]. In vacuum, levitated UC particles heat up steadily and are lost from the trap [SNIPPET]. The 2025 study of levitated single UC particles covered 0.1–10³ W/cm² [SNIPPET: ACS Photonics 2025].

## 2. Laser-heated incandescent motes ("embers")
- **Physics.** At 1 atm, conduction to air dominates. The fraction radiated is only 3–13 % for a 20 µm black sphere between 1500 and 3000 K, and 1.5–3.5 % for 5 µm [ESTIMATE; continuum Nu = 2, which overestimates the loss by ~10–30 % for d ≲ 5 µm because Kn ~ 0.1–0.2 when hot].

| T (K) | Blackbody lm/W radiated | 20 µm, ε = 0.9: P_abs | lm/W_abs | 50 µm, ε = 0.9: lm/W_abs |
|---|---|---|---|---|
| 2000 | 1.6 | 18 mW | 0.09 | 0.22 |
| 2500 | 8.0 | 28 mW | 0.72 | 1.6 |
| 3000 | 20.7 | 41 mW | 2.7 | 5.6 |

*[ESTIMATE]. Air conductivity above ~2500 K is underestimated because O2 dissociation raises the effective conductivity [MEMORY], so real efficacy is lower still.*

- **Lifetime in air.** Carbon, soot and tungsten burn. Under the diffusion-limited d² law (oxidation is diffusion-controlled above ~1800 K [SNIPPET, Sandia char]), a 20 µm carbon mote lasts **~10–30 ms** and a 5 µm mote **~1 ms** [ESTIMATE]. Tungsten forms WO3, which is volatile above 1000–1200 °C [SNIPPET], and lasts a similar number of milliseconds [ESTIMATE]. These are fuses, not pixels.
- **Refractory oxides.** They are stable in air. Melting points [MEMORY, high]: Al2O3 2345 K, Y2O3 2698 K, ZrO2 ~2988 K, HfO2 ~3031 K, ThO2 ~3663 K. Langmuir evaporation runs 1–4 orders of magnitude below the equilibrium limit [SNIPPET], so evaporation at 2500 K is slow. **The catch: pure oxides are nearly transparent at 0.98–1.55 µm**, so the trap beam cannot heat them. They would need an absorbing dopant (Yb2O3 at 976 nm; Ce or other transition metals) or a ~10 µm CO2 beam [MEMORY].
- **Welsbach/candoluminescent emitters.** ThO2 with 1–2 % CeO2 is a selective emitter: bright in the visible, dim in the NIR, about 2 lm/W versus 0.2 for tungsten at the same temperature [SNIPPET, source not pinned]. Thoria is radioactive and not acceptable in a room display.
- **Laser-induced white emission (LIWE).** Graphene foam and Yb2O3 give white light under CW 975 nm (graphene bulb 6.98 lm/W) **only in vacuum**; the emission collapses above ~0.1 mbar [SNIPPET]. This is independent confirmation that conduction to air defeats hot emitters.
- **Trap compatibility.** Photophoretic force scales with ΔT. A mote at 2000 K or more also drives a strong convective plume and chaotic photophoretic forces, which conflicts with stable trapping [ESTIMATE, qualitative].
- **Verdict.** 0.1–3 lm/W_abs, millisecond lifetimes for carbon and metals, and 20–40 mW per mote. Embers are 20–100× worse than Er upconversion and chemically unstable. Reject, except perhaps doped-oxide embers as an orange "warm white" curiosity.

## 3. Other emitters the trap beam could power

### 3.1 One-photon photoluminescence (QDs, perovskites, Eu²⁺/Ce³⁺ phosphors)
- These need a UV, violet or blue pump. Efficacy is high: with QY 0.9 and a 405 nm pump, green 530 nm gives **~405 lm/W_abs**, cyan 495 nm (BaSi2O2N2:Eu, IQE 90 % [SNIPPET]) ~134, and orange 600 nm ~262 [ESTIMATE].
- The pump itself is barely visible: 405 nm has V = 0.0008, i.e. 0.55 lm/W. Smalley's photophoretic display used exactly this "near-invisible" 405 nm trap [SNIPPET: Nature 2018].
- The costs are (i) the beam still shows as violet scatter on dust, (ii) retinal blue-light hazard limits, and (iii) the brief's "no visible beams" rule. It is worth putting to the lab as a deliberate exception.
- **Photostability.** Inorganic Eu²⁺ and Ce³⁺ phosphors are robust (laser-lighting grade) [MEMORY]. Giant CdSe/CdS QDs show photobleaching and partial recovery at 15 W/mm² [SNIPPET]. Perovskite NCs degrade under heat, light and moisture [MEMORY]. Hot motes speed up all of these.

### 3.2 Two-photon excitation (NIR pump, visible out)
- CsPbBr3 NCs have σ2 of 10⁴–10⁵ GM [SNIPPET]. Under CW light, a 20 µm mote packed with NCs at 1 MW/cm² (800 nm) absorbs ~8 µW of the 3.1 W incident on it, a fraction of ~3×10⁻⁶ [ESTIMATE].
- **Not viable under CW.** It would need fs or ps pulses at average powers well above eye-safety limits.
- A related route, triplet-fusion (TTA) UC driving CsPbI3 QDs in a volumetric demo, exists [SNIPPET], but TTA needs oxygen-free solids.

### 3.3 Optoelectronic micro-upconverters (photovoltaic + LED, "light-powered micro-LEDs")
- Ding et al. (PNAS 2018): a GaAs double-junction photodiode plus an AlGaInP LED in a ~9 µm-thick stack converts ~810 nm to 630 nm (red) or 590 nm (yellow) with **QY ~1.5 %**, *linearly*, at 1–100 mW/cm². Tunable lifetime is 20–200 ns [SNIPPET]. An IR-to-blue (470 nm) version uses an InGaN LED plus two double-junction GaAs photodiodes [SNIPPET]. OWiC chips are 8×75×175 µm and 100 ng [SNIPPET].
- Advantages over UC:
  - no intensity threshold (linear), so it works at mW/cm²;
  - any colour, including true amber, cyan and 600 nm orange (InGaN/AlGaInP);
  - near-100 % absorption of the trap light.
- Ceiling: laser power converter efficiency ~60–69 % [MEMORY: GaAs record ~69 % near 858 nm] × micro-LED wall-plug efficiency ~10–50 % [MEMORY; drops below ~20 µm through sidewall recombination, especially in AlGaInP] gives roughly **~10–30 % power efficiency, i.e. ~20–60 lm/W_abs for red and up to ~50–150 for amber** [ESTIMATE].
- Costs:
  - cleanroom-made chips, not powders;
  - flat die (roughly 50×50×9 µm), which emit anisotropically and need to be rotation-stable in a photophoretic trap;
  - an ~810 nm pump, which is faintly visible at high power;
  - blue needs about 3 V, so ≥ 3 GaAs junctions in series.
- This is the only route that could give *efficient, saturated* cyan and orange from an IR beam.

## 4. Colour: cyan (480–495 nm) and orange (~600 nm)
The mixing calculations below use CIE 1931 colour-matching functions (Wyman–Sloan–Shirley analytic fit) and a D65 white point [ESTIMATE].

| Target | Best IR-driven option | Needed mix | Luminous efficacy of the light | Luminous efficacy per W absorbed |
|---|---|---|---|---|
| Cyan 480–490 nm (dominant) | Tm 475 + Er 540 in one mote or neighbouring motes | 70–90 % of optical power at 475 nm, 10–30 % at 540 nm (dominant 480–488 nm) | 136–250 lm/W | limited by blue: ≈ QY_blue × 736, i.e. **~0.7–7 lm/W_abs** |
| Cyan (spectral) | Tb³⁺ ⁵D₄→⁷F₆ at 490 nm; Dy³⁺ 480 nm | the 545 nm (Tb) or 575 nm (Dy) line dominates | – | via Yb-pair or Gd-migration UC; no QY found |
| Cyan (1-photon) | BaSi2O2N2:Eu²⁺ (495–500 nm, IQE 90 %) | needs a 405–455 nm pump | 181 lm/W | ~134 lm/W_abs |
| Orange ~590–600 nm (dominant) | Er red-rich (Mn-, Ce- or Tm-codoped NaYF4; NaErF4 R/G up to 18.7 [SNIPPET]) | **~92–94 % of power at 655 nm** (≈95 % of photons) | **90–105 lm/W** | ~5–10 lm/W_abs |
| Orange (spectral) | Sm³⁺ 599 nm, Eu³⁺ 592/615 nm via Gd-sublattice migration (5-photon Tm→Gd) [SNIPPET] | – | 300–520 lm/W | UCQY likely ≲ 10⁻³ [MEMORY], giving ≲ 0.5 lm/W_abs |
| Orange (true 600 nm, linear) | PV + AlGaInP/InGaN amber micro-LED | – | 431–517 lm/W | ~50–150 lm/W_abs (ESTIMATE, section 3.3) |
| Orange (thermal) | 2000–2500 K ember (CCT ~2000 K looks orange) | – | 1.6–8 lm/W radiated | 0.1–0.7 lm/W_abs (section 2) |

**Summary.** Er/Yb green is the only efficient IR-UC colour (~60–120 lm/W_abs). Red (655 nm) carries very little luminance (57 lm/W of light) and blue even less. Colour-mixed orange works with red-rich Er at ~5–10 lm/W_abs. Cyan is blue-starved. True spectral orange or cyan needs either PV-LED chips or a violet pump.

## 5. Recommended calibration for `mote/physics.py` EMITTERS
- **`Er_green_red`:** QY_max 0.10 (micro-crystal) [SNIPPET]; I_sat 1–10 W/cm² (the model has 30; keep 30 as a nanoparticle case). Lines (540 0.6 / 655 0.4) are reasonable; the high-power split is not measured here. T_q ~550–650 K is plausible for an oxide-shelled crystal (currently 520 K). Add an absorption fraction A(d, Yb%) from the table in section 1.5.
- **`Tm_blue`:** keep QY_max 0.02 as the total UCQY, but set the blue share to 5–50 %, so blue UCQY is 0.1–1 %. The current 50 % share is the optimistic bound.
- **`Er_1532`:** visible UCQY 1–4 %. Add a ~980 nm share of 70–90 % at low intensity (Fischer: output is mostly NIR). The current 30 % is optimistic.
- **Incandescent:** the model's formula is sound. Add a burnout clock (carbon ~1–30 ms for 5–20 µm) and flag ΔT ≥ 1500 K as incompatible with trapping.

## Gaps
1. **Power-resolved UCQY curve for bulk micro-crystals.** The 10.5 % point's power density and the green/red/NIR split at ≥1 kW/cm² are not in the snippets. The Kaiser 2017 full text is needed.
2. **Thermal quenching of bulk β-NaYF4:Yb,Er between 300 and 700 K.** No percentage-remaining figure was found; only the 900 K survival of silica-coated nanoparticles and a 625 K coalescence onset. A heated-stage measurement is needed.
3. **Heavily doped *bulk* UC.** Does NaYbF4:Er micro-crystal UCQY stay near 7–9 % like the core/shell nanocrystals?
4. **Bulk Tm blue UCQY at kW/cm²,** and the definition used in Page 1998. Absolute Ho/Yb UCQY.
5. **Visible-only UCQY under 1532 nm for micro-crystals.** The 3.71 % figure is for nanoparticles, with unknown intensity.
6. **Optical damage and melting threshold** of single UC micro-crystals in air. The DSC "melting ~670 °C" conflicts with other phase data; this needs checking.
7. **Photobleaching of dye-sensitised UC** at kW/cm² in air.
8. **Micro-LED numbers left unverified** after the search budget ran out: wall-plug efficiency of a 20–50 µm AlGaInP or InGaN micro-LED, the GaAs power-converter record, and any 2023–26 "light-powered micro-LED" papers.
9. **Thermally enhanced UC hosts** (Sc2(MoO4)3, Yb2W3O12): absolute UCQY at 500–700 K has not been measured and could favour hot motes.

## Sources (via search snippets)
- Kaiser 2017: https://pubs.rsc.org/en/content/articlelanding/2017/nr/c7nr02449e
- Sci Rep 2023: https://www.nature.com/articles/s41598-023-35164-x
- Homann 2018: https://pubmed.ncbi.nlm.nih.gov/29732658
- Nano Res 2022 (Yb/Er concentration): https://link.springer.com/article/10.1007/s12274-022-4570-5
- Boyer & van Veggel 2010: https://pubs.rsc.org/en/content/articlelanding/2010/nr/c0nr00253d
- Page 1998: https://opg.optica.org/josab/abstract.cfm?uri=josab-15-3-996
- Meijer 2018 (LiYF4:Yb,Tm): https://pubs.rsc.org/en/content/articlelanding/2018/cp/c8cp03935f
- LiYF4:Yb,Er core/shell: https://link.springer.com/article/10.1007/s12274-020-3116-y
- Fischer 2014: https://www.sciencedirect.com/science/article/abs/pii/S002223131400194X
- MacDougall 2012: https://opg.optica.org/oe/abstract.cfm?uri=oe-20-s6-a879
- 8.4 % in PFCB matrix: https://pubs.aip.org/aip/jap/article-abstract/114/1/013505/167688
- 3.71 % Er-sensitised: https://www.sciencedirect.com/science/article/abs/pii/S0022231319310658
- LiYF4:Er at 1490 nm: https://pmc.ncbi.nlm.nih.gov/articles/PMC3430509/
- 1530 nm colour tuning: https://pubs.aip.org/aip/adv/article/13/5/055203/2887791
- Dye cascade: https://pubs.acs.org/doi/abs/10.1021/acs.nanolett.5b02830
- Silica-coated thermometry to 900 K: https://doi.org/10.1021/acs.jpcc.6b10279
- DSC of NaYF4: https://www.researchgate.net/publication/277573490
- In-situ phase change: https://pubmed.ncbi.nlm.nih.gov/38619542/
- Sc2(MoO4)3 thermal enhancement: https://pmc.ncbi.nlm.nih.gov/articles/PMC9019035/
- Dual 980/1550 nm: https://www.sciencedirect.com/science/article/abs/pii/S0925346720309381
- Er:Y2O3 (975 nm; 39,000 cd/m² at 850 mW): https://opg.optica.org/ol/abstract.cfm?uri=ol-25-5-338
- Levitated UC single particles: https://pubs.acs.org/doi/10.1021/acsphotonics.4c02024
- Photophoretic display: https://www.nature.com/articles/nature25176
- Graphene LIWE: https://www.nature.com/articles/srep41281
- Yb2O3 LIWE: https://www.sciencedirect.com/science/article/pii/S0025540822002823
- Tungsten oxidation: https://www.sciencedirect.com/science/article/pii/S2352179125001309
- Char combustion: https://www.osti.gov/pages/servlets/purl/1326060
- Langmuir evaporation: https://arxiv.org/pdf/1902.05005
- Luminous-efficacy limit: https://tmurphy.physics.ucsd.edu/papers/lumens-per-watt.pdf
- Ding 2018: https://www.pnas.org/doi/10.1073/pnas.1802064115
- Low-power optoelectronic UC 2019: https://shengxingstars.github.io/www/publications.html
- Optoelectronic thermometer: https://www.nature.com/articles/s41377-022-00825-5
- Cortese 2020: https://www.pnas.org/doi/full/10.1073/pnas.1919677117
- CsPbBr3 two-photon: https://pubs.acs.org/doi/10.1021/acs.jpclett.7b00613
- Giant QD photostability: https://pmc.ncbi.nlm.nih.gov/articles/PMC9417657/
- BaSi2O2N2: https://link.springer.com/article/10.1140/epjp/s13360-024-04962-1
- Gd-migration UC: https://www.sciencedirect.com/science/article/pii/S2589965124000461
- Volumetric UC glasses: https://www.nature.com/articles/s41377-024-01672-2
- TTA/perovskite volumetric: https://pmc.ncbi.nlm.nih.gov/articles/PMC12156221/

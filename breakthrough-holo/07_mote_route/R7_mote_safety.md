# R7 - Safety of an open-air, many-trap IR "mote" display (980 / 1064 / 1550 nm CW, 1-100 mW per trap)

Compiled 2026-09-30. Scope: laser eye/skin limits and classes, regulatory routes for open-beam displays, airborne-particle
exposure, and thermal/fire hazards for hundreds to thousands of photophoretic traps holding 5-50 µm particles
(cellulose, carbon, NaYF4:Yb,Er) and moving them at 1-2 m/s.

**Confidence codes.** **A** = read this session in a primary text, a verbatim search snippet, or an open-source transcription
that cites table and page. **B** = secondary source or recalled, and cross-checked (e.g. MPE × aperture area = AEL).
**C** = conflicting or unverified; check the purchased standard. **INFERRED** = my own arithmetic or engineering reading.

**Access caveat.** The egress proxy blocked icnirp.org, iec.ch, fda.gov, arxiv.org, PMC, DTIC, Seibersdorf, Wikipedia and iteh.ai.
The web-search budget (200) ran out during this task. Evidence therefore comes from:
- search-engine snippets;
- the eCFR mirror on GitHub (`lucas-amberg/ecfr-analyzer`, 21 CFR 1040.10/.11, 2025-02-06 snapshot);
- the IEC 60825-1:2014 implementation `llano1025/calEng` (`LaserSafetyShared.tsx`: Tables 3/6/8/9/10), which has one known typo
  (C7 exponent 0.0018 instead of 0.018; irrelevant here);
- the ICNIRP-2013 skin transcription `CBORT-NCBIB/MPE-Calculator-Skin` (`icnirp_2013.json`);
- sibling notes `01_research/R3_safety_limits.md` and `07_mote_route/R5_optical_trap_displays.md`.

---

## 0. MASTER TABLE

Notation: E = irradiance, H = radiant exposure, t = exposure time [s]. C_A = C4 (IEC), C_C = C7, C_E = C6.
C_A(980) = 10^(0.002·280) = **3.63**; C_A(1064) = **5.0**; C_C(980, 1064) = **1.0**.
Eye limiting aperture 7 mm (area 3.85×10⁻⁵ m²); skin 3.5 mm (9.62×10⁻⁶ m²).

| # | Hazard | Limit | Conditions | Source | Conf. |
|---|---|---|---|---|---|
| E1 | Retina 980 nm, CW | H = 18 C_A t^0.75 J/m² → **92 W/m² (3.6 mW in 7 mm) @0.25 s; 37 W/m² (1.4 mW) @10 s**; E = 10 C_A C_C = **36 W/m² (1.40 mW)** for 10 s-3×10⁴ s | small source α ≤ 1.5 mrad (C_E = 1, T2 = 10 s); 5 µs ≤ t < T2 | ICNIRP 2013 / IEC 60825-1:2014 Annex A (via AEL/area) | B |
| E2 | Retina 1064 nm, CW | H = 90 C_C t^0.75 J/m² → **127 W/m² (4.9 mW) @0.25 s**; E = **50 W/m² = 5 mW/cm² (1.9 mW)** for 10 s-3×10⁴ s | as E1; 13 µs ≤ t < T2 | ICNIRP 2013 / IEC 2014; ANSI Z136.1 "5.0 C_C mW/cm²" | B |
| E3 | Cornea 1550 nm (1500-1800) | **10⁴ J/m² (1 J/cm²)** for 10⁻⁹-10 s; **1000 W/m² (0.1 W/cm²)** for 10 s-3×10⁴ s → 31 mW @0.25 s (1 mm ap.), 18 mW @1 s, **9.6 mW ≥10 s (3.5 mm)** | aperture 1 mm (t ≤ 0.35 s), 1.5·t^0.375 mm, 3.5 mm (t ≥ 10 s) | ICNIRP 2013 Tab. 5 (transcription); IEC Tab. 10 (calEng) | A |
| E4 | Extended-source terms | C_E = α/1.5 mrad (1.5 < α ≤ α_max); α_max = 100 mrad (t > 0.25 s); T2 = 10·10^((α-1.5)/98.5) s (10-100 s) | 400-1400 nm | IEC 2014 Tab. 9 (calEng) | B |
| E5 | A trap focus seen as a source | 20-100 µm focus at 100 mm → α = 0.2-1 mrad → **point source, C_E = 1, T2 = 10 s** | any viewing ≥ 100 mm | INFERRED | INFERRED |
| S1 | Skin 980 / 1064 nm | 1.1×10⁴ C_A t^0.25 J/m²: 11.3 / 15.6 W/cm² @0.25 s; **2000 C_A W/m² = 0.73 / 1.0 W/cm² (70 / 96 mW in 3.5 mm)** for t > 10 s | 3.5 mm aperture | ICNIRP 2013 Tab. 7 (transcription) | A |
| S2 | Skin 1550 nm | as cornea E3: 1 J/cm² (≤10 s); **0.1 W/cm² (9.6 mW in 3.5 mm)** for t > 10 s; 10 mW/cm² if > 1000 cm² exposed | 3.5 mm | ICNIRP 2013 Tab. 5/7 note c | A |
| S3 | Small-beam skin rule | "For beam diameters less than 1 mm, the actual radiant exposure, i.e., not averaged over the 3.5 mm aperture, should be compared" → **every 20-100 µm focus on skin exceeds the skin MPE even at 1 mW** (12.7-318 W/cm² vs ≤ 1 W/cm²) | ICNIRP only; ANSI Z136.1-2022 has no such rule; one snippet adds "and t < 0.35 s" | ICNIRP 2013 Tab. 7 note b (transcription + snippet) | C (scope conflict) |
| K1 | Class 1 AEL, CW (t > T2) | **980 nm 1.43 mW** (3.9×10⁻⁴ C4 W); **1064 nm 1.97 mW** (3.5×10⁻³·10^-0.25 C7 W); **1550 nm 10 mW** | Cond. 3: 7 mm (3.5 mm at 1550) aperture at 100 mm from reference point | IEC 60825-1:2014 Tab. 3 (calEng); = MPE × area | B |
| K2 | Class 3R AEL, CW | **980: 7.2 mW** (≈1.97×10⁻³ C4 W); **1064: 9.8 mW**; **1550: 50 mW** (5×10⁻² W) | = 5 × Class 1 | IEC 2014 Tab. 6 (calEng) | B |
| K3 | Class 3B AEL, CW | **0.5 W** (t ≥ 0.25 s), all three λ | above = Class 4 | IEC 2014 Tab. 8 (calEng) | B |
| K4 | Class 1M | Class 1 AEL met under Cond. 3 but exceeded under Cond. 1 (50 mm at 2000 mm for 400-1400; 7× Cond. 3 aperture at 2000 mm for 1400-4000). **Cond. 2 (eye loupe) deleted in 2014**, so 1M is now a collimated large-beam class, **not a route for diverging trap beams** | measurement conditions | IEC 2014 Tab. 10 (calEng); change note (snippet) | B |
| K5 | Time base | 100 s; **30 000 s where intentional long-term viewing is inherent** (a display). For IR retinal/corneal CW limits this has no effect beyond T2 = 10 s | classification | IEC 2014 §4.3e (calEng) | B |
| K6 | Scanned or moving beams | Each pass across the aperture is a pulse. Rule 1 (single pulse) and Rule 2 (average over T); C5/C_P only for α > 5 mrad and never > 1400 nm or on skin. **Classification must hold under a scan/stall single fault** | IEC 2014 §4.3; ICNIRP p. 287 | B |
| K7 | Per-trap Class 1 power (Gaussian, Cond. 3) | Max **total** power whose cones overlap at the worst 100 mm point: NA 0.1 → 6.6 / 9.1 / 168 mW; NA 0.3 → 53 / 73 / 1470 mW (980 / 1064 / 1550) | ideal Gaussian; real aberrated traps must be measured | INFERRED from K1 | INFERRED |
| R1 | US: display = "demonstration laser product" | "entertainment, advertising display, or artistic composition". Must not allow access above **Class I**, or IIa/II/IIIa where applicable. IIIa = "**visible** laser radiation", so an **IR display is Class I-only without a variance** | 21 CFR 1040.10(b)(13), (b)(8); 1040.11(c) | eCFR (GitHub mirror) | A |
| R2 | FDA light-show variance | >Class I not allowed < **3.0 m above** any audience standing surface or < **2.5 m** lateral/below; audience areas held to **Class I**; no scanning into the audience except diffuse reflections from atmosphere/screens; a **scanning safeguard** that senses scanner motion is required if scanning is relied on | variance (Form FDA 3147) | FDA variance documents (snippets, verbatim) | A |
| R3 | FDA Laser Notice 56 (2019) | Conformance with IEC 60825-1 Ed. 3 is accepted in lieu of most of 1040.10/.11. IEC 1M ≈ CDRH Class I "may need re-evaluation"; IEC 3R ≈ IIIa | USA | FDA LN56 / LN57 (snippets) | B |
| R4 | EU consumer: EN 50689:2021 | Consumer products: **Class 1, Class 2, or a restricted 3R** (justification, deliberate activation, emission indicator, not a pointer). **Child-appealing → Class 1 only** plus limits at contact and at the smallest beam diameter | EU (with EN 60825-1:2014/A11:2021) | UL, JJR, Seibersdorf (snippets) | B |
| R5 | IEC TR 60825-3:2022 (shows) | Covers **380-780 nm** show lasers. TR 60825-14: only Class 1, 2 or visible 3R in **unsupervised** areas. Audience scanning is judged against single-pulse, multi-pulse and average MPE | guidance | IEC webstore (snippet) | A/B |
| P1 | WHO 2021 AQG | **PM2.5: 5 µg/m³ annual, 15 µg/m³ 24 h; PM10: 15 µg/m³ annual, 45 µg/m³ 24 h** | ambient, public | WHO 2021 (snippet; also R3) | A |
| P2 | Room-air background | ISO 14644-1 Class 9 ("≈ ordinary room"): ≤ 35.2 M/m³ ≥0.5 µm, **≤ 293 000/m³ ≥5 µm**; Class 8: 29 300/m³ ≥5 µm. Indoor PM10 in homes ≈ 30-35 µg/m³ (24 h means) | reference, not a health limit | ISO 14644-1 (snippet); AAQR/T&F studies (snippet) | A / B |
| P3 | Settling (Stokes + Schiller-Naumann) | 20 µm: **1.8 cm/s** cellulose (1.5 g/cm³), 2.1 cm/s carbon (1.8), **5.0 cm/s** NaYF4 (4.21); 5 µm: 0.11-0.32 cm/s; 50 µm: 10-28 cm/s | still air, 20 °C | INFERRED (unit-density 10 µm = 0.30 cm/s matches Hinds) | INFERRED/B |
| P4 | Occupational limits | Cellulose ACGIH 10 mg/m³ (OSHA 15 total); carbon black OSHA/NIOSH 3.5, **ACGIH 3 mg/m³ inhalable**, IARC 2B; yttrium (as Y) 1 mg/m³; fluorides (as F) 2.5 mg/m³ | 8-h TWA, workers | NIOSH/OSHA/ACGIH (snippets) | A |
| P5 | Mass budget, 1000 × 20 µm particles/h | **6.3 µg/h** cellulose, 7.5 carbon, **17.6 µg/h NaYF4** (55-154 mg/yr). Well-mixed steady state in 30 m³ at 0.5 ACH plus settling: **≈ 0.008 µg/m³, about 1 particle/m³** | 2.5 m fall height | INFERRED | INFERRED |
| T1 | Focal irradiance | 1 mW @100 µm = **12.7 W/cm²** … 100 mW @20 µm = **32 kW/cm²** (mean over the spot) | CW | INFERRED | INFERRED |
| T2 | Fire rule of thumb | "irradiance > **10 W/cm²** can ignite combustible material"; Class 4 (> 0.5 W) = fire hazard; high-3B can ignite | ANSI Z136.1-based EHS guidance | university EHS (snippet) | B |
| T3 | Skin burn threshold (for scale) | 1070 nm CW porcine MVL ED50: **432 J/cm² (≈ 43 W/cm², ≈ 6 W) at 0.6 cm, 10 s** vs MPE ≈ 9.8 J/cm² (×44). 1540 nm, 600 µs: 20 / 8.1 / 7.4 J/cm² at 0.7 / 1.0 / 5 mm (threshold rises for small spots) | in-vivo Yucatan pig | Vincelette 2014 JBO 19:035007; Zuclich et al. (snippets) | A |
| T4 | Trap on skin, estimate | ΔT ≈ 0.1 K/mW (980/1064), ≈ 0.4 K/mW (1550) → 100 mW: **+12 K / +40 K** (pain or burn at 1550 within seconds); ≤ 10 mW: ≤ 1-4 K | steady state, diffusion-limited | INFERRED | INFERRED |
| T5 | Trap on black paper/fabric, estimate | ΔT = P/(π k a): 1 mW → 57-290 K; **10 mW → 570-2900 K** (char/ignition locally) | absorbing surface at focus | INFERRED | INFERRED |

---

## 1. Laser MPE detail (ICNIRP 2013 = IEC 60825-1:2014 Annex A; ANSI Z136.1 is numerically the same for these cases)

**Retinal thermal, 400-1400 nm** (7 mm aperture; evaluation at ≥100 mm, see §2):
- 700-1050 nm: H = 2×10⁻³ C_A J/m² (10⁻¹¹ s-5 µs); **H = 18 C_A C_E t^0.75 J/m² (5 µs ≤ t < T2)**; **E = 18 C_A C_E T2^-0.25 W/m²** for t ≥ T2.
  For a small source, T2 = 10 s gives **E = 10 C_A W/m²** (ANSI: 1.0 C_A mW/cm²).
- 1050-1400 nm: H = 2×10⁻² C_C J/m² (to 13 µs); **H = 90 C_C C_E t^0.75 J/m²**; **E = 50 C_C W/m²** (ANSI 5.0 C_C mW/cm²) for t ≥ 10 s.
  (Class 1 values 7×10⁻⁴ C4 t^0.75 J and 3.5×10⁻³ C7 t^0.75 J ÷ 3.85×10⁻⁵ m² = 18.2 and 91 → checks.)
- C_C = 1 for 700-1150 nm; 10^(0.018(λ-1150)) for 1150-1200; 8 + 10^(0.04(λ-1250)) for 1200-1400 (IEC 2014 form) (B).
- There is no photochemical term above 600 nm. The 30 000 s time base changes nothing for these small IR sources.

**Worked values** (power into the 7 mm pupil at the MPE; INFERRED arithmetic from the formulas):

| t | 980 nm | 1064 nm | 1550 nm (cornea, aperture per E3) |
|---|---|---|---|
| 0.25 s | 92 W/m², **3.56 mW** | 127 W/m², **4.90 mW** | 4×10⁴ W/m², **31 mW** (1 mm) |
| 1 s | 65 W/m², 2.52 mW | 90 W/m², 3.46 mW | 10⁴ W/m², 17.7 mW (1.5 mm) |
| 10 s-3×10⁴ s | 36 W/m², **1.40 mW** | 50 W/m², **1.92 mW** | 1000 W/m², **9.6 mW** (3.5 mm) |

**Skin** (3.5 mm aperture): 400-1400 nm: 200 C_A J/m² (1-100 ns); **1.1×10⁴ C_A t^0.25 J/m²** (10⁻⁷-10 s); **2×10³ C_A W/m²** (10 s-3×10⁴ s).
For >1400 nm skin = cornea (E3). Large-area derating applies >1400 nm for t > 10 s: 10 000/A_s mW/cm² for A_s = 100-1000 cm², then 10 mW/cm² (A).
Rule 3 (C_P) never applies to skin (A).

**Limiting apertures** (A/B): eye 7 mm (400-1400 nm); 1 mm / 1.5 t^0.375 mm / 3.5 mm (>1400 nm, t ≤ 0.35 / 0.35-10 / ≥ 10 s); skin 3.5 mm.
ANSI uses 0.3 s instead of 0.35 s (C).

## 2. Classification of a many-trap open-air display

**AELs** (IEC 60825-1:2014 via calEng; t ≥ 10 s):

| Class | 980 nm | 1064 nm | 1550 nm |
|---|---|---|---|
| Class 1 | 1.43 mW | 1.97 mW | 10 mW |
| Class 3R | 7.2 mW | 9.8 mW | 50 mW |
| Class 3B | 500 mW | 500 mW | 500 mW |

Short-time Class 1 (1550 nm): 8 mJ for 10⁻⁹-0.35 s (≈ 32 mW for 0.25 s), then 1.8×10⁻² t^0.75 J to 10 s (B).
Class 2/2M do not exist in the IR, so there is no blink-reflex allowance: IR is invisible and triggers no aversion response.

**How a diverging beam after a focus is assessed** (B, with INFERRED application):
- IEC Condition 3 places the aperture (7 mm; 3.5 mm at 1550 nm for t ≥ 10 s) **100 mm from the reference point** (Table 11; the apparent source).
  For an accessible focus the focus is the apparent source. If the closest point of human access is farther away, you measure there (C: check Table 11 wording).
- Condition 1 (50 mm aperture, or 7 × Cond. 3 aperture above 1400 nm, at 2000 mm) catches only ~3 % of an NA-0.1 cone. Condition 3 therefore governs, and **1M gives no relief**.
- The US rule 1040.10(e)(3)(i) is similar: 7 mm stop, 10⁻³ sr acceptance, and for scanned light the acceptance direction follows the beam at up to 5 rad/s (A).
- Gaussian fraction through a 7 mm stop at 100 mm: NA 0.05 → 62 %, 0.1 → 22 %, 0.2 → 5.9 %, 0.3 → 2.7 %. Through 3.5 mm (1550 nm): 22 %, 5.9 %, 1.5 %, 0.68 % (INFERRED).
- **Overlap is the real limit (INFERRED).** All trap cones that overlap at the worst 100 mm point add. Example: 1000 traps in a 10 cm field with NA 0.3 cones (w ≈ 30 mm) puts about 30 % of them in one aperture.
  Class 1 then allows ≈ 73 mW / 300 ≈ **0.25 mW per trap at 1064 nm** and ≈ 1.47 W / 300 ≈ **5 mW per trap at 1550 nm**.
  BYU photophoretic traps needed **≥ 18-24 mW** each at 405 nm (R5). Only 1550 nm, high NA, and beam cones pointed away from any head position come close.
- **Single faults (B/INFERRED).** A holographic/SLM or galvo multiplexer fault can dump the summed power (e.g. 1000 × 10 mW = 10 W, Class 4) into one spot or the zero order.
  Class 1 must hold under reasonably foreseeable single faults. This needs an independent total-power monitor and shutter, qualified to functional-safety practice.
- The eye can also be put *inside* the converging or diverging cone, within z ≈ 3.5 mm / NA of the focus (35 mm at NA 0.1), where the whole trap power enters the pupil.
  The standard accepts this for retinal hazard because such close points are defocused. At 1550 nm the corneal and skin hazard at the focus is not covered by the 100 mm rule (C).

**Moving and scanned traps (B/INFERRED).**
- At 1-2 m/s a cone of radius w sweeps a fixed pupil in ≈ 2w/v (NA 0.1 at 100 mm: 20 ms per pass).
- Rule 1 compares each pass with the single-pulse AEL for that duration. Rule 2 compares the time-average over T (up to 30 000 s) with the CW AEL.
- C5 = 1 because α < 5 mrad. Motion therefore buys only a **duty-cycle average**, and it cannot be credited unless a stall is detected and shut off.
  FDA 1040.10(f)(9) scanning safeguard (A); IEC single-fault clause (B).

## 3. Regulatory routes and precedents

- **USA.**
  - A mote display is a *demonstration laser product* (A). Class IIa/II/IIIa are defined for **visible** radiation only (1040.10(b)(8): IIIa = "visible laser radiation…", A).
    So an IR display may not give human access above **Class I** unless FDA grants a variance.
  - Light-show variances keep >Class I beams ≥ 3.0 m above and ≥ 2.5 m laterally from audience areas. Audience areas stay at Class I, and audience scanning is refused except for diffuse reflections (A, variance text).
    A touchable open trap volume cannot meet this, so in practice **Class 1 (IEC, accepted via Laser Notice 56) is the only consumer route** (INFERRED from A/B).
  - Note (B): CDRH does not "approve" non-medical laser products. Makers file product reports, and variances are granted per product/venue.
- **EU.** EN 60825-1:2014+A11:2021 plus **EN 50689:2021** allow consumer Class 1, 2 and a restricted 3R. IR has no Class 2, and an IR 3R needs a written justification of why Class 1 is inadequate (B).
  A "hologram" toy is likely *child-appealing* → **Class 1 only** plus extra limits at contact and at the smallest beam diameter (B; values not obtained).
  IEC TR 60825-3:2022 covers visible (380-780 nm) shows. TR 60825-14 allows only Class 1, 2 or visible 3R in unsupervised areas (A/B).
- **Can many low-power beams be Class 1/1M/3R?**
  - **Class 1: yes, if the summed accessible emission at every 100 mm point is below the AEL** (§2), including faults.
    This needs sub-mW traps at 980/1064 nm or a few mW at 1550 nm, or engineering (beam dumps, and cone directions that never reach an accessible 100 mm point) (INFERRED).
  - 1M: not applicable (K4).
  - 3R: fails the US demonstration-product rule for IR; EU consumer only with justification (A/B).
- **Precedents for open IR consumer beams** (all Class 1):
  - iPhone Face ID / LiDAR: 940 nm VCSEL, "Class 1 per IEC 60825-1 Ed. 3 … complies with 21 CFR 1040.10/1040.11 … Laser Notice 56" (A, Apple support snippet).
  - Bosch **BMV080** open-beam particulate sensor: Class 1, EN 50689 consumer, LN56; Seibersdorf report LE-L176/23 (A, GitHub datasheet copy). This is the closest analogue: a laser measuring particles in open room air.
  - Robot-vacuum LDS and ams **TMF8829** ToF: Class 1 incl. single faults, EN 50689 (A).
  - **Luminar 1550 nm lidar**: Class 1 while firing pulses "~40× more powerful" than 905 nm systems (B). Laser Focus World has raised safety questions about high-average-power 1550 nm lidar, including camera damage (B).
  - **Free-space optical comms (Li-Fi-type laser links)** use IEC 60825-12 "hazard/access levels" (Level 1 = Class 1 AEL at any accessible location) (A, snippet). This does not cover power beaming.
  - **Wi-Charge** (IR laser power, "up to 3 W over 10 m" claimed): says it complies with IEC 60825-1 as **Class 1**, earned **UL** safety approval (Apr 2019), and was reported as "approved by FDA" (B).
    Mechanism: a **distributed laser resonator** between retro-reflectors in transmitter and receiver. An opaque object in the beam kills lasing intrinsically, backed by fast (µs) detection in patents and "guard beams" in related designs (B).
  - Academic DCCL power beaming (Opt. Express 2025): ≈150 mW delivered under eye-safe conditions with 650 mW intracavity at 1064 nm; corneal E < 0.1 W/cm² (A, snippet).
- **Lesson (INFERRED).** Power-beaming products reach Class 1 because the hazardous field **cannot exist without the receiver**, so blocking the beam removes it.
  Photophoretic traps have no such intrinsic collapse. An equivalent would be an *active* presence or occlusion interlock whose credit in classification is uncertain (C).
  Expect a notified/NRTL lab (UL, TÜV, Seibersdorf) to demand functional-safety evidence (IEC 61508 / ISO 13849-style) and to classify on worst-case single-fault power.

## 4. Particles in room air

- **Guidelines (A):** WHO 2021 PM2.5 5 / 15 µg/m³ and PM10 15 / 45 µg/m³ (annual / 24 h). PM10 is by definition a 50 % cut at **10 µm aerodynamic diameter**, so 20 µm motes mostly lie *outside* PM10.
- **Background (A/B):** ordinary rooms are about ISO Class 8-9 (≤ 29 300-293 000 particles/m³ ≥ 5 µm). Home indoor PM10 is ≈ 30-35 µg/m³.
  One walking person emits ~10⁶ particles/min ≥ 0.5 µm (10⁵ at rest) (B, cleanroom literature).
- **Fate (INFERRED):** aerodynamic diameter d_a = d·√ρ gives 20 µm cellulose ≈ 24 µm, carbon ≈ 27 µm, NaYF4 ≈ 41 µm.
  - Fall times from 1.5 m: ≈ 85 s (cellulose), 70 s (carbon), 30 s (NaYF4). 50 µm particles fall in 5-15 s.
  - Inhalable fraction (EN 481/ISO 7708: 0.5(1+e^(-0.06·d_a)), B) ≈ 0.54-0.62. **Not respirable** (50 % cut 4 µm), and thoracic only below ~10 µm d_a.
  - 5 µm particles (d_a 6-10 µm) are thoracic and stay up for ~10-20 min.
  - Deposition is mainly in the nose and pharynx with mucociliary clearance.
- **Mass budget, 1000 × 20 µm/h (INFERRED).** Per particle: 6.3 ng (cellulose), 7.5 ng (carbon), 17.6 ng (NaYF4).
  - Emission: 6.3-17.6 µg/h = **55-154 mg/yr**, almost all deposited on the floor or table beneath the volume.
  - Settling removes particles at 26-72 h⁻¹, far faster than 0.5 ACH. The well-mixed airborne level is **≈ 0.008 µg/m³ (~1 particle/m³)**.
  - That is ≈ 0.05 % of the WHO PM10 annual value, 10⁵× below background counts, and ~10⁹× below the OELs (P4).
  - A full dump of 1000 trapped particles (power loss) = 6-18 µg.
  - Near-field breathing-zone exposure right above an open volume is higher, but still ng-µg scale.
- **Toxicity notes:**
  - *Cellulose*: low-toxicity nuisance dust (ACGIH 10 mg/m³) (A).
  - *Carbon*: carbon black OSHA 3.5 / ACGIH 3 mg/m³ inhalable, IARC 2B (A). Laser-heated absorbing carbon in air can oxidise (roughly ≥ 400-500 °C, B/INFERRED) and shed **ultrafine soot or PAH**.
    Measure UFP (CPC) and CO near the volume. This, not the 20 µm mass, is the plausible inhalation issue (INFERRED).
  - *NaYF4:Yb,Er*: dissolution in water releases **F⁻ and Ln³⁺ ions**, which cause in-vitro cytotoxicity (A, Sci. Rep. 2022 snippet).
    Coated UCNPs showed no significant cytotoxicity at ≤ 0.1 mg/mL for 24 h (B). Micro-crystals have far less specific surface than nanoparticles (INFERRED).
    NaYF4 is **40 % F by mass**, so 154 mg/yr ≈ 62 mg F, about 50 toothpaste brushings (INFERRED). OELs are Y 1 mg/m³ and F 2.5 mg/m³ (A).
    Watch for breakage into fines, pica/ingestion by children, and the absence of any lanthanide consumer inhalation guideline (C).
  - The IR laser itself is not a chemical source unless it heats particles or dust to pyrolysis (INFERRED).

## 5. Thermal and fire

- **Focus intensity (INFERRED, mean over spot):**

| Spot Ø | 1 mW | 10 mW | 100 mW |
|---|---|---|---|
| 20 µm | 318 W/cm² | 3.2 kW/cm² | 32 kW/cm² |
| 50 µm | 51 W/cm² | 510 W/cm² | 5.1 kW/cm² |
| 100 µm | 12.7 W/cm² | 127 W/cm² | 1.3 kW/cm² |

  Every case meets or exceeds the ANSI-derived "> 10 W/cm² can ignite combustibles" flag (B). For such tiny spots, though, ignition is set by **absorbed power versus conduction loss**, not by irradiance.
  At NA 0.1 the beam is ≥ 1 mm wide once ≥ 5 mm from the focus (1.7 mm at NA 0.3), so hazards are confined to a few mm around each focus (INFERRED).
- **Skin.**
  - MPEs: S1-S3. With the ICNIRP small-beam note, the focus exceeds the skin EL at any power in range (C on scope).
  - Measured thresholds are much higher: 1070 nm, 10 s, 0.6 cm → ED50 ≈ 43 W/cm² peak (≈ 6 W). Thresholds *rise* as spots shrink (1540 nm: 20 J/cm² at 0.7 mm vs 7.4 J/cm² at 5 mm) (A).
    Schulmeister/ILSC modelling warns that for ~1 mm stationary beams the MPE margin can shrink to ≈ 1-3× (B).
  - Estimate (INFERRED, diffusion-limited point source, k = 0.45 W/m·K):
    - 980/1064 nm penetrates ~mm with ~50 % remitted: +0.12 K/mW, so 100 mW gives +12 K (warmth or pain at ~45 °C, no burn in seconds).
    - 1550 nm is absorbed within ~1 mm by water: +0.4 K/mW, so **100 mW gives ≈ +40 K, a burn within seconds**; ≤ 10 mW gives ≤ 4 K.
    - A hand sweeping through at 1-2 m/s dwells only ms per focus. The risk is a **stationary finger or a face at a trap**.
- **Hair.** Dark hair (melanin) is a strong absorber at 980/1064 nm. Laser hair removal uses tens of J/cm² over ms.
  A 20-100 µm focus at ≥ 10 mW on a 50-100 µm hair shaft will singe it (smell, smoke) (INFERRED).
- **Paper, fabric, dust.**
  - Surface-disk estimate ΔT = P_abs/(π k a) with k ≈ 0.1 W/m·K: **1 mW → 57-290 K; 10 mW → 0.6-2.9×10³ K** on black paper or fabric at the focus (INFERRED; ignores pyrolysis, convection and thin-sheet effects).
  - Local charring or a smoulder spot is expected at ≥ ~5-10 mW. Sustained flaming needs more heated area; hobbyist reports put "black paper lights" at ~0.5 W focused (C).
  - Cellulose ignites at ≈ 250 °C at minimum flux and > 600 °C surface temperature at high flux (B). White paper absorbs weakly at 980/1064 nm and more at 1550 nm (OH bands) (INFERRED).
  - The display's **own absorbing motes are the fuel**: photophoretic trapping works by heating the particle, so carbon motes at 10-100 mW can glow or oxidise (INFERRED; measure particle T by pyrometry).
- **Fire posture (INFERRED).** Total IR in a 1000-trap field is 1-100 W, i.e. Class 4 fire hazard in aggregate.
  Require beam dumps rated for total power, no combustibles in the dump path, over-temperature cut-outs, and occlusion shut-off.

## 6. Bottom line (INFERRED)
1. **Per trap**, 980/1064 nm traps above ~1.4-2 mW exceed Class 1 when the cone can reach the eye at 100 mm. High NA helps (≤ ~50-70 mW per isolated trap at NA 0.3).
   **Summed** cones make any 1000-trap field at 1-100 mW each Class 3B/4 unless beams are dumped away from all accessible 100 mm points.
2. **1550 nm is the only candidate that approaches Class 1** with mW-level traps (AEL 10 mW in 3.5 mm; ≈ 5 mW per trap for 300 overlapping NA-0.3 cones).
   But the corneal/skin hazard *at* the focus (0.1 W/cm² EL; burn estimate +0.4 K/mW) makes an open, touchable volume unacceptable at ≥ 10s of mW.
3. **Regulatory reality:** a US consumer IR display must be Class I/IEC Class 1 (no IR 3R, no variance path for touchable volumes). EU child-appealing → Class 1.
   The credible products are an **enclosed, interlocked vitrine ("Class 1 with embedded Class 4")**, or an open volume with sub-mW traps (probably below trapping threshold).
4. **Particles are not the problem** (ng/m³); laser-heated carbon smoke/UFP and NaYF4 fines are the chemical items to test.

## 7. Open items (verify with purchased texts)
- IEC 60825-1:2014 Table 11 reference point for an accessible focus, and whether active presence-sensing shut-off can be credited in classification (Wi-Charge-type argument).
- ICNIRP Table 7 note b scope (all t or t < 0.35 s only).
- EN 50689 numeric child-appealing limits.
- Wi-Charge certification documents (UL standard and number, FDA accession).
- Real (aberrated) trap far-field profiles, which must be measured with a 7 mm / 3.5 mm stop at 100 mm.
- Carbon and NaYF4 particle temperatures and emissions under trapping powers.

## Sources
- ICNIRP (2013) Health Phys 105(3):271-295 (via `CBORT-NCBIB/MPE-Calculator-Skin/web/standards/icnirp_2013.json`, Tables 3, 5, 7, 8 notes b/c); IEC 60825-1:2014 (Tables 3, 6, 8, 9, 10 via `github.com/llano1025/calEng` `src/calculators/elv/LaserSafetyShared.tsx`); ANSI Z136.1-2014/-2022 (via R3 and transcription `ansi_z136_2022.json`).
- IEC 60825-1 Ed.3 change summary (webstore.ansi.org / iec.ch snippets: Condition 2 removed, Class 1C added); IEC TR 60825-3:2022 (webstore.iec.ch/en/publication/64984); IEC 60825-12 (globalspec / ansi webstore snippets).
- 21 CFR 1040.10(b)(8), (b)(13), (e)(3)(i), (f)(9) and 1040.11(c): github.com/lucas-amberg/ecfr-analyzer `public/ecfr/2025-02-06/21/I/J/1040/`; FDA variance application texts (fda.gov/media/72256, downloads.regulations.gov FDA-2021-V-0986) snippets; FDA Laser Notice 56 (fda.gov/media/110120) and LN57 (fda.gov/media/107723) snippets.
- EN 50689:2021: ul.com "Understand the New Laser Product Safety Standards for Europe"; jjrlab.com; Seibersdorf white paper EN 50689 (title/snippet only).
- Precedents: support.apple.com "Class 1 Laser information for iPhone"; Bosch BMV080 datasheet copy (github.com/ALucek/RAG-Overview `documents/bmv080-ds.md`); ams TMF8829 datasheet copy (github.com/simonwkim02/vpla-stack); IEEE Spectrum "Under the Hood of Luminar's Long-Reach Lidar"; Laser Focus World "Safety questions raised about 1550 nm lidar"; Wi-Charge (en.wikipedia.org/wiki/Wi-Charge, digitaltrends.com "wi-charge … approved fda", patents US8525097B2 / US20170373543A1); "Safety analysis for a distributed coupled-cavity laser-based wireless power transfer", Opt. Express 2025 (arXiv 2507.21891).
- WHO global air quality guidelines 2021 (NBK574594); ISO 14644-1 class table (casrai.org, gmpinsiders snippets); cleanroom human-emission data (europeanpharmaceuticalreview.com, schillingengineering.de snippets); indoor PM10 in homes (aaqr.org; tandfonline 10.1080/26395940.2020.1728198 snippets).
- NIOSH/OSHA/ACGIH: cdc.gov/niosh/idlh/1333864 (carbon black), /7440655 (yttrium), /fluoride; cdc.gov/niosh pel88 cellulose 9004-34; acgih.org carbon-black.
- NaYF4 UCNP stability/cytotoxicity: Sci. Rep. 12, 2022 (s41598-022-07630-5); BME Frontiers review bmef.0120.
- Skin thresholds: Vincelette et al., J. Biomed. Opt. 19(3):035007 (2014); Zuclich et al. 1540 nm porcine (PubMed 16674191); DeLisi et al. JBO 25(3):035001 (2020); Jean/Schulmeister skin-model papers (BOE 12(5):2586; ILSC 2023 P101); JLA 38(4):042001 (1567 nm, 2026).
- Fire: university EHS pages (ehs.utexas.edu laser non-beam hazards; OSHA Technical Manual III-6); cellulose ignition review (Shen et al., researchgate 317041329).
- Photophoretic-trap context: Smalley et al., Nature 553:486 (2018); Barton et al., RSI 92:103002 (2021), via R5_optical_trap_displays.md.

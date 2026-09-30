# R3 - Safety limits for an open-air laser-plasma "hologram" projector (+ ultrasound haptics)

Compiled 2026-09-30. Scope: exact guideline numbers with sources for laser eye/skin MPE (1030-2600 nm),
laser product classes, UV, indoor air (O3/NO2/NO), audible + airborne-ultrasound noise, photosensitive flicker.

**Confidence codes**
- **A**: seen this session in a primary text, a verbatim quote, or an open-source transcription of the standard that cites table/page numbers.
- **B**: recalled from the standard/literature and cross-checked for internal consistency (e.g. MPE x aperture area = AEL; continuity at breakpoints), but not re-read this session.
- **C**: low confidence, conflicting sources, or known to differ between editions. **Must be checked against the purchased standard before design freeze.**
- **INFERRED**: my own derivation/interpolation/engineering reading (marked explicitly).

**Research-access caveat (read first).** In this session the proxy blocked almost all web domains (icnirp.org, iec.ch, osha.gov,
who.int, etc.). The shared web-search budget ran out partway through. Laser numbers were verified from (i) search-result
snippets, (ii) two open-source GitHub transcriptions of the standards: `CBORT-NCBIB/MPE-Calculator-Skin`
(`web/standards/icnirp_2013.json`, `ansi_z136_2022.json`, which cite ICNIRP 2013 Tables 5/7/8 and ANSI Z136.1-2022 Tables 9a-c/10a)
and `llano1025/calEng` (`src/calculators/elv/LaserSafetyShared.tsx`, an IEC 60825-1:2014 Table 3/10 implementation that contains
at least one typo, e.g. C7 exponent written 0.0018 instead of 0.018), and (iii) consistency checks. None of these substitutes for the
paid IEC 60825-1:2014 / ANSI Z136.1-2022 text.

---

## 0. MASTER TABLE

Notation: H = radiant exposure, E = irradiance, t = exposure/pulse duration [s], λ in nm. 1 J/cm² = 10⁴ J/m².
C_A (ANSI) = C4 (IEC); C_C (ANSI) = C7 (IEC); C_E (ANSI) = C6 (IEC); C_P (ANSI) = C5 (IEC).

| # | Hazard | Limit | Conditions | Source | Conf. |
|---|---|---|---|---|---|
| L1 | Retina, 1030 nm, ns pulse | H = 2×10⁻³ C_A J/m² (C_A=4.57 → 9.1×10⁻³ J/m² = 0.91 µJ/cm²) | 10⁻¹¹ ≤ t < 5×10⁻⁶ s, 7 mm aperture, small source | ICNIRP 2013 / IEC 60825-1:2014 Tab. A.1 (via Class 1 AEL 7.7×10⁻⁸ C4 J in calEng) | B |
| L2 | Retina, 1064 nm, ns pulse | H = 2×10⁻² C_C J/m² (= 2 µJ/cm²; 0.77 µJ in 7 mm) | 10⁻¹¹ ≤ t < 1.3×10⁻⁵ s | same (AEL 7.7×10⁻⁷ C7 J) | B |
| L3 | Retina, 1030/1064, fs-ps | 700-1050: H = 1×10⁻³ C_A J/m²; 1050-1400: 1×10⁻² C_C J/m² | 10⁻¹³ ≤ t < 10⁻¹¹ s | ICNIRP 2013 (raised vs 2007: 1.5×10⁻⁴ / 1.5×10⁻³) | **C** (one code uses 1×10⁻³ C7 for 1050-1400) |
| L4 | Retina, 1030/1064, 5 or 13 µs to 10 s | 700-1050: H = 18 C_A C_E t^0.75 J/m²; 1050-1400: 90 C_C C_E t^0.75 J/m² | small source C_E = 1 | ICNIRP 2013 / IEC 2014 | B |
| L5 | Retina, 1030/1064, long | E = 10 C_A C_C W/m² (1064: 50 W/m² = 5 mW/cm² → 1.9 mW in 7 mm) | 10 s(T2) < t ≤ 3×10⁴ s, α ≤ 1.5 mrad | ANSI "5.0 C_C mW/cm²" for 1.05-1.4 µm; IEC "10 C4 C7 W·m⁻²" | B |
| L6 | Cornea 1400-1500 nm | 10³ J/m² (0.1 J/cm²) ; 5.6×10³ t^0.25 J/m² ; 10³ W/m² (0.1 W/cm²) | 10⁻⁹-10⁻³ s ; 10⁻³-10 s ; 10-3×10⁴ s | ICNIRP 2013 Table 5 (transcription) | A |
| L7 | Cornea 1500-1800 nm (1550) | 10⁴ J/m² (1.0 J/cm²) ; 10³ W/m² (0.1 W/cm²) | 10⁻⁹-10 s ; 10-3×10⁴ s | ICNIRP 2013 Table 5; ANSI "static 1 J/cm²" | A |
| L8 | Cornea 1800-2600 nm (2 µm) | as 1400-1500: 0.1 J/cm² ; 0.56 t^0.25 J/cm² ; 0.1 W/cm² | 10⁻⁹-10⁻³ ; 10⁻³-10 ; 10-3×10⁴ s | ICNIRP 2013 Table 5 | A |
| L9 | Cornea >1400 nm, sub-ns | IEC 2014 (INFERRED from AEL): E = 10¹² W/m² (1400-1500, 1800-2600), 10¹³ W/m² (1500-1800), 10¹¹ W/m² (2600+) → 1550 nm, 100 fs: 1 J/m² | 10⁻¹³ ≤ t < 10⁻⁹ s | Class 1 AEL 8×10⁵ / 8×10⁶ / 8×10⁴ W ÷ 1 mm aperture (calEng) | **C** |
| L10 | Cornea/skin >1400, sub-ns, ANSI 2022 | 1400-1500: 0.03 / 0.10 J/cm²; 1500-1800: 0.10 / 0.30 J/cm²; 1800-2600: 0.01 / 0.03 J/cm² | 10⁻¹³-10⁻¹¹ / 10⁻¹¹-10⁻⁹ s | ANSI Z136.1-2022 Table 9c (skin; transcription); ocular assumed same (INFERRED) | **C** (about 1000× more lenient than L9 at 100 fs) |
| L11 | ANSI 2022 change 1400-1500 | 0.3 J/cm² (10⁻⁹-10⁻³ s); 0.56 t^0.25 + 0.2 J/cm² (10⁻³-4 s); 1.0 J/cm² (4-10 s) | skin table 9c | ANSI Z136.1-2022 (transcription) | B |
| S1 | Skin 400-1400 (1030/1064) | 200 C_A J/m² ; 1.1×10⁴ C_A t^0.25 J/m² ; 2×10³ C_A W/m² → 1064 nm: 0.1 J/cm² (ns), 1.0 W/cm² (CW) | 10⁻⁹-10⁻⁷ ; 10⁻⁷-10 ; 10-3×10⁴ s | ICNIRP 2013 Table 7 | A |
| S2 | Skin 400-1400, sub-ns (ANSI 2022) | 2.0 C_A×10⁻³ J/cm² ; 6.0 C_A×10⁻³ J/cm² | 10⁻¹³-10⁻¹¹ ; 10⁻¹¹-10⁻⁹ s | ANSI Z136.1-2022 Table 9b (transcription) | B |
| S3 | Skin >1400 nm | same as cornea L6-L8; long-term 0.1 W/cm² | t ≤ 10 s; t > 10 s, area ≤ 100 cm² | ICNIRP 2013 Table 5 | A |
| S4 | Skin >1400, large area | E = 10 000/A_s mW/cm² (A_s cm²); 10 mW/cm² (100 W/m²) | t > 10 s; 100-1000 cm²; >1000 cm² | ICNIRP 2013 Tab.7 note c, p.281; ANSI 2022 §8.4.2 | A |
| P1 | Repetitive pulses, rules | R1 each pulse ≤ single-pulse MPE; R2 any group in time T ≤ MPE(T); R3 C_P = N^-0.25 | all λ (R1, R2); R3 retinal thermal only | ICNIRP 2013 p.287 | A |
| P2 | C5 (IEC 2014) | C5 = 1 for α ≤ 5 mrad; α > 5 mrad: N^-0.25 ≥ 0.4 (N≤40) if α ≤ α_max, ≥ 0.2 (N≤625) if α > α_max; only t < 0.25 s | 400-1400 nm | Seibersdorf white paper (snippet); ANSI 2014 "Rule 3 only for extended sources" | B |
| P3 | >1400 nm & skin | C5/C_P **not applied**: rules 1+2 only | eye >1400 nm, all skin | IEC 60825-1:2014 (snippet); ICNIRP 2013 p.287 | A |
| P4 | Pulse grouping T_i | 5 µs (400-1050), 13 µs (1050-1400), 1 ms (1400-1500), 10 s (1500-1800), 1 ms (1800-2600), 100 ns (2600+) | pulses within T_i are summed as one | IEC 60825-1:2014 (calEng) | B |
| A1 | Eye limiting aperture | 7 mm (400-1400); 1 mm (180-400) | MPE averaging | IEC 2014 Tab. A.3 / ANSI | B |
| A2 | Eye aperture >1400 nm | 1 mm (t ≤ 0.35 s); 1.5 t^(3/8) mm (0.35-10 s); 3.5 mm (≥10 s); 11 mm (0.1-1 mm λ) | ANSI uses 0.3 s breakpoint (C) | IEC 2014 Tab.10 (calEng) | B |
| A3 | Skin aperture | 3.5 mm (180 nm-100 µm); 11 mm (100 µm-1 mm); if beam < 1 mm use actual (non-averaged) H | | ICNIRP 2013 Tab. 8 + Tab.7 note b; ANSI 2022 Tab.10a | A |
| K1 | Class 1 AEL 1550 nm | 8×10⁻³ J/pulse (10⁻⁹-0.35 s); 1.8×10⁻² t^0.75 J (0.35-10 s); **10 mW** (>10 s); 8×10⁶ W peak (10⁻¹³-10⁻⁹ s) | Cond. 3: 100 mm, 1 mm → 3.5 mm aperture | IEC 60825-1:2014 Table 3 (calEng); MPE × area checks | B (sub-ns C) |
| K2 | Class 1 AEL 2 µm | 8×10⁻⁴ J (10⁻⁹-10⁻³ s); 4.4×10⁻³ t^0.25 J (10⁻³-0.35 s); 1.0×10⁻² t J (0.35-10 s); **10 mW** (>10 s); 8×10⁵ W (sub-ns) | 1800-2600 nm | same; "4.4 t^0.25 mJ" confirmed for 1400-1500 (search snippet) | B |
| K3 | Class time base | 100 s (λ > 400 nm); **30 000 s** where intentional long-term viewing is inherent (a display) and for λ ≤ 400 nm; 0.25 s for Class 2/2M/3R | classification | IEC 60825-1:2014 §4.3e (calEng) | B |
| K4 | US consumer display | "Demonstration laser product" (entertainment/display): no human access above Class I/IIa/II/IIIa without a variance (21 CFR 1040.11(c), 1010.4); FDA accepts IEC 60825-1 Ed.3 via Laser Notice 56 (2019) | USA | 21 CFR 1040.10/.11 | B |
| K5 | Incoherent (plasma) emission | IEC 62471 Exempt: E_S ≤ 0.001 W/m² eff (30 000 s); E_UVA ≤ 10 W/m² (1000 s); L_B ≤ 100 W m⁻² sr⁻¹ (10⁴ s); E_IR ≤ 100 W/m² (1000 s) | lamp/LED-type sources | IEC 62471:2006 / CIE S009 | B |
| U1 | Actinic UV 180-400 nm | 30 J/m² effective (S(λ)-weighted) per 8 h | skin + eye | ICNIRP 2004 UV; ACGIH TLV | A |
| U2 | S(λ) at plasma lines | 315: 0.003; 337: ≈3.2×10⁻⁴; 357: ≈1.5×10⁻⁴; 380: 6.4×10⁻⁵; 391: ≈4.2×10⁻⁵ | tabulated 5 nm steps; interp. INFERRED | ICNIRP 2004 Tab.1 / ACGIH | A (tab.) / INFERRED |
| U3 | UVA eye (315-400) | 10⁴ J/m² (1.0 J/cm²) unweighted for t < 1000 s; 10 W/m² (1.0 mW/cm²) for t ≥ 1000 s | 8 h | ICNIRP 2004; ACGIH | A |
| G1 | O3 occupational | OSHA PEL 0.1 ppm 8-h TWA; NIOSH REL C 0.1 ppm; ACGIH TLV 0.05 (heavy) / 0.08 (moderate) / 0.10 (light) ppm, 0.20 ppm (≤2 h) | workers | 29 CFR 1910.1000; NIOSH; ACGIH | A |
| G2 | O3 device emission | ≤ **0.050 ppm** (UL 867 §37 test chamber) | indoor air-cleaning devices sold in California | CARB 17 CCR §94800-94810 | A |
| G3 | O3 device (medical) | ≤ 0.05 ppm | FDA device ozone limit | 21 CFR 801.415 | B |
| G4 | O3 ambient/indoor | WHO 2021: 100 µg/m³ 8-h, 60 µg/m³ peak season; EPA NAAQS 0.070 ppm 8-h; Health Canada indoor 40 µg/m³ (20 ppb) 8-h; EU target 120 µg/m³ max daily 8-h | public | WHO AQG 2021; 40 CFR 50.19; HC RIAQG; Dir. 2008/50/EC | A (WHO) / B |
| G5 | NO2 | WHO 2021: 25 µg/m³ 24-h, 10 µg/m³ annual, 200 µg/m³ 1-h; EPA 100 ppb 1-h, 53 ppb annual; OSHA C 5 ppm; NIOSH STEL 1 ppm; ACGIH TLV 0.2 ppm; HC indoor 170 µg/m³ 1-h, 20 µg/m³ 24-h; EU OEL 0.5 ppm 8-h / 1 ppm STEL | | WHO; 40 CFR 50.11; NIOSH; ACGIH; Health Canada 2015; Dir. 2017/164 | A (WHO/EPA/OSHA/NIOSH/ACGIH) / B |
| G6 | NO | OSHA PEL 25 ppm TWA; NIOSH REL 25 ppm; EU IOELV 2 ppm 8-h; no WHO AQG | | 29 CFR 1910.1000; Dir. 2017/164 | A (OSHA) / B |
| G7 | Indoor dynamics | O3 surface removal typically 2-4 h⁻¹ (one occupied CA house: 1.3 h⁻¹); US residential AER central ≈ 0.45 h⁻¹; purifier sizing: smoke CADR (cfm) ≥ 2/3 × floor area (ft²) | well-mixed room | Weschler 2000; Lee 1999; Liu 2021 PNAS; EPA EFH 2011; AHAM AC-1 | B (Liu: A) |
| N1 | Residential noise | Living rooms 35 dB LAeq,16h; bedrooms 30 dB LAeq,8h and 45 dB LAmax (single events) | indoors | WHO Guidelines for Community Noise 1999 | A |
| N2 | Occupational noise | NIOSH REL 85 dBA 8-h, 3 dB exchange; OSHA PEL 90 dBA/5 dB, action level 85 dBA; impulse peak 140 dB; EU 2003/10/EC 87 dB(A)/140 dB(C) | workers | 29 CFR 1910.95; NIOSH 98-126 | B |
| N3 | Airborne ultrasound, ACGIH | Ceiling (1/3-oct): 105 dB (10-20 kHz), 110 (25 kHz), 115 (31.5-100 kHz); 8-h TWA 88/89/92/94 dB at 10/12.5/16/20 kHz; +30 dB allowed if there is no body coupling (140/145) | at the ear, re 20 µPa | ACGIH (AFOSH 48-20 Tab.4; Leighton 2016 Tab.1) | A |
| N4 | Airborne ultrasound, public | IRPA/INIRC 1984: **70 dB** (20 kHz band), **100 dB** (25-100 kHz bands); occupational 75/110 dB | general public, interim | INIRC-IRPA 1984 (quoted in Leighton 2016) | A |
| N5 | Ultrasound, equipment | ≤ 110 dB (20-100 kHz) at operator position and 1 m; inside useful beam > 110 dB needs a marking | lab/measurement equipment | BS EN 61010-1:2010 (quoted in Leighton 2016) | A |
| N6 | Ultrasound > 100 kHz | **No airborne exposure guideline found** | | Leighton 2016 (guidelines stop at 100 kHz) | A (absence) |
| F1 | Flashing content | ≤ 3 general/red flashes in any 1 s, OR combined flash area ≤ 0.006 sr (25 % of any 10° field) | general flash: ΔL ≥ 10 % rel. lum., darker < 0.80 | WCAG 2.x SC 2.3.1 (w3c/wcag source) | A |
| F2 | Broadcast flash | general flash = pair of opposing changes ≥ 20 cd/m² with darker state < 160 cd/m² (HDR: Michelson ≥ 1/17); > 3 flashes/s avoided | TV/video | ITU-R BT.1702 (as cited in WCAG Understanding 2.3.1) | A |
| F3 | Light modulation | Low risk: Mod% < 0.025·f (f < 90 Hz), < 0.08·f (90-1250 Hz); no-effect: < 0.01·f (<90 Hz), < 0.0333·f (90-3000 Hz) | periodic flicker | IEEE 1789-2015 §8.1.1 (open-source impl.) | B |

---

## 1. Laser MPE: eye (ICNIRP 2013 = basis of IEC 60825-1:2014 Annex A; ANSI Z136.1-2014/-2022)

### 1.1 Correction factors and parameters
| Symbol (ANSI / IEC) | Value | Conf. |
|---|---|---|
| C_A / C4 | 1.0 (400-700); **10^(0.002(λ-700))** (700-1050); **5.0** (1050-1400). At 1030 nm: 10^0.66 = **4.57**; at 1064: **5.0** | A (ICNIRP/ANSI transcriptions) |
| C_C / C7 | 1.0 (700-1150); **10^(0.018(λ-1150))** (1150-1200); **8 + 10^(0.04(λ-1250))** (1200-1400) (IEC 2014 new formula above 1200 nm). At 1030/1064: 1.0 | B (the 2014 change is confirmed by a search snippet) |
| C_E / C6 | 1 for α ≤ α_min; α/α_min for α_min < α ≤ α_max; α_max/α_min for α > α_max | B |
| α_min | 1.5 mrad | A (code) |
| α_max (IEC 2014) | 5 mrad (t < 625 µs); 200·t^0.5 mrad (625 µs ≤ t ≤ 0.25 s); 100 mrad (t > 0.25 s) | B (code + white paper) |
| T2 | 10 s (α ≤ 1.5 mrad); **10 × 10^((α-1.5)/98.5)** s (1.5 < α ≤ 100 mrad); 100 s (α > 100 mrad) | B |
| C_P / C5 | N^-0.25, restricted in 2014 (see §1.4) | B |

### 1.2 1030-1064 nm (retinal thermal hazard region, 7 mm aperture), small source (C_E = 1)
IEC form (J·m⁻² / W·m⁻²). ANSI Z136.1 uses the same values in J/cm² (×10⁻⁴).
| Duration t | 700-1050 nm (1030) | 1050-1400 nm (1064) | Conf. |
|---|---|---|---|
| 10⁻¹³-10⁻¹¹ s | H = 1.0×10⁻³ C_A | H = 1.0×10⁻² C_C (pattern value) | C |
| 10⁻¹¹ s - T_i (5 µs / 13 µs) | H = 2×10⁻³ C_A (ANSI: 2.0 C_A×10⁻⁷ J/cm²) | H = 2×10⁻² C_C (ANSI: 2.0 C_C×10⁻⁶ J/cm²) | B |
| T_i - 10 s | H = 18 C_A C_E t^0.75 (ANSI 1.8 C_A t^0.75 mJ/cm²) | H = 90 C_C C_E t^0.75 (ANSI 9.0 C_C t^0.75 mJ/cm²) | B |
| 10 s - 3×10⁴ s (α ≤ 1.5 mrad) | E = 10 C_A C_C W/m² (1.0 C_A mW/cm²) | E = 10 C_A C_C = 50 C_C W/m² (5.0 C_C mW/cm²) | B |
| t > T2 (extended) | E = 18 C_A C_C C_E T2^-0.25 W/m² | same form | B |
Consistency checks (INFERRED): 18·(5×10⁻⁶)^0.75 = 1.9×10⁻³ ≈ 2×10⁻³; 90·(1.3×10⁻⁵)^0.75 = 1.95×10⁻² ≈ 2×10⁻²;
18·10^0.75/10 = 10.1 W/m². The 2013/2014 ns plateau was **lowered by 2.5×** from the 2007 values (5×10⁻³ C_A / 5×10⁻² C_C J/m²).
The fs limits were **raised** from 1.5×10⁻⁴ C_A / 1.5×10⁻³ C_C J·m⁻² (2007) (B).
Worked values: 1064 nm, 10 ns → 2 µJ/cm² (0.77 µJ into 7 mm); 1030 nm → 0.91 µJ/cm² (0.35 µJ). 1064 nm CW staring → 5 mW/cm² (1.9 mW into 7 mm).

### 1.3 >1400 nm (cornea); aperture per A2
| t | 1400-1500 nm | 1500-1800 nm (1550) | 1800-2600 nm (2 µm) | 2600 nm-1 mm | Source/Conf. |
|---|---|---|---|---|---|
| 10⁻¹³-10⁻⁹ s | IEC: E = 10¹² W/m²; ANSI-2022: 0.03 J/cm² (<10 ps), 0.10 (10 ps-1 ns) | IEC: 10¹³ W/m²; ANSI: 0.10 / 0.30 J/cm² | IEC: 10¹² W/m²; ANSI: 0.01 / 0.03 J/cm² | IEC: 10¹¹ W/m²; ANSI: 1×10⁻³ / 3×10⁻³ | C (IEC values INFERRED from AEL; 2007 ed. had 10¹¹ W/m² for all >1400) |
| 10⁻⁹-10⁻⁷ s | 10³ J/m² (0.1 J/cm²) | 10⁴ J/m² (1.0 J/cm²) | 10³ J/m² | 100 J/m² (0.01 J/cm²) | A |
| 10⁻⁷-10⁻³ s | 10³ J/m² | 10⁴ J/m² | 10³ J/m² | 5.6×10³ t^0.25 J/m² | A |
| 10⁻³-10 s | 5.6×10³ t^0.25 J/m² (0.56 t^0.25 J/cm²) | 10⁴ J/m² | 5.6×10³ t^0.25 J/m² | 5.6×10³ t^0.25 | A |
| 10-3×10⁴ s | 1000 W/m² (0.1 W/cm²) | 1000 W/m² | 1000 W/m² | 1000 W/m² | A |
- ICNIRP footnote (A, search snippet): *for beam diameters < 1 mm and pulse durations < 0.35 s, compare the actual (non-averaged) radiant exposure with the EL.*
- ICNIRP 2013 also added a corneal limit for **1250 (1200)-1400 nm** in addition to the retinal one (A, snippet). This does not affect 1030/1064.
- **ANSI Z136.1-2022 revised 1400-1500 nm** (L11): 0.3 J/cm² (1 ns-1 ms), 0.56 t^0.25 + 0.2 J/cm² (1 ms-4 s), 1.0 J/cm² (4-10 s). Continuity checks out (INFERRED). IEC 60825-1:2014 still uses the ICNIRP 2013 values.
- **Critical open item (C):** for fs pulses at 1550 nm the IEC-derived limit (10¹³ W/m² × 10⁻¹³ s = 1 J/m² = 10⁻⁴ J/cm²) and ANSI-2022 (0.1 J/cm²) differ by **about 10³**. Design to the lower value until the standard texts are checked.

### 1.4 Repetitively pulsed / scanned exposure
Verbatim (ICNIRP 2013 p. 287, via transcription, A):
- **Rule 1**: "The exposure from any single pulse shall not exceed the EL for a single pulse of that pulse duration."
- **Rule 2**: "The exposure from any group of pulses delivered in time T shall not exceed the EL for time T." (T from pulse duration to total exposure duration.)
- **Rule 3**: "For the retinal thermal limits, an additional factor Cp is applied": H_pulse ≤ H_single × C_P, **C_P = N^-0.25** (N = pulses in T2 or T_max).

IEC 60825-1:2014 / ANSI 2014 restrictions (B):
- C5 applies only to pulse durations < 0.25 s. **α ≤ 5 mrad → C5 = 1.** α > 5 mrad → C5 = N^-0.25 floored at 0.4 (count ≤ 40 pulses) for α ≤ α_max, and at 0.2 (≤ 625 pulses) for α > α_max (Seibersdorf white paper snippet). ANSI 2014: "Rule 3 only applies in specific circumstances such as extended sources" (snippet).
- Pulses closer than **T_i** (P4) are grouped into one effective pulse.
- An open-source IEC implementation also uses **C5 = 5·N^-0.25 (min 0.4) for N > 600** in the "t ≤ T_i / emission > 0.25 s" branch (C). Verify this in the standard.
- **Exceptions:** λ > 1400 nm: C5 is **not applicable**. Only rules 1 and 2 apply (A, snippet of IEC 2014 citing ICNIRP 2013). **Skin: Rule 3 never applies** (A, ICNIRP p.287; ANSI 2022 §8.4.1).
- Older editions (IEC 2007, ANSI 2007) applied C_P = N^-0.25 to all 400-10⁶ nm. Many legacy tools still do this, so check any calculator you use.

INFERRED design examples (single point, 1 kHz, 10 ns pulses, staring > 10 s):
- 1550 nm: Rule 1 gives 1 J/cm² per pulse (7.9 mJ in 1 mm). Rule 2 gives 0.1 W/cm² × 0.0962 cm² (3.5 mm) = 9.6 mW, which is **≤ 9.6 µJ/pulse**. Rule 2 dominates by about 800×.
- 1064 nm: Rule 1 allows 0.77 µJ/pulse (7 mm). Rule 2 allows 1.9 mW, i.e. 1.9 µJ/pulse. Rule 1 dominates, and C5 = 1 (small source).
- For comparison, the legacy C_P with N = 10⁴ in T2 = 10 s gives 0.1 × 0.77 = 0.077 µJ.

### 1.5 Limiting apertures (A1-A3)
Eye: 1 mm (180-400 nm); **7 mm (400-1400 nm)**; >1400 nm to 100 µm: **1 mm (t ≤ 0.35 s), 1.5·t^(3/8) mm (0.35-10 s), 3.5 mm (t ≥ 10 s)**; 11 mm (0.1-1 mm).
Skin: 3.5 mm (180 nm-100 µm), 11 mm (100 µm-1 mm). ICNIRP 2013 defines beam diameter at 1/e points (p. 288) (A).
ANSI Z136.1 uses 0.3 s instead of 0.35 s for the >1.4 µm breakpoint (C).

---

## 2. Laser MPE: skin

| λ | t | ICNIRP 2013 (A) | ANSI Z136.1-2022 (B, transcription) |
|---|---|---|---|
| 400-1400 (1030/1064) | 10⁻¹³-10⁻¹¹ s | not in consulted source | 2.0 C_A×10⁻³ J/cm² |
| | 10⁻¹¹-10⁻⁹ s | not in consulted source (IEC 2007: 2×10¹¹ C4 W/m², C) | 6.0 C_A×10⁻³ J/cm² |
| | 10⁻⁹-10⁻⁷ s | 200 C_A J/m² (0.02 C_A J/cm²) | 2.0 C_A×10⁻² J/cm² |
| | 10⁻⁷-10 s | 1.1×10⁴ C_A t^0.25 J/m² | 1.1 C_A t^0.25 J/cm² |
| | 10-3×10⁴ s | 2.0×10³ C_A W/m² (0.2 C_A W/cm²) | 0.2 C_A W/cm² |
| 1400-1500 | as §1.3 (cornea = skin) | 0.1 J/cm² ; 0.56 t^0.25 ; 0.1 W/cm² | see L10/L11 |
| 1500-1800 | | 1.0 J/cm² (≤10 s) ; 0.1 W/cm² | 0.10/0.30/1.0 J/cm²; 0.1 W/cm² |
| 1800-2600 | | 0.1 J/cm² ; 0.56 t^0.25 ; 0.1 W/cm² | 0.01/0.03/0.1 J/cm²; 0.56 t^0.25; 0.1 W/cm² |
- Worked values: 1064 nm → 0.1 J/cm² (1-100 ns), 1.0 W/cm² CW; 1030 nm → 0.091 J/cm², 0.91 W/cm² (INFERRED arithmetic).
- **Large-area rule** (λ > 1400 nm, t > 10 s; ICNIRP Tab. 7 note c / p.281; ANSI §8.4.2) (A): E_limit = 0.1 W/cm² for A_s ≤ 100 cm²;
  **10 000/A_s mW/cm²** (A_s in cm²) for 100-1000 cm²; **10 mW/cm²** (100 W/m²) above 1000 cm². IEC wording: "between 0.01 m² and 0.1 m² the MPE varies inversely with irradiated area; > 0.1 m²: 100 W·m⁻²" (B).
- Neither standard addresses how the large-area rule applies to scanning beams (A, stated in the transcription notes).
- UV skin successive-day derating: factor 2.5 (280-400 nm) (A, transcription). Only relevant if the plasma UV is treated as laser-like; normally use §4.

---

## 3. Laser product classification, embedded products, scanning, shows

### 3.1 Class 1 AEL, IEC 60825-1:2014 Table 3 (B; cross-checks: MPE × aperture area)
| t | 1400-1500 | **1500-1800 (1550 nm)** | **1800-2600 (2 µm)** | 2600-4000 |
|---|---|---|---|---|
| 10⁻¹³-10⁻⁹ s (C) | 8×10⁵ W | 8×10⁶ W | 8×10⁵ W | 8×10⁴ W |
| 10⁻⁹-10⁻⁷ s | 8×10⁻⁴ J | 8×10⁻³ J | 8×10⁻⁴ J | 8×10⁻⁵ J |
| 10⁻⁷-10⁻³ s | 8×10⁻⁴ J | 8×10⁻³ J | 8×10⁻⁴ J | 4.4×10⁻³ t^0.25 J |
| 10⁻³-0.35 s | 4.4×10⁻³ t^0.25 J | 8×10⁻³ J | 4.4×10⁻³ t^0.25 J | 4.4×10⁻³ t^0.25 J |
| 0.35-10 s | 1.0×10⁻² t J | 1.8×10⁻² t^0.75 J | 1.0×10⁻² t J | 1.0×10⁻² t J |
| 10 s-3×10⁴ s | **1.0×10⁻² W** | **1.0×10⁻² W (10 mW)** | **1.0×10⁻² W** | 1.0×10⁻² W |
Checks (INFERRED): 10⁴ J/m² × π(0.5 mm)² = 7.85 mJ; 5600 t^0.25 × π(0.5 mm)² = 4.4×10⁻³ t^0.25 J; 1000 W/m² × π(1.75 mm)² = 9.6 mW.
1064 nm Class 1 (for reference, B): 7.7×10⁻⁷ C7 J (10⁻¹¹-1.3×10⁻⁵ s); 3.5×10⁻³ C7 t^0.75 J (to 10 s); 3.9×10⁻⁴ C4 C7 W ≈ 2 mW (t > 10 s).
- **Measurement conditions (B):** Condition 3 is at **100 mm** from the reference point with a 7 mm aperture (400-1400 nm) or 1 mm / 1.5 t^(3/8) / 3.5 mm (1400-4000 nm). Condition 1 (optical aids) is at 2000 mm with 50 mm (400-1400) or 7× the Condition 3 aperture (1400-4000).
- **Time base (K3):** a display is designed for intentional viewing, so classification uses **T = 30 000 s**. Rule 2 average-power limits therefore apply over up to 8.3 h.
- The accessible emission is evaluated over all operation and **reasonably foreseeable single-fault conditions** (B). For a scanner, a scan or mirror stall is a single fault. If a stall would raise the class, an independent scan-failure detector/shut-off is needed.

### 3.2 "Class 1 with an embedded laser"
- Definition (IEC 60825-1:2014 §3 / ANSI Z136.1, B): an **embedded laser product** is one that, because engineering features limit the accessible emission, has a **lower class than the laser inside it**. Typical cases are laser printers, DVD drives, and enclosed Class-4 machining systems labelled Class 1.
- "Class 1 during operation" means that in normal use no accessible position exceeds the Class 1 AEL, which is achieved by a protective housing plus safety interlocks. Panels that give access to Class 3B/4 radiation during service must be interlocked or tool-removable and labelled. The service or maintenance state can expose higher-class radiation, so it is controlled by procedure. (B)
- **Implication (INFERRED):** an air-plasma voxel needs focal intensities of roughly 10¹¹ W/cm² (ns, 1064 nm) to 10¹³-10¹⁴ W/cm² (fs). These are order-of-magnitude literature values (C), not safety numbers, and they are about 10⁸-10¹⁰ times any MPE. A consumer device can therefore be **Class 1 only if the plasma volume and the whole beam path are inaccessible**, e.g. inside a sealed, interlocked, laser-opaque but visibly transparent enclosure, with the beam terminated in a dump. An open-air volume that a hand or eye can enter is a Class 4 exposure. Engineering controls such as presence sensing (light curtains, depth cameras) that blank the beam are safety functions. They would need functional-safety evidence (e.g. IEC 61508/ISO 13849-style) and are not accepted by the classification standard as a way to lower the class (B/INFERRED).
- EU consumer route: **EN 50689:2021** (consumer laser products) restricts consumer products to low classes, and embedded higher classes are allowed only inside a Class 1 product (C; verify scope and limits).

### 3.3 Scanned beams (B)
- Evaluate scanned emission at the Condition 3 location and aperture. For a stationary aperture, each sweep is a pulse whose **duration is the dwell time** (aperture diameter / spot speed). The pulse rate is the frame rate, and rules 1 and 2 (and C5 where applicable) apply to that pulse train.
- For extended or scanned apparent sources in 400-1400 nm, α and C6 depend on the scan pattern. See the Seibersdorf white paper "Extended Source AEL Analysis of Scanned Laser Emission".
- Scan-failure safeguard as in §3.1.

### 3.4 Laser shows / displays in open air
- **FDA (USA), B:** 21 CFR 1040.10(b) defines a "demonstration laser product" to include entertainment and advertising display. §1040.11(c) limits these to Class I/IIa/II/IIIa accessible emission unless the manufacturer holds a **variance** (21 CFR 1010.4; Form FDA 3147 for light shows).
- FDA's usual variance conditions keep beams ≥ 3 m above and ≥ 2.5 m laterally from audience surfaces. **Audience scanning** is permitted only when the MPE is not exceeded in audience areas (C: exact wording is in the variance conditions / FDA guidance).
- FDA **Laser Notice 56** (2019) accepts conformance with IEC 60825-1 Ed. 3 in lieu of parts of 1040.10/.11 (B).
- **IEC TR 60825-3** (guidance for laser displays and shows) and **ANSI Z136.10** (entertainment, displays, exhibitions) (C: check current editions).
- **Incoherent emission** from the plasma spark (broadband visible + N2 UV lines) falls under **IEC 62471 / CIE S009** (photobiological safety of lamps), not IEC 60825. Risk-group limits are in K5. RG1: E_S 0.003 W/m² (10⁴ s), E_UVA 33 W/m² (300 s), L_B 10⁴ W m⁻² sr⁻¹ (100 s), E_IR 570 W/m² (100 s). RG2: 0.03, 100, 4×10⁶ (0.25 s), 3200 W/m² (10 s) (B).
- IR eye (780-3000 nm, incoherent): E_IR ≤ 18 000·t^-0.75 W/m² (t ≤ 1000 s), 100 W/m² (t > 1000 s) (B; ICNIRP 2013 incoherent / IEC 62471).

---

## 4. UV exposure limits (plasma emission; incoherent)

- **Actinic UV, 180-400 nm** (skin + eye): H_eff = Σ E_λ·S(λ)·Δλ·t ≤ **30 J/m² effective within 8 h** (A: ICNIRP 2004, ACGIH).
  Permissible time t_max = 30 / E_eff [s] (E_eff in W/m²).
- **UVA 315-400 nm, eye** (unweighted): ≤ **10⁴ J/m² (1.0 J/cm²)** for t < 1000 s; ≤ **10 W/m² (1.0 mW/cm²)** for t ≥ 1000 s (A: ICNIRP 2004 "within an 8-h period ... should not exceed 10⁴ J·m⁻²"; ACGIH 1.0 J/cm² <1000 s, 1.0 mW/cm² >1000 s).
- **S(λ) table (ICNIRP 2004 Tab. 1 = ACGIH), UV-A/B portion** (A for 335/340/355/360; B for the rest; the TLV column = 30/S(λ) checks out):
  313: 0.006 | 315: **0.003** | 316: 0.0024 | 317: 0.0020 | 318: 0.0016 | 319: 0.0012 | 320: 0.0010 | 322: 0.00067 | 323: 0.00054 | 325: 0.00050 | 328: 0.00044 | 330: 0.00041 | 333: 0.00037 | **335: 0.00034 | 340: 0.00028** | 345: 0.00024 | 350: 0.00020 | **355: 0.00016 | 360: 0.00013** | 365: 0.00011 | 370: 9.3×10⁻⁵ | 375: 7.7×10⁻⁵ | **380: 6.4×10⁻⁵** | 385: 5.3×10⁻⁵ | **390: 4.4×10⁻⁵ | 395: 3.6×10⁻⁵** | 400: 3.0×10⁻⁵. Peak is 270 nm: 1.000.
- **At N2/N2⁺ emission lines** (INFERRED, log-linear interpolation): S(315.9) ≈ 0.0025 · S(337.1) ≈ **3.15×10⁻⁴** · S(357.7) ≈ **1.47×10⁻⁴** · S(380.5) ≈ **6.3×10⁻⁵** · S(391.4) ≈ **4.2×10⁻⁵**.
  Example: an effective 30 J/m² at 337 nm alone corresponds to about 9.5×10⁴ J/m² unweighted. That is **above** the UVA 10⁴ J/m² eye limit, so **for 337-400 nm lines the UVA eye limit governs**; for 315-320 nm the actinic limit governs (INFERRED).
- Laser (coherent) UV, for reference (A, ICNIRP 2013 Table 5 via transcription): 180-302 nm 30 J/m²; 302-315 nm stepwise (40 J/m² at 302 to 6.3 kJ/m² at 313-315); 315-400 nm 10 kJ/m² (t ≥ 10 s); thermal cap 5.6 t^0.25 kJ/m² (10⁻⁹-10 s).

---

## 5. Indoor air: O3, NO2, NO

### 5.1 Limits (see G1-G6). Conversions at 25 °C, 1 atm (INFERRED arithmetic)
O3: 1 ppm = 1.96 mg/m³ (WHO 100 µg/m³ ≈ 51 ppb; 60 µg/m³ ≈ 31 ppb). NO2: 1 ppm = 1.88 mg/m³ (200 µg/m³ ≈ 106 ppb; 25 ≈ 13 ppb; 10 ≈ 5.3 ppb). NO: 1 ppm = 1.23 mg/m³.
- Ozone, occupational (A): OSHA PEL 0.1 ppm 8-h TWA. ACGIH TLV 0.05 ppm heavy / 0.08 moderate / 0.10 light work (8-h), 0.20 ppm for ≤ 2 h. NIOSH REL 0.1 ppm ceiling.
- Ozone, products (A): CARB requires indoor air-cleaning devices to be certified at **≤ 0.050 ppm** per **ANSI/UL 867 §37** (since 2010; 17 CCR 94800 ff.). Related limits (B): FDA 21 CFR 801.415 0.05 ppm; IEC/EN 60335-2-65 (air cleaners) 5×10⁻⁶ % by volume = 0.05 ppm (C); FAA 14 CFR 25.832 cabin 0.25 ppm any time above FL320 and 0.1 ppm 3-h TWA above FL270.
- Ozone, public: WHO 2021 AQG **100 µg/m³ 8-h**, 60 µg/m³ peak season (A). EPA NAAQS 0.070 ppm (8-h, 2015) (B). Health Canada residential indoor 40 µg/m³ (20 ppb) 8-h (B). EU target 120 µg/m³ max daily 8-h mean; information threshold 180 and alert 240 µg/m³ 1-h (B).
- NO2 (A unless noted): WHO 2021 **25 µg/m³ 24-h, 10 µg/m³ annual, 200 µg/m³ 1-h**. EPA NAAQS **100 ppb 1-h** (3-yr avg of 98th percentile daily max) and **53 ppb annual**. OSHA PEL 5 ppm ceiling. NIOSH REL 1 ppm 15-min STEL. ACGIH TLV-TWA 0.2 ppm. Health Canada indoor 170 µg/m³ (90 ppb) 1-h and 20 µg/m³ (11 ppb) 24-h (B). EU IOELV (Dir. 2017/164) 0.5 ppm 8-h, 1 ppm STEL (B). EU 2030 ambient (Dir. 2024/2881) 20 µg/m³ annual, 50 µg/m³ 24-h (C).
- NO: OSHA PEL 25 ppm TWA (A); NIOSH REL 25 ppm (B); ACGIH TLV 25 ppm (B); EU IOELV 2 ppm 8-h (B). There is no WHO guideline. Indoors NO reacts with O3 to form NO2 (NO + O3 → NO2 + O2), so treat NO emission as NO2 precursor load (INFERRED).
- Byproduct note (INFERRED/C): hot laser-induced air plasma (~10⁴ K) mainly forms **NO**, via Zeldovich chemistry. UV/cold-discharge chemistry forms O3. NO2 forms downstream. Measure all three.

### 5.2 Room dynamics and removal (B unless noted)
- Well-mixed steady state (INFERRED, standard mass balance): **C_ss = S / [V·(λ_ACH + k_surf + η·CADR/V)] + C_background·(penetration term)**, with S the emission rate (µg/h), V the room volume (m³), and λ, k in h⁻¹.
- **O3 surface removal (k_surf):** residences typically **~2-4 h⁻¹**. Examples: Weschler 2000 review (Indoor Air 10:269); Lee et al. 1999 (JAWMA 49:1238, 43 homes, central value ≈ 2.8 h⁻¹, B); Yao & Zhao 2018 (Build. Environ. 142:101, Chinese homes). **Liu et al. 2021 PNAS** reported a "relatively low indoor ozone decay constant (1.3 h⁻¹)" in an occupied California house (A).
- **Air-change rate:** US residential central tendency ≈ **0.45 h⁻¹** (EPA Exposure Factors Handbook 2011 ch. 19; 10th percentile ≈ 0.18) (B). Tight new homes are about 0.1-0.3 h⁻¹; the user's 0.5-1 h⁻¹ is typical of older or leakier stock.
- **Portable air cleaner CADR** (AHAM AC-1, particles only): consumer units are typically ~100-400 cfm (170-680 m³/h). The AHAM sizing rule is **smoke CADR ≥ 2/3 × room floor area (ft²)** (8-ft ceiling; ≈ 5 ACH). Particle CADR says **nothing** about O3/NO2 removal. Gas-phase performance needs e.g. GB/T 18801 or AHAM AC-4 style tests (C).
- **O3 destruction catalysts:** MnO2 / MnO2-CuO (hopcalite-type) or Pd catalysts. Fresh, at design face velocity, single-pass removal is typically **>90 % (often >99 %)**. It declines with humidity and poisoning. Aircraft cabin ozone converters are designed at ≥ ~95 % (C: vendor/aviation data, not a standard). Activated carbon also destroys O3 (reactively, with finite life).
- **NO2 sorbents:** plain activated carbon adsorbs NO2 but partly reduces it to **NO**, which is then released. KMnO4-impregnated alumina, or carbon impregnated with KOH/K2CO3/KI/urea, captures NO2 better, and KMnO4 media oxidise NO → NO2 for capture. **NO is poorly adsorbed at room temperature**, so plan an oxidise-then-sorb stage (B/C).
- INFERRED sizing examples (30 m³ bedroom, λ = 0.45 h⁻¹):
  - O3, k_surf = 2.8 h⁻¹: holding the device-added O3 ≤ 20 µg/m³ (≈10 ppb) needs S ≤ 20 × 30 × 3.25 ≈ **2 mg/h**.
  - NO2, ignoring surface loss (conservative): ≤ 10 µg/m³ annual-equivalent needs S ≤ 10 × 30 × 0.45 ≈ **0.14 mg/h**.
  - A CARB-style chamber test would additionally cap the concentration at 50 ppb.

---

## 6. Noise and airborne ultrasound

### 6.1 Audible
- **WHO Guidelines for Community Noise (1999)** (A, verbatim via secondary): dwellings indoors **35 dB LAeq,16h** (speech intelligibility, moderate annoyance, day/evening). "Recommended guideline values inside bedrooms are **30 dB LAeq** for steady-state continuous noise and for a noise event **45 dB LAmax**" (single events, not more than ~10-15 per night). WHO 2018 Environmental Noise Guidelines give outdoor source-specific values, e.g. road Lden 53, Lnight 45 dB (A, secondary).
- Occupational (B): NIOSH REL 85 dBA 8-h TWA, 3 dB exchange, 140 dB peak. OSHA 29 CFR 1910.95 PEL 90 dBA / 5 dB exchange, action level 85 dBA, 140 dB peak (impulse). EU 2003/10/EC exposure limit 87 dB(A) / 140 dB(C) peak; action values 80/85 dB(A), 135/137 dB(C).
- INFERRED relevance: each breakdown makes a shock-wave "snap". At kHz repetition this is a **tonal** source at the pulse rate plus harmonics. Tonal noise is more annoying, so target well below 30-35 dB(A) at the listener, or push the repetition rate above ~20 kHz. Then the ultrasound limits below apply instead.

### 6.2 Airborne ultrasound (1/3-octave band SPL, dB re 20 µPa)
| Band centre (kHz) | 10 | 12.5 | 16 | 20 | 25 | 31.5 | 40 | 50 | 63-100 |
|---|---|---|---|---|---|---|---|---|---|
| ACGIH TLV ceiling (A) | 105 | 105 | 105 | 105 | 110 | 115 | 115 | 115 | 115 (B for 63-100) |
| ACGIH 8-h TWA (A) | 88 | 89 | 92 | 94 | - | - | - | - | - |
| ACGIH ceiling, no body coupling (A, Howard et al. via Leighton) | 105 | 105 | 105 | 105 | 140 | 145 | 145 | 145 | 145 (B) |
| INIRC-IRPA 1984 occupational (A) | - | - | - | 75 | 110 | 110 | 110 | 110 | 110 |
| **INIRC-IRPA 1984 general public (A)** | - | - | - | **70** | **100** | **100** | **100** | **100** | **100** |
| Health Canada 1991 (A) | - | - | 75 | 75 | 110 | 110 | 110 | 110 | 110 (B) |
| BS EN 61010-1:2010 equipment (A) | - | - | - | 110 (20-100 kHz, at operator and at 1 m) | | | | | |
- ACGIH footnotes (A, via AFOSH Std 48-20 Tab. 4): the limits "are designed to prevent possible hearing loss caused by the subharmonics ... rather than the ultrasonic sound itself". "Subjective annoyance and discomfort may occur in some individuals at levels between 75 and 105 dB for the frequencies from 10 kHz to 20 kHz especially if they are tonal". The +30 dB relaxation applies only where the ultrasound cannot couple into the body (water or contact). With direct contact, the air limits do not apply (B).
- IRPA public rationale (A, verbatim): "exposure of the general public ... at levels up to 110 dB is not known to cause untoward health effects ... an added safety factor should be incorporated ... Thus an SPL of 100 dB is recommended ... [20 kHz band] An SPL of 70 dB is recommended." Health Canada limits "are independent of time of exposure as subjective effects can occur immediately" (A).
- **> 100 kHz:** no airborne guideline found. The compendium (Leighton 2016, Proc. R. Soc. A 472:20150624) covers 8-100 kHz only and notes that guidelines rest on scant data and are **not validated for public/tonal exposure** (A).
- INFERRED for mid-air haptics (40 kHz arrays; focal SPL can exceed ~150 dB): keep the SPL at any head/ear position ≤ 100 dB in the 40 kHz band (IRPA public) and ≤ 70 dB in the 20 kHz band. Watch for audible subharmonics and AM-modulation sidebands (200 Hz haptic modulation is audible) against the 30-35 dB(A) room targets. Keep foci away from faces.

---

## 7. Flicker and photosensitive epilepsy (scanned volumetric display)
- **WCAG 2.x SC 2.3.1 (Level A)**, verbatim (A): "Web pages do not contain anything that flashes more than three times in any one second period, or the flash is below the general flash and red flash thresholds."
  Content is below threshold if "there are no more than three general flashes and / or no more than three red flashes within any one-second period; or the combined area of flashes occurring concurrently occupies no more than a total of **.006 steradians within any 10 degree visual field** ... (25% of any 10 degree visual field)".
  - "A general flash is defined as a pair of opposing changes in relative luminance of 10% or more of the maximum relative luminance (1.0) where the relative luminance of the darker image is below 0.80."
  - A saturated red transition has R/(R+G+B) ≥ 0.8 with a chromaticity difference > 0.2 (CIE 1976 UCS), per ISO 9241-391.
  - Exception: fine balanced patterns with elements < 0.1° per side.
- **ITU-R BT.1702** (as cited in WCAG Understanding, A): general flash = "a change in luminance of **20 cd/m²** or more where the darker image is below **160 cd/m²**"; HDR with darker state ≥ 160 cd/m²: Michelson contrast ≥ 1/17. BT.1702 / Ofcom limit flashes to ≤ 3 per second when the flashing area exceeds ~25 % of the screen (B).
- Physiology (B): photoparoxysmal responses occur for flashes roughly **3-60 Hz**, with peak sensitivity ~15-20 Hz. High-contrast striped patterns are also provocative (ISO 9241-391).
- **IEEE 1789-2015** (general lighting flicker, B via implementation): low-risk Mod% < 0.025·f (f < 90 Hz), < 0.08·f (90-1250 Hz), unrestricted > 1250 Hz. No observable effect: < 0.01·f (< 90 Hz), < 0.0333·f (90-3000 Hz), unrestricted > 3 kHz.
- INFERRED application:
  - Voxel refresh (frame) rates of 3-60 Hz make each voxel a flash source. Small sparse points subtending ≪ 0.006 sr within any 10° field pass the WCAG area test. Large filled shapes or full-scene blinking at 3-60 Hz can fail it.
  - Prefer frame rates ≥ 60-90 Hz with low modulation depth, avoid scene-wide luminance steps > 3/s, and avoid red saturated flashes.
  - Also check stroboscopic effects from kHz pulse trains if pulse energy varies.

---

## 8. Key open items (to resolve with purchased standards)
1. Sub-ns corneal/skin limits >1400 nm: IEC 2014 (peak-irradiance form, L9) vs ANSI 2022 (L10) differ by about 10³ at 100 fs. Also the 1050-1400 nm ultrashort retinal value (L3).
2. Exact IEC 2014 C5 algorithm branches (t ≤ T_i, N > 600, 5·N^-0.25).
3. ANSI eye aperture breakpoint (0.3 vs 0.35 s) and whether ANSI 2022 ocular >1400 nm equals its skin Table 9c.
4. EN 50689 consumer-laser restrictions; current editions of IEC TR 60825-3 / ANSI Z136.10; FDA show-variance separation-distance wording.
5. Health Canada / EU indoor values (G4-G6 "B" items) and IEC 60335-2-65 ozone clause.

## Sources
- ICNIRP (2013) Guidelines on limits of exposure to laser radiation 180 nm-1000 µm. Health Phys 105(3):271-295, doi:10.1097/HP.0b013e3182983fd4 (icnirp.org/cms/upload/publications/ICNIRPLaser180gdl_2013.pdf).
- Open-source transcriptions: github.com/CBORT-NCBIB/MPE-Calculator-Skin (`web/standards/icnirp_2013.json`, `web/standards/ansi_z136_2022.json`); github.com/llano1025/calEng (`src/calculators/elv/LaserSafetyShared.tsx`, IEC 60825-1:2014).
- IEC 60825-1:2014 (Ed. 3.0); ANSI Z136.1-2014 and -2022 (LIA). Seibersdorf Laboratories, "White Paper IEC 60825-1" and "Extended Source AEL Analysis of Scanned Laser Emission" (laser-led-lamp-safety.seibersdorf-laboratories.at). ResearchGate: "Comparison of corneal injury thresholds with laser safety limits" (ILSC 2019).
- ICNIRP (2004) UV guidelines, Health Phys 87(2):171-186 (ICNIRPUV2004.pdf); ACGIH TLVs & BEIs (UV, ozone, NO2, ultrasound).
- CARB, Regulation for Limiting Ozone Emissions from Indoor Air Cleaning Devices (ww2.arb.ca.gov/resources/documents/indoor-air-cleaning-devices-regulation); ANSI/UL 867 §37.
- WHO global air quality guidelines 2021 (ncbi.nlm.nih.gov/books/NBK574594/); US EPA NO2 NAAQS (epa.gov/naaqs/nitrogen-dioxide-no2-primary-air-quality-standards); NIOSH 1988 PEL project pages for ozone and NO2 (cdc.gov/niosh/chemicals/pel88/); NJDOH ozone fact sheet; OSHA method ID-190 (NO).
- Liu Y. et al. (2021) Observing ozone chemistry in an occupied residence, PNAS 118(6):e2018140118. Lee K. et al. (1999) JAWMA 49:1238-1244. Yao M., Zhao B. (2018) Build. Environ. 142:101-106. Weschler C.J. (2000) Indoor Air 10:269-288. US EPA Exposure Factors Handbook (2011) ch. 19.
- WHO (1999) Guidelines for Community Noise (Berglund, Lindvall, Schwela), iris.who.int/handle/10665/66217.
- AFOSH Std 48-20 (10 May 2013) Table 4 (ACGIH 2010 ultrasound TLV), text at github.com/thatpub/pubs. Leighton T.G. (2016) Proc. R. Soc. A 472:20150624, Table 1 & Appendix B (incl. INIRC-IRPA 1984, Health Canada 1991, BS EN 61010-1:2010 quotes).
- W3C WCAG 2.x SC 2.3.1 and "general flash and red flash thresholds" definition; Understanding 2.3.1 (github.com/w3c/wcag); ITU-R BT.1702; IEEE Std 1789-2015.
- US 21 CFR 1040.10, 1040.11, 1010.4, 801.415; FDA Laser Notice 56 (2019); 14 CFR 25.832; 29 CFR 1910.95, 1910.1000.

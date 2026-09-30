# R2 — Particle-based volumetric displays, acoustophoresis & mid-air haptics: hard numbers

Compiled 2026-09-30 for the "touchable mid-air volumetric projector" study.

**How this was sourced (read first).** In this session every WebFetch to the primary sites (nature.com, arxiv.org, PMC, pubs.aip.org,
ADS, BYU, the Hirayama site, Wikipedia) was **blocked by the network egress proxy**. All numbers therefore come from
**search-engine extracts of the cited pages**. The URL given is the page the extract came from. The web-search budget
(200 calls) ran out before topics 4b (gloves), 5 (measured attenuation) and 6 (DESY acousto-optics) were covered, so those
sections rely on a standard formula (COMPUTED) or are flagged UNVERIFIED.
Confidence key:
- **HIGH**: stated in an abstract, a datasheet or the paper's own text, as shown in the extract.
- **MED**: stated in a search extract of a primary or secondary page, but not checked against the full text.
- **LOW**: indirect, attribution unclear, or recalled from memory without being re-verified.
- **COMPUTED**: my own arithmetic from the sourced inputs or a standard formula.
- **ESTIMATE**: an engineering guess with no source.

---

## KEY NUMBERS

| Quantity | Value | Conditions | Source | Confidence |
|---|---|---|---|---|
| OTD trap laser wavelength | 405 nm ("near-invisible") | Smalley 2018 OTD, photophoretic trap | https://www.nature.com/articles/nature25176 ; https://pubs.aip.org/aip/rsi/article/92/10/103002/955132/Photophoretic-trap-testing-rig-for-volumetric | HIGH |
| OTD test-rig trap laser | 500 mW, 405 nm diode | BYU trap test rig (RSI 2021) | https://pubs.aip.org/aip/rsi/article/92/10/103002/955132/Photophoretic-trap-testing-rig-for-volumetric | MED |
| OTD minimum hold power | < 24 mW at 405 nm | BYU trap studies (RSI 2021 / SPIE 2023 wavelength study) | https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12443/124430D/Effects-of-photophoretic-trapping-under-varying-wavelengths-of-light/10.1117/12.2649439.full | LOW (unclear which paper it comes from) |
| OTD particle | Cellulose, ~10 µm | Nature 2018 | https://www.nature.com/articles/nature25176 ; https://www.nature.com/articles/s41598-021-86495-6 | HIGH |
| OTD image point size | < 10 µm ("ten-micrometre image points") | Nature 2018 abstract | https://www.nature.com/articles/nature25176 | HIGH |
| OTD colours | RGB laser illumination of the trapped particle | Nature 2018 | https://news.byu.edu/news/better-hologram-byu-study-produces-3d-images-float-thin-air | HIGH |
| OTD display volume | "typically 1 cm³" | Current OTD prototypes | https://par.nsf.gov/servlets/purl/10141807 (Rogers et al., Appl. Opt. 58, G363, 2019) | MED |
| OTD particles per image | 1 (single particle, POV) | Nature 2018 | https://www.nature.com/articles/nature25176 | HIGH |
| OTD trap max speed / accel. | 1.5 m/s; > 3 g | "Poisson" trap, preliminary BYU undergraduate result | http://jur.byu.edu/?p=22268 | MED |
| OTD refresh | > 10 frames/s POV lower bound; 12 frames/s used | Sci. Rep. 2021 | https://www.nature.com/articles/s41598-021-86495-6 | MED |
| OTD scaling target | 1 cm³ → 100 cm³ by moving many particles along simple paths | Bond et al., SPIE 12445 (2023) | https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12445/124450I/Diffractive-optics-for-scaling-photophoretic-trap-displays/10.1117/12.2655275.short | HIGH |
| Metallic "boat" trap | Au particles with radius ≥ 1 µm held > 1 h; > 100 µm coated microspheres; 532 nm CW laser scanned by AOMs | Phys. Rev. Applied 22, 064042 (2024) | https://journals.aps.org/prapplied/abstract/10.1103/PhysRevApplied.22.064042 | MED |
| MATD arrays | 2 opposed arrays of 16×16 transducers (= 512), 23.4 cm apart | Hirayama et al., Nature 575, 320 (2019) | https://www.nature.com/articles/s41586-019-1739-5 ; https://arxiv.org/pdf/2203.01987 | HIGH (the total of 512 is COMPUTED) |
| MATD frequency / update rate | 40 kHz; trap position and amplitude updated at 40 kHz | Nature 2019 | https://www.nature.com/articles/s41586-019-1739-5 | HIGH |
| MATD particle | Expanded polystyrene (EPS) bead, 1 mm radius | Nature 2019 | https://discovery.ucl.ac.uk/id/eprint/10110412/1/114630Q(1).pdf | HIGH |
| MATD max particle speed | 8.75 m/s vertical; 3.75 m/s horizontal | Nature 2019 abstract | https://www.nature.com/articles/s41586-019-1739-5 | HIGH |
| MATD working volume | 10 × 10 × 10 cm³ | Nature 2019 / SPIE 2020 | https://discovery.ucl.ac.uk/id/eprint/10110412/1/114630Q(1).pdf | HIGH |
| MATD POV frame time | ≤ 0.1 s (~10 Hz) | Nature 2019 | https://www.nature.com/articles/s41586-019-1739-5 | MED |
| Holographic acoustic tweezers | Up to 25 mm-sized particles moved independently; 2 × 256 emitters, 40 kHz | Marzo & Drinkwater, PNAS 116, 84 (2019) | https://www.pnas.org/doi/10.1073/pnas.1813047115 | HIGH |
| GS-PAT solver speed | 17,000 solutions/s for up to 32 points (GTX 1660) | ACM TOG 39(4) 2020 | https://discovery.ucl.ac.uk/id/eprint/10106840/ | HIGH |
| OpenMPD sync rate | 10 kHz sound-field rate | ACM TOG 2023 | https://dl.acm.org/doi/10.1145/3572896 | HIGH |
| Levitation around scattering objects | > 10,000 hologram updates/s | Hirayama et al., Sci. Adv. 8, eabn7614 (2022) | https://www.science.org/doi/10.1126/sciadv.abn7614 | HIGH |
| Multi-particle stability (AAC) | Failures cut from 21 % to 6 % over 100 paths | CHI 2026 | https://dl.acm.org/doi/10.1145/3772318.3791903 | HIGH |
| Ultraleap STRATOS Explore | 256 transducers (16×16, 10 mm, 40 kHz); update rate 40 kHz; range ≈ 70 cm; 242×207×34 mm; 24 VDC × 3.75 A max | Datasheet | https://www.mouser.com/datasheet/2/1031/Ultrleap_USX_129_USX_datasheet_STRATOS_Explore_Dev-2451107.pdf | HIGH |
| STRATOS maximum electrical power | 90 W | 24 V × 3.75 A | derived from the datasheet above | COMPUTED |
| Smallest haptic point | 8.6 mm diameter | Ultraleap | https://support.ultraleap.com/hc/en-us/articles/360004368558-What-is-the-resolution-of-Ultrahaptics | HIGH |
| STRATOS Inspire interaction zone | Ideal 63 × 48 × 48 cm; max 70 × 56 × 56 cm | Datasheet | https://www.mouser.com/datasheet/2/1031/Ultraleap_12182019_USI-1673864.pdf | HIGH |
| Focal SPL, measured | > 160 dB peak in the focal region | STRATOS 16×16 at 40 kHz, focus 20 cm; PTB scanner | http://pub.dega-akustik.de/ICA2019/data/articles/000085.pdf ; JASA 148, 1713 (2020) https://pubs.aip.org/asa/jasa/article/148/3/1713/916118/Experimental-characterization-of-high-intensity | HIGH |
| Focal pressure (patent) | 2585 Pa RMS ≈ 162.2 dB | 285-element 40 kHz array, focal length 200 mm | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9936324 | MED (dB value COMPUTED) |
| SPL needed for haptics | > 145 dB at the focus | Ultrasound haptics literature | https://pub.dega-akustik.de/ICA2019/data/articles/001374.pdf | MED |
| Detection threshold | 556.9 Pa (≈ 148.9 dB) for AM at 200 Hz; 334.1 Pa (≈ 144.5 dB) for STM line | Howard et al., cited in the source | https://arxiv.org/pdf/2405.02800 | MED (dB values COMPUTED) |
| Hoshi 2010 AUTD | 324 transducers, 40 kHz; 16 mN force; 20 mm focal spot | IEEE ToH 2010 | https://dl.acm.org/doi/10.1109/toh.2010.4 | MED |
| IRPA/INIRC 1984 occupational limits (8 h) | 75 dB at 20 kHz; 110 dB at 25 kHz; 115 dB at 31.5–100 kHz (1/3-octave bands) | Short exposures: +3 dB (2–4 h), +6 dB (1–2 h), +9 dB (< 1 h) | https://www.icnirp.org/cms/upload/publications/INIRCUltrasound.PDF ; https://journals.lww.com/health-physics/fulltext/2024/08000/validity_of_the_1984_interim_guidelines_on.7.aspx | MED-HIGH |
| IRPA 1984 general-public limits | −5 dB at 20 kHz, −10 dB above, never > 100 dB → about 70 / 100 / 100 dB | Continuous exposure | same as above | MED (band values COMPUTED) |
| Health Canada (Safety Code 24, 1991) | 75 dB at 20 kHz; 110 dB at ≥ 25 kHz | Occupational | https://www.canada.ca/content/dam/hc-sc/documents/services/environmental-workplace-health/reports-publications/radiation/safety-code_24-securite-eng.pdf | MED-HIGH |
| ACGIH TLV (ceiling) | 110 dB at 25 kHz; 115 dB at 31.5–100 kHz; +30 dB allowed if the sound cannot couple into the body (→ 140/145 dB) | In air | https://www.icben.ethz.ch/2008/PDFs/Lenhardt.pdf ; https://laerm.ch/wp-content/uploads/Review_Ultrasound_Exposure_Limits.pdf | MED |
| Human hearing test, 40 kHz | 100–120 dB SPL for 5 min: no significant PTA threshold shift (5 dB criterion, power > 80 %) | ICA 2019 | https://pub.dega-akustik.de/ICA2019/data/articles/001374.pdf | HIGH |
| Cognition test, 40 kHz | 120 dB SPL: no cognitive effect (Ultraleap-funded) | Di Battista et al., Appl. Acoust. 2022 | https://www.sciencedirect.com/science/article/pii/S0003682X2200425X | HIGH |
| Fairy Lights lasers | 30–100 fs, ≤ 1 kHz, ≤ 7 mJ/pulse → 4,000 dots/s; 269 fs, 1045 nm, 200 kHz, ≤ 50 µJ → 200,000 dots/s | Ochiai et al., ACM TOG 35(2) 2016 | https://arxiv.org/pdf/1506.06668 ; https://dl.acm.org/doi/10.1145/2850414 | HIGH |
| Plasma ignition | Plasma from 0.2 mJ (30 fs); peak 36 PW/cm² against a > 1 PW/cm² threshold | Fairy Lights | https://arxiv.org/pdf/1506.06668 | HIGH |
| Plasma skin-proxy damage | At 1 W: < 2 s gives 100 µm holes only; > 2 s adds heat damage (cow leather) | Fairy Lights | https://arxiv.org/pdf/1506.06668 | MED |
| Laser-plasma tactile threshold | 50 % detection at 0.03–0.04 W; > 90 % at 0.16 W | Laser-plasma haptics study | https://ncbi.nlm.nih.gov/pmc/articles/PMC8517193 | LOW-MED (attribution unclear) |
| Air absorption at 20 °C, 50 % RH, 1 atm | 40 kHz 1.32; 100 kHz 3.28; 200 kHz 8.23; 500 kHz 41.8; 1 MHz 162 dB/m | ISO 9613-1 formula, small-signal | https://www.iso.org/standard/17426.html | COMPUTED |
| Speed of sound at 20 °C | 343.2 m/s (λ = 8.58 mm at 40 kHz) | Dry-air approximation | standard formula | COMPUTED |
| DESY air acousto-optic modulator | ~20 GW peak-power pulses deflected; > 50 % efficiency | Schrödel/Heyl et al., Nat. Photonics 2024 | https://doi.org/10.1038/s41566-023-01304-y | LOW (recalled, could not verify in this session) |

---

## 1. Optical Trap Display (OTD), photophoretic volumetric displays

**Core paper.** Smalley, Nygaard et al., "A photophoretic-trap volumetric display", *Nature* 553, 486–490 (25 Jan 2018).
https://www.nature.com/articles/nature25176

How it works:
- Aberrations in a lens system (spherical plus astigmatic) create a photophoretic trap that holds one opaque **cellulose** particle.
- The trap is scanned through the volume while RGB lasers light the particle. Persistence of vision turns its path into an image.
- The images can be seen from every angle, including geometries that holograms and light fields cannot produce.
- Image points are about 10 µm. The trap light is 405 nm and "near-invisible".
- Demonstrated images include a butterfly, a prism, the BYU logo, rings around an arm, and a person in a lab coat.
  Source: https://news.byu.edu/news/better-hologram-byu-study-produces-3d-images-float-thin-air

Numbers found:
- Test-rig trap laser: 500 mW, 405 nm diode. Minimum hold power: < 24 mW at 405 nm (attribution LOW).
- Display volume: "typically 1 cm³" (Rogers, Laney, Peatross, Smalley, "Improving photophoretic trap volumetric displays", *Appl. Opt.* 58, G363, 2019; https://opg.optica.org/ao/abstract.cfm?uri=ao-58-34-G363).
- "Poisson-spot" trap: stays stable above 3 g, with a top speed of 1.5 m/s (preliminary; http://jur.byu.edu/?p=22268).
- Frame rate: > 10 frames/s is treated as the POV lower bound, and 12 frames/s was used (Sci. Rep. 2021).

Not retrieved: the exact trap power and speed in the Nature 2018 paper itself, the RGB laser powers, and the drawing time per image (see Gaps).

**Follow-ups, 2019–2026**
| Year | Work | Key content | Source |
|---|---|---|---|
| 2019 | Rogers et al., Appl. Opt. 58 G363 (invited) | Roadmap to improve OTD; 1 cm³ volumes | https://par.nsf.gov/servlets/purl/10141807 |
| 2020 | Compact OTD using a focus-tunable lens (OSA 3D) | Compact scanning | https://opg.optica.org/abstract.cfm?uri=3D-2020-JTh2A.34 |
| 2021 | Rogers & Smalley, "Simulating virtual images in optical trap displays", Sci. Rep. 11 | Moving-perspective backdrop plus motion parallax makes the display look larger or deeper than the physical volume; "theoretically an infinite size display" | https://www.nature.com/articles/s41598-021-86495-6 |
| 2021 | Barton et al., RSI 92, 103002 | Automated trap test rig: < 1 % average standard error, > 98 % accuracy | https://pubs.aip.org/aip/rsi/article/92/10/103002/955132/Photophoretic-trap-testing-rig-for-volumetric |
| ~2021–22 | JoVE 63113: miniature automatic photophoretic trapping rigs | Rig fabrication | https://www.jove.com/t/63113/fabrication-testing-miniature-automatic-photophoretic-trapping |
| 2023 | Bond, Kuttler, Hales, Smalley, SPIE 12445 | Diffractive optics to trap **many particles on simple paths**, scaling 1 → 100 cm³ | https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12445/124450I/Diffractive-optics-for-scaling-photophoretic-trap-displays/10.1117/12.2655275.short |
| 2023 | SPIE 12443, trapping vs wavelength | Wavelength dependence | https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12443/124430D/Effects-of-photophoretic-trapping-under-varying-wavelengths-of-light/10.1117/12.2649439.full |
| 2024 | "Optical trapping of large metallic particles in air", PR Applied 22, 064042; JoVE 2025 protocol | Horizontal "boat" trap, 532 nm CW, AOM-scanned sidewalls; Au radius ≥ 1 µm held > 1 h; > 100 µm coated spheres | https://journals.aps.org/prapplied/abstract/10.1103/PhysRevApplied.22.064042 ; https://doi.org/10.3791/68766 |
| 2024 | ACS Photonics 11: ultrastable 3D photophoretic traps via a single multimode fibre | Stronger forces, suited to larger volumes | cited in the 2026 review below |
| 2025 | Photonics Research 13: dynamic holographic optical bottles, selective manipulation and merging of multiple absorbing particles | Multi-particle control | cited in the 2026 review below |
| 2025 | BYU tech transfer (ID 2022-026): "frozen waves"/Bessel light-tube traps + SLM | Faster refresh by avoiding the SLM speed limit; multiple particles quoted as 10×, 100× or 1000× in size or image complexity (aspirational) | https://techtransfer.byu.edu/technologies-section-new/optical-trap-display-and-printing-technology |
| 2026 | Pahi et al., "Photophoretic trapping: fundamentals, advances and future directions", ChemPhysChem (arXiv 2512.09401) | Outlook: parallel SLM traps, AOD/EOD scanning, engineered particles | https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/cphc.202500890 |

Related laser-only volumetric displays:
- Kumagai, Numazawa, Hayasaki, "Volumetric cloud display", *Optica* 12, 1139 (2025). A femtosecond laser triggers condensation in ethanol-supersaturated vapour and RGB lasers light the cloud. https://ui.adsabs.harvard.edu/abs/2025Optic..12.1139K/abstract
- Kumagai et al., "Fist-sized aerial volumetric display with femtosecond laser drawing", JSID 2025. https://sid.onlinelibrary.wiley.com/doi/10.1002/jsid.2025

**Design arithmetic (ESTIMATE).**
- At 1.5 m/s and 10 fps, one particle draws at most **15 cm of line per frame**.
- At 10 µm point pitch that is ≤ 1.5 × 10⁴ distinct points per frame per particle.
- A filled 10 cm × 10 cm surface at 1 mm pitch needs 10⁴ points. That takes roughly 10–100 particles running in parallel once real trap blur and path overhead are included.
- Conclusion: **multi-particle trapping is the gating technology for OTD.**

## 2. Acoustophoretic displays (MATD and successors)

**Core paper.** Hirayama, Martinez Plasencia, Masuda, Subramanian, "A volumetric display for visual, tactile and audio presentation using acoustic trapping", *Nature* 575, 320–323 (2019).
https://www.nature.com/articles/s41586-019-1739-5 (open copy: https://sussex.figshare.com/articles/journal_contribution/A_volumetric_display_for_visual_tactile_and_audio_presentation_using_acoustic_trapping/23472326)

Hardware:
- Two opposed 16×16 arrays at 40 kHz (512 transducers, 10 mm), 23.4 cm apart.
  Note: some search summaries wrongly say "256 total".
- Driven by an FPGA using square-wave phase and duty-cycle control.
- Trap position and amplitude update at 40 kHz, inside a **10 × 10 × 10 cm³** volume.

Particle and image:
- Particle: EPS bead, 1 mm radius, lit by synchronised RGB LEDs.
- Speed: **8.75 m/s vertical, 3.75 m/s horizontal**.
- POV frame ≤ 0.1 s. Example content: a multicolour (3:2) torus knot.

Multimodal output:
- Touch: a secondary focusing trap, time-multiplexed with the levitation trap.
- Sound: amplitude modulation, demodulated in mid-air.
- Phase minimisation keeps levitation, touch and sound working together.
- Sources: https://discovery.ucl.ac.uk/id/eprint/10110412/1/114630Q(1).pdf (SPIE 2020 companion paper) and the Nature abstract.

Not retrieved: peak accelerations (g), and the tactile or audio SPL values from the MATD paper (see Gaps).

**Successors**
| Work | Numbers / claim | Source |
|---|---|---|
| Marzo & Drinkwater, "Holographic acoustic tweezers", PNAS 116:84 (2019) | 2 × 256-emitter arrays; **up to 25** mm-sized particles moved independently | https://www.pnas.org/doi/10.1073/pnas.1813047115 |
| GS-PAT (Plasencia, Hirayama, Montano-Murillo, Subramanian; ACM TOG 39(4) 2020) | **17 k solutions/s, ≤ 32 points**, GTX 1660; earlier solvers managed ~hundreds/s | https://discovery.ucl.ac.uk/id/eprint/10106840/ |
| Hirayama et al., Sci. Adv. 8 eabn7614 (2022) | > 10,000 updates/s while modelling scattering objects; displays above and below obstacles | https://www.science.org/doi/10.1126/sciadv.abn7614 |
| OptiTrap (Paneva et al., ACM TOG 41(5) 2022) | Optimal-control trap paths: larger, faster, more accurate POV shapes than before | https://dl.acm.org/doi/10.1145/3517746 |
| Content rendering via optimal path following (UCL) | Continuation of OptiTrap | https://discovery.ucl.ac.uk/id/eprint/10179179/ |
| OpenMPD (ACM TOG 2023) | Presentation engine synchronised at **10 kHz**; Unity integration | https://dl.acm.org/doi/10.1145/3572896 |
| JOLED (UIST 2016) | Levitated Janus voxels rotated electrostatically | https://dl.acm.org/doi/10.1145/2984511.2984549 |
| LeviProps (UIST 2019) | Levitated fabric props held by holographic tweezers | https://dl.acm.org/doi/10.1145/3332165.3347882 |
| ArticuLev (CHI 2021) | Self-assembly of articulated multi-bead primitives | https://discovery.ucl.ac.uk/id/eprint/10123790/ |
| LeviPrint (SIGGRAPH 2022) | Traps elongated sticks in both position and orientation; robot-arm assembly | https://dl.acm.org/doi/10.1145/3528233.3530752 |
| TipTrap (UIST 2022) | Uses sound scattered off the fingertip to build a trap: direct touch-and-drag of levitated content | https://dl.acm.org/doi/abs/10.1145/3526113.3545675 |
| DataLev (CHI 2023) | Mid-air data physicalisation | https://dl.acm.org/doi/10.1145/3544548.3581016 |
| StableLev (CHI 2024) | AutoEncoder/LSTM instability detection; > 180,000 simulated data points (Naive + GS-PAT) | https://dl.acm.org/doi/10.1145/3613904.3642286 |
| Temporal acoustic point holography (SIGGRAPH 2024) | Temporal multi-point holography | https://dl.acm.org/doi/10.1145/3641519.3657443 |
| Single-sided levitation in zero-order Bessel beams (PRL, arXiv 2412.15539) | Stable one-sided levitation **in pressure maxima** | https://arxiv.org/pdf/2412.15539 |
| AcoustoBots (swarm robots carrying PATs) | Mobile acoustophoretic multimodality | https://pmc.ncbi.nlm.nih.gov/articles/PMC12133503 |
| AcoustoReinforce (AAAI 2026) | Deep RL for multi-particle paths | https://ojs.aaai.org/index.php/AAAI/article/view/40217 |
| AAC (CHI 2026) | Actor-critic planning plus repair; failures **21 % → 6 %** over 100 paths | https://dl.acm.org/doi/10.1145/3772318.3791903 |
| Acta Acustica 2026 dual-array tweezers | Real-time phase control of 128 transducers at 40 kHz | https://doi.org/10.1051/aacus/2026006 |

**Particle count.** The highest independently-controlled count found in this session is **25** (PNAS 2019). I did not find a verified
2023–2026 record above that. More recent work targets *stability* of a few to tens of particles instead of raw count (StableLev, AAC).

**Design arithmetic (ESTIMATE).**
- 8.75 m/s × 0.1 s = 0.875 m of path per POV frame at most. Real shapes are far smaller because of acceleration and trap-stiffness limits.
- A 40 kHz field has λ = 8.6 mm, so the trap pitch and the minimum spacing between particles are about mm-scale.
  A dense "Iron-Man" image would need either many particles or a much higher carrier frequency.
  Higher frequency, however, increases air absorption (§5).

## 3. Mid-air ultrasound haptics: specifications, perception and SAFETY

**Ultraleap STRATOS Explore** (datasheet https://www.mouser.com/datasheet/2/1031/Ultrleap_USX_129_USX_datasheet_STRATOS_Explore_Dev-2451107.pdf):
- 256 transducers (16×16, 40 kHz; UHEV1 uses 10 mm transducers).
- Update rate 40 kHz; maximum range ≈ 70 cm.
- 242 × 207 × 34 mm; 24 VDC ±10 %, 3.75 A max (≈ 90 W, COMPUTED); operates 0–40 °C.
- Minimum point diameter 8.6 mm (https://support.ultraleap.com/hc/en-us/articles/360004368558-What-is-the-resolution-of-Ultrahaptics).

**STRATOS Inspire** (https://www.mouser.com/datasheet/2/1031/Ultraleap_12182019_USI-1673864.pdf): ideal zone 63 × 48 × 48 cm, maximum 70 × 56 × 56 cm.

**Other arrays:**
- AUTD3 (Shinoda–Makino, IEEE ToH 2021): 249 transducers per module at 40 kHz, tiled over EtherCAT, open source.
  https://dl.acm.org/doi/10.1109/TOH.2021.3069976 ; https://github.com/shinolab/autd3
- Hoshi et al. 2010: 324 transducers, 16 mN DC force, 20 mm focus. https://dl.acm.org/doi/10.1109/toh.2010.4

**Focal pressure.**
- Liebler, Kling, Gerlach, Koch measured a STRATOS (16×16 MA40S4S, focus 20 cm) with the PTB scanner. Nonlinear propagation produced **> 160 dB peak SPL** in the focal region.
  Measuring it properly needs microphones with a high linearity ceiling and wide bandwidth for the harmonics.
  http://pub.dega-akustik.de/ICA2019/data/articles/000085.pdf ; https://pubs.aip.org/asa/jasa/article/148/3/1713/916118/Experimental-characterization-of-high-intensity
- A patent reports 2585 Pa RMS at 200 mm from a 285-element array, which is 162.2 dB (COMPUTED).
- Perceptible haptics generally needs **> 145 dB** (https://pub.dega-akustik.de/ICA2019/data/articles/001374.pdf).
- Conversion (COMPUTED): 155 dB = 1.12 kPa RMS; 160 dB = 2.0 kPa RMS.

**Perception thresholds.**
- AM at 200 Hz: 556.9 Pa. STM line: 334.1 Pa (Howard et al., quoted in https://arxiv.org/pdf/2405.02800).
- Lateral modulation lowers the detection threshold by roughly 10 dB compared with AM, over 10–200 Hz modulation
  (https://link.springer.com/content/pdf/10.1007/978-3-031-04043-6_9.pdf, MED).
- Skin heating is reported above ~4.0 kPa focal pressure (MED-LOW; thermal work, e.g. https://arxiv.org/pdf/2002.02635).
- Modulation at ~200 Hz also produces audible 200 Hz sound (demodulation).

**Exposure guidelines** (1/3-octave band SPL, dB re 20 µPa)
| Band centre | IRPA/INIRC 1984, occupational 8 h | IRPA 1984, public (COMPUTED from rule) | Health Canada 1991 | ACGIH TLV ceiling (in air) | ACGIH, no coupling (+30 dB) |
|---|---|---|---|---|---|
| 20 kHz | 75 | 70 | 75 | — (audible-range TLVs apply) | — |
| 25 kHz | 110 | 100 | 110 | 110 | 140 |
| 31.5–100 kHz (40 kHz band) | 115 | 100 (cap) | 110 | 115 | 145 |

Sources:
- INIRC 1984: https://www.icnirp.org/cms/upload/publications/INIRCUltrasound.PDF
- ICNIRP 2024 statement (Health Phys. 127(2):326–347): https://www.icnirp.org/cms/upload/publications/ICNIRPUltrasoundStatement2024.pdf
- Health Canada Safety Code 24: https://www.canada.ca/content/dam/hc-sc/documents/services/environmental-workplace-health/reports-publications/radiation/safety-code_24-securite-eng.pdf
- ACGIH, as summarised by Lenhardt 2008: https://www.icben.ethz.ch/2008/PDFs/Lenhardt.pdf
- Review of airborne ultrasound limits (Acoustics 2005): https://laerm.ch/wp-content/uploads/Review_Ultrasound_Exposure_Limits.pdf

Notes on the table:
- IRPA short-exposure allowances: +3 dB (2–4 h/day), +6 dB (1–2 h), +9 dB (< 1 h).
- Health Canada bases its limits on Acton & Carson, who found no temporary threshold shift up to 110 dB in the 20 and 25 kHz bands.
- The +30 dB OSHA/ACGIH relaxation (→ 145 dB) is contested (Leighton, Proc. R. Soc. A 2016: https://royalsocietypublishing.org/rspa/article/472/2185/20150624/57686/Are-some-people-suffering-as-a-result-of).
- **ICNIRP 2024:** the endpoints are relevant, but the 1984 limits rest on limited evidence and "could be too low or too high". ICNIRP says it cannot revise them until data gaps are closed.
- Japan and ISO values were not retrieved (see Gaps).

**Human-exposure studies for haptics.**
- Hearing (ICA 2019): 40 kHz at 100–120 dB SPL for 5 min caused no significant PTA change, with > 80 % power at a 5 dB criterion (https://pub.dega-akustik.de/ICA2019/data/articles/001374.pdf).
- Cognition (Di Battista et al., Appl. Acoust. 2022; Ultraleap-funded; Bristol): 120 dB at 40 kHz had no effect (https://www.sciencedirect.com/science/article/pii/S0003682X2200425X).
- Literature summary in those sources: no known effects below ~110 dB; temporary threshold shifts associated with > 145 dB.
- Ultraleap HDK guidance (https://leap2.ultraleap.com/hdk-rec192/info/):
  - do not aim at ears or eyes, and keep the head out of the space above the array;
  - keep about 30 cm between the head and the feedback zone;
  - continuous feedback can temporarily reduce sensitivity, so take a 10–15 min break.
- **No Ultraleap safety white paper with numeric limits was found** in this session.

**Hearing risk at 155 dB focal SPL (analysis; the dB differences are COMPUTED).**
- 155 dB is 40 dB above the IRPA occupational 40 kHz limit (115 dB) and 55 dB above the public cap (100 dB). It also exceeds the relaxed ACGIH "no-coupling" ceiling (145 dB) by 10 dB.
- These limits apply to the SPL *at the ear*. The focus is small (≥ 8.6 mm) and SPL falls off quickly away from it; air absorption adds ~1.3 dB/m at 40 kHz, which is minor.
- Tested human exposures so far only reach **120 dB, 5 min**. There are **no published human data at 145–160 dB** at the ear.
- Design rule (ESTIMATE):
  - never let a focus, grating lobe or reflection land on the head;
  - hold ear-position SPL ≤ 110–115 dB (occupational) or ≤ 100 dB (public);
  - verify with wideband microphones that capture harmonics and subharmonics (per PTB).

## 4. Plasma/laser haptics and glove haptics

**Fairy Lights in Femtoseconds** (Ochiai, Kumagai, Hoshi, Rekimoto, Hasegawa, Hayasaki; SIGGRAPH 2015 / ACM TOG 35(2) 2016):
https://arxiv.org/pdf/1506.06668 ; https://dl.acm.org/doi/10.1145/2850414

Lasers and rendering:
- Laser A: 30–100 fs, ≤ 1 kHz, ≤ 7 mJ/pulse → 4,000 dots/s.
- Laser B: 269 fs, 1045 nm, 200 kHz, ≤ 50 µJ/pulse → **200,000 dots/s**.
- Air plasma forms from 0.2 mJ (30 fs). Peak intensity is 36 PW/cm², against an ionisation threshold > 1 PW/cm².
- Voxels are addressed with an SLM hologram.

Touch and safety:
- Touching a voxel gives a shock-wave "impulse"; the paper demonstrates a haptic floating button.
- Cow leather at 1 W, 50–6000 ms exposures: under 2 s only ~100 µm holes; beyond 2 s, heat damage.
  So touch interactions must stay **≪ 2 s per spot**.

**Laser-induced tactile sensations**
- Thermoelastic haptics: "Laser-induced thermoelastic effects can evoke tactile sensations", Sci. Rep. 5:11016 (2015), https://www.nature.com/articles/srep11016.
  Low-power, guideline-compliant irradiation raised skin temperature by < ~2.5 °C, i.e. no heat pain (MED).
- Laser plasma near the skin: "Mid-Air Tactile Sensations Evoked by Laser-Induced Plasma" (Frontiers, 2021), https://ncbi.nlm.nih.gov/pmc/articles/PMC8517193.
  50 % detection at 0.03–0.04 W; > 90 % at 0.16 W (LOW-MED; the extract did not show which paper this came from).

Pulse energy, wavelength and latency for these two papers were not retrieved.

**Simple haptic gloves (vibrotactile / electrotactile).** The search budget ran out before this topic.
Only ESTIMATES from general engineering knowledge, all unsourced:
| Actuator | Latency | Cost |
|---|---|---|
| ERM motors | ~20–50 ms to spin up | cheap, < US$1 each |
| LRAs | ~5–20 ms | — |
| Piezo actuators | < 1–5 ms | — |
| Electrotactile electrodes | < 1 ms electrical (with sensation variability and comfort issues) | — |
| Consumer vibrotactile gloves | — | ~US$10²–10³ |
| Microfluidic / force-feedback research gloves | — | ~US$10⁴+ |

## 5. Acoustic attenuation in air vs frequency, and speed of sound

Small-signal atmospheric absorption from the **ISO 9613-1:1993** formula:
- Conditions: T = 20 °C, RH = 50 %, p = 101.325 kPa, giving h = 1.153 % molar water vapour.
- Relaxation frequencies: O₂ 35.4 kHz, N₂ 332 Hz.
- Standard reference: https://www.iso.org/standard/17426.html (COMPUTED here; the page was not fetched).

| f | α (dB/m) | Classical part only (dB/m) | Loss over 10 cm | Loss over 30 cm | λ (mm) |
|---|---|---|---|---|---|
| 20 kHz | 0.52 | 0.06 | 0.05 dB | 0.16 dB | 17.2 |
| 40 kHz | **1.32** | 0.26 | 0.13 dB | 0.40 dB | 8.58 |
| 100 kHz | **3.28** | 1.60 | 0.33 dB | 0.98 dB | 3.43 |
| 200 kHz | **8.23** | 6.39 | 0.82 dB | 2.47 dB | 1.72 |
| 500 kHz | **41.8** | 40.0 | 4.2 dB | 12.6 dB | 0.69 |
| 1 MHz | **162** | 160 | 16.2 dB | 48.5 dB | 0.34 |

Caveats:
- ISO 9613-1 was built for audio-range noise. Extending it to ultrasound is standard practice, but I could not verify its stated accuracy band in this session.
- Above ~200 kHz, classical (viscous and thermal) absorption dominates, rising as f², so humidity matters little.
- At focal SPL ≥ 150 dB, **nonlinear losses** (harmonic generation and shock formation) add extra loss not captured above. This is consistent with the harmonics PTB measured.
- A measured 300 kHz high-intensity beam characterisation also exists: https://pubs.aip.org/asa/jasa/article-abstract/153/5/2878/2890440/Characterization-of-high-intensity-progressive (JASA 153, 2878) (numbers not retrieved).

Speed of sound (COMPUTED from the ideal-gas approximation):
- Dry air at 20 °C: **343.2 m/s** (331.3·√(1+T/273.15)).
- 50 % RH adds only about +0.3–0.4 m/s (ESTIMATE).

**Implications for the design (ESTIMATE).**
- 40 kHz gives ~9 mm resolution with negligible loss out to 1 m.
- 200 kHz gives ~2 mm resolution but costs ~8 dB/m.
- 1 MHz (0.34 mm) loses about 16 dB per 10 cm, so it only works at cm-scale standoff.
- Doubling frequency roughly halves the focal spot but greatly increases path loss.

## 6. Acousto-optics in ambient air (DESY / Heyl group)

- Paper, from recall and not verified in this session: Y. Schrödel, …, M. Kupnik, C. M. Heyl, "Acousto-optic modulation of gigawatt-scale laser pulses in ambient air", *Nature Photonics* 18, 54–59 (2024; online 2023). https://doi.org/10.1038/s41566-023-01304-y
- Recalled headline claims (LOW confidence; verify before use):
  - an ultrasound-generated density grating in ambient air deflects ultrashort pulses of ~20 GW peak power;
  - efficiency is > 50 %;
  - beam quality is preserved;
  - the ultrasound source was built by TU Darmstadt (Kupnik).
- **Not retrieved:** acoustic frequency, SPL, interaction length, diffraction angle.
  Physics check (COMPUTED): with Λ = c/f, the Bragg angle θ_B ≈ λ_opt/(2Λ). For λ = 1.03 µm and f = 0.5 MHz (Λ ≈ 0.69 mm), θ_B ≈ 0.75 mrad. That is sub-mrad deflection unless f is raised, and absorption rises as f² (§5).

---

## Gaps / unknowns
1. **Access:** every WebFetch was egress-blocked, and the web-search budget (200) was used up. Nothing here was checked against a full-text PDF. Priority re-checks, once access is available:
   - Nature 2018 OTD Methods: trap laser power, RGB powers, measured particle speed and acceleration, drawing time per image, image dimensions in mm.
   - Nature 2019 MATD Methods: peak accelerations (g), tactile focal pressure (Pa or dB), audio SPL, duty-cycle split between levitation, touch and sound.
2. **OTD multi-particle:** no peer-reviewed demonstration was found showing N > 1 particles *drawing an image* with numbers. The 2023 SPIE work is preliminary, and the 2025 Photonics Research optical-bottle paper shows manipulation only.
3. **Acoustophoretic particle count:** the latest verified independent-control maximum is 25 (2019). A 2023–2026 record, if it exists, was not found.
4. **Largest levitation arrays and levitation at a distance:** no numbers retrieved beyond single-sided Bessel-beam levitation.
5. **Japanese airborne-ultrasound guideline (Japan Industrial Safety Assoc., 1971)** and any **ISO/IEC** exposure standard: values not retrieved. I believe no ISO exposure-limit standard for airborne ultrasound exists; the German VDI 3766 applies to workplaces. Both points are unverified.
6. **Ultraleap safety white paper** with numeric compliance data: not found. Its HDK guidance is qualitative.
7. **Human data at 145–162 dB at the ear:** none found. The highest tested exposure is 120 dB for 5 min.
8. **Laser haptics:** pulse energy, wavelength, latency and cost for the thermoelastic and plasma haptics papers were not retrieved.
9. **Gloves:** latency and cost figures are ESTIMATES only.
10. **Measured (non-ISO) air absorption at 100 kHz–1 MHz** and **DESY acousto-optic parameters** (frequency, SPL, angle, efficiency): unverified.

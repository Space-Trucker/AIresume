# Idea round 1: independent answer (Sonnet)

Conventions: L = luminance, eps = lm per absorbed W, E = spark energy, P = absorbed optical power, `[?]` = uncertain by x3-10. All numbers are hand estimates from memory; no web. Beam-type hazards (class-4 beams crossing the room; eye-safe 1.5-2 um and tracked shut-off needed, MPE ~0.1 W/cm2 CW) apply to every scanned-beam idea below and were not in the brief.

## 0. Premise checks (where I agree and where I don't)

- **P1 Gap arithmetic: agree.** The eye's PSF (~1 arcmin = 0.5 mm at 1.7 m), not the drawn width, sets stroke luminance. 100 cd/m2 x 0.5 mm = 0.05 cd/m, and 4pi x 0.05 = 0.63 lm per metre of stroke. 10-100 m of strokes gives 6-60 lm. Cyan tax: V(490 nm) = 0.21, so a cyan lumen costs 4.6x the radiant watts of a 555 nm lumen.
- **P2 Rayleigh: agree.** beta(532) ~1.2e-5 /m. A 1 W beam gives dI/dl = P*beta*683*V/4pi = 5.6e-4 cd/m, about 1 cd/m2 at 0.5 mm apparent width. 100 cd/m2 needs ~90 W of circulating power. Lab's 200 W is right.
- **P3 Challenge: eps ~1 lm/W looks like a mJ-spark number, not a 20 uJ voxel number.** Radiated fraction = (optically thin emission ~R^3 x cooling time) / (enthalpy ~R^3), so it scales with t_cool, i.e. ~R (hydro) to ~R^2 (conduction). That gives eps ~ E^(1/3 to 2/3). A 20 uJ spark (R ~0.15 mm; what 10^4-10^5 dots/frame forces) then gives eps ~0.03-0.3 lm/W `[?]`. A direct estimate for a 100 um, 10 kK ball gives ~0.01. The dense-dot plasma gap is therefore 3-30x worse than stated: 6 lm costs 20-200 W, not 6 W. This is the first thing to measure.
- **P4 NO yield 1e17/J: agree.** It equals the classic arc energy cost (~2.8 MJ/mol = 2e17/J). The best plasma N-fixation reactors reach 0.3-0.7 MJ/mol, which is ~1e18/J and the wrong direction. Thermal sparks cannot make less NO per joule.
- **P5 The binding constraint is NOISE, not NO.**
  - Acoustic power is ~0.6 P. For P = 30 W: 18 W, i.e. 121 dB SPL at 1 m broadband.
  - A fast-heating monopole has p(w) ~ w*dV, so its energy spectrum rises as f^2 up to f_c = c/(2piR). The audible fraction is ~(15 kHz/f_c)^3.
  - R = 0.7 mm (1 mJ): f_c = 78 kHz, fraction 7e-3 (-21 dB). R = 0.15 mm (20 uJ): f_c = 360 kHz, fraction 7e-5 (-41 dB).
  - So audible noise per lumen ~ E/eps ~ E^(1/3 to 2/3): small sparks are quieter per lumen, but make more NO per lumen.
  - At E = 20 uJ, eps = 0.1: about 66 dB(A) at 2 m **per lumen**, +10 dB per decade of lumens. 40 dB(A) means ~3 mlm total. The target (6-60 lm) is 3.5-4.5 decades above that. Ideas A/C below buy at most 15-20 dB. Air plasma cannot meet 35-40 dB(A) at the target brightness.
- **P6 Theorem and lemma: agree, with two additions.**
  - (i) Refraction cannot change the radiance of a uniform diffuse field (etendue). Passive index or phase "holograms" are invisible in room light, which closes that loophole for good.
  - (ii) The touch lemma is a single-sided-emitter statement (see E2).

## A. More lumens per joule, per NO, per shock

**A1 Stipple: sparse bright dots + perceptual completion.**
(a) Draw strokes as dots spaced 3-5x the eye blur (2-3 mm at 1.7 m) and rely on contour integration (Field/Hayes association field), visible persistence (30-100 ms) and the sparkler effect. Bloch's law means one flash per 40 ms frame counts fully. Use fewer, bigger sparks.
(b) Lumens needed drop 3-5x for equal salience `[?]`. eps rises 2-4x (5x larger E). Net absorbed power falls 8-20x: ~6-lm-equivalent at 2-10 W instead of 20-200 W. NO per lumen falls with eps.
(c) Does not touch the noise wall (~75 dB(A) at 2 m for the 6-lm case). Dotted look, not solid strokes.

**A2 Isobaric (slow-ramp) heating to suppress the shock.**
(a) The shock exists because deposition is faster than R/c (0.15-1.5 us). Heating over tau >> R/c is quasi-isobaric, so the energy goes to enthalpy and radiation. The linear monopole estimate is E_ac/E ~ 2.6e-10 * E/tau^3 (SI): 20 uJ over 100 us gives 0.5 %; over 10 us the nonlinear regime gives >=50 %.
(b) Shock fraction 60 % -> ~1 % (-18 dB) if tau = 100 us, costing P = 0.2 W per spark.
(c) A 0.1 mm plasma cannot be held on 0.2 W: conduction loss 4piR*kappa*dT ~1-10 W `[?]`, so tau <= 10-20 us and the gain shrinks to -3 to -6 dB. Each spark then costs ~100 uJ.

**A3 Seed + long-wavelength heater (double pulse, inverse bremsstrahlung).**
(a) A fs seed at NA ~0.07 (200 mm aperture at 1.5 m: w0 ~5 um, z_R ~70 um) reaches 1e13 W/cm2 with ~1 uJ and makes n_e ~1e17-1e18 cm-3. A 2 um or 10.6 um pulse (1-10 W, ~10 us) is then absorbed only in the seed: alpha(10.6 um, 1e17, 1 eV) ~5 cm-1, ~100 % above 1e18, while cold air is transparent. This gives a controllable T ~10-15 kK (continuum-optimal) and quasi-isobaric heating (A2).
(b) A 0.1 x 1.5 mm plasma at 12 kK emits ~0.5 lm for ~10 us: eps ~0.03-0.1 lm/W `[?]`, no better than mJ sparks, but shock is -6 to -15 dB and the ignition cost is only ~1 uJ.
(c) Needs a 10 W-class CO2 or Tm-fibre source. Average ~60 W for 10^4 dots x 60 Hz. Noise stays at the P5 wall.

**A4 Microwave/RF sustainment of a laser seed: agree with lab.**
A small plasma is a resonant scatterer with sigma_abs <= 3 lambda^2/8pi ~17 cm2 at 2.45 GHz. Depositing 10 W needs S ~1e4 W/m2, which is 1000x the ICNIRP public limit (10 W/m2) and ~900 W over a 0.3 x 0.3 m volume. Dead.

**A5 Burst mode / wavelength / pulse format.**
GHz bursts just re-implement A2/A3. UV (<=266 nm) lowers threshold ~10x but photolyses O2 to O3 (1e16-1e17/J) and is unsafe. Wavelength does not change eps. Nothing gained.

## B. Colour (cyan ~490 nm, orange ~600 nm) at a point in air

**B1 Chromatic adaptation via ambient tint.**
(a) A 8-12 kK plasma looks white/blue-white. If the room is 2200-2700 K (which the projector could ask smart bulbs for), von Kries adaptation makes the same flash read ice-blue/aqua. Orange accents come from cooler, lower-energy sparks (~6 kK) or from the tinted room itself.
(b) Costs 0 lumens. Expected shift ~Delta u'v' 0.03-0.06 `[?]`: aqua-blue, not saturated cyan.
(c) Needs control of room lighting. Purity is limited.

**B2 Time-gated spectral evolution.**
Early (<0.3 us) N II/O II lines near 460-500 nm (N II 500.1/500.5 nm is cyan-green) ride on continuum; late (>1 us) N2 first-positive/N I/O I 777 nm is red-orange. Real, but the continuum dominates and lines are only ~10-20 % of visible power `[?]`. You get a hue tilt, not a colour.

**B3 Doped gas curtain (see F4).** Ne gives orange-red lines (585-640 nm, sign colour). He 501.6/492.2 nm and hot Ar II 476/488/497 nm give cyan-blue lines. Xe gives bright white. Also removes NO/O3.

**B4 C2 Swan seeding.** ~1 % hydrocarbon in the plume gives Swan bands (474/516/563 nm), blue-green. Fatal: CO, HCHO, soot, flammability; also green-dominant.

**B5 Fluorescent surfaces (glove, ring, fingertips).** UV/blue laser onto a dye gives cyan or orange with QY ~0.9 and 40-60 nm width. Trivial, but only on surfaces (E3).

**B6 Fechner/Benham flicker colours.** Achromatic flicker patterns at 5-15 Hz evoke faint blue/green/red. Desaturated and unreliable; a garnish at best.

**B7 Aerosol gating (F1) or resonant vapour (F5)** gives any colour: Tm3+ 475 nm cyan, Er3+ 660 nm, Eu3+ 590/615 nm; Na 589 nm orange.

**B8 Chemiluminescence kills.**
- Air afterglow (O+NO -> NO2*): O atoms live ~13 us at 1 atm, k_rad ~6e-17 cm3/s, so ~3e6 photons/spark against 6e10 needed.
- O2(a) dimol 634 nm: needs sigma ~1e-24 cm2, i.e. ~1e5 J/cm2 to pump.
- NO2 LIF at 50 ppb: 7e-8 of the beam per metre.

## C. Audible noise

**C1 Small sparks (scaling law from P5).**
(a) Audible acoustic energy per spark ~ E * (15 kHz * 2pi R/c)^3 ~ E^2, so at fixed P the audible power ~ P*E. Use the smallest spark the eye can see (~20 uJ).
(b) About -10 dB per lumen versus 1 mJ sparks, at 4-14x more NO per lumen. Result: ~66 dB(A) per lumen at 2 m, so 6 lm gives ~74 dB(A). 40 dB(A) needs total light <= ~3 mlm (+-10 dB).
(c) Not enough alone; ultrasound above ~100 kHz is absorbed in air within metres and adds to heating, not to audibility.

**C2 Phase-locked firing above 20 kHz.**
(a) Fire all sparks on a 40-60 kHz grid so the spectrum is lines above audibility; A-weighting and the ear ignore it.
(b) Works for one listener if arrival times are compensated (sources 0.3-1.5 ms apart are spread over many periods).
(c) Fatal for several listeners and for room reflections: jitter of 0.3-1 ms destroys the line structure. Marginal gain.

**C3 Active cancellation: dead.** A spark is a positive volume source with no sign inversion. Sources must sit within lambda/10 (2 mm at 15 kHz), and quiet zones are ~7 mm at the ear. Room-wide cancellation of a 100 kHz-wide impulse train is impossible.

**C4 Masking.** A 45-50 dB(A) ambient masker (purifier fan, music) hides spark noise up to ~5 dB below it: worth +8 dB, so ~6x lumens at most. Only honest if the noise limit is "relative to a normal living room".

**C5 Scheduling.** Bunching a frame's sparks into a <1 ms burst changes crest factor, not Leq. Lowering refresh to 40 Hz gives -1.8 dB and risks flicker at >50 cd/m2. Negligible.

**C6 Don't heat air.** Everything quiet in this document (F1, F2, F3) avoids explosive deposition altogether.

## D. Cut or remove NO/O3

**D1 NO is not NO2: ozone is the limiting reagent.**
(a) A hot spark emits NO; O3 is destroyed at >400 K. Room NO2 only forms via NO + O3 -> NO2 (k = 1.8e-14 cm3/s) and NO + RO2/HO2. With indoor O3 ~5-15 ppb, the conversion lifetime is ~4-20 min, and the NO2 formable is capped by O3 supply: ACH 0.5/h x 30 ppb outdoor x 0.8 penetration ~ 10-15 ppb/h.
(b) 1e19 NO/s in 50 m3 at ACH 0.5 is ~60 ppb NO steady, ~1000x under NO's occupational TLV (25 ppm). NO2 is then capped by O3 supply at ~10-15 ppb increment. A 100 m3/h NO2 scrubber (90 %) removes 1800 ppb*m3/h against ~600 supplied. This turns 10^3-10^4 m3/h into ~10^2.
(c) Assumes a regulator accepts NO ~60-200 ppb (no public NO limit exists to my knowledge) and ignores HONO from heterogeneous NO2 and O3-rich buildings `[?]`.

**D2 Source capture.**
(a) Sparks make a small buoyant plume (10-20 W is a candle-sized plume, rising ~0.1-0.2 m/s). Place the display volume under the projector body/canopy (kitchen-hood principle) so >=90 % is captured at ~1 ppm.
(b) Flow needed = emission / concentration: 1e19/s / (1 ppm = 2.5e19 /m3) = 0.4 m3/s = 1400 m3/h (140 m3/h at 1e18/s), versus ~8e4 m3/h for room dilution to 20 ppb. Reduction 10-50x.
(c) Flow near the display (0.2-0.3 m/s) disturbs hand and spark position and adds flow noise. Capture fraction depends on room drafts. Display volume must sit near the hood.

**D3 Media.** Permanganate-alumina (Purafil-class, ~8 wt% capacity) takes NO and NO2: 1e19 NO/s ~1.8 g NO/h needs ~20-25 g media/h (~100 g per 4 h session). MnO2/Carulite catalysts destroy O3 at negligible cost. Consumable, but tractable.

**D4 In-plume DeNOx (NH3 / hydrocarbon SNCR).** The window is 1100-1400 K; the spark plume crosses it in 40-400 us against the ~10-100 ms the chemistry needs. NH3 at ppm levels is also not comfortable. Low probability.

**D5 Slower quench.** NO freezes near 2000-2500 K; only a slow-cooling large volume would let N + NO -> N2 + O consume it. Micro-sparks cool in microseconds. Not available.

**D6 Higher eps.** NO scales with joules, so every x2 in eps halves NO per lumen (A1, A3).

## E. Loopholes, perceptual tricks, the glove

**E1 Refractive holograms: closed (P6). Thermal micro-turbulence scattering: dead but instructive.** Scattered fraction is (2pi*dn_rms*L/lambda)^2: dn = 1e-5, L = 1 mm gives 1.6 %, about 1.6e6x Rayleigh. Fatal: a 1 um structure lives ~1 ns (thermal diffusion), and building it needs ~12 uJ/mm3 delivered through an absorber (CO2 at 4.26 um, alpha ~0.14 cm-1: ~0.85 mJ per voxel). No.

**E2 Touch lemma is single-sided.** A shell of emitters loses only ~5-10 % of rays per arm (the arm's solid angle from P), and a hand on the viewer side of P cuts nothing behind P except its own occlusion, which is physically correct. It fails on "consumer projector", not on physics: it needs a surrounding shell (room-scale, ~10^9-10^12 rays). AIRR/Asukanet-style real images are non-erasing but limited to a +-30 degree cone.

**E3 The glove.**
- A fluorescent/retroreflective glove is a first-opaque-surface at P: 1000x cheaper (0.03 lm versus 30 lm), and cyan/orange for free (B5).
- Use it as fingertip- or wrist-anchored UI (rings, menus, "tool" halos) while plasma or beads make the 3D body.
- The glove also carries tracking markers to close beam paths on hands (P7).
- Fatal: only the hand, and only near it.

**E4 Dim-room / mesopic mode (challenge to the 50-150 lux spec).**
- Wall L at 100 lux ~16 cd/m2; strokes at 25-180 cd/m2 give contrast 2-10. At 5 lux the wall is ~0.8 cd/m2, so the same contrast needs 1.6-8 cd/m2: 16-22x fewer lumens.
- Purkinje: V'(490) = 0.90 versus V(490) = 0.21, a 1.5-3x extra gain for cyan in the mesopic range.
- Combined with A1: 6-60 lm -> ~0.05-0.5 lm, which is 53-63 dB(A) at 2 m. Still 15-25 dB over, but no longer absurd.
- Fatal: not a "50-150 lux room".

**E5 Temporal salience.** Modulated/moving stimuli are 2-3x easier to detect (de Lange, peak 8-10 Hz). An animated shimmer style buys conspicuity, not fill.

**E6 Brief kills of "missed mechanisms"**
- Non-collinear FWM (BOXCARS): acceptance angle ~lambda/a, efficiency (pi*dn*l/lambda)^2 ~1e-7, ~5e5 photons/pulse versus 6.7e10.
- Air lasing: forward only.
- Radioluminescence of N2: UV, ~20 photons/MeV.
- Passive dust: ~10 particles/cm3 gives beta ~1e-7/m.

## F. Grey zone

**F1 Bounded, recovered, gated-luminescent aerosol cell.**
(a) A ~0.5 m laminar cell holds 30 nm upconversion particles (NaYF4:Yb,Er,Tm). Two-photon-like I^2 emission (or crossed two-colour beams) localises light to +-3 z_R (1-20 mm at NA 0.025-0.07). Emission is cyan (Tm 475 nm), green or red (Er 660 nm); a HEPA-class loop recovers the particles.
(b) 1e-3 lm per mm3 voxel = 4e12 photons/s, at ~1e6-1e7 photons/s per particle, so 4e5-4e6 particles/mm3, i.e. 20-230 ug/m3 inside the cell. At 0.1-3 % energy efficiency 6 lm needs 0.3-10 W of IR (eye-safe 1.5 um Er route is worse `[?]`). Emission persists 0.1-1 ms per excitation, which smooths pulsed scanning. Noise 0, NO 0, O3 0, arbitrary colour.
(c) Fatal candidates: inhalation toxicology of insoluble rare-earth fluoride nanoparticles (needs room average <1 ug/m3, i.e. 20-200x containment), 30 nm particles do not settle and must be filtered, a hand punching through disrupts laminar flow, and beam hazard. Breaks "no particles" and probably "open air".

**F2 Levitated bead arrays (acoustic trap, from Smalley 2018 / Hirayama 2019; speeds from memory).**
(a) A 1 mm expanded-polystyrene bead in a 40 kHz phased-array trap moves at up to ~9 m/s, painting a 3D image by persistence of vision. A tracked sub-mW cyan spotlight per bead gives its light.
(b) Path per bead per frame at 60 Hz is 15 cm, so 100 beads give 15 m of stroke per frame (the low end of the 10-100 m budget). Brightness is cheap because light hits a surface: duty is 1 mm / 9 m/s / 16.7 ms = 0.67 %, so a 100 cd/m2 average needs 15,000 cd/m2 on the bead = 60 klux = 0.06 lm per bead, about 0.4 mW of 490 nm light. Trap power ~0.1 W acoustic per trap (155 dB SPL over (lambda/2)^2).
(c) Demonstrated: 1-few beads, ~10 cm, ~10 Hz. Scaling to 100 independent 9 m/s traps needs thousands of transducers. The hand within ~5 cm distorts the standing wave (touch lemma applies partially: top/bottom arrays with side hand entry helps). Ultrasound in the room must stay <~90-110 dB. Beam hazard is small (mW).

**F3 Mist sheets (Fogscreen class), possibly stacked.** Pure-water mist is safe and touchable, and a projector paints any point of a thin sheet. Fatal: 2D only (three to five stacked sheets at 5-20 cm give depth-fused illusion), forward-scatter peak makes side and back views 30-100x dimmer, and the mist and its edge are visible in 50-150 lux (haze, not clean air).

**F4 Engineered noble-gas volume (laminar recirculating column).**
(a) In Ar/Ne/Xe there is no N2/O2, so no NO or O3. Monatomic gas has no dissociation sink, so more energy radiates (est. 3-10x eps `[?]`). Ne gives orange-red lines, Ar/He give cyan lines, Xe gives white.
(b) A leak of 6 m3/h into a 50 m3 room at ACH 0.5 gives 24 % Ar and O2 falling to ~16 % (asphyxiant); <=0.5 m3/h keeps Ar at ~2 %. Xe costs ~$10^4/m3, so closed-loop recovery is mandatory.
(c) Shock and noise are unchanged (P5). Hand entrainment restores air chemistry locally. Not "open room air".

**F5 Resonant tracer vapour (Na 589 nm, orange).**
(a) After pressure broadening (~15 GHz) sigma ~7e-13 cm2, still 1e14x Rayleigh. Yield ~5 % after O2/N2 quench, I_sat_eff ~9 W/cm2. About 4e9 atoms/cm3 (0.15 ug/m3) gives 4e12 photons/s per mm3 voxel. A 0.1 W beam, not 90 W.
(b) That is a x10^3 reduction in beam power for orange.
(c) Fatal: saturated Na vapour at 300 K is only ~1e6 cm-3 (4000x short), it is reactive (NaOH aerosol), the beam glows along its whole path, and there is no cyan analogue (Ba+ 493 nm needs ions).

**F6 Haze + beams (laser-show haze).** beta = 1e-2 /m (1-3 mg/m3, x100 the PM2.5 guideline) makes a 0.1 W beam sufficient for a 0.05 cd/m line. Fatal: every beam glows along its whole path, so only chords, no points; and the haze is visible in room light.

## Cross-check table (does anything beat all three walls: light, noise, NO?)

| Route | Light | Noise | NO/O3 | Colour | Open air, no particles |
|---|---|---|---|---|---|
| Dense-dot air plasma (lab baseline) | 3-30x short | 35-45 dB over | fixable 10-50x (D1-D3) | violet-white | yes |
| Sparse dim-room plasma (A1+A3+E4+D+B1) | ~ok at 0.05-0.5 lm | 15-25 dB over | ok | aqua at best | yes |
| Gated UC aerosol cell (F1) | ok | none | none | any | no (particles, cell) |
| Levitated beads (F2) | ok (surface) | ultrasound only | none | any | yes, small scale |
| Noble-gas column (F4) | better | still over | none | Ne/Ar/He lines | no |

## Top 3 ideas, ranked by P(works) x impact (impact 0-10 = fraction of the stated goal delivered)

1. **F2 Levitated multi-bead persistence-of-vision array with tracked spotlights.** P ~0.4 (single-bead, ~10 cm, 10 Hz already published; scaling to tens of beads and 30-60 Hz is engineering, not physics) x impact ~6 = **2.4**. Solves light, colour, noise and NO/O3 at once because light hits a surface. Limits: size (<~30-50 cm), bead count, touch disturbs the trap.
2. **Sparse-dot plasma stack: A1 (stipple, mJ-class dots) + A3 (seed + long-wavelength heater) + E4 (dim mesopic room) + B1 (tinted room) + D1/D2/D3 (O3-limited NO2, source capture, media).** P ~0.6 (each piece is conventional) x impact ~3 = **1.8**. Only route that keeps "open air, nothing added". Closes the NO wall and most of the light wall; does not close the noise wall (still ~15-25 dB over).
3. **F1 Bounded, recovered, gated UC-nanoparticle aerosol cell.** P ~0.12 (toxicology and containment unproven) x impact ~9 = **1.1**. Only idea I found that could hit cd/m2, cyan/orange, 60 Hz, silence and zero NO/O3 at room scale. Breaks "no particles" in the strict sense.

Not ranked but cheap and mandatory: D1-D3 (P ~0.7, removes the NO wall, leaves the noise wall).

**First experiments (decide everything above).** (1) Measure eps(E) and audible-band SPL of 5-50 uJ sparks at 2 m; if eps < 0.03 lm/W or SPL(per lm) > 70 dB(A), plasma dense-dot is dead. (2) Measure indoor NO -> NO2 conversion with real O3 (D1). (3) Screen UC-NP aerosol toxicology and HEPA loop containment (F1).

## Verdict

No. An Iron Man-quality hologram in the strict sense (25-180 cd/m2 strokes, 10^4-10^5 points at 60 Hz, all-around, touchable, glasses/fog/particle-free, <=40 dB(A), NO2 < 20-50 ppb) cannot be engineered from known physics. Air plasma is the only in-air emitter, but it hits three independent walls. Light: probably 3-30x worse than the lab's 1 lm/W once sparks are small enough for 10^4-10^5 dots. Noise: audible level scales as ~66 dB(A) per lumen at 2 m, so 40 dB(A) allows ~3 mlm against a 6-60 lm target, a 35-45 dB shortfall that no pulse format or cancellation scheme recovers. Colour: violet-white only, ice-blue at best with a tinted room. The NO/O3 wall is the one that yields: NO is O3-limited in its conversion to NO2, and source capture plus permanganate/MnO2 media cuts the flow needed by 10-50x. The closest achievable things are, in order: (i) a tabletop volumetric display of a few tens of cm made of acoustically levitated beads lit by tracked spotlights, which is bright, coloured, silent, not-quite-touch-safe, and needs no plasma; (ii) a dim-room, sparse-dot plasma "constellation" of ~10^2-10^3 dots at 55-65 dB(A) with a glove-anchored fluorescent UI, i.e. a candle-flame-scale hologram; and (iii) only if inhalation safety and containment of nanoparticles can be shown, a bounded gated-luminescent aerosol cell, which is the one route with a credible path to cinematic brightness and colour and which quietly abandons the "nothing but air" premise.

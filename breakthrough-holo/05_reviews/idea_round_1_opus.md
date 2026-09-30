# Idea round 1: independent review (Opus)

Tags: **[D]** derived here (scratch scripts, standard physics); **[E]** order-of-magnitude estimate, ±3–10×; **[L]** from the lab's R1–R4 files; **[?]** unknown, needs measurement. P = my probability the idea works as stated.

## 0. Where I think the lab is wrong (read this first)

1. **Noise is mis-attributed, and it is the tightest constraint, not the loosest.** Audible noise comes from *heat-release shot noise*, not from the shock wave. Each absorbed joule expands air isobarically by κ = (γ−1)/(γp₀) = 2.8×10⁻⁶ m³/J. A Poisson stream of such volume steps gives [D]:
   **L_A(1 m, free field) ≈ 35 dB(A) + 10·log₁₀(P·E / 2.7×10⁻⁷ W·J)**, with P the absorbed power and E the absorbed energy per voxel. Add 3–5 dB for a room.
   - The lab's operating point (10 W, 30 µJ) gives ~66 dB(A). Even 1 W at 10 µJ gives 51 dB(A).
   - With random voxel order, 35 dB(A) allows only **~27 mW at 10 µJ**.
   - Sanity check: the same model predicts 76 dB SPL at 10 cm for 1 kHz × 0.1 mJ absorbed. The Fairy Lights snippet reports 77 dB [L]; its distance and energy are uncertain.
   - The shock energy at µJ scale is MHz ultrasound that dissipates within a few cm. It is not what you hear. Fix in C2.
2. **Chemistry is framed both too loosely and too strictly.**
   - Too loose on NO₂: WHO 2021 24-h NO₂ is 25 µg/m³ ≈ **13 ppb**, not 20–50 ppb. At 13 ppb, a 50 m³ room at 0.5 ACH tolerates only 2×10¹⁵ NO₂/s, i.e. **~20 mW absorbed** at 10¹⁷/J.
   - Too strict on NO: hot sparks make mostly **NO**, which the lab lumps in with NO₂. NO is not NO₂ (see D1).
3. **1 lm/W is optimistic for display-sized voxels.** It is a mJ-spark number. The radiated fraction scales roughly with kernel size ∝ E^{1/3} [E], so a 10 µJ voxel gives ~0.03–0.3 lm/W [?].
4. **"Cyan is not available" is too pessimistic.**
   - Under 2700–3000 K room light, a 10–20 kK plasma continuum has a dominant wavelength of **480–482 nm at colorimetric purity ~0.5** relative to the adapted white [D, CIE 1931]. That is the film's azure-cyan (see B1).
   - Orange is genuinely unavailable in pure air.
5. **The target unit is wrong.** Visibility of thin strokes is set by linear intensity L·w (cd/m) times stroke length, not by the number of points.
   - Flux Φ = 4π·L·w·ℓ. Examples: 10 m at 10 cd/m² × 1 mm → 1.3 lm; 10 m at 25 cd/m² → 3.1 lm; the film maximum (57 m at 180 cd/m²) → 130 lm.
   - In "pen" mode (C2) the budget is joules per metre of stroke, not points per frame.
6. **Theorem 1 is right but can be sharpened (E1).** Sharpened, it also closes the "scatter at P" door for weak media, including plasma, which has Δn ~ 10⁻³.

---
## A. More visible lumens per absorbed joule (and per NO, per unit of shock)

**A1. Kernel-size law (framing, not a fix).**
- (a) Light ∝ n_e²·V·t_emit, and t_emit ≈ kernel radius / expansion speed. The radiated fraction therefore rises with kernel size until the radiative time (~1 µs at 10¹⁹ cm⁻³, 1 eV) equals the expansion time, at r ~ mm.
- (b) η(E) ≈ (0.3–3 lm/W)·(E/10 mJ)^{1/3} [E] → ~0.03–0.3 lm/W at 10 µJ and ~0.1–1 lm/W at 300 µJ.
  - Blast radius R₀ = (E/p₀)^{1/3}: 0.21 mm at 1 µJ, 0.46 mm at 10 µJ, 1 mm at 100 µJ.
  - Per stroke: L_eq(1 mm width) = η·ε·f/(4π·w). With η = 0.2 lm/W, ε = 20 mJ per metre of stroke per frame and f = 60 Hz → **19 cd/m²**. Stroke brightness per metre is fine; total metres × chemistry is the problem.
- (c) Bigger voxels are brighter per joule but coarser. There is no free lunch; the optimum is ~10–100 µJ at 0.3–0.5 mm pitch.

**A2. Seed-and-heat voxels (two lasers).**
- (a) A ps/fs 1.5–2 µm pulse (NA 0.2–0.3) seeds n_e ~10¹⁸ cm⁻³ at P. A ns or 100 ps heater at 2 µm or 10.6 µm (inverse bremsstrahlung ∝ λ²) then grows and heats only the seeded kernel. Its intensity stays below unseeded breakdown (~10⁹ W/cm² at 10.6 µm).
- (b) Absorbed fraction rises from 1–26 % [L] to ~80 % [E]. Deposited energy becomes deterministic (pulse-to-pulse jitter of a few %, versus ~10–20 % near threshold), which C2 needs. All stray light is at ≥1.5 µm (cornea-only MPE). Gain in lm per *delivered* J ≈ ×3–10; in lm per *absorbed* J ≈ ×1–2 [E].
- (c) At 10.6 µm, n_c = 10¹⁹ cm⁻³, so dense seeds reflect the heater and the heater energy must be tuned. A 10.6 µm spot at f/10 is ~0.26 mm, which caps resolution. P ≈ 0.4.

**A3. Temperature targeting ("warm sparks", ~1–1.5 eV).**
- (a) At T_e ≳ 3 eV most radiation is VUV. Nearby cold air absorbs it, which photolyses O₂ (→ O₃, then NO₂ via NO + O₃) and wastes energy. Holding the kernel at ~1–1.5 eV with heater energy and duration shifts the recombination continuum toward the visible.
- (b) Visible share of the radiation could rise ×2–3 [E], and O₃ from the VUV halo falls sharply [?].
- (c) A cooler kernel is also less dense, and light ∝ n². The net effect may be ≤×2. P ≈ 0.3.

**A4. Double pulse / burst reheating.**
- (a) A second pulse reheats the expanding kernel after ~0.1–1 µs.
- (b) LIBS gains of 2–100× are for solid targets. In gas the kernel is already rarefied (n²), so expect ≤×1.5–2 [E].
- (c) It adds energy into lower-density gas. Useful only for stabilising absorption (see A2).

**A5. Microwave/RF sustainment of laser seeds.**
- (a) Seeds are placed by the laser; a sub-breakdown RF field heats only the seeded voxels.
- (b) Sustaining an air plasma at 1 atm needs E/N ~30–100 Td, i.e. **0.75–2.5 MV/m**. At 100 GHz, a 3 mm spot at 1 MV/m is ~9 kW. ICNIRP public exposure is ~61 V/m.
- (c) **Dead** (the lab's kill stands).

**A6. Shock recycling (untried).**
- (a) A ring of 6–12 micro-sparks around P sends converging shocks that implode at P and flash there, recovering the 50–80 % shock share.
- (b) The core is tiny and unstable (Guderley). Shock-focusing light yields are ≲10⁻³ of shock energy [E], and it heats P, so NO goes up.
- (c) **Net loss** in both light and chemistry. Dead, but cheap to simulate.

**A7. GA pulse shaping (×1.82, measured [L]).** Take it. It stacks with A2 and costs nothing chemically.

---
## B. Colour at a point in ordinary air

**B1. Warm-surround chromatic adaptation (pure air, best colour idea).**
- (a) Viewers adapt to the room, not to 0.1 mm strokes. Light the room at 2700–3000 K (the film labs are warm-lit), and a hot-plasma "white" is seen relative to a warm white point.
- (b) Computed [D]: a 10/15/20 kK continuum under 2700 K adaptation has dominant wavelength **482/481/480 nm, purity 0.48/0.53/0.55**; under 4000 K, 479 nm at purity 0.35–0.44; under D65, 473 nm at purity only 0.16–0.28.
- (c) Adaptation is incomplete (~70–90 %). The spark's true chromaticity is uncertain [?], and N₂⁺ 391/428 nm lines pull it toward violet. It gives cyan-azure, not saturated 490 nm, and no orange. **P ≈ 0.6** for "reads as hologram-cyan".

**B2. Mesopic (Purkinje) boost for violet-blue emission.**
- (a) V′/V is ~17 at 430 nm and ~23 at 400 nm; times 1700/683 lm/W, scotopic efficacy is ~43× and ~58× photopic. So in a ≤10–20 lux room, N₂/N₂⁺ violet light is seen much brighter than photopic lumens say, and bluer.
- (b) Mesopic weighting (m ~0.3–0.7) gives ×5–15 for the violet component, peripheral only [E].
- (c) The fovea has no rods, so fixated fine lines get ~×1. It helps glow and "presence", not detail. Cold fs plasma at 10⁻⁵ lm/W stays dead even at ×50.

**B3. Pure-air spectral engineering.**
- (a) Emphasise the N₂⁺ 1N (0,2) band at 470.9 nm, N II 500.5 nm, and Hβ 486.1 nm (from 1–2 % H₂O) by tuning temperature and density.
- (b) Each is ≲1–5 % of visible output beside the continuum and violet bands [E].
- (c) Negligible hue shift. Dead as a colour source (useful only as diagnostics).

**B4. Plasma Thomson/Mie scattering of a cyan probe.**
- (a) A cyan beam scatters off the free electrons, so the colour comes from the laser.
- (b) σ_IB/σ_T ≈ 10⁴–10⁵ at 490 nm and n_e ~10¹⁹ cm⁻³ [D]. The probe heats the plasma instead of scattering, so ≤10⁻⁴ of the probe becomes cyan light. A plasma sphere with Δn ~3×10⁻³ has a scattering efficiency ≲0.06 and scatters mostly forward.
- (c) **Dead.**

**B5. Seeded sparks (grey zone).**
- (a) A spark on a projector-placed NaCl micro-particle (the same material as halotherapy salt aerosol) emits Na D at 589 nm (orange) for µs after the continuum. Ba II 493.4 nm would be cyan, but soluble Ba is toxic.
- (b) Aerosol LIBS shows Na D is intensely visible [E, standard LIBS experience].
- (c) Each accent needs a particle delivered exactly to P, it is consumed, and it adds chemistry. Accents only.

**B6. Laser-heated "ember" particles (grey zone).**
- (a) Absorbing micro-particles are laser-heated to 1800–2500 K and glow orange.
- (b) They are bright per particle, but the Planckian locus never passes through cyan.
- (c) Oxidation, smoke and fire perception. Orange accents only.

**B7. RGB-lit recoverable particles (grey zone).** The only route to full saturated colour; see F1. 1 mW onto a particle gives 0.07 lm (490 nm) or 0.2 lm (600 nm), and a 1 mW visible beam is Class 2.

**B8. Two-photon vision.**
- (a) fs 1000–1100 nm light is seen as ~500–550 nm through two-photon isomerisation (Palczewska 2014).
- (b) It only works for light the eye itself focuses, i.e. light that arrives from direction P.
- (c) Theorem 1 applies unchanged. **Dead** as an in-air colour source.

---
## C. Audible noise from pulsed micro-sparks

**C1. Thermoacoustic shot-noise law** (§0.1). Volume steps have spectrum |p(f)| = ρ·2πf·κ·E/(4πr), so the noise is weighted ∝ f² and **dominated by 3–15 kHz**. Consequences:
- Noise ∝ P·E, so smaller voxels are quieter only in proportion to E.
- Active noise control can't reach 3–15 kHz across a room (λ/10 ≈ 2–10 mm).
- Radiated energy is silent, but it is only ~1–30 % of the total.

**C2. Subsonic "pens" with constant heat rate (new; the key noise idea).**
- (a) A uniformly moving source of constant strength does not radiate: its retarded source strength q₀/(1−M·cosθ) is constant in time [D]. So draw strokes as continuous paths: each pen is a focus moving at M ≈ 0.3–0.45 (100–150 m/s) and firing equal pulses at 300–500 kHz with 0.2–0.4 mm pitch.
  - Sound then comes only from stroke starts and stops (use 1 ms Hann energy ramps and Eulerian path planning), from curvature (negligible at v ≪ c), and from energy jitter.
- (b) [D] Random order at 3 W and 10 µJ gives 55.5 dB(A). Pen mode, same power:
  - ramps (3000/s, 1 ms, 1 W pens) → **25 dB(A)**;
  - jitter at σ_E = 2 %/5 % → 21.5/29.5 dB(A).
  - ⇒ ~**30 dB(A)** total, i.e. −25 dB.
  - About 10 pens × 100 m/s ≈ 17 m of stroke per frame at 60 Hz.
- (c) Risks [?]: absorbed-energy jitter near breakdown (~10–20 %) would give only −14 to −20 dB, so it needs A2's deterministic seeding. Each pulse sees the previous kernel's hot wake. Content changes must be faded over ≥50 ms. It needs ~10–20 simultaneous foci. **P ≈ 0.5.**

**C3. Put the pulse comb in ultrasound that air absorbs.**
- (a) Each pen's periodic train puts energy only at k·f_p.
- (b) The f_p line is ~97–109 dB at 1 m for a 1 W pen at 250–500 kHz, before absorption [D]. Air absorption is 8 dB/m at 200 kHz and 42 dB/m at 500 kHz [L]. Choose **f_p ≥ 300–500 kHz**: it decays within ~0.5 m and avoids the 25–100 kHz band (public limit 100 dB [L]).
- (c) There is no guideline above 100 kHz. Hands inside the volume get MHz fields, but air-to-skin transmission is ~0.1 %. Fine.

**C4. Avoid the Mach-cone trap (a pitfall the lab would hit).**
- (a) A single raster drawing 10 m per frame at 60 Hz moves at 600 m/s (Mach 1.75). The retarded-time factor diverges at cosθ = 1/M, so every stroke radiates a coherent "sonic boom" sheet.
- (b) This is much worse than C1.
- (c) Use ≥10 parallel subsonic pens, never a supersonic scan.

**C5. Active cancellation with a perfect reference.** The display knows every pulse, so feed-forward anti-noise is exact in timing. Cancellation is global only below ~300–500 Hz, where the noise is small anyway. It is a helper, not a fix.

**Side effect to plan for:** strokes heat air at 0.3–1.2 W/m. That raises the local air temperature by ~5–20 K (conduction-only estimate; convection lowers it), giving Δn ~10⁻⁵ and a visible *schlieren shimmer* around strokes. It is a heat-haze artefact; arguably it even looks "holographic".

---
## D. Cutting or removing NO/O₃

**D1. NO is not NO₂ (reframe the constraint).**
- (a) Hot kernels make mainly NO (Zeldovich chemistry, and N atoms reacting with O₂). At ppb levels, 2NO + O₂ → 2NO₂ is second order in NO: k = 3.3×10⁻³⁹·e^{530/T} cm⁶/s gives only **0.04, 0.18, 1.6 and 18 ppb/h of NO₂ at 50, 100, 300 and 1000 ppb NO** [D].
  - Limits: NO ACGIH TLV 25 ppm and EU IOELV 2 ppm; NO₂ WHO 13 ppb (24 h), EU OEL 0.5 ppm [L]. So NO is 4–125× more tolerated than NO₂.
  - Gas stoves already give 100–500 ppb of NO indoors.
- (b) Holding NO ≤ 100–300 ppb in 50 m³ at 0.5 ACH allows 1.7–5×10¹⁶ NO/s, i.e. 0.17–0.5 W at 10¹⁷/J; at 2 ACH, 2 W.
  - For 10 m of stroke at 20 cd/m² with η = 0.2–1 lm/W (2.4–12 W absorbed), you need **~120–600 m³/h** of air exchange. Under the NO₂-at-13 ppb framing it would be **~13,000 m³/h**. A ×10–25 gain.
- (c) Caveats:
  - Excess NO turns *all* incoming O₃ into NO₂ within ~7 s (k = 1.8×10⁻¹⁴ cm³/s), so NO₂ ≈ the indoor O₃ supply. Filter O₃ out of the incoming air with carbon.
  - The NO₂/NOx ratio at the source for 10 µJ kernels is **unknown** [?]. If it is ≥5 %, the gain collapses.
  - Chronic ~0.3 ppm NO for the public needs toxicology review.
  - **P ≈ 0.35.**

**D2. O₃-free sparks.** Avoid cold fs plasmas: they give ~30× more O₃ than NO [L], and O₃ then titrates NO into NO₂. Use warm kernels (A3) to cut the VUV halo. Target O₃:NOx < 0.05 [?].

**D3. Displacement flow into the projector.**
- (a) Buoyant plumes from 1–10 W spread over 1 m² rise at only ~4 cm/s [D], so room drafts dominate. Instead, pull a gentle 0.1 m/s flow up through the volume footprint (~360 m³/h) into a ceiling-mounted projector fitted with KMnO₄/alumina (oxidises NO → NO₂, then sorbs it) and an O₃ catalyst.
- (b) This captures a concentrated plume, worth ≈×2–5 over treating mixed room air [E]. A large, slow fan can be ~30 dB(A).
- (c) Sorbent is consumed at 10¹⁸ NO/s ≈ 0.3 g/h of NO₂ → ~2–4 kg/yr of media at 2 h/day [E]. Drafts break capture.

**D4. N-atom reburn (N + NO → N₂ + O, k = 3×10⁻¹¹).** Costs ~20–40 eV per NO destroyed, i.e. +50–100 % energy [E]. It also makes O atoms, then O₃. **Dead.**

**D5. Fast micro-kernel quench.**
- (a) 50–100 µm kernels cool by conduction in ~2–10 µs, faster than thermal Zeldovich NO forms (~60 µs at 4000 K) [D].
- (b) Could cut thermal NO ×3–10 [?].
- (c) N atoms from recombination still become NO via N + O₂, so the floor is ~1 NO per N atom (~10¹⁶–10¹⁷/J). **Measure; do not assume.**

---
## E. Loopholes and missed mechanisms

**E1. Momentum-budget theorem (sharpens T1).**
- Every coherent (parametric) process driven by fields from aperture A emits k_s = Σ±k_i. For visible output from a cone of half-angle α, sinθ_s ≲ (Σ|k_i|/k_s)·sin α, i.e. θ_s ≲ α for THG and ≲ 3α ≈ 12° for FWM at α = 4°.
- Sideways output requires ω_s ≤ Σω·(1−cos α), i.e. far IR.
- The only escapes:
  1. incoherent emission at P;
  2. condensed matter at P with Δn·size ≳ λ (Δn ~0.1–1, i.e. particles or droplets);
  3. gain-guided emission (E2).
- Plasma as a scatterer fails (B4), and so do plasma gratings written by projector light (their K = k₁−k₂ also lies inside the cone). Mirrors on walls supply momentum only by adding room infrastructure. The lab's conclusion stands, with a sharper reason.

**E2. Eye-directed ASE "line voxels" (untried; long shot).**
- (a) For each tracked eye, write a 1–2 mm × 10–20 µm gain column at P, aligned with P→eye (a flying focus or short line focus). Amplified spontaneous emission leaves mainly along the axis, so the eye sees a point at P while others see a faint line.
- (b) The directional gain vs isotropic emission is 4π/Ω ≈ **10⁵** (one pupil at 1 m intercepts only 5.6×10⁻⁷ of 4π).
- (c) Air gain lines are 337 nm (UV), 391/428 nm (N₂⁺), and 742/845 nm (N, O, backward-pumped): nothing visible except violet. The gain-length product over mm is ≪1 at 1 atm, so there is no real directionality. It needs one column per eye per voxel, and it sends coherent UV-violet into eyes. **P ≈ 0.02**, impact huge.

**E3. Target re-spec (vision science, not physics).** Linear intensity × length (§0.5), a dim warm lab (≤20–30 lux, B1/B2), and 2–5× contrast rather than the film's 5–12×. Together they cut the need from 6–60 lm to **~1–3 lm**. (CFF ≈ 40 Hz for dim thin strokes cuts voxel rate, not lumens.) P ≈ 0.8 as a spec, but it is a relaxation of Iron Man quality, not a breakthrough.

**E4. The glove does four jobs.**
1. **Conformal emitter:** hologram points that lie *on* the hand (the gauntlet scene) shown by emitters in the glove are exact for all viewers, because a surface point emitting isotropically is in-volume emission.
2. **Laser PPE:** an absorbing outer layer with high damage threshold lets pens run near hands. Fairy Lights leather shows ~100 µm holes [L], and a glove makes that a non-issue.
3. **Fiducials** for sub-mm tracking and a 5–10 mm plasma keep-out halo.
4. **Vibrotactile haptics.**

P ≈ 0.8, medium impact. It does not help beams that the hand blocks; multi-aperture addressing does.

**E5. Gaze-contingent density.**
- With few tracked viewers, thin out content far from every fovea. Saves ×2–4 in average power [E].
- Gaze-tracking all viewers from the projector is hard. ns flashes also give "phantom-array" ghosts during saccades (a real artefact of all plasma voxels).
- P ≈ 0.3.

**E6. "Clean" air is not empty.**
- Natural ions, ~10³ cm⁻³ (≈1 per mm³), can seed avalanche for a 10.6 µm heater. This lowers the threshold, not the lm/J.
- Ambient ultrafine particles (~10⁴ cm⁻³), laser-heated to incandescence: ~10⁴ photons per voxel, versus the ~7×10⁹ per voxel needed for 1 lm at 6×10⁵ voxels/s. Dead.
- Local condensation of room humidity at RH 50 % needs ΔT ≈ −15 K (Δp ≈ −17 kPa) held for ms. That is ≥180 dB of sustained rarefaction. Dead.

**E7. Harvest the room's own dust as scatterers.** R3 is technically satisfied, since the dust is ambient. It is the grey zone in disguise, with random sizes and dirty particles. Mentioned only to close the loophole honestly.

---
## F. Grey zone (projector-supplied, recovered matter)

**F1. RGB-lit photophoretic particle accents (OTD scale-up).**
- (a) 10–100 cellulose particles of 10–30 µm, each in its own trap, drawing POV strokes at ~1 m/s and lit by RGB lasers.
- (b) 100 particles draw ~1.7 m of accent per 60 Hz frame; the film needs 1–11 % orange. 1 mW gives 0.07–0.2 lm per particle. Silent and chemistry-free.
- (c) Hold power is ~24–100 mW per trap [L, low confidence]; 405 nm trap light glows purple, and NIR trap light is a retinal hazard. Hands knock particles out, so the base needs a catch tray. Fails at 10⁴+ points. **P ≈ 0.3** for accents.

**F2. Optically powered levitated micro-LED voxels (untried).**
- (a) 100 µm InGaN chiplets on micro-PV cells, powered by an invisible IR beam and emitting their own 490 nm cyan (or amber AlInGaP).
- (b) IR → cyan ~10–15 % [E]. One chiplet at 1 mW cyan = 0.14 lm, about 10⁴× a plasma voxel's light per watt. No visible beams, no chemistry.
- (c) Levitation (acoustic traps at ≥150 dB near people; photophoresis cannot lift µg chips), orientation control, count ~tens, and eye foreign-body risk. **P ≈ 0.1.**

**F3. Ballistic water droplets (self-evaporating).** Stopping distance at 5 m/s is 6 mm for 20 µm drops, 0.15 m for 100 µm and ≲1 m for 300 µm (Stokes; real drag is larger). Only ≥300 µm drops cross the volume, and they rain onto people. **Dead.**

**F4. Two-photon, photoswitch or upconversion (UCNP) aerosols.**
- 50 nm UCNPs at 1 per mm³ are only 0.27 µg/m³, but they give ≤10⁶ photons/s per particle, versus 7×10⁹ per voxel-flash needed.
- 10 µm dye beads at 1 per mm³ are 0.5 g/m³ of visible PM10 haze.
- **Dead** (fog in disguise).

**F5. Swept 10 µm fibre (swept-volume display with ~0.1 mg of matter).**
- Aeolian tones at 0.2·v/d ≈ 2 MHz (inaudible). Full colour with lasers. No chemistry.
- It is a swept screen, and a thread moving at ~90 m/s is a cutting hazard for hands. Violates R3/R8.

---
## Top 3, ranked by P × impact

1. **C2 + C1: subsonic constant-rate pens, with A2 seeding for stable absorption.**
   - P ≈ 0.5.
   - Without it, 35 dB(A) caps absorbed power at ~27 mW for 10 µJ voxels (~0.005 lm), which kills any pure-air display regardless of chemistry.
   - With it, ~10 W is ≈30 dB(A): ~×300 power headroom.
   - Test: microphone plus random-order vs pen-order firing at 1–3 W.
2. **D1 + D2 + D3: make NO, not NO₂/O₃, and hold NO at ≤100–300 ppb with ~120–600 m³/h of air exchange through a ceiling intake.**
   - P ≈ 0.35.
   - Impact: required air treatment falls from ~10⁴ to ~10² m³/h (×10–25), i.e. "gas-stove-class" air impact.
   - Hinges on NO₂/NOx < 5 % and O₃:NOx < 5 % for 10–100 µJ warm kernels (measure with a chemiluminescence NOx analyser and an O₃ monitor in a 1 m³ chamber).
3. **B1: warm-surround adaptation for colour.**
   - P ≈ 0.6.
   - It turns "violet-white plasma" into a ~481 nm, purity ~0.5 azure-cyan for everyone in a 2700–3000 K-lit room: ~90 % of the film's palette, in pure air, at zero energy cost.
   - Orange accents still need F1/B5 (grey zone).

Runners-up: A2 as a standalone lm/J and eye-safety gain (P 0.4, ×1.5–3); E4 glove (P 0.8, safety and touch); E2 ASE (P 0.02 × 10⁵).

## Verdict

- **Film level: no.** With known physics, pure room air, bystander-safe chemistry and 35 dB(A), the film-level spec cannot be met. That spec is 10–57 m of 25–180 cd/m² stroke in a 50–150 lux room, saturated cyan *and* orange, at 60 Hz. The binding product is:
  - (lm per absorbed J) ≈ 0.03–1 lm/W for display-sized (10–300 µJ) kernels, times
  - (NOx per J) ≈ 10¹⁶–10¹⁷.
  - Even under the most favourable reframing (NO-not-NO₂, pen scheduling, warm-surround colour), the full film spec needs ~10–100 W and ~10³–10⁴ m³/h of air treatment. That is 1–2 orders of magnitude beyond an everyday device.
  - The lab's "only plasma" conclusion is correct and can be proven more sharply (E1). No clean-air loophole survives except gain-guided emission (E2), which air cannot supply in the visible.
- **Closest achievable** (plausibly engineerable, P ~0.2–0.3 pending two bench measurements):
  - What it shows: a **dim, warm-lit-room** display with **~2–10 m of stroke per frame at ~10–20 cd/m²-equivalent**, reading azure-cyan (B1) with no true orange, at 60 Hz. That is far beyond anything demonstrated (Fairy Lights: ≤1 cm³; Burton: dark rooms).
  - How it is driven: seed-and-heat 1.5–2 µm / 10.6 µm lasers with ~10 subsonic pens, 2–12 W absorbed, at ~30–35 dB(A).
  - Air and touch: ~100–600 m³/h of air exchange through the projector, holding NO ≤0.3 ppm and NO₂ ≲10 ppb. A glove provides touch, haptics, hand-surface content and hand laser protection.
- **Grey zone:** a few dozen recoverable, RGB-lit particles (F1) could add saturated orange and cyan accents. Particles cannot carry the bulk at 10⁴–10⁵ points.
- **Two measurements decide whether the gap is ×1 or ×100.** Build nothing else until they exist:
  1. η(E) in lm per absorbed J;
  2. NO/NO₂/O₃ per J, both for 10–100 µJ seeded-and-heated kernels.

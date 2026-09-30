# Task list (from a word-by-word reading of the request)

Status: `[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped (with reason)

## A. Lab setup
- [x] A1 Create the folder in this repo (`breakthrough-holo/`) on a new pushed branch (`breakthrough-holo`)
- [x] A2 Write down the goal and a testable definition of "solved" before any results (`GOAL.md`)
- [~] A3 Research Anthropic engineering articles on working with Claude on long research and its environment; turn them into a lab protocol (`WORKFLOW.md`)
- [~] A4 Research how frontier scientists and AI-scientist systems set up research workflows (hypothesis logs, pre-registration, red teams)
- [~] A5 Lab notebook with dated entries (`NOTEBOOK.md`); push often, since the container is ephemeral

## B. Understand the target exactly
- [ ] B1 Break down the Iron Man 1 armor-design scene and the Iron Man 2 lab scenes: size, colors, density, interaction verbs (grab, spin, expand, throw, poke), number of viewers, lighting
- [ ] B2 Turn these into measurable targets: voxel count, luminance, refresh rate, volume, colors, latency (links to GOAL R6–R9)

## C. State of the art (start from the top tier)
- [~] C1 Laser-induced air-plasma volumetric displays: Aerial Burton (2006→), Fairy Lights in Femtoseconds (2016), anything newer (to 2026)
- [~] C2 Particle displays: optical trap display (Smalley 2018→), acoustic MATD (Hirayama 2019→), holographic acoustic tweezers, anything newer
- [~] C3 Mid-air haptics (ultrasound), plasma haptics, haptic gloves
- [~] C4 Fundamental limits of light-field and holographic displays; aerial imaging; nonlinear optics in air; acousto-optics in air (2024 Nature Photonics)
- [~] C5 Safety numbers: IEC 60825-1 MPE (eye and skin; 1.0, 1.55 and 2 µm; ultrashort pulses; repetitive pulses), O₃/NO₂ indoor limits, ultrasound exposure limits, UV (actinic), noise

## D. Theory
- [ ] D1 Prove what physics allows and forbids for "floating, all-angle, no-medium" images (radiance / line-of-sight theorem)
- [ ] D2 Touch-occlusion lemma: which display classes can draw a hologram *in front of* a hand
- [ ] D3 Enumerate every mechanism that can emit or redirect light *at* a point in clean air; rule each in or out quantitatively
- [ ] D4 Derive the governing trade-off for the surviving mechanism(s), e.g. brightness vs air chemistry vs noise vs laser safety

## E. Simulations (each validated against a published number before use)
- [ ] E1 Clean-air scattering bounds: Rayleigh, Raman, χ⁽³⁾ four-wave mixing → power needed
- [ ] E2 Acousto-optic Bragg deflection in air vs ultrasound frequency and attenuation
- [ ] E3 Plasma voxel physics: breakdown threshold vs wavelength, pulse length and NA; voxel size; electron count
- [ ] E4 Plasma light output: fluorescence (cold, fs) and continuum (hot) → photons per voxel → perceived luminance
- [ ] E5 Air chemistry: O₃/NO/NO₂ per voxel → room box model with ventilation and scrubbing → allowed voxel rate
- [ ] E6 Acoustics: blast wave per voxel → pulse train → audible and ultrasonic SPL at the listener, with air absorption
- [ ] E7 Laser safety: beam cones before and after focus, fluence and irradiance vs MPE, interlock margins
- [ ] E8 System: multi-aperture addressing, occlusion by bodies and hands, scheduling, rendering an Iron Man-style model and a video panel within the voxel budget, and what viewers see
- [ ] E9 Alternative engine: particle swarm (acoustic) capacity vs safety, for comparison and hybrid accents
- [ ] E10 Multi-objective optimization over design parameters → Pareto front → chosen operating point

## F. Engineering
- [ ] F1 Architecture of "the projector": source, beam shaping, scanning, focusing, tracking, interlocks, scrubber, glove
- [ ] F2 Bill of materials, power, thermal, size, cost
- [ ] F3 Software stack: content → voxel scheduler → safety kernel → hardware; runnable reference implementation
- [ ] F4 Safety case: hazard analysis (FMEA), standards map
- [ ] F5 Product and startup notes: advertising signage, helmet HUD variant, lab/showroom unit; roadmap and the first prototype a founder can build

## G. Rigor
- [ ] G1 Independent red-team review by separate agents ("ask other models")
- [ ] G2 When stuck: new-idea generation rounds, including ideas not yet tried in the literature
- [ ] G3 Final verdict per requirement (MET / PARTIAL / NOT MET), graded honestly against `GOAL.md`
- [ ] G4 Ping the owner only if solved

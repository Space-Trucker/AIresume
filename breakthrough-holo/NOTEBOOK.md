# Lab notebook: breakthrough-holo

Dated entries: hypothesis → test → result → decision. Newest at the bottom.

---

## 2026-09-30 · Entry 1: Lab opened

- Goal and grading rule fixed in `00_mission/GOAL.md` (R1–R10).
- Task list in `00_mission/TASKS.md`.
- Five parallel literature agents launched:
  - R0 workflow methods
  - R1 air-plasma displays
  - R2 particle, acoustic and haptic displays
  - R3 safety limits
  - R4 film target and display limits
- Starting line of attack (before reading the literature, from first principles): pin down exactly what free-space optics forbids. The owner's constraints (no screen, no fog, no glasses, visible all around, touchable) are very tight, and the first job is to find the physically allowed corner of design space, if there is one.

---

## 2026-09-30 · Entry 2: Theory, first kills, and the real bottleneck

**Theory (T1).**
- Line-of-sight theorem: in clean air, an image point can only be seen along a line of sight that ends on an emitter. A "projector through the air" covers ~0.14 % of 4π.
- Touch lemma: any surface-emitter display (wall, table, plate) is erased by a hand behind the image point.
- Conclusion: in-volume emission is *necessary*.

**E1/E2 (validated: Rayleigh cross-section matches Bucholtz 1995 to 0.04 %; ISO 9613 gives 1.32 dB/m at 40 kHz).** Mechanisms killed:
- Rayleigh (~2 MW per frame, and the glow can't be localised).
- Coherent nonlinear optics (side emission suppressed by 10⁻¹³ to 10⁻⁵¹).
- Incoherent nonlinear scattering (~5 photons per voxel).
- Microwave/THz breakdown (kW-scale RF).
- Acousto-optics (10° deflection needs 112 MHz sound, absorbed within 10 µm).

**Survivor:** laser-induced air plasma. The only grey-zone alternative is projector-supplied particles.

**E3 plasma model** (PPT ionisation plus inverse bremsstrahlung plus depletion). PPT for O₂ at 800 nm is within 2.6× of Couairon's multiphoton fit; the avalanche cross-section matches Couairon's 5.44×10⁻²⁰ cm²; the self-focusing threshold of 3.3 GW matches literature.
- Dense plasma (ne ≈ 2.5×10¹⁹ cm⁻³) forms at ~2–10 µJ with NA 0.1–0.3.
- Absorption is only 1–26 % for sub-ps pulses (the model lacks multiple ionisation, so this is a lower bound).

**Literature (R1): the decisive fact.** Luminous output of *cold* femtosecond plasma is ~10⁻⁵ lm/W (quenched N₂ bands in the UV-violet). *Hot* nanosecond sparks give ~1 lm/W (continuum; 22–34 % of absorbed energy radiated), but 50–80 % of the energy goes into a shock wave (noise), and they make ~10¹⁷ NO per J.

**Target (R4 film analysis).**
- Strokes ~25–180 cd/m² in a 50–150 lux lab.
- 10⁴–10⁵ points per frame; 10⁶–10⁸ voxels/s.
- ~90 % cyan.
- ≤ 35–40 dB(A).

**New framing (hypothesis H1).** For a pure-air display, brightness is capped by *air chemistry* (NO/O₃ per photon) and *noise* (shock energy per photon), not by laser power. Rough estimate:
- Iron Man brightness in a lit lab needs 6–60 lm.
- At ~1 lm/W that is 6–60 W absorbed, i.e. NO production that needs ~10³–10⁴ m³/h of scrubbing.
- Status: probably NOT MET by 10–1000×.

To test H1 quantitatively: E4 (luminous efficacy vs spark size), E5 (room chemistry), E6 (audible noise), E7 (laser safety). In parallel, run an idea round with other models to attack each bottleneck.

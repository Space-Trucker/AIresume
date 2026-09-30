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

---

## 2026-09-30 · Entry 3: Budget model, safety, noise correction, colour, feasibility

**Budget model** (`display_budget.py`), calibrated against literature:
- A 50 mJ ns spark gives 2.1 lm/W (literature 0.7–6) and an acoustic peak at 55 kHz (literature 50–100 kHz).
- Micro-sparks (1–100 µJ) come out at 0.1–0.4 lm/W, because small kernels are quenched by expansion before they radiate.

**E5 air chemistry.**
- The near-field plume at a face 0.5 m away dominates the well-mixed room term.
- Without source capture, even 1 W absorbed gives 64 ppb.
- With a built-in push–pull capture airflow (90 %) and a 900 m³/h scrubber, ≤ 2–3 W absorbed stays ≤ 20 ppb.

**E7 laser safety at 1550 nm.**
- Single-pulse eye hazard zone: 4–16 mm around each focus (IEC-derived, conservative).
- Average exposure elsewhere: ≤ 10 mW/cm², against a 100 mW/cm² limit.
- Hand interlock (22 mm margin) blanks 1.3–4 % of the hologram.
- The plasma's own UV is safe by more than 100×.
- 2 µm is worse than 1550 nm (10× lower MPE).

**E6 / E6b acoustic phase scheduling (new idea).**
- Timing sparks so clicks arrive evenly at tracked ears cuts the DIRECT-field audible noise by 26 dB (sorted, 1 listener) and 35–40 dB (L-BFGS, up to 8 tracked listeners at once).
- Untracked positions are unchanged, and the random-order baseline reproduces the analytic Campbell floor within 0.4 dB.
- **Self-caught error:** I first applied the gain to the total level. Room reflections arrive scrambled, and the reverberant level follows *total radiated* audible power, which timing cannot reduce at 5–20 kHz (radiating modes ≫ free parameters).
- Corrected real-room benefit: 1–10 dB depending on room absorption.
- Path-order drawing is 6–10 dB *worse* (supersonic voxel strings make coherent Mach waves).

**E9 particle swarms (grey zone):** film-scale content needs 30–450 fast beads and 123–142 dB of room ultrasound (public limit 100 dB). Not safe; even a 1–5 bead colour accent gives 114–126 dB.

**E11 colour:** calibration passes to within 0.1 %. The air-plasma palette runs violet → blue-white → white → greenish-white, plus a dim red-pink (H-α and O I in humid air). Film cyan (0.206, 0.262) and orange are outside the gamut.

**E10 feasibility** (Monte Carlo over literature bands; engineered air handling; SAFE means ≤ 50 ppb, ≤ 85 dB(A) and ultrasound ≤ 100 dB):

| Target | P(safe) | Noise | Air |
|---|---|---|---|
| Film-exact, lit lab (50 cd/m², 30k points) | 0.09 | 79 dB(A) | 505 ppb |
| Film density, dim lab (10 cd/m², 10k points) | 0.64 | 64 dB(A) | at the 50 ppb limit |
| **Iron Man style, dim lab (3 cd/m², 5k points)** | **0.95** | 53 dB(A) | 10 ppb |

Quiet (≤ 45 dB(A)) holds only for sparse content or treated rooms.

**Key perceptual point:** in a dim lab (0.5 cd/m² background), 3–4 cd/m² strokes have the film's own contrast ratio (4.5–12× background). The eye adapts, so the film *look* is reproduced in a dark room, just not the absolute brightness of a lit room.

**Decision:** the pure-air plasma engine is the design line. Film-exact quality (lit room, cyan/orange) is graded NOT MET by physics. Still pending: the idea round (3 models) and the red team.

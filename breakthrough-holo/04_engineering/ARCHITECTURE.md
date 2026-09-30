# Aether-1: architecture of an air-plasma hologram projector

> **RED-TEAM STATUS (read first).** This architecture was reviewed adversarially (`05_reviews/red_team_1.md`), and three problems were confirmed:
> 1. §3.2 addressing optics violate étendue (~250×/axis). The E12 redesign is ~4 galvo-tiled heads with 30–50 mm mirrors, NA ≈ 0.03 and 100–160 µJ per voxel; its optics are still to be designed.
> 2. The device is an **open Class 4 laser**. There is no consumer classification route (EN 50689). The only lawful route is a supervised venue installation under variance, with a SIL-3-class interlock.
> 3. The quiet and clean numbers rest on idealisations: noise is 50–58 dB(A) at the user plus the fan; realistic capture is 0.3–0.7; UV is 0.1–5× the limit.
>
> The sections below are kept as the v1 design record. Corrections are marked **[RT]**. Feasibility after correction: `03_simulations/sim_e10b_redteam_corrected.py`.

*Aerial Emissive Three-dimensional Holographic Engine.* A ceiling "halo" projector that draws glowing points in ordinary room air: no fog, no screen, no glasses. The points are visible from every side and can be touched with a glove.

Every number below comes from a simulation in `03_simulations/` or a cited source in `01_research/`. Numbers marked **[EXP]** are the critical unknowns that the first lab experiments must measure (see `ROADMAP.md`).

---

## 1. Operating principle

1. An eye-safe-band (1550 nm) ultrashort pulse is focused to a ~10 µm spot anywhere in a ~1 × 1 × 1.8 m volume.
   - Above ~10¹⁴ W/cm² the air ionises (E3).
   - A hot micro-spark (~5–10 µJ absorbed) emits a flash of bluish-white light in all directions: one **voxel**.
2. About 10⁴ voxels are redrawn 60 times per second, so persistence of vision fuses them into glowing wireframes.
3. Cameras track every person, hand and head.
   - A safety kernel blanks any voxel whose hazard zone could touch skin or eyes (E7).
   - A scheduler times each spark so the clicks reach tracked ears as an even, inaudible stream (E6b).
   - A built-in airflow captures and scrubs the ozone and nitrogen oxides at the source (E5).

---

## 2. Block diagram

```
          ┌────────────────────── CEILING HALO (Ø 1.2 m, 2.7 m height) ──────────────────────┐
          │  3 × OPTICAL HEAD (120° apart)          AIR HANDLER               SENSOR RING      │
          │  ┌────────────────────────────┐        ┌─────────────┐        ┌──────────────────┐ │
 1550 nm  │  │ 4 channels × [AOD-x, AOD-y,│        │ 900 m³/h fan│        │ 6 × ToF depth cam│ │
 fs/ps ───┼─►│ AO-lens z] → 28 cm final   │        │ MnO₂ + KMnO₄│        │ 2 × 60 GHz radar │ │
 source   │  │ asphere (NA≈0.1 @ 1.5 m)   │        │ + carbon    │        │ 240 Hz, ≤5 ms    │ │
 (rack)   │  └────────────────────────────┘        │ O₃/NO₂ ppb  │        └────────┬─────────┘ │
          │        ▲ per-voxel fire/aim            │ sensors     │                 │           │
          └────────┼────────────────────────────── └─────┬───────┘ ────────────────┼───────────┘
                   │                                      │ brightness governor     │ skeletons, ears, eyes
             ┌─────┴──────────────────────────────────────┴─────────────────────────┴───────┐
             │ SAFETY KERNEL (FPGA, redundant)  ←  SCHEDULER (GPU)  ←  CONTENT ENGINE (GPU) │
             │ capsule tests @1 MHz, fast AOM    acoustic phase       3D models → strokes  │
             │ shutter + mech. shutter (<10 ms)  scheduling, energy,  video → dither panel │
             │ watchdog, SIL-2 target            channel assignment   gestures from glove  │
             └───────────────────────────────────────────────────────────────────────────────┘
                                         ▲ BLE (7.5 ms)
                                   ┌─────┴──────┐
                                   │   GLOVE    │ IR markers, 5 fingertip actuators,
                                   │            │ 1550-nm-opaque outer layer
                                   └────────────┘
```

---

## 3. Subsystem specifications

### 3.1 Light engine (laser)

| Parameter | Value | Why |
|---|---|---|
| Wavelength | 1550 nm (Er fibre CPA, or Yb-pumped OPCPA signal) | Corneal/skin MPE ~10³–10⁶ × higher than at 1 µm and no retinal hazard. Hazard zone ≤ 4–16 mm around each focus (E7). 2 µm has a 10× lower MPE than 1550, so 1550 wins. |
| Pulse format | fs seed (≤0.5 µJ, ignition) + 1–3 ps heater (5–30 µJ), or single 0.3–1 ps pulse | fs pulses ignite reliably but absorb little (E3: 1–26 %); ps heating via electron–ion collisions raises absorption and kernel temperature (efficacy) **[EXP]** |
| Energy per voxel | 5–10 µJ absorbed (10–40 µJ incident) | Needed for ~3–5 cd/m² strokes (display_budget) |
| Voxel rate | 0.3–1.0 × 10⁶ /s (pulse on demand) | 5k–15k points per frame at 60 Hz |
| Timing | Pulse picking from a 40 MHz oscillator (25 ns grid) | Acoustic phase scheduling needs arbitrary firing times; the audio band needs only µs accuracy |
| Average power | 20–40 W optical; ~150–250 W electrical | — |

### 3.2 Addressing optics (per head: 4 parallel channels; 12 in the system)

- **x/y:** a pair of TeO₂ acousto-optic deflectors (1550 nm AR-coated), random access in ≤ 10 µs.
- **z:** an acousto-optic lens (counter-chirped AOD pair, as in random-access 3D two-photon microscopes), 20–40 cm focal range.
- **Final optic:** 28 cm aspheric/Fresnel doublet → NA ≈ 0.09–0.12 at 1.3–1.7 m. Spot w₀ ≈ 4–5.5 µm, voxel ~10 µm × 100–200 µm.
- **Channel throughput:** 12 × 50–80 k voxels/s = 0.6–1 M voxels/s.
- **Three heads 120° apart:** if a hand or head blocks one beam path, another head addresses the voxel. The routing is in `holo_engine/kernel.py`, and blanking stays ≤ 4 % with a hand inside the hologram (E7).

### 3.3 Safety kernel (the heart of "safe for everyday use")

- **Exclusion capsules.**
  - Skin margin = single-pulse hazard zone (≤ 10 mm at 20 µJ) + tracking error (5 mm) + latency × speed (5 ms × 1.5 m/s) ≈ **22 mm**.
  - Heads: +150 mm, so no voxel is ever drawn near a face.
- **Path check.** Each voxel's converging cone must clear every capsule for at least one head; otherwise the voxel is blanked.
- **Two independent tracking chains** (depth cameras, radar). Any disagreement or dropout blanks the affected region within one frame.
- **Hardware.**
  - FPGA "last gate" before the AOM.
  - The AOM defaults to off (fail-safe).
  - Mechanical shutter, 10 ms.
  - Laser interlock loop.
- **Average exposure** anywhere outside the capsules: ≤ 10 mW/cm², against a 100 mW/cm² corneal limit (E7).
- **Certification target:** Class 1 during operation by engineering controls (IEC 60825-1), functional safety IEC 61508 SIL 2, FDA variance for a demonstration laser product (US).
  - **[RT]** Not achievable. The accessible beam is Class 4 and presence sensing cannot lower the class.
  - The real route is a venue installation under variance with a trained operator and a SIL-3-class interlock.
  - The kernel must also add a scene depth map, blank any voxel whose post-focus cone meets an unknown or specular object within ~1 m, and apply eye margins to any unrecognised occupant (pets, toddlers).
  - Margins must come from the real NA(z) and energy: 45–90 mm, not 22 mm.

### 3.4 Air handling

- **Push–pull airflow.** An annular laminar curtain descends at 0.2 m/s around the image volume, and a central extraction in the halo captures ≥ 90 % of plasma products at the source.
- **Scrubbing:** 900 m³/h through MnO₂ (ozone catalyst), KMnO₄/alumina (NO → NO₂ capture) and activated carbon (NO₂).
- **Closed loop:** ppb-level O₃/NO₂ sensors at the halo rim. The **brightness governor** caps absorbed power so the breathing-zone increment stays ≤ 20 ppb. The allowance is ~2–3 W absorbed with capture on, against 0.3 W without (E5).

### 3.5 Quiet drawing: subsonic multi-channel tracing (primary) + listener phase locking (optional)

- **Primary (E6c): subsonic pens.** Each of the K = 12–24 channels owns a set of strokes and traces them back to back.
  - Regular click train at 25–40 kHz, i.e. above hearing.
  - 3 mm pitch, trace speed 75–120 m/s (Mach 0.22–0.35).
  - 4-voxel energy ramps at stroke ends.
- **Physics:** a steady source moving slower than sound radiates no audio except at ends, turns and jumps.
- **Result: total radiated audible power −19.5 to −26.5 dB in *all* directions**, so the room's reverberant field drops too. Worst direction −14.5 to −19.5 dB.
- **Counter-example:** drawing with one supersonic beam (Mach 3) is +7.6 dB louder, from Mach-wave booms.
- **Optional (E6b): listener phase locking.** Small firing-time shifts make clicks arrive evenly at up to 8 tracked ears: −35 to −40 dB in the *direct* field only.
  - Reflections are not controlled, so the real-room benefit is 1–10 dB on top.
  - Not yet co-optimised with subsonic tracing.
- **Operating point:** 40–44 dB(A) at 1 m in a normal room for 5–9 m of strokes (E10). That is hearing-safe (limit 85 dB(A)) and a quiet-office level, not bedroom-quiet.

### 3.6 Glove (the only thing the user wears)

- Thin knit glove, 10 IR-retroreflective markers (sub-mm tracking), 5 fingertip voice-coil or piezo actuators.
- BLE LE isochronous link, ≤ 7.5 ms.
- **[RT]** The outer layer must be *diffuse and absorbing* (carbon-loaded), not aluminised. A cupped reflective glove can re-collimate a voxel's transmitted beam above MPE across the room (red team #12).
- **Touch** is computed against the *virtual geometry*, not the lit voxels: the interlock blanks voxels within 22 mm of the hand, but the finger still "feels" the surface (`holo_engine/demo.py`).
- **Gestures:** pinch/grab to move, two-hand spread to scale, flick to throw away, poke for buttons. These are the film's interactions (R4 DR-12).
- **Conformal emitters (optional, idea round):** a sparse grid of flexible micro-LEDs in the glove shows hologram content that lies *on* the hand, such as the film's gauntlet scene. A surface point emitting isotropically is correct for every viewer. The glove is also the one place where the film's **orange accents** can appear.
- **Known perceptual artefact:** ns point flashes smear into "phantom arrays" during eye saccades, as with PWM LEDs. Splitting each point into 2–4 sub-flashes per frame reduces it, at some cost in efficacy.

### 3.6b Room setting (part of the product spec)

- **Dim room:** background ≲ 0.5–2 cd/m² (≈ 2–10 lux).
  - Strokes of 3–10 cd/m² then have the film's own contrast ratio (4.5–12× background, R4).
- **Warm (2700–3000 K) room lighting.**
  - After chromatic adaptation, the plasma's bluish-white continuum is *seen* as saturated azure: hue 202–213°, against the film's cyan at 181–199° (E11, Bradford model).
  - The film's workshop is itself warm-lit.
- **Stroke budget (brightness × length), from air chemistry and noise:**

  | Air limit | Stroke length | Luminance |
  |---|---|---|
  | Strict (≤ 13 ppb, P = 0.75) | ~5 m | 3 cd/m² |
  | Lenient (≤ 50 ppb, P = 0.82) | ~9 m | 4 cd/m² |

  For comparison, a life-size armor silhouette is ~9–15 m.
  - `content.fit_to_budget` picks strokes by priority: silhouettes → small features → contour slices.

### 3.7 Content engine (`holo_engine/`, runnable)

- **3D models:** feature edges plus contour slices, the Iron Man look (`content.py`).
- **Video:** ordered-dither panel. The budget allows roughly 96 × 54 "pixel" panels.
- **Per frame:**
  1. Energy allocation.
  2. Safety gate.
  3. Acoustic phase schedule.
  4. Channel packing.
  5. Laser/AOD command stream.

---

## 4. Power, size, cost (prototype)

| Item | Estimate |
|---|---|
| Electrical power | ~0.5 kW (laser 200 W, compute 100 W, air 80 W, other 100 W) |
| Ceiling halo | Ø 1.2 m, 25 cm deep, ~35 kg; laser source in a 19" rack (or a 2nd-generation integrated head) |
| Prototype BOM | ≈ $300k–450k. The 30 W 1550 nm ultrafast source is 50–70 % of it. |
| Volume-product BOM target | $20k–50k. Mainly a 1550 nm fibre-laser cost-down, as happened with LIDAR. |

---

## 5. Capability versus the film (details in `05_reviews/FINAL_VERDICT.md`)

**Achievable (E10 Monte Carlo over literature uncertainty):**
- Life-size, all-around-visible, glove-touchable **azure wireframe** holograms (warm-lit room) with **5–9 m of glowing strokes** (2.5k–4.5k points at 2 mm pitch) at 60 Hz, in a dim room.
- About 40–44 dB(A); P(safe) 0.58–0.96 depending on the air criterion.
- 3D models, animations, UI glyphs.
- Low-resolution monochrome video panels.

**Not achievable in air without an added medium:**
- The film's brightness in a lit room.
- 10⁵-point density.
- Cyan/orange colour.

These are ruled out by the light–chemistry–noise trilemma (T2).

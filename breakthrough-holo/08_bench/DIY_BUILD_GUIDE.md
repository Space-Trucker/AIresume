# DIY build guide: from a bench measurement to a glowing glyph in mid-air

**Audience.** A private builder buying parts online (Amazon, AliExpress, Alibaba, eBay) plus a few safety-critical items from specialist vendors.

**Scope, honestly.**
- **Buildable:** the experiments that decide whether the MOTE route works (DIY-1), and a working miniature optical-trap display: one particle drawing a 1–2 cm glowing glyph in air inside a box. This is the physics BYU published in *Nature* (2018), at hobby scale (DIY-2/3).
- **Not buildable this way:** the room-scale Iron-Man system. It needs thousands of steered beams and a mote material that does not exist yet (`05_reviews/FINAL_VERDICT.md`).

**Sourcing.** Part numbers, price ranges and red flags are in `R11_sourcing.md`. This guide covers the engineering and procedures.

---

## DIY-0. Safety kit: build this first, or build nothing

The lasers used here are **Class 3B/4**. A 405/445 nm beam of 100 mW or more can permanently blind in milliseconds, **including from a reflection**, and many online laser modules are under- or over-labelled.

| Item | Requirement | Why |
|---|---|---|
| Laser safety goggles | Certified **EN 207** (or ANSI Z136) marking with **OD ≥ 4** (better 5+) at your exact wavelength(s). From a reputable laser-safety vendor, not a no-name listing | Fake or uncertified goggles are common online and can transmit the beam |
| Opaque enclosure around the whole beam path | Aluminium extrusion (2020/2040) frame with opaque panels. Viewing window only in **certified laser-safety acrylic** rated OD ≥ 4 at the wavelength | You watch through a camera or the window, never along the beam |
| Lid interlock | Microswitch on the lid, wired **in hardware** in series with the laser driver's enable or supply, so opening the lid kills the laser. Plus a **key switch** and a **mushroom E-stop** | Software is not a safety device |
| Beam dump | Black anodised aluminium or ceramic absorber at the end of every beam | No beam ever reaches a wall |
| Thermal power meter | Know your real power; online modules are often mislabelled | Needed for the physics too |
| Particle handling | Particles stay **sealed** (capped cuvette) or inside the closed enclosure. Wear a P100/FFP3 mask when handling dry powders. **No nanopowders (ITO etc.) outside a glovebox** | 1–10 µm particles are respirable |
| Local rules | Check your country's rules on owning Class 3B/4 lasers. Some restrict or ban them | Legal |

**Working rules.**
- Align at the lowest current the driver allows, with goggles on.
- Raise power only with the lid closed.
- No reflective jewellery or tools near the beam.
- Never be alone with an open Class 4 beam.

---

## DIY-1. Photophoretic velocimetry: measures the force law (gate G1)

**What it settles.** Whether the photophoretic force per absorbed watt matches the model (C_ph ≈ 0.67–1.04) and its 1/(k_p + 2k_g) conductivity dependence. Every MOTE number rests on this.

**Layout (side view).**
```
 [445 nm module] --> [iris] --> [optional 2x expander] --> | cuvette (sealed, particles) | --> [beam dump]
                                                                 ^ camera (90 deg, macro lens,
                                                                   long-pass/notch filter, dim red LED side light)
```

**Design numbers** (`diy_calcs.py`, our validated model):
- **Intensity:** a 1.5 W, 445 nm beam ~4 mm across gives ~10 W/cm². That is enough. Particle heating is only 2–6 K, so nothing melts.
- **Predicted drift along the beam:**

  | Particle | Drift | Notes |
  |---|---|---|
  | Carbon-coated hollow glass (d ≈ 5 µm) | ~10 mm/s | **Best reference** |
  | Glassy carbon (d ≈ 5 µm) | ~0.23 mm/s | High conductivity, so 40× slower. **This contrast tests the law** |
  | Laser-printer toner | ~3.4 mm/s | Cheap first test |

- **Camera:** ~3 µm/px. Keep motion ≤ 5 px per frame, which needs 80–700 fps depending on the particle. A phone's 240 fps slow-motion with a clip-on macro lens is enough for toner and glassy carbon. A global-shutter machine-vision camera with a cropped region of interest is better.
- **Filters:** block the 445 nm scatter from the sensor (long-pass/notch). Track particles by a dim **red LED** side-light, so tracking works with the beam on or off.

**Procedure.** Same as `BENCH_PLAN.md` B1:
- beam-off reference;
- three powers;
- reverse the direction;
- white silica tracer spheres for convection;
- record the beam-centre height.

Then run `track_b1.py`, then `analyze_b1.py`. Both are self-tested.

**Gate G1.** Implied C_ph within 0.5–1.3 for the skin-absorbing spheres, and a glassy-carbon / hollow-sphere drift ratio within ×2 of the model.

---

## DIY-2. Miniature optical-trap display: one particle draws a glyph (BYU replication)

**Layout (top view).**
```
 [405 nm diode, adjustable current] --> [collimator] --> [galvo X] --> [galvo Y] --> [lens f = 100-150 mm] --> trap
        (single-mode 20-120 mW, or multimode 0.3-1 W)                                    (focus inside the box)
 [illumination: cyan/RGB laser or LED, co-aligned via a dichroic, or a flood from the side] --> lights the particle
```

**How the trap works.** A tightly focused beam with *deliberate aberration* creates a dark pocket surrounded by light. An absorbing particle drifts into it and is held there by photophoresis (R5, R8).
- BYU used 405 nm, f = 125 mm and 30 mm galvos, with spherical aberration plus astigmatism.
- Try a cheap plano-convex singlet used **backwards** (flat side toward the beam) for extra spherical aberration, and/or tilt it slightly for astigmatism.

**Design numbers** (`diy_calcs.py`):
- **Particle choice dominates.**
  - **Carbon-coated hollow glass microspheres:** safe power window ~3 000×, top speed ~0.6 m/s.
  - **Toner / black polymer spheres:** trap, but melt above ~150 °C, which limits speed to ~0.05 m/s.
  - **Dense LED-phosphor grains cannot be trapped.** They burn before they lift.
- **Power.** The model needs only µW–mW absorbed. BYU's rigs needed 18–24 mW of trap light to hold particles reliably, because the trap geometry, not the force, is limiting. **Start at ~10–20 mW and increase slowly.** Too much power burns particles.
- **Drawing.**
  - One particle at speed v draws v/f metres of line per frame.
  - At 0.5 m/s: a ~1.6 cm circle at 10 Hz, or ~0.5 cm at 30 Hz.
  - At BYU's best 1.8 m/s: ~1.9 cm at 30 Hz.
  - **Expect 1–2 cm glyphs at 10–20 Hz**, with visible flicker. That matches BYU.
- **Galvos.** Hobby laser-show (ILDA) galvos easily drive 10–30 Hz shapes. The field is about ±(f · θ). With f = 100 mm and ±10° mechanical (±20° optical), that is ≈ ±35 mm, far more than needed.
- **Loading particles.** A gentle puff from a syringe or a vibrating sieve above the focus. Particles fall through and one gets caught; others settle.

**Control software** (`diy2_control/`):
- `path_gen.py` (self-tested): circle, lissajous, heart, star.
  - Constant speed, or `--variable_speed` (slows in tight curves to ≤ 5 g, with brightness compensation).
  - Outputs a CSV and a C header.
- `helios_stream.py`: streams to a USB ILDA DAC. The simplest route; untested on hardware.
- `galvo_esp32/galvo_esp32.ino`: ESP32 + MCP4922 12-bit DAC, with an interlock input. Untested on hardware; needs a level shifter to ±5/±10 V for the galvo driver.
- **Test galvo code with the trap laser OFF.**

**Milestones.**
1. Trap one particle and hold it for a minute.
2. Move it slowly (1 mm/s) with the galvos.
3. Raise the speed until it is lost; **record max speed against trap power**. No such curve has been published (R8 gap), so this is real new data.
4. Draw a 1 cm circle, then a heart (`--variable_speed`).
5. Light it cyan.

---

## DIY-3. Self-glowing trapped particle (towards the MOTE "glowing mote")

**What the model says works:**
- **Fluorescent polymer microspheres** (dye absorbing 405 nm) trap at low power; the window is ~7×. They glow under the trap beam itself but bleach in minutes. Good for a first "self-luminous" demo.
- **Dense phosphor grains do not trap** (above).

The real MOTE mote (aerogel plus ITO island skin plus phosphor) is bench item B2. It needs a chemistry lab: layer-by-layer nanoparticle coating and a Stöber silica overcoat. It is not a DIY purchase.

**Practical colour today.** Use BYU's approach: trap a black particle and light it with a co-aligned **cyan** laser or LED. It scatters Iron-Man blue.

---

## DIY-4. 1550 nm opposed-pair trap at room distance (bench B3)

This is the first step toward the MOTE architecture: an eye-safer wavelength, two heads facing each other, 1–1.5 m apart.

**Hardware:**
- a 1550 nm DFB seed plus an erbium fibre amplifier (EDFA, 1–5 W), split in two;
- fibre collimators;
- **optical isolators**, so each head's beam cannot feed back into the other's amplifier;
- vortex (LG01) phase plates;
- 100–150 mm lenses.

**Safety:**
- 1550 nm is invisible, so use IR viewer cards.
- 1550 nm goggles.
- Fully enclosed beam path.
- **Respirable test motes stay in a closed, HEPA-bled enclosure.**

**Expect a higher budget** (~$5–20k; see R11) and alignment skill.

---

## What success means

| Stage | Done when | Feeds |
|---|---|---|
| DIY-1 | Measured C_ph and the k-dependence | `budget2.py` C_ph; verdict re-grade |
| DIY-2 | 1–2 cm glyph drawn in air; max-speed vs power curve | Validates the trap model at BYU scale; new data |
| DIY-3 | A self-glowing particle drawing a glyph | First "glowing mote" |
| DIY-4 | A mote held between two 1550 nm heads at ≥ 1 m | Gate G3, the MOTE architecture |

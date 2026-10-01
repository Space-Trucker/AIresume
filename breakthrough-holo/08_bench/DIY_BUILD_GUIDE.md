# DIY build guide: from a bench measurement to a glowing glyph in mid-air

**Audience.** A private builder buying parts online (Amazon, AliExpress, Alibaba, eBay), plus a few safety-critical items from specialist vendors.

**Scope, honestly.**
- **Buildable:**
  - the experiments that decide whether the MOTE route works (DIY-1);
  - a miniature optical-trap display, in which one particle draws a 1–2 cm glowing glyph in air inside a box. This is the physics BYU published in *Nature* (2018), at hobby scale (DIY-2/3).
- **Not buildable this way:** the room-scale Iron-Man system. It needs thousands of steered beams and a mote material that does not exist yet (`05_reviews/FINAL_VERDICT.md`).
- **Nobody has published a hobbyist build of a working photophoretic trap display** (R11 §10). The closest are BYU's low-cost JoVE rig and Cal Poly student builds. You would be among the first, and your measurements would be new data.

**Companion files.**

| File | What it gives you |
|---|---|
| `R11_sourcing.md` | Part numbers, prices, search keywords, red flags, legal notes and full BOM tables (§14). Every price is a search snapshot (±30 %); check before ordering. Validation notes are at the top |
| `diy_calcs.py` | Particle speeds, trap power windows, camera frame rates |
| `sim_d1_lens_trap.py` | Which lens, beam size and orientation make a trap pocket (21 self-tests) |
| `diy2_control/` | Path generator, Helios and ESP32 drivers, `ELECTRONICS.md` (interlock and galvo circuit), `autotrap.py` (automatic trap tester) |
| `ORDER_LIST.md` | **What to put in the cart**: three orders (safety kit, DIY-1, DIY-2) with picks, quantities and prices |

---

## Shopping plan at a glance

| Stage | You get | Cost (USD, R11 estimates) | Buy from specialists |
|---|---|---|---|
| **DIY-0 safety kit** | Eyewear, enclosure, interlock, dump, power meter | ~$750–1,650 (included in DIY-1 totals) | Eyewear, meter, dump, interlock parts |
| **DIY-1 velocimetry** | The force law measured (gate G1) | **$1.4–2.0k** budget / **$2.6–3.6k** recommended, including DIY-0 | Reference particles, camera |
| **DIY-2 trap display** | A particle held in air, then a 1–2 cm glyph | **+$0.6–1.5k** (reuses DIY-1 parts) | Trap lens |
| DIY-2c retro beam (optional) | Return beam for spheres (new experiment) | +$0.3–0.9k [estimate, not sourced] | Corner cube, PBS, quarter-wave plate |
| **DIY-3 glowing particles** | Phosphor and fluorescent screening | +$0.3–1.2k | – |
| **DIY-4 1550 nm pair** | MOTE trap physics at 1–1.5 m (gate G3) | **$7–11k** (1 W) / **$10–17k** (5 W) | All fibre parts, vortex plates |

**Order of purchase:** DIY-0 first, all of it, before any laser is powered. Then DIY-1, then DIY-2. DIY-4 only after G1 passes.

---

## DIY-0. Safety kit: build this first, or build nothing

The lasers here are **Class 3B/4**. A 405/445 nm beam of 100 mW or more can permanently blind in milliseconds, **including from a reflection**. Many online laser modules are mislabelled: engraver "20 W/40 W" ratings are *electrical*; the optical output is about 5 W (R11 §1.4).

| Item | Requirement | Example (R11) |
|---|---|---|
| **Laser safety eyewear** (one pair per person plus a guest pair) | **EN 207** with a test-house mark, or ANSI Z136 with a published transmission curve. **OD ≥ 5 (LB5)** at every wavelength in use. The **LB rating must cover your maximum power**, not just the OD | Thorlabs **LG3**: OD 7+ at 180–532 nm, $191. Its LB rating limits use to about 1 W CW at 532 nm, so check the rating at your wavelength and power. LaserVision F18 ($69–259). Not LG9: it misses 405 and 1550 nm |
| **Viewing eyewear for DIY-2** | OD ≥ 5 from ~395 to ≥ 415 nm with **high visible transmission**, so you see the lit particle | Yellow "190–420/450 nm" filters from the same makers |
| **Opaque enclosure** around the whole beam path | 2020/2040 aluminium extrusion with opaque panels. A viewing window only in **certified** laser-safety material (EN 207 / EN 12254) at your wavelength. **Orange engraver-lid acrylic is not certified** | Extrusion $30–80; panels local |
| **Hardware interlock** | Lid switches, key switch, E-stop and a manual-reset safety relay that **removes laser-driver power**. Software is not a safety device. **Full design: `diy2_control/ELECTRONICS.md` §1** | Safety relay (Pilz/Omron/Phoenix class) $80–250; coded-magnet or tongue safety switches; total $100–350 |
| **Beam dump** at the end of every beam | **Rated** dump. **Black-anodised aluminium is not a dump in the near-IR** (it reflects ~66 %) and its dye bleaches at W-level blue | Thorlabs **LB1**: $63, 400 nm–2 µm, 10 W |
| **Thermal power meter** | Thermopile, ≥ 3 W, aperture ≥ 10 mm, known calibration. Online modules are often mislabelled, and the physics needs real watts | Used Ophir 3A head ($199–262) plus Nova/Juno display ($300–500); or Thorlabs PM16-405/-425 ($1,343). A $120 marketplace meter is for relative checks only |
| **Particle handling** | Particles stay **sealed** (capped cuvette) or inside the closed enclosure. P100/FFP3 mask and nitrile gloves when handling powders. **No nanopowders (ITO etc.) outside a glovebox** | $60–400 including a closed box with a HEPA bleed |
| **Local rules** | Check them first (R11 §11). For example: in the US, a laser display **shown to others** above Class IIIa needs an FDA variance; Australia treats handheld lasers > 1 mW as prohibited weapons; Switzerland bans laser pointers above Class 1 | Buy mains-powered, non-handheld modules with class labels, and keep invoices |

**Working rules.**
- Align at the lowest current the driver allows, with eyewear on.
- Raise power only with the lid closed.
- No reflective jewellery or tools near the beam.
- Never be alone with an open Class 4 beam.
- Test the interlock before every session (`ELECTRONICS.md` §1).

---

## DIY-1. Photophoretic velocimetry: measures the force law (gate G1)

**What it settles.** Whether the photophoretic force per absorbed watt matches the model (C_ph ≈ 0.67–1.04) and its 1/(k_p + 2k_g) conductivity dependence. Every MOTE number rests on this.

**Layout (side view).**
```
 [445 nm module + driver] --> [iris] --> [expander] --> | cuvette (sealed, particles) | --> [beam dump]
                                                               ^ camera (90 deg, macro/telecentric lens,
                                                                 long-pass/notch filter, dim red LED side light)
```

**Laser.**
- Use a **single-emitter** diode with a glass lens, such as a Nichia NDB7875 445 nm 1.6–2 W in a copper module ($65–96), plus a separate **constant-current** driver with TTL and soft start ($15–45).
- **Not an engraver head.** Those combine 2–4 emitters into a tiny focused spot and cannot give a clean collimated beam.
- **Power sizing** (peak I₀ = 2P/πw²):
  - 10 W/cm² needs **0.63 W** in a 4 mm (1/e² diameter) beam.
  - **Keep the optical power within your eyewear's LB rating.** LG3-class eyewear covers ~1 W CW, so run ≤ 1 W.
  - At 1 W you get 16 W/cm² at 4 mm, 64 W/cm² at 2 mm and ~250 W/cm² at 1 mm.
  - For the hot end of the power series (mote heating ~50–100 K), **tighten the beam rather than adding power**. `analyze_b1.py` normalises each track to its local Gaussian intensity.
- **Profile the beam.** Its radius enters squared, so a 10 % radius error is a 20 % force error. A razor knife-edge on a micrometer stage, plus the power meter, is enough (R11 §6.4).

**Particles** (R11 §5; the predictions come from `diy_calcs.py`):

| Particle | Role | Predicted drift at 10 W/cm² | Buy |
|---|---|---|---|
| **Glassy carbon** spheres 2–12 µm (k_p ≈ 6) | Skin absorber, high k: the force-law reference | 0.23 mm/s (settling 1.2 mm/s) | Thermo 038008 ($72 / 10 g), SPI Sigradur K; Sigma 484164 ships to businesses only |
| **Black polymer** spheres ≥ 10 µm (k_p ≈ 0.2–0.3) | Low k: the contrast partner. Volume absorber, so give `analyze_b1.py` its J₁/A | ~3.4 mm/s | Cospheric BKPMS black PE ($142+) |
| **White silica** spheres ~5 µm | Non-absorbing tracers that measure convection | 0 (convection only) | Cospheric ($224–367), Whitehouse (from £70) |
| Toner | **Practice only.** Wax binder softens at ~50–65 °C | ~3.4 mm/s | Any refill bottle |
| ~~Carbon-coated hollow glass~~ | Would be the best low-k skin absorber (10 mm/s), but **it is not a stock item**. It is a chemistry-lab job (bench B2) | – | – |

Measure the size distribution yourself under a microscope with a stage micrometer: a stated range such as "0.4–12 µm" is not a distribution.

**Camera.**
- Keep motion ≤ 5 px per frame: 80–700 fps at ~3 µm/px, depending on the particle.
- **Best value:** Basler acA720-520um, 525 fps global shutter, $379–436 (validated). Pair it with a 1×/2× telecentric C-mount lens ($166–176 on AliExpress, or Edmund $645).
- **Budget:** Raspberry Pi Global Shutter camera with a cropped region of interest.
- **A phone's 240 fps slow-motion is qualitative only:** rolling shutter, compression and auto-exposure.
- Verify the frame interval by filming an LED blinking at a known rate.

**Procedure.** Same as `BENCH_PLAN.md` B1:
- a beam-off reference;
- three powers, covering mote heating from ~2 K to 100+ K;
- reverse the beam direction;
- silica tracers present;
- record the beam-centre height.

Then run `track_b1.py`, then `analyze_b1.py`. Both are self-tested.

**Gate G1.** Implied C_ph within 0.5–1.3 for glassy carbon, and a glassy-carbon / black-polymer drift ratio within ×2 of the model, with the polymer's J₁/A as an input.

---

## DIY-2. Miniature optical-trap display (BYU replication, with a new twist)

### What the new trap-optics simulation says (`sim_d1_lens_trap.py`, 2026-10-01)

I ray-traced a real catalogue lens (Thorlabs LA1509-A, f = 100 mm) and computed the 3D light field around its focus with diffraction. Then I computed how much light a 5–8 µm particle would intercept at each position. The 21 self-tests include textbook Airy and vortex results, energy conservation and the known ~4× extra aberration of a backwards lens.

1. **A cheap lens mounted backwards (flat side toward the beam) makes a real trap pocket.** Its depth depends sharply on beam size:

   | Beam 1/e² radius | Spherical aberration (waves at the 1 % radius) | Pocket contrast, 5 µm particle | Pocket contrast, 8 µm particle |
   |---|---|---|---|
   | 2.5 mm | 0.6 | 2.7 | none |
   | **3 mm (6 mm beam)** | **1.2** | **≈ 21 (best)** | 3.0 |
   | 3.5 mm | 2.3 | 12 | 3.9 |
   | 4 mm | 3.8 | 7 | 3.3 |
   | 6 mm | 19 | 1.6 | 1.7 |

   Contrast is the light at the pocket wall divided by the light at its centre. The sweet spot is about **1–2 waves** of spherical aberration. The pocket is ~6 µm in radius, so particles of ≤ 5 µm feel it best. The normal orientation (curved side first) gives almost no pocket at these beam sizes. **A 6 mm beam also fits standard 7 mm galvo mirrors.** Diode beams are not clean Gaussians, so treat 6 mm as the starting point and tune the beam size with an iris while watching the capture rate.

2. **But a smooth sphere held up by gravity alone is slow.** In one upward beam the push must equal the particle's weight, so the beam power only sets its height. The sideways force it can take is then η × (contrast − 1) × its weight, and its top drawing speed is that factor times its settling speed:
   - **≈ 1–20 mm/s** with a lens pocket or even an ideal $850+ vortex plate (contrast 20–80);
   - a 1 cm glyph at 10 Hz needs **~0.3 m/s**. With a vortex plate that would take 13–56 W of 405 nm, which is impractical and unsafe.
3. **BYU's traps reach 1.8 m/s because they are not gravity-balanced.** Their traps work the same at 0 g and 2 g (Peatross 2018), and they use **irregular** particles: cellulose "black liquor", soot. Some shape-dependent or still-unexplained force (R8 §1.1) holds them along the beam. So **for a display, use BYU-type irregular black particles, not smooth spheres.** Our sphere model cannot predict their speed; your measurement will.
4. **New idea for spheres: a return beam.** If a second beam pushes back along the axis, the particle no longer has to balance its weight, and the sideways force can rise toward the particle's burn limit:
   - toward ~0.5–0.6 m/s for low-k skin absorbers;
   - ~0.25 m/s estimated for activated-charcoal grains, whose properties are estimated, not measured.

   A collimating lens plus a **corner-cube retroreflector** at that lens's back focal plane sends the beam back onto the **same trap point wherever the galvos move it**. A plain mirror would not, because it images the point to the opposite side. Cal Poly's simple retro-reflector already gave 3× longer trapping (R11 §10). This is stage DIY-2c.

These are registered as predictions P27–P30 (`07_mote_route/PREDICTIONS.md`, Addendum B) **before** any measurement.

### Layout

```
 [405 nm diode + driver] --> [expander to 6 mm (1/e^2)] --> [galvo X] --> [galvo Y] --> [LA1509 f=100, FLAT SIDE FIRST] --> trap
       (0.1-1 W, TTL + analog; R11 S1)                       (mirrors coated for 405 nm)           (focus inside the box)
 [illumination: cyan/RGB laser or LED, combined by a dichroic, or a side flood] --> lights the particle
 Beam vertical (pointing UP) for DIY-2a; best pocket ~0.8 mm before the paraxial focus; rated dump above
```

### DIY-2a: static trap first (no galvos)

This follows BYU's JoVE rig: laser-cut wood, a 30 mm lens holder, and an electromagnet "tapper" that drops particles through the focus.
1. Find which particles trap. Run many drops per particle type and log the capture rate. BYU's screen found printer toner trapped ~10 % of the time.
2. Measure hold time against power. Start at ~10–20 mW and raise slowly. BYU's lowest successful trap was 18 mW (minimum hold < 24 mW); too much power burns particles.
3. Measure top speed: move the lens with a stage, or use the galvos once fitted, until the particle is lost. **No published max-speed-vs-power curve exists (R8 gap), so this is new data.**

**Particles to screen:**
- **Irregular:** activated charcoal (food grade, sediment it in IPA to get the < 10 µm fraction); candle soot scraped from glass; graphite powder; carbon black; nigrosin; toner.
- **Spheres, as the control:** glassy carbon, black PE.

Use a 405 nm-blocking camera filter and long exposures to photograph traps.

**Automate it** (`diy2_control/autotrap.py`, self-tested on a simulated rig; firmware `autotrap_esp32/` is untested on hardware):
- the ESP32 sets the laser power, enables it and pulses the tapper;
- the camera decides capture from a spot that persists, so falling particles are rejected, and measures hold time;
- output: capture probability with 95 % intervals and median hold time against power, ~200+ trials an hour, like BYU's rig.

It polls the interlock every second, refuses powers above `--max_mW` or outside the meter calibration, and always leaves the laser off. It is still not a safety device: the hardware interlock is.

### DIY-2b: drawing (BYU replication)

- **Galvos.** A hobby ILDA set ($95–210) is fine. The particle, not the galvo, limits speed (R11 §7.1). Choose on:
  - mirror ≥ 7 mm, ideally 10 mm;
  - a coating that reflects at 405 nm (ask for the curve; silver is poor at 405 nm);
  - low overshoot.
- **DAC.**
  - **Helios** ($99–114): **12-bit**, ≤ 4095 points per frame (validated). Turn the galvo driver's size trim down so the 1–2 cm field uses most of the range, giving about 6 µm per step instead of 18.
  - Or the ESP32 + MCP4922 board in `ELECTRONICS.md` §2.
  - A 16-bit DAC (HeliosPRO, DAC8562) removes the trim step.
- **Software** (`diy2_control/`):
  - `path_gen.py`: shapes, constant or variable speed, brightness compensation;
  - `helios_stream.py`;
  - `galvo_esp32.ino`.

  Hardware code is untested. Test it with the trap laser OFF.
- **Drawing numbers.** One particle at speed v draws v/f metres of line per frame:

  | Speed | 10 Hz | 30 Hz |
  |---|---|---|
  | 0.5 m/s | ~1.6 cm circle | ~0.5 cm circle |
  | 1.8 m/s (BYU's best) | – | ~1.9 cm circle |

  **Expect 1–2 cm glyphs at 10–20 Hz** with visible flicker, as BYU's are.

**Milestones.**
1. Hold one particle for a minute.
2. Move it at 1 mm/s.
3. Raise the speed until it is lost; record max speed against power.
4. Draw a 1 cm circle, then a heart (`--variable_speed`).
5. Light it cyan.

### DIY-2c (optional): retro-beam trap for spheres

This is a new experiment, so the parts cost is an estimate (+$0.3–0.9k).

```
 laser --> [PBS] --> [quarter-wave] --> galvos (at L1's front focal plane) --> L1 (backwards) --> trap
                                                                               --> L2 (f, one f past the trap)
                                                                               --> corner cube (vertex at L2's back focal plane)
 The return beam re-focuses on the trap point at every galvo position. PBS + quarter-wave send most of it into a dump
 before it reaches the diode.
```

- **Corner cube:** use a metal-coated hollow one, which preserves polarisation better.
- **Axial stiffness:** move L2 a fraction of a millimetre so the return focus sits just beyond the trap point.
- **Feedback into the diode:** isolation is only partial, because the galvo mirrors and cube change polarisation. Measure the power at the PBS dump port. If feedback destabilises the diode, add a 405 nm Faraday isolator (~$1k+, estimate).
- **Safety:** retro-reflected beams travel back along the path. Keep everything enclosed.
- **Test (P29):** do spheres get ≥ 5× faster, and do they trap with the beam horizontal?

---

## DIY-3. Self-glowing trapped particle (towards the MOTE "glowing mote")

**Model results:**
- **Fluorescent polymer microspheres** trap, but their window is narrow: ×5 now that the PS softening point (~100 °C) is used. Cospheric FM spheres ($148 / 500 mg) are amino-formaldehyde, which tolerates more heat, but **405 nm excitation is unconfirmed**. Test a sample first.
- **Dense phosphor grains do not trap.** They are heavy and conduct heat.

**Screening kit** (R11 §9):
- cyan BaSi₂O₂N₂:Eu (Stanford Advanced Materials from $100, D50 15 µm: sediment out the fine fraction);
- nitride red ($50 / 5 g);
- a **true 405 nm** LED (many "UV" torches are 395 nm);
- long-pass filters;
- optionally a USB spectrometer to confirm what marketplace powders really are.

**Practical colour today.** Use BYU's approach: trap a black particle and light it with a co-aligned **cyan** laser or LED. It scatters Iron-Man blue.

The real MOTE mote (aerogel plus ITO island skin plus phosphor) is bench item B2. It needs a chemistry lab and is not a DIY purchase.

---

## DIY-4. 1550 nm opposed-pair trap at room distance (bench B3)

This is the first step toward the MOTE architecture: an eye-safer wavelength, two heads facing each other, 1–1.5 m apart. Do it only after G1 passes.

**Hardware** (R11 §8):
- **Seed:** a 1550 nm DFB butterfly with isolator ($620+), or a broad Fabry–Perot test source ($189) if the EDFA accepts it. A broad source also suppresses stimulated Brillouin scattering.
- **Amplifier:** a **single-port** EDFA, about $2.3k for 1 W or $4.3–5.9k for 5 W. **Marketplace "EDFAs" are mostly cable-TV multi-port units:** the headline power is split over 8–32 outputs.
- **Splitter:** a 50:50 coupler rated above the amplifier power.
- **Isolators:** ≥ 2–5 W rated, one per head ($164–399).
- **Fibre parts:** power-rated collimators. Standard connectors are rated only ~0.5 W, so splice at the high-power end.
- **Vortex plates:** **spiral phase plates** (Zoko SPP-1550, $846 each). Avoid polarisation-dependent retarders in a non-PM fibre chain.
- **Final lenses:** **Ø100–150 mm aperture**, f ≈ 1–1.5 m, NA ≈ 0.03–0.05, NIR anti-reflection coated (~$325 each for Ø100 mm). The aperture is the point; Ø100 mm condensers with f ≈ 150 mm are the wrong part.

**Safety:**
- 1550 nm is invisible, and silicon cameras and cheap IR viewers cannot see it. Use VRC2/VRC4 cards ($101).
- Eyewear: Thorlabs LG11 ($430).
- Rated dumps (LB1). Black-anodised parts reflect at 1550 nm.
- A fully enclosed path.
- **Respirable test motes stay in a closed, HEPA-bled enclosure.**

**Budget:** $7–11k with a 1 W amplifier, $10–17k with 5 W.

---

## What success means

| Stage | Done when | Feeds |
|---|---|---|
| DIY-1 | Measured C_ph and the k-dependence | `budget2.py` C_ph; verdict re-grade |
| DIY-2a | Capture rate and max-speed-vs-power for spheres **and** irregular particles | P27/P28: tests whether display-speed trapping needs particle shape |
| DIY-2b | A 1–2 cm glyph drawn in air | First open-air POV image of your own |
| DIY-2c | Sphere speed with and without the return beam | P29: a new trap architecture |
| DIY-3 | A self-glowing particle drawing a glyph | First "glowing mote" |
| DIY-4 | A mote held between two 1550 nm heads at ≥ 1 m | Gate G3, the MOTE architecture |

# Bench program: turning the MOTE route's unknowns into measurements

**Why a bench now.** The remaining uncertainty in the MOTE route is no longer mostly theory. Every gate depends on a number that has not been measured (verdict v4, `07_mote_route/RESULTS.md`):

| # | Unknown | What it decides | Model's current assumption |
|---|---|---|---|
| U1 | Photophoretic force per absorbed watt at 1 atm (prefactor C_ph and the k_p dependence) | Whether the whole force law, and so every speed and channel count, is right | C_ph ∈ [0.67, 1.04]; force ∝ 1/(k_p + 2k_g) |
| U2 | Figure of merit of a real engineered mote, FOM = (J₁/A)/(k_eff + 2k_g) | Whether the route exists (needs ≳ 4 m·K/W) | 5.3 (ITO skin on aerogel), not made yet |
| U3 | Passive doughnut-pair trapping at room distance | The no-fast-loop architecture | η = 0.25–0.37 (exact LG01 model) |
| U4 | Cyan phosphor glow from a µm mote under a µW violet pump | Brightness and pump eye-safety margin | ~150 lm per absorbed W; α₄₀₅ unknown |

The stages are ordered by value of information and cost. Each has a **decision gate**. Analysis code for B1 is ready: `analyze_b1.py`, which passes its self-test (it recovers a synthetic C_ph = 0.9 after subtracting background drift).

---

## SAFETY FIRST (all stages)

The lasers below are **Class 3B or Class 4**. They can blind instantly, including from reflections, and can burn skin and ignite materials.

- **Enclose the whole beam path** in an opaque box with an interlocked lid that cuts laser power when opened. Watch through a camera or a filtered window, never by eye along the beam.
- **Wear goggles** rated for the exact wavelength (OD ≥ 4–5 at that wavelength) whenever the enclosure is open. No watches, rings or reflective tools near the beam.
- **Terminate every beam** in a beam dump (black anodised or ceramic absorber), never on a wall.
- **Align at the lowest power** the laser allows. Raise power only with the lid closed.
- **Particles stay sealed.** Handle powders wet or in a closed container; seal them in the cuvette. Wear a P100/FFP3 mask when handling dry powders. Nanopowders, especially ITO (indium), are an inhalation hazard.
- **Check local rules** for Class 4 lasers. If you can, have someone with laser-safety training review the setup.

---

## B1: Photophoretic velocimetry (settles U1). About 1–3 k$, weeks.

**Idea.** A uniform, collimated laser beam crosses a sealed cuvette of still air holding a few black microspheres. Each sphere drifts along the beam at a constant speed v. Stokes' law with slip gives the force F = 6πμav/C_c. The absorbed power is P_abs = A·πa²·I. So F/P_abs is measured directly and compared with the model. No temperature measurement is needed.

Using particles with **different known conductivities** tests the 1/(k_p + 2k_g) law. Model predictions at 10 W/cm² (1 atm):

| Particle | k_p (W/m/K) | a | Drift along beam | Settling |
|---|---|---|---|---|
| Glassy-carbon sphere | ~6 | 2.5 µm | 0.23 mm/s | 1.2 mm/s |
| Black (carbon-loaded) PMMA/PS sphere | ~0.25 | 2.5 µm | 5.0 mm/s | 0.85 mm/s |
| Carbon-coated hollow glass / hollow silica | ~0.1 | 2.5 µm | 10 mm/s | 0.23 mm/s |

**Hardware (generic):**
- Laser: 445–450 nm diode module, 0.5–2 W, or 808 nm, or 1064 nm. The wavelength matters little for black particles. Expand and collimate to a 2–4 mm beam, slightly larger than the camera field, so the intensity is near-uniform over the particles.
- Thermal power meter, and beam profiling (a camera or knife edge) for the 1/e² radius.
- Sealed quartz or glass cuvette, 10 × 10 mm. Add a few µg of particles, cap it, let it settle for minutes, then shake gently.
- Camera with macro or microscope lens (~2–5 µm/pixel, ≥ 30 fps). Side illumination: a dim LED or the beam's own glint. Optionally a long-pass filter to protect the sensor.
- Enclosure, beam dump, interlock (above).
- Particles: glassy-carbon spheres (2–12 µm), black-dyed/carbon-loaded polymer microspheres, hollow silica microspheres. Measure their size distribution under a microscope.

**Procedure.**
1. Beam off: record 30 s of tracks (background drift and settling).
2. Beam on at three powers.
3. Reverse the beam direction (rotate the cuvette 180°) to cancel residual convection.
4. Repeat for each particle type.
5. Track particles (e.g. with the `trackpy` Python package) into `tracks.csv` (columns particle_id, t_s, x_m, y_m, beam_on). Write `run.json` (power, beam radius, particle radius, density, absorptance, k_p, beam_direction).
6. Run `python3 analyze_b1.py tracks.csv run.json`.

**Gate G1.**
- Implied C_ph within 0.5–1.3 for the black polymer spheres, and the ratio of glassy-carbon to polymer drift within ×2 of the model: the force law holds and the atlas stands.
- C_ph < 0.3: speeds and channel counts worsen roughly ×3. The MOTE route is likely uneconomic.
- C_ph > 1.5: the route gets easier.

---

## B2: Engineered mote and its FOM (settles U2). Chemistry lab access needed.

**Recipe A′ (M7-validated on paper).**
1. Start from silica-aerogel or hollow-silica microparticles (radius 1.5–2.5 µm).
2. Add an ITO-nanocrystal island skin by electrostatic layer-by-layer assembly (polyelectrolyte primer, then ITO nanocrystal dispersion), aiming at an optical depth ≥ 2 at 1550 nm.
3. Grow a thin Stöber silica overcoat (oxidation protection, inhalation safety).
4. Optionally dope a little Er/Yb nanophosphor in as a ratiometric thermometer: the 525/545 nm green line ratio gives the mote temperature to about ±2 K.

**Measure.**
- Drift velocity per incident intensity in the B1 rig. With the Er thermometer, this gives force per kelvin of mean heating, which is FOM directly.
- Optional: the skin's optical depth, by transmission of a coated flat witness slide.

**Gate G2.**
- FOM ≥ 4 m·K/W: build B3.
- FOM 2–4: the route is 3–5× bigger; re-plan.
- FOM < 2: the MOTE route is not viable with today's materials.

---

## B3: Passive doughnut pair at room distance (settles U3). About 10–20 k$.

**Setup.**
- Two opposed 1064 nm or 1550 nm beams (fibre laser plus amplifier, split in two), each through a vortex phase plate (LG01).
- Focus at 1.0–1.5 m with 100–150 mm lenses, foci slightly up-beam of the trap point (axial stiffness, T5 §4).
- A small fan or traversed nozzle gives a known cross-flow.

**Measure.**
- Hold time.
- Lateral escape air speed against beam power.
- Mote temperature (Er thermometer).
- Compare with η from `physics.lg01_trap`.

**Gate G3.** η ≥ 0.2 and holding against ≥ 0.1 m/s cross-flow at ≤ 10 mW per beam.

---

## B4: First glowing MOTE line (settles U4).

Add a co-aligned µW 405 nm pump focused on the trapped mote, and move the trap along a 5 cm circle at 30–45 Hz. Measure luminous intensity per mote against absorbed pump.

**Gate G4.** ≥ 100 lm per absorbed W, with a visible cyan line in a dim room. This is the first open-air MOTE hologram stroke.

---

## How the results feed back

Each measured number replaces an assumption in `07_mote_route/mote/budget2.py`:
- C_ph → `C_ph`;
- FOM → a new entry in `MOTES`;
- η → `lg01_trap` check;
- lm/W → `PHOSPHOR`.

Re-run `sim_m8_levers.py`. The verdict is then re-graded on measured numbers instead of models.

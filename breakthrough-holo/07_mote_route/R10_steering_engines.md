# R10: Steering engines for the MOTE heads (multi-beam steering, focus tracking, best-guess head)

Compiled 2026-10-01. **Question.** Can ~12 room heads, each driving ~30–150 (accent) up to ~500–650 (film density)
independent 1550 nm trap beams, be built? Every beam must be focused (w ≈ 6–20 µm), depth-tracked over ±0.25 m, pointed to
0.3–0.6 µrad and power-modulated at ≥ 20–50 kHz, with an optional co-aligned 405 nm pump focused to ~2 µm.

**Provenance tags:**
- [FULL]: full text read.
- [SNIPPET]: search-engine snippet or abstract.
- [MEMORY]: model recall, not re-verified.
- [ESTIMATE]: my own calculation, with inputs stated.

The derivations in §1 and §5 come from a short script kept outside the repo (scratchpad `r10_calc.py`). Every formula it uses
is written out in the text.

**Access caveat.** WebFetch was egress-blocked for arxiv.org, pmc.ncbi.nlm.nih.gov and mirrorcletech.com, the same pattern R8
found. **Nothing below is [FULL].** All literature numbers come from search snippets or abstracts.

---

## Bottom line

1. **Each beam fills the whole exit window, so the window cannot be divided among beams.**
   - A Gaussian beam focused to waist w at throw L has a 1/e² footprint at the head of D_b = 2Lλ/(πw).
   - At 1.5 m: 247 / 148 / 74 mm for w = 6 / 10 / 20 µm, and 193 mm for the 2 µm, 405 nm pump.
   - At 2.3 m: 378 / 227 / 113 mm (pump 297 mm) [ESTIMATE].
   - With 150–300 mm windows, every beam must use (nearly) the full aperture. Aperture tiling would raise w by √N.
   - **The only workable decomposition is field-plane tiling.** A shared large objective forms an intermediate field. Each
     channel's steerer owns one cell of that field (a 1/√N patch of the 1 m image) and hands motes over to its neighbours.
     This is a "multi-scale" optic, the transmit-side twin of the AWARE-2 gigapixel camera (one monocentric objective with
     98 micro-cameras) [SNIPPET].
2. **The binding budget is steering étendue, not channel count.**
   - The étendue of all channels together must equal the head's étendue (window × field angle):
     **Σ_modules (d·Δθ)² ≥ f_cov·G²** per axis, where d is the steerer's clear aperture and Δθ its full optical scan angle.
   - G (per axis) = 1.2 × 1.4 × D_b × Θ_field ≈ 2.14 λ · (F/2w), and it does not depend on throw.
   - G ≈ **166 mm·rad** for a w = 10 µm trap and **216 mm·rad** with the 2 µm pump. It is 83 mm·rad at w = 20 µm and
     277 mm·rad at w = 6 µm [ESTIMATE].
   - f_cov is the fraction of the image field one head must be able to reach. It is 0.33–1, depending on how the 12-head
     scheduler shares motes.
   - So the module count has a floor, **N ≥ f_cov·G²/E²**, regardless of how few motes there are. E = d·Δθ is the
     per-device étendue.
3. **Per-device étendue E, per axis, today:**

   | Device | E (mm·rad) | Source |
   |---|---|---|
   | 2 mm MEMS mirror, ±7.5° | ≈ 1.0 | [SNIPPET + ESTIMATE] |
   | 5 mm MEMS mirror, ±5° | ≈ 1.75 | |
   | 1550 nm AOD (200 spots) | ≈ 0.55 | |
   | TI PLM | ≈ 2.1 × 1.2 | |
   | 1920-pixel LCoS | ≈ 3.0 | |
   | 4K LCoS | ≈ 6 | |
   | 10 mm galvo pair, ±10–12.5° | ≈ 7–8.7 | |
   | 20 mm galvo pair | ≈ 14–17.5 | |

   At w = 10 µm, f_cov = 1 and with the pump, a film-density head therefore needs:

   | Steerer | Devices needed |
   |---|---|
   | 2 mm MEMS mirrors | ~43 000 |
   | 5 mm MEMS mirrors | ~15 000 |
   | PLMs | ~18 000 |
   | 10 mm galvo pairs | **~620–960** |
   | 20 mm galvo pairs | **~150–240** |

   **Today, galvo-class steerers (or a large-aperture MEMS mirror that does not yet exist) are the only ones whose étendue
   matches the mote count.** A single shared modulator covers 1/500 (4K LCoS) to 1/150,000 (1550 nm AOD) of a head, which confirms the red-team
   note numerically.
4. **Neutral-atom tweezer arrays address ~10³ spots per axis, against our 2.5–8.3×10⁴ (trap) and 2.5×10⁵ (pump): 25–300×
   short per axis. They also do not provide independent 2D motion.**
   - Record sizes:
     - 11,998 sites with 6,100 atoms (Caltech; SLM-static plus AOD-mobile);
     - 18,225 sites with ~11,000 atoms from one 2 cm metasurface (Tsinghua, 2026);
     - > 3,000 atoms run continuously, reloading 300,000 atoms/s (Harvard/MIT).
   - Moves run at 0.05–0.55 µm/µs, i.e. 0.05–0.55 m/s, and up to 4.2 m/s in 3D [SNIPPET]. In absolute speed these match the
     motes (0.2–0.64 m/s).
   - **Crossed AODs only make rank-1 grids** (rows and columns that cannot cross) [SNIPPET]. At 1550 nm an AOD resolves only
     ~200 × 200 spots [SNIPPET].
   - **What transfers:** the coarse/fine hierarchy, FPGA multi-tone control, and integrated TFLN many-channel modulators
     (> 1,000 channels, 26 ns) [SNIPPET].
   - **What does not transfer:** one shared aperture serving all traps.
5. **Depth tracking is the least mature per-channel function.**
   - Need per beam: ±0.25 m equals 620–6,850 Rayleigh ranges (98–1,090 waves of defocus) for the trap, and **16,100
     Rayleigh ranges (2,570 waves)** for the 2 µm, 405 nm pump. Focus bandwidth is 0.2–2.2 kHz for the trap and 5.1 kHz for
     the pump (at 0.5 m/s, first-order lag ≤ z_R/2) [ESTIMATE].
   - Available range (fast devices are short of range, long-range devices are slow):

     | Device | Range | Speed | Source |
     |---|---|---|---|
     | 3D AOD | 22 Rayleigh ranges | 100 kHz | [SNIPPET] |
     | Acousto-optic lens | ~28 waves | 30 kHz | [SNIPPET + ESTIMATE] |
     | MEMS deformable or varifocal mirror | a few to tens of waves | 10–60 kHz | |
     | KTN lens | < 1 wave at 3 mm | µs | |
     | Electrically tunable lens (ETL) | ~40 waves | 2.5–15 ms | |

   - **Best fit:** an **optical-disc-pickup (OPU)-style voice-coil remote-focus unit.** An NA 0.85 objective oscillates
     against a fixed mirror. Mechanical focus bandwidth is 3–10 kHz [SNIPPET]. A stroke of ±0.4–0.8 mm [MEMORY] gives
     0.6–1.2 mm of OPD. That covers a w ≥ 9–10 µm trap fully and 55–100 % of the pump's range [ESTIMATE].
   - **Optional fine stage:** a MEMS varifocal mirror (25 kHz).
6. **Best-guess head today** [ESTIMATE]:
   - **H150 (sketch or rich accent):** 150 galvo modules (14–20 mm, ±10–12.5°), each with a DFB laser, an OPU-style
     focus unit and a quad-cell back-scatter sensor.
   - **H600 (film density):** ~600 galvo modules of 10–14 mm.

   | Head | Cost/channel | Head cost | Power | Module array |
   |---|---|---|---|---|
   | H150 | $0.7–5 k | $0.15–0.95 M | 0.2–1.2 kW | 0.55–0.75 m square |
   | H600 | $0.7–5 k | $0.5–3.2 M | 0.9–4.5 kW | **1.1–1.5 m square** |

   Neither is a "small head".
   - **Room totals today:** about **$0.5–5 M** (accent) and **$4–40 M** (film density, ~7,200 channels).
   - **In 5–10 years,** dense high-étendue MEMS tiles with integrated photonics and ASICs could reach **$50–250 per
     channel** and 0.1–0.3 W per channel. That puts a film-density room at **$0.4–2 M** with heads ≤ 0.3–0.4 m across.
7. **The single most valuable development** is a **2-axis analog MEMS mirror with E ≥ 5–9 mm·rad per axis** (e.g. a
   7–8 mm mirror at ±12–15° mechanical, about 4–8× today's quasi-static MEMS étendue). It should have:
   - ≥ 1 kHz quasi-static bandwidth;
   - integrated angle sensing (µrad-class);
   - an array pitch of ≤ 12–15 mm;
   - ideally, an integrated focus stage ("MEMS arrays with integrated focus").

   It would replace a $300–1,000, 1–6 W galvo module with a $20–100, ≤ 0.2 W die share. It would also shrink the head about
   4× linearly.

   **Why not the other candidates:**
   - **A 2D OPA with > 10⁴ spots per axis** would need ~10⁷–10⁸ phase elements per device. It is also unnecessary, because
     field tiling needs only 10³–5×10³ spots per axis per module.
   - **AOD+SLM hybrids** are étendue-starved.
   - **Time-multiplexing** does not reduce the total étendue. It also needs ≥ 1–4 MHz revisits to keep the mote face's
     thermal ripple ≤ 15–30 K [ESTIMATE].

---

## KEY NUMBERS

### A. What one head must do (derived; F = 1 m field, throw L = 1.5–2.3 m, depth ±0.25 m)

| Quantity | w = 6 µm | w = 10 µm | w = 20 µm | Pump 2 µm @ 405 nm | Tag |
|---|---|---|---|---|---|
| Beam NA, λ/(πw) | 0.082 | 0.049 | 0.025 | 0.065 | ESTIMATE |
| 1/e² footprint at head, at 1.5 / 2.0 / 2.3 m (mm) | 247 / 329 / 378 | 148 / 197 / 227 | 74 / 99 / 113 | 193 / 258 / 297 | ESTIMATE |
| Resolvable spots per axis over 1 m, F/(2w) | 83,000 | 50,000 | 25,000 | 250,000 | ESTIMATE |
| Head étendue per axis G = 1.2 × 1.4 × D_b × Θ (mm·rad) | 277 | 166 | 83 | 216 | ESTIMATE |
| z_R = πw²/λ | 73 µm | 203 µm | 811 µm | 31 µm | ESTIMATE |
| Rayleigh ranges in 0.5 m depth | 6,850 | 2,470 | 620 | 16,100 | ESTIMATE |
| Defocus to cover the depth (waves / OPD), W = Δz·NA²/2 | 1,090 / 1.69 mm | 390 / 0.61 mm | 98 / 0.15 mm | 2,570 / 1.04 mm | ESTIMATE |
| Focus bandwidth for lag ≤ z_R/2 (v = 0.15 / 0.5 m/s) | 0.65 / 2.2 kHz | 0.24 / 0.79 kHz | 0.06 / 0.20 kHz | 1.5 / 5.1 kHz | ESTIMATE |
| Pointing at the head (given) | 0.3–0.6 µrad | 0.3–0.6 µrad | 0.3–0.6 µrad | ~0.28 µrad | M3 |
| Pointing needed at a module mirror (× beam-expansion M ≈ 11–29) | 3–17 µrad optical (all cases) | | | | ESTIMATE |
| Per-module spots per axis, S = (F/2w)·1.2/√N, for N = 35 / 150 / 600 | 16,900 / 8,200 / 4,100 | 10,100 / 4,900 / 2,450 | 5,100 / 2,450 / 1,230 | 50,700 / 24,500 / 12,250 | ESTIMATE |

### B. Technology figures

| Technology | Key figures | Tag |
|---|---|---|
| 1D silicon OPA, 8,192 elements (Poulton et al., CLEO 2020; IEEE JSTQE 2022) | 1 µm pitch; 100° × 17° field of view (FoV); FWHM 0.01° × 0.039° (≈ 10,000 × 440 spots, second axis by 120 nm wavelength tuning); flip-chip CMOS drivers | SNIPPET |
| 1,000-channel OPA (Liu, Meng, Hu; Photonics Research 2026) | 180° FoV, 0.07° × 0.17°, side-lobe level −18.7 dB; 20 × 50 passive-matrix PWM drive | SNIPPET |
| Largest active 2D OPAs | 512 elements: 1.9 W, 70° × 6°, P_π 1.7 mW (Miller et al., Optica 2020). 1,024 elements: 55 W. Microring 2D OPA: ~330 kHz, ~250 µW static per element. 64 × 64 passive with 8 × 8 active (Sun et al., Nature 2013) | SNIPPET |
| TFLN OPA | 32 channels, 12–14 ns electro-optic response, 40° FoV at 633 nm. Multi-target 320 Gb/s optical wireless (Nat. Commun. 2025) | SNIPPET |
| Focal-plane switch array (Zhang, Wu et al., Nature 603, 253, 2022) | 128 × 128 (16,384) MEMS-switched grating antennas on 10 × 11 mm²; 70° × 70°; 0.6° addressing pitch, 0.05° beam (sparse); µs switching | SNIPPET |
| Mirrorcle 2-axis MEMS mirror | 2 mm: DC to > 2 kHz, resonance ~1.3 kHz. 5 mm: ±5° mechanical, ~500 Hz. Quasi-static ≤ ±7.5° mechanical. Repeatability < 0.001°. Mirrors 0.8–7.5 mm. **2 mm packaged: $299–329 (qty ≥ 10)** | SNIPPET |
| MEMS optical cross-connect (OXC) mirror arrays | Lucent 1100-port: **36 × 36 = 1,296 analog 2-axis mirrors per array**, 2.1 dB mean / 4.0 dB max loss. Google Palomar 136 × 136: 176 mirrors per die, ms switching, < 2 dB, 108 W | SNIPPET |
| 10 mm MEMS fast-steering mirror with piezoresistive sensing | 0.3 µrad minimum resolution; 0.52 µrad (3σ) repeatability in closed loop; > 2 kHz | SNIPPET |
| 10 mm galvo heads (laser-marking class) | 1 % full-scale step 0.18–0.35 ms; repeatability < 2 µrad; 16–18 bit; **$199–2,299**. Thorlabs 10 mm 2-axis: $2.4–5.9 k | SNIPPET |
| AOD at 1550 nm (Isomet OAD1550-XY) | 200 × 200 Rayleigh spots, 7 mm aperture, 20 MHz bandwidth. TeO₂ time-bandwidth product (TBP) up to ~1,200–4,000 (visible, large aperture) | SNIPPET |
| LCoS SLM (Meadowlark) | 1920 × 1152 at 1550 nm: 4.7 ms liquid-crystal response, 211 Hz. 1024²: up to 1.6 kHz (shorter λ) | SNIPPET |
| TI phase light modulator (PLM, DLP6750-class) | 1358 × 800, 10.8 µm, ≤ 5.76 kHz, 4-bit. At 1550 nm only 0.81π of phase stroke, so diffraction efficiency ~¼ of maximum; Talbot recycling gives 30 % | SNIPPET |
| Liquid-crystal polarization gratings (LCPG) | ~100 % efficiency per grating; > ±40° in discrete steps. Ferroelectric-LC (FLC) shutter plus polarization grating: 95.7 %, 82 µs (1064 nm) | SNIPPET |
| KTN electro-optic | Deflector: 150 mrad; ~32 spots at 200–560 kHz. Lens: 0–0.5 m⁻¹, 3 mm, DC–10 kHz, ~1 µs | SNIPPET |
| Metasurface (Lumotive LM10) | 160° FoV, 0.39° steps (~410 directions per axis), 100 µs (25 µs liquid-crystal metasurface), 905/940 nm only, 9 × 10 mm aperture | SNIPPET |
| Neutral-atom tweezers | 11,998 sites / 6,100 atoms, 130 W, ~1.4 mW per tweezer, 610 µm coherent transport at 99.95 %. 18,225 sites / 11,022 atoms from one metasurface. Moves 0.55 µm/µs, up to 4.2 m/s. 3D AOD axial range 22 Rayleigh ranges at 100 kHz | SNIPPET |
| Focus actuators | Acousto-optic lens: 30 kHz 3D random access, > 137 µm at 40× / 0.8 NA. MEMS varifocal: 25 kHz small-signal (3 mm), > 300 planes. Kilo-DM: 1.5 µm stroke < 20 µs, 60 kHz frame. ETL EL-10-30: < 2.5 ms rise, 6–15 ms settle. Optical-pickup focus: 3–10 kHz. Phone AF voice coil: 0.4 mm stroke, ~10 ms | SNIPPET |

---

## 1. What a head has to do: the geometry that decides the architecture

### 1.1 Why beams cannot each get their own patch of the window

D_b = 2Lλ/(πw) is the 1/e² diameter a beam must have at the head to focus to waist w at throw L. It is 74–378 mm across the
design range (table A). A truncating aperture should be ≥ 1.4 D_b to keep clipping side-lobes and focal-spot growth small.

So a 150–300 mm window is filled by **each** beam. Two consequences follow:

- **Aperture tiling fails.** Giving each of N beams a 1/√N sub-aperture multiplies w by √N. At N = 600 that turns 10 µm
  into ~250 µm [ESTIMATE].
- **Every beam must pass through one shared large objective.** The beams can only be separated where they are spatially
  distinct, which is near a (curved) intermediate field surface of that objective. Each channel therefore owns a field cell,
  of size F/√N at the mote: 41 mm for N = 600, 82 mm for N = 150. It hands motes to neighbouring cells, or to other heads,
  as they move.

This is exactly the multi-scale camera idea run backwards: AWARE-2 used one monocentric objective with 98 micro-cameras
to make 1 Gpixel over 120° × 50° [SNIPPET]. Our head, counted in resolvable trap spots, is 0.6–7×10⁹ "pixels"
(w = 20 → 6 µm). Counted for the 2 µm pump it is ~9×10¹⁰ [ESTIMATE].

### 1.2 The étendue budget: the head-level rule

Define, per axis:
- the steerer étendue E = d_clear × Δθ_opt,full;
- the head étendue G = k_overlap × 1.4 × D_b × Θ_field.

Here Θ_field = F/L. Because D_b ∝ L and Θ ∝ 1/L, **G does not depend on throw**: G = 2.14 λ (F/2w) with k = 1.2. Conservation
of étendue requires:

**Σ_modules E² ≥ f_cov·G²  ⇒  N_modules ≥ f_cov·G²/E²**  [ESTIMATE]

Module-count floor for a film-density head (w = 10 µm; G² = 2.75×10⁴ mm²rad² for the trap, 4.7×10⁴ with the pump):

| Steerer (per axis E) | N for trap, f_cov = 1 / 0.33 | N with pump, f_cov = 1 / 0.33 | Tag |
|---|---|---|---|
| 1550 nm AOD, 200 spots (E ≈ 0.55) | 91,000 / 30,000 | 155,000 / 51,000 | ESTIMATE from SNIPPET |
| Mirrorcle 2 mm, ±7.5° mechanical (E ≈ 1.05) | 25,000 / 8,200 | 43,000 / 14,000 | ESTIMATE from SNIPPET |
| Mirrorcle 5 mm, ±5° (E ≈ 1.75) | 9,000 / 3,000 | 15,000 / 5,100 | ESTIMATE from SNIPPET |
| TI PLM, 1358 × 800 px (E ≈ 2.1 × 1.24) | 10,500 / 3,500 | 18,000 / 6,000 | ESTIMATE from SNIPPET |
| 4K LCoS, 3840 px (E ≈ 6.0 × 3.3) | 1,400 / 460 | 2,400 / 790 | ESTIMATE |
| Poulton-class 1D OPA (E ≈ 14 × ~1.2) | ~1,600 / 540 | ~2,800 / 930 | ESTIMATE from SNIPPET |
| 10 mm galvo, ±10–12.5° (E ≈ 7.0–8.7) | 360–560 / 120–185 | 620–960 / 205–320 | ESTIMATE |
| 20 mm galvo, ±10–12.5° (E ≈ 14–17.5) | 90–140 / 30–46 | 155–240 / 50–80 | ESTIMATE |

*Note on the pump columns.* For diffractive steerers (SLM, AOD, OPA), E scales with λ (E ≈ N_pixels·λ). At 405 nm their
pump rows are therefore ~(1550/405)² ≈ 15× worse than shown. Mirrors are achromatic, which is one more reason to steer
both wavelengths with mirrors.

**Reading.**
- One shared modulator covers at most 1/500 (4K LCoS) to 1/150,000 (AOD) of a head. The red-team note stands.
- Steerers whose étendue matches the mote count per head (150–650) are **10–20 mm galvo pairs** today.
- At w = 20 µm, divide every N by 4; at w = 6 µm, multiply by 2.8.

The f_cov factor (how much of the image each head must reach) comes from the 12-head scheduling geometry (M4). It is the
cheapest lever and has not been computed (Gap 11).

### 1.3 Depth: why focus is hard

- **Range.** The defocus needed to sweep ±0.25 m is W = Δz·NA²/2, i.e. N_R/(2π) waves, where N_R = Δz/z_R:
  - 98 waves (w = 20 µm) to 1,090 waves (w = 6 µm) for the trap;
  - **2,570 waves** for the pump (table A).
  - In OPD that is 0.15–1.7 mm, independent of where in the system the focusing element sits. At a pupil of diameter d the
    focal power needed scales as 1/d²; M3 found ~200 D at a 10 mm pupil.
- **Precision.** ±z_R/2:
  - trap, w = 10 µm: ±100 µm, i.e. ±0.12 µm of OPD;
  - pump: ±15 µm, i.e. **±31 nm of OPD** (λ₄₀₅/13).
- **Bandwidth.** B ≥ v/(πz_R) is 0.2–2.2 kHz (trap) and 5.1 kHz (pump) at v = 0.5 m/s.
  - The motes follow *planned* paths, so feed-forward of the plan leaves only the disturbance (drafts 0.05–0.15 m/s). That
    cuts B by about 3–10×.
  - The large-stroke stage then only has to follow the mote's axial speed scaled by (NA_out/NA_actuator)². At an NA 0.85
    actuator that is a few mm/s [ESTIMATE].

### 1.4 Pointing

The head needs 0.3–0.6 µrad. In module space, angles are magnified by M = (beam at window)/(beam at mirror) ≈ 11–29 for
N = 150–600, so a module mirror needs only **3–17 µrad optical** [ESTIMATE]. This is within:
- marking-galvo repeatability (< 2 µrad) [SNIPPET];
- MEMS fast-steering mirrors (0.3 µrad resolution, 0.52 µrad 3σ) [SNIPPET];
- Mirrorcle's open-loop repeatability (< 0.001° mechanical ≈ 35 µrad optical) [SNIPPET], only when closed on the mote's
  back-scatter. That closure is needed anyway.

The trade-off is fixed by étendue: smaller steering apertures relax pointing precision exactly as fast as they lose
resolvable spots.

### 1.5 Time-multiplexing several motes per steerer: limited, and no étendue gain

- **Thermal limit.** M2b gives a photophoretic force lag τ_F ≈ 15 µs (a = 1 µm). A beam that visits K motes in turn must
  revisit each fast enough that the hot-face temperature ripple stays small. Inputs:
  - absorbed average power ≈ 2P·a²/w² = 0.45 mW (10 mW beam, a = 1.5 µm, w = 10 µm);
  - heated skin depth ≈ max(0.2 µm, √(κt)).

  Resulting ripple: ~15 K at a 0.25 µs revisit period, 29 K at 1 µs, 41 K at 2 µs, **independent of K** [ESTIMATE; crude].
  Because the design is heat-limited (T_face ≤ 450–600 K), the revisit rate must be ≥ 1–4 MHz, with dwell ≤ 30–300 ns for
  K = 3–10. Only electro-optic devices qualify: TFLN OPAs at 12–14 ns and TFLN MZIs at 26 ns [SNIPPET]. The focus would
  also have to switch per visit.
- **No étendue gain.** If K motes share a module, each module must cover √K× more spots per axis. **Σ E² is unchanged.**
  Time-multiplexing reduces the device count only if big-étendue devices are cheaper per unit étendue than small ones, and
  the cheap big ones (galvos) cannot switch in nanoseconds.
- **Conclusion:** one physical channel per beam for the next decade.

---

## 2. Survey of multi-beam steering technologies (Q1)

The spot count S per axis is quoted either as given in the source (for SLMs, ~pixels/2) or as E/(1.78 λ) for a Gaussian beam
with 1.4× clearance. "Beams" means simultaneous independent beams per device.

| Family | S per axis | Beams per device | Speed | Efficiency | 1550 nm power | Cost per channel | Maturity | Tag |
|---|---|---|---|---|---|---|---|---|
| **Si OPA, 1D (8,192 elements)** | ~10,000 (phase) × ~440 (λ-tuned) | 1 (multi-beam only by splitting the aperture) | thermo-optic, ~10–100 µs [MEMORY] | main-lobe/insertion loss typically −5 to −10 dB [MEMORY] | Si waveguides ≲ 0.1–0.5 W total before two-photon/free-carrier loss [MEMORY]; ample per beam | research; Taara ships an OPA (> 1,000 emitters) for FSO [SNIPPET] | lab → first product | SNIPPET |
| **Si OPA, 2D** | ~22–32 (512–1,024 elements); 64 × 64 passive | 1–4 (Butler-matrix multi-beam) [SNIPPET] | thermo-optic ~kHz; microring ~330 kHz | low; grating lobes unless pitch ≤ λ/2 | as above | research | lab | SNIPPET |
| **TFLN OPA** | ~32–100 | 1 (multi-target by time or holography) | **ns** (12–14 ns) | n/a | fine | research | lab | SNIPPET |
| **Focal-plane switch array (FPSA)** | 128 addressable (sparse: 0.6° pitch vs 0.05° beam) | 1 per input (more with more inputs) | µs, sub-MHz | n/a | fine | research | lab | SNIPPET |
| **2-axis MEMS mirror** | 2 mm: ~380–500; 5 mm: ~630 | 1 | DC–2 kHz (2 mm); ~500 Hz (5 mm) | ~95–98 % (Au) [MEMORY] | trivial at 10 mW | **$299–329** (2 mm, qty ≥ 10) + driver | product | SNIPPET |
| **MEMS OXC arrays** | small mirrors, ~100–300 [MEMORY] | **136–1,296 mirrors per die** | ms switching, held for years | 2 dB fibre-to-fibre | W-class aggregate | buried in $10⁵–10⁶ switches | product | SNIPPET |
| **Galvo pair** | 10 mm: ~2,500–3,150; 20 mm: ~5,000–6,300 | 1 | 0.18–0.35 ms 1 % step (≈ 1–2 kHz small-signal) [ESTIMATE] | ~98 % | kW-class | **$199–2,299** (10 mm marking class) | mass product | SNIPPET |
| **AOD (TeO₂)** | 200 (1550 nm, 7 mm); ≤ 1,000–2,000 visible | **multi-tone: tens to ~100 per axis**, but crossed AODs give only rank-1 grids | access 10–30 µs; tone updates µs | 50–80 % per axis [MEMORY] | W-class | $3–10 k per axis with RF [MEMORY] | product | SNIPPET |
| **Integrated AO (TFLN)** | tens | **tens per channel** (multi-tone) | sub-µs | n/a | n/a (780 nm demo) | research | lab | SNIPPET |
| **LCoS SLM** | ~960 × 576 (1920 × 1152) | many (holographic; power split, ~1/K each) | **211 Hz at 1550 nm** | ~60–90 % first order [MEMORY] | 10s of W with cooling [MEMORY] | $10–30 k per device [MEMORY] | product | SNIPPET |
| **TI PLM** | ~680 × 400 | many (holographic) | ≤ 5.76 kHz | **~30 % at 1550 nm** (Talbot trick) | moderate | EVM-class [MEMORY] | product (visible) | SNIPPET |
| **Fraunhofer MEMS SLM** | 512 × 2048 tilt mirrors; piston arrays in development | many | 2 kHz | n/a | n/a | n/a | lab/product | SNIPPET |
| **LCPG stack** | discrete 2ⁿ states, > ±40° | 1 | ms (nematic); **82 µs** (FLC + PG) | ~96–99 % per stage | high | moderate | product (BNS / Meadowlark) | SNIPPET |
| **KTN electro-optic deflector** | ~32 at 200–560 kHz | 1 | sub-µs | high | moderate | NTT-AT module [MEMORY] | product | SNIPPET |
| **Liquid-crystal metasurface (Lumotive)** | ~410 | 1 (reconfigurable) | 25–100 µs | moderate [MEMORY] | **905/940 nm only** | chip product | product | SNIPPET |
| **FSO multi-beam (wavelength-routed)** | set by the AWGR port count | **80 beams via an 80-port AWGR** | wavelength-tuning speed | high | high | telecom parts | lab | SNIPPET |
| **VIPA + grating (atom control)** | 83 × 52 | 1 | **> 84 MFPS** | n/a | n/a | lab | lab | SNIPPET |

**Notes.**
1. **OPAs.** The 8,192-element 1D OPA [SNIPPET] has in one device about the 2D spot product of a ~6 mm galvo pair (~4×10⁶).
   Its second axis, however, is wavelength-steered, so each module would need its own widely tunable laser. Drive is also
   costly: thermo-optic at ~1–2 mW per element is 8–16 W per OPA, or ~5–10 kW per 600-module head [ESTIMATE].
   - Microring phase shifters (~250 µW static [SNIPPET]) or electro-optic TFLN could fix the power.
   - A 2D OPA with ~3,000 spots per axis needs ~10⁷ λ/2-pitch elements. The largest active 2D OPA has 512–1,024 elements
     [SNIPPET], 4 orders of magnitude short.
   - An "OPA chip with N beams" does not escape the étendue rule: beams from one aperture share that aperture's étendue. It
     helps only with *clustering* (several motes in one cell).
2. **MEMS OXCs** prove that **10²–10³ independently held analog 2-axis mirrors per die**, with years-long stable pointing,
   are manufacturable. Their mirrors are small and slow to switch: the étendue per mirror is low. What is missing is the
   OXC array architecture with Mirrorcle-or-larger étendue per mirror.
3. **Galvos** are the cheapest étendue today: about $3–50 per mm²rad² (device price, 10–20 mm marking class), against
   about $270–900 per mm²rad² for 2 mm MEMS with driver [ESTIMATE from SNIPPET prices]. They are bulky (≈ 40–60 mm module pitch) and
   power-hungry (≈ 1–6 W per pair including linear drivers [ESTIMATE]). Fans and coils may also break the "silent display"
   claim (RESULTS §6).
4. **LCPG plus fast FLC switches** (82 µs, 95.7 % [SNIPPET]) can multiply a small MEMS mirror's étendue by 2ⁿ per axis in
   discrete hops. Example: 2 mm MEMS × 8 = 8.4 mm·rad per axis, galvo-equivalent, with 6–8 stages at ~0.73 total
   throughput [ESTIMATE]. Each hop blanks the beam for ~20–100 µs. The other beams on that mote must dim in concert (mote
   drift ~4–12 µm in 82 µs at 0.05–0.15 m/s air), or the mote is handed over. This is the nearest-term route to compact
   modules (Gap 6).

---

## 3. Neutral-atom optical tweezer arrays (Q2)

| System | Sites / atoms | How traps are made and moved | Numbers | Tag |
|---|---|---|---|---|
| Manetsch et al. (Endres, Caltech), Nature 2025 (arXiv 2403.12021) | **11,998 sites / > 6,100 atoms** | static SLM tweezers (1,055 / 1,061 nm); crossed-AOD mobile tweezers pick up and move atoms | 130 W from fibre amplifiers, ~35–40 W at the objective, **~1.4 mW per tweezer**; coherent transport over **610 µm** at 99.95 % | SNIPPET |
| Chiu et al. (Lukin), Nature 2025 | > 3,000 atoms held > 2 h | two optical-lattice conveyor belts feed a reservoir; tweezers reload | **300,000 atoms/s** reloaded, 30,000 initialised qubits/s; > 50 M atoms cycled | SNIPPET |
| Pichard et al. (Browaeys), PR Applied 22, 024073 (2024) | 2,088 sites at 6 K; 828-atom target assembled | single moving tweezer via orthogonal AODs; FPGA and fast DACs | atom-by-atom, i.e. serial | SNIPPET |
| Lin et al. (USTC), PRL 2025 | **2,024 atoms defect-free in 60 ms** | SLM only; AI-computed hologram per step; all atoms move in parallel | constant time in N (claimed to scale to 10⁴–10⁵) | SNIPPET |
| Wang et al. (Zhai, Tsinghua), arXiv 2606.02715 (2026) | **135 × 135 = 18,225 sites / 11,022 atoms (mean)** | one ~2 cm metasurface, outside vacuum, ~1.5 cm working distance; static | filling 60.5 % | SNIPPET |
| Bluvstein et al., Nature 2022 | tens to hundreds | crossed AODs, cubic (constant-jerk) frequency ramps | **0.55 µm/µs** average transport | SNIPPET |
| Lu et al. (Stamper-Kurn), arXiv 2510.11451 | n/a | 3D AOD lens ("3D-AODL"), Shepard waveforms | 200 × 200 × 136 µm³ volume, **> 4.2 m/s** | SNIPPET |
| Picard & Endres, Device 2026 (arXiv 2510.07633) | n/a | double-pass AOD plus Littrow grating as a frequency-tuned lens | **axial 22 Rayleigh ranges, switching ≤ 100 kHz**; multi-tone gives multi-focal patterns | SNIPPET |
| Generic rearrangement figures | n/a | AOD | static-to-mobile hand-off 60 µs each way; peak speeds 54 / 130 / 550 µm/ms; acceleration 2,750–5,500 m/s² | SNIPPET |
| Constraints | n/a | crossed AODs | rows and columns move in tandem and must not cross; intermodulation creates spurious tweezers; intensity calibration overhead ∝ (tones)² | SNIPPET |
| Per-column AOD design (SPIE 2024) | 20 columns | one AOD per column, then mirror cascades | independent spacing within each column | SNIPPET |
| TFLN control photonics | > 1,000 channels | MZI meshes | 26 ns rise, 71 dB extinction at 795 nm | SNIPPET |

**Resolvable field.** Tweezer fields are ~10²·⁵–10³ spots per axis [ESTIMATE].
- A 110–135-site row at 2–3 spot pitch gives ~300–400.
- AOD time-bandwidth products give 200 at 1550 nm and up to ~1,000–2,000 in the visible.

A head needs 25,000–83,000 spots per axis (trap) and 250,000 (pump), i.e. **25–300× more per axis** (10³–10⁵× in area).
In étendue, a tweezer objective (~1 mm field × NA 0.5–0.7 at ~1 µm) holds ≈ 1 mm·rad, against 83–277 mm·rad for a head
[ESTIMATE].

**Speeds.** Tweezer moves (0.05–0.55 m/s, up to 4.2 m/s) equal or exceed mote speeds (0.2–0.64 m/s). In spot units, tweezers
slew ~3×10⁵ spots/s against our ~1–3×10⁴ spots/s. **Speed is not the problem; field and independence are.**

**How the architecture could scale to ours** [ESTIMATE]:
- **Shared-aperture SLM or AOD engine.** It does not scale. Covering a head would take 460–2,400 4K SLMs, or
  30,000–155,000 1550 nm AOD pairs (§1.2), and SLMs run at ≤ 211 Hz at 1550 nm.
- **"Static array + mobile tweezers" hierarchy.** It maps onto coarse/fine steering: a coarse discrete selector (LCPG,
  switch tree or FPSA) feeding a continuous fine steerer (MEMS mirror). That is the hybrid in §2 note 4.
- **Parts that transfer directly:**
  - FPGA multi-tone synthesis with µs updates and intensity feedback;
  - parallel-move planning (USTC), which becomes the workload manager's hand-over planner;
  - TFLN many-channel modulators for per-channel 20–50 kHz power control (huge margin);
  - metasurfaces for static fan-out of the per-module source beams.
- **The 3D AOD (22 Rayleigh ranges)** is 30–300× short of our 620–6,850 Rayleigh ranges. It would serve only as a fast
  fine-focus vernier.

---

## 4. Variable-focus tracking for many beams (Q3)

| Device | Defocus range | Speed | Aperture / notes | Fits our 98–2,570 waves at 0.2–5 kHz? | Tag |
|---|---|---|---|---|---|
| Acousto-optic lens (Kirkby / Silver; Nadella 2016) | > 137 µm at 40× / 0.8 NA, ≈ 44 µm OPD ≈ **28 waves at 1.55 µm** | **30 kHz** 3D random access | 4 AODs per beam; lateral and axial share the AO bandwidth | No (range) | SNIPPET + ESTIMATE |
| 3D AOD (Picard & Endres 2026) | **22 Rayleigh ranges** (≈ 3.5 waves) | ≤ 100 kHz | one AOD per axis pair | No (range); possible fine vernier | SNIPPET |
| MEMS varifocal mirrors (Microsyst. Nanoeng. review 2023) | "> 300 resolvable planes"; a few µm stroke | 3 mm SU-8 membrane: 100 µs step, **25 kHz small-signal**; piezo: 2 kHz; 460 kHz resonant (300 Hz usable) | mm apertures | Fine stage only (±10–30 waves) | SNIPPET |
| Boston Micromachines Kilo-DM | 1.5 µm (< 20 µs), 3.5 µm (< 80 µs) stroke, i.e. ~2–5 waves of defocus | 60 kHz frame | 952–1,024 actuators | Fine or aberration stage only | SNIPPET |
| KTN varifocal lens (NTT-AT) | 0–0.5 m⁻¹ at 3 mm, i.e. **< 0.4 waves** | DC–10 kHz, ~1 µs | 488–3,500 nm | No | SNIPPET + ESTIMATE |
| Electrically tunable lens (Optotune EL-10-30) | e.g. 5–10 dpt at 10 mm, ≈ 40 waves | < 2.5 ms rise, 6–15 ms settle | 10 mm | No (speed) | SNIPPET + ESTIMATE |
| TAG lens | large | 70 kHz to several 100 kHz, **sinusoidal sweep only** | gating each beam to its depth gives duty ≈ 2z_R/range ≈ 0.1–0.3 % | No (needs 300–1,000× peak power) | SNIPPET + ESTIMATE |
| Remote focusing, voice-coil mirror | mm stroke | 5–25 ms response | achromatic (mirror) | Coarse only | SNIPPET |
| Lateral-to-axial remote focus (galvo onto a tilted or stepped mirror; Light Sci. Appl. 2020) | N_R ≈ 2 × S_lateral × tanα × NA_r ≈ 1,000–3,000 Rayleigh ranges with a MEMS mirror [ESTIMATE] | **12 kHz resonant**; 1–5 kHz with focus actuators | one extra 1-axis MEMS or galvo per channel | Covers trap w ≥ 8–10 µm; not w = 6 µm or the pump | SNIPPET + ESTIMATE |
| **Optical-disc-pickup (OPU) actuator as remote focus** | stroke ±0.4–0.8 mm [MEMORY] at NA 0.85, i.e. OPD ≈ s·NA² ≈ **0.6–1.2 mm** (390–770 waves at 1.55 µm) | mechanical bandwidth **3–10 kHz** (5.3 kHz Blu-ray design) | mass-produced; 405 nm optics exist | **Yes for trap w ≥ 9–10 µm; 55–100 % of the pump range** | SNIPPET + MEMORY + ESTIMATE |
| Phone autofocus voice coil (VCM) | 0.4 mm stroke | ~10 ms settle (±5 µm); resonance 50–150 Hz | very cheap | Coarse only | SNIPPET |

**Remote-focus stroke needed**, s = OPD/NA_r²:

| Case | NA 0.5 | NA 0.7 | NA 0.85 |
|---|---|---|---|
| Trap, w = 20 µm | 0.6 mm | 0.31 mm | 0.21 mm |
| Trap, w = 10 µm | 2.4 mm | 1.22 mm | 0.83 mm |
| Pump | 4.2 mm | 2.1 mm | 1.44 mm |
| Trap, w = 6 µm | 6.7 mm | 3.4 mm | 2.3 mm |

**Recommendation** [ESTIMATE]. Use one OPU-class 2-axis voice-coil objective (NA ≈ 0.85) per channel as a
**remote-focus unit**: polarizing beam splitter, λ/4 plate, then the objective against a fixed mirror (Botcherby
geometry).
- **Range.** It covers the trap at w ≥ 9–10 µm in one stage. The pump or w = 6 µm needs ~1.5–2.3 mm. Options:
  - a longer-stroke voice-coil flexure (coarse, 30–100 Hz) plus a MEMS varifocal fine stage (±10–30 waves, 10–25 kHz);
  - or relax the pump to w_p ≈ 3 µm.
- **Error signal.** An astigmatic focus-error signal from the mote's back-scatter, exactly as in a disc drive.
- **Required precision** (pump case): ±31 nm OPD, i.e. ±40–60 nm mirror position at NA 0.7–0.85. That is DVD/Blu-ray
  servo class.
- **Why OPU-class.** It is the only per-channel focus engine that combines the range, kHz bandwidth, two-wavelength
  (mirror-based, achromatic) operation and $10–100 cost. It is **not demonstrated** in this role (Gap 2).

---

## 5. Best-guess head architecture (Q4)

### 5.1 Optical layout: a multi-scale transmit head

1. **Shared objective.**
   - 250 mm clear aperture (300 mm maximum), field ±18–20° (1 m at 1.5 m).
   - Reflective or monocentric (Schmidt/Bouwers-type), so that 405 and 1550 nm share the focal surface.
   - Diffraction-limited at NA 0.05 (1550 nm) **and** 0.065 (405 nm) after per-module correction of residuals, as AWARE's
     micro-optics correct its monocentric objective.
2. **Geometry.**
   - The curved field surface has image-side NA′. The objective focal length is f ≈ D_w/(2NA′).
   - Module pitch on the field surface: p = D_w·Θ/(2NA′√N) = 167 mm·rad/(2NA′√N).
   - For N = 600: p = 14 mm at NA′ 0.25 (f ≈ 0.5 m), 28 mm at 0.125 (f ≈ 1 m), 56 mm at 0.0625 (f ≈ 2 m, folded).
   - **Module-array area is ≈ N·p²** whatever the fold [ESTIMATE]. A head's linear size is therefore ≈ √N × (module
     pitch). That is why galvo-based heads are large.
3. **Hand-over.** Cells overlap by 20 % (k = 1.2). The scheduler cross-fades power between adjacent modules, or adjacent
   heads, over ~1 ms when a mote crosses a cell boundary. At 0.2–0.64 m/s and 41–82 mm cells, that is a hand-over every
   ~0.06–0.4 s per mote [ESTIMATE].
4. **Clustering.** Bright strokes concentrate motes into few cells. This is handled by the 12-head workload manager and, in
   later generations, by multi-beam modules (holographic split inside one cell).

### 5.2 One channel (module): signal chain and per-channel BOM

| # | Function | Today (COTS-based) | Cost today (qty 10²–10³) | At volume, ~10⁴/yr | 5–10 yr integrated | Power per channel | Tag |
|---|---|---|---|---|---|---|---|
| 1 | 1550 nm source and fast power modulation | own 10–20 mW DFB, direct current modulation (MHz bandwidth covers the 20–50 kHz push loop; per-channel lasers are mutually incoherent, so overlapping beams do not fringe) | $50–300 | $10–30 | III-V-on-SiN laser array, or one amplifier plus a TFLN/SiN modulator array | 0.2–0.5 W | MEMORY / ESTIMATE |
| 2 | 405 nm pump (10–40 µW) | shared 405 nm single-mode diode → 1:N splitter → per-channel on/off (SiN thermo-optic or MEMS variable attenuator) | $20–100 | $5–20 | on-chip splitter and switch | < 0.05 W | ESTIMATE |
| 3 | Beam combine and condition | fibre dichroic, collimator, polarizing beam splitter, λ/4 plate | $50–200 | $10–30 | wafer-level micro-optics | 0 | ESTIMATE |
| 4 | Focus | OPU-type voice-coil remote focus (NA 0.85, ±0.4–0.8 mm, 3–10 kHz); optional MEMS varifocal fine stage | $30–150 (+$100–500 fine stage) | $10–40 | MEMS z-stage plus membrane | 0.05–0.3 W | SNIPPET / MEMORY / ESTIMATE |
| 5 | Steering | **10–14 mm galvo pair** (film head) or **14–20 mm** (H150); 18-bit; < 2 µrad repeatability | $200–2,300 | $150–500 | **high-étendue MEMS mirror die share** | 1–6 W (galvo) → ≤ 0.2 W (MEMS) | SNIPPET / ESTIMATE |
| 6 | Relay to field cell | scan lens plus field lens (telecentric) | $100–400 | $15–50 | molded | 0 | ESTIMATE |
| 7 | Back-scatter sensing | descanned return → InGaAs quad cell (lateral) and astigmatic focus error (z); ≥ 200 kSa/s | $50–300 | $10–30 | on-chip Ge detectors (coherent detection possible) | 0.1–0.3 W | ESTIMATE |
| 8 | Control | FPGA per 32–64 channels: 20–50 kHz power loop; 1–5 kHz steer and focus loops; feed-forward; hand-over | $50–200 | $20–50 | ASIC per 64 channels | 0.2–0.5 W | ESTIMATE |
| 9 | Mechanics, alignment, test | hand / semi-automatic active alignment | $100–800 | $30–80 | wafer-level | 0 | ESTIMATE |
| | **Total per channel** | | **≈ $0.7–5 k** (central $1.5–2.5 k) | **≈ $0.3–0.8 k** | **≈ $50–250** | **1.5–7.5 W → 0.1–0.3 W** | ESTIMATE |

### 5.3 Two head designs (w_trap = 10 µm; 2 µm pump; D_w = 250 mm)

| | **H150** (sketch per head, or rich accent) | **H600** (film density per head) |
|---|---|---|
| Channels | 150 | 600 |
| Steerer | 14–20 mm galvo pair (E ≈ 10–17.5 mm·rad) | 10–14 mm galvo pair (E ≈ 7–12 mm·rad) |
| Field coverage f_cov achieved (trap / with pump) | 0.55–1 / 0.3–1 | 1 / 0.6–1 |
| Cell at the mote | 98 mm (k = 1.2) | 49 mm |
| Spots per module, S | ~4,900 needed / ~3,500–6,300 available | ~2,450 needed / ~2,500–4,300 available |
| Module mirror pointing needed | 3–9 µrad optical | 6–17 µrad optical |
| Focus | OPU remote focus (+ fine stage for the pump) | same |
| Optical output | 1.5 W at 1550 nm; ≤ 6 mW at 405 nm | 6 W at 1550 nm; ≤ 24 mW at 405 nm |
| Electrical power today | **0.2–1.2 kW** | **0.9–4.5 kW** |
| Module array / head size today | 0.55–0.75 m square; head ~0.8 m deep (folded) | **1.1–1.5 m square**; ~1 m deep |
| Cost today (+ $50–200 k objective, frame, thermal) | **$0.15–0.95 M** | **$0.5–3.2 M** |
| Cost at volume (≥ 10⁴ channels/yr) | $60–150 k | $0.2–0.5 M |
| 5–10 yr (integrated MEMS tiles, ≤ 12 mm pitch) | $10–40 k; 15–45 W; ~0.15 m array | $30–150 k; 60–180 W; **~0.3 m array** |

All rows: [ESTIMATE], from SNIPPET part prices.

**Room totals** [ESTIMATE]. Today's per-channel range is $0.7–5 k.
- **Accent: about $0.5–5 M.**
  - Channel need: 340–420 channels (M8). Coverage favours ~12 × 50–90 large-galvo modules (20–30 mm) rather than 12 × 35.
  - Throughput: ≈ 1.5–2.5 W at 1550 nm (M8). Electrical: ~1–8 kW today.
- **Sketch: about $1–9 M.** 1,500–1,800 channels in 12 × H150.
- **Film density: about $4–40 M.** 6,100–7,600 channels in 12 × H600.
  - Electrical: ~11–55 kW today, against ~1–2 kW integrated.
  - With 5–10 yr integration: **$0.4–2 M**.

**Why H600 is not a "small head" today.** Area ≈ N·p², and a galvo module needs p ≈ 45–60 mm. A ≤ 0.3–0.4 m head with
600 channels needs p ≤ 12–15 mm, with E ≥ 5–9 mm·rad inside that footprint. **No steering device does that today**
(MEMS: E ≤ 1.75; galvo: right E, ~4× too wide).

### 5.4 The nearest-term compact alternative (not demonstrated)

**Module:** 2 mm MEMS mirror (E ≈ 1.05) plus a 3–4-stage passive-PG and FLC stack per axis (×8–16 discrete), giving an
effective E of ≈ 8–17 mm·rad.
- **Cost and size:** ≈ $400–1,500 per channel at ~15–20 mm pitch.
- **Costs:**
  - 25–30 % throughput loss;
  - 20–100 µs hop blanks with coordinated dimming or hand-over;
  - per-hop calibration.

It is worth a bench test if the MEMS route stalls [ESTIMATE].

---

## 6. Which single development would cut cost and complexity most? (Q5)

Ranked by how much of the per-channel cost, power and size it removes, given the étendue rule of §1.2 [ESTIMATE].

1. **High-étendue 2-axis analog MEMS mirror arrays with integrated sensing and focus.**
   - **Target:**
     - E ≥ 5–9 mm·rad per axis (e.g. 7–8 mm at ±12–15° mechanical, or 5 mm at ±20°);
     - ≥ 1 kHz quasi-static bandwidth;
     - closed-loop ≤ 5–10 µrad optical;
     - 8 × 8 per die at ≤ 12–15 mm pitch;
     - plus an integrated piston/varifocal or z-stage focus.
   - **Today:**
     - Mirrorcle 2 mm at ±7.5° gives E ≈ 1.05 at ~2 kHz; 5 mm at ±5° gives 1.75 at ~500 Hz [SNIPPET].
     - The figure of merit D·θ·f is ~4–8× short.
     - OXC arrays prove 10²–10³ mirrors per die with long-term holding [SNIPPET].
     - AlScN piezo-MEMS and the 10 mm sensed MEMS FSM (> 2 kHz, 0.3 µrad) [SNIPPET] point the way.
   - **Payoff:**
     - per-channel steering $300–1,000 → $20–100;
     - power 1–6 W → ≤ 0.2 W;
     - head linear size ÷4 (1.2 m → 0.3 m for H600);
     - room film-density cost ~÷10.
   - This is the "MEMS arrays with integrated focus" option, and it is the recommended one.
2. **Per-channel focus engine with ≥ 1,000–2,600 waves at ≥ 1–5 kHz.** For example, an OPU-class actuator adapted to
   remote focus, or a MEMS z-stage with ≥ 1.5 mm stroke at NA 0.85. It is needed for the pump at 2 µm and for traps with
   w < 9 µm.
3. **An electro-optic 1D OPA (TFLN or BTO) with ≥ 4 k elements, plus a cheap fast-hopping widely tunable laser per
   module.** This is a solid-state module of galvo-class étendue with ns agility, and the long shot (≥ 10 years). It enables
   time-multiplexing only if the thermal ripple (§1.5) allows it.

**Not recommended as the key development:**
- **A 2D OPA with > 10⁴ spots per axis** needs 10⁷–10⁸ elements per device. Field tiling needs only 1–5×10³ spots per axis
  per module.
- **A multi-beam AOD+SLM hybrid** has E ≈ 0.5–6 mm·rad per device, 200 spots at 1550 nm, ≤ 211 Hz (LCoS) and 30 %
  efficiency (PLM at 1550 nm). It is 10²–10⁵× short of a head.

---

## 7. Gaps and what could not be verified

1. **No compact high-étendue steerer exists** (E ≥ 5–9 mm·rad at ≤ 12–15 mm pitch, ≥ 1 kHz). The film-density head is
   therefore a ~1.2 m, kW-class galvo cabinet today. Galvo electrical power (1–6 W per pair) and acoustic/fan noise are
   [ESTIMATE].
2. **Focus engine not demonstrated.** Not demonstrated:
   - the OPU-as-remote-focus concept;
   - its stroke (±0.4–0.8 mm is [MEMORY]);
   - nm-class precision on a mote's back-scatter focus-error signal;
   - two-wavelength (405/1550) chromatic tracking.

   Pump focus (2,570 waves, ±31 nm OPD) is the hardest single per-channel spec.
3. **The head objective is undesigned.** It needs a 250–300 mm aperture with a ±18–20° field, and must be
   diffraction-limited at 1550 nm (NA 0.05) and 405 nm (NA 0.065) on a curved field surface. At 405 nm it is a
   ~10¹¹-spot optic. Per-module correction is assumed, not shown.
4. **Ghosts and stray foci.** 600 beams pass through shared optics, and each surface reflects ~0.1–0.5 % [MEMORY]. That
   creates ghost foci that may sit on other motes (stray force) or create overlap hazards. Not analysed.
5. **Back-scatter sensing SNR** for ≤ 0.5 µm lateral and ≤ z_R/2 axial error at 20–50 kHz per channel, through the
   descanned path with 600 neighbours' stray light, is not computed.
6. **Hand-over choreography** (cross-fades between modules and heads; LCPG/FLC hop blanking; passive-pair partners) is not
   simulated. The 82 µs FLC figure is at 1064 nm [SNIPPET].
7. **Time-multiplexing thermal ripple** (§1.5) uses a crude skin heat-capacity model. A proper transient-conduction model
   is needed before discarding it entirely.
8. **Prices.** Only the Mirrorcle 2 mm price, galvo prices (marking heads $199–2,299; Thorlabs $2.4–5.9 k) and EDFA ranges
   are [SNIPPET]. Everything else is [MEMORY] or [ESTIMATE], with ±2–3× uncertainty.
9. **Not verified (snippets only):**
   - Lucent OXC mirror size and tilt (only "36 × 36 arrays" seen);
   - Poulton OPA switching speed and efficiency;
   - Taara OPA specs;
   - the Tsinghua 11,000-atom metasurface paper (preprint);
   - Picard & Endres 3D-AOD details;
   - 8,192-element OPA power.
10. **Not found:** any 2D OPA larger than 1,024 active elements, any multi-beam OPA beyond 4 × 4 Butler-matrix beams, and
    any MEMS mirror array with both ≥ 5 mm mirrors and kHz quasi-static bandwidth.
11. **f_cov per head** (the share of the 1 m image each of the 12 heads must reach, while each mote still gets ~3
    well-angled beams) is not computed from the M4 geometry. Every module count above scales linearly with it. **This is
    the cheapest next calculation.**
12. **Calibration at scale.** Mapping ~7,000 channels × (2 angles + focus) to mote space over temperature needs continuous
    self-calibration from back-scatter. Its drift budget is unknown.

---

## Sources

Search-result URLs, all used at SNIPPET level.

**OPAs**
- Poulton et al., 8,192-element OPA: https://www.researchgate.net/publication/361693259_Coherent_LiDAR_With_an_8192-Element_Optical_Phased_Array_and_Driving_Laser
- 1,000-channel 180° OPA: https://arxiv.org/pdf/2508.19977 ; https://www.researching.cn/articles/OJeb58dd81bf12739c
- Miller et al., 512-element OPA (Optica 7, 3, 2020): https://opg.optica.org/optica/fulltext.cfm?uri=optica-7-1-3&id=425088
- Microring 2D OPA (APL Photonics 8, 051305): https://pubs.aip.org/aip/app/article/8/5/051305/2893498/
- Sun et al., Nature 493, 195 (2013): https://mtlsites.mit.edu/annual_reports/2013/large-scale-nanophotonic-phased-array/
- Butler-matrix multi-beam OPA: https://www.nature.com/articles/s44310-025-00059-4
- TFLN OPAs: https://pubmed.ncbi.nlm.nih.gov/40310843 ; https://www.nature.com/articles/s41467-025-67696-3
- Taara Photonics: https://www.optica-opn.org/home/industry/2026/february/taara_launches_photonics_communications_platform/

**FPSA**
- Zhang et al., Nature 603, 253 (2022): https://www.nature.com/articles/s41586-022-04415-8 ; https://bsac.berkeley.edu/publications/large-scale-microelectromechanical-systems-based-silicon-photonics-lidar

**MEMS mirrors and OXCs**
- Mirrorcle: https://www.mirrorcletech.com/wp/products/mems-mirrors/ ; https://mirrorcletech.com/pdf/MirrorcleTech_Device_Prices.pdf ; https://optics.org/press/3087
- Lucent 1100-port OXC: https://ieeexplore.ieee.org/abstract/document/1237580
- Google Palomar/Apollo: https://arxiv.org/pdf/2208.10041
- MEMS FSM with piezoresistive sensing: https://www.nature.com/articles/s41378-025-00935-1 ; https://www.sciencedirect.com/science/article/pii/S0924424725004200

**Galvos**
- https://www.laserchina.com/products/galvo-head/
- http://www.sintecoptronics.com/markinghead.asp
- https://www.scanneroptics.com/products/ultra-galvo-scanner/
- https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=14124

**AODs**
- https://isomet.com/App-Manual_pdf/AO%20Scanning-rev2.pdf
- https://www.rp-photonics.com/acousto_optic_deflectors.html

**Integrated AO**
- https://www.nature.com/articles/s41467-025-59831-x

**SLMs**
- Meadowlark: https://www.meadowlark.com/wp-content/uploads/2025/04/SLM-Standard-DS0325-1920.pdf ; https://www.meadowlark.com/shop/slms/1024-x-1024-spatial-light-modulator/
- TI PLM: https://pmc.ncbi.nlm.nih.gov/articles/PMC9501248/ ; https://www.mdpi.com/2072-666X/13/6/966
- Fraunhofer IPMS: https://www.ipms.fraunhofer.de/en/press-media/press/2023/light-control-with-optical-microsystems.html

**Liquid-crystal steering**
- LCPG: https://www.researchgate.net/publication/258716670_Polarization_Gratings_for_Non-mechanical_Beam_Steering_Applications
- FLC + PG: https://www.tandfonline.com/doi/full/10.1080/02678292.2019.1573327
- Cascaded LC: https://arxiv.org/pdf/2607.28482

**KTN**
- https://ntt-review.jp/archive/ntttechnical.php?contents=ntr200912sf4.html
- https://keytech.ntt-at.com/en/ktn_crystal/prd_2052.html

**Metasurfaces**
- Lumotive LM10: https://optics.org/news/14/8/47
- MIT hybrid PIC-metasurface: https://arxiv.org/abs/2604.13233
- Metalens FPA: https://papers.cool/arxiv/2603.26654

**FSO**
- Koonen AWGR: https://opg.optica.org/jlt/abstract.cfm?uri=jlt-34-20-4802 ; https://opg.optica.org/oe/fulltext.cfm?uri=oe-24-17-19211&id=348466

**Neutral-atom tweezers**
- Manetsch et al.: https://www.nature.com/articles/s41586-025-09641-4 ; https://www.osti.gov/pages/servlets/purl/3376333
- Chiu et al.: https://www.nature.com/articles/s41586-025-09596-6
- Pichard et al.: https://arxiv.org/abs/2405.19503
- Lin et al. (USTC): https://arxiv.org/abs/2412.14647 ; https://phys.org/news/2025-08-ai-technique-defect-free-arrays.html
- Wang et al. (Tsinghua): https://arxiv.org/abs/2606.02715
- Bluvstein et al.: https://www.nature.com/articles/s41586-022-04592-6
- Lu et al.: https://arxiv.org/abs/2510.11451
- Picard & Endres: https://arxiv.org/abs/2510.07633
- Per-column AOD design: https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12911/2692620/
- Crossed-AOD constraints: https://arxiv.org/html/2508.02670 ; https://arxiv.org/pdf/2512.16774
- TFLN quantum-control photonics: https://www.researchgate.net/publication/394473130
- VIPA SLM: https://arxiv.org/abs/2608.18071

**Focus**
- Acousto-optic lens: https://www.researchgate.net/publication/44852499 ; https://pubmed.ncbi.nlm.nih.gov/27749836/
- MEMS varifocal review: https://www.nature.com/articles/s41378-022-00481-0
- Kilo-DM: https://bostonmicromachines.com/products/deformable-mirrors/standard-deformable-mirrors/
- Optotune EL-10-30: https://archive.optotune.com/images/products/Optotune%20EL-10-30.pdf
- TAG lens: https://pubmed.ncbi.nlm.nih.gov/41845802/
- Lateral-to-axial remote focus: https://www.nature.com/articles/s41377-020-00401-9
- Optical-pickup actuators: https://www.researchgate.net/publication/224126794
- Phone autofocus voice coil: https://www.ti.com/lit/ds/symlink/drv201a.pdf

**Multi-scale optics**
- AWARE-2: https://www.nature.com/articles/nature11150

**Fibre positioners (analog for field-plane tiling)**
- DESI (5,000 positioners, 5 µm RMS, 10.4 mm pitch): https://arxiv.org/pdf/1807.09907

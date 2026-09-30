# R5: Optical-trap (photophoretic) volumetric displays, state of the art 2016–2026

Compiled 2026-09-30. Scope: hard numbers for a room-scale, screenless, glasses-free "Iron Man" display
built from optically trapped micro-particles drawn at persistence-of-vision (POV) speed.

**Provenance tags:** [FULL] = full text read. [SNIPPET] = search-engine snippet or abstract (the
number is quoted, but I did not see its context in the paper). [MEMORY] = model recall, not re-verified.
[ESTIMATE] = my own calculation, with inputs stated.
**Access caveat:** WebFetch was egress-blocked for every publisher, arXiv, PMC, university, patent and
Wikipedia host I tried (nature.com was not attempted; NSF-PAR, JoVE, ANU, BYU, Cal Poly, J-STAGE,
Semantic Scholar and others were all blocked). No paper was read in full, so **nothing below is
[FULL]**. Every number is from a snippet or abstract, or it is labelled MEMORY or ESTIMATE.
The web-search budget (200 calls) was used up before a few last checks; see Gaps.

---

## KEY NUMBERS

| Quantity | Value | Conditions | Source | Tag | Conf. |
|---|---|---|---|---|---|
| OTD image-point (voxel) size | ~10 µm ("ten-micrometre image points") | single cellulose particle, POV | Smalley et al., *Nature* 553, 486 (2018) abstract | SNIPPET | High |
| Trap wavelength (display) | 405 nm diode ("near-invisible", Blu-ray) | trap beam, separate from RGB illumination | Nature 2018; BYU press; RSI 2021 | SNIPPET | High |
| Trap mechanism | aberration trap: spherical aberration + (oblique) astigmatism | single lens, loosely focused | Nature 2018 abstract; AO 2019 | SNIPPET | High |
| Trap lens focal length | 125 mm; x/y galvo scanners with 30 mm aperture | Nature 2018 Methods | Nature 2018 (via Gale full-text snippet) | SNIPPET | Med |
| Early prototype trap power | 3–4.06 W from a 10 W Verdi (532 nm) | "early single-beam display prototypes" | Nature 2018 Methods (snippet) | SNIPPET | Med |
| Test-rig laser | 500 mW, 405 nm diode; practical test range 10–500 mW | BYU automated trap rig | Barton et al., *RSI* 92, 103002 (2021) / AO 2019 | SNIPPET | High |
| Lowest successful trap power | 18 mW; "min hold power < 24 mW" | 405 nm | BYU rig papers (RSI 2021 / AO 2019) | SNIPPET | Med-High |
| Power delivered to trap (LCOS expt) | 48 mW (from a 100 mW 405 nm diode) | LCOS-shaped trap | Rogers et al., *Appl. Opt.* 58, G363 (2019) | SNIPPET | Med |
| Max particle linear velocity | >1,827 mm/s | "tests optimized for velocity" | Nature 2018 (snippet) | SNIPPET | Med-High |
| Max particle acceleration | >5 g | same | Nature 2018 (snippet) | SNIPPET | Med-High |
| Earlier velocity/accel. | >3 g, 1.5 m/s (preliminary) | 2017 undergraduate ("Poisson") trap | Goodsell & Smalley, BYU JUR 2017 | SNIPPET | Med |
| Controllable air speed | up to 2 m/s relative to air; cm-scale patterns | photophoretic trap, room air | Peatross, Smalley et al., *Proc. SPIE* 10723, 1072302 (2018) | SNIPPET | High |
| Vector image throughput | 1,307 vertices at 12.8 frames/s = 16,700 points/s | single particle, 2018 | Nature 2018 (snippet) | SNIPPET | Med-High |
| POV refresh floor | >10 frames/s | flicker threshold used by BYU | Rogers & Smalley, *Sci. Rep.* 11, 7522 (2021) | SNIPPET | High |
| Demonstrated image volume | < ~1 cm³ ("ping-pong-ball" volume); complex images were long exposures of up to ~30–60 s | single particle | SPIE 12445 (2023) abstract; CACM Oct 2018; LFW/N&V coverage | SNIPPET | High |
| Scaling goal (multi-particle) | 1 cm³ → 100 cm³ by moving many particles along simple paths | binary grating, Fresnel lens (preliminary) | Bond, Kuttler, Hales, Smalley, *Proc. SPIE* 12445, 124450I (2023) | SNIPPET | High |
| Particles in a display simultaneously | 1 (all published OTD images); multi-particle only "preliminary" | – | Nature 2018; SPIE 2023 | SNIPPET | High |
| Trap hold time (best) | mean 1.1 h, pickup 87% (67 attempts); max >17.2 h | 532 nm, 3.0 W | BYU trap-rig (RSI 2021 / JoVE) | SNIPPET | Med-High |
| Rig throughput | ~250 trapping trials/hour; SE <1%, accuracy >98% | automated rig | RSI 2021; OSA 3D 2021 3F4A.3 | SNIPPET | High |
| Best focal-length window | 80–160 mm is most efficient (60–200 mm tested); a maximum trapping focal length exists | 405 nm; 532/630 nm also compared | Ababseh, Childers, Jin, *Proc. SPIE* 12443 (2023); DH 2022 Th4A.5 | SNIPPET | High |
| Retro-reflector gain | ~3× average trapping time | Cal Poly POT rig | Garcia et al., *Proc. SPIE* 13388, 133880E (2025) | SNIPPET | Med |
| Added spherical aberration | no significant effect on trap rate (p = 0.183, 80 trials per level) | soot particles, Revibro mirror | Cropper, Grochett, Smalley, *Proc. SPIE* 13390 (2025) | SNIPPET | High |
| Large gold particles | radius ≥1 µm solid Au held >1 h; AOM-drawn "boat" trap | for plasmonic display points | Mirzaei-Ghormish, Griffith, Smalley, Camacho, *PR Applied* 22, 064042 (2024) | SNIPPET | High |
| Photophoretic force vs radiation pressure | ~10⁴× (≈4 orders); 4–5 orders vs gradient force; ~10² vs radiation pressure for 1–10 µm | absorbing particles in air | Lin et al., JOSA B 34, 1242 (2017); Desyatnikov et al., Opt. Express (2009) | SNIPPET | High |
| Measured trapping force | 1.39(9) pN (Gaussian); 2.49(18) pN (Gaussian + HG) | fibre-based PP tweezers | likely dual-mode fibre tweezers, arXiv 1704.02248 | SNIPPET | Med (attrib.) |
| Transport speed without loss | 5 mm/s axial | dual-mode fibre tweezers | arXiv 1704.02248 | SNIPPET | Med |
| Vortex-beam guiding | few mW (<1 mW quoted); 0.1–10 µm C agglomerates; few mm; up to 1 cm/s; ±2 µm | dual vortex, w = 8.4 µm | Shvedov et al., *Opt. Express* 17, 5743 (2009) | SNIPPET | High |
| Longest guided transport | ~100 µm particles over 1.5 m pipeline, ±10 µm positioning | vortex "optical pipeline" | Shvedov et al., *PRL* 105, 118103 (2010) | SNIPPET | High |
| Tractor beam in air | 200 µm Au-coated (<25 nm) hollow glass spheres, up to 20 cm, reversible by polarization | single beam, photophoretic | Shvedov et al., *Nat. Photon.* 8, 846 (2014) | SNIPPET | High |
| Many particles in one static trap | > several hundred particles | tapered-ring field, >100 mW; ρ = 1–7 g/cm³ | *Opt. Express* 22, 23716 (2014) | SNIPPET | High |
| Fastest orbital motion in air | 7 µm sphere, 340 Hz on 120 µm track (≈4 cm/s), up to 10 g | ℓ = 242 beam | Droby … Carmon, *Sci. Adv.* 11 (39) (2025) | SNIPPET | High |
| Macroscopic photophoretic levitation | 6 mm mylar/CNT disks at 10–30 Pa; nanocardboard at 10–200 Pa; ~0.5 mm hover only at 1 atm | ~1 sun | Azadi et al., *Sci. Adv.* (2021); Cortes et al., *Adv. Mater.* 32, 1906878 (2020) | SNIPPET | High |
| Macro levitation 2025 | 1 cm alumina/Cr structure at 26.7 Pa, 0.55 sun | thermal transpiration | Schafer et al., *Nature* 644, 362 (2025) | SNIPPET | High |
| PP force per absorbed mW, 10 µm sphere at 1 atm | ~3×10⁻⁹ N/mW (k_p = 0.1 W/m·K, J₁ = 0.5); ~4×10⁻¹⁰ (k_p = 1) | ideal upper bound, continuum limit | this work: Yalamov/Reed and Rohatschek formulas | ESTIMATE | Order-of-mag |
| Same, 100 µm sphere | ~3×10⁻¹⁰ N/mW (k_p = 0.1); scales ∝ 1/(a·(k_p + 2k_g)) | – | this work | ESTIMATE | Order-of-mag |
| Stokes drag at 2 m/s | 3.4 nN (10 µm), 17 nN (50 µm), 34 nN (100 µm); Re = 1.3–13 | air, 20 °C | this work | ESTIMATE | High (physics) |
| Weight | 7.7 pN (10 µm, ρ = 1.5), 0.96 nN (50 µm), 7.7 nN (100 µm) | – | this work | ESTIMATE | High |
| Room-scale particle count | ~50–170 particles for 10 m of drawn line at 10–30 Hz and 1.8 m/s; ~550–1,700 for 100 m | POV line budget | this work | ESTIMATE | Med |

---

## 1. BYU (Smalley) optical trap display (OTD) and allied groups

**Core paper.** Smalley, Nygaard, Squire, Van Wagoner, Rasmussen, Gneiting, Qaderi, Goodsell, Rogers,
Lindsey, Costner, Monk, Pearson, Haymore, Peatross, "A photophoretic-trap volumetric display",
*Nature* 553, 486–490 (25 Jan 2018), doi:10.1038/nature25176 [SNIPPET; the author list beyond Smalley,
Nygaard and Squire is MEMORY]. The key facts:
- A cellulose particle (the group calls it "black liquor"; estimated at ~10 µm) sits in a photophoretic
  trap. The trap is made by spherical aberration plus astigmatism of a 405 nm beam. The trap is scanned
  through the volume while collinear R, G and B lasers illuminate the particle. The result is a large
  colour gamut, low speckle and ~10 µm image points [SNIPPET].
- Methods (Gale full-text snippet): a 125 mm lens, x/y galvanometers with 30 mm aperture and
  Al-coated mirrors, and microcontroller drive. Photos were taken through a 405 nm dichroic used as a
  notch filter. Early prototypes used a 10 W Verdi (532 nm) at 3–4.06 W [SNIPPET, Med].
- Performance: velocity >1,827 mm/s and acceleration >5 g. Vector images of 1,307 vertices were drawn at
  12.8 fps, which is 16,700 points/s. The authors say an order-of-magnitude gain in scan rate or
  complexity "should be possible without further optimization" [SNIPPET, Med-High].
- Limits stated in coverage: the maximum speed relative to air is ~2 m/s, so complex images had to be
  drawn over ~30 s (long exposures) [SNIPPET, Laser Focus World and Nature N&V coverage]. The volume is
  about the size of a ping-pong ball, and exposures took up to ~1 min (CACM, Oct 2018) [SNIPPET].
- Nature N&V: Blundell, "Trapped particle makes 3D images", *Nature* 553, 408 (2018) [SNIPPET].

**Trap physics and robustness papers (BYU / Peatross).**
- Peatross, Smalley, Rogers, Nygaard, Laughlin, Qaderi, Howe, *Proc. SPIE* 10723, 1072302 (2018): the
  trap is strong enough to draw cm-scale patterns. Control is kept at air speeds up to 2 m/s [SNIPPET].
- Ware, Peatross, Smalley, Tveten, Peatross, *Proc. SPIE* 11798 (2021), "Preferred locations in a laser
  beam…": particles prefer diffraction features created by spherical aberration. How a near-unidirectional
  beam gives an upstream restoring force was still unexplained [SNIPPET].
- Rogers, Laney, Peatross, Smalley, "Improving photophoretic trap volumetric displays [Invited]",
  *Appl. Opt.* 58(34), G363–G369 (2019). It covers trapping, scanning, scaling, robustness, safety and
  occlusion. Findings: scaling means replicating the trap and scanning several particles in sync.
  Anisotropic scatter allows occlusion. It proposes coated uniform microspheres instead of black liquor.
  It names the next steps as SLM parallel traps, AOD/EOD beam steering and engineered particles
  [SNIPPET]. The LCOS experiment delivered 48 mW to the trap from a 100 mW diode [SNIPPET, Med].
- Trap test rigs: Barton, Huffman, Briceno, Darm, Smalley, *RSI* 92, 103002 (2021), plus OSA 3D 2021
  paper 3F4A.3 and a JoVE protocol. The rig starts from a 500 mW 405 nm diode and tests 10–500 mW.
  The lowest successful trap was 18 mW, and minimum hold power was <24 mW at 405 nm. The rig runs about
  250 trials/hour. The biggest effects on hold time and airflow tolerance come from power, wavelength and
  NA. Shorter wavelengths trap better for both black liquor and tungsten. At 532 nm and 3.0 W: 87% pickup,
  mean hold 1.1 h, maximum >17.2 h. More power helps "until … too destructive for the particle
  reservoir" [SNIPPET].
- Cropper, Grochett, Smalley, *Proc. SPIE* 13390, 1339008 (2025): spherical aberration was varied with a
  Revibro tunable-focus mirror, with 80 automated trials per level on soot particles. There was no
  significant effect (ANOVA p = 0.183) [SNIPPET].
- Mirzaei-Ghormish, Griffith, Smalley, Camacho, *PR Applied* 22, 064042 (Dec 2024; arXiv 2310.04860).
  An AOM-scanned, horizontally oriented "boat" trap self-loads solid gold of radius ≥1 µm and holds it
  >1 h. The trap can scan axially or be enlarged, aimed at plasmonic and metallic display points. A JoVE
  protocol followed in 2026 [SNIPPET].

**Displays and optics after 2018.**
- Rogers & Smalley, "Simulating virtual images in optical trap displays", *Sci. Rep.* 11, 7522 (2021).
  A time-varying perspective backdrop simulates depth beyond the physical volume. POV needs >10 fps.
  The 2021 press demos (Star Trek ships, "lightsabers") were still drawn with one particle
  [SNIPPET]. I found no velocity or image-size numbers in snippets.
- Bond, Kuttler, Hales, Smalley, *Proc. SPIE* 12445, 124450I (2023), "Diffractive optics for scaling
  photophoretic trap displays". It moves many particles on simple paths rather than one particle on a
  complex path, aiming at 1 → 100 cm³. It reports preliminary binary-grating and Fresnel-lens results
  [SNIPPET]. A BYU concept figure shows a "three-colour, multiple-particle volume raster at video rate,
  20 cm tall". This is a **concept, not a demonstration** [SNIPPET; attribution unclear].
- Chae, Bang, Jeong, B. Lee (SNU), OSA 2020 JTh2A.34: a focus-tunable lens replaces the bulky z-stage
  [SNIPPET].
- Cal Poly (X. Jin group): Childers, Ababseh, Jin, DH 2022 Th4A.5, found the first measured *maximum
  focal length* beyond which nothing traps. They note that images are "limited to 1 cm³".
  Ababseh et al., *Proc. SPIE* 12443 (2023): capture is best at f ≈ 80–160 mm (60–200 mm tested) at
  405 nm, and 405, 532 and 630 nm were compared. Garcia et al., *Proc. SPIE* 13388 (2025): retro-reflectors
  give ~3× longer trapping times [SNIPPET]. The actual f_max value was not captured (see Gaps).
- "Hunt for the Hologram" (BYU, 2023–25): classroom "UFO" trap kits used in 5 classrooms to screen
  particles (graphite and yeast were trapped). It is a crowdsourced particle search [SNIPPET].
- NA: not recovered. [ESTIMATE] With f = 125 mm and a beam of a few mm, the NA is ≈0.01–0.05. This is a
  loosely focused, long-working-distance trap, which suits a room-scale throw, but f_max (Cal Poly) is a
  warning sign.

**Colour and illumination.** Collinear RGB lasers illuminate the particle, which acts as a passive
scatterer. The trap light is 405 nm and "near-invisible", yet visible enough to see the particle
[SNIPPET]. RGB wavelengths and powers were **not recovered**. [MEMORY] The paper reports a gamut larger
than the display standards it was compared with; I do not remember the numbers.

**Particle loss.** Published figures are hold times on a static rig (mean 1.1 h, maximum 17 h at 3 W,
532 nm). I found no published per-frame loss rate while scanning at 1–2 m/s. Loss mechanisms named in the
papers: airflow, heating that damages the particle reservoir, and the trap "hopping" that the boat trap
avoids [SNIPPET]. The 2018 display re-trapped from a reservoir [MEMORY].

## 2. Photophoretic force physics in air at 1 atm (5–100 µm)

**Regime.** At 1 atm the mean free path is λ ≈ 65–68 nm, so Kn = λ/a ≈ 10⁻³–10⁻² for 5–100 µm. That is
the continuum/slip regime (Reed 1977; Yalamov, Kutukov & Shchukin 1976) [SNIPPET].

**Two forces** [SNIPPET]:
- *ΔT-force* comes from uneven surface temperature (thermal creep, slip coefficient κ_s ≈ 1.14).
  It depends on k_p, k_g and the absorption-asymmetry factor J₁. Its sign can reverse (negative
  photophoresis) for weakly absorbing or transparent particles.
- *Δα-force* comes from uneven thermal accommodation coefficient over the surface. It does not depend on
  particle orientation relative to the light, only on the particle body. One source states that at 1 atm
  it dominates for µm absorbing particles in air, and that for µm spheres it exceeds gravity once the
  accommodation variation Δα > 0.055 [SNIPPET, attribution to one nonuniform-accommodation paper, Med].

**Formulas.**
- Continuum ΔT-force (Yalamov/Reed form) [MEMORY, standard form]:
  F_ΔT ≈ −(9π/2)·μ²·a·I·J₁ / [ρ_g·T·(k_p + 2k_g)], with a thermal-creep factor (~1.1) sometimes applied.
  Force per absorbed power (P_abs = πa²I·Q_abs):
  F/P_abs ≈ 9μ²J₁ / [2ρ_g·T·(k_p+2k_g)·a·Q_abs] ∝ 1/a.
- Rohatschek (1995) interpolation across all pressures [SNIPPET]:
  F(p) = 2F_max / (p/p_max + p_max/p), with p_max = (η/r)·√(12RT/M) and
  F_max = (πηr²I / 2k_p)·√(R/(3TM)).
  [ESTIMATE] For air at 293 K, p_max ≈ 3.6 kPa (d = 10 µm), 730 Pa (50 µm) and 360 Pa (100 µm).
  At 1 atm the force is therefore ~15–150× below its maximum. That is why cm-scale bodies need 10–200 Pa.
- [ESTIMATE] Both formulas agree within ~30%. The ideal upper bound is ≈3×10⁻⁹ N per absorbed mW for a
  10 µm, k_p ≈ 0.1 W/m·K particle, and ≈3×10⁻¹⁰ N/mW at 100 µm. For comparison, radiation pressure
  gives 3.3×10⁻¹² N/mW, so the ratio is 10²–10³, consistent with the "2–4 orders" in the literature.
  A high-k_p particle (k_p ≈ 1, e.g. a glassy or metallic core) loses about 7×. **Low thermal
  conductivity plus strong asymmetric absorption is the design lever.**
- Measured small-scale forces: 1.39 ± 0.09 pN and 2.49 ± 0.18 pN restoring force in fibre tweezers
  [SNIPPET]. Trap stiffness rises linearly with intensity (Lin et al. 2017, forced oscillation, C and
  CuO particles) [SNIPPET]. A stiffness-measurement method was reported in *APL* 125, 091105 (2024);
  its values were not recovered.
- Field data (Horvath, *KONA* 31, 2014): 400 nm Fe-oxide particles in solar-constant flux move at
  50–300 µm/s photophoretically versus 6–30 µm/s settling [SNIPPET].

**Gravity versus lift versus drag** [ESTIMATE, Stokes, η = 1.81×10⁻⁵ Pa·s]:

| d | weight (ρ = 1.5) | Stokes drag at 2 m/s | Re | τ_relax | ideal P_abs to cancel drag |
|---|---|---|---|---|---|
| 10 µm | 7.7 pN | 3.4 nN | 1.3 | 0.46 ms | ~1 mW |
| 50 µm | 0.96 nN | 17 nN | 6.6 | 12 ms | ~30 mW |
| 100 µm | 7.7 nN | 34 nN | 13 | 46 ms | ~120 mW |

Implication: **drag, not gravity, sets the speed limit.** v_max ∝ F_restore/(6πηa) ∝ P_abs/a² in the
continuum limit. The observed ~2 m/s with 20–500 mW traps means the effective restoring efficiency is only
a few % of the ideal bound. A 5 g acceleration needs only ~40 pN on a 10 µm particle, which is trivial.
The acceleration limit is therefore trap-geometry and dynamics, not force [ESTIMATE].
At 1.83 m/s and 5 g the minimum turn radius is v²/a ≈ 6.8 cm, so **sharp corners force slow-downs**
[ESTIMATE].

**Macroscopic photophoretic levitation (Bargatin, Keith and others).**
- Cortes et al., *Adv. Mater.* 32, 1906878 (2020): nanocardboard plates with 50 nm walls. At 1 atm they
  only hover ~0.5 mm over a substrate (air cushion). Mid-air levitation happens at 10–200 Pa, with
  payloads heavier than the plate [SNIPPET].
- Azadi et al., *Sci. Adv.* (Feb 2021, abe1127): 0.5 µm mylar with a CNT underside. 6 mm disks levitate
  at 10–30 Pa under roughly 1-sun intensity, and a shaped light field traps them [SNIPPET]. Intensity in
  W/cm² was not recovered.
- Bargatin group, *PR Applied* 21, 044019 (2024): Ge selective absorber (~80% visible absorption,
  emissivity ~0.1) levitates at up to 43% lower irradiance than CNT flyers. A NASA NIAC award followed
  in 2025 [SNIPPET].
- Schafer, Kim, Sharipov, …, Vlassak, Keith, *Nature* 644, 362 (2025): a 1 cm perforated alumina/Cr
  bilayer flies at 26.7 Pa under 0.55 sun. Concept flyers are 3–80 cm for 60–80 km altitude [SNIPPET].
- **Bottom line:** every macroscopic photophoretic levitation needs about 10–200 Pa (10⁻⁴–2×10⁻³ atm).
  None works in free air at 1 atm. At 1 atm only µm-scale particles, up to ~200 µm hollow shells, are
  photophoretically trapped.

## 3. Other optical trapping and transport in air

- **Vortex and doughnut traps (ANU: Shvedov, Rode, Desyatnikov, Krolikowski, Kivshar).**
  - *Opt. Express* 17, 5743 (2009): dual counter-propagating vortices, w = 8.4 µm, a few mW (the
    theory-versus-experiment companion paper quotes <1 mW). They guided 0.1–10 µm C agglomerates over a
    few mm at up to 1 cm/s with ±2 µm stability [SNIPPET].
  - *Appl. Phys. A* 100, 327 (2010): the same system as a review [SNIPPET].
  - *PRL* 105, 118103 (2010), "Giant optical manipulation": carbon agglomerates of 0.1–100 µm and
    carbon-coated hollow glass of 50–100 µm. It moved a 100 µm particle along a **1.5 m** "optical
    pipeline" with ±10 µm positioning, >1000× the previous manipulation distance. Longer distances need
    more power and risk burning the particle. Speed is ~mm/s [SNIPPET; speed Low].
  - *Opt. Lett.* 37, 1934 (2012): multi-beam interference lattice for 3D manipulation of particle
    *ensembles* [SNIPPET]. The count was not recovered.
  - *Nat. Photon.* 8, 846 (2014), tractor beam: 200 µm hollow glass with <25 nm Au. It pulls or pushes
    over **up to 20 cm**, reversed by polarization (radial versus azimuthal) [SNIPPET].
- **Bottle beams and other configurations:** "Robust trapping and manipulation of airborne particles with
  a bottle beam", *Opt. Express* 19, 17350 (2011); "Optical configurations for photophoretic trap of single
  particles in air", *RSI* 87, 103104 (2016); Raman-trap *Opt. Express* 20, 5325 (2012); counterflow-nozzle
  loading *APL* 104, 113507 (2014) [SNIPPET titles only; authors and numbers not recovered].
- **Many particles:** a tapered-ring field holds **>several hundred** particles at >100 mW, with
  ρ = 1–7 g/cm³ (*Opt. Express* 22, 23716, 2014). A single-mode fibre plus lens traps several particles
  and chains (*J. Opt.* 24, 074003, 2022). A multi-linear cylindrical-lens trap gives several trapping
  planes (*Optik*, Oct 2022). A multimode-fibre speckle trap is "ultrastable" (*ACS Photonics* 11, 159,
  2024) [SNIPPET]. **None of these moves the particles independently.** I found no demonstration of
  independent SLM-addressed photophoretic trap arrays in air. BYU names it as the next step.
- **Holographic optical tweezers (HOT) in air** exist for *transparent aerosol droplets* using
  gradient force (Burnham & McGloin, *Opt. Express* 14, 4175, 2006). High-NA gradient traps in air are
  limited to ~µm droplets and short working distance [SNIPPET title; MEMORY for details].
- **Conveyors:** the optical Archimedes' screw (Hadad … Roichman, Bahabad, *Optica* 5, 551, 2018)
  moves µm carbon particles up- or downstream over **0.5 cm** with controlled velocity [SNIPPET].
  Dual-mode fibre tweezers reach 5 mm/s axial without loss [SNIPPET].
- **Speed record (orbital):** Droby … Roichman, Carmon, *Sci. Adv.* (2025): a 7 µm sphere orbits at
  340 Hz on a 120 µm track (≈4 cm/s), up to 10 g, underdamped in air, Q·f = 5300 Hz, ℓ = 242 [SNIPPET].
- **Takeaway:** long-distance transport in air (20–150 cm) is proven, but only at mm/s–cm/s. The
  m/s-class motion needed for POV has been shown only by BYU aberration traps over ~cm strokes.

## 4. Emissive or upconverting particles, trap-powered emission, and commercial efforts

- **No published OTD uses upconverting or fluorescent particles** (none found through 2026-09). One
  snippet (likely the Nature 2018 discussion or a BYU patent) describes "active" image points: fluorescent
  particles or aerosol droplets trapped by an IR beam and excited by a low-power UV beam for coloured
  emission. It is a proposal, not a demonstration [SNIPPET, attribution Med-Low].
- **Nearest neighbours:**
  - Upconverting Er/Yb single particles have been *levitated in a Paul trap in vacuum*, with luminescence
    measured over 0.1–10³ W/cm² at 980 nm (*ACS Photonics* 12, 1783, 2025) [SNIPPET].
  - Full-colour upconversion *solid-glass* volumetric displays exist (*Light Sci. Appl.* 2024,
    s41377-024-01672-2) [SNIPPET].
  - **Implication:** an IR (e.g. 980 nm) trap that also pumps upconversion would merge trap and
    illumination beams. It remains untested for photophoretic trapping, and UCNP efficiency at
    ~10²–10⁴ W/cm² trap intensities is typically ≲1–10% [MEMORY/ESTIMATE].
- **Other free-space POV scatterers (for comparison):**
  - Acoustic levitation: Foisy's 1 mm foam ball moves at >1 m/s in 100×100×140 mm with RGB LEDs
    (hackster.io) [SNIPPET]; OptiTrap (*ACM TOG* 2022) [SNIPPET].
  - Electrically driven levitated scatterers (arXiv 1806.06662) [SNIPPET title].
  - Femtosecond-laser plasma voxels: Kumagai/Hayasaki, dual-path SLM rendering in Xe at SIGGRAPH 2024
    E-Tech, and a "fist-sized" display in *J. SID* 2025 [SNIPPET]. These are not trap-based.
- **Commercial:** BYU tech-transfer lists "optical trap display and printing technology". Patents seen
  in results: US 10,129,517 (full-colour free-space volumetric display with occlusion), US 10,989,931
  (photophoretic display device), US 11,173,837 (optical cloaking with a photophoretic OTD),
  US 11,130,287 (optical trap 3D printing) and US 12,276,593 (focused hollow-beam trap). Assignees were
  not verified. **No OTD startup or product was found for 2020–2026.** A 2024 *Inside Higher Ed* story
  mixed up OTD with Proto's LCD "hologram" boxes, which are not volumetric [SNIPPET].

## Design implications for a room-scale OTD [ESTIMATE]

1. **Particle budget.** At the demonstrated ~1.8 m/s and 10–30 Hz refresh, one particle draws 6–18 cm
   of line per frame. A room wireframe with 10 m of line needs ~56–170 independently steered particles.
   100 m needs ~550–1,700. The 2018 throughput of 16,700 points/s is the single-particle baseline.
2. **Throw distance.** The demonstrated focal lengths are 80–160 mm, and a maximum trapping focal
   length exists. Room scale (1–3 m throw) is **~10–20× beyond any demonstrated photophoretic
   *display* trap**. Only vortex pipelines (1.5 m) and tractor beams (20 cm) reach that range, and they
   run at mm/s.
3. **Drag-limited speed.** v_max ∝ P_abs/a². Smaller, low-k_p, strongly asymmetric absorbers are
   faster per mW but scatter less light, so brightness and speed trade off directly.
4. **Laser load.** At 20–500 mW per trap, 100–1,000 traps means 2–500 W of 405 nm light in a room. That
   is a serious eye-safety problem (AO 2019 lists safety as a core issue).

## Gaps (not recovered; all due to blocked full text or the search budget)

- Nature 2018: exact trap power at 405 nm in the display, beam diameter and NA, RGB laser wavelengths
  and powers, particle size distribution, image dimensions (mm), and the loss/re-trap rate during
  scanning.
- AO 2019: acceleration and speed data after 2018, and the parameters of the multi-particle LCOS trial.
- SPIE 12445 (2023): how many particles were trapped at once and their spacing.
- Cal Poly DH 2022: the numerical maximum trapping focal length.
- APL 125, 091105 (2024) and JOSA B 2017: stiffness values in N/m.
- Shvedov PRL 2010 and Nat. Photon. 2014: laser power (W) and transport speeds.
- Bargatin Sci. Adv. 2021: intensity in W/m².
- Whether any 2024–2026 BYU paper shows more than one particle drawing an image. None was found; the
  2025–26 SPIE Practical Holography XXXIX/XL/XLI contents were only partly visible.
- Any demonstration of trap-beam-pumped emission (upconversion or fluorescence) in a photophoretic trap.
- Review to read in full when access allows: Pahi et al., "Photophoretic Trapping: Fundamentals,
  Advances and Future Directions", arXiv 2512.09401 / *ChemPhysChem* 2026 (e202500890).

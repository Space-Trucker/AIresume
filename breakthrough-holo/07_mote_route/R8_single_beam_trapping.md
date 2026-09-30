# R8: Single-beam 3D photophoretic trapping in air: mechanism, measured strength, pull, range and sensing

Compiled 2026-09-30. This report asks whether one head, with a single beam per mote, could replace the multi-head push trap. The
question is whether a single-beam trap can deliver a useful fraction η of the ideal photophoretic force as a restoring force in
**every** direction, including back toward the source.

**Provenance tags:** [FULL] = full text read. [SNIPPET] = search-engine snippet or abstract. [MEMORY] = model recall, not
re-verified. [ESTIMATE] = my own calculation or argument, with inputs stated.
**Access caveat:** WebFetch and curl were egress-blocked for every host tried: nature.com, pubs.aip.org, arxiv.org, the ANU
repository, USPTO, and (via curl) Optica, Wiley, IOP, Springer, PMC, NSF-PAR, BYU and Cal Poly repositories, Crossref,
OpenAlex and Semantic Scholar. **Nothing below is [FULL].** Numbers come from snippets or abstracts; the rest is labelled
MEMORY or ESTIMATE. This report builds on R5 (`R5_optical_trap_displays.md`) and does not repeat its display numbers except
where they are needed here.

---

## Bottom line

1. **No published mechanism gives a strong upstream (toward-source) force from a single forward beam acting on an opaque,
   isotropic particle.** For a positive-photophoretic sphere, every ray in a forward beam has k_z > 0, so the ΔT force has
   F_z > 0. For any opaque body, the upstream component is bounded by about tan θ_max ≈ NA (0.05–0.1) of |F| [ESTIMATE, §1.3].
   Published single-beam "3D" traps get axial balance from one of these instead:
   - gravity, with a vertical beam;
   - particle asymmetry: the Δα force, negative photophoresis, or rotation-coupled forces;
   - backward light: counter-propagating beams, a confocal fold, or a retro-reflector.

   BYU's own group calls the upstream restoring force in its aberrated traps an **open question** (Ware et al., SPIE 2021)
   [SNIPPET].
2. **BYU's 1.83 m/s is transverse speed.** The galvos scan x and y. Depth (z) was moved by a "bulky linear stage" (Chae et
   al., 2020) [SNIPPET]. BYU traps are equally stable at 0 g and 2 g (Peatross et al., SPIE 2018) [SNIPPET]. So a
   non-gravitational axial restoring force exists, but its magnitude is only bounded below: at least about 2× the particle's
   weight, i.e. η_axial ≳ 0.005.
3. **The BYU transverse speed does imply a high transverse η.** Under the continuum ΔT model, 1.83 m/s needs
   η_transverse ≈ 0.33–0.9, and only in the most favourable corner: particle radius a ≈ 2.5 µm, k_p ≈ 0.05 W/m/K,
   ΔT ≈ 500 K. At a = 5 µm it needs η > 1 unless k_p ≤ 0.05 and ΔT ≥ 500 K [ESTIMATE, §7]. So "η ≳ 0.4" is right for the
   **transverse** plane only. The alternative reading is that BYU's particle was small (a ≲ 3 µm) and very hot.
4. **The strongest demonstrated pulling (upstream) speeds are 1–10 cm/s.** Lin, Hart & Li (2015) reached this with negative
   photophoresis over about 1 m. Shvedov (2014) reached 0.8 mm/s with a polarization-switched shell. Both are 20–2000× below
   BYU's transverse speed, and neither was normalised to push force per watt [SNIPPET].
5. **Best estimate for a single head at 1550 nm, 1.5 m, NA 0.05–0.1, a = 3–10 µm** [ESTIMATE, §7]:
   - η_transverse ≈ 0.1–0.6;
   - η_downstream ≈ 1;
   - **η_upstream ≈ 0 for an opaque mote.** The bound is ≲ NA; the achievable value is probably ≪ 0.05.

   **η_single is therefore set by the upstream direction and is ≈ 0.** A single head works only if at least one of these holds:
   - the mote is engineered to pull (a lensing or Janus mote, or a second wavelength or polarization; §3);
   - passive back-reflected light is added;
   - the content is restricted so that along-beam velocity is small, i.e. the gravitational settling speed of 0.3–18 mm/s,
     or cm/s with a pull mote.

---

## KEY NUMBERS

| Quantity | Value | Conditions | Source | Tag |
|---|---|---|---|---|
| Upstream restoring force in aberrated single-beam traps | "needs to be explained … open question" | BYU aberrated traps; particles sit at dark rings where S_z drops to ~1% of nearby values while radial S stays significant | Ware, A. Peatross, Smalley, Tveten, J. Peatross, *Proc. SPIE* 11798 (2021) | SNIPPET |
| Gravity dependence of BYU trap | no noticeable stability difference at 0 g and 2 g; orbits/oscillations with excursions of tens of µm and up to 10 g; control kept to 2 m/s air speed | BYU display traps | J. Peatross et al., *Proc. SPIE* 10723, 1072302 (2018) | SNIPPET |
| BYU axial (z) scanning | "bulky linear stage"; replaced by a focus-tunable lens in a compact variant | OTD architecture | Chae, Bang, Jeong, B. Lee, OSA Imaging Congress 2020, JTh2A.34 | SNIPPET |
| BYU transverse record | > 1.827 m/s, > 5 g | "tests optimized for velocity" | Smalley et al., *Nature* 553, 486 (2018) (via R5) | SNIPPET |
| Poisson-spot trap (enclosed dark oval) | stable at > 3 g, 1.5 m/s (preliminary) | built because aberration and vortex traps leave particles "free to move up and downstream" | Goodsell & Smalley, BYU JUR 2017 | SNIPPET |
| Display trap power | 80 mW at 405 nm (RGB illumination at 24.4 / 30.5 / 15.89 mW) | BYU display | Rogers et al., *Appl. Opt.* 58, G363 (2019) (attribution Med) | SNIPPET |
| Measured PP trap stiffness | 6.14, 4.26 and 4.15 pN/µm (x axis) | carbon microclusters of 2–13 µm, 640 nm, f = 25 mm lens, ≈ 20 mW during measurement (70 mW to trap) | Pahi et al., *J. Phys. Photonics* 7, 035026 (2025); arXiv 2503.16059 | SNIPPET |
| Stiffness versus power | linear in trapping intensity | C and CuO particles, forced oscillation | Lin, Deng, Wei, Li, Wang, *JOSA B* 34, 1242 (2017) | SNIPPET |
| Archimedes-screw conveyor | ≤ 0.3 mm/s over 0.5 cm, both directions; stiffness "≈ 50 pN/m" (units as quoted, unverified) | 1.4 µm carbon aggregates | Hadad et al., *Optica* 5, 551 (2018) | SNIPPET |
| Trapped-particle temperature | 322 K → 830 K over 200–2950 mW; 18.3 ± 0.4 K per 100 mW | SWCNT / diamond Raman thermometry, universal optical trap (UOT) centre | Ai, Pan, Videen, Wang, *Appl. Spectrosc.* (2023) | SNIPPET |
| PP force response time | up to ≈ 1 s | beam off → particle pulled toward source by residual PP; power up → pushed by radiation pressure | Chen, He, Wu, Li, *PR Applied* 10, 054027 (2018) | SNIPPET |
| Mote thermal time constant | τ_ext ≈ 0.03–1.9 ms; τ_int (k_p = 0.02) ≈ 0.14–7.5 ms | a = 3–10 µm, ρc = 0.3–1.5 MJ/m³K | this work | ESTIMATE |
| Negative-PP pulling | 1–10 cm/s toward source over meter scale; particle rotation 0.2–10 kHz; speed set by intensity | single collimated beam, µm absorbing particles and smut spores | Lin, Hart, Li, *APL* 106, 171906 (2015) | SNIPPET |
| Push versus pull direction | set by particle orientation and morphology, not by size or beam parameters | 10–50 µm CNT particles | Wang, Gong, Pan, Videen, *APL* 109, 011905 (2016) | SNIPPET |
| Polarization tractor | 0.8 mm/s pull at 200 mW; up to 20 cm; reversed by radial ↔ azimuthal polarization | ≈ 200 µm hollow glass (≈ 300 nm wall) + 7–15 nm Au | Shvedov et al., *Nat. Photon.* 8, 846 (2014) | SNIPPET |
| Longest free-space guide | ≈ 1.5 m pipeline, ±10 µm; "several mm/s"; 0.5 m remote deposition at 10 µm accuracy | vortex (doughnut) beam, ≈ 100 µm C-coated hollow glass | Shvedov et al., *PRL* 105, 118103 (2010); phys.org (2010) | SNIPPET |
| Maximum trap focal length (fibre-fed beam) | most particles at f = 75 mm; very few at 100–125 mm; none at 150–200 mm (simulation predicted trapping) | single-mode-fibre beam plus lens | Banerjee group, *J. Opt.* 24, 074003 (2022); arXiv 2201.06526 | SNIPPET |
| Maximum trap focal length (Cal Poly) | best capture at f ≈ 80–160 mm (60–200 mm tested), 405 nm; a limit exists | free-space beam | Ababseh, Childers, Jin, *Proc. SPIE* 12443 (2023); DH 2022 Th4A.5 | SNIPPET |
| Wavelength trend | shorter λ traps better for black liquor and tungsten | BYU rig, 405 / 532 nm | Barton et al., *RSI* 92, 103002 (2021) | SNIPPET |
| Upstream-force bound, opaque body, forward-only light | F_up/\|F\| ≤ tan θ_max ≈ NA = 0.05–0.1 | ΔT force, any shape | this work, §1.3 | ESTIMATE |
| Gravity-only "upstream" speed | settling speed 0.3–18 mm/s | a = 3–10 µm, ρ = 0.3–1.5 g/cm³ | this work | ESTIMATE |
| η_transverse required by BYU 1.83 m/s | 0.33–0.9 (favourable corner); > 1 at a = 5 µm, k_p = 0.1 | continuum ΔT model, Oseen drag | this work, §7 | ESTIMATE |
| η_single at 1550 nm, 1.5 m, NA 0.05–0.1 | transverse 0.1–0.6; upstream ≈ 0 (≤ NA bound) | a = 3–10 µm, opaque mote | this work, §7 | ESTIMATE |
| Shot-noise position precision, 1.5 m | 1–15 nm per sample at 10–50 kHz | 5 % diffuse backscatter of 0.1–0.5 mW absorbed, 0.1–0.3 m collection aperture | this work, §5 | ESTIMATE |
| BFP / balanced detection in air | < 3 fm/√Hz, > 50 MHz bandwidth (75 MHz detector) | 1 µm SiO₂ bead in a dual-beam trap, short range | Li, Kheifets, Medellin, Raizen, *Science* 328, 1673 (2010) | SNIPPET |
| Event-camera latency | < 100 µs at 1000 lux; < 1 ms at 5 lux; 1 Gev/s peak; Si sensor | Sony/Prophesee IMX636 | product brief (2024) | SNIPPET |
| Neuromorphic multi-particle feedback | 3 particles cooled simultaneously, tens detected; µs timestamps, sub-ms latency | charged microspheres, Paul trap in vacuum | Ren et al., *Nat. Commun.* (2025), arXiv 2408.00661 | SNIPPET |
| Drawn (time-multiplexed) trap | AOM drawing at 5 kHz, 1 W instantaneous, ≈ 10 mW average per point, NA 0.2 (simulation parameters) | "boat" trap, Au spheres of radius ≥ 1 µm held > 1 h | Mirzaei-Ghormish, Griffith, Smalley, Camacho, *PR Applied* 22, 064042 (2024) | SNIPPET |
| Independent multi-particle optical-trap display | none found (2018–Sep 2026) | – | R5 plus this search | SNIPPET |

---

## 1. Mechanism of single-beam 3D photophoretic trapping in air

### 1.1 What the literature says

- **Lateral confinement is well understood.** An absorbing particle is pushed from hot to cold, so it sits in dark regions
  enclosed by light. Examples:
  - the dark core of a vortex (Shvedov 2009, 2010);
  - a bottle made by spherical aberration (Shvedov et al., *Opt. Express* 19, 17350, 2011);
  - the dark cone above an axicon-ring focus (Redding & Pan, *Opt. Lett.* 40, 2798, 2015);
  - holographic bottles (Alpmann et al., *APL* 100, 111101, 2012);
  - BYU's aberration pockets.

  [SNIPPET for all.]
- **Axial balance differs by group and geometry:**
  - **Gravity (vertical beam, "levitation").** The Banerjee (IISER Kolkata), Li (ECU) and Pan/Wang/Videen single-Gaussian traps
    work this way. Clusters sit "slightly above the focal plane" and move toward the focus as power drops (Pahi, Paul,
    Banerjee, *New J. Phys.*, 2024). Sil et al. (*APL* 117, 221106, 2020): PP forces "confine particles by a combination of
    levitation and active trapping"; the transverse PP component produces a torque, which causes rotation that generates a
    restoring force [SNIPPET]. BYU's patent text says the same for vertical configurations: axial confinement balances the
    longitudinal PP force against gravity, "described as optical levitation" [SNIPPET].
  - **Δα (accommodation) force and morphology.** Zhang et al. (Chen group, *Opt. Express* 20, 16212, 2012) is described as
    3D trapping of **non-spherical** particles in one focused Gaussian beam via the Δα force [SNIPPET, attribution Med].
    The Pahi/Banerjee review (arXiv 2512.09401; *ChemPhysChem* 2026) states that **regular (symmetric) particles cannot be
    stably trapped with a horizontal beam**: the Δα force vanishes, and the ΔT force and gravity are orthogonal
    [SNIPPET; I attribute the sentence to this review, Med].
  - **Negative photophoresis.** Li's group pulls irregular absorbing particles toward the source (APL 2015). In their
    power-modulation study (PR Applied 2018), removing the beam lets the lingering PP force pull the particle up toward the
    source, and a power spike pushes it away by radiation pressure. So the axial equilibrium was negative PP against
    gravity plus radiation pressure [SNIPPET]. Wang et al. (APL 2016): push or pull is "dominated by the particle's
    orientation and morphology" [SNIPPET].
  - **Counter-propagating light.** Examples:
    - dual vortices (Shvedov 2009);
    - Pan's UOT, where one hollow beam folded by two parabolic reflectors forms counter-propagating cones
      (*Opt. Express* 27, 33061, 2019);
    - the Gong/Pan/Wang confocal scheme that "converts one trapping beam to two counter-propagating beams"
      (*RSI* 87, 103104, 2016);
    - Zhu et al.'s two counter-propagating hollow beams (*APL* 125, 091105, 2024);
    - the Cal Poly retro-reflector, which gave ≈ 3× longer average trapping time (*Proc. SPIE* 13388, 2025).

    [SNIPPET for all.]
  - **BYU aberration traps (display).** Particles prefer dark rings of the spherical-aberration diffraction pattern (Ware
    2021) [SNIPPET]. There is no gravity dependence between 0 g and 2 g (Peatross 2018) [SNIPPET]. The upstream restoring force
    is "an open question" (Ware 2021) [SNIPPET]. In 2017 BYU wrote that in aberration and vortex traps "particles are free to
    move up and downstream along the beam". That is why they built the Poisson-spot trap, which encloses the particle in a
    dark oval (JUR 2017) [SNIPPET].
  - **Rotation.** Trapped irregular particles spin or orbit at 0.2–20 kHz. Centripetal accelerations reach ≈ 20 g (Lin & Li,
    *APL* 104, 101909, 2014). The rotation is coupled to axial oscillation (Pahi 2024) [SNIPPET]. Rotation is how asymmetric
    body forces get averaged or rectified. It is a feature of the trap, not a design lever that anyone has quantified.

### 1.2 Accepted picture (synthesis)

For absorbing particles in a single beam, the accepted picture is this. Lateral confinement comes from the dark region
enclosed by light. **Axial** confinement needs something other than the forward ΔT push. In practice that is:
- gravity (most aerosol-science traps);
- particle asymmetry (the Δα force, negative PP, rotation); in BYU traps with irregular black-liquor or char particles this is
  presumably what acts, but it is unexplained;
- a second, backward-going beam or reflection.

No paper found derives or measures a strong upstream restoring force for a symmetric opaque particle in forward-only light.
Radiation pressure is 10²–10⁴× weaker (R5) and also points downstream.

### 1.3 Bound on the upstream force for an opaque body [ESTIMATE]

- **Sphere.** In the continuum ΔT model the force points from the heated region toward the cold side. For an opaque sphere,
  each ray heats the face it strikes, so each contribution to F is parallel to its own ray k. If all rays have k_z > 0 (one
  head), then F_z > 0.
- **Arbitrary opaque shape** (flat, tilted "sail" motes):
  - A lit facet has outward normal n with n·k < 0, and the force from its heat is along −n.
  - An upstream component (F_z < 0) needs n_z > 0.
  - Combined with n·k < 0, this gives n_z < tan θ·|n_⊥|, where θ is the ray angle to the axis.
  - So F_up/|F| ≤ tan θ_max ≈ NA, which is **≤ 0.05–0.1 at NA 0.05–0.1**, even with perfect orientation.
- **Escapes from the bound:**
  - the Δα force, which is body-fixed and depends on the accommodation pattern, not on which face is lit;
  - rear-side heating in transparent or lensing particles (J₁ > 0, negative PP);
  - any backward-propagating light.

  These are exactly the mechanisms the literature invokes.

---

## 2. Measured stiffness, maximum force, speed and heating

**Stiffness.**
- **Pahi et al. (2025)** [SNIPPET]:
  - 4.15–6.14 pN/µm transverse, from Brownian PSD;
  - carbon microclusters, 640 nm, loosely focused through a 25 mm lens;
  - particles trapped at 70 mW, measured at ≈ 20 mW;
  - quoted masses 19 / 30 / 67 "pico-kg" (units ambiguous).
- **Sil et al. (APL 2020):** stiffness versus power and particle size from wideband excitation [SNIPPET]. No numbers were
  recovered.
- **Lin et al. (JOSA B 2017):** stiffness is linear in intensity [SNIPPET].
- **Zhu et al. (APL 2024):** stiffness from a release-and-recapture flight between two counter-propagating hollow-beam traps
  [SNIPPET]. No values were recovered.
- **Hadad 2018:** "≈ 50 pN/m" for the Archimedes screw [SNIPPET; units suspicious].
- **Fibre tweezers (R5):** 1.39 / 2.49 pN maximum restoring force; axial transport at 5 mm/s without loss [SNIPPET].

**Maximum force and escape speed.**
- No published curve of maximum transverse speed versus power was found for any photophoretic trap.
- Displays:
  - BYU > 1.83 m/s, > 5 g (2018);
  - Poisson trap 1.5 m/s, > 3 g (2017);
  - 2 m/s air speed (SPIE 2018).

  The power at which these were reached is not in any snippet; the display power was 80 mW at 405 nm (AO 2019)
  [SNIPPET].
- Airflow guidance from the BYU rig papers: airflow in PP systems "typically < 1 m/s, may be < 1 cm/s"; lower airflow lowers
  the power needed [SNIPPET].
- Other speeds:
  - Carmon/Roichman orbital trap: 0.06–5.5 cm/s, 10 g (*Sci. Adv.* 2025) [SNIPPET];
  - negative-PP pipeline: 1–10 cm/s;
  - vortex guide: 1 cm/s at a few mW;
  - conveyor: ≤ 0.3 mm/s.
- [ESTIMATE] Typical scale: stiffness × trap half-width gives about 5 pN/µm × 10 µm ≈ 50 pN at ≈ 20 mW. That is **30–70× below**
  the 1.7–3.8 nN drag BYU's particle must have felt at 1.83 m/s. So lab "stiffness" traps and the BYU display trap work in
  very different force regimes. The difference comes from power, particle temperature and trap geometry. The stiffness data
  cannot be used to calibrate η.

**Heating.**
- Ai et al. (2023): **322–830 K** particle surface temperature over 200–2950 mW (18.3 K per 100 mW) at the UOT centre; the
  hollow-beam walls are hotter [SNIPPET].
- Carbon nanofoam traps at powers as low as 0.3 mW [SNIPPET].
- BYU: more power helps "until … too destructive for the particle reservoir" (RSI 2021) [SNIPPET]. No BYU particle
  temperature was found.
- [ESTIMATE] BYU at 1.83 m/s implies ΔT ≈ 300–500 K, i.e. P_abs ≈ 0.25–0.8 mW for a = 2.5–5 µm.

**Force latency.**
- Chen et al. (2018): PP force time constant up to ≈ 1 s for their particles [SNIPPET].
- [ESTIMATE] For 3–10 µm low-k motes, τ ≈ 0.03–2 ms (external), up to ≈ 7 ms internal at k_p = 0.02. This is one to two orders
  of magnitude longer than a 20 kHz loop period of 50 µs. The force-lag model (M2b) must use these values.

---

## 3. Tractor beams and bidirectional axial control in air

| Design | Push/pull control | Demonstrated performance | Source | Tag |
|---|---|---|---|---|
| Semitransparent thin shell (≈ 300 nm glass + 7–15 nm Au, ≈ 200 µm) | polarization of a TEM01* doughnut: radial ↔ azimuthal moves the hot spot between front and back | pull at 0.8 mm/s with 200 mW; range up to 20 cm; stop or reverse on demand | Shvedov et al., *Nat. Photon.* 8, 846 (2014) | SNIPPET |
| Irregular absorbing particles (smut spores, C) | fixed by morphology; speed set by intensity | pull at 1–10 cm/s over about 1 m, collimated beam; ≈ 20 µm placement | Lin, Hart, Li, *APL* 106, 171906 (2015) | SNIPPET |
| CNT particles of 10–50 µm | set by orientation and morphology (not controllable) | push or pull after release from a trap | Wang et al., *APL* 109, 011905 (2016) | SNIPPET |
| Au microplate on a tapered fibre | PP pull near the tip versus radiation push away from it (supercontinuum) | oscillation on the fibre; not free-floating | Lu et al., *PRL* 118, 043601 (2017) | SNIPPET |
| Transparent sphere with rear focusing (Mie "lens"), J₁ > 0 | size parameter and absorption (orientation-independent) | classical negative photophoresis; no fast free-space trap found | Horvath, *KONA* 31 (2014) review; Tehranian & Greene-type Mie models | SNIPPET/MEMORY |
| Non-thermal optical pulling (for scale) | beam shaping or material | ≈ 14 cm range estimate at ≈ 1 W (theory); nanofibre pulls a droplet 40 cm at µm/s | Li, Chen, Lin, Ng, *Sci. Adv.* (2019); *Nat. Commun.* 16, 7424 (2025) | SNIPPET |

**Force per watt, pull versus push.**
- No paper found normalises pull force to push force for the same particle and power. This is a **gap**.
- [ESTIMATE] For Shvedov's shell, if drag-limited and horizontal: F ≈ 6πμav ≈ 27 pN at 200 mW, about 0.1 pN/mW. That is
  roughly 10⁻³–10⁻² of the ideal PP force for the heat it probably absorbed.
- [ESTIMATE] For a designed lensing mote (high-index transparent core, rear hot spot), geometry caps the pull at ≈ 0.25 of the
  ideal force per unit heat. A glass-like core conducts heat at k ≈ 1 W/m/K, which costs another ≈ 5–15× against an aerogel
  composite (the (k_p + 2k_g) factor). So **η_pull ≈ 0.02–0.1** relative to the opaque low-k push mote.
- [ESTIMATE] Two-wavelength Janus or shell designs could switch push/pull from one head: coating absorbing at λ₁ (push) and a
  rear absorber reached by lensing at λ₂ (pull). Nothing like this has been demonstrated in air.

---

## 4. Long working distance (> 0.5 m)

- **Shvedov et al., PRL 2010:** ≈ 100 µm carbon-coated hollow glass or C agglomerates guided along a ≈ 1.5 m vortex "pipeline",
  with ±10 µm positioning. Speed "several mm/s", depending on particle structure and mass. Remote deposition at 0.5 m with
  10 µm accuracy; aimed by a movable mirror at targets about 1 m away. Power not recovered; the related HGMS work used 532 nm
  at 50 mW–2 W [SNIPPET].
- **Lin, Hart & Li, APL 2015:** meter-scale **pulling** in a collimated beam at 1–10 cm/s [SNIPPET].
- **Shvedov 2014:** tractor beam over 20 cm [SNIPPET].
- **Nanofibre pulling (*Nat. Commun.* 2025):** 40 cm, but guided along a fibre at µm/s [SNIPPET].
- **2020–2026:** no free-space photophoretic *trap* (3D confinement at a focus) with working distance > 0.2 m was found.
  Display traps work at f ≈ 25–200 mm. Two groups report a **maximum focal length**:
  - Banerjee: none trapped at 150–200 mm with a fibre-fed beam;
  - Cal Poly: 80–160 mm is optimal at 405 nm.

  [SNIPPET for both.] [ESTIMATE] Both used a fixed input beam, so the real limit is a **minimum NA** (roughly 0.01–0.02 for
  mm-scale beams), not a distance. A 1.5 m trap at NA 0.05–0.1 (150–300 mm aperture) is not excluded by these results, but
  it is untested.

---

## 5. Multi-particle position sensing at high rate

- **In air, the physics is proven.** Balanced BFP detection reached < 3 fm/√Hz with > 50 MHz bandwidth on a 1 µm bead in air
  (Raizen 2010), at short range and high NA [SNIPPET]. A photophoretic trap has been stabilised by laser-power feedback from a
  position-sensitive detector, using (A−B)/(A+B) edge-mirror detection [SNIPPET; attribution uncertain, probably Pan/Wang or
  Chen group].
- **Event cameras:**
  - µs timestamps, but pixel latency < 100 µs (bright) to < 1 ms (dim) (IMX636), 1 Gev/s peak [SNIPPET];
  - neuromorphic feedback cooled 3 particles at once and detected tens; latency sub-ms (Ren et al., *Nat. Commun.* 2025)
    [SNIPPET];
  - an optical-modulation trick gives up to 400× temporal resolution (*Sci. Rep.* 15, 35299, 2025) [SNIPPET];
  - 30 kHz DVS tracking claimed in early work (Ni et al., *J. Microsc.* 2012) [SNIPPET].

  **Latency of 0.1–1 ms is too long for the 15–30 kHz loop the push trap needs**, where total latency must be ≲ 10–20 µs.
  Commercial event sensors are silicon, so they are blind at 1550 nm. They could only see the visible phosphor emission,
  which is ≈ nW per mote: ≈ 350 photons per 50 µs sample, giving σ ≈ 0.5 µm [ESTIMATE]. That is marginal.
- **Photon budget at 1.5 m** [ESTIMATE]:
  - assumptions: 5 % diffuse backscatter of the trap light, 0.1–0.5 mW absorbed per mote, collection aperture 0.1–0.3 m;
  - collected power: 6–250 nW at 1550 nm;
  - photons per sample: 4×10⁵–10⁸ at 10–50 kHz;
  - shot-noise σ = 1–15 nm, against a 0.5 µm requirement.

  **Precision is not the limit.** The limits are:
  - latency;
  - separating thousands of motes;
  - glints of the trap wavelength from the optics;
  - z sensing: stereo baseline, or astigmatic focus error with capture range ±λ/NA² ≈ ±0.15–0.6 mm.

  The natural single-head scheme is **descanned per-channel quadrant (or astigmatic) detection**: each steering channel
  collects its own mote's backscatter back through its own scanner, as in a laser tracker or CD pickup. This scales one
  detector per channel. No example in a trap display was found.

---

## 6. Multi-particle trap displays and holographic photophoretic traps (2020–2026)

- **No independent control of more than one particle in a display has been published** (through Sep 2026).
  - BYU's diffractive scaling (binary grating, Fresnel lens) reports trap rate only (N = 50) for multiple simultaneous traps
    (Bond et al., SPIE 12445, 2023) [SNIPPET].
  - Rogers (thesis 2020; AO 2019): "multiple suspended particles in a linear array from a single laser source" [SNIPPET].
  - BYU names SLMs and AOD/EOD as next steps; the Pahi 2026 review lists the same [SNIPPET].
- **SLM photophoretic traps in air (not displays):**
  - Alpmann et al. (APL 2012): holographic bottle beams hold several particles at defined positions and move them on
    arbitrary paths;
  - Porfirev (Opt. Eng. 59, 055109, 2020): SLM confinement, 2D/3D guiding, revolution, transfer between traps;
  - Porfirev et al. (*Phys. Wave Phenom.* 32, 83, 2024): polygon beams make arrays of bottle traps; hundreds to thousands
    of C agglomerates trapped and guided along curved paths;
  - "optical mill" (APL 115, 201103, 2019): hundreds to thousands of particles transferred between cuvettes.

  [SNIPPET for all.]
  **Update rates:** LCOS SLMs run at ≈ 60–120 Hz frames [MEMORY]. No SLM-based photophoretic work reports faster
  updates. That is far too slow for POV strokes; SLMs suit static trap arrays, not scanning.
- **Time-multiplexed drawn traps** (BYU boat trap): an AOM draws the trap walls at ≈ 5 kHz. The particle sees ≈ 10 mW
  averaged from 1 W instantaneous. The drawing frequency must be fast relative to particle dynamics but slow enough not to
  distort the trap [SNIPPET]. This is the closest demonstrated precedent for one head drawing many trap walls with an AOD.

---

## 7. η estimates

**7.1 What BYU's speed implies** [ESTIMATE]. Inputs:
- continuum ΔT force per kelvin of mean heating: F/ΔT = C·18πμ²J₁′k_g/(ρT₀(k_p + 2k_g)), with J₁′ = 0.5, C = 1–1.56;
- this gives 6.7 / 4.5 / 1.9 pN/K at k_p = 0.05 / 0.1 / 0.3;
- Oseen drag at 1.83 m/s: 1.74 nN (a = 2.5 µm, Re 0.6), 2.95 nN (4 µm), 3.83 nN (5 µm, Re 1.2).

| a | k_p | ΔT = 300 K (C = 1 / 1.56) | ΔT = 500 K (C = 1 / 1.56) |
|---|---|---|---|
| 2.5 µm | 0.05 | 0.86 / 0.55 | 0.52 / **0.33** |
| 2.5 µm | 0.1 | 1.29 / 0.82 | 0.77 / 0.49 |
| 4 µm | 0.05 | 1.47 / 0.94 | 0.88 / 0.56 |
| 5 µm | 0.1 | 2.83 / 1.82 | 1.70 / 1.09 |

(The entries are the η required.)
- The data are consistent only with a small (a ≲ 3–4 µm), low-k, hot (ΔT ≈ 400–500 K) particle with **η_transverse ≈ 0.35–0.9**.
  The Δα force on irregular char may add force the ΔT model omits, which would lower the η needed.
- **Best estimate: η_BYU,transverse ≈ 0.5 (range 0.3–0.9).**
- This agrees with a geometric check. Take a particle pressed against a sharp bright/dark edge (a half-lit sphere). Its heat
  dipole per unit heat is 4a/(3π) laterally, against 2a/3 axially for uniform light, so F_x/F_z = 2/π. **The lateral η per
  unit heat is therefore at most ≈ 0.64**, reached when the wall is sharper than the particle. For BYU,
  λ/(2NA) ≈ 3.4–10 µm at 405 nm with NA ≈ 0.02–0.06 [ESTIMATE of NA], which is comparable to the particle diameter, so this
  bound is nearly reachable.
- **Axial:** η_downstream ≈ 1 (the beam push). η_upstream is unmeasured. It is bounded below by the 2 g result (≳ 0.005) and
  bounded above by §1.3 (≲ NA) unless the Δα force or negative PP acts.

**7.2 Scaling to 1550 nm, 1.5 m, NA 0.05–0.1, a = 3–10 µm** [ESTIMATE].
- At fixed NA, and with aberrations specified in waves, the trap pattern is the same in units of λ/NA (transverse) and λ/NA²
  (axial). Distance enters only through the aperture: 150–300 mm at 1.5 m.
- The relevant variable is a·NA/λ, particle size against feature size:
  - BYU: ≈ 0.12–0.75, for a = 2.5–5 µm and NA 0.02–0.06;
  - ours at NA 0.1: 0.19 (a = 3 µm) to 0.65 (a = 10 µm);
  - ours at NA 0.05: 0.10–0.32.
- Transverse η is linear in a·NA/λ below saturation and caps near 0.64.
- Resulting transverse η:

| Case | η_transverse |
|---|---|
| NA 0.1, a = 5–10 µm | 0.3–0.6 (BYU-like) |
| NA 0.1, a = 3 µm | 0.15–0.35 |
| NA 0.05, a = 10 µm | 0.2–0.5 |
| NA 0.05, a = 3 µm | 0.07–0.2 |

- **Upstream: ≈ 0 for an opaque low-k mote; bound ≤ NA = 0.05–0.1.** Gravity gives at most the settling speed of
  0.3–18 mm/s, and only if the head is below the volume.
- **Adverse factors:**
  - BYU and Cal Poly report that shorter wavelength traps better [SNIPPET];
  - larger features in µm mean larger trap excursions (tens of µm, still sub-voxel);
  - trapping at NA 0.05–0.1 with a 150–300 mm aperture has never been tried.
- **η_single (worst direction) ≈ 0 to 0.05** without an engineered pull mechanism. With a lensing or two-wavelength pull mote,
  the rough range is ≈ 0.02–0.1 (§3). Both are far below the "≳ 0.4 in every direction" a single-head architecture needs.

**7.3 Design implications** (for the model, not demonstrated):
1. Keep the multi-head push trap as the baseline. A **"hybrid 2-head"** is worth modelling:
   - one head gives single-beam transverse trapping at η ≈ 0.3–0.6;
   - an opposing second head (or a passive back-reflector behind the volume, cf. the Cal Poly retro-reflector and the Pan
     confocal fold) supplies the upstream force.
2. If only one head is used, route strokes so that the along-beam component is small and mostly downstream. Budget
   upstream speed at settling speed (mm/s), or cm/s with an engineered pull mote.
3. A bench test at NA ≈ 0.05–0.1 is decisive. The measurement is the transverse escape speed versus P_abs and particle ΔT,
   and separately the **upstream** escape speed, at 1550 nm with a 150–300 mm aperture.

---

## Gaps (could not verify)

- Nature 2018 Methods: the trap power at which 1.83 m/s was reached, beam diameter and NA, particle size distribution, and
  **whether any fast axial motion was tested**. The z-stage inference comes from Chae 2020 [SNIPPET], not from BYU directly.
- Ware et al. 2021 and A. Peatross's 2023 senior thesis ("Stability of photophoretic trapping…"): any quantitative axial force.
  Also Kunzler's 2026 senior thesis (imaging particles against beam structure).
- Pahi et al. 2026 review (arXiv 2512.09401): full mechanism discussion. The "symmetric particles cannot be trapped
  horizontally" sentence is attributed to it from a snippet.
- Stiffness values in Zhu et al., APL 125, 091105 (2024) and Sil et al., APL 117, 221106 (2020). No measured maximum
  transverse force or escape velocity versus power exists for any PP trap in snippets.
- Laser power and wavelength in Lin/Hart/Li 2015 (pulling). Power and speed per particle in Shvedov PRL 2010. Push speed
  versus pull speed in Shvedov 2014. **No push-versus-pull force-per-watt comparison exists** in what I could see.
- The actual maximum focal-length numbers and beam diameters in Cal Poly DH 2022 and SPIE 12443.
- Any 2024–2026 BYU paper with more than one independently controlled particle. SPIE PW 2026 contents were not visible.
- Whether any SWIR (InGaAs) event sensor exists commercially; I believe none, [MEMORY].
- The attribution of the PSD-plus-locking-circuit feedback stabilisation of a PP trap.
- The Hadad 2018 stiffness units, and the μN-scale PP force claimed in a Desyatnikov-2009 snippet, which I judge implausible.

## Sources (all accessed as search snippets on 2026-09-30)

- Ware et al., SPIE 11798 (2021): https://www.spiedigitallibrary.org/conference-proceedings-of-spie/11798/2596791/
- Peatross et al., SPIE 10723 (2018): https://www.semanticscholar.org/paper/89a518e7291b9e13e95467803fecb19ca9a1bfe8
- Goodsell & Smalley, BYU JUR (2017): http://jur.byu.edu/?p=22268
- Chae et al., OSA 2020 JTh2A.34: https://opg.optica.org/abstract.cfm?uri=AOMS-2020-JTh2A.34
- Rogers et al., AO 58, G363 (2019): https://par.nsf.gov/servlets/purl/10141807 ; Rogers thesis: https://scholarsarchive.byu.edu/etd/8686/
- Barton et al., RSI 92, 103002 (2021): https://pubs.aip.org/aip/rsi/article/92/10/103002/955132/
- Pahi et al., J. Phys. Photonics (2025): https://iopscience.iop.org/article/10.1088/2515-7647/adec2a ; arXiv 2503.16059
- Pahi, Paul, Banerjee, NJP (2024): https://arxiv.org/abs/2407.00669
- Pahi, Sahoo, Sil, Banerjee, review (2026): https://arxiv.org/abs/2512.09401 ; https://pubmed.ncbi.nlm.nih.gov/42060828/
- Sil et al., APL 117, 221106 (2020): https://pubs.aip.org/aip/apl/article-abstract/117/22/221106/39176/
- Sil et al., ACS Photonics 11 (2024), multimode fibre: https://arxiv.org/abs/2301.04089
- Banerjee group, fibre plus lenses, J. Opt. 24, 074003 (2022): https://arxiv.org/pdf/2201.06526
- Bera et al., OL 41, 4356 (2016): https://opg.optica.org/ol/abstract.cfm?uri=ol-41-18-4356
- Lin et al., JOSA B 34, 1242 (2017): https://opg.optica.org/josab/abstract.cfm?uri=josab-34-6-1242
- Lin & Li, APL 104, 101909 (2014): https://pubs.aip.org/aip/apl/article-abstract/104/10/101909/130546/
- Lin, Hart, Li, APL 106, 171906 (2015): https://pubs.aip.org/aip/apl/article/106/17/171906/28335/
- Chen et al., PR Applied 10, 054027 (2018): https://arxiv.org/abs/1902.11177
- Wang, Gong, Pan, Videen, APL 109, 011905 (2016): https://pubs.aip.org/aip/apl/article/109/1/011905/31179/
- Redding & Pan, OL 40, 2798 (2015): https://opg.optica.org/ol/fulltext.cfm?uri=ol-40-12-2798&id=320178
- Gong, Pan, Wang, RSI 87, 103104 (2016): https://pubs.aip.org/aip/rsi/article/87/10/103104/368053/
- Gong, Pan, Videen, Wang, JQSRT 214, 94 (2018): https://ui.adsabs.harvard.edu/abs/2018JQSRT.214...94G/abstract
- Ai, Pan, Videen, Wang, Appl. Spectrosc. (2023): https://doi.org/10.1177/00037028231198878
- Zhang et al., OE 20, 16212 (2012): search result summary only
- Shvedov et al., OE 19, 17350 (2011): https://pubmed.ncbi.nlm.nih.gov/21935099
- Shvedov et al., Appl. Phys. A 100, 327 (2010): https://link.springer.com/article/10.1007/s00339-010-5860-4
- Shvedov et al., PRL 105, 118103 (2010): https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.105.118103 ; https://phys.org/news/2010-09-scientists-meter-scale-distances-video.html
- Shvedov et al., Nat. Photon. 8, 846 (2014): https://www.nature.com/articles/nphoton.2014.242 ; https://www.sci.news/physics/science-long-distance-optical-tractor-beam-02221.html
- Lu et al., PRL 118, 043601 (2017): https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.118.043601
- Li, Chen, Lin, Ng, Sci. Adv. (2019): https://www.science.org/doi/10.1126/sciadv.aau7814
- Nanofibre pulling, Nat. Commun. 16, 7424 (2025): https://www.nature.com/articles/s41467-025-62536-w
- Hadad et al., Optica 5, 551 (2018): https://arxiv.org/abs/1706.10122
- Droby et al., Sci. Adv. 11 (2025): https://www.science.org/doi/10.1126/sciadv.adx1485
- Zhu et al., APL 125, 091105 (2024): https://pubs.aip.org/aip/apl/article/125/9/091105/3310190/
- Garcia et al., SPIE 13388 (2025): https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13388/133880E/
- Ababseh, Childers, Jin, SPIE 12443 (2023): https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12443/124430D/ ; DH 2022: https://opg.optica.org/abstract.cfm?uri=DH-2022-Th4A.5
- Mirzaei-Ghormish et al., PR Applied 22, 064042 (2024): https://arxiv.org/html/2310.04860
- Bond et al., SPIE 12445 (2023): https://ui.adsabs.harvard.edu/abs/2023SPIE12445E..0IB/abstract
- Alpmann et al., APL 100, 111101 (2012): https://archive.org/details/arxiv-1112.5270
- Porfirev, Opt. Eng. 59, 055109 (2020): https://www.spiedigitallibrary.org/journals/optical-engineering/volume-59/issue-5/055109/
- Porfirev et al., Phys. Wave Phenom. 32, 83 (2024): https://link.springer.com/article/10.3103/S1541308X24700031
- "Optical mill", APL 115, 201103 (2019): https://pubs.aip.org/aip/apl/article/115/20/201103/37425/
- Li, Kheifets, Medellin, Raizen, Science 328, 1673 (2010): https://users.physics.ox.ac.uk/~Foot/Phynance/Raizen1BrownianM.pdf
- Ren et al., Nat. Commun. (2025): https://www.nature.com/articles/s41467-025-65677-0 ; APL 121, 113506 (2022): https://arxiv.org/abs/2206.11220
- Neuromorphic modulation, Sci. Rep. 15, 35299 (2025): https://www.nature.com/articles/s41598-025-19215-z
- IMX636 brief: https://www.prophesee.ai/wp-content/uploads/2024/05/IMX636-Product-Brief-2024-v3.0.pdf
- Ni et al., J. Microsc. 245, 236 (2012): https://www.researchgate.net/publication/51800897

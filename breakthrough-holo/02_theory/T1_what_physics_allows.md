# T1: What physics allows

**Question:** What must be physically true of any device that shows an image floating in open air, visible from all around, with no screen, fog or glasses, and that renders correctly around a hand touching it?

**Answer (proved below):** light must be *created at the image points themselves, inside the air*. In clean air, only one mechanism does this strongly enough: **laser-induced ionisation (plasma)**. Everything else either does not localise, is too weak by many orders of magnitude, or cannot send light sideways toward viewers.

This is not a counsel of despair. It tells us exactly which road to engineer, and which trade-offs (brightness vs air chemistry vs noise vs laser safety) the simulations must quantify.

---

## 1. Setting

- The image volume Ω is ordinary room air: homogeneous, linear to first order, ~2.5×10²⁵ molecules/m³.
- Viewers' eyes are at positions E outside, or even partly inside, Ω.
- Opaque objects: walls, floor, furniture, people and hands.
- The device is a "projector": it can send any electromagnetic or acoustic field into Ω from an exit aperture A of finite size.

---

## 2. Theorem 1: line of sight (the "display frustum")

**Statement.** Take an eye at E and a desired image point P. Let B be the first opaque surface hit by the ray that starts at E, passes through P and continues beyond P. If the medium on the segment E→B neither emits nor scatters light, the light E receives from the direction of P is exactly the light leaving B toward E. Nothing placed "at P" by any external beam can change it.

**Proof sketch.**
- Geometrical optics: in a source-free, non-scattering, homogeneous medium the radiative transfer equation reduces to dL/ds = 0. Radiance is constant along straight rays (the brightness theorem, conservation of étendue).
- Wave optics: the field in a source-free homogeneous region obeys the Helmholtz equation. Its local angular content (the Wigner distribution / generalised radiance) is transported along straight lines. The field in Ω is fully determined by its sources on the boundary ∂Ω (Kirchhoff–Helmholtz).
- Either way, the radiance the eye receives along direction −û, where û = (P−E)/|P−E|, is set by the boundary point B = E + t·û. Light crossing P in any *other* direction never enters the eye. ∎

**Corollary 1.1: a projector sees only its own frustum.** A projector with exit aperture A can make P visible to E only if the line E→P, extended, hits A.

- Example: a 0.3 m ceiling aperture 2 m from P covers Ω_A = 0.071 m² / (2 m)² ≈ 0.018 sr, which is **0.14 % of 4π**.
- The Iron Man requirement is ~4π, so a projector that only sends light *through* the image region can serve at most 0.14 % of viewing directions. That is why every aerial-imaging, light-field and holographic display needs its screen/plate/aperture *behind* the image.
- R1 + R5 (floating, visible from all around) are therefore impossible with "light passing through" designs. This is the physics behind the owner's "not a holo table, not a holo wall".

**Corollary 1.2: only two escapes exist.**
- **(a)** Surround the viewer with emitting boundaries: all walls, floor and ceiling become directional light-field emitters (a "holodeck room"). This violates R3/R4 (screens, room infrastructure) and fails the touch lemma below.
- **(b)** Make the medium at P emit or scatter, i.e. create light *at P*. This is the only escape compatible with R1–R4.

---

## 3. Lemma 2: touch and occlusion

Consider any display in which P is produced by an emitter at a surface S behind P (escape (a), or any screen, plate or wall). A hand H that lies between P and S on the line of sight blocks the ray E→P→S. The viewer then sees the *hand* where the hologram should be in front of it.

In the Iron Man scenes, hands are inside the hologram. From almost every viewpoint, part of the hologram lies in front of the hand, so this failure is unavoidable for surface-emitter displays.

Painting the hologram onto a glove (projection mapping) fixes it for **one** viewer only. A diffuse glove point G is seen by viewer E₁ through hologram point P₁ and by viewer E₂ through a different point P₂, and must show two different colours at once.

**Therefore:** R2 (no eyewear) + R5 (many viewers, all around) + R7 (touch with correct appearance) ⇒ **in-volume emission**. This is independent of Theorem 1 and reaches the same conclusion.

---

## 4. Theorem 2: in clean air, only plasma is strong enough

We need a process that turns energy delivered by the projector into light **(i)** localised at P, **(ii)** radiated toward all viewers (incoherent, near-isotropic) and **(iii)** bright enough to see. All numbers are checked in `03_simulations/sim_e1_clean_air_bounds.py`.

| Candidate mechanism | Localised at P? | Radiates sideways? | Strength | Verdict |
|---|---|---|---|---|
| Rayleigh / Raman / Brillouin scattering by air molecules | **No**: linear in intensity, so the whole beam glows uniformly until it hits a wall (a "light-sabre line", never a bounded shape) | Yes | β ≈ 1.3×10⁻⁵ m⁻¹ at 532 nm; ~10² W per mm³ voxel for 100 cd/m² | Dead for 3D images |
| Coherent nonlinear optics (third-harmonic generation, four-wave mixing, stimulated Raman) | Yes, at the focus | **No**: phase matching sends light forward; side emission from a focus smoother than λ is exponentially suppressed | n₂ ≈ 3×10⁻²³ m²/W | Dead |
| Incoherent nonlinear scattering (hyper-Rayleigh/Raman) | Yes | Yes | ≈ (n₂I/(n−1))² ≈ 3×10⁻³ of Rayleigh even at the ionisation limit; ~10⁴–10⁵ photons per pulse | Dead (far too weak) |
| Multiphoton excitation of N₂/O₂ *without* ionisation | Yes | Yes | O₂ dissociates (no visible fluorescence); N₂ emitting states need ≥ 11 eV, which is the plasma regime anyway | Merges into plasma |
| **Laser-induced ionisation (air plasma)** | **Yes**: a sharp intensity threshold makes it a true voxel | **Yes**: spontaneous emission is isotropic | ~10⁸–10¹¹ photons per voxel (to be quantified in E4) | **Only survivor** |
| Microwave / THz breakdown | Yes, but voxels are ≥ mm (diffraction) | Yes | Breakdown field ~3 MV/m → ~10 mJ per voxel; room RF exposure far above limits | Dead (safety, resolution) |
| Sound (acousto-optics) | Yes | **No**: large-angle Bragg scattering needs acoustic wavelengths ~λ_light, i.e. f ≳ 100 MHz, absorbed within micrometres in air | Deflection ≲ 1 mrad at 0.5 MHz | Dead as a light source; usable only as a small-angle in-air optic |
| Thermal lensing (laser-heated air channels) | Yes | No (small angles only) | Δn ~ 10⁻⁵ | Dead |
| Electrical discharge | Needs electrodes in the volume | — | — | Violates R1/R3 |
| Direct neural or retinal stimulation | — | — | Retinal position follows ray direction (Theorem 1 again); cortical stimulation is not image-registered and not safe for everyday use | Dead |
| Matter supplied by the projector (levitated particles, acoustic or optical traps) | Yes | Yes, efficient scattering, **full colour** | Very bright per watt | Allowed only in the R3 grey zone (projector-supplied, recovered particles) |

**Theorem 2 (informal, by exhaustion plus numbers).** For a device consisting only of a projector and ambient air, the only mechanism that produces localised, isotropic, visible emission at a strength of practical interest is **laser-induced air plasma**.

The optional, grey-zone alternative is **projector-supplied scattering particles** held and moved by acoustic or optical fields.

---

## 5. What this means for the design (the research programme)

1. **The core engine is a laser-induced air-plasma voxel engine.** This is the physics of Aerial Burton (2006) and *Fairy Lights in Femtoseconds* (2016), so the road is real but unfinished. The research question becomes quantitative:
   > How bright, how big, how dense, how colourful and how *safe* can an air-plasma volumetric display be made?
2. **The governing trade-offs** (explored in simulations E3–E7, E10):
   - **Brightness ↔ air chemistry.** Every ionisation in air eventually makes O₃ and/or NO/NO₂. Indoor limits cap total brightness, so photons per reactive molecule is the key figure of merit.
   - **Brightness ↔ noise.** Every plasma voxel is a tiny blast wave. A high repetition rate pushes the energy into inaudible ultrasound, which air absorbs.
   - **Laser safety.** The unconverted beam continues past the focus. Eye-safe wavelengths (≥ 1.4 µm) raise the eye's permissible exposure by ~10⁴–10⁶ over 1 µm.
   - **Addressability.** A hand can block the beam path from the projector. Several apertures and occlusion-aware scheduling are needed.
   - **Colour.** Air plasma emits violet-blue molecular bands (cold plasma) through to white continuum (hot plasma). There is no independent RGB. Colour is the hardest requirement (R9), and grey-zone hybrids may be the only route to the orange accents.
3. **Touch:** a glove (allowed by the owner) with vibrotactile feedback plus camera hand tracking, optionally ultrasound mid-air haptics or plasma-shock haptics. The rendering kernel must re-route voxels whose beams would cross a hand.

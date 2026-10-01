# D1 independent check: red team of `sim_d1_lens_trap.py` (claims A to D)

**Date:** 2026-10-01.
**Script:** `08_bench/d1b_independent_check.py`. Run `python3 d1b_independent_check.py`; it takes about 6 minutes on 4 cores.
**Outputs:** `results/d1b_independent_check.json` and `results/d1b_independent_check.log`.

The check never calls the simulation's ray trace, pupil/OPD, Debye integral or disc-weight code for its own numbers. I imported the simulation only afterwards, to put its numbers beside mine (section "Bugs" and the B table). No existing file was edited.

## Verdicts

| Claim | Verdict | Key numbers (independent check vs. claim) |
|---|---|---|
| **A** LA1509-A flat side first, w = 3 mm: about 1.2 waves of SA and LA about -0.9 mm at the 1 % radius | **CONFIRMED** | 1.228 waves (exact angle characteristic), 1.205 (thin- and thick-lens Seidel), 1.21 (the sim's finite-sphere definition). LA = -0.892 mm. |
| **B** Pocket for w = 3 mm: contrast about 20.7 at z = -0.76 mm, wall about 6 µm, axially stable. w = 4 mm: about 6.8 at -1.35 mm. w = 2.5 mm: about 2.7. Curved first: 3.4 or less | **CONFIRMED** (the sim's number is about 11 % low) | Exact angular spectrum gives **23.3 at -0.7635 mm**, wall 6.1 µm, dP0/dz < 0, stable run 64 µm. w = 4 mm: 7.0 at -1.370 mm. w = 2.5 mm: 2.84 at -0.774 mm. Curved first, w = 3 mm: no stable pocket (max 1.14); w = 4 and 6 mm: 3.5 and 3.4. Every case is within 12 % and 0.05 mm. |
| **C** v = η(C-1)·v_settle, so a 5 µm sphere draws at only about mm/s even at C = 80, and m/s needs something beyond gravity | **CONFIRMED for the stated case.** The generalisation is overstated. | 2.4 mm/s at C = 20.7 and 9.7 mm/s at C = 80. Temperature and slip change this by less than 2 % (and by ×0.70 even at the 700 K burn limit). Optimally sized heavier spheres in a scalable dark core reach **0.1 to 0.15 m/s** in the same model, which is still far below 1.8 m/s. A gradient-force estimate gives η about 0.26, not 0.4. |
| **D** A corner cube at L2's back focal plane refocuses onto the same trap point at any scan position, coaxially if the trap space is telecentric; a flat mirror inverts | **PARTLY CONFIRMED** | The paraxial geometry is exactly right, and it holds for **any** cube position. A real singlet L2, though, moves the return focus axially by +0.33 mm at 2 mm off axis and +2.0 mm at 5 mm. Telecentric scanning is the worst galvo position for the L1 pocket. A TIR cube fails (2 dB isolation, return-focus factor 0.31). |

Beyond the four claims, I tested things the simulation does not model (sections E and F). They matter more for the DIY build than the 10 % contrast discrepancy:

* **Galvo aperture.** A 7 mm galvo aperture on the w = 3 mm beam cuts the pocket contrast from 23 to **5.2**. An iris does the same thing.
* **Scanning.** Galvos at L1's front focal plane, the telecentric layout of DIY-2c, give a contrast of 12 at 1 mm and **3.6 at 2 mm** trap offset.
* **Coma-free pivot.** A galvo pivot about 25 to 35 mm before the flat face keeps the contrast at **21 to 22.6 out to 5 mm**.
* **Diode astigmatism.** The tolerance is about 0.1 wave (contrast 16 at 0.1 wave, 7.5 at 0.2, none at 0.4).
* **Beam size.** The contrast is sharply tuned: w = 2.9 / 3.0 / 3.1 / 3.25 mm give 14 / 23 / 33 / 29.

---

## A. Spherical aberration of the backwards LA1509-A

**Method (independent of the sim).**

* **Ray trace.** A scalar-trig meridional trace (angle form of Snell's law, not the sim's vector form), with N-BK7 n = 1.53024 (Schott h-line), R = 51.5 mm, tc = 3.6 mm.
* **OPD.** OPD is defined by Hamilton's angle characteristic: the optical path to the foot of the perpendicular dropped from the paraxial focus onto each ray. This is the OPD on a reference sphere of infinite radius, which is the phase a plane-wave (Debye) expansion needs.
* **Cross-checks.**
  * The exact identity dT/du = -d(u), i.e. W(u) = ∫ LA(u') sin u' du'. It agrees to all printed digits.
  * Thin-lens Seidel (Welford), with B = ∓1 and C = -1.
  * Surface-by-surface Seidel for the thick lens.

**Paraxial check.** Flat first: BFL = 97.126 mm = R/(n-1). Curved first: BFL = 94.773 mm = f - tc/n. Both are exact.

| w (mm) | h₉₉ (mm) | NA₉₉ | W₉₉ angle char. (waves) | W₉₉ sim definition | Seidel thin / thick | LA₉₉ exact (3rd order) |
|---|---|---|---|---|---|---|
| 2.5 flat | 3.794 | 0.039 | -0.589 | -0.60 | 0.581 / 0.581 | -0.619 (-0.612) mm |
| **3.0 flat** | **4.552** | **0.047** | **-1.228** | **-1.21** | **1.205 / 1.205** | **-0.892 (-0.878) mm** |
| 3.5 flat | 5.311 | 0.055 | -2.291 | -2.27 | 2.232 / 2.232 | -1.215 mm |
| 4.0 flat | 6.070 | 0.063 | -3.941 | -3.83 | 3.808 / 3.808 | -1.590 mm |
| 6.0 flat | 9.105 | 0.096 | -20.85 | -19.38 | 19.28 / 19.28 | -3.606 mm |
| 3.0 curved | 4.552 | 0.047 | -0.303 | (-0.30) | 0.303 / 0.301 | -0.222 mm |

* **Flat/curved SA ratio** at h = 1.5 mm: 4.012 from the trace, against 3.981 from thin-lens Seidel.
* **Reference-sphere difference.** The sim's W₉₉ is about 1.5 % smaller at w = 3 mm and about 7 % smaller at 6 mm. The cause is its finite reference sphere (see Bug 1). Seidel third order is 2 % below the exact value at w = 3 mm because of higher orders.
* **Definition note.** W here is measured about the paraxial focus. After best-focus balancing, the peak-to-valley is about a quarter of this. That is a wording point, not an error.

## B. Pocket in the focal region by an independent wave method

**Method.**

* **Exit-plane field.** I built the geometric-optics field on the real plane z = tc behind the lens: back vertex for flat first, back face for curved first. Each input ray h maps to an exit radius ρ(h). The phase is k·OPL(h), and the amplitude comes from energy conservation: |E|² cos u · ρ dρ = I_in · h dh, normalised to 1 W.
* **Propagation.** I then propagated with the **exact scalar angular spectrum in Hankel form**: A(κ) = ∫E J₀(κρ)ρ dρ by direct quadrature over h (dh = 0.25 µm), followed by U(r,z) = ∫A·exp(i k_z (L+z))·J₀(κr)·κ dκ with k_z - k evaluated without cancellation. There is no Debye or Fresnel approximation and no reference sphere.
* **Disc average.** A sparse polar quadrature (24-point Gauss-Legendre × 64-point trapezoid, linear interpolation of I(r)). This is a different scheme from the sim's exact annulus-overlap weights.
* **Metric.** The same metric as the claim: the first local maximum of P_int(r₀) divided by P_int(0). Stability requires dP_int(0)/dz < 0, beam pointing up.
* **Grids.** z from -2.4 to +1.0 mm in 4 µm steps, then a 0.5 µm refinement around the best point.

**Validation.**

| Check | Result |
|---|---|
| Airy peak / (πNA²/λ²) | 1.0000 |
| First zero / (0.61 λ/NA) | 1.0001 |
| Power 1 mm before focus | 0.998 W |
| Power in every config | 0.994 to 1.0004 W |
| Disc quadrature, I = 1 | error 8e-16 |
| Disc quadrature, I = r² | error 6e-4 |
| 2D model of section E reproduces 23.17 at -0.764 mm | yes |
| My own Debye integral with the angle-characteristic OPD | 23.23 at -0.7635 mm |

**Results (a = 2.5 µm).**

| Config | Sim (log or its own pipeline) | This check, best stable (0.5 µm z grid) | Wall r₀ | Stable run |
|---|---|---|---|---|
| flat, w 2.5 mm | 2.68 at -0.771 mm (guide: 2.7) | **2.84 at -0.7735 mm** | 6.0 µm | 72 µm |
| flat, w 2.75 mm | – | 7.04 at -0.766 | 6.1 | 68 |
| flat, w 2.9 mm | – | 14.2 at -0.7645 | 6.1 | 64 |
| **flat, w 3.0 mm** | **20.7 at -0.76** (sim fine z: 21.1 at -0.758) | **23.3 at -0.7635 mm** | **6.1** (sim 6.1) | 64 (sim 61) |
| flat, w 3.1 mm | 29.2 at -0.761 (sim pipeline) | **33.0 at -0.7635** | 6.1 | 60 |
| flat, w 3.25 mm | – | 28.9 at -0.7635 | 6.1 | 52 |
| flat, w 3.5 mm | 11.7 at -1.10 | 13.0 at -1.1085 | 4.7 (4.7) | 48 |
| **flat, w 4.0 mm** | **6.8 at -1.35** | **7.03 at -1.3695** | 4.1 (4.0) | 40 |
| flat, w 6.0 mm | 1.6 at -2.06 | 1.63 at -2.11 | 1.8 (1.8) | 40 |
| curved, w 3.0 mm | no stable pocket (max 1.13) | **no stable pocket (max 1.14)** | – | – |
| curved, w 4.0 mm | 3.4 at -0.39 | 3.52 at -0.387 | 4.8 | 36 |
| curved, w 6.0 mm | 3.4 at -0.38 | 3.43 at -0.3835 | 5.0 | 36 |
| flat, w 3 mm, a = 4 µm (toner) | 3.0 at -0.77 | 3.10 at -0.780 | – | – |

**Why the sim is about 10 % low at w = 3 mm.** This is fully attributed to its reference-sphere choice (Bug 1). Running my own Debye integral with the sim's finite-sphere OPD gives 21.2 at -0.7575 mm, which matches the sim's own fine-z value of 21.1. With the angle-characteristic OPD it gives 23.2, matching the exact propagation.

Disc averaging is not the cause: my quadrature applied to the sim's intensity reproduces 21.13 exactly.

### Refinements the claim does not state

1. **Axial margin.** In every configuration the minimum of P₀(z) falls within 0.5 µm of the contrast peak. The quoted best contrast therefore sits at the edge of axial stability: the stiffness there tends to 0.
   * Further upstream along z, the contrast and stiffness are:

     | Distance upstream of the P₀ minimum | Contrast | -dlnP₀/dz |
     |---|---|---|
     | 5 µm | 21.4 | 2.0 %/µm |
     | 10 µm | 18.1 | 3.4 %/µm |
     | 20 µm | 11.4 | 4.3 %/µm |

   * Levitation needs P₀(z_eq) = P_lev/(A·P_beam), and that must not fall below P₀,min. A beam power above P_lev/(A·P₀,min) ejects the particle upward.
   * The beam power that holds the particle 10 µm upstream (contrast about 18) is only about 1.3× below that ejection threshold. Expect to need power regulation of about ±10 %, and particle-to-particle absorptance spread will matter.
   * So "axially stable at contrast 20.7" holds, but realistically it means contrast **about 15 to 21**.

2. **The beam-size optimum is a grid artifact.** The pocket is a narrow resonance in SA. The peak is at **w ≈ 3.1 mm (W₉₉ ≈ 1.4 waves, contrast 33)**, not 3.0 mm. A ±3 % change in w swings the contrast between 14 and 33. The guide's "sweet spot 1 to 2 waves" is right in spirit, but a DIY diode beam whose size is uncertain by ±10 % could land anywhere between 3 and 33.

3. **Fragility.** A 0.02-wave phase change at the 1 % radius (Bug 1) moved the contrast by 10 %. Catalogue-singlet surface irregularity (λ/4 at 633 nm) is about 0.2 waves of transmitted wavefront error at 405 nm. Real-world contrast will scatter well below the ideal number (see E).

## C. Levitated drawing speed

**Derivation check.** The lateral holding force is F_lat = η(C-1)·mg. The drag is 6πμav/C_c and v_settle = mg·C_c/(6πμa); buoyancy is 0.3 %. So v = η(C-1)·v_settle exactly. The algebra is correct.

**Inputs, recomputed independently.**

* Viscosity: Sutherland in ICAO form.
* Mean free path: Chapman-Enskog, μ = 0.499 ρ c̄ λ, giving 65.2 nm.
* Slip correction: Allen & Raabe, which is a different fit from the sim's Davies; C_c = 1.030.
* v_settle for the 5 µm, ρ = 400 sphere: **0.308 mm/s**, matching the claim of about 0.3.

**Speeds and temperature effects.**

| C | v | Particle temperature rise at the wall |
|---|---|---|
| 20.7 | 2.43 mm/s | +1.4 K |
| 80 | 9.7 mm/s | +5.4 K |

* At these contrasts, the viscosity and slip changes are below 2 %.
* Even at the 700 K burn limit (film temperature 497 K), μ rises ×1.466 and C_c rises ×1.026. The net is a speed factor of ×0.70.
* **Neither temperature-dependent viscosity nor Cunningham changes the order of magnitude.** "About mm/s" is fair; precisely, it is 2 to 10 mm/s.
* The burn cap is 9.3×10³ in my cruder model (no temperature jump), against the sim's 7.3×10³. Either way it is far above the optical contrast, so the **optics, not burning, limit the 5 µm sphere**. It would need C ≈ 2400 to reach 0.3 m/s.

**Force law.**

* Applying the linear-gradient photophoretic law F_lat = (3/8)·a·∇I (skin absorber, hemisphere heat dipole) to the computed w = 3 mm pocket gives a maximum lateral force of 5.7·mg. The η(C-1) law gives 8.9·mg.
* That corresponds to an **equivalent η of about 0.26**, so the claimed speeds are optimistic by about 1.5×. This strengthens the claim.

**Overstated generalisation.**

* At C_opt ≥ C_burn, the levitated bound equals the burn-limited, axially balanced bound η·fpw·P_burn/drag, and that bound does not depend on weight. The gravity penalty is not intrinsic: it comes from C_burn ∝ 1/(ρa³) being far above the optical contrast for light 5 µm particles.
* Scanning sizes with physically paired (ρ, k_p, T_max), η = 0.4, and the wall held at half the burn power (in brackets: at the burn limit):

  | Particle | C_opt = 80 (scalable vortex core) | C_opt = 20.7 |
  |---|---|---|
  | Hollow glass with carbon skin, d ≈ 20 to 25 µm | 0.11 (0.15) m/s | 0.07 (0.09) m/s, d ≈ 31 to 39 µm |
  | Solid glass with skin | 0.05 (0.07) m/s | |
  | Black polymer | 0.03 (0.05) m/s | |
  | Glassy carbon | 0.02 (0.03) m/s | |

* The singlet SA pocket cannot serve these larger particles. Its wall is at 6 µm, so already at a = 4 µm the contrast is only 3.1. Large spheres need a dark core that scales with them, such as a vortex or bottle beam far from focus.
* **The conclusion survives.** In this sphere model, gravity-levitated spheres top out around 0.1 m/s, well short of 1.8 m/s and short of the 0.3 m/s the guide needs for a 1 cm glyph at 10 Hz. But "about mm/s" describes only the 5 µm sphere. With bigger hollow spheres and a vortex core, about 0.1 m/s (3 to 5 mm glyphs at 10 Hz) is not excluded.
* I did not verify the BYU 0 g / 2 g statement; it was outside the scope of the tools here.

## D. Corner-cube return beam

**ABCD analysis** (lab-frame slopes; corner cube = point inversion, (x, θ) → (-x, θ); flat mirror (x, θ) → (x, -θ)). The trap sits in L2's front focal plane, and the reflector sits at L2's back focal plane plus e.

* **Corner cube:** the round trip is M = [[1, 0], [2e/f², -1]].
  * **The trap plane is imaged onto itself with m = +1 for any e.** BFP placement is not needed for refocusing onto the same point.
  * The offset e only tilts the return cone, by 2e·x₀/f². For f = 100 mm and x₀ = 5 mm, that is 5 mrad at e = 5 mm and 20 mrad at e = 20 mm.
  * With e = 0 and telecentric trap space, the return cone is exactly coaxial. That part of the claim is confirmed, and it is the only thing the BFP position buys, besides keeping the footprint centred on the vertex.
* **Flat mirror at the BFP:** M = [[-1, 0], [-2e/f², 1]], so x₀ → -x₀. "Images the point to the opposite side" is confirmed.
* **Spherical mirrors.** A concave mirror centred on the trap also inverts. A cat's eye (lens plus mirror at its focus, i.e. a mirror at an intermediate image) would work like the cube, so "any plain mirror fails" is true only in the collimated space.
* **Trap off L2's front focal plane** by δ: the return focuses at -δ, the mirror image. The lateral position holds to second order: 2eδx₀/f² = 3 µm for e = 10 mm, δ = 0.3 mm, x₀ = 5 mm.
* **Wave picture.** L2 plus cube acts as a **plane mirror at L2's front focal plane**, not a phase conjugator: I_ret(x, y, z) = T·I_fwd(x, y, 2z_FFP - z).
  * The forward and return pockets coincide only if L2's front focal plane is placed at the forward pocket, about 0.76 mm before L1's paraxial focus.
  * The return's on-axis intercept rises upward, which stabilises the particle. Moving L2 by Δ moves the return by 2Δ.

**Exact 3D vector trace** (real LA1509 as L2, flat side toward the trap, ideal hollow cube, telecentric cone from the trap):

* **Lateral tracking is confirmed.** The mean return position is within 0.02 µm at x₀ = 2 mm and within 1.7 µm at 5 mm (e = 0).
* **The return focus walks axially.** This comes from L2's field curvature and astigmatism, doubled by the double pass:

  | Cone NA | On axis | x₀ = 2 mm | x₀ = 5 mm |
  |---|---|---|---|
  | 0.01 | +13 µm | **+334 µm** | **+2.04 mm** |
  | 0.047 | +0.30 mm (L2's own double-pass SA, roughly 0.6 extra waves at the 1 % radius) | +0.62 mm | +2.3 mm |

* The pocket is only about ±20 µm deep in z. A singlet L2 therefore keeps the return inside the pocket only within about **±0.5 mm** of the axis, since the shift scales as x₀². "Any lateral trap position" holds paraxially only.
* L2 needs to be a flat-field, well-corrected (telecentric scan-type) lens. L1's own field curvature adds to the mismatch.
* The extra SA in the return beam also changes its pocket, because the pocket is sharply tuned (see B).

**Coaxiality conflicts with the pocket.** A coaxial return needs galvos at L1's front focal plane, which is telecentric. But that is the worst pivot for the backwards-L1 pocket (section E: contrast 12 at 1 mm, 3.6 at 2 mm). At the coma-free pivot about 30 mm before the lens, the chief ray in trap space has slope about 0.69·x/f. The return cone is then tilted 2θ_c from the forward cone: 28 mrad at x = 2 mm, against a cone NA of 47 mrad. It still refocuses on the same point.

**Polarisation and feedback.** 3D polarisation ray trace with Chipman PRT matrices and Fresnel coefficients; laser x-polarised, PBS, QWP at 45°, cube, QWP, PBS; galvo mirrors assumed ideal:

| Cube | Cube reflectance | Return fraction the PBS sends back to the laser | Isolation | Return-focus factor from sector polarisation |
|---|---|---|---|---|
| Hollow, perfect conductor | 1.000 | 0 | complete | 1.000 |
| Hollow, bare Al (n = 0.49 + 4.86i) | 0.768 | 1.4e-4 | 38.6 dB | 0.998 |
| Solid N-BK7, uncoated TIR | 1.000 | 0.61 | **2.2 dB** | **0.31** |

The guide's "metal-coated hollow cube" advice is correct, and a TIR cube is unusable.

Caveats I did not model:

* **Galvo mirrors and QWP placement.** The galvo mirrors' s/p retardance changes with scan angle, especially for dielectric HR coatings at 45° ± scan. With the QWP before the galvos, the isolation becomes scan-dependent; putting it between the galvos and L1 is cleaner.
* **Feedback into the diode.** The return retraces the whole train into the diode. Round-trip transmission is about 0.6 to 0.7 with Al, and realistic isolation is 20 to 30 dB, so expect about 0.05 to 0.7 % optical feedback. That is enough to destabilise a single-mode 405 nm diode; a multimode diode will more likely show power noise. A Faraday isolator is the robust fix, as the guide says.
* **Axial balance.** T < 1 leaves a net upward push of (1-T), so the balance point is set by geometry (the L2 offset), not by the beams' equality.
* **Cube accuracy.** The return focus is displaced by f₂ times the cube's beam deviation, and tilting the cube does not remove it. At f₂ = 97 mm:

  | Beam deviation | Return-focus offset |
  |---|---|
  | 5 arcsec | 2.4 µm |
  | 30 arcsec | 14 µm |
  | 1 arcmin | 28 µm |

  The pocket wall is at 6 µm, so the cube must be **≤ 5 arcsec**; a cheap 1 to 3 arcmin cube will miss.
* **Coherence.** Coherent forward/return interference has a 202 nm period and averages out over a 5 µm particle.

## E. Beyond the claims: scanning, decenter, astigmatism (flat first, w = 3 mm)

**Method.**

* An exact 3D vector trace of the tilted, decentred input beam through L1.
* The 3D angle characteristic about the chief ray's paraxial-plane point, interpolated onto a regular (s_x, s_y) grid. The amplitude comes from the ray Jacobian.
* A 2D angular-spectrum sum by matrix Fourier transform, then a disc average by FFT with the analytic disc transform 2πaJ₁(qa)/q.
* The 2D escape barrier is found by bisection on sub-level-set connectivity over all local minima within 20 µm of the chief ray. The pocket must also be axially stable.
* On axis it reproduces 23.17 at -0.764 mm.

| Perturbation | Best stable 2D contrast |
|---|---|
| none | 23.2 |
| input astigmatism 0.05 / 0.1 / 0.2 / 0.4 waves (ρ²cos2φ at h₉₉) | 21.1 / 16.3 / 7.5 / about 1 (none) |
| input coma 0.1 / 0.2 / 0.4 waves (ρ³cosφ at h₉₉) | 21.7 / 20.3 / 16.8 |
| lens decentred 0.1 / 0.3 mm | 21.7 / 18.3 |
| scan, galvo at L1's front focal point (telecentric), trap at 0.25 / 0.5 / 1 / 2 mm | 20.8 / 17.5 / 11.9 / **3.6** |
| scan, galvo at the lens, trap at 0.25 / 0.5 / 1 / 2 / 3 mm | 21.7 / 20.2 / 18.1 / 12.2 / 7.3 |
| trap at 2 mm, pivot 15 / 25 / 35 / 50 / 70 mm before the flat face | 17.4 / 20.9 / 21.5 / 16.7 / 9.7 |
| **pivot 30 mm before the lens**, trap at 2 / 3 / 4 / 5 mm | **22.0 / 22.6 / 22.3 / 22.4**; the pocket z shifts by -15 to -85 µm, which is field curvature |

**Readings.**

* A coma-free stop position exists (stop-shift cancellation of the SA-induced coma). Put the galvo pivot (the midpoint of the X and Y mirrors) **about 25 to 35 mm before the flat face**.
* Do **not** put the galvos at L1's front focal plane: that is the guide's DIY-2c layout.
* Diode astigmatism must be corrected to **≲ 0.1 wave** at the 1 % radius, i.e. ≲ 0.2 wave peak to valley over 9 mm. That is tighter than typical uncorrected diode modules.

## F. Guide statement "a 6 mm beam also fits standard 7 mm galvo mirrors"

The pocket is made by the SA phase of rays out to and beyond the 1 % radius (4.55 mm). A hard aperture cuts those rays off. I modelled the aperture at the lens; with a Fresnel number of about 1000 at 30 mm, that is a good approximation.

| Aperture diameter | Best stable contrast | Position |
|---|---|---|
| 7 mm | **5.2** | -0.88 mm |
| 8 mm | 6.8 | -0.80 mm |
| 10 mm | 20.9 | -0.76 mm |

**Use 10 mm mirrors, or a larger aperture.** The guide's advice to "tune the beam size with an iris" has the same flaw: an iris truncates the beam rather than resizing it. Tune w with the expander instead.

---

## Bugs and issues in the simulation

1. **Wrong OPD definition for the Debye phase** (`sim_d1_lens_trap.py`, lines 83 to 93, `pupil()`, used at line 125).
   * W is the OPD on a reference sphere of finite radius Rr = zF - tc, passing through the back vertex. The Debye/plane-wave integral needs the angle characteristic, i.e. an infinite radius. The phase error is R - √(R² - d²) ≈ (LA·sin θ)²/2R, with d the ray's perpendicular miss distance from F. That is 0.0225 waves at the 1 % radius for w = 3 mm.
   * **Effects:**
     * the w = 3 mm best contrast comes out at 21.1 instead of 23.3 (-9 %), and z shifts by +5 µm;
     * the reported W₉₉ is 1.21 instead of 1.23 waves, 3.83 instead of 3.94 at w = 4 mm, and 19.4 instead of 20.8 at w = 6 mm.
   * It is not conclusion-changing.
   * **Fix:** W = opl + (C - p)·d - (opl_axis + Rr), i.e. the path to the foot of the perpendicular from C.
2. **The quoted 20.7 is a coarse-grid sample** (700 z points over 2.67 mm, 3.8 µm steps). The sim's own fine-z maximum is 21.1.
3. **"Best at w = 3 mm" is an artifact of the CONFIGS grid** (line 344: 2, 3, 3.5, 4, 6 mm). The sim itself gives 29.2 at w = 3.1 mm; the exact value is 33.0.
4. **The best-trap selection** (line 180, `best_trap`) picks the zero-stiffness edge of axial stability (see B, refinement 1). It is not a coding bug, but the reported "stable" contrast is a limit value.
5. **Minor.**
   * Line 116 omits the 1/√cos θ Debye apodisation: under 0.3 % at NA 0.1.
   * In `diy_calcs.v_levitated` (line 65), only the viscosity is taken at the film temperature; the Cunningham factor is not. That is at most 3 % at the burn limit.
   * `window()` (line 49) evaluates force per watt at 293 K, while v_max uses μ at the film temperature. This is inconsistent but irrelevant for C ≤ 80.
6. **Not modelled, but decisive for the build** (the sim says so in its docstring): scanning coma, astigmatism, aperture clipping. These are quantified in E and F; they matter more than items 1 to 5.

## Limits of this check

* The model is scalar (NA ≤ 0.1), with a geometric-optics field at the lens exit; the lens Fresnel number is large, so that is valid.
* The input is an ideal TEM00 beam, with Fresnel transmission variation ignored.
* I kept the same particle model as the sim: intercepted power over a transverse disc, ΔT photophoresis. I questioned its lateral efficiency only through the gradient law.
* The polarisation numbers cover the cube alone.
* No measurement data were used.

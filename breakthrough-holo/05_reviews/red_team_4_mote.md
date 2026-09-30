# Red team 4: the MOTE route (Phase 3)

Reviewer roles: aerosol and photophoresis physicist, laser-safety assessor, optical and control engineer. The brief was to find everything that is wrong, optimistic or unsupported, ranked by how much it could change the conclusions.

**State reviewed** (2026-09-30, 17:05–17:36 UTC; the lab edited files during the review, and the versions listed are the ones used):
- `07_mote_route/mote/physics.py` (16:43), `safety.py` (16:44), `budget.py` (17:08, with `B_focus`, the `single` architecture and the v2 wall-light model), `feedback.py` (17:13, with the force lag), `dynamics.py`
- `validation/validate_mote.py` and `results/validation_mote.json` (26/26)
- `sim_m1_atlas.py`, `sim_m1c_focus_scenarios.py`, `sim_m2_feedback_scan.py`, `sim_m2b_force_lag.py`, `sim_m3_steering_spec.py`, and all `results/*.json|log` up to `m2c_slow_force.log`
- `02_theory/T5_mote_theory.md`, `07_mote_route/RESULTS.md`, `PREDICTIONS.md`, R5–R7, and a skim of R8 (arrived 17:33)

**Method.** Numbers marked *[RT4]* were computed for this review. The scratch scripts are in the session scratchpad (`…/scratchpad/rt4/`) and are not committed:
- `r2_prefactor.py`: first-principles prefactor
- `r3_sens.py`: sensitivity atlas
- `fb_real.py`, `r4b.py`, `r4c.py`: feedback with a realisable beam
- `r5_j1.py`: ray-traced J₁
- `r6_material.py`, `r8_dense.py`: material-consistent atlas
- `r7_overlap.py`: pump-beam overlap
- `r9_lg01.py`: exact doughnut force
- `r10_corrected.py`: combined corrected atlas
- `r11_misc.py`: other checks

The sensitivity and corrected atlases re-use the lab's `budget.design` through monkeypatches, on the same grid as `sim_m1_atlas.py`. Items marked **[memory]** come from recall; web access to full texts was blocked, so check them before using them as pass/fail criteria.

**Headline reproduced exactly** *[RT4]*: film density with push4, a = 1 µm, k_p = 0.02, 300 mm heads, cyan phosphor at 405 nm:
- v = 1.14 m/s, N = 1 131, 4 524 channels;
- ΔT = 149 K, 0.874 mW per trap beam, 1.81 W at 1550 nm;
- 36.2 µW per pump beam against a 39 µW AEL.

The next speed step (1.42 m/s) fails both the heat limit and the pump AEL, so **the design sits on two constraint edges at once**.

**Severity counts:** 3 critical, 11 major, 11 minor.

---

## Verified correct

- **Air and aerosol properties.** Mean free path, Cunningham factor, settling and diffusion (M01–M04). Stokes–Oseen drag.
- **Heat balance.** The Kirchhoff integral and the Fuchs temperature-jump form Q = 4πa∫k dT/(1+ζ/a) are right. Radiation is negligible (~2×10⁻⁸ W against ~5×10⁻⁵ W).
- **Structure of the slip correction.** Solving the l = 1 conduction problem with a temperature jump gives exactly [(k_p + 2k_g)(1 + 2c_t Kn k_p/(k_p+2k_g))]⁻¹. The momentum factor (1+3c_m Kn)⁻¹ is Brock's. At Kn ≈ 0.07–0.1 the Talbot-coefficient interpolation is good to about ±20 % [memory].
- **Lateral dipole ratio F_x/F_z = (3/8) g a.** Correct in the linear limit (g·a ≪ 1) for an isotropic sphere that absorbs at its surface.
  - Internal conduction does not change it, because both components share the factor 1/(k_p+2k_g).
  - The sign (force toward lower intensity) is right.
  - Its misuse at large a/w is Major 2.
- **Heat-force identity algebra.** F/ΔT = 18π μ² J₁′ k_g/(ρT(k_p+2k_g)) is correct in the continuum *for surface absorption*. See Major 3 for why it fails for real motes.
- **Push-trap allocation factors.** Tetrahedral: 3 / 2.23 / 1.22. Octahedral: √3 / 1.5 / 1.0. M14 checks these against a linear programme.
- **Class 1 AELs.** 405 nm 39 µW, 980 nm 1.42 mW and 1550 nm 10 mW match IEC 60825-1:2014 as I recall it [memory].
- **1550 nm trap beams are Class 1 in normal operation.** 0.87 mW per beam. The worst-case sum of 20 foci lined up along one head's axis through a 3.5 mm stop is 4.5 mW *[RT4]*. The exit-window rule gives 36.7 W per head.
- **Checked and negligible** *[RT4]*:
  - Brownian motion: 41 nm rms per 50 µs.
  - Gravity: 6×10⁻¹⁴ N against 5×10⁻¹⁰ N of drag.
  - Radiation pressure.
  - Out-of-focus beams at other motes: about 3 foreign motes sit inside each cone within ±0.25 m, but at ≤ 10⁻⁵ of the focal intensity.
  - Photon budget for 0.5 µm sensing: about 10⁶ backscattered photons per 50 µs.

---

## Critical

### C1. The mote the whole route depends on is self-contradictory

With a physically consistent mote, every content target is infeasible or an order of magnitude harder.

**What the budget assumes, all at once, in a mote of radius 1 µm:**
- k_p = 0.02 W/m/K. That is *below still air* (0.026). Only a nanoporous aerogel-like solid reaches it.
- J₁/A = 0.5 with A_trap = 0.9 at 1550 nm, i.e. all heat deposited in a skin much thinner than a.
- A_abs = 0.7 at 405 nm for the phosphor. For a ≤ 2 µm grain this needs α ≈ 9 000 cm⁻¹. Eu²⁺ phosphors at usual doping are about 10³ cm⁻¹ [memory, unverified]. Powders absorb well only through multiple scattering over many grains.
- For the UC emitter, `uc_absorptance(a, x_Yb)` treats **the whole mote as a dense NaYF₄:Yb crystal**. Such a crystal has k_p of order 1–5 W/m/K [memory], not 0.02.

**These requirements conflict.** A low-k carrier is mostly void, so any absorber dispersed in it absorbs through the volume, and J₁ collapses. A dense emitter or absorber brings k_p ≥ 1.

**Evidence** *[RT4]*.

*J₁ collapses unless absorption is very shallow.* A geometric-optics ray trace (refraction, Beer–Lambert, one internal reflection; `r5_j1.py`) gives J₁/Q_abs = −0.5 only for α·a ≳ 30:

| α·a | 1 | 2 | 3 | 5 | 10 | 30 |
|---|---|---|---|---|---|---|
| J₁/Q_abs (n = 1.5) | −0.06 | −0.20 | −0.29 | −0.38 | −0.45 | −0.49 |

For α·a ≲ 0.3 it changes sign (negative photophoresis).

*Consequences for specific motes:*
- Solid carbon at 1550 nm (k ≈ 0.8 [memory], α ≈ 6.5×10⁴ cm⁻¹), a = 1 µm: J₁/A ≈ 0.40.
- The same carbon at 10 vol % in an aerogel: J₁/A = 0.02 (a = 1 µm) and 0.16 (a = 2.5 µm).
- A thin opaque skin (α·t ≥ 2) on an aerogel core has k_eff ≈ k_core + 4k_skin/(α·a). For amorphous carbon at a = 1 µm that is ≈ 0.9 W/m/K.

*Material-consistent atlases* (same grid as M1, film density unless stated; `r6`, `r8`, `r10`):

| Mote model | Best film-density design | Motes | Channels | 1550 nm total |
|---|---|---|---|---|
| As coded (k_p 0.02, J₁/A 0.5, A 0.9) | push4, a = 1 µm | 1 131 | 4 524 | 1.8 W |
| Porous low-k: k_p 0.03, 10 % carbon (J₁/A from ray trace), Tf fix | lateral2 UC, a = 5 µm (still with the coded doughnut error, Major 2) | 13 166 | 26 331 | 4.6 W |
| Plausible-optimistic: k_p 0.15, J₁/A 0.4, A 0.85, with Majors 1–2 and C3's A_abs 0.3 and 0.5 µm jitter | push6, a = 1 µm, v = 0.30 m/s | 4 314 | 25 885 | 10.6 W |
| Pessimistic: k_p 0.5, same corrections | **none**, not even the 1 m accent | – | – | – |
| Dense: k_p 1 or 3, carbon-like J₁, T_max 450 **or 600 K** | **none**, not even the 1 m accent | – | – | – |

**The figure of merit (J₁/A)/(k_p + 2k_g) governs everything.** In the headline it is 6.1 m·K/W. A carbon-skinned aerogel reaches about 1.9 (3× worse). Dense carbon reaches 0.4 (15× worse).

**Fix.**
- State in T5 and RESULTS that the route requires a mote with (J₁/A)/(k_p + 2k_g) ≳ 3–6 m·K/W. No such particle has been made or measured.
- Make the atlas material-consistent:
  - J₁/A and A_trap as functions of (α, a, n);
  - k_eff from a core–shell model;
  - pump absorptance from the emitter's own volume, not the mote's.
- Until a mote is measured, report the conclusion as a range spanning the plausible-optimistic and dense rows above.
- This, not steering, is the first thing a bench must settle (T5 §11 item 2 should become item 1).

### C2. The push-trap feedback result (15–20 kHz) comes from a beam that cannot exist at NA 0.1. With a realisable beam it needs 50–100 kHz.

**What is wrong.**
- `feedback.py` uses a super-Gaussian flat-top exp(−2(ρ/R)⁸) with R_ft = 10 µm.
- Its 10–90 % edge is 3.3 µm wide.
- The diffraction-limited coherent edge at NA 0.1 and 1550 nm is ≥ 5.5 µm (with 19 % overshoot) *[RT4]*.
- The beam also carries 1.86× the power the budget allots (I·πw² with w = 6.41 µm).

**The realisable beam.** The only profile consistent with the budget's "power factor 2" is an incoherent LG00 + LG01 mix at w = 6.41 µm:
- α = 0.5 gives zero curvature;
- α = 0.4 gives a 7 % dimple at 2.5× power.

The flat mix stays within 3 % of peak only out to 2.4 µm. Beyond that it pushes the mote outward: (3/8)·a·g = −0.03 at 3 µm and −0.10 at 5 µm. With the loop's 2T steering lag, that anti-spring runs away.

**Evidence** *[RT4]*. The lab's own `feedback.run`, patched only for the profile (`fb_real.py`); 32 motes, a = 1 µm, 1 m/s circle, 0.1 m/s draft; loss when ρ > 1.2w in ≥ 2 beams:

| Beam | 20 kHz | 50 kHz | 100 kHz | 200 kHz |
|---|---|---|---|---|
| Lab flat-top, R_ft = 10 µm (gust σ 0.1) | 0 % lost | 0 % | 0 % | – |
| LG mix α = 0.5, flat (σ 0.1) | **100 % lost within 0.6 ms** | **100 % within 4 ms** | 0 % | 0 % |
| LG mix α = 0.5 (σ 0.2) | – | **100 %** | 0 % | 0 % |
| LG mix α = 0.4, dimpled (σ 0.1) | **97 % lost** (median 57 ms) | 0 % | 0 % | 0 % |
| LG mix α = 0.4 (σ 0.2) | – | 3 % | 0 % | 0 % |

**The statistics cannot support the claim anyway.**
- Zero losses in 6.4 mote-seconds gives a 95 % upper bound of 3/6.4 s ≈ 28 per minute per mote, not "< 1 %/min". Demonstrating < 1 %/min needs ≥ 18 000 loss-free mote-seconds.
- The Rayleigh-tail extrapolation reported in `m2_feedback_scan` (10⁻³⁰/min) is contradicted inside the same runs. At a = 2.5 µm and 20 kHz, 34 % of motes were lost in 0.2 s while the extrapolation printed 1.9×10⁻³³/min. RESULTS now acknowledges the statistics, but the extrapolated numbers remain in the JSON.
- The sim lets each beam push up to 1.5 × drag(v + 0.3). That is about 1.6× the thermal authority the budget allows, and the sim tracks no mote temperature.

**Corrected number.**
- Loop rate ≥ 50 kHz with a dimpled beam (+25 % trap power), or ≈ 100 kHz with a flat one.
- Steering actuators need time constants of ≈ 10–20 µs. That means AOD or EO class; galvos and MEMS are ruled out.
- **P23 (2–20 kHz) scores ✗**, not "partial".

**Fix.**
- Replace the super-Gaussian with a band-limited profile computed from the pupil at the design NA.
- Cap force by heat and track T inside the sim.
- Run ≥ 10⁴ mote-seconds, or use importance sampling.
- Report lateral2 as the passive alternative (Major 2).

### C3. "Class 1" is not established for the product. The 405 nm pump fails once overlap, pointing and single faults are counted.

**What is wrong.** `safety.py` and `budget.py` check each beam alone against the AEL (pump: 36.2 of 39 µW, a 7 % margin). They do not check:

**(a) Overlap.** Accessible emission is the *sum* through a 7 mm aperture. When motes lie along a stroke pointing toward their pump head, spaced 2.65 cm (one segment per frame), a pupil at one focus receives *[RT4, `r7_overlap.py`]*:

| Motes on the axis | 1 | 2 | 3 | 5 | 20 |
|---|---|---|---|---|---|
| Power at the pupil | 36 µW | 71 µW | 92 µW | 111 µW | 132 µW |
| × AEL | 0.93 | 1.8 | 2.4 | 2.9 | **3.4** |

At 100 mm upstream (Condition 3), 20 motes still give 0.8× AEL. Any content with depth strokes breaks Class 1 unless pump routing forbids this geometry.

**(b) Pointing.** The pump waist is 1.68 µm, with z_R = 16.8 µm including M² = 1.3 (M3 uses 22 µm, without M²). With the mote-to-beam jitter the lab's own M2 run produces (0.85 µm rms per axis), the average intercept falls from 0.51 to 0.30, and the pump per beam rises to about 62 µW (1.6× AEL). At 0.36 µm jitter (a 100 kHz loop) it is still 41 µW.
- Indoor turbulence adds to this. The tilt-removed Strehl at 405 nm through 0.3 m is 0.76 at C_n² = 10⁻¹³ and 0.06 at 10⁻¹², the latter typical of a person's thermal plume [memory for C_n² ranges].

**(c) Absorptance.** A_abs = 0.7 is unsupported (C1). At A_abs = 0.3, every phosphor design in the atlas fails at 405 nm.

**(d) Single fault.** IEC 60825-1 classifies under reasonably foreseeable single faults [memory]. Loss or freeze of a head's multiplexer (hologram collapse to one spot, zero order, steering stall) focuses the whole head into one spot:
- 405 nm: ≈ 10 mW, 256× the AEL.
- 1550 nm: 0.45 W, 45× the AEL, Class 3B.

The embedded sources are Class 3B. Claiming Class 1 then needs a safety-rated, independent power monitor with shutdown in ≲ 0.4 ms at 405 nm (10 mW × t ≤ ~3.9 µJ, the short-exposure AEL [memory]) and ≲ 18 ms at 1550 nm (8 mJ). None is designed. `safety.py` models only a scan stall of a time-shared channel.

**Corrected statement.**
- 1550 nm: Class 1 in normal operation is plausible.
- 405 nm: Class 1 is not met with the stated margins.
- Product: Class 1 is contingent on a certified fault-shutdown design.

At a pump margin that survives overlap and jitter (≤ 0.3× AEL per beam), the phosphor film-density design needs about 3× more motes, or must move to larger motes.

**Fix.**
- Add a point-sum AEL check over all beams at worst-case accessible positions (the focus and 100 mm) for the actual stroke geometry.
- Add a pointing-jitter and turbulence derate to the pump intercept.
- Add a single-fault section with numbers.
- Treat the 980 nm UC film-exact design (1.24 of 1.43 mW, 87 %) the same way.

---

## Major

### 1. A spurious (T_f/T₀) factor raises the photophoretic force by 25 % at the design point

**What is wrong.** `photophoretic_force` uses μ(T_f)²/(ρ(T_f)·T₀). The creep coefficient is ν/T = μR/p, so ρ and T must be taken at the same state. Mixing them multiplies the force by T_f/T₀, which is 1.254 at T_m = 442 K *[RT4]*.

**Effect** *[RT4]*. Removing the factor gives film density at push4:
- v = 0.91 m/s, N = 1 414, 5 655 channels (+25 %);
- 2.34 W at 1550 nm.

**Fix.** Use ρ(T_f)·T_f, or μ²R/p.

### 2. The lateral2 (doughnut) trap model is wrong in both directions: badly optimistic for large motes, pessimistic in heat for small ones

**What is wrong.**
- **Beam power.** `profile = e/2` implies an on-mote intensity 4P/(eπw²), twice the true LG01 peak 2P/(eπw²). At the r = w/2 flank the model assumes, the power is understated 2.43×.
- **Nonlinearity.** (3/8)·g·a is linear. At a = 5 µm, w = 6.4 µm, g·a ≈ 1.6 and the mote spans the ring.

**Evidence.** Exact surface-flux dipole integrated over the lit hemisphere of the sphere in an LG01 beam, maximised over position (`r9_lg01.py`) *[RT4]*:

| a | η coded | η exact (at max force) | Force per beam W, code/exact |
|---|---|---|---|
| 1 µm | 0.117 | **0.247** (at r = 0.33 w) | 1.9× optimistic |
| 2.5 µm | 0.293 | 0.372 | 2.6× optimistic |
| 5 µm | 0.585 | **0.118** | **13.5× optimistic**; heat per force 5× understated |

**Consequences.**
- The UC lateral2 design (a = 5 µm, 2 761 motes, 0.98 W), which RESULTS lists as the UC option, is invalid by about an order of magnitude.
- At a = 1 µm, lateral2 is *better* on heat than coded. With the exact model it becomes the best film-density design: 1 767 motes, **3 534 channels**, 9.7 W, 2.75 mW per beam, Class 1 *[RT4]*.
- It is a *passive* lateral trap, so the 50–100 kHz loop of C2 is not needed laterally. This is a genuine opportunity for the lab.

**Fix.** Replace `eta_lateral` and `profile` with the exact integral, tabulated in a/w.

### 3. J₁ = 0.5·A and the "size-independent" heat-force identity hold only for skin-deep absorption

**What is wrong.**
- The identity assumes J₁/A = ½ for all sizes. In fact J₁/A = f(α·a), so for a fixed material small motes lose force per kelvin (C1 table).
- This removes most of the 1/a speed advantage that makes a = 1 µm optimal.
- At a = 1 µm and 1550 nm the size parameter is x ≈ 4. Mie internal-field hot spots can move J₁ either way. A Mie internal-field calculation is needed; geometric optics is only indicative there.
- ½·A is not an upper bound. Surface heating allows |J₁| ≤ 0.75·A (all heat at the pole). ½ is the natural value for an opaque Lambertian sphere, not the maximum.

**Fix.** Compute J₁(x, m) with Mie internal fields for the candidate materials and carry it into the atlas.

### 4. The C_ph range [1, 1.56] is inconsistent with the code's own J₁ normalisation

**Evidence** *[RT4, `r2_prefactor.py`]*.
- Thermal creep over a held sphere gives F = 4π C_s μν T₁/T. The chain was checked by the squirmer relation U = 2B₁/3 and by reproducing Epstein's thermophoretic force exactly (ratio 1.0000).
- The surface-flux dipole T₁ = |J₁| I a/(k_p + 2k_g), with J₁ = −½ for an opaque sphere, was checked numerically.
- Together these make the code's 9π/2 prefactor correspond to **C_s = 9/8, not 3/4**.

So C_ph = 1 is already the kinetic value; Talbot's C_s = 1.17 gives C_ph = 1.04. The defensible range is C_ph ∈ [0.67 (Maxwell), 1.04]. The literature formula could not be fetched to confirm the published normalisation [memory: "9π/2 with J₁ = −½" is the usual form]. Either way, **1.56 double-counts**.

**Where this matters.** C_ph = 1 is not "conservative". M22 used 1.56 in its BYU window. T5 §11 asks the bench to "settle C_ph ∈ [1, 1.56]".

**Fix.** Correct the docstring, T5 §1 and M22.

### 5. The steering wall is an étendue (space–bandwidth) wall, not only integration

**What is wrong.** "Channels = N × heads" assumes every channel can reach the whole 1 m field at NA 0.1 through one shared 300 mm aperture.

**Evidence** *[RT4]*. The head's space–bandwidth product is (0.3 m × 0.67 rad/λ)²:
- 1.6×10¹⁰ at 1550 nm;
- 2.3×10¹¹ at 405 nm.

A shared-aperture holographic multiplexer would need that many pixels, updated at ≥ 50 kHz. The largest phase SLMs have about 3×10⁷ pixels at ≤ 1 kHz [memory].

Separate steerers must split the head's étendue:
- 1 131 channels per head leaves each channel a tile of about 3 × 3 cm. At 1.14 m/s a mote crosses a tile about once per frame.
- Relayed to a 0.3 m aperture, a 2 mm MEMS mirror (±0.35 rad) covers a 0.7 cm tile, i.e. about 20 000 tiles per m².
- A 30 mm galvo covers a 21 cm tile, but only about 23 such channels fit in one head.

**Real hardware** is therefore about (field/tile)² channels per head with hand-over every frame, or a modulator 10³–10⁴× beyond the state of the art. Physics does not forbid it, but "every function exists in some device" understates the gap by orders of magnitude.

**Fix.** Add the étendue bound to M3. Count tiles and hand-overs, not N × heads.

### 6. The `single` architecture (η = 0.5, h_worst = 1) is unsupported, and the lab's own R8 now says so

- η_single = 0.5 is inferred from M22, which assumes the force model it is meant to test (circular).
- h_worst = 1 assumes the same force *toward the source*. R8 finds η_upstream ≈ 0 (bounded by about NA) for opaque motes, and BYU's 1.83 m/s was transverse.
- m1c's best `single` rows also need 600 mm apertures and a 0.8 µm pump waist with z_R ≈ 4 µm at 1.5 m.

**Fix.** Remove `single` from the atlas unless it is given an upstream η ≤ NA, or an explicitly hypothetical pull mote.

### 7. Unmodelled forces of 10–50 % of the trap force

*[RT4, `r11_misc.py`]*
- **Pump photophoresis.** The phosphor's pump heat (4.6 µW) is **0.29×** the force-producing absorbed power, fixed along the pump axis. It is counted in temperature but not in force.
- **Δα force.** Gas-temperature dipole ≈ 2(ζ/a)·Δα·ΔT_mean = 0.28·Δα·ΔT, against ≈ 38 K of net ΔT-dipole in the worst direction. That is 11–33 % for Δα = 0.1–0.3, fixed to the body. Shape-induced transverse forces from a composite mote are similar.
- **Rotation.** A torque of only 0.1·F·a spins a 1 µm mote at ≈ 15 kHz, so Ω·τ_F ≈ 1.4. The thermal dipole then smears and rotates, giving a sideways force of order F/2. R8 cites 0.2–20 kHz spin in trapped particles [snippet].

**Fix.** Add a 30–50 % force margin (more heat), or model these terms explicitly in the sim.

### 8. Touch, occlusion and wakes destroy push-trap motes

*[RT4]*
- A tetrahedral mote that loses one head's beam can oppose only **33 %** of draft directions. A 0.1 m/s draft carries it out of the ≈ 5 µm usable beam in ≈ 50 µs.
- A hand plus forearm in a 0.5 m image shadows roughly 5–30 % of motes from at least one head.
- The obstruction interlock also cuts beams. Hand wakes (~1 m/s) exceed the 0.2 m/s margin.

"Touchable" therefore means a hand can pass safely while the image is locally destroyed and must be re-dispensed. There is no haptic feedback (pN forces). The GOAL grading must say so. Lateral2 (two heads) is less exposed.

### 9. 30 Hz persistence of vision with µs-long point flashes will flicker and phantom-array

**Evidence** *[RT4]*. At 60 Hz the atlas moves to push6 at 2.22 m/s: 1 158 motes, 6 948 channels (+54 %).

**Fix.** Make 60 Hz the default, or run a psychophysics check.

### 10. The validation suite cannot detect an over-predicted force

26/26 pass, but:
- **Tautological:** M09, M11 and M13 test the code's own formula.
- **Circular:** M17 and M18 compare against R6 estimates made from the same assumptions. M18 re-implements R6's path-length formula rather than calling `uc_absorptance`.
- **One-sided:**
  - M22's window (100–700 K) passes for almost any parameters.
  - M23 and M24 pass whenever the model predicts *more* force.
  - BYU's 18–24 mW hold power against the model's µW is "explained" as trap inefficiency and never tested.
- **Weak:** M26 multiplies the pump heat by 0, and its stated upper criterion is not evaluated.
- **Missing:**
  - the LG01 profile;
  - energy conservation of the wall-light model;
  - multi-beam AEL sums;
  - a band-limited beam in the feedback sim;
  - **any measured photophoretic force per absorbed watt at 1 atm.**

The central number (≈ 7×10⁻¹² N/K after slip at k_p = 0.02) is therefore unvalidated.

**Fix.** Add falsifiable tests. Commission the bench measurement of F/P_abs on a characterised sphere.

### 11. Hot-face quenching and the thermal ceiling apply to the mean temperature only

**What is wrong.** The lit face runs T₁ ≈ 0.76·ΔT_force above the mean for k_p = 0.02. For the largest single beam (1.22 F) that is ≈ 46 K. The phosphor quench uses the mean T.

**Evidence** *[RT4]*. At T_m + T₁ ≈ 488 K the coded quench gives q = 0.69, against 0.88 at 442 K. That is +27 % pump, i.e. 46 µW per beam, already over the 39 µW AEL.

**Fix.** Evaluate quenching and material limits at T_m + T₁.

---

## Minor

1. **The v2 wall-light model violates energy conservation.**
   - `(1−icp) + icp·q_diff + …` counts the diffracted lobe on top of the light that misses the mote. For a = 1 µm at 405 nm, wall_W = 1.08 × P_pump, more than the pump emits.
   - v1's P(1 − icp·A_abs) is the correct total, since all unabsorbed light lands somewhere.
   - Separately, `whitener_gain = 1` ignores optical-brightener fluorescence under 405 nm (gain ≈ 3–20 [memory]). The ratio becomes 0.03–0.2 against the 0.05 criterion. Rejecting scatter motes remains correct.
2. **1 µm motes are respirable.** They have d_ae ≈ 2.4 µm and settle at 0.2 mm/s. R7's "not respirable" analysis was for 20 µm motes. The mass is negligible (ng/h), but the inhalation toxicology of a nitride-phosphor/carbon/ITO composite is unknown. Update RESULTS §1.
3. **Phosphor numbers.**
   - A_abs: see C1.
   - IQE 0.9 for BaSi₂O₂N₂:Eu is at the top of the reported range. One snippet reports +14.7 % IQE from an additive, implying a lower baseline.
   - The thermal-quench parameters are uncalibrated.
4. **Focus spec.** M3 computes z_R without M² (pump 22 µm against 16.8 µm; trap 83 µm against 64 µm).
5. **Stored results contain non-physical values.** For example, `m1b_single_head.json` has pump = 1.5×10⁶¹ W and ΔT = 5 707 K from the 6 000 K bisection cap. Store NaN and a flag instead.
6. **RESULTS tally.** It says "0 ✗", but P15 carries a ✗ for lateral. After C2, P23 is ✗.
7. **Opposed heads blind each other's sensors.** In push6 and lateral2, each head receives the opposite head's full diverging trap power (about 0.3 W) through its aperture. Wavelength or polarisation separation is needed.
8. **`R_head` is the 1/e² radius.** Clear apertures must be about 1.3–1.5× larger (400–450 mm optics for "300 mm heads").
9. **Absorbing surfaces at a focus.** Black paper or cloth at a trap focus reaches ≈ +540 K in steady state (0.87 mW on 6.4 µm, k = 0.1). The interlock timing must be specified against the thermal time of ≈ 0.4 ms.
10. **Air margin.** u_air = 0.2 m/s is thin next to walking wakes, HVAC and thermal plumes (0.2–0.5 m/s [memory]). At 0.3 m/s the headline needs 1 414 motes and 5 655 channels *[RT4]*.
11. **Docstrings.** `dynamics.py` says η_trap = 0.3 is "calibrated on published data"; no calibration exists. The physics.py docstring points to the "derivation in 02_theory/T5", but T5 gives the result, not the derivation.

---

## What the corrections do to the headline (film density, 30 Hz, *[RT4]*)

| Case | Best design | Motes | Channels | 1550 nm | Status |
|---|---|---|---|---|---|
| As coded | push4, a = 1 µm | 1 131 | 4 524 | 1.8 W | pump at 93 % of AEL |
| + Tf fix only | push4 | 1 414 | 5 655 | 2.3 W | |
| + exact lateral2 only | lateral2, a = 1 µm (passive) | 1 767 | 3 534 | 9.7 W | |
| Ideal mote, corrected optics (Tf fix, lateral2 exact, A_abs 0.3, 0.5 µm jitter, dimple 2.5) | lateral2, a = 2.5 µm | 2 761 | 5 522 | 6.6 W | pump overlap still unchecked |
| Plausible-optimistic mote, same corrections | push6, a = 1 µm, 0.30 m/s | 4 314 | 25 885 | 10.6 W | needs a ≥ 50–100 kHz loop |
| k_p ≥ 0.5, or a dense mote | none (not even the 1 m accent) | – | – | – | infeasible |

The étendue tiling of Major 5 multiplies the hardware channel count further.

---

## Top 5 changes before any verdict

1. **Make the mote physically consistent (C1, Majors 3 and 11).**
   - J₁(α, a) from Mie internal fields.
   - k_eff from a core–shell model.
   - Pump absorptance from the emitter volume.
   - A UC mote cannot have k_p = 0.02.

   Report the atlas as a band over mote materials. Put a measured force per absorbed watt and a measured k_eff on a real composite mote first on the bench list.
2. **Redo the feedback with a band-limited beam at the design NA and a heat-capped force (C2).**
   - Quote the loop rate from ≥ 10⁴ mote-seconds.
   - Rescore P23.
   - Promote the exact-model lateral2 (passive) as the lead architecture.
3. **Rebuild `safety.py` around accessible emission, not per-beam power (C3).**
   - Sum all beams at worst-case points for real stroke geometries.
   - Derate pump intercept for jitter and turbulence.
   - Add a single-fault analysis with required shutdown times.

   Until then, write "Class 1 in normal operation at 1550 nm; not established at 405 nm or for the product".
4. **Fix the model errors.**
   - The Tf/T₀ factor (Major 1).
   - The LG01 power and nonlinearity (Major 2).
   - C_ph ∈ [0.67, 1.04] (Major 4).
   - Wall-light energy conservation (Minor 1).
   - Drop `single` or give it an upstream η ≤ NA (Major 6).
   - Add the force margins of Major 7.
5. **Replace "channels = N × heads" with an étendue-limited channel and tile count (Major 5).** State the touch and occlusion behaviour honestly (Major 8), and use 60 Hz as the default refresh (Major 9).

---

## Overall judgement

The lab's claim is: **"physics and Class 1 safety allow film-density open-air images; the binding problem is steering-engine engineering."** **It is overstated.** It is not proven wrong, but it is not supported as written.

**What survives:**
- No physical law is violated.
- 1550 nm trap beams are Class 1 in normal operation.
- Brownian motion, gravity, radiation pressure and mote–mote interactions are negligible.
- With an *ideal* mote the film-density budget closes on paper at about 1.4–2.8 thousand motes and 3.5–5.7 thousand steering channels after the model fixes.

**What does not survive:**
1. **"Physics allows" rests on a mote nobody has made.** Its figure of merit (J₁/A)/(k_p + 2k_g) must be 3–15× better than any plausible composite.
   - At plausible-optimistic values: about 4 300 motes, 26 000 channels and 11 W.
   - For a dense mote: nothing is feasible, not even a 1 m accent.

   The binding unknown is materials physics and an unmeasured force law, before any steering engineering.
2. **"Class 1" is not demonstrated.**
   - The 405 nm pump sits at 93 % of its AEL per beam.
   - Overlapping pump beams reach up to 3.4× the AEL.
   - Realistic pointing fails it by itself.
   - The product's embedded sources are Class 3B under single faults, with no shutdown design.
3. **The push-trap control spec is optimistic by 3–5×.** It needs 50–100 kHz, not 15–20, once the beam obeys diffraction. Touch and occlusion destroy push-trap motes.
4. **The steering problem is étendue-limited.** It needs about 10¹⁰ addressable spots per head or per-frame tile hand-over, not just "thousands of existing devices integrated".

A defensible one-line verdict today: *"If a µm mote with (J₁/A)/(k_p+2k_g) ≳ 3 m·K/W and ≥ 0.3 pump absorptance can be made, and its photophoretic force per watt is measured to match theory within ~×1.5, a passive two-head doughnut (lateral2) design could draw film-density strokes with ~2–6 thousand channels under Class 1 at 1550 nm. The pump's Class 1, the fault-safety architecture and an étendue-limited steering engine remain open. None of these has been shown on a bench."*

The route stays worth a bench. It is not yet a physics-level "yes".

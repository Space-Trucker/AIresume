# Idea round 2: independent theorist report (Opus)

*Written 2026-10-01. I read `IDEA_ROUND_2_BRIEF.md`, `T6_unlock_theory.md`, `m15_lightcurtain_static.py`, `00_mission/GOAL.md`, `05_reviews/FINAL_VERDICT.md` and the 1550/500 nm rows of `01_research/R3_safety_limits.md`. I edited no other file.*

*New numbers come from a scratch script that imports M15 read-only and changes only the jitter model and the mote list. The recipe is in Appendix A. I used 23 web searches; several standards and publisher sites are blocked by the egress proxy, so some standards wording comes from secondary sources and is flagged.*

**Tags**
- **[MEASURED+src]**: a measured or documented fact with its source. For standards, this means wording seen in a secondary source this session.
- **[THEORY]**: derived here.
- **[ESTIMATE]**: an order-of-magnitude judgement.
- **[SPECULATIVE]**: an untested idea.
- **"recalled"**: from memory, not re-verified this session.

---

## 0. Summary

1. **The cubic draft law P ∝ N·u³/f² comes from the jitter model, not from physics.** [THEORY]
   - M15b sets mote jitter to u/(2π·f_bw), which treats the whole air speed u (0.3 m/s) as unpredictable. With a proportional-only loop, the mean flow actually gives a *constant offset*, not jitter. With integral action (a PI loop), the mean flow is cancelled exactly.
   - What remains is set by the *Eulerian acceleration* of room air, about 0.1–2 m/s². Room air at a fixed point carries almost no velocity above the Kolmogorov frequency U/(2πη_K) ≈ 10–60 Hz.
   - PI pinning error = a_E/(2π f_bw)² ≈ **0.04–1.3 µm at 200 Hz** in rooms, and ≈ 0.4 µm at 1 kHz in a fast hand's wake. The M15b model gives **240 µm at 200 Hz and 24 µm at 2 kHz**.
   - So the spot radius r_c is set by 3a, beam wander (1–4 µm) and sensing, **not by u/f**.
   - Power then scales **linearly** with u at fixed r_c. Under Class 1 per focus, *pixels* scale linearly with u instead.
2. **With pinning, normal rooms (0.3 m/s) become feasible within the 100 W IR cap** for an ITO-class mote, using the same M15d machinery (H14, δ = 3 mm). [THEORY/MODEL]
   - Sketch: 95 W, 1.6×10⁹ px, about $77k at volume.
   - Film density: 93 W, 9.6×10⁹ px, about $0.32M at volume.
   - M15d had these at 163 W (fail) and ~1 kW (fail).
   - Carbon-aerogel motes still fail on **heat** in normal rooms. The heat bound, not power, is where u really bites.
3. **Class 1 per focus is reachable without any light curtain**, even at 0.3 m/s. [THEORY/MODEL]
   - At r_c = 14–16 µm, a pinned mote needs P_focus ≈ 4.7–5 mW (2 foci per 3.5 mm aperture ≤ 10 mW).
   - Total 1550 nm is **8 W for a sketch and 46–50 W for film density**.
   - The price is **pixels**: 2.3×10¹⁰ in total for full-field holograms (H14). That is about $0.73M at volume prices and $26M at lab prices.
   - **The curtain's real value is a 10–20× pixel saving, not feasibility.**
4. **Corrected dose numbers.** The 1550 nm cut dose is not binding. [MEASURED via R3 L7/K1 + THEORY]
   - For exposures under 0.35 s the corneal limit is 10⁴ J/m² over a **1 mm** aperture, i.e. **7.85 mJ**. The brief's "9.6 mJ in 3.5 mm" and the M15 code (10³ J/m² × 3.5 mm) use the wrong value and aperture; by coincidence they give a similar number.
   - The allowed cut time is **157 ms at 50 mW and 39 ms at 200 mW**. A standard IEC 61496 Type 4 response (6–13 ms) is enough, so the "≤ 1.4 ms" requirement can be relaxed 10–100×.
   - LCSV's visible illumination spots (~0.01–0.2 mW) are already Class 1 and need no curtain.
5. **Standards verdict on "every beam is its own light curtain".**
   - It is physically sound and dose-compliant.
   - As the *basis* for a consumer Class 1 classification it has **no direct precedent**. The closest are:
     - Wi-Charge: UL and Class 1 certified, but with *intrinsic* resonator physics, not electronics;
     - IEC 60825-1 Class 1C: sensor-based eye protection, but only for skin-contact products under a vertical standard;
     - IEC 62471-5: detection systems accepted as *installation* controls for professional RG3 projectors;
     - IEC 60825-2: automatic power reduction (APR) for fibre systems.
   - EN 50689 adds "exposure ≤ MPE at any position" for child-appealing consumer products.
   - P(accepted as primary safeguard for a consumer Class 1 product) ≈ **0.2–0.3** [ESTIMATE].
   - The curtain's undetected failure modes are **sub-threshold intercepts summed over many beams** (concave or refractive objects near a multi-watt head) and self-shadow versus threshold. Neither is covered by M15's checks.
6. **No new physics route was found (2015–2026).**
   - Paul traps, upconversion self-lighting, soot motes, time multiplexing, line foci, standing-wave light recycling and particle streams each die on a stated number (§6).
   - The needle stays in MOTE/LCSV. The binding items have shifted from power and safety to **(i) the mote FOM (heat), (ii) per-mote µm sensing at ≥ 0.2–1 kHz, and (iii) hologram pixel count and compute.**

---

## 1. Re-derivation of B2–B7 and the invariants: which assumptions are fundamental?

### 1.1 B2, holding intensity

The lab's force law (`physics.py`) is

  F = C·(9π/2)·μ²·a·I·J₁ / (ρT·(k_p+2k_g)).

Define the dipole temperature scale T₁ ≡ I·a·J₁/(k_p+2k_g). Then

  **F = C·(9π/2)·μν·T₁/T** (ν = μ/ρ, the kinematic viscosity) [THEORY]

and, against Stokes drag 6πμaw/Cc,

  **F/drag = (3C/4)·(ν/(a·w))·(T₁/T)·Cc, so the required T₁ = (4/3)·T·a·w/(ν·C·Cc).**

At a = 5 µm and w = 0.3 m/s this gives T₁ ≈ 46 K; at a = 2.5 µm, 23 K. [THEORY]

The mean temperature rise is ΔT_mean = A·I·a/(4k_g). Its ratio to the dipole term is **T₁/ΔT_mean = 4k_g·FOM** (≈ 0.5 at FOM 5). Inserting T₁ recovers B2 exactly: I_hold = 4ρT·h·w/(3η·C·μ·FOM·A·Cc). [THEORY; matches the M15 self-test]

Which assumptions in B2 are fundamental?

| Assumption | Fundamental? | Comment |
|---|---|---|
| Continuum ΔT force (Kn ≪ 1) | Yes at 1 atm for a ≳ 0.3 µm | In the transition regime the force slip (~1/5 at a = 0.1 µm) loses more than the Cunningham factor (2.9) gains. No gain from going smaller [THEORY] |
| w = full air speed u | Yes for static voxels | Momentum relaxation time τ_p = 2ρ_p a²/(9μ) ≈ 3 µs (5 µm, 100 kg/m³). The mote has no inertia to ride out gusts [THEORY] |
| C_ph ≈ 0.85 | Nearly | Maxwell's thermal-creep ceiling is ~1.17, so at most +35 % [ESTIMATE] |
| h, η geometry | Nearly | H14 already has h_mean 1.28 |
| Only beam-direction (ΔT) force | **No** | The Δα (accommodation) force is body-fixed and scales with ΔT_mean, not T₁. For poor-FOM motes it could matter. It needs orientation sensing and control: rotational diffusion time is ~14 s at 5 µm and ~2 s at 2.5 µm [SPECULATIVE] |

**Verdict.** B2 is essentially fundamental. The only levers are FOM·A and u.

### 1.2 B3, heat: A cancels, and size is the lever

Substituting I_hold into ΔT = A·a·I/(4k_g) gives

  **ΔT = ρT·h·w·a / (3η·C·μ·FOM·Cc·k_g)**, which is independent of A. [THEORY]

The maximum holdable air speed at ΔT ≤ 300 K, h = 2.14 (from the scratch script):

| FOM | a = 1 µm | 2.5 µm | 5 µm | 10 µm |
|---|---|---|---|---|
| 1.6 (5 µm carbon, white) | 0.83 m/s | 0.32 | 0.16 | 0.08 |
| 2.5 (10 µm carbon, white) | 1.29 | 0.49 | 0.24 | 0.12 |
| 4.0 | 2.07 | 0.79 | 0.39 | 0.19 |
| 5.3 (ITO-aerogel) | 2.74 | **1.05** | 0.51 | 0.26 |

**This is the true draft bound.** Normal rooms and hand wakes (~1 m/s locally) need FOM ≳ 4 *and* a ≲ 2.5 µm.
- The cost of small motes is visible scattering cross-section (∝ a²) and respirability (R3/R8).
- The bound is not fundamental in a: it is a *design choice* the M15 runs did not explore below 5 µm.

### 1.3 B4–B6 and the cubic law: the non-fundamental step

T6 chains three steps:
- r_c ≥ k·u/f (B6);
- P_focus = h·I_hold·πr_c² (B4);
- I_hold ∝ u (B2),

which gives P ∝ N·u³/f². The first step assumes the mote's velocity error is the whole air speed, unpredictable at every update. M15b encodes this as jitter = u/(2π·f_bw).

**Room air at a fixed point is a band-limited, smooth signal.**
- With mean speed U, fluctuation u′ and dissipation ε, the smallest eddies have size η_K = (ν³/ε)^¼ ≈ 0.8–2.4 mm. They are swept past at frequency ≲ U/(2πη_K) ≈ 7–60 Hz; above that the spectrum falls off exponentially.
- The disturbance a pinning loop sees is therefore a slowly varying velocity with Eulerian acceleration a_E ≈ U·u′/λ_T, where λ_T is the Taylor microscale.

The mote is an overdamped plant: ẋ = u_air + F/γ. A PI loop on position cancels any constant u (the integral term supplies the mean drag). Its error to an acceleration is **x_err = a_E/ω_n²**. [THEORY, standard control]

Pinning error by loop type (scratch script; ε values are [ESTIMATE] for indoor air, consistent with the fully developed spectra Hanzawa et al. 1987 measured in 20 ventilated spaces [MEASURED+src: DTU Orbit]):

| Case (U, u′, ε) | η_K | a_E | Type-1 jitter u/(2πf) at 200 Hz / 2 kHz | **PI error at 200 Hz / 1 kHz** |
|---|---|---|---|---|
| Quiet (0.1, 0.04, 10⁻⁴) | 2.4 mm | 0.07 m/s² | 80 µm / 8 µm | **0.04 / 0.002 µm** |
| Normal (0.3, 0.1, 10⁻³) | 1.4 mm | 0.64 m/s² | 240 µm / 24 µm | **0.4 / 0.016 µm** |
| Busy (0.3, 0.15, 10⁻²) | 0.8 mm | 2.1 m/s² | 240 µm / 24 µm | **1.3 / 0.05 µm** |
| Fast hand wake (1.0, 0.5, 5×10⁻²) | 0.5 mm | 15 m/s² | 800 µm / 80 µm | **9.5 / 0.4 µm** |

Turbulent accelerations are intermittent: peaks reach 5–10× the rms [ESTIMATE]. Even so, a ~1 kHz PI loop holds the mote to ≲ 4 µm in a hand wake, and a 200 Hz loop does so in a normal room.

Other contributions to the error budget:
- **Beam wander** from indoor refractive turbulence (dn/dT = −0.93×10⁻⁶/K): 0.4–1.2 µm over 1.5 m in room air; ~3.6 µm when crossing a 3 K hand plume [THEORY/ESTIMATE].
- **Sensing noise** is unknown (see the risks below).

I take **σ_total ≈ 4 µm**, so r_c ≥ max(3σ, 3a) ≈ 12–15 µm.

**Corrected bound B6′: f_bw ≥ (1/2π)·√(a_E,peak/x_tol)** ≈ 60–110 Hz for room air and 300–600 Hz for hand wakes (x_tol = 4 µm). This replaces "f ≥ u/r_c ≈ 10–50 kHz". [THEORY]

**Practical caveat** [ESTIMATE]:
- A hologram-only loop (PLM at 1.44 kHz frames, ~1 ms latency) reaches f_c ≈ 80 Hz. That is enough for quiet or normal air (2.5 µm at ε = 10⁻³) but not for busy air (8 µm) or hand wakes.
- T6's I4 fast amplitude plane is therefore still needed. It must be **analog**: spatial dithering of the several DMD pixels inside each spot's footprint, not temporal PWM.
- With 50 µs binary frames, each "off" frame lets the mote drift u·50 µs = 15 µm.

**Remaining risks**
- **Sensing:** per-mote position to ~2–4 µm at ≥ 1 kHz for 10³–10⁴ motes.
  - Photon budget for camera centroiding of the visible scatter: ~2.6×10⁴ photons/ms → ~6 µm per mm-pixel, which is marginal.
  - Better: per-spot transmitted-power read-out at the receiver's image plane (an InGaAs camera superpixel per spot, as the curtain needs anyway) plus a known intensity gradient or spot dither. [SPECULATIVE]
- **Actuator:** forces are positive-only along 6–14 directions. Allocation is fine with H14.
- **Rotation and Δα bias:** slow, so the integral term absorbs it.

### 1.4 The P·M invariant: what survives

P_total·M = N·h·I_hold·A_f/(η_shape·η_holo) is an étendue / space-bandwidth statement. It is **fundamental for "any spot anywhere in A_f" from one hologram per head**.

With pinning it is **linear in u** (through I_hold), not cubic. Under Class 1 per focus, P_focus is fixed by the AEL, so **M ∝ I_hold ∝ u** and P_total is nearly fixed. That is why normal rooms double the pixel count rather than multiplying power by 27.

Loopholes I tried:

| Attempt | Result (number that decides) |
|---|---|
| Time-multiplexing spots | Dead. Drift during off-time u·t_off must be < r_c, so t_off < 50 µs at 0.3 m/s and r_c = 15 µm. Phase-SLM frames are ≥ 0.7 ms [THEORY] |
| Line foci along strokes instead of dots | Dead. Power ratio = 2δ/(π r_c) = **127× more** (δ = 3 mm, r_c = 15 µm) [THEORY] |
| Broad "zone" beams carry the mean draft force | Dead. Lit area per mote ~1 cm² against πr_c² → ~10⁴–10⁵× more power [THEORY] |
| Standing-wave recycling (receiver re-images the light back) | Dead for pushes: illumination from both sides cancels J₁. A ring geometry or re-routing to other motes gains ≤ 1/(1−R·η_holo) ≈ 2× at η_holo 0.6 [THEORY/ESTIMATE]. The Cal Poly 2025 thesis on beam-reflection trapping shows reflections are used, but for trap stability, not recycling [MEASURED+src: Cal Poly thesis 2947, title only] |
| Fixed DOE lattice + amplitude mask | Dead. With uniform illumination the efficiency is N/M ≈ 10⁻⁵. It needs light steering (= the hologram again) [THEORY] |
| **Tiled, steerable sub-holograms** (small SLM per tile, steered by an FSM/MEMS mirror to where strokes are) | **Partial.** Pixels ≈ S_proj·s/(πr_c²) instead of A_f/(πr_c²). For a 5 m sketch with s = 2 cm tiles: **~10× fewer pixels**, but ~250 tiles per head. For film density (30 m of strokes in 1 m²): only ~1.7×. Also cuts hologram compute from ~10¹⁵ to ~10¹³–10¹⁴ flop/s (per-tile problems) [ESTIMATE] |

### 1.5 B7, light budget

Φ = 4π·S·w_res·L is bookkeeping and is fundamental.

T6's I3 (terminated side-scatter illumination) is sound. Per-spot visible powers come out at ~10–200 µW, below the 500 nm Class 1 AEL of 0.39 mW (lab's `sf.ael_class1`). **The visible beams need no curtain**; only wall stray light from receiver leakage matters. [MODEL]

### 1.6 Issues found in M15 (for the main session; I did not edit the file)

1. **`trap_cut_dose` uses 10³ J/m² × a 3.5 mm aperture (9.6 mJ).**
   - The correct value for t < 0.35 s at 1500–1800 nm is 10⁴ J/m² over a 1 mm aperture = **7.85 mJ**. This is consistent with R3 rows L7 and K1 (Class 1 AEL 8 mJ for 10⁻⁹–0.35 s).
   - It is numerically similar and non-binding, so no result changes. The comment is wrong.
2. **The jitter model u/(2π·f_bw)** (`design2`): see §1.3. It is the dominant source of pessimism in normal rooms.
3. **Exit-window check only.** The summed sub-threshold intercept of many beams (§7.4, F2/F3) and the Condition 1 optical-aid case (§7.4, F8) are not checked.
4. **Line-of-sight focus stacking.** Strokes parallel to a head's axis put ~10–15 cones inside one 3.5 mm aperture. This matters for the no-curtain design (§2.3) and is not modelled.

---

## 2. Draft immunity in a normal room: numbers

### 2.1 Same machinery as M15d, with only the jitter changed (σ = 4 µm)

Settings: ≤ 100 W IR, H14, δ = 3 mm, curtain safety, cost-optimised. [MODEL, scratch `r2_cap.py`]

| Content / room | Mote | M15d (2 kHz type-1 jitter) | **Pinned (σ = 4 µm)** |
|---|---|---|---|
| Sketch, normal | ITO-aerogel 5 µm | 163 W, fails cap | **95 W, r_c 55 µm, 1.6×10⁹ px, $77k vol / $2.0M lab; holds with one head blocked** |
| Sketch, normal | ITO-aerogel 2.5 µm | 175 W, fails cap and visible checks | **81 W, 2.3×10⁹ px, $99k / $2.8M; ΔT 114 K** |
| Film density, calm | ITO-aerogel 5 µm | 124 W, fails cap | **93 W, 5.1×10⁹ px, $182k / $5.9M** |
| Film density, normal | ITO-aerogel 5 µm | 979 W, fails | **93 W, r_c 22 µm, 9.6×10⁹ px, $317k / $10.8M** |
| Any, normal | Carbon-aerogel (white) 5–10 µm | Fails on heat | **Still fails on heat** (ΔT 475–534 K) |

### 2.2 Local events in a normal room

| Event | Local air | Holdable? | Note |
|---|---|---|---|
| Hand plume (still hand) | 0.1–0.25 m/s, δT 1–3 K | Yes | Beam wander ≤ 4 µm [THEORY] |
| Hand moving at 1 m/s, within ~1–2 hand-widths and in its wake | up to ~0.5–1 m/s, a ~ 15–25 m/s² | Only with FOM ≳ 4 and a ≲ 2.5 µm (u_max 0.8–1.05 m/s) and a ~1 kHz analog loop | Needs ~3.3× I_hold, which exceeds Class 1 per focus by ~1.6× transiently. **Expect a local dropout zone ~5–10 cm around fast hands** unless the curtain is used there [ESTIMATE] |
| Talking or breathing toward the image | Jet ~1 m/s at the mouth, ~0.1–0.2 m/s at 0.5–1 m | Yes beyond ~0.5 m | [ESTIMATE] |
| Walking past at 1 m/s, 0.5 m away | Wake ~0.1–0.3 m/s | Yes | [ESTIMATE] |

### 2.3 Class 1 per focus, no curtain

Largest r_c with 2·P_focus ≤ 10 mW (two foci per 3.5 mm aperture at δ = 3 mm); H14; σ = 4 µm. [MODEL, scratch `r2_numbers.py` §7]

| Content / room | Mote | r_c | P_focus | **1550 nm total** | ΔT | Pixels (14 heads) | Cost vol / lab |
|---|---|---|---|---|---|---|---|
| Sketch, quiet | ITO-aerogel 5 µm | 27 µm | 4.6 mW | **7.7 W** | 74 K | 1.1×10¹⁰ | $0.37M / $12.6M |
| Sketch, **normal** | ITO-aerogel 2.5 µm | 16 µm | 5.0 mW | **8.3 W** | 114 K | 2.3×10¹⁰ | $0.73M / $26M |
| Film density, **normal** | ITO-aerogel 5 µm | 16 µm | 4.7 mW | **46 W** | 190 K | 2.3×10¹⁰ | $0.73M / $26M |
| Any | Carbon-aerogel 10 µm | — | — | No r_c works | — | — | — |

**Reading** [THEORY]
- Power is trivial; **pixels are the whole cost.**
- With 2 cm steerable tiles, a sketch drops to ~2–3×10⁹ px, which matches the curtain design's pixel count.
- The safety case changes from "detect people" to "never emit a frame whose summed field exceeds the AEL anywhere, and catch faults". That is a proactive *field checker* plus a fault monitor, close to a LiDAR scanning safeguard (§7.2).
- The FINAL_VERDICT's "certified scheduler" requirement survives as this field checker: line-of-sight stacking of up to ~10–15 cones (§1.6 item 4) must be scheduled away.

---

## 3. Materials: FOM from measured or bulk data (short)

**Soot / carbon nanocluster motes: killed by measurement.**
- Soot aggregates (a_eq = 2.9 µm) move at 160 µm/s in 3 W/cm² [MEASURED+src: ResearchGate 287037864].
- Inverting B2: **C·FOM·A ≈ 0.13 m·K/W**, about 30× below the ~4 needed. Fractal aggregates of nm spheres heat almost uniformly, so J₁ → 0. [THEORY]
- Shvedov et al. guided carbon nanoclusters at ~1 cm/s in open air [MEASURED+src: PubMed 19333344]; at the implied 10⁶–10⁷ W/m², that is also C·FOM·A ≪ 1 [ESTIMATE].

**Hollow-shell geometry: k_eff from bulk numbers.** [THEORY + bulk k]
- For a thin wall (thickness t, conductivity k_s) around gas (k_in), the l = 1 conduction matching gives k_eff ≈ k_in + 2k_s·t/a.
- With silica k_s ≈ 1 W/m/K:

| Shell | k_eff (W/m/K) | FOM |
|---|---|---|
| a = 5 µm, t = 100 nm, CO₂ fill | 0.056 | 4.2 |
| a = 5 µm, t = 50 nm, CO₂ fill | 0.036 | 5.1 |
| a = 2.5 µm, t = 50 nm, CO₂ fill | 0.056 | 4.2 |

- These assume J₁/A = 0.45, i.e. a front skin absorbing ≥ 90 % in one pass. If the skin is weaker, light reaches the back wall: J₁/A ≈ 0.30 → FOM 2.6.
- So the hollow shell removes the *k_eff measurement* uncertainty (no µm-scale aerogel k), **but not the island-skin problem.** That is the same open item as the ITO-aerogel mote.
- Discontinuous NIR absorbers worth screening for islands [SPECULATIVE]: Cu₂₋ₓS / Cu₂₋ₓSe nanocrystals, whose plasmon resonance is tunable to ~1.1–1.6 µm (recalled).

**Smaller is better for drafts.**
- a = 2–2.5 µm halves ΔT and doubles u_max (table in §1.2).
- Cost: 4× more visible power per mote, still ~1 W in total, and the motes are fully respirable. The R3/R8 toxicology issue remains open.

**Black motes are fine under I3.** Terminated illumination removes the visible-transparency requirement. The remaining conflict is side-scatter albedo (q ≈ 0.05 for black, ~0.3 with a white shell).

---

## 4. Light generation (short)

**Terminated side-scatter (I3)** works. Visible spots are ≲ 0.2 mW each, so Class 1 per spot [MODEL].

**Upconversion of the trap light itself (Er³⁺, 1550 → green/red): killed.** [ESTIMATE]
- Er³⁺ absorption in β-NaYF₄:25%Er: σ ≈ 5×10⁻²¹ cm², α ≈ 17 cm⁻¹, so about 1 % is absorbed across a 5 µm mote.
- Visible UC quantum yield ~1–3%.
- Result: ~20 µlm per mote at I_hold(0.3 m/s), against 66–110 µlm needed. A pure NaYF₄ mote is 3–5× short and has near-zero photophoretic FOM (k ~ 1–5). A 10 % dilution in aerogel is 30–50× short.
- Green quenches at ΔT 100–200 K, and there is no cyan.

**Self-luminous chiplet motes** (photovoltaic + µLED): killed for holding. The electrical side would be easy (~5 µW per mote), but silicon's k ≈ 150 W/m/K gives FOM ≈ 0, so there is no photophoretic force. [THEORY]

---

## 5. Steering and holography, 2026 (short)

**Precedents for many holographic spots**
- Caltech, *Nature* 2025: 12,000 tweezer sites from **two SLMs** at 1055/1061 nm [MEASURED+src: Nature s41586-025-09641-4]. The field is mm-scale, so its space-bandwidth product is ~10⁵, far from 10⁹.
- Samara group: SLM-generated photophoretic trap arrays in air (20×20) [MEASURED+src: CEUR-WS Vol-1638 Paper15].
- BYU (Smalley et al.) is scaling OTDs with diffractive optics [MEASURED+src: SPIE 12445 2023; RSI 92, 103002 2021].
- A December 2025 review of photophoretic trapping exists (arXiv 2512.09401); only the abstract listing was seen.

**Pixel economics** [ESTIMATE]
- Devices: ~10⁶–10⁷ px per phase SLM at 60–1440 Hz, so 10⁹–10¹⁰ px means 10²–10³ devices.
- Full-field compute: ~3×10¹² flop per head-frame (weighted Gerchberg–Saxton (GS) at 10⁹ px) gives ~10¹⁵ flop/s for 14 heads at 30 Hz.
- Static content needs no recomputation; amplitude goes to the fast plane.
- Per-tile holograms cut compute to ~10¹³–10¹⁴ flop/s.

---

## 6. Entirely different routes (literature 2015–2026), each with the number that decides it

| Route | Source | Fate |
|---|---|---|
| fs plasma voxels ("Fairy Lights") | Ochiai 2016 (recalled; ResearchGate 279068554) | Already ruled out: plasma (noise, O₃, UV) |
| Acoustic trap displays (MATD, GS-PAT, OpenMPD) | Hirayama 2019 (in brief) | Already ruled out: ≥ 100 dB in the beam cones |
| Planar Paul trap, electrically scanned gold particle | Berthelot & Bonod, *Opt. Lett.* 44, 1476 (2019) [MEASURED+src] | **Killed at room scale.** A 5 µm mote at its surface-field charge limit (8×10⁻¹⁵ C) needs **E ≈ 6×10⁴ V/m** to resist 0.3 m/s, against ICNIRP's public reference of 83 V/m at 3 kHz–10 MHz (recalled) and DC perception/sparking at ~10–20 kV/m [THEORY/ESTIMATE] |
| Swept elastic diffuser, touchable | UPNA, CHI 2025 [MEASURED+src: Hackaday 2025-04-14] | Moving screen (R1/R3). Desk scale. Good for touch UX studies |
| Laminar "invisible particulate streams" + laser (VAST) | Blaise Photonics 2025 press release [MEASURED+src: natlawreview] | R3: added media, plus particle exposure. Shows market appetite; R3 kills it as specified |
| Real-image / light-field rooms (AIRR, holographic walls) | (recalled) | R5 or R1 kill. A true holographic wall needs ~(3 m / 0.5 µm)² ≈ 4×10¹³ px per wall [THEORY] |
| Micro-drones as voxels | (recalled) | Rotor noise and size; kill at 10³+ voxels [ESTIMATE] |
| Er upconversion / self-luminous chiplets | §4 | Kill |

**No missed route beats light-held motes.** The needle is inside LCSV.

---

## 7. Standards-level analysis of "every beam is its own light curtain"

### 7.1 What the classification framework says

- **Class 1** is "safe under reasonably foreseeable conditions of operation… either inherently or by virtue of their engineering design." [MEASURED+src: Lasermet overview; IEC 60825-1:2014]
- Classification uses the **highest accessible emission under reasonably foreseeable single-fault conditions**. Whether a fault is "reasonably foreseeable" is a probabilistic, risk-analysis judgement. Risk analysis also decides "whether additional functional safety (automated power reduction for case of fault) is needed" and "whether automated power reduction is permitted to not be fast enough to assure the AEL is not exceeded"; IEC 61508 can be applied. [MEASURED+src: Schulmeister, ILSC 2013, abstract/snippets; full text blocked]
- **Embedded lasers**: a Class 1 product may contain Class 3B/4 lasers when protective housings and interlocks prevent human access. [MEASURED+src: Lasermet]
- **Scanned emission**: products classified on scanned emission "shall not, as a result of scan failure… permit human access to laser radiation in excess of the AEL". In other words, **a monitoring safeguard may carry the classification under fault conditions.** [MEASURED+src: secondary quote of IEC 60825-1 scanning-safeguard clause, allpcb.com]
- **Class 1C** (new in IEC 60825-1:2014, recalled): products for *contact application to skin*. Engineering means such as contact sensors prevent ocular exposure although the raw emission can exceed Class 3R/3B. It is defined only together with a vertical standard. **This is the one place the base standard credits sensing-based eye protection, and it is restricted to contact devices.**
- **The edition is still 3.0 (2014).** I found no published Edition 4 [MEASURED+src: IEC webstore listing]. IEC 60825-4 Ed. 3 (2022), with EN publication in 2024/2025, is current for laser guards.
- **The consumer layer in Europe** is EN 50689:2021. Child-appealing laser products must be Class 1 *and* "the laser radiation level at any position" must not exceed Table A.5 of EN 60825-1 [MEASURED+src: JJR Lab summary]. A hologram projector could be judged child-appealing.
  - On a strict reading, the instantaneous irradiance at a 50 mW, 30 µm focus (~1.8×10⁷ W/m²) exceeds the MPE "at a position" until the cut acts.
  - The design is defensible only if the assessor accepts exposure-duration-limited MPEs, i.e. those for t_cut.
- **AV equipment route** (recalled): IEC 62368-1 refers lasers to IEC 60825-1 and treats interlocks as safeguards. Safety software would likely be judged to IEC 60730-1 Annex H class C or IEC 61508.

### 7.2 Precedents

| Precedent | Mechanism | Status | Relevance |
|---|---|---|---|
| **Wi-Charge** (W-level IR power beaming) | Distributed resonator: an object in the beam stops lasing "at the speed of light", with no electronics | **UL and Class 1 certified** (LIGHTS-3W) [MEASURED+src: Wikipedia, Laser Focus World]. A 2025 safety analysis of a distributed coupled-cavity laser (DCCL) limits eye-safe output to ~150 mW and treats partial obstruction as the hard case [MEASURED+src: arXiv 2507.21891 snippet] | Closest consumer precedent, but the cut is *intrinsic physics*. LCSV's open, non-resonant beams would rely on electronics |
| **IEC 60825-2 APR** (fibre systems) | Automatic power reduction after a fibre break | The hazard level is set by "normal power and the speed of APR"; shutdown within ≤ 1 s, preferred ~160 ms (ITU-T G.664) [MEASURED+src: Lightwave] | Proves a *timed engineered shutdown* can set a hazard level, but in restricted/controlled locations, not for consumers |
| **IEC 62471-5 RG3 projectors** | "Installation method, separation height, barriers, **detection systems** or other control measures shall prevent hazardous eye access within the hazard distance" [MEASURED+src: Epson HD notice] | Professional installations | Detection is accepted as an **installation control**, *not* as a way to lower the risk group |
| **PowerLight** (laser power beaming) | "Virtual enclosure" safety ring; shut-off "within milliseconds"; LOPA-based safety architecture [MEASURED+src: GeekWire 2021; SPIE 13359] | Class 4 industrial/outdoor | Functional-safety design pattern, not a consumer Class 1 |
| **Microvision "virtual protective housing"** | Class 1 short-range probe pulses; higher-energy pulses only if no near object is detected [MEASURED+src: patent US12019188 via verdict.co.uk] | Patent (design concept) | Template for *restart logic*: re-arm only after a Class 1 probe confirms the path is clear |
| **IEC 60825-4 active guards** | A guard element issues a termination signal on excess exposure. "A reasonably foreseeable fault within the active guard system shall not lead to the loss of the safety function"; faults must be detected "at or before the next demand" [MEASURED+src: iTeh IEC 60825-4 preview/catalogue] | Machinery guards (with ISO 11553) | The brief's precedent is **mis-cited**: active guards detect *laser hits on a guard*, not humans. They do give the functional-safety template |
| **IEC 61496 Type 4 light curtains** | Self-checking, two-channel ESPE | Response **6–13 ms**, 14 mm resolution, PL e / SIL 3 [MEASURED+src: Schneider XUSL4E14F061N 9 ms; Datasensing SLIM 7 ms; SICK deTec4 13 ms] | Response time is adequate for 1550 nm (§7.3). Detection capability (14 mm) is far coarser than per-beam monitoring; a per-beam scheme has no type-tested equivalent |

**Can an interlock-dependent product be Class 1?**
- **Yes, if the interlock guards against faults or service access**: embedded lasers, scanning safeguards, APR-like fault cuts.
- **Unprecedented, if the interlock must act on every normal-use access to open-air hazardous emission.** Only Class 1C (skin contact, vertical standard) and Wi-Charge (intrinsic resonator) come close.
- A test house could literally measure only P·t_cut (its detector trips the beam). It would then also be expected to test **non-tripping geometries** (§7.4, F1/F2), and to apply EN 50689 if the product is consumer and child-appealing.
- **P(accepted as the primary basis of a consumer Class 1 classification) ≈ 0.2–0.3** [ESTIMATE].
- P(accepted as an installation control for a professional or venue product, like RG3 projectors) ≈ 0.6 [ESTIMATE].
- The realistic consumer path is a **new vertical standard**, the way 1C was created. That is a multi-year effort.

### 7.3 MPE dose during a cut [MEASURED via R3 + THEORY]

**1550 nm, cornea**
- Limits: H = 10⁴ J/m² for 1 ns–10 s (R3 L7, ICNIRP 2013 Table 5). The limiting aperture is 1 mm for t < 0.35 s, consistent with the Class 1 AEL of 8 mJ in R3 K1. So the limit is **7.85 mJ** through 1 mm.
- Dose for a 1.4 ms cut:
  - 50 mW → 70 µJ (0.9 % of the limit);
  - 200 mW → 280 µJ (3.6 %).
- **Allowed t_cut:** 785 ms at 10 mW, 157 ms at 50 mW, 39 ms at 200 mW, 16 ms at 500 mW. A Type 4 curtain's 6–13 ms is sufficient up to ~0.6 W per focus.
- **Fault case (not curtain-related):** the SLM or compute concentrates P_head into one spot. At 5 W the limit is reached in **1.6 ms**, at 20 W in 0.4 ms. An independent fast monitor of the emitted field with an AOM or laser-driver cut is required, with or without the curtain.
- Long-term: 10³ W/m² over 3.5 mm = 9.6 mW (≈ the 10 mW Class 1 AEL).
- Pulse-train rules above 1400 nm are rules 1 and 2 only (R3 P3). With probe-gated restarts (Microvision-style), repeated exposure is negligible: 70 µJ/s average is 0.07 mW.

**1550 nm, skin**
- Same 10⁴ J/m² over 3.5 mm (96 mJ) during a cut: irrelevant.
- But a finger *held* in a 50 mW focus for > 10 s exceeds the 10³ W/m² long-term limit by ~5× (5.2 kW/m² averaged over 3.5 mm). The curtain also covers skin.

**500 nm, retina** (Class 1 AEL, 18 µs–10 s, C6 = 1: 7×10⁻⁴·t^0.75 J)

| t | Energy limit | Max spot power |
|---|---|---|
| 0.1 ms | 0.70 µJ | 7.0 mW |
| 1 ms | 3.9 µJ | 3.9 mW |
| 1.4 ms | 5.1 µJ | 3.6 mW |
| 10 ms | 22 µJ | 2.2 mW |
| 0.25 s | 0.25 mJ | 0.99 mW |

LCSV visible spots are ≲ 0.2 mW, below the long-term Class 1 AEL of 0.39 mW, so the curtain is **unnecessary for visible light**.

### 7.4 Failure modes of per-beam monitoring (numbers)

**F1. Self-shadow versus threshold.**
- The mote blocks s = A·(a/r_c)² of its own beam: 2.8 % at r_c = 30 µm, a = 5 µm; **11 %** at r_c = 3a.
- θ_det must exceed s plus noise, unless the expected shadow is subtracted using the sensed position. That makes sensing a *safety-relevant* function.
- The undetected leak is ≤ θ_det·P_focus ≤ AEL, so P_focus ≤ 10 mW/θ_det = 67–200 mW for θ_det = 5–15 %. [THEORY]

**F2. Summed sub-threshold intercept** (not in M15).
- An aperture that takes a fraction f_k < θ_det of many cones receives (local bundle irradiance) × (aperture area) undetected.
- Example: a dense UI panel of 1000 motes in 10×10 cm at 50 mW per beam. At ~0.3 m in front, the bundle irradiance is ~3.6 kW/m², giving **~35 mW in a 3.5 mm aperture**. Each cone is ~9 mm wide there, so each per-beam drop is 3.8 % < 5 %: undetected.
- A real face blocks whole cones and trips the curtain. An **optical instrument or a small object** does not.
- Constraint: Σ_k min(f_k, θ_det)·P_k ≤ AEL for every aperture position. [THEORY]

**F3. Concave or refractive concentrators near a head** (spoon, magnifier, water-filled glass, curved phone glass).
- Example: a 5 cm concentrator near a 3–7 W head window takes ~1 % of *every* beam (each drop 1 %, undetected) and can refocus **30–70 mW** into one point.
- The defence is a **head-level absolute power-balance** check with a threshold below the AEL: ~0.1–0.3 % of P_head.
- That is marginal, because mote shadows (3–11 % of head power) must be modelled to ≲ 1 % of themselves. [ESTIMATE]
- Flat mirrors are benign: they keep the foci separate, so ≤ 2 foci × θ_det × P per pupil ≈ 5 mW.

**F4. Transparent objects** (glasses, plastic, droplets) transmit 92–99 %: a drop of 1–8 %, possibly sub-threshold, while displacing foci. Same remedy as F3.

**F5. Receiver blinding or common cause** (sunlight at 1550 nm, other heads' light, saturation). It can mask a drop. The remedy is per-beam modulation tags with lock-in detection plus two diverse channels (receiver array + emitter-side pickoff), i.e. ISO 13849 Category 3/4.

**F6. Restart into a still-present eye.** Re-arm only after a Class 1 probe confirms a clear path (VPH pattern).

**F7. Aerosols** (cooking smoke, vapes, candles) attenuate beams by 1–50 % and cause nuisance trips, i.e. image dropouts. Reliability, not safety.

**F8. Class 1 versus 1M (optical aids)** [THEORY, check against IEC 60825-1 Table 10].
- A 50 mm collecting aperture near a head window of diameter D takes (50 mm/D)² of P_head: 3.3 W × 1 % = 33 mW at D = 0.5 m.
- So 46 W film-density heads need D ≳ 0.9 m, more heads, or acceptance of Class 1M. This applies to both the curtain design and the no-curtain design.

**F9. Required integrity.**
- Severity S2 (corneal burns can scar), frequent exposure F2, avoidance P2 give a required performance level **PL e** (ISO 13849-1).
- That means Category 4, diagnostic coverage ≥ 99 %, two independent cut paths: a per-spot blank in the DMD plane plus a head AOM or laser-driver cut, with cross-monitoring. [ESTIMATE]

### 7.5 Verdict

- **Physics: sound.** Dose margins at 1550 nm are 25–100× for cuts of ≤ 13 ms.
- **Classification: unproven.** F1–F3 are the technical weak points, and the consumer path needs a new vertical standard.
- **Recommended architecture:**
  1. **Class 1 per focus by design** (pinning plus a certified field checker plus a fast fault monitor; §2.3), which has scanning-safeguard precedent.
  2. The curtain as defence in depth and as the basis of a **professional/venue mode** (Class 3B/4 with installation controls, as for RG3 projectors) that buys the 10–20× pixel saving.

---

## 8. Ranked top 5 (expected impact × probability it is real)

| # | Idea | What it fixes | Key number | Probability real | Biggest risk |
|---|---|---|---|---|---|
| 1 | **PI pinning loop using the band-limited nature of room air.** Replace the u/(2πf) jitter model; r_c → max(3a, 3σ) | Blocker 3 (normal rooms); B6 (kHz, not 10–50 kHz); the cubic law becomes linear in u; R8/R9 in ordinary rooms | PI error a_E/ω² = **0.4–1.3 µm at 200 Hz** (normal or busy room) vs 240 µm in the M15b model. Normal-room film density fits **93 W / 9.6×10⁹ px** (M15d: ~1 kW, fail) | 0.55 | Per-mote 2–4 µm sensing at ≥ 1 kHz for 10³–10⁴ motes; an analog (dithered) fast amplitude plane; intermittent gusts near hands |
| 2 | **Class 1 per focus by design (no curtain dependence)** at r_c 14–16 µm, enforced by a pre-emission field checker plus a fast fault monitor | Blocker 4 / R8 (safety case maps onto the scanning-safeguard precedent); B4 holds even at 0.3 m/s | P_focus **4.7–5.0 mW**. Total 1550 nm: **8 W (sketch), 46–50 W (film)**. 2.3×10¹⁰ px (~$0.73M vol, $26M lab) | 0.45 (conditional on #1) | Pixel count and compute; line-of-sight focus stacking (scheduler is still a safety function); single-fault SLM concentration needs ≤ 1.6 ms cut at 5 W/head; Class 1M optical-aid case for big heads |
| 3 | **Re-scoped curtain**: virtual protective housing for venue mode and defence in depth, with corrected dose rules (1 mm aperture, 7.85 mJ) and probe-gated restart | Blocker 4 for venue products; removes the ≤ 1.4 ms requirement; delivers a 10–20× pixel saving where accepted | Allowed t_cut **157 ms at 50 mW, 39 ms at 200 mW** vs 6–13 ms Type 4 response; visible spots already Class 1 | 0.6 as installation control; **0.2–0.3 as consumer Class 1 basis** | F2/F3 summed sub-threshold intercepts (needs a ≤ 0.1–0.3 % head power-balance check); EN 50689 "≤ MPE at any position"; no consumer precedent with electronic (non-intrinsic) cut |
| 4 | **Small (a ≈ 2–2.5 µm) hollow-shell motes** with plasmonic island skin; k_eff from bulk silica | The heat bound in normal rooms and hand wakes (the real u-limit); material k uncertainty | k_eff = k_in + 2k_s·t/a = 0.036–0.056 → **FOM 4.2–5.1** (if J₁/A ≈ 0.45); u_max **0.8–1.05 m/s** at ΔT ≤ 300 K | 0.3 | Island skin still unmade (≥ 90 % single-pass absorption without lateral conduction; J₁/A 0.30 → FOM 2.6); 50 nm-wall µm shells are fragile; fully respirable size (R3/R8 toxicology) |
| 5 | **Tiled, steerable sub-holograms** (small SLM tiles aimed by FSM/MEMS at stroke footprints; per-tile compute) | Pixel count and hologram compute (R10) for wireframe content; makes #2 affordable for sketches | Pixels ∝ S_proj·s/(πr_c²): sketch **~10× fewer** (2.3×10¹⁰ → ~2–3×10⁹) with 2 cm tiles; compute ~10¹⁵ → 10¹³–10¹⁴ flop/s | 0.5 | ~250 steerable tiles per head; only ~1.7× gain for film-density or video panels; tile hand-over during content motion |

**Killed this round:**
- soot/carbon-aggregate motes (C·FOM·A = 0.13);
- Er upconversion from trap light (3–50× short, no cyan);
- self-luminous chiplets (FOM ≈ 0);
- room-scale Paul traps (6×10⁴ V/m);
- time multiplexing (u·t_off ≫ r_c);
- line foci (127×);
- zone beams (10⁴–10⁵×);
- standing-wave recycling (J₁ cancels);
- particle streams (R3).

## 9. What the main session should check next (ordered)

1. **Re-run M15b–d with a PI pinning model**: σ from a_E, latency and sensing, not u/(2π·f_bw). Add a < 2.5 µm mote size grid.
2. **Add the safety checks M15 lacks**:
   - summed sub-threshold intercept (F2);
   - head power-balance threshold (F3);
   - line-of-sight focus stacking for the no-curtain design;
   - Condition 1 (50 mm) at head windows (F8);
   - corrected 1550 nm cut dose (1 mm, 10⁴ J/m²).
3. **Design the sensing chain on paper**: receiver image-plane superpixels per spot + dither or gradient → position noise per mote at 1 kHz. This is now the critical-path unknown, next to the mote.
4. **Bench addition to G1–G4**: one mote, PI loop, fan-driven turbulence with measured ε. Measure pinning error against bandwidth and confirm x_err ≈ a_E/ω².

---

## Appendix A: reproducing the new numbers (scratch scripts, not committed)

- `r2_numbers.py` and `r2_cap.py` import `09_unlock/m15_lightcurtain_static.py` unchanged.
- **Pinning:** call `design2` / `optimise` with `bw_frac = u/(2π·σ·f_fast)`, σ = 4 µm, so that `jitter = σ` (then r_c ≥ max(3σ, 3a) and r_v ≥ max(2σ, 1.5a)).
- **Hollow mote:** `MOTES["hollow_ito"] = dict(alpha=None, j1A=0.45, A=0.9, k_eff=0.036, q_side=0.3, T_max=600, rho=60, j1_factor=1)`.
- **No-curtain scan:** r_c grid 7.5 µm × 1.05ⁱ, keeping the largest r_c with 2·P_focus ≤ 10 mW.
- **Turbulence:** η_K = (ν³/ε)^¼; λ_T = √(15νu′²/ε); a_E = √((U·u′/λ_T)² + (ε^¾/ν^¼)²); PI error = a_E/(2πf_bw)².

## Sources

- Wi-Charge: [Wikipedia](https://en.wikipedia.org/wiki/Wi-Charge); [Laser Focus World](https://www.laserfocusworld.com/lasers-sources/article/16557086/infrared-lasers-provide-wireless-cell-phone-charging)
- Resonant beam / DCCL safety: [Distributed Laser Charging, arXiv 1801.03835](https://arxiv.org/pdf/1801.03835); [DCCL safety analysis, arXiv 2507.21891](https://arxiv.org/pdf/2507.21891)
- IEC 60825-1 risk analysis and single fault: [Schulmeister, ILSC 2013](https://www.seibersdorf-laboratories.at/fileadmin/user_upload/docs/le/las/publ/2013_ilsc_risk_analysis_relevant_laser_products_iec_60825-1_schulmeister_01.pdf); [Lasermet classification overview](https://www.lasermet.com/laser-safety-services/an-overview-of-the-led-and-laser-classification-system-in-en-60825-1-and-iec-60825-1/); [IEC 60825-1:2014 webstore](https://webstore.iec.ch/en/publication/3587)
- Scanning safeguard (secondary): [allpcb LiDAR safety](https://www.allpcb.com/allelectrohub/are-lidars-safe-technical-analysis-of-lidar-safety); Microvision VPH: [verdict.co.uk](https://www.verdict.co.uk/microvision-gets-grant-for-eye-safe-light-detection-and-ranging-system-with-virtual-housing/)
- IEC 60825-2 APR: [Lightwave, DWDM eye safety](https://www.lightwaveonline.com/optical-tech/article/16648942/laser-eye-safety-for-dwdm-networks); [ITU-T G.664](https://www.itu.int/rec/dologin_pub.asp?lang=f&id=T-REC-G.664-199907-S!!PDF-E&type=items)
- IEC 60825-4: [iTeh EN IEC 60825-4:2024](https://standards.iteh.ai/catalog/standards/clc/02089986-3ee9-4b1a-b3e7-196f60e5c75d/en-iec-60825-4-2024); [IEC 60825-4:2022 preview](https://cdn.standards.iteh.ai/samples/22956/9b14c36750d44e35bd16146859319178/IEC-60825-4-2022.pdf)
- EN 50689: [JJR Lab](https://www.jjrlab.com/news/new-european-standard-for-laser-products-en50689-2021.html); [ILSC 2023 abstract](https://pubs.aip.org/lia/ilsc/proceedings-abstract/ILSC2023/2023/L0602/3298026)
- IEC 62471-5 hazard distance and detection: [Epson HD notice](https://files.support.epson.com/docid/cpd5/cpd56230/source/notices/reference/pl20000unl_l20002unl/hazard_distance_pl20000unl.html); [Panasonic RG whitepaper](https://eu.connect.panasonic.com/sites/default/files/media/document/2022-12/en_risk_group_whitepaper.pdf)
- PowerLight: [GeekWire 2021](https://www.geekwire.com/2021/powerlight-ericsson-demonstrate-laser-beaming-system-power-5g-base-stations/); [SPIE 13359](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13359/133590A/Analysis-and-design-of-safe-laser-power-beaming-systems/10.1117/12.3043851.short)
- Type 4 light curtains: [Schneider XUSL4E14F061N](https://www.mouser.com/datasheet/2/357/Preventa_Safety_detection_XUSL4E14F061N-1787359.pdf); [Datasensing SLIM](https://www.datasensing.com/eng/safety-and-guidance/slim/sl4-14-0150-e/957910000-pm-1183.html); [SICK deTec4](https://pim.galco.com/Manufacturer/Sick/TechDocument/Data%20Sheet/dataSheet_C4C-EB07510A10000_1219537_en.pdf)
- Room air turbulence: [Hanzawa, Melikov, Fanger 1987 (DTU Orbit)](https://orbit.dtu.dk/en/publications/airflow-characteristics-in-the-occupied-zone-of-ventilated-spaces/)
- Photophoresis data: [soot aggregates](https://www.researchgate.net/publication/287037864_Photophoretic_motion_of_fractal-like_soot_aggregates_Experiment_and_theory_comparison); [Shvedov 2009](https://pubmed.ncbi.nlm.nih.gov/19333344/); [SLM photophoretic arrays (CEUR-WS)](https://ceur-ws.org/Vol-1638/Paper15.pdf)
- OTD / BYU: [Nature 2018](https://www.nature.com/articles/nature25176); [RSI 2021](https://pubs.aip.org/aip/rsi/article/92/10/103002/955132/Photophoretic-trap-testing-rig-for-volumetric); [SPIE 2023](https://ui.adsabs.harvard.edu/abs/2023SPIE12445E..0IB/abstract); [Cal Poly 2025 thesis](https://digitalcommons.calpoly.edu/theses/2947/); [review arXiv 2512.09401](https://arxiv.org/pdf/2512.09401)
- Tweezer arrays: [Nature 2025, 6100 qubits](https://www.nature.com/articles/s41586-025-09641-4)
- Other routes: [Paul-trap display, Opt. Lett. 2019](https://opg.optica.org/ol/abstract.cfm?uri=ol-44-6-1476); [UPNA elastic diffuser (Hackaday)](https://hackaday.com/2025/04/14/elastic-bands-enable-touchable-volumetric-display/); [Blaise Photonics VAST](https://natlawreview.com/press-releases/blaise-photonics-solves-worlds-first-safe-mid-air-volumetric-touchable)
- Lab-internal: `01_research/R3_safety_limits.md` rows L7, K1, P3 (1550 nm MPE, Class 1 AEL, pulse rules)

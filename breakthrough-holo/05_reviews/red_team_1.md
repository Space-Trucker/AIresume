# Red team 1: laser-plasma physics, laser safety, acoustics

Reviewer roles: senior laser-plasma physicist, laser-safety officer and acoustician. The brief was to break the claims.

**State reviewed.** The files as they stood at about 02:45 UTC on 2026-09-30. Several files changed while the review was running, and the review covers the latest versions:
- `display_budget.py` (heat-release noise model, `total_gain_db`)
- E6 (room columns), E6c (new) and E5b (new)
- E10 (subsonic gain and the strict NO₂ criterion)
- `ARCHITECTURE.md` §3.5–3.6b
- `FINAL_VERDICT.md` draft v1

**Method.** Every number marked *[RT]* was computed for this review by importing the lab's own code: `sim_e6_acoustic_scheduling`, `sim_e6c_subsonic_tracing`, `holo_engine/kernel.py` and `sim_e7_laser_safety.hazard_length`. The only changes were perturbations of the lab's own inputs. The scripts are `rt_acoustic.py`, `rt_e6c.py` and `rt_kernel.py` in the session scratchpad.

**Severity counts:** 3 critical, 11 major, 5 minor. Findings 1–2 cover theory, 3–4 plasma light, 5–8 acoustics, 9–10 chemistry, 11–15 laser and optical safety, 16–17 hardware, 18 colour, and 19 the grading.

---

## A. Theory (T1, T2)

### 1. Minor: the line-of-sight theorem and the touch lemma hold, but the proof has gaps worth closing

**Claim (T1):** light the eye receives from the direction of P is the light leaving the first opaque surface B. Only in-volume emission escapes this.

**Assessment.** No loophole changes the conclusion. Three statements are missing:
- **Refraction.** Inhomogeneous air (heat, sound) bends rays; it does not only scatter them. The maximum bend is set by total internal reflection at a density step. For fully depleted air, Δn ≤ 2.7×10⁻⁴, so the deviation is at most 2·√(2Δn) ≈ 2.6°. That cannot reach viewers at large angles.
- **Plasma mirrors.** Air at 1 atm can reach at most n_e ≈ 1–2×10²⁶ m⁻³, even with multiple ionisation. That is well below the critical density for visible light (4.5×10²⁷ m⁻³ at 500 nm). A plasma therefore cannot reflect visible light toward a viewer.
- **Coherent processes.** "Side emission is suppressed at a smooth focus" covers one beam only. The general argument is momentum closure: every parametric output k-vector is a signed sum of input k-vectors from one aperture. It must therefore lie near the input cone (the idea round's "momentum-budget theorem"). Without this argument, crossed-beam four-wave mixing aimed at a tracked eye looks like a 10⁵× efficiency loophole (4π/Ω_pupil), and a reader cannot rule it out.

**Touch lemma.** It is correct. The only escape is a light-field-emitting glove, which is not a "simple glove".

**Fix:** add these three short paragraphs to T1.

### 2. Minor: T2's "independent upper bound" contradicts T2's own calibration point

**Claim:** an optically thick kernel radiates at most 3σT⁴/(ε c_s), which is ≲ 5 % for T ≤ 3 eV. "No air plasma much exceeds ~1 lm per absorbed watt."

**Why weak:**
- The calibration point is a ns spark radiating 22–34 %. That is 5–7× above the "bound", so the reference plasma must be at T ≫ 3 eV. R1 agrees: "mostly UV at T_e > 10⁵ K".
- The σT⁴ bound is size-independent and rises as T⁴. It does not cap efficacy.
- The ≲ 1–2 lm/W ceiling actually follows from the *visible fraction*: ≲ 1–3 % of absorbed energy lands in 400–700 nm (R1, lightning ≲ 1 %).

**Fix:** replace the σT⁴ argument with the visible-fraction argument. Also note that the 22–34 % UV/VUV share of ns sparks photolyses O₂, a hidden ozone source (see finding 10).

---

## B. Plasma light (question 2)

### 3. Major: the micro-spark luminous efficacy (0.1–0.4 lm/W) is an extrapolation from an estimate, not a calibrated prediction, and the model is inconsistent with E3

**Claim (T2, `display_budget.luminous_efficacy`):**
- "Calibration: ns sparks give 0.7–6 lm/W; the model reproduces 2.1 lm/W at 50 mJ."
- 1–100 µJ micro-sparks give 0.1–0.4 lm/W.

**Why wrong or weak:**
1. **The calibration is circular.**
   - R1 line 178 *assumes* 0.5–3 % of absorbed energy in the visible for ns sparks.
   - R1 gap G2: "No measured luminous efficiency (lm/W) was found for laser sparks."
   - R1 gap G1: no absolute luminance for any fs air display.
   - `f_rad_ref` and `lm_per_W_rad` are then tuned to hit that assumption. Reproducing 2.1 lm/W is by construction, not a validation.
   - There is no measured anchor anywhere in the chain.
2. **The kernel energy density is taken from the wrong regime.**
   - `eps_k` = 2.5×10⁹ J/m³ is ≈ 300 eV per *atom* at 1 atm (≈ 620 eV per molecule). That is the energy absorbed along a growing ns-spark absorption front, not a thermalised micro-kernel.
   - The lab's own E3 gives n_e ≈ 2.5×10¹⁹ cm⁻³ for 2–10 µJ foci. That implies ε ≈ n_e(I_p + 3/2 kT_e) ≈ 1×10⁸ J/m³, about 25× lower.
3. **The parametrisation has the wrong sign in ε.**
   - x ∝ r₀ with a fixed τ_rad means a *lower* energy density gives a *larger* r₀ and a *higher* η. With E3's ε, η rises to ~0.4 lm/W.
   - Physically, lower n and T lengthen τ_rad (the radiated power scales as n²Λ(T)), so η should fall.
   - The f ∝ r₀ law is the optically thin limit. The ns reference kernel radiates mostly in the thick, hot, UV phase. The extrapolation therefore crosses regimes over 3.5 decades of energy.
4. **Independent estimate [RT, order of magnitude].**
   - Optically thin N/O plasma at n_e ≈ 2.5×10¹⁹ cm⁻³ and 1.5–2 eV: line plus recombination loss ~10¹⁵ W/m³, so τ_rad ~ 100 ns.
   - Hydrodynamic quench r₀/c_s ≈ 10 µm / 4 km/s ≈ 2.5 ns, so f_rad ~ 1–3 %.
   - The visible share of that radiation depends on whether N II/O II green-blue lines (V ≈ 0.3–0.7) or violet N₂/N₂⁺ bands (V ≈ 10⁻³–10⁻²) dominate.
   - **Plausible η: 0.01–1 lm/W.** The floor is the cold fs plasma at 10⁻⁵ lm/W. The ceiling is ~1–2 lm/W.
   - The lab's nominal 0.15 lm/W is not implausible, but it is not predicted either. The low end of the Monte Carlo band (0.03) should extend to ~0.005–0.01. At that level the product collapses to sparse accents.

**Fix:**
- Label η "unmeasured (±30×)" everywhere it is used.
- Re-derive ε_k from E3 and make τ_rad a function of (n, T).
- Under the pre-registered rule, every requirement whose number depends on η is PARTIAL pending X1 (see finding 19).
- X1 must record absorbed energy and a calibrated spectrum from 200–900 nm, not only lumens.

### 4. Major: the assumed 25–50 % absorption contradicts E3 (1–26 % for sub-ps pulses)

**Claim (ARCHITECTURE §3.1):** "5–10 µJ absorbed (10–40 µJ incident)".

**Why weak:**
- The seed-plus-heater scheme that is supposed to raise absorption is [EXP]; the only simulation says 1–26 %.
- At 10 % absorption:
  - Incident energy becomes 50–100 µJ.
  - Laser average power becomes 30–100 W instead of 20–40 W.
  - The single-pulse hazard zone grows ×1.6–2.2 (it scales as √E).
  - Transmitted power onto floors and people rises (finding 15).

**Fix:** carry absorption as an explicit uncertain parameter (0.05–0.5) through E7, E10 and the BOM, and add it to X1.

---

## C. Acoustics (question 3)

### 5. Minor (a validation): the random-order audible level is physically robust, and the dB(A) value is dominated by 12.5–20 kHz

**Check [RT].**
- Thermal-monopole estimate: each spark leaves a permanent volume step ΔV = (γ−1)E/(γp₀). The far-field spectrum is |P(f)| = ρ f ΔV/(2r).
- At 5.66×10⁵ sparks/s and 6.8 µJ, the Campbell sum gives **55.7 dB(A)** direct at 1 m. The N-wave model's direct part gives 55.2 dB(A).
- The absolute floor is therefore right, and it does not depend on N-wave details, k_T or nonlinear propagation. The lab has since adopted this heat-release model as a cross-check.

**Caveat.** With an f² spectrum, **63 % of the A-weighted energy is in the 12.5–20 kHz bands**:
- A-weighting overstates the loudness for adults over ~40, whose thresholds at 16 kHz are 40–70 dB SPL.
- It understates annoyance for children and teenagers, who hear a whine.
- Unscheduled, the 20 kHz band reaches ≈ 70 dB at 0.3 m for the 5 cd/m², 10k-point case. That is the INIRC-IRPA public limit for that band.

**Fix:** report the 16 kHz and 20 kHz band levels separately, next to dB(A).

### 6. Major: listener phase locking (E6 −26 dB, E6b −35 to −40 dB) holds only for a point ear in free field with perfect repeatability

**Claim:**
- T2 §2: "−26 dB for one tracked listener".
- ROADMAP X4: "validates −26 dB".
- ARCHITECTURE §3.5: E6b gives "real-room benefit 1–10 dB on top".

**What is and is not the cause.**
- It is *not* an artefact of repeated frames. Listener-locked timing works frame by frame.
- It is *not* an artefact of nonlinear N-wave propagation. The audio band is set by the linear thermal monopole.
- It *is* an artefact of four assumptions: the ear as a mathematical point known exactly; free-field propagation; identical spark amplitudes; and no head.

**Robustness [RT]** (E6 armour content, listener-locked schedule, change of A-weighted level versus random order, computed on the lab's own `arrival_spectrum` machinery):

| Perturbation | Level change vs random |
|---|---|
| None (lab result) | −26.7 dB |
| Ear displaced 1 mm | −26.0 dB |
| Ear displaced 2 mm | −23.1 dB |
| Ear displaced 5 mm | −20.9 dB |
| Ear displaced 10 mm | −14.1 dB |
| Ear displaced 20 mm | −7.3 dB |
| Ear displaced 50 mm | −2.8 dB |
| **Other ear (0.16 m lateral)** | **−1.3 dB** |
| Spark-amplitude jitter 5 % rms | −23.7 dB |
| Spark-amplitude jitter 10 % rms | −19.5 dB |
| Spark-amplitude jitter 20 % rms | −14.2 dB |
| Spark-amplitude jitter 30 % rms | −11.0 dB |
| Arrival-time jitter 0.5 µs | −24.1 dB |
| Arrival-time jitter 1 µs | −20.3 dB |
| Arrival-time jitter 2 µs | −15.1 dB |
| Arrival-time jitter 5 µs | −8.3 dB |
| Arrival-time jitter 10 µs | −3.0 dB |
| HRTF-like direction-dependent error, ±1 dB / ±5 µs | −14.7 dB |
| HRTF-like direction-dependent error, ±3 dB / ±20 µs | −4.0 dB |
| Floor reflection only (R = 0.9) | −10.5 dB |
| Six first-order image sources (5×5×2.7 m room) | −6.4 dB |
| Full diffuse reverberation (lab's own E6 room columns, A = 20–60 m²) | −1 to −3 dB |

- The "quiet zone" has a radius of ~5 mm at −20 dB. One tracked point protects one eardrum at best.
- Realistic physical timing jitter is 1–2 µs:
  - The 0.2 m/s capture curtain alone shifts arrivals by L·u/c² ≈ 2 µs over 1.2 m.
  - A 0.1 K temperature difference along the path shifts them by ~0.6 µs.
  - A 5–10 ms tracking latency at 0.2–0.5 m/s head speed gives 1–5 mm ear error.
- "1–10 dB on top" in a room: the 10 dB end needs I_rev < 0.1·I_dir at 1.2 m, which means A ≳ 700 m² (an anechoic room).
- E6b's schedules also ignore hardware limits. The minimum pulse gaps are 0.01–0.18 ns. There is no per-channel ≥ 10–20 µs AOD access constraint, no channel or aperture assignment, and no amplifier energy-versus-interval model.

**Fix:**
- Delete "−26 dB" from T2 and ROADMAP X4. Quote "≤ 2 dB in a furnished room; direct field −8 to −15 dB at a real ear".
- If phase locking is kept, re-run E6b with image sources, a spherical-head HRTF, ±5 mm ear uncertainty, 10 % amplitude jitter and the hardware constraints.

### 7. Major: subsonic multi-channel tracing (E6c, −19.5 to −26.5 dB) was tested only on the most favourable content

**Claim (ARCHITECTURE §3.5, FINAL_VERDICT):**
- "Total radiated audible power −19.5 to −26.5 dB in all directions."
- E10 applies a flat −15 dB, and the speciation Monte Carlo applies −19.5 dB.

**The physics is sound.** A steady, subsonically moving monopole radiates only at ends, turns and changes of strength. E6c is the lab's best acoustic idea.

**But the test content is long, smooth, closed, constant-brightness rings** (the armour wireframe). Iron Man content is dense UI (ref4/ref5): glyphs, text, point markers and video panels.

**Tests [RT]** (lab's `schedule_subsonic`, K = 12, 40 kHz, ramp 4, 48 far-field directions):

| Content or fault | Total radiated audible power vs random |
|---|---|
| Armour (lab case) | −23.0 dB |
| Armour with a 45 mm interlock hole at one hand | −22.9 dB (negligible) |
| Armour with 2 % misfires | **−15.4 dB** |
| Armour with 0.5 % dust-seeded 3× outliers + 10 % jitter | **−13.8 dB** |
| UI glyphs, 1000 strokes of 1.5–3 cm (frame fill 87 %) | **−5.9 dB** (K24/25 kHz: −8.1 dB) |
| 96×54 video panel, all pixels on | −11.3 dB |
| 96×54 video panel, 50 % dither | **−2.8 dB** |

- **Where misfires and outliers come from.** Near-threshold ps breakdown has stochastic misfires. Indoor air holds ~10⁶–3×10⁷ particles/m³ larger than 0.5 µm. The pre-focus volume above the particle-seeded threshold is ~10⁻¹¹–10⁻¹⁰ m³. That gives particle-seeded sparks on ~0.01–0.5 % of shots. These are also visible "twinkles" in front of the intended voxel.
- **The residual is tonal.** For static frames the residual is a 60 Hz-harmonic line spectrum, a buzz rather than broadband hiss. ISO 1996-2 applies a +3 to +6 dB penalty for tonal noise.
- **The 25 kHz variant (K24) has a Doppler problem.** At M = 0.22, its regular 25 kHz line is Doppler-shifted down to ≈ 20.5 kHz on receding strokes. That puts it into the 70 dB IRPA 20-kHz band and into the hearing range of children.
- **Tones reach pets.** Every variant concentrates ultrasound into 25–40 kHz tones, about 6 dB above the broadband level in-band. That is ≈ 70–80 dB at 0.3–1 m, where dog and cat hearing thresholds are ~10–25 dB SPL.

**Fix:**
- Make the E6c gain content-dependent. Use −5 to −10 dB for UI, text or video-rich frames, and add misfire and outlier terms.
- Keep f_ch ≥ 35 kHz.
- State that video panels stay at essentially random-order noise.

### 8. Major: the noise budget omits the loudest subsystem, uses an occupational limit as the pass mark, and puts the listener too far away

**Claims:**
- FINAL_VERDICT R8: "Hearing ✓: 40–44 dB(A) (limit 85 dB(A))."
- E10: "SAFE ≤ 85 dB(A)".

**Why wrong:**
- **Wrong limit.** 85 dB(A) is the occupational 8-h hearing-damage action level. The criteria set by the lab itself (GOAL R8 "limits for bystanders", T2 "35 dB(A) home target", R3 N1 WHO 35 dB LAeq for living rooms) all say 35.
- **Missing source: the 900 m³/h air handler.**
  - It pushes air through MnO₂, KMnO₄/alumina and carbon beds (Δp ~200–500 Pa).
  - Consumer purifiers of 850–1000 m³/h are rated ~55–65 dB(A) at maximum speed, with low-Δp media.
  - The air handler alone is plausibly ≥ 45 dB(A) at 1 m.
  - Laser-rack cooling for ~0.5 kW is also missing.
- **Wrong distance.** The interacting user's ears are 0.3–0.5 m from the strokes, not 1 m. In a room with A = 20 m², that adds ≈ +3–5 dB (the direct-to-reverberant ratio rises from 0.4 to ~2).

**Estimate for Iron-Man-style content (armour plus UI plus a panel) at the user's ear:**
- Plasma: 59 dB(A) at 1 m unscheduled, −5 to −12 dB from finding 7, +3–5 dB for distance, giving **50–58 dB(A)**.
- Plus the air handler.
- R8 noise is **NOT MET** by 15–23 dB.

**Fix:**
- Put the air handler (with its media pressure drop) and cooling into the noise budget.
- Evaluate at 0.4 m.
- Grade against 35 dB(A), and show 85 dB(A) only as the hearing-damage threshold.

---

## D. Air chemistry (question 4)

### 9. Major: 90 % source capture is physically implausible for this geometry, and the near-field model is optimistic for the user

**Claim (ARCHITECTURE §3.4, E5, E5b, E10):** push–pull airflow "captures ≥ 90 % at the source", allowing 2–3 W absorbed instead of 0.3 W.

**Why wrong:**
- The extraction is in the ceiling halo at 2.7 m, but the sparks are 0.8–2.6 m below it.
- A sink's inflow velocity falls as Q/(2πx²). For Q = 0.25 m³/s that is **0.04 m/s at 1 m and 0.01 m/s at 2 m**. Room drafts are 0.1–0.2 m/s, and a walking person's wake is 0.5–1 m/s.
- The interacting person's own thermal plume, ~0.2–0.25 m/s upward, entrains chest-level products into the breathing zone. This is the documented "personal cloud" effect.
- The descending 0.2 m/s curtain opposes the upward path to the central exhaust, and people's arms and bodies cut through it by design.
- Industrial capture hoods reach ≥ 90 % only within ~1 hood diameter, with capture velocities of 0.25–0.5 m/s.
- The near-field term treats the hologram as a point source 0.5 m away. A touching user's face is 0.2–0.4 m from the strokes of a 1.8 m distributed source, which gives 1.3–2.5× more.

**Estimate:**
- A realistic capture of 0.3–0.7 makes (1 − capture) 3–7× larger than assumed.
- With the lab's own E5 numbers, the ≤ 20 ppb budget becomes **~0.4–1 W absorbed**, i.e. 0.06–0.15 lm. That is the "sparse style" tier, not 5–9 m of strokes.

**Fix:**
- CFD with a heated manikin whose hands are in the volume.
- Carry capture as 0.3–0.9 in the E10 Monte Carlo.
- Make X5 use a thermal manikin and real cross-drafts.

### 10. Major: the Y band is plausible, but the ×12 "NO-rich" budget multiplier (E5b) is fragile, and the headline operating point already breaks the lab's own governor

**Claims:**
- E5b: hot-spark speciation (90 % NO) multiplies the room-safe power by 12.3.
- FINAL_VERDICT: air is "10–23 ppb".

**Why weak:**
1. **Speciation is likely the other way for micro-sparks.**
   - A 10 µm kernel quenches in ns. Thermal (Zeldovich) NO needs µs–ms above ~2000 K.
   - Any VUV fraction photolyses O₂ into 2 O₃ per photon. If 10–20 % of the absorbed energy leaves as VUV, Y_O₃ ≈ 1.5–3×10¹⁷ per J, at or above the top of the Y band.
   - Micro-sparks are therefore more likely O₃-rich (the ×2.3 case) than NO-rich.
2. **NO-rich operation is not stable indoors.**
   - At the limit, E5b allows 185–300 ppb NO continuously in the breathing zone. No public guideline supports this; 300 ppb is 15 % of an 8-h occupational limit meant for healthy workers.
   - Ventilation imports O₃. With summer outdoor O₃ at 60–80 ppb and windows open (ACH 2–3), about 240 ppb/h of O₃ enters and is titrated by NO within ~10 s. My estimate is ≈ 15 ppb NO₂ steady state even with the scrubber, above the 13 ppb criterion.
   - Carbon beds reduce part of the captured NO₂ back to NO.
3. **The demo's own operating point violates the governor.** `holo_engine/out/stats.json` shows 9 m at 4 cd/m² → **22.6 ppb**. That exceeds ARCHITECTURE §3.4's governor limit (≤ 20 ppb) and the strict WHO 24-h NO₂ value (13 ppb). It is allowed only through the speculative speciation multiplier.

**Fix:**
- Default to "all NOx ends as NO₂" until X2 and X7 are measured.
- Include ventilation-borne O₃ in scenarios.
- Size the demo to the governor.

---

## E. Laser and optical safety (question 5)

### 11. Major: the hazard zones and interlock margins are inconsistent with the optical design, and at the margin they allow about 2× the MPE

**Claims:**
- E7 and ARCHITECTURE §3.3: hazard zone "≤ 4–16 mm", "≤ 10 mm at 20 µJ".
- Kernel: `hazard_skin_m = 0.010`, margin 22.5 mm.
- Blanking "1–4 %".

**Why wrong:**
- E7's headline uses NA 0.2, but the architecture has NA 0.09–0.12 at 1.3–1.7 m, falling to ≈ 0.05 for voxels 2.6 m from a ceiling head.
- The hazard zone scales as √E/NA. From the lab's own `hazard_length` (IEC-derived, 1 mm aperture) [RT]:

| Pulse | E incident | NA 0.12 | NA 0.09 | NA 0.05 |
|---|---|---|---|---|
| 0.3 ps | 20 µJ | 17 mm | 22 mm | 40 mm |
| 0.3 ps | 40 µJ | 24 mm | 32 mm | 57 mm |
| 1 ps | 40 µJ | 13 mm | 17 mm | 30 mm |

- At the 22.5 mm margin with NA 0.09 and 40 µJ at 0.3 ps, skin fluence is 2E/(π(NA·d)²) = **6.2 J/m², 2× the IEC-derived 3 J/m²**. The same holds for 1 ps pulses to far voxels (NA 0.05: 20 J/m² vs 10 J/m²).
- **Latency × speed is too small.**
  - The margin assumes 5 ms × 1.5 m/s. The product's own gesture set includes "flick to throw away", with fingertips at 2–5 m/s.
  - Depth-camera plus processing latency is ~8–10 ms at 240 Hz.
  - Tracker dropout is blanked only "within one frame" (16.7 ms).
- **5 mm tracking error is optimistic.** ToF depth noise is ~1 % of range (2–3 cm at 2–3 m) for unmarked bystander fingers. The aluminised glove is specular and causes ToF dropouts and multipath on exactly the hand that must be tracked best.

**Estimate:**
- A corrected margin is **45–90 mm**.
- Blanking [RT], with the lab's kernel and armour content:
  - Lab's reach-in scenario: 1.1 % → 4.6 %.
  - Person leaning over the model with a two-hand grab from above: **4.0 % → 19.9 %**. All three apertures are on the ceiling, so bodies above the content shadow everything beneath them.

**Fix:**
- Derive `hazard_skin_m` from the actual NA(z) and incident E per voxel.
- Use ≥ 3 m/s and the dropout latency.
- Report the local "hole" around each hand, not the global blank fraction.

### 12. Major: objects are not modelled, only human capsules

These missed hazards follow from the kernel knowing only tracked human skin and heads.

**(a) Specular and refractive objects in the post-focus cone.**
- A concave reflector whose focal length f roughly matches its distance from a voxel re-collimates the diverging transmitted beam. The fluence 2E/(π(NA·f)²) then stays constant over metres.
- Example: f = 2 cm, NA 0.1, 20 µJ transmitted gives **3.2 J/m², above the IEC-derived single-pulse MPE, at any distance across the room**. The beam is invisible.
- Candidates:
  - A cupped **aluminised glove** (the design's own choice).
  - Spoons, bowls, jewellery, watch cases.
  - Glass spheres or paperweights and camera lenses. Glass transmits 1550 nm, so these can re-focus to a new, untracked focus. Water-filled glassware is safe at 1550 nm because water absorbs it.
- A flat mirror only folds the path and does not increase the hazard.

**(b) Foci on or inside objects.**
- At the focus, 40 µJ in a 5 µm waist is ~10⁶ J/m². That ablates and chars paper, fabric, hair, plastic props and phones held "into" the hologram, 60 times a second per voxel.
- It also means the glove's "non-ablating aluminised" claim fails under the very fault it is meant to cover. The ablation threshold of aluminium at sub-ps is ~10³ J/m².

**(c) Non-human and small occupants.**
- The kernel has no "unknown occupancy → blank" rule.
- Pets (a cat on the table, a bird) and toddlers, whose faces sit at 0.8–1.2 m, inside the armour's height range, are not "heads" to the tracker. They get the 22 mm skin margin, not the 170 mm eye margin.

**Fix:**
- Add a scene depth map to the safety kernel, with a conservative "unknown object → eye margin" rule.
- Blank voxels whose *post-focus* cone meets any non-diffuse or unknown surface within ~1 m.
- Forbid content from intersecting surfaces.
- Make the glove outer layer diffuse and absorbing (for example carbon-loaded), not aluminised.

### 13. Major: the "UV: more than 100× margin" result rests on a single-wavelength weighting

**Claim (E7 `uv_exposure`, FINAL_VERDICT):** 8-h actinic dose 0.08 J/m² at 0.5 m against a 30 J/m² limit.

**Why wrong:** all UV is weighted with S(337 nm) = 3.2×10⁻⁴, but air-plasma UV is not one line.
- **N₂ second positive system.** It includes the 315.9 nm band (S ≈ 0.0024) and the 296.2 and 297.7 nm bands (S ≈ 0.46–0.5), at roughly 5 % and 3 % of the 337 nm band (AIRFLY-type ratios). Band-resolved, S_eff ≈ 0.011, **about 30× the assumed value**.
- **Hot continuum.** The lab's own E11 continuum at T = 3 eV puts ≈ 0.5× the visible power into 200–280 nm, where S = 0.3–1. NO-γ bands (200–250 nm) add more, and NO is produced.

**Estimate:** with the lab's inputs (3 W absorbed, f_rad 3 %, 30 % UV):
- 8-h dose at 0.5 m: **2.7 J/m²** (N₂ bands) to **~25 J/m²** (continuum-weighted). The margin is **1–11×**, not > 100×.
- At a user's 0.3 m, the margin is 0.4–4×. The daily limit can be exceeded during a working day at the display.

**Fix:**
- Measure 200–400 nm in X1 with a calibrated spectroradiometer.
- Weight with the full ICNIRP S(λ).
- Include UV dose in the brightness governor.

### 14. Critical: the product classification and certification path contradict the lab's own safety research

**Claims:**
- ARCHITECTURE §3.3: "Certification target: Class 1 during operation by engineering controls (IEC 60825-1)".
- FINAL_VERDICT R8, laser sub-check: ✓.

**Why wrong:**
- R3 §3.2 (the lab's own notes) says an open-air volume that a hand or eye can enter is a Class 4 exposure, and that presence sensing is **not accepted by the classification standard as a way to lower the class**. "Class 1 during operation" requires a protective housing.
- Accessible emission:
  - Peak power: 40 µJ / 0.3 ps ≈ 1.3×10⁸ W, against the sub-ns Class 1 AEL of 8×10⁶ W (×17).
  - Average power: 20–40 W, against 10 mW (×2000–4000) and the 0.5 W Class 3B limit.
  - The accessible beam is **Class 4** by any reading.
- Regulation:
  - EU consumer-laser rules (EN 50689:2021, R3 §3.2) do not allow an open Class 4 consumer product.
  - US demonstration laser products above Class IIIa need an FDA variance (21 CFR 1040.11(c)). Variances are granted to operators with separation distances or MPE-compliant audience scanning, not for home appliances.
- **SIL 2 is under-specified.** The failure consequence is irreversible eye injury (corneal ablation at ~10⁶ J/m²), with frequent exposure and poor chance of avoidance.
  - Machinery practice would put this at PL e / SIL 3-class.
  - Fleet arithmetic: at PFH 10⁻⁶ /h, 10⁵ units running 2000 h/yr give ~200 dangerous failures per year.

**Fix:**
- Regrade the laser sub-check as NOT MET for everyday or home use.
- State that the only lawful route today is a supervised venue installation (Class 4, variance, trained operator, SIL 3-class interlock).
- Enclosing the volume would make Class 1 possible, but it breaks R1 and R7.

### 15. Minor: average-exposure inputs are understated

**Claim (E7 (b)):** 10 W transmitted, giving ≤ 10 mW/cm².

**Why weak:**
- The architecture's 20–40 W optical, with 5–10 µJ of 10–40 µJ absorbed, transmits 15–35 W. With 10 % absorption (finding 4) it transmits more.
- Head-over-hologram irradiance becomes 15–35 mW/cm². That is below the 100 mW/cm² corneal limit, but the stated 10× margin is really 3–7×.
- For a person under a dense cluster, it approaches the 10 mW/cm² large-area skin limit.

**Fix:** tie P_trans to the architecture's (E_incident − E_absorbed) × rate.

---

## F. Buildability (R10)

### 16. Critical: the addressing optics violate conservation of étendue by about 250× per axis, so R10 "MET" is false

**Claim (ARCHITECTURE §3.2):**
- A TeO₂ AOD pair plus an AO lens, then a 28 cm asphere or Fresnel doublet.
- NA ≈ 0.09–0.12 foci anywhere in a ~1 × 1 × 1.8 m volume.
- 50–80 k random-access voxels/s per channel.
- FINAL_VERDICT: "Every part exists today".

**Why wrong (the Lagrange invariant):**
- **What the AOD can deliver.**
  - A slow-shear TeO₂ AOD (v ≈ 620 m/s, Δf ≈ 50 MHz) with 10 µs access has aperture D = vτ ≈ 6.2 mm.
  - Its scan range at 1550 nm is λΔf/v ≈ 0.125 rad, giving **N ≈ τΔf ≈ 500 resolvable spots per axis**.
- **What the design needs.**
  - A 28 cm aperture at NA 0.1, covering ±0.5 m at 1.5 m (≈ 0.67 rad), needs N ≈ D·Δθ/λ ≈ 0.28 × 0.67 / 1.55×10⁻⁶ ≈ **1.2×10⁵ per axis**.
  - That is a shortfall of ~240× per axis and ~6×10⁴ in 2D. No lens after the AOD can change it.
- **Options, and why each fails.**
  - Expand the AOD beam to 28 cm: the field shrinks to ±2 mm.
  - Keep the 1 m field: each spot grows to ~2 mm, so NA ≈ 5×10⁻⁴. Reaching ~10¹⁴ W/cm² at 0.3 ps would then need ~0.5 J per pulse.
  - Use galvos instead: they reach ~10× less étendue than needed, at kHz rates, not 50–80 kHz.
- **Other defects in the stated design:**
  - **Depth range.** An AO-lens range of 0.2–0.4 m cannot cover the 0.8–2.8 m throw that a 1.8 m-tall volume under a 2.7 m ceiling needs. At 2.6 m, NA ≈ 0.05: intensity ÷ 3–4 and hazard zone ×2 (finding 11).
  - **Dispersion.** The AOD's angular dispersion for an 8 nm (0.3 ps) bandwidth smears the focus ~3× beyond the diffraction limit at 0.1 rad deflection unless it is compensated.
  - **Lens quality.** A Fresnel doublet is not diffraction-limited at NA 0.1 over a ±20° field. A lens that is would be a telescope-class objective, not a startup part.
  - **No optical simulation exists** (no E8 optics).

**Fix:**
- Write an étendue budget: (spot size) × (resolvable spots) = field.
- A room-scale volume needs a different addressing concept: slow, large-aperture steering, many tiled sub-volumes, or far fewer and larger sparks (ns, mJ). Each of these changes the brightness, noise and chemistry budget.
- A desk-scale volume (≈ 5–10 cm field) is compatible with AODs and would be an honest Phase-1 target.
- Regrade R10 as NOT MET.

### 17. Major: the laser source and pulse-on-demand timing are beyond "exists today"

**Claim:** a 1550 nm Er fibre CPA or Yb-pumped OPCPA, 20–40 W, 10–40 µJ, pulse-on-demand on a 25 ns grid, with a fs seed plus a ps heater.

**Why weak:**
- To my knowledge, commercial 1.5 µm ultrafast sources are ≤ ~10 W. 1.5 µm OPCPA at tens of W is research-grade.
- The LIDAR cost-down analogy fails: LIDAR sources are ns, low-energy lasers.
- Irregular pulse-on-demand in fibre amplifiers makes pulse energy depend on the preceding interval. For example, the first pulses after the 13 % idle time at the end of each E6c frame are larger. That directly feeds the amplitude-jitter floors in findings 6 and 7.
- Two synchronised amplifiers (seed plus heater) double this problem.
- With E3's absorption (finding 4), the required power may be 30–100 W.

**Fix:**
- Cite a real source or quantify the extrapolation.
- Add amplifier gain dynamics to the timing and noise model.
- Count the source as the main R10 risk.

---

## G. Colour, perception, consistency

### 18. Minor: the "near-cyan azure" hue, the "dim warm workshop", and a few inconsistencies

**Colour.**
- E11 applies *complete* Bradford adaptation to a 2700 K illuminant. At 2–10 lux, CIECAM02 gives a degree of adaptation D ≈ 0.7–0.8, and mesopic vision desaturates colour. The perceived hue will be less saturated than hue 202–213° suggests.
- The plasma line strengths are themselves labelled estimates.

**Film lighting.** "The film's workshop is itself warm-lit" and dim contradicts R4 DR-8 and DR-14, which put the film lab at 50–150 lux (5–15 cd/m² background). The required 2–10 lux room is an environment constraint on the user.

**Inconsistencies:**
- E6c and the demo use 3 mm and 2 mm pitch, while the budget is computed at 1 mm pitch (the demo's 542 k voxels/s is computed for n = 9038 points but it renders 4519).
- R9 claims "2 mm pitch ✓".
- T2 still says −26 dB.

**Fix:**
- Use CIECAM02 with D computed from the adapting luminance, and describe the hue as "bluish-white to azure in a dim warm room".
- Make pitch a single parameter across E6c, E7, E10 and the demo.

---

## H. Grading (question 6)

### 19. Critical: several FINAL_VERDICT grades do not survive the pre-registered rule

"MET only if a simulation or a cited measurement supports it with numbers."

| Req | Lab grade | Red-team grade | Reason |
|---|---|---|---|
| R1, R2, R3, R5 | MET | **MET** | Agreed. T1 and in-volume isotropic emission are sound. |
| R4 Projector only | MET | **PARTIAL** | Needs a dim (≤ 10 lux), warm-lit room (a room condition) and a separate 19" laser rack. |
| R6 Content | PARTIAL | **PARTIAL** | Agreed. Add that dithered video stays at random-order noise (finding 7). |
| R7 Touch | MET | **PARTIAL** | The criterion says the hologram must render correctly around the hand. It never can within a 45–90 mm sphere of any hand (finding 11) or ~170 mm of any head. Ceiling-only apertures shadow up to ~20 % of content under a leaning user. |
| R8 Safe everyday | PARTIAL (laser ✓, UV ✓, hearing ✓) | **NOT MET** | Laser: Class 4; the certification path contradicts R3; the margin allows 2× MPE (findings 11, 14). UV: unverified, 1–11× margin (finding 13). Noise: 50–58 dB(A) at the user plus the air handler, against 35 dB(A) (findings 7, 8). Air: depends on implausible 90 % capture (finding 9). |
| R9 Quality | PARTIAL | **PARTIAL** | Agreed. η is unmeasured (±30×), so even the dim-lab brightness is a model extrapolation (finding 3). |
| R10 Buildable | MET | **NOT MET** | The scanner violates étendue by ~250× per axis. No depth coverage. The source is beyond commercial parts (findings 16, 17). |

**Result: 4 MET, 4 PARTIAL, 2 NOT MET**, against the lab's 7 / 3 / 0.

- The lab's decision not to ping the owner is correct.
- The headline sentence "can be engineered on paper with known physics and within safety limits" is **not supported**. Neither the "engineered" part (R10) nor the "within safety limits" part (R8) holds as designed.

**Fix:**
- Adopt the corrected scorecard.
- Change the one-paragraph answer to say which parts are physics-limited (T1, T2, colour), which are engineering-open (scanner, source, capture), and which are regulatory (Class 4).

---

## What holds up (so the owner knows what is solid)

- **T1** (line of sight, touch lemma) and the **E1/E2 kills** are correct. Rayleigh 215 W per mm³ voxel at 100 cd/m², coherent side-emission suppression, acousto-optic reach and microwave breakdown were all re-checked.
- **The trilemma framing** (lumens per J against reactive molecules per J against audible volume per J) is the right way to pose the problem. The audible floor is robust, because it is the thermal-monopole law (finding 5).
- **Subsonic multi-channel tracing** is genuine physics and the best noise lever. It is just content-dependent (finding 7).
- The lab caught its own direct-field over-claim, and its "film-exact is not reachable" conclusion is sound.

## Overall assessment

The science half of this work is good:
- The impossibility theorem.
- The identification of air plasma as the only medium-free emitter.
- The trilemma as the governing budget.
- The noise physics, once corrected.

The engineering and safety half over-claims. Three problems each independently break "buildable and safe for everyday use":

1. **The addressing optics cannot exist as specified.** They violate étendue by ~250× per axis, and no alternative has been costed.
2. **The device is a Class 4 open-beam laser.** The lab's own safety notes rule out the certification path it claims, and the interlock margins as parameterised allow about 2× the MPE.
3. **The "quiet" and "clean" numbers depend on idealisations** that fail for real content or real rooms:
   - E6/E6b point ears.
   - E6c smooth rings.
   - 90 % capture from a ceiling sink 1–2.6 m away.
   - A UV check weighted at 337 nm only.

**The two decisive plasma numbers are unmeasured.** Luminous efficacy (±30×) and speciation or Y (±10×) are not measured anywhere in the literature the lab cites.

**What an honest statement supports today:**
- A **desk-scale, supervised-venue, dim-room research demonstrator** (≈ 5–10 cm field, AOD-compatible, Class 4 under a variance) is a sound Phase-1 experiment for measuring X1, X2, X5 and the acoustic claims.
- A room-scale, home-use "Iron Man" projector is not supported by this design.

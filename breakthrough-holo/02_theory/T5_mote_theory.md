# T5: Theory of the MOTE route (light-held, self-emitting micro-motes)

**Route.** The projector dispenses motes of radius a ≈ 1–5 µm. Infrared photophoretic beams hold each mote and move it along the strokes of the image fast enough for persistence of vision. The mote makes its own light: a phosphor pumped by a µW violet beam, or upconversion pumped at 980 nm. T1 left two ways to put light at a point in open air: plasma (Phase 1–2) or matter at the point. This is the second way, and it avoids plasma's walls of ozone, NO₂, UV and noise.


> **v2 correction box (after red team 4; numbers below this box are v1 unless marked).** Each correction was re-derived or recomputed independently before acceptance. Details: `07_mote_route/RESULTS.md` §1.
> - **§1, force.** ρ and T are taken at the same state (ρT = p/R), which removes a spurious ×T_f/T₀ (+25 %). The creep prefactor corresponds to C_s = 9/8, so **C_ph ∈ [0.67, 1.04]**, not [1, 1.56].
> - **§1, J₁.** J₁ = A/2 only for skin-deep absorption (α·a ≳ 30). The heat-force identity holds per unit of J₁/A. The governing figure of merit is **FOM = (J₁/A)/(k_eff + 2k_g)**.
>   - 6.1 m·K/W in v1;
>   - 4.4–5.3 for engineered aerogel / core–shell motes (none made yet);
>   - 2.0 for a plausible-optimistic mote;
>   - 0.4 for dense motes.
> - **§2, speeds.** Corrected heat-limited speeds are **0.4–0.9 m/s** for engineered motes (a = 1–2.5 µm, 450 K hot face) and 0.2–0.4 m/s for plausible-optimistic ones.
> - **§3, lateral efficiency.** The linear η_lat = 0.75 a/w is valid only for a ≪ w. The exact LG01 integral gives η = 0.25 / 0.37 / 0.12 at a/w = 0.16 / 0.39 / 0.78.
> - **§8–9, beams and loop.** Flat-top push beams need R_ft ≥ 20 µm so that their edges are realisable, and a ≥ 20–50 kHz loop. Passive LG01 pairs need no fast loop.
> - **§6, safety.** Class 1 needs scheduler-enforced no-overlap and a certified fault shutdown. Per-beam compliance is not enough.
> - **§10, channels.** Channels are étendue-tiled. The corrected designed-lab counts are ~10³ (accent) to ~10⁴ (film density).

Code: `07_mote_route/mote/` (physics, safety, budget, feedback). Validation: `07_mote_route/validation/validate_mote.py` (26/26). Results: `07_mote_route/RESULTS.md`.

## 1. Heat–force identity

The ΔT-photophoretic force on a sphere is given by the continuum formula (Yalamov 1976; Reed 1977):

  F = C_ph · 9π μ² a I J₁ / (2 ρ T₀ (k_p + 2k_g)) · S(Kn)

- The slip factor is S = [(1 + 3c_m Kn)(1 + 2c_t Kn k_p/(k_p + 2k_g))]⁻¹, with c_m = 1.14 and c_t = 2.18.
- C_ph = 1 corresponds to Maxwell's creep coefficient (c_s = 3/4). Kinetic theory gives up to 1.56.
- For an opaque mote the lit face holds all the heat, so J₁ = A/2, where A is the absorptance.

The absorbed power is P = A π a² I. In the continuum, the mean heating is ΔT = P / (4π a k_g). Eliminating I gives

  **F = 18π μ² J₁′ k_g ΔT / (ρ T₀ (k_p + 2k_g))**   (J₁′ = J₁/A ≤ 1/2)

**The force per kelvin of mean mote heating does not depend on the mote size.** It is 4.5×10⁻¹² N/K at k_p = 0.1 W/m/K and 9.5×10⁻¹² N/K at k_p = 0.02 (validation M11).

Consequences:
- Levitating a 2.5 µm mote needs only ≈ 0.2 K of heating.
- Pushing it through air at 1 m/s (Stokes drag 8.5×10⁻¹⁰ N) needs ≈ 190 K (k_p = 0.1).
- Heat, not laser power, sets how fast a mote can move.

## 2. Speed law

Dividing by the Stokes drag 6π μ a v:

  v_max = 3 μ J₁′ k_g ΔT_max η / (ρ T₀ a (k_p + 2k_g) h)

- η is the fraction of the ideal force the trap geometry delivers in the wanted direction.
- h is the heat multiplier: total absorbed power per unit of net force.

**Speed rises as 1/a and as ΔT_max/(k_p + 2k_g).** The second factor has a floor, because 2k_g ≈ 0.05–0.06 W/m/K even for an aerogel mote.

Heat-limited maximum speeds at T_mote ≤ 450 K, still air, k_p = 0.02 (budget.max_speed_heat):

| a | push4 (h = 3) | push6 (h = √3) | lateral2, 100 mm heads | lateral2, 300 mm heads |
|---|---|---|---|---|
| 1 µm | 1.58 m/s | 2.73 m/s | 0.18 m/s | 0.55 m/s |
| 2.5 µm | 0.78 | 1.36 | 0.23 | 0.69 |
| 5 µm | 0.42 | 0.73 | 0.25 | 0.74 |

**BYU consistency.** BYU's record of 1.83 m/s (Smalley et al., Nature 2018; a ≈ 5 µm char particle) needs ΔT ≈ 160–400 K at η = 1 (validation M22). The model reproduces a real display without exotic assumptions. It also implies that the aberrated single-beam trap BYU used reaches η ≳ 0.4. At η ≪ 0.4 the particle would have had to run at well over 1000 K.

## 3. Lateral force from an intensity gradient, and why long throw hurts

Take an opaque sphere lit along z, with intensity gradient g = d ln I/dx across it. The first moments of the absorbed flux over the lit hemisphere give

  F_x / F_z = (3/8) g a   (validation M13)

- On the inner flank of a doughnut (LG01) beam, g ≈ 2/w, so **η_lat = 0.75 a/w**.
- At room throw the focus is wide: w = M² λ d/(π R). At 1550 nm, 1.5 m throw and a 100 mm head, w = 19 µm.
- So a single-head gradient trap wastes most of its heat, with η_lat ≈ 0.04–0.2.
- Its best speed at a 100 mm aperture is 0.25 m/s (**P22 confirmed**, predicted 0.1–0.5).
- A 300 mm aperture triples this, to 0.55–0.74 m/s.

## 4. The multi-head push trap

Beams from several heads each push along their own axis, which gives η = 1. A controller chooses the non-negative beam forces f_i with Σ f_i d_i = F.

| Layout | Minimum Σf/F, worst direction | Mean | Largest single beam |
|---|---|---|---|
| Tetrahedral, 4 heads | 3 | 2.23 | 1.22 F |
| Octahedral, 6 heads | √3 | 1.5 | 1.0 F |

The tetrahedral minimum is Σf/F = −3 min_i(u·d_i). This closed form was checked against a linear programme (validation M14).

Push beams are laterally unstable: a Gaussian or flat-top edge pushes the mote out. Holding the mote needs **active position feedback**; see §9.

## 5. Light: heat per lumen decides the emitter

A mote that must emit φ_m lumens absorbs φ_m / η_lm of pump power, and part of that becomes heat.

| Emitter | lm per absorbed W | Heat per lm | Pump Class 1 AEL | Notes |
|---|---|---|---|---|
| Eu²⁺ cyan phosphor (BaSi₂O₂N₂, 497 nm) pumped at 405 nm | ≈ 150 | ≈ 4.5 mW/lm | **39 µW** (photochemical) | Iron-Man cyan. The pump AEL binds |
| Yb/Er upconversion, 980 nm pump | ≈ 74 at saturation (R6: 60–120) | ≈ 12 mW/lm | 1.43 mW | Green/red only. Weak absorption: A = 1–6 % per mote |
| White scatterer lit by a visible beam | none absorbed | — | 0.39 mW | **Rejected.** Forward diffraction (Babinet) sends as much light to the walls as to the viewers, so the room shows a glow |
| Incandescent mote | 0.1–3 | ≥ 300 mW/lm | — | **Rejected** (R6). It burns in milliseconds and melts the heat budget |

At film density one mote must give ≈ 1.7 mlm. With the cyan phosphor that is ≈ 12 µW absorbed and only ≈ 5 µW of heat, a few K. **The emitter's heat is small; the trap sets the heat budget.**

## 6. Laser safety scales with head aperture

- **Per beam:** P_beam = I_mote · π w²/2 · (profile factor). The required intensity I_mote does not depend on mote size (§1–2). So each beam's power scales as w², i.e. as (λ d/R)².
- **Exit window:** all beams overlap there. Class 1 then needs P_head · 2 (r_ap/R)² ≤ AEL, so the allowed head power grows as R². At 1550 nm this is 4.1 W for a 100 mm head and 37 W for a 300 mm head.
- **Obstruction interlock:** when a finger or sleeve enters a focus, the beam is cut. A 100 µs cut limits the dose at the focus to ≈ 0.02 J/cm², far below the 1 J/cm² limit for ≤ 10 s at 1550 nm. This holds even under ICNIRP's strict small-beam skin rule (R7 S3).
- **Binding term:** the 405 nm pump's 39 µW per-beam limit binds most often (§8).

**Result (M1 atlas, 1550 nm trap):** at film density every beam and every exit window can be Class 1. The film-density design uses 0.87 mW per trap beam, 1.8 W of 1550 nm in total, and 36 µW per pump beam. (**P24:** Class 1 holds, but the total is 1.8 W, below the predicted 2–15 W.)

## 7. How many motes

N = S f / (v · duty). Each mote draws v·duty metres of stroke per second, and the image needs S·f.

At 30 Hz, 30 m of strokes and 1.1 m/s, N ≈ 1100–1200. The total trap power follows as

  P_trap ≈ N · h_mean · I(v + u) · π w²/2 ∝ S f h_mean (1 + u/v) w².

Slow motes cost motes, not heat. Fast motes cost heat.

## 8. Focus tracking: the depth law

A beam's focus must follow its mote along the beam axis. A focus loop of bandwidth B lags a ramp by v/(2πB). Keeping that lag within z_R/2 = π w²/(2λ) gives

  **P_beam · B ≥ I_mote · λ · v · k / (2π)**   (k = profile factor)

**Trap beam** (I ≈ 6×10⁶ W/m², 1550 nm, v ≈ 1.1 m/s, k = 2): P·B ≥ 3.5 W·Hz. A 1 kHz focus loop needs 3.5 mW per beam, still under Class 1. The trap is not the problem.

**Pump beam** (cyan phosphor, a = 1 µm, I_p ≈ 5.5×10⁶ W/m², 405 nm): P·B ≥ 0.39 W·Hz. Within the 39 µW AEL this needs **B ≥ 10 kHz** (M3: ≈ 17 kHz). The alternatives:
- larger motes, which lower I_p as 1/a²;
- the 980 nm upconversion pump, whose AEL is 36× higher: ≈ 3 kHz;
- splitting the pump across heads, each beam assessed separately.

## 9. Feedback law (M2)

The controller must correct a gust u before the mote leaves the flat-top of radius R_ft. This needs a loop bandwidth ω_c ≳ 2u/R_ft.

Time-domain simulation (a = 1 µm, R_ft = 10 µm, 1 m/s circle, 0.1 m/s draft plus OU gusts; 32 motes × 0.2 s per point):

| Gust σ | Lost at 5 kHz | 10 kHz | 15 kHz | 20 kHz | 30 kHz | 50 kHz |
|---|---|---|---|---|---|---|
| 0.05 m/s | 100 % | 0 | 0 | 0 | 0 | 0 |
| 0.1 m/s | 100 % | 31 % | 0 | 0 | 0 | 0 |
| 0.2 m/s | 100 % | 100 % | 53 % | 0 | 0 | 0 |

Other findings:
- **Sensing:** position noise must be ≲ 0.5 µm per axis at the loop rate. At 2 µm every mote was lost.
- **Mote size:** 2.5 µm motes need ≥ 50 kHz with this controller, because their inertia time τ_p grows as a².
- **Controller variant:** a naive disturbance observer made things worse by differentiating sensor noise, so this remains a controller-design task.
- **P23** (2–20 kHz): consistent at room gusts (15–20 kHz). At 2× gusts it needs 20–30 kHz. The simulations cannot certify "< 1 %/min" statistically; they show zero losses over 6.4 mote-seconds per point.

## 10. The steering wall

Each mote needs one beam from every head (push) or from each of the two heads (lateral2). So **steering channels = heads × S f/(v · duty)**.

| Target | Motes N | Channels (push4) |
|---|---|---|
| Accent (1 m) | ≈ 40 | 150 |
| Sketch (5 m) | ≈ 190 | 750 |
| Film density (30 m) | ≈ 1100 | 4500 |

Per channel (M3), at a 300 mm head:
- **Lateral positions:** ≈ 78 000 resolvable spots per axis over a 1 m field. That exceeds even a 30 mm galvo pair (≈ 27 000), so channels need tiling with hand-over.
- **Pointing:** ≈ 0.6 µrad precision (trap) and ≈ 0.3 µrad (pump).
- **Focus:** 2–17 kHz tracking over ±0.25 m.
- **Loop rate:** ≈ 20 kHz intensity and sensing.

Every one of these functions exists in some device today: galvo, MEMS, acousto-optic lens, quadrant detector. What does not exist is thousands of channels combining all of them. **This is an engineering wall, not a physics wall.**

## 11. What only a bench can settle (value-of-information order)

1. **Single-beam 3D trapping at room throw.** Does a BYU-type aberrated trap hold a 3–5 µm mote at NA ≈ 0.1 and 1.5 m, and what η? If η ≥ 0.5 the channel count drops 4× (one head).
2. **Mote engineering.** A composite of k_p ≲ 0.05, absorbing at 1550 nm, with a phosphor shell, surviving 450 K. Plus the photophoretic force per kelvin, to settle C_ph ∈ [1, 1.56].
3. **Push-trap feedback.** Closing the loop at ≥ 20 kHz on one mote with four beams.
4. **Phosphor at kW/cm²-class pump intensity.** Saturation and thermal quenching of the cyan phosphor on a hot mote.

# Idea round 3: can anything beat B9? (independent theorist report, Opus)

*Written 2026-10-01. I read `IDEA_ROUND_3_BRIEF.md`, `T7_gaussian_voxels.md`, `T6_unlock_theory.md` (§1–3c), `05_reviews/red_team_6_lcsv.md` (summary and verdicts), `05_reviews/IDEA_ROUND_1_SYNTHESIS.md`, `idea_round_2_opus.md`, `idea_round_2_sonnet.md`, `07_mote_route/R7_mote_safety.md` (§2–3), `07_mote_route/R5_optical_trap_displays.md` (speed rows), `07_mote_route/mote/physics.py`, and `m18c_vector_pin.py`. I edited no repository file except this one.*

*Scratch scripts (not committed), in the session scratchpad: `r3_numbers.py` (every closed-form number below; imports `mote/physics.py` read-only) and `r3_profile.py` (a copy of `m18c.simulate` in follow mode with the spot profile as a parameter; imports `m18c`, `m18b` and `rt6_check` read-only). Web searches used: 5 of 10.*

**Tags.** [MEASURED] = a documented fact, with its source. [DERIVED] = derived here from stated physics. [SIM] = from my scratch run of the repo's validated loop model. [ESTIMATE] = an order-of-magnitude judgement. [SPECULATIVE] = an untested idea. "recalled" = from memory, not re-checked this session.

---

## 0. Verdict in one screen

1. **No single physical mechanism beats B9 by ≥ 10×.** Three physics floors hold:
   - **Force per watt in air.** Thermal creep sets I_unit ≥ ~2.7×10⁶ W/m² per m/s even for an ideal skin absorber (k_p → 0). With slip at 1 µm that is ≥ 3.7×10⁶. Today's mote is at 7.3×10⁶, so the most a better mote can give is ×2. Every other per-particle force in air that I checked is weaker per watt (from ×0.4 for Δα down to ×2×10⁻⁴ for radiation pressure), runs out of propellant within ms to s, or needs fields above human perception (§3).
   - **The ~10 mW per pupil is physical, not only a convention.** At 1.4–1.8 µm a cornea placed at a focus warms by ≈ 0.7 K/mW whatever the NA, because water absorption (α ≈ 10³ m⁻¹) spreads the heat over ~1 mm [DERIVED/ESTIMATE]. Longer-wavelength water bands concentrate the heat and make small foci *worse*. 1550 nm is already the best band (§4).
   - **s ≥ 1 and h ≥ 1.** A pupil at a mote always collects that mote's own beams.
2. **B9 is not a physics bound. At T7's own mode count, it sits ~12× (realistic) to ~57× (floor) above the physics floors.** Written in modes, B9 is
   > **M_head ≥ (2·clip·os·L)² · h·s · I_unit · v_rel / (2π·AEL)** [DERIVED]
   
   The spot size drops out. T7's 6×10⁸ modes per head buy 4.9 cm/s because of four factors:
   - clip·os = 4.1× above étendue;
   - h·s = 7.1 (random head assignment, worst push direction);
   - FOM 5.3;
   - a 1.1 m field per head.
   
   None of these is a law of physics (§1).
3. **≥ 10× is reachable for *sketch-density* content by stacking four engineering levers (idea 1). None of them is ≥ 10× alone.** The levers are stacking-aware head assignment with heads placed against the room's mean flow, an ideal-skin mote, a follow-mode hologram loop at w ≈ 25–35 µm with better sensing, and a smaller field per head. Product: **v_rel,mean ≈ 0.5–1.4 m/s against 4.9 cm/s, i.e. ×10–30**, at T7's mode count once the field per head shrinks to ~0.6–0.8 m. Film density gets ×5–10. The heat bound B3 then binds at ~1–2.7 m/s (1 µm mote). Probability ≈ 0.35 [ESTIMATE].
4. **For moving foci B9 is the wrong bound (idea 2).** Class 1 at ≥ 1400 nm judges a moving focus as a pulse train through a stationary aperture (rule 1 plus rule 2, no C5; R7 row K6). The relevant invariant is the **energy per unit air-relative path**, E/L = h·I_unit·πw²/2 (28 mJ/m at w = 35 µm). The eye budget becomes a **crossing-rate budget**: ≤ 100 pupil crossings per second at w = 35 µm.
   - **POV motes may therefore move at 0.5–1.2 m/s (heat-limited) under passive Class 1**, with a scan-stall safeguard, which is the base standard's own scanning provision. That is ×10–25 on v_rel.
   - The draft enters only as (1 + u/v_m).
   - The condition is f_r·s′·d_ap ≤ 2·AEL/(π w² h I_unit), i.e. **w ≤ 31–53 µm at 30 Hz refresh**.
   - The price is per-mote steered channels (~6 per mote), not physics. This overturns T7's "fast animation is excluded under passive Class 1" as a *safety* statement. It is still excluded for *holographic* static voxels, where content speed is ≲ (C·f²/k²)^⅓ ≈ 0.07–0.2 m/s at 5 kHz (§2.2).
5. **The only ≥ 10× attack on the draft itself is to stop fighting the air and ride it (idea 3).** A push–pull, wind-tunnel-grade laminar column (Tu 0.1–1 %) carries the motes. Then v_rel ≈ U_j·Tu + steering ≈ 0.3–3 mm/s against the 48 mm/s of a still room. It is physically sound, but it changes the product: an air outlet and inlet, mote recirculation of ~3×10⁴ motes/s, and wake dropouts behind hands. [SPECULATIVE], probability ≈ 0.15.
6. **What must break for a *free* ≥ 10× (no extra modes, channels or air handling)?** Either the corneal limit (physiology plus law; no) or thermal creep's force per watt (gas kinetics; no). Every ≥ 10× route therefore pays in **scheduling + modes**, **steered channels**, or **air handling**.

---

## 1. The B9 ledger: where the 5 cm/s comes from

**B9 in modes** [DERIVED]. T7 gives
- M_head = (2·clip·os·L/(πw))²;
- B9: v = 2·AEL/(πw²·h·s·I_unit).

Eliminating w:

> M_head = (2·clip·os·L)² · h·s · I_unit · v / (2π·AEL), and at the étendue floor M_min = L²·h·s·I_unit·v/(2·AEL).

**Check.** T7 values (clip 1.2, os 1.5, L = √1.2 m, h·s 7.1, I_unit 7.3×10⁶, AEL 10 mW) give 1.28×10¹⁰ modes per head per m/s. At 6.1×10⁸ that is 4.8 cm/s, matching T7's 4.9 cm/s (`r3_numbers.py` §A).

**So a faster mote costs modes linearly, whatever the spot size.** Shrinking w only spends modes. "Buildable spot sizes" really means "buildable mode counts plus a loop that can hold the smaller spot."

| Factor in B9 | T7 value | Physics floor | Lever that moves it | Realistic gain | Floor gain | Cost |
|---|---|---|---|---|---|---|
| I_unit (W/m² per m/s) | 7.3×10⁶ (FOM 5.3, slip ×1.39) | ≥ 2.7×10⁶ no-slip, ≥ 3.7×10⁶ at 1 µm (FOM ≤ 9.7 with J₁/A ≤ 0.5, k_p → 0) [DERIVED, `physics.py`] | ideal island-skin mote, k_eff ≤ 0.015 | ×1.4 | ×2.0 | unmade mote (already the program's gate) |
| AEL per pupil | 10 mW, 3.5 mm | ~10–30 mW is physiological at 1.4–1.8 µm (§4) | none | ×1 | ×1 | — |
| h (push overhead) | 2 (h_worst) | 1 | heads placed against the room's *persistent* mean flow; H14 h_mean 1.28 | ×1.5 | ×2 | installation survey |
| s (pupil stacking) | 3.4 sketch, 5.1 film (random heads, M17) | 1 | stacking-aware head assignment in the field checker; s ∝ w via tube length | ×2–2.8 sketch, ×1.5–2 film | ×3.4–5 | certified scheduler (exists anyway) |
| clip·os (modes above étendue) | 4.1 | ~1.5–2 | tighter clip, field stop, foveated tiles (I7) | ×2 | ×4.1 | optics design |
| L² (field per head) | 1.2 m² | the image's own size | heads address only the content zone (a ~0.6 m desk-scale hologram: ×3.3) | scope | scope | content restricted to a zone |

The **product of the non-scope levers is ×12 (realistic) to ×57 (floor)** at equal modes and equal field. Including the field-per-head scope lever, the realistic figure is ×40.

The remaining question is whether the loop can hold the smaller spots that this budget implies. That is idea 1's simulation.

---

## 2. Ranked ideas

| # | Idea | Gain on v_rel vs B9 (4.9–10 cm/s) | Physics status | Cost / risk | P(real) |
|---|---|---|---|---|---|
| 1 | **Stacked levers at equal modes**: stacking-aware head assignment and mean-flow-aligned heads (h·s 7.1 → 1.5–2), ideal-skin mote (×1.4), follow-mode hologram loop at w 25–35 µm with σ_n ≤ 2–4 µm, field per head ~0.6–0.8 m | **×10–30 sketch, ×5–10 film** (0.5–1.4 m/s mean); heat-capped near 1–2.7 m/s | DERIVED + SIM | scheduler optimisation; unmade mote; the loop is unverified at office authority; modes ×2–3 unless the field shrinks | 0.35 |
| 2 | **Crossing-rate bound for moving foci**: POV motes and moving content are judged per pupil crossing (rule 1 + rule 2), not as a static focus | **×10–25 for v_rel and content speed** under passive Class 1 (+ stall safeguard); draft-immune to (1 + u/v_m) | DERIVED; standards basis per R7 K6 [secondary] | ~6 steered channels per POV mote (≈ 1,600 for a sketch at 1 m/s); no gain for still-room static voxels (×0.5) | 0.5 (classification), 0.25 (affordable channels) |
| 3 | **Push–pull laminar co-flow column** ("air conveyor"): motes ride a Tu 0.1–1 % column at 0.3 m/s; the image is drawn by flowing motes | **×15–100 on draft-driven v_rel** in the column | DERIVED/ESTIMATE; Tu from wind-tunnel practice [MEASURED] | outlet + inlet hardware, ~3×10⁴ motes/s recirculated, hand wakes, 30–40 dB(A) fan, owner's "no gas" reading | 0.15 |
| 4 | **Electrostatic common mode**: electret-charged motes plus a 1.4–5.7 kV/m room field cancel the spatially smooth mean flow U | ×1.5–2.3 on mean v_rel (home / quiet office) | DERIVED; perception 10–45 kV/m [MEASURED] | electret motes (~10⁻¹⁴ C), charge decay τ ≈ 15 min, electrodes in table and ceiling | 0.3 |
| 5 | **Passively dipped spots** (incoherent LG00 + LG01): remove the Gaussian runaway | ×1.2–2 in eye budget at σ_n 1.5 µm in quiet rooms; predicted ×3–5 in drafty rooms at low noise; ×1 at σ_n 4 µm | SIM (quiet rooms); scaling prediction (offices) | ×2 power per spot and ×2–3 modes per spot | 0.3 |
| 6 | **Sensing-noise lever** inside idea 1 (runaway model: w_min ∝ √(σ_n·F·τ)) | ×1.2–1.7 when σ_n drops 4 → 1.5 µm (sim; folded into idea 1) | SIM | bigger collection optics or receiver shadow sensing (T6 I6) | 0.5 |

### 2.1 Idea 1: stacked levers at equal modes (the B9 ledger cashed in)

**(a) Head assignment and placement: h·s 7.1 → 1.5–2** [DERIVED/ESTIMATE]

B9 is a *mean-power* bound, so two parts of it are too pessimistic.

- **h.** B9 uses h_worst = 2. For a 10–100 s average, the relevant h is the time mean over the draft-direction distribution: h_mean = 1.36 (H10) or 1.28 (H14). If the persistent mean flow at the image (a convection loop, a thermal plume) is opposed by a head placed on its axis, h → 1.05–1.15.
- **s.** M17's 3.4 (sketch) and 5.1 (film) assume *random* head choice.
  - The extra beyond 1 comes from other motes' beams whose "pupil tube" passes through the worst point. That tube has length ±z_c = ±d_ap/(2θ), θ = λ/(πw): ±18 cm at w = 50 µm, ±12 cm at 35 µm.
  - The time-mean count per tube is n·V_c with V_c = 4π(d_ap/2)³/θ = 6.8 cm³ at 50 µm and 4.8 cm³ at 35 µm. For a sketch, n·V_c = 0.44–0.63; for film density, 1.75–2.5 (`r3_numbers.py` §A).
  - With 10–14 heads to choose 3 from, a scheduler that minimises the summed power at every mote's own pupil can plausibly reach **s ≈ 1.2–1.5 for a sketch** [ESTIMATE].
  - Film density has too many motes per tube; ~2–3 is more realistic.
  - Because V_c ∝ w, **s also falls when w falls.**
- **Product.** h·s ≈ 1.4–2 (sketch) or 2.5–3.5 (film), against 7.1: **×3.5–5 and ×2–2.8** at equal spot size and modes.

**(b) Mote: FOM 5.3 → 7–8** (island skin, k_eff ≈ 0.012–0.02). That is ×1.3–1.5. The ceiling is ×2. This is known (T7 §2, Sonnet round 2).

**(c) Spot size held by the loop: what does the follow-mode hologram loop really need?** [SIM]

I reran RT6/m18c's validated machinery in follow mode with my scratch copy `r3_profile.py`:
- MEMS phase modulator at 5 kHz, 2 frames latency, 30 µs lag;
- authority 5.4σ;
- 30 motes × 5 s per point, i.e. 144 mote-s;
- loss when the offset from the spot centre exceeds 1.5w, as in m18c.

| Room | σ_n (sensing) | Gaussian w, holds / loses | Dipped spot (LG00:LG01 = 1:1), holds | r_p99.9 |
|---|---|---|---|---|
| still (σ_u 0.03, L 3 cm) | 4 µm | 30 µm and 25 µm 0/30; **20 µm 8/30 lost** | 20 and 25 µm 0/30 | 16–18 µm |
| quiet office (U 0.1) | 4 µm | 25 µm 0/30; **20 µm 19/30 lost** | 20 and 25 µm 0/30 | 16–19 µm |
| still | 1.5 µm | **15 µm 8/30, 12 µm 21/30, 10 µm 30/30 lost** | **10 µm 0/30**, 12 and 15 µm 0/30 | 6–7 µm (dip), 7–9 (Gaussian) |
| quiet office | 1.5 µm | **15 µm 13/30, 12 µm 30/30 lost** | **10 µm 0/30**, 12 µm 0/30 | 6–7 µm |

(The dip's eye-equivalent Gaussian waist is √2·w, i.e. 14 µm for the 10 µm dip.)

Readings:
- **The follow-mode loop at 5 kHz holds a Gaussian at w ≈ 25 µm with T7's 4 µm sensing noise.** T7's design point is w = 51 µm. This is a short-run result. 0/30 in 144 mote-s bounds the loss rate only at ≲ 2×10⁻²/s, against the 10⁻⁴/s target, so RT7 must repeat it with m18c's long runs.
- m18c's own follow runs at 3 kHz lose at 35 µm. 5 kHz is therefore the threshold rate.
- **The runaway model predicts Gaussian w_min ∝ √(σ_n·F·τ)**, not ∝ σ_n. The runaway rate is F·4r/w² with r ≈ 4σ_n, and it must stay below ~1/τ_loop [DERIVED]. The sims show an even weaker noise dependence: cutting noise 4 → 1.5 µm moves w_min only from ~22 µm to an estimated ~17–20 µm (still/quiet rooms). The lower end is fixed by the Gaussian still losing 8–13/30 at 15 µm; the 20 µm, 1.5 µm-noise run had not finished when I wrote this. That is worth ×1.2–1.7 in B9. **Sensing noise is a weak lever on its own; loop rate and authority matter as much.**
- **Combined with B9 this gives the true loop-plus-eye bound** v_max ≈ √(C·Γ/(4·k·σ_n)), with C = 2·AEL/(π·h·s·I_unit) and Γ the loop rate. Here the loop must hold the authority that the drafts demand, which itself scales with v. Speed then rises only as the square root of every lever, so ×10 needs ×100 in the product C·Γ/σ_n, for example ×10 in C (geometry, mote, field) and ×10 in Γ/σ_n.

**(d) Field per head.** If heads address only the content zone (~0.6–0.8 m instead of 1.1 m), modes drop ×1.9–3.3. That pays for w 50 → 30 µm at T7's mode count.

**Cashed in.** The table gives the *eye-safety capacity* for a sketch, v = 4.9 cm/s × (50/w)² × (7.1/h·s) × (FOM/5.3). The loop holding these w is verified only up to quiet-office authority (~0.26 m/s). Spending the capacity on stronger drafts needs the office-authority loop check (below). Spending it on content motion is limited by B8 (§2.2).

| w | h·s | FOM | v_rel,mean | ×B9 | Modes per head at L = 1.1 m / L = 0.65 m |
|---|---|---|---|---|---|
| 35 µm | 2.0 | 7 | 0.47 m/s | ×9.6 | 1.3×10⁹ / 4.5×10⁸ |
| 30 µm | 1.75 | 7.5 | **0.78 m/s** | **×16** | 1.8×10⁹ / 6.2×10⁸ |
| 25 µm | 1.5 | 8 | 1.4 m/s | ×29 (heat-capped) | 2.5×10⁹ / 8.9×10⁸ |
| 30 µm, film | 3.0 | 7.5 | 0.46 m/s | ×9.4 | 1.8×10⁹ / 6.2×10⁸ |

**What still fails** [ESTIMATE]:
1. **Office authority.** My sims stop at σ_u = 0.03. At σ_u = 0.1 the authority is ×3 (U + 5.4σ ≈ 0.64 m/s), so the Gaussian runaway needs w_min ×√3 ≈ 1.7, or a 15 kHz loop. Dipped spots (idea 5) are the predicted fix there.
2. **Heat.** The hot face at office gust peaks is 429 K at 1 µm (T7), which is fine. Above ~1.5 m/s mean, ITO's 573 K binds.
3. **The ideal mote is unmade.** Without it, divide by 1.4.

**Verdict.** About ×10 for sketches by engineering alone, physically sound. It does not come free.

### 2.2 Idea 2: B9 is a static-focus bound; moving foci obey a crossing-rate bound

**Standards basis** [MEASURED, secondary, via R7 row K6]:
- for scanned or moving beams, each pass across the stationary aperture is a pulse;
- rule 1 (single pulse) and rule 2 (average over T) apply;
- C5 is not applied above 1400 nm;
- classification must hold under a scan or stall single fault.

The base standard's scanning-safeguard clause covers that fault (round 2 §7.1). Condition 3 places the aperture 100 mm from the apparent source; for scanned beams at 1400–1500 nm it uses 1 mm at 100 mm (IEC preview, search snippet).

**Invariant** [DERIVED]. For a mote moving through still air, the light needed per unit path is

> E/L = h·I_unit·πw²/2 = **57 mJ/m (w 50 µm) or 28 mJ/m (w 35 µm)**,

independent of speed: power ∝ v, dwell ∝ 1/v. One full pupil crossing deposits (E/L)·d_ap = **0.20 mJ or 0.10 mJ**.

**The budget is crossings, not speed:**
- **Long-term AEL (10 mW, 3.5 mm):** ≤ 50 crossings/s at 50 µm, ≤ 102 crossings/s at 35 µm.
- **0.35–10 s windows** (18 mJ·t^0.75 through 1.5·t^0.375 mm): ≥ 105–800 crossings/s. Not binding.
- **Rule 1** (≤ 8 mJ per pass in 1 mm): ≥ 40× margin.

**POV.** A point on a stroke is crossed f_r·s′ times per second (s′ counts other strokes in its tubes). The draft adds only the factor (1 + u/v_m). The condition is

> f_r · s′ · d_ap · (1 + u/v_m) ≤ 2·AEL/(π w² h I_unit), **independent of mote speed.**

So POV is passive-Class-1 for *any* v_m when w ≤ 53/46 µm (s′ 1.5, u/v_m 0/0.3) or ≤ 36/31 µm (s′ 3.3) at f_r = 30 Hz, and ≤ 37–22 µm at 60 Hz (`r3_numbers.py` §A).
- The mote speed is then capped by heat: mean rise 71 K at 1 m/s for a = 1 µm, hot face ~100 K; M16 found ~1.2 m/s.
- **v_rel = 0.5–1.2 m/s is ×10–25 over B9's 4.9 cm/s**, and an office draft of 0.2–0.3 m/s costs only ×1.2–1.3 more light.

**Stall fault.** A stuck focus at v_m = 1 m/s, w = 35 µm carries 28 mW, so the cut must come within ~0.29 s (8 mJ rule-1 budget). Use ≤ 100 ms. The tracking loop sees a stall in < 1 ms.

**Moving content made of static voxels** (rigid object motion). Time-averaged, a fixed pupil sees n·V_c motes' power, not s:
- sketch: s_eff ≈ 0.44–0.63 against 3.4;
- film: 1.75–2.5 against 5.1.

That is ×5–8 for sparse content and ×2–3 for dense content. But holographic voxels are also capped by B8 (v ≤ w·f/k). Combining B8 and B9:

> **v_content ≤ C^⅓ (f/k)^⅔** [DERIVED]: 7 cm/s at 5 kHz with T7's C (w* = 42 µm); 13 cm/s with idea 1's ×7 in C; ~0.2 m/s with time-averaging for sketches.

**So fast Iron-Man animation is excluded for the *holographic* architecture by the hologram rate, not by eye safety.** With steered POV channels it is eye-safe.

**What it does not do.** In a still room POV deposits ~2× the eye energy of static voxels for the same image (load f_r·d_ap ≈ 0.105 m/s equivalent at 30 Hz against u ≈ 0.048). It wins only when drafts exceed ~0.1 m/s or content moves.

**Cost.** RT6 counted ~6 steered beams per POV mote. A sketch needs N = S·f_r/(v·duty) ≈ 5 m × 30 Hz / (1 m/s × 0.57) ≈ 260 motes, i.e. ~1,600 channels. That is v4's (R10) cost structure: $1–8M at $0.7–5k per channel. Physics is not the obstacle.

**Verdict.** This is a genuine B9 loophole for moving foci. It corrects T7 §5 item 3 as a safety statement. Its value is content speed and draft immunity, not still-room cost.

### 2.3 Idea 3: ride the air (push–pull laminar co-flow column)

**Why it is the only ≥ 10× draft attack.** v_rel is the air speed *at the mote, relative to the mote*. If the motes move with a conditioned air column, v_rel is only the column's residual turbulence plus the steering the content needs.

**Numbers**
- **Column turbulence.** Column at U_j = 0.3 m/s, section 0.3 × 0.3 m. Wind-tunnel-grade conditioning (honeycomb, 2–3 screens, contraction ratio ≥ 9–25) gives a potential-core Tu ≈ 0.1 % [MEASURED: Brunel open-jet tunnel]. Air-curtain-grade jets have Tu ≤ 8 % in the core and ~20 % in the shear layer [MEASURED, search snippet]. The potential core is 4.7–7.7 D long [MEASURED, snippet], i.e. 1.4–2.3 m for D = 0.3 m.
  - At Tu 0.1–1 %: σ = 0.3–3 mm/s, mean |v_rel| ≈ 0.5–5 mm/s, authority U_rel + 5.4σ ≈ 2–16 mm/s.
  - Compare 48 mm/s mean and 210 mm/s authority in a still room. **Gain ×10–100.** At air-curtain-grade Tu 8 %, the gain collapses to ×1.2, so it lives or dies on conditioning.
- **Eye.** Holding power per focus scales with v_rel, so it is ≤ 1/10 of the still-room value. The visible illumination dominates. B9 is effectively retired inside the column.
- **Optics.** All motes in the core share U_j, so the foci pattern translates rigidly. Each head applies a common translation (fast steering mirror plus focus) as a sawtooth. The slow hologram adds and drops motes. That is cheaper than per-mote POV channels [ESTIMATE].
- **Mote flux.** A sketch needs ≈ f_r × (stroke length projected ⊥ flow)/δ ≈ 30 Hz × 3.2 m / 3 mm ≈ **3×10⁴ motes/s** through the image, recaptured at the inlet. At 99.9 % capture the room receives ~30 motes/s, ~70 ng/h of 1 µm ITO-aerogel. Negligible mass, but respirable (R3/R8 toxicology, as for every route).
- **Air handling.** 0.027 m³/s (97 m³/h) at 30–60 Pa: 30–40 dB(A) unless silenced. ≤ 30 dB(A) needs large slow fans and a lined plenum [ESTIMATE]. The air at room temperature in the column is a light breeze on the hands. ASHRAE-type draft discomfort is mostly about cooler air on the neck [ESTIMATE].
- **Cross-drafts.** Room drafts (0.05–0.2 m/s) push on a free jet. Push–pull geometry (an inlet facing the outlet) keeps the column. The core shrinks by ~0.1 per unit length from shear-layer growth (0.18 m usable at 0.6 m) [ESTIMATE].
- **Hands.** A hand in the column leaves a wake with u′ ≈ 0.1–0.2·U_j = 3–6 cm/s for ~5–10 hand widths downstream: a still-room-like zone where idea 1's budget applies. Upstream, the flow deflects around the hand.

**Verdict.** Physically sound, ×10–100 on the draft term. But it is a different product: a holo-table inlet with a ceiling or overhead outlet, and a mote fountain. It may collide with the owner's "no fog or gas" reading, though it is clean air. [SPECULATIVE], P ≈ 0.15.

### 2.4 Idea 4: electrostatic common mode against the mean flow [SPECULATIVE]

**Charge** [DERIVED]:
- A 1 µm mote carrying an electret charge at a surface field of ~10⁸ V/m (micro-gap breakdown scale [ESTIMATE]) holds q ≈ 1.1×10⁻¹⁴ C (~100 V).
- The electron-emission limit, ~9×10⁸ V/m (Hinds, recalled), would allow ×9.
- **Photo-charging fails:** photoemission stops at ~4 V, giving q = 4.5×10⁻¹⁶ C. Holding even 5 cm/s would then need 36 kV/m.

**Field needed.** Cancelling a spatially smooth mean flow U = 0.05 / 0.1 / 0.2 m/s needs **E = 1.4 / 2.8 / 5.7 kV/m**. That is below the 10–45 kV/m human detection range for DC fields [MEASURED: ICNIRP; EMF-portal; Kursawe et al. 2021]. WHO and ICNIRP find no adverse effect apart from microshocks.

**Gain.** Mean |u| falls from ≈ 0.07 to 0.048 m/s (home), ×1.45; from 0.11 to 0.048 (quiet office), ×2.3. Gust authority (σ) is untouched. A vertical field between a table electrode and a ceiling electrode is the natural first version, since thermal plumes are vertical.

**Costs**
- Charge relaxation in room air: τ = ε₀/σ_air ≈ 15 min at σ_air 10⁻¹⁴ S/m [ESTIMATE]. Motes must be recharged, and the loop's integrator learns each mote's q.
- A charged-mote inhalation note.
- Kilovolt electrodes with µA-limited supplies.

### 2.5 Idea 5: passively dipped spots (tested; marginal in quiet rooms)

**What it is.** An incoherent LG00 + LG01 mix (for example, orthogonal polarisations) with g(ρ) = (1 + 2x)e^(−2x), x = ρ²/w². The force no longer falls with small offsets, so the Gaussian runaway that couples loop rate to w disappears. A 1:2 mix even restores.

**Price.** Half the centre intensity per watt, so ×2 power for the same holding intensity (×3 for 1:2). The eye-equivalent Gaussian waist is therefore √2·w. Modes ×2–3 per spot.

**Result** [SIM, §2.1 table]:
- At σ_n 4 µm the dip holds at 20 µm (eye-equivalent 28 µm), where the Gaussian already holds at 25 µm: **no net gain.**
- At σ_n 1.5 µm the dip holds at 10 µm (eye-equivalent 14 µm), where the Gaussian still loses 8–13/30 at 15 µm: **×1.2–2 net.**
- The dip's w_min is noise-limited (r_p99.9 ≈ 4.2σ_n), while the Gaussian's grows as √(σ_n·F·τ). **Prediction:** in office drafts (F ×3) the dip gains ×3–5 [DERIVED, not simulated].
- **In modes, dips always cost more.**

Use them only where authority is high and the mode budget is not binding.

---

## 3. Force per watt in air: everything I checked (1 µm mote, drag 3.2×10⁻¹⁰ N at 1 m/s)

ΔT-photophoresis: F/P_abs = 1.7×10⁻⁵ N/W (k_p 0.04, J₁/A 0.5); 2.6×10⁻⁵ at k_p 0.012. That is 19 µW absorbed per m/s.

**Scaling law** [DERIVED]. For *any* thermally driven gas force on a body of size ℓ:
- force ~ μν·ΔT/T × G_F;
- drag ~ μvℓ × G_D;
- heat ~ k_g·ΔT·ℓ × G_H.

So I_hold ~ (G_D G_H/(G_F G_A))·k_g·T·v/ν. It is size-independent, and the shape changes it only through O(1) factors.

The thermodynamic floor for a surface-slip swimmer (Lighthill efficiency ≤ ½) is 2Fv = 6.5×10⁻¹⁰ W at 1 m/s. Photophoresis is ×3×10⁴ above it. The waste is thermal creep's poor efficiency, and in air only heat can drive it.

| Mechanism | Number that decides (formula) | Verdict |
|---|---|---|
| Radiation pressure / gradient force | F/P ≈ Q/c = 3.3×10⁻⁹ N/W, i.e. **2×10⁻⁴ ×** | dead |
| Δα (accommodation) photophoresis | dipole 2(ζ/a)Δα·ΔT_mean against T₁ = 4k_g·FOM·ΔT_mean, ratio 0.4Δα at 1 µm (ζ ≈ 0.11 µm); body-fixed, needs orientation control (D_r ≈ 9 s⁻¹) | **≤ 0.4×**, dead |
| Knudsen pump / thermal transpiration through pores | open-body back-flow: R_in/R_out ≈ a²/(3κ) ≈ 5×10³ (κ ≈ 7×10⁻¹⁷ m²), so Δp ≈ 2×10⁻⁴ of the stall pressure; force ≤ 1 % of drag at 1 m/s | dead (confirms Sonnet R2) |
| Shaped motes, radiometric vanes, needles | same scaling law, O(1) shape factors | ≤ ×2, dead as a 10× lever |
| Negative photophoresis / Janus pull | lets a head push *or* pull, so h → 1; back-side heating needs weak absorption (FOM_neg ≲ 0.3 FOM) or orientation control | ≤ ×1.3–2 via h, minor |
| Free-molecular / sub-µm motes | Epstein drag ∝ a², force ∝ a³I, so I_hold ∝ 1/a; continuum is optimal (round 2 opus) | dead |
| Superlinear pulsing (hot-gas μ²/k_g ∝ T^0.58) | ×1.3 at T_f 450 K, capped by ITO 573 K | dead |
| Photo-charging + room field | q ≤ 4πε₀a·4 V = 4.5×10⁻¹⁶ C; E = 3.6×10⁴ / 1.4×10⁵ / 7.3×10⁵ V/m for 0.05 / 0.2 / 1 m/s | dead (above perception) |
| Electret charge + room field | E = 1.4–5.7 kV/m for 0.05–0.2 m/s *common mode only* (Earnshaw: no mm-scale addressing) | idea 4 (×1.5–2.3) |
| Magnetic (χ ≈ 1 loading) | B·dB/dz = 4.7 T²/m (5 cm/s) to 97 T²/m (1 m/s) | dead |
| Acoustic | T6 beam-cone bound > 100 dB within 1 m; Gor'kov force ∝ a³ negligible at 1 µm | dead (documented) |
| Ablation / sublimation micro-rocket | propellant ṁ = F/u_e (u_e 1 km/s): lifetime **2 ms at 1 m/s, 0.2 s at 1 cm/s** for a 6×10⁻¹⁶ kg mote | dead |
| Humidity-fed evaporation (Stefan flow) | supply ≤ Dρ_v/a = 0.25 kg/m²/s gives u ≤ 0.21 m/s, force = drag at **0.07 m/s**, for 3.5 µW latent heat (photophoresis needs 1.4 µW); and it needs a vapour sink | dead |
| Air-heating thermophoresis / buoyant micro-plumes | v_th = K·ν∇T/T needs ∇T ≈ 4×10⁶ K/m for 0.1 m/s; a 1 mW air heat source makes a 1.7 cm/s laminar plume shared by all neighbours | dead |
| Acoustic or infrasonic active draft cancellation | u = p/(ρc): 5 cm/s needs **20 Pa = 120 dB** at 1–20 Hz; sound is irrotational, turbulence vortical | dead |
| EHD ion-wind "voxel drones" | ~10⁻² N/W (recalled), but mm-scale kV devices, corona ozone, gravity 10⁻⁵ N per mg | dead (not motes; ozone; round-2 drone kill) |
| Tethers / nanofibre webs | mechanical holding at zero light | dead (a medium; breaks on touch; inhalable fibres) |

---

## 4. Eye-safety basis: is there a sound loophole for a *static* focus?

1. **Physical corneal heating at a focus** [DERIVED/ESTIMATE, `r3_numbers.py` §D].
   - At 1550 nm (α ≈ 10³ m⁻¹), the heat is deposited along a ~1 mm cone. On-axis rise ≈ (P·α/4πk)·ln(1 mm/r) ≈ **7–8 K per 10 mW at NA 0.01–0.1**, against 1.8 K for a collimated 3.5 mm beam. This is consistent with R7's 0.4 K/mW skin estimate.
   - So **~10 mW per pupil is near the physical long-exposure comfort limit for any NA.** 100 mW at a focus is a ~70 K corneal burn risk.
   - **The 100 mm Condition 3 distance** would let NA-0.1 foci carry ×17 more (R7 K7: 168 mW) *on paper*. It is **physically unsafe** for an accessible focus, and EN 50689's "at any position" closes it. Rejected.
2. **Other wavelengths.**
   - 1.94 µm and 2.94 µm absorb within 0.1 mm and 1 µm, so a focus heats the corneal surface: **~28–29 K per 10 mW**, worse.
   - 10.6 µm has the same 1000 W/m² MPE but 6.8× larger diffraction-limited spots, so B9 ÷ 47.
   - The long-term MPE is the same 1000 W/m² over 3.5 mm at 1.4 µm–0.1 mm (R7 E3/S2).
   - **1.5–1.7 µm is already optimal.**
3. **Pulsing.** The force is linear in mean absorbed power, so ×1. Rule 2 caps mean power anyway.
4. **Corneal directional acceptance** (beams from behind the head cannot enter): ≤ ×2. The skin MPE at 1550 nm is the same 1000 W/m² over 3.5 mm, and touch puts fingers at foci. Dead.
5. **"Spread over many directions."** At the mote all of its own beams converge, so s ≥ 1 by construction. Only *other* motes' stacking can be scheduled away (idea 1).
6. **Interlocks and curtain.** Already covered: P ≈ 0.2–0.3 for consumer use.
7. **The one sound loophole is motion** (idea 2).
8. **Risk to every route.** ICNIRP's small-beam skin note ("compare the actual radiant exposure for beams < 1 mm", R7 S3) would make any µm focus on skin exceed the EL. Its scope (t < 0.35 s?) is unresolved in R7. RT7 should settle it, because it applies to T7's design and to all ideas here equally.

---

## 5. Answer to the brief: can B9 be beaten by ≥ 10×, and what has to break?

- **Static content, sketch density: yes, by idea 1.** The passive-Class-1 cap on mean v_rel rises ×10–30, to 0.5–1.4 m/s. The loop is verified holding the needed spots (w 25–35 µm) only up to quiet-office authority.
  - Requirements:
    - h·s ≤ 1.5–2 via stacking-aware assignment and mean-flow-aligned heads;
    - FOM 7–8;
    - follow-mode 5 kHz holograms at w 25–35 µm with σ_n ≤ 2–4 µm;
    - a field per head of ~0.6–0.8 m to stay at T7's mode count.
  - No physics is violated. All four are engineering, and two are unverified: long-run loss rates at small w, and office-authority loops.
- **Film density:** ×5–10.
- **Moving content and fast animation: yes, ≥ 10×, by idea 2** (crossing-rate bound, passive Class 1 with a stall safeguard). The cost moves to steered channels.
- **Drafty rooms (office σ_u 0.1, hand wakes):** idea 1 covers mean office drafts (0.16–0.2 m/s) only at the optimistic end, w ≤ 30 µm with h·s ≤ 1.75. The loop at office authority is unproven. Ideas 3 (×10–100, product-changing) and 4 (×1.5–2.3) are the draft-specific levers.
- **What would have to break for a free ≥ 10× on a static voxel?**
  1. Thermal creep's force per watt in a 1 atm gas: I_unit ∝ k_g·T/ν, ≥ 2.7×10⁶ W/m² per m/s. Gas kinetics: **no.**
  2. The ~10 mW-per-pupil corneal limit at 1.4–1.8 µm. Physiology plus standard: **no.**
  3. s, h ≥ 1. Geometry: **no.**
  4. Étendue, M ≥ L²/(πw²). **No.**

  Everything between these floors and T7's operating point (×12–57) is engineering, and it is where the 10× lives.

---

## 6. Lab tests (weeks-scale) for the top three

**Test A: idea 1, does the follow-mode loop hold small spots, and how small can s get?** (3–6 weeks)
1. *Software, 1 week.* Rerun M17 with a stacking-aware head-assignment optimiser (greedy or LP: for each mote pick the 3 heads minimising the maximum summed power in any 3.5 mm pupil). Report s_worst for sketch and film at w = 25, 35, 50 µm. **Pass:** s_worst ≤ 1.5 for a sketch.
2. *Software, 1 week.* Long m18c follow runs (60 motes × 150 s) at MEMS 5 kHz for w = 20–30 µm, σ_n = 1.5 and 4 µm, still / quiet office / **office σ_u 0.1**, Gaussian and dipped profiles. **Pass:** < 10⁻⁴/s at w ≤ 30 µm (quiet) and ≤ 40 µm (office).
3. *Bench, 3–4 weeks.* One absorbing mote (carbon, or the ITO candidate if it exists) in a 1550 nm focus of w = 25 µm. A fast steering mirror (≥ 5 kHz small-signal) emulates follow mode. Camera centroiding with a 50 mm lens (target σ_n ≤ 2 µm at 5 kHz). A fan-driven turbulence box with measured σ_u = 0.03 and 0.1 m/s. Add calibrated synthetic noise to the position estimate to map **w_min against σ_n**. **Pass:** w_min ≤ 30 µm at σ_u 0.03, and the √(σ_n F τ) scaling.

**Test B: idea 2, the crossing-rate invariant and the stall safeguard** (3–4 weeks, on a BYU-style galvo photophoretic rig)
1. Hold one mote on a closed 10 cm loop at v_m = 0.2, 0.5 and 1 m/s with a galvo-steered 1550 nm focus (w 35 µm). Log the minimum holding power P(v). **Pass:** P ∝ v_rel, so E/L is constant within 30 %.
2. Put a 3.5 mm and a 1 mm aperture with fast InGaAs detectors on the loop and at 5 / 20 / 50 mm off it. Record per-pass energy and the 10 s mean against f_r. **Pass:** mean = f_r·(E/L)·d_ap within 30 %, and per-pass energy ≪ 8 mJ.
3. Stall injection (freeze the galvo): measure the time from stall to beam cut. **Pass:** ≤ 100 ms with an independent channel. Write the classification argument (rule 1, rule 2, scanning safeguard) for a test house to review.

**Test C: idea 3, can a push–pull column keep v_rel ≤ 5 mm/s in a real room?** (2–4 weeks)
1. A 0.2 × 0.2 m push nozzle (honeycomb + 3 screens + contraction ratio ≥ 9) at 0.3 m/s, with a pull inlet 0.6 m opposite.
2. Measure core Tu with a hot-wire or LDA:
   - with a fan cross-draft of 0.1–0.2 m/s;
   - with a person walking at 1 m from it;
   - with a hand inserted.
3. Seed 1–3 µm particles and track their lateral dispersion over 0.3 m (high-speed camera). Measure fan noise in dB(A).
4. **Pass:**
   - lateral rms velocity relative to the column ≤ 3 mm/s outside hand wakes (×15 on a still room's mean);
   - noise ≤ 30 dB(A) at 1 m;
   - the wake dropout zone measured.

---

## 7. Notes for the main session and red team 7

- **T7 B9 uses h_worst with a mean-power limit.** Use the time-mean h at the worst pupil (×1–1.5).
- **T7's design waist (51 µm) is not the 5 kHz follow-mode loop limit** in my short runs (~25 µm at σ_n 4 µm). Long runs are needed before changing the design point.
- **"Fast Iron-Man animation is excluded under passive Class 1"** (T7 §5 item 3, §6) should read "excluded for holographic static voxels by B8×B9 (v ≲ C^⅓(f/k)^⅔ ≈ 7–20 cm/s at 5 kHz)". It is eye-safe in POV mode under the crossing-rate bound.
- **B9 in modes** (§1) is a cleaner statement of the wall than B9 in w. It shows that sensing noise, loop rate and modes trade one-for-one against eye budget.
- **I did not model** the lateral photophoretic gradient force in the loop sims. m18c omits it too. It is outward for Gaussians (rate 1.5·a·F/w², 7.5 % of beam force at w = 10 µm, ρ = 5 µm) and inward for 1:2 dips, so it favours dips slightly.

## Sources

**Web (this session)**
- IEC 60825-1:2014 preview, Condition 3 at 100 mm from the apparent source (search snippet): [ANSI webstore preview](https://webstore.ansi.org/preview-pages/iec/preview_iec60825-1%7Bed3.0%7Db.pdf); [IEC preview](https://webstore.iec.ch/en/iec_catalog/product/preview/?id=L3B1Yi9wZGYvcHJldmlldy9pbmZvX2llYzYwODI1LTF7ZWQzLjB9Yi5wZGY%3D).
- Multiple-pulse rule 3 / C5 tied to 400–1400 nm retinal limits (search snippets): [DTIC ADA614650](https://apps.dtic.mil/sti/pdfs/ADA614650.pdf); [Seibersdorf white paper, not fetchable here](https://www.seibersdorf-laboratories.at/fileadmin/user_upload/docs/le/las/publ/whitepaper_iec-60825-1_v1d.pdf).
- Static E-field perception 10–45 kV/m; no adverse effects except microshocks: [ICNIRP static electric fields](https://www.icnirp.org/en/frequencies/static-electric-fields-0-hz/index.html); [EMF-Portal](https://www.emf-portal.org/en/cms/page/home/effects/static-fields); [Kursawe et al., Environ. Health 2021](https://ehjournal.biomedcentral.com/articles/10.1186/s12940-021-00781-4).
- Open-jet core Tu ≈ 0.1 % with contraction ratio 20–25: [Brunel open-jet wind tunnel](https://bura.brunel.ac.uk/bitstream/2438/10041/1/Fulltext.pdf).
- Potential core 4.7–7.7 d; air-curtain core Tu ≤ 8 % (snippets): [nozzle geometry and potential core](https://www.academia.edu/53312049/Effect_of_nozzle_geometry_and_semi_confinement_on_the_potential_core_of_a_turbulent_axisymmetric_free_jet); [potential core comparisons](https://www.researchgate.net/figure/Potential-Core-Length-Comparisons_tbl3_255668009).
- Aerosol charge limits: [Hinds, Aerosol Technology ch. 15 (search hit; value recalled, not verified)](https://www.academia.edu/42913208/_15_Hinds_1999_Aerosol_Technology_Electricity).

**Repository (read-only)**
- `07_mote_route/R7_mote_safety.md`: E3, S2, S3, K6, K7, T3–T4.
- `07_mote_route/R5_optical_trap_displays.md`: passive OTD traps at ~1.8–2 m/s relative to air with 20–500 mW at 405 nm.
- `09_unlock/T7_gaussian_voxels.md`, `09_unlock/T6_unlock_theory.md`, `05_reviews/red_team_6_lcsv.md`, `09_unlock/m18c_vector_pin.py`, `09_unlock/results/m18c_follow.log`.

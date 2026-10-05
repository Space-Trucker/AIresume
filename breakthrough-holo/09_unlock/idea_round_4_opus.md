# Idea round 4: FLOW-X, AIR-SV, the needle, and the nearest home-buildable variant (independent report, Opus)

*Written 2026-10-05. I read `IDEA_ROUND_4_HOME_BRIEF.md` (with the AIR-SV addendum), `05_reviews/FINAL_VERDICT.md` (v5), `m20_flowx.py`, `m21_airsv.py` and their logs, `idea_round_3_opus.md`, `idea_round_3_sonnet.md`, the T8 status box, RT7 (summary, C1, M8, M9), the RT8 summary, `T1_what_physics_allows.md`, `m18d_touch_air.py` and its log, `07_mote_route/mote/physics.py` and `safety.py`. I edited no repository file except this one.*

*Scratch scripts (session scratchpad, not committed):*
- *`r4_flowx.py`: column shear layer, buoyancy of temperature non-uniformity, cross-draft response, hand numbers, inkjet injection, supply/haze/mass, escape with settling;*
- *`r4_airsv.py`: imports `physics.py` and `m21_airsv.py` read-only. Photophoretic force per watt for big beads, Oseen bead–bead interactions, chains and tilted strokes, the pulsed-kick surface flash, skin-capped transport speed, cross-draft tolerance, visible spots and speckle, the divergence argument;*
- *`r4_engine.py`: Lambert-sphere phase function, FLOW-X and FLOW-R visible design points, the single-pulse visible AEL, charged motes, and the needle candidates.*

*Web searches used: 7 of 10 (sources at the end).*

**Tags.**
- [MEASURED]: a documented fact, with its source.
- [DERIVED]: derived here from stated physics, with the formula.
- [ESTIMATE]: an order-of-magnitude judgement.
- [SPECULATIVE]: an untested idea.
- "recalled": from memory, not re-checked this session.

---

## 0. Verdict in one screen

1. **FLOW-X fails in a home as specified, but its core idea survives in a changed form that I call FLOW-R ("rain").** Five findings:
   1. **The targeting premise fails.**
      - Tu 0.1–0.2 % needs a wind-tunnel contraction (a settling chamber 2–3× the nozzle width) and ≤ 1–3 mK thermal uniformity at 1–2.5 cm scales (§1.2).
      - A buildable home column runs at an effective Tu ≈ 0.5–1 %. That gives σ_x ≈ 5–10 mm over a 1 m fall and p_hit ≈ 0.04–0.08 for a 1 mm stroke.
      - The "targeted" supply therefore rises to ~10⁶ motes/s, the same as an untargeted rain [DERIVED].
   2. **No commodity part can inject on demand to ±0.5 mm in two dimensions.** Inkjet drops also bring heat and momentum: 1.6×10⁵ drops/s of 30 pL carry **11.8 W of evaporative cooling**, and each stream makes a cold rope sinking at 0.7–3 cm/s.
   3. **Content lags by 1.2–5 s.**
   4. **Hand wakes.** A hand degrades everything below it down to the inlet.
   5. **m20 overcounts the visible engine.** Its w_v = 2.5a forces 0.5–4.7×10⁹ modes. Sparse white motes lit from above allow w_v = 80–140 µm at ≤ 0.39 mW per beam: 16–50× fewer modes, or at desk scale 8–40 steered spots and no hologram at all. That is passive visible Class 1, with **no IR anywhere** (§1.4).

   **FLOW-R** decouples supply from content. An untargeted, uniform rain of 10–14 µm food-grade motes falls in a guarded downward column, and cameras gate per-mote visible spots.
   - **Gains:**
     - zero injection latency, so content can move at any speed;
     - the image survives hand wakes, because mixing a uniform concentration leaves it uniform;
     - insensitivity to Tu, mK gradients and common-mode cross-drafts.
   - **Prices:**
     - 1.6×10⁵ motes/s (desk) to 1.4×10⁶ motes/s (room), i.e. 0.5–11 g/h;
     - **13–35 mg/m³ inside the column, at an optical depth of 0.08–0.3 %, which is sub-visible**;
     - ≥ 99 % recapture;
     - real-time 3D tracking at 0.05–0.2 particles per pixel. **Tracking is the hard part, and it limits FLOW-R to desk scale at home.**
2. **AIR-SV is dead for an open room.** Six findings:
   - **No passive 3D trap is possible.** The inertia-free bead velocity u − v_s·ẑ is divergence-free, so the best any steady flow can offer is neutral stability; the inertial correction is ≤ 0.1 s⁻¹ [DERIVED].
   - **Cross-drafts.** Holding the core's lateral air speed at the beads to ≤ 1 mm/s needs room cross-drafts ≤ **8–21 mm/s**, against 20–100 mm/s in the brief. Guards help ~5×.
   - **Hands.** A hand plume (35–400 mm/s) is 10–400× the trim authority. Rebuilding content at the skin-capped transport speed of **4.6 mm/s per bead** takes **22 s per 10 cm** of bead travel.
   - **Vertical strokes.** Bead wakes (Oseen) give **2.3 mm/s per vertical neighbour at 3 mm, and 9.4 mm/s at the top of a 10 cm vertical stroke**. That fails the EN 50689 skin rule (1.6 mW against 0.785 mW) for 40 µm beads. Lateral interactions are 10× *weaker* than m21 assumed.
   - **Pulsed trims.** With K = 1000 beads per beam, each kick flashes the lit face by **+146 K (PMMA, above its glass transition) or +352 K (a 1 µm glass shell, 645 K, above ITO's 573 K)**. K ≤ 300 is needed, i.e. 3× the beams.
   - **Bead sizing.** A 0.1–0.25 % size spread needs elutriation-sorted beads.

   It survives only as an enclosed or still-air "levitated bead sculpture".
3. **The needle.** No untried physical principle beats the home constraints within the vision's rules. The deciding numbers are in §4. I list:
   - electrostatic weight support;
   - bead and drop rain;
   - helium soap bubbles;
   - acoustic POV;
   - nonlinear (upconversion) and photochromic selection in a uniform mote rain;
   - EHD silent columns;
   - eye tricks;
   - retroreflective gloves.

   **The useful finds are design levers inside FLOW-R:**
   - uniform rain;
   - charged motes, steered at 0.3–4 kV/m for ±2 mm/s and collected electrostatically;
   - fluorescent food-grade motes, or multimode RGB lasers, against speckle;
   - a black glove used as the beam dump.
4. **The nearest home-buildable variant is a desk "holo-pedestal" running FLOW-R** (§5).
   - **What it delivers:**
     - a 0.2 m image in open air, 360° viewable;
     - 0.5–1 m of strokes at 20–30 Hz, 3–5 mm sampling, 1.5–3 cd/m² lines in a dim room;
     - glove touch, with a 7–15 cm shadow below the hand;
     - no IR, visible Class 1 per beam;
     - ≤ 30 dB(A), ~$5–12k of commodity parts.
   - **What it relaxes:**
     - "no gas/fog" becomes a sub-visible food-grade mote stream;
     - "not a table" becomes a 0.45 m hood above and a pedestal inlet below;
     - size (×5 smaller), brightness and content density.
5. **Ranking:**
   1. FLOW-R desk;
   2. an aerial-imaging plate with a glove (works today, but it is a holo-window and not the vision);
   3. FLOW-X targeted;
   4. AIR-SV (enclosed sculpture only);
   5. the photophoretic routes (not home);
   6. acoustic POV (killed by SPL).

   **FLOW-R is better than AIR-SV on every home criterion; FLOW-X is the better of the two as briefed** (§3).

---

## 1. FLOW-X evaluated

### 1.1 What m20 gets right and wrong

| m20 item | Status | Correction |
|---|---|---|
| Motes follow the air (τ_p 0.1–9 ms, St ≪ 1) | Right | a = 5 µm mannitol: τ_p 0.46 ms, v_s 4.5 mm/s [DERIVED] |
| σ_x = Tu·H (frozen, ballistic) | Right in form | **Tu 0.1–0.3 % is not reachable at home** (§1.2). Realistically 0.5–1 %, so σ_x 5–10 mm |
| Supply 1.6–4.7×10⁵ /s | Right at its Tu | At home Tu the targeted supply equals a uniform rain (~10⁶ /s, §1.3) |
| Room level 1.8–5 300 µg/m³ | **Too high by 13–50×** | m20 removes particles only by 0.5 ACH. Floor deposition v_s/H is 6.5 h⁻¹ (a = 5 µm) to 26 h⁻¹ (a = 10 µm) [DERIVED] |
| w_v = max(2.5a, 20 µm), giving 0.5–4.7×10⁹ modes | **Overcounted** | Sparse motes (spacing 4–9 mm) allow w_v 80–140 µm: 16–50× fewer modes, or 8–40 galvo/AOD spots at desk scale (§1.4) |
| q = 0.3, two beams | Conservative | A white Lambertian mote lit from above gives p = 0.76–0.86 for every horizontal viewer (§1.4) |
| Stray light: L_wall at room albedo 0.8 | Avoidable | Beams from above end in the black inlet (reflectance ~2 %) |
| "Co-moving hologram updating at U/1 mm ≈ 300 Hz" | **Not commodity** | 4K LCoS runs at 60 Hz, which makes horizontal strokes U/60 = 4.2 mm thick (§1.4) |

### 1.2 Laminar column physics in a furnished room with people

| Item | Formula | Number | Consequence | Tag |
|---|---|---|---|---|
| Exit boundary layer | θ = 0.664 L/√(UL/ν) | 2.0–2.8 mm for 0.15–0.3 m nozzle walls at 0.25 m/s | sets the shear-layer scale | DERIVED |
| Kelvin–Helmholtz roll-up | f·θ/U ≈ 0.016; spatial growth −α_iθ ≈ 0.1 | f 1.4–2 Hz, λ_KH 6–9 cm; ×10³ growth (Tu 0.1 % → 10 %) within **14–20 cm of the lip** | the shear layer is turbulent before the image starts | DERIVED (constants recalled) |
| Shear-layer noise inside the core | irrotational decay: u′/U ≈ 0.15·exp(−2πy/λ_KH) | 2–4×10⁻² at 2 cm, **1–4×10⁻³ at 5 cm**, ≤ 1.2×10⁻⁴ at 10 cm | the seeded core must sit ≥ 5–10 cm inside the layer (a guard) | DERIVED |
| Core erosion | inner edge moves inward ~0.09 per unit length (potential core 4.7–7.7 D, measured, round 3) | 4 / 9 / 14 cm per side at 0.5 / 1 / 1.5 m | nozzle = image + 2·(guard + erosion + drift) | ESTIMATE |
| Tu without a contraction | honeycomb takes 30 % to 1.2 % [MEASURED, flow-conditioning ref.]; screens are subcritical at Re_wire = 0.25·50 µm/ν = 0.8 | **0.3–1 %** in a home-sized unit | wind-tunnel 0.1 % needs a contraction ratio ≥ 9, i.e. a settling chamber 3× wider than a 1.1 m nozzle (3.3 m): not home furniture | ESTIMATE |
| Temperature non-uniformity in the core | blob speed = min[(2/9)(gΔT/T)R²/ν·1.5, 0.5√(2gΔT R/T)] | 10 mK, R = 1 cm: 0.74 mm/s; 3 mK, 2.5 cm: 1.1 mm/s; 30 mK, 1 cm: 2.2 mm/s | Tu 0.2 % (0.5 mm/s) needs ≤ 1–3 mK at cm scales. A 10 W fan already warms 0.16 m³/s by 52 mK, non-uniformly | DERIVED |
| Room stratification (1–2 K/m) | g·ΔT/T | 0.5 K → 0.017 m/s², 6.7 cm/s over 4 s | common-mode deceleration (tracked); heavy-over-light edges destabilise the mixing layer | DERIVED |
| Cross-draft | "slug" model: v_lat = C·U_c²·H/(2DU), C ≈ 1.5; vs Pratte–Baines y/(rD) = 2.05·(x/(rD))^0.28 | U = 0.25: U_c 0.05 m/s → 9–10 mm/s lateral, **0.8–1.9 cm shift**; U_c 0.1 → 38–40 mm/s, **3–7.5 cm** (P–B: 0.6–1.3 cm) | **common mode**: harmless for tracked motes, but the inlet must be oversized by ≥ 5–10 cm per side | DERIVED / correlation recalled |
| Draft-eddy shear inside the core | gradient ≈ v_lat/ℓ | 10 mm/s over a 0.3 m eddy: a 3 mm pair separates 0.4 mm in 4 s | ruins ±0.5 mm targeting; irrelevant to a tracked rain | DERIVED |
| People | plume entrainment at the column 1.7–3.4 mm/s per person at 1–2 m (sonnet round 3) | ≤ 1 % of U | small cross-draft term | DERIVED (round 3) |
| Hand in the column | Re = UL/ν; Ri = gΔT·L/(T·U²) | Re 1 300 at 0.25 m/s; **Ri 0.51 bare hand, 0.06 glove** (ΔT 1.5 K); shedding 0.6 Hz | a bare hand's plume opposes the downward flow and disturbs ≤ 1 hand width upstream; an isothermal glove does not | DERIVED |

**Push–pull stability.**
- A slow column (U 0.25 m/s) has a cross-flow velocity ratio of r = U/U_c = 2.5–12 in the brief's drafts.
- The pull inlet's suction decays as ~Q/(10x² + A) (recalled), so it holds the column only in the last ~0.3 D. The column's own momentum does the rest.
- I estimate **95–99.9 % recapture** depending on drafts and hands, with a pull/push ratio of 1.5–2 and an inlet oversized by 5–10 cm per side [ESTIMATE]. This has to be measured (§7).

**Sizing** [DERIVED from the rows above]:

| Size | Image | Geometry | Nozzle | Push flow | Pull flow |
|---|---|---|---|---|---|
| Desk | 0.2 m | 0.45 m from nozzle to inlet | ≈ 0.42 m | 0.044 m³/s (160 m³/h) | ~0.09 m³/s |
| Room | 0.6 × 1 m | 1.3 m from the nozzle to the bottom of the image | ≈ 1.1 m | 0.3 m³/s (1 100 m³/h) | ~0.5 m³/s |

### 1.3 Mote generation, recapture and latency

**The commodity injector** [MEASURED]: an HP45 thermal inkjet cartridge.
- 300 nozzles at 600 dpi;
- 29–35 pL per drop at 12–18 kHz, i.e. up to 3.6–5.4×10⁶ drops/s;
- ±5 % drop volume;
- open-source controllers exist.

**From drop to mote** [DERIVED, `r4_flowx.py` §F]:
- A 30 pL drop (d₀ = 39 µm) of a 3 % solution dries to a **10.5 µm mote**, and a 1 % solution to a 7.3 µm mote.
- It dries in 0.86 s at 50 % RH (d²-law, t = ρ_l d₀²/(8 D_v Δρ_v)).
- Ejected at 10 m/s, it stops within ~29 mm.

**What injection does to the column** [DERIVED]:
- **Momentum.** 1.6×10⁵ drops/s at 10 m/s carry 48 µN, against the column's ρU²A = 48 mN. Split over 300 streams, the induced jets reach 8 mm/s at 0.3 m, i.e. 3 % of U.
- **Latent heat.** Each 30 pL drop absorbs 7.4×10⁻⁵ J. At 1.6×10⁵ drops/s that is **11.8 W** of cooling. One stream at 60 drops/s is a 4.4 mW cold line source: 29 mm/s as a still-air plume, or ~7 mm/s as an advected thermal wake (ΔT ∝ P/(ρc_pU·4παt)). It drags its own and its neighbours' motes.
- **Fixes.** The drop volume fixes the water per mote: a 14 µm mote from a 30 pL drop needs ~7 % solids and still evaporates ~3×10⁻¹¹ kg of water.
  - Use smaller drops (1.2–4 pL heads give ×8–25 less latent heat per mote of the same size).
  - Or dry in a separate duct and reheat its air (~12 W) before it joins the plenum.

**2D on-demand placement** [ESTIMATE]:
- A head is a line (x).
- To get y you need either a 2D array of heads sitting *in* the flow, whose fairings shed wakes, or a carriage scanning at ≥ 2·0.2 m·30 Hz = 12 m/s.
- Screens downstream of the injector catch motes: Stk = τ_p U/(d_w/2) = 9 for a 14 µm mote on a 50 µm wire, so each screen removes ~25–35 %.
- **There is no commodity 2D on-demand mote printer.**

**Targeting at home Tu** [DERIVED, `r4_flowx.py` §G]:
- p_hit = erf(0.5 mm/(√2·σ_x)).
- At σ_x 5–10 mm, p_hit is 0.04–0.08, so the 5 m / 60 Hz sketch needs 0.8–1.6×10⁶ motes/s.
- **That equals the uniform rain** of §5 (1.4×10⁶ /s). Targeting buys nothing once Tu ≥ 0.5 %.

**Latency** [DERIVED]: t = (z_inj + z)/U:
- 1.2 s (top of the image) to 5.2 s (bottom) for the room column;
- 1.4 s for a desk column.

The 3 s figure in the brief is right. For Iron-Man interaction (≤ 0.1 s) **targeted FLOW-X fails R6/R7**.

**Recapture.**
- A filter in the pull path captures ≥ 99.9 % of 10–14 µm particles. Escape is set by motes that never reach the inlet (§1.2).
- Charged motes help (§4, item 5): a grounded inlet grille at 1–3 kV/m pulls them in. A corona precipitator is excluded because it makes ozone.

### 1.4 Visible lighting: Class 1, modes or channels, stray light, ghosts, speckle

**Phase function of a white, Lambertian mote** [DERIVED]:
- p(α) = ω·(8/3π)·[sin α + (π−α)·cos α], normalised to isotropic = 1 (checked: its 4π average is ω). α is the phase angle.
- With ω = 0.9: p = 2.40 at α = 0°, 1.46 at 60°, **0.76 at 90°**, 0.26 at 120°.
- **Two heads lit from above, 30° off vertical and on opposite azimuths, give p = 0.76–0.86 for every horizontal viewer (±6 % in azimuth).**
- This replaces RT7's 66–220 wall emitters (RT7 C1). Viewers below the image (α > 120°) see ≤ 0.3.

**Design points** [DERIVED, `r4_engine.py` §2; line luminance L per 1 mm line, sample spacing δ, one pass lit for d_s/U, worst-azimuth p = 0.5 (conservative), mote albedo 0.9]:

| Point | a | Supply | Motes/s | In-column n | Optical depth across the column | In-column mass | Spot w_v (z_R) | Power per beam | Pupil mean | Lit at once | Other motes in one beam tube |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Room, targeted (m20-like: 5 m strokes, 60 Hz, δ 3 mm, 3 cd/m²) | 10 µm | targeted, σ_x 2 mm | 3.2×10⁵ | 3.5×10⁶ /m³ | 0.13 % | 22 mg/m³ | 100 µm (6.3 cm) | 0.12 mW | 0.058 mW ✓ | 400 | 0.07 |
| Desk, targeted (1 m, 30 Hz) | 10 µm | targeted, σ_x 1 mm | 1.6×10⁴ | 1.6×10⁶ | 0.03 % | 10 mg/m³ | 100 µm | 0.24 mW | 0.058 mW ✓ | 40 | 0.02 |
| Desk rain A (1 m, 30 Hz, δ 3 mm, 3 cd/m²) | 5 µm | rain, N_s = 1 | 4.0×10⁵ | 4.0×10⁷ | 0.19 % | 31 mg/m³ | 45 µm (1.3 cm) | 0.19 mW | 0.047 mW ✓ | 40 | 0.08 |
| **Desk rain B′ (0.5 m, 20 Hz, δ 5 mm, 1.5 cd/m²)** | **7 µm** | rain, N_s = 1 | **1.6×10⁵** | 1.6×10⁷ | **0.15 %** | 35 mg/m³ | **80 µm (4 cm)** | **0.39 mW** | 0.062 mW ✓ | **8** | 0.10 |
| Desk rain C (B′ with a = 5 µm) | 5 µm | rain | 1.6×10⁵ | 1.6×10⁷ | 0.08 % | 13 mg/m³ | 80 µm | 0.76 mW | 0.12 mW ✓ | 8 | 0.10 |
| Room rain (0.6 m image, 5 m strokes, B′ settings, w 140 µm) | 7 µm | rain | 1.4×10⁶ | 1.6×10⁷ | 0.30 % | 35 mg/m³ | 140 µm (12 cm) | 1.19 mW | 0.19 mW ✓ | 80 | 0.59 |

Readings:
- **Visible Class 1 holds by mean power at every design point** (the pupil mean is ≤ 0.39 mW).
- **Peak per beam.** At B′ each beam carries ≤ 0.39 mW, so even a stalled scanner is Class 1 [DERIVED].
- **Time-sharing a scanner.** Sharing one scanner among several motes inside a mote's 4 ms crossing raises the beam's peak power. The single-pulse visible AEL, 7×10⁻⁴·t^0.75 J, allows **3.9 mW for 1 ms and 2.8 mW for 4 ms** [DERIVED], so ×4 time-sharing is legal per pulse. A stalled beam then exceeds 0.39 mW, so it needs a scan-fail safeguard (standard in laser shows, ~$100–300) [ESTIMATE].
- **What changed against RT7 C1.** RT7 C1 forced 10¹¹–10¹² visible modes for 1 µm forward-scattering motes. Here the motes are 10–14 µm, white, carried by the air (not by light) and sparse (4–9 mm apart), so a spot can be 6–20× the mote radius. The engine shrinks to:
  - **8–40 simultaneous spots** for a desk: 4–8 galvo channels with ×4 time-sharing, or one 2D AOD per head;
  - **80–400 spots** for a room: tens of AOD channels, or a fast SLM.

  A 60 Hz LCoS hologram makes horizontal strokes 4.2 mm thick at U = 0.25 m/s, so it suits the room scale only if that is acceptable.
- **Ghosts.** Other motes inside one beam's Rayleigh tube: n·πw²·L = 0.02–0.6.
  - With 3 heads, the controller picks a head whose tube is empty. The residual ghost rate is ≤ 1–3 % of spots [DERIVED].
  - Gating matters. An *ungated* beam would light its path: the path-to-focus ratio is n·πa²·L/(η·P_mote) ≈ 17:1 in a 5 µm rain. So **per-mote gating from tracking is mandatory**, otherwise it is a laser show in haze.
- **Stray light.**
  - Beams from above end in the black inlet louvres (R ≈ 2 %). For the room at 0.19 W visible, that leaves ≈ 0.004 cd/m² on the walls [DERIVED].
  - **A hand under a lit mote receives the rest of the beam**: 0.39 mW on skin makes a bright dot. Blank every beam whose continuation hits a tracked hand, or wear a **matte black glove (albedo ≤ 3 %), which turns the glove into the beam dump**.
- **Speckle.**
  - A rough 14 µm mote has a speckle grain of λ/(2a) ≈ 36 mrad, far larger than a pupil seen from 1–2 m. Each lit mote therefore shows an exponentially distributed random brightness per viewer.
  - Multimode RGB diodes (Δλ 1–2 nm) give 3–5 independent patterns, i.e. contrast ≈ 0.45–0.6 [ESTIMATE].
  - **Fluorescent motes remove speckle entirely**, because their emission is incoherent. Example: food-grade riboflavin or fluorescein in mannitol, pumped at 470–490 nm, where the Class 1 AEL is 98–246 µW (`safety.py`). Each mote is lit once, so bleaching is irrelevant [SPECULATIVE].

### 1.5 Touch, hand plumes and wakes

| Effect | Number | Targeted FLOW-X | Rain (FLOW-R) | Tag |
|---|---|---|---|---|
| Flow upstream of the hand | potential flow; St = τ_p U/L ≈ 0.005, so motes go round and do not impact | content above the hand is intact | intact | DERIVED |
| Near-wake bubble | ~1–2 hand widths (8–16 cm) | lost | lost (few motes enter) | ESTIMATE |
| Far wake | u′ ≈ 0.1–0.2 U = 2.5–5 cm/s over 5–10 D (40–80 cm) | **lost down to the inlet**: σ ~ cm, so p_hit → 0 | **survives**: mixing keeps the rain uniform, and tracking handles the motion | DERIVED/ESTIMATE |
| Shadow from the top heads | depth W/(2·tan θ) = 8 cm/(2·tan 30°) | 6.9 cm below the hand unlit | same; a low side head fills it, with stray light on the far side | DERIVED |
| Plume | Ri 0.51 bare / 0.06 glove | bare hand disturbs ≤ 1 width upstream | same | DERIVED |
| Beam onto the hand | 0.39 mW dot | blank or use a black glove | same | DERIVED |

### 1.6 Noise and comfort

- **Noise.**
  - Fan filter units run at **42–56 dB(A)**, e.g. 52 dB(A) for a 0.6 × 1.2 m unit at 0.45 m/s and 100 Pa [MEASURED].
  - Scaling by L_W ≈ K + 10·log Q + 20·log Δp, a desk column (push 0.044 m³/s at ~15 Pa without HEPA; pull ~0.09 m³/s through a large-area filter at ~20 Pa) gives **≈ 21 dB(A) push and ≈ 27–30 dB(A) pull**.
  - The room column gives **35–40 dB(A)** with lined plenums [ESTIMATE].
  - Galvos ticking on random-access jumps are audible: enclose them, or use AODs, which are silent.
- **Comfort.** ISO 7730: DR = (34 − t_a)(v − 0.05)^0.62·(0.37·v·Tu + 3.14). At v = 0.25 m/s, Tu 1 %, t_a 22 °C, DR = 14 % (recalled formula), below the 20 % category-B limit. It applies to the hands and arms in the column, not to the neck [DERIVED].

### 1.7 Particulate safety and regulation

**Room level** [DERIVED, `r4_flowx.py` §H, 50 m³, 0.5 ACH plus floor deposition v_s/2.5 m]:

| Case | Circulated | Room at 99 % capture | Room at 99.9 % capture |
|---|---|---|---|
| Desk rain C (a = 5 µm) | 0.45 g/h | 13 µg/m³ | 1.3 µg/m³ |
| Desk rain B′ (a = 7 µm) | 1.24 g/h | 18 µg/m³ | 1.8 µg/m³ |
| Room rain | 11 g/h | ~160 µg/m³ | ~16 µg/m³ |

For scale, the WHO 24 h PM10 guideline is 45 µg/m³ (recalled). **The room scale needs 99.9 %.**

**In-column air** holds 13–35 mg/m³. A face in the column inhales ~15 µg per breath (0.5 L), against a 10–25 mg lactose carrier dose per inhaler puff (recalled) [ESTIMATE].

**Material.**
- **Polymer (PMMA/PS) motes are a regulatory problem.** EU 2023/2055 restricts synthetic polymer microparticles. Its derogation needs them "contained by technical means so that releases … are prevented" [MEASURED], and a 0.1–1 % leak is not that.
- **Use inhalation excipients instead:** mannitol, trehalose or lactose, spray-dried from an inkjet. Or amorphous silica from a silica sol.
  - Mannitol is a bronchial-challenge agent (Aridol) at 35–635 mg (recalled). The room dose (~µg/h) is 10⁴× lower, but trehalose or lactose is the safer default.
  - Sugar residue feeds microbes in the inlet filter, so replace filters routinely.
- Dust explosion: the minimum explosible concentration of sugar dust (~30–60 g/m³, recalled) is 10³× above the in-column 35 mg/m³.

**Inhalability** [DERIVED]: d_ae = d·√ρ = 10–20 µm, inhalable fraction 0.6–0.75, respirable ≲ 5 %. That is better than the 1 µm ITO motes of the MOTE route (R3/R8).

### 1.8 Cost and buildability (FLOW-X as briefed)

The column and air handling are commodity:
- desk: $0.5–1.5k;
- room: $3–8k.

The 2D on-demand injector is a custom development (no commodity part, §1.3). The co-moving 300 Hz hologram is not commodity either. **FLOW-X as briefed is therefore not home-buildable. FLOW-R is** (§5).

### 1.9 The main session's first-pass questions, answered

| Question | Answer |
|---|---|
| Dispersion over 1 m at Tu 0.1–0.2 % | 1–2 mm is right at that Tu. Home columns reach 0.5–1 %, so **5–10 mm** |
| Supply 6×10⁴–10⁵ /s for a sketch | m20: 1.6–4.7×10⁵ /s. At home Tu, targeted needs 0.8–1.6×10⁶ /s, the same as a rain |
| Escape ≥ 99.9 % | 99 % is enough for a desk (≤ 18 µg/m³); a room needs 99.9 %. m20 overstates room levels 13–50× by omitting deposition |
| Injection latency ~3 s | 1.2–5.2 s (room), 1.4 s (desk): **fatal for interaction; fixed only by a rain** |
| Hand wakes | Targeted: everything below the hand is lost. Rain: only the near wake (8–16 cm) and a 7 cm top-head shadow |
| Fan noise | ≤ 30 dB(A) desk, 35–40 dB(A) room |
| "No gas", "not a table" | Clean room air plus a sub-visible particle stream (optical depth ≤ 0.3 %, 30–1 000× thinner than a fog screen [ESTIMATE]) is still a medium. There is a pedestal or floor inlet below. **Owner's ruling** |

---

## 2. AIR-SV evaluated

### 2.1 Passive versus active stability [DERIVED]

**The bead equation.** A bead with τ_p ≪ the flow time moves at V = u(x) − v_s·ẑ (+ trims). Since ∇·u = 0, ∇·V = 0. The Jacobian of V at any fixed point therefore has zero trace, and **no steady flow can make an attracting 3D equilibrium**: neutral is the best possible.

**The inertial correction** is ∇·V_p ≈ −τ_p·(S² − Ω²) ≤ 0.003–0.1 s⁻¹ (τ_p 12–24 ms, strain 0.5–2 s⁻¹). That is negligible.

**A rotameter-style trap fails.** A decelerating upflow (dU/dz = −G) gives vertical stiffness G but an outward lateral drift G·r/2. With G = 0.01 s⁻¹ (vertical restoring only 10 µm/s per mm), a bead 0.2 m from the axis already drifts out at 1 mm/s.

**Every AIR-SV voxel is therefore actively held in 3D.** The light loop must cover all disturbances, at ≥ ~30 Hz for column turbulence at f ≈ U/ℓ ≈ 5 Hz. m21's 10 Hz revisit (K = 1000) is below Nyquist.

### 2.2 Cross-drafts, guard flows and the column

- **The limit.** AIR-SV voxels are static in the lab frame, so the lateral *air* speed at each bead must stay ≤ the trim authority (~1–5 mm/s). By the slug model (§1.2), that needs **room cross-drafts ≤ 8–11 mm/s (U 0.06) to 15–21 mm/s (U 0.2)** [DERIVED, `r4_airsv.py` §5]. The brief's 20–100 mm/s exceeds it by 2–10×.
- **A guard.** A guard annulus at ~5× U cuts the core's lateral velocity by ~5×, because the guard fluid spends 5× less time in the cross-flow and channels the core [ESTIMATE]. Three costs:
  - a 0.3–0.5 m/s draft on people;
  - a ΔU ≈ 0.4 m/s shear layer whose u′ ≈ 6 cm/s eats 5–10 cm of core;
  - +5–10 dB of fan noise.

  It then tolerates ≤ 40–100 mm/s only at the optimistic end.
- **Core uniformity.** The core must equal v_s to ±1–5 % *everywhere and for minutes*. That needs temperature uniformity of ≤ 1–3 mK at 1–2.5 cm scales (§1.2, rows "temperature non-uniformity") and fan control to ±0.1 %. The beads' mean drift can serve as the fan's sensor.

**Verdict: fails in an ordinary room. A vitrine (enclosure) would fix it, but breaks "open air" and touch.**

### 2.3 Bead–bead hydrodynamics and collective sedimentation [DERIVED, `r4_airsv.py` §2]

The Oseen length ν/U is 0.14–0.28 mm, so at 3–10 mm spacing the far field is Oseen, not Stokes. Each bead exerts F = mg on the air:
- a **source flow** outside its wake: u = F/(4πρU r²);
- a **wake deficit** downstream (above the bead, in an upflow): u = F/(4πμx)·exp(−U s²/(4νx)), with 1/e radius √(4νx/U).

| Bead (a, ρ, U) | Lateral neighbour at 3 mm | In-wake neighbour at 3 mm | Top of a vertical stroke, 3 mm spacing: 1 / 3 / 10 / 30 cm | Stroke tilted 20° / 30° / 45° (100 beads) | m21 assumption |
|---|---|---|---|---|---|
| 30 µm, 600, 62 mm/s | 0.08 mm/s | 0.98 mm/s | 1.5 / 2.8 / 4.0 / 5.1 mm/s (≤ 0.48 mW, skin ok) | 1.2 / 0.6 / 0.17 | 0.46 mm/s Stokes lateral per neighbour |
| **40 µm, 600, 105 mm/s** | **0.11 mm/s** | **2.31 mm/s** | 3.5 / 6.5 / **9.4** / 12.0 mm/s, i.e. **1.1 / 1.6 / 2.0 mW per focus at 3 / 10 / 30 cm: fails EN 50689 (0.785 mW)** | 1.8 / 0.7 / 0.08 | 1.05 mm/s × 2 × 0.2 = 0.42 |
| 20 µm, 1200, 56 mm/s | 0.05 | 0.58 | 0.9 / 1.6 / 2.4 / 3.0 | 0.8 / 0.4 / 0.13 | 0.28 |

- **Horizontal strokes are 10× better than m21 assumed. Vertical and steep (< 20–30° from vertical) strokes are 5–25× worse.** At a = 40 µm the deficit fails the skin rule beyond ~3 cm of vertical stroke. At a = 30 µm it stays skin-legal but needs 4–10× m21's trim power.
- **Fixes:** sample steep strokes at ≥ 10 mm (1.0–3.6 mm/s); use smaller, denser beads (a = 20 µm, ρ 1200); or keep content ≥ 30° off vertical.
- **"80 % pre-compensated by design" has no mechanism.** Only light, local air speed or a per-position bead size can offset a wake. The last would mean sorting beads into ~0.1 % size classes and assigning them by position.
- **Sheets** (actuator disc): a filled horizontal patch at 3 mm pitch carries w_A = mg/δ² = 1.8×10⁻⁴ N/m². That induces v_i = w_A/(2ρU) = **0.7 mm/s at the sheet and 1.4 mm/s above it** (40 µm/600). This is comparable to the whole trim budget.
- **The whole image** (1 667 beads, 2.6 µN over 0.25 m²) produces a deficit of W/(ρUA) ≈ 0.08 mm/s. Negligible.

### 2.4 Time-shared pulsed IR trims [DERIVED, `r4_airsv.py` §1, §3]

**Force per absorbed watt for big beads.**
- `physics.py` (skin J₁/A 0.5, C_ph 0.85) gives F/P = 4.8 / 2.9 / 1.8 ×10⁻⁷ N/W at a = 40 µm for k_p 0.04 / 0.1 / 0.19 W/m/K (0.19 is solid PMMA).
- m21 uses 4.25×10⁻⁷.
- **I_unit for a 40 µm bead is therefore 1.1–6.0×10⁷ W/m² per m/s** (A 0.25–0.5), against m21's 1.5×10⁷. Trim power rises by up to ×4 for solid polymer beads.

**Response to a 0.1 ms kick.**
- Gas-side thermal time a²/α_air = 74 µs, so thermal creep follows the surface within the dwell.
- The surface dipole decays over the body's conduction time a²/α_p: 14.5 ms for PMMA.
- The system is linear, so the impulse is (F/P)·E_abs whatever the pulse shape (∫T₁dt equals the DC gain times the energy). Hot gas adds ×1.3 (μ²/(ρT) ∝ T^1.4).
- **Pulsing therefore loses no mean force.**

**But the lit face flashes:**

| Bead (a, ρ) | P_abs mean (m21) | K = 1000, 0.1 ms: solid PMMA / 1 µm glass shell | K = 300 | K = 100 |
|---|---|---|---|---|
| 30 µm, 600 | 11 µW | +78 K / +187 K | +23 / +56 K | +8 / +19 K |
| **40 µm, 600** | 37 µW | **+146 K / +352 K** | +44 / +105 K | +15 / +35 K |
| 40 µm, 1200 | 71 µW | +277 K / +669 K | +83 / +201 K | +28 / +67 K |

Formulas: semi-infinite solid ΔT = 2q√t/(√π·(e_p + e_air)), with e_PMMA = 568 W·s^0.5/m²/K; lumped glass shell ΔT = q·t/(ρ·c·t_w). m21's "+14–29 K" is the bulk average.
- PMMA's glass transition (105 °C, i.e. ΔT ≈ 85 K) and ITO's 573 K (ΔT ≈ 280 K) both need **K ≤ ~300** at 40 µm/600, so **3.3× m21's trim beams**.
- Revisit then improves from 0.1 s to 30 ms. The bead's per-kick jump du·T_rev falls from 116 to 35 µm, which also removes a ~3 % brightness flicker at 10 Hz inside a 490 µm spot (1 − exp(−2·58²/490²) = 2.8 %).

**Peak energies** of 6–30 µJ per pulse are ≪ 7.85 mJ (rule 1).

### 2.5 Bead material

**A white body with a 1550 nm skin** [ESTIMATE]:
- ITO on glass microspheres needs vacuum coating of powders, which is not commodity.
- A Cs-tungsten-bronze (CWO) nanoparticle skin in an acrylic binder is commodity for windows. It absorbs strongly at 1–2.5 µm with a slight blue-grey visible tint.
- A ~1 µm CWO-loaded skin should reach A ≈ 0.3–0.5 at 1550 nm, at the cost of ~5–15 % visible absorption, which tints and warms the bead.

**Size spread:**
- Commercial "monodisperse" microspheres have CV of 5–10 % (typical vendor statement, [MEASURED]); the best are ~1–2 % (recalled).
- AIR-SV needs 0.1–0.25 %. An elutriator (the column itself: a 1 % mismatch drifts 1 mm/s, i.e. 6 cm/min) can sort to that, keeping ~5–15 % of a 3 %-CV batch [DERIVED].
- Each bead's v_s can also be learned in situ from its mean trim.

### 2.6 Bead placement and content-change time

**Transport speed is capped by the skin rule.**
- Light carries a bead at E/L = h·I_unit·πw_t²/2 = **170 mJ/m** (a = 40 µm, w_t = 60 µm).
- The EN skin cap (0.785 mW, i.e. 7.85 mJ per 10 s through 1 mm) therefore limits each focus to **4.6 mm/s**: **22 s per 10 cm, 1.8 min per 0.5 m** [DERIVED].
- Bursts do not help: the 10 s budget is the same 7.85 mJ.
- Loading from the column base at mm/s takes 10²–10³ s for a 1 m image.

**AIR-SV is a slowly morphing sculpture.** It fails R6 (animation) and interactive R7.

### 2.7 Touch, noise, safety, cost

- **Touch.** A warm hand's plume (35–400 mm/s, m18d) exceeds the trims (1–5 mm/s) by 10–400×. Beads above and around the hand are blown up and out, and rebuilding takes minutes.
- **Noise.** 35–45 dB(A), including the guard.
- **Safety.** Beads are 60–120 µm in diameter, inhalable fraction ~0.5, not thoracic, and the inventory is ~0.3 mg: negligible. IR stays within EN 50689 except for vertical strokes (§2.3).
- **Visible light.** m21's design (w_v 370–490 µm, one 4K LCoS per head) is right for static content. 98.7 % of the 0.43 W of visible light misses the beads and must end in the black pedestal honeycomb.
- **Speckle.** Static coherent spots on 60–80 µm beads freeze it: grain 6–8 mrad against a pupil's 3.3 mrad at 1.5 m. Each bead shows a fixed random brightness per viewer that changes as the viewer moves. This needs wavelength or angle diversity.
- **Cost** [ESTIMATE]:
  - column with guard: $2–6k;
  - 4 × (4K LCoS + RGB): $16–40k;
  - 1550 nm EDFA: $2–5k;
  - 12–16 galvo trim channels: $3–8k;
  - cameras: $4–10k;
  - beads and sorting: $1–3k;
  - **total $30–70k**.

### 2.8 Verdict on AIR-SV

**Killed for an open home room.** The reasons, with numbers:
- cross-draft tolerance 8–21 mm/s against 20–100 mm/s;
- touch destroys content, which takes minutes to rebuild;
- content changes at ~4.6 mm/s per bead;
- vertical strokes fail the skin rule at 40 µm;
- pulsed trims need ×3.3 beams;
- no passive 3D stability exists.

**What survives:** a "levitated bead sculpture" in a still or enclosed space. It is a genuinely new static-voxel display that beats B9, because the air bears the weight and light trims only ~1–5 mm/s. Its probability is about 0.3 as a sculpture and ≤ 0.02 as the home vision [ESTIMATE].

---

## 3. FLOW-X versus AIR-SV (and FLOW-R)

| Criterion | FLOW-X (targeted) | AIR-SV | **FLOW-R (rain)** |
|---|---|---|---|
| Tolerated cross-draft | ~0.1 m/s (common mode, tracked) | **8–21 mm/s** | ~0.1 m/s |
| Needed Tu / thermal uniformity | ≤ 0.05 % for ±0.5 mm targeting (fails at home) | ≤ 1–3 mK, ±1–5 % profile | **insensitive** (Tu 1 % fine) |
| Content latency | 1.2–5 s | minutes | **one frame (33–50 ms)** |
| Content speed | any, once supplied | ≤ 4.6 mm/s per bead | **any** |
| Hand in the volume | everything below the hand lost | beads blown off; minutes to rebuild | near wake plus a 7 cm shadow lost |
| IR / photophoresis | none | 1550 nm trims, skin-limited | **none** |
| Visible engine | 40–400 spots, w 100 µm | 4K LCoS per head (static) | 8–80 spots, w 80–140 µm |
| Particles | 0.4–7 g/h, 10–22 mg/m³ in column | ~0.3 mg inventory | 0.5–11 g/h, 13–35 mg/m³ in column |
| Hard part | 2D on-demand injector | still air plus touch | **real-time 3D tracking (0.05–0.2 ppp)** |
| Home desk P [ESTIMATE] | 0.15 | 0.02 (open), 0.3 (enclosed) | **0.45** |

**Of the two briefed leads, FLOW-X is the better one. Its rain form, FLOW-R, is the best home route I can find.**

---

## 4. The needle: other routes against the home constraints

| # | Route | Deciding numbers | Rule it bends | Verdict |
|---|---|---|---|---|
| 1 | **FLOW-R** (uniform rain plus gated visible spots) | §1.4 table: 1.6×10⁵–1.4×10⁶ motes/s, optical depth 0.08–0.3 %, ≤ 0.39 mW per beam, latency one frame | gas/fog (sub-visible medium), table (pedestal) | **Top idea** (§5) |
| 2 | **Electrostatic weight support** (charged 40 µm beads in a vertical field, light trims only) | q at the Gauss limit (3 MV/m surface field) = 5.3×10⁻¹³ C, so E = mg/q = **3.0 kV/m** (below the 10–45 kV/m perception range). But drafts act directly on the beads: 5 mm/s already needs 0.85 mW per focus (skin 0.785) | room electrodes | **Dead**: needs ≤ 4 mm/s still air, and the B9 power is ∝ w² ∝ a² [DERIVED] |
| 3 | **Charged motes inside FLOW-R** (steering and capture) | a 2 mm/s lateral trim needs E = 6πμa·v/q = 0.2–0.4 kV/m (full charge) or 2–4 kV/m (10 % charge). Space charge at full charge (n 1.6–4×10⁷ /m³) pushes the cloud outward at 14–110 mm/s; at 10 % charge, 0.14–1.1 mm/s | none new | **Useful lever**: common-mode drift correction plus a grounded inlet field for capture. Induction-charge the inkjet drops [DERIVED] |
| 4 | **Bead or drop rain** (gravity POV, no column) | v_t 0.5–6.7 m/s for 0.3–2 mm beads. Draft σ 0.05 m/s scatters 0.3 mm beads by ~10 cm and 2 mm beads by < 1 mm. But ~10⁴ beads/s of 2 mm (4.2 mg each) is ~40 g/s (150 kg/h) recirculated; impacts carry ~1 W (rain noise, ~60 dB [ESTIMATE]); hands are pelted | table (catch basin), "a fountain" | **Dead** for home: mass flow, noise, touch [DERIVED] |
| 5 | **Helium-filled soap bubbles** (neutrally buoyant 0.3 mm seeds) | no settling, but no holding either: 2 cm/s of draft needs F = 1×10⁻⁹ N, i.e. 0.31 W of radiation pressure. Visible unlit, burst wet on touch | gas (helium), visible medium | **Dead** [DERIVED] |
| 6 | **Acoustic POV** (MATD) | demonstrated: 16 × 16 arrays at 23.4 cm, 8.75 m/s vertical [MEASURED]. Trap SPL ~150–160 dB at 40 kHz [ESTIMATE] against 110 dB occupational / ~100 dB public [MEASURED]. Pets hear 40 kHz | table/box between arrays | **Dead** for home (as the repo found) |
| 7 | **Uniform rain with nonlinear selection** (upconverting motes, crossed 980 nm and 1.5 µm beams, as in Downing 1996) | need ~10 µW visible per lit mote; upconversion ~1–3 % at 10 W/cm² (recalled), and a 7 µm Yb mote absorbs ~1–2 % (α ~10 cm⁻¹). That means ~50 mW per lit mote, against the 980 nm Class 1 limit of 1.43 mW | none | **Dead by ~30–100×** [ESTIMATE] |
| 8 | **Photochromic light-sheet selection** in motes (the 2020 solution-based light-sheet display idea) | merocyanine fluorescence QY of a few %, with a 405 nm photochemical Class 1 limit of 39 µW per pupil. Each lit mote needs ~10 µW out | none | **Dead / marginal** [ESTIMATE] |
| 9 | **EHD (ion-wind) silent column** | corona makes ozone at ppb–ppm locally, against a ~50 ppb indoor limit (recalled) | ozone | **Dead** |
| 10 | **Eye tricks** (saccade "phantom arrays", retinal scanning from room heads) | no stable 3D location; and by T1 Theorem 1 the apparent direction is bounded by the head's aperture | — | **Dead** |
| 11 | **Retroreflective glove plus per-viewer heads** (correct occlusion on the hand) | retroreflection cone ~0.5–1° means a head within ~3.5 cm of each eye at 2 m, which is effectively eyewear | glasses | **Dead** as a route. The **black glove as a beam dump** (§1.4) is the useful remnant |
| 12 | **Aerial-imaging plate** (dihedral corner-reflector array) plus a glove | real image in open air, 10–30 cm in front of the plate; **viewing angle 40°** (ASKA3D-200NT) [MEASURED]; touch via hand tracking; plates from 200 to 1 050 mm | not a holo-table/wall (the plate is a window); not all-around | **Works today**, but it is the holo-window the owner excluded |

---

## 5. The nearest home-buildable variant: a desk FLOW-R "holo-pedestal"

**Architecture.**
- **Hood above.** An arm- or ceiling-hung hood, 0.45 × 0.45 m. It contains:
  - a push outlet (fan, screens, then mote injection, then a 3 mm honeycomb, with no screens after injection);
  - the mote generator: an HP45 firing a ~7 % trehalose/mannitol solution (30 pL → 14 µm motes) into a heated drying duct whose ~12 W latent sink is reheated, with induction charging;
  - 2–3 visible heads at 30° off vertical;
  - 2–4 tracking cameras with an 850 nm LED flood.
- **Pedestal below.** A 0.5 m pedestal inlet ~0.45 m below the outlet: black louvres (the beam dump), a grounded capture grille, a filter and the pull fan.
- **The image** floats in open air between the two: no walls, so people can walk round it and reach in.
- **Air:** 0.25 m/s down.
- **Lighting:** each tracked mote that crosses content gets a gated spot of w_v 80 µm at ≤ 0.39 mW per beam.

**Specification and relaxations against the vision:**

| Vision requirement | Desk FLOW-R delivers | Relaxation, and by how much |
|---|---|---|
| Floating in open air | ✓ image in free air; no enclosure; hands enter | — |
| Not a holo-table/wall | hood 0.45 m above, pedestal inlet 0.5 m below | **bent**: a "holo-pedestal". The room-scale version can use a ceiling hood and a floor grille |
| No gases (fog) | clean room air carrying food-grade 10–14 µm motes at 13–35 mg/m³; optical depth 0.08–0.15 % (unlit column invisible at < 1 % contrast) | **bent**: a sub-visible particle stream, 30–1 000× thinner than a fog screen [ESTIMATE]. Owner's ruling |
| No glasses, no screens | ✓ | — |
| Touchable (glove allowed) | hand in the volume; content above the hand intact; ~8–16 cm near wake plus a 7 cm shadow lost below it; black, isothermal, haptic glove | partial: a local shadow under the hand |
| Visible from all around | 360° in azimuth (p = 0.76–0.86 ±6 %); from above down to ~20° below the image's horizon | elevation-limited |
| Size and content | 0.2 m image; **0.5 m of strokes** (B′) to 1 m (A); 20–30 Hz; 3–5 mm sampling; sparkly (Poisson, 13 % dropouts per 0.1 s at N_s = 1) | **×5 smaller and ×10 sparser** than an Iron-Man room sketch (~1 m, 5 m of strokes) |
| Brightness | 1.5–3 cd/m² lines (Class-1-capped per beam); dim room (surfaces ≲ 5–10 cd/m²) | dim room only |
| Animation and interaction | any content speed; one-frame latency plus tracking (≤ 50 ms) | ✓ (the decisive gain over FLOW-X and AIR-SV) |
| Colour | RGB lasers on white motes, or fluorescent motes | ✓ |
| Safe for everyday use | visible Class 1 per beam (B′) with a scan-fail cut; no IR, no UV; ≤ 30 dB(A); 0.25 m/s breeze (DR 14 %); room particles 1.8–18 µg/m³ at 99.9–99 % capture; non-polymer edible motes | needs ≥ 99 % capture and an owner's ruling on the medium |
| Room conditions | tolerates people and ~0.1 m/s drafts (common mode); HVAC need not pause | inlet oversized by 5–10 cm per side |

**Parts class and cost** [ESTIMATE]:

| Block | Commodity parts | Cost |
|---|---|---|
| Air | 2 quiet PWM fans or a small EC blower; 3 mm aluminium honeycomb; stainless screens; F7/HEPA panel; acoustic foam; frame | $0.5–1.5k |
| Motes | HP45 cartridge plus an open controller; heated drying duct; trehalose/mannitol (food or pharma grade, ~$20–60/kg; 0.5–1.2 g/h) | $0.3–0.6k |
| Tracking | 2–4 global-shutter machine-vision cameras (2–5 MP, 100–200 fps) with lenses; 850 nm LED flood; GPU PC | $3–7k |
| Visible engine | 2–3 heads, each with RGB multimode diodes and 2 ILDA galvo pairs plus a scan-fail board (a 2D AOD per head is the quieter upgrade, +$6–15k) | $1.5–4k |
| Capture / charging | inlet grille at 1–3 kV/m from a µA-limited supply; induction ring at the nozzle | $0.1–0.3k |
| Glove | matte black, isothermal; vibrotactile haptics | $0.1–0.5k |
| **Total** | | **$5–12k** (galvo) / **$12–25k** (AOD) |

**What blocks scaling it to the room** (a 0.6 × 1 m image, 5 m of strokes) [DERIVED/ESTIMATE]:
- **Tracking.** About 5.8×10⁶ motes are in flight, i.e. ≈ 0.5 particles per pixel even at 12 MP. Multi-camera 3D particle tracking works up to ~0.1–0.2 ppp with flow-predicted trajectories, so this needs ~6–8 high-resolution cameras and custom real-time tracking.
- **Spots.** 80+ simultaneous gated spots.
- **Air.** 1 100 m³/h of quiet air handling.
- **Capture.** 99.9 % recapture.

That is startup scale, at ~$50–150k, not a home build.

---

## 6. Ranked list

| Rank | Idea | Why | P [ESTIMATE] |
|---|---|---|---|
| **1** | **FLOW-R desk holo-pedestal** (uniform food-grade mote rain in a guarded downward column; tracked, gated visible spots; no IR) | Only route with open air, all-round view, interactive latency, passive visible Class 1 and commodity parts. It bends "no gas" and "not a table" | 0.45 that a desk demo meets its own spec; ~0.1 at room scale on a home budget |
| 2 | Aerial-imaging plate plus glove | Exists and is touchable, but it is a 40° holo-window | 0.95 works; low fit to the vision |
| 3 | FLOW-X targeted (as briefed) | Fewer motes only at Tu ≤ 0.05 %; no 2D injector; 1.2–5 s latency | 0.15 desk / 0.05 room |
| 4 | AIR-SV | Dead in open rooms; works as an enclosed, slowly morphing sculpture | ≤ 0.02 open / 0.3 enclosed |
| 5 | Photophoretic routes (T7, T8 POV-X) | Unchanged by this round: not home (B9, skin rule, 10³–10⁴ channels or 10¹⁰ modes) | see v5 |
| 6 | Acoustic POV (MATD) | 150–160 dB against a 100–110 dB limit; a box | dead |
| — | Electrostatic weight, bead/drop rain, helium bubbles, upconversion and photochromic selection, EHD, eye tricks, retroreflective glove | §4 numbers | dead |

---

## 7. Weeks-scale bench test for FLOW-R (6 weeks, ~$4–8k)

**Goal.** Decide whether a home desk column can (1) contain an invisible mote rain, (2) be tracked, and (3) be lit per mote within Class 1 to the B′ spec.

**Week 1–2. Column and containment.**
1. Build a 0.3 m nozzle (fan, 2 screens, then the seeding plane, then a 3 mm honeycomb, 40 mm long) and a pedestal inlet 0.45 m below (0.45 m louvres plus a filter), with pull/push ratio 1.5–2.
2. Seed it with the mote generator (week 2). Measure:
   - the core velocity and Tu by particle tracking;
   - core width against height.
3. Repeat the measurements with:
   - a box fan giving 0.05 and 0.1 m/s cross-draft at the column (checked with a hot-wire);
   - a person walking past at 1 m;
   - a bare hand and a gloved hand in the volume.
4. **Pass:**
   - the seeded core is ≥ 0.2 m wide at the inlet with a ≥ 5 cm guard;
   - common-mode shift ≤ 3 cm at 0.1 m/s.

**Week 2–3. Motes and capture.**
1. Drive an HP45 with ~7 % trehalose at ~5 kHz on ~30 active nozzles into a 40 °C drying duct with reheat. Size the dried motes on sticky slides under a microscope. **Target:** 12–14 µm, CV ≤ 5 %.
2. Run at 1.6×10⁵ /s. Measure escape with an optical particle counter (PM10 channel) at 0.5–1 m around the column and with sticky slides on the floor, under each disturbance of week 1, with and without the grille field.
3. **Pass:**
   - capture ≥ 99 % with a person walking and a 0.1 m/s draft;
   - room PM10 increment ≤ 20 µg/m³ after 1 h;
   - unlit column contrast ≤ 0.5 % against a 30 cd/m² background (calibrated camera).

**Week 3–5. Tracking and gated light.**
1. Use 3 cameras (2–5 MP, 150–200 fps) with an 850 nm flood. Run predictive 3D tracking in a 0.2 m cube at the B′ density (expected 0.05–0.1 ppp in the cube).
2. Add one head: an RGB multimode diode, an ILDA galvo with w_v 80 µm, and a scan-fail board. Light only the motes that cross a programmed 1 mm × 5 cm stroke.
3. Measure:
   - luminous intensity per lit mote against the model (p = 0.76–0.86 × ω);
   - gating jitter, against a target of ≤ 40 µm at the spot;
   - ghost rate;
   - beam power through a 7 mm aperture at the worst points (in the volume and on the stroke);
   - stall-to-cut time.
4. **Pass:**
   - ≥ 1.5 cd/m² on the stroke at ≤ 0.39 mW per beam;
   - ghost rate ≤ 3 %;
   - pupil mean ≤ 0.1 mW;
   - end-to-end latency ≤ 50 ms;
   - tracking keeps ≥ 90 % of motes that cross the stroke.

**Week 5–6. Integrated glyph and people.**
1. Show a 10 cm ring plus a crosshair (~0.5 m of strokes) at 20 Hz with 2 heads.
2. Run a 5-person viewing study: sparkle and speckle acceptability with multimode and with fluorescent motes, flicker, and haze visibility.
3. Measure the hand-shadow extent, and noise in dB(A) at 1 m.
4. **Pass:**
   - viewers rate the glyph "floating and legible" from all azimuths;
   - hand shadow ≤ 15 cm;
   - ≤ 30 dB(A).

**What a fail means.**
- **Capture < 99 %:** FLOW-R needs a vitrine, and the open-air claim falls.
- **Tracking < 90 %:** shrink the volume, or move to the coarse "regional rain" (seed only the content's footprint).
- **Brightness short at Class 1:** use bigger motes (L ∝ a²) or smaller spots with per-spot focus.

---

## 8. Notes for the main session

1. **m20 (FLOW-X)** needs these corrections:
   - add floor deposition (v_s/H) to the room level; it is 13–50× lower;
   - replace w_v = 2.5a with the Class-1-limited w_v and count spots or channels, not 10⁹ modes;
   - use the Lambert p(α) with top lighting (0.76–0.86) instead of q = 0.3;
   - add a home-Tu row (0.5–1 %), where targeting collapses to rain;
   - the co-moving 300 Hz hologram is not commodity.
2. **m21 (AIR-SV)** needs these corrections:
   - replace the Stokes neighbour term with Oseen: source 1/r² laterally, wake F/(4πμx) vertically, harmonic sums along steep strokes;
   - replace the bulk ΔT_kick with the lit-face flash, which gives K ≤ ~300;
   - take F/P for big beads from `physics.py` (k_p 0.04–0.19);
   - add the cross-draft tolerance (≤ 8–21 mm/s) and the divergence-free no-trap statement;
   - the revisit period must be ≤ ~30 ms (loop Nyquist).
3. **A general result for every air-carried route** [DERIVED]: in any incompressible flow, inertia-free particles have a solenoidal velocity field, so **no passive 3D trap exists**. Air can carry or bear weight, but holding needs active forces.
4. **The structural reason the visible side works here and failed in T7 and RT7 C1:** once the air bears the weight, motes can be 10–14 µm and white (Lambertian), and sparse motes allow spots 6–20× their radius. Visible Class 1 and the engine count both close at desk scale. The bottleneck moves to **particle tracking**, which is software and camera pixels, not physics.
5. **Open items I did not settle:**
   - push–pull capture with people around (needs measurement);
   - real-time 3D particle tracking at 0.05–0.2 ppp on a home GPU;
   - the owner's ruling on "a sub-visible food-grade mote stream" and "a pedestal inlet";
   - EN 50689's treatment of a scanned visible beam with a scan-fail cut.

## Sources

**Web (this session, 7 searches)**
- Acoustic trap display, 16 × 16 arrays at 23.4 cm, 8.75 m/s: [Hirayama et al., Nature 575, 320 (2019)](https://www.nature.com/articles/s41586-019-1739-5).
- HP45 thermal inkjet: 300 nozzles, 600 dpi, 29–35 pL, 12–18 kHz, ±5 % drop volume: [Phoenix Digital Solutions HP45](https://phoenix-digital-solutions.com/products/hp45-inkjet). Open controllers: [HP45 Controller V4](https://ytec3d.com/hp45-controller-v4/); [Oasis 3DP](https://hackaday.io/project/86954-oasis-3dp).
- Fan filter unit noise of 42–56 dB(A) at 0.45 m/s, 100 Pa: [SCT cleanroom FFU guide](https://www.sctcleanroom.com/news/complete-guide-to-ffufan-filter-unit/); [Mayair FFU brochure](https://mayairgroup.com/wp-content/uploads/2024/07/Fan-Filter-Brochure-INTLM-B-FFU-U-E-V1-R1-2403-3.pdf).
- EU synthetic polymer microparticle restriction and its "contained by technical means" derogation: [Regulation (EU) 2023/2055](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32023R2055); [European Commission page](https://single-market-economy.ec.europa.eu/sectors/chemicals/reach/restrictions/commission-regulation-eu-20232055-restriction-microplastics-intentionally-added-products_en).
- Monodisperse polymer microspheres, typical CV 5–10 % (search summary): [Polysciences PMMA microspheres](https://polysciences.com/products/polybead-polymethyl-methacrylate-microspheres-monodisperse).
- Aerial imaging plate, 40° viewing angle, sizes 200–1 050 mm: [ASKA3D (Auronova)](https://auronova.com.sg/product/aska-3d-media-players/); [Display Daily on ASKA3D](https://www.displaydaily.com/paid-news/ldm/ldm-event-reports/ldm-company-event-reports/aska3d-is-not-just-pepper-s-ghost).
- Airborne ultrasound limits (110 dB above 25 kHz; public −10 dB): [ICNIRP statement 2024](https://www.icnirp.org/cms/upload/publications/ICNIRPUltrasoundStatement2024.pdf); [review of airborne ultrasound limits](https://www.researchgate.net/publication/235923211_A_review_of_current_airborne_ultrasound_exposure_limits).
- Honeycomb reducing Tu from 30 % to 1.2 %: [Flow conditioning (Wikipedia)](https://en.wikipedia.org/wiki/Flow_conditioning); [NASA TM-81868, screens and honeycomb](https://ntrs.nasa.gov/api/citations/19810020599/downloads/19810020599.pdf).

**Repository (read-only):**
- `09_unlock/m20_flowx.py`, `m21_airsv.py`, `results/m20_run.log`, `results/m21_run.log`, `m18d_touch_air.py`;
- `idea_round_3_opus.md` (open-jet Tu 0.1 % with contraction, potential-core lengths);
- `idea_round_3_sonnet.md` (EN 50689 skin rule, plume and room sources);
- `05_reviews/red_team_7_gaussian.md` (C1, M8, M9), `red_team_8_pov_x.md`, `FINAL_VERDICT.md` (v5);
- `02_theory/T1_what_physics_allows.md`;
- `07_mote_route/mote/physics.py`, `safety.py`.

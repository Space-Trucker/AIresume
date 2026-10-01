# T6: Bounds, invariants and loopholes for any matter-at-the-point display (draft v1)

*Status: theory draft, written 2026-10-01 before idea round 2 reports. Every claim is tagged [DERIVED], [MODEL] (computed in `m15_lightcurtain_static.py` with the validated MOTE physics) or [ASSUMPTION].*

## 1. What cannot be avoided

**Theorem T1 (from T1).** A free-space image visible from all around needs light made or scattered **at the image point**. Air alone cannot do it without plasma. So the image needs **matter at the point**: motes or beads. That matter must be held, positioned and lit. [DERIVED, T1]

**Bound B2: holding intensity.** A photophoretic mote of radius a, moving at speed w relative to the air, needs an intensity at the mote of

  I_hold = 4·ρT·h·w / (3·η·C_ph·μ·FOM·A·Cc)

where:
- ρT = p/R_air = 353 kg·K/m³;
- h ≥ 1 is the push-geometry overhead (octahedral push: √3 worst case);
- η ≤ 1 for pushes, ≤ 2/π for lateral gradient traps;
- FOM = (J₁/A)/(k_eff + 2k_g).

I_hold does **not depend on mote size**. [DERIVED from the validated force law; checked in `m15 --selftest` within 5 %]

Example: w = 0.1 m/s, FOM 4.1, η = 1, h = 1, margin 1.3 → I_hold ≈ 1×10⁶ W/m².

**Bound B3: heat.** ΔT = A·a·I/(4k_g). At I_hold this is 76 K for a = 5 µm at w = 0.1 m/s, and 195 K at w = 0.3 m/s (octahedral push). Small motes run cool. [DERIVED]

**Bound B4: the light must stay with the mote.** The trap light fills a spot of radius r_c that contains the mote's position uncertainty. So the power at one focus is P_focus = h·I_hold·π r_c²/η_shape. [DERIVED]

**Bound B5: addressable modes.** To put such spots anywhere in a field of area A_f, each head needs M = A_f/(π r_c²) independent modes (pixels of a hologram, or resolvable spots of a scanner). [DERIVED; étendue]

**Bound B6: control.** The mote must be pushed back before it leaves its spot: f_ctrl ≥ k·u/r_c. A passive (feedback-free) trap needs gradient features of size ~a, so r_c ~ a. [DERIVED; M2 earlier found 20–50 kHz at r_c = 20 µm, u = 0.3]

**The invariant.** Combining B4 and B5 for N motes:

  **P_total · M = N · h_mean · I_hold · A_f / (η_shape·η_holo)** [DERIVED; checked in m15 self-test]

Combining with B6:

  **P_total ≥ N · π·h·I_hold·(k·u/f)² ∝ N·u³/f²**, since I_hold ∝ u.

**Drafts enter cubed.** A normal room (0.3 m/s) costs **27×** the power of a quiet one (0.1 m/s) at the same control rate. [DERIVED]

**Class 1 per focus** (P_focus ≤ 10 mW at 1550 nm) forces r_c ≤ 27 µm at 0.3 m/s. That is why v4 needs 10³–10⁴ precisely steered beams. [DERIVED]

**Acoustic beam-cone bound.** A trap bead needs ~150–160 dB at the bead and carries ~0.03–1 W of ultrasound. At distance d from the focus, a beam of half-angle θ spreads that power over π(d·tanθ)². At d = 0.3–1 m that is still 105–120 dB. The public limit is 100 dB (IRPA, 25–100 kHz), and no guideline exists above 100 kHz. **Any listener inside a beam cone within ~1 m of a bead exceeds the limit.** [DERIVED with R3 limits; sharper than E9's room-average argument]

## 2. Loopholes (each bound's non-fundamental assumption)

| Bound | Assumption | Loophole | Status |
|---|---|---|---|
| B4 Class 1 per focus | An eye can stay at a focus for ≥ 10 s | **Monitored-beam "light curtain"** (I1): every beam ends on a receiver that measures its transmitted power. Any intercept above θ_det cuts it within t_cut. The hazard becomes (a) an undetected partial intercept ≤ θ_det·P_focus ≤ AEL, and (b) the dose during the cut ≤ the short-exposure MPE | **Candidate.** Standards fit (IEC 60825-1 classification with engineering controls; IEC 60825-4 active guards; IEC 61496 light curtains) is under review by idea round 2 |
| B7 light budget | Light from a phosphor pumped by a 405 nm beam; unabsorbed pump reaches the walls | **Terminated scattering illumination** (I3): a visible spot lights the mote, and its beam ends in a receiver, so walls see no direct light. This removes T5's reason for rejecting scatterers (Babinet forward light reaching the walls) | **Candidate.** It also allows **black motes** (no visible transparency needed), hence a known-material mote: carbon aerogel |
| Material | The absorber must be visible-transparent (ITO/Cs_xWO₃ islands) | With I3, a **carbon-aerogel microsphere** works: black, k ≈ 0.03–0.05 W/m/K (bulk), skin-like absorption. FOM ≈ 3–4.4 from bulk data | **Candidate.** Bulk-property estimate; k at µm size still needs measuring (B2 bench) |
| Mote speed | POV needs fast motes (S·f/v motes) | **Static voxels** (I2): motes sit at the image points (spacing δ) and move only with the content. Each mote needs force only against drafts. Content speed ≤ r_c × (hologram rate)/k | **Candidate for static and slow content.** Fast hand-manipulated objects still need POV channels |
| B6 control | Every mote needs its own fast loop through the hologram | **Split control** (I4): a slow hologram places the spots. A fast per-line-of-sight amplitude modulator (a DMD in an intermediate field plane, 10–20 kHz) sets each spot's force. Drafts are smooth on cm scales, so even zone-level control helps | **Candidate.** Needs per-mote position sensing at ≥ 10 kHz (event cameras or receiver detectors) |
| Drafts | Room air is uncontrolled | The power cost ∝ u³ makes **room air speed the master variable**. Quiet zones (≤ 0.1–0.15 m/s) are realistic with calm HVAC (ASHRAE comfort ≤ 0.2 m/s). Human thermal plumes are 0.1–0.25 m/s near hands | No loophole found; design for u ≈ 0.1–0.15 m/s with margin |

## 3. Candidate architecture LCSV (light-curtain static voxels)

**Heads and beams.**
- Six heads in an octahedral layout: three opposed pairs, set "gracefully" on ceiling, floor and walls (the owner allows many heads).
- Each head is an emitter and a receiver.
- **Emitter:**
  - 1550 nm laser, fed through a phase-hologram tile array that places flat-top spots of radius r_c at each mote;
  - a DMD amplitude plane for fast per-spot force;
  - a visible (cyan, plus optional orange or RGB) illumination hologram.
- **Receiver:** monitors every incoming beam (curtain) and senses each mote's shadow and position.

**Motes.** Carbon-aerogel microspheres, a ≈ 5 µm, about 0.05 ng each. A film-density image uses 15,000–30,000 of them, about 1 µg in total.

**First-pass numbers** (M15, carbon aerogel FOM 4.1, octahedral push, curtain safety):

| Case | N motes | r_c | 1550 nm total | Visible total | Modes per direction | Notes |
|---|---|---|---|---|---|---|
| Sketch, quiet (0.1 m/s), δ = 2 mm, fast 1.4 kHz device | 2,500 | 21 µm | 13 W | 0.15 W | 7×10⁸ | Pixel count is the cost driver |
| Sketch, quiet, 4K LCoS at 360 Hz | 2,500 | 83 µm | 177 W | 10 W | 5×10⁷ (31 SLMs) | Power is the cost driver |
| Film density, quiet, δ = 2 mm, fast device | 15,000 | 21 µm | 80 W | 1–6 W | 7×10⁸ | |
| Any content, normal room (0.3 m/s) | | | ×27 power | | | Infeasible at fixed modes |

**Second pass: split control and a stray-light fix (M15b/M15c, `results/m15b_split_control.json`, `m15c_capped.json`).**
- **Split control.** The spot radius is now set by the fast amplitude loop (20 kHz DMD plane, 2 kHz loop bandwidth, mote jitter = u/(2π·bw): 8 µm quiet, 24 µm normal), not by the slow hologram.
- **Stray light.** The criterion is now *added wall luminance* ≤ 0.01 cd/m². Light leaking from the receivers (10⁻³) spreads over ~50 m² of walls. budget2's 5 %-of-flux rule assumed pump light striking walls directly.
- **Optimisation.** Both radii (r_c, r_v) are cost-optimised, with total 1550 nm capped at 100 W:

| Content | Room u | Motes (δ) | r_c | IR total | Visible | Hologram pixels (all heads) | Content speed | Cost, volume / lab [ASSUMPTION prices] |
|---|---|---|---|---|---|---|---|---|
| Accent | quiet / calm / **normal** | 333–500 (2–3 mm) | 72–152 µm | 87–97 W | 0.2–0.3 W | 1.7–4.2×10⁸ | 0.9–1.8 cm/s | $19–27k / $0.3–0.6M |
| Sketch | quiet / calm | 1,667–2,500 | 44–69 µm | 90–100 W | 0.9 W | 4.9–11×10⁸ | 0.5–0.8 cm/s | $29–46k / $0.7–1.3M |
| Sketch | normal | 1,667–2,500 | 72 µm | 316–474 W | 0.5 W | 5×10⁸ | | fails the 100 W cap |
| Film density | quiet, δ = 3 mm | 10,000 | 28 µm | 98 W | 1.4 W | 2.9×10⁹ | 0.3 cm/s | $102k / $3.4M |
| Film density | calm / normal | | | 240–2,800 W | | | | fails the cap |

These are model results with white-coated carbon-aerogel motes: FOM 3.4, side albedo 0.3 [ESTIMATE].

For comparison, v4 POV needs ~12,200 steered beams for a sketch ($8.6–61M) and ~50,000 for film density.

**What carries the gain.**
1. The curtain lets each focus carry 25–200 mW instead of ≤ 10 mW, so spots can be 3–10× wider.
2. Static voxels need force only against drafts, not against tracing speed.
3. Holographic parallelism replaces one galvo per beam.
4. Terminated scattering removes the 405 nm pump and phosphor, so black or carbon motes are allowed.

**Third pass: mote FOM computed from optical depth (M15c, `results/m15c_capped.json`).**

Carbon aerogel (5 % solid) is a **volume** absorber with α ≈ 3×10⁵ m⁻¹ [ESTIMATE]. At a = 5 µm, αa = 1.5, which gives J₁/A ≈ 0.2 and FOM ≈ 1.6 with a white coat. At a = 10 µm, J₁/A ≈ 0.30 and FOM ≈ 2.5. That corrects the FOM 4.1 I had assumed in passes 1–2.

With a 100 W IR cap and δ = 3 mm:

| Content | quiet (0.10 m/s) | calm (0.15) | normal (0.30) |
|---|---|---|---|
| Accent, 10 µm white carbon | ✓ 98 W, 1.3×10⁸ px, $18k vol / $0.28M lab | ✓ | ✗ heat (ΔT 460 K) |
| Sketch, 10 µm white carbon | ✓ 100 W, 5.4×10⁸ px, $30k / $0.73M | ✓ 94 W, 8.3×10⁸ px, $39k / $1.05M | ✗ (393 W, heat) |
| Film density, 10 µm white carbon | ✗ 144 W | ✗ 302 W | ✗ |
| Sketch, ITO-aerogel mote (FOM 5.3, unmade) | ✓ 94 W, 3.4×10⁸ px | ✓ 89 W | ✓ at 193 W |
| Film density, ITO-aerogel mote | ✓ 92 W, 2.0×10⁹ px, $75k / $2.4M | ✓ at 173 W | ✗ (> 1 kW; limited by the fast loop's jitter) |

**Reading.**
- With a **known-material-class mote** (carbon aerogel, still unmeasured at µm size), the model reaches the **Iron-Man sketch in quiet or calm rooms**.
- **Film density** needs the better mote or ~150–300 W.
- **Normal rooms** need a faster force loop: jitter ∝ u/bandwidth sets r_c ≥ 72 µm at 0.3 m/s.

**Fourth pass: measured room layouts and hand occlusion (M15d, `results/m15d_layouts.json`).**

The ideal octahedron (h_worst 1.73) cannot push in all directions when one head is blocked. M4's measured layouts can:
- H10 (8 corners + ceiling spot + floor head): h_worst 2.14, h_mean 1.38, one-head-occluded p95 4.47.
- H14 (H10 + 4 wall niches): h_mean 1.28, occluded p95 3.73.

With ≤ 100 W IR and δ = 3 mm:

| Content / room | 10 µm white carbon mote (known material class, FOM 2.5) | ITO-aerogel mote (FOM 5.3, unmade) |
|---|---|---|
| Accent, quiet | ✓ (H10: 89 W, 2×10⁸ px); **local dropout near hands** (overheats with a head blocked) | ✓, holds with a head blocked |
| Accent, calm / normal | ✗ heat | ✓ (normal: H14 holds with a head blocked) |
| Sketch, quiet | ✓ (91 W, 8.7×10⁸ px, $48k vol / $1.2M lab); local dropout near hands | ✓ (86 W, 5.1×10⁸ px, $37k / $0.78M), holds with a head blocked |
| Sketch, calm | ✗ heat | ✓ (82–95 W) |
| Sketch, normal | ✗ | needs 163–176 W |
| Film density, quiet | ✗ (121–131 W) | ✓ (84–98 W, 3.1–3.4×10⁹ px, $114–131k vol / $3.6–4.0M lab) |
| Film density, calm | ✗ | needs 124–133 W |

**Reading.**
- **The mote's FOM buys robustness, not just cost.** The ITO-class mote keeps holding when a hand blocks a head; the carbon mote overheats there.
- The verdict's gate (FOM ≳ 4) stands for any image that the hands go *into*.

**Known gaps** (to be closed before any grade change):
1. **Black motes scatter weakly** (side albedo ~5 %), so wall stray light fails at 1 % leakage. Fixes to test:
   - tighter illumination spots, co-centred by the fast loop;
   - white-coated carbon motes (q ≈ 0.3);
   - receiver leakage ≤ 10⁻³.
2. **Hologram pixel count.** Slow LCoS is enough once split control is used, but film density needs ~3×10⁹ pixels, about 330 4K panels. Fast per-spot amplitude control needs one DMD per head at an intermediate field plane. Spots at different depths must stay localised there; my estimate is ~10 px blur at 1/50 demagnification. Per-mote position sensing at ≥ 20 kHz for up to 10⁴ motes is assumed, not designed (event cameras or receiver detectors). The jitter model u/(2π·bw) assumes ~80 µs loop latency; 150–200 µs would double r_c and the IR power.
3. **Content speed.** Holographic static voxels move at ~0.3–2 cm/s (r_c × hologram rate / 3). Hand-manipulated content needs hybrid POV channels, per-tile fast rigid transforms (a fast steering mirror for translation, focus for depth), or reduced density while moving.
5. **Hand occlusion.** A hand blocks every beam it crosses, and the curtain cuts them. With only 6 octahedral heads, a mote that loses its +x head cannot be pushed in −x. Robust touch needs 8–12 heads, as in v4's R12 rig, which costs pixels and power ∝ heads.
6. **Sensing.** Per-mote 3D position to ~10 µm at ≥ 20 kHz for 10³–10⁴ motes. A candidate is several event cameras with modulated illumination: ~2×10⁸ position samples per second in total. This needs design.
4. **Safety argument.** Whether IEC 60825-1/-4 accept a monitored-beam interlock as the primary safeguard for a consumer product.

## 3a'. Idea round 2 (materials and hardware) and real device rates (M15e, `results/m15e_real_devices.json`)

**Report:** `idea_round_2_sonnet.md`. Main-session checks:
- **Confirmed with physics.py.** An optically thick **plain black carbon aerogel mote** (a = 15 µm, α = 3×10⁵ m⁻¹, k = 0.035) has τ = 4.5, J₁/A = 0.35, **FOM = 4.05**, FOM·A = 3.95. At 10 µm, FOM = 3.4. Larger motes reach the FOM ≳ 4 gate with a material class that has measured bulk data.
- **Accepted: the white coat is thermally harmful.** A shell adds lateral conduction k_s·2t/a and roughly halves FOM·A. Passes 3–4 used an optimistic +0.01 W/m/K. The black mote (side albedo ~1–3 %) is preferred.
- **Accepted: real device rates.**
  - The phase hologram is a 4K LCoS (GAEA-2.1) at 60–180 Hz; no 8K phase LCoS exists.
  - The fast gate is a DLP650LNIR at **12.5 kHz**, not 20 kHz.
  - The TI PLM (1.44 kHz) is available by invitation only, with 4-bit phase and ~30 % efficiency at 1550 nm.
  - No single device gives 10⁸–10⁹ modes at kHz rates.
- **Sensing.** No SWIR event camera exists. Per-mote tracking at ≥ 20 kHz has to use visible-scatter event cameras (IMX636 class, ~1 Gev/s), split over 8–12 cameras.
- **Killed (with the numbers that kill them, in the report):**
  - Er³⁺ upconversion of the trap light;
  - visible trap beams;
  - third-harmonic generation;
  - hollow carbon spheres;
  - core-shell skins;
  - nano-absorber composites at the τ ≥ 3 needed;
  - carbon-black-opacified silica aerogel at µm size.

**M15e: H10 layout, ≤ 100 W IR, δ = 3 mm, 12.5 kHz gate, 180 Hz hologram.**

| Content / room | Black carbon 10–15 µm (FOM 3.4–4.1) | ITO-aerogel 5 µm (FOM 5.3, unmade) |
|---|---|---|
| Accent, quiet | ✓ 85 W, 2.6–5.8×10⁸ px (31–70 4K panels), $29–39k vol; **drops out near hands** | ✓ 84 W, 21 panels; holds with a head blocked |
| Sketch, quiet | ✓ 86 W, 0.7–1.1×10⁹ px (82–135 panels), $42–55k vol; drops out near hands | ✓ 86 W, 62 panels; holds |
| Sketch, calm | ✗ heat / visible-spot class | ✓ 82 W, 91 panels |
| Film density, quiet | ✗ 160–180 W | ✗ 102 W (just over the cap) |
| Any content, normal room | ✗ | ✗ (holographic mode) → use the fast-POV mode (§3c) |

**Net.**
- With a **known material class** (black carbon aerogel, still to be measured at µm size), the holographic static mode reaches an **Iron-Man sketch in a quiet room** using ~80–135 4K phase panels and ~86 W of 1550 nm.
- Robust touch, calm rooms and film density need the better mote.
- Normal rooms need the fast-POV mode.

## 3b. Content speed (I5), checked with the existing v4 machinery

**Bound B8, content speed.** Content cannot move faster than its motes can, relative to the air. The heat-limited mote speed is v_max ≈ 0.2–0.5 m/s with today's best-estimate motes (v4/M13). [DERIVED]

**Holographic static voxels are slower still.** Between hologram frames a mote can move at most ~r_c/k, so v ≤ r_c·F_holo/k:

| Hologram device | Content speed |
|---|---|
| LCoS (360 Hz) | ≈ 1–2 cm/s |
| PLM-class (1.44 kHz) | ≈ 4–8 cm/s |

[MODEL]

**Elongated "track" spots** of length ℓ along the motion raise the limit to ℓ·F_holo/k. The cost is IR power ∝ ℓ/r_c for the moving motes only. [DERIVED]

**Hybrid POV channels for a grabbed object** (M13 machinery, best estimate plus certified scheduling, quiet zone):

| Object stroke length | Steered beams | Mote speed |
|---|---|---|
| 0.3 m | ~700 | 0.21 m/s |
| 0.5 m | ~1,160 | 0.21 m/s |
| 1.0 m | ~2,330 | 0.21 m/s |

[MODEL, `07_mote_route/sim_m13_corrected_floor.py` cell() with custom content]

**Consequences.**
- Iron-Man "flick" gestures (1–2 m/s) are **not reachable by any photophoretic-mote display**.
- Hand-speed manipulation (0.3–0.5 m/s) is reachable only for small objects, at hundreds to thousands of steered beams.
- The practical design treats a fast move as **"dissolve and re-form"**: the object fades or thins during the move, and the motes re-settle within ~1–2 s. This is a UX workaround, not physics, and it counts against R6/R9.

## 3c. Fast POV with the curtain (LCSV-P, M16, `m16_fast_pov.py`, `results/m16_fast_pov.json`)

In v4 the mote speed (0.2–0.5 m/s) was capped by the **light budget**, not by force:
- the 405 nm pump's 39 µW Class 1 limit;
- each POV mote's lumens grow with v, because fewer motes draw the same strokes.

With I1 (curtain) and I3 (terminated visible scattering, a tracked spot per mote), **heat** sets the speed instead. Assumptions:
- H10 room layout, ITO-skin mote (FOM 5.3, needed because carbon is a volume absorber and fails at 1 µm);
- tracking loop 5 kHz with feedforward along the planned stroke, 2 % residual;
- T_max 573 K.

| Content, room | Mote a, speed v | Motes | Steered beams (3 push + 1 light) | IR / visible | Hand-occluded |
|---|---|---|---|---|---|
| Sketch, quiet / calm | 1–1.5 µm, **1.0 m/s** | 526 | **2,105** (v4: 12,200) | 4–8 W / 0.2–0.7 W | overheats near the hand |
| Sketch, quiet / calm / **normal** | 1–2.5 µm, **0.5 m/s** | 1,053 | 4,211 | 3–38 W / 0.05–2.4 W | ✓ at 1–1.5 µm |
| Film density, quiet / calm | 1–1.5 µm, 1.0 m/s | 2,169 | **8,675** (v4: ~50,000) | 15–34 W / 0.9–4 W | overheats near the hand |
| Film density, **normal** | 1.5–2.5 µm, 0.5 m/s | 4,337 | 17,349 | 133–144 W / 2–6 W | ✓ at 1.5 µm |

**Reading.**
- The curtain plus terminated scattering cut v4's beam count **~6×** at the same content.
- They make **normal (0.3 m/s) rooms** feasible at 0.5 m/s mote speed.
- They raise content speed to ~0.5–1 m/s, versus 1–8 cm/s for the holographic static voxels.
- Heat, not light, now caps v at ~1.2 m/s for 1 µm ITO motes.

**Combined architecture.**
- Holographic static voxels (LCSV-H) carry the static and slow bulk (UI panels, models at rest, video panels).
- Fast POV channels (LCSV-P) carry moving and grabbed content and accents.
- Both share the same heads, curtain receivers, lasers and motes.

## 4. What would make the theory "complete"

All of the following must hold:
- A mote whose FOM is computed from **measured** properties at its size;
- a safety case accepted under existing standards;
- hardware whose pixel count, speed and power exist **today**;
- every requirement R1–R10 MET in a model that two independent checks reproduce.

At the time of writing, none of the four is complete. This note is the map of where the needle must be.

# Idea round 3: independent report (Sonnet), resumed after Opus and T8

*Written 2026-10-01. I read `IDEA_ROUND_3_BRIEF.md`, T6 §1–3, T7, `red_team_6_lcsv.md`, idea rounds 1 and 2, `07_mote_route/R3/R7` (standards rows), `idea_round_3_opus.md` and `T8_pov_crossing.md`. I edited no repository file except this one.*

*Scope after the coordinator's message: the Opus report already settles force per watt (all dead), the B9 ledger, the crossing-rate rule, the laminar co-flow column and the electrostatic common mode. I do not repeat those. I concentrate on (a) verifying the eye/skin rules, (b) still-air engineering for a home, and (c) anything that beats T8's constraints.*

**Tags.** [VERIFIED] = seen in a source this session. [DERIVED] = derived here from stated physics. [SIM] = my scratch simulation (imports the repo's code read-only). [ESTIMATE] = order-of-magnitude. [SPECULATIVE] = untested. [NOT VERIFIED] = I could not reach the source.

**Web budget.** 10 of 10 searches used (ICNIRP table and footnote, IEC pulsed/scanned rules, plume velocities, cleanroom flow, water absorption, porous photophoresis, DCCL intrinsic safety, ICNIRP 2020 comments, EN 50689). Three direct fetches (icnirp.org, the sfrp.asso.fr mirror, arxiv.org) were blocked by the egress proxy, so **no standard text was read in full**: everything below is from search snippets, R3/R7, or derivation, and is marked accordingly.

**Scratch scripts** (session scratchpad, not committed): `a1–a4.py` (B9 and passive pairs, `physics.py`/`m18` read-only), `b1–b3.py` (moving-content exposure simulation, reuses `m17` geometry), `s1–s2.py` (head-assignment optimiser), `c1.py` (force catalogue), `d1.py`, `f1.py` (air budget), `e1–e3.py` (AEL windows, strict readings, corneal heating).

---

## 0. Verdict in one screen

1. **B9 is beaten ≥ 10× only for *moving* content, and I confirm Opus idea 2 / T8 independently** [SIM]: a rigid wireframe sketch (1 650 motes, w = 50 µm, still-room draft) rotating at 0.25–2 m/s edge speed gives a worst-cell time-averaged pupil power of 0.46–2.8 mW against 9.6 mW (film density: 3.7–13 mW), although per-focus power reaches 36–69 mW. **But it fails for content whose strokes move along themselves** (rotating latitude rings: 108–246 mW average, 11–25× over), and cells near the axis keep their static value. The rule needs a space-time dose-map governor, not just a crossing-rate formula (§1.4).
2. **New and verified: for a child-appealing consumer product the skin criterion binds, not the eye** (EN 50689: skin MPE of EN 60825-1 Table A.5, accessible emission measured through a **1 mm aperture, 10 s time base** [VERIFIED, snippets]). At 1500–1800 nm that is **0.785 mW per focus**, 12× tighter than the eye's 9.6 mW. Consequences [DERIVED]:
   - static voxels at w = 50 µm fail by **4×** (B9 becomes **1.2 cm/s** instead of 4.7 cm/s);
   - POV (T8) is capped at **w ≤ 31 µm at 30 Hz regardless of stacking**, so the scheduling gain Opus counts for T8 (w up ×1.4) is **not available** under this rule;
   - T8's sketch point (w 31–35 µm) sits at the limit (margin 0.8–1.0), 60 Hz fails.
3. **Standards risk that decides between T7 and T8** (ICNIRP's non-averaged small-beam rule, §1.2): static foci fail it by 26× at 0.35 s, moving foci pass with 1.4–1.8× margin at 30 Hz. T8 is robust to every reading I could construct; T7 is not.
4. **(b) Still air:** the realistic target is **σ_u ≈ 1 cm/s, not 3 cm/s**, and what it buys is narrow: it rescues static voxels under the skin rule at w = 35 µm. The cheapest measures (pause HVAC, siting, no uncooled heat source below the image, heads above or liquid-cooled) are free to $2k and plausibly give 1–2 cm/s [ESTIMATE; calibration assumed]. A physical floor of **0.4–1.0 cm/s** comes from the motes' own heat. Active cancellation and laminar shields fail on numbers (§2).
5. **(c) One new idea beats T8's eye/skin budget: passive-pair POV channels at w ≈ 3 µm** (E/L ÷ 8.4; eye margin 8.5×, skin 6.6×; removes the ~20 kHz per-channel loop), at the price of heads with R/d ≥ 0.2 (§3, idea 2). Probability ≈ 0.15. One free hedge: lateral dither of POV tracks (×2–5 against the strict reading).
6. **No free ≥ 10×.** Every route is paid for in head aperture, channels, scheduling, or air handling. I found no wavelength, pulse regime, force mechanism or draft trick that changes that.

---

## 1. (a) Eye and skin rules: what I verified, and what it implies

### 1.1 Verification ledger

| Item | Value | Status | Where |
|---|---|---|---|
| Cornea MPE 1500–1800 nm | 1 J/cm² (10⁴ J/m²), no duration dependence up to 10 s | **VERIFIED** (search: "static 1 J/cm²", unlike the 1800–2600 band) | ICNIRP 2013 Table; ANSI 2022 per R3 |
| Limiting aperture, > 1400 nm | 1 mm for t ≤ 0.35 s; 3.5 mm for t ≥ 10 s; t^0.375 between | **VERIFIED** (search); coefficient 1.5 mm from R3 | ICNIRP/IEC |
| Long-term cornea limit | 1000 W/m² = 0.1 W/cm² (t > 10 s) | consistent with R3 (A); DCCL paper uses the same 0.1 W/cm² corneal criterion [VERIFIED indirectly] | R3 L7 |
| Class 1 AEL at 1550 nm | 7.85 mJ (1 mm, t ≤ 0.35 s); 96 mJ in 10 s; **9.6 mW ≥ 10 s** | computed from the above; "typical ~10 mW eye-safe threshold" [VERIFIED snippet] | IEC Table 3 via R3 K1 |
| Small-beam note | "For beam diameters < 1 mm and pulse durations < 0.35 s, compare the actual (non-averaged) radiant exposure with the limit", attached to the **cornea limits above 1400 nm** | **VERIFIED** (two searches, incl. ICNIRP 2020 comments) | ICNIRP 2013 footnote |
| Same note for skin (Table 7 note b) | R7 S3 says no time restriction | **NOT VERIFIED** (icnirp.org blocked) | R7 |
| ANSI Z136.1 small-beam rule | none (R7); 1400–1500 nm revised in 2022 | **NOT VERIFIED** this session; from R3 | R3 L11, R7 S3 |
| Scanned beams, 1400–4000 nm | AEL energy measured through a 1 mm aperture at 100 mm (Condition 3 for scanned beams) | **VERIFIED** as a snippet of an older edition (1.2); Ed. 3 text not read | IEC 60825-1 |
| Pulse-train rules | most restrictive of rules (i) single pulse, (ii) average over T, (iii) multiple-pulse correction "as appropriate"; (iii) is a 400–1400 nm retinal rule, so rules 1+2 only above 1400 nm | snippet + R3 P2/P3 (B) | IEC §4.3 |
| **EN 50689 child-appealing** | Class 1 **and** skin MPE (EN 60825-1:2014 Table A.5); skin-accessible emission measured with a **1 mm aperture, 10 s time base** (> 400 nm) | **VERIFIED** (UL, BACL, JJR snippets); full text not read | EN 50689:2021 |
| Water absorption (Hale–Querry) | 1480 nm 21.2, 1500 17.6, 1540 11.8, 1560 9.67, 1600 6.72, 1640 4.98 cm⁻¹ | **VERIFIED** | omlc data via search |
| Plume speeds of a person | 0.19–0.35 m/s above the head (manikin, seated or standing) | **VERIFIED** | indoor-air literature (search) |
| Cleanroom laminar flow | 0.25–0.75 m/s typical, 0.45 m/s common | **VERIFIED** | cleanroom practice (search) |

**Closed item for T8:** rule 3 (C5) is a retinal 400–1400 nm rule that applies only for sources above 5 mrad. A 15–50 µm visible focus seen from ≥ 0.1 m subtends ≲ 0.5 mrad, so C5 = 1 and only rules 1 and 2 bind (R3 P2, B-confidence).

### 1.2 Three readings of "dose through a small focus", applied to the designs

Definitions (E/L = h·I_unit·πw²/2, h = 2.14, I_unit = 7.30×10⁶ W/m² per m/s; per pass the focus carries H_pass = √(2/π)·(E/L)/w at its track centre):
- **IEC eye:** mean power through 3.5 mm ≤ 9.62 mW.
- **EN 50689 skin (child-appealing):** mean power through **1 mm** over 10 s ≤ 1000 W/m² × 7.85×10⁻⁷ m² = **0.785 mW**, stacking s″ ≈ 1.1 [DERIVED, the 1 mm tube is 23× smaller in volume].
- **ICNIRP strict (cornea, < 1 mm beam, t < 0.35 s):** non-averaged H ≤ 10⁴ J/m² summed over the passes a corneal point receives in 0.35 s (f_r·0.35 = 10.5 passes at 30 Hz, all on the same track).

| Design | IEC eye: P (mW), margin | EN 50689 skin: P (mW), margin | ICNIRP strict: H (J/m²), margin |
|---|---|---|---|
| T8 sketch, w 35 µm, 30 Hz, s′ 3.0 | 9.46, **1.02** | 0.99, **0.79** | 7 190, 1.39 |
| T8 sketch, w 31 µm | 7.42, 1.30 | 0.78, **1.01** | 6 370, 1.57 |
| T8 sketch with scheduling s′ 1.5, w 35 | 4.76, 2.02 | 0.99, **0.79** | 7 190, 1.39 |
| T8 film, w 27 µm, s′ 4.6 | 8.64, 1.11 | 0.59, 1.33 | 5 550, 1.80 |
| T8 sketch at 60 Hz, w 27 µm | 11.3, **0.85** | 1.18, **0.67** | 11 100, **0.90** |
| Static voxel, still room (v̄ = 4.8 cm/s), w 50 µm | 9.7, 0.99 | 3.24, **0.24** | static at 0.35 s: **0.038** |
| Static voxel, w 35 µm | 4.76, 2.0 | 1.59, **0.50** | 0.038 |
| Passive pair POV, w 3 µm (idea 2) | 1.13, **8.5** | 0.118, **6.6** | 9 997, **1.0** |

Largest POV waist at 30 Hz [DERIVED]: eye 35 / 50 / 28 µm for s′ 3.0 / 1.5 / 4.6; **skin 31 µm for any s′**; strict-local 49 µm.

Readings:
- **The skin criterion is the binding one once stacking is scheduled away.** It does not stack (1 mm), so only w, h·I_unit and f_r move it.
- **The strict reading is a different physics:** H_pass ∝ I_hold·w/η is independent of speed and of stacking, and only w, FOM and f_r help. A pair (idea 2) does not help here: its intensity rises as its spot shrinks.
- **Static foci fail the strict reading by 26× at any power above ~0.1 mW** (w = 50 µm: P ≤ 0.11 mW for 0.35 s). That reading is probably not meant for CW foci (ICNIRP footnote scope; R7 conf. C), but a test house could apply it, and T7's whole design rests on the opposite assumption.
- **Stall fault timing depends on the reading:** a stuck 28 mW focus (1 m/s, w = 35 µm) reaches the IEC rule-1 dose (7.85 mJ, 1 mm) in **0.28 s**, the EN skin dose in 0.28 s, and the strict dose in **0.7 ms**. The strict case needs a hardware cut per head in tens of µs (an AOM per head), not the ≤ 100 ms watchdog T8 assumes.

### 1.3 A fingertip at a focus, and the physical margin of the limits [DERIVED/ESTIMATE]

Steady centre temperature rise of water-like tissue under a Gaussian focus (Hankel solution, adiabatic surface = upper bound, k = 0.58 W/m/K, α from Hale–Querry), per 10 mW:

| Wavelength (α, m⁻¹) | w = 3 µm | 15 µm | 35 µm | 50 µm | collimated 3.5 mm |
|---|---|---|---|---|---|
| 1480 nm (2 120) | 34 K | 25 | 20 | 18 | 3.2 |
| **1550 nm (1 070)** | **19** | 14 | 12 | 11 | **2.6** |
| 1600 nm (672) | 13 | 9.9 | 8.3 | 7.7 | 2.2 |
| **1640 nm (498)** | **9.9** | 7.7 | 6.6 | 6.1 | 1.9 |
| 1900 nm (~1.2×10⁴, recalled) | 135 | 85 | 60 | 51 | 4.2 |
| 3 µm, 10.6 µm (recalled) | 530–1 670 | 240–420 | | 104–134 | 4.5 |

(Halve the first four rows for an isothermal-surface bound.)

- **A 10 mW Class 1 focus heats a cornea-like absorber by 6–19 K, 4–7× the 2.6 K of the collimated reference the 3.5 mm average is built on.** The mean-power quantity is therefore *not* a conservative proxy for a micro-focus; it matches ICNIRP's 2020 remark that the 7 mm/3.5 mm stop makes the limit exceed predicted thresholds for small beams (snippet).
- **At the EN 50689 skin limit (0.785 mW) the rise is ~1 K**, i.e. the child-appealing skin rule is thermally conservative by ~10× while the eye AEL for a micro-focus is not. A fingertip at a 3 mW static focus (T7) warms by ~3.5 K: harmless physically, non-compliant legally.
- **1550 nm is already near the best band; 1600–1700 nm is ~1.7× gentler at equal power** (deeper heat), mid-IR and 1.9 µm are 5–100× worse. That is a physical margin, not a legal one: the standard's limit is 1000 W/m² at all of them.
- No pulsed regime helps: the force is linear in mean absorbed power (opus §4), rule 2 caps the mean, and two-photon absorption fails by 10³–10⁵ (§3 killed list).

### 1.4 Moving foci: rules plus my simulation

**Rules.** Each pass is a pulse (rule 1 ≤ 7.85 mJ through 1 mm; rule 2 averages over T, no C5 above 1400 nm); passes carry 0.05–0.24 mJ at w 35–50 µm, so rule 1 holds with ≥ 30× margin; classification must survive a scan/stall fault. I could verify the older-edition scanned-beam wording and the rule structure, not the Ed. 3 text.

**Simulation** [SIM, `b1–b3.py`; m17 geometry, 14 heads, 3 random heads per mote, w = 50 µm, h = 2.14, draft v̄ = 0.048 m/s; per-beam power ∝ the mote's air-relative speed]:

| Content | Edge speed (m/s) | Per-focus mean / max (mW) | Worst random-cell time average (mW) | AEL |
|---|---|---|---|---|
| Sketch (1 650 motes), static | 0 | 2.9 | 9.7 at a mote (stacking 3.32) | 9.62 |
| Sketch, rigid rotation | 0.25 / 0.5 / 1 / 2 | 11 / 20 / 36 / 69 (max 18 / 32 / 62 / 120) | **0.46 / 0.80 / 1.48 / 2.84** | 9.62 |
| Film (9 900 motes), static | 0 | 2.9 | 14 (stacking 4.91) | |
| Film, rotation | 0.5 / 1 / 2 | 19 / 35 / 67 | **3.7 / 6.8 / 13.0** | |
| Globe (8 151 motes), all motes rotate (equator 1 m/s) | 1 | 46 (max 64) | **on latitudes 246 max (108 median); meridians 113 (12)** | |
| Globe, latitude motes held, meridian motes move | 1 | 27 | latitudes 19.6 (13.2), meridians 33.6 (9.0); static globe is 25 | |

- **A random sketch passes up to ≥ 2 m/s, film up to ~1.4 m/s**, so on the eye criterion at w = 50 µm B9 is not the binding wall for transversal content; heat (B3: v_rel ≤ 1.44 m/s push, 0.69 m/s with a head blocked, a = 1 µm, hot face ≤ 573 K [DERIVED, `m18.hold`]) is. This is the same conclusion as Opus idea 2 and T8, reached by a different route.
- **What the formula misses:** strokes that move *along* themselves (rings, helices) are crossed continuously, so duty ≈ 1 at power ∝ v (globe latitudes: 11–25× over). Rotating a rotationally symmetric ring changes nothing visually, so the content planner must assign motes **Eulerian-wise** (hold the ring's motes, move only motes that change the image). Even then converging meridians at the poles (and any dense dwelling region) stay at the static level: the globe's static value (25 mW) already exceeds the AEL at w = 50 µm.
- **Cells near the rotation axis keep the static value** (their motes barely move, so P = P_unit·v_draft with duty 1). The design point is therefore still set by T7's static still-room arithmetic for the slow part of any scene; motion only exempts the fast part. A governor must keep a running dose map per 3.5 mm cell (and per 1 mm cell for the skin rule) over 1, 3, 10 s windows.

### 1.5 Bursts: windowed AEL [DERIVED]

AEL(t)/t at 1500–1800 nm: 22.4 mW (0.35 s, 1 mm), 17.7 mW (1 s, 1.5 mm), 13.4 mW (3 s, 2.3 mm), **9.62 mW (≥ 10 s, 3.5 mm)**. Because the smaller aperture also stacks fewer beams (s ≈ 1.1–1.5 instead of 3.3), a hold or re-capture burst may carry **~10–20 mW per focus for ≤ 0.35–1 s**, i.e. ×4–7 over the long-term 2.9 mW, once per ≥ 10 s window (EN skin: 7.85 mJ per 10 s, so one 20 mW × 0.35 s burst per window). Useful for hand wakes and re-acquisition; void under the strict reading (0.1 mW at 0.35 s).

### 1.6 What does not help (eye/skin basis)

- **Extended-source relief (C6):** exists only for 400–1400 nm retinal limits; a focus is a point source, C6 = 1; above 1400 nm there is no retinal image at all.
- **Condition 3 at 100 mm:** rejected by Opus and by EN 50689's "any position".
- **Intrinsic self-closing beams (Wi-Charge-like):** the DCCL paper delivers 150 mW "eye-safe" from a 650 mW 1064 nm beam [VERIFIED], but through a divergent beam and a retroreflecting receiver, with the eye-hazard case being partial obstruction. For foci this would need one gain element and one cat's-eye retro per beam (~10⁴), and the 5 % partial-intercept threshold limits each beam to ~200 mW. [SPECULATIVE, P ≈ 0.05.]
- **A mote as the cavity retroreflector** (laser lases only when a mote is present): a cornea returns 2–2.5 % Fresnel reflection, against ~10⁻⁵ from a 1 µm mote, so an eye would be a better mirror than the mote. Killed.

---

## 2. (b) Still-air engineering for a home

**Calibration warning.** I found no measured σ_u for rooms with HVAC off. The relation σ_core = C·√(gβΔT_w·H) below uses C ≈ 0.10, chosen so that ΔT_w = 1 K, H = 2.5 m gives T7's 3 cm/s; it is a scaling hypothesis, not a measurement. Measure first (§5, Test C).

### 2.1 Source terms at the image (1–2 m from the source unless stated)

| Source | Formula | Number | Type |
|---|---|---|---|
| **HVAC register running** | free jet u = K·u₀√A₀/x, K ≈ 5.5, u₀ 2.5 m/s, 0.15×0.3 m grille; room recirculation after attachment | free jet 0.97 m/s at 3 m, 0.58 m/s at 5 m; occupied-zone recirculation 0.05–0.15 m/s with turbulence intensity 30–50 % (RT6 survey values) | steady + turbulent |
| Wall and window natural convection | σ ≈ C√(gβΔT_w H) (assumed C) | 3 cm/s at ΔT_w = 1 K; 2 cm/s at 0.44 K; **1 cm/s at 0.11 K**; 0.5 cm/s at 0.03 K. A double-glazed window runs 1.9 K inside (U 1.0, 15 K outside), triple 1.1 K | slow, steady |
| Seated viewer, plume | point plume B = gQ_c/(ρc_pT), Q_c = 50 W → entrainment inflow (dQ_v/dz)/(2πr), Q_v = 0.115B^⅓z^(5/3) | plume above head 0.19–0.35 m/s [VERIFIED]; **inflow at the image: 3.4 mm/s at 1 m, 1.7 mm/s at 2 m per person** | steady |
| Viewer exhaling toward the image | steady jet u = 6.3u₀d/x (upper bound; puffs and buoyant bend reduce it), u₀ 1.5 m/s, d 2 cm | ≤ 0.19 / 0.13 / 0.09 m/s at 1 / 1.5 / 2 m | puffs |
| Walker | potential flow of a 0.2 m body at 1 m/s: U R³/(2r³); axisymmetric wake 1.1U(x/D)^(-2/3) | 3.2 cm/s at 0.5 m, 0.4 cm/s at 1 m laterally (1 s); wake 0.38 m/s at 2 m *behind* | transient |
| Door opening | gravity current 0.5√(g′H), ΔT 2 K | 0.18 m/s for 10–60 s | transient |
| **Heat source below or beside the image** (laser head, power supply, lamp) | ideal plume w = 4.7B^⅓z^(-⅓) | **0.14 m/s per W at z = 1 m**; 20 W: 0.49 m/s at 0.5 m; plume radius ≈ 0.12z. For ≤ 1 cm/s the *convective* heat must be ≤ **0.17 mW (z 0.5 m), 0.35 mW (1 m), 0.7 mW (2 m)** | steady column |
| **The motes' own heat** | area source, w = (B_A·z)^⅓ | T7 static sketch 3.9 mW total: 0.38 cm/s; T8 sketch (526 motes at 0.5 m/s): 12 mW: 0.70 cm/s; T8 film: 82 mW: 1.0 cm/s | steady, upward |
| Hand | plume 0.1–0.25 m/s (round-2 Opus), wake 5–10 hand widths | local, 10–40 cm/s | local |

**Heads and electronics** dissipate far more than the allowed milliwatts: the IR sources alone are 16–68 W at 25 % wall-plug, and 3 000–13 000 steered channels at an assumed 0.05–0.2 W each add 150–2 600 W [ESTIMATE]. Any of that left in the room below the image makes a 0.2–0.5 m/s column.

### 2.2 What σ_u this gives (quadrature sum of the steady terms, transients excluded) [ESTIMATE]

| Case | Mean U / σ_u at the image |
|---|---|
| Typical evening, HVAC cycling, 3 viewers, uncooled equipment | 5–10 cm/s / 3–5 cm/s (T7's "home"/"quiet office") |
| + HVAC paused, image ≥ 1.5–2 m from registers, windows, radiators, doors; viewers ≥ 1.5 m; nothing hot in the column below the image | ≈ 0–1 cm/s / **1.5–2.5 cm/s** |
| + heads above or liquid-cooled to a remote radiator; cellular shades on glazing (ΔT_w 1.9 → 0.9 K, σ × 0.7) | 0–1 / **1–1.5 cm/s** |
| + isothermal envelope (±0.1 K walls, radiant panels, no glazing) | 0–0.5 / **0.5–1 cm/s** [SPECULATIVE] |
| Floor set by the motes' own heat | 0.4–1.0 cm/s upward |

### 2.3 Mitigations ranked by cost, with noise and comfort

| # | Measure | Effect | Cost | Noise | Comfort |
|---|---|---|---|---|---|
| 1 | Pause HVAC (setback or zone damper, 20–30 min before the show) | removes the 5–15 cm/s register-driven mean and most turbulence | $0 | **−10 to −20 dBA** (35–45 → ≤ 25) | drift ≤ 1.5 K/h upper bound for 100 W in a 50 m³ room with 3× furnishing mass; real 0.2–1 K/h; ISO 7730 draught rating 0 % |
| 2 | Siting: image and viewers placed per §2.1 | removes plumes and most breath | $0 | 0 | 0 |
| 3 | Heads above the image; electronics ducted or liquid-cooled to a closet or outside | removes 0.15–0.5 m/s columns | $0.5–2k, pump 20–30 dBA | | |
| 4 | Cellular or insulating shades | σ_core × 0.7 | $200–800 | 0 | slightly warmer surface temperature |
| 5 | Isothermal envelope | to 0.5–1 cm/s | $10–30k+ | 0 | radiant ceiling/floor comfort is fine |
| 6 | Opus's push–pull laminar column | ×10–100 on the draft term | outlet, inlet, 4 W fan (0.027 m³/s at 45 Pa, η 0.3) | 30–40 dBA unsilenced | air at 0.3 m/s on hands; ISO 7730 DR 8–17 % for v 0.1–0.3 m/s at Tu 10–40 % |
| 7 | Active micro-jet cancellation wall | ≤ 2–3× at best; interior plumes are not controllable from the boundary | 1 600 / 6 400 / 17 800 actuators for 10 / 5 / 3 cm eddies | fans: **52 / 58 / 62 dBA** (incoherent sum); a valved plenum avoids it but not the cost | |
| 8 | Laminar shield at U < 0.25 m/s | no: cleanrooms run 0.25–0.75 m/s [VERIFIED]; at 0.05 m/s the supply must be uniform to ±75 mK, at 0.01 m/s to ±3 mK | | | the shield *adds* its own mean flow, so v_rel does not fall |

Comfort limits (0.2 m/s) are ~20× looser than the display's need (1 cm/s), so comfort engineering gives nothing; the display wants a thermal-engineering standard.

### 2.4 What σ_u target the standards actually set

Static-voxel B9 under each criterion, mean v_rel = 1.6σ_u [DERIVED]:

| w | Eye (s 3.3): v_max, σ_max | EN 50689 skin (s″ 1.1): v_max, σ_max |
|---|---|---|
| 50 µm | 4.7 cm/s, 2.9 cm/s | **1.2 cm/s, 0.73 cm/s** |
| 35 µm | 9.7 cm/s, 6.1 cm/s | **2.4 cm/s, 1.5 cm/s** |
| 25 µm | 19 cm/s, 12 cm/s | 4.7 cm/s, 2.9 cm/s |

So for a child-appealing product static voxels need **σ_u ≈ 1 cm/s with w ≤ 35 µm** (P_focus 0.48 mW, skin margin 1.5×, eye 6×), which is the engineered-room end of §2.2 plus T7's 10 kHz loop. A POV mote is cheaper to air-condition: the draft enters only as (1 + u/v). POV beats static when mean |u| exceeds f_r·d·s′/s = **3 cm/s under the skin rule** (d = 1 mm) or ~10 cm/s under the eye rule (d = 3.5 mm) [DERIVED]. A hybrid that picks static or POV per stroke from a measured local u is therefore sound (small gain, scheduling only).

---

## 3. Ranked ideas new in this report

| # | Idea | Gain | Status | Cost / risk | P |
|---|---|---|---|---|---|
| 1 | **Verified constraint: EN 50689 skin limit (0.785 mW, 1 mm, 10 s)** binds POV at w ≤ 31 µm and static voxels at 1.2 cm/s (w 50 µm) | not a gain: removes ×1.4 from T8's scheduling lever and ×4 from T7's B9 | VERIFIED (snippets) + DERIVED | applies if the product is child-appealing; a hologram of Iron Man almost certainly is | — |
| 2 | **Passive-pair POV channels, w ≈ 3 µm, a = 1 µm** | E/L 3.58 vs 30 mJ/m (÷ 8.4): eye margin 8.5×, skin 6.6×; allows 60 Hz and film density; **no per-mote 20 kHz sensing loop** (feed-forward steering plus ≤ 100 Hz registration) | DERIVED (`lg01_trap`, M13 pair factor 1.35/η); geometric optics at w ≈ 2λ, ±2× | heads with **R/d ≥ 0.2** (R 0.3 m at 1.5 m, 0.45 m at 2.3 m; T8 has 0.11 m at up to 4 m); pair heat factor 3.65 caps v at 0.84 m/s (a = 1 µm); registration of the two axes to ≲ 1 µm against 0.4–1.2 µm beam wander; axial hold in drafts along the pair axis unverified | 0.15 |
| 3 | **Lateral dither of POV tracks (±3w, random per refresh)** | strict-local H: ÷ 5 expected, ÷ 2.3 worst case | DERIVED | free: a random lateral offset of the plan (the loop follows 100 µm in 33 ms = 3 mm/s); no effect on IEC/EN averages; the 6–20 µm drawing scatter T8 already has gives part of it | 0.7 as a hedge |
| 4 | **Stacking-aware head assignment, measured** | static s_worst **3.36 → 1.60 (sketch), 5.43 → 2.75 (film)** with greedy moves and no push-feasibility constraint (upper bound) | SIM, `s2.py` | confirms Opus idea 1(a) (1.2–1.5 / 2–3); under the skin rule it buys nothing for POV, and for static voxels s″ ≈ 1.1 already | 0.6 |
| 5 | **σ_u ≈ 1 cm/s room plus w 35 µm** to recover static voxels under the skin rule | static B9 1.2 → 2.4 cm/s at w 35 µm, σ budget 1.5 cm/s | DERIVED + §2 | engineered room; motes' own heat floor 0.4–1 cm/s | 0.3 |
| 6 | **Dose-map governor with Eulerian mote assignment** (hold symmetric strokes, move only image-changing motes) | keeps moving content at 0.5–2 m/s Class-1 where the crossing formula would fail (globe rings 11–25× over) | SIM | space-time dose accounting per 3.5 mm and 1 mm cell; certified; adds to the existing field checker | 0.5 |
| 7 | **Burst allowance** from AEL(t)/t | ×4–7 per focus for ≤ 0.35–1 s, once per window | DERIVED | void under the strict reading | 0.4 |
| 8 | **Heat-source and HVAC rules** (§2.1–2.3) | removes 0.1–0.5 m/s columns and 5–15 cm/s register flows | DERIVED | free to $2k | 0.8 |
| 9 | Lever stack for static voxels at equal modes: w 50 → 35 (×2.0), h·s 7.1 → 3 (×2.4), FOM 5.3 → 8 (×1.5), w → 25 (×2.0) | ×2.0 / 4.8 / 7.3 / **14.2** on total mean v_rel | DERIVED (T7 formula) | each factor is optimistic; the skin rule removes ~4× | 0.25 |

**Killed in this report, with the number that kills them**

| Idea | Number |
|---|---|
| Two-photon (superlinear) pulsed absorption | A₂ = β·I_pk·L ≈ 8×10⁻¹²·5×10¹¹·2×10⁻⁶ = 8×10⁻⁶ (Si) or 10⁻³ (best organic β = 10⁻⁹ m/W): 10³–10⁵ short of unity at 10 mW mean |
| Free-molecular nano-mote (a ≤ 100 nm) for the 100× radiometric ceiling F/P = 1/(αc̄) = 2.2×10⁻³ N/W | Biot h·a/k_p = 0.05–0.6 for aerogel k_p 0.02–0.05, so the faces stay near-isothermal; realistic F/P ≈ 10⁻⁴; σ_abs ≤ πa²: I_unit ≈ 5×10⁶ (no gain over 7.6×10⁶) and visible scatter ≥ 100× lower |
| Resonant sub-wavelength absorber (σ_abs,max = 3λ²/8π = 2.9×10⁻¹³ m², Q_abs 1.5–3 at a 0.25–0.3 µm) | I_unit(A = 1) is 1.14×10⁷ at 0.3 µm; with Q = 3 → 3.8×10⁶, ×2 over the 1 µm mote, but visible cross-section ÷ 10 and slip 0.4 |
| Evaporative or ablative propellant | 1 µm mote (6×10⁻¹⁶ kg): lifetime 10 ms (500 m/s vapour) or 59 ms (3 km/s) at the drag of 0.1 m/s |
| Electrostatic hold | Peek-limited charge 1.3×10⁻¹⁵ C (1 µm): 2.5×10⁴ V/m for 0.1 m/s |
| ΔT-photophoresis gain from thermal stress slip or porous transpiration | the literature says thermal-stress slip "always increases" the photophoretic mobility [VERIFIED snippet]; no magnitude found; Opus bounds transpiration at ≤ 1 % of drag; treat as ×1–2 [SPECULATIVE] |
| Mote as regenerative cavity element, extended-source relief, wavelength change, pulsing | §1.6, §1.3 |

---

## 4. Answer to (c): does anything beat T8's constraints?

T8's binding constraints are the crossing-rate budget (w ≤ 31–35 µm at 30 Hz), the ~20 kHz per-channel loop, and standards acceptance.

- **Eye and skin budget:** only idea 2 (passive pairs) moves it materially (×6–8). The scheduler lever is capped by the skin rule at w = 31 µm; FOM (×1.5) and a path-aligned push (h_mean 1.35 instead of 2.14, ×1.6, if heads sit near stroke tangents) are small.
- **Refresh rate:** E ∝ f_r. A dim lab (3–4 cd/m²) may tolerate 25 Hz (×1.2); this needs a flicker measurement, not a calculation.
- **Strict reading:** tracks dither (idea 3) and a per-head hardware cut (0.7 ms) are the only hedges.
- **Draft:** T8 pays (1 + u/v) in eye budget and heat at gust peaks (hot face 433–521 K at σ_u = 0.1). No draft measure is needed for eye safety; the useful ones are the heat-source rules (they remove 0.1–0.5 m/s columns that exceed T8's authority margin locally) and the hand-wake dropout zone.

**Overall verdict on B9.** It is beaten ≥ 10× for moving content (confirmed, with the Eulerian and dose-map caveats) and by 5–14× for static content only by stacking levers each of which is unproven; the skin rule for child-appealing products removes ~4× from the static route and ~1.4× from T8's scheduling gain. **The heat wall B3 (0.7–1.4 m/s at a = 1 µm, ×2 at 0.5 µm, ×1.5 at best FOM) then binds**, so the achievable total over B9's 5 cm/s is about ×15–30 for POV and ×5–15 for static voxels, not more.

---

## 5. Lab tests (weeks-scale) for the top three

**Test A: settle the standards readings with data and a test house** (3–4 weeks)
1. 1550 nm fibre amplifier (50–500 mW), galvo or rotating mirror, focus w = 35–50 µm. InGaAs photodiode behind 1 mm and 3.5 mm apertures; record per-pass energy, the 10 s mean against crossing rate, and the stall-to-cut time. **Pass:** mean = f_r·(E/L)·d within 30 %; per-pass energy ≪ 7.85 mJ.
2. Hydrogel or ex-vivo-like phantom with a fine thermocouple or IR camera: ΔT under static and moving foci at 1, 3, 10 mW (w 35 µm). **Pass:** static within ×2 of the model (6–12 K per 10 mW); moving ≤ 10 % of static.
3. Written pre-compliance opinion from a notified body on: crossing-rate classification, the EN 50689 1 mm skin criterion for a hologram product, the ICNIRP small-beam note, and the stall cut time. **This is the cheapest way to resolve the three open readings.**

**Test B: passive-pair efficiency at NA ≥ 0.2** (4–6 weeks; extends BENCH_PLAN U3)
1. Two opposed LG01 beams (1550 nm, 100 mW; spiral plates or SLM) through NA 0.2 aspheres at 0.25 m: w ≈ 3–4 µm. A 1–3 µm absorbing particle (carbon-coated hollow glass or graphite flake) in still air; a calibrated nozzle gives 2–20 cm/s cross-flow.
2. Measure escape speed against pair power and a/w; compare with the table (P_pair 3.6 mW per m/s at a = 1 µm, w = 3 µm; 7.5 mW at w = 4; 14 mW at w = 5). Calibrate F/P_abs with a single beam first so the particle's FOM drops out.
3. Misregister the two axes by 0.5–2 µm. **Pass:** η within ×2 of the model; escape ≥ 0.2 m/s at ≤ 20 mW; loss of capacity ≤ 30 % at 1 µm misregistration.

**Test C: particle-tracking anemometry for σ_u** (2 weeks, ~$3–5k)
1. 532 nm sheet (0.5–1 W), 200 fps camera, 2 µm DEHS seeding (wait 5–10 min for the generator jet to die), 0.5 × 0.5 m field: velocity noise ≈ 0.4 mm/s (4 µm / 10 ms), far below hot-sphere anemometer accuracy (±2 cm/s).
2. Four conditions in an ordinary room: HVAC on with 3 people; HVAC paused; + shades; + a 20 W source 0.5 m below the field, bare and ducted. **Pass:** the plume prediction (0.49 m/s) within ±30 %, and σ_u (paused, sited, no heat below) ≤ 1.5–2.5 cm/s; fit C in σ_core = C√(gβΔT_w H) by varying ΔT_w with a heated panel in a foam test cell (0.05–2 K).

---

## 6. Notes for the main session and red team 7

- **T8 §1/§2 should add the EN 50689 skin row.** At 30 Hz the sketch w ≤ 31 µm for any s′; T8's 31–35 µm is at the limit, film at 27 µm passes, 60 Hz fails (margins in §1.2).
- **T8 §1 estimate of s′** (3.0 sketch, 4.6 film) is consistent with my static optimiser only before scheduling; after scheduling s_static is 1.6/2.75, giving s′ ≈ 1.5/2.5 by T8's formula. Under the skin rule this does not enlarge w.
- **Stall timing:** T8's ≤ 100 ms watchdog is right for IEC rule 1 (0.28 s) and EN skin; it is wrong by 400× if a test house applies the ICNIRP non-averaged cornea footnote (0.7 ms).
- **Content planner:** moving content needs Eulerian assignment and a space-time dose map. A rotating wireframe of symmetric rings violates the budget by 11–25× if its motes are all moved.
- **Rule 3 (C5) for the visible illumination** is not applicable for point-like foci (α ≤ 5 mrad); close that item.
- **Heat:** the motes' own absorbed power (12–82 mW per image) is a 0.4–1 cm/s convective floor, comparable to the draft target; the head and electronics heat is orders larger and must leave the room or sit above the image.
- **Unverified and open:** Ed. 3 scanned-beam text, ICNIRP skin note b, the full text of EN 50689, ANSI Z136.1-2022 small-beam handling. Sources for these were blocked.

## Sources

**Web (this session)**
- ICNIRP 2013 laser guidelines, 1500–1800 nm static 1 J/cm², apertures: [ResearchGate: corneal injury thresholds vs limits](https://www.researchgate.net/publication/336119396_Comparison_of_corneal_injury_thresholds_with_laser_safety_limits); [ICNIRP guidelines (listing)](https://www.icnirp.org/cms/upload/publications/ICNIRPLaser180gdl_2013_2020.pdf).
- Small-beam non-averaged footnote and its cornea scope; 7 mm stop remark: [ICNIRP 2020 comments, Health Physics](https://journals.lww.com/health-physics/Fulltext/2020/05000/Comments_on_the_2013_ICNIRP_Laser_Guidelines.5.aspx).
- IEC 60825-1 pulsed rules, scanned beams 1400–4000 nm at 1 mm / 100 mm (older edition snippet): [IEC 60825-1 Ed. 1.2 copy](https://shop.textalk.se/shop/ws26/40626/files/full_size_-_for_start_page_banner/iec60825-1%7Bed1.2%7Den.pdf); [IEC Ed. 3 preview](https://webstore.iec.ch/en/iec_catalog/product/preview/?id=L3B1Yi9wZGYvcHJldmlldy9pbmZvX2llYzYwODI1LTF7ZWQzLjB9Yi5wZGY%3D).
- EN 50689 child-appealing: Class 1 and skin MPE (Table A.5), 1 mm aperture, 10 s: [UL](https://www.ul.com/insights/understand-new-laser-product-safety-standards-europe); [JJR Lab](https://www.jjrlab.com/news/new-european-standard-for-laser-products-en50689-2021.html); [ILSC 2023 abstract](https://pubs.aip.org/lia/ilsc/proceedings-abstract/ILSC2023/2023/L0602/3298026).
- Water absorption (Hale and Querry): [omlc data](https://omlc.org/spectra/water/data/hale73.dat).
- Human thermal plumes 0.19–0.35 m/s: [thermal plumes of standing and lying humans](https://www.tandfonline.com/doi/full/10.1080/23744731.2021.1963133); [plume and breathing interaction](https://www.sciencedirect.com/science/article/abs/pii/S0378778818331098).
- Cleanroom laminar flow 0.25–0.75 m/s: [Dalkia: airflow in cleanrooms](https://dalkia.co.uk/news-insights/the-importance-of-airflow-in-cleanrooms/).
- DCCL intrinsic eye safety (150 mW delivered from 650 mW, cornea < 0.1 W/cm²): [arXiv 2507.21891](https://arxiv.org/abs/2507.21891).
- Thermal stress slip raises photophoretic mobility: [Surfaces 2026](https://doi.org/10.3390/surfaces9010015).

**Repository (read-only):** `R3_safety_limits.md` (L6–L11, K1, P2, P3), `R7_mote_safety.md` (E3, S2, S3, K5–K7, R4, T4), `T7`, `T8`, `idea_round_3_opus.md`, `m17_exposure_field.py`, `m18_gaussian_lcsv.py`, `mote/physics.py`.

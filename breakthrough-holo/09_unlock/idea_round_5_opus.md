# Idea round 5: a loophole hunt against the full-vision tetralemma (independent report, Opus)

*Written 2026-10-05. I read `IDEA_ROUND_5_BRIEF.md`, `05_reviews/FINAL_VERDICT.md` (v6), `09_unlock/T9_home_routes.md` (with the RT9 box and the main session's new §2.9 O-band addendum, which appeared while I worked), `05_reviews/red_team_9_home.md`, `idea_round_4_opus.md`, and skimmed `idea_round_3_opus.md`, `T6_unlock_theory.md`, `red_team_8_pov_x.md`, `m22_needles.py` (§H), `m23b_rain_law.py`, `m24_oband.py`, `m25_oband_static.py` (header). I edited no repository file except this one.*

*Scratch work (session scratchpad, not committed):*
- *`r5_mie.py` / `r5_mie.json`: Mie phase functions of pure-water drops (size-averaged ±10 %) against a white Lambertian mote, head layouts and room-light haze. It imports `rt6_check.bhmie` read-only (validated in RT6). Validation here: Q_ext = 2.08 at x = 233, as expected for large spheres.*
- *A second script (drop lifetimes, water load, buoyancy, impaction, space charge) was **blocked by the environment's safety gate before it ran**. Every number in §2.1–2.6 and §3 was therefore derived by hand from the formulas shown. They are tagged [DERIVED], and the arithmetic is in the text so a red team can check it.*

*Web searches: 3 of 10 (sources at the end). Facts from memory are marked [memory].*

**Tags:**
- [MEASURED]: a documented fact with a source.
- [DERIVED]: derived here from the stated formula.
- [ESTIMATE]: an order-of-magnitude judgement.
- [SPECULATIVE]: an untested idea.

**Concurrency note.** While I worked, the main session added the **O-band window** (T9 §2.9, m24, m25): moving the holding light to 1290–1342 nm raises the EN 50689 skin cap ×10. I do not re-propose it. §3.2 is an independent check of it.

---

## 0. Verdict in one screen

1. **No pillar falls.** The tetralemma stands. Every loophole I found either relaxes a pillar or moves its cost elsewhere, and I name which.

2. **New idea: EVAP-R, a self-erasing pure-water rain** (pillar 1, with knock-on effects on pillars 2 and 3). FLOW-R's trehalose motes become **distilled-water drops of 30 pL**, which evaporate completely ~0.5–1.2 m below the injector.
   - **What it removes:**
     - the pedestal inlet and the 99.9–99.97 % capture requirement;
     - all particulate (no PM, no residue on surfaces, no allergen);
     - the drying duct.
   - **What it changes.** Water drops are ×14–22 dimmer than white motes at 90°, but a low ring of 4–6 heads at 25–30° elevation restores parity per unit area (Mie, §2.3). The bigger drops (29–36 µm at the image) then cut the beam power per lit drop to **~0.2 mW total, 50 µW per head beam at w 140 µm**: ×2–4 below FLOW-R B′. This **fixes RT9's C2 at desk scale** and lets the spots be wider (better aim, no focus bands).
   - **What it costs:**
     - haze ×1.6–3.4 at equal number density (~4–9 % contrast against a black wall at 10 lux; < 1 % against an ordinary wall);
     - lifetime ∝ 1/(ρ_s(T_wb) − ρ_v), so the vanish height moves ×2.6 between 30 % and 70 % RH;
     - 17 g/h of water (+4 % RH in a 50 m³ room);
     - faint beam-end sparkle on the floor.
   - **Fit.** It is literally a mist, so the "no fog" ruling is still needed. Otherwise it is the nearest thing yet to "a projector head that breathes an invisible mist", with no table, pedestal or residue.

3. **New lever: flow normal to the content plane.** FLOW-R's flow direction is free. Blowing the rain along the content's thin axis (e.g. from a wall or shelf head behind a panel-like image) puts every in-plane stroke perpendicular to the flow. RT9's texture law then gives short ~3–5 mm gaps everywhere, instead of 67 % of vertical-stroke length in > 10 mm gaps [DERIVED from RT9 §10]. A 30–45° oblique flow is the compromise for 3D content.

4. **Contrarian (C3).** RT9's hand-wake aim miss (σ 71 µm, 15–39 % hits) uses the inertial-range diffusive Lagrangian model √(C₀εt)·t/√3. At a 3–6 ms look-ahead that model is invalid, because Δ ≪ τ_η = 35 ms (wake) and 196 ms (core). In the dissipative range velocity is smooth, so the miss is ½·a·Δ² plus the estimator error:
   - σ = **19–31 µm in the wake** at Δ 3–5 ms with 1 kHz frames and 10 µm centroids;
   - hits **57–88 % (w 80) and 92–99.8 % (w 140)**.

   This is analytic only and needs a Monte Carlo check (§3.1).

5. **Desk FLOW-R (opus round 4 §5, 3D tracking) against RT9 C1–C3** (§4):
   - **C1 escapes.** Tracking lights every crossing: 16–19 /s per sample, against 3.4–4.8 /s for the FLOW-R2 probe.
   - **C2 is marginal as specified:**
     - per head 0.84–1.56 mW, i.e. 2.2–4× the 0.39 mW AEL at the scan vertex and 0.4–1.4× at 100 mm;
     - a pupil inside the column on an along-beam stroke gets 0.8–1.5×.

     It passes with a ≥ 100 mm recessed exit plus 3–4 heads, or with EVAP's bigger drops (0.2–0.36× at 100 mm).
   - **C3 passes in the core** (σ 10–23 µm, 79–99.9 % hits at w 80). It is **marginal in a hand wake at B′'s w 80** (57–88 %) and passes at w 140.

6. **Contrarian checks on the pillars:**
   - **EN 50689 skin aperture of 1 mm: confirmed** by an independent snippet. Not over-strict as a reading.
   - **O-band: the ×10 skin lever is confirmed.** But the "Class 1 eye AEL ~0.1–0.5 W at 1310 nm" is a dual-limit reading that IEC 60825-1 Ed. 3 itself flags: "may not adequately protect the anterior parts of the eye … caution". Physically, 1310 nm heats the anterior eye like 1550 nm at **~4.5× (collimated) to ~8× (focused) the power, not 50×**.
     - So RT8 C1's 27–91 mW pupil stacking at 1310 nm is **0.6–2× the physical equivalent of 1550 nm Class 1**, not "0.05–0.18×, resolved".
     - The per-focus skin cap still binds.
   - **Drafts.** The tetralemma at the mean v is lenient, not strict: gusts raise the loop rate ×3–4.
   - **T9's drying time of 0.86 s is ×3 too short.** A drop's surface sits at the wet-bulb temperature, so a 30 pL water drop lives **2.6 s** at 20 °C and 50 % RH. FLOW-R's trehalose drying duct must be ×3 longer.

7. **Dead, with numbers** (§1):
   - ambient room dust as the medium (×10³–10⁴ too sparse);
   - fixed-ray engines: DLP/LCD projectors are ×3 000 short of pixel power, and VCSEL ray arrays are starved ×60;
   - IR erasure of unwanted drops (~12 W latent, ~30 W IR);
   - gravity drizzle (7.5 mm/h rain);
   - an electric drift column (space charge: 9 mm/s at 3 kV/m);
   - confocal self-gating (voxel starved ×10–25);
   - spinning invisible filaments (child safety means an enclosure);
   - LED spot lighting (étendue).

   **Vortex-ring mist delivery** from ceiling heads is physically possible but coarse (±7–19 cm), faintly visible as rings, and unproven: [SPECULATIVE], P ≈ 0.1.

8. **Ranking** (§5). P(physically works) × fit:
   1. **EVAP-R desk "holo-pendant"**: 0.45 × 0.35 ≈ 0.16;
   2. FLOW-R desk with RT9-proof fixes: 0.45 × 0.25 ≈ 0.11;
   3. EVAP-R room pendant with regional seeding: 0.15 × 0.45 ≈ 0.07;
   4. aerial-imaging plate: 0.95 × 0.05;
   5. O-band static voxels: ~0.05 × 0.8;
   6. vortex-ring delivery: 0.1 × 0.4.

   A 6-week, ~$4–8k bench for EVAP-R is in §6.

---

## 1. Attacks on the four pillars

### 1.1 Pillar 1 (no fog): media that are not fog

| # | Candidate | Deciding numbers | Verdict |
|---|---|---|---|
| 1a | **Self-erasing pure-water drops (EVAP-R)** | 30 pL (d₀ 38.5 µm) lives t = ρ_l·d₀²/(8·D_v·Δρ_v), with Δρ_v = ρ_s(T_wb) − ρ_v∞: **1.76 / 2.60 / 4.51 s at 30 / 50 / 70 % RH** (20 °C). It leaves no residue. 17 g/h for a desk rain | **Top idea** (§2). Bends "no fog" in name (water mist), not in sight (sub-visible). Removes capture and particulate [DERIVED] |
| 1b | **Medium only where the image is** (regional seeding × finite lifetime) | Seed only the content footprint ± 5 cm (needs Tu ≤ 3 % over 1.5 m, so σ ≤ 4.5 cm; home Tu 0.5–1 % suffices), and tune the lifetime so drops vanish 5–30 cm below the image. Desk mist volume ≈ 0.2 × 0.2 × 0.5 m | **Works as a lever** inside EVAP-R. Not a separate route [DERIVED] |
| 1c | **Ambient room dust as the medium** (nothing added) | Indoor particles ≥ 5–10 µm: ~10³–10⁵ /m³ [ESTIMATE from 5–10 µg/m³ coarse PM] vs the 1.6×10⁷ /m³ needed. The fill F = n·U·d_s²·t_eye falls ×10²–10⁴. Using all particles ≥ 1 µm (10⁶–10⁷ /m³) needs ×~460 beam power per particle (cross-section), i.e. > Class 1 per beam, and tracking sub-µm particles | **Dead** [DERIVED] |
| 1d | Laser-induced condensation | Needs fs filaments in supersaturated air (TW-class, plasma, ozone) | **Dead** (plasma kill applies) [memory] |
| 1e | Subliming motes (camphor, menthol, CO₂ snow) | Vapour exposure and smell; CO₂ snow needs −78 °C generation and is a gas release | **Dead** for a home product [ESTIMATE] |
| 1f | Motes recycled inside the volume (a closed vortex or stationary ring) | No steady flow traps inert particles (T9 §2.7, divergence-free velocity). A held vortex in open air needs an opposing jet, which is a column | **Dead** [DERIVED, T9 §2.7] |
| 1g | Fluorescent additive in the water (no speckle) | ppm dye leaves ~ng residue particles per drop, so it is no longer self-erasing | **Rejected**: it trades away EVAP's only advantage [DERIVED] |

### 1.2 Pillar 2 (occupied open air): make drafts irrelevant without a column

| # | Candidate | Deciding numbers | Verdict |
|---|---|---|---|
| 2a | **Selection plus short-lived local medium** (EVAP + tracking) | Drafts move drops but do not destroy a uniform field. The medium lives 1.8–4.5 s, so a 5 cm/s draft displaces it ≤ 9–23 cm. The column survives only as a gentle delivery jet (0.044 m³/s desk; push only, no pull) | **Lever**: the column shrinks to a push-only pendant/wall jet [DERIVED] |
| 2b | **Flow direction as a design variable** | RT9 law: F(θ) ≈ n·U·d_s·t·(d_s·\|cos θ\| + b·\|sin θ\|). Gaps > 10 mm hold 67 % of stroke length at θ = 0 vs 7 % at θ = 90°. Flow ⟂ the content plane makes every in-plane stroke θ = 90°. A 45° oblique flow cuts the strokes within ±10° of the flow from ~40 % (armor, vertical flow) to ~10–15 % [ESTIMATE] | **Lever**, free [DERIVED] |
| 2c | **Vortex-ring delivery** (ceiling head fires mist-laden rings; no column) | Turbulent ring: R = α·x, U ∝ x⁻³, α ≈ 0.01–0.02 [memory, Glezer & Coles 1990]. For R₀ 3 cm, x₀ = R₀/α ≈ 2 m: crossing 1.2 m takes 2.8 s and arrives at 0.24 m/s (U₀ 1 m/s), or 1.4 s at 0.49 m/s (U₀ 2 m/s). **Drift in a 5 cm/s draft: 7–14 cm** (±15–19 cm at slow arrival). The capsule needs ~10⁸ /m³ drops: ~1 % optical depth, i.e. faint visible rings against a dark wall | **[SPECULATIVE]**, P ≈ 0.1. Coarse, visible-ish, unknown puff uniformity (fill flicker) |
| 2d | Electric drift column (charged drops pulled down by a room field) | Space charge E_sc = n·q·R/(3ε₀) ≤ 0.3·E caps q ≤ 3ε₀·0.3E/(nR) = 5×10⁻¹⁸·E C (n 1.6×10⁷, R 0.1 m). Drift v = qE/(6πμa) = **8.7 mm/s at 3 kV/m**, ~0.1 m/s only at 10 kV/m, which is the perception threshold, and grounded bodies concentrate it | **Dead / marginal** [DERIVED] |
| 2e | Gravity drizzle (100 µm water drops at their own 0.25 m/s) | v_t = 0.25 m/s (Re 1.6). The same number flux gives **7.5 kg/m²/h = 7.5 mm/h rain**. Lifetime ~13–17 s, so drops reach the floor | **Dead** (re-confirms the drop-rain kill) [DERIVED] |
| 2f | Heavier or inertial motes | Inertia filters only gusts faster than 1/τ_p. The mean drift equals the air speed. The light-force-to-drag ratio is size-independent (I_unit, T6 B2) | **Dead** [DERIVED] |
| 2g | Active room-air control (jets or sound cancelling drafts) | 5 cm/s by sound needs 20 Pa = 120 dB (opus round 3). Jets add vorticity | **Dead** [DERIVED, round 3] |

### 1.3 Pillar 3 (child-safe light)

| # | Candidate | Deciding numbers | Verdict |
|---|---|---|---|
| 3a | **O-band holding light** (main session, m24) | Skin ×10 (C_A = 5): 7.85 mW per 1 mm. Eye dual limit 0.5 W per the standard. **My check (§3.2):** physical anterior-eye heating makes 1310 nm ≈ 1550 nm at ×4.5–8 the power. Skin still binds per focus | **Confirmed** for the skin cap. The eye-margin claims shrink ~×6–10 |
| 3b | EN 50689 skin aperture: 1 mm or IEC's usual 3.5 mm? | A 3.5 mm aperture would give ×12 (9.6 mW at 1550 nm). The independent snippet says EN 50689 measures skin-accessible emission "using a 1 mm aperture and timebases of 10 s (> 400 nm)" | **Not over-strict**: the 1 mm reading stands [MEASURED, snippet] |
| 3c | **Bigger scatterers lower the per-beam power** (selection displays) | P_beam ∝ 1/(1 − e^(−2a²/w²)). Water drops at a 15 µm image radius vs trehalose at 7 µm: ×4.6 cross-section | **Lever** (EVAP-R): C2 at desk scale falls ×2–4 (§4) [DERIVED] |
| 3d | Recessed scan vertex (spread before the first accessible plane) | At desk scale 8 lit drops share a head. At 100 mm from the vertex beams spread over 25–45 mm, and a 7 mm pupil catches 20–35 % | **Cheap at desk scale**; needs 200–300 mm or ×2 heads at room scale [ESTIMATE] |
| 3e | Geometry that makes a focus inaccessible; self-limiting optics | The touchable region *is* the focus region. Self-limiting means sensing plus blanking, i.e. an interlock (P 0.2–0.3, round 2) | **No new mechanism** [DERIVED] |
| 3f | Incoherent (LED) spot lighting, under IEC 62471 instead of 60825 | Étendue: a 1 W, 1 mm² LED (3.1×10⁻⁶ m²sr) into a w 140 µm, NA 0.05 spot (4.8×10⁻¹⁰ m²sr) gives 0.16 mW, but the depth of field is only ~w/NA ≈ 3 mm. At NA 0.01 it gives 6 µW | **Dead** for steered spots [DERIVED] |
| 3g | Visible colour choice | Cyan at 488 nm: V = 0.14 (×5 power vs 520 nm) and a photochemical Class 1 limit of ~0.22 mW [memory, C3 = 10^(0.02(λ−450))]. **Use 505–520 nm for the Iron-Man cyan-green** | Design rule [ESTIMATE] |

### 1.4 Pillar 4 (commodity addressing)

| # | Candidate | Deciding numbers | Verdict |
|---|---|---|---|
| 4a | Consumer DLP/LCD projector as the FLOW-R lighting engine | A 1 W projector spreads ~1 µW per pixel. A 14 µm mote in a 0.3 mm pixel intercepts 1.7×10⁻³, so it needs ~2.9 mW per lit pixel. **×3 000 short** (amplitude modulators cannot concentrate light) | **Dead** [DERIVED] |
| 4b | Addressable VCSEL array as fixed rays | True rate n·U·w_r·d_s = 1.6e7 × 0.25 × 8e-5 × 1e-3 = **0.32 /s** per ray-sample vs 20 /s (×60 starved). Stroke coverage = ray fill factor ~4 % | **Dead** [DERIVED] |
| 4c | **2D AOD heads** (multi-tone, silent, ~10 µs access) | 8–40 simultaneous spots per head. At w 140 µm, z_R = πw²/λ = **0.12 m**, so one fixed focus covers a 0.2 m desk image (w 80 needs 3 focus bands) | **Lever** with EVAP-R's wide spots [DERIVED; AOD price $1–3k per axis, ESTIMATE] |
| 4d | Confocal self-gating (the visible beam is its own probe; head photodiode behind a pinhole) | The two-head coincidence voxel has a horizontal projected area ~(2w)² = 0.03–0.08 mm² vs 0.5–0.7 mm² for FLOW-R2's already-starved probe | **Dead as gating; useful as hit-confirmation** for drift calibration [DERIVED] |
| 4e | Event cameras for the final aim | Sub-ms latency [memory] gives Δ ≈ 1–2 ms, so σ ≲ 15 µm even in hand wakes (§3.1) | **Lever** for C3 [ESTIMATE] |
| 4f | Commodity SBP for O-band static voxels | Need 7.7×10⁶ true modes at 4.4 kHz per head (3 cm/s). DLP9000 (4.1 Mpx, ~15 kHz binary [memory]): binary Lee holograms give ~10⁶ modes at ~10 % efficiency, so **~8 per head and ×10 IR**. TI PLM 1.3 Mpx at 1.44 kHz: too slow. **At 1 cm/s** (2.6×10⁶ modes, 840 Hz) two PLMs per head suffice: commodity for a *still room* only | **Gap ~3–10× at home drafts** (agrees with T9 §2.9) [DERIVED] |
| 4g | Regional seeding cuts the tracking load | Room armor: footprint 0.045 m² vs a 0.45 m² column means ×10 fewer drops, **0.06 ppp at 12 MP** instead of ~0.5 | **Lever**: room tracking becomes research-grade rather than impossible [DERIVED] |

---

## 2. EVAP-R: the self-erasing water rain (top idea)

### 2.1 Drop lifetime: the wet-bulb d²-law [DERIVED]

A small drop's surface sits at its wet-bulb temperature T_s, set by **k_a·(T − T_s) = L_v·D_v·(ρ_s(T_s) − ρ_v∞)**. Inputs: k_a = 0.0257, L_v = 2.45 MJ/kg, D_v = 2.5×10⁻⁵, Magnus ρ_s. The lifetime is t_L = ρ_l·d₀²/(8·D_v·Δρ_v).

| 20 °C | T_s | Δρ_v (g/m³) | 10 pL (26.7 µm) | **30 pL (38.5 µm, HP45)** | 41 pL (42.7 µm) | Fall of 30 pL in a 0.25 m/s column |
|---|---|---|---|---|---|---|
| RH 30 % | 10.0 °C | 4.21 | 0.85 s | **1.76 s** | 2.17 s | 0.48 m |
| RH 50 % | 13.2 °C | 2.84 | 1.25 s | **2.60 s** | 3.20 s | 0.71 m |
| RH 70 % | 16.1 °C | 1.64 | 2.17 s | **4.51 s** | 5.55 s | 1.23 m |
| RH 50 %, ambient surface (T9's form) | — | 8.62 | — | 0.86 s | — | — |

- **Check:** 998 × (38.5 µm)² = 1.479×10⁻⁶ kg/m; ÷ (8 × 2.5×10⁻⁵ × 2.84×10⁻³) = 2.60 s. ±10 % for D_v(T_s) and ventilation (Re ≈ 0.1) [DERIVED].
- **Correction to T9 §3.3.** The "d²-law drying 0.86 s" omits the wet-bulb depression. The real figure is ×3, so **FLOW-R's trehalose drying duct must be ~3× longer** (more still as a solute shell forms).
- **Fall** z = (U + v̄_s)·t_L, with v_s(38.5 µm) = ρgd²/(18μ) = 4.45 cm/s, averaging half of that over the drop's life.
- **Size at the image** (injection 0.1 m above a 0.2 m image):
  - 50 % RH: d = 38.5·√(1 − t/t_L) = **35.7 µm at the top, 29.2 µm at the bottom**;
  - 30 % RH: 34.2 → 23.6 µm;
  - 70 % RH: 37.0 → 33.8 µm.

  Brightness ∝ d². The controller knows each drop's z and age, so it scales the flash energy.
- **RH robustness.** The vanish height moves ×2.6 between 30 % and 70 % RH.
  - Warming the column to lower RH is **not** allowed: +3 K stalls a 0.5 m desk column (U² = U₀² − 2g′H < 0, RT9 M5).
  - Humidifying the column air is not allowed either: 0.044 m³/s × 5 g/m³ = 0.8 kg/h into the room.
  - Use **drop volume** instead: two printheads (e.g. 10 pL and 30 pL), or a grayscale piezo head, chosen by a hygrometer. Also set the image within the top ~0.3 m below injection [DERIVED].

### 2.2 Water load, cooling and the column [DERIVED]

| Case | Rate | Water | Steady room increment (50 m³, 0.5 ACH) | Latent sink |
|---|---|---|---|---|
| Desk, 30 pL, 0.2 m seeded core (B′ rain n 1.6×10⁷ /m³) | 1.6×10⁵ /s | **17 g/h** | +0.69 g/m³ (**+4 % RH**) | 11.7 W |
| Desk, 10 pL | 1.6×10⁵ /s | 5.7 g/h | +1.3 % RH | 3.9 W |
| Room armor, pendant 0.2 m above a 0.6 m image, regional seeding 0.045 m², n 2.6×10⁷, 41 pL | 2.9×10⁵ /s | **43 g/h** | +1.7 g/m³ (+10 % RH) | 29 W |
| Room, ceiling column 1.5 m fall (62 µm drops), full 0.45 m² column | 1.4×10⁶ /s | **630 g/h** | saturates the room | — |

For scale: a person exhales ~40 g/h and a room humidifier delivers 200–500 g/h [memory].

**Consequences:**
- **Delivery distance costs water as (distance/U)^1.5 per drop**, because the needed d₀ ∝ √(distance/U). So the air source must sit close to the image: a pendant or wall head, not a ceiling.
- **Column cooling.** 11.7 W into 0.044 m³/s × 1.2 × 1005 = 53 W/K gives **−0.22 K**. Over 0.5 m: U² = 0.0625 + 2·(9.81·0.22/293)·0.5, so U = 0.264 m/s (+6 %). Harmless; it slightly helps a downward column.
- **Glove.** τ_p = ρd²/(18μ) = 2.8–4.5 ms, so St = τ_p·U/r_finger = 0.14–0.23 and ~10–20 % of drops impact. A palm held in the rain collects ~0.4–0.9 g/h: a few mg per minute, which evaporates [DERIVED / ESTIMATE].
- **Satellite drops** of a few pL vanish in ≤ 0.3 s. Unlike sugar satellites, they leave nothing respirable.
- **Hygiene.** Use distilled water and treat the reservoir as one does a humidifier's (refill and clean) [ESTIMATE].

### 2.3 Optics: Mie scattering of water drops vs a white mote [DERIVED, `r5_mie.py`]

p_rel = 4π·(dσ/dΩ)/(πa²), size-averaged ±10 %, 520 nm. A white Lambertian sphere (ω 0.9) gives p_rel = ω·(8/3π)·[sin α + (π−α)·cos α], with α = 180° − θ.

| Scatterer | 20° | 40° | 60° | **90°** | 120° | 140° | 150° | 160° | Rainbow peak |
|---|---|---|---|---|---|---|---|---|---|
| Water 14 µm | 8.55 | 2.46 | 0.60 | **0.055** | 0.081 | 0.60 | 0.30 | 0.27 | 141.6°: 0.67 |
| Water 30 µm | 8.54 | 2.46 | 0.51 | **0.035** | 0.061 | 0.77 | 0.26 | 0.23 | 141.1°: 0.85 |
| Water 38.5 µm | 8.62 | 2.41 | 0.49 | **0.039** | 0.051 | 0.86 | 0.36 | 0.22 | 140.8°: 0.92 |
| White Lambert (ω 0.9) | — | 0.08 | 0.26 | **0.76** | 1.46 | — | 2.11 | — | — |

At 450 and 638 nm the values are within ±20 % of these (38.5 µm: 90° 0.033 / 0.042; 140° 0.87 / 0.81).

**Head layouts.** Each drop is lit by all heads with equal power. The table gives p per unit total beam power for horizontal viewers at all azimuths:

| Layout (elevation seen from the image) | Water 30 µm min / median / max | White min / median / max |
|---|---|---|
| 2 heads, el 60°, opposite (FLOW-R) | **0.035** / 0.14 / 0.29 | 0.76 / 0.81 / 0.86 |
| 3 heads, el 60° (pendant rim) | 0.10 / 0.15 / 0.20 | 0.81 |
| 3 heads, el 30° | 0.31 / 0.92 / 1.65 | 0.92 |
| **4 heads, el 30°** | **0.54 / 0.95 / 1.29** | 0.91 |
| 6 heads, el 25° | 1.04 / 1.17 / 1.29 | 0.93 |
| 3 heads, el 15° | 0.38 / 1.42 / 3.82 | 0.96 |

**Readings:**
- **Top lighting (FLOW-R's heads) fails for water by ×5–22.**
- **A low ring (4–6 heads at 25–30°) reaches parity per unit area.** The heads on the far side use water's strong forward lobe (θ 40–60°, p 0.5–2.5), and the near-side heads use the rainbow (θ ≈ 141°).
- **Viewer-aware head selection** (cameras see where people are) lets each drop be lit only by the 1–2 heads that serve present viewers, which halves the power [DERIVED].
- **Cosmetic effects:**
  - colour shifts near the rainbow angle (~2° per colour);
  - per-drop twinkle from two-glint interference while the drop evaporates.

  Multimode diodes average both [ESTIMATE].

### 2.4 Power per lit drop and per beam [DERIVED]

**Required luminous intensity per lit drop.** J = L·d_s/(n·d_s²) = 1.5 × 10⁻³/16 = 9.4×10⁻⁵ cd (B′: 1.5 cd/m², d_s 1 mm, n 1.6×10⁷).

**Intercepted power.** P_int = 4πJ/(683·V·p) = 2.43×10⁻⁶/p W.

**Beam power.** P_m = P_int/(1 − e^(−2a²/w²)).

| Design | a at the image | w | Capture fraction | p (worst azimuth) | **P_m per lit drop (all heads)** | Per head beam | Aim radius w/2 | z_R |
|---|---|---|---|---|---|---|---|---|
| FLOW-R B′ (opus, trehalose) | 7 µm | 80 µm | 0.0152 | 0.50 (opus) – 0.76 (2 heads) | **0.21–0.39 mW** | 0.105–0.39 mW | 40 µm | 3.9 cm |
| EVAP-R, 4 heads el 30° | 15 µm | 100 µm | 0.044 | 0.54 | **0.10 mW** | 26 µW | 50 µm | 6.0 cm |
| **EVAP-R, 4 heads el 30°** | 15 µm | **140 µm** | 0.0227 | 0.54 | **0.20 mW** | **50 µW** | **70 µm** | **12 cm** |
| EVAP-R, 4 heads el 30° | 15 µm | 200 µm | 0.0112 | 0.54 | 0.40 mW | 100 µW | 100 µm | 24 cm |

**Readings:**
- **Every row is Class 1 per beam.** For a 4 ms horizontal crossing the flash is 0.2 µJ, against a single-pulse AEL of 7×10⁻⁴·t^0.75 = 11 µJ.
- **Ghost dots at w 140** (other drops within ±z_R in the beam tube): n·πw²·2z_R = 0.23, i.e. ~20 % of flashes, as RT9 found at room scale. The tracker knows every drop, so it **skips a head whose tube holds another drop** (P all four occupied = 0.2⁴ = 0.16 %). The residual is a few % plus a small azimuthal brightness loss [DERIVED]. At w 100 the ghost-tube probability is 0.08.

### 2.5 Haze [DERIVED]

**Room-light phase factor.** For upper-hemisphere room light (cosine-weighted) and horizontal viewers it is **0.635 for water vs 0.866 for white** per unit area. Water's forward lobe catches lights behind the column, so **water is not intrinsically less visible**.

**At equal number density**, the haze ratio is (d_water/14 µm)² × 0.733: **×1.65 (21 µm) to ×3.4 (30 µm)**.

**Scaled from RT9's calibration** (0.63 % optical depth ↔ 11 % contrast against a ρ 0.05 wall at 10 lux):
- desk B′ trehalose: ~2.7 %;
- **desk EVAP: ~4.5–9 % against a black backdrop, ~0.5–0.9 % against a ρ 0.5 wall.**

So it is sub-visible in an ordinary room, and faint against black in the dark. Smaller drops (10 pL) at low RH sit at the low end.

### 2.6 What EVAP-R changes in the vision fit

| Vision item | FLOW-R desk (opus) | **EVAP-R desk** |
|---|---|---|
| No table | hood above plus pedestal inlet below | **push-only pendant** (or wall/shelf head); nothing below the image |
| No gas or fog | sub-visible trehalose dust, 99 % capture, residue | **sub-visible water mist that vanishes 5–30 cm below the image**; no capture, no residue, no PM |
| Heads | 2 heads in the hood | 4–6 small laser heads at ~25–30° elevation (walls, shelves or pendant arms 0.5–0.8 m out) |
| Per-beam power and C2 | 0.1–0.39 mW; C2 marginal (§4) | **26–100 µW; C2 passes** with a 100 mm recess |
| Aim tolerance | 40 µm | **50–100 µm**; one focus band with AOD heads |
| Haze | ~2.7 % against black | ~4.5–9 % against black (×1.65–3.4) |
| New burdens | drying duct, capture, filters, sugar residue | RH-dependent vanish height (two drop sizes); 17 g/h water; beams end on the floor (faint sparkle: use a dark rug or mat) |
| Line texture | vertical strokes in long gaps | **flow-normal or oblique jet** gives short gaps (§1.2, 2b) |
| Noise | push ~21 dB(A) plus pull 27–30 dB(A) | **push only, ~21 dB(A)** (opus's scaling) |

### 2.7 Room scale [DERIVED / ESTIMATE]

**Configuration:** a 0.6 m armor, a pendant 0.2 m above it, 41 pL drops, regional seeding over 0.045 m², and RT9's room settings (3 mm sampling, 3 cd/m²).

| Item | Value |
|---|---|
| Drops in the image region | 7×10⁵, i.e. **0.06 ppp at 12 MP** (6–8 cameras, research-grade real-time tracking) |
| Simultaneous lit drops | n·d_s²·S = **81** |
| Power per lit drop (w 140, a 17 µm) | 0.19 mW |
| Load with 8 heads | **1.9 mW per head**: 4.9× at the vertex, ~1–2× at 100 mm. Needs a 200–300 mm recess or 16 heads |
| Water | 43 g/h (+10 % RH) |
| Cost | heads $3–14k + cameras $8–20k + air $1–3k: **~$15–40k** (vs RT9's $50–120k for FLOW-R2) |

### 2.8 Vortex-ring delivery (the "projector-only" stretch) [SPECULATIVE]

**The idea.** A ceiling head fires rings (5 cm orifice, speaker-driven, U₀ 1–2 m/s) whose humid capsule carries ~2×10⁴ drops each at ~3–25 Hz. No column and no pendant.

**Numbers** (§1.2, 2c):
- arrival in 1.4–2.8 s at 0.24–0.49 m/s;
- drift 7–14 cm in a 5 cm/s draft;
- drops must live ≥ 3–4 s, so d₀ ≳ 45–48 µm;
- capsule optical depth ~1 %, i.e. faint rings against a dark wall;
- the impulse is a breath-like puff (~3×10⁻⁴ N·s).

**Unknowns:**
- puff breakup and uniformity, i.e. fill flicker;
- ring-to-ring interference;
- whether the fill is steady enough.

**P ≈ 0.1.** Worth one afternoon on the bench (§6, optional).

---

## 3. Contrarian checks

### 3.1 RT9 C3: the look-ahead miss is overestimated in hand wakes [DERIVED, analytic]

**RT9's model.** σ = √(C₀·ε·t)·t/√3 (C₀ ≈ 6). This is a velocity random walk, valid only for τ_η ≪ t ≪ T_L.

**Where the aim actually operates:**
- **Wake** (ε = u′³/L = 1.25×10⁻² m²/s³): τ_η = √(ν/ε) = **35 ms**.
- **Core** (ε 3.9×10⁻⁴): τ_η = **196 ms**.
- The aim works at Δ = 3–6 ms ≪ τ_η.

There velocity is smooth, and the residual is the **unknown acceleration**. Heisenberg–Yaglom gives ⟨a_i²⟩ = a₀·ε^(3/2)·ν^(−1/2):
- wake (a₀ ≈ 2.3 at Re_λ ≈ 89 [memory, Sawford fit]): **a_rms ≈ 0.9 m/s²**;
- core: **0.07 m/s²**.

**Estimator.** A constant-velocity least-squares fit to N = 5 frames at 1 kHz (window 4 ms), predicting h = Δ + 2 ms ahead of the window centre:
- noise σ_c·√(1/N + h²/S), with S = τ²·N(N²−1)/12 = 10 ms²;
- bias ½·a·(h² − S/N), checked on an exact parabola.

| Region | σ_c | Δ | σ (per axis) | Hits w 80 (R 40) | w 140 (R 70) | w 200 (R 100) | RT9 |
|---|---|---|---|---|---|---|---|
| Core | 10 µm | 3 ms | 16 µm | 95 % | ~100 % | ~100 % | 93 % / 99.97 % (17 µm) |
| Core | 10 µm | 5 ms | 23 µm | 79 % | 99 % | ~100 % | — |
| **Wake** | 10 µm | 3 ms | **19 µm** | **88 %** | **99.8 %** | ~100 % | **15 % / 39 %** (71 µm) |
| **Wake** | 10 µm | 5 ms | **31 µm** | **57 %** | **92 %** | 99.5 % | — |
| Wake | 20 µm | 3 ms | 35 µm | 49 % | 87 % | 98.5 % | — |
| Wake | 20 µm | 5 ms | 50 µm | 28 % | 63 % | 87 % | — |

P(hit) = 1 − exp(−R²/2σ²), the same criterion as RT9.

**Readings:**
- **RT9's wake hits are too pessimistic by ×2–3 in σ** once the velocity is estimated over a window shorter than τ_η.
- The decisive inputs are **centroid noise ≤ 10–15 µm and latency ≤ 3–5 ms**.
- **Photons for the centroid.** For a defocus-blurred, shot-noise-limited drop, σ_c ≈ Δz/√(E·σ·p·t·QE/hν), independent of the aperture.
  - The IR flood must stay within the IEC 62471 exempt mean of 100 W/m² [memory], which caps E·t per 1 ms frame at 0.1 J/m².
  - For a 30 µm water drop and Δz 5–10 cm, σ_c ≈ **8–15 µm**. Trehalose motes (×4.6 smaller cross-section) get ×2.1 worse [DERIVED].
- **Status.** Analytic only. A red team should run Sawford's (1991) second-order Lagrangian model with this estimator before the numbers are used.

### 3.2 The O-band window (m24): a physical check of the eye margin [MEASURED rule + DERIVED]

**The rule is confirmed** (search, this session): "IEC 60825-1:2014, for classification of laser products as Class 1, specifies Class 3B AELs as dual limit" at 1250–1400 nm. **The standard also warns** that "the limits to protect the retina … may not adequately protect the anterior parts of the eye (cornea, iris) and caution needs to be exercised" [MEASURED, snippet].

**Physical estimate** (k = 0.58 W/m/K; water α ≈ 130 m⁻¹ at 1310 nm vs 1 000 m⁻¹ at 1550 nm [memory]):

| Beam | 1550 nm | 1310 nm | Ratio |
|---|---|---|---|
| Collimated, 3.5 mm | disc source: ΔT ≈ P/(π·r_b·k) → ~2–3 K at 10 mW (opus round 3: 1.8 K) | long cylinder (1/α = 7.7 mm ≫ r_b): ΔT ≈ (0.63P/(2πk/α))·(½ + ln(1/(α·r_b))) ≈ **44 K/W** → 0.45 K at 10 mW, **2.2 K at 50 mW, 22 K at 0.5 W** | equal heating at **~4.5×** the power |
| Focused at the cornea | 0.7–0.8 K/mW (opus round 3) | (Pα/4πk)·ln(1/(α·z₀)), z₀ ≈ 50 µm: **0.09 K/mW** | **~8×** |

**Consequences:**
- **The skin cap still binds.** Per focus at 1310 nm the skin allows 3.3 mW (after h·s 2.35). The physical eye equivalent, 45–80 mW ÷ 7.1 = 6–11 mW, is above that. m24's main lever (×10) survives.
- **RT8 C1's pupil stacking at 1310 nm** is 27–91 mW against a physical equivalent of ~45 mW: **0.6–2×, not 0.05–0.18×.** "Resolved" holds only under the dual-limit reading that the standard itself flags.
- A child-appealing product that relies on a 0.1–0.5 W eye AEL in this band invites a notified body to apply the caution note [ESTIMATE].
- **The mote absorber must move.** ITO's plasma edge sits near 1.2–1.6 µm, so absorption at 1310 nm is weaker. Cs_xWO₃ and carbon are fine [ESTIMATE].

### 3.3 The EN 50689 1 mm skin aperture [MEASURED, snippet]

The ×12 alternative (IEC's usual 3.5 mm skin aperture) is **not** available. EN 50689 measures skin-accessible emission through 1 mm over 10 s (> 400 nm). Pillar 3's reading is correct, not over-strict.

### 3.4 Drafts: is pillar 2 over-strict? [DERIVED]

**No.** The tetralemma uses the **mean** v (3 cm/s). That is fair for the 10 s skin-dose budget, which averages gusts; the short-term skin MPE allows ~×30 peaks over 0.1 s (m25 header). But the **loop** must follow gust peaks U + 5.4σ (RT6 C1), 0.13–0.6 m/s at home. So the loop column of T9 §2.8 (10·v/w) is lenient by ×3–4 (m22's own docstring). Neither pillar is over-strict.

### 3.5 T9 §3.3 drying time

0.86 s → **2.6 s** (§2.1, wet bulb).

---

## 4. Desk FLOW-R (opus round 4 §5, 3D tracking) against RT9 C1–C3

**Settings:** B′, 0.5 m of strokes, 20 Hz, δ 5 mm, d_s 1 mm, n 1.6×10⁷ /m³, 8 lit motes at once, 2 hood heads at 30° off vertical.

| Criterion | Desk FLOW-R as specified (trehalose, w 80) | Desk EVAP-R (water, w 100–140, 4 heads at el 30°) | Tag |
|---|---|---|---|
| **C1, rate.** Every tracked crossing is lit (no probe voxel). Rate = η_track × n·U·δ·d_s = η × 20 /s | **Escapes**: 16–19 /s at η 0.8–0.95 (vs 3.4–4.8 /s for FLOW-R2). Dark per 0.1 s: e^(−1.6 to −1.9) = **15–20 %** (design 13.5 %) | same; larger drops raise η (photons ×4.6) | DERIVED; η at 0.03–0.07 ppp in real time [ESTIMATE, unshown] |
| **C2, head aggregation.** Per-head mean = N_lit·P_m/H | P_m 0.21–0.39 mW, H 2: **0.84–1.56 mW**, i.e. **2.2–4.0×** the 0.39 mW AEL at the scan vertex. At 100 mm (beams spread 25–45 mm; a 7 mm pupil catches 20–35 %): 0.17–0.55 mW = **0.4–1.4×** | P_m 0.10–0.20 mW, H 4: **0.2–0.4 mW**, 0.5–1.0× at the vertex; **0.1–0.36× at 100 mm** | DERIVED (capture fraction ESTIMATE) |
| C2, pupil inside the column, stroke along a beam (~3 lit motes) | up to 3 × 0.105–0.195 = 0.3–0.6 mW: **0.8–1.5×** | 3 × 26–50 µW = 0.08–0.15 mW: **0.2–0.4×** | DERIVED |
| C2, skin at the exit window (1 mm, visible 1.57 mW) | ≤ 1.56 mW: borderline at the vertex; OK with a 100 mm recess | OK | DERIVED |
| **C3, aim** (§3.1; Δ 3–5 ms, 1 kHz ROI, σ_c 10 µm) | Core: **79–95 %**. Hand wake: **57–88 %** (RT9 said 15 %) | Core ~100 %. Wake: **92–99.8 %** (w 140) | DERIVED (analytic) |
| C3, registration | Cameras to galvo ≤ 20–30 µm over 0.5–0.8 m. Aluminium at 23 µm/m/K drifts ~16 µm/K, so recalibrate in closed loop every few seconds from observed flash hits. ILDA galvo LSB ~11 µrad (8 µm at 0.7 m) [ESTIMATE] | same; the 70 µm aim radius leaves margin | ESTIMATE |

**Answer to task 3:**
- **C1: yes, escapes.** It was an artefact of probe gating.
- **C3: yes in the core, and in the wake at w ≥ 140**, if latency is ≤ 3–5 ms and centroids are ≤ 10–15 µm. It is marginal in the wake at B′'s w 80.
- **C2: not cleanly, as specified.** Two hood heads carrying 8 lit motes are 2–4× the AEL at the vertex and up to 1.4× at 100 mm. A ≥ 100 mm recessed exit plus 3–4 heads, or EVAP's bigger drops, passes.
- The **real-time tracking** at η ≥ 0.8 with ≤ 5 ms end-to-end latency is the open item. It is commodity cameras plus custom software, not physics.

---

## 5. Ranking: P(physically works) × fit to the vision

| Rank | Idea | P [ESTIMATE] | Fit [ESTIMATE] | Score | What it bends |
|---|---|---|---|---|---|
| **1** | **EVAP-R desk "holo-pendant"**: push-only pendant (or wall-head flow-normal) jet; 30 pL distilled-water rain that vanishes below the image; 4 low RGB/AOD or galvo heads (w 100–140); 3–4 tracking cameras with 1 kHz ROI; viewer-aware heads | 0.45 | 0.35 | **0.16** | sub-visible transient water mist (owner's ruling); a pendant or wall jet; 0.2 m image; dotted lines; dim room |
| 2 | FLOW-R desk (opus) with C2/C3 fixes (100 mm recess, 3–4 heads, ≤ 5 ms aim) | 0.45 | 0.25 | 0.11 | sugar dust, hood plus pedestal, capture |
| 3 | EVAP-R room pendant (regional seeding, 0.6 m armor) | 0.15 | 0.45 | 0.07 | as rank 1 at 0.6 m; 43 g/h water; 0.06 ppp tracking; 8–16 heads; ~$15–40k |
| 4 | Aerial-imaging plate plus glove | 0.95 | 0.05 | 0.05 | a holo-window (excluded) |
| 5 | O-band static voxels (main session) | ~0.05 at home | 0.8 | 0.04 | unmade 1.3 µm mote; 3–10× modes at 3 cm/s; loop (m25 pending); eye margin physically ×4.5–8, not ×50 |
| 6 | Vortex-ring mist delivery from ceiling heads | 0.10 | 0.40 | 0.04 | faint visible rings, ±7–19 cm, fill flicker |
| — | Dead: ambient dust, projector or VCSEL fixed rays, IR erasure, drizzle, electric column, confocal gating, spinning filament, LED spots | — | — | — | §1 |

**"More, or something new?"** Within known physics and commodity parts, the vision needs *more*: a medium. The new part is that the medium can be **transient water** that leaves nothing and needs no capture. That is the smallest "medium" footprint this project has found. The irreducible bends are:
- a sub-visible, short-lived mist;
- a gentle air source (pendant or wall jet);
- dotted lines at fill 0.2–0.4;
- 0.2–0.6 m scale in a dim room.

---

## 6. Weeks-scale bench test for EVAP-R (6 weeks, ~$4–8k)

**Goal.** Decide four things:
1. whether a pure-water rain vanishes where the wet-bulb law says;
2. whether low heads light it as Mie says;
3. whether the aim reaches ≥ 90 % in a hand wake at ≤ 5 ms;
4. whether the heads are Class 1 per product.

**Week 1: drops and lifetime.**
- **Build:** an HP45 (open controller) firing distilled water at ~1.6×10⁵ /s into a 0.3 m push-only nozzle at 0.25 m/s, with a honeycomb and no pull. A 520 nm light sheet and a camera image the vanish height. **Water-sensitive spray cards** (agricultural, commodity) on the floor and a table at 0.3/0.6/0.9 m below measure deposition.
- **Sweep:** RH 30/50/70 % using a room humidifier or dehumidifier.
- **Pass:** vanish height within ±20 % of 0.48 / 0.71 / 1.23 m, and ≤ 1 drop/cm² per 10 min on a card 0.3 m below the predicted vanish height.
- **Fail meaning:** a large lifetime error kills the RH control plan.

**Week 2: optics.**
- **Build:** one RGB multimode diode on a galvo at 30° elevation, plus a calibrated camera on an arc at 0–180° azimuth.
- **Measure:** per-drop luminous intensity against angle; the Mie prediction is p(40°) 2.4, p(90°) 0.035, p(141°) 0.85, normalised to the beam power through a 7 mm aperture. Also measure the unlit column's contrast against a black and a grey backdrop under ceiling lights.
- **Pass:** within ×1.5 of Mie, and haze ≤ 10 % against black at 10 lux.

**Weeks 3–4: tracking and aim (the decisive test of §3.1 against RT9 C3).**
- **Build:**
  - 3 global-shutter cameras: full frame at 150–200 fps for track initiation, plus 1 kHz ROIs on a 1 mm × 5 cm stroke;
  - an 850 nm strobe at a mean ≤ 100 W/m²;
  - an FPGA or GPU predictor using a constant-velocity fit over 4 ms;
  - one galvo head, then one AOD head;
  - (optional) an event camera.
- **Measure:** the hit fraction (a flash on a drop seen by a visible-band camera) at Δ = 3/5/8 ms, in the core and 10 cm below a gloved hand moving at 0.1–0.2 m/s; also centroid σ_c.
- **Pass:** ≥ 90 % at w 140 in the wake at Δ ≤ 5 ms (my estimate: 92–99.8 %).
- **Fail:** ≤ 40 % at σ_c ≤ 15 µm means RT9's diffusive model is right, and the touch region degrades.

**Week 5: four heads and safety.**
- Run 4 heads at el 30° with a 100 mm recessed exit window.
- Measure the mean power through a 7 mm aperture at the window, at 100 mm and inside the column on an along-beam stroke, and through a 1 mm aperture at the window. Measure the stall-to-cut time.
- **Pass:** ≤ 0.39 mW (7 mm) and ≤ 1.57 mW (1 mm) everywhere; stall cut ≤ 50 ms.

**Week 6: glyph, people and room.**
- Show a 10 cm ring plus crosshair at 20 Hz in two configurations: a vertical pendant jet and a **flow-normal** horizontal jet.
- Run a 5-person viewing study: texture, sparkle, haze, colour shifts near the rainbow angle, floor sparkle, breeze.
- Log a hygrometer in a closed 30–50 m³ room for 2 h (predicted +4 % RH), glove dampness, and dB(A) at 1 m.
- **Pass:**
  - "floating and legible" from all azimuths;
  - flow-normal texture preferred;
  - ≤ +6 % RH after 2 h;
  - ≤ 30 dB(A).

**Optional (one afternoon).** A speaker-driven ring cannon (5 cm orifice) seeded with the same drops, fired over 1.2 m with a fan cross-draft of 5 cm/s. Measure arrival scatter (predicted 7–14 cm) and ring visibility against black.

---

## 7. Notes for the main session

1. **T9 §3.3:** drying 0.86 s → 2.6 s (wet bulb). The trehalose drying duct must be ×3 longer.
2. **RT9 C3:** the √(C₀εt)·t/√3 miss applies only for t ≫ τ_η. Use a dissipative-range model, i.e. Sawford 1991 with a windowed estimator, for 3–6 ms look-ahead. The wake numbers here (57–99.8 %) need that Monte Carlo before they replace RT9's 15–39 %.
3. **Desk FLOW-R C2:** count per-head load as N_lit·P_m/H. B′ is 2–4× at the vertex and 0.4–1.4× at 100 mm. Recess the exit ≥ 100 mm and use 3–4 heads.
4. **O-band (T9 §2.9, m24):** keep the skin ×10. Replace "eye AEL 0.1–0.5 W" with "standard: dual limit 0.5 W, with Ed. 3's own caution for the anterior eye; physics: ~45–80 mW equivalent". RT8 C1 at 1310 nm is then 0.6–2×, not resolved.
5. **The flow direction is a free design variable** in every rain display. Set it normal to the content's main plane (or oblique for 3D content). This is the cheapest fix for the vertical-stroke texture weakness.
6. **EVAP-R deserves an m26:**
   - wet-bulb lifetimes;
   - Mie p(θ) per head layout (`r5_mie.py` is a starting point);
   - per-head C2 load;
   - haze;
   - RH control by drop volume.

---

## Sources

**Web (this session, 3 searches):**
- EN 50689 measures skin-accessible emission through a 1 mm aperture with 10 s (> 400 nm) timebases; child-appealing products must be Class 1 (search summary): [SIST EN 50689:2022](https://standards.iteh.ai/catalog/standards/sist/3d8e5fe9-a2ff-4dbe-a38d-438365c3f907/sist-en-50689-2022); [JJR Lab on EN 50689](https://www.jjrlab.com/news/new-european-standard-for-laser-products-en50689-2021.html); [BS EN 50689:2021 preview](https://webstore.ansi.org/preview-pages/BSI/preview_30371378.pdf); [TÜV SÜD test report under EN 50689](https://s3file_list.lips-hci.com/s3file/LIPS%20Partner%20Portal/Product%20Resource/LIPSedge%20AE450/Certifications/Laser%20EU/AE450-20230925-6110623030701%20TUV%20SUD%20IEC_EN%2060825-12014%20EN%202021%20EN%2050689%20Report.pdf).
- IEC 60825-1:2014 uses the Class 3B AEL as a dual limit for Class 1 at 1250–1400 nm; the new C7 raises the Class 1 AEL there; the standard cautions that the retinal limits "may not adequately protect the anterior parts of the eye": [Schulmeister et al., Comparison of corneal injury thresholds with laser safety limits](https://www.researchgate.net/publication/336119396_Comparison_of_corneal_injury_thresholds_with_laser_safety_limits); [Schulmeister, The upcoming new editions of IEC 60825-1 and ANSI Z136.1](https://www.researchgate.net/publication/328325074_The_upcoming_new_editions_of_IEC_60825-1_and_ANSI_Z1361_-_Examples_on_impact_for_classification_and_exposure_limits); [IEC 60825-1:2014 preview](https://webstore.iec.ch/en/iec_catalog/product/preview/?id=L3B1Yi9wZGYvcHJldmlldy9pbmZvX2llYzYwODI1LTF7ZWQzLjB9Yi5wZGY%3D).
- Turbulent vortex rings, slow growth by an entrainment excess, similarity scaling: [Glezer & Coles, J. Fluid Mech. 211, 243 (1990)](https://stanford.edu/~cantwell/AA218_Course_Material/Resources/An%20experimental%20study%20of%20a%20turbulent%20vortex%20ring.pdf); [ADS abstract](https://ui.adsabs.harvard.edu/abs/1990JFM...211..243G/abstract).

**[memory]** (not re-checked):
- water refractive index and absorption at 1310/1550 nm;
- the ring growth α ≈ 0.01–0.02;
- Heisenberg–Yaglom a₀ ≈ 2.3 at Re_λ ~ 90;
- the IEC 62471 IR exempt limit of 100 W/m²;
- the photochemical C3;
- DLP9000 and PLM specifications;
- event-camera latency;
- indoor coarse-PM number densities;
- breath and humidifier water rates.

**Repository (read-only):**
- `05_reviews/FINAL_VERDICT.md`, `red_team_9_home.md`, `red_team_8_pov_x.md`;
- `09_unlock/T9_home_routes.md`, `idea_round_4_opus.md`, `idea_round_3_opus.md`, `T6_unlock_theory.md`;
- `m22_needles.py`, `m23b_rain_law.py`, `m24_oband.py` with `results/m24_run.log`, `m25_oband_static.py`;
- `rt6_check.py` (`bhmie`).

---

## Summary (≤ 400 words)

**The tetralemma stands.** No loophole keeps all four pillars at home with commodity parts. EN 50689's 1 mm skin aperture is confirmed independently, and drafts are treated leniently, not strictly.

**New idea, EVAP-R.** Replace FLOW-R's trehalose motes with 30 pL distilled-water drops. At the wet-bulb surface they live 1.8/2.6/4.5 s at 30/50/70 % RH and vanish 0.5–1.2 m below a push-only pendant or wall jet.
- **Gains:** no pedestal, capture, particulate or residue; 17 g/h of water.
- **Optics (Mie):** water is ×14–22 dimmer than white at 90°, but a low ring of 4–6 heads (25–30°) restores parity.
- **Power:** the bigger drops need ~50 µW per head beam at w 140 µm. That fixes RT9 C2 at desk scale and gives a 70 µm aim radius.
- **Costs:** haze ×1.6–3.4 against black, an RH-dependent vanish height, and floor sparkle. It is still a mist, so "no fog" needs the owner's ruling.

**New lever.** Blow the rain normal to the content plane, so every in-plane stroke gets short gaps.

**Contrarian results:**
- **RT9 C3** uses an inertial-range model at Δ ≪ τ_η. A dissipative-range estimate gives 57–88 % (w 80) and 92–99.8 % (w 140) hand-wake hits, against 15–39 %. It is analytic and needs a Monte Carlo.
- **O-band:** the ×10 skin lever holds. But Ed. 3 itself cautions about the anterior eye, and 1310 nm heats it like 1550 nm at only ×4.5–8 the power. So RT8 C1 there is 0.6–2×, not resolved.
- **T9's drying time** is ×3 short (2.6 s, not 0.86 s).

**Desk FLOW-R against RT9:**
- C1 escapes (16–19 /s per sample).
- C3 passes in the core, and in the wake at w ≥ 140 with ≤ 3–5 ms latency.
- C2 is marginal: 2–4× at the vertex, 0.4–1.4× at 100 mm. A recess plus 3–4 heads, or water drops, fixes it.

**Dead, with numbers:** ambient dust, projector/VCSEL fixed rays, IR erasure, drizzle, an electric drift column, confocal gating, spinning filaments and LED spots. Vortex-ring delivery is speculative (P ≈ 0.1).

**Ranking (P × fit):** EVAP-R desk 0.16 > fixed FLOW-R desk 0.11 > EVAP-R room 0.07 > aerial plate 0.05 > O-band static 0.04 ≈ vortex rings 0.04.

**Next step.** A 6-week, ~$4–8k bench: vanish height against RH, brightness by angle, hand-wake aim hits at ≤ 5 ms (decisive against RT9), Class 1 per head, and a flow-normal viewing study.

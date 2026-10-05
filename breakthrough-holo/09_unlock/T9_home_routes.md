# T9: Home routes. The air carries the motes, light addresses them, and the full vision meets a tetralemma

**Status: the full vision is NOT SOLVED. FLOW-R2 as specified was REFUTED as a credible nearest build by red team 9 (correction box below).**
- The nearest candidate is **FLOW-R2**: a room-scale, gated, uniform mote rain. A camera-gated light engine replaces 3D tracking.
- It bends two of the owner's rules:
  - the medium: a sub-visible stream of food-grade motes;
  - the hardware: a ceiling air unit plus a floor grille.
- It also renders vertical strokes as flowing dashes.
- **Waiting on red team 9 (RT9).**

> **Correction by red team 9 (`05_reviews/red_team_9_home.md`, 3 critical, 6 major, 10 minor).**
>
> **Re-checked by the main session.**
> - C1 matches m23's own `r_vox` of 4.5–9 /s against the 20 /s budget, an inconsistency that m23 computed but never compared.
> - C3 is plain arithmetic: 0.58 mm of wander against a 40–70 µm aim.
> - C2 is confirmed to order of magnitude: the content subtends only ~0.12 × 0.19 rad from a ceiling head, so a pupil near the exit collects ~20–50 % of the 0.2 W probe fan.
>
> **What survives:**
> - the bounds of §2.2–2.6 and the tetralemma arithmetic (all reproduced);
> - the crossed-probe *geometry*;
> - the mannitol correction;
> - per-beam, per-flash visible Class 1 (C5 = 1 for point sources in IEC 60825-1 Ed. 3).
>
> **What fails for FLOW-R2 as specified:**
> - **C1, starved rain.** The probe ∩ camera voxel admits only 3.4–4.8 crossings/s per sample, 17–24 % of the 20 /s design. That leaves 62–71 % of samples dark per 0.1 s, not 13.5 %. Fixing it needs a ≥ 3 mm² sheet voxel (ghosts 1–5 %) or a ×4–6 rain (48–67 % haze contrast, no longer sub-visible).
> - **C2, heads are Class 1 per beam, not per product.** About 1 000 lines leave each ceiling head in a tight bundle:
>   - visible: 11.5–115× the CW AEL at 10 cm;
>   - 850 nm probe: 133× at 10 cm, 35× at 50 cm;
>   - skin at the probe exit: 24× (EN 50689).
>
>   A distributed, wide-aperture launch is needed. It is neither commodity nor discreet.
> - **C3, missed shots.** The 23 ms open-loop look-ahead hits the mote for 0.2–0.7 % of flashes. Velocity estimation plus ≤ 1.5 mm look-ahead gives 93–99.97 % in the core, but 15–39 % in a hand's wake.
>
> **Majors:**
> - **M1, photons vs depth of field.** A 35 mm aperture blurs ~3 mm. At 6–12 mm the budget is 230–1 070 e⁻.
> - **M2, gated fill.** Gated flashes cut the fill to 0.11–0.15 (vertical) and 0.05–0.09 (horizontal).
> - **M4, particles.** 99.97 % capture is needed for WHO 45 µg/m³. Lactose carries milk protein, so trehalose should be the default.
> - **M5, column buoyancy.** ±0.3 K of column/room mismatch changes the image-level speed by ±20 %, and +1 K stalls it.
> - **M6, cost.** ~$50–120k.
>
> **The main session's fill law (m23b) is confirmed**, with a qualification: vertical strokes keep 67 % of their length in gaps > 10 mm (horizontal: 7 %).
>
> **Net:** T9's top verdict ("not solved") is confirmed and strengthened. **FLOW-R2 is not a credible nearest full-vision build as specified**, and it bends three rules, not two (medium, ceiling and floor hardware, dotted or streaky lines). Its redesign path is RT9's "what would change the verdict" items 1–6, none of which is commodity or shown.

**Sources:**
- Models m20 (FLOW-X), m21 / m21b (AIR-SV), m22 (needles), m23 (FLOW-R2).
- `idea_round_4_opus.md` (idea round 4, independent).
- All runs are logged in `results/`.

---

## 0. Verdict in one screen

1. **Full vision, as the owner wrote it:**
   - touchable, open air, no table or wall, no glasses / gases / screens;
   - safe every day, a "sophisticated projector", built from commodity parts.

   **Not reachable with known physics plus commodity parts.** The tetralemma (§2.8) gives four requirements that cannot all hold at home. Each escape found so far relaxes at least one of them.

2. **New bounds this round** (m22). Each closes a door that looked open:
   - **Laplace low-pass.** Fields set up from outside the image cannot address mm structure. Only waves address single motes.
   - **One-way photo-charge.** Per-bead charge control ratchets out in seconds.
   - **Thermal kick theorem.** Time-sharing costs heat in proportion to T_rev/τ_th.
   - **Self-addressing laser cavities need 5–800 kW of pump.**
   - **Coulomb crystals are 10²–10⁵× too soft** against drafts.

3. **Air-carried routes** (idea round 4 opus, double-checked here):
   - **FLOW-X as briefed fails at home.** It needs Tu ≤ 0.2 % and a 2D on-demand injector, and content lags by 1.2–5 s.
   - **AIR-SV is dead in open rooms.** It needs cross-drafts ≤ 8–21 mm/s, and hands and plumes destroy it. **E-AIR-SV** (fixed bead charge plus a weak field, this round) repairs the static wake and size-spread problems, but not drafts, hands or content speed. It survives as an enclosed sculpture.
   - **FLOW-R** (opus) is the strongest: a uniform rain of white motes in a gentle downward column. Only motes crossing the content are lit, so content updates in one frame and survives hand wakes.

4. **FLOW-R2 (this round) removes FLOW-R's room-scale wall, 3D tracking.**
   - An invisible IR pencil projector sends one beam through a point just above each content sample.
   - Two or three ordinary cameras watch only those pixels.
   - A mote seen by all cameras at once is at the content point by geometry, so no tracking is needed. Accidental ghosts are ≤ 0.6 % with two cameras (m23).
   - What remains at room scale:
     - the visible spot engine: 20–80 simultaneous focused spots, ~10⁷ modes or 40–60 galvo channels, ~$10–30k;
     - 20–34 g/h of motes;
     - ≥ 99.9 % capture;
     - faint haze against dark walls (6–11 % contrast at 10 lux);
     - vertical strokes shown as ~33 %-filled flowing dashes (59 % of the Iron-Man armor's strokes are near-vertical).

5. **Rule-12 corrections to the opus report:**
   - **Mannitol must not be used.** Inhaled mannitol is a bronchial provocation agent (the Aridol test). Use lactose (an inhalation excipient) or trehalose.
   - **The room rain is denser than opus's room row** once sampling is 3 mm at 3 cd/m²: 56 vs 35 mg/m³.
   - **Vertical strokes are the main rendering weakness** (§3.4).

**No eureka:**
- FLOW-R2 needs the owner's rulings on the medium and on ceiling/floor hardware;
- RT9 has not run;
- the room-scale visible engine is not home-priced.

---

## 1. What "home" adds (from the round-4 brief)

- **Occupied rooms:**
  - drafts with mean 0.02–0.1 m/s and σ_u 0.02–0.1 m/s;
  - bare-hand plumes of 0.1–0.4 m/s (0.035–0.2 m/s with an isothermal glove).
- **EN 50689 for child-appealing products:** skin 0.785 mW per focus (1 mm aperture, 10 s), eye Class 1.
- **Commodity parts only**, and **particulate safety** (WHO PM10 24-h guideline 45 µg/m³).

---

## 2. Bounds

### 2.1 The addressing theorem and the holding/visibility tension [DERIVED, m21 header]

**Two costs pull mote size in opposite directions:**
- **Holding a mote with light** costs I(v)·area per focus. B2 makes I independent of size, so a per-focus cap gives **v_rel ≤ P_cap/(I_unit·a²)**: small motes win.
- **Lighting a mote for the eye** costs p/η_s with η_s ≈ 2a²/w². With w set by addressing, a fixed spot cap needs **M ~ A·p/(a²·P_cap)** modes: big motes win.

**Resolution:** let the air carry the motes (FLOW-X/R) or hold them (AIR-SV), and use light only to light or trim.

### 2.2 Laplace low-pass: only waves address [DERIVED, m22 §A]

**The bound:**
- A static or quasi-static field component of period Λ set up by sources a distance d away scales as exp(−2πd/Λ). This covers electric, magnetic and potential-flow fields.
- 3–6 mm structure from sources 5 cm away is attenuated by 10⁻²³–10⁻⁴⁶; from 30 cm, by 10⁻¹³⁷.
- To keep 1 % of a period-P component, the source must be within 0.73·P (4.4 mm for P = 6 mm).

**Consequences:**
- Electrodes, coils or air nozzles outside the image can only apply **common-mode and low-order** forces.
- Per-mote forces in open air require propagating waves: light (safe but weak) or sound (strong but loud).
- This generalises opus round 3's "Earnshaw: no mm-scale addressing".

### 2.3 Photo-charge is one-way, and its ratchet runs in seconds [DERIVED, m22 §B–C]

**Charge limits for a 20 µm bead in a 1 kV/m room field:**

| Charge route | q (C) | Note |
|---|---|---|
| Needed for useful force | ~10⁻¹³ | |
| Peek corona onset | 1.6×10⁻¹² | |
| Positive photocharge (recapture) | **7×10⁻¹⁷** | Photoelectrons thermalise and attach to O₂ within ~5 µm, where the bead's own field beats the room field. |
| Like-sign ion diffusion | 4×10⁻¹⁶ | |
| Pauthenier, room field | 1.3×10⁻¹⁶ | |
| Pauthenier, 1 MV/m corona zone | 1.3×10⁻¹³ | |

**So:**
- Light can only *lower* |q|, by photodetaching electrons from a negative bead.
- Raising |q| needs a corona zone outside the image.

**The ratchet** (m22 §C): per-bead loads fluctuate (an OU process with correlation time 1 s), the global field must cover the bead whose load swings from low to high, and every other bead then trims down.
- The global field leaves a 10× range in **23–31 s at 0.3 % load fluctuation**, 7–9 s at 1 %, and 0.1–0.2 s at 30 %.
- Bidirectional light that absorbs most of the fluctuation only stretches this to seconds.
- **Per-bead charge is therefore a static setting**, changed only on content changes.

### 2.4 The thermal kick theorem for time-shared trims [DERIVED, m22 §D]

**The theorem:** one beam serves K beads with dwell t_d, so T_rev = K·t_d. A lumped bead with τ_th = ρc·a²/(3k_g) peaks at

  ΔT_peak/ΔT_ss = K·(1−e^(−t_d/τ))/(1−e^(−T_rev/τ)) → T_rev/τ_th

with the same mean force.
- The closed form matches direct integration (9.755 vs 9.761).

**Examples at K 1000, t_d 0.1 ms:**
- ×10 for 40 µm, ρ 600;
- ×18 for 30 µm;
- ×78 for 20 µm, ρ 300;
- ×170 for 5 µm PMMA.

**Agreement with opus:** opus's lit-face surface flash (+146 K PMMA, +352 K glass shell at K = 1000) is the surface-layer version of the same theorem. Both give **K ≲ 300 or T_rev ≲ 3τ_th**.

### 2.5 Self-addressing laser cavities [DERIVED, m22 §E]

**The idea:** retroreflecting motes as cavity end mirrors sharing one gain medium. Lasing would exist only where a mote is, which lifts the skin cap (skin at a focus breaks the cavity) and self-addresses.

**The bounds:**
- Low diffraction loss needs a·R ≥ 0.72·λL, i.e. a 25–75 mm head radius at a 2 m throw.
- The gain étendue must equal the field's, (Xλ/πw)² ≈ 10⁷–10⁸ modes.
- A gain layer of thickness t = ln G_p/g holds NA² ≤ 2λ/(πt) without channel overlap.
- Hence the pump floor:

  **P_pump ≥ G_field·(ln G_p)²·hν_p/(2λ·g·σ_e·τ)**

| Gain medium | Pump floor |
|---|---|
| Er:Yb glass | 9×10⁴–8×10⁵ W |
| Nd:YAG | 3×10⁴–3×10⁵ W |
| Bulk InGaAsP | **5.5×10³–5×10⁴ W** |

**Dead.**

### 2.6 Coulomb crystals: charged motes as in-volume electrodes [DERIVED, m22 §F]

- **The idea:** motes inside the volume escape §2.2, because the field sources are now inside the image.
- **The numbers:** 5 µm beads at 3 mm spacing, up to the Peek limit: shear modulus 6×10⁻¹⁰–6×10⁻⁷ Pa, against a draft stress of 6×10⁻⁵ Pa (1 cm/s over 10 cm). The strain would be 10²–10⁵.
- **Dead.**

### 2.7 No passive trap for air-carried beads [DERIVED, opus §2.1]

- The inertia-free bead velocity u − v_s·ẑ is divergence-free, so a steady flow can at best be neutrally stable.
- The inertial correction is ≤ 0.1 s⁻¹.
- Every air-held voxel needs active trims.

### 2.8 The tetralemma for the full vision [DERIVED, m22 §H; B9; RT6–RT8]

The full vision would need all four of the following.

**(i) No fog.**
- At most ~10⁴ individually controlled motes.
- Or a sub-visible medium (FLOW-R) that the owner rules acceptable.

**(ii) Open air in an occupied room.**
- Per-mote authority must reach the mean relative speed v of several cm/s, with gust peaks of U + 5.4σ ≈ 0.2 m/s.
- The alternative is a conditioned air column that carries or holds the motes.

**(iii) Safety.**
- Per-mote force must come from light (§2.2). The per-focus cap then sets **w ≤ √(2P_cap/(π·h·s·I_unit·v))**.
- Under the child-skin rule (h·s = 2.35):
  - v = 1 cm/s → w ≤ 38 µm;
  - 3 cm/s → 22 µm;
  - 10 cm/s → 12 µm.

**(iv) Commodity addressing.**
- About (X/πw)² true modes per head, refreshed at ≥ 10·v/w.

| v | Modes per head | 4K LCoS per head | Loop |
|---|---|---|---|
| 1 cm/s | 2.6×10⁷ | 2.9 | 2.7 kHz |
| 3 cm/s | 7.7×10⁷ | 8.8 | 14 kHz |
| 10 cm/s | 2.6×10⁸ | 29 | 84 kHz |

Today's modulators run at 0.1–1 kHz for 4K LCoS and ~10 kHz for 1 Mpx DMDs.

**The escapes, and what each gives up:**

| Escape | Requirement it relaxes |
|---|---|
| Air column (AIR-SV, FLOW-X/R) | "not a table", plus touch or interactivity |
| Interlock safety | consumer classification (P 0.2–0.3, round 2) |
| Sub-visible rain (FLOW-R/R2) | "no gas" (owner's ruling) |
| Smaller, sparser image | the "full" in full vision |

No route found in eight red teams and four idea rounds relaxes none of them.

### 2.9 Addendum (main session, after RT9; **not yet red-teamed**): the O-band window [MEASURED rules + DERIVED, m24]

**What the project used.** Since round 1 it held motes at 1550 nm, chosen for eye safety. At 1550 nm the EN 50689 skin rule binds at 0.785 mW per focus (1 mm, 10 s; 1000 W/m²).

**Two Ed. 3 / ICNIRP rules change the picture at 1250–1400 nm:**
- **Skin:** the long-exposure MPE is 2000·C_A W/m² with C_A = 5 at 1050–1400 nm, i.e. 10 kW/m². That is **×10 → 7.85 mW per 1 mm**.
- **Eye:** Edition 3 raised C7 at 1250–1400 nm to 8 + 10^(0.04(λ−1250)), which is 259 at 1310 nm (32× the old value). The cornea is protected by a Class 3B dual limit of 0.5 W. So **the Class 1 eye AEL is ~0.1–0.5 W at 1290–1342 nm**, against 10 mW at 1550 nm.
- Sources: Seibersdorf white papers on IEC 60825-1 Ed. 3 and A11; ILSC 2019 "Comparison of corneal injury thresholds with laser safety limits"; ICNIRP 2013 as transcribed in `07_mote_route/R7_mote_safety.md`.

**Consequences** (m24):

| Item | Effect at 1310 nm |
|---|---|
| Binding per-focus cap | still skin, but **3.3 mW** after h·s = 2.35 (0.33 mW at 1550) |
| Tetralemma at 3 cm/s | w ≤ 69 µm, **7.7×10⁶ true modes**, 4.4 kHz (1550: 22 µm, 7.7×10⁷, 14 kHz) |
| Tetralemma at 10 cm/s | 38 µm, 2.6×10⁷, 27 kHz |
| RT8 C1 (POV pupil stacking 2.7–9.1× at 1550) | **0.05–0.18×** the 1310 nm AEL: resolved |
| RT9 C2 (FLOW-R2 probe) | the eye case becomes 0.21×; skin at the exit 9.4× (was 24×) |

**What it does not change:**
- **Addressing (pillar 4).** About 10⁷ modes per head at ≥ 4 kHz is still ~10–20× beyond a TI PLM (1.3 Mpx at 1.44 kHz) or a 4K LCoS (8.8 Mpx at ≤ 240 Hz). It is ~4–10× beyond DMD binary holography after its SBP and efficiency losses.
- **The visible engine.**
- **Motes.** The IR absorber must move to 1.3 µm: heavily doped ITO or Cs_xWO₃ nanocrystals (visible-transparent, strong NIR absorption) [ESTIMATE].

**Sources at 1.3 µm** (O-band telecom and DPSS) [ESTIMATE, to check]:
- 1310 nm DFB/FP diodes;
- O-band SOAs and PDFAs;
- 1342 nm Nd:YVO₄.

**Net.** The O-band is a genuine ×10 lever on the binding safety rule and removes the eye-stacking failures. It narrows the tetralemma's addressing gap from ~100× to ~10×. It does not close it.

---

## 3. Air-carried routes

### 3.1 FLOW-X as briefed: fails at home (opus §1)

- **Targeting fails.** A home column has an effective Tu of 0.5–1 %, so σ_x is 5–10 mm over 1 m and p_hit is 0.04–0.08. Targeted supply then equals a uniform rain.
- **No 2D injector.** No commodity 2D on-demand injector exists.
- **Inkjet heat.** Inkjet streams carry 11.8 W of evaporative cooling (re-derived here: 30 pL × 2.45 MJ/kg × 1.6×10⁵/s).
- **Content lag:** 1.2–5 s.
- **Corrections to m20:** the visible engine was overcounted by 16–50× (white sparse motes allow w_v 80–140 µm), and room particles were too high because floor settling was left out.

### 3.2 AIR-SV and E-AIR-SV: enclosed sculpture only

**AIR-SV fails in open rooms** (opus §2, m21b):
- cross-drafts must stay ≤ 8–21 mm/s;
- hand plumes are 10–400× the trim authority;
- vertical-stroke wakes need 1.6 mW per focus, above the skin cap;
- K = 1000 kicks overheat the bead surface;
- content moves at 22 s per 10 cm.

**E-AIR-SV** (m22 §G, this round): a static per-bead charge set at injection, plus a weak global field.
- **Static wake fix.** The wake deficits (−4.7 to −17 mm/s on the armor) and the size spread are compensated with E_v = 76–231 V/m at 30 % of the Peek charge. Charge use is p50 0.5, max 0.9.
- **Cross-drafts.** Common-mode cross-drafts of 1–5 cm/s need E_h = 100–580 V/m.
- **What it does not fix:**
  - **Grounded hand.** A grounded hand in that field perturbs beads at **9–31 mm/s at 10 cm** and 2–7 mm/s at 20 cm (monopole-dominated). An actively driven glove would remove the monopole term.
  - **Differential drafts** (§2.2).
  - **Content speed.**
  - **Charge leakage.** τ ≈ 0.3–1 h even in ion-depleted column air.
- **Verdict:** a better enclosed sculpture, not the vision.

### 3.3 FLOW-R (opus): the uniform gated rain

**What it is:**
- An untargeted rain of 10–14 µm-diameter white motes in a guarded 0.25 m/s downward column.
- The column runs from a hood above to an inlet below.
- Each mote is lit only while it crosses the content.
- Visible light only, Class 1 per beam.

**What it gains:**
- one-frame content latency, so any content speed;
- the image survives hand wakes, because mixing a uniform concentration leaves it uniform;
- insensitivity to Tu and common-mode drafts.

**Opus's wall:** 3D tracking at 0.5 particles per pixel at room scale. Hence a desk scale (0.2 m image, ~$5–12k).

**Rule-12 re-derivations** (all agree):
- 30 pL → 38.5 µm drop → 10.3 µm mote at 3 % solids;
- d²-law drying 0.86 s;
- Lambert phase function p(90°) = 0.764 at ω 0.9 (m23 self-test: 4π average = 1.0000);
- in-column mass 34 mg/m³ at n 1.6×10⁷ /m³, a = 7 µm;
- column optical depth 0.15 % at 0.3 m;
- per-beam power 0.36 mW at w_v 80 µm for 1.5 cd/m² at 520 nm;
- crossing rate n·U·δ·d_s = 20 /s per 5 mm sample.

**Corrections:**
1. **No mannitol.** Inhaled mannitol powder is the Aridol bronchial challenge agent: asthmatics react at cumulative doses of tens to hundreds of mg. A face inside the column at 35–56 mg/m³ inhales ~20–30 mg per hour. Use **lactose** (the standard dry-powder-inhaler excipient) or trehalose, and keep faces out of the column.
2. **Food grade is not inhalation grade.** Inside the column the concentration is 35–56 mg/m³, above the 10 mg/m³ inhalable nuisance-dust limit (ACGIH). That is acceptable only for brief exposures, with the face outside the column.
3. **Vertical strokes** (see §3.4).

### 3.4 FLOW-R2: crossed-probe gating replaces tracking (m23, this round)

**Principle** [DERIVED]:
- **Probe head B.** An 850 nm DLP projector, stopped down to pencil beams (w_p 0.35 mm, z_R 0.45 m), sends one pencil through P_k⁺, a point 6 mm above content sample P_k.
- **Cameras.** Cameras A, A′ and A″ (global shutter, ~1 kHz, IR band-pass) read only the pixels where P_k⁺ projects.
- **Detection.** A mote lit by *any* probe beam that shows in all cameras' pixels at once is at P_k⁺, because the lines of sight meet only there.
- **Firing.** The controller predicts the mote's arrival at P_k 23 ms later (lateral wander 0.6 mm at Tu 10 %) and fires a focused visible spot.

**Ghosts** (Monte Carlo on 1 026 armor samples, eps 0.5–1 mm; m23):
- A single camera sees 0.1–1.9 ghost beams per sample.
- Accidental two-camera coincidences add **≤ 0.6 %** of the true rate at a 2 ms window, and three cameras add ≤ 0.05 %.

**Signal:**
- 0.2 mW per pencil gives ~1.3×10⁴ photo-electrons per crossing through a 35 mm aperture at 1.6 m.
- Total probe power is 0.2 W, spread over ~1 000 diverging pencils; the eye case still needs checking in RT9.
- Each pencil also sees 3.7×10³ spurious crossings per second elsewhere along it. These are ignored by pixel ROI.

**Room-scale numbers** (0.8 m column, 0.6 m armor of 3.1 m strokes, 20 Hz, 3 mm sampling, 3 cd/m², a = 7 µm lactose):

| Quantity | Value |
|---|---|
| Rain | n 2.6×10⁷ /m³; **56 mg/m³** in the column; **34 g/h**; 576 m³/h of air |
| Optical depth across the column | 0.63 %: **11 % contrast against a dark wall at 10 lux**, 1 % in a 100 lux room |
| Room particles | 50 µg/m³ at 99.9 % capture (500 at 99 %), with settling. **Needs ≥ 99.9–99.97 %** |
| Dropouts | 13.5 % of samples dark in a given 0.1 s (N_s 1); 1.8 % at N_s 2, at twice the mass |
| Vertical strokes | **33 % coverage per 50 ms** (flowing dashes); 67 % with a 2 mm tolerance. **59 % of the armor's strokes are within 30° of vertical** |
| Visible | 1.33 mW for a 3.9 ms flash at w_v 140 µm (5.2 µJ, half the single-pulse AEL); 0.44 mW at w_v 80 µm. Needs a scan-fail cut |
| Spot engine | **79 simultaneous spots** (21 with 1 ms flashes, at 1.3× the single-pulse AEL, which fails) |
| Ghost dots | 19 % at w_v 140 µm (other motes within ±z_R = 12 cm); **2 % at w_v 80 µm** (z_R 3.9 cm) |
| Engine size at w_v 80 µm | 1.0×10⁷ modes per head, or galvo channels in depth bands of 8 cm (~40–60 channels) |

**Lighter setting** (δ 5 mm, 1.5 cd/m²): 34 mg/m³, 20 g/h, 0.38 % optical depth, 48 simultaneous spots, vertical coverage 20 %.

**Desk** (0.3 m column, 1 m of strokes): 4.7 g/h, 7 µg/m³ in the room at 99.9 %, 26 spots, 4.7×10⁵ modes. That is FLOW-R's regime, now without tracking.

---

## 4. Nearest buildable variants against the vision

| Vision item | FLOW-R desk (opus) | **FLOW-R2 room** (this round) | E-AIR-SV enclosed |
|---|---|---|---|
| Open air, walk-around | ✓ | ✓ | ✗ (enclosure) |
| Not a table or wall | hood + pedestal | **ceiling unit + floor grille** | box |
| No gas or fog | sub-visible rain (0.15 %) | sub-visible rain (0.4–0.6 %); faint haze against dark walls | ✓ |
| Size | 0.2 m | **0.6 m** | 0.3–0.6 m |
| Interactivity | one frame | **one frame** | minutes |
| Touch | hand shadow 7–15 cm below | same | destroys content |
| Line quality | sparkly; vertical strokes dashed | same | solid, static |
| Brightness | 1.5–3 cd/m², dim room | same | similar |
| Safety | visible Class 1 per beam plus scan-fail; lactose | same, plus 99.9 % capture | IR trims |
| Cost class | $5–12k | **$30–60k** (visible engine $10–30k, cameras $3–6k, air $1–2k, probe $1k) [ESTIMATE] | $10–20k |

---

## 5. What stands between FLOW-R2 and "solved"

1. **Owner rulings:**
   - Is a sub-visible lactose rain (0.4–0.6 % optical depth, 34–56 mg/m³ in the column) "no gas or fog"?
   - Is a ceiling unit plus a floor grille "just a projector"?
2. **Rendering:**
   - Vertical strokes come out as flowing dashes, and 13.5 % of samples are dark in any 0.1 s.
   - An Iron-Man armor is 59 % near-vertical strokes.
   - Denser rain fixes this at a cost in mass and haze.
3. **Room-scale spot engine.** It is not home-priced.
4. **Measured capture** of ≥ 99.9 % with people moving around.

---

## 6. Open items for RT9

- **§2.8 tetralemma:** is any escape missing?
- **Crossed-probe gating:**
  - geometry;
  - camera timing;
  - eye exposure of the 0.2 W probe fan;
  - whether a mote at P_k⁺ always reaches P_k (wander, Tu, column deflection).
- **Visible flash Class 1 under EN 50689:**
  - repetitive-pulse rules;
  - scan-fail;
  - stacking at a pupil inside the column.
- **Rain rendering:** dropouts and vertical strokes.
- **Particles:** lactose safety, capture and haze.
- **m22 E** pump bound assumptions.
- **m22 G** hand-field estimate.

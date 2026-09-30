# Lab notebook: breakthrough-holo

Dated entries: hypothesis → test → result → decision. Newest at the bottom.

---

## 2026-09-30 · Entry 1: Lab opened

- Goal and grading rule fixed in `00_mission/GOAL.md` (R1–R10).
- Task list in `00_mission/TASKS.md`.
- Five parallel literature agents launched:
  - R0 workflow methods
  - R1 air-plasma displays
  - R2 particle, acoustic and haptic displays
  - R3 safety limits
  - R4 film target and display limits
- Starting line of attack (before reading the literature, from first principles): pin down exactly what free-space optics forbids. The owner's constraints (no screen, no fog, no glasses, visible all around, touchable) are very tight, and the first job is to find the physically allowed corner of design space, if there is one.

---

## 2026-09-30 · Entry 2: Theory, first kills, and the real bottleneck

**Theory (T1).**
- Line-of-sight theorem: in clean air, an image point can only be seen along a line of sight that ends on an emitter. A "projector through the air" covers ~0.14 % of 4π.
- Touch lemma: any surface-emitter display (wall, table, plate) is erased by a hand behind the image point.
- Conclusion: in-volume emission is *necessary*.

**E1/E2 (validated: Rayleigh cross-section matches Bucholtz 1995 to 0.04 %; ISO 9613 gives 1.32 dB/m at 40 kHz).** Mechanisms killed:
- Rayleigh (~2 MW per frame, and the glow can't be localised).
- Coherent nonlinear optics (side emission suppressed by 10⁻¹³ to 10⁻⁵¹).
- Incoherent nonlinear scattering (~5 photons per voxel).
- Microwave/THz breakdown (kW-scale RF).
- Acousto-optics (10° deflection needs 112 MHz sound, absorbed within 10 µm).

**Survivor:** laser-induced air plasma. The only grey-zone alternative is projector-supplied particles.

**E3 plasma model** (PPT ionisation plus inverse bremsstrahlung plus depletion). PPT for O₂ at 800 nm is within 2.6× of Couairon's multiphoton fit; the avalanche cross-section matches Couairon's 5.44×10⁻²⁰ cm²; the self-focusing threshold of 3.3 GW matches literature.
- Dense plasma (ne ≈ 2.5×10¹⁹ cm⁻³) forms at ~2–10 µJ with NA 0.1–0.3.
- Absorption is only 1–26 % for sub-ps pulses (the model lacks multiple ionisation, so this is a lower bound).

**Literature (R1): the decisive fact.** Luminous output of *cold* femtosecond plasma is ~10⁻⁵ lm/W (quenched N₂ bands in the UV-violet). *Hot* nanosecond sparks give ~1 lm/W (continuum; 22–34 % of absorbed energy radiated), but 50–80 % of the energy goes into a shock wave (noise), and they make ~10¹⁷ NO per J.

**Target (R4 film analysis).**
- Strokes ~25–180 cd/m² in a 50–150 lux lab.
- 10⁴–10⁵ points per frame; 10⁶–10⁸ voxels/s.
- ~90 % cyan.
- ≤ 35–40 dB(A).

**New framing (hypothesis H1).** For a pure-air display, brightness is capped by *air chemistry* (NO/O₃ per photon) and *noise* (shock energy per photon), not by laser power. Rough estimate:
- Iron Man brightness in a lit lab needs 6–60 lm.
- At ~1 lm/W that is 6–60 W absorbed, i.e. NO production that needs ~10³–10⁴ m³/h of scrubbing.
- Status: probably NOT MET by 10–1000×.

To test H1 quantitatively: E4 (luminous efficacy vs spark size), E5 (room chemistry), E6 (audible noise), E7 (laser safety). In parallel, run an idea round with other models to attack each bottleneck.

---

## 2026-09-30 · Entry 3: Budget model, safety, noise correction, colour, feasibility

**Budget model** (`display_budget.py`), calibrated against literature:
- A 50 mJ ns spark gives 2.1 lm/W (literature 0.7–6) and an acoustic peak at 55 kHz (literature 50–100 kHz).
- Micro-sparks (1–100 µJ) come out at 0.1–0.4 lm/W, because small kernels are quenched by expansion before they radiate.

**E5 air chemistry.**
- The near-field plume at a face 0.5 m away dominates the well-mixed room term.
- Without source capture, even 1 W absorbed gives 64 ppb.
- With a built-in push–pull capture airflow (90 %) and a 900 m³/h scrubber, ≤ 2–3 W absorbed stays ≤ 20 ppb.

**E7 laser safety at 1550 nm.**
- Single-pulse eye hazard zone: 4–16 mm around each focus (IEC-derived, conservative).
- Average exposure elsewhere: ≤ 10 mW/cm², against a 100 mW/cm² limit.
- Hand interlock (22 mm margin) blanks 1.3–4 % of the hologram.
- The plasma's own UV is safe by more than 100×.
- 2 µm is worse than 1550 nm (10× lower MPE).

**E6 / E6b acoustic phase scheduling (new idea).**
- Timing sparks so clicks arrive evenly at tracked ears cuts the DIRECT-field audible noise by 26 dB (sorted, 1 listener) and 35–40 dB (L-BFGS, up to 8 tracked listeners at once).
- Untracked positions are unchanged, and the random-order baseline reproduces the analytic Campbell floor within 0.4 dB.
- **Self-caught error:** I first applied the gain to the total level. Room reflections arrive scrambled, and the reverberant level follows *total radiated* audible power, which timing cannot reduce at 5–20 kHz (radiating modes ≫ free parameters).
- Corrected real-room benefit: 1–10 dB depending on room absorption.
- Path-order drawing is 6–10 dB *worse* (supersonic voxel strings make coherent Mach waves).

**E9 particle swarms (grey zone):** film-scale content needs 30–450 fast beads and 123–142 dB of room ultrasound (public limit 100 dB). Not safe; even a 1–5 bead colour accent gives 114–126 dB.

**E11 colour:** calibration passes to within 0.1 %. The air-plasma palette runs violet → blue-white → white → greenish-white, plus a dim red-pink (H-α and O I in humid air). Film cyan (0.206, 0.262) and orange are outside the gamut.

**E10 feasibility** (Monte Carlo over literature bands; engineered air handling; SAFE means ≤ 50 ppb, ≤ 85 dB(A) and ultrasound ≤ 100 dB):

| Target | P(safe) | Noise | Air |
|---|---|---|---|
| Film-exact, lit lab (50 cd/m², 30k points) | 0.09 | 79 dB(A) | 505 ppb |
| Film density, dim lab (10 cd/m², 10k points) | 0.64 | 64 dB(A) | at the 50 ppb limit |
| **Iron Man style, dim lab (3 cd/m², 5k points)** | **0.95** | 53 dB(A) | 10 ppb |

Quiet (≤ 45 dB(A)) holds only for sparse content or treated rooms.

**Key perceptual point:** in a dim lab (0.5 cd/m² background), 3–4 cd/m² strokes have the film's own contrast ratio (4.5–12× background). The eye adapts, so the film *look* is reproduced in a dark room, just not the absolute brightness of a lit room.

**Decision:** the pure-air plasma engine is the design line. Film-exact quality (lit room, cyan/orange) is graded NOT MET by physics. Still pending: the idea round (3 models) and the red team.

---

## 2026-09-30 · Entry 4: Idea round (Opus) and the subsonic-tracing breakthrough

**Independent convergence.** The Opus idea-round reviewer and I both reached "draw like a subsonic pen" as the #1 noise lever, independently.

**E6c** confirms it. K parallel beam channels each trace their strokes with regular 40 kHz clicks at trace Mach 0.22–0.35. This cuts **TOTAL radiated audible power by 19.5–26.5 dB in all 96 far-field directions** (worst direction −14.5 to −19.5 dB), so reverberation is reduced too. A supersonic single path is +7.6 dB (Mach-wave booms). Physics: a steady source moving slower than sound radiates no audio except at ends, jumps and turns.

**Corrections adopted from the review.**
1. **Heat-release noise model** (the permanent expansion ΔV of each spark sets the audible floor). It agrees with my shock-wave N-wave model within 0.2 dB, and with the reviewer's closed form within ~6 dB (theirs is free-field only). Noise estimates are robust.
2. **Strict air criterion:** ≤ 13 ppb (WHO 2021 24-h NO₂ = 25 µg/m³, assuming worst-case all NOx ends as NO₂); lenient 50 ppb. Speciation (NO vs NO₂ vs O₃) is unmeasured (experiment X2).
3. **Colour:** checked the reviewer's "warm room makes it cyan" claim.
   - The simple dominant-wavelength-vs-adapting-white method gives 483 nm, purity 0.42 (film cyan: 484 nm, 0.45).
   - A proper Bradford chromatic-adaptation model gives **hue 202–213° (azure), against the film's 181–199°**.
   - So: a blue/near-cyan look, not an exact match. The optimistic method was rejected.
4. **Budget by stroke length × luminance** (not point count). A life-size armor outline alone is ~15 m of stroke.
   - `holo_engine/content.fit_to_budget` now selects strokes by priority to fit the chemistry budget.
   - Demo: 9 m of strokes at 4 cd/m² (film contrast in a 0.5 cd/m² dim room) → 3.1 W absorbed, 22.6 ppb, 44 dB(A).

**E10 (updated: subsonic tracing −15 dB worst-direction, heat-release noise, strict air):**

| Target | Air | Noise | P(safe, ≤ 50 ppb) | P(safe, ≤ 13 ppb) |
|---|---|---|---|---|
| Iron-Man style, dim (3 cd/m², 5 m of strokes) | 10 ppb | 40 dB(A) | 0.96 | 0.75 |
| Film contrast, dim (4 cd/m², 9 m) | 22.5 ppb | 44 dB(A) | 0.82 | 0.58 |
| Film density, dim (10 cd/m², 10 m) | — | 50 dB(A) | 0.64 | 0.30 |
| Film-exact lit lab | — | — | 0.11 | 0.01 |

---

## 2026-09-30 · Entry 5: Idea round (Sonnet) and the chemistry-speciation lever

**Sonnet idea round.**
- Same overall verdict: film-exact is impossible; the closest option is a dim-room sparse plasma display.
- It judged noise unrecoverable ("35–45 dB over") because it lacked subsonic tracing (E6c recovers 15–26 dB in all directions).
- Its grey-zone pick is a levitated-bead tabletop display; E9 shows 114–142 dB of room ultrasound, so it was rejected.
- Its nanoparticle-aerosol idea is recorded in T3.

**E5b speciation lever** (from both reviewers). Indoor NO converts to NO₂ only by reacting with O₃, which the projector's MnO₂ stage scrubs. Kinetic box model (k(NO+O₃) = 1.9×10⁻¹⁴ cm³/s, 40 ppb outdoor O₃), limits NO₂ ≤ 13 ppb, O₃ ≤ 20 ppb and NO ≤ 300 ppb:

| Products | Allowed absorbed power |
|---|---|
| All NO₂ | 1.75 W |
| Cold-filament-like (70 % O₃) | 4.0 W (×2.3) |
| Mixed | 7.7 W (×4.4) |
| Hot-spark-like (90 % NO) | 21.5 W (×12.3) |

**Consequence (E10 speciation-aware Monte Carlo, K = 24 subsonic tracing, −19.5 dB):** film stroke density at film contrast in a dim lab (4 cd/m²):

| Strokes | P(safe) | P(safe and ≤ 50 dB(A)) |
|---|---|---|
| 15 m | 0.81 | 0.66 |
| 30 m | 0.64 | 0.48 |
| 57 m | 0.45 | 0.31 |

Film *density* in a dim lab is therefore plausible, and the product tier is decided by two bench measurements: X1 (lm per J) and X2 (NO/NO₂/O₃ speciation per J). A lit-room film match stays out of reach.

---

## 2026-09-30 · Entry 6: Owner rules; Fable idea round; double-validation of agent claims

**Owner (mid-run):** check for existing runs before simulating; double-validate every result, mine or an agent's. Now protocol rules 11–12 in WORKFLOW.md.

**Fable idea round.** Same verdict as Opus and Sonnet: film-exact is impossible in air; the closest is "Fairy Lights at 100× scale in a dim lab". It independently arrived at the constant-flux, subsonic, never-blank drawing rule (the same as E6c) and warm-room cyan. Its two no-go scalings reinforce T2:
- No bright and chemically cold air plasma exists (radiative branching ∝ ionisation fraction).
- A quiet isobaric kernel radiates ≥ 10 % only above r ≈ 3 mm.

**Double-validation of its claims:**

1. **Regulatory: CONFIRMED** (search snippets from UL, BSI, ANSI blog, iTeh; standard text not purchased).
   - EN 50689:2021 allows consumer laser products only in Class 1, Class 2 and a restricted part of Class 3R. Class 1C (engineering controls protect the eyes) is limited to skin-contact devices and is excluded from EN 50689.
   - So an open-air, presence-sensed plasma projector has **no consumer/home certification route today**. The route is professional or venue products under variance, which ROADMAP phase 2 already assumed.
   - This lowers R10 (sellable to homes) and qualifies R8 ("everyday use" = supervised venues until a new product category exists).
2. **Chemistry "10–30 lm with a downdraft hood": arithmetic checks, model incomplete.** The room-balance term is 18 ppb as claimed, but it omits the near-field plume. The same 10 % leak gives ~127 ppb at a face 0.5 m away unless the downdraft reliably carries it away from faces (experiment X5). It also assumes ~1 lm/W for 10 µJ kernels, against the lab's 0.1–0.4 (Opus and Sonnet both agree with the lab). **Not adopted.** The lab's E10/E5b numbers stand.
3. **Ultrasound from the regular click comb: CHECKED, benign.** The 40 kHz comb line from heat-release pulses is ~59.6 dB per channel at 1 m, ~70 dB for 12 channels, against a 100 dB public limit.
   - Parametric self-demodulation of MHz blast ultrasound is negligible: it is absorbed at 42–160 dB/m, so it has only a few cm of interaction length. This is an order-of-magnitude estimate, not simulated.
4. **Ar II 488/496 nm lines** (air is 0.93 % Ar) as a cyan contribution: plausible but unquantified. Left for X1 spectroscopy.

---

## 2026-09-30 · Entry 7: Red team, independent validation, regrade (v1 over-graded)

The red team found 3 critical, 11 major and 5 minor problems (`05_reviews/red_team_1.md`). Per owner rule 12, I re-checked before adopting:

| # | Claim | My check | Verdict |
|---|---|---|---|
| 16 | AOD scanner violates étendue ~250×/axis | N_AOD = τΔf ≈ 500; need F/(2w₀) ≈ 10⁵ at NA 0.1, F = 1 m | **Confirmed** |
| 11 | 22.5 mm margin allows 2× MPE at NA 0.09 / 40 µJ | 2E/(π(NA·d)²) = 6.2 J/m² vs 3 J/m² | **Confirmed** |
| 13 | UV margin is 1–11×, not > 100× | E7b band-resolved ICNIRP S(λ): N₂ bands 1.9–5.3×; hot continuum 0.1–0.4× (dose over the limit) | **Confirmed, worse** |
| 7 | Subsonic gain is content-dependent (UI −6 dB) | Independent UI-glyph content, my code: −6.1 dB (random control −0.1 dB) | **Confirmed** |
| 14 | Class 4; no consumer class; SIL 2 too low | Entry 6 web check (EN 50689 classes 1/2/restricted 3R; 1C only for skin contact) | **Confirmed** |
| 3 | Efficacy calibration is circular | R1 gap G2: no measured lm/W for laser sparks | **Confirmed** (my calibration was estimate-on-estimate) |
| 9 | 90 % capture implausible from a ceiling sink | Sink velocity Q/(2πx²) = 0.04 m/s at 1 m < room drafts | **Confirmed** |
| 8 | Fan noise missing; wrong limit and distance | 900 m³/h through media beds ≈ purifier max 55–65 dB(A) | **Accepted** (estimate) |
| 10 | Speciation likely O₃-rich; ×12 fragile | ns quench vs µs–ms Zeldovich; VUV photolysis | **Accepted** (physics argument; X7 decides) |
| 6 | Listener locking fragile (ear ±5 mm, jitter, reflections) | Consistent with my own Entry 3 correction | **Accepted** |
| 4, 12, 15, 17, 18 | Absorption, object hazards, transmitted power, source availability, colour adaptation | Consistent with lab data (E3) and physics | **Accepted** |

**E10b (red-team-corrected Monte Carlo):**
- Efficacy 0.01–1 lm/W.
- Capture 0.3–0.9.
- Speciation ×1–2.3.
- UV constraint added.
- Noise at 0.4 m, including the fan, with content-dependent gain.

| Target | P(home-safe) | P(venue-safe) |
|---|---|---|
| Sparse accents (1 m) | 0 | 0.71 |
| Sketch (5 m) | 0 | 0.36 |
| Film contrast (9 m) | 0 | 0.21 |
| Film density (30 m) | 0 | 0.08 |
| Film-exact | 0 | 0 |

**E12 étendue budget:** AOD random access cannot address a room. A galvo-tiled redesign (4 heads, 30–50 mm mirrors, NA ≈ 0.03, 100–160 µJ per voxel) is consistent on paper, but hazard zones grow ~1/NA.

**Regrade:** 4 MET / 4 PARTIAL / 2 NOT MET (R8 safety, R10 buildability). Not solved; no ping. FINAL_VERDICT rewritten as v2.

**Lesson for the protocol:** my v1 engineering claims were graded before an adversarial review. Next time the red team runs *before* any verdict draft is written.

---

## 2026-09-30 · Entry 8: Owner question: "how about multiple projectors?"

**Rule 11 check.** Multiple heads were already in the design (3 heads) and in E12 (tiling K = 1–25 for étendue). New question: does the number of projectors change the power, and so the chemistry, UV and noise budget?

**E13 result.**
1. **The incident laser power floor for a quiet, room-scale display is independent of K.** P_min = π I_th τ f_min F² / (4N²).
   - 22.5 W with 30 mm galvos; 14.7 W with 50 mm galvos.
   - Analytic and numeric agree exactly for K = 1–25. Only bigger scanner étendue N lowers it.
2. **More projectors do not change the absorbed power.** Sparks just above threshold absorb 0.2–3 % (E3 model) and are far too dim. Absorbed power is therefore set by the light wanted, P_abs = lumens/η. That is a per-room quantity, and chemistry, UV and the noise floor scale with it.
3. **Spreading the same light over more, smaller sparks is a trade, not a win.**
   - Heat-release noise ∝ P_abs·E_spark gives −3 dB per halving of spark energy.
   - The η model gives 0.154 → 0.134 → 0.117 lm/W for 5 → 2.5 → 1.25 µJ, so each halving costs +15 % absorbed power and hence more NO₂/UV. The binding constraint gets worse.

**What multiple projectors do help:**
- The étendue problem (E12).
- Hand and body shadowing (R7).
- The single-pulse hazard per beam: √E/NA, with higher NA per head.

**What they don't:** light per joule, air, UV, and Class 4. Every head is another open Class 4 beam.

**Other multi-projector variants (reasoning, not simulated):**
- **Surround the room with projectors aimed at eyes:** this is the light-field room. It fails the touch lemma (a hand erases the hologram in front of it) and it is a screen room (R3/R4).
- **Crossed beams from two projectors** (spark only where they cross, each beam at ~½ threshold intensity, since ionisation ∝ I⁸):
  - Gains: sharper voxels at low NA, and each beam's hazard zone ×0.7.
  - Costs: the same light per joule; ps-level timing (~0.1 mm path match) across metres; two clear paths per voxel.
  - Worth a resolution bench test (add to X-series); it does not change the verdict.

**Scorecard unchanged: 4 MET / 4 PARTIAL / 2 NOT MET.**

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
   - The η model gives 0.139 → 0.111 → 0.090 lm/W for 5 → 2.5 → 1.25 µJ absorbed, so each halving costs +23–25 % absorbed power and hence more NO₂/UV. The binding constraint gets worse. (A first draft of this entry quoted 0.154/0.134/0.117 before the check ran; corrected.)

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

---

## 2026-09-30 · Entry 9: Buehler fact-check → workflow v2 → building the SPARK instrument

**Fact-check** (`06_buehler_factcheck/FACTCHECK.md`; primary source github.com/lamm-mit/graphene-agent, README lines verified by me).
- The underlying work is real and unusually transparent: Claude Fable 5.1 built and validated a REBO2 atomistic instrument, with 20 tests and hashed predictions.
- The post overstates it:
  - "first-principles / quantum ground truth" is really an empirical classical potential;
  - "multiple days" was 30 h autonomous;
  - "far better material" contradicts "no claim is made about real materials";
  - the "25 % stronger" figure contradicts the repo's own headline, "Hierarchy is not a free lunch".
- 10⁻¹³ eV/atom proves code correctness, not physics. We adopt the workflow (`WORKFLOW_v2.md`) and require physics tests as well as code tests.

**Why an instrument.** The verdict's decisive unknowns are the spark's light per joule (η, ±30×), reactive molecules per joule, UV and noise. They were literature guesses. SPARK computes them from physics:
- `eos.py`: Cantera airNASA9 equilibrium below 18 kK plus my own Saha solver for N/O up to 3+ ions (to 300 kK). The two agree within 2.4 % in their 14–18 kK overlap.
- `radiation.py`: Kramers–Unsöld continuum, 24 N/O line multiplets, escape factors.
- `hydro.py`: 1D Lagrangian spherical hydro with artificial viscosity, implicit conduction and radiative loss, plus an isobaric late phase.
- `chemistry.py`: Zeldovich/ozone/NO₂ kinetics with detailed balance on NASA thermo, and VUV/EUV photochemistry.

**Validation so far (11/12 fast tests pass; 8 pending on long runs):**
- Sod shock tube L1 error 0.23 %.
- Sedov ξ₀ = 1.0356 against 1.0328 (**P1 PASS**).
- Energy conservation 7×10⁻⁵ (Sod) and 5.5×10⁻³ (Sedov).
- Kinetics reach Cantera equilibrium within 0.8 %.
- O-atom lifetime exact (13.26 µs).
- Photometry 679.6 lm for 1 W at 555 nm (0.5 %).

**Errors caught.**
- (a) My kinetics first assumed a fixed molecule count; dissociation broke equilibrium by 20–33 %. Fixed with a per-parent-molecule basis.
- (b) V08 first "failed" at 3400 % because the test let heat diffuse past the domain edge; the solver itself is fine (0.35 %, converging).
- (c) The first "residual heat" number double-counted the outgoing sound wave. Replaced with a probe-bounded closure: 99.6 %.

**V12 derivation (escape factor, thick limit).**
- In the optically thick limit, β = 1/τ with τ = κR.
- The loss is then j·(4/3)πR³/(κR) with j = 4πκB, giving (16π²/3)R²B.
- A blackbody surface loses 4π²R²B, so the ratio is 4/3.
- The approximation over-predicts thick emission by 33 %. Micro-kernels are thin in the visible, so this bites only in the VUV.

**First physics result: 10 µJ micro-spark in a 10 µm kernel.**

| Quantity | Result |
|---|---|
| Radiated | 0.53 % (P3 ✓) |
| η | 0.085 lm/W (P4 ✓) |
| Blast energy (Sedov fit) | 52 % (P8 ✓ under the literature definition) |
| Far-field sound | only 3.9 % |
| NO | 1.1×10¹⁶ /J |
| O₃ | 2.6×10¹⁵ /J, mostly from VUV photolysis |
| NO₂ | 1.8×10¹⁴ /J |
| All reactive species | 1.4×10¹⁶ /J (3.5× below the display budget's nominal) |

**Analytic law from the SPARK tables.** For isochoric deposition, visible light per joule ≈ lm(ρ₀,T)·(r₀/c_s)/ε, which peaks at 40–60 kK. It gives η ≈ 5.5×10³ lm W⁻¹ m⁻¹ × r₀: efficiency is proportional to spark radius. That is a resolution–efficiency trade-off, and fine strokes force small, inefficient sparks (registered as P10).

---

## 2026-09-30 · Entry 10: Red team 2 on SPARK; fixes; v1 results withdrawn

Independent review (`05_reviews/red_team_2_spark.md`): 4 critical, 10 major, 8 minor findings. I re-checked the critical ones (rule 12) before adopting them.

1. **NO chemistry artefact — CONFIRMED by my own test.** Starting cells from ambient air clamped at 6000 K inflates frozen NO 9–180× against starting from the LTE composition. Held at 6000 K from ambient, NO overshoots to 11 % (14× equilibrium).
   - **All v1 NO/NO₂/O₃/"reactive per J" numbers are withdrawn**, including the "3.5× below the display budget" I reported to the owner.
   - Fix: LTE start below 7000 K, no clamp, Kossyi O+O+M, 5× atom third-body efficiency, and a high-T O₃ decomposition rate.
   - New test V21: frozen NO ≤ the maximum equilibrium value. Frozen NO is now 2×10⁻³ to 1.4×10⁻² per air molecule.
2. **VUV lines were dropped as "trapped" — CONFIRMED.** The rebuilt tables show thin VUV-line emission 10–20× the rest.
   - 9 N/O VUV lines added (NIST-type data, flagged ±3×), with Voigt escape (tabulated β(τ₀, a); Stark width 0.01 nm at 10²³ m⁻³, ×0.3–3).
   - Their photons feed O₂ photolysis, making O₃.
3. **Late cooling had no vortex mixing — CONFIRMED against data** (200 mJ at 21 µs: 15.0 kK vs 6.9 kK measured).
   - Added an entrainment model: onset 0.35 r_c/c₀, time constant 0.10 r_c/c₀, calibrated on the 200 mJ data (so V18 is now a calibration, not a test).
   - Independent check: V23 (75 mJ at 10 µs vs Dumitrache).
   - For micro-sparks (low Reynolds number) mixing is uncertain, so it is run as an on/off bracket.
4. **Validation state was over-reported — CONFIRMED.**
   - V12 was hard-coded; it is now a real test.
   - V16 (monopole law) FAILS in the reference run with a ratio of 1.85: the display budget's noise model is ~3–5 dB optimistic.
   - V17a and V18 failed on v1 runs. All results are now published as they are.

**Other fixes:**
- Kirchhoff κ extra-factor bug.
- EOS extended to N⁶⁺/O⁷⁺ and 1 MK, with a loud error when out of range (was a silent clamp).
- Molecular bands (N₂ 1+/2+, N₂⁺ 1−, NO γ/β).
- Actinic S(λ) from 180 nm.
- Cylindrical geometry, to bracket elongated foci (sphere vs line).
- Noh implosion test (V22: 61 vs 64) for converging-shock cases.

**Not claimable from SPARK (red team 2 list, adopted):**
- The "~50 % blast share": the Sedov estimator returns ~0.5 by construction for real-gas Γ.
- Any ε ≥ 10⁹ J/m³ result, until the EOS extension is re-validated.
- Absolute micro-spark η better than about ×3, given the Biberman factor, conductivity table and geometry.

v1 runs are archived in `results/v1_superseded/`.

---

## 2026-09-30 · Entry 11: Atlas complete; E10c re-grade; the lumen-locked pollution law

**Atlas (40 formats, SPARK v2).**

| Finding | Detail | Prediction |
|---|---|---|
| η rises with spark size at fixed deposition density | ε = 10⁹: 0.034 lm/W at 1 µJ → 0.39 at 1 mJ | P5 ✓ |
| Coefficient below prediction | η/r₀ ≈ 2×10³ lm W⁻¹ m⁻¹, 2.5× under my estimate | P10 ✗ |
| Double pulse loses light | 0.15–0.73× single; the reheated kernel is dilute | P9 ✗, P12 ✓ |
| Shell implosion | Stalled numerically | P13 inconclusive |
| Line focus | η ×3, same UV and chemistry per lumen | — |
| Mixing | No effect on micro-spark light; −20–25 % NO | — |

Operational note: the shell runs hung for 2 h on 4 cores (time step collapsed at the converging shock). I added a wall-clock cap with a `completed` flag. My first `pkill -f atlas.py` killed its own shell, because the command line contained the pattern; I redid it safely.

**E10c: feasibility with SPARK numbers** (model-form bands η ×3, reactive ×3, UV ×(0.5–3); noise +5.4 dB from the V16 fail):

| Target | P(home) | P(venue) |
|---|---|---|
| Sparse accents | 0 | 0.69–0.73 |
| 5 m sketch | 0 | 0.15–0.23 |
| Film contrast (9 m) | 0 | 0.03–0.05 |
| Film density | 0 | 0 |
| Film exact | 0 | 0 |

For the sketch, the binding constraints are air (80 % of draws fail), noise (76 %) and O₃ (37 %).

**Lumen-locked pollution law (T4).** UV and reactive gases per lumen are fixed by the plasma's spectral shape and VUV lines, not by spark design.
- The UV cap alone limits a continuous display to Φ ≤ 1 lm with the user at 0.4 m. Film density needs 1.5 lm; the film itself needs 19 lm.
- Registered as P14 for the bench.

---

## 2026-09-30 · Entry 12: Red team 3 on T4 and E10c: the "law" is withdrawn

Red team 3 (`05_reviews/red_team_3_T4.md`): 3 critical, 9 major, 7 minor. It reproduced the atlas and E10c exactly. I re-checked its key claims (rule 12):

1. **"UV per lumen invariant" is a property of my continuum model — CONFIRMED.** The emission table alone gives act/lm 1.1–2.2×10⁻³ over 9–40 kK and 0.01–1.17 kg/m³, so the hydro can't change it. Model-form range ×0.3–2.
2. **The ad hoc EUV rule supplies 30–54 % of reactive per lumen — CONFIRMED** (29–67 % of NO) across the atlas.
3. **The UV cap "Φ ≤ 1 lm whatever the air handling" held only for a viewer at 0.4 m for 8 h/day** (arithmetic confirmed). At 1.5 m, 2 h/day the cap is ~51–62 lm, so UV does not bind at normal distances.
4. **E10c does not implement lumen locking** (η, yields and UV were sampled independently), and **its P(home) = 0 is driven by noise:** the 48 dB(A) fan alone exceeds 35 dB(A). Venue probability for the sketch ranges 0–0.64 across defensible variants:
   - 0 without the untested subsonic-tracing gain;
   - 0.40 with capture fixed at 0.9;
   - 0.64 for realistic viewing with hazard-consistent air metrics.
5. **The +5.4 dB noise correction partly double-counts** (+0.1 to +7.1 dB by format; +2.5 dB for the most-used format). V16 is ill-conditioned (probe record cut ~3 µs after arrival).
6. **All light, UV and VUV come out within ~50 ns**, at high density and 20–40 kK: exactly where the untested instantaneous-LTE deposition assumption rules.

**Actions:**
- T4 rewritten as "SPARK per-lumen scaling (model result; hypothesis P14b)", with scenario tables.
- P14 declared violated as posed; P14b registered for the bench.
- The verdict is re-worded (v3): home is ruled out by spark noise and regulation; venue feasibility is an open question the bench must settle; UV binds only for lamp-standard certification at 0.2 m.

**Lesson (workflow).** Calling a model regularity a "law" before checking whether it is baked into an input table was an overclaim. New sub-rule for rule 5: before claiming an invariant, test it on the input tables alone.

---

## 2026-09-30 · Entry 13: Owner: "no giving up". Phase 3 opens: the MOTE route

**Why this route.** T1 leaves exactly two doors: light made at the point by air plasma, or by matter at the point. Plasma was pushed to its limit (Entries 9–12). Its walls (ozone, UV, noise, low lm/W) all come from making light by *burning air*. The matter door was only screened, with acoustic beads (E9: ultrasound too loud) and violet optical traps (T3: Class 4).

The new combination has not been analysed in the literature I know. The projector dispenses and holds its own microscopic motes:
- **trap:** infrared photophoretic traps (the BYU optical-trap display physics, scaled);
- **light:** the motes emit visible light themselves by upconversion, pumped by the trapping or a co-aligned IR beam, so no visible laser beams cross the room.

**First-principles scaling** (continuum photophoresis; Stokes drag; J₁ = 0.5; k_p = 0.2 W/m/K):
- v_max ≈ 7.4×10⁻⁸ m/s per W/m² of intensity, independent of mote radius: 0.74 m/s at 1 kW/cm², 2.2 m/s at 3 kW/cm².
- Mean mote heating ΔT ≈ 16 K per (µm radius × kW/cm²): 5 µm motes run ~150 K hot at 1 kW/cm², 10 µm motes ~310 K.
- **Light budget** (Φ = 4π L w S; N = S f / v): at ~60 lm per absorbed W (green upconversion), a 5 m sketch needs ~0.02 mW per mote, and **film-exact (lit lab)** needs ~0.35 mW per mote × 900 motes, about 0.3 W absorbed. Plasma needed 50–1000 W with ozone, UV and noise.
- A 5 µm mote lost to a draft settles at ~1 mm/s. 1000 lost per hour is ~0.3 µg/h, negligible next to room dust.

**New binding questions** (for a MOTE instrument, predictions P15–P21):
- the heating vs upconversion thermal-quenching trade;
- trace speed and mote count;
- robustness to drafts and hand wakes;
- étendue and optics for hundreds to thousands of traps;
- per-beam laser class. At 1550 nm the Class 1 CW limit is ~10 mW, which could make each beam Class 1: a consumer route that plasma never had.

Research agents launched: R5 (optical-trap display state of the art), R6 (emitter materials), R7 (CW-IR and particle safety).

## 2026-09-30 · Entry 14: MOTE instrument v1, atlas, feedback and the steering wall

**What R5–R7 changed.**
- **Room throw widens the trap.** A 1.5 m throw makes the focus much wider than a mote (w ≈ 6–19 µm at 1550 nm). So a single-head gradient trap wastes most of its heat.
- **Consumer rules mean Class 1.** US and EU consumer IR displays must be Class 1: 10 mW per beam at 1550 nm, 39 µW at 405 nm.
- **Emitter choice.** Upconversion works (~74 lm/W absorbed) but absorbs weakly. Incandescent motes burn.

**New physics, derived and validated** (T5; `validate_mote.py` 26/26):
- **Heat-force identity.** The force per kelvin of mean mote heating does not depend on radius: 9.5×10⁻¹² N/K at k_p = 0.02. **Heat, not laser power, limits speed.**
- **Speed law.** v_max ∝ ΔT/(a (k_p + 2k_g) h).
- **Lateral law.** F_x/F_z = (3/8) g a, which gives η_lat = 0.75 a/w.
- **Push-trap allocation factors.** Tetrahedral heads: 1–3; octahedral: 1–√3.
- **Focus law.** P_beam · B_focus ≥ I λ v k/2π.
- **BYU consistency.** The model reproduces BYU's 1.83 m/s record with 160–400 K of heating. That implies BYU's single-beam trap reaches η ≳ 0.4.

**Atlas M1** (576 designs × 5 targets; best by channel count). Design: push4, a = 1 µm, k_p = 0.02, 300 mm heads, cyan phosphor with a 405 nm pump.
- **Film density** (4 cd/m², 30 m of strokes): 1 131 motes, 4 524 channels, 1.8 W of 1550 nm. Class 1 per beam (0.87 mW) and at every exit window; 36 µW pump per beam against the 39 µW limit; mote ΔT = 149 K.
- **Sketch:** 188 motes, 754 channels.
- **Accent:** 38 motes, 151 channels.
- **Film-exact in a lit lab:** only upconversion motes with push6, needing 32 k channels.
- **Scatter motes are dead.** I first missed forward diffraction, which lights the walls as much as the image; it was fixed in atlas v2.

**Feedback M2.** A push trap needs a ≥ 15–20 kHz loop at room gusts and ≤ 0.5 µm position sensing.
- An attempted disturbance observer made things worse by amplifying sensor noise. This is logged as a negative result.
- M2b adds the photophoretic force lag: the mote's internal thermal diffusion, τ_F ≈ 15 µs at a = 1 µm.

**Steering wall (M3).** Each channel needs:
- ~78 000 resolvable positions per axis over a 1 m field (more than a 30 mm galvo);
- 0.3–0.6 µrad pointing precision;
- 2–17 kHz focus tracking;
- 20 kHz control.

Each function exists in some device; thousands of integrated channels do not. **The binding problem has moved from physics to engineering.**

**My own bugs this entry** (all fixed before any result was used):
- **Budget.** The final force was not recomputed at the converged temperature (M25 caught it).
- **Dynamics.** An impulsive start lost every mote in the validation test; motes now start moving with the trap.
- **Feedback sim, time step.** A 12.5 µm step was larger than the trap.
- **Feedback sim, stale reference.** A stale plan reference in the beam re-centring was worse than no correction.
- **Shell.** `pkill -f` killed my own shell a second time. **Rule: kill by PID only.**

Predictions: 8 ✓, 3 partial, 1 inconclusive (RESULTS.md §5). Red team 4 is running. Verdict v4 waits for it.

## 2026-09-30 · Entry 15: Red team 4 lands; MOTE v2; the owner's room rig

**Red team 4 (MOTE): 3 critical, 11 major, 11 minor.** Per owner rule 12, I re-derived or recomputed every key claim before accepting it:
- **ρ(T_f) mixed with T₀:** a real bug, +25 % force. Now ρT = p/R.
- **C_ph:** my claimed range [1, 1.56] double-counted. Re-derivation F = 4π C_s μ² T₁/(ρT) shows the code's form is C_s = 9/8, and the same formula reproduces Epstein exactly (M27, M28). **C_ph ∈ [0.67, 1.04].**
- **Doughnut trap:** my linear law was wrong both ways. The exact integral (M29) matches RT4 to ±0.01.
- **J₁ = A/2:** needs absorption depth ≲ a/30. My straight-ray model (M30) matches RT4's ray trace.
- **"Impossible mote":** accepted. A low-k body cannot also be a dense absorber. New mote classes, by FOM = (J₁/A)/(k_eff + 2k_g):
  - engineered aerogel with an island NIR skin: 5.3;
  - core–shell (dense phosphor core, aerogel shell): 4.4;
  - plausible: 2.0;
  - dense: 0.4.
- **Feedback beam:** the 10 µm flat-top edge was unrealisable. Accepted. My R_ft 20–30 µm runs have realisable edges.
- **Safety:** accepted. Class 1 needs scheduler-enforced no-overlap plus a fault-shutdown design.

**Owner's direction: many discreet heads in the room.** M4 studied layouts:
- **Corners are bad.** A 4-corner layout has worst-case heat factor 16.5; 8 corners, 4.8.
- **What works:** heads directly above and below the image, plus a close ring. The **R12 "lab rig"** has worst 2.22, mean 1.33 and throws 1.2–2.3 m. It survives one blocked head in 99 % of cases.

**M5 corrected atlas: the hard truth.**
- **Normal room** (0.3 m/s drafts): nothing is feasible, not even a 1 m accent.
- **Designed lab** (quiet-air zone ≤ 0.15 m/s, 500 K phosphor, scheduled no-overlap, non-fluorescent surfaces), at 45 Hz with an engineered mote:

  | Target | Channels |
  |---|---|
  | Accent | 840–1 000 (passive pairs, no fast loop) |
  | Iron-Man sketch | 2 700–4 400 |
  | Film density | 9 100–15 100, with 33–85 W of 1550 nm |
  | Film-exact | ~40 000 |

- **Plausible motes:** 3–5× worse.

**Predictions rescored:** 2 ✓, 2 partial, 6 ✗, 2 inconclusive. My v1 "8 ✓" rested on my own bugs. That is why the red team exists.

**M22 (BYU consistency) now fails.** The corrected force needs 270–745 K for BYU's lateral 1.83 m/s. Either BYU's particle was low-k, or the continuum model under-predicts. **A measurement of force per absorbed watt on a real mote is now bench item 1 for the whole route.**

**Verdict v4.** Not solved. MOTE is the best route: silent, chemistry-free and Class-1-beamed. It is conditional on:
- a mote material nobody has made;
- a designed room;
- a 10³–10⁴-channel beam engine;
- a new safety argument.

Scorecard: 4 MET / 5 PARTIAL / 1 NOT MET, up from 4 / 4 / 2 in v3.

## 2026-09-30 · Entry 16: Owner asked "working?"; the mote becomes a recipe

**M6 (my own analysis).** How opaque must the engineered mote's absorber skin be? J₁/A ≥ 0.43 needs optical depth ≥ 2 at 1550 nm (≥ 86 % single pass), in a non-percolating skin of ≲ 0.1–0.2 a.

**R9 (materials search).** Two concrete recipes that clear the FOM gate on paper, both with a silica overcoat:
- aerogel body + Cs_xWO₃ island skin + Eu-nitride phosphor (FOM ≈ 5);
- core–shell with a BaSi₂O₂N₂:Eu core (FOM ≈ 4.1, bright).

Supporting findings:
- ITO is rejected on inhalation toxicity.
- QDs and dyes are rejected on temperature.
- Micron aerogel is makeable (spray-gel, d₅₀ ≈ 2.4 µm), but its conductivity at that size is unmeasured.

**Double-check of R9's calibration claim.** Lewittes 1982 at 30 Torr is "within 10 %" only for an assumed k_p = 0.3 and an unknown J₁, near the Kn ≈ 1 maximum. I downgrade it to order-of-magnitude consistency. There is still no absolute 1 atm micron force measurement, so bench item 1 is unchanged.

The route's first question is now concrete: make recipe A or B at 1–4 µm, then measure k_eff, skin optical depth, α₄₀₅ and force per absorbed watt.

## 2026-09-30 · Entry 17: Owner: "Validate and confirm"

**Three-layer validation.**
1. **Suite:** 31/32 pass. M22 (BYU consistency) fails honestly, as reported.
2. **Reproducibility:** four headline atlas rows re-run from the committed code give identical channel counts (837 / 2 656 / 9 121 / 13 134).
3. **Independent recipe check (M7).**
   - A new ray-march shell model passes its self-tests. A thin opaque shell gives 0.4996, and the whole-sphere case matches `physics.j1_over_A`, an independent implementation, to 3 decimals.
   - The first version of the M7 script had a bug: optically thick steps did not conserve energy. The self-test caught it, and the fix is an exact exp(−τ) difference.

**Result: not confirmed as written.**
- R9's recipe A used Cs_xWO₃ islands 0.2 µm thick on a 1.5 µm mote. R9's own shielding snippet implies α ≈ 1×10⁴ cm⁻¹, so the skin τ is only 0.1–0.6 and the FOM is 0.4–2.0. That fails.
- Recipe B with Cs_xWO₃ is marginal at best (3.1–3.9).
- Both pass only with an ITO-class plasmonic skin (FOM ≈ 5.0–5.3).
- R9's rejection of ITO rested on occupational toxicity. My exposure estimate for lost motes is ~ng/m³, ~10³× below the cited lowest-effect level, so ITO becomes a toxicology question rather than a veto.
- Recipe B's 60–90 % pump absorptance needs α₄₀₅ ≳ 4×10³ cm⁻¹, which is unverified.
- **This was a synthesis error in R9:** it said Cs_xWO₃ needs ~1 µm solid-equivalent, then used 0.2 µm. I had passed it on without checking; the owner's request caught it.

Verdict v4's mote condition is tightened to an ITO-class skin plus toxicology. The rest of verdict v4 is unchanged.

## 2026-10-01 · Entry 18: "Continue until the full vision is unlocked; I can build anything"

**M8, the floor with every known lever.** Levers: ITO skin, 600 K face, hot phosphor, a laminar zone with mean-flow feed-forward, 45 Hz, 12-head rig.
- Accents: 340–420 beams.
- Sketch: 1 500–1 800.
- Film density: 6 100–7 600.
- Film-exact (lit room): infeasible. The 405 nm pump's Class 1 limit caps brightness.

**This is the physics floor.** It is set by the heat-force identity: speed is limited by how hot a mote may run. The only levers left are measured materials and steering scale.

**Owner can build, so the critical path moves to the bench.** `08_bench/BENCH_PLAN.md` defines four staged experiments with decision gates:
- **B1 (photophoretic velocimetry, ~1–3 k$):** black spheres drifting in a uniform beam in a sealed cuvette. Gives force per absorbed W, so C_ph and the 1/(k_p + 2k_g) law. Predicted drifts: 0.2–10 mm/s at 10 W/cm².
- **B2:** the ITO-skin aerogel mote with an Er thermometer gives FOM directly.
- **B3:** passive doughnut pair at 1–1.5 m.
- **B4:** first glowing stroke.

`analyze_b1.py` is self-tested: it recovers a synthetic C_ph = 0.9 after background subtraction. The safety section comes first: Class 3B/4 lasers enclosed and interlocked; nanopowders sealed.

**Entry 18, addendum.**
- **M8b (owner rule 12).** An independent recomputation of the sketch floor point from physics primitives, without `budget2.design`, gives T_face 495 K and 1 850 channels, against M8's 488 K and 1 845.
- **M8c corrects my M8 "film-exact: none".** That result came from restricting a ≤ 2.5 µm and 2 pump beams per mote. With a = 2.5–4 µm and 4–6 pump beams per mote from different heads (each ≤ 39 µW), lit-room film-exact is feasible:
  - green (β-SiAlON) motes: ~6 100 trap beams;
  - cyan motes: ~10 500.
- 450/470 nm pumps fail on visible stray light; 405 nm stays.

## 2026-10-01 · Entry 19: Bench toolchain, touch physics, red team 5 launched

**Bench B1 toolchain.** A self-contained tracker (velocity-predicted linking) plus a robust analysis (straight-line filter, medians), self-tested end to end: it recovers a synthetic 5.000 mm/s drift exactly. The self-test caught two of my mistakes:
- a frame-rate/linking mismatch (now documented as a rule: ≤ 5 px per frame);
- noise tracks biasing the mean (fixed by the straightness filter and medians).

**M9 touch.**
- Without avoidance, contact loses 6–14 % of the motes a hand meets.
- With predictive avoidance, there are 0 losses: the image parts around the hand by up to 5.5 cm and reforms.
- My first two versions of the avoidance logic were wrong:
  - one parked motes in the hand's path;
  - one chased schedule lag through space.
  Both were fixed before the result was recorded.

**Red team 5** is reviewing v2, M4–M8c and the bench code. **R10** is researching the steering engine.

## 2026-10-01 · Entry 20: The steering engine is an étendue and cost wall

**R10 survey, with my checks.**
- **Shared window.** Each beam is ~148 mm wide at the head (checked), so every beam fills a ~150–300 mm window. The engine must be a shared objective with tiled steering cells, not a per-beam patch.
- **Module floor.** Steering modules per head ≥ f_cov (G/E)². My check for a 10 mm galvo gives ~560, against R10's 620–960.
- **Tweezer arrays** are 25–300× short in field.
- **Focus tracking** is the least mature function.

**M10 (R10's suggested next step).** f_cov on the 12-head rig is ≈ 0.75–1. Shrinking per-head coverage to 0.58 raises the worst heat factor from 2.2 to 8.

**Cost today (R10).**
- Accent room $0.5–5 M.
- Film-density room $4–40 M.
- With integration: ~$0.4–2 M.

**Verdict R10 (startup-buildable) stays NOT MET today.** The path there is a fundable component: a large-étendue 2-axis analog MEMS mirror array.

**Entry 20, addendum: M11 demonstrator ladder (conditional on G1–G2).**

| Demo | Beams | Cost today | Integrated |
|---|---|---|---|
| D1 first glyph | 69 | $0.05–0.3 M | — |
| D2 arc-reactor UI | 350 | $0.25–1.8 M | — |
| D3 desk Jarvis panel | ~970 | $0.7–4.9 M | $49–243 k |
| D4 Iron-Man sketch | ~2 400 | $1.7–12 M | — |

Small demos are mote-limited; the étendue floor dominates only at ~1 m fields. A credible startup path: bench B1–B4, then D1, D2, then an integrated D3.

(Housekeeping: commit 763f503's message lost its dollar figures to shell expansion; the correct figures are in RESULTS §10.)

## 2026-10-01 · Entry 21: Ultimate bound, and a safety-accounting fix I found myself

**M12, ultimate bound.** With hypothetical perfect materials (perfect skin, k_eff 0.01, survives 900 K), beam counts fall only ~30 % below the ITO floor:
- sketch ~1 300;
- film density ~5 300.

The binding limit moves from heat to the 10 mW Class 1 cap on trap beams. **The MOTE route is fundamentally a 10³–10⁴-beam machine for Iron-Man content.** No material breakthrough changes that order of magnitude.

**Self-found correction.** Beams converging on a mote add at the cornea at 1550 nm. `budget2` checked them per beam; it now checks the sum per focus. Effects:
- the floor rises: accent ~490, sketch ~2 100, film density ~8 800, film-exact 8 800–10 500;
- passive doughnut pairs become the best architecture (2 beams per focus).

**Demonstrators re-run:**

| Demo | Beams | Cost today |
|---|---|---|
| D1 | 79 | $0.06–0.4 M |
| D2 | 404 | $0.3–2 M |
| D3 | ~1 100 | $0.8–5.6 M |
| D4 | ~2 400 | $1.7–12 M |

Red team 5, still running, reviews the pre-fix state; its findings will be applied on top.

## 2026-10-01 · Entry 22: Red team 5, and the honest scale of the MOTE route

**RT5: 2 critical, 10 major.** Every key item verified before acceptance:
- **Pump beams uncounted (C1).**
- **"Floor" was really an optimistic design point (C2).**
- **"Laminar zone" was my physics error (M3).** Feed-forward cannot remove drag.
- **Pair factor 1.35/η (M1).**
- **Core–shell pump branch silently lost in an earlier patch of mine (M4).** Confirmed by inspection, then restored.
- **Pump turbulence and focus (M5).**
- **k_overlap not certifiable as written (M6).**
- **60 Hz (M7).**
- **ITO ≤ 573 K (M8).**
- **B1 confounds C_ph with J₁/A (M10).**

The cornea-sum item (M2) I had found independently an hour earlier.

**M13 (budget v2.1).**
- **Without certified safety scheduling, nothing is feasible.**
- **With it (best estimate):** accent ~2 800, sketch ~12 200, film density ~50 000 steered beams (trap + pump).
- **Demonstrators:** first 10 cm glyph ~455 beams ($0.3–2.3 M today); sketch ~12 200 ($8.6–61 M).

Two red teams moved the film-density figure from my v1 claim of 4 500 to 50 000 (×11). Each step was a real error found and verified. This is exactly why the owner's double-validation rule exists.

**Where the vision stands, factually.**
- Physics does not forbid an open-air, silent, chemistry-free, Class-1-per-focus, touchable Iron-Man hologram. The MOTE route is that existence proof on paper.
- But at today's best estimate, it is a 10⁴–10⁵-beam machine that needs:
  - a mote nobody has made;
  - a safety argument nobody has certified;
  - a quiet room.
- It is not a "very sophisticated projector" in the consumer sense.
- The two measurements that could move this by large factors are cheap: B1 (force law) and B2 (mote FOM).

**Entry 22, addendum: M14, the regulatory lever.** Certified interlock credit (30 mW per focus) gives:
- accent ~1 350 steered beams;
- sketch ~5 900;
- film density ~20 300;
- motes at 0.45–0.53 m/s.

Above 3× the heat limit binds again, so the lever is worth ~2–2.5× and saturates. **All levers stacked** (perfect execution, interlock credit, integrated MEMS at $50–250 per channel): an Iron-Man sketch room is ~$0.3–1.5 M and a film-density room ~$1–5 M. Today: ~$4–30 M for a sketch.

# T7: Gaussian static voxels, forward-scatter illumination and the Class 1 speed bound (round 3 of the unlock program)

**Status: not solved.**
- Round 3 closes the physics chain for **slow content in still air**, with every link quantified.
- It finds a new bound (B9) that explains why fast content and draughty rooms stay out of reach under passive eye safety.
- Every number here is pending red team 7.

**Files**
- `m18_gaussian_lcsv.py`: design model. Output in `results/m18_run.log` and `results/m18_gaussian_lcsv.json`.
- `m18b_holo_loop.py`: hologram-rate pinning loop, plus the Gaussian common-radial-loss model.
- `m18c_vector_pin.py`: 3D vector loop with the real H10 heads and LP allocation. Output in `results/m18c_*`.

**What carries over, and what is reused**
- Red team 6's corrections C1–C3 all stand:
  - authority at U + 5.4σ;
  - power provisioned at U + 3.1σ;
  - aerogel motes are index-matched (n ≈ 1.04).
- RT6's validated code is reused, not re-derived: BHMIE, the loop tuner and simulator, the draft spectra and LP `min_push`. Rule 11 (no duplicated simulation) is respected.

## 1. Three design changes against RT6's corrected LCSV

### 1.1 Gaussian spots instead of flat-tops (answers RT6 C2a)

RT6 showed that a flat-top of plateau ρ (in units of λ/NA) needs 1.2π²ρ² modes per spot area. Flat-tops were chosen only to tolerate the 8 µm binary-DMD jitter.

A Gaussian focus has no flat-top excess. For waist w, one head addressing an L × L field needs

> M_head = (2·clip·os·L / (π w))²  (independent of the throw),

with:
- clip 1.2: aperture side 2.4 W, where W = λd/(πw);
- os 1.5: pixel oversampling, so that the grid replicas fall outside the field, behind a field stop. Envelope efficiency is 0.65.

The étendue minimum is L²/(πw²). The clip and os factors cost 4.1× above that minimum.

At equal conventions this is about 8× fewer modes than RT6's flat-top count. The price is that the spot force depends on position, so the loop must hold the mote near the centre (§3).

### 1.2 Forward-scatter, viewer-aware illumination (answers RT6 C3 without a coat)

The uncoated ITO-aerogel mote scatters almost nothing sideways. It is a weak phase object, and its scatter is concentrated in the forward diffraction lobe. Own BHMIE run (RT6's code; the self-test reproduces RT6's q(30°) 0.27 and q(90°) 3.2×10⁻³):

| a | q(10°) | q(15°) | q(20°) | q(25°) | q(30°) | q(90°) |
|---|---|---|---|---|---|---|
| 0.75 µm | 12.8 | 5.7 | 1.5 | 0.13 | 0.08 | 7×10⁻⁴ |
| 1.0 µm | 24.5 | 5.0 | 0.25 | 0.49 | 0.27 | 3.7×10⁻³ |
| 1.5 µm | 27 | 2.0 | 1.4 | 0.29 | 0.24 | 3.5×10⁻³ |

(q_iso at 500 nm, averaged ±2.5°. The coat target in RT6 was 0.3.)

**How it is used.** Each visible spot is aimed so that its line through the mote passes 10–20° from a tracked viewer's eye. The mote then sends that viewer 15–100× more light than a white-coated mote would at 90°. Consequences:
- **No coat.** The mote keeps FOM 5.3 instead of 4.1.
- **Visible spots of 10–20 µW.** This is far below the 0.39 mW Class 1 limit even with 3.3× pupil stacking and 2 beams per mote.
- **Little stray light.** About 0.07 W of visible light for a sketch, and wall light of 0.0008 cd/m².

**Costs**
- Illumination must come from *behind the image* as each viewer sees it, within 10–25°. That needs viewer tracking and visible emitters spread around the room: about 15 for a horizontal ring of viewers.
- Each visible emitter forms spots of w_v ≈ 15–50 µm across the field. Its mode count is of the same order as an IR head's, so it is **not cheap**.
- The lobe has Mie ripples (q(15°) sits near the first Airy null for a = 1 µm). Two remedies:
  - a polydisperse mote batch, ±10 % in radius;
  - working at 8–10°, inside the main lobe.
- The viewer must not stand in the unscattered beam. Its cone half-angle is only λ/(π w_v) ≈ 0.6°, so this is easy to avoid with tracking.

### 1.3 Small motes: heat is no longer binding (answers RT6 C1 heat)

The mote's temperature rise scales with its size and its speed relative to the air: ΔT ∝ a·v_rel (B3 with B2). At a = 1 µm, the hot face at gust peaks (U + 5.4σ) is:

| Room | Hot face | With one head occluded |
|---|---|---|
| Still | 330 K | 368 K |
| Home (U 0.05) | 341 K | 390 K |
| Quiet office (U 0.1) | 352 K | 411 K |
| Office (σ 0.1) | 429 K | 555 K |

All are below the 573 K limit for ITO. In RT6's own table the 5 µm coated mote reached 655 K at σ 0.1.

**Price.** I_hold rises ×1.39 at 1 µm because slip reduces the photophoretic force. The self-test checks B2 with slip included.

## 2. B9, a new bound: under passive Class 1 the mote's speed relative to the air is capped

**Class 1 at 1500–1800 nm** [memory, IEC 60825-1; RT7 to verify]:
- for t ≤ 10 s the limit is a radiant exposure of 10⁴ J/m², over 1 mm for t < 0.35 s;
- beyond that, an irradiance of 1000 W/m² over 3.5 mm, i.e. about 10 mW.

So the cap applies to *mean* power per focus. Gust surges lasting milliseconds are harmless: the 0.35 s dose limit over 1 mm is 7.85 mJ.

**The bound.** Three relations combine:
- the per-focus mean power is P = h_worst·I·πw²/2;
- B2 gives I = I_unit·v_rel (I_unit ≈ 7.3×10⁶ W/m² per m/s for the 1 µm ITO mote, slip included);
- the worst pupil collects s·P (M17 stacking).

Together:

> **v_rel,mean ≤ 2·AEL / (π w² · h_worst · s · I_unit)**

| w | Static voxels (h·s ≈ 7.1) | Sparse geometry (h·s ≈ 1.5) |
|---|---|---|
| 15 µm | 53 cm/s | 2.6 m/s |
| 20 µm | 30 cm/s | 1.5 m/s |
| 35 µm | 10 cm/s | 48 cm/s |
| 50 µm | 4.9 cm/s | 23 cm/s |
| 70 µm | 2.5 cm/s | 12 cm/s |

**What it means**
- v_rel is the draft *plus* the content's own motion.
- A still room already spends about 4.8 cm/s on its draft: the mean of |u| is σ√(8/π).
- Static voxels at w = 50 µm therefore have essentially no budget left for moving content.
- Iron-Man animation (0.25–1 m/s at model edges) under *passive* Class 1 needs w ≈ 10–20 µm and sparse geometry. That runs into the diffraction limit at room throws (w ≥ λd/(πR)) and into loops of ≳ 20–50 kHz (§3).
- The bound is independent of mote size (B2), apart from slip. The only material lever is the FOM: an ideal skin absorber has a ceiling of about 7–11, against 5.3 today, so at most ×1.4–2.
- **B9 is why every route tried so far ends in "still air, slow content", or in interlock-based eye safety** (the curtain I1, which opus rated P ≈ 0.2–0.3 for consumer acceptance).

## 3. Pinning without a DMD: the hologram as the actuator

**The loop (m18b, m18c).**
- RT6's loop machinery: von Kármán + Pao drafts, exact discretisation, PID tuned at modulus margin ≤ 2, saturation at 5.4σ.
- The modulator is the hologram itself: frame rate f, latency of d frames, its own response lag.
- Sensor noise is 3–6 µm per frame.
- The Gaussian spot's force falls off with the mote's offset.

**Common-radial model (m18b).** It applies exp(−2r²/w²) to every beam.
- It shows a **profile instability**. When the mote drifts, its force drops, so it drifts further.
- The growth rate is about F·4r/w² (~500–800 s⁻¹ at w = 50 µm, F ≈ 0.05 m/s). That is faster than a 40–60 Hz loop.
- Gain scheduling (the controller divides by the spot factor at the measured position) helps at 100 µm, not at 50 µm.

**Vector model (m18c).**
- The ten real H10 heads.
- Minimum-power allocation: the hull facet hit by the force ray, i.e. 3 beams. It equals RT6's linprog to 4×10⁻¹⁶.
- Each beam loses force only through the mote's offset across its own axis.
- Gain scheduling and a per-beam authority cap.

Results with 4 µm noise and L = 3 cm. Quick runs are 30 motes × 3 s; the full grid is 60 motes × 20 s in `results/m18c_run.log`:

| Modulator (latency) | Still | Home (U 0.05) | Quiet office (U 0.1) |
|---|---|---|---|
| PLM 1.44 kHz (2 frames) | lost at all w ≤ 70 µm | lost | lost |
| PLM 1.44 kHz (1 frame) | holds at 70 µm (0/60 in 1 188 mote-s); lost at ≤ 50 µm | same | same (0/60 at 70 µm) |
| MEMS 3 kHz (2 frames) | holds at 50–70 µm | 1/30 lost at 50 µm | 2/30 lost at 50 µm |
| MEMS 5 kHz (2 frames) | holds at 50–70 µm (r_p99.9 7 µm) | holds at 50–70 µm | holds at 50–70 µm |
| MEMS 10 kHz (2 frames) | see results/m18c_run.log | | |

Long runs (60 motes × 150 s) at the candidate points are in `results/m18c_vector_pin_long.json`. **Zero losses in T mote-s only bounds the rate at 3/T.** The 10⁻⁴ /s target needs ≥ 3×10⁴ mote-s, which these runs do not reach.

**Takeaway.** A **≥ 3–5 kHz phase modulator with ≤ 2 frames of total latency** holds 1 µm motes in w = 50 µm Gaussian spots in still to quiet-office air. Today's 1550 nm LCoS (60–400 Hz) cannot.

**Physics allows it; no part does yet.**
- MEMS piston modulators settle in ~10 µs.
- TI's PLM is a MEMS device whose 1.44 kHz is set by its data path.

**The cost.** The full hologram is recomputed every frame:
- 6×10⁹ pixels × ~600 spots per head × 5 kHz ≈ **1.5×10¹⁶ operations/s**;
- **~120 Tb/s** into the modulators.

**I9: decouple the loop from the hologram** [ARCHITECTURE, main session; RT7 to check].
- **Idea.** A slow hologram (≤ 100 Hz) forms the spots. Per-spot amplitude is then set by a *stack of 4 fast transmissive amplitude layers* in the head's demagnified intermediate image volume.
- **Geometry.** At ×15 lateral demagnification, the 0.8 m image depth becomes 3.6 mm, so the layers are ~0.9 mm apart, each conjugate to a 0.2 m slab.
- **Why low NA makes it work.** Gaussian beams have NA ≈ 0.01, so each spot is ≤ 1 mm (room units) at its own layer and ≤ 8 mm at the others. The layers therefore need only ~1 mm room-unit pixels (~1.2 Mpx per layer).
- **Crosstalk** ≈ 0.1–0.5 %. That is (projected spot density 354 /m² per slab) × (footprint 12–200 mm²) × (modulated fraction).
  - RT6's 72–99 % was for one plane at NA 0.03–0.08.
- **Étendue.** Each 73 × 73 mm layer at NA_int 0.15 carries the head's 5×10⁻⁴ m²·sr.
- **Speed.** It needs analog-capable fast LC: DHF-FLC or π-cell, ~100 µs.
- **What it buys.** The loop's compute falls to per-mote PID plus allocation, ~10⁸ operations/s. Data falls to ~0.2 Tb/s per head.
- **What it does not fix.** Moving content still needs the slow hologram to move the spots: content speed ≤ w·f/k (B8), which is 1.7 mm/s at 100 Hz. **I9 is therefore for static or slowly morphing scenes only.**

## 4. Design points that pass every check (m18, `results/m18_run.log`)

Common assumptions:
- H10;
- 1 µm uncoated ITO-aerogel mote: FOM 5.3; A = 1 or 0.5;
- forward illumination at 15°;
- η = 0.75 (hologram) × 0.65 (pixel envelope) × 0.85 (optics);
- mean-power Class 1 with M17 stacking recomputed for Gaussian beams: 3.3 for a sketch, 5.2 for film.

| Content / room | Modulator | w | IR | Modes, IR heads | Data | Hologram compute | Visible |
|---|---|---|---|---|---|---|---|
| Sketch, still | MEMS 5 kHz | 51 µm | 12.5 W | 6.1×10⁹ | 123 Tb/s | 1.5×10¹⁶ /s | 0.07 W |
| Sketch, home | MEMS 10 kHz | 43 µm | 13.7 W | 8.7×10⁹ | 347 Tb/s | 4.3×10¹⁶ /s | 0.09 W |
| Film density, still | MEMS 10 kHz | 40 µm | 48 W | 9.7×10⁹ | 387 Tb/s | 2.9×10¹⁷ /s | 0.57 W |

Rows that fail:
- **Quiet office:** every row fails. Class 1 needs w ≤ 33 µm and the loop needs ≥ 40 µm.
- **Office (σ 0.1):** fails on everything that depends on Class 1.
- **A = 0.5:** fails except for the sketch in a still room at 10 kHz.
- **Visible-emitter modes are not counted above.** They are of the same order, ×1–2 over about 15 emitters.

**Compared with RT6's corrected table**, still-room film density becomes feasible (48 W against "infeasible at 100 W"). It also needs no coat, no DMD, and no curtain. **The mode count did not fall:** Class 1 caps w at ~40–50 µm, and the loop forbids smaller w without faster modulators.

## 5. What remains (the walls, ranked)

1. **B9 and drafts → still air and slow content.**
   - Under passive Class 1 the mote's mean speed relative to the air is at most ~5–10 cm/s at buildable spot sizes.
   - That is a **physics bound**, not an engineering one.
   - The levers are:
     - a higher FOM: at most ×1.4–2;
     - interlock-based eye safety: venue-grade, uncertain for consumers;
     - a force mechanism with far more force per watt than ΔT-photophoresis in air. None is known; see T6 §1 and B2.
2. **The hologram engine.**
   - 6–10×10⁹ IR modes plus visible modes.
   - 5–10 kHz if the hologram is the loop actuator (10¹⁶–10¹⁷ operations/s).
   - Or, with I9, ~100 Hz holograms plus fast amplitude stacks, but then slow content only.
3. **Content speed.** Moving content needs moving spots: w·f/k ≥ 0.25 m/s means f ≈ 15 kHz full-hologram updates. B9 caps it at 5–10 cm/s anyway. **Fast Iron-Man animation is excluded under passive Class 1.**
4. **The mote**, which has never been made:
   - a 1 µm ITO-island-skin aerogel sphere with A ≥ 0.5–1, k_eff ≈ 0.04 and a size spread for smooth forward scatter;
   - respirable, with indium toxicology (R3).
5. **Visible geometry.** Forward illumination needs emitters behind the image for every viewer, plus viewer tracking.
6. **Sensing.** Every mote must be located to ~4 µm, 5–10 thousand times a second, with ≤ 1 frame of latency.
   - Photon budget: ~4 500 photons per mote per 0.2 ms through a 25 mm lens at 1.5 m, so σ ≈ 3 µm at 100 µm pixels.
   - Needs a multi-ROI camera readout. Plausible, not built.

7. **Touch stirs the air** (`m18d_touch_air.py`, `results/m18d_run.log`).
   - **A moving hand.** Potential flow past a sphere gives |u| ≤ V(R/r)³. Measured from the centre of the hand or finger, motes are lost within:

     | | V = 0.3 m/s | V = 1 m/s |
     |---|---|---|
     | Finger | 1.0 cm | 1.5 cm |
     | Hand | 5.5 cm | 8.3 cm |

     There is also a turbulent wake at Re ≈ 300–6000.
   - **A warm, still hand** sends 0.10–0.4 m/s of air upward. That is 2–8× B9's mean budget at w = 50 µm, and the range comes from two estimates (laminar plate and MTT plume).
   - **A glove that keeps its surface within ~1.5 K of the room** cuts this to 0.035–0.2 m/s. That gives the owner's "simple glove" a second job: it must be thermally neutral.
   - **What touch looks like.** The hologram parts around a moving hand, over ~1–8 cm, and re-forms from spare motes. Motes cannot rest on the skin. A person's body plume (~0.2 m/s) keeps the image ≥ 15–20 cm from torsos and faces.

## 6. Bottom line for the full vision

**Physically consistent (pending RT7):** slow or static Iron-Man-style sketches, and film-density wireframes, floating in still air with no screen, glasses or gas. They need:
- passive Class 1 at 1550 nm and in the visible;
- 12–50 W of IR;
- a never-built mote;
- a ≥ 5 kHz, ~10¹⁰-mode phase engine.

**Not reachable with passive eye safety:**
- **fast animation** (≥ 10 cm/s content);
- **ordinary ventilated rooms** (σ_u ≈ 0.1 m/s).

Both are capped by B9, which is a physics limit of ΔT-photophoresis in air combined with the 10 mW Class 1 AEL. **"Touchable" interaction stirs the air locally,** so the hologram near a moving hand runs in "office" conditions and will shed motes there.

**The needle, if it exists, has to beat B9.** Candidates:
- a light-to-force mechanism in air with ≫ 2×10⁻⁵ N/W per µm of mote;
- a way to make the focus inaccessible to the eye without interlocks;
- an eye-safety basis other than per-pupil mean power (none is known at 1550 nm).

## 7. What to measure first (value of information)

1. **The 1 µm ITO-aerogel mote:** A, k_eff, and q(θ) over 5–30° with a size spread. Bench B2 plus a goniometer.
2. **Draft statistics (U, σ, L) in a "still" living room with people present**, and next to a moving hand. This decides B9's budget.
3. **A 1–4 kHz phase modulator at 1550 nm** holding one mote in a w = 50 µm Gaussian focus with camera feedback. This checks the profile instability and the loop.
4. **An I9 stack:** two fast LC layers in a demagnified intermediate volume, measuring crosstalk.

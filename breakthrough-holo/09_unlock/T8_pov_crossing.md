# T8: fast POV motes under passive Class 1 by the crossing-rate rule ("POV-X")

**Status: REFUTED as a full-vision candidate by red team 8** (`05_reviews/red_team_8_pov_x.md`). The main session checked it: m19b with the force resolved inside each frame loses 16/20 motes in office air at w 35 µm, against 1/20 with a frame-held force. **What survives:** the crossing-rate framework (B9 does not bound moving foci), and POV as a research direction.

> **Red team 8 verdict** (3 critical, 11 major, 8 minor; double-validated against m17, m18c, linprog and m19b's own code):
> 1. **The pupil load is 2.7–9.1× the AEL.** The minimum-power LP pushes each mote with beams running along its stroke, so one pupil on a stroke collects every neighbour's beam within ~12 cm of divergence.
>    - T8's waist gives 26–88 mW, and 57–88 mW on the project's own Iron-Man outline, against an AEL of 9.6 mW.
>    - Class 1 then needs w ≈ 11–23 µm, below the diffraction floor of 0.11 m heads.
>    - A stacking-aware allocation fixes random content, but the compact outline is still ×2.2–4.5 over.
> 2. **The 20 kHz loop loses motes.** The force tracks the mote within ~2 µs, inside a frame, and a profile instability grows at ~4vδ/w² ≈ 10⁴ /s.
>    - With the force resolved inside the frame: 3.6–9.9 losses/s per mote in office air and 0.2–0.7 /s in still air at w ≈ 35 µm.
>    - It holds only with ~2 µm sensing in still air, or w ≥ 50 µm.
> 3. **"~3 200 channels, no hologram engine" is inconsistent.**
>    - Tour motes cross the whole field, so a channel needs 46–52 mm·rad per axis, and a 0.22 m head has the étendue of ~2 such channels.
>    - Sharing a head therefore needs a mode multiplexer, i.e. a hologram or a positioner array. Positioners cannot animate, and they cost 4.5–6.8× the beams in use.
> - **Majors:**
>   - the EN 50689 skin margin is 0.75;
>   - a strict ICNIRP reading needs a 0.6–1 ms stall cut;
>   - a multi-focus single fault reaches 8 mJ in 5–25 ms;
>   - IR power is 7.7 W, not 4.4 W, because every mote moves all the time;
>   - with the realistic mote the hot face at an office gust peak is 593 K, and 655 K with one head occluded;
>   - the farthest throw's diffraction floor is 32 µm;
>   - visible light per RT7 C1, with a 39 µW blue photochemical limit;
>   - 30 Hz flicker at a 4–6 % duty per point;
>   - indium in room air reaches 4–180 % of Japan's worker limit at the simulated loss rates.

**Original status line (superseded):** candidate full-vision architecture, physics-consistent in my models, not yet validated by a red team.

**Files**
- `m19_pov_crossing.py`: design model. Output in `results/m19_run.log` and `results/m19_pov_crossing.json`.
- `m19b_pov_track.py`: 3D vector tracking loop for moving motes. Output in `results/m19b_*`.

**Inputs from earlier rounds**
- idea round 3 (opus, `idea_round_3_opus.md`, idea 2);
- R7 rows K6/K7 (the standards basis);
- T7: the 1 µm mote, forward-scatter illumination, and Gaussian spots with follow mode;
- RT6: the corrections.

> **Updates after red team 7 and idea round 3 (sonnet)** (main session, pending red team 8):
> - **Mean wind (RT7 C3).** m19b now adds the mean wind U and includes it in the authority. POV spots follow their motes, so it holds: at 20 kHz and v 0.5 m/s, the quiet office (U 0.1) loses 0/20 at w 35–50 µm, and the office (σ 0.1, U 0.1) loses 2/20 at 35 µm and 0/20 at 50 µm. The §3 table predates this fix.
> - **Realistic mote (RT7 C2): E/L doubles.**
>   - With A = 0.5, the eye-limited waist is 21–24 µm for a sketch and 17.5–20 µm for film density.
>   - Heads need an aperture radius R ≥ 0.15 m (30 cm) for diffraction. The office film case fails even then.
>   - The loop must then hold ~20 µm spots (`results/m19b_smallspot_quick.log`: 20 motes × 3 s, mean wind on, v 0.5 m/s):
>
>     | Loop | Sensing noise | w = 20 µm | w = 25 µm | Drawing error p50 / p99.9 |
>     |---|---|---|---|---|
>     | 20 kHz | 2 µm | loses 17–19/20 | holds | 3–9 / 10–14 µm |
>     | 20 kHz | 1 µm | holds | holds | 1–2 / 2–5 µm |
>     | 40 kHz | 2 µm | holds (0/20, still and quiet office) | holds | 2–4 / 5–9 µm |
>
>   - **Requirement with the realistic mote:** ~40 kHz per-channel loops with ≤ 2 µm sensing, or 20 kHz with ≤ 1 µm. These are short runs only (56 mote-s each), so loss rates are not yet bounded below 5×10⁻²/s.
> - **EN 50689 child-appealing skin rule** (sonnet, snippet-verified): 0.785 mW mean through 1 mm over 10 s. With the realistic mote this caps the waist at ~19–21 µm (sketch). A strict ICNIRP small-beam reading would also need a ~0.7 ms stall cut, against T8's ≤ 100 ms.
> - **Visible illumination (RT7 C1)** applies to T8 too. Free-standing viewers all round the image need 66–220 wall emitters, and the direct beams reach the audience. Restricting viewers to a front zone (~15–20 emitters), or using an isotropically scattering mote, are the alternatives. Neither is solved.
> - **Strokes that move along themselves** (sonnet's moving-beam sim) put 11–25× the limit through a pupil on the stroke. The content planner must assign motes so that no pupil is swept repeatedly, using an Eulerian assignment and a space-time dose map.

## 1. The loophole in B9: a moving focus is a pulse train, not a static focus

**The standards basis.** Two independent sources agree:
- **R7 (2026-09-30):** each pass of a scanned or moving beam across the aperture is a pulse. Rule 1 (single pulse) and rule 2 (average over T) apply. C5 does not apply above 1400 nm or on skin. Classification must survive a scan/stall single fault (IEC 60825-1:2014 §4.3; ICNIRP).
- **Opus round 3:** the same rules, from the IEC preview and DTIC sources.

**The invariant.** A mote moving at v relative to the air needs P = h·I_unit·v·πw²/2 (B2), so the **energy per unit path is E/L = h·I_unit·πw²/2, whatever its speed**. A pupil on a stroke is crossed f_r times per second, and the stroke tubes of other motes add to that (s′). Its mean power is

> P̄_pupil = f_r · s′ · d_ap · (1 + u/v) · E/L ≤ AEL (10 mW)

There is no v in the bound. The draft enters only as (1 + u/v).

**Counting s′.** POV lays f_r·E/L per metre of stroke. That is equivalent to static voxels at spacing δ with power f_r·E/L·δ each. M17's stacking for random heads then gives s′ = 1 + (s_static − 1)·δ/d_ap:
- **≈ 3.0 for a sketch;**
- **≈ 4.6 for film density.**

The opus estimates were 1.5 and 3.3, which I corrected upward.

**The other two rules**
- **Rule 1** (a single pass ≤ 7.85 mJ over 1 mm, t < 0.35 s): passes carry 0.05–0.11 mJ, a margin above 70×.
- **Stall fault:** a stuck focus reaches the rule-1 dose in **0.25–0.76 s**. The tracking loop sees a stall in < 1 ms, so a ≤ 100 ms independent cut is easy.

## 2. Design (m19, 30 Hz refresh, 1 µm uncoated ITO-aerogel mote, H10, head aperture radius 0.11 m)

| Content / room | v | Motes | Channels | w (eye) | Hot face at gust peak | IR | Visible | Visible per pupil |
|---|---|---|---|---|---|---|---|---|
| Sketch, still to office (σ 0.1) | 0.5 m/s | 526 | 3 158 | 31–34 µm | 433–521 K | 4.4 W | 0.015 W | 35–43 µW (≤ 390) |
| Sketch, still to quiet office | 0.8 m/s | 329 | 1 974 | 34–35 µm | 489–507 K | 4.4 W | 0.015 W | ✓ |
| Film density, still / home | 0.5–0.8 m/s | 1 355–2 169 | 8 133–13 012 | 27–28 µm | 433–498 K | 17 W | 0.08 W | ✓ |
| Film density, office | 0.5–0.8 m/s | | | 25–26 µm | 521–573 K | | | below the diffraction floor of 0.11 m heads; needs larger apertures |

Notes on the table:
- **Total IR power does not depend on v:** P_IR ≈ S·AEL·h_mean/(s′·d_ap·h_worst·η).
- **Visible** uses forward illumination at 10° (q = 24.5). Rule 3 (C5) for the retina has not been evaluated yet.
- **Beams per mote:** 6, i.e. 3 LP pushes + 1 hand-over + 2 illumination (RT6 M9).

## 3. Can a steered spot carry the mote along the stroke? (m19b: vector model, real H10 heads)

**Model**
- Each mote traces the tightest POV loop: a circle of radius v/(2π f_r), i.e. 2.7 mm at 0.5 m/s.
- The controller uses plan feedforward, predicts across the latency, keeps the spot centred on the predicted mote (follow), runs PID, allocates by LP, and caps each beam at (v + 5.4σ)·c_max.
- Sensing noise is 4 µm per frame, with 2 frames of latency.

**Results** (quick runs, 20 motes × 2 s):

| Per-channel loop | w | v | Still | Quiet office | Office (σ 0.1) | Drawing error p50 / p99.9 |
|---|---|---|---|---|---|---|
| 5 kHz | 35–50 µm | 0.5–0.8 | lost | lost | lost | — |
| 10 kHz | 50 µm | 0.5 | 0/20 | 0/20 | 1/20 | 6–20 / 18–35 µm |
| 20 kHz | 50 µm | 0.5–0.8 | 0/20 | 0/20 | 0/20 | 3–14 / 10–22 µm |
| 20 kHz | 35 µm | 0.5 | 0/20 | 0/20 | 1/20 | 5–17 / 22–27 µm |
| 20 kHz | 35 µm | 0.8 | 11/20 | 14/20 | 19/20 | — |

- The grids for w = 25–35 µm, 2–4 µm noise and 40 kHz are running. They will go into `results/m19b_*`.
- **The requirement:** each steered channel needs a **~20 kHz fine loop** (fine steering by piezo or EO plus per-channel sensing, ≤ 100 µs total latency) to carry the eye-limited w ≈ 31–35 µm sketch spots at 0.5 m/s.

## 4. What this architecture delivers against the vision (if validated)

- **Touchable.** The motes' authority is v + 5.4σ ≈ 1 m/s, so a warm hand's plume (0.1–0.4 m/s) and slow gestures stay within it. A fast hand still clears ~1–8 cm, and motes re-form behind it. Feel comes from the glove.
- **Open air, no screen, glasses or gas:** ~300–2 000 solid µm motes are in the air at any time.
- **Ordinary rooms, office drafts included:** the draft costs only (1 + u/v) in eye budget and heat at gust peaks, and the 1 µm mote stays ≤ 521 K at 0.5 m/s.
- **Fast animation:** content can move as fast as the motes, 0.5–0.8 m/s.
- **Safe for everyday use:**
  - passive Class 1 at 1550 nm by the crossing-rate rule, plus a stall safeguard, which the base standard's scanning provision covers;
  - visible light under Class 1 (rule 3 still to be checked);
  - **the open item is toxicology:** 1 µm ITO motes are respirable (R3).
- **"A very sophisticated projector":**
  - 10 heads of ~0.22 m aperture;
  - ~3 200 single-mode channels for a sketch, ~8 000–13 000 for film density;
  - 4–17 W of IR;
  - **no hologram engine.**
- **Brightness:** 3–4 cd/m² lines for a dim lab. A lit room (50 cd/m²) breaks visible Class 1 per pupil by ~10×.

## 5. Open items: what must be true for "it works"

1. **The mote:**
   - a 1 µm ITO-island-skin aerogel sphere with A ≈ 1 and FOM ≈ 5.3, never made;
   - A = 0.5 halves the eye-limited w², which needs faster loops;
   - toxicology.
2. **The per-channel loop:**
   - ~20 kHz with ≤ 100 µs latency and ~4 µm sensing per mote, ×3 000 channels;
   - sensing per channel by quadrant photodiodes on the beam's far side (T6 I6), or high-speed multi-ROI cameras.
3. **Channel hardware** (T7 and the opus notes on étendue). A full-field channel needs D·θ ≈ 24 mm·rad per axis (about a 25 mm, ±0.5 rad mirror). The cheaper route is a "patch" channel:
   - a fiber positioner in the image plane of a shared objective (DESI-style) for the coarse position;
   - a fast fine stage for the ~1.5 cm stroke segment.
   POV motes patrol only v·duty/f_r ≈ 1–1.5 cm per refresh, so the fine stage covers ±1 cm and the coarse positioner moves only when content moves. Patch coverage overhead for clustered strokes is about ×1.5–3.
4. **Acceptance of the crossing-rate classification for a consumer product:**
   - the stall safeguard must be functional-safety-rated;
   - the EN 50689 extra limits for child-appealing products are unknown;
   - ICNIRP's small-beam skin note (opus §4.8) is an open question.
5. **Flicker at 30 Hz.** 60 Hz doubles the motes and channels, and halves w² through the eye bound.
6. **Pupil stacking under a scheduler** (opus idea 1). If assignment cuts s′ to ~1.5, w grows by ×1.4 and loops get easier.

## 6. Comparison with the earlier verdicts

| | v4 (MOTE, best estimate) | T7 (holographic static voxels) | T8 (POV-X) |
|---|---|---|---|
| Sketch channels / modes | 12 200 steered beams | ~6×10⁹ modes at 5 kHz | ~3 200 steered beams |
| Rooms | quiet zone ≤ 0.15 m/s | still air only (B9) | office drafts OK |
| Content speed | ≤ 0.2–0.5 m/s | ≤ 5–10 cm/s | 0.5–0.8 m/s |
| Eye safety | needs certified scheduling | passive Class 1 | passive Class 1 by crossing rate, plus stall cut |
| Mote | FOM ≥ 4, 2.5–5 µm, pumped phosphor | 1 µm ITO, forward scatter | same as T7 |

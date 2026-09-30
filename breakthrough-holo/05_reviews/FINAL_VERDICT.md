# Final verdict

*Graded against the requirements frozen in `00_mission/GOAL.md` before any results existed. Three independent models (Opus, Sonnet, Fable) reviewed the bottleneck and reached the same verdict; see `IDEA_ROUND_1_SYNTHESIS.md`. A requirement is MET only if a simulation or cited measurement supports it with numbers, and PARTIAL if it is met only under stated restrictions. Draft v1: will be revised after the red-team review.*

## One-paragraph answer

**Iron Man-*style* holograms from a single projector, with no glasses, fog, gas or screen, visible from all around and touchable with a glove, can be engineered on paper with known physics and within safety limits. They are not film-*exact*.**

The only way to make light at a point in open air is to turn that point of air into a tiny plasma spark with a focused eye-safe (1550 nm) laser pulse (T1: a theorem plus a numerical kill of every alternative). Air sparks are poor lamps, and each one makes a click and a whiff of NO/O₃. That caps a room-safe display at roughly **0.2–0.5 lumens of light, i.e. 5–9 m of glowing strokes**, redrawn 60 times a second (T2, E10).

In a **dim, warm-lit room**, which is how Tony Stark's workshop is lit, that is enough to reproduce the film's *contrast* and a *near-cyan azure* hue (E11), life-size and all-around. It stays quiet enough for an office (~40–44 dB(A)) thanks to a new drawing method, subsonic multi-channel tracing (E6c).

It cannot match the film's density (the film shows 9–57 m of strokes), its brightness in a lit room, its orange accents, or full-motion video. Those would need 10–400× more light than the air of a room can safely supply.

## Scorecard

| ID | Requirement | Grade | Evidence |
|---|---|---|---|
| R1 | Image in free space, nothing behind it | **MET** | In-volume plasma voxels (T1, E3) |
| R2 | No eyewear | **MET** | Isotropic emission seen by the naked eye |
| R3 | No added media | **MET** | Only room air, ionised at the focus. The capture airflow is room air. |
| R4 | Projector only (+ glove) | **MET** | One ceiling "halo": laser, optics, sensors and air handling (ARCHITECTURE). Needs a dimmable, warm-lit room. |
| R5 | All-around, many viewers | **MET** | Spontaneous emission is isotropic; no viewing zone (T1) |
| R6 | 3D models, animation, video panel | **PARTIAL** | 3D wireframes and animation at 60 Hz within a 5–9 m stroke budget (holo_engine demo). Video only as a low-resolution monochrome dot panel (~2.6k dots). |
| R7 | Touch interaction | **MET** | Glove haptics against the virtual geometry. Content in front of the hand stays visible (in-volume emission). The interlock leaves a 22 mm gap around skin and blanks < 4 % of the image (E7). |
| R8 | Safe for everyday use | **PARTIAL** | Five sub-checks below. |
| R9 | Iron Man quality | **PARTIAL** | Life-size ✓; µm voxels at 2 mm pitch ✓; film contrast in a dim lab ✓; azure hue 202–213° vs film 181–199° (near) ✓; smooth 60 Hz ✓. **Density 5–9 m vs the film's 9–57 m ✗; orange accents ✗** (desired only). |
| R10 | Buildable by a startup | **MET** (build) / ⚠ (sell to homes) | Every part exists today (1550 nm ultrafast fibre lasers, AODs, depth cameras, FPGA). BOM, roadmap and a runnable reference pipeline are provided. **Unmeasured plasma numbers:** X1, X2, X6, X7. **Regulatory:** EN 50689 allows consumer lasers only in Class 1, Class 2 and a restricted part of Class 3R; Class 1C (engineering-protected eyes) is for skin-contact devices only. So there is no home-product route today; first sales are venue or professional under variance (Entry 6). |

**R8 sub-checks:**

| Check | Result | Status |
|---|---|---|
| Laser | Hazard confined to ≤ 16 mm around each focus; ≤ 10 % of MPE elsewhere. Relies on an active tracking interlock (Class 1 by engineering controls), not intrinsic safety. **Consumer classification not currently available** (EN 50689), so venue/professional use under variance comes first. | ✓ physics / ⚠ regulation |
| Air | Breathing-zone increment 10–23 ppb. P(≤ 50 ppb) = 0.82–0.96 and P(≤ 13 ppb, strict WHO 24-h NO₂) = 0.58–0.75 over literature uncertainty. | ⚠ pending X1–X2 |
| Hearing and ultrasound | 40–44 dB(A); ultrasound bands ≤ 82 dB (limits 85 dB(A) and 100 dB). | ✓ |
| Living-room comfort | 40–44 dB(A) is above the WHO 35 dB(A) guideline. | ⚠ |
| UV | More than 100× margin. | ✓ |

**Result: 7 MET, 3 PARTIAL, 0 NOT MET under the pre-registered criteria. Against the owner's stricter wish, "exact Iron Man hologram quality", the answer is no.** Film-exact brightness in a lit room scores P(safe) ≈ 0.01–0.11 (E10).

Per the owner's instruction and the pre-registered rule ("ping only if the design MEETS the spec"), **this outcome does not trigger a ping.**

## What is genuinely new here

1. **A clean impossibility result (T1).**
   - Line-of-sight theorem and touch lemma.
   - A numerical kill of Rayleigh, Raman, coherent and incoherent nonlinear optics, acousto-optics, microwave and thermal routes.
   - Conclusion: air plasma is the *only* projector-only, medium-free route, whoever builds it.
2. **The light–chemistry–noise trilemma (T2).** It turns "can we build Iron Man holograms?" into two measurable numbers: lumens per absorbed joule, and reactive molecules per joule.
3. **Subsonic multi-channel tracing (E6c).**
   - Draw every stroke with a regular > 20 kHz click train moving slower than sound. This removes 19.5–26.5 dB of audible noise in *all* directions, including room reverberation.
   - The same idea was reached independently by the Opus reviewer. The Sonnet reviewer, lacking it, judged noise unrecoverable.
4. **Listener phase locking (E6b):** −35 to −40 dB direct-field noise at up to 8 tracked ears at once, by firing-time optimisation. Reflections cap the real-room gain at 1–10 dB, and I caught and corrected my own over-claim.
5. **Warm-room colour adaptation (E11):** the colourless-looking plasma reads as saturated azure in a 2700 K room (Bradford model). That is close to film cyan.
6. **A runnable reference pipeline (`holo_engine/`).**
   - Content → budget fit → safety gate (tracked hands and heads, 3 apertures) → glove haptics → physically scaled previews.

## What would change the verdict

- **X1/X2 at the optimistic end** (efficacy ≥ 1 lm/W for 5–20 µJ seeded-and-heated kernels, and ≤ 10¹⁶ reactive molecules per J, mostly NO): the stroke budget grows about 5–15×, reaching film density in a dim lab.
- **Owner accepts contained particles** (T3): colour and brightness routes reopen, with their own safety problems.
- **Owner accepts a helmet visor** for personal use: exact film quality is available today, and it is a separate product.

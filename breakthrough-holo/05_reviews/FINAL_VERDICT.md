# Final verdict (v3, after the SPARK instrument campaign and three red teams)

*Graded against the requirements frozen in `00_mission/GOAL.md` before any results. History: v1 over-graded; red team 1 corrected it to v2; this v3 adds the SPARK spark-physics instrument (built after the owner's "AI builds its own instrument" request), its 40-format atlas, and red teams 2 and 3.*

## Answer

**The full vision cannot be unlocked by simulation or by engineering: an Iron Man film-quality hologram in open room air from one projector, with no glasses, fog or screen, touchable, and safe for everyday home use.** Two parts are proved and one is regulatory:

1. **Physics (T1).** In clean air, light can only be made at a point by turning that point into plasma. Every other mechanism fails by many orders of magnitude, and three independent models plus two red teams agree. So any such projector is a laser-spark display.
2. **Physics (SPARK instrument).** Laser sparks are dim lamps: 0.016–0.4 lm per absorbed watt, and smaller for the fine sparks that thin lines need. They make ozone and NO, emit actinic UV, and click.
   - A home display is ruled out by **noise**. Spark noise alone exceeds a living room's 35 dB(A) in 97–100 % of simulated cases, even with a silent air handler.
   - Anything near film brightness is ruled out by **air quality**.
3. **Regulation.** The beam is an open Class 4 laser focus. Consumer laser rules (EN 50689) have no route for it, so it is a supervised-venue installation at best.

**What remains open, and only a bench can settle it:** whether a *venue* version can show an Iron-Man *sketch* (≈ 5 m of glowing blue-white lines, dim room, touchable with a glove). SPARK puts that probability anywhere between **0 and ~0.6**, depending on three things no simulation can pin down:
- whether the quiet-drawing trick works on real sparks;
- how much of the fumes the airflow captures;
- the true UV/ozone per unit of light.

## Scorecard (v3; unchanged from v2 except the evidence)

| ID | Requirement | Grade | Evidence |
|---|---|---|---|
| R1 | Free-space image | MET | T1; in-volume plasma |
| R2 | No eyewear | MET | isotropic emission |
| R3 | No added media | MET | room air only |
| R4 | Projector only | PARTIAL | needs a dim warm room, a laser rack and an air handler |
| R5 | All-around, many viewers | MET | isotropic |
| R6 | 3D models, animation, video | PARTIAL | sparse wireframes; video only as a dot panel at near random-order noise |
| R7 | Touch | PARTIAL | glove haptics yes; the interlock leaves 45–90 mm holes around hands |
| R8 | Safe for everyday use | **NOT MET** | Home: noise (SPARK + E10c; red team 3). Laser: open Class 4. Air: fails beyond a sketch in home-sized rooms. UV: binds only for lamp certification at 0.2 m, not at normal viewing distances (red team 3 corrected my T4 v1 claim). |
| R9 | Iron Man quality | PARTIAL | the film's contrast in a dim room at sketch density, if the venue questions resolve favourably; no orange; not film density |
| R10 | Buildable by a startup | NOT MET | the scanner étendue problem is only solved on paper (galvo tiling, E12); 20–60 W 1550 nm ultrafast sources are not commercial parts |

**4 MET, 4 PARTIAL, 2 NOT MET. Not solved, so no ping, per the owner's rule.**

## What the SPARK campaign established (and how firmly)

| Result | Firmness |
|---|---|
| Laser-spark hydrodynamics, energy closure and implosions work numerically | Implementation-validated: Sod, Sedov, Noh, conservation, convergence (22/24 validation tests pass) |
| ns-spark radiated share 25 % (measured 22–34 %), NO 7.4–7.9×10¹⁶ /J (measured 4.6×10¹⁶–1.5×10¹⁷), cooling at 10 µs, shock pressure at 1 mm | Physics-validated against published measurements |
| Micro-spark light per watt 0.016–0.4 lm/W, rising with spark size (P5 ✓; P10 coefficient ✗) | Model result, ±3× (Biberman factor, conductivity, LTE deposition) |
| A second pulse *reduces* light (P9 ✗) | Model result, robust in sign |
| A line focus triples light per watt, with the same UV and chemistry per unit light | Model result, robust (like-for-like comparison) |
| UV and O₃ rise in step with light (T4) | Model property, not a law. The UV ratio is set by the continuum model (±×3); 30–54 % of the reactive total is an ad hoc EUV rule |
| Deep-UV lines make sparks ozone-rich | Model result; the line strengths are from memory (±3×) |
| Honest fails | V16 (noise-law cross-check, ill-conditioned) and V18 (early temperature at 1 µs) |

## What would move the verdict (bench experiments, ordered by value of information)

| # | Measurement | Why it matters |
|---|---|---|
| 1 | Subsonic multi-channel tracing on real sparks (X4): audible spectrum of a regular click train moving slower than sound, with UI-like content | Venue sketch probability 0 without it, ~0.2–0.6 with it |
| 2 | Source capture of spark fumes with a heated manikin and hands in the volume (X5) | Capture 0.3 → 0.9 moves the air cap ~10× |
| 3 | Calibrated 180–900 nm spectrum and lumens per absorbed joule for ps micro-sparks, time-resolved over the first 50 ns (X1) | Tests SPARK's η and the UV-per-lumen value (P14b), and the instantaneous-LTE assumption |
| 4 | O₃, NO and NO₂ per joule and per lumen (X2/X7), versus Cook 2000's "no detectable O₃" for long sparks | Tests the ozone-rich prediction |

None of the plausible outcomes makes a home Iron Man projector. They decide whether a supervised, dim-venue "hologram sketch" product exists.

**Other routes to the owner's goals (T3):**
- **Helmet visor:** exact film look now; it is eyewear, which a helmet can have.
- **Contained particle displays:** colour at desk scale.

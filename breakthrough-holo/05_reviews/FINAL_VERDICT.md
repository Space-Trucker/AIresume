# Final verdict (v2, after the red team)

*Graded against the requirements frozen in `00_mission/GOAL.md` before any results existed. A requirement is MET only if a simulation or cited measurement supports it with numbers. v1 over-graded. The independent red team (`red_team_1.md`) found 3 critical and 11 major problems; I re-checked every critical and major claim I could test, and all held. Validation details are in NOTEBOOK Entry 7. This v2 adopts the corrected scorecard.*

## One-paragraph answer

**No, not as the owner asked: a single projector cannot make film-quality Iron Man holograms in open air that are safe for everyday home use. The reason is physics, not effort, and five independent analyses agree.**

The only way to make light at a point in open room air, with no glasses, fog or screen, is to ionise that point with a focused laser (T1: theorem plus numerical elimination of every alternative). Air sparks are dim lamps: 0.01–1 lm per watt, and never measured for display-sized sparks. Every spark also produces:
- a click (noise);
- NO₂/O₃ (air quality);
- UV-C (a skin and eye dose).

It is also an open Class 4 laser focus.

Put together, the safe light budget in a room is far below what the film shows (E10b, red-team corrected, Monte Carlo over all literature uncertainty):
- **Home use: probability 0** at every content level. Noise alone rules it out; even the scrubber fan exceeds 35 dB(A).
- **Supervised venue** (≤ 55 dB(A)): 0.71 for sparse accents (~1 m of glowing strokes), 0.36 for an Iron-Man "sketch" (~5 m), 0.21 for film contrast in a dim lab (~9 m), 0.08 for film density (~30 m), 0 for the film-exact lit lab.

## Scorecard (v2)

| ID | Requirement | v1 | **v2** | Why |
|---|---|---|---|---|
| R1 | Image in free space | MET | **MET** | In-volume plasma voxels (T1, E3) |
| R2 | No eyewear | MET | **MET** | Isotropic emission |
| R3 | No added media | MET | **MET** | Only room air |
| R4 | Projector only (+ glove) | MET | **PARTIAL** | Needs a dim (≤ 10 lux), warm-lit room, a separate laser rack, and an air handler |
| R5 | All-around, many viewers | MET | **MET** | Spontaneous emission is isotropic |
| R6 | 3D models, animation, video | PARTIAL | **PARTIAL** | Sparse wireframes only; video is a low-resolution dot panel at almost random-order noise (red team #7, reproduced: UI content −6 dB) |
| R7 | Touch | MET | **PARTIAL** | Glove haptics work, but a laser interlock blanks a 45–90 mm sphere around every hand and ~170 mm around heads. Ceiling apertures shadow up to ~20 % of content under a leaning user (red team #11). |
| R8 | Safe for everyday use | PARTIAL | **NOT MET** | Six sub-checks below. |
| R9 | Iron Man quality | PARTIAL | **PARTIAL** | Film-contrast azure strokes are possible only as a sparse sketch in a dim warm room, and the efficacy they rely on is unmeasured. There is no orange, and the film density of 9–57 m of strokes has P(safe) ≤ 0.2. |
| R10 | Buildable by a startup | MET | **NOT MET** | Three problems, listed below. |

**R8 sub-checks:**

| Check | Result |
|---|---|
| Laser | An open Class 4 beam (peak 17× and average 2000–4000× over Class 1). Presence sensing cannot lower the class. EN 50689 bars consumer Class 4; the US needs an FDA variance (red team #14; confirmed, Entry 6). |
| Interlock | The v1 margins allowed 2× the MPE (verified). Concave objects can re-collimate the transmitted beam across the room (red team #12). |
| UV | The band-resolved actinic dose at 0.3–0.5 m is 0.1–5× the 8-h limit (E7b, worse than the red team's estimate). |
| Air | The v1 assumption of 90 % capture from a ceiling sink is implausible; realistic 0.3–0.7 (red team #9). |
| Noise | 50–58 dB(A) at the user plus the fan, against 35 dB(A) (red team #8). |
| Hearing | Hearing-safe; nothing approaches 85 dB(A). |

**R10 problems:**
- The random-access scanner violates étendue by ~250× per axis (verified).
- A galvo-tiled redesign (E12: 4 heads, NA ≈ 0.03, 100–160 µJ per voxel) is consistent on paper, but it enlarges the hazard zones and has no optical design yet.
- A 20–60 W 1550 nm ultrafast source is not a commercial part.

**Result: 4 MET, 4 PARTIAL, 2 NOT MET. Not solved. Per the owner's instruction, no ping.**

## What is solid (and new)

1. **T1: impossibility theorem.** Light at a point in clean air must be made there. The v1 argument is sharpened by the idea rounds' momentum-budget argument: every coherent process stays inside the source aperture's cone. So a projector-only, medium-free, all-around display is necessarily an air-plasma display, whoever builds it.
2. **T2: the governing budget.** For any such display, lumens per joule against reactive molecules, audible sound and UV per joule. The binding numbers are two unmeasured plasma properties: efficacy, and NO/NO₂/O₃ per joule.
3. **E6c: subsonic multi-channel tracing.** A new drawing law for quiet plasma displays: regular > 35 kHz click trains moving slower than sound. It gives −20 to −26 dB total radiated noise for long smooth strokes, but only −3 to −8 dB for UI or video content (red team, reproduced).
4. **E5b, E7b, E11, E12:** speciation kinetics, band-resolved UV, colour adaptation, and the étendue budget. Each removes a hidden assumption a future builder would otherwise trip on.
5. **Process:** three independent idea rounds and one red team. Two of my own over-claims were caught and corrected in the record (Entries 3 and 7).

## What an honest next step looks like

A **desk-scale, supervised research demonstrator** (≈ 5–30 cm field, 1 galvo head, Class 4 under a variance, dim room) whose purpose is to *measure* the numbers that decide everything (ROADMAP X1–X7):
- lm per absorbed J;
- speciation;
- the 200–400 nm UV spectrum;
- spark stability;
- the capture efficiency of a real airflow.

If X1 turns out ≥ 1 lm/W with O₃-free, NO-light chemistry and low UV-C, the venue tier grows. None of the plausible outcomes makes a safe living-room Iron Man projector.

For the owner's other ideas:
- A **helmet visor HUD** gives exact film quality today; it is eyewear, which is allowed in a helmet.
- **Contained particle displays** give colour at desk scale (T3).

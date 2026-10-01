# Prediction registry: MOTE route (committed before any MOTE instrument run)

**Route.** The projector dispenses and holds a few hundred to a few thousand microscopic motes (≈ 2–25 µm) in focused infrared photophoretic traps. It moves them at persistence-of-vision speed. The motes emit visible light themselves (upconversion, pumped by the same or a co-aligned IR beam), so no visible laser beam crosses the room.

GOAL R3 status: grey zone (projector-supplied, recovered matter). Total mass is micrograms, not a fog or aerosol.

First-principles basis (NOTEBOOK Entry 13):
- continuum photophoretic force F = 9π μ² a I J₁ / (2 ρ T (k_p + 2 k_g));
- v_max = F / (6π μ a), independent of mote size;
- mean heating ΔT ∝ a·I;
- required flux Φ = 4π L w S; motes needed N = S f / v.

| ID | Prediction | Interval |
|---|---|---|
| P15 | Max reliable trace speed of a 5 µm composite mote whose mean heating is kept ≤ 150 K | 0.3–1.5 m/s |
| P16 | Motes needed at 30 Hz: 5 m sketch / 30 m film density | 100–600 / 600–3000 |
| P17 | Total IR trap power for film density (30 m, 4 cd/m²) | 1–30 W |
| P18 | Visible lumens per watt of *total* IR sent into the room (trap + pump), green upconversion motes | 0.05–2 lm/W |
| P19 | A 5 µm mote at ≥ 0.7 m/s can be held with ≤ 10 mW per beam (the IEC Class 1 CW limit at 1550 nm) | yes |
| P20 | A room draft of 0.2 m/s causes > 1 %/s mote loss unless the trap force margin is ≥ 2× the drag at 0.2 m/s | yes |
| P21 | Film-exact brightness (50 cd/m², 30 m of strokes, lit lab) needs < 5 W of absorbed emitter power in total, zero reactive gases and zero audible noise from the motes | yes |

## Addendum A: registered after R5–R7 reported, before MOTE instrument v1 runs (2026-09-30)

R5–R7 changed the question. First, room throw (1–3 m) makes the trap focus much wider than the mote (w ≈ λd/(πR)). Second, published single-beam photophoretic traps have only worked at 80–160 mm. Third, US/EU consumer rules require Class 1 for an IR display. So the instrument v1 compares two trap architectures:
- **Single-head lateral trap.** Lateral restoring force comes from the intensity gradient across the mote; efficiency is taken to scale as a/w.
- **Multi-head push trap.** Four or more heads, each beam pushing along its own axis, stabilised by active position feedback.

| ID | Prediction | Interval |
|---|---|---|
| P22 | Single-head lateral trap, 1.5 m throw, 100 mm aperture, 1550 nm: best speed at ΔT ≤ 200 K over a = 1–5 µm and k_p ≥ 0.02 W/m/K | 0.1–0.5 m/s |
| P23 | Four-head push trap with feedback, tracing at 1 m/s in a 0.1 m/s draft with 0.1 m/s gusts: control-loop rate needed for < 1 %/min mote loss | 2–20 kHz |
| P24 | Film density (30 m, 4 cd/m², 30 Hz) with a 1550 nm trap and a violet/blue-pumped phosphor: Class 1 per beam **and** at every head's exit aperture, with head apertures ≤ 300 mm; total 1550 nm power | yes; 2–15 W |
| P25 | Same film density with a Yb-rich UC emitter pumped at 980 nm: Class 1 at 980 nm (per beam and exit aperture) needs a head aperture | ≥ 200 mm |
| P26 | BYU's 1.83 m/s record (a ≈ 5 µm char particle), run through our force model at η = 1 with slip corrections: implied mean mote heating ΔT | 250–700 K |

## Scores (after instrument v2 = v1 + red team 4 corrections; full table in RESULTS.md §8)

- **✓ (2):** P21, P22.
- **Partial (2):** P15, P26.
- **✗ (6):** P16, P17, P18, P19, P23, P24.
- **Inconclusive (2):** P20, P25.

The v1 scores (8 ✓) rested on model errors found by red team 4, and are withdrawn.

## Addendum B: DIY bench predictions, registered 2026-10-01 before any DIY measurement

These come from `08_bench/sim_d1_lens_trap.py` (21 self-tests) and `08_bench/diy_calcs.py`. Rig: 405 nm diode, Thorlabs LA1509-A (f = 100 mm) or an equivalent N-BK7 plano-convex, beam vertical and pointing up.

| ID | Prediction | Interval |
|---|---|---|
| P27 | Smooth spheres (glassy carbon 2–12 µm, black PE ≥ 10 µm) held in a single upward beam, lens flat side first, beam 1/e² radius ≈ 3 mm: the lateral drag speed at which they are lost (moved by galvos or a stage) | ≤ 2 cm/s |
| P28 | Irregular black particles (activated charcoal < 10 µm, candle soot, graphite, toner) in the same rig: at least one type traps with gravity-independent behaviour (also holds with the beam horizontal) and reaches | ≥ 0.1 m/s |
| P29 | Adding a corner-cube return beam (DIY-2c) to the P27 rig: sphere loss speed rises by, and spheres also trap with the beam horizontal | ≥ ×5; yes |
| P30 | Capture probability against beam 1/e² radius, LA1509 flat side first: peak location; with the curved side first at the same radius, capture is | 2.8–3.6 mm; ≤ ½ of the peak value |

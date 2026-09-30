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

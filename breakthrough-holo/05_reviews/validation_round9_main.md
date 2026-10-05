# Round 9 validation (rule 12): fresh recomputation of m22, m23 and the opus round-4 numbers

**Why the main session ran this itself.** The independent sonnet validator launched for round 9 stopped at its first step: a safety filter flagged the request, which included a question on inhalation dosing. The main session did not try to get around the filter. It recomputed the physics numbers itself with a fresh script, `09_unlock/v9_fresh_check.py`, which does not import m22 or m23. The thermal kick model uses an exact exponential update rather than m22's Euler integration. Output: `09_unlock/results/v9_fresh_check.log`.

| Claim (source) | Project value | Fresh value | Agree |
|---|---|---|---|
| Kick ratio, 40 / 20 / 5 µm (m22 D) | 10.11 / 78.04 / 168.59 | 10.11 / 78.04 / 168.59 | ✓ |
| Peek onset field, q_lim at 20 µm (m22 B) | q_lim 1.58e-12 C | 3.56e7 V/m, 1.583e-12 C | ✓ |
| Positive photo-recapture q (m22 B) | 6.95e-17 C | 6.954e-17 C | ✓ |
| Pauthenier q, room / corona field (m22 B) | 1.34e-16 / 1.34e-13 C | 1.335e-16 / 1.335e-13 C | ✓ |
| Pump floor at w 40 µm, Er:Yb / Nd:YAG / InGaAsP (m22 E) | 2.04e5 / 7.16e4 / 1.24e4 W | 2.044e5 / 7.155e4 / 1.241e4 W | ✓ |
| Coulomb-crystal strain (m22 F) | 1.1e5 / 1.1e3 / 98 | same | ✓ |
| Tetralemma w_max, skin rule, 1 / 3 / 10 cm/s (m22 H) | 37.6 / 21.7 / 11.9 µm | same | ✓ |
| Room rain (m23): n, mg/m³, optical depth, g/h | 2.57e7, 56.2, 0.63 %, 33.5 | same | ✓ |
| Room particles at 99.9 % capture; dropout; vertical coverage (m23) | 50 µg/m³; 0.135; 0.33 | same | ✓ |
| Visible flash at w_v 140 / 80 µm (m23) | 1.33 / 0.44 mW; 5.15 / 1.69 µJ; AEL 10.84 µJ | same | ✓ |
| Ghost dots at w_v 140 / 80 µm (m23) | 0.188 / 0.020 | same | ✓ |
| Probe photo-electrons per crossing (m23) | 13 236 | 13 236 | ✓ |
| Opus round 4: drop and mote size, drying time, latent heat, Lambert p(90°) | 38.5 µm → 10.5 µm; 0.86 s; 11.8 W; 0.764 | 38.6 → 10.4 µm; 0.86 s; 11.8 W; 0.764 | ✓ |

**Scope and limits.**
- This check confirms the arithmetic and one change of integrator.
- It does **not** confirm that the formulas are physically right. That is red team 9's brief: the gating geometry, the visible pulse-train safety rules, the vertical-stroke rendering model, and the pump bound's DOF assumption.
- The mannitol/Aridol statement in T9 rests on the main session's recall. It is also put to red team 9.

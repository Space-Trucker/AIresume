# Idea round 1: synthesis (three independent models, each briefed with the same bottleneck memo)

Files: `idea_round_1_opus.md` (35 ideas), `idea_round_1_sonnet.md`, `idea_round_1_fable.md`. All three models reached the same verdict independently.

## Where the three models agree with the lab

- The line-of-sight theorem and touch lemma hold.
  - Opus sharpened them into a *momentum-budget theorem*: every coherent process driven from an aperture emits inside that aperture's cone.
  - The only escapes are incoherent emission at P, condensed matter at P, or gain-guided emission.
- Air plasma is the only projector-only, medium-free emitter.
- Film-exact quality (lit-room brightness, 10⁴–10⁵ points, cyan + orange) is not reachable within bystander safety. The closest achievable thing is a dim-room plasma display.

## Adopted (and tested here)

| Idea | Source | Lab test | Outcome |
|---|---|---|---|
| **Subsonic multi-channel "pens"**: regular > 20 kHz clicks at trace Mach < 1 | Opus C2; independently the lab (E6c) | E6c | **−19.5 to −26.5 dB total radiated audible power, all directions.** Robust to ≤ 10 % spark jitter (−18 dB). Adopted as the primary noise method. |
| Avoid the Mach-cone trap | Opus C4 | E6 / E6c | Confirmed: supersonic path drawing is +7.6 dB |
| Heat-release (thermoacoustic) noise law | Opus C1 | `display_budget.heat_release_band_p2` | Agrees with the lab's N-wave model within 0.2 dB. Adopted as a cross-check. |
| NO is not NO₂; O₃-limited conversion; O₃ scrubbing | Opus D1/D2, Sonnet D1 | E5b kinetics | Room-safe power ×2.3 (O₃-rich) to ×12.3 (NO-rich). Adopted; speciation becomes experiment X7. |
| Warm-surround chromatic adaptation | Opus B1, Sonnet B1 | E11 (Bradford) | The plasma is seen as azure (hue 202–213°) vs film cyan (181–199°). Adopted, with the stricter Bradford result, not the optimistic dominant-wavelength one. |
| Budget in stroke length × luminance | Opus §0.5 | `content.fit_to_budget` | Adopted; the demo content is now budget-compliant |
| Strict NO₂ limit (WHO 24-h ≈ 13 ppb) | Opus §0.2 | E10 | Adopted as the strict criterion |
| Glove with four jobs (emitter for on-hand content, laser protection, markers, haptics) | Opus E4, Sonnet E | ARCHITECTURE §3.6 | Adopted. On-hand emitters could also carry the film's *orange* accents on the gauntlet. |
| Seed-and-heat voxels (fs seed + long-λ heater); GA pulse shaping ×1.82 | Opus A2/A7, Sonnet A3 | Inside the `eta_mult` uncertainty band | Adopted as the X1 test matrix |

## Recorded but not adopted

| Idea | Why |
|---|---|
| Gaze-contingent density (Opus E5, ×2–4) | Needs gaze tracking of every viewer at room distance. Plausible later upgrade; not credited in the budget. |
| Shock recycling (Opus A6) | Net loss (shock-focusing light yield ≲ 10⁻³) |
| RF sustainment of laser seeds (Opus A5) | Needs 0.75–2.5 MV/m, far above RF exposure limits (confirms E1 kill) |
| Eye-directed ASE "line voxels" (Opus E2) | Only violet/UV gain lines in air, gain-length ≪ 1 at 1 atm. P ≈ 0.02. |
| Ambient ions, dust or humidity as media (Opus E6/E7) | Too weak, or the grey zone in disguise |
| Levitated bead swarm (Sonnet F2, Opus F1) | E9: 114–142 dB room ultrasound. Tabletop-enclosure product only. |
| Gated upconversion nanoparticle aerosol (Sonnet F1, Opus F4) | An aerosol medium (R3) with unknown inhalation toxicology. Recorded in T3. |
| Active anti-noise (Opus C5) | Global only below ~300–500 Hz, where noise is already small |

## Where the lab disagrees with a reviewer

- **Sonnet: "noise is 35–45 dB over and no pulse format or cancellation recovers it."** Subsonic tracing is not cancellation of individual sparks. A regular, subsonically moving click train simply has almost no audio-band content (a steady moving source doesn't radiate). E6c shows it numerically with full phase-accurate sums over 96 far-field directions.
- **The lab's own first E6 claim (−26 dB) was direct-field only.** It was corrected (Entry 3) before any reviewer flagged it.

## Fable (added) and its validation

- **Top ideas:**
  - A downdraft-hood capture with a consumable cartridge.
  - Constant-flux acoustics: never blank, grey scale by revisit density, and a subwoofer for the < 300 Hz frame comb. This is the same physics as E6c.
  - Warm dim room with N II / Ar II cyan lines.
  - Seeded ps and 2 µm heater with Zeldovich freeze-out for 3–10× lm per NO.
- **Regulatory warning (confirmed, Entry 6):**
  - EN 50689 consumer products are limited to Class 1, Class 2 and a restricted part of Class 3R.
  - Class 1C is for skin-contact devices only.
  - So there is no home-product route for an open-air plasma projector today. It is a venue or professional product under variance.
- **Its 10–30 lm estimate was not adopted:** it omits the near-field plume (~127 ppb at 0.5 m) and assumes ~1 lm/W for 10 µJ kernels.

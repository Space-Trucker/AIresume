# Idea round 2 brief: find the loophole ("needle") that unlocks the full vision

**Read first:** `00_mission/GOAL.md` (requirements R1–R10), `05_reviews/FINAL_VERDICT.md` (v4 verdict: 4 MET / 5 PARTIAL / 1 NOT MET), `02_theory/T5_mote_theory.md`, `07_mote_route/RESULTS.md`.

## Where we stand (2026-10-01)

**Physics routes.**
- **T1:** light at a point in open air needs **matter or plasma** at that point.
- **Plasma** (laser sparks) is ruled out for homes by noise, O₃/NO₂ and UV.
- **Acoustic bead displays** (MATD-type, Hirayama et al. *Nature* 2019) were ruled out at room scale by ultrasound exposure.
- The surviving route is **MOTE**: 1–3 µm motes held by 1550 nm photophoretic beams (Class 1 per beam), glowing via an Eu²⁺ cyan phosphor under a µW 405 nm pump.

**What blocks "solved".**
1. **Material.** The mote needs FOM = (J₁/A)/(k_eff + 2k_g) ≳ 4 m·K/W. The design is an ITO/Cs_xWO₃ island skin on a 1–4 µm silica aerogel; it has never been made, and its k at µm scale has never been measured.
2. **Steering engine.** About 2.8k (accent), 12k (sketch) and 50k (film density) steered beams at $0.7–5k each.
3. **Drafts.** Normal rooms (0.3 m/s drafts, hand plumes) defeat mote speeds of ~0.5 m/s, so a quiet-air zone is required.
4. **Product safety.** Class 1 for the product depends on a certified beam scheduler.

## Bounds derived by the main session (attack these)

- **B2, holding intensity.** I_hold = 4ρT·h·w / (3η·C_ph·μ·FOM·A·Cc), with:
  - ρT = p/R (353 kg·K/m³);
  - w = mote speed relative to air;
  - h ≥ 1, the push-geometry overhead (tetrahedral 2.2, octahedral 1.5);
  - η ≤ 1 for pushes, ≤ 2/π for lateral gradient traps;
  - A = absorptance;
  - Cc = slip correction.

  I_hold is **independent of mote size**: about 4×10⁶ W/m² at w = 0.3 m/s, FOM = 5, h = 2.2.
- **B3, heat.** ΔT = A·a·I/(4k_g). Small motes run cool.
- **B4, eye safety per focus.** Total power ≤ P_AEL (10 mW at 1550 nm) inside any 7 mm aperture. So the light must sit within r_c ≤ √(P_AEL/πI) ≈ 27 µm of the mote, and the mote must be localised to ~27 µm.
- **B5, addressable modes.** Per beam direction, M ≥ A_field / (π r_c²) = A_field·I/P_AEL ≈ 4×10⁸ for a 1 m² field.
- **B6, control rate.** f ≥ u/r_c ≈ 10 kHz in a normal room. Passive gradient traps need feature sizes ~a, which costs 10–100× more modes.
- **B7, light budget.** Total emitted flux for line luminance L over S metres of strokes is Φ = 4π·S·w_res·L. That is ≈ 0.66 lm for film density (30 m, 4 cd/m², w_res = 0.44 mm).
  - The pump must land on µm motes efficiently.
  - Unabsorbed 405 nm light makes walls glow through optical brighteners.
  - The 405 nm Class 1 AEL is 39 µW.
- **Acoustic route.** About 0.03–1 W of ultrasound per bead.
  - Beam cones exceed the **100 dB** public limit (IRPA, 25–100 kHz) within ~1 m of each bead.
  - The reverberant room field is 104–126 dB at sketch to film scale.
  - No guidelines exist above 100 kHz, but strong air absorption there forces arrays within ~0.5 m.
  - Upside: strong forces, built-in haptics, cheap arrays, mm beads that are not respirable.

## Main-session candidate to attack or improve: "every beam is its own light curtain" + holographic static voxels

- **Light curtain.** Each trap beam terminates on a receiver head (octahedral layout: 3 opposed pairs). The receiver monitors each beam's transmitted power. Any blockage (eye, finger, sleeve) cuts that spot within ≤ 1 ms through the next SLM frame, with a fast AOM as backup.
  - **Dose.** 50 mW × 1.4 ms = 70 µJ, against the 1 ms corneal limit of ~9.6 mJ in a 3.5 mm aperture.
  - **Effect.** This removes B4's 10 mW cap, so B5 becomes a power–modes invariant: P_total · M ≈ N·I·A_field.
  - **Precedent.** IEC 61496 light curtains; IEC 60825-4 active laser guards.
- **Holographic static voxels.**
  - Static motes act as dotted-line voxels, spaced δ = 1–3 mm, and move only as the content moves.
  - Fast phase SLMs (holographic multi-spot, per-spot amplitude) replace thousands of galvo beams.
  - Receivers double as position sensors through the mote shadow.
- **Open problems.**
  - The pump efficiency problem (B7) with spots ≫ mote.
  - SLM speed (kHz) and 1550 nm phase stroke.
  - Hologram compute latency.
  - POV is incompatible with discrete hologram steps (the trap can move only ≤ r_c per update).

## Your task

Think like a theoretical physicist hunting for loopholes. For each idea, give the physics with **numbers** (order of magnitude at least), what it fixes (blocker 1–4, bounds B2–B7, or requirements R1–R10), and the new risks. Cover:
1. **Loopholes** in B2–B7: any assumption that is not fundamental.
2. **Materials with already-measured properties** that reach FOM ≥ 3–4 for µm motes, or a geometry whose FOM follows from bulk data. Avoid unmade composites if you can.
3. **Draft immunity** for a normal room (0.3 m/s, hand plumes, breathing).
4. **Light generation** that avoids the pump-focusing problem: self-aligned pumping, trap light converted to visible light, emitters that tolerate heat, or anything else.
5. **Steering or holography technology** at ~10⁸–10⁹ modes with kHz updates: what exists in 2026, what it costs, and what its limits are.
6. **Entirely different routes** that satisfy R1–R10 and that we have missed: other forces, other emitters, perceptual tricks that still keep light at the point. Search the literature (2015–2026).
7. **An adversarial check of the light-curtain candidate.** Does it really hold up under IEC 60825-1/-4 and the MPE tables? What are its failure modes?

Use web search where you can. Tag every claim as [MEASURED+source], [THEORY], [ESTIMATE] or [SPECULATIVE]. Rank your top 5 ideas by (expected impact × probability it is real). Be honest: if something cannot work, say so with the number that kills it.

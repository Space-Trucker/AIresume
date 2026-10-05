# Idea round 5: a loophole hunt against the full-vision tetralemma (brief for one independent idea agent)

## The vision

**What the owner wants:** Iron Man 1/2 lab holograms, which must be:
- touchable (a simple glove is allowed);
- in open room air;
- not a holo-table or holo-wall;
- free of glasses, gases or fog, and screens;
- safe for everyday use, including children (EN 50689);
- "just a very sophisticated projector" (several discreet heads in the room are fine);
- buildable at home from commodity (Amazon/Alibaba) parts.

**The owner's words:** "you have to solve whether it's more or something new", "stay ambitious and not lazy".

## Where nine red teams and four idea rounds left it

Read these first:
- `05_reviews/FINAL_VERDICT.md` (v6 at the top);
- `09_unlock/T9_home_routes.md` (with the RT9 correction box);
- `05_reviews/red_team_9_home.md`;
- `09_unlock/idea_round_4_opus.md`.

Skim:
- `09_unlock/idea_round_3_opus.md` (force-per-watt physics floors);
- `09_unlock/T6_unlock_theory.md` (T1: matter must be at the image point);
- `05_reviews/red_team_8_pov_x.md`.

**The tetralemma (T9 §2.8).** These four cannot all hold at home with known physics and commodity parts:
1. **No fog:** ≲ 10⁴ individually controlled motes, or a sub-visible medium.
2. **Occupied open air:** per-mote authority above drafts of a few cm/s (gusts ~0.2 m/s), or a conditioned air column.
3. **Child-safe light:** per-mote force must come from light, because static fields from outside cannot address mm structure (Laplace low-pass). The per-focus cap then forces small spots. Under the skin rule at 3 cm/s, w ≤ 22 µm.
4. **Commodity addressing:** that needs ~7.7×10⁷ modes per head at ~14 kHz, against today's 10⁶–10⁷ modes at 0.1–10 kHz.

**Already killed** (deciding numbers are in the files):
- plasma voxels;
- acoustic levitation and acoustic POV (SPL);
- photophoretic static voxels (B9 plus modes) and photophoretic POV (RT8);
- electrostatic support (body distortion, one-way charge ratchet);
- Coulomb crystals;
- self-addressing laser cavities (5 kW–0.8 MW pump);
- helium bubbles; bead or drop rain;
- upconversion and photochromic selection;
- EHD fans (ozone);
- eye tricks and retinal steering (T1);
- retroreflective gloves;
- aerial-imaging plates (a window, excluded);
- FLOW-X targeting and AIR-SV in open rooms;
- FLOW-R2 room gating (RT9 C1–C3).

**The nearest real thing:** a desk FLOW-R. It is a uniform trehalose mote rain in a guarded downward column between a hood and a pedestal, with tracked and gated visible spots. It gives a 0.2 m image for ~$5–12k, and bends "no gas" and "not a table".

## Your task

1. **Attack each of the four pillars** for a loophole the project has not considered. Candidates to weigh, but go beyond them:
   - **Pillar 1.** Media that are not "fog", e.g.:
     - motes that become invisible when unlit, or are reabsorbed or evaporate harmlessly;
     - motes recycled within the image volume;
     - a medium that exists only where the image is.
   - **Pillar 2.** Ways to make drafts irrelevant without a column:
     - motes whose drag-to-control ratio is far better;
     - motes riding on something that does not follow the air;
     - closed-loop room-air control.
   - **Pillar 3.** Safety relaxations that are legitimately consistent with consumer use, e.g.:
     - wavelengths with much higher skin or eye limits;
     - geometry that makes a focus physically inaccessible;
     - self-limiting optics.
   - **Pillar 4.** Addressing with far fewer modes or channels, e.g.:
     - self-organisation;
     - passive traps that need no loop;
     - content structured to match the hardware;
     - commodity devices with unexpectedly large space-bandwidth (consumer projectors, LiDAR, VCSEL arrays, OLED/microLED, MEMS mirror arrays, DMD tiling);
     - compressive or sparse-aperture tricks (beware RT-style traps such as power, sidelobes and loop rate).
2. **Contrarian check.** Is any pillar actually wrong or over-strict? Re-derive one or two of its numbers independently, e.g. B9 under a different safety reading, the home draft statistics, or the per-focus cap.
3. **Desk FLOW-R check.** Does the desk FLOW-R (opus round 4 §5, with 3D tracking, not crossed probes) escape RT9's C1–C3?
   - C1, rate starvation: tracking lights any crossing mote.
   - C2, head aggregation: galvo heads emit 1–4 beams at a time.
   - C3, aim precision: tracking accuracy and latency vs a 40–70 µm aim.

   Give numbers.
4. **Rank** the results: P(physically works) × fit to the vision. For the top idea, give a weeks-scale bench test.

## Rules

- **Evidence:**
  - Physics first: a formula and an order-of-magnitude number for every claim.
  - Tag each claim [MEASURED], [DERIVED], [ESTIMATE] or [SPECULATIVE].
  - Say plainly when an idea fails, and why.
- **Scope:**
  - Check the repo first, and do not re-propose killed routes without a new mechanism that defeats the stated killer.
  - At most 10 web searches.
  - Do not research inhalation dosing or medical topics. Treat particle safety only as the PM and occupational limits already stated in T9 and RT9.
- **Files:**
  - Write the report to `09_unlock/idea_round_5_opus.md`. Scripts may go in the session scratchpad.
  - Do not edit other files, commit, or kill processes.
  - Finish with a summary of at most 400 words.

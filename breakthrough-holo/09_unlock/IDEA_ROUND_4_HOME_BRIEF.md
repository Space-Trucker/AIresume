# Idea round 4: the full vision, buildable at home (brief for independent idea agents)

## The owner's latest instruction

"Continue until you've unlocked the full vision, buildable at home."

**The vision.** Iron Man 1/2 lab holograms:
- touchable;
- floating in open air;
- not a holo-table or holo-wall;
- no glasses, no gases (fog) and no screens; a simple glove is allowed;
- safe for everyday use;
- "just a very sophisticated projector".

Several discreet heads in the room are fine. The owner can build hardware bought online (Amazon/Alibaba) and wants a theory that says it will work.

## What "at home" adds to the earlier rounds

- **Ordinary rooms.** People are present, HVAC may be off but bodies, hands and heads produce plumes.
  - Typical draft at the image: U 0.02–0.1 m/s, σ_u 0.02–0.1 m/s.
  - A warm bare hand's plume is 0.1–0.4 m/s.
- **Child-appealing consumer product.** EN 50689 applies:
  - Class 1 for the eye;
  - **skin MPE through 1 mm over 10 s, i.e. 0.785 mW per focus at 1550 nm** (idea round 3 sonnet, snippet-verified; reproduced by RT8).
- **Cost and buildability** by a skilled hobbyist or startup: commodity parts, no custom fabs.

## What eight red teams established (read `05_reviews/FINAL_VERDICT.md` v5 first)

1. **Light-held motes (photophoresis).**
   - The intensity needed is I ≈ 1.5×10⁷ W/m² per m/s of mote speed relative to air, for a realistic 1 µm skinned mote (RT7 C2). It does not depend on size.
   - **B9.** A static voxel's mean v_rel is ≤ 2·AEL/(π w² h s I_unit). Under the home skin rule that is ~0.6 cm/s at w = 50 µm, and only ~6 cm/s even at w = 15 µm.
   - **Profile instability.** A Gaussian spot that loses force as the mote drifts grows at ~F·4r/w². Holding small spots needs ≥ 20–200 kHz loops (m18c, m19b, RT8).
2. **Moving foci (POV).** These obey the crossing-rate rule, so B9 does not apply.
   - But minimum-power beams run along strokes, which stacks 2.7–9× the AEL into a pupil (RT8 C1).
   - Each channel needs full-field étendue, or a mode multiplexer (RT8 C3).
3. **Visible light.**
   - Uncoated µm motes scatter only forward, so viewers anywhere need 66–220 wall emitters (RT7 C1).
   - Isotropic (white-coated) motes need ≥ ~5 µm radius to keep visible spots within Class 1 at ~3 cd/m² line luminance.
   - Self-luminous motes are pump-limited: the 405 nm photochemical Class 1 limit is 39 µW (v4).
4. **Physics floors** (opus round 3):
   - nothing in air beats thermal creep's force per watt by more than ~2×;
   - ~10 mW per pupil is physiological at 1.4–1.8 µm;
   - acoustic levitation is killed by the beam-cone SPL bound (> 100 dB within 1 m);
   - plasma voxels are killed by noise, ozone and laser class.

## A new lead from the main session to evaluate: "FLOW-X" (the air does the holding)

**The idea.**
- Instead of holding motes against the air with light, let a **conditioned, slow, laminar push–pull air column** carry them: downward, 0.2–0.3 m/s, turbulence intensity 0.1–0.5 %, ~0.6 m square.
- **Injection.** White, non-toxic 5–10 µm motes (e.g. PMMA microspheres) are injected at the top on demand, at the right (x, y) and time. One option is a continuous-inkjet-style droplet generator with electrostatic deflection, whose droplets dry into motes.
- **Motion.** The motes fall through the image volume with the air and are recaptured by the pull inlet below.
- **Lighting.** Cameras track each mote. Visible spots light a mote only while it passes through the content: a persistence-of-vision image whose vertical scan is the air flow itself.
- **Co-moving frame.** In the frame moving with the air the motes are static voxels. A visible holographic engine can therefore be translated rigidly at U by a global scanner, updating only at U / (1 mm) ≈ 300 Hz.

**What it would remove:**
- no IR lasers and no photophoresis;
- no B9, skin-rule or profile-instability problem;
- isotropic white motes;
- slow loops.

**The main session's first-pass questions:**
- dispersion over a 1 m fall: ~1–2 mm at Tu 0.1–0.2 %;
- mote supply: ~6×10⁴–10⁵ motes/s for a sketch, ~2–3×10⁵ in flight;
- particulate escape: needs ≥ 99.9 % recapture for 10 µm motes;
- injection latency: content needs motes ~3 s in advance;
- hand wakes;
- fan noise;
- whether an air column and a floor or table inlet violate "no gas / not a table".

## Your task

1. **Evaluate FLOW-X hard, with numbers.** Kill it or improve it. Cover:
   - laminar column physics in a furnished room with people: core turbulence, shear layers, cross-drafts, thermal plumes, the push–pull stability;
   - mote generation and recapture;
   - visible lighting: Class 1, modes or channels, stray light;
   - touch and hand wakes;
   - noise and comfort;
   - particulate safety;
   - the interactive-content latency;
   - cost and buildability from commodity parts.
2. **Find other routes that beat the home constraints.**
   - The "needle": any physical principle not yet tried, e.g. using the air, gravity, electrostatics, the eye/brain, or the glove, within the vision's rules.
   - For each: the deciding numbers, and which rule (if any) it bends.
3. **Define the nearest *home-buildable* variant of the vision.** State exactly which requirements it relaxes and by how much (image size, viewing zone, brightness, touch behaviour, room conditions), with a parts list class and a cost estimate.

## Rules

- Physics first: every claim gets an order-of-magnitude number and its formula.
- Tag each claim [MEASURED], [DERIVED], [ESTIMATE] or [SPECULATIVE].
- Say plainly when an idea fails, and why.
- Check what the repository already covers (`05_reviews/`, `09_unlock/`, `07_mote_route/`) and do not repeat it.
- At most 10 web searches.
- Output one markdown file at the path given in your task, ending with a ranked list and a weeks-scale bench test for the top idea.

## Addendum: a second lead from the main session, "AIR-SV" (the air holds, light only trims)

Model: `m21_airsv.py`, output in `results/m21_run.log`.

**The tension it resolves** [DERIVED]:
- Holding with light: per-focus power ∝ I(v)·a², so the eye/skin cap gives v_rel ≤ P_cap/(I_unit·a²). This favours small motes.
- Lighting for the eye: modes ∝ A·p/(a²·P_cap). This favours big motes.
- The fix is to let the **air carry the weight**: an **upward** laminar column at U = v_s of size-sorted white beads with a visible-transparent IR skin, e.g. ITO on PMMA or hollow glass, a ≈ 30–40 µm, ρ ≈ 600–1200, U ≈ 0.06–0.2 m/s. Light then only *trims* by ~0.4–2 mm/s.

**What remains for the light to supply.** Trims cover Stokeslet interactions at 3 mm spacing (80 % pre-compensated by design), a 0.1–0.25 % size spread and Tu 0.2 %. That is I ≈ 0.6–3×10⁴ W/m² and **0.04–0.37 mW per focus** (skin-safe), with ΔT of 1–5 K.

**Time-shared pulsed trims.** One galvo IR beam per head visits ~1 000 beads round-robin:
- 0.1 ms dwell, 0.1 s revisit;
- beads drift 40–220 µm between kicks;
- 4–37 µJ per pulse (rule 1: 7.85 mJ);
- kicks heat the bead by 14–29 K;
- the galvo needs 7–10 mm·rad of étendue, which is commodity hardware.

**Visible lighting.** Static holographic spots with w_v ≈ 370–490 µm, about 10× the bead radius, which Class 1 allows. That is ~2–3.5×10⁶ modes per head, i.e. **one 4K LCoS per head**.

**Open problems:**
- **The column against room cross-drafts and people:** a guard flow is probably needed.
- **A warm hand's plume** (0.035–0.4 m/s) is 16–160× the trim authority, so beads above a hand are blown away.
- **Bead placement and content changes are slow** at mm/s trim authority.
- **Collective sedimentation** of bead chains.
- **Bead materials:** an ITO or IR-dye skin on a white body.
- **"Not a table":** the air source sits below the image, in a pedestal or floor vent.

Evaluate AIR-SV with the same rigour as FLOW-X. Compare the two, and say which (if either) is the better home-buildable route.

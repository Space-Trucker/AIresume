# Idea round 3: beat B9 (brief for independent idea agents)

## The goal

The owner wants Iron-Man-lab holograms (Iron Man 1/2):
- touchable;
- floating in open air, from a "very sophisticated projector";
- no screens, glasses or fog/gas (a simple glove is allowed);
- safe for everyday use in a normal home.

Several heads around the room are fine.

## Where the research stands (read `09_unlock/T7_gaussian_voxels.md` and `09_unlock/T6_unlock_theory.md` §1 for detail)

The only route that survived five red teams is **photophoretic motes**: µm absorbing particles held in air by 1550 nm beams, made visible by scattering visible light, with every beam focused from heads around the room.

**The physics is closed for slow content in still air:**
- 1 µm ITO-skin aerogel motes;
- Gaussian spots w ≈ 40–50 µm;
- per-focus mean power ~3 mW, which keeps the worst 3.5 mm pupil within Class 1 (10 mW) after stacking;
- 12–50 W of IR;
- a ≥ 5 kHz phase-modulator loop;
- about 10¹⁰ hologram modes.

**The wall is B9.**
- ΔT-photophoresis needs an intensity at the mote of I = I_unit·v_rel, with I_unit ≈ 5–7×10⁶ W/m² per m/s of mote speed relative to the air. This is bound B2: I = 4ρTv/(3·C·μ·FOM·A·Cc·s_slip). It is **independent of mote size**, and FOM = (J₁/A)/(k_p + 2k_g) ≤ ~7–11 (k_g of air, J₁/A ≤ 0.5–0.75).
- Eye safety at 1550 nm, Class 1, is about 10 mW mean power through a 3.5 mm pupil. A pupil can sit at any focus, and it collects s ≈ 3–5 overlapping beams.
- Per-focus mean power = h·I·πw²/2, with h ≈ 2 (push geometry).
- So **v_rel,mean ≤ 2·AEL/(π w²·h·s·I_unit)**: about 5 cm/s at w = 50 µm, 10 cm/s at 35 µm, 30 cm/s at 20 µm.
- Spots smaller than ~35–50 µm need position loops faster than 10 kHz: the Gaussian profile instability grows at ~F·4r/w². They also hit diffraction at 4 m throws.
- A still room spends ~5 cm/s on drafts: σ_u ≈ 0.03 m/s, mean |u| = 1.6σ. An office spends 15–20 cm/s. A moving hand stirs more. Iron-Man animation needs 0.25–1 m/s.

## Your task

**Find mechanisms or architectures that beat B9 by ≥ 10×**, physically sound and everyday-safe. Attack any factor:
1. **Force per watt in air.** Any light-to-force (or other remotely powered, per-particle-addressable) mechanism in air at 1 atm with ≫ the ΔT-photophoretic force per absorbed watt (~2×10⁻⁵ N/W for a 1 µm mote, scaling as 1/a).
   - Consider: Δα photophoresis; thermal transpiration and Knudsen-pump particles; shaped or Janus particles; negative photophoresis; radiometric vanes; optically switched electrostatics (photo-charging plus room fields); magnetically or acoustically assisted hybrids (the acoustic beam-cone bound gives > 100 dB within 1 m, see T6); evaporative or sublimating micro-rockets; anything else.
   - Give the force per watt with numbers.
2. **Eye-safety basis.** Is there a sound way for a focus to be bright enough while eye-safe without interlocks?
   - Consider: making the focus physically inaccessible; spreading the power over many directions so that no pupil collects it; wavelengths with higher limits (e.g. 1.4–4 µm water bands, or 10.6 µm where the MPE is the same irradiance); pulsed regimes; IEC 60825-1 / ANSI Z136 subtleties (extended sources, C6, time bases).
   - Cite the standard's numbers; check them if you can.
3. **Drafts.** Ways to make the air at the image still without screens or gas: active acoustic or thermal flow control, an image region shielded by laminar air, co-moving frames. Quantify, including noise and comfort.
4. **Architecture.** Ways around the h·s factor, the loop-speed–spot-size coupling, or the ~10¹⁰ hologram modes.

## Rules

- **Physics first.** Every claim gets an order-of-magnitude number, with the formula.
- Mark each claim [MEASURED], [DERIVED], [ESTIMATE] or [SPECULATIVE].
- Say plainly when an idea fails, and why.
- **Check what the research already covers** (T6 §1–3, T7, `05_reviews/`) and do not repeat it. Acoustic levitation, plasma voxels and fog are dead for documented reasons.
- **At most 10 web searches.**
- Output: one markdown file at the path given in your task, with:
  - a ranked list of ideas with numbers;
  - for the top 1–3: a test a lab could run in weeks.

# Idea round 1: break the bottleneck

You are an independent physicist and inventor consulted by a research lab. The lab is designing, *theoretically*, a consumer projector that makes Iron Man-style holograms. The holograms float in open room air, are visible from all around to several people, are touchable (a simple glove is allowed), and need no glasses, fog, gas or screens. It must be safe for everyday indoor use.

## What the lab has established (challenge any of it if you think it is wrong)

1. **Line-of-sight theorem.** In clean air, light reaching an eye from the direction of point P must come from the first opaque surface behind P, unless something *at P* emits or scatters. A projector that only sends light through the air covers ~0.1 % of viewing directions. So light must be created or redirected at P itself, inside the air.
2. **Touch lemma.** Any display whose emitters are on a surface behind the image (walls, tables, plates, light-field panels) is erased by a hand between the image point and that surface. So in-volume emission is needed.
3. **Everything except plasma killed by numbers:**
   - Rayleigh scattering is linear, so a beam glows along its whole length; 1 mm³ at 100 cd/m² needs ~200 W.
   - Coherent nonlinear emission (THG/FWM) is phase-matched forward; side emission is suppressed by 10⁻¹³ or more.
   - Incoherent nonlinear scattering gives ~5 photons per voxel.
   - Microwave/THz breakdown needs kW of RF in the room.
   - Acousto-optics in air is small-angle only (10° needs 112 MHz sound, absorbed in 10 µm).
   - Thermal lensing gives Δn ~ 10⁻⁵.
4. **Laser-induced air plasma is the only strong in-air light source.**
   - Cold femtosecond plasma: ~10⁻⁵ lm per absorbed W (quenched N₂ bands, UV-violet).
   - Hot sparks: ~1 lm/W (continuum). But 50–80 % of absorbed energy goes into a shock wave, and they make ~10¹⁷ NO molecules per absorbed J (O₃ too).
5. **Target (from film analysis).**
   - Strokes of 25–180 cd/m² in a 50–150 lux room.
   - 10⁴–10⁵ points per frame at 60 Hz.
   - ~90 % cyan with orange accents.
   - Noise ≤ 35–40 dB(A).
   - Indoor NO₂ < ~20–50 ppb and O₃ < 50 ppb.
6. **Resulting gap (estimate).**
   - The target needs ~6–60 lm of emitted light.
   - At ~1 lm/W that means 6–60 W absorbed, which makes ~10¹⁸–10¹⁹ NO/s.
   - Staying under the limits would take 10³–10⁴ m³/h of scrubbing.
   - Audible noise is likely far above 35 dB(A).
   - Colour: air plasma gives only violet to white; cyan is not available.

## Your task
Think hard and creatively. Include ideas nobody has tried, and use physics from any field (plasma physics, atmospheric chemistry, nonlinear optics, acoustics, vision science, materials, quantum optics). For each idea give:

- (a) the mechanism in 2–4 sentences;
- (b) a quick order-of-magnitude estimate showing whether it beats the bottleneck;
- (c) the fatal flaw, if any.

Cover at least:
- **A.** More *visible lumens per absorbed joule* from air plasma, per unit of NO/O₃ produced and per unit of shock energy: pulse formats, wavelengths, plasma size and temperature, double pulses, microwave/RF sustainment of laser-seeded plasma, etc.
- **B.** Ways to get *colour* (especially cyan ~490 nm and orange ~600 nm) at a point in ordinary air.
- **C.** Ways to cut *audible noise* from pulsed micro-sparks (scheduling, repetition rate, active cancellation, spark size).
- **D.** Ways to cut or *remove* NO/O₃ (plasma chemistry, catalytic scrubbing, airflow design, recombination).
- **E.** Any loophole in the line-of-sight theorem or the touch lemma, or any other mechanism for making light at a point in clean air that the lab has missed. Include perceptual or vision-science tricks and anything involving the *glove*.
- **F.** Any "grey zone" idea (e.g. particles supplied and recovered by the projector) that could hit the target safely, with its trade-offs.

End with your **top 3 ideas ranked by (probability they work) × (impact)**, and one paragraph of honest verdict: can an Iron Man-quality display in this sense be engineered with known physics under these safety constraints, and if not, what is the closest achievable thing?

Keep it under ~250 lines, dense and quantitative. Don't use web tools; reason from physics you know, and flag uncertain numbers. Write your answer to the file path given in your instructions. Don't run git commands.

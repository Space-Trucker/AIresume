# Aether-M: architecture of a MOTE hologram projector (concept; numbers from `07_mote_route/RESULTS.md`)

**Status:** draft concept. Red team 4 findings will be folded in.

## One-paragraph description

Four compact heads sit around the viewing volume, for example in the room's upper corners or on a ring, 1.5 m from the image. Each head has a 300 mm exit window.

Together they hold roughly 40 motes (accent) up to 1 100 motes (film density). The motes are microscopic, about 2 µm across, and float in invisible 1550 nm beams. The heads sweep them along the image's lines at about 1 m/s, redrawing every line 30–60 times a second. A µW violet beam, focused on each mote, makes its phosphor shell glow Iron-Man cyan, or orange or green for accents.

When unlit, a mote is a speck of dust far below visibility. Lit, it is a moving point of light, and persistence of vision turns the points into glowing lines. There is no fog, screen, glasses, plasma, ozone or noise. A gloved (or bare) hand can reach in: the heads see the hand, route motes around or along it, and the glove gives haptic feedback.

## Blocks

| Block | Function | Key numbers (film density) | Technology basis |
|---|---|---|---|
| Mote cartridge | Stores, dispenses, recaptures and cleans composite motes (low-k carrier + 1550 nm absorber + Eu²⁺ phosphor shell) | ~10³ motes in flight; ~10⁴ per day replaced; micrograms in total | Hollow-silica / aerogel microspheres; phosphor coating (bench item B2) |
| Trap engine (per head) | One 1550 nm channel per mote: fiber-split source → intensity modulator (20 kHz) → coarse + fine 2D steering → focus tracker (2–4 kHz) → shared 300 mm window | ≈ 1 100 channels per head; 0.87 mW per beam; ≤ 0.5 W per head | Telecom 1550 nm parts (EDFA, splitters, VOAs); MEMS / galvo steering; MEMS varifocal |
| Pump engine | One 405 nm channel per mote, co-aligned with one trap channel; tight focus (w ≈ 1.7 µm) with ~17 kHz focus tracking | 36 µW per beam (Class 1 AEL 39 µW) | GaN diodes; the focus tracking is the hard part |
| Sensing | Measures each mote's offset from each beam at 20 kHz with ≤ 0.5 µm precision, from its own 1550 nm back-scatter (quadrant detection per channel) plus a global camera | Photon budget ≈ 10⁷ photons per 50 µs gives nm-level shot-noise precision; the hard part is systematics | Optical-tweezers back-focal-plane detection |
| Controller | Per mote: feed-forward along the planned route, PI feedback, non-negative force allocation across heads, flat-top beam re-centring. Global: content → strokes → mote tour (mote_plan.py) | 20 kHz × 4 500 channels | FPGA/GPU; M2/M2b models |
| Safety | Class 1 by design (per beam and per exit window). Plus: obstruction interlock (µs beam cut when a beam loses its mote), per-channel power monitors, scan/stall watchdog, hand/skin detection | Interlock dose at a focus 0.02 J/cm² (limit 1 J/cm²) | IEC 60825-1:2014; R7 open items must be settled with a notified body |

## Why four heads and not one

- **One head** can push motes only away from itself. Its sideways (gradient) force at room throw is weak (η_lat = 0.75 a/w), so single-head designs top out at 0.25–0.7 m/s.
- **Four heads** can push in any direction with full efficiency, but need fast feedback and cost 4× the channels.
- **A single-head (BYU-type) design** would cut channels about 4×. That depends on a trap efficiency η_single ≳ 0.5 at 1.5 m throw, which no one has measured (bench item B1).

## Staged roadmap (value of information first)

| Stage | Goal | Channels | What it proves |
|---|---|---|---|
| B1 | One mote, one head, 1.5 m throw, NA ≈ 0.1 at 1550 nm (BYU scaled 12× in distance) | 1 | Single-beam 3D trapping at room throw; measured η_single and force per kelvin (C_ph) |
| B2 | Mote engineering: k_p ≤ 0.05, 1550 absorber, cyan phosphor shell, 450 K survival | — | The speed law's inputs; phosphor quenching on a hot mote |
| B3 | One mote, four heads, closed loop ≥ 20 kHz, room air with fans | 4 | Push-trap control, gust rejection, force lag τ_F |
| B4 | One mote drawing a 5 cm glowing cyan circle at 30 Hz | 4–5 | The first MOTE "voxel line"; brightness per mote |
| D1 | "Accent": arc-reactor-sized UI elements, ~40 motes | ~150 | Multi-mote scheduling, hand interaction, Class 1 audit |
| D2 | "Iron-Man sketch", 5 m of strokes | ~750 | The first recognisable Iron Man hologram |
| P | Film density, 30 m | ~4 500 | Needs integrated steering: photonic phased arrays or MEMS arrays with focus |

# Aether-M: architecture of a MOTE hologram projector (concept; numbers from `07_mote_route/RESULTS.md`)

> **v2 update (red team 4 plus the owner's room rig).** This supersedes the numbers in the v1 text below.
>
> **The room ("lab rig", M4).** Twelve small heads (100–300 mm windows):
> - a ring of 6 in a ceiling cove about 1.8 m around the workbench;
> - a low ring of 4 in the bench skirt or floor;
> - one ceiling spot directly above the image and one floor or bench head directly below it.
>
> Throws are 1.2–2.3 m. Each mote uses about 3 heads at a time, chosen and handed over by the workload manager. The rig survives one blocked head in 99 % of cases. Corner-only layouts are 2–7× worse on heat.
>
> **Room requirements:**
> - a quiet-air zone (≤ 0.15 m/s) around the image, e.g. displacement ventilation or a gentle laminar curtain;
> - non-fluorescent surfaces near the beams.
>
> **Engineered motes:** aerogel or core–shell with an island NIR-absorber skin. They do not exist yet; bench item 1 is to make them and measure them.
>
> **Scale in a designed lab at 45 Hz:**
>
> | Target | Motes | Trap beams | 1550 nm total |
> |---|---|---|---|
> | Accent | ~420–500 | ~840–1 000 (passive doughnut pairs, no fast loop) | ~3 W |
> | Iron-Man sketch | ~900–2 200 | ~2 700–4 400 | 8–16 W |
> | Film density | ~3 000–7 600 | ~9 000–15 000 | 33–85 W |
>
> **Software stack (the owner's question: "rendering software, workload management and ...?"):**
> 1. **Content renderer:** models, UI and video become strokes, then mote tours (`holo_engine/mote_plan.py`).
> 2. **Workload manager:** assigns and hands over motes between heads. It balances load, routes around hands and bodies, and enforces the *safety scheduling rule* that no two foci of one head share a 3.5/7 mm line of sight.
> 3. **Real-time control:** a per-channel intensity and steering loop, ≥ 20–50 kHz for push beams; passive pairs need only feed-forward.
> 4. **Room sensing:** mote tracking (per-channel back-scatter plus cameras); hand, head and eye tracking.
> 5. **Calibration:** head poses, beam maps, focus tables; continuous self-calibration from the motes themselves.
> 6. **Safety supervisor:** independent hardware. Accessible-emission sums at the worst points, per-head power monitors, obstruction interlock in about 100 µs, certified fault shutdown.
> 7. **Mote logistics:** dispense, recapture, clean and replace; count lost motes.
> 8. **Interaction:** gesture recognition plus haptic glove.
> 9. **Air manager:** monitors the quiet-air zone and slows or pauses content when drafts exceed the margin.

**Status (v1 text below):** draft concept, superseded where it conflicts with the box above.

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

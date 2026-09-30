# Mission: Iron Man–style touchable holograms from a projector

## The request (verbatim essentials)

> "Research, engineer and run simulation until you hit the jackpot … a fully working project and machine that can show and project holograms just like Iron Man … research on Iron Man 2 holograms scene in lab or Iron Man 1 scene of building armor … Actual touchable holograms … Not holo table not holo wall. Straight up projected and touchable holograms."

Clarifications the owner gave before going to sleep:

> "Research, Engineer fully iron man style holograms. No glasses. These holograms will be able to project complex things. From 3d models to movies to animate, interactive with touch no tools other than the projector. Only thing that the user may need is a simple kind of glove for touch? Exactly I don't want you to build the physical machine but I want you to solve it theoretically. Without needs of gases or screen or glasses etc. I'm thinking just a very sophisticated projector."

> "Maybe as well start a startup if you get me the exact iron man hologram quality product theoretical and engineer it. Then I'll build first projector whether it was running with light + waves or something completely different. Remember it has to be safe for every day usage. Maybe my start up will sell it advertising or put it in helmet like iron man helmet."

> Hardware on hand: a Raspberry Pi. That doesn't matter much, since this is cloud-based theoretical research, engineering and simulation.

> Save the work on a new branch and push it (no pull request).

## Reference frames supplied (in this folder)

| File | Scene | What it shows |
|---|---|---|
| `ref1_ironman1_armor_hologram.jpg` | Iron Man (2008), armor design | Man-sized blue wireframe armor floating in open room air, orange accents, hand manipulation |
| `ref2_ironman2_lab.webp` | Iron Man 2 (2010), lab | Several cyan hologram panels and objects around two people, both see them |
| `ref3_ironman2_city_model.jpg` | Iron Man 2, Expo model | Large green/blue wireframe city model; the owner says this "holo table" form is *not* the goal |
| `ref4_ironman2_periodic_table.jpg` | Iron Man 2, element discovery | Wall-sized grid of translucent tiles; the "holo wall" form is *not* the goal, but the content type (dense UI) is |
| `ref5_ironman2_globe_ui.jpg` | Iron Man 2 | Dense glowing UI: globe, schematics, point markers |

## Formal requirements (what "solved" means)

A *theoretical, engineered and simulated* device design (not a physical build) that satisfies:

| ID | Requirement | Acceptance criterion |
|---|---|---|
| R1 | **Free-space image.** Imagery appears in open room air, not on or behind a surface. | Image points lie in a volume with no screen, table or wall behind them from the viewer's side. |
| R2 | **No eyewear.** | Unaided eyes; any number of viewers. |
| R3 | **No added media.** No fog, gas, mist or screens. | Only ambient room air in the image volume. (Particles supplied and recovered by the projector itself are a grey zone; flagged wherever used.) |
| R4 | **Projector only.** One sophisticated projector unit (it may be ceiling-, wall- or desk-mounted). A simple glove is allowed for touch. | No other room infrastructure required. |
| R5 | **All-around visibility**, like the films: walk around it, and several people see it at once. | Visible over ≥ 2π sr (goal 4π) from any viewer position outside the volume. |
| R6 | **Complex content:** 3D models, animation, movies (video panels), UI. | Renders arbitrary 3D wireframe/point geometry at ≥ 30 Hz, plus a floating video panel. |
| R7 | **Touch interaction:** grab, rotate, poke, feel. | Hand tracking plus tactile feedback (glove allowed); hologram must render correctly in front of or around the hand. |
| R8 | **Safe for everyday use.** | Meets laser (IEC 60825-1 MPE), indoor air (O₃/NO₂), noise and ultrasound, UV, electrical and thermal limits for bystanders with no protective equipment except the optional glove. |
| R9 | **"Iron Man quality."** | Scale ~0.3–2 m, fine line detail (≤ 2 mm), visible brightness in a dim lab, blue/cyan look (orange accents desired), smooth motion. |
| R10 | **Buildable in principle by a startup.** | Every subsystem uses components that exist today or clear, quantified extrapolations; there is a bill of materials and a power budget. |

Grading rule (set before any results, to avoid moving goalposts): a requirement is **MET** only if a simulation or a cited measurement supports it with numbers. **PARTIAL** means it is met under stated restrictions (e.g. a dim room only). **NOT MET** means physics or safety forbids it, and the notebook records why.

Ping the owner only if the design MEETS the spec. If the conclusion is a failure, do not ping (owner's instruction).

# breakthrough-holo: Iron Man holograms, researched to the physical limit

An overnight research lab, run autonomously, answering one question:

> Can a single "very sophisticated projector" make Iron Man-style holograms in open room air, with no glasses, fog or screens, touchable with at most a glove, and safe for everyday use?

**Short answer.** *Iron Man-style*: yes, on paper, with known physics. *Film-exact*: no.

The only way to put light at a point in open air is to spark that point with a focused laser pulse. Sparks are dim, clicky and make trace NO/O₃. That caps a room-safe display at ~5–9 m of glowing strokes, which is enough for a life-size, near-cyan, touchable wireframe in a dim warm-lit room. The film shows 9–57 m of strokes, orange accents and lit-room brightness, and physics puts that out of reach.

Full grading: [`05_reviews/FINAL_VERDICT.md`](05_reviews/FINAL_VERDICT.md).

| Start here | What it is |
|---|---|
| [`00_mission/GOAL.md`](00_mission/GOAL.md) | The request, the reference frames and requirements R1–R10, frozen before any result |
| [`NOTEBOOK.md`](NOTEBOOK.md) | Dated lab notebook: every hypothesis, kill and correction (including my own mistakes) |
| [`02_theory/`](02_theory) | T1: what physics allows (theorem + kills). T2: the light–chemistry–noise trilemma. T3: grey-zone routes. |
| [`03_simulations/`](03_simulations) | 11 simulations, each calibrated against a published number (`python3 run_all.py --fast`) |
| [`04_engineering/`](04_engineering) | Aether-1 architecture, roadmap and experiments, and the runnable `holo_engine` pipeline |
| [`05_reviews/`](05_reviews) | Independent idea rounds (three other models), red team, final verdict |
| [`01_research/`](01_research) | Literature notes with sources: plasma displays, particle displays and haptics, safety limits, film analysis, research methods |

## Key figures (`03_simulations/results/`)

- `e10_feasibility_map.png`: where a pure-air plasma display is safe, against the film target
- `e6c_subsonic_tracing.png`: the drawing method that removes ~20 dB of noise in every direction
- `e11_plasma_color.png`: which colours air plasma can make
- `e7_hazard_zone.png`: laser hazard confined to millimetres around each spark
- `../04_engineering/holo_engine/out/`: previews of the hologram, a hand inside it, and room comparisons

## Reproduce

```bash
pip install numpy scipy matplotlib pillow
cd 03_simulations && python3 run_all.py --fast      # ~3 min (add no flag for the 15-min E6b optimisation)
cd ../04_engineering/holo_engine && python3 demo.py 4 0.5 9 1.8 && python3 compare_rooms.py
```

"""M11: a demonstrator ladder for the startup.

How small can the first impressive MOTE demos be? The étendue floor (R10) scales with field^2, and the beam count with
mote count, so this sizes both.

Ladder (luminance 3-4 cd/m^2, dim room, ITO-aerogel mote, designed-lab L3 levers, 45 Hz):
* D1 'first glyph': a 10 cm circle (0.31 m of stroke), field 0.15 m, heads at ~0.8 m.
* D2 'arc-reactor UI': 1 m of strokes, field 0.3 m, heads at ~1.0 m.
* D3 'desk Jarvis panel': 3 m of strokes, field 0.4 m, heads at ~1.2 m.
* D4 'Iron-Man sketch': 5 m of strokes, field 1.0 m, heads at ~2.0 m.
Modules per head = max(étendue floor f_cov (G/E)^2, active beams per head). G = D_head x field/throw; D_head is set by
w = 10 um at the throw. E = 7 mm rad (10 mm galvo pair). f_cov = 1. 12 heads.
Cost band: $0.7-5k per channel today (R10); $50-250 integrated (5-10 yr).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget2 as b2  # noqa: E402

LEVERS = dict(f=45.0, k_overlap=1.0, k_ov_trap=1.0, whitener_gain=1.0, T_max=600.0, u_air=0.05,
              emitter="cyan_BaSi2O2N2_hiT")
LADDER = {"D1 first glyph (10 cm circle)": (3.0, 0.31, 0.95, 0.15, 0.8),
          "D2 arc-reactor UI (1 m strokes)": (3.0, 1.0, 0.6, 0.30, 1.0),
          "D3 desk Jarvis panel (3 m)": (4.0, 3.0, 0.65, 0.40, 1.2),
          "D4 Iron-Man sketch (5 m)": (3.0, 5.0, 0.57, 1.00, 2.0)}
E, HEADS, W0 = 7.0, 12, 10e-6
out = {}
for name, (L, S, duty, field, throw) in LADDER.items():
    best = None
    for mote in ("ito_aerogel", "ito_coreshell"):
        for arch in ("room_push", "room_pairs"):
            for a in (1.5e-6, 2.5e-6):
                for v in b2.V_GRID:
                    d = b2.design(content=(L, S, duty), a=a, v=v, mote=mote, arch=arch, R_head=0.075, n_pump=2, **LEVERS)
                    if d["feasible"] and (best is None or d["channels"] < best["channels"]):
                        best = d
    D_head = 2 * 1.55e-6 * throw / (math.pi * W0) * 1e3                  # mm, 1/e^2 diameter for w0 = 10 um
    G = D_head * field / throw                                         # mm rad per axis
    floor = (G / E) ** 2
    beams_per_head = best["channels"] / HEADS
    modules = max(floor, beams_per_head)
    total = modules * HEADS
    out[name] = dict(N=best["N"], beams=best["channels"], arch=best["arch"], v=best["v"], D_head_mm=D_head, G=G,
                     etendue_floor_per_head=floor, modules_per_head=modules, modules_total=total,
                     cost_today_M=(total * 0.7e3 / 1e6, total * 5e3 / 1e6), cost_integrated_k=(total * 50 / 1e3, total * 250 / 1e3))
    r = out[name]
    print(f"{name:34s} motes {r['N']:5.0f} beams {r['beams']:5.0f} ({r['arch']}, v {r['v']:.2f}) | head beam {D_head:.0f} mm, "
          f"G {G:.0f} mm rad, floor {floor:.0f}/head -> {total:.0f} modules | today ${r['cost_today_M'][0]:.2f}-{r['cost_today_M'][1]:.1f} M, "
          f"integrated ${r['cost_integrated_k'][0]:.0f}-{r['cost_integrated_k'][1]:.0f} k")
json.dump(out, open(os.path.join(HERE, "results", "m11_demonstrators.json"), "w"), indent=1, default=float)

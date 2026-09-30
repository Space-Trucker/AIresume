"""MOTE planner: turn hologram strokes into mote routes and count the motes an Iron Man scene needs.

The strokes are chained into one closed tour. A greedy nearest-end walk sets the stroke order and direction, and
blanked jumps join one stroke to the next. Motes circulate around the tour at speed v, spaced v/f apart, so every
point of every stroke is revisited once per frame (1/f). This gives
    N = (S + J) f / v,   duty = S / (S + J)
where S is the stroke length and J the jump length. That is exactly the budget formula (N = S f / (v duty)),
with the duty now measured on real content.

Usage: python3 mote_plan.py   -> prints N for the procedural armor at several stroke budgets, speeds and refresh rates
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

import content as c


def chain(strokes):
    """Greedy nearest-end chaining; returns ordered strokes (possibly reversed) and total jump length."""
    rem = [np.asarray(s, float) for s in strokes if len(s) > 1]
    order = [rem.pop(0)]
    J = 0.0
    while rem:
        end = order[-1][-1]
        best, bi, rev = None, None, False
        for i, s in enumerate(rem):
            d0, d1 = np.linalg.norm(s[0] - end), np.linalg.norm(s[-1] - end)
            if best is None or min(d0, d1) < best:
                best, bi, rev = min(d0, d1), i, d1 < d0
        s = rem.pop(bi)
        order.append(s[::-1] if rev else s)
        J += best
    J += float(np.linalg.norm(order[-1][-1] - order[0][0]))
    return order, J


def plan(strokes, v, f):
    S = sum(c.stroke_length(s) for s in strokes)
    _, J = chain(strokes)
    N = (S + J) * f / v
    return dict(S=S, J=J, duty=S / (S + J), N=N, spacing_mm=v / f * 1e3)


if __name__ == "__main__":
    full = c.procedural_armor(height=1.8, slice_step=0.06)
    out = {}
    for budget in (5.0, 9.0, 30.0, None):
        strokes = full if budget is None else c.fit_to_budget(full, budget)[0]
        for v, arch in ((1.14, "push4 a=1um"), (0.37, "single a=5um (eta 0.5)"), (0.47, "lateral2 a=2.5um")):
            for f in (30.0, 60.0):
                p = plan(strokes, v, f)
                key = f"{'full' if budget is None else budget} m | {arch} | {f:.0f} Hz"
                out[key] = p
                print(f"{key:45s} S={p['S']:5.1f} m  jumps={p['J']:5.1f} m  duty={p['duty']:.2f}  N={p['N']:6.0f} motes")
    os.makedirs("out", exist_ok=True)
    with open(os.path.join("out", "mote_plan.json"), "w") as fh:
        json.dump(out, fh, indent=1)

"""M10: how much of the image must each head cover? (R10: steering modules per head >= f_cov (G/E)^2.)

On the M4 'R12 lab rig', restrict each head to a sub-field of the image volume and check two things: every mote position
can still be pushed in every direction (LP feasible), and what the heat factor costs.
Sub-field rules:
* 'all': every head covers the whole image (f_cov = 1).
* 'near k': each head covers only the image grid points for which it is among the k nearest heads.
f_cov is then the mean fraction of grid points a head covers.
Writes results/m10_coverage.json.
"""
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sim_m4_room_heads import CENTER, HALF, LAYOUTS, alloc, fib_sphere, push_dirs  # noqa: E402

heads = np.asarray(LAYOUTS["R12 lab rig (6 ceiling-ring + 4 low-ring + spot + floor)"], float)
grid = [CENTER + HALF * np.array(s) for s in itertools.product((-1, -0.5, 0, 0.5, 1), repeat=3)]
U = fib_sphere(240)
out = {}
for rule in ["all", "near 9", "near 8", "near 7", "near 6", "near 5"]:
    cover = np.ones((len(heads), len(grid)), bool)
    if rule != "all":
        k = int(rule.split()[1])
        for gi, p in enumerate(grid):
            d = np.linalg.norm(heads - p, axis=1)
            keep = np.argsort(d)[:k]
            cover[:, gi] = False
            cover[keep, gi] = True
    hs, infeasible = [], 0
    for gi, p in enumerate(grid):
        D = push_dirs(heads[cover[:, gi]], p)
        for u in U:
            h = alloc(D, u)[0]
            if math.isinf(h):
                infeasible += 1
            else:
                hs.append(h)
    f_cov = float(cover.mean())
    hs = np.array(hs)
    out[rule] = dict(f_cov=f_cov, infeasible_frac=infeasible / (len(grid) * len(U)), h_worst=float(hs.max()),
                     h_mean=float(hs.mean()), h_p95=float(np.percentile(hs, 95)))
    print(f"{rule:7s}: f_cov {f_cov:.2f}, infeasible {100 * out[rule]['infeasible_frac']:.1f} %, h worst {hs.max():.2f} "
          f"p95 {np.percentile(hs, 95):.2f} mean {hs.mean():.2f}", flush=True)
json.dump(out, open(os.path.join(HERE, "results", "m10_coverage.json"), "w"), indent=1)

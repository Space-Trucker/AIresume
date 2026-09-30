"""M6: how opaque must an engineered mote's absorber skin be?

Model: an aerogel core (n ~ 1.05, so rays are nearly straight) with a thin absorbing skin of normal-incidence optical
depth tau at 1550 nm. The front skin absorbs 1 - exp(-tau/cos); the transmitted rest crosses the core and the back
skin absorbs a further fraction, which heats the far side and cancels part of the asymmetry.
J1 = (3/4) M1 / (P a) (surface absorption gives 1/2). Geometric optics only (x = 2 pi a/lambda ~ 4-16 for a = 1-4 um).
Writes results/m6_skin_j1.json.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def j1_skin(tau, n=4000):
    b = (np.arange(n) + 0.5) / n
    c = np.sqrt(1 - b * b)
    w = 2 * b / n
    f1 = 1 - np.exp(-tau / c)
    f2 = np.exp(-tau / c) * (1 - np.exp(-tau / c))
    A = float(np.sum((f1 + f2) * w))
    M1 = float(np.sum((-f1 * c + f2 * c) * w))
    return A, -0.75 * M1 / A


if __name__ == "__main__":
    rows = []
    for tau in (0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0):
        A, j = j1_skin(tau)
        rows.append(dict(tau=tau, A=A, j1A=j, single_pass_normal=1 - np.exp(-tau)))
        print(f"skin optical depth {tau:4.1f} (normal single-pass absorption {100 * (1 - np.exp(-tau)):3.0f} %): "
              f"A = {A:.2f}, J1/A = {j:.3f}")
    json.dump(rows, open(os.path.join(HERE, "results", "m6_skin_j1.json"), "w"), indent=1)

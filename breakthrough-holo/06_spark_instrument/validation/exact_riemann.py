"""Exact Riemann solver for the ideal-gas shock tube (Toro, ch. 4), used by validation V5."""
import math

import numpy as np


def sod_exact(x, t, x0=0.5, L=(1.0, 0.0, 1.0), R=(0.125, 0.0, 0.1), g=1.4):
    rl, ul, pl = L
    rr, ur, pr = R
    cl, cr = math.sqrt(g * pl / rl), math.sqrt(g * pr / rr)

    def f(p, rk, pk, ck):
        if p > pk:
            A, B = 2 / ((g + 1) * rk), (g - 1) / (g + 1) * pk
            return (p - pk) * math.sqrt(A / (p + B))
        return 2 * ck / (g - 1) * ((p / pk) ** ((g - 1) / (2 * g)) - 1)
    lo, hi = 1e-8, 10 * max(pl, pr)
    for _ in range(200):
        p = 0.5 * (lo + hi)
        if f(p, rl, pl, cl) + f(p, rr, pr, cr) + ur - ul > 0:
            hi = p
        else:
            lo = p
    ps = 0.5 * (lo + hi)
    us = 0.5 * (ul + ur) + 0.5 * (f(ps, rr, pr, cr) - f(ps, rl, pl, cl))
    rsl = rl * (ps / pl) ** (1 / g)
    rsr = rr * ((ps / pr + (g - 1) / (g + 1)) / ((g - 1) / (g + 1) * ps / pr + 1))
    Ssr = ur + cr * math.sqrt((g + 1) / (2 * g) * ps / pr + (g - 1) / (2 * g))
    csl = cl * (ps / pl) ** ((g - 1) / (2 * g))
    rho = np.empty_like(x)
    for i, xi in enumerate(x):
        s = (xi - x0) / t
        if s < ul - cl:
            rho[i] = rl
        elif s < us - csl:
            rho[i] = rl * (2 / (g + 1) + (g - 1) / ((g + 1) * cl) * (ul - s)) ** (2 / (g - 1))
        elif s < us:
            rho[i] = rsl
        elif s < Ssr:
            rho[i] = rsr
        else:
            rho[i] = rr
    return rho

"""M8b: independent hand recomputation of one M8 floor design (owner rule 12: double-validate).

Recomputes the sketch push design (ito_aerogel, a = 1.5 um, v = 0.64 m/s, u_air = 0.05, 45 Hz, R12 rig) from first
principles. It uses only the air-property primitives in physics.py, not budget2.design. The heat balance is solved by
its own bisection, and the photophoretic force is written out from the creep formula
F = 4 pi C_s mu^2 T1 / (rho T), T1 = (J1/A) P_abs / (pi a (k_eff + 2 k_g)), with C_s = 9/8 (C_ph = 1).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import physics as ph  # noqa: E402

a, v, u, margin, f, S, duty = 1.5e-6, 0.64, 0.05, 1.3, 45.0, 5.0, 0.57
j1A, k_eff, A = 0.486, 0.04, 1.0
h_worst, single, beams = 2.22, 1.19, 3
p_over_R = ph.P0 / ph.R_AIR


def solve():
    Tm = 400.0
    for _ in range(200):
        Tf = 0.5 * (ph.T0 + Tm)
        mu, kg = ph.mu_air(Tf), ph.k_air(Tf)
        Re = ph.rho_air(Tf) * (v + u) * 2 * a / mu
        F = margin * 6 * math.pi * mu * a * (v + u) * (1 + 3 / 16 * Re) / ph.cunningham(a, Tf)
        # force per absorbed W, written out: F = 4 pi (9/8) mu^2 / (rho T) * j1A * P / (pi a (k + 2kg)) * slip
        kn = ph.mfp(Tf) / a
        slip = 1 / ((1 + 3 * 1.14 * kn) * (1 + 2 * 2.18 * kn * k_eff / (k_eff + 2 * kg)))
        fpw = 4 * math.pi * 1.125 * mu ** 2 / p_over_R * j1A / (math.pi * a * (k_eff + 2 * kg)) * slip
        P_F = F / fpw
        heat = P_F * h_worst                       # pump heat is small here (~uW); added below
        # own bisection for the conduction + jump + radiation balance
        lo, hi = ph.T0, 3000.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            Tfm = 0.5 * (ph.T0 + mid)
            zeta = 2 * 1.4 / 2.4 * ph.mfp(Tfm) / 0.71
            loss = 4 * math.pi * a * ph.k_integral(mid) / (1 + zeta / a) * (1 + min(Re * 0.71, 1) / 4) \
                + 0.9 * ph.SIGMA * 4 * math.pi * a * a * (mid ** 4 - ph.T0 ** 4)
            lo, hi = (mid, hi) if loss < heat + 6e-6 else (lo, mid)
        Tm_new = 0.5 * (lo + hi)
        if abs(Tm_new - Tm) < 1e-3:
            break
        Tm = 0.5 * (Tm + Tm_new)
    T1 = j1A * P_F * single / (math.pi * a * (k_eff + 2 * kg))
    return Tm, Tm + T1, P_F


Tm, Tface, P_F = solve()
N = S * f / (v * duty)
print(f"independent: T_mean {Tm:.0f} K, T_face {Tface:.0f} K, N {N:.0f}, channels {beams * N:.0f}, P_F {P_F * 1e6:.1f} uW")
print("M8 reported: T_face 488 K, N 615, channels 1845")

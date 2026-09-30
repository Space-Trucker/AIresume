"""E5b: Does it matter WHICH molecules the sparks make? NO vs NO2 vs O3 speciation and indoor
kinetics, as a lever on the stroke budget (idea-round reviewers, Opus #2 and Sonnet D1).

Box model (well-mixed room + the same near-field plume factor as E5 applied to primary emissions):
  d[NO]/dt  = S*fNO  - k[NO][O3] - L_NO[NO]
  d[NO2]/dt = S*fNO2 + k[NO][O3] - L_NO2[NO2]
  d[O3]/dt  = S*fO3  + ach*[O3]_out - k[NO][O3] - (L_O3 + scrubber)[O3]
k(NO+O3) = 1.9e-14 cm^3/s at 298 K (JPL/IUPAC evaluations). Outdoor O3 = 40 ppb, indoor surface
loss: O3 3/h, NO2 0.5/h, NO ~0 (ventilation only). Scrubber (MnO2 + KMnO4/alumina + carbon)
removes O3 at 85 % and NO2 at 70 % of CADR, NO at 20 %.
Limits used: NO2 <= 13 ppb (WHO 24-h), O3 <= 20 ppb increment (Health Canada 8-h), NO <= 300 ppb
(well below EU 8-h OEL 2 ppm, conservative for the public).
Output: allowed absorbed power (W) for each speciation scenario -> multiplier vs the 'all NO2' rule.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from holo_common import N_AIR, save_json
from display_budget import P

K_NO_O3 = 1.9e-14 * 1e-6          # m^3/s
V, ACH, CADR, CAP = 50.0, 0.5, 900.0, 0.9


def steady(P_abs, fNO, fNO2, fO3, Y=None, t_end=6 * 3600):
    Y = P("Y_react") if Y is None else Y
    S = Y * P_abs * (1 - CAP) / V                                  # molecules/m^3/s into the room
    kv = ACH / 3600
    sc = CADR / 3600 / V
    O3_out = 40e-9 * N_AIR

    def f(t, y):
        no, no2, o3 = y
        r = K_NO_O3 * no * o3
        return [S * fNO - r - (kv + 0.2 * sc) * no,
                S * fNO2 + r - (kv + 0.5 / 3600 + 0.7 * sc) * no2,
                S * fO3 + kv * O3_out - r - (kv + 3 / 3600 + 0.85 * sc) * o3]
    o3_0 = kv * O3_out / (kv + 3 / 3600 + 0.85 * sc)
    sol = solve_ivp(f, (0, t_end), [0, 0, o3_0], method="LSODA", rtol=1e-6, atol=1e3)
    no, no2, o3 = sol.y[:, -1] / N_AIR * 1e9
    # near-field plume increment at a face 0.5 m away (E5, D_t = 0.005 m^2/s) for primary emissions
    nf = Y * P_abs * (1 - CAP) / (4 * math.pi * 0.005 * 0.5) / N_AIR * 1e9
    return dict(NO=no + nf * fNO, NO2=no2 + nf * fNO2, O3_increment=(o3 - o3_0 / N_AIR * 1e9) + nf * fO3,
                O3_background=o3_0 / N_AIR * 1e9)


def allowed_power(fNO, fNO2, fO3):
    lo, hi = 1e-3, 1e3
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        s = steady(mid, fNO, fNO2, fO3)
        ok = s["NO2"] <= 13 and s["O3_increment"] <= 20 and s["NO"] <= 300
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo, steady(lo, fNO, fNO2, fO3)


if __name__ == "__main__":
    print("E5b NOx speciation lever")
    scen = {
        "worst: all NO2": (0.0, 1.0, 0.0),
        "cold-plasma-like (filament data): 70% O3, 25% NO2, 5% NO": (0.05, 0.25, 0.70),
        "mixed: 50% NO, 20% NO2, 30% O3": (0.5, 0.2, 0.3),
        "hot-spark-like: 90% NO, 7% NO2, 3% O3": (0.9, 0.07, 0.03),
    }
    out = {}
    base = None
    for name, (a, b, c) in scen.items():
        Pw, s = allowed_power(a, b, c)
        base = base or Pw
        out[name] = dict(allowed_P_abs_W=Pw, multiplier=Pw / base, at_limit=s)
        print(f"  {name:58s} allowed absorbed power {Pw:6.2f} W (x{Pw/base:4.1f}); at limit NO {s['NO']:.0f}, "
              f"NO2 {s['NO2']:.1f}, dO3 {s['O3_increment']:.1f} ppb")
    save_json("e5b_nox_speciation.json", out)
    print("  -> if micro-sparks emit mostly NO (experiment X2), the chemistry budget grows several-fold;"
          " if they behave like cold filaments (mostly O3), it shrinks.")

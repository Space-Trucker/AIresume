"""E13: Do MORE PROJECTORS help? (owner question after verdict v2)

New question, not covered by existing runs: E12 tiled the volume with K heads for etendue, but
did not ask whether K changes the minimum laser/absorbed power of a quiet display.

Model (all inputs from earlier runs):
  * Each head covers field F/sqrt(K) with N resolvable spots per axis (E12), so its NA and the
    breakdown energy are E_bd = I_th * pi * w0^2 * tau, w0 = F / (2 N sqrt(K)).
  * Subsonic tracing (E6c, red team #7) needs every head to fire a regular train >= f_min = 35 kHz,
    so the total voxel rate is >= K * f_min.
  * => minimum incident power P_min = K f_min E_bd = pi I_th tau f_min F^2 / (4 N^2):
    INDEPENDENT of K (analytic). Checked numerically below, and the absorbed fraction at each
    operating point is taken from the lab's plasma model (E3, plasma_model.simulate_voxel).
Compared with the realistic strict-air budget of ~0.4-1 W absorbed (red team #9, E10b).
"""
import math

from holo_common import save_json
from plasma_model import simulate_voxel

LAM, I_TH, TAU, F_MIN, FIELD = 1.55e-6, 5e17, 0.3e-12, 35e3, 1.0
MIRRORS = {"30 mm galvo, +-20 deg": 0.030 * 0.70 / LAM, "50 mm galvo, +-15 deg": 0.050 * 0.52 / LAM}

if __name__ == "__main__":
    print("E13 multiple projectors: minimum power of a quiet, room-scale plasma display")
    out = {}
    for name, N in MIRRORS.items():
        analytic = math.pi * I_TH * TAU * F_MIN * FIELD ** 2 / (4 * N ** 2)
        rows = []
        for K in (1, 4, 9, 16, 25):
            w0 = FIELD / (2 * N * math.sqrt(K))
            NA = LAM / (math.pi * w0)
            E_bd = I_TH * math.pi * w0 ** 2 * TAU
            P_inc = K * F_MIN * E_bd
            v = simulate_voxel(1.2 * E_bd, LAM, NA, TAU)          # 20 % above threshold
            P_abs = K * F_MIN * v["E_dep"]
            rows.append(dict(K=K, NA=NA, E_bd_uJ=E_bd * 1e6, P_inc_W=P_inc, abs_frac=v["abs_frac"],
                             P_abs_W=P_abs, plasma_len_um=v["plasma_len"] * 1e6))
            print(f"  {name:22s} K={K:2d}: NA {NA:.3f}, spark {E_bd*1e6:6.1f} uJ, min rate {K*F_MIN/1e3:5.0f} k/s, "
                  f"P_inc {P_inc:5.1f} W (analytic {analytic:5.1f}), absorbed {v['abs_frac']*100:4.1f}% -> P_abs {P_abs:5.2f} W")
        out[name] = dict(N_per_axis=N, P_inc_min_analytic_W=analytic, rows=rows)
    save_json("e13_multi_projector.json", out)
    print("  -> incident-power floor is the same for any number of projectors; only bigger scanner etendue lowers it (1/N^2).")
    print("  -> sparks just above threshold absorb only 0.2-3 % (E3 model, a lower bound) and are far dimmer than a")
    print("     visible stroke needs (~5 uJ absorbed each, E10). So absorbed power is set by the light wanted,")
    print("     P_abs = lumens / eta, which does not depend on how many projectors deliver it. Chemistry, UV and")
    print("     the noise floor scale with P_abs, so multiple projectors leave the E10b verdict unchanged.")

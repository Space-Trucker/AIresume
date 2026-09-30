"""M1c: MOTE atlas with a focus-tracking technology constraint (added after M3 showed that focus tracking, not
lateral steering, is the hardest per-channel requirement).

Scenarios for the per-beam focus bandwidth B_focus:
* ideal (no limit);
* 100 kHz (acousto-optic lens, 4 AODs per channel);
* 20 kHz;
* 5 kHz (MEMS varifocal mirror).
For each content target and scenario, report the design with the fewest steering channels.
Writes results/m1c_focus_scenarios.json.
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget as bd  # noqa: E402
from sim_m1_atlas import V_GRID  # noqa: E402

SCEN = {"ideal": None, "AOL_100kHz": 1e5, "20kHz": 2e4, "MEMS_5kHz": 5e3}
out = {}
for content in ("accent", "sketch", "film_contrast", "film_density", "film_exact"):
    out[content] = {}
    for sname, B in SCEN.items():
        best = None
        for arch, (em, lp), a, R, eta in itertools.product(
                ["push4", "push6", "lateral2", "single"],
                [("phosphor:cyan_BaSi2O2N2", 405), ("uc:Er_green_red_Yb98", 980)],
                [1e-6, 2.5e-6, 5e-6], [0.05, 0.15, 0.3], [0.5]):
            if arch != "single" and R == 0.3:
                continue
            for v in V_GRID:
                d = bd.design(content=content, v=v, arch=arch, emitter=em, pump_lam=lp if em.startswith("phos") else 405,
                              a=a, kp=0.02, R_head=R, u_air=0.2, T_max=450.0, B_focus=B, eta_single=eta)
                if d["feasible"] and (best is None or d["channels"] < best["channels"]):
                    best = dict(d, R_head=R)
        out[content][sname] = best
        if best:
            print(f"{content:14s} {sname:11s} {best['arch']:8s} {best['emitter'][:14]:14s} a={best['a_um']:.1f} "
                  f"R={best['R_head']} v={best['v']:.2f} N={best['N']:.0f} ch={best['channels']:.0f} "
                  f"w_t={best['w_trap_um']:.1f} w_p={best['w_pump_um']:.1f} um trap {best['P_trap_total_W']:.2f} W", flush=True)
        else:
            print(f"{content:14s} {sname:11s} NONE feasible", flush=True)
with open(os.path.join(HERE, "results", "m1c_focus_scenarios.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=float)

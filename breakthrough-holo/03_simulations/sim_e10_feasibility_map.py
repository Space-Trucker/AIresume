"""E10: Feasibility map of a pure-air plasma hologram display, with literature uncertainty.

For each stroke luminance L (cd/m^2) and number of points per frame n (60 Hz):
  absorbed power, room O3+NOx increment (ppb), audible noise (dB(A)), under
    - 'baseline' : well-mixed 50 m^3 room, 0.5 ACH, built-in 400 m^3/h scrubber at 70 %
    - 'engineered': plus 90 % local capture (push-pull airflow through the image volume),
                    900 m^3/h at 85 %, and acoustic phase scheduling gain from E6b
Monte Carlo over the literature bands in display_budget.PARAMS gives P(feasible) at the
Iron Man target and at a 'dim-lab Iron-Man-style' target.
"""
import json
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import RESULTS, save_json
from display_budget import PARAMS, display_budget

rng = np.random.default_rng(3)

ROOM_BASE = dict(room_m3=50.0, ach=0.5, cadr_m3h=400.0, scrub_eff=0.7, capture=0.0, decay_per_h=0.5)
ROOM_ENG = dict(room_m3=50.0, ach=0.5, cadr_m3h=900.0, scrub_eff=0.85, capture=0.9, decay_per_h=0.5)


def scheduling_gain_db():
    p = os.path.join(RESULTS, "e6b_multilistener.json")
    if os.path.exists(p):
        res = json.load(open(p))
        # use the 4-listener case, worst tracked listener (conservative)
        for r in res:
            if r["M"] == 4:
                return float(np.max(r["tracked_after"]))
    return -26.0 + 10  # fallback: single-listener gain degraded by 10 dB


def sample_params():
    sc = {}
    for k, (nom, lo, hi) in PARAMS.items():
        sc[k] = float(math.exp(rng.uniform(math.log(lo), math.log(hi))))
    return sc


def evaluate(L, n, room, sched_db, sc=None, A=20.0):
    """sched_db applies to the DIRECT field only (reflections are not controllable)."""
    return display_budget(L, n, sc=sc, room=room, direct_gain_db=sched_db, room_absorption_m2=A)


if __name__ == "__main__":
    print("E10 feasibility map")
    sched = scheduling_gain_db()
    print(f"  acoustic phase-scheduling gain used: {sched:+.1f} dB (worst tracked listener, 4 tracked)")
    Ls = np.logspace(0, np.log10(200), 40)
    ns = np.logspace(2, 5, 40)
    maps = {}
    for tag, room in (("baseline", ROOM_BASE), ("engineered", ROOM_ENG)):
        ppb = np.zeros((len(Ls), len(ns)))
        dba = np.zeros_like(ppb)
        pw = np.zeros_like(ppb)
        for i, L in enumerate(Ls):
            for j, n in enumerate(ns):
                b = evaluate(L, n, room, sched if tag == "engineered" else 0.0)
                ppb[i, j] = b["ppb"]
                dba[i, j] = b["dBA_sched"]
                pw[i, j] = b["P_abs"]
        maps[tag] = (ppb, dba, pw)

    # Monte Carlo at targets
    targets = {
        "Iron Man lit lab (50 cd/m2, 3e4 pts)": (50.0, 3e4),
        "Iron Man dim lab (10 cd/m2, 1e4 pts)": (10.0, 1e4),
        "Iron-Man-style dim (3 cd/m2, 5e3 pts)": (3.0, 5e3),
        "Sparse accent layer (3 cd/m2, 1e3 pts)": (3.0, 1e3),
    }
    mc = {}
    for name, (L, n) in targets.items():
        ok_b = ok_e = safe_e = 0
        rows = []
        for _ in range(400):
            sc = sample_params()
            b1 = evaluate(L, n, ROOM_BASE, 0.0, sc)
            b2 = evaluate(L, n, ROOM_ENG, sched, sc)
            ok_b += (b1["ppb"] <= 20) and (b1["dBA_sched"] <= 45)
            ok_e += (b2["ppb"] <= 20) and (b2["dBA_sched"] <= 45)
            safe_e += (b2["ppb"] <= 50) and (b2["dBA"] <= 85) and (b2["ultrasound_band_dB"] <= 100)
            rows.append((b2["ppb"], b2["dBA_sched"], b2["P_abs"]))
        rows = np.array(rows)
        nom_b = evaluate(L, n, ROOM_BASE, 0.0)
        nom_e = evaluate(L, n, ROOM_ENG, sched)
        mc[name] = dict(L=L, n=n, P_feasible_baseline=ok_b / 400, P_feasible_engineered=ok_e / 400,
                        P_safe_engineered=safe_e / 400,
                        nominal_baseline=nom_b, nominal_engineered=nom_e,
                        engineered_ppb_p10_p50_p90=np.percentile(rows[:, 0], [10, 50, 90]).tolist(),
                        engineered_dBA_p10_p50_p90=np.percentile(rows[:, 1], [10, 50, 90]).tolist(),
                        engineered_Pabs_p10_p50_p90=np.percentile(rows[:, 2], [10, 50, 90]).tolist())
        print(f"  {name:42s} nominal: P_abs={nom_e['P_abs']:.2f} W, lm={nom_e['lumens']:.2f}, "
              f"baseline {nom_b['ppb']:.0f} ppb/{nom_b['dBA']:.0f} dB(A); engineered {nom_e['ppb']:.1f} ppb/"
              f"{nom_e['dBA_sched']:.0f} dB(A), US {nom_e['ultrasound_band_dB']:.0f} dB | P(QUIET: <=20 ppb, <=45 dB(A)) base {ok_b/400:.2f}, "
              f"eng {ok_e/400:.2f} | P(SAFE: <=50 ppb, <=85 dB(A), US<=100 dB) eng {safe_e/400:.2f}")
    save_json("e10_feasibility.json", dict(scheduling_gain_dB=sched, monte_carlo=mc))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, tag in zip(axes, ("baseline", "engineered")):
        ppb, dba, pw = maps[tag]
        X, Y = np.meshgrid(ns, Ls)
        ok = (ppb <= 50) & (dba <= 85)
        ax.contourf(X, Y, ok.astype(float), levels=[-0.5, 0.5, 1.5], colors=["#f3d9d9", "#d4ecd4"])
        c1 = ax.contour(X, Y, ppb, levels=[20, 50], colors="#b03030", linestyles=["-", "--"])
        ax.clabel(c1, fmt=lambda v: f"{v:.0f} ppb", fontsize=7)
        c2 = ax.contour(X, Y, dba, levels=[45, 55, 85], colors="#3050b0", linestyles=[":", "--", "-"])
        ax.clabel(c2, fmt=lambda v: f"{v:.0f} dB(A)", fontsize=7)
        ax.add_patch(plt.Rectangle((1e4, 25), 9e4, 155, fill=False, ec="k", lw=1.5))
        ax.text(1.1e4, 150, "Iron Man\n(film, lit lab)", fontsize=8)
        ax.add_patch(plt.Rectangle((3e3, 2), 7e3, 8, fill=False, ec="k", lw=1, ls=":"))
        ax.text(3.1e3, 1.3, "dim-lab style", fontsize=7)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("points per frame (60 Hz)")
        ax.set_title(f"{tag}: green = SAFE (<=50 ppb, <=85 dB(A))", fontsize=9)
    axes[0].set_ylabel("stroke luminance (cd/m²)")
    plt.tight_layout(); plt.savefig(f"{RESULTS}/e10_feasibility_map.png", dpi=120); plt.close()
    print("  saved results/e10_feasibility.json and e10_feasibility_map.png")

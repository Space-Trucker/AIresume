"""M1: MOTE design atlas (v2: forward diffraction counted in wall light; BYU-regime single-head architecture added). For every content target x trap architecture x emitter x mote size x k_p x head aperture,
find the fastest feasible trace speed. Feasible means all of:
* mote heating <= T_max;
* Class 1 per beam and at each head's exit window, for the trap and for the emitter pump;
* stray pump/visible light on the walls <= 5 % of the image flux.
Then report the design that needs the fewest steering channels (N x heads).

Writes results/m1_atlas.json and results/m1_best.json; prints the summary per content target.
"""
import itertools
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget as bd  # noqa: E402

V_GRID = [0.05 * 1.25 ** k for k in range(21)]            # 0.05 ... 4.3 m/s
EMITTERS = [("phosphor:cyan_BaSi2O2N2", 405), ("phosphor:cyan_BaSi2O2N2", 450), ("uc:Er_green_red_Yb98", 980),
            ("scatter", 488)]
KEEP = ["content", "arch", "emitter", "a_um", "kp", "v", "N", "dT", "P_beam_mW", "P_trap_total_W", "P_head_W",
        "head_limit_W", "P_pump_beam_uW", "ael_pump_uW", "P_pump_total_mW", "wall_ratio", "channels", "n_axis",
        "w_trap_um", "lm_per_mote", "fails", "feasible"]


def best_for(**kw):
    best, last = None, None
    for v in V_GRID:
        d = bd.design(v=v, **kw)
        last = d
        if d["feasible"]:
            best = d
    return best, last


if __name__ == "__main__":
    t0 = time.time()
    rows = []
    for content in bd.CONTENT:
        for arch, (em, lam_p), a, kp, R in itertools.product(["single", "lateral2", "push4", "push6"], EMITTERS,
                                                             [0.5e-6, 1e-6, 2.5e-6, 5e-6], [0.02, 0.1, 0.5],
                                                             [0.05, 0.10, 0.15]):
            best, last = best_for(content=content, arch=arch, emitter=em, pump_lam=lam_p if em.startswith("phos") else 405,
                                  scatter_lam=lam_p, a=a, kp=kp, R_head=R, u_air=0.2, T_max=450.0)
            d = best or bd.design(v=0.05, content=content, arch=arch, emitter=em,
                                  pump_lam=lam_p if em.startswith("phos") else 405, scatter_lam=lam_p, a=a, kp=kp,
                                  R_head=R, u_air=0.2, T_max=450.0)
            row = {k: d[k] for k in KEEP}
            row.update(R_head=R, pump_lam=lam_p)
            rows.append(row)
        print(f"{content} done ({time.time() - t0:.0f} s)", flush=True)
    with open(os.path.join(HERE, "results", "m1_atlas.json"), "w") as fh:
        json.dump(rows, fh, indent=0, default=float)
    summary = {}
    for content in bd.CONTENT:
        rs = [r for r in rows if r["content"] == content]
        feas = [r for r in rs if r["feasible"]]
        causes = Counter(c for r in rs if not r["feasible"] for c in r["fails"])
        by_em = {}
        for r in feas:
            key = f"{r['emitter']}@{r['pump_lam']}"
            if key not in by_em or r["channels"] < by_em[key]["channels"]:
                by_em[key] = r
        best = min(feas, key=lambda r: (r["channels"], r["P_trap_total_W"])) if feas else None
        summary[content] = dict(n=len(rs), n_feasible=len(feas), fail_causes=dict(causes), best=best, best_by_emitter=by_em)
        print(f"\n== {content}: {len(feas)}/{len(rs)} feasible; fail causes {dict(causes)}")
        for key, r in by_em.items():
            print(f"   {key:32s} {r['arch']:8s} a={r['a_um']:.1f} kp={r['kp']} R={r['R_head']} v={r['v']:.2f} N={r['N']:.0f} "
                  f"ch={r['channels']:.0f} dT={r['dT']:.0f} trap {r['P_trap_total_W']:.2f} W ({r['P_beam_mW']:.2f} mW/beam) "
                  f"pump {r['P_pump_beam_uW']:.1f}/{r['ael_pump_uW']:.0f} uW wall {r['wall_ratio']:.3f}")
    with open(os.path.join(HERE, "results", "m1_best.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=float)

"""M8: the floor. How far can every known lever push the MOTE channel count?

Levers, each tied to a fact or a validated model:
* mote: M7-validated ITO-class skin. 'ito_aerogel' (FOM ~5.3) and 'ito_coreshell' (FOM ~4.6, bright pump core).
* temperature: the hot face may reach 600 K. ITO loses free carriers above ~620 K in air (R9). The phosphor quench T50
  is 520 K (baseline) or 650 K (R9 snippet: BaSi2O2N2 quench onset near 450 C).
* air: a gentle, steady (laminar) flow through the image zone. The swarm measures the mean flow and the controller
  cancels it (feed-forward), so the margin only has to cover the fluctuation, 0.05 m/s (laminar) or 0.15 m/s.
* refresh 45 Hz; R12 lab rig; safety-aware scheduling; non-fluorescent surfaces (as in S4).
For each content target, report the fewest channels over a = 1-2.5 um, head window R = 75-150 mm, push / passive pairs.
Writes results/m8_levers.json.
"""
import itertools
import json
import os
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget2 as b2  # noqa: E402

BASE = dict(f=45.0, k_overlap=1.0, k_ov_trap=1.0, whitener_gain=1.0)
SCEN = {
    "L0 designed lab (S4), ITO skin": dict(T_max=500.0, u_air=0.15, emitter="cyan_BaSi2O2N2"),
    "L1 + hot face 600 K": dict(T_max=600.0, u_air=0.15, emitter="cyan_BaSi2O2N2"),
    "L2 + hot phosphor (T50 650 K)": dict(T_max=600.0, u_air=0.15, emitter="cyan_BaSi2O2N2_hiT"),
    "L3 + laminar zone (0.05 m/s fluct.)": dict(T_max=600.0, u_air=0.05, emitter="cyan_BaSi2O2N2_hiT"),
}


def cell(args):
    content, sname, mote, arch, a, R = args
    best = None
    for v in b2.V_GRID:
        d = b2.design(content=content, a=a, v=v, mote=mote, arch=arch, R_head=R, n_pump=2, **BASE, **SCEN[sname])
        if d["feasible"]:
            best = d
    if best:
        best = {k: best[k] for k in ("content", "mote", "arch", "a_um", "v", "N", "channels", "T_face", "P_beam_mW",
                                     "P_trap_total_W", "P_pump_beam_uW", "wall_ratio")}
        best.update(scenario=sname, R_head=R)
    return best


if __name__ == "__main__":
    jobs = list(itertools.product(list(b2.CONTENT), list(SCEN), ["ito_aerogel", "ito_coreshell"],
                                  ["room_push", "room_pairs"], [1e-6, 1.5e-6, 2.5e-6], [0.075, 0.1, 0.15]))
    with Pool(4) as pool:
        rows = [r for r in pool.map(cell, jobs, chunksize=6) if r]
    json.dump(rows, open(os.path.join(HERE, "results", "m8_levers.json"), "w"), indent=0, default=float)
    for content in b2.CONTENT:
        for sname in SCEN:
            for arch in ("room_push", "room_pairs"):
                rs = [r for r in rows if r["content"] == content and r["scenario"] == sname and r["arch"] == arch]
                if rs:
                    r = min(rs, key=lambda r: r["channels"])
                    print(f"{content:13s} | {sname:36s} | {arch:10s} {r['mote']:13s} a={r['a_um']:.1f} R={r['R_head']} "
                          f"v={r['v']:.2f} N={r['N']:6.0f} ch={r['channels']:6.0f} Tface={r['T_face']:.0f} "
                          f"trap {r['P_trap_total_W']:.1f} W beam {r['P_beam_mW']:.1f} mW pump {r['P_pump_beam_uW']:.1f} uW")
                else:
                    print(f"{content:13s} | {sname:36s} | {arch:10s} none")

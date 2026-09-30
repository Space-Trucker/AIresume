"""M5: corrected MOTE atlas (budget2: red-team-4 corrections + the owner's room head array, 'R12 lab rig').

Grid:
* content: the five targets;
* mote class: coreshell / engineered / optimistic / dense;
* architecture: room_push (active) / room_pairs (passive LG01);
* mote radius a: 1-4 um;
* head window radius R: 75-150 mm;
* scenario (S4/S5 added after the S0-S3 run: a designed lab):
  - S0 baseline: 60 Hz, 0.3 m/s air, T_face <= 450 K;
  - S1 quiet-air zone: 0.15 m/s;
  - S2 hot phosphor: T_face <= 500 K;
  - S3: S1 + S2 at 45 Hz.
For each (content, mote, scenario), report the feasible design with the fewest trap channels, and the fail causes.
Writes results/m5_atlas_v2.json.
"""
import itertools
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget2 as b2  # noqa: E402

SCEN = {"S0 baseline 60Hz u0.3 T450": dict(f=60.0, u_air=0.3, T_max=450.0),
        "S1 quiet-air u0.15": dict(f=60.0, u_air=0.15, T_max=450.0),
        "S2 hot T500": dict(f=60.0, u_air=0.3, T_max=500.0),
        "S3 quiet+hot 45Hz": dict(f=45.0, u_air=0.15, T_max=500.0),
        # designed lab: quiet-air zone, hot-tolerant phosphor, safety-aware scheduling (no two foci of one head on a
        # 3.5/7 mm line of sight, so no beam overlap: k_overlap = 1), non-fluorescent room surfaces (brightener gain 1)
        "S4 designed lab 45Hz": dict(f=45.0, u_air=0.15, T_max=500.0, k_overlap=1.0, k_ov_trap=1.0, whitener_gain=1.0),
        "S5 designed lab 60Hz": dict(f=60.0, u_air=0.15, T_max=500.0, k_overlap=1.0, k_ov_trap=1.0, whitener_gain=1.0)}
MOTES = ["coreshell", "engineered", "optimistic", "dense"]
KEEP = ["content", "mote", "arch", "a_um", "v", "f", "N", "channels", "pump_channels", "eta", "T_face", "dT", "w_trap_um",
        "P_beam_mW", "P_trap_total_W", "P_head_W", "P_pump_beam_uW", "A_pump", "icp", "P_pump_total_mW", "wall_ratio",
        "FOM", "fails", "feasible"]


def cell(args):
    content, mote, sname, arch, a, R, npump = args
    sc = SCEN[sname]
    best, slowest = None, None
    for v in b2.V_GRID:
        d = b2.design(content=content, a=a, v=v, mote=mote, arch=arch, R_head=R, n_pump=npump, **sc)
        if slowest is None:
            slowest = d
        if d["feasible"]:
            best = d
    d = best or slowest
    row = {k: d[k] for k in KEEP}
    row.update(scenario=sname, R_head=R, n_pump=npump)
    return row


if __name__ == "__main__":
    t0 = time.time()
    jobs = list(itertools.product(list(b2.CONTENT), MOTES, list(SCEN), ["room_push", "room_pairs"],
                                  [1e-6, 1.5e-6, 2.5e-6, 4e-6], [0.075, 0.1, 0.15], [2, 3]))
    with Pool(4) as pool:
        rows = pool.map(cell, jobs, chunksize=8)
    print(f"{len(rows)} cells in {time.time() - t0:.0f} s")
    with open(os.path.join(HERE, "results", "m5_atlas_v2.json"), "w") as fh:
        json.dump(rows, fh, indent=0, default=float)
    summary = {}
    for content in b2.CONTENT:
        for sname in SCEN:
            for mote in MOTES:
                rs = [r for r in rows if r["content"] == content and r["scenario"] == sname and r["mote"] == mote]
                feas = [r for r in rs if r["feasible"]]
                key = f"{content} | {sname} | {mote}"
                if feas:
                    r = min(feas, key=lambda r: (r["channels"], r["P_trap_total_W"]))
                    summary[key] = r
                    print(f"{key:58s} {r['arch']:10s} a={r['a_um']:.1f} R={r['R_head']} v={r['v']:.2f} N={r['N']:6.0f} "
                          f"ch={r['channels']:6.0f} Tface={r['T_face']:.0f} beam {r['P_beam_mW']:.1f} mW trap {r['P_trap_total_W']:.1f} W "
                          f"pump {r['P_pump_beam_uW']:.1f} uW x{r['n_pump']} wall {r['wall_ratio']:.3f}")
                else:
                    c = Counter(x for r in rs for x in r["fails"])
                    summary[key] = dict(none=True, fail_causes=dict(c))
                    print(f"{key:58s} NONE  {dict(c.most_common(3))}")
    with open(os.path.join(HERE, "results", "m5_best.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=float)

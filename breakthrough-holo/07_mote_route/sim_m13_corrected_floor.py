"""M13: corrected floor after red team 5 (budget v2.1). Counts trap AND pump steered beams.

Scenarios:
* O 'optimistic, errors fixed': 45 Hz, T_face <= 600 K, C_ph 1.0, total air 0.15 m/s, scheduler no-overlap (k = 1),
  non-fluorescent room, 405 nm absorption 1500 /cm (aerogel-dispersed), 0.5 um pump jitter, ideal pump focus.
* B 'best estimate': 60 Hz, T_face <= 573 K (ITO degradation band), C_ph 0.85, total air 0.15 m/s, k = 2 (no certified
  overlap monitor yet), 1.0 um pump jitter (closed-loop on emission), pump focus tracking 3 kHz.
* R 'R9-consistent materials': B with k_eff +0.03, aerogel 405 nm absorption 500 /cm, dense-core 1000 /cm.
* B' / R': B / R with certified safety scheduling (k = 1). B and R turned out infeasible because, with k = 2 on top of
  the summed foci, even holding a mote against 0.15 m/s needs > 5 mW per focus.
Grid: aerogel / core-shell mote, push (4 channels per mote) / passive pairs (pair factor 1.35/eta), a = 1.5-4 um,
R = 0.075-0.15 m, n_pump = 1/2/4. Minimised: total steered beams (trap + pump).
Writes results/m13_corrected_floor.json.
"""
import itertools
import json
import os
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget2 as b2  # noqa: E402

SCEN = {
    "O optimistic (errors fixed)": (dict(f=45.0, T_max=600.0, C_ph=1.0, u_air=0.15, k_overlap=1.0, k_ov_trap=1.0,
                                         whitener_gain=1.0, alpha_pump=1.5e5, jitter=0.5e-6), ("ito_aerogel", "ito_coreshell")),
    "B best estimate": (dict(f=60.0, T_max=573.0, C_ph=0.85, u_air=0.15, k_overlap=2.0, k_ov_trap=2.0, whitener_gain=1.0,
                             alpha_pump=1.5e5, jitter=1.0e-6, B_focus_pump=3e3), ("ito_aerogel", "ito_coreshell")),
    "B' best estimate + certified scheduling (k=1)": (dict(f=60.0, T_max=573.0, C_ph=0.85, u_air=0.15, k_overlap=1.0,
                                                          k_ov_trap=1.0, whitener_gain=1.0, alpha_pump=1.5e5, jitter=1.0e-6,
                                                          B_focus_pump=3e3), ("ito_aerogel", "ito_coreshell")),
    "R' R9 materials + certified scheduling": (dict(f=60.0, T_max=573.0, C_ph=0.85, u_air=0.15, k_overlap=1.0,
                                                    k_ov_trap=1.0, whitener_gain=1.0, alpha_pump=5e4, jitter=1.0e-6,
                                                    B_focus_pump=3e3), ("ito_aerogel_r9", "ito_coreshell_r9")),
    "R R9-consistent materials": (dict(f=60.0, T_max=573.0, C_ph=0.85, u_air=0.15, k_overlap=2.0, k_ov_trap=2.0,
                                       whitener_gain=1.0, alpha_pump=5e4, jitter=1.0e-6, B_focus_pump=3e3),
                                  ("ito_aerogel_r9", "ito_coreshell_r9")),
}
EMIT = {"cyan": "cyan_BaSi2O2N2_hiT", "green": "green_bSiAlON_hiT"}


def cell(args):
    content, sname, color = args
    kw, motes = SCEN[sname]
    best = None
    for mote, arch, a, R, npump in itertools.product(motes, ["room_push", "room_pairs"], [1.5e-6, 2.5e-6, 4e-6],
                                                     [0.075, 0.1, 0.15], [1, 2, 4]):
        for v in b2.V_GRID:
            d = b2.design(content=content, a=a, v=v, mote=mote, arch=arch, R_head=R, n_pump=npump, emitter=EMIT[color], **kw)
            if d["feasible"]:
                tot = d["channels"] + d["pump_channels"]
                if best is None or tot < best["total"]:
                    best = dict(total=tot, trap=d["channels"], pump=d["pump_channels"], N=d["N"], v=d["v"], arch=arch,
                                mote=mote, a_um=d["a_um"], R=R, n_pump=npump, T_face=d["T_face"],
                                P_trap_W=d["P_trap_total_W"], P_pump_uW=d["P_pump_beam_uW"])
    return dict(content=content, scenario=sname, color=color, best=best)


if __name__ == "__main__":
    jobs = list(itertools.product(list(b2.CONTENT), list(SCEN), ["cyan", "green"]))
    with Pool(4) as pool:
        rows = pool.map(cell, jobs)
    json.dump(rows, open(os.path.join(HERE, "results", "m13_corrected_floor.json"), "w"), indent=1, default=float)
    for r in rows:
        b = r["best"]
        tag = f"{r['content']:13s} | {r['scenario']:28s} | {r['color']:5s}"
        if b:
            print(f"{tag} total {b['total']:6.0f} (trap {b['trap']:6.0f} + pump {b['pump']:6.0f}) N={b['N']:6.0f} v={b['v']:.2f} "
                  f"{b['arch']:10s} {b['mote']:16s} a={b['a_um']:.1f} R={b['R']} x{b['n_pump']} Tface={b['T_face']:.0f} trap {b['P_trap_W']:.0f} W")
        else:
            print(f"{tag} none")

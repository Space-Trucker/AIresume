"""SPARK design atlas: sweep spark formats; one JSON per case in ../results/atlas/ (existing cases are skipped)."""
import json
import math
import os
import sys
from multiprocessing import Pool

from run_spark import run_case, to_json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "atlas")
os.makedirs(OUT, exist_ok=True)


def r0_for(E, eps):
    # Gaussian profile exp(-r^2/r0^2): peak energy density = E / (pi^1.5 r0^3); set it to eps
    return (E / (math.pi ** 1.5 * eps)) ** (1 / 3)


def cases():
    cs = []
    for E in (1e-6, 3e-6, 10e-6, 30e-6, 100e-6, 300e-6, 1e-3):
        for eps in (1e8, 3e8, 1e9, 3e9):
            cs.append(dict(label=f"A_E{E*1e6:g}uJ_eps{eps:.0e}", E_abs=E, r0=r0_for(E, eps)))
    r10 = r0_for(10e-6, 3e8)
    for d in (3e-9, 30e-9, 300e-9):
        cs.append(dict(label=f"B_double_5+5uJ_delay{d*1e9:g}ns", E_abs=10e-6, r0=r10, pulses=[(d, 5e-6, r10)]))
    for E in (10e-6, 100e-6):
        for Rs_um in (30, 100):
            cs.append(dict(label=f"C_shell_E{E*1e6:g}uJ_R{Rs_um}um", E_abs=E, r0=r0_for(E, 3e8), profile="shell",
                           shell_R=Rs_um * 1e-6))
    # geometry bracket: line focus (cylindrical, per unit length) at matched peak energy density and radius
    for E_sph, eps in ((10e-6, 3e8), (100e-6, 3e8)):
        r0 = r0_for(E_sph, eps)
        E_L = eps * math.pi * r0 * r0            # J/m for a 2D Gaussian with the same peak energy density
        cs.append(dict(label=f"D_cyl_matched_E{E_sph*1e6:g}uJ_eps{eps:.0e}", E_abs=E_L, r0=r0, geometry="cylindrical"))
    # mixing on (upper bound on cooling) for micro-sparks
    for E in (3e-6, 10e-6, 100e-6):
        cs.append(dict(label=f"M_mix_E{E*1e6:g}uJ_eps3e+08", E_abs=E, r0=r0_for(E, 3e8), mix=True))
    return cs


def work(c):
    path = os.path.join(OUT, c["label"] + ".json")
    if os.path.exists(path):
        return c["label"], "skipped (exists)"
    kw = {k: v for k, v in c.items() if k not in ("label", "E_abs", "r0")}
    try:
        res = run_case(c["E_abs"], c["r0"], label=c["label"], max_wall=1500, **kw)
        open(path, "w").write(to_json(res))
        return c["label"], f"eta={res['eta_lm_per_W']:.3g} NO/J={res.get('NO_per_J', float('nan')):.2e} wall={res['wall_s']:.0f}s"
    except Exception as ex:  # record failures, never hide them
        open(path.replace(".json", ".FAILED.txt"), "w").write(repr(ex))
        return c["label"], f"FAILED {ex!r}"


if __name__ == "__main__":
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    cs = cases()
    print(f"{len(cs)} cases", flush=True)
    with Pool(nproc) as p:
        for lab, msg in p.imap_unordered(work, cs):
            print(lab, msg, flush=True)

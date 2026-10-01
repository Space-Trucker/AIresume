"""M8c: can film-exact (50 cd/m^2, lit room) be unlocked within Class 1?

Levers on the pump side:
* more pump beams per mote (2/4/6, from different heads; each beam assessed separately);
* longer pump wavelength (405 / 450 / 470 nm). The Class 1 photochemical AEL rises as C3 = 10^(0.02(lambda-450)):
  39 / 39 / 98 uW;
* phosphor colour: cyan 497 nm (V ~0.3) or green 540 nm (V ~0.95).
Mote and room as in M8 L3 (ito_coreshell / ito_aerogel, 600 K face, laminar zone, 45 Hz, R12 rig).
The wall-light check uses V(pump) (470 nm is visible blue) with non-fluorescent surfaces.
Writes results/m8c_bright.json.
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget2 as b2  # noqa: E402

BASE = dict(f=45.0, k_overlap=1.0, k_ov_trap=1.0, whitener_gain=1.0, T_max=600.0, u_air=0.05)
rows = []
for content in ("film_density", "film_exact"):
    for emitter, lam_p, npump in itertools.product(["cyan_BaSi2O2N2_hiT", "green_bSiAlON_hiT"], [405, 450, 470], [2, 4, 6]):
        best = None
        for mote, arch, a, R in itertools.product(["ito_aerogel", "ito_coreshell"], ["room_push", "room_pairs"],
                                                  [1.5e-6, 2.5e-6, 4e-6], [0.1, 0.15]):
            for v in b2.V_GRID:
                d = b2.design(content=content, a=a, v=v, mote=mote, arch=arch, R_head=R, n_pump=npump,
                              emitter=emitter, pump_lam=lam_p, **BASE)
                if d["feasible"] and (best is None or d["channels"] < best["channels"]):
                    best = dict(d, R_head=R)
        tag = f"{content:12s} {emitter:20s} pump {lam_p} nm x{npump}"
        if best:
            rows.append(dict(content=content, emitter=emitter, pump_lam=lam_p, n_pump=npump, **{k: best[k] for k in
                        ("mote", "arch", "a_um", "v", "N", "channels", "pump_channels", "P_trap_total_W", "P_pump_beam_uW",
                         "wall_ratio")}))
            print(f"{tag}: {best['arch']:10s} {best['mote']:13s} a={best['a_um']:.1f} N={best['N']:6.0f} ch={best['channels']:6.0f} "
                  f"(+{best['pump_channels']:.0f} pump) trap {best['P_trap_total_W']:.0f} W pump {best['P_pump_beam_uW']:.0f} uW "
                  f"wall {best['wall_ratio']:.3f}", flush=True)
        else:
            print(f"{tag}: none", flush=True)
json.dump(rows, open(os.path.join(HERE, "results", "m8c_bright.json"), "w"), indent=1, default=float)

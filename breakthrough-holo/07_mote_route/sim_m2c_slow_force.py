"""M2c: push-trap feedback with a slow photophoretic force response (R8: lag up to ~a^2/alpha_p).

beta_F = 1 means tau_F = a^2/alpha_p = 75 us at a = 1 um, k_p = 0.02. Scan the flat-top radius R_ft (beam power
scales as R_ft^2; R_ft = 30 um is about 7.8 mW, near the 10 mW Class 1 limit), gusts and loop rate.
Writes results/m2c_slow_force.json.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import feedback as fb  # noqa: E402

rows = []
t0 = time.time()
for R_ft in (10e-6, 20e-6, 30e-6):
    for gs in (0.1, 0.2):
        for f in (20e3, 50e3):
            c = dict(R_ft=R_ft, gust_sigma=gs, f_loop=f, beta_F=1.0)
            r = fb.run(T_sim=0.2, n_motes=32, a=1e-6, **c)
            rows.append(dict(c, lost_frac=r["lost_frac"], rms_err_um=r["rms_err_um"], tau_F_us=r["tau_F_us"]))
            print(f"{c} lost {r['lost_frac']:.2f} rms_err {r['rms_err_um']:.1f} um tau_F {r['tau_F_us']:.0f} us "
                  f"({time.time() - t0:.0f} s)", flush=True)
with open(os.path.join(HERE, "results", "m2c_slow_force.json"), "w") as fh:
    json.dump(rows, fh, indent=1)

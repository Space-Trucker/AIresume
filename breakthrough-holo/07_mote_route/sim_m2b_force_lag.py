"""M2b: feedback push trap including the photophoretic force lag (internal thermal diffusion, tau_F = 0.2 a^2/alpha_p).

The loop gain is capped at w_c <= 1/(4 tau_F). Scan loop rate, gusts, flat-top radius R_ft and beta_F.
Writes results/m2b_force_lag.json.
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
cases = []
for R_ft in (10e-6, 20e-6):
    for gs in (0.1, 0.2):
        for f in (10e3, 20e3, 50e3):
            cases.append(dict(R_ft=R_ft, gust_sigma=gs, f_loop=f))
for beta in (0.1, 0.5):
    cases.append(dict(R_ft=10e-6, gust_sigma=0.1, f_loop=20e3, beta_F=beta))
for c in cases:
    r = fb.run(T_sim=0.2, n_motes=32, a=1e-6, **c)
    row = dict(c, lost_frac=r["lost_frac"], rms_err_um=r["rms_err_um"], max_rho_um=r["max_rho_um"],
               sigma_rho_um=r["sigma_rho_um"], tau_F_us=r["tau_F_us"])
    rows.append(row)
    print(f"{c} lost {r['lost_frac']:.2f} rms_err {r['rms_err_um']:.2f} um tau_F {r['tau_F_us']:.1f} us ({time.time()-t0:.0f} s)",
          flush=True)
with open(os.path.join(HERE, "results", "m2b_force_lag.json"), "w") as fh:
    json.dump(rows, fh, indent=1)

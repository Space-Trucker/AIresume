"""M2: feedback push trap - required control-loop rate (prediction P23), with sensitivity to mote size, gusts, heads.

Tracing a 5 cm circle at 1 m/s in a 0.1 m/s draft plus OU gusts. Outputs: lost fraction over T_sim, per-axis rms of
the mote-to-beam offset, and a Rayleigh-tail extrapolated loss rate. Writes results/m2_feedback_scan.json.
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
for a in (1e-6, 2.5e-6):
    for gs in (0.05, 0.1, 0.2):
        for f in (5e3, 10e3, 15e3, 20e3, 30e3, 50e3):
            cases.append(dict(a=a, gust_sigma=gs, f_loop=f, heads="tetra"))
for f in (10e3, 20e3, 50e3):
    cases.append(dict(a=1e-6, gust_sigma=0.1, f_loop=f, heads="octa"))
for sm in (0.1e-6, 2e-6):
    cases.append(dict(a=1e-6, gust_sigma=0.1, f_loop=20e3, heads="tetra", sigma_m=sm))
for c in cases:
    r = fb.run(T_sim=0.2, n_motes=32, **c)
    row = dict(c, lost_frac=r["lost_frac"], rms_err_um=r["rms_err_um"], max_err_um=r["max_err_um"],
               max_rho_um=r["max_rho_um"], sigma_rho_um=r["sigma_rho_um"],
               loss_extrap_per_min=r["loss_rate_extrap_per_min"], tau_p_us=r["tau_p_us"])
    rows.append(row)
    print(f"{c} lost {r['lost_frac']:.2f} sig_rho {r['sigma_rho_um']:.2f} um extrap {r['loss_rate_extrap_per_min']:.2e}/min "
          f"({time.time() - t0:.0f} s)", flush=True)
with open(os.path.join(HERE, "results", "m2_feedback_scan.json"), "w") as fh:
    json.dump(rows, fh, indent=1)

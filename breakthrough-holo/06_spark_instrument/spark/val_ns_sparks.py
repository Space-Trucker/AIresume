"""Physics validation runs: ns-class laser sparks (literature energy partition, Thomson T_e, NO/J)."""
import json
import sys

import numpy as np

from eos import fast
from radiation import load as load_rad, conductivity
from hydro import Spark
from chemistry import spark_products
from run_spark import to_json

E, r0, tag = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
mix = len(sys.argv) > 4 and sys.argv[4] == "mix"
tv = float(sys.argv[5]) if len(sys.argv) > 5 else 0.35
tm = float(sys.argv[6]) if len(sys.argv) > 6 else 0.10
eos, rad = fast(), load_rad()
s = Spark(eos, E, r0, rad=rad, kappa_fn=conductivity, n_core=48, growth=1.04, mix=mix, mix_tv=tv, mix_tau=tm)
s.r_probe = 3 * s.rc
s.probe_j = int(np.argmin(np.abs(s.r - s.r_probe)))
# kernel diagnostics at the literature times
marks = {1e-6: None, 10e-6: None, 20e-6: None, 21e-6: None}
while s.t < 5e-3:
    if s.phase == 1:
        T = s.step_compressible()
        rho = s.m / s._vol(s.r)
        for tm in marks:
            if marks[tm] is None and s.t >= tm:
                Tn = eos.T(rho, s.e)
                ne = eos.base.ne_of_T(rho, Tn)
                marks[tm] = dict(Tmax=float(Tn.max()), ne_at_Tmax=float(ne[int(np.argmax(Tn))]))
        if s.step % 200 == 0 and s.ready_for_isobaric():
            s.to_isobaric()
    else:
        for tm in marks:
            if marks[tm] is None and s.t >= tm:
                marks[tm] = dict(Tmax=float(s.Tiso.max()), ne_at_Tmax=float("nan"))
        if s.Tiso.max() < 1200:
            break
        dt = getattr(s, "dt_iso", 1e-9)
        Tb = s.Tiso.copy()
        s.step_isobaric(dt)
        rel = float(np.max(np.abs(s.Tiso - Tb) / Tb))
        s.dt_iso = dt * (1.3 if rel < 0.01 else (0.7 if rel > 0.03 else 1.0))
res = s.summary()
res["marks"] = {str(k): v for k, v in marks.items()}
res["chem"] = spark_products(s)
res["NO_per_J"] = res["chem"]["NO_total"] / E
res["reactive_per_J"] = res["chem"]["NOx_plus_O3"] / E
res.update(E_in=E, r0=r0)
open(f"../results/val_{tag}.json", "w").write(to_json(res))
print(tag, "done", res["f_rad"], res["f_sedov"], res["eta_lm_per_W"], res["NO_per_J"])

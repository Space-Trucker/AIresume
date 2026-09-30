"""Grid/time-step convergence and closure runs for the 10 uJ reference micro-spark (V13-V16)."""
import json
from run_spark import run_case, to_json
cases = {"ref": dict(), "fine_grid": dict(n_core=96, growth=1.015), "half_cfl": dict(cfl=0.15)}
out = {}
for k, kw in cases.items():
    out[k] = run_case(10e-6, 10e-6, **kw)
    print(k, out[k]["eta_lm_per_W"], out[k]["f_sedov"], out[k].get("NO_per_J"), out[k]["closure_at_switch"], flush=True)
    open("../results/val_convergence.json", "w").write(to_json(out))

"""Run one SPARK case (hydro + radiation + conduction + chemistry) and return a JSON-able dict."""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np

from eos import fast
from radiation import load as load_rad, conductivity
from hydro import Spark
from chemistry import spark_products

_EOS = _RAD = None


def run_case(E_abs, r0, kappa_mult=1.0, n_core=48, growth=1.03, cfl=0.3, chem=True, t_end=5e-3, rad_on=True,
             profile="gauss", label=None, shell_R=None, pulses=None, geometry="spherical", mix=False,
             mix_tv=0.35, mix_tau=0.10, max_wall=None):
    global _EOS, _RAD
    if _EOS is None:
        _EOS, _RAD = fast(), load_rad()
    t0 = time.time()
    s = Spark(_EOS, E_abs, r0, rad=_RAD if rad_on else None, kappa_fn=conductivity, kappa_mult=kappa_mult,
              n_core=n_core, growth=growth, cfl=cfl, profile=profile, shell_R=shell_R, pulses=pulses,
              geometry=geometry, mix=mix, mix_tv=mix_tv, mix_tau=mix_tau)
    E0 = s.total_energy()
    res = s.run(t_end=t_end, max_wall=max_wall)
    res["energy_drift_phase1"] = float("nan")
    if s.phase == 1:
        res["energy_drift_phase1"] = (s.total_energy() + s.W_out + sum(s.E_rad.values()) - E0) / E_abs
    if chem and len(s.hist_t) > 3:
        res["chem"] = spark_products(s)
        c = res["chem"]
        res["NO_per_J"] = c["NO_total"] / E_abs
        res["NO2_per_J"] = c["NO2_total"] / E_abs
        res["O3_per_J"] = c["O3_total"] / E_abs
        res["reactive_per_J"] = c["NOx_plus_O3"] / E_abs
    res.update(dict(profile=profile, shell_R=shell_R, pulses=pulses, r0=r0, kappa_mult=kappa_mult, n_core=n_core, cfl=cfl, wall_s=time.time() - t0, label=label,
                    act_per_J=res["act_J"] / E_abs))
    return res


def to_json(obj):
    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        return o
    return json.dumps(conv(obj), indent=1)


if __name__ == "__main__":
    r = run_case(10e-6, 10e-6)
    print(to_json(r))

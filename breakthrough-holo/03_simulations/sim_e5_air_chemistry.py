"""E5: Indoor air quality around an air-plasma display.

Box model of a room (well mixed) plus a near-field plume term for the breathing zone:
  dC/dt = S(1-capture)/V - (ACH + CADR*eff/V + k_decay) C
  near-field increment at distance r from a continuous point source with indoor turbulent
  diffusivity D_t (0.001-0.01 m^2/s):  C_nf(r) = S(1-capture) / (4 pi D_t r)
S = Y_react * P_abs (reactive molecules per s). Limits (R3 notes): O3 device limit 50 ppb (UL 867),
Health Canada O3 20 ppb 8-h; NO2 WHO 1-h 106 ppb, EPA annual 53 ppb, WHO annual 5.3 ppb.
Design target used by the lab: room increment + near-field increment <= 20 ppb.
"""
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import N_AIR, RESULTS, save_json
from display_budget import P

print("E5 air chemistry")
Y = P("Y_react")
cases = {
    "baseline: 400 m3/h scrubber, no capture": dict(cadr=400, eff=0.7, capture=0.0),
    "engineered: 600 m3/h, 80% capture": dict(cadr=600, eff=0.8, capture=0.8),
    "engineered+: 900 m3/h, 90% capture": dict(cadr=900, eff=0.85, capture=0.9),
}
V, ach, kdec = 50.0, 0.5, 0.5
out = {}
t = np.linspace(0, 3 * 3600, 1000)
fig, ax = plt.subplots(figsize=(7, 4))
for name, c in cases.items():
    rows = {}
    for P_abs in (0.3, 1.0, 3.0, 10.0):
        S = Y * P_abs * (1 - c["capture"]) / N_AIR * 1e9      # ppb*m^3/s
        k = ach / 3600 + c["cadr"] * c["eff"] / 3600 / V + kdec / 3600
        C_room = S / V / k * (1 - np.exp(-k * t))
        nf = {Dt: S / (4 * math.pi * Dt * 0.5) for Dt in (0.001, 0.005, 0.01)}
        rows[P_abs] = dict(room_ss_ppb=float(C_room[-1]), near_field_ppb_at_0p5m=nf,
                           total_typical_ppb=float(C_room[-1] + nf[0.005]))
        if P_abs == 3.0:
            ax.plot(t / 3600, C_room + nf[0.005], label=f"{name} (3 W absorbed)")
        print(f"  {name:42s} P_abs={P_abs:5.1f} W: room {C_room[-1]:7.1f} ppb + near-field(0.5 m) "
              f"{nf[0.005]:6.1f} ppb (range {nf[0.01]:.1f}-{nf[0.001]:.1f})")
    out[name] = rows
ax.axhline(20, color="k", ls="--", lw=1); ax.text(0.1, 21, "lab design target 20 ppb", fontsize=8)
ax.axhline(50, color="r", ls=":", lw=1); ax.text(0.1, 52, "UL 867 ozone 50 ppb", fontsize=8, color="r")
ax.set_xlabel("hours of operation"); ax.set_ylabel("O3+NOx increment at a face 0.5 m away (ppb)")
ax.set_yscale("log"); ax.legend(fontsize=7); ax.set_title("Air-plasma display: breathing-zone reactive species")
plt.tight_layout(); plt.savefig(f"{RESULTS}/e5_air_chemistry.png", dpi=120); plt.close()
save_json("e5_air_chemistry.json", out)
print("  saved results/e5_air_chemistry.json/.png")

"""E2: Can SOUND sculpt air into something that sends projector light toward viewers?

Sound waves modulate air density, so they change its refractive index and can diffract light
(demonstrated for high-power lasers in ambient air, DESY 2024). To redirect light by an angle theta,
the Bragg condition needs acoustic wavelength Lambda = lambda / (2 sin(theta/2)). Air absorbs
ultrasound roughly as f^2, so we compute how far such sound can travel.
Outputs results/e2_acoustooptic_air.json and results/e2_bragg_vs_absorption.png
"""
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import C_SOUND, GAMMA_AIR, P_ATM, air_n_minus_1, iso9613_alpha_db_per_m, save_json, RESULTS

lam = 532e-9
out = {"lambda_nm": 532}
print("E2 acousto-optics in air")

# absorption at typical ultrasonic frequencies
freqs = np.array([40e3, 100e3, 200e3, 500e3, 1e6, 10e6, 100e6, 1e9])
alpha = iso9613_alpha_db_per_m(freqs)
table = []
for f, a in zip(freqs, alpha):
    Lam = C_SOUND / f
    theta = lam / Lam                        # first-order (Raman-Nath/Bragg) deflection, rad
    reach = 20.0 / a                         # distance for 20 dB loss
    table.append(dict(f_Hz=f, alpha_dB_m=a, acoustic_wavelength_m=Lam, deflection_mrad=theta * 1e3,
                      reach_20dB_m=reach))
    print(f"  f={f:10.3g} Hz  alpha={a:10.4g} dB/m  Lambda={Lam*1e6:10.3f} um  deflection={theta*1e3:9.4f} mrad"
          f"  20-dB reach={reach:10.3g} m")
out["table"] = table

# frequency needed for useful display angles
need = []
for th_deg in (1, 10, 45, 90):
    th = math.radians(th_deg)
    Lam = lam / (2 * math.sin(th / 2))
    f = C_SOUND / Lam
    a = float(iso9613_alpha_db_per_m(f))
    need.append(dict(theta_deg=th_deg, f_Hz=f, alpha_dB_m=a, reach_20dB_m=20 / a))
    print(f"  to deflect {th_deg:3d} deg need f={f:.3g} Hz; absorption {a:.3g} dB/m; 20-dB reach {20/a:.3g} m")
out["needed_for_angle"] = need

# strength: refractive-index modulation at 160 dB SPL (2 kPa)
p = 2000.0
dn = air_n_minus_1(lam) * p / (GAMMA_AIR * P_ATM)
out["delta_n_at_160dB"] = dn
print(f"  index modulation at 160 dB SPL: dn={dn:.2e} (strong phase grating over 10 cm, but only tiny angles)")
print("  -> sound can steer light by <~1 mrad; sending light sideways to viewers is impossible: DEAD as a display source")

fig, ax1 = plt.subplots(figsize=(7, 4.2))
ff = np.logspace(4, 9, 300)
ax1.loglog(ff, lam / (C_SOUND / ff) * 1e3, color="#4a7bd1", label="max deflection (mrad)")
ax1.set_xlabel("ultrasound frequency (Hz)")
ax1.set_ylabel("deflection of 532 nm light (mrad)", color="#4a7bd1")
ax2 = ax1.twinx()
ax2.loglog(ff, 20 / iso9613_alpha_db_per_m(ff), color="#d1734a", label="20 dB reach (m)")
ax2.set_ylabel("distance sound survives, 20 dB loss (m)", color="#d1734a")
ax1.axhline(math.radians(10) * 1e3, color="#4a7bd1", ls=":", lw=1)
ax1.text(1.2e4, math.radians(10) * 1e3 * 1.2, "10° needed to reach viewers", color="#4a7bd1", fontsize=8)
plt.title("Acousto-optics in air: big angles need sound that dies in µm")
plt.tight_layout(); plt.savefig(f"{RESULTS}/e2_bragg_vs_absorption.png", dpi=120); plt.close()
save_json("e2_acoustooptic_air.json", out)
print("  saved results/e2_acoustooptic_air.json")

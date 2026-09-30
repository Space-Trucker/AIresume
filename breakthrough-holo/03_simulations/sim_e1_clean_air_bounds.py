"""E1: Can clean room air itself be made to glow at a chosen point, other than by ionising it?

Tests every non-plasma optical mechanism from T1 section 4 with numbers:
  (a) Rayleigh scattering: power per voxel, and the 'glowing line' problem
  (b) coherent nonlinear emission (THG/FWM): sideways emission suppressed by phase matching
  (c) incoherent nonlinear (hyper-Rayleigh-type) scattering: photons per voxel per pulse
  (d) microwave/THz breakdown: energy per voxel and RF exposure
Outputs results/e1_clean_air_bounds.json and results/e1_*.png
"""
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import (N_AIR, N2_AIR, air_n_minus_1, check, photon_energy, rayleigh_sigma,
                         save_json, V_photopic, RESULTS)

out = {}
print("E1 clean-air bounds")

# ---------- calibration ----------
# Bucholtz (1995, Appl. Opt. 34, 2765) Table: sigma_Rayleigh(550 nm) = 4.513e-27 cm^2 (= 4.513e-31 m^2)
cal_ok = check("Rayleigh sigma @550nm (m^2)", rayleigh_sigma(550e-9), 4.513e-31, 0.05, "Bucholtz 1995 Appl.Opt. 34:2765")
out["calibration_rayleigh_550_pass"] = cal_ok

# ---------- (a) Rayleigh ----------
p90 = 3 / (16 * math.pi) * (1 + 0.0)   # phase function at 90 deg, per sr (normalised to 1 over 4pi)
rows = []
for lam_nm in (450, 532, 633):
    lam = lam_nm * 1e-9
    beta = rayleigh_sigma(lam) * N_AIR          # 1/m
    V = float(V_photopic(lam_nm))
    # line luminance of a 1 W, 1 mm beam seen side-on
    d = 1e-3
    L_line = 683 * V * (1.0 * beta * p90 / d)    # cd/m^2 per W
    # power for a 1 mm^3 'voxel' of luminance L (if the beam could be stopped at the voxel)
    need = {}
    for Lv in (1.0, 10.0, 100.0):
        Le = Lv / (683 * V)                     # W/(sr m^2)
        E_irr = Le / (beta * d * p90)           # W/m^2 through 1 mm depth
        need[f"L{int(Lv)}"] = E_irr * d * d     # W per 1 mm^2 cross-section voxel
    rows.append(dict(lam_nm=lam_nm, beta_per_m=beta, line_cd_m2_per_W_1mm=L_line,
                     watts_per_voxel_for_1cd=need["L1"], watts_per_voxel_for_10cd=need["L10"],
                     watts_per_voxel_for_100cd=need["L100"]))
    print(f"  Rayleigh {lam_nm} nm: beta={beta:.3e}/m, 1 W 1 mm beam side luminance={L_line:.3f} cd/m2, "
          f"voxel needs {need['L1']:.2f} W @1cd/m2, {need['L100']:.0f} W @100cd/m2")
out["rayleigh"] = rows
frame_voxels = 1e5
out["rayleigh_frame_1e5_voxels_10cd_W"] = rows[1]["watts_per_voxel_for_10cd"] * frame_voxels
print(f"  -> an Iron-Man frame of 1e5 voxels at 10 cd/m2 would need {out['rayleigh_frame_1e5_voxels_10cd_W']:.2e} W,"
      " AND the beams cannot stop at the voxel (linear process): DEAD")

# ---------- (b) coherent nonlinear emission sideways ----------
# Power radiated at angle theta by a Gaussian-envelope 3rd-order polarisation ~ exp(-dk^2 w0^2 / 6);
# for THG sideways dk = 3k*sqrt(2)  ->  suppression S = exp(-3 k^2 w0^2)
sup = []
for w_over_lam in (0.25, 0.5, 1.0, 2.0, 5.0):
    kw = 2 * math.pi * w_over_lam
    S_log10 = -3 * kw * kw / math.log(10)
    sup.append(dict(w0_over_lambda=w_over_lam, log10_side_suppression=S_log10))
    print(f"  coherent side-emission suppression, w0={w_over_lam} lambda: 10^{S_log10:.1f}")
out["coherent_side_suppression"] = sup

# ---------- (c) incoherent nonlinear scattering ----------
lam = 1.03e-6
I_ion = 5e17                     # W/m^2 (~5e13 W/cm^2, onset of ionisation for ~100 fs)
ratio = (N2_AIR * I_ion / air_n_minus_1(lam)) ** 2
w0, Lz, tau = 5e-6, 100e-6, 100e-15
Nmol = N_AIR * math.pi * w0 ** 2 * Lz
ray_photons = Nmol * rayleigh_sigma(lam) * I_ion * tau / photon_energy(lam)
nl_photons = ray_photons * ratio
out["incoherent_nl"] = dict(intensity_W_m2=I_ion, ratio_to_rayleigh=ratio, rayleigh_photons_per_pulse=ray_photons,
                            nonlinear_photons_per_pulse=nl_photons)
print(f"  incoherent nonlinear: ratio to Rayleigh={ratio:.2e}; photons/pulse/voxel ~ {nl_photons:.1f} "
      f"(plasma voxel gives ~1e8+) -> DEAD")

# ---------- (d) microwave / THz breakdown ----------
Z0 = 376.73
E_bd = 3.5e6  # V/m rms, ~atmospheric breakdown for us pulses (order of magnitude; rises at THz)
mw = []
for f_ghz in (10, 100, 300, 1000):
    lam_mw = 3e8 / (f_ghz * 1e9)
    spot = math.pi * (lam_mw / 2) ** 2
    Ppk = E_bd ** 2 / Z0 * spot
    E_vox = Ppk * 1e-6
    mw.append(dict(f_GHz=f_ghz, voxel_mm=lam_mw * 1e3, peak_W=Ppk, J_per_voxel_1us=E_vox,
                   avg_W_at_1e5_voxels_s=E_vox * 1e5))
    print(f"  {f_ghz:5d} GHz: voxel~{lam_mw*1e3:.2f} mm, {E_vox*1e3:.1f} mJ/voxel (1 us), "
          f"{E_vox*1e5/1e3:.1f} kW average at 1e5 voxels/s vs ICNIRP public limit 10 W/m^2 -> DEAD")
out["microwave_thz"] = mw

# ---------- plot ----------
fig, ax = plt.subplots(figsize=(7, 4.2))
names = ["Rayleigh voxel\n(10 cd/m², 1 mm³)", "Incoherent NL\n(photons/pulse)", "Plasma voxel\n(photons/pulse, E4)"]
vals = [rows[1]["watts_per_voxel_for_10cd"], nl_photons, 1e8]
ax.bar([0], [vals[0]], color="#4a7bd1")
ax.set_yscale("log")
ax.set_xticks([0]); ax.set_xticklabels([names[0]])
ax.set_ylabel("W per voxel (continuous)")
ax.set_title("Rayleigh: power per 1 mm³ voxel for 10 cd/m² at 532 nm")
ax.text(0, vals[0] * 1.3, f"{vals[0]:.0f} W", ha="center")
plt.tight_layout(); plt.savefig(f"{RESULTS}/e1_rayleigh_voxel_power.png", dpi=120); plt.close()

save_json("e1_clean_air_bounds.json", out)
print("  saved results/e1_clean_air_bounds.json")

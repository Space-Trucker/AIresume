"""E7b: Band-resolved actinic-UV check of the plasma's own emission (red-team finding 13).

E7 weighted all UV with S(337 nm) only. Here the full ICNIRP/ACGIH relative spectral
effectiveness S(lambda) (200-400 nm) is applied to two emission models from E11:
  (a) N2 second-positive bands incl. the 296.2/297.7/315.9 nm bands (relative strengths typical of
      air fluorescence spectra, ~3 % / 5 % of 337 nm; ESTIMATE)
  (b) hot continuum at T = 2 and 3 eV (optically thin free-free/free-bound shape, as E11)
Dose = radiated UV power / (4 pi r^2) * S_eff * 8 h; limit 30 J/m^2 effective (ICNIRP 2004).
"""
import math

import numpy as np

from holo_common import save_json

S_TAB = {200: 0.03, 210: 0.075, 220: 0.12, 230: 0.19, 240: 0.30, 250: 0.43, 254: 0.5, 260: 0.65, 270: 1.0,
         280: 0.88, 290: 0.64, 297: 0.46, 300: 0.30, 305: 0.06, 310: 0.015, 315: 0.003, 320: 0.001,
         330: 0.00041, 340: 0.00028, 350: 0.0002, 360: 0.00013, 370: 0.000093, 380: 0.000064,
         390: 0.000045, 400: 0.00003}
lam = np.arange(200, 900.1, 0.5)
S = np.exp(np.interp(lam, list(S_TAB), np.log(list(S_TAB.values())), right=-60))
S[lam > 400] = 0.0


def lines(pairs, w=1.0):
    s = np.zeros_like(lam)
    for l0, a in pairs:
        s += a * np.exp(-0.5 * ((lam - l0) / w) ** 2)
    return s


N2 = [(296.2, 0.03), (297.7, 0.03), (315.9, 0.05), (337.1, 1.0), (353.7, 0.2), (357.7, 0.7), (371.0, 0.1),
      (375.5, 0.3), (380.5, 0.4), (391.4, 0.6), (394.3, 0.1), (399.8, 0.15), (405.9, 0.1), (427.8, 0.2)]


def continuum(T):
    return np.exp(-1239.84 / (lam * T)) / lam ** 2


def s_eff(spec):
    return float(np.sum(spec * S) / np.sum(spec))          # actinic weight per watt of emitted light


if __name__ == "__main__":
    print("E7b actinic UV, band-resolved")
    P_abs, f_rad, hours = 3.0, 0.03, 8.0
    out = {}
    for name, spec in (("N2 bands", lines(N2)), ("continuum 2 eV", continuum(2.0)), ("continuum 3 eV", continuum(3.0))):
        se = s_eff(spec)
        for r in (0.3, 0.5):
            H = P_abs * f_rad / (4 * math.pi * r * r) * se * hours * 3600
            out[f"{name} @ {r} m"] = dict(S_eff_per_W=se, dose_8h_J_m2=H, margin=30.0 / H)
            print(f"  {name:15s} S_eff={se:.2e}/W  r={r} m: 8-h effective dose {H:6.2f} J/m^2 -> margin {30/H:6.1f}x")
    print(f"  (E7's single-wavelength estimate used S_eff = 3.2e-4 x 0.3 UV share = {3.2e-4*0.3:.1e}/W)")
    save_json("e7b_uv_actinic.json", out)

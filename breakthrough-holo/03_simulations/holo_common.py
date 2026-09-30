"""Shared physical constants and helpers for the breakthrough-holo simulations.

Every function that encodes a physical model states its source in the docstring.
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

# --- fundamental constants (SI) ---
c = 299_792_458.0            # m/s
h = 6.626_070_15e-34         # J s
hbar = h / (2 * math.pi)
kB = 1.380_649e-23           # J/K
e = 1.602_176_634e-19        # C
me = 9.109_383_7e-31         # kg
eps0 = 8.854_187_8128e-12    # F/m
mu0 = 4e-7 * math.pi

# --- air at 20 C, 1 atm ---
P_ATM = 101_325.0            # Pa
T_ROOM = 293.15              # K
N_AIR = P_ATM / (kB * T_ROOM)  # molecules / m^3  (~2.50e25)
RHO_AIR = 1.204              # kg/m^3
C_SOUND = 343.2              # m/s
GAMMA_AIR = 1.4
N2_AIR = 2.9e-23             # m^2/W nonlinear index of air near 800 nm (Wahlstrand 2012: ~3e-19 cm^2/W)

RESULTS = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS, exist_ok=True)


def photon_energy(lam_m: float) -> float:
    return h * c / lam_m


# CIE 1924 photopic V(lambda) and 1951 scotopic V'(lambda), 10 nm steps 380-780 nm.
_LAM = np.arange(380, 790, 10)
_V = np.array([
    0.0000390, 0.000120, 0.000396, 0.00121, 0.00400, 0.0116, 0.0230, 0.0380, 0.0600, 0.0910,
    0.139, 0.208, 0.323, 0.503, 0.710, 0.862, 0.954, 0.995, 0.995, 0.952,
    0.870, 0.757, 0.631, 0.503, 0.381, 0.265, 0.175, 0.107, 0.0610, 0.0320,
    0.0170, 0.00821, 0.00410, 0.00209, 0.00105, 0.000520, 0.000249, 0.000120, 0.0000600, 0.0000300,
    0.0000149])
_VS = np.array([
    0.000589, 0.002209, 0.00929, 0.03484, 0.0966, 0.1998, 0.3281, 0.455, 0.567, 0.676,
    0.793, 0.904, 0.982, 0.997, 0.935, 0.811, 0.650, 0.481, 0.3288, 0.2076,
    0.1212, 0.0655, 0.03315, 0.01593, 0.00737, 0.003335, 0.001497, 0.000677, 0.0003129, 0.0001480,
    0.0000715, 0.00003533, 0.00001780, 0.00000914, 0.00000478, 0.000002546, 0.000001379, 0.000000760, 0.000000425, 0.000000241,
    0.000000139])


def V_photopic(lam_nm):
    return np.interp(lam_nm, _LAM, _V, left=0.0, right=0.0)


def V_scotopic(lam_nm):
    return np.interp(lam_nm, _LAM, _VS, left=0.0, right=0.0)


def rayleigh_sigma(lam_m: float) -> float:
    """Rayleigh cross-section of air per molecule (m^2).

    sigma = 24 pi^3 / (lambda^4 N^2) * ((n^2-1)/(n^2+2))^2 * F_k,  F_k ~ 1.05 (King factor)
    Refractive index from Ciddor/Edlen-type dispersion (Peck & Reeder 1972 form).
    """
    s2 = (1.0 / (lam_m * 1e6)) ** 2  # 1/um^2
    n_minus_1 = (5791817.0 / (238.0183 - s2) + 167909.0 / (57.362 - s2)) * 1e-8
    n = 1 + n_minus_1 * (N_AIR / 2.547e25)
    Ns = N_AIR
    Fk = 1.05
    return 24 * math.pi ** 3 / (lam_m ** 4 * Ns ** 2) * ((n * n - 1) / (n * n + 2)) ** 2 * Fk


def air_n_minus_1(lam_m: float) -> float:
    s2 = (1.0 / (lam_m * 1e6)) ** 2
    return (5791817.0 / (238.0183 - s2) + 167909.0 / (57.362 - s2)) * 1e-8


def iso9613_alpha_db_per_m(f_hz, T=T_ROOM, rh=50.0, pa=P_ATM):
    """Atmospheric sound absorption (dB/m), ISO 9613-1:1993 closed form.

    Formally specified to ~10 MHz*atm scaling; accurate to +-10 % in the audio range and still
    physically meaningful (classical + O2/N2 relaxation) into the ultrasonic range.
    """
    f = np.asarray(f_hz, dtype=float)
    pr = 101_325.0
    T0 = 293.15
    T01 = 273.16
    C = -6.8346 * (T01 / T) ** 1.261 + 4.6151
    psat_over_pr = 10 ** C
    hmol = rh * psat_over_pr * (pr / pa)  # molar concentration of water vapour, %
    frO = (pa / pr) * (24 + 4.04e4 * hmol * (0.02 + hmol) / (0.391 + hmol))
    frN = (pa / pr) * (T / T0) ** (-0.5) * (9 + 280 * hmol * math.exp(-4.170 * ((T / T0) ** (-1 / 3) - 1)))
    alpha = 8.686 * f ** 2 * (
        1.84e-11 * (pa / pr) ** -1 * (T / T0) ** 0.5
        + (T / T0) ** -2.5 * (
            0.01275 * math.exp(-2239.1 / T) / (frO + f ** 2 / frO)
            + 0.1068 * math.exp(-3352.0 / T) / (frN + f ** 2 / frN)
        )
    )
    return alpha


def save_json(name: str, obj) -> str:
    path = os.path.join(RESULTS, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, default=float)
    return path


def check(label: str, value: float, ref: float, tol_frac: float, source: str) -> bool:
    """Print a calibration check against a published number; return pass/fail."""
    ok = abs(value - ref) <= tol_frac * abs(ref)
    print(f"  [CAL {'PASS' if ok else 'FAIL'}] {label}: model={value:.4g} ref={ref:.4g} "
          f"(tol {tol_frac*100:.0f}%) src: {source}")
    return ok

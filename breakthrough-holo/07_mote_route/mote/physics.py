"""MOTE instrument: physics of an IR-trapped, self-emitting micro-mote in room air.

Models (each validated in validation/validate_mote.py):
* air transport vs T: Sutherland viscosity, conductivity k(T) ~ T^0.82, ideal-gas density
* mote heat balance: P_abs = 4 pi a * int_{T0}^{Tm} k(T) dT  (continuum conduction, Kirchhoff transform)
                             + eps sigma 4 pi a^2 (Tm^4 - T0^4)
* photophoretic force (continuum regime, Kn << 1; Reed 1977 / Yalamov 1976 form):
      F = C_ph * 9 pi mu^2 a I J1 / (2 rho T (k_p + 2 k_g)),  C_ph a calibration factor (default 1)
  evaluated with gas properties at the film temperature (T0+Tm)/2
* drag: Stokes with Oseen correction  F = 6 pi mu a v (1 + 3/16 Re)
* upconversion: photon QY(I, T) = QY_max * s/(1+s) * q(T), s = I/I_sat, q(T) = 1/(1+exp((T-T_q)/dT_q));
  energy yield = QY * lambda_pump / lambda_emit; lumens = 683 V(lambda) * visible power
"""
from __future__ import annotations

import math

import numpy as np

SIGMA = 5.670374e-8
KB = 1.380649e-23
G = 9.81
T0 = 293.15
P0 = 101325.0


def mu_air(T):
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)


def k_air(T):
    return 0.0257 * (T / 293.15) ** 0.82


def rho_air(T):
    return P0 / (287.05 * T)


def k_integral(T):
    """int_{T0}^{T} k_air dT' (closed form of the power law)."""
    c = 0.0257 / 293.15 ** 0.82
    return c * (T ** 1.82 - T0 ** 1.82) / 1.82


def mote_temperature(P_abs, a, eps=0.9):
    """Steady mote temperature for absorbed power P_abs (W), radius a (m)."""
    lo, hi = T0, 6000.0
    for _ in range(100):
        Tm = 0.5 * (lo + hi)
        loss = 4 * math.pi * a * k_integral(Tm) + eps * SIGMA * 4 * math.pi * a * a * (Tm ** 4 - T0 ** 4)
        if loss > P_abs:
            hi = Tm
        else:
            lo = Tm
    return 0.5 * (lo + hi)


def thermal_time(a, rho_p=4200.0, cp=700.0, T=T0):
    """Mote thermal time constant (s): m c_p / (4 pi a k)."""
    m = 4 / 3 * math.pi * a ** 3 * rho_p
    return m * cp / (4 * math.pi * a * k_air(T))


def photophoretic_force(a, I, kp, J1=0.5, Tm=T0, C_ph=1.0):
    """Continuum ΔT-photophoretic force (N) on a sphere of radius a in intensity I (W/m^2)."""
    Tf = 0.5 * (T0 + Tm)
    mu, rho, kg = mu_air(Tf), rho_air(Tf), k_air(Tf)
    return C_ph * 9 * math.pi * mu ** 2 * a * I * J1 / (2 * rho * T0 * (kp + 2 * kg))


def drag(a, v, T=T0):
    mu, rho = mu_air(T), rho_air(T)
    Re = rho * abs(v) * 2 * a / mu
    return 6 * math.pi * mu * a * v * (1 + 3 / 16 * Re)


def settling_velocity(a, rho_p):
    return 2 * rho_p * G * a * a / (9 * mu_air(T0))


def brownian_rms(a, t, T=T0):
    D = KB * T / (6 * math.pi * mu_air(T) * a)
    return math.sqrt(2 * D * t)


# --- emission ---------------------------------------------------------------------------------
_LAM = np.arange(380, 790, 10)
_V = np.array([0.0000390, 0.000120, 0.000396, 0.00121, 0.00400, 0.0116, 0.0230, 0.0380, 0.0600, 0.0910,
               0.139, 0.208, 0.323, 0.503, 0.710, 0.862, 0.954, 0.995, 0.995, 0.952,
               0.870, 0.757, 0.631, 0.503, 0.381, 0.265, 0.175, 0.107, 0.0610, 0.0320,
               0.0170, 0.00821, 0.00410, 0.00209, 0.00105, 0.000520, 0.000249, 0.000120, 0.0000600, 0.0000300,
               0.0000149])


def V(lam_nm):
    return float(np.interp(lam_nm, _LAM, _V, left=0.0, right=0.0))


# emitter presets: list of (lambda_nm, share of emitted photons), and model parameters (to calibrate)
EMITTERS = {
    "Er_green_red": dict(lines=[(540, 0.6), (655, 0.4)], QY_max=0.10, I_sat=30e4, T_q=520.0, dT_q=60.0, lam_pump=980),
    "Tm_blue": dict(lines=[(475, 0.5), (800, 0.5)], QY_max=0.02, I_sat=100e4, T_q=480.0, dT_q=60.0, lam_pump=980),
    "Er_1532": dict(lines=[(540, 0.4), (655, 0.3), (980, 0.3)], QY_max=0.05, I_sat=50e4, T_q=520.0, dT_q=60.0, lam_pump=1532),
}


def uc_lumens(P_abs_pump, I_pump, Tm, emitter="Er_green_red", params=None):
    """Visible lumens emitted by an upconverting mote absorbing P_abs_pump (W) at intensity I_pump (W/m^2)."""
    p = dict(EMITTERS[emitter])
    if params:
        p.update(params)
    s = I_pump / p["I_sat"]
    q = 1.0 / (1.0 + math.exp((Tm - p["T_q"]) / p["dT_q"]))
    qy = p["QY_max"] * s / (1 + s) * q
    lm = 0.0
    vis_W = 0.0
    for lam, share in p["lines"]:
        # photons emitted per absorbed photon: qy*share; energy ratio lambda_pump/lambda
        Pw = P_abs_pump * qy * share * p["lam_pump"] / lam
        lm += 683 * V(lam) * Pw
        if 380 <= lam <= 780:
            vis_W += Pw
    return lm, vis_W, qy


def incandescent_lumens(Tm, a, eps=0.9):
    """Thermal visible emission of a grey mote at Tm (lm), Planck integrated over 380-780 nm."""
    lam = np.arange(380e-9, 781e-9, 5e-9)
    h, c = 6.62607015e-34, 299792458.0
    B = 2 * h * c * c / lam ** 5 / np.expm1(h * c / (lam * KB * Tm))
    Vv = np.interp(lam * 1e9, _LAM, _V)
    return float(683 * eps * math.pi * 4 * math.pi * a * a * np.sum(B * Vv) * 5e-9)

"""Laser-safety bookkeeping for the MOTE projector (IEC 60825-1:2014 / ICNIRP 2013 values from R7).

Class 1 accessible emission limits (AEL) for CW, long exposure, small source (C6 = 1):
* 400-450 nm: 39 uW, the photochemical limit 3.9e-5 * C3 W with C3 = 1.
* 450-500 nm: 39 uW * C3, C3 = 10^(0.02 (lambda-450)); the thermal cap is 0.39 mW.
* 500-700 nm: 0.39 mW (thermal).
* 980 nm: 1.43 mW (3.9e-4 * C4, C4 = 3.63).
* 1064 nm: 1.97 mW.
* 1500-1800 nm: 10 mW.
Measurement aperture: 7 mm for 400-1400 nm; 3.5 mm at 1550 nm for t >= 10 s.

Conservative reading used here (R7 open item: the Table 11 reference point for an accessible focus):
* the image volume is accessible, so an eye can sit at a trap focus and receive the whole beam, giving P_beam <= AEL;
* at a head's exit window all beams overlap; with a Gaussian-apodised fill of radius R the centre irradiance is
  2 P_head / (pi R^2), giving P_head * 2 (r_ap/R)^2 <= AEL;
* single-fault rule (scan stall): a time-shared channel's peak power must itself be <= AEL.
"""
from __future__ import annotations

import math


def ael_class1(lam_nm):
    if 400 <= lam_nm < 450:
        return 39e-6
    if 450 <= lam_nm < 500:
        return min(39e-6 * 10 ** (0.02 * (lam_nm - 450)), 0.39e-3)
    if 500 <= lam_nm <= 700:
        return 0.39e-3
    if 900 <= lam_nm <= 1000:
        return 3.9e-4 * 10 ** (0.002 * (lam_nm - 700))
    if 1000 < lam_nm <= 1150:
        return 1.97e-3
    if 1500 <= lam_nm <= 1800:
        return 10e-3
    raise ValueError(f"no AEL tabulated for {lam_nm} nm")


def meas_aperture(lam_nm):
    return 3.5e-3 if lam_nm >= 1400 else 7e-3


def exit_fraction(lam_nm, R_head):
    """Fraction of a head's total power that passes the measurement aperture at the exit window."""
    r = meas_aperture(lam_nm) / 2
    return min(1.0, 2 * (r / R_head) ** 2)


def head_power_limit(lam_nm, R_head):
    return ael_class1(lam_nm) / exit_fraction(lam_nm, R_head)


def beam_through_pupil(P, w0, lam_nm, z, d_ap=None):
    """Power through an aperture at distance z beyond a Gaussian focus of waist w0."""
    lam = lam_nm * 1e-9
    d_ap = d_ap or meas_aperture(lam_nm)
    zR = math.pi * w0 * w0 / lam
    w = w0 * math.sqrt(1 + (z / zR) ** 2)
    return P * (1 - math.exp(-2 * (d_ap / 2) ** 2 / (w * w)))


def interlock_dose(P, w0, t_off):
    """Radiant exposure (J/m^2) at the focus spot before an obstruction interlock cuts the beam."""
    return P * t_off / (math.pi * w0 * w0)

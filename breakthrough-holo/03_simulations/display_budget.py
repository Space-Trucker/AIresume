"""Budget model for an air-plasma volumetric display: light, air chemistry and noise per voxel.

Each quantity has a nominal value and a (low, high) uncertainty band taken from the literature
notes in 01_research/. Symbols:
  E      absorbed energy per voxel (J)
  N_dot  voxel rate (voxels/s)
  eta_lm luminous output per absorbed W (lm/W)

Physics of the size scaling (see 02_theory/T2_plasma_budget.md):
  * Radiated fraction f_rad = x/(1+x), x = x_ref * r0/r_ref. A hot kernel radiates for a time
    ~tau_rad (set by density and temperature, which are roughly fixed by breakdown physics) but
    survives only ~r0/c_s before expansion quenches it, so x ~ (r0/c_s)/tau_rad.
    Calibrated so a ~0.3 mm ns-spark kernel radiates 22-34 % of E (R1 notes, energy-budget row).
  * Kernel radius r0 = max(focal radius, (3E/(4 pi eps_k))^(1/3)), with eps_k the kernel energy
    density at breakdown (a 50 mJ ns spark in 0.02 mm^3 gives eps_k ~ 2.5e9 J/m^3).
  * Luminous efficacy of the radiated energy (lm per radiated W) is calibrated so ns sparks give
    0.7-6 lm per absorbed W.
  * Acoustic energy = f_ac*E. Far-field N-wave duration T = k_T * R0/c with R0 = (E_ac/p0)^(1/3);
    k_T is calibrated so 50 mJ sparks peak at 50-100 kHz (R1 notes, acoustic-spectrum row).
  * Reactive species (O3 + NO + NO2) per absorbed J: 1e16-1.5e17 (filament and lightning/spark
    literature, R1 notes, chemistry rows).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from holo_common import C_SOUND, N_AIR, P_ATM, RHO_AIR

# ---------------- literature parameters: (nominal, low, high) ----------------
PARAMS = {
    "f_rad_ref": (0.28, 0.22, 0.34),          # radiated fraction of a ns spark kernel
    "r_ref": (150e-6, 100e-6, 200e-6),        # kernel radius of that spark (m)
    "lm_per_W_rad": (7.0, 2.5, 20.0),         # lm per radiated W (hot air-plasma continuum)
    "eps_k": (2.5e9, 1e9, 1e10),              # kernel energy density at breakdown (J/m^3)
    "f_ac": (0.6, 0.5, 0.8),                  # fraction of absorbed energy into the blast wave
    "k_T": (0.3, 0.15, 0.6),                  # N-wave duration factor (T = k_T R0/c); 50 mJ sparks peak 50-100 kHz
    "Y_react": (5e16, 3e15, 1.5e17),          # reactive molecules (O3+NOx) per absorbed J (fs filament data
                                              # imply ~5e15-1e16 per absorbed J; lightning/sparks ~1e17)
    "eta_mult": (1.0, 0.3, 3.0),              # model-form uncertainty on micro-spark luminous efficacy
}


def P(name, which="nom"):
    nom, lo, hi = PARAMS[name]
    return {"nom": nom, "lo": lo, "hi": hi}[which]


def kernel_radius(E, focal_radius=5e-6, eps_k=None):
    eps_k = P("eps_k") if eps_k is None else eps_k
    return np.maximum(focal_radius, (3 * np.asarray(E) / (4 * math.pi * eps_k)) ** (1 / 3))


def radiated_fraction(r0, f_ref=None, r_ref=None):
    f_ref = P("f_rad_ref") if f_ref is None else f_ref
    r_ref = P("r_ref") if r_ref is None else r_ref
    x_ref = f_ref / (1 - f_ref)
    x = x_ref * np.asarray(r0) / r_ref
    return x / (1 + x)


def luminous_efficacy(E, focal_radius=5e-6, sc=None):
    """lm per absorbed W for voxels of absorbed energy E (J). sc: optional param overrides."""
    sc = sc or {}
    r0 = kernel_radius(E, focal_radius, sc.get("eps_k"))
    f = radiated_fraction(r0, sc.get("f_rad_ref"), sc.get("r_ref"))
    return f * sc.get("lm_per_W_rad", P("lm_per_W_rad")) * sc.get("eta_mult", 1.0)


# ---------------- acoustics ----------------
def nwave_duration(E_ac, k_T=None):
    k_T = P("k_T") if k_T is None else k_T
    R0 = (np.asarray(E_ac) / P_ATM) ** (1 / 3)
    return k_T * R0 / C_SOUND


def audible_fraction(T, f_max=20e3):
    """Fraction of an N-wave's acoustic energy below f_max.

    Model spectrum |P(f)|^2 ~ f^2 exp(-(f/fc)^2) (zero-mean pulse), fc = 1/(pi T).
    Fraction below f_max = P(3/2, (f_max/fc)^2) (regularised lower incomplete gamma).
    """
    from scipy.special import gammainc
    fc = 1.0 / (math.pi * np.asarray(T))
    return gammainc(1.5, (f_max / fc) ** 2)


A_WEIGHT_TABLE = {  # IEC 61672 A-weighting (dB) at 1/3-octave centres
    1000: 0.0, 1250: 0.6, 1600: 1.0, 2000: 1.2, 2500: 1.3, 3150: 1.2, 4000: 1.0, 5000: 0.5,
    6300: -0.1, 8000: -1.1, 10000: -2.5, 12500: -4.3, 16000: -6.6, 20000: -9.3}


def audible_spl_random(N_dot, E, r=1.0, room_absorption_m2=20.0, sc=None):
    """A-weighted SPL (dB(A)) at distance r from a random-order voxel cloud.

    Incoherent sum (Campbell's theorem): power spectral density = rate * |P1(f)|^2.
    Direct field plus diffuse reverberant field (Sabine), per 1/3-octave band.
    """
    sc = sc or {}
    f_ac = sc.get("f_ac", P("f_ac"))
    E_ac = f_ac * np.asarray(E, dtype=float)
    T = nwave_duration(E_ac, sc.get("k_T"))
    from scipy.special import gammainc
    fc = 1.0 / (math.pi * T)
    total = 0.0
    for fcen, aw in A_WEIGHT_TABLE.items():
        f1, f2 = fcen / 2 ** (1 / 6), fcen * 2 ** (1 / 6)
        frac = gammainc(1.5, (f2 / fc) ** 2) - gammainc(1.5, (f1 / fc) ** 2)
        Wband = N_dot * E_ac * frac                       # acoustic power in band (W)
        I_dir = Wband / (4 * math.pi * r * r)
        I_rev = 4 * Wband / room_absorption_m2            # diffuse-field intensity-equivalent
        I = I_dir + I_rev
        total = total + I * 10 ** (aw / 10)
    return 10 * np.log10(np.maximum(total, 1e-30) / 1e-12)


# ---------------- chemistry ----------------
def room_steady_ppb(P_abs, room_m3=50.0, ach=0.5, cadr_m3h=400.0, scrub_eff=0.7, capture=0.0,
                    decay_per_h=0.5, Y=None):
    """Steady-state increment of reactive species (ppb) in a well-mixed room.

    Source S = Y*P_abs*(1-capture) molecules/s; sinks: ventilation, scrubber (CADR x efficiency),
    surface/chemical decay. capture = fraction trapped at the source by local exhaust.
    """
    Y = P("Y_react") if Y is None else Y
    S = Y * np.asarray(P_abs) * (1 - capture)
    Q = (ach * room_m3 + cadr_m3h * scrub_eff + decay_per_h * room_m3) / 3600.0   # m^3/s
    C = S / (Q * N_AIR)
    return C * 1e9


def breathing_zone_ppb(P_abs, r_face=0.5, D_t=0.005, Y=None, **room):
    """Room steady state + near-field plume increment at a face r_face from the hologram (E5)."""
    Y = P("Y_react") if Y is None else Y
    cap = room.get("capture", 0.0)
    nf = Y * np.asarray(P_abs) * (1 - cap) / (4 * math.pi * D_t * r_face) / N_AIR * 1e9
    return room_steady_ppb(P_abs, Y=Y, **room) + nf


def max_absorbed_power(limit_ppb=20.0, **kw):
    return limit_ppb / room_steady_ppb(1.0, **kw)


# ---------------- perception ----------------
def point_intensity_needed(L_stroke, stroke_width=1e-3, spacing=1e-3):
    """cd per point for dotted strokes to match a stroke of luminance L (cd/m^2) and width w."""
    return L_stroke * stroke_width * spacing


def energy_per_flash(L_stroke, frame_hz=60.0, focal_radius=5e-6, sc=None):
    """Absorbed energy per voxel flash so that one flash per frame gives stroke luminance L.

    Solves E * eta(E) = 4*pi*I_pt/frame_hz by bisection in log space.
    """
    Q = 4 * math.pi * point_intensity_needed(L_stroke) / frame_hz      # lm*s per flash
    lo, hi = 1e-12, 10.0
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if mid * float(luminous_efficacy(mid, focal_radius, sc)) < Q:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def display_budget(L_stroke, n_points, frame_hz=60.0, focal_radius=5e-6, sc=None, room=None):
    """Everything for one operating point: E per flash, rate, absorbed power, lm, ppb, dB(A)."""
    sc = sc or {}
    room = room or {}
    E = energy_per_flash(L_stroke, frame_hz, focal_radius, sc)
    N_dot = n_points * frame_hz
    P_abs = N_dot * E
    Phi = 4 * math.pi * point_intensity_needed(L_stroke) * n_points
    ppb = float(breathing_zone_ppb(P_abs, Y=sc.get("Y_react"), **room))
    dBA = float(audible_spl_random(N_dot, E, sc=sc))
    return dict(L=L_stroke, n_points=n_points, E_flash=E, voxel_rate=N_dot, P_abs=P_abs, lumens=Phi,
                eta=float(luminous_efficacy(E, focal_radius, sc)), ppb=ppb, dBA=dBA)

"""MOTE instrument: physics of a light-trapped, self-emitting micro-mote in room air (v1).

Each model is validated in validation/validate_mote.py.

Air, 1 atm, as a function of T:
* viscosity: Sutherland;
* conductivity: k(T) ~ T^0.82;
* density: ideal gas;
* mean free path: lambda = (mu/p) sqrt(pi R T / 2).

Heat balance of the mote (continuum, with the Fuchs temperature-jump correction and low-Pe forced convection):
    P_abs = 4 pi a [int_{T0}^{Tm} k dT] * Nu/2 / (1 + zeta/a)  +  eps sigma 4 pi a^2 (Tm^4 - T0^4)
    zeta = (2-alpha_T)/alpha_T * 2 gamma/(gamma+1) * lambda / Pr ;  Nu/2 = 1 + Pe/4  (Acrivos-Taylor)

Photophoretic force (Delta-T type):
* continuum form (Yalamov 1976; Reed 1977):
      F = C_ph * 9 pi mu^2 a I J1 / (2 rho T0 (k_p + 2 k_g));
* slip correction: [(1 + 3 c_m Kn)(1 + 2 c_t Kn k_p / (k_p + 2 k_g))]^-1, with c_m = 1.14, c_t = 2.18 (Talbot 1980 coefficients);
* prefactor (red team 4, Major 4; re-derived here): thermal creep gives F = 4 pi C_s mu nu T1/T with surface dipole
  T1 = |J1| I a / (k_p + 2 k_g), so the 9 pi/2 form corresponds to C_s = 9/8. C_ph = C_s/(9/8) spans 0.67 (Maxwell 3/4)
  to 1.04 (Talbot 1.17). Default C_ph = 1.0.
* the creep coefficient is nu/T = mu R/p, so rho and T are taken at the same state (v1 mixed rho(T_f) with T0, which
  inflated the force by T_f/T0; red team 4, Major 1).
* J1: J1 = 0.5 A only for skin-deep absorption (alpha a >~ 30). For finite alpha a, j1_over_A(alpha a) from a
  straight-ray Beer-Lambert model (checked against red team 4's refracting ray trace, within ~0.07).

Force in terms of absorbed power: with P_abs = A pi a^2 I,
    F = C_ph * 9 mu^2 * 0.5 * P_abs / (2 rho T0 a (k_p + 2k_g)) * slip,
which is proportional to P_abs / a. Because P_abs ~ a * dT, the force per kelvin of mote heating is independent of a.
This "heat-force identity" is the core scaling of the MOTE route.

Lateral force from an intensity gradient g = d ln I / dx across an opaque sphere lit along z:
    F_x / F_z = (3/8) g a.
This comes from the first moments of the absorbed flux over the lit hemisphere (derivation in 02_theory/T5).
The inner flank of an LG01 doughnut has g = 2/w, so eta_lat = 0.75 a / w.

Drag: Stokes, with the Oseen correction and the Cunningham slip factor.
"""
from __future__ import annotations

import math

import numpy as np

SIGMA = 5.670374e-8
KB = 1.380649e-23
G = 9.81
T0 = 293.15
P0 = 101325.0
R_AIR = 287.05
C_M, C_T, C_S_MAXWELL = 1.14, 2.18, 0.75
PR_AIR, GAMMA_AIR = 0.71, 1.4


def mu_air(T):
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)


def k_air(T):
    return 0.0257 * (T / 293.15) ** 0.82


def rho_air(T):
    return P0 / (R_AIR * T)


def mfp(T=T0):
    return mu_air(T) / P0 * math.sqrt(math.pi * R_AIR * T / 2)


def knudsen(a, T=T0):
    return mfp(T) / a


def cunningham(a, T=T0):
    kn = knudsen(a, T)
    return 1 + kn * (1.257 + 0.4 * math.exp(-1.1 / kn))


def k_integral(T):
    """int_{T0}^{T} k_air dT' (closed form of the power law)."""
    c = 0.0257 / 293.15 ** 0.82
    return c * (T ** 1.82 - T0 ** 1.82) / 1.82


def heat_loss(Tm, a, eps=0.9, v_rel=0.0, alpha_T=1.0):
    """Power (W) a mote at Tm loses to air (conduction with temperature jump, low-Pe convection) + radiation."""
    Tf = 0.5 * (T0 + Tm)
    zeta = (2 - alpha_T) / alpha_T * 2 * GAMMA_AIR / (GAMMA_AIR + 1) * mfp(Tf) / PR_AIR
    Pe = rho_air(Tf) * abs(v_rel) * 2 * a / mu_air(Tf) * PR_AIR
    conv = 1 + min(Pe, 1.0) / 4
    return 4 * math.pi * a * k_integral(Tm) * conv / (1 + zeta / a) + eps * SIGMA * 4 * math.pi * a * a * (Tm ** 4 - T0 ** 4)


def mote_temperature(P_abs, a, eps=0.9, v_rel=0.0, alpha_T=1.0):
    """Steady mote temperature for absorbed power P_abs (W), radius a (m)."""
    if P_abs <= 0:
        return T0
    lo, hi = T0, 6000.0
    for _ in range(100):
        Tm = 0.5 * (lo + hi)
        if heat_loss(Tm, a, eps, v_rel, alpha_T) > P_abs:
            hi = Tm
        else:
            lo = Tm
    return 0.5 * (lo + hi)


def thermal_time(a, rho_p=1500.0, cp=900.0, T=T0):
    """Mote thermal time constant (s): m c_p / (4 pi a k)."""
    m = 4 / 3 * math.pi * a ** 3 * rho_p
    return m * cp / (4 * math.pi * a * k_air(T))


def pp_slip(a, kp, T=T0):
    kn = knudsen(a, T)
    kg = k_air(T)
    return 1.0 / ((1 + 3 * C_M * kn) * (1 + 2 * C_T * kn * kp / (kp + 2 * kg)))


def photophoretic_force(a, I, kp, J1=0.5, Tm=T0, C_ph=1.0, slip=True):
    """Delta-T photophoretic force (N) on a sphere of radius a in intensity I (W/m^2); gas at film temperature."""
    Tf = 0.5 * (T0 + Tm)
    mu, rho, kg = mu_air(Tf), rho_air(Tf), k_air(Tf)
    s = pp_slip(a, kp, Tf) if slip else 1.0
    return C_ph * 9 * math.pi * mu ** 2 * a * I * J1 / (2 * rho * Tf * (kp + 2 * kg)) * s


def force_per_absorbed_watt(a, kp, Tm=T0, C_ph=1.0, slip=True, j1A=0.5):
    """F / P_abs (N/W): J1 = j1A * A, P_abs = A pi a^2 I. j1A = 0.5 for skin-deep absorption."""
    return photophoretic_force(a, 1.0, kp, J1=j1A, Tm=Tm, C_ph=C_ph, slip=slip) / (math.pi * a * a)


def j1_over_A(alpha_a):
    """|J1|/A for a sphere absorbing with coefficient alpha, lit along z (straight rays, Beer-Lambert, J1 = (3/4) M1/(P a))."""
    if alpha_a > 200:
        return 0.5
    n = 800
    b = (np.arange(n) + 0.5) / n
    L = 2 * np.sqrt(1 - b * b)
    Ab = 1 - np.exp(-alpha_a * L)
    s_mean = 1 / alpha_a - L * np.exp(-alpha_a * L) / np.maximum(Ab, 1e-300)
    P = np.sum(Ab * b)
    M1 = np.sum(Ab * (-L / 2 + s_mean) * b)
    return float(-0.75 * M1 / P)


def absorptance(alpha_a):
    n = 800
    b = (np.arange(n) + 0.5) / n
    return float(np.sum((1 - np.exp(-alpha_a * 2 * np.sqrt(1 - b * b))) * 2 * b) / n)


def mote_material(a, alpha_trap, k_core, k_skin=0.0, skin="none"):
    """Consistent mote: returns (A_trap, J1/A, k_eff).
    skin='none': absorber dispersed through the mote (alpha = volume absorption).
    skin='continuous': thin absorbing shell (depth ~ 2/alpha) of conductivity k_skin, which spreads the heat dipole:
      k_eff = k_core + 4 k_skin / (alpha a)   (red team 4, C1).
    skin='islands': discontinuous absorber layer (no lateral conduction): k_eff = k_core."""
    aa = alpha_trap * a
    k_eff = k_core + (4 * k_skin / aa if skin == "continuous" else 0.0)
    return absorptance(aa), j1_over_A(aa), k_eff


def k_coated_sphere(k_core, k_shell, core_frac):
    """Effective conductivity of a sphere with a core of radius core_frac*a inside a shell (Maxwell-Garnett /
    coated-sphere result): k_s [(k_c+2k_s) + 2 phi (k_c-k_s)] / [(k_c+2k_s) - phi (k_c-k_s)], phi = core_frac^3."""
    phi = core_frac ** 3
    return k_shell * ((k_core + 2 * k_shell) + 2 * phi * (k_core - k_shell)) / ((k_core + 2 * k_shell) - phi * (k_core - k_shell))


def figure_of_merit(j1A, k_eff, T=T0):
    """(J1/A)/(k_p + 2 k_g) in m K / W: speed, force per kelvin and heat budget all scale with it."""
    return j1A / (k_eff + 2 * k_air(T))


def drag(a, v, T=T0, slip=True):
    mu, rho = mu_air(T), rho_air(T)
    Re = rho * abs(v) * 2 * a / mu
    c = cunningham(a, T) if slip else 1.0
    return 6 * math.pi * mu * a * v * (1 + 3 / 16 * Re) / c


def settling_velocity(a, rho_p, slip=True):
    return 2 * rho_p * G * a * a / (9 * mu_air(T0)) * (cunningham(a) if slip else 1.0)


def brownian_rms(a, t, T=T0):
    D = KB * T * cunningham(a, T) / (6 * math.pi * mu_air(T) * a)
    return math.sqrt(2 * D * t)


def eta_lateral(a, w, kappa=0.75):
    """v1 linear law (3/8) g a with g = 2/w. Valid only for a << w; kept for reference. Use lg01_trap()."""
    return min(1.0, kappa * a / w)


_LG_CACHE = {}


def lg01_trap(a, w, n=61):
    """Exact passive LG01 (doughnut) trap for an opaque sphere lit along z (red team 4, Major 2; checked here).
    Surface-flux dipole integrated over the lit hemisphere, maximised over mote position (restoring side only).
    Returns (eta, f_I): eta = lateral restoring force per absorbed watt relative to the ideal axial force per absorbed
    watt; f_I = mean intensity on the mote at that position, as a fraction of the ring peak 2P/(e pi w^2)."""
    key = round(a / w, 3)
    if key in _LG_CACHE:
        return _LG_CACHE[key]
    r = a / w
    th = np.linspace(0, math.pi / 2, n)
    ph = np.linspace(0, 2 * math.pi, 2 * n)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    sx, sy, cz = np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)
    dA = np.sin(TH)
    best_Mx, res = 0.0, (0.0, 0.0)
    for x0 in np.linspace(0.01, 1.2, 120):
        X, Y = x0 + r * sx, r * sy
        r2 = X * X + Y * Y
        q = 2 * r2 * np.exp(-2 * r2) * cz          # LG01 in units of 2P/(pi w^2), times cos(theta)
        Mx = np.trapezoid(np.trapezoid(q * sx * dA, ph, axis=1), th)
        Pq = np.trapezoid(np.trapezoid(q * dA, ph, axis=1), th)
        if Mx > best_Mx:                            # hot side at +x -> force toward the axis (restoring)
            best_Mx = Mx
            res = (float(Mx / (Pq * 2 / 3)), float(Pq / (math.pi * 2 / math.e)))
    _LG_CACHE[key] = res
    return res


# --- photometry ------------------------------------------------------------------------------
_LAM = np.arange(380, 790, 10)
_V = np.array([0.0000390, 0.000120, 0.000396, 0.00121, 0.00400, 0.0116, 0.0230, 0.0380, 0.0600, 0.0910,
               0.139, 0.208, 0.323, 0.503, 0.710, 0.862, 0.954, 0.995, 0.995, 0.952,
               0.870, 0.757, 0.631, 0.503, 0.381, 0.265, 0.175, 0.107, 0.0610, 0.0320,
               0.0170, 0.00821, 0.00410, 0.00209, 0.00105, 0.000520, 0.000249, 0.000120, 0.0000600, 0.0000300,
               0.0000149])


def V(lam_nm):
    return float(np.interp(lam_nm, _LAM, _V, left=0.0, right=0.0))


# --- emitters --------------------------------------------------------------------------------
# UC presets (R6 section 5): QY(I,T) = QY_max * s/(1+s) * q(T); s = I/I_sat; q = 1/(1+exp((T-T_q)/dT_q)).
# 'lines' = (lambda_nm, photon share of the upconverted output). The Yb absorption cross-section and density give the
# single-pass absorptance A = 1 - exp(-alpha * 4a/3) (mean chord of a sphere).
N_CATION_NAYF4 = 1.35e28          # cation sites per m^3 in beta-NaYF4
SIGMA_YB_980 = 1.0e-24            # m^2 (1.0e-20 cm^2, R6: 0.9-1.2e-20)
UC = {
    "Er_green_red": dict(lines=[(540, 0.6), (655, 0.4)], QY_max=0.10, I_sat=5e4, T_q=600.0, dT_q=50.0, lam_pump=980, x_Yb=0.20),
    "Er_green_red_Yb98": dict(lines=[(540, 0.6), (655, 0.4)], QY_max=0.07, I_sat=5e4, T_q=600.0, dT_q=50.0, lam_pump=980, x_Yb=0.98),
    "Tm_blue": dict(lines=[(475, 0.15), (800, 0.85)], QY_max=0.02, I_sat=30e4, T_q=550.0, dT_q=50.0, lam_pump=980, x_Yb=0.20),
}
# Down-converting phosphors (R6 section 4; nitride/oxynitride Eu2+), pumped by a violet or blue beam.
# QY = internal quantum efficiency; A_abs = absorptance of a few-micron grain at the pump wavelength; T50 = 50 % quench.
PHOSPHOR = {
    "cyan_BaSi2O2N2": dict(lam_em=497, fwhm=35, QY=0.90, A_abs=0.7, T50=520.0, dT_q=40.0),
    # R9 (snippet): BaSi2O2N2:Eu quench onset reported near 450 C; optimistic sensitivity case
    "cyan_BaSi2O2N2_hiT": dict(lam_em=497, fwhm=35, QY=0.90, A_abs=0.7, T50=650.0, dT_q=40.0),
    "cyan_ideal900": dict(lam_em=497, fwhm=35, QY=0.95, A_abs=0.7, T50=1000.0, dT_q=40.0),   # hypothetical bound only
    "green_bSiAlON": dict(lam_em=540, fwhm=55, QY=0.85, A_abs=0.6, T50=600.0, dT_q=50.0),
    # beta-SiAlON:Eu is a robust green (high thermal stability; excitable to ~480 nm) [MEMORY]; optimistic T50
    "green_bSiAlON_hiT": dict(lam_em=540, fwhm=55, QY=0.85, A_abs=0.6, T50=650.0, dT_q=50.0),
    "red_CaAlSiN3": dict(lam_em=650, fwhm=90, QY=0.85, A_abs=0.8, T50=600.0, dT_q=50.0),
}


def band_V(lam_c, fwhm):
    """Mean V over a Gaussian emission band (luminous efficacy of the band = 683 * band_V lm/W)."""
    lam = np.linspace(lam_c - 2 * fwhm, lam_c + 2 * fwhm, 81)
    wgt = np.exp(-4 * math.log(2) * ((lam - lam_c) / fwhm) ** 2)
    return float(np.sum(wgt * np.interp(lam, _LAM, _V, left=0, right=0)) / np.sum(wgt))


def uc_absorptance(a, x_Yb):
    alpha = N_CATION_NAYF4 * x_Yb * SIGMA_YB_980
    return 1 - math.exp(-alpha * 4 * a / 3)


def uc_lumens(P_abs_pump, I_pump, Tm, emitter="Er_green_red", params=None):
    """Visible lumens emitted by an upconverting mote absorbing P_abs_pump (W) at intensity I_pump (W/m^2)."""
    p = dict(UC[emitter])
    if params:
        p.update(params)
    s = I_pump / p["I_sat"]
    q = 1.0 / (1.0 + math.exp(min((Tm - p["T_q"]) / p["dT_q"], 700.0)))
    qy = p["QY_max"] * s / (1 + s) * q
    lm = 0.0
    vis_W = 0.0
    for lam, share in p["lines"]:
        Pw = P_abs_pump * qy * share * p["lam_pump"] / lam        # photons out per photon in x energy ratio
        lm += 683 * V(lam) * Pw
        if 380 <= lam <= 780:
            vis_W += Pw
    return lm, vis_W, qy


def phosphor_lumens(P_abs_pump, lam_pump, Tm, name="cyan_BaSi2O2N2"):
    """Lumens and emitted power of a down-converting phosphor mote; returns (lm, W_out, heat_W)."""
    p = PHOSPHOR[name]
    q = 1.0 / (1.0 + math.exp(min((Tm - p["T50"]) / p["dT_q"], 700.0)))
    W_out = P_abs_pump * p["QY"] * q * lam_pump / p["lam_em"]
    return 683 * band_V(p["lam_em"], p["fwhm"]) * W_out, W_out, P_abs_pump - W_out


def incandescent_lumens(Tm, a, eps=0.9):
    """Thermal visible emission of a grey mote at Tm (lm), Planck integrated over 380-780 nm."""
    lam = np.arange(380e-9, 781e-9, 5e-9)
    h, c = 6.62607015e-34, 299792458.0
    B = 2 * h * c * c / lam ** 5 / np.expm1(h * c / (lam * KB * Tm))
    Vv = np.interp(lam * 1e9, _LAM, _V)
    return float(683 * eps * math.pi * 4 * math.pi * a * a * np.sum(B * Vv) * 5e-9)


EMITTERS = UC  # backward-compatible name used by v0 scripts

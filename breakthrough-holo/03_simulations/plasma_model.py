"""Plasma-voxel physics: strong-field ionisation of air in a focused ultrashort pulse.

Model
-----
* Photo-ionisation of O2 and N2: PPT (Perelomov-Popov-Terent'ev) cycle-averaged rate, linear
  polarisation, with Talebpour's effective charges (Z_O2 = 0.53, Z_N2 = 0.9). Formula as given in
  Couairon & Mysyrowicz, Phys. Rep. 441, 47 (2007), Sec. 4.2.
* Collisional (avalanche) ionisation via inverse bremsstrahlung, Drude cross-section
  sigma_ib = k0*w*tau_c / (n_c (1 + w^2 tau_c^2)), with tau_c = 350 fs for air (Couairon 2007).
* Linear focusing of a Gaussian beam (valid while P_peak << P_cr and plasma defocusing is weak;
  both are checked and reported).
* Energy deposited = ionisation energy + inverse-bremsstrahlung heating integrated over the focus.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.special import dawsn, gamma as Gamma

from holo_common import N_AIR, N2_AIR, c, e, eps0, me

AU_TIME = 2.418_884_326e-17      # s
AU_INTENSITY = 3.509_445e16      # W/cm^2 (for field amplitude 1 a.u.)
HARTREE_EV = 27.211_386

SPECIES = {
    # name: (Ip eV, Z_eff, fraction of air)
    "O2": (12.063, 0.53, 0.21),
    "N2": (15.576, 0.90, 0.78),
}
TAU_C = 350e-15  # electron-neutral collision time in air (s), Couairon 2007


def ppt_rate(I_Wcm2, lam_m, species="O2", kmax_terms=400):
    """Cycle-averaged PPT ionisation rate (1/s) for intensity array I (W/cm^2)."""
    Ip_eV, Z, _ = SPECIES[species]
    I = np.atleast_1d(np.asarray(I_Wcm2, dtype=float))
    out = np.zeros_like(I)
    Ip = Ip_eV / HARTREE_EV
    w = 45.563_352_5 / (lam_m * 1e9)              # photon energy in a.u.
    nstar = Z / math.sqrt(2 * Ip)
    lstar = nstar - 1
    C2 = 2 ** (2 * nstar) / (nstar * Gamma(nstar + lstar + 1) * Gamma(nstar - lstar))
    E0 = (2 * Ip) ** 1.5
    mask = I > 1e8
    E = np.sqrt(I[mask] / AU_INTENSITY)
    g = w * math.sqrt(2 * Ip) / E                  # Keldysh gamma
    gfun = 3 / (2 * g) * ((1 + 1 / (2 * g * g)) * np.arcsinh(g) - np.sqrt(1 + g * g) / (2 * g))
    nu = Ip / w * (1 + 1 / (2 * g * g))
    alpha = 2 * (np.arcsinh(g) - g / np.sqrt(1 + g * g))
    beta = 2 * g / np.sqrt(1 + g * g)
    # sum over photon numbers kappa >= nu
    k0 = np.ceil(nu)
    kk = k0[:, None] + np.arange(kmax_terms)[None, :]
    d = kk - nu[:, None]
    terms = np.exp(-alpha[:, None] * d) * dawsn(np.sqrt(beta[:, None] * d))
    A0 = 4 / math.sqrt(3 * math.pi) * (g * g / (1 + g * g)) * terms.sum(axis=1)
    W_au = (math.sqrt(6 / math.pi) * C2 * Ip * (2 * E0 / (E * np.sqrt(1 + g * g))) ** (2 * nstar - 1.5)
            * A0 * np.exp(-2 * E0 * gfun / (3 * E)))
    out[mask] = W_au / AU_TIME
    return out


_PPT_CACHE = {}


def ppt_rate_fast(I_Wcm2, lam_m, species="O2"):
    """PPT rate via log-log interpolation of a 400-point table (1e11..1e16 W/cm^2)."""
    key = (round(lam_m * 1e12), species)
    if key not in _PPT_CACHE:
        grid = np.logspace(11, 16, 400)
        rates = ppt_rate(grid, lam_m, species)
        _PPT_CACHE[key] = (np.log(grid), np.log(np.maximum(rates, 1e-300)))
    lg, lr = _PPT_CACHE[key]
    I = np.asarray(I_Wcm2, dtype=float)
    out = np.exp(np.interp(np.log(np.maximum(I, 1e-30)), lg, lr, left=-690.0, right=lr[-1]))
    return np.where(I > 1e11, out, 0.0)


def sigma_ib(lam_m, ne=None, Te_eV=5.0, lnL=5.0):
    """Inverse-bremsstrahlung (Drude) cross-section per electron, m^2.

    Collision frequency = electron-neutral (1/350 fs, Couairon 2007) + electron-ion
    (Spitzer: nu_ei = 2.91e-6 * ne[cm^-3] * lnL * Te^-1.5 s^-1, NRL Plasma Formulary).
    Te is an assumed effective electron temperature of the laser-heated plasma (default 5 eV).
    """
    w = 2 * math.pi * c / lam_m
    nc = eps0 * me * w * w / e ** 2
    k0 = w / c
    nu = 1.0 / TAU_C
    if ne is not None:
        nu = nu + 2.91e-6 * (np.asarray(ne) * 1e-6) * lnL * Te_eV ** -1.5
    tau = 1.0 / nu
    return k0 * w * tau / (nc * (1 + (w * tau) ** 2))


def critical_power(lam_m, n2=N2_AIR):
    """Critical power for self-focusing (Marburger, Gaussian beam), W."""
    return 3.77 * lam_m ** 2 / (8 * math.pi * n2)


def critical_density(lam_m):
    w = 2 * math.pi * c / lam_m
    return eps0 * me * w * w / e ** 2   # m^-3


def simulate_voxel(E_pulse, lam_m, NA, tau_fwhm, nr=48, nz=160, nt=240, avalanche=True, Te_eV=5.0):
    """Ionisation and absorption in the focal volume of a Gaussian pulse.

    Retarded-time frame (tau = t - z/c): for each time slice the pulse is propagated through the
    focus from front to back, and depleted by inverse-bremsstrahlung absorption
    alpha = sigma_ib * n_e (plus ionisation losses). Linear (vacuum) focusing geometry: plasma
    defocusing is NOT modelled; its importance is reported through ne/nc and phase_defocus.

    E_pulse: J, lam_m: m, NA: focusing half-angle (w0 = lam/(pi NA)), tau_fwhm: s
    """
    w0 = lam_m / (math.pi * NA)
    zR = math.pi * w0 ** 2 / lam_m
    P_peak = 0.9394 * E_pulse / tau_fwhm
    I0 = 2 * P_peak / (math.pi * w0 ** 2)          # W/m^2
    r = np.linspace(0, 3.0 * w0, nr)
    z = np.linspace(-4.0 * zR, 4.0 * zR, nz)
    dr, dz = r[1] - r[0], z[1] - z[0]
    R, Z = np.meshgrid(r, z, indexing="ij")
    wz = w0 * np.sqrt(1 + (Z / zR) ** 2)
    Ilin = I0 * (w0 / wz) ** 2 * np.exp(-2 * R ** 2 / wz ** 2)      # W/m^2 (no depletion)
    ring = 2 * math.pi * np.maximum(R, dr / 4) * dr                   # annulus area
    ring[0, :] = math.pi * (dr / 2) ** 2
    dV = ring * dz
    t = np.linspace(-2.0 * tau_fwhm, 2.0 * tau_fwhm, nt)
    dt = t[1] - t[0]
    env = np.exp(-4 * math.log(2) * t ** 2 / tau_fwhm ** 2)
    nO2 = SPECIES["O2"][2] * N_AIR * np.ones_like(Ilin)
    nN2 = SPECIES["N2"][2] * N_AIR * np.ones_like(Ilin)
    ne = np.zeros_like(Ilin)
    Eion = np.zeros_like(Ilin)
    Eib = np.zeros_like(Ilin)
    UiO2 = SPECIES["O2"][0] * e
    UiN2 = SPECIES["N2"][0] * e
    for k in range(nt):
        # depletion along z by IB absorption with current electron density
        alpha = (sigma_ib(lam_m, ne, Te_eV) * ne) if avalanche else np.zeros_like(ne)   # 1/m
        tau_opt = np.cumsum(alpha, axis=1) * dz - alpha * dz        # optical depth before each cell
        It = Ilin * env[k] * np.exp(-tau_opt)
        Icm = It * 1e-4
        wO = ppt_rate_fast(Icm, lam_m, "O2")
        wN = ppt_rate_fast(Icm, lam_m, "N2")
        dnO = nO2 * -np.expm1(-wO * dt)
        dnN = nN2 * -np.expm1(-wN * dt)
        # IB energy absorbed in this slice (cannot exceed the slice's energy passing through the cell)
        heat = np.minimum(alpha * It * dt, It * dt / dz)            # J/m^3
        neutrals = np.maximum(nO2 - dnO + nN2 - dnN, 0.0)
        if avalanche:
            dn_av = np.minimum(heat / (1.5 * UiO2) * (neutrals / (nO2 + nN2 + 1.0)), neutrals)
        else:
            dn_av = np.zeros_like(ne)
        fO = np.where(neutrals > 0, (nO2 - dnO) / np.maximum(neutrals, 1.0), 0.0)
        nO2 = np.maximum(nO2 - dnO - dn_av * fO, 0.0)
        nN2 = np.maximum(nN2 - dnN - dn_av * (1 - fO), 0.0)
        ne = ne + dnO + dnN + dn_av
        Eion += dnO * UiO2 + dnN * UiN2
        Eib += heat
    Ne = float((ne * dV).sum())
    E_dep = float(((Eion + Eib) * dV).sum())
    ne_pk = float(ne.max())
    thr = max(0.01 * ne_pk, 1e22)
    inside = ne > thr
    Vp = float((dV * inside).sum())
    if inside.any():
        r_ext = float(r[inside.any(axis=1)].max())
        zs = z[inside.any(axis=0)]
        z_len = float(zs.max() - zs.min())
    else:
        r_ext = z_len = 0.0
    nc = critical_density(lam_m)
    # plasma-defocusing phase across the plasma: k * (ne/(2 nc)) * length
    phase = 2 * math.pi / lam_m * (ne_pk / (2 * nc)) * max(z_len, dz)
    return dict(E_pulse=E_pulse, lam=lam_m, NA=NA, tau=tau_fwhm, w0=w0, zR=zR, I0_Wcm2=I0 * 1e-4,
                P_peak=P_peak, P_over_Pcr=P_peak / critical_power(lam_m), Ne=Ne, ne_peak=ne_pk,
                ne_over_nc=ne_pk / nc, E_dep=E_dep, E_ion=float((Eion * dV).sum()),
                E_ib=float((Eib * dV).sum()), abs_frac=E_dep / E_pulse,
                plasma_volume=Vp, plasma_diam=2 * r_ext, plasma_len=z_len, phase_defocus=phase)

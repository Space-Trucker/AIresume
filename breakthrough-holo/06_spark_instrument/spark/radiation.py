"""SPARK radiation: optically thin LTE emission of equilibrium air plasma, tabulated on (rho, T).

Continuum (free-free + free-bound), hydrogenic Kramers-Unsoeld form with a Biberman factor XI:
  j_nu(4pi) = C * z^2 n_e n_z T^-1/2 * exp(-h nu/kT) * [1 + XI(exp(min(h nu, chi_g)/kT) - 1)
              + sum_edges w (2 chi/kT) exp(chi/kT) H(h nu - chi)]
  C = 6.8e-51 W m^-3 Hz^-1 m^6 K^1/2 (Rybicki & Lightman eq. 5.14b in SI)
  chi_g: binding energy of the lowest merged excited level; edges: ground/metastable levels.
Lines: LTE upper-level populations x A x h nu, for the strongest N I, O I, N II, O II multiplets
  (multiplet-summed gA and upper energies rounded from NIST ASD; flagged +-2x in the model ledger).
Not included (ledger): molecular bands (N2, N2+, NO), e-neutral bremsstrahlung, VUV resonance lines
  (treated as trapped), line broadening/self-absorption (escape handled per band at run time).
Outputs per (rho, T) cell in W/m^3 (4 pi): bands euv (<102 nm), vuv (102-200), uvc, uvb, uva, vis, ir;
  lumens/m^3 (photopic), actinic-weighted W/m^3 (ICNIRP S(lambda)); photon rates for O2 photolysis
  (130-200 nm) and ionising (<102 nm); and continuum absorption coefficients at 5 probe wavelengths.
"""
from __future__ import annotations

import math
import os

import numpy as np

from eos import (ION, LEVELS, NA, NZ, P0, X_N2, X_O2, cantera_state, kB, h, eV, saha_state, M_N, M_O)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "rad_table.npz")
c = 299792458.0
C_KR = 6.8e-51
XI = 1.5
LAM = np.geomspace(40e-9, 2500e-9, 700)
NU = c / LAM
BANDS = {"euv": (0, 102e-9), "vuv": (102e-9, 200e-9), "uvc": (200e-9, 280e-9), "uvb": (280e-9, 315e-9),
         "uva": (315e-9, 400e-9), "vis": (400e-9, 700e-9), "ir": (700e-9, 1e-3)}
PROBES = np.array([90e-9, 150e-9, 250e-9, 550e-9, 900e-9])

# (element, charge of emitting species, lambda nm, sum gA s^-1, E_upper eV)  -- multiplet totals, ~NIST
LINES = [
    ("N", 0, 746.8, 1.5e8, 11.996), ("N", 0, 868.3, 5.0e8, 11.76), ("N", 0, 821.6, 5.0e8, 11.84),
    ("N", 0, 493.5, 1.0e7, 12.97), ("N", 0, 411.0, 2.0e7, 13.70),
    ("O", 0, 777.4, 5.5e8, 10.74), ("O", 0, 844.6, 2.9e8, 10.99), ("O", 0, 615.8, 1.1e8, 12.75),
    ("O", 0, 645.4, 1.5e7, 12.66), ("O", 0, 533.0, 3.0e7, 13.07), ("O", 0, 926.6, 3.0e8, 12.08),
    ("N", 1, 567.9, 8.8e8, 20.65), ("N", 1, 500.5, 2.0e9, 23.14), ("N", 1, 463.0, 5.0e8, 21.16),
    ("N", 1, 399.5, 6.8e8, 21.60), ("N", 1, 444.7, 5.5e8, 23.20), ("N", 1, 648.2, 1.0e8, 20.41),
    ("N", 1, 661.1, 1.5e8, 21.60), ("N", 1, 343.7, 3.0e8, 22.10),
    ("O", 1, 441.5, 8.0e8, 26.25), ("O", 1, 464.9, 3.0e9, 25.66), ("O", 1, 434.9, 1.0e9, 25.85),
    ("O", 1, 407.2, 2.0e9, 28.80), ("O", 1, 391.9, 5.0e8, 26.30),
]
CHI_G = {1: 4.0, 2: 11.0, 3: 20.0, 4: 30.0, 5: 45.0, 6: 60.0, 7: 80.0}   # eV, lowest merged level, by ion charge

# Vacuum-UV lines (review finding 2). (element, charge, lambda nm, g_u, g_l, E_u eV, E_l eV, A s^-1),
# multiplet-averaged, rounded from NIST ASD [MEMORY-flagged, +-3x]. Emission escapes through Voigt wings.
VUV_LINES = [
    ("N", 0, 120.0, 12, 4, 10.33, 0.0, 4.0e8), ("N", 0, 113.4, 12, 4, 10.93, 0.0, 1.5e8),
    ("N", 0, 149.3, 6, 10, 10.69, 2.38, 2.6e8), ("N", 0, 174.3, 6, 6, 10.69, 3.58, 5.0e7),
    ("O", 0, 130.4, 3, 9, 9.52, 0.0, 2.0e8), ("O", 0, 102.7, 15, 9, 12.08, 0.0, 4.0e7),
    ("N", 1, 108.5, 15, 9, 11.44, 0.0, 3.7e8), ("N", 1, 91.6, 9, 9, 13.54, 0.0, 1.2e9),
    ("O", 1, 83.4, 12, 4, 14.87, 0.0, 8.0e8),
]
STARK_REF_NM = 0.01      # Stark FWHM (nm) at n_e = 1e23 m^-3 for these lines; uncertain x0.3-3 (ledger)
AMU_ = 1.66053907e-27

# Molecular band systems in LTE (review finding 9): (molecule, T_e eV, g_u/g_x, A s^-1, [(l0,l1,share)...])
MOL_BANDS = [
    ("N2", 11.03, 6.0, 2.5e7, [(295, 320, 0.2), (330, 340, 0.35), (350, 360, 0.25), (370, 405, 0.2)]),   # N2 2+
    ("N2", 7.39, 6.0, 1.5e5, [(580, 700, 0.25), (700, 1050, 0.75)]),                                  # N2 1+
    ("N2+", 3.17, 1.0, 1.6e7, [(385, 395, 0.4), (420, 432, 0.3), (455, 480, 0.3)]),                   # N2+ 1-
    ("NO", 5.48, 0.5, 5.0e6, [(200, 240, 0.5), (240, 300, 0.5)]),                                     # NO gamma
    ("NO", 5.69, 1.0, 3.0e5, [(220, 300, 0.6), (300, 380, 0.4)]),                                     # NO beta
]


def _V():
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "..", "03_simulations"))
    from holo_common import V_photopic
    return V_photopic(LAM * 1e9)


def _S():
    tab = {180: 0.012, 190: 0.019, 200: 0.03, 210: 0.075, 220: 0.12, 230: 0.19, 240: 0.30, 250: 0.43, 254: 0.5, 260: 0.65, 270: 1.0,
           280: 0.88, 290: 0.64, 297: 0.46, 300: 0.30, 305: 0.06, 310: 0.015, 315: 0.003, 320: 0.001,
           330: 0.00041, 340: 0.00028, 350: 0.0002, 360: 0.00013, 370: 0.000093, 380: 0.000064,
           390: 0.000045, 400: 0.00003}
    l = LAM * 1e9
    s = np.exp(np.interp(l, list(tab), np.log(list(tab.values()))))
    s[(l < 180) | (l > 400)] = 0.0
    return s


def composition(T, rho, gas):
    """Number densities: ne, and dict (el, z) -> n for atoms/atomic ions (+ molecular ions as z=1)."""
    if T <= 16000.0:
        st = cantera_state(gas, T, rho)
        n = st["X"] * st["P"] / (kB * T)
        idx = {s: gas.species_index(s) for s in gas.species_names}
        comp = {("N", 0): n[idx["N"]], ("O", 0): n[idx["O"]], ("N", 1): n[idx["N+"]], ("O", 1): n[idx["O+"]],
                ("mol", 1): n[idx["NO+"]] + n[idx["N2+"]] + n[idx["O2+"]],
                "N2": n[idx["N2"]], "NO": n[idx["NO"]], "N2+": n[idx["N2+"]]}
        for el in ("N", "O"):
            for z in range(2, NZ[el]):
                comp[(el, z)] = 0.0
        return st["ne"], comp
    s = saha_state(T, rho)
    n_mol = rho / (X_N2 * 2 * M_N + X_O2 * 2 * M_O)
    nuc = {"N": 2 * X_N2 * n_mol, "O": 2 * X_O2 * n_mol}
    comp = {(el, z): nuc[el] * s["f" + el][z] for el in ("N", "O") for z in range(NZ[el])}
    comp[("mol", 1)] = 0.0
    comp["N2"] = comp["NO"] = comp["N2+"] = 0.0
    return s["ne"], comp


def spectrum(T, ne, comp):
    """Emission j_lambda (W m^-3 m^-1, 4 pi) and absorption coefficient kappa(lambda) (m^-1)."""
    kT = kB * T
    hnu = h * NU
    jnu = np.zeros_like(NU)
    for z in range(1, max(NZ.values())):
        nz = sum(comp.get((el, z), 0.0) for el in ("N", "O")) + (comp[("mol", 1)] if z == 1 else 0.0)
        if nz <= 0:
            continue
        base = C_KR * z * z * ne * nz / math.sqrt(T) * np.exp(-hnu / kT)
        chig = CHI_G[z] * eV
        term = 1.0 + XI * (np.exp(np.minimum(hnu, chig) / kT) - 1.0)
        # explicit ground-state edges of the recombined species (charge z-1), weight by element share
        for el in ("N", "O"):
            if z - 1 >= len(ION[el]):
                continue
            share = comp.get((el, z), 0.0) / nz if nz > 0 else 0.0
            chi = ION[el][z - 1] * eV
            w = share * 0.5
            term = term + w * (2 * chi / kT) * np.where(hnu >= chi, np.exp(np.minimum(chi / kT, 700.0)), 0.0)
        jnu += base * term
    jlam = jnu * NU / LAM                     # j_lambda = j_nu * c / lambda^2
    # lines (deposited in one wavelength bin each)
    from eos import part_fn
    for el, z, lam_nm, gA, Eu in LINES:
        n = comp.get((el, z), 0.0)
        if n <= 0:
            continue
        Z, _ = part_fn(el, z, T)
        power = n * gA * math.exp(-Eu * eV / kT) / Z * h * c / (lam_nm * 1e-9)     # W/m^3
        k = int(np.argmin(np.abs(LAM - lam_nm * 1e-9)))
        dl = (LAM[min(k + 1, len(LAM) - 1)] - LAM[max(k - 1, 0)]) / 2
        jlam[k] += power / dl
    # molecular bands (LTE upper-state populations, rovibrational partition ratio taken as 1: ledger +-2x)
    for mol, Te, gr, A, parts in MOL_BANDS:
        nm_ = comp.get(mol, 0.0)
        if nm_ <= 0:
            continue
        nu_pop = nm_ * gr * math.exp(-Te * eV / kT)
        for l0, l1, share in parts:
            lam_c = 0.5 * (l0 + l1) * 1e-9
            P = nu_pop * A * h * c / lam_c * share                 # W/m^3
            m = (LAM >= l0 * 1e-9) & (LAM < l1 * 1e-9)
            if m.any():
                jlam[m] += P / (l1 - l0) / 1e-9
    # Kirchhoff absorption of the continuum. j_nu (4 pi, spontaneous) = 4 pi kappa' B_nu with kappa' the
    # absorption coefficient corrected for stimulated emission, which is what governs escape.
    # (v1 multiplied by an extra (1-exp(-h nu/kT))^-1: review finding 7, fixed.)
    Bnu = 2 * h * NU ** 3 / c ** 2 / np.expm1(np.minimum(hnu / kT, 700.0))
    kappa = jnu / (4 * math.pi * np.maximum(Bnu, 1e-300))
    return jlam, kappa


def vuv_line_data(T, ne, comp, stark_nm=None):
    """Per VUV line: emissivity (W/m^3, 4 pi), line-centre absorption coefficient k0 (1/m), damping a."""
    from eos import part_fn
    stark_nm = STARK_REF_NM if stark_nm is None else stark_nm
    kT = kB * T
    out = []
    for el, z, lam_nm, gu, gl, Eu, El, A in VUV_LINES:
        n = comp.get((el, z), 0.0)
        lam = lam_nm * 1e-9
        nu0 = c / lam
        if n <= 0:
            out.append((0.0, 0.0, 1e-3))
            continue
        Z, _ = part_fn(el, z, T)
        nu_ = n * gu * math.exp(-Eu * eV / kT) / Z
        nl_ = n * gl * math.exp(-El * eV / kT) / Z
        j = nu_ * A * h * nu0
        m_at = (14.0067 if el == "N" else 15.999) * AMU_
        dnuD = nu0 / c * math.sqrt(2 * kT / m_at)                  # Doppler 1/e half-width (Hz)
        fwhm_stark = c * (stark_nm * 1e-9 * ne / 1e23) / lam ** 2   # Hz
        gamma = A + 2 * math.pi * fwhm_stark                         # angular damping (s^-1)
        a = gamma / (4 * math.pi * dnuD)
        from scipy.special import wofz
        H0 = float(wofz(1j * a).real)
        phi0 = H0 / (math.sqrt(math.pi) * dnuD)
        k0 = lam ** 2 / (8 * math.pi) * (gu / gl) * A * nl_ * phi0 * (1 - math.exp(-h * nu0 / kT))
        out.append((j, k0, a))
    return out


_BETA = None


def voigt_escape(tau0, a):
    """Mean escape probability for a Voigt line of centre optical depth tau0 and damping a
    (per-frequency escape (1-e^-tau)/tau, profile-weighted). Tabulated, vectorised."""
    global _BETA
    if _BETA is None:
        from scipy.special import wofz
        lt = np.linspace(-3, 12, 121)
        la = np.linspace(-5, 1, 61)
        x = np.concatenate([-np.logspace(4, -3, 400), np.logspace(-3, 4, 400)])
        B = np.zeros((len(lt), len(la)))
        for j, lav in enumerate(la):
            av = 10 ** lav
            H = wofz(x + 1j * av).real
            w = H / H.max()
            dx = np.gradient(x)
            for i, ltv in enumerate(lt):
                t = 10 ** ltv * w
                pe = np.where(t > 1e-8, -np.expm1(-t) / np.maximum(t, 1e-300), 1.0)
                B[i, j] = float((H * pe * dx).sum() / (H * dx).sum())
        _BETA = (lt, la, np.log(B))
    lt, la, LB = _BETA
    x = np.clip(np.log10(np.maximum(tau0, 1e-3)), lt[0], lt[-1])
    y = np.clip(np.log10(np.maximum(a, 1e-5)), la[0], la[-1])
    i = np.clip(((x - lt[0]) / (lt[1] - lt[0])).astype(int), 0, len(lt) - 2)
    j = np.clip(((y - la[0]) / (la[1] - la[0])).astype(int), 0, len(la) - 2)
    u = (x - lt[i]) / (lt[1] - lt[0])
    v = (y - la[j]) / (la[1] - la[0])
    r = (1 - u) * ((1 - v) * LB[i, j] + v * LB[i, j + 1]) + u * ((1 - v) * LB[i + 1, j] + v * LB[i + 1, j + 1])
    return np.exp(r)


def band_integrals(jlam, kappa, V, S):
    out = {}
    dlam = np.gradient(LAM)
    for b, (l0, l1) in BANDS.items():
        m = (LAM >= l0) & (LAM < l1)
        out[b] = float(np.sum(jlam[m] * dlam[m]))
    out["lm"] = float(683.0 * np.sum(jlam * V * dlam))
    out["act"] = float(np.sum(jlam * S * dlam))
    ph = jlam * LAM / (h * c) * dlam
    out["ph_o2"] = float(np.sum(ph[(LAM >= 130e-9) & (LAM < 200e-9)]))
    out["ph_ion"] = float(np.sum(ph[LAM < 102e-9]))
    out["kappa"] = np.interp(PROBES, LAM, kappa)
    return out


def build_table():
    import cantera as ct
    from eos import load
    eos = load()
    gas = ct.Solution("airNASA9.yaml")
    gas.X = {"N2": X_N2, "O2": X_O2}
    V, S = _V(), _S()
    Ts, rhos = eos.Ts, eos.rhos
    keys = list(BANDS) + ["lm", "act", "ph_o2", "ph_ion"]
    tab = {k: np.zeros((len(rhos), len(Ts))) for k in keys}
    kap = np.zeros((len(rhos), len(Ts), len(PROBES)))
    nl = len(VUV_LINES)
    vj = np.zeros((len(rhos), len(Ts), nl))
    vk = np.zeros_like(vj)
    va = np.full_like(vj, 1e-3)
    for i, rho in enumerate(rhos):
        for j, T in enumerate(Ts):
            if T < 1500:
                continue
            ne, comp = composition(T, rho, gas)
            jl, k = spectrum(T, ne, comp)
            b = band_integrals(jl, k, V, S)
            for kk in keys:
                tab[kk][i, j] = b[kk]
            kap[i, j] = b["kappa"]
            for q, (jj, kk, aa) in enumerate(vuv_line_data(T, ne, comp)):
                vj[i, j, q], vk[i, j, q], va[i, j, q] = jj, kk, aa
    np.savez(CACHE, Ts=Ts, rhos=rhos, kap=kap, vj=vj, vk=vk, va=va, **tab)
    return RadTable(np.load(CACHE))


class RadTable:
    KEYS = list(BANDS) + ["lm", "act", "ph_o2", "ph_ion"]

    def __init__(self, d):
        self.d = {k: d[k] for k in self.KEYS}
        self.kap = d["kap"]
        self.vj, self.vk, self.va = d["vj"], d["vk"], d["va"]
        self.vlam = np.array([l[2] for l in VUV_LINES])
        self.lT, self.lr = np.log(d["Ts"]), np.log(d["rhos"])

    def _idx(self, rho, T):
        x = np.clip(np.log(rho), self.lr[0], self.lr[-1])
        i = np.clip(np.searchsorted(self.lr, x) - 1, 0, len(self.lr) - 2)
        w = (x - self.lr[i]) / (self.lr[i + 1] - self.lr[i])
        y = np.clip(np.log(T), self.lT[0], self.lT[-1])
        j = np.clip(np.searchsorted(self.lT, y) - 1, 0, len(self.lT) - 2)
        v = (y - self.lT[j]) / (self.lT[j + 1] - self.lT[j])
        return i, w, j, v

    def get(self, rho, T):
        i, w, j, v = self._idx(np.atleast_1d(rho), np.atleast_1d(T))
        out = {}
        for k in self.KEYS:
            A = np.log(np.maximum(self.d[k], 1e-300))
            r = (1 - w) * ((1 - v) * A[i, j] + v * A[i, j + 1]) + w * ((1 - v) * A[i + 1, j] + v * A[i + 1, j + 1])
            out[k] = np.where(r < -600, 0.0, np.exp(r))
        A = np.log(np.maximum(self.kap, 1e-300))
        r = ((1 - w)[:, None] * ((1 - v)[:, None] * A[i, j] + v[:, None] * A[i, j + 1])
             + w[:, None] * ((1 - v)[:, None] * A[i + 1, j] + v[:, None] * A[i + 1, j + 1]))
        out["kappa"] = np.where(r < -600, 0.0, np.exp(r))
        for key, tab in (("vj", self.vj), ("vk", self.vk), ("va", self.va)):
            A = np.log(np.maximum(tab, 1e-300))
            r = ((1 - w)[:, None] * ((1 - v)[:, None] * A[i, j] + v[:, None] * A[i, j + 1])
                 + w[:, None] * ((1 - v)[:, None] * A[i + 1, j] + v[:, None] * A[i + 1, j + 1]))
            out[key] = np.where(r < -600, 0.0, np.exp(r))
        return out


def load():
    if not os.path.exists(CACHE):
        return build_table()
    return RadTable(np.load(CACHE))


# thermal conductivity of equilibrium air at 1 atm (W/m/K); D'Angola/Capitelli-type curve, rounded
# [MEMORY, to be checked against VALIDATION_DATA]; above 30 kK electron (Spitzer-like) T^2.5 growth.
K_T = np.array([300, 1000, 2000, 3000, 3800, 5000, 6000, 7000, 8000, 10000, 12000, 15000, 20000, 30000])
K_V = np.array([0.026, 0.066, 0.12, 0.30, 0.65, 0.40, 0.9, 2.3, 1.4, 1.0, 1.6, 3.2, 2.4, 3.5])


def conductivity(T, mult=1.0):
    T = np.asarray(T, float)
    k = np.exp(np.interp(np.log(T), np.log(K_T), np.log(K_V)))
    hot = T > 30000
    k = np.where(hot, 3.5 * (T / 30000.0) ** 2.5, k)
    return mult * np.minimum(k, 200.0)


if __name__ == "__main__":
    import time
    t = time.time()
    r = build_table()
    print(f"radiation table built in {time.time()-t:.0f}s")

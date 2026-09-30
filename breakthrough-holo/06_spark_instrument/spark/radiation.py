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

from eos import (ION, LEVELS, NA, P0, X_N2, X_O2, cantera_state, kB, h, eV, saha_state, M_N, M_O)

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
CHI_G = {1: 4.0, 2: 11.0, 3: 20.0}       # eV, lowest merged level of the recombined species, by ion charge


def _V():
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "..", "03_simulations"))
    from holo_common import V_photopic
    return V_photopic(LAM * 1e9)


def _S():
    tab = {200: 0.03, 210: 0.075, 220: 0.12, 230: 0.19, 240: 0.30, 250: 0.43, 254: 0.5, 260: 0.65, 270: 1.0,
           280: 0.88, 290: 0.64, 297: 0.46, 300: 0.30, 305: 0.06, 310: 0.015, 315: 0.003, 320: 0.001,
           330: 0.00041, 340: 0.00028, 350: 0.0002, 360: 0.00013, 370: 0.000093, 380: 0.000064,
           390: 0.000045, 400: 0.00003}
    l = LAM * 1e9
    s = np.exp(np.interp(l, list(tab), np.log(list(tab.values()))))
    s[(l < 200) | (l > 400)] = 0.0
    return s


def composition(T, rho, gas):
    """Number densities: ne, and dict (el, z) -> n for atoms/atomic ions (+ molecular ions as z=1)."""
    if T <= 16000.0:
        st = cantera_state(gas, T, rho)
        n = st["X"] * st["P"] / (kB * T)
        idx = {s: gas.species_index(s) for s in gas.species_names}
        comp = {("N", 0): n[idx["N"]], ("O", 0): n[idx["O"]], ("N", 1): n[idx["N+"]], ("O", 1): n[idx["O+"]],
                ("N", 2): 0.0, ("O", 2): 0.0, ("N", 3): 0.0, ("O", 3): 0.0,
                ("mol", 1): n[idx["NO+"]] + n[idx["N2+"]] + n[idx["O2+"]]}
        return st["ne"], comp
    s = saha_state(T, rho)
    n_mol = rho / (X_N2 * 2 * M_N + X_O2 * 2 * M_O)
    nuc = {"N": 2 * X_N2 * n_mol, "O": 2 * X_O2 * n_mol}
    comp = {(el, z): nuc[el] * s["f" + el][z] for el in ("N", "O") for z in range(4)}
    comp[("mol", 1)] = 0.0
    return s["ne"], comp


def spectrum(T, ne, comp):
    """Emission j_lambda (W m^-3 m^-1, 4 pi) and absorption coefficient kappa(lambda) (m^-1)."""
    kT = kB * T
    hnu = h * NU
    jnu = np.zeros_like(NU)
    for z in (1, 2, 3):
        nz = sum(comp.get((el, z), 0.0) for el in ("N", "O")) + (comp[("mol", 1)] if z == 1 else 0.0)
        if nz <= 0:
            continue
        base = C_KR * z * z * ne * nz / math.sqrt(T) * np.exp(-hnu / kT)
        chig = CHI_G[z] * eV
        term = 1.0 + XI * (np.exp(np.minimum(hnu, chig) / kT) - 1.0)
        # explicit ground-state edges of the recombined species (charge z-1), weight by element share
        for el in ("N", "O"):
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
    # Kirchhoff absorption of the continuum: kappa_nu = j_nu / (4 pi B_nu) (j_nu is 4pi-integrated)
    Bnu = 2 * h * NU ** 3 / c ** 2 / np.expm1(np.minimum(hnu / kT, 700.0))
    kappa = jnu / (4 * math.pi * np.maximum(Bnu, 1e-300)) * (1 - np.exp(-np.minimum(hnu / kT, 700.0))) ** -1
    return jlam, kappa


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
    np.savez(CACHE, Ts=Ts, rhos=rhos, kap=kap, **tab)
    return RadTable(np.load(CACHE))


class RadTable:
    KEYS = list(BANDS) + ["lm", "act", "ph_o2", "ph_ion"]

    def __init__(self, d):
        self.d = {k: d[k] for k in self.KEYS}
        self.kap = d["kap"]
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

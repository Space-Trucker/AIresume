"""SPARK equation of state: equilibrium air plasma, 300 K to 300 kK.

* T <= 18 kK: Cantera `airNASA9.yaml` (NASA Glenn 9-coefficient thermo, 11 species: N2 O2 NO N O
  N2+ O2+ NO+ N+ O+ e-), chemical equilibrium at fixed (T, rho).
* T >= 14 kK: own Saha solver for atoms and ions up to charge 3+ (N, O), with low-lying-level partition
  functions. Its internal energy is shifted per density to match Cantera at 16 kK; the branches are
  blended linearly over 14-18 kK. Molecules are negligible there (checked in validation V3).
Tables are cached in eos_table.npz. Energies are per kg, relative to ambient air (300 K, 1 atm).
"""
from __future__ import annotations

import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "eos_table.npz")

kB = 1.380649e-23
h = 6.62607015e-34
me = 9.1093837e-31
eV = 1.602176634e-19
NA = 6.02214076e23
AMU = 1.66053907e-27
M_N, M_O = 14.0067 * AMU, 15.999 * AMU
X_N2, X_O2 = 0.79, 0.21                      # same mixture as Cantera composition below
P0, T0 = 101325.0, 300.0

# ionisation energies (eV) and low-lying levels (g, E eV) per charge state (NIST ASD, rounded)
ION = {"N": [14.534, 29.601, 47.445, 77.474, 97.890, 552.07], "O": [13.618, 35.121, 54.936, 77.414, 113.90, 138.12, 739.29]}
LEVELS = {
    ("N", 0): [(4, 0.0), (10, 2.384), (6, 3.576)],
    ("N", 1): [(1, 0.0), (3, 0.006), (5, 0.016), (5, 1.899), (1, 4.053), (5, 5.85)],
    ("N", 2): [(2, 0.0), (4, 0.022), (12, 7.09)],
    ("N", 3): [(1, 0.0), (9, 8.33)],
    ("O", 0): [(5, 0.0), (3, 0.020), (1, 0.028), (5, 1.967), (1, 4.19)],
    ("O", 1): [(4, 0.0), (10, 3.325), (6, 5.017)],
    ("O", 2): [(1, 0.0), (3, 0.014), (5, 0.038), (5, 2.51), (1, 5.35)],
    ("O", 3): [(2, 0.0), (4, 0.048), (12, 8.86)],
    ("N", 4): [(2, 0.0), (6, 10.0)], ("N", 5): [(1, 0.0)], ("N", 6): [(2, 0.0)],
    ("O", 4): [(1, 0.0), (9, 10.2)], ("O", 5): [(2, 0.0), (6, 12.0)], ("O", 6): [(1, 0.0)], ("O", 7): [(2, 0.0)],
}
NZ = {el: len(ION[el]) + 1 for el in ION}      # number of charge states tracked per element
H0_ATOM = {"N": 466.48e3 / NA, "O": 242.46e3 / NA}   # J per atom at 0 K relative to N2/O2 at 298 K


def part_fn(el, z, T):
    """Partition function and mean excitation energy (J) of element el, charge z."""
    kT = kB * T
    g = np.array([l[0] for l in LEVELS[(el, z)]], float)
    E = np.array([l[1] for l in LEVELS[(el, z)]]) * eV
    w = g * np.exp(-E / kT)
    Z = w.sum()
    return Z, float((w * E).sum() / Z)


def saha_state(T, rho):
    """Atomic/ionic equilibrium at (T, rho). Returns dict with P, u (J/kg, abs. ref), ne, fractions."""
    n_heavy_mol = rho / (X_N2 * 2 * M_N + X_O2 * 2 * M_O)       # molecules per m^3 (if undissociated)
    nuc = {"N": 2 * X_N2 * n_heavy_mol, "O": 2 * X_O2 * n_heavy_mol}
    lam3 = (h * h / (2 * math.pi * me * kB * T)) ** 1.5

    def fractions(ne):
        out = {}
        for el in ("N", "O"):
            nz = NZ[el]
            Zs, Es = zip(*[part_fn(el, z, T) for z in range(nz)])
            lr = [0.0]
            for z in range(nz - 1):
                lS = (math.log(2 * Zs[z + 1] / Zs[z] / lam3 / ne) - ION[el][z] * eV / (kB * T))
                lr.append(lr[-1] + lS)
            lr = np.array(lr)
            r = np.exp(lr - lr.max())
            out[el] = (r / r.sum(), np.array(Es))
        return out

    # charge neutrality: solve ne = sum_z z n_z by bisection in log space
    lo, hi = 1e10, 8 * (nuc["N"] + nuc["O"])
    for _ in range(200):
        ne = math.sqrt(lo * hi)
        f = fractions(ne)
        charge = sum(nuc[el] * float((f[el][0] * np.arange(NZ[el])).sum()) for el in ("N", "O"))
        if charge > ne:
            lo = ne
        else:
            hi = ne
    ne = math.sqrt(lo * hi)
    f = fractions(ne)
    n_tot = ne + nuc["N"] + nuc["O"]
    P = n_tot * kB * T
    U = 1.5 * kB * T * n_tot                                          # J/m^3 translational
    for el in ("N", "O"):
        fr, Es = f[el]
        cum_ion = np.concatenate([[0.0], np.cumsum(ION[el])]) * eV
        U += nuc[el] * float((fr * (Es + cum_ion[:NZ[el]] + H0_ATOM[el])).sum())
    return dict(P=P, u=U / rho, ne=ne, fN=f["N"][0], fO=f["O"][0])


def cantera_state(gas, T, rho):
    gas.TD = T, rho
    gas.equilibrate("TV")
    ne = gas.concentrations[gas.species_index("e-")] * 1000 * NA
    return dict(P=gas.P, u=gas.int_energy_mass, ne=ne, X=gas.X.copy())


def build_table(nT=170, nrho=70):
    import cantera as ct
    gas = ct.Solution("airNASA9.yaml")
    gas.X = {"N2": X_N2, "O2": X_O2}
    Ts = np.unique(np.concatenate([np.geomspace(250.0, 18000.0, 110), np.geomspace(14000.0, 1.0e6, 90)]))
    rhos = np.geomspace(1e-5, 30.0, nrho)
    P = np.zeros((len(rhos), len(Ts)))
    U = np.zeros_like(P)
    NE = np.zeros_like(P)
    gas.TP = T0, P0
    gas.equilibrate("TP")
    u_ref = gas.int_energy_mass
    rho0 = gas.density
    for i, rho in enumerate(rhos):
        c16 = cantera_state(gas, 16000.0, rho)
        s16 = saha_state(16000.0, rho)
        du = c16["u"] - s16["u"]
        for j, T in enumerate(Ts):
            if T <= 14000.0:
                c = cantera_state(gas, T, rho)
                P[i, j], U[i, j], NE[i, j] = c["P"], c["u"], c["ne"]
            elif T >= 18000.0:
                s = saha_state(T, rho)
                P[i, j], U[i, j], NE[i, j] = s["P"], s["u"] + du, s["ne"]
            else:
                w = (T - 14000.0) / 4000.0
                c = cantera_state(gas, T, rho)
                s = saha_state(T, rho)
                P[i, j] = (1 - w) * c["P"] + w * s["P"]
                U[i, j] = (1 - w) * c["u"] + w * (s["u"] + du)
                NE[i, j] = (1 - w) * c["ne"] + w * s["ne"]
    U -= u_ref
    np.savez(CACHE, Ts=Ts, rhos=rhos, P=P, U=U, NE=NE, rho0=rho0, u_ref=u_ref)
    return load()


class EOS:
    """Fast (rho, e) -> (T, P, c_s, n_e) lookups by bilinear interpolation in (log rho, e/log T)."""

    def __init__(self, d):
        self.Ts, self.rhos = d["Ts"], d["rhos"]
        self.lT, self.lr = np.log(self.Ts), np.log(self.rhos)
        self.P, self.U, self.NE = d["P"], d["U"], d["NE"]
        self.rho0 = float(d["rho0"])
        # enforce monotone U in T for inversion
        self.Um = np.maximum.accumulate(self.U + 1e-9 * np.arange(len(self.Ts))[None, :], axis=1)

    def _rho_idx(self, rho):
        x = np.clip(np.log(rho), self.lr[0], self.lr[-1])
        i = np.clip(np.searchsorted(self.lr, x) - 1, 0, len(self.lr) - 2)
        w = (x - self.lr[i]) / (self.lr[i + 1] - self.lr[i])
        return i, w

    def T_of(self, rho, e):
        rho = np.atleast_1d(rho).astype(float)
        e = np.atleast_1d(e).astype(float)
        i, w = self._rho_idx(rho)
        out = np.empty_like(e)
        for k in range(len(e)):
            lt0 = np.interp(e[k], self.Um[i[k]], self.lT)
            lt1 = np.interp(e[k], self.Um[i[k] + 1], self.lT)
            out[k] = math.exp((1 - w[k]) * lt0 + w[k] * lt1)
        return out

    def _interp_T(self, tab, rho, T, log=False):
        rho = np.atleast_1d(rho).astype(float)
        T = np.atleast_1d(T).astype(float)
        i, w = self._rho_idx(rho)
        x = np.clip(np.log(T), self.lT[0], self.lT[-1])
        j = np.clip(np.searchsorted(self.lT, x) - 1, 0, len(self.lT) - 2)
        v = (x - self.lT[j]) / (self.lT[j + 1] - self.lT[j])
        A = np.log(np.maximum(tab, 1e-300)) if log else tab
        r = ((1 - w) * ((1 - v) * A[i, j] + v * A[i, j + 1]) + w * ((1 - v) * A[i + 1, j] + v * A[i + 1, j + 1]))
        return np.exp(r) if log else r

    def P_of_T(self, rho, T):
        return self._interp_T(self.P, rho, T, log=True)

    def e_of_T(self, rho, T):
        return self._interp_T(self.U, rho, T)

    def ne_of_T(self, rho, T):
        return self._interp_T(self.NE, rho, T, log=True)

    def state(self, rho, e):
        T = self.T_of(rho, e)
        P = self.P_of_T(rho, T)
        # sound speed from finite differences of P(rho, s): use c^2 = dP/drho|_e + P/rho^2 dP/de|_rho
        dr = 1e-3
        de = np.maximum(1e-3 * np.abs(e), 50.0)
        Pr = self.P_of_T(rho * (1 + dr), self.T_of(rho * (1 + dr), e))
        Pe = self.P_of_T(rho, self.T_of(rho, e + de))
        c2 = (Pr - P) / (rho * dr) + P / rho ** 2 * (Pe - P) / de
        return T, P, np.sqrt(np.maximum(c2, 1.0))


def load():
    if not os.path.exists(CACHE):
        return build_table()
    return EOS(np.load(CACHE))


if __name__ == "__main__":
    import time
    t = time.time()
    eos = build_table()
    print(f"table built in {time.time()-t:.0f}s: {eos.P.shape}")


class FastEOS:
    """Vectorised (rho, e) -> T, P lookups on a regular (log rho, asinh(e/E_S)) grid, built from EOS.
    Also provides isobaric (P0) tables rho(T), h(T) for the late, low-Mach phase."""
    E_S = 1.0e4

    def __init__(self, eos: EOS, ns=900):
        self.base = eos
        self.lr = eos.lr
        self.e_max = float(eos.U[:, -1].min())          # largest e covered at every density
        self.s = np.linspace(math.asinh(-2e5 / self.E_S), math.asinh(self.e_max / self.E_S), ns)
        es = self.E_S * np.sinh(self.s)
        self.lTt = np.zeros((len(self.lr), ns))
        self.lPt = np.zeros_like(self.lTt)
        for i in range(len(self.lr)):
            lt = np.interp(es, eos.Um[i], eos.lT)
            self.lTt[i] = lt
            self.lPt[i] = np.interp(lt, eos.lT, np.log(eos.P[i]))
        self.rho0 = eos.rho0
        # isobaric tables at P0
        lP0 = math.log(P0)
        self.iso_lT = eos.lT
        lrho = np.empty(len(eos.lT))
        for j in range(len(eos.lT)):
            col = np.log(eos.P[:, j])
            lrho[j] = np.interp(lP0, col, eos.lr)
        self.iso_lrho = lrho
        rho_iso = np.exp(lrho)
        u_iso = np.array([np.interp(lrho[j], eos.lr, eos.U[:, j]) for j in range(len(eos.lT))])
        self.iso_h = u_iso + P0 / rho_iso

    def _bil(self, tab, rho, e):
        x = np.clip(np.log(rho), self.lr[0], self.lr[-1])
        i = np.clip(np.searchsorted(self.lr, x) - 1, 0, len(self.lr) - 2)
        w = (x - self.lr[i]) / (self.lr[i + 1] - self.lr[i])
        y = np.clip(np.arcsinh(e / self.E_S), self.s[0], self.s[-1])
        ds = self.s[1] - self.s[0]
        k = np.clip(((y - self.s[0]) / ds).astype(int), 0, len(self.s) - 2)
        v = (y - self.s[k]) / ds
        return (1 - w) * ((1 - v) * tab[i, k] + v * tab[i, k + 1]) + w * ((1 - v) * tab[i + 1, k] + v * tab[i + 1, k + 1])

    def T(self, rho, e):
        return np.exp(self._bil(self.lTt, rho, e))

    def P(self, rho, e):
        return np.exp(self._bil(self.lPt, rho, e))

    def state(self, rho, e):
        P = self.P(rho, e)
        de = np.maximum(1e-3 * np.abs(e), 200.0)
        Pr = self.P(rho * 1.001, e)
        Pe = self.P(rho, e + de)
        c2 = (Pr - P) / (rho * 0.001) + P / rho ** 2 * (Pe - P) / de
        return self.T(rho, e), P, np.sqrt(np.maximum(c2, 100.0))

    def e_of(self, rho, T):
        return self.base.e_of_T(rho, T)

    def iso_rho(self, T):
        return np.exp(np.interp(np.log(T), self.iso_lT, self.iso_lrho))

    def iso_hT(self, T):
        return np.interp(np.log(T), self.iso_lT, self.iso_h)

    def iso_T_of_h(self, hh):
        hm = np.maximum.accumulate(self.iso_h)
        return np.exp(np.interp(hh, hm, self.iso_lT))


class IdealEOS:
    """Ideal gas (gamma) with the same interface, for analytic validation tests."""

    def __init__(self, gamma=1.4, R=287.0, rho0=1.2):
        self.g, self.R, self.rho0 = gamma, R, rho0
        self.cv = R / (gamma - 1)

    def T(self, rho, e):
        return np.maximum(e, 1e-12) / self.cv

    def P(self, rho, e):
        return (self.g - 1) * rho * np.maximum(e, 0.0)

    def state(self, rho, e):
        P = self.P(rho, e)
        return self.T(rho, e), P, np.sqrt(np.maximum(self.g * P / rho, 1e-6))

    def e_of(self, rho, T):
        return self.cv * np.asarray(T, float)


def fast():
    return FastEOS(load())

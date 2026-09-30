"""SPARK chemistry: NO / NO2 / O3 along Lagrangian temperature histories, plus photochemistry.

Species: N2 O2 N O NO NO2 O3. Thermo (for equilibrium constants of reverse reactions): NASA
polynomials from Cantera `nasa_gas.yaml`. Forward rate constants (molecule, cm, s units), standard
evaluations (Baulch 1994/2005; JPL 19-5; Kossyi 1992) as noted; every reaction is reversible through
detailed balance.
  R1 N2 + O  = NO + N      3.0e-10 exp(-38370/T)                  (Zeldovich, Baulch)
  R2 N + O2  = NO + O      1.06e-14 T exp(-3160/T)                (Hanson & Salimian)
  R3 O + O + M = O2 + M    3.31e-31 T^-1  (x2.5 unless T<1000)    (GRI-3.0 recombination)
  R4 N + N + M = N2 + M    8.3e-34 exp(500/T)                     (Kossyi)
  R5 N + O + M = NO + M    1.76e-31 T^-0.5                        (Kossyi)
  R6 O + O2 + M = O3 + M   6.0e-34 (T/300)^-2.4                   (JPL)
  R7 O + O3  = O2 + O2     8.0e-12 exp(-2060/T)                   (JPL)
  R8 NO + O3 = NO2 + O2    3.0e-12 exp(-1500/T)                   (JPL)
  R9 O + NO + M = NO2 + M  9.0e-32 (T/300)^-1.5                   (JPL, low-pressure limit)
  R10 NO2 + O = NO + O2    5.1e-12 exp(210/T)                     (JPL)
Photochemistry from escaped VUV/EUV (model ledger, +-2x): each 130-200 nm photon dissociates O2 -> 2 O3;
each <102 nm photon -> 1 NO + 1.5 O3.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.integrate import solve_ivp

SP = ["N2", "O2", "N", "O", "NO", "NO2", "O3"]
IDX = {s: i for i, s in enumerate(SP)}
kB_cgs = 1.380649e-16
R_ = 8.314462618

_THERMO = None


def _thermo():
    global _THERMO
    if _THERMO is None:
        import cantera as ct
        allsp = {s.name: s for s in ct.Species.list_from_file("nasa_gas.yaml")}
        _THERMO = [allsp[n].thermo for n in SP]
    return _THERMO


_GT = None


def _g_table():
    global _GT
    if _GT is None:
        th = _thermo()
        Tg = np.linspace(250.0, 8000.0, 3101)
        G = np.empty((len(Tg), len(SP)))
        for j, T in enumerate(Tg):
            for i, t in enumerate(th):
                G[j, i] = (t.h(T) - T * t.s(T)) / (R_ * 1000 * T)
        _GT = (Tg, G)
    return _GT


def g0_RT(T):
    """Standard-state Gibbs energy / RT for each species at T (1 bar), tabulated every 2.5 K."""
    Tg, G = _g_table()
    j = min(max(int((T - Tg[0]) / (Tg[1] - Tg[0])), 0), len(Tg) - 2)
    w = (T - Tg[j]) / (Tg[1] - Tg[0])
    return (1 - w) * G[j] + w * G[j + 1]


# reactions: (reactants dict, products dict, third_body, k(T) forward in molecule-cm-s units)
def _rxns():
    return [
        ({"N2": 1, "O": 1}, {"NO": 1, "N": 1}, False, lambda T: 3.0e-10 * math.exp(-38370 / T)),
        ({"N": 1, "O2": 1}, {"NO": 1, "O": 1}, False, lambda T: 1.06e-14 * T * math.exp(-3160 / T)),
        ({"O": 2}, {"O2": 1}, True, lambda T: 3.31e-31 / T * (2.5 if T >= 1000 else 1.0)),
        ({"N": 2}, {"N2": 1}, True, lambda T: 8.3e-34 * math.exp(500 / T)),
        ({"N": 1, "O": 1}, {"NO": 1}, True, lambda T: 1.76e-31 * T ** -0.5),
        ({"O": 1, "O2": 1}, {"O3": 1}, True, lambda T: 6.0e-34 * (T / 300) ** -2.4),
        ({"O": 1, "O3": 1}, {"O2": 2}, False, lambda T: 8.0e-12 * math.exp(-2060 / T)),
        ({"NO": 1, "O3": 1}, {"NO2": 1, "O2": 1}, False, lambda T: 3.0e-12 * math.exp(-1500 / T)),
        ({"O": 1, "NO": 1}, {"NO2": 1}, True, lambda T: 9.0e-32 * (T / 300) ** -1.5),
        ({"NO2": 1, "O": 1}, {"NO": 1, "O2": 1}, False, lambda T: 5.1e-12 * math.exp(210 / T)),
    ]


RX = _rxns()
NU = np.zeros((len(RX), len(SP)))
for k, (re, pr, _, _) in enumerate(RX):
    for s, v in re.items():
        NU[k, IDX[s]] -= v
    for s, v in pr.items():
        NU[k, IDX[s]] += v


def rates(T, n):
    """Net production rates dn/dt (cm^-3 s^-1) for number densities n (cm^-3)."""
    T = float(min(max(T, 250.0), 8000.0))
    M = n.sum()
    g = g0_RT(T)
    c0 = 1e5 / (kB_cgs * 1e-7 * T) * 1e-6       # standard concentration (1 bar) in cm^-3
    w = np.zeros(len(SP))
    for k, (re, pr, tb, kf) in enumerate(RX):
        kfor = kf(T) * (M if tb else 1.0)
        dG = float(NU[k] @ g)
        dn = int(NU[k].sum())
        Kc = math.exp(-dG) * c0 ** dn             # concentration-based equilibrium constant
        krev = kfor / max(Kc, 1e-300)
        fw = kfor * np.prod([n[IDX[s]] ** v for s, v in re.items()])
        bw = krev * np.prod([n[IDX[s]] ** v for s, v in pr.items()])
        w += NU[k] * (fw - bw)
    return w


def integrate_history(t, T, P, n_init=None, t_mix=1e-3):
    """Integrate species number fractions along T(t), P(t) (SI), then a mixing quench to 300 K."""
    t = np.asarray(t, float)
    T = np.asarray(T, float)
    P = np.asarray(P, float)
    if n_init is None:
        x = np.zeros(len(SP))
        x[IDX["N2"]], x[IDX["O2"]] = 0.79, 0.21
    else:
        x = np.asarray(n_init, float)

    def Tfun(tt):
        if tt <= t[-1]:
            return float(np.interp(tt, t, T)), float(np.interp(tt, t, P))
        f = min(1.0, (tt - t[-1]) / t_mix)
        return T[-1] + (300.0 - T[-1]) * f, 101325.0

    def rhs(tt, y):
        # y_i = molecules of species i per parent air molecule (conserved-mass basis). The actual
        # number density follows from P = n_tot k T with n_tot = n_parent * sum(y).
        Tt, Pt = Tfun(tt)
        ntot = Pt / (1.380649e-23 * Tt) * 1e-6
        y = np.maximum(y, 0.0)
        sy = y.sum()
        n = y / sy * ntot
        return rates(Tt, n) * sy / ntot

    sol = solve_ivp(rhs, (t[0], t[-1] + 1.5 * t_mix), x, method="LSODA", rtol=1e-6, atol=1e-16)
    return np.maximum(sol.y[:, -1], 0.0)


def equilibrium_fractions(T, P):
    """Equilibrium mole fractions of the 7 species (for the kinetics consistency test)."""
    import cantera as ct
    allsp = {s.name: s for s in ct.Species.list_from_file("nasa_gas.yaml")}
    gas = ct.Solution(thermo="ideal-gas", species=[allsp[n] for n in SP])
    gas.TPX = T, P, {"N2": 0.79, "O2": 0.21}
    gas.equilibrate("TP")
    return gas.X


def spark_products(spark, T_start=1800.0, max_cells=160):
    """Molecules of NO, NO2, O3 produced by a SPARK run (thermal kernel chemistry + photochemistry)."""
    ht = np.array(spark.hist_t)
    HT = np.array(spark.hist_T)
    HP = np.array(spark.hist_P)
    Tmax = HT.max(0)
    hot = np.where(Tmax > T_start)[0]
    if len(hot) > max_cells:
        hot = hot[np.linspace(0, len(hot) - 1, max_cells).astype(int)]
        weight = (Tmax > T_start).sum() / len(hot)
    else:
        weight = 1.0
    AMU = 1.66053907e-27
    m_mol = 0.79 * 28.014 * AMU + 0.21 * 31.998 * AMU
    tot = {"NO": 0.0, "NO2": 0.0, "O3": 0.0, "N": 0.0, "O": 0.0}
    for i in hot:
        # clamp: above 6000 K treat as 6000 K (equilibrium is fast there; avoids ionised regime)
        Ti = np.minimum(HT[:, i], 6000.0)
        x = integrate_history(ht, Ti, np.maximum(HP[:, i], 1e3))
        n_molec = spark.m[i] / m_mol          # parent air molecules in this Lagrangian cell (~conserved)
        for s in tot:
            tot[s] += weight * x[IDX[s]] * n_molec
    photo_O3 = 2.0 * spark.ph_o2 + 1.5 * spark.ph_ion
    photo_NO = 1.0 * spark.ph_ion
    return dict(thermal=tot, photo_O3=photo_O3, photo_NO=photo_NO,
                NO_total=tot["NO"] + photo_NO, NO2_total=tot["NO2"], O3_total=tot["O3"] + photo_O3,
                NOx_plus_O3=tot["NO"] + tot["NO2"] + photo_NO + tot["O3"] + photo_O3)

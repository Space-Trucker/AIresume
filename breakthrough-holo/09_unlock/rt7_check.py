"""Red team 7: independent checks of T7 (Gaussian static voxels, forward-scatter illumination, B9, hologram-rate
pinning, I9). One file, one section per claim. Results go to results/rt7_<section>.json; console output is teed to
results/rt7_run.log by the caller.

Independence rules (owner rule: double-validate):
- Air properties, drag, photophoretic force (re-derived from thermal creep), slip, heat balance, Mie (own BHMIE and an
  anomalous-diffraction cross-check), LP allocation (hull-equation method, checked against scipy linprog), the
  turbulence model (3D isotropic von Karman-Pao, longitudinal and transverse spectra, mean wind), the PID tuner and the
  loop simulator are all written here.
- physics.py, rt6_check.py, m17_exposure_field.py, m18*.py are imported ONLY in clearly marked cross-check lines.

Run: python3 rt7_check.py <section> [<section> ...]   sections: phys mie vis modes b9 loop loopx i9 table all
"""
import json
import math
import os
import sys
import time
import zlib

import numpy as np
from scipy import optimize, signal, special, stats
from scipy.linalg import expm
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))


def dump(name, obj):
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, f"rt7_{name}.json"), "w") as fh:
        json.dump(obj, fh, indent=1, default=float)


# ======================================================================================================================
# Air (independent forms: Sutherland viscosity, US-Standard-Atmosphere conductivity, Kim et al. 2005 slip correction)
# ======================================================================================================================
P_ATM, R_GAS, T_AMB = 101325.0, 287.05, 293.15


def mu(T):
    return 1.458e-6 * T ** 1.5 / (T + 110.4)


def kg(T):
    return 2.64638e-3 * T ** 1.5 / (T + 245.4 * 10 ** (-12.0 / T))


def rho(T):
    return P_ATM / (R_GAS * T)


def mfp(T):
    return mu(T) / P_ATM * math.sqrt(math.pi * R_GAS * T / 2)


def cc(a, T=T_AMB):
    kn = mfp(T) / a
    return 1 + kn * (1.142 + 0.558 * math.exp(-0.999 / kn))


def kint(T, T0=T_AMB, n=200):
    t = np.linspace(T0, T, n)
    return float(np.trapezoid(kg(t), t))


# ======================================================================================================================
# Section phys: B2 / I_unit, slip, heat, absorber plausibility (A and J1/A), FOM ceiling
# ======================================================================================================================
C_M, C_T = 1.14, 2.18          # velocity-slip and temperature-jump coefficients (Talbot 1980) [memory]


def creep_force(a, q1, kp, Ts, K=0.956, slip=True):
    """Photophoretic force (N) from thermal creep, derived here: a sphere whose gas-side surface temperature has a
    dipole dT1 cos(theta) creeps gas towards the hot pole at v_s = K (mu/(rho T)) grad_s T; holding such a 'squirmer'
    (B1 = K mu dT1/(rho T a)) needs F = 4 pi mu a B1 = 4 pi K mu^2 dT1/(rho T). The surface flux dipole q1 (W/m^2)
    gives dT1 = q1 a / (k_p (1 + 2 C_t Kn) + 2 k_g) (temperature jump), and velocity slip divides by (1 + 3 C_m Kn).
    K = 0.75 (Maxwell) ... 1.17 (kinetic theory); 0.956 reproduces the project's C_ph = 0.85 (C_ph = K / (9/8))."""
    Tf = 0.5 * (Ts + T_AMB)
    kn = mfp(Tf) / a if slip else 0.0
    dT1 = q1 * a / (kp * (1 + 2 * C_T * kn) + 2 * kg(Tf))
    return 4 * math.pi * K * mu(Tf) ** 2 * dT1 / (rho(Tf) * Tf) / (1 + 3 * C_M * kn)


def drag_force(a, v, T=T_AMB):
    return 6 * math.pi * mu(T) * a * v / cc(a, T)


def heat_temp(P_abs, a, alpha_T=0.9):
    """Mean mote temperature: conduction with the Fuchs temperature jump (zeta = (2-a)/a 2g/(g+1) lambda/Pr), no
    convection (Pe << 1 at 1 um), radiation neglected (< 1 % at 1 um)."""
    def f(T):
        Tf = 0.5 * (T + T_AMB)
        zeta = (2 - alpha_T) / alpha_T * 2 * 1.4 / 2.4 * mfp(Tf) / 0.71
        return 4 * math.pi * a * kint(T) / (1 + zeta / a) - P_abs
    return optimize.brentq(f, T_AMB, 3000.0)


def hold_I(a, v, j1A=0.486, A=1.0, kp=0.04, K=0.956, h=2.14, slip=True):
    """Peak intensity at the mote (W/m^2) for photophoretic force = drag(v), the mote heated by h x that beam
    (LP overhead). Returns I, mean T, hot-face T (mean + l=1 surface amplitude of the NET force dipole)."""
    Ts = T_AMB + 10
    for _ in range(60):
        F = drag_force(a, v, 0.5 * (Ts + T_AMB))
        f1 = creep_force(a, 1.0, kp, Ts, K, slip)           # force per unit q1
        q1 = F / f1
        I = q1 / (j1A * A)
        P = h * A * math.pi * a * a * I
        Tn = heat_temp(P, a)
        if abs(Tn - Ts) < 1e-3:
            break
        Ts = 0.5 * (Ts + Tn)
    Tf = 0.5 * (Ts + T_AMB)
    kn = mfp(Tf) / a if slip else 0.0
    dT1_solid = q1 * a * (1 + 2 * C_T * kn) / (kp * (1 + 2 * C_T * kn) + 2 * kg(Tf))
    return dict(I=I, Tm=Ts, T_hot=Ts + dT1_solid, q1=q1)


def slab_rta(n, k, t, lam, theta=0.0, pol="s", n0=1.0):
    """Reflectance, transmittance, absorptance of a homogeneous film (n + ik, thickness t) in a medium n0 (2x2
    characteristic-matrix method, oblique incidence)."""
    N1 = complex(n, k)
    s0 = n0 * math.sin(theta)
    c0 = math.cos(theta)
    c1 = np.sqrt(1 - (s0 / N1) ** 2)
    if pol == "s":
        e0, e1 = n0 * c0, N1 * c1
    else:
        e0, e1 = n0 / c0, N1 / c1
    d = 2 * math.pi / lam * N1 * c1 * t
    M = np.array([[np.cos(d), -1j * np.sin(d) / e1], [-1j * e1 * np.sin(d), np.cos(d)]])
    B, C = M @ np.array([1.0, e0])
    r = (e0 * B - C) / (e0 * B + C)
    tt = 2 * e0 / (e0 * B + C)
    R = abs(r) ** 2
    T = abs(tt) ** 2
    return R, T, 1 - R - T


def skin_sphere(n, k, t, lam=1.55e-6, nb=60):
    """Straight-ray sphere with a homogeneous absorbing skin (n + ik, thickness t) on an index-matched core: front pass,
    back pass, and one internal reflection back to the front. Returns A (absorption efficiency) and J1/A
    = (3/4) sum(P_i cos theta_i) / sum(P_i) (cos theta from the lit pole; front > 0, back < 0)."""
    b = (np.arange(nb) + 0.5) / nb
    Pf = Pb = Mf = Mb = 0.0
    for bi in b:
        th = math.asin(bi)
        Rs, Ts_, As = slab_rta(n, k, t, lam, th, "s")
        Rp, Tp, Ap = slab_rta(n, k, t, lam, th, "p")
        R, T, A1 = 0.5 * (Rs + Rp), 0.5 * (Ts_ + Tp), 0.5 * (As + Ap)
        w = 2 * bi / nb                       # ring weight, sum = 1 over the disc
        c = math.cos(th)
        front = A1 + T * R * A1               # first front pass + back-reflected light absorbed at the front
        back = T * A1                         # back pass (higher orders negligible)
        Pf += w * front
        Pb += w * back
        Mf += w * front * c
        Mb += w * back * (-c)
    A = Pf + Pb
    return A, 0.75 * (Mf + Mb) / A


def volume_absorber(alpha_a, nb=400):
    """Straight-ray Beer-Lambert sphere (n = 1), own implementation: A and J1/A."""
    b = (np.arange(nb) + 0.5) / nb
    c = np.sqrt(1 - b * b)
    L = 2 * c                                    # chord / a
    s = np.linspace(0, 1, 401)[None, :] * L[:, None]   # path coordinate / a
    dens = alpha_a * np.exp(-alpha_a * s)        # absorbed per unit path
    z = c[:, None] - s                           # axial coordinate / a (lit pole at +1)
    P = np.trapezoid(dens, s, axis=1)
    M = np.trapezoid(dens * z, s, axis=1)
    w = 2 * b / nb
    A = float(np.sum(w * P))
    # J1/A = (3/4) <z/a> for a volume source (first moment of the absorbed power)
    return A, float(0.75 * np.sum(w * M) / A)


def sec_phys():
    out = {}
    print("PHYS air at 293 K: mu %.3e, k %.4f, rho %.3f, mfp %.1f nm, Cc(1 um) %.3f" % (
        mu(T_AMB), kg(T_AMB), rho(T_AMB), mfp(T_AMB) * 1e9, cc(1e-6)))
    # --- I_unit for the 1 um ITO-aerogel mote, three creep coefficients, with and without slip
    rows = {}
    for K in (0.75, 0.956, 1.17):
        for slip in (True, False):
            r = hold_I(1e-6, 0.1, K=K, slip=slip)
            rows[f"K{K}_slip{slip}"] = r["I"] / 0.1
    out["I_unit"] = rows
    print("PHYS I_unit (W/m^2 per m/s, 1 um ITO aerogel, J1/A 0.486, A 1, k_p 0.04): " +
          ", ".join(f"{k} {v:.2e}" for k, v in rows.items()))
    sl = rows["K0.956_slipFalse"] / rows["K0.956_slipTrue"]
    out["slip_penalty_1um"] = 1 / sl
    # slip factor alone vs size
    for a in (0.5e-6, 1e-6, 2.5e-6, 5e-6):
        kn = mfp(T_AMB) / a
        s = 1 / ((1 + 3 * C_M * kn) * (1 + 2 * C_T * kn * 0.04 / (0.04 + 2 * kg(T_AMB))))
        r1 = hold_I(a, 0.1)["I"] / 0.1
        out[f"size_{a * 1e6:.1f}um"] = dict(s_ph=s, Cc=cc(a), I_unit=r1)
        print(f"PHYS a {a * 1e6:.1f} um: slip factor on F_ph {s:.3f}, Cc {cc(a):.3f}, I_unit {r1:.2e} W/m^2 per m/s")
    # --- cross-check with the project's model (m18.hold, physics.py)
    try:
        import m18_gaussian_lcsv as m18                       # CROSS-CHECK ONLY
        i18 = m18.hold(1e-6, 0.1)["I"] / 0.1
        out["xcheck_m18_I_unit"] = i18
        print(f"PHYS cross-check: m18.hold I_unit {i18:.2e} vs RT7 (K 0.956, slip) {rows['K0.956_slipTrue']:.2e} "
              f"(ratio {rows['K0.956_slipTrue'] / i18:.3f})")
    except Exception as ex:  # pragma: no cover
        print("PHYS cross-check failed:", ex)
    # --- heat at gust peaks (T7 sec 1.3): v_pk = U + 5.4 sigma, h_worst 2.14, occluded 4.47
    rooms = {"still": (0.0, 0.03), "home": (0.05, 0.03), "quiet_office": (0.10, 0.03), "office": (0.10, 0.10)}
    heat = {}
    for rn, (U, s) in rooms.items():
        v = U + 5.4 * s
        for A, j1A in ((1.0, 0.486), (0.5, 0.486), (0.62, 0.30)):
            r = hold_I(1e-6, v, j1A=j1A, A=A)
            ro = hold_I(1e-6, v, j1A=j1A, A=A, h=4.47)
            heat[f"{rn}_A{A}_j{j1A}"] = dict(v_pk=v, I=r["I"], Tm=r["Tm"], T_hot=r["T_hot"], T_hot_occ=ro["T_hot"])
        print(f"PHYS heat {rn:12s} v_pk {v:.3f} m/s: hot face {heat[f'{rn}_A1.0_j0.486']['T_hot']:.0f} K "
              f"(occluded {heat[f'{rn}_A1.0_j0.486']['T_hot_occ']:.0f}); A 0.5 {heat[f'{rn}_A0.5_j0.486']['T_hot']:.0f} K; "
              f"thin-skin-consistent A 0.62 J1/A 0.30: {heat[f'{rn}_A0.62_j0.3']['T_hot']:.0f} K "
              f"(occ {heat[f'{rn}_A0.62_j0.3']['T_hot_occ']:.0f})")
    out["heat"] = heat
    # --- absorber plausibility: thin film limit, skin on a sphere, volume absorber
    lam = 1.55e-6
    film = {}
    for t in (20e-9, 50e-9, 100e-9, 150e-9, 300e-9):
        best = (0, None)
        for n in np.linspace(0.2, 4.0, 39):
            for k in np.linspace(0.05, 8.0, 80):
                A1 = slab_rta(n, k, t, lam)[2]
                if A1 > best[0]:
                    best = (A1, (n, k))
        film[f"{t * 1e9:.0f}nm"] = dict(A_max=best[0], n=best[1][0], k=best[1][1])
    out["film_single_pass_max"] = film
    print("PHYS single-pass absorptance ceiling of a homogeneous film in air at 1550 nm (normal incidence): " +
          ", ".join(f"{k}: {v['A_max']:.2f} (n {v['n']:.1f}, k {v['k']:.1f})" for k, v in film.items()))
    # Drude ITO (N 1e27 m^-3, m* 0.35, gamma 1.5e14 rad/s, eps_inf 3.9) as a continuous skin
    w = 2 * math.pi * 2.998e8 / lam
    wp2 = 1e27 * (1.602e-19) ** 2 / (8.854e-12 * 0.35 * 9.109e-31)
    eps = 3.9 - wp2 / (w * w + 1j * 1.5e14 * w)
    nk = np.sqrt(eps)
    out["ito_drude_eps"] = [eps.real, eps.imag]
    sk = {}
    for t in (20e-9, 50e-9, 100e-9, 150e-9):
        A, j = skin_sphere(nk.real, nk.imag, t)
        sk[f"ITO_{t * 1e9:.0f}nm"] = dict(A=A, J1A=j, J1=A * j)
    # best homogeneous skin of thickness t on a 1 um sphere: maximise J1 = A * J1/A (what the force needs)
    for t in (50e-9, 100e-9, 150e-9, 250e-9):
        best = (0, None)
        for n in np.linspace(0.3, 3.0, 19):
            for k in np.linspace(0.1, 6.0, 40):
                A, j = skin_sphere(n, k, t)
                if A * j > best[0]:
                    best = (A * j, (n, k, A, j))
        sk[f"best_{t * 1e9:.0f}nm"] = dict(J1=best[0], n=best[1][0], k=best[1][1], A=best[1][2], J1A=best[1][3])
    out["skin_sphere"] = sk
    for kk, v in sk.items():
        print(f"PHYS skin {kk:14s}: A {v['A']:.2f}  J1/A {v['J1A']:.3f}  J1 = A J1/A {v.get('J1', v['A'] * v['J1A']):.3f}"
              + (f"  (n {v['n']:.2f}, k {v['k']:.2f})" if 'n' in v else ""))
    vol = {}
    for aa in (0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0):
        A, j = volume_absorber(aa)
        vol[str(aa)] = dict(A=A, J1A=j, J1=A * j)
    out["volume_absorber"] = vol
    print("PHYS volume absorber (n = 1, straight rays), alpha*a: " +
          ", ".join(f"{k}: A {v['A']:.2f} J1/A {v['J1A']:.2f} J1 {v['J1']:.2f}" for k, v in vol.items()))
    try:
        import physics as ph                                     # CROSS-CHECK ONLY
        out["xcheck_physics_j1A_aa2"] = [ph.absorptance(2.0), ph.j1_over_A(2.0)]
        print(f"PHYS cross-check physics.py alpha*a 2: A {ph.absorptance(2.0):.3f} J1/A {ph.j1_over_A(2.0):.3f} vs RT7 "
              f"{vol['2.0']['A']:.3f} / {vol['2.0']['J1A']:.3f}")
    except Exception as ex:  # pragma: no cover
        print("PHYS physics cross-check failed:", ex)
    # FOM ceiling: J1/A <= 0.75 (point absorber at the lit pole), 0.5 skin; k_p >= 0.005-0.02; k_g at 300-330 K
    fom = {}
    for j1A in (0.5, 0.75):
        for kp in (0.0, 0.01, 0.02):
            fom[f"j{j1A}_kp{kp}"] = j1A / (kp + 2 * kg(310.0))
    out["FOM_ceiling"] = fom
    print("PHYS FOM ceiling (m K/W) at T_f 310 K: " + ", ".join(f"{k} {v:.1f}" for k, v in fom.items()) +
          f"; today's mote {0.486 / (0.04 + 2 * kg(310.0)):.2f}")
    dump("phys", out)
    return out


# ======================================================================================================================
# Section mie: own BHMIE, anomalous-diffraction cross-check, ripples, nulls, size spread
# ======================================================================================================================
def mie_S(x, m, mu_):
    """Own Mie implementation (Wiscombe-style upward Riccati-Bessel, logarithmic derivative by downward recurrence).
    Returns Qext, Qsca, S1(mu), S2(mu)."""
    nmax = int(x + 4.05 * x ** (1 / 3) + 2)
    mx = m * x
    nd = int(max(nmax, abs(mx))) + 20
    D = np.zeros(nd + 1, complex)
    for n in range(nd, 0, -1):
        D[n - 1] = n / mx - 1 / (D[n] + n / mx)
    n = np.arange(1, nmax + 1)
    # Riccati-Bessel psi_n(x) = x j_n(x), xi_n = x h_n^(1)(x)
    jn = special.spherical_jn(np.arange(0, nmax + 1), x)
    yn = special.spherical_yn(np.arange(0, nmax + 1), x)
    psi = x * jn
    xi = x * (jn + 1j * yn)
    psi_n, psi_m1 = psi[1:], psi[:-1]
    xi_n, xi_m1 = xi[1:], xi[:-1]
    Dn = D[1:nmax + 1]
    a = ((Dn / m + n / x) * psi_n - psi_m1) / ((Dn / m + n / x) * xi_n - xi_m1)
    b = ((m * Dn + n / x) * psi_n - psi_m1) / ((m * Dn + n / x) * xi_n - xi_m1)
    Qext = 2 / x ** 2 * np.sum((2 * n + 1) * (a.real + b.real))
    Qsca = 2 / x ** 2 * np.sum((2 * n + 1) * (np.abs(a) ** 2 + np.abs(b) ** 2))
    mu_ = np.atleast_1d(mu_)
    pi_prev = np.zeros_like(mu_)
    pi_cur = np.ones_like(mu_)
    S1 = np.zeros_like(mu_, complex)
    S2 = np.zeros_like(mu_, complex)
    for i in range(nmax):
        nn = i + 1
        tau = nn * mu_ * pi_cur - (nn + 1) * pi_prev
        f = (2 * nn + 1) / (nn * (nn + 1))
        S1 += f * (a[i] * pi_cur + b[i] * tau)
        S2 += f * (a[i] * tau + b[i] * pi_cur)
        pi_prev, pi_cur = pi_cur, ((2 * nn + 1) * mu_ * pi_cur - (nn + 1) * pi_prev) / nn
    return Qext, Qsca, S1, S2


def q_iso(a, lam, m, th_deg):
    """Isotropic-equivalent scattering efficiency 4 pi (dC/dOmega)/(pi a^2) = 2(|S1|^2+|S2|^2)/x^2 (unpolarised)."""
    x = 2 * math.pi * a / lam
    _, _, S1, S2 = mie_S(x, m, np.cos(np.radians(th_deg)))
    return 2 * (np.abs(S1) ** 2 + np.abs(S2) ** 2) / x ** 2


def q_ada(a, lam, m, th_deg, nb=2000):
    """Anomalous diffraction (van de Hulst) amplitude S(theta) = x^2 int_0^1 [1 - exp(-i rho sqrt(1-b^2))]
    J0(x b sin theta) b db, rho = 2 x (m - 1); q_iso = 4 |S|^2 / x^2 (both polarisations equal)."""
    x = 2 * math.pi * a / lam
    rho_c = 2 * x * (m - 1)
    b = (np.arange(nb) + 0.5) / nb
    ph = 1 - np.exp(-1j * rho_c * np.sqrt(1 - b * b))
    th = np.radians(np.atleast_1d(th_deg))
    J = special.j0(x * np.outer(np.sin(th), b))
    S = x * x * (J * (ph * b)[None, :]).sum(axis=1) / nb
    return 4 * np.abs(S) ** 2 / x ** 2


def window_avg(fun, centre, half=2.5, n=41):
    th = np.linspace(centre - half, centre + half, n)
    return float(np.mean(fun(th)))


def sec_mie():
    out = dict(table={}, ada={}, spread={}, nulls={}, sens={})
    lam, m = 500e-9, complex(1.04, 1e-4)
    # self-test against the Bohren-Huffman BHMIE example (x 3, m 1.55): Qext 3.1054, Qsca 3.1054 [memory, RT6 used it]
    x_bh = 2 * math.pi * 0.525 / 0.6328          # Bohren-Huffman BHMIE test case: a 0.525 um, lambda 0.6328 um, m 1.55
    Qe, Qs, _, _ = mie_S(x_bh, complex(1.55, 0.0), np.array([1.0]))
    print(f"MIE self-test BH case (x {x_bh:.3f}, m 1.55): Qext {Qe:.4f} (BH 3.1054), Qsca {Qs:.4f}")
    out["selftest"] = [Qe, Qs]
    angles = (5, 8, 10, 12, 15, 17, 20, 25, 30, 90)
    print("MIE q_iso at 500 nm, n 1.04+1e-4i, averaged +-2.5 deg (T7 table: a 0.75/1.0/1.5 um, q(10) 12.8/24.5/27, "
          "q(15) 5.7/5.0/2.0, q(20) 1.5/0.25/1.4):")
    for a in (0.5e-6, 0.75e-6, 1.0e-6, 1.25e-6, 1.5e-6, 2.5e-6):
        row = {str(t): window_avg(lambda th: q_iso(a, lam, m, th), t) for t in angles}
        out["table"][f"{a * 1e6:.2f}"] = row
        ada = {str(t): window_avg(lambda th: q_ada(a, lam, m, th), t) for t in (10, 15, 20)}
        out["ada"][f"{a * 1e6:.2f}"] = ada
        print(f"  a {a * 1e6:4.2f} um: " + "  ".join(f"{k}:{v:.3g}" for k, v in row.items()) +
              f"   | ADA 10/15/20: {ada['10']:.3g}/{ada['15']:.3g}/{ada['20']:.3g}")
    # cross-check against RT6's BHMIE (same physics, other code)
    try:
        import rt6_check as rt6                                    # CROSS-CHECK ONLY
        r = rt6.q_iso_profile(1e-6, lam, m, angles_deg=(10, 15, 20, 90), halfwidth=2.5)
        out["xcheck_rt6"] = r["q_iso"]
        print(f"MIE cross-check rt6.q_iso_profile a 1 um: {r['q_iso']}  (RT7: 10 {out['table']['1.00']['10']:.3g}, "
              f"15 {out['table']['1.00']['15']:.3g}, 20 {out['table']['1.00']['20']:.3g}, 90 {out['table']['1.00']['90']:.3g})")
    except Exception as ex:  # pragma: no cover
        print("MIE rt6 cross-check failed:", ex)
    # nulls of the first minimum (fine grid, unaveraged)
    th = np.linspace(2, 40, 761)
    for a in (0.75e-6, 1.0e-6, 1.5e-6):
        q = q_iso(a, lam, m, th)
        i = np.where((q[1:-1] < q[:-2]) & (q[1:-1] < q[2:]))[0] + 1
        out["nulls"][f"{a * 1e6:.2f}"] = [float(th[j]) for j in i[:3]]
        print(f"MIE first minima, a {a * 1e6:.2f} um: {[round(float(th[j]), 1) for j in i[:3]]} deg "
              f"(depth q_min/q(10deg) {q[i[0]] / q_iso(a, lam, m, np.array([10.0]))[0]:.3f})")
    # sensitivity: d ln q / d theta at 15 deg (1 um) and size sensitivity d ln q / d ln a
    a = 1e-6
    q14, q16 = (window_avg(lambda t: q_iso(a, lam, m, t), c) for c in (14, 16))
    qa1, qa2 = (window_avg(lambda t: q_iso(aa, lam, m, t), 15) for aa in (0.95e-6, 1.05e-6))
    out["sens"] = dict(dlnq_dtheta_per_deg_15=(math.log(q16) - math.log(q14)) / 2,
                       dlnq_dlna_15=(math.log(qa2) - math.log(qa1)) / (math.log(1.05) - math.log(0.95)))
    print(f"MIE sensitivity at 15 deg, a 1 um: d ln q/d theta {out['sens']['dlnq_dtheta_per_deg_15']:.2f} per deg; "
          f"d ln q/d ln a {out['sens']['dlnq_dlna_15']:.1f}")
    # size spread: uniform +-10 % in radius around the nominal; the batch mean and the mote-to-mote spread at a fixed
    # angle (each mote is ONE size, so the viewer sees the spread as brightness non-uniformity)
    for a0 in (0.75e-6, 1.0e-6, 1.5e-6):
        aa = a0 * np.linspace(0.9, 1.1, 41)
        for t in (8, 10, 12, 15, 17):
            qs = np.array([q_iso(x_, lam, m, np.array([float(t)]))[0] for x_ in aa])
            out["spread"][f"{a0 * 1e6:.2f}_{t}"] = dict(mean=float(qs.mean()), p10=float(np.percentile(qs, 10)),
                                                        p90=float(np.percentile(qs, 90)), min=float(qs.min()),
                                                        max=float(qs.max()))
        print(f"MIE +-10 % radius spread, a {a0 * 1e6:.2f} um: " + "  ".join(
            f"{t}deg mean {out['spread'][f'{a0 * 1e6:.2f}_{t}']['mean']:.2g} [min {out['spread'][f'{a0 * 1e6:.2f}_{t}']['min']:.2g}, "
            f"max {out['spread'][f'{a0 * 1e6:.2f}_{t}']['max']:.2g}]" for t in (10, 15, 17)))
    # the usable angular window: where q >= 2 (40 % of T7's design q 5) for a 1 um mote +-10 %
    th = np.linspace(1, 30, 291)
    for a0 in (0.75e-6, 1.0e-6):
        qmin = np.min([q_iso(a0 * f, lam, m, th) for f in (0.9, 0.95, 1.0, 1.05, 1.1)], axis=0)
        ok = th[qmin >= 2.0]
        out[f"window_q2_{a0 * 1e6:.2f}"] = [float(ok.min()), float(ok.max())] if ok.size else None
        # first angle where the worst size drops below 2
        bad = th[qmin < 2.0]
        print(f"MIE a {a0 * 1e6:.2f} um +-10 %: worst-size q >= 2 from {ok.min():.1f} up to {bad.min():.1f} deg "
              f"(contiguous window)")
        out[f"window_q2_{a0 * 1e6:.2f}"] = [float(ok.min()), float(bad.min())]
    dump("mie", out)
    return out


# ======================================================================================================================
# Section vis: forward-illumination geometry for several viewers, emitter count, visible modes, glow, sensing photons
# ======================================================================================================================
ROOM = np.array([6.0, 5.0, 2.8])
CENTER = np.array([3.0, 2.5, 1.3])
HALF = np.array([0.5, 0.5, 0.4])
H10 = np.array([(0.15, 0.15, 2.7), (5.85, 0.15, 2.7), (5.85, 4.85, 2.7), (0.15, 4.85, 2.7),
                (0.15, 0.15, 0.12), (5.85, 0.15, 0.12), (5.85, 4.85, 0.12), (0.15, 4.85, 0.12),
                (3.0, 2.5, 2.75), (3.0, 2.5, 0.05)])          # M4/RT6 H10 head coordinates (m)


def wall_emitters(spacing, z_lo=0.2, z_hi=2.6):
    pts = []
    zs = np.arange(z_lo, z_hi + 1e-9, spacing)
    for x in np.arange(spacing / 2, ROOM[0], spacing):
        for z in zs:
            pts += [(x, 0.02, z), (x, ROOM[1] - 0.02, z)]
    for y in np.arange(spacing / 2, ROOM[1], spacing):
        for z in zs:
            pts += [(0.02, y, z), (ROOM[0] - 0.02, y, z)]
    return np.array(pts)


def angle_deg(u, v):
    c = np.sum(u * v, axis=-1) / (np.linalg.norm(u, axis=-1) * np.linalg.norm(v, axis=-1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def coverage(E, n_view, th1, th2, n_trials=40, n_motes=300, eye_clear=2.0, seed=0, r_view=(1.6, 2.4)):
    """Fraction of (viewer, mote) pairs that some emitter can light within the forward window [th1, th2] (scattering
    angle at the mote between emitter->mote and mote->viewer) while its direct beam beyond the mote misses every viewer's
    eye by > eye_clear degrees. Viewers on a horizontal ring around the image (random azimuths >= 40 deg apart)."""
    rng = np.random.default_rng(seed)
    ok_tot = n_tot = 0
    per_view_emitters = []
    for _ in range(n_trials):
        az = []
        while len(az) < n_view:
            a = rng.uniform(0, 2 * math.pi)
            if all(abs((a - b + math.pi) % (2 * math.pi) - math.pi) > math.radians(40) for b in az):
                az.append(a)
        r = rng.uniform(*r_view, n_view)
        eyes = np.stack([CENTER[0] + r * np.cos(az), CENTER[1] + r * np.sin(az), 1.6 + rng.uniform(-0.1, 0.1, n_view)], 1)
        eyes = np.clip(eyes, [0.3, 0.3, 1.0], ROOM - 0.3)
        M = CENTER + (rng.random((n_motes, 3)) * 2 - 1) * HALF
        din = M[:, None, :] - E[None, :, :]                       # emitter -> mote (n_m, n_e, 3)
        for v in range(n_view):
            dout = eyes[v][None, :] - M                               # mote -> viewer
            th = angle_deg(din, dout[:, None, :])
            good = (th >= th1) & (th <= th2)
            for o in range(n_view):                                   # direct beam must miss all eyes
                th_o = angle_deg(din, (eyes[o][None, :] - M)[:, None, :])
                good &= th_o > eye_clear
            ok = good.any(axis=1)
            ok_tot += ok.sum()
            n_tot += n_motes
            per_view_emitters.append(int(good.any(axis=0).sum()))
    return ok_tot / n_tot, float(np.mean(per_view_emitters))


def modes_gauss(L, w, clip=1.2, os_=1.5):
    return (2 * clip * os_ * L / (math.pi * w)) ** 2


def sec_vis():
    out = dict(coverage={})
    lam, m = 500e-9, complex(1.04, 1e-4)
    # --- forward-window coverage vs emitter spacing on the walls
    print("VIS forward-illumination coverage: emitters on a wall grid, viewers on a ring at 1.6-2.4 m, eye height 1.6 m")
    for (th1, th2) in ((10.0, 20.0), (3.0, 15.0), (4.0, 10.0)):
        for n_view in (1, 3):
            for spacing in (1.0, 0.5, 0.3, 0.2):
                E = wall_emitters(spacing)
                f, used = coverage(E, n_view, th1, th2, n_trials=12 if spacing < 0.3 else 20, n_motes=200)
                out["coverage"][f"{th1}-{th2}_v{n_view}_s{spacing}"] = dict(n_emitters=len(E), frac=f, used_per_viewer=used)
                print(f"  window {th1:4.1f}-{th2:4.1f} deg, {n_view} viewers, spacing {spacing:.1f} m ({len(E):4d} emitters):"
                      f" pairs covered {100 * f:5.1f}%, emitters useful per viewer {used:.0f}")
    # --- modes per visible emitter (same counting rule as T7) and totals
    L = math.sqrt(1.2)
    vm = {}
    for wv in (14.4e-6, 25e-6, 34e-6):
        Pv = 10.7e-6 * (wv / 14.4e-6) ** 2       # same intensity at the mote
        vm[f"{wv * 1e6:.1f}"] = dict(modes_per_emitter=modes_gauss(L, wv), P_spot_uW=Pv * 1e6,
                                     class1_vis_ok_6p6=Pv * 6.6 <= 0.39e-3)
    out["vis_modes"] = vm
    print("VIS modes per visible emitter (T7 rule (2 clip os L/(pi w))^2, L = sqrt(1.2) m): " + ", ".join(
        f"w_v {k} um: {v['modes_per_emitter']:.2e} (spot {v['P_spot_uW']:.0f} uW)" for k, v in vm.items()) +
          f"; IR head at w 51 um: {modes_gauss(L, 51e-6):.2e}")
    # --- emitter glow seen by the viewer it serves (non-signal light of the emitter hologram)
    P_e = 0.07 / 15
    Omega_f = (1.0 / 3.0) ** 2
    ap = (2 * 1.2 * 500e-9 * 3.0 / (math.pi * 14.4e-6)) ** 2
    out["glow"] = {}
    for frac in (0.25, 1e-2, 1e-3):
        I_cd = frac * P_e / Omega_f * 683 * 0.323
        out["glow"][str(frac)] = dict(I_cd=I_cd, L_cd_m2=I_cd / ap)
    J_mote = 3.0 * 1e-3 * 3e-3
    print(f"VIS emitter glow toward its viewer (P_e {P_e * 1e3:.1f} mW, field {Omega_f:.2f} sr, aperture {math.sqrt(ap) * 1e3:.0f} mm): "
          + ", ".join(f"non-signal {k}: {v['I_cd']:.2e} cd, {v['L_cd_m2']:.1f} cd/m^2" for k, v in out["glow"].items())
          + f"; one mote {J_mote:.1e} cd, whole sketch {J_mote * 1667:.3f} cd")
    # --- sensing photons per 0.2 ms frame, 25 mm lens at 1.5 m
    Om = math.pi * 0.0125 ** 2 / 1.5 ** 2
    E_ph_v, E_ph_ir = 6.626e-34 * 2.998e8 / 500e-9, 6.626e-34 * 2.998e8 / 1.55e-6
    I_v = 2 * 10.7e-6 / (math.pi * 14.4e-6 ** 2)
    I_ir = 3.5e5
    a = 1e-6
    q90 = window_avg(lambda t: q_iso(a, lam, m, t), 90)
    q15 = window_avg(lambda t: q_iso(a, lam, m, t), 15)
    th = np.array([20.0, 40.0, 60.0])
    q_ir = q_iso(a, 1.55e-6, complex(1.05, 0.12), th)
    x_ir = 2 * math.pi * a / 1.55e-6
    Qe_ir, Qs_ir, _, _ = mie_S(x_ir, complex(1.05, 0.12), np.array([1.0]))
    ph = {}
    for name, I, q, Eph, qe in (("vis_90deg", I_v, q90, E_ph_v, 0.7), ("vis_15deg", I_v, q15, E_ph_v, 0.7),
                                ("ir_20deg", I_ir, q_ir[0], E_ph_ir, 0.8), ("ir_40deg", I_ir, q_ir[1], E_ph_ir, 0.8),
                                ("ir_60deg", I_ir, q_ir[2], E_ph_ir, 0.8)):
        P = I * q * a * a / 4 * Om
        N = P / Eph * 2e-4 * qe
        sig = {f"px{int(p * 1e6)}um": math.sqrt((max(p, 2e-4) ** 2 / 4 + p * p / 12) / max(N, 1e-9)) * 1e6 for p in (1e-4, 5e-4)}
        ph[name] = dict(q=float(q), photoelectrons=N, sigma_um=sig)
    out["photons"] = ph
    out["ir_mote_Q"] = dict(Qext=Qe_ir, Qsca=Qs_ir, Qabs=Qe_ir - Qs_ir)
    print(f"VIS sensing (25 mm lens at 1.5 m, 0.2 ms): IR mote proxy m 1.05+0.12i Qabs {Qe_ir - Qs_ir:.2f} Qsca {Qs_ir:.2f}")
    for k, v in ph.items():
        print(f"  {k:10s} q {v['q']:.3g}: {v['photoelectrons']:.3g} photoelectrons/frame -> sigma " +
              ", ".join(f"{kk} {vv:.1f} um" for kk, vv in v["sigma_um"].items()))
    dump("vis", out)
    return out


# ======================================================================================================================
# Section modes: per-head hologram pixel count with the real H10 geometry; os/clip conventions; RT6 comparison
# ======================================================================================================================
def box_points(n=12):
    g = np.linspace(-1, 1, n)
    P = []
    for i in range(3):
        for s_ in (-1, 1):
            A, B = np.meshgrid(g, g)
            pts = np.zeros((A.size, 3))
            pts[:, i] = s_
            pts[:, (i + 1) % 3] = A.ravel()
            pts[:, (i + 2) % 3] = B.ravel()
            P.append(pts)
    return CENTER + np.vstack(P) * HALF


def head_modes(head, w, clip=1.2, os_=1.5):
    """Pixels for one head: square aperture 2 clip W_max (W_max = lam d_max/(pi w), the farthest voxel) times the
    angular field the volume subtends from the head (pitch lam / (2 os sin theta_half) per axis, axes chosen as the
    principal axes of the projected volume). Independent of lam."""
    P = box_points()
    v = P - head
    d = np.linalg.norm(v, axis=1)
    u = v / d[:, None]
    ax = (CENTER - head) / np.linalg.norm(CENTER - head)
    e1 = np.cross(ax, [0, 0, 1.0]) if abs(ax[2]) < 0.9 else np.cross(ax, [1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    t1, t2 = u @ e1, u @ e2                                  # direction sines in the two transverse axes
    # centre the field on its own mid-point (a tilted carrier is free)
    sx = 0.5 * (t1.max() - t1.min())
    sy = 0.5 * (t2.max() - t2.min())
    Nx = 2 * clip * d.max() / (math.pi * w) * 2 * os_ * sx
    Ny = 2 * clip * d.max() / (math.pi * w) * 2 * os_ * sy
    return dict(M=Nx * Ny, d_max=float(d.max()), d_min=float(d.min()), sin_half=(float(sx), float(sy)),
                aperture_mm=2 * clip * 1.55e-6 * d.max() / (math.pi * w) * 1e3, pitch_um=1.55 / (2 * os_ * max(sx, sy)))


def sec_modes():
    out = dict(heads=[])
    w = 51e-6
    L = math.sqrt(1.2)
    t7 = modes_gauss(L, w)
    tot = 0.0
    for i, h in enumerate(H10):
        r = head_modes(h, w)
        tot += r["M"]
        out["heads"].append(r)
        print(f"MODES head {i} {tuple(h)}: d {r['d_min']:.2f}-{r['d_max']:.2f} m, sin(half-field) {r['sin_half'][0]:.3f} x "
              f"{r['sin_half'][1]:.3f}, aperture {r['aperture_mm']:.0f} mm, pitch {r['pitch_um']:.2f} um, M {r['M']:.2e} "
              f"(T7 per head {t7:.2e}, x{r['M'] / t7:.1f})")
    out["total_H10"] = tot
    out["t7_total"] = 10 * t7
    print(f"MODES H10 total at w 51 um: {tot:.2e} vs T7 {10 * t7:.2e} (x{tot / (10 * t7):.2f})")
    # conventions: etendue minimum, T7 clip/os, RT6 flat-top at rho 1 (bare and with T7's conventions)
    A_f = 1.2
    et = A_f / (math.pi * w * w)
    rt6_bare = A_f * math.pi / w ** 2                       # rho = 1, NA = lam / r_c, r_c = w
    rt6_conv = rt6_bare * 1.5 ** 2 * 4 / math.pi             # + os^2 and a square aperture enclosing the disc
    out["conventions"] = dict(etendue_min=et, t7=t7, rt6_bare_rho1=rt6_bare, rt6_t7conv_rho1=rt6_conv,
                              ratio_t7_over_min=t7 / et, ratio_rt6conv_over_t7=rt6_conv / t7,
                              ratio_rt6bare_over_min=rt6_bare / et)
    print(f"MODES conventions at w = r_c = 51 um, A_f 1.2 m^2: etendue minimum {et:.2e}; T7 {t7:.2e} (x{t7 / et:.2f}); "
          f"RT6 flat-top rho 1 bare {rt6_bare:.2e} (x{rt6_bare / et:.1f} the minimum, x{rt6_bare / t7:.1f} T7); with T7's os/square "
          f"conventions {rt6_conv:.2e} (x{rt6_conv / t7:.1f} T7)")
    # pixel-envelope efficiency at os 1.5: arithmetic and harmonic mean (uniform spots across the field)
    x = np.linspace(-1 / 3, 1 / 3, 801)
    X, Y = np.meshgrid(x, x)
    e = (np.sinc(X) * np.sinc(Y)) ** 2
    out["envelope"] = dict(arith=float(e.mean()), harmonic=float(1 / np.mean(1 / e)), corner=float(e.min()))
    print(f"MODES pixel envelope at os 1.5: mean {e.mean():.3f}, harmonic {1 / np.mean(1 / e):.3f}, corner {e.min():.3f} "
          f"(T7 text says 0.65; m18 code uses {0.787:.3f})")
    # clip 1.2 truncation loss of a Gaussian by a square of half-side 1.2 W
    tr = special.erf(math.sqrt(2) * 1.2) ** 2
    out["clip_transmission"] = tr
    print(f"MODES clip 1.2: square aperture passes {tr:.3f} of the Gaussian beam")
    dump("modes", out)
    return out


# ======================================================================================================================
# Turbulence (own): 3D isotropic von Karman-Pao, longitudinal + transverse Eulerian spectra by Taylor, plus mean wind
# ======================================================================================================================
NU = 1.5e-5


def spectra_1d(sigma, L11, Uc, f, Ceps=0.5):
    """One-sided frequency spectra (m^2/s^2/Hz) of the longitudinal and transverse velocity at a fixed point."""
    eps = Ceps * sigma ** 3 / L11
    eta = (NU ** 3 / eps) ** 0.25
    ke = 0.747 / L11
    k = np.logspace(-3, 6, 6000)
    E = k ** 4 / (ke * ke + k * k) ** (17 / 6) * np.exp(-5.2 * (np.sqrt(np.sqrt((k * eta) ** 4 + 0.4 ** 4)) - 0.4))
    E *= 1.5 * sigma ** 2 / np.trapezoid(E, k)
    k1 = 2 * math.pi * np.asarray(f) / Uc
    # E11(k1) = int_k1^inf E/k (1 - k1^2/k^2) dk ; E22 = int_k1^inf E/(2k) (1 + k1^2/k^2) dk  (Pope 6.211-6.212)
    cE = np.concatenate([[0], np.cumsum(0.5 * (E[1:] / k[1:] + E[:-1] / k[:-1]) * np.diff(k))])
    cE3 = np.concatenate([[0], np.cumsum(0.5 * (E[1:] / k[1:] ** 3 + E[:-1] / k[:-1] ** 3) * np.diff(k))])
    I1 = cE[-1] - np.interp(k1, k, cE)
    I3 = cE3[-1] - np.interp(k1, k, cE3)
    E11 = I1 - k1 ** 2 * I3
    E22 = 0.5 * (I1 + k1 ** 2 * I3)
    S11 = E11 * 2 * math.pi / Uc
    S22 = E22 * 2 * math.pi / Uc
    return S11, S22, eta


def gen_drafts(n_motes, dur, fs, sigma, L11, U, Uc, rng):
    """Velocity time series (n_motes, 3, n) = mean wind U along a random horizontal unit vector e_m + turbulence whose
    longitudinal component lies along e_m (transverse along the other two axes)."""
    n = int(dur * fs) + 2
    f = np.fft.rfftfreq(n, 1 / fs)
    S11, S22, _ = spectra_1d(sigma, L11, Uc, np.maximum(f, 1e-6))
    S11[0] = S22[0] = 0
    out = np.zeros((n_motes, 3, n), np.float32)
    phi = rng.uniform(0, 2 * math.pi, n_motes)
    e1 = np.stack([np.cos(phi), np.sin(phi), np.zeros(n_motes)], 1)
    e2 = np.stack([-np.sin(phi), np.cos(phi), np.zeros(n_motes)], 1)
    e3 = np.tile([0, 0, 1.0], (n_motes, 1))
    for comp, S, E_ in ((0, S11, e1), (1, S22, e2), (2, S22, e3)):
        amp = np.sqrt(S * fs * n / 4)
        X = (rng.normal(size=(n_motes, f.size)) + 1j * rng.normal(size=(n_motes, f.size))) * amp
        x = np.fft.irfft(X, n=n, axis=1)
        tgt = math.sqrt(np.trapezoid(S, f))
        x *= (tgt / x.std(axis=1, keepdims=True))
        if comp == 0:
            x += U
        out += (x[:, None, :] * E_[:, :, None]).astype(np.float32)
    return out


# ======================================================================================================================
# LP allocation (own, hull-equation method) and checks
# ======================================================================================================================
class Alloc:
    """Minimum-sum nonnegative c with sum_j c_j k_j = f, for many motes at once. For each mote: hull of the unit beam
    vectors k_j; the ray along f leaves the hull through the facet maximising n.f / (-b); c = facet barycentric / s."""

    def __init__(self, homes, heads=H10):
        self.K = []
        n_f = []
        for hm in homes:
            K = hm - heads
            K /= np.linalg.norm(K, axis=1)[:, None]
            self.K.append(K)
            n_f.append(len(ConvexHull(K).simplices))
        self.K = np.array(self.K)
        nm, nf = len(homes), max(n_f)
        self.N = np.zeros((nm, nf, 3))
        self.B = -np.ones((nm, nf))
        self.Minv = np.zeros((nm, nf, 3, 3))
        self.idx = np.zeros((nm, nf, 3), int)
        for i, K in enumerate(self.K):
            hull = ConvexHull(K)
            for j, (simp, eq) in enumerate(zip(hull.simplices, hull.equations)):
                self.N[i, j] = eq[:3]
                self.B[i, j] = eq[3]
                self.Minv[i, j] = np.linalg.inv(K[simp].T)
                self.idx[i, j] = simp
        self.ar = np.arange(nm)

    def __call__(self, f):
        r = np.einsum("mfk,mk->mf", self.N, f) / (-self.B)
        j = np.argmax(r, axis=1)
        c = np.einsum("mkl,ml->mk", self.Minv[self.ar, j], f)
        return self.idx[self.ar, j], np.maximum(c, 0.0)


def lp_check(n=300, seed=3):
    from scipy.optimize import linprog
    rng = np.random.default_rng(seed)
    home = CENTER + (rng.random((1, 3)) * 2 - 1) * HALF
    al = Alloc(home)
    dev = err = 0.0
    for _ in range(n):
        f = rng.normal(size=3)
        f /= np.linalg.norm(f)
        idx, c = al(f[None, :])
        K = al.K[0]
        res = linprog(np.ones(10), A_eq=K.T, b_eq=f, bounds=[(0, None)] * 10, method="highs")
        dev = max(dev, abs(c.sum() - res.fun))
        err = max(err, np.linalg.norm(c[0] @ K[idx[0]] - f))
    return dev, err


# ======================================================================================================================
# Section b9: the speed bound, stacking with LP weights and aligned strokes, Class 1 window averages
# ======================================================================================================================
def beam_frac(rho, w, R=1.75e-3):
    """Exact fraction of a Gaussian beam (1/e^2 radius w) through a disc of radius R whose centre is rho from the axis
    (noncentral chi-square, 2 dof)."""
    return stats.ncx2.cdf(4 * R * R / (w * w), 2, 4 * rho * rho / (w * w))


def exposure_pts(points, heads_xyz, foci, P_beam, w0, lam=1.55e-6, R=1.75e-3):
    zR = math.pi * w0 * w0 / lam
    D = foci - heads_xyz
    Lb = np.linalg.norm(D, axis=1)
    U_ = D / Lb[:, None]
    E = np.zeros(len(points))
    for i, p in enumerate(points):
        v = p - heads_xyz
        t = np.einsum("ij,ij->i", v, U_)
        rho2 = np.maximum(np.einsum("ij,ij->i", v, v) - t * t, 0)
        z = t - Lb
        wz = w0 * np.sqrt(1 + (z / zR) ** 2)
        fr = beam_frac(np.sqrt(rho2), wz, R)
        fr[t < 0] = 0
        E[i] = np.sum(P_beam * fr)
    return E


def strokes_rt7(S, delta, rng):
    """Own synthetic line content: random 3D circular arcs, radius 3-20 cm, 60-300 deg, inside the volume."""
    pts, tot = [], 0.0
    while tot < S:
        R = rng.uniform(0.03, 0.2)
        ang = math.radians(rng.uniform(60, 300))
        c = CENTER + HALF * rng.uniform(-0.75, 0.75, 3)
        nr = rng.normal(size=3)
        nr /= np.linalg.norm(nr)
        a1 = np.cross(nr, rng.normal(size=3))
        a1 /= np.linalg.norm(a1)
        a2 = np.cross(nr, a1)
        n = max(2, int(R * ang / delta))
        t = np.linspace(0, ang, n)
        p = c + R * (np.cos(t)[:, None] * a1 + np.sin(t)[:, None] * a2)
        p = p[np.all(np.abs(p - CENTER) <= HALF, axis=1)]
        pts.append(p)
        tot += R * ang
    return np.vstack(pts)


def mean_c(homes, n_dir=3000, seed=11):
    """E over isotropic draft directions of the LP coefficient of every head, per mote (for |u| independent of
    direction, the mean beam power of head j at mote m is P_unit E|u|/E|u| * E[c_j])."""
    rng = np.random.default_rng(seed)
    al = Alloc(homes)
    D = rng.normal(size=(n_dir, 3))
    D /= np.linalg.norm(D, axis=1)[:, None]
    C = np.zeros((len(homes), 10))
    hw = np.zeros(len(homes))
    for d in D:
        idx, c = al(np.tile(d, (len(homes), 1)))
        np.add.at(C, (np.repeat(np.arange(len(homes)), 3), idx.ravel()), c.ravel())
        hw = np.maximum(hw, c.sum(axis=1))
    return C / n_dir, hw


def stacking_case(motes, w, probes, weights=None, rng=None, random_heads=False):
    """Mean summed exposure at probe points, in units of the per-focus unit power P_unit (beam power for unit LP
    coefficient). weights: (n_m, 10) mean LP coefficient per head; random_heads: m17's model (3 random heads,
    equal split of h_worst-free unit focus power)."""
    if random_heads:
        hs, fs, pw = [], [], []
        for mo in motes:
            for j in rng.choice(10, 3, replace=False):
                hs.append(H10[j])
                fs.append(mo)
                pw.append(1.0 / 3)
    else:
        hs, fs, pw = [], [], []
        for mo, wt in zip(motes, weights):
            for j in range(10):
                if wt[j] > 1e-6:
                    hs.append(H10[j])
                    fs.append(mo)
                    pw.append(wt[j])
    return exposure_pts(probes, np.array(hs), np.array(fs), np.array(pw), w)


def sec_b9(quick=False):
    out = dict(bound={}, stacking={}, windows={})
    AEL = 1000.0 * math.pi * 1.75e-3 ** 2                         # 9.62 mW (t > 10 s, 3.5 mm)
    print(f"B9 Class 1 at 1500-1800 nm [memory; MPE 0.1 W/cm^2 and 1.5 t^0.375 mm aperture confirmed by search]: "
          f"AEL(t>10 s) = 1000 W/m^2 x 3.5 mm disc = {AEL * 1e3:.2f} mW; AEL(t<=0.35 s) = 1e4 J/m^2 x 1 mm disc = "
          f"{1e4 * math.pi * 0.5e-3 ** 2 * 1e3:.2f} mJ")
    # power-equivalent AEL vs exposure duration (energy / t), for the window check
    def ael_P(t):
        if t <= 0.35:
            return 1e4 * math.pi * 0.5e-3 ** 2 / t
        if t < 10:
            return 1e4 * math.pi * (0.75e-3 * t ** 0.375) ** 2 / t
        return AEL
    out["ael_P"] = {str(t): ael_P(t) for t in (0.01, 0.1, 0.35, 1, 3, 10, 100)}
    print("B9 power-equivalent AEL(t): " + ", ".join(f"{t} s {ael_P(t) * 1e3:.1f} mW" for t in (0.01, 0.1, 0.35, 1, 3, 10, 100)))
    # I_unit (own model)
    Iu = {K: hold_I(1e-6, 0.1, K=K)["I"] / 0.1 for K in (0.75, 0.956, 1.17)}
    Iu_real = hold_I(1e-6, 0.1, j1A=0.40, A=0.60)["I"] / 0.1           # best 100-150 nm homogeneous skin (sec phys)
    out["I_unit"] = dict(K=Iu, realistic_skin=Iu_real)
    hs_t7 = 7.1
    for w in (15e-6, 20e-6, 35e-6, 50e-6, 70e-6):
        v = 2 * AEL / (math.pi * w * w * hs_t7 * Iu[0.956])
        vr = 2 * AEL / (math.pi * w * w * hs_t7 * Iu_real)
        out["bound"][f"{w * 1e6:.0f}"] = dict(v_t7conv=v, v_realistic_mote=vr,
                                              v_range_K=[2 * AEL / (math.pi * w * w * hs_t7 * Iu[K]) for K in (0.75, 1.17)])
        print(f"B9 w {w * 1e6:3.0f} um, h s 7.1: v_max {v * 100:5.1f} cm/s (K 0.75-1.17: {out['bound'][f'{w * 1e6:.0f}']['v_range_K'][0] * 100:.1f}-"
              f"{out['bound'][f'{w * 1e6:.0f}']['v_range_K'][1] * 100:.1f}); realistic skin (A 0.6, J1/A 0.40): {vr * 100:5.1f} cm/s")
    # mode invariant: v_max x (pixels per head) = const
    c_inv = 2 * AEL * math.pi / (hs_t7 * Iu[0.956] * (2 * 1.2 * 1.5 * math.sqrt(1.2)) ** 2)
    out["v_per_mode_per_head"] = c_inv
    print(f"B9 invariant: v_max = {c_inv:.2e} m/s per hologram pixel per head (T7 conventions) -> 1 m/s needs "
          f"{1 / c_inv:.2e} px/head (w {math.sqrt(2 * AEL / (math.pi * hs_t7 * Iu[0.956] * 1.0)) * 1e6:.1f} um); with the real H10 "
          f"field (x2.2) {2.2 / c_inv:.1e}")
    # --- stacking: validate own exposure code against m17's model, then LP-weighted and aligned content
    rng = np.random.default_rng(5)
    w = 50e-6
    sk = strokes_rt7(5.0, 3e-3, rng)
    pr = np.vstack([sk[rng.choice(len(sk), 300 if quick else 800, replace=False)],
                    CENTER + (rng.random((200, 3)) * 2 - 1) * (HALF + 0.3)])
    E_rand = stacking_case(sk, w, pr, rng=rng, random_heads=True)
    out["stacking"]["sketch_random_heads_equal_split"] = float(E_rand.max())
    try:
        import m17_exposure_field as m17                              # CROSS-CHECK ONLY
        d17 = m17.run(P_focus=1e-3, r_c=w, S=5.0, n_probe=2000)
        out["stacking"]["xcheck_m17_sketch"] = d17["stacking_factor"]
        print(f"B9 stacking cross-check, sketch, w 50 um, 3 random heads, equal split: RT7 {E_rand.max():.2f} vs m17 "
              f"{d17['stacking_factor']:.2f} (m17 uses 14 heads)")
    except Exception as ex:  # pragma: no cover
        print("B9 m17 cross-check failed:", ex)
    Cm, hw = mean_c(sk)
    E_lp = stacking_case(sk, w, pr, weights=Cm)
    out["stacking"]["sketch_LP_mean"] = float(E_lp.max())
    out["stacking"]["h_mean_over_dirs"] = float(Cm.sum(axis=1).mean())
    out["stacking"]["h_worst_mean"] = float(hw.mean())
    print(f"B9 sketch (random arcs, {len(sk)} motes), LP-weighted mean exposure: worst pupil {E_lp.max():.2f} P_unit "
          f"(T7 assumes h_worst x s = 7.1); mean LP cost over directions {Cm.sum(axis=1).mean():.2f}, worst {hw.mean():.2f}")
    # aligned content: a vertical line under the ceiling head (on axis, and 1/3 cm off), a line aimed at a corner head
    cases = {}
    zs = np.arange(CENTER[2] - HALF[2], CENTER[2] + HALF[2], 3e-3)
    for name, off in (("vertical_on_axis", 0.0), ("vertical_1cm_off", 0.01), ("vertical_3cm_off", 0.03)):
        line = np.stack([np.full(zs.size, 3.0 + off), np.full(zs.size, 2.5), zs], 1)
        cases[name] = line
    hdir = (CENTER - H10[0]) / np.linalg.norm(CENTER - H10[0])
    ts = np.arange(-0.45, 0.45, 3e-3)
    cases["aimed_at_corner_head"] = CENTER + ts[:, None] * hdir[None, :]
    for name, line in cases.items():
        Cl, hwl = mean_c(line)
        # probes: along the line and its extension 0.3 m towards both ends
        ext = np.linspace(-0.3, 0.3, 61)
        d = line[-1] - line[0]
        d /= np.linalg.norm(d)
        probes = np.vstack([line[::3], line[0] - ext[ext > 0][:, None] * d, line[-1] + ext[ext > 0][:, None] * d])
        E = stacking_case(line, w, probes, weights=Cl)
        cases_out = dict(worst=float(E.max()), n_motes=len(line), h_mean=float(Cl.sum(axis=1).mean()))
        out["stacking"][name] = cases_out
        print(f"B9 aligned content '{name}' ({len(line)} motes): worst pupil {E.max():.1f} P_unit (x{E.max() / 7.1:.1f} T7's 7.1)")
    # same for w 25 and 70 um (Rayleigh range scales w^2)
    for ww in (25e-6, 70e-6):
        line = cases["vertical_on_axis"]
        Cl, _ = mean_c(line)
        E = stacking_case(line, ww, line[::3], weights=Cl)
        out["stacking"][f"vertical_on_axis_w{ww * 1e6:.0f}"] = float(E.max())
        print(f"B9 vertical on-axis line at w {ww * 1e6:.0f} um: worst pupil {E.max():.1f} P_unit")
    # --- window averages of the per-focus power (proportional to |u| in still air, U + u_l in a mean wind)
    for (sig, L11, U, Uc) in ((0.03, 0.03, 0.0, 0.03), (0.03, 0.10, 0.0, 0.03), (0.03, 0.03, 0.10, 0.10)):
        rr = np.random.default_rng(zlib.crc32(f"{sig}{L11}{U}".encode()))
        fs = 50.0
        dur = 400.0 if quick else 2000.0
        u = gen_drafts(40, dur, fs, sig, L11, U, Uc, rr).astype(float)
        sp = np.linalg.norm(u, axis=1)                                # |u|, per mote
        mean = sp.mean()
        res = {}
        worst = 0.0
        for T in (0.35, 1.0, 3.0, 10.0, 30.0):
            k = int(T * fs)
            cs = np.cumsum(np.pad(sp, ((0, 0), (1, 0))), axis=1)
            rm = (cs[:, k:] - cs[:, :-k]) / k / mean
            p999 = float(np.percentile(rm, 99.9))
            res[str(T)] = dict(p99=float(np.percentile(rm, 99)), p999=p999, max=float(rm.max()),
                               ratio_to_AEL=p999 * AEL / ael_P(T))
            worst = max(worst, p999 * AEL / ael_P(T))
        key = f"sig{sig}_L{L11}_U{U}"
        out["windows"][key] = dict(mean_speed=mean, by_T=res, design_derate=worst)
        print(f"B9 window check {key}: mean |u| {mean:.3f} m/s; running-mean p99.9 / mean: " +
              ", ".join(f"{T}s {v['p999']:.2f}" for T, v in res.items()) +
              f" -> worst window / AEL(t) at a mean set to the 10 mW AEL: {worst:.2f}")
    dump("b9", out)
    return out


# ======================================================================================================================
# Section loop: own PID tuner (closed-loop eigenvalues + modulus margin) and own vectorised 3D pinning simulator
# ======================================================================================================================
MODS = {"MEMS 10 kHz": (10000.0, 20e-6), "MEMS 5 kHz": (5000.0, 30e-6), "MEMS 3 kHz": (3000.0, 50e-6),
        "PLM 1.44 kHz": (1440.0, 100e-6)}
ROOMS_RT7 = {"still": (0.03, 0.03, 0.0, 0.03), "home": (0.03, 0.03, 0.05, 0.05), "quiet_office": (0.03, 0.03, 0.10, 0.10)}


def plant_d(T, tau):
    e = math.exp(-T / tau)
    Ad = np.array([[1.0, tau * (1 - e)], [0.0, e]])
    Bd = np.array([T - tau * (1 - e), 1 - e])
    return Ad, Bd


def meas_weights(meas, lat):
    """Weights on (x_k, x_{k-1}, ...) of the measurement used at frame k. 'inst': x_{k-lat} (m18c convention);
    'avg': exposure-averaged frame ending lat frames before the command frame: (x_{k-lat} + x_{k-lat-1}) / 2."""
    wv = np.zeros(lat + 2)
    if meas == "inst":
        wv[lat] = 1.0
    else:
        wv[lat] = wv[lat + 1] = 0.5
    return wv


def closed_loop_matrix(T, tau, K, wv):
    """Noise-free per-axis closed loop: state [x, F, x_{k-1}..x_{k-n}, I, e_prev]."""
    Kp, Ki, Kd = K
    Ad, Bd = plant_d(T, tau)
    nb = len(wv) - 1
    n = 2 + nb + 2
    A = np.zeros((n, n))
    # y = sum wv_j x_{k-j}; e = -y ; cmd = Kp e + Ki T I + Kd (e - e_prev)/T
    ycoef = np.zeros(n)
    ycoef[0] = wv[0]
    for j in range(1, nb + 1):
        ycoef[2 + j - 1] = wv[j]
    ecoef = -ycoef
    cmd = (Kp + Kd / T) * ecoef
    cmd[2 + nb] += Ki * T
    cmd[3 + nb] += -Kd / T
    A[0, :] = cmd * Bd[0]
    A[0, 0] += Ad[0, 0]
    A[0, 1] += Ad[0, 1]
    A[1, :] = cmd * Bd[1]
    A[1, 1] += Ad[1, 1]
    if nb >= 1:
        A[2, 0] = 1.0
        for j in range(1, nb):
            A[2 + j, 2 + j - 1] = 1.0
    A[2 + nb, :] = ecoef
    A[2 + nb, 2 + nb] += 1.0
    A[3 + nb, :] = ecoef
    return A


def loop_metrics(T, tau, K, wv, S_turb, f, sig_n, n_th=3000):
    Kp, Ki, Kd = K
    Ad, Bd = plant_d(T, tau)
    th = np.linspace(1e-4, math.pi, n_th)
    z = np.exp(1j * th)

    def G(zz, B):
        out = []
        for z_ in zz:
            M = np.linalg.solve(z_ * np.eye(2) - Ad, B)
            out.append(M[0])
        return np.array(out)
    Gp = G(z, Bd)
    H = sum(wv[j] * z ** (-j) for j in range(len(wv)))
    C = Kp + Ki * T / (z - 1) + Kd * (1 - 1 / z) / T
    L = C * H * Gp
    S = 1 / (1 + L)
    Ms = float(np.abs(S).max())
    var_n = sig_n ** 2 * np.trapezoid(np.abs(C * Gp * S) ** 2, th) / math.pi
    zt = np.exp(1j * 2 * math.pi * f * T)
    Gu = G(zt, np.array([T, 0.0]))
    Gpt = G(zt, Bd)
    Ht = sum(wv[j] * zt ** (-j) for j in range(len(wv)))
    Ct = Kp + Ki * T / (zt - 1) + Kd * (1 - 1 / zt) / T
    var_t = np.trapezoid(np.abs(Gu / (1 + Ct * Ht * Gpt)) ** 2 * S_turb, f)
    i_c = int(np.argmax(np.abs(L) < 1))
    return math.sqrt(var_t), math.sqrt(var_n), Ms, float(th[i_c] / (2 * math.pi * T))


def tune_rt7(T, tau, wv, sigma, L11, Uc, sig_n, Ms_max=2.0, stiff=False):
    f = np.logspace(-2, math.log10(0.45 / T), 300)
    S11, _, _ = spectra_1d(sigma, L11, Uc, f)
    lat_eff = float(np.sum(wv * np.arange(len(wv)))) + 0.5
    wref = 1 / (lat_eff * T + tau)
    best = None
    for kp in wref * np.array([0.15, 0.25, 0.35, 0.5, 0.7, 0.9, 1.2]):
        for ti in (2.0, 4.0, 8.0, 16.0):
            for td in (0.0, 0.1, 0.25, 0.5):
                K = (kp, kp * wref / ti, kp * td / wref)
                if np.max(np.abs(np.linalg.eigvals(closed_loop_matrix(T, tau, K, wv)))) >= 1 - 1e-9:
                    continue
                st, sn, Ms, fc = loop_metrics(T, tau, K, wv, S11, f, sig_n, n_th=1500)
                if Ms > Ms_max:
                    continue
                tot = math.hypot(st, sn)
                score = -fc if stiff else tot                   # stiff: highest crossover at Ms <= 2
                if best is None or score < best[6]:
                    best = (tot, K, st, sn, Ms, fc, score)
    return best


def simulate_rt7(mod, room, w, n_motes=200, dur=60.0, seed=1, sig_n=4e-6, meas="inst", lat=2, follow=False,
                 lateral=True, gain_sched=True, k_auth=1.0, mean_wind=True, a=1e-6, t_warm=0.3, fs_t=500.0,
                 r_def=100e-6, verbose=False, stiff=False):
    f_fr, tau_m = MODS[mod]
    sigma, L11, U, Uc = ROOMS_RT7[room]
    if not mean_wind:
        U = 0.0
    T = 1 / f_fr
    tau = tau_m + 1e-6                                           # modulator lag + l=1 thermal lag (~1 us at 1 um)
    wv = meas_weights(meas, lat)
    best = tune_rt7(T, tau, wv, sigma, L11, Uc, sig_n, stiff=stiff)
    K = best[1]
    Kp, Ki, Kd = K
    rng = np.random.default_rng(seed)
    homes = CENTER + (rng.random((n_motes, 3)) * 2 - 1) * HALF
    al = Alloc(homes)
    D = rng.normal(size=(400, 3))
    D /= np.linalg.norm(D, axis=1)[:, None]
    cmax = np.zeros(n_motes)
    for d_ in D:
        _, c_ = al(np.tile(d_, (n_motes, 1)))
        cmax = np.maximum(cmax, c_.max(axis=1))
    cap = k_auth * (U + 5.4 * sigma) * cmax                       # per-beam authority (speed units)
    u_all = gen_drafts(n_motes, dur + 1.0, fs_t, sigma, L11, U, Uc, rng)
    zR = math.pi * w * w / 1.55e-6
    eT = math.exp(-T / tau)
    n_fr = int(dur / T)
    nb = lat + 2
    hist = np.zeros((nb, n_motes, 3))
    x = np.zeros((n_motes, 3))
    u0 = u_all[:, :, 0].astype(float)
    F = -u0.copy()
    integ = F / (Ki * T)
    e_prev = np.zeros((n_motes, 3))
    ar = np.arange(n_motes)[:, None]
    lost = np.zeros(n_motes, bool)
    t_lost = np.full(n_motes, np.inf)
    t_w = np.full(n_motes, np.inf)                                # first |x| > w (fixed) / offset > w (follow)
    t_def = np.full(n_motes, np.inf)                              # first |x| > r_def (image defect)
    rs, sat = [], 0
    for k in range(n_fr):
        t = k * T
        it = (t + 0.5 * T) * fs_t
        i0 = int(it)
        fr_ = it - i0
        u = u_all[:, :, i0] * (1 - fr_) + u_all[:, :, i0 + 1] * fr_
        y = np.tensordot(wv, hist[:len(wv)], axes=(0, 0)) + sig_n * rng.standard_normal((n_motes, 3))
        e = -y
        f_des = Kp * e + Ki * T * integ + Kd * (e - e_prev) / T
        e_prev = e
        idx, c = al(f_des)
        Kb = al.K[ar, idx]                                        # (n, 3 beams, 3)
        centre = y if follow else 0.0
        if gain_sched and not follow:
            dm = y
            pm = np.einsum("njk,nk->nj", Kb, dm)
            r2m = np.sum(dm * dm, axis=1)[:, None] - pm * pm
            g_hat = np.maximum(np.exp(-2 * r2m / (w * w)), 0.05)
        else:
            g_hat = 1.0
        amp = c / g_hat
        sc = np.maximum(amp.max(axis=1) / cap, 1.0)
        amp = amp / sc[:, None]
        unsat = sc <= 1.0
        sat += int(np.sum(~unsat & ~lost))
        integ += np.where(unsat[:, None], e, 0.0)
        dx = x - centre
        pz = np.einsum("njk,nk->nj", Kb, dx)                      # axial offsets
        rho_v = dx[:, None, :] - pz[:, :, None] * Kb              # perpendicular offset vectors (n, 3, 3)
        r2 = np.sum(rho_v * rho_v, axis=2)
        w2z = w * w * (1 + (pz / zR) ** 2)
        g = (w * w / w2z) * np.exp(-2 * r2 / w2z)
        dirs = Kb + (1.5 * a * rho_v / w2z[:, :, None] if lateral else 0.0)
        Fc = np.einsum("nj,njk->nk", amp * g, dirs)
        x = x + u * T + Fc * T + (F - Fc) * tau * (1 - eT)
        F = Fc + (F - Fc) * eT
        hist = np.roll(hist, 1, axis=0)
        hist[0] = x
        if t > t_warm:
            r = np.linalg.norm(x, axis=1)
            off = np.linalg.norm(x - (y if follow else 0.0), axis=1)
            crit = off if follow else r
            newly = (crit > 1.5 * w) | (r > 1e-3)
            newly &= ~lost
            t_lost[newly] = t
            lost |= newly
            t_w[(crit > w) & ~np.isfinite(t_w)] = t
            t_def[(r > r_def) & ~np.isfinite(t_def)] = t
            if k % 25 == 0:
                rs.append(r[~lost])
    R = np.concatenate(rs) if rs else np.array([np.nan])
    T_eff = float(np.sum(np.minimum(t_lost, dur) - t_warm))
    nl = int(lost.sum())
    lo = stats.chi2.ppf(0.025, 2 * nl) / 2 / T_eff if nl else 0.0
    hi = (stats.chi2.ppf(0.975, 2 * nl + 2) / 2 if nl else -math.log(0.05)) / T_eff
    n_w = int(np.isfinite(t_w).sum())
    n_def = int(np.isfinite(t_def).sum())
    return dict(mod=mod, room=room, w_um=w * 1e6, n_motes=n_motes, dur=dur, meas=meas, lat=lat, follow=follow,
                lateral=lateral, mean_wind=mean_wind, stiff=stiff, U=U, sig_n_um=sig_n * 1e6, K=list(K), f_c_Hz=best[5], Ms=best[4],
                sigma_lin_um=best[0] * 1e6, lost=nl, mote_s=T_eff, rate=nl / T_eff, rate_ci95=[lo, hi],
                n_exceed_w=n_w, n_defect_100um=n_def, r_p50_um=float(np.nanpercentile(R, 50) * 1e6),
                r_p999_um=float(np.nanpercentile(R, 99.9) * 1e6), sat_frac=sat / (n_fr * n_motes))


def fmt_loop(r):
    return (f"{r['mod']:12s} {r['room']:12s} w {r['w_um']:3.0f} {'follow' if r['follow'] else 'fixed '} {r['meas']}{r['lat']}"
            f"{' stiff' if r.get('stiff') else ''} "
            f"lat{'+' if r['lateral'] else '-'} U {r['U']:.2f} noise {r['sig_n_um']:.0f}: f_c {r['f_c_Hz']:5.0f} Hz, lost "
            f"{r['lost']}/{r['n_motes']} in {r['mote_s']:.0f} mote-s, rate {r['rate']:.1e}/s [95% {r['rate_ci95'][0]:.1e}, "
            f"{r['rate_ci95'][1]:.1e}], >w {r['n_exceed_w']}, >100um {r['n_defect_100um']}, r_p50 {r['r_p50_um']:.1f} "
            f"r_p99.9 {r['r_p999_um']:.1f} um, sat {r['sat_frac']:.1e}")


LOOP_RUNS = {
    # name: kwargs
    "A_mems5_w50_still_m18cconv": dict(mod="MEMS 5 kHz", room="still", w=50e-6, lateral=False),
    "B_mems5_w50_still": dict(mod="MEMS 5 kHz", room="still", w=50e-6),
    "C_mems5_w50_still_lat3": dict(mod="MEMS 5 kHz", room="still", w=50e-6, meas="avg", lat=2),
    "D_mems5_w50_home_meanwind": dict(mod="MEMS 5 kHz", room="home", w=50e-6),
    "E_mems5_w50_qoffice_meanwind": dict(mod="MEMS 5 kHz", room="quiet_office", w=50e-6),
    "E0_mems5_w50_qoffice_nomean": dict(mod="MEMS 5 kHz", room="quiet_office", w=50e-6, mean_wind=False),
    "Es_mems5_w50_qoffice_meanwind_stiff": dict(mod="MEMS 5 kHz", room="quiet_office", w=50e-6, stiff=True),
    "Ds_mems5_w50_home_meanwind_stiff": dict(mod="MEMS 5 kHz", room="home", w=50e-6, stiff=True),
    "F_plm1f_w70_still": dict(mod="PLM 1.44 kHz", room="still", w=70e-6, lat=1),
    "G_plm1f_w70_qoffice_meanwind": dict(mod="PLM 1.44 kHz", room="quiet_office", w=70e-6, lat=1),
    "H_follow_mems3_w35_still": dict(mod="MEMS 3 kHz", room="still", w=35e-6, follow=True),
    "I_follow_mems3_w35_qoffice_meanwind": dict(mod="MEMS 3 kHz", room="quiet_office", w=35e-6, follow=True),
    "J_follow_plm1f_w50_qoffice_meanwind": dict(mod="PLM 1.44 kHz", room="quiet_office", w=50e-6, lat=1, follow=True),
    "K_mems5_w50_still_noise8": dict(mod="MEMS 5 kHz", room="still", w=50e-6, sig_n=8e-6),
    "L_mems10_w40_home_meanwind": dict(mod="MEMS 10 kHz", room="home", w=40e-6),
    "M_mems10_w35_still": dict(mod="MEMS 10 kHz", room="still", w=35e-6),
}


def sec_loop(names=None, n_motes=200, dur=60.0):
    out = {}
    dev, err = lp_check()
    print(f"LOOP LP allocation vs scipy linprog: max |cost diff| {dev:.1e}, max force error {err:.1e}")
    # tuner cross-check against rt6.tune on the m18c MEMS 5 kHz case (d = 2, tau 30 us, 4 um noise)
    b = tune_rt7(1 / 5000, 31e-6, meas_weights("inst", 2), 0.03, 0.03, 0.03, 4e-6)
    out["tuner"] = dict(K=list(b[1]), sigma_lin_um=b[0] * 1e6, f_c=b[5], Ms=b[4])
    try:
        import rt6_check as rt6                                       # CROSS-CHECK ONLY
        tp, tfm = rt6.mote_times(1e-6, 150.0, 800.0, 0.04)
        fturb, Sturb, eta, nu0 = rt6.turb_norm(0.03, 0.03, 0.03)
        sel = (fturb > 1e-3) & (fturb < 0.45 * 5000)
        r6 = rt6.tune(tp, 30e-6 + tfm, 1 / 5000, 2, fturb[sel][::4], Sturb[sel][::4], 4e-6, 0.0)
        out["tuner"]["rt6"] = dict(K=list(r6[1]), sigma_um=r6[0] * 1e6, Ms=r6[5])
        print(f"LOOP tuner MEMS 5 kHz d2: RT7 K {np.round(b[1], 1)}, sigma {b[0] * 1e6:.2f} um, f_c {b[5]:.0f} Hz, Ms {b[4]:.2f}; "
              f"rt6.tune K {np.round(r6[1], 1)}, sigma {r6[0] * 1e6:.2f} um, Ms {r6[5]:.2f}")
    except Exception as ex:  # pragma: no cover
        print("LOOP rt6 tuner cross-check failed:", ex)
    for name, kw in LOOP_RUNS.items():
        if names and name not in names:
            continue
        t0 = time.time()
        kw = dict(kw)
        kw.setdefault("n_motes", n_motes)
        kw.setdefault("dur", dur)
        kw.setdefault("seed", zlib.crc32(name.encode()) % 100000)
        r = simulate_rt7(**kw)
        out[name] = r
        print(f"LOOP {name}: " + fmt_loop(r) + f"  ({time.time() - t0:.0f} s)", flush=True)
        dump("loop" + ("_" + "_".join(names) if names else ""), out)
    return out


# ======================================================================================================================
# Section i9: slow hologram + fast amplitude stack in a demagnified intermediate volume
# ======================================================================================================================
def gauss_pixel_frac(cx, cy, wf, px0, py0, p):
    """Fraction of a 2D Gaussian (1/e^2 radius wf, centre cx, cy) inside the square pixel [px0, px0+p] x [py0, py0+p]."""
    s2 = wf / math.sqrt(2)                          # 1/e^2 radius w -> sigma = w/2; erf argument (x - c)/(sqrt2 sigma)
    fx = 0.5 * (special.erf((px0 + p - cx) / s2) - special.erf((px0 - cx) / s2))
    fy = 0.5 * (special.erf((py0 + p - cy) / s2) - special.erf((py0 - cy) / s2))
    return fx * fy


def i9_crosstalk(P, head, n_layers=4, p=1e-3, w0=50e-6, own_frac=0.98, lam=1.55e-6):
    """Per head: conjugate planes perpendicular to the head axis, equally spaced over the depth the content spans.
    Each mote is modulated at its own (nearest) layer by the pixels that hold >= (1-own_frac) of its beam there.
    Crosstalk of mote j = fraction of its beam passing, at any layer, through pixels owned by other motes.
    Conflict = a mote's own pixels are also owned by another mote."""
    h = np.asarray(head, float)
    ax = (CENTER - h) / np.linalg.norm(CENTER - h)
    e1 = np.cross(ax, [0, 0, 1.0]) if abs(ax[2]) < 0.9 else np.cross(ax, [1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    rel = P - h
    dep = rel @ ax
    lo, hi = dep.min(), dep.max()
    planes = lo + (np.arange(n_layers) + 0.5) * (hi - lo) / n_layers
    own = np.argmin(np.abs(dep[:, None] - planes[None, :]), axis=1)
    zR = math.pi * w0 * w0 / lam
    u = rel / np.linalg.norm(rel, axis=1)[:, None]
    # crossing of beam j with plane l: point h + t u, with (t u).ax = planes[l]
    cosb = u @ ax
    owner = [dict() for _ in range(n_layers)]
    foot = {}
    for j in range(len(P)):
        for l in range(n_layers):
            t = planes[l] / cosb[j]
            q = t * u[j]
            cx, cy = q @ e1, q @ e2
            zf = t - np.linalg.norm(rel[j])                      # distance from the focus along the beam
            wf = w0 * math.sqrt(1 + (zf / zR) ** 2) / max(cosb[j], 0.3)
            foot[(j, l)] = (cx, cy, wf)
        cx, cy, wf = foot[(j, own[j])]
        r = 2.0 * wf + p
        ix = np.arange(math.floor((cx - r) / p), math.floor((cx + r) / p) + 1)
        iy = np.arange(math.floor((cy - r) / p), math.floor((cy + r) / p) + 1)
        for a_ in ix:
            for b_ in iy:
                fr = gauss_pixel_frac(cx, cy, wf, a_ * p, b_ * p, p)
                if fr > (1 - own_frac) / 4:
                    owner[own[j]].setdefault((a_, b_), []).append(j)
    xt = np.zeros(len(P))
    conflict = np.zeros(len(P), bool)
    for j in range(len(P)):
        for l in range(n_layers):
            cx, cy, wf = foot[(j, l)]
            r = 2.0 * wf + p
            ix = np.arange(math.floor((cx - r) / p), math.floor((cx + r) / p) + 1)
            iy = np.arange(math.floor((cy - r) / p), math.floor((cy + r) / p) + 1)
            for a_ in ix:
                for b_ in iy:
                    ow = owner[l].get((a_, b_))
                    if not ow:
                        continue
                    others = [o for o in ow if o != j]
                    if not others:
                        continue
                    fr = gauss_pixel_frac(cx, cy, wf, a_ * p, b_ * p, p)
                    xt[j] += fr
                    if l == own[j] and j in ow:
                        conflict[j] = True
    return dict(depth_span=float(hi - lo), xt_median=float(np.median(xt)), xt_mean=float(xt.mean()),
                xt_p90=float(np.percentile(xt, 90)), xt_p99=float(np.percentile(xt, 99)),
                frac_xt_gt_1pct=float(np.mean(xt > 0.01)), frac_xt_gt_10pct=float(np.mean(xt > 0.10)),
                frac_conflict=float(conflict.mean()), n=len(P))


def sec_i9(quick=False):
    out = dict(geometry={}, crosstalk=[])
    # geometry: relay with lateral magnification 15 at the centre throw; intermediate depth for each head's range
    for i in (0, 8, 9):
        h = H10[i]
        P = box_points()
        d = np.linalg.norm(P - h, axis=1)
        dc = np.linalg.norm(CENTER - h)
        f = dc / 16.0                                             # m = (d - f)/f = 15 at d_c
        si = 1 / (1 / f - 1 / d)
        out["geometry"][str(i)] = dict(d_min=float(d.min()), d_max=float(d.max()), room_depth=float(d.max() - d.min()),
                                       inter_depth_mm=float((si.max() - si.min()) * 1e3),
                                       m_range=[float((d.min() - f) / f), float((d.max() - f) / f)])
        g = out["geometry"][str(i)]
        print(f"I9 head {i}: room depth {g['room_depth']:.2f} m (T7: 0.8 m) -> intermediate depth {g['inter_depth_mm']:.1f} mm at "
              f"m 15 (T7: 3.6 mm); lateral magnification varies {g['m_range'][0]:.1f}-{g['m_range'][1]:.1f} over the depth")
    rng = np.random.default_rng(7)
    for S, label in ((5.0, "sketch"), (30.0, "film")):
        P = strokes_rt7(S, 3e-3, rng)
        if quick and S > 10:
            P = P[rng.choice(len(P), 3000, replace=False)]
        for hi_ in (0, 9):
            for nl in (4, 8):
                for sub in (1.0, 0.33):
                    Q = P if sub == 1.0 else P[rng.random(len(P)) < sub]
                    r = i9_crosstalk(Q, H10[hi_], n_layers=nl)
                    r.update(content=label, head=int(hi_), n_layers=nl, served_fraction=sub)
                    out["crosstalk"].append(r)
                    print(f"I9 {label:6s} head {hi_} layers {nl} served {sub:.2f} (N {r['n']}): crosstalk median "
                          f"{100 * r['xt_median']:.2f}% mean {100 * r['xt_mean']:.2f}% p90 {100 * r['xt_p90']:.1f}% p99 "
                          f"{100 * r['xt_p99']:.0f}%; motes >1% {100 * r['frac_xt_gt_1pct']:.0f}%, >10% "
                          f"{100 * r['frac_xt_gt_10pct']:.0f}%; own-pixel conflicts {100 * r['frac_conflict']:.1f}%", flush=True)
    dump("i9", out)
    return out


# ======================================================================================================================
# Section loopx: cross-check of the mean-wind omission with T7's OWN simulator (m18c), monkeypatched in memory only
# ======================================================================================================================
def sec_loopx(n_motes=30, dur=10.0):
    import rt6_check as rt6                                            # CROSS-CHECK ONLY (T7's own simulator)
    import m18b_holo_loop as m18b
    import m18c_vector_pin as m18c
    out = {}
    orig = rt6.synth_turb
    for U in (0.0, 0.10):
        def synth_mean(n_series, n, fs, u_rms, L, Uc, rng, _U=U):
            x = orig(n_series, n, fs, u_rms, L, Uc, rng).astype(float)
            nm = n_series // 3
            ph_ = np.random.default_rng(99).uniform(0, 2 * math.pi, nm)
            x[0::3] += _U * np.cos(ph_)[:, None]
            x[1::3] += _U * np.sin(ph_)[:, None]
            return x.astype(np.float32)
        rt6.synth_turb = synth_mean
        try:
            for case, w in ((m18b.CASES[5], 50e-6), (m18b.CASES[3], 70e-6)):
                draft = m18b.DRAFTS[3]                                     # quiet office: sigma 0.03, Uc 0.10
                auth = (U + 5.4 * draft[1]) / draft[1]
                t0 = time.time()
                r = m18c.simulate(case, draft, w, n_motes=n_motes, dur=dur, seed=4242, auth=auth)
                key = f"{case[0]}_w{w * 1e6:.0f}_U{U}"
                out[key] = r
                print(f"LOOPX m18c.simulate {case[0]:30s} quiet office w {w * 1e6:.0f} um, mean wind U {U:.2f} m/s, "
                      f"authority (U+5.4 sigma): lost {r['lost']}/{r['n_motes']} in {r['mote_seconds']:.0f} mote-s, "
                      f"r_p99.9 {r['r_p999_um']:.1f} um, sat {r['sat_frac']:.1e} ({time.time() - t0:.0f} s)", flush=True)
        finally:
            rt6.synth_turb = orig
    dump("loopx", out)
    return out


def sec_b9fix():
    """Stacking-aware allocation: drop, per mote, every head whose line of sight is within 2 deg of the stroke direction
    (both senses), then redo the LP. Reports the worst-pupil exposure and the LP cost penalty."""
    out = {}
    w = 50e-6
    zs = np.arange(CENTER[2] - HALF[2], CENTER[2] + HALF[2], 3e-3)
    hdir = (CENTER - H10[0]) / np.linalg.norm(CENTER - H10[0])
    ts = np.arange(-0.45, 0.45, 3e-3)
    lines = {"vertical_on_axis": (np.stack([np.full(zs.size, 3.0), np.full(zs.size, 2.5), zs], 1), np.array([0, 0, 1.0])),
             "aimed_at_corner_head": (CENTER + ts[:, None] * hdir[None, :], hdir)}
    rng = np.random.default_rng(3)
    D = rng.normal(size=(3000, 3))
    D /= np.linalg.norm(D, axis=1)[:, None]
    for name, (line, sd) in lines.items():
        keep = []
        for hj in H10:
            v = CENTER - hj
            v /= np.linalg.norm(v)
            keep.append(abs(v @ sd) < math.cos(math.radians(2.0)))
        keep = np.array(keep)
        heads = H10[keep]
        al = Alloc(line, heads=heads)
        C = np.zeros((len(line), len(heads)))
        hw = np.zeros(len(line))
        for d in D:
            idx, c = al(np.tile(d, (len(line), 1)))
            np.add.at(C, (np.repeat(np.arange(len(line)), 3), idx.ravel()), c.ravel())
            hw = np.maximum(hw, c.sum(axis=1))
        C /= len(D)
        Cfull = np.zeros((len(line), 10))
        Cfull[:, keep] = C
        ext = np.linspace(0.01, 0.3, 30)
        probes = np.vstack([line[::3], line[0] - ext[:, None] * sd, line[-1] + ext[:, None] * sd])
        E = stacking_case(line, w, probes, weights=Cfull)
        out[name] = dict(heads_dropped=int((~keep).sum()), worst=float(E.max()), h_mean=float(C.sum(axis=1).mean()),
                         h_worst=float(hw.max()))
        print(f"B9FIX {name}: drop {int((~keep).sum())} co-axial head(s) -> worst pupil {E.max():.1f} P_unit, LP cost mean "
              f"{C.sum(axis=1).mean():.2f}, worst {hw.max():.2f} (all heads: worst ~1.7-2.1)")
    dump("b9fix", out)
    return out


if __name__ == "__main__":
    secs = sys.argv[1:] or ["all"]
    t0 = time.time()
    table = {"phys": sec_phys, "mie": sec_mie, "vis": sec_vis, "modes": sec_modes, "b9": sec_b9, "loop": sec_loop, "i9": sec_i9, "loopx": sec_loopx, "b9fix": sec_b9fix}
    for s in secs:
        if s == "all":
            for f in table.values():
                f()
        else:
            table[s]()
    print(f"[rt7 sections {secs} done in {time.time() - t0:.0f} s]")

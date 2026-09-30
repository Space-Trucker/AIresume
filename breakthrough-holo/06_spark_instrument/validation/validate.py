"""SPARK validation suite: 20 registered tests (implementation V01-V16, physics V17-V20).

Usage: python3 validate.py        (fast tests run live; slow physics runs are read from ../results/*.json)
Writes ../results/validation.json and prints PASS / FAIL / PENDING per test.
Implementation tests prove the code implements the model. Physics tests compare with published
measurements (sources in VALIDATION_DATA.md). A result may claim only what its weakest relevant test supports.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")

from eos import fast, IdealEOS, P0, cantera_state, saha_state  # noqa: E402
from hydro import Spark                                           # noqa: E402
from exact_riemann import sod_exact                               # noqa: E402
import chemistry as ch                                            # noqa: E402

tests = []


def record(tid, name, kind, value, criterion, ok, source):
    status = "PENDING" if ok is None else ("PASS" if ok else "FAIL")
    tests.append(dict(id=tid, name=name, kind=kind, value=value, criterion=criterion, status=status, source=source))
    print(f"  [{status:7s}] {tid} {name}: {value}  (criterion: {criterion})")


def load_json(name):
    p = os.path.join(RES, name)
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    print("SPARK validation suite")
    eos = fast()
    rho0 = eos.rho0
    # V01
    P = float(eos.P(np.array([rho0]), eos.e_of(np.array([rho0]), np.array([300.0])))[0])
    record("V01", "EOS ambient pressure", "impl", f"{P:.1f} Pa", "101325 +-0.2 %", abs(P / P0 - 1) < 0.002, "definition")
    # V02
    import cantera as ct
    gas = ct.Solution("airNASA9.yaml")
    gas.X = {"N2": 0.79, "O2": 0.21}
    worst = 0.0
    for rho in (0.01, 0.1, 1.2, 10.0):
        c, s = cantera_state(gas, 16000.0, rho), saha_state(16000.0, rho)
        worst = max(worst, abs(c["P"] / s["P"] - 1), abs(c["ne"] / s["ne"] - 1))
    record("V02", "Cantera vs own Saha solver at 16 kK (P, n_e)", "impl", f"max dev {worst*100:.2f} %", "< 3 %",
           worst < 0.03, "independent implementations")
    # V03
    rho = np.array([1.17, 0.05, 0.01, 5.0, 0.3])
    T = np.array([2000.0, 5000.0, 15000.0, 3000.0, 60000.0])
    rt = float(np.max(np.abs(eos.T(rho, eos.e_of(rho, T)) / T - 1)))
    record("V03", "EOS inversion round trip", "impl", f"{rt*100:.3f} %", "< 0.1 %", rt < 1e-3, "self-consistency")
    # V04 isobaric table vs direct Cantera equilibrium at 1 atm
    gas.TP = 10000.0, P0
    gas.equilibrate("TP")
    d = abs(float(eos.iso_rho(np.array([10000.0]))[0]) / gas.density - 1)
    record("V04", "isobaric density table vs Cantera at 10 kK, 1 atm", "impl", f"{d*100:.2f} %", "< 2 %",
           d < 0.02, "Cantera airNASA9 (NASA CEA data)")
    # V05, V07a Sod
    g = 1.4
    ieos = IdealEOS(g, R=1.0, rho0=1.0)
    N = 400
    r = np.linspace(0, 1, N + 1)
    xc = 0.5 * (r[1:] + r[:-1])
    rh = np.where(xc < 0.5, 1.0, 0.125)
    Pp = np.where(xc < 0.5, 1.0, 0.1)
    s = Spark.from_arrays(ieos, r, rh, Pp / ((g - 1) * rh), "planar", P_ext=0.1)
    E0 = s.total_energy()
    while s.t < 0.2:
        s.step_compressible()
    xc = 0.5 * (s.r[1:] + s.r[:-1])
    L1 = float(np.mean(np.abs(s.m / np.diff(s.r) - sod_exact(xc, s.t))) / np.mean(sod_exact(xc, s.t)))
    record("V05", "Sod shock tube vs exact Riemann solution", "impl", f"L1 {L1*100:.2f} %", "< 1 %", L1 < 0.01, "Toro ch. 4")
    dS = abs((s.total_energy() + s.W_out - E0) / E0)
    # V06, V07b Sedov
    Nc = 600
    r = np.linspace(0, 1.0, Nc + 1)
    V = 4 / 3 * math.pi * (r[1:] ** 3 - r[:-1] ** 3)
    e = np.full(Nc, 1e-6)
    e[:3] += 1.0 / V[:3].sum()
    s = Spark.from_arrays(ieos, r, np.ones(Nc), e, "spherical")
    E0 = s.total_energy()
    xs = []
    while s.t < 0.08:
        s.step_compressible()
        if s.step % 20 == 0 and s.t > 0.01:
            rr = s.m / s._vol(s.r)
            j = int(np.argmax(rr))
            xs.append(0.5 * (s.r[j] + s.r[j + 1]) / s.t ** 0.4)
    xi = float(np.mean(xs))
    record("V06", "Sedov-Taylor constant xi0 (gamma 1.4)", "impl", f"{xi:.4f}", "1.0328 +- 3 % (prediction P1)",
           abs(xi / 1.0328 - 1) < 0.03, "Sedov 1959; Diaz & Rigby 2022")
    dSe = abs((s.total_energy() + s.W_out - E0) / E0)
    record("V07", "energy conservation (Sod / Sedov)", "impl", f"{dS:.1e} / {dSe:.1e}", "< 1e-3 / < 1e-2",
           dS < 1e-3 and dSe < 1e-2, "conservation law")
    # V08 conduction operator vs analytic Gaussian diffusion
    kap, cv, rho_c = 1.0, 1000.0, 1.0
    ieos2 = IdealEOS(1.4, R=cv * 0.4, rho0=rho_c)
    Nc = 300
    r = np.linspace(0, 3e-3, Nc + 1)
    rc = 0.5 * (r[1:] + r[:-1])
    a = 2e-4
    T0 = 300 + 100 * np.exp(-(rc / a) ** 2)
    s = Spark.from_arrays(ieos2, r, np.full(Nc, rho_c), cv * T0, "spherical", kappa_fn=lambda T, m: np.full_like(T, kap))
    D = kap / (rho_c * cv)
    t_end, nsteps = 3 * a * a / (4 * D), 400        # Gaussian widens by 2x; stays far from the wall
    dt = t_end / nsteps
    for _ in range(nsteps):
        Tn = s.e / cv
        s.e = s.e + s._conduction(Tn, np.full(Nc, rho_c), dt) / s.m
    Ta = 300 + 100 * (a * a / (a * a + 4 * D * t_end)) ** 1.5 * np.exp(-rc ** 2 / (a * a + 4 * D * t_end))
    err = float(np.max(np.abs(s.e / cv - Ta)) / (Ta.max() - 300))
    record("V08", "implicit conduction vs analytic 3D diffusion", "impl", f"max err {err*100:.2f} % of peak", "< 3 %",
           err < 0.03, "Carslaw & Jaeger")
    # V09 kinetics -> equilibrium
    worst = 0.0
    for Tk in (3000.0, 4000.0, 5000.0, 6000.0):
        y = ch.integrate_history(np.array([0, 5e-3]), np.array([Tk, Tk]), np.array([P0, P0]), t_mix=1e-12)
        x = y / y.sum()
        xe = ch.equilibrium_fractions(Tk, P0)
        worst = max(worst, abs(x[ch.IDX["NO"]] / xe[ch.IDX["NO"]] - 1))
    record("V09", "kinetics relax to Cantera equilibrium NO (3-6 kK)", "impl", f"max dev {worst*100:.2f} %", "< 2 %",
           worst < 0.02, "detailed balance")
    # V10 O-atom lifetime
    n = np.zeros(7)
    nt = P0 / (1.380649e-23 * 300) * 1e-6
    n[ch.IDX["N2"]], n[ch.IDX["O2"]], n[ch.IDX["O"]] = 0.79 * nt, 0.21 * nt, 1e10
    tau = n[ch.IDX["O"]] / (-ch.rates(300.0, n)[ch.IDX["O"]])
    tau_a = 1 / (6.0e-34 * n[ch.IDX["O2"]] * nt)
    record("V10", "O-atom lifetime (O+O2+M) at 300 K", "impl", f"{tau*1e6:.2f} us vs {tau_a*1e6:.2f} us", "< 1 %",
           abs(tau / tau_a - 1) < 0.01, "JPL k0 = 6.0e-34 (T/300)^-2.4")
    # V11 photopic normalisation
    import radiation as rd  # noqa
    V_ = rd._V()
    k = int(np.argmin(np.abs(rd.LAM - 555e-9)))
    jl = np.zeros_like(rd.LAM)
    jl[k] = 1.0 / np.gradient(rd.LAM)[k]
    lm = rd.band_integrals(jl, np.zeros_like(jl), V_, rd._S())["lm"]
    record("V11", "photometry: 1 W at 555 nm", "impl", f"{lm:.1f} lm", "683 +- 1 %", abs(lm / 683 - 1) < 0.01, "CIE")
    # V12 thick-limit escape factor vs blackbody (analytic: ratio 4/3 by construction of beta)
    # numeric: uniform thick sphere (T 20 kK, rho 20 kg/m^3, R 1 m): model loss vs blackbody, 540-560 nm
    kB_, h_, c_ = 1.380649e-23, 6.62607015e-34, 299792458.0
    Tt, rt_, R = 20000.0, 20.0, 1.0
    ne_, comp_ = rd.composition(Tt, rt_, gas)
    jl_, kap_ = rd.spectrum(Tt, ne_, comp_)
    m_ = (rd.LAM > 540e-9) & (rd.LAM < 560e-9)
    dl_ = np.gradient(rd.LAM)[m_]
    tau_ = kap_[m_] * R
    beta_ = -np.expm1(-tau_) / tau_
    L_model = float((jl_[m_] * dl_ * beta_).sum()) * 4 / 3 * math.pi * R ** 3
    Bl = 2 * h_ * c_ ** 2 / rd.LAM[m_] ** 5 / np.expm1(h_ * c_ / (rd.LAM[m_] * kB_ * Tt))
    L_bb = float((math.pi * Bl * dl_).sum()) * 4 * math.pi * R * R
    ratio_ = L_model / L_bb
    record("V12", "optically thick sphere: model loss / blackbody (540-560 nm)", "impl", f"{ratio_:.3f} (tau {tau_.mean():.1e})",
           "4/3 +- 10 % (escape-factor approximation)", abs(ratio_ / (4 / 3) - 1) < 0.10, "Kirchhoff + escape factor")
    # V13-V16 from convergence runs
    cv_ = load_json("val_convergence.json")
    if cv_ and "fine_grid" in cv_ and "half_cfl" in cv_:
        ref, fg, hc = cv_["ref"], cv_["fine_grid"], cv_["half_cfl"]
        def dev(a_, b_, key):
            return abs(a_[key] / b_[key] - 1)
        g1 = max(dev(fg, ref, "eta_lm_per_W"), dev(fg, ref, "f_sedov"), dev(fg, ref, "NO_per_J"))
        g2 = max(dev(hc, ref, "eta_lm_per_W"), dev(hc, ref, "f_sedov"), dev(hc, ref, "NO_per_J"))
        record("V13", "grid convergence (eta, blast, NO) 48 vs 96 core cells", "impl", f"max dev {g1*100:.1f} %", "< 10 %", g1 < 0.10, "numerics")
        record("V14", "time-step convergence (CFL 0.3 vs 0.15)", "impl", f"max dev {g2*100:.1f} %", "< 5 %", g2 < 0.05, "numerics")
        cl = ref["closure_at_switch"]
        record("V15", "energy closure (heat + sound + light = absorbed)", "impl", f"{cl:.4f}", "0.97-1.03", 0.97 < cl < 1.03, "conservation")
        mr = ref.get("audible", {}).get("monopole_ratio_2_15kHz", float("nan"))
        record("V16", "heat-release monopole law (noise model) vs simulated waveform, 2-15 kHz", "impl",
               f"measured/predicted {mr:.2f}", "0.67-1.5", (0.67 < mr < 1.5) if mr == mr else False,
               "display_budget.heat_release_band_p2")
    else:
        for tid, nm in (("V13", "grid convergence"), ("V14", "time-step convergence"), ("V15", "energy closure"),
                        ("V16", "heat-release monopole law")):
            record(tid, nm, "impl", "run pending", "-", None, "numerics")
    # V21 NO overshoot bound (review finding 1): frozen NO from LTE start must not exceed max equilibrium x_NO
    mx = 0.0
    for tau in (1e-7, 1e-6, 1e-5, 1e-4, 1e-3):
        tt = np.linspace(0, 5 * tau, 300)
        TT = 1500 + 5500 * np.exp(-tt / tau)
        y = ch.integrate_history(tt, TT, np.full_like(tt, P0), n_init=ch._eq_init(7000.0, P0))
        mx = max(mx, y[ch.IDX["NO"]] / y.sum())
    record("V21", "frozen NO bounded by max equilibrium x_NO (5.06 %)", "impl", f"max frozen x_NO {mx:.2e}", "<= 5.06e-2",
           mx <= 5.06e-2, "LTE initial condition, detailed balance")
    # V22 Noh implosion (gamma 5/3): post-shock density 64 (review finding 13; covers shell/converging cases)
    ieos3 = IdealEOS(5 / 3, R=1.0, rho0=1.0)
    Nn = 400
    r = np.linspace(0, 1.0, Nn + 1)
    sN = Spark.from_arrays(ieos3, r, np.ones(Nn), np.full(Nn, 1e-9), "spherical", P_ext=0.0)
    sN.u[:] = -1.0
    sN.u[0] = 0.0
    while sN.t < 0.6:
        sN.step_compressible()
    rc_ = 0.5 * (sN.r[1:] + sN.r[:-1])
    rhoN = sN.m / sN._vol(sN.r)
    plateau = float(np.median(rhoN[(rc_ > 0.08) & (rc_ < 0.17)]))
    record("V22", "Noh spherical implosion post-shock density", "impl", f"{plateau:.1f}", "64 +- 15 %",
           abs(plateau / 64 - 1) < 0.15, "Noh 1987")
    # physics tests (published measurements; SPARK v2 runs with mixing model)
    runs = {k: load_json(f"val_{k}.json") for k in ("ns50mJ_r150_mix", "ns75mJ_r200_mix", "ns200mJ_r300_mix")}
    n50, n75, n200 = runs["ns50mJ_r150_mix"], runs["ns75mJ_r200_mix"], runs["ns200mJ_r300_mix"]
    if n50:
        fr = n50["f_rad_escaping_gt200nm"]
        frt = n50["f_rad"]
        record("V17", "ns spark 50 mJ radiated share (all bands / >200 nm)", "physics", f"{frt*100:.1f} % / {fr*100:.1f} %",
               "22-34 % (Phuoc 2005), x2 band 11-68 % on all-band", 0.11 <= frt <= 0.68, "Phuoc, Opt. Lasers Eng. 43, 113 (2005)")
    else:
        record("V17", "ns spark radiated share", "physics", "run pending", "-", None, "Phuoc 2005")
    if n200:
        m1 = n200["marks"].get("1e-06")
        m21 = n200["marks"].get("2.1e-05")
        ok = (m1 and 0.67 < m1["Tmax"] / 51500 < 1.5) and (m21 and 0.67 < m21["Tmax"] / 6900 < 1.5)
        record("V18", "200 mJ kernel T at 1 us / 21 us (mixing model calibrated here)", "physics",
               f"{m1['Tmax']:.0f} K / {m21['Tmax']:.0f} K", "51,500 / 6,900 K within x1.5 (Thomson)", bool(ok),
               "Zhang et al. SAB 157, 6 (2019) - CALIBRATION point for mix_tv, mix_tau")
        no = n200["NO_per_J"]
        record("V19", "ns spark NO per absorbed J", "physics", f"{no:.2e} /J", "4.6e16-1.5e17 /J, x2 band",
               2.3e16 <= no <= 3e17, "Rahman/Cooray 2003; Navarro-Gonzalez 2001")
        fv = n200["E_rad"]["vis"] / n200["E_rad_total"] if n200["E_rad_total"] > 0 else 0
        record("V20", "visible fraction of hot-spark emission", "physics", f"{fv*100:.2f} %", "0.1-10 % (da Silva 2019)",
               0.001 <= fv <= 0.10, "da Silva et al. JGR 2019")
    else:
        for tid, nm in (("V18", "kernel temperature history"), ("V19", "ns spark NO per J"), ("V20", "visible fraction")):
            record(tid, nm, "physics", "run pending", "-", None, "")
    if n75:
        m10 = n75["marks"].get("1e-05")
        record("V23", "75 mJ kernel T at 10 us (independent of calibration)", "physics", f"{m10['Tmax']:.0f} K",
               "~12,000 K within x1.5 (Dumitrache 2016)", 8000 <= m10["Tmax"] <= 18000, "Dumitrache et al. PoP 23, 093515 (2016)")
        # shock pressure when the shock is at r = 1 mm
        tr = np.array(n75.get("shock_traj", []))
        if len(tr):
            k = int(np.argmin(np.abs(tr[:, 1] - 1e-3)))
            p1 = tr[k, 2] / 1e6
            record("V24", "75 mJ shock pressure at r = 1 mm", "physics", f"{p1:.2f} MPa",
                   "0.5-15.7 MPa band for 25-140 mJ (Noor 2025)", 0.5 <= p1 <= 15.7, "Noor et al. Appl. Opt. 64, 4910 (2025)")
    else:
        record("V23", "75 mJ kernel T at 10 us", "physics", "run pending", "-", None, "Dumitrache 2016")
        record("V24", "shock pressure at 1 mm", "physics", "run pending", "-", None, "Noor 2025")
    npass = sum(t["status"] == "PASS" for t in tests)
    nfail = sum(t["status"] == "FAIL" for t in tests)
    npend = sum(t["status"] == "PENDING" for t in tests)
    print(f"  => {npass} PASS, {nfail} FAIL, {npend} PENDING of {len(tests)}")
    json.dump(dict(tests=tests, n_pass=npass, n_fail=nfail, n_pending=npend), open(os.path.join(RES, "validation.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

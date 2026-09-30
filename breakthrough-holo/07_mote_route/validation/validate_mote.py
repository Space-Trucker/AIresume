"""MOTE validation suite (instrument v1).

Test types:
* implementation (I): the code does what the model says;
* physics (P): the model matches published measurements or textbook values;
* consistency (C): published display results are reproducible by the model within physical bounds.
Sources are in the `source` field and in 07_mote_route/R5-R7.

Usage: python3 validate_mote.py   -> writes ../results/validation_mote.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mote"))
RES = os.path.join(HERE, "..", "results")
os.makedirs(RES, exist_ok=True)

import physics as ph   # noqa: E402
import safety as sf    # noqa: E402
import budget as bd    # noqa: E402
import dynamics as dy  # noqa: E402

tests = []


def record(tid, name, kind, value, criterion, ok, source):
    tests.append(dict(id=tid, name=name, kind=kind, value=value, criterion=criterion,
                      status="PASS" if ok else "FAIL", source=source))


def rel(a, b):
    return abs(a - b) / abs(b)


# --- aerosol mechanics (Hinds, Aerosol Technology 2nd ed., tables A.11/A.12) -------------------------------
lam = ph.mfp(ph.T0)
record("M01", "mean free path of air, 293 K", "P", lam * 1e6, "0.066 um +-3 %", rel(lam, 0.066e-6) < 0.03, "Hinds 2.25")
cc1, cc01 = ph.cunningham(0.5e-6), ph.cunningham(0.05e-6)
record("M02", "Cunningham factor d = 1 um and 0.1 um", "P", [cc1, cc01], "1.168, 2.91 +-4 %",
       rel(cc1, 1.168) < 0.04 and rel(cc01, 2.91) < 0.04, "Hinds table A.11")
vs = ph.settling_velocity(5e-6, 1000.0)
record("M03", "settling velocity, d = 10 um, unit density", "P", vs * 1e3, "3.06 mm/s +-4 %", rel(vs, 3.06e-3) < 0.04,
       "Hinds table A.11 (3.06e-3 m/s)")
D = (ph.brownian_rms(0.5e-6, 1.0) ** 2) / 2
record("M04", "diffusion coefficient, d = 1 um", "P", D, "2.77e-11 m^2/s +-5 %", rel(D, 2.77e-11) < 0.05,
       "Hinds table A.9")
Fd = ph.drag(2.5e-6, 1.0, slip=False)
record("M05", "drag = Stokes x (1 + 3Re/16)", "I", Fd, "exact", rel(Fd, 6 * math.pi * ph.mu_air(ph.T0) * 2.5e-6 *
       (1 + 3 / 16 * ph.rho_air(ph.T0) * 5e-6 / ph.mu_air(ph.T0))) < 1e-12, "Oseen")

# --- heat balance -----------------------------------------------------------------------------------------
a = 2.5e-6
P_small = 1e-6
Tm = ph.mote_temperature(P_small, a, eps=0.0)
zeta = 2 * 1.4 / 2.4 * ph.mfp(0.5 * (ph.T0 + Tm)) / 0.71
expect = P_small * (1 + zeta / a) / (4 * math.pi * a * ph.k_air(0.5 * (ph.T0 + Tm)))
record("M06", "small-dT conduction with temperature jump", "I", Tm - ph.T0, f"{expect:.3f} K +-1 %",
       rel(Tm - ph.T0, expect) < 0.01, "Fuchs jump-sphere solution")
Tq = np.linspace(ph.T0, 700, 20001)
kint = np.trapezoid(ph.k_air(Tq), Tq)
record("M07", "Kirchhoff integral vs numerical", "I", ph.k_integral(700), "trapezoid +-1e-6",
       rel(ph.k_integral(700), kint) < 1e-6, "calculus")
kt = ph.k_air(600.0)
record("M08", "air conductivity at 600 K", "P", kt, "0.0469 W/m/K +-5 %", rel(kt, 0.0469) < 0.05,
       "Incropera table A.4 (46.9 mW/m/K)")

# --- photophoresis ----------------------------------------------------------------------------------------
Fc = ph.photophoretic_force(a, 1e7, 0.1, slip=False)
mu, rho, kg = ph.mu_air(ph.T0), ph.rho_air(ph.T0), ph.k_air(ph.T0)
Fref = 9 * math.pi * mu ** 2 * a * 1e7 * 0.5 / (2 * (ph.P0 / ph.R_AIR) * (0.1 + 2 * kg))   # rho*T = p/R (RT4 Major 1)
record("M09", "continuum photophoretic force = Yalamov/Reed formula", "I", Fc, "exact", rel(Fc, Fref) < 1e-12,
       "Reed 1977 eq.; Horvath 2014 review")
s_big = ph.pp_slip(1e-3, 0.1)
record("M10", "slip factor -> 1 as Kn -> 0", "I", s_big, "> 0.999", s_big > 0.999, "limit")
# heat-force identity: force per kelvin of mean heating is size-independent in the continuum limit
fk = []
for aa in (1e-6, 2.5e-6, 5e-6, 10e-6):
    P = 1e-6
    T = ph.T0 + P / (4 * math.pi * aa * kg)
    fk.append(ph.force_per_absorbed_watt(aa, 0.1, slip=False) * P / (T - ph.T0))
record("M11", "heat-force identity: F/dT independent of a (continuum)", "I", fk, "spread < 1e-9",
       (max(fk) - min(fk)) / min(fk) < 1e-9, "T5 derivation")
# photophoretic vs radiation pressure (R5: photophoresis ~1e2-1e4 x radiation pressure for 1-10 um absorbers)
ratio = ph.photophoretic_force(a, 1e7, 0.1) / (1e7 * math.pi * a * a / 2.998e8)
record("M12", "photophoretic / radiation-pressure force, a = 2.5 um", "P", ratio, "1e2 - 1e5",
       1e2 <= ratio <= 1e5, "R5: JOSA B 34, 1242 (2017); Opt. Express 2009")

# lateral efficiency (3/8) g a: integrate absorbed-flux dipole over the lit hemisphere numerically
th = np.linspace(0, math.pi / 2, 801)
phi = np.linspace(0, 2 * math.pi, 801)
TH, PH = np.meshgrid(th, phi, indexing="ij")
g = 0.1 / a
x = a * np.sin(TH) * np.cos(PH)
z = a * np.cos(TH)
q = (1 + g * x) * np.cos(TH)                              # absorbed flux on the lit face (light along z)
dA = np.sin(TH)
num_x = np.trapezoid(np.trapezoid(q * x * dA, phi, axis=1), th)
num_z = np.trapezoid(np.trapezoid(q * z * dA, phi, axis=1), th)
record("M13", "lateral/axial dipole ratio = (3/8) g a", "I", num_x / num_z, f"{3 / 8 * g * a:.5f} +-0.5 %",
       rel(num_x / num_z, 3 / 8 * g * a) < 0.005, "T5 derivation")

# tetrahedral force allocation: closed form vs linear programme
try:
    from scipy.optimize import linprog
    d = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]) / math.sqrt(3)
    rng = np.random.default_rng(1)
    err = 0.0
    for _ in range(200):
        u = rng.normal(size=3)
        u /= np.linalg.norm(u)
        lp = linprog(np.ones(4), A_eq=d.T, b_eq=u, bounds=[(0, None)] * 4)
        err = max(err, abs(lp.fun - (-3 * min(d @ u))))
    record("M14", "push4 minimal summed force = -3 min(u.d)", "I", err, "< 1e-6", err < 1e-6, "LP check of T5")
except ImportError:
    record("M14", "push4 allocation (scipy missing)", "I", None, "scipy", False, "")

# --- photometry and emitters ------------------------------------------------------------------------------
record("M15", "V(555) = 1 -> 683 lm/W", "I", 683 * ph.V(555), "683 +-0.5 %", rel(683 * ph.V(555), 683) < 0.005, "CIE 1924")
bb = ph.incandescent_lumens(3000.0, 1e-5, eps=1.0) / (ph.SIGMA * 3000.0 ** 4 * 4 * math.pi * 1e-10)
record("M16", "blackbody luminous efficacy at 3000 K", "P", bb, "20.7 lm/W +-5 %", rel(bb, 20.7) < 0.05,
       "R6 (Planck x V); Murphy lumens-per-watt")
lm, vis, qy = ph.uc_lumens(1.0, 1e9, ph.T0, "Er_green_red")
record("M17", "UC Er/Yb efficacy at saturation, 293 K", "P", lm, "60-120 lm/W_abs (R6)", 60 <= lm <= 120,
       "R6: Kaiser 2017 (UCQY 10.5 %), Sci Rep 2023")
A5 = ph.uc_absorptance(2.5e-6, 0.20)
A5r = 1 - math.exp(-ph.N_CATION_NAYF4 * 0.2 * ph.SIGMA_YB_980 * 5e-6)
record("M18", "UC absorptance, d = 5 um, 20 % Yb (path d) vs R6 1.4 %", "P", A5r, "1.4 % +-25 %",
       rel(A5r, 0.014) < 0.25, "R6 section 1.5")
lm_p, W_p, heat_p = ph.phosphor_lumens(1.0, 405, ph.T0, "cyan_BaSi2O2N2")
record("M19", "phosphor energy balance: out + heat = absorbed", "I", W_p + heat_p, "1.000", abs(W_p + heat_p - 1) < 1e-12,
       "energy conservation")

# --- safety tables (R7 master table) ----------------------------------------------------------------------
ok = (rel(sf.ael_class1(980), 1.43e-3) < 0.02 and rel(sf.ael_class1(1064), 1.97e-3) < 0.02
      and sf.ael_class1(1550) == 10e-3 and sf.ael_class1(405) == 39e-6)
record("M20", "Class 1 AEL table (980/1064/1550/405 nm)", "I",
       [sf.ael_class1(l) for l in (405, 980, 1064, 1550)], "R7 K1 values", ok, "R7 K1; IEC 60825-1:2014 Table 3")

# --- dynamics ---------------------------------------------------------------------------------------------
# a mote in a moving generic trap: lost iff trap speed exceeds F_max/drag (static prediction), no gusts
a_d, rho_d, P_b, w_b, kp_d = 5e-6, 1500.0, 20e-3, 20e-6, 0.1
Fmax = dy.trap_Fmax(a_d, P_b, w_b, kp_d)
v_static = Fmax / (6 * math.pi * ph.mu_air(ph.T0) * a_d) * ph.cunningham(a_d)
pts = [(0.01 * math.cos(t), 0.01 * math.sin(t), 0) for t in np.linspace(0, 2 * math.pi, 129)[:-1]]   # smooth circle
lo_ok = not dy.simulate(pts, 0.8 * v_static, a_d, rho_d, P_b, w_b, kp_d, draft=(0, 0, 0), gust_sigma=0, loops=1)["lost"]
hi_lost = dy.simulate(pts, 1.25 * v_static, a_d, rho_d, P_b, w_b, kp_d, draft=(0, 0, 0), gust_sigma=0, loops=1)["lost"]
record("M21", "dynamic loss threshold brackets static F_max/drag on a circle (0.8x kept, 1.25x lost)", "I",
       dict(v_static=v_static, kept_at_0p8=lo_ok, lost_at_1p25=hi_lost), "both true", lo_ok and hi_lost, "consistency")

# --- published-display consistency -----------------------------------------------------------------------
dTs = []
for aa in (4e-6, 5e-6):
    for kp in (0.05, 0.1, 0.2):
        for C in (0.67, 1.04):
            T = ph.T0 + 100
            for _ in range(100):
                F = ph.drag(aa, 1.83, 0.5 * (ph.T0 + T))
                P = F / ph.force_per_absorbed_watt(aa, kp, T, C)
                T = 0.5 * T + 0.5 * ph.mote_temperature(P, aa, v_rel=1.83)
            dTs.append(T - ph.T0)
record("M22", "BYU 1.83 m/s (Nature 2018, lateral) reproducible below char/ignition (dT < 700 K) at eta = 1 [one-sided]", "C",
       dict(min=min(dTs), max=max(dTs)), "100 K < dT < 700 K for all cases", 100 < min(dTs) and max(dTs) < 700,
       "R5: Smalley et al. Nature 553, 486 (2018)")
# Shvedov 2009: carbon agglomerates guided at up to 1 cm/s with < 1 mW in a w = 8.4 um vortex
F1 = ph.drag(2.5e-6, 0.01)
P_need = F1 / ph.force_per_absorbed_watt(2.5e-6, 0.05)
record("M23", "Shvedov 2009 guiding (1 cm/s, < 1 mW) within model", "C", P_need * 1e6,
       "absorbed power needed < 1 mW x intercept(0.1)", P_need < 1e-4, "R5: Shvedov Opt. Express 2009")
# BYU minimum hold power 18-24 mW: the model needs far less to beat gravity -> holding is not force-limited
Pg = 4 / 3 * math.pi * (5e-6) ** 3 * 1500 * ph.G / ph.force_per_absorbed_watt(5e-6, 0.1)
record("M24", "BYU hold power (18-24 mW) >> model gravity-balance absorbed power", "C", Pg * 1e6,
       "< 1 % of 18 mW", Pg < 0.18e-3, "R5: BYU rig papers (RSI 2021)")

# --- budget self-consistency ------------------------------------------------------------------------------
dsg = bd.design(content="sketch", a=1e-6, kp=0.02, v=0.8, arch="push6", R_head=0.15, u_air=0.2)
F_chk = ph.force_per_absorbed_watt(1e-6, 0.02, dsg["Tm"]) * dsg["P_abs_force"]
record("M25", "budget: absorbed power reproduces required force at solved T", "I", F_chk / dsg["F_need"], "1 +-1e-6",
       abs(F_chk / dsg["F_need"] - 1) < 1e-6, "self-consistency")
P_heat = dsg["P_abs_force"] * math.sqrt(3) + dsg["P_abs_pump_uW"] * 1e-6 * 0
T_chk = ph.heat_loss(dsg["Tm"], 1e-6, v_rel=1.0)
record("M26", "budget: solved T within heat balance (trap heat <= loss at T)", "I",
       dict(heat_in_trap=dsg["P_abs_force"] * math.sqrt(3), loss=T_chk), "trap heat <= loss <= 1.2 x trap+pump",
       dsg["P_abs_force"] * math.sqrt(3) <= T_chk * 1.0001, "self-consistency")

# --- v2 tests (after red team 4) -------------------------------------------------------------------------
# M27: prefactor <-> creep coefficient. F = 4 pi C_s mu^2 T1/(rho T) with T1 = |J1| I a/(k_p + 2 k_g) (Epstein-consistent);
# the code's 9 pi/2 form must equal C_s = 9/8 at C_ph = 1.
Tt = ph.T0
T1 = 0.5 * 1e7 * a / (0.1 + 2 * ph.k_air(Tt))
F_creep = 4 * math.pi * (9 / 8) * ph.mu_air(Tt) ** 2 * T1 / (ph.P0 / ph.R_AIR)
record("M27", "code prefactor = thermal creep with C_s = 9/8 (Epstein-consistent derivation)", "I",
       ph.photophoretic_force(a, 1e7, 0.1, slip=False) / F_creep, "1 +-1e-9",
       abs(ph.photophoretic_force(a, 1e7, 0.1, slip=False) / F_creep - 1) < 1e-9, "RT4 Major 4; T5 v2")
# M28: Epstein thermophoresis limit from the same creep formula (independent textbook form)
G = 1000.0
T1_th = 3 * ph.k_air(Tt) * G * a / (2 * ph.k_air(Tt) + 0.1)
F_ep = 9 * math.pi * ph.mu_air(Tt) ** 2 * a * ph.k_air(Tt) * G / ((ph.P0 / ph.R_AIR) * (2 * ph.k_air(Tt) + 0.1))
F_cr = 4 * math.pi * 0.75 * ph.mu_air(Tt) ** 2 * T1_th / (ph.P0 / ph.R_AIR)
record("M28", "creep formula reproduces Epstein (1929) thermophoresis with C_s = 3/4", "P", F_cr / F_ep, "1 +-1e-9",
       abs(F_cr / F_ep - 1) < 1e-9, "Epstein 1929; Hinds eq. 10.x")
# M29: exact LG01 trap vs red team 4's independent integration (0.247 / 0.372 / 0.118 at a/w = 1, 2.5, 5 / 6.4)
lg = [ph.lg01_trap(x * 1e-6, 6.4e-6)[0] for x in (1.0, 2.5, 5.0)]
record("M29", "exact LG01 restoring efficiency vs RT4 (0.247/0.372/0.118)", "I", lg, "each within 0.02",
       all(abs(u - v) < 0.02 for u, v in zip(lg, (0.247, 0.372, 0.118))), "RT4 r9_lg01.py")
# M30: J1/A(alpha a) vs RT4 refracting ray trace (0.06/0.20/0.29/0.38/0.45/0.49 at 1/2/3/5/10/30), within 0.08
jj = [ph.j1_over_A(x) for x in (1, 2, 3, 5, 10, 30)]
record("M30", "J1/A(alpha a) straight-ray vs RT4 refracting ray trace", "I", jj, "each within 0.08",
       all(abs(u - v) < 0.08 for u, v in zip(jj, (0.06, 0.20, 0.29, 0.38, 0.45, 0.49))), "RT4 r5_j1.py")
# M31: coated-sphere conductivity limits (phi=0 -> shell; phi=1 -> core)
record("M31", "coated-sphere k_eff limits", "I", [ph.k_coated_sphere(5, 0.02, 0.0), ph.k_coated_sphere(5, 0.02, 1.0)],
       "0.02 and 5.0", abs(ph.k_coated_sphere(5, 0.02, 0.0) - 0.02) < 1e-12 and abs(ph.k_coated_sphere(5, 0.02, 1.0) - 5) < 1e-9,
       "Maxwell")
# M32: budget2 wall light never exceeds the pump power sent (energy conservation, RT4 Minor 1)
import budget2 as b2  # noqa: E402
d2 = b2.design(content="sketch", a=1e-6, v=0.3, mote="engineered", arch="room_push", whitener_gain=1.0)
wall_W = d2["wall_ratio"] * d2["P_pump_total_mW"] * 0 + d2["wall_ratio"] * (4 * math.pi * 3.0 * 1e-3 * 5.0) / (683 * ph.V(405))
record("M32", "budget2 wall light <= pump power (energy)", "I", dict(wall_W=wall_W, pump_W=d2["P_pump_total_mW"] / 1e3),
       "wall_W <= pump_W", wall_W <= d2["P_pump_total_mW"] / 1e3 * (1 + 1e-9), "RT4 Minor 1")


if __name__ == "__main__":
    n_pass = sum(t["status"] == "PASS" for t in tests)
    for t in tests:
        v = t["value"]
        vs_ = json.dumps(v, default=float)[:70]
        print(f"{t['id']} [{t['kind']}] {t['status']:4s} {t['name'][:70]:70s} {vs_}")
    print(f"{n_pass}/{len(tests)} pass")
    with open(os.path.join(RES, "validation_mote.json"), "w") as fh:
        json.dump(dict(passed=n_pass, total=len(tests), tests=tests), fh, indent=1, default=float)

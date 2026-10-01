"""Red team 6: independent checks of the LCSV (M15) and LCSV-P (M16) models. 05_reviews/red_team_6_lcsv.md.

Everything here is re-derived; physics.py is imported ONLY to cross-check the force law, heat balance and J1/A against
independent implementations (owner rule: double-validate). m15/m16 are never called; their results are read from JSON.

Sections (python3 rt6_check.py <section> ...; no argument runs all):
  phys    independent air/force/heat/J1 implementations + cross-checks vs physics.py
  geom    H10/H14 push-overhead LP re-derived from the M4 head coordinates
  repro   task 1: the three LCSV cases (+ discrepancy table vs m15 JSON)
  loop    task 2(i): latency/PWM/turbulence feedback model (frequency domain + time-domain simulation)
  dmd     task 2(ii): DMD at an intermediate field plane: depth blur and crosstalk on synthetic strokes
  holo    task 2(iii): flat-top vs NA, mode counts, MRAF multi-flat-top simulation
  mote    task 2(iv): carbon / ITO aerogel optical depth, FOM bands, hot face
  mie     task 2(v): Mie side scatter (own BHMIE, validated) + coated-sphere estimate; luminance check
  stray   task 2(vi): wall luminance vs the old 5 % rule; air and dust scatter
  safety  task 2(vii): curtain arithmetic
  m16     scope addition: LCSV-P rows and attacks
  table   corrected design table
"""
import json
import math
import os
import sys
import zlib

import numpy as np
from scipy import integrate, optimize, signal, special
from scipy.linalg import expm

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))

# ----------------------------------------------------------------------------------------------------------------------
# Independent physics
# ----------------------------------------------------------------------------------------------------------------------
T0, P0, RAIR, SIG = 293.15, 101325.0, 287.05, 5.670374e-8
KB = 1.380649e-23
# air conductivity table (Incropera Table A.4, W/m/K) - independent of physics.py's power law
_KT = np.array([250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 900, 1000.0])
_KK = np.array([22.3, 26.3, 30.0, 33.8, 37.3, 40.7, 43.9, 46.9, 49.7, 52.4, 54.9, 57.3, 62.0, 66.7]) * 1e-3


def mu(T):                       # Sutherland, C1-form
    return 1.458e-6 * T ** 1.5 / (T + 110.4)


def kg(T):
    return float(np.interp(T, _KT, _KK))


def kint(T):                     # int_T0^T k dT (trapezoid on the table)
    Ts = np.linspace(T0, T, 200)
    return float(np.trapezoid([kg(t) for t in Ts], Ts))


def mfp(T):
    return mu(T) / P0 * math.sqrt(math.pi * RAIR * T / 2)


def cunn(a, T=T0):               # Allen & Raabe (1985) coefficients (physics.py uses Davies)
    kn = mfp(T) / a
    return 1 + kn * (1.142 + 0.558 * math.exp(-0.999 / kn))


def drag(a, v, T=T0):
    Re = (P0 / (RAIR * T)) * abs(v) * 2 * a / mu(T)
    return 6 * math.pi * mu(T) * a * v * (1 + 3 / 16 * Re) / cunn(a, T)


def pp_force(a, I, kp, J1, Tm=T0, C=0.85):
    """Delta-T photophoretic force (Yalamov/Reed continuum + Talbot slip), gas at film temperature, rho*T = p/R."""
    Tf = 0.5 * (T0 + Tm)
    kn = mfp(Tf) / a
    k2 = kg(Tf)
    slip = 1.0 / ((1 + 3 * 1.14 * kn) * (1 + 2 * 2.18 * kn * kp / (kp + 2 * k2)))
    return C * 9 * math.pi * mu(Tf) ** 2 * a * I * J1 / (2 * (P0 / RAIR) * (kp + 2 * k2)) * slip


def heat_loss(Tm, a, v=0.0, eps=0.9):
    Tf = 0.5 * (T0 + Tm)
    zeta = 2 * 1.4 / 2.4 * mfp(Tf) / 0.71                       # Fuchs jump distance, alpha_T = 1
    Pe = (P0 / (RAIR * Tf)) * abs(v) * 2 * a / mu(Tf) * 0.71
    return (4 * math.pi * a * kint(Tm) * (1 + min(Pe, 1) / 4) / (1 + zeta / a)
            + eps * SIG * 4 * math.pi * a * a * (Tm ** 4 - T0 ** 4))


def T_of_P(P, a, v=0.0):
    if P <= 0:
        return T0
    return optimize.brentq(lambda T: heat_loss(T, a, v) - P, T0, 5000.0)


def j1A_abs(aa, n=400):
    """|J1|/A and absorptance A for a volume absorber, straight rays, Gauss-Legendre in b = sin(phi) (independent of
    physics.py's midpoint rule). J1 = (3/4) M1/(P a): first moment of the absorbed power toward the lit side."""
    if aa > 300:
        return 0.5, 1.0
    x, w = np.polynomial.legendre.leggauss(n)
    ph_ = 0.25 * math.pi * (x + 1)                 # phi in (0, pi/2), b = sin(phi), db = cos(phi) dphi
    wb = w * 0.25 * math.pi
    b = np.sin(ph_)
    L = 2 * np.cos(ph_)                            # chord / a
    E = np.exp(-aa * L)
    Pb = 1 - E                                     # absorbed fraction on the ray
    # int_0^L aa e^{-aa s} (L/2 - s) ds   (distance toward the lit face measured from the centre plane)
    Mb = (L / 2) * Pb - (1 / aa - E * (L + 1 / aa))
    jac = b * np.cos(ph_)
    P = np.sum(wb * Pb * jac) * 2                  # normalised by pi a^2 * I  (int 2 b db)
    M = np.sum(wb * Mb * jac) * 2
    return 0.75 * M / P, P


def j1A_mc(aa, n=400000, seed=1):
    """Monte-Carlo check of J1/A (third method)."""
    rng = np.random.default_rng(seed)
    b = np.sqrt(rng.random(n))
    L = 2 * np.sqrt(1 - b * b)
    s = -np.log(1 - rng.random(n)) / aa
    hit = s < L
    z = L[hit] / 2 - s[hit]
    return 0.75 * z.mean(), hit.mean()


# ----------------------------------------------------------------------------------------------------------------------
# Inputs copied (as data, not code) from m15 so the reproduction is like-for-like
# ----------------------------------------------------------------------------------------------------------------------
CONTENT = {"accent": (3.0, 1.0, 0.5), "sketch": (3.0, 5.0, 0.57), "film_density": (4.0, 30.0, 0.83)}
MOTES = {
    "carbon_aerogel": dict(alpha=3e5, k=0.045, q=0.05, Tmax=600.0, rho=100.0, j1f=1.0),
    "carbon_aerogel_white": dict(alpha=3e5, k=0.055, q=0.30, Tmax=600.0, rho=110.0, j1f=0.9),
    "carbon_aerogel_pess": dict(alpha=2e5, k=0.08, q=0.03, Tmax=550.0, rho=150.0, j1f=1.0),
    "ito_aerogel": dict(alpha=None, j1A=0.486, A=1.0, k=0.04, q=0.30, Tmax=600.0, rho=150.0, j1f=1.0),
}
ROOMS = {"quiet": 0.10, "calm": 0.15, "normal": 0.30}
LAYOUT_M15 = {"H10": dict(h_worst=2.14, h_mean=1.38, heads=10, occ=4.47), "H14": dict(h_worst=2.14, h_mean=1.28, heads=14, occ=3.73)}
COST_VOL = dict(px=3e-5, W_ir=20.0, W_vis=50.0, head=2e3)
COST_LAB = dict(px=1.1e-3, W_ir=200.0, W_vis=500.0, head=20e3)
V500 = 0.323                                     # CIE 1931 V(500 nm)
AEL_1550, AEL_500 = 10e-3, 0.39e-3


def mote(name, a):
    M = dict(MOTES[name])
    if M.get("alpha"):
        jA, A = j1A_abs(M["alpha"] * a)
        M["j1A"], M["A"] = jA * M["j1f"], A
    return M


def holding(a, M, u, h_worst, C=0.85, margin=1.3):
    """Mote temperature and holding intensity for force margin*drag(u) in the worst direction (heat = h_worst*P)."""
    def resid(Tm):
        Tf = 0.5 * (T0 + Tm)
        F = margin * drag(a, u, Tf)
        Pabs = F / pp_force(a, 1.0, M["k"], M["j1A"], Tm, C) * M["A"] * math.pi * a * a
        return heat_loss(Tm, a, u) - h_worst * Pabs, Pabs
    Tm = optimize.brentq(lambda T: resid(T)[0], T0 + 1e-3, 3000.0)
    Pabs = resid(Tm)[1]
    return dict(Tm=Tm, dT=Tm - T0, P_abs=Pabs, I_hold=Pabs / (M["A"] * math.pi * a * a),
                FOM=M["j1A"] / (M["k"] + 2 * kg(T0)))


def lcsv(content, a, mote_name, room, layout, delta=3e-3, r_c=None, r_v=None, jitter=None, f_fast=2e4, bw_frac=0.1,
         eff_holo=0.6, eta_shape=0.8, u_force=None, q=None, cap=100.0, layouts=LAYOUT_M15, occluded=False, M=None,
         extra_eff=1.0, modes_factor=1.0):
    L, S, _ = CONTENT[content]
    M = M or mote(mote_name, a)
    if q is not None:
        M = dict(M, q=q)
    G = dict(layouts[layout])
    hw = G["occ"] if occluded else G["h_worst"]
    u = ROOMS[room] if isinstance(room, str) else room
    H = holding(a, M, u if u_force is None else u_force, hw)
    jit = u / (2 * math.pi * bw_frac * f_fast) if jitter is None else jitter
    rmin = max(3 * jit, 3 * a)
    N = S / delta
    Phi = 4 * math.pi * L * 1e-3 * S
    Psc = Phi / N / (683 * V500)
    I_vis = Psc / (M["q"] * math.pi * a * a)
    vmin = max(2 * jit, 1.5 * a)
    eff = eff_holo * extra_eff

    def evaluate(rc, rv):
        Pu = H["I_hold"] * math.pi * rc ** 2 / eta_shape
        P_ir = N * G["h_mean"] * Pu / eff
        Pvs = I_vis * math.pi * rv ** 2 / eta_shape
        P_vis = N * Pvs / eff
        Mdir = modes_factor / (math.pi * rc ** 2)
        Mvis = modes_factor / (math.pi * rv ** 2)
        px = G["heads"] * Mdir + Mvis
        c = {k: C["px"] * px + C["W_ir"] * P_ir + C["W_vis"] * P_vis + C["head"] * G["heads"]
             for k, C in (("vol", COST_VOL), ("lab", COST_LAB))}
        Lwall = 0.8 * 1e-3 * P_vis * 683 * V500 / (math.pi * 50)
        fails = []
        if H["Tm"] > M["Tmax"]:
            fails.append("heat")
        if 0.02 * hw * Pu > AEL_1550:
            fails.append("trap_curtain_threshold")
        if Pvs > AEL_500:
            fails.append("vis_spot_class1")
        if P_vis > AEL_500 / (2 * (3.5e-3 / 0.3) ** 2):
            fails.append("vis_exit_window")
        if P_ir > cap:
            fails.append("ir_power_cap")
        if Lwall > 0.01:
            fails.append("wall_light")
        return dict(r_c_um=rc * 1e6, r_v_um=rv * 1e6, P_unit_mW=Pu * 1e3, P_focus_mW=hw * Pu * 1e3, P_ir_W=P_ir,
                    P_vis_spot_uW=Pvs * 1e6, P_vis_W=P_vis, M_dir=Mdir, M_vis=Mvis, px_total=px,
                    cost_vol_k=c["vol"] / 1e3, cost_lab_k=c["lab"] / 1e3, L_wall=Lwall, fails=fails)
    if r_c is None:
        # continuous optimum (volume prices): cost(rc) = A/rc^2 + B rc^2 separately in rc and rv, with bounds
        A_c = COST_VOL["px"] * G["heads"] * modes_factor / math.pi
        B_c = COST_VOL["W_ir"] * N * G["h_mean"] * H["I_hold"] * math.pi / (eta_shape * eff)
        rc_cap = math.sqrt(0.999 * cap * eff * eta_shape / (N * G["h_mean"] * H["I_hold"] * math.pi))
        r_c = min(max((A_c / B_c) ** 0.25, rmin), rc_cap) if rc_cap >= rmin else rmin
        A_v = COST_VOL["px"] * modes_factor / math.pi
        B_v = COST_VOL["W_vis"] * N * I_vis * math.pi / (eta_shape * eff)
        rv_cl = math.sqrt(0.999 * AEL_500 * eta_shape / (I_vis * math.pi))
        rv_ew = math.sqrt(0.999 * AEL_500 / (2 * (3.5e-3 / 0.3) ** 2) * eff * eta_shape / (N * I_vis * math.pi))
        rv_cl = min(rv_cl, rv_ew)
        r_v = max((A_v / B_v) ** 0.25, vmin)
        r_v = min(r_v, rv_cl) if rv_cl >= vmin else vmin
    out = dict(content=content, a_um=a * 1e6, mote=mote_name, room=room, layout=layout, N=N, FOM=H["FOM"],
               j1A=M["j1A"], A=M["A"], dT=H["dT"], I_hold=H["I_hold"], jitter_um=jit * 1e6, phi_mote_lm=Phi / N,
               P_sc_W=Psc, I_vis=I_vis)
    out.update(evaluate(r_c, r_v))
    out["feasible"] = not out["fails"]
    return out


# ----------------------------------------------------------------------------------------------------------------------
def sec_phys():
    import physics as ph
    rows = []
    for a, kp, Tm in ((5e-6, 0.04, 370.0), (10e-6, 0.055, 530.0), (1e-6, 0.04, 490.0)):
        f_me = pp_force(a, 1e6, kp, 0.486, Tm, 0.85)
        f_ph = ph.photophoretic_force(a, 1e6, kp, J1=0.486, Tm=Tm, C_ph=0.85)
        P = 4e-6 * (a / 5e-6)
        t_me, t_ph = T_of_P(P, a, 0.1), ph.mote_temperature(P, a, v_rel=0.1)
        d_me, d_ph = drag(a, 0.1), ph.drag(a, 0.1)
        rows.append(dict(a_um=a * 1e6, force_rt6=f_me, force_ph=f_ph, force_ratio=f_me / f_ph, T_rt6=t_me, T_ph=t_ph,
                         dT_ratio=(t_me - T0) / (t_ph - T0), drag_ratio=d_me / d_ph))
    jrows = []
    for aa in (0.5, 1.0, 1.5, 3.0, 6.0, 30.0):
        jg, Ag = j1A_abs(aa)
        jm, Am = j1A_mc(aa)
        jrows.append(dict(alpha_a=aa, j1A_gl=jg, j1A_mc=jm, j1A_ph=ph.j1_over_A(aa), A_gl=Ag, A_mc=Am, A_ph=ph.absorptance(aa)))
    # closed form B2 (T6) vs full model
    M = mote("ito_aerogel", 5e-6)
    Hh = holding(5e-6, M, 0.1, 1.0)
    I_cf = 1.3 * 4 * (P0 / RAIR) * 0.1 / (3 * 0.85 * mu(T0) * Hh["FOM"] * 1.0 * cunn(5e-6))
    out = dict(force_heat_drag=rows, j1A=jrows, B2_closed_form=I_cf, B2_model_h1=Hh["I_hold"], B2_ratio=Hh["I_hold"] / I_cf)
    print("PHYS: force/heat/drag ratios rt6/physics.py")
    for r in rows:
        print(f"  a={r['a_um']:.0f}um force {r['force_ratio']:.3f}  dT {r['dT_ratio']:.3f}  drag {r['drag_ratio']:.4f}")
    for r in jrows:
        print(f"  alpha*a={r['alpha_a']:5.1f}  J1/A GL {r['j1A_gl']:.4f} MC {r['j1A_mc']:.4f} ph {r['j1A_ph']:.4f} | "
              f"A GL {r['A_gl']:.4f} MC {r['A_mc']:.4f} ph {r['A_ph']:.4f}")
    print(f"  B2 closed form {I_cf:.3e} vs model (h=1, hot gas) {Hh['I_hold']:.3e} ratio {out['B2_ratio']:.3f}")
    json.dump(out, open(os.path.join(RES, "rt6_phys.json"), "w"), indent=1)
    return out


# ----------------------------------------------------------------------------------------------------------------------
CEIL = [(0.15, 0.15, 2.7), (5.85, 0.15, 2.7), (5.85, 4.85, 2.7), (0.15, 4.85, 2.7)]
FLOOR = [(0.15, 0.15, 0.12), (5.85, 0.15, 0.12), (5.85, 4.85, 0.12), (0.15, 4.85, 0.12)]
NICHE = [(0.05, 2.5, 1.3), (5.95, 2.5, 1.3), (3.0, 0.05, 1.3), (3.0, 4.95, 1.3)]
H10 = CEIL + FLOOR + [(3.0, 2.5, 2.75), (3.0, 2.5, 0.05)]
H14 = CEIL + FLOOR + NICHE + [(3.0, 2.5, 2.75), (3.0, 2.5, 0.05)]
CENTER, HALF = np.array([3.0, 2.5, 1.3]), np.array([0.5, 0.5, 0.4])


def sphere_pts(n, seed=0):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1)[:, None]


def min_push(D, u):
    r = optimize.linprog(np.ones(len(D)), A_eq=D.T, b_eq=u, bounds=[(0, None)] * len(D), method="highs")
    return (r.fun, r.x) if r.success else (math.inf, None)


def sec_geom():
    out = {}
    U = sphere_pts(400, 7)
    rng = np.random.default_rng(3)
    pts = CENTER + HALF * rng.uniform(-1, 1, size=(40, 3))
    for name, heads in (("H10", H10), ("H14", H14)):
        Hd = np.asarray(heads, float)
        hs, occ, nact, throws = [], [], [], []
        for p in np.vstack([pts, CENTER + HALF * np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])]):
            D = p - Hd
            throws += list(np.linalg.norm(D, axis=1))
            D = D / np.linalg.norm(D, axis=1)[:, None]
            for u in U:
                h, f = min_push(D, u)
                hs.append(h)
                nact.append(int((f > 1e-6).sum()))
            for k in range(len(Hd)):
                Dk = np.delete(D, k, 0)
                occ.append(max(min_push(Dk, u)[0] for u in U[::8]))
        hs, occ = np.array(hs), np.array(occ)
        # 'provisioned' power if every head's spot must carry its worst-case share at all times (no slow redistribution)
        out[name] = dict(h_worst=float(hs.max()), h_mean=float(hs.mean()), occ_p95=float(np.percentile(occ[np.isfinite(occ)], 95)),
                         occ_infeasible=float(np.mean(~np.isfinite(occ))), active_mean=float(np.mean(nact)),
                         throw_min=float(min(throws)), throw_max=float(max(throws)),
                         throws_center=[float(np.linalg.norm(np.array(h) - CENTER)) for h in heads])
        print(f"GEOM {name}: h_worst {out[name]['h_worst']:.2f} mean {out[name]['h_mean']:.2f} occluded p95 {out[name]['occ_p95']:.2f} "
              f"(infeasible {out[name]['occ_infeasible']:.3f}); active {out[name]['active_mean']:.2f}; throws {out[name]['throw_min']:.2f}-{out[name]['throw_max']:.2f} m")
    json.dump(out, open(os.path.join(RES, "rt6_geom.json"), "w"), indent=1)
    return out


# ----------------------------------------------------------------------------------------------------------------------
CASES = {
    "a_sketch_ito5": dict(content="sketch", a=5e-6, mote_name="ito_aerogel", room="quiet", layout="H10"),
    "b_film_ito5": dict(content="film_density", a=5e-6, mote_name="ito_aerogel", room="quiet", layout="H10"),
    "c_sketch_carbonW10": dict(content="sketch", a=10e-6, mote_name="carbon_aerogel_white", room="quiet", layout="H10"),
}


def m15_row(case):
    rows = json.load(open(os.path.join(RES, "m15d_layouts.json")))
    c = CASES[case]
    for r in rows:
        if (r["content"] == c["content"] and r["room"] == c["room"] and r["mote"] == c["mote_name"]
                and r["layout"] == c["layout"]):
            return r
    raise KeyError(case)


def sec_repro():
    out = {}
    print("REPRO: rt6 (independent) vs m15d JSON;  [at m15's r_c,r_v] and [rt6 continuous optimum]")
    keys = [("FOM", "FOM"), ("dT", "dT"), ("jitter_um", "jitter_um"), ("r_c_um", "r_c_um"), ("r_v_um", "r_v_um"),
            ("P_focus_mW", "P_focus_mW"), ("P_ir_W", "P_ir_W"), ("P_vis_spot_uW", "P_vis_spot_uW"), ("P_vis_W", "P_vis_W"),
            ("M_dir", "M_dir"), ("M_vis", "M_vis")]
    for case, c in CASES.items():
        m = m15_row(case)
        same = lcsv(**c, r_c=m["r_c_um"] * 1e-6, r_v=m["r_v_um"] * 1e-6)
        opt = lcsv(**c)
        occl = lcsv(**c, r_c=m["r_c_um"] * 1e-6, r_v=m["r_v_um"] * 1e-6, occluded=True)
        m_px = 10 * m["M_dir"] + m["M_vis"]
        I_m15 = m["P_focus_mW"] * 1e-3 / 2.14 * 0.8 / (math.pi * (m["r_c_um"] * 1e-6) ** 2)
        comp = {k1: dict(m15=m[k2], rt6_same=same[k1], rt6_opt=opt[k1], dev_same=same[k1] / m[k2] - 1) for k1, k2 in keys}
        comp["px_total"] = dict(m15=m_px, rt6_same=same["px_total"], rt6_opt=opt["px_total"], dev_same=same["px_total"] / m_px - 1)
        comp["I_hold"] = dict(m15=I_m15, rt6_same=same["I_hold"], rt6_opt=opt["I_hold"], dev_same=same["I_hold"] / I_m15 - 1)
        comp["occluded_dT"] = dict(m15=m["occluded_dT"], rt6_same=occl["dT"], rt6_opt=occl["dT"], dev_same=occl["dT"] / m["occluded_dT"] - 1)
        out[case] = dict(compare=comp, rt6_same=same, rt6_opt=opt, rt6_occluded=occl, m15_fails=m["fails"])
        print(f" {case}")
        for k, v in comp.items():
            flag = "  <-- >15%" if abs(v["dev_same"]) > 0.15 else ""
            print(f"   {k:14s} m15 {v['m15']:10.4g}  rt6@same {v['rt6_same']:10.4g} ({100 * v['dev_same']:+5.1f}%)  rt6 opt {v['rt6_opt']:10.4g}{flag}")
        print(f"   fails m15 {m['fails']}  rt6 {same['fails']} / opt {opt['fails']} ; occluded fails {occl['fails']}")
    json.dump(out, open(os.path.join(RES, "rt6_repro.json"), "w"), indent=1, default=float)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Task 2(i): feedback loop with latency, force lag, DMD quantisation and Kolmogorov drafts
# ----------------------------------------------------------------------------------------------------------------------
NU_AIR = 1.51e-5


def turb_spectrum(f, u_rms, L, Uc, Ceps=0.5):
    """One-sided Eulerian frequency spectrum (m^2/s^2/Hz) of one velocity component at a fixed point: von Karman
    longitudinal spectrum with a Pao dissipation cutoff, Taylor conversion f = Uc k/(2 pi)."""
    eps = Ceps * u_rms ** 3 / L
    eta = (NU_AIR ** 3 / eps) ** 0.25
    k = 2 * math.pi * np.asarray(f) / Uc
    F = (2 * L / math.pi) / (1 + (1.339 * L * k) ** 2) ** (5 / 6) * np.exp(-2.25 * (k * eta) ** (4 / 3))
    return F * 2 * math.pi / Uc, eta


def turb_norm(u_rms, L, Uc):
    f = np.logspace(-4, 5, 20000)
    S, eta = turb_spectrum(f, 1.0, L, Uc)
    S = S * (1.0 / u_rms ** 2) * 0 + S          # unit-variance shape
    m0 = np.trapezoid(S, f)
    # use u_rms for the cutoff (eta depends on u_rms)
    S2, eta = turb_spectrum(f, u_rms, L, Uc)
    m0 = np.trapezoid(S2, f)
    m2 = np.trapezoid(S2 * f * f, f)
    return f, S2 * u_rms ** 2 / m0, eta, math.sqrt(m2 / m0)


def rice_level(rate, nu0, dims=3):
    """Level b/sigma whose upcrossing rate equals `rate` for an isotropic Gaussian vector process (chi_dims) with
    per-component zero-crossing frequency nu0 (Hz). sigma'/sigma = 2 pi nu0."""
    w = 2 * math.pi * nu0
    if dims == 1:
        f = lambda x: 2 * w / (2 * math.pi) * math.exp(-x * x / 2) - rate          # |u_x| two-sided
    else:
        f = lambda x: w / math.pi * x * x * math.exp(-x * x / 2) - rate
    return optimize.brentq(f, 1.0, 20.0)


def mote_times(a, rho, cp, kp):
    m = 4 / 3 * math.pi * a ** 3 * rho
    gam = 6 * math.pi * mu(T0) * a / cunn(a)
    tau_p = m / gam
    kap = 2 * kg(T0) / kp
    # slowest l=1 internal mode with gas-side flux 2 k_g T/a: k_p*lam*j1'(lam) = -2 k_g j1(lam)
    j1 = lambda x: special.spherical_jn(1, x)
    dj1 = lambda x: special.spherical_jn(1, x, derivative=True)
    lam = optimize.brentq(lambda x: x * dj1(x) + kap * j1(x), 0.5, 4.49)
    tau_F = a * a * rho * cp / kp / lam ** 2
    return tau_p, tau_F


def plant_ss(tau_p, tau_F):
    A = np.array([[0, 1, 0], [0, -1 / tau_p, 1 / tau_p], [0, 0, -1 / tau_F]])
    B = np.array([[0, 0], [1 / tau_p, 0], [0, 1 / tau_F]])      # inputs: u (air), w_c (commanded force / gamma)
    return A, B


def discretise(A, B, T):
    n, m = A.shape[0], B.shape[1]
    Mx = np.zeros((n + m, n + m))
    Mx[:n, :n], Mx[:n, n:] = A * T, B * T
    E = expm(Mx)
    return E[:n, :n], E[:n, n:]


def plant_resp(tau_p, tau_F, T, d, fturb):
    """Precompute the discrete w_c -> x response on the unit circle and at the turbulence frequencies."""
    Ad, Bd = discretise(*plant_ss(tau_p, tau_F), T)
    num, den = signal.ss2tf(Ad, Bd[:, [1]], np.array([[1.0, 0, 0]]), np.zeros((1, 1)))
    th = np.linspace(1e-4, math.pi, 4000)
    z = np.exp(1j * th)
    zt = np.exp(1j * 2 * math.pi * fturb * T)
    Pw = np.polyval(num[0], z) / np.polyval(den, z) * z ** (-d)
    Pwt = np.polyval(num[0], zt) / np.polyval(den, zt) * zt ** (-d)
    return dict(z=z, th=th, Pw=Pw, zt=zt, Pwt=Pwt, T=T, tau_p=tau_p, f=fturb, num=num[0], den=den, d=d)


def stable(pr, K):
    """Closed-loop poles of the discrete PID loop inside the unit circle (Nyquist-safe check)."""
    Kp, Ki, Kd = K
    T = pr["T"]
    if Ki == 0:                      # PD: C = [Kp T z + Kd (z-1)] / (T z)  (no common (z-1) factor)
        Nc = np.array([Kp * T + Kd, -Kd])
        Dc = T * np.array([1.0, 0.0])
    else:
        Nc = np.polyadd(np.polyadd(Kp * T * np.array([1.0, -1.0, 0.0]), Ki * T * T * np.array([1.0, 0.0, 0.0])),
                        Kd * np.array([1.0, -2.0, 1.0]))
        Dc = T * np.array([1.0, -1.0, 0.0])
    zd = np.zeros(pr["d"] + 1)
    zd[0] = 1.0
    char = np.polyadd(np.polymul(np.polymul(Dc, pr["den"]), zd), np.polymul(Nc, np.trim_zeros(pr["num"], "f")))
    return bool(np.max(np.abs(np.roots(char))) < 1 - 1e-9)


def loop_freq(pr, K, Sturb, sig_n, q_step):
    """Frequency-domain closed loop (discrete PID at frame period T with d frames of latency). sigma_x per axis from
    turbulence, sensor noise and quantisation (first-order error feedback), and the modulus margin max|S|."""
    Kp, Ki, Kd = K
    z, th, Pw, zt, Pwt, T = pr["z"], pr["th"], pr["Pw"], pr["zt"], pr["Pwt"], pr["T"]
    C = Kp + Ki * T / (1 - 1 / z) + Kd * (1 - 1 / z) / T
    L = C * Pw
    S = 1 / (1 + L)
    Tc = L / (1 + L)
    Ms = float(np.max(np.abs(S)))
    w = 2 * math.pi * pr["f"]
    Ct = Kp + Ki * T / (1 - 1 / zt) + Kd * (1 - 1 / zt) / T
    Gu = 1 / (1j * w * (1 + 1j * w * pr["tau_p"]))
    Hx = Gu / (1 + Ct * Pwt)
    var_t = float(np.trapezoid(np.abs(Hx) ** 2 * Sturb, pr["f"]))
    var_n = sig_n ** 2 * float(np.trapezoid(np.abs(Tc) ** 2, th) / math.pi)
    var_q = (q_step ** 2 / 12) * float(np.trapezoid(np.abs(Pw * S * (1 - 1 / z)) ** 2, th) / math.pi)
    return math.sqrt(var_t), math.sqrt(var_n), math.sqrt(var_q), Ms


def crossover_hz(pr, K):
    Kp, Ki, Kd = K
    z, T = pr["z"], pr["T"]
    L = (Kp + Ki * T / (1 - 1 / z) + Kd * (1 - 1 / z) / T) * pr["Pw"]
    i = int(np.argmax(np.abs(L) < 1))
    return float(np.angle(z[i]) / (2 * math.pi * T))


def tune(tau_p, tau_F, T, d, fturb, Sturb, sig_n, q_step, Ms_max=2.0):
    pr = plant_resp(tau_p, tau_F, T, d, fturb)
    best = None
    w_ref = 1 / ((d + 0.5) * T + tau_F + tau_p)       # rough crossover scale (rad/s)
    for kp in w_ref * np.array([0.1, 0.15, 0.25, 0.35, 0.5, 0.7, 1.0, 1.4]):
        for ti_mult in (2, 3, 6, 12, 1e9):
            for kd_mult in (0.0, 0.15, 0.3, 0.6, 1.0):
                ki = kp / (ti_mult / w_ref) if ti_mult < 1e8 else 0.0
                kd = kp * kd_mult * (tau_p + tau_F)
                st, sn, sq, Ms = loop_freq(pr, (kp, ki, kd), Sturb, sig_n, q_step)
                if Ms > Ms_max or not np.isfinite(st) or not stable(pr, (kp, ki, kd)):
                    continue
                tot = math.sqrt(st * st + sn * sn + sq * sq)
                if best is None or tot < best[0]:
                    best = (tot, (kp, ki, kd), st, sn, sq, Ms)
    return best


def synth_turb(n_series, n, fs, u_rms, L, Uc, rng):
    f = np.fft.rfftfreq(n, 1 / fs)
    S, _ = turb_spectrum(np.maximum(f, 1e-6), u_rms, L, Uc)
    S[0] = 0
    amp = np.sqrt(S * fs * n / 2)
    X = (rng.normal(size=(n_series, f.size)) + 1j * rng.normal(size=(n_series, f.size))) * amp
    x = np.fft.irfft(X, n=n, axis=1)
    x *= u_rms / x.std()
    return x.astype(np.float32)


def simulate(tau_p, tau_F, T, d, K, u_rms, L, Uc, sig_n, w_max, levels, n_motes=150, dur=8.0, seed=0, fs_t=4000.0):
    """Time-domain: 3 axes x n_motes, exact per-frame discretisation, ZOH force, d-frame latency, saturation at w_max
    (force authority expressed as the air speed it balances), DMD quantisation into `levels` steps per sign with
    first-order error feedback (sigma-delta). Returns radial-error statistics."""
    rng = np.random.default_rng(seed)
    Ad, Bd = discretise(*plant_ss(tau_p, tau_F), T)
    n_fr = int(dur / T)
    n_t = int(dur * fs_t) + 2
    M = 3 * n_motes
    U = synth_turb(M, n_t, fs_t, u_rms, L, Uc, rng)
    s = np.zeros((3, M))
    hist = np.zeros((d + 1, M))
    Kp, Ki, Kd = K
    integ = np.zeros(M)
    e_prev = np.zeros(M)
    sd_err = np.zeros(M)
    sat_frames = 0
    r_max = np.zeros(n_motes)
    samples = []
    first_exceed = {r: np.full(n_motes, np.inf) for r in (10e-6, 20e-6, 30e-6, 50e-6, 100e-6)}
    for k in range(n_fr):
        t = k * T
        it = t * fs_t
        i0 = int(it)
        fr = it - i0
        u = U[:, i0] * (1 - fr) + U[:, i0 + 1] * fr
        y = hist[-1] + sig_n * rng.standard_normal(M)        # measurement taken d frames ago
        e = -y
        wc_raw = Kp * e + Ki * T * integ + Kd * (e - e_prev) / T
        e_prev = e
        wc = np.clip(wc_raw, -w_max, w_max)
        integ += np.where(np.abs(wc_raw) < w_max, e, 0.0)   # conditional integration (anti-windup)
        if levels:
            v = wc + sd_err
            wq = np.clip(np.round(v / w_max * levels), -levels, levels) * w_max / levels
            sd_err = v - wq
            wc = wq
        sat_frames += int(np.sum(np.abs(wc_raw) >= w_max))
        s = Ad @ s + Bd[:, [0]] * u + Bd[:, [1]] * wc
        hist = np.roll(hist, 1, axis=0)
        hist[0] = s[0]
        if k * T > 0.2:
            r = np.sqrt(s[0, 0::3] ** 2 + s[0, 1::3] ** 2 + s[0, 2::3] ** 2)
            r_max = np.maximum(r_max, r)
            for rr, arr in first_exceed.items():
                hit = (r > rr) & ~np.isfinite(arr)
                arr[hit] = t
            if k % 20 == 0:
                samples.append(s[0].copy())
    X = np.array(samples)
    sx = float(X.std())
    t_eff = n_motes * (dur - 0.2)
    exceed_rate = {f"{rr * 1e6:.0f}um": float(np.sum(np.isfinite(arr)) / t_eff) for rr, arr in first_exceed.items()}
    R = np.sqrt(X[:, 0::3] ** 2 + X[:, 1::3] ** 2 + X[:, 2::3] ** 2).ravel()
    return dict(sigma_x_um=sx * 1e6, r_p50_um=float(np.percentile(R, 50) * 1e6), r_p999_um=float(np.percentile(R, 99.9) * 1e6),
                r_max_um=float(r_max.max() * 1e6), sat_frac=sat_frames / (n_fr * M), first_exceed_rate_per_s=exceed_rate,
                mote_seconds=t_eff)


def sec_loop(quick=False):
    out = dict(motes={}, rice={}, freq=[], sim=[])
    motes = {"ito5": (5e-6, 150.0, 800.0, 0.04), "carbonW10": (10e-6, 110.0, 700.0, 0.055)}
    for k, (a, rho, cp, kp) in motes.items():
        tp, tf = mote_times(a, rho, cp, kp)
        out["motes"][k] = dict(tau_p_us=tp * 1e6, tau_F_us=tf * 1e6)
        print(f"LOOP mote {k}: tau_p {tp * 1e6:.0f} us, force lag (l=1 thermal mode) {tf * 1e6:.0f} us")
    # Rice: force authority needed against drafts (loss < 1e-4 /s per mote)
    for u_rms in (0.03, 0.1, 0.3):
        for L in (0.01, 0.03, 0.1):
            for Ucm in (1.0, 3.0):
                f, S, eta, nu0 = turb_norm(u_rms, L, Ucm * u_rms)
                b = rice_level(1e-4, nu0, 3)
                b1 = rice_level(1e-4, nu0, 1)
                out["rice"][f"u{u_rms}_L{L}_Uc{Ucm}"] = dict(u_rms=u_rms, L=L, Uc=Ucm * u_rms, eta_mm=eta * 1e3, nu0_Hz=nu0,
                                                            b_sigma_3D=b, b_sigma_axis=b1, u_auth=b * u_rms,
                                                            force_vs_m15_quiet=b * u_rms / 0.13)
    print("LOOP Rice levels (3D isotropic, 1e-4/s): " + ", ".join(
        f"{k}: nu0 {v['nu0_Hz']:.0f} Hz b {v['b_sigma_3D']:.2f}" for k, v in out["rice"].items() if "Uc1.0" in k))
    # frequency-domain sweep
    cfgs = []
    for mk in ("ito5", "carbonW10"):
        for f_fr, dlist in ((20e3, (2, 3, 5)), (12.5e3, (2, 3))):
            for d in dlist:
                for u_rms, L in ((0.1, 0.01), (0.1, 0.1), (0.3, 0.01), (0.3, 0.1)):
                    cfgs.append((mk, f_fr, d, u_rms, L))
    for mk, f_fr, d, u_rms, L in cfgs:
        tp, tf = out["motes"][mk]["tau_p_us"] * 1e-6, out["motes"][mk]["tau_F_us"] * 1e-6
        T = 1 / f_fr
        fturb, Sturb, eta, nu0 = turb_norm(u_rms, L, u_rms)
        sel = (fturb > 1e-3) & (fturb < 0.45 * f_fr)
        fturb, Sturb = fturb[sel][::4], Sturb[sel][::4]
        rec = dict(mote=mk, f_frame=f_fr, latency_us=d * T * 1e6, u_rms=u_rms, L=L)
        for lv_name, levels in (("binary", 1), ("64lev", 64)):
            w_max = 4.5 * u_rms
            q = 2 * w_max / (2 * levels)      # step between adjacent levels (levels per sign)
            best = tune(tp, tf, T, d, fturb, Sturb, 1e-6, q)
            if best is None:
                rec[lv_name] = None
                continue
            tot, K, st, sn, sq, Ms = best
            fc = crossover_hz(plant_resp(tp, tf, T, d, fturb), K)
            bx = rice_level(1e-4, max(fc, 1.0), 3)          # radial error level for 1e-4/s, nu_x ~ crossover
            a_m = 5e-6 if mk == "ito5" else 10e-6
            rec[lv_name] = dict(sigma_tot_um=tot * 1e6, sig_turb_um=st * 1e6, sig_noise_um=sn * 1e6, sig_quant_um=sq * 1e6,
                                Ms=Ms, K=K, w_max=w_max, f_c_Hz=fc, b_x=bx, r_c_needed_um=(a_m + bx * tot) * 1e6)
        # P-only "m15 formula" check: steady error u/omega_c for a P loop with the same latency
        rec["m15_jitter_um"] = 0.1 / (2 * math.pi * 2e3) * 1e6 * (u_rms / 0.1)
        out["freq"].append(rec)
        b = rec.get("binary")
        g = rec.get("64lev")
        print(f"  {mk:9s} {f_fr / 1e3:4.1f}kHz lat {rec['latency_us']:3.0f}us u {u_rms} L {L}: binary sigma "
              f"{b['sigma_tot_um'] if b else float('nan'):6.2f} um (turb {b['sig_turb_um'] if b else 0:.2f}, noise {b['sig_noise_um'] if b else 0:.2f}, "
              f"quant {b['sig_quant_um'] if b else 0:.2f}) f_c {b['f_c_Hz'] if b else 0:5.0f} Hz r_c,min {b['r_c_needed_um'] if b else 0:5.1f} | "
              f"64-level {g['sigma_tot_um'] if g else float('nan'):6.2f} um r_c,min {g['r_c_needed_um'] if g else 0:5.1f}")
    # time-domain validation on a subset (also exercises saturation)
    sims = [("ito5", 20e3, 3, 0.1, 0.01, 4.5, 1), ("ito5", 20e3, 3, 0.1, 0.01, 4.5, 64),
            ("ito5", 12.5e3, 2, 0.1, 0.01, 4.5, 1), ("ito5", 20e3, 5, 0.3, 0.01, 4.5, 64),
            ("carbonW10", 20e3, 3, 0.1, 0.01, 4.5, 1), ("carbonW10", 20e3, 5, 0.1, 0.1, 4.5, 64),
            ("ito5", 20e3, 3, 0.1, 0.01, 1.3, 64), ("ito5", 20e3, 3, 0.1, 0.01, 2.0, 64), ("ito5", 20e3, 3, 0.1, 0.01, 3.0, 64)]
    if quick:
        sims = sims[:2]
    for mk, f_fr, d, u_rms, L, kauth, levels in sims:
        tp, tf = out["motes"][mk]["tau_p_us"] * 1e-6, out["motes"][mk]["tau_F_us"] * 1e-6
        T = 1 / f_fr
        fturb, Sturb, eta, nu0 = turb_norm(u_rms, L, u_rms)
        sel = (fturb > 1e-3) & (fturb < 0.45 * f_fr)
        w_max = kauth * u_rms
        q = 2 * w_max / (2 * levels)
        best = tune(tp, tf, T, d, fturb[sel][::4], Sturb[sel][::4], 1e-6, q)
        r = simulate(tp, tf, T, d, best[1], u_rms, L, u_rms, 1e-6, w_max, levels, n_motes=100 if not quick else 30,
                     dur=6.0 if not quick else 1.0, seed=zlib.crc32(f'{mk}{d}{levels}{kauth}{f_fr}{u_rms}{L}'.encode()) % 100000)
        r.update(mote=mk, f_frame=f_fr, latency_us=d * T * 1e6, u_rms=u_rms, L=L, k_auth=kauth, levels=levels,
                 freq_sigma_um=best[0] * 1e6)
        out["sim"].append(r)
        print(f"  SIM {mk:9s} {f_fr / 1e3:4.1f}kHz lat {d * T * 1e6:3.0f}us u {u_rms} L {L} auth {kauth}x lev {levels}: sigma_x {r['sigma_x_um']:.2f} um "
              f"(freq-domain {best[0] * 1e6:.2f}) r_p99.9 {r['r_p999_um']:.1f} r_max {r['r_max_um']:.0f} um sat {r['sat_frac']:.2e} "
              f"exceed/s {r['first_exceed_rate_per_s']}")
    json.dump(out, open(os.path.join(RES, "rt6_loop.json"), "w"), indent=1, default=float)
    return out



# ----------------------------------------------------------------------------------------------------------------------
# Task 2(iii): flat-top spots vs NA; mode count; MRAF multi-flat-top simulation
# ----------------------------------------------------------------------------------------------------------------------
def flat_top_eta(rho_p, n=512):
    """Band-limited coherent flat-top: for a plateau radius rho_p (units lambda/NA), the m15-equivalent shape
    efficiency eta_eq = I_min(r<=rho_p) * pi rho_p^2 / P_total (m15 writes P = I pi r_c^2 / eta_shape), maximised
    over a soft-edged disk target (erf edge; radius r0, edge width we) filtered by the pupil (cutoff NA/lambda)."""
    span = max(14.0, 7 * rho_p)
    x = (np.arange(n) - n / 2) * span / n
    X, Y = np.meshgrid(x, x)
    R = np.hypot(X, Y)
    dA = (span / n) ** 2
    fx = np.fft.fftfreq(n, span / n)
    FX, FY = np.meshgrid(fx, fx)
    pupil = np.hypot(FX, FY) <= 1.0
    best = (0.0, None, None, None)
    inside = R <= rho_p
    for r0 in rho_p + np.array([-0.2, 0.0, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0]):
        if r0 <= 0:
            continue
        for we in (0.1, 0.2, 0.3, 0.45, 0.6, 0.8):
            A = 0.5 * special.erfc((R - r0) / we)
            I = np.abs(np.fft.ifft2(np.fft.fft2(A) * pupil)) ** 2
            eta = I[inside].min() * math.pi * rho_p ** 2 / (I.sum() * dA)
            if eta > best[0]:
                rip = float(I[inside].max() / I[inside].min() - 1)
                best = (float(eta), float(r0), float(we), rip)
    return best


def mraf(n_spots=60, r_spot=4.0, N=256, pad=2, iters=150, mix=0.5, init="prism", seed=0, quant_bits=8, blur=0.0):
    from scipy.ndimage import gaussian_filter
    """MRAF (Pasienski-DeMarco) for n_spots soft flat-top disks of radius r_spot resolution cells in the Fourier plane
    of an N x N phase-only SLM (uniform illumination). Output grid is padded x pad (1 resolution cell = pad pixels).
    Reports efficiency into the plateaus, plateau rms/min, zero-order fraction."""
    rng = np.random.default_rng(seed)
    M = N * pad
    yy, xx = np.mgrid[0:M, 0:M] - M // 2
    rp = r_spot * pad
    centres = []
    while len(centres) < n_spots:
        c = rng.uniform(-0.42 * M, 0.42 * M, 2)
        if np.hypot(*c) < 6 * rp:
            continue
        if all(np.hypot(*(c - d)) > 2.6 * rp for d in centres):
            centres.append(c)
    T = np.zeros((M, M))
    plate = np.zeros((M, M), bool)
    sig = np.zeros((M, M), bool)
    for c in centres:
        r = np.hypot(xx - c[0], yy - c[1])
        T = np.maximum(T, 0.5 * special.erfc((r - 1.15 * rp) / (0.35 * pad)))
        plate |= r <= rp * 0.9
        sig |= r <= rp * 1.15 + 1.5 * pad
    Ein = np.zeros((M, M))
    sl = slice(M // 2 - N // 2, M // 2 + N // 2)
    Ein[sl, sl] = 1.0
    if init == "prism":
        ph = np.zeros((M, M), complex)
        u = np.arange(M) - M // 2
        U, V = np.meshgrid(u, u)
        for c in centres:
            ph += np.exp(1j * (2 * math.pi * (U * c[0] + V * c[1]) / M + rng.uniform(0, 2 * math.pi)))
        phi = np.angle(ph)
    elif init == "smooth":
        psi = np.zeros((M, M))
        for c in centres:
            r2 = (xx - c[0]) ** 2 + (yy - c[1]) ** 2
            psi = np.where(r2 <= (1.6 * rp) ** 2, 0.5 * math.pi * r2 / rp ** 2 + rng.uniform(0, 2 * math.pi), psi)
        phi = np.angle(np.fft.ifft2(np.fft.ifftshift(T * np.exp(1j * psi))))
    else:
        phi = rng.uniform(0, 2 * math.pi, (M, M))
    Tn = T / math.sqrt((T ** 2).sum())
    for _ in range(iters):
        G = np.fft.fftshift(np.fft.fft2(Ein * np.exp(1j * phi)))
        Gn = G / math.sqrt((np.abs(G) ** 2).sum())
        newG = np.where(sig, mix * Tn * np.exp(1j * np.angle(Gn)), (1 - mix) * Gn)
        phi = np.angle(np.fft.ifft2(np.fft.ifftshift(newG)))
    if quant_bits:
        q = 2 * math.pi / 2 ** quant_bits
        phi = np.round(phi / q) * q
    if blur:
        # fringing field: the LC responds to the WRAPPED phase map (drive voltage) smoothed over ~blur pixels;
        # the fly-back at each 2 pi wrap sends light into the zero order and ghosts
        phi = gaussian_filter(np.mod(phi, 2 * math.pi), blur)
    field = Ein * np.exp(1j * phi)
    I = np.abs(np.fft.fftshift(np.fft.fft2(field))) ** 2
    I /= I.sum()
    Ip = I[plate]
    per = []
    for c in centres:
        m = np.hypot(xx - c[0], yy - c[1]) <= rp * 0.9
        per.append(I[m].mean())
    per = np.array(per)
    loc = []
    for c in centres:
        m = np.hypot(xx - c[0], yy - c[1]) <= rp * 0.9
        v = I[m]
        loc.append(v.std() / v.mean())
    return dict(n_spots=n_spots, r_spot_cells=r_spot, eff_plateau=float(Ip.sum()), eff_signal=float(I[sig].sum()),
                rms_within_spot=float(np.mean(loc)), min_over_mean=float(np.min([I[np.hypot(xx - c[0], yy - c[1]) <= rp * 0.9].min() / p
                                                                               for c, p in zip(centres, per)])),
                spot_to_spot_rms=float(per.std() / per.mean()), zero_order=float(I[M // 2 - pad:M // 2 + pad + 1, M // 2 - pad:M // 2 + pad + 1].sum()),
                cells_per_spot=float(math.pi * r_spot ** 2), slm_px=N * N, spots_per_Mpx=n_spots / (N * N) * 1e6)


def sec_holo():
    out = dict(flat_top=[], designs={}, mraf=[])
    lam = 1.55e-6
    for rho in (0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0):
        eta, r0, we, rip = flat_top_eta(rho)
        out["flat_top"].append(dict(rho_p=rho, eta=eta, r0=r0, edge=we, ripple=rip))
        print(f"HOLO flat-top plateau radius {rho:.2f} lambda/NA: eta_eq {eta:.3f} (target r0 {r0:.2f}, edge {we}, ripple {rip:.2f})")
    ft = out["flat_top"]
    rho80 = next((r["rho_p"] for r in ft if r["eta"] >= 0.8), None)
    # interpolate rho for eta = 0.8
    rr = np.array([r["rho_p"] for r in ft])
    ee = np.array([r["eta"] for r in ft])
    rho80 = float(np.interp(0.8, ee, rr)) if ee.max() >= 0.8 else float("nan")
    out["rho_eta80"] = rho80
    rep = json.load(open(os.path.join(RES, "rt6_repro.json")))
    for case, v in rep.items():
        d = v["rt6_same"]
        rc = d["r_c_um"] * 1e-6
        NA = rho80 * lam / rc
        NA_airy = 0.61 * lam / rc
        M_req = 1.2 * math.pi * NA ** 2 / lam ** 2       # projected field ~1.2 m^2 per head (corner view of the volume)
        out["designs"][case] = dict(r_c_um=rc * 1e6, NA_needed=NA, NA_airy=NA_airy, R_ap_at_4p75m=NA * 4.75,
                                    R_ap_at_3p95m=NA * 3.95, M_dir_m15=d["M_dir"], M_req=M_req, ratio=M_req / d["M_dir"],
                                    px_total_m15=d["px_total"], px_total_req=d["px_total"] * M_req / d["M_dir"],
                                    LCoS4K_per_head=M_req / 8.8e6)
        print(f"  {case}: r_c {rc * 1e6:.0f} um -> NA {NA:.4f} (Airy {NA_airy:.4f}); aperture radius at 3.95/4.75 m "
              f"{NA * 3.95 * 1e3:.0f}/{NA * 4.75 * 1e3:.0f} mm; modes/head {M_req:.2e} vs m15 {d['M_dir']:.2e} (x{M_req / d['M_dir']:.1f}); "
              f"4K LCoS per head {M_req / 8.8e6:.0f}")
    for r_spot in (1.5, 3.0):
        for init in ("random", "smooth"):
            for blur in (0.0, 0.3, 0.6):
                mix = 0.6
                res = mraf(n_spots=40, r_spot=r_spot, N=256, pad=2, iters=120, mix=mix, init=init, seed=1, blur=blur)
                res.update(init=init, mix=mix, fringing_px=blur)
                out["mraf"].append(res)
                print(f"  MRAF r_spot {r_spot} cells ({res['cells_per_spot']:.0f} cells/spot) init {init:6s} fringing {blur}: eff(plateau) "
                      f"{res['eff_plateau']:.2f} eff(signal) {res['eff_signal']:.2f} rms in spot {res['rms_within_spot']:.2f} "
                      f"min/mean {res['min_over_mean']:.2f} spot-to-spot {res['spot_to_spot_rms']:.2f} zero-order {res['zero_order']:.1e}")
    json.dump(out, open(os.path.join(RES, "rt6_holo.json"), "w"), indent=1, default=float)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Task 2(ii): DMD at an intermediate field plane
# ----------------------------------------------------------------------------------------------------------------------
def strokes(S, delta, seed=0):
    """Synthetic line content: random 3D circular arcs (radius 4-20 cm, 60-300 deg) in the 1 x 1 x 0.8 m volume."""
    rng = np.random.default_rng(seed)
    pts = []
    total = 0.0
    while total < S:
        R = rng.uniform(0.04, 0.2)
        ang = math.radians(rng.uniform(60, 300))
        c = CENTER + HALF * rng.uniform(-0.8, 0.8, 3)
        nrm = rng.normal(size=3)
        nrm /= np.linalg.norm(nrm)
        e1 = np.cross(nrm, [0.3, 0.5, 0.8])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(nrm, e1)
        n = max(2, int(R * ang / delta))
        t = np.linspace(0, ang, n)
        p = c + R * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2)
        p = np.clip(p, CENTER - HALF, CENTER + HALF)
        pts.append(p)
        total += R * ang
    return np.vstack(pts)


def crosstalk(P, head, NA, r_c, n_planes=1):
    h = np.asarray(head, float)
    ax = (CENTER - h) / np.linalg.norm(CENTER - h)
    e1 = np.cross(ax, [0, 0, 1.0]) if abs(ax[2]) < 0.9 else np.cross(ax, [1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    rel = P - h
    dep = rel @ ax
    d_lo, d_hi = dep.min(), dep.max()
    planes = d_lo + (np.arange(n_planes) + 0.5) * (d_hi - d_lo) / n_planes
    pl = planes[np.argmin(np.abs(dep[:, None] - planes[None, :]), axis=1)]
    q = np.stack([rel @ e1, rel @ e2], 1) * (pl / dep)[:, None]
    rho = NA * np.abs(dep - pl) + r_c
    from scipy.spatial import cKDTree
    over = np.zeros(len(P), int)
    for k in np.unique(pl):
        idx = np.where(pl == k)[0]
        tr = cKDTree(q[idx])
        rmax = rho[idx].max()
        pairs = tr.query_pairs(2 * rmax, output_type="ndarray")
        if len(pairs):
            i, j = idx[pairs[:, 0]], idx[pairs[:, 1]]
            hit = np.linalg.norm(q[i] - q[j], axis=1) < rho[i] + rho[j]
            np.add.at(over, i[hit], 1)
            np.add.at(over, j[hit], 1)
    return dict(frac_overlapped=float(np.mean(over > 0)), mean_overlaps=float(over.mean()),
                footprint_mm_p50=float(np.median(rho) * 1e3), footprint_mm_max=float(rho.max() * 1e3),
                depth_span_m=float(d_hi - d_lo))


def sec_dmd():
    out = dict(cases=[], etendue={})
    lam = 1.55e-6
    hol = json.load(open(os.path.join(RES, "rt6_holo.json")))
    rho80 = hol["rho_eta80"]
    # DLP650LNIR: 1280 x 800, 10.8 um, +-12 deg tilt (TI datasheet); usable NA at the DMD ~ sin(12 deg)
    A_dmd = 1280 * 800 * (10.8e-6) ** 2
    NA_dmd = math.sin(math.radians(12))
    E_dmd = A_dmd * math.pi * NA_dmd ** 2
    for case, S, delta, rc in (("a_sketch_ito5", 5.0, 3e-3, 86e-6), ("b_film_ito5", 30.0, 3e-3, 35e-6),
                               ("c_sketch_carbonW10", 5.0, 3e-3, 61e-6)):
        P = strokes(S, delta, seed=2)
        for rho in (1.0, rho80):
            NA = rho * lam / rc
            E_req = 1.2 * math.pi * NA ** 2
            out["etendue"][f"{case}_rho{rho:.2f}"] = dict(NA=NA, E_req=E_req, E_dmd=E_dmd, dmds_per_head=E_req / E_dmd,
                                                         mirror_mm_single_dmd=1.2 / 1280 * 1e3)
            for head_name, head in (("corner", H10[0]), ("floor", H10[9])):
                for npl in (1, 4, 16):
                    r = crosstalk(P, head, NA, rc, npl)
                    r.update(case=case, head=head_name, n_planes=npl, NA=NA, rho=rho, N=len(P))
                    out["cases"].append(r)
                    print(f"DMD {case:18s} rho {rho:.2f} {head_name:6s} N {len(P):5d} NA {NA:.4f} planes {npl:2d}: overlapped "
                          f"{100 * r['frac_overlapped']:5.1f}% mean overlaps {r['mean_overlaps']:.1f}, footprint p50 "
                          f"{r['footprint_mm_p50']:.2f} mm max {r['footprint_mm_max']:.1f} mm (one-DMD mirror = 0.94 mm)")
            print(f"  etendue (rho {rho:.2f}): required {E_req:.2e} m^2 sr per head vs one DLP650LNIR {E_dmd:.2e} -> {E_req / E_dmd:.0f} DMDs per head")
    json.dump(out, open(os.path.join(RES, "rt6_dmd.json"), "w"), indent=1, default=float)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Task 2(v): Mie (own BHMIE) and coated/white estimates
# ----------------------------------------------------------------------------------------------------------------------
def bhmie(x, m, theta):
    """Bohren & Huffman BHMIE (downward log-derivative recurrence). theta in rad. Returns Qext, Qsca, Qback, S1, S2."""
    nstop = int(x + 4 * x ** (1 / 3) + 2)
    y = m * x
    nmx = int(max(nstop, abs(y)) + 16)
    D = np.zeros(nmx + 1, complex)
    for n in range(nmx, 0, -1):
        D[n - 1] = n / y - 1 / (D[n] + n / y)
    mu_ = np.cos(theta)
    pi0, pi1 = np.zeros_like(mu_), np.ones_like(mu_)
    S1 = np.zeros_like(mu_, complex)
    S2 = np.zeros_like(mu_, complex)
    psi0, psi1 = math.cos(x), math.sin(x)
    chi0, chi1 = -math.sin(x), math.cos(x)
    xi1 = complex(psi1, -chi1)
    qsca = qext = 0.0
    qb = 0j
    an1 = bn1 = 0j
    for n in range(1, nstop + 1):
        fn = (2 * n + 1) / (n * (n + 1))
        psi = (2 * n - 1) * psi1 / x - psi0
        chi = (2 * n - 1) * chi1 / x - chi0
        xi = complex(psi, -chi)
        an = ((D[n] / m + n / x) * psi - psi1) / ((D[n] / m + n / x) * xi - xi1)
        bn = ((D[n] * m + n / x) * psi - psi1) / ((D[n] * m + n / x) * xi - xi1)
        qsca += (2 * n + 1) * (abs(an) ** 2 + abs(bn) ** 2)
        qext += (2 * n + 1) * (an.real + bn.real)
        qb += (2 * n + 1) * (-1) ** n * (an - bn)
        pi_ = pi1
        tau = n * mu_ * pi_ - (n + 1) * pi0
        S1 += fn * (an * pi_ + bn * tau)
        S2 += fn * (an * tau + bn * pi_)
        psi0, psi1 = psi1, psi
        chi0, chi1 = chi1, chi
        xi1 = complex(psi1, -chi1)
        pi1 = ((2 * n + 1) * mu_ * pi_ - (n + 1) * pi0) / n
        pi0 = pi_
    return 2 * qext / x ** 2, 2 * qsca / x ** 2, abs(qb) ** 2 / x ** 2, S1, S2


def mg(eps_i, f):
    """Maxwell-Garnett effective permittivity, spherical inclusions eps_i in air at volume fraction f."""
    b = (eps_i - 1) / (eps_i + 2)
    return (1 + 2 * f * b) / (1 - f * b)


def q_iso_profile(a, lam, m, angles_deg=(30, 60, 90, 120, 150, 170), halfwidth=5.0):
    x = 2 * math.pi * a / lam
    th = np.radians(np.linspace(0.05, 179.95, 7200))
    Qe, Qs, Qb, S1, S2 = bhmie(x, m, th)
    qiso = 2 * (np.abs(S1) ** 2 + np.abs(S2) ** 2) / x ** 2          # 4 pi (dC/dOmega) / (pi a^2)
    prof = {}
    for ang in angles_deg:
        sel = np.abs(np.degrees(th) - ang) <= halfwidth
        prof[str(ang)] = float(qiso[sel].mean())
    w = np.sin(th)
    side = (np.degrees(th) >= 30) & (np.degrees(th) <= 150)
    frac_side = float(np.trapezoid((qiso * w)[side], th[side]) / 2)    # fraction of pi a^2 I scattered into 30-150 deg
    return dict(x=x, m=str(m), Qext=Qe, Qsca=Qs, Qback=Qb, q_iso=prof, q_side_30_150=frac_side,
                q_iso_mean_30_150=float(np.trapezoid((qiso * w)[side], th[side]) / np.trapezoid(w[side], th[side])))


def lambert_sphere_q(R, phase_deg):
    """Isotropic-equivalent q for a diffuse (Lambertian) sphere of albedo R at phase angle alpha = 180 - scattering
    angle: p(alpha) = 8/(3 pi) [sin a + (pi - a) cos a] (normalised to 1 over 4 pi)."""
    al = math.radians(phase_deg)
    return R * 8 / (3 * math.pi) * (math.sin(al) + (math.pi - al) * math.cos(al))


def sec_mie():
    out = dict(validation={}, cases={}, white={}, luminance={})
    th = np.radians([0.0, 90.0, 180.0])
    Qe, Qs, Qb, *_ = bhmie(5.213, complex(1.55, 0.0), th)
    out["validation"]["BH_x5.213_m1.55"] = dict(Qext=Qe, Qsca=Qs, Qback=Qb, ref=dict(Qext=3.1054, Qsca=3.1054, Qback=2.9253))
    Qe2, Qs2, *_ = bhmie(300.0, complex(1.5, 0.01), th)
    out["validation"]["large_x"] = dict(Qext=Qe2, ref="-> 2")
    print(f"MIE validation: BH test Qext {Qe:.4f} (3.1054) Qback {Qb:.4f} (2.9253); x=300 Qext {Qe2:.3f} (->2)")
    lam = 500e-9
    gc500 = complex(1.95, 0.79)                    # light-absorbing / glassy carbon at ~500-550 nm [memory: Bond & Bergstrom 2006]
    eff_c = np.sqrt(mg(gc500 ** 2, 0.05))
    cases = {
        "ito_aerogel_5um": (5e-6, complex(1.04, 1e-4)),
        "ito_aerogel_1um": (1e-6, complex(1.04, 1e-4)),
        "ito_aerogel_1.5um": (1.5e-6, complex(1.04, 1e-4)),
        "carbon_aerogel_MG_5um": (5e-6, complex(eff_c.real, eff_c.imag)),
        "carbon_aerogel_MG_10um": (10e-6, complex(eff_c.real, eff_c.imag)),
        "dense_black_carbon_5um": (5e-6, gc500),
        "dense_black_carbon_10um": (10e-6, gc500),
        "solid_silica_1um": (1e-6, complex(1.46, 0)),
        "solid_TiO2_1um": (1e-6, complex(2.6, 0)),
    }
    for k, (a, m) in cases.items():
        r = q_iso_profile(a, lam, m)
        out["cases"][k] = r
        print(f"  {k:24s} m={m.real:.3f}+{m.imag:.4f}i x={r['x']:.0f}: Qsca {r['Qsca']:.2f}; q_iso(deg) " +
              " ".join(f"{a_}:{v:.3g}" for a_, v in r["q_iso"].items()) + f" | frac into 30-150 deg {r['q_side_30_150']:.3g}")
    for R in (0.1, 0.3, 0.6):
        out["white"][str(R)] = {str(al): lambert_sphere_q(R, al) for al in (0, 30, 60, 90, 120, 150, 170)}
    print("  Lambertian white coat q_iso vs phase angle (0 = viewer beside the illuminating head): " +
          "; ".join(f"R={R}: " + " ".join(f"{k}:{v:.2f}" for k, v in d.items()) for R, d in out["white"].items()))
    # KM reflectance of a non-absorbing shell of thickness t on a black core: R = St/(1+St), S ~ 0.75/l*
    out["white"]["KM"] = {f"t{t}_l{l}": (0.75 * t / l) / (1 + 0.75 * t / l) for t in (0.5, 1.0, 2.0) for l in (0.5, 1.0, 3.0, 10.0)}
    # luminance check for the m15 cases: visible spot power needed with Mie q instead of q_side = 0.3
    rep = json.load(open(os.path.join(RES, "rt6_repro.json")))
    for case, v in rep.items():
        d = v["rt6_same"]
        a = d["a_um"] * 1e-6
        key = "ito_aerogel_5um" if "ito" in case else "carbon_aerogel_MG_10um"
        qm = out["cases"][key]["q_iso"]["90"]
        need = d["P_vis_spot_uW"] * 0.3 / qm
        dot_arcmin_1m = 3e-3 / 1.0 * 180 / math.pi * 60
        out["luminance"][case] = dict(q_m15=0.3, q_mie_90=qm, P_vis_spot_uW_m15=d["P_vis_spot_uW"], P_vis_spot_uW_uncoated=need,
                                      within_class1_uncoated=need <= 390, dot_spacing_arcmin_at_1m=dot_arcmin_1m,
                                      I_v_cd=d["phi_mote_lm"] / (4 * math.pi))
        print(f"  {case}: q(90deg) uncoated {qm:.2e} -> visible spot {need / 1e3:.3g} mW (m15 {d['P_vis_spot_uW'] / 1e3:.3f} mW at q=0.3); "
              f"dots at 3 mm = {dot_arcmin_1m:.1f} arcmin at 1 m; I_v per dot {d['phi_mote_lm'] / (4 * math.pi):.2e} cd")
    json.dump(out, open(os.path.join(RES, "rt6_mie.json"), "w"), indent=1, default=lambda o: str(o))
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Task 2(iv): mote properties
# ----------------------------------------------------------------------------------------------------------------------
def sec_mote():
    out = dict(alpha={}, fom_band=[], hot_face={})
    lam = 1.55e-6
    # carbon at 1550 nm: glassy/amorphous carbon n ~ 2.3-2.7, k ~ 0.8-1.2 [memory]; 5 % solid
    for nk in ((2.3, 0.8), (2.5, 1.0), (2.7, 1.2)):
        m = complex(*nk)
        a_bulk = 4 * math.pi * nk[1] / lam
        e_eff = mg(m ** 2, 0.05)
        n_eff = np.sqrt(e_eff)
        out["alpha"][f"n{nk[0]}_k{nk[1]}"] = dict(alpha_bulk=a_bulk, alpha_5pct_linear=0.05 * a_bulk,
                                                 alpha_MG=4 * math.pi * n_eff.imag / lam, n_eff=str(n_eff))
    out["alpha"]["literature_MEC"] = "carbon aerogel IR mass extinction 2.62 m^2/g (3-5 um), 1.23 m^2/g (8-14 um); x 100 kg/m^3 -> 2.6e5 /m"
    print("MOTE alpha(1550) for 5 % carbon: " + "; ".join(f"{k}: linear {v['alpha_5pct_linear']:.2e}, MG {v['alpha_MG']:.2e}"
                                                         for k, v in out["alpha"].items() if isinstance(v, dict)))
    for a in (5e-6, 10e-6):
        for alpha in (1.2e5, 2e5, 3e5, 4.5e5):
            jA, A = j1A_abs(alpha * a)
            for k in (0.03, 0.045, 0.055, 0.08):
                for coat in (False, True):
                    j = jA * (0.9 if coat else 1.0)
                    out["fom_band"].append(dict(a_um=a * 1e6, alpha=alpha, k=k + (0.01 if coat else 0), white=coat, j1A=j, A=A,
                                                FOM=j / (k + (0.01 if coat else 0) + 2 * kg(T0))))
    fb = [r["FOM"] for r in out["fom_band"] if r["a_um"] == 10 and r["white"]]
    fb5 = [r["FOM"] for r in out["fom_band"] if r["a_um"] == 5 and r["white"]]
    out["fom_white10_range"] = (min(fb), max(fb))
    out["fom_white5_range"] = (min(fb5), max(fb5))
    print(f"  white-coated carbon FOM band: a=10 um {min(fb):.2f}-{max(fb):.2f}; a=5 um {min(fb5):.2f}-{max(fb5):.2f}")
    # hot face: T_face ~ T_m + 1.33 T1, T1 = J1 I a/(k_p + 2 k_g(T_f)) for the net push (RT5: 1.33 x T1 for a uniform push)
    rep = json.load(open(os.path.join(RES, "rt6_repro.json")))
    for case, v in rep.items():
        d = v["rt6_same"]
        M = mote(d["mote"], d["a_um"] * 1e-6)
        Tm = T0 + d["dT"]
        T1 = M["j1A"] * M["A"] * d["I_hold"] * d["a_um"] * 1e-6 / (M["k"] + 2 * kg(0.5 * (T0 + Tm)))
        Tocc = T0 + v["rt6_occluded"]["dT"]
        out["hot_face"][case] = dict(Tm=Tm, T1=T1, T_face=Tm + 1.33 * T1, T_face_occluded=Tocc + 1.33 * T1 * 4.47 / 2.14 * 0 + 1.33 * T1)
        print(f"  {case}: T_m {Tm:.0f} K, T1 {T1:.0f} K -> hot face ~{Tm + 1.33 * T1:.0f} K; occluded mean {Tocc:.0f} K, face ~{Tocc + 1.33 * T1:.0f} K")
    json.dump(out, open(os.path.join(RES, "rt6_mote.json"), "w"), indent=1, default=str)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Task 2(vi) stray light and 2(vii) safety arithmetic; receiver geometry and bystander trips
# ----------------------------------------------------------------------------------------------------------------------
ROOM_BOX = (6.0, 5.0, 2.8)


def ray_exit(p, d):
    """Distance along unit d from p (inside the room box) to the box boundary."""
    t = []
    for i, L in enumerate(ROOM_BOX):
        if d[i] > 1e-12:
            t.append((L - p[i]) / d[i])
        elif d[i] < -1e-12:
            t.append(-p[i] / d[i])
    return min(t)


def sec_stray():
    out = dict(cases={}, receivers={}, air={})
    rep = json.load(open(os.path.join(RES, "rt6_repro.json")))
    mie = json.load(open(os.path.join(RES, "rt6_mie.json")))
    Vlm = 683 * V500
    for case, v in rep.items():
        d = v["rt6_same"]
        L, S, _ = CONTENT[d["content"]]
        Phi = 4 * math.pi * L * 1e-3 * S
        Pv = d["P_vis_W"]
        leak = 1e-3
        Lw = 0.8 * leak * Pv * Vlm / (math.pi * 50)
        old = leak * Pv * Vlm / Phi
        L_img = 0.8 * Phi / (math.pi * 50)
        # air scatter of the visible beams over ~4 m path: Rayleigh 1.4e-5 /m (500 nm) + indoor aerosol 2e-5..1e-4 /m
        frac_air = [4.0 * (1.4e-5 + b) for b in (2e-5, 1e-4)]
        Pair = [Pv * f * Vlm for f in frac_air]
        # glow luminance seen through the converging bundle near the image: E ~ P_vis/(1 m^2), 1 m path, isotropic
        Lglow = [Pv / 1.0 * (1.4e-5 + b) * 1.0 / (4 * math.pi) * Vlm for b in (2e-5, 1e-4)]
        # dust sparkle: particles > 1 um, 1e5-1e7 /m^3, in the bright part of each visible spot (I > I_vis/10)
        rv = d["r_v_um"] * 1e-6
        NA_v = 0.61 * 500e-9 / rv * 1.5
        Vbright = math.pi * (math.sqrt(10) * rv) ** 2 * 2 * (math.sqrt(10) * rv / NA_v)
        dust = [n * Vbright * d["N"] for n in (1e5, 1e6, 1e7)]
        out["cases"][case] = dict(P_vis_W=Pv, Phi_image_lm=Phi, L_wall_leak=Lw, L_wall_image_itself=L_img, old_rule_ratio=old,
                                  old_rule_pass=old <= 0.05, air_scatter_lm=Pair, air_scatter_frac_of_image=[p / Phi for p in Pair],
                                  glow_cd_m2=Lglow, dust_sparkles=dust, receiver_glow_cd_m2_small=leak * Pv * Vlm / (math.pi * 0.28),
                                  receiver_glow_cd_m2_4m2=leak * Pv * Vlm / (math.pi * 4.0))
        print(f"STRAY {case}: P_vis {Pv:.2f} W ({Pv * Vlm:.0f} lm) vs image {Phi:.3f} lm; leak 1e-3 -> L_wall {Lw:.1e} cd/m2 "
              f"(image's own flux adds {L_img:.1e}); old 5% rule: {100 * old:.0f} % of image flux -> {'pass' if old <= 0.05 else 'FAIL'}; "
              f"air scatter {Pair[0]:.3f}-{Pair[1]:.3f} lm = {100 * Pair[0] / Phi:.0f}-{100 * Pair[1] / Phi:.0f} % of image flux; "
              f"dust sparkles {dust[0]:.1f}/{dust[1]:.0f}/{dust[2]:.0f}")
    # receiver landing zones for H10: where do the beams through the image volume end?
    corners = np.array([CENTER + HALF * np.array([sx, sy, sz]) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
    rng = np.random.default_rng(5)
    vol = CENTER + HALF * rng.uniform(-1, 1, (400, 3))
    for i, h in enumerate(H10):
        h = np.asarray(h, float)
        ends = []
        for p in vol:
            dvec = (p - h) / np.linalg.norm(p - h)
            ends.append(p + dvec * ray_exit(p, dvec))
        ends = np.array(ends)
        span = ends.max(0) - ends.min(0)
        dims = sorted(span)[-2:]
        out["receivers"][f"head{i}"] = dict(pos=h.tolist(), landing_span_m=span.tolist(), area_m2_bbox=float(dims[0] * dims[1]))
    areas = [r["area_m2_bbox"] for r in out["receivers"].values()]
    print(f"  H10 receiver landing zones (bounding box of beam ends through the volume): {min(areas):.1f}-{max(areas):.1f} m^2 per head")
    json.dump(out, open(os.path.join(RES, "rt6_stray.json"), "w"), indent=1, default=float)
    return out


def bystander_trips(NA, n_view=6, R_view=1.2, head_h=1.6, head_r=0.12, torso=True, seed=4):
    """Fraction of (mote, head) trap beams whose post-focus continuation (cone NA) is cut by a bystander standing
    around the image (head sphere + torso cylinder)."""
    rng = np.random.default_rng(seed)
    P = CENTER + HALF * rng.uniform(-1, 1, (300, 3))
    ang = np.linspace(0, 2 * math.pi, n_view, endpoint=False) + 0.3
    viewers = [np.array([CENTER[0] + R_view * math.cos(t), CENTER[1] + R_view * math.sin(t)]) for t in ang]
    hit = 0
    tot = 0
    mote_cut = np.zeros(len(P), bool)
    for h in H10:
        h = np.asarray(h, float)
        for ip, p in enumerate(P):
            dvec = (p - h) / np.linalg.norm(p - h)
            s = np.linspace(0.02, ray_exit(p, dvec), 300)
            pts = p + s[:, None] * dvec
            rad = NA * s
            cut = False
            for vxy in viewers:
                rxy = np.hypot(pts[:, 0] - vxy[0], pts[:, 1] - vxy[1])
                head = np.hypot(rxy, pts[:, 2] - head_h) < head_r + rad
                body = (rxy < 0.2 + rad) & (pts[:, 2] < 1.45) & (pts[:, 2] > 0.0) if torso else np.zeros_like(head)
                if np.any(head | body):
                    cut = True
                    break
            hit += cut
            mote_cut[ip] |= cut
            tot += 1
    return hit / tot, float(mote_cut.mean())


def sec_safety():
    out = dict(cases={})
    rep = json.load(open(os.path.join(RES, "rt6_repro.json")))
    mie = json.load(open(os.path.join(RES, "rt6_mie.json")))
    t = 1.4e-3
    A35 = math.pi * (3.5e-3 / 2) ** 2
    A1 = math.pi * (1e-3 / 2) ** 2
    A7 = math.pi * (7e-3 / 2) ** 2
    for case, v in rep.items():
        d = v["rt6_same"]
        Pf = d["P_focus_mW"] * 1e-3
        Pv = d["P_vis_spot_uW"] * 1e-6
        a = d["a_um"] * 1e-6
        rc = d["r_c_um"] * 1e-6
        r = dict(P_focus_mW=Pf * 1e3, undetected_mW=0.02 * Pf * 1e3, undetected_vs_AEL=0.02 * Pf / AEL_1550,
                 E_cut_mJ=Pf * t * 1e3,
                 limit_m15_mJ=1e3 * A35 * 1e3, limit_1mm_0p1Jcm2_mJ=1e3 * A1 * 1e3, limit_1mm_1Jcm2_mJ=1e4 * A1 * 1e3,
                 skin_limit_mJ=0.56e4 * t ** 0.25 * A35 * 1e3,
                 vis_spot_mW=Pv * 1e3, vis_E_cut_uJ=Pv * t * 1e6, vis_limit_uJ=18 * t ** 0.75 * A7 * 1e6,
                 vis_spots_in_pupil=1 + 7.0 / 3.0, vis_sum_in_pupil_mW=Pv * (1 + 7.0 / 3.0) * 1e3,
                 mote_extinction_frac=2 * math.pi * a * a / (math.pi * rc * rc / 0.8))
        out["cases"][case] = r
        print(f"SAFETY {case}: P_focus {Pf * 1e3:.1f} mW, undetected 2% {0.02 * Pf * 1e3:.2f} mW ({100 * 0.02 * Pf / AEL_1550:.0f}% of 10 mW); "
              f"cut dose {Pf * t * 1e3:.3f} mJ vs m15 limit {1e3 * A35 * 1e3:.2f} mJ (3.5 mm, 0.1 J/cm2), 1-mm aperture "
              f"{1e3 * A1 * 1e3:.3f}/{1e4 * A1 * 1e3:.2f} mJ (0.1/1 J/cm2); 500 nm spot {Pv * 1e3:.3f} mW, cut {Pv * t * 1e6:.2f} uJ vs "
              f"{18 * t ** 0.75 * A7 * 1e6:.2f} uJ; ~{1 + 7 / 3:.1f} spots in a 7 mm pupil = {Pv * (1 + 7 / 3) * 1e3:.2f} mW; "
              f"mote's own extinction {100 * r['mote_extinction_frac']:.1f}% of its beam")
    for nv in (1, 2, 6):
        for NA in (0.005, 0.05):
            fr, fm = bystander_trips(NA, n_view=nv)
            out[f"bystander_trip_frac_n{nv}_NA{NA}"] = fr
            out[f"bystander_motes_losing_a_head_n{nv}_NA{NA}"] = fm
            print(f"  bystanders ({nv} people at 1.2 m): {100 * fr:.0f}% of (mote, head) trap beams cut downstream of the focus, "
                  f"{100 * fm:.0f}% of motes lose >= 1 head (NA {NA})")
    json.dump(out, open(os.path.join(RES, "rt6_safety.json"), "w"), indent=1, default=float)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Scope addition: M16 fast POV (LCSV-P)
# ----------------------------------------------------------------------------------------------------------------------
def pov(content, a, v, room_u, f=60.0, f_bw=5e3, ff=0.02, hw=2.14, hm=1.38, Tmax=573.0, q=0.3, r_c_floor=0.0,
        eta_shape=0.8, u_heat=None, occluded=False, M=None):
    L, S, duty = CONTENT[content]
    M = M or dict(MOTES["ito_aerogel"])
    if occluded:
        hw = 4.47
    N = S * f / (v * duty)
    uh = room_u if u_heat is None else u_heat

    def resid(Tm, w):
        Tf = 0.5 * (T0 + Tm)
        F = 1.3 * drag(a, w, Tf)
        Pabs = F / pp_force(a, 1.0, M["k"], M["j1A"], Tm, 0.85) * M["A"] * math.pi * a * a
        return heat_loss(Tm, a, w) - hw * Pabs, Pabs
    Tm = optimize.brentq(lambda T: resid(T, v + uh)[0], T0 + 1e-3, 4000.0)
    Tp = optimize.brentq(lambda T: resid(T, v + room_u)[0], T0 + 1e-3, 4000.0)
    Pabs = resid(Tp, v + room_u)[1]
    I = Pabs / (M["A"] * math.pi * a * a)
    err = (room_u + ff * v) / (2 * math.pi * f_bw)
    r_c = max(3 * err, 3 * a, r_c_floor)
    Pu = I * math.pi * r_c ** 2 / eta_shape
    Phi = 4 * math.pi * L * 1e-3 * S
    phi_m = Phi / (N * duty)
    Psc = phi_m / (683 * V500)
    r_v = max(2 * err, 1.5 * a)
    Pvs = Psc / (q * math.pi * a * a) * math.pi * r_v ** 2 / 0.8
    return dict(content=content, a_um=a * 1e6, v=v, u=room_u, N=N, channels_m16=4 * N, dT=Tm - T0, T_m=Tm, heat_fail=Tm > Tmax,
                I_hold=I, err_um=err * 1e6, r_c_um=r_c * 1e6, P_focus_mW=hw * Pu * 1e3, P_ir_W=N * hm * Pu, P_vis_spot_mW=Pvs * 1e3,
                P_vis_W=N * Pvs, phi_m=phi_m)


def sec_m16():
    out = dict(rows={}, attacks={})
    m16 = json.load(open(os.path.join(RES, "m16_fast_pov.json")))
    mie = json.load(open(os.path.join(RES, "rt6_mie.json")))
    hol = json.load(open(os.path.join(RES, "rt6_holo.json")))
    lam = 1.55e-6
    sel = [("sketch", "quiet", 1.0, 1.0), ("sketch", "normal", 1.0, 0.5), ("film_density", "normal", 1.5, 0.5),
           ("film_density", "quiet", 1.0, 1.0)]
    for content, room, a_um, v in sel:
        ref = next(r for r in m16 if (r["content"], r["room"], r["a_um"], r["v"]) == (content, room, a_um, v))
        mine = pov(content, a_um * 1e-6, v, ROOMS[room])
        occ = pov(content, a_um * 1e-6, v, ROOMS[room], occluded=True)
        key = f"{content}_{room}_a{a_um}_v{v}"
        comp = {k: dict(m16=ref[k2], rt6=mine[k], dev=mine[k] / ref[k2] - 1) for k, k2 in
                (("N", "N"), ("dT", "dT"), ("err_um", "err_um"), ("r_c_um", "r_c_um"), ("P_focus_mW", "P_focus_mW"),
                 ("P_ir_W", "P_ir_W"), ("P_vis_spot_mW", "P_vis_spot_mW"), ("P_vis_W", "P_vis_W"))}
        comp["occluded_dT"] = dict(m16=ref["occluded_dT"], rt6=occ["dT"], dev=occ["dT"] / ref["occluded_dT"] - 1)
        out["rows"][key] = dict(compare=comp, occluded_heat_fail=occ["heat_fail"], m16_occluded_fails=ref["occluded_fails"])
        print(f"M16 {key}: " + "; ".join(f"{k} {v_['m16']:.4g}/{v_['rt6']:.4g} ({100 * v_['dev']:+.1f}%)" for k, v_ in comp.items())
              + f" | occluded heat fail rt6 {occ['heat_fail']} (m16 {ref['occluded_fails']})")
    # attack 1: diffraction-limited flat-top radius at H10 throws (R_head 0.3 m)
    ft = {round(r["rho_p"], 2): r["eta"] for r in hol["flat_top"]}
    att = {}
    for rho in (1.0, 3.0):
        for d in (1.25, 3.95, 4.75):
            att[f"rc_min_rho{rho}_d{d}"] = rho * lam * d / 0.3 * 1e6
    out["attacks"]["diffraction_rc_min_um"] = att
    print("  diffraction-limited plateau radius (um), R_head 0.3 m: " + ", ".join(f"{k} {v:.0f}" for k, v in att.items()))
    # attack 2: achievable loop bandwidth vs latency for a 1-um mote (tau_p 2 us, tau_F 0.4 us), 100 kHz actuation
    tp, tf = mote_times(1e-6, 150.0, 800.0, 0.04)
    bw = {}
    f, S, eta, nu0 = turb_norm(0.1, 0.01, 0.1)
    for lat in (10e-6, 20e-6, 50e-6, 100e-6, 150e-6, 250e-6):
        T = 10e-6
        d = int(round(lat / T))
        s_ = (f > 1e-3) & (f < 4e4)
        best = tune(tp, tf, T, d, f[s_][::4], S[s_][::4], 0.2e-6, 1e-4)
        fc = crossover_hz(plant_resp(tp, tf, T, d, f[s_][::4]), best[1])
        bw[f"{lat * 1e6:.0f}us"] = fc
    out["attacks"]["loop_crossover_Hz_vs_latency_noise_optimal"] = bw
    # maximum crossover with modulus margin <= 2 (P-only, exact discrete plant) vs analytic 1/(8 tau) (PM 45 deg)
    bwmax = {}
    for lat in (10e-6, 20e-6, 50e-6, 100e-6, 150e-6, 250e-6):
        T = 5e-6
        d = int(round(lat / T))
        pr = plant_resp(tp, tf, T, d, np.array([1.0, 10.0]))
        best = 0.0
        for kp in np.logspace(2, 6, 160):
            L = kp * pr["Pw"]
            if np.max(np.abs(1 / (1 + L))) <= 2.0 and stable(pr, (kp, 0.0, 0.0)):
                best = max(best, crossover_hz(pr, (kp, 0.0, 0.0)))
        bwmax[f"{lat * 1e6:.0f}us"] = dict(f_c_max=best, analytic=1 / (8 * (lat + T / 2)))
    out["attacks"]["loop_crossover_max_Hz"] = bwmax
    print("  max P-loop crossover (Ms<=2) vs latency: " + ", ".join(f"{k}: {v['f_c_max']:.0f} Hz (1/8tau {v['analytic']:.0f})" for k, v in bwmax.items()))
    print("  1-um mote loop crossover vs total latency: " + ", ".join(f"{k}: {v:.0f} Hz" for k, v in bw.items()))
    # attack 3/5: corrected rows (lenient flat-top rho=1 at the corner throw, eta 0.56; camera latency 150 us;
    # q from a plausible coated 1-um mote; 6 beams per mote; u_heat for turbulence peaks)
    f_c150 = bwmax["150us"]["f_c_max"]
    q_unc = mie["cases"]["ito_aerogel_1um"]["q_iso"]["90"]
    corr = {}
    for content, room, a_um, v in sel:
        u = ROOMS[room]
        for label, kw in (("m16_as_is", {}),
                          ("diffraction_rho1", dict(r_c_floor=1.0 * lam * 3.95 / 0.3, eta_shape=0.56)),
                          ("+latency150us", dict(r_c_floor=1.0 * lam * 3.95 / 0.3, eta_shape=0.56, f_bw=f_c150)),
                          ("+turb_peaks(sigma=u)", dict(r_c_floor=1.0 * lam * 3.95 / 0.3, eta_shape=0.56, f_bw=f_c150, u_heat=5.4 * u))):
            r = pov(content, a_um * 1e-6, v, u, **kw)
            r["channels_rt6"] = 6.5 * r["N"]
            r["P_vis_spot_uncoated_mW"] = r["P_vis_spot_mW"] * 0.3 / q_unc
            corr[f"{content}_{room}_a{a_um}_v{v}|{label}"] = r
            print(f"  {content:12s} {room:6s} a {a_um} v {v} {label:22s}: r_c {r['r_c_um']:5.1f} um, T_m {r['T_m']:4.0f} K "
                  f"{'HEAT' if r['heat_fail'] else 'ok  '}, P_focus {r['P_focus_mW']:6.1f} mW, P_IR {r['P_ir_W']:7.1f} W, vis spot "
                  f"{r['P_vis_spot_mW']:.2f} mW (uncoated {r['P_vis_spot_uncoated_mW']:.0f} mW), channels {r['N'] * 4:.0f} -> {r['channels_rt6']:.0f}")
    out["corrected"] = corr
    out["attacks"]["q_uncoated_1um_90deg"] = q_unc
    json.dump(out, open(os.path.join(RES, "rt6_m16.json"), "w"), indent=1, default=float)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Corrected LCSV table
# ----------------------------------------------------------------------------------------------------------------------
def sec_table():
    out = {}
    hol = json.load(open(os.path.join(RES, "rt6_holo.json")))
    ft = {round(r["rho_p"], 2): r["eta"] for r in hol["flat_top"]}
    loop = json.load(open(os.path.join(RES, "rt6_loop.json")))
    # r_c floor from the loop model: NIR DMD (12.5 kHz binary), 160-240 us latency, u_rms 0.1, L 1 cm; scaled with authority
    fl = {r["mote"]: r["binary"]["r_c_needed_um"] for r in loop["freq"]
          if r["f_frame"] == 12.5e3 and r["latency_us"] > 200 and r["u_rms"] == 0.1 and r["L"] == 0.01}
    ito_w = dict(MOTES["ito_aerogel"], j1A=0.486 * 0.9, k=0.055, Tmax=573.0)       # white-coated ITO mote, m15 coat penalty
    rooms = {"still (U 0, sigma 0.03)": (0.03 * 5.4, 0.03 * 3.1, 0.03),
             "quiet office (U 0.1, sigma 0.03)": (0.1 + 0.03 * 5.4, 0.1 + 0.03 * 3.1, 0.03),
             "turbulent quiet (U 0, sigma 0.1)": (0.1 * 5.4, 0.1 * 3.1, 0.1)}
    rho, eta_eq = 1.0, ft[1.0]
    mf = 1.2 * math.pi ** 2 * rho ** 2
    for case, c in CASES.items():
        base = lcsv(**c)
        out[f"{case}|m15 model (rt6 optimum)"] = base
        Mx = dict(ito_w) if "ito" in case else None
        for rname, (u_heat, u_pow, sig) in rooms.items():
            a = c["a"]
            q_auth = 5.4 * sig / 0.45
            mk = "ito5" if "ito" in case else "carbonW10"
            rmin = max(a + (fl[mk] * 1e-6 - a) * max(q_auth, 0.3), 3 * a)
            M = Mx or mote(c["mote_name"], a)
            Ht = holding(a, M, u_heat, LAYOUT_M15["H10"]["h_worst"])
            d = lcsv(**c, M=M, u_force=u_pow, jitter=rmin / 3, eta_shape=eta_eq, extra_eff=0.6, modes_factor=mf)
            d["dT_peak"] = Ht["dT"]
            d["heat_fail_peak"] = Ht["Tm"] > M["Tmax"]
            d["r_c_floor_um"] = rmin * 1e6
            if d["heat_fail_peak"] and "heat" not in d["fails"]:
                d["fails"] = d["fails"] + ["heat@peak"]
            d["feasible"] = not d["fails"]
            out[f"{case}|{rname}"] = d
    print("TABLE corrected LCSV (rt6): flat-top rho 1.0 (eta_eq %.2f), modes x%.1f, DMD+relay eff 0.6, white-coated ITO "
          "(FOM %.1f, 573 K), loop floor from NIR-DMD binary model" % (eta_eq, mf, ito_w["j1A"] / (ito_w["k"] + 2 * kg(T0))))
    for k, d in out.items():
        print(f"  {k:62s} r_c {d['r_c_um']:5.0f} dT(power) {d['dT']:4.0f} dT(peak) {d.get('dT_peak', d['dT']):4.0f} P_IR {d['P_ir_W']:6.1f} W "
              f"P_vis {d['P_vis_W']:5.2f} W px {d['px_total']:.1e} vol$ {d['cost_vol_k']:6.0f}k lab$ {d['cost_lab_k'] / 1e3:6.1f}M  {','.join(d['fails']) or 'OK'}")
    json.dump(out, open(os.path.join(RES, "rt6_table.json"), "w"), indent=1, default=float)
    return out

if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    secs = sys.argv[1:] or ["phys", "geom", "repro", "loop", "dmd", "holo", "mote", "mie", "stray", "safety", "m16", "table"]
    for s in secs:
        if s == "loopq":
            sec_loop(quick=True)
        else:
            globals()["sec_" + s]()

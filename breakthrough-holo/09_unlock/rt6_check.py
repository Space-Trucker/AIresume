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
    return dict(z=z, th=th, Pw=Pw, zt=zt, Pwt=Pwt, T=T, tau_p=tau_p, f=fturb)


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
                if Ms > Ms_max or not np.isfinite(st):
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
            rec[lv_name] = dict(sigma_tot_um=tot * 1e6, sig_turb_um=st * 1e6, sig_noise_um=sn * 1e6, sig_quant_um=sq * 1e6,
                                Ms=Ms, K=K, w_max=w_max)
        # P-only "m15 formula" check: steady error u/omega_c for a P loop with the same latency
        rec["m15_jitter_um"] = 0.1 / (2 * math.pi * 2e3) * 1e6 * (u_rms / 0.1)
        out["freq"].append(rec)
        b = rec.get("binary")
        g = rec.get("64lev")
        print(f"  {mk:9s} {f_fr / 1e3:4.1f}kHz lat {rec['latency_us']:3.0f}us u {u_rms} L {L}: binary sigma "
              f"{b['sigma_tot_um'] if b else float('nan'):6.2f} um (turb {b['sig_turb_um'] if b else 0:.2f}, noise {b['sig_noise_um'] if b else 0:.2f}, "
              f"quant {b['sig_quant_um'] if b else 0:.2f}) | 64-level {g['sigma_tot_um'] if g else float('nan'):6.2f} um")
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
                     dur=6.0 if not quick else 1.0, seed=hash((mk, d, levels, kauth)) % 1000)
        r.update(mote=mk, f_frame=f_fr, latency_us=d * T * 1e6, u_rms=u_rms, L=L, k_auth=kauth, levels=levels,
                 freq_sigma_um=best[0] * 1e6)
        out["sim"].append(r)
        print(f"  SIM {mk:9s} {f_fr / 1e3:4.1f}kHz lat {d * T * 1e6:3.0f}us u {u_rms} L {L} auth {kauth}x lev {levels}: sigma_x {r['sigma_x_um']:.2f} um "
              f"(freq-domain {best[0] * 1e6:.2f}) r_p99.9 {r['r_p999_um']:.1f} r_max {r['r_max_um']:.0f} um sat {r['sat_frac']:.2e} "
              f"exceed/s {r['first_exceed_rate_per_s']}")
    json.dump(out, open(os.path.join(RES, "rt6_loop.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    secs = sys.argv[1:] or ["phys", "geom", "repro", "loop", "dmd", "holo", "mote", "mie", "stray", "safety", "m16", "table"]
    for s in secs:
        if s == "loopq":
            sec_loop(quick=True)
        else:
            globals()["sec_" + s]()

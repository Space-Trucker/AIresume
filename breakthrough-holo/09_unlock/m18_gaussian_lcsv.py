"""M18: static voxels with Gaussian spots, hologram-rate pinning and forward-scatter illumination ("LCSV-G").

Red team 6 (RT6) showed three things that sink LCSV as specified in m15:
- C1: the force authority must cover gust peaks U + 5.4 sigma;
- C2: flat-top spots cost 1.2 pi^2 rho^2 modes per spot area, and the intermediate-plane DMD fails on etendue and depth;
- C3: aerogel motes are index-matched, so their 90-degree scatter is ~1e-3.

This model keeps RT6's corrections and changes three design choices:
1. Gaussian spots. RT6's loop model pins a mote to 1-2 um in a still room with integral action, so the force need not be
   flat across the spot. A Gaussian focus of waist w (P = I0 pi w^2 / 2) needs about 0.9 os^2 L^2 / w^2 hologram modes
   per head, with no pi^2 rho^2 flat-top excess.
2. No DMD. Amplitude control comes from the hologram itself, at 0.5-1.4 kHz, which must follow drafts of 0.4-23 Hz.
3. Forward-scatter illumination. A small uncoated ITO-aerogel mote (n ~ 1.04) scatters q ~ 0.25 at 20-30 degrees but
   ~3e-3 at 90 degrees (RT6 C3). So each viewer is lit from a head roughly behind the mote, 15-40 degrees off their
   line of sight. No white coat is needed, and the mote keeps its FOM.

Class 1 at 1500-1800 nm limits the radiant exposure (1e4 J/m^2 for t <= 10 s) and then the irradiance (1000 W/m^2 over
3.5 mm). So the per-focus cap applies to the mean power. Gust-peak surges of milliseconds are far below the dose limit
(0.785 W for 10 ms over a 1 mm aperture). The stacking factor of beams in a 3.5 mm pupil is recomputed with
m17_exposure_field for each waist, because low-NA Gaussian beams stay narrow over tens of cm.

Run: python3 m18_gaussian_lcsv.py  -> results/m18_gaussian_lcsv.json, results/m18_run.log (via tee)
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))
sys.path.insert(0, HERE)
import physics as ph  # noqa: E402
import budget2 as b2  # noqa: E402
import m15_lightcurtain_static as m15  # noqa: E402
import m17_exposure_field as m17  # noqa: E402
import rt6_check as rt6  # noqa: E402  (BHMIE, validated against Bohren-Huffman by RT6)

LAM_IR, LAM_VIS = 1.55e-6, 500e-9
AEL_IR, AEL_VIS = 10e-3, 0.39e-3
T_HOT_MAX = 573.0                         # ITO plasmon survives air below ~250-300 C at the hot face (RT6 M3)
N_ITO = complex(1.04, 1e-4)               # RT6 C3: ITO island skin on silica aerogel, visible index
ROOMS = {                                 # (U mean, sigma_u per component, r_p99.9 of the pinned mote) in m/s, m/s, m
    "still": (0.00, 0.03, 7.2e-6),        # r_p99.9 from m18c (vector model, MEMS 5 kHz, 4 um sensor noise, w 50 um)
    "home": (0.05, 0.03, 8.1e-6),
    "quiet_office": (0.10, 0.03, 9.2e-6),
    "office": (0.10, 0.10, 30e-6),        # not simulated at 5 kHz; RT6 loop scaling (x3 sigma_u) [ESTIMATE]
}
# smallest Gaussian waist the hologram-rate loop holds without losses (m18c vector model; 0 of 30 lost in 84 mote-s,
# long runs in results/m18c_vector_pin_long.json): 5 kHz MEMS phase modulator with 2 frames of latency
W_LOOP = {"MEMS 5 kHz": {"still": 50e-6, "home": 50e-6, "quiet_office": 50e-6, "office": 120e-6},
          "MEMS 10 kHz": {"still": 35e-6, "home": 40e-6, "quiet_office": 40e-6, "office": 90e-6}}
LAYOUT = {                                 # H10 (M4 heads; RT6 re-derived 2.13 / 1.355)
    "h_worst": 2.14, "h_mean": 1.38, "heads": 10, "occ": 4.47}
L_FIELD = math.sqrt(1.2)                  # side of the field each head addresses (m), RT6 A_field 1.2 m^2
D_THROW = 3.95                            # corner-head throw (m); M_head does not depend on it
ETA_HOLO, ETA_OPT = 0.75, 0.85           # GS multi-spot signal fraction; relay/window
OS, CLIP = 1.5, 1.2                       # pixel oversampling (replicas outside the field, behind a stop); aperture/W


def eta_px(os_):
    """Field-averaged pixel-envelope efficiency sinc^2(theta Delta/lam) over |theta| <= theta_half (square field),
    pitch Delta = lam / (2 os theta_half)."""
    x = np.linspace(-0.5 / os_, 0.5 / os_, 201)
    s1 = np.sinc(x) ** 2
    return float(np.mean(s1) ** 2)


def speeds(U, s, n=200000, seed=3):
    """Authority (gust peak), provisioned and mean relative air speeds for a 3D draft U e_x + N(0, s^2 I)."""
    rng = np.random.default_rng(seed)
    u = rng.normal(0.0, s, size=(n, 3))
    u[:, 0] += U
    mean = float(np.linalg.norm(u, axis=1).mean())
    return dict(v_pk=U + 5.4 * s, v_prov=U + 3.1 * s, v_mean=mean)


def hold(a, v, mote="ito_aerogel", A=None, C_ph=0.85, h=LAYOUT["h_worst"], margin=1.0):
    """Intensity at the mote for force margin*drag(v), with mote heat h * P_abs (h = LP overhead of the head layout)."""
    Mt = m15.mote_props(mote, a)
    A = Mt["A"] if A is None else A
    Tm = ph.T0 + 20
    for _ in range(100):
        Tf = 0.5 * (ph.T0 + Tm)
        F = margin * ph.drag(a, v, Tf)
        fpw = ph.force_per_absorbed_watt(a, Mt["k_eff"], Tm, C_ph, j1A=Mt["j1A"])
        P_abs = F / fpw
        Tn = ph.mote_temperature(h * P_abs, a, v_rel=v)
        if abs(Tn - Tm) < 0.005:
            break
        Tm = 0.5 * (Tm + Tn)
    I = P_abs / (A * math.pi * a * a)
    kg = ph.k_air(ph.T0)
    hot = ph.T0 + (Tm - ph.T0) * (1 + 3 * Mt["j1A"] * A * kg / (Mt["k_eff"] + 2 * kg))   # + l=1 surface mode
    return dict(I=I, Tm=Tm, T_hot=hot, FOM=ph.figure_of_merit(Mt["j1A"], Mt["k_eff"]))


def modes_per_head(w, os_=OS, clip=CLIP):
    """Phase pixels for one head addressing an L x L field with Gaussian spots of waist w: square aperture of side
    2 clip W, W = lam d / (pi w); pixel pitch lam / (2 os theta_half), theta_half = L / (2 d). Independent of d:
    (2 clip W)(2 os theta_half)/lam per side = 2 clip os L / (pi w)."""
    return (2.0 * clip * os_ * L_FIELD / (math.pi * w)) ** 2


_STACK = {}


def stacking(w, S):
    """Worst summed 3.5 mm-pupil exposure over the per-focus power (M17 geometry, Gaussian beams of waist w)."""
    key = (round(w * 1e6), S)
    if key not in _STACK:
        d = m17.run(P_focus=1e-3, r_c=w, S=S, n_probe=2000)
        _STACK[key] = d["stacking_factor"]
    return _STACK[key]


def mie_forward(a, angles=(10, 15, 20, 25, 30, 40, 60, 90), lam=LAM_VIS, m=N_ITO, halfwidth=2.5):
    return rt6.q_iso_profile(a, lam, m, angles_deg=angles, halfwidth=halfwidth)


def design(content="sketch", room="still", a=1.0e-6, A=1.0, delta=3e-3, theta_s=25, os_=OS, w=None, n_illum=2,
           modulator="MEMS 5 kHz", leak=1e-2, bits=4):
    L, S, _ = b2.CONTENT[content]
    N = S / delta
    U, s, pin = ROOMS[room]
    v = speeds(U, s)
    H = LAYOUT
    pk = hold(a, v["v_pk"], A=A)                                   # authority and heat at the gust peak
    pk_occ = hold(a, v["v_pk"], A=A, h=H["occ"])                   # same, one head occluded
    mean = hold(a, v["v_mean"], A=A)
    prov = hold(a, v["v_prov"], A=A)
    # largest waist that keeps the worst pupil at Class 1 (mean power; stacking depends on w and content); the loop
    # needs w >= W_LOOP. The design uses w = w_class1 if the loop allows it (fewest modes), else the loop floor.
    f_holo = float(modulator.split()[1]) * 1e3
    w_loop = W_LOOP[modulator][room]
    w_lo, w_hi = 5e-6, 400e-6
    for _ in range(18):
        wm = math.sqrt(w_lo * w_hi)
        Pf = H["h_worst"] * mean["I"] * math.pi * wm * wm / 2
        if Pf * stacking(wm, S) <= AEL_IR:
            w_lo = wm
        else:
            w_hi = wm
    w_class1 = w_lo
    if w is None:
        w = max(w_class1, w_loop)
    st = stacking(w, S)
    P_focus_mean = H["h_worst"] * mean["I"] * math.pi * w * w / 2
    P_focus_peak = H["h_worst"] * pk["I"] * math.pi * w * w / 2
    eta = ETA_HOLO * eta_px(os_) * ETA_OPT
    P_ir = N * H["h_mean"] * prov["I"] * math.pi * w * w / 2 / eta
    M_head = modes_per_head(w, os_)
    M_tot = H["heads"] * M_head
    W_head = LAM_IR * D_THROW / (math.pi * w)
    head_limit = AEL_IR * (1.5 * W_head) ** 2 / (2 * (1.75e-3) ** 2)   # exit window, beams fill 1.5 W
    # visible: forward scatter at theta_s, Gaussian spot covering the pinning residual
    mie = mie_forward(a, angles=(theta_s, 90))
    q = mie["q_iso"][str(theta_s)]
    V = 683 * ph.V(500)
    J_mote = L * 1e-3 * delta                                     # cd per mote (line 1 mm wide)
    I_v = 4 * math.pi * J_mote / (math.pi * a * a * q * V)        # W/m^2 at the mote toward a viewer at theta_s
    w_v = max(2 * pin, 4e-6)                                      # covers the pinned mote's p99.9 excursion
    P_v_spot = I_v * math.pi * w_v * w_v / 2
    P_vis = N * n_illum * P_v_spot / eta
    L_wall = 0.8 * leak * P_vis * V / (math.pi * 50.0)
    ops = M_tot * (N * 3.0 / H["heads"]) * f_holo                 # point-source CGH, 3 LP beams per mote, every frame
    data = M_tot * bits * f_holo                                  # bit/s into the modulators
    fails = []
    if w_class1 < w_loop:
        fails.append("loop_vs_class1")
    if pk["T_hot"] > T_HOT_MAX:
        fails.append("heat_peak")
    if P_focus_mean * st > AEL_IR * 1.0001:
        fails.append("class1_ir")
    if P_ir / H["heads"] > head_limit:
        fails.append("exit_window")
    if P_v_spot * 3.3 * n_illum > AEL_VIS:
        fails.append("class1_vis")
    if L_wall > 0.01:
        fails.append("wall_light")
    return dict(content=content, room=room, a_um=a * 1e6, A=A, N=N, U=U, sigma=s, **{k: round(x, 4) for k, x in v.items()},
                FOM=pk["FOM"], I_mean=mean["I"], I_prov=prov["I"], I_peak=pk["I"], T_hot_peak=pk["T_hot"],
                T_hot_peak_occ=pk_occ["T_hot"], w_um=w * 1e6, stacking=st, P_focus_mean_mW=P_focus_mean * 1e3,
                P_focus_peak_mW=P_focus_peak * 1e3, P_ir_W=P_ir, head_aperture_mm=2 * 1.5 * W_head * 1e3,
                P_ir_head_W=P_ir / H["heads"], head_limit_W=head_limit, M_head=M_head, M_total=M_tot, data_bps=data,
                modulator=modulator, w_class1_um=w_class1 * 1e6, w_loop_um=w_loop * 1e6, eta_total=eta,
                panels_4K=M_tot / 8.85e6, q_fwd=q, q_90=mie["q_iso"]["90"], theta_s=theta_s, w_v_um=w_v * 1e6,
                P_v_spot_uW=P_v_spot * 1e6, P_vis_W=P_vis, L_wall=L_wall, cgh_ops=ops, fails=fails, feasible=not fails)


def selftest():
    ok = True
    # 1. hold(): I scales ~linearly with v (drag-dominated) and does not depend on a for a skin absorber (B2)
    i1, i2 = hold(1e-6, 0.05)["I"], hold(1e-6, 0.10)["I"]
    i3 = hold(2.5e-6, 0.10)["I"]
    t1 = 1.8 < i2 / i1 < 2.2 and 0.75 < i3 / i2 < 1.33
    print(f"self-test 1 (I ~ v, ~size-free): {'PASS' if t1 else 'FAIL'} I(0.1)/I(0.05) {i2 / i1:.2f}, I(2.5um)/I(1um) {i3 / i2:.2f}")
    # 2. B2 closed form at 0.1 m/s, 1 um, cold gas: I = 4 rho T v / (3 C mu FOM A Cc s) within 20 %, where s is the
    #    slip reduction of the photophoretic force (pp_slip, 0.72 at 1 um; B2 as written in T6 omits it)
    Mt = m15.mote_props("ito_aerogel", 1e-6)
    FOM = ph.figure_of_merit(Mt["j1A"], Mt["k_eff"])
    i_cf = 4 * ph.rho_air(ph.T0) * ph.T0 * 0.1 / (3 * 0.85 * ph.mu_air(ph.T0) * FOM * 1.0 * ph.cunningham(1e-6)
                                                  * ph.pp_slip(1e-6, Mt["k_eff"]))
    t2 = 0.8 < i2 / i_cf < 1.2
    print(f"self-test 2 (B2 closed form): {'PASS' if t2 else 'FAIL'} model/closed {i2 / i_cf:.3f}")
    # 3. mode count: 0.912 os^2 L^2/w^2 for clip 1.5
    t3 = abs(modes_per_head(50e-6, 1.0, 1.5) / (0.9119 * 1.2 / 50e-6 ** 2) - 1) < 1e-3
    print(f"self-test 3 (mode count): {'PASS' if t3 else 'FAIL'}")
    # 4. Mie: RT6's q(30) and q(90) for the 1 um ITO-aerogel mote (0.24-0.27 and 2.9-3.2e-3)
    mie = mie_forward(1e-6, angles=(30, 90), halfwidth=5.0)
    t4 = 0.2 < mie["q_iso"]["30"] < 0.3 and 2.5e-3 < mie["q_iso"]["90"] < 3.5e-3
    print(f"self-test 4 (Mie vs RT6): {'PASS' if t4 else 'FAIL'} q30 {mie['q_iso']['30']:.3f} q90 {mie['q_iso']['90']:.2e}")
    # 5. speeds: mean |u| for U = 0 is sigma sqrt(8/pi)
    sp = speeds(0.0, 0.03)
    t5 = abs(sp["v_mean"] / (0.03 * math.sqrt(8 / math.pi)) - 1) < 0.01
    print(f"self-test 5 (Maxwell mean speed): {'PASS' if t5 else 'FAIL'} {sp['v_mean']:.4f}")
    return t1 and t2 and t3 and t4 and t5 and ok


def b9_speed_bound(w, a=1.0e-6, A=1.0, h_s=None, content_S=5.0, v_probe=0.1):
    """B9: the largest MEAN speed of the mote relative to the air (draft + content motion) at which the worst
    3.5 mm pupil stays within the Class 1 AEL. Per-focus mean power = h_worst I(v) pi w^2/2 <= AEL / stacking, and
    I(v) ~ I_unit v (B2). So v_max = 2 AEL / (pi w^2 h_worst s I_unit). I_unit is evaluated at v_probe."""
    I_unit = hold(a, v_probe, A=A)["I"] / v_probe
    hs = LAYOUT["h_worst"] * stacking(w, content_S) if h_s is None else h_s
    return 2 * AEL_IR / (math.pi * w * w * hs * I_unit), I_unit, hs


def main():
    assert selftest()
    print("\nB9 (Class 1 speed bound): mean mote speed relative to the air, draft + content motion, at which the worst")
    print("pupil reaches the 10 mW AEL. Static-voxel geometry (h_worst x stacking ~7), and a sparse POV-like case (h s = 1.5):")
    b9 = []
    for w in (15e-6, 20e-6, 35e-6, 50e-6, 70e-6):
        v_static, I_unit, hs = b9_speed_bound(w)
        v_pov, _, _ = b9_speed_bound(w, h_s=1.5)
        b9.append(dict(w_um=w * 1e6, I_unit=I_unit, h_s_static=hs, v_static=v_static, v_pov=v_pov))
        print(f"  w {w * 1e6:3.0f} um: I_unit {I_unit:.2e} W/m^2 per m/s;  static (h s {hs:.1f}) v_max {v_static * 100:5.1f} cm/s;  "
              f"sparse (h s 1.5) v_max {v_pov * 100:5.1f} cm/s")
    print("\nForward scatter of uncoated ITO-aerogel motes at 500 nm (q_iso, isotropic-equivalent; RT6 coat target 0.3):")
    fw = {}
    for a in (0.5e-6, 0.75e-6, 1.0e-6, 1.5e-6, 2.5e-6):
        d = mie_forward(a)
        fw[f"{a * 1e6:.2f}"] = d
        print(f"  a {a * 1e6:4.2f} um  Qsca {d['Qsca']:.3f}  " + "  ".join(f"{k}deg {v:.3g}" for k, v in d["q_iso"].items()))
    rows = []
    hdr = (f"{'content':12s} {'room':12s} {'modulator':11s} {'A':>4s} {'Thot':>5s} {'occ':>5s} {'w_c1':>5s} {'w':>4s} {'stk':>5s} "
           f"{'Pf':>5s} {'P_IR':>6s} {'apert':>5s} {'M_tot':>8s} {'Tb/s':>6s} {'q':>5s} {'Pv':>6s} {'P_vis':>6s} {'Lwall':>7s} "
           f"{'CGH':>8s}  fails")
    print("\n" + hdr)
    for content in ("sketch", "film_density"):
        for room in ROOMS:
            for modulator in ("MEMS 5 kHz", "MEMS 10 kHz"):
                for A in (1.0, 0.5):
                    a = 1.0e-6
                    d = design(content, room, a=a, A=A, modulator=modulator, theta_s=15 if room != "office" else 25)
                    rows.append(d)
                    print(f"{content:12s} {room:12s} {modulator:11s} {A:4.1f} {d['T_hot_peak']:5.0f} {d['T_hot_peak_occ']:5.0f} "
                          f"{d['w_class1_um']:5.0f} {d['w_um']:4.0f} {d['stacking']:5.2f} {d['P_focus_mean_mW']:5.2f} {d['P_ir_W']:6.1f} "
                          f"{d['head_aperture_mm']:5.0f} {d['M_total']:8.2e} {d['data_bps'] / 1e12:6.0f} {d['q_fwd']:5.3f} "
                          f"{d['P_v_spot_uW']:6.1f} {d['P_vis_W']:6.2f} {d['L_wall']:7.4f} {d['cgh_ops']:8.1e}  "
                          f"{','.join(d['fails']) or 'OK'}")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m18_gaussian_lcsv.json"), "w") as fh:
        json.dump(dict(forward_scatter=fw, b9=b9, rows=rows), fh, indent=1, default=float)


if __name__ == "__main__":
    main()

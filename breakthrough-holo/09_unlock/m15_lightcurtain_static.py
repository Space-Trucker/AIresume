"""M15: light-curtain holographic static-voxel MOTE ("LCSV"), compared on the same physics as budget v2.1 (POV).

Four changes against the v4 POV design (T6 section 3):
  I1 every beam terminates on an opposite receiver head that monitors its transmitted power. A drop beyond theta_det
     cuts that spot within t_cut, so the per-focus 10 mW Class 1 cap becomes "an undetected partial intercept stays
     <= AEL" (P_focus <= AEL/theta_det), with the dose during the cut checked against the short-exposure MPE;
  I2 static (dotted) voxels: motes sit at image points spaced delta along the strokes and move only with the content;
  I3 light by side-scatter of a visible illumination spot whose beam also ends in a receiver (no wall light, no
     phosphor, no 405 nm pump), so the mote may be black: a carbon-aerogel microsphere (bulk-property estimate);
  I4 drafts are spatially smooth: a fast low-order force modulator per head (DMD zones at an intermediate field plane)
     cancels them; holograms (slow SLM) only place spots. Per-mote residual speed u_res sets the spot (r_c) via the
     hologram update rate.
Octahedral push (6 heads = 3 opposed pairs): worst/mean sum of pushes and max single beam per unit force from T5 §4.

Run: python3 m15_lightcurtain_static.py  -> results/m15_lcsv.json (+ console table); --selftest for checks.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))
import physics as ph  # noqa: E402
import safety as sf  # noqa: E402
import budget2 as b2  # noqa: E402

OCTA = dict(h_worst=math.sqrt(3), h_mean=1.5, single=1.0, heads=6)
# measured room layouts from M4 (07_mote_route/results/m4_room_heads.json): push overheads with all heads, and the
# 95th-percentile worst overhead with one head occluded by a hand (occ_p95)
LAYOUTS = {
    "octa6": dict(OCTA, occ_p95=math.inf),
    "H10": dict(h_worst=2.14, h_mean=1.38, single=1.13, heads=10, occ_p95=4.47),
    "H14": dict(h_worst=2.14, h_mean=1.28, single=1.13, heads=14, occ_p95=3.73),
}

# motes: j1A, k_eff (W/m/K), A_trap (1550 nm), q_side (fraction of pi a^2 scattered into side directions at ~500 nm),
# T_max (K), density (kg/m^3)
# motes: alpha (1/m, effective absorption at 1550 nm; J1/A and A follow from alpha*a via physics.py), k_eff (W/m/K),
# q_side (fraction of pi a^2 scattered into side directions at ~500 nm), T_max (K), density (kg/m^3), j1_factor (<1 if a
# coating adds thermal resistance in front of the absorber)
MOTES = {
    # carbon aerogel (RF-derived, ~5 % solid, rho ~100 kg/m^3): k_eff 0.03-0.05 W/m/K at 1 atm (bulk literature range; not
    # measured at um size). Effective absorption ~ 5 % x glassy-carbon alpha (6.5e6 1/m) ~ 3e5 1/m [ESTIMATE, 2e5-6e5]:
    # a VOLUME absorber at a = 5 um (alpha*a = 1.5), so J1/A ~ 0.2 and FOM ~ 2 (not the skin value 0.4-0.5).
    "carbon_aerogel": dict(alpha=3e5, k_eff=0.045, q_side=0.05, T_max=600.0, rho=100.0, j1_factor=1.0),
    "carbon_aerogel_pess": dict(alpha=2e5, k_eff=0.08, q_side=0.03, T_max=550.0, rho=150.0, j1_factor=1.0),
    # with a thin porous white silica shell: visible side scatter q ~ 0.3 [ESTIMATE]; shell lowers J1 ~10 %, adds k
    "carbon_aerogel_white": dict(alpha=3e5, k_eff=0.055, q_side=0.30, T_max=600.0, rho=110.0, j1_factor=0.9),
    # idea round 2 (sonnet, verified with physics.py): plain BLACK carbon aerogel, optically thick by size. No white coat:
    # a coat adds lateral conduction (k_eff + 2 k_s t/a) and roughly halves FOM.A. Side albedo of a black sphere ~1-3 %.
    "carbon_black": dict(alpha=3e5, k_eff=0.035, q_side=0.02, T_max=600.0, rho=100.0, j1_factor=1.0),
    "carbon_black_dense": dict(alpha=6e5, k_eff=0.05, q_side=0.02, T_max=600.0, rho=200.0, j1_factor=1.0),
    # R9-pessimistic ITO mote (k_eff +0.03 for a micron aerogel denser at its surface): FOM ~4.0
    "ito_aerogel_r9": dict(alpha=None, j1A=0.486, A=1.0, k_eff=0.07, q_side=0.3, T_max=573.0, rho=150.0, j1_factor=1.0),
    # v4 reference mote (ITO island skin on silica aerogel): skin absorber, J1/A 0.486 regardless of size
    "ito_aerogel": dict(alpha=None, j1A=0.486, A=1.0, k_eff=0.04, q_side=0.3, T_max=600.0, rho=150.0, j1_factor=1.0),
}


def mote_props(name, a):
    Mt = MOTES[name]
    if Mt.get("alpha"):
        j1A = ph.j1_over_A(Mt["alpha"] * a) * Mt["j1_factor"]
        A = ph.absorptance(Mt["alpha"] * a)
    else:
        j1A, A = Mt["j1A"], Mt["A"]
    return dict(Mt, j1A=j1A, A=A)


ROOMS = {"quiet": dict(u=0.10, u_res=0.01, a_E=0.6), "calm": dict(u=0.15, u_res=0.015, a_E=1.0),
         "normal": dict(u=0.30, u_res=0.03, a_E=2.4)}
# a_E: rms Eulerian acceleration of the air velocity at a fixed point (m/s^2) ~ U du/dx with Kolmogorov-scale gradients
# (eps 1e-4..1e-3 m^2/s^3, eta ~1.4 mm): idea round 2 (opus) estimate, consistent with 0.4-1.3 um pinning at 200 Hz
DEVICES = {  # hologram device: pixels, frame rate (Hz), efficiency into the spots
    "LCoS_4K": dict(px=8.8e6, rate=360.0, eff=0.6),
    "PLM_MEMS": dict(px=1.3e6, rate=1440.0, eff=0.5),
}
V_CYAN = 683 * ph.V(500)          # lm/W at 500 nm


def design(content="sketch", delta=1.5e-3, a=5e-6, mote="carbon_aerogel", room="quiet", device="LCoS_4K",
           D_field=1.0, safety="curtain", theta_det=0.02, t_cut=1.4e-3, C_ph=0.85, force_margin=1.3, eta_shape=0.8,
           v_content=0.0, k_track=3.0, R_head=0.25, leak=0.01, n_illum=1, f_zone_max=2e4, r_c_min_mult=3.0):
    L, S, _duty = b2.CONTENT[content]
    Mt, Rm, Dv = mote_props(mote, a), ROOMS[room], DEVICES[device]
    N = S / delta
    # --- holding: force against drafts + content motion, octahedral pushes, iterate mote temperature
    Tm = ph.T0 + 30
    for _ in range(60):
        Tf = 0.5 * (ph.T0 + Tm)
        F = force_margin * ph.drag(a, Rm["u"] + v_content, Tf)
        fpw = ph.force_per_absorbed_watt(a, Mt["k_eff"], Tm, C_ph, j1A=Mt["j1A"])
        P_abs_unit = F / fpw                                       # absorbed power that gives force F (eta = 1 push)
        heat = OCTA["h_worst"] * P_abs_unit
        Tn = ph.mote_temperature(heat, a, v_rel=Rm["u"])
        if abs(Tn - Tm) < 0.01:
            break
        Tm = 0.5 * (Tm + Tn)
    I_unit = P_abs_unit / (Mt["A"] * math.pi * a * a)             # intensity at the mote for force F (one beam)
    # --- spot size: residual per-mote motion between hologram updates must stay inside the flat-top
    r_c = max(k_track * Rm["u_res"] / Dv["rate"], r_c_min_mult * a)
    P_unit = I_unit * math.pi * r_c ** 2 / eta_shape              # flat-top spot power giving force F
    P_single = OCTA["single"] * P_unit
    P_focus = OCTA["h_worst"] * P_unit                           # all trap beams through one point (eye at the mote)
    # --- light: side scatter of a visible illumination spot (also terminated in a receiver)
    Phi = 4 * math.pi * L * 1e-3 * S                              # same luminous-flux bookkeeping as budget2
    phi_m = Phi / N
    P_sc = phi_m / V_CYAN                                         # side-scattered visible power per mote
    I_vis = P_sc / (Mt["q_side"] * math.pi * a * a)
    P_vis_spot = I_vis * math.pi * r_c ** 2 / eta_shape / n_illum
    # --- totals
    P_trap_total = N * OCTA["h_mean"] * P_unit / Dv["eff"]
    P_vis_total = N * n_illum * P_vis_spot / Dv["eff"]
    modes_dir = D_field ** 2 / (math.pi * r_c ** 2)
    slm_per_dir = modes_dir / Dv["px"]
    f_zone = k_track * Rm["u"] / r_c                             # fast smooth-draft loop rate
    v_content_max = r_c * Dv["rate"] / k_track                   # trap can move <= r_c/k per hologram frame
    # --- safety
    ael_t, ael_v = sf.ael_class1(1550), sf.ael_class1(500)
    fails = []
    if Tm > Mt["T_max"]:
        fails.append("heat")
    if safety == "class1":
        if P_focus > ael_t:
            fails.append("trap_focus_class1")
        if P_vis_spot > ael_v:
            fails.append("vis_spot_class1")
    else:
        # undetected partial intercept below the trip threshold must itself be Class 1
        if theta_det * P_focus > ael_t:
            fails.append("trap_curtain_threshold")
        if theta_det * P_vis_spot > ael_v or P_vis_spot > 10 * ael_v:
            fails.append("vis_curtain")
        # dose during the cut vs short-exposure MPE through the measurement aperture
        H_cornea_1ms = 1e3 * math.pi * (sf.meas_aperture(1550) / 2) ** 2     # J, 1550 nm, t <= 1 ms (ICNIRP Tab.5)
        if P_focus * t_cut > H_cornea_1ms:
            fails.append("trap_cut_dose")
        H_ret = 18 * t_cut ** 0.75 * math.pi * (7e-3 / 2) ** 2              # J, 400-700 nm, retina thermal
        if P_vis_spot * t_cut > H_ret:
            fails.append("vis_cut_dose")
    if P_trap_total / OCTA["heads"] > sf.head_power_limit(1550, R_head):
        fails.append("trap_exit_window")
    if P_vis_total / OCTA["heads"] > sf.head_power_limit(500, R_head):
        fails.append("vis_exit_window")
    if f_zone > f_zone_max:
        fails.append("zone_loop_rate")
    wall_ratio = leak * P_vis_total * V_CYAN / Phi
    if wall_ratio > 0.05:
        fails.append("wall_light")
    if v_content > v_content_max:
        fails.append("content_speed")
    return dict(content=content, room=room, mote=mote, device=device, safety=safety, a_um=a * 1e6, delta_mm=delta * 1e3,
                N=N, FOM=ph.figure_of_merit(Mt["j1A"], Mt["k_eff"]), dT=Tm - ph.T0, I_unit_Wm2=I_unit,
                r_c_um=r_c * 1e6, P_focus_mW=P_focus * 1e3, P_single_mW=P_single * 1e3, P_vis_spot_mW=P_vis_spot * 1e3,
                P_trap_total_W=P_trap_total, P_vis_total_W=P_vis_total, modes_per_dir=modes_dir,
                slm_per_dir=slm_per_dir, slm_total=slm_per_dir * OCTA["heads"], f_zone_kHz=f_zone / 1e3,
                v_content_max_cm_s=v_content_max * 100, lm_per_mote=phi_m, wall_ratio=wall_ratio, fails=fails,
                feasible=not fails)


def selftest():
    ok = True

    def chk(name, got, want, tol):
        nonlocal ok
        good = abs(got - want) <= tol * abs(want)
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'} {name}: {got:.4g} (want {want:.4g} +- {tol:.0%})")

    print("M15 self-test")
    # 1. I_unit is independent of mote size (T6 B2) at fixed temperature: compare a = 2.5 and 5 um
    # (skin absorber, so FOM itself does not depend on a; for volume absorbers J1/A grows with alpha*a)
    d1 = design(a=2.5e-6, r_c_min_mult=1.0, mote="ito_aerogel")
    d1b = design(a=5e-6, r_c_min_mult=1.0, mote="ito_aerogel")
    chk("I_hold independent of a (2.5 vs 5 um, skin mote)", d1["I_unit_Wm2"], d1b["I_unit_Wm2"], 0.15)
    d2 = design(a=5e-6, r_c_min_mult=1.0)
    # 2. closed form I = 4 rhoT w/(3 C mu FOM A Cc) x margin (eta = 1, h = 1) at room temperature, small heating
    a = 5e-6
    Mt = mote_props("carbon_aerogel", a)
    w = ROOMS["quiet"]["u"]
    I_cf = 1.3 * 4 * (101325 / ph.R_AIR) * w / (3 * 0.85 * ph.mu_air(ph.T0) * ph.figure_of_merit(Mt["j1A"], Mt["k_eff"])
                                                 * Mt["A"] * ph.cunningham(a))
    chk("I_hold vs closed form (T6 B2), slip ~ few %", d2["I_unit_Wm2"], I_cf, 0.12)
    # 3. luminous bookkeeping: N * lm_per_mote = Phi
    chk("flux bookkeeping", d2["N"] * d2["lm_per_mote"], 4 * math.pi * 3.0e-3 * 5.0, 1e-9)
    # 4. modes x power invariant: P_trap_total * modes = N h_mean I_unit D^2 / (eta_shape eff)
    inv = d2["N"] * OCTA["h_mean"] * d2["I_unit_Wm2"] * 1.0 / (0.8 * 0.6)
    chk("power x modes invariant", d2["P_trap_total_W"] * d2["modes_per_dir"], inv, 1e-6)
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return ok


def main():
    if "--selftest" in sys.argv:
        raise SystemExit(0 if selftest() else 1)
    selftest()
    rows = []
    hdr = (f"{'content':12s} {'room':6s} {'mote':19s} {'dev':8s} {'safety':7s} {'dmm':>4s} {'N':>6s} {'FOM':>4s} {'dT':>4s} "
           f"{'r_c':>5s} {'Pfoc':>6s} {'Pvis':>6s} {'Ptrap':>6s} {'Pvis':>5s} {'modes/dir':>9s} {'SLMs':>5s} "
           f"{'zone':>5s} {'vmax':>5s}  fails")
    print("\n" + hdr)
    print(f"{'':54s}{'um':>5s} {'mW':>6s} {'mW':>6s} {'W':>6s} {'W':>5s} {'':>9s} {'tot':>5s} {'kHz':>5s} {'cm/s':>5s}")
    for content in ("accent", "sketch", "film_density"):
        for room in ("quiet", "normal"):
            for mote in ("carbon_aerogel", "carbon_aerogel_pess"):
                for device in ("LCoS_4K", "PLM_MEMS"):
                    for safety in ("class1", "curtain"):
                        for delta in (1.0e-3, 2.0e-3):
                            d = design(content=content, room=room, mote=mote, device=device, safety=safety, delta=delta)
                            rows.append(d)
                            if mote == "carbon_aerogel_pess" and device == "PLM_MEMS":
                                continue
                            print(f"{content:12s} {room:6s} {mote:19s} {device:8s} {safety:7s} {delta * 1e3:4.1f} "
                                  f"{d['N']:6.0f} {d['FOM']:4.1f} {d['dT']:4.0f} {d['r_c_um']:5.0f} {d['P_focus_mW']:6.1f} "
                                  f"{d['P_vis_spot_mW']:6.3f} {d['P_trap_total_W']:6.1f} {d['P_vis_total_W']:5.2f} "
                                  f"{d['modes_per_dir']:9.2e} {d['slm_total']:5.0f} {d['f_zone_kHz']:5.1f} "
                                  f"{d['v_content_max_cm_s']:5.1f}  {','.join(d['fails']) or 'OK'}")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m15_lcsv.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print("\nwrote results/m15_lcsv.json")


COST = {  # [ASSUMPTION] lab-today vs volume prices
    "lab": dict(px=1.1e-3, W_ir=200.0, W_vis=500.0, head=20e3),
    "volume": dict(px=3e-5, W_ir=20.0, W_vis=50.0, head=2e3),
}


def design2(content="sketch", delta=2e-3, a=5e-6, mote="carbon_aerogel", room="quiet", f_fast=2e4, bw_frac=0.1,
            r_c=None, r_v=None, holo_rate=360.0, holo_eff=0.6, D_field=1.0, theta_det=0.02, t_cut=1.4e-3, C_ph=0.85,
            force_margin=1.3, eta_shape=0.8, R_head=0.3, leak=1e-3, lam_vis=500.0, P_ir_max=None, layout="octa6",
            occluded=False, jitter_model="white", bw_pin=500.0, floor=3e-6, safety="curtain", k_ov=2.0):
    """Split control (I4): spot positions from a slow hologram (holo_rate); spot force from a fast amplitude plane at
    f_fast with loop bandwidth bw_frac*f_fast. Mote jitter = u/(2 pi f_bw); r_c >= 3 jitter and >= 3a; the illumination
    spot only needs to cover the jitter (r_v = max(2 jitter, 1.5 a))."""
    L, S, _ = b2.CONTENT[content]
    Mt, Rm = mote_props(mote, a), ROOMS[room]
    G = dict(LAYOUTS[layout])
    if occluded:                                                   # a hand shadows one head for these motes
        G["h_worst"] = G["occ_p95"]
    N = S / delta
    Tm = ph.T0 + 30
    for _ in range(60):
        Tf = 0.5 * (ph.T0 + Tm)
        F = force_margin * ph.drag(a, Rm["u"], Tf)
        fpw = ph.force_per_absorbed_watt(a, Mt["k_eff"], Tm, C_ph, j1A=Mt["j1A"])
        P_abs_unit = F / fpw
        Tn = ph.mote_temperature(G["h_worst"] * P_abs_unit, a, v_rel=Rm["u"])
        if abs(Tn - Tm) < 0.01:
            break
        Tm = 0.5 * (Tm + Tn)
    I_unit = P_abs_unit / (Mt["A"] * math.pi * a * a)
    if jitter_model == "white":      # v1: the full air speed treated as unpredictable at every update (pessimistic)
        jitter = Rm["u"] / (2 * math.pi * bw_frac * f_fast)
    else:                            # integral-action pinning: residual = a_E / w_c^2 + sensing/beam-wander floor
        jitter = Rm["a_E"] / (2 * math.pi * bw_pin) ** 2 + floor
    r_min = max(3 * jitter, 3 * a)
    r_c = max(r_c or r_min, r_min)
    P_unit = I_unit * math.pi * r_c ** 2 / eta_shape
    P_focus = G["h_worst"] * P_unit
    Phi = 4 * math.pi * L * 1e-3 * S
    V_vis = 683 * ph.V(lam_vis)
    P_sc = Phi / N / V_vis
    r_v = max(r_v or 0.0, 2 * jitter, 1.5 * a)
    P_vis_spot = P_sc / (Mt["q_side"] * math.pi * a * a) * math.pi * r_v ** 2 / eta_shape
    P_ir = N * G["h_mean"] * P_unit / holo_eff
    P_vis = N * P_vis_spot / holo_eff
    M_dir = D_field ** 2 / (math.pi * r_c ** 2)
    M_vis = D_field ** 2 / (math.pi * r_v ** 2)                  # illumination hologram (1-2 heads)
    fails = []
    if Tm > Mt["T_max"]:
        fails.append("heat")
    if safety == "class1":           # passive Class 1 per focus; k_ov foci may share one aperture (field checker)
        if P_focus * k_ov > sf.ael_class1(1550):
            fails.append("trap_focus_class1")
        if P_vis_spot * k_ov > sf.ael_class1(lam_vis):
            fails.append("vis_spot_class1")
    else:
        if theta_det * P_focus > sf.ael_class1(1550):
            fails.append("trap_curtain_threshold")
        # corrected (idea round 2): 1500-1800 nm cornea, t < 0.35 s: 1e4 J/m^2 over a 1 mm aperture = 7.85 mJ
        if P_focus * t_cut > 1e4 * math.pi * (0.5e-3) ** 2:
            fails.append("trap_cut_dose")
        if P_vis_spot > sf.ael_class1(lam_vis):
            fails.append("vis_spot_class1")
    if P_ir / G["heads"] > sf.head_power_limit(1550, R_head):
        fails.append("trap_exit_window")
    if P_vis > sf.head_power_limit(lam_vis, R_head):
        fails.append("vis_exit_window")
    if P_ir_max is not None and P_ir > P_ir_max:
        fails.append("ir_power_cap")
    # stray light: with every beam ending in a receiver, only the leak fraction (black-cavity reflection + dust scatter
    # along the path) reaches the room, spread diffusely over ~A_wall of surfaces. Criterion: added wall luminance
    # <= 0.01 cd/m^2, far below a dim lab's ambient (0.3-3 cd/m^2) and the 3-4 cd/m^2 image lines. (budget2's 5 %-of-
    # image-flux rule was for pump light striking walls directly.)
    A_wall, rho_wall = 50.0, 0.8
    wall_ratio = leak * P_vis * V_vis / Phi
    L_wall = rho_wall * leak * P_vis * V_vis / (math.pi * A_wall)
    if L_wall > 0.01:
        fails.append("wall_light")
    cost = {}
    for k, c in COST.items():
        cost[k] = (c["px"] * (G["heads"] * M_dir + M_vis) + c["W_ir"] * P_ir + c["W_vis"] * P_vis
                   + c["head"] * G["heads"])
    return dict(content=content, room=room, mote=mote, delta_mm=delta * 1e3, N=N, FOM=ph.figure_of_merit(Mt["j1A"], Mt["k_eff"]),
                dT=Tm - ph.T0, jitter_um=jitter * 1e6, r_c_um=r_c * 1e6, r_v_um=r_v * 1e6, P_focus_mW=P_focus * 1e3,
                P_vis_spot_uW=P_vis_spot * 1e6, P_ir_W=P_ir, P_vis_W=P_vis, M_dir=M_dir, M_vis=M_vis,
                v_content_max_cm_s=r_c * holo_rate / 3 * 100, wall_ratio=wall_ratio, L_wall=L_wall, cost_lab_k=cost["lab"] / 1e3,
                cost_volume_k=cost["volume"] / 1e3, fails=fails, feasible=not fails)


def optimise(basis="lab", **kw):
    """Cheapest feasible (r_c, r_v) on log grids, at lab or volume prices."""
    key = "cost_lab_k" if basis == "lab" else "cost_volume_k"
    best = None
    for i in range(36):
        for j in range(0, 30, 2):
            d = design2(r_c=10e-6 * 1.12 ** i, r_v=5e-6 * 1.15 ** j, **kw)
            if d["feasible"] and (best is None or d[key] < best[key]):
                best = d
    if best is None:
        best = design2(**kw)
    best["basis"] = basis
    return best


def main2():
    print("\nM15b split control (fast amplitude plane 20 kHz), curtain safety, cost-optimised spot radii (r_c, r_v)")
    print(f"{'content':12s} {'room':6s} {'mote':20s} {'basis':6s} {'dmm':>4s} {'N':>6s} {'dT':>4s} {'r_c':>5s} "
          f"{'r_v':>4s} {'Pfoc':>6s} {'Pvis':>6s} {'P_IR':>6s} {'P_vis':>6s} {'M/dir':>8s} {'M_vis':>8s} {'vmax':>5s} "
          f"{'lab$k':>7s} {'vol$k':>6s}  fails")
    rows = []
    for content in ("accent", "sketch", "film_density"):
        for room in ("quiet", "calm", "normal"):
            for mote in ("carbon_aerogel", "carbon_aerogel_white", "carbon_aerogel_pess"):
                for basis in ("lab", "volume"):
                    d = optimise(basis=basis, content=content, room=room, mote=mote, delta=2e-3)
                    rows.append(d)
                    print(f"{content:12s} {room:6s} {mote:20s} {basis:6s} {d['delta_mm']:4.1f} {d['N']:6.0f} "
                          f"{d['dT']:4.0f} {d['r_c_um']:5.0f} {d['r_v_um']:4.0f} {d['P_focus_mW']:6.1f} "
                          f"{d['P_vis_spot_uW']:6.1f} {d['P_ir_W']:6.1f} {d['P_vis_W']:6.2f} {d['M_dir']:8.1e} "
                          f"{d['M_vis']:8.1e} {d['v_content_max_cm_s']:5.1f} {d['cost_lab_k']:7.0f} "
                          f"{d['cost_volume_k']:6.0f}  {','.join(d['fails']) or 'OK'}")
    with open(os.path.join(HERE, "results", "m15b_split_control.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


def main4(P_ir_max=100.0):
    print(f"\nM15d measured room layouts (M4) instead of the ideal octahedron; <= {P_ir_max:.0f} W IR; hand-occlusion case")
    print(f"{'content':12s} {'room':6s} {'mote':20s} {'a':>3s} {'layout':6s} {'occl':5s} {'dT':>4s} {'r_c':>5s} {'P_IR':>6s} "
          f"{'P_vis':>6s} {'px_total':>9s} {'lab$k':>7s} {'vol$k':>6s}  fails")
    rows = []
    for content in ("accent", "sketch", "film_density"):
        for room in ("quiet", "calm", "normal"):
            for mote, a in (("carbon_aerogel_white", 10e-6), ("ito_aerogel", 5e-6)):
                for layout in ("H10", "H14"):
                    d = optimise(basis="volume", content=content, room=room, mote=mote, a=a, delta=3e-3,
                                 P_ir_max=P_ir_max, layout=layout)
                    # the same spots, with one head occluded near a hand: does the mote still hold (heat)?
                    do = design2(content=content, room=room, mote=mote, a=a, delta=3e-3, layout=layout, occluded=True,
                                 r_c=d["r_c_um"] * 1e-6, r_v=d["r_v_um"] * 1e-6)
                    rows.append(dict(d, layout=layout, occluded_dT=do["dT"], occluded_fails=do["fails"]))
                    px = LAYOUTS[layout]["heads"] * d["M_dir"] + d["M_vis"]
                    occ = "heat" if "heat" in do["fails"] else "ok"
                    print(f"{content:12s} {room:6s} {mote:20s} {a * 1e6:3.0f} {layout:6s} {occ:5s} {d['dT']:4.0f} "
                          f"{d['r_c_um']:5.0f} {d['P_ir_W']:6.1f} {d['P_vis_W']:6.2f} {px:9.1e} {d['cost_lab_k']:7.0f} "
                          f"{d['cost_volume_k']:6.0f}  {','.join(d['fails']) or 'OK'}")
    with open(os.path.join(HERE, "results", "m15d_layouts.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


def main5(P_ir_max=100.0, f_fast=12.5e3, holo_rate=180.0):
    """Real 2026 device rates (idea round 2): DLP650LNIR 12.5 kHz binary gate, GAEA-2.1 4K phase LCoS 60-180 Hz."""
    print(f"\nM15e real device rates (fast gate {f_fast / 1e3:.1f} kHz, hologram {holo_rate:.0f} Hz), H10 layout, "
          f"<= {P_ir_max:.0f} W IR, delta 3 mm; black carbon motes sized for optical depth")
    print(f"{'content':12s} {'room':6s} {'mote':18s} {'a':>3s} {'FOM':>4s} {'dT':>4s} {'occ':>4s} {'r_c':>5s} {'r_v':>4s} "
          f"{'P_IR':>6s} {'P_vis':>6s} {'px_total':>9s} {'4K':>5s} {'vmax':>5s} {'vol$k':>6s}  fails")
    rows = []
    for content in ("accent", "sketch", "film_density"):
        for room in ("quiet", "calm", "normal"):
            for mote, a in (("carbon_black", 10e-6), ("carbon_black", 15e-6), ("carbon_black_dense", 5e-6),
                            ("ito_aerogel", 5e-6)):
                d = optimise(basis="volume", content=content, room=room, mote=mote, a=a, delta=3e-3,
                             P_ir_max=P_ir_max, layout="H10", f_fast=f_fast, holo_rate=holo_rate)
                do = design2(content=content, room=room, mote=mote, a=a, delta=3e-3, layout="H10", occluded=True,
                             r_c=d["r_c_um"] * 1e-6, r_v=d["r_v_um"] * 1e-6, f_fast=f_fast, holo_rate=holo_rate)
                px = LAYOUTS["H10"]["heads"] * d["M_dir"] + d["M_vis"]
                rows.append(dict(d, a_um=a * 1e6, px_total=px, occluded_dT=do["dT"], occluded_fails=do["fails"]))
                print(f"{content:12s} {room:6s} {mote:18s} {a * 1e6:3.0f} {d['FOM']:4.1f} {d['dT']:4.0f} "
                      f"{do['dT']:4.0f} {d['r_c_um']:5.0f} {d['r_v_um']:4.0f} {d['P_ir_W']:6.1f} {d['P_vis_W']:6.2f} "
                      f"{px:9.1e} {px / 8.3e6:5.0f} {d['v_content_max_cm_s']:5.2f} {d['cost_volume_k']:6.0f}  "
                      f"{','.join(d['fails']) or 'OK'}{' | occluded: heat' if 'heat' in do['fails'] else ''}")
    with open(os.path.join(HERE, "results", "m15e_real_devices.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


def main6(P_ir_max=100.0):
    """Integral-action pinning (idea round 2, opus) vs the v1 white-noise jitter; curtain vs passive Class 1 per focus."""
    print(f"\nM15f pinning loop (500 Hz, a_E/w^2 + 3 um floor), real device rates, H14, <= {P_ir_max:.0f} W IR, delta 3 mm")
    print(f"{'content':12s} {'room':6s} {'mote':12s} {'a':>4s} {'safety':7s} {'dT':>4s} {'occ':>4s} {'r_c':>5s} {'Pfoc':>6s} "
          f"{'P_IR':>6s} {'P_vis':>6s} {'px_total':>9s} {'4K':>6s} {'vol$k':>6s} {'lab$M':>6s}  fails")
    rows = []
    for content in ("sketch", "film_density"):
        for room in ("quiet", "calm", "normal"):
            for mote, a in (("ito_aerogel", 2.5e-6), ("ito_aerogel", 5e-6), ("carbon_black", 15e-6)):
                for safety in ("curtain", "class1"):
                    kw = dict(content=content, room=room, mote=mote, a=a, delta=3e-3, layout="H14", f_fast=12.5e3,
                              holo_rate=180.0, jitter_model="pinning", safety=safety)
                    d = optimise(basis="volume", P_ir_max=P_ir_max, **kw)
                    do = design2(occluded=True, r_c=d["r_c_um"] * 1e-6, r_v=d["r_v_um"] * 1e-6, **kw)
                    px = LAYOUTS["H14"]["heads"] * d["M_dir"] + d["M_vis"]
                    rows.append(dict(d, a_um=a * 1e6, safety=safety, px_total=px, occluded_dT=do["dT"],
                                     occluded_fails=do["fails"]))
                    print(f"{content:12s} {room:6s} {mote:12s} {a * 1e6:4.1f} {safety:7s} {d['dT']:4.0f} {do['dT']:4.0f} "
                          f"{d['r_c_um']:5.0f} {d['P_focus_mW']:6.1f} {d['P_ir_W']:6.1f} {d['P_vis_W']:6.2f} {px:9.1e} "
                          f"{px / 8.3e6:6.0f} {d['cost_volume_k']:6.0f} {d['cost_lab_k'] / 1e3:6.1f}  "
                          f"{','.join(d['fails']) or 'OK'}{' | occluded: heat' if 'heat' in do['fails'] else ''}")
    with open(os.path.join(HERE, "results", "m15f_pinning.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


def main3(P_ir_max=100.0):
    print(f"\nM15c practical cap: <= {P_ir_max:.0f} W of 1550 nm in total (volume prices); mote FOM from alpha*a")
    print(f"{'content':12s} {'room':6s} {'mote':20s} {'a':>3s} {'FOM':>4s} {'dT':>4s} {'dmm':>4s} {'N':>6s} {'r_c':>5s} "
          f"{'r_v':>4s} {'Pfoc':>6s} {'P_IR':>6s} {'P_vis':>6s} {'px_total':>9s} {'vmax':>5s} {'lab$k':>7s} {'vol$k':>6s}  fails")
    rows = []
    for content in ("accent", "sketch", "film_density"):
        for room in ("quiet", "calm", "normal"):
            for mote, a in (("carbon_aerogel_white", 5e-6), ("carbon_aerogel_white", 10e-6), ("carbon_aerogel_pess", 10e-6)):
                d = optimise(basis="volume", content=content, room=room, mote=mote, a=a, delta=3e-3, P_ir_max=P_ir_max)
                rows.append(dict(d, a_um=a * 1e6))
                px = OCTA["heads"] * d["M_dir"] + d["M_vis"]
                print(f"{content:12s} {room:6s} {mote:20s} {a * 1e6:3.0f} {d['FOM']:4.1f} {d['dT']:4.0f} {d['delta_mm']:4.1f} "
                      f"{d['N']:6.0f} {d['r_c_um']:5.0f} {d['r_v_um']:4.0f} {d['P_focus_mW']:6.1f} {d['P_ir_W']:6.1f} "
                      f"{d['P_vis_W']:6.2f} {px:9.1e} {d['v_content_max_cm_s']:5.1f} {d['cost_lab_k']:7.0f} "
                      f"{d['cost_volume_k']:6.0f}  {','.join(d['fails']) or 'OK'}")
    with open(os.path.join(HERE, "results", "m15c_capped.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()
    main2()
    main3()
    main4()
    main5()
    main6()

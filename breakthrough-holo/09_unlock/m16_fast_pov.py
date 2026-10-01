"""M16: fast POV motes with the light curtain and terminated scattering illumination ("LCSV-P").

In v4 the mote speed (0.2-0.5 m/s) was set by the light budget: the 405 nm pump's 39 uW Class 1 limit and the lumens
each mote must give (phi_m grows with v because fewer motes draw the same strokes). With (I1) a monitored-beam curtain
and (I3) visible scattering whose beams end in receivers, the speed is set by heat instead, and small skin-absorbing motes
are fast: v ~ 3 C mu k_g dT FOM / (rho T a) (T5). This model keeps v4's per-mote steered beams (feedforward along the
planned stroke plus a feedback loop) and asks how many channels and watts film density needs at 0.5-5 m/s.

Run: python3 m16_fast_pov.py  -> results/m16_fast_pov.json
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))
sys.path.insert(0, HERE)
import physics as ph  # noqa: E402
import safety as sf  # noqa: E402
import budget2 as b2  # noqa: E402
import m15_lightcurtain_static as m15  # noqa: E402


def design(content="film_density", v=2.0, a=1.5e-6, mote="ito_aerogel", room="quiet", layout="H10", f=60.0,
           f_bw=5e3, ff_err=0.02, C_ph=0.85, force_margin=1.3, eta_shape=0.8, T_max=573.0, theta_det=0.02,
           t_cut=1.4e-3, lam_vis=500.0, R_head=0.3, leak=1e-3, occluded=False):
    """f_bw: tracking-loop bandwidth (Hz) of each steered channel; ff_err: fraction of v not removed by feedforward
    along the planned stroke (path/timing errors); position error = (u + ff_err v)/(2 pi f_bw)."""
    L, S, duty = b2.CONTENT[content] if isinstance(content, str) else content
    Mt = m15.mote_props(mote, a)
    G = dict(m15.LAYOUTS[layout])
    if occluded:
        G["h_worst"] = G["occ_p95"]
    u = m15.ROOMS[room]["u"]
    N = S * f / (v * duty)
    Tm = ph.T0 + 50
    for _ in range(80):
        Tf = 0.5 * (ph.T0 + Tm)
        F = force_margin * ph.drag(a, v + u, Tf)
        fpw = ph.force_per_absorbed_watt(a, Mt["k_eff"], Tm, C_ph, j1A=Mt["j1A"])
        P_abs_unit = F / fpw
        Tn = ph.mote_temperature(G["h_worst"] * P_abs_unit, a, v_rel=v + u)
        if abs(Tn - Tm) < 0.01:
            break
        Tm = 0.5 * (Tm + Tn)
    I_unit = P_abs_unit / (Mt["A"] * math.pi * a * a)
    err = (u + ff_err * v) / (2 * math.pi * f_bw)
    r_c = max(3 * err, 3 * a)
    P_unit = I_unit * math.pi * r_c ** 2 / eta_shape
    P_focus = G["h_worst"] * P_unit
    # light: each mote gives phi_m while drawing; side scatter of a tracked visible spot (r_v covers the error)
    Phi = 4 * math.pi * L * 1e-3 * S
    phi_m = Phi / (N * duty)
    V_vis = 683 * ph.V(lam_vis)
    P_sc = phi_m / V_vis
    r_v = max(2 * err, 1.5 * a)
    P_vis_spot = P_sc / (Mt["q_side"] * math.pi * a * a) * math.pi * r_v ** 2 / eta_shape
    beams_per_mote = 3 + 1                                      # ~3 active pushes (M4) + 1 illumination
    channels = N * beams_per_mote
    P_ir = N * G["h_mean"] * P_unit
    P_vis = N * P_vis_spot
    fails = []
    if Tm > T_max:
        fails.append("heat")
    if theta_det * P_focus > sf.ael_class1(1550):
        fails.append("trap_curtain_threshold")
    if P_focus * t_cut > 1e3 * math.pi * (sf.meas_aperture(1550) / 2) ** 2:
        fails.append("trap_cut_dose")
    H_ret = 18 * t_cut ** 0.75 * math.pi * (7e-3 / 2) ** 2
    if theta_det * P_vis_spot > sf.ael_class1(lam_vis) or P_vis_spot * t_cut > H_ret:
        fails.append("vis_curtain")
    if P_ir / G["heads"] > sf.head_power_limit(1550, R_head):
        fails.append("trap_exit_window")
    if P_vis / G["heads"] > sf.head_power_limit(lam_vis, R_head):
        fails.append("vis_exit_window")
    L_wall = 0.8 * leak * P_vis * V_vis / (math.pi * 50.0)
    if L_wall > 0.01:
        fails.append("wall_light")
    return dict(content=content if isinstance(content, str) else f"custom S{S}", v=v, a_um=a * 1e6, mote=mote, room=room,
                layout=layout, FOM=ph.figure_of_merit(Mt["j1A"], Mt["k_eff"]), N=N, channels=channels, dT=Tm - ph.T0,
                err_um=err * 1e6, r_c_um=r_c * 1e6, P_focus_mW=P_focus * 1e3, P_vis_spot_mW=P_vis_spot * 1e3,
                P_ir_W=P_ir, P_vis_W=P_vis, lm_per_mote=phi_m, L_wall=L_wall, fails=fails, feasible=not fails)


def main():
    rows = []
    print(f"{'content':12s} {'room':6s} {'a':>4s} {'v':>4s} {'N':>6s} {'chan':>6s} {'dT':>5s} {'err':>5s} {'r_c':>4s} "
          f"{'Pfoc':>6s} {'Pvis':>6s} {'P_IR':>6s} {'P_vis':>6s}  fails  [occluded: dT]")
    for content in ("sketch", "film_density"):
        for room in ("quiet", "calm", "normal"):
            for a in (1.0e-6, 1.5e-6, 2.5e-6):
                for v in (0.5, 1.0, 2.0, 3.0, 5.0):
                    d = design(content=content, room=room, a=a, v=v)
                    do = design(content=content, room=room, a=a, v=v, occluded=True)
                    rows.append(dict(d, occluded_dT=do["dT"], occluded_fails=do["fails"]))
                    print(f"{content:12s} {room:6s} {a * 1e6:4.1f} {v:4.1f} {d['N']:6.0f} {d['channels']:6.0f} {d['dT']:5.0f} "
                          f"{d['err_um']:5.1f} {d['r_c_um']:4.0f} {d['P_focus_mW']:6.1f} {d['P_vis_spot_mW']:6.2f} "
                          f"{d['P_ir_W']:6.1f} {d['P_vis_W']:6.2f}  {','.join(d['fails']) or 'OK'}  [{do['dT']:.0f}"
                          f"{' heat' if 'heat' in do['fails'] else ''}]")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m16_fast_pov.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()

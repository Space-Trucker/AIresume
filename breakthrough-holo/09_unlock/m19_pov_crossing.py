"""M19: fast POV motes under passive Class 1 by the crossing-rate rule (idea round 3, opus idea 2), with RT6/T7 fixes.

Why a moving focus is judged differently (IEC 60825-1 multiple-pulse rules above 1400 nm; R7 rows K6/K7):
- every pass of a moving focus through a fixed aperture is one pulse;
- rule 1 compares each pass with the single-pulse limit (1e4 J/m^2 over 1 mm for t < 0.35 s, i.e. 7.85 mJ);
- rule 2 compares the time average over T with the CW AEL (10 mW over 3.5 mm);
- C5 does not apply above 1400 nm;
- a scan/stall single fault must be detected and cut (scanning safeguard).

A mote moving at v relative to the air needs P = h I_unit v pi w^2/2, so the energy per unit path is
E/L = h I_unit pi w^2 / 2, whatever its speed. A pupil on a stroke refreshed f_r times per second, also crossed by s'
other tubes, receives on average f_r s' d_ap (1 + u/v) E/L. This bound does not depend on v. Heat (B3) is what limits
the mote speed.

The model keeps every correction already accepted:
- RT6: gust authority U + 5.4 sigma; diffraction floor of the spot; ~6-7 steered beams per mote (3 LP pushes,
  1 hand-over, 2 illumination);
- T7: 1 um uncoated ITO-aerogel mote, slip included; forward-scatter illumination at 10-15 degrees.

Steered-channel etendue: a full-field channel needs D*theta >= 1.5 lam L / (pi w) per axis. A patch channel (fiber
positioner in a shared objective's image plane plus a fast fine actuator) needs only lam^2 plus mechanical travel.

Run: python3 m19_pov_crossing.py -> results/m19_pov_crossing.json, results/m19_run.log
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))
import physics as ph  # noqa: E402
import budget2 as b2  # noqa: E402
import m18_gaussian_lcsv as m18  # noqa: E402

D_AP = 3.5e-3
AEL_IR, AEL_VIS = 10e-3, 0.39e-3
E_PASS_MAX = 1e4 * math.pi * 0.5e-3 ** 2          # rule 1 single pass, t < 0.35 s, 1 mm aperture: 7.85 mJ
H_WORST, H_MEAN = 2.14, 1.38
ROOMS = {"still": (0.0, 0.03), "home": (0.05, 0.03), "quiet_office": (0.10, 0.03), "office": (0.10, 0.10)}
BEAMS_PER_MOTE = 3 + 1 + 2                        # LP pushes + hand-over + two illumination beams (RT6 M9)
ETA_STEER = 0.7                                   # channel optics (fiber/relay/objective) [ESTIMATE]
L_FIELD, D_THROW = math.sqrt(1.2), 3.95


def design(content="sketch", room="still", v=0.8, f_r=60.0, a=1.0e-6, s_prime=None, w=None, theta_s=10, n_vis=2,
           R_head=0.07):
    L_cd, S, duty = b2.CONTENT[content]
    U, sig = ROOMS[room]
    sp = m18.speeds(U, sig)
    u_mean = sp["v_mean"]
    v_pk = v + sp["v_pk"]                                         # gust peak on top of the stroke speed
    pk = m18.hold(a, v_pk, h=H_WORST)                             # heat at the worst instant
    I_unit = m18.hold(a, v, h=H_WORST)["I"] / v
    N = S * f_r / (v * duty)
    # eye, crossing-rate rule 2: f_r s' d_ap (1 + u/v) E/L <= AEL, E/L = h_w I_unit pi w^2/2  -> largest w
    # s' from the static-voxel stacking (M17, random heads) of the equivalent power-per-length pattern: POV deposits
    # f_r E/L per metre of stroke, which is static voxels at spacing delta with P_s = f_r E/L delta. So
    # s' = 1 + (s_static - 1) delta/d_ap (own path + neighbours' tubes). Iterate, because s_static depends on w.
    w_eye = 50e-6
    for _ in range(6 if s_prime is None else 1):
        sp_ = 1 + (m18.stacking(w_eye, S) - 1) * 3e-3 / D_AP if s_prime is None else s_prime
        load = f_r * sp_ * D_AP * (1 + u_mean / v)
        w_eye = math.sqrt(2 * AEL_IR / (load * H_WORST * I_unit * math.pi))
    s_prime = sp_
    w_diff = 1.5 * LAM * D_THROW / (math.pi * R_head)            # diffraction: head aperture radius R_head (clip 1.5)
    if w is None:
        w = min(w_eye, 60e-6)
    E_per_L = H_WORST * I_unit * math.pi * w * w / 2
    mean_pupil = load * E_per_L
    E_pass = E_per_L * D_AP                                       # one full pass through 3.5 mm (rule 1 uses 1 mm)
    P_focus = E_per_L * (v + u_mean)                              # instantaneous per-focus power, mean draft
    t_stall = E_PASS_MAX / P_focus                                # time to reach the rule-1 dose if the focus stalls
    P_ir = N * duty * H_MEAN / H_WORST * P_focus / ETA_STEER      # motes draw only during the duty fraction
    # visible: luminance of a 1 mm line; per mote flux while drawing; forward scatter at theta_s
    Phi = 4 * math.pi * L_cd * 1e-3 * S
    phi_m = Phi / (N * duty)
    q = m18.mie_forward(a, angles=(theta_s,))["q_iso"][str(theta_s)]
    V = 683 * ph.V(500)
    I_v = phi_m / (math.pi * a * a * q * V)
    w_v = max(w / 2, 10e-6)                                       # covers the tracking error (w/3-ish) [ESTIMATE]
    P_v = I_v * math.pi * w_v * w_v / 2
    P_vis = N * duty * n_vis * P_v / ETA_STEER
    # visible crossing, rule 2: time-mean power through a 7 mm pupil on a stroke (both illumination beams of the mote
    # converge there) against 0.39 mW. Rule 3 (C5, retinal, 400-1400 nm) is not evaluated here [TODO RT7].
    vis_mean_pupil = f_r * s_prime * 7e-3 * (P_v / v) * n_vis
    channels = N * BEAMS_PER_MOTE
    etendue_full = 1.5 * LAM * L_FIELD / (math.pi * w)            # m rad per axis for a full-field channel
    fails = []
    if pk["T_hot"] > m18.T_HOT_MAX:
        fails.append("heat")
    if w < w_diff:
        fails.append("diffraction")
    if mean_pupil > AEL_IR * 1.0001:
        fails.append("class1_ir")
    if E_pass > E_PASS_MAX:
        fails.append("rule1")
    if vis_mean_pupil > AEL_VIS:
        fails.append("class1_vis")
    return dict(content=content, room=room, v=v, f_r=f_r, s_prime=s_prime, R_head=R_head, N=N, channels=channels,
                T_hot_peak=pk["T_hot"],
                v_pk=v_pk, I_unit=I_unit, w_eye_um=w_eye * 1e6, w_um=w * 1e6, w_diff_um=w_diff * 1e6,
                E_per_L_mJ_m=E_per_L * 1e3, mean_pupil_mW=mean_pupil * 1e3, E_pass_mJ=E_pass * 1e3,
                P_focus_mW=P_focus * 1e3, t_stall_ms=t_stall * 1e3, P_ir_W=P_ir, q=q, P_v_uW=P_v * 1e6, P_vis_W=P_vis,
                vis_mean_pupil_uW=vis_mean_pupil * 1e6, etendue_full_mrad=etendue_full * 1e3, fails=fails,
                feasible=not fails)


LAM = 1.55e-6


def main():
    rows = []
    print(f"{'content':12s} {'room':12s} {'v':>4s} {'f_r':>3s} {'s1':>3s} {'N':>5s} {'chan':>6s} {'Thot':>5s} {'w':>4s} "
          f"{'E/L':>5s} {'pupil':>6s} {'Epass':>6s} {'Pfoc':>5s} {'stall':>6s} {'P_IR':>5s} {'Pv':>6s} {'P_vis':>6s} "
          f"{'vis_p':>6s} {'Dth':>5s} {'Rap':>4s}  fails")
    for content in ("sketch", "film_density"):
        for room in ROOMS:
            for f_r in (30.0, 60.0):
                for v in (0.5, 0.8, 1.0):
                    R_head = 0.11
                    d = design(content, room, v=v, f_r=f_r, s_prime=None, R_head=R_head)
                    s1 = d["s_prime"]
                    rows.append(d)
                    print(f"{content:12s} {room:12s} {v:4.1f} {f_r:3.0f} {s1:3.1f} {d['N']:5.0f} {d['channels']:6.0f} "
                          f"{d['T_hot_peak']:5.0f} {d['w_um']:4.0f} {d['E_per_L_mJ_m']:5.1f} {d['mean_pupil_mW']:6.2f} "
                          f"{d['E_pass_mJ']:6.3f} {d['P_focus_mW']:5.1f} {d['t_stall_ms']:6.0f} {d['P_ir_W']:5.1f} "
                          f"{d['P_v_uW']:6.1f} {d['P_vis_W']:6.3f} {d['vis_mean_pupil_uW']:6.1f} {d['etendue_full_mrad']:5.1f} "
                          f"{R_head * 100:4.0f}  "
                          f"{','.join(d['fails']) or 'OK'}")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m19_pov_crossing.json"), "w") as fh:
        json.dump(rows, fh, indent=1, default=float)


if __name__ == "__main__":
    main()

"""MOTE system budget v2, after red team 4 (05_reviews/red_team_4_mote.md) and the owner's room head arrays (M4).

Changes from v1 (budget.py, kept for reproducibility of the v1 atlas):
* Mote material is consistent (C1). Classes:
  - 'engineered': aerogel core, island absorber skin, j1A 0.43, k_eff 0.03;
  - 'optimistic': j1A 0.40, k_eff 0.15, A 0.85 (red team's plausible-optimistic);
  - 'dense': j1A 0.40, k_eff 1.0.
  The pump absorptance comes from the phosphor loading of the mote volume (alpha_pump).
* Force model: rho and T at the same state (Major 1); C_ph = 1.0, range 0.67-1.04 (Major 4); J1 = j1A * A (Major 3).
  A force margin (default x1.3) covers pump photophoresis, delta-alpha, shape and spin forces (Major 7).
* Temperature limit and phosphor quench are evaluated at the hot face, T_m + T1 (Major 11).
* Architectures on the M4 room arrays:
  - 'room_push': the M4 'R12 lab rig' (ceiling ring of 6 + low ring of 4 + ceiling spot + floor head; throws
    1.2-2.3 m). Active feedback. h_worst 2.22, h_mean 1.33, largest single beam 1.19, 3 active beams. Dithered flat-top of radius R_ft >= 20 um (C2/M2c), so the edge
    >= w is realisable.
  - 'room_pairs': passive LG01 pairs (exact lg01_trap, Major 2). The workload manager picks the opposed pair best
    aligned with the motion. Heat factor h_worst ~ 1.02/eta, h_mean ~ 0.5 + 0.58/eta (M4 fit); 2 beams per mote.
* Pump (C3): n_pump beams per mote from different heads, each <= AEL/k_overlap (scheduler rule: at most k_overlap
  pump foci on one line of sight), intercept derated for pointing jitter, exit-window check per pump head.
* Wall light is energy-conserving (Minor 1), with an optical-brightener gain.
* Refresh 60 Hz by default (Major 9); content duty from mote_plan on the armor; u_air = 0.3 m/s (Minor 10).
"""
from __future__ import annotations

import math

import physics as ph
import safety as sf

CONTENT = {  # (L cd/m^2, S m, duty from mote_plan.py on the procedural armor)
    "accent": (3.0, 1.0, 0.5),
    "sketch": (3.0, 5.0, 0.57),
    "film_contrast": (4.0, 9.0, 0.72),
    "film_density": (4.0, 30.0, 0.83),
    "film_exact": (50.0, 30.0, 0.83),
}
MOTES = {  # j1A, k_eff (W/m/K), A_trap at 1550 nm; pump model
    # core-shell: dense Eu2+ phosphor core (radius 0.6 a, k ~ 5 W/m/K, alpha_405 ~ 5e5 1/m [memory; RT4: 1e5-1e6]),
    # silica-aerogel shell (k 0.02), island (non-percolating) NIR-absorber skin (+0.01 W/m/K); pump focused on the core
    "coreshell": dict(j1A=0.43, k_eff=ph.k_coated_sphere(5.0, 0.02, 0.6) + 0.01, A=0.95, core_frac=0.6, alpha_core=5e5),
    "engineered": dict(j1A=0.43, k_eff=0.03, A=0.99),
    # M7-validated recipes with an ITO-class plasmonic skin (alpha ~5.7e5 /cm, skin tau >> 2): J1/A from sim_m7
    "ito_aerogel": dict(j1A=0.486, k_eff=0.04, A=1.0),
    # hypothetical ceiling: perfect skin, k_eff 0.01 (better than any known solid), survives 900 K (bound only)
    "ideal_bound": dict(j1A=0.5, k_eff=0.01, A=1.0),
    "ito_coreshell": dict(j1A=0.489, k_eff=ph.k_coated_sphere(5.0, 0.02, 0.6) + 0.01, A=1.0, core_frac=0.6, alpha_core=5e5),
    "optimistic": dict(j1A=0.40, k_eff=0.15, A=0.85),
    "dense": dict(j1A=0.40, k_eff=1.0, A=0.90),
}
ROOM = {  # M4 'R12 lab rig': 6-head ceiling ring + 4-head low ring + ceiling spot + floor head; throws 1.2-2.3 m
    "room_push": dict(h_worst=2.22, h_mean=1.33, single=1.19, beams=3, heads=12, throw=2.0),
    "room_pairs": dict(beams=2, heads=12, throw=2.0),
}


def waist(lam_nm, throw, R_head, M2=1.3):
    return M2 * lam_nm * 1e-9 * throw / (math.pi * R_head)


def intercept(a, w, jitter=0.0):
    return (1 - math.exp(-2 * a * a / (w * w))) * (w * w / (w * w + 4 * jitter * jitter))


def design(content="film_density", a=2.5e-6, v=0.5, mote="engineered", arch="room_push", f=60.0, u_air=0.3,
           T_max=450.0, C_ph=1.0, force_margin=1.3, R_head=0.075, R_ft_min=20e-6, eta_shape=0.8,
           emitter="cyan_BaSi2O2N2", pump_lam=405, alpha_pump=1.5e5, n_pump=2, pump_R_head=None, pump_throw=2.0,
           jitter=0.5e-6, k_overlap=2.0, whitener_gain=5.0, k_ov_trap=2.0, focus_sum=True):
    L, S, duty = CONTENT[content] if isinstance(content, str) else content     # or a custom (L, S, duty) tuple
    Mt = MOTES[mote]
    arc = dict(ROOM[arch])
    j1A, k_eff, A = Mt["j1A"], Mt["k_eff"], Mt["A"]
    w_t = waist(1550, arc["throw"], R_head)
    if arch == "room_pairs":
        eta, f_I = ph.lg01_trap(a, w_t)
        arc.update(h_worst=1.02 / max(eta, 1e-6), h_mean=0.5 + 0.58 / max(eta, 1e-6), single=0.5)
    else:
        eta, f_I = 1.0, 1.0
    Phi = 4 * math.pi * L * 1e-3 * S
    N = S * f / (v * duty)
    phi_m = Phi / (N * duty)
    ph_p = ph.PHOSPHOR[emitter]
    A_pump = ph.absorptance(alpha_pump * a)
    pump_R_head = pump_R_head or R_head
    w_p = waist(pump_lam, pump_throw, pump_R_head)
    icp = intercept(a, w_p, jitter)

    Tm, T_face = ph.T0 + 50, ph.T0 + 60
    P_F = P_abs_pump = P_abs_beam = 0.0
    for _ in range(100):
        Tf = 0.5 * (ph.T0 + Tm)
        F_need = force_margin * ph.drag(a, v + u_air, Tf)
        fpw = ph.force_per_absorbed_watt(a, k_eff, Tm, C_ph, j1A=j1A)
        # ideal absorbed power for the force; the architecture's heat factor h_worst (which for pairs already holds
        # 1/eta for the lateral direction) multiplies it below. Dividing by eta here as well would count eta twice.
        P_F = F_need / fpw
        P_abs_beam = P_F * arc["single"] if arch == "room_push" else P_F * arc["h_worst"] / 2
        T1 = j1A * P_abs_beam / (math.pi * a * (k_eff + 2 * ph.k_air(Tf)))
        lm_W, _, _ = ph.phosphor_lumens(1.0, pump_lam, T_face, emitter)
        P_abs_pump = phi_m / lm_W if lm_W > 1e-9 else math.inf
        heat = P_F * arc["h_worst"] + P_abs_pump * (1 - lm_W / (683 * ph.band_V(ph_p["lam_em"], ph_p["fwhm"])))
        Tm_new = ph.mote_temperature(heat, a, v_rel=v + u_air) if math.isfinite(heat) else 6000.0
        T_face_new = Tm_new + T1
        if abs(Tm_new - Tm) < 0.01 and abs(T_face_new - T_face) < 0.01:
            break
        Tm, T_face = 0.5 * (Tm + Tm_new), 0.5 * (T_face + T_face_new)
    runaway = Tm > 2000 or not math.isfinite(P_abs_pump)

    # --- trap beams
    I_mote = P_abs_beam / (A * math.pi * a * a)
    if arch == "room_push":
        R_ft = max(R_ft_min, w_t)
        P_beam = I_mote * math.pi * R_ft ** 2 / eta_shape
    else:
        R_ft = None
        P_beam = P_abs_beam * math.e * w_t ** 2 / (2 * A * a * a * max(f_I, 1e-6))
    P_trap_total = N * (P_beam * arc["h_mean"] / arc["single"] if arch == "room_push" else 2 * P_beam * arc["h_mean"] / arc["h_worst"])
    P_head = P_trap_total / arc["heads"]
    # --- pump beams
    P_pump_beam = P_abs_pump / (n_pump * A_pump * icp) if math.isfinite(P_abs_pump) else math.inf
    P_pump_total = N * n_pump * P_pump_beam
    wall_lm = 683 * ph.V(pump_lam) * whitener_gain * P_pump_total * (1 - icp * A_pump)
    ael_t, ael_p = sf.ael_class1(1550), sf.ael_class1(pump_lam)
    fails = []
    if runaway or T_face > T_max:
        fails.append("heat")
    # 1550 nm is a corneal hazard: all trap beams converging on one mote cross at its focus, so an eye placed there
    # receives their SUM (focus_sum, added after M12). Push: worst-direction total = P_beam * h_worst / single;
    # pairs: 2 beams.
    if focus_sum:
        P_focus = P_beam * (arc["h_worst"] / arc["single"] if arch == "room_push" else 2.0)
    else:
        P_focus = P_beam
    if P_focus * k_ov_trap > ael_t:
        fails.append("trap_beam_class")
    if P_head > sf.head_power_limit(1550, R_head):
        fails.append("trap_exit_class")
    if P_pump_beam * k_overlap > ael_p:
        fails.append("pump_beam_class")
    if P_pump_total / arc["heads"] > sf.head_power_limit(pump_lam, pump_R_head):
        fails.append("pump_exit_class")
    if wall_lm / Phi > 0.05:
        fails.append("wall_light")
    return dict(content=content if isinstance(content, str) else f"custom L{L} S{S}", mote=mote, arch=arch, a_um=a * 1e6, v=v, f=f, N=N, channels=N * arc["beams"],
                pump_channels=N * n_pump, eta=eta, h_worst=arc["h_worst"], Tm=Tm, T_face=T_face, dT=Tm - ph.T0,
                w_trap_um=w_t * 1e6, R_ft_um=(R_ft or 0) * 1e6, P_beam_mW=P_beam * 1e3, P_trap_total_W=P_trap_total,
                P_head_W=P_head, P_focus_mW=(P_focus if 'P_focus' in dir() else P_beam) * 1e3, w_pump_um=w_p * 1e6, A_pump=A_pump, icp=icp, P_pump_beam_uW=P_pump_beam * 1e6,
                P_pump_total_mW=P_pump_total * 1e3, lm_per_mote=phi_m, wall_ratio=wall_lm / Phi,
                FOM=ph.figure_of_merit(j1A, k_eff), fails=fails, feasible=not fails)


V_GRID = [0.05 * 1.2 ** k for k in range(26)]


def best_speed(**kw):
    best = None
    for v in V_GRID:
        d = design(v=v, **kw)
        if d["feasible"]:
            best = d
    return best

"""M21: AIR-SV, air-levitated static voxels. The air holds the beads up; light only trims them, in time-shared pulses.

Design principle (T9):
- Holding a mote with light costs per-focus power I(v_rel) * area. B2 makes I independent of size, so the eye/skin
  cap gives v_rel <= P_cap / (I_unit a^2): light-holding favours small motes.
- Lighting a mote for the eye costs spot power p / eta_s, with eta_s ~ 2 a^2 / w^2, and the addressing modes scale as
  A / w^2. Under a fixed Class 1 spot cap that is M ~ A p / (a^2 P_cap): visibility favours big motes.
- Way out: let the AIR carry the weight (an upward laminar column at U = v_s of size-sorted white beads), and use
  light only for small trims.

Model per bead (radius a, density rho, ITO-type IR skin on a white visible-scattering body):
- U = v_s (Schiller-Naumann drag); Re; Stokes response time tau_p; thermal time tau_th = rho c a^2 / (3 k_g).
- Trim speed du the light must supply:
  - Stokeslet interactions with neighbours at spacing delta: 0.75 (a/delta) U per neighbour, 2 neighbours [DERIVED]
    (static and predictable; a fraction f_comp can be pre-compensated by design);
  - size tolerance: 2 * size spread * U;
  - column turbulence: Tu * U.
- Trim intensity: I = I_unit * du, with I_unit = 1.5e7 W/m^2 per m/s (RT7 realistic skin; size-independent).
- Trim spot w_t = 1.5 a. Mean per-focus power P_t = h I pi w_t^2 / 2, against the skin limit (0.785 mW, 1 mm, 10 s)
  and the eye limit (10 mW / stacking 3).
- Time-shared pulsed trims: one galvo beam visits K beads round-robin.
  - Each visit lasts t_dwell (0.1 ms incl. a small step); revisit period T_rev = K t_dwell.
  - A bead drifts freely between kicks by du * T_rev (must stay << w_v).
  - Peak power K * P_t; pulse energy K * P_t * t_dwell, against rule 1 (7.85 mJ through 1 mm, t < 0.35 s).
  - Temperature rise per kick: K P_abs t_dwell / (m c).
  - Galvo etendue per axis: D*theta >= 1.5 lam L / (pi w_t).
- Visible lighting: static holographic spots of waist w_v, the largest allowed by visible Class 1 per pupil:
  2 beams * stacking 3 * P_spot <= 0.39 mW. The modes per head follow from w_v (m18 counting).
- The warm-hand plume (0.035-0.4 m/s, m18d) and cross-drafts against the trim authority.

Run: python3 m21_airsv.py -> results/m21_airsv.json, results/m21_run.log
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MU, G, RHO_A, KG = 1.81e-5, 9.81, 1.2, 0.026
I_UNIT = 1.5e7
V500 = 683 * 0.323
SKIN, EYE = 0.785e-3, 10e-3


def v_settle(a, rho):
    v = 2 * rho * G * a * a / (9 * MU)
    for _ in range(40):
        Re = RHO_A * v * 2 * a / MU
        v = 2 * rho * G * a * a / (9 * MU) / (1 + 0.15 * Re ** 0.687)
    return v


def airsv(a=40e-6, rho=600.0, cp=800.0, spread=0.0025, Tu=0.002, delta=3e-3, f_comp=0.8, h=2.0, L=3.0, field=0.6,
          K=1000, t_dwell=1e-4, heads=4, n_beads=1667, F_per_P_1um=1.7e-5):
    U = v_settle(a, rho)
    Re = RHO_A * U * 2 * a / MU
    m = 4 / 3 * math.pi * a ** 3 * rho
    tau_p = m / (6 * math.pi * MU * a)
    tau_th = rho * cp * a * a / (3 * KG)
    du_int = 2 * 0.75 * a / delta * U * (1 - f_comp)
    du_tol = 2 * spread * U
    du_tu = Tu * U
    du = du_int + du_tol + du_tu
    I = I_UNIT * du
    w_t = 1.5 * a
    P_t = h * I * math.pi * w_t ** 2 / 2                       # mean per-focus trim power
    F_drag = 6 * math.pi * MU * a * du
    P_abs = F_drag / (F_per_P_1um * 1e-6 / a)                 # force per absorbed watt ~ 1/a (continuum)
    dT_mean = P_abs / (4 * math.pi * a * KG)
    T_rev = K * t_dwell
    drift = du * T_rev
    P_peak = K * P_t
    E_pulse = P_peak * t_dwell
    dT_kick = K * P_abs * t_dwell / (m * cp)
    etendue = 1.5 * 1.55e-6 * field / (math.pi * w_t)          # m rad per axis for the trim galvo
    beams_per_head = math.ceil(n_beads * h / heads / K)
    # visible: per-bead scattered power for a 1 mm line at luminance L sampled every delta (static, duty 1), q = 0.3
    J = L * 1e-3 * delta
    p_sc = 4 * math.pi * J / 0.3 / V500                        # W intercepted in total (2 beams)
    P_spot_max = 0.39e-3 / (3 * 2)
    eff_min = (p_sc / 2) / P_spot_max
    w_v = a * math.sqrt(2 / eff_min) if eff_min < 1 else a      # eta ~ 2a^2/w^2 for w >> a
    modes_head = (2 * 1.2 * 1.5 * field / (math.pi * w_v)) ** 2
    P_vis = n_beads * 2 * P_spot_max / 0.5
    return dict(a_um=a * 1e6, rho=rho, U=U, Re=Re, tau_p_ms=tau_p * 1e3, tau_th_ms=tau_th * 1e3, du_mm_s=du * 1e3,
                du_int=du_int * 1e3, du_tol=du_tol * 1e3, du_tu=du_tu * 1e3, I_trim=I, P_trim_mW=P_t * 1e3,
                skin_ok=P_t <= SKIN, eye_ok=P_t <= EYE / 3, P_abs_uW=P_abs * 1e6, dT_mean=dT_mean, T_rev_ms=T_rev * 1e3,
                drift_um=drift * 1e6, P_peak_W=P_peak, E_pulse_mJ=E_pulse * 1e3, rule1_ok=E_pulse <= 7.85e-3,
                dT_kick=dT_kick, etendue_mmrad=etendue * 1e3, trim_beams_per_head=beams_per_head, w_v_um=w_v * 1e6,
                modes_head=modes_head, P_vis_W=P_vis, hand_plume_ratio=(0.035 / du, 0.1 / du))


def main():
    rows = []
    print(f"{'a':>4s} {'rho':>5s} {'U':>6s} {'Re':>5s} {'tau_p':>6s} {'tau_th':>6s} {'du':>5s} {'Ptrim':>6s} {'skin':>4s} "
          f"{'dT':>5s} {'drift':>6s} {'Ppeak':>6s} {'Epulse':>7s} {'dTkick':>6s} {'D*th':>5s} {'beams':>5s} {'w_v':>5s} "
          f"{'modes/hd':>8s} {'hand/du':>9s}")
    for rho in (300.0, 600.0, 1200.0):
        for a in (20e-6, 30e-6, 40e-6, 60e-6):
            for spread in (0.0025, 0.001):
                d = airsv(a=a, rho=rho, spread=spread)
                rows.append(d)
                print(f"{d['a_um']:4.0f} {rho:5.0f} {d['U']:6.3f} {d['Re']:5.2f} {d['tau_p_ms']:6.1f} {d['tau_th_ms']:6.1f} "
                      f"{d['du_mm_s']:5.2f} {d['P_trim_mW']:6.3f} {'ok' if d['skin_ok'] else 'X':>4s} {d['dT_mean']:5.1f} "
                      f"{d['drift_um']:6.0f} {d['P_peak_W']:6.2f} {d['E_pulse_mJ']:7.3f} {d['dT_kick']:6.1f} "
                      f"{d['etendue_mmrad']:5.1f} {d['trim_beams_per_head']:5d} {d['w_v_um']:5.0f} {d['modes_head']:8.1e} "
                      f"{d['hand_plume_ratio'][0]:4.0f}-{d['hand_plume_ratio'][1]:<4.0f}")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m21_airsv.json"), "w") as fh:
        json.dump(rows, fh, indent=1, default=float)


if __name__ == "__main__":
    main()

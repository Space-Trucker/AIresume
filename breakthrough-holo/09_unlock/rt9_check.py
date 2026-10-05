"""RT9: red-team checks on T9 (FLOW-R2) and m22/m23. Every number has a formula.

Each block is one attack. Results -> results/rt9_checks.json and stdout. Imports m23 read-only to reuse its model.
No repository file is edited by this script.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m23_flowr2 as m23  # noqa: E402

H, Cc, LAM_P, LAM_V = 6.626e-34, 3e8, 850e-9, 520e-9
MU, G, RHO_A = 1.81e-5, 9.81, 1.2
out = {}


def sci(x):
    return float(x)


# ----------------------------------------------------------------- 1. camera aperture vs depth of field vs photons
def block_aperture():
    """The photon budget uses a 35 mm aperture; the ghost gating assumes a 0.5-1 mm line-of-sight width (eps).
    A lens of aperture A focused at z_0 blurs a point at depth dz to a circle of confusion c = A*|dz|/(z_0+dz)~A*dz/z0.
    So the line-of-sight tube width across a +-0.4 m column is set by A, not by the pixel. Reconcile the two."""
    z0 = 1.6
    col_half = 0.4                      # column depth +- 0.4 m (m23 box z in [0.75,1.65] about 1.2)
    r = {}
    for A in (0.035, 0.010, 0.002):
        c_edge = A * col_half / z0      # circle of confusion at the near/far column edge
        c_mid = A * 0.1 / z0
        r[f"A_{A*1e3:.0f}mm"] = dict(coc_edge_mm=c_edge*1e3, coc_at_0p1m_mm=c_mid*1e3)
    # photons scale with A^2 (collection solid angle). m23 base uses A=35 mm -> 13236 e-.
    base = m23.flowr2(S=3.08)
    e_base, A_base = base["probe_electrons"], 0.035
    for A in (0.002, 0.010):
        r[f"A_{A*1e3:.0f}mm"]["electrons_per_crossing"] = e_base * (A/A_base)**2
        r[f"A_{A*1e3:.0f}mm"]["frames_at_1kHz"] = (2*0.35e-3/base_Uf()) / 1e-3
    r["A_35mm"] = dict(coc_edge_mm=0.035*col_half/z0*1e3, electrons_per_crossing=e_base)
    # aperture needed for eps=0.5 mm DoF across the column
    r["A_for_eps0.5mm_over_column"] = 0.5e-3 * z0 / col_half
    return r


def base_Uf():
    v_s = 2*1520*G*(7e-6)**2/(9*MU)
    return 0.25 + v_s


# ----------------------------------------------------------------- 2. look-ahead wander vs spot size
def block_wander():
    Uf = base_Uf()
    rows = {}
    for Tu in (0.01, 0.02, 0.05, 0.10):
        for Delta in (6e-3, 1.5e-3, 1.0e-3):
            t_lead = Delta/Uf
            wander = Tu*0.25*t_lead     # ballistic sigma = u' * t, u'=Tu*U
            rows[f"Tu{Tu*100:.0f}%_D{Delta*1e3:.1f}mm"] = dict(t_lead_ms=t_lead*1e3, wander_mm=wander*1e3)
    # spot radii and the power penalty of enlarging the spot to catch the wander (eff ~ 2a^2/w^2, P ~ 1/eff)
    a = 7e-6
    spots = {}
    for w in (80e-6, 140e-6, 300e-6, 600e-6):
        eff = (1-math.exp(-2*a*a/(w*w)))*0.9
        spots[f"w_{w*1e6:.0f}um"] = dict(eff=eff, rel_power_vs_140um=((1-math.exp(-2*a*a/(140e-6)**2))*0.9)/eff)
    # draft deflection over the look-ahead (common-mode, steady cross-draft)
    drafts = {uc: uc*(6e-3/Uf)*1e3 for uc in (0.02, 0.05, 0.1)}
    return dict(wander=rows, spots=spots, Uf=Uf, draft_shift_mm_over_6mm={f"{k*1e3:.0f}mm/s": v for k, v in drafts.items()})


# ----------------------------------------------------------------- 3. visible flash: repetitive-pulse C5 = N^-0.25
def block_repetitive():
    """IEC 60825-1 repetitive-pulse for the eye (visible, retinal thermal): take the MOST restrictive of
    rule 1 (single pulse <= AEL_1), rule 2 (mean power over T <= CW AEL) and rule 3 (per-pulse <= AEL_1 * C5),
    C5 = N^-0.25 over N pulses in the time base T. m23 applies ONLY rule 1. A fixating eye sees one image
    sample re-lit at f_r (one mote-crossing flash each), so N = f_r * T."""
    def ael1(t):
        return 7e-4 * t**0.75           # J, Class 1 retinal thermal, 400-700 nm, point source
    rows = {}
    for (name, t_f, E_flash, f_flash) in (
            ("room 20Hz w140 (3.9 ms)", 3.9e-3, 5.15e-6, 20.0),
            ("room 20Hz w80 (3.9 ms)", 3.9e-3, 5.15e-6/ (0.44/1.33), 20.0),  # same E_flash (luminance-fixed)
            ("room 1 ms flash", 1.0e-3, 5.15e-6, 20.0),
            ("30 Hz w140", 3.9e-3, 5.15e-6, 30.0)):
        a1 = ael1(t_f)
        cw = 0.39e-3                    # 520 nm CW Class 1 AEL (thermal), W
        E_flash = 5.15e-6               # luminance-fixed energy per crossing, independent of w_v
        P_peak = E_flash/t_f
        for T in (0.25, 10.0, 100.0):
            N = f_flash*T
            C5 = N**-0.25
            rule1 = E_flash/a1
            rule2 = (P_peak*t_f*f_flash)/cw      # mean power / CW AEL
            rule3 = E_flash/(a1*C5)
            rows[f"{name}_T{T:.0f}s"] = dict(N=N, C5=C5, rule1=rule1, rule2=rule2, rule3=rule3,
                                             worst=max(rule1, rule2, rule3))
    return rows


# ----------------------------------------------------------------- 4. probe fan eye/skin (850 nm) near field
def block_probe_eye():
    """0.2 W of 850 nm, ~1027 pencils from a ceiling projector. Class 1 small-source AEL at 850 nm:
    3.9e-4 * C4, C4 = 10^(0.002*(850-700)). Check (a) one pencil, (b) a near pupil that collects many pencils,
    (c) the whole 0.2 W into a 7 mm pupil at close range, (d) skin of a hand in the fan."""
    C4 = 10**(0.002*(850-700))
    ael_eye = 3.9e-4 * C4               # W, CW small source through 7 mm
    P_pencil, P_tot = 0.2e-3, 0.205
    # near pupil: exit aperture ~2 cm; at distance d the 0.2 W fills a cone to the 0.8 m column at 1.25 m below.
    rows = {}
    for d in (0.1, 0.2, 0.5, 1.25):
        footprint = 0.02 + (0.8-0.02)*(d/1.25)      # linear spread from 2 cm exit to 0.8 m at the image
        area = math.pi*(footprint/2)**2
        pupil = math.pi*(3.5e-3)**2
        P_in = P_tot*min(1.0, pupil/area)
        rows[f"d_{d*100:.0f}cm"] = dict(footprint_m=footprint, P_pupil_mW=P_in*1e3, over_ael=P_in/ael_eye)
    # skin MPE 850 nm, 10 s exposure ~ 2000 * C4 W/m^2 (IEC skin, 700-1050 nm) through 3.5 mm
    skin_mpe_Wm2 = 2000*C4
    skin_limit_through_ap = skin_mpe_Wm2 * math.pi*(3.5e-3/2)**2
    return dict(C4=C4, ael_eye_mW=ael_eye*1e3, one_pencil_over_ael=P_pencil/ael_eye,
                near_pupil=rows, skin_mpe_Wm2=skin_mpe_Wm2, skin_limit_mW=skin_limit_through_ap*1e3,
                pencils_in_7mm_pupil_at_column=max(1.0, (7e-3/ (0.8/math.sqrt(1027)))**2))


# ----------------------------------------------------------------- 5. room particle load vs WHO, deposition split
def block_particles():
    r = {}
    for eta in (0.999, 0.9997, 0.99):
        base = m23.flowr2(S=3.08, eta_c=eta)
        r[f"eta_{eta}"] = dict(room_ug_m3=base["room_ug_m3"], g_per_h=base["g_per_h"])
    # deposition vs ventilation split of k_loss
    v_s = 2*1520*G*(7e-6)**2/(9*MU)
    k_vent, k_dep = 0.5/3600, v_s/2.5
    r["k_loss_split"] = dict(k_vent=k_vent, k_dep=k_dep, frac_to_surfaces=k_dep/(k_vent+k_dep))
    # escaped mass that lands on surfaces per 8 h day at 99.9% capture
    base = m23.flowr2(S=3.08)
    esc_g_h = base["g_per_h"]*0.001
    r["escaped_g_per_h"] = esc_g_h
    r["surface_g_per_8h"] = esc_g_h*8*(k_dep/(k_vent+k_dep))
    r["WHO_PM10_24h_ug_m3"] = 45.0
    r["ACGIH_inhalable_mg_m3"] = 10.0
    r["in_column_mg_m3"] = base["mass_mg_m3"]
    return r


# ----------------------------------------------------------------- 6. vertical coverage at longer eye time
def block_coverage():
    Uf = base_Uf()
    n = m23.flowr2(S=3.08)["n_per_m3"]
    r = {}
    for t_eye in (0.05, 0.10, 0.15):
        r[f"t_eye_{t_eye*1e3:.0f}ms"] = dict(vert_cov=min(1.0, n*(1e-3)**2*Uf*t_eye),
                                             p_drop=math.exp(-1*20*t_eye))
    return r


# ----------------------------------------------------------------- 7. m22 spot-checks
def block_m22():
    EPS0 = 8.854e-12
    # Laplace low-pass for 6 mm period at 5 cm
    atten = math.exp(-2*math.pi*0.05/6e-3)
    # thermal kick limit: T_rev/tau for the closed form
    def kick(K, t_d, tau):
        T = K*t_d
        return K*(1-math.exp(-t_d/tau))/(1-math.exp(-T/tau))
    tau_40 = 600*800*(40e-6)**2/(3*0.026)
    # E pump bound sanity (InGaAsP best case), order of magnitude only
    return dict(laplace_6mm_5cm=atten, kick_1000_40um=kick(1000, 1e-4, tau_40), tau_th_40um_ms=tau_40*1e3)


# ----------------------------------------------------------------- 8. ghost MC with a realistic (blur) eps
def block_ghost_blur():
    """Re-run m23's own ghost MC at eps values that match the defocus blur of the 35 mm aperture
    (coc ~ 2-9 mm across the column) to see how the 2-camera ghost ratio grows."""
    from m23_flowr2 import armor_samples, ghost_counts, ghost_ratio, flowr2
    P, _ = armor_samples()
    Pw = P + np.array([0.0, 0.0, 1.2])
    box = (np.array([-0.4, -0.4, 0.75]), np.array([0.4, 0.4, 1.65]))
    Bpos = np.array([0.35, 0.0, 2.45])
    cams = [np.array([-1.4, 0.9, 2.3]), np.array([1.0, -1.3, 2.3]), np.array([-0.2, 1.6, 2.3])]
    n = flowr2(S=3.08)["n_per_m3"]
    r = {}
    for eps in (0.5e-3, 1.0e-3, 2.0e-3, 4.0e-3):
        gs = np.array([ghost_counts(Pw, Bpos, cam, eps, box) for cam in cams])
        r_vox = n*0.25*(2*0.35e-3)*(2*eps)
        ratio2 = float(np.mean(ghost_ratio(gs[:2], r_vox, 2e-3)))
        ratio3 = float(np.mean(ghost_ratio(gs, r_vox, 2e-3)))
        r[f"eps_{eps*1e3:.1f}mm"] = dict(g_mean=[float(g.mean()) for g in gs], r_vox=r_vox,
                                         ratio_2cam_2ms=ratio2, ratio_3cam_2ms=ratio3)
    return r


def main():
    out["1_aperture_dof_photons"] = block_aperture()
    out["2_wander_vs_spot"] = block_wander()
    out["3_repetitive_pulse_C5"] = block_repetitive()
    out["4_probe_fan_eye_skin"] = block_probe_eye()
    out["5_particles"] = block_particles()
    out["6_vertical_coverage"] = block_coverage()
    out["7_m22_spotcheck"] = block_m22()
    out["8_ghost_blur"] = block_ghost_blur()

    print("\n=== 1. camera aperture vs depth of field vs photons ===")
    for k, v in out["1_aperture_dof_photons"].items():
        print(f"  {k}: {v}")
    print("\n=== 2. look-ahead wander vs spot ===")
    for k, v in out["2_wander_vs_spot"]["wander"].items():
        print(f"  {k}: t_lead {v['t_lead_ms']:.1f} ms, wander {v['wander_mm']:.3f} mm")
    print("  spots:", {k: round(v["rel_power_vs_140um"], 2) for k, v in out["2_wander_vs_spot"]["spots"].items()})
    print("  draft shift over 6 mm:", out["2_wander_vs_spot"]["draft_shift_mm_over_6mm"])
    print("\n=== 3. visible repetitive-pulse (worst of rules 1/2/3; >1 = over Class 1) ===")
    for k, v in out["3_repetitive_pulse_C5"].items():
        print(f"  {k}: N {v['N']:.0f} C5 {v['C5']:.3f} | rule1 {v['rule1']:.2f} rule2 {v['rule2']:.2f} "
              f"rule3 {v['rule3']:.2f} -> worst {v['worst']:.2f}")
    print("\n=== 4. probe fan eye/skin (850 nm) ===")
    pe = out["4_probe_fan_eye_skin"]
    print(f"  C4 {pe['C4']:.2f}, eye AEL {pe['ael_eye_mW']:.2f} mW, one pencil/AEL {pe['one_pencil_over_ael']:.2f}")
    for k, v in pe["near_pupil"].items():
        print(f"    near pupil {k}: P {v['P_pupil_mW']:.3f} mW, over AEL {v['over_ael']:.2f}")
    print(f"  skin MPE {pe['skin_mpe_Wm2']:.0f} W/m^2 -> {pe['skin_limit_mW']:.2f} mW through 3.5 mm")
    print("\n=== 5. room particles ===")
    for k, v in out["5_particles"].items():
        print(f"  {k}: {v}")
    print("\n=== 6. vertical coverage / dropouts vs eye time ===")
    for k, v in out["6_vertical_coverage"].items():
        print(f"  {k}: vert_cov {v['vert_cov']:.2f}, p_drop {v['p_drop']:.3f}")
    print("\n=== 7. m22 spot-check ===", out["7_m22_spotcheck"])
    print("\n=== 8. ghost MC vs eps (defocus blur) ===")
    for k, v in out["8_ghost_blur"].items():
        print(f"  {k}: g_mean {[round(x,2) for x in v['g_mean']]} r_vox {v['r_vox']:.1f} "
              f"2cam {v['ratio_2cam_2ms']:.4f} 3cam {v['ratio_3cam_2ms']:.5f}")

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "rt9_checks.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))


if __name__ == "__main__":
    main()

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

# motes: j1A, k_eff (W/m/K), A_trap (1550 nm), q_side (fraction of pi a^2 scattered into side directions at ~500 nm),
# T_max (K), density (kg/m^3)
MOTES = {
    # carbon aerogel (RF-derived), rho ~100 kg/m^3: k_eff 0.03-0.05 W/m/K at 1 atm (bulk literature range; not measured at
    # um size), glassy-carbon-like absorption diluted by 5 % solid -> alpha ~ 5e5-1.5e6 1/m, skin-like at a = 5 um.
    # q_side: a black sphere's side scatter is mostly surface reflection (Fresnel ~4-8 %) [ESTIMATE].
    "carbon_aerogel": dict(j1A=0.40, k_eff=0.045, A=0.95, q_side=0.05, T_max=600.0, rho=100.0),
    "carbon_aerogel_pess": dict(j1A=0.30, k_eff=0.08, A=0.90, q_side=0.03, T_max=550.0, rho=150.0),
    # v4 reference mote (ITO skin on silica aerogel), white-ish: higher side scatter
    "ito_aerogel": dict(j1A=0.486, k_eff=0.04, A=1.0, q_side=0.3, T_max=600.0, rho=150.0),
}

ROOMS = {"quiet": dict(u=0.10, u_res=0.01), "normal": dict(u=0.30, u_res=0.03)}
DEVICES = {  # hologram device: pixels, frame rate (Hz), efficiency into the spots
    "LCoS_4K": dict(px=8.8e6, rate=360.0, eff=0.6),
    "PLM_MEMS": dict(px=1.3e6, rate=1440.0, eff=0.5),
}
V_CYAN = 683 * ph.V(500)          # lm/W at 500 nm


def design(content="sketch", delta=1.5e-3, a=5e-6, mote="carbon_aerogel", room="quiet", device="LCoS_4K",
           D_field=1.0, safety="curtain", theta_det=0.02, t_cut=1.4e-3, C_ph=0.85, force_margin=1.3, eta_shape=0.8,
           v_content=0.0, k_track=3.0, R_head=0.25, leak=0.01, n_illum=1, f_zone_max=2e4, r_c_min_mult=3.0):
    L, S, _duty = b2.CONTENT[content]
    Mt, Rm, Dv = MOTES[mote], ROOMS[room], DEVICES[device]
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
    d1 = design(a=2.5e-6, r_c_min_mult=1.0)
    d2 = design(a=5e-6, r_c_min_mult=1.0)
    chk("I_hold independent of a (2.5 vs 5 um)", d1["I_unit_Wm2"], d2["I_unit_Wm2"], 0.15)
    # 2. closed form I = 4 rhoT w/(3 C mu FOM A Cc) x margin (eta = 1, h = 1) at room temperature, small heating
    Mt = MOTES["carbon_aerogel"]
    a = 5e-6
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


if __name__ == "__main__":
    main()

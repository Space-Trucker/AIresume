"""RT10: red-team checks of idea round 5 (EVAP-R), T9 §2.9/§3.5, m24 and m25.

STATUS NOTE. The environment's safety gate blocked every Bash call in the RT10 session after the
first few reads, so this script was WRITTEN BUT NEVER RUN there. Every number in
`05_reviews/red_team_10_evapr.md` was therefore derived by hand from the formulas below, with the
arithmetic shown in the report. Running this file reproduces (and should be used to check) all of it.

Run: python3 rt10_check.py  ->  results/rt10_checks.json, results/rt10_run.log

Part A  drop physics: wet-bulb closure (sphere balance vs psychrometric), d^2-law lifetime, fall with
        shrinkage, deposition at a given pendant height, the RH at which a surface stays dry, in-jet
        vapour feedback, satellites, coalescence (Saffman-Turner + differential sedimentation),
        residue per drop vs water TDS, glove impaction.
Part B  optics: geometric-optics checks of the Mie table (Fresnel external reflection at 90 deg,
        Lambert sphere phase function), head-ring phase sums, required beam power, the
        beam-streak/image luminance invariant, floor glare, haze, scanned-beam Class 1 recess.
Part C  aim: opus round 5 §3.1 estimator (window fit + Heisenberg-Yaglom bias) swept over wake
        strength, drop-inertia filtering, photon-limited centroid noise, and the 200 fps variant.
Part D  rendering: the m23b/RT9 fill law with the flow angle, and the cost of flow-normal.
Part E  m25/m24: turbulence spectrum moments, the delay-limited loop-gain law, the P/cap closed form,
        the feedforward variant, and the O-band cap/tetralemma reproduction.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")

# ---------------------------------------------------------------- constants
KA, LV, DV = 0.0257, 2.46e6, 2.45e-5          # W/m/K, J/kg, m^2/s  (air at ~20 C)
RHO_W, MU, G, NU = 998.0, 1.81e-5, 9.81, 1.5e-5
RHO_A, CP_A = 1.2, 1006.0
V520, KM = 0.71, 683.0                         # photopic V(520 nm), lm/W
I_UNIT = 1.5e7                                 # T6 force-per-intensity (speed units)
AEL_CW = 3.9e-4                                # visible Class 1 CW, 7 mm (W)
AEL_SKIN_VIS = 2000.0 * math.pi * 0.5e-3 ** 2  # EN 50689 1 mm, 400-1400 nm (W) = 1.571 mW


def psat(Tc):
    return 610.94 * math.exp(17.625 * Tc / (Tc + 243.04))


def rho_v(Tc, RH=1.0):
    return RH * psat(Tc) / (461.5 * (Tc + 273.15))


def Ts_sphere(T, RH):
    """Drop-surface temperature from the Nu=Sh=2 balance k_a (T-Ts) = L_v D_v (rho_s(Ts)-rho_inf)."""
    rinf = rho_v(T, RH)
    f = lambda Ts: KA * (T - Ts) - LV * DV * (rho_v(Ts) - rinf)
    lo, hi = -30.0, T
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def Tw_psychro(T, RH, P=101325.0):
    """Psychrometric wet bulb, cp (T-Tw) = L (w_s(Tw)-w): the boundary-layer (Le^2/3) closure."""
    w = 0.622 * RH * psat(T) / (P - RH * psat(T))
    f = lambda Tw: CP_A * (T - Tw) - LV * (0.622 * psat(Tw) / (P - psat(Tw)) - w)
    lo, hi = -30.0, T
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def d_of_V(V):
    return (6 * V / math.pi) ** (1 / 3)


def lifetime(d0, T, RH):
    Ts = Ts_sphere(T, RH)
    drho = rho_v(Ts) - rho_v(T, RH)
    return RHO_W * d0 * d0 / (8 * DV * drho), Ts, drho


def v_stokes(d):
    return RHO_W * G * d * d / (18 * MU)


def fall_to_vanish(d0, tL, U):
    """z = U t + v0 (t - t^2/(2 tL)) evaluated at t = tL (v_s ~ d^2 ~ (1-t/tL))."""
    return (U + 0.5 * v_stokes(d0)) * tL


def time_to_height(d0, tL, U, H):
    """Solve U t + v0 (t - t^2/(2 tL)) = H; None if the drop vanishes first."""
    v0 = v_stokes(d0)
    a, b = v0 / (2 * tL), U + v0
    disc = b * b - 4 * a * H
    if disc < 0:
        return None
    t = (b - math.sqrt(disc)) / (2 * a)
    return t if t <= tL else None


# ---------------------------------------------------------------- Part A
def part_a(log):
    out = {}
    T = 20.0
    log("== A1 wet-bulb closure and lifetime (30 pL = 38.6 um) ==")
    log(f"  Lewis number Le = (k_a/(rho_a cp_a))/D_v = {(KA / (RHO_A * CP_A)) / DV:.3f};"
        f" sphere/psychrometric depression ratio = 1/Le")
    rows = []
    for RH in (0.3, 0.32, 0.5, 0.7, 0.8):
        for Vd in (3e-15, 1e-14, 3e-14, 4.1e-14):
            d0 = d_of_V(Vd)
            tL, Ts, drho = lifetime(d0, T, RH)
            Tw = Tw_psychro(T, RH)
            drho_p = rho_v(Tw) - rho_v(T, RH)
            tL_p = RHO_W * d0 * d0 / (8 * DV * drho_p)
            z = fall_to_vanish(d0, tL, 0.25)
            rows.append(dict(RH=RH, V_pL=Vd * 1e12, d0_um=d0 * 1e6, Ts_C=Ts, Tw_psy_C=Tw,
                             drho_g_m3=drho * 1e3, tL_s=tL, tL_psychro_s=tL_p,
                             short_by_pct=100 * (1 - tL_p / tL), vanish_m=z))
            log(f"  RH {RH:.0%} {Vd * 1e12:5.1f} pL d0 {d0 * 1e6:5.1f} um: Ts {Ts:5.2f} C (psy {Tw:5.2f}),"
                f" drho {drho * 1e3:4.2f} g/m3, tL {tL:5.2f} s (psy {tL_p:5.2f}, {100 * (1 - tL_p / tL):4.1f}% short),"
                f" vanish {z:5.2f} m")
    out["lifetimes"] = rows

    log("== A2 deposition below a pendant of height H (U 0.25 m/s) ==")
    dep = []
    for H in (0.5, 0.8, 1.6):
        for Vd in (1e-14, 3e-14, 4.1e-14):
            d0 = d_of_V(Vd)
            for RH in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
                tL, _, _ = lifetime(d0, T, RH)
                t = time_to_height(d0, tL, 0.25, H)
                if t is None:
                    dep.append(dict(H=H, V_pL=Vd * 1e12, RH=RH, dry=True))
                    continue
                frac_d2 = 1 - t / tL
                mfrac = frac_d2 ** 1.5
                flux = 1.6e5 if Vd <= 3e-14 else 2.9e5
                g_h = flux * Vd * RHO_W * mfrac * 3600 * 1e3
                area = 0.04 if Vd <= 3e-14 else 0.045
                # surface evaporation capacity, h_m ~ 0.0145 m/s at 0.25 m/s over a 0.2 m patch
                cap = 0.0145 * (rho_v(T) - rho_v(T, RH)) * 3600 * 1e3
                dep.append(dict(H=H, V_pL=Vd * 1e12, RH=RH, dry=False, d_arrive_um=d0 * 1e6 * frac_d2 ** 0.5,
                                mass_frac=mfrac, g_h=g_h, g_m2_h=g_h / area, surf_cap_g_m2_h=cap,
                                wets=g_h / area > cap))
                log(f"  H {H:.1f} m {Vd * 1e12:4.1f} pL RH {RH:.0%}: arrives {d0 * 1e6 * frac_d2 ** 0.5:5.1f} um,"
                    f" {mfrac:5.3f} of mass, {g_h:5.2f} g/h = {g_h / area:6.1f} g/m2/h"
                    f" (surface can take {cap:5.0f}) {'WET' if g_h / area > cap else 'damp only'}")
    out["deposition"] = dep

    log("== A3 the RH that keeps a surface at height H dry ==")
    thr = []
    for H in (0.5, 0.8, 1.6):
        for Vd in (1e-14, 3e-14, 4.1e-14):
            d0 = d_of_V(Vd)
            lo, hi = 0.05, 0.98
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                tL, _, _ = lifetime(d0, T, mid)
                if fall_to_vanish(d0, tL, 0.25) < H:
                    lo = mid
                else:
                    hi = mid
            thr.append(dict(H=H, V_pL=Vd * 1e12, RH_max=0.5 * (lo + hi)))
            log(f"  H {H:.1f} m, {Vd * 1e12:4.1f} pL: dry only at RH <= {50 * (lo + hi):4.1f} %")
    out["rh_thresholds"] = thr

    log("== A4 in-jet vapour feedback ==")
    fb = []
    for name, g_h, area, U in (("desk 0.2 m core", 17.3, 0.04, 0.2724), ("room seeded 0.045 m2", 43.0, 0.045, 0.2774)):
        Q = area * U * 3600
        add = g_h / Q
        for RH in (0.3, 0.5, 0.7):
            _, _, drho = lifetime(d_of_V(3e-14), T, RH)
            fb.append(dict(case=name, Q_m3_h=Q, add_g_m3=add, RH=RH, frac_of_drho=add / (drho * 1e3),
                           lifetime_gain_pct=100 * (0.5 * add / (drho * 1e3)) / (1 - 0.5 * add / (drho * 1e3))))
            log(f"  {name}: {Q:5.1f} m3/h, +{add:4.2f} g/m3 = {100 * add / (drho * 1e3):4.1f} % of drho at RH {RH:.0%}")
    out["jet_feedback"] = fb

    log("== A5 coalescence and ventilation ==")
    eps_jet = 0.25 ** 3 / 0.3
    r = 0.5 * d_of_V(3e-14)
    K = 1.3 * math.sqrt(eps_jet / NU) * (2 * r) ** 3
    n = 1.6e7
    rate = K * n
    log(f"  Saffman-Turner at in-jet eps {eps_jet:.3f} m2/s3: K {K:.2e} m3/s, rate {rate:.2e} /s,"
        f" {rate * 2.64:.1e} per lifetime")
    ds = 0.5 * d_of_V(3e-15)
    dv = v_stokes(2 * r) - v_stokes(2 * ds)
    Ksed = math.pi * (r + ds) ** 2 * dv * 0.05
    log(f"  differential sedimentation (E 0.05): dv {dv * 1e2:.2f} cm/s, K {Ksed:.2e} m3/s,"
        f" rate {Ksed * n:.2e} /s")
    Re = v_stokes(2 * r) * 2 * r / NU
    fv = 1 + 0.3 * math.sqrt(Re) * 0.88
    Re_jet = 15.0 * 2 * r / NU
    fv_jet = 1 + 0.3 * math.sqrt(Re_jet) * 0.88
    tau_p = RHO_W * (2 * r) ** 2 / (18 * MU)
    log(f"  ventilation: Re {Re:.3f} -> f_v {fv:.3f} at terminal; Re {Re_jet:.1f} -> f_v {fv_jet:.2f} in a 15 m/s jet"
        f" (tau_p {tau_p * 1e3:.2f} ms, stopping distance {15 * tau_p * 1e3:.0f} mm)")
    tau_T = RHO_W * 4182 * (2 * r) ** 2 / (12 * KA)
    log(f"  thermal relaxation to the wet bulb: {tau_T * 1e3:.1f} ms")
    out["coalescence"] = dict(eps_jet=eps_jet, K_ST=K, rate_ST=rate, K_sed=Ksed, rate_sed=Ksed * n,
                              f_v_terminal=fv, f_v_jet=fv_jet, tau_p_ms=tau_p * 1e3, tau_T_ms=tau_T * 1e3)

    log("== A6 residue per drop vs water quality ==")
    res = []
    for tds in (0.03, 1.0, 10.0, 250.0):          # mg/L
        for Vd, flux in ((3e-14, 1.6e5),):
            m = Vd * 1e3 * tds * 1e-6             # kg per drop (Vd m3 -> L x1e3, mg/L -> kg)
            d = (6 * (m / 2000.0) / math.pi) ** (1 / 3)
            mdot = flux * m * 3600 * 1e6          # mg/h
            c_mass = mdot * 1e3 / 25.0            # ug/m3 at 25 m3/h ventilation
            c_num = flux * 3600 / 25.0 / 1e6      # per cm3
            res.append(dict(tds_mg_L=tds, m_per_drop_fg=m * 1e18, d_um=d * 1e6, mg_h=mdot,
                            ug_m3=c_mass, per_cm3=c_num))
            log(f"  TDS {tds:6.2f} mg/L: {m * 1e18:7.1f} fg/drop -> {d * 1e6:5.2f} um nucleus,"
                f" {mdot:7.3f} mg/h, {c_mass:7.2f} ug/m3, {c_num:.2e} /cm3")
    for frac in (0.001, 0.01, 0.10):
        m = 3e-14 * frac * 1040.0
        d = (6 * (m / 1040.0) / math.pi) ** (1 / 3)
        log(f"  humectant {frac:.1%}: {m * 1e12:6.3f} ng/drop -> {d * 1e6:5.1f} um,"
            f" {1.6e5 * m * 3600 * 1e3:6.2f} g/h deposited")
    out["residue"] = res

    log("== A7 glove impaction ==")
    for rb, label in ((0.008, "finger r 8 mm"), (0.05, "palm r 50 mm")):
        St = tau_p * 0.25 / rb
        eta = max(0.0, (St - 0.125) / (St + 0.4))
        log(f"  {label}: St {St:.3f}, Langmuir-Blodgett eta {eta:.3f}")
    inter = 0.25 * 1.6e5
    log(f"  palm blocking 25 % of a 0.2 m core: {inter:.0e} drops/s x eta 0.03 ->"
        f" {inter * 0.03 * 3e-14 * RHO_W * 3600 * 1e3:.2f} g/h")
    return out


# ---------------------------------------------------------------- Part B
def fresnel(theta_i_deg, m=1.335):
    ti = math.radians(theta_i_deg)
    s, c = math.sin(ti), math.cos(ti)
    q = math.sqrt(m * m - s * s)
    Rs = ((c - q) / (c + q)) ** 2
    Rp = ((m * m * c - q) / (m * m * c + q)) ** 2
    return Rs, Rp, 0.5 * (Rs + Rp)


def p_lambert(theta_deg, omega=0.9):
    a = math.pi - math.radians(theta_deg)
    return omega * (8 / (3 * math.pi)) * (math.sin(a) + (math.pi - a) * math.cos(a))


# opus round 5 §2.3 Mie table for a 38.5 um water drop at 520 nm, for interpolation
P_WATER = [(20, 8.62), (40, 2.41), (60, 0.49), (90, 0.039), (120, 0.051), (140, 0.86), (141, 0.92),
           (150, 0.36), (160, 0.22), (180, 0.20)]


def p_water(theta):
    th = min(max(theta, 20.0), 180.0)
    for (a, pa), (b, pb) in zip(P_WATER, P_WATER[1:]):
        if a <= th <= b:
            f = (th - a) / (b - a)
            return math.exp(math.log(pa) + f * (math.log(pb) - math.log(pa)))
    return P_WATER[-1][1]


def ring_sum(n_heads, elev_deg, pfun, n_az=181):
    """p per unit TOTAL beam power for horizontal viewers at all azimuths (opus §2.3 convention)."""
    el = math.radians(elev_deg)
    vals = []
    for i in range(n_az):
        phiv = 2 * math.pi * i / n_az
        s = 0.0
        for h in range(n_heads):
            phih = 2 * math.pi * h / n_heads
            ct = -math.cos(el) * math.cos(phiv - phih)
            s += pfun(math.degrees(math.acos(max(-1.0, min(1.0, ct)))))
        vals.append(s / n_heads)
    vals.sort()
    return vals[0], vals[len(vals) // 2], vals[-1]


def part_b(log):
    out = {}
    log("== B1 geometric-optics check of the Mie 90 deg value ==")
    Rs, Rp, Rm = fresnel(45.0)
    log(f"  external reflection at theta 90 deg (theta_i 45): p = R = {Rm:.4f}"
        f"  [Rs {Rs:.4f}, Rp {Rp:.5f}, ratio {Rs / Rp:.1f}]  vs opus Mie 0.035-0.055")
    log(f"  Lambert sphere: p(90) {p_lambert(90):.3f} (opus 0.764), p(150) {p_lambert(150):.3f} (opus 2.11)")
    log(f"  side-scatter deficit water/white at 90 deg: {p_lambert(90) / 0.039:.1f}x to {p_lambert(90) / 0.055:.1f}x")
    out["go_check"] = dict(R_mean_45=Rm, Rs=Rs, Rp=Rp, pol_ratio=Rs / Rp,
                           lambert_90=p_lambert(90), lambert_150=p_lambert(150))

    log("== B2 head-ring phase sums (p per unit total beam power) ==")
    rings = []
    for nh, el in ((2, 60), (3, 60), (3, 30), (4, 30), (6, 25), (6, 45), (3, 15)):
        lo, md, hi = ring_sum(nh, el, p_water)
        wl = ring_sum(nh, el, p_lambert)[1]
        rings.append(dict(heads=nh, elev=el, water_min=lo, water_med=md, water_max=hi, white_med=wl,
                          ripple=hi / lo if lo > 0 else None))
        log(f"  {nh} heads el {el:2d}: water {lo:5.2f}/{md:5.2f}/{hi:5.2f} (ripple {hi / lo:4.1f}x),"
            f" white {wl:5.2f}")
    out["rings"] = rings

    log("== B3 required power per lit drop and per head ==")
    pw = []
    L_line, d_s, n = 1.5, 1e-3, 1.6e7
    J = L_line * d_s / (n * d_s * d_s)
    log(f"  J = L d_s/(n d_s^2) = {J:.3e} cd per lit drop")
    for label, a, w, H, p in (("FLOW-R B' trehalose", 7e-6, 80e-6, 2, 0.504),
                              ("FLOW-R 6 low heads", 7e-6, 80e-6, 6, 0.81),
                              ("EVAP-R 4 heads el 30", 15e-6, 140e-6, 4, 0.54),
                              ("EVAP-R 6 heads el 25", 15e-6, 140e-6, 6, 1.04),
                              ("EVAP-R 2 heads el 60", 15e-6, 140e-6, 2, 0.035)):
        cap = 1 - math.exp(-2 * a * a / (w * w))
        P_int = 4 * math.pi * J / (KM * V520 * p)
        P_tot = P_int / cap
        n_lit = 8
        pw.append(dict(case=label, a_um=a * 1e6, w_um=w * 1e6, heads=H, p=p, capture=cap,
                       P_total_mW=P_tot * 1e3, P_beam_uW=P_tot / H * 1e6,
                       per_head_mW=n_lit * P_tot / H * 1e3,
                       vertex_x_AEL=n_lit * P_tot / H / AEL_CW, one_beam_x_AEL=P_tot / H / AEL_CW,
                       lines_to_AEL=AEL_CW / (P_tot / H)))
        log(f"  {label:24s} cap {cap:.4f}  total {P_tot * 1e3:5.3f} mW  beam {P_tot / H * 1e6:6.1f} uW"
            f"  head(8 lines) {n_lit * P_tot / H * 1e3:5.3f} mW = {n_lit * P_tot / H / AEL_CW:5.2f}x AEL"
            f"  lines to AEL {AEL_CW / (P_tot / H):5.1f}")
    out["power"] = pw

    log("== B4 scanned-beam Class 1: the recess that the time average needs ==")
    rec = []
    for label, P_head, fan in (("FLOW-R desk 2 heads", 1.56e-3, 0.333), ("EVAP-R desk 4 heads", 0.40e-3, 0.333),
                               ("EVAP-R desk 6 heads", 0.137e-3, 0.333), ("EVAP-R room 8 heads", 1.9e-3, 0.6)):
        Om = fan * fan
        s = math.sqrt(math.pi * 3.5e-3 ** 2 * P_head / (Om * AEL_CW))
        rec.append(dict(case=label, P_head_mW=P_head * 1e3, recess_mm=s * 1e3))
        log(f"  {label:22s} P_head {P_head * 1e3:5.2f} mW, fan {fan:.2f} rad -> recess >= {s * 1e3:5.1f} mm")
    out["recess"] = rec

    log("== B5 beam streak vs image luminance (the clear-drop trilemma) ==")
    Q = 2.08
    strk = []
    for label, w, H, a, p_bar, p_head, P_beam, D in (
            ("EVAP 4 heads el 30, D 1.0 m", 140e-6, 4, 15e-6, 1.29, 4.5, 50e-6, 1.0),
            ("EVAP 4 heads el 30, D 0.5 m", 140e-6, 4, 15e-6, 1.29, 4.5, 50e-6, 0.5),
            ("EVAP 6 heads el 25, D 1.0 m", 140e-6, 6, 15e-6, 1.29, 6.1, 17.2e-6, 1.0),
            ("EVAP 6 heads el 25, D 0.5 m", 140e-6, 6, 15e-6, 1.29, 6.1, 17.2e-6, 0.5),
            ("FLOW-R white, D 1.0 m", 80e-6, 2, 7e-6, 0.81, 0.86, 195e-6, 1.0)):
        beta = n * Q * math.pi * a * a
        I_line = P_beam * beta * p_head / (4 * math.pi) * KM * V520      # cd per metre of beam
        L_str = I_line / (D * D * 2.909e-4)                              # 1 arcmin eye blur
        cap = 1 - math.exp(-2 * a * a / (w * w))
        P_int = H * P_beam * cap
        L_img = P_int * p_bar / (4 * math.pi) * KM * V520 * n * d_s
        strk.append(dict(case=label, beta=beta, L_streak=L_str, L_image=L_img, ratio=L_str / L_img,
                         x_dark_wall=L_str / (0.05 * 10 / math.pi)))
        log(f"  {label:30s} beta {beta:.4f}/m  streak {L_str:7.4f} cd/m2  image {L_img:5.2f} cd/m2"
            f"  ratio {100 * L_str / L_img:5.1f} %  = {L_str / (0.05 * 10 / math.pi):6.2f}x a rho .05 wall at 10 lux")
    out["streaks"] = strk

    log("== B6 haze and floor glare ==")
    hz = []
    for a in (15e-6, 19.3e-6):
        tau = n * Q * math.pi * a * a * 0.2
        for p_room, name in ((0.635, "water"), (0.866, "white")):
            L = tau * p_room * 20.0 / (4 * math.pi)
            hz.append(dict(a_um=a * 1e6, medium=name, tau_pct=tau * 100, L_haze=L,
                           contrast_dark=L / (0.05 * 10 / math.pi), contrast_lit=L / (0.5 * 100 / math.pi)))
            log(f"  a {a * 1e6:4.1f} um {name}: tau {tau * 100:5.2f} % -> {L:.5f} cd/m2 ="
                f" {100 * L / (0.05 * 10 / math.pi):5.2f} % of a dark wall, {100 * L / (0.5 * 100 / math.pi):5.3f} % of a lit wall")
    out["haze"] = hz
    for P_beam, path, rho in ((50e-6, 2.2, 0.2), (50e-6, 2.2, 0.02), (195e-6, 2.2, 0.2)):
        wz = 140e-6 * math.sqrt(1 + (path / 0.12) ** 2)
        E = P_beam * KM * V520 / (math.pi * wz * wz)
        log(f"  beam {P_beam * 1e6:5.1f} uW at {path} m past focus: radius {wz * 1e3:4.2f} mm,"
            f" {E:8.0f} lux -> {rho * E / math.pi:8.1f} cd/m2 on rho {rho}")
    return out


# ---------------------------------------------------------------- Part C
def aim_sigma(sig_c, tau, N, Delta, a_rms):
    """opus round 5 §3.1: constant-velocity window fit, prediction h ahead of the window centre."""
    S = tau * tau * N * (N * N - 1) / 12.0
    h = Delta + 0.5 * (N - 1) * tau
    noise = sig_c * math.sqrt(1.0 / N + h * h / S)
    bias = 0.5 * a_rms * (h * h - S / N)
    return math.hypot(noise, bias), noise, bias, h, S


def part_c(log):
    out = {}
    log("== C1 Heisenberg-Yaglom accelerations and the aim miss ==")
    rows = []
    tau_p = RHO_W * d_of_V(3e-14) ** 2 / (18 * MU)
    for name, u, L, a0 in (("core", 0.025, 0.04, 2.0), ("gloved wake u' 0.1", 0.1, 0.08, 2.3),
                           ("bare hand u' 0.2", 0.2, 0.08, 3.0), ("bare hand u' 0.3", 0.3, 0.08, 3.5),
                           ("bare hand u' 0.4", 0.4, 0.08, 3.8)):
        eps = u ** 3 / L
        tau_eta = math.sqrt(NU / eps)
        a_f = math.sqrt(a0 * eps ** 1.5 / math.sqrt(NU))
        St = tau_p / tau_eta
        a_d = a_f / math.sqrt(1 + (2 * math.pi * St) ** 2) if St > 0.3 else a_f * (1 - 1.0 * St)
        lam = math.sqrt(15 * NU * u * u / eps)
        for sig_c in (10e-6, 20e-6, 30e-6):
            for Delta, tau, N in ((3e-3, 1e-3, 5), (5e-3, 1e-3, 5), (8e-3, 5e-3, 5)):
                sig, nz, bi, h, S = aim_sigma(sig_c, tau, N, Delta, a_d)
                hits = {f"w{int(w * 1e6)}": 1 - math.exp(-(w / 2) ** 2 / (2 * sig * sig))
                        for w in (80e-6, 140e-6, 200e-6)}
                rows.append(dict(region=name, eps=eps, tau_eta_ms=tau_eta * 1e3, Re_lam=u * lam / NU,
                                 a_fluid=a_f, a_drop=a_d, St_eta=St, sig_c_um=sig_c * 1e6,
                                 Delta_ms=Delta * 1e3, frame_ms=tau * 1e3, h_ms=h * 1e3,
                                 sigma_um=sig * 1e6, noise_um=nz * 1e6, bias_um=bi * 1e6,
                                 valid=Delta < 0.3 * tau_eta, **hits))
                log(f"  {name:20s} eps {eps:.2e} tau_eta {tau_eta * 1e3:6.1f} ms a_drop {a_d:6.2f} m/s2 |"
                    f" sig_c {sig_c * 1e6:4.0f} Delta {Delta * 1e3:3.0f} frame {tau * 1e3:3.0f} ->"
                    f" sigma {sig * 1e6:6.1f} um (noise {nz * 1e6:5.1f}, bias {bi * 1e6:6.1f})"
                    f" hits {hits['w80']:5.1%}/{hits['w140']:5.1%}/{hits['w200']:5.1%}"
                    f" {'' if Delta < 0.3 * tau_eta else '  [MODEL OUT OF RANGE]'}")
    out["aim"] = rows

    log("== C2 photon-limited centroid noise vs tracking geometry ==")
    ph = []
    for theta, Apert, z, Dz in ((90, 0.025, 0.5, 0.05), (40, 0.025, 0.5, 0.05), (20, 0.025, 0.5, 0.05),
                                (90, 0.050, 0.5, 0.05)):
        a = 15e-6
        sig_sca = 2.08 * math.pi * a * a
        E = 0.1                                    # J/m2 per 1 ms frame at the 100 W/m2 exempt mean
        dOm = math.pi * (Apert / 2) ** 2 / (z * z)
        frac = p_water(theta) * dOm / (4 * math.pi)
        Ne = E * sig_sca * frac / (6.626e-34 * 3e8 / 850e-9) * 0.3
        blur = Dz * (Apert / 2) / z
        ph.append(dict(theta=theta, aperture_mm=Apert * 1e3, p=p_water(theta), e_minus=Ne,
                       blur_mm=blur * 1e3, sigma_c_um=blur / math.sqrt(max(Ne, 1.0)) * 1e6))
        log(f"  theta {theta:3d} deg, A {Apert * 1e3:4.1f} mm: p {p_water(theta):6.3f}, {Ne:8.0f} e-,"
            f" blur {blur * 1e3:4.2f} mm -> sigma_c {blur / math.sqrt(max(Ne, 1.0)) * 1e6:6.1f} um")
    out["photons"] = ph
    return out


# ---------------------------------------------------------------- Part D
def part_d(log):
    out = {}
    log("== D1 fill law with the flow angle (m23b + RT9 §10) ==")
    rows = []
    for Dview, b in ((1.5, 0.436e-3), (0.5, 0.145e-3)):
        for d_s in (1e-3, 2e-3, 3e-3):
            for t_eye in (0.05, 0.1):
                n0 = 1.6e7
                F0 = n0 * 0.2724 * d_s * d_s * t_eye
                F90 = n0 * 0.2724 * d_s * b * t_eye
                n_need = F0 / (0.2724 * d_s * b * t_eye) if b > 0 else None
                rows.append(dict(view_m=Dview, b_mm=b * 1e3, d_s_mm=d_s * 1e3, t_eye=t_eye,
                                 F_par=F0, F_perp=F90, ratio=b / d_s,
                                 n_to_restore=n_need, water_g_h=17.3 * n_need / n0,
                                 spots=n0 * d_s * d_s * 0.5))
                log(f"  view {Dview} m, d_s {d_s * 1e3:.0f} mm, t_eye {t_eye:.2f}: F(0) {F0:5.3f},"
                    f" F(90) {F90:5.3f} (ratio {b / d_s:5.3f}); restoring F needs n x{n_need / n0:5.2f}"
                    f" = {17.3 * n_need / n0:6.1f} g/h; spots {n0 * d_s * d_s * 0.5:5.0f}")
    out["fill"] = rows

    log("== D2 sag of a horizontal flow-normal jet ==")
    for throw, Uj in ((0.2, 0.25), (0.6, 0.25)):
        t = throw / Uj
        gp = G * (0.22 / 293.15 - 0.611 * 0.441e-3 / 1.2)
        droop = 0.5 * gp * t * t
        settle = 0.5 * v_stokes(d_of_V(3e-14)) * t
        log(f"  throw {throw} m: t {t:4.2f} s, g' {gp:.2e} m/s2, droop {droop * 1e3:5.1f} mm,"
            f" settling {settle * 1e3:5.1f} mm, total {1e3 * (droop + settle):5.1f} mm,"
            f" drop path {math.degrees(math.atan(v_stokes(d_of_V(3e-14)) / Uj)):4.1f} deg off horizontal")
    return out


# ---------------------------------------------------------------- Part E
def turb_moments(u_rms, L, Uc, Ceps=0.5):
    eps = Ceps * u_rms ** 3 / L
    eta = (NU ** 3 / eps) ** 0.25
    f = [10 ** (-4 + 9 * i / 40000.0) for i in range(40001)]
    m0 = m2 = 0.0
    prev_f = prev_S = None
    for fi in f:
        k = 2 * math.pi * fi / Uc
        S = (2 * L / math.pi) / (1 + (1.339 * L * k) ** 2) ** (5 / 6) * math.exp(-2.25 * (k * eta) ** (4 / 3))
        S *= 2 * math.pi / Uc
        if prev_f is not None:
            m0 += 0.5 * (S + prev_S) * (fi - prev_f)
            m2 += 0.5 * (S * fi * fi + prev_S * prev_f * prev_f) * (fi - prev_f)
        prev_f, prev_S = fi, S
    return eps, eta, math.sqrt(m2 / m0), 3.963 * Uc, Uc / (2 * math.pi * eta)


def part_e(log):
    out = {}
    log("== E1 m25 turbulence spectrum: where the disturbance energy sits ==")
    sp = []
    for u_rms, L, Uc, name in ((0.03, 0.03, 0.03, "still room"), (0.03, 0.03, 0.05, "home"),
                               (0.03, 0.03, 0.10, "quiet office"), (0.10, 0.03, 0.10, "office sigma .1"),
                               (0.03, 0.30, 0.05, "home, L 0.3 m (realistic)")):
        eps, eta, f_rms, f0, f_eta = turb_moments(u_rms, L, Uc)
        sp.append(dict(case=name, u_rms=u_rms, L=L, Uc=Uc, eps=eps, eta_mm=eta * 1e3, f_knee=f0,
                       f_eta=f_eta, f_rms=f_rms, omega_rms=2 * math.pi * f_rms, taylor_ratio=Uc / u_rms))
        log(f"  {name:28s} eps {eps:.2e} eta {eta * 1e3:5.2f} mm knee {f0:6.3f} Hz f_eta {f_eta:6.2f} Hz"
            f" f_rms {f_rms:6.3f} Hz (omega {2 * math.pi * f_rms:6.2f}) Uc/u' {Uc / u_rms:4.2f}")
    out["spectrum"] = sp

    log("== E2 m25 loop: delay-limited gain and the position error ==")
    tau_th = 5e-6 ** 2 * 1190 * 1420 / (0.2 * 2.295 ** 2)
    log(f"  tau_th(a 5 um PMMA) {tau_th * 1e3:.3f} ms; tau_p {(4 / 3 * math.pi * 5e-6 ** 3 * 1190) / (6 * math.pi * MU * 5e-6 / 1.016) * 1e3:.3f} ms")
    lp = []
    _, _, f_rms, _, _ = turb_moments(0.03, 0.03, 0.05)
    w_rms = 2 * math.pi * f_rms
    for name, fr, d, tau_lc in (("LCoS 120 Hz", 120.0, 2, 4e-3), ("LCoS 240 Hz", 240.0, 2, 2e-3),
                                ("500 Hz class", 500.0, 2, 0.5e-3), ("PLM 1.44 kHz", 1440.0, 2, 0.1e-3),
                                ("MEMS 5 kHz", 5000.0, 2, 0.03e-3)):
        T = 1 / fr
        D = (d + 0.5) * T + tau_th + tau_lc
        Kp, Ki = 0.5 / D, (0.5 / D) ** 2 / 4
        sig_fb = 0.03 * w_rms / Ki
        sig_ff = (0.03 * w_rms * D) * w_rms / Ki
        lp.append(dict(case=name, D_ms=D * 1e3, Kp=Kp, Ki=Ki, sigma_fb_um=sig_fb * 1e6,
                       sigma_ff_um=sig_ff * 1e6,
                       holds_fb_w70=sig_fb < 1.5 * 70e-6, holds_ff_w70=sig_ff < 1.5 * 70e-6))
        log(f"  {name:14s} D {D * 1e3:6.2f} ms Kp {Kp:7.1f} Ki {Ki:9.1f} -> sigma_x"
            f" {sig_fb * 1e6:8.1f} um (PID only), {sig_ff * 1e6:7.2f} um (with air feedforward);"
            f" 1.5w(70) = 105 um -> {'holds' if sig_fb < 105e-6 else 'LOST'} / "
            f"{'holds' if sig_ff < 105e-6 else 'LOST'}")
    D_max = math.sqrt(1.5 * 70e-6 * 0.0625 / (0.03 * w_rms))
    log(f"  delay that just holds w 70 um with PID only: D <= {D_max * 1e3:.2f} ms"
        f" -> frame rate >= {1 / ((D_max - 0.1e-3 - tau_th) / 2.5):.0f} Hz at tau_lc 0.1 ms")
    out["loop"] = lp

    log("== E3 m25 P/cap closed form, and the w that fits the cap ==")
    CAP = 7.854e-3 / 1.1
    pc = []
    for draft, Um, ur in (("still room", 0.0, 0.03), ("home", 0.05, 0.03), ("quiet office", 0.10, 0.03)):
        umag = math.sqrt(Um * Um + 3 * ur * ur)
        for h in (1.38, 2.14):
            for w in (40e-6, 55e-6, 70e-6, 100e-6):
                for prof, pp in (("gauss", 1.0), ("dip", 2.0)):
                    P = h * umag * I_UNIT * math.pi * w * w / 2 * pp
                    pc.append(dict(draft=draft, h=h, w_um=w * 1e6, profile=prof, u_mag=umag,
                                   P_mW=P * 1e3, P_over_cap=P / CAP))
            for prof, pp in (("gauss", 1.0), ("dip", 2.0)):
                wmax = math.sqrt(2 * CAP / (h * umag * I_UNIT * math.pi * pp))
                log(f"  {draft:13s} h {h:4.2f} |u| {umag:.4f} m/s: {prof:5s} fits the cap only at"
                    f" w <= {wmax * 1e6:5.1f} um -> modes (0.6/pi w)^2 = {(0.6 / (math.pi * wmax)) ** 2:.2e} per head")
    out["pcap"] = pc

    log("== E4 m24 reproduction and the eye-margin check ==")
    def c7(l):
        if l < 1150:
            return 1.0
        if l < 1200:
            return 10 ** (0.018 * (l - 1150))
        if l < 1250:
            return 8.0
        return 8.0 + 10 ** (0.04 * (l - 1250))
    for lam in (1290, 1310, 1342, 1550):
        skin = (1000.0 if lam > 1400 else 10000.0) * math.pi * 0.5e-3 ** 2
        eye = 10e-3 if lam > 1400 else min(3.5e-3 * c7(lam) * 10 ** -0.25, 0.5)
        log(f"  {lam} nm: C7 {c7(lam) if lam <= 1400 else float('nan'):9.1f} skin(1 mm) {skin * 1e3:6.3f} mW"
            f" eye {eye * 1e3:7.1f} mW -> per-focus cap {min(skin, eye / 2.35) * 1e3:6.3f} mW")
    for lam, alpha in ((1550, 1000.0), (1310, 130.0), (1342, 200.0)):
        k, rb, P = 0.58, 1.75e-3, 10e-3
        if 1 / alpha < rb:
            dT = P / (math.pi * rb * k)
            model = "disc"
        else:
            dT = (0.63 * P * alpha / (2 * math.pi * k)) * (0.5 + math.log(1 / (alpha * rb)))
            model = "line"
        log(f"  {lam} nm alpha {alpha:6.0f} /m (1/alpha {1e3 / alpha:5.2f} mm): collimated 3.5 mm,"
            f" {model:4s} model -> {dT:5.2f} K at 10 mW = {dT / P:6.1f} K/W")
    log("  ratio to 1550 nm, collimated: see the report; RT8 C1 27-91 mW vs 45-80 mW equivalent"
        " -> 0.34-2.0x, not 0.6-2x")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    res = {}
    for name, fn in (("A_drops", part_a), ("B_optics", part_b), ("C_aim", part_c),
                     ("D_render", part_d), ("E_oband", part_e)):
        log(f"\n######## {name} ########")
        res[name] = fn(log)
    with open(os.path.join(OUT, "rt10_checks.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    with open(os.path.join(OUT, "rt10_run.log"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

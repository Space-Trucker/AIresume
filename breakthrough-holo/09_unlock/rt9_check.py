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


# ----------------------------------------------------------------- 3. visible flash: repetitive-pulse rules
def block_repetitive():
    """IEC 60825-1 repetitive pulses, retinal thermal, visible: the most restrictive of rule 1 (single pulse <= AEL_1),
    rule 2 (mean power over T <= the CW AEL) and rule 3 (per pulse <= AEL_1*C5, C5 = N^-0.25). Edition 3 (2014) sets
    C5 = 1 for apparent sources < 5 mrad (ISH1:2017; Schulmeister ILSC 2015), so rule 3 does NOT bind for a beam focus
    or a lit mote (point sources). Rule 3 is shown for the Ed. 2 (2007) reading only. The energy per crossing is fixed by
    the luminance; the BEAM energy is that divided by the capture eff ~ 2a^2/w_v^2, so 5.15 uJ at w_v 140 um and 1.70 uJ at 80 um
    (m23 rows). At 30 Hz the per-flash energy falls as 20/30 (same luminance, more flashes). One fixating pupil on one sample's beam sees
    f_flash = N_s f_r flashes per second."""
    def ael1(t):
        return 7e-4 * t**0.75
    cw = 0.39e-3
    rows = {}
    for name, t_f, f, E in (("w140 3.9 ms, 20 Hz", 3.9e-3, 20.0, 5.15e-6), ("w140 1 ms, 20 Hz", 1e-3, 20.0, 5.15e-6),
                            ("w80 3.9 ms, 20 Hz", 3.9e-3, 20.0, 1.70e-6), ("w80 1 ms, 20 Hz", 1e-3, 20.0, 1.70e-6),
                            ("w140 3.9 ms, 30 Hz", 3.9e-3, 30.0, 5.15e-6 * 20/30)):
        for T in (0.25, 10.0, 100.0):
            N = f*T
            C5 = N**-0.25
            r1, r2, r3 = E/ael1(t_f), E*f/cw, E/(ael1(t_f)*C5)
            rows[f"{name}, T {T:g} s"] = dict(N=N, C5_ed2=C5, rule1=r1, rule2=r2, rule3_ed2_only=r3,
                                             worst_ed3_point=max(r1, r2), worst_ed2=max(r1, r2, r3))
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
    skin_limit_through_ap = skin_mpe_Wm2 * math.pi*(1e-3/2)**2      # EN 50689: 1 mm, 10 s
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


# ----------------------------------------------------------------- 9. probe-gated event rate vs the design rate
def _interval(px, py, p0, d, r, zc):
    """z-interval (absolute) where the vertical line through (px, py) lies within r of the line p0 + t d.
    Returns (lo, hi) arrays, lo > hi when empty. Vectorised over px, py."""
    ax, ay, az = px - p0[0], py - p0[1], -p0[2]
    adot = ax*d[0] + ay*d[1] + az*d[2]
    A = 1 - d[2]**2
    B = 2*(az - adot*d[2])
    C = ax*ax + ay*ay + az*az - adot*adot - r*r
    if A < 1e-12:                                   # the line is vertical: all or nothing
        ok = C <= 0
        return np.where(ok, -1e9, 1e9), np.where(ok, 1e9, -1e9)
    disc = B*B - 4*A*C
    sq = np.sqrt(np.maximum(disc, 0))
    lo, hi = (-B - sq)/(2*A), (-B + sq)/(2*A)
    bad = disc < 0
    return np.where(bad, 1e9, lo), np.where(bad, -1e9, hi)


def block_probe_rate(n_samp=150, seed=3):
    """m23 sizes the rain so that N_s f_r = 20 motes/s cross each sample's delta x d_s window (3 mm x 1 mm). But a
    mote is detected (and so lit) only if it passes through the voxel pencil B_k (radius R_p) AND camera tube 1 AND
    camera tube 2 (half-width eps). The rate through that voxel is n*Uf*A_proj, with A_proj its horizontal projected
    area, computed exactly here on the m23 geometry (probe in the ceiling unit, cameras A, A')."""
    P, _ = m23.armor_samples()
    Pw = P + np.array([0.0, 0.0, 1.2])
    Bpos = np.array([0.35, 0.0, 2.45])
    cams = [np.array([-1.4, 0.9, 2.3]), np.array([1.0, -1.3, 2.3])]
    base = m23.flowr2(S=3.08)
    n, Uf = base["n_per_m3"], base["v_s_mm_s"]*1e-3 + 0.25
    design_rate = 1.0*20.0
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(Pw), n_samp, replace=False)
    g = np.linspace(-4e-3, 4e-3, 321)
    GX, GY = np.meshgrid(g, g)
    dA = (g[1]-g[0])**2
    res = {}
    for R_p in (0.35e-3, 0.525e-3):
        for eps in (0.5e-3, 1.0e-3, 2.0e-3):
            areas, angs = [], []
            for k in idx:
                Pp = Pw[k] + np.array([0, 0, 6e-3])
                px, py = Pp[0] + GX, Pp[1] + GY
                dB = (Pp - Bpos)/np.linalg.norm(Pp - Bpos)
                lo, hi = _interval(px, py, Pp, dB, R_p, Pp[2])
                for cam in cams:
                    dc = (Pp - cam)/np.linalg.norm(Pp - cam)
                    l2, h2 = _interval(px, py, Pp, dc, eps, Pp[2])
                    lo, hi = np.maximum(lo, l2), np.minimum(hi, h2)
                areas.append(np.sum(hi > lo)*dA)
                angs.append(math.degrees(math.acos(abs(dB[2]))))
            A = np.array(areas)
            rate = n*Uf*A
            res[f"Rp{R_p*1e3:.3f}_eps{eps*1e3:.1f}"] = dict(
                A_proj_mm2_p50=float(np.median(A)*1e6), rate_p50=float(np.median(rate)),
                rate_p10=float(np.percentile(rate, 10)), rate_p90=float(np.percentile(rate, 90)),
                frac_of_design=float(np.median(rate)/design_rate),
                drop_100ms=float(np.exp(-np.median(rate)*0.1)), pencil_angle_from_vertical_deg=float(np.median(angs)))
    res["design_rate_per_sample"] = design_rate
    res["design_window_mm2"] = 3.0*1.0
    # the pencil runs ~15 deg from vertical: a mote stays inside it for 2 R_p / sin(phi) of fall
    phi = math.radians(res[f"Rp0.350_eps0.5"]["pencil_angle_from_vertical_deg"])
    res["dwell_in_pencil_ms_true"] = 2*0.35e-3/math.sin(phi)/Uf*1e3
    res["dwell_in_pencil_ms_m23"] = 2*0.35e-3/Uf*1e3
    return res


# ----------------------------------------------------------------- 10. painted fill vs stroke angle (coordinator)
def fill_mc(theta_deg, n_area, Uf, d_s, t_eye, b, L=0.3, gated=False, delta=3e-3, seed=0, reps=40):
    """2D Monte Carlo in the viewing plane. Motes within the stroke's depth slab d_s have areal density n_area = n d_s.
    Each falls a distance Uf t_eye during the eye time. Painted set = the part of its path inside the ribbon (width d_s
    about the stroke axis), seen as a stadium of width b (eye blur, >= the mote). Fill = covered fraction of the stroke
    axis (projections of the painted pieces). gated=True: FLOW-R2's per-sample flashes, lit only for d_s of fall after
    the mote passes each sample point (samples every delta along the axis)."""
    rng = np.random.default_rng(seed)
    th = math.radians(theta_deg)
    t_hat = np.array([math.sin(th), math.cos(th)])     # (x, z): theta from vertical
    n_hat = np.array([math.cos(th), -math.sin(th)])
    fall = Uf*t_eye
    pad = fall + d_s + 0.01
    fills, gaps10 = [], []
    for _ in range(reps):
        # bounding box of the ribbon, padded upward by the fall
        xs = np.array([0, L*t_hat[0]])
        zs = np.array([0, L*t_hat[1]])
        x0, x1 = xs.min() - d_s - 0.005, xs.max() + d_s + 0.005
        z0, z1 = zs.min() - d_s - 0.005, zs.max() + pad
        N = rng.poisson(n_area*(x1 - x0)*(z1 - z0))
        px = rng.uniform(x0, x1, N)
        pz = rng.uniform(z0, z1, N)
        nst = 600
        s = np.linspace(0, fall, nst)                   # fall distance samples
        cov = np.zeros(int(L/2e-4) + 1, bool)
        for i in range(N):
            X = np.full(nst, px[i])
            Z = pz[i] - s
            u = X*t_hat[0] + Z*t_hat[1]                # along-axis coordinate
            v = X*n_hat[0] + Z*n_hat[1]                # across
            ins = (np.abs(v) <= d_s/2) & (u >= 0) & (u <= L)
            if gated:
                # lit only within d_s of fall after passing each sample: z-distance below the sample's level
                k = np.round(u/delta)
                zsamp = k*delta*t_hat[1]
                xsamp = k*delta*t_hat[0]
                dz_below = (zsamp + (X - xsamp)*0) - Z      # fall since the sample level (vertical strokes)
                if abs(t_hat[1]) > 0.5:
                    ins &= (dz_below >= 0) & (dz_below <= d_s) & (np.abs(u - k*delta) <= d_s/2 + 1e-9)
                else:
                    ins &= np.abs(u - k*delta) <= 0.35e-3      # horizontal-ish: only motes through the pencil
            if not ins.any():
                continue
            # paint each contiguous lit run separately (gated flashes leave gaps between samples)
            idx_ins = np.flatnonzero(ins)
            cuts = np.flatnonzero(np.diff(idx_ins) > 1)
            starts = np.r_[idx_ins[0], idx_ins[cuts + 1]]
            ends = np.r_[idx_ins[cuts], idx_ins[-1]]
            for s0, s1 in zip(starts, ends):
                uu = u[s0:s1 + 1]
                lo = max(0, int((uu.min() - b/2)/2e-4))
                hi = min(len(cov) - 1, int((uu.max() + b/2)/2e-4))
                cov[lo:hi + 1] = True
        fills.append(cov.mean())
        # gap statistics: fraction of the axis length in uncovered runs longer than 10 mm
        runs, cur = [], 0
        for c_ in cov:
            if not c_:
                cur += 1
            elif cur:
                runs.append(cur); cur = 0
        if cur:
            runs.append(cur)
        gaps10.append(sum(r for r in runs if r*2e-4 > 10e-3)/len(cov))
    return float(np.mean(fills)), float(np.mean(gaps10))


def block_fill():
    base = m23.flowr2(S=3.08)
    n, Uf, d_s = base["n_per_m3"], base["v_s_mm_s"]*1e-3 + 0.25, 1e-3
    res = {"formula": {}, "mc": {}, "mc_gated": {}}
    for t_eye in (0.05, 0.10):
        for th in (0, 30, 45, 60, 90):
            c, s_ = abs(math.cos(math.radians(th))), abs(math.sin(math.radians(th)))
            res["formula"][f"t{t_eye*1e3:.0f}_th{th}"] = dict(
                coord_cos_plus_sin=n*Uf*d_s*d_s*t_eye*(c + s_), m23_vertical_only=n*Uf*d_s*d_s*t_eye)
    for th in (0, 30, 45, 60, 90):
        f, g10 = fill_mc(th, n*d_s, Uf, d_s, 0.05, b=d_s)
        res["mc"][f"t50_th{th}"] = dict(fill=f, frac_len_in_gaps_gt10mm=g10)
    for th in (0, 90):
        f, g10 = fill_mc(th, n*d_s, Uf, d_s, 0.05, b=d_s, gated=True)
        res["mc_gated"][f"t50_th{th}"] = dict(fill=f, frac_len_in_gaps_gt10mm=g10)
    # d_s for fill 1 at the same n (same mass), and what it costs
    ds1 = math.sqrt(1/(n*Uf*0.05))
    res["d_s_for_fill1_50ms_mm"] = ds1*1e3
    res["cost_at_d_s_2mm"] = dict(simult_spots_x=(2e-3/d_s)**2, visible_power_x=2e-3/d_s,
                                  flash_ms=2e-3/Uf*1e3, E_over_AEL1=5.15e-6/(7e-4*(2e-3/Uf)**0.75))
    return res


# ----------------------------------------------------------------- 11. beam aggregation at the heads (eye, skin)
def _capture(rho, w, R):
    """Fraction of a Gaussian beam (1/e^2 radius w) offset rho from the centre of a disc of radius R."""
    from scipy.stats import ncx2
    sig = w/2
    return ncx2.cdf((R/sig)**2, 2, (rho/sig)**2)


def _lines_through_disc(src, targets, centre, normal, R, w_at):
    """Sum of captured fractions of lines src -> targets (continued) through a disc (centre, normal, radius R)."""
    d = targets - src
    d = d/np.linalg.norm(d, axis=1, keepdims=True)
    t = ((centre - src) @ normal)/(d @ normal)
    hit = src + t[:, None]*d
    rho = np.linalg.norm(hit - centre, axis=1)
    ok = t > 0
    return np.where(ok, _capture(rho, w_at(t), R), 0.0)


def block_heads(w0_vis=140e-6, E=5.15e-6):
    P, _ = m23.armor_samples()
    Pw = P + np.array([0.0, 0.0, 1.2])
    centre_img = np.array([0.0, 0.0, 1.2])
    fr = 20.0
    res = {}
    # visible: one head 30 deg off vertical (each of 3 heads alike), all its lines through one scanner exit
    off = 1.25*math.tan(math.radians(30))
    head = np.array([off, 0.0, 2.45])
    lam, w0 = 520e-9, w0_vis
    zR = math.pi*w0*w0/lam
    Lmean = np.linalg.norm(Pw - head, axis=1).mean()
    w_head = w0*math.sqrt(1 + (Lmean/zR)**2)
    axis = (centre_img - head)/np.linalg.norm(centre_img - head)
    for alloc, per_line in (("events split over 3 heads", E*fr/3), ("one head per sample", E*fr)):
        rows = {}
        for d in (0.0, 0.1, 0.2, 0.5):
            c0 = head + d*axis
            # beam radius near the head ~ w_head (far from the focus)
            best = 0.0
            # scan the disc centre over the plane at distance d
            e1 = np.cross(axis, [0, 1, 0]); e1 /= np.linalg.norm(e1)
            e2 = np.cross(axis, e1)
            span = max(0.004, d*0.25)
            for a_ in np.linspace(-span, span, 41):
                for b_ in np.linspace(-span, span, 41):
                    cc = c0 + a_*e1 + b_*e2
                    f = _lines_through_disc(head, Pw, cc, axis, 3.5e-3, lambda t: np.full_like(t, w_head))
                    best = max(best, float(f.sum()))
            rows[f"d_{d*100:.0f}cm"] = dict(lines_in_pupil=best, mean_mW=best*per_line*1e3,
                                            over_cw_ael=best*per_line/0.39e-3)
        res[f"visible head, {alloc}"] = rows
    # skin at the exit (EN 50689, 1 mm, 10 s): fraction of each line through a 1 mm disc at the scanner, all lines
    f1 = float(_lines_through_disc(head, Pw, head + 1e-6*axis, axis, 0.5e-3,
                                   lambda t: np.full_like(t, w_head)).sum())
    res["visible head exit skin 1mm"] = dict(sum_frac=f1, mean_mW=f1*E*fr/3*1e3, limit_mW=2000*math.pi*(0.5e-3)**2*1e3)
    # probe: 0.2 mW per pencil, CW, from Bpos to P_k+ (850 nm, w_p 0.35 mm, zR 0.45 m)
    Bpos = np.array([0.35, 0.0, 2.45])
    Pp = Pw + np.array([0, 0, 6e-3])
    wp, zRp = 0.35e-3, math.pi*(0.35e-3)**2/850e-9
    w_lens = wp*math.sqrt(1 + (np.linalg.norm(Pp - Bpos, axis=1).mean()/zRp)**2)
    axp = (centre_img - Bpos)/np.linalg.norm(centre_img - Bpos)
    e1 = np.cross(axp, [0, 1, 0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(axp, e1)
    C4 = 10**(0.002*150)
    rows = {}
    for d in (0.0, 0.1, 0.2, 0.5):
        c0 = Bpos + d*axp
        best = 0.0
        span = max(0.004, d*0.25)
        for a_ in np.linspace(-span, span, 41):
            for b_ in np.linspace(-span, span, 41):
                f = _lines_through_disc(Bpos, Pp, c0 + a_*e1 + b_*e2, axp, 3.5e-3, lambda t: np.full_like(t, w_lens))
                best = max(best, float(f.sum()))
        rows[f"d_{d*100:.0f}cm"] = dict(pencils_in_pupil=best, mW=best*0.2, over_ael=best*0.2e-3/(3.9e-4*C4))
    res["probe head (850 nm)"] = rows
    fsk = float(_lines_through_disc(Bpos, Pp, Bpos + 1e-6*axp, axp, 0.5e-3, lambda t: np.full_like(t, w_lens)).sum())
    res["probe exit skin 1mm"] = dict(mW=fsk*0.2, limit_mW=2000*C4*math.pi*(0.5e-3)**2*1e3)
    res["beam radius at heads mm"] = dict(visible=w_head*1e3, probe=w_lens*1e3)
    res["total visible mean W"] = 1026*E*fr
    return res


# ----------------------------------------------------------------- 12. stacking at a pupil inside the column
def block_column_pupil(seed=5, w0_vis=140e-6, E=5.15e-6):
    """A pupil (7 mm) placed inside the column, facing up toward the heads (a face leaning into the image).
    Sum the time-mean power of every visible line (3 heads at 30 deg, events split evenly) whose beam passes the pupil.
    The pupil is scanned over a grid covering the content's bounding box plus 10 cm above."""
    P, _ = m23.armor_samples()
    Pw = P + np.array([0.0, 0.0, 1.2])
    fr = 20.0
    off = 1.25*math.tan(math.radians(30))
    heads = [np.array([off*math.cos(a), off*math.sin(a), 2.45]) for a in np.radians([0, 120, 240])]
    lam, w0 = 520e-9, w0_vis
    zR = math.pi*w0*w0/lam
    best, best_at = 0.0, None
    rng = np.random.default_rng(seed)
    pts = np.column_stack([rng.uniform(-0.15, 0.15, 3000), rng.uniform(-0.06, 0.03, 3000), rng.uniform(0.9, 1.6, 3000)])
    pts = np.vstack([pts, Pw[rng.choice(len(Pw), 600, replace=False)] + np.array([0, 0, 0.004])])
    for c in pts:
        tot = 0.0
        for h in heads:
            nrm = (h - c)/np.linalg.norm(h - c)          # pupil faces the head
            Lk = np.linalg.norm(Pw - h, axis=1)

            def w_at(t, Lk=Lk):
                return w0*np.sqrt(1 + ((t - Lk)/zR)**2)
            tot += float(_lines_through_disc(h, Pw, c, nrm, 3.5e-3, w_at).sum())*E*fr/3
        if tot > best:
            best, best_at = tot, c
    return dict(worst_mean_mW=best*1e3, over_cw_ael=best/0.39e-3, at=[float(x) for x in best_at])


# ----------------------------------------------------------------- 13. column buoyancy and width
def block_column():
    T0, U0, H = 293.0, 0.25, 1.25
    res = {}
    for dT in (-1.0, -0.3, 0.3, 1.0):            # column minus room at image height (negative = colder = sinks faster)
        gp = G*dT/T0                              # buoyancy acceleration, + = upward (opposes the fall)
        U2 = U0*U0 - 2*gp*H
        res[f"dT_{dT:+.1f}K"] = dict(Ri=abs(gp)*H/(U0*U0), U_at_image=math.sqrt(U2) if U2 > 0 else 0.0)
    res["stratification_1.5K_per_m_over_1.25m_K"] = 1.5*1.25
    P, _ = m23.armor_samples()
    res["armor_width_m"] = float(np.ptp(P[:, 0])); res["armor_depth_m"] = float(np.ptp(P[:, 1]))
    res["armor_height_m"] = float(np.ptp(P[:, 2]))
    # core erosion ~0.09 per unit length per side (opus round 3/4): usable core at the image bottom
    res["core_at_image_bottom_m"] = 0.8 - 2*0.09*1.55
    # a column only as wide as the content needs: 0.23 m + 2*(guard 5 cm + erosion 0.14 m + wander/drift 3 cm)
    C_min = 0.23 + 2*(0.05 + 0.14 + 0.03)
    res["C_min_m"] = C_min
    res["mass_flux_ratio_vs_0.8m"] = (C_min/0.8)**2
    return res


def main():
    out["1_aperture_dof_photons"] = block_aperture()
    out["2_wander_vs_spot"] = block_wander()
    out["3_repetitive_pulse"] = block_repetitive()
    out["4_probe_single_pencil"] = block_probe_eye()
    out["5_particles"] = block_particles()
    out["6_vertical_coverage"] = block_coverage()
    out["7_m22_spotcheck"] = block_m22()
    out["8_ghost_blur"] = block_ghost_blur()
    out["9_probe_rate"] = block_probe_rate()
    out["10_fill"] = block_fill()
    out["11_heads"] = block_heads()
    out["11b_heads_w80"] = block_heads(80e-6, 1.70e-6)
    out["12_column_pupil"] = block_column_pupil()
    out["12b_column_pupil_w80"] = block_column_pupil(w0_vis=80e-6, E=1.70e-6)
    out["13_column"] = block_column()
    for k, v in out.items():
        print(f"\n=== {k} ===")
        print(json.dumps(v, indent=1, default=float)[:4000])
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "rt9_checks.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))


if __name__ == "__main__" and "--addenda" not in sys.argv and "--aim" not in sys.argv:
    main()


# ----------------------------------------------------------------- 14. addenda (run after main via --addenda)
def block_addenda():
    P, _ = m23.armor_samples()
    Pw = P + np.array([0.0, 0.0, 1.2])
    cams = [np.array([-1.4, 0.9, 2.3]), np.array([1.0, -1.3, 2.3]), np.array([-0.2, 1.6, 2.3])]
    base = m23.flowr2(S=3.08)
    e35 = base["probe_electrons"]
    Uf = base["v_s_mm_s"]*1e-3 + 0.25
    res = {"cams": []}
    for cam in cams:
        rng_ = np.linalg.norm(Pw - cam, axis=1)
        z0 = float(np.median(rng_))
        half = float((rng_.max() - rng_.min())/2)
        row = dict(range_m=z0, depth_half_m=half)
        for eps in (0.5e-3, 1.0e-3):
            A = eps*z0/half                       # circle of confusion <= eps over the content depth
            row[f"A_for_coc_{eps*1e3:.1f}mm_mm"] = A*1e3
            # electrons per detection: m23 scaling (A^2, 1/z^2) times the true dwell in the voxel (~4.6-10 ms vs 2.7)
            row[f"e_per_crossing_{eps*1e3:.1f}mm"] = e35*(A/0.035)**2*(1.6/z0)**2
        row["coc_at_35mm_mm"] = 0.035*half/z0*1e3
        res["cams"].append(row)
    # fill MC with a 1-arcmin eye blur at 1.5 m (b = 0.44 mm) instead of b = d_s
    n = base["n_per_m3"]
    fm = {}
    for th in (0, 90):
        fm[f"cont_th{th}"] = fill_mc(th, n*1e-3, Uf, 1e-3, 0.05, b=0.44e-3)
        fm[f"gated_th{th}"] = fill_mc(th, n*1e-3, Uf, 1e-3, 0.05, b=0.44e-3, gated=True)
    res["fill_b0.44mm"] = {k: dict(fill=v[0], frac_len_in_gaps_gt10mm=v[1]) for k, v in fm.items()}
    # vertical strokes, gated, with flashes stretched to delta/Uf (cover the whole 3 mm per sample)
    t3 = 3e-3/Uf
    res["vertical_stretched_flash"] = dict(t_flash_ms=t3*1e3, E_uJ=5.15*3, E_over_AEL1=15.45e-6/(7e-4*t3**0.75))
    # the visible engine's simultaneous spots if the probe voxel is widened to the design window (rate 20/s) and
    # vertical strokes get stretched flashes (59 % of samples)
    events = 1026*20.0
    res["simult_spots_stretched_vertical"] = events*(0.41*1e-3/Uf + 0.59*3e-3/Uf)
    # a rain dense enough to make the m23 voxel deliver 20/s (rate 3.4-4.8/s at R_p 0.35, eps 0.5-1)
    for r in (3.4, 4.8):
        k = 20.0/r
        res[f"rain_x{k:.1f}"] = dict(mass_mg_m3=base["mass_mg_m3"]*k, g_h=base["g_per_h"]*k,
                                     tau_pct=base["tau_col_pct"]*k,
                                     contrast_dark_wall_pct=base["tau_col_pct"]*k/100*0.9/0.05*100)
    return res


if __name__ == "__main__" and "--addenda" in sys.argv:
    out_ad = block_addenda()
    print(json.dumps(out_ad, indent=1, default=float))
    with open(os.path.join(HERE, "results", "rt9_addenda.json"), "w") as fh:
        json.dump(out_ad, fh, indent=1, default=float)


# ----------------------------------------------------------------- 15. aim: fraction of flashes landing on the mote
def block_aim():
    """Hit = mote within R = w_v/2 of the spot centre (>= 61 % of peak intensity). Per-axis lateral error sigma:
    as specified, sigma = Tu*U*t_lead (ballistic; T_L ~ L/u' ~ 1 s >> t_lead). Fix: velocity from multi-frame
    centroids during the ~10 ms pencil dwell, then only the Lagrangian velocity change over t_lead remains:
    sigma ~ sqrt(C0 eps t)*t/sqrt(3) (C0 ~ 6, recalled) plus the velocity-estimate error. P(hit) = 1-exp(-R^2/2sigma^2)."""
    Uf = base_Uf()
    res = {}
    for Tu in (0.01, 0.10):
        for D in (6e-3, 1.5e-3):
            t = D/Uf
            sig = Tu*0.25*t
            res[f"spec Tu{Tu*100:.0f}% D{D*1e3:.1f}mm"] = {f"w{int(w*1e6)}": 1-math.exp(-(w/2)**2/(2*sig*sig))
                                                         for w in (80e-6, 140e-6)} | dict(sigma_um=sig*1e6)
    for name, eps_turb in (("core sigma_u 25 mm/s, L 4 cm", 0.025**3/0.04), ("hand wake u' 0.1 m/s, L 8 cm", 0.1**3/0.08)):
        t = 1.5e-3/Uf
        s_acc = math.sqrt(6*eps_turb*t)*t/math.sqrt(3)
        s_vel = (14e-6*math.sqrt(12)/(8e-3*math.sqrt(8)))*t       # 14 um centroids, 8 frames over 8 ms
        sig = math.hypot(s_acc, s_vel)
        res[f"fix D1.5mm + velocity, {name}"] = {f"w{int(w*1e6)}": 1-math.exp(-(w/2)**2/(2*sig*sig))
                                                 for w in (80e-6, 140e-6)} | dict(sigma_um=sig*1e6, eps=eps_turb)
    return res


if __name__ == "__main__" and "--aim" in sys.argv:
    r = block_aim()
    print(json.dumps(r, indent=1))
    with open(os.path.join(HERE, "results", "rt9_aim.json"), "w") as fh:
        json.dump(r, fh, indent=1)

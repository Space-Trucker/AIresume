"""M23: FLOW-R2, a room-scale gated mote rain. FLOW-R (idea round 4, opus) plus crossed-probe gating in place of 3D
particle tracking.

FLOW-R (09_unlock/idea_round_4_opus.md §5): a uniform, untargeted rain of white food-grade motes (a ~ 5-7 um) falls
with a guarded downward column (U ~ 0.25 m/s). Each mote that crosses the content gets a gated visible spot, so
content updates in one frame. Opus found that 3D particle tracking (0.5 particles per pixel at room scale) limits it to
desk scale.

Crossed-probe gating (main session, this model) replaces tracking with local, geometric detection:
- A probe head B (an IR DLP projector stopped down to pencil beams, w_p ~ 0.25-0.5 mm, z_R ~ 0.2-0.8 m) sends one
  pencil through P_k+ = P_k + Delta z_hat, a look-ahead point just above each content sample P_k.
- Cameras A and A' (ordinary global-shutter machine-vision cameras at 0.5-1 kHz) watch only the pixels p_k, p'_k
  where P_k+ projects.
- A mote crossing B_k at P_k+ lights both pixels in the same frame. The controller predicts its arrival at P_k
  (Delta / U later) and fires a focused visible spot there for d_s / U.
- With one camera, every probe beam B_j that crosses the line of sight L_k inside the column makes ghosts: these are
  epipolar coincidences. Two cameras need the mote within eps of both L_k and L'_k, which only P_k+ satisfies.
  Ghosts then come only from probe beams that pass through P_k+ itself. This part counts both cases by Monte Carlo on
  the armor content.

Everything else (rain density, mass, haze, capture, visible Class 1, path glitter, simultaneous spots, air) follows
FLOW-R's formulas with room-scale numbers. Tags: all [DERIVED] from the stated inputs unless marked.

Run: python3 m23_flowr2.py -> results/m23_flowr2.json, results/m23_run.log
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "04_engineering", "holo_engine"))
import content as c  # noqa: E402

MU, G, RHO_A = 1.81e-5, 9.81, 1.2
H_PLANCK, C_LIGHT = 6.626e-34, 3e8
V555 = 683.0


def lambert_phase(alpha, albedo=0.9):
    """Phase function of a Lambertian sphere, normalised so the isotropic value is 1 (alpha = phase angle)."""
    return albedo * 8 / (3 * math.pi) * (math.sin(alpha) + (math.pi - alpha) * math.cos(alpha))


def armor_samples(size=0.6, spacing=3e-3):
    strokes, _ = c.procedural_armor_budget(max_length_m=9.0, height=1.8)
    pts, ids = c.strokes_to_points(strokes, spacing * 1.8 / size)
    pts = (pts - pts.mean(axis=0)) * (size / 1.8)
    tang = np.zeros_like(pts)
    for k in np.unique(ids):
        m = np.where(ids == k)[0]
        if len(m) < 2:
            tang[m] = [1, 0, 0]
            continue
        p = pts[m]
        d = np.gradient(p, axis=0)
        n = np.linalg.norm(d, axis=1, keepdims=True)
        tang[m] = d / np.maximum(n, 1e-12)
    return pts, tang


def line_line(p1, d1, p2, d2):
    """Closest distance and the parameters (t on line 1, s on line 2) of two lines p + t d (d unit)."""
    w0 = p1 - p2
    b = d1 @ d2
    dd = d1 @ w0
    e = d2 @ w0
    den = 1 - b * b
    if den < 1e-12:
        return float(np.linalg.norm(np.cross(w0, d1))), 0.0, 0.0
    t = (b * e - dd) / den
    s = (e - b * dd) / den
    return float(np.linalg.norm(w0 + t * d1 - s * d2)), t, s


def ghost_counts(P, Bpos, cam, eps, box):
    """For each sample k: the number of probe beams B_j (j != k, through P_j) that pass within eps of the camera's line
    of sight L_k through P_k, at a point inside the column box and away from P_k. A mote crossing B_j there lights the
    camera's pixel p_k although it is not at P_k (a single-camera ghost). A mote near P_k lit by any beam is a true
    event: every camera's line of sight through P_k meets there."""
    lo, hi = box
    n = len(P)
    dB = P - Bpos
    dB = dB / np.linalg.norm(dB, axis=1, keepdims=True)
    g = np.zeros(n)
    idx = np.arange(n)
    for k in range(n):
        dl = P[k] - cam
        dl = dl / np.linalg.norm(dl)
        w0 = cam - Bpos
        b = dB @ dl
        dd = w0 @ dl
        e = dB @ w0
        den = np.maximum(1 - b * b, 1e-12)
        t = (b * e - dd) / den
        s_ = (e - b * dd) / den
        q1 = cam + t[:, None] * dl
        q2 = Bpos + s_[:, None] * dB
        dist = np.linalg.norm(q1 - q2, axis=1)
        inside = np.all((q2 >= lo) & (q2 <= hi), axis=1)
        far = np.linalg.norm(q2 - P[k], axis=1) > 2 * eps
        g[k] = np.sum((dist < eps) & inside & far & (idx != k))
    return g


def ghost_ratio(gs, r_vox, tau_c):
    """Accidental m-camera coincidence rate over the true rate for one sample: each camera sees ghosts at g_i r_vox;
    an m-fold coincidence within tau_c happens at m prod(g_i r_vox) tau_c^(m-1); the true rate is r_vox."""
    m = len(gs)
    if m == 1:
        return gs[0]
    return m * np.prod(gs, axis=0) * (r_vox * tau_c) ** (m - 1)


def flowr2(S=None, delta=3e-3, d_s=1e-3, f_r=20.0, N_s=1.0, U=0.25, a=7e-6, rho=1520.0, C=0.8, H_room=2.5,
           eta_c=0.999, ach=0.5, room_V=50.0, L_line=3.0, lam_vis=520e-9, w_v=140e-6, n_heads_vis=3, t_flash=None,
           w_p=0.35e-3, lam_p=850e-9, P_p=0.2e-3, cam_D=0.035, cam_dist=1.6, qe=0.35, Delta=6e-3, Tu=0.1,
           E_amb_lux=10.0):
    v_s = 2 * rho * G * a * a / (9 * MU)
    Uf = U + v_s
    m = 4 / 3 * math.pi * a ** 3 * rho
    n = N_s * f_r / (Uf * delta * d_s)                          # horizontal-stroke sampling
    mass = n * m
    tau_col = n * 2 * math.pi * a * a * C                       # extinction (Q_ext ~ 2) across the column
    flux = n * Uf * C * C
    g_h = flux * m * 3600 * 1e3
    # column haze seen against the room: L_col ~ tau E / pi (albedo 0.9, phase ~1) vs a dark wall (rho 0.05)
    haze_cd = tau_col * E_amb_lux / math.pi * 0.9
    wall_cd = 0.05 * E_amb_lux / math.pi
    # dropout and vertical-stroke coverage over an eye time of 50-100 ms
    p_drop_100ms = math.exp(-N_s * f_r * 0.1)
    vert_cov_50ms = n * d_s * d_s * Uf * 0.05
    vert_cov_50ms_2ds = n * (2 * d_s) * d_s * Uf * 0.05
    # room particles: escape (1 - eta_c) of the flux; loss by ventilation + settling to the floor
    k_loss = ach / 3600 + v_s / H_room
    room_ugm3 = flux * m * (1 - eta_c) / (k_loss * room_V) * 1e9
    # visible: line luminance L per 1 mm line, lit once per crossing for d_s/U (duty D)
    D = N_s * f_r * d_s / Uf
    J = L_line * 1e-3 * delta
    V = 0.71                                                     # 520 nm
    p_worst = lambert_phase(math.radians(90.0)) * 0.66           # worst azimuth (opus uses 0.5 conservative)
    p_sc = 4 * math.pi * (J / D) / (p_worst * V555 * V)          # W scattered by the lit mote
    eff = (1 - math.exp(-2 * a * a / (w_v * w_v))) * 0.9
    t_cross = d_s / Uf
    E_flash = p_sc / eff * t_cross                               # energy per crossing is fixed by the luminance
    t_f = t_cross if t_flash is None else t_flash
    P_beam = E_flash / t_f                                       # shorter flashes need more peak power
    ael_single = 7e-4 * t_f ** 0.75                               # J, visible single-pulse AEL (C6 = 1)
    events = (S / delta) * N_s * f_r
    simult = events * t_f
    glitter = n * math.pi * C * w_v * w_v / 2                    # path light / focus light (diffuse, see T9)
    z_R_v = math.pi * w_v * w_v / lam_vis
    ghost_dots = n * math.pi * w_v * w_v / 2 * 2 * z_R_v          # other motes within +-z_R of a gated focus
    modes_vis = (C / (math.pi * w_v)) ** 2
    # probe and detection
    z_R_p = math.pi * w_p * w_p / lam_p
    intercept = 1 - math.exp(-2 * a * a / (w_p * w_p))
    omega = math.pi * (cam_D / 2) ** 2 / cam_dist ** 2
    photons = P_p * intercept * 0.9 * omega / (4 * math.pi) * 0.76 * (2 * w_p / Uf) / (H_PLANCK * C_LIGHT / lam_p)
    electrons = photons * qe
    t_lead = Delta / Uf
    wander = Tu * U * t_lead                                     # lateral wander between probe and content point
    spurious = n * 2 * w_p * Uf * C                              # crossings per probe beam per second (anywhere)
    P_probe_total = (S / delta) * P_p
    air_m3h = C * C * U * 3600
    return dict(S_m=S, n_per_m3=n, mass_mg_m3=mass * 1e6, tau_col_pct=tau_col * 100, flux_per_s=flux, g_per_h=g_h,
                v_s_mm_s=v_s * 1e3, haze_cd_m2=haze_cd, dark_wall_cd_m2=wall_cd, p_drop_100ms=p_drop_100ms,
                vert_cov_50ms=vert_cov_50ms, vert_cov_50ms_2ds=vert_cov_50ms_2ds, room_ug_m3=room_ugm3, duty=D,
                P_beam_mW=P_beam * 1e3, t_flash_ms=t_f * 1e3, E_flash_uJ=E_flash * 1e6,
                ael_single_uJ=ael_single * 1e6, class1_single=E_flash <= ael_single, events_per_s=events,
                simult_spots=simult, glitter=glitter, ghost_dots=ghost_dots, z_R_vis_cm=z_R_v * 100, modes_vis=modes_vis,
                z_R_probe_m=z_R_p, probe_photons=photons, probe_electrons=electrons, lead_ms=t_lead * 1e3,
                wander_mm=wander * 1e3, spurious_per_beam_s=spurious, P_probe_total_mW=P_probe_total * 1e3,
                air_m3_h=air_m3h)


def selftest():
    ok = True
    # Lambert phase function: 4 pi average equals the albedo
    al = np.linspace(0, math.pi, 20001)
    avg = np.trapezoid([lambert_phase(x, 1.0) for x in al] * np.sin(al), al) / 2
    ok &= abs(avg - 1.0) < 1e-3
    ok &= abs(lambert_phase(math.pi / 2) - 0.764) < 0.01
    # line-line: skew lines x-axis and the line (0, 1, z) are 1 apart
    d, _, _ = line_line(np.zeros(3), np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0]))
    ok &= abs(d - 1.0) < 1e-12
    print(f"selftest: Lambert 4pi average {avg:.4f}, p(90) {lambert_phase(math.pi / 2):.3f}, line distance {d:.3f} "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    assert selftest()
    P, T = armor_samples()
    S = len(P) * 3e-3
    vert = np.abs(T[:, 2]) > math.cos(math.radians(30))
    print(f"\nArmor content at 0.6 m: {len(P)} samples at 3 mm, S = {S:.2f} m; near-vertical (within 30 deg) "
          f"{vert.mean() * 100:.1f} %")
    out = dict(content=dict(N=len(P), S_m=S, frac_vertical=float(vert.mean())))
    rows = []
    print(f"\n{'case':34s} {'n/m3':>8s} {'mg/m3':>6s} {'tau%':>5s} {'g/h':>5s} {'room ug':>7s} {'drop':>5s} "
          f"{'vert':>5s} {'Pbeam':>6s} {'Efl/AEL':>8s} {'spots':>5s} {'glit':>5s} {'modes':>8s} {'e-':>7s} "
          f"{'wand':>5s} {'air m3/h':>8s} {'gdots':>5s}")
    cases = {
        "room 20 Hz N_s 1 (B' settings)": dict(),
        "room 30 Hz N_s 1": dict(f_r=30.0),
        "room 20 Hz N_s 2 (fewer dropouts)": dict(N_s=2.0),
        "room 20 Hz a 5 um": dict(a=5e-6),
        "room 20 Hz, 1 ms flashes": dict(t_flash=1e-3),
        "room 20 Hz, 99 % capture": dict(eta_c=0.99),
        "room 20 Hz, w_v 80 um": dict(w_v=80e-6),
        "room 20 Hz, delta 5 mm, 1.5 cd/m2": dict(delta=5e-3, L_line=1.5),
        "desk 0.3 m column (S 1 m)": dict(C=0.3),
    }
    for name, kw in cases.items():
        Sx = 1.0 if "desk" in name else S
        r = flowr2(S=Sx, **kw)
        r["case"] = name
        rows.append(r)
        print(f"{name:34s} {r['n_per_m3']:8.2e} {r['mass_mg_m3']:6.1f} {r['tau_col_pct']:5.2f} {r['g_per_h']:5.2f} "
              f"{r['room_ug_m3']:7.1f} {r['p_drop_100ms']:5.3f} {r['vert_cov_50ms']:5.2f} {r['P_beam_mW']:6.2f} "
              f"{r['E_flash_uJ'] / r['ael_single_uJ']:8.2f} {r['simult_spots']:5.0f} {r['glitter']:5.3f} "
              f"{r['modes_vis']:8.2e} {r['probe_electrons']:7.0f} {r['wander_mm']:5.2f} {r['air_m3_h']:8.0f} "
              f"{r['ghost_dots']:5.3f}")
    r0 = rows[0]
    print(f"\n  haze: column {r0['haze_cd_m2']:.4f} cd/m2 vs dark wall {r0['dark_wall_cd_m2']:.3f} cd/m2 at 10 lux "
          f"(contrast {r0['haze_cd_m2'] / r0['dark_wall_cd_m2'] * 100:.1f} %); probe z_R {r0['z_R_probe_m']:.2f} m; "
          f"look-ahead {r0['lead_ms']:.1f} ms; spurious crossings per probe beam {r0['spurious_per_beam_s']:.0f}/s; "
          f"total probe power {r0['P_probe_total_mW']:.0f} mW; flash {r0['t_flash_ms']:.1f} ms, "
          f"{r0['E_flash_uJ']:.2f} uJ vs single-pulse AEL {r0['ael_single_uJ']:.2f} uJ")
    out["rows"] = rows

    # ghosts: geometry in metres, image centre at (0, 0, 1.2) m above the floor; armor content
    Pw = P + np.array([0.0, 0.0, 1.2])
    box = (np.array([-0.4, -0.4, 0.75]), np.array([0.4, 0.4, 1.65]))
    Bpos = np.array([0.35, 0.0, 2.45])                            # probe projector in the ceiling unit
    cams = [np.array([-1.4, 0.9, 2.3]), np.array([1.0, -1.3, 2.3]), np.array([-0.2, 1.6, 2.3])]
    r0 = rows[0]
    gres = {}
    for eps in (0.5e-3, 1.0e-3):
        gs = np.array([ghost_counts(Pw, Bpos, cam, eps, box) for cam in cams])
        r_vox = r0["n_per_m3"] * 0.25 * (2 * 0.35e-3) * (2 * eps)   # crossings/s through one probe-beam x pixel voxel
        d = dict(g_mean=[float(g.mean()) for g in gs], r_vox=r_vox)
        for tau_c in (2e-3, 1e-3, 0.5e-3):
            d[f"ratio_2cam_tau{tau_c * 1e3:.1f}ms"] = float(np.mean(ghost_ratio(gs[:2], r_vox, tau_c)))
            d[f"ratio_3cam_tau{tau_c * 1e3:.1f}ms"] = float(np.mean(ghost_ratio(gs, r_vox, tau_c)))
        gres[f"{eps * 1e3:.1f}"] = d
        print(f"  ghosts at eps {eps * 1e3:.1f} mm: single-camera ghost beams per sample "
              + ", ".join(f"{g:.1f}" for g in d["g_mean"]) + f" (r_vox {r_vox:.1f}/s); accidental/true: "
              + "; ".join(f"2 cams {d[f'ratio_2cam_tau{t:.1f}ms']:.3f}, 3 cams {d[f'ratio_3cam_tau{t:.1f}ms']:.4f} "
                          f"at {t:.1f} ms" for t in (2.0, 1.0, 0.5)))
    out["ghosts"] = gres
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m23_flowr2.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))


if __name__ == "__main__":
    main()

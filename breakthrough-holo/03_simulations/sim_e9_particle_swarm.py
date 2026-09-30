"""E9: Grey-zone check: can a SWARM of projector-supplied levitated particles (acoustic traps,
RGB-lit) reach Iron Man scale safely? This is the only full-colour, efficient-light alternative (T1).

Physics:
  * Gor'kov radiation force on a small sphere in a standing wave of pressure amplitude p0:
      F_max = 4 pi a^3 k (p0^2 / (4 rho c^2)) Phi,  Phi = f1/3 + f2/2 (~0.80 for EPS in air)
    Calibration: MATD (Hirayama 2019) moved 1 mm-radius EPS beads at up to 8.75 m/s with ~kPa traps.
  * Drag F_d = 0.5 rho v^2 Cd pi a^2 (Cd from standard sphere curve).
  * Stroke budget (film target R4 DR-4): 9-57 m of stroke per frame; N = L_stroke * f_frame / v.
  * Acoustic power per trap ~ focal intensity p0^2/(2 rho c) x lambda^2 / splitting efficiency (0.5).
  * Room ultrasound level: direct + reverberant (Sabine, air absorption included).
Limits (R3): IRPA 1984 public 100 dB (25-100 kHz bands); ACGIH ceiling 115 dB (+30 dB if no body coupling).
"""
import math

import numpy as np

from holo_common import C_SOUND, RHO_AIR, iso9613_alpha_db_per_m, save_json

MU = 1.81e-5


def cd_sphere(Re):
    return 24 / Re * (1 + 0.15 * Re ** 0.687) + 0.42 / (1 + 4.25e4 * Re ** -1.16)


def max_speed(p0, a=1e-3, f=40e3, rho_p=30.0):
    k = 2 * math.pi * f / C_SOUND
    f2 = 2 * (rho_p - RHO_AIR) / (2 * rho_p + RHO_AIR)
    Phi = 1 / 3 + f2 / 2
    F = 4 * math.pi * a ** 3 * k * p0 ** 2 / (4 * RHO_AIR * C_SOUND ** 2) * Phi
    # speed where drag equals available force (minus weight margin ignored for horizontal moves)
    v = np.linspace(0.01, 30, 3000)
    Re = RHO_AIR * v * 2 * a / MU
    Fd = 0.5 * RHO_AIR * v ** 2 * cd_sphere(Re) * math.pi * a * a
    ok = v[Fd < F]
    return float(ok.max()) if len(ok) else 0.0, F


def room_spl(W_ac, f=40e3, V=50.0, surf_abs_m2=20.0, r=0.6):
    m = iso9613_alpha_db_per_m(f) / 8.686  # Np/m
    A = surf_abs_m2 + 4 * m * V
    I_rev = 4 * W_ac / A
    I_dir = W_ac / (4 * math.pi * r * r) * math.exp(-2 * m * r)
    return 10 * math.log10(I_rev / 1e-12), 10 * math.log10((I_rev + I_dir) / 1e-12)


if __name__ == "__main__":
    print("E9 particle swarm (acoustic levitation) at Iron Man scale")
    out = {}
    # calibration: MATD-like, 1 mm radius EPS, 40 kHz
    for p0 in (1000, 2000, 4000, 8000):
        v, F = max_speed(p0)
        print(f"  p0={p0:5d} Pa ({20*math.log10(p0/math.sqrt(2)/2e-5):.0f} dB rms): max bead speed {v:.1f} m/s, force {F*1e6:.1f} uN")
    v_cal, _ = max_speed(4000)
    out["calibration"] = dict(p0=4000, v_max=v_cal, MATD_reported=8.75)
    print(f"  [CAL] at 4 kPa model gives {v_cal:.1f} m/s vs MATD 3.75-8.75 m/s (order-of-magnitude check)")
    rows = []
    for stroke_m, fr in ((9.0, 30.0), (9.0, 60.0), (57.0, 60.0)):
        for p0 in (2000, 4000):
            v, F = max_speed(p0)
            N = stroke_m * fr / v
            I_focus = p0 ** 2 / (2 * RHO_AIR * C_SOUND)
            lam = C_SOUND / 40e3
            W_trap = I_focus * lam ** 2 / 0.5
            W = N * W_trap
            spl_rev, spl_near = room_spl(W)
            rows.append(dict(stroke_m=stroke_m, frame_hz=fr, p0=p0, v=v, particles=N, W_acoustic=W,
                             room_reverb_dB=spl_rev, head_0p6m_dB=spl_near))
            print(f"  stroke {stroke_m:4.0f} m/frame @ {fr:.0f} Hz, p0 {p0} Pa: v={v:.1f} m/s -> {N:6.0f} particles, "
                  f"{W:7.0f} W ultrasound -> room {spl_rev:.0f} dB, head at 0.6 m {spl_near:.0f} dB (public limit 100)")
    out["iron_man_scale"] = rows
    # smallest useful accent layer: 5 beads (arc reactor, highlights)
    for N in (1, 5, 20):
        W = N * (4000 ** 2 / (2 * RHO_AIR * C_SOUND)) * (C_SOUND / 40e3) ** 2 / 0.5
        spl_rev, spl_near = room_spl(W)
        out[f"accent_{N}"] = dict(W=W, room=spl_rev, near=spl_near)
        print(f"  accent layer {N:2d} beads: {W:6.1f} W -> room {spl_rev:.0f} dB, head {spl_near:.0f} dB")
    save_json("e9_particle_swarm.json", out)
    print("  -> Iron-Man-scale particle swarms need ~30-450 fast particles and fill the room with 123-142 dB "
          "ultrasound: NOT SAFE. Even a 1-5 bead colour accent gives 114-126 dB, above the 100 dB public limit (below the ACGIH 145 dB no-contact ceiling).")

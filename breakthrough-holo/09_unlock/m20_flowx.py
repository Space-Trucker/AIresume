"""M20: FLOW-X, a POV mote display whose vertical scan is a conditioned laminar air column (no IR, no photophoresis).

Concept (IDEA_ROUND_4_HOME_BRIEF.md):
- a push-pull air column (downward, speed U, turbulence intensity Tu, side D) carries injected white motes of radius a
  through the image volume (height H);
- cameras track the motes;
- visible spots light a mote only while it is inside the content (a stroke of thickness d_s);
- in the frame moving with the air the motes are static voxels, so the visible spots can be translated rigidly at U
  by a global scanner and the hologram only switches spots on and off.

Physics used (all [DERIVED] unless marked):
- Mote response: Stokes time tau_p = rho (2a)^2 / (18 mu); settling speed v_s = 2 rho g a^2 / (9 mu); Stokes number
  tau_p U / l_eddy << 1, so the motes follow the air.
- Lateral wander over the fall. The turbulence decays slowly (eddy turnover l_t/sigma >> H/U), so a mote keeps its
  lateral velocity: sigma_x ~ Tu * U * (H/U) = Tu * H, independent of U [ESTIMATE; frozen, ballistic regime].
- POV duty per content point: D = f_r * d_s / U (the time a mote spends inside a stroke of thickness d_s, times
  f_r passes per second).
- Brightness: a 1 mm line of luminance L, sampled every delta, needs J = L * 1e-3 * delta (cd) per point. A lit mote
  must give J / D while lit, i.e. scattered flux 4 pi (J/D)/q, where q_iso ~ 0.3 for a white diffuse sphere seen
  from the side (RT6 C3; 2 opposed beams for viewers all round).
- Spot efficiency: the fraction of a Gaussian spot (waist w_v) intercepted by a mote of radius a centred in it is
  1 - exp(-2 a^2 / w_v^2).
- Eye safety (visible): a pupil on a stroke receives f_r passes per second, each lasting d_s/U (the spot is on only
  inside the stroke). The mean through a 7 mm pupil, times the stacking s (beams of neighbouring motes; ~3 assumed
  from RT6 M5), must be <= 0.39 mW (Class 1, long exposure).
- Particulates: in-flight mass = N_flight * m; mass circulated per hour; room level for a recapture efficiency
  eta_c in a 50 m^3 room at 0.5 air changes per hour (steady state = escape rate / (ACH * V)).
- Visible hologram modes (co-moving engine, per head): (2 clip os L / (pi w_v))^2, as m18.

Run: python3 m20_flowx.py -> results/m20_flowx.json, results/m20_run.log
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MU, G = 1.81e-5, 9.81
V500 = 683 * 0.323                                   # lm/W at 500 nm (cyan, as m15-m19)


def flowx(a=10e-6, rho=1190.0, U=0.3, Tu=0.002, H=1.0, Dcol=0.6, S=5.0, delta=3e-3, d_s=1e-3, L=3.0, f_r=60.0,
          w_v=None, q=0.3, n_beams=2, s_stack=3.0, eta_c=0.999, eta_opt=0.5, heads=4, room_V=50.0, ach=0.5,
          frac_horizontal=0.6):
    m = 4 / 3 * math.pi * a ** 3 * rho
    tau_p = rho * (2 * a) ** 2 / (18 * MU)
    v_s = 2 * rho * G * a * a / (9 * MU)
    sig_x = Tu * H                                    # lateral wander at the bottom of the image
    # supply: horizontal content needs one stream per (x, y) pixel; vertical strokes share a column. Hit
    # probability of passing within +-d_s/2 of the aimed y when the wander is sig_x (1D Gaussian):
    p_hit = math.erf(d_s / 2 / (math.sqrt(2) * max(sig_x, 1e-9)))
    n_pix = S / delta
    n_col = n_pix * frac_horizontal + (S * (1 - frac_horizontal)) / 0.05   # vertical strokes: ~1 column per 5 cm
    flux = n_col * f_r / p_hit                        # motes/s injected
    t_fall = H / (U + v_s)
    n_flight = flux * t_fall
    mass_rate = flux * m                              # kg/s circulated
    room_ugm3 = mass_rate * (1 - eta_c) * 3600 / (ach * room_V) * 1e9
    col_ugm3 = n_flight * m / (Dcol * Dcol * H) * 1e9
    # POV duty and lit-mote brightness
    D = min(1.0, f_r * d_s / (U + v_s))
    J = L * 1e-3 * delta
    flux_lit = 4 * math.pi * (J / D) / q / V500      # W scattered (isotropic-equivalent) by a lit mote
    if w_v is None:
        w_v = max(2.5 * a, 20e-6)                     # spot a few mote radii wide: covers the tracking error
    eff = 1 - math.exp(-2 * a * a / (w_v * w_v))
    P_spot = flux_lit / (n_beams * eff)               # per beam, while lit
    # pupil: f_r passes/s, each lit for d_s/U, n_beams beams converge, stacking s_stack
    pupil = s_stack * n_beams * P_spot * f_r * d_s / (U + v_s)
    lit_now = n_pix * D                               # motes lit at any instant (one per content point x duty)
    P_vis = lit_now * n_beams * P_spot / eta_opt
    stray = P_vis * (1 - eff)
    L_wall = 0.8 * stray * V500 / (math.pi * room_V)  # bare walls (no receivers), as RT7 C1 M8 estimate
    modes = heads * (2 * 1.2 * 1.5 * Dcol / (math.pi * w_v)) ** 2
    holo_rate = (U + v_s) / d_s                       # on/off switching rate in the co-moving frame
    latency = t_fall
    return dict(a_um=a * 1e6, U=U, Tu=Tu, tau_p_ms=tau_p * 1e3, v_s_mm_s=v_s * 1e3, sig_x_mm=sig_x * 1e3, p_hit=p_hit,
                flux=flux, n_flight=n_flight, mass_g_per_h=mass_rate * 3600 * 1e3, col_ugm3=col_ugm3, room_ugm3=room_ugm3,
                duty=D, w_v_um=w_v * 1e6, eff=eff, P_spot_uW=P_spot * 1e6, pupil_mW=pupil * 1e3, lit_now=lit_now,
                P_vis_W=P_vis, L_wall=L_wall, modes=modes, holo_rate=holo_rate, latency_s=latency,
                class1_vis=pupil <= 0.39e-3)


def main():
    rows = []
    print(f"{'a':>4s} {'U':>4s} {'Tu%':>5s} {'tau_p':>6s} {'v_s':>5s} {'sig_x':>5s} {'p_hit':>5s} {'flux/s':>8s} "
          f"{'flight':>8s} {'g/h':>6s} {'col':>7s} {'room':>7s} {'duty':>5s} {'w_v':>4s} {'eff':>5s} {'Pspot':>7s} "
          f"{'pupil':>6s} {'P_vis':>6s} {'Lwall':>6s} {'modes':>8s} {'lat':>4s}")
    for a in (2.5e-6, 5e-6, 10e-6, 15e-6, 25e-6):
        for U in (0.2, 0.3):
            for Tu in (0.001, 0.003):
                d = flowx(a=a, U=U, Tu=Tu)
                rows.append(d)
                print(f"{d['a_um']:4.1f} {U:4.1f} {Tu * 100:5.2f} {d['tau_p_ms']:6.2f} {d['v_s_mm_s']:5.1f} {d['sig_x_mm']:5.1f} "
                      f"{d['p_hit']:5.2f} {d['flux']:8.2e} {d['n_flight']:8.2e} {d['mass_g_per_h']:6.3f} {d['col_ugm3']:7.1f} "
                      f"{d['room_ugm3']:7.2f} {d['duty']:5.2f} {d['w_v_um']:4.0f} {d['eff']:5.3f} {d['P_spot_uW']:7.1f} "
                      f"{d['pupil_mW']:6.3f} {d['P_vis_W']:6.3f} {d['L_wall']:6.3f} {d['modes']:8.2e} {d['latency_s']:4.1f}"
                      f"{'' if d['class1_vis'] else '  CLASS1-VIS FAIL'}")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m20_flowx.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()

"""M23b: the rain rendering law for FLOW-R / FLOW-R2 (main session, round 9).

A uniform rain (density n, fall speed U) renders a stroke of thickness d_s. Each mote is lit while it is inside the
stroke tube.
- **Fill.** The painted fraction of the stroke over an eye time t_eye is F(theta) ~ n U d_s^2 t_eye (|cos theta| +
  |sin theta|), where theta is the angle between the stroke and the flow. It is the same order for vertical strokes
  (flowing streaks) and horizontal strokes (dots). The perceived lit fraction is 1 - exp(-F).
- **Lit motes.** The number lit at once is n d_s^2 S = F_0 S / (U t_eye), independent of d_s, with S the stroke
  length and F_0 = F(0).
- **Per-mote output.** Each lit mote must supply a luminous intensity J = L d_s / (n d_s^2) for line luminance L.
- **Cost of solid lines.** Mass, haze and particle load scale with n = F_0 / (U d_s^2 t_eye). Thicker lines are
  therefore cheap in mass, but simultaneous spots grow with F_0 S / (U t_eye) whatever the thickness.
Run: python3 m23b_rain_law.py -> results/m23b_run.log
"""
import math

MU, G, RHO = 1.81e-5, 9.81, 1520.0


def law(S, U, d_s, F0, a=7e-6, t_eye=0.05, C=0.8, L=3.0, w_v=80e-6, V=0.71, p_worst=0.764 * 0.66):
    v_s = 2 * RHO * G * a * a / (9 * MU)
    Uf = U + v_s
    n = F0 / (Uf * d_s * d_s * t_eye)
    m = 4 / 3 * math.pi * a ** 3 * RHO
    J = L * d_s / (n * d_s * d_s)
    p_sc = 4 * math.pi * J / (p_worst * 683 * V)
    eff = (1 - math.exp(-2 * a * a / w_v ** 2)) * 0.9
    return dict(n=n, mg_m3=n * m * 1e6, tau_pct=n * 2 * math.pi * a * a * C * 100, g_h=n * Uf * C * C * m * 3.6e6,
                spots=n * d_s * d_s * S, P_mW=p_sc / eff * 1e3, lit_frac=1 - math.exp(-F0))


if __name__ == "__main__":
    print(f"{'scale':6s} {'S m':>4s} {'U':>5s} {'d_s mm':>6s} {'F0':>4s} {'lit':>5s} {'n/m3':>8s} {'mg/m3':>6s} "
          f"{'tau%':>5s} {'g/h':>6s} {'spots':>6s} {'P/mote mW':>9s}")
    for scale, S, C in (("room", 3.08, 0.8), ("desk", 1.0, 0.3)):
        for U in (0.25, 0.15):
            for d_s in (1e-3, 2e-3):
                for F0 in (0.33, 1.0):
                    r = law(S, U, d_s, F0, C=C)
                    print(f"{scale:6s} {S:4.1f} {U:5.2f} {d_s * 1e3:6.1f} {F0:4.2f} {r['lit_frac']:5.2f} {r['n']:8.2e} "
                          f"{r['mg_m3']:6.1f} {r['tau_pct']:5.2f} {r['g_h']:6.2f} {r['spots']:6.0f} {r['P_mW']:9.3f}")

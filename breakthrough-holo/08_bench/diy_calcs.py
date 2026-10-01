"""DIY engineering calculations (stages DIY-1 to DIY-3) using the validated MOTE physics (07_mote_route/mote/physics.py).

DIY-1 photophoretic velocimetry: drift speed per particle type, the camera fps/scale needed, and heating.
DIY-2 BYU-style optical trap display: the power window for a trapped particle, between holding it against gravity and
      drafts, and keeping it below its burn/melt temperature. Also maximum drawing speed against absorbed power, and the
      image size drawable at a given refresh rate.
DIY-3 self-glowing particles: fluorescent polymer spheres versus dense phosphor grains (why dense grains fail).
Run: python3 diy_calcs.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))
import physics as ph  # noqa: E402

# particle catalogue: (radius m, density, k_p W/m/K, J1/A, absorptance at the trap wavelength, max safe T K, note)
PARTICLES = {
    "glassy carbon sphere, d=5 um": (2.5e-6, 1500, 6.3, 0.5, 0.9, 900, "skin-deep absorber, high k: force-law reference"),
    "carbon-coated hollow glass, d=5 um": (2.5e-6, 400, 0.1, 0.5, 0.9, 700, "skin-deep, low k; NOT a stock item (R11): custom (B2)"),
    "laser-printer toner, d~8 um": (4e-6, 1200, 0.2, 0.3, 0.8, 335, "cheap; volume absorber; binder Tg ~50-65 C (R11), wax"),
    "black PMMA/PS sphere, d=10 um": (5e-6, 1100, 0.2, 0.3, 0.8, 373, "volume absorber; Tg ~100 C"),
    "fluorescent PS sphere, d=10 um": (5e-6, 1050, 0.15, 0.15, 0.3, 373, "dye absorbs 405 nm; weak absorber; Tg ~100 C; bleaches"),
    "LED phosphor grain (nitride), d~15 um": (7.5e-6, 4000, 3.0, 0.3, 0.8, 700, "dense ceramic: heavy and high k"),
    "activated charcoal grain, d~6 um": (3e-6, 600, 0.2, 0.5, 0.9, 620, "ESTIMATED props: porous, irregular (BYU char-like); "
                                         "oxidises in air above ~350 C"),
}


def diy1(I=1e5, um_per_px=3.0):
    print(f"\nDIY-1 velocimetry at I = {I / 1e4:.0f} W/cm^2 (peak of 0.63 W in a Gaussian of 4 mm 1/e^2 diameter; I0 = 2P/(pi w^2)),"
          f" {um_per_px} um/px")
    for name, (a, rho, kp, j1A, A, Tmax, note) in PARTICLES.items():
        F = A * ph.photophoretic_force(a, I, kp, J1=j1A)
        v = F / (6 * math.pi * ph.mu_air(ph.T0) * a) * ph.cunningham(a)
        vs = ph.settling_velocity(a, rho)
        dT = ph.mote_temperature(A * math.pi * a * a * I, a) - ph.T0
        fps = max(v, vs) / (5 * um_per_px * 1e-6)
        print(f"  {name:38s} drift {v * 1e3:6.2f} mm/s  settle {vs * 1e3:5.2f} mm/s  heating {dT:5.1f} K  "
              f"-> camera >= {fps:4.0f} fps")


def window(name, C_ph=0.85):
    """(force per absorbed W [N/W], absorbed W that balances the weight along the beam (eta = 1), absorbed W at which
    the mean temperature reaches the particle's max safe T)."""
    a, rho, kp, j1A, A, Tmax, note = PARTICLES[name]
    weight = 4 / 3 * math.pi * a ** 3 * rho * ph.G
    fpw = ph.force_per_absorbed_watt(a, kp, j1A=j1A, C_ph=C_ph)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if ph.mote_temperature(mid, a) < Tmax else (lo, mid)
    return fpw, weight / fpw, lo


def v_levitated(name, contrast, eta=0.4):
    """Top lateral speed of a particle levitated in one upward beam, in a dark pocket of the given contrast
    (P_wall / P_axis, capped by the burn limit): eta (C - 1) times the settling speed, with the air viscosity taken at
    the film temperature of the particle when it absorbs the wall power (P_lev * C)."""
    a, rho, kp, j1A, A, Tmax, note = PARTICLES[name]
    fpw, P_lev, P_burn = window(name)
    C = min(contrast, P_burn / P_lev)
    T = ph.mote_temperature(P_lev * C, a)
    v_s = ph.settling_velocity(a, rho) * ph.mu_air(ph.T0) / ph.mu_air(0.5 * (ph.T0 + T))
    return max(0.0, eta * (C - 1) * v_s)


def diy2(lam_trap=405e-9, w=8e-6):
    """Single-beam trap at ~100 mm focal length, focal spot w. Window = [P_hold, P_burn] in absorbed power, then trap power
    via intercept (spot ~ particle)."""
    print(f"\nDIY-2 trap display (405 nm, focal spot w = {w * 1e6:.0f} um; eta_lateral ~0.4 assumed, BYU regime)")
    print("  v_max 'axially balanced' needs the axial push cancelled by something other than gravity: a counter-propagating\n"
          "  (retro) beam, or the shape-dependent mechanism of BYU's irregular particles. 'Levitated' = gravity balances the\n"
          "  push in one upward beam; pocket contrast 7 (cheap singlet) or 80 (ideal vortex plate) from sim_d1_lens_trap.py.")
    print("  The absorbed-power window (hold..burn) is the robust number. 'peak-intercept power' assumes the particle sits at\n"
          "  the beam peak; in a dark-pocket trap it absorbs only edge light, so the laser power needed is higher (BYU's\n"
          "  measured minimum hold: 18-24 mW at 405 nm). Raise power slowly; above the burn line the particle chars or melts.")
    eta = 0.4
    for name, (a, rho, kp, j1A, A, Tmax, note) in PARTICLES.items():
        fpw, P_lev, P_burn = window(name)
        P_hold = P_lev / eta                                               # absorbed W to hold against gravity laterally
        icp = 1 - math.exp(-2 * a * a / (w * w))
        # max lateral speed at the burn limit (relative to air)
        v_max = eta * fpw * P_burn / (6 * math.pi * ph.mu_air(0.5 * (ph.T0 + Tmax)) * a) * ph.cunningham(a)
        ok = "OK" if P_burn > 3 * P_hold else ("marginal" if P_burn > P_hold else "CANNOT TRAP")
        # levitated in a single upward beam (sim_d1_lens_trap): v = eta (contrast - 1) v_settle, contrast <= burn cap
        v_lev = [v_levitated(name, C) for C in (7, 80)]
        print(f"  {name:38s} hold {P_hold * 1e6:8.2f} uW_abs  burn {P_burn * 1e3:6.2f} mW_abs  window x{P_burn / P_hold:8.0f} [{ok}]"
              f"  peak-intercept power {P_hold / (A * icp) * 1e3:6.3f}-{P_burn / (A * icp) * 1e3:6.1f} mW\n"
              f"  {'':38s} v_max: axially balanced {v_max:5.2f} m/s | levitated, lens pocket {v_lev[0] * 1e3:5.1f} mm/s, "
              f"vortex plate {v_lev[1] * 1e3:5.1f} mm/s")


def drawing(v=0.5, f=(10, 20, 30)):
    print(f"\nDrawing with one particle at {v} m/s: path per frame = v/f")
    for fr in f:
        L = v / fr
        print(f"  {fr:2d} Hz: {L * 100:5.1f} cm of line per frame (a circle of diameter {L / math.pi * 100:4.1f} cm)")


if __name__ == "__main__":
    diy1()
    diy2()
    drawing(0.5)
    drawing(1.8)

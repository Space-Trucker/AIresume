"""M22: needles for the home vision, quantified. Each part is a bound or a model behind a T9 claim.

A. Laplace low-pass. A static or quasi-static field (E, B, potential flow) set up by sources outside the image cannot
   address mm-scale structure: a Fourier component of period Lam decays as exp(-2 pi d / Lam) a distance d from the
   sources [DERIVED, standard]. Only propagating waves (light, sound) address single motes in open air.
B. Photo-charge. Light can change a bead's charge only one way in air [DERIVED]:
   - a positive bead recaptures its photoelectrons. They thermalise and attach to O2 within ~5 um, where the bead's own
     field beats any safe room field once q > 4 pi eps0 (a + r_t)^2 E_room;
   - a negative bead loses electrons readily (they are repelled), so photodetachment lowers |q|;
   - raising |q| needs like-sign ions against the bead's Coulomb barrier. Diffusion charging stalls near
     4 pi eps0 a kT/e, and field charging at the Pauthenier limit 12 pi eps0 a^2 E_local. So recharging needs a corona
     zone (E ~ 1e6 V/m), not the image volume.
C. One-way charge ratchet. Per-bead charge control is "down only" (light) plus a global field (up for all). Under
   fluctuating per-bead loads the global field must grow every time any bead swings from a low to a high load. This
   part simulates the field growth and the lifetime before the field leaves a 10x range.
D. Time-shared thermal kick theorem. One beam visits K beads, each for t_d, so T_rev = K t_d. A lumped bead
   (tau_th = rho c a^2 / (3 k_g)) peaks at
       dT_peak / dT_ss = K (1 - exp(-t_d / tau)) / (1 - exp(-T_rev / tau))  ->  T_rev / tau_th  (t_d << tau << T_rev),
   while the mean force is unchanged (linear). Time-sharing therefore costs heat in proportion to T_rev / tau_th.
E. Self-addressing laser cavity: each mote a retroreflecting end mirror sharing one gain medium. Needs:
   - Fresnel condition a R >= 0.72 lam L for low diffraction loss;
   - gain etendue >= field etendue G = (X lam / (pi w))^2. A slab of gain g and thickness t = ln(G_p)/g holds
     NA^2 <= 2 lam / (pi t) without channel overlap, so its etendue is 2 A lam / t;
   - pump power P >= A t N_inv h nu_p / tau = G (ln G_p)^2 h nu_p / (2 lam g sigma_e tau) [DERIVED].
F. Coulomb crystal of charged beads (motes as in-volume electrodes). The shear modulus 0.1 n q^2/(4 pi eps0 a_ws) is
   compared with the draft stress n 6 pi mu a du l.
G. E-AIR-SV: AIR-SV (m21) plus a fixed per-bead charge and a weak global field. The static wake deficits (m21b) and the
   size spread are compensated by charge set at injection (trimmed down by photodetachment on content changes). The
   common-mode cross-draft is compensated by a global horizontal field. Outputs: field, charge use, hand distortion.
H. Tetralemma numbers. Per-mote authority v under a per-focus cap gives w_max; then the hologram modes per head and
   the loop rate, against commodity modulators. h s are m18's worst-direction factor times stacking (skin: h_worst 2.14
   x s_skin 1.1; eye static 7.1; eye sparse 1.5). The loop column is 10 v / w at the MEAN speed; gust peaks
   (U + 5.4 sigma, RT6 C1) are ~3-4x higher.

Run: python3 m22_needles.py -> results/m22_needles.json, results/m22_run.log
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m21_airsv as m21  # noqa: E402
import m21b_bead_wakes as m21b  # noqa: E402

EPS0, E_CH, KB, T0 = 8.854e-12, 1.602e-19, 1.381e-23, 293.0
MU, RHO_A, KG = 1.81e-5, 1.2, 0.026
LAM = 1.55e-6
I_UNIT = 1.5e7                      # W/m^2 per m/s, realistic skin (RT7 C2)
SKIN_CAP, EYE_CAP = 0.785e-3, 10e-3


def peek_sphere(a):
    """Corona-onset surface field of a sphere of radius a (m), Peek's sphere form, 27.2 (1 + 0.54/sqrt(r_cm)) kV/cm."""
    r_cm = a * 100
    return 27.2e5 * (1 + 0.54 / math.sqrt(r_cm))


def q_limit(a):
    return 4 * math.pi * EPS0 * a * a * peek_sphere(a)


# ---------------------------------------------------------------- A
def part_a():
    rows = []
    for lam_s in (3e-3, 6e-3, 0.03, 0.1):
        for d in (0.05, 0.3, 1.0):
            rows.append(dict(period_m=lam_s, d_m=d, attenuation=math.exp(-2 * math.pi * d / lam_s)))
    d_1pc = {lam_s: lam_s * math.log(100) / (2 * math.pi) for lam_s in (3e-3, 6e-3, 0.03, 0.1)}
    return dict(rows=rows, d_for_1pc=d_1pc)


# ---------------------------------------------------------------- B
def part_b(a=20e-6, E_room=1e3, r_t=5e-6):
    q_need = 1e-13
    q_pos_photo = 4 * math.pi * EPS0 * (a + r_t) ** 2 * E_room
    q_pos_4V = 4 * math.pi * EPS0 * a * 4.0
    q_diff = 4 * math.pi * EPS0 * a * KB * T0 / E_CH * math.log(1 + 1e3)   # ~ln(1 + N t) with N t ~ 1e3 [ESTIMATE]
    q_pauth_room = 12 * math.pi * EPS0 * a * a * E_room
    q_pauth_corona = 12 * math.pi * EPS0 * a * a * 1e6
    return dict(a_um=a * 1e6, q_needed=q_need, q_limit_peek=q_limit(a), q_pos_photo_recapture=q_pos_photo,
                q_pos_photo_4V=q_pos_4V, q_like_ion_diffusion=q_diff, q_pauthenier_room=q_pauth_room,
                q_pauthenier_corona_1MVm=q_pauth_corona)


# ---------------------------------------------------------------- C
def ratchet(f, N=1667, tau_c=1.0, dt=0.02, t_max=3600.0, E_range=10.0, seed=1, f_light=0.0):
    """Down-only per-bead charge plus a global field. Load F_i = 1 + f xi_i(t), xi an OU process (unit variance,
    correlation time tau_c). Light (bidirectional) absorbs |f xi| up to f_light, so the charge carries only the excess
    beyond the light's authority. Returns the time at which the field must exceed E_range x its start."""
    rng = np.random.default_rng(seed)
    xi = rng.normal(size=N)
    a_ou = math.exp(-dt / tau_c)
    b_ou = math.sqrt(1 - a_ou * a_ou)

    def charge_load(x):
        excess = np.sign(x) * np.maximum(np.abs(f * x) - f_light, 0.0)
        return 1.0 + excess

    F = charge_load(xi)
    E = 1.0
    q = F / E
    t = 0.0
    while t < t_max:
        xi = a_ou * xi + b_ou * rng.normal(size=N)
        F = charge_load(xi)
        E = max(E, float(np.max(F / q)))
        q = np.minimum(q, F / E)
        t += dt
        if E > E_range:
            return t
    return float("inf")


def part_c():
    rows = []
    for f in (0.003, 0.01, 0.03, 0.1, 0.3):
        for N in (100, 1667):
            life = ratchet(f, N=N, t_max=3600.0 if f < 0.03 else 600.0)
            rows.append(dict(f=f, N=N, lifetime_s=life))
    # light absorbs fluctuations up to f_light: only the excess ratchets
    for f, fl in ((0.1, 0.3), (0.1, 0.25), (0.3, 0.6)):
        rows.append(dict(f=f, N=1667, f_light=fl, lifetime_s=ratchet(f, N=1667, f_light=fl, t_max=3600.0)))
    return rows


# ---------------------------------------------------------------- D
def kick_ratio(K, t_d, tau):
    T = K * t_d
    return K * (1 - math.exp(-t_d / tau)) / (1 - math.exp(-T / tau))


def kick_sim(K, t_d, tau, n_per=40, periods=40):
    """Direct integration of the lumped model (validates the closed form)."""
    T = K * t_d
    dt = min(t_d / n_per, tau / 50)
    x = 0.0          # dT / dT_ss (P_mean R_th = 1)
    peak = 0.0
    t = 0.0
    while t < periods * T:
        p = K if (t % T) < t_d else 0.0
        x += dt * (p - x) / tau
        t += dt
        if t > (periods - 2) * T:
            peak = max(peak, x)
    return peak


def part_d():
    rows = []
    for a, rho, cp in ((40e-6, 600.0, 800.0), (30e-6, 600.0, 800.0), (20e-6, 300.0, 800.0), (5e-6, 1190.0, 1420.0)):
        tau = rho * cp * a * a / (3 * KG)
        for K, t_d in ((1000, 1e-4), (100, 1e-4), (10, 1e-4), (500, 1e-5)):
            rows.append(dict(a_um=a * 1e6, rho=rho, tau_th_ms=tau * 1e3, K=K, t_d_ms=t_d * 1e3,
                             T_rev_ms=K * t_d * 1e3, ratio=kick_ratio(K, t_d, tau),
                             approx_Trev_over_tau=K * t_d / tau))
    check = (kick_ratio(200, 1e-4, 2e-3), kick_sim(200, 1e-4, 2e-3))
    return dict(rows=rows, check_closed_vs_sim=check)


# ---------------------------------------------------------------- E
GAIN_MEDIA = {   # sigma_e (m^2), tau (s), g_max (m^-1), pump photon (J)
    "Er:Yb glass 1535 nm": (7e-25, 8e-3, 100.0, 6.626e-34 * 3e8 / 976e-9),
    "Nd:YAG 1064 nm": (2.8e-23, 2.3e-4, 300.0, 6.626e-34 * 3e8 / 808e-9),
    "InGaAsP bulk 1550 nm": (5e-20, 1e-9, 1.5e5, 6.626e-34 * 3e8 / 1.2e-6),
}


def part_e(X=0.6, L=2.0, loss_rt=0.3):
    rows = []
    G_p = math.sqrt(1 / (1 - loss_rt))
    for w in (20e-6, 40e-6, 60e-6):
        a = 1.5 * w
        R_min = 0.72 * LAM * L / a
        G_field = (X * LAM / (math.pi * w)) ** 2
        modes = G_field / LAM ** 2
        for name, (sig, tau, g, hnu) in GAIN_MEDIA.items():
            t = math.log(G_p) / g
            A_g = G_field * math.log(G_p) / (2 * LAM * g)
            N_inv = g / sig
            P = A_g * t * N_inv * hnu / tau
            rows.append(dict(w_um=w * 1e6, mote_a_um=a * 1e6, R_min_mm=R_min * 1e3, modes=modes, medium=name,
                             t_mm=t * 1e3, A_gain_cm2=A_g * 1e4, P_pump_W=P))
    return dict(G_p=G_p, rows=rows)


# ---------------------------------------------------------------- F
def part_f(a=5e-6, d=3e-3, du=0.01, ell=0.1):
    n = 1 / d ** 3
    a_ws = (3 / (4 * math.pi * n)) ** (1 / 3)
    rows = []
    for frac in (0.03, 0.3, 1.0):
        q = frac * q_limit(a)
        mu_s = 0.1 * n * q * q / (4 * math.pi * EPS0 * a_ws)
        stress = n * 6 * math.pi * MU * a * du * ell
        rows.append(dict(a_um=a * 1e6, d_mm=d * 1e3, q=q, shear_modulus_Pa=mu_s, draft_stress_Pa=stress,
                         strain=stress / mu_s))
    return rows


# ---------------------------------------------------------------- G
def part_g(content="armor", a=40e-6, rho=600.0, spread=0.0025, q_frac=0.3, R_hand=0.04, h_off=0.3,
           u_cross=(0.01, 0.03, 0.05)):
    U = m21.v_settle(a, rho)
    P = m21b.content_points(content)
    u = m21b.wake_field(P, a, U)
    uz = u[:, 2]
    # size spread: v_s varies by 2 spread U (1 sigma); +-3 sigma covered by charge
    size_dev = 3 * 2 * spread * U
    delta = max(0.0, -float(uz.min())) + size_dev     # nominal rise speed the downward electric force cancels
    drag_per_speed = 6 * math.pi * MU * a
    f_i = drag_per_speed * (delta + uz)               # >= 0 by construction (before the size term)
    q_d = q_frac * q_limit(a)
    E_v = drag_per_speed * (delta + float(uz.max()) + size_dev) / q_d
    q_use = f_i / E_v
    E_h = {f"{uc:.2f}": drag_per_speed * uc / q_d for uc in u_cross}
    # grounded hand in the field: monopole from the potential offset h_off*E (hand height vs the field's zero) plus
    # the induced dipole 3x at the surface; equivalent bead speed at distance r from the hand centre
    hand = {}
    for r in (0.06, 0.1, 0.15, 0.2):
        e_pert = E_v * h_off * R_hand / r ** 2 + E_v * 2 * (R_hand / r) ** 3
        hand[f"{r:.2f}"] = q_d * e_pert / drag_per_speed
    # charge leakage in ion-depleted column air: ion pairs ~10 /cm^3/s (radon, cosmic), transit H/U
    n_ion = 10e6 * (1.0 / U)
    tau_leak = EPS0 / (2 * E_CH * n_ion * 1.5e-4)
    return dict(content=content, a_um=a * 1e6, rho=rho, U=U, N=len(P), uz_min_mm_s=float(uz.min()) * 1e3,
                uz_max_mm_s=float(uz.max()) * 1e3, delta_mm_s=delta * 1e3, q_design=q_d, q_limit=q_limit(a),
                E_vertical_V_m=E_v, q_use_p50=float(np.percentile(q_use, 50)) / q_d,
                q_use_max=float(q_use.max()) / q_d, E_horizontal_V_m=E_h,
                hand_pert_speed_mm_s={k: v * 1e3 for k, v in hand.items()}, tau_leak_h=tau_leak / 3600)


# ---------------------------------------------------------------- H
COMMODITY = {"4K LCoS (8.8 Mpx, ~0.1-1 kHz)": 8.8e6, "DLP 0.65in NIR DMD (1 Mpx, ~10 kHz binary)": 1.024e6,
             "TI PLM 0.67in (1.3 Mpx, 1.44 kHz)": 1.3e6}


def part_h(X=0.6):
    rows = []
    for cap_name, cap, hs in (("child skin, h 2.14 x s 1.1", SKIN_CAP, 2.14 * 1.1), ("eye, sparse hs 1.5", EYE_CAP, 1.5),
                              ("eye, static voxel hs 7.1", EYE_CAP, 7.1)):
        for v in (0.01, 0.03, 0.1, 0.3):
            w = math.sqrt(2 * cap / (math.pi * hs * I_UNIT * v))
            modes_true = (X / (math.pi * w)) ** 2
            modes_m18 = (2 * 1.2 * 1.5 * X / (math.pi * w)) ** 2
            loop = 10 * v / w
            rows.append(dict(cap=cap_name, v=v, w_max_um=w * 1e6, modes_true=modes_true, modes_m18=modes_m18,
                             lcos_per_head=modes_true / 8.8e6, loop_Hz=loop))
    return rows


def selftest():
    ok = True
    r = kick_ratio(200, 1e-4, 2e-3)
    s = kick_sim(200, 1e-4, 2e-3)
    ok &= abs(r - s) / r < 0.05
    ok &= abs(kick_ratio(10000, 1e-6, 1e-3) - 10.0) / 10 < 0.06       # t_d << tau << T_rev -> T_rev/tau
    ok &= abs(q_limit(1e-2) / (4 * math.pi * EPS0 * 1e-4 * 27.2e5 * (1 + 0.54))) - 1 < 1e-9
    ok &= ratchet(0.0, N=50, t_max=10.0) == float("inf")              # no fluctuation, no ratchet
    print(f"selftest: kick closed {r:.3f} vs sim {s:.3f}; ratchet(f=0) inf; Peek ok -> {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    assert selftest()
    out = {}
    print("\nA. Laplace low-pass: attenuation exp(-2 pi d / period) of field structure set by sources at distance d")
    out["A"] = part_a()
    for r in out["A"]["rows"]:
        print(f"  period {r['period_m'] * 1e3:6.1f} mm  d {r['d_m']:4.2f} m  attenuation {r['attenuation']:.2e}")
    print("  distance from the sources for 1 % of a period-P component: " +
          ", ".join(f"P {k * 1e3:.0f} mm -> {v * 1e3:.1f} mm" for k, v in out["A"]["d_for_1pc"].items()))

    print("\nB. Photo-charge limits (C) for a 20 um bead, room field 1 kV/m")
    out["B"] = part_b()
    for k, v in out["B"].items():
        print(f"  {k:28s} {v:.3g}")

    print("\nC. One-way charge ratchet: time until the global field leaves a 10x range (OU loads, tau_c 1 s)")
    out["C"] = part_c()
    for r in out["C"]:
        fl = r.get("f_light", 0.0)
        print(f"  f {r['f']:5.3f}  N {r['N']:5d}  light covers {fl:4.2f}  lifetime {r['lifetime_s']:8.1f} s")

    print("\nD. Time-shared thermal kicks: peak dT / steady dT at the same mean power")
    out["D"] = part_d()
    for r in out["D"]["rows"]:
        print(f"  a {r['a_um']:4.0f} um rho {r['rho']:5.0f}  tau_th {r['tau_th_ms']:7.3f} ms  K {r['K']:5d}  t_d "
              f"{r['t_d_ms']:5.3f} ms  T_rev {r['T_rev_ms']:7.2f} ms  ratio {r['ratio']:8.2f}  "
              f"(T_rev/tau {r['approx_Trev_over_tau']:8.2f})")
    print(f"  check: closed form {out['D']['check_closed_vs_sim'][0]:.3f} vs integration "
          f"{out['D']['check_closed_vs_sim'][1]:.3f}")

    print("\nE. Self-addressing intracavity motes: gain etendue and pump power (field 0.6 m, throw 2 m, loss 30 %)")
    out["E"] = part_e()
    for r in out["E"]["rows"]:
        print(f"  w {r['w_um']:3.0f} um (mote a {r['mote_a_um']:3.0f}, head R >= {r['R_min_mm']:5.1f} mm)  modes "
              f"{r['modes']:.2e}  {r['medium']:22s} t {r['t_mm']:8.4f} mm  area {r['A_gain_cm2']:9.2f} cm^2  "
              f"pump >= {r['P_pump_W']:9.2e} W")

    print("\nF. Coulomb crystal of 5 um beads at 3 mm: shear modulus vs draft stress (du 1 cm/s over 10 cm)")
    out["F"] = part_f()
    for r in out["F"]:
        print(f"  q {r['q']:.2e} C  shear {r['shear_modulus_Pa']:.2e} Pa  draft stress {r['draft_stress_Pa']:.2e} Pa  "
              f"strain {r['strain']:.1e}")

    print("\nG. E-AIR-SV: fixed per-bead charge compensates static wakes and size spread (armor, 0.6 m)")
    out["G"] = []
    for a, rho in ((30e-6, 600.0), (40e-6, 600.0), (40e-6, 1200.0)):
        g = part_g(a=a, rho=rho)
        out["G"].append(g)
        print(f"  a {g['a_um']:3.0f} um rho {g['rho']:5.0f}  U {g['U']:.3f} m/s  N {g['N']}  uz {g['uz_min_mm_s']:6.2f}.."
              f"{g['uz_max_mm_s']:5.2f} mm/s  Delta {g['delta_mm_s']:5.2f} mm/s  q {g['q_design']:.2e} C "
              f"(limit {g['q_limit']:.2e})  E_v {g['E_vertical_V_m']:6.0f} V/m  q use p50 {g['q_use_p50']:.2f} max "
              f"{g['q_use_max']:.2f}")
        print("      E_h for cross-draft " + ", ".join(f"{k} m/s: {v:5.0f} V/m" for k, v in g['E_horizontal_V_m'].items())
              + "   hand field perturbation (bead speed) " +
              ", ".join(f"r {k} m: {v:5.1f} mm/s" for k, v in g['hand_pert_speed_mm_s'].items())
              + f"   charge leak tau ~{g['tau_leak_h']:.1f} h")

    print("\nH. Tetralemma: per-mote authority v under a per-focus cap -> largest spot w, modes per head, loop rate")
    out["H"] = part_h()
    for r in out["H"]:
        print(f"  {r['cap']:28s} v {r['v'] * 100:5.1f} cm/s  w_max {r['w_max_um']:6.1f} um  modes(true) "
              f"{r['modes_true']:.2e}  (m18 count {r['modes_m18']:.2e})  4K LCoS per head {r['lcos_per_head']:7.1f}  "
              f"loop >= {r['loop_Hz']:8.0f} Hz")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m22_needles.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else str(o))


if __name__ == "__main__":
    main()

"""MOTE system budget v1: from an Iron Man content target to motes, heat, powers, laser class and steering load.

Content: S metres of strokes, luminance L (cd/m^2) on a w_s = 1 mm stroke width, redrawn at f Hz.
This is the same definition as E10/E10b. Flux Phi = 4 pi L w_s S. A mote tracing at speed v covers v/f metres of
stroke per frame and emits for a fraction `duty` of its path, so N = S f / (v duty).

Trap architectures (02_theory/T5):
* 'lateral2': two opposed heads with LG01 (doughnut) beams. The lateral force is the gradient force,
  eta = 0.75 a / w. Each beam's axial push is cancelled by the opposing head. Heat per unit force = 1/eta.
* 'push4': four tetrahedral heads with dimpled flat-top beams and active position feedback. Each beam pushes along
  its own axis (eta = 1). Summed beam force per unit net force: worst 3.0, mean 2.23; max single beam 1.22.
* 'push6': six heads on +-x, +-y, +-z. Summed force: worst sqrt(3), mean 1.5; max single beam 1.0.

Heat, force and speed are solved self-consistently. At the worst-case direction, T_mote <= T_max; the gas properties
follow the film temperature.

Emitters (the light each mote must make: phi_m = Phi / (N duty) while emitting):
* 'phosphor:<name>': Eu2+ nitride phosphor pumped by a violet/blue beam (pump_lam).
* 'uc:<name>': Yb/Er upconversion pumped at 980 nm.
* 'scatter': a visible beam scattered by a white mote (albedo, side-scatter factor g_side).
Pass-through pump or visible light reaching the walls is reported as 'wall_ratio' = wall lumens / image lumens.
"""
from __future__ import annotations

import math

import physics as ph
import safety as sf

CONTENT = {
    "accent": (3.0, 1.0),
    "sketch": (3.0, 5.0),
    "film_contrast": (4.0, 9.0),
    "film_density": (4.0, 30.0),
    "film_exact": (50.0, 30.0),
}
ARCH = {  # heads, eta (None = lateral formula), h_worst, h_mean, max single-beam share, beam-profile power factor
    "lateral2": dict(heads=2, eta=None, h_worst=1.0, h_mean=1.0, single=0.5, profile=math.e / 2),
    "push4": dict(heads=4, eta=1.0, h_worst=3.0, h_mean=2.23, single=1.22, profile=1.0),
    "push6": dict(heads=6, eta=1.0, h_worst=math.sqrt(3), h_mean=1.5, single=1.0, profile=1.0),
    # 'single': one head, BYU-type aberrated single-beam 3D trap, extrapolated from 125 mm to room throw at similar NA.
    # eta_single (default 0.5) is inferred, not measured: BYU's 1.83 m/s is reproducible below 700 K only if eta >~ 0.4
    # (validation M22). Required regime: mote radius >= 0.8 w (BYU: particle larger than the focal structure).
    "single": dict(heads=1, eta="single", h_worst=1.0, h_mean=1.0, single=1.0, profile=1.0),
}
# profile: P_beam = I_at_mote * pi w^2/2 * profile. LG01 ring peak is 2P/(pi w^2 e); the dimpled flat-top is taken as
# a Gaussian-equivalent peak (factor 1) plus FLATTOP_PENALTY below.
FLATTOP_PENALTY = 2.0


def waist(lam_nm, throw, R_head, M2=1.3):
    return M2 * lam_nm * 1e-9 * throw / (math.pi * R_head)


def intercept(a, w):
    return 1 - math.exp(-2 * a * a / (w * w))


def design(content="film_density", a=2.5e-6, kp=0.1, v=1.0, arch="push4", emitter="phosphor:cyan_BaSi2O2N2",
           lam_trap=1550, pump_lam=405, throw=1.5, R_head=0.05, T_max=450.0, u_air=0.3, f=30.0, duty=0.7,
           w_s=1e-3, C_ph=1.0, A_trap=0.9, rho_p=1500.0, albedo=0.8, g_side=0.5, scatter_lam=488,
           whitener_gain=1.0, field=1.0, M2=1.3, interlock_s=1e-4, eta_single=0.5, B_focus=None, R_ft=None, eta_shape=0.8):
    L, S = CONTENT[content] if isinstance(content, str) else content
    A = ARCH[arch]
    w_t = waist(lam_trap, throw, R_head, M2)
    # focus tracking: a beam's focus must follow the mote along the beam axis. A tracking loop of bandwidth B_focus
    # lags a ramp of speed v by v / (2 pi B_focus); keeping that lag <= z_R / 2 needs z_R = pi w^2 / lambda >=
    # v / (pi B_focus), which sets a minimum waist (T5 section 8)
    if B_focus:
        w_t = max(w_t, math.sqrt(v * lam_trap * 1e-9 / (math.pi ** 2 * B_focus)))
    if A["eta"] is None:
        eta = ph.eta_lateral(a, w_t)
    elif A["eta"] == "single":
        eta = eta_single
    else:
        eta = A["eta"]
    Phi = 4 * math.pi * L * w_s * S
    N = S * f / (v * duty)
    phi_m = Phi / (N * duty)
    out = dict(content=content, arch=arch, emitter=emitter, a_um=a * 1e6, kp=kp, v=v, w_trap_um=w_t * 1e6, eta=eta,
               N=N, Phi_lm=Phi, lm_per_mote=phi_m)

    # --- emitter: absorbed pump power and its heat (solved together with temperature) -----------------------
    kind, _, name = emitter.partition(":")
    lam_e_nm = pump_lam if kind == "phosphor" else (980 if kind == "uc" else scatter_lam)
    w_p = waist(lam_e_nm, throw, R_head, M2)
    if B_focus:
        w_p = max(w_p, math.sqrt(v * lam_e_nm * 1e-9 / (math.pi ** 2 * B_focus)))
    icp = intercept(a, w_p)

    def emitter_heat(Tm):
        if kind == "phosphor":
            p = ph.PHOSPHOR[name]
            lm_per_W_abs, _, _ = ph.phosphor_lumens(1.0, pump_lam, Tm, name)
            if lm_per_W_abs <= 0:
                return math.inf, math.inf, 0.0
            P_abs = phi_m / lm_per_W_abs
            P_beam = P_abs / (p["A_abs"] * icp)
            return P_abs * (1 - lm_per_W_abs / (683 * ph.band_V(p["lam_em"], p["fwhm"]))), P_beam, P_abs
        if kind == "uc":
            p = ph.UC[name]
            A_uc = ph.uc_absorptance(a, p["x_Yb"])
            P_abs = phi_m / 60.0
            for _ in range(60):   # fixed point: efficacy depends on the intensity the absorbed power implies
                I = P_abs / (A_uc * math.pi * a * a)
                lm, vis, qy = ph.uc_lumens(P_abs, I, Tm, name)
                eff = lm / P_abs if P_abs > 0 else 0.0
                if eff <= 1e-6:
                    return math.inf, math.inf, 0.0
                P_abs = 0.5 * P_abs + 0.5 * phi_m / eff
            I = P_abs / (A_uc * math.pi * a * a)
            _, vis, _ = ph.uc_lumens(P_abs, I, Tm, name)
            return P_abs - vis, P_abs / (A_uc * icp), P_abs
        if kind == "scatter":
            lm_per_W = 683 * ph.V(scatter_lam) * icp * albedo * g_side
            P_beam = phi_m / lm_per_W
            return P_beam * icp * (1 - albedo), P_beam, P_beam * icp * (1 - albedo)
        return 0.0, 0.0, 0.0

    # --- self-consistent trap force / heat / temperature at the worst-case direction ------------------------
    Tm = ph.T0 + 50
    for _ in range(80):
        Tf = 0.5 * (ph.T0 + Tm)
        F_need = ph.drag(a, v + u_air, Tf)
        P_abs_force = F_need / (eta * ph.force_per_absorbed_watt(a, kp, Tm, C_ph))
        heat_e, P_pump_beam, P_abs_pump = emitter_heat(Tm)
        P_heat = P_abs_force * A["h_worst"] + heat_e
        if not math.isfinite(P_heat):
            Tm_new = 6000.0
        else:
            Tm_new = ph.mote_temperature(P_heat, a, v_rel=v + u_air)
        if abs(Tm_new - Tm) < 0.01:
            Tm = Tm_new
            break
        Tm = 0.5 * Tm + 0.5 * Tm_new
    Tf = 0.5 * (ph.T0 + Tm)
    F_need = ph.drag(a, v + u_air, Tf)
    P_abs_force = F_need / (eta * ph.force_per_absorbed_watt(a, kp, Tm, C_ph))
    heat_e, P_pump_beam, P_abs_pump = emitter_heat(Tm)

    # --- beams ------------------------------------------------------------------------------------------------
    # intensity at the mote for the largest single-beam force share
    if arch == "lateral2":
        P_abs_beam = P_abs_force / 2                          # two opposed beams share the lateral force
    else:
        P_abs_beam = P_abs_force * A["single"]
    I_mote = P_abs_beam / (A_trap * math.pi * a * a)
    if arch == "lateral2":
        P_beam = max(I_mote * math.pi * w_t ** 2 / 2 * A["profile"], P_abs_beam / A_trap)
    elif arch == "single":
        P_beam = P_abs_beam / (A_trap * intercept(a, w_t))
    else:
        # push beams: flat-top of radius R_ft (M2b/M2c: R_ft ~ 15-20 um is needed for gust rejection when the
        # photophoretic force lags by tau_F ~ a^2/alpha_p). Default (R_ft=None): Gaussian-equivalent, P = I pi w^2.
        if R_ft:
            P_beam = max(I_mote * math.pi * max(R_ft, w_t) ** 2 / eta_shape, P_abs_beam / A_trap)
        else:
            P_beam = max(I_mote * math.pi * w_t ** 2 / 2 * FLATTOP_PENALTY, P_abs_beam / A_trap)
    trap_W_per_mote = (2 * P_beam if arch == "lateral2" else P_beam * A["h_mean"] / A["single"])
    P_trap_total = N * trap_W_per_mote
    P_head = P_trap_total / A["heads"]
    P_pump_total = N * P_pump_beam if math.isfinite(P_pump_beam) else math.inf
    ael_t = sf.ael_class1(lam_trap)
    head_lim_t = sf.head_power_limit(lam_trap, R_head)
    lam_e = pump_lam if kind == "phosphor" else (980 if kind == "uc" else scatter_lam)
    ael_p = sf.ael_class1(lam_e) if kind in ("phosphor", "uc", "scatter") else math.inf
    head_lim_p = sf.head_power_limit(lam_e, R_head) if kind in ("phosphor", "uc", "scatter") else math.inf

    # pass-through light that reaches the walls, relative to the image flux
    if kind in ("phosphor", "scatter"):
        # light reaching the walls: the part of the beam that misses the mote, plus forward diffraction (Babinet:
        # a mote much larger than the wavelength removes 2x its geometric cross-section; the extra 1x is diffracted
        # into a ~lambda/(2a) cone that lands on the walls), plus, for a phosphor, the unabsorbed intercepted pump
        x_size = 2 * math.pi * a / (lam_e * 1e-9)
        q_diff = min(1.0, (x_size / 4.0) ** 2)            # ~0 for small motes (Rayleigh), -> 1 for x >> 1
        if kind == "phosphor":
            A_em = ph.PHOSPHOR[name]["A_abs"]
            wall_W = P_pump_total * ((1 - icp) + icp * q_diff + icp * (1 - A_em) * 0.5)
        else:
            wall_W = P_pump_total * ((1 - icp) + icp * q_diff + icp * albedo * (1 - g_side))
        wall_lm = 683 * ph.V(lam_e) * wall_W * whitener_gain
        wall_ratio = wall_lm / Phi
    else:
        wall_ratio = 0.0

    # steering load: every head addresses every mote; continuous tracking with steps <= w/3
    channels = N * A["heads"]
    spot_rate = channels * 3 * v / w_t
    n_axis = field / (2 * w_t)

    fails = []
    if arch == "single" and a < 0.8 * w_t:
        fails.append("single_regime")
    if Tm > T_max:
        fails.append("heat")
    if P_beam > ael_t:
        fails.append("trap_beam_class")
    if P_head > head_lim_t:
        fails.append("trap_exit_class")
    if kind in ("phosphor", "uc", "scatter"):
        if not math.isfinite(P_pump_beam) or P_pump_beam > ael_p:
            fails.append("emitter_beam_class")
        if P_pump_total / A["heads"] > head_lim_p:
            fails.append("emitter_exit_class")
        if wall_ratio > 0.05:
            fails.append("wall_light")
    out.update(Tm=Tm, dT=Tm - ph.T0, F_need=F_need, P_abs_force=P_abs_force, I_mote_Wcm2=I_mote / 1e4,
               P_beam_mW=P_beam * 1e3, ael_trap_mW=ael_t * 1e3, P_trap_total_W=P_trap_total, P_head_W=P_head,
               head_limit_W=head_lim_t, P_pump_beam_uW=P_pump_beam * 1e6, ael_pump_uW=ael_p * 1e6,
               P_pump_total_mW=P_pump_total * 1e3, P_abs_pump_uW=P_abs_pump * 1e6, wall_ratio=wall_ratio,
               channels=channels, spot_rate=spot_rate, n_axis=n_axis, w_pump_um=w_p * 1e6, icp=icp,
               interlock_dose_Jcm2=sf.interlock_dose(P_beam, w_t, interlock_s) / 1e4,
               lm_per_W_total=Phi / max(P_trap_total + (P_pump_total if math.isfinite(P_pump_total) else 0), 1e-12),
               fails=fails, feasible=not fails)
    return out


def best_speed(v_grid=None, **kw):
    """Fastest feasible trace speed (fewest motes) for a design; returns the design dict (or the slowest failing one)."""
    v_grid = v_grid or [0.05 * 1.15 ** k for k in range(40)]
    best = None
    for v in v_grid:
        d = design(v=v, **kw)
        if d["feasible"]:
            best = d
    return best if best is not None else design(v=v_grid[0], **kw)


def max_speed_heat(a, kp, arch="push4", T_max=450.0, u_air=0.0, **kw):
    """Largest v for which the mote stays below T_max (trap heat only; no emitter)."""
    lo, hi = 0.0, 50.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        d = design(a=a, kp=kp, v=max(mid, 1e-4), arch=arch, emitter="none", T_max=T_max, u_air=u_air, **kw)
        if d["Tm"] <= T_max:
            lo = mid
        else:
            hi = mid
    return lo

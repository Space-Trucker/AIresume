"""Feedback-stabilised multi-beam photophoretic push trap (architecture 'push4' / 'push6'), time-domain.

Model:
* Each head i sends a beam along d_i. The beam has a flat-top profile f(rho) = exp(-2 (rho/R)^8): flat inside,
  steep edges, no dimple. With no passive lateral restoring force, the edges push the mote OUT of the beam. This is
  the conservative case.
* Force from beam i on the mote: F_i = k_I I_i f(rho_i) d_i - (3/8) a k_I I_i grad_perp f(rho_i), with k_I = F per unit
  intensity at the design temperature. The lateral term points toward lower intensity.
* Mote: linear drag with inertia, integrated exactly over each step:
  v <- v_eq + (v - v_eq) exp(-dt/tau_p), v_eq = u_air + F/c, c = 6 pi mu a / Cc.
* Air: steady draft plus 3D Ornstein-Uhlenbeck gusts (sigma, correlation time).
* Beam pointing: analog feed-forward along the planned path p_ref(t), plus a correction delta. The correction is
  updated at f_loop from the measured mote position and slewed with pointing time constant tau_steer.
* Measurement: each loop period gives the mote position (e.g. back-scatter of each beam on a quadrant detector)
  with Gaussian noise sigma_m and one period of latency.
* Force control at f_loop: F_des = c [v_ref + w_c e + w_i int e]; e = p_ref - p_meas; w_c = 2 pi f_loop / 10.
  The demand is split over the beams by the minimum-sum non-negative allocation, each beam capped at F_beam_max
  (heat / Class 1 cap).
* The mote is lost when it sits outside the flat-top (rho > R + a) of more than one beam: it can no longer be pushed
  in all directions.
"""
from __future__ import annotations

import math

import numpy as np

import physics as ph

TETRA = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]) / math.sqrt(3)
OCTA = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)


def allocate(Fvec, D):
    """Minimum-sum non-negative beam forces with sum f_i d_i = Fvec (exact for TETRA and OCTA)."""
    if len(D) == 4:
        p = D @ Fvec
        return 0.75 * (p - p.min())
    f = np.zeros(len(D))
    for k in range(3):
        if Fvec[k] >= 0:
            f[2 * k] = Fvec[k]
        else:
            f[2 * k + 1] = -Fvec[k]
    return f


def flat(rho, R):
    x = (rho / R) ** 8
    return math.exp(-2 * x), -16 * x / rho * math.exp(-2 * x) if rho > 0 else 0.0


def run(a=1e-6, rho_p=1500.0, kp=0.02, heads="tetra", R_ft=10e-6, speed=1.0, radius=0.05, T_sim=0.3,
        f_loop=20e3, tau_steer=None, sigma_m=0.5e-6, draft=(0.1, 0.0, 0.0), gust_sigma=0.1, gust_tau=0.3,
        F_cap_factor=1.5, u_design=0.3, Tm=400.0, n_motes=16, seed=0, dt=None, trace=False, dob=False, dob_tau=2.0, force_lag=True, rhoc_p=1.5e6, beta_F=0.2, w_c_cap=True):
    """Integrate n_motes independent motes (independent gusts and sensor noise) in parallel."""
    rng = np.random.default_rng(seed)
    D = TETRA if heads == "tetra" else OCTA
    nb = len(D)
    M = n_motes
    Tf = 0.5 * (ph.T0 + Tm)
    c = 6 * math.pi * ph.mu_air(Tf) * a / ph.cunningham(a, Tf)
    m = 4 / 3 * math.pi * a ** 3 * rho_p
    tau_p = m / c
    k_I = ph.photophoretic_force(a, 1.0, kp, J1=0.5, Tm=Tm)       # N per W/m^2 (opaque mote)
    F_nom = ph.drag(a, speed + u_design, Tf)
    F_beam_max = F_cap_factor * F_nom
    T_loop = 1.0 / f_loop
    tau_steer = tau_steer if tau_steer is not None else 2 * T_loop
    dt = dt or min(T_loop / 4, tau_p / 2, R_ft / (5 * max(speed, 0.05)))
    n = int(T_sim / dt)
    steps_per_loop = max(1, int(round(T_loop / dt)))
    w_c = 2 * math.pi * f_loop / 10
    w_i = w_c / 10
    om = speed / radius
    decay = math.exp(-dt / tau_p)
    # the photophoretic force needs the mote's internal temperature dipole to form: a first-order lag with
    # tau_F = beta_F a^2 / alpha_p (alpha_p = k_p / (rho c)_p; beta_F ~ 0.2 because the lit surface layer forms first)
    tau_F = beta_F * a * a / (kp / rhoc_p) if force_lag else 0.0
    lagF = 1 - math.exp(-dt / tau_F) if tau_F > 0 else 1.0
    f_eff = None
    if tau_F > 0 and w_c_cap:
        w_c = min(w_c, 1.0 / (4 * tau_F))           # keep the loop well inside the force-lag pole
        w_i = w_c / 10
    slew = 1 - math.exp(-dt / tau_steer)
    draft = np.asarray(draft, float)

    def ref(t):
        return np.array([radius * math.cos(om * t), radius * math.sin(om * t), 0.0]), \
            np.array([-speed * math.sin(om * t), speed * math.cos(om * t), 0.0])

    p0, v0 = ref(0.0)
    x = np.tile(p0, (M, 1))
    v = np.tile(v0, (M, 1))
    gust = np.zeros((M, 3))
    delta = np.zeros((M, 3))
    delta_cmd = np.zeros((M, 3))
    e_int = np.tile(-draft / w_i, (M, 1))          # steady draft already learned (swarm-wide estimate)
    F_fb = c * w_i * e_int
    pending = None                                   # measurement taken last loop (one-period latency)
    prev_meas = None                                 # for the disturbance observer
    u_est = np.tile(draft, (M, 1))
    F_applied_acc = np.zeros((M, 3))
    n_acc = 0
    F_avg_prev = None                                # mean applied force over [t_(k-2), t_(k-1)]
    alive = np.ones(M, bool)
    t_lost = np.full(M, np.nan)
    max_err = np.zeros(M)
    sq_err = np.zeros(M)
    max_rho = np.zeros(M)
    sq_rho = np.zeros(M)
    n_rho = 0
    grav = np.array([0.0, 0.0, -m * ph.G])
    tr = []
    for k in range(n):
        t = k * dt
        p_ref, v_ref = ref(t)
        if k % steps_per_loop == 0:
            meas = (x + sigma_m * rng.standard_normal((M, 3)), p_ref.copy())
            if pending is not None:
                e = pending[1] - pending[0]              # deviation from the plan at the measurement time
                if dob:
                    # disturbance observer: air velocity = measured mote velocity - (applied force)/c over the same
                    # period [t_(k-2), t_(k-1)], low-passed with time constant 2T
                    if prev_meas is not None and F_avg_prev is not None:
                        u_raw = (pending[0] - prev_meas) / T_loop - F_avg_prev / c
                        u_est += (u_raw - u_est) * (1 - math.exp(-1.0 / dob_tau))
                    prev_meas = pending[0]
                    F_fb = c * (w_c * e - u_est)
                else:
                    e_int += e * T_loop
                    F_fb = c * (w_c * e + w_i * e_int)
                delta_cmd = -e                           # re-centre the beams on the mote (relative to the plan)
            pending = meas
            if dob:
                F_avg_prev = F_applied_acc / n_acc if n_acc else None
                F_applied_acc = np.zeros((M, 3))
                n_acc = 0
        delta += (delta_cmd - delta) * slew
        centre = p_ref + delta
        Fd = c * v_ref + F_fb                                        # (M,3) force demand
        P = Fd @ D.T                                                 # (M,nb)
        if nb == 4:
            f = 0.75 * (P - P.min(axis=1, keepdims=True))
        else:
            f = np.concatenate([np.clip(Fd, 0, None)[:, :, None], np.clip(-Fd, 0, None)[:, :, None]], 2).reshape(M, 6)
        scale = np.minimum(1.0, F_beam_max / np.maximum(f.max(axis=1), 1e-30))
        f *= scale[:, None]
        sat = scale < 1.0
        if f_eff is None:
            f_eff = f.copy()
        f_eff += (f - f_eff) * lagF
        f = f_eff
        r = x - centre
        F = np.tile(grav, (M, 1))
        F_beams_start = F.copy()
        n_out = np.zeros(M, int)
        for i in range(nb):
            along = r @ D[i]
            r_perp = r - along[:, None] * D[i]
            rho = np.linalg.norm(r_perp, axis=1)
            xx = (rho / R_ft) ** 8
            fv = np.exp(-2 * xx)
            dfv = np.where(rho > 0, -16 * xx / np.maximum(rho, 1e-30) * fv, 0.0)
            F += (f[:, i] * fv)[:, None] * D[i]
            F += (-(3 / 8) * a * f[:, i] * dfv / np.maximum(rho, 1e-30))[:, None] * r_perp
            n_out += rho > R_ft + a
            max_rho = np.maximum(max_rho, np.where(alive, rho, 0))
            sq_rho += np.where(alive, rho ** 2, 0)
        if dob:
            F_applied_acc += F - F_beams_start
            n_acc += 1
        n_rho += nb
        gust += -gust / gust_tau * dt + gust_sigma * math.sqrt(2 * dt / gust_tau) * rng.standard_normal((M, 3))
        v_eq = draft + gust + F / c
        v = v_eq + (v - v_eq) * decay
        x = x + v * dt
        p_next, _ = ref(t + dt)
        err = np.linalg.norm(x - p_next, axis=1)
        max_err = np.where(alive, np.maximum(max_err, err), max_err)
        sq_err += np.where(alive, err ** 2, 0)
        if trace:
            tr.append((t, float(np.linalg.norm(x[0] - p_next)), float(np.linalg.norm(delta[0])), bool(sat[0]), int(n_out[0]), float(np.linalg.norm(gust[0])), float(np.linalg.norm(delta_cmd[0])), (x[0] - p_next).tolist(), delta[0].tolist()))
        newly = alive & (n_out >= 2)
        t_lost[newly] = t
        alive &= ~newly
        if not alive.any():
            break
    lost = ~alive
    sig = float(np.sqrt(sq_rho.sum() / max(1, n_rho) / M / 2))   # per-axis rms of the mote-to-beam offset
    # Rice-type extrapolation: independent offset samples at ~ w_c / (2 pi) per second, Rayleigh tail beyond R_ft + a
    nu = w_c / (2 * math.pi)
    rate_extrap = nu * math.exp(-((R_ft + a) ** 2) / (2 * sig * sig)) if sig > 0 else 0.0
    return dict(trace=tr, sigma_rho_um=sig * 1e6, loss_rate_extrap_per_min=rate_extrap * 60,n=M, lost_frac=float(lost.mean()), t_lost=t_lost, T_sim=T_sim,
                loss_per_min=float(lost.mean()) / T_sim * 60, rms_err_um=float(np.sqrt(sq_err.sum() / max(1, n) / M)) * 1e6,
                max_err_um=float(np.median(max_err)) * 1e6, max_rho_um=float(np.median(max_rho)) * 1e6,
                tau_p_us=tau_p * 1e6, tau_F_us=tau_F * 1e6, dt_us=dt * 1e6, F_nom=F_nom)

"""MOTE dynamics: a mote held in a moving photophoretic trap, in turbulent room air.

Trap force (radial, toward the trap centre): F(r) = -F_max * u * exp((1 - u^2)/2), u = r / w,
peaking at r = w with value F_max (a smooth potential well with capture radius ~3w).
F_max = eta_trap * F_ph(I_peak), where F_ph is the continuum photophoretic force (physics.py) and eta_trap
is the fraction of the photophoretic force a trap geometry turns into restoring force (calibrated on
published optical-trap-display data; see validation).
Air: mean draft + Ornstein-Uhlenbeck gusts (sigma, correlation time), optional hand-wake pulses.
The mote is 'lost' if it ever leaves 3w from the trap centre.
"""
from __future__ import annotations

import math

import numpy as np

from physics import G, T0, drag, mu_air, photophoretic_force, rho_air


def trap_Fmax(a, P_beam, w, kp, J1=0.5, eta_trap=0.3, Tm=T0, C_ph=1.0):
    I_peak = 2 * P_beam / (math.pi * w * w)
    return eta_trap * photophoretic_force(a, I_peak, kp, J1=J1, Tm=Tm, C_ph=C_ph)


def path_positions(points, speed, dt, loops=1):
    """Trap trajectory along a closed polyline at constant speed; returns (N,3) positions and velocities."""
    P = np.asarray(points, float)
    P = np.vstack([P, P[:1]])
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    L = s[-1]
    t_end = loops * L / speed
    ts = np.arange(0, t_end, dt)
    sp = (ts * speed) % L
    X = np.stack([np.interp(sp, s, P[:, i]) for i in range(3)], 1)
    Vv = np.gradient(X, dt, axis=0)
    return ts, X, Vv


def simulate(points, speed, a, rho_p, P_beam, w, kp, draft=(0.1, 0.0, 0.0), gust_sigma=0.1, gust_tau=0.3,
             eta_trap=0.3, Tm=T0, loops=3, seed=0, hand_wake=None, dt=None):
    """Integrate the mote; returns dict(lost, t_lost, max_lag/w, rms_lag, Fmax_over_weight)."""
    rng = np.random.default_rng(seed)
    m = 4 / 3 * math.pi * a ** 3 * rho_p
    tau_p = m / (6 * math.pi * mu_air(T0) * a)
    dt = dt or min(tau_p / 5, 2e-5)
    ts, X, _ = path_positions(points, speed, dt, loops)
    Fmax = trap_Fmax(a, P_beam, w, kp, eta_trap=eta_trap, Tm=Tm)
    x = X[0].copy()
    v = np.zeros(3)
    gust = np.zeros(3)
    lags = []
    Tf = 0.5 * (T0 + Tm)
    for k in range(1, len(ts)):
        # Ornstein-Uhlenbeck gust
        gust += (-gust / gust_tau) * dt + gust_sigma * math.sqrt(2 * dt / gust_tau) * rng.standard_normal(3)
        u_air = np.array(draft, float) + gust
        if hand_wake is not None:
            t0, dur, amp, direction = hand_wake
            if t0 <= ts[k] <= t0 + dur:
                u_air = u_air + amp * np.asarray(direction, float)
        d = x - X[k]
        r = float(np.linalg.norm(d))
        if r > 3 * w:
            return dict(lost=True, t_lost=float(ts[k]), max_lag_over_w=r / w, rms_lag_over_w=float(np.sqrt(np.mean(np.square(lags)))) if lags else 0.0,
                        Fmax_over_weight=Fmax / (m * G))
        uu = r / w
        Ftrap = -Fmax * uu * math.exp((1 - uu * uu) / 2) * (d / r) if r > 0 else np.zeros(3)
        rel = v - u_air
        sp = float(np.linalg.norm(rel))
        Fd = -drag(a, sp, Tf) * (rel / sp) if sp > 0 else np.zeros(3)
        Fg = np.array([0.0, 0.0, -m * G])
        # semi-implicit (drag is stiff for small motes): treat linear Stokes part implicitly
        c = 6 * math.pi * mu_air(Tf) * a
        v = (v + dt / m * (Ftrap + Fg + (Fd + c * rel)) + dt / m * c * u_air) / (1 + dt * c / m)
        x = x + v * dt
        lags.append(r / w)
    lags = np.array(lags)
    return dict(lost=False, t_lost=None, max_lag_over_w=float(lags.max()), rms_lag_over_w=float(np.sqrt(np.mean(lags ** 2))),
                Fmax_over_weight=Fmax / (m * G))


def loss_rate(points, speed, a, rho_p, P_beam, w, kp, n=12, seconds=None, **kw):
    """Monte-Carlo mote loss fraction over the simulated loops, and mean max lag."""
    lost = 0
    lag = []
    for s in range(n):
        r = simulate(points, speed, a, rho_p, P_beam, w, kp, seed=s, **kw)
        lost += r["lost"]
        lag.append(r["max_lag_over_w"])
    return lost / n, float(np.median(lag))

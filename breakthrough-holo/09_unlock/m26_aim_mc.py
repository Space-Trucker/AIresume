"""M26: a Monte Carlo of the gated-flash aim (RT9 C3 vs idea round 5 §3.1).

The question. A falling mote is tracked at f_cam with position noise sig_pos. Its velocity is fitted over the last
N frames, and a visible spot is fired at the predicted position tau later. Does the spot land within r_aim of the
mote?
- RT9 used an inertial-range (Lagrangian structure-function) wander and found 15-39 % hits in a hand wake.
- Round 5 argued that tau (3-5 ms) is far below the Kolmogorov time, where the velocity is smooth, and found
  57-88 % at r_aim 40 um and 92-99.8 % at 70 um.

Model [DERIVED]. Sawford's (1991) second-order Lagrangian stochastic model gives each lateral velocity component
both time scales: smooth below tau_eta, decorrelating at T_L.
- da = -(1/tau_eta + 1/T_L) a dt - u/(tau_eta T_L) dt + sqrt(2 sigma^2 (1/tau_eta + 1/T_L)/(tau_eta T_L)) dW
- du = a dt, dx = u dt
- with eps = C_eps sigma^3/L, tau_eta = sqrt(nu/eps), T_L = 2 sigma^2/(C0 eps), C0 = 6.

Regimes (lateral sigma, integral scale L):
- column core at Tu 1 % / 10 % of U = 0.25 m/s, L 0.1 m;
- a gloved-hand wake (sigma 30 mm/s, L 5 cm);
- a bare-hand wake (60 mm/s, 5 cm).

Tracking. Positions are sampled at f_cam with Gaussian noise. Velocity is the least-squares slope over N frames, and
the prediction is x_last + v_fit (tau + (N-1)/(2 f_cam) offset handled exactly). A hit means the 2D lateral error is
below r_aim.

Run: python3 m26_aim_mc.py -> results/m26_run.log, results/m26_aim_mc.json
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NU = 1.5e-5
C0, CEPS = 6.0, 0.5
REGIMES = {  # sigma (m/s, per lateral component), L (m)
    "core Tu 1 %": (0.0025, 0.10),
    "core Tu 10 %": (0.025, 0.10),
    "gloved-hand wake": (0.030, 0.05),
    "bare-hand wake": (0.060, 0.05),
    "near wake (stress)": (0.080, 0.02),
    "near wake (extreme)": (0.100, 0.01),
}


def sawford(n, dt, steps, sigma, L, rng):
    eps = CEPS * sigma ** 3 / L
    te = math.sqrt(NU / eps)
    TL = 2 * sigma ** 2 / (C0 * eps)
    a1 = 1 / te + 1 / TL
    a0 = 1 / (te * TL)
    q = math.sqrt(2 * sigma ** 2 * a1 * a0 * dt)
    # stationary start: E[u a] = 0, var(u) = sigma^2, var(a) = sigma^2 / (tau_eta T_L) (Lyapunov equation)
    u = rng.normal(0, sigma, n)
    a = rng.normal(0, sigma * math.sqrt(a0), n)
    x = np.zeros((steps, n))
    for k in range(steps):
        a += (-a1 * a - a0 * u) * dt + q * rng.normal(size=n)
        u += a * dt
        x[k] = (x[k - 1] if k else 0.0) + u * dt
    return x, te, TL, u.std()


def run(regime, f_cam=1000.0, sig_pos=5e-6, N=5, tau=4e-3, r_aims=(40e-6, 70e-6), n=4000, seed=0):
    sigma, L = REGIMES[regime]
    dt = 1e-5
    rng = np.random.default_rng(seed)
    t_hist = (N - 1) / f_cam
    steps = int(round((t_hist + tau) / dt)) + 1
    errs2 = np.zeros(n)
    for comp in range(2):
        x, te, TL, su = sawford(n, dt, steps, sigma, L, rng)
        idx = [int(round(k / f_cam / dt)) for k in range(N)]
        ts = np.array([k / f_cam for k in range(N)])
        meas = x[idx] + rng.normal(0, sig_pos, (N, n))
        A = np.vstack([ts, np.ones(N)]).T
        coef, *_ = np.linalg.lstsq(A, meas, rcond=None)
        slope, icpt = coef
        t_fire = t_hist + tau
        pred = icpt + slope * t_fire
        true = x[steps - 1]
        errs2 += (pred - true) ** 2
    err = np.sqrt(errs2)
    return dict(regime=regime, f_cam=f_cam, sig_pos_um=sig_pos * 1e6, N=N, tau_ms=tau * 1e3, tau_eta_ms=te * 1e3,
                T_L_ms=TL * 1e3, err_p50_um=float(np.median(err) * 1e6), err_p90_um=float(np.percentile(err, 90) * 1e6),
                hits={f"{r * 1e6:.0f}": float(np.mean(err < r)) for r in r_aims})


def main():
    rows = []
    # self-check: the stationary variance is preserved over 10 T_eta (bare-hand wake)
    rng = np.random.default_rng(9)
    _, te, TL, su = sawford(20000, 1e-4, int(0.5 / 1e-4), REGIMES["bare-hand wake"][0], REGIMES["bare-hand wake"][1], rng)
    print(f"self-check: bare-hand wake sigma {REGIMES['bare-hand wake'][0]:.3f} -> simulated {su:.4f} m/s after 0.5 s "
          f"(tau_eta {te * 1e3:.0f} ms, T_L {TL * 1e3:.0f} ms)")
    print(f"{'regime':17s} {'f_cam':>6s} {'sig':>4s} {'N':>2s} {'tau':>4s} {'tau_eta':>7s} {'T_L':>6s} "
          f"{'err p50/p90 um':>15s} {'hit 40um':>8s} {'hit 70um':>8s}")
    for regime in REGIMES:
        for f_cam, sig, N, tau in ((1000.0, 5e-6, 5, 4e-3), (1000.0, 10e-6, 5, 4e-3), (1000.0, 5e-6, 5, 2e-3),
                                   (2000.0, 5e-6, 8, 2e-3), (500.0, 5e-6, 4, 6e-3), (1000.0, 5e-6, 10, 4e-3)):
            r = run(regime, f_cam, sig, N, tau, seed=hash((regime, f_cam, sig, N, tau)) % 10000)
            rows.append(r)
            print(f"{regime:17s} {f_cam:6.0f} {sig * 1e6:4.0f} {N:2d} {tau * 1e3:4.1f} {r['tau_eta_ms']:7.1f} "
                  f"{r['T_L_ms']:6.0f} {r['err_p50_um']:6.1f}/{r['err_p90_um']:<7.1f} {r['hits']['40']:8.3f} "
                  f"{r['hits']['70']:8.3f}", flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m26_aim_mc.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()

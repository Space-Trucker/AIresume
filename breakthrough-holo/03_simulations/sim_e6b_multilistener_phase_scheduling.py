"""E6b: 'Acoustic phase scheduling': choose every spark's firing time so the plasma display is
quiet at SEVERAL tracked listeners at once.

Setup: a static frame of N voxels repeats every 1/60 s, so the far-field pressure at listener j
is periodic and its audible content lives only at the harmonics f_n = 60 n Hz (n = 1..333):
    g_jn = sum_k a_kj exp(-i w_n (t_k + r_kj/c)),   a_kj = 1/r_kj
Audible power at j ~ sum_n W(f_n) |g_jn|^2, with W = (N-wave spectrum ~ f^2) x A-weighting.
A random schedule gives E|g_jn|^2 = sum_k a_kj^2 (Campbell): that is the incoherent baseline.
Free variables: firing phases t_k in [0, 1/60) (circular), about 10^4 of them, against 333
complex constraints per listener. Minimised with L-BFGS using the analytic gradient.
We report the dB(A) change vs random at the tracked listeners AND at untracked positions.
"""
import math
import time

import numpy as np
from scipy.optimize import minimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import C_SOUND, RESULTS, save_json
from display_budget import A_WEIGHT_TABLE
from sim_e6_acoustic_scheduling import armor_wireframe

rng = np.random.default_rng(11)
FRAME_HZ = 60.0
harm = np.arange(1, 334)
f = harm * FRAME_HZ
w_ang = 2 * np.pi * f
# A-weighting interpolated in log-f, times N-wave low-frequency spectrum ~ f^2
aw_f = np.array(list(A_WEIGHT_TABLE.keys()), dtype=float)
aw_db = np.array(list(A_WEIGHT_TABLE.values()))
lowf = np.array([20, 50, 100, 200, 500]); lowdb = np.array([-50.5, -30.2, -19.1, -10.9, -3.2])
allf = np.concatenate([lowf, aw_f]); alldb = np.concatenate([lowdb, aw_db])
A_db = np.interp(np.log10(f), np.log10(allf), alldb)
W = (f / 1e4) ** 2 * 10 ** (A_db / 10)
W = W / W.sum()


def setup(n_listeners, spacing=2e-3):
    strokes = armor_wireframe(spacing)
    pts = np.concatenate(strokes)
    c0 = pts.mean(0)
    # tracked listeners: heads around the hologram at 0.8-1.6 m, ear height ~1.6 m
    ang = np.linspace(0, 2 * np.pi, n_listeners, endpoint=False) + 0.3
    rad = rng.uniform(0.8, 1.6, n_listeners)
    L = np.stack([c0[0] + rad * np.cos(ang), c0[1] + rad * np.sin(ang), np.full(n_listeners, 1.6)], 1)
    # untracked test positions: 24 random points in a 5x5 m room, 1.0-1.8 m high, >0.6 m away
    U = []
    while len(U) < 24:
        p = np.array([rng.uniform(-2.5, 2.5), rng.uniform(-2.5, 2.5), rng.uniform(1.0, 1.8)]) + np.array([c0[0], c0[1], 0])
        if np.linalg.norm(p[:2] - c0[:2]) > 0.6:
            U.append(p)
    return pts, L, np.array(U)


def amps_delays(pts, Ls):
    r = np.linalg.norm(pts[None, :, :] - Ls[:, None, :], axis=2)     # (M, N)
    return 1.0 / r, r / C_SOUND


def objective(t, a, d):
    M = a.shape[0]
    J = 0.0
    grad = np.zeros_like(t)
    for j in range(M):
        ph = np.exp(-1j * np.outer(w_ang, t + d[j]))                 # (F, N)
        E = ph * a[j][None, :]
        g = E.sum(1)                                                  # (F,)
        base = np.sum(a[j] ** 2)
        J += np.sum(W * np.abs(g) ** 2) / base
        grad += (2 * np.real((np.conj(g) * W * (-1j * w_ang))[:, None] * E).sum(0)) / base
    return J / M, grad / M


def band_level(t, a, d):
    """dB(A) change vs random baseline for each listener (rows of a, d)."""
    out = []
    for j in range(a.shape[0]):
        g = (np.exp(-1j * np.outer(w_ang, t + d[j])) * a[j][None, :]).sum(1)
        out.append(10 * math.log10(np.sum(W * np.abs(g) ** 2) / np.sum(a[j] ** 2) / np.sum(W)))
    return np.array(out)


def run_case(M, iters=300):
    pts, L, U = setup(M)
    N = len(pts)
    aL, dL = amps_delays(pts, L)
    aU, dU = amps_delays(pts, U)
    t0 = rng.uniform(0, 1 / FRAME_HZ, N)
    before_L = band_level(t0, aL, dL)
    before_U = band_level(t0, aU, dU)
    tic = time.time()
    r = minimize(objective, t0, args=(aL, dL), jac=True, method="L-BFGS-B",
                 options=dict(maxiter=iters, maxfun=iters * 2))
    t = np.mod(r.x, 1 / FRAME_HZ)
    after_L = band_level(t, aL, dL)
    after_U = band_level(t, aU, dU)
    # minimum spacing between pulses (ns) to check the laser can actually fire this schedule
    ts = np.sort(t)
    min_gap = np.min(np.diff(ts)) * 1e9
    return dict(M=M, N=N, secs=time.time() - tic, iters=int(r.nit),
                tracked_before=before_L.tolist(), tracked_after=after_L.tolist(),
                untracked_before=before_U.tolist(), untracked_after=after_U.tolist(),
                min_pulse_gap_ns=float(min_gap), mean_gap_ns=float(1e9 / (N * FRAME_HZ)))


if __name__ == "__main__":
    print("E6b multi-listener acoustic phase scheduling")
    results = []
    for M in (1, 2, 4, 8):
        res = run_case(M)
        results.append(res)
        print(f"  M={M}: N={res['N']} voxels, {res['iters']} iters, {res['secs']:.0f}s | tracked dB change: "
              f"before {np.mean(res['tracked_before']):+.1f}, after mean {np.mean(res['tracked_after']):+.1f} "
              f"(worst {np.max(res['tracked_after']):+.1f}) | untracked after mean {np.mean(res['untracked_after']):+.1f} "
              f"(worst {np.max(res['untracked_after']):+.1f}) | min pulse gap {res['min_pulse_gap_ns']:.1f} ns")
    save_json("e6b_multilistener.json", results)
    fig, ax = plt.subplots(figsize=(7, 4))
    Ms = [r["M"] for r in results]
    ax.plot(Ms, [np.mean(r["tracked_after"]) for r in results], "o-", label="tracked listeners (mean)")
    ax.plot(Ms, [np.max(r["tracked_after"]) for r in results], "o--", label="tracked listeners (worst)")
    ax.plot(Ms, [np.mean(r["untracked_after"]) for r in results], "s-", label="untracked room points (mean)")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("number of tracked listeners optimised at once")
    ax.set_ylabel("audible noise vs random order (dB)")
    ax.set_title("Acoustic phase scheduling: firing-time optimisation")
    ax.legend(fontsize=8)
    plt.tight_layout(); plt.savefig(f"{RESULTS}/e6b_multilistener.png", dpi=120); plt.close()
    print("  saved results/e6b_multilistener.json/.png")

"""M9: touch. A hand sweeps through a MOTE hologram; what happens to the image?

Scene: the procedural Iron Man armor at sketch density (5 m of strokes), scaled into the 1 x 1 x 0.8 m image volume.
Motes are spaced v/f along the chained tour (mote_plan), and the design is the M8 'L3' sketch push design
(v = 0.64 m/s, 45 Hz, relative-speed budget 0.69 m/s with a 1.3 force margin).

Hand: a sphere of radius 4.5 cm crossing the image at speed U.
* Air: potential flow around a moving sphere,
  u = U R^3/(2 r^3) [3 (U_hat . r_hat) r_hat - U_hat],
  plus a crude turbulent wake: a cylinder of radius R behind the hand, axial speed 0.5 U exp(-s/3R), s up to 8R.
* Mote: the beams track the mote (closed loop), so the air cannot strip it from its beams. The trap can supply relative
  speed up to v_rel_max = 0.69 m/s against the air:
  - if the air plus the planned trace exceeds that, the mote is carried along and lags its plan;
  - after the hand passes, the mote returns to its plan at the spare speed.
* Lost: a mote inside the hand sphere (contact; it sticks to the glove).
* Option 'avoid': the workload manager tracks the hand and predicts it 150 ms ahead. Motes inside a 'danger tube' (within
  R + 1.5 cm of the hand's path, ahead of the hand, inside the horizon) are pushed sideways, out of the tube, at the
  full relative-speed budget. The image parts around the hand like smoke, then reforms.
Reports: motes displaced > 2 mm from their stroke (visible distortion at 1-2 m), maximum displacement, contact losses,
and time until every surviving mote is back on its stroke (< 1 mm). Writes results/m9_touch.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "04_engineering", "holo_engine"))
import content as c  # noqa: E402
from mote_plan import chain  # noqa: E402

V, F, VREL, RH = 0.64, 45.0, 0.69, 0.045


def tour_points():
    full = c.procedural_armor(height=1.8, slice_step=0.06)
    strokes, _ = c.fit_to_budget(full, 5.0)
    order, _ = chain(strokes)
    P = np.vstack([np.asarray(s, float) for s in order])
    P = P - P.mean(0)
    P *= 0.8 / np.ptp(P[:, 2])                                   # fit 0.8 m tall
    seg = np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    return P, s


def interp(P, s, q):
    q = q % s[-1]
    Pc = np.vstack([P, P[:1]])
    return np.stack([np.interp(q, s, Pc[:, i]) for i in range(3)], -1)


def air(x, hc, U, Uhat):
    r = x - hc
    rn = np.linalg.norm(r, axis=-1, keepdims=True)
    rn = np.maximum(rn, 1e-6)
    rh = r / rn
    pot = U * RH ** 3 / (2 * rn ** 3) * (3 * (rh @ Uhat)[..., None] * rh - Uhat)
    pot = np.where(rn > RH, pot, 0.0)
    s_back = -(r @ Uhat)                                          # distance behind the hand centre
    radial = np.linalg.norm(r - (r @ Uhat)[..., None] * Uhat, axis=-1)
    wake = np.where((s_back > 0) & (s_back < 8 * RH) & (radial < RH), 0.5 * U * np.exp(-s_back / (3 * RH)), 0.0)
    return pot + wake[..., None] * Uhat


def run(U, avoid=False, dt=1e-3):
    P, s = tour_points()
    L = s[-1]
    N = int(round(L * F / V))
    q0 = np.arange(N) * (L / N)
    Uhat = np.array([1.0, 0.0, 0.0])
    start = np.array([-0.7, 0.0, 0.1])                           # hand crosses at chest height of the armour
    T_cross = 1.4 / U
    q = q0.copy()                                                # each mote's progress along the tour
    x = interp(P, s, q)
    lost = np.zeros(N, bool)
    parked = np.zeros(N, bool)
    lag = np.zeros(N)
    disp_max = np.zeros(N)
    t, t_end = 0.0, T_cross + 1.0
    reform_t = None
    while t < t_end:
        hc = start + Uhat * U * min(t, T_cross) if t <= T_cross else start + Uhat * U * T_cross + np.array([0, 0, 1.0])
        target = interp(P, s, q0 + V * t)
        x_plan = interp(P, s, q + V * dt)
        u = air(x, hc, U, Uhat) if t <= T_cross else np.zeros_like(x)
        if avoid and t <= T_cross:
            r = x - hc
            along = r @ Uhat
            perp = r - along[:, None] * Uhat
            pn = np.linalg.norm(perp, axis=1)
            parked = (along > -RH) & (along < U * 0.15 + RH) & (pn < RH + 0.015)
        else:
            parked = np.zeros(len(x), bool)
        # desired velocity: follow the plan (return to the own stroke point). Schedule lag is NOT chased through space;
        # the scheduler re-phases tours afterwards.
        want = (x_plan - x) / dt
        rel = want - u
        rn = np.linalg.norm(rel, axis=1, keepdims=True)
        scale = np.minimum(1.0, VREL / np.maximum(rn, 1e-12))
        vel = u + rel * scale
        if parked.any():
            r = x[parked] - hc
            perp = r - (r @ Uhat)[:, None] * Uhat
            out_dir = perp / np.maximum(np.linalg.norm(perp, axis=1, keepdims=True), 1e-9)
            vel[parked] = u[parked] + VREL * out_dir                          # dodge sideways at the full budget
        vel[lost] = 0.0
        x_new = x + vel * dt
        # advance plan progress only for motes that are on track (within 1 mm of their plan point)
        on_track = np.linalg.norm(x_new - x_plan, axis=1) < 1e-3
        q = np.where(on_track & ~parked & ~lost, q + V * dt, q)
        x = x_new
        if t <= T_cross:
            inside = np.linalg.norm(x - hc, axis=1) < RH
            lost |= inside & ~parked
        # image distortion = distance of each mote from its own point on the stroke (a mote that lags along its tour
        # still draws the right shape; the scheduler re-spaces tour phases afterwards)
        d = np.linalg.norm(x - interp(P, s, q), axis=1)
        disp_max = np.maximum(disp_max, np.where(lost, 0, d))
        if t > T_cross and reform_t is None and np.all(d[~lost] < 1e-3):
            reform_t = t - T_cross
        t += dt
    return dict(U=U, avoid=avoid, N=N, lost=int(lost.sum()), displaced_gt_2mm=int((disp_max > 2e-3).sum()),
                max_disp_mm=float(disp_max.max() * 1e3), reform_s=reform_t)


if __name__ == "__main__":
    out = []
    for U in (0.3, 0.6, 1.0):
        for avoid in (False, True):
            r = run(U, avoid)
            out.append(r)
            print(f"hand {U:.1f} m/s, avoid={avoid}: N={r['N']}, lost {r['lost']}, displaced >2 mm {r['displaced_gt_2mm']}, "
                  f"max displacement {r['max_disp_mm']:.0f} mm, reform after {r['reform_s']} s", flush=True)
    json.dump(out, open(os.path.join(HERE, "results", "m9_touch.json"), "w"), indent=1)

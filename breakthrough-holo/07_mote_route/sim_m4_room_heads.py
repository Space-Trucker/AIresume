"""M4: room head arrays (owner, 2026-09-30: "multiple heads are fine, even more than 4, as long as they sit gracefully
in the room").

Geometry: a 6 x 5 x 2.8 m room; the image volume is 1.0 x 1.0 x 0.8 m, centred at (3.0, 2.5, 1.3) m (above a workbench).
The heads are small fixtures in ceiling coves, baseboards and wall niches.

For every mote position (27-point grid in the image volume) and every force direction u (600 on the sphere):
* Push allocation (active feedback). Solve the linear programme min sum f_i s.t. sum f_i d_i = u, f_i >= 0, with d_i the
  unit push direction of head i at that position. The heat factor is h(u) = min sum f. Also record the number of
  active beams and the largest single-beam share.
* Occlusion. Remove one head (a hand or body shadows it) and recompute the worst h. Infinite means some direction
  cannot be pushed.
* Passive doughnut pairs (lateral2). Two heads whose push directions at the mote are within 25 deg of opposite form a
  pair. For direction u the cost is |u.e| (axial, push difference) + |u_perp|/eta_lat, minimised over pairs; eta_lat is
  from physics.lg01_trap. The workload manager picks, per mote and instant, the pair best aligned with the motion.
Writes results/m4_room_heads.json.
"""
import itertools
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))

ROOM = (6.0, 5.0, 2.8)
CENTER = np.array([3.0, 2.5, 1.3])
HALF = np.array([0.5, 0.5, 0.4])
CEIL = [(0.15, 0.15, 2.7), (5.85, 0.15, 2.7), (5.85, 4.85, 2.7), (0.15, 4.85, 2.7)]
FLOOR = [(0.15, 0.15, 0.12), (5.85, 0.15, 0.12), (5.85, 4.85, 0.12), (0.15, 4.85, 0.12)]
NICHE = [(0.05, 2.5, 1.3), (5.95, 2.5, 1.3), (3.0, 0.05, 1.3), (3.0, 4.95, 1.3)]
LAYOUTS = {
    "H4 room-tetra (2 ceiling + 2 baseboard corners)": [CEIL[0], CEIL[2], FLOOR[1], FLOOR[3]],
    "H6 (4 ceiling corners + 2 baseboard mid-walls)": CEIL + [(3.0, 0.08, 0.12), (3.0, 4.92, 0.12)],
    "H8 (8 room corners)": CEIL + FLOOR,
    "H12 (8 corners + 4 wall niches at 1.3 m)": CEIL + FLOOR + NICHE,
    "H10 (8 corners + ceiling spot + floor head under the image)": CEIL + FLOOR + [(3.0, 2.5, 2.75), (3.0, 2.5, 0.05)],
    "H14 (8 corners + 4 niches + ceiling spot + floor head)": CEIL + FLOOR + NICHE + [(3.0, 2.5, 2.75), (3.0, 2.5, 0.05)],
    # 'lab rig': a ceiling ring of 6 heads (radius 1.8 m, cove at 2.65 m) + a low ring of 4 heads (radius 1.6 m, in the
    # workbench skirt / floor at 0.25 m) + ceiling spot + floor head: throws ~1.4-2.3 m
    "R12 lab rig (6 ceiling-ring + 4 low-ring + spot + floor)": [
        (3.0 + 1.8 * math.cos(k * math.pi / 3), 2.5 + 1.8 * math.sin(k * math.pi / 3), 2.65) for k in range(6)] + [
        (3.0 + 1.6 * math.cos(math.pi / 4 + k * math.pi / 2), 2.5 + 1.6 * math.sin(math.pi / 4 + k * math.pi / 2), 0.25)
        for k in range(4)] + [(3.0, 2.5, 2.75), (3.0, 2.5, 0.05)],
    "R8 lab rig (4 ceiling-ring + 4 low-ring, staggered)": [
        (3.0 + 1.8 * math.cos(k * math.pi / 2), 2.5 + 1.8 * math.sin(k * math.pi / 2), 2.65) for k in range(4)] + [
        (3.0 + 1.6 * math.cos(math.pi / 4 + k * math.pi / 2), 2.5 + 1.6 * math.sin(math.pi / 4 + k * math.pi / 2), 0.25)
        for k in range(4)],
}
ONLY = sys.argv[1:]


def fib_sphere(n):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


def push_dirs(heads, p):
    d = p[None, :] - np.asarray(heads, float)
    return d / np.linalg.norm(d, axis=1)[:, None]


def alloc(D, u):
    r = linprog(np.ones(len(D)), A_eq=D.T, b_eq=u, bounds=[(0, None)] * len(D), method="highs")
    if not r.success:
        return math.inf, 0, math.inf
    f = r.x
    return float(r.fun), int((f > 1e-6).sum()), float(f.max())


def pairs(D, tol_deg=25.0):
    out = []
    for i, j in itertools.combinations(range(len(D)), 2):
        ang = math.degrees(math.acos(max(-1.0, min(1.0, float(D[i] @ -D[j])))))
        if ang <= tol_deg:
            e = D[i] - D[j]
            out.append(e / np.linalg.norm(e))
    return out


def study(heads, eta_lat=0.25, n_dir=600):
    U = fib_sphere(n_dir)
    grid = [CENTER + HALF * np.array(s) for s in itertools.product((-1, 0, 1), repeat=3)]
    hs, act, single, lat_costs = [], [], [], []
    occl_worst = []
    for p in grid:
        D = push_dirs(heads, p)
        for u in U:
            h, na, fm = alloc(D, u)
            hs.append(h)
            act.append(na)
            single.append(fm)
        # occlusion: drop each head in turn, on a coarser direction set
        for k in range(len(heads)):
            Dk = np.delete(D, k, axis=0)
            occl_worst.append(max(alloc(Dk, u)[0] for u in U[::6]))
        P = pairs(D)
        for u in U:
            if P:
                lat_costs.append(min(abs(u @ e) + np.linalg.norm(u - (u @ e) * e) / eta_lat for e in P))
            else:
                lat_costs.append(math.inf)
    throws = [float(np.linalg.norm(np.asarray(h) - CENTER)) for h in heads]
    throw_mean = float(np.mean(throws))
    hs = np.array(hs)
    occl = np.array(occl_worst)
    lat = np.array(lat_costs)
    return dict(n_heads=len(heads), throw_min=min(throws), throw_max=max(throws), throw_mean=throw_mean,
                h_worst=float(hs.max()), h_mean=float(hs[np.isfinite(hs)].mean()), h_p95=float(np.percentile(hs, 95)),
                active_mean=float(np.mean(act)), single_max=float(max(single)),
                occluded_worst_h=float(np.max(occl)) if np.all(np.isfinite(occl)) else math.inf,
                occluded_frac_infeasible=float(np.mean(~np.isfinite(occl))),
                occluded_worst_h_finite_p95=float(np.percentile(occl[np.isfinite(occl)], 95)) if np.any(np.isfinite(occl)) else math.inf,
                n_pairs_center=len(pairs(push_dirs(heads, CENTER))),
                lateral_pairs_worst=float(lat.max()), lateral_pairs_mean=float(lat[np.isfinite(lat)].mean()) if np.any(np.isfinite(lat)) else math.inf)


if __name__ == "__main__":
    prev = {}
    if ONLY and os.path.exists(os.path.join(HERE, "results", "m4_room_heads.json")):
        prev = json.load(open(os.path.join(HERE, "results", "m4_room_heads.json")))
    out = dict(prev)
    for name, heads in LAYOUTS.items():
        if ONLY and not any(name.startswith(o) for o in ONLY):
            continue
        for eta in (0.25, 0.37):
            r = study(heads, eta_lat=eta)
            out[f"{name} | eta_lat {eta}"] = r
            print(f"{name:52s} eta_lat={eta}: throw {r['throw_min']:.1f}-{r['throw_max']:.1f} m | push h worst {r['h_worst']:.2f} "
                  f"mean {r['h_mean']:.2f} p95 {r['h_p95']:.2f}, active beams {r['active_mean']:.2f}, max single {r['single_max']:.2f} | "
                  f"one head blocked: worst h {r['occluded_worst_h']:.2f} (infeasible {100 * r['occluded_frac_infeasible']:.0f} % of cases) | "
                  f"pairs {r['n_pairs_center']}, pair-lateral cost worst {r['lateral_pairs_worst']:.2f} mean {r['lateral_pairs_mean']:.2f}",
                  flush=True)
    with open(os.path.join(HERE, "results", "m4_room_heads.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)

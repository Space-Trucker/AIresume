"""M21b: bead-bead hydrodynamic interactions in AIR-SV on real content (Oseen far field).

Each bead of radius a hovers in an upward flow U = v_s. In its own frame the air passes it upward with drag
F = 6 pi mu a U, and at the Oseen length nu/U (~0.15 mm at U 0.1 m/s) its far field changes from Stokes to Oseen
form. Beads sit 3 mm apart, i.e. 20-40 Oseen lengths, so the Oseen far field applies [DERIVED, standard]:
- inside the wake, downstream (above the bead): an axial velocity deficit
  u_def(z, r) = F / (4 pi mu z) * exp(-U r^2 / (4 nu z));
- outside the wake: a potential-source outflow of strength F/(rho U), u_src = F / (4 pi rho U R^2) radially, which
  balances the wake deficit.

The deficit makes a bead above another sink. Every other bead's wake and source flow is summed at each bead; the
vertical and lateral perturbations become the trim speed the light must supply, which is compared with m21's
budget. Content: the project's procedural Iron-Man armor (content.py, 9 m stroke budget) scaled to a 0.6 m image,
plus random segments, both sampled every 3 mm.

Run: python3 m21b_bead_wakes.py -> results/m21b_bead_wakes.json, results/m21b_run.log
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "04_engineering", "holo_engine"))
import content as c  # noqa: E402

MU, RHO_A = 1.81e-5, 1.2
NU = MU / RHO_A


def wake_field(P, a, U):
    """Velocity perturbation (3-vector, z up = flow direction) at every bead from all the others."""
    F = 6 * math.pi * MU * a * U
    n = len(P)
    out = np.zeros((n, 3))
    for i in range(n):
        d = P[i] - P                       # vector from each source j to target i
        d[i] = np.nan
        dz = d[:, 2]
        r2 = d[:, 0] ** 2 + d[:, 1] ** 2
        R2 = r2 + dz ** 2
        down = dz > 0                      # target downstream (above) the source: inside the wake region
        u = np.zeros((n, 3))
        # wake deficit (opposes the flow, i.e. pushes the target down)
        zz = np.where(down, dz, 1.0)
        defz = np.where(down, F / (4 * math.pi * MU * zz) * np.exp(-U * r2 / (4 * NU * zz)), 0.0)
        u[:, 2] -= defz
        # potential source outflow (radial from the source)
        src = F / (4 * math.pi * RHO_A * U * R2)
        Rn = np.sqrt(R2)
        u += (src / Rn)[:, None] * d
        u[i] = 0.0
        out[i] = np.nansum(u, axis=0)
    return out


def dedupe(P, dmin):
    """Merge points closer than dmin (strokes that share end points or cross): one bead per site."""
    keep = []
    for p in P:
        if not keep or np.min(np.linalg.norm(np.array(keep) - p, axis=1)) >= dmin:
            keep.append(p)
    return np.array(keep)


def content_points(kind, size=0.6, spacing=3e-3, seed=0):
    if kind == "armor":
        strokes, used = c.procedural_armor_budget(max_length_m=9.0, height=1.8)
        pts, _ = c.strokes_to_points(strokes, spacing * 1.8 / size)
        pts = (pts - pts.mean(axis=0)) * (size / 1.8)
        return dedupe(pts, 0.5 * spacing)
    rng = np.random.default_rng(seed)
    P = []
    for _ in range(int(5.0 / 0.1)):
        p0 = (rng.random(3) - 0.5) * size
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        for k in range(int(0.1 / spacing)):
            P.append(p0 + d * k * spacing)
    return dedupe(np.array(P), 0.5 * spacing)


def main():
    rows = []
    print(f"{'content':8s} {'a_um':>4s} {'U':>5s} {'N':>5s} {'dz_p50':>7s} {'dz_p90':>7s} {'dz_p99':>7s} {'dz_max':>7s} "
          f"{'lat_p99':>7s}   (mm/s; m21 budget assumed du_int ~0.1-0.4 mm/s)")
    for kind in ("armor", "random"):
        P = content_points(kind)
        for a, U in ((30e-6, 0.062), (40e-6, 0.105), (40e-6, 0.200)):
            u = wake_field(P, a, U)
            vz = np.abs(u[:, 2])
            lat = np.linalg.norm(u[:, :2], axis=1)
            d = dict(content=kind, a_um=a * 1e6, U=U, N=len(P), dz_p50=float(np.percentile(vz, 50) * 1e3),
                     dz_p90=float(np.percentile(vz, 90) * 1e3), dz_p99=float(np.percentile(vz, 99) * 1e3),
                     dz_max=float(vz.max() * 1e3), lat_p99=float(np.percentile(lat, 99) * 1e3),
                     frac_over_1mm_s=float(np.mean(vz > 1e-3)), frac_over_2mm_s=float(np.mean(vz > 2e-3)))
            rows.append(d)
            print(f"{kind:8s} {a * 1e6:4.0f} {U:5.3f} {len(P):5d} {d['dz_p50']:7.3f} {d['dz_p90']:7.3f} {d['dz_p99']:7.3f} "
                  f"{d['dz_max']:7.3f} {d['lat_p99']:7.3f}   >1 mm/s: {d['frac_over_1mm_s'] * 100:4.1f} %  "
                  f">2 mm/s: {d['frac_over_2mm_s'] * 100:4.1f} %")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m21b_bead_wakes.json"), "w") as fh:
        json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()

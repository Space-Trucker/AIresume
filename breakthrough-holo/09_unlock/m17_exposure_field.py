"""M17: summed 1550 nm exposure anywhere in the room for a static-voxel (LCSV) image ("line-of-sight stacking").

Each mote is held by ~3 active push beams from the H14 heads, focused at the mote with flat-top radius r_c (modelled as
a Gaussian of waist w0 = r_c). Away from its focus a beam diverges with half-angle lam/(pi w0). An eye (3.5 mm limiting
aperture for 1400-4000 nm, long exposure) placed anywhere collects the parts of ALL beams passing through it. Class 1
for the product needs the worst-case sum <= 10 mW, not just each focus <= AEL (idea round 2, opus: "a certified field
checker is still required"). This script finds the worst point for random film-density images and reports by how much a
naive per-focus design overshoots, and what per-focus cap restores the sum.

Run: python3 m17_exposure_field.py  -> results/m17_exposure.json
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55e-6
R_AP = 3.5e-3 / 2                      # limiting aperture radius at 1550 nm, long exposure
AEL = 10e-3
CEIL = [(0.15, 0.15, 2.7), (5.85, 0.15, 2.7), (5.85, 4.85, 2.7), (0.15, 4.85, 2.7)]
FLOOR = [(0.15, 0.15, 0.12), (5.85, 0.15, 0.12), (5.85, 4.85, 0.12), (0.15, 4.85, 0.12)]
NICHE = [(0.05, 2.5, 1.3), (5.95, 2.5, 1.3), (3.0, 0.05, 1.3), (3.0, 4.95, 1.3)]
H14 = np.array(CEIL + FLOOR + NICHE + [(3.0, 2.5, 2.75), (3.0, 2.5, 0.05)])
CENTER = np.array([3.0, 2.5, 1.3])
HALF = np.array([0.5, 0.5, 0.4])


def image(S=30.0, delta=3e-3, seg=0.1, rng=None):
    """Random wireframe: segments of length seg with random orientation inside the image volume; motes every delta."""
    pts = []
    n_seg = int(S / seg)
    for _ in range(n_seg):
        while True:
            p0 = CENTER + (rng.random(3) * 2 - 1) * HALF
            d = rng.normal(size=3)
            d /= np.linalg.norm(d)
            p1 = p0 + d * seg
            if np.all(np.abs(p1 - CENTER) <= HALF):
                break
        n = int(seg / delta)
        for k in range(n):
            pts.append(p0 + d * seg * k / n)
    return np.array(pts)


def beams_for(motes, n_active=3, rng=None):
    """Each mote: n_active distinct heads chosen with probability ~ spread over directions (random here)."""
    src = []
    for m in motes:
        idx = rng.choice(len(H14), size=n_active, replace=False)
        for i in idx:
            src.append((H14[i], m))
    return src


def exposure(points, beams, P_beam, w0):
    """Power through a 3.5 mm aperture at each point (aperture normal along each beam; Gaussian overlap)."""
    zR = math.pi * w0 * w0 / LAM
    total = np.zeros(len(points))
    S = np.array([b[0] for b in beams])
    F = np.array([b[1] for b in beams])
    D = F - S
    L = np.linalg.norm(D, axis=1)
    U = D / L[:, None]
    for j, x in enumerate(points):
        v = x - S
        t = np.einsum("ij,ij->i", v, U)                      # distance along the beam from the source
        z = t - L                                            # distance from the focus (negative = before)
        rho2 = np.einsum("ij,ij->i", v, v) - t * t           # squared distance from the axis
        w2 = w0 * w0 * (1 + (z / zR) ** 2)
        # fraction of a Gaussian beam (1/e^2 radius w) through a disc of radius R_AP offset by rho (good approximation):
        frac = (1 - np.exp(-2 * R_AP ** 2 / w2)) * np.exp(-2 * rho2 / (w2 + 2 * R_AP ** 2))
        frac[t < 0] = 0.0                                    # behind the head
        total[j] = P_beam * frac.sum()
    return total


def run(P_focus=4.0e-3, r_c=25e-6, S=30.0, delta=3e-3, n_active=3, seed=1, n_probe=4000):
    rng = np.random.default_rng(seed)
    motes = image(S, delta, rng=rng)
    beams = beams_for(motes, n_active, rng)
    P_beam = P_focus / n_active                              # the active beams share the focus budget
    # probe points: at motes (an eye placed at a voxel), and random points in and around the image volume
    n_m = min(n_probe // 2, len(motes))
    probes = np.vstack([motes[rng.choice(len(motes), size=n_m, replace=False)],
                        CENTER + (rng.random((n_probe // 2, 3)) * 2 - 1) * (HALF + 0.3)])
    E = exposure(probes, beams, P_beam, r_c)
    at_motes = E[:n_m]
    return dict(N=len(motes), beams=len(beams), P_focus_mW=P_focus * 1e3, r_c_um=r_c * 1e6, max_mW=float(E.max() * 1e3),
                p99_mW=float(np.percentile(E, 99) * 1e3), at_mote_median_mW=float(np.median(at_motes) * 1e3),
                own_focus_mW=P_focus * 1e3, stacking_factor=float(E.max() / P_focus))


def selftest():
    rng = np.random.default_rng(0)
    # one beam, aperture at its focus: all its power passes (w0 << R_AP)
    src = [(H14[0], CENTER)]
    E = exposure(np.array([CENTER]), src, 1e-3, 25e-6)
    ok1 = abs(E[0] - 1e-3) < 1e-6
    # far from the focus along the axis the fraction ~ (R_AP/w)^2 * 2
    z = 0.3
    x = CENTER + (CENTER - H14[0]) / np.linalg.norm(CENTER - H14[0]) * z
    E2 = exposure(np.array([x]), src, 1e-3, 25e-6)
    w = 25e-6 * math.sqrt(1 + (z / (math.pi * 25e-6 ** 2 / LAM)) ** 2)
    ok2 = abs(E2[0] - 1e-3 * (1 - math.exp(-2 * R_AP ** 2 / w ** 2))) < 1e-9
    print(f"self-test: focus capture {'PASS' if ok1 else 'FAIL'} ({E[0] * 1e3:.4f} mW); off-focus fraction "
          f"{'PASS' if ok2 else 'FAIL'} ({E2[0] * 1e3:.4f} mW at 0.3 m, w = {w * 1e3:.2f} mm)")
    return ok1 and ok2


if __name__ == "__main__":
    assert selftest()
    rows = []
    print(f"{'case':38s} {'N':>6s} {'Pfoc':>5s} {'r_c':>4s} {'max':>6s} {'p99':>6s} {'stack':>6s}")
    for name, P, r, S in (("film density, passive Class 1 (M15f)", 4.0e-3, 25e-6, 30.0),
                          ("film density, passive Class 1, r_c 15", 4.0e-3, 15e-6, 30.0),
                          ("sketch, passive Class 1", 4.0e-3, 25e-6, 5.0),
                          ("film density, curtain (M15f)", 10.0e-3, 22e-6, 30.0),
                          ("film density, curtain, 50 mW", 50.0e-3, 55e-6, 30.0)):
        d = run(P_focus=P, r_c=r, S=S)
        d["case"] = name
        rows.append(d)
        print(f"{name:38s} {d['N']:6d} {d['P_focus_mW']:5.1f} {d['r_c_um']:4.0f} {d['max_mW']:6.2f} {d['p99_mW']:6.2f} "
              f"{d['stacking_factor']:6.2f}")
    print("\nper-focus cap that keeps the worst summed exposure <= 10 mW (power scales linearly):")
    for d in rows:
        cap = d["P_focus_mW"] * 10.0 / d["max_mW"]
        d["focus_cap_for_class1_mW"] = cap
        print(f"  {d['case']:38s} cap {cap:5.2f} mW per focus (pixel count x{max(1.0, d['P_focus_mW'] / cap):.1f} "
              f"at fixed intensity, P*M invariant)")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m17_exposure.json"), "w") as fh:
        json.dump(rows, fh, indent=1)

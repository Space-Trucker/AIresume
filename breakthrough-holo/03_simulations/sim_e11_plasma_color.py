"""E11: What COLOURS can air plasma make? Chromaticity of the emission regimes, and the gamut
reachable by mixing pulse formats in time (persistence of vision averages them).

Regimes (spectral content from standard air-plasma spectroscopy; relative line strengths are
typical values for air sparks/filaments and are ESTIMATES, to be measured in experiment X1):
  S1 cold fs plasma      : N2 second positive + N2+ first negative bands (violet)
  S2 hot early continuum : free-free/free-bound continuum, T = 3 eV
  S3 ionic-line phase    : N II / O II lines + T = 2 eV continuum (N II 500.5 nm is cyan-green)
  S4 neutral-line phase  : O I, N I, H-alpha (humid air) + T = 1 eV continuum
Colour matching: CIE 1931 2-degree, 10 nm table. Calibration: equal-energy white -> (1/3, 1/3);
6500 K Planckian -> (0.3135, 0.3237).
"""
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import RESULTS, check, save_json

LAM = np.arange(380, 790, 10.0)
XB = np.array([0.001368, 0.004243, 0.01431, 0.04351, 0.13438, 0.2839, 0.34828, 0.3362, 0.2908, 0.19536,
               0.09564, 0.03201, 0.0049, 0.0093, 0.06327, 0.1655, 0.2904, 0.43345, 0.5945, 0.7621,
               0.9163, 1.0263, 1.0622, 1.0026, 0.85445, 0.6424, 0.4479, 0.2835, 0.1649, 0.0874,
               0.04677, 0.0227, 0.011359, 0.00579, 0.002899, 0.00144, 0.00069, 0.000332, 0.000166, 0.000083, 0.000042])
YB = np.array([0.000039, 0.00012, 0.000396, 0.00121, 0.004, 0.0116, 0.023, 0.038, 0.06, 0.09098,
               0.13902, 0.20802, 0.323, 0.503, 0.71, 0.862, 0.954, 0.99495, 0.995, 0.952,
               0.87, 0.757, 0.631, 0.503, 0.381, 0.265, 0.175, 0.107, 0.061, 0.032,
               0.017, 0.00821, 0.004102, 0.002091, 0.001047, 0.00052, 0.000249, 0.00012, 0.00006, 0.00003, 0.000015])
ZB = np.array([0.00645, 0.02005, 0.06785, 0.2074, 0.6456, 1.3856, 1.74706, 1.77211, 1.6692, 1.28764,
               0.81295, 0.46518, 0.272, 0.1582, 0.07825, 0.04216, 0.0203, 0.00875, 0.0039, 0.0021,
               0.00165, 0.0011, 0.0008, 0.00034, 0.00019, 0.00005, 0.00002] + [0.0] * 14)
FINE = np.arange(380, 781, 1.0)
xb, yb, zb = (np.interp(FINE, LAM, a) for a in (XB, YB, ZB))


def xy(spec):
    X, Y, Z = (np.sum(spec * a) for a in (xb, yb, zb))
    s = X + Y + Z
    return X / s, Y / s, Y


def lines(pairs, width=1.0):
    s = np.zeros_like(FINE)
    for lam, a in pairs:
        s += a * np.exp(-0.5 * ((FINE - lam) / width) ** 2)
    return s


def continuum(T_eV):
    # optically thin free-free + free-bound, per unit wavelength: ~ exp(-hc/(lam kT)) / lam^2
    hc_eV_nm = 1239.84
    return np.exp(-hc_eV_nm / (FINE * T_eV)) / FINE ** 2


def planck(T):
    l = FINE * 1e-9
    return 1 / (l ** 5 * (np.exp(1.4388e-2 / (l * T)) - 1))


N2_BANDS = [(380.5, 0.4), (394.3, 0.1), (399.8, 0.15), (405.9, 0.1), (420.0, 0.05), (426.9, 0.03), (434.4, 0.02),
            (391.4, 0.6), (427.8, 0.2), (470.9, 0.03)]
N_II = [(399.5, 0.3), (444.7, 0.2), (463.1, 0.5), (500.5, 1.0), (504.5, 0.2), (567.9, 0.8), (593.2, 0.3),
        (648.2, 0.2), (661.1, 0.2)]
O_II = [(407.2, 0.3), (434.9, 0.3), (441.5, 0.4), (459.1, 0.2), (464.9, 0.5)]
NEUTRAL = [(615.7, 0.1), (645.4, 0.05), (656.3, 0.3), (486.1, 0.05), (777.3, 1.0), (746.8, 0.8)]


def normalise(s):
    return s / np.sum(s * yb)


STATES = {
    "S1 cold fs (N2 bands)": normalise(lines(N2_BANDS, 1.5)),
    "S2 hot continuum 3 eV": normalise(continuum(3.0)),
    "S3 ionic lines + 2 eV": normalise(normalise(lines(N_II + O_II, 0.8)) + 0.5 * normalise(continuum(2.0))),
    "S4 neutral lines + 1 eV": normalise(normalise(lines(NEUTRAL, 0.8)) + 0.5 * normalise(continuum(1.0))),
    "S3' N II-dominated (line phase, weak continuum)": normalise(normalise(lines(N_II, 0.8)) + 0.1 * normalise(continuum(2.0))),
}

if __name__ == "__main__":
    print("E11 plasma colour gamut")
    ee = xy(np.ones_like(FINE))
    ok1 = check("equal-energy white x", ee[0], 1 / 3, 0.01, "CIE definition")
    ok2 = check("equal-energy white y", ee[1], 1 / 3, 0.01, "CIE definition")
    p65 = xy(planck(6500.0))
    ok3 = check("6500 K Planckian x", p65[0], 0.3135, 0.01, "CIE Planckian locus")
    ok4 = check("6500 K Planckian y", p65[1], 0.3237, 0.01, "CIE Planckian locus")
    res = {"calibration_pass": bool(ok1 and ok2 and ok3 and ok4), "states": {}}
    for k, s in STATES.items():
        x, y, _ = xy(s)
        res["states"][k] = (x, y)
        print(f"  {k:48s} x={x:.3f} y={y:.3f}")
    targets = {"film cyan (sRGB 0,0.8,1)": None, "film orange (sRGB 1,0.5,0)": None}

    def srgb_xy(r, g, b):
        def lin(u):
            return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
        r, g, b = map(lin, (r, g, b))
        M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
        X, Y, Z = M @ np.array([r, g, b])
        return X / (X + Y + Z), Y / (X + Y + Z)
    targets = {"film cyan": srgb_xy(0, 0.8, 1.0), "film orange": srgb_xy(1.0, 0.5, 0.0), "D65 white": (0.3127, 0.329)}
    res["targets"] = targets
    # is the target inside the convex hull of the states (mixing by persistence of vision)?
    from scipy.spatial import ConvexHull, Delaunay
    pts = np.array(list(res["states"].values()))
    hull = Delaunay(pts)
    for k, t in targets.items():
        inside = bool(hull.find_simplex(np.array(t)) >= 0)
        d = float(np.min(np.linalg.norm(pts - np.array(t), axis=1)))
        res.setdefault("reachable", {})[k] = dict(inside_gamut=inside, xy=t)
        print(f"  target {k:12s} xy=({t[0]:.3f},{t[1]:.3f}) inside plasma mixing gamut: {inside}")
    save_json("e11_plasma_color.json", res)
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    # spectral locus
    s = np.array([xy(np.exp(-0.5 * ((FINE - l) / 0.5) ** 2))[:2] for l in range(390, 700, 2)])
    ax.plot(s[:, 0], s[:, 1], "k-", lw=0.8); ax.plot([s[0, 0], s[-1, 0]], [s[0, 1], s[-1, 1]], "k:", lw=0.8)
    hp = pts[ConvexHull(pts).vertices]
    ax.fill(hp[:, 0], hp[:, 1], color="#9ec5ff", alpha=0.4, label="air-plasma gamut (mixing regimes)")
    for k, (x, y) in res["states"].items():
        ax.plot(x, y, "o", color="#2050a0"); ax.annotate(k.split(" (")[0].split(" +")[0], (x, y), fontsize=7, xytext=(4, 4), textcoords="offset points")
    for k, (x, y) in targets.items():
        ax.plot(x, y, "*", ms=12, color={"film cyan": "#00b8d4", "film orange": "#ff8c00", "D65 white": "k"}[k], label=k)
    ax.set_xlabel("CIE x"); ax.set_ylabel("CIE y"); ax.set_xlim(0, 0.75); ax.set_ylim(0, 0.85)
    ax.legend(fontsize=7, loc="upper right"); ax.set_title("Colours an air-plasma display can mix")
    plt.tight_layout(); plt.savefig(f"{RESULTS}/e11_plasma_color.png", dpi=120); plt.close()
    print("  saved results/e11_plasma_color.json/.png")

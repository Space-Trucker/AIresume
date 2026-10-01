"""D1b: independent red-team check of sim_d1_lens_trap.py (claims A-D).

Nothing here calls the simulation's ray trace, Debye integral or disc-weight code for the core numbers. Methods:
  A  own meridional trace written in angle (scalar trig) form, OPD from Hamilton's angle characteristic (optical path
     to the foot of the perpendicular from the paraxial focus), cross-checked by the identity dT/dtheta = -d(theta)
     (integral of the longitudinal aberration) and by Seidel sums (thin lens and surface-by-surface thick lens).
  B  geometric-optics field on a real plane just behind the lens (amplitude from energy conservation, phase k*OPL),
     exact scalar angular-spectrum propagation in Hankel form (A(kappa) by direct quadrature, exp(i kz z)), then the
     disc average by polar Gauss-Legendre x trapezoid quadrature on interpolated intensity (sparse matrix).
  C  own drag / settling / Cunningham / Sutherland numbers, burn-cap scaling with particle size and density, and a
     gradient-force estimate of the lateral efficiency from the computed pocket profile.
  D  ABCD round trips (lab-frame slopes) for corner cube / flat mirror at and away from L2's back focal plane, an
     exact 3D vector ray trace through a real plano-convex L2 and an ideal hollow corner cube, and 3D polarisation
     ray tracing (Fresnel, Chipman PRT matrices) of QWP - cube - QWP into a PBS.
  E  beyond the claims: exact 3D trace of tilted / decentred beams through L1, 3D angle characteristic -> 2D angular
     spectrum -> disc average by FFT with the analytic disc transform -> 2D escape barrier (watershed by bisection).
  F  the guide's "6 mm beam fits 7 mm galvo mirrors": the part-B pipeline with a hard aperture.
  The simulation module is imported ONLY at the end, to put its own numbers next to ours (comparison, not reuse).
Run: python3 d1b_independent_check.py [--quick] [--parts ABCDE]   -> results/d1b_independent_check.json
  (~6 min on 4 cores; a subset of --parts is merged into an existing JSON)
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import j0, j1
from scipy.sparse import csr_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")

LAM = 405e-9
K0 = 2 * np.pi / LAM
N_GLASS = 1.53024          # N-BK7 at 404.66 nm (Schott h-line), independent of the sim's constant
R_CURV = 51.5e-3
T_C = 3.6e-3
CLEAR = 11.43e-3           # 90 % of 25.4 mm diameter


# ===================================================================================================== A. ray optics
def trace_flat_first(h, n=N_GLASS, R=R_CURV, tc=T_C):
    """Collimated ray at height h hits the plane z = 0 (no bend), meets the sphere (centre z = tc - R) at
    z_s = tc - R + sqrt(R^2 - h^2), incidence angle i = asin(h/R), refraction n sin i = sin i'. The outgoing ray makes
    the angle u = i' - i with the axis, toward the axis. Returns height at the last surface, its z, u, OPL to that point."""
    h = np.asarray(h, float)
    zs = tc - R + np.sqrt(R * R - h * h)
    i = np.arcsin(h / R)
    ip = np.arcsin(n * h / R)
    u = ip - i
    return h, zs, u, n * zs


def trace_curved_first(h, n=N_GLASS, R=R_CURV, tc=T_C):
    """Sphere first (centre at z = R): z1 = R - sqrt(R^2 - h^2), sin i = h/R, sin i' = sin i / n, the ray in glass is at
    u1 = i - i' toward the axis; plane exit at z = tc: sin u2 = n sin u1."""
    h = np.asarray(h, float)
    z1 = R - np.sqrt(R * R - h * h)
    i = np.arcsin(h / R)
    ip = np.arcsin(np.sin(i) / n)
    u1 = i - ip
    L = (tc - z1) / np.cos(u1)
    h2 = h - L * np.sin(u1)
    u2 = np.arcsin(n * np.sin(u1))
    return h2, np.full_like(h, tc), u2, z1 + n * L


TRACE = {"flat_first": trace_flat_first, "curved_first": trace_curved_first}


def paraxial_focus(orient):
    y, z, u, _ = TRACE[orient](np.array([1e-7]))
    return float(z[0] + y[0] / math.tan(u[0]))


def angle_characteristic(orient, h):
    """W(h) = T(h) - T(0), T = optical path from the input plane z = 0 to the foot of the perpendicular dropped from the
    paraxial focus F onto the ray (= OPD on a reference sphere of infinite radius about F). Also LA(h) and theta(h)."""
    zF = paraxial_focus(orient)
    y, z, u, opl = TRACE[orient](h)
    # unit ray direction e = (-sin u, cos u) in (y, z); vector F - P = (-y, zF - z)
    T = opl + y * np.sin(u) + (zF - z) * np.cos(u)
    y0, z0, u0, opl0 = TRACE[orient](np.array([0.0]))
    T0 = opl0[0] + (zF - z0[0])
    LA = z + y / np.tan(u) - zF
    return zF, T - T0, LA, u


def opd_from_LA(u, LA):
    """Identity for the angle characteristic about F: dT/du = -d(u), d = signed perpendicular distance of the ray from
    F = -LA sin u (ray crossing the axis a distance LA before F). So W(u) = int_0^u LA(u') sin u' du'."""
    f = LA * np.sin(u)
    return np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(u))])


def seidel_thin(h, f, n=N_GLASS, B=+1.0, C=-1.0):
    """Thin-lens third-order W040 at height h (Welford): S_I = h^4/(4 f^3) [ (n/(n-1))^2 + (n+2)/(n (n-1)^2)
    (B + 2 (n^2-1)/(n+2) C)^2 - n/(n+2) C^2 ], W040 = S_I / 8. Object at infinity: C = -1 with B = (c1+c2)/(c1-c2):
    curved first B = +1, flat first B = -1."""
    br = (n / (n - 1)) ** 2 + (n + 2) / (n * (n - 1) ** 2) * (B + 2 * (n * n - 1) / (n + 2) * C) ** 2 - n / (n + 2) * C * C
    return h ** 4 / (32 * f ** 3) * br


def seidel_thick(orient, h, n=N_GLASS, R=R_CURV, tc=T_C):
    """Surface-by-surface Seidel S_I = -sum A^2 y Delta(u/n), A = n (y c + u), with a paraxial marginal ray of height
    h (sign convention: u positive = ray rising, c = 1/R). Returns W040 = S_I / 8 (positive = marginal focus short in
    this convention is checked numerically against the trace)."""
    if orient == "flat_first":
        surfs = [(0.0, 1.0, n, tc), (-1.0 / R, n, 1.0, None)]
    else:
        surfs = [(1.0 / R, 1.0, n, tc), (0.0, n, 1.0, None)]
    y, u, S = h, 0.0, 0.0
    for c, n1, n2, t in surfs:
        A = n1 * (y * c + u)
        u2 = (n1 * u - y * c * (n2 - n1)) / n2
        S += -A * A * y * (u2 / n2 - u / n1)
        u = u2
        if t is not None:
            y = y + t * u
    return S / 8


def part_A():
    out = {}
    print("\n=== A. ray trace and wavefront spherical aberration (own trace) ===")
    f_eff = R_CURV / (N_GLASS - 1)
    for orient in ("flat_first", "curved_first"):
        zF = paraxial_focus(orient)
        bfl = zF - T_C
        print(f"  {orient:12s}: paraxial focus at {zF * 1e3:.4f} mm from the front vertex, BFL {bfl * 1e3:.4f} mm "
              f"(EFL R/(n-1) = {f_eff * 1e3:.4f}; expected BFL {'f' if orient == 'flat_first' else 'f - tc/n'} = "
              f"{(f_eff if orient == 'flat_first' else f_eff - T_C / N_GLASS) * 1e3:.4f} mm)")
        out[orient] = dict(zF_mm=zF * 1e3, BFL_mm=bfl * 1e3, rows=[])
    for w in (2.5e-3, 3e-3, 3.5e-3, 4e-3, 6e-3):
        h99 = w * math.sqrt(math.log(100) / 2)                      # exp(-2 h^2 / w^2) = 0.01
        for orient in ("flat_first", "curved_first"):
            hs = np.linspace(0, h99, 4001)
            hs[0] = 1e-9
            zF, W, LA, u = angle_characteristic(orient, hs)
            W2 = opd_from_LA(u, LA)
            Wth = -seidel_thin(h99, f_eff, B=(-1.0 if orient == "flat_first" else 1.0))
            Wtk = seidel_thick(orient, h99)
            row = dict(w_mm=w * 1e3, h99_mm=h99 * 1e3, NA99=float(np.sin(u[-1])), W99_waves=float(W[-1] / LAM),
                       W99_from_LA_waves=float(W2[-1] / LAM), W_seidel_thin_waves=float(Wth / LAM),
                       W_seidel_thick_waves=float(Wtk / LAM), LA99_mm=float(LA[-1] * 1e3),
                       LA_third_order_mm=float(-4 * abs(Wtk) / math.sin(u[-1]) ** 2 * 1e3))
            out[orient]["rows"].append(row)
            print(f"  w {w * 1e3:3.1f} mm {orient:12s} h99 {h99 * 1e3:5.3f} mm  NA {row['NA99']:.4f}  W(angle char.) "
                  f"{row['W99_waves']:+7.3f}  W(int LA) {row['W99_from_LA_waves']:+7.3f}  Seidel thin {row['W_seidel_thin_waves']:+7.3f}"
                  f"  thick |{abs(row['W_seidel_thick_waves']):6.3f}| waves   LA {row['LA99_mm']:+6.3f} mm (3rd order "
                  f"{row['LA_third_order_mm']:+6.3f})")
    # flat/curved ratio at small aperture vs thin-lens Seidel
    h = np.array([1e-9, 1.5e-3])
    Wf = angle_characteristic("flat_first", h)[1][-1]
    Wc = angle_characteristic("curved_first", h)[1][-1]
    rat_th = seidel_thin(1, 1, B=-1) / seidel_thin(1, 1, B=1)
    out["ratio_flat_over_curved_h1p5mm"] = float(Wf / Wc)
    out["ratio_thin_seidel"] = float(rat_th)
    print(f"  SA ratio flat/curved at h = 1.5 mm: trace {Wf / Wc:.3f}, thin-lens Seidel {rat_th:.3f}")
    return out


# =============================================================================================== B. angular spectrum
def exit_plane_rays(orient, hs):
    """Map input height h to the real plane z = tc (back vertex for flat first, back face for curved first):
    radius rho(h), OPL(h) from the input plane z = 0, ray angle u."""
    y, z, u, opl = TRACE[orient](hs)
    dz = T_C - z                                                   # air gap to the plane (0 for curved first)
    rho = y - dz * np.tan(u)
    opl = opl + dz / np.cos(u)
    return rho, opl, u


def angular_spectrum(orient, w, kap, dh=0.25e-6, hmax=None, chunk=256):
    """A(kappa) = int E(rho) J0(kappa rho) rho drho on the exit plane, integrated over the input height h:
    E rho drho = sqrt(I_in(h) h rho (drho/dh) / cos u) exp(i k OPL) dh  (energy conservation, |E|^2 cos u = flux).
    I_in normalised to 1 W. Returns A and the propagation distance from the exit plane to the paraxial focus."""
    if hmax is None:
        hmax = min(CLEAR, 3.6 * w)
    hs = (np.arange(int(round(hmax / dh))) + 0.5) * dh
    rho, opl, u = exit_plane_rays(orient, hs)
    drho = np.gradient(rho, hs)
    Iin = 2 / (np.pi * w * w) * np.exp(-2 * hs ** 2 / (w * w))
    phase = K0 * (opl - opl[0])
    g = np.sqrt(Iin * hs * rho * drho / np.cos(u)) * np.exp(1j * phase) * dh
    A = np.empty(len(kap), complex)
    for i0 in range(0, len(kap), chunk):
        Jm = j0(np.outer(kap[i0:i0 + chunk], rho))
        A[i0:i0 + chunk] = Jm @ g.real + 1j * (Jm @ g.imag)
    L = paraxial_focus(orient) - T_C
    return A, L, float(np.max(np.sin(u) * (Iin > Iin[0] * 1e-8)))


def propagate(A, kap, L, zrel, rs):
    """U(r, L + z) = int A(kappa) exp(i kz (L + z)) J0(kappa r) kappa dkappa, exact scalar (Hankel-pair normalised so
    that |U|^2 is W/m^2 for 1 W). Returns I[z, r]."""
    dk = kap[1] - kap[0]
    dkz = -kap * kap / (K0 + np.sqrt(K0 * K0 - kap * kap))       # kz - k, without cancellation
    Jr = j0(np.outer(rs, kap))                                    # (Nr, Nk)
    out = np.empty((len(zrel), len(rs)))
    for i0 in range(0, len(zrel), 128):
        zz = zrel[i0:i0 + 128]
        G = (A * kap * dk)[:, None] * np.exp(1j * np.outer(dkz, L + zz))
        U = Jr @ G.real + 1j * (Jr @ G.imag)
        out[i0:i0 + 128] = (np.abs(U) ** 2).T
    return out


def disc_matrix(rs, r0s, a, n_r=24, n_phi=64):
    """Sparse M with P_int(r0) = M @ I(r): polar quadrature over the disc (radius a, centre at distance r0 from the axis):
    Gauss-Legendre in rho' (weight rho'), trapezoid in phi' (periodic -> spectral), linear interpolation of I(r)."""
    x, wx = leggauss(n_r)
    rp = 0.5 * a * (x + 1)
    wr = 0.5 * a * wx * rp
    ph = (np.arange(n_phi) + 0.5) * 2 * np.pi / n_phi
    wp = 2 * np.pi / n_phi
    RP, PH = np.meshgrid(rp, ph, indexing="ij")
    RP, PH = RP.ravel(), PH.ravel()
    W = np.repeat(wr, n_phi) * wp
    dr = rs[1] - rs[0]
    R = np.sqrt(r0s[:, None] ** 2 + RP[None, :] ** 2 + 2 * r0s[:, None] * RP[None, :] * np.cos(PH)[None, :])
    t = R / dr
    j = np.floor(t).astype(int)
    fr = t - j
    rows = np.repeat(np.arange(len(r0s)), 2 * len(RP))
    cols = np.concatenate([j, j + 1], axis=1).ravel()
    vals = np.concatenate([W[None, :] * (1 - fr), W[None, :] * fr], axis=1).ravel()
    M = csr_matrix((vals, (rows, cols)), shape=(len(r0s), len(rs) + 1))
    return M[:, :len(rs)]


def pocket_metrics(P, zrel):
    """Same metric definition as the claim: contrast = first local max of P_int(r0) away from the axis / P_int(0),
    only where P_int rises from the axis; axial stability = dP_int(0)/dz < 0 (beam up, z downstream)."""
    P0 = P[:, 0]
    con = np.zeros(len(zrel))
    iw = np.zeros(len(zrel), int)
    for k in range(len(zrel)):
        row = P[k]
        if row[1] <= row[0]:
            continue
        i = 1
        while i + 1 < len(row) and row[i + 1] > row[i]:
            i += 1
        if i + 1 < len(row):
            con[k], iw[k] = row[i] / row[0], i
    dP0 = np.gradient(P0, zrel)
    return P0, con, iw, dP0


def best_stable(con, dP0, zrel):
    ok = (con >= 1.05) & (dP0 < 0)
    ok[:2] = ok[-2:] = False
    if not ok.any():
        return None
    k = int(np.argmax(np.where(ok, con, -1)))
    lo = hi = k
    while lo > 0 and ok[lo - 1]:
        lo -= 1
    while hi + 1 < len(ok) and ok[hi + 1]:
        hi += 1
    return k, float(zrel[hi] - zrel[lo])


def validate_B():
    """Propagator checks on cases with known answers (no lens): (1) perfect converging spherical wave, uniform
    amplitude, NA 0.05 at 97 mm -> Airy peak pi NA^2 P / lam^2 and first zero 0.61 lam / NA; (2) power conservation;
    (3) disc quadrature on I = 1 and I = r^2."""
    print("\n  propagator validation")
    res = {}
    L = 0.097
    NA = 0.05
    rmax = NA * L / math.sqrt(1 - NA * NA)
    dr = 0.25e-6
    rho = (np.arange(int(rmax / dr)) + 0.5) * dr
    E = np.exp(-1j * K0 * (np.sqrt(rho ** 2 + L * L) - L))
    # normalise to 1 W (flux ~ |E|^2 cos theta; use |E|^2 for the ideal-case peak formula, small NA)
    E /= math.sqrt(np.sum(np.abs(E) ** 2 * 2 * np.pi * rho) * dr)
    kap = np.linspace(0, 1.6 * NA * K0, 8000)
    A = np.empty(len(kap), complex)
    for i0 in range(0, len(kap), 256):
        A[i0:i0 + 256] = j0(np.outer(kap[i0:i0 + 256], rho)) @ (E * rho * dr)
    rs = np.arange(0, 12e-6, 0.01e-6)
    I = propagate(A, kap, L, np.array([0.0]), rs)[0]
    # true focus of the uniform spherical wave in scalar theory is at L (Fresnel number >> 1)
    peak_want = math.pi * NA ** 2 / LAM ** 2
    iz = np.argmin(I[: int(0.6 * len(rs))])
    res["airy_peak_ratio"] = float(I[0] / peak_want)
    res["airy_zero_ratio"] = float(rs[iz] / (0.6098 * LAM / NA))
    rs2 = np.arange(0, 400e-6, 0.1e-6)
    I2 = propagate(A, kap, L, np.array([-1e-3]), rs2)[0]
    res["power_1mm_defocus"] = float(np.sum(I2 * 2 * np.pi * rs2) * 0.1e-6)
    print(f"    Airy peak / (pi NA^2/lam^2) = {res['airy_peak_ratio']:.4f}; first zero / (0.61 lam/NA) = "
          f"{res['airy_zero_ratio']:.4f}; power 1 mm before focus = {res['power_1mm_defocus']:.4f} W")
    a = 2.5e-6
    rs3 = np.arange(0, 40e-6, 0.1e-6)
    r0 = np.arange(0, 30e-6, 0.1e-6)
    M = disc_matrix(rs3, r0, a)
    u1 = M @ np.ones_like(rs3)
    u2 = M @ rs3 ** 2
    want2 = np.pi * a * a * (r0 ** 2 + a * a / 2)
    res["disc_uniform_maxerr"] = float(np.max(np.abs(u1 / (np.pi * a * a) - 1)))
    res["disc_r2_maxerr"] = float(np.max(np.abs(u2 / want2 - 1)))
    print(f"    disc quadrature: max rel err uniform {res['disc_uniform_maxerr']:.2e}, I = r^2 {res['disc_r2_maxerr']:.2e}")
    return res


def run_config(orient, w, a=2.5e-6, zlo=-2.4e-3, zhi=1.0e-3, dz=4e-6, rmax=250e-6, dr=0.1e-6, nk=5000,
               dh=0.25e-6, refine=True, clip=None):
    """clip: hard circular aperture radius on the input beam (e.g. a galvo mirror), applied at the lens."""
    t0 = time.time()
    hmax = min(CLEAR, 3.6 * w)
    smax = float(np.max(np.sin(exit_plane_rays(orient, np.array([hmax]))[2])))
    kap = np.linspace(0, 1.15 * smax * K0 + 40 / w, nk)
    A, L, _ = angular_spectrum(orient, w, kap, dh=dh, hmax=hmax if clip is None else min(hmax, clip))
    zrel = np.arange(zlo, zhi + dz / 2, dz)
    rs = np.arange(0, rmax, dr)
    I = propagate(A, kap, L, zrel, rs)
    r0s = rs[rs <= rmax - a - 2 * dr]
    M = disc_matrix(rs, r0s, a)
    P = (M @ I.T).T
    P0, con, iw, dP0 = pocket_metrics(P, zrel)
    b = best_stable(con, dP0, zrel)
    res = dict(orient=orient, w_mm=w * 1e3, a_um=a * 1e6, z_mm=(zrel * 1e3).tolist(), contrast=con.tolist(),
               dP0dz_sign=np.sign(dP0).astype(int).tolist(), wall_um=(r0s[iw] * 1e6).tolist())
    # power check at the far end of the window
    res["power_check_W"] = float(np.sum(I[0] * 2 * np.pi * rs) * dr)
    if b is not None:
        k, run = b
        res.update(best_contrast=float(con[k]), best_z_mm=float(zrel[k] * 1e3), best_wall_um=float(r0s[iw[k]] * 1e6),
                   stable_run_um=run * 1e6)
        if refine:                                                # fine z scan around the best
            zf = np.arange(zrel[k] - 60e-6, zrel[k] + 30e-6 + 1e-7, 0.5e-6)
            If = propagate(A, kap, L, zf, rs)
            Pf = (M @ If.T).T
            P0f, conf, iwf, dPf = pocket_metrics(Pf, zf)
            bf = best_stable(conf, dPf, zf)
            if bf is not None:
                kf = bf[0]
                res.update(best_contrast_fine=float(conf[kf]), best_z_fine_mm=float(zf[kf] * 1e3),
                           best_wall_fine_um=float(r0s[iwf[kf]] * 1e6))
                # axial margin: where is the minimum of P0(z) relative to the contrast peak, and what contrast is left
                # where the push still varies by >= 1 % of the weight per micron (-dlnP0/dz >= 1/100 um)
                im = int(np.argmin(P0f))
                slope = -np.gradient(np.log(P0f), zf)
                res["z_P0min_fine_mm"] = float(zf[im] * 1e3)
                res["axial"] = {}
                for up in (5e-6, 10e-6, 20e-6, 30e-6):
                    kk = int(np.argmin(np.abs(zf - (zf[im] - up))))
                    res["axial"][f"{up * 1e6:.0f}um_upstream"] = dict(contrast=float(conf[kk]),
                                                                      minus_dlnP0dz_per_um=float(slope[kk] * 1e-6))
                stiff = (slope * 1e-6 >= 0.01) & (conf >= 1.05)
                if stiff.any():
                    ks = int(np.argmax(np.where(stiff, conf, 0)))
                    res["axial"]["best_with_1pct_per_um"] = dict(contrast=float(conf[ks]), z_mm=float(zf[ks] * 1e3))
                res["profile_best"] = dict(r_um=(rs[:800] * 1e6).tolist(), I=(If[kf, :800]).tolist(),
                                           r0_um=(r0s[:800] * 1e6).tolist(), P=(Pf[kf, :800]).tolist())
    # also the max contrast regardless of axial stability, for context
    kk = int(np.argmax(con))
    res.update(max_contrast_any=float(con[kk]), max_contrast_any_z_mm=float(zrel[kk] * 1e3),
               max_contrast_any_stable=bool(dP0[kk] < 0), seconds=time.time() - t0)
    return res, (zrel, rs, I, r0s, P)


def part_B(quick=False):
    print("\n=== B. focal region by exact angular-spectrum propagation from the real exit plane ===")
    out = dict(validation=validate_B(), configs=[])
    cfgs = [("flat_first", 2.5e-3), ("flat_first", 2.75e-3), ("flat_first", 2.9e-3), ("flat_first", 3e-3),
            ("flat_first", 3.1e-3), ("flat_first", 3.25e-3), ("flat_first", 3.5e-3), ("flat_first", 4e-3),
            ("flat_first", 6e-3), ("curved_first", 3e-3), ("curved_first", 4e-3), ("curved_first", 6e-3)]
    if quick:
        cfgs = [("flat_first", 3e-3), ("flat_first", 4e-3)]
    else:
        res8, _ = run_config("flat_first", 3e-3, a=4e-6)
        out["toner_a4um_w3"] = {k: v for k, v in res8.items() if k not in ("z_mm", "contrast", "dP0dz_sign", "wall_um")}
        print(f"  flat_first   w 3.0 mm, a = 4 um (toner-size): best stable contrast {res8.get('best_contrast_fine', float('nan')):.2f}"
              f" at {res8.get('best_z_fine_mm', float('nan')):+.4f} mm")
    store = {}
    for orient, w in cfgs:
        kw = dict(dz=8e-6, nk=3000, dh=0.5e-6) if quick else {}
        if w >= 6e-3:
            kw.update(zlo=-4.5e-3, rmax=350e-6)
        res, data = run_config(orient, w, **kw)
        out["configs"].append(res)
        store[(orient, w)] = data
        if "best_contrast" in res:
            print(f"  {orient:12s} w {w * 1e3:3.1f} mm: best stable contrast {res['best_contrast']:7.2f} at z "
                  f"{res['best_z_mm']:+.3f} mm (fine: {res.get('best_contrast_fine', float('nan')):7.2f} at "
                  f"{res.get('best_z_fine_mm', float('nan')):+.4f} mm), wall r0 {res['best_wall_um']:.1f} um, stable run "
                  f"{res['stable_run_um']:.0f} um; max any {res['max_contrast_any']:.2f} at {res['max_contrast_any_z_mm']:+.3f} "
                  f"(stable {res['max_contrast_any_stable']}); power {res['power_check_W']:.4f} W; {res['seconds']:.0f} s")
        else:
            print(f"  {orient:12s} w {w * 1e3:3.1f} mm: no axially stable pocket; max any {res['max_contrast_any']:.2f} "
                  f"at {res['max_contrast_any_z_mm']:+.3f} mm; {res['seconds']:.0f} s")
        if "axial" in res:
            ax = res["axial"]
            print(f"      P0(z) minimum at {res['z_P0min_fine_mm']:+.4f} mm; contrast 5/10/20 um upstream of it: "
                  f"{ax['5um_upstream']['contrast']:.1f}/{ax['10um_upstream']['contrast']:.1f}/{ax['20um_upstream']['contrast']:.1f}"
                  f" (-dlnP0/dz {ax['5um_upstream']['minus_dlnP0dz_per_um'] * 100:.2f}/{ax['10um_upstream']['minus_dlnP0dz_per_um'] * 100:.2f}"
                  f"/{ax['20um_upstream']['minus_dlnP0dz_per_um'] * 100:.2f} %/um); best with >= 1 %/um: "
                  f"{ax.get('best_with_1pct_per_um', {}).get('contrast', float('nan')):.1f}")
    return out, store



# ======================================================================================================= C. dynamics
KB = 1.380649e-23
P_ATM = 101325.0
M_AIR = 0.028965
R_U = 8.314462
G = 9.80665


def mu_sutherland(T):
    """ICAO form mu = beta T^1.5 / (T + S), beta = 1.458e-6, S = 110.4 K."""
    return 1.458e-6 * T ** 1.5 / (T + 110.4)


def mfp_ce(T):
    """Chapman-Enskog simple kinetic theory: mu = 0.499 rho cbar lambda."""
    rho_cbar = P_ATM * math.sqrt(8 * M_AIR / (math.pi * R_U * T))
    return mu_sutherland(T) / (0.499 * rho_cbar)


def cunningham_ar(a, T):
    """Allen & Raabe (1985) slip correction, Kn = lambda / a."""
    kn = mfp_ce(T) / a
    return 1 + kn * (1.142 + 0.558 * math.exp(-0.999 / kn))


def v_settle(a, rho_p, T=293.15):
    rho_g = P_ATM * M_AIR / (R_U * 293.15)
    return 2 * (rho_p - rho_g) * G * a * a * cunningham_ar(a, T) / (9 * mu_sutherland(T))


def k_air(T):
    return 0.0257 * (T / 293.15) ** 0.82


def p_burn(a, Tmax, eps=0.9, T0=293.15):
    """Absorbed power that holds the particle at Tmax: Kirchhoff-transformed conduction (k(T) power law) plus grey
    radiation, no temperature-jump correction (gives a slightly larger P_burn than a jump-corrected model)."""
    Ts = np.linspace(T0, Tmax, 2001)
    kint = np.trapezoid(k_air(Ts), Ts)
    return 4 * np.pi * a * kint + eps * 5.670374e-8 * 4 * np.pi * a * a * (Tmax ** 4 - T0 ** 4)


def f_per_watt(a, kp, j1A=0.5, C_ph=0.85, T=293.15):
    """Continuum (Kn << 1) Delta-T photophoretic force per absorbed watt, F = 9 pi mu^2 a I J1 / (2 rho T (kp + 2 kg)),
    J1 = j1A * A, P_abs = A pi a^2 I (Yalamov/Reed form; no slip corrections). C_ph = 0.85 as the bench model."""
    rho_g = P_ATM * M_AIR / (R_U * T)
    return C_ph * 9 * mu_sutherland(T) ** 2 * j1A / (2 * rho_g * T * (kp + 2 * k_air(T)) * a)


def v_draw(a, rho_p, C_opt, kp=0.1, Tmax=700.0, eta=0.4, A=0.9):
    """Top lateral speed of a gravity-levitated sphere: eta (C - 1) v_settle with C = min(C_opt, P_burn / P_lev); drag
    at the film temperature of the particle absorbing C P_lev (viscosity AND slip), temperature from a simple
    conduction + radiation balance."""
    m = 4 / 3 * math.pi * a ** 3 * rho_p
    P_lev = m * G / f_per_watt(a, kp)
    Pb = p_burn(a, Tmax)
    C = min(C_opt, Pb / P_lev)
    if C <= 1:
        return 0.0, Pb / P_lev, 293.15
    lo, hi = 293.15, Tmax + 1
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if p_burn(a, mid) < C * P_lev else (lo, mid)
    Tp = lo
    Tf = 0.5 * (293.15 + Tp)
    v_cold = eta * (C - 1) * v_settle(a, rho_p)
    corr = (mu_sutherland(293.15) / mu_sutherland(Tf)) * (cunningham_ar(a, Tf) / cunningham_ar(a, 293.15))
    return v_cold * corr, Pb / P_lev, Tp


def part_C(profile=None):
    print("\n=== C. levitated drawing speed ===")
    out = {}
    a, rho = 2.5e-6, 400.0
    vs = v_settle(a, rho)
    out["v_settle_mm_s"] = vs * 1e3
    out["cunningham_293K"] = cunningham_ar(a, 293.15)
    print(f"  5 um hollow carbon-coated glass (rho 400): v_settle {vs * 1e3:.3f} mm/s (Cunningham {cunningham_ar(a, 293.15):.4f},"
          f" mfp {mfp_ce(293.15) * 1e9:.1f} nm)")
    rows = []
    for C in (2.7, 6.8, 20.7, 80, 300, 1000, 2500):
        v, cap, Tp = v_draw(a, rho, C)
        rows.append(dict(C=C, v_mm_s=v * 1e3, burn_cap=cap, T_particle_K=Tp))
        print(f"    C {C:6.1f}: v = {v * 1e3:8.2f} mm/s  (burn cap C {cap:7.0f}, particle at {Tp:6.1f} K at the wall)")
    out["hollow_5um"] = rows
    # temperature corrections at the burn limit
    Tmax = 700.0
    Tf = 0.5 * (293.15 + Tmax)
    out["visc_ratio_at_burn"] = mu_sutherland(Tf) / mu_sutherland(293.15)
    out["slip_ratio_at_burn"] = cunningham_ar(a, Tf) / cunningham_ar(a, 293.15)
    print(f"  at the burn limit (700 K, film {Tf:.0f} K): viscosity x{out['visc_ratio_at_burn']:.3f}, slip x"
          f"{out['slip_ratio_at_burn']:.3f} -> speed x{out['slip_ratio_at_burn'] / out['visc_ratio_at_burn']:.3f}")
    # contrast needed for 0.3 m/s
    Cneed = 0.3 / (0.4 * vs) + 1
    out["C_needed_0p3"] = Cneed
    print(f"  contrast needed for 0.3 m/s at 293 K drag: {Cneed:.0f}")
    # heavier spheres: v = eta (min(C_opt, C_burn) - 1) v_settle; at C_opt >= C_burn this equals the burn-limited,
    # axially-balanced bound eta * fpw * P_burn / drag (independent of weight). Physically paired (rho, k_p, T_max);
    # 'margin 2' keeps the wall absorption at half the burn power.
    mats = [("hollow glass + C skin", 400, 0.1, 700.0), ("black polymer", 1100, 0.25, 373.0),
            ("solid glass + C skin", 2500, 1.1, 700.0), ("glassy carbon", 1500, 6.3, 900.0)]
    out["heavier"] = []
    for C_opt in (20.7, 80.0):
        for mname, rho_p, kp, Tm in mats:
            for margin in (1.0, 2.0):
                best = (0.0, None, None)
                for a_ in np.geomspace(1.5e-6, 40e-6, 60):
                    m = 4 / 3 * math.pi * a_ ** 3 * rho_p
                    cb = p_burn(a_, Tm) / (m * G / f_per_watt(a_, kp))
                    C = min(C_opt, cb / margin)
                    v, _, _ = v_draw(a_, rho_p, C, kp=kp, Tmax=Tm)
                    if v > best[0]:
                        best = (v, a_, cb)
                out["heavier"].append(dict(C_opt=C_opt, material=mname, margin=margin, v_m_s=best[0],
                                           d_um=None if best[1] is None else 2 * best[1] * 1e6, burn_cap=best[2]))
                print(f"  C_opt {C_opt:5.1f}, {mname:22s} (rho {rho_p}, kp {kp}, Tmax {Tm:.0f} K), burn margin {margin:.0f}: "
                      f"best levitated speed {best[0]:.3f} m/s at d = {2 * best[1] * 1e6:5.1f} um (burn cap there {best[2]:.0f})")
    # burn-limited (axially balanced) bound for the 5 um hollow sphere
    fpw = f_per_watt(a, 0.1)
    Pb = p_burn(a, 700.0)
    v_bal = 0.4 * fpw * Pb * cunningham_ar(a, Tf) / (6 * math.pi * mu_sutherland(Tf) * a)
    out["v_balanced_burn_limited_m_s"] = v_bal
    out["P_lev_nW"] = 4 / 3 * math.pi * a ** 3 * rho * G / fpw * 1e9
    print(f"  5 um hollow sphere: P_lev {out['P_lev_nW']:.1f} nW absorbed, P_burn {Pb * 1e3:.3f} mW, burn-limited "
          f"(axially balanced) bound eta fpw P_burn / drag = {v_bal:.2f} m/s")
    # gradient-force estimate of the lateral efficiency from the computed pocket profile
    if profile is not None:
        r0 = np.array(profile["r0_um"]) * 1e-6
        P = np.array(profile["P"])
        iw = int(np.argmax(P[: np.searchsorted(r0, 30e-6)]))
        dP = np.gradient(P, r0)
        Fmax = 3 / 8 * a * np.max(dP[: iw + 1])
        eta_eq = Fmax / (P[iw] - P[0])
        out["eta_gradient_model"] = float(eta_eq)
        print(f"  lateral force from the (3/8) a dI/dx linear-gradient law on the computed w = 3 mm pocket: "
              f"F_lat,max = {Fmax / P[0]:.2f} x weight vs eta (C-1) = {0.4 * (P[iw] / P[0] - 1):.2f} x weight "
              f"-> equivalent eta {eta_eq:.2f}")
    return out


# ============================================================================================ D. retro-reflection
def Pf(d):
    return np.array([[1.0, d], [0.0, 1.0]])


def Pb(d):
    return np.array([[1.0, -d], [0.0, 1.0]])


def Lf(f):
    return np.array([[1.0, 0.0], [-1.0 / f, 1.0]])


def Lb(f):
    return np.array([[1.0, 0.0], [1.0 / f, 1.0]])


CC = np.array([[-1.0, 0.0], [0.0, 1.0]])        # point inversion through the vertex, lab-frame slope unchanged
FM = np.array([[1.0, 0.0], [0.0, -1.0]])        # flat mirror normal to the axis


def round_trip(f, e, reflector, delta=0.0):
    """Lab-frame (x, dx/dz) map from the plane z = 0 (trap plane, L2's front focal plane is at z = -delta... i.e. L2
    sits at z = f + delta) back to z = 0, reflector at L2's back focal plane + e."""
    d1 = f + delta
    return Pb(d1) @ Lb(f) @ Pb(f + e) @ reflector @ Pf(f + e) @ Lf(f) @ Pf(d1)


def return_focus(M, x0, zt=0.0):
    """Rays from the point (x0, zt) with slopes th: at z = 0 they are at x0 - th zt; after the round trip
    x' = M00 x + M01 th, th' = M10 x + M11 th; return ray x(z) = x' + th' z. Find z where x is independent of th."""
    # x(z) = M00 (x0 - th zt) + M01 th + z (M10 (x0 - th zt) + M11 th); d/dth = -M00 zt + M01 + z(-M10 zt + M11) = 0
    z = (M[0, 0] * zt - M[0, 1]) / (M[1, 1] - M[1, 0] * zt)
    x = M[0, 0] * x0 + z * M[1, 0] * x0
    chief = M[1, 0] * x0                               # return slope of the forward telecentric chief ray (th = 0)
    return z, x, chief


def refract3(d, nrm, eta):
    cosi = -np.sum(nrm * d, axis=-1, keepdims=True)
    k = 1 - eta * eta * (1 - cosi * cosi)
    return eta * d + (eta * cosi - np.sqrt(k)) * nrm


def cube_normals():
    """Three orthonormal mirror normals with n . z = 1/sqrt(3) (cube axis along z)."""
    nz = 1 / math.sqrt(3)
    nt = math.sqrt(2 / 3)
    return np.array([[nt * math.cos(t), nt * math.sin(t), nz] for t in (0.3, 0.3 + 2 * math.pi / 3, 0.3 + 4 * math.pi / 3)])


def corner_cube(p, d, V, NRM, fresnel=None):
    """Ideal hollow corner cube (infinite faces) with vertex V; reflect each ray until it leaves. Optionally returns the
    3x3 polarisation ray-tracing matrices (Chipman) built from complex Fresnel coefficients fresnel(cos_i) -> (rs, rp)."""
    p, d = p.copy(), d.copy()
    Pm = np.repeat(np.eye(3)[None], len(p), axis=0).astype(complex)
    for _ in range(3):
        dn = d @ NRM.T                                         # (N, 3)
        t = -((p - V) @ NRM.T) / np.where(dn > 1e-15, dn, np.nan)
        t = np.where(t > 1e-12, t, np.inf)
        j = np.argmin(t, axis=1)
        tt = t[np.arange(len(p)), j][:, None]
        n = NRM[j]
        p = p + tt * d
        dout = d - 2 * np.sum(d * n, axis=1, keepdims=True) * n
        if fresnel is not None:
            cosi = np.abs(np.sum(d * n, axis=1))
            rs, rp = fresnel(cosi)
            s = np.cross(d, n)
            s /= np.linalg.norm(s, axis=1, keepdims=True)
            pin = np.cross(d, s)
            pout = np.cross(dout, s)
            Pi = (rs[:, None, None] * s[:, :, None] * s[:, None, :] + rp[:, None, None] * pout[:, :, None] * pin[:, None, :]
                  + dout[:, :, None] * d[:, None, :])
            Pm = Pi @ Pm
        d = dout
    return p, d, Pm


def trace_L2_forward(p, d, z_flat, n=N_GLASS, R=R_CURV, tc=T_C):
    """Flat face at z_flat facing the trap, convex face (vertex z_flat + tc) facing the reflector."""
    t = (z_flat - p[:, 2:3]) / d[:, 2:3]
    p = p + t * d
    d = refract3(d, np.array([0.0, 0.0, -1.0]), 1 / n)
    C = np.array([0.0, 0.0, z_flat + tc - R])
    q = p - C
    b = np.sum(q * d, axis=1, keepdims=True)
    c = np.sum(q * q, axis=1, keepdims=True) - R * R
    t = -b + np.sqrt(b * b - c)
    p = p + t * d
    nrm = -(p - C) / R
    return p, refract3(d, nrm, n)


def trace_L2_back(p, d, z_flat, n=N_GLASS, R=R_CURV, tc=T_C):
    C = np.array([0.0, 0.0, z_flat + tc - R])
    q = p - C
    b = np.sum(q * d, axis=1, keepdims=True)
    c = np.sum(q * q, axis=1, keepdims=True) - R * R
    t = -b - np.sqrt(b * b - c)
    p = p + t * d
    d = refract3(d, (p - C) / R, 1 / n)
    t = (z_flat - p[:, 2:3]) / d[:, 2:3]
    p = p + t * d
    return p, refract3(d, np.array([0.0, 0.0, 1.0]), n)


def best_focus(p, d):
    """Least-squares point closest to all rays (3D)."""
    A = np.zeros((3, 3))
    b = np.zeros(3)
    for pi, di in zip(p, d):
        Mi = np.eye(3) - np.outer(di, di)
        A += Mi
        b += Mi @ pi
    return np.linalg.solve(A, b)


def exact_retro(x0, e, reflector="cube", NA=0.06, nr=12, nphi=24, f_mode="paraxial", delta=0.0):
    f = R_CURV / (N_GLASS - 1)
    z_flat = f - T_C / N_GLASS + delta                    # trap point at L2's front focal point (flat side toward it)
    zv = z_flat + T_C + f + e                             # back focal point is f past the convex vertex
    rr = np.sqrt((np.arange(nr) + 0.5) / nr) * NA
    ph = np.arange(nphi) * 2 * np.pi / nphi
    S, PH = np.meshgrid(rr, ph, indexing="ij")
    sx, sy = (S * np.cos(PH)).ravel(), (S * np.sin(PH)).ravel()
    d = np.stack([sx, sy, np.sqrt(1 - sx ** 2 - sy ** 2)], axis=1)
    p = np.tile([x0, 0.0, 0.0], (len(d), 1))
    p, d = trace_L2_forward(p, d, z_flat)
    t = (zv - 40e-3 - p[:, 2:3]) / d[:, 2:3]
    p = p + t * d
    if reflector == "cube":
        p, d, _ = corner_cube(p, d, np.array([0.0, 0.0, zv]), cube_normals())
    else:
        t = (zv - p[:, 2:3]) / d[:, 2:3]
        p = p + t * d
        d = d * np.array([1.0, 1.0, -1.0])
    p, d = trace_L2_back(p, d, z_flat)
    t = (0.0 - p[:, 2:3]) / d[:, 2:3]
    pz0 = p + t * d
    bf = best_focus(p, d)
    chief_tilt = float(np.mean(d[:, 0] / -d[:, 2]))     # mean lab-frame dx/dz of the return cone... sign: travelling -z
    return dict(x_at_trap_plane_um=float(np.mean(pz0[:, 0]) * 1e6), rms_at_trap_plane_um=float(np.sqrt(np.mean(
        (pz0[:, 0] - np.mean(pz0[:, 0])) ** 2 + pz0[:, 1] ** 2)) * 1e6), best_focus_um=(bf * 1e6).tolist(),
        return_cone_axis_mrad=float(np.mean(d[:, 0] / d[:, 2])) * 1e3)


def fresnel_factory(N):
    def fr(cosi):
        sin2 = 1 - cosi ** 2
        cost = np.sqrt(1 - sin2 / N ** 2 + 0j)
        rs = (cosi - N * cost) / (cosi + N * cost)
        rp = (N * cosi - cost) / (N * cosi + cost)
        return rs, rp
    return fr


def cube_isolation(N, label, n_pts=4000, seed=1):
    """Laser polarised along x, PBS passes x and dumps y, QWP fast axis at 45 deg passed twice, ideal cube in between
    (beam along +z, return along -z). Fraction of the returned power that the PBS sends back toward the laser."""
    rng = np.random.default_rng(seed)
    r = 8e-3 * np.sqrt(rng.random(n_pts))
    t = 2 * np.pi * rng.random(n_pts)
    p = np.stack([r * np.cos(t), r * np.sin(t), np.full(n_pts, -40e-3)], axis=1)
    d = np.tile([0.0, 0.0, 1.0], (n_pts, 1))
    _, dout, Pm = corner_cube(p, d, np.zeros(3), cube_normals(), fresnel=fresnel_factory(N))
    # QWP (fast axis 45 deg) in lab x-y; same lab matrix in both directions for a linear retarder
    c = 1 / math.sqrt(2)
    Rm = np.array([[c, -c], [c, c]])
    Q = Rm @ np.diag([1, 1j]) @ Rm.T
    Ein = Q @ np.array([1.0, 0.0])
    E3 = np.concatenate([Ein, [0.0]])
    Eo = (Pm @ E3)[:, :2]                                   # return field, lab x-y
    Eq = Eo @ Q.T
    back = np.abs(Eq[:, 0]) ** 2
    tot = np.sum(np.abs(Eo) ** 2, axis=1)
    refl = float(np.mean(tot))
    leak = float(np.sum(back) / np.sum(tot))
    # on-axis return-focus intensity relative to a polarisation-uniform return (coherent sum over the six sectors)
    strehl_circ = float(np.sum(np.abs(np.mean(Eo, axis=0)) ** 2) / np.mean(tot))
    Elin = (Pm @ np.array([1.0, 0.0, 0.0]))[:, :2]
    strehl_lin = float(np.sum(np.abs(np.mean(Elin, axis=0)) ** 2) / np.mean(np.sum(np.abs(Elin) ** 2, axis=1)))
    print(f"    {label:34s}: cube reflectance {refl:.3f}, fraction of the return sent back to the laser by the PBS "
          f"{leak:.3f} ({-10 * math.log10(max(leak, 1e-12)):.1f} dB isolation); on-axis return-focus factor from the "
          f"sector polarisation: circular in {strehl_circ:.3f}, linear in {strehl_lin:.3f}")
    return dict(reflectance=refl, leak=leak, strehl_circular=strehl_circ, strehl_linear=strehl_lin)


def part_D():
    print("\n=== D. retro-reflection geometry ===")
    out = {}
    f = 0.1
    for name, refl in (("corner cube", CC), ("flat mirror", FM)):
        for e in (0.0, 5e-3, 20e-3):
            M = round_trip(f, e, refl)
            z, x, ch = return_focus(M, 5e-3)
            out[f"{name}_e{e * 1e3:g}mm"] = dict(M=M.tolist(), return_focus_z_mm=z * 1e3, return_x_mm=x * 1e3,
                                                  return_chief_slope_mrad=ch * 1e3)
            print(f"  {name:11s} e = {e * 1e3:4.0f} mm: M = [[{M[0, 0]:+.3f}, {M[0, 1]:+.4f}], [{M[1, 0]:+.4f}, {M[1, 1]:+.3f}]]"
                  f"  trap x0 = 5 mm -> return focus x = {x * 1e3:+.4f} mm at z = {z * 1e3:+.4f} mm, return cone axis "
                  f"slope {ch * 1e3:+.3f} mrad")
    # trap displaced axially from L2's front focal plane (delta), cube at BFP
    for zt in (0.2e-3, -0.5e-3):
        M = round_trip(f, 0.0, CC)
        z, x, ch = return_focus(M, 5e-3, zt=zt)
        print(f"  corner cube, trap {zt * 1e3:+.1f} mm from L2's front focal plane: return focus at z = {z * 1e3:+.3f} mm "
              f"(mirror image), x = {x * 1e3:+.4f} mm")
        out[f"cube_trap_offset_{zt * 1e3:g}mm"] = dict(z_mm=z * 1e3, x_mm=x * 1e3)
    M = round_trip(f, 10e-3, CC)
    z, x, ch = return_focus(M, 5e-3, zt=0.3e-3)
    print(f"  corner cube e = 10 mm and trap +0.3 mm: return focus z = {z * 1e3:+.4f} mm, x = {x * 1e3:+.5f} mm "
          f"(second-order lateral error {abs(x - 5e-3) * 1e6:.2f} um)")
    print("  exact 3D trace: real LA1509 as L2 (flat side to the trap), ideal hollow cube, telecentric cone from the trap")
    ex = {}
    for NA in (0.01, 0.047):
        for refl in ("cube", "flat"):
            for x0 in (0.0, 2e-3, 5e-3):
                for e in (0.0, 20e-3):
                    if refl == "flat" and e:
                        continue
                    r = exact_retro(x0, e, refl, NA=NA)
                    ex[f"NA{NA:g}_{refl}_x{x0 * 1e3:g}_e{e * 1e3:g}"] = r
                    print(f"    NA {NA:5.3f} {refl:4s} x0 {x0 * 1e3:3.0f} mm e {e * 1e3:3.0f} mm: mean return x at trap "
                          f"plane {r['x_at_trap_plane_um']:+10.2f} um, rms {r['rms_at_trap_plane_um']:6.2f} um, best "
                          f"focus (x {r['best_focus_um'][0]:+8.1f}, z {r['best_focus_um'][2]:+7.1f}) um, return cone "
                          f"axis {r['return_cone_axis_mrad']:+.3f} mrad")
    out["exact"] = ex
    print("  polarisation through QWP-cube-QWP into a PBS (galvo mirrors ideal):")
    pol = {}
    pol["perfect_conductor"] = cube_isolation(1e6j, "hollow, perfect conductor")
    pol["Al_405"] = cube_isolation(0.49 + 4.86j, "hollow, bare Al (n = 0.49 + 4.86i)")
    pol["TIR_BK7"] = cube_isolation(1 / N_GLASS, "solid N-BK7, uncoated TIR")
    out["polarisation"] = pol
    return out


# ================================================================ E. beyond the claims: scanning, decenter, astigmatism
def trace3_flat_first(p, d, n=N_GLASS, R=R_CURV, tc=T_C, z0=0.0):
    """3D vector trace through the plano-convex lens, flat face at z0 facing the beam. Returns exit point, direction,
    optical path from the start points."""
    t = (z0 - p[:, 2:3]) / d[:, 2:3]
    opl = t[:, 0].copy()
    p = p + t * d
    d = refract3(d, np.array([0.0, 0.0, -1.0]), 1 / n)
    C = np.array([0.0, 0.0, z0 + tc - R])
    q = p - C
    b = np.sum(q * d, axis=1, keepdims=True)
    c = np.sum(q * q, axis=1, keepdims=True) - R * R
    t = -b + np.sqrt(b * b - c)
    opl += n * t[:, 0]
    p = p + t * d
    return p, refract3(d, -(p - C) / R, n), opl


def pupil_2d(w, theta=0.0, stop="ffp", decenter=0.0, extra=None, nu=241, ds=8e-4):
    """Exact 3D trace of a collimated Gaussian beam (1/e^2 radius w) tilted by theta about y, pivoting about the stop
    (front focal point = telecentric galvo, or the lens's flat face), optionally shifted by `decenter` (lens decenter).
    extra(u, v) adds an input wavefront (m), u along the tilt plane. Returns the angular spectrum on a regular
    (sx, sy) grid: amplitude, phase k*T with T the 3D angle characteristic about F (chief ray x paraxial focal plane)."""
    from scipy.interpolate import griddata
    f = R_CURV / (N_GLASS - 1)
    zs = -(f - T_C / N_GLASS) if stop == "ffp" else 0.0
    S = np.array([decenter, 0.0, zs])
    din = np.array([math.sin(theta), 0.0, math.cos(theta)])
    eu = np.array([math.cos(theta), 0.0, -math.sin(theta)])
    ev = np.array([0.0, 1.0, 0.0])
    uu = np.linspace(-3.4 * w, 3.4 * w, nu)
    U, V = np.meshgrid(uu, uu, indexing="ij")
    P0 = S[None, :] + U.ravel()[:, None] * eu + V.ravel()[:, None] * ev - 0.02 * din
    D0 = np.tile(din, (P0.shape[0], 1))
    P, E, opl = trace3_flat_first(P0, D0)
    if extra is not None:
        opl = opl + extra(U.ravel(), V.ravel())
    ic = (nu // 2) * nu + nu // 2
    zF = paraxial_focus("flat_first")
    tF = (zF - P[ic, 2]) / E[ic, 2]
    F = P[ic] + tF * E[ic]
    T = opl + np.sum((F[None, :] - P) * E, axis=1)
    amp_in = np.exp(-(U ** 2 + V ** 2) / w ** 2)
    sx, sy = E[:, 0].reshape(nu, nu), E[:, 1].reshape(nu, nu)
    du = uu[1] - uu[0]
    jac = np.abs(np.gradient(sx, du, axis=0) * np.gradient(sy, du, axis=1)
                 - np.gradient(sx, du, axis=1) * np.gradient(sy, du, axis=0))
    A = amp_in / np.sqrt(jac)
    sxc, syc = sx.flat[ic], sy.flat[ic]
    half = 1.02 * max(np.max(np.abs(sx - sxc)), np.max(np.abs(sy - syc)))
    g = np.arange(-half, half + ds / 2, ds)
    GX, GY = np.meshgrid(sxc + g, syc + g, indexing="ij")
    pts = np.stack([sx.ravel(), sy.ravel()], axis=1)
    Tg = griddata(pts, T - T[ic], (GX, GY), method="cubic")
    Ag = griddata(pts, A.ravel(), (GX, GY), method="cubic")
    m = np.isfinite(Tg) & np.isfinite(Ag)
    Ag = np.where(m, Ag, 0.0)
    Tg = np.where(m, Tg, 0.0)
    return dict(sx=sxc + g, sy=syc + g, A=Ag, T=Tg, F=F, chief=E[ic])


def field_2d(pp, z, xi, yi):
    """U(F + (x_c(z) + xi, yi, z)) = sum A exp(i k (T + sx x + sy y + sz z)), x_c following the chief ray."""
    SX, SY = np.meshgrid(pp["sx"], pp["sy"], indexing="ij")
    SZ = np.sqrt(1 - SX ** 2 - SY ** 2)
    ch = pp["chief"]
    xc, yc = ch[0] / ch[2] * z, ch[1] / ch[2] * z
    G = pp["A"] * np.exp(1j * K0 * (pp["T"] + (SZ - ch[2]) * z + (SX - ch[0]) * xc + (SY - ch[1]) * yc))
    Ex = np.exp(1j * K0 * np.outer(xi, pp["sx"] - ch[0]))
    Ey = np.exp(1j * K0 * np.outer(yi, pp["sy"] - ch[1]))
    return Ex @ G @ Ey.T


def disc_average_fft(I, dx, a):
    n = I.shape[0]
    q = 2 * np.pi * np.fft.fftfreq(n, dx)
    QX, QY = np.meshgrid(q, q, indexing="ij")
    Q = np.sqrt(QX ** 2 + QY ** 2)
    with np.errstate(invalid="ignore", divide="ignore"):
        D = np.where(Q > 0, 2 * np.pi * a * j1(Q * a) / np.where(Q > 0, Q, 1), np.pi * a * a)
    return np.real(np.fft.ifft2(np.fft.fft2(I) * D / (dx * dx))) * dx * dx


def escape_contrast(P, dx, rsearch=20e-6, rdom=24e-6, nmin=12):
    """2D pocket: every local minimum (9x9-pixel window) within rsearch of the window centre is a
    candidate; its barrier is the lowest level at which the sub-level set connected to it reaches a circle of radius
    rdom around it. Returns the best (barrier/min, min idx); (1.0, centre) if there is no interior local minimum."""
    from scipy import ndimage
    n = P.shape[0]
    c = n // 2
    X = (np.arange(n) - c) * dx
    XX, YY = np.meshgrid(X, X, indexing="ij")
    R = np.hypot(XX, YY)
    loc = (P == ndimage.minimum_filter(P, size=9)) & (R <= rsearch)
    cand = np.argwhere(loc)
    if len(cand) == 0:
        return 1.0, (c, c)
    cand = cand[np.argsort(P[cand[:, 0], cand[:, 1]])][:nmin]
    best = (1.0, (c, c))
    for i, j in cand:
        pmin = P[i, j]
        rd = min(rdom, X[-1] - 3e-6 - R[i, j])
        if rd < 8e-6:
            continue
        dom = np.hypot(XX - XX[i, j], YY - YY[i, j]) <= rd
        edge = dom & ~ndimage.binary_erosion(dom)
        lo, hi = pmin, float(np.max(P[dom]))
        for _ in range(40):
            mid = math.sqrt(lo * hi) if lo > 0 else 0.5 * (lo + hi)
            lab, _ = ndimage.label((P <= mid) & dom)
            L = lab[i, j]
            if L and np.any((lab == L) & edge):
                hi = mid
            else:
                lo = mid
        if hi / pmin > best[0]:
            best = (hi / pmin, (int(i), int(j)))
    return best


def scan_pocket(pp, zrel, a=2.5e-6, half=48e-6, dx=0.25e-6):
    xi = np.arange(-half, half + dx / 2, dx)
    best = (0.0, None, None)
    rows = []
    for z in zrel:
        I = np.abs(field_2d(pp, z, xi, xi)) ** 2
        P = disc_average_fft(I, dx, a)
        con, (i, j) = escape_contrast(P, dx)
        rows.append((z, con, P[i, j], i, j))
    rows = np.array(rows, dtype=float)
    # axial stability: intercept at the pocket minimum must fall downstream
    dP = np.gradient(rows[:, 2], rows[:, 0])
    ok = (rows[:, 1] >= 1.05) & (dP < 0)
    if ok.any():
        k = int(np.argmax(np.where(ok, rows[:, 1], 0)))
        best = (float(rows[k, 1]), float(rows[k, 0]), (float((rows[k, 3] - len(xi) // 2) * dx), float((rows[k, 4] - len(xi) // 2) * dx)))
    return best, rows


def part_E(quick=False):
    print("\n=== E. off-axis / misalignment: exact 3D trace + 2D angular spectrum (flat first, w = 3 mm) ===")
    w = 3e-3
    f = R_CURV / (N_GLASS - 1)
    h99 = w * math.sqrt(math.log(100) / 2)
    zrel = np.arange(-0.86e-3, -0.66e-3 + 1e-9, (6e-6 if quick else 3e-6))
    out = {}
    cases = [("on axis (validation vs part B)", dict())]
    for A_ in (0.05, 0.1, 0.2, 0.4):
        cases.append((f"input astigmatism {A_:.2f} waves (rho^2 cos 2phi at h99)",
                      dict(extra=(lambda A_: lambda u, v: A_ * LAM * (u * u - v * v) / h99 ** 2)(A_))))
    for A_ in (0.1, 0.2, 0.4):
        cases.append((f"input coma {A_:.2f} waves (rho^3 cos phi at h99)",
                      dict(extra=(lambda A_: lambda u, v: A_ * LAM * (u * u + v * v) * u / h99 ** 3)(A_))))
    for dc_ in (0.1e-3, 0.3e-3):
        cases.append((f"lens decentered {dc_ * 1e3:.1f} mm (beam on axis)", dict(decenter=dc_)))
    for xt in (0.25e-3, 0.5e-3, 1e-3, 2e-3):
        cases.append((f"scan, galvo at front focal point (telecentric), trap at {xt * 1e3:.2f} mm",
                      dict(theta=math.atan(xt / f), stop="ffp")))
        cases.append((f"scan, galvo at the lens, trap at {xt * 1e3:.2f} mm", dict(theta=math.atan(xt / f), stop="lens")))
    # galvo pivot s before the flat face == chief ray through (s tan(theta), 0, 0) at the face
    for sp in (15e-3, 25e-3, 35e-3, 50e-3, 70e-3):
        th = math.atan(2e-3 / f)
        cases.append((f"scan, galvo pivot {sp * 1e3:.0f} mm before lens, trap at 2.00 mm",
                      dict(theta=th, stop="lens", decenter=sp * math.tan(th))))
    for xt in (3e-3, 4e-3, 5e-3):
        th = math.atan(xt / f)
        cases.append((f"scan, galvo pivot 30 mm before lens, trap at {xt * 1e3:.2f} mm",
                      dict(theta=th, stop="lens", decenter=30e-3 * math.tan(th))))
    for name, kw in cases:
        t0 = time.time()
        pp = pupil_2d(w, **kw)
        (con, z, xy), rows = scan_pocket(pp, zrel)
        out[name] = dict(contrast=con, z_mm=None if z is None else z * 1e3, offset_um=None if xy is None else
                         [v * 1e6 for v in xy], max_any=float(np.max(rows[:, 1])))
        zs_ = "  --  " if z is None else f"{z * 1e3:+.4f}"
        print(f"  {name:62s}: best stable 2D contrast {con:6.2f} at z {zs_} mm (max any {np.max(rows[:, 1]):6.2f})"
              f"  [{time.time() - t0:.0f} s]")
    return out


def part_F():
    """Guide claim: 'a 6 mm beam (w = 3 mm) also fits standard 7 mm galvo mirrors'. The pocket is made by the phase
    of rays out to and beyond the 1 % radius (4.55 mm); a 7 mm aperture cuts at 3.5 mm, where the intensity is
    exp(-2 (3.5/3)^2) = 6.6 % of peak (6.6 % of the power is lost)."""
    print("\n=== F. beam clipped by the galvo mirror aperture (flat first, w = 3 mm; aperture modelled at the lens) ===")
    out = {}
    for clip in (3.5e-3, 4.0e-3, 5.0e-3):
        res, _ = run_config("flat_first", 3e-3, clip=clip)
        keep = {k: v for k, v in res.items() if k not in ("z_mm", "contrast", "dP0dz_sign", "wall_um", "profile_best")}
        out[f"aperture_diam_{2 * clip * 1e3:g}mm"] = keep
        print(f"  aperture diameter {2 * clip * 1e3:4.1f} mm: best stable contrast "
              f"{res.get('best_contrast_fine', res.get('best_contrast', float('nan'))):6.2f} at "
              f"{res.get('best_z_fine_mm', res.get('best_z_mm', float('nan'))):+.4f} mm (max any {res['max_contrast_any']:.2f} "
              f"at {res['max_contrast_any_z_mm']:+.3f} mm)")
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--parts", default="ABCDEF")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    results = {}
    if "A" in args.parts:
        results["A"] = part_A()
    if "B" in args.parts:
        results["B"], _ = part_B(args.quick)
    path = os.path.join(OUT, "d1b_independent_check.json")
    if set(args.parts) != set("ABCDEF") and os.path.exists(path):
        with open(path) as fh:
            old = json.load(fh)
        old.update(results)
        results = old
    if "C" in args.parts:
        prof = None
        for c in results.get("B", {}).get("configs", []):
            if c["orient"] == "flat_first" and abs(c["w_mm"] - 3) < 1e-9 and "profile_best" in c:
                prof = c["profile_best"]
        results["C"] = part_C(prof)
    if "D" in args.parts:
        results["D"] = part_D()
    if "E" in args.parts:
        results["E"] = part_E(args.quick)
    if "F" in args.parts:
        results["F"] = part_F()
    with open(path, "w") as fh:
        json.dump(results, fh, indent=1)

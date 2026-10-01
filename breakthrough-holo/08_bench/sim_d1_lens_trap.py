"""D1: can a cheap catalogue singlet make a usable photophoretic trap pocket for the DIY-2 display?

Exact meridional ray trace of a plano-convex N-BK7 lens (Thorlabs LA1509-type: f = 100 mm, R = 51.5 mm, tc = 3.6 mm,
25.4 mm diameter) at 405 nm, curved side first (normal) or flat side first ("backwards", ~4x more spherical aberration).
The wavefront error W(h) is the optical path difference on the reference sphere about the paraxial focus. The focal field
is the Debye integral U(r, z) = C * int A(s) exp(i k [W + z (cos(theta) - 1)]) J_m(k r s) s ds, with s = sin(theta),
A from energy conservation of a Gaussian input beam (1/e^2 radius w), truncated by the lens clear aperture. m = 0 for a
plain beam; m = 1 for an ideal vortex (LG01-type) phase plate in front of the lens. An optional central stop (opaque disc
on a window: a "Poisson-spot" beam) is included.

The particle feels the light it intercepts, so the intensity is averaged over the particle's cross-section (a disc of
radius a, transverse to the beam): P_int(r0, z) = power a particle centred at (r0, z) intercepts, per watt of beam.

Trap figure (vertical beam pointing UP, particle levitated: R8 says vertical photophoretic traps balance the axial push
against gravity). On the axis the particle absorbs A * P_beam * P0(z); it sits where that equals its levitation power,
so the beam power only sets the height. It is laterally held if P_int rises away from the axis to a wall P_wall, and axially
stable if P0 falls downstream (dP0/dz < 0). The lateral acceleration it withstands is g_lat = eta_lat * (P_wall/P0 - 1) g,
and its top lateral (drawing) speed is g_lat * v_settle. Burn limit: at the wall it absorbs P_lev * P_wall / P0, which must
stay below P_burn, so the useful contrast is capped at P_burn / P_lev. Depth of the pocket, i.e. contrast P_wall/P0, is
therefore the figure of merit of the optics.

Not modelled (stated, not hidden): astigmatism/tilt (breaks symmetry), polarization (NA <= 0.1, negligible), particle
shape effects (delta-alpha force), the unexplained upstream force BYU sees (R8 section 1.1), convection.
Run: python3 sim_d1_lens_trap.py [--quick]  -> results/d1_lens_trap.json, results/d1_best_map.png
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.special import j0, j1

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diy_calcs as dc  # noqa: E402

LAM = 405e-9
K = 2 * math.pi / LAM
N_BK7 = 1.5302          # N-BK7 at 404.7 nm (Schott h-line)
LENS = dict(R=51.5e-3, tc=3.6e-3, clear=0.9 * 12.7e-3)
ETA_LAT = 0.4           # same lateral efficiency as diy_calcs (BYU regime)


# ----------------------------------------------------------------------------------------------------------- ray trace
def refract(d, nrm, eta):
    """Vector Snell. d: unit direction, nrm: unit normal pointing toward the incident side, eta = n1/n2."""
    cosi = -np.dot(nrm, d)
    sin2t = eta * eta * (1 - cosi * cosi)
    return eta * d + (eta * cosi - math.sqrt(1 - sin2t)) * nrm


def trace(h, orient, R=LENS["R"], tc=LENS["tc"], n=N_BK7):
    """Collimated ray at height h from the plane z = 0 (front vertex). Returns exit point (y, z), direction (dy, dz),
    optical path length to the exit point. Coordinates as numpy [y, z]."""
    d = np.array([0.0, 1.0])
    if orient == "curved_first":
        z1 = R - math.sqrt(R * R - h * h)
        p1 = np.array([h, z1])
        nrm = (p1 - np.array([0.0, R])) / R                     # points to -z at the vertex: toward incident side
        d = refract(d, nrm, 1 / n)
        t = (tc - z1) / d[1]
        p2 = p1 + t * d
        opl = z1 + n * t
        d = refract(d, np.array([0.0, -1.0]), n)
        return p2, d, opl
    z2 = tc - R + math.sqrt(R * R - h * h)                      # flat first: no bend at the plane, then the sphere
    p2 = np.array([h, z2])
    nrm = -(p2 - np.array([0.0, tc - R])) / R                   # toward the incident (glass) side
    d = refract(d, nrm, n)
    return p2, d, n * z2


def axis_cross(p, d):
    return p[1] - p[0] * d[1] / d[0]


def pupil(orient, hs):
    """Paraxial focus zF, and for each input height h: s = sin(theta), W(h) (OPD on the reference sphere, m), LA(h)."""
    p, d, _ = trace(1e-6, orient)
    zF = axis_cross(p, d)
    Rr = zF - LENS["tc"]
    C = np.array([0.0, zF])
    opl_axis = trace(0.0, orient)[2]                            # the reference sphere passes through the back vertex
    s, W, LA = [], [], []
    for h in hs:
        p, d, opl = trace(h, orient)
        q = p - C                                               # intersect |p + t d - C| = Rr, first root t > 0
        b = np.dot(q, d)
        c = np.dot(q, q) - Rr * Rr
        t = -b - math.sqrt(b * b - c)
        W.append(opl + t - opl_axis)
        s.append(-d[0])
        LA.append(axis_cross(p, d) - zF)
    return zF, np.array(s), np.array(W), np.array(LA)


# --------------------------------------------------------------------------------------------------------- focal field
def focal_field(orient, w, zs, rs, m=0, stop=0.0, uniform=False, ideal=False, nh=1500, s_max_ideal=None, hcut=None):
    """Intensity I(z, r) in W/m^2 for 1 W of beam. ideal=True: W = 0 with s = h/f (validation). hcut: truncate the
    Gaussian input at this radius (default: the lens clear aperture)."""
    hmax = LENS["clear"] if hcut is None else min(hcut, LENS["clear"])
    hs = np.linspace(hmax / nh / 2, hmax, nh)
    dh = hs[1] - hs[0]
    if ideal:
        f = 0.1
        s = hs / f if s_max_ideal is None else hs / hmax * s_max_ideal
        W = np.zeros_like(hs)
        zF = f
    else:
        zF, s, W, _ = pupil(orient, hs)
    Iin = np.ones_like(hs) if uniform else np.exp(-2 * hs ** 2 / w ** 2)
    Iin = np.where(hs < stop, 0.0, Iin)
    dsdh = np.gradient(s, hs)
    amp = np.sqrt(Iin * hs * s * dsdh) * dh                     # A(s) s ds, in h
    norm = K * K / (2 * math.pi * np.sum(Iin * hs * dh))        # |C|^2 for 1 W (paraxial Hankel-Parseval)
    cos_t = np.sqrt(1 - s * s)
    bessel = j1 if m == 1 else j0
    out = np.empty((len(zs), len(rs)))
    for r0 in range(0, len(rs), 2000):
        J = bessel(K * np.outer(rs[r0:r0 + 2000], s))           # (Nr chunk, Nh)
        for i0 in range(0, len(zs), 64):
            zz = zs[i0:i0 + 64, None]
            g = amp[None, :] * np.exp(1j * K * (W[None, :] + zz * (cos_t[None, :] - 1)))
            U = g.real @ J.T + 1j * (g.imag @ J.T)
            out[i0:i0 + 64, r0:r0 + 2000] = norm * np.abs(U) ** 2
    return zF, out


def _cap_area(R, a, d):
    """Area of the intersection of a disc of radius R at the origin with a disc of radius a centred at distance d."""
    R = np.maximum(R, 0.0)
    out = np.where(d >= R + a, 0.0, np.pi * np.minimum(R, a) ** 2)
    part = (d < R + a) & (d > np.abs(R - a))
    with np.errstate(invalid="ignore", divide="ignore"):
        c1 = np.clip((d * d + R * R - a * a) / (2 * d * R), -1, 1)
        c2 = np.clip((d * d + a * a - R * R) / (2 * d * a), -1, 1)
        tri = np.sqrt(np.maximum((-d + R + a) * (d + R - a) * (d - R + a) * (d + R + a), 0))
        lens = R * R * np.arccos(c1) + a * a * np.arccos(c2) - 0.5 * tri
    return np.where(part, lens, out)


def disc_weights(rs, a):
    """Sparse W[r0_idx, r_idx]: area of the disc (radius a, centred at r0) inside the annulus around grid radius r,
    so P_int(r0) = sum_r I(r) W[r0, r] is exact for I piecewise constant on the annuli."""
    from scipy.sparse import csr_matrix
    dr = rs[1] - rs[0]
    edges = np.concatenate([[0.0], 0.5 * (rs[1:] + rs[:-1]), [rs[-1] + dr / 2]])
    rows, cols, vals = [], [], []
    nb = int(math.ceil(a / dr)) + 2
    for i, r0 in enumerate(rs):
        j0_, j1_ = max(0, i - nb), min(len(rs), i + nb + 1)
        A = _cap_area(edges[j0_:j1_ + 1], a, r0)
        w = np.diff(A)
        rows += [i] * len(w)
        cols += list(range(j0_, j1_))
        vals += list(w)
    return csr_matrix((vals, (rows, cols)), shape=(len(rs), len(rs)))


def lateral_pockets(Pint, zs):
    """Per z: on-axis value P0, wall P_wall (first local max of P_int(r0) away from the axis, if P_int rises from it),
    wall radius index. Returns arrays (P0, P_wall, i_wall) with P_wall = nan where the axis is not a lateral minimum."""
    P0 = Pint[:, 0]
    Pw = np.full(len(zs), np.nan)
    iw = np.zeros(len(zs), int)
    for k in range(len(zs)):
        row = Pint[k]
        if row[1] <= row[0]:
            continue
        i = 1
        while i + 1 < len(row) and row[i + 1] > row[i]:
            i += 1
        if i + 1 < len(row):
            Pw[k], iw[k] = row[i], i
    return P0, Pw, iw


def best_trap(P0, Pw, zs, cap):
    """Axially stable (dP0/dz < 0, beam up) lateral pockets; return the best by min(contrast, cap) - 1."""
    dP = np.gradient(P0, zs)
    con = np.where(np.isfinite(Pw) & (P0 > 0), Pw / np.where(P0 > 0, P0, np.inf), 0)
    ok = (con >= 1.05) & (dP < 0)
    ok[:3] = ok[-3:] = False                                    # ignore the z-window edges
    if not ok.any():
        return None
    k = int(np.argmax(np.where(ok, np.minimum(con, cap), -1.0)))
    # length of the contiguous stable run around k (axial capture range)
    lo = k
    while lo > 0 and ok[lo - 1]:
        lo -= 1
    hi = k
    while hi + 1 < len(ok) and ok[hi + 1]:
        hi += 1
    return dict(k=k, contrast=float(con[k]), z_rel_mm=float(zs[k] * 1e3), stable_run_um=float((zs[hi] - zs[lo]) * 1e6),
                run_hits_window_edge=bool(lo <= 3 or hi >= len(ok) - 4), best_at_edge=bool(k <= 4 or k >= len(ok) - 5))


def spp_focal_profile(rs, w_in, f):
    """Analytic focal-plane intensity of a Gaussian (1/e^2 radius w_in, untruncated) through an ideal charge-1 spiral
    phase plate and an ideal lens (paraxial): U(r) ~ b exp(-y) [I0(y) - I1(y)], b = k r / f, y = b^2 w_in^2 / 8.
    Normalised to 1 W numerically by the caller."""
    from scipy.special import i0e, i1e
    b = K * rs / f
    y = b * b * w_in * w_in / 8
    return (b * (i0e(y) - i1e(y))) ** 2                          # i0e = exp(-y) I0(y)


def vortex_far(w_in, v_need=0.3, zmax=60e-3, nz=24):
    """Levitation trap above the focus of a Gaussian beam through an ideal charge-1 spiral phase plate (Debye integral,
    input truncated at 2.5 w_in, sampled for the defocus phase), for every particle in PARTS, out to zmax.
    Two r grids per height: a fine one over [0, 3a] for the on-axis intercept, a coarse one (dr <= w(z)/1000) for the
    wall, where the field is smooth on the particle scale. Returns {particle: (rows, first height where v_draw >= v_need
    with the wall absorption below the burn limit)}."""
    f = LENS["R"] / (N_BK7 - 1)
    w0 = LAM * f / (math.pi * w_in)
    hcut = 2.5 * w_in
    s_c = hcut / f
    out = {p: ([], None) for p in PARTS}
    for z in np.geomspace(0.3e-3, zmax, nz):
        wz = math.hypot(w0, z * w_in / f)
        a_max = max(PARTS.values())
        r_fine = np.arange(0, 3 * a_max, a_max / 100)
        dr_c = min(min(PARTS.values()) / 25, wz / 1000) if wz < 20 * a_max else wz / 1000
        r_coarse = np.arange(0, 3 * wz + 10e-6, dr_c)
        rr = np.concatenate([r_fine, r_coarse])
        nh = int(max(3000, 25 * z * s_c * s_c / (2 * LAM) + 25 * K * rr.max() * s_c / (2 * math.pi)))
        _, I = focal_field("curved_first", w_in, np.array([z]), rr, m=1, nh=nh, hcut=hcut)
        I_f, I_c = I[0, :len(r_fine)], I[0, len(r_fine):]
        power = float(np.sum(I_c * 2 * np.pi * r_coarse) * dr_c)
        for pname, a in PARTS.items():
            fpw, P_lev, P_burn = dc.window(pname)
            A = dc.PARTICLES[pname][4]
            P0 = float((disc_weights(r_fine, a) @ I_f)[0])
            Pint_c = disc_weights(r_coarse, a) @ I_c
            Pw = float(Pint_c.max())
            con = Pw / P0
            P_beam = P_lev / (A * P0)
            g_lat = ETA_LAT * (min(con, P_burn / P_lev) - 1)
            row = dict(z_mm=z * 1e3, beam_radius_um=wz * 1e6, wall_radius_um=float(r_coarse[np.argmax(Pint_c)] * 1e6),
                       contrast=con, beam_W=float(P_beam), v_draw_m_s=float(dc.v_levitated(pname, con, ETA_LAT)),
                       wall_abs_mW=float(P_lev * con * 1e3), burns=bool(P_lev * con > P_burn), power_check=power)
            rows, hit = out[pname]
            rows.append(row)
            if hit is None and row["v_draw_m_s"] >= v_need and not row["burns"]:
                out[pname] = (rows, row)
    return out


# ---------------------------------------------------------------------------------------------------------- validation
def self_test():
    ok = True

    def chk(name, got, want, tol):
        nonlocal ok
        good = abs(got - want) <= tol * abs(want)
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'} {name}: {got:.5g} (want {want:.5g}, tol {tol:.0%})")

    print("self-test")
    # 1. Airy: uniform pupil, no aberration, NA 0.05: peak = pi NA^2 P / lam^2, first zero at v = 3.8317
    NA = 0.05
    rs = np.linspace(0, 12e-6, 1201)
    _, I = focal_field(None, 1, np.array([0.0]), rs, uniform=True, ideal=True, s_max_ideal=NA)
    chk("Airy peak / (pi NA^2/lam^2)", I[0, 0], math.pi * NA ** 2 / LAM ** 2, 0.01)
    iz = np.argmin(I[0, :int(1201 * 0.6)])
    chk("Airy first zero v", K * NA * rs[iz], 3.8317, 0.01)
    # 2. on-axis axial zero: u = k NA^2 z / 2 ... I(z) ~ sinc^2(u/4) -> first zero at z = 2 lam / NA^2 (paraxial)
    zs = np.linspace(0, 1.2 * 2 * LAM / NA ** 2, 2001)
    _, Iz = focal_field(None, 1, zs, np.array([0.0]), uniform=True, ideal=True, s_max_ideal=NA)
    chk("axial first zero z (2 lam/NA^2)", zs[np.argmin(Iz[:, 0])], 2 * LAM / NA ** 2, 0.02)
    # 3. power conservation in a defocused aberrated plane (flat first, w = 4 mm): integral I 2 pi r dr = 1 W
    rs2 = np.linspace(0, 1.5e-3, 6001)
    zF, I2 = focal_field("flat_first", 4e-3, np.array([-0.3e-3]), rs2, nh=4000)
    chk("power in plane (1 W)", float(np.sum(I2[0] * 2 * np.pi * rs2) * (rs2[1] - rs2[0])), 1.0, 0.02)
    # 4. ray trace: EFL of a plano-convex = R/(n-1) for both orientations; BFL(curved first) = f - tc/n
    f = LENS["R"] / (N_BK7 - 1)
    zc, *_ = pupil("curved_first", np.array([1e-3]))
    zf, *_ = pupil("flat_first", np.array([1e-3]))
    chk("BFL curved first (f - tc/n)", zc - LENS["tc"], f - LENS["tc"] / N_BK7, 1e-4)
    chk("BFL flat first (f)", zf - LENS["tc"], f, 1e-4)
    # 5. spherical aberration: W040 from OPD vs LA * NA^2 / 4 (small aperture), and the flat/curved ratio vs thin-lens
    #    Seidel (shape factor q = -/+1, position factor p = -1): ratio = (A + B + Cc + D) / (A - B + Cc + D)
    h = np.array([2e-3])
    for o in ("curved_first", "flat_first"):
        _, s, W, LA = pupil(o, h)
        chk(f"W040 {o}: OPD vs LA*NA^2/4", abs(W[0]), abs(LA[0]) * s[0] ** 2 / 4, 0.03)
    n = N_BK7
    A_, B_, C_, D_ = (n + 2) / (n - 1), 4 * (n + 1), (3 * n + 2) * (n - 1), n ** 3 / (n - 1)
    seidel = (A_ + B_ + C_ + D_) / (A_ - B_ + C_ + D_)
    _, _, Wc, _ = pupil("curved_first", h)
    _, _, Wf, _ = pupil("flat_first", h)
    chk("SA ratio flat/curved vs thin-lens Seidel", abs(Wf[0] / Wc[0]), seidel, 0.05)
    # 6. sign: with spherical aberration the axial intensity maximum moves from the paraxial focus toward the lens
    #    (marginal rays focus short)
    zs3 = np.linspace(-3e-3, 0.5e-3, 701)
    _, I3 = focal_field("flat_first", 4e-3, zs3, np.array([0.0]))
    _, _, _, LA3 = pupil("flat_first", np.array([4e-3]))
    good = LA3[0] < 0 and zs3[np.argmax(I3[:, 0])] < 0
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'} marginal focus short (LA {LA3[0] * 1e3:.2f} mm) and axial peak before paraxial "
          f"focus ({zs3[np.argmax(I3[:, 0])] * 1e3:.2f} mm)")
    # 7. disc average of a uniform field = pi a^2
    rs4 = np.linspace(0, 20e-6, 401)
    Lw = disc_weights(rs4, 2.5e-6)
    chk("disc average of uniform I (pi a^2), r0 = 0", float(Lw[0].sum()), math.pi * 2.5e-6 ** 2, 0.001)
    chk("disc average of uniform I (pi a^2), r0 = 10 um", float(Lw[200].sum()), math.pi * 2.5e-6 ** 2, 0.001)
    # I = r^2 (vortex core): exact P_int(r0) = pi a^2 (r0^2 + a^2 / 2)
    rs5 = np.linspace(0, 20e-6, 2001)
    Pq = disc_weights(rs5, 2.5e-6) @ (rs5 ** 2)
    for i in (0, 100, 500):
        chk(f"disc average of I = r^2 at r0 = {rs5[i] * 1e6:.0f} um", float(Pq[i]),
            math.pi * 2.5e-6 ** 2 * (rs5[i] ** 2 + 2.5e-6 ** 2 / 2), 0.01)
    # 8. Debye vortex, ideal lens (f = 100 mm, w 2 mm), vs the analytic Gaussian-through-spiral-plate focal profile.
    #    (With the real singlet the on-axis intercept differs by ~12 %: the dark core is sensitive to small aberration.)
    rs6 = np.arange(0, 40e-6, 0.05e-6)
    _, I6 = focal_field(None, 2e-3, np.array([0.0]), rs6, m=1, nh=4000, ideal=True)
    rw = np.arange(0, 3e-3, 0.05e-6)
    Iw = spp_focal_profile(rw, 2e-3, 0.1)
    Ia = spp_focal_profile(rs6, 2e-3, 0.1) / (np.sum(Iw * 2 * np.pi * rw) * (rw[1] - rw[0]))
    chk("SPP focal ring peak, Debye vs analytic", float(I6[0].max()), float(Ia.max()), 0.01)
    chk("SPP focal ring radius, Debye vs analytic", float(rs6[np.argmax(I6[0])]), float(rs6[np.argmax(Ia)]), 0.01)
    Dw = disc_weights(rs6, 2.5e-6)
    chk("SPP on-axis intercept (a = 2.5 um), Debye vs analytic", float((Dw @ I6[0])[0]), float((Dw @ Ia)[0]), 0.01)
    # 9. far-field Debye sampling: power conserved 30 mm above the focus
    far = vortex_far(2e-3, zmax=30e-3, nz=2)
    rows = far["carbon-coated hollow glass, d=5 um"][0]
    chk("vortex power in plane at 30 mm (1 W, input cut at 2.5 w)", rows[-1]["power_check"], 1 - math.exp(-12.5), 0.02)
    # 10. two-grid intercepts agree with a single fine grid at a height where both are affordable (z = 2 mm)
    zz = 2e-3
    f10 = LENS["R"] / (N_BK7 - 1)
    wz = math.hypot(LAM * f10 / (math.pi * 2e-3), zz * 2e-3 / f10)
    rs10 = np.arange(0, 3 * wz + 10e-6, 0.1e-6)
    _, I10 = focal_field("curved_first", 2e-3, np.array([zz]), rs10, m=1, nh=6000, hcut=5e-3)
    P10 = disc_weights(rs10, 2.5e-6) @ I10[0]
    far10 = vortex_far(2e-3, zmax=zz, nz=2)["carbon-coated hollow glass, d=5 um"][0][-1]   # geomspace: last = zmax
    chk("two-grid contrast vs single fine grid (z = 2 mm)", far10["contrast"], float(P10.max() / P10[0]), 0.03)
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return ok


# ----------------------------------------------------------------------------------------------------------------- run
CONFIGS = [
    dict(name="normal (curved first), w 2 mm", orient="curved_first", w=2e-3),
    dict(name="normal (curved first), w 4 mm", orient="curved_first", w=4e-3),
    dict(name="normal (curved first), w 6 mm", orient="curved_first", w=6e-3),
    dict(name="backwards (flat first), w 2 mm", orient="flat_first", w=2e-3),
    dict(name="backwards (flat first), w 3 mm", orient="flat_first", w=3e-3),
    dict(name="backwards (flat first), w 3.5 mm", orient="flat_first", w=3.5e-3),
    dict(name="backwards (flat first), w 4 mm", orient="flat_first", w=4e-3),
    dict(name="backwards (flat first), w 6 mm", orient="flat_first", w=6e-3),
    dict(name="backwards + 3 mm stop, w 4 mm", orient="flat_first", w=4e-3, stop=1.5e-3),
    dict(name="vortex plate, normal, w 2 mm", orient="curved_first", w=2e-3, m=1),
    dict(name="vortex plate, normal, w 4 mm", orient="curved_first", w=4e-3, m=1),
]
PARTS = {"carbon-coated hollow glass, d=5 um": 2.5e-6, "laser-printer toner, d~8 um": 4e-6}


def run(quick=False):
    res = []
    best_map = None
    for cfg in CONFIGS:
        hs = np.linspace(1e-5, LENS["clear"], 400)
        zF, s, W, LA = pupil(cfg["orient"], hs)
        Iin = np.exp(-2 * hs ** 2 / cfg["w"] ** 2)
        h99 = hs[np.searchsorted(-Iin, -0.01)] if Iin[-1] < 0.01 else hs[-1]
        LA99 = float(np.interp(h99, hs, LA))
        W_waves = float(np.interp(h99, hs, W) / LAM)
        NA = float(np.interp(h99, hs, s))
        zlo, zhi = min(1.3 * LA99, -0.5e-3), 1.5e-3
        nz = 300 if quick else 700
        zs = np.linspace(zlo, zhi, nz)
        rmax = min(1.3 * max(-zlo, zhi) * NA + 20e-6, 700e-6)
        dr = 0.2e-6 if quick else 0.1e-6
        rs = np.arange(0, rmax, dr)
        _, I = focal_field(cfg["orient"], cfg["w"], zs, rs, m=cfg.get("m", 0), stop=cfg.get("stop", 0.0),
                           nh=1500 if quick else 3000)
        row = dict(config=cfg["name"], NA_99=NA, LA_99_mm=LA99 * 1e3, W_99_waves=W_waves, particles={})
        for pname, a in PARTS.items():
            fpw, P_lev, P_burn = dc.window(pname)
            A = dc.PARTICLES[pname][4]
            cap = P_burn / P_lev
            Pint = (disc_weights(rs, a) @ I.T).T                  # (Nz, Nr0): W intercepted per W of beam
            P0, Pw, iw = lateral_pockets(Pint, zs)
            b = best_trap(P0, Pw, zs, cap)
            if b is None:
                row["particles"][pname] = dict(trap=False)
                continue
            k = b["k"]
            con = min(b["contrast"], cap)
            P_beam = P_lev / (A * P0[k])
            g_lat = ETA_LAT * (con - 1)
            row["particles"][pname] = dict(
                trap=True, contrast=b["contrast"], contrast_cap_burn=cap, z_rel_paraxial_mm=b["z_rel_mm"],
                axial_stable_run_um=b["stable_run_um"], run_hits_window_edge=b["run_hits_window_edge"],
                best_at_window_edge=b["best_at_edge"], wall_radius_um=float(rs[iw[k]] * 1e6),
                intercept_frac_axis=float(P0[k]), beam_power_mW=P_beam * 1e3, g_lat=g_lat,
                v_draw_max_m_s=dc.v_levitated(pname, b["contrast"], ETA_LAT), wall_abs_mW=P_lev * Pw[k] / P0[k] * 1e3, burn_abs_mW=P_burn * 1e3)
            if pname.startswith("carbon") and (best_map is None or con > best_map[0]):
                best_map = (con, cfg["name"], zs, rs, I, Pint, k)
        if cfg.get("m", 0) == 1:
            far = vortex_far(cfg["w"], nz=12 if quick else 24)
            row["vortex_far"] = {p: dict(rows=r_, first_0p3_m_s=h_) for p, (r_, h_) in far.items()}
        res.append(row)
        print(f"{cfg['name']:34s} NA {NA:.3f}  LA {LA99 * 1e3:6.2f} mm  W {W_waves:6.2f} waves")
        for pname, d in row["particles"].items():
            if not d["trap"]:
                print(f"    {pname:36s} no axially stable on-axis pocket")
                continue
            print(f"    {pname:36s} contrast {d['contrast']:9.1f} (burn cap {d['contrast_cap_burn']:7.0f})  at z "
                  f"{d['z_rel_paraxial_mm']:+6.2f} mm  run {d['axial_stable_run_um']:5.0f} um  wall r "
                  f"{d['wall_radius_um']:5.1f} um  beam {d['beam_power_mW']:9.3f} mW  g_lat {d['g_lat']:8.1f}  "
                  f"v_draw {d['v_draw_max_m_s']:6.3f} m/s")
        for pname, d in row.get("vortex_far", {}).items():
            h = d["first_0p3_m_s"]
            best = max(d["rows"], key=lambda q: q["v_draw_m_s"])
            if h:
                print(f"    far above focus, {pname:22.22s}: 0.3 m/s first reached {h['z_mm']:5.1f} mm above focus, dark "
                      f"core wall at {h['wall_radius_um']:4.0f} um, needs {h['beam_W']:6.2f} W of 405 nm (wall absorbs {h['wall_abs_mW']:.2f} mW)")
            else:
                print(f"    far above focus, {pname:22.22s}: never 0.3 m/s; best {best['v_draw_m_s']:.3f} m/s at "
                      f"{best['z_mm']:.1f} mm, {best['beam_W']:.2f} W (burn limit caps the contrast)")
    return res, best_map


def plot(best_map, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    con, name, zs, rs, I, Pint, k = best_map
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ext = [zs[0] * 1e3, zs[-1] * 1e3, -rs[-1] * 1e6, rs[-1] * 1e6]
    full = np.concatenate([I[:, ::-1], I], axis=1).T
    ax[0].imshow(np.log10(full / full.max() + 1e-6), aspect="auto", extent=ext, origin="lower", cmap="inferno",
                 vmin=-4)
    ax[0].set(title=f"log10 intensity: {name}", xlabel="z from paraxial focus (mm), beam goes ->", ylabel="r (um)")
    ax[0].axvline(zs[k] * 1e3, color="cyan", lw=0.8)
    ax[1].semilogy(rs * 1e6, Pint[k] / Pint[k].max(), label="intercepted by a 5 um particle")
    ax[1].semilogy(rs * 1e6, I[k] / I[k].max(), alpha=0.6, label="intensity")
    ax[1].set(title=f"slice at the trap point (z = {zs[k] * 1e3:+.2f} mm)", xlabel="r (um)", ylabel="relative",
              ylim=(1e-4, 1.5))
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    if not self_test():
        sys.exit(1)
    res, best_map = run(args.quick)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "d1_lens_trap.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    if best_map is not None:
        plot(best_map, os.path.join(HERE, "results", "d1_best_map.png"))
    print("wrote results/d1_lens_trap.json, results/d1_best_map.png")

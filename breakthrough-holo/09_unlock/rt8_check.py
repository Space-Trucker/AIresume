"""Red team 8: independent checks of T8 (POV-X: fast POV motes under passive Class 1 by the crossing-rate rule).

One file, one section per attack. Results go to results/rt8_<section>.json; console output is teed to
results/rt8_run.log by the caller.

Independence (owner rule: double-validate every result, including this file's):
- Written here: head geometry and LP allocation by enumeration of head triples (checked against scipy linprog and
  against m18c's hull-facet allocator), POV tour construction (greedy chaining with blanked jumps), the time-averaged
  moving-beam exposure field (each tour element is visited f_r times per second for dl/v; its beams are Gaussian with
  the Rayleigh range; capture through a disc by the m17-style closed form, checked against the exact non-central
  chi-square), a frozen 3D von Karman-Pao turbulence field by random Fourier modes (mean wind included; the mote moves
  THROUGH the field), my own PID tuner (vectorised 1D closed-loop simulation), and a vectorised tracking simulator.
- Project / RT6 / RT7 code is imported only in lines marked XCHECK.

Run: python3 rt8_check.py <section> [...]   sections: std expo loop phys chan sense table
"""
import json
import math
import os
import sys
import time
import zlib
from itertools import combinations

import numpy as np
from scipy import optimize, stats

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))
sys.path.insert(0, os.path.join(HERE, "..", "04_engineering", "holo_engine"))


def dump(name, obj):
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, f"rt8_{name}.json"), "w") as fh:
        json.dump(obj, fh, indent=1, default=float)


# ======================================================================================================================
# Shared geometry and constants (H10 heads as in RT6/M4; image volume as in m17/m18c)
# ======================================================================================================================
H10 = np.array([(0.15, 0.15, 2.7), (5.85, 0.15, 2.7), (5.85, 4.85, 2.7), (0.15, 4.85, 2.7),
                (0.15, 0.15, 0.12), (5.85, 0.15, 0.12), (5.85, 4.85, 0.12), (0.15, 4.85, 0.12),
                (3.0, 2.5, 2.75), (3.0, 2.5, 0.05)])
CENTER = np.array([3.0, 2.5, 1.3])
HALF = np.array([0.5, 0.5, 0.4])
LAM = 1.55e-6
R_AP = 1.75e-3                      # 3.5 mm limiting aperture (1400-4000 nm, t >= 10 s)
AEL_IR = 1000.0 * math.pi * R_AP ** 2   # 9.62 mW (T8 rounds to 10 mW)
TRIPLES = np.array(list(combinations(range(10), 3)))

# T8 design rows (m19 as committed in 2182f4c, results/m19_run.log): content, room, v, w_um, s', E/L mJ/m
T8_ROWS = [("sketch", "still", 0.5, 34.3, 3.0, 29.0), ("sketch", "office", 0.5, 31.0, 3.0, 23.1),
           ("sketch", "still", 0.8, 35.0, 3.0, 30.0), ("film_density", "still", 0.5, 28.0, 4.6, 18.9)]
ROOMS = {"still": (0.0, 0.03), "home": (0.05, 0.03), "quiet_office": (0.10, 0.03), "office": (0.10, 0.10)}


# ----------------------------------------------------------------------------------------------------------------------
# LP allocation by enumerating head triples (own). For a mote at x, beams push along k_j = (x - H_j)/|x - H_j|.
# min sum c_j s.t. sum c_j k_j = f, c >= 0. A basic optimal solution uses at most 3 beams, so the optimum is the
# cheapest triple whose 3x3 system has a nonnegative solution.
# ----------------------------------------------------------------------------------------------------------------------
def triple_inverses(x):
    """x: (n, 3) mote positions -> K (n, 10, 3), Minv (n, 120, 3, 3), valid (n, 120)."""
    K = x[:, None, :] - H10[None, :, :]
    K /= np.linalg.norm(K, axis=2)[:, :, None]
    M = K[:, TRIPLES, :]                                   # (n, 120, 3 beams, 3 xyz)
    M = np.transpose(M, (0, 1, 3, 2))                      # columns are the beam vectors
    det = np.linalg.det(M)
    valid = np.abs(det) > 1e-6
    M2 = np.where(valid[:, :, None, None], M, np.eye(3))
    return K, np.linalg.inv(M2), valid


def lp_alloc(f, Minv, valid):
    """f (n, 3), Minv (n, 120, 3, 3) -> C (n, 10) minimum-sum nonnegative coefficients."""
    co = (Minv @ f[:, None, :, None])[..., 0]             # (n, 120, 3)
    ok = valid & (co.min(axis=2) >= -1e-12)
    cost = np.where(ok, co.sum(axis=2), np.inf)
    best = np.argmin(cost, axis=1)
    n = f.shape[0]
    ar = np.arange(n)
    C = np.zeros((n, 10))
    C[ar[:, None], TRIPLES[best]] = np.maximum(co[ar, best], 0.0)
    bad = ~np.isfinite(cost[ar, best])
    C[bad] = np.nan
    return C


def hull_facets(K):
    """Own hull-facet enumeration from the 120 head triples (a triple is a facet if every other beam vector lies on one
    side of its plane, away from the origin). K (10, 3) -> idx (16, 3), Minv (16, 3, 3), valid (16,)."""
    idx, inv = [], []
    for t in TRIPLES:
        a, b, c = K[t]
        n = np.cross(b - a, c - a)
        if np.linalg.norm(n) < 1e-9:
            continue
        sd = (K - a) @ n
        others = np.delete(sd, t)
        if np.all(others <= 1e-12) or np.all(others >= -1e-12):
            M = K[t].T
            if abs(np.linalg.det(M)) > 1e-9:
                idx.append(t)
                inv.append(np.linalg.inv(M))
    m = len(idx)
    I = np.zeros((16, 3), int)
    V = np.zeros((16, 3, 3))
    I[:m], V[:m] = np.array(idx), np.array(inv)
    V[m:] = np.eye(3)
    ok = np.zeros(16, bool)
    ok[:m] = True
    return I, V, ok


def lp_alloc_f(f, I, V, ok):
    """Facet allocation: f (n, 3), I (n, 16, 3), V (n, 16, 3, 3), ok (n, 16) -> C (n, 10)."""
    co = (V @ f[:, None, :, None])[..., 0]
    good = ok & (co.min(axis=2) >= -1e-12)
    cost = np.where(good, co.sum(axis=2), np.inf)
    best = np.argmin(cost, axis=1)
    n = f.shape[0]
    ar = np.arange(n)
    C = np.zeros((n, 10))
    C[ar[:, None], I[ar, best]] = np.maximum(co[ar, best], 0.0)
    return C


def lp_selftest(n=300, seed=3):
    """Own allocator vs scipy linprog and vs m18c's hull-facet allocator (XCHECK)."""
    from scipy.optimize import linprog
    rng = np.random.default_rng(seed)
    x = CENTER + (rng.random((n, 3)) * 2 - 1) * HALF
    f = rng.normal(size=(n, 3))
    K, Minv, valid = triple_inverses(x)
    C = lp_alloc(f, Minv, valid)
    dev_lp, dev_res = 0.0, 0.0
    for i in range(n):
        r = linprog(np.ones(10), A_eq=K[i].T, b_eq=f[i], bounds=[(0, None)] * 10, method="highs")
        dev_lp = max(dev_lp, abs(r.fun - C[i].sum()) / max(r.fun, 1e-9))
        dev_res = max(dev_res, np.linalg.norm(C[i] @ K[i] - f[i]) / np.linalg.norm(f[i]))
    import m18c_vector_pin as m18c                          # XCHECK
    dev_m18c = 0.0
    for i in range(50):
        simp, inv = m18c.facets(K[i])
        idx, c = m18c.allocate(f[i], simp, inv)
        dev_m18c = max(dev_m18c, abs(c.sum() - C[i].sum()) / C[i].sum())
    # worst LP cost over directions at the centre (RT6: h_worst 2.13-2.14 over the volume)
    D = rng.normal(size=(4000, 3))
    D /= np.linalg.norm(D, axis=1)[:, None]
    Kc, Mc, vc = triple_inverses(np.tile(CENTER, (4000, 1)))
    hc = lp_alloc(D, Mc, vc).sum(axis=1)
    return dict(dev_linprog=dev_lp, residual=dev_res, dev_m18c=dev_m18c, h_worst_centre=float(hc.max()),
                h_mean_centre=float(hc.mean()))


# ----------------------------------------------------------------------------------------------------------------------
# Gaussian capture through a disc of radius R whose centre is rho from the beam axis (1/e^2 radius wz)
# ----------------------------------------------------------------------------------------------------------------------
def frac_approx(rho2, wz2, R=R_AP):
    return (1 - np.exp(-2 * R * R / wz2)) * np.exp(-2 * rho2 / (wz2 + 2 * R * R))


def frac_exact(rho, wz, R=R_AP):
    return stats.ncx2.cdf(4 * R * R / (wz * wz), 2, 4 * rho * rho / (wz * wz))


# ======================================================================================================================
# Section std: standards arithmetic (IEC 60825-1:2014 rules 1-2 above 1400 nm, ICNIRP strict small-beam note,
# EN 50689 skin criterion, stall timing, visible rules incl. photochemical C3 at the 30 000 s display time base)
# ======================================================================================================================
def ael_1550(t):
    """Class 1 AEL at 1500-1800 nm (J for t < 10 s, W thereafter) and its limiting aperture diameter (m)."""
    if t <= 0.35:
        return 8e-3, 1e-3
    if t < 10:
        return 1.8e-2 * t ** 0.75, 1.5e-3 * t ** 0.375
    return 1e-2, 3.5e-3


def sec_std():
    out = {}
    print("== std: standards arithmetic for T8's design rows ==")
    for content, room, v, w_um, sp, EL in T8_ROWS:
        w = w_um * 1e-6
        EL = EL * 1e-3
        U, sig = ROOMS[room]
        um = {"still": 0.0479, "office": 0.185}.get(room, 0.1)
        k = (1 + um / v)
        rows = {}
        # rule 2 at every window T: energy through the aperture d(T) on a stroke = f_r s'(d) d (1+u/v) E/L T
        # (crossing chord ~ d; s' assumed the same for every aperture size: optimistic for large d, see expo)
        for T in (0.35, 1.0, 3.0, 10.0, 100.0):
            ael, d = ael_1550(T)
            E = 30.0 * sp * d * k * EL * T
            lim = ael * (T if T >= 10 else 1.0)
            rows[f"T{T}"] = dict(aperture_mm=d * 1e3, dose_mJ=E * 1e3, limit_mJ=lim * 1e3, ratio=E / lim)
        # rule 1 (single pass through 1 mm)
        e_pass = EL * 1e-3
        # ICNIRP strict (cornea > 1400 nm, beam < 1 mm, t < 0.35 s): non-averaged H on the track centre, own track only
        H_pass = math.sqrt(2 / math.pi) * EL / w
        H_035 = H_pass * 30.0 * 0.35 * k
        # EN 50689 child-appealing skin criterion (skin MPE via 1 mm, 10 s): 1000 W/m^2 x 0.785 mm^2 = 0.785 mW
        P_skin = 30.0 * 1.1 * 1e-3 * k * EL
        # stall: P_focus = E/L (v + u); time to the time-dependent AEL (1 mm <= 0.35 s, 1.5 t^0.375 mm to 10 s)
        P_foc = EL * (v + um)
        P_cap = EL * (v + U + 5.4 * sig)                       # loop at full authority (gust-peak cap)
        def t_to(P):
            f = lambda t: P * t - ael_1550(t)[0]
            return optimize.brentq(f, 1e-6, 9.99)
        out[f"{content}/{room}/{v}"] = dict(rule2=rows, E_pass_1mm_mJ=e_pass * 1e3, rule1_margin=8e-3 / e_pass,
                                            H_pass_Jm2=H_pass, H_035_Jm2=H_035, strict_margin=1e4 / H_035,
                                            P_skin_1mm_mW=P_skin * 1e3, skin_margin=0.785e-3 / P_skin,
                                            P_focus_mW=P_foc * 1e3, t_stall_s=t_to(P_foc), P_cap_mW=P_cap * 1e3,
                                            t_stall_cap_s=t_to(P_cap), t_stall_strict_ms=1e4 * math.pi * w * w / 2 /
                                            P_cap * 1e3)
        r = out[f"{content}/{room}/{v}"]
        print(f"  {content:12s} {room:7s} v {v}: rule-2 ratio at 0.35/1/3/10 s "
              + " / ".join(f"{rows[f'T{T}']['ratio']:.2f}" for T in (0.35, 1.0, 3.0, 10.0))
              + f"; rule 1 margin {r['rule1_margin']:.0f}x; ICNIRP strict H(0.35 s) {H_035:.0f} J/m^2 "
              f"(margin {r['strict_margin']:.2f}); EN 50689 skin {P_skin * 1e3:.2f} mW (margin {r['skin_margin']:.2f});"
              f" stall to AEL {r['t_stall_s']:.2f} s at P_focus {P_foc * 1e3:.1f} mW, {r['t_stall_cap_s']:.2f} s at "
              f"the authority cap {P_cap * 1e3:.1f} mW; strict-reading stall {r['t_stall_strict_ms']:.2f} ms")
    # convergence single fault: K channels of one head driven to one point (common coordinate fault)
    conv = {}
    for K_ch in (2, 5, 20, 100):
        P = K_ch * 15.9e-3
        conv[K_ch] = dict(P_W=P, t_to_8mJ_ms=8e-3 / P * 1e3)
    out["convergence_fault"] = conv
    print("  convergence fault (K stalled/converged foci at 15.9 mW): " +
          "; ".join(f"K={k}: {c['P_W'] * 1e3:.0f} mW, 8 mJ in {c['t_to_8mJ_ms']:.0f} ms" for k, c in conv.items()))
    # visible: per-pupil Class 1 at the 30 000 s display time base: thermal 0.39 mW; photochemical 3.9e-5 C3 W
    # (400-600 nm, t > 100 s) [memory; IEC Table 3], C3 = 10^(0.02 (lam - 450)) for 450-600 nm, 1 below 450 nm
    vis = {}
    for lam in (450, 470, 488, 500, 520, 532):
        C3 = 1.0 if lam <= 450 else 10 ** (0.02 * (lam - 450))
        vis[lam] = dict(photochem_uW=3.9e-5 * C3 * 1e6, thermal_uW=390.0, limit_uW=min(390.0, 3.9e-5 * C3 * 1e6))
    out["visible_limits"] = vis
    print("  visible Class 1 per pupil (30 000 s): " + "; ".join(f"{l} nm {v['limit_uW']:.0f} uW" for l, v in vis.items()))
    print("  T8 visible per pupil 35-43 uW (sketch) / 46-59 uW (film): within the 500 nm limit (390 uW) but at/over "
          "the 450 nm photochemical limit (39 uW)")
    # rule 3 (C5): 400-1400 nm retinal thermal only; C_P = 1 for alpha < 5 mrad and pulses longer than T_i (ICNIRP
    # 2013 via search snippet); a mote at >= 0.1 m subtends < 0.1 mrad, so rules 1 and 2 bind in the visible too.
    out["rule3_note"] = "C5 = 1 for alpha < 5 mrad (point source); not applied to cornea/skin or above 1400 nm"
    dump("std", out)
    return out


# ======================================================================================================================
# Section expo: time-averaged moving-beam exposure field of POV tours (LP-chosen heads vs T8's random-head s')
# ======================================================================================================================
def random_segments(S, rng, seg=0.1):
    """m17-style content: straight 10 cm segments, random orientation, inside the volume."""
    out, tot = [], 0.0
    while tot < S - 1e-9:
        while True:
            p0 = CENTER + (rng.random(3) * 2 - 1) * HALF
            d = rng.normal(size=3)
            d /= np.linalg.norm(d)
            p1 = p0 + d * seg
            if np.all(np.abs(p1 - CENTER) <= HALF):
                break
        out.append(np.array([p0, p1]))
        tot += seg
    return out


def random_arcs(S, rng):
    """RT7-style content: circular arcs of radius 3-20 cm spanning 60-300 degrees."""
    out, tot = [], 0.0
    while tot < S:
        R = rng.uniform(0.03, 0.2)
        ang = math.radians(rng.uniform(60, 300))
        c = CENTER + HALF * rng.uniform(-0.7, 0.7, 3)
        nr = rng.normal(size=3)
        nr /= np.linalg.norm(nr)
        a1 = np.cross(nr, rng.normal(size=3))
        a1 /= np.linalg.norm(a1)
        a2 = np.cross(nr, a1)
        t = np.linspace(0, ang, max(3, int(R * ang / 2e-3)))
        p = c + R * (np.cos(t)[:, None] * a1 + np.sin(t)[:, None] * a2)
        p = p[np.all(np.abs(p - CENTER) <= HALF, axis=1)]
        if len(p) > 2:
            out.append(p)
            tot += float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())
    return out


def armor(S, height=0.8):
    """The project's procedural Iron-Man armor (04_engineering/holo_engine/content.py), scaled to the 0.8 m tall image
    volume and cut to an S-metre stroke budget (silhouettes first)."""
    import content as ct
    strokes = ct.procedural_armor_budget(max_length_m=S, height=height)[0]
    return [np.asarray(s, float) + np.array([CENTER[0], CENTER[1], CENTER[2] - HALF[2]]) for s in strokes]


def aligned_lines():
    """Adversarial but ordinary content: a 30 cm vertical line 3 cm off the ceiling/floor-head axis (an arm, a sword)
    and a 30 cm line aimed at a corner head, plus 4.4 m of random segments."""
    up = np.array([[CENTER[0] + 0.03, CENTER[1], CENTER[2] - 0.15], [CENTER[0] + 0.03, CENTER[1], CENTER[2] + 0.15]])
    d = CENTER - H10[0]
    d /= np.linalg.norm(d)
    corner = np.array([CENTER + np.array([0.1, -0.1, 0.0]) - 0.15 * d, CENTER + np.array([0.1, -0.1, 0.0]) + 0.15 * d])
    return [up, corner] + random_segments(4.4, np.random.default_rng(13))


def chain_tour(strokes):
    """Greedy nearest-end chaining into one closed tour (own). Returns a list of (polyline, lit) pieces."""
    rem = [np.asarray(s, float) for s in strokes if len(s) > 1]
    order = [rem.pop(0)]
    while rem:
        end = order[-1][-1]
        d0 = [np.linalg.norm(s[0] - end) for s in rem]
        d1 = [np.linalg.norm(s[-1] - end) for s in rem]
        i0, i1 = int(np.argmin(d0)), int(np.argmin(d1))
        if d0[i0] <= d1[i1]:
            order.append(rem.pop(i0))
        else:
            order.append(rem.pop(i1)[::-1])
    pieces = []
    for k, s in enumerate(order):
        pieces.append((s, True))
        nxt = order[(k + 1) % len(order)][0]
        pieces.append((np.array([s[-1], nxt]), False))
    return pieces


def elements(pieces, dl):
    """Resample every piece at spacing dl: midpoints, unit tangents, lengths, lit flags."""
    P, T, L, LIT = [], [], [], []
    for poly, lit in pieces:
        seg = np.diff(poly, axis=0)
        sl = np.linalg.norm(seg, axis=1)
        for a, d, l in zip(poly[:-1], seg, sl):
            if l < 1e-9:
                continue
            n = max(1, int(math.ceil(l / dl)))
            s = (np.arange(n) + 0.5) / n
            P.append(a + s[:, None] * d)
            T.append(np.tile(d / l, (n, 1)))
            L.append(np.full(n, l / n))
            LIT.append(np.full(n, lit))
    return np.vstack(P), np.vstack(T), np.concatenate(L), np.concatenate(LIT)


def beam_powers(P, T, v, w, I_unit, room, mode="lp", n_draw=16, seed=5, theta_min=0.0, rng_heads=None):
    """Mean beam power (W) per element and head, (n, 10). mode 'lp': LP-chosen heads for f = v t - u, averaged over
    draft draws; 'random': 3 random heads per element cluster with equal split of the h_worst focus power (m17/T8)."""
    n = len(P)
    U, sig = ROOMS[room]
    unit = I_unit * math.pi * w * w / 2                   # beam power per unit LP coefficient (m/s)
    if mode == "random":
        B = np.zeros((n, 10))
        cl = np.arange(n) // 6                            # one random head triple per 3 mm "voxel" (dl 0.5 mm)
        for c in np.unique(cl):
            B[np.ix_(cl == c, rng_heads.choice(10, 3, replace=False))] = 2.14 * v * unit / 3
        return B, np.full(n, 2.14)
    K, Minv, valid = triple_inverses(P)
    if theta_min > 0:                                     # stacking-aware: forbid beams within theta_min of the motion
        cosang = np.einsum("nij,nj->ni", K, T)            # cos(angle between beam j and the tangent)
        bad = cosang > math.cos(math.radians(theta_min))
        valid = valid & ~np.any(bad[:, TRIPLES], axis=2)
    rng = np.random.default_rng(seed)
    acc = np.zeros((n, 10))
    hsum = np.zeros(n)
    for _ in range(n_draw):
        u = rng.normal(0, sig, size=(n, 3))
        u[:, 0] += U
        f = v * T - u
        C = lp_alloc(f, Minv, valid)
        acc += C
        hsum += C.sum(axis=1) / np.linalg.norm(f, axis=1)
    return acc / n_draw * unit, hsum / n_draw


def exposure(probes, Pel, Tel, Lel, B, v, w, f_r=30.0, chunk=8, exact=True):
    """Time-averaged power (W) through a 3.5 mm aperture at each probe (aperture normal to each beam: m17 convention,
    an upper bound for oblique beams). Each element is crossed f_r times per second and occupied for dl/v each time."""
    j_el, j_h = np.nonzero(B > 1e-6 * B.max())
    S = H10[j_h]
    F = Pel[j_el]
    D = F - S
    Lb = np.linalg.norm(D, axis=1)
    Ub = D / Lb[:, None]
    wt = f_r * Lel[j_el] / v * B[j_el, j_h]               # time-mean beam power weight (W)
    zR = math.pi * w * w / LAM
    out = np.zeros(len(probes))
    for i0 in range(0, len(probes), chunk):
        X = probes[i0:i0 + chunk]
        V = X[:, None, :] - S[None, :, :]
        t = np.einsum("pbk,bk->pb", V, Ub)
        rho2 = np.maximum(np.einsum("pbk,pbk->pb", V, V) - t * t, 0.0)
        z = t - Lb[None, :]
        wz2 = w * w * (1 + (z / zR) ** 2)
        if exact:                                         # exact capture wherever it can matter (rho < R + 4 w(z))
            fr = np.zeros_like(rho2)
            m = (t > 0) & (rho2 < (R_AP + 4 * np.sqrt(wz2)) ** 2)
            fr[m] = frac_exact(np.sqrt(rho2[m]), np.sqrt(wz2[m]))
        else:
            fr = frac_approx(rho2, wz2)
        fr[t < 0] = 0.0
        out[i0:i0 + chunk] = fr @ wt
    return out


def contributions(probe, Pel, Lel, B, v, w, f_r=30.0):
    """Per-element, per-head contributions at one probe (for diagnosis)."""
    zR = math.pi * w * w / LAM
    D = Pel[:, None, :] - H10[None, :, :]
    Lb = np.linalg.norm(D, axis=2)
    U = D / Lb[:, :, None]
    V = probe[None, None, :] - H10[None, :, :]
    t = np.einsum("hk,nhk->nh", V[0], U)
    rho2 = np.maximum(np.sum(V[0] ** 2, axis=1)[None, :] - t * t, 0)
    z = t - Lb
    fr = frac_exact(np.sqrt(rho2), w * np.sqrt(1 + (z / zR) ** 2))
    fr[t < 0] = 0
    return f_r * Lel[:, None] / v * B * fr


def expo_case(strokes, name, room, v, w, I_unit, mode="lp", theta_min=0.0, dl=0.5e-3, n_rand=1500, seed=1,
              include_jumps=True, refine=True):
    pieces = chain_tour(strokes)
    S = sum(float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum()) for p, lit in pieces if lit)
    J = sum(float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum()) for p, lit in pieces if not lit)
    if not include_jumps:
        pieces = [(p, lit) for p, lit in pieces if lit]
    Pel, Tel, Lel, LIT = elements(pieces, dl)
    rng = np.random.default_rng(seed)
    B, hbar = beam_powers(Pel, Tel, v, w, I_unit, room, mode=mode, theta_min=theta_min, rng_heads=rng)
    ok = np.all(np.isfinite(B), axis=1)
    B[~ok] = 0.0
    probes = np.vstack([Pel[::4], CENTER + (rng.random((n_rand, 3)) * 2 - 1) * (HALF + 0.15)])
    E = exposure(probes, Pel, Tel, Lel, B, v, w)
    if refine:
        top = probes[np.argsort(E)[-12:]]
        g = np.arange(-2, 3) * 0.6e-3
        G = np.array([(a, b, c) for a in g for b in g for c in g])
        probes2 = (top[:, None, :] + G[None, :, :]).reshape(-1, 3)
        E2 = exposure(probes2, Pel, Tel, Lel, B, v, w)
        probes = np.vstack([probes, probes2])
        E = np.concatenate([E, E2])
    i = int(np.argmax(E))
    # m17's closed-form capture at the worst probe (comparison: it under-reads crossings by ~11 %)
    E_ex = exposure(probes[i:i + 1], Pel, Tel, Lel, B, v, w, exact=False)[0]
    C = contributions(probes[i], Pel, Lel, B, v, w)
    by_head = C.sum(axis=0)
    d_el = np.linalg.norm(Pel - probes[i], axis=1)
    near = C[d_el < 5e-3].sum()
    # T8's own-path reference: f_r d_ap E/L with the LOCAL mean E/L of the elements within 2 mm (no stacking)
    loc = d_el < 2e-3
    EL_loc = float(B[loc].sum(axis=1).mean() / v) if loc.any() else float("nan")
    own_ref = 30.0 * 3.5e-3 * EL_loc
    EL_T8 = 2.14 * I_unit * math.pi * w * w / 2
    res = dict(content=name, room=room, v=v, w_um=w * 1e6, mode=mode, theta_min=theta_min, S=S, J=J,
               duty=S / (S + J), n_el=len(Pel), max_mW=float(E.max() * 1e3), max_m17form_mW=float(E_ex * 1e3),
               p999_probe_mW=float(np.percentile(E, 99.9) * 1e3), median_on_tour_mW=float(np.median(E[:len(Pel[::4])]) * 1e3),
               worst_xyz=probes[i].tolist(), worst_by_head_mW=(by_head * 1e3).tolist(),
               within_5mm_frac=float(near / C.sum()), h_mean_tour=float(np.nanmean(hbar)),
               EL_T8_mJm=EL_T8 * 1e3, EL_local_mJm=EL_loc * 1e3,
               s_eff_vs_T8_EL=float(E.max() / (30.0 * 3.5e-3 * EL_T8)),
               ratio_to_AEL=float(E.max() / AEL_IR), w_class1_um=float(w * 1e6 * math.sqrt(AEL_IR / E.max())))
    return res


def i_unit(v=0.5, A=1.0):
    import m18_gaussian_lcsv as m18                        # XCHECK source of T8's own I_unit (validated by RT6/RT7)
    return m18.hold(1e-6, v, h=2.14, A=A)["I"] / v


def expo_selftest():
    """(1) closed-form capture vs exact ncx2; (2) one beam at its focus; (3) crossing invariant: a single straight
    stroke crossed by its own beam perpendicular to it gives f_r d_ap E/L; (4) own exposure function vs m17.exposure
    on the same static beams (XCHECK)."""
    rng = np.random.default_rng(2)
    rho = rng.uniform(0, 4e-3, 2000)
    wz = 10 ** rng.uniform(-5, -2.3, 2000)
    a, e = frac_approx(rho ** 2, wz ** 2), frac_exact(rho, wz)
    err = float(np.max(np.abs(a - e)))
    # single stroke along x through the centre, one beam from the ceiling-centre head (perpendicular to x)
    w = 35e-6
    x = np.arange(-0.05, 0.05, 0.25e-3) + 0.125e-3
    Pel = CENTER + np.stack([x, 0 * x, 0 * x], 1)
    Tel = np.tile([1.0, 0, 0], (len(x), 1))
    Lel = np.full(len(x), 0.25e-3)
    B = np.zeros((len(x), 10))
    B[:, 8] = 0.010                                       # 10 mW per focus at v = 0.5 m/s: E/L = 0.02 J/m
    E = exposure(CENTER[None, :], Pel, Tel, Lel, B, 0.5, w)[0]
    ref = 30.0 * 3.5e-3 * 0.02
    # same stroke but the beam at 20 deg to the stroke: expect ~ d_ap / sin(20 deg) (narrow beam) -> x 2.9
    Hs = CENTER + np.array([-math.cos(math.radians(20)), 0, math.sin(math.radians(20))]) * 3.0
    D = Pel - Hs
    # emulate by moving head 8 temporarily
    H8 = H10[8].copy()
    H10[8] = Hs
    E20 = exposure(CENTER[None, :], Pel, Tel, Lel, B, 0.5, w)[0]
    H10[8] = H8
    import m17_exposure_field as m17                       # XCHECK
    motes = CENTER + (rng.random((300, 3)) * 2 - 1) * HALF * 0.3
    beams = [(H10[j], m) for m in motes for j in rng.choice(10, 3, replace=False)]
    probes = motes[:60]
    E17 = m17.exposure(probes, beams, 1e-3, 35e-6)
    # own: static beams = elements with dl/v f_r = 1 (set f_r = v / dl)
    Pb = np.array([b[1] for b in beams])
    Bb = np.zeros((len(beams), 10))
    for i, (h, m) in enumerate(beams):
        Bb[i, int(np.argmin(np.linalg.norm(H10 - h, axis=1)))] = 1e-3
    Eown = exposure(probes, Pb, None, np.full(len(beams), 1.0), Bb, 1.0, 35e-6, f_r=1.0, exact=False)
    Eown_ex = exposure(probes, Pb, None, np.full(len(beams), 1.0), Bb, 1.0, 35e-6, f_r=1.0)
    dev17 = float(np.max(np.abs(Eown - E17) / E17))
    ex_over_17 = float(np.max(Eown_ex) / np.max(E17))
    out = dict(capture_max_abs_err=err, crossing_perp_ratio=E / ref, crossing_20deg_ratio=E20 / ref,
               expected_20deg=1 / math.sin(math.radians(20)), dev_vs_m17=dev17, exact_over_m17_worst=ex_over_17)
    print(f"  self-test: capture closed form vs exact max |err| {err:.3f}; perpendicular crossing / (f_r d E/L) "
          f"{E / ref:.3f} (expect ~1); beam at 20 deg to the stroke {E20 / ref:.2f} (narrow-beam 1/sin = "
          f"{1 / math.sin(math.radians(20)):.2f}); own exposure vs m17.exposure on identical static beams max rel dev "
          f"{dev17:.2e}; worst static pupil exact/m17 form {ex_over_17:.3f}")
    return out


def sec_expo(quick=False):
    print("== expo: POV exposure field, LP-chosen heads, tours with jumps ==")
    out = dict(selftest=expo_selftest(), cases=[])
    lp = lp_selftest()
    out["lp_selftest"] = lp
    print(f"  LP self-test: own vs linprog max rel dev {lp['dev_linprog']:.1e}, residual {lp['residual']:.1e}, vs m18c "
          f"facets {lp['dev_m18c']:.1e}; h_worst at centre {lp['h_worst_centre']:.3f}, h_mean {lp['h_mean_centre']:.3f}")
    Iu = i_unit(0.5)
    contents = {"segments": random_segments(5.0, np.random.default_rng(11)),
                "arcs": random_arcs(5.0, np.random.default_rng(12)),
                "armor": armor(5.0), "aligned": aligned_lines()}
    plan = []
    for cname in ("segments", "arcs", "armor", "aligned"):
        plan.append((cname, "still", 0.5, 34.3e-6, "random", 0.0, False))   # T8/M17 convention (validation)
        plan.append((cname, "still", 0.5, 34.3e-6, "lp", 0.0, False))
        plan.append((cname, "still", 0.5, 34.3e-6, "lp", 0.0, True))
        plan.append((cname, "office", 0.5, 31.0e-6, "lp", 0.0, True))
        plan.append((cname, "still", 0.5, 34.3e-6, "lp", 30.0, True))       # stacking-aware: no beam within 30 deg
    if quick:
        plan = plan[:3]
    for cname, room, v, w, mode, th, jumps in plan:
        t0 = time.time()
        r = expo_case(contents[cname], cname, room, v, w, Iu, mode=mode, theta_min=th, include_jumps=jumps)
        r["wall_s"] = time.time() - t0
        out["cases"].append(r)
        print(f"  {cname:8s} {room:6s} v {v} w {w * 1e6:4.1f} {mode:6s} th_min {th:2.0f} jumps {str(jumps):5s}: "
              f"duty {r['duty']:.2f}; worst pupil {r['max_mW']:6.1f} mW (m17 form {r['max_m17form_mW']:6.1f}; AEL 9.62) "
              f"= x{r['ratio_to_AEL']:.2f}; s'_eff (vs T8 E/L) {r['s_eff_vs_T8_EL']:.2f}; median on tour "
              f"{r['median_on_tour_mW']:.2f} mW; <5 mm share {r['within_5mm_frac']:.2f}; h_mean {r['h_mean_tour']:.2f}; "
              f"Class-1 w {r['w_class1_um']:.1f} um  [{r['wall_s']:.0f} s]", flush=True)
        dump("expo", out)
    return out


# ======================================================================================================================
# Section loop: independent POV tracking simulation (own turbulence, tuner and simulator)
# ======================================================================================================================
NU = 1.51e-5


class Turb:
    """Frozen-plus-unsteady 3D isotropic turbulence by random Fourier modes ('kinematic simulation'): von Karman energy
    spectrum with a Pao dissipation cutoff, divergence-free modes, per-mode unsteadiness omega_n = lam_u sqrt(k^3 E(k)),
    advected by a mean wind U (unit direction per mote). Longitudinal integral scale set to L by construction."""

    def __init__(self, sigma, L, U=0.0, n_modes=300, seed=0, lam_u=0.5, Ceps=0.5):
        rng = np.random.default_rng(seed)
        self.sigma, self.L, self.U = sigma, L, U
        eps = Ceps * sigma ** 3 / L
        self.eta = (NU ** 3 / eps) ** 0.25
        ke = 1.0 / L
        kk = np.logspace(math.log10(0.02 * ke), math.log10(4.0 / self.eta), 4000)
        E = lambda k, ke_: (k / ke_) ** 4 / (1 + (k / ke_) ** 2) ** (17 / 6) * np.exp(-1.5 * (k * self.eta) ** (4 / 3))
        # longitudinal integral scale L11 = (pi / (2 sigma^2)) int E(k)/k dk with sigma^2 = (2/3) int E dk
        def L11(ke_):
            e = E(kk, ke_)
            return math.pi / 2 * np.trapezoid(e / kk, kk) / (2 / 3 * np.trapezoid(e, kk))
        ke = optimize.brentq(lambda x: L11(x) - L, 0.05 / L, 20 / L)
        self.ke = ke
        edges = np.logspace(math.log10(0.02 * ke), math.log10(4.0 / self.eta), n_modes + 1)
        kc = np.sqrt(edges[1:] * edges[:-1])
        dk = np.diff(edges)
        e = E(kc, ke) * dk
        e *= 3.0 * sigma ** 2 / e.sum()                      # <|u|^2> = sum a^2/2 = 3 sigma^2
        amp = np.sqrt(2 * e)
        kd = rng.normal(size=(n_modes, 3))
        kd /= np.linalg.norm(kd, axis=1)[:, None]
        sd = np.cross(kd, rng.normal(size=(n_modes, 3)))
        sd /= np.linalg.norm(sd, axis=1)[:, None]
        self.k = kd * kc[:, None]
        self.a = sd * amp[:, None]
        self.ph = rng.random(n_modes) * 2 * math.pi
        Ek = e / dk
        self.om = lam_u * np.sqrt(kc ** 3 * Ek)

    def __call__(self, x, t, udir):
        """x (n, 3) positions, t time, udir (n, 3) unit mean-wind directions -> u (n, 3)."""
        xs = x - self.U * t * udir
        arg = xs @ self.k.T + self.ph[None, :] + self.om[None, :] * t
        return np.cos(arg) @ self.a + self.U * udir


def plant_dt(T, tau, n_sub):
    """Per-substep exact factor for the first-order beam-amplitude lag."""
    return math.exp(-(T / n_sub) / tau)


def tune_pid(T, d, tau, sig_n, u_series, Ms_max=2.0, dur=1.5):
    """Own tuner: discrete loop (velocity command -> first-order lag tau -> integrator, ZOH, d frames of latency) with
    PID on the measured error. Candidates are kept if the modulus margin max|S| <= Ms_max (frequency response of the
    exact ZOH discretisation); the one with the smallest p99.9 |x| in a 1D time-domain run against the supplied
    seen-turbulence series (u_series, sampled at the frame rate) and the sensor noise wins."""
    from scipy import signal
    A = np.array([[0.0, 1.0], [0.0, -1.0 / tau]])
    Bc = np.array([[0.0], [1.0 / tau]])
    sysd = signal.cont2discrete((A, Bc, np.array([[1.0, 0.0]]), np.zeros((1, 1))), T, method="zoh")
    num, den = signal.ss2tf(sysd[0], sysd[1], sysd[2], sysd[3])
    zz = np.exp(1j * np.linspace(1e-3, math.pi, 3000))
    Pz = np.polyval(num[0], zz) / np.polyval(den, zz) * zz ** (-d)
    Deff = (d + 0.5) * T + tau
    cands = []
    for kp in np.array([0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.65, 0.8]) / Deff:
        for ki in np.array([0.0, 0.01, 0.02, 0.05, 0.1, 0.2]) / Deff ** 2:
            for kd in (0.0, 0.1, 0.2, 0.4):
                kdv = kd * kp * Deff
                C = kp + ki * T / (1 - 1 / zz) + kdv * (1 - 1 / zz) / T
                Ms = float(np.max(np.abs(1 / (1 + C * Pz))))
                if Ms <= Ms_max:
                    cands.append((kp, ki, kdv, Ms))
    if not cands:
        return None
    G = np.array(cands)
    n = len(G)
    rng = np.random.default_rng(7)
    nf = min(len(u_series), int(dur / T))
    a_lag = math.exp(-T / tau)
    x = np.zeros(n)
    F = np.zeros(n)
    integ = np.zeros(n)
    e_prev = np.zeros(n)
    hist = np.zeros((d + 1, n))
    rec = []
    for k in range(nf):
        y = hist[-1] + sig_n * rng.standard_normal(n)
        e = -y
        integ += e
        fc = G[:, 0] * e + G[:, 1] * T * integ + G[:, 2] * (e - e_prev) / T
        e_prev = e
        # exact over the frame: F relaxes to fc; x integrates F + u
        dx = fc * T + (F - fc) * tau * (1 - a_lag) + u_series[k] * T
        F = fc + (F - fc) * a_lag
        x = x + dx
        hist = np.roll(hist, 1, axis=0)
        hist[0] = x
        if k > nf // 5:
            rec.append(np.abs(x))
    R = np.array(rec)
    R[~np.isfinite(R)] = 1.0
    p999 = np.percentile(R, 99.9, axis=0)
    i = int(np.argmin(p999))
    return dict(Kp=float(G[i, 0]), Ki=float(G[i, 1]), Kd=float(G[i, 2]), Ms=float(G[i, 3]), p999_1d=float(p999[i]))


def cmax_dirs(Minv, valid, n=800, seed=1):
    rng = np.random.default_rng(seed)
    D = rng.normal(size=(n, 3))
    D /= np.linalg.norm(D, axis=1)[:, None]
    out = np.zeros(len(Minv))
    for i in range(len(Minv)):
        C = lp_alloc(D, np.repeat(Minv[i:i + 1], n, axis=0), np.repeat(valid[i:i + 1], n, axis=0))
        out[i] = np.nanmax(C)
    return out


def cmax_dirs_f(FI, FV, FO, n=800, seed=1):
    rng = np.random.default_rng(seed)
    D = rng.normal(size=(n, 3))
    D /= np.linalg.norm(D, axis=1)[:, None]
    out = np.zeros(len(FI))
    for i in range(len(FI)):
        C = lp_alloc_f(D, np.repeat(FI[i:i + 1], n, 0), np.repeat(FV[i:i + 1], n, 0), np.repeat(FO[i:i + 1], n, 0))
        out[i] = C.max()
    return out


def sim_track(f_loop=20000.0, d=2, tau_act=30e-6, w=35e-6, v=0.5, f_r=30.0, room="office", L=0.03, sig_n=4e-6,
              n_m=100, dur=10.0, seed=0, path="circle", eulerian=False, mean_wind=True, auth=5.4, n_sub=2,
              lost_mult=1.5, turb_every=4, R_line=0.15, verbose=False):
    """Vectorised 3D tracking of n_m motes, each carried by LP-allocated beams from the 10 H10 heads.
    path 'circle': the tightest POV loop, radius v/(2 pi f_r) (m19b); 'line': a locally straight stroke (circle of
    radius R_line, a tour-model mote). Spot centred on the plan-predicted position and swept at the plan velocity
    within the frame (m19b's implicit assumption). eulerian=True samples the turbulence at the loop centre (m19b) instead
    of at the mote; mean_wind=False drops the mean wind (m19b as committed)."""
    U, sig = ROOMS[room]
    if not mean_wind:
        U = 0.0
    T = 1.0 / f_loop
    rng = np.random.default_rng(seed)
    turb = Turb(sig, L, U=U, seed=seed + 101)
    centres = CENTER + (rng.random((n_m, 3)) * 2 - 1) * HALF * 0.8
    phi = rng.random(n_m) * 2 * math.pi
    udir = np.stack([np.cos(phi), np.sin(phi), np.zeros(n_m)], 1)
    Rp = v / (2 * math.pi * f_r) if path == "circle" else R_line
    om = v / Rp
    e1 = rng.normal(size=(n_m, 3))
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = rng.normal(size=(n_m, 3))
    e2 -= np.sum(e2 * e1, axis=1)[:, None] * e1
    e2 /= np.linalg.norm(e2, axis=1)[:, None]
    ph0 = rng.random(n_m) * 2 * math.pi

    def plan(t):
        c, s_ = np.cos(om * t + ph0)[:, None], np.sin(om * t + ph0)[:, None]
        return centres + Rp * (c * e1 + s_ * e2), v * (-s_ * e1 + c * e2)

    K, Minv, valid = triple_inverses(centres)
    FI, FV, FO = map(np.array, zip(*[hull_facets(K[i]) for i in range(n_m)]))
    cm = cmax_dirs(Minv[:20], valid[:20])
    cm = np.concatenate([cm, cmax_dirs_f(FI[20:], FV[20:], FO[20:])]) if n_m > 20 else cm
    chk = lp_alloc_f(np.tile([0.3, -0.2, 0.5], (min(n_m, 20), 1)), FI[:20], FV[:20], FO[:20])
    chk2 = lp_alloc(np.tile([0.3, -0.2, 0.5], (min(n_m, 20), 1)), Minv[:20], valid[:20])
    assert np.allclose(chk, chk2, atol=1e-12), "facet allocation != triple enumeration"
    caps = (v + U + auth * sig) * cm
    # tuning on the seen turbulence of one mote along its path (component along e1), own tuner
    nt = int(1.5 / T)
    ts = np.arange(0, nt, turb_every) * T
    useries = np.array([turb(plan(t)[0][:1] if not eulerian else centres[:1], t, udir[:1])[0] @ e1[0] for t in ts])
    useries = np.repeat(useries - useries.mean(), turb_every)[:nt]
    gains = tune_pid(T, d, tau_act, sig_n, useries)
    Kp, Ki, Kd = gains["Kp"], gains["Ki"], gains["Kd"]
    p0, v0 = plan(0.0)
    x = p0.copy()
    u0 = turb(x if not eulerian else centres, 0.0, udir)
    A = lp_alloc_f(v0 - u0, FI, FV, FO)                    # beam amplitudes (velocity units), start in equilibrium
    integ = -u0 / (Ki * T) if Ki > 0 else np.zeros((n_m, 3))
    e_prev = np.zeros((n_m, 3))
    hist = np.repeat(x[None], d + 1, axis=0)
    phist = np.repeat(p0[None], d + 1, axis=0)
    lost = np.zeros(n_m, bool)
    t_lost = np.full(n_m, np.inf)
    a_sub = plant_dt(T, tau_act, n_sub)
    n_fr = int(dur / T)
    w2 = w * w
    err_s, off_s = [], []
    sat = 0
    # head-usage statistics: per mote, the set of heads with commanded amplitude > 2 % of the max, per revolution
    rev_T = 2 * math.pi / om if path == "circle" else 1.0 / f_r
    used = np.zeros((n_m, 10), bool)
    rev_counts, switch = [], np.zeros(n_m)
    prev_set = np.zeros((n_m, 10), bool)
    u_cur = u0
    u_next = u0
    t_next = 0.0
    for k in range(n_fr):
        t = k * T
        if k % turb_every == 0:
            u_cur = u_next if k > 0 else u0
            t_next = t + turb_every * T
            pn, _ = plan(t_next)
            u_next = turb(x if not eulerian else centres, t_next, udir)
        p, vp = plan(t)
        y = hist[(k - d) % (d + 1)] + sig_n * rng.standard_normal((n_m, 3))
        xh = y + p - phist[(k - d) % (d + 1)]
        e = p - xh
        fdes = vp + Kp * e + Ki * T * integ + Kd * (e - e_prev) / T
        e_prev = e
        Ac = lp_alloc_f(fdes, FI, FV, FO)
        Ac[~np.isfinite(Ac)] = 0.0
        s = Ac.max(axis=1) / caps
        over = s > 1
        Ac[over] /= s[over][:, None]
        sat += int(over.sum())
        integ[~over] += e[~over]
        on = Ac > 0.02 * np.maximum(Ac.max(axis=1, keepdims=True), 1e-12)
        used |= on
        switch += np.any(on & ~prev_set, axis=1)
        prev_set = on
        for j in range(n_sub):
            tt = t + j * T / n_sub
            c = xh + vp * (tt - t)                        # spot centre swept along the plan within the frame
            fr = (tt - (k - k % turb_every) * T) / (turb_every * T)
            uu = u_cur * (1 - fr) + u_next * fr
            dx = x - c
            proj = np.einsum("nij,nj->ni", K, dx)
            rho2 = np.sum(dx * dx, axis=1)[:, None] - proj ** 2
            g = np.exp(-2 * rho2 / w2)
            A = Ac + (A - Ac) * a_sub
            F = np.einsum("ni,nij->nj", A * g, K)
            x = x + (F + uu) * (T / n_sub)
        off = np.linalg.norm(x - (xh + vp * T), axis=1)
        pT, _ = plan(t + T)
        hist[(k + 1) % (d + 1)] = x
        phist[(k + 1) % (d + 1)] = pT
        if t > 0.2:
            newly = (off > lost_mult * w) & ~lost
            t_lost[newly] = t
            lost |= newly
            if k % 20 == 0:
                err_s.append(np.linalg.norm(x - pT, axis=1)[~lost])
                off_s.append(off[~lost])
        if (k + 1) % int(round(rev_T / T)) == 0:
            rev_counts.append(used[~lost].sum(axis=1))
            used[:] = False
    Ee = np.concatenate(err_s) if err_s else np.array([np.nan])
    O = np.concatenate(off_s) if off_s else np.array([np.nan])
    t_eff = float(np.sum(np.minimum(t_lost, dur) - 0.2))
    nl = int(lost.sum())
    RC = np.concatenate(rev_counts) if rev_counts else np.array([np.nan])
    lo, hi = poisson_ci(nl, t_eff)
    return dict(f_loop=f_loop, d=d, tau_act_us=tau_act * 1e6, w_um=w * 1e6, v=v, room=room, U=U, sigma=sig,
                sig_n_um=sig_n * 1e6, path=path, eulerian=eulerian, mean_wind=mean_wind, n_m=n_m, dur=dur,
                gains=gains, lost=nl, mote_s=t_eff, rate=nl / max(t_eff, 1e-9), rate_lo=lo, rate_hi=hi,
                err_p50_um=float(np.nanpercentile(Ee, 50) * 1e6), err_p999_um=float(np.nanpercentile(Ee, 99.9) * 1e6),
                off_p999_um=float(np.nanpercentile(O, 99.9) * 1e6), sat_frac=sat / (n_fr * n_m),
                heads_per_rev_mean=float(np.nanmean(RC)), heads_per_rev_p90=float(np.nanpercentile(RC, 90)),
                heads_per_rev_max=float(np.nanmax(RC)), facet_switch_per_s=float(np.mean(switch) / dur),
                eta_mm=turb.eta * 1e3)


def poisson_ci(n, T, conf=0.95):
    a = 1 - conf
    lo = 0.0 if n == 0 else stats.chi2.ppf(a / 2, 2 * n) / 2 / T
    hi = stats.chi2.ppf(1 - a / 2, 2 * n + 2) / 2 / T
    return lo, hi


def turb_selftest():
    """Variance per component and the longitudinal integral scale of the generated field; Eulerian frequency spectrum
    vs rt6.turb_spectrum's shape (XCHECK)."""
    tb = Turb(0.1, 0.03, U=0.0, n_modes=300, seed=3)
    rng = np.random.default_rng(1)
    X = CENTER + rng.random((4000, 3)) * 2.0
    u = tb(X, 0.0, np.tile([1.0, 0, 0], (4000, 1)))
    var = u.var(axis=0)
    # longitudinal correlation along x
    r = np.linspace(0, 0.2, 81)
    f = []
    for ri in r:
        u2 = tb(X + np.array([ri, 0, 0]), 0.0, np.tile([1.0, 0, 0], (4000, 1)))
        f.append(np.mean(u[:, 0] * u2[:, 0]) / np.mean(u[:, 0] ** 2))
    L11 = float(np.trapezoid(f, r))
    return dict(sigma_comp=np.sqrt(var).tolist(), L11=L11, eta_mm=tb.eta * 1e3)


def sec_loop(which="key"):
    print("== loop: independent POV tracking simulation ==")
    out = dict(turb_selftest=turb_selftest(), runs=[])
    ts = out["turb_selftest"]
    print(f"  turbulence self-test: sigma per component {np.round(ts['sigma_comp'], 3)} (target 0.1), L11 "
          f"{ts['L11'] * 100:.1f} cm (target 3), eta {ts['eta_mm']:.2f} mm")
    if which == "key":
        plan = [  # (kwargs)
            dict(room="office", w=35e-6, path="circle", eulerian=True, mean_wind=False, n_m=100, dur=10.0),  # m19b as published
            dict(room="office", w=35e-6, path="circle", n_m=100, dur=10.0),
            dict(room="office", w=31e-6, path="circle", n_m=100, dur=10.0),
            dict(room="still", w=35e-6, path="circle", n_m=100, dur=10.0),
            dict(room="quiet_office", w=35e-6, path="circle", n_m=100, dur=10.0),
            dict(room="office", w=35e-6, path="line", n_m=100, dur=10.0),
            dict(room="still", w=34e-6, path="line", n_m=100, dur=10.0),
        ]
    elif which == "sens":
        plan = [
            dict(room="still", w=34e-6, path="circle", sig_n=6e-6, n_m=100, dur=10.0),
            dict(room="still", w=34e-6, path="circle", d=3, n_m=100, dur=10.0),
            dict(room="still", w=34e-6, path="circle", f_loop=10000.0, tau_act=50e-6, n_m=100, dur=10.0),
            dict(room="office", w=35e-6, path="circle", v=0.8, n_m=100, dur=10.0),
            dict(room="still", w=34e-6, path="circle", n_sub=1, n_m=100, dur=10.0),
        ]
    else:  # long
        plan = [dict(room="still", w=34e-6, path="circle", n_m=200, dur=40.0),
                dict(room="office", w=35e-6, path="circle", n_m=200, dur=40.0)]
    for i, kw in enumerate(plan):
        t0 = time.time()
        r = sim_track(seed=1000 + 17 * i + zlib.crc32(which.encode()) % 997, **kw)
        r["wall_s"] = time.time() - t0
        out["runs"].append(r)
        print(f"  {r['f_loop'] / 1e3:4.0f} kHz d{r['d']} {r['room']:12s} U {r['U']:.2f} w {r['w_um']:4.1f} v {r['v']} "
              f"{r['path']:6s} {'euler' if r['eulerian'] else 'moving'} noise {r['sig_n_um']:.0f}: lost {r['lost']}/"
              f"{r['n_m']} in {r['mote_s']:.0f} mote-s (rate {r['rate']:.1e}/s, 95% CI {r['rate_lo']:.1e}-"
              f"{r['rate_hi']:.1e}); draw err p50 {r['err_p50_um']:.1f} p99.9 {r['err_p999_um']:.1f} um; offset p99.9 "
              f"{r['off_p999_um']:.1f}; sat {r['sat_frac']:.1e}; heads/rev mean {r['heads_per_rev_mean']:.1f} p90 "
              f"{r['heads_per_rev_p90']:.0f} max {r['heads_per_rev_max']:.0f}; new-head events {r['facet_switch_per_s']:.0f}/s;"
              f" Ms {r['gains']['Ms']:.2f}  [{r['wall_s']:.0f} s]", flush=True)
        dump(f"loop_{which}", out)
    return out


if __name__ == "__main__":
    secs = sys.argv[1:] or ["std"]
    for s in secs:
        if s == "std":
            sec_std()
        elif s == "expo":
            sec_expo()
        elif s == "expoq":
            sec_expo(quick=True)
        elif s.startswith("loop"):
            sec_loop(s[5:] if len(s) > 4 else "key")

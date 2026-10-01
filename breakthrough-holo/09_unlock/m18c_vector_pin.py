"""M18c: pinning a mote with Gaussian beams from the real H10 heads. A 3D vector model with LP force allocation.

m18b's common-radial model applies the Gaussian factor exp(-2 r^2/w^2) to every beam. That is pessimistic. Each beam
loses force only through the mote's offset across its own axis. The force deficit moves the mote along the net force,
which runs mostly along the dominant pushing beams, so their intensity barely changes over the 4-15 mm Rayleigh range.

Model per mote, per hologram frame:
- beams k_j: unit propagation vectors from the 10 H10 heads (RT6/M4 coordinates) to the mote's home position.
  Positive photophoresis pushes along k_j.
- controller: per-axis PID (rt6.tune gains) on the measured position (d frames old, Gaussian noise) gives the desired
  force vector f;
- allocation: the minimum-power nonnegative combination sum c_j k_j = f. The LP optimum is the facet of the convex hull
  of {k_j} that the ray through f crosses, so it uses 3 beams;
- gain scheduling: a_j = c_j / g_j(y_measured), g_j = exp(-2 rho_j^2 / w^2), rho_j the measured offset across beam j;
- authority: every beam is capped at A_cap = 5.4 sigma * max_j c_j over all directions. An over-cap command is scaled
  down as a whole;
- delivered force: sum a_j g_j(x_true) k_j, through the modulator lag tau_F (first order), into the overdamped mote.

Run: python3 m18c_vector_pin.py [--quick]  -> results/m18c_vector_pin.json
"""
import json
import math
import os
import sys
import zlib

import numpy as np
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt6_check as rt6  # noqa: E402
import m18b_holo_loop as m18b  # noqa: E402

HEADS = np.array(rt6.H10)
CENTER = np.array([3.0, 2.5, 1.3])
HALF = np.array([0.5, 0.5, 0.4])


def facets(K):
    """Convex-hull facets of the beam directions (rows of K) and the inverse of each facet's 3x3 matrix."""
    hull = ConvexHull(K)
    inv = np.array([np.linalg.inv(K[s].T) for s in hull.simplices])
    return hull.simplices, inv


def allocate(f, simp, inv):
    """Minimum-sum nonnegative beam coefficients for force f (3,) on one mote: facet whose cone contains f."""
    C = inv @ f                                   # (n_facets, 3)
    ok = np.all(C >= -1e-12, axis=1)
    i = int(np.argmax(ok)) if ok.any() else int(np.argmax(C.min(axis=1)))
    return simp[i], np.maximum(C[i], 0.0)


def c_max_over_directions(simp, inv, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, 3))
    v /= np.linalg.norm(v, axis=1)[:, None]
    worst_single, worst_sum = 0.0, 0.0
    for f in v:
        _, c = allocate(f, simp, inv)
        worst_single = max(worst_single, c.max())
        worst_sum = max(worst_sum, c.sum())
    return worst_single, worst_sum


def simulate(case, draft, w_spot, sig_n=4e-6, n_motes=60, dur=10.0, seed=0, fs_t=4000.0, auth=5.4, r_lost_mult=1.5,
             follow=False):
    """follow: every hologram frame re-centres each spot on the mote's latest measured position (the hologram is
    recomputed every frame anyway), so the beams are offset only by measurement noise plus the motion during the
    latency. The force still pushes the mote back towards its home voxel. Without follow, spots stay on the home voxel.
    A mote is lost when its offset from its spot centre exceeds r_lost_mult * w_spot."""
    cname, f_fr, d, tau_lc = case
    dname, u_rms, L, Uc = draft
    tp, tfm = rt6.mote_times(m18b.A_MOTE, m18b.RHO, m18b.CP, m18b.KP)
    T = 1 / f_fr
    tau_F = tau_lc + tfm
    fturb, Sturb, eta, nu0 = rt6.turb_norm(u_rms, L, Uc)
    sel = (fturb > 1e-3) & (fturb < 0.45 * f_fr)
    best = rt6.tune(tp, tau_F, T, d, fturb[sel][::4], Sturb[sel][::4], sig_n, 0.0)
    Kp, Ki, Kd = best[1]
    rng = np.random.default_rng(seed)
    homes = CENTER + (rng.random((n_motes, 3)) * 2 - 1) * HALF
    beams, simps, invs, caps, hsum = [], [], [], [], []
    for h in homes:
        K = h - HEADS
        K /= np.linalg.norm(K, axis=1)[:, None]
        simp, inv = facets(K)
        cmax, csum = c_max_over_directions(simp, inv, n=600, seed=1)
        beams.append(K)
        simps.append(simp)
        invs.append(inv)
        caps.append(auth * u_rms * cmax)
        hsum.append(csum)
    caps = np.array(caps)
    # exact per-frame discretisation of the overdamped mote (per axis) with the force lag
    Ad, Bd = rt6.discretise(*rt6.plant_ss(tp, tau_F), T)
    n_fr = int(dur / T)
    n_t = int(dur * fs_t) + 2
    U = rt6.synth_turb(3 * n_motes, n_t, fs_t, u_rms, L, Uc, rng).reshape(n_motes, 3, n_t)
    x = np.zeros((n_motes, 3))
    v = np.zeros((n_motes, 3))
    F = -U[:, :, 0].astype(float)                 # start in equilibrium
    integ = F / (Ki * T)
    hist = np.zeros((d + 1, n_motes, 3))
    e_prev = np.zeros((n_motes, 3))
    lost = np.zeros(n_motes, bool)
    t_lost = np.full(n_motes, np.inf)
    r_samples, sat = [], 0
    w2 = w_spot * w_spot
    for k in range(n_fr):
        t = k * T
        it = t * fs_t
        i0 = int(it)
        fr = it - i0
        uu = U[:, :, i0] * (1 - fr) + U[:, :, i0 + 1] * fr
        y = hist[-1] + sig_n * rng.standard_normal((n_motes, 3))
        e = -y
        f_des = Kp * e + Ki * T * integ + Kd * (e - e_prev) / T
        e_prev = e
        F_cmd = np.zeros((n_motes, 3))
        off = np.zeros(n_motes)
        for i in range(n_motes):
            if lost[i]:
                continue
            K = beams[i]
            idx, c = allocate(f_des[i], simps[i], invs[i])
            Kb = K[idx]
            # spot centre: home voxel, or the latest measured position (follow); gain scheduling from the measured
            # offset of the mote across each beam relative to the spot centre
            c_spot = y[i] if follow else np.zeros(3)
            dm = y[i] - c_spot
            rho2_m = np.sum(dm ** 2) - (Kb @ dm) ** 2
            g_hat = np.maximum(np.exp(-2 * rho2_m / w2), 0.05)
            a = c / g_hat
            s = a.max() / caps[i]
            if s > 1:
                a = a / s
                sat += 1
            else:
                integ[i] += e[i]                      # conditional integration (anti-windup)
            dx = x[i] - c_spot
            rho2 = np.sum(dx ** 2) - (Kb @ dx) ** 2
            g = np.exp(-2 * rho2 / w2)
            F_cmd[i] = (a * g) @ Kb
            off[i] = math.sqrt(np.sum(dx ** 2))
        # plant, per axis: state (x, v, F) with inputs (u, F_cmd)
        for ax in range(3):
            S = np.vstack([x[:, ax], v[:, ax], F[:, ax]])
            S = Ad @ S + Bd[:, [0]] * uu[:, ax] + Bd[:, [1]] * F_cmd[:, ax]
            x[:, ax], v[:, ax], F[:, ax] = S
        hist = np.roll(hist, 1, axis=0)
        hist[0] = x
        r = np.linalg.norm(x, axis=1)
        if t > 0.2:
            r_spot = off if follow else r
            newly = (r_spot > r_lost_mult * w_spot) & ~lost
            t_lost[newly] = t
            lost |= newly
            if k % 10 == 0:
                r_samples.append(r[~lost])
    R = np.concatenate(r_samples) if r_samples else np.array([np.nan])
    t_eff = float(np.sum(np.minimum(t_lost, dur) - 0.2))
    nl = int(lost.sum())
    return dict(case=cname, draft=dname, w_um=w_spot * 1e6, f_frame=f_fr, latency_frames=d, sig_noise_um=sig_n * 1e6,
                follow=follow,
                K=list(best[1]), r_p50_um=float(np.nanpercentile(R, 50) * 1e6), r_p999_um=float(np.nanpercentile(R, 99.9) * 1e6),
                r_max_um=float(np.nanmax(R) * 1e6), lost=nl, n_motes=n_motes, mote_seconds=t_eff,
                loss_rate=nl / t_eff, loss_rate_95_upper=(3.0 if nl == 0 else nl + 2 * math.sqrt(nl)) / t_eff,
                sat_frac=sat / (n_fr * n_motes), h_sum_mean=float(np.mean(hsum)), h_sum_max=float(np.max(hsum)))


def selftest():
    # allocation reproduces the requested force with nonnegative coefficients, and the LP cost matches RT6's H10 h_worst
    K = CENTER - HEADS
    K /= np.linalg.norm(K, axis=1)[:, None]
    simp, inv = facets(K)
    rng = np.random.default_rng(5)
    err = 0.0
    for _ in range(200):
        f = rng.normal(size=3)
        idx, c = allocate(f, simp, inv)
        err = max(err, np.linalg.norm(c @ K[idx] - f) / np.linalg.norm(f))
    # the facet allocation must equal RT6's linprog minimum (min_push) at the same point, direction by direction
    dev = 0.0
    for _ in range(100):
        f = rng.normal(size=3)
        f /= np.linalg.norm(f)
        _, c = allocate(f, simp, inv)
        dev = max(dev, abs(c.sum() - rt6.min_push(K, f)[0]))
    cmax, csum = c_max_over_directions(simp, inv, n=4000)
    ok = err < 1e-9 and dev < 1e-6
    print(f"self-test: allocation error {err:.1e}; |facet cost - linprog| max {dev:.1e}; worst LP cost at the centre "
          f"{csum:.2f} (RT6's 2.13 is the worst over 48 volume points): {'PASS' if ok else 'FAIL'}")
    return ok


def main(quick=False):
    assert selftest()
    rows = []
    cases = [m18b.CASES[0], m18b.CASES[3], m18b.CASES[4], m18b.CASES[5], m18b.CASES[6]]
    drafts = [m18b.DRAFTS[0], m18b.DRAFTS[2], m18b.DRAFTS[3]]
    for case in cases:
        for draft in drafts:
            for w in (35e-6, 40e-6, 50e-6, 70e-6):
                seed = zlib.crc32(f"{case[0]}{draft[0]}{w}".encode()) % 100000
                r = simulate(case, draft, w, n_motes=30 if quick else 60, dur=3.0 if quick else 20.0, seed=seed)
                rows.append(r)
                print(f"  {case[0]:30s} {draft[0]:22s} w {w * 1e6:3.0f} um: r_p50 {r['r_p50_um']:5.1f} r_p99.9 {r['r_p999_um']:5.1f} "
                      f"r_max {r['r_max_um']:6.1f} um  lost {r['lost']}/{r['n_motes']} in {r['mote_seconds']:.0f} mote-s "
                      f"(95% upper {r['loss_rate_95_upper']:.1e}/s)  sat {r['sat_frac']:.1e}", flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m18c_vector_pin.json"), "w") as fh:
        json.dump(rows, fh, indent=1, default=float)


def main_long():
    """Long runs at the candidate operating points, for loss statistics (0 losses in T mote-s bounds the rate at 3/T)."""
    rows = []
    for case, draft, w in ((m18b.CASES[5], m18b.DRAFTS[0], 50e-6), (m18b.CASES[5], m18b.DRAFTS[2], 50e-6),
                           (m18b.CASES[6], m18b.DRAFTS[2], 40e-6), (m18b.CASES[6], m18b.DRAFTS[3], 35e-6),
                           (m18b.CASES[3], m18b.DRAFTS[0], 70e-6)):
        seed = zlib.crc32(f"long{case[0]}{draft[0]}{w}".encode()) % 100000
        r = simulate(case, draft, w, n_motes=60, dur=150.0, seed=seed)
        rows.append(r)
        print(f"  LONG {case[0]:30s} {draft[0]:22s} w {w * 1e6:3.0f} um: r_p50 {r['r_p50_um']:5.1f} r_p99.9 {r['r_p999_um']:5.1f} "
              f"r_max {r['r_max_um']:6.1f} um  lost {r['lost']}/{r['n_motes']} in {r['mote_seconds']:.0f} mote-s "
              f"(95% upper {r['loss_rate_95_upper']:.1e}/s)  sat {r['sat_frac']:.1e}", flush=True)
        with open(os.path.join(HERE, "results", "m18c_vector_pin_long.json"), "w") as fh:
            json.dump(rows, fh, indent=1, default=float)


def main_follow():
    """Spot-following grid: the smallest waist each modulator holds (60 motes x 20 s per point)."""
    rows = []
    for case in (m18b.CASES[3], m18b.CASES[4], m18b.CASES[5]):
        for draft in (m18b.DRAFTS[0], m18b.DRAFTS[2], m18b.DRAFTS[3]):
            for w in (25e-6, 30e-6, 35e-6, 50e-6):
                seed = zlib.crc32(f"follow{case[0]}{draft[0]}{w}".encode()) % 100000
                r = simulate(case, draft, w, n_motes=60, dur=20.0, seed=seed, follow=True)
                rows.append(r)
                print(f"  FOLLOW {case[0]:30s} {draft[0]:22s} w {w * 1e6:3.0f} um: r_p50 {r['r_p50_um']:5.1f} r_p99.9 "
                      f"{r['r_p999_um']:5.1f} r_max {r['r_max_um']:6.1f} um  lost {r['lost']}/{r['n_motes']} in "
                      f"{r['mote_seconds']:.0f} mote-s (95% upper {r['loss_rate_95_upper']:.1e}/s)  sat {r['sat_frac']:.1e}",
                      flush=True)
                with open(os.path.join(HERE, "results", "m18c_vector_pin_follow.json"), "w") as fh:
                    json.dump(rows, fh, indent=1, default=float)


if __name__ == "__main__":
    if "--follow" in sys.argv:
        main_follow()
    elif "--long" in sys.argv:
        main_long()
    else:
        main(quick="--quick" in sys.argv)

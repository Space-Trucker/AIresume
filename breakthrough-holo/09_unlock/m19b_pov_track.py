"""M19b: can a steered Gaussian spot carry a 1 um mote along a POV stroke at 0.5-1 m/s? (vector model, real H10 heads)

This extends m18c (validated LP facet allocation, gain scheduling, per-beam authority cap, follow mode) to a moving
target p(t). Each mote traces a closed loop of circumference v/f_r once per refresh: a circle of radius R = v/(2 pi f_r)
in a random plane, which is the tightest stroke a POV mote of that duty would draw.

The controller of each steered channel:
- measures y = x(t - d T) + noise;
- predicts the present position x_hat = y + p(t) - p(t - d T) from the plan;
- puts the spot centre at x_hat (follow);
- commands the force f = v_plan(t) (feedforward: an overdamped mote moves at F + u) + PID(p - x_hat);
- allocates f over 3 beams by LP and caps each beam at (v + 5.4 sigma) * c_max.

Outputs:
- the drawing error |x - p| (image sharpness);
- the loss rate: offset from the spot centre > 1.5 w.

Run: python3 m19b_pov_track.py [--quick] -> results/m19b_pov_track.json
"""
import json
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt6_check as rt6  # noqa: E402
import m18b_holo_loop as m18b  # noqa: E402
import m18c_vector_pin as m18c  # noqa: E402

CASES = [  # name, loop rate (Hz), latency frames, actuator lag (s): steered channels, not holograms
    ("channel 5 kHz", 5000.0, 2, 0.1e-3),
    ("channel 10 kHz", 10000.0, 2, 0.05e-3),
    ("channel 20 kHz", 20000.0, 2, 0.03e-3),
]


MEAN_WIND = {"still, L 3 cm": 0.0, "still, L 10 cm": 0.0, "home, L 3 cm": 0.05, "quiet office, L 3 cm": 0.10,
             "office sigma 0.1, L 3 cm": 0.10}       # red team 7 C3: the drafts carry a mean wind U, not only eddies


def simulate(case, draft, w_spot, v_plan=0.8, f_r=30.0, sig_n=4e-6, n_motes=40, dur=6.0, seed=0, fs_t=4000.0,
             auth=5.4, r_lost_mult=1.5, mean_wind=True):
    cname, f_fr, d, tau_lc = case
    dname, u_rms, L, Uc = draft
    U_mean = MEAN_WIND.get(dname, 0.0) if mean_wind else 0.0
    tp, tfm = rt6.mote_times(m18b.A_MOTE, m18b.RHO, m18b.CP, m18b.KP)
    T = 1 / f_fr
    tau_F = tau_lc + tfm
    fturb, Sturb, eta, nu0 = rt6.turb_norm(u_rms, L, Uc)
    sel = (fturb > 1e-3) & (fturb < 0.45 * f_fr)
    best = rt6.tune(tp, tau_F, T, d, fturb[sel][::4], Sturb[sel][::4], sig_n, 0.0)
    Kp, Ki, Kd = best[1]
    rng = np.random.default_rng(seed)
    centres = m18c.CENTER + (rng.random((n_motes, 3)) * 2 - 1) * m18c.HALF
    R = v_plan / (2 * math.pi * f_r)
    om = v_plan / R
    e1 = rng.normal(size=(n_motes, 3))
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = rng.normal(size=(n_motes, 3))
    e2 -= np.sum(e2 * e1, axis=1)[:, None] * e1
    e2 /= np.linalg.norm(e2, axis=1)[:, None]
    ph0 = rng.random(n_motes) * 2 * math.pi

    def plan(t):
        c, s = np.cos(om * t + ph0)[:, None], np.sin(om * t + ph0)[:, None]
        return R * (c * e1 + s * e2), v_plan * (-s * e1 + c * e2)

    beams, simps, invs, caps = [], [], [], []
    for h in centres:
        K = h - m18c.HEADS
        K /= np.linalg.norm(K, axis=1)[:, None]
        simp, inv = m18c.facets(K)
        cmax, _ = m18c.c_max_over_directions(simp, inv, n=600, seed=1)
        beams.append(K)
        simps.append(simp)
        invs.append(inv)
        caps.append((v_plan + U_mean + auth * u_rms) * cmax)
    caps = np.array(caps)
    Ad, Bd = rt6.discretise(*rt6.plant_ss(tp, tau_F), T)
    n_fr = int(dur / T)
    n_t = int(dur * fs_t) + 2
    U = rt6.synth_turb(3 * n_motes, n_t, fs_t, u_rms, L, Uc, rng).reshape(n_motes, 3, n_t)
    if U_mean > 0:                                    # mean wind along a random horizontal direction per mote
        phi = rng.random(n_motes) * 2 * math.pi
        U = U + (U_mean * np.stack([np.cos(phi), np.sin(phi), np.zeros(n_motes)], axis=1))[:, :, None]
    p0, v0 = plan(0.0)
    x = p0.copy()
    vel = v0.copy()
    F = v0 - U[:, :, 0].astype(float)             # start on the path, in equilibrium
    integ = -U[:, :, 0].astype(float) / (Ki * T)
    hist = np.repeat(x[None], d + 1, axis=0)
    phist = np.repeat(p0[None], d + 1, axis=0)
    e_prev = np.zeros((n_motes, 3))
    lost = np.zeros(n_motes, bool)
    t_lost = np.full(n_motes, np.inf)
    err_s, off_s, sat = [], [], 0
    w2 = w_spot * w_spot
    for k in range(n_fr):
        t = k * T
        it = t * fs_t
        i0 = int(it)
        fr = it - i0
        uu = U[:, :, i0] * (1 - fr) + U[:, :, i0 + 1] * fr
        p, vp = plan(t)
        y = hist[-1] + sig_n * rng.standard_normal((n_motes, 3))
        x_hat = y + p - phist[-1]
        e = p - x_hat
        f_des = vp + Kp * e + Ki * T * integ + Kd * (e - e_prev) / T
        e_prev = e
        F_cmd = np.zeros((n_motes, 3))
        off = np.zeros(n_motes)
        for i in range(n_motes):
            if lost[i]:
                continue
            K = beams[i]
            idx, c = m18c.allocate(f_des[i], simps[i], invs[i])
            Kb = K[idx]
            a = c.copy()                              # spot centred on x_hat: g_hat = 1 by construction
            s = a.max() / caps[i]
            if s > 1:
                a = a / s
                sat += 1
            else:
                integ[i] += e[i]
            dx = x[i] - x_hat[i]
            rho2 = np.sum(dx ** 2) - (Kb @ dx) ** 2
            g = np.exp(-2 * rho2 / w2)
            F_cmd[i] = (a * g) @ Kb
            off[i] = math.sqrt(np.sum(dx ** 2))
        for ax in range(3):
            S = np.vstack([x[:, ax], vel[:, ax], F[:, ax]])
            S = Ad @ S + Bd[:, [0]] * uu[:, ax] + Bd[:, [1]] * F_cmd[:, ax]
            x[:, ax], vel[:, ax], F[:, ax] = S
        hist = np.roll(hist, 1, axis=0)
        hist[0] = x
        phist = np.roll(phist, 1, axis=0)
        phist[0] = plan(t + T)[0]                     # the plan at the time of the stored x (after this frame)
        if t > 0.2:
            newly = (off > r_lost_mult * w_spot) & ~lost
            t_lost[newly] = t
            lost |= newly
            if k % 10 == 0:
                pn, _ = plan(t + T)
                err_s.append(np.linalg.norm(x - pn, axis=1)[~lost])
                off_s.append(off[~lost])
    E = np.concatenate(err_s) if err_s else np.array([np.nan])
    O = np.concatenate(off_s) if off_s else np.array([np.nan])
    t_eff = float(np.sum(np.minimum(t_lost, dur) - 0.2))
    nl = int(lost.sum())
    return dict(case=cname, draft=dname, U_mean=U_mean, w_um=w_spot * 1e6, v=v_plan, f_r=f_r, R_mm=R * 1e3,
                sig_noise_um=sig_n * 1e6,
                err_p50_um=float(np.nanpercentile(E, 50) * 1e6), err_p999_um=float(np.nanpercentile(E, 99.9) * 1e6),
                off_p999_um=float(np.nanpercentile(O, 99.9) * 1e6), lost=nl, n_motes=n_motes, mote_seconds=t_eff,
                loss_95_upper=(3.0 if nl == 0 else nl + 2 * math.sqrt(nl)) / t_eff, sat_frac=sat / (n_fr * n_motes))


def main(quick=False):
    rows = []
    drafts = [m18b.DRAFTS[0], m18b.DRAFTS[3], m18b.DRAFTS[4]]
    for case in CASES:
        for draft in drafts:
            for w in (35e-6, 50e-6):
                for v in (0.5, 0.8):
                    seed = zlib.crc32(f"pov{case[0]}{draft[0]}{w}{v}".encode()) % 100000
                    r = simulate(case, draft, w, v_plan=v, n_motes=20 if quick else 40, dur=2.0 if quick else 6.0,
                                 seed=seed)
                    rows.append(r)
                    print(f"  {case[0]:15s} {draft[0]:24s} w {w * 1e6:3.0f} um v {v:3.1f} m/s (R {r['R_mm']:.1f} mm): "
                          f"draw err p50 {r['err_p50_um']:5.1f} p99.9 {r['err_p999_um']:6.1f} um; spot offset p99.9 "
                          f"{r['off_p999_um']:5.1f} um; lost {r['lost']}/{r['n_motes']} in {r['mote_seconds']:.0f} mote-s; "
                          f"sat {r['sat_frac']:.1e}", flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m19b_pov_track.json"), "w") as fh:
        json.dump(rows, fh, indent=1, default=float)


def main_grid2(out_dir):
    """Smaller spots (the eye-limited w of m19 with M17-derived s': 31-35 um sketch, 25-28 um film) and sensing noise."""
    rows = []
    cases = CASES[1:] + [("channel 40 kHz", 40000.0, 2, 0.015e-3)]
    for case in cases:
        for draft in (m18b.DRAFTS[0], m18b.DRAFTS[3], m18b.DRAFTS[4]):
            for w in (25e-6, 30e-6, 35e-6):
                for sig_n in (4e-6, 2e-6):
                    seed = zlib.crc32(f"pov2{case[0]}{draft[0]}{w}{sig_n}".encode()) % 100000
                    r = simulate(case, draft, w, v_plan=0.5, sig_n=sig_n, n_motes=40, dur=6.0, seed=seed)
                    rows.append(r)
                    print(f"  {case[0]:15s} {draft[0]:24s} w {w * 1e6:3.0f} um noise {sig_n * 1e6:.0f} um v 0.5: draw err p50 "
                          f"{r['err_p50_um']:5.1f} p99.9 {r['err_p999_um']:6.1f} um; offset p99.9 {r['off_p999_um']:5.1f}; "
                          f"lost {r['lost']}/{r['n_motes']} in {r['mote_seconds']:.0f} mote-s; sat {r['sat_frac']:.1e}",
                          flush=True)
                    with open(os.path.join(out_dir, "m19b_pov_track_grid2.json"), "w") as fh:
                        json.dump(rows, fh, indent=1, default=float)


if __name__ == "__main__":
    if "--grid2" in sys.argv:
        main_grid2(sys.argv[sys.argv.index("--grid2") + 1])
    else:
        main(quick="--quick" in sys.argv)

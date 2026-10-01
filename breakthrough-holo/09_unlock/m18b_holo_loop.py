"""M18b: can the hologram itself be the pinning actuator? Loop error for a hologram-rate loop (no DMD) in still air.

Uses red team 6's validated loop machinery (rt6_check: von Karman + Pao drafts, exact discretisation, PID tuning with
modulus margin <= 2, time-domain simulation with saturation). Changes from RT6's DMD cases:
- frame rate 0.5-1.44 kHz (LCoS / PLM-class phase modulators);
- the modulator's own response is a first-order lag tau_LC on the commanded force (it replaces the mote's l=1 thermal
  lag, which is microseconds);
- continuous amplitude (levels = 0) or 256 levels;
- camera centroid noise of 3-6 um per frame;
- authority 5.4 sigma (RT6 C1); the mote is the 1 um ITO-aerogel mote of M18.

Run: python3 m18b_holo_loop.py  -> results/m18b_holo_loop.json
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

A_MOTE, RHO, CP, KP = 1.0e-6, 150.0, 800.0, 0.04
CASES = [  # name, frame rate (Hz), latency frames, modulator lag (s)
    ("PLM 1.44 kHz", 1440.0, 2, 0.1e-3),
    ("LCoS 1 kHz", 1000.0, 2, 0.5e-3),
    ("LCoS 500 Hz", 500.0, 2, 1.0e-3),
    ("PLM 1.44 kHz, 1-frame latency", 1440.0, 1, 0.1e-3),
    ("MEMS 3 kHz", 3000.0, 2, 0.05e-3),
    ("MEMS 5 kHz", 5000.0, 2, 0.03e-3),
    ("MEMS 10 kHz", 10000.0, 2, 0.02e-3),
]
DRAFTS = [  # name, u_rms per component, L, convection speed Uc
    ("still, L 3 cm", 0.03, 0.03, 0.03),
    ("still, L 10 cm", 0.03, 0.10, 0.03),
    ("home, L 3 cm", 0.03, 0.03, 0.05),
    ("quiet office, L 3 cm", 0.03, 0.03, 0.10),
    ("office sigma 0.1, L 3 cm", 0.10, 0.03, 0.10),
]


def run(quick=False):
    tp, tf_mote = rt6.mote_times(A_MOTE, RHO, CP, KP)
    print(f"mote a {A_MOTE * 1e6:.1f} um: tau_p {tp * 1e6:.1f} us, l=1 thermal lag {tf_mote * 1e6:.2f} us")
    out = dict(tau_p=tp, tau_F_mote=tf_mote, rows=[])
    for cname, f_fr, d, tau_lc in CASES:
        T = 1 / f_fr
        tau_F = tau_lc + tf_mote
        for dname, u, L, Uc in DRAFTS:
            fturb, Sturb, eta, nu0 = rt6.turb_norm(u, L, Uc)
            sel = (fturb > 1e-3) & (fturb < 0.45 * f_fr)
            w_max = 5.4 * u
            for sig_n in (3e-6, 6e-6):
                best = rt6.tune(tp, tau_F, T, d, fturb[sel][::4], Sturb[sel][::4], sig_n, 0.0)
                if best is None:
                    print(f"  {cname:30s} {dname:22s} noise {sig_n * 1e6:.0f} um: no stable tuning")
                    continue
                tot, K, st, sn, sq, Ms = best
                fc = rt6.crossover_hz(rt6.plant_resp(tp, tau_F, T, d, fturb[sel][::4]), K)
                seed = zlib.crc32(f"{cname}{dname}{sig_n}".encode()) % 100000
                r = rt6.simulate(tp, tau_F, T, d, K, u, L, Uc, sig_n, w_max, 0, n_motes=40 if quick else 120,
                                 dur=4.0 if quick else 20.0, seed=seed, fs_t=4000.0)
                rec = dict(case=cname, draft=dname, f_frame=f_fr, latency_ms=d * T * 1e3, tau_lc_ms=tau_lc * 1e3,
                           u_rms=u, L=L, Uc=Uc, nu0_Hz=nu0, sig_noise_um=sig_n * 1e6, f_c_Hz=fc, Ms=Ms,
                           freq_sigma_um=tot * 1e6, freq_turb_um=st * 1e6, freq_noise_um=sn * 1e6, **r)
                out["rows"].append(rec)
                print(f"  {cname:30s} {dname:22s} noise {sig_n * 1e6:.0f} um: f_c {fc:5.1f} Hz  sigma (freq) {tot * 1e6:5.2f} um "
                      f"[turb {st * 1e6:5.2f}, noise {sn * 1e6:4.2f}]  sim sigma_x {r['sigma_x_um']:5.2f} um  r_p99.9 "
                      f"{r['r_p999_um']:5.1f}  r_max {r['r_max_um']:5.1f} um  sat {r['sat_frac']:.1e}  "
                      f"exceed/s {r['first_exceed_rate_per_s']}")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m18b_holo_loop.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    return out


def simulate_gauss(tau_p, tau_F, T, d, K, u_rms, L, Uc, sig_n, w_max, w_spot, n_motes=120, dur=20.0, seed=0,
                   fs_t=4000.0, r_lost=None, gain_schedule=True):
    """rt6.simulate with the Gaussian spot's position-dependent force: the delivered force on every axis is the
    commanded force times exp(-2 r^2 / w_spot^2), r the mote's radial offset from the spot centre (all beams share
    the focus). This is pessimistic: with several beams, a displacement along a pushing beam's axis costs no force.
    gain_schedule: the controller divides its command by the spot factor at the measured position (it knows the beam
    profile), within the authority. A mote is counted lost once r exceeds r_lost (default 1.5 w_spot), where the
    force has fallen to 1 %."""
    rng = np.random.default_rng(seed)
    Ad, Bd = rt6.discretise(*rt6.plant_ss(tau_p, tau_F), T)
    r_lost = 1.5 * w_spot if r_lost is None else r_lost
    n_fr = int(dur / T)
    n_t = int(dur * fs_t) + 2
    M = 3 * n_motes
    U = rt6.synth_turb(M, n_t, fs_t, u_rms, L, Uc, rng)
    s = np.zeros((3, M))
    hist = np.zeros((d + 1, M))
    Kp, Ki, Kd = K
    integ = np.zeros(M)
    if Ki > 0:                       # start in equilibrium: the integrator already balances the initial air velocity
        integ = -U[:, 0].astype(float) / (Ki * T)
    e_prev = np.zeros(M)
    lost = np.zeros(n_motes, bool)
    t_lost = np.full(n_motes, np.inf)
    r_max = np.zeros(n_motes)
    samples = []
    for k in range(n_fr):
        t = k * T
        it = t * fs_t
        i0 = int(it)
        fr = it - i0
        u = U[:, i0] * (1 - fr) + U[:, i0 + 1] * fr
        y = hist[-1] + sig_n * rng.standard_normal(M)
        e = -y
        wc_raw = Kp * e + Ki * T * integ + Kd * (e - e_prev) / T
        e_prev = e
        if gain_schedule:            # the controller divides by the spot factor at the MEASURED (delayed, noisy) position
            ry = np.sqrt(y[0::3] ** 2 + y[1::3] ** 2 + y[2::3] ** 2)
            g_hat = np.repeat(np.maximum(np.exp(-2 * ry * ry / (w_spot * w_spot)), 0.05), 3)
        else:
            g_hat = 1.0
        amp_raw = wc_raw / g_hat
        amp = np.clip(amp_raw, -w_max, w_max)      # beam amplitude limited by the authority (peak intensity)
        integ += np.where(np.abs(amp_raw) < w_max, e, 0.0)
        r = np.sqrt(s[0, 0::3] ** 2 + s[0, 1::3] ** 2 + s[0, 2::3] ** 2)
        g = np.repeat(np.exp(-2 * r * r / (w_spot * w_spot)), 3)
        s = Ad @ s + Bd[:, [0]] * u + Bd[:, [1]] * (amp * g)
        hist = np.roll(hist, 1, axis=0)
        hist[0] = s[0]
        r = np.sqrt(s[0, 0::3] ** 2 + s[0, 1::3] ** 2 + s[0, 2::3] ** 2)
        if t > 0.2:
            newly = (r > r_lost) & ~lost
            t_lost[newly] = t
            lost |= newly
            r_max = np.maximum(r_max, np.where(lost, r_max, r))
            if k % 20 == 0:
                samples.append(r[~lost].copy())
    R = np.concatenate(samples) if samples else np.zeros(0)
    if R.size == 0:
        R = np.array([np.nan])
    t_eff = float(np.sum(np.minimum(t_lost, dur) - 0.2))
    return dict(r_p50_um=float(np.percentile(R, 50) * 1e6), r_p999_um=float(np.percentile(R, 99.9) * 1e6),
                r_max_um=float(r_max.max() * 1e6), lost=int(lost.sum()), mote_seconds=t_eff,
                loss_rate_per_s=float(lost.sum() / t_eff), loss_rate_95_upper=float(3.0 / t_eff if lost.sum() == 0
                                                                                   else (lost.sum() + 2 * math.sqrt(lost.sum())) / t_eff))


def run_gauss(quick=False):
    """Loss rate of a 1 um mote in a Gaussian spot of waist w for the realistic modulators, still/home/quiet-office."""
    tp, tf_mote = rt6.mote_times(A_MOTE, RHO, CP, KP)
    out = []
    for cname, f_fr, d, tau_lc in (CASES[3], CASES[4], CASES[5]):
        T = 1 / f_fr
        tau_F = tau_lc + tf_mote
        for dname, u, L, Uc in (DRAFTS[0], DRAFTS[2], DRAFTS[3]):
            fturb, Sturb, eta, nu0 = rt6.turb_norm(u, L, Uc)
            sel = (fturb > 1e-3) & (fturb < 0.45 * f_fr)
            sig_n = 4e-6
            best = rt6.tune(tp, tau_F, T, d, fturb[sel][::4], Sturb[sel][::4], sig_n, 0.0)
            for w in (25e-6, 35e-6, 50e-6):
                seed = zlib.crc32(f"g{cname}{dname}{w}".encode()) % 100000
                r = simulate_gauss(tp, tau_F, T, d, best[1], u, L, Uc, sig_n, 5.4 * u, w,
                                   n_motes=40 if quick else 150, dur=4.0 if quick else 30.0, seed=seed)
                r.update(case=cname, draft=dname, w_um=w * 1e6, sig_noise_um=sig_n * 1e6)
                out.append(r)
                print(f"  GAUSS {cname:30s} {dname:22s} w {w * 1e6:3.0f} um: r_p50 {r['r_p50_um']:5.1f} r_p99.9 "
                      f"{r['r_p999_um']:5.1f} r_max {r['r_max_um']:5.1f} um  lost {r['lost']}/{150 if not quick else 40} "
                      f"over {r['mote_seconds']:.0f} mote-s  (rate {r['loss_rate_per_s']:.1e}/s, 95% upper "
                      f"{r['loss_rate_95_upper']:.1e}/s)")
    with open(os.path.join(HERE, "results", "m18b_gauss_loss.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    return out


if __name__ == "__main__":
    if "--gauss" in sys.argv:
        run_gauss(quick="--quick" in sys.argv)
    else:
        run(quick="--quick" in sys.argv)

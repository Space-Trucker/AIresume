"""M25: static light-held voxels at 1310 nm (the O-band window, m24) with Gaussian or dipped spots, driven by a
slow hologram loop (LCoS 120/240 Hz, PLM 1.44 kHz) in home drafts with the mean wind.

The question. m24 raised the per-focus skin cap ×10, to 7.85 mW per 1 mm at 1310 nm. Can that headroom buy
dipped spots? Dipped spots have no Gaussian runaway (opus round 3, idea 5), and they cost ×2 power. If they work, a
commodity-rate hologram (≤ 240 Hz) with velocity feedforward could hold motes in a home. RT8's lesson is built in:
the light force is resolved INSIDE each frame (substeps), not held per frame.

Model (all [DERIVED] from the stated inputs):
- **Mote.** White PMMA, a = 5 um, with a Cs_xWO3/ITO 1.3 um skin. Overdamped with response tau_p, and a thermal
  force lag tau_F (rt6.mote_times). Force is expressed in speed units, F/gamma.
- **Air.** u(t) = U_mean e (random horizontal direction per mote) plus von Karman turbulence per component (rt6).
- **Heads.** Ten heads (rt6.H10). Each push is along its beam (head to mote). Allocation is the minimum-sum
  nonnegative facet solution (m18c).
- **Spot profile** g(x), x = rho^2/w^2, where rho is the offset across the beam from the spot centre:
  - Gaussian: e^-2x;
  - dip (LG00 + LG01 mix): (1 + 2x) e^-2x, flat to first order. It needs 2x the power for the same centre intensity.
- **Controller, once per frame T, with d frames of latency.**
  - It reads the position measured d frames earlier (noise sig_n), and estimates the mote velocity from successive
    measurements.
  - Air estimate: u_est = v_est - F_est, where F_est is the force it commanded then.
  - Command: f_des = -u_est - Kp (x_pred - home) - Ki integral, with x_pred = y + v_est (d T + T/2).
  - The spot is centred on x_pred (follow mode). Beam amplitudes are c / g(predicted offset ~ 0).
- **Power metric.** The run-mean of the SUMMED beam intensity at each focus (skin at the focus sees every beam) is
  divided by the per-focus mean cap and reported as P/cap.
- **Caps.** Per beam, the instantaneous amplitude is capped at peak_factor x the mean cap. The skin MPE allows much
  higher short-term exposure: 1.1e4 C_A t^0.25 J/m^2 gives ~31x for 0.1 s. The run-mean per-focus power is reported
  against the cap (EN 50689: 7.85 mW per 1 mm at 1310 nm, divided by s = 1.1).
- **Loss.** A mote is lost when its distance from its spot centre exceeds 1.5 w.

Run:
- `python3 m25_oband_static.py` -> results/m25_oband_static.json, results/m25_run.log
- `python3 m25_oband_static.py --quick`
"""
import json
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m18c_vector_pin as m18c  # noqa: E402
import rt6_check as rt6  # noqa: E402

I_UNIT = 1.5e7
CAP_FOCUS = 7.854e-3 / 1.1          # W, mean per focus at 1310 nm (EN 50689 skin via 1 mm, stacking 1.1)
A, RHO, CP, KP = 5e-6, 1190.0, 1420.0, 0.2
CASES = {  # name: frame rate, latency frames, modulator lag
    "LCoS 120 Hz": (120.0, 2, 4e-3),
    "MEMS 5 kHz (not commodity)": (5000.0, 2, 0.03e-3),
    "LCoS 240 Hz": (240.0, 2, 2e-3),
    "PLM 1.44 kHz": (1440.0, 2, 0.1e-3),
}
DRAFTS = {  # name: u_rms, L, Uc, U_mean
    "still room": (0.03, 0.03, 0.03, 0.0),
    "home": (0.03, 0.03, 0.05, 0.05),
    "quiet office": (0.03, 0.03, 0.10, 0.10),
    "office sigma 0.1": (0.10, 0.03, 0.10, 0.10),
}


def profile(x, kind):
    return np.exp(-2 * x) if kind == "gauss" else (1 + 2 * x) * np.exp(-2 * x)


def simulate(case, draft, w, kind, n_motes=30, dur=8.0, seed=0, sig_n=4e-6, fs=20000.0, peak_factor=10.0,
             bw_frac=1 / 25):
    f_fr, d, tau_lc = CASES[case]
    u_rms, L, Uc, U_mean = DRAFTS[draft]
    tau_p, tau_th = rt6.mote_times(A, RHO, CP, KP)
    tau_F = tau_th + tau_lc
    T = 1 / f_fr
    n_sub = max(4, int(round(fs * T)))
    h = T / n_sub
    prof_power = 1.0 if kind == "gauss" else 2.0
    v_cap = CAP_FOCUS / (I_UNIT * math.pi * w * w / 2 * prof_power)     # mean cap per beam, speed units
    a_max = peak_factor * v_cap
    rng = np.random.default_rng(seed)
    homes = m18c.CENTER + (rng.random((n_motes, 3)) * 2 - 1) * m18c.HALF
    beams, simps, invs = [], [], []
    for hm in homes:
        K = hm - m18c.HEADS
        K /= np.linalg.norm(K, axis=1)[:, None]
        s, iv = m18c.facets(K)
        beams.append(K)
        simps.append(s)
        invs.append(iv)
    ang = rng.random(n_motes) * 2 * math.pi
    Umean = U_mean * np.stack([np.cos(ang), np.sin(ang), np.zeros(n_motes)], 1)
    n_fr = int(dur * f_fr)
    n_t = n_fr * n_sub + 2
    if u_rms > 0:
        Ut = rt6.synth_turb(3 * n_motes, n_t, 1 / h, u_rms, L, Uc, rng).reshape(n_motes, 3, n_t)
    else:
        Ut = np.zeros((n_motes, 3, n_t), np.float32)
    x = homes.copy()
    u0 = Umean + Ut[:, :, 0]
    F = -u0.copy()                                  # start in equilibrium
    v = np.zeros((n_motes, 3))
    D = (d + 0.5) * T + tau_F                       # loop delay
    Kp = 0.5 / D                                    # single-integrator plant with delay: Kp D ~ 0.5
    Ki = Kp * Kp / 4
    integ = np.zeros((n_motes, 3))
    v_f = np.zeros((n_motes, 3))
    beta = 0.3                                      # velocity low-pass per frame
    y_hist = [x.copy() for _ in range(d + 2)]
    spot = x.copy()
    idx_all = np.zeros((n_motes, 3), int)
    amp = np.zeros((n_motes, 3))
    for i in range(n_motes):
        idx, c = m18c.allocate(F[i], simps[i], invs[i])
        idx_all[i] = idx
        amp[i] = c
    integ = -F / Ki                                 # integrator starts at the equilibrium force
    lost = np.zeros(n_motes, bool)
    t_lost = np.full(n_motes, np.inf)
    pw_acc = np.zeros(n_motes)                      # time integral of the summed beam amplitudes at the focus
    home_err, spot_off = [], []
    sat = 0
    k_t = 0
    for k in range(n_fr):
        t = k * T
        # ---- controller (uses data d frames old): PID on the predicted position, spot on the prediction
        y_m = y_hist[-(d + 1)] + sig_n * rng.standard_normal((n_motes, 3))
        y_m1 = y_hist[-(d + 2)] + sig_n * rng.standard_normal((n_motes, 3))
        v_f += beta * ((y_m - y_m1) / T - v_f)
        x_pred = y_m + v_f * (d * T + T / 2)
        err = x_pred - homes
        integ += err * T
        f_des = -Kp * err - Ki * integ
        spot = x_pred
        for i in range(n_motes):
            if lost[i]:
                continue
            idx, c = m18c.allocate(f_des[i], simps[i], invs[i])
            s_ = c.max() / a_max
            if s_ > 1:
                c = c / s_
                sat += 1
            idx_all[i] = idx
            amp[i] = c
        # ---- plant, n_sub substeps with the hologram held
        for j in range(n_sub):
            uu = Umean + Ut[:, :, k_t]
            k_t += 1
            Kb = np.stack([beams[i][idx_all[i]] for i in range(n_motes)])          # (n, 3 beams, 3)
            dx = x - spot
            along = np.einsum("nbk,nk->nb", Kb, dx)
            rho2 = np.sum(dx * dx, axis=1)[:, None] - along ** 2
            g = profile(np.maximum(rho2, 0.0) / (w * w), kind)
            F_inst = np.einsum("nb,nbk->nk", amp * g, Kb)
            F += h * (F_inst - F) / tau_F
            v += h * (uu + F - v) / tau_p if tau_p > h else (uu + F - v)
            x += h * v
            pw_acc += h * amp.sum(axis=1)                 # all beams converge on the focus (skin sees the sum)
        y_hist.append(x.copy())
        y_hist.pop(0)
        off = np.linalg.norm(x - spot, axis=1)
        if t > 0.3:
            newly = (off > 1.5 * w) & ~lost
            t_lost[newly] = t
            lost |= newly
            if k % 5 == 0:
                home_err.append(np.linalg.norm(x - homes, axis=1)[~lost])
                spot_off.append(off[~lost])
    HE = np.concatenate(home_err) if home_err else np.array([np.nan])
    SO = np.concatenate(spot_off) if spot_off else np.array([np.nan])
    t_eff = float(np.sum(np.minimum(t_lost, dur) - 0.3))
    mean_pw = pw_acc / (n_fr * T) / v_cap
    return dict(case=case, draft=draft, w_um=w * 1e6, profile=kind, v_cap_mean=v_cap, lost=int(lost.sum()),
                n=n_motes, mote_s=t_eff, home_p50_um=float(np.nanpercentile(HE, 50) * 1e6),
                home_p99_um=float(np.nanpercentile(HE, 99) * 1e6), spot_off_p99_um=float(np.nanpercentile(SO, 99) * 1e6),
                mean_power_over_cap_max=float(np.max(mean_pw[~lost])) if (~lost).any() else float("nan"),
                mean_power_over_cap_p50=float(np.median(mean_pw[~lost])) if (~lost).any() else float("nan"),
                sat_frac=sat / max(1, n_fr * n_motes), tau_p_ms=tau_p * 1e3, tau_th_ms=tau_th * 1e3)


def selftest():
    # still air, no turbulence: a mote must stay at home
    DRAFTS["zero"] = (0.0, 0.03, 0.05, 0.0)
    r = simulate("PLM 1.44 kHz", "zero", 70e-6, "gauss", n_motes=4, dur=0.5, seed=1)
    ok = r["lost"] == 0
    x = np.linspace(0, 0.2, 5)
    ok &= np.all(np.abs(profile(x, "dip")[:2] - 1) < 0.05)
    print(f"selftest: PLM home w70 gauss lost {r['lost']}/4, dip flat near centre -> {'PASS' if ok else 'FAIL'}")
    return ok


def main(quick=False):
    assert selftest()
    rows = []
    grid = []
    for case in ("LCoS 240 Hz", "PLM 1.44 kHz", "MEMS 5 kHz (not commodity)"):
        for draft in ("still room", "home", "quiet office"):
            for w in (40e-6, 55e-6, 70e-6, 100e-6):
                for kind in ("gauss", "dip"):
                    grid.append((case, draft, w, kind))
    if quick:
        grid = [g for g in grid if g[1] == "home" and g[2] == 70e-6]
    print(f"{'case':27s} {'draft':12s} {'w':>4s} {'prof':5s} {'v_cap':>6s} {'lost':>6s} {'home p50/p99 um':>16s} "
          f"{'spot p99':>8s} {'P/cap p50/max':>14s} {'sat':>6s}")
    for case, draft, w, kind in grid:
        seed = zlib.crc32(f"{case}{draft}{w}{kind}".encode()) % 100000
        r = simulate(case, draft, w, kind, seed=seed, n_motes=20, dur=3.0 if quick else 5.0)
        rows.append(r)
        print(f"{case:27s} {draft:12s} {w * 1e6:4.0f} {kind:5s} {r['v_cap_mean']:6.3f} {r['lost']:3d}/{r['n']:<2d} "
              f"{r['home_p50_um']:7.0f}/{r['home_p99_um']:<7.0f} {r['spot_off_p99_um']:8.1f} "
              f"{r['mean_power_over_cap_p50']:6.2f}/{r['mean_power_over_cap_max']:<6.2f} {r['sat_frac']:6.3f}", flush=True)
        out_dir = os.environ.get("M25_OUT", os.path.join(HERE, "results"))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "m25_oband_static.json"), "w") as fh:
            json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)

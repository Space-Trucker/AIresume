"""E6: How loud is a plasma display, and can smart spark ORDERING and TIMING make it quiet?

Every voxel is a tiny blast wave. Energy in the audible band comes from how the click train
*arrives* at an ear. For a zero-mean N-wave s(t), below its corner frequency its spectrum is
S(f) ~ i 2 pi f M1, so the audible pressure at a listener is set by
    G(f) = sum_k (1/r_k) exp(-i 2 pi f (t_k + r_k / c))
i.e. by the low-frequency structure of the arrival process.

Random order gives Poisson-like G (Campbell's theorem, the incoherent floor used in
display_budget.audible_spl_random). This script computes |G(f)|^2 in each audible 1/3-octave band
for several orderings, relative to random, and so gives the dB(A) change for each strategy:
  1. random     : random permutation every frame, constant laser rate
  2. path       : natural stroke order (how a vector display is usually drawn)
  3. stratified : bit-reversal interleave of a space-filling order (every short window samples
                  the whole object evenly)
  4. listener-locked (NEW): firing time t_k = slot_k - r_k/c so that clicks ARRIVE periodically
                  at a tracked listener, with voxels assigned to slots sorted by distance
Listeners: the tracked one (L0), plus untracked ones in other directions.
Validation: the random ordering must reproduce the analytic incoherent level within ~1 dB.
"""
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import C_SOUND, RESULTS, save_json
from display_budget import A_WEIGHT_TABLE, audible_spl_random

rng = np.random.default_rng(7)


def armor_wireframe(spacing=2e-3):
    """Iron-Man-like test content: helmet ellipsoid, torso rings, arc-reactor circle, limbs."""
    pts = []

    def add_curve(xyz):
        seg = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(seg)])
        n = max(2, int(s[-1] / spacing))
        si = np.linspace(0, s[-1], n)
        pts.append(np.stack([np.interp(si, s, xyz[:, i]) for i in range(3)], axis=1))

    t = np.linspace(0, 2 * np.pi, 400)
    # helmet: 6 latitude + 6 longitude rings on an ellipsoid centred at z=1.55
    for lat in np.linspace(-0.8, 0.8, 6):
        r = 0.10 * np.cos(lat)
        add_curve(np.stack([r * np.cos(t), r * np.sin(t), 1.55 + 0.13 * np.sin(lat) + 0 * t], 1))
    for lon in np.linspace(0, np.pi, 6, endpoint=False):
        u = np.linspace(-np.pi / 2, np.pi / 2, 200)
        add_curve(np.stack([0.10 * np.cos(u) * np.cos(lon), 0.10 * np.cos(u) * np.sin(lon), 1.55 + 0.13 * np.sin(u)], 1))
    # torso: 10 elliptic rings z = 0.95..1.40
    for z in np.linspace(0.95, 1.40, 10):
        add_curve(np.stack([0.20 * np.cos(t), 0.12 * np.sin(t), z + 0 * t], 1))
    # arc reactor
    add_curve(np.stack([0.04 * np.cos(t), -0.125 + 0 * t, 1.28 + 0.04 * np.sin(t)], 1))
    # limbs: 4 lines with rings
    for x0, sgn in ((0.24, 1), (-0.24, -1)):
        add_curve(np.array([[x0, 0, 1.38], [x0 + 0.08 * sgn, 0, 1.05], [x0 + 0.10 * sgn, 0, 0.78]]))
    for x0 in (0.10, -0.10):
        add_curve(np.array([[x0, 0, 0.95], [x0, 0, 0.50], [x0, 0, 0.05]]))
    return pts   # list of polylines (strokes)


def orderings(strokes):
    path = np.concatenate(strokes, axis=0)
    n = len(path)
    out = {"path": path}
    out["random"] = None  # generated per frame
    # stratified: order along a space-filling-ish key (morton code), then bit-reversal interleave
    q = ((path - path.min(0)) / (np.ptp(path, 0).max() + 1e-9) * 1023).astype(np.int64)

    def spread(v):
        v = v & 0x3FF
        v = (v | (v << 16)) & 0x030000FF
        v = (v | (v << 8)) & 0x0300F00F
        v = (v | (v << 4)) & 0x030C30C3
        v = (v | (v << 2)) & 0x09249249
        return v
    morton = spread(q[:, 0]) | (spread(q[:, 1]) << 1) | (spread(q[:, 2]) << 2)
    idx = np.argsort(morton)
    bits = int(math.ceil(math.log2(n)))
    rev = np.array([int(format(i, f"0{bits}b")[::-1], 2) for i in range(2 ** bits)])
    rev = rev[rev < n]
    out["stratified"] = path[idx][rev]
    return out, path


def arrival_spectrum(src_pts, t_emit, listener, freqs, amp=None):
    r = np.linalg.norm(src_pts - listener, axis=1)
    tau = t_emit + r / C_SOUND
    a = (1.0 / r) if amp is None else amp / r
    G = np.zeros(len(freqs), dtype=complex)
    ch = 20000
    w = np.hanning(len(tau))      # taper to avoid edge leakage
    for i in range(0, len(tau), ch):
        ph = np.exp(-2j * np.pi * np.outer(freqs, tau[i:i + ch]))
        G += ph @ (a[i:i + ch] * w[i:i + ch])
    return np.abs(G) ** 2 / np.sum(w ** 2)


def band_freqs(n_per=40):
    fb = {}
    for fc in A_WEIGHT_TABLE:
        f1, f2 = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)
        fb[fc] = rng.uniform(f1, f2, n_per)
    return fb


def run(frame_hz=60.0, frames=12, listeners=None):
    strokes = armor_wireframe()
    ords, path = orderings(strokes)
    n = len(path)
    rate = n * frame_hz
    T = 1.0 / rate
    print(f"  content: {len(strokes)} strokes, {n} voxels/frame, voxel rate {rate:.3g}/s")
    center = path.mean(0)
    listeners = listeners or {
        "L0 tracked, front 1.2 m": center + np.array([0, -1.2, 0.2]),
        "L1 side 1.5 m": center + np.array([1.5, 0, 0.2]),
        "L2 behind 2 m": center + np.array([0, 2.0, 0.0]),
        "L3 diagonal 1 m": center + np.array([0.7, -0.7, 0.3]),
    }
    L0 = list(listeners.values())[0]
    fb = band_freqs()
    freqs = np.concatenate(list(fb.values()))
    res = {}
    for name in ("random", "path", "stratified", "listener_locked"):
        pts_all, t_all = [], []
        for fr in range(frames):
            t0 = fr / frame_hz
            if name == "random":
                P = path[rng.permutation(n)]
                t = t0 + np.arange(n) * T
            elif name in ("path", "stratified"):
                P = ords[name]
                t = t0 + np.arange(n) * T
            else:
                # listener-locked: sort by distance to L0, arrivals exactly periodic at L0
                r0 = np.linalg.norm(path - L0, axis=1)
                P = path[np.argsort(r0)]
                rs = np.sort(r0)
                t = t0 + np.arange(n) * T - (rs - rs.mean()) / C_SOUND
            pts_all.append(P)
            t_all.append(t)
        Pa = np.concatenate(pts_all)
        ta = np.concatenate(t_all)
        res[name] = {}
        for lname, L in listeners.items():
            psd = arrival_spectrum(Pa, ta, L, freqs)
            # per-band mean relative to random-Poisson expectation: E|G|^2 = <1/r^2> (per click)
            r = np.linalg.norm(Pa - L, axis=1)
            poisson = np.mean(1.0 / r ** 2)
            k = 0
            bands = {}
            for fc, fr_ in fb.items():
                m = len(fr_)
                bands[fc] = float(np.mean(psd[k:k + m]) / poisson)
                k += m
            res[name][lname] = bands
    return res, n, rate, listeners


if __name__ == "__main__":
    print("E6 acoustic scheduling")
    res, n, rate, listeners = run()
    # reference operating point: dim-lab strokes 5 cd/m^2 -> E per flash from display_budget
    from display_budget import energy_per_flash
    E = energy_per_flash(5.0)
    base = float(audible_spl_random(rate, E))
    print(f"  reference: E={E*1e6:.2f} uJ/flash, random-order level {base:.1f} dB(A) (analytic incoherent floor)")
    summary = {}
    for name, per_l in res.items():
        summary[name] = {}
        for lname, bands in per_l.items():
            # A-weighted change relative to random: weight each band by its random-case A-weighted share
            from display_budget import nwave_duration, P as PP
            from scipy.special import gammainc
            E_ac = PP("f_ac") * E
            Tn = nwave_duration(E_ac)
            fcn = 1 / (math.pi * Tn)
            num = den = 0.0
            for fc, ratio in bands.items():
                f1, f2 = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)
                w = (gammainc(1.5, (f2 / fcn) ** 2) - gammainc(1.5, (f1 / fcn) ** 2)) * 10 ** (A_WEIGHT_TABLE[fc] / 10)
                num += w * ratio
                den += w
            d = 10 * math.log10(num / den)
            summary[name][lname] = dict(delta_dB=d, dBA=base + d)
            print(f"  {name:16s} {lname:24s}  {d:+6.1f} dB  ->  {base + d:5.1f} dB(A)")
    save_json("e6_acoustic_scheduling.json", dict(voxels_per_frame=n, voxel_rate=rate, E_flash=E,
                                                   random_dBA=base, results=res, summary=summary))
    # plot
    fig, ax = plt.subplots(figsize=(8, 4.2))
    names = list(summary.keys())
    lnames = list(listeners.keys())
    wbar = 0.2
    for j, ln in enumerate(lnames):
        ax.bar(np.arange(len(names)) + (j - 1.5) * wbar, [summary[nm][ln]["dBA"] for nm in names], wbar, label=ln)
    ax.axhline(35, color="k", ls="--", lw=1)
    ax.text(len(names) - 0.6, 36, "home limit 35 dB(A)", ha="right", fontsize=8)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names)
    ax.set_ylabel("audible noise, dB(A)")
    ax.set_title(f"Plasma display noise vs spark scheduling ({n} voxels/frame, 5 cd/m² strokes)")
    ax.legend(fontsize=7)
    plt.tight_layout(); plt.savefig(f"{RESULTS}/e6_acoustic_scheduling.png", dpi=120); plt.close()
    print("  saved results/e6_acoustic_scheduling.json/.png")

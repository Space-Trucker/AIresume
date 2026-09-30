"""E6c: 'Subsonic multi-channel stroke tracing': cut the TOTAL radiated audible noise (all
directions, reverberation included) by drawing like a quiet moving source.

Physics: a click train that is (i) regular at a rate above the audio band (40 kHz) and (ii)
advances along a smooth stroke slower than sound (trace Mach number M = v/c < 1) has no audio-band
far-field radiation except from stroke ends, jumps and changes of velocity. It behaves like a
subsonically moving steady source; the audio-band phase per click never accumulates coherently. A
supersonic trace (E6 'path', Mach 3) does the opposite and builds Mach waves (+8 dB).

We give K parallel beam channels (AOD channels) their own strokes, trace each at f_ch clicks/s with
3 mm spacing (v = 120 m/s, M = 0.35), interleave the channels in time, repeat identical frames at
60 Hz, and compute the audible (A-weighted, N-wave-weighted) power at the frame harmonics in 96
far-field directions (a sphere at 4 m) plus near listeners, relative to random order.
Averaged over the sphere, this is the change in TOTAL radiated audible power, which is what sets
the reverberant level in a room.
"""
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import C_SOUND, RESULTS, save_json
from sim_e6_acoustic_scheduling import armor_wireframe
from sim_e6b_multilistener_phase_scheduling import W, w_ang, FRAME_HZ

rng = np.random.default_rng(5)


def fibonacci_sphere(n, R, c):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = np.pi * (1 + 5 ** 0.5) * i
    return c + R * np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


def audible_rel(P, t, listeners):
    """A-weighted audible power at each listener, relative to the random (Campbell) expectation."""
    out = []
    for L in listeners:
        r = np.linalg.norm(P - L, axis=1)
        a = 1.0 / r
        g = (np.exp(-1j * np.outer(w_ang, t + r / C_SOUND)) * a[None, :]).sum(1)
        out.append(np.sum(W * np.abs(g) ** 2) / (np.sum(a ** 2) * np.sum(W)))
    return 10 * np.log10(np.array(out))


def schedule_subsonic(strokes, K, f_ch, spacing, ramp=0):
    """Assign strokes to K channels (greedy load balance), trace each channel's strokes back to
    back at f_ch clicks/s (continuous train, no gaps within a frame), interleave channels in time."""
    loads = [[] for _ in range(K)]
    counts = np.zeros(K, int)
    order = sorted(range(len(strokes)), key=lambda i: -len(strokes[i]))
    for i in order:
        k = int(np.argmin(counts))
        loads[k].append(i)
        counts[k] += len(strokes[i])
    P, T, A = [], [], []
    dt = 1.0 / f_ch
    for k in range(K):
        n = 0
        for i in loads[k]:
            st = strokes[i]
            for j, p in enumerate(st):
                P.append(p)
                T.append(n * dt + k * dt / K)
                amp = 1.0
                if ramp:
                    amp = min(1.0, (j + 1) / ramp, (len(st) - j) / ramp)
                A.append(amp)
                n += 1
    return np.array(P), np.array(T), np.array(A), counts


if __name__ == "__main__":
    print("E6c subsonic multi-channel stroke tracing")
    spacing = 3e-3
    strokes = armor_wireframe(spacing)
    Pall = np.concatenate(strokes)
    n = len(Pall)
    c0 = Pall.mean(0)
    sphere = fibonacci_sphere(96, 4.0, c0)
    near = c0 + np.array([[0, -1.2, 0.2], [1.5, 0, 0.2], [0.7, -0.7, 0.3], [0, 2.0, 0.0]])
    res = {}
    # baseline: random order at the same total rate
    rate = n * FRAME_HZ
    t_rand = rng.permutation(n) / rate
    res["random"] = dict(sphere=audible_rel(Pall, t_rand, sphere), near=audible_rel(Pall, t_rand, near))
    # supersonic single-channel path order (E6 'path')
    t_path = np.arange(n) / rate
    res["path_supersonic_1ch"] = dict(sphere=audible_rel(Pall, t_path, sphere), near=audible_rel(Pall, t_path, near))
    for K, f_ch, ramp in ((12, 40e3, 0), (12, 40e3, 4), (24, 25e3, 4), (6, 80e3, 4)):
        P, T, Aamp, counts = schedule_subsonic(strokes, K, f_ch, spacing, ramp)
        frame_time = counts.max() / f_ch
        mach = spacing * f_ch / C_SOUND
        tag = f"subsonic_K{K}_f{int(f_ch/1e3)}k_M{mach:.2f}_ramp{ramp}"
        # amplitude ramps change per-click amplitude: include via weighting a (scale both sums)
        def rel(Ls):
            out = []
            for L in Ls:
                r = np.linalg.norm(P - L, axis=1)
                a = Aamp / r
                g = (np.exp(-1j * np.outer(w_ang, T + r / C_SOUND)) * a[None, :]).sum(1)
                out.append(np.sum(W * np.abs(g) ** 2) / (np.sum(a ** 2) * np.sum(W)))
            return 10 * np.log10(np.array(out))
        res[tag] = dict(sphere=rel(sphere), near=rel(near), frame_fill=float(frame_time * FRAME_HZ),
                        voxels_per_s=float(n * FRAME_HZ))
        print(f"  {tag:40s} frame fill {frame_time*FRAME_HZ*100:5.1f}% of 1/60 s")
    summ = {}
    for k, v in res.items():
        tot = 10 * np.log10(np.mean(10 ** (v["sphere"] / 10)))
        summ[k] = dict(total_radiated_dB=float(tot), sphere_worst_dB=float(v["sphere"].max()),
                       near_dB=[float(x) for x in v["near"]])
        print(f"  {k:40s} TOTAL radiated audible power {tot:+6.1f} dB vs random | worst direction {v['sphere'].max():+6.1f} | "
              f"near listeners {np.round(v['near'],1)}")
    save_json("e6c_subsonic_tracing.json", dict(voxels_per_frame=n, summary=summ))
    fig, ax = plt.subplots(figsize=(8, 4))
    ks = list(summ.keys())
    ax.bar(range(len(ks)), [summ[k]["total_radiated_dB"] for k in ks], color=["#888", "#c55"] + ["#4a7bd1"] * (len(ks) - 2))
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(len(ks))); ax.set_xticklabels([k.replace("_", "\n") for k in ks], fontsize=6)
    ax.set_ylabel("total radiated audible power vs random (dB)")
    ax.set_title("Subsonic multi-channel tracing: quiet in every direction (reverberation included)", fontsize=9)
    plt.tight_layout(); plt.savefig(f"{RESULTS}/e6c_subsonic_tracing.png", dpi=120); plt.close()
    print("  saved results/e6c_subsonic_tracing.json/.png")


# ---------------------------------------------------------------- robustness: shot-to-shot spark jitter
if __name__ == "__main__":
    print("  robustness to shot-to-shot absorbed-energy jitter (K=12, 40 kHz, ramp 4):")
    P, T, Aamp, counts = schedule_subsonic(strokes, 12, 40e3, spacing, 4)
    jit = {}
    for sigma in (0.05, 0.10, 0.20):
        A2 = Aamp * (1 + sigma * rng.standard_normal(len(Aamp)))
        vals = []
        for L in sphere[::3]:
            r = np.linalg.norm(P - L, axis=1)
            a = A2 / r
            g = (np.exp(-1j * np.outer(w_ang, T + r / C_SOUND)) * a[None, :]).sum(1)
            vals.append(np.sum(W * np.abs(g) ** 2) / (np.sum(a ** 2) * np.sum(W)))
        tot = 10 * np.log10(np.mean(vals))
        jit[sigma] = float(tot)
        print(f"    energy jitter {sigma*100:4.0f}% rms -> total radiated audible power {tot:+.1f} dB vs random "
              f"(jitter floor ~ {10*np.log10(sigma**2/(1+sigma**2)):+.1f} dB)")
    import json as _j
    _p = f"{RESULTS}/e6c_subsonic_tracing.json"
    _d = _j.load(open(_p)); _d["jitter"] = jit; _j.dump(_d, open(_p, "w"), indent=2)

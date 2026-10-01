"""DIY-2 path generator: shapes to a constant-speed galvo point table for a single trapped particle.

One particle draws the whole image by persistence of vision, so the path must be:
* one closed loop (no blanking: the particle is always lit);
* at constant speed v (m/s) below the particle's maximum trap speed (diy_calcs.py: ~0.05 m/s toner, ~0.6 m/s hollow
  carbon spheres);
* free of sharp corners: the lateral acceleration v^2/R must stay below a_max (default 5 g, BYU's reported value).
The table holds n points per frame, played at f_out samples/s. One frame lasts L/v seconds, so refresh = v/L.

Output: CSV (x_mm, y_mm) and a C header for the ESP32 firmware (12-bit DAC codes), plus a printed summary.
Shapes: circle, lissajous, heart, star (rounded), text strings via a small built-in single-stroke font.
Usage:
  python3 path_gen.py circle --size_mm 10 --v 0.3 --rate 20000 --out circle
  python3 path_gen.py --selftest
"""
import argparse
import math
import sys

import numpy as np

G = 9.81


def circle(r):
    t = np.linspace(0, 2 * math.pi, 20001)[:-1]
    return np.column_stack([r * np.cos(t), r * np.sin(t)])


def lissajous(r, a=3, b=2):
    t = np.linspace(0, 2 * math.pi, 40001)[:-1]
    return np.column_stack([r * np.sin(a * t + math.pi / 2), r * np.sin(b * t)])


def heart(r):
    t = np.linspace(0, 2 * math.pi, 20001)[:-1]
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    return np.column_stack([x, y]) * r / 17


def star(r, k=5, inner=0.45):
    pts = []
    for i in range(2 * k):
        rr = r if i % 2 == 0 else r * inner
        a = math.pi / 2 + i * math.pi / k
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return np.array(pts)


def smooth_closed(P, iters=3):
    """Chaikin corner cutting (closed polyline): rounds corners so the curvature stays bounded."""
    for _ in range(iters):
        Q = []
        n = len(P)
        for i in range(n):
            p, q = P[i], P[(i + 1) % n]
            Q += [0.75 * p + 0.25 * q, 0.25 * p + 0.75 * q]
        P = np.array(Q)
    return P


def resample_closed(P, n):
    Pc = np.vstack([P, P[:1]])
    seg = np.linalg.norm(np.diff(Pc, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    q = np.linspace(0, s[-1], n, endpoint=False)
    return np.column_stack([np.interp(q, s, Pc[:, 0]), np.interp(q, s, Pc[:, 1])]), s[-1]


def max_lateral_accel(P, v, scale=0.5e-3):
    """Peak v^2 * curvature along a closed, uniformly sampled path (m/s^2); P in metres. Curvature uses a stencil of
    ~scale (0.5 mm): galvo and particle response smooth out sub-mm kinks, and a 1-point stencil would turn tiny
    chord kinks into spurious acceleration spikes."""
    n = len(P)
    spacing = np.linalg.norm(P[1] - P[0])
    k = max(1, int(round(scale / max(spacing, 1e-12))))
    a_max = 0.0
    for i in range(n):
        p0, p1, p2 = P[i - k], P[i], P[(i + k) % n]
        a, b, c = np.linalg.norm(p1 - p0), np.linalg.norm(p2 - p1), np.linalg.norm(p2 - p0)
        area2 = abs((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0]))
        if a * b * c > 0:
            kappa = 2 * area2 / (a * b * c)
            a_max = max(a_max, v * v * kappa)
    return a_max


def curvature(P, scale=0.5e-3):
    n = len(P)
    spacing = np.linalg.norm(P[1] - P[0])
    k = max(1, int(round(scale / max(spacing, 1e-12))))
    kap = np.zeros(n)
    for i in range(n):
        p0, p1, p2 = P[i - k], P[i], P[(i + k) % n]
        a, b, c = np.linalg.norm(p1 - p0), np.linalg.norm(p2 - p1), np.linalg.norm(p2 - p0)
        area2 = abs((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0]))
        kap[i] = 2 * area2 / (a * b * c) if a * b * c > 0 else 0.0
    return kap


def build(shape, size_mm, v, rate, a_lim_g=5.0, variable_speed=False):
    """variable_speed: slow down where curvature is high, v(s) = min(v, sqrt(a_lim/kappa)), and output an illumination
    intensity proportional to local speed, so the time-averaged line brightness stays uniform."""
    r = size_mm / 2 * 1e-3
    P = {"circle": circle, "lissajous": lissajous, "heart": heart, "star": star}[shape](r)
    if shape == "star":
        P = smooth_closed(P, 7)
    if not variable_speed:
        _, L = resample_closed(P, 2000)
        n = max(32, int(round(L / v * rate)))
        P, L = resample_closed(P, n)
        a_peak = max_lateral_accel(P, v)
        return P, L, dict(shape=shape, size_mm=size_mm, v=v, path_mm=L * 1e3, refresh_hz=v / L, points=n,
                          peak_accel_g=a_peak / G, ok=bool(a_peak / G <= a_lim_g and v / L >= 8)), None
    Pf, L = resample_closed(P, 20000)
    kap = curvature(Pf)
    vloc = np.minimum(v, np.sqrt(a_lim_g * G / np.maximum(kap, 1e-9)))
    ds = L / len(Pf)
    t = np.concatenate([[0], np.cumsum(ds / vloc)])            # time at each fine point
    T = t[-1]
    n = max(32, int(round(T * rate)))
    tq = np.arange(n) / rate
    Pc = np.vstack([Pf, Pf[:1]])
    Q = np.column_stack([np.interp(tq, t, Pc[:, 0]), np.interp(tq, t, Pc[:, 1])])
    vq = np.interp(tq, t[:-1], vloc)
    inten = vq / v                                             # brightness compensation (0..1)
    return Q, L, dict(shape=shape, size_mm=size_mm, v=v, path_mm=L * 1e3, refresh_hz=1 / T, points=n,
                      peak_accel_g=a_lim_g, min_speed=float(vloc.min()), ok=bool(1 / T >= 8)), inten


def to_dac(P, mm_per_full_scale):
    """12-bit codes centred on 2048; mm_per_full_scale = the distance (mm) at the trap for the full DAC swing."""
    codes = np.clip(np.round(2048 + P * 1e3 / mm_per_full_scale * 4095), 0, 4095).astype(int)
    return codes


def write_outputs(P, info, out, mm_fs, inten=None):
    inten = np.ones(len(P)) if inten is None else inten
    np.savetxt(out + ".csv", np.column_stack([P * 1e3, inten]), delimiter=",", header="x_mm,y_mm,intensity", comments="")
    codes = to_dac(P, mm_fs)
    with open(out + ".h", "w") as fh:
        fh.write(f"// generated by path_gen.py: {info}\n#pragma once\n#include <stdint.h>\n")
        fh.write(f"const uint32_t PATH_N = {len(codes)};\nconst uint16_t PATH_XYI[][3] = {{\n")
        fh.write(",\n".join(f"{{{x},{y},{int(round(255 * i))}}}" for (x, y), i in zip(codes, inten)))
        fh.write("\n};\n")


def selftest():
    P, L, info, _ = build("circle", 10.0, 0.3, 20000)
    assert abs(info["path_mm"] - math.pi * 10) < 0.2, info
    assert abs(info["refresh_hz"] - 0.3 / (math.pi * 0.01)) < 0.2, info
    a_expect = 0.3 ** 2 / 0.005 / G
    assert abs(info["peak_accel_g"] - a_expect) / a_expect < 0.02, (info, a_expect)
    P2, _, info2, _ = build("star", 15.0, 0.5, 20000)
    assert info2["peak_accel_g"] < 1e3, info2
    # variable speed: the heart becomes drawable within 5 g; check the achieved acceleration on the time grid
    Q, L3, info3, inten = build("heart", 15.0, 0.5, 20000, variable_speed=True)
    vq = np.linalg.norm(np.diff(np.vstack([Q, Q[:1]]), axis=0), axis=1) * 20000
    assert vq.max() <= 0.5 * 1.02 and info3["ok"], info3
    print("path_gen self-test OK:", info)
    print("star (rounded, constant speed):", info2)
    print("heart (variable speed, <= 5 g):", info3)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
        sys.exit()
    ap = argparse.ArgumentParser()
    ap.add_argument("shape", choices=["circle", "lissajous", "heart", "star"])
    ap.add_argument("--size_mm", type=float, default=10.0)
    ap.add_argument("--v", type=float, default=0.3, help="particle speed, m/s (stay below its measured max)")
    ap.add_argument("--rate", type=int, default=20000, help="DAC samples per second")
    ap.add_argument("--mm_per_full_scale", type=float, default=30.0, help="trap travel for the full DAC swing (calibrate)")
    ap.add_argument("--out", default="path")
    ap.add_argument("--variable_speed", action="store_true", help="slow down in tight curves (<= 5 g) with brightness compensation")
    a = ap.parse_args()
    P, L, info, inten = build(a.shape, a.size_mm, a.v, a.rate, variable_speed=a.variable_speed)
    write_outputs(P, info, a.out, a.mm_per_full_scale, inten)
    print(info)
    if not info["ok"]:
        print("WARNING: refresh < 8 Hz (flicker) or acceleration above 5 g: shrink the shape or raise v within limits")

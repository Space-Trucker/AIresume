"""Bench B1 particle tracker: frames to tracks.csv for analyze_b1.py.

Input: a folder of grayscale frames (PNG or TIFF via Pillow; or .npy arrays), named so they sort in time order.
Run parameters (command line):
    --fps 60 --um_per_px 3.0 --threshold 0.25 --min_area 2 --max_jump_px 6 [--beam_on_frames 0-299,600-899]
Particles appear as bright glints (side-lit). Steps:
1. Detection: threshold at (threshold x frame max); label connected blobs; take the intensity-weighted centroid of each.
2. Linking: greedy nearest neighbour from frame to frame within max_jump_px.
3. Tracks of >= 10 frames are written as particle_id, t_s, x_m, y_m, beam_on.
x is the image column (orient the beam along the columns); y is the row, with up positive.
Frame-rate rule: keep motion below ~5 px per frame (fps >= drift / (5 x um_per_px)). For 5 mm/s at 3 um/px that means
>= 330 fps, or use lower magnification. The constant-velocity predictor tolerates steady drift but not a beam
switching on mid-track; the first frames after a switch start new tracks.

Usage:
    python3 track_b1.py frames_dir out.csv --fps 60 --um_per_px 3 --beam_on_frames 0-299
    python3 track_b1.py --selftest
"""
import argparse
import csv
import os
import sys

import numpy as np
from scipy import ndimage


def load_frames(d):
    files = sorted(f for f in os.listdir(d) if f.lower().endswith((".png", ".tif", ".tiff", ".npy")))
    for f in files:
        p = os.path.join(d, f)
        if f.endswith(".npy"):
            yield np.load(p).astype(float)
        else:
            from PIL import Image
            yield np.asarray(Image.open(p).convert("L"), float)


def detect(frame, threshold, min_area):
    mask = frame > threshold * frame.max()
    lab, n = ndimage.label(mask)
    if n == 0:
        return np.zeros((0, 2))
    idx = [i for i in range(1, n + 1) if (lab == i).sum() >= min_area]
    if not idx:
        return np.zeros((0, 2))
    return np.array(ndimage.center_of_mass(frame, lab, idx))      # (row, col)


def link(dets, max_jump):
    """Greedy linking with a constant-velocity predictor (the search radius is centred on last + last step)."""
    tracks, active, next_id = {}, {}, 0
    for k, pts in enumerate(dets):
        used, new_active = set(), {}
        for tid, (pk, last, vel) in active.items():
            if len(pts) == 0:
                continue
            pred = last + vel
            dd = np.linalg.norm(pts - pred, axis=1)
            j = int(np.argmin(dd))
            if dd[j] <= max_jump and j not in used:
                used.add(j)
                tracks[tid].append((k, pts[j]))
                new_active[tid] = (k, pts[j], pts[j] - last)
        for j, p in enumerate(pts):
            if j not in used:
                tracks[next_id] = [(k, p)]
                new_active[next_id] = (k, p, np.zeros(2))
                next_id += 1
        active = new_active
    return tracks


def parse_ranges(s, n):
    on = np.zeros(n, int)
    if not s:
        on[:] = 1
        return on
    for part in s.split(","):
        a, b = part.split("-")
        on[int(a):int(b) + 1] = 1
    return on


def run(frames_dir, out_csv, fps, um_per_px, threshold=0.25, min_area=2, max_jump_px=6.0, beam_on_frames=None):
    dets = [detect(f, threshold, min_area) for f in load_frames(frames_dir)]
    on = parse_ranges(beam_on_frames, len(dets))
    tracks = link(dets, max_jump_px)
    s = um_per_px * 1e-6
    n_written = 0
    with open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["particle_id", "t_s", "x_m", "y_m", "beam_on"])
        for tid, pts in tracks.items():
            if len(pts) < 10:
                continue
            # split a track where the beam state changes, so each segment has one state
            seg = 0
            prev = on[pts[0][0]]
            for k, (r, c) in pts:
                if on[k] != prev:
                    seg += 1
                    prev = on[k]
                w.writerow([f"{tid}_{seg}", k / fps, c * s, -r * s, int(on[k])])
            n_written += 1
    return n_written


def selftest():
    """Synthetic movie: 12 particles drifting +x at 5 mm/s while the beam is on (frames 0-59) and settling at 1 mm/s; they
    stay in frame for the beam-off reference (frames 60-239). Recover the drift."""
    import tempfile
    rng = np.random.default_rng(0)
    d = tempfile.mkdtemp()
    fps, um_px, H, W, n_frames = 400.0, 3.0, 240, 400, 240
    pos = np.column_stack([rng.uniform(40, 200, 12), rng.uniform(20, 120, 12)])          # (row, col) in px
    yy, xx = np.mgrid[0:H, 0:W]
    for k in range(n_frames):
        on = k < 60
        img = rng.normal(0.02, 0.01, (H, W))
        for p in pos:
            img += np.exp(-((yy - p[0]) ** 2 + (xx - p[1]) ** 2) / (2 * 1.2 ** 2))
        np.save(os.path.join(d, f"f{k:04d}.npy"), img)
        pos[:, 1] += (5e-3 if on else 0.0) / fps / (um_px * 1e-6)                    # +x drift in px/frame
        pos[:, 0] += 1e-3 / fps / (um_px * 1e-6)                                     # settling (rows grow downward)
    out = os.path.join(d, "tracks.csv")
    n = run(d, out, fps, um_px, beam_on_frames="0-59")
    import json
    run_json = os.path.join(d, "run.json")
    json.dump({"beam_power_W": 1.0, "beam_radius_1e2_m": 1.75e-3, "particle_radius_m": 2.5e-6, "absorptance": 0.9,
               "k_particle": 0.25, "beam_direction": 1}, open(run_json, "w"))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from analyze_b1 import analyze
    res = analyze(out, run_json)
    print(f"tracks written: {n}; recovered drift {res['drift_m_s'] * 1e3:.3f} mm/s (true 5.000)")
    assert abs(res["drift_m_s"] - 5e-3) < 0.1e-3, "self-test failed"
    print("tracker self-test OK")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("frames_dir")
        ap.add_argument("out_csv")
        ap.add_argument("--fps", type=float, required=True)
        ap.add_argument("--um_per_px", type=float, required=True)
        ap.add_argument("--threshold", type=float, default=0.25)
        ap.add_argument("--min_area", type=int, default=2)
        ap.add_argument("--max_jump_px", type=float, default=6.0)
        ap.add_argument("--beam_on_frames", default=None)
        a = ap.parse_args()
        print(run(a.frames_dir, a.out_csv, a.fps, a.um_per_px, a.threshold, a.min_area, a.max_jump_px, a.beam_on_frames),
              "tracks written")

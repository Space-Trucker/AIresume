"""End-to-end demo of the Aether reference pipeline.

content -> voxels -> safety gate (tracked hand/head, 3 ceiling apertures) -> glove haptics ->
physically scaled preview renders from several viewpoints, plus a floating video panel.

Usage:  python3 demo.py [stroke_luminance_cd_m2] [room_background_cd_m2]
Outputs PNGs and stats.json into ./out/
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import procedural_armor, procedural_armor_budget, strokes_to_points, video_panel_points  # noqa: E402
from kernel import Capsule, SafetyParams, safety_gate, glove_contacts          # noqa: E402
from render import render                                                     # noqa: E402

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)


def save_png(rgb, path):
    from PIL import Image
    Image.fromarray((rgb * 255).astype(np.uint8)).save(path)


PERCEIVED_AZURE = (0.07, 0.55, 1.0)   # E11: plasma continuum seen in a 2700 K-lit room (Bradford)


def main(L_stroke=4.0, background=0.5, spacing=2e-3, budget_m=9.0, height=1.8):
    """Budget-compliant content (E10): <= budget_m of strokes at L_stroke (film contrast in a dim lab)."""
    strokes, _ = procedural_armor_budget(budget_m, height)
    P, sid = strokes_to_points(strokes, spacing)
    P = P + np.array([0.0, 0.0, 0.1])       # stand the armor on a 10 cm plinth
    n = len(P)
    # luminous intensity per point for dotted strokes (see display_budget.point_intensity_needed)
    I_pt = L_stroke * 1e-3 * spacing           # cd  (stroke width 1 mm)
    intensity = np.full(n, I_pt)
    centre = P.mean(0)
    stroke_m = n * spacing
    stats = dict(points_per_frame=n, stroke_length_m=stroke_m, stroke_luminance=L_stroke,
                 room_background=background, point_intensity_cd=I_pt, total_lumens=4 * math.pi * I_pt * n)
    # physics budget check for this content (display_budget, engineered air + subsonic tracing)
    sys.path.insert(0, os.path.join(HERE, "..", "..", "03_simulations"))
    from display_budget import display_budget
    b = display_budget(L_stroke, stroke_m / 1e-3, room=dict(room_m3=50.0, ach=0.5, cadr_m3h=900.0, scrub_eff=0.85,
                                                           capture=0.9, decay_per_h=0.5), total_gain_db=-15.0)
    stats["budget"] = {k: b[k] for k in ("P_abs", "lumens", "ppb", "dBA_sched", "ultrasound_band_dB", "voxel_rate")}

    views = {
        "front": centre + np.array([0.0, -2.0, 0.25]),
        "three_quarter": centre + np.array([1.4, -1.4, 0.35]),
        "side": centre + np.array([2.0, 0.0, 0.2]),
        "from_above": centre + np.array([0.6, -1.2, 1.4]),
    }
    for name, eye in views.items():
        img = render(P, intensity, eye, centre, background=background, color=PERCEIVED_AZURE, warm_room=True)
        save_png(img, os.path.join(OUT, f"view_{name}.png"))

    # ---- interaction: right hand reaching into the chest, tracked head nearby
    shoulder = centre + np.array([0.35, -0.75, 0.30])
    wrist = centre + np.array([0.08, -0.22, 0.30])
    palm = centre + np.array([0.02, -0.10, 0.30])
    head = centre + np.array([0.30, -0.95, 0.60])
    capsules = [Capsule(shoulder, wrist, 0.045, "skin"), Capsule(wrist, palm, 0.04, "skin"),
                Capsule(head, head + np.array([0, 0, 0.001]), 0.11, "head")]
    apertures = [np.array([0.9, 0.0, 2.7]), np.array([-0.45, 0.78, 2.7]), np.array([-0.45, -0.78, 2.7])]
    sp = SafetyParams()
    fire, choice = safety_gate(P, apertures, capsules, sp)
    stats.update(interlock_margin_mm=sp.margin * 1e3, blanked_fraction=float(1 - fire.mean()),
                 aperture_use=[int((choice == k).sum()) for k in range(len(apertures))])
    fingertips = {"index": palm + np.array([-0.02, 0.06, 0.02]), "thumb": palm + np.array([0.03, 0.05, -0.01])}
    # move 'index' onto the nearest hologram point to show a touch event
    d = np.linalg.norm(P - fingertips["index"], axis=1)
    fingertips["index"] = P[np.argmin(d)] + np.array([0, 0, 0.004])
    stats["glove_events"] = glove_contacts(fingertips, P)   # touch is tested against the virtual geometry, not the (interlock-blanked) lit voxels
    eye = centre + np.array([-0.9, -1.8, 0.35])
    img = render(P[fire], intensity[fire], eye, centre, background=background, capsules=capsules[:2],
                 color=PERCEIVED_AZURE, warm_room=True)
    save_png(img, os.path.join(OUT, "interaction_hand_in_hologram.png"))

    # ---- floating video panel (procedural 'globe' frame), dithered to points
    h, w = 54, 96
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot(xx - w / 2, (yy - h / 2) * 1.0)
    frame = np.clip(1 - np.abs(r - 20) / 3, 0, 1) + 0.6 * ((r < 18) & ((xx // 6 + yy // 6) % 2 == 0))
    frame = np.clip(frame, 0, 1)
    pitch = 4e-3
    Pv = video_panel_points(frame, centre + np.array([0.35, 0.0, 0.2]), np.array([0.0, 1.0, 0.0]) * 0,
                            np.array([0, 0, 1.0]), pitch)
    Pv = video_panel_points(frame, centre + np.array([0.30, -0.10, 0.05]), np.array([0.5, -0.5, 0]) / math.sqrt(0.5),
                            np.array([0, 0, 1.0]), pitch)
    Pall = np.concatenate([P, Pv])
    Iall = np.concatenate([intensity, np.full(len(Pv), I_pt)])
    stats["video_panel_points"] = int(len(Pv))
    img = render(Pall, Iall, centre + np.array([-0.4, -2.1, 0.25]), centre, background=background,
                 color=PERCEIVED_AZURE, warm_room=True)
    save_png(img, os.path.join(OUT, "armor_plus_video_panel.png"))
    json.dump(stats, open(os.path.join(OUT, "stats.json"), "w"), indent=2)
    return stats


if __name__ == "__main__":
    L = float(sys.argv[1]) if len(sys.argv) > 1 else 4.0
    B = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 9.0
    height = float(sys.argv[4]) if len(sys.argv) > 4 else 1.8
    print(json.dumps(main(L, B, budget_m=budget, height=height), indent=2))

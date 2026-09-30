"""Side-by-side preview: the SAME achievable plasma hologram (budget-limited stroke luminance)
in a dim lab vs a normally lit room, and the film-level brightness for reference.

Output: out/compare_rooms.png
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import procedural_armor, strokes_to_points  # noqa: E402
from render import render                                 # noqa: E402

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

spacing = 3e-3
P, _ = strokes_to_points(procedural_armor(slice_step=0.035), spacing)
P = P + np.array([0, 0, 0.1])
c = P.mean(0)
eye = c + np.array([1.5, -1.9, 0.35])
cases = [
    ("achievable (4 cd/m2 strokes), dim lab 0.5 cd/m2", 4.0, 0.5),
    ("achievable (4 cd/m2 strokes), lit room 40 cd/m2", 4.0, 40.0),
    ("film level (200 cd/m2 = 5x bg), lit room 40 cd/m2", 200.0, 40.0),
]
tiles = []
for title, L, B in cases:
    I = np.full(len(P), L * 1e-3 * spacing)
    tiles.append(render(P, I, eye, c, W=420, H=560, background=B))
img = np.concatenate(tiles, axis=1)
from PIL import Image, ImageDraw
im = Image.fromarray((img * 255).astype(np.uint8))
d = ImageDraw.Draw(im)
for k, (title, _, _) in enumerate(cases):
    d.text((k * 420 + 8, 8), title, fill=(255, 220, 120))
im.save(os.path.join(OUT, "compare_rooms.png"))
print("saved out/compare_rooms.png")

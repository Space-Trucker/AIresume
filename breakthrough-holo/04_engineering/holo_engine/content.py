"""Content layer: turn 3D models and video into 'strokes' (polylines) sampled as plasma voxels.

The Iron Man look is thin glowing contour and edge lines over translucent volumes, which suits
a point-emitter display: we draw iso-contours (slices) and silhouettes, not filled surfaces.

Supported inputs:
  * procedural armor (for tests and demos, no external assets)
  * Wavefront OBJ meshes: feature edges (dihedral angle > threshold) plus horizontal contour slices
  * video/2D images: a floating panel rendered as an ordered-dither point field
"""
from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------- sampling helpers
def resample_polyline(xyz: np.ndarray, spacing: float) -> np.ndarray:
    seg = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    if s[-1] < 1e-9:
        return xyz[:1]
    n = max(2, int(round(s[-1] / spacing)) + 1)
    si = np.linspace(0, s[-1], n)
    return np.stack([np.interp(si, s, xyz[:, i]) for i in range(3)], axis=1)


def strokes_to_points(strokes, spacing):
    pts, ids = [], []
    for k, st in enumerate(strokes):
        p = resample_polyline(np.asarray(st, float), spacing)
        pts.append(p)
        ids.append(np.full(len(p), k))
    return np.concatenate(pts), np.concatenate(ids)


# ---------------------------------------------------------------- procedural armor
def _superellipsoid_slices(center, radii, z_levels, e=0.6, n=160):
    """Horizontal contour rings of a superellipsoid |x/a|^(2/e)+|y/b|^(2/e)+|z/c|^(2/e)=1."""
    cx, cy, cz = center
    a, b, c = radii
    out = []
    for z in z_levels:
        u = (z - cz) / c
        if abs(u) >= 1:
            continue
        k = (1 - abs(u) ** (2 / e)) ** (e / 2)
        t = np.linspace(0, 2 * np.pi, n)
        ct, st = np.cos(t), np.sin(t)
        x = a * k * np.sign(ct) * np.abs(ct) ** e
        y = b * k * np.sign(st) * np.abs(st) ** e
        out.append(np.stack([cx + x, cy + y, np.full(n, z)], 1))
    return out


def _profile(center, radii, e=0.6, n=160, plane="xz"):
    cx, cy, cz = center
    a, b, c = radii
    t = np.linspace(0, 2 * np.pi, n)
    ct, st = np.cos(t), np.sin(t)
    if plane == "xz":
        return np.stack([cx + a * np.sign(ct) * np.abs(ct) ** e, np.full(n, cy), cz + c * np.sign(st) * np.abs(st) ** e], 1)
    return np.stack([np.full(n, cx), cy + b * np.sign(ct) * np.abs(ct) ** e, cz + c * np.sign(st) * np.abs(st) ** e], 1)


def procedural_armor(height=1.8, slice_step=0.03):
    """Man-sized armor 'hologram': superellipsoid parts, contour slices and outlines."""
    s = height / 1.8
    parts = [  # (center, radii, exponent)
        ((0, 0, 1.62), (0.095, 0.11, 0.13), 0.7),      # helmet
        ((0, 0, 1.33), (0.20, 0.13, 0.17), 0.5),       # chest
        ((0, 0, 1.08), (0.15, 0.10, 0.10), 0.6),       # abdomen
        ((0, 0, 0.93), (0.17, 0.11, 0.07), 0.6),       # pelvis
        ((0.27, 0, 1.40), (0.08, 0.08, 0.07), 0.8),    # shoulders
        ((-0.27, 0, 1.40), (0.08, 0.08, 0.07), 0.8),
        ((0.30, 0, 1.18), (0.05, 0.05, 0.15), 0.8),    # upper arms
        ((-0.30, 0, 1.18), (0.05, 0.05, 0.15), 0.8),
        ((0.33, 0, 0.90), (0.045, 0.045, 0.13), 0.8),  # forearms
        ((-0.33, 0, 0.90), (0.045, 0.045, 0.13), 0.8),
        ((0.09, 0, 0.66), (0.07, 0.07, 0.22), 0.8),    # thighs
        ((-0.09, 0, 0.66), (0.07, 0.07, 0.22), 0.8),
        ((0.09, 0, 0.25), (0.055, 0.055, 0.20), 0.8),  # shins
        ((-0.09, 0, 0.25), (0.055, 0.055, 0.20), 0.8),
    ]
    strokes = []
    for c, r, e in parts:
        c = tuple(v * s for v in c)
        r = tuple(v * s for v in r)
        zl = np.arange(c[2] - r[2], c[2] + r[2], slice_step * s)
        strokes += _superellipsoid_slices(c, r, zl, e)
        strokes.append(_profile(c, r, e, plane="xz"))
        strokes.append(_profile(c, r, e, plane="yz"))
    # arc reactor: two concentric rings on the chest front
    t = np.linspace(0, 2 * np.pi, 120)
    for rr in (0.035, 0.022):
        strokes.append(np.stack([rr * s * np.cos(t), np.full_like(t, -0.132 * s), 1.34 * s + rr * s * np.sin(t)], 1))
    # eye slits
    for x0 in (0.03, -0.03):
        strokes.append(np.array([[x0 * s - 0.02 * s, -0.105 * s, 1.64 * s], [x0 * s + 0.02 * s, -0.105 * s, 1.645 * s]]))
    return strokes


# ---------------------------------------------------------------- OBJ meshes
def load_obj(path):
    V, F = [], []
    for line in open(path):
        if line.startswith("v "):
            V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            idx = [int(tok.split("/")[0]) - 1 for tok in line.split()[1:]]
            for k in range(1, len(idx) - 1):
                F.append([idx[0], idx[k], idx[k + 1]])
    return np.array(V), np.array(F)


def mesh_feature_edges(V, F, angle_deg=35.0):
    """Edges whose adjacent faces differ by more than angle_deg, plus boundary edges."""
    n = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    edges = {}
    for fi, (a, b, c) in enumerate(F):
        for u, v in ((a, b), (b, c), (c, a)):
            key = (min(u, v), max(u, v))
            edges.setdefault(key, []).append(fi)
    cos_t = math.cos(math.radians(angle_deg))
    out = []
    for (u, v), fs in edges.items():
        if len(fs) == 1 or (len(fs) == 2 and np.dot(n[fs[0]], n[fs[1]]) < cos_t):
            out.append(np.array([V[u], V[v]]))
    return out


def mesh_slices(V, F, step):
    """Horizontal contour lines of a triangle mesh (marching triangles)."""
    zmin, zmax = V[:, 2].min(), V[:, 2].max()
    segs = []
    for z in np.arange(zmin + step / 2, zmax, step):
        d = V[F, 2] - z                                   # (nF, 3)
        for k in range(len(F)):
            s = np.sign(d[k])
            if s.max() <= 0 or s.min() >= 0:
                continue
            P = []
            for i, j in ((0, 1), (1, 2), (2, 0)):
                if s[i] != s[j]:
                    t = d[k, i] / (d[k, i] - d[k, j])
                    P.append(V[F[k, i]] + t * (V[F[k, j]] - V[F[k, i]]))
            if len(P) == 2:
                segs.append(np.array(P))
    return segs


# ---------------------------------------------------------------- video panel
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def video_panel_points(frame_gray: np.ndarray, origin, u_vec, v_vec, pitch):
    """Ordered-dither a grayscale frame (0..1) onto a floating panel; returns voxel positions.

    A plasma display can only emit points, so video becomes a dither of lit points: bright
    pixels get a voxel, dark pixels don't (the voxel budget caps panel resolution).
    """
    h, w = frame_gray.shape
    th = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    on = frame_gray > th
    ys, xs = np.nonzero(on)
    origin = np.asarray(origin, float)
    return origin + np.outer(xs * pitch, u_vec) + np.outer((h - 1 - ys) * pitch, v_vec)

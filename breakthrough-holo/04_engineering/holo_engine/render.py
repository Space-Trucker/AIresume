"""Physically scaled preview renderer: what a viewer would see of the plasma voxels.

Each voxel is a point source of luminous intensity I (cd) refreshed at frame rate. For a pinhole
camera at distance r the illuminance it makes at the eye is I/r^2; we splat that into pixels and
add a room background of luminance B, then apply a simple global tone curve. Colour: hot-plasma
continuum (bluish white, CIE ~ (0.27, 0.29)), optionally tinted to show 'film cyan' for comparison.
Hands and bodies are drawn as opaque silhouettes; voxels in FRONT of a hand remain visible
(in-volume emission), which is what the touch lemma requires.
"""
from __future__ import annotations

import math

import numpy as np


def look_at(eye, target, up=(0, 0, 1)):
    eye, target, up = map(lambda v: np.asarray(v, float), (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return eye, np.stack([r, u, f])


def project(P, eye, R, f_px, W, H):
    X = (P - eye) @ R.T
    z = X[:, 2]
    ok = z > 0.05
    x = W / 2 + f_px * X[:, 0] / np.where(ok, z, 1)
    y = H / 2 - f_px * X[:, 1] / np.where(ok, z, 1)
    return x, y, z, ok


def render(P, intensity_cd, eye, target, W=640, H=720, fov_deg=58, background=0.5, capsules=(),
           color=(0.72, 0.84, 1.0), exposure=1.0, psf_px=1.1):
    """Return an RGB float image (0..1)."""
    eye, R = look_at(eye, target)
    f_px = (W / 2) / math.tan(math.radians(fov_deg / 2))
    img = np.zeros((H, W))
    x, y, z, ok = project(P, eye, R, f_px, W, H)
    # occlusion by opaque capsules (hands/body): a voxel is hidden if a capsule lies between
    vis = ok.copy()
    if len(capsules):
        from kernel import point_capsule_distance
        for cap in capsules:
            for s in np.linspace(0.05, 0.95, 20):
                X = eye[None, :] + s * (P - eye[None, :])
                vis &= point_capsule_distance(X, cap) > 0
    Ev = intensity_cd / np.maximum(z, 0.05) ** 2          # lux at the eye from each voxel
    # pixel solid angle -> convert illuminance into equivalent pixel luminance
    pix_sr = (1.0 / f_px) ** 2
    L = Ev / pix_sr                                       # cd/m^2 if spread over one pixel
    xi, yi = np.round(x).astype(int), np.round(y).astype(int)
    keep = vis & (xi >= 1) & (xi < W - 1) & (yi >= 1) & (yi < H - 1)
    np.add.at(img, (yi[keep], xi[keep]), L[keep])
    # small PSF blur (eye/optics) + bloom
    from scipy.ndimage import gaussian_filter
    img = gaussian_filter(img, psf_px) + 0.15 * gaussian_filter(img, 6 * psf_px)
    # room background: vertical gradient around B cd/m^2
    bg = background * (0.8 + 0.4 * np.linspace(1, 0, H))[:, None] * np.ones((1, W))
    # capsule silhouettes (skin, lit by room + faint plasma glow)
    sil = np.zeros((H, W), bool)
    if len(capsules):
        yy, xx = np.mgrid[0:H, 0:W]
        dirs = np.stack([(xx - W / 2) / f_px, -(yy - H / 2) / f_px, np.ones_like(xx, float)], -1)
        dirs = dirs @ R
        dirs /= np.linalg.norm(dirs, axis=-1, keepdims=True)
        from kernel import point_capsule_distance
        for cap in capsules:
            for t in np.linspace(0.2, 3.0, 60):
                Xs = eye[None, :] + t * dirs.reshape(-1, 3)
                sil |= (point_capsule_distance(Xs, cap) < 0).reshape(H, W)
    tot = bg + img
    # tone curve: compress relative to background adaptation level
    adapt = max(background, 0.5)
    v = exposure * tot / (tot + 3 * adapt)
    rgb = np.stack([v * c for c in color], -1)
    skin = np.array([0.55, 0.42, 0.36]) * (background / (background + 3 * adapt) + 0.08)
    rgb[sil] = skin + np.stack([v * c for c in color], -1)[sil] * 0.0
    # voxels in front of the hand drawn on top (in-volume emission)
    if len(capsules):
        front = np.zeros((H, W))
        np.add.at(front, (yi[keep], xi[keep]), L[keep])
        front = gaussian_filter(front, psf_px)
        fv = exposure * front / (front + 3 * adapt)
        rgb[sil] = np.clip(rgb[sil] + np.stack([fv * c for c in color], -1)[sil], 0, 1)
    return np.clip(rgb, 0, 1)

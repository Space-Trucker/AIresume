"""Safety kernel and per-frame scheduler for the Aether air-plasma projector.

Order of operations per frame (the 'last gate' logic would run on an FPGA; this is a reference model):
  1. exclusion: blank any voxel whose focus lies within the hazard margin of a tracked body part
     (eye zone around heads is much larger than the skin margin around hands)
  2. beam routing: for each remaining voxel, pick an aperture whose converging beam cone reaches
     the focus without crossing a body capsule; blank the voxel if no aperture is clear
  3. energy: per-voxel pulse energy from the brightness request (display_budget model)
  4. acoustic phase scheduling: firing times that keep tracked ears quiet (E6b)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Capsule:
    a: np.ndarray
    b: np.ndarray
    r: float
    kind: str = "skin"      # "skin" | "head"


@dataclass
class SafetyParams:
    hazard_skin_m: float = 0.010      # single-pulse skin/eye hazard zone around a focus (E7, 1550 nm, 20 uJ)
    tracking_err_m: float = 0.005
    latency_s: float = 0.005
    max_speed_m_s: float = 1.5
    head_extra_m: float = 0.15        # extra exclusion around heads (eyes): never draw near faces
    beam_na: float = 0.12             # focusing NA: beam cone half-angle ~ NA

    @property
    def margin(self):
        return self.hazard_skin_m + self.tracking_err_m + self.latency_s * self.max_speed_m_s


def point_capsule_distance(P, cap: Capsule):
    ab = cap.b - cap.a
    t = np.clip(((P - cap.a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
    return np.linalg.norm(P - (cap.a + t[:, None] * ab), axis=1) - cap.r


def segment_hits_capsule(A, P, cap: Capsule, radius_fn, n=24):
    """Does the cone from aperture A to focus P (radius radius_fn(dist_to_focus)) touch the capsule?"""
    hit = np.zeros(len(P), bool)
    for s in np.linspace(0.0, 0.98, n):
        X = A[None, :] + s * (P - A[None, :])
        dist_to_focus = (1 - s) * np.linalg.norm(P - A[None, :], axis=1)
        hit |= point_capsule_distance(X, cap) < radius_fn(dist_to_focus)
    return hit


def safety_gate(P, apertures, capsules, sp: SafetyParams):
    """Returns (fire_mask, aperture_index) for voxel focus positions P (N,3)."""
    N = len(P)
    fire = np.ones(N, bool)
    for cap in capsules:
        extra = sp.head_extra_m if cap.kind == "head" else 0.0
        fire &= point_capsule_distance(P, cap) > (sp.margin + extra)
    choice = np.full(N, -1)
    for k, A in enumerate(apertures):
        A = np.asarray(A, float)
        clear = np.ones(N, bool)
        for cap in capsules:
            clear &= ~segment_hits_capsule(A, P, cap, lambda d: sp.beam_na * d + sp.margin)
        take = fire & clear & (choice < 0)
        choice[take] = k
    fire &= choice >= 0
    return fire, choice


def glove_contacts(fingertips, P, touch_radius=0.006):
    """Haptic events: for each fingertip, whether it touches the hologram and how many voxels are near."""
    events = []
    for name, f in fingertips.items():
        d = np.linalg.norm(P - np.asarray(f)[None, :], axis=1)
        n = int((d < touch_radius).sum())
        events.append(dict(finger=name, touching=n > 0, voxels_within=n,
                           intensity=float(min(1.0, n / 6.0)), nearest_mm=float(d.min() * 1e3)))
    return events

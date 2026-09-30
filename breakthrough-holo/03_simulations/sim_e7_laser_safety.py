"""E7: Laser safety of an air-plasma projector at 'eye-safe' wavelengths.

Questions:
 (a) Around each voxel focus, how big is the zone where a single pulse exceeds the
     eye (cornea) and skin maximum permissible exposure (MPE)? That zone is what the
     tracking interlock must keep people out of.
 (b) Average irradiance on a face/eye or skin anywhere in the beam cones (MPE rule 2).
 (c) How much of an Iron-Man-style hologram must be blanked while a hand is inside it?

MPE values (R3 notes, grades B/C, i.e. to be confirmed against the purchased standards):
  1500-1800 nm, t < 1 ns : IEC-derived 1e13 W/m^2 * t  (conservative); ANSI-2022 skin 0.1 J/cm^2
  1800-2600 nm, t < 1 ns : IEC-derived 1e12 W/m^2 * t ;                  ANSI-2022 skin 0.01 J/cm^2
  long exposure (>10 s)  : 0.1 W/cm^2 (cornea and skin, >1400 nm); skin > 1000 cm^2: 10 mW/cm^2
  limiting aperture (eye, >1400 nm, t <= 0.35 s): 1 mm; long-term: 3.5 mm
"""
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from holo_common import RESULTS, save_json
from sim_e6_acoustic_scheduling import armor_wireframe


def mpe_single(lam_nm, tau, std="IEC"):
    """Single-pulse corneal/skin MPE as radiant exposure (J/m^2) for tau < 1 ns."""
    if std == "IEC":
        E_irr = 1e13 if 1500 <= lam_nm <= 1800 else 1e12
        return E_irr * tau
    return (0.1 if 1500 <= lam_nm <= 1800 else 0.01) * 1e4   # ANSI 2022 (J/cm^2 -> J/m^2)


def aperture_avg_fluence(E, w, aperture_d=1e-3):
    """Peak fluence of a Gaussian beam (1/e^2 radius w) averaged over a circular aperture."""
    a = aperture_d / 2
    # fraction of power inside radius a centred on the beam: 1 - exp(-2 a^2 / w^2)
    frac = 1 - np.exp(-2 * a * a / (w * w))
    return E * frac / (math.pi * a * a)


def hazard_length(E, lam_nm, tau, NA, std="IEC"):
    """Distance from focus (m) beyond which a single pulse is below MPE (1 mm aperture)."""
    mpe = mpe_single(lam_nm, tau, std)
    w0 = lam_nm * 1e-9 / (math.pi * NA)
    z = np.logspace(-6, 0, 4000)
    w = np.sqrt(w0 ** 2 + (NA * z) ** 2)
    F = aperture_avg_fluence(E, w)
    bad = F > mpe
    return float(z[bad].max()) if bad.any() else 0.0, mpe


def skin_hazard_length(E, lam_nm, tau, NA, std="ANSI"):
    """Skin: no aperture averaging for small beams (conservative): peak fluence 2E/(pi w^2)."""
    mpe = mpe_single(lam_nm, tau, std)
    w0 = lam_nm * 1e-9 / (math.pi * NA)
    z = np.logspace(-6, 0, 4000)
    w = np.sqrt(w0 ** 2 + (NA * z) ** 2)
    F = 2 * E / (math.pi * w * w)
    bad = F > mpe
    return float(z[bad].max()) if bad.any() else 0.0


def hand_blanking(margin, spacing=2e-3):
    """Fraction of hologram voxels blanked by an interlock radius `margin` around a hand
    reaching into the torso (hand + forearm modelled as capsules)."""
    pts = np.concatenate(armor_wireframe(spacing))
    c = pts.mean(0)
    # forearm from outside to torso centre, hand (palm+fingers) as a capsule ~ 10 cm long, r 4 cm
    segs = [(c + np.array([0.05, -0.55, 0.25]), c + np.array([0.0, -0.18, 0.25]), 0.045),   # forearm
            (c + np.array([0.0, -0.18, 0.25]), c + np.array([-0.02, -0.06, 0.25]), 0.045)]  # hand in torso
    blank = np.zeros(len(pts), bool)
    for a, b, r in segs:
        ab = b - a
        tt = np.clip(((pts - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(pts - (a + tt[:, None] * ab), axis=1)
        blank |= d < (r + margin)
    return float(blank.mean()), len(pts)


if __name__ == "__main__":
    print("E7 laser safety")
    out = {"hazard_zone": [], "average": {}, "hand_blanking": []}
    for lam in (1550, 2050):
        for tau in (0.3e-12, 3e-12):
            for E in (5e-6, 20e-6, 50e-6):
                for NA in (0.1, 0.2):
                    zi, mi = hazard_length(E, lam, tau, NA, "IEC")
                    za, ma = hazard_length(E, lam, tau, NA, "ANSI")
                    zs = skin_hazard_length(E, lam, tau, NA, "ANSI")
                    zsi = skin_hazard_length(E, lam, tau, NA, "IEC")
                    out["hazard_zone"].append(dict(lam_nm=lam, tau_ps=tau * 1e12, E_uJ=E * 1e6, NA=NA,
                                                   zone_IEC_mm=zi * 1e3, zone_ANSI_mm=za * 1e3,
                                                   skin_zone_ANSI_mm=zs * 1e3, skin_zone_IEC_mm=zsi * 1e3,
                                                   mpe_IEC=mi, mpe_ANSI=ma))
    for r in out["hazard_zone"]:
        if r["NA"] == 0.2 and r["tau_ps"] < 1:
            print(f"  {r['lam_nm']} nm {r['tau_ps']:.1f} ps {r['E_uJ']:4.0f} uJ NA{r['NA']}: single-pulse hazard zone "
                  f"eye {r['zone_IEC_mm']:.1f} mm (IEC-derived, 1 mm aperture); skin unaveraged {r['skin_zone_ANSI_mm']:.2f} mm (ANSI) / {r['skin_zone_IEC_mm']:.1f} mm (IEC-derived)")
    # (b) average exposure: transmitted beam power spread over the floor/footprint below display
    P_trans = 10.0          # W of laser power passing through the voxels (display running ~0.5-1 M voxels/s)
    for name, area_m2 in (("floor footprint 1 m^2 (beams end on floor)", 1.0),
                          ("head leaning 30 cm above voxels, intercepting 20% of beams in 200 cm^2", None)):
        if area_m2:
            irr = P_trans / (area_m2 * 1e4)
        else:
            irr = 0.2 * P_trans / 200.0
        out["average"][name] = irr
        print(f"  average irradiance, {name}: {irr*1e3:.1f} mW/cm^2 (limit 100 mW/cm^2 cornea >10 s; "
              f"10 mW/cm^2 skin >1000 cm^2)")
    # (c) interlock blanking around a hand
    for hz_mm in (2, 5, 10):
        for track_err_mm, latency_ms, speed in ((5, 5, 1.0), (10, 10, 2.0)):
            margin = (hz_mm + track_err_mm + latency_ms * speed) * 1e-3
            fr, n = hand_blanking(margin)
            out["hand_blanking"].append(dict(hazard_mm=hz_mm, track_err_mm=track_err_mm, latency_ms=latency_ms,
                                             hand_speed_m_s=speed, margin_mm=margin * 1e3, blanked_fraction=fr))
            print(f"  hand inside torso: hazard {hz_mm} mm + tracking {track_err_mm} mm + {latency_ms} ms x {speed} m/s"
                  f" -> margin {margin*1e3:.0f} mm -> {fr*100:.1f}% of {n} voxels blanked")
    save_json("e7_laser_safety.json", out)
    # plot hazard zone vs energy
    fig, ax = plt.subplots(figsize=(6.5, 4))
    Es = np.logspace(-6, -4, 30)
    for lam, ls in ((1550, "-"), (2050, "--")):
        ax.plot(Es * 1e6, [hazard_length(E, lam, 0.3e-12, 0.2, "IEC")[0] * 1e3 for E in Es], ls, label=f"{lam} nm, IEC-derived")
        ax.plot(Es * 1e6, [hazard_length(E, lam, 0.3e-12, 0.2, "ANSI")[0] * 1e3 for E in Es], ls, alpha=0.5, label=f"{lam} nm, ANSI 2022")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("pulse energy passing the focus (µJ)")
    ax.set_ylabel("single-pulse hazard zone around focus (mm)")
    ax.set_title("Eye/skin hazard is confined to millimetres around each spark")
    ax.legend(fontsize=7)
    plt.tight_layout(); plt.savefig(f"{RESULTS}/e7_hazard_zone.png", dpi=120); plt.close()
    print("  saved results/e7_laser_safety.json/.png")


# ---------------------------------------------------------------- (d) plasma UV emission
def uv_exposure(P_abs=3.0, f_rad=0.03, uv_frac=0.3, r=0.5, hours=8.0):
    """Actinic-UV check for the plasma's own emission (ICNIRP: 30 J/m^2 effective per 8 h;
    UVA eye 10 W/m^2 for >1000 s). Conservative: 30 % of radiated power in 315-400 nm, weighted
    with S(lambda) of the strongest N2 lines (S(337 nm) ~ 3.2e-4)."""
    P_uv = P_abs * f_rad * uv_frac                    # W
    E_uv = P_uv / (4 * math.pi * r * r)               # W/m^2 at a face r away
    H_eff = E_uv * 3.2e-4 * hours * 3600              # J/m^2 effective
    return dict(P_uv_W=P_uv, uva_irradiance_W_m2=E_uv, actinic_8h_J_m2=H_eff,
                uva_limit_W_m2=10.0, actinic_limit_J_m2=30.0)


if __name__ == "__main__":
    u = uv_exposure()
    print(f"  plasma UV at 0.5 m (3 W absorbed, 8 h): UVA {u['uva_irradiance_W_m2']*1e3:.1f} mW/m^2 (limit 10 W/m^2), "
          f"actinic {u['actinic_8h_J_m2']:.2f} J/m^2 eff (limit 30) -> SAFE by >100x")
    import json
    p = f"{RESULTS}/e7_laser_safety.json"
    d = json.load(open(p)); d["uv"] = u; json.dump(d, open(p, "w"), indent=2)

"""E12: Etendue (space-bandwidth) budget for addressing plasma voxels over a room-scale volume
(red-team finding 16: the AOD design is ~250x short per axis).

Resolvable spots per axis a scanner can address: N = D * dtheta / lambda (aperture x scan angle).
Spots needed across a field F at focusing NA: N_req = F / (2 w0), w0 = lambda / (pi NA).
So a scanner with N spots covering field F forces NA <= 2 N lambda / (pi F), and the breakdown
energy E_bd ~ I_th * pi w0^2 * tau (I_th ~ 5e13 W/cm^2 at 0.3 ps, E3). Tiling the volume with K
heads (field F/sqrt(K) each) buys NA. Subsonic tracing needs per-head click rate >= 35 kHz
(red-team #7), so K <= total voxel rate / 35 kHz.
"""
import math

from holo_common import save_json

lam = 1.55e-6
I_th = 5e17        # W/m^2
tau = 0.3e-12
SCANNERS = {  # (N per axis, mode)
    "TeO2 AOD, 10 us access (random access)": (500, "random"),
    "galvo 10 mm mirror, +-20 deg (vector)": (0.010 * 0.70 / lam, "vector"),
    "galvo 30 mm mirror, +-20 deg (vector)": (0.030 * 0.70 / lam, "vector"),
    "galvo 50 mm mirror, +-15 deg (vector, slow)": (0.050 * 0.52 / lam, "vector"),
}

if __name__ == "__main__":
    print("E12 etendue budget (room field 1.0 m per axis at ~1.5 m throw)")
    out = {}
    for name, (N, mode) in SCANNERS.items():
        rows = []
        for K in (1, 4, 9, 16, 25):
            F = 1.0 / math.sqrt(K)
            NA = min(0.2, 2 * N * lam / (math.pi * F))
            w0 = lam / (math.pi * NA)
            E_bd = I_th * math.pi * w0 ** 2 * tau
            zlen = 2 * math.pi * w0 ** 2 / lam
            rate_ok = 300e3 / K >= 35e3
            rows.append(dict(heads=K, field_m=F, NA=NA, w0_um=w0 * 1e6, E_breakdown_uJ=E_bd * 1e6,
                             voxel_length_mm=zlen * 1e3, click_rate_ok_at_300k=rate_ok))
            print(f"  {name:45s} K={K:2d}: field {F:.2f} m -> NA {NA:.4f}, w0 {w0*1e6:6.1f} um, "
                  f"E_bd {E_bd*1e6:8.1f} uJ, voxel length {zlen*1e3:6.2f} mm, per-head rate {'ok' if rate_ok else 'too low'}")
        out[name] = dict(N_per_axis=N, mode=mode, tiling=rows)
    save_json("e12_etendue_budget.json", out)
    print("  -> AOD random access cannot address a room at NA>0.001 (mJ-J sparks). Galvo vector heads, 30 mm, "
          "K=4-9 tiles give NA 0.03-0.05 and 40-120 uJ breakdown energy, compatible with subsonic tracing only for "
          "K<=8 at 300k voxels/s; hazard zones grow ~1/NA (E7) -> 50-100 mm interlock margins.")

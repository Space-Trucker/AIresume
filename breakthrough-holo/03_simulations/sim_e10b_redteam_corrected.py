"""E10b: Feasibility re-run with the red-team corrections adopted after independent validation
(05_reviews/red_team_1.md; NOTEBOOK Entry 7). New run justified: inputs changed.

Changes vs E10:
  * luminous efficacy band widened to 0.01-1 lm/W (eta_mult 0.07-7): no measured anchor exists (#3)
  * source capture 0.3-0.9 (uniform), not 0.9 (#9)
  * chemistry: strict 13 ppb as all-NO2; speciation multiplier 1-2.3 only (micro-sparks likely O3-rich) (#10)
  * NEW constraint: actinic UV 8-h dose at the user (0.4 m) <= 30 J/m^2, S_eff 6.9e-3 (N2 bands) to
    0.11 (hot continuum) per radiated W (E7b)
  * noise evaluated at the user's ear (0.4 m); content-dependent subsonic gain: -20 dB (long strokes)
    to -6 dB (UI glyphs), sampled; plus the air handler (45 dB(A) at 1 m, ~48 at 0.4 m) (#7, #8)
  * criteria: HOME = <=35 dB(A) and all air/UV limits; VENUE = <=55 dB(A) and all air/UV limits
"""
import math

import numpy as np

from holo_common import RESULTS, save_json
from display_budget import PARAMS, display_budget, radiated_fraction, kernel_radius

rng = np.random.default_rng(17)
ROOM = dict(room_m3=50.0, ach=0.5, cadr_m3h=900.0, scrub_eff=0.85, decay_per_h=0.5)


def sample():
    sc = {}
    for k, (nom, lo, hi) in PARAMS.items():
        sc[k] = math.exp(rng.uniform(math.log(lo), math.log(hi)))
    sc["eta_mult"] = math.exp(rng.uniform(math.log(0.07), math.log(7.0)))
    return sc


def evaluate(L, stroke_m, sc):
    cap = rng.uniform(0.3, 0.9)
    gain = -rng.uniform(6.0, 20.0)
    spec = math.exp(rng.uniform(0.0, math.log(2.3)))
    s_eff = math.exp(rng.uniform(math.log(6.9e-3), math.log(0.11)))
    b = display_budget(L, stroke_m / 1e-3, sc=sc, room=dict(ROOM, capture=cap), total_gain_db=gain,
                       r_listener=0.4)
    fan = 48.0
    dBA = 10 * math.log10(10 ** (b["dBA_sched"] / 10) + 10 ** (fan / 10))
    r0 = kernel_radius(b["E_flash"], 5e-6, sc.get("eps_k"))
    f_rad = float(radiated_fraction(r0, sc.get("f_rad_ref"), sc.get("r_ref")))
    uv = b["P_abs"] * f_rad * s_eff / (4 * math.pi * 0.4 ** 2) * 8 * 3600
    air_ok = b["ppb"] / spec <= 13.0
    uv_ok = uv <= 30.0
    return dict(air_ok=air_ok, uv_ok=uv_ok, dBA=dBA, home=air_ok and uv_ok and dBA <= 35,
                venue=air_ok and uv_ok and dBA <= 55, P_abs=b["P_abs"], uv=uv, ppb=b["ppb"] / spec)


if __name__ == "__main__":
    print("E10b red-team-corrected feasibility (1000 Monte Carlo draws per target)")
    targets = {"sparse accent (3 cd/m2, 1 m of strokes)": (3.0, 1.0),
               "Iron-Man sketch (3 cd/m2, 5 m)": (3.0, 5.0),
               "film contrast, dim lab (4 cd/m2, 9 m)": (4.0, 9.0),
               "film density, dim lab (4 cd/m2, 30 m)": (4.0, 30.0),
               "film-exact lit lab (50 cd/m2, 30 m)": (50.0, 30.0)}
    out = {}
    for name, (L, m) in targets.items():
        rows = [evaluate(L, m, sample()) for _ in range(1000)]
        f = lambda k: float(np.mean([r[k] for r in rows]))
        med = lambda k: float(np.median([r[k] for r in rows]))
        out[name] = dict(P_air_ok=f("air_ok"), P_uv_ok=f("uv_ok"), P_home=f("home"), P_venue=f("venue"),
                         median_dBA=med("dBA"), median_P_abs=med("P_abs"), median_uv=med("uv"), median_ppb=med("ppb"))
        print(f"  {name:42s} P(air ok) {out[name]['P_air_ok']:.2f}  P(UV ok) {out[name]['P_uv_ok']:.2f}  "
              f"median {out[name]['median_dBA']:.0f} dB(A) | P(HOME-safe) {out[name]['P_home']:.2f}  "
              f"P(VENUE-safe) {out[name]['P_venue']:.2f}")
    save_json("e10b_redteam_corrected.json", out)

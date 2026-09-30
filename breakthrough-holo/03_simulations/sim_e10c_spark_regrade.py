"""E10c: Feasibility re-graded with SPARK-instrument numbers instead of literature guesses.

Inputs per spark format (atlas case A_*: absorbed energy E, peak energy density eps): luminous efficacy
eta, reactive molecules per J (NO, NO2, O3 separately), actinic UV per J, from 06_spark_instrument/results/atlas.
Model-form uncertainty (red team 2; sampled log-uniformly): eta x[1/3, 3]; reactive x[1/3, 3];
actinic x[1/2, 3]; audible noise +5.4 dB (V16: simulated waveform / heat-release law = 1.86 in amplitude)
with +-2 dB. Room, capture (0.3-0.9) and subsonic-tracing gain (-6..-20 dB) as in E10b.

For a target (stroke luminance L, stroke length S) the required flux is Phi = 4 pi L w S (w = 1 mm).
A format with energy E gives N = Phi / (60 eta E) sparks per frame, i.e. dot pitch S/N; formats with pitch
> 3 mm (visibly dotted) or < 0.3 mm are rejected. Each draw picks the format that maximises the safety
margin. Criteria: air (O3 increment <= 20 ppb and total NOx+O3 as NO2 <= 13 ppb... strict) or lenient 50 ppb;
UV 8-h dose at 0.4 m <= 30 J/m^2; HOME <= 35 dB(A), VENUE <= 55 dB(A) at the user (0.4 m, incl. fan 48 dB(A)).
"""
import glob
import json
import math
import os

import numpy as np

from holo_common import RESULTS, save_json
from display_budget import breathing_zone_ppb, audible_spl_random

ATLAS = os.path.join(os.path.dirname(__file__), "..", "06_spark_instrument", "results", "atlas")
rng = np.random.default_rng(23)
ROOM = dict(room_m3=50.0, ach=0.5, cadr_m3h=900.0, scrub_eff=0.85, decay_per_h=0.5)


def load_formats():
    out = []
    for p in sorted(glob.glob(os.path.join(ATLAS, "A_*.json"))):
        d = json.load(open(p))
        E = d["E_abs"]
        c = d.get("chem", {})
        out.append(dict(label=d.get("label", os.path.basename(p)), E=E, r0=d["r0"], eta=d["eta_lm_per_W"],
                        NO=c.get("NO_total", 0) / E, NO2=c.get("NO2_total", 0) / E, O3=c.get("O3_total", 0) / E,
                        act=d["act_J"] / E, f_rad=d["f_rad"]))
    return out


def evaluate(fmt, L, S, u):
    Phi = 4 * math.pi * L * 1e-3 * S
    eta = fmt["eta"] * u["eta"]
    N = Phi / (60 * eta * fmt["E"])
    pitch = S / N
    if pitch > 3e-3 or pitch < 0.3e-3:
        return None
    P = Phi / eta
    room = dict(ROOM, capture=u["capture"])
    Yr = (fmt["NO"] + fmt["NO2"] + fmt["O3"]) * u["Y"]
    ppb_all = float(breathing_zone_ppb(P, Y=Yr, **room))
    ppb_o3 = float(breathing_zone_ppb(P, Y=fmt["O3"] * u["Y"], **room))
    uv = P * fmt["act"] * u["act"] / (4 * math.pi * 0.4 ** 2) * 8 * 3600
    dba = float(audible_spl_random(N * 60, fmt["E"], r=0.4, total_gain_db=u["sub"])) + 5.4 + u["dnoise"]
    dba = 10 * math.log10(10 ** (dba / 10) + 10 ** (48 / 10))
    return dict(P=P, pitch=pitch, ppb_all=ppb_all, ppb_o3=ppb_o3, uv=uv, dBA=dba)


def draw():
    lu = lambda a, b: math.exp(rng.uniform(math.log(a), math.log(b)))
    return dict(eta=lu(1 / 3, 3), Y=lu(1 / 3, 3), act=lu(0.5, 3), capture=rng.uniform(0.3, 0.9),
                sub=-rng.uniform(6, 20), dnoise=rng.uniform(-2, 2))


if __name__ == "__main__":
    fmts = load_formats()
    print(f"E10c SPARK-based re-grade: {len(fmts)} atlas spark formats")
    for f in fmts:
        print(f"  {f['label']:26s} r0 {f['r0']*1e6:6.1f} um  eta {f['eta']:.3f} lm/W  NO {f['NO']:.1e}  O3 {f['O3']:.1e}  act {f['act']:.1e} /J")
    targets = {"sparse accent (3 cd/m2, 1 m)": (3.0, 1.0), "Iron-Man sketch (3 cd/m2, 5 m)": (3.0, 5.0),
               "film contrast dim (4 cd/m2, 9 m)": (4.0, 9.0), "film density dim (4 cd/m2, 30 m)": (4.0, 30.0),
               "film-exact lit lab (50 cd/m2, 30 m)": (50.0, 30.0)}
    res = {}
    for name, (L, S) in targets.items():
        home = venue = venue_strict = 0
        fail = {"air (strict 13 ppb)": 0, "ozone > 20 ppb": 0, "UV 8-h dose": 0, "noise > 55 dB(A)": 0, "no valid format": 0}
        best = {}
        n = 800
        for _ in range(n):
            u = draw()
            cands = [(f, evaluate(f, L, S, u)) for f in fmts]
            cands = [(f, r) for f, r in cands if r]
            if not cands:
                fail["no valid format"] += 1
                continue
            def margin(r):
                return min(13 / max(r["ppb_all"], 1e-9), 30 / max(r["uv"], 1e-9), 10 ** ((55 - r["dBA"]) / 20))
            f, r = max(cands, key=lambda fr: margin(fr[1]))
            best[f["label"]] = best.get(f["label"], 0) + 1
            fail["air (strict 13 ppb)"] += r["ppb_all"] > 13
            fail["ozone > 20 ppb"] += r["ppb_o3"] > 20
            fail["UV 8-h dose"] += r["uv"] > 30
            fail["noise > 55 dB(A)"] += r["dBA"] > 55
            air_len = r["ppb_all"] <= 50 and r["ppb_o3"] <= 20
            air_str = r["ppb_all"] <= 13
            uv_ok = r["uv"] <= 30
            home += air_str and uv_ok and r["dBA"] <= 35
            venue += air_len and uv_ok and r["dBA"] <= 55
            venue_strict += air_str and uv_ok and r["dBA"] <= 55
        top = max(best, key=best.get) if best else None
        res[name] = dict(P_home=home / n, P_venue_lenient_air=venue / n, P_venue_strict_air=venue_strict / n,
                         most_chosen_format=top, fail_fraction={k: v / n for k, v in fail.items()})
        print(f"  {name:36s} P(home) {home/n:.2f} | P(venue, lenient air) {venue/n:.2f} | "
              f"P(venue, strict air) {venue_strict/n:.2f} | best format {top}")
        print("      fails (fraction of draws): " + ", ".join(f"{k} {v/n:.2f}" for k, v in fail.items()))
    save_json("e10c_spark_regrade.json", dict(formats=fmts, results=res))

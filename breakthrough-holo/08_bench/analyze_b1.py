"""Bench B1 analysis: photophoretic velocimetry. Measures force per absorbed watt at 1 atm and compares it with the
MOTE model (07_mote_route/mote/physics.py).

Input: a CSV of tracked particles with columns
    particle_id, t_s, x_m, y_m          (x = along the beam, y = vertical; from a calibrated camera)
plus a JSON run file:
    {"beam_power_W": 1.0, "beam_radius_1e2_m": 1.75e-3, "particle_radius_m": 2.5e-6, "particle_density": 1100,
     "absorptance": 0.9, "k_particle": 0.25, "material": "carbon-black PMMA", "beam_direction": +1}
The run should include beam-off segments (column beam_on = 0/1), so background drift (convection) can be subtracted,
and a reversed-beam run (beam_direction -1) to cancel any residual flow.

Output: the measured drift velocity along the beam, the photophoretic force (Stokes with slip), the absorbed power, the
measured F/P_abs, the model's F/P_abs, and the implied C_ph (model expects 0.67-1.04 for J1/A = 0.5; a sphere with
volume absorption gives less).

Usage: python3 analyze_b1.py tracks.csv run.json
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "07_mote_route", "mote"))
import physics as ph  # noqa: E402


def fit_velocity(rows, max_resid_m=5e-6):
    """Least-squares slope of x(t) and y(t). Rejects tracks that are not straight lines (noise / mislinks): the rms
    residual of x(t) must be <= max(max_resid_m, 10 % of the track's x span)."""
    n = len(rows)
    if n < 8:
        return None
    t = [r[0] for r in rows]
    tm = sum(t) / n
    out = []
    for k in (1, 2):
        z = [r[k] for r in rows]
        zm = sum(z) / n
        slope = sum((ti - tm) * (zi - zm) for ti, zi in zip(t, z)) / sum((ti - tm) ** 2 for ti in t)
        out.append(slope)
        if k == 1:
            res = [zi - (zm + slope * (ti - tm)) for ti, zi in zip(t, z)]
            rms = math.sqrt(sum(r * r for r in res) / n)
            span = max(z) - min(z)
            if rms > max(max_resid_m, 0.1 * span):
                return None
    return out


def analyze(tracks_csv, run_json):
    run = json.load(open(run_json))
    groups = defaultdict(lambda: {0: [], 1: []})
    with open(tracks_csv) as fh:
        for r in csv.DictReader(fh):
            on = int(r.get("beam_on", 1))
            groups[r["particle_id"]][on].append((float(r["t_s"]), float(r["x_m"]), float(r["y_m"])))
    v_on, v_off = [], []
    for g in groups.values():
        for on, lst in g.items():
            v = fit_velocity(sorted(lst))
            if v:
                (v_on if on else v_off).append(v[0] * run.get("beam_direction", 1))
    if not v_on:
        raise SystemExit("no beam-on tracks")
    med = lambda L: sorted(L)[len(L) // 2]     # medians resist the odd mislinked track
    vx = med(v_on) - (med(v_off) if v_off else 0.0)
    a, A, kp = run["particle_radius_m"], run["absorptance"], run["k_particle"]
    w = run["beam_radius_1e2_m"]
    I = 2 * run["beam_power_W"] / (math.pi * w * w) * run.get("intensity_fraction_at_particle", 1.0)
    F = 6 * math.pi * ph.mu_air(ph.T0) * a * vx / ph.cunningham(a)
    P_abs = A * math.pi * a * a * I
    model = ph.force_per_absorbed_watt(a, kp, C_ph=1.0)
    res = dict(n_tracks_on=len(v_on), n_tracks_off=len(v_off), drift_m_s=vx, intensity_W_m2=I, force_N=F,
               P_abs_W=P_abs, measured_F_per_Pabs=F / P_abs, model_F_per_Pabs_Cph1=model,
               implied_C_ph=(F / P_abs) / model)
    return res


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(json.dumps(analyze(sys.argv[1], sys.argv[2]), indent=1))
    else:
        # self-test with synthetic data generated from the model itself (C_ph = 0.9): must return implied_C_ph ~ 0.9
        import random
        import tempfile
        random.seed(1)
        run = {"beam_power_W": 1.0, "beam_radius_1e2_m": 1.75e-3, "particle_radius_m": 2.5e-6, "particle_density": 1100,
               "absorptance": 0.9, "k_particle": 0.25, "beam_direction": 1}
        I = 2 * 1.0 / (math.pi * 1.75e-3 ** 2)
        v_true = 0.9 * 0.9 * ph.photophoretic_force(2.5e-6, I, 0.25, J1=0.5) / (6 * math.pi * ph.mu_air(ph.T0) * 2.5e-6) * ph.cunningham(2.5e-6)
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "t.csv"), "w") as fh:
            fh.write("particle_id,t_s,x_m,y_m,beam_on\n")
            for p in range(20):
                for k in range(60):
                    t = k / 30
                    on = 1 if p < 14 else 0
                    x = (v_true * t if on else 0.0) + 0.0003 * t + random.gauss(0, 2e-6)
                    fh.write(f"{p},{t},{x},{-1e-3 * t},{on}\n")
        json.dump(run, open(os.path.join(d, "r.json"), "w"))
        res = analyze(os.path.join(d, "t.csv"), os.path.join(d, "r.json"))
        print(json.dumps(res, indent=1))
        assert abs(res["implied_C_ph"] - 0.9) < 0.02, "self-test failed"
        print("self-test OK (synthetic C_ph 0.9 recovered, background drift subtracted)")

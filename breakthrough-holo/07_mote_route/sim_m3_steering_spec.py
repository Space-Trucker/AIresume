"""M3: steering-engine specification for the best MOTE designs, compared with the steering technology that exists.

For each content target, take the atlas design with the fewest steering channels (results/m1_best.json). Each
channel (one beam from one head to one mote) needs:
* lateral positioning over the field: resolvable spots per axis = field / (2 w); tiles are possible, with hand-over;
* depth (focus) tracking: Rayleigh range z_R = pi w^2 / lambda; levels = depth range / (z_R/2). A first-order focus
  loop of bandwidth B lags a ramp of speed v by v/(2 pi B); keeping the lag <= z_R/2 needs B >= v / (pi z_R);
* pointing precision ~ R_ft/10 for the trap (R_ft = 1.5 w) and ~ w_p/4 for the pump; angular = precision / throw;
* intensity modulation and position sensing at the control-loop rate (M2: >= ~20 kHz).
The technology table holds representative per-device values (order of magnitude, from memory; marked in the output).
Writes results/m3_steering_spec.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mote"))
import budget as bd  # noqa: E402

THROW, FIELD, DEPTH, F_LOOP = 1.5, 1.0, 0.5, 20e3
TECH = {  # name: (resolvable spots per axis, small-step bandwidth Hz, typical unit cost USD) -- order of magnitude [MEMORY]
    "2D MEMS mirror, 2 mm, +-10 deg": (0.002 * 0.70 / 1.55e-6, 2e3, 50),
    "2D MEMS mirror, 5 mm, +-15 deg": (0.005 * 1.05 / 1.55e-6, 1e3, 300),
    "galvo pair, 10 mm, +-20 deg": (0.010 * 1.40 / 1.55e-6, 3e3, 2000),
    "galvo pair, 30 mm, +-20 deg": (0.030 * 1.40 / 1.55e-6, 5e2, 5000),
    "piezo fast-steering mirror, 10 mm, +-2 mrad": (0.010 * 0.008 / 1.55e-6, 5e3, 3000),
    "TeO2 2D AOD, 10 us access": (500, 1e5, 8000),
    "Si-photonic OPA (2025 research)": (1000, 1e6, None),
}
FOCUS_TECH = {  # (focal-power range at a 10 mm pupil in diopters, bandwidth Hz) [MEMORY]
    "electrically tunable lens": (20, 1e2),
    "MEMS varifocal mirror": (100, 5e3),
    "acousto-optic lens (AOD pair)": (500, 1e5),
    "resonant TAG lens (sweeping only)": (1000, 5e5),
}


def spec(d):
    lam_t, lam_p = 1550e-9, 405e-9
    w = d["w_trap_um"] * 1e-6
    R_ft = 1.5 * w
    zR_t = math.pi * w * w / lam_t
    w_p = bd.waist(405 if "phosphor" in d["emitter"] else (980 if "uc" in d["emitter"] else 488), THROW, d["R_head"])
    lam_pp = 405e-9 if "phosphor" in d["emitter"] else (980e-9 if "uc" in d["emitter"] else 488e-9)
    zR_p = math.pi * w_p * w_p / lam_pp
    v = d["v"]
    heads = bd.ARCH[d["arch"]]["heads"]
    # pupil-referred focus range: focus change dz at throw d through a head of radius R, relayed to a 10 mm pupil
    mag = d["R_head"] / 0.005
    diopters_head = DEPTH / THROW ** 2
    return dict(content=d["content"], arch=d["arch"], emitter=d["emitter"], N=d["N"], heads=heads,
                channels=d["channels"], v=v, w_trap_um=w * 1e6, w_pump_um=w_p * 1e6,
                spots_per_axis_full_field=FIELD / (2 * w), zR_trap_mm=zR_t * 1e3, zR_pump_um=zR_p * 1e6,
                depth_levels_trap=DEPTH / (zR_t / 2), depth_levels_pump=DEPTH / (zR_p / 2),
                focus_bw_trap_kHz=v / (math.pi * zR_t) / 1e3, focus_bw_pump_kHz=v / (math.pi * zR_p) / 1e3,
                pointing_trap_urad=R_ft / 10 / THROW * 1e6, pointing_pump_urad=w_p / 4 / THROW * 1e6,
                focus_power_at_10mm_pupil_D=diopters_head * mag ** 2, loop_kHz=F_LOOP / 1e3)


if __name__ == "__main__":
    best = json.load(open(os.path.join(HERE, "results", "m1_best.json")))
    out = dict(assumptions=dict(throw_m=THROW, field_m=FIELD, depth_m=DEPTH, loop_Hz=F_LOOP), tech=TECH,
               focus_tech=FOCUS_TECH, specs=[])
    for content, s in best.items():
        for key, d in (s.get("best_by_emitter") or {}).items():
            sp = spec(d)
            out["specs"].append(sp)
            print(f"{content:14s} {key:30s} ch={sp['channels']:.0f} spots/axis={sp['spots_per_axis_full_field']:.0f} "
                  f"zR trap {sp['zR_trap_mm']:.2f} mm, pump {sp['zR_pump_um']:.0f} um | focus BW trap "
                  f"{sp['focus_bw_trap_kHz']:.1f} kHz, pump {sp['focus_bw_pump_kHz']:.0f} kHz | pointing "
                  f"{sp['pointing_trap_urad']:.2f}/{sp['pointing_pump_urad']:.2f} urad | pupil focus range "
                  f"{sp['focus_power_at_10mm_pupil_D']:.0f} D")
    print("\nTechnology (per device, order of magnitude, from memory):")
    for k, (n, bw, cost) in TECH.items():
        print(f"  {k:45s} {n:8.0f} spots/axis, {bw:8.0f} Hz, ~${cost}")
    with open(os.path.join(HERE, "results", "m3_steering_spec.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)

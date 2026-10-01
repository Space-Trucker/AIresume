"""M18d: how much does a hand stir the air at the image? Air speeds near a moving or warm hand, compared with B9 and the
gust authority of a still-room design (U + 5.4 sigma = 0.16 m/s).

1. A moving hand or finger (potential flow past a sphere of radius R, speed V): the disturbance at distance r from
   the centre (r > R) is at most |u| = V (R/r)^3 (on the axis; half of that abeam). Motes are lost where |u| exceeds
   the authority u_auth: r_lost = R (V/u_auth)^(1/3). The wake behind a bluff body (Re = 2RV/nu ~ 10^3) is
   turbulent and holds ~V/2 over a few R downstream [ESTIMATE].
2. A warm, still hand (33 C skin in 21 C air) drives natural convection. Two estimates bracket the speed above it:
   - lower: the laminar boundary layer of a vertical plate of length x, u_max ~ 0.56 sqrt(g beta dT x) (Ostrach
     similarity, Pr 0.71; Gr ~ 1e6, so laminar) [DERIVED, constant from memory];
   - upper: a point-source plume of convective power Q = h A dT, centreline w(z) = 4.7 (g beta Q/(rho c_p))^(1/3)
     z^(-1/3) (Morton-Taylor-Turner) [DERIVED, constant from memory]; it overestimates close to an extended source.
3. A glove that holds its outer surface near room temperature (dT 1-2 K) cuts Q by ~10x and w by ~10^(1/3) = 2.2x.

Run: python3 m18d_touch_air.py -> results/m18d_touch_air.json
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
U_AUTH = 0.16            # still-room design authority (U + 5.4 sigma, sigma 0.03), m/s
V_MEAN_B9 = 0.049        # B9 mean-speed cap at w = 50 um, static voxels, m/s


def lost_radius(R, V, u_auth=U_AUTH):
    return R * (V / u_auth) ** (1 / 3)


def plume_speed(Q, z, T=294.0):
    g, beta, rho, cp = 9.81, 1 / T, 1.2, 1005.0
    B = g * beta * Q / (rho * cp)
    return 4.7 * B ** (1 / 3) * z ** (-1 / 3)


def main():
    out = dict(moving=[], plume=[])
    print("Moving hand/finger: radius around it (and its turbulent wake, ~V/2 over a few R) where motes are lost "
          f"(authority {U_AUTH} m/s)")
    for name, R in (("finger", 0.008), ("hand", 0.045)):
        for V in (0.05, 0.1, 0.3, 1.0):
            r = lost_radius(R, V) if V > U_AUTH else R
            out["moving"].append(dict(part=name, R=R, V=V, r_lost=r, Re=2 * R * V / 1.5e-5))
            print(f"  {name:6s} V {V:4.2f} m/s: lost within r = {r * 100:4.1f} cm of its centre"
                  f"{' (only contact; V below authority)' if V <= U_AUTH else ''}; Re {2 * R * V / 1.5e-5:5.0f}")
    print("\nNatural convection above a still hand (plate x = 8 cm; plume Q = h A dT, h 4 W/m^2K, A 0.04 m^2):")
    for name, dT in (("bare hand (33 C skin)", 12.0), ("insulated glove (dT 1.5 K)", 1.5)):
        Q = 4.0 * 0.04 * dT
        u_plate = 0.56 * math.sqrt(9.81 / 294.0 * dT * 0.08)
        for z in (0.02, 0.05, 0.10, 0.20):
            w = plume_speed(Q, z + 0.03)            # virtual origin ~3 cm below the hand's top surface [ESTIMATE]
            out["plume"].append(dict(case=name, Q=Q, z=z, w_plume_upper=w, u_plate_lower=u_plate))
            print(f"  {name:28s} {z * 100:4.0f} cm above: {u_plate:5.3f}-{w:5.3f} m/s  "
                  f"({u_plate / V_MEAN_B9:3.1f}-{w / V_MEAN_B9:3.1f}x the B9 mean budget at w = 50 um)")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "m18d_touch_air.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()

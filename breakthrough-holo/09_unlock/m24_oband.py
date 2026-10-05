"""M24: the O-band window. Moving the IR holding light from 1550 nm to 1300-1350 nm.

Why, under IEC 60825-1:2014 (Ed. 3) and ICNIRP 2013:
- **Skin** [MEASURED rule, ICNIRP 2013 Tab. 7, as R7]: the long-exposure MPE (t > 10 s) is 2000 C_A W/m² at
  400-1400 nm, with C_A = 5 at 1050-1400 nm, i.e. 10 kW/m². At 1400 nm-1 mm it is 1000 W/m². EN 50689 assesses skin
  through 1 mm over 10 s (RT9-verified), so the per-focus skin cap rises ×10, from 0.785 mW to 7.85 mW.
- **Eye, retina** [MEASURED rule]: the Class 1 AEL at 1050-1400 nm (t >= T2 = 10 s) is 3.5e-3 C7 T2^-0.25 W
  (R7: 1.97 mW at 1064 nm). Edition 3 sets C7 = 8 + 10^(0.04 (lambda - 1250)) for 1250-1400 nm: 259 at 1310 nm, which
  is 32x the old value (Seibersdorf white paper).
- **Eye, cornea** [MEASURED rule]: at 1250-1400 nm Ed. 3 adds the Class 3B AEL (0.5 W CW) as a dual limit to protect
  the cornea (Seibersdorf; ILSC 2019).
- So the Class 1 eye AEL at 1310 nm is min(0.51 W, 0.5 W) ~ 0.5 W, against 10 mW at 1550 nm.

This model recomputes, at 1550 nm and at 1290/1310/1342 nm:
- the binding per-focus cap (skin per focus vs eye / (h s));
- the tetralemma rows of m22 §H (w_max, true modes, loop rate);
- RT8 C1, POV pupil stacking at 2.7-9.1x the 1550 nm AEL;
- RT9 C2, the 0.2 W probe fan: 104 mW in a pupil at 10 cm and 74 mW through 1 mm at the exit.

Run: python3 m24_oband.py -> results/m24_run.log
"""
import math

I_UNIT = 1.5e7
X = 0.6


def c7(lam_nm):
    if lam_nm < 1150:
        return 1.0
    if lam_nm < 1200:
        return 10 ** (0.018 * (lam_nm - 1150))
    if lam_nm < 1250:
        return 8.0
    if lam_nm <= 1400:
        return 8.0 + 10 ** (0.04 * (lam_nm - 1250))
    return float("nan")


def class1_eye(lam_nm):
    """Long-exposure Class 1 AEL (W), small source."""
    if lam_nm > 1400:
        return 10e-3                                    # 1400-4000 nm (as used throughout the project)
    retina = 3.5e-3 * c7(lam_nm) * 10 ** -0.25          # 1050-1400 nm, T2 = 10 s
    if lam_nm >= 1250:
        return min(retina, 0.5)                         # Class 3B dual limit (cornea)
    return retina


def skin_cap(lam_nm):
    """EN 50689: skin MPE (t >= 10 s) through 1 mm (W)."""
    E = 1000.0 if lam_nm > 1400 else 2000.0 * 5.0     # C_A = 5 at 1050-1400 nm
    return E * math.pi * 0.5e-3 ** 2


def main():
    print("Per-focus caps (W):")
    rows = []
    for lam in (1550, 1342, 1310, 1290, 1270):
        eye = class1_eye(lam)
        skin = skin_cap(lam)
        cap_eye_static = eye / 7.1           # m18 static h*s (pupil at a focus with neighbours)
        cap_skin = skin / (2.14 * 1.1)       # skin h*s (m22 H)
        cap = min(cap_eye_static, cap_skin)
        which = "skin" if cap_skin <= cap_eye_static else "eye"
        rows.append((lam, eye, skin, cap, which))
        print(f"  {lam} nm: C7 {c7(lam) if lam <= 1400 else float('nan'):8.1f}  eye Class 1 {eye * 1e3:7.1f} mW  "
              f"skin 1 mm {skin * 1e3:6.3f} mW  -> per-focus mean cap {cap * 1e3:6.3f} mW (binding: {which})")
    print("\nTetralemma at the binding cap (w_max = sqrt(2 cap/(pi I_unit v)) with cap already divided by h s):")
    for lam, eye, skin, cap, which in rows:
        if lam not in (1550, 1310):
            continue
        for v in (0.01, 0.03, 0.1, 0.2):
            w = math.sqrt(2 * cap / (math.pi * I_UNIT * v))
            modes = (X / (math.pi * w)) ** 2
            print(f"  {lam} nm v {v * 100:4.0f} cm/s: w_max {w * 1e6:6.1f} um  true modes {modes:.2e}  "
                  f"(m18 count x13: {modes * 12.96:.2e})  loop >= {10 * v / w:7.0f} Hz")
    print("\nRT8 C1 (POV pupil stacking 2.7-9.1x the 10 mW AEL at 1550 nm), same beams at 1310 nm:")
    print(f"  27-91 mW against {class1_eye(1310) * 1e3:.0f} mW -> {27 / (class1_eye(1310) * 1e3):.2f}-"
          f"{91 / (class1_eye(1310) * 1e3):.2f}x the AEL (eye); skin per focus x10 headroom")
    print("\nRT9 C2 (FLOW-R2 probe fan, 0.2 W) moved from 850 nm to 1310 nm:")
    print(f"  pupil at 10 cm: 104 mW against {class1_eye(1310) * 1e3:.0f} mW -> {104 / (class1_eye(1310) * 1e3):.2f}x; "
          f"skin at the exit through 1 mm: 74 mW against {skin_cap(1310) * 1e3:.2f} mW -> "
          f"{74 / (skin_cap(1310) * 1e3):.1f}x (850 nm: 24x)")


if __name__ == "__main__":
    main()

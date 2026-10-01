"""Self-check of the DIY-2 galvo command stage in ELECTRONICS.md (inverting op-amp with offset, MCP4922 at VREF 2.5 V).
Recomputes the transfer function, the offset divider, the reconstruction-filter corner and the position step.
Run: python3 electronics_check.py   (exits non-zero if a design number is off)
"""
import math
import sys

VREF = 2.5


def stage(code, rin, rf, r_top, r_bot, vref=VREF):
    vdac = vref * code / 4096.0
    vm = vref * r_bot / (r_top + r_bot)
    return vm * (1 + rf / rin) - (rf / rin) * vdac


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"  {'PASS' if ok else 'FAIL'} {name}: {got:+.4f} (want {want:+.4f} +- {tol})")
    return ok


def main():
    ok = True
    print("+-5 V stage: Rin 10k, Rf 40.2k, divider 15k/10k")
    for code, want in ((0, 5.02), (2048, 0.0), (4095, -5.03)):
        ok &= check(f"code {code}", stage(code, 10e3, 40.2e3, 15e3, 10e3), want, 0.02)
    print("+-10 V stage: Rin 10k, Rf 80.6k, divider 12.7k/10.2k")
    for code, want in ((0, 10.0), (2048, 0.0), (4095, -10.0)):
        ok &= check(f"code {code}", stage(code, 10e3, 80.6e3, 12.7e3, 10.2e3), want, 0.1)
    G = 4.02
    ok &= check("Vm rule 1.25 G/(1+G), G=4.02", 1.25 * G / (1 + G), 2.5 * 10 / 25, 0.002)
    fc = 1 / (2 * math.pi * 40.2e3 * 470e-12)
    ok &= check("filter corner kHz (Rf 40.2k, Cf 470p)", fc / 1e3, 8.4, 0.1)
    # reference current budget: LM4040-2.5 via 1k from 3.3 V; loads = divider (25k) + two unbuffered VREF inputs (~165k each)
    i_feed = (3.3 - 2.5) / 1e3
    i_load = 2.5 / 25e3 + 2 * 2.5 / 165e3
    ok &= check("LM4040 spare current mA (needs > 0.06)", (i_feed - i_load) * 1e3, 0.67, 0.05)
    # position step: +-10 deg mechanical = +-20 deg optical behind f = 100 mm for the +-5 V full swing
    span = 2 * 0.100 * math.tan(math.radians(20))
    step_um = span / 4096 * 1e6
    ok &= check("step um at full scale (f=100 mm, +-10 deg mech)", step_um, 17.8, 0.5)
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

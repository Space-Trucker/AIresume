# Round 10 fresh checks (main session) of idea round 5 numbers: wet-bulb drop lifetime, water load and RH rise.
import math
def psat(Tc):  # Pa, Magnus
    return 610.94*math.exp(17.625*Tc/(Tc+243.04))
def rho_v(Tc, RH):
    return RH*psat(Tc)/(461.5*(Tc+273.15))
def wet_bulb(T, RH, P=101325.0):
    """Psychrometric wet bulb by bisection: cp (T - Tw) = L (w_s(Tw) - w)."""
    w = 0.622 * RH * psat(T) / (P - RH * psat(T))
    f = lambda Tw: 1006 * (T - Tw) - 2.45e6 * (0.622 * psat(Tw) / (P - psat(Tw)) - w)
    lo, hi = -20.0, T
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(mid) > 0:          # f decreases with Tw: root lies above mid
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
d0=(6*30e-15/math.pi)**(1/3); Dv=2.45e-5
for RH in (0.3,0.5,0.7):
    Tw=wet_bulb(20.0,RH); drho=rho_v(Tw,1.0)-rho_v(20.0,RH)
    t=1000*d0**2/(8*Dv*drho)
    print(f"RH {RH:.0%}: wet bulb {Tw:5.1f} C, drho {drho*1e3:.2f} g/m3, lifetime {t:.2f} s (ambient-temperature formula {1000*d0**2/(8*Dv*(rho_v(20,1)-rho_v(20,RH))):.2f} s)")
flux=1.6e5; m=30e-15*1000
print(f"water load {flux*m*3600*1e3:.1f} g/h; RH rise in 50 m3 at 0.5 ACH: {flux*m*3600/(0.5*50)/rho_v(20,1.0)*100:.1f} %")

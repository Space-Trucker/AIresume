import math, statistics
ND = statistics.NormalDist(); G = 0.5772156649015329
def f(n): return 0.0 if n <= 1 else (1-G)*ND.inv_cdf(1-1/n) + G*ND.inv_cdf(1-1/(n*math.e))
z95 = ND.inv_cdf(0.95)
print("Global-null false-pass probability when N_counted is used in the DSR but N_actual independent trials were really run (V = null, normal):")
for nc in (10, 20, 30, 50):
    zs = f(nc) + z95
    row = []
    for na in (10, 20, 30, 50, 100, 200):
        row.append(f"Nact={na}: {1-ND.cdf(zs)**na:.4f}")
    print(f"  Ncounted={nc:3d} (z*={zs:.3f}): " + "  ".join(row))
# SE of half-sample SR and P(half < 0.25)
q=252
for sr in (1.0, 1.5):
    s = sr/math.sqrt(q); se = math.sqrt(q)*math.sqrt((1+0.5*s*s)/(1199))
    p = ND.cdf((0.25-sr)/se)
    print(f"true SR {sr}: s.e.(half, 1200d)={se:.3f}  P(one half <0.25)={p:.4f}  P(either half <0.25)~{1-(1-p)**2:.4f}")
s = 1.5/math.sqrt(q); se=math.sqrt(q)*math.sqrt((1+0.5*s*s)/188)
print(f"189-day forward window: s.e.={se:.3f}  P(obs SR<0 | true 1.5)={ND.cdf(-1.5/se):.3f}")
import datetime
d0=datetime.date(2016,1,4); d1=datetime.date(2026,10,15)
yrs=(d1-d0).days/365.25
print(f"2016-01-04 to 2026-10-15: {yrs:.2f} years ~ {yrs*252:.0f} trading days")

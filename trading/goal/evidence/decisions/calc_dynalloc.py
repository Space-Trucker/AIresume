import math
from statistics import NormalDist
# --- Little's law and risk budget
rt_per_week=25; days=5; hold_days=3.0
lam=rt_per_week/days; L=lam*hold_days
print(f"Little: lambda={lam}/day, W={hold_days}d -> avg concurrent L={L}")
print(f"avg risk per position if open risk cap 2.0% fully used: {2.0/L:.3f}%")
for r in (0.5,0.25,0.2,0.15,0.133,0.1):
    print(f"risk/pos {r}%: total N<= {math.floor(2.0/r+1e-9)}, per side N<= {math.floor(1.5/r+1e-9)}; throughput at 3d hold = {math.floor(2.0/r+1e-9)/3*5:.1f} RT/week")
# notional vs stop distance at 4% overnight cap
for d in (2.0,2.5,3,4,5,6,8,12.5):
    print(f"stop dist {d}% at 4% notional -> risk {4*d/100:.3f}% of equity; N within 2% open risk = {math.floor(2.0/(4*d/100)+1e-9)}; gross used = {4*math.floor(2.0/(4*d/100)+1e-9)}%")
# costs
rt_bps=8; notional=4.0
cost_rt_pct_eq = notional*rt_bps/10000*100/100  # % of equity
cost_rt = notional/100*rt_bps/10000  # fraction of equity
print(f"cost per RT at 4% notional: {cost_rt*100:.4f}% of equity (${cost_rt*100000:.2f} on $100k)")
annual = cost_rt*rt_per_week*52*100
print(f"annual cost at 25 RT/week: {annual:.2f}% of equity; budget 4.5% -> headroom {4.5-annual:.2f}%/yr = {(4.5-annual)/(cost_rt*52*100):.2f} extra RT/week")
print(f"stressed x1.5: annual {annual*1.5:.2f}%")
# cost in R units: RT cost / risk = rt_bps/ stop distance
for d in (2.5,4,6):
    print(f"stop {d}%: RT cost = {rt_bps/100/d:.3f} R (stressed {1.5*rt_bps/100/d:.3f} R); entry hurdle 2x cost = {2*rt_bps/100/d:.3f} R")
# alpha decay: fraction of initial expected gain (0..T) remaining at age t, exponential decay with half-life h
def rem(t,T,h):
    phi=math.log(2)/h
    return (math.exp(-phi*t)-math.exp(-phi*T))/(1-math.exp(-phi*T))
print("remaining fraction of the trade's total expected gain, horizon T=3d")
for h in (0.5,1,2,3,6):
    print(" h=%.1fd: "%h + ", ".join(f"t={t}d:{rem(t,3,h):.2f}" for t in (0.25,0.5,1,1.5,2,2.5)))
# winner's curse: expected max of N iid standard normals
nd=NormalDist()
def emax(N, steps=20000):
    # E[max] = int x * N * phi(x) * Phi(x)^(N-1) dx
    lo,hi=-8,8; dx=(hi-lo)/steps; s=0.0
    for i in range(steps):
        x=lo+(i+0.5)*dx
        s+=x*N*nd.pdf(x)*nd.cdf(x)**(N-1)*dx
    return s
for N in (2,5,10,20,50,100,500,1000,2000):
    print(f"E[max of {N} N(0,1)] = {emax(N):.2f}")
# shrinkage: if forecast = signal with noise, posterior shrink factor = var_true/(var_true+var_noise)
for ic in (0.02,0.05,0.1):
    print(f"IC={ic}: Grinold alpha = IC*vol*z -> with vol 2%/day, z=2: {ic*2*2:.3f}%/day")

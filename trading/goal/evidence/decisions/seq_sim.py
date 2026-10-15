import math, random, sys
sys.path.insert(0, "/home/user/AIresume/trading/goal")
from goaltests import gates, sim
def run(rule, sr, model="normal", reps=600, years=3, seed=1):
    rng = random.Random(f"seq-{sr}-{model}-{seed}")
    sigma = 0.002
    mu = sr / math.sqrt(252) * sigma
    stop1 = stop3 = halve1 = 0; tstops = []
    for _ in range(reps):
        x = sim.returns(252 * years, mu, sigma, model, rng)
        acts = gates.sequential(rule, x)
        st = [d for d, a in acts if a == "stop"]
        if st:
            tstops.append(st[0])
            stop3 += 1
            stop1 += st[0] <= 252
        halve1 += any(a in ("halve", "stop") and d <= 252 for d, a in acts)
    med = sorted(tstops)[len(tstops)//2] if tstops else None
    return stop1/reps, stop3/reps, halve1/reps, med
for h1, stop, halve in [(1.5, math.log(0.1/0.95), math.log(1/3)), (1.5, math.log(0.05), math.log(1/3)), (1.0, math.log(0.1/0.95), math.log(1/3))]:
    rule = {"h1_sr": h1, "cap": math.log(18), "stop_at": stop, "halve_at": halve, "look_every_days": 21, "burn_in_days": 21}
    print(f"H1 {h1} stop {stop:.2f} halve {halve:.2f}")
    for sr in (0.0, 0.5, 1.0, 1.5):
        s1, s3, h, med = run(rule, sr)
        print(f"  true SR {sr}: stopped within 1y {s1:.0%}, 3y {s3:.0%}; halved within 1y {h:.0%}; median days to stop {med}")

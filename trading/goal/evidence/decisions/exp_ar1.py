import math, random, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/user/AIresume/trading/goal")
from goaltests import gates, sim, stats
from goaltests.spec import load, rule
from goaltests.gt04_power import _setup, _sigma, _g1_record

def g1_power(args):
    days, half, model = args
    spec = load("/home/user/AIresume/trading/goal/goal.toml")
    s = _setup(spec); s["oos_days"] = days
    g1 = dict(rule(spec, "G1")); g1["min_days"] = days; g1["min_sr_each_half"] = half
    rng = random.Random(f"exp-{days}-{half}-{model}")
    sigma = _sigma(s, model); mu1 = stats.daily_sr(1.5) * sigma
    reps = 600; found = 0
    for _ in range(reps):
        rec, chosen = _g1_record(s, [mu1] + [0.0] * 9, sigma, model, rng)
        if chosen == 0 and gates.evaluate(g1, rec)[0]:
            found += 1
    return (days, half, model, found / reps)

if __name__ == "__main__":
    jobs = [(d, h, m) for d in (2250, 2400) for h in (0.5, 0.25, 0.0) for m in ("ar1", "normal")]
    with ProcessPoolExecutor(4) as pool:
        for d, h, m, p in pool.map(g1_power, jobs):
            print(f"days {d} half {h} {m}: G1 power {p:.1%}", flush=True)

import math, random, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/user/AIresume/trading/goal")
from goaltests import gates, sim, stats

def job(args):
    block, stop, halve, model = args
    rule = {"h1_sr": 1.5, "cap": math.log(18), "stop_at": stop, "halve_at": halve, "look_every_days": 21, "block_days": block, "burn_in_days": 21}
    rng = random.Random(f"live-{block}-{stop}-{model}")
    sigma = 0.002
    if model == "ar1":
        sigma = sigma / math.sqrt(sim.five_day_factor("ar1"))
    reps = 600
    fs = sum(any(a == "stop" for _, a in gates.sequential(rule, sim.returns(756, stats.daily_sr(1.5) * sigma, sigma, model, rng))) for _ in range(reps))
    ds = dh = 0
    for _ in range(reps):
        acts = gates.sequential(rule, sim.returns(756, 0.0, sigma, model, rng))
        ds += any(a == "stop" for _, a in acts)
        dh += any(a in ("halve", "stop") and d <= 252 for d, a in acts)
    return args, fs / reps, dh / reps, ds / reps

if __name__ == "__main__":
    jobs = [(1, st, -1.1, m) for st in (-2.5, -2.75) for m in ("normal", "garch", "ar1", "t4")]
    with ProcessPoolExecutor(4) as pool:
        for args, fs, dh, ds in pool.map(job, jobs):
            print(f"block {args[0]} stop {args[1]} {args[3]}: false stop 3y {fs:.1%}; dead halved 1y {dh:.0%}, stopped 3y {ds:.0%}", flush=True)

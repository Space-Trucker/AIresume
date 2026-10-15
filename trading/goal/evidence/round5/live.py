"""Live test options: false stops of the target, dead detection, decay detection (zero net, and costs remaining)."""
import sys, random, math
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/user/AIresume/trading/goal")
from goaltests import gates, sim, stats

SIG = 0.002
DRAG_SR = -(25 * 52 * 0.04 * 8e-4) / (0.002 * math.sqrt(252))   # costs remaining once the gross edge is gone

def run(args):
    stop, cap, model, reps = args
    rule = {"h1_sr": 1.5, "cap": cap, "stop_at": stop, "halve_at": -1.1, "grow_at": 1.1, "look_every_days": 21}
    rng = random.Random(f"live-{model}-{stop}-{cap}")
    mu = lambda sr: stats.daily_sr(sr) * SIG
    fs = dh = ds = 0
    dec = {"zero": [0, 0, 0], "costs": [0, 0, 0]}
    for _ in range(reps):
        acts = gates.sequential(rule, sim.returns(756, mu(1.5), SIG, model, rng))
        fs += any(a == "stop" for _, a in acts)
        acts = gates.sequential(rule, sim.returns(756, mu(0.0), SIG, model, rng))
        ds += any(a == "stop" for _, a in acts)
        dh += any(a in ("halve", "stop") and d <= 252 for d, a in acts)
        for kind, sr_after in (("zero", 0.0), ("costs", DRAG_SR)):
            x = sim.returns(504, mu(1.5), SIG, model, rng) + sim.returns(756, mu(sr_after), SIG, model, rng)
            acts = gates.sequential(rule, x)
            if any(a == "stop" and d <= 504 for d, a in acts):
                continue
            dec[kind][0] += 1
            dec[kind][1] += any(a in ("halve", "stop") and 504 < d <= 756 for d, a in acts)
            dec[kind][2] += any(a == "stop" and 504 < d <= 1260 for d, a in acts)
    return (stop, cap, model, fs / reps, dh / reps, ds / reps,
            dec["zero"][1] / dec["zero"][0], dec["zero"][2] / dec["zero"][0],
            dec["costs"][1] / dec["costs"][0], dec["costs"][2] / dec["costs"][0])

if __name__ == "__main__":
    jobs = [(s, c, m, 1500) for s in (-2.5, -2.3, -2.2, -2.0) for c in (2.89, 1e9) for m in sim.NOISE_MODELS]
    with ProcessPoolExecutor(4) as pool:
        for r in pool.map(run, jobs):
            print(f"stop {r[0]:5} cap {r[1]:>6g} {r[2]:6}: false stop {r[3]:5.1%} | dead halve1 {r[4]:5.1%} stop3 {r[5]:5.1%} | "
                  f"decay0 halve1 {r[6]:5.1%} stop3 {r[7]:5.1%} | decay-costs halve1 {r[8]:5.1%} stop3 {r[9]:5.1%}", flush=True)

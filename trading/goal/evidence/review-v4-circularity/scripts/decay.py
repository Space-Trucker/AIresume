"""The scenario GT-4 never simulates: a strategy with the targeted edge that loses it after two years.
Same live-test code (goaltests.gates.sequential) and same noise generator (goaltests.sim) as GT-4.
Reports how often, and how fast, the live test stops it after the decay, for the goal's cap (ln 18)
and for an uncapped test (mutant M37)."""
import math
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/frozen")
from goaltests import gates, sim, stats  # noqa: E402
from goaltests.spec import load  # noqa: E402

spec = load("/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/frozen/goal.toml")
live = spec["live"]
base = {"h1_sr": live["test_h1_sr"], "cap": live["test_cap_llr"], "stop_at": live["test_stop_llr"],
        "halve_at": live["test_halve_llr"], "grow_at": live.get("test_grow_llr", 0.0),
        "look_every_days": live.get("retire_check_every_trading_days", 21)}
sigma = spec["risk"]["vol_target_daily_pct"] / 100
good_years, dead_years, reps = 2, 3, 2000
for label, cap in (("goal cap 2.89", base["cap"]), ("no cap (M37)", 1000.0)):
    rule = dict(base, cap=cap)
    rng = random.Random("decay")
    stop_in, halves, fresh_halve, fresh_stop = [], [], [], []
    for _ in range(reps):
        r = (sim.returns(252 * good_years, stats.daily_sr(1.5) * sigma, sigma, "normal", rng)
             + sim.returns(252 * dead_years, 0.0, sigma, "normal", rng))
        acts = gates.sequential(rule, r)
        stops = [d for d, a in acts if a == "stop"]
        early = stops and stops[0] <= 252 * good_years
        stop_in.append(None if early else (stops[0] - 252 * good_years if stops else math.inf))
        if not early:
            halves.append(any(a in ("halve", "stop") and 252 * good_years < d <= 252 * (good_years + 1) for d, a in acts))
            dead0 = gates.sequential(rule, sim.returns(252 * 3, 0.0, sigma, "normal", rng))
            fresh_halve.append(any(a in ("halve", "stop") and d <= 252 for d, a in dead0))
            fresh_stop.append(any(a == "stop" for d, a in dead0))
    after = [s for s in stop_in if s is not None]
    within = lambda y: sum(1 for s in after if s <= 252 * y) / len(after)  # noqa: E731
    print(f"{label}: stopped within 1/2/3 years of the decay: {within(1):.0%} / {within(2):.0%} / {within(3):.0%} "
          f"(of {len(after)} runs not stopped while the edge was real); halved within 1 year of the decay: "
          f"{sum(halves) / len(halves):.0%}; for comparison, dead from day one (GT-4's case): halved in year 1 "
          f"{sum(fresh_halve) / len(fresh_halve):.0%}, stopped within 3 years {sum(fresh_stop) / len(fresh_stop):.0%}")

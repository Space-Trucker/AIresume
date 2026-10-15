import sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, "/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/frozen")
from goaltests import data, stats, gt02_consistency as g2, gt03_costs as g3

# 1. largest overnight gaps in the five stocks, 1999 on
for name in ("goog", "msft", "orcl", "nvda", "yhoo"):
    b = [r for r in data.bars(name) if r["date"].year >= 1999]
    gaps = sorted(((b[i]["open"] / b[i - 1]["close"] - 1), b[i]["date"].strftime("%Y-%m-%d")) for i in range(1, len(b)))
    print(name, len(b), "worst down:", [(f"{g:+.1%}", d) for g, d in gaps[:4]], "biggest up:", [(f"{g:+.1%}", d) for g, d in gaps[-4:]])
q = g2.overnight_gaps()
print("q99 after dropping top 2%:", {k: round(v["q99"], 4) for k, v in q.items()})
# 2. Erlang
for load, servers in ((15, 18), (15, 15), (15, 20), (15, 16), (15, 17)):
    print("erlang_b", load, servers, round(g2.erlang_b(load, servers), 4))
# 3. residual vol and book vol
rv = g2.residual_vol()
print("residual vol", rv, "book vol at 15 x 4%", 0.04 * rv * math.sqrt(15) * 100)
# 4. GT-3 numbers
vol = g3.daily_vol()
stock_d = (vol["goog"] + vol["msft"]) / 2 * 1e4
print("daily vols", vol, "stock_d bps", stock_d)
print("external round trip", g3.external_round_trip_bps())
lo, hi = (y * stock_d * math.sqrt(0.02 / 100) for y in (0.5, 1.0))
print("impact lo/hi at 0.02% ADV", lo, hi, "vs 1.5*1.5 =", 2.25)
for m in (150, 556, 600, 780):
    move = stock_d * math.sqrt(m / 390)
    print("IC entry at", m, "min:", 16 / (g3.SIGN_BET_EFFICIENCY * move))

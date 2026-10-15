"""Forward-test length needed to confirm a net Sharpe of 1.5 (Bailey & Lopez de Prado 2012 MinTRL,
PSR power, and a DSR-style multiple-testing benchmark). Independent implementation; cross-checked
against the repo's goaltests/stats.py when its path is given as argv[1]."""
import math
import sys
from statistics import NormalDist

N = NormalDist()
G = 0.5772156649015329
D = 252  # trading days per year


def var_term(sr, skew, kurt):
    return 1 - skew * sr + (kurt - 1) / 4 * sr * sr


def mintrl(sr_ann, star_ann, conf=0.95, skew=0.0, kurt=3.0):
    sr, st = sr_ann / math.sqrt(D), star_ann / math.sqrt(D)
    z = N.inv_cdf(conf)
    return 1 + var_term(sr, skew, kurt) * (z / (sr - st)) ** 2


def n_for_power(sr_ann, star_ann, alpha=0.05, power=0.80, skew=0.0, kurt=3.0):
    """Days so that a one-sided test of SR <= star rejects with the given power when the true SR is sr."""
    sr, st = sr_ann / math.sqrt(D), star_ann / math.sqrt(D)
    za, zb = N.inv_cdf(1 - alpha), N.inv_cdf(power)
    return 1 + var_term(sr, skew, kurt) * ((za + zb) / (sr - st)) ** 2


def power_at(sr_ann, star_ann, n, alpha=0.05, skew=0.0, kurt=3.0):
    sr, st = sr_ann / math.sqrt(D), star_ann / math.sqrt(D)
    se = math.sqrt(var_term(sr, skew, kurt) / (n - 1))
    return N.cdf((sr - st) / se - N.inv_cdf(1 - alpha))


def exp_max_sr(trials, var_sr):
    return math.sqrt(var_sr) * ((1 - G) * N.inv_cdf(1 - 1 / trials)
                                + G * N.inv_cdf(1 - 1 / (trials * math.e)))


def dsr(sr_ann, n, trials, skew=0.0, kurt=3.0):
    sr = sr_ann / math.sqrt(D)
    sr0 = exp_max_sr(trials, 1.0 / n)
    return N.cdf((sr - sr0) * math.sqrt(n - 1) / math.sqrt(var_term(sr, skew, kurt)))


def n_for_dsr(sr_ann, trials, target=0.95, skew=0.0, kurt=3.0):
    n = 3
    while dsr(sr_ann, n, trials, skew, kurt) < target:
        n += 1
    return n


def yrs(n):
    return f"{n:7.0f} days = {n / D:5.1f} yr"


print("Target: true annualized net Sharpe 1.5 (daily SR = %.4f), 252 days/yr" % (1.5 / math.sqrt(D)))
print("\n1) MinTRL (observed SR = 1.5, PSR >= 95%), Bailey & Lopez de Prado 2012")
for skew, kurt, lab in [(0, 3, "normal"), (-0.5, 6, "skew -0.5, kurt 6"), (-1, 10, "skew -1, kurt 10")]:
    for star in (0.0, 0.5, 1.0):
        print(f"   {lab:18s} SR*={star:3.1f}: {yrs(mintrl(1.5, star, skew=skew, kurt=kurt))}")

print("\n2) Days for 80% power at alpha 5% (true SR = 1.5), normal")
for star in (0.0, 0.5, 1.0):
    print(f"   SR*={star:3.1f}: {yrs(n_for_power(1.5, star))}")

print("\n3) Autocorrelation: effective-sample inflation (Newey-West factor f) on 80%-power, SR*=0")
for f in (1.0, 1.25, 1.5):
    print(f"   f={f:4.2f}: {yrs(f * n_for_power(1.5, 0.0))}")

print("\n4) Power of PSR(SR*=0) at 95% after n days, true SR 1.5, normal")
for n in (120, 250, 500, 756, 1260, 2400):
    print(f"   n={n:5d} ({n / D:4.1f} yr): power = {power_at(1.5, 0.0, n):.2f}")

print("\n5) DSR >= 0.95 with observed SR 1.5 and N trials (var of SR across trials = 1/n)")
for trials in (10, 50, 100):
    print(f"   N={trials:4d}: {yrs(n_for_dsr(1.5, trials))}")

print("\n6) Same thresholds at true SR 1.0 and 2.0 (MinTRL, SR*=0, normal)")
for s in (1.0, 2.0, 3.0):
    print(f"   SR={s:3.1f}: {yrs(mintrl(s, 0.0))}")

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
    import stats  # repo module, imported read-only
    a = stats.min_track_record(stats.daily_sr(1.5), 0.0)
    b = mintrl(1.5, 0.0)
    c = stats.min_track_record(stats.daily_sr(1.5), stats.daily_sr(1.0), skew=-1, kurt=10)
    d = mintrl(1.5, 1.0, skew=-1, kurt=10)
    print(f"\nCross-check vs repo stats.py: {a:.2f} vs {b:.2f}; {c:.2f} vs {d:.2f}")

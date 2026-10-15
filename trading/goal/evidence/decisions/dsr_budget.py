"""DSR thresholds, power and program-level success vs. trial budget.

Formulas (Bailey & Lopez de Prado 2014, JPM 40(5)):
  SR0  = sqrt(V) * [ (1-g) * Z^-1(1 - 1/N) + g * Z^-1(1 - 1/(N e)) ]      (expected max SR of N null trials)
  DSR  = Phi( (SRhat - SR0) * sqrt(T-1) / sqrt(1 - s3*SRhat + (k4-1)/4 * SRhat^2) )
  SRhat, SR0 in per-period (daily) units; s3 = skewness, k4 = (non-excess) kurtosis; g = Euler-Mascheroni.
Sampling s.e. of a per-period SR estimate (Mertens 2002 / Opdyke 2007, used inside PSR/DSR):
  se(SR) = sqrt( (1 - s3*SR + (k4-1)/4 * SR^2) / (T-1) )
"""
import math
import statistics
import numpy as np

ND = statistics.NormalDist()
GAMMA = 0.5772156649015329
Q = 252  # trading days per year
Z95 = ND.inv_cdf(0.95)


def f_emax(n):
    """Bailey-LdP approximation of E[max of n iid N(0,1)]."""
    if n <= 1:
        return 0.0
    return (1 - GAMMA) * ND.inv_cdf(1 - 1 / n) + GAMMA * ND.inv_cdf(1 - 1 / (n * math.e))


_erf = np.frompyfunc(math.erf, 1, 1)


def exact_max_moments(n):
    x = np.linspace(-9, 9, 36001)
    phi = np.exp(-x * x / 2) / math.sqrt(2 * math.pi)
    Phi = 0.5 * (1 + _erf(x / math.sqrt(2)).astype(float))
    pdf = n * phi * Phi ** (n - 1)
    dx = x[1] - x[0]
    m1 = float(np.sum(x * pdf) * dx)
    m2 = float(np.sum(x * x * pdf) * dx)
    return m1, math.sqrt(max(m2 - m1 * m1, 0.0))


def se_ann(sr_ann, T, s3=0.0, k4=3.0, q=Q):
    s = sr_ann / math.sqrt(q)
    return math.sqrt(q) * math.sqrt((1 - s3 * s + (k4 - 1) / 4 * s * s) / (T - 1))


def dsr(sr_hat_ann, sr0_ann, T, s3=0.0, k4=3.0, q=Q):
    s = sr_hat_ann / math.sqrt(q)
    s0 = sr0_ann / math.sqrt(q)
    z = (s - s0) * math.sqrt(T - 1) / math.sqrt(1 - s3 * s + (k4 - 1) / 4 * s * s)
    return ND.cdf(z)


def required_sr(sr0_ann, T, s3=0.0, k4=3.0, conf=0.95, q=Q):
    lo, hi = sr0_ann, sr0_ann + 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if dsr(mid, sr0_ann, T, s3, k4, q) >= conf:
            hi = mid
        else:
            lo = mid
    return hi


def power(sr_true_ann, thr_ann, T, s3=0.0, k4=3.0, q=Q):
    return 1 - ND.cdf((thr_ann - sr_true_ann) / se_ann(sr_true_ann, T, s3, k4, q))


def hdr(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# ---------------------------------------------------------------------------
hdr("0. Validation against the DSR paper example (as reproduced by interactiveml.org): "
    "SR_ann=2.5, T=1250, N=100, V_ann=0.5, skew=-3, kurt=10")
for q in (250, 252):
    sr0 = math.sqrt(0.5) * f_emax(100)
    d = dsr(2.5, sr0, 1250, -3, 10, q)
    print(f"q={q}: SR0_ann={sr0:.4f}  SR0_daily={sr0/math.sqrt(q):.4f}  DSR={d:.4f}")
    # N at which DSR crosses 0.95 and 0.90
    for conf in (0.95, 0.90):
        nstar = None
        for n in range(2, 2000):
            if dsr(2.5, math.sqrt(0.5) * f_emax(n), 1250, -3, 10, q) < conf:
                nstar = n
                break
        print(f"   smallest N with DSR < {conf}: {nstar}")

hdr("0b. MinBTL check (Bailey, Borwein, LdP, Zhu 2014): years needed so that E[max null SR_ann] = 1 is f(N)^2")
for n in (10, 20, 45, 50, 100):
    print(f"N={n:4d}: f(N)={f_emax(n):.4f}  MinBTL(years, E[max]=1.0)={f_emax(n)**2:.2f}")

# ---------------------------------------------------------------------------
hdr("1. E[max] of N iid N(0,1): Bailey-LdP approximation vs exact; sqrt(2 ln N); s.d. of the max")
for n in (2, 5, 10, 20, 30, 50, 100, 200, 500, 1000):
    m1, sd = exact_max_moments(n)
    print(f"N={n:5d}: approx={f_emax(n):.4f} exact={m1:.4f} sqrt(2lnN)={math.sqrt(2*math.log(n)):.4f} sd(max)={sd:.4f}")

# ---------------------------------------------------------------------------
T = 2400
se0 = se_ann(0.0, T)
hdr(f"2. Program baseline: T={T} daily obs, V = null sampling variance -> s.e.(SR_ann)={se0:.4f}; "
    "required observed SR_ann for DSR>=0.95 and power")
print("N    f(N)   SR0_ann | req SR (normal) | req SR (skew-0.5,kurt6) | req SR (skew-1,kurt10) | "
      "power@1.0 power@1.25 power@1.5 power@2.0 (normal)")
for n in (1, 2, 5, 10, 15, 20, 30, 50, 100, 200, 500, 1000):
    sr0 = se0 * f_emax(n)
    r_n = required_sr(sr0, T)
    r_a = required_sr(sr0, T, -0.5, 6)
    r_b = required_sr(sr0, T, -1, 10)
    pw = [power(s, r_n, T) for s in (1.0, 1.25, 1.5, 2.0)]
    print(f"{n:5d} {f_emax(n):.3f} {sr0:.3f}  |   {r_n:.3f}         |   {r_a:.3f}                 |   {r_b:.3f}                | "
          + "  ".join(f"{p:.3f}" for p in pw))

hdr("2b. Same, power with non-normal returns (skew -0.5, kurt 6) and (skew -1, kurt 10) for true SR 1.5")
for n in (10, 20, 30, 50, 100):
    sr0 = se0 * f_emax(n)
    for (s3, k4) in ((-0.5, 6), (-1, 10)):
        r = required_sr(sr0, T, s3, k4)
        print(f"N={n:4d} skew={s3:5.1f} kurt={k4:3.0f}: req SR={r:.3f}  power@1.5={power(1.5, r, T, s3, k4):.3f}  power@1.0={power(1.0, r, T, s3, k4):.3f}")

# ---------------------------------------------------------------------------
hdr("3. Sensitivity to Newey-West effective sample size T_eff (normal returns, V = null variance at T_eff)")
for teff in (2400, 1800, 1200, 800):
    s0 = se_ann(0.0, teff)
    row = []
    for n in (10, 20, 50, 100):
        sr0 = s0 * f_emax(n)
        r = required_sr(sr0, teff)
        row.append(f"N={n}: req={r:.2f} pow1.5={power(1.5, r, teff):.2f}")
    print(f"T_eff={teff:5d} (se0={s0:.3f}): " + " | ".join(row))

# ---------------------------------------------------------------------------
hdr("4. Sensitivity to V (cross-trial dispersion of SR estimates), T=2400, normal returns")
for sd_ann in (se0 * math.sqrt(0.2), se0, 0.45, 0.55, 0.75):
    row = []
    for n in (10, 20, 50, 100):
        sr0 = sd_ann * f_emax(n)
        r = required_sr(sr0, T)
        row.append(f"N={n}: SR0={sr0:.2f} req={r:.2f} pow1.5={power(1.5, r, T):.2f}")
    print(f"sd across trials={sd_ann:.3f}: " + " | ".join(row))
# expected sample variance across trials when 1 true (SR 1.5) among N-1 nulls
print("Expected cross-sectional sd when 1 of N trials is a true SR 1.5 and the rest are null:")
for n in (10, 20, 50, 100):
    v = se0 ** 2 + (1.5 ** 2) * (n - 1) / (n * n)  # var of mixture: sampling var + between-trial var
    sd = math.sqrt(v)
    sr0 = sd * f_emax(n)
    r = required_sr(sr0, T)
    print(f"  N={n:4d}: sd={sd:.3f} SR0={sr0:.3f} req={r:.3f} power@1.5={power(1.5, r, T):.3f}")

# ---------------------------------------------------------------------------
hdr("5. Implied false-pass rate of the DSR>=0.95 gate (global null, independent trials, V known) vs Bonferroni / HLZ t=3")
for n in (10, 20, 50, 100):
    zstar = f_emax(n) + Z95  # threshold in s.e. units (normal returns, ignores tiny SR-dependence of s.e.)
    fwer = 1 - ND.cdf(zstar) ** n
    zb = ND.inv_cdf(1 - 0.05 / n)
    print(f"N={n:4d}: DSR z*={zstar:.3f} (SR_ann {zstar*se0:.3f}) FWER={fwer:.4f} | Bonferroni-5% z={zb:.3f} (SR_ann {zb*se0:.3f})")
print(f"HLZ t=3.0 hurdle at T=2400 corresponds to SR_ann = {3.0*math.sqrt(Q/T):.3f}; t=2.0 -> {2.0*math.sqrt(Q/T):.3f}")

# ---------------------------------------------------------------------------
hdr("6. Program-level Monte Carlo: prior pi=5% per independent idea, true SR_ann=1.5, T=2400, normal returns")
rng = np.random.default_rng(20261015)
R = 200_000
PI = 0.05
S = 1.5
se_true = se_ann(S, T)


def simulate(n_trials, v_mode, pi=PI, m_variants=1, rho=0.8, n_dsr=None, R=R):
    """n_trials total runs = K ideas x m variants. v_mode: 'null' (V=se0^2) or 'sample' (cross-sectional var).
    n_dsr: N used in DSR (default max(n_trials,10)). Returns P(any true pass), P(any false pass), FWER-like."""
    K = n_trials // m_variants
    true = rng.random((R, K)) < pi
    sr_true = np.where(true, S, 0.0)
    se_i = np.where(true, se_true, se0)
    z_idea = rng.standard_normal((R, K))
    z_var = rng.standard_normal((R, K, m_variants))
    if m_variants == 1:
        eps = z_idea[:, :, None]
    else:
        eps = math.sqrt(rho) * z_idea[:, :, None] + math.sqrt(1 - rho) * z_var
    est = sr_true[:, :, None] + se_i[:, :, None] * eps
    est = est.reshape(R, K * m_variants)
    is_true = np.repeat(true, m_variants, axis=1)
    nd = max(n_trials, 10) if n_dsr is None else n_dsr
    if v_mode == "null":
        sd = np.full(R, se0)
    else:
        sd = est.std(axis=1, ddof=1)
    sr0 = sd * f_emax(nd)
    # DSR with normal returns: z = (s - s0) sqrt(T-1)/sqrt(1 + s^2/2), s daily
    s = est / math.sqrt(Q)
    s0 = sr0[:, None] / math.sqrt(Q)
    z = (s - s0) * math.sqrt(T - 1) / np.sqrt(1 + 0.5 * s * s)
    passed = z >= Z95
    any_true = (passed & is_true).any(axis=1).mean()
    any_false = (passed & ~is_true).any(axis=1).mean()
    n_pass_true = (passed & is_true).sum()
    n_pass_false = (passed & ~is_true).sum()
    ppv = n_pass_true / max(n_pass_true + n_pass_false, 1)
    any_true_idea = true.any(axis=1).mean()
    return any_true, any_false, ppv, any_true_idea


print("Independent ideas (each run = new idea):")
print("  N   | V=null: P(find true) P(false pass) PPV | V=sample: P(find true) P(false pass) PPV | P(>=1 true idea exists) | analytic 1-(1-pi*pow)^N")
for n in (10, 20, 30, 50, 100):
    a = simulate(n, "null")
    b = simulate(n, "sample")
    r = required_sr(se0 * f_emax(max(n, 10)), T)
    analytic = 1 - (1 - PI * power(S, r, T)) ** n
    print(f"  {n:4d} |   {a[0]:.3f}  {a[1]:.4f}  {a[2]:.3f}            |   {b[0]:.3f}  {b[1]:.4f}  {b[2]:.3f}              |   {a[3]:.3f}                 | {analytic:.3f}")

print("\nGlobal null (pi=0): false-pass probability of the gate")
for n in (10, 20, 50, 100):
    a = simulate(n, "null", pi=0.0)
    b = simulate(n, "sample", pi=0.0)
    print(f"  N={n:4d}: V=null {a[1]:.4f}   V=sample {b[1]:.4f}")

print("\nParameter variants: K ideas x 3 variants each (within-idea corr 0.8), DSR N = raw run count vs N = ideas (clustered)")
for n in (9, 12, 21, 30, 51, 99):
    a = simulate(n, "sample", m_variants=3)
    c = simulate(n, "sample", m_variants=3, n_dsr=max(n // 3, 10))
    print(f"  runs={n:3d} ideas={n//3:3d}: raw-N P(find true)={a[0]:.3f} P(false)={a[1]:.4f} | clustered-N P(find true)={c[0]:.3f} P(false)={c[1]:.4f} | P(true idea exists)={a[3]:.3f}")

# ---------------------------------------------------------------------------
hdr("7. Data-accrual arithmetic")
print(f"Trading days for a fresh 2,400-day G1 window: {2400/Q:.2f} years")
print(f"9 months of calendar time ~ {9*21} trading days of new data; s.e.(SR_ann) on that = {se_ann(0, 189):.2f}")
se120 = se_ann(1.5, 120)
print(f"G2 120 days: s.e.(SR_ann) at true 1.5 = {se120:.2f}; P(observed SR<0 | true 1.5) = {ND.cdf(-1.5/se120):.3f}; "
      f"P(observed SR<1.0 | true 1.5) = {ND.cdf((1.0-1.5)/se120):.3f}")
for t in (1.645, 2.0, 3.0):
    print(f"Days of live/forward data for t={t} at true SR 1.5 (expected): {Q*(t/1.5)**2:.0f} days = {(t/1.5)**2:.2f} years")
# N at which E[max null SR] reaches the 1.0 floor with T=2400
lo, hi = 1.0, 1e9
for _ in range(300):
    mid = math.sqrt(lo * hi)
    if se0 * f_emax(mid) >= 1.0:
        hi = mid
    else:
        lo = mid
print(f"N at which E[max null SR_ann] = 1.0 with T=2400 (V=null): ~{hi:.0f} independent trials")
for target in (0.5, 0.75):
    lo, hi = 1.0, 1e9
    for _ in range(300):
        mid = math.sqrt(lo * hi)
        if se0 * f_emax(mid) >= target:
            hi = mid
        else:
            lo = mid
    print(f"N at which E[max null SR_ann] = {target} with T=2400: ~{hi:.0f}")

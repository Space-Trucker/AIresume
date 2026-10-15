"""Addendum: program success sensitivity (prior, true SR of real edges, V convention, parameter variants)."""
import math
import statistics
import numpy as np

ND = statistics.NormalDist()
GAMMA = 0.5772156649015329
Q = 252
Z95 = ND.inv_cdf(0.95)
T = 2400


def f_emax(n):
    if n <= 1:
        return 0.0
    return (1 - GAMMA) * ND.inv_cdf(1 - 1 / n) + GAMMA * ND.inv_cdf(1 - 1 / (n * math.e))


def se_ann(sr_ann, T, s3=0.0, k4=3.0, q=Q):
    s = sr_ann / math.sqrt(q)
    return math.sqrt(q) * math.sqrt((1 - s3 * s + (k4 - 1) / 4 * s * s) / (T - 1))


se0 = se_ann(0.0, T)
rng = np.random.default_rng(7)


def simulate(n_trials, v_mode, pi=0.05, S=1.5, m_variants=1, rho=0.8, R=200_000):
    K = n_trials // m_variants
    true = rng.random((R, K)) < pi
    sr_true = np.where(true, S, 0.0)
    se_i = np.where(true, se_ann(S, T), se0)
    z_idea = rng.standard_normal((R, K))
    if m_variants == 1:
        eps = z_idea[:, :, None]
    else:
        eps = math.sqrt(rho) * z_idea[:, :, None] + math.sqrt(1 - rho) * rng.standard_normal((R, K, m_variants))
    est = (sr_true[:, :, None] + se_i[:, :, None] * eps).reshape(R, K * m_variants)
    is_true = np.repeat(true, m_variants, axis=1)
    nd = max(n_trials, 10)
    if v_mode == "null":
        sd = np.full(R, se0)
    elif v_mode == "sample":
        sd = est.std(axis=1, ddof=1)
    elif v_mode == "floor_excl_max":
        # cross-sectional variance excluding the best trial, floored at the null sampling variance
        srt = np.sort(est, axis=1)[:, :-1]
        sd = np.maximum(srt.std(axis=1, ddof=1), se0)
    sr0 = sd * f_emax(nd)
    s = est / math.sqrt(Q)
    s0 = sr0[:, None] / math.sqrt(Q)
    z = (s - s0) * math.sqrt(T - 1) / np.sqrt(1 + 0.5 * s * s)
    passed = z >= Z95
    return (passed & is_true).any(axis=1).mean(), (passed & ~is_true).any(axis=1).mean(), true.any(axis=1).mean()


print("A. Parameter variants (3 per idea, within-idea corr 0.8), raw-N counting, V = null variance")
for n in (9, 12, 21, 30, 51):
    a = simulate(n, "null", m_variants=3)
    print(f"  runs={n:3d} ideas={n//3:3d}: P(find true)={a[0]:.3f} P(false)={a[1]:.4f} P(true idea exists)={a[2]:.3f}")

print("\nB. Independent ideas, V = max(null, cross-sectional var excluding best trial)")
for n in (10, 20, 30, 50, 100):
    a = simulate(n, "floor_excl_max")
    b = simulate(n, "floor_excl_max", pi=0.0)
    print(f"  N={n:4d}: P(find true)={a[0]:.3f} P(false pass)={a[1]:.4f} | global-null false pass={b[1]:.4f}")

print("\nC. Sensitivity of P(find true) to the true SR of real edges and to the prior (independent ideas, V = null)")
for S in (1.0, 1.25, 1.5, 2.0):
    row = []
    for n in (10, 20, 30, 50):
        row.append(f"N={n}: {simulate(n, 'null', S=S, R=100_000)[0]:.3f}")
    print(f"  true SR={S:.2f}: " + "  ".join(row))
for pi in (0.025, 0.05, 0.10):
    row = []
    for n in (10, 20, 30, 50):
        row.append(f"N={n}: {simulate(n, 'null', pi=pi, R=100_000)[0]:.3f}")
    print(f"  prior={pi:.3f} (SR 1.5): " + "  ".join(row))

print("\nD. Same with T_eff = 1200 (Newey-West halves the sample), V = null at T_eff")
T = 1200
se0 = se_ann(0.0, T)
for n in (10, 20, 30, 50):
    a = simulate(n, "null", R=100_000)
    print(f"  N={n:4d}: P(find true)={a[0]:.3f} P(false pass)={a[1]:.4f}")

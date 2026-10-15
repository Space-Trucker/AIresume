"""Statistics the gates use: Sharpe ratios and their sampling error, the Probabilistic and Deflated
Sharpe Ratios, and minimum track record length (Bailey & López de Prado 2012, 2014)."""
from __future__ import annotations

import math
from statistics import NormalDist, fmean

N01 = NormalDist()
EULER_GAMMA = 0.5772156649015329


def moments(xs: list[float]) -> tuple[float, float, float, float]:
    """Mean, standard deviation (n-1), skewness and kurtosis (not excess; 3 for a normal)."""
    n = len(xs)
    m = fmean(xs)
    d = [x - m for x in xs]
    m2 = sum(v * v for v in d) / n
    if m2 == 0:
        return m, 0.0, 0.0, 3.0
    m3 = sum(v ** 3 for v in d) / n
    m4 = sum(v ** 4 for v in d) / n
    sd = math.sqrt(m2 * n / (n - 1)) if n > 1 else 0.0
    return m, sd, m3 / m2 ** 1.5, m4 / m2 ** 2


def sharpe(xs: list[float]) -> float:
    """Per-period Sharpe ratio (mean over standard deviation)."""
    m, sd, _, _ = moments(xs)
    return m / sd if sd > 0 else 0.0


def psr(sr: float, sr_star: float, n: int, skew: float = 0.0, kurt: float = 3.0) -> float:
    """Probability that the true per-period Sharpe exceeds ``sr_star``, given an estimate ``sr`` from
    ``n`` observations with the given skewness and kurtosis."""
    var = 1 - skew * sr + (kurt - 1) / 4 * sr * sr
    if n < 2 or var <= 0:
        return 0.0
    return N01.cdf((sr - sr_star) * math.sqrt(n - 1) / math.sqrt(var))


def expected_max_sr(n_trials: int, var_sr: float) -> float:
    """Expected maximum of ``n_trials`` Sharpe estimates whose true value is zero, with variance
    ``var_sr`` across trials (the benchmark the Deflated Sharpe Ratio uses)."""
    if n_trials <= 1 or var_sr <= 0:
        return 0.0
    return math.sqrt(var_sr) * ((1 - EULER_GAMMA) * N01.inv_cdf(1 - 1 / n_trials)
                                + EULER_GAMMA * N01.inv_cdf(1 - 1 / (n_trials * math.e)))


def dsr(sr: float, n: int, n_trials: int, var_sr: float | None = None, skew: float = 0.0,
        kurt: float = 3.0) -> float:
    """Deflated Sharpe Ratio: the PSR against the best Sharpe expected from ``n_trials`` tries with no
    edge. Without a measured ``var_sr``, the variance of a Sharpe estimate from ``n`` observations
    with no edge is used (1/n)."""
    if var_sr is None:
        var_sr = 1.0 / max(n, 2)
    return psr(sr, expected_max_sr(n_trials, var_sr), n, skew, kurt)


def min_track_record(sr: float, sr_star: float = 0.0, confidence: float = 0.95, skew: float = 0.0,
                     kurt: float = 3.0) -> float:
    """Observations needed for a true Sharpe of ``sr`` to show PSR(sr_star) >= ``confidence``."""
    if sr <= sr_star:
        return math.inf
    z = N01.inv_cdf(confidence)
    return 1 + (1 - skew * sr + (kurt - 1) / 4 * sr * sr) * (z / (sr - sr_star)) ** 2


def autocorr_factor(xs: list[float], lags: int) -> float:
    """How much autocorrelation inflates the variance of a mean: 1 + 2 * sum of rho_k over lags 1 to
    ``lags`` with Bartlett weights 1 - k/(lags+1) (Newey and West). Never below 1, so negative
    autocorrelation does not make a record look longer than it is. Dividing the number of
    observations by it gives the effective number of independent observations."""
    n = len(xs)
    if lags <= 0 or n <= lags + 1:
        return 1.0
    m = fmean(xs)
    d = [x - m for x in xs]
    c0 = sum(v * v for v in d)
    if c0 == 0:
        return 1.0
    f = 1.0
    for k in range(1, lags + 1):
        f += 2 * (1 - k / (lags + 1)) * sum(d[i] * d[i - k] for i in range(k, n)) / c0
    return max(f, 1.0)


def max_drawdown(returns: list[float]) -> float:
    """Largest fall from a peak of the compounded equity curve, as a fraction of the peak."""
    eq = peak = 1.0
    worst = 0.0
    for r in returns:
        eq *= 1 + r
        peak = max(peak, eq)
        worst = max(worst, 1 - eq / peak)
    return worst


def annualize_sr(daily_sr: float, days: int = 252) -> float:
    return daily_sr * math.sqrt(days)


def daily_sr(annual_sr: float, days: int = 252) -> float:
    return annual_sr / math.sqrt(days)


def quantile(xs: list[float], q: float) -> float:
    s = sorted(xs)
    if not s:
        return math.nan
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def ols_alpha_beta(y: list[float], x: list[float]) -> tuple[float, float, list[float]]:
    """Intercept, slope and residual-plus-intercept series of y on x (the excess-return series)."""
    mx, my = fmean(x), fmean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx if sxx > 0 else 0.0
    alpha = my - beta * mx
    return alpha, beta, [b - beta * a for a, b in zip(x, y)]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson interval of a rate k/n; (0, 1) when there is nothing to count."""
    if n <= 0:
        return 0.0, 1.0
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def rolling_beta(y: list[float], x: list[float], window: int = 252) -> list[float | None]:
    """For each day t, the slope of y on x over the ``window`` days before t (as of the previous close),
    or None while fewer than ``window`` days are known."""
    out: list[float | None] = [None] * len(y)
    sx = sy = sxx = sxy = 0.0
    for t in range(len(y)):
        if t >= window:
            n = window
            var = sxx - sx * sx / n
            out[t] = (sxy - sx * sy / n) / var if var > 0 else 0.0
            a, b = x[t - window], y[t - window]
            sx -= a; sy -= b; sxx -= a * a; sxy -= a * b  # noqa: E702
        sx += x[t]; sy += y[t]; sxx += x[t] * x[t]; sxy += x[t] * y[t]  # noqa: E702
    return out

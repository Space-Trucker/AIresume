"""Synthetic track records whose true edge we set, so a gate's verdict can be checked against the
truth. Daily returns are mu + sigma * x, where the noise x has unit variance and one of four shapes:
normal, fat-tailed (Student t, 4 degrees of freedom), volatility clustering (GARCH(1,1) with t
innovations), or autocorrelated (AR(1), rho 0.1)."""
from __future__ import annotations

import math
import random

NOISE_MODELS = ("normal", "t4", "garch", "ar1")
AR1_RHO = 0.1


def _t4(rng: random.Random) -> float:
    # t(4) = z / sqrt(chi2_4 / 4), and chi2_4 = -2 ln(u1 u2); t(4) has variance 2
    u = (1.0 - rng.random()) * (1.0 - rng.random())
    return rng.gauss(0, 1) / math.sqrt(-math.log(u)) if u < 1.0 else 0.0


def noise(n: int, model: str, rng: random.Random) -> list[float]:
    if model == "normal":
        return [rng.gauss(0, 1) for _ in range(n)]
    if model == "t4":
        return [_t4(rng) for _ in range(n)]
    if model == "garch":
        a, b = 0.08, 0.90
        w = 1 - a - b
        var, prev, out = 1.0, 0.0, []
        for _ in range(n):
            var = w + a * prev * prev + b * var
            prev = math.sqrt(var) * _t4(rng)
            out.append(prev)
        return out
    if model == "ar1":
        rho, prev, out = AR1_RHO, rng.gauss(0, 1), []
        s = math.sqrt(1 - rho * rho)
        for _ in range(n):
            prev = rho * prev + s * rng.gauss(0, 1)
            out.append(prev)
        return out
    raise ValueError(model)


def five_day_factor(model: str) -> float:
    """Variance of a 5-day sum of the noise over 5 times its daily variance: 1 unless the noise is
    autocorrelated. A volatility budget measured on 5-day P&L sizes positions down by its root."""
    if model != "ar1":
        return 1.0
    return 1 + 2 * sum((1 - k / 5) * AR1_RHO ** k for k in range(1, 5))


def returns(n: int, mu: float, sigma: float, model: str, rng: random.Random) -> list[float]:
    return [mu + sigma * x for x in noise(n, model, rng)]


def best_of(mus: list[float], n_days: int, sigma: float, model: str,
            rng: random.Random) -> tuple[list[float], list[float], int]:
    """One strategy per true daily mean in ``mus``; returns the one with the highest Sharpe, every
    strategy's Sharpe (for the Deflated Sharpe Ratio), and the index of the one chosen."""
    from .stats import sharpe
    best, best_sr, best_i, srs = None, -math.inf, -1, []
    for i, mu in enumerate(mus):
        r = returns(n_days, mu, sigma, model, rng)
        s = sharpe(r)
        srs.append(s)
        if s > best_sr:
            best, best_sr, best_i = r, s, i
    return best, srs, best_i

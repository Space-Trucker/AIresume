"""Synthetic track records whose true edge we set, so a gate's verdict can be checked against the
truth. Daily returns are mu + sigma * x, where the noise x has unit variance and one of four shapes:
normal, fat-tailed (Student t, 4 degrees of freedom), volatility clustering (GARCH(1,1) with t
innovations), or autocorrelated (AR(1), rho 0.1)."""
from __future__ import annotations

import math
import random

NOISE_MODELS = ("normal", "t4", "garch", "ar1")


def _t4(rng: random.Random) -> float:
    z = rng.gauss(0, 1)
    chi2 = sum(rng.gauss(0, 1) ** 2 for _ in range(4))
    return z / math.sqrt(chi2 / 4) / math.sqrt(2)  # Student t(4) has variance 2


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
        rho, prev, out = 0.1, 0.0, []
        s = math.sqrt(1 - rho * rho)
        for _ in range(n):
            prev = rho * prev + s * rng.gauss(0, 1)
            out.append(prev)
        return out
    raise ValueError(model)


def returns(n: int, mu: float, sigma: float, model: str, rng: random.Random) -> list[float]:
    return [mu + sigma * x for x in noise(n, model, rng)]


def best_of(n_trials: int, n_days: int, mu: float, sigma: float, model: str,
            rng: random.Random) -> tuple[list[float], list[float]]:
    """``n_trials`` strategies with the same true daily mean; returns the one with the highest
    in-sample Sharpe and the list of every trial's Sharpe (for the Deflated Sharpe Ratio)."""
    from .stats import sharpe
    best, best_sr, srs = None, -math.inf, []
    for _ in range(n_trials):
        r = returns(n_days, mu, sigma, model, rng)
        s = sharpe(r)
        srs.append(s)
        if s > best_sr:
            best, best_sr = r, s
    return best, srs

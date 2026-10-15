"""What each gate rule in a goal file means, as code, so a track record can be judged by the rule
exactly as written. A record holds what an evaluation would observe; the gate says pass or fail. An
input a rule needs and the record lacks fails the gate: nothing passes by default.

Rule kinds:
* ``net_positive``: total net profit above zero, with optional minimum days, trades, drawdown limit
  and rule-breach count (the rule version 1 states);
* ``dsr``: research on history (G1). The Deflated Sharpe Ratio of the net excess returns must reach a
  threshold on enough out-of-sample days. Its benchmark is the best Sharpe expected from N variants
  with no edge, each with the sampling variance of a Sharpe ratio, where N is every variant ever
  evaluated on the history and never below ``min_trials``. The Sharpe itself must reach a minimum, in
  the whole history and in each chronological half; the history must make money; with costs raised by
  the stress multiplier the Sharpe must stay above a floor; a Sharpe above a plausibility ceiling
  needs a look-ahead audit, and with ``require_lag_audit`` every candidate needs one. The P&L must
  come from the conservative fill model;
* ``paper``: paper trading (G2), over a window fixed in advance: at least ``min_days`` days and
  ``min_risk_trades`` risk-bearing trades, the trades reached within ``max_days_to_trades`` days.
  Drawdown and rule limits; conservative fills; fidelity: paper tracks a rerun of the frozen G1
  strategy on the same days (the mean daily gap is not significantly worse than ``fidelity_margin_sr``
  Sharpe units, and at least ``min_trade_match`` of the rerun's trades appear in paper); and the
  window's excess return, and its net profit when required, above zero;
* ``sequential``: the live test (O8): a sequential probability ratio test of "no edge" against "the
  targeted edge" on the live daily excess returns, its log-likelihood ratio capped so that a long
  good run cannot hide a later decay. At each look, the ratio decides: stop, halve, or allow growth;
* ``owner_decision``: no statistical rule; the owner decides.

Returns are daily, as fractions of equity, net of the evaluation's cost model. With
``autocorr_lags`` set, every significance test counts effective observations: the number of days
divided by the variance inflation that autocorrelation over that many lags causes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import stats


@dataclass
class Record:
    daily: list[float]                        # net daily returns
    excess: list[float] | None = None          # net daily excess returns (market exposure removed)
    trades: int = 0                            # round trips
    risk_trades: int | None = None             # round trips that risked at least the minimum
    rule_breaches: int = 0
    n_trials: int | None = None                # variants ever evaluated on this history
    stressed: list[float] | None = None        # net daily excess returns with costs raised by the stress multiplier
    conservative_fills: bool | None = None     # P&L from fills only when price trades through
    audit_passed: bool = False                 # look-ahead audit done and clean
    lag_audit_ok: bool | None = None           # results did not improve with every input lagged one more bar
    days_to_min_trades: int | None = None      # paper days until the minimum number of risk-bearing trades
    rerun: list[float] | None = None           # daily excess returns of the frozen G1 strategy rerun on the paper days
    rerun_match: float | None = None           # share of the rerun's round trips that paper made too
    rotations: int = 0                         # times a held position was replaced by a candidate
    rotation_gain: list[float] | None = None   # daily net return with rotation less the same strategy without it
    regime: list[int] | None = None            # 1 on the more turbulent days (above the median VIX), 0 on the calmer
    # what the strategy did, for the risk rules
    every_position_has_stop: bool = True
    max_risk_per_trade_pct: float = 0.0
    max_risk_per_position_pct: float = 0.0
    max_open_risk_pct: float = 0.0
    max_gross_pct: float = 0.0
    max_position_pct: float = 0.0
    max_overnight_long_pct: float = 0.0        # largest long position held overnight
    max_overnight_short_pct: float = 0.0       # largest short position held overnight
    max_overnight_gross_pct: float = 0.0
    max_overnight_net_pct: float = 0.0         # beta-adjusted, long minus short
    max_overnight_dollar_net_pct: float = 0.0  # in dollars, long minus short
    max_holding_days: float = 0.0
    notes: list[str] = field(default_factory=list)


def _series(rec: Record, metric: str) -> list[float]:
    return rec.excess if metric == "excess" and rec.excess is not None else rec.daily


def regime_proxy(xs: list[float], window: int = 20) -> list[int]:
    """Where no VIX is recorded: 1 on days whose trailing volatility (the record's own, over
    ``window`` days) is above its median, 0 otherwise. The first days use what they have."""
    vols = []
    for i in range(len(xs)):
        w = xs[max(0, i - window + 1):i + 1]
        m = sum(w) / len(w)
        vols.append(sum((x - m) ** 2 for x in w) / len(w))
    cut = sorted(vols)[len(vols) // 2]
    return [1 if v > cut else 0 for v in vols]


def hac_lower(xs: list[float], confidence: float, lags: int) -> tuple[float, float]:
    """(mean, one-sided lower confidence bound of the mean), the variance widened for autocorrelation
    (Newey-West with ``lags`` lags)."""
    n = len(xs)
    m, sd, _, _ = stats.moments(xs)
    se = sd * math.sqrt(stats.autocorr_factor(xs, lags) / n) if n > 1 else math.inf
    return m, m - stats.N01.inv_cdf(confidence) * se


def lag_audit(now: list[float], lagged: list[float], alpha: float = 0.01) -> tuple[bool, str]:
    """The lag audit: the same strategy with every input one bar older. A leak collapses the Sharpe
    ratio, misaligned data raises it. Fails when, beyond the paired standard error at ``alpha``, the
    lagged Sharpe ratio falls below half the original or rises more than 10% above it."""
    n = min(len(now), len(lagged))
    a, b = now[:n], lagged[:n]
    s_a, s_b = stats.sharpe(a), stats.sharpe(b)
    ma, sa, _, _ = stats.moments(a)
    mb, sb, _, _ = stats.moments(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / max(n - 1, 1)
    rho = cov / (sa * sb) if sa > 0 and sb > 0 else 0.0
    se = math.sqrt(max(2 * (1 - rho), 1e-12) / n)          # paired difference of two daily Sharpe ratios
    z = stats.N01.inv_cdf(1 - alpha)
    if s_a / 2 - s_b > z * se:
        return False, f"lagged Sharpe {stats.annualize_sr(s_b):.2f} far below half of {stats.annualize_sr(s_a):.2f}: a leak"
    if s_b - 1.1 * s_a > z * se:
        return False, f"lagged Sharpe {stats.annualize_sr(s_b):.2f} far above {stats.annualize_sr(s_a):.2f}: misaligned data"
    return True, "clean"


def _fills(rule: dict, rec: Record) -> str | None:
    if rule.get("require_conservative_fills", True) and rec.conservative_fills is not True:
        return "P&L not from the conservative fill model" if rec.conservative_fills is False else "fill model not stated"
    return None


def evaluate(rule: dict, rec: Record) -> tuple[bool | None, str]:
    """(passed, why). ``None`` means the gate is not decided by a rule (the owner decides)."""
    kind = rule.get("kind")
    if kind == "owner_decision":
        return None, "owner decides"
    if kind == "net_positive":
        n = len(rec.daily)
        if n < rule.get("min_days", 0):
            return False, f"{n} days < {rule['min_days']}"
        if rec.trades < rule.get("min_trades", 0):
            return False, f"{rec.trades} trades < {rule['min_trades']}"
        if "max_drawdown_pct" in rule and stats.max_drawdown(rec.daily) * 100 > rule["max_drawdown_pct"]:
            return False, "drawdown limit"
        if "rule_breaches" in rule and rec.rule_breaches > rule["rule_breaches"]:
            return False, "rule breaches"
        total = sum(rec.daily)
        return total > 0, f"net {total:+.4f}"
    if kind == "dsr":
        series = _series(rec, rule.get("metric", "excess"))
        n = len(series)
        if n < rule.get("min_days", 0):
            return False, f"{n} out-of-sample days < {rule['min_days']}"
        if (why := _fills(rule, rec)) is not None:
            return False, why
        m, sd, sk, ku = stats.moments(series)
        sr = m / sd if sd > 0 else 0.0
        ceiling = rule.get("plausibility_sr_max")
        if ceiling is not None and stats.annualize_sr(sr) > ceiling and not rec.audit_passed:
            return False, f"Sharpe {stats.annualize_sr(sr):.1f} above {ceiling}: audit for leaks first"
        if rule.get("require_lag_audit") and rec.lag_audit_ok is not True:
            return False, "no clean lag audit" if rec.lag_audit_ok is None else "the lag audit failed: a leak, or misaligned data"
        if "sr_min" in rule and stats.annualize_sr(sr) < rule["sr_min"]:
            return False, f"Sharpe {stats.annualize_sr(sr):.2f} < {rule['sr_min']}"
        if "min_sr_each_half" in rule:
            half = n // 2
            for part in (series[:half], series[half:]):
                if stats.annualize_sr(stats.sharpe(part)) < rule["min_sr_each_half"]:
                    return False, f"Sharpe below {rule['min_sr_each_half']} in one half of the history"
        if rule.get("require_net_profit") and sum(rec.daily) <= 0:
            return False, "the history does not make money after costs"
        if rule.get("require_positive_by_regime"):
            regime = rec.regime if rec.regime is not None and len(rec.regime) == n else regime_proxy(series)
            for flag, name in ((0, "calmer"), (1, "more turbulent")):
                part = [x for x, r in zip(series, regime) if r == flag]
                if part and sum(part) <= 0:
                    return False, f"no excess return in the {name} half of the days"
        if rec.n_trials is None:
            return False, "the number of variants evaluated is not stated"
        trials = max(rec.n_trials, rule.get("min_trials", 1))
        n_eff = n / stats.autocorr_factor(series, rule.get("autocorr_lags", 0))
        d = stats.dsr(sr, n_eff, trials, None, sk, ku)   # null variance of a Sharpe ratio: 1 / n_eff
        if d < rule["dsr_min"]:
            return False, f"DSR {d:.3f} < {rule['dsr_min']}"
        if "stress_sr_min" in rule:
            if rec.stressed is None:
                return False, "no results with stressed costs"
            if stats.annualize_sr(stats.sharpe(rec.stressed)) < rule["stress_sr_min"]:
                return False, "fails with costs raised to the stress level"
        if "rotation_gain_confidence" in rule and rec.rotations > 0:
            # rotation is an add-on judged against the same strategy without it; the strategy itself
            # can still pass without rotation
            if rec.rotation_gain is None:
                return False, "a rotating strategy without its no-rotation twin: ship and judge the twin"
            m, low = hac_lower(rec.rotation_gain, rule["rotation_gain_confidence"], rule.get("autocorr_lags", 0))
            if low <= 0:
                return False, (f"rotation doesn't clearly pay ({m * 1e4:+.2f} bp a day, lower bound {low * 1e4:+.2f}): "
                               "ship and judge the strategy without rotation")
        return True, f"DSR {d:.3f}"
    if kind == "paper":
        series = _series(rec, rule.get("metric", "excess"))
        daily = rec.daily
        n = len(series)
        if n < rule.get("min_days", 0):
            return False, f"{n} paper days < {rule['min_days']}"
        risky = rec.risk_trades if rec.risk_trades is not None else rec.trades
        if risky < rule.get("min_risk_trades", 0):
            return False, f"{risky} risk-bearing trades < {rule['min_risk_trades']}"
        if "max_days_to_trades" in rule:
            if rec.days_to_min_trades is None:
                return False, "days to the minimum trades not stated"
            if rec.days_to_min_trades > rule["max_days_to_trades"]:
                return False, f"{rec.days_to_min_trades} days to reach the minimum trades > {rule['max_days_to_trades']}"
        if rec.rule_breaches > rule.get("rule_breaches", 0):
            return False, "rule breaches"
        if stats.max_drawdown(daily) * 100 > rule.get("max_drawdown_pct", math.inf):
            return False, "drawdown limit"
        if (why := _fills(rule, rec)) is not None:
            return False, why
        if "fidelity_noninferiority_sr" in rule:
            # non-inferiority: paper must show, with confidence, that it trails the rerun of the frozen
            # strategy by less than the margin; noise makes that harder to show, so G2 runs on (up to
            # max_days) until it is shown or the days run out
            if rec.rerun is None or rec.rerun_match is None or len(rec.rerun) != n:
                return False, "no rerun of the frozen G1 strategy to compare with"
            if rec.rerun_match < rule.get("min_trade_match", 0.0):
                return False, f"only {rec.rerun_match:.0%} of trades matched between paper and the rerun"
            gap = [p - q for p, q in zip(series, rec.rerun)]
            vol = stats.moments(rec.rerun)[1]
            margin = rule["fidelity_noninferiority_sr"] / math.sqrt(252) * vol
            gm, low = hac_lower(gap, 1 - rule.get("fidelity_alpha", 0.05), rule.get("autocorr_lags", 0))
            if low <= -margin:
                if n < rule.get("max_days", n):
                    return None, f"continue: fidelity not yet shown (lower bound {low / vol * math.sqrt(252):+.2f} Sharpe)"
                return False, f"paper may trail the rerun by more than {rule['fidelity_noninferiority_sr']:g} Sharpe"
        m = sum(series) / n
        if m <= 0:
            return False, "paper excess return not positive"
        if rule.get("require_net_profit") and sum(daily) <= 0:
            return False, "the paper account did not make money"
        return True, f"excess {m * 252:+.2%} a year"
    raise ValueError(f"unknown gate rule kind {kind!r}")


def sequential(rule: dict, excess: list[float]) -> list[tuple[int, str]]:
    """The live test's decisions on a record of daily excess returns: (day, action) at each look,
    action one of "stop", "halve", "hold" (no growth) or "grow" (capital may grow). It stops at the
    first "stop". The test runs on returns summed over ``block_days`` (so short-lived autocorrelation
    does not count as evidence), and its log-likelihood ratio of "the targeted edge" against "no edge"
    uses the record's own volatility, capped at ``cap`` so a long good run cannot hide a later decay.
    It looks every ``look_every_days`` (rounded to whole blocks), after ``burn_in_days``."""
    block = max(1, int(rule.get("block_days", 1)))
    sr1 = rule["h1_sr"] / math.sqrt(252 / block)
    every = max(1, round(rule.get("look_every_days", 21) / block))
    burn = rule.get("burn_in_days", 21)
    llr, out = 0.0, []
    total = sq = 0.0
    n_blocks = len(excess) // block
    for b in range(1, n_blocks + 1):
        x = sum(excess[(b - 1) * block:b * block])
        total += x
        sq += x * x
        if b < 2:
            continue
        mean = total / b
        sd = math.sqrt(max(sq / b - mean * mean, 1e-18) * b / (b - 1))
        llr = min(rule["cap"], llr + sr1 * x / sd - sr1 * sr1 / 2)
        day = b * block
        if day >= burn and b % every == 0:
            if llr <= rule["stop_at"]:
                out.append((day, "stop"))
                return out
            out.append((day, "halve" if llr <= rule["halve_at"] else ("grow" if llr >= rule.get("grow_at", 0.0) else "hold")))
    return out


def risk_rule_violations(risk: dict, rec: Record) -> list[str]:
    """The limits a goal's risk section sets that this record breaks. A limit the goal does not set
    cannot be broken: that is how a vague goal lets bad behavior through."""
    out = []
    overnight = max(rec.max_overnight_long_pct, rec.max_overnight_short_pct)
    checks = [("risk_per_trade_pct", rec.max_risk_per_trade_pct, "risk per trade"),
              ("risk_per_position_pct", rec.max_risk_per_position_pct, "risk per position"),
              ("max_open_risk_pct", rec.max_open_risk_pct, "open risk"),
              ("max_open_risk_per_side_pct", rec.max_open_risk_pct, "open risk on one side"),
              ("max_gross_exposure_pct", rec.max_gross_pct, "gross exposure"),
              ("max_position_pct", rec.max_position_pct, "position size"),
              ("max_position_overnight_pct", overnight, "overnight position size"),
              ("max_overnight_long_pct", rec.max_overnight_long_pct, "overnight long position"),
              ("max_overnight_short_pct", rec.max_overnight_short_pct, "overnight short position"),
              ("max_overnight_gross_pct", rec.max_overnight_gross_pct, "overnight gross exposure"),
              ("max_overnight_net_pct", rec.max_overnight_net_pct, "overnight net exposure"),
              ("max_overnight_dollar_net_pct", rec.max_overnight_dollar_net_pct, "overnight dollar net exposure")]
    for key, observed, what in checks:
        if key in risk and observed > risk[key] + 1e-9:
            out.append(f"{what} {observed:g}% > {risk[key]:g}%")
    if risk.get("stop_required") and not rec.every_position_has_stop:
        out.append("a position without a stop")
    return out

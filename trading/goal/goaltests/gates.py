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
    rotation_values: list[float] | None = None  # each rotation's realized value: new result less the replaced one's forgone result
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
    max_holding_days: float = 0.0
    notes: list[str] = field(default_factory=list)


def _series(rec: Record, metric: str) -> list[float]:
    return rec.excess if metric == "excess" and rec.excess is not None else rec.daily


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
            return False, "no clean lag audit" if rec.lag_audit_ok is None else "results improve with inputs lagged: a leak"
        if "sr_min" in rule and stats.annualize_sr(sr) < rule["sr_min"]:
            return False, f"Sharpe {stats.annualize_sr(sr):.2f} < {rule['sr_min']}"
        if "min_sr_each_half" in rule:
            half = n // 2
            for part in (series[:half], series[half:]):
                if stats.annualize_sr(stats.sharpe(part)) < rule["min_sr_each_half"]:
                    return False, f"Sharpe below {rule['min_sr_each_half']} in one half of the history"
        if rule.get("require_net_profit") and sum(rec.daily) <= 0:
            return False, "the history does not make money after costs"
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
        if "min_rotations_judged" in rule and rec.rotations > 0:
            values = rec.rotation_values
            if values is None:
                return False, "rotations not followed to the replaced positions' planned exits"
            if len(values) < rule["min_rotations_judged"]:
                return False, f"{len(values)} rotations < {rule['min_rotations_judged']}: too few to judge; run without rotation"
            m, sd, _, _ = stats.moments(values)
            low = m - stats.N01.inv_cdf(rule.get("rotation_confidence", 0.5)) * sd / math.sqrt(len(values))
            if low <= 0:
                return False, (f"rotations don't clearly pay: mean {m:+.5f} of equity each, lower bound {low:+.5f}; "
                               "run without rotation")
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
        if "fidelity_margin_sr" in rule:
            if rec.rerun is None or rec.rerun_match is None or len(rec.rerun) != n:
                return False, "no rerun of the frozen G1 strategy to compare with"
            if rec.rerun_match < rule.get("min_trade_match", 0.0):
                return False, f"only {rec.rerun_match:.0%} of the rerun's trades made on paper"
            gap = [p - q for p, q in zip(series, rec.rerun)]
            gm, gsd, _, _ = stats.moments(gap)
            vol = stats.moments(rec.rerun)[1]
            margin = rule["fidelity_margin_sr"] / math.sqrt(252) * vol
            if gsd > 0:
                g_eff = n / stats.autocorr_factor(gap, rule.get("autocorr_lags", 0))
                z = (gm + margin) / (gsd / math.sqrt(g_eff))
                if stats.N01.cdf(z) < rule.get("fidelity_alpha", 0.05):
                    return False, f"paper falls short of the rerun (z {z:.2f})"
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
              ("max_overnight_net_pct", rec.max_overnight_net_pct, "overnight net exposure")]
    for key, observed, what in checks:
        if key in risk and observed > risk[key] + 1e-9:
            out.append(f"{what} {observed:g}% > {risk[key]:g}%")
    if risk.get("stop_required") and not rec.every_position_has_stop:
        out.append("a position without a stop")
    return out

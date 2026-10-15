"""What each gate rule in a goal file means, as code, so a track record can be judged by the rule
exactly as written. A record holds what an evaluation would observe; the gate says pass or fail.

Rule kinds:
* ``net_positive``: total net profit above zero, with optional minimum days, trades, drawdown limit
  and rule-breach count (the rule version 1 states);
* ``dsr``: research on history (G1); the Deflated Sharpe Ratio of the net excess returns, over the
  variants tried, must reach a threshold on enough out-of-sample days, and the Sharpe itself a
  minimum. The benchmark is the best Sharpe expected from that many variants with no edge, each with
  the sampling variance of a Sharpe ratio (``trial_variance = "observed"`` uses the variance across
  the variants instead, as Bailey and López de Prado do when the variants can't be counted). With
  costs raised by the stress multiplier the Sharpe must stay above a floor, and a Sharpe above a
  plausibility ceiling needs an audit for look-ahead leaks. The P&L must come from the conservative
  fill model;
* ``paper``: paper trading (G2): enough days and risk-bearing trades, drawdown and rule limits,
  conservative fills, the combined out-of-sample and paper record significant, and paper results not
  significantly below what G1 promised;
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
    daily: list[float]                       # net daily returns
    excess: list[float] | None = None         # net daily excess returns (market exposure removed)
    trades: int = 0                           # round trips
    risk_trades: int | None = None            # round trips that risked at least the minimum
    rule_breaches: int = 0
    n_trials: int = 1                         # variants tried before choosing this one
    trial_srs: list[float] | None = None      # every variant's daily Sharpe
    stressed: list[float] | None = None       # net daily returns with costs raised by the stress multiplier
    oos: list[float] | None = None            # G1 out-of-sample excess returns (for G2)
    claimed_sr: float | None = None           # G1's daily Sharpe estimate (for G2)
    conservative_fills: bool = True           # P&L from fills only when price trades through
    audit_passed: bool = False                # look-ahead audit done and clean
    # what the strategy did, for the risk rules
    every_position_has_stop: bool = True
    max_risk_per_trade_pct: float = 0.0
    max_risk_per_position_pct: float = 0.0
    max_open_risk_pct: float = 0.0
    max_gross_pct: float = 0.0
    max_position_pct: float = 0.0
    max_overnight_long_pct: float = 0.0       # largest long position held overnight
    max_overnight_short_pct: float = 0.0      # largest short position held overnight
    max_overnight_gross_pct: float = 0.0
    max_overnight_net_pct: float = 0.0        # beta-adjusted, long minus short
    max_holding_days: float = 0.0
    notes: list[str] = field(default_factory=list)


def _series(rec: Record, metric: str) -> list[float]:
    return rec.excess if metric == "excess" and rec.excess is not None else rec.daily


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
        if rule.get("require_conservative_fills", True) and not rec.conservative_fills:
            return False, "P&L not from conservative fills"
        m, sd, sk, ku = stats.moments(series)
        sr = m / sd if sd > 0 else 0.0
        ceiling = rule.get("plausibility_sr_max")
        if ceiling is not None and stats.annualize_sr(sr) > ceiling and not rec.audit_passed:
            return False, f"Sharpe {stats.annualize_sr(sr):.1f} above {ceiling}: audit for leaks first"
        if "sr_min" in rule and stats.annualize_sr(sr) < rule["sr_min"]:
            return False, f"Sharpe {stats.annualize_sr(sr):.2f} < {rule['sr_min']}"
        n_eff = n / stats.autocorr_factor(series, rule.get("autocorr_lags", 0))
        var = None  # the sampling variance of a Sharpe ratio with no edge: 1 / n_eff
        if rule.get("trial_variance") == "observed" and rec.trial_srs and len(rec.trial_srs) > 1:
            mt = sum(rec.trial_srs) / len(rec.trial_srs)
            var = sum((s - mt) ** 2 for s in rec.trial_srs) / (len(rec.trial_srs) - 1)
        d = stats.dsr(sr, n_eff, max(rec.n_trials, 1), var, sk, ku)
        if d < rule["dsr_min"]:
            return False, f"DSR {d:.3f} < {rule['dsr_min']}"
        floor = rule.get("stress_sr_min")
        if floor is not None and rec.stressed is not None:
            if stats.annualize_sr(stats.sharpe(rec.stressed)) < floor:
                return False, "fails with costs raised to the stress level"
        return True, f"DSR {d:.3f}"
    if kind == "paper":
        series = _series(rec, rule.get("metric", "excess"))
        first = rule.get("min_days", 0)
        if len(series) < first:
            return False, f"{len(series)} paper days < {first}"
        # paper trading runs min_days; if its excess return is not positive by then, it runs once more
        # for extend_days and is judged on everything (a real edge loses over 60 days now and then)
        if rule.get("extend_days") and sum(series[:first]) <= 0 and len(series) >= first + rule["extend_days"]:
            series = series[:first + rule["extend_days"]]
            daily = rec.daily[:first + rule["extend_days"]]
        else:
            series = series[:first] if first else series
            daily = rec.daily[:len(series)]
        n = len(series)
        risky = rec.risk_trades if rec.risk_trades is not None else rec.trades
        if risky < rule.get("min_risk_trades", 0):
            return False, f"{risky} risk-bearing trades < {rule['min_risk_trades']}"
        if rec.rule_breaches > rule.get("rule_breaches", 0):
            return False, "rule breaches"
        if stats.max_drawdown(daily) * 100 > rule.get("max_drawdown_pct", math.inf):
            return False, "drawdown limit"
        if rule.get("require_conservative_fills", True) and not rec.conservative_fills:
            return False, "P&L not from conservative fills"
        m, sd, sk, ku = stats.moments(series)
        lags = rule.get("autocorr_lags", 0)
        if rec.claimed_sr is not None and sd > 0:
            # one-sided test: is paper's mean significantly below the mean G1 promised?
            n_eff = n / stats.autocorr_factor(series, lags)
            z = (m - rec.claimed_sr * sd) / (sd / math.sqrt(n_eff))
            if stats.N01.cdf(z) < rule.get("shortfall_alpha", 0.05):
                return False, f"paper below G1's promise (z {z:.2f})"
        combined = (rec.oos or []) + series
        cm, csd, csk, cku = stats.moments(combined)
        c_eff = len(combined) / stats.autocorr_factor(combined, lags)
        p = stats.psr(cm / csd if csd > 0 else 0.0, 0.0, c_eff, csk, cku)
        if p < rule.get("combined_psr_min", 0.0):
            return False, f"combined PSR {p:.3f} < {rule['combined_psr_min']}"
        if m <= 0:
            return False, "paper excess return not positive"
        return True, f"combined PSR {p:.3f}"
    raise ValueError(f"unknown gate rule kind {kind!r}")


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

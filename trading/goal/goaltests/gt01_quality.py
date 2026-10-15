"""GT-1: statement quality. Oracle: the characteristics ISO/IEC/IEEE 29148 asks of each requirement
(necessary, unambiguous, singular, feasible, verifiable, free of design) and of the set (complete,
consistent), applied as rules."""
from __future__ import annotations

import math
import os
import re

from .spec import Check, rule

TEST = "GT-1"
KIND = "presence"
METHODS = {"test", "analysis", "inspection", "demonstration"}
KINDS = {"achieve", "maintain", "avoid"}
# words with no agreed measure (ISO 29148 lists these kinds of terms as signs of ambiguity)
VAGUE = ["realistic", "strict", "fast", "quick", "robust", "adequate", "appropriate", "as needed",
         "etc", "and/or", "user-friendly", "constantly", "all day", "whole market", "small", "large",
         "minimize", "maximize", "best", "good", "about", "approximately", "several", "some", "many",
         "few", "no crashes", "heavily traded", "penny"]
# statements of how, not what: the goal must stay free of architecture
DESIGN = ["ai model", "fast code", "code", "database", "python", "server", "llm", "neural",
          "machine learning", "websocket", "cloud", "docker", "kubernetes", "microservice", "split-second calls"]
# constraints that must be numbers for the goal to be testable
REQUIRED_NUMBERS = {
    "constraints": ["max_holding_trading_days", "max_holding_calendar_days", "universe_min_price_usd",
                    "universe_min_dollar_volume_usd", "universe_max_spread_bps"],
    "risk": ["risk_per_position_pct", "max_open_risk_pct", "max_position_pct",
             "max_position_overnight_pct", "max_gross_exposure_pct", "daily_loss_limit_pct",
             "max_drawdown_halt_pct", "vol_target_daily_pct"],
    "costs": ["round_trip_cost_bps", "stress_cost_multiplier"],
    "activity": ["cost_budget_pct_per_year", "min_risk_trades_per_week"],
    "returns": ["min_net_excess_sharpe", "target_net_excess_sharpe"],
}
# a required number that may instead be given as several more specific ones
ALTERNATIVES = {"max_position_overnight_pct": ("max_overnight_long_pct", "max_overnight_short_pct")}
# what a key result must cover, from outside the goal: the owner's own needs (goal_v1.toml), the
# regulations GT-7 applies, and the method's evidence rules. Each concern names its source and the
# words one key result's statement must contain (every group, any word of a group). Deleting the key
# result for a concern fails the goal; GT-7 checks the controls the same way
REQUIRED_RESULTS = [
    ("an edge net of costs and luck, on history it was not built on", "owner; Bailey and Lopez de Prado",
     [["deflated sharpe"]]),
    ("paper trading makes money after costs before real money", "owner", [["paper"], ["makes money", "profit"]]),
    ("every share covered by a stop at the broker that acts while the system is down",
     "owner (strict risk rules); RTS 6 Art. 14", [["stop"], ["broker"], ["stopped", "disconnected"]]),
    ("a kill switch", "owner; RTS 6 Art. 12", [["kill switch"]]),
    ("the drawdown halt", "owner (never more than 10% below the peak)", [["halt"], ["below its highest", "below its peak"]]),
    ("no order breaks a limit", "owner (a risk manager with fixed limits blocks any trade); 15c3-5",
     [["no order"], ["limit"]]),
    ("positions closed within the holding limit", "owner", [["closed within"], ["trading days"]]),
    ("a daily report", "owner", [["daily report"]]),
    ("live profit and loss the owner can see", "owner", [["profit and loss"], ["see", "shown"]]),
    ("positions and orders match the broker's", "15c3-5(c)(2); Knight Capital", [["match the broker"]]),
    ("no trades against the system's own orders", "FINRA 15-09 (wash trades)", [["own orders"]]),
    ("short sales only when easy to borrow", "Regulation SHO (locate)", [["easy to borrow"]]),
    ("message rates bounded", "RTS 6 Art. 15", [["messages"]]),
    ("every variant registered and counted", "Harvey, Liu and Zhu; Bailey and Lopez de Prado",
     [["every variant"], ["registered"]]),
    ("point-in-time history", "survivorship and look-ahead bias", [["point-in-time"]]),
    ("independent challenge before each gate", "SR 11-7 / SR 26-2", [["independent"], ["review"]]),
    ("a live test that stops a strategy whose edge has gone", "owner (drop strategies)",
     [["sequential test"], ["stops"]]),
    ("weekly review, and changes only through the evidence", "owner", [["reviewed every"], ["registration"]]),
    ("live costs checked against the cost model", "the cost model is an assumption until real fills test it",
     [["live"], ["cost model"]]),
]
NUMBER_WORDS = {2: "twice", 3: "three times", 4: "four times"}


def _num(spec: dict, path: str):
    """A setting by path: "G1.dsr_min" reads gate G1's rule, "risk.max_drawdown_pct" a section."""
    head, key = path.split(".", 1)
    values = rule(spec, head) if head.startswith("G") and head[1:].isdigit() else spec.get(head, {})
    return values.get(key)


# key results that restate a setting: the field must state the setting's value (a threshold must equal
# it; a number in a text must appear in it). A goal whose key result and setting disagree says two things
RESTATES = [
    ("KR1.1", "threshold", lambda s: _num(s, "G1.dsr_min")),
    ("KR1.2", "threshold", lambda s: _num(s, "G1.sr_min")),
    ("KR1.2", "threshold", lambda s: _num(s, "returns.min_net_excess_sharpe")),
    ("KR1.2", "objective_value", lambda s: _num(s, "returns.target_net_excess_sharpe")),
    ("KR1.3", "threshold", lambda s: _num(s, "G1.stress_sr_min")),
    ("KR1.3", "statement", lambda s: None if _num(s, "costs.stress_cost_multiplier") is None
     else round((_num(s, "costs.stress_cost_multiplier") - 1) * 100, 6)),
    ("KR1.5", "threshold", lambda s: None if _num(s, "G2.fidelity_noninferiority_sr") is None
     else -_num(s, "G2.fidelity_noninferiority_sr")),
    ("KR1.5", "statement", lambda s: _num(s, "G2.min_days")),
    ("KR1.5", "statement", lambda s: _num(s, "G2.max_days")),
    ("KR1.6", "threshold", lambda s: None if _num(s, "G2.min_trade_match") is None
     else round(_num(s, "G2.min_trade_match") * 100, 6)),
    ("KR1.7", "window", lambda s: _num(s, "G2.min_days")),
    ("KR1.7", "window", lambda s: _num(s, "G2.min_risk_trades")),
    ("KR1.9", "threshold", lambda s: _num(s, "G1.min_sr_each_half")),
    ("KR2.2", "statement", lambda s: _num(s, "risk.max_drawdown_halt_pct")),
    ("KR2.3", "threshold", lambda s: _num(s, "risk.max_day_loss_pct")),
    ("KR2.3", "statement", lambda s: _num(s, "risk.daily_loss_limit_pct")),
    ("KR2.6", "threshold", lambda s: None if None in (_num(s, "risk.vol_target_daily_pct"), _num(s, "risk.vol_max_multiple"))
     else round(_num(s, "risk.vol_target_daily_pct") * _num(s, "risk.vol_max_multiple"), 6)),
    ("KR2.6", "statement", lambda s: _num(s, "risk.vol_max_multiple")),
    ("KR2.7", "threshold", lambda s: _num(s, "risk.max_drawdown_pct")),
    ("KR2.8", "threshold", lambda s: _num(s, "risk.max_jump_loss_pct")),
    ("KR3.1", "statement", lambda s: _num(s, "activity.entry_min_gain_to_cost")),
    ("KR3.2", "statement", lambda s: _num(s, "constraints.max_holding_trading_days")),
    ("KR3.2", "statement", lambda s: _num(s, "constraints.max_holding_calendar_days")),
    ("KR3.3", "statement", lambda s: _num(s, "order_limits.data_max_age_seconds")),
    ("KR3.4", "threshold", lambda s: _num(s, "G2.max_days_to_trades")),
    ("KR3.4", "statement", lambda s: _num(s, "G2.min_risk_trades")),
    ("KR3.4", "metric", lambda s: _num(s, "activity.risk_bearing_min_risk_pct")),
    ("KR4.4", "threshold", lambda s: _num(s, "order_limits.stop_check_seconds")),
    ("KR5.2", "threshold", lambda s: _num(s, "order_limits.max_orders_per_fill")),
    ("KR6.1", "statement", lambda s: _num(s, "G1.min_trials")),
    ("KR7.3", "statement", lambda s: _num(s, "order_limits.report_deadline_new_york")),
    ("KR8.1", "statement", lambda s: _num(s, "live.review_every_trading_days")),
    ("KR8.1", "statement", lambda s: _num(s, "live.forward_validation_days")),
    ("KR8.2", "odds", lambda s: _num(s, "live.test_stop_llr")),
    ("KR8.2", "odds", lambda s: _num(s, "live.test_halve_llr")),
    ("KR8.2", "odds", lambda s: _num(s, "live.test_grow_llr")),
    ("KR8.2", "statement", lambda s: None if _num(s, "evaluation.max_false_stop_3y") is None
     else round(_num(s, "evaluation.max_false_stop_3y") * 100, 6)),
]


def _states(text: str, value) -> bool:
    """Whether a text states a value: as a number standing alone (9 in "9%", not in "19"), in its
    thousands form, or as a word ("twice")."""
    if isinstance(value, str):
        return value in text
    forms = {f"{value:g}"} | ({f"{int(value):,}"} if float(value).is_integer() and abs(value) >= 1000 else set())
    if any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", text) for f in forms):
        return True
    return float(value).is_integer() and NUMBER_WORDS.get(int(value), "\0") in text.lower()


# defined terms that contain a vague word
TERMS = ["best bid or offer", "best bid", "best offer"]


def _words(text: str, terms: list[str]) -> list[str]:
    low = text.lower()
    for t in TERMS:
        low = low.replace(t, " ")
    return [t for t in terms if re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low)]


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="", kind="": out.append(Check(TEST, name, ok, detail, kind))  # noqa: E731

    intent = spec.get("intent", {})
    add("mission stated", bool(intent.get("mission")))
    add("viewpoint stated", bool(intent.get("viewpoint")))
    add("non-goals stated (scope is bounded)", bool(intent.get("non_goals")),
        "" if intent.get("non_goals") else "nothing is declared out of scope")
    add("stakeholders and their needs stated", bool(spec.get("stakeholders")))

    objectives = {o["id"]: o for o in spec.get("objectives", [])}
    krs = spec.get("key_results", [])
    gates = {g["id"] for g in spec.get("gates", [])}
    for oid, o in objectives.items():
        mine = [k for k in krs if k.get("objective") == oid]
        add(f"{oid} has a measurable key result", bool(mine))
        design = _words(o.get("statement", ""), DESIGN)
        add(f"{oid} states what, not how", not design, ", ".join(design))
        # KAOS: every goal is achieve, maintain or avoid; GQM: every goal asks the question its
        # key results answer
        add(f"{oid} has a goal kind (KAOS)", o.get("kind") in KINDS, o.get("kind", "none"))
        add(f"{oid} states the question its key results answer (GQM)", bool(o.get("question")))

    for k in krs:
        kid = k.get("id", "?")
        missing = [f for f in ("metric", "unit", "comparator", "threshold", "window", "data", "method", "gate")
                   if f not in k or k[f] in ("", None)]
        add(f"{kid} is verifiable (metric, unit, threshold, window, data, method, gate)", not missing,
            "missing " + ", ".join(missing) if missing else "")
        add(f"{kid} traces to an objective", k.get("objective") in objectives)
        if "method" in k:
            add(f"{kid} uses an ISO 29148 verification method", k["method"] in METHODS, k["method"])
        if "gate" in k:
            mine = k["gate"] if isinstance(k["gate"], list) else [k["gate"]]
            add(f"{kid} belongs to a gate that exists", all(g in gates for g in mine), ", ".join(mine))
        vague = _words(k.get("statement", ""), VAGUE)
        add(f"{kid} is unambiguous", not vague, ", ".join(vague))
        design = _words(k.get("statement", ""), DESIGN)
        add(f"{kid} is free of design", not design, ", ".join(design))

    for section, keys in REQUIRED_NUMBERS.items():
        values = spec.get(section, {})
        number = lambda key: isinstance(values.get(key), (int, float))  # noqa: E731
        absent = [key for key in keys if not number(key)
                  and not (key in ALTERNATIVES and all(number(k) for k in ALTERNATIVES[key]))]
        add(f"{section}: the limits are numbers", not absent, "unspecified: " + ", ".join(absent) if absent else "")
    # every text that states a limit or a rule, not only key results: a vague word anywhere in them
    # leaves a limit open (version 4 scanned four sections; "a realistic price" in [measurement] passed)
    texts: list[tuple[str, str]] = []
    for section in ("constraints", "risk", "costs", "activity", "returns", "measurement", "order_limits",
                    "kill_criteria", "live", "evaluation"):
        texts += [(f"{section}.{key}", v) for key, v in spec.get(section, {}).items() if isinstance(v, str)]
    for g in spec.get("gates", []):
        texts += [(f"{g['id']}.{key}", v) for key, v in g.get("rule", {}).items() if isinstance(v, str)]
    texts += [(c.get("id", "?"), c.get("statement", "")) for c in spec.get("controls", [])]
    found = sorted({f"{where}: {w}" for where, t in texts for w in _words(t, VAGUE)})
    add("every limit, rule and control is stated without vague words", not found, "; ".join(found))

    # what the key results must cover, from outside the goal
    statements = [(k.get("id", "?"), k.get("statement", "").lower()) for k in krs]
    for concern, source, groups in REQUIRED_RESULTS:
        hit = next((kid for kid, t in statements if all(any(w in t for w in g) for g in groups)), None)
        add(f"a key result covers {concern} ({source})", hit is not None, hit or "no key result states it")

    # a count that must be zero: "no X" with a tolerance is "some X"
    loose = [k.get("id", "?") for k in krs if k.get("unit") == "count" and k.get("comparator") in ("==", "<=")
             and k.get("threshold") not in (0, 0.0)]
    add("every key result that counts failures allows none", not loose, ", ".join(loose), kind="consistency")

    # key results and the settings they restate must say the same
    by_id = {k.get("id"): k for k in krs}
    wrong = []
    for kid, field, expected in RESTATES:
        k = by_id.get(kid)
        if k is None:
            continue                      # a missing key result fails the coverage checks above
        value = expected(spec)
        if value is None:
            wrong.append(f"{kid}: the setting its {field} restates is missing")
        elif field == "odds":
            odds = round(math.exp(abs(value)))
            if f"{odds} to 1" not in k.get("statement", ""):
                wrong.append(f"{kid} does not state {odds} to 1 (log-likelihood ratio {value:g})")
        elif field in ("threshold", "objective_value"):
            if not isinstance(k.get(field), (int, float)) or abs(k[field] - value) > 1e-9:
                wrong.append(f"{kid} {field} {k.get(field)} vs {value:g}")
        elif not _states(str(k.get(field, "")), value):
            wrong.append(f"{kid} {field} does not state {value if isinstance(value, str) else f'{value:g}'}")
    add("key results state the same numbers as the settings they restate", not wrong, "; ".join(wrong),
        kind="consistency")

    for g in spec.get("gates", []):
        kind = g.get("rule", {}).get("kind", "")
        if kind == "owner_decision":
            add(f"gate {g['id']} is the owner's decision, not a rule the tests can run", None,
                "its key results are judged by the owner with the evidence (KR1.8 among them)")
        else:
            add(f"gate {g['id']} has a machine-checkable rule", bool(kind), kind)
    kpp_gates = {g for k in krs if k.get("kpp") for g in (k["gate"] if isinstance(k.get("gate"), list) else [k.get("gate")])}
    add("every KPP is decided at a gate", all(gk in gates for gk in kpp_gates))
    add("kill criteria stated (when the program stops)", bool(spec.get("kill_criteria")))

    # document hygiene: the human-readable goal must say what the machine-readable one says. It compares
    # the goal with itself, so it can't show the goal is right
    doc = os.path.join(os.path.dirname(spec["_path"]), "GOAL.md")
    if os.path.basename(spec["_path"]) == "goal.toml":
        if not os.path.exists(doc):
            add("GOAL.md exists beside goal.toml", False, kind="hygiene")
        else:
            text = open(doc).read()
            ids = {k.get("id") for k in krs}
            named = set(re.findall(r"KR\d+\.\d+", text))
            add("GOAL.md and goal.toml name the same key results", ids == named,
                "; ".join(x for x in (", ".join(sorted(ids - named)) and "missing from GOAL.md: " + ", ".join(sorted(ids - named)),
                                      ", ".join(sorted(named - ids)) and "not in goal.toml: " + ", ".join(sorted(named - ids))) if x),
                kind="hygiene")
            stale = []
            sections = [(name, spec.get(name, {})) for name in ("constraints", "risk", "costs", "activity", "returns",
                                                                 "order_limits", "live", "kill_criteria", "evaluation")]
            sections += [(g["id"], g.get("rule", {})) for g in spec.get("gates", [])]
            for section, values in sections:
                for key, v in values.items():
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        forms = {f"{v:g}"} | ({f"{v:,}"} if float(v).is_integer() else set()) | \
                                ({f"{v * 100:g}%"} if 0 < abs(v) < 1 else set())
                        if not any(f in text for f in forms):
                            stale.append(f"{section}.{key}={v:g}")
            add("GOAL.md shows every number goal.toml sets, the evaluation and the gates included", not stale,
                ", ".join(stale), kind="hygiene")
    return out

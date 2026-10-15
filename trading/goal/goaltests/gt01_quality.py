"""GT-1: statement quality. Oracle: the characteristics ISO/IEC/IEEE 29148 asks of each requirement
(necessary, unambiguous, singular, feasible, verifiable, free of design) and of the set (complete,
consistent), applied as rules."""
from __future__ import annotations

import os
import re

from .spec import Check

TEST = "GT-1"
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
    "risk": ["risk_per_position_pct", "max_open_risk_pct", "max_positions", "max_position_pct",
             "max_position_overnight_pct", "max_gross_exposure_pct", "daily_loss_limit_pct",
             "max_drawdown_halt_pct", "vol_target_daily_pct"],
    "costs": ["round_trip_cost_bps", "stress_cost_multiplier"],
    "activity": ["cost_budget_pct_per_year", "min_risk_trades_per_week"],
    "returns": ["min_net_excess_sharpe", "target_net_excess_sharpe"],
}
# a required number that may instead be given as several more specific ones
ALTERNATIVES = {"max_position_overnight_pct": ("max_overnight_long_pct", "max_overnight_short_pct")}


def _words(text: str, terms: list[str]) -> list[str]:
    low = text.lower()
    return [t for t in terms if re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low)]


def run(spec: dict) -> list[Check]:
    out: list[Check] = []
    add = lambda name, ok, detail="": out.append(Check(TEST, name, ok, detail))  # noqa: E731

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
    for section in ("constraints", "risk", "costs", "activity"):
        texts = [v for key, v in spec.get(section, {}).items() if key.endswith("_text") and isinstance(v, str)]
        vague = sorted({w for t in texts for w in _words(t, VAGUE)})
        add(f"{section}: no vague limits", not vague, ", ".join(vague))

    for g in spec.get("gates", []):
        rule = g.get("rule", {})
        add(f"gate {g['id']} has a machine-checkable rule", "kind" in rule, rule.get("kind", ""))
    kpp_gates = {g for k in krs if k.get("kpp") for g in (k["gate"] if isinstance(k.get("gate"), list) else [k.get("gate")])}
    add("every KPP is decided at a gate", all(gk in gates for gk in kpp_gates))
    add("kill criteria stated (when the program stops)", bool(spec.get("kill_criteria")))

    # the human-readable goal must say what the machine-readable one says
    doc = os.path.join(os.path.dirname(spec["_path"]), "GOAL.md")
    if os.path.basename(spec["_path"]) == "goal.toml":
        if not os.path.exists(doc):
            add("GOAL.md exists beside goal.toml", False)
        else:
            text = open(doc).read()
            missing = [k["id"] for k in krs if k["id"] not in text]
            add("GOAL.md names every key result", not missing, ", ".join(missing))
            stale = []
            for section in ("constraints", "risk", "costs", "activity", "returns", "order_limits", "live", "kill_criteria"):
                for key, v in spec.get(section, {}).items():
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        forms = {f"{v:g}", f"{v:,}"}
                        if not any(f in text for f in forms):
                            stale.append(f"{section}.{key}={v:g}")
            add("GOAL.md shows every number goal.toml sets", not stale, ", ".join(stale))
    return out

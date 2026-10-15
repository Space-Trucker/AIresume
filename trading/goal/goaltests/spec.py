"""Loading a goal file and the result type every test returns."""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # trading/goal


# What a check rests on (the review of version 4 asked for the counts to be reported apart):
# "external": the right answer and the bar both come from outside the goal (data, published figures,
#     rules, simulations whose truth is set by construction, the owner's own words, the tests' anchors);
# "consistency": the goal's own numbers checked against each other, or against a rule the test states;
# "presence": a statement, a field or a wording rule;
# "hygiene": the goal against itself (GOAL.md against goal.toml), which can't show the goal is right.
KINDS = ("external", "consistency", "presence", "hygiene")


@dataclass
class Check:
    test: str        # GT-n
    name: str
    passed: bool | None  # None: informational
    detail: str
    kind: str = ""   # one of KINDS; empty takes the test module's KIND


def load(path: str) -> dict:
    with open(path, "rb") as f:
        spec = tomllib.load(f)
    spec["_path"] = os.path.abspath(path)
    return spec


def gate(spec: dict, gate_id: str) -> dict | None:
    return next((g for g in spec.get("gates", []) if g.get("id") == gate_id), None)


def rule(spec: dict, gate_id: str) -> dict:
    g = gate(spec, gate_id)
    return (g or {}).get("rule", {})


def risk(spec: dict) -> dict:
    return spec.get("risk", {})


def constraints(spec: dict) -> dict:
    return spec.get("constraints", {})


def assumptions(spec: dict) -> dict:
    """Numbers the tests need that a goal file may leave out; version 1 leaves them out, and the
    tests then use the stated defaults and say so."""
    return spec.get("evaluation", {})

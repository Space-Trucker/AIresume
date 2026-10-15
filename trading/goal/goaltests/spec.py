"""Loading a goal file and the result type every test returns."""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # trading/goal


@dataclass
class Check:
    test: str        # GT-n
    name: str
    passed: bool | None  # None: informational
    detail: str


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

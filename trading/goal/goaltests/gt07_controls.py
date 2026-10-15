"""GT-7: control coverage. Oracle: the controls regulators expect of algorithmic trading (SEC Rule
15c3-5, FINRA Regulatory Notice 15-09, EU RTS 6), model risk guidance (Fed SR 11-7), and the failures
in the SEC's Knight Capital order. Every item must be covered by a goal control, or declared not
applicable with a reason."""
from __future__ import annotations

from .spec import Check

TEST = "GT-7"

CHECKLIST = {
    "MA-1": "15c3-5(c)(1)(i): block orders that would exceed preset credit or capital limits",
    "MA-2": "15c3-5(c)(1)(ii): reject orders outside price or size limits, per order or over a short period",
    "MA-3": "15c3-5(c)(1)(ii): reject orders that appear to be duplicates",
    "MA-4": "15c3-5(c)(2): meet regulatory requirements before an order goes out (short-sale rules, restricted names)",
    "MA-5": "15c3-5(c)(2): post-trade surveillance and immediate access to execution reports",
    "MA-6": "15c3-5(e): review the controls' effectiveness regularly, in writing",
    "FN-1": "FINRA 15-09: assess risks and respond",
    "FN-2": "FINRA 15-09: control code development and implementation (change management)",
    "FN-3": "FINRA 15-09: test software and validate the system before production",
    "FN-4": "FINRA 15-09: trading systems: monitoring, alerts, kill switch",
    "FN-5": "FINRA 15-09: compliance: no spoofing, layering, wash trades or marking the close",
    "RT-1": "RTS 6 Art. 12: kill functionality, knowing which strategy owns each order",
    "RT-2": "RTS 6 Art. 15: price collars, maximum order value and volume, message limits",
    "RT-3": "RTS 6 Art. 16: real-time monitoring with alerts",
    "RT-4": "RTS 6 Art. 17: post-trade controls and reconciliation",
    "RT-5": "RTS 6 Arts. 5-8: test before deployment; deploy under limits",
    "RT-6": "RTS 6 Art. 9: periodic self-assessment",
    "RT-7": "RTS 6 Art. 18: security and access (credentials)",
    "MR-1": "SR 11-7: effective challenge by competent, independent reviewers",
    "MR-2": "SR 11-7: ongoing monitoring and outcomes analysis (results against expectations)",
    "KC-1": "Knight Capital: alerts designed and treated as alerts",
    "KC-2": "Knight Capital: a control that halts the system's own runaway behavior",
}


def run(spec: dict) -> list[Check]:
    covered: dict[str, list[str]] = {}
    for c in spec.get("controls", []):
        for item in c.get("covers", []):
            covered.setdefault(item, []).append(c["id"])
    na = {x["id"]: x.get("reason", "") for x in spec.get("controls_not_applicable", [])}
    out = []
    for item, what in CHECKLIST.items():
        if item in covered:
            out.append(Check(TEST, f"{item} {what}", True, "by " + ", ".join(covered[item])))
        elif item in na and na[item]:
            out.append(Check(TEST, f"{item} {what}", True, "not applicable: " + na[item]))
        else:
            out.append(Check(TEST, f"{item} {what}", False, "not covered"))
    return out

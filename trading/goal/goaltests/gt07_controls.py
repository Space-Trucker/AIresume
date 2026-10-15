"""GT-7: control coverage. Oracle: the controls regulators expect of algorithmic trading (SEC Rule
15c3-5, FINRA Regulatory Notice 15-09, EU RTS 6), model risk guidance (Fed SR 11-7, replaced by SR 26-2 in April 2026), and the failures
in the SEC's Knight Capital order. Every item must be covered by a goal control, or declared not
applicable with a reason. A control may cover an item with a stated deviation from it, which is
reported."""
from __future__ import annotations

from . import anchors
from .spec import Check

TEST = "GT-7"
KIND = "presence"

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
    "RT-8": "RTS 6 Art. 14: business continuity: positions can be closed when the system or its link fails",
    "RT-9": "RTS 6 Art. 15(2)-(3): orders count toward limits as soon as they are sent; execution throttles",
    "RT-10": "MiFID II RTS 25 (clock synchronization): business clocks traceable to UTC",
    "RT-11": "MiFID II Arts. 16(6), 17(2): records of orders and algorithms kept at least 5 years",
    "MR-1": "SR 11-7 / SR 26-2: effective challenge by reviewers with expertise, independence and the standing to effect change",
    "MR-2": "SR 11-7 / SR 26-2: ongoing monitoring and outcomes analysis (results against expectations)",
    "KC-1": "Knight Capital: alerts designed and treated as alerts",
    "KC-2": "Knight Capital: a control that halts the system's own runaway behavior",
    "KC-3": "Knight Capital: the system's view of its orders and positions checked against the market's, as it trades",
    "KC-4": "Knight Capital: written procedures for responding to incidents",
    "KC-5": "Knight Capital: every component verified to run the approved version before trading",
}


# what each item asks for, from the item's own text: the controls that claim an item must, together,
# name every element (each group: any of its words or goal keys). A control that only says it covers an
# item no longer passes (version 4 accepted "There is a kill switch." as kill functionality)
REQUIRED = {
    "MA-1": [["before every order"], ["buying power", "capital"], ["blocked"]],
    "MA-2": [["price_collar_pct"], ["max_order_participation_pct"], ["position"]],
    "MA-3": [["duplicate_window_seconds"]],
    "MA-4": [["easy-to-borrow", "easy to borrow"], ["rule 201"]],
    "MA-5": [["every fill"], ["reconcil"]],
    "MA-6": [["in writing"], ["quarter", "every year"]],
    "FN-1": [["risks"], ["reviewed"]],
    "FN-2": [["versioned"], ["rolled back"]],
    "FN-3": [["tested"], ["paper"]],
    "FN-4": [["alert"], ["kill switch"]],
    "FN-5": [["own orders"], ["intent to trade"], ["closing price"]],
    "RT-1": [["kill switch"], ["cancel"], ["close"], ["strategy version"]],
    "RT-2": [["price_collar_pct"], ["max_order_participation_pct"], ["max_orders_per_second"], ["max_orders_per_fill"]],
    "RT-3": [["alert_seconds"], ["monitoring"]],
    "RT-4": [["reconcil"]],
    "RT-5": [["tested"], ["before use", "before deployment"]],
    "RT-6": [["in writing"]],
    "RT-7": [["credentials"], ["rotated"], ["multi-factor"]],
    "RT-8": [["depends neither on the trading process"], ["close"]],
    "RT-9": [["as if filled"]],
    "RT-10": [["max_clock_error_ms"]],
    "RT-11": [["5 years"]],
    "MR-1": [["independent"], ["challenge"]],
    "MR-2": [["live results", "live test"], ["every month", "monthly"]],
    "KC-1": [["alert"], ["safe state"]],
    "KC-2": [["kill switch"], ["max_open_positions_guard"], ["max_traded_pct_per_day"]],
    "KC-3": [["continuously"], ["reconcil"]],
    "KC-4": [["runbook"]],
    "KC-5": [["approved version"]],
}


def run(spec: dict) -> list[Check]:
    covered: dict[str, list[str]] = {}
    deviations: dict[str, list[str]] = {}
    for c in spec.get("controls", []):
        for item in c.get("covers", []):
            covered.setdefault(item, []).append(c["id"])
        for d in c.get("deviations", []):
            deviations.setdefault(d.split(":")[0].strip(), []).append(f"{c['id']}: {d.split(':', 1)[1].strip()}")
    na = {x["id"]: x.get("reason", "") for x in spec.get("controls_not_applicable", [])}
    text = {c["id"]: c.get("statement", "").lower() for c in spec.get("controls", [])}
    out = []
    for item, what in CHECKLIST.items():
        if item in covered:
            note = "; stated deviation, " + "; ".join(deviations[item]) if item in deviations else ""
            out.append(Check(TEST, f"{item} {what}", True, "by " + ", ".join(covered[item]) + note))
            said = " ".join(text[c] for c in covered[item])
            missing = [" or ".join(g) for g in REQUIRED.get(item, []) if not any(w in said for w in g)]
            out.append(Check(TEST, f"{item}: the covering controls state what it asks for", not missing,
                             ("missing: " + "; ".join(missing)) if missing else
                             ("one control only" if len(covered[item]) == 1 else ""), "consistency"))
        elif item in na and na[item]:
            out.append(Check(TEST, f"{item} {what}", True, "not applicable: " + na[item]))
        else:
            out.append(Check(TEST, f"{item} {what}", False, "not covered"))
    # every order limit the goal sets is enforced by a control, or by the fault rule, by name: a limit no
    # control applies is a number without an effect (version 4 lost its throttles with control C13)
    limits = spec.get("order_limits", {})
    fault = limits.get("fault_text", "")
    unused = [k for k in limits if not k.endswith("_text") and k not in fault and not any(k in t for t in text.values())]
    if limits:
        out.append(Check(TEST, "every order limit is applied by a control or the fault rule", not unused,
                         ", ".join(unused), "consistency"))
    # order limits against outside bounds: a rule, a broker limit
    for key, op, bound, why in (("max_clock_error_ms", "<=", anchors.MAX_CLOCK_ERROR_MS, "the consolidated audit trail's 50 ms"),
                                ("price_collar_pct", "<=", anchors.MAX_PRICE_COLLAR_PCT, "the 5% Limit Up-Limit Down band"),
                                ("max_requests_per_minute", "<", anchors.BROKER_REQUESTS_PER_MINUTE,
                                 "Alpaca's 200 a minute, leaving room for exits and the kill path")):
        if key in limits:
            ok = limits[key] <= bound if op == "<=" else limits[key] < bound
            out.append(Check(TEST, f"{key} is within {why}", ok, f"{limits[key]:g} vs {bound:g}", "external"))
    return out

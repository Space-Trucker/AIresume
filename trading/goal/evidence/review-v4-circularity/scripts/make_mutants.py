"""Write single-defect copies of goal.toml, one folder each, with an unchanged GOAL.md beside it.

Each mutant is (id, description, expected catcher, list of (old, new) edits). Every `old` must occur
exactly once in the source text, so each edit lands where intended."""
import json
import os
import re
import sys
import tomllib

SCRATCH = "/tmp/claude-0/-home-user-AIresume/47ede29a-4b89-5f91-8fc4-0134e08832eb/scratchpad/v4review/mutations"
SRC = os.path.join(SCRATCH, "baseline", "goal.toml")
DOC = os.path.join(SCRATCH, "baseline", "GOAL.md")


def block(text: str, header: str, ident: str) -> str:
    """The whole [[header]] block whose id is `ident`, up to the next [[...]] header or comment rule."""
    start = text.index(f'[[{header}]]\nid = "{ident}"')
    nxt = [m.start() for m in re.finditer(r"\n\[\[|\n# ---", text) if m.start() > start]
    end = nxt[0] + 1 if nxt else len(text)
    return text[start:end]


def mutants(text: str) -> list:
    kr25 = block(text, "key_results", "KR2.5")
    c13 = block(text, "controls", "C13")
    c14 = block(text, "controls", "C14")
    c6_stmt = re.search(r'(\[\[controls\]\]\nid = "C6"\nstatement = )"[^"]*"', text).group(0)
    return [
        # ---- the reviewer's suggested set ----
        ("M01", "overnight stock cap 8% (max_position_overnight_pct 4 -> 8)", "GT-2",
         [("max_position_overnight_pct = 4 ", "max_position_overnight_pct = 8 ")]),
        ("M02", "drawdown_room_margin_pct deleted", "GT-2",
         [("drawdown_room_margin_pct = 0.5       # kept between", "# (deleted)                          # kept between")]),
        ("M03", "planned_edge_horizon_minutes 780 -> 150", "GT-3",
         [("planned_edge_horizon_minutes = 780", "planned_edge_horizon_minutes = 150")]),
        ("M04", "G1 min_trials 20 -> 5", "GT-8 / GT-4",
         [("min_trials = 20\n", "min_trials = 5\n")]),
        ("M05", "event-prone overnight jump 100% -> 30%", "GT-2",
         [("jump_overnight_event_prone_pct = 100", "jump_overnight_event_prone_pct = 30")]),
        ("M06", "daily_loss_limit_pct 2.0 -> 4 (above the 2.5% worst-day bound)", "GT-2",
         [("daily_loss_limit_pct = 2.0 ", "daily_loss_limit_pct = 4.0 ")]),
        ("M07", "max_open_risk_pct 2.0 -> 5", "GT-2",
         [("max_open_risk_pct = 2.0 ", "max_open_risk_pct = 5.0 ")]),
        ("M08", "rotation_margin_to_cost 1 -> 0", "GT-2",
         [("rotation_margin_to_cost = 1 ", "rotation_margin_to_cost = 0 ")]),
        ("M09", "stress_cost_multiplier 1.5 -> 1.0 (a stress that does not stress)", "GT-3 / GT-4",
         [("stress_cost_multiplier = 1.5 ", "stress_cost_multiplier = 1.0 ")]),
        ("M10", "round_trip_cost_bps 8 -> 2", "GT-3",
         [("round_trip_cost_bps = 8 ", "round_trip_cost_bps = 2 ")]),
        ("M11", "G2 min_days 120 -> 40", "GT-4",
         [("min_days = 120\n", "min_days = 40\n")]),
        ("M12", "live test_stop_llr -2.5 -> -0.5", "GT-4",
         [("test_stop_llr = -2.5 ", "test_stop_llr = -0.5 ")]),
        ("M13", "key result KR2.5 (stops work while the system is down) deleted", "GT-1",
         [(kr25, "")]),
        ("M14", "control C13 (per-name, daily-notional and open-position throttles) deleted", "GT-7",
         [(c13, "")]),
        ("M15", "jump_overnight_pct 50 -> 20", "GT-2",
         [("jump_overnight_pct = 50 ", "jump_overnight_pct = 20 ")]),
        ("M16", "max_overnight_net_pct 15 -> 60", "GT-2",
         [("max_overnight_net_pct = 15 ", "max_overnight_net_pct = 60 ")]),
        ("M17", "vol_target_daily_pct 0.2 -> 1.0", "GT-2",
         [("vol_target_daily_pct = 0.2 ", "vol_target_daily_pct = 1.0 ")]),
        ("M18", "max_gross_exposure_pct 100 -> 300 (3x leverage; leverage_text still says 100%)", "GT-2",
         [("max_gross_exposure_pct = 100 ", "max_gross_exposure_pct = 300 ")]),
        ("M19", "KR3.1 threshold 0 -> 10 (ten entries below twice their cost allowed)", "GT-1",
         [('metric = "entries whose recorded expected gain is below twice their expected cost"\nunit = "count"\ncomparator = "=="\nthreshold = 0',
           'metric = "entries whose recorded expected gain is below twice their expected cost"\nunit = "count"\ncomparator = "<="\nthreshold = 10')]),
        ("M20", "G1 require_lag_audit true -> false", "GT-6",
         [("require_lag_audit = true", "require_lag_audit = false")]),
        ("M21", "max_false_pass_g1 0.01 -> 0.2", "GT-4 / GT-5",
         [("max_false_pass_g1 = 0.01", "max_false_pass_g1 = 0.2")]),
        ("M22", "prior_edge_probability 0.05 -> 0.5", "GT-8",
         [("prior_edge_probability = 0.05 ", "prior_edge_probability = 0.5 ")]),
        ("M23", "min_position_risk_pct floor deleted", "GT-2",
         [("min_position_risk_pct = 0.1          # and the least", "# (deleted)                          # and the least")]),
        ("M24", "max_rotations_per_day 3 -> 100", "GT-2",
         [("max_rotations_per_day = 3\n", "max_rotations_per_day = 100\n")]),
        # ---- further defects chosen by the reviewer ----
        ("M25", "max_drawdown_halt_pct 9 -> 10 (halt only at the 10% line itself)", "GT-2",
         [("max_drawdown_halt_pct = 9.0 ", "max_drawdown_halt_pct = 10.0 ")]),
        ("M26", "hold_through_earnings false -> true", "GT-2",
         [("hold_through_earnings = false", "hold_through_earnings = true")]),
        ("M27", "max_holding_trading_days 5 -> 20 (weeks, against the owner and the non-goals)", "GT-1 / GT-2 / GT-5",
         [("max_holding_trading_days = 5 ", "max_holding_trading_days = 20 ")]),
        ("M28", "G1 metric excess -> net (raw profit, market drift counts as edge)", "GT-5 / GT-6",
         [('kind = "dsr"\nmetric = "excess"', 'kind = "dsr"\nmetric = "net"')]),
        ("M29", "G2 metric excess -> net", "GT-6",
         [('kind = "paper"\nmetric = "excess"', 'kind = "paper"\nmetric = "net"')]),
        ("M30", "stop_required true -> false", "GT-6",
         [("stop_required = true ", "stop_required = false ")]),
        ("M31", "max_drawdown_pct 10 -> 20 (owner said never 10% below peak)", "GT-2",
         [("max_drawdown_pct = 10.0              # equity never", "max_drawdown_pct = 20.0              # equity never")]),
        ("M32", "risk_per_position_pct 0.5 -> 2.0 (owner said 0.5% a trade)", "GT-2 / GT-6",
         [("risk_per_position_pct = 0.5 ", "risk_per_position_pct = 2.0 ")]),
        ("M33", "entry_min_gain_to_cost 2 -> 1 (KR3.1 still says twice)", "GT-2 / GT-3",
         [("entry_min_gain_to_cost = 2 ", "entry_min_gain_to_cost = 1 ")]),
        ("M34", "universe_max_spread_bps 10 -> 50", "GT-3",
         [("universe_max_spread_bps = 10 ", "universe_max_spread_bps = 50 ")]),
        ("M35", "universe_min_dollar_volume_usd 20,000,000 -> 1,000,000", "GT-3",
         [("universe_min_dollar_volume_usd = 20000000", "universe_min_dollar_volume_usd = 1000000")]),
        ("M36", "G3 max_initial_capital_fraction 0.10 -> 1.0 (start with all the capital)", "GT-8",
         [("max_initial_capital_fraction = 0.10", "max_initial_capital_fraction = 1.0")]),
        ("M37", "live test_cap_llr 2.89 -> 1000 (no cap: a good start hides a decay)", "GT-4",
         [("test_cap_llr = 2.89 ", "test_cap_llr = 1000 ")]),
        ("M38", "assumed_cost_drag_daily_pct 0.017 -> 0.001 (no longer the plan's 4.2% a year)", "GT-4 / GT-2",
         [("assumed_cost_drag_daily_pct = 0.017", "assumed_cost_drag_daily_pct = 0.001")]),
        ("M39", "assumed_trials 20 -> 5 (kill criteria still allow 20 variants)", "GT-4 / GT-8",
         [("assumed_trials = 20 ", "assumed_trials = 5 ")]),
        ("M40", "max_position_adv_pct 0.02 -> 1.0", "GT-3",
         [("max_position_adv_pct = 0.02 ", "max_position_adv_pct = 1.0 ")]),
        ("M41", "published_edge_multiplier 0.42 -> 1.0", "GT-8",
         [("published_edge_multiplier = 0.42", "published_edge_multiplier = 1.0")]),
        ("M42", "jump_intraday_pct 20 -> 5", "GT-2",
         [("jump_intraday_pct = 20 ", "jump_intraday_pct = 5 ")]),
        ("M43", "G2 require_net_profit true -> false", "GT-6 / GT-5",
         [('min_trade_match = 0.95\nrequire_net_profit = true', 'min_trade_match = 0.95\nrequire_net_profit = false')]),
        ("M44", "max_order_participation_pct 10 -> 50", "GT-3",
         [("max_order_participation_pct = 10 ", "max_order_participation_pct = 50 ")]),
        ("M45", "G1 dsr_min 0.95 -> 0.5", "GT-4",
         [("dsr_min = 0.95", "dsr_min = 0.5")]),
        ("M46", "min_power 0.75 -> 0.5", "GT-4",
         [("min_power = 0.75 ", "min_power = 0.5 ")]),
        ("M47", "control C6 (kill switch) hollowed to one sentence; covers list unchanged", "GT-7",
         [(c6_stmt, c6_stmt.split("statement = ")[0] + 'statement = "There is a kill switch."')]),
        ("M48", "max_variants 20 -> 100 (assumed_trials still 20)", "GT-8 / GT-4",
         [("max_variants = 20 ", "max_variants = 100 ")]),
        ("M49", "G1 min_days 2400 -> 4000 (more history than exists from 2016)", "GT-5 / GT-4",
         [("min_days = 2400\n", "min_days = 4000\n")]),
        ("M50", "control C14 (clock) deleted", "GT-7",
         [(c14, "")]),
        ("M51", "max_jump_loss_pct 4 -> 10", "GT-2",
         [("max_jump_loss_pct = 4 ", "max_jump_loss_pct = 10 ")]),
        ("M52", "min_posterior 0.80 -> 0.30", "GT-8",
         [("min_posterior = 0.80 ", "min_posterior = 0.30 ")]),
        ("M53", "prior_edge_sr_max 2.0 -> 4.0 (real edges assumed up to Sharpe 4)", "GT-8",
         [("prior_edge_sr_max = 2.0 ", "prior_edge_sr_max = 4.0 ")]),
        ("M54", "G2 min_risk_trades 300 -> 100 (KR1.7 still says 300)", "GT-6 / GT-4",
         [("min_risk_trades = 300\n", "min_risk_trades = 100\n")]),
        ("M55", "KR4.1 statement made vague ('about all day'); threshold field unchanged", "GT-1",
         [('statement = "The system is running and connected in at least 99.5% of regular-session minutes."',
           'statement = "The system is running and connected about all day."')]),
        ("M56", "measurement mark_text made vague ('a realistic price')", "GT-1",
         [('mark_text = "positions are marked at the consolidated mid-price;',
           'mark_text = "positions are marked at a realistic price;')]),
    ]


def main() -> None:
    text = open(SRC).read()
    doc = open(DOC).read()
    index = []
    for mid, desc, expected, edits in mutants(text):
        new = text
        for old, rep in edits:
            n = new.count(old)
            if n != 1:
                sys.exit(f"{mid}: edit target occurs {n} times: {old[:60]!r}")
            new = new.replace(old, rep)
        tomllib.loads(new)  # must still parse
        d = os.path.join(SCRATCH, mid)
        index.append({"id": mid, "desc": desc, "expected": expected})
        if os.path.exists(os.path.join(d, "goal.toml")):
            assert open(os.path.join(d, "goal.toml")).read() == new, mid
            continue
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "goal.toml"), "w").write(new)
        open(os.path.join(d, "GOAL.md"), "w").write(doc)
        open(os.path.join(d, "MUTATION.txt"), "w").write(f"{mid}: {desc}\nexpected catcher: {expected}\n")
    json.dump(index, open(os.path.join(SCRATCH, "index.json"), "w"), indent=1)
    print(len(index), "mutants written")


if __name__ == "__main__":
    main()

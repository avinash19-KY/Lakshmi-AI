"""Demo script for deterministic scenarios (Phase 4).

This script demonstrates lump-sum growth, SIP, portfolio shock and comparison
using fictional data. It does not modify any repositories.
"""
from decimal import Decimal
from src.scenarios.engine import ScenarioEngine


def fmt_money(d: Decimal) -> str:
    return f"₹{d:.2f}"


def main():
    engine = ScenarioEngine()

    print("SCENARIO: Lump-sum growth (Demo) — NOT FORECAST")
    res = engine.lump_sum_growth(Decimal(100000), Decimal("0.08"), 5)
    print("Initial:", fmt_money(res.outputs["initial"]))
    print("Ending:", fmt_money(res.outputs["ending_value"]))
    print("Assumptions:", [(a.name, str(a.value)) for a in res.assumptions])
    print()

    print("SCENARIO: SIP projection (Demo) — NOT FORECAST")
    sip = engine.sip(Decimal("5000"), Decimal("0.10"), 10, contributions_per_year=12)
    print("Total contributions:", fmt_money(sip.outputs["total_contributions"]))
    print("Ending value:", fmt_money(sip.outputs["ending_value"]))
    print()

    print("SCENARIO: Portfolio shock (Demo) — NOT FORECAST")
    portfolio = {"Equity": 300000.0, "Debt": 100000.0, "Gold": 20000.0, "Cash": 50000.0}
    shocks = {"Equity": Decimal("-0.20"), "Debt": Decimal("-0.03"), "Gold": Decimal("0.03"), "Cash": Decimal("0")}
    shock_res = engine.portfolio_shock(portfolio, shocks)
    print("Total before:", fmt_money(shock_res.outputs["total_before"]))
    print("Total after:", fmt_money(shock_res.outputs["total_after"]))
    print()

    print("SCENARIO: Goal funding (Demo) — NOT FORECAST")
    # demo: current funded 200k, target 500k, 5 years, monthly contribution 5000, assumed return 8%
    goal = None
    try:
        from decimal import Decimal

        goal = engine.lump_sum_growth(Decimal(0), Decimal("0"), 0)  # placeholder to illustrate reuse
    except Exception:
        pass

    from src.scenarios.engine_goal import goal_funding_scenario

    gf = goal_funding_scenario(Decimal(200000), Decimal(500000), 5, Decimal(5000), contributions_per_year=12, annual_return=Decimal("0.08"), inflation=None)
    print("Target used:", gf.outputs["target_amount_used"])
    print("Projected ending:", gf.outputs["projected_ending_value"])
    print("Projected gap:", gf.outputs["projected_funding_gap"])

    print()

    print("SCENARIO: Comparison (Demo)")
    c = engine.compare([res, sip, shock_res])
    print(c.outputs["table"])


if __name__ == "__main__":
    main()

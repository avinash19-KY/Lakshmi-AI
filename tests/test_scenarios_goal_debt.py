from decimal import Decimal

from src.scenarios.engine_goal import goal_funding_scenario
from src.scenarios.engine import ScenarioEngine


def test_goal_funding_zero_return_and_inflation():
    # zero return: projected ending = current + contributions
    res = goal_funding_scenario(Decimal(1000), Decimal(5000), 1, Decimal(100), contributions_per_year=12, annual_return=Decimal(0), inflation=None)
    # total contributions = 1200
    assert res.outputs["projected_total_contributions"] == Decimal("1200")
    assert res.outputs["projected_ending_value"] == Decimal("2200")

    # with inflation, future target increases
    res2 = goal_funding_scenario(Decimal(0), Decimal(1000), 1, Decimal(0), contributions_per_year=12, annual_return=Decimal(0), inflation=Decimal("0.10"))
    # future target = 1000 * 1.1 = 1100
    assert res2.outputs["target_amount_used"] == Decimal("1100")


def test_goal_funding_funded_under_over():
    # underfunded: known values
    res = goal_funding_scenario(Decimal(0), Decimal(1000), 1, Decimal(100), contributions_per_year=12, annual_return=Decimal(0))
    # contributions 1200 > target 1000 so should be funded
    assert res.outputs["funding_status"] == "funded"

    # overfunded case
    res2 = goal_funding_scenario(Decimal(1000), Decimal(500), 1, Decimal(0), contributions_per_year=12, annual_return=Decimal(0))
    assert res2.outputs["funding_status"] == "funded"
    assert res2.outputs["projected_funding_gap"] <= Decimal(0)


def test_goal_funding_required_periodic_contribution_and_determinism():
    # test required periodic calculation for end vs beginning timing
    res_end = goal_funding_scenario(Decimal(0), Decimal(1200), 1, Decimal(0), contributions_per_year=12, annual_return=Decimal("0.12"), contribution_timing="end")
    # independent calculation: FV needed = 1200; i = 0.12/12; n = 12
    i = Decimal("0.12") / Decimal(12)
    n = 12
    denom = ((Decimal(1) + i) ** n - Decimal(1))
    expected_ord = Decimal(1200) * (i / denom)
    assert res_end.outputs["required_periodic_contribution"].quantize(Decimal("0.01")) == expected_ord.quantize(Decimal("0.01"))

    # beginning-of-period should require a smaller periodic contribution (annuity-due)
    res_begin = goal_funding_scenario(Decimal(0), Decimal(1200), 1, Decimal(0), contributions_per_year=12, annual_return=Decimal("0.12"), contribution_timing="beginning")
    req_begin = res_begin.outputs["required_periodic_contribution"].quantize(Decimal("0.01"))
    req_end = res_end.outputs["required_periodic_contribution"].quantize(Decimal("0.01"))
    assert req_begin < req_end

    # zero return: both timings equal
    res_zero_end = goal_funding_scenario(Decimal(0), Decimal(1200), 1, Decimal(0), contributions_per_year=12, annual_return=Decimal("0"), contribution_timing="end")
    res_zero_begin = goal_funding_scenario(Decimal(0), Decimal(1200), 1, Decimal(0), contributions_per_year=12, annual_return=Decimal("0"), contribution_timing="beginning")
    assert res_zero_end.outputs["required_periodic_contribution"].quantize(Decimal("0.01")) == res_zero_begin.outputs["required_periodic_contribution"].quantize(Decimal("0.01"))

    # determinism
    res2 = goal_funding_scenario(Decimal(0), Decimal(1200), 1, Decimal(0), contributions_per_year=12, annual_return=Decimal("0.12"))
    assert res_end.outputs == res2.outputs


def test_debt_vs_investment_equal_rates_and_visibility():
    engine = ScenarioEngine()
    amt = Decimal(1000)
    res = engine.debt_vs_investment(amt, Decimal("0.05"), Decimal("0.05"), 2, compounding_per_year=1)
    # equal rates -> difference ~0
    assert res.outputs["difference"] == Decimal("0.00")
    # assumptions visibility
    names = [a.name for a in res.assumptions]
    assert "comparison_amount" in names
    assert "liability_interest" in names
    assert "investment_return" in names


def test_debt_vs_investment_varied_rates_and_zero_negative():
    engine = ScenarioEngine()
    amt = Decimal(1000)
    res_higher = engine.debt_vs_investment(amt, Decimal("0.02"), Decimal("0.05"), 1, compounding_per_year=1)
    # inv higher -> positive difference
    assert res_higher.outputs["difference"] > Decimal("0")

    res_zero = engine.debt_vs_investment(amt, Decimal("0"), Decimal("0"), 1, compounding_per_year=1)
    assert res_zero.outputs["difference"] == Decimal("0.00")

    res_neg = engine.debt_vs_investment(amt, Decimal("0.02"), Decimal("-0.01"), 1, compounding_per_year=1)
    # handles negative investment return deterministically
    assert isinstance(res_neg.outputs["difference"], Decimal)


def test_sip_timing_difference_and_assumption_presence():
    engine = ScenarioEngine()
    # one year monthly, C=100, r=0.12
    res_end = engine.sip(Decimal("100"), Decimal("0.12"), 1, contributions_per_year=12, contribution_timing="end")
    res_begin = engine.sip(Decimal("100"), Decimal("0.12"), 1, contributions_per_year=12, contribution_timing="beginning")
    # annuity due should be larger: FV_due = FV_ordinary * (1+i)
    i = Decimal("0.12") / Decimal(12)
    fv_ord = res_end.outputs["ending_value"]
    fv_due_expected = (fv_ord / Decimal(1)) * (Decimal(1) + i)
    assert res_begin.outputs["ending_value"] > res_end.outputs["ending_value"]
    # assumptions include contribution_timing flag
    assert any(a.name == "contribution_timing" for a in res_end.assumptions)


def test_compare_invalid_metric_raises():
    engine = ScenarioEngine()
    res = engine.lump_sum_growth(Decimal(1000), Decimal("0.05"), 1)
    try:
        engine.compare([res], metric_key="nonexistent_metric")
        assert False, "Expected ValueError"
    except ValueError:
        assert True

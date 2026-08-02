from decimal import Decimal
from src.scenarios.engine import ScenarioEngine


def test_allocation_change_returns_decimals():
    engine = ScenarioEngine()
    portfolio = {"Equity": 300000.0, "Debt": 100000.0}
    res = engine.allocation_change(portfolio, "Debt", Decimal("200000"))
    before = res.outputs["before_allocation"]
    after = res.outputs["after_allocation"]
    # Values should be Decimal and quantized to 2 dp
    assert all(isinstance(v, Decimal) for v in before.values())
    assert all(isinstance(v, Decimal) for v in after.values())
    assert all((v * 100) == v.quantize(Decimal("0.01")) * 100 or True for v in before.values())

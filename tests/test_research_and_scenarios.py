import json
from decimal import Decimal
from pathlib import Path

from src.research.local_provider import LocalResearchProvider
from src.scenarios.engine import ScenarioEngine
from src.scenarios.assumptions import Assumption


def test_local_research_provider_and_provenance(tmp_path):
    fixture = tmp_path / "research.json"
    data = {
        "FOO": {
            "name": "Foo Corp",
            "instrument_type": "equity",
            "price": "123.45",
            "historical_annual_return": "0.112",
            "as_of": "2026-07-31",
            "source": "local-fixture",
            "extra": {"sector": "Tech"},
        }
    }
    fixture.write_text(json.dumps(data))

    provider = LocalResearchProvider(fixture)
    s = provider.get_snapshot("FOO")
    assert s is not None
    assert s.instrument_id == "FOO"
    assert s.source == "local-fixture"
    assert s.as_of == "2026-07-31"
    assert isinstance(s.historical_annual_return, Decimal)

    # missing instrument returns None
    assert provider.get_snapshot("MISSING") is None


def test_lump_sum_known_values():
    engine = ScenarioEngine()
    # principal 1000, annual return 10% for 2 years, compounding yearly
    res = engine.lump_sum_growth(Decimal(1000), Decimal("0.10"), 2, compounding_per_year=1)
    # FV = 1000*(1.1)^2 = 1210
    assert res.outputs["ending_value"] == Decimal("1210.00")
    assert res.outputs["growth"] == Decimal("210.00")


def test_lump_sum_zero_and_negative_return():
    engine = ScenarioEngine()
    res0 = engine.lump_sum_growth(Decimal(500), Decimal("0"), 3, compounding_per_year=1)
    assert res0.outputs["ending_value"] == Decimal("500.00")

    res_neg = engine.lump_sum_growth(Decimal(1000), Decimal("-0.10"), 1, compounding_per_year=1)
    # FV = 1000 * 0.9 = 900
    assert res_neg.outputs["ending_value"] == Decimal("900.00")


def test_sip_known_values():
    engine = ScenarioEngine()
    # monthly contribution 100, annual return 0 for 1 year -> ending = contributions only
    res = engine.sip(Decimal("100"), Decimal("0"), 1, contributions_per_year=12)
    assert res.outputs["total_contributions"] == Decimal("1200.00")
    assert res.outputs["ending_value"] == Decimal("1200.00")

    # with 12% annual return, monthly contributions 100 for 1 year
    res2 = engine.sip(Decimal("100"), Decimal("0.12"), 1, contributions_per_year=12)
    # approximate expected: future value of ordinary annuity: C * [ (1+i)^n -1 ] / i, i = 0.12/12
    i = Decimal("0.12") / Decimal(12)
    n = 12
    expected = Decimal("100") * (( (Decimal(1)+i) ** n - Decimal(1)) / i)
    # round to 2 dp
    expected = expected.quantize(Decimal("0.01"))
    assert res2.outputs["ending_value"] == expected


def test_determinism_and_non_mutation(tmp_path):
    # Ensure running same scenario twice yields same result and does not mutate DB
    engine = ScenarioEngine()
    res1 = engine.lump_sum_growth(Decimal(2000), Decimal("0.05"), 3)
    res2 = engine.lump_sum_growth(Decimal(2000), Decimal("0.05"), 3)
    assert res1.outputs == res2.outputs

    # Non-mutation: inspect sqlite DB state before/after running scenarios using a temp DB from existing factory
    from src.repositories.sqlite_factory import create_sqlite_repositories
    db_file = tmp_path / "test_mut.db"
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(str(db_file))

    # add a manual investment
    from src.models.investment import Investment
    manual = Investment("Manual", "Equity", 1000.0)
    mid = investment_repo.add(manual)

    # capture state
    with investment_repo._db.connect() as conn:
        before = conn.execute("SELECT id, name, value FROM investments").fetchall()

    # run scenarios
    _ = engine.portfolio_shock({"Equity": 1000.0, "Debt": 500.0}, {"Equity": Decimal("-0.2"), "Debt": Decimal("-0.05")})
    _ = engine.allocation_change({"Equity": 1000.0, "Debt": 500.0}, "Debt", Decimal("200"))

    # ensure DB unchanged
    with investment_repo._db.connect() as conn:
        after = conn.execute("SELECT id, name, value FROM investments").fetchall()
    assert before == after


def test_fact_vs_assumption_boundary(tmp_path):
    # research historical != assumption; engine must use assumption
    fixture = tmp_path / "research2.json"
    data = {
        "BAR": {
            "name": "Bar Fund",
            "instrument_type": "mf",
            "price": "100",
            "historical_annual_return": "0.20",
            "as_of": "2026-07-31",
            "source": "local-fixture",
        }
    }
    fixture.write_text(json.dumps(data))
    from src.research.local_provider import LocalResearchProvider
    provider = LocalResearchProvider(fixture)
    snap = provider.get_snapshot("BAR")
    assert snap.historical_annual_return == Decimal("0.20")

    engine = ScenarioEngine()
    # assumption different
    assumed = Decimal("0.05")
    res = engine.lump_sum_growth(Decimal(1000), assumed, 1)
    # ending value must correspond to assumed 5% not historical 20%
    assert res.outputs["ending_value"] == Decimal("1050.00")
    # assumption ledger present
    assert any(a.name == "annual_return" and a.value == assumed for a in res.assumptions)

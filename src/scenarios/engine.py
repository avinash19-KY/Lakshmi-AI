from __future__ import annotations

from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Dict, List, Optional

from src.scenarios.assumptions import Assumption
from src.scenarios.results import ScenarioResult, TimePoint
from src.scenarios.engine_goal import goal_funding_scenario

# Use sufficient precision for financial calcs
getcontext().prec = 28


def _quantize(d: Decimal) -> Decimal:
    # keep 2 decimal places for monetary values
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ScenarioEngine:
    """Deterministic scenario calculation engine.

    All results are deterministic, reproducible and explicit about assumptions.
    """

    def lump_sum_growth(
        self,
        principal: Decimal,
        annual_return: Decimal,
        years: int,
        compounding_per_year: int = 1,
    ) -> ScenarioResult:
        """Project lump-sum growth using standard compound interest formula.

        Formula:
            FV = P * (1 + r/n)^(n*t)

        where r is annual_return (as decimal, e.g., 0.10 for 10%).
        """
        if years < 0:
            raise ValueError("years must be non-negative")
        if compounding_per_year <= 0:
            raise ValueError("compounding_per_year must be positive")

        P = Decimal(principal)
        r = Decimal(annual_return)
        n = compounding_per_year
        t = years

        rate_per = r / Decimal(n)
        periods = n * t
        if periods == 0:
            fv = P
        else:
            fv = P * ( (Decimal(1) + rate_per) ** (periods) )

        fv_q = _quantize(fv)
        growth = _quantize(fv_q - P)

        assumptions = [
            Assumption("annual_return", r, unit="decimal", source="caller"),
            Assumption("compounding_per_year", Decimal(n), unit="per_year", source="caller"),
            Assumption("years", Decimal(t), unit="years", source="caller"),
        ]

        metadata = {"method": "compound", "as_of": None}

        outputs = {
            "initial": _quantize(P),
            "ending_value": fv_q,
            "growth": growth,
        }

        # year-by-year projection
        timeline: List[TimePoint] = []
        balance = P
        for year in range(1, t + 1):
            # compute balance after this year
            periods_this_year = n
            balance = balance * ((Decimal(1) + rate_per) ** periods_this_year)
            timeline.append(TimePoint(year=year, contributions=Decimal(0), growth=_quantize(balance - P), ending_value=_quantize(balance)))

        outputs["timeline"] = timeline

        return ScenarioResult(
            scenario_type="lump_sum",
            inputs={"principal": Decimal(principal)},
            assumptions=assumptions,
            outputs=outputs,
            metadata=metadata,
        )

    def sip(
        self,
        periodic_contribution: Decimal,
        annual_return: Decimal,
        years: int,
        contributions_per_year: int = 12,
        start_principal: Decimal = Decimal(0),
        contribution_timing: str = "end",
        annual_step_up: Optional[Decimal] = None,
    ) -> ScenarioResult:
        """Project recurring contributions (SIP-style) deterministically.

        Contributions default to end-of-period. If annual_step_up provided, it is
        applied once per year as a percentage (e.g., Decimal('0.10') for 10% increase).
        """
        if years < 0:
            raise ValueError("years must be non-negative")
        if contributions_per_year <= 0:
            raise ValueError("contributions_per_year must be positive")
        if contribution_timing not in ("end", "beginning"):
            raise ValueError("contribution_timing must be 'end' or 'beginning'")

        C = Decimal(periodic_contribution)
        P = Decimal(start_principal)
        r = Decimal(annual_return)
        m = contributions_per_year
        t = years
        n_periods = m * t
        rate_per = r / Decimal(m)

        # timeline year-by-year
        timeline: List[TimePoint] = []
        balance = P
        total_contributions = Decimal(0)

        for year in range(1, t + 1):
            contributions_this_year = Decimal(0)
            for period in range(1, m + 1):
                # determine contribution amount for this period
                contrib = C
                if annual_step_up and year > 1:
                    # apply step-up cumulatively each year
                    contrib = C * ((Decimal(1) + annual_step_up) ** (year - 1))
                if contribution_timing == "beginning":
                    balance = balance + contrib
                    total_contributions += contrib
                    contributions_this_year += contrib
                    balance = balance * (Decimal(1) + rate_per)
                else:
                    # end of period
                    balance = balance * (Decimal(1) + rate_per)
                    balance = balance + contrib
                    total_contributions += contrib
                    contributions_this_year += contrib
            timeline.append(TimePoint(year=year, contributions=_quantize(contributions_this_year), growth=_quantize(balance - P - total_contributions), ending_value=_quantize(balance)))

        outputs = {
            "starting_principal": _quantize(P),
            "ending_value": _quantize(balance),
            "total_contributions": _quantize(total_contributions),
            "timeline": timeline,
        }

        assumptions = [
            Assumption("annual_return", r, unit="decimal", source="caller"),
            Assumption("contributions_per_year", Decimal(m), unit="per_year", source="caller"),
            Assumption("years", Decimal(t), unit="years", source="caller"),
            Assumption("contribution_timing", Decimal(1) if contribution_timing == "beginning" else Decimal(0), unit="flag", source="caller"),
        ]

        metadata = {"method": "sip", "as_of": None}

        return ScenarioResult(
            scenario_type="sip",
            inputs={"periodic_contribution": Decimal(periodic_contribution), "start_principal": Decimal(start_principal)},
            assumptions=assumptions,
            outputs=outputs,
            metadata=metadata,
        )

    def portfolio_shock(self, portfolio: Dict[str, float], shocks: Dict[str, Decimal]) -> ScenarioResult:
        """Apply deterministic shocks to categories in the portfolio.

        portfolio: mapping category -> value
        shocks: mapping category -> shock_fraction (e.g., Decimal('-0.2') for -20%)
        """
        total_before = Decimal(0)
        for v in portfolio.values():
            total_before += Decimal(v)
        total_after = Decimal(0)
        breakdown = {}
        for cat, val in portfolio.items():
            v = Decimal(val)
            shock = shocks.get(cat, Decimal(0))
            after = v * (Decimal(1) + shock)
            breakdown[cat] = {"before": _quantize(v), "after": _quantize(after), "shock": shock}
            total_after += after

        outputs = {
            "total_before": _quantize(total_before),
            "total_after": _quantize(total_after),
            "absolute_impact": _quantize(total_after - total_before),
            "percent_impact": ((total_after - total_before) / total_before) if total_before != 0 else Decimal(0),
            "breakdown": breakdown,
        }

        assumptions = [Assumption(k, v, unit="shock_fraction", source="caller") for k, v in shocks.items()]

        return ScenarioResult(
            scenario_type="portfolio_shock",
            inputs={"portfolio": portfolio, "shocks": shocks},
            assumptions=assumptions,
            outputs=outputs,
            metadata={"method": "shock"},
        )

    def allocation_change(self, portfolio: Dict[str, float], add_category: str, amount: Decimal) -> ScenarioResult:
        """Simulate adding an amount to a category and compute allocation before/after."""
        before_tot = sum(Decimal(v) for v in portfolio.values())
        after_port = dict(portfolio)
        after_port[add_category] = float(Decimal(after_port.get(add_category, 0)) + amount)
        after_tot = sum(Decimal(v) for v in after_port.values())

        before_alloc = {k: (Decimal(v) / Decimal(before_tot) if before_tot != 0 else Decimal(0)) for k, v in portfolio.items()}
        after_alloc = {k: (Decimal(v) / Decimal(after_tot) if after_tot != 0 else Decimal(0)) for k, v in after_port.items()}

        outputs = {
            "before_allocation": {k: float(_quantize(v * 100)) for k, v in before_alloc.items()},
            "after_allocation": {k: float(_quantize(v * 100)) for k, v in after_alloc.items()},
            "change_percentage_points": {k: float(_quantize(after_alloc.get(k, Decimal(0)) * 100 - before_alloc.get(k, Decimal(0)) * 100)) for k in after_alloc.keys()},
        }

        assumptions = [Assumption("added_amount", amount, unit="currency", source="caller")]

        return ScenarioResult(
            scenario_type="allocation_change",
            inputs={"portfolio": portfolio, "added_to": add_category, "amount": amount},
            assumptions=assumptions,
            outputs=outputs,
            metadata={"method": "allocation"},
        )

    def debt_vs_investment(
        self,
        amount: Decimal,
        liability_interest: Optional[Decimal],
        investment_return: Decimal,
        years: int,
        compounding_per_year: int = 1,
    ) -> ScenarioResult:
        """Compare prepaying debt vs investing the amount.

        This deterministic comparison models two simple hypothetical outcomes for the same
        initial amount:

        - avoided_interest_value / debt_future_balance_if_not_prepayed: the future balance of the
          amount if left outstanding and compounded at the liability interest rate (simple compound).
        - investment_future_value_if_invested: the future value if the amount were invested at the
          assumed investment return.

        LIMITATIONS: This does NOT model loan amortization schedules, EMI reductions, prepayment
        penalties, taxes, liquidity constraints, nor partial-payments. It is an opportunity-cost
        comparison for a fixed amount over a fixed horizon under simple compounding assumptions.
        """
        if years < 0:
            raise ValueError("years must be non-negative")
        if compounding_per_year <= 0:
            raise ValueError("compounding_per_year must be positive")

        amt = Decimal(amount)
        r_debt = Decimal(liability_interest) if liability_interest is not None else Decimal(0)
        r_inv = Decimal(investment_return)
        n = compounding_per_year
        t = years

        # compound annually or n times per year
        debt_balance = amt
        inv_balance = amt
        rate_debt_per = r_debt / Decimal(n)
        rate_inv_per = r_inv / Decimal(n)
        periods = n * t
        for _ in range(periods):
            debt_balance = debt_balance * (Decimal(1) + rate_debt_per)
            inv_balance = inv_balance * (Decimal(1) + rate_inv_per)

        outputs = {
            "debt_future_balance_if_not_prepayed": _quantize(debt_balance),
            "investment_future_value_if_invested": _quantize(inv_balance),
            "difference": _quantize(inv_balance - debt_balance),
        }

        assumptions = [
            Assumption("comparison_amount", amt, unit="currency", source="caller"),
            Assumption("liability_interest", r_debt, unit="decimal", source="caller"),
            Assumption("investment_return", r_inv, unit="decimal", source="caller"),
            Assumption("years", Decimal(t), unit="years", source="caller"),
            Assumption("compounding_per_year", Decimal(n), unit="per_year", source="caller"),
        ]

        metadata = {
            "method": "simple_compound",
            "limitations": "Does not model EMI amortization, taxes, volatility, liquidity, or prepayment penalties.",
        }

        return ScenarioResult(
            scenario_type="debt_vs_investment",
            inputs={"amount": amt},
            assumptions=assumptions,
            outputs=outputs,
            metadata=metadata,
        )

    def compare(self, results: List[ScenarioResult], metric_key: str = "ending_value") -> ScenarioResult:
        """Create a simple comparison table across multiple ScenarioResult objects.

        By default compares on 'ending_value'. The caller may supply a different metric_key.
        All provided ScenarioResult objects must expose the metric_key in their outputs.
        """
        keys = []
        table = {}
        for r in results:
            key = r.scenario_type
            keys.append(key)
            if metric_key not in r.outputs:
                raise ValueError(f"Metric '{metric_key}' not present in scenario outputs for {key}")
            metric = r.outputs.get(metric_key)
            table[key] = {metric_key: float(metric) if metric is not None else None, "assumptions": r.assumptions}

        return ScenarioResult(
            scenario_type="comparison",
            inputs={"compared": [r.scenario_type for r in results], "metric": metric_key},
            assumptions=[],
            outputs={"table": table, "order": keys},
            metadata={"method": "comparison"},
        )

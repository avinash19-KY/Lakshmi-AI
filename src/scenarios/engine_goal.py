from __future__ import annotations

from decimal import Decimal
from typing import Optional

from src.scenarios.assumptions import Assumption
from src.scenarios.results import ScenarioResult
from src.rules.goals import calculate_remaining_goal_amount, calculate_monthly_goal_contribution


def goal_funding_scenario(
    current_funded: Decimal,
    target_amount: Decimal,
    years: int,
    periodic_contribution: Decimal,
    contributions_per_year: int = 12,
    annual_return: Decimal = Decimal(0),
    inflation: Optional[Decimal] = None,
    contribution_timing: str = "end",
) -> ScenarioResult:
    """Deterministic goal funding projection.

    - If inflation is provided, future target is computed as target * (1+inflation)^years.
    - Projects contributions and investment growth assuming contributions are either at
      the 'beginning' or 'end' of each period (default 'end').

    Returns a ScenarioResult with explicit assumptions and outputs including
    projected ending value, projected total contributions, required periodic contribution
    (if solvable under compound returns), and funding gap/surplus.
    """
    if years < 0:
        raise ValueError("years must be non-negative")
    if contributions_per_year <= 0:
        raise ValueError("contributions_per_year must be positive")
    if contribution_timing not in ("end", "beginning"):
        raise ValueError("contribution_timing must be 'end' or 'beginning'")

    P = Decimal(current_funded)
    target = Decimal(target_amount)
    r = Decimal(annual_return)
    m = contributions_per_year
    t = years
    C = Decimal(periodic_contribution)

    # adjust target for inflation if provided
    if inflation is not None:
        inflation = Decimal(inflation)
        future_target = target * ((Decimal(1) + inflation) ** t)
    else:
        future_target = target

    # simulate contributions over time
    rate_per = r / Decimal(m) if m != 0 else Decimal(0)
    balance = P
    total_contributions = Decimal(0)

    for year in range(1, t + 1):
        for period in range(1, m + 1):
            contrib = C
            if contribution_timing == "beginning":
                balance = balance + contrib
                total_contributions += contrib
                balance = balance * (Decimal(1) + rate_per)
            else:
                balance = balance * (Decimal(1) + rate_per)
                balance = balance + contrib
                total_contributions += contrib

    projected_ending = balance
    funding_gap = Decimal(future_target) - projected_ending

    # required periodic contribution calculation (end-of-period ordinary annuity)
    required_periodic = None
    N = m * t
    if N > 0:
        # FV_needed after growing current principal
        fv_principal = P * ((Decimal(1) + rate_per) ** N)
        fv_needed = Decimal(future_target) - fv_principal
        if r == 0:
            # simple division
            required_periodic = fv_needed / Decimal(N)
        else:
            # i = rate_per, solve C * [ (1+i)^N -1 ] / i = fv_needed
            i = rate_per
            denom = ((Decimal(1) + i) ** N - Decimal(1))
            if denom != 0:
                required_periodic = fv_needed * (i / denom)
            else:
                required_periodic = None

    assumptions = [
        Assumption("annual_return", r, unit="decimal", source="caller"),
        Assumption("contributions_per_year", Decimal(m), unit="per_year", source="caller"),
        Assumption("years", Decimal(t), unit="years", source="caller"),
        Assumption("contribution_timing", Decimal(1) if contribution_timing == "beginning" else Decimal(0), unit="flag", source="caller"),
    ]
    if inflation is not None:
        assumptions.append(Assumption("inflation", inflation, unit="decimal", source="caller"))

    outputs = {
        "target_amount_used": Decimal(future_target),
        "current_funded_amount": Decimal(P),
        "projected_total_contributions": total_contributions,
        "projected_ending_value": projected_ending,
        "projected_funding_gap": funding_gap,
        "required_periodic_contribution": required_periodic,
        "funding_status": "funded" if projected_ending >= Decimal(future_target) else "underfunded",
    }

    metadata = {
        "inflation_applied": inflation is not None,
        "inflation_rate": inflation if inflation is not None else None,
        "method": "compound_projection",
        "limitations": "Required periodic calculation assumes fixed rate and ordinary annuity math; does not account for taxes or changes in contribution timing beyond the provided flag.",
    }

    return ScenarioResult(
        scenario_type="goal_funding",
        inputs={"target_amount": Decimal(target_amount), "periodic_contribution": Decimal(periodic_contribution)},
        assumptions=assumptions,
        outputs=outputs,
        metadata=metadata,
    )

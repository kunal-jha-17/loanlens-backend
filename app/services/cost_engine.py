from __future__ import annotations

from math import isclose


def _irr(cashflows: list[float]) -> float:
    """Calculate the IRR for a list of cash flows using a stable iterative method."""
    if not cashflows:
        return 0.0

    # A bad negative or zero denominator can cause non-convergence. Guard against that.
    rate = 0.05
    for _ in range(2000):
        npv = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))
        dnpv = sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cashflows))
        if abs(dnpv) < 1e-12:
            break
        new_rate = rate - (npv / dnpv)
        if new_rate <= -0.9999:
            new_rate = -0.99
        if abs(new_rate - rate) < 1e-12:
            rate = new_rate
            break
        rate = new_rate

    return rate


def compute_cash_flow_cost(net_disbursal: float, fees: list[dict], repayment_schedule: list[dict], tenure_months: int) -> tuple[float, float, list[dict]]:
    """Compute total repayment and estimated annualised cost from deterministic cash-flow data."""
    fee_total = sum(float(item["amount"]) for item in fees)
    total_repayment = 0.0
    schedule: list[dict] = []

    for item in repayment_schedule:
        amount = float(item["amount"])
        total_repayment += amount
        schedule.append({
            "month": int(item.get("month", len(schedule) + 1)),
            "amount": amount,
        })

    if total_repayment <= 0:
        total_repayment = float(net_disbursal) + fee_total

    cashflows = [-float(net_disbursal)]
    for idx, item in enumerate(repayment_schedule, start=1):
        amount = float(item["amount"])
        cashflows.append(amount)

    monthly_rate = _irr(cashflows)
    annualised_cost = ((1 + monthly_rate) ** 12) - 1 if monthly_rate > -1 else 0.0

    return round(total_repayment, 2), round(annualised_cost, 6), schedule

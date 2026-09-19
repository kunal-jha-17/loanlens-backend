from __future__ import annotations

from dataclasses import dataclass

from app.models import Extraction, RepaymentEntry


@dataclass(frozen=True)
class CostComputation:
    total_repayment: float | None
    estimated_annualised_cost: float | None
    schedule: list[RepaymentEntry]
    assumptions: list[str]
    limitations: list[str]
    apr_vs_computed_note: str


def _annualised_from_monthly_irr(cashflows: list[float]) -> float | None:
    """Deterministic IRR solver using bisection for monthly schedules."""
    if len(cashflows) < 2:
        return None

    def npv(rate: float) -> float:
        return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))

    low = -0.99
    high = 10.0
    low_npv = npv(low)
    high_npv = npv(high)

    if low_npv == 0:
        monthly = low
    elif high_npv == 0:
        monthly = high
    elif low_npv * high_npv > 0:
        return None
    else:
        monthly = 0.0
        for _ in range(300):
            mid = (low + high) / 2
            mid_npv = npv(mid)
            monthly = mid
            if abs(mid_npv) < 1e-8:
                break
            if low_npv * mid_npv < 0:
                high = mid
                high_npv = mid_npv
            else:
                low = mid
                low_npv = mid_npv

    if monthly <= -1:
        return None
    return (1 + monthly) ** 12 - 1


def _normalise_schedule(repayment_schedule: list[RepaymentEntry]) -> list[RepaymentEntry]:
    return sorted(repayment_schedule, key=lambda item: item.month)


def compute_cash_flow_cost(extraction: Extraction) -> CostComputation:
    assumptions = [
        "MVP supports monthly repayment schedules only; each schedule entry month is treated as one month from disbursal.",
        "All amounts are computed deterministically from extracted values; no LLM-based math is used.",
    ]
    limitations: list[str] = []

    schedule = _normalise_schedule(extraction.repayment_schedule)

    if not schedule:
        limitations.append("Repayment schedule is missing, so annualised cost cannot be computed.")
        return CostComputation(
            total_repayment=None,
            estimated_annualised_cost=None,
            schedule=[],
            assumptions=assumptions,
            limitations=limitations,
            apr_vs_computed_note="Verify with lender: insufficient repayment schedule data.",
        )

    total_repayment = round(sum(item.amount for item in schedule), 2)

    if extraction.net_disbursal is None or extraction.net_disbursal <= 0:
        limitations.append("Net disbursal is missing or invalid, so annualised cost cannot be computed.")
        return CostComputation(
            total_repayment=total_repayment,
            estimated_annualised_cost=None,
            schedule=schedule,
            assumptions=assumptions,
            limitations=limitations,
            apr_vs_computed_note="Verify with lender: missing valid net disbursal.",
        )

    cashflows = [-extraction.net_disbursal]
    max_month = schedule[-1].month
    monthly_amounts = {item.month: item.amount for item in schedule}
    for month in range(1, max_month + 1):
        cashflows.append(monthly_amounts.get(month, 0.0))

    if all(cf <= 0 for cf in cashflows) or all(cf >= 0 for cf in cashflows):
        limitations.append("Cashflow signs are invalid for cost computation; verify repayment entries.")
        annualised = None
    else:
        annualised = _annualised_from_monthly_irr(cashflows)
        if annualised is None:
            limitations.append("Annualised cost did not converge from available cashflows; verify with lender.")

    if annualised is None:
        apr_note = "Verify with lender: computed annualised cost is unavailable from current data."
    elif extraction.stated_apr is None:
        apr_note = "Verify with lender: stated APR not visible for comparison."
    else:
        delta = abs(annualised - extraction.stated_apr)
        if delta > 0.02:
            apr_note = (
                f"Verify with lender: stated APR ({extraction.stated_apr:.4f}) differs from computed annualised cost "
                f"({annualised:.4f})."
            )
        else:
            apr_note = "Stated APR is broadly aligned with computed annualised cost."

    if extraction.sanctioned_amount is not None and extraction.net_disbursal > extraction.sanctioned_amount:
        limitations.append("Net disbursal exceeds sanctioned amount; verify extracted values.")

    return CostComputation(
        total_repayment=total_repayment,
        estimated_annualised_cost=round(annualised, 6) if annualised is not None else None,
        schedule=schedule,
        assumptions=assumptions,
        limitations=limitations,
        apr_vs_computed_note=apr_note,
    )

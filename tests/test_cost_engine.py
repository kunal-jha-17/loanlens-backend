from __future__ import annotations

from app.models import Extraction
from app.services.cost_engine import compute_cash_flow_cost


def _extraction(**overrides):
    payload = {
        "lender_name": "Demo",
        "sanctioned_amount": 100000,
        "net_disbursal": 95000,
        "fees": [{"name": "processing_fee", "amount": 5000}],
        "tenure": 12,
        "repayment_schedule": [{"month": month, "amount": 10000} for month in range(1, 13)],
        "stated_apr": 0.25,
        "ocr_confidence": 0.95,
        "field_confidence": {},
    }
    payload.update(overrides)
    return Extraction(**payload)


def test_cost_engine_happy_path() -> None:
    cost = compute_cash_flow_cost(_extraction())
    assert cost.total_repayment == 120000
    assert cost.estimated_annualised_cost is not None


def test_cost_engine_handles_missing_schedule_safely() -> None:
    cost = compute_cash_flow_cost(_extraction(repayment_schedule=[]))
    assert cost.estimated_annualised_cost is None
    assert "missing" in " ".join(cost.limitations).lower()


def test_cost_engine_handles_non_convergent_signs_safely() -> None:
    cost = compute_cash_flow_cost(_extraction(repayment_schedule=[{"month": 1, "amount": 0.0001}]))
    assert cost.estimated_annualised_cost is None or cost.estimated_annualised_cost >= -1


def test_cost_engine_marks_apr_discrepancy_for_verification() -> None:
    cost = compute_cash_flow_cost(_extraction(stated_apr=0.01))
    assert "Verify with lender" in cost.apr_vs_computed_note

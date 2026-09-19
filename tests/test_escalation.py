from __future__ import annotations

from app.models import ComplianceRule, Extraction
from app.services.escalation import build_escalation_draft


def test_escalation_routes_to_sachet_for_unknown_high_risk() -> None:
    extraction = Extraction(
        lender_name="Unknown App",
        sanctioned_amount=10000,
        net_disbursal=9000,
        fees=[],
        tenure=2,
        repayment_schedule=[{"month": 1, "amount": 6000}, {"month": 2, "amount": 6000}],
        permissions_text="call log",
        repayment_account_text="personal upi",
    )
    rules = [
        ComplianceRule(rule_id="FLOW-01", status="Potential concern", evidence_text="x", reason_text="x"),
        ComplianceRule(rule_id="DATA-01", status="Potential concern", evidence_text="x", reason_text="x"),
    ]
    draft_type, draft = build_escalation_draft(extraction, rules, "not_found_in_snapshot")
    assert draft_type == "sachet_cybercrime"
    assert "do not auto-submit" in draft


def test_escalation_routes_to_grievance_for_named_entity_dispute() -> None:
    extraction = Extraction(
        lender_name="Apex Capital Finance",
        sanctioned_amount=10000,
        net_disbursal=9000,
        fees=[],
        tenure=2,
        repayment_schedule=[{"month": 1, "amount": 6000}, {"month": 2, "amount": 6000}],
        grievance_text="grievance@apex.example",
    )
    rules: list[ComplianceRule] = []
    draft_type, draft = build_escalation_draft(extraction, rules, "listed_association_found")
    assert draft_type == "grievance_officer"
    assert "RBI CMS" in draft

from __future__ import annotations

from app.models import LoanLensResponse, Extraction, CostReceipt, ComplianceRule, ActionReceipt


def build_mock_response() -> LoanLensResponse:
    return LoanLensResponse(
        extraction=Extraction(
            lender_name="Apex Capital Finance",
            sanctioned_amount=150000.0,
            net_disbursal=138500.0,
            fees=[
                {"name": "processing_fee", "amount": 7500.0},
                {"name": "documentation_fee", "amount": 4000.0},
            ],
            tenure=12,
            repayment_schedule=[
                {"month": 1, "amount": 13000.0},
                {"month": 2, "amount": 13000.0},
                {"month": 3, "amount": 13000.0},
            ],
            nominal_rate=0.18,
            stated_apr=0.18,
            cooling_off_text="Cooling-off period applies before disbursal.",
            grievance_text="Grievance contact: grievance@apexcapital.in",
            permissions_text="Permission sought for contact and call log access for verification.",
            ocr_confidence=0.94,
        ),
        cost_receipt=CostReceipt(
            sanctioned_amount=150000.0,
            net_disbursal=138500.0,
            fees=[
                {"name": "processing_fee", "amount": 7500.0},
                {"name": "documentation_fee", "amount": 4000.0},
            ],
            total_repayment=158200.0,
            schedule=[
                {"month": 1, "amount": 13000.0},
                {"month": 2, "amount": 13000.0},
                {"month": 3, "amount": 13000.0},
            ],
            estimated_annualised_cost=0.21,
            assumptions=[
                "Repayment schedule and due-date timings are assumed as shown in the document.",
                "No hidden charges were identified in the visible text.",
            ],
            limitations=[
                "Actual annualised cost depends on final repayment terms and any additional fees not visible in the uploaded image.",
                "OCR confidence below 1.0 may require manual verification.",
            ],
        ),
        compliance_receipt=[
            ComplianceRule(
                rule_id="KFS-01",
                status="Pass",
                evidence_text="Sanctioned amount, net disbursal, fees, and repayment schedule are visible.",
                reason_text="All key KFS fields are present.",
            ),
            ComplianceRule(
                rule_id="COST-01",
                status="Pass",
                evidence_text="Net disbursal is lower than sanctioned amount by a disclosed fees stack.",
                reason_text="Fee deduction is clear and disclosed.",
            ),
        ],
        action_receipt=ActionReceipt(
            dla_status="listed_association_found",
            snapshot_date="2025-05-08",
            next_steps=[
                "Verify the lender name against the uploaded KFS and DLA snapshot.",
                "Save the evidence pack before any action or escalation.",
            ],
            complaint_draft=None,
        ),
    )

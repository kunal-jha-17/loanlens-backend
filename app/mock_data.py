from __future__ import annotations

from app.models import ActionReceipt, ComplianceRule, CostReceipt, Extraction, Fee, LoanLensResponse


def build_mock_response() -> LoanLensResponse:
    return LoanLensResponse(
        extraction=Extraction(
            lender_name="Apex Capital Finance",
            sanctioned_amount=150000.0,
            net_disbursal=138500.0,
            fees=[
                Fee(name="processing_fee", amount=7500.0),
                Fee(name="documentation_fee", amount=4000.0),
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
                Fee(name="processing_fee", amount=7500.0),
                Fee(name="documentation_fee", amount=4000.0),
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
            ComplianceRule(
                rule_id="FEE-01",
                status="Pass",
                evidence_text="No undisclosed platform/LSP fee was detected in the visible terms.",
                reason_text="The fee structure appears to be disclosed.",
            ),
            ComplianceRule(
                rule_id="FLOW-01",
                status="Pass",
                evidence_text="No personal-account repayment risk was identified in the extracted text.",
                reason_text="Repayment information did not show an unclear account flow.",
            ),
            ComplianceRule(
                rule_id="DATA-01",
                status="Potential concern",
                evidence_text="Permission sought for contact and call log access for verification.",
                reason_text="The document requests contact/call-log access and should be reviewed.",
            ),
            ComplianceRule(
                rule_id="GRV-01",
                status="Pass",
                evidence_text="Grievance contact: grievance@apexcapital.in",
                reason_text="A grievance channel is visible.",
            ),
            ComplianceRule(
                rule_id="COOL-01",
                status="Pass",
                evidence_text="Cooling-off period applies before disbursal.",
                reason_text="Cooling-off wording is visible.",
            ),
            ComplianceRule(
                rule_id="DLA-01",
                status="Needs verification",
                evidence_text="DLA association should be checked against the snapshot table.",
                reason_text="No match should be assumed without snapshot verification.",
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

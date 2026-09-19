from __future__ import annotations

from datetime import UTC, datetime

from app.constants import CRITICAL_CONFIDENCE_THRESHOLD, CRITICAL_FIELDS, GLOBAL_DISCLAIMER
from app.models import ActionReceipt, CostReceipt, Extraction, LoanLensResponse
from app.services.cost_engine import compute_cash_flow_cost
from app.services.dla_lookup import DlaSnapshotLookup
from app.services.escalation import build_escalation_draft
from app.services.rules_engine import evaluate_rules


class CriticalFieldError(ValueError):
    pass


def _critical_missing_fields(extraction: Extraction) -> list[str]:
    missing = []
    for field in CRITICAL_FIELDS:
        value = getattr(extraction, field)
        if value in (None, "") or (field == "repayment_schedule" and not extraction.repayment_schedule):
            missing.append(field)
    return missing


def _low_confidence_warnings(extraction: Extraction) -> list[str]:
    warnings: list[str] = []

    if extraction.ocr_confidence is not None and extraction.ocr_confidence < CRITICAL_CONFIDENCE_THRESHOLD:
        warnings.append(
            f"OCR confidence {extraction.ocr_confidence:.2f} is below threshold {CRITICAL_CONFIDENCE_THRESHOLD:.2f}; verify critical fields manually."
        )

    for field in CRITICAL_FIELDS:
        field_conf = extraction.field_confidence.get(field)
        if field_conf is not None and field_conf < CRITICAL_CONFIDENCE_THRESHOLD:
            warnings.append(
                f"Field confidence for {field} is {field_conf:.2f} (< {CRITICAL_CONFIDENCE_THRESHOLD:.2f}); needs verification."
            )

    return warnings


def process_extraction(extraction: Extraction) -> LoanLensResponse:
    missing_critical = _critical_missing_fields(extraction)
    if missing_critical:
        raise CriticalFieldError(f"Missing critical fields: {', '.join(missing_critical)}")

    warnings = _low_confidence_warnings(extraction)

    cost = compute_cash_flow_cost(extraction)
    dla_lookup = DlaSnapshotLookup()
    dla_status = dla_lookup.lookup(extraction.lender_name)
    rules = evaluate_rules(extraction, dla_status, cost.estimated_annualised_cost, warnings)
    draft_type, complaint_draft = build_escalation_draft(extraction, rules, dla_status)

    if any(rule.status in {"Missing", "Needs verification"} for rule in rules):
        warnings.append("One or more checks need verification based on missing or low-confidence fields.")

    cost_receipt = CostReceipt(
        sanctioned_amount=extraction.sanctioned_amount,
        net_disbursal=extraction.net_disbursal,
        fees=extraction.fees,
        total_repayment=cost.total_repayment,
        schedule=cost.schedule,
        estimated_annualised_cost=cost.estimated_annualised_cost,
        apr_vs_computed_note=cost.apr_vs_computed_note,
        assumptions=cost.assumptions,
        limitations=cost.limitations,
    )

    action_receipt = ActionReceipt(
        dla_status=dla_status,
        snapshot_date=dla_lookup.snapshot_date,
        snapshot_notice=dla_lookup.snapshot_notice(),
        next_steps=[
            "Review all flagged items and verify with the lender using the original KFS/loan document.",
            "Preserve screenshots, KFS copy, and repayment proof before any complaint draft is sent.",
        ],
        complaint_draft=complaint_draft,
        draft_type=draft_type,
        evidence_pack={
            "generated_at": datetime.now(UTC).isoformat(),
            "rule_ids": [rule.rule_id for rule in rules],
            "warning_count": len(warnings),
            "draft_only": True,
        },
    )

    return LoanLensResponse(
        extraction=extraction,
        cost_receipt=cost_receipt,
        compliance_receipt=rules,
        action_receipt=action_receipt,
        global_disclaimer=GLOBAL_DISCLAIMER,
        processing_warnings=warnings,
    )

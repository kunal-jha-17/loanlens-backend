from __future__ import annotations

from app.constants import CRITICAL_CONFIDENCE_THRESHOLD, CRITICAL_FIELDS, RULE_IDS
from app.models import ComplianceRule, DlaStatus, Extraction


def _build_rule(rule_id: str, status: str, evidence: str, reason: str) -> ComplianceRule:
    return ComplianceRule(rule_id=rule_id, status=status, evidence_text=evidence, reason_text=reason)


def evaluate_rules(
    extraction: Extraction,
    dla_status: DlaStatus,
    annualised_cost: float | None,
    processing_warnings: list[str],
) -> list[ComplianceRule]:
    results: dict[str, ComplianceRule] = {}

    missing_critical = [
        field
        for field in CRITICAL_FIELDS
        if getattr(extraction, field) in (None, "") or (field == "repayment_schedule" and not extraction.repayment_schedule)
    ]

    low_confidence_fields = [
        field
        for field in CRITICAL_FIELDS
        if extraction.field_confidence.get(field) is not None
        and extraction.field_confidence[field] < CRITICAL_CONFIDENCE_THRESHOLD
    ]

    if missing_critical:
        results["KFS-01"] = _build_rule(
            "KFS-01",
            "Missing",
            f"Missing critical fields: {', '.join(missing_critical)}.",
            "Key Fact Statement fields are incomplete in the visible extraction.",
        )
    elif low_confidence_fields or (extraction.ocr_confidence is not None and extraction.ocr_confidence < CRITICAL_CONFIDENCE_THRESHOLD):
        results["KFS-01"] = _build_rule(
            "KFS-01",
            "Needs verification",
            f"Low confidence on critical fields: {', '.join(low_confidence_fields) or 'ocr_confidence'}.",
            "Critical KFS values are present but confidence is below threshold.",
        )
    else:
        results["KFS-01"] = _build_rule(
            "KFS-01",
            "Pass",
            "Sanctioned amount, net disbursal, tenure, and monthly repayment schedule are visible.",
            "Critical KFS fields are available with acceptable confidence.",
        )

    if annualised_cost is None or extraction.stated_apr is None:
        results["COST-01"] = _build_rule(
            "COST-01",
            "Needs verification",
            "Unable to complete deterministic APR comparison from available fields.",
            "Verify with lender using complete repayment schedule, disbursal, and stated APR.",
        )
    else:
        delta = abs(annualised_cost - extraction.stated_apr)
        if delta > 0.02:
            results["COST-01"] = _build_rule(
                "COST-01",
                "Potential concern",
                f"Computed annualised cost {annualised_cost:.4f} vs stated APR {extraction.stated_apr:.4f}.",
                "Verify with lender; discrepancy may come from hidden/unstated charges or extraction errors.",
            )
        else:
            results["COST-01"] = _build_rule(
                "COST-01",
                "Pass",
                f"Computed annualised cost {annualised_cost:.4f} is close to stated APR {extraction.stated_apr:.4f}.",
                "Cost disclosure appears internally consistent.",
            )

    fee_names = [fee.name.lower() for fee in extraction.fees]
    if any(token in name for name in fee_names for token in ("platform", "lsp", "service_partner", "convenience")):
        results["FEE-01"] = _build_rule(
            "FEE-01",
            "Potential concern",
            f"Extracted fee names: {', '.join(fee.name for fee in extraction.fees)}.",
            "Fee list includes platform/LSP-like charges that should be explicitly verified with lender.",
        )
    elif extraction.sanctioned_amount and extraction.net_disbursal and extraction.net_disbursal < extraction.sanctioned_amount and not extraction.fees:
        results["FEE-01"] = _build_rule(
            "FEE-01",
            "Needs verification",
            "Net disbursal is lower than sanctioned amount, but no fee breakdown is visible.",
            "Fee deductions may exist but are not explicitly shown.",
        )
    else:
        results["FEE-01"] = _build_rule(
            "FEE-01",
            "Pass",
            "No platform/LSP-like fee token was detected in extracted fee names.",
            "No obvious undisclosed fee marker found in current extraction.",
        )

    repayment_text = (extraction.repayment_account_text or "").lower()
    if any(token in repayment_text for token in ("personal", "individual", "upi", "wallet", "friend")):
        results["FLOW-01"] = _build_rule(
            "FLOW-01",
            "Potential concern",
            f"Repayment account text: {extraction.repayment_account_text}",
            "Repayment flow may reference a personal/unclear account and should be verified.",
        )
    elif not extraction.repayment_account_text:
        results["FLOW-01"] = _build_rule(
            "FLOW-01",
            "Needs verification",
            "Repayment account details are not visible.",
            "Unable to confirm whether repayment goes to a business account.",
        )
    else:
        results["FLOW-01"] = _build_rule(
            "FLOW-01",
            "Pass",
            f"Repayment account text: {extraction.repayment_account_text}",
            "Repayment destination appears explicitly described.",
        )

    permissions_text = (extraction.permissions_text or "").lower()
    if any(token in permissions_text for token in ("contact", "call log", "telephony")):
        results["DATA-01"] = _build_rule(
            "DATA-01",
            "Potential concern",
            f"Permissions text: {extraction.permissions_text}",
            "Contact/call-log/telephony permission requests should be reviewed carefully.",
        )
    elif not extraction.permissions_text:
        results["DATA-01"] = _build_rule(
            "DATA-01",
            "Needs verification",
            "No permissions statement is visible in extracted text.",
            "Unable to confirm whether sensitive phone permissions are requested.",
        )
    else:
        results["DATA-01"] = _build_rule(
            "DATA-01",
            "Pass",
            f"Permissions text: {extraction.permissions_text}",
            "No contact/call-log/telephony request detected in current text.",
        )

    if extraction.grievance_text:
        results["GRV-01"] = _build_rule(
            "GRV-01",
            "Pass",
            extraction.grievance_text,
            "Grievance contact details are visible.",
        )
    else:
        results["GRV-01"] = _build_rule(
            "GRV-01",
            "Missing",
            "Grievance contact details are not present in visible extraction.",
            "A grievance channel should be disclosed.",
        )

    if extraction.cooling_off_text:
        results["COOL-01"] = _build_rule(
            "COOL-01",
            "Pass",
            extraction.cooling_off_text,
            "Cooling-off wording is visible.",
        )
    else:
        results["COOL-01"] = _build_rule(
            "COOL-01",
            "Missing",
            "Cooling-off wording is not visible in extraction.",
            "Cooling-off availability should be disclosed or confirmed.",
        )

    if dla_status == "listed_association_found":
        results["DLA-01"] = _build_rule(
            "DLA-01",
            "Pass",
            "DLA snapshot lookup returned listed association found.",
            "A reported association exists in the dated snapshot.",
        )
    elif dla_status == "not_found_in_snapshot":
        results["DLA-01"] = _build_rule(
            "DLA-01",
            "Potential concern",
            "DLA snapshot lookup returned no match for provided lender/app name.",
            "No snapshot match was found; verify entity naming and credentials with lender.",
        )
    else:
        results["DLA-01"] = _build_rule(
            "DLA-01",
            "Needs verification",
            "DLA snapshot could not verify association from available name.",
            "Snapshot verification is inconclusive and needs manual confirmation.",
        )

    # Ensure exactly one result for each rule ID.
    return [results[rule_id] for rule_id in RULE_IDS]

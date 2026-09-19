from __future__ import annotations

from app.models import ComplianceRule, DlaStatus, Extraction


def build_escalation_draft(
    extraction: Extraction,
    rules: list[ComplianceRule],
    dla_status: DlaStatus,
) -> tuple[str | None, str | None]:
    status_by_rule = {rule.rule_id: rule.status for rule in rules}
    lender_name = extraction.lender_name or "the lender/app"

    high_risk_unknown = dla_status != "listed_association_found" and (
        status_by_rule.get("FLOW-01") == "Potential concern"
        or status_by_rule.get("DATA-01") == "Potential concern"
    )

    if high_risk_unknown:
        draft = (
            "Draft for Sachet + cybercrime.gov.in/1930 (do not auto-submit):\n"
            f"- App/entity shown as: {lender_name}\n"
            "- Snapshot status: association not confirmed\n"
            "- Concerns observed from document text: possible unclear repayment flow and/or intrusive permissions\n"
            "- Request review of unauthorised or suspicious app behaviour and preserve evidence screenshots."
        )
        return "sachet_cybercrime", draft

    if extraction.grievance_text and extraction.lender_name:
        draft = (
            "Draft to grievance officer (do not auto-submit):\n"
            f"- Entity: {lender_name}\n"
            "- Request clarification on charges, repayment destination, and disclosures based on attached evidence.\n"
            "- Ask for written response timeline and redress steps.\n"
            "- If unresolved after 30 days, you may escalate through RBI CMS with the evidence pack."
        )
        return "grievance_officer", draft

    return None, None

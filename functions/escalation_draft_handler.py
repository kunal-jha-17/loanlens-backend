from __future__ import annotations


def lambda_handler(event, context):
    draft_type = event.get("draft_type")
    extraction = event.get("extraction", {})
    rules = event.get("compliance_receipt", [])

    lender_name = extraction.get("lender_name") or "the lender/app"
    flagged_rules = [
        rule.get("rule_id")
        for rule in rules
        if rule.get("status") in {"Potential concern", "Missing"}
    ]

    if draft_type == "grievance_officer":
        draft = (
            "Draft to grievance officer (do not auto-submit):\n"
            f"- Entity: {lender_name}\n"
            f"- Evidence flags: {', '.join(flagged_rules) or 'none'}\n"
            "- Please clarify the charges, repayment destination, disclosures, "
            "and grievance process shown in the attached evidence.\n"
            "- If unresolved after 30 days, you may escalate through RBI CMS "
            "with the evidence pack."
        )
    else:
        draft = (
            "Draft for Sachet + cybercrime.gov.in/1930 (do not auto-submit):\n"
            f"- App/entity shown as: {lender_name}\n"
            f"- Evidence flags: {', '.join(flagged_rules) or 'none'}\n"
            "- Request review of the reported app/entity and preserve the "
            "screenshots, documents, and communications."
        )

    return {
        "draft_type": draft_type,
        "complaint_draft": draft,
        "auto_submitted": False,
    }

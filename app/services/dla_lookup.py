from __future__ import annotations

from app.models import ComplianceRule

RULE_LIBRARY = {
    "KFS-01": {
        "result_text": "Key loan terms such as sanctioned amount, net disbursal, fees, or repayment schedule are missing.",
    },
    "COST-01": {
        "result_text": "The lender has deducted fees or other amounts such that net disbursal is lower than the sanctioned amount.",
    },
    "FEE-01": {
        "result_text": "An undisclosed platform or LSP fee may be present and should be verified with the lender.",
    },
    "FLOW-01": {
        "result_text": "Repayment appears to be routed to an unclear, personal, or non-business account.",
    },
    "DATA-01": {
        "result_text": "The document requests contacts, call-log, or telephony permissions that should be reviewed.",
    },
    "GRV-01": {
        "result_text": "No grievance contact or escalation channel is shown in the visible terms.",
    },
    "COOL-01": {
        "result_text": "Cooling-off wording is missing or not clearly disclosed.",
    },
    "DLA-01": {
        "result_text": "No match was found in the DLA snapshot for the lender or app name.",
    },
}


def compute_cash_flow_cost(
    net_disbursal: float,
    fees: list[dict],
    repayment_schedule: list[dict],
    tenure_months: int,
) -> tuple[float, float, list[dict]]:
    """Compute total repayment and annualised cost from deterministic cash-flow data."""
    fee_total = sum(float(item.get("amount", 0.0)) for item in fees)
    schedule: list[dict] = []
    total_repayment = 0.0

    for index, item in enumerate(repayment_schedule, start=1):
        amount = float(item.get("amount", 0.0))
        total_repayment += amount
        schedule.append({
            "month": int(item.get("month", index)),
            "amount": round(amount, 2),
        })

    if total_repayment <= 0:
        total_repayment = float(net_disbursal) + fee_total

    cashflows = [-float(net_disbursal)]
    for item in repayment_schedule:
        cashflows.append(float(item.get("amount", 0.0)))

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

    annualised_cost = ((1 + rate) ** 12) - 1 if rate > -1 else 0.0
    return round(total_repayment, 2), round(annualised_cost, 6), schedule


def evaluate_rules(extraction: dict) -> list[ComplianceRule]:
    """Evaluate the eight seeded rule IDs against the extracted payload."""
    results: list[ComplianceRule] = []

    sanctioned = float(extraction.get("sanctioned_amount", 0.0) or 0.0)
    net_disbursal = float(extraction.get("net_disbursal", 0.0) or 0.0)
    fees = extraction.get("fees", [])
    permissions_text = (extraction.get("permissions_text") or "").lower()
    grievance_text = (extraction.get("grievance_text") or "").lower()
    cooling_off_text = (extraction.get("cooling_off_text") or "").lower()

    if sanctioned <= 0 or net_disbursal <= 0 or not extraction.get("repayment_schedule"):
        results.append(
            ComplianceRule(
                rule_id="KFS-01",
                status="Missing",
                evidence_text="Required KFS fields are not visible or are incomplete.",
                reason_text=RULE_LIBRARY["KFS-01"]["result_text"],
            )
        )
    else:
        results.append(
            ComplianceRule(
                rule_id="KFS-01",
                status="Pass",
                evidence_text="Sanctioned amount, net disbursal, fees, and repayment schedule are visible.",
                reason_text="All key KFS fields are present.",
            )
        )

    if net_disbursal < sanctioned:
        results.append(
            ComplianceRule(
                rule_id="COST-01",
                status="Pass",
                evidence_text=f"Net disbursal {net_disbursal} is lower than sanctioned amount {sanctioned}.",
                reason_text=RULE_LIBRARY["COST-01"]["result_text"],
            )
        )
    else:
        results.append(
            ComplianceRule(
                rule_id="COST-01",
                status="Needs verification",
                evidence_text="Net disbursal is not lower than sanctioned amount based on the current data.",
                reason_text="The pricing relationship should be checked for accuracy.",
            )
        )

    hidden_fee = any(
        "platform" in str(item.get("name", "")).lower() or "lsp" in str(item.get("name", "")).lower()
        for item in fees
    )
    if hidden_fee:
        results.append(
            ComplianceRule(
                rule_id="FEE-01",
                status="Potential concern",
                evidence_text="A platform or LSP fee is visible in the extracted fee list.",
                reason_text=RULE_LIBRARY["FEE-01"]["result_text"],
            )
        )
    else:
        results.append(
            ComplianceRule(
                rule_id="FEE-01",
                status="Pass",
                evidence_text="No undisclosed platform/LSP fee was detected in the extracted fees.",
                reason_text="The fee structure appears to be disclosed.",
            )
        )

    if "personal" in permissions_text or "bank account" in permissions_text or "upi" in permissions_text:
        results.append(
            ComplianceRule(
                rule_id="FLOW-01",
                status="Potential concern",
                evidence_text="Permissions or payment details imply an unclear or personal account flow.",
                reason_text=RULE_LIBRARY["FLOW-01"]["result_text"],
            )
        )
    else:
        results.append(
            ComplianceRule(
                rule_id="FLOW-01",
                status="Pass",
                evidence_text="No explicit personal-account repayment risk was identified.",
                reason_text="Repayment information was not flagged as unclear.",
            )
        )

    if "contact" in permissions_text or "call log" in permissions_text or "telephony" in permissions_text:
        results.append(
            ComplianceRule(
                rule_id="DATA-01",
                status="Potential concern",
                evidence_text="The document requests call-log or telephony permissions.",
                reason_text=RULE_LIBRARY["DATA-01"]["result_text"],
            )
        )
    else:
        results.append(
            ComplianceRule(
                rule_id="DATA-01",
                status="Pass",
                evidence_text="The document does not show contact or call-log permissions in the visible text.",
                reason_text="Permission requests do not appear excessive based on the visible data.",
            )
        )

    if not grievance_text:
        results.append(
            ComplianceRule(
                rule_id="GRV-01",
                status="Missing",
                evidence_text="No grievance contact was found in the extracted text.",
                reason_text=RULE_LIBRARY["GRV-01"]["result_text"],
            )
        )
    else:
        results.append(
            ComplianceRule(
                rule_id="GRV-01",
                status="Pass",
                evidence_text=grievance_text,
                reason_text="A grievance contact is visible.",
            )
        )

    if not cooling_off_text:
        results.append(
            ComplianceRule(
                rule_id="COOL-01",
                status="Missing",
                evidence_text="Cooling-off wording is not visible in the extracted text.",
                reason_text=RULE_LIBRARY["COOL-01"]["result_text"],
            )
        )
    else:
        results.append(
            ComplianceRule(
                rule_id="COOL-01",
                status="Pass",
                evidence_text=cooling_off_text,
                reason_text="Cooling-off wording is visible.",
            )
        )

    results.append(
        ComplianceRule(
            rule_id="DLA-01",
            status="Needs verification",
            evidence_text="DLA association should be checked against the snapshot table.",
            reason_text=RULE_LIBRARY["DLA-01"]["result_text"],
        )
    )

    return results

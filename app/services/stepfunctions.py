from __future__ import annotations

import json

from app.services.aws_resources import (
    ESCALATION_STATE_MACHINE_ARN,
    stepfunctions_client,
)


def _requires_escalation(rules, dla_status) -> bool:
    return dla_status == "not_found_in_snapshot" or any(
        getattr(rule, "status", None) in {"Potential concern", "Missing"}
        for rule in rules
    )


def _decide_draft_type(rules, dla_status) -> str:
    if dla_status != "listed_association_found" and any(
        getattr(rule, "rule_id", None) in {"FLOW-01", "DATA-01"}
        and getattr(rule, "status", None) == "Potential concern"
        for rule in rules
    ):
        return "sachet_cybercrime"
    return "grievance_officer"


def maybe_start_escalation(*, extraction, rules, dla_status, response):
    """
    Returns (complaint_draft, draft_type, execution_arn). All None if no
    escalation was needed or the state machine isn't configured. Uses a
    SYNCHRONOUS Express execution (start_sync_execution) so the draft comes
    back in the same API response instead of async.
    """
    if not _requires_escalation(rules, dla_status):
        return None, None, None

    if not ESCALATION_STATE_MACHINE_ARN:
        response.processing_warnings.append(
            "Escalation was required, but no state machine ARN is configured."
        )
        return None, None, None

    draft_type = _decide_draft_type(rules, dla_status)

    payload = {
        "draft_type": draft_type,
        "extraction": extraction.model_dump(mode="json"),
        "compliance_receipt": [rule.model_dump(mode="json") for rule in rules],
    }

    try:
        result = stepfunctions_client().start_sync_execution(
            stateMachineArn=ESCALATION_STATE_MACHINE_ARN,
            input=json.dumps(payload),
        )
    except Exception as exc:
        response.processing_warnings.append(f"Escalation workflow call failed: {exc}")
        return None, None, None

    output = json.loads(result.get("output", "{}"))
    complaint_draft = output.get("complaint_draft")
    execution_arn = result.get("executionArn")

    return complaint_draft, draft_type, execution_arn

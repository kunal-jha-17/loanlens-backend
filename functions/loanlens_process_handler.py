from __future__ import annotations

import json

from app.models import Extraction, LoanLensInput
from app.services.orchestrator import CriticalFieldError, process_extraction


def lambda_handler(event, context):
    body = event.get("body") or "{}"
    payload = json.loads(body) if isinstance(body, str) else body

    try:
        request = LoanLensInput(**payload)
        response = process_extraction(request.extraction)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response.model_dump(mode="json")),
        }
    except CriticalFieldError as exc:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": str(exc)}),
        }
    except Exception as exc:  # deterministic bounded error
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": f"Invalid request payload: {exc}"}),
        }

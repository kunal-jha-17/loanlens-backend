from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.services.aws_resources import interaction_logs_table

try:
    from app.services.masking import mask_payload
except ImportError:
    # Fallback if masking.py doesn't exist yet — don't crash logging over it.
    def mask_payload(payload):
        return payload


def write_interaction_log(
    *,
    request_payload: dict,
    response_payload: dict,
    status: str,
    table=None,
) -> str:
    interaction_id = str(uuid4())
    now = datetime.now(UTC)
    expires_at = int((now + timedelta(days=30)).timestamp())

    item = {
        "interaction_id": interaction_id,
        "created_at": now.isoformat(),
        "expires_at": expires_at,
        "status": status,
        "request": mask_payload(request_payload),
        "response": mask_payload(response_payload),
    }

    try:
        (table or interaction_logs_table()).put_item(Item=item)
    except Exception:
        # Never let logging failure break the actual user-facing response.
        pass

    return interaction_id

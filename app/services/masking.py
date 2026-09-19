from __future__ import annotations

import re

PATTERNS = [
    # Bank account (9-18 digits)
    re.compile(r"\b\d{9,18}\b"),
    # PAN
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE),
    # Aadhaar with optional separators
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    # Phone numbers with optional +91
    re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"),
    # UPI IDs
    re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b"),
    # QR payload fragment
    re.compile(r"\b(?:upi://|QR[:\s]).+", re.IGNORECASE),
]


def mask_text(value: str | None) -> str | None:
    if value is None:
        return None

    masked = value
    for pattern in PATTERNS:
        masked = pattern.sub("[REDACTED]", masked)
    return masked


def mask_payload(payload: dict) -> dict:
    result: dict = {}
    for key, value in payload.items():
        if isinstance(value, str):
            result[key] = mask_text(value)
        elif isinstance(value, list):
            result[key] = [mask_payload(item) if isinstance(item, dict) else mask_text(item) if isinstance(item, str) else item for item in value]
        elif isinstance(value, dict):
            result[key] = mask_payload(value)
        else:
            result[key] = value
    return result

from __future__ import annotations

from app.services.masking import mask_payload, mask_text


def test_mask_text_redacts_expected_tokens() -> None:
    raw = "PAN ABCDE1234F, Aadhaar 1234 5678 9123, phone +91 9876543210, upi user@upi"
    masked = mask_text(raw)
    assert "ABCDE1234F" not in masked
    assert "9876543210" not in masked
    assert "user@upi" not in masked


def test_mask_payload_nested() -> None:
    payload = {"a": {"phone": "9876543210"}, "b": ["ABCDE1234F", {"upi": "foo@upi"}]}
    masked = mask_payload(payload)
    assert masked["a"]["phone"] == "[REDACTED]"
    assert masked["b"][0] == "[REDACTED]"

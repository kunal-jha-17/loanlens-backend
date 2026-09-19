from __future__ import annotations

import json

from functions.health_handler import lambda_handler as health_handler
from functions.loanlens_mock_handler import lambda_handler as mock_handler
from functions.loanlens_process_handler import lambda_handler as process_handler


def test_health_handler() -> None:
    response = health_handler({}, {})
    assert response["statusCode"] == 200


def test_mock_handler_returns_contract() -> None:
    response = mock_handler({}, {})
    assert response["statusCode"] == 200
    payload = json.loads(response["body"])
    assert "global_disclaimer" in payload


def test_process_handler_bad_payload_error() -> None:
    response = process_handler({"body": json.dumps({})}, {})
    assert response["statusCode"] in {400, 422}

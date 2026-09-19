from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.constants import GLOBAL_DISCLAIMER
from app.main import app


ROOT = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_mock_contract_contains_required_sections_and_disclaimer() -> None:
    response = client.get("/loanlens/mock")
    assert response.status_code == 200
    payload = response.json()
    assert set(["extraction", "cost_receipt", "compliance_receipt", "action_receipt"]).issubset(payload.keys())
    assert payload["global_disclaimer"] == GLOBAL_DISCLAIMER


def test_process_endpoint_typed_success() -> None:
    payload = _fixture("extraction_clean.json")
    response = client.post("/loanlens/process", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["action_receipt"]["snapshot_notice"].startswith("Directory result is based on a snapshot dated")
    assert len(body["compliance_receipt"]) == 8


def test_process_endpoint_missing_critical_field_returns_clear_error() -> None:
    payload = _fixture("extraction_clean.json")
    payload["extraction"]["net_disbursal"] = None
    response = client.post("/loanlens/process", json=payload)
    assert response.status_code == 422
    assert "Missing critical fields" in response.json()["detail"]

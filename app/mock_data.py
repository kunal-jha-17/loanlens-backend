from __future__ import annotations

import json
from pathlib import Path

from app.models import Extraction, LoanLensResponse
from app.services.orchestrator import process_extraction


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "extraction_clean.json"


def build_mock_response() -> LoanLensResponse:
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    extraction = Extraction(**payload["extraction"])
    return process_extraction(extraction)

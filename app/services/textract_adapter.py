from __future__ import annotations

import json
from pathlib import Path

import boto3

from app.config import SETTINGS
from app.models import Extraction


class TextractAdapter:
    def extract(self, bucket: str, key: str) -> Extraction:
        raise NotImplementedError


class FakeTextractAdapter(TextractAdapter):
    """Deterministic local adapter for tests and local SAM usage."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        self.fixture_path = fixture_path or Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "extraction_clean.json"

    def extract(self, bucket: str, key: str) -> Extraction:
        with self.fixture_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return Extraction(**payload["extraction"])


class AwsTextractAdapter(TextractAdapter):
    """Thin boundary that calls Textract asynchronously. Parsing remains deterministic."""

    def __init__(self) -> None:
        self.client = boto3.client("textract", region_name=SETTINGS.aws_region)

    def extract(self, bucket: str, key: str) -> Extraction:
        # Start async job and return a bounded placeholder extraction; downstream marks for verification.
        self.client.start_document_text_detection(DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}})
        return Extraction(
            lender_name=None,
            sanctioned_amount=None,
            net_disbursal=None,
            fees=[],
            tenure=None,
            repayment_schedule=[],
            ocr_confidence=0.0,
            field_confidence={},
        )

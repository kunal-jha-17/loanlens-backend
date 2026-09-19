from __future__ import annotations

import json
import os

from app.config import SETTINGS
from app.services.masking import mask_payload
from app.services.textract_adapter import AwsTextractAdapter, FakeTextractAdapter


def _adapter():
    use_fake = os.getenv("USE_FAKE_TEXTRACT", "true").lower() == "true"
    return FakeTextractAdapter() if use_fake else AwsTextractAdapter()


def lambda_handler(event, context):
    records = event.get("Records", [])
    adapter = _adapter()
    outputs = []

    for record in records:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        extraction = adapter.extract(bucket, key)
        outputs.append(
            {
                "bucket": bucket,
                "key": key,
                "extraction": mask_payload(extraction.model_dump(mode="json")),
                "rules_table": SETTINGS.dynamodb_rules_table,
            }
        )

    return {"statusCode": 200, "body": json.dumps({"results": outputs})}

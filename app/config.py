from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class ServiceSettings:
    app_env: str = os.getenv("APP_ENV", "development")
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    s3_input_bucket: str = os.getenv("S3_INPUT_BUCKET", "loanlens-uploads")
    dynamodb_rules_table: str = os.getenv("DYNAMODB_RULES_TABLE", "loanlens-rules")
    dynamodb_dla_table: str = os.getenv("DYNAMODB_DLA_TABLE", "loanlens-dla-snapshot")
    dynamodb_logs_table: str = os.getenv("DYNAMODB_LOGS_TABLE", "loanlens-interaction-log")
    escalation_state_machine_arn: str = os.getenv("ESCALATION_STATE_MACHINE_ARN", "")


SETTINGS = ServiceSettings()

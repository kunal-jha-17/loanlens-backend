from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceSettings:
    app_env: str = "development"
    aws_region: str = "ap-south-1"
    s3_input_bucket: str = "loanlens-uploads"
    dynamodb_rules_table: str = "loanlens-rules"
    dynamodb_dla_table: str = "loanlens-dla-snapshot"
    dynamodb_logs_table: str = "loanlens-interaction-log"
    dla_snapshot_date: str = "2025-05-08"


SETTINGS = ServiceSettings()

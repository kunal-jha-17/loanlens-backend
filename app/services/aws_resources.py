from __future__ import annotations

import os

import boto3

# Self-contained env reads — no dependency on config.py internals, so this
# can't break on an unknown SETTINGS shape. Falls back to sane defaults.
AWS_REGION = os.getenv("LOANLENS_AWS_REGION", os.getenv("AWS_REGION", "ap-south-1"))
DLA_TABLE_NAME = os.getenv("DYNAMODB_DLA_TABLE", "LoanLensDlaSnapshotTable")
LOGS_TABLE_NAME = os.getenv("DYNAMODB_LOGS_TABLE", "LoanLensInteractionLogsTable")
ESCALATION_STATE_MACHINE_ARN = os.getenv("ESCALATION_STATE_MACHINE_ARN", "")


def dynamodb_resource():
    return boto3.resource("dynamodb", region_name=AWS_REGION)


def stepfunctions_client():
    return boto3.client("stepfunctions", region_name=AWS_REGION)


def dla_snapshot_table():
    return dynamodb_resource().Table(DLA_TABLE_NAME)


def interaction_logs_table():
    return dynamodb_resource().Table(LOGS_TABLE_NAME)

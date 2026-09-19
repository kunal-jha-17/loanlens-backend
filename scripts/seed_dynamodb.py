from __future__ import annotations

import json
from pathlib import Path

import boto3

from app.config import SETTINGS


ROOT = Path(__file__).resolve().parents[1]


def _load_json(relative_path: str):
    with (ROOT / relative_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_rules_table() -> None:
    table = boto3.resource("dynamodb").Table(SETTINGS.dynamodb_rules_table)
    for item in _load_json("data/rules_seed.json"):
        table.put_item(Item=item)


def seed_dla_snapshot_table() -> None:
    payload = _load_json("data/dla_snapshot_2026-09-01.json")
    table = boto3.resource("dynamodb").Table(SETTINGS.dynamodb_dla_table)
    for entry in payload["entries"]:
        table.put_item(
            Item={
                "snapshot_date": payload["snapshot_date"],
                "canonical_name": entry["canonical_name"],
                "aliases": entry["aliases"],
                "listed_association": entry["listed_association"],
            }
        )


if __name__ == "__main__":
    seed_rules_table()
    seed_dla_snapshot_table()
    print("Seeded rules and DLA snapshot tables.")

from __future__ import annotations

from boto3.dynamodb.conditions import Key

from app.constants import DLA_NOTICE_TEMPLATE
from app.models import DlaStatus
from app.services.aws_resources import dla_snapshot_table


class DlaSnapshotLookup:
    def __init__(self, table=None) -> None:
        self.table = table or dla_snapshot_table()
        self.snapshot_date = "2026-09-01"

    def lookup(self, lender_name: str | None) -> DlaStatus:
        normalized = " ".join((lender_name or "").strip().lower().split())
        if not normalized:
            return "unable_to_verify"

        try:
            response = self.table.query(
                KeyConditionExpression=Key("snapshot_date").eq(self.snapshot_date)
            )
        except Exception:
            return "unable_to_verify"

        for item in response.get("Items", []):
            canonical_name = " ".join(
                str(item.get("canonical_name", "")).lower().split()
            )
            aliases = {
                " ".join(str(alias).lower().split())
                for alias in item.get("aliases", [])
            }

            if normalized == canonical_name or normalized in aliases:
                if item.get("listed_association") is True:
                    return "listed_association_found"
                return "not_found_in_snapshot"

        return "not_found_in_snapshot"

    def snapshot_notice(self) -> str:
        return DLA_NOTICE_TEMPLATE.format(date=self.snapshot_date)

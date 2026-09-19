from __future__ import annotations

import json
from pathlib import Path

from app.constants import DLA_NOTICE_TEMPLATE
from app.models import DlaStatus


def _normalize_name(name: str) -> str:
    return " ".join(name.lower().strip().split())


class DlaSnapshotLookup:
    def __init__(self, snapshot_path: Path | None = None) -> None:
        self.snapshot_path = snapshot_path or Path(__file__).resolve().parents[2] / "data" / "dla_snapshot_2026-09-01.json"
        self.snapshot_data = self._load_snapshot()

    def _load_snapshot(self) -> dict:
        with self.snapshot_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @property
    def snapshot_date(self) -> str:
        return self.snapshot_data["snapshot_date"]

    def snapshot_notice(self) -> str:
        return DLA_NOTICE_TEMPLATE.format(date=self.snapshot_date)

    def lookup(self, lender_name: str | None) -> DlaStatus:
        if not lender_name:
            return "unable_to_verify"

        normalized = _normalize_name(lender_name)
        for entry in self.snapshot_data.get("entries", []):
            aliases = [_normalize_name(alias) for alias in entry.get("aliases", [])]
            canonical = _normalize_name(entry.get("canonical_name", ""))
            if normalized == canonical or normalized in aliases:
                return "listed_association_found" if entry.get("listed_association", False) else "not_found_in_snapshot"

        return "not_found_in_snapshot"

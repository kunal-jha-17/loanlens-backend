from __future__ import annotations

from app.constants import DLA_NOTICE_TEMPLATE
from app.services.dla_lookup import DlaSnapshotLookup


def test_dla_alias_match_and_status_values() -> None:
    lookup = DlaSnapshotLookup()
    assert lookup.lookup("Apex CF") == "listed_association_found"
    assert lookup.lookup("Unknown App") == "not_found_in_snapshot"
    assert lookup.lookup(None) == "unable_to_verify"


def test_dla_notice_exact_template_wording() -> None:
    lookup = DlaSnapshotLookup()
    assert lookup.snapshot_notice() == DLA_NOTICE_TEMPLATE.format(date=lookup.snapshot_date)

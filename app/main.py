from __future__ import annotations

from app.config import SETTINGS


def build_snapshot_notice(snapshot_date: str) -> str:
    return (
        f"Directory result is based on a snapshot dated {snapshot_date}. "
        "Listing indicates a reported association, not RBI approval, registration, or endorsement. "
        "A missing match may be caused by name differences or an outdated snapshot."
    )


def lookup_dla_status(lender_name: str) -> tuple[str, str, list[str], str | None]:
    """Return a DLA status using a deterministic snapshot-style lookup."""
    normalized = (lender_name or "").strip().lower()
    snapshot_date = SETTINGS.dla_snapshot_date

    if not normalized:
        return (
            "unable_to_verify",
            snapshot_date,
            [
                "Confirm the lender name is visible in the uploaded offer.",
                "Verify the exact name against the DLA snapshot before advising the user.",
            ],
            None,
        )

    alias_map = {
        "apex capital finance": "listed_association_found",
        "starfin credit": "not_found_in_snapshot",
        "griha loans": "unable_to_verify",
    }
    status = alias_map.get(normalized, "not_found_in_snapshot")

    if status == "listed_association_found":
        next_steps = [
            "Verify the lender name against the uploaded KFS and DLA snapshot.",
            "Save the evidence pack and make clear that the result is a reported association, not RBI approval.",
        ]
        complaint_draft = None
    elif status == "not_found_in_snapshot":
        next_steps = [
            "Ask the lender or app provider for the official entity and licence details.",
            "Save the screenshot and document for later grievance or complaint review.",
        ]
        complaint_draft = None
    else:
        next_steps = [
            "Request the exact lender name and app / entity registration details.",
            "Document the uncertainty and avoid presenting the association as regulator-approved.",
        ]
        complaint_draft = None

    return status, snapshot_date, next_steps, complaint_draft

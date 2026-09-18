from __future__ import annotations

from app.config import SETTINGS


def lookup_dla_status(lender_name: str) -> tuple[str, str, list[str], str | None]:
    """Return the DLA status using a snapshot-style lookup. This intentionally avoids any claim of RBI approval."""
    normalized = (lender_name or "").strip().lower()

    if not normalized:
        return (
            "unable_to_verify",
            SETTINGS.dla_snapshot_date,
            [
                "Confirm the lender name is visible in the uploaded offer.",
                "Verify the exact name against the DLA snapshot before advising the user.",
            ],
            None,
        )

    known_matches = {
        "apex capital finance": "listed_association_found",
        "starfin credit": "not_found_in_snapshot",
        "griha loans": "unable_to_verify",
    }

    status = known_matches.get(normalized, "not_found_in_snapshot")

    if status == "listed_association_found":
        next_steps = [
            "Save the snapshot evidence and lender association.",
            "Keep the user informed that this is a reported association, not RBI approval.",
        ]
        complaint_draft = None
    elif status == "not_found_in_snapshot":
        next_steps = [
            "Ask the lender or app provider for their official entity and licence details.",
            "Save the screenshot and document for any future complaint or grievance filing.",
        ]
        complaint_draft = None
    else:
        next_steps = [
            "Request the exact lender name and app / entity registration details.",
            "Document the uncertainty and avoid presenting it as a regulator-approved app.",
        ]
        complaint_draft = None

    return status, SETTINGS.dla_snapshot_date, next_steps, complaint_draft

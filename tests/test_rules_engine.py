from __future__ import annotations

import json
from pathlib import Path

from app.models import Extraction
from app.services.cost_engine import compute_cash_flow_cost
from app.services.dla_lookup import DlaSnapshotLookup
from app.services.rules_engine import evaluate_rules


FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> Extraction:
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return Extraction(**payload["extraction"])


def test_rules_have_exact_eight_ids_and_allowed_statuses() -> None:
    extraction = _load("extraction_clean.json")
    cost = compute_cash_flow_cost(extraction)
    dla = DlaSnapshotLookup().lookup(extraction.lender_name)
    rules = evaluate_rules(extraction, dla, cost.estimated_annualised_cost, [])

    assert [rule.rule_id for rule in rules] == ["KFS-01", "COST-01", "FEE-01", "FLOW-01", "DATA-01", "GRV-01", "COOL-01", "DLA-01"]
    assert all(rule.status in {"Pass", "Missing", "Needs verification", "Potential concern"} for rule in rules)


def test_concerning_fixture_demonstrates_required_concerns() -> None:
    extraction = _load("extraction_concerning.json")
    cost = compute_cash_flow_cost(extraction)
    dla = DlaSnapshotLookup().lookup(extraction.lender_name)
    rules = evaluate_rules(extraction, dla, cost.estimated_annualised_cost, ["low confidence"])
    by_id = {rule.rule_id: rule for rule in rules}

    assert by_id["FEE-01"].status == "Potential concern"
    assert by_id["FLOW-01"].status == "Potential concern"
    assert by_id["DATA-01"].status == "Potential concern"
    assert by_id["COOL-01"].status == "Missing"
    assert by_id["GRV-01"].status == "Missing"

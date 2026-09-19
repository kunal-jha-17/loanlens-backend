from app.services.cost_engine import compute_cash_flow_cost, evaluate_rules


def test_cost_engine_basic():
    total_repayment, annual_cost, schedule = compute_cash_flow_cost(
        net_disbursal=90000.0,
        fees=[{"name": "processing_fee", "amount": 5000.0}],
        repayment_schedule=[
            {"month": 1, "amount": 8000.0},
            {"month": 2, "amount": 8000.0},
            {"month": 3, "amount": 8000.0},
        ],
        tenure_months=12,
    )

    assert total_repayment > 0
    assert annual_cost >= 0
    assert len(schedule) == 3


def test_rules_engine():
    extraction = {
        "lender_name": "Apex Capital Finance",
        "sanctioned_amount": 100000,
        "net_disbursal": 90000,
        "fees": [{"name": "processing_fee", "amount": 10000}],
        "repayment_schedule": [{"month": 1, "amount": 10000}],
        "cooling_off_text": "Cooling-off period applies before disbursal.",
        "grievance_text": "Grievance: grievance@example.com",
        "permissions_text": "Contact and call-log access requested.",
    }

    rules = evaluate_rules(extraction)
    rule_ids = {rule.rule_id for rule in rules}

    assert "KFS-01" in rule_ids
    assert "COST-01" in rule_ids
    assert "FEE-01" in rule_ids
    assert "DATA-01" in rule_ids
    assert "GRV-01" in rule_ids
    assert "COOL-01" in rule_ids
    assert "DLA-01" in rule_ids
    assert any(rule.status in {"Pass", "Potential concern", "Missing"} for rule in rules)

from app.mock_data import build_mock_response


def test_mock_response_shape():
    response = build_mock_response()

    assert "extraction" in response.model_dump()
    assert "cost_receipt" in response.model_dump()
    assert "compliance_receipt" in response.model_dump()
    assert "action_receipt" in response.model_dump()

    extraction = response.extraction
    assert extraction.lender_name
    assert extraction.sanctioned_amount > 0
    assert extraction.net_disbursal > 0
    assert extraction.ocr_confidence >= 0.0

    assert response.compliance_receipt[0].rule_id
    assert response.action_receipt.dla_status in {
        "listed_association_found",
        "not_found_in_snapshot",
        "unable_to_verify",
    }

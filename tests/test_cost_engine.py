from app.mock_data import build_mock_response


def test_mock_response_shape():
    response = build_mock_response()
    payload = response.model_dump()

    assert "extraction" in payload
    assert "cost_receipt" in payload
    assert "compliance_receipt" in payload
    assert "action_receipt" in payload

    extraction = response.extraction
    assert extraction.lender_name
    assert extraction.sanctioned_amount > 0
    assert extraction.net_disbursal > 0
    assert extraction.ocr_confidence >= 0.0
    assert len(response.compliance_receipt) >= 8

    assert response.action_receipt.dla_status in {
        "listed_association_found",
        "not_found_in_snapshot",
        "unable_to_verify",
    }

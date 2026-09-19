from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.mock_data import build_mock_response
from app.models import Extraction, LoanLensInput, LoanLensResponse
from app.services.cost_engine import compute_cash_flow_cost, evaluate_rules
from app.services.dla_lookup import build_snapshot_notice, lookup_dla_status

app = FastAPI(title="LoanLens Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "loanlens-backend"}


@app.get("/loanlens/mock", response_model=LoanLensResponse)
def get_mock_response() -> LoanLensResponse:
    return build_mock_response()


@app.post("/loanlens/process", response_model=LoanLensResponse)
def process_loan_document(payload: LoanLensInput) -> LoanLensResponse:
    extraction = payload.extraction
    lender_name = extraction.lender_name or "Apex Capital Finance"
    fees = [fee.model_dump() for fee in extraction.fees]
    repayment_schedule = [entry.model_dump() for entry in extraction.repayment_schedule]
    sanctioned_amount = float(extraction.sanctioned_amount)
    net_disbursal = float(extraction.net_disbursal)
    tenure = int(extraction.tenure)

    total_repayment, annualised_cost, schedule = compute_cash_flow_cost(
        net_disbursal=net_disbursal,
        fees=fees,
        repayment_schedule=repayment_schedule,
        tenure_months=tenure,
    )

    compliance = evaluate_rules(extraction.model_dump())
    dla_status, snapshot_date, next_steps, complaint_draft = lookup_dla_status(lender_name)
    snapshot_notice = build_snapshot_notice(snapshot_date)

    return LoanLensResponse(
        extraction=Extraction(
            lender_name=lender_name,
            sanctioned_amount=sanctioned_amount,
            net_disbursal=net_disbursal,
            fees=extraction.fees,
            tenure=tenure,
            repayment_schedule=extraction.repayment_schedule,
            nominal_rate=extraction.nominal_rate,
            stated_apr=extraction.stated_apr,
            cooling_off_text=extraction.cooling_off_text,
            grievance_text=extraction.grievance_text,
            permissions_text=extraction.permissions_text,
            ocr_confidence=extraction.ocr_confidence,
        ),
        cost_receipt={
            "sanctioned_amount": sanctioned_amount,
            "net_disbursal": net_disbursal,
            "fees": fees,
            "total_repayment": total_repayment,
            "schedule": schedule,
            "estimated_annualised_cost": annualised_cost,
            "assumptions": [
                "Repayment schedule and due-date timings are assumed as shown in the document.",
                "Annualised cost is computed from the deterministic cash-flow model.",
            ],
            "limitations": [
                "Actual annualised cost depends on final repayment terms and any missing fields.",
                "A low OCR confidence may require manual verification.",
            ],
        },
        compliance_receipt=compliance,
        action_receipt={
            "dla_status": dla_status,
            "snapshot_date": snapshot_date,
            "next_steps": [
                snapshot_notice,
                *next_steps,
            ],
            "complaint_draft": complaint_draft,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

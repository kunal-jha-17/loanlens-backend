from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.mock_data import build_mock_response
from app.models import LoanLensResponse
from app.services.cost_engine import evaluate_rules
from app.services.dla_lookup import lookup_dla_status
from app.services.cost_engine import compute_cash_flow_cost

app = FastAPI(title="LoanLens Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
def process_loanfile(payload: dict) -> LoanLensResponse:
    extraction = payload.get("extraction", {})
    lender_name = extraction.get("lender_name", "Apex Capital Finance")
    fees = extraction.get("fees", [])
    repayment_schedule = extraction.get("repayment_schedule", [])
    sanctioned_amount = float(extraction.get("sanctioned_amount", 0.0) or 0.0)
    net_disbursal = float(extraction.get("net_disbursal", 0.0) or 0.0)
    tenure = int(extraction.get("tenure", 12) or 12)

    total_repayment, annual_cost, schedule = compute_cash_flow_cost(
        net_disbursal=net_disbursal or sanctioned_amount,
        fees=fees,
        repayment_schedule=repayment_schedule,
        tenure_months=tenure,
    )

    compliance = evaluate_rules(extraction)
    dla_status, snapshot_date, next_steps, complaint_draft = lookup_dla_status(lender_name)

    result = LoanLensResponse(
        extraction={
            "lender_name": lender_name,
            "sanctioned_amount": sanctioned_amount,
            "net_disbursal": net_disbursal,
            "fees": fees,
            "tenure": tenure,
            "repayment_schedule": repayment_schedule,
            "nominal_rate": extraction.get("nominal_rate", 0.18),
            "stated_apr": extraction.get("stated_apr", 0.18),
            "cooling_off_text": extraction.get("cooling_off_text"),
            "grievance_text": extraction.get("grievance_text"),
            "permissions_text": extraction.get("permissions_text"),
            "ocr_confidence": extraction.get("ocr_confidence", 0.9),
        },
        cost_receipt={
            "sanctioned_amount": sanctioned_amount,
            "net_disbursal": net_disbursal,
            "fees": fees,
            "total_repayment": total_repayment,
            "schedule": schedule,
            "estimated_annualised_cost": annual_cost,
            "assumptions": [
                "Repayment schedule and due-date timings are assumed as shown in the document.",
                "Annualised cost is computed from the deterministic cash-flow model.",
            ],
            "limitations": [
                "Actual annualised cost depends on final repayment terms and missing fields.",
                "A low OCR confidence may require manual review.",
            ],
        },
        compliance_receipt=compliance,
        action_receipt={
            "dla_status": dla_status,
            "snapshot_date": snapshot_date,
            "next_steps": next_steps,
            "complaint_draft": complaint_draft,
        },
    )

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

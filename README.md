# LoanLens Backend

LoanLens backend scaffold implementing the PRD for a serverless AWS-based document-analysis pipeline.

## What is included

- FastAPI service for local development and API contracts
- AWS SAM template for Lambda-based deployment
- Deterministic cost engine based on cash-flow math
- Rules engine for the required RBI-aligned checks
- DLA snapshot lookup with safe message wording
- Mock response contract aligned to the PRD
- Synthetic sample artifacts for clean and concerning cases
- Unit tests for the contract and finance logic

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API endpoints

- GET /health
- GET /loanlens/mock
- POST /loanlens/process

## API contract

The backend publishes the following response schema:

```json
{
  "extraction": {
    "lender_name": "string",
    "sanctioned_amount": 100000,
    "net_disbursal": 92000,
    "fees": [
      { "name": "processing_fee", "amount": 5000 }
    ],
    "tenure": 12,
    "repayment_schedule": [
      { "month": 1, "amount": 8500 }
    ],
    "nominal_rate": 0.18,
    "stated_apr": 0.18,
    "cooling_off_text": "string or null",
    "grievance_text": "string or null",
    "permissions_text": "string or null",
    "ocr_confidence": 0.92
  },
  "cost_receipt": {
    "sanctioned_amount": 100000,
    "net_disbursal": 92000,
    "fees": [
      { "name": "processing_fee", "amount": 5000 }
    ],
    "total_repayment": 103500,
    "schedule": [
      { "month": 1, "amount": 8500 }
    ],
    "estimated_annualised_cost": 0.21,
    "assumptions": ["..."],
    "limitations": ["..."]
  },
  "compliance_receipt": [
    {
      "rule_id": "KFS-01",
      "status": "Pass",
      "evidence_text": "...",
      "reason_text": "..."
    }
  ],
  "action_receipt": {
    "dla_status": "listed_association_found",
    "snapshot_date": "2025-05-08",
    "next_steps": ["..."],
    "complaint_draft": "string or null"
  }
}
```

## Notes

- No LLM-computed math is used in the core cost engine.
- No fraud or legality verdict is emitted by the backend.
- The backend never says an app is "RBI-approved".
- All compliance and action output is evidence-led and deterministic.

## Deployment

The SAM template is in `template.yaml` and can be packaged and deployed with:

```bash
sam build
sam deploy --guided
```

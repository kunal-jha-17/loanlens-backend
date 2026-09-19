# LoanLens Backend (PRD-Bounded MVP)

LoanLens backend is a deterministic FastAPI + AWS SAM service for educational loan-document analysis.

## Safety and scope guarantees

- Deterministic math only (no LLM-computed numbers).
- No fraud/legality verdicts; outputs are evidence-led and "verify with lender" where needed.
- DLA outcomes are limited to:
  - `listed_association_found`
  - `not_found_in_snapshot`
  - `unable_to_verify`
- DLA lookup uses a dated synthetic snapshot, not a live regulator API.
- Escalation output is draft-only and never auto-submitted.
- Uses synthetic/redacted fixtures only.
- Bedrock/Strands is **not** used to compute numbers or rule outcomes.

## API contract

Required response sections are preserved:

- `extraction`
- `cost_receipt`
- `compliance_receipt`
- `action_receipt`

Additional bounded fields:

- `global_disclaimer` (exact required PRD disclaimer)
- `processing_warnings`

Endpoints:

- `GET /health`
- `GET /loanlens/mock`
- `POST /loanlens/process`

## Local development

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
pytest -q
python -m compileall app functions tests
```

## SAM deployment prerequisites

- AWS SAM CLI
- AWS credentials with permissions for Lambda, API Gateway, S3, DynamoDB, Step Functions, IAM

Validate template locally:

```bash
python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('template.yaml').read_text())"
sam validate
```

## Seed commands (synthetic data)

Rules and DLA snapshot data:

```bash
python scripts/seed_dynamodb.py
```

Seed inputs come from:

- `data/rules_seed.json`
- `data/dla_snapshot_2026-09-01.json`

## Architecture summary

1. API receives an already-extracted payload (`/loanlens/process`) or returns synthetic mock (`/loanlens/mock`).
2. Fixed sequence orchestration runs:
   - deterministic finance engine
   - rules evaluator (8 fixed IDs)
   - DLA snapshot lookup with alias matching
   - draft-only escalation routing
3. PII masking utility is available before logs/storage.
4. S3 upload bucket triggers extraction Lambda with Textract boundary:
   - AWS adapter starts async Textract job
   - deterministic fake adapter is used for local tests

## Known limitations (honest MVP boundaries)

- AWS Textract adapter currently starts async jobs but does not implement full job-result polling.
- DynamoDB reads in runtime path are currently represented by local deterministic snapshot loading for core logic.
- Escalation state machine is bounded routing scaffolding and does not send any external complaints/messages.
- No authentication, payments, lender onboarding, credit decisioning, or generic chat APIs are implemented.

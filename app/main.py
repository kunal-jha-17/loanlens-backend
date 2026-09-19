from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.mock_data import build_mock_response
from app.models import LoanLensInput, LoanLensResponse
from app.services.orchestrator import CriticalFieldError, process_extraction

app = FastAPI(title="LoanLens Backend", version="0.2.0")

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
def process_loanfile(payload: LoanLensInput) -> LoanLensResponse:
    try:
        return process_extraction(payload.extraction)
    except CriticalFieldError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

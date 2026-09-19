from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RepaymentEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    month: int = Field(..., ge=1)
    amount: float = Field(..., gt=0)


class Fee(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    amount: float = Field(..., gt=0)


class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lender_name: str
    sanctioned_amount: float = Field(..., gt=0)
    net_disbursal: float = Field(..., gt=0)
    fees: list[Fee] = Field(default_factory=list)
    tenure: int = Field(..., gt=0)
    repayment_schedule: list[RepaymentEntry] = Field(default_factory=list)
    nominal_rate: float = 0.0
    stated_apr: float | None = None
    cooling_off_text: str | None = None
    grievance_text: str | None = None
    permissions_text: str | None = None
    ocr_confidence: float = Field(ge=0.0, le=1.0)


class CostReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sanctioned_amount: float
    net_disbursal: float
    fees: list[Fee]
    total_repayment: float
    schedule: list[RepaymentEntry]
    estimated_annualised_cost: float
    assumptions: list[str]
    limitations: list[str]


class ComplianceRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str
    status: Literal["Pass", "Missing", "Needs verification", "Potential concern"]
    evidence_text: str
    reason_text: str


class ActionReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dla_status: Literal["listed_association_found", "not_found_in_snapshot", "unable_to_verify"]
    snapshot_date: str
    next_steps: list[str]
    complaint_draft: str | None = None


class LoanLensResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    extraction: Extraction
    cost_receipt: CostReceipt
    compliance_receipt: list[ComplianceRule]
    action_receipt: ActionReceipt


class LoanLensInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    extraction: Extraction

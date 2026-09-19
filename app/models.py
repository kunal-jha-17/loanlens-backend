from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RuleStatus = Literal["Pass", "Missing", "Needs verification", "Potential concern"]
DlaStatus = Literal["listed_association_found", "not_found_in_snapshot", "unable_to_verify"]
DraftType = Literal["grievance_officer", "sachet_cybercrime"]


class RepaymentEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    month: int = Field(..., ge=1)
    amount: float = Field(..., gt=0)


class Fee(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    amount: float = Field(..., ge=0)


class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lender_name: str | None = None
    sanctioned_amount: float | None = Field(default=None, gt=0)
    net_disbursal: float | None = Field(default=None, gt=0)
    fees: list[Fee] = Field(default_factory=list)
    tenure: int | None = Field(default=None, gt=0)
    repayment_schedule: list[RepaymentEntry] = Field(default_factory=list)
    nominal_rate: float | None = None
    stated_apr: float | None = None
    cooling_off_text: str | None = None
    grievance_text: str | None = None
    permissions_text: str | None = None
    repayment_account_text: str | None = None
    ocr_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    field_confidence: dict[str, float] = Field(default_factory=dict)


class CostReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sanctioned_amount: float | None
    net_disbursal: float | None
    fees: list[Fee]
    total_repayment: float | None
    schedule: list[RepaymentEntry]
    estimated_annualised_cost: float | None
    apr_vs_computed_note: str
    assumptions: list[str]
    limitations: list[str]


class ComplianceRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    status: RuleStatus
    evidence_text: str
    reason_text: str


class ActionReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dla_status: DlaStatus
    snapshot_date: str
    snapshot_notice: str
    next_steps: list[str]
    complaint_draft: str | None = None
    draft_type: DraftType | None = None
    evidence_pack: dict[str, Any] = Field(default_factory=dict)


class LoanLensResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extraction: Extraction
    cost_receipt: CostReceipt
    compliance_receipt: list[ComplianceRule]
    action_receipt: ActionReceipt
    global_disclaimer: str
    processing_warnings: list[str] = Field(default_factory=list)


class LoanLensInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extraction: Extraction

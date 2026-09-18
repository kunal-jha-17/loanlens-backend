from __future__ import annotations

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class Fee(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    amount: float


class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lender_name: str
    sanctioned_amount: float
    net_disbursal: float
    fees: list[Fee]
    tenure: int
    repayment_schedule: list[dict[str, Any]]
    nominal_rate: float
    stated_apr: Optional[float] = None
    cooling_off_text: Optional[str] = None
    grievance_text: Optional[str] = None
    permissions_text: Optional[str] = None
    ocr_confidence: float = Field(ge=0.0, le=1.0)


class CostReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sanctioned_amount: float
    net_disbursal: float
    fees: list[Fee]
    total_repayment: float
    schedule: list[dict[str, Any]]
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
    complaint_draft: Optional[str] = None


class LoanLensResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    extraction: Extraction
    cost_receipt: CostReceipt
    compliance_receipt: list[ComplianceRule]
    action_receipt: ActionReceipt

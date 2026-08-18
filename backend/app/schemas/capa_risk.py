from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ComplaintSummaryInfo(BaseModel):
    """Technical executive summary of the reported complaint."""
    executive_summary: str = Field(..., description="High-level technical summary of reported complaint")
    defect_impact: str = Field(..., description="Impact on product quality and patient safety")
    batch_scope: str = Field(..., description="Affected batch/lot scope evaluation")
    customer_risk: str = Field(..., description="Risk level for reporting entity / healthcare providers")


class RiskClassificationInfo(BaseModel):
    """Multi-dimensional AI Risk Matrix evaluation."""
    severity_level: str = Field(..., description="Initial severity: CRITICAL, MAJOR, or MINOR")
    occurrence_probability: str = Field(..., description="Probability tier: HIGH, MEDIUM, or LOW")
    detection_difficulty: str = Field(..., description="Detection tier: HARD, MODERATE, or EASY")
    rpn_score: float = Field(..., description="Risk Priority Number (1.0 to 100.0)")
    health_hazard_class: str = Field(..., description="FDA/EMA Health Hazard Class: CLASS_I, CLASS_II, or CLASS_III")
    risk_explanation: str = Field(..., description="Technical explanation of the risk classification")


class CapaItemDetail(BaseModel):
    """Detailed CAPA action item with target timelines and effectiveness criteria."""
    capa_id: str = Field(..., description="Unique CAPA reference ID (e.g. CAPA-01)")
    action_type: str = Field(..., description="Action type: CORRECTIVE or PREVENTIVE")
    title: str = Field(..., description="Short title of the CAPA item")
    description: str = Field(..., description="Detailed description of corrective/preventive measure")
    owner_department: str = Field(..., description="Responsible department (e.g. QA, QC, Production, Maintenance)")
    target_timeline_days: int = Field(default=30, description="Target completion timeline in days")
    effectiveness_verification_plan: str = Field(..., description="GMP effectiveness verification criteria")


class CapaRiskAssessmentRequest(BaseModel):
    """Request schema for evaluating CAPA recommendations and AI risk classification."""
    form_data: Dict[str, Any] = Field(..., description="Complaint payload dictionary")
    complaint_id: Optional[int] = Field(default=None, description="Optional ID of saved complaint")


class CapaRiskAssessmentResponse(BaseModel):
    """Unified response containing Complaint Summary, Risk Classification, and CAPA Plan."""
    complaint_summary: ComplaintSummaryInfo = Field(..., description="Executive summary section")
    risk_classification: RiskClassificationInfo = Field(..., description="AI Risk matrix classification section")
    capa_plan: List[CapaItemDetail] = Field(default_factory=list, description="Actionable CAPA plan items")
    gmp_audit_readiness_notes: str = Field(..., description="GMP & Regulatory compliance readiness notes")

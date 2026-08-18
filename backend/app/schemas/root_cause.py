from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RootCauseHypothesis(BaseModel):
    """Pydantic model representing a potential root cause hypothesis."""
    category: str = Field(..., description="Ishikawa category (e.g. Machine / Equipment, Material Defect, Method / Process)")
    title: str = Field(..., description="Short title of the probable cause")
    description: str = Field(..., description="Technical explanation of the potential failure mechanism")
    confidence_level: str = Field(..., description="Confidence tier: HIGH, MEDIUM, or LOW")
    likelihood_score: float = Field(..., description="Percentage likelihood score (0 to 100)")


class InvestigationStep(BaseModel):
    """Pydantic model for recommended QA/QC investigation checklist item."""
    step_number: int = Field(..., description="Sequential step number")
    action: str = Field(..., description="Specific investigation action item")
    department: str = Field(..., description="Responsible department (e.g. QC Lab, Production, Maintenance, QA)")
    priority: str = Field(..., description="Priority tier: CRITICAL, HIGH, or MEDIUM")


class CapaRecommendation(BaseModel):
    """Pydantic model for recommended CAPA item."""
    action_type: str = Field(..., description="Type: CORRECTIVE or PREVENTIVE")
    title: str = Field(..., description="Short title of the action")
    description: str = Field(..., description="Detailed description of corrective or preventive measure")
    target_timeline_days: int = Field(default=30, description="Recommended completion timeline in days")


class RootCauseRecommendationRequest(BaseModel):
    """Schema requesting AI root cause recommendation for a complaint payload."""
    complaint_id: Optional[int] = Field(default=None, description="Optional database ID of saved complaint")
    form_data: Dict[str, Any] = Field(..., description="Complaint attributes dictionary")


class RootCauseRecommendationResponse(BaseModel):
    """Schema returning root cause analysis, investigation checklist, and CAPA recommendations."""
    summary_assessment: str = Field(..., description="Executive QA summary of probable root causes")
    suggested_root_cause_category: str = Field(..., description="Primary recommended root cause category")
    hypotheses: List[RootCauseHypothesis] = Field(default_factory=list, description="Ranked list of root cause hypotheses")
    investigation_checklist: List[InvestigationStep] = Field(default_factory=list, description="Recommended investigation steps")
    capa_recommendations: List[CapaRecommendation] = Field(default_factory=list, description="Suggested CAPA measures")


class UpdateComplaintRcaCapaRequest(BaseModel):
    """Schema for updating RCA & CAPA fields on a saved complaint record."""
    root_cause_category: Optional[str] = Field(default=None, description="Selected root cause category")
    investigation_findings: Optional[str] = Field(default=None, description="Detailed investigation findings text")
    capa_required: bool = Field(default=False, description="Whether formal CAPA is required")
    capa_details: Optional[str] = Field(default=None, description="Detailed CAPA plan text")

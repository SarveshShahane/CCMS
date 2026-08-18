from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MissingFieldDetail(BaseModel):
    """Details regarding a missing required or recommended field."""
    field: str = Field(..., description="Key name of the field")
    label: str = Field(..., description="Human readable title for UI display")
    category: str = Field(..., description="Field severity category: critical, important, or optional")
    suggestion: str = Field(..., description="Actionable suggestion or tip to retrieve this field")


class CompletenessCheckRequest(BaseModel):
    """Schema for requesting a completeness check on raw/draft complaint form data."""
    form_data: Dict[str, Any] = Field(..., description="Dictionary of complaint fields")
    generate_email: bool = Field(default=False, description="Whether to invoke LLM to generate customer clarification email")


class CompletenessCheckResponse(BaseModel):
    """Schema returning completeness evaluation metrics and missing fields breakdown."""
    completeness_score: float = Field(..., description="Overall completeness percentage (0 to 100)")
    status: str = Field(..., description="Status tier: INCOMPLETE, PARTIALLY_COMPLETE, or READY_FOR_INVESTIGATION")
    is_ready_for_investigation: bool = Field(..., description="True if score >= 80 and zero critical fields missing")
    
    missing_critical: List[MissingFieldDetail] = Field(default_factory=list, description="Missing critical mandatory fields")
    missing_important: List[MissingFieldDetail] = Field(default_factory=list, description="Missing important regulatory fields")
    missing_optional: List[MissingFieldDetail] = Field(default_factory=list, description="Missing supplementary context fields")
    
    total_missing_count: int = Field(default=0, description="Total count of missing fields across all categories")
    suggested_followup_email: Optional[str] = Field(default=None, description="Generated email draft requesting missing details")

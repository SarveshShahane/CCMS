from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DuplicateMatch(BaseModel):
    """Details of an existing complaint record matching the target payload."""
    complaint_id: int = Field(..., description="Database ID of matched complaint")
    complaint_number: str = Field(..., description="Complaint reference number (e.g. CMP-8A3F)")
    product_name: Optional[str] = Field(default=None, description="Product name")
    batch_number: Optional[str] = Field(default=None, description="Batch/Lot number")
    title: Optional[str] = Field(default=None, description="Complaint summary title")
    status: str = Field(..., description="Current status of matched complaint")
    initial_severity: Optional[str] = Field(default=None, description="Initial severity rating")
    similarity_score: float = Field(..., description="Weighted similarity score (0 to 100)")
    match_tier: str = Field(..., description="Tier: HIGH_CONFIDENCE_DUPLICATE or POTENTIAL_RELATED_COMPLAINT")
    matched_fields: List[str] = Field(default_factory=list, description="List of matching attributes (e.g. batch_number, product_name)")


class DuplicateCheckRequest(BaseModel):
    """Request schema for checking duplicate complaints against draft form data."""
    form_data: Dict[str, Any] = Field(..., description="Complaint payload dictionary")
    exclude_complaint_id: Optional[int] = Field(default=None, description="Optional ID of complaint to exclude from self-matching")


class DuplicateCheckResponse(BaseModel):
    """Response schema returning duplicate matches and recommended action."""
    has_duplicates: bool = Field(..., description="True if any match score >= 50%")
    highest_similarity_score: float = Field(..., description="Highest similarity score percentage among matches")
    total_matches_count: int = Field(default=0, description="Total count of candidate matches found")
    duplicate_matches: List[DuplicateMatch] = Field(default_factory=list, description="List of matching complaints sorted by similarity")
    recommended_action: str = Field(..., description="Suggested QA action (e.g. Link to Batch Investigation #CMP-XXXX)")

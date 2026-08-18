from datetime import date, datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, ConfigDict


class ComplaintCreate(BaseModel):
    """Schema for creating a new pharmaceutical complaint."""
    complaint_source: Optional[str] = Field(default="Pharmacy", description="Source type (e.g. Pharmacy, Hospital, Patient)")
    customer_name: Optional[str] = Field(default=None, description="Customer or entity name")
    customer_contact_email: Optional[str] = Field(default=None, description="Contact email")
    customer_contact_phone: Optional[str] = Field(default=None, description="Contact phone")
    
    product_name: Optional[str] = Field(default=None, description="Full product name")
    product_code: Optional[str] = Field(default=None, description="Product code or SKU")
    dosage_form: Optional[str] = Field(default=None, description="Form of product (Capsules, Tablets, etc.)")
    product_strength: Optional[str] = Field(default=None, description="Dosage strength (e.g. 500 mg)")
    batch_number: Optional[str] = Field(default=None, description="Batch or lot identification number")
    
    affected_quantity: float = Field(default=1.0, description="Numerical affected quantity")
    affected_quantity_unit: str = Field(default="units", description="Unit of measure")
    
    originating_site_block: Optional[str] = Field(default=None, description="Manufacturing site/block")
    impacted_npm: Optional[str] = Field(default=None, description="Impacted non-product material")
    
    complaint_category: Optional[str] = Field(default=None, description="Primary defect category")
    title: Optional[str] = Field(default=None, description="Short summary title")
    description: Optional[str] = Field(default=None, description="Detailed problem description")
    sample_received: bool = Field(default=False, description="Whether physical sample was received")
    
    initial_severity: Optional[str] = Field(default=None, description="Initial severity rating (Critical, Major, Minor)")
    suggested_severity: Optional[str] = Field(default=None, description="AI suggested severity")
    priority: Optional[str] = Field(default=None, description="Priority rating")
    ai_risk_assessment: Optional[str] = Field(default=None, description="AI Risk Assessment summary")
    ai_suggested_next_action: Optional[str] = Field(default=None, description="AI suggested next steps")
    ai_extra_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw extracted JSON data")
    
    incident_date: Optional[Union[str, date]] = Field(default=None, description="Incident date (e.g. 2026-08-15, March 2026, 2026)")
    manufacturing_date: Optional[Union[str, date]] = Field(default=None, description="Manufacturing date (e.g. 2026-03-01, Jan 2026, 2026)")
    expiry_date: Optional[Union[str, date]] = Field(default=None, description="Expiry date (e.g. 2028-02-28, March 2028, 2028)")


class ComplaintResponse(BaseModel):
    """Schema for returning detailed complaint metadata."""
    id: int
    complaint_number: str
    status: str
    
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    customer_contact_email: Optional[str] = None
    customer_contact_phone: Optional[str] = None
    
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    dosage_form: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    
    affected_quantity: float
    affected_quantity_unit: str
    
    complaint_category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    sample_received: bool
    
    initial_severity: Optional[str] = None
    ai_risk_assessment: Optional[str] = None
    ai_suggested_next_action: Optional[str] = None
    
    incident_date: Optional[Union[str, date]] = None
    complaint_date: date
    manufacturing_date: Optional[Union[str, date]] = None
    expiry_date: Optional[Union[str, date]] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplaintListResponse(BaseModel):
    """Schema for paginated complaint list responses."""
    items: List[ComplaintResponse]
    total: int
    skip: int
    limit: int

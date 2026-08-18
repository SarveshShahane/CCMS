from datetime import date, datetime
from typing import Optional, Dict, Any

from sqlalchemy import (
    String,
    Text,
    Float,
    Boolean,
    Date,
    DateTime,
    Integer,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.config.db import Base


class Complaint(Base):
    """
    Pharmaceutical Customer Complaint Database Model.
    
    Designed with flexible string inputs rather than strict ENUM constraints
    to seamlessly handle dynamic UI drop-downs, free text, and AI extractions.
    Includes base defaults for quantity measures and full date tracking fields.
    """
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complaint_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="NEW", index=True, nullable=False)

    complaint_source: Mapped[Optional[str]] = mapped_column(String(100), default="Pharmacy", nullable=True)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    product_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    product_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    dosage_form: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    product_strength: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    affected_quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    affected_quantity_unit: Mapped[str] = mapped_column(String(50), default="units", nullable=False)
    normalized_quantity: Mapped[Optional[float]] = mapped_column(Float, default=1.0, nullable=True)

    originating_site_block: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) 
    impacted_npm: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)            

    complaint_category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sample_received: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    initial_severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)      
    suggested_severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)     
    priority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)               
    ai_risk_assessment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)         
    ai_suggested_next_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    root_cause_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    investigation_findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    capa_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    capa_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    incident_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    complaint_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    manufacturing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    sample_received_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    investigation_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    investigation_completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    capa_target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    capa_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    resolved_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
import random
import string
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint
from app.schemas.complaint import ComplaintCreate


from datetime import date, datetime
import re

def parse_flexible_date(val: Optional[str]) -> Optional[date]:
    """Helper to parse full date (YYYY-MM-DD), month-year (March 2026, 03/2026), or year (2026)."""
    if not val or not str(val).strip():
        return None
    val_str = str(val).strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', val_str):
        try:
            return datetime.strptime(val_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$', val_str):
        for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y'):
            try:
                return datetime.strptime(val_str, fmt).date()
            except ValueError:
                pass
    if re.match(r'^\d{1,2}/\d{4}$', val_str):
        try:
            return datetime.strptime(val_str, '%m/%Y').date()
        except ValueError:
            pass
    for fmt in ('%B %Y', '%b %Y', '%Y-%m'):
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            pass
    if re.match(r'^\d{4}$', val_str):
        try:
            return date(int(val_str), 1, 1)
        except ValueError:
            pass
    return None


class ComplaintRepository:
    """Repository layer managing database queries for Complaint entities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_unique_complaint_number(self) -> str:
        """Generates unique complaint number string e.g. CMP-20260818-8A3F."""
        date_str = func.to_char(func.now(), "YYYYMMDD")
        while True:
            random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            complaint_num = f"CMP-{random_suffix}"
            stmt = select(Complaint).where(Complaint.complaint_number == complaint_num)
            res = await self.db.execute(stmt)
            if not res.scalar_one_or_none():
                return complaint_num

    async def create(self, data: ComplaintCreate) -> Complaint:
        """Persists a new complaint record into the database."""
        complaint_num = await self.generate_unique_complaint_number()
        
        db_complaint = Complaint(
            complaint_number=complaint_num,
            status="NEW",
            complaint_source=data.complaint_source,
            customer_name=data.customer_name,
            customer_contact_email=data.customer_contact_email,
            customer_contact_phone=data.customer_contact_phone,
            product_name=data.product_name,
            product_code=data.product_code,
            dosage_form=data.dosage_form,
            product_strength=data.product_strength,
            batch_number=data.batch_number,
            affected_quantity=data.affected_quantity,
            affected_quantity_unit=data.affected_quantity_unit,
            originating_site_block=data.originating_site_block,
            impacted_npm=data.impacted_npm,
            complaint_category=data.complaint_category,
            title=data.title,
            description=data.description,
            sample_received=data.sample_received,
            initial_severity=data.initial_severity,
            suggested_severity=data.suggested_severity,
            priority=data.priority,
            ai_risk_assessment=data.ai_risk_assessment,
            ai_suggested_next_action=data.ai_suggested_next_action,
            ai_extra_data=data.ai_extra_data,
            incident_date=parse_flexible_date(data.incident_date),
            manufacturing_date=parse_flexible_date(data.manufacturing_date),
            expiry_date=parse_flexible_date(data.expiry_date),
        )
        self.db.add(db_complaint)
        await self.db.commit()
        await self.db.refresh(db_complaint)
        return db_complaint

    async def get_by_id(self, complaint_id: int) -> Optional[Complaint]:
        """Fetches a single complaint by ID."""
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_complaints(self, skip: int = 0, limit: int = 50) -> Tuple[List[Complaint], int]:
        """Lists complaints with pagination."""
        total_stmt = select(func.count(Complaint.id))
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar() or 0

        stmt = select(Complaint).order_by(Complaint.created_at.desc()).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        items = list(res.scalars().all())

        return items, total

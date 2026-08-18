from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.complaint import ComplaintRepository
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
)
from app.models.complaint import Complaint


class ComplaintService:
    """Service layer coordinating business logic for pharmaceutical complaints."""

    def __init__(self, db: AsyncSession):
        self.repo = ComplaintRepository(db)

    async def create_complaint(self, data: ComplaintCreate) -> ComplaintResponse:
        """Validates and creates a new complaint."""
        complaint = await self.repo.create(data)
        return ComplaintResponse.model_validate(complaint)

    async def get_complaint(self, complaint_id: int) -> Optional[ComplaintResponse]:
        """Fetches complaint detail by ID."""
        complaint = await self.repo.get_by_id(complaint_id)
        if not complaint:
            return None
        return ComplaintResponse.model_validate(complaint)

    async def list_complaints(self, skip: int = 0, limit: int = 50) -> ComplaintListResponse:
        """Returns paginated complaint records."""
        items, total = await self.repo.list_complaints(skip=skip, limit=limit)
        return ComplaintListResponse(
            items=[ComplaintResponse.model_validate(c) for c in items],
            total=total,
            skip=skip,
            limit=limit,
        )

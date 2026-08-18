from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.services.complaint import ComplaintService
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
)

router = APIRouter(prefix="/complaints", tags=["Complaints"])


def get_complaint_service(db: AsyncSession = Depends(get_db)) -> ComplaintService:
    """Dependency helper injecting AsyncSession into ComplaintService."""
    return ComplaintService(db)


@router.post(
    "/",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a new complaint record",
    description="Saves a customer complaint into the database with dynamic fields and initial AI risk assessments.",
)
async def create_complaint(
    req: ComplaintCreate,
    service: ComplaintService = Depends(get_complaint_service),
):
    try:
        return await service.create_complaint(req)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create complaint: {str(exc)}",
        )


@router.get(
    "/",
    response_model=ComplaintListResponse,
    status_code=status.HTTP_200_OK,
    summary="List complaints",
    description="Returns a paginated list of submitted complaints.",
)
async def list_complaints(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    service: ComplaintService = Depends(get_complaint_service),
):
    return await service.list_complaints(skip=skip, limit=limit)


@router.get(
    "/{complaint_id}",
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
    summary="Get complaint details",
    description="Fetches detailed complaint metadata by ID.",
)
async def get_complaint(
    complaint_id: int,
    service: ComplaintService = Depends(get_complaint_service),
):
    complaint = await service.get_complaint(complaint_id=complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found.",
        )
    return complaint

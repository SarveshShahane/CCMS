from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.services.complaint import ComplaintService
from app.services.completeness import CompletenessService
from app.services.root_cause import RootCauseService
from app.services.duplicate_detection import DuplicateDetectionService
from app.services.capa_risk import CapaRiskService
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
)
from app.schemas.completeness import (
    CompletenessCheckRequest,
    CompletenessCheckResponse,
)
from app.schemas.root_cause import (
    RootCauseRecommendationRequest,
    RootCauseRecommendationResponse,
    UpdateComplaintRcaCapaRequest,
)
from app.schemas.duplicate_detection import (
    DuplicateCheckRequest,
    DuplicateCheckResponse,
)
from app.schemas.capa_risk import (
    CapaRiskAssessmentRequest,
    CapaRiskAssessmentResponse,
)

router = APIRouter(prefix="/complaints", tags=["Complaints"])


def get_complaint_service(db: AsyncSession = Depends(get_db)) -> ComplaintService:
    """Dependency helper injecting AsyncSession into ComplaintService."""
    return ComplaintService(db)


@router.post(
    "/evaluate-capa-risk",
    response_model=CapaRiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate CAPA recommendations and AI Risk Classification",
    description="Generates executive complaint summary, multi-dimensional AI risk classification (RPN, Health Hazard Class), and actionable CAPA plan.",
)
async def evaluate_capa_risk(
    req: CapaRiskAssessmentRequest,
):
    service = CapaRiskService()
    return await service.evaluate_capa_and_risk(req.form_data)


@router.post(
    "/check-duplicates",
    response_model=DuplicateCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check potential duplicate complaints",
    description="Evaluates draft complaint payload against saved database records to detect duplicate reports and batch defect clusters.",
)
async def check_duplicate_complaints(
    req: DuplicateCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DuplicateDetectionService(db)
    return await service.check_duplicates(req.form_data, exclude_id=req.exclude_complaint_id)


@router.post(
    "/recommend-root-cause",
    response_model=RootCauseRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Recommend root causes and investigation checklist",
    description="Runs AI Root Cause Analysis (Ishikawa 5M+E framework) on complaint payload and returns probable root causes, QA investigation checklist, and suggested CAPAs.",
)
async def recommend_root_cause(
    req: RootCauseRecommendationRequest,
):
    service = RootCauseService()
    return await service.analyze_root_cause(req.form_data)


@router.post(
    "/check-completeness",
    response_model=CompletenessCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check complaint completeness and missing fields",
    description="Evaluates draft or existing complaint data against GMP completeness criteria and optionally generates follow-up email drafts.",
)
async def check_complaint_completeness(
    req: CompletenessCheckRequest,
):
    service = CompletenessService()
    result = service.evaluate(req.form_data)
    if req.generate_email:
        email_draft = await service.generate_clarification_email(req.form_data, result)
        result.suggested_followup_email = email_draft
    return result


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
    "/{complaint_id}/evaluate-capa-risk",
    response_model=CapaRiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate CAPA and Risk for saved complaint ID",
    description="Fetches saved complaint record and generates executive summary, AI Risk matrix classification, and CAPA plan.",
)
async def evaluate_saved_capa_risk(
    complaint_id: int,
    service: ComplaintService = Depends(get_complaint_service),
):
    complaint = await service.get_complaint(complaint_id=complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found.",
        )
    capa_service = CapaRiskService()
    return await capa_service.evaluate_capa_and_risk(complaint.model_dump())


@router.get(
    "/{complaint_id}/duplicates",
    response_model=DuplicateCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Get duplicate matches for a saved complaint",
    description="Fetches matching duplicate or sibling batch complaints for an existing saved complaint record.",
)
async def get_saved_complaint_duplicates(
    complaint_id: int,
    service: ComplaintService = Depends(get_complaint_service),
    db: AsyncSession = Depends(get_db),
):
    complaint = await service.get_complaint(complaint_id=complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found.",
        )
    dup_service = DuplicateDetectionService(db)
    return await dup_service.check_duplicates(complaint.model_dump(), exclude_id=complaint_id)


@router.post(
    "/{complaint_id}/recommend-root-cause",
    response_model=RootCauseRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Recommend root cause for saved complaint ID",
    description="Fetches saved complaint record and generates AI Root Cause Analysis (Ishikawa framework), investigation checklist, and CAPA recommendations.",
)
async def recommend_root_cause_for_saved(
    complaint_id: int,
    service: ComplaintService = Depends(get_complaint_service),
):
    complaint = await service.get_complaint(complaint_id=complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found.",
        )
    rca_service = RootCauseService()
    return await rca_service.analyze_root_cause(complaint.model_dump())


@router.patch(
    "/{complaint_id}/rca-capa",
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
    summary="Update RCA and CAPA investigation metadata",
    description="Updates root_cause_category, investigation_findings, capa_required, and capa_details on a saved complaint record.",
)
async def update_complaint_rca_capa(
    complaint_id: int,
    req: UpdateComplaintRcaCapaRequest,
    service: ComplaintService = Depends(get_complaint_service),
):
    updated = await service.update_rca_capa(
        complaint_id=complaint_id,
        root_cause_category=req.root_cause_category,
        investigation_findings=req.investigation_findings,
        capa_required=req.capa_required,
        capa_details=req.capa_details,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found.",
        )
    return updated


@router.get(
    "/{complaint_id}/completeness",
    response_model=CompletenessCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Get completeness evaluation for saved complaint",
    description="Fetches completeness score, missing fields breakdown, and generated clarification email for a saved complaint record.",
)
async def get_saved_complaint_completeness(
    complaint_id: int,
    generate_email: bool = Query(True, description="Whether to include generated email draft"),
    service: ComplaintService = Depends(get_complaint_service),
):
    complaint = await service.get_complaint(complaint_id=complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found.",
        )
    comp_service = CompletenessService()
    form_data = complaint.model_dump()
    result = comp_service.evaluate(form_data)
    if generate_email:
        result.suggested_followup_email = await comp_service.generate_clarification_email(form_data, result)
    return result


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





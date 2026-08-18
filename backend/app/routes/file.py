from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    HTTPException,
    status,
)
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.services.file import FileService
from app.schemas.file import (
    FileResponse,
    FileUploadResponse,
    FileListResponse,
    FileDeleteResponse,
)
from app.exceptions.file import (
    FileNotFoundException,
    InvalidFileExtensionException,
    FileTooLargeException,
    FileStorageException,
    FileException,
)

router = APIRouter(prefix="/files", tags=["Files"])


def get_file_service(db: AsyncSession = Depends(get_db)) -> FileService:
    """Dependency helper injecting AsyncSession into FileService."""
    return FileService(db)


def handle_file_exceptions(exc: FileException) -> None:
    """Maps custom domain file exceptions to standard FastAPI HTTP exceptions."""
    if isinstance(exc, FileNotFoundException):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        )
    elif isinstance(exc, InvalidFileExtensionException):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        )
    elif isinstance(exc, FileTooLargeException):
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=exc.message,
        )

    elif isinstance(exc, FileStorageException):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.message,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file attachment",
    description="Uploads a file (PDF, DOCX, TXT, EML up to 10 MB) attached optional complaint_id or chat_id.",
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload (max 10MB)"),
    complaint_id: Optional[int] = Form(None, description="Optional Complaint ID link"),
    chat_id: Optional[int] = Form(None, description="Optional Chat Session ID link"),
    service: FileService = Depends(get_file_service),
):
    try:
        return await service.upload_file(
            file=file,
            complaint_id=complaint_id,
            chat_id=chat_id,
        )
    except FileException as exc:
        handle_file_exceptions(exc)


@router.get(
    "/",
    response_model=FileListResponse,
    status_code=status.HTTP_200_OK,
    summary="List file attachments",
    description="Returns a paginated list of file attachments with optional complaint_id and chat_id filtering.",
)
async def list_files(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    complaint_id: Optional[int] = Query(None, description="Filter by complaint ID"),
    chat_id: Optional[int] = Query(None, description="Filter by chat ID"),
    service: FileService = Depends(get_file_service),
):
    try:
        return await service.list_files(
            skip=skip,
            limit=limit,
            complaint_id=complaint_id,
            chat_id=chat_id,
        )
    except FileException as exc:
        handle_file_exceptions(exc)


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get file metadata",
    description="Fetches detailed metadata of a file attachment by its ID.",
)
async def get_file_metadata(
    file_id: int,
    service: FileService = Depends(get_file_service),
):
    try:
        return await service.get_file_metadata(file_id=file_id)
    except FileException as exc:
        handle_file_exceptions(exc)


@router.get(
    "/{file_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download physical file",
    description="Downloads the physical file content by file ID.",
)
async def download_file(
    file_id: int,
    service: FileService = Depends(get_file_service),
):
    try:
        file_path, filename, content_type = await service.get_file_for_download(file_id=file_id)
        return FastAPIFileResponse(
            path=str(file_path),
            filename=filename,
            media_type=content_type,
        )
    except FileException as exc:
        handle_file_exceptions(exc)


@router.delete(
    "/{file_id}",
    response_model=FileDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete file attachment",
    description="Deletes file attachment record from database and removes physical file from disk storage.",
)
async def delete_file(
    file_id: int,
    service: FileService = Depends(get_file_service),
):
    try:
        return await service.delete_file(file_id=file_id)
    except FileException as exc:
        handle_file_exceptions(exc)

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class FileBase(BaseModel):
    """Base schema for file attachment data."""
    filename: str = Field(..., description="Original filename uploaded by the user")
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., description="File size in bytes")
    extension: str = Field(..., description="File extension without dot (e.g. pdf, docx, txt, eml)")
    complaint_id: Optional[int] = Field(None, description="ID of associated complaint, if any")
    chat_id: Optional[int] = Field(None, description="ID of associated chat session, if any")


class FileResponse(FileBase):
    """Schema representing file metadata response."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique file ID")
    stored_filename: str = Field(..., description="Unique internal storage filename")
    file_path: str = Field(..., description="Server relative storage path")
    status: str = Field("PENDING", description="Background processing status: PENDING, PROCESSING, COMPLETED, FAILED")
    extracted_text: Optional[str] = Field(None, description="Extracted text from PDF or document")
    processing_error: Optional[str] = Field(None, description="Error message if background processing failed")
    created_at: datetime = Field(..., description="Timestamp when file was uploaded")
    updated_at: datetime = Field(..., description="Timestamp when file record was last updated")


class FileUploadResponse(FileResponse):
    """Schema for upload operation response."""
    pass


class FileListResponse(BaseModel):
    """Schema for paginated list of file attachments."""
    items: List[FileResponse] = Field(default_factory=list, description="List of file attachment records")
    total: int = Field(..., description="Total count of files matching filter")
    skip: int = Field(0, description="Number of skipped items")
    limit: int = Field(50, description="Maximum number of items returned")


class FileDeleteResponse(BaseModel):
    """Schema for file deletion confirmation."""
    id: int = Field(..., description="ID of deleted file")
    message: str = Field(..., description="Status message")
    deleted: bool = Field(True, description="Deletion success indicator")

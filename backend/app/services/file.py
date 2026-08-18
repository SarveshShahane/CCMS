import asyncio
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import FileAttachment
from app.repositories.file import FileRepository
from app.schemas.file import FileResponse, FileListResponse, FileDeleteResponse
from app.jobs.worker import enqueue_file_processing
from app.exceptions.file import (
    FileNotFoundException,
    InvalidFileExtensionException,
    FileTooLargeException,
    FileStorageException,
)


class FileService:
    """Manages file uploads, size validation, storage, and background text parsing."""

    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "eml"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  

    def __init__(self, db: AsyncSession, upload_dir: Optional[Path | str] = None):
        self.db = db
        self.repository = FileRepository(db)
        self.upload_dir = Path(upload_dir or "uploads/files")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_extension(self, filename: str) -> str:
        """Extracts lowercase file extension without dot."""
        if "." in filename:
            return filename.rsplit(".", 1)[-1].lower().strip()
        return ""

    async def upload_file(
        self,
        file: UploadFile,
        complaint_id: Optional[int] = None,
        chat_id: Optional[int] = None,
    ) -> FileResponse:
        """Validates, stores file on disk, and queues background processing."""
        original_filename = file.filename or "unnamed_file"
        extension = self._get_extension(original_filename)

        if extension not in self.ALLOWED_EXTENSIONS:
            raise InvalidFileExtensionException(extension, self.ALLOWED_EXTENSIONS)

        content = await file.read()
        file_size = len(content)

        if file_size > self.MAX_FILE_SIZE:
            raise FileTooLargeException(file_size, self.MAX_FILE_SIZE)

        stored_filename = f"{uuid.uuid4().hex}.{extension}"
        target_path = self.upload_dir / stored_filename

        try:
            await asyncio.to_thread(target_path.write_bytes, content)
        except Exception as exc:
            raise FileStorageException(f"Failed to write file to storage: {str(exc)}") from exc

        file_record = FileAttachment(
            filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(target_path),
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            extension=extension,
            status="PENDING",
            complaint_id=complaint_id,
            chat_id=chat_id,
        )

        saved_file = await self.repository.create(file_record)

        await enqueue_file_processing(saved_file.id)

        return FileResponse.model_validate(saved_file)

    async def get_file_metadata(self, file_id: int) -> FileResponse:
        """Retrieve file metadata by file ID."""
        file_record = await self.repository.get_by_id(file_id)
        if not file_record:
            raise FileNotFoundException(file_id)
        return FileResponse.model_validate(file_record)

    async def get_file_for_download(self, file_id: int) -> Tuple[Path, str, str]:
        """
        Retrieve physical file path, original filename, and content-type for download.
        """
        file_record = await self.repository.get_by_id(file_id)
        if not file_record:
            raise FileNotFoundException(file_id)

        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise FileStorageException(f"Physical file missing on server for ID {file_id}.")

        return file_path, file_record.filename, file_record.content_type

    async def list_files(
        self,
        skip: int = 0,
        limit: int = 50,
        complaint_id: Optional[int] = None,
        chat_id: Optional[int] = None,
    ) -> FileListResponse:
        """List file attachment records with optional filtering and pagination."""
        items = await self.repository.get_all(
            skip=skip,
            limit=limit,
            complaint_id=complaint_id,
            chat_id=chat_id,
        )
        total = await self.repository.count(
            complaint_id=complaint_id,
            chat_id=chat_id,
        )

        return FileListResponse(
            items=[FileResponse.model_validate(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def delete_file(self, file_id: int) -> FileDeleteResponse:
        """
        Delete file attachment record and remove physical file from disk.
        """
        file_record = await self.repository.get_by_id(file_id)
        if not file_record:
            raise FileNotFoundException(file_id)

        file_path = Path(file_record.file_path)

        if file_path.exists():
            try:
                await asyncio.to_thread(file_path.unlink, True)
            except Exception as exc:
                raise FileStorageException(f"Failed to delete file from disk: {str(exc)}") from exc

        await self.repository.delete(file_record)

        return FileDeleteResponse(
            id=file_id,
            message=f"File ID {file_id} deleted successfully.",
            deleted=True,
        )

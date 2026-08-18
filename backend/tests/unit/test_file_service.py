from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile

from app.services.file import FileService
from app.models.file import FileAttachment
from app.exceptions.file import (
    FileNotFoundException,
    InvalidFileExtensionException,
    FileTooLargeException,
)


@pytest.mark.asyncio
async def test_upload_invalid_extension(tmp_path):
    mock_db = AsyncMock()
    service = FileService(db=mock_db, upload_dir=tmp_path)

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "malicious.exe"

    with pytest.raises(InvalidFileExtensionException) as exc_info:
        await service.upload_file(file=mock_file)

    assert "exe" in str(exc_info.value)


@pytest.mark.asyncio
async def test_upload_file_too_large(tmp_path):
    mock_db = AsyncMock()
    service = FileService(db=mock_db, upload_dir=tmp_path)

    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "large_doc.pdf"
    mock_file.read.return_value = b"0" * (11 * 1024 * 1024)

    with pytest.raises(FileTooLargeException) as exc_info:
        await service.upload_file(file=mock_file)

    assert "11.00 MB" in str(exc_info.value)


@pytest.mark.asyncio
async def test_upload_valid_file_success(tmp_path):
    mock_db = AsyncMock()
    service = FileService(db=mock_db, upload_dir=tmp_path)

    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test_complaint.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read.return_value = b"PDF dummy content"

    now = datetime.now(timezone.utc)
    created_record = FileAttachment(
        id=1,
        filename="test_complaint.pdf",
        stored_filename="uuid_test.pdf",
        file_path=str(tmp_path / "uuid_test.pdf"),
        content_type="application/pdf",
        file_size=len(b"PDF dummy content"),
        extension="pdf",
        complaint_id=10,
        chat_id=None,
        created_at=now,
        updated_at=now,
    )
    service.repository.create = AsyncMock(return_value=created_record)

    response = await service.upload_file(file=mock_file, complaint_id=10)

    assert response.id == 1
    assert response.filename == "test_complaint.pdf"
    assert response.extension == "pdf"
    assert response.complaint_id == 10
    service.repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_file_metadata_not_found():
    mock_db = AsyncMock()
    service = FileService(db=mock_db)
    service.repository.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(FileNotFoundException):
        await service.get_file_metadata(file_id=999)


@pytest.mark.asyncio
async def test_delete_file_success(tmp_path):
    mock_db = AsyncMock()
    service = FileService(db=mock_db, upload_dir=tmp_path)

    test_file_path = tmp_path / "sample.pdf"
    test_file_path.write_bytes(b"content")

    now = datetime.now(timezone.utc)
    record = FileAttachment(
        id=5,
        filename="sample.pdf",
        stored_filename="sample.pdf",
        file_path=str(test_file_path),
        content_type="application/pdf",
        file_size=7,
        extension="pdf",
        created_at=now,
        updated_at=now,
    )
    service.repository.get_by_id = AsyncMock(return_value=record)
    service.repository.delete = AsyncMock(return_value=True)

    result = await service.delete_file(file_id=5)

    assert result.deleted is True
    assert not test_file_path.exists()

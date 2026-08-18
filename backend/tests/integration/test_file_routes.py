import io
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from main import app
from app.routes.file import get_file_service
from app.services.file import FileService
from app.models.file import FileAttachment


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def file_service(mock_db, tmp_path):
    """Instantiate FileService with a mock database and temporary directory."""
    return FileService(db=mock_db, upload_dir=tmp_path)


@pytest.fixture
def async_client(file_service):
    """FastAPI AsyncClient fixture overriding get_file_service dependency."""
    app.dependency_overrides[get_file_service] = lambda: file_service
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_file_success(async_client, file_service, tmp_path, monkeypatch):
    """Test successful upload of a valid file via POST /api/v1/files/upload."""
    monkeypatch.setattr("app.services.file.enqueue_file_processing", AsyncMock(return_value="job_123"))
    now = datetime.now(timezone.utc)
    mock_file_record = FileAttachment(
        id=101,
        filename="complaint_report.pdf",
        stored_filename="uuid_101.pdf",
        file_path=str(tmp_path / "uuid_101.pdf"),
        content_type="application/pdf",
        file_size=128,
        extension="pdf",
        status="PENDING",
        complaint_id=42,
        chat_id=None,
        created_at=now,
        updated_at=now,
    )
    file_service.repository.create = AsyncMock(return_value=mock_file_record)

    file_content = b"%PDF-1.4 sample content"
    files = {"file": ("complaint_report.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"complaint_id": "42"}

    response = await async_client.post("/api/v1/files/upload", files=files, data=data)

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["id"] == 101
    assert json_data["filename"] == "complaint_report.pdf"
    assert json_data["extension"] == "pdf"
    assert json_data["complaint_id"] == 42


@pytest.mark.asyncio
async def test_upload_file_invalid_extension_400(async_client):
    """Test upload rejection with 400 Bad Request for disallowed file extensions."""
    file_content = b"import sys; sys.exit(0)"
    files = {"file": ("script.py", io.BytesIO(file_content), "text/x-python")}

    response = await async_client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 400
    json_data = response.json()
    assert "not allowed" in json_data["detail"].lower()


@pytest.mark.asyncio
async def test_upload_file_too_large_413(async_client):
    """Test upload rejection with 413 Payload Too Large when file size > 10MB."""
    large_content = b"0" * (11 * 1024 * 1024)
    files = {"file": ("large_document.pdf", io.BytesIO(large_content), "application/pdf")}

    response = await async_client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 413
    json_data = response.json()
    assert "exceeds maximum allowed limit" in json_data["detail"].lower()


@pytest.mark.asyncio
async def test_get_file_metadata_success(async_client, file_service, tmp_path):
    """Test GET /api/v1/files/{file_id} returns file metadata."""
    now = datetime.now(timezone.utc)
    mock_record = FileAttachment(
        id=202,
        filename="batch_log.txt",
        stored_filename="uuid_202.txt",
        file_path=str(tmp_path / "uuid_202.txt"),
        content_type="text/plain",
        file_size=64,
        extension="txt",
        status="PENDING",
        complaint_id=15,
        chat_id=None,
        created_at=now,
        updated_at=now,
    )
    file_service.repository.get_by_id = AsyncMock(return_value=mock_record)

    response = await async_client.get("/api/v1/files/202")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["id"] == 202
    assert json_data["filename"] == "batch_log.txt"
    assert json_data["extension"] == "txt"


@pytest.mark.asyncio
async def test_get_file_metadata_not_found_404(async_client, file_service):
    """Test GET /api/v1/files/{file_id} returns 404 for missing file ID."""
    file_service.repository.get_by_id = AsyncMock(return_value=None)

    response = await async_client.get("/api/v1/files/9999")

    assert response.status_code == 404
    json_data = response.json()
    assert "not found" in json_data["detail"].lower()


@pytest.mark.asyncio
async def test_download_file_success(async_client, file_service, tmp_path):
    """Test GET /api/v1/files/{file_id}/download streams the stored file."""
    now = datetime.now(timezone.utc)
    stored_path = tmp_path / "uuid_303.pdf"
    stored_path.write_bytes(b"%PDF-1.4 test download content")

    mock_record = FileAttachment(
        id=303,
        filename="user_download.pdf",
        stored_filename="uuid_303.pdf",
        file_path=str(stored_path),
        content_type="application/pdf",
        file_size=len(b"%PDF-1.4 test download content"),
        extension="pdf",
        status="PENDING",
        created_at=now,
        updated_at=now,
    )
    file_service.repository.get_by_id = AsyncMock(return_value=mock_record)

    response = await async_client.get("/api/v1/files/303/download")

    assert response.status_code == 200
    assert response.content == b"%PDF-1.4 test download content"
    assert "application/pdf" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_list_files_success(async_client, file_service, tmp_path):
    """Test GET /api/v1/files/ returns list of file metadata."""
    now = datetime.now(timezone.utc)
    mock_records = [
        FileAttachment(
            id=1,
            filename="file1.pdf",
            stored_filename="uuid_1.pdf",
            file_path=str(tmp_path / "uuid_1.pdf"),
            content_type="application/pdf",
            file_size=100,
            extension="pdf",
            status="PENDING",
            created_at=now,
            updated_at=now,
        ),
        FileAttachment(
            id=2,
            filename="file2.docx",
            stored_filename="uuid_2.docx",
            file_path=str(tmp_path / "uuid_2.docx"),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=200,
            extension="docx",
            status="PENDING",
            created_at=now,
            updated_at=now,
        ),
    ]
    file_service.repository.get_all = AsyncMock(return_value=mock_records)
    file_service.repository.count = AsyncMock(return_value=2)

    response = await async_client.get("/api/v1/files/?skip=0&limit=50")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 2
    assert len(json_data["items"]) == 2
    assert json_data["items"][0]["id"] == 1
    assert json_data["items"][1]["id"] == 2


@pytest.mark.asyncio
async def test_delete_file_success(async_client, file_service, tmp_path):
    """Test DELETE /api/v1/files/{file_id} removes physical file and database record."""
    now = datetime.now(timezone.utc)
    stored_path = tmp_path / "uuid_404.eml"
    stored_path.write_bytes(b"From: test@example.com")

    mock_record = FileAttachment(
        id=404,
        filename="email_message.eml",
        stored_filename="uuid_404.eml",
        file_path=str(stored_path),
        content_type="message/rfc822",
        file_size=22,
        extension="eml",
        status="PENDING",
        created_at=now,
        updated_at=now,
    )
    file_service.repository.get_by_id = AsyncMock(return_value=mock_record)
    file_service.repository.delete = AsyncMock(return_value=True)

    response = await async_client.delete("/api/v1/files/404")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["id"] == 404
    assert json_data["deleted"] is True
    assert not stored_path.exists()

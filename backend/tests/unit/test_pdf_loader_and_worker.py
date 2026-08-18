import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.pdf_loader import extract_text_from_file
from app.jobs.worker import get_arq_redis_settings, enqueue_file_processing, process_file_job, WorkerSettings
from app.utils.structure_output import ComplaintExtractionOutput


def test_extract_text_from_txt_file(tmp_path: Path):
    """Test extract_text_from_file with text extension."""
    test_file = tmp_path / "sample.txt"
    test_file.write_text("Batch AMX240602: Amoxicillin 500mg capsules discolored.", encoding="utf-8")

    extracted = extract_text_from_file(test_file, extension="txt")
    assert "AMX240602" in extracted
    assert "Amoxicillin" in extracted


def test_extract_text_missing_file():
    """Test extract_text_from_file raises FileNotFoundError on missing file."""
    with pytest.raises(FileNotFoundError):
        extract_text_from_file("non_existent_file.pdf", extension="pdf")


def test_get_arq_redis_settings():
    """Test ARQ redis settings configuration helper."""
    redis_settings = get_arq_redis_settings()
    assert redis_settings.host in ("127.0.0.1", "localhost") or isinstance(redis_settings.host, str)
    assert isinstance(redis_settings.port, int)


@pytest.mark.asyncio
async def test_enqueue_file_processing():
    """Test enqueue_file_processing enqueues job to ARQ pool."""
    mock_job = MagicMock()
    mock_job.job_id = "job_test_123"
    mock_pool = AsyncMock()
    mock_pool.enqueue_job = AsyncMock(return_value=mock_job)

    with patch("app.jobs.worker.get_arq_pool", return_value=mock_pool):
        job_id = await enqueue_file_processing(file_id=1)
        assert job_id == "job_test_123"
        mock_pool.enqueue_job.assert_called_once_with("process_file_job", 1, _keep_result=0)


@pytest.mark.asyncio
async def test_process_file_job_file_not_found():
    """Test process_file_job returns failed status when file ID does not exist in DB."""
    mock_db = AsyncMock()
    mock_file_repo = AsyncMock()
    mock_file_repo.get_by_id = AsyncMock(return_value=None)

    with patch("app.jobs.worker.AsyncSessionLocal", return_value=mock_db), \
         patch("app.jobs.worker.FileRepository", return_value=mock_file_repo):
        res = await process_file_job(ctx={}, file_id=999)
        assert res["status"] == "failed"
        assert "not found" in res["error"]


import pytest
from unittest.mock import AsyncMock
from app.models.complaint import Complaint
from app.services.duplicate_detection import DuplicateDetectionService, _calculate_token_overlap_score
from app.schemas.complaint import ComplaintCreate
from app.services.complaint import ComplaintService



@pytest.fixture
def anyio_backend():
    return 'asyncio'


def test_token_overlap_score():
    text1 = "Discolored capsules found in blister pack"
    text2 = "Discolored capsules observed inside packaging"
    overlap = _calculate_token_overlap_score(text1, text2)
    assert overlap > 0.0


@pytest.mark.anyio
async def test_duplicate_detection_with_matching_batch():
    mock_db = AsyncMock()
    dup_service = DuplicateDetectionService(mock_db)

    # Mock candidate complaint record
    c1 = Complaint(
        id=1,
        complaint_number="CMP-8A3F",
        status="NEW",
        product_name="Amoxicillin 500mg",
        batch_number="AMX2026-DUP-01",
        complaint_category="Packaging / Labeling",
        title="Broken blister seals",
        description="Found 10 broken seals in batch AMX2026-DUP-01.",
        customer_name="Apollo Hospital",
        initial_severity="Major",
    )

    dup_service.repo.find_candidates_for_duplicate_check = AsyncMock(return_value=[c1])

    form_data = {
        "product_name": "Amoxicillin 500mg",
        "batch_number": "AMX2026-DUP-01",
        "complaint_category": "Packaging / Labeling",
        "description": "Seals torn on blister pack.",
    }

    res = await dup_service.check_duplicates(form_data)
    assert res.has_duplicates is True
    assert res.highest_similarity_score >= 75.0
    assert len(res.duplicate_matches) > 0
    assert res.duplicate_matches[0].complaint_number == "CMP-8A3F"
    assert "batch_number" in res.duplicate_matches[0].matched_fields


@pytest.mark.anyio
async def test_duplicate_detection_no_match():
    mock_db = AsyncMock()
    dup_service = DuplicateDetectionService(mock_db)
    dup_service.repo.find_candidates_for_duplicate_check = AsyncMock(return_value=[])

    form_data = {
        "product_name": "Unique Product XYZ 123",
        "batch_number": "UNIQUE-LOT-99999",
        "description": "Clean description with no matching candidates.",
    }

    res = await dup_service.check_duplicates(form_data)
    assert res.has_duplicates is False
    assert len(res.duplicate_matches) == 0


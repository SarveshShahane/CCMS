import pytest
from app.services.completeness import CompletenessService


def test_completeness_100_percent():
    service = CompletenessService()
    full_data = {
        "product_name": "Amoxicillin Capsules 500mg",
        "batch_number": "AMX202608",
        "description": "Capsules were discolored and stuck together in the blister pack.",
        "complaint_category": "Packaging / Labeling",
        "affected_quantity": 10,
        "customer_name": "Metro Pharmacy",
        "customer_contact_email": "qa@metropharmacy.com",
        "dosage_form": "Capsules",
        "product_strength": "500 mg",
        "incident_date": "2026-08-10",
        "manufacturing_date": "2026-01-15",
        "expiry_date": "2028-01-15",
        "product_code": "AMX-500-CAP",
        "complaint_source": "Pharmacy",
        "sample_received": True,
    }

    res = service.evaluate(full_data)
    assert res.completeness_score == 100.0
    assert res.status == "READY_FOR_INVESTIGATION"
    assert res.is_ready_for_investigation is True
    assert len(res.missing_critical) == 0
    assert len(res.missing_important) == 0
    assert len(res.missing_optional) == 0


def test_completeness_missing_critical():
    service = CompletenessService()
    incomplete_data = {
        "customer_name": "John Doe",
        "description": "Broken seals",
        # missing product_name, batch_number, complaint_category, affected_quantity
    }

    res = service.evaluate(incomplete_data)
    assert res.completeness_score < 50.0
    assert res.status == "INCOMPLETE"
    assert res.is_ready_for_investigation is False
    assert len(res.missing_critical) > 0


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_generate_clarification_email():


    service = CompletenessService()
    data = {
        "product_name": "Paracetamol 500mg",
        "description": "Chipped tablets in bottle",
        "customer_name": "Apollo Pharmacy",
    }
    eval_res = service.evaluate(data)
    email = await service.generate_clarification_email(data, eval_res)
    assert "Batch" in email or "Apollo Pharmacy" in email or "Paracetamol" in email

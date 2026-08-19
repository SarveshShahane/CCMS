import pytest
from app.services.root_cause import RootCauseService, _get_deterministic_fallback_rca


@pytest.fixture
def anyio_backend():
    return 'asyncio'


def test_deterministic_fallback_rca_discoloration():
    form_data = {
        "product_name": "Amoxicillin 500mg",
        "batch_number": "AMX9902",
        "complaint_category": "Discoloration",
        "description": "Capsules were turned yellow and discolored.",
    }
    res = _get_deterministic_fallback_rca(form_data)
    assert res.suggested_root_cause_category == "Environment / Storage"
    assert len(res.hypotheses) > 0
    assert len(res.investigation_checklist) > 0
    assert len(res.capa_recommendations) > 0


def test_deterministic_fallback_rca_packaging():
    form_data = {
        "product_name": "Cough Syrup",
        "batch_number": "SYP102",
        "complaint_category": "Packaging / Labeling",
        "description": "Cap seals were loose and leaking in carton.",
    }
    res = _get_deterministic_fallback_rca(form_data)
    assert res.suggested_root_cause_category == "Machine / Equipment"
    assert any(h.category == "Machine / Equipment" for h in res.hypotheses)


@pytest.mark.anyio
async def test_root_cause_service_analyze():
    service = RootCauseService()
    form_data = {
        "product_name": "Paracetamol 650mg",
        "batch_number": "PCT2026",
        "complaint_category": "Sub-potency",
        "description": "Assay test showed lower potency than label claim.",
    }
    res = await service.analyze_root_cause(form_data)
    assert res.suggested_root_cause_category is not None
    assert len(res.hypotheses) > 0
    assert len(res.investigation_checklist) > 0
    assert len(res.capa_recommendations) > 0


@pytest.mark.anyio
async def test_root_cause_service_empty_form_raises_value_error():
    service = RootCauseService()
    form_data = {
        "product_name": "",
        "batch_number": "",
        "complaint_category": "",
        "description": "",
    }
    with pytest.raises(ValueError, match="Complaint form is empty"):
        await service.analyze_root_cause(form_data)


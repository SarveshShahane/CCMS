import pytest
from app.services.capa_risk import CapaRiskService, _get_deterministic_fallback_capa_risk


@pytest.fixture
def anyio_backend():
    return 'asyncio'


def test_deterministic_fallback_capa_risk_critical():
    form_data = {
        "product_name": "Paracetamol 650mg",
        "batch_number": "PCT2026-CRIT",
        "complaint_category": "Contamination",
        "description": "Black particulate matter observed in liquid suspension.",
        "initial_severity": "Critical",
    }
    res = _get_deterministic_fallback_capa_risk(form_data)
    assert res.risk_classification.severity_level == "CRITICAL"
    assert res.risk_classification.health_hazard_class == "CLASS_I"
    assert res.risk_classification.rpn_score >= 80.0
    assert len(res.capa_plan) > 0
    assert any(c.action_type == "CORRECTIVE" for c in res.capa_plan)


def test_deterministic_fallback_capa_risk_minor():
    form_data = {
        "product_name": "Vitamin C Tablets",
        "batch_number": "VIT102",
        "complaint_category": "Packaging / Labeling",
        "description": "Outer carton label slightly scuffed.",
        "initial_severity": "Minor",
    }
    res = _get_deterministic_fallback_capa_risk(form_data)
    assert res.risk_classification.severity_level in ["MINOR", "MAJOR"]
    assert len(res.capa_plan) > 0


@pytest.mark.anyio
async def test_capa_risk_service_evaluate():
    service = CapaRiskService()
    form_data = {
        "product_name": "Amoxicillin 500mg Capsules",
        "batch_number": "AMX8890",
        "complaint_category": "Discoloration",
        "description": "Yellowish spots on capsule shells.",
    }
    res = await service.evaluate_capa_and_risk(form_data)
    assert res.complaint_summary.executive_summary is not None
    assert res.risk_classification.severity_level in ["CRITICAL", "MAJOR", "MINOR"]
    assert res.risk_classification.rpn_score > 0
    assert len(res.capa_plan) > 0

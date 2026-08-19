import json
import logging
import re
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate

from app.config.llm import LLMConfig
from app.prompts.prompt import (
    ROOT_CAUSE_RECOMMENDATION_SYSTEM_PROMPT,
    ROOT_CAUSE_RECOMMENDATION_USER_PROMPT,
)
from app.schemas.root_cause import (
    RootCauseRecommendationResponse,
    RootCauseHypothesis,
    InvestigationStep,
    CapaRecommendation,
)

logger = logging.getLogger(__name__)


def _extract_json_payload(text: str) -> dict:
    """Strips reasoning blocks (<think>...</think>) and parses JSON."""
    clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    return json.loads(clean_text)


def _get_deterministic_fallback_rca(form_data: Dict[str, Any], reason: str = "") -> RootCauseRecommendationResponse:
    """
    Deterministic rule-based RCA generator for pharmaceutical defects when LLM is offline or unavailable.
    """
    category = str(form_data.get("complaint_category") or "").lower()
    description = str(form_data.get("description") or "").lower()
    product_name = form_data.get("product_name") or "Pharmaceutical Product"
    batch_number = form_data.get("batch_number") or "Unknown Lot"

    if "packaging" in category or "seal" in description or "leak" in description:
        primary_cat = "Machine / Equipment"
        hypotheses = [
            RootCauseHypothesis(
                category="Machine / Equipment",
                title="Heat Sealer Temperature Drift",
                description="Fluctuation in blister sealing temperature or pressure resulting in non-hermetic seals.",
                confidence_level="HIGH",
                likelihood_score=85.0,
            ),
            RootCauseHypothesis(
                category="Material Defect",
                title="Blister Foil Pinhole Defect",
                description="Micro-perforations or defective lamination in the aluminum foil batch.",
                confidence_level="MEDIUM",
                likelihood_score=60.0,
            ),
            RootCauseHypothesis(
                category="Man / Human Factor",
                title="Line Clearance & Sealer Calibration Oversight",
                description="Inadequate verification of sealing parameters during packaging line setup.",
                confidence_level="LOW",
                likelihood_score=35.0,
            ),
        ]
        checklist = [
            InvestigationStep(step_number=1, action=f"Audit batch packaging record for batch #{batch_number}.", department="QA / Production", priority="CRITICAL"),
            InvestigationStep(step_number=2, action="Inspect retention samples under 10x magnification for sealing defects.", department="QC Lab", priority="CRITICAL"),
            InvestigationStep(step_number=3, action="Review heat sealer thermal logging sensor calibration data.", department="Maintenance", priority="HIGH"),
            InvestigationStep(step_number=4, action="Perform leak test (methylene blue dye test) on returned samples.", department="QC Lab", priority="HIGH"),
        ]
        capas = [
            CapaRecommendation(action_type="CORRECTIVE", title="Recalibrate Heat Sealer Sensors", description="Perform temperature mapping and replace worn heating elements on packaging line.", target_timeline_days=7),
            CapaRecommendation(action_type="PREVENTIVE", title="Implement Automated Vision Inspection", description="Install inline automated vision system to detect unsealed or defective blisters automatically.", target_timeline_days=30),
        ]

    elif "discolor" in category or "discolor" in description or "color" in description or "moisture" in description:
        primary_cat="Environment / Storage"
        hypotheses = [
            RootCauseHypothesis(
                category="Environment / Storage",
                title="Humidity & Moisture Infiltration",
                description="Exposure to ambient humidity causing active ingredient hydrolysis or oxidation discoloration.",
                confidence_level="HIGH",
                likelihood_score=88.0,
            ),
            RootCauseHypothesis(
                category="Material Defect",
                title="Excipient Impurity Reaction",
                description="Interaction between active pharmaceutical ingredient and binder/excipient batch under light/heat.",
                confidence_level="MEDIUM",
                likelihood_score=65.0,
            ),
            RootCauseHypothesis(
                category="Method / Process",
                title="Drying Phase Time Variance",
                description="Insufficient drying time during granulation leading to residual moisture.",
                confidence_level="MEDIUM",
                likelihood_score=50.0,
            ),
        ]
        checklist = [
            InvestigationStep(step_number=1, action="Test moisture content (Karl Fischer titration) on retention sample.", department="QC Lab", priority="CRITICAL"),
            InvestigationStep(step_number=2, action="Review HVAC humidity and temperature logs for packaging suite during lot run.", department="Engineering", priority="HIGH"),
            InvestigationStep(step_number=3, action="Perform HPLC degradation product assay on discolored units.", department="QC Analytical", priority="CRITICAL"),
        ]
        capas = [
            CapaRecommendation(action_type="CORRECTIVE", title="Quarantine Affected Batch Stock", description="Issue immediate quarantine hold for remaining units of batch in distribution centers.", target_timeline_days=3),
            CapaRecommendation(action_type="PREVENTIVE", title="Upgrade Desiccant Packaging Protection", description="Add silica desiccant canisters to primary bottle packaging line specifications.", target_timeline_days=15),
        ]

    else:
        primary_cat = "Method / Process"
        hypotheses = [
            RootCauseHypothesis(
                category="Method / Process",
                title="Manufacturing Process Parameter Deviation",
                description=f"Potential deviation during blending, compression, or filling of {product_name}.",
                confidence_level="HIGH",
                likelihood_score=75.0,
            ),
            RootCauseHypothesis(
                category="Machine / Equipment",
                title="Equipment Wear / Tooling Tolerance Shift",
                description="Mechanical wear on processing tooling leading to physical quality variation.",
                confidence_level="MEDIUM",
                likelihood_score=55.0,
            ),
            RootCauseHypothesis(
                category="Material Defect",
                title="Raw Material Lot Variability",
                description="Minor particle size or bulk density variation in raw material lot.",
                confidence_level="LOW",
                likelihood_score=40.0,
            ),
        ]
        checklist = [
            InvestigationStep(step_number=1, action=f"Conduct batch manufacturing record (BMR) audit for lot #{batch_number}.", department="QA Investigation", priority="CRITICAL"),
            InvestigationStep(step_number=2, action="Perform physical and chemical testing on retention samples.", department="QC Lab", priority="CRITICAL"),
            InvestigationStep(step_number=3, action="Interview line operators and review equipment logbooks.", department="Production / QA", priority="HIGH"),
        ]
        capas = [
            CapaRecommendation(action_type="CORRECTIVE", title="Investigate Batch Production Logs", description="Re-verify in-process IPC test results (tablet hardness, friability, disintegration).", target_timeline_days=10),
            CapaRecommendation(action_type="PREVENTIVE", title="Standardize Line Clearance SOP", description="Update standard operating procedure for line setup and in-process check frequency.", target_timeline_days=30),
        ]

    summary = (
        f"Automated RCA for {product_name} (Batch #{batch_number}). "
        f"Primary failure mode identified under category: '{primary_cat}'. "
        f"Recommended 4-step QA investigation and targeted CAPA plan attached."
    )
    if reason:
        summary += f" (Note: Rule-based fallback applied: {reason})"

    return RootCauseRecommendationResponse(
        summary_assessment=summary,
        suggested_root_cause_category=primary_cat,
        hypotheses=hypotheses,
        investigation_checklist=checklist,
        capa_recommendations=capas,
    )


class RootCauseService:
    """Service performing AI-driven Ishikawa & 5-Whys Root Cause Analysis."""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()

    async def analyze_root_cause(self, form_data: Dict[str, Any]) -> RootCauseRecommendationResponse:
        """
        Analyzes complaint metadata and returns structured RCA recommendations.
        """
        product_name = str(form_data.get("product_name") or "").strip()
        description = str(form_data.get("description") or "").strip()
        title = str(form_data.get("title") or "").strip()
        batch_number = str(form_data.get("batch_number") or "").strip()

        if not any([product_name, description, title, batch_number]):
            raise ValueError("Complaint form is empty. Please provide at least a Product Name, Title, or Description before performing Root Cause Analysis.")

        try:
            llm_client = self.llm_config.get_llm()
            prompt = ChatPromptTemplate.from_messages([
                ("system", ROOT_CAUSE_RECOMMENDATION_SYSTEM_PROMPT),
                ("user", ROOT_CAUSE_RECOMMENDATION_USER_PROMPT),
            ])

            chain = prompt | llm_client
            raw_res = await chain.ainvoke({
                "product_name": form_data.get("product_name") or "Unspecified Product",
                "product_code": form_data.get("product_code") or "N/A",
                "dosage_form": form_data.get("dosage_form") or "N/A",
                "product_strength": form_data.get("product_strength") or "N/A",
                "batch_number": form_data.get("batch_number") or "N/A",
                "complaint_category": form_data.get("complaint_category") or "General",
                "description": form_data.get("description") or "No description provided",
                "affected_quantity": form_data.get("affected_quantity") or 1,
                "affected_quantity_unit": form_data.get("affected_quantity_unit") or "units",
                "initial_severity": form_data.get("initial_severity") or "Major",
                "incident_date": str(form_data.get("incident_date") or "N/A"),
            })

            text_content = raw_res.content if hasattr(raw_res, 'content') else str(raw_res)
            json_dict = _extract_json_payload(text_content)
            return RootCauseRecommendationResponse.model_validate(json_dict)

        except Exception as exc:
            logger.warning(f"RootCauseService LLM analysis failed: {exc}. Using deterministic fallback.")
            return _get_deterministic_fallback_rca(form_data, reason=str(exc))

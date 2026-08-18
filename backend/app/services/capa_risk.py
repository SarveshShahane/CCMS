import json
import logging
import re
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate

from app.config.llm import LLMConfig
from app.prompts.prompt import (
    CAPA_RISK_ASSESSMENT_SYSTEM_PROMPT,
    CAPA_RISK_ASSESSMENT_USER_PROMPT,
)
from app.schemas.capa_risk import (
    CapaRiskAssessmentResponse,
    ComplaintSummaryInfo,
    RiskClassificationInfo,
    CapaItemDetail,
)

logger = logging.getLogger(__name__)


def _extract_json_payload(text: str) -> dict:
    """Strips reasoning blocks (<think>...</think>) and parses JSON."""
    clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    return json.loads(clean_text)


def _get_deterministic_fallback_capa_risk(form_data: Dict[str, Any], reason: str = "") -> CapaRiskAssessmentResponse:
    """
    Deterministic rule-based CAPA & Risk engine for pharmaceutical defects when LLM is offline or unavailable.
    """
    product_name = form_data.get("product_name") or "Pharmaceutical Product"
    batch_number = form_data.get("batch_number") or "Unknown Lot"
    category = str(form_data.get("complaint_category") or "").lower()
    description = str(form_data.get("description") or "").lower()
    initial_severity = str(form_data.get("initial_severity") or "Major").upper()

    if "contaminat" in category or "contaminat" in description or "sub-potency" in category or initial_severity == "CRITICAL":
        sev = "CRITICAL"
        hh_class = "CLASS_I"
        rpn = 90.0
        prob = "HIGH"
        diff = "HARD"
        summary_text = f"Critical quality complaint involving potential patient risk or therapeutic failure for {product_name} (Batch #{batch_number})."
        capa_items = [
            CapaItemDetail(
                capa_id="CAPA-01",
                action_type="CORRECTIVE",
                title="Immediate Quarantining of Batch Stock",
                description=f"Quarantine all remaining units of Batch #{batch_number} across warehouses and distribution channels.",
                owner_department="QA / Warehouse",
                target_timeline_days=2,
                effectiveness_verification_plan="Verify 100% reconciliation of physical inventory against SAP stock records.",
            ),
            CapaItemDetail(
                capa_id="CAPA-02",
                action_type="CORRECTIVE",
                title="Assay & Impurity Lab Investigation",
                description="Conduct full pharmacopeial testing (HPLC assay, dissolution, mass spec) on retention samples.",
                owner_department="QC Analytical",
                target_timeline_days=7,
                effectiveness_verification_plan="Certificate of Analysis (CoA) review by QA Manager.",
            ),
            CapaItemDetail(
                capa_id="CAPA-03",
                action_type="PREVENTIVE",
                title="Raw Material Supplier Quality Audit",
                description="Audit API/excipient vendor quality system and revise raw material release specifications.",
                owner_department="Vendor Quality QA",
                target_timeline_days=30,
                effectiveness_verification_plan="Audit report approval and zero out-of-specification (OOS) results in 3 subsequent vendor lots.",
            ),
        ]
    elif "discolor" in category or "discolor" in description or "packaging" in category or "seal" in description:
        sev = "MAJOR"
        hh_class = "CLASS_II"
        rpn = 65.0
        prob = "MEDIUM"
        diff = "MODERATE"
        summary_text = f"Major physical/packaging defect reported for {product_name} (Batch #{batch_number}). Product specification compromised."
        capa_items = [
            CapaItemDetail(
                capa_id="CAPA-01",
                action_type="CORRECTIVE",
                title="Inspect Line Sealing Parameters & Retention Units",
                description="Inspect retention sample blister packs and recalibrate packaging line heat sealing temperature sensors.",
                owner_department="Maintenance / Production",
                target_timeline_days=5,
                effectiveness_verification_plan="Zero sealing failures observed in 100 random retention blister samples.",
            ),
            CapaItemDetail(
                capa_id="CAPA-02",
                action_type="PREVENTIVE",
                title="Upgrade In-line Automated Vision Inspection",
                description="Install automated camera vision system to detect unsealed blisters or discolored tablets automatically during packaging.",
                owner_department="Engineering / QA",
                target_timeline_days=30,
                effectiveness_verification_plan="Validation protocol (IQ/OQ/PQ) completion and 100% defect capture during line challenge test.",
            ),
        ]
    else:
        sev = "MINOR"
        hh_class = "CLASS_III"
        rpn = 35.0
        prob = "LOW"
        diff = "EASY"
        summary_text = f"Minor cosmetic or isolated defect reported for {product_name} (Batch #{batch_number}). Unlikely to impact therapeutic efficacy."
        capa_items = [
            CapaItemDetail(
                capa_id="CAPA-01",
                action_type="CORRECTIVE",
                title="Review Packaging Line Clearance Logs",
                description="Review line clearance logbook and re-train packaging line operators on visual defect standards.",
                owner_department="Production",
                target_timeline_days=10,
                effectiveness_verification_plan="Training record log signed by Quality Assurance Trainer.",
            ),
            CapaItemDetail(
                capa_id="CAPA-02",
                action_type="PREVENTIVE",
                title="Standardize In-Process Visual Inspection Frequency",
                description="Increase in-process visual check sampling frequency from hourly to every 30 minutes.",
                owner_department="Quality Assurance",
                target_timeline_days=14,
                effectiveness_verification_plan="SOP revision approval and zero repeat cosmetic complaints over 60 days.",
            ),
        ]

    summary_info = ComplaintSummaryInfo(
        executive_summary=summary_text,
        defect_impact=f"Reported issue: '{description[:150]}'. Evaluated for batch {batch_number}.",
        batch_scope=f"Single lot ({batch_number}) under active investigation.",
        customer_risk="Moderate to Low health hazard depending on patient exposure.",
    )

    risk_info = RiskClassificationInfo(
        severity_level=sev,
        occurrence_probability=prob,
        detection_difficulty=diff,
        rpn_score=rpn,
        health_hazard_class=hh_class,
        risk_explanation=f"Calculated RPN of {rpn} based on {sev} severity and {hh_class} health hazard risk framework.",
    )

    readiness_notes = "CAPA recommendations aligned with 21 CFR Part 211.192 / ICH Q9 Risk Management guidelines."
    if reason:
        readiness_notes += f" (Deterministic rule fallback used: {reason})"

    return CapaRiskAssessmentResponse(
        complaint_summary=summary_info,
        risk_classification=risk_info,
        capa_plan=capa_items,
        gmp_audit_readiness_notes=readiness_notes,
    )


class CapaRiskService:
    """Service generating AI-driven Executive Complaint Summaries, Risk Matrix, and CAPA Plans."""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()

    async def evaluate_capa_and_risk(self, form_data: Dict[str, Any]) -> CapaRiskAssessmentResponse:
        """
        Evaluates complaint payload and returns unified Executive Summary, Risk Classification, and CAPA Plan.
        """
        try:
            llm_client = self.llm_config.get_llm()
            prompt = ChatPromptTemplate.from_messages([
                ("system", CAPA_RISK_ASSESSMENT_SYSTEM_PROMPT),
                ("user", CAPA_RISK_ASSESSMENT_USER_PROMPT),
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
                "customer_name": form_data.get("customer_name") or "Anonymous Customer",
                "complaint_source": form_data.get("complaint_source") or "Direct Intake",
                "incident_date": str(form_data.get("incident_date") or "N/A"),
            })

            text_content = raw_res.content if hasattr(raw_res, 'content') else str(raw_res)
            json_dict = _extract_json_payload(text_content)
            return CapaRiskAssessmentResponse.model_validate(json_dict)

        except Exception as exc:
            logger.warning(f"CapaRiskService LLM analysis failed: {exc}. Using deterministic fallback.")
            return _get_deterministic_fallback_capa_risk(form_data, reason=str(exc))

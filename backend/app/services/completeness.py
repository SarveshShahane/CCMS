import logging
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate

from app.config.llm import LLMConfig
from app.prompts.prompt import COMPLAINT_CLARIFICATION_EMAIL_PROMPT
from app.schemas.completeness import (
    CompletenessCheckResponse,
    MissingFieldDetail,
)

logger = logging.getLogger(__name__)


# Definition of field requirements and metadata
CRITICAL_FIELDS = [
    {
        "field": "product_name",
        "label": "Product Name",
        "weight": 10,
        "suggestion": "Specify the full trade or brand name of the drug product.",
    },
    {
        "field": "batch_number",
        "label": "Batch / Lot Number",
        "weight": 10,
        "suggestion": "Required for lot trace, batch record audit, and retention sample checks.",
    },
    {
        "field": "description",
        "label": "Complaint Description",
        "weight": 10,
        "suggestion": "Describe the physical defect, symptom, packaging anomaly, or adverse event.",
    },
    {
        "field": "complaint_category",
        "label": "Complaint Category",
        "weight": 10,
        "suggestion": "Select the primary defect classification (e.g. Discoloration, Packaging).",
    },
    {
        "field": "affected_quantity",
        "label": "Affected Quantity",
        "weight": 10,
        "suggestion": "State how many units/packs/tablets are affected.",
    },
]

IMPORTANT_FIELDS = [
    {
        "field": "customer_name",
        "label": "Customer / Entity Name",
        "weight": 7,
        "suggestion": "Provide the name of the hospital, pharmacy, or patient reporting.",
    },
    {
        "field": "customer_contact",
        "label": "Contact Information (Email or Phone)",
        "weight": 7,
        "suggestion": "Required to contact the reporter for follow-up and sample retrieval.",
    },
    {
        "field": "dosage_form",
        "label": "Dosage Form",
        "weight": 7,
        "suggestion": "Form of medication (e.g. Capsules, Injectable, Oral Solution).",
    },
    {
        "field": "product_strength",
        "label": "Product Strength",
        "weight": 7,
        "suggestion": "Specify concentration or strength (e.g. 500 mg, 10 mg/mL).",
    },
    {
        "field": "incident_date",
        "label": "Incident / Discovery Date",
        "weight": 7,
        "suggestion": "Date when defect or issue was noticed by customer.",
    },
]

OPTIONAL_FIELDS = [
    {
        "field": "manufacturing_date",
        "label": "Manufacturing Date",
        "weight": 3,
        "suggestion": "helps locate batch release documentation and stability logs.",
    },
    {
        "field": "expiry_date",
        "label": "Expiry Date",
        "weight": 3,
        "suggestion": "Check if product was within shelf-life when incident occurred.",
    },
    {
        "field": "product_code",
        "label": "Product / SKU Code",
        "weight": 3,
        "suggestion": "Internal material code or GTIN.",
    },
    {
        "field": "complaint_source",
        "label": "Complaint Source",
        "weight": 3,
        "suggestion": "Channel of intake (e.g. Pharmacy, Distributor, Patient).",
    },
    {
        "field": "sample_received",
        "label": "Physical Sample Status",
        "weight": 3,
        "suggestion": "Indicate whether defective physical unit was returned for lab testing.",
    },
]


class CompletenessService:
    """Service evaluating complaint completeness against pharmaceutical QA criteria."""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()

    def evaluate(self, form_data: Dict[str, Any]) -> CompletenessCheckResponse:
        """
        Evaluates complaint form dictionary and returns completeness score, missing fields, and status.
        """
        score = 0.0
        missing_critical: List[MissingFieldDetail] = []
        missing_important: List[MissingFieldDetail] = []
        missing_optional: List[MissingFieldDetail] = []

        # 1. Evaluate Critical Fields
        for item in CRITICAL_FIELDS:
            val = form_data.get(item["field"])
            if val is not None and str(val).strip() != "" and str(val).strip() != "0":
                score += item["weight"]
            else:
                missing_critical.append(
                    MissingFieldDetail(
                        field=item["field"],
                        label=item["label"],
                        category="critical",
                        suggestion=item["suggestion"],
                    )
                )

        # 2. Evaluate Important Fields
        for item in IMPORTANT_FIELDS:
            if item["field"] == "customer_contact":
                email = form_data.get("customer_contact_email")
                phone = form_data.get("customer_contact_phone")
                has_contact = (email and str(email).strip()) or (phone and str(phone).strip())
                if has_contact:
                    score += item["weight"]
                else:
                    missing_important.append(
                        MissingFieldDetail(
                            field="customer_contact_email",
                            label=item["label"],
                            category="important",
                            suggestion=item["suggestion"],
                        )
                    )
            else:
                val = form_data.get(item["field"])
                if val is not None and str(val).strip() != "":
                    score += item["weight"]
                else:
                    missing_important.append(
                        MissingFieldDetail(
                            field=item["field"],
                            label=item["label"],
                            category="important",
                            suggestion=item["suggestion"],
                        )
                    )

        # 3. Evaluate Optional Fields
        for item in OPTIONAL_FIELDS:
            val = form_data.get(item["field"])
            if val is not None and str(val).strip() != "" and val is not False:
                score += item["weight"]
            else:
                missing_optional.append(
                    MissingFieldDetail(
                        field=item["field"],
                        label=item["label"],
                        category="optional",
                        suggestion=item["suggestion"],
                    )
                )

        # Score normalization & status determination
        score = min(100.0, max(0.0, round(score, 1)))
        has_critical_missing = len(missing_critical) > 0
        is_ready = (score >= 80.0) and not has_critical_missing

        if is_ready:
            status = "READY_FOR_INVESTIGATION"
        elif score >= 50.0:
            status = "PARTIALLY_COMPLETE"
        else:
            status = "INCOMPLETE"

        total_missing = len(missing_critical) + len(missing_important) + len(missing_optional)

        return CompletenessCheckResponse(
            completeness_score=score,
            status=status,
            is_ready_for_investigation=is_ready,
            missing_critical=missing_critical,
            missing_important=missing_important,
            missing_optional=missing_optional,
            total_missing_count=total_missing,
            suggested_followup_email=None,
        )

    async def generate_clarification_email(
        self, form_data: Dict[str, Any], response: CompletenessCheckResponse
    ) -> str:
        """
        Uses LLM (or deterministic template fallback) to generate a customer follow-up email.
        """
        all_missing = response.missing_critical + response.missing_important
        if not all_missing:
            return "No critical or important information is missing. The complaint record has sufficient details for investigation."

        bullet_list = "\n".join([f"- {item.label}: {item.suggestion}" for item in all_missing])

        customer_name = form_data.get("customer_name") or "Valued Customer / Pharmacy Partner"
        product_name = form_data.get("product_name") or "the reported pharmaceutical product"
        batch_number = form_data.get("batch_number") or "[Not Provided]"
        description = form_data.get("description") or "[Details under review]"

        try:
            llm_client = self.llm_config.get_llm()
            prompt = ChatPromptTemplate.from_template(COMPLAINT_CLARIFICATION_EMAIL_PROMPT)
            chain = prompt | llm_client
            res = await chain.ainvoke(
                {
                    "customer_name": customer_name,
                    "product_name": product_name,
                    "batch_number": batch_number,
                    "description": description,
                    "missing_fields_bulleted": bullet_list,
                }
            )
            email_content = res.content if hasattr(res, "content") else str(res)
            return email_content.strip()
        except Exception as exc:
            logger.warning(f"LLM email generation fallback triggered due to: {exc}")
            return (
                f"Subject: Important: Clarification Request for Customer Complaint - {product_name}\n\n"
                f"Dear {customer_name},\n\n"
                f"Thank you for contacting our Quality Assurance department regarding {product_name} (Batch #{batch_number}).\n\n"
                "To ensure a thorough Quality Control investigation and comply with regulatory requirements, "
                "we kindly request the following additional details regarding your report:\n\n"
                f"{bullet_list}\n\n"
                "Please reply to this email or send photos of the batch packaging and affected unit at your earliest convenience.\n\n"
                "Sincerely,\n"
                "Quality Assurance & Customer Safety Team"
            )

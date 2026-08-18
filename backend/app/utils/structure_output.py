import logging
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.config.llm import LLMConfig
from app.prompts.prompt import (
    COMPLAINT_EXTRACTION_SYSTEM_PROMPT,
    COMPLAINT_EXTRACTION_USER_PROMPT,
)

logger = logging.getLogger(__name__)


class ComplaintExtractionOutput(BaseModel):
    """
    Pydantic schema for structured output extraction from customer complaints.
    Enforces strict typing and nullability for fields not explicitly mentioned.
    """
    is_valid_complaint: bool = Field(
        description="True if user input describes a legitimate product quality issue or complaint, False otherwise."
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="Name of the customer, entity, or pharmacy submitting the complaint (e.g. Apollo Pharmacy). Null if not mentioned."
    )
    complaint_source: Optional[str] = Field(
        default=None,
        description="Source type of complaint (e.g., Pharmacy, Hospital, Patient, Distributor). Null if not mentioned."
    )
    product_name: Optional[str] = Field(
        default=None,
        description="Full product name (e.g., Amoxicillin Capsules 500 mg). Null if not mentioned."
    )
    product_code: Optional[str] = Field(
        default=None,
        description="Product item code or SKU. Null if not mentioned."
    )
    dosage_form: Optional[str] = Field(
        default=None,
        description="Form of product (e.g., Capsules, Tablets, Ointment, Injection). Null if not mentioned."
    )
    product_strength: Optional[str] = Field(
        default=None,
        description="Strength specification (e.g., 500 mg, 10 mg/ml). Null if not mentioned."
    )
    batch_number: Optional[str] = Field(
        default=None,
        description="Batch or lot identification number (e.g. AMX240602). Null if not mentioned."
    )
    affected_quantity: Optional[float] = Field(
        default=None,
        description="Numerical quantity of affected units. Null if not mentioned."
    )
    affected_quantity_unit: Optional[str] = Field(
        default=None,
        description="Unit for affected quantity (e.g., capsules, packs, bottles). Null if not mentioned."
    )
    complaint_category: Optional[str] = Field(
        default=None,
        description="Primary defect category (e.g., Discoloration, Packaging, Contamination, Sub-potency). Null if not mentioned."
    )
    title: Optional[str] = Field(
        default=None,
        description="Brief summary title for the complaint record. Null if not mentioned."
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of reported problem extracted from input. Null if not mentioned."
    )
    initial_severity: Optional[str] = Field(
        default=None,
        description="Initial severity rating: Critical, Major, or Minor. Null if not mentioned."
    )
    ai_risk_assessment: Optional[str] = Field(
        default=None,
        description="Concise initial risk assessment analysis generated for the reported complaint. Null if not mentioned."
    )
    ai_suggested_next_action: Optional[str] = Field(
        default=None,
        description="Recommended next steps for QA/QC team. Null if not mentioned."
    )
    manufacturing_date: Optional[str] = Field(
        default=None,
        description="Manufacturing date string (e.g., March 2026). Null if not mentioned."
    )
    expiry_date: Optional[str] = Field(
        default=None,
        description="Expiry date string (e.g., February 2028). Null if not mentioned."
    )
    incident_date: Optional[str] = Field(
        default=None,
        description="Date when incident occurred. Null if not mentioned."
    )
    response_message: str = Field(
        description="Natural language summary message to present back to the user."
    )


class ComplaintStructuredParser:
    """
    Utility class combining Pydantic schemas and LangChain to produce structured output from LLMs.
    """

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()

    async def parse_complaint(self, user_input: str) -> ComplaintExtractionOutput:
        """
        Parses raw complaint text into a structured ComplaintExtractionOutput Pydantic object using LangChain.

        :param user_input: Raw text string sent by user
        :return: ComplaintExtractionOutput Pydantic object
        """
        try:
            llm_client = self.llm_config.get_llm()
        except ValueError as err:
            logger.warning(f"LLM API key not configured: {err}")
            return self._fallback_parse(user_input, error_reason="LLM API Key missing.")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", COMPLAINT_EXTRACTION_SYSTEM_PROMPT),
            ("user", COMPLAINT_EXTRACTION_USER_PROMPT),
        ])

        try:
            structured_llm = llm_client.with_structured_output(ComplaintExtractionOutput)
            chain = prompt_template | structured_llm
            result = await chain.ainvoke({"user_input": user_input})
            
            if isinstance(result, ComplaintExtractionOutput):
                return result
            elif isinstance(result, dict):
                return ComplaintExtractionOutput.model_validate(result)
            else:
                return self._fallback_parse(user_input, error_reason="Invalid structure returned by LLM.")

        except Exception as exc:
            logger.error(f"Error invoking structured output chain: {exc}", exc_info=True)
            try:
                parser = PydanticOutputParser(pydantic_object=ComplaintExtractionOutput)
                fallback_template = ChatPromptTemplate.from_messages([
                    ("system", COMPLAINT_EXTRACTION_SYSTEM_PROMPT + "\n\n{format_instructions}"),
                    ("user", COMPLAINT_EXTRACTION_USER_PROMPT),
                ])
                chain = fallback_template | llm_client | parser
                return await chain.ainvoke({
                    "user_input": user_input,
                    "format_instructions": parser.get_format_instructions(),
                })
            except Exception as secondary_exc:
                logger.error(f"Secondary parsing attempt failed: {secondary_exc}")
                return self._fallback_parse(user_input, error_reason=str(exc))

    def _fallback_parse(self, user_input: str, error_reason: str) -> ComplaintExtractionOutput:
        """
        Deterministic fallback when LLM is unavailable or fails.
        """
        is_basic_valid = len(user_input.strip()) > 10 and any(
            kw in user_input.lower() for kw in ["complaint", "defect", "discolored", "batch", "expired", "report", "capsule", "tablet"]
        )
        if is_basic_valid:
            return ComplaintExtractionOutput(
                is_valid_complaint=True,
                description=user_input,
                response_message=(
                    "Complaint received. Extracted basic details from input, but automated structured parsing "
                    f"encountered an issue ({error_reason}). Please review data manually."
                )
            )
        return ComplaintExtractionOutput(
            is_valid_complaint=False,
            response_message=(
                "Unable to parse complaint. Please provide relevant details such as product name, "
                "batch number, manufacturing/expiry date, or description of the issue."
            )
        )

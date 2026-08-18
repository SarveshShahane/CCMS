import json
import logging
import re
from typing import Optional, TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END

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
        default=True,
        description="True if user input describes a legitimate product quality issue or complaint, False otherwise."
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="Name of the customer, entity, or pharmacy submitting the complaint (e.g. Apollo Pharmacy). Null if not mentioned."
    )
    customer_contact_email: Optional[str] = Field(
        default=None,
        description="Contact email of the customer or submitter (e.g. quality@apollohealth.com). Null if not mentioned."
    )
    customer_contact_phone: Optional[str] = Field(
        default=None,
        description="Contact phone number of the customer or submitter (e.g. +1-800-555-0199). Null if not mentioned."
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
    response_message: Optional[str] = Field(
        default="Complaint processed and extracted.",
        description="Natural language summary message to present back to the user."
    )


class ComplaintState(TypedDict):
    """
    Custom state definition for the LangGraph complaint extraction workflow.
    """
    user_input: str
    llm_config: Optional[LLMConfig]
    extracted_output: Optional[ComplaintExtractionOutput]
    error: Optional[str]


def _extract_json_payload(text: str) -> dict:
    """
    Strips reasoning blocks (like <think>...</think>) and extracts clean JSON dictionary from LLM string output.
    """
    clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    return json.loads(clean_text)


def _fallback_parse(user_input: str, error_reason: str) -> ComplaintExtractionOutput:
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


async def extract_complaint_node(state: ComplaintState) -> dict:
    """
    LangGraph Node function that executes LLM extraction logic or fallback logic.
    """
    user_input = state.get("user_input", "")
    llm_config = state.get("llm_config") or LLMConfig()

    try:
        llm_client = llm_config.get_llm()
    except ValueError as err:
        logger.warning(f"LLM API key not configured: {err}")
        fallback = _fallback_parse(user_input, error_reason="LLM API Key missing.")
        return {"extracted_output": fallback, "error": str(err)}

    parser = PydanticOutputParser(pydantic_object=ComplaintExtractionOutput)

    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", COMPLAINT_EXTRACTION_SYSTEM_PROMPT + "\n\nCRITICAL INSTRUCTION: Output ONLY valid raw JSON matching these schema instructions (no markdown, no reasoning, no extra text):\n{format_instructions}"),
            ("user", COMPLAINT_EXTRACTION_USER_PROMPT),
        ])

        chain = prompt_template | llm_client
        raw_response = await chain.ainvoke({
            "user_input": user_input,
            "format_instructions": parser.get_format_instructions(),
        })

        text_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
        json_dict = _extract_json_payload(text_content)
        output = ComplaintExtractionOutput.model_validate(json_dict)
        return {"extracted_output": output, "error": None}

    except Exception as exc:
        logger.warning(f"Prompt JSON extraction approach failed: {exc}. Trying fallback structured output chain.")

        try:
            structured_llm = llm_client.with_structured_output(ComplaintExtractionOutput)
            fallback_prompt = ChatPromptTemplate.from_messages([
                ("system", COMPLAINT_EXTRACTION_SYSTEM_PROMPT),
                ("user", COMPLAINT_EXTRACTION_USER_PROMPT),
            ])
            chain = fallback_prompt | structured_llm
            result = await chain.ainvoke({"user_input": user_input})

            if isinstance(result, ComplaintExtractionOutput):
                return {"extracted_output": result, "error": None}
            elif isinstance(result, dict):
                output = ComplaintExtractionOutput.model_validate(result)
                return {"extracted_output": output, "error": None}
        except Exception as secondary_exc:
            logger.error(f"Structured output fallback failed: {secondary_exc}")

        fallback = _fallback_parse(user_input, error_reason=str(exc))
        return {"extracted_output": fallback, "error": str(exc)}


class ComplaintStructuredParser:
    """
    Utility class combining Pydantic schemas, LangChain, and LangGraph to produce structured output from LLMs.
    """

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()
        self.graph = self._build_graph()

    def _build_graph(self):
        """
        Builds and compiles the LangGraph StateGraph.
        """
        workflow = StateGraph(ComplaintState)
        workflow.add_node("extract_complaint", extract_complaint_node)
        workflow.add_edge(START, "extract_complaint")
        workflow.add_edge("extract_complaint", END)
        return workflow.compile()

    def _extract_json_payload(self, text: str) -> dict:
        """
        Backward-compatible helper proxy method.
        """
        return _extract_json_payload(text)

    def _fallback_parse(self, user_input: str, error_reason: str) -> ComplaintExtractionOutput:
        """
        Backward-compatible helper proxy method.
        """
        return _fallback_parse(user_input, error_reason)

    async def parse_complaint(self, user_input: str) -> ComplaintExtractionOutput:
        """
        Parses raw complaint text into a structured ComplaintExtractionOutput Pydantic object using LangGraph.

        :param user_input: Raw text string sent by user
        :return: ComplaintExtractionOutput Pydantic object
        """
        initial_state: ComplaintState = {
            "user_input": user_input,
            "llm_config": self.llm_config,
            "extracted_output": None,
            "error": None,
        }

        result = await self.graph.ainvoke(initial_state)
        extracted = result.get("extracted_output")
        if extracted:
            return extracted

        return _fallback_parse(user_input, error_reason="LangGraph returned empty output.")


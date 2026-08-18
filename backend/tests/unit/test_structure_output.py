import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

from app.utils.structure_output import (
    ComplaintExtractionOutput,
    ComplaintState,
    ComplaintStructuredParser,
    extract_complaint_node,
    _extract_json_payload,
    _fallback_parse,
)
from app.config.llm import LLMConfig


def test_extract_json_payload_clean_text():
    raw_response = '```json\n{"is_valid_complaint": true, "product_name": "Test Med"}\n```'
    parsed = _extract_json_payload(raw_response)
    assert parsed["product_name"] == "Test Med"


def test_extract_json_payload_with_think_tags():
    raw_response = '<think>analyzing input...</think>{"is_valid_complaint": true, "batch_number": "B123"}'
    parsed = _extract_json_payload(raw_response)
    assert parsed["batch_number"] == "B123"


def test_fallback_parse():
    user_input = "Complaint regarding discolored capsules in batch AMX123"
    result = _fallback_parse(user_input, error_reason="Test error")
    assert result.is_valid_complaint is True
    assert "Test error" in result.response_message


@pytest.mark.asyncio
async def test_extract_complaint_node_missing_api_key():
    mock_llm_config = MagicMock(spec=LLMConfig)
    mock_llm_config.get_llm.side_effect = ValueError("GROQ_API_KEY environment variable is not set.")

    state: ComplaintState = {
        "user_input": "Reporting defective batch B100 of Amoxicillin",
        "llm_config": mock_llm_config,
        "extracted_output": None,
        "error": None,
    }

    result = await extract_complaint_node(state)
    assert result["extracted_output"] is not None
    assert result["extracted_output"].is_valid_complaint is True
    assert "LLM API Key missing" in result["extracted_output"].response_message
    assert "GROQ_API_KEY" in result["error"]


@pytest.mark.asyncio
async def test_extract_complaint_node_successful_chain_invocation():
    from langchain_core.runnables import RunnableLambda

    async def mock_invoke(input_val):
        return AIMessage(
            content='{"is_valid_complaint": true, "product_name": "Paracetamol 500mg", "batch_number": "PCT999"}'
        )

    mock_llm = RunnableLambda(mock_invoke)
    mock_llm_config = MagicMock(spec=LLMConfig)
    mock_llm_config.get_llm.return_value = mock_llm

    state: ComplaintState = {
        "user_input": "Found damaged packaging in Paracetamol 500mg batch PCT999",
        "llm_config": mock_llm_config,
        "extracted_output": None,
        "error": None,
    }

    result = await extract_complaint_node(state)
    assert result["error"] is None
    assert result["extracted_output"].product_name == "Paracetamol 500mg"
    assert result["extracted_output"].batch_number == "PCT999"


@pytest.mark.asyncio
async def test_complaint_structured_parser_langgraph_invocation():
    from langchain_core.runnables import RunnableLambda

    async def mock_invoke(input_val):
        return AIMessage(
            content='{"is_valid_complaint": true, "product_name": "Ibuprofen 400mg", "customer_name": "Apollo Pharmacy"}'
        )

    mock_llm = RunnableLambda(mock_invoke)
    mock_llm_config = MagicMock(spec=LLMConfig)
    mock_llm_config.get_llm.return_value = mock_llm

    parser = ComplaintStructuredParser(llm_config=mock_llm_config)
    assert parser.graph is not None

    output = await parser.parse_complaint("Apollo Pharmacy reported issues with Ibuprofen 400mg")
    assert isinstance(output, ComplaintExtractionOutput)
    assert output.product_name == "Ibuprofen 400mg"
    assert output.customer_name == "Apollo Pharmacy"


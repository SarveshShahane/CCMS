from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.chat import ChatService
from app.models.chat import Chat, ChatMessage
from app.schemas.chat import ChatCreateRequest, ChatMessageCreate
from app.exceptions.chat import ChatNotFoundException, ChatMessageException
from app.utils.structure_output import ComplaintExtractionOutput
from app.prompts.prompt import INITIAL_AI_MESSAGE


@pytest.mark.asyncio
async def test_create_chat_creates_session_and_initial_ai_message():
    mock_db = AsyncMock()
    service = ChatService(db=mock_db)

    now = datetime.now(timezone.utc)
    saved_chat = Chat(id=1, title="New Complaint Chat", complaint_id=None, created_at=now, updated_at=now)
    welcome_msg = ChatMessage(id=1, chat_id=1, sender="ai", content=INITIAL_AI_MESSAGE, created_at=now)
    saved_chat.messages = [welcome_msg]

    service.repository.create = AsyncMock(return_value=saved_chat)
    service.repository.add_message = AsyncMock(return_value=welcome_msg)
    service.repository.get_by_id = AsyncMock(return_value=saved_chat)

    req = ChatCreateRequest(title=None)
    response = await service.create_chat(req)

    assert response.id == 1
    assert response.title == "New Complaint Chat"
    assert len(response.messages) == 1
    assert response.messages[0].sender == "ai"
    assert INITIAL_AI_MESSAGE in response.messages[0].content


@pytest.mark.asyncio
async def test_get_chat_not_found():
    mock_db = AsyncMock()
    service = ChatService(db=mock_db)
    service.repository.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(ChatNotFoundException):
        await service.get_chat(chat_id=999)


@pytest.mark.asyncio
async def test_send_message_extracts_structured_data_and_updates_title():
    mock_db = AsyncMock()
    service = ChatService(db=mock_db)

    now = datetime.now(timezone.utc)
    chat_record = Chat(id=42, title="New Complaint Chat", created_at=now, updated_at=now, messages=[])
    service.repository.get_by_id = AsyncMock(return_value=chat_record)

    user_msg_db = ChatMessage(id=10, chat_id=42, sender="user", content="Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg. Batch number AMX240602.", created_at=now)
    extracted_output = ComplaintExtractionOutput(
        is_valid_complaint=True,
        customer_name="Apollo Pharmacy",
        product_name="Amoxicillin Capsules 500 mg",
        batch_number="AMX240602",
        response_message="Complaint parsed successfully. I've extracted the product details, mapped the batch information, and generated an initial risk assessment for the discolored capsules."
    )
    ai_msg_db = ChatMessage(id=11, chat_id=42, sender="ai", content=extracted_output.response_message, extra_data=extracted_output.model_dump(), created_at=now)

    service.repository.add_message = AsyncMock(side_effect=[user_msg_db, ai_msg_db])
    service.repository.update_title = AsyncMock()
    service.parser.parse_complaint = AsyncMock(return_value=extracted_output)

    msg_req = ChatMessageCreate(content="Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg. Batch number AMX240602.")
    result = await service.send_message(chat_id=42, message_input=msg_req)

    assert result.chat_id == 42
    assert result.user_message.content == msg_req.content
    assert "Complaint parsed successfully" in result.ai_message.content
    assert result.extracted_data.batch_number == "AMX240602"
    assert result.extracted_data.customer_name == "Apollo Pharmacy"
    assert result.extracted_data.product_name == "Amoxicillin Capsules 500 mg"
    service.repository.update_title.assert_called_once_with(42, "Complaint: Amoxicillin Capsules 500 mg")


@pytest.mark.asyncio
async def test_guardrail_unmentioned_parameters_stay_null():
    extracted = ComplaintExtractionOutput(
        is_valid_complaint=True,
        description="Packaging damaged",
        response_message="Complaint logged."
    )
    assert extracted.product_name is None
    assert extracted.batch_number is None
    assert extracted.customer_name is None
    assert extracted.expiry_date is None
    assert extracted.manufacturing_date is None

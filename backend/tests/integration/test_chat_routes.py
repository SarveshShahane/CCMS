from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from main import app
from app.routes.chat import get_chat_service
from app.services.chat import ChatService
from app.models.chat import Chat, ChatMessage
from app.schemas.chat import ChatCreateRequest, ChatMessageCreate
from app.utils.structure_output import ComplaintExtractionOutput
from app.prompts.prompt import INITIAL_AI_MESSAGE


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def chat_service(mock_db):
    """Instantiate ChatService with a mock database."""
    return ChatService(db=mock_db)


@pytest.fixture
def async_client(chat_service):
    """FastAPI AsyncClient fixture overriding get_chat_service dependency."""
    app.dependency_overrides[get_chat_service] = lambda: chat_service
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_chat_route_success(async_client, chat_service):
    """Test POST /api/v1/chats/ creates new chat with initial welcome AI message."""
    now = datetime.now(timezone.utc)
    welcome_msg = ChatMessage(
        id=1, chat_id=10, sender="ai", content=INITIAL_AI_MESSAGE, created_at=now
    )
    mock_chat = Chat(
        id=10,
        title="New Complaint Chat",
        complaint_id=None,
        messages=[welcome_msg],
        created_at=now,
        updated_at=now,
    )
    chat_service.repository.create = AsyncMock(return_value=mock_chat)
    chat_service.repository.add_message = AsyncMock(return_value=welcome_msg)
    chat_service.repository.get_by_id = AsyncMock(return_value=mock_chat)

    response = await async_client.post("/api/v1/chats/", json={})

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["id"] == 10
    assert json_data["title"] == "New Complaint Chat"
    assert len(json_data["messages"]) == 1
    assert json_data["messages"][0]["sender"] == "ai"
    assert "Ready to process new complaints" in json_data["messages"][0]["content"]


@pytest.mark.asyncio
async def test_list_chats_route_success(async_client, chat_service):
    """Test GET /api/v1/chats/ returns list of chat summaries."""
    now = datetime.now(timezone.utc)
    mock_chats = [
        Chat(id=1, title="Chat 1", complaint_id=None, created_at=now, updated_at=now),
        Chat(id=2, title="Chat 2", complaint_id=None, created_at=now, updated_at=now),
    ]
    chat_service.repository.get_all = AsyncMock(return_value=mock_chats)
    chat_service.repository.count = AsyncMock(return_value=2)

    response = await async_client.get("/api/v1/chats/?skip=0&limit=50")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 2
    assert len(json_data["items"]) == 2
    assert json_data["items"][0]["id"] == 1
    assert json_data["items"][1]["id"] == 2


@pytest.mark.asyncio
async def test_get_chat_route_success(async_client, chat_service):
    """Test GET /api/v1/chats/{chat_id} returns detailed chat session."""
    now = datetime.now(timezone.utc)
    msg1 = ChatMessage(id=1, chat_id=5, sender="ai", content=INITIAL_AI_MESSAGE, created_at=now)
    mock_chat = Chat(
        id=5, title="Amoxicillin Issue", complaint_id=None, messages=[msg1], created_at=now, updated_at=now
    )
    chat_service.repository.get_by_id = AsyncMock(return_value=mock_chat)

    response = await async_client.get("/api/v1/chats/5")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["id"] == 5
    assert json_data["title"] == "Amoxicillin Issue"
    assert len(json_data["messages"]) == 1


@pytest.mark.asyncio
async def test_get_chat_route_not_found_404(async_client, chat_service):
    """Test GET /api/v1/chats/{chat_id} returns 404 for non-existent chat."""
    chat_service.repository.get_by_id = AsyncMock(return_value=None)

    response = await async_client.get("/api/v1/chats/9999")

    assert response.status_code == 404
    json_data = response.json()
    assert "was not found" in json_data["detail"]


@pytest.mark.asyncio
async def test_delete_chat_route_success(async_client, chat_service):
    """Test DELETE /api/v1/chats/{chat_id} deletes chat session."""
    now = datetime.now(timezone.utc)
    mock_chat = Chat(id=7, title="To Be Deleted", created_at=now, updated_at=now)
    chat_service.repository.get_by_id = AsyncMock(return_value=mock_chat)
    chat_service.repository.delete = AsyncMock(return_value=True)

    response = await async_client.delete("/api/v1/chats/7")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["id"] == 7
    assert json_data["deleted"] is True


@pytest.mark.asyncio
async def test_delete_chat_route_not_found_404(async_client, chat_service):
    """Test DELETE /api/v1/chats/{chat_id} returns 404 for non-existent chat."""
    chat_service.repository.get_by_id = AsyncMock(return_value=None)

    response = await async_client.delete("/api/v1/chats/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message_route_success(async_client, chat_service):
    """Test POST /api/v1/chats/{chat_id}/messages sends message and gets structured AI response."""
    now = datetime.now(timezone.utc)
    mock_chat = Chat(id=12, title="New Complaint Chat", created_at=now, updated_at=now, messages=[])
    chat_service.repository.get_by_id = AsyncMock(return_value=mock_chat)

    complaint_text = "Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg. Batch number AMX240602."
    
    extracted_output = ComplaintExtractionOutput(
        is_valid_complaint=True,
        customer_name="Apollo Pharmacy",
        product_name="Amoxicillin Capsules 500 mg",
        batch_number="AMX240602",
        response_message="Complaint parsed successfully. I've extracted the product details, mapped the batch information, and generated an initial risk assessment for the discolored capsules."
    )

    user_msg_db = ChatMessage(id=20, chat_id=12, sender="user", content=complaint_text, created_at=now)
    ai_msg_db = ChatMessage(
        id=21, chat_id=12, sender="ai", content=extracted_output.response_message, extra_data=extracted_output.model_dump(), created_at=now
    )

    chat_service.repository.add_message = AsyncMock(side_effect=[user_msg_db, ai_msg_db])
    chat_service.repository.update_title = AsyncMock()
    chat_service.parser.parse_complaint = AsyncMock(return_value=extracted_output)

    payload = {"content": complaint_text, "sender": "user"}
    response = await async_client.post("/api/v1/chats/12/messages", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["chat_id"] == 12
    assert json_data["user_message"]["content"] == complaint_text
    assert "Complaint parsed successfully" in json_data["ai_message"]["content"]
    assert json_data["extracted_data"]["batch_number"] == "AMX240602"
    assert json_data["extracted_data"]["customer_name"] == "Apollo Pharmacy"
    assert json_data["extracted_data"]["product_name"] == "Amoxicillin Capsules 500 mg"


@pytest.mark.asyncio
async def test_send_message_route_empty_message_400(async_client, chat_service):
    """Test POST /api/v1/chats/{chat_id}/messages returns 400 when content is empty."""
    now = datetime.now(timezone.utc)
    mock_chat = Chat(id=12, title="Test Chat", created_at=now, updated_at=now)
    chat_service.repository.get_by_id = AsyncMock(return_value=mock_chat)

    response = await async_client.post("/api/v1/chats/12/messages", json={"content": "   "})

    assert response.status_code == 400

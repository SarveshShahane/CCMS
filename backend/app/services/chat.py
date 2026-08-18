import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat, ChatMessage
from app.repositories.chat import ChatRepository
from app.schemas.chat import (
    ChatCreateRequest,
    ChatMessageCreate,
    ChatResponse,
    ChatDetailResponse,
    ChatListResponse,
    ChatDeleteResponse,
    SendMessageResponse,
    ChatMessageResponse,
)
from app.exceptions.chat import (
    ChatNotFoundException,
    ChatMessageException,
)
from app.prompts.prompt import INITIAL_AI_MESSAGE
from app.utils.structure_output import ComplaintStructuredParser

logger = logging.getLogger(__name__)


class ChatService:
    """Manages chat sessions and LLM complaint extraction."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ChatRepository(db)
        self.parser = ComplaintStructuredParser()

    async def create_chat(self, req: ChatCreateRequest) -> ChatDetailResponse:
        """Creates a new chat session with an initial welcome message."""
        chat_title = req.title.strip() if req.title else "New Complaint Chat"
        
        chat_record = Chat(
            title=chat_title,
            complaint_id=req.complaint_id,
        )
        saved_chat = await self.repository.create(chat_record)

        initial_ai_msg = ChatMessage(
            chat_id=saved_chat.id,
            sender="ai",
            content=INITIAL_AI_MESSAGE,
            extra_data={"type": "welcome_message"},
        )
        await self.repository.add_message(initial_ai_msg)

        updated_chat = await self.repository.get_by_id(saved_chat.id)
        return ChatDetailResponse.model_validate(updated_chat)

    async def get_chat(self, chat_id: int) -> ChatDetailResponse:
        """Fetches chat session details by ID."""
        chat_record = await self.repository.get_by_id(chat_id)
        if not chat_record:
            raise ChatNotFoundException(chat_id)
        return ChatDetailResponse.model_validate(chat_record)

    async def list_chats(self, skip: int = 0, limit: int = 50) -> ChatListResponse:
        """Returns paginated chat sessions."""
        chats = await self.repository.get_all(skip=skip, limit=limit)
        total = await self.repository.count()

        return ChatListResponse(
            items=[ChatResponse.model_validate(c) for c in chats],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def delete_chat(self, chat_id: int) -> ChatDeleteResponse:
        """Deletes a chat session and its history."""
        chat_record = await self.repository.get_by_id(chat_id)
        if not chat_record:
            raise ChatNotFoundException(chat_id)

        await self.repository.delete(chat_record)

        return ChatDeleteResponse(
            id=chat_id,
            message=f"Chat session ID {chat_id} deleted successfully.",
            deleted=True,
        )

    async def send_message(
        self, chat_id: int, message_input: ChatMessageCreate
    ) -> SendMessageResponse:
        """Saves user message, triggers structured LLM extraction, and stores AI reply."""
        chat_record = await self.repository.get_by_id(chat_id)
        if not chat_record:
            raise ChatNotFoundException(chat_id)

        user_content = message_input.content.strip()
        if not user_content:
            raise ChatMessageException("Message content cannot be empty.")

        user_msg = ChatMessage(
            chat_id=chat_id,
            sender=message_input.sender or "user",
            content=user_content,
        )
        saved_user_msg = await self.repository.add_message(user_msg)

        extracted_data = await self.parser.parse_complaint(user_content)

        ai_msg = ChatMessage(
            chat_id=chat_id,
            sender="ai",
            content=extracted_data.response_message,
            extra_data=extracted_data.model_dump(),
        )
        saved_ai_msg = await self.repository.add_message(ai_msg)

        if chat_record.title in ["New Complaint Chat", None, ""]:
            if extracted_data.product_name:
                new_title = f"Complaint: {extracted_data.product_name}"
                await self.repository.update_title(chat_id, new_title)
            elif extracted_data.title:
                await self.repository.update_title(chat_id, extracted_data.title)

        return SendMessageResponse(
            chat_id=chat_id,
            user_message=ChatMessageResponse.model_validate(saved_user_msg),
            ai_message=ChatMessageResponse.model_validate(saved_ai_msg),
            extracted_data=extracted_data,
        )


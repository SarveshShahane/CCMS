from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.utils.structure_output import ComplaintExtractionOutput


class ChatMessageCreate(BaseModel):
    """Schema for sending a new message in a chat session."""
    content: str = Field(..., min_length=1, description="Message content text")
    sender: str = Field(default="user", description="Message sender ('user', 'ai', or 'system')")


class ChatMessageResponse(BaseModel):
    """Schema for displaying a chat message record."""
    id: int
    chat_id: int
    sender: str
    content: str
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatCreateRequest(BaseModel):
    """Schema for creating a new chat session."""
    title: Optional[str] = Field(default=None, description="Optional title for the chat session")
    complaint_id: Optional[int] = Field(default=None, description="Optional linked complaint ID")


class ChatResponse(BaseModel):
    """Schema for chat session basic metadata summary."""
    id: int
    title: Optional[str] = None
    complaint_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(ChatResponse):
    """Schema for detailed chat session with full message history."""
    messages: List[ChatMessageResponse] = []


class ChatListResponse(BaseModel):
    """Schema for paginated chat session list responses."""
    items: List[ChatResponse]
    total: int
    skip: int
    limit: int


class ChatDeleteResponse(BaseModel):
    """Schema for chat session deletion response."""
    id: int
    message: str
    deleted: bool


class SendMessageResponse(BaseModel):
    """Schema for the response after sending a message to the AI copilot."""
    chat_id: int
    user_message: ChatMessageResponse
    ai_message: ChatMessageResponse
    extracted_data: Optional[ComplaintExtractionOutput] = None

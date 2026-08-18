from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.services.chat import ChatService
from app.schemas.chat import (
    ChatCreateRequest,
    ChatMessageCreate,
    ChatDetailResponse,
    ChatListResponse,
    ChatDeleteResponse,
    SendMessageResponse,
)
from app.exceptions.chat import (
    ChatException,
    ChatNotFoundException,
    ChatMessageException,
    LLMProcessingException,
)

router = APIRouter(prefix="/chats", tags=["Chats"])


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Dependency helper injecting AsyncSession into ChatService."""
    return ChatService(db)


def handle_chat_exceptions(exc: ChatException) -> None:
    """Maps custom domain chat exceptions to standard FastAPI HTTP exceptions."""
    if isinstance(exc, ChatNotFoundException):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        )
    elif isinstance(exc, ChatMessageException):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        )
    elif isinstance(exc, LLMProcessingException):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.message,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/",
    response_model=ChatDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
    description="Creates a new chat session for complaint processing and returns initial welcome AI message.",
)
async def create_chat(
    req: ChatCreateRequest,
    service: ChatService = Depends(get_chat_service),
):
    try:
        return await service.create_chat(req)
    except ChatException as exc:
        handle_chat_exceptions(exc)


@router.get(
    "/",
    response_model=ChatListResponse,
    status_code=status.HTTP_200_OK,
    summary="List chat sessions",
    description="Returns a paginated list of chat sessions ordered by latest activity.",
)
async def list_chats(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    service: ChatService = Depends(get_chat_service),
):
    try:
        return await service.list_chats(skip=skip, limit=limit)
    except ChatException as exc:
        handle_chat_exceptions(exc)


@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get chat session details",
    description="Fetches chat session details including full message history by chat ID.",
)
async def get_chat(
    chat_id: int,
    service: ChatService = Depends(get_chat_service),
):
    try:
        return await service.get_chat(chat_id=chat_id)
    except ChatException as exc:
        handle_chat_exceptions(exc)


@router.delete(
    "/{chat_id}",
    response_model=ChatDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a chat session",
    description="Deletes a chat session and all associated message records.",
)
async def delete_chat(
    chat_id: int,
    service: ChatService = Depends(get_chat_service),
):
    try:
        return await service.delete_chat(chat_id=chat_id)
    except ChatException as exc:
        handle_chat_exceptions(exc)


@router.post(
    "/{chat_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to chat",
    description="Sends user complaint text to chat session, invokes LangChain LLM structured output parsing, and returns AI response.",
)
async def send_message(
    chat_id: int,
    message: ChatMessageCreate,
    service: ChatService = Depends(get_chat_service),
):
    try:
        return await service.send_message(chat_id=chat_id, message_input=message)
    except ChatException as exc:
        handle_chat_exceptions(exc)

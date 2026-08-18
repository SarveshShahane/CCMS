from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat, ChatMessage


class ChatRepository:
    """
    Repository layer for Chat and ChatMessage database operations.
    Encapsulates all database query logic for chat sessions and messages.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, chat: Chat) -> Chat:
        """Create and persist a new Chat session."""
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_by_id(self, chat_id: int) -> Optional[Chat]:
        """Fetch a Chat session by ID along with its messages eagerly loaded."""
        stmt = (
            select(Chat)
            .options(selectinload(Chat.messages))
            .where(Chat.id == chat_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 50) -> List[Chat]:
        """Retrieve a paginated list of Chat sessions ordered by updated_at desc."""
        stmt = (
            select(Chat)
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count total Chat sessions in database."""
        stmt = select(func.count(Chat.id))
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def delete(self, chat: Chat) -> bool:
        """Delete a Chat session and all associated cascade messages."""
        await self.db.delete(chat)
        await self.db.commit()
        return True

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        """Add and persist a new ChatMessage record to a chat session."""
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def update_title(self, chat_id: int, title: str) -> Optional[Chat]:
        """Update the title of a chat session."""
        chat = await self.get_by_id(chat_id)
        if chat:
            chat.title = title
            await self.db.commit()
            await self.db.refresh(chat)
        return chat

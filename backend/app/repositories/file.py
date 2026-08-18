from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import FileAttachment


class FileRepository:
    """
    Repository layer for FileAttachment database operations.
    Encapsulates all database interactions for file records.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, file_attachment: FileAttachment) -> FileAttachment:
        """Create and persist a new FileAttachment record."""
        self.db.add(file_attachment)
        await self.db.commit()
        await self.db.refresh(file_attachment)
        return file_attachment

    async def get_by_id(self, file_id: int) -> Optional[FileAttachment]:
        """Fetch a FileAttachment record by its primary key ID."""
        stmt = select(FileAttachment).where(FileAttachment.id == file_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        complaint_id: Optional[int] = None,
        chat_id: Optional[int] = None,
    ) -> List[FileAttachment]:
        """Retrieve a paginated list of FileAttachment records with optional filters."""
        stmt = select(FileAttachment)
        
        if complaint_id is not None:
            stmt = stmt.where(FileAttachment.complaint_id == complaint_id)
        if chat_id is not None:
            stmt = stmt.where(FileAttachment.chat_id == chat_id)

        stmt = stmt.order_by(FileAttachment.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        complaint_id: Optional[int] = None,
        chat_id: Optional[int] = None,
    ) -> int:
        """Count total FileAttachment records matching the specified filters."""
        stmt = select(func.count(FileAttachment.id))

        if complaint_id is not None:
            stmt = stmt.where(FileAttachment.complaint_id == complaint_id)
        if chat_id is not None:
            stmt = stmt.where(FileAttachment.chat_id == chat_id)

        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def delete(self, file_attachment: FileAttachment) -> bool:
        """Delete a FileAttachment record from the database."""
        await self.db.delete(file_attachment)
        await self.db.commit()
        return True

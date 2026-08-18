from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.config.db import Base


class FileAttachment(Base):
    """
    File Attachment Database Model.
    
    Stores metadata for uploaded files attached to complaints or chat sessions.
    Supports formats: PDF, DOCX, TXT, EML up to 10 MB.
    """
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    extension: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)

    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    complaint_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("complaints.id", ondelete="SET NULL"), nullable=True, index=True
    )
    chat_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chats.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
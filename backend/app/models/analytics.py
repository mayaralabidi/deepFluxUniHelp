"""Analytics and feedback models for usage tracking and user feedback."""

from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, String, Integer, Text, DateTime, Enum as SQLEnum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from backend.app.core.database import Base
from backend.app.models.user import GUID


class ChatLog(Base):
    """SQLAlchemy model for chat interactions."""
    __tablename__ = "chat_logs"
    
    id = Column(GUID(), primary_key=True, default=uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # List of document names
    response_time_ms = Column(Integer, nullable=False)  # milliseconds
    tokens_used = Column(Integer, nullable=True)  # Prompt + completion tokens
    session_id = Column(String(100), nullable=True, index=True)  # For grouping across conversations
    conversation_id = Column(GUID(), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<ChatLog(user_id={self.user_id}, response_time={self.response_time_ms}ms)>"


class DocumentAccess(Base):
    """SQLAlchemy model for document access tracking."""
    __tablename__ = "document_accesses"
    
    id = Column(GUID(), primary_key=True, default=uuid4, nullable=False)
    document_name = Column(String(255), nullable=False)
    document_id = Column(String(100), nullable=True)  # ChromaDB document ID
    accessed_by_user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_type = Column(String(50), nullable=False)  # "retrieved" | "uploaded" | "deleted"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<DocumentAccess(doc={self.document_name}, type={self.access_type})>"


class FeedbackCategory(str, Enum):
    """Categories for user feedback."""
    WRONG_ANSWER = "wrong_answer"
    INCOMPLETE = "incomplete"
    OUTDATED = "outdated"
    OTHER = "other"


class FeedbackLog(Base):
    """SQLAlchemy model for user feedback on chat responses."""
    __tablename__ = "feedback_logs"
    
    id = Column(GUID(), primary_key=True, default=uuid4, nullable=False)
    chat_log_id = Column(GUID(), ForeignKey("chat_logs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1 (👍) or -1 (👎)
    comment = Column(Text, nullable=True)  # User's optional comment
    correction = Column(Text, nullable=True)  # User's suggested correction
    category = Column(SQLEnum(FeedbackCategory), nullable=True)
    reviewed_by_admin = Column(Boolean, default=False, nullable=False)
    admin_notes = Column(Text, nullable=True)  # Admin's response/action taken
    resolved_at = Column(DateTime, nullable=True)  # When issue was resolved
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<FeedbackLog(chat_id={self.chat_log_id}, rating={self.rating})>"


# Pydantic schemas for API

class ChatLogRead(BaseModel):
    """Schema for chat log response."""
    id: str
    user_id: str
    question: str
    answer: str
    sources: Optional[list[str]] = None
    response_time_ms: int
    tokens_used: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackSubmit(BaseModel):
    """Schema for submitting feedback."""
    chat_log_id: str
    rating: int = Field(..., ge=-1, le=1)  # -1 or 1
    comment: Optional[str] = Field(None, max_length=1000)
    correction: Optional[str] = Field(None, max_length=2000)
    category: Optional[FeedbackCategory] = None


class FeedbackRead(BaseModel):
    """Schema for feedback response."""
    id: str
    chat_log_id: str
    user_id: str
    rating: int
    comment: Optional[str] = None
    correction: Optional[str] = None
    category: Optional[FeedbackCategory] = None
    reviewed_by_admin: bool
    admin_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    """Schema for feedback statistics."""
    total: int
    positive_count: int
    negative_count: int
    satisfaction_rate: float  # Percentage of positive feedback
    by_category: dict[str, int]  # {category: count}
    unreviewed_count: int

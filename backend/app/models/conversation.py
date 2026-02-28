"""Conversation and Message models for conversation history."""

from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from backend.app.core.database import Base
from backend.app.models.user import GUID


class MessageRole(str, Enum):
    """Role of message sender."""
    USER = "user"
    ASSISTANT = "assistant"


class Conversation(Base):
    """SQLAlchemy Conversation model."""
    __tablename__ = "conversations"
    
    id = Column(GUID(), primary_key=True, default=uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)  # Auto-generated from first question
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Conversation(title={self.title}, user_id={self.user_id})>"


class Message(Base):
    """SQLAlchemy Message model."""
    __tablename__ = "messages"
    
    id = Column(GUID(), primary_key=True, default=uuid4, nullable=False)
    conversation_id = Column(GUID(), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SQLEnum(MessageRole), nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # List of document names/references
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(role={self.role}, conversation_id={self.conversation_id})>"


# Pydantic schemas
from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    """Schema for a single message."""
    id: str
    role: MessageRole
    content: str
    sources: Optional[list[dict]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationRead(BaseModel):
    """Schema for conversation response with messages."""
    id: str
    user_id: str
    title: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    messages: list[MessageSchema] = []
    
    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    """Schema for conversation in list view (preview only)."""
    id: str
    title: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

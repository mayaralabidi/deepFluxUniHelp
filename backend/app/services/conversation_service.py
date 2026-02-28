"""Conversation management service."""

import logging
from uuid import UUID
from typing import Optional, List, Tuple

from sqlalchemy import select, and_, func, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.conversation import Conversation, Message, MessageRole, ConversationRead, MessageSchema
from backend.app.models.user import User

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing user conversations and message history."""
    
    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: UUID,
        first_question: str,
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            db: Database session
            user_id: User ID
            first_question: First user question (used to auto-generate title)
        
        Returns:
            Created Conversation object
        """
        # Auto-generate title from first question (truncate to 60 chars)
        title = first_question[:60].strip()
        if len(first_question) > 60:
            title += "..."
        
        conversation = Conversation(
            user_id=user_id,
            title=title,
            is_archived=False,
        )
        
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        logger.info(f"Conversation created: {conversation.id} for user {user_id}")
        return conversation
    
    @staticmethod
    async def add_message(
        db: AsyncSession,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        sources: Optional[List[dict]] = None,
    ) -> Message:
        """
        Add a message to a conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role (user or assistant)
            content: Message content
            sources: Optional list of source documents
        
        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources,
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        logger.debug(f"Message added to conversation {conversation_id}")
        return message
    
    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Optional[ConversationRead]:
        """
        Get a conversation with all its messages.
        
        Verifies user ownership.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID (for ownership check)
        
        Returns:
            ConversationRead with all messages, or None if not found/not owned
        """
        result = await db.execute(
            select(Conversation)
            .where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                )
            )
            .options(selectinload(Conversation.messages))
        )
        
        conversation = result.scalars().first()
        
        if conversation is None:
            return None
        
        return ConversationRead.model_validate(conversation)
    
    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_archived: bool = False,
    ) -> Tuple[List[Conversation], int]:
        """
        List user's conversations.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Max results
            offset: Pagination offset
            include_archived: Include archived conversations
        
        Returns:
            Tuple of (conversations list, total count)
        """
        query = select(Conversation).where(Conversation.user_id == user_id)
        
        if not include_archived:
            query = query.where(Conversation.is_archived == False)
        
        # Count total
        count_result = await db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == user_id
            )
        )
        total = count_result.scalar() or 0
        
        # Get paginated results, sorted by most recent
        query = query.order_by(desc(Conversation.updated_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        conversations = result.scalars().all()
        
        return conversations, total
    
    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Delete a conversation (only if owned by user).
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID (for ownership check)
        
        Returns:
            True if deleted, False if not owned/not found
        """
        result = await db.execute(
            select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                )
            )
        )
        
        conversation = result.scalars().first()
        
        if conversation is None:
            return False
        
        await db.delete(conversation)
        await db.commit()
        
        logger.info(f"Conversation {conversation_id} deleted")
        return True
    
    @staticmethod
    async def archive_conversation(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Archive a conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID (for ownership check)
        
        Returns:
            True if archived, False if not owned/not found
        """
        result = await db.execute(
            select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                )
            )
        )
        
        conversation = result.scalars().first()
        
        if conversation is None:
            return False
        
        conversation.is_archived = True
        await db.commit()
        
        logger.info(f"Conversation {conversation_id} archived")
        return True
    
    @staticmethod
    async def search_conversations(
        db: AsyncSession,
        user_id: UUID,
        query: str,
        limit: int = 10,
    ) -> List[Conversation]:
        """
        Search conversations by title or message content.
        
        Args:
            db: Database session
            user_id: User ID
            query: Search query
            limit: Max results
        
        Returns:
            List of matching conversations
        """
        # Search in conversation titles and message content
        result = await db.execute(
            select(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    or_(
                        Conversation.title.ilike(f"%{query}%"),
                        Conversation.messages.any(
                            Message.content.ilike(f"%{query}%")
                        ),
                    ),
                )
            )
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        
        conversations = result.scalars().all()
        return conversations
    
    @staticmethod
    async def get_recent_messages(
        db: AsyncSession,
        conversation_id: UUID,
        limit: int = 6,
    ) -> List[Message]:
        """
        Get most recent messages from a conversation (for LLM context).
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Max messages to return
        
        Returns:
            List of recent messages (oldest to newest)
        """
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        
        messages = list(reversed(result.scalars().all()))  # Reverse to get oldest first
        return messages

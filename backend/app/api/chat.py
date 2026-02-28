"""
Chat API with RAG and conversation support.
"""

import asyncio
import logging
import time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.conversation import MessageRole, ConversationListItem
from backend.app.rag.chain import invoke_rag
from backend.app.services.conversation_service import ConversationService
from backend.app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response schemas
class ChatRequest(BaseModel):
    """Chat request with optional conversation support."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None  # UUID string
    create_new: bool = False  # Force create new conversation


class SourceInfo(BaseModel):
    """Information about a source document."""
    content: str
    source: str


class ChatResponse(BaseModel):
    """Chat response with sources."""
    answer: str
    sources: list[SourceInfo] = []
    conversation_id: str
    message_id: str


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Chat endpoint with RAG and conversation support.
    
    Supports three modes:
    1. create_new=True: Start a new conversation
    2. conversation_id provided: Continue existing conversation
    3. Neither: Creates a new conversation (default behavior)
    
    Logs analytics for each interaction and stores conversation history.
    
    Args:
        request: Chat request
        current_user: Authenticated user
        db: Database session
    
    Returns:
        ChatResponse with answer and sources
    
    Raises:
        400: Empty message
        401: Unauthorized
        404: Conversation not found
        504: RAG timeout
        500: Server error
    """
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    
    try:
        # Determine conversation mode
        conversation_id = None
        existing = None  # Track if we're continuing an existing conversation
        
        if request.create_new or request.conversation_id is None:
            # Create new conversation
            conversation = await ConversationService.create_conversation(
                db=db,
                user_id=current_user.id,
                first_question=request.message,
            )
            conversation_id = conversation.id
            logger.info(f"New conversation created: {conversation_id}")
        else:
            # Use existing conversation
            conversation_id = UUID(request.conversation_id)
            existing = await ConversationService.get_conversation(
                db=db,
                conversation_id=conversation_id,
                user_id=current_user.id,
            )
            if existing is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or not owned by user",
                )
            logger.info(f"Continuing conversation: {conversation_id}")
        
        # Get recent conversation history for context (if continuing existing conversation)
        recent_messages = []
        if existing is not None:
            recent_messages = await ConversationService.get_recent_messages(
                db=db,
                conversation_id=conversation_id,
                limit=6,
            )
        
        # Invoke RAG with conversation context
        start_time = time.time()
        from starlette.concurrency import run_in_threadpool
        
        try:
            answer, sources = await asyncio.wait_for(
                run_in_threadpool(
                    invoke_rag,
                    request.message,
                    recent_messages,  # Pass conversation history
                ),
                timeout=settings.RAG_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error(f"RAG operation timed out after {settings.RAG_TIMEOUT}s")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Request timeout. Please try again.",
            )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract source document names
        source_names = [source for _, source in sources]
        
        # Log chat interaction
        chat_log = await AnalyticsService.log_chat(
            db=db,
            user_id=current_user.id,
            question=request.message,
            answer=answer,
            sources=source_names,
            response_time_ms=response_time_ms,
            tokens_used=None,  # Can be extracted from OpenAI response if available
            conversation_id=conversation_id,
        )
        
        # Store messages in conversation
        user_message = await ConversationService.add_message(
            db=db,
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=request.message,
        )
        
        assistant_message = await ConversationService.add_message(
            db=db,
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=answer,
            sources=[{"name": s, "type": "document"} for s in source_names],
        )
        
        # Log document access for analytics
        for source_name in source_names:
            await AnalyticsService.log_document_access(
                db=db,
                document_name=source_name,
                user_id=current_user.id,
                access_type="retrieved",
            )
        
        logger.info(
            f"Chat completed: {response_time_ms}ms, "
            f"user={current_user.email}, "
            f"conversation={conversation_id}"
        )
        
        return ChatResponse(
            answer=answer,
            sources=[
                SourceInfo(content=content, source=source)
                for content, source in sources
            ],
            conversation_id=str(conversation_id),
            message_id=str(assistant_message.id),
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat operation failed",
        )


@router.get("/conversations", status_code=status.HTTP_200_OK)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    include_archived: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all conversations for current user.
    
    Args:
        limit: Results per page (1-100)
        offset: Pagination offset
        include_archived: Include archived conversations
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of conversations with pagination info
    """
    try:
        if not (1 <= limit <= 100):
            raise ValueError("Limit must be between 1 and 100")
        
        conversations, total = await ConversationService.list_conversations(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            include_archived=include_archived,
        )
        
        return {
            "status": "success",
            "data": [ConversationListItem.model_validate(c) for c in conversations],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
            },
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific conversation with all messages.
    
    Args:
        conversation_id: Conversation ID (UUID)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Full conversation with message history
    """
    try:
        conversation = await ConversationService.get_conversation(
            db=db,
            conversation_id=UUID(conversation_id),
            user_id=current_user.id,
        )
        
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        
        return {
            "status": "success",
            "data": conversation.model_dump(),
        }
    except ValueError as e:
        if "invalid UUID" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID",
            )
        raise


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a conversation permanently.
    
    Args:
        conversation_id: Conversation ID (UUID)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        No content (204)
    """
    try:
        success = await ConversationService.delete_conversation(
            db=db,
            conversation_id=UUID(conversation_id),
            user_id=current_user.id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    except ValueError as e:
        if "invalid UUID" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID",
            )
        raise


@router.patch("/conversations/{conversation_id}/archive", status_code=status.HTTP_200_OK)
async def archive_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Archive a conversation (not deleted, just hidden).
    
    Args:
        conversation_id: Conversation ID (UUID)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Archived conversation
    """
    try:
        success = await ConversationService.archive_conversation(
            db=db,
            conversation_id=UUID(conversation_id),
            user_id=current_user.id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        
        conversation = await ConversationService.get_conversation(
            db=db,
            conversation_id=UUID(conversation_id),
            user_id=current_user.id,
        )
        
        return {
            "status": "success",
            "data": conversation.model_dump(),
        }
    except ValueError as e:
        if "invalid UUID" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID",
            )
        raise


@router.get("/conversations/search/{query}", status_code=status.HTTP_200_OK)
async def search_conversations(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search conversations by title or content.
    
    Args:
        query: Search query
        limit: Max results (1-50)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of matching conversations
    """
    try:
        if not (1 <= limit <= 50):
            raise ValueError("Limit must be between 1 and 50")
        
        conversations = await ConversationService.search_conversations(
            db=db,
            user_id=current_user.id,
            query=query,
            limit=limit,
        )
        
        return {
            "status": "success",
            "data": [ConversationListItem.model_validate(c) for c in conversations],
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

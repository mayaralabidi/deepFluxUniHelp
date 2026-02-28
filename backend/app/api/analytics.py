"""Analytics API endpoints."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.dependencies import require_staff_or_admin
from backend.app.models.user import User
from backend.app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary_stats(
    days: int = 30,
    _: User = Depends(require_staff_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary statistics (staff+ only).
    
    Args:
        days: Look back N days (0 = all time)
        _: Current user (role check only)
        db: Database session
    
    Returns:
        Summary stats: total_chats, total_users, avg_response_time, satisfaction_rate, etc.
    """
    try:
        stats = await AnalyticsService.get_summary_stats(db, days=days)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        logger.error(f"Error getting summary stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        )


@router.get("/top-questions")
async def get_top_questions(
    days: int = 30,
    limit: int = 10,
    _: User = Depends(require_staff_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get most frequently asked questions (staff+ only).
    
    Args:
        days: Look back N days
        limit: Max questions to return (1-100)
        _: Current user (role check only)
        db: Database session
    
    Returns:
        List of questions with frequency count
    """
    if not (1 <= limit <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100",
        )
    
    try:
        questions = await AnalyticsService.get_top_questions(db, limit=limit, days=days)
        return {
            "status": "success",
            "data": questions,
        }
    except Exception as e:
        logger.error(f"Error getting top questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve questions",
        )


@router.get("/top-documents")
async def get_top_documents(
    days: int = 30,
    limit: int = 10,
    _: User = Depends(require_staff_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get most frequently retrieved documents (staff+ only).
    
    Args:
        days: Look back N days
        limit: Max documents to return (1-100)
        _: Current user (role check only)
        db: Database session
    
    Returns:
        List of documents with access counts
    """
    if not (1 <= limit <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100",
        )
    
    try:
        documents = await AnalyticsService.get_top_documents(db, limit=limit, days=days)
        return {
            "status": "success",
            "data": documents,
        }
    except Exception as e:
        logger.error(f"Error getting top documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents",
        )


@router.get("/daily-usage")
async def get_daily_usage(
    days: int = 30,
    _: User = Depends(require_staff_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get daily usage time series (staff+ only).
    
    Args:
        days: Number of days to return
        _: Current user (role check only)
        db: Database session
    
    Returns:
        List of daily stats: date, chat_count, unique_users
    """
    if not (1 <= days <= 365):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365",
        )
    
    try:
        usage = await AnalyticsService.get_daily_usage(db, days=days)
        return {
            "status": "success",
            "data": usage,
        }
    except Exception as e:
        logger.error(f"Error getting daily usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage data",
        )


@router.get("/unanswered")
async def get_unanswered_questions(
    limit: int = 20,
    _: User = Depends(require_staff_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get questions with likely low-confidence answers (staff+ only).
    
    Useful for identifying gaps in knowledge base or RAG performance.
    
    Args:
        limit: Max questions to return (1-100)
        _: Current user (role check only)
        db: Database session
    
    Returns:
        List of questions where answers may be incomplete
    """
    if not (1 <= limit <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100",
        )
    
    try:
        questions = await AnalyticsService.get_unanswered_questions(db, limit=limit)
        return {
            "status": "success",
            "data": questions,
        }
    except Exception as e:
        logger.error(f"Error getting unanswered questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve unanswered questions",
        )

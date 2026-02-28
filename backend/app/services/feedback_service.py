"""Feedback service for managing user feedback."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from uuid import UUID

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.analytics import FeedbackLog, FeedbackCategory, ChatLog, FeedbackStats

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for managing user feedback."""
    
    @staticmethod
    async def submit_feedback(
        db: AsyncSession,
        chat_log_id: UUID,
        user_id: UUID,
        rating: int,
        comment: Optional[str] = None,
        correction: Optional[str] = None,
        category: Optional[FeedbackCategory] = None,
    ) -> FeedbackLog:
        """
        Submit feedback on a chat response.
        
        Args:
            db: Database session
            chat_log_id: Associated ChatLog ID
            user_id: User submitting feedback
            rating: 1 (👍) or -1 (👎)
            comment: Optional comment
            correction: Optional suggested correction
            category: Category of issue
        
        Returns:
            Created FeedbackLog
        
        Raises:
            ValueError: If rating is not 1 or -1
        """
        if rating not in (1, -1):
            raise ValueError("Rating must be 1 or -1")
        
        # Verify chat_log exists
        chat_result = await db.execute(
            select(ChatLog).where(ChatLog.id == chat_log_id)
        )
        if chat_result.scalars().first() is None:
            raise ValueError(f"ChatLog {chat_log_id} not found")
        
        feedback = FeedbackLog(
            chat_log_id=chat_log_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            correction=correction,
            category=category,
            reviewed_by_admin=False,
        )
        
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        
        logger.info(f"Feedback submitted: {feedback.id} (rating={rating})")
        return feedback
    
    @staticmethod
    async def get_feedback_list(
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0,
        rating: Optional[int] = None,
        category: Optional[FeedbackCategory] = None,
        reviewed: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[List[FeedbackLog], int]:
        """
        Get list of feedback with optional filtering.
        
        Args:
            db: Database session
            limit: Results per page
            offset: Pagination offset
            rating: Filter by rating (1 or -1)
            category: Filter by category
            reviewed: Filter by review status
            date_from: Filter by created_at >= date
            date_to: Filter by created_at <= date
        
        Returns:
            Tuple of (feedback list, total count)
        """
        query = select(FeedbackLog)
        
        # Apply filters
        filters = []
        if rating is not None:
            filters.append(FeedbackLog.rating == rating)
        if category is not None:
            filters.append(FeedbackLog.category == category)
        if reviewed is not None:
            filters.append(FeedbackLog.reviewed_by_admin == reviewed)
        if date_from is not None:
            filters.append(FeedbackLog.created_at >= date_from)
        if date_to is not None:
            filters.append(FeedbackLog.created_at <= date_to)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Count total
        count_result = await db.execute(
            select(func.count(FeedbackLog.id)).where(
                and_(*filters) if filters else True
            )
        )
        total = count_result.scalar() or 0
        
        # Get paginated results
        query = query.order_by(desc(FeedbackLog.created_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        feedbacks = result.scalars().all()
        
        return feedbacks, total
    
    @staticmethod
    async def mark_reviewed(
        db: AsyncSession,
        feedback_id: UUID,
        admin_id: UUID,
        admin_notes: str,
    ) -> FeedbackLog:
        """
        Mark feedback as reviewed by admin.
        
        Args:
            db: Database session
            feedback_id: Feedback ID
            admin_id: Admin user ID
            admin_notes: Admin's notes/response
        
        Returns:
            Updated FeedbackLog
        """
        result = await db.execute(
            select(FeedbackLog).where(FeedbackLog.id == feedback_id)
        )
        feedback = result.scalars().first()
        
        if feedback is None:
            raise ValueError(f"Feedback {feedback_id} not found")
        
        feedback.reviewed_by_admin = True
        feedback.admin_notes = admin_notes
        
        await db.commit()
        await db.refresh(feedback)
        
        logger.info(f"Feedback {feedback_id} marked as reviewed by admin {admin_id}")
        return feedback
    
    @staticmethod
    async def mark_resolved(
        db: AsyncSession,
        feedback_id: UUID,
        admin_id: UUID,
    ) -> FeedbackLog:
        """
        Mark feedback as resolved.
        
        Args:
            db: Database session
            feedback_id: Feedback ID
            admin_id: Admin user ID
        
        Returns:
            Updated FeedbackLog
        """
        result = await db.execute(
            select(FeedbackLog).where(FeedbackLog.id == feedback_id)
        )
        feedback = result.scalars().first()
        
        if feedback is None:
            raise ValueError(f"Feedback {feedback_id} not found")
        
        feedback.resolved_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(feedback)
        
        logger.info(f"Feedback {feedback_id} marked as resolved")
        return feedback
    
    @staticmethod
    async def get_feedback_stats(
        db: AsyncSession,
        days: int = 30,
    ) -> FeedbackStats:
        """
        Get feedback statistics.
        
        Args:
            db: Database session
            days: Look back N days
        
        Returns:
            FeedbackStats object
        """
        since = datetime.utcnow() - timedelta(days=days) if days > 0 else datetime.min
        
        # Base query with date filter
        base_query = select(FeedbackLog).where(FeedbackLog.created_at >= since)
        
        # Total feedback
        total_result = await db.execute(
            select(func.count(FeedbackLog.id)).where(FeedbackLog.created_at >= since)
        )
        total = total_result.scalar() or 0
        
        # Positive feedback
        positive_result = await db.execute(
            select(func.count(FeedbackLog.id)).where(
                and_(
                    FeedbackLog.created_at >= since,
                    FeedbackLog.rating == 1,
                )
            )
        )
        positive_count = positive_result.scalar() or 0
        
        # Negative feedback
        negative_result = await db.execute(
            select(func.count(FeedbackLog.id)).where(
                and_(
                    FeedbackLog.created_at >= since,
                    FeedbackLog.rating == -1,
                )
            )
        )
        negative_count = negative_result.scalar() or 0
        
        # Satisfaction rate
        satisfaction_rate = (positive_count / total * 100) if total > 0 else 0
        
        # By category
        category_result = await db.execute(
            select(FeedbackLog.category, func.count(FeedbackLog.id)).where(
                and_(
                    FeedbackLog.created_at >= since,
                    FeedbackLog.category != None,
                )
            ).group_by(FeedbackLog.category)
        )
        
        by_category = {}
        for category, count in category_result.fetchall():
            by_category[category.value] = count
        
        # Unreviewed
        unreviewed_result = await db.execute(
            select(func.count(FeedbackLog.id)).where(
                and_(
                    FeedbackLog.created_at >= since,
                    FeedbackLog.reviewed_by_admin == False,
                )
            )
        )
        unreviewed_count = unreviewed_result.scalar() or 0
        
        return FeedbackStats(
            total=total,
            positive_count=positive_count,
            negative_count=negative_count,
            satisfaction_rate=round(satisfaction_rate, 1),
            by_category=by_category,
            unreviewed_count=unreviewed_count,
        )

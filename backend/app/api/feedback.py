"""Feedback API endpoints."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.dependencies import (
    get_current_user,
    require_staff_or_admin,
    require_admin,
)
from backend.app.models.user import User
from backend.app.models.analytics import FeedbackCategory, FeedbackSubmit, FeedbackRead
from backend.app.services.feedback_service import FeedbackService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FeedbackRead:
    """
    Submit feedback on a chat response.
    
    Args:
        feedback_data: Feedback submission data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created feedback record
    
    Raises:
        400: Invalid chat_log_id
        422: Invalid rating (must be 1 or -1)
    """
    try:
        feedback = await FeedbackService.submit_feedback(
            db=db,
            chat_log_id=feedback_data.chat_log_id,
            user_id=current_user.id,
            rating=feedback_data.rating,
            comment=feedback_data.comment,
            correction=feedback_data.correction,
            category=feedback_data.category,
        )
        
        logger.info(f"Feedback submitted by {current_user.email}: {feedback.id}")
        return FeedbackRead.model_validate(feedback)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback",
        )


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_feedback(
    limit: int = 20,
    offset: int = 0,
    rating: Optional[int] = None,
    category: Optional[str] = None,
    reviewed: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    _: User = Depends(require_staff_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List feedback with filtering (staff+ only).
    
    Args:
        limit: Results per page (1-100)
        offset: Pagination offset
        rating: Filter by rating (1 or -1)
        category: Filter by category (wrong_answer/incomplete/outdated/other)
        reviewed: Filter by review status
        date_from: ISO format date string
        date_to: ISO format date string
        _: Current user (role check only)
        db: Database session
    
    Returns:
        List of feedback with total count
    """
    try:
        if not (1 <= limit <= 100):
            raise ValueError("Limit must be between 1 and 100")
        
        # Parse dates
        parsed_date_from = None
        parsed_date_to = None
        
        if date_from:
            parsed_date_from = datetime.fromisoformat(date_from)
        if date_to:
            parsed_date_to = datetime.fromisoformat(date_to)
        
        # Parse category
        parsed_category = None
        if category:
            try:
                parsed_category = FeedbackCategory(category)
            except ValueError:
                raise ValueError(f"Invalid category: {category}")
        
        feedbacks, total = await FeedbackService.get_feedback_list(
            db=db,
            limit=limit,
            offset=offset,
            rating=rating,
            category=parsed_category,
            reviewed=reviewed,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
        )
        
        feedback_data = [FeedbackRead.model_validate(f) for f in feedbacks]
        
        return {
            "status": "success",
            "data": feedback_data,
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
    except Exception as e:
        logger.error(f"Error listing feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback",
        )


@router.patch("/{feedback_id}/review", response_model=FeedbackRead)
async def mark_feedback_reviewed(
    feedback_id: str,
    admin_notes: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> FeedbackRead:
    """
    Mark feedback as reviewed by admin (admin only).
    
    Args:
        feedback_id: Feedback ID
        admin_notes: Admin's notes/response
        admin_user: Current admin user
        db: Database session
    
    Returns:
        Updated feedback record
    """
    try:
        from uuid import UUID
        
        feedback = await FeedbackService.mark_reviewed(
            db=db,
            feedback_id=UUID(feedback_id),
            admin_id=admin_user.id,
            admin_notes=admin_notes,
        )
        
        return FeedbackRead.model_validate(feedback)
        
    except ValueError as e:
        if "invalid UUID" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid feedback ID",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error marking feedback reviewed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark feedback as reviewed",
        )


@router.patch("/{feedback_id}/resolve", response_model=FeedbackRead)
async def mark_feedback_resolved(
    feedback_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> FeedbackRead:
    """
    Mark feedback as resolved (admin only).
    
    Args:
        feedback_id: Feedback ID
        admin_user: Current admin user
        db: Database session
    
    Returns:
        Updated feedback record
    """
    try:
        from uuid import UUID
        
        feedback = await FeedbackService.mark_resolved(
            db=db,
            feedback_id=UUID(feedback_id),
            admin_id=admin_user.id,
        )
        
        return FeedbackRead.model_validate(feedback)
        
    except ValueError as e:
        if "invalid UUID" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid feedback ID",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error marking feedback resolved: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark feedback as resolved",
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_feedback_stats(
    days: int = 30,
    _: User = Depends(require_staff_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get feedback statistics (staff+ only).
    
    Args:
        days: Look back N days (0 = all time)
        _: Current user (role check only)
        db: Database session
    
    Returns:
        Feedback statistics
    """
    try:
        if not (0 <= days <= 365):
            raise ValueError("Days must be between 0 and 365")
        
        stats = await FeedbackService.get_feedback_stats(db, days=days)
        
        return {
            "status": "success",
            "data": stats.model_dump(),
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback statistics",
        )

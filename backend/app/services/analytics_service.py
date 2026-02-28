"""Analytics service for usage tracking and statistics."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from uuid import UUID

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.analytics import ChatLog, DocumentAccess, FeedbackLog, FeedbackCategory, FeedbackStats
from backend.app.models.user import User

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for logging and analyzing system usage."""
    
    @staticmethod
    async def log_chat(
        db: AsyncSession,
        user_id: UUID,
        question: str,
        answer: str,
        sources: Optional[List[str]],
        response_time_ms: int,
        tokens_used: Optional[int] = None,
        conversation_id: Optional[UUID] = None,
    ) -> ChatLog:
        """
        Log a chat interaction.
        
        Args:
            db: Database session
            user_id: User ID
            question: User's question
            answer: Assistant's answer
            sources: List of document names used
            response_time_ms: Response time in milliseconds
            tokens_used: Total tokens used (prompt + completion)
            conversation_id: Associated conversation ID
        
        Returns:
            Created ChatLog record
        """
        chat_log = ChatLog(
            user_id=user_id,
            question=question,
            answer=answer,
            sources=sources,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            conversation_id=conversation_id,
        )
        
        db.add(chat_log)
        await db.commit()
        await db.refresh(chat_log)
        
        logger.debug(f"Chat logged: {chat_log.id} ({response_time_ms}ms)")
        return chat_log
    
    @staticmethod
    async def log_document_access(
        db: AsyncSession,
        document_name: str,
        user_id: UUID,
        access_type: str,
        document_id: Optional[str] = None,
    ) -> DocumentAccess:
        """
        Log document access (retrieval, upload, deletion).
        
        Args:
            db: Database session
            document_name: Name of document
            user_id: User ID
            access_type: "retrieved", "uploaded", or "deleted"
            document_id: ChromaDB document ID (optional)
        
        Returns:
            Created DocumentAccess record
        """
        access_log = DocumentAccess(
            document_name=document_name,
            document_id=document_id,
            accessed_by_user_id=user_id,
            access_type=access_type,
        )
        
        db.add(access_log)
        await db.commit()
        await db.refresh(access_log)
        
        return access_log
    
    @staticmethod
    async def get_top_questions(
        db: AsyncSession,
        limit: int = 10,
        days: int = 30,
    ) -> List[Dict]:
        """
        Get most frequently asked questions.
        
        Args:
            db: Database session
            limit: Number of questions to return
            days: Look back N days
        
        Returns:
            List of {"question": str, "count": int}
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(ChatLog.question, func.count(ChatLog.id).label("count"))
            .where(ChatLog.created_at >= since)
            .group_by(ChatLog.question)
            .order_by(desc("count"))
            .limit(limit)
        )
        
        rows = result.fetchall()
        return [{"question": row[0], "count": row[1]} for row in rows]
    
    @staticmethod
    async def get_top_documents(
        db: AsyncSession,
        limit: int = 10,
        days: int = 30,
    ) -> List[Dict]:
        """
        Get most frequently retrieved documents.
        
        Args:
            db: Database session
            limit: Number of documents to return
            days: Look back N days
        
        Returns:
            List of {"document_name": str, "access_count": int}
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(DocumentAccess.document_name, func.count(DocumentAccess.id).label("count"))
            .where(
                and_(
                    DocumentAccess.created_at >= since,
                    DocumentAccess.access_type == "retrieved",
                )
            )
            .group_by(DocumentAccess.document_name)
            .order_by(desc("count"))
            .limit(limit)
        )
        
        rows = result.fetchall()
        return [{"document_name": row[0], "access_count": row[1]} for row in rows]
    
    @staticmethod
    async def get_daily_usage(
        db: AsyncSession,
        days: int = 30,
    ) -> List[Dict]:
        """
        Get daily usage statistics.
        
        Args:
            db: Database session
            days: Number of days to return
        
        Returns:
            List of {"date": str, "chat_count": int, "unique_users": int}
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(
                func.date(ChatLog.created_at).label("date"),
                func.count(ChatLog.id).label("chat_count"),
                func.count(func.distinct(ChatLog.user_id)).label("unique_users"),
            )
            .where(ChatLog.created_at >= since)
            .group_by(func.date(ChatLog.created_at))
            .order_by("date")
        )
        
        rows = result.fetchall()
        return [
            {
                "date": str(row[0]),
                "chat_count": row[1],
                "unique_users": row[2],
            }
            for row in rows
        ]
    
    @staticmethod
    async def get_summary_stats(
        db: AsyncSession,
        days: int = 30,
    ) -> Dict:
        """
        Get overall summary statistics.
        
        Args:
            db: Database session
            days: Look back N days (0 = all time)
        
        Returns:
            Dict with summary stats
        """
        since = datetime.utcnow() - timedelta(days=days) if days > 0 else datetime.min
        
        # Total chats
        total_chats_result = await db.execute(
            select(func.count(ChatLog.id)).where(ChatLog.created_at >= since)
        )
        total_chats = total_chats_result.scalar() or 0
        
        # Unique users
        unique_users_result = await db.execute(
            select(func.count(func.distinct(ChatLog.user_id))).where(ChatLog.created_at >= since)
        )
        total_users = unique_users_result.scalar() or 0
        
        # Average response time
        avg_response_result = await db.execute(
            select(func.avg(ChatLog.response_time_ms)).where(ChatLog.created_at >= since)
        )
        avg_response_time = avg_response_result.scalar() or 0
        
        # Total documents indexed
        docs_result = await db.execute(
            select(func.count(func.distinct(DocumentAccess.document_id))).where(
                DocumentAccess.access_type == "uploaded"
            )
        )
        total_docs = docs_result.scalar() or 0
        
        # Satisfaction rate (positive feedback / total feedback)
        positive_result = await db.execute(
            select(func.count(FeedbackLog.id)).where(FeedbackLog.rating == 1)
        )
        positive_count = positive_result.scalar() or 0
        
        total_feedback_result = await db.execute(
            select(func.count(FeedbackLog.id))
        )
        total_feedback = total_feedback_result.scalar() or 0
        
        satisfaction_rate = (positive_count / total_feedback * 100) if total_feedback > 0 else 0
        
        return {
            "total_chats": total_chats,
            "total_users": total_users,
            "avg_response_time_ms": round(float(avg_response_time), 2),
            "total_docs_indexed": total_docs,
            "satisfaction_rate": round(satisfaction_rate, 1),
        }
    
    @staticmethod
    async def get_unanswered_questions(
        db: AsyncSession,
        threshold: float = 0.5,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Get questions where answers were likely low-confidence.
        
        Detection method: Checks if answer contains phrases like "I don't know", 
        "unclear", "not found", etc.
        
        Args:
            db: Database session
            threshold: Confidence threshold (unused in current implementation)
            limit: Max questions to return
        
        Returns:
            List of {"question": str, "answer_preview": str, "created_at": datetime}
        """
        low_confidence_phrases = [
            "i don't know",
            "i cannot",
            "i'm unable",
            "not found",
            "unclear",
            "uncertain",
            "no information",
            "outside my knowledge",
        ]
        
        # Find chats where answer contains low-confidence phrases
        results = []
        query_result = await db.execute(
            select(ChatLog).order_by(desc(ChatLog.created_at)).limit(limit * 3)
        )
        
        all_logs = query_result.scalars().all()
        
        for log in all_logs:
            if any(phrase in log.answer.lower() for phrase in low_confidence_phrases):
                results.append({
                    "question": log.question,
                    "answer_preview": log.answer[:200],
                    "created_at": log.created_at,
                })
                if len(results) >= limit:
                    break
        
        return results

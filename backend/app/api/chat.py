"""
Chat API with RAG
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.rag.chain import invoke_rag
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class SourceInfo(BaseModel):
    content: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question and get an answer based on RAG.

    The core logic is blocking (embeddings lookup + network call to
    the LLM).  FastAPI runs async endpoints on the event loop, so we
    offload the work to a threadpool with ``run_in_threadpool`` to
    prevent the server from starving other requests.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message vide")

    try:
        # heavy work is delegated to thread pool to avoid blocking the
        # event loop and to keep uvicorn responsive.  this also makes
        # it easier to apply timeouts at the client side.
        from starlette.concurrency import run_in_threadpool

        logger.info(f"Processing chat request: {request.message[:50]}...")

        # Set timeout for the entire RAG operation
        try:
            answer, sources = await asyncio.wait_for(
                run_in_threadpool(invoke_rag, request.message),
                timeout=settings.RAG_TIMEOUT,
            )
            logger.info(f"Chat request completed successfully")
            return ChatResponse(
                answer=answer,
                sources=[
                    SourceInfo(content=content, source=source)
                    for content, source in sources
                ],
            )
        except asyncio.TimeoutError:
            logger.error(f"RAG operation timed out after {settings.RAG_TIMEOUT}s")
            raise HTTPException(
                status_code=504,
                detail=f"La requête a dépassé le délai d'attente ({settings.RAG_TIMEOUT}s). Veuillez réessayer."
            )
            
    except ValueError as e:
        logger.error(f"ValueError in chat: {str(e)}")
        if "GROQ_API_KEY" in str(e):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

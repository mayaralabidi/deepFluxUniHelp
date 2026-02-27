"""
Chat API with RAG
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.rag.chain import invoke_rag

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
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message vide")

    try:
        answer, sources = invoke_rag(request.message)
        return ChatResponse(
            answer=answer,
            sources=[
                SourceInfo(content=content, source=source)
                for content, source in sources
            ],
        )
    except ValueError as e:
        if "GROQ_API_KEY" in str(e):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

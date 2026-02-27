"""
deepFluxUniHelp - Backend API
FastAPI application entry point
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.documents import router as documents_router
from backend.app.api.chat import router as chat_router
from backend.app.api.generate import router as generate_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="deepFluxUniHelp",
    description="Assistant IA pour la vie étudiante universitaire",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Pre-load models on startup to avoid timeout on first chat request."""
    logger.info("Preloading RAG models on startup...")
    try:
        from backend.app.rag.chain import get_rag_chain
        from backend.app.rag.vectorstore import get_vectorstore
        
        # Load vectorstore and embeddings
        logger.info("Loading embeddings model...")
        vectorstore = get_vectorstore()
        logger.info("Embeddings model loaded successfully")
        
        # Load RAG chain (LLM)
        logger.info("Loading RAG chain and LLM...")
        chain, retriever = get_rag_chain()
        logger.info("RAG chain loaded successfully")
        
        logger.info("✅ All models preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload models: {str(e)}")
        # Don't crash the server, but log the error


@app.get("/")
def root():
    """Health check"""
    return {"status": "ok", "message": "deepFluxUniHelp API"}


@app.get("/health")
def health():
    """Health endpoint for Docker/load balancers"""
    return {"status": "healthy"}


app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(generate_router)

# Phase 5: Integration
# - POST /chat
# - POST /generate
# - POST /documents (upload/index)
# - GET /documents

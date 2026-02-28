"""
deepFluxUniHelp - Backend API
FastAPI application entry point
"""

import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.auth import router as auth_router
from backend.app.api.documents import router as documents_router
from backend.app.api.chat import router as chat_router
from backend.app.api.generate import router as generate_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.feedback import router as feedback_router
from backend.app.core.database import init_db
from backend.app.core.config import settings
from backend.app.core.security import hash_password
from backend.app.models.user import User, UserRole

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
    """Initialize database and preload models on startup."""
    logger.info("🚀 Starting up deepFluxUniHelp...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized")
        
        # Create default admin user if no users exist
        from sqlalchemy import select
        from backend.app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users_exist = result.scalars().first() is not None
            
            if not users_exist:
                logger.info("No users found. Creating default admin user...")
                admin_user = User(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_PASSWORD),
                    full_name="Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                db.add(admin_user)
                await db.commit()
                logger.info(f"✅ Default admin user created: {settings.ADMIN_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Preload RAG models
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


# Include routers
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(generate_router)
app.include_router(analytics_router)
app.include_router(feedback_router)

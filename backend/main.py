"""
deepFluxUniHelp - Backend API
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.documents import router as documents_router
from backend.app.api.chat import router as chat_router
from backend.app.api.generate import router as generate_router

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

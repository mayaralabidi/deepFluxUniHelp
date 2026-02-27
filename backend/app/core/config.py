"""
Application configuration
Loads from environment variables
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of backend/)
_env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    """Application settings"""

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3-8b-8192")

    # RAG
    CHROMA_PERSIST_DIR: Path = Path(
        os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    )
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
    )
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K: int = int(os.getenv("TOP_K", "4"))


settings = Settings()

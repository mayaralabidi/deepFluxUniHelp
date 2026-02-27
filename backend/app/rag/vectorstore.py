"""
ChromaDB vector store with sentence-transformers embeddings
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from backend.app.core.config import settings


COLLECTION_NAME = "university_docs"


def get_embeddings() -> HuggingFaceEmbeddings:
    """Create HuggingFace embeddings (sentence-transformers)."""
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )


def get_vectorstore(persist_directory: Path | None = None) -> Chroma:
    """
    Get or create the ChromaDB vector store.
    """
    persist_dir = str(persist_directory or settings.CHROMA_PERSIST_DIR)
    persist_dir_path = Path(persist_dir)
    persist_dir_path.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )


def get_retriever(vectorstore: Chroma, top_k: int | None = None) -> Chroma:
    """Create a retriever from the vector store."""
    k = top_k or settings.TOP_K
    return vectorstore.as_retriever(search_kwargs={"k": k})


def clear_collection(vectorstore: Chroma) -> None:
    """Clear all documents from the collection."""
    vectorstore.delete_collection()

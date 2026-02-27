"""
Document ingestion pipeline: load → chunk → index
"""

from pathlib import Path

from langchain_core.documents import Document

from backend.app.rag.chunking import split_documents
from backend.app.rag.loaders import load_document, load_documents_from_directory
from backend.app.rag.vectorstore import get_vectorstore


def ingest_file(file_path: Path) -> int:
    """
    Ingest a single file into the vector store.
    Returns the number of chunks added.
    """
    docs = load_document(file_path)
    chunks = split_documents(docs)
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    return len(chunks)


def ingest_directory(dir_path: Path) -> dict[str, int]:
    """
    Ingest all supported documents from a directory.
    Returns stats: {"files": N, "chunks": M}
    """
    docs = load_documents_from_directory(dir_path)
    if not docs:
        return {"files": 0, "chunks": 0}

    chunks = split_documents(docs)
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    sources = {doc.metadata.get("source", "") for doc in docs}
    return {"files": len(sources), "chunks": len(chunks)}


def search(query: str, top_k: int | None = None) -> list[tuple[Document, float]]:
    """
    Search the vector store and return relevant documents with scores.
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=top_k or 4)
    return results

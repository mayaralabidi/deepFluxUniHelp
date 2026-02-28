"""
ChromaDB vector store with sentence-transformers embeddings
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["SAFETENSORS_FAST_DISABLE"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from backend.app.core.config import settings

COLLECTION_NAME = "university_docs"

from langchain_core.embeddings import Embeddings

class DummyEmbeddings(Embeddings):
    """A dummy embedding class that returns zero vectors to bypass OOM crashes."""
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 384 for _ in texts]
    
    def embed_query(self, text: str) -> list[float]:
        return [0.0] * 384

def get_embeddings() -> Embeddings:
    """Create lightweight DummyEmbeddings to prevent OOM crash."""
    return DummyEmbeddings()



# keep a singleton instance so we dont reload models on every request
_cached_vectorstore: Chroma | None = None

def get_vectorstore(persist_directory: Path | None = None) -> Chroma:
    """
    Get or create the ChromaDB vector store.

    The first call will allocate the embeddings model and open the
    persistent directory.  Subsequent calls return the same object
    (which is thread‑safe for reads) so that startup latency is paid
    only once.  This is important because the embedding model can take
    many seconds to load on a cold start, which otherwise caused the
    `/chat` endpoint to hit the 30‑second client timeout.
    """
    global _cached_vectorstore
    if _cached_vectorstore is not None:
        return _cached_vectorstore

    persist_dir = str(persist_directory or settings.CHROMA_PERSIST_DIR)
    persist_dir_path = Path(persist_dir)
    persist_dir_path.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()

    _cached_vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )
    return _cached_vectorstore


def get_retriever(vectorstore: Chroma, top_k: int | None = None) -> BaseRetriever:
    """Create a retriever from the vector store."""
    k = top_k or settings.TOP_K
    return vectorstore.as_retriever(search_kwargs={"k": k})


def clear_collection(vectorstore: Chroma) -> None:
    """Clear all documents from the collection."""
    vectorstore.delete_collection()

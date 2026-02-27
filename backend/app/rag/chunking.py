"""
Text chunking and splitting with configurable parameters
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from backend.app.core.config import settings


def create_text_splitter(
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> RecursiveCharacterTextSplitter:
    """Create a text splitter with configurable chunk size and overlap."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def split_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """
    Split documents into chunks, preserving metadata.
    """
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    return splitter.split_documents(documents)

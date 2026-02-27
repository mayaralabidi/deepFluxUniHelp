"""
Document loaders for PDF, DOCX, TXT, Markdown
"""

from pathlib import Path
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)


def get_loader_for_path(file_path: Path) -> BaseLoader | None:
    """Return the appropriate loader for a file path."""
    suffix = file_path.suffix.lower()
    loaders = {
        ".pdf": lambda: PyPDFLoader(str(file_path)),
        ".docx": lambda: Docx2txtLoader(str(file_path)),
        ".doc": lambda: Docx2txtLoader(str(file_path)),
        ".txt": lambda: TextLoader(str(file_path), encoding="utf-8"),
        ".md": lambda: TextLoader(str(file_path), encoding="utf-8"),
    }
    if suffix in loaders:
        return loaders[suffix]()
    return None


def load_document(file_path: Path) -> list[Document]:
    """
    Load a single document and return its content as LangChain Documents.
    Adds source file path to metadata.
    """
    loader = get_loader_for_path(file_path)
    if loader is None:
        raise ValueError(f"Format non supporté: {file_path.suffix}")

    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = str(file_path)
        doc.metadata["filename"] = file_path.name
    return docs


def load_documents_from_directory(
    dir_path: Path,
    suffixes: tuple[str, ...] = (".pdf", ".docx", ".doc", ".txt", ".md"),
) -> list[Document]:
    """
    Load all supported documents from a directory recursively.
    """
    all_docs: list[Document] = []
    for path in dir_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in suffixes:
            try:
                docs = load_document(path)
                all_docs.extend(docs)
            except Exception as e:
                # Log but continue
                print(f"Erreur chargement {path}: {e}")
    return all_docs

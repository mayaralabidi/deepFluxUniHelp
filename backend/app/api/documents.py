"""
Document ingestion and search API
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.app.rag.ingestion import ingest_file, ingest_directory, search
from backend.app.rag.vectorstore import clear_collection, get_vectorstore

router = APIRouter(prefix="/documents", tags=["documents"])


class SearchQuery(BaseModel):
    query: str
    top_k: int = 4


class SearchResult(BaseModel):
    content: str
    source: str
    score: float


class IngestResponse(BaseModel):
    message: str
    files: int
    chunks: int


@router.post("/ingest-file", response_model=IngestResponse)
async def ingest_uploaded_file(
    file: UploadFile = File(...),
):
    """Upload and index a single document (PDF, DOCX, TXT, MD)."""
    suffix = Path(file.filename or "").suffix.lower()
    allowed = {".pdf", ".docx", ".doc", ".txt", ".md"}
    if suffix not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté. Utilisez: {', '.join(allowed)}",
        )

    # Save temporarily and ingest
    suffix_map = {".doc": ".docx"}
    ext = suffix_map.get(suffix, suffix)
    with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        chunks = ingest_file(tmp_path)
        return IngestResponse(
            message=f"Document indexé: {file.filename}",
            files=1,
            chunks=chunks,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


class IngestDirectoryRequest(BaseModel):
    path: str = "data/sample"


@router.post("/ingest-directory", response_model=IngestResponse)
async def ingest_directory_route(body: IngestDirectoryRequest):
    """
    Index all documents in a directory.
    path: relative path from project root (e.g. data/sample)
    """
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    dir_path = project_root / body.path
    if not dir_path.is_dir():
        raise HTTPException(
            status_code=400, detail=f"Répertoire invalide: {body.path}"
        )

    try:
        stats = ingest_directory(dir_path)
        return IngestResponse(
            message=f"Indexation terminée: {body.path}",
            files=stats["files"],
            chunks=stats["chunks"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=list[SearchResult])
async def search_documents(query: SearchQuery):
    """Search for relevant document chunks."""
    try:
        results = search(query.query, top_k=query.top_k)
        return [
            SearchResult(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                score=float(score),
            )
            for doc, score in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset")
async def reset_index():
    """Clear the document index (use with caution)."""
    try:
        vs = get_vectorstore()
        clear_collection(vs)
        return {"message": "Index réinitialisé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Document ingestion and search API
"""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.rag.ingestion import ingest_file, ingest_directory, search
from backend.app.rag.vectorstore import clear_collection, get_vectorstore
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_admin
from backend.app.models.user import User
from backend.app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

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
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upload and index a single document (PDF, DOCX, TXT, MD). Admin only."""
    suffix = Path(file.filename or "").suffix.lower()
    allowed = {".pdf", ".docx", ".doc", ".txt", ".md"}
    if suffix not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        
        # Log document upload
        await AnalyticsService.log_document_access(
            db=db,
            document_name=file.filename or "unknown",
            user_id=current_user.id,
            access_type="uploaded",
        )
        
        logger.info(f"Document uploaded: {file.filename} by {current_user.email}")
        
        return IngestResponse(
            message=f"Document indexé: {file.filename}",
            files=1,
            chunks=chunks,
        )
    except Exception as e:
        logger.error(f"Error ingesting file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        tmp_path.unlink(missing_ok=True)


class IngestDirectoryRequest(BaseModel):
    path: str = "data/sample"


@router.post("/ingest-directory", response_model=IngestResponse)
async def ingest_directory_route(
    body: IngestDirectoryRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Index all documents in a directory. Admin only.
    path: relative path from project root (e.g. data/sample)
    """
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    dir_path = project_root / body.path
    if not dir_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Répertoire invalide: {body.path}"
        )

    try:
        stats = ingest_directory(dir_path)
        
        # Log directory ingestion
        await AnalyticsService.log_document_access(
            db=db,
            document_name=body.path,
            user_id=current_user.id,
            access_type="uploaded",
        )
        
        logger.info(f"Directory ingested: {body.path} by {current_user.email}")
        
        return IngestResponse(
            message=f"Indexation terminée: {body.path}",
            files=stats["files"],
            chunks=stats["chunks"],
        )
    except Exception as e:
        logger.error(f"Error ingesting directory {body.path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/search", response_model=list[SearchResult])
async def search_documents(
    query: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search for relevant document chunks. Requires authentication."""
    try:
        results = search(query.query, top_k=query.top_k)
        
        # Log search queries from all documents retrieved
        for doc, score in results:
            source_name = doc.metadata.get("source", "unknown")
            await AnalyticsService.log_document_access(
                db=db,
                document_name=source_name,
                user_id=current_user.id,
                access_type="searched",
            )
        
        logger.info(
            f"Search performed: '{query.query[:50]}' by {current_user.email} "
            f"returned {len(results)} results"
        )
        
        return [
            SearchResult(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                score=float(score),
            )
            for doc, score in results
        ]
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/reset")
async def reset_index(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Clear the document index (use with caution). Admin only."""
    try:
        vs = get_vectorstore()
        clear_collection(vs)
        
        # Log reset operation
        await AnalyticsService.log_document_access(
            db=db,
            document_name="INDEX_RESET",
            user_id=current_user.id,
            access_type="deleted",
        )
        
        logger.warning(f"Index reset by {current_user.email}")
        
        return {"message": "Index réinitialisé"}
    except Exception as e:
        logger.error(f"Error resetting index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

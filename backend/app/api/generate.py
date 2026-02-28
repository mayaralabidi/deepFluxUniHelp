"""
Document generation API
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.generator import generate_document, PROMPTS
from backend.app.services.pdf_export import text_to_pdf
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


class GenerateRequest(BaseModel):
    doc_type: str
    params: dict


@router.post("/", response_model=dict)
async def generate_body(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a document (attestation, réclamation, convention_stage).
    Returns the generated text. Requires authentication.
    """
    if request.doc_type not in PROMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type inconnu. Utilisez: {', '.join(PROMPTS.keys())}",
        )

    try:
        text = generate_document(request.doc_type, **request.params)
        
        # Log document generation
        await AnalyticsService.log_document_access(
            db=db,
            document_name=f"generated_{request.doc_type}",
            user_id=current_user.id,
            access_type="generated",
        )
        
        logger.info(
            f"Document generated: {request.doc_type} by {current_user.email}"
        )
        
        return {"text": text, "doc_type": request.doc_type}
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        logger.error(f"ValueError generating {request.doc_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating {request.doc_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.post("/pdf")
async def generate_pdf(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a document and return it as PDF. Requires authentication.
    """
    if request.doc_type not in PROMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type inconnu. Utilisez: {', '.join(PROMPTS.keys())}",
        )

    try:
        text = generate_document(request.doc_type, **request.params)
        titles = {
            "attestation": "Demande d'attestation",
            "reclamation": "Réclamation",
            "convention_stage": "Demande de convention de stage",
        }
        title = titles.get(request.doc_type, "Document")
        pdf_bytes = text_to_pdf(text, title=title)
        
        # Log PDF generation
        await AnalyticsService.log_document_access(
            db=db,
            document_name=f"generated_pdf_{request.doc_type}",
            user_id=current_user.id,
            access_type="generated",
        )
        
        logger.info(
            f"PDF generated: {request.doc_type}_pdf by {current_user.email}"
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.doc_type}.pdf"
            },
        )
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        logger.error(f"ValueError generating PDF {request.doc_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating PDF {request.doc_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )


@router.get("/types")
async def list_types(current_user: User = Depends(get_current_user)):
    """List available document types. Requires authentication."""
    return {"types": list(PROMPTS.keys())}

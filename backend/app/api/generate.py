"""
Document generation API
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from backend.app.services.generator import generate_document, PROMPTS
from backend.app.services.pdf_export import text_to_pdf

router = APIRouter(prefix="/generate", tags=["generate"])


class GenerateRequest(BaseModel):
    doc_type: str
    params: dict


@router.post("/", response_model=dict)
async def generate_body(request: GenerateRequest):
    """
    Generate a document (attestation, réclamation, convention_stage).
    Returns the generated text.
    """
    if request.doc_type not in PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Type inconnu. Utilisez: {', '.join(PROMPTS.keys())}",
        )

    try:
        text = generate_document(request.doc_type, **request.params)
        return {"text": text, "doc_type": request.doc_type}
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.post("/pdf")
async def generate_pdf(request: GenerateRequest):
    """
    Generate a document and return it as PDF.
    """
    if request.doc_type not in PROMPTS:
        raise HTTPException(
            status_code=400,
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
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.doc_type}.pdf"
            },
        )
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/types")
async def list_types():
    """List available document types."""
    return {"types": list(PROMPTS.keys())}

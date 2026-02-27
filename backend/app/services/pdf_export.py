"""
PDF export for generated documents
"""

from io import BytesIO
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT


def _escape(s: str) -> str:
    return html.escape(s, quote=True).replace("\n", "<br/>")


def text_to_pdf(text: str, title: str = "Document") -> bytes:
    """
    Convert plain text to PDF.
    Returns PDF bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm
    )
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
    )
    title_style = ParagraphStyle(
        name="Title",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=20,
    )

    story = []
    story.append(Paragraph(_escape(title), title_style))
    story.append(Spacer(1, 0.5*cm))

    for para in text.split("\n\n"):
        if para.strip():
            story.append(Paragraph(_escape(para), style))
            story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    return buffer.getvalue()

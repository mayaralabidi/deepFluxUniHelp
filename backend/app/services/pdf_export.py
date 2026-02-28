"""
PDF export for generated documents — professional letterhead layout.
"""

from datetime import date
from io import BytesIO
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.colors import HexColor

# ── Brand colours ──────────────────────────────────────────────────────────
PRIMARY   = HexColor("#6C63FF")   # indigo
SECONDARY = HexColor("#00D4AA")   # teal
DARK      = HexColor("#1A1F2E")
MID_GREY  = HexColor("#4A5568")
LIGHT_GREY = HexColor("#8B95A8")
RULE_GREY  = HexColor("#D1D5DB")
PAGE_BG    = colors.white


# ── Helpers ─────────────────────────────────────────────────────────────────
def _esc(s: str) -> str:
    """HTML-escape; convert newlines to <br/>."""
    return html.escape(s, quote=True).replace("\n", "<br/>")


def _style(name, **kw) -> ParagraphStyle:
    return ParagraphStyle(name=name, **kw)


# ── Page template with header/footer drawn on canvas ────────────────────────
def _make_page_template(doc, title: str, doc_type_label: str):
    """Return a PageTemplate that draws the letterhead on every page."""

    def on_page(canvas, doc):
        canvas.saveState()
        w, h = A4

        # ── Top colour bar ────────────────────────────────────────────────
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, h - 1.6 * cm, w, 1.6 * cm, fill=1, stroke=0)

        # Institution name (left)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawString(2 * cm, h - 1.15 * cm, "UniHelp")

        # Document type label (right)
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(HexColor("#D1FAF3"))
        canvas.drawRightString(w - 2 * cm, h - 1.15 * cm, doc_type_label.upper())

        # ── Thin accent line just below the bar ──────────────────────────
        canvas.setStrokeColor(SECONDARY)
        canvas.setLineWidth(2)
        canvas.line(0, h - 1.65 * cm, w, h - 1.65 * cm)

        # ── Footer ───────────────────────────────────────────────────────
        canvas.setStrokeColor(RULE_GREY)
        canvas.setLineWidth(0.5)
        canvas.line(2 * cm, 1.6 * cm, w - 2 * cm, 1.6 * cm)

        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(LIGHT_GREY)
        today = date.today().strftime("%d/%m/%Y")
        canvas.drawString(2 * cm, 1.1 * cm, f"Généré par UniHelp · {today}")
        canvas.drawRightString(
            w - 2 * cm, 1.1 * cm,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    frame = Frame(
        2 * cm, 2.2 * cm,
        A4[0] - 4 * cm, A4[1] - 4.2 * cm,
        id="main",
    )
    return PageTemplate(id="standard", frames=[frame], onPage=on_page)


# ── Styles ──────────────────────────────────────────────────────────────────
DOC_TITLE = _style(
    "DocTitle",
    fontName="Helvetica-Bold",
    fontSize=17,
    textColor=PRIMARY,
    spaceAfter=4,
    leading=22,
    alignment=TA_LEFT,
)
DOC_SUBTITLE = _style(
    "DocSubtitle",
    fontName="Helvetica-Oblique",
    fontSize=10,
    textColor=LIGHT_GREY,
    spaceAfter=14,
    leading=14,
    alignment=TA_LEFT,
)
SECTION_LABEL = _style(
    "SectionLabel",
    fontName="Helvetica-Bold",
    fontSize=9,
    textColor=PRIMARY,
    spaceBefore=10,
    spaceAfter=3,
    leading=12,
    alignment=TA_LEFT,
)
BODY = _style(
    "Body",
    fontName="Helvetica",
    fontSize=10.5,
    textColor=DARK,
    leading=16,
    spaceBefore=4,
    spaceAfter=6,
    alignment=TA_JUSTIFY,
)
BODY_SMALL = _style(
    "BodySmall",
    fontName="Helvetica",
    fontSize=9,
    textColor=MID_GREY,
    leading=13,
    spaceAfter=4,
    alignment=TA_LEFT,
)


# ── Line detection helpers ───────────────────────────────────────────────────
_OBJET_RE  = re.compile(r"^(objet\s*:|object\s*:)", re.I)
_SIGN_KEYS = {"cordialement", "sincèrement", "veuillez agréer",
              "dans l'attente", "dans cette attente", "je vous prie"}


def _is_section_header(line: str) -> bool:
    """True for short ALL-CAPS lines or 'Objet :' lines."""
    stripped = line.strip()
    if _OBJET_RE.match(stripped):
        return True
    if len(stripped) < 60 and stripped == stripped.upper() and stripped.replace(" ", ""):
        return True
    return False


def _is_salutation_or_close(line: str) -> bool:
    lower = line.strip().lower()
    return any(lower.startswith(k) for k in _SIGN_KEYS)


# ── Main entry point ─────────────────────────────────────────────────────────
def text_to_pdf(text: str, title: str = "Document", doc_type: str = "") -> bytes:
    """
    Convert AI-generated letter text to a professional PDF.
    Returns PDF bytes.
    """
    buffer = BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.4 * cm,
        bottomMargin=2.4 * cm,
    )

    # Map doc_type key → human label
    type_labels = {
        "attestation":      "Demande d'attestation",
        "reclamation":      "Réclamation",
        "convention_stage": "Convention de stage",
    }
    doc_type_label = type_labels.get(doc_type, title)

    doc.addPageTemplates([_make_page_template(doc, title, doc_type_label)])

    story = []

    # ── Document title block ─────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(_esc(title), DOC_TITLE))
    story.append(HRFlowable(
        width="100%", thickness=1.5,
        color=SECONDARY, spaceAfter=12,
    ))

    # ── Body: parse paragraphs ───────────────────────────────────────────
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for para in paragraphs:
        lines = para.splitlines()

        # Single-line section header (e.g. "Objet : ..." or "MADAME, MONSIEUR,")
        if len(lines) == 1 and _is_section_header(lines[0]):
            story.append(Paragraph(_esc(lines[0].strip()), SECTION_LABEL))
            continue

        # Salutation / closing paragraph → slightly smaller, italic feel
        if len(lines) == 1 and _is_salutation_or_close(lines[0]):
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(_esc(para), BODY_SMALL))
            continue

        # Normal paragraph
        story.append(Paragraph(_esc(para), BODY))

    # ── Closing spacer ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))

    doc.build(story)
    return buffer.getvalue()

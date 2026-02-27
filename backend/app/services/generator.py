"""
Document generation: attestation, réclamation, convention de stage
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from backend.app.core.config import settings


PROMPTS = {
    "attestation": """Génère un email de demande d'attestation d'inscription. Utilise les informations suivantes:

- Nom complet: {nom}
- Numéro étudiant: {numero_etudiant}
- Type d'attestation: {type_attestation}
- Motif: {motif}
- Date: {date}

Format: email formel adressé au secrétariat, avec objet, formule d'appel, corps du message, formule de politesse et signature.""",

    "reclamation": """Génère un email de réclamation. Utilise les informations suivantes:

- Nom complet: {nom}
- Numéro étudiant: {numero_etudiant}
- Matière ou élément concerné: {matiere}
- Description du problème: {description}
- Pièces jointes éventuelles: {pieces_jointes}

Format: email formel, courtois mais ferme, avec objet, formule d'appel, exposé des faits, demande, formule de politesse et signature.""",

    "convention_stage": """Génère une demande de convention de stage. Utilise les informations suivantes:

- Nom complet: {nom}
- Numéro étudiant: {numero_etudiant}
- Entreprise: {entreprise}
- Dates du stage: {dates}
- Tuteur entreprise: {tuteur_entreprise}
- Référent pédagogique: {referent_pedagogique}
- Description du stage: {description}

Format: email formel au service des stages ou au référent pédagogique, avec objet, toutes les informations nécessaires pour établir la convention, formule de politesse et signature.""",
}


# Default keys per doc_type
DEFAULT_PARAMS = {
    "attestation": {"nom": "", "numero_etudiant": "", "type_attestation": "Inscription", "motif": "", "date": ""},
    "reclamation": {"nom": "", "numero_etudiant": "", "matiere": "", "description": "", "pieces_jointes": "Aucune"},
    "convention_stage": {
        "nom": "", "numero_etudiant": "", "entreprise": "", "dates": "",
        "tuteur_entreprise": "Non renseigné", "referent_pedagogique": "Non renseigné", "description": "",
    },
}


def generate_document(doc_type: str, **kwargs) -> str:
    """
    Generate a document based on type and parameters.
    doc_type: attestation, reclamation, convention_stage
    """
    if doc_type not in PROMPTS:
        raise ValueError(f"Type inconnu: {doc_type}")

    defaults = DEFAULT_PARAMS.get(doc_type, {})
    params = {**defaults, **{k: v for k, v in kwargs.items() if k in defaults}}
    params = {k: (v if v is not None and str(v).strip() else defaults.get(k, "")) for k, v in params.items()}

    if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
        raise ValueError(
            "GROQ_API_KEY non configuré. Ajoutez votre clé dans le fichier .env"
        )

    llm = ChatGroq(
        model=settings.LLM_MODEL,
        temperature=0.4,
        api_key=settings.GROQ_API_KEY,
    )
    prompt = ChatPromptTemplate.from_template(PROMPTS[doc_type])
    chain = prompt | llm
    result = chain.invoke(params)
    return result.content if hasattr(result, "content") else str(result)

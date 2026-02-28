"""
RAG chain: retriever + LLM for answering questions
"""

from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

from backend.app.core.config import settings
from backend.app.rag.vectorstore import get_vectorstore


SYSTEM_PROMPT = """Tu es l'assistant de l'université. Tu aides les étudiants avec des réponses claires, utiles et polies.

Règles importantes:
- Réponds en français de manière claire et concise
- Si le contexte ci-dessous contient des extraits de documents: base-toi UNIQUEMENT sur ce contexte. Si l'information n'y est pas, dis-le et suggère de contacter le secrétariat.
- Si le contexte est vide (aucun document): réponds quand même en t'appuyant sur tes connaissances générales. Si une règle/procédure peut varier selon l'université, indique-le et propose de préciser l'université/filière/année, ou de vérifier auprès du secrétariat.
- Ne mentionne pas de contraintes techniques (mémoire, serveur, RAG, etc.).
- Quand tu utilises le contexte, cite la source entre parenthèses, par ex. (calendrier_2025.txt) ou (reglement_examens.pdf p.12).
- Si le contexte n'est pas vide, termine par une ligne: "📎 Sources : ..." listant les sources réellement utilisées (sans inventer).
- Sois professionnel et bienveillant
- Si l'utilisateur continue une conversation précédente, tiens compte de l'historique pour plus de contexte

{conversation_history}

Contexte:
{context}

Question: {question}"""


def format_docs(docs):
    """Format retrieved documents for the prompt."""
    parts: list[str] = []
    for d in docs:
        filename = d.metadata.get("filename")
        if not filename:
            src = d.metadata.get("source")
            filename = Path(str(src)).name if src else "document"

        page = d.metadata.get("page")
        page_label = f" p.{int(page) + 1}" if page is not None else ""
        parts.append(f"[Source: {filename}{page_label}]\n{d.page_content}")

    return "\n\n---\n\n".join(parts)



# cache chain and retriever so they are only created once
_rag_chain = None
_retriever = None

def get_rag_chain():
    """Build and return the RAG chain.

    The chain and its underlying retriever (which in turn holds the
    vectorstore) are expensive to initialise because they load a
    sentence-transformers model and wire up the LLM.  We keep them in
    module globals so repeated calls (e.g. for every `/chat` request)
    are cheap.
    """
    global _rag_chain, _retriever
    if _rag_chain is not None and _retriever is not None:
        return _rag_chain, _retriever

    if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
        raise ValueError(
            "GROQ_API_KEY non configuré. Ajoutez votre clé dans le fichier .env"
        )

    vectorstore = get_vectorstore()
    _retriever = vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K})

    llm = ChatGroq(
        model=settings.LLM_MODEL,
        temperature=0.3,
        api_key=settings.GROQ_API_KEY,
        timeout=settings.LLM_TIMEOUT,  # timeout for API calls
    )

    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    # Simplified chain to just format the prompt and call the LLM
    # The context will be passed explicitly during invoke()
    _rag_chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    return _rag_chain, _retriever



from typing import Tuple, List, Optional

def _format_conversation_history(messages: Optional[List] = None) -> str:
    """Format recent conversation messages for context."""
    if not messages:
        return ""
    
    history_lines = ["Historique récent de la conversation:"]
    for msg in messages:
        role = "Étudiant" if msg.role.value == "user" else "Assistant"
        history_lines.append(f"{role}: {msg.content[:200]}")  # Truncate long messages
    
    return "\n".join(history_lines) + "\n\n"


def invoke_rag(
    question: str,
    recent_messages: Optional[List] = None,
) -> Tuple[str, List[tuple[str, str]]]:
    """
    Invoke RAG with optional conversation history and return (answer, sources).

    Args:
        question: Current user question
        recent_messages: Optional list of recent Message objects for context

    Returns:
        Tuple of (answer, sources) where sources is list of (content, source_path) tuples
    """
    chain, retriever = get_rag_chain()

    # If retrieval is available, use it; otherwise, fall back to general knowledge mode (empty context).
    context = ""
    sources: List[tuple[str, str]] = []
    if retriever is not None:
        try:
            docs = retriever.get_relevant_documents(question)
            if docs:
                context = format_docs(docs)
                # Only expose lightweight, human-readable source labels (deduped)
                seen: set[str] = set()
                for d in docs:
                    filename = d.metadata.get("filename")
                    if not filename:
                        src = d.metadata.get("source")
                        filename = Path(str(src)).name if src else "document"

                    page = d.metadata.get("page")
                    label = f"{filename} (p.{int(page) + 1})" if page is not None else str(filename)
                    if label in seen:
                        continue
                    seen.add(label)
                    sources.append((d.page_content[:300], label))
        except Exception:
            # Any retrieval failure should not block answering.
            context = ""
            sources = []

    # Format conversation history for the prompt
    conversation_history = _format_conversation_history(recent_messages)

    # Invoke chain with explicit context
    answer = chain.invoke({
        "context": context,
        "question": question,
        "conversation_history": conversation_history,
    })

    return answer, sources

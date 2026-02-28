"""
RAG chain: retriever + LLM for answering questions
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from backend.app.core.config import settings
from backend.app.rag.vectorstore import get_vectorstore


SYSTEM_PROMPT = """Tu es l'assistant de l'université. Tu réponds aux questions des étudiants en t'appuyant UNIQUEMENT sur le contexte fourni ci-dessous.

Règles importantes:
- Réponds en français de manière claire et concise
- Base-toi UNIQUEMENT sur le contexte fourni. Si le contexte ne contient pas l'information, dis que tu ne peux pas répondre avec certitude et suggère de contacter le secrétariat
- Cite les sources quand c'est pertinent (nom du document)
- Sois professionnel et bienveillant
- Si l'utilisateur continue une conversation précédente, tiens compte de l'historique pour plus de contexte

{conversation_history}

Contexte:
{context}

Question: {question}"""


def format_docs(docs):
    """Format retrieved documents for the prompt."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)



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
    
    # Manually invoke retriever to get docs
    docs = retriever.invoke(question)
    context = format_docs(docs)

    # Format conversation history for the prompt
    conversation_history = _format_conversation_history(recent_messages)

    # Invoke chain with explicit context
    answer = chain.invoke({
        "context": context,
        "question": question,
        "conversation_history": conversation_history,
    })

    sources = [
        (doc.page_content, doc.metadata.get("source", "unknown"))
        for doc in docs
    ]
    return answer, sources

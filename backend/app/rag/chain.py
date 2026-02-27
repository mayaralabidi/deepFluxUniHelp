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

Contexte:
{context}

Question: {question}"""


def format_docs(docs):
    """Format retrieved documents for the prompt."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def get_rag_chain():
    """Build and return the RAG chain."""
    if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
        raise ValueError(
            "GROQ_API_KEY non configuré. Ajoutez votre clé dans le fichier .env"
        )
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K})

    llm = ChatGroq(
        model=settings.LLM_MODEL,
        temperature=0.3,
        api_key=settings.GROQ_API_KEY,
    )

    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def invoke_rag(question: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Invoke RAG and return (answer, sources).
    sources: list of (content, source_path)
    """
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K})
    docs = retriever.invoke(question)

    chain = get_rag_chain()
    answer = chain.invoke(question)

    sources = [
        (doc.page_content, doc.metadata.get("source", "unknown"))
        for doc in docs
    ]
    return answer, sources

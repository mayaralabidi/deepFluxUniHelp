# Choix techniques — deepFluxUniHelp

**Version** : 1.0  
**Date** : 27 février 2025  
**Phase** : 1 – Conception

---

## 1. Vue d'ensemble

| Composant | Technologie retenue | Alternative |
|-----------|---------------------|-------------|
| Langage backend | **Python 3.11+** | — |
| Framework API | **FastAPI** | Flask |
| Frontend | **Streamlit** (prototype v1) | React/Next.js (v2) |
| Base vectorielle | **ChromaDB** | Pinecone, Qdrant |
| Framework RAG | **LangChain** | LlamaIndex |
| Embeddings | **sentence-transformers** (par défaut) | OpenAI embeddings |
| LLM | **OpenAI API** (GPT-4o-mini) | Ollama/Llama (local) |
| Traitement documents | **PyPDF2, python-docx, unstructured** | — |
| Déploiement | **Docker + Docker Compose** | — |

---

## 2. Justifications

### 2.1 Python + FastAPI
- Écosystème AI/ML mature (LangChain, Hugging Face)
- FastAPI : performances, validation automatique, docs OpenAPI
- Typage et asynchronicité pour des API réactives

### 2.2 Streamlit (prototype)
- Déploiement rapide d'une UI chat
- Intégration directe avec le backend Python
- Suffisant pour prototype et démo vidéo
- Migration vers React possible en v2 si besoin

### 2.3 ChromaDB
- Gratuit, sans API externe
- Persistance locale simple
- Intégration LangChain native
- Adapté au prototype et déploiement on-premise

### 2.4 sentence-transformers (embeddings)
- Modèle multilingue FR/EN (ex. `paraphrase-multilingual-MiniLM-L12-v2`)
- Pas de coût API pour les embeddings
- Exécution locale

### 2.5 OpenAI API (LLM)
- Qualité et fiabilité pour le français
- GPT-4o-mini : bon rapport coût/performance
- Fallback possible vers Ollama pour usage local

---

## 3. Architecture cible

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                      │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │    Chat     │  │ Génération docs  │  │    Sources     │  │
│  └──────┬──────┘  └────────┬─────────┘  └────────┬───────┘  │
└─────────┼──────────────────┼─────────────────────┼──────────┘
          │                  │                     │
          └──────────────────┼─────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │  /chat      │  │ /generate        │  │ /documents     │  │
│  └──────┬──────┘  └────────┬─────────┘  └────────┬───────┘  │
└─────────┼──────────────────┼─────────────────────┼──────────┘
          │                  │                     │
          ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Couche RAG / LLM                          │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │ ChromaDB    │  │ LangChain RAG    │  │ OpenAI / LLM   │  │
│  │ (vector DB) │  │ (retriever)      │  │                │  │
│  └─────────────┘  └──────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Versions et dépendances principales

| Package | Version | Usage |
|---------|---------|-------|
| fastapi | ^0.109 | API REST |
| uvicorn | ^0.27 | Serveur ASGI |
| langchain | ^0.1 | RAG, chaînes |
| langchain-openai | ^0.0.5 | Intégration OpenAI |
| chromadb | ^0.4 | Base vectorielle |
| sentence-transformers | ^2.2 | Embeddings |
| streamlit | ^1.29 | Interface |
| pypdf2 | ^3.0 | PDF |
| python-docx | ^1.0 | Word |

---

## 5. Variables d'environnement

```env
# LLM
OPENAI_API_KEY=sk-...

# RAG
CHROMA_PERSIST_DIR=./data/chroma
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
LLM_MODEL=gpt-4o-mini

# Optionnel : Ollama pour usage local
# USE_OLLAMA=true
# OLLAMA_BASE_URL=http://localhost:11434
```

---

## 6. Paramètres RAG

| Paramètre | Valeur |
|-----------|--------|
| Chunk size | 800 caractères |
| Chunk overlap | 200 caractères |
| Top-k | 4 |
| Température LLM | 0.3 (réponses déterministes) |

---

*Document de référence pour l'implémentation. Toute modification fera l'objet d'une mise à jour.*

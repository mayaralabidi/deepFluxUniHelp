# Plan d'implémentation — deepFluxUniHelp

**Version** : 1.0  
**Date** : 27 février 2025

---

## Vue d'ensemble

| Phase | Durée | Statut |
|-------|-------|--------|
| **Phase 1 – Conception** | 1–2 semaines | ✅ Terminée |
| Phase 2 – Base documentaire | 1–2 semaines | ✅ Terminée |
| Phase 3 – Assistant | 2–3 semaines | ✅ Terminée |
| Phase 4 – Génération | 1–2 semaines | ✅ Terminée |
| Phase 5 – Intégration | 1 semaine | ✅ Terminée |
| Phase 6 – Livrables | 1 semaine | À venir |

---

## Phase 1 – Conception (1–2 semaines)

### Objectifs
- Finaliser les spécifications et choix techniques
- Produire les maquettes UI
- Initialiser la structure du projet

### Tâches

| # | Tâche | Livrable | Statut |
|---|-------|----------|--------|
| 1.1 | Document des choix techniques | `docs/CHOIX_TECHNIQUES.md` | En cours |
| 1.2 | Maquettes UI / wireframes | `docs/maquettes/` | À faire |
| 1.3 | Structure du projet | Dossiers, config de base | À faire |
| 1.4 | Dépendances et environnement | `requirements.txt`, `.env.example` | À faire |
| 1.5 | Docker de base | `Dockerfile`, `docker-compose.yml` | À faire |

### Critères de validation Phase 1
- [ ] Choix techniques documentés et validés
- [ ] Maquettes des écrans principaux (chat, génération, admin)
- [ ] Projet initialisable avec `pip install` ou `docker compose up`
- [ ] README mis à jour avec instructions de démarrage

---

## Phase 2 – Base documentaire (1–2 semaines)

### Objectifs
- Pipeline d'ingestion des documents (PDF, DOCX, TXT)
- Indexation vectorielle (ChromaDB)
- Tests RAG sur jeu de données exemple

### Tâches

| # | Tâche | Livrable | Statut |
|---|-------|----------|--------|
| 2.1 | Loaders de documents | PDF, DOCX, TXT, Markdown | ✅ |
| 2.2 | Chunking et métadonnées | Splitter configurable | ✅ |
| 2.3 | Embeddings et ChromaDB | Index vectoriel | ✅ |
| 2.4 | API d'ingestion | Endpoints upload/index | ✅ |
| 2.5 | Documents exemple | Jeu de test (FAQ, procédures) | ✅ |

### Critères de validation Phase 2
- [ ] Import de documents fonctionnel
- [ ] Recherche sémantique opérationnelle
- [ ] Top-k documents récupérés avec scores

---

## Phase 3 – Assistant (2–3 semaines)

### Objectifs
- API de chat avec RAG
- Interface utilisateur (chat)
- Affichage des sources

### Tâches

| # | Tâche | Livrable | Statut |
|---|-------|----------|--------|
| 3.1 | Pipeline RAG complet | Contexte + LLM → réponse | ✅ |
| 3.2 | API `/chat` | Endpoint avec historique | ✅ |
| 3.3 | Interface chat | UI Streamlit | ✅ |
| 3.4 | Références sources | Affichage documents/paragraphes | ✅ |
| 3.5 | Gestion des sessions | Historique par session | ✅ |

### Critères de validation Phase 3
- [ ] Questions répondues via RAG
- [ ] Sources citées dans la réponse
- [ ] Interface chat utilisable

---

## Phase 4 – Génération (1–2 semaines)

### Objectifs
- Modèles de documents (attestation, réclamation, convention stage)
- Paramétrage par l'utilisateur
- Export texte/PDF

### Tâches

| # | Tâche | Livrable | Statut |
|---|-------|----------|--------|
| 4.1 | Modèles de prompts | Attestation, réclamation, convention | ✅ |
| 4.2 | Formulaire de paramétrage | Champs variables | ✅ |
| 4.3 | Génération LLM | Texte final | ✅ |
| 4.4 | Export PDF | Téléchargement | ✅ |

### Critères de validation Phase 4
- [ ] Au moins 3 types de documents générés
- [ ] Export téléchargeable

---

## Phase 5 – Intégration (1 semaine)

### Objectifs
- Tests end-to-end
- Déploiement Docker
- Documentation utilisateur

### Tâches

| # | Tâche | Livrable | Statut |
|---|-------|----------|--------|
| 5.1 | Tests E2E | Scénarios automatisés | ✅ |
| 5.2 | Docker production | Image complète | ✅ |
| 5.3 | Documentation | README, guide utilisateur | ✅ |

---

## Phase 6 – Livrables (1 semaine)

### Objectifs
- Vidéo de démonstration
- Script de test
- Livraison finale

### Tâches

| # | Tâche | Livrable | Statut |
|---|-------|----------|--------|
| 6.1 | Vidéo démo | 5–10 min | À venir |
| 6.2 | Script de test | Jeu d'essai documenté | À venir |
| 6.3 | Livraison | Tag release, archive | À venir |

---

## Structure cible du projet

```
deepFluxUniHelp/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── rag/
│   │   └── services/
│   ├── requirements.txt
│   └── main.py
├── frontend/                # Interface Streamlit ou React
│   ├── app.py               # ou src/ si React
│   └── ...
├── data/                    # Documents à indexer
│   └── sample/
├── docs/
│   ├── CAHIER_DES_CHARGES.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── CHOIX_TECHNIQUES.md
│   └── maquettes/
├── scripts/                 # Scripts utilitaires
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── README.md
```

# Guide utilisateur — deepFluxUniHelp

**Version** : 1.0  
**Date** : 27 février 2025

---

## 1. Présentation

deepFluxUniHelp est un assistant IA pour la vie étudiante universitaire. Il permet de :
- **Poser des questions** sur l'inscription, les attestations, les stages, les rattrapages, etc.
- **Générer des documents** administratifs (demande d'attestation, réclamation, convention de stage)

Les réponses sont basées sur les documents officiels que vous avez indexés.

---

## 2. Démarrage

### 2.1 Installation

1. Cloner le projet
2. Créer un environnement virtuel : `python -m venv .venv`
3. Activer : `.venv\Scripts\activate` (Windows) ou `source .venv/bin/activate` (Linux/Mac)
4. Installer : `pip install -r requirements.txt`
5. Copier : `copy .env.example .env`
6. Ajouter votre clé OpenAI dans `.env` : `OPENAI_API_KEY=sk-...`

### 2.2 Indexation des documents

**Important** : Avant de poser des questions, indexez vos documents.

**Option A** — Script :
```powershell
python scripts/ingest_sample.py
```

**Option B** — API :
```bash
# Indexer data/sample
curl -X POST http://localhost:8000/documents/ingest-directory \
  -H "Content-Type: application/json" \
  -d '{"path": "data/sample"}'
```

**Option C** — Upload d'un fichier (Swagger : http://localhost:8000/docs) :
- POST `/documents/ingest-file`
- Joindre un fichier PDF, DOCX, TXT ou MD

### 2.3 Lancer l'application

**Terminal 1** — API :
```powershell
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2** — Interface :
```powershell
streamlit run frontend/app.py
```

Ou avec Docker :
```powershell
docker compose up --build
```

- **Interface** : http://localhost:8501
- **API** : http://localhost:8000
- **Docs API** : http://localhost:8000/docs

---

## 3. Utilisation

### 3.1 Assistant Chat

1. Ouvrir l'onglet **Chat**
2. Taper votre question (ex. : « Comment obtenir une attestation ? »)
3. L'assistant répond en s'appuyant sur les documents indexés
4. Cliquer sur **Sources** pour voir les documents utilisés

**Exemples de questions** :
- Comment m'inscrire pour la rentrée ?
- Quelle est la procédure pour une attestation d'inscription ?
- Comment faire une demande de convention de stage ?
- Quelle est la date limite pour les rattrapages ?

### 3.2 Génération de documents

1. Ouvrir l'onglet **Générer un document**
2. Choisir le type : Attestation, Réclamation ou Convention de stage
3. Remplir les champs obligatoires (marqués *)
4. Cliquer sur **Générer**
5. Vérifier l'aperçu puis **Télécharger PDF**

**Types de documents** :
- **Attestation** : Nom, n° étudiant, type (Inscription, Scolarité…), motif, date
- **Réclamation** : Nom, n° étudiant, matière, description du problème, pièces jointes
- **Convention de stage** : Nom, n° étudiant, entreprise, dates, tuteur, référent pédagogique, description

---

## 4. API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Santé de l'API |
| `/health` | GET | Health check |
| `/chat` | POST | Poser une question (body: `{"message": "..."}`) |
| `/generate/` | POST | Générer un document (body: `{"doc_type": "...", "params": {...}}`) |
| `/generate/pdf` | POST | Générer et télécharger en PDF |
| `/generate/types` | GET | Lister les types de documents |
| `/documents/search` | POST | Recherche sémantique |
| `/documents/ingest-file` | POST | Upload et indexation |
| `/documents/ingest-directory` | POST | Indexation d'un répertoire |
| `/documents/reset` | DELETE | Réinitialiser l'index |

---

## 5. Variables d'environnement

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `OPENAI_API_KEY` | Clé API OpenAI | Oui (pour chat et génération) |
| `CHROMA_PERSIST_DIR` | Dossier de persistance ChromaDB | Non (défaut : ./data/chroma) |
| `API_BASE_URL` | URL de l'API (frontend) | Non (défaut : http://localhost:8000) |

---

## 6. Dépannage

**Erreur « Module not found »** : Vérifier que vous exécutez depuis la racine du projet.

**Aucune réponse pertinente** : Vérifier que les documents sont indexés (`python scripts/ingest_sample.py`).

**Erreur OpenAI** : Vérifier `OPENAI_API_KEY` dans `.env`.

**Frontend ne joint pas l'API** : Avec Docker, `API_BASE_URL=http://api:8000`. En local : `http://localhost:8000`.

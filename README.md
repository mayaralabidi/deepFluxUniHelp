# deepFluxUniHelp

**Assistant IA pour la vie ?tudiante universitaire**

deepFluxUniHelp centralise les documents officiels, r?pond aux questions des ?tudiants via LLM + RAG, et g?n?re des messages/formulaires administratifs standardis?s.

---
# Les délivrables

lien de la presentation: https://www.canva.com/design/DAHCl4Fmmy0/TcEDjVMdOWpQFMmSQOXBnw/edit?utm_content=DAHCl4Fmmy0&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

lien de la video demonstrative: https://www.canva.com/design/DAHCmsnWRgU/gD69kSEpXXBAP5iDrg3ZPw/edit?utm_content=DAHCmsnWRgU&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

## Structure du projet

```
deepFluxUniHelp/
??? backend/           # API FastAPI
??? frontend/          # Interface Streamlit
??? data/              # Documents ? indexer
??? docs/              # Documentation (cahier des charges, maquettes)
??? scripts/           # Scripts utilitaires
```

---

## D?marrage rapide

### Pr?requis

- Python 3.11+
- (Optionnel) Docker & Docker Compose

### Installation locale

1. Cloner le projet
2. Cr?er un environnement virtuel :

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Installer les d?pendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :

   ```bash
   copy .env.example .env
   # ?diter .env et ajouter OPENAI_API_KEY
   ```

### Lancer l'application

**API (FastAPI)** :

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- API : http://localhost:8000
- Docs : http://localhost:8000/docs

**Frontend (Streamlit)** :

```bash
streamlit run frontend/app.py
```

- Interface : http://localhost:8501

**Indexer les documents exemple** (avant utilisation du chat) :

```powershell
python scripts/ingest_sample.py
```

### Docker

```bash
docker compose up --build
```

- API : http://localhost:8000
- Frontend : http://localhost:8501

---

## Documentation

| Document | Description |
|----------|-------------|
| [Cahier des charges](docs/CAHIER_DES_CHARGES.md) | Sp?cifications compl?tes du projet |
| [Plan d'impl?mentation](docs/IMPLEMENTATION_PLAN.md) | Phases et t?ches |
| [Choix techniques](docs/CHOIX_TECHNIQUES.md) | Stack et architecture |
| [Maquettes UI](docs/maquettes/UI_WIREFRAMES.md) | Wireframes des ecrans |
| [Guide utilisateur](docs/GUIDE_UTILISATEUR.md) | Instructions d'utilisation |

---

## Statut

- **Phase 1 (Conception)** : Termin?e
- **Phase 2 (Base documentaire)** : Termin?e
- **Phase 3 (Assistant)** : Termin?e
- **Phase 4 (G?n?ration)** : Termin?e
- **Phase 5 (Int?gration)** : Termin?e

---

## Licence

Projet universitaire.

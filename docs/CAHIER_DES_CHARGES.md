# Cahier des charges — deepFluxUniHelp
## Assistant IA pour la vie étudiante universitaire

**Version** : 1.0  
**Date** : 27 février 2025  
**Statut** : Projet en conception

---

## 1. Synthèse du projet

### 1.1 Présentation

**deepFluxUniHelp** est un assistant conversationnel basé sur l’intelligence artificielle (LLM + RAG) destiné aux universités. Il centralise les documents officiels, répond aux questions des étudiants et génère des messages et formulaires administratifs standardisés, en réduisant la charge des secrétariats et en garantissant des réponses cohérentes et traçables.

### 1.2 Problématique adressée

| Problème | Impact |
|----------|--------|
| Répétition des mêmes questions | Secrétariats surchargés, temps d’attente élevé |
| Réponses variables selon les interlocuteurs | Incohérence, frustration, perte de confiance |
| Difficile d’accéder aux documents officiels | Erreurs, retards, méconnaissance des procédures |
| Messages et demandes non standardisés | Traitement plus long, risques d’omissions |

### 1.3 Solution proposée

Un assistant IA qui :
1. **Centralise** les documents officiels (règlements, procédures, FAQ, notes internes).
2. **Répond** aux questions des étudiants via LLM + RAG.
3. **Génère** automatiquement des emails et formulaires administratifs standardisés.

---

## 2. Objectifs du projet

### 2.1 Objectifs principaux

| Objectif | Description | Indicateur |
|----------|-------------|------------|
| **O1** | Centraliser les documents officiels | Nombre de sources indexées, couverture des thématiques |
| **O2** | Répondre aux questions via LLM + RAG | Pertinence des réponses, temps de réponse |
| **O3** | Générer automatiquement emails/formulaires | Types de documents générés, taux d’utilisation |

### 2.2 Objectifs secondaires

- Alléger la charge des personnels administratifs.
- Harmoniser les réponses entre services et interlocuteurs.
- Offrir un accès 24h/24 aux informations administratives.
- Traçabilité des sources (référence aux documents officiels).

---

## 3. Périmètre fonctionnel

### 3.1 Thématiques couvertes (domaines métier)

| Domaine | Exemples de sujets | Documents concernés |
|---------|--------------------|----------------------|
| Inscription | Réinscription, changement de filière, dossier incomplet | Procédures d’inscription, calendriers |
| Certificats et attestations | Attestation d’inscription, relevé de notes, certificat de scolarité | Modèles, conditions de délivrance |
| Bourses et aides | Critères, dossiers, délais | Règlements, formulaires CAF, CROUS |
| Stages | Conventions, rapports, validations | Procédures, modèles de conventions |
| Absences et rattrapages | Justification, demande de rattrapage | Règlement des études, procédures |
| Paiement | Frais, échéancier, exonération | Tarifs, procédures de paiement |
| Calendrier | Rentrée, examens, vacances | Calendriers universitaires |
| Règlement intérieur | Droits et devoirs, sanctions | Règlement intérieur, chartes |

### 3.2 Fonctionnalités attendues

#### Module 1 : Base documentaire et RAG

| Fonctionnalité | Description | Priorité |
|----------------|-------------|----------|
| Import de documents | Chargement de PDF, Word, HTML, pages web | P0 |
| Traitement et indexation | Découpage en chunks, métadonnées (type, date, thème) | P0 |
| Recherche sémantique | Embeddings + recherche vectorielle pour RAG | P0 |
| Mise à jour des sources | Mise à jour incrémentale, gestion des versions | P1 |

#### Module 2 : Assistant conversationnel

| Fonctionnalité | Description | Priorité |
|----------------|-------------|----------|
| Interface de chat | Interface texte pour poser des questions | P0 |
| Réponses basées RAG | Réponses générées à partir des documents indexés | P0 |
| Références aux sources | Affichage des documents/paragraphes utilisés | P0 |
| Historique de session | Conservation des échanges par session | P1 |
| Multi-langue (FR/EN) | Support français et éventuellement anglais | P2 |

#### Module 3 : Génération de documents

| Fonctionnalité | Description | Priorité |
|----------------|-------------|----------|
| Modèles de messages | Attestation, réclamation, demande de stage, etc. | P0 |
| Paramétrage par l’utilisateur | Nom, filière, dates, motifs personnalisés | P0 |
| Export (texte, PDF) | Téléchargement du message généré | P0 |
| Prévisualisation | Aperçu avant export | P1 |

#### Module 4 : Administration et configuration

| Fonctionnalité | Description | Priorité |
|----------------|-------------|----------|
| Gestion des sources | Ajout/suppression, priorisation des documents | P1 |
| Paramètres LLM | Choix de modèle, température, longueur des réponses | P1 |
| Statistiques d’usage | Questions fréquentes, types de demandes | P2 |

### 3.3 Hors périmètre (v1)

- Authentification SSO et gestion des rôles avancée (possible en v2).
- Intégration directe avec les logiciels de gestion (Apogée, etc.).
- Prise de rendez-vous en ligne.
- Support vocal (reconnaissance/synthèse vocale).

---

## 4. Utilisateurs cibles

### 4.1 Personas

| Persona | Profil | Besoins principaux |
|---------|--------|---------------------|
| **Étudiant (primo)** | Nouveau, peu familier des procédures | Réponses simples, formulaires prêts à l’emploi |
| **Étudiant (avancé)** | Connaît déjà les bases | Informations précises, mises à jour rapides |
| **Personnel administratif** | Secrétariat, scolarité | Moins de questions répétitives, messages standardisés |
| **Administrateur système** | Responsable de la plateforme | Configuration, maintenance, statistiques |

### 4.2 Cas d’usage principaux

1. **Étudiant** : « Comment obtenir une attestation d’inscription ? »  
   → Réponse + lien vers la procédure + possibilité de générer un modèle de demande.

2. **Étudiant** : « Je veux faire une demande de stage »  
   → Explication de la procédure + génération d’un email type de demande de convention.

3. **Étudiant** : « Quelle est la date limite pour les rattrapages ? »  
   → Réponse basée sur le calendrier officiel, avec référence au document source.

4. **Personnel** : Vérifier qu’un message généré par l’assistant respecte les standards internes.

---

## 5. Architecture technique proposée

### 5.1 Stack technologique recommandée

| Composant | Technologies possibles |
|-----------|------------------------|
| Backend | Python (FastAPI) ou Node.js |
| Base vectorielle | ChromaDB, Pinecone, Qdrant, ou Weaviate |
| LLM | OpenAI GPT-4, Claude, Llama (local), ou API Mistral |
| Embeddings | OpenAI text-embedding-3, sentence-transformers (local) |
| Traitement documents | LangChain / LlamaIndex, PyPDF2, python-docx |
| Frontend | React, Next.js, ou Streamlit (prototype rapide) |
| Hébergement | Docker, déploiement cloud (Azure, AWS, GCP) ou on-premise |

### 5.2 Architecture logique (RAG)

```
[Utilisateur] 
    → [Interface Chat]
    → [API Backend]
    → [Pipeline RAG]
        ├── [Recherche vectorielle] ← [Base documentaire indexée]
        ├── [Construction du prompt] (contexte + question)
        └── [LLM] → réponse + sources
    → [Module Génération] (si demande de document)
    → [Réponse + document exportable]
```

### 5.3 Flux de données

1. **Ingestion** : documents → parsing → chunks → embeddings → base vectorielle.
2. **Question** : question utilisateur → embedding → recherche top-k → prompt enrichi → LLM → réponse.
3. **Génération** : type de document + paramètres → prompt spécialisé → LLM → texte structuré → export.

---

## 6. Spécifications détaillées

### 6.1 Base documentaire

| Spécification | Détail |
|---------------|--------|
| Formats supportés | PDF, DOCX, TXT, HTML, Markdown |
| Taille maximale par document | À définir (ex : 50 Mo) |
| Métadonnées requises | Type, date de publication, thème, niveau (université/faculté) |
| Politique de mise à jour | Manuel ou planifiée (cron) |

### 6.2 RAG (Retrieval-Augmented Generation)

| Paramètre | Valeur recommandée |
|-----------|--------------------|
| Chunk size | 500–1000 tokens |
| Chunk overlap | 100–200 tokens |
| Top-k documents | 3–5 |
| Seuil de pertinence | À calibrer selon la base |

### 6.3 Modèles de documents générables (v1)

| Type | Champs variables typiques |
|------|---------------------------|
| Demande d’attestation | Nom, N° étudiant, type d’attestation, date, motif |
| Réclamation | Nom, N° étudiant, matière/élément, description, pièces jointes |
| Demande de convention de stage | Nom, entreprise, dates, tuteur, référent pédagogique |
| Demande de rattrapage | Nom, matière, date d’absence, justificatif |
| Demande de bourse / exonération | Situation, revenus, situation familiale (selon modèle) |

### 6.4 Exigences non fonctionnelles

| Critère | Objectif |
|---------|----------|
| Disponibilité | 24h/24 en production |
| Temps de réponse | < 5 s pour une question simple |
| Confidentialité | Données hébergées selon la politique de l’établissement (RGPD) |
| Accessibilité | Respect des normes d’accessibilité (WCAG 2.1 niveau AA si applicable) |
| Scalabilité | Support de plusieurs centaines de requêtes/jour |

---

## 7. Livrables attendus

### 7.1 Application / Prototype

- Application fonctionnelle (web) avec :
  - Interface de chat.
  - Module RAG alimenté par une base documentaire exemple.
  - Génération d’au moins 3 types de documents (ex : attestation, réclamation, convention stage).
- Code source versionné et documenté (README, commentaires).
- Instructions de déploiement (Docker, variables d’environnement).

### 7.2 Vidéo de démonstration

- Durée : 5–10 minutes.
- Contenu : présentation du contexte, démo des fonctionnalités clés, exemples de questions et de documents générés.
- Public : enseignants, responsables administratifs, partenaires.

### 7.3 Script (jeu d’essai)

- Scénarios de test :
  - Questions variées par thématique.
  - Cas limites (question hors périmètre, formulation ambiguë).
  - Génération de documents avec différents paramètres.
- Critères de validation : pertinence des réponses, présence des sources, qualité des documents générés.

---

## 8. Plan de réalisation (phases)

| Phase | Durée indicative | Activités |
|-------|------------------|-----------|
| **Phase 1 – Conception** | 1–2 semaines | Finalisation du cahier des charges, choix techniques, maquettes UI |
| **Phase 2 – Base documentaire** | 1–2 semaines | Pipeline d’ingestion, indexation, tests RAG |
| **Phase 3 – Assistant** | 2–3 semaines | API, chat, intégration LLM + RAG, références sources |
| **Phase 4 – Génération** | 1–2 semaines | Modèles de documents, paramétrage, export |
| **Phase 5 – Intégration** | 1 semaine | Tests E2E, déploiement, documentation |
| **Phase 6 – Livrables** | 1 semaine | Vidéo démo, script de test, livraison |

**Durée totale estimée** : 7–11 semaines (selon taille de l’équipe et complexité).

---

## 9. Risques et contraintes

### 9.1 Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Documents obsolètes | Moyenne | Élevé | Processus de mise à jour formalisé, dates visibles |
| Hallucinations du LLM | Moyenne | Élevé | RAG strict, limitation des réponses aux sources, disclaimer |
| Coût des API LLM | Moyenne | Moyen | Choix de modèles, cache, usage local possible |
| Données personnelles | Faible | Élevé | Pas de stockage persistant des questions, anonymisation si logs |
| Adhésion des utilisateurs | Moyenne | Moyen | Formation, communication, itérations sur l’UX |

### 9.2 Contraintes

- Respect du RGPD pour les données traitées.
- Budget API LLM à anticiper.
- Documents officiels souvent au format PDF (gestion des tableaux et images).
- Nécessité d’une validation juridique des textes générés par l’assistant.

---

## 10. Critères d’acceptation et de succès

### 10.1 Critères d’acceptation (livraison)

- [ ] L’assistant répond correctement à des questions sur les 5 thématiques minimum (inscription, attestations, stages, absences/rattrapages, paiement).
- [ ] Les réponses s’appuient sur des sources documentaires et les références sont affichées.
- [ ] Au moins 3 types de documents peuvent être générés et exportés.
- [ ] Une vidéo de démonstration et un script de test sont livrés.
- [ ] Le code est documenté et déployable via Docker (ou équivalent).

### 10.2 Indicateurs de succès (post-déploiement)

- Taux de satisfaction des utilisateurs (enquête).
- Réduction du volume de questions répétitives adressées aux secrétariats.
- Nombre de documents générés et utilisés.
- Taux de pertinence des réponses (validation manuelle sur échantillon).

---

## Annexes

### A. Glossaire

- **LLM** : Large Language Model (ex. GPT-4, Claude).
- **RAG** : Retrieval-Augmented Generation (recherche documentaire + génération par LLM).
- **Embedding** : Représentation vectorielle d’un texte pour la recherche sémantique.
- **Chunk** : Fragment de document utilisé pour l’indexation et la récupération.

### B. Références

- RGPD : Règlement (UE) 2016/679.
- LangChain : https://python.langchain.com/
- LlamaIndex : https://www.llamaindex.ai/

---

*Document établi dans le cadre du projet deepFluxUniHelp. Toute évolution du périmètre ou des objectifs fera l’objet d’une mise à jour de ce cahier des charges.*

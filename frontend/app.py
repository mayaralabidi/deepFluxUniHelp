"""
deepFluxUniHelp - Frontend (Streamlit)
Interface utilisateur
"""

import os
import streamlit as st
import httpx

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="deepFluxUniHelp",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 deepFluxUniHelp")
st.caption("Assistant IA pour la vie étudiante universitaire")

st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Section",
    ["Chat", "Générer un document", "À propos"],
    index=0,
)


def call_chat(message: str, history: list) -> dict:
    """Call the chat API."""
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{API_BASE}/chat",
            json={"message": message, "history": history},
        )
        r.raise_for_status()
        return r.json()


def call_generate(doc_type: str, params: dict) -> dict:
    """Call the generate API."""
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{API_BASE}/generate/",
            json={"doc_type": doc_type, "params": params},
        )
        r.raise_for_status()
        return r.json()


def download_pdf(doc_type: str, params: dict) -> bytes:
    """Download generated document as PDF."""
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{API_BASE}/generate/pdf",
            json={"doc_type": doc_type, "params": params},
        )
        r.raise_for_status()
        return r.content


if page == "Chat":
    st.subheader("Assistant Chat")
    st.markdown("Posez vos questions sur l'inscription, les attestations, les stages, etc.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources" not in st.session_state:
        st.session_state.sources = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📎 Sources"):
                    for s in msg["sources"]:
                        st.caption(f"**{s.get('source', '')}**")
                        st.text(s.get("content", "")[:200] + "..." if len(s.get("content", "")) > 200 else s.get("content", ""))

    if prompt := st.chat_input("Posez votre question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Recherche..."):
                try:
                    resp = call_chat(prompt, [])
                    answer = resp.get("answer", "")
                    sources = resp.get("sources", [])
                    st.markdown(answer)
                    if sources:
                        with st.expander("📎 Sources"):
                            for s in sources:
                                src = s.get("source", "unknown")
                                content = s.get("content", "")[:300]
                                st.caption(f"**{src.split('/')[-1]}**")
                                st.text(content + ("..." if len(s.get("content", "")) > 300 else ""))
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })
                except Exception as e:
                    err_msg = str(e)
                    if hasattr(e, "response") and e.response is not None:
                        try:
                            body = e.response.json()
                            err_msg = body.get("detail", err_msg)
                        except Exception:
                            if e.response.text:
                                err_msg = e.response.text[:500]
                    st.error(f"Erreur: {err_msg}")

elif page == "Générer un document":
    st.subheader("Générer un document administratif")

    doc_type = st.selectbox(
        "Type de document",
        ["attestation", "reclamation", "convention_stage"],
        format_func=lambda x: {
            "attestation": "Demande d'attestation",
            "reclamation": "Demande de réclamation",
            "convention_stage": "Demande de convention de stage",
        }[x],
    )

    if doc_type == "attestation":
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet *", "")
            numero_etudiant = st.text_input("Numéro étudiant *", "")
            type_attestation = st.selectbox(
                "Type d'attestation",
                ["Inscription", "Scolarité", "Assiduité", "Notes"],
            )
        with col2:
            motif = st.text_input("Motif (ex: CAF, sécurité sociale)", "")
            date = st.text_input("Date", placeholder="Ex: 27/02/2025")

    elif doc_type == "reclamation":
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet *", "")
            numero_etudiant = st.text_input("Numéro étudiant *", "")
            matiere = st.text_input("Matière / élément concerné *", "")
        with col2:
            description = st.text_area("Description du problème *", "")
            pieces_jointes = st.text_input("Pièces jointes", "")

    else:
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet *", "")
            numero_etudiant = st.text_input("Numéro étudiant *", "")
            entreprise = st.text_input("Entreprise d'accueil *", "")
            dates = st.text_input("Dates du stage *", placeholder="Ex: du 1er mars au 30 avril 2025")
            tuteur_entreprise = st.text_input("Tuteur entreprise", "")
        with col2:
            referent_pedagogique = st.text_input("Référent pédagogique", "")
            description = st.text_area("Description du stage", "")

    if st.button("Générer"):
        if not nom.strip() or not numero_etudiant.strip():
            st.warning("Veuillez remplir le nom et le numéro étudiant (champs obligatoires).")
        else:
            if doc_type == "attestation":
                params = {
                    "nom": nom, "numero_etudiant": numero_etudiant,
                    "type_attestation": type_attestation, "motif": motif, "date": date,
                }
            elif doc_type == "reclamation":
                params = {
                    "nom": nom, "numero_etudiant": numero_etudiant,
                    "matiere": matiere, "description": description,
                    "pieces_jointes": pieces_jointes or "Aucune",
                }
            else:
                params = {
                    "nom": nom, "numero_etudiant": numero_etudiant,
                    "entreprise": entreprise, "dates": dates,
                    "tuteur_entreprise": tuteur_entreprise or "Non renseigné",
                    "referent_pedagogique": referent_pedagogique or "Non renseigné",
                    "description": description or "Non renseigné",
                }

            try:
                with st.spinner("Génération..."):
                    result = call_generate(doc_type, params)
                text = result.get("text", "")
                st.text_area("Aperçu", text, height=300)
                pdf_bytes = download_pdf(doc_type, params)
                st.download_button(
                    "📥 Télécharger PDF",
                    data=pdf_bytes,
                    file_name=f"{doc_type}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                err_msg = str(e)
                if hasattr(e, "response") and e.response is not None:
                    try:
                        body = e.response.json()
                        err_msg = body.get("detail", err_msg)
                    except Exception:
                        if e.response.text:
                            err_msg = e.response.text[:500]
                st.error(f"Erreur: {err_msg}")

else:
    st.subheader("À propos")
    st.markdown("""
    **deepFluxUniHelp** est un assistant IA pour les universités qui :
    - Centralise les documents officiels
    - Répond aux questions via LLM + RAG
    - Génère des documents administratifs standardisés

    **Utilisation** : indexez d'abord vos documents via l'API (`POST /documents/ingest-directory`)
    ou le script `python scripts/ingest_sample.py`, puis posez vos questions.
    """)


st.sidebar.markdown("---")
st.sidebar.markdown("**Thématiques**")
st.sidebar.markdown("- Inscription")
st.sidebar.markdown("- Attestations")
st.sidebar.markdown("- Stages")
st.sidebar.markdown("- Bourses")
st.sidebar.markdown("- Rattrapages")

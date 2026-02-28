"""
deepFluxUniHelp - Frontend (Streamlit)
Assistant IA pour la vie étudiante universitaire
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

# Modern, elegant styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Headers */
    h1 { color: #1e3a8a; font-weight: 700; }
    h2 { color: #1e40af; font-weight: 600; }
    h3 { color: #1e40af; font-weight: 600; }
    
    /* Cards */
    .stContainer {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        padding: 25px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(245, 87, 108, 0.3);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > textarea {
        border: 2px solid #e0e7ff !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextArea > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Sidebar */
    .stSidebar {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stSidebar [data-testid="stSidebarNav"] { background: transparent; }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 { color: white; }
    .stSidebar label { color: white !important; font-weight: 500; }
    .stSidebar .stMarkdown { color: rgba(255, 255, 255, 0.9); }
    
    /* Chat messages */
    .stChatMessage {
        border-radius: 12px;
        padding: 15px;
    }
    
    /* Messages styling */
    [data-testid="chatMessageUser"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    [data-testid="chatMessageAssistant"] {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea;
        border-bottom: 3px solid #667eea !important;
    }
    
    /* Alerts */
    .stAlert { border-radius: 8px; }
    
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid #10b981 !important;
    }
    
    .stError {
        background-color: rgba(245, 87, 108, 0.1) !important;
        border-left: 4px solid #f5576c !important;
    }
    
    .stWarning {
        background-color: rgba(251, 146, 60, 0.1) !important;
        border-left: 4px solid #fb923c !important;
    }
    
    .stInfo {
        background-color: rgba(102, 126, 234, 0.1) !important;
        border-left: 4px solid #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# Header with gradient
col1, col2 = st.columns([1, 0.3])
with col1:
    st.markdown("<h1>🎓 deepFluxUniHelp</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666; font-size: 16px; margin-top: -10px;'>Ton assistant IA pour l'université</p>", unsafe_allow_html=True)

st.markdown("---")

st.sidebar.markdown("## 📍 Navigation", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Sections",
    ["💬 Chat", "📄 Documents", "ℹ️ À propos"],
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


if page == "💬 Chat":
    st.markdown("### 💬 Pose ta question")
    st.markdown("Question sur l'inscription, les attestations, les stages, bourses, rattrapages... On t'aide! 🚀")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📎 Sources"):
                    for s in msg["sources"]:
                        st.caption(f"• {s.get('source', '').split('/')[-1]}")

    if prompt := st.chat_input("✏️ Écris ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Recherche en cours..."):
                try:
                    resp = call_chat(prompt, [])
                    answer = resp.get("answer", "")
                    sources = resp.get("sources", [])
                    st.markdown(answer)
                    if sources:
                        with st.expander("📎 Sources"):
                            for s in sources:
                                src = s.get("source", "").split('/')[-1]
                                st.caption(f"• {src}")
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
                    st.error(f"❌ Erreur: {err_msg}")

elif page == "📄 Documents":
    st.markdown("### 📄 Générer un document")
    st.markdown("Crée facilement tes attestations, réclamations et conventions de stage 📝")

    doc_type = st.selectbox(
        "📋 Quel document tu veux créer?",
        ["attestation", "reclamation", "convention_stage"],
        format_func=lambda x: {
            "attestation": "📜 Attestation (inscription, scolarité, assiduité...)",
            "reclamation": "⚠️ Réclamation",
            "convention_stage": "🤝 Convention de stage",
        }[x],
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    if doc_type == "attestation":
        with col1:
            st.markdown("**📋 Infos obligatoires**")
            nom = st.text_input("👤 Nom complet", placeholder="Jean Dupont")
            numero_etudiant = st.text_input("🆔 N° étudiant", placeholder="23456789")
            type_attestation = st.selectbox("📄 Type", ["Inscription", "Scolarité", "Assiduité", "Notes"])
        with col2:
            st.markdown("**📝 Détails**")
            motif = st.text_input("💬 Motif", placeholder="CAF, Sécurité sociale...")
            date = st.text_input("📅 Date", placeholder="27/02/2025")

    elif doc_type == "reclamation":
        with col1:
            st.markdown("**📋 Infos obligatoires**")
            nom = st.text_input("👤 Nom complet", placeholder="Jean Dupont")
            numero_etudiant = st.text_input("🆔 N° étudiant", placeholder="23456789")
            matiere = st.text_input("📚 Matière", placeholder="Mathématiques, Physique...")
        with col2:
            st.markdown("**📝 Description**")
            description = st.text_area("📝 Détaille ton problème", placeholder="Explique ce qui s'est passé...")
            pieces_jointes = st.text_input("📎 Pièces jointes", placeholder="Notes, documents...")

    else:
        with col1:
            st.markdown("**📋 Infos obligatoires**")
            nom = st.text_input("👤 Nom complet", placeholder="Jean Dupont")
            numero_etudiant = st.text_input("🆔 N° étudiant", placeholder="23456789")
            entreprise = st.text_input("🏢 Entreprise", placeholder="Google, Microsoft...")
            dates = st.text_input("📅 Dates", placeholder="1er juin - 30 août 2025")
        with col2:
            st.markdown("**👥 Contacts**")
            tuteur_entreprise = st.text_input("👨‍💼 Tuteur entreprise", placeholder="Jean Martin")
            referent_pedagogique = st.text_input("👨‍🏫 Référent", placeholder="Prof. Sophie Bernard")
            description = st.text_area("📝 Description du stage", placeholder="Ce que tu vas faire...")

    st.markdown("---")
    if st.button("⚡ Générer mon document", use_container_width=True):
        if not nom.strip() or not numero_etudiant.strip():
            st.warning("⚠️ Complète le nom et le N° étudiant!")
        else:
            if doc_type == "attestation":
                params = {"nom": nom, "numero_etudiant": numero_etudiant, "type_attestation": type_attestation, "motif": motif, "date": date}
            elif doc_type == "reclamation":
                params = {"nom": nom, "numero_etudiant": numero_etudiant, "matiere": matiere, "description": description, "pieces_jointes": pieces_jointes or "Aucune"}
            else:
                params = {"nom": nom, "numero_etudiant": numero_etudiant, "entreprise": entreprise, "dates": dates, "tuteur_entreprise": tuteur_entreprise or "Non renseigné", "referent_pedagogique": referent_pedagogique or "Non renseigné", "description": description or "Non renseigné"}

            try:
                with st.spinner("✨ Génération..."):
                    result = call_generate(doc_type, params)
                text = result.get("text", "")
                
                st.success("✅ Document généré avec succès!")
                st.markdown("---")
                st.text_area("📖 Aperçu", text, height=300)
                
                pdf_bytes = download_pdf(doc_type, params)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.download_button("📥 Télécharger PDF", data=pdf_bytes, file_name=f"{doc_type}_{numero_etudiant}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                err_msg = str(e)
                if hasattr(e, "response") and e.response is not None:
                    try:
                        body = e.response.json()
                        err_msg = body.get("detail", err_msg)
                    except Exception:
                        if e.response.text:
                            err_msg = e.response.text[:500]
                st.error(f"❌ Erreur: {err_msg}")

else:
    st.markdown("### ℹ️ À propos")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Pourquoi deepFluxUniHelp?**")
        st.markdown("""
        T'as des questions administratives? Des documents à faire? C'est stressant!
        
        **deepFluxUniHelp** c'est ton assistant perso qui:
        - ✅ Répond à tes questions 24/7
        - ✅ Génère tes documents officieux
        - ✅ T'aide avec l'inscription, attestations, stages...
        """)
    
    with col2:
        st.markdown("**⚡ Comment ça marche?**")
        st.markdown("""
        1️⃣ Tu poses une question → **Chat**
        2️⃣ Tu crées un document → **Documents**
        3️⃣ Tu télécharges en PDF → **Prêt!**
        
        **Thèmes:** Inscription, Attestations, Stages, Bourses, Rattrapages
        """)
    
    st.markdown("---")
    
    st.markdown("**🚀 Mise en route:**")
    st.code("python scripts/ingest_sample.py", language="bash")
    st.markdown("Puis utilise le Chat et Générer des documents!")
    
    st.markdown("---")
    
    st.info("💡 **Powered by:** LLM + RAG (IA intelligente sur tes documents)", icon="⚙️")

st.sidebar.markdown("---")
st.sidebar.markdown("**💬 Thèmes couverts:**")
st.sidebar.markdown("""
🎓 Inscription
📄 Attestations
🏢 Stages
💰 Bourses
📝 Rattrapages
⚖️ Réclamations
""")


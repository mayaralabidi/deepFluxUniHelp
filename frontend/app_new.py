"""
DeepFluxUniHelp - Premium Streamlit Frontend

A comprehensive university assistant with:
- JWT Authentication with RBAC
- Chat with conversation history & RAG
- Document generation (structured per UI wireframes)
- Analytics dashboard
- Feedback management

Design inspiration: Linear.app, Notion, Claude.ai
Theme: Premium dark UI with purple/teal accents
"""

import streamlit as st
import requests
import re
from typing import Optional
from datetime import datetime

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================
st.set_page_config(
    page_title="DeepFluxUniHelp",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# PREMIUM DARK THEME CSS
# ============================================================================
st.markdown("""
<style>
    /* GLOBAL RESETS & FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0F1117 !important;
        color: #F0F2F8 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Hide Streamlit elements (keep sidebar toggle usable) */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none !important; }
    /* Don't hide the header/toolbar, it contains the sidebar reopen control */
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #6C63FF;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #7D76FF;
    }
    
    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: #161B27 !important;
        border-right: 1px solid #2A3142 !important;
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        width: 280px !important;
        padding-top: 16px !important;
        padding-bottom: 16px !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: #F0F2F8 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* USER PROFILE CARD */
    .user-profile-card {
        background: linear-gradient(135deg, #1E2433, #252D40);
        border: 1px solid #2A3142;
        border-radius: 12px;
        padding: 16px;
        margin: 0 12px 20px 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        text-align: center;
    }
    
    .user-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6C63FF, #00D4AA);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: white;
        font-size: 18px;
    }
    
    .user-name {
        font-size: 14px;
        color: #F0F2F8;
        font-weight: 600;
        max-width: 100%;
        word-break: break-word;
    }
    
    .user-email {
        font-size: 11px;
        color: #8B95A8;
        max-width: 100%;
        word-break: break-word;
    }
    
    .role-badge {
        border-radius: 10px;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 4px 10px;
        font-weight: 600;
        display: inline-block;
    }
    
    .role-badge.student {
        background: #6C63FF22;
        color: #6C63FF;
        border: 1px solid #6C63FF44;
    }
    
    .role-badge.staff {
        background: #00D4AA22;
        color: #00D4AA;
        border: 1px solid #00D4AA44;
    }
    
    .role-badge.admin {
        background: #FF475722;
        color: #FF4757;
        border: 1px solid #FF475744;
    }
    
    /* SECTION LABELS */
    .section-label {
        font-size: 10px;
        color: #4A5568 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
        margin: 16px 12px 8px 12px;
        display: block;
    }
    
    /* NAVIGATION BUTTONS */
    section[data-testid="stSidebar"] .stButton > button {
        width: auto !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        background: transparent !important;
        color: #8B95A8 !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        box-shadow: none !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        justify-content: flex-start !important;
        display: flex !important;
        align-items: center !important;
        margin: 2px 12px !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #1E2433 !important;
        color: #F0F2F8 !important;
        border-left: 3px solid #6C63FF !important;
        padding-left: 11px !important;
    }
    
    /* ACTIVE NAV */
    section[data-testid="stSidebar"] .stButton > button.active {
        background: linear-gradient(90deg, #6C63FF15, transparent) !important;
        color: #6C63FF !important;
        border-left: 3px solid #6C63FF !important;
        padding-left: 11px !important;
        font-weight: 600 !important;
    }
    
    /* NEW CONVERSATION BUTTON STYLING */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 14px !important;
        width: 256px !important;
        font-size: 14px !important;
        box-shadow: none !important;
        justify-content: center !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        filter: brightness(1.1);
        box-shadow: 0 4px 15px #6C63FF44 !important;
    }
    
    /* CONVERSATION LIST */
    .conv-item {
        border-radius: 8px;
        padding: 10px 12px;
        cursor: pointer;
        margin: 2px 12px;
        color: #F0F2F8;
        background: transparent;
        border-left: 3px solid transparent;
        font-size: 13px;
    }
    
    .conv-item:hover {
        background: #1E2433;
    }
    
    .conv-item.active {
        background: #1E2433;
        border-left: 3px solid #6C63FF;
    }
    
    /* DIVIDERS */
    hr {
        border: none !important;
        border-top: 1px solid #2A3142 !important;
        margin: 12px 0 !important;
    }
    
    /* MAIN CONTENT HEADER */
    .main-header {
        font-size: 28px;
        font-weight: 800;
        color: #F0F2F8;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #8B95A8;
        margin-bottom: 12px;
    }
    
    .header-divider {
        background: linear-gradient(90deg, #6C63FF, #00D4AA, transparent);
        height: 2px;
        border-radius: 2px;
        margin-bottom: 24px;
    }
    
    /* CHAT CONTAINER */
    .chat-container {
        max-width: 780px;
        margin: 0 auto;
        padding-bottom: 100px;
    }
    
    /* MESSAGE ANIMATIONS */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* MESSAGE STYLING */
    .message-user-wrap {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
        animation: slideUp 0.3s ease;
    }
    
    .message-user {
        background: linear-gradient(135deg, #6C63FF, #8B5CF6);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        max-width: 65%;
        box-shadow: 0 4px 12px #6C63FF33;
        word-wrap: break-word;
    }
    
    .msg-timestamp-user {
        font-size: 10px;
        color: #ffffff66;
        text-align: right;
        margin-top: 4px;
    }
    
    .message-assistant-wrap {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 16px;
        animation: slideUp 0.3s ease;
    }
    
    .message-assistant {
        background: #1E2433;
        border: 1px solid #2A3142;
        color: #F0F2F8;
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .msg-timestamp-asst {
        font-size: 10px;
        color: #4A5568;
        margin-top: 4px;
    }
    
    /* SOURCES */
    .stExpander {
        background-color: #0F1117 !important;
        border: 1px solid #2A3142 !important;
        border-radius: 8px !important;
    }
    
    .source-pill {
        background: #6C63FF15;
        color: #6C63FF;
        border-radius: 6px;
        padding: 4px 8px;
        display: inline-block;
        margin-right: 4px;
        margin-bottom: 4px;
        font-size: 12px;
    }
    
    /* FEEDBACK BUTTONS */
    .feedback-buttons {
        display: flex;
        gap: 8px;
        margin-top: 8px;
    }
    
    .feedback-btn {
        background: transparent;
        border: none;
        cursor: pointer;
        color: #4A5568;
        font-size: 16px;
        padding: 4px 8px;
    }
    
    .feedback-btn:hover {
        transform: scale(1.2);
    }
    
    .feedback-btn.active-up {
        color: #00D4AA;
    }
    
    .feedback-btn.active-down {
        color: #FF4757;
    }
    
    /* EMPTY STATE */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 20px;
        text-align: center;
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
    }
    
    .empty-icon {
        font-size: 64px;
        margin-bottom: 16px;
        animation: pulse 2s infinite ease-in-out;
    }
    
    .empty-heading {
        font-size: 18px;
        color: #F0F2F8;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .empty-subtext {
        font-size: 14px;
        color: #8B95A8;
        max-width: 320px;
        margin: 0 auto;
    }
    
    /* AUTH PAGES */
    .auth-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 20px;
        background-color: #0F1117;
    }
    
    .auth-card {
        background: #1E2433;
        border: 1px solid #2A3142;
        border-radius: 16px;
        padding: 40px;
        width: 100%;
        max-width: 520px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    .auth-logo {
        font-size: 48px;
        text-align: center;
        margin-bottom: 16px;
    }
    
    .auth-title {
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #6C63FF, #00D4AA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
    }
    
    .auth-subtitle {
        text-align: center;
        font-size: 13px;
        color: #8B95A8;
        margin-bottom: 32px;
    }
    
    /* INPUT FIELDS */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background-color: #1E2433 !important;
        border: 1px solid #2A3142 !important;
        border-radius: 10px !important;
        color: #F0F2F8 !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #4A5568 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6C63FF !important;
        box-shadow: 0 0 0 3px #6C63FF22 !important;
    }
    
    /* CHAT INPUT */
    .stChatInputContainer {
        background-color: #161B27 !important;
        border-top: 1px solid #2A3142 !important;
    }
    
    .stChatInputContainer input {
        background-color: #1E2433 !important;
        border: 1px solid #2A3142 !important;
        border-radius: 14px !important;
        color: #F0F2F8 !important;
        padding: 12px 16px !important;
    }
    
    /* BUTTONS */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
        font-size: 14px !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        filter: brightness(1.1);
        box-shadow: 0 4px 15px #6C63FF44 !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #8B95A8 !important;
        border: 1px solid #2A3142 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #1E2433 !important;
        color: #F0F2F8 !important;
    }
    
    /* FORM COMPONENTS */
    .form-section-title {
        font-size: 16px;
        font-weight: 700;
        color: #F0F2F8;
        margin: 20px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .form-divider {
        border: none;
        border-top: 1px solid #2A3142;
        margin: 16px 0;
    }
    
    /* DOCUMENT GENERATION CARD */
    .doc-form-card {
        background: #1E2433;
        border: 1px solid #2A3142;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .form-field-label {
        color: #F0F2F8;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* PREVIEW SECTION */
    .preview-section {
        background: #0F1117;
        border: 1px solid #2A3142;
        border-radius: 8px;
        padding: 16px;
        margin-top: 20px;
    }
    
    .preview-title {
        font-size: 12px;
        color: #8B95A8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        font-weight: 700;
    }
    
    /* METRIC CARDS */
    .metric-card {
        background: #1E2433;
        border: 1px solid #2A3142;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #F0F2F8;
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 13px;
        color: #8B95A8;
    }
    
    /* TABLES */
    .stDataFrame {
        background-color: #161B27 !important;
    }
    
    /* LABELS & HELP TEXT */
    .stLabel > label {
        color: #F0F2F8 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    [data-testid="stMarkdownContainer"] small {
        color: #8B95A8 !important;
    }
    
    /* ALERTS */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        border-left: 3px solid !important;
    }
    
    /* SELECTBOX DROPDOWN */
    .stSelectbox > div > div > div {
        background-color: #1E2433 !important;
        color: #F0F2F8 !important;
        border: 1px solid #2A3142 !important;
        border-radius: 10px !important;
    }
    
    /* RADIO BUTTONS */
    .stRadio > div {
        background-color: transparent !important;
    }
    
    .stRadio > div > div > label {
        color: #F0F2F8 !important;
    }
    
    /* SPINNER */
    .stSpinner > div {
        color: #6C63FF !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTS & CONFIG
# ============================================================================

API_BASE_URL = "http://127.0.0.1:8000"


# ============================================================================
# SESSION STATE INIT
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "page" not in st.session_state:
        st.session_state.page = "chat"
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    if "active_nav" not in st.session_state:
        st.session_state.active_nav = "chat"


# ============================================================================
# API FUNCTIONS
# ============================================================================

def api_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None,
    token: Optional[str] = None,
    return_raw: bool = False,
) -> tuple[bool, dict | bytes | None]:
    """Make API request with error handling."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=data, headers=headers, timeout=30)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)
        elif method == "PATCH":
            resp = requests.patch(url, json=data, headers=headers, timeout=10)
        else:
            return False, {"error": f"Unknown method: {method}"}
        
        if resp.status_code in [200, 201]:
            if return_raw:
                return True, resp.content
            return True, resp.json()
        elif resp.status_code == 401:
            st.session_state.token = None
            st.session_state.user = None
            return False, {"error": "Authentication required"}
        else:
            try:
                return False, resp.json()
            except:
                return False, {"error": f"HTTP {resp.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return False, {"error": f"Request failed: {str(e)}"}


def login(email: str, password: str) -> bool:
    """Authenticate user and store JWT token."""
    success, response = api_request(
        "POST",
        "/auth/login",
        {"email": email, "password": password},
    )
    
    if success and "access_token" in response:
        st.session_state.token = response["access_token"]
        st.session_state.user = response.get("user")
        return True
    
    error_msg = response.get("detail") or response.get("error") or "Unknown error"
    st.error(f"❌ Login failed: {error_msg}")
    return False


def register(email: str, password: str, full_name: str) -> bool:
    """Register new user."""
    success, response = api_request(
        "POST",
        "/auth/register",
        {
            "email": email,
            "password": password,
            "full_name": full_name,
        },
    )
    
    if success:
        st.success("✅ Registration successful! Please log in.")
        return True
    
    error_msg = response.get("detail") or response.get("error") or "Registration failed"
    st.error(f"❌ Error: {error_msg}")
    return False


def get_current_user() -> Optional[dict]:
    """Fetch current user profile."""
    success, response = api_request("GET", "/auth/me", token=st.session_state.token)
    return response if success else None


def send_message(message: str, conversation_id: Optional[str] = None) -> Optional[dict]:
    """Send message to chat endpoint."""
    success, response = api_request(
        "POST",
        "/chat",
        {
            "message": message,
            "conversation_id": conversation_id,
            "create_new": conversation_id is None,
        },
        token=st.session_state.token,
    )
    
    if success:
        return response
    
    error_msg = response.get("detail") or response.get("error") or "Chat failed"
    st.error(f"❌ Error: {error_msg}")
    return None


def get_conversations(limit: int = 20, offset: int = 0) -> Optional[dict]:
    """Get list of user's conversations."""
    success, response = api_request(
        "GET",
        f"/chat/conversations?limit={limit}&offset={offset}",
        token=st.session_state.token,
    )
    return response if success else None


def get_conversation_messages(conversation_id: str) -> Optional[dict]:
    """Get messages in a conversation."""
    success, response = api_request(
        "GET",
        f"/chat/conversations/{conversation_id}",
        token=st.session_state.token,
    )
    return response if success else None


def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation."""
    success, _ = api_request(
        "DELETE",
        f"/chat/conversations/{conversation_id}",
        token=st.session_state.token,
    )
    return success


def submit_feedback(
    chat_log_id: str,
    rating: int,
    comment: Optional[str] = None,
    correction: Optional[str] = None,
    category: Optional[str] = None,
) -> bool:
    """Submit feedback on a chat response."""
    success, response = api_request(
        "POST",
        "/feedback",
        {
            "chat_log_id": chat_log_id,
            "rating": rating,
            "comment": comment,
            "correction": correction,
            "category": category,
        },
        token=st.session_state.token,
    )
    
    if not success:
        detail = response.get("detail")
        if isinstance(detail, list) and detail:
            error_msg = detail[0].get("msg", str(detail[0]))
        else:
            error_msg = detail or response.get("error") or "Feedback submission failed"
        st.error(f"❌ Error: {error_msg}")
    return success


def get_analytics_summary(days: int = 7) -> Optional[dict]:
    """Get analytics summary."""
    success, response = api_request(
        "GET",
        f"/analytics/summary?days={days}",
        token=st.session_state.token,
    )
    return response.get("data") if success else None


def get_feedback_stats() -> Optional[dict]:
    """Get feedback statistics."""
    success, response = api_request(
        "GET",
        "/feedback/stats",
        token=st.session_state.token,
    )
    return response.get("data") if success else None


def get_generate_types() -> Optional[dict]:
    """Get available document types and field definitions. Returns {types: [...], fields_by_type: {...}} or None."""
    success, response = api_request(
        "GET",
        "/generate/types",
        token=st.session_state.token,
    )
    if not success:
        return None
    return {
        "types": response.get("types") or [],
        "fields_by_type": response.get("fields_by_type") or {},
    }


def generate_document(doc_type: str, params: dict) -> Optional[dict]:
    """Generate a document of specified type."""
    success, response = api_request(
        "POST",
        "/generate",
        {"doc_type": doc_type, "params": params},
        token=st.session_state.token,
    )
    
    if success:
        return response
    
    error_msg = response.get("detail") or response.get("error") or "Document generation failed"
    st.error(f"❌ Error: {error_msg}")
    return None


def generate_pdf(doc_type: str, params: dict) -> Optional[bytes]:
    """Generate a PDF document of specified type."""
    success, response = api_request(
        "POST",
        "/generate/pdf",
        {"doc_type": doc_type, "params": params},
        token=st.session_state.token,
        return_raw=True,
    )
    
    if success:
        return response
    
    if isinstance(response, dict):
        error_msg = response.get("detail") or response.get("error") or "PDF generation failed"
    else:
        error_msg = "PDF generation failed"
    
    st.error(f"❌ Error: {error_msg}")
    return None


# ============================================================================
# PAGE: LOGIN
# ============================================================================

def page_login():
    """User login page."""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">🎓</div>
            <div class="auth-title">deepFluxUniHelp</div>
            <div class="auth-subtitle">University Administrative Assistant</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("📧 Email Address", placeholder="your.email@university.edu")
        password = st.text_input("🔐 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
        
        if submitted and email and password:
            if login(email, password):
                st.rerun()
    
    st.divider()
    
    st.markdown("<div style='text-align: center; font-size: 13px; color: #8B95A8; margin: 16px 0;'>Don't have an account?</div>", unsafe_allow_html=True)
    if st.button("📝 Create Account", use_container_width=True, key="to_register"):
        st.session_state.auth_page = "register"
        st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)


# ============================================================================
# PAGE: REGISTER
# ============================================================================

def page_register():
    """User registration page."""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">🎓</div>
            <div class="auth-title">deepFluxUniHelp</div>
            <div class="auth-subtitle">University Administrative Assistant</div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form"):
        email = st.text_input("📧 Email Address", placeholder="your.email@university.edu")
        full_name = st.text_input("👤 Full Name", placeholder="John Doe")
        password = st.text_input("🔐 Password", type="password", placeholder="Minimum 8 characters")
        password_confirm = st.text_input("🔐 Confirm Password", type="password", placeholder="Re-enter password")
        
        submitted = st.form_submit_button("✅ Register", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not full_name or not password:
                st.error("❌ All fields are required")
            elif len(password) < 8:
                st.error("❌ Password must be at least 8 characters")
            elif password != password_confirm:
                st.error("❌ Passwords don't match")
            elif register(email, password, full_name):
                st.session_state.auth_page = "login"
                st.rerun()
    
    st.divider()
    
    st.markdown("<div style='text-align: center; font-size: 13px; color: #8B95A8; margin: 16px 0;'>Already have an account?</div>", unsafe_allow_html=True)
    if st.button("🔑 Back to Login", use_container_width=True, key="to_login"):
        st.session_state.auth_page = "login"
        st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)


# ============================================================================
# PAGE: CHAT
# ============================================================================

def page_chat():
    """Main chat interface."""
    # Header
    st.markdown("""
        <div class="main-header">
            <span style="color: #6C63FF; text-shadow: 0 0 10px #6C63FF44;">💬</span> Chat with Assistant
        </div>
        <div class="header-subtitle">Ask questions and get answers powered by your university documents</div>
        <div class="header-divider"></div>
    """, unsafe_allow_html=True)
    
    # Sidebar: Conversations
    with st.sidebar:
        st.markdown('<div class="section-label">Conversations</div>', unsafe_allow_html=True)
        
        if st.button("➕ New Conversation", key="new_conv", use_container_width=True, type="primary"):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        
        # Load conversations (API returns {"data": [...], "pagination": ...})
        conv_data = get_conversations(limit=10)
        if conv_data and conv_data.get("data"):
            for conv in conv_data["data"]:
                is_active = (conv["id"] == st.session_state.current_conversation_id)
                
                col1, col2 = st.columns([5, 1], gap="small")
                with col1:
                    if st.button(f"💬 {conv['title'][:22]}", key=f"conv_{conv['id']}", use_container_width=True):
                        st.session_state.current_conversation_id = conv["id"]
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv['id']}", help="Delete conversation", use_container_width=False):
                        if delete_conversation(conv["id"]):
                            st.toast("✅ Conversation deleted")
                            st.rerun()
        else:
            st.markdown("<div style='font-size: 12px; color: #4A5568; text-align: center; padding: 20px;'>📭 No conversations yet</div>", unsafe_allow_html=True)
    
    # Message display
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    messages_rendered = False
    with st.container():
        if st.session_state.current_conversation_id:
            conv_data = get_conversation_messages(str(st.session_state.current_conversation_id))
            messages_list = (conv_data.get("data") or {}).get("messages") or []
            if messages_list:
                messages_rendered = True
                for msg in messages_list:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div class="message-user-wrap">
                            <div class="message-user">
                                {msg['content']}
                                <div class="msg-timestamp-user">Just now</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Strip any model-generated "📎 Sources : ..." line; we render it only when sources exist.
                        content = msg.get("content", "")
                        content = re.sub(r"(?im)^\\s*📎\\s*Sources\\s*:.*$", "", content).strip()

                        st.markdown(f"""
                        <div class="message-assistant-wrap">
                            <span class="assistant-avatar">🤖</span>
                            <div class="message-assistant">
                                {content}
                                <div class="msg-timestamp-asst">Assistant</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Sources (each source can be dict {"name": "...", "type": "..."} or string)
                        if msg.get("sources"):
                            names = []
                            feedback_id = None
                            for source in msg["sources"]:
                                if isinstance(source, dict) and source.get("type") == "meta":
                                    if source.get("name") in ("feedback_id", "chat_log_id"):
                                        feedback_id = source.get("value")
                                    continue

                                name = source.get("name", source) if isinstance(source, dict) else source
                                if name:
                                    names.append(str(name))

                            if feedback_id:
                                st.markdown(
                                    f"<div style='margin: -6px 0 10px 56px; color: #8B95A8; font-size: 12px;'>Feedback ID : <span style='color:#F0F2F8;'>{feedback_id}</span></div>",
                                    unsafe_allow_html=True,
                                )
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    st.text_input(
                                        "Feedback ID (copier-coller)",
                                        value=feedback_id,
                                        disabled=True,
                                        label_visibility="collapsed",
                                        key=f"fbid_{msg.get('id', feedback_id)}",
                                    )
                                with col_b:
                                    if st.button("Utiliser", key=f"use_fbid_{msg.get('id', feedback_id)}"):
                                        st.session_state.last_chat_log_id = feedback_id
                                        st.toast("✅ Feedback ID sélectionné")

                            if names:
                                joined = " · ".join(names)
                                st.markdown(
                                    f"<div style='margin: -6px 0 10px 56px; color: #8B95A8; font-size: 12px;'>📎 Sources : {joined}</div>",
                                    unsafe_allow_html=True,
                                )
                            with st.expander(f"📎 {len(msg['sources'])} sources"):
                                for source in msg["sources"]:
                                    if isinstance(source, dict) and source.get("type") == "meta":
                                        continue
                                    name = source.get("name", source) if isinstance(source, dict) else source
                                    st.markdown(f'<span class="source-pill">{name}</span>', unsafe_allow_html=True)
    
    if not messages_rendered:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🎓</div>
            <div class="empty-heading">Start a conversation</div>
            <div class="empty-subtext">Ask anything about your university procedures, deadlines, or documents.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    prompt = st.chat_input("💬 Ask anything about university documents...")
    
    if prompt:
        with st.spinner("🔄 Thinking..."):
            result = send_message(prompt, st.session_state.current_conversation_id)
            if result:
                st.session_state.current_conversation_id = result.get("conversation_id")
                if result.get("chat_log_id"):
                    st.session_state.last_chat_log_id = result.get("chat_log_id")
                st.rerun()


# ============================================================================
# PAGE: GENERATE DOCUMENTS
# ============================================================================

def page_generate():
    """Document generation page with form fields customized per document type."""
    # Header
    st.markdown("""
        <div class="main-header">
            <span style="color: #00D4AA; text-shadow: 0 0 10px #00D4AA44;">📄</span> Generate Documents
        </div>
        <div class="header-subtitle">Create administrative documents with your information</div>
        <div class="header-divider" style="background: linear-gradient(90deg, #00D4AA, #6C63FF, transparent);"></div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="form-section-title">Générer un document administratif</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    doc_data = get_generate_types()
    if not doc_data or not doc_data.get("types"):
        st.error("❌ No document types available. Contact administrator.")
        return
    
    doc_types = doc_data["types"]
    fields_by_type = doc_data.get("fields_by_type") or {}
    
    st.markdown('<div class="doc-form-card">', unsafe_allow_html=True)
    
    with st.form("document_generation_form"):
        st.markdown('<div class="form-field-label">Type de document <span style="color: #FF4757;">*</span></div>', unsafe_allow_html=True)
        selected_type = st.selectbox(
            "Select type",
            doc_types,
            index=0,
            label_visibility="collapsed",
            key="gen_doctype",
        )
        
        st.markdown('<div style="margin: 16px 0;"></div>', unsafe_allow_html=True)
        
        fields = fields_by_type.get(selected_type, [])
        form_values = {}
        
        for i, f in enumerate(fields):
            label = f.get("label", f.get("key", ""))
            if f.get("required"):
                label += " *"
            key_suffix = f"gen_{selected_type}_{f['key']}"
            placeholder = f.get("placeholder") or ""
            kind = f.get("kind") or "text"
            
            if kind == "textarea":
                form_values[f["key"]] = st.text_area(
                    label,
                    placeholder=placeholder,
                    height=80,
                    label_visibility="visible",
                    key=key_suffix,
                )
            else:
                default = datetime.today().strftime('%d/%m/%Y') if kind == "date" else ""
                form_values[f["key"]] = st.text_input(
                    label,
                    value=default,
                    placeholder=placeholder,
                    label_visibility="visible",
                    key=key_suffix,
                )
        
        st.markdown('<div style="margin: 20px 0;"></div>', unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            btn_text = st.form_submit_button("📄 Générer", use_container_width=True)
        with col_btn2:
            btn_reset = st.form_submit_button("🔄 Réinitialiser", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if btn_text or btn_reset:
        if btn_reset:
            st.rerun()
        
        required_keys = [f["key"] for f in fields_by_type.get(selected_type, []) if f.get("required")]
        missing = [k for k in required_keys if not (form_values.get(k) or "").strip()]
        if missing:
            labels = {f["key"]: f.get("label", f["key"]) for f in fields_by_type.get(selected_type, [])}
            st.error("❌ Champs obligatoires manquants : " + ", ".join(labels.get(k, k) for k in missing))
        else:
            params = {k: (v or "").strip() for k, v in form_values.items()}
            with st.spinner("✨ Génération du document..."):
                result = generate_document(selected_type, params)
                if result and "text" in result:
                    st.success(f"✅ {selected_type} généré avec succès !")
                    
                    st.markdown('<div class="preview-section">', unsafe_allow_html=True)
                    st.markdown('<div class="preview-title">─── Aperçu ─────────────────────────────────────────────────────────────</div>', unsafe_allow_html=True)
                    st.markdown(f'<pre style="color: #F0F2F8; font-size: 12px; overflow-x: auto;">{result["text"]}</pre>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="⬇️ Télécharger Texte",
                            data=result["text"],
                            file_name=f"{selected_type.lower().replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with col2:
                        pdf_result = generate_pdf(selected_type, params)
                        if pdf_result:
                            st.download_button(
                                label="⬇️ Télécharger PDF",
                                data=pdf_result,
                                file_name=f"{selected_type.lower().replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )


# ============================================================================
# PAGE: ANALYTICS
# ============================================================================

def page_analytics():
    """Analytics dashboard (staff+ only)."""
    st.markdown("""
        <div class="main-header">
            <span style="color: #00D4AA; text-shadow: 0 0 10px #00D4AA44;">📊</span> Analytics Dashboard
        </div>
        <div class="header-subtitle">Track usage and performance metrics</div>
        <div class="header-divider" style="background: linear-gradient(90deg, #00D4AA, #6C63FF, transparent);"></div>
    """, unsafe_allow_html=True)
    
    # Check role
    if st.session_state.user.get("role") == "student":
        st.error("❌ You don't have access to analytics. Contact administrator.")
        return
    
    # Time period selector
    col1, col2, col3 = st.columns([1, 4, 2])
    with col1:
        days = st.selectbox("📅 Period:", [7, 30, 90], format_option=lambda x: f"Last {x} days")
    
    st.divider()
    
    # Get analytics
    with st.spinner("📊 Loading metrics..."):
        stats = get_analytics_summary(days=days)
    
    if stats:
        # Metric cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metrics = [
            ("💬", "Total Chats", stats.get("total_chats", 0), col1),
            ("👥", "Active Users", stats.get("total_users", 0), col2),
            ("⏱️", "Avg Response", f"{stats.get('avg_response_time_ms', 0):.0f}ms", col3),
            ("📄", "Documents", stats.get("total_documents", 0), col4),
            ("😊", "Satisfaction", f"{stats.get('satisfaction_rate', 0):.1f}%", col5),
        ]
        
        for icon, label, value, col in metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No analytics data available")


# ============================================================================
# PAGE: FEEDBACK
# ============================================================================

def page_feedback():
    """Feedback system."""
    st.markdown("""
        <div class="main-header">
            <span style="color: #FF4757; text-shadow: 0 0 10px #FF475744;">📝</span> Feedback
        </div>
        <div class="header-subtitle">Help us improve — share your feedback</div>
        <div class="header-divider" style="background: linear-gradient(90deg, #FF4757, #6C63FF, transparent);"></div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Submit Feedback")
    
    with st.form("feedback_form"):
        default_log_id = st.session_state.get("last_chat_log_id", "")
        chat_log_id = st.text_input(
            "🔍 Feedback ID (Chat Log ID)",
            value=default_log_id,
            placeholder="From last chat response, or paste ID",
        )
        
        col1, col2 = st.columns(2)
        with col1:
            rating = st.radio("👍 Helpful?", ["👍 Yes", "👎 No"], horizontal=True)
        
        with col2:
            category = st.selectbox("📂 Category", ["wrong_answer", "incomplete", "outdated", "other"])
        
        comment = st.text_area("💬 Comment", max_chars=500, placeholder="Your thoughts...")
        correction = st.text_area("✏️ Correction", max_chars=1000, placeholder="Suggest improvement...")
        
        submitted = st.form_submit_button("📤 Submit", use_container_width=True, type="primary")
        
        if submitted:
            if chat_log_id:
                rating_val = 1 if "Yes" in rating else -1
                if submit_feedback(chat_log_id, rating_val, comment, correction, category):
                    st.success("✅ Feedback submitted. Thank you!")
                    st.rerun()
            else:
                st.error("❌ Please provide a Feedback ID")
    
    # Admin section
    if st.session_state.user and st.session_state.user.get("role") == "admin":
        st.divider()
        st.markdown("### 📋 Admin: Feedback Review")
        
        with st.spinner("📊 Loading..."):
            feedback_stats = get_feedback_stats()
        
        if feedback_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px;">📝</div>
                    <div class="metric-value">{feedback_stats.get('total', 0)}</div>
                    <div class="metric-label">Total Feedback</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px;">👍</div>
                    <div class="metric-value">{feedback_stats.get('positive_count', 0)}</div>
                    <div class="metric-label">Positive</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px;">😊</div>
                    <div class="metric-value">{feedback_stats.get('satisfaction_rate', 0):.1f}%</div>
                    <div class="metric-label">Satisfaction</div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def show_navigation():
    """Display sidebar navigation for authenticated users."""
    with st.sidebar:
        # User profile card
        if st.session_state.user:
            initials = st.session_state.user.get('full_name', 'U')[0].upper()
            role = st.session_state.user.get('role', 'student')
            
            st.markdown(f"""
            <div class="user-profile-card">
                <div class="user-avatar">{initials}</div>
                <div class="user-name">{st.session_state.user.get('full_name', 'User')}</div>
                <div class="user-email">{st.session_state.user.get('email', '')}</div>
                <div class="role-badge {role}">{role.upper()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation menu
        st.markdown('<div class="section-label">Navigation</div>', unsafe_allow_html=True)
        
        # Menu items
        menu_items = {
            "💬 Chat": "chat",
            "📄 Generate": "generate",
            "📝 Feedback": "feedback",
        }
        
        # Add analytics for staff+
        if st.session_state.user and st.session_state.user.get("role") != "student":
            menu_items["📊 Analytics"] = "analytics"
        
        # Navigation buttons
        for label, page_id in menu_items.items():
            is_active = st.session_state.page == page_id
            button_type = "primary" if is_active else "secondary"
            
            if st.button(label, use_container_width=True, type=button_type, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "chat"
            st.rerun()


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main app logic."""
    init_session_state()
    
    # Auth pages
    if not st.session_state.token:
        if st.session_state.auth_page == "login":
            page_login()
        else:
            page_register()
        return
    
    # Load user if needed
    if not st.session_state.user:
        st.session_state.user = get_current_user()
        if not st.session_state.user:
            st.error("❌ Failed to load user profile")
            st.session_state.token = None
            st.rerun()
    
    # Show navigation
    show_navigation()
    
    # Route to page
    page = st.session_state.page
    
    if page == "chat":
        page_chat()
    elif page == "generate":
        page_generate()
    elif page == "analytics":
        page_analytics()
    elif page == "feedback":
        page_feedback()
    else:
        st.error(f"Unknown page: {page}")


if __name__ == "__main__":
    main()

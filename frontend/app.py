"""
DeepFluxUniHelp - Professional Streamlit Frontend

A comprehensive university assistant with:
- JWT Authentication with RBAC
- Chat with conversation history & RAG
- Document generation
- Analytics dashboard
- Feedback management
"""

import streamlit as st
import requests
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

# Custom CSS Styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #1f77b4;
        --secondary: #ff7f0e;
        --success: #2ca02c;
        --danger: #d62728;
    }
    
    /* Sidebar styling - Dark purple gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    /* Sidebar text styling */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white !important;
    }
    
    [data-testid="stSidebar"] p {
        color: white !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    [data-testid="stSidebar"] button {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Remove extra spacing in sidebar */
    [data-testid="stSidebar"] > div {
        padding-top: 0.5rem !important;
    }
    
    /* Sidebar dividers */
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Header styling */
    .header-container {
        display: flex;
        align-items: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2em;
    }
    
    .header-container p {
        margin: 5px 0 0 0;
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Menu styling */
    .menu-container {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .menu-button {
        padding: 10px 15px;
        border-radius: 5px;
        border: 1px solid #ddd;
        background-color: #f0f0f0;
        cursor: pointer;
        transition: 0.3s;
    }
    
    .menu-button:hover {
        background-color: #e0e0e0;
    }
    
    .menu-button.active {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    /* Message styling */
    .message-user {
        background-color: #e3f2fd;
        border-left: 4px solid #667eea;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    
    .message-assistant {
        background-color: #f5f5f5;
        border-left: 4px solid #666;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    
    /* Metric card styling */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    
    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    
    /* User info card - compact styling */
    .user-info-card {
        background-color: rgba(255, 255, 255, 0.1);
        border-left: 4px solid #667eea;
        padding: 8px 12px;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        color: white;
        font-size: 0.85em;
        line-height: 1.3;
    }
    
    .user-info-card strong {
        display: block;
        font-size: 0.95em;
        margin-bottom: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# API base URL
API_BASE_URL = "http://localhost:8000"

# --- Session State Management ---
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


# --- API Functions ---
def api_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None,
    token: Optional[str] = None,
) -> tuple[bool, dict | None]:
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
    st.error(f"Login failed: {error_msg}")
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
        st.success("Registration successful! Please log in.")
        return True
    
    error_msg = response.get("detail") or response.get("error") or "Registration failed"
    st.error(f"Error: {error_msg}")
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
    st.error(f"Error: {error_msg}")
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
        error_msg = response.get("error") or "Feedback submission failed"
        st.error(f"Error: {error_msg}")
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


def get_generate_types() -> Optional[list]:
    """Get available document generation types."""
    success, response = api_request(
        "GET",
        "/generate/types",
        token=st.session_state.token,
    )
    return response.get("types") if success else []


def generate_document(doc_type: str) -> Optional[dict]:
    """Generate a document of specified type."""
    success, response = api_request(
        "POST",
        "/generate",
        {"doc_type": doc_type},
        token=st.session_state.token,
    )
    
    if success:
        return response
    
    error_msg = response.get("detail") or response.get("error") or "Document generation failed"
    st.error(f"Error: {error_msg}")
    return None


def generate_pdf(doc_type: str) -> Optional[bytes]:
    """Generate a PDF document of specified type."""
    success, response = api_request(
        "POST",
        "/generate/pdf",
        {"doc_type": doc_type},
        token=st.session_state.token,
    )
    
    if success:
        return response
    
    error_msg = response.get("detail") or response.get("error") or "PDF generation failed"
    st.error(f"Error: {error_msg}")
    return None


# ============================================================================
# PAGE: LOGIN
# ============================================================================
def page_login():
    """User login page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="header-container">
            <h1>🎓 DeepFluxUniHelp</h1>
            <p>University Assistant with Retrieval-Augmented Generation</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🔐 Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@university.edu")
            password = st.text_input("🔐 Password", type="password")
            
            col_submit, col_empty = st.columns([1, 2])
            with col_submit:
                submitted = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submitted and email and password:
                if login(email, password):
                    st.rerun()
        
        st.divider()
        
        st.markdown("### Don't have an account?")
        if st.button("📝 Create Account", use_container_width=True):
            st.session_state.auth_page = "register"
            st.rerun()


# ============================================================================
# PAGE: REGISTER
# ============================================================================
def page_register():
    """User registration page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="header-container">
            <h1>🎓 DeepFluxUniHelp</h1>
            <p>University Assistant with Retrieval-Augmented Generation</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📝 Create Your Account")
        
        with st.form("register_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@university.edu")
            full_name = st.text_input("👤 Full Name", placeholder="John Doe")
            password = st.text_input("🔐 Password", type="password", help="Minimum 8 characters")
            password_confirm = st.text_input("🔐 Confirm Password", type="password")
            
            col_submit, col_empty = st.columns([1, 2])
            with col_submit:
                submitted = st.form_submit_button("✅ Register", use_container_width=True)
            
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
        
        st.markdown("### Already have an account?")
        if st.button("🔑 Back to Login", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()


# ============================================================================
# PAGE: AUTH ROUTER
# ============================================================================
def page_auth():
    """Route between login and register pages."""
    if st.session_state.auth_page == "login":
        page_login()
    else:
        page_register()


# ============================================================================
# PAGE: CHAT
# ============================================================================
def page_chat():
    """Main chat interface."""
    st.title("💬 Chat with Assistant")
    st.markdown("Ask questions and get answers powered by your university documents")
    
    # Sidebar: Conversation History
    with st.sidebar:
        st.header("📚 Conversations")
        
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # Load recent conversations
        conv_data = get_conversations(limit=10)
        if conv_data and conv_data.get("conversations"):
            for conv in conv_data["conversations"]:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"💬 {conv['title'][:30]}", key=f"conv_{conv['id']}", use_container_width=True):
                        st.session_state.current_conversation_id = conv["id"]
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{conv['id']}", help="Delete"):
                        if delete_conversation(conv["id"]):
                            st.success("Deleted!")
                            st.rerun()
        else:
            st.info("📭 No conversations yet. Start a new one!")
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Active Conversation**")
    with col2:
        if st.session_state.current_conversation_id:
            st.caption(f"ID: {str(st.session_state.current_conversation_id)[:8]}...")
    
    # Message display area
    with st.container(height=400):
        if st.session_state.current_conversation_id:
            conv_data = get_conversation_messages(str(st.session_state.current_conversation_id))
            if conv_data and conv_data.get("messages"):
                for msg in conv_data["messages"]:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div class="message-user">
                            <strong>👤 You:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="message-assistant">
                            <strong>🤖 Assistant:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if msg.get("sources"):
                            st.caption("📄 Sources:")
                            for source in msg["sources"][:3]:
                                st.caption(f"  • {source}")
    
    # Input area
    st.divider()
    
    with st.form("message_form"):
        col1, col2 = st.columns([5, 1])
        with col1:
            message = st.text_input("💬 Your question:", placeholder="Ask anything about university documents...")
        with col2:
            submitted = st.form_submit_button("Send ➤", use_container_width=True)
        
        if submitted and message:
            with st.spinner("🔄 Processing..."):
                result = send_message(message, st.session_state.current_conversation_id)
                if result:
                    st.session_state.current_conversation_id = result.get("conversation_id")
                    st.rerun()


# ============================================================================
# PAGE: ANALYTICS
# ============================================================================
def page_analytics():
    """Analytics dashboard (staff+ only)."""
    st.title("📊 Analytics Dashboard")
    st.markdown("Track usage and performance metrics")
    
    # Check role
    if st.session_state.user.get("role") == "student":
        st.error("❌ You don't have access to analytics. Contact administrator.")
        return
    
    # Time period selector
    col1, col2, col3 = st.columns(3)
    with col1:
        days = st.selectbox("📅 Time Period:", [7, 30, 90], index=0, format_option=lambda x: f"Last {x} days")
    
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
            ("⏱️", "Avg Response Time", f"{stats.get('avg_response_time_ms', 0):.0f}ms", col3),
            ("📄", "Documents", stats.get("total_documents", 0), col4),
            ("😊", "Satisfaction", f"{stats.get('satisfaction_rate', 0):.1f}%", col5),
        ]
        
        for icon, label, value, col in metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.5em;">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No analytics data available")


# ============================================================================
# PAGE: GENERATE DOCUMENTS
# ============================================================================
def page_generate():
    """Document generation page."""
    st.title("📄 Generate Documents")
    st.markdown("Create custom documents from your chat history")
    
    doc_types = get_generate_types()
    
    if not doc_types:
        st.error("❌ No document types available. Contact administrator.")
        return
    
    st.info("📋 Select document type and format below")
    st.divider()
    
    # Document type selector
    selected_type = st.selectbox("📋 Choose Document Type:", doc_types, index=0)
    
    st.divider()
    
    # Generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Text Format")
        st.markdown("Download as plain text (.txt)")
        
        if st.button("Generate Text Document", use_container_width=True, key="btn_text"):
            with st.spinner("✨ Generating document..."):
                result = generate_document(selected_type)
                if result and "content" in result:
                    st.success(f"✅ {selected_type} generated successfully!")
                    
                    # Preview
                    with st.expander("📖 Preview Content", expanded=True):
                        st.text_area("Content:", value=result["content"], height=200, disabled=True)
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download as .txt",
                        data=result["content"],
                        file_name=f"{selected_type.lower().replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
    
    with col2:
        st.subheader("📕 PDF Format")
        st.markdown("Download as PDF document (.pdf)")
        
        if st.button("Generate PDF Document", use_container_width=True, key="btn_pdf"):
            with st.spinner("✨ Generating PDF..."):
                result = generate_pdf(selected_type)
                if result and "pdf_content" in result:
                    st.success(f"✅ {selected_type} PDF generated successfully!")
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download as .pdf",
                        data=result["pdf_content"],
                        file_name=f"{selected_type.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    
    st.divider()
    st.info("💡 **Tip:** Documents are generated from your chat history. Use analytics to track generation usage.")


# ============================================================================
# PAGE: FEEDBACK
# ============================================================================
def page_feedback():
    """Feedback system."""
    st.title("📝 Feedback System")
    st.markdown("Help us improve by providing feedback on responses")
    
    st.subheader("Submit Feedback")
    st.markdown("Share your thoughts about a specific chat response")
    
    with st.form("feedback_form"):
        chat_log_id = st.text_input("🔍 Chat Log ID:", placeholder="Paste the ID from chat message")
        
        col1, col2 = st.columns(2)
        with col1:
            rating = st.radio("👍 How was this response?", 
                             [("👍 Helpful", 1), ("👎 Not Helpful", -1)])
        
        with col2:
            category = st.selectbox("📂 Category:", 
                                   ["wrong_answer", "incomplete", "outdated", "other"])
        
        comment = st.text_area("💬 Comment (optional):", max_chars=500, placeholder="Tell us what you think...")
        correction = st.text_area("✏️ Correction (optional):", max_chars=1000, placeholder="Suggest a correction...")
        
        submitted = st.form_submit_button("📤 Submit Feedback", use_container_width=True)
        
        if submitted:
            if chat_log_id:
                if submit_feedback(chat_log_id, rating, comment, correction, category):
                    st.rerun()
            else:
                st.error("❌ Please provide a Chat Log ID")
    
    # Admin feedback review
    if st.session_state.user and st.session_state.user.get("role") == "admin":
        st.divider()
        st.subheader("📋 Admin: Feedback Review")
        
        with st.spinner("📊 Loading feedback stats..."):
            feedback_stats = get_feedback_stats()
        
        if feedback_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.5em;">📝</div>
                    <div class="metric-value">{feedback_stats.get('total', 0)}</div>
                    <div class="metric-label">Total Feedback</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.5em;">👍</div>
                    <div class="metric-value">{feedback_stats.get('positive_count', 0)}</div>
                    <div class="metric-label">Positive</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.5em;">👎</div>
                    <div class="metric-value">{feedback_stats.get('negative_count', 0)}</div>
                    <div class="metric-label">Negative</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.5em;">😊</div>
                    <div class="metric-value">{feedback_stats.get('satisfaction_rate', 0):.1f}%</div>
                    <div class="metric-label">Satisfaction</div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application logic."""
    init_session_state()
    
    # Show auth pages if not logged in
    if not st.session_state.token:
        page_auth()
        return
    
    # Load user profile if needed
    if not st.session_state.user:
        st.session_state.user = get_current_user()
        if not st.session_state.user:
            st.error("❌ Failed to load user profile")
            st.session_state.token = None
            st.rerun()
    
    # Show sidebar navigation
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


# ============================================================================
# SIDEBAR NAVIGATION (when logged in)
# ============================================================================
def show_navigation():
    """Display navigation sidebar for logged-in users."""
    with st.sidebar:
        # User info - Compact styling
        if st.session_state.user:
            st.markdown(f"""
            <div class="user-info-card">
                <strong>👤 {st.session_state.user.get('full_name', 'User')}</strong>
                📧 {st.session_state.user.get('email', '')}<br>
                🎯 {st.session_state.user.get('role', '').title()}
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation menu
        st.markdown("#### 🔗 Navigation")
        
        # Build menu items
        menu_items = {
            "💬 Chat": "chat",
            "📄 Generate": "generate",
            "📝 Feedback": "feedback",
        }
        
        # Add analytics only for staff+
        if st.session_state.user and st.session_state.user.get("role") != "student":
            menu_items["📊 Analytics"] = "analytics"
        
        # Menu buttons - Compact with reduced padding
        for label, page_id in menu_items.items():
            is_active = st.session_state.page == page_id
            button_type = "primary" if is_active else "secondary"
            
            if st.button(label, use_container_width=True, type=button_type, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
        
        st.divider()
        
        # Logout button - Compact
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()


if __name__ == "__main__":
    main()


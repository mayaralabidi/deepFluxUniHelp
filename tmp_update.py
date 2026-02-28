import re

def update_app_py():
    with open('frontend/app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace the entire CSS block
    old_css_match = re.search(r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)', content, re.DOTALL)
    
    new_css = '''st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

/* Global resets & fonts */
* {
    font-family: 'Inter', sans-serif;
}
body {
    background-color: #0F1117;
    color: #F0F2F8;
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
.stApp {
    background-color: #0F1117;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Smooth scrollbar styling */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0F1117;
}
::-webkit-scrollbar-thumb {
    background: #6C63FF;
    border-radius: 10px;
}
* {
    transition: all 0.2s ease;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #161B27 !important;
    border-right: 1px solid #2A3142;
    min-width: 280px !important;
    max-width: 280px !important;
}
section[data-testid="stSidebar"] { 
    width: 280px !important; 
}

/* Hide sidebar toggle arrow */
[data-testid="collapsedControl"] {
    display: none;
}

/* User profile card (top of sidebar) */
.user-info-card {
    background: linear-gradient(135deg, #1E2433, #252D40);
    border: 1px solid #2A3142;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
}
.user-avatar {
    background: linear-gradient(135deg, #6C63FF, #00D4AA);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 16px;
    color: white;
    flex-shrink: 0;
}
.user-details {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.user-name {
    font-size: 14px;
    color: #F0F2F8;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
}
.user-email {
    font-size: 11px;
    color: #8B95A8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 6px;
}
.role-badge {
    border-radius: 10px;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 2px 8px;
    display: inline-block;
    width: fit-content;
}
.role-badge.student { background: #6C63FF22; color: #6C63FF; border: 1px solid #6C63FF44; }
.role-badge.staff { background: #00D4AA22; color: #00D4AA; border: 1px solid #00D4AA44; }
.role-badge.admin { background: #FF475722; color: #FF4757; border: 1px solid #FF475744; }

/* Section labels */
.section-label {
    font-size: 10px;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
    margin-bottom: 8px;
    margin-top: 16px;
}

/* Navigation buttons (Targeting Streamlit buttons via custom classes when possible) */
/* Overriding Streamlit button default styles in Sidebar */
[data-testid="stSidebar"] button {
    width: 100%;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    background: transparent !important;
    color: #8B95A8 !important;
    border: none !important;
    box-shadow: none !important;
    display: flex !important;
    justify-content: flex-start !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] button:hover {
    background: #1E2433 !important;
    color: #F0F2F8 !important;
    border-left: 3px solid #6C63FF !important;
}
[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #6C63FF15, transparent) !important;
    color: #6C63FF !important;
    border-left: 3px solid #6C63FF !important;
    font-weight: 600 !important;
}

/* Custom classes for st.markdown buttons */
.btn-new-conv {
    background: linear-gradient(135deg, #6C63FF, #8B5CF6);
    border-radius: 10px;
    width: 100%;
    color: white;
    font-weight: 600;
    padding: 10px;
    text-align: center;
    cursor: pointer;
    border: none;
    display: block;
    text-decoration: none;
}
.btn-new-conv:hover {
    filter: brightness(1.1);
    box-shadow: 0 4px 15px #6C63FF44;
}

/* Conversation list items */
.conv-item {
    border-radius: 8px;
    padding: 10px 12px;
    background: transparent;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    margin-bottom: 4px;
    color: #F0F2F8;
    text-decoration: none;
}
.conv-item:hover {
    background: #1E2433;
}
.conv-item.active {
    background: #1E2433;
    border-left: 3px solid #6C63FF;
}
.conv-title {
    font-size: 13px;
    max-width: 180px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.conv-date {
    font-size: 11px;
    color: #4A5568;
}

/* Dividers */
hr {
    border: none;
    border-top: 1px solid #2A3142;
    margin: 12px 0;
}
[data-testid="stSidebar"] hr {
    margin: 12px 0 !important;
    border-color: #2A3142 !important;
}

/* Header section */
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
}
.header-divider {
    background: linear-gradient(90deg, #6C63FF, #00D4AA, transparent);
    height: 2px;
    border-radius: 2px;
    margin-bottom: 24px;
    margin-top: 8px;
}

/* Chat messages area */
.chat-container {
    max-width: 780px;
    margin: 0 auto;
    padding-bottom: 80px;
}
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
    position: relative;
}
.assistant-avatar {
    position: absolute;
    top: -10px;
    left: -10px;
    font-size: 20px;
    background: #161B27;
    border-radius: 50%;
}
.msg-timestamp-asst {
    font-size: 10px;
    color: #4A5568;
    margin-top: 4px;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

/* Sources section */
.sources-chip {
    cursor: pointer;
    font-size: 12px;
    color: #8B95A8;
    background: #0F1117;
    border: 1px solid #2A3142;
    padding: 4px 8px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
}
.sources-content {
    background: #0F1117;
    border: 1px solid #2A3142;
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
    font-size: 12px;
}
.source-pill {
    background: #6C63FF15;
    color: #6C63FF;
    border-radius: 6px;
    padding: 2px 6px;
    display: inline-block;
    margin-right: 4px;
    margin-bottom: 4px;
}

/* Empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
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
}

/* Login/Register Card */
.auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding-top: 10vh;
}
.auth-card {
    background: #1E2433;
    border: 1px solid #2A3142;
    border-radius: 16px;
    padding: 40px;
    width: 100%;
    max-width: 420px;
    margin: 0 auto;
}
.auth-logo {
    font-size: 40px;
    text-align: center;
    margin-bottom: 16px;
}
.auth-title {
    text-align: center;
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #00D4AA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.auth-subtitle {
    text-align: center;
    font-size: 12px;
    color: #8B95A8;
    margin-bottom: 32px;
}

/* Streamlit Inputs Customization */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background-color: #1E2433 !important;
    border: 1px solid #2A3142 !important;
    border-radius: 14px !important;
    color: #F0F2F8 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox > div > div:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px #6C63FF22 !important;
}

/* Primary Button global override */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    filter: brightness(1.1);
    box-shadow: 0 4px 15px #6C63FF44 !important;
}

/* Analytics Cards */
.metric-card-new {
    background: #1E2433;
    border: 1px solid transparent;
    background-image: linear-gradient(#1E2433, #1E2433), linear-gradient(135deg, #2A3142, #6C63FF44);
    background-origin: border-box;
    background-clip: content-box, border-box;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value-new {
    font-size: 2em;
    font-weight: 800;
    color: #F0F2F8;
}
.metric-label-new {
    font-size: 0.9em;
    color: #8B95A8;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)'''

    if old_css_match:
        content = content[:old_css_match.start()] + new_css + content[old_css_match.end():]

    # Replacing user-info rendering
    old_user_info = '''            <div class="user-info-card">
                <strong>👤 {st.session_state.user.get('full_name', 'User')}</strong>
                📧 {st.session_state.user.get('email', '')}<br>
                🎯 {st.session_state.user.get('role', '').title()}
            </div>'''
            
    new_user_info = '''            <div class="user-info-card">
                <div class="user-avatar">{st.session_state.user.get('full_name', 'U')[0].upper()}</div>
                <div class="user-details">
                    <span class="user-name">{st.session_state.user.get('full_name', 'User')}</span>
                    <span class="user-email">{st.session_state.user.get('email', '')}</span>
                    <span class="role-badge {st.session_state.user.get('role', 'student')}">{st.session_state.user.get('role', 'student')}</span>
                </div>
            </div>'''
    content = content.replace(old_user_info, new_user_info)
    
    # Replacing header in login/register
    old_header = '''        <div class="header-container">
            <h1>🎓 DeepFluxUniHelp</h1>
            <p>University Assistant with Retrieval-Augmented Generation</p>
        </div>'''
        
    new_header = '''        <div class="auth-card">
            <div class="auth-logo">🎓</div>
            <div class="auth-title">deepFluxUniHelp</div>
            <div class="auth-subtitle">University Administrative Assistant</div>'''
            
    content = content.replace(old_header, new_header)

    with open('frontend/app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_app_py()
    print("Done")

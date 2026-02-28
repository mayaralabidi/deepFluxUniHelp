# Quick Start Guide - DeepFluxUniHelp V2.0

## What's New

Your application now includes **4 enterprise features**:

### 1️⃣ JWT Authentication & Role-Based Access Control

- Users can register and login with email/password
- 3 roles: Student, Staff, Admin
- Secure token-based authentication
- Different access levels for different endpoints

### 2️⃣ Conversation History & Memory

- Chat history is stored in database
- Recent messages injected into RAG for context-aware responses
- Users can manage conversations (view, delete, archive, search)
- Auto-generated conversation titles

### 3️⃣ Analytics Dashboard

- Track usage statistics (chats, users, documents)
- Response time monitoring
- Knowledge gap detection (unanswered questions)
- Staff and Admin only

### 4️⃣ Feedback System

- Users rate responses (👍 helpful / 👎 not helpful)
- Provide feedback comments and corrections
- Admin review and management panel
- Satisfaction rate tracking

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Database
DATABASE_PATH=data/chroma/chroma.db

# Security (Generate a random secret key)
SECRET_KEY=your-secret-key-here-32-chars-minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default admin account (change these!)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=AdminPassword123

# LLM API
GROQ_API_KEY=your-groq-api-key-here

# Other settings (optional)
DEBUG=false
```

### 3. Load Sample Data (Optional)

```bash
python scripts/ingest_sample.py
```

### 4. Start the Backend

```bash
python scripts/run_api.py
```

✅ API will be available at `http://localhost:8000`

### 5. Start the Frontend (in a new terminal)

```bash
streamlit run frontend/app.py
```

✅ Frontend will be available at `http://localhost:8501`

---

## How to Use

### Create an Account

1. Open `http://localhost:8501`
2. Click **Register**
3. Enter email, name, and password
4. Submit → You now have a **Student** account

### Chat with RAG

1. Click **💬 Chat**
2. Type your question
3. Send → Get response with sources
4. Continue conversation → Recent messages used as context

### Submit Feedback

1. Click **📝 Feedback**
2. Get a chat log ID from the chat interface
3. Rate the response (👍 or 👎)
4. Add optional comments or corrections
5. Submit

### View Analytics (Staff/Admin Only)

1. Register as staff or admin user (see Admin section below)
2. Click **📊 Analytics**
3. Select time period
4. View:
   - Total chats
   - Active users
   - Response times
   - Satisfaction rate

---

## Admin Functions

### Create Admin User

```python
# Option 1: Via API
POST http://localhost:8000/auth/register
{
    "email": "admin@example.com",
    "password": "SecurePassword123",
    "full_name": "Admin User"
}

# Option 2: Manually edit default admin in .env
# Set ADMIN_EMAIL and ADMIN_PASSWORD before first startup
```

### Admin Capabilities

- ✅ Ingest documents
- ✅ Reset vector store
- ✅ View analytics dashboard
- ✅ Review and resolve feedback
- ✅ All student/staff capabilities

---

## API Reference

### Authentication

```bash
# Register
POST /auth/register
{
    "email": "user@example.com",
    "password": "password",
    "full_name": "User Name"
}

# Login
POST /auth/login
{
    "email": "user@example.com",
    "password": "password"
}
Response: { "access_token": "...", "user": {...} }

# Get current user
GET /auth/me
Headers: Authorization: Bearer {token}

# Refresh token
POST /auth/refresh
Headers: Authorization: Bearer {token}
```

### Chat

```bash
# Send message
POST /chat
Headers: Authorization: Bearer {token}
{
    "message": "Your question",
    "conversation_id": "uuid-or-null",
    "create_new": false
}

# List conversations
GET /chat/conversations?limit=20&offset=0
Headers: Authorization: Bearer {token}

# Get conversation history
GET /chat/conversations/{id}
Headers: Authorization: Bearer {token}

# Delete conversation
DELETE /chat/conversations/{id}
Headers: Authorization: Bearer {token}

# Search conversations
GET /chat/conversations/search/{query}
Headers: Authorization: Bearer {token}
```

### Feedback

```bash
# Submit feedback
POST /feedback
Headers: Authorization: Bearer {token}
{
    "chat_log_id": "uuid",
    "rating": 1 or -1,
    "comment": "optional comment",
    "correction": "optional correction",
    "category": "wrong_answer|incomplete|outdated|other"
}

# List feedback (staff+)
GET /feedback/list?limit=20&offset=0
Headers: Authorization: Bearer {token}

# Get statistics (staff+)
GET /feedback/stats
Headers: Authorization: Bearer {token}

# Mark reviewed (admin)
PATCH /feedback/{id}/review
Headers: Authorization: Bearer {token}
{ "admin_notes": "..." }

# Mark resolved (admin)
PATCH /feedback/{id}/resolve
Headers: Authorization: Bearer {token}
```

### Analytics

```bash
# Summary statistics
GET /analytics/summary?days=7
Headers: Authorization: Bearer {token}

# Top questions
GET /analytics/top-questions?limit=10&days=7
Headers: Authorization: Bearer {token}

# Top documents
GET /analytics/top-documents?limit=10&days=7
Headers: Authorization: Bearer {token}

# Daily usage
GET /analytics/daily-usage?days=7
Headers: Authorization: Bearer {token}

# Unanswered questions
GET /analytics/unanswered?limit=10
Headers: Authorization: Bearer {token}
```

---

## Database Tables

### users

- id, email, hashed_password, full_name, student_id, role, is_active, created_at, updated_at

### conversations

- id, user_id, title, is_archived, created_at, updated_at

### messages

- id, conversation_id, role, content, sources, created_at

### chat_logs (for analytics)

- id, user_id, question, answer, sources, response_time_ms, tokens_used, conversation_id, created_at

### document_accesses

- id, document_name, accessed_by_user_id, access_type, created_at

### feedback_logs

- id, chat_log_id, user_id, rating, comment, correction, category, reviewed_by_admin, admin_notes, resolved_at, created_at

---

## Troubleshooting

### Issue: Port 8000 already in use

```bash
# Kill existing process
taskkill /PID {pid} /F

# Or use different port
python -m uvicorn backend.main:app --port 8001
```

### Issue: "ModuleNotFoundError"

```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Reinstall specific package
pip install aiosqlite
pip install python-jose[cryptography]
```

### Issue: Database locked

```bash
# Delete the database file to start fresh
rm data/chroma/chroma.db

# Or wait for other connections to close
```

### Issue: Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:8000/docs

# Check API_BASE_URL in frontend/app.py is correct
# Default: http://localhost:8000
```

---

## Key Features Explained

### Conversation History with RAG

When you send a message, the system:

1. Retrieves your last 6 messages
2. Formats them as conversation context
3. Injects into RAG prompt along with document search
4. LLM generates response aware of previous context
5. New messages stored for future reference

### Analytics Tracking

Every action is logged:

- Chat questions/answers with response time
- Document access (retrieved, uploaded, deleted, generated)
- Feedback ratings and categories
- Used to generate dashboard statistics

### Feedback System

- Users rate responses to improve knowledge base
- Corrections can be submitted for knowledge gaps
- Admin reviews feedback, marks as resolved
- Satisfaction metrics tracked over time

---

## Files Changed

**Backend API:**

- `backend/main.py` - FastAPI initialization
- `backend/app/core/config.py` - Configuration
- `backend/app/core/database.py` - SQLAlchemy setup
- `backend/app/core/security.py` - JWT & passwords
- `backend/app/core/dependencies.py` - RBAC
- `backend/app/models/user.py` - User model
- `backend/app/models/conversation.py` - Conversation models
- `backend/app/models/analytics.py` - Analytics models
- `backend/app/api/auth.py` - Auth endpoints
- `backend/app/api/chat.py` - Chat endpoints (refactored)
- `backend/app/api/documents.py` - Document endpoints (updated)
- `backend/app/api/generate.py` - Generation endpoints (updated)
- `backend/app/api/analytics.py` - Analytics endpoints (NEW)
- `backend/app/api/feedback.py` - Feedback endpoints (NEW)
- `backend/app/services/conversation_service.py` - Conversation logic (NEW)
- `backend/app/services/analytics_service.py` - Analytics logic (NEW)
- `backend/app/services/feedback_service.py` - Feedback logic (NEW)
- `backend/app/rag/chain.py` - RAG chain (updated for history)

**Frontend:**

- `frontend/app.py` - Complete Streamlit app (refactored)

---

## Next Steps

### Immediate

1. ✅ Test registration & login
2. ✅ Test chat functionality
3. ✅ Test analytics dashboard
4. ✅ Test feedback system

### Short-term

- [ ] Create test accounts with different roles
- [ ] Load documents using admin function
- [ ] Generate analytics by chatting
- [ ] Review feedback as admin

### Medium-term

- [ ] Write unit tests
- [ ] Deploy to production
- [ ] Monitor usage patterns
- [ ] Collect user feedback

### Long-term

- [ ] Migrate to PostgreSQL
- [ ] Add Redis caching
- [ ] Build mobile app
- [ ] Advanced analytics

---

## Support

**API Docs:** http://localhost:8000/docs (Swagger UI)
**Alternative Docs:** http://localhost:8000/redoc (ReDoc)

Questions? Check the implementation files:

- `FEATURES_IMPLEMENTED.md` - Detailed feature docs
- `docs/CHOIX_TECHNIQUES.md` - Technical choices
- `docs/CAHIER_DES_CHARGES.md` - Original requirements

---

**Happy chatting! 🎓**

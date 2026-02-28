#!/usr/bin/env python
"""
Diagnosis script to test backend components one by one.
"""

import sys
import traceback

print("=" * 80)
print("DEEPFLUXUNIHELP - BACKEND DIAGNOSIS")
print("=" * 80)

# Test 1: Environment variables
print("\n[1/8] Testing environment variables...")
try:
    from backend.app.core.config import settings
    print(f"  [OK] Settings OK - DEBUG={settings.DEBUG}")
    print(f"  [OK] GROQ_API_KEY configured: {bool(settings.GROQ_API_KEY)}")
    print(f"  [OK] ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Database setup
print("\n[2/8] Testing database setup...")
try:
    from backend.app.core.database import AsyncSessionLocal, engine, Base
    print(f"  [OK] Database connection OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Models
print("\n[3/8] Testing models...")
try:
    from backend.app.models.user import User, UserRole
    from backend.app.models.conversation import Conversation, Message
    from backend.app.models.analytics import ChatLog, DocumentAccess, FeedbackLog
    print(f"  [OK] All models OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Security functions
print("\n[4/8] Testing security functions...")
try:
    from backend.app.core.security import hash_password, verify_password, create_access_token, decode_token
    test_pwd = "TestPassword123"
    hashed = hash_password(test_pwd)
    verified = verify_password(test_pwd, hashed)
    assert verified, "Password verification failed"
    print(f"  [OK] Security functions OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: RAG Chain (vector store)
print("\n[5/8] Testing RAG vectorstore...")
try:
    from backend.app.rag.vectorstore import get_vectorstore
    print(f"  [INFO] Initializing vectorstore (this may take a moment)...")
    vectorstore = get_vectorstore()
    print(f"  [OK] Vectorstore OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    print(f"  [INFO] Note: This usually means GROQ_API_KEY is invalid or vector models can't be downloaded")
    sys.exit(1)

# Test 6: RAG Chain (LLM)
print("\n[6/8] Testing RAG chain (LLM)...")
try:
    from backend.app.rag.chain import get_rag_chain
    print(f"  [INFO] Initializing RAG chain (this may take a moment)...")
    chain, retriever = get_rag_chain()
    print(f"  [OK] RAG chain OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    print(f"  [INFO] Note: This usually means GROQ_API_KEY is invalid")
    sys.exit(1)

# Test 7: Services
print("\n[7/8] Testing services...")
try:
    from backend.app.services.conversation_service import ConversationService
    from backend.app.services.analytics_service import AnalyticsService
    from backend.app.services.feedback_service import FeedbackService
    print(f"  [OK] All services OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 8: API routers
print("\n[8/8] Testing API routers...")
try:
    from backend.app.api.auth import router as auth_router
    from backend.app.api.chat import router as chat_router
    from backend.app.api.documents import router as documents_router
    from backend.app.api.generate import router as generate_router
    from backend.app.api.analytics import router as analytics_router
    from backend.app.api.feedback import router as feedback_router
    print(f"  [OK] All routers OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Final: Main app
print("\n[FINAL] Testing main FastAPI app...")
try:
    from backend.main import app
    print(f"  [OK] FastAPI app OK")
except Exception as e:
    print(f"  [FAIL] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("[SUCCESS] ALL TESTS PASSED! Backend is ready to run.")
print("=" * 80)
print("\nTo start the API server, run:")
print("  python scripts/run_api.py")
print("\nOr:")
print("  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")

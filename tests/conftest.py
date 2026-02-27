"""
Pytest configuration and fixtures
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set test env vars
os.environ.setdefault("CHROMA_PERSIST_DIR", str(project_root / "data" / "test_chroma"))
os.environ.setdefault("GROQ_API_KEY", "sk-test-key")  # Mock for tests without API


@pytest.fixture
def api_base_url():
    """API base URL for E2E tests."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")

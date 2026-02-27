"""
E2E API tests
Run with: pytest tests/test_api.py -v
Requires API running: uvicorn backend.main:app --port 8000
"""

import httpx
import pytest


@pytest.fixture
def client():
    """HTTP client for API tests."""
    base_url = "http://localhost:8000"
    with httpx.Client(base_url=base_url, timeout=30.0) as c:
        yield c


class TestHealth:
    """Health endpoints."""

    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert "deepFluxUniHelp" in str(data)

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json().get("status") == "healthy"


class TestDocuments:
    """Documents API."""

    def test_search_empty(self, client):
        """Search returns 200 (may be empty if no docs indexed)."""
        r = client.post("/documents/search", json={"query": "attestation", "top_k": 2})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_generate_types(self, client):
        """List document types."""
        r = client.get("/generate/types")
        assert r.status_code == 200
        data = r.json()
        assert "types" in data
        assert "attestation" in data["types"]
        assert "reclamation" in data["types"]
        assert "convention_stage" in data["types"]


class TestGenerate:
    """Document generation (requires OPENAI_API_KEY)."""

    @pytest.mark.skipif(
        not __import__("os").environ.get("GROQ_API_KEY", "").startswith("sk-") and not __import__("os").environ.get("GROQ_API_KEY", "").startswith("gsk_"),
        reason="GROQ_API_KEY not set or invalid",
    )
    def test_generate_attestation(self, client):
        r = client.post(
            "/generate/",
            json={
                "doc_type": "attestation",
                "params": {
                    "nom": "Jean Dupont",
                    "numero_etudiant": "2024001234",
                    "type_attestation": "Inscription",
                    "motif": "CAF",
                    "date": "27/02/2025",
                },
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "text" in data
        assert len(data["text"]) > 50
        assert "attestation" in data.get("doc_type", "")

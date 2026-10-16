import pytest
from app.services.ai_service import get_ai_provider
from app.database import SessionLocal

def test_rag_hallucination_guard():
    ai = get_ai_provider()
    db = SessionLocal()
    try:
        # Scenario with nonexistent act details
        fake_facts = {
            "incident_type": "Space Crimes Act 3025",
            "location": "Mars colony alpha"
        }
        response = ai.generate_legal_analysis(fake_facts, "en", db)

        # Check that no citation lists are fabricated for unverified acts
        citations = getattr(response, "citations", [])
        assert len(citations) > 0
        for citation in citations:
            assert citation.source_authority == "Unverified" or citation.confidence == "Low"
            assert "Unable to verify this provision" in citation.summary

    finally:
        db.close()

def test_rag_verified_retrieval():
    ai = get_ai_provider()
    db = SessionLocal()
    try:
        real_facts = {
            "incident_type": "Physical assault",
            "location": "Market"
        }
        response = ai.generate_legal_analysis(real_facts, "en", db)
        assert "provisions" in response
        assert len(response["provisions"]) > 0
        first_prov = response["provisions"][0]
        assert "Bharatiya Nyaya Sanhita, 2023" in first_prov["act"]
        assert first_prov["verification_status"] == "VERIFIED"
        assert "indiacode.nic.in" in first_prov["source_url"]
    finally:
        db.close()

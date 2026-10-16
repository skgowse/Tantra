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
        for citation in response.citations:
            assert citation.source_authority == "Unverified" or citation.confidence == "Low"
            assert "Unable to verify this provision" in citation.summary
            
    finally:
        db.close()

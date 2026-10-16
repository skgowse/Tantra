import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.services.ai_provider import get_ai_provider, GeminiAIProvider, DeterministicFallbackProvider
from app.services.summary_service import generate_factual_incident_summary

client = TestClient(app)

# =====================================================================
# SCENARIO A: A user reports receiving a threatening message.
# =====================================================================
def test_scenario_a_threatening_message():
    res = client.post("/api/chat/message", json={
        "message": "A stranger called me and threatened to kill me if I don't give him money.",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["extracted_facts"]["incident_type"] == "Physical Assault or Threats"
    assert data["jurisdiction_hint"] == "criminal"

    # Analyze legal grounds
    res_analysis = client.post("/api/incident/analyze", json={
        "facts": data["extracted_facts"],
        "language": "en"
    })
    assert res_analysis.status_code == 200
    analysis = res_analysis.json()
    sections = [p["section_number"] for p in analysis["provisions"]]
    assert "351" in sections  # Criminal Intimidation under BNS 2023

# =====================================================================
# SCENARIO B: A user reports a suspected online bank fraud with amount.
# =====================================================================
def test_scenario_b_online_bank_fraud():
    res = client.post("/api/chat/message", json={
        "message": "I received an SMS with a link. After clicking, Rs. 45000 was debited from my SBI bank account via UPI.",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    facts = data["extracted_facts"]
    assert "45000" in facts.get("injuries_or_loss", "")
    assert data["jurisdiction_hint"] == "financial_cyber"
    assert "1930" in data.get("suggested_next_step", "")

    # Summary verification
    summary_res = client.post("/api/incident/summary", json={"facts": facts, "language": "en"})
    assert summary_res.status_code == 200
    stmt = summary_res.json()["statement_text"]
    assert "45000" in stmt
    assert "National Cyber Crime Reporting Portal" in summary_res.json()["target_authority"]

# =====================================================================
# SCENARIO C: A user describes a property ownership dispute (civil).
# =====================================================================
def test_scenario_c_property_ownership_dispute_non_criminal():
    res = client.post("/api/chat/message", json={
        "message": "My neighbor has placed a fence crossing over our legal boundary wall on our ancestral land. There is no physical fight, but he claims the land is his.",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    facts = data["extracted_facts"]
    assert facts["jurisdiction_type"] == "civil"
    assert "Civil Court" in data["suggested_next_step"]

    # Factual summary should NOT demand a criminal FIR
    summary_res = client.post("/api/incident/summary", json={"facts": facts, "language": "en"})
    assert summary_res.status_code == 200
    stmt = summary_res.json()["statement_text"]
    assert "Civil Court" in summary_res.json()["target_authority"]
    assert "FIR under relevant sections" not in stmt  # Does not force criminal FIR

# =====================================================================
# SCENARIO D: An incomplete incident description.
# =====================================================================
def test_scenario_d_incomplete_incident_description():
    res = client.post("/api/chat/message", json={
        "message": "Someone harassed me.",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["is_clarified"] is False
    assert len(data["missing_facts"]) > 0
    # Must ask a targeted follow up question
    assert len(data["reply"]) > 10

# =====================================================================
# SCENARIO E: A user reports injury and immediate physical threat.
# =====================================================================
def test_scenario_e_immediate_threat_and_injury():
    res = client.post("/api/chat/message", json={
        "message": "He is attacking me now with a knife and I am bleeding heavily right now inside my house!",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["safety_alert"] is True
    assert "112" in data["reply"]
    assert "108" in data["reply"]

# =====================================================================
# SCENARIO F: A user changes an earlier answer.
# =====================================================================
def test_scenario_f_user_changes_earlier_answer():
    # User initially mentions yesterday, then changes to last week
    res1 = client.post("/api/chat/message", json={
        "message": "This happened yesterday.",
        "language": "en"
    })
    session_id = res1.json()["session_id"]

    res2 = client.post("/api/chat/message", json={
        "session_id": session_id,
        "message": "Actually wait, I made a mistake, it was not yesterday, it happened 2 weeks ago.",
        "language": "en"
    })
    assert res2.status_code == 200
    # System accepts update without crashing
    assert res2.json()["session_id"] == session_id

# =====================================================================
# SCENARIO G: A user enters Telugu text.
# =====================================================================
def test_scenario_g_telugu_language_flow():
    res = client.post("/api/chat/message", json={
        "message": "నిన్న సాయంత్రం కాలేజీ దగ్గర ఒక వ్యక్తి నన్ను చంపేస్తానని బెదిరించాడు.",
        "language": "te"
    })
    assert res.status_code == 200
    data = res.json()
    # Response must be in Telugu
    assert any(ord(char) >= 0x0C00 and ord(char) <= 0x0C7F for char in data["reply"])
    assert data["extracted_facts"]["incident_type"] == "Physical Assault or Threats"

# =====================================================================
# SCENARIO H: An AI provider becomes unavailable (Fallback check).
# =====================================================================
def test_scenario_h_ai_provider_failure_fallback():
    # Simulate failed Gemini provider with invalid key
    broken_gemini = GeminiAIProvider("invalid_fake_key_test")
    # Calling interpret_and_respond should gracefully fall back to deterministic response
    result = broken_gemini.interpret_and_respond(
        messages=[{"role": "user", "content": "My laptop was stolen from library."}],
        language="en",
        existing_facts={}
    )
    assert result is not None
    assert "reply" in result
    assert result["extracted_facts"]["incident_type"] == "Theft or Robbery"
    assert result["provider_used"] == "deterministic"

# =====================================================================
# SCENARIO I: A legal source cannot be verified.
# =====================================================================
def test_scenario_i_unverified_source_cannot_be_verified():
    ai = get_ai_provider()
    db = SessionLocal()
    try:
        fake_facts = {
            "incident_type": "Fictitious Martian Space Law 3025",
            "location": "Sector 99 Mars"
        }
        res = ai.generate_legal_analysis(fake_facts, "en", db)
        citations = getattr(res, "citations", [])
        assert len(citations) > 0
        assert citations[0].source_authority == "Unverified"
        assert "Unable to verify this provision" in citations[0].summary
    finally:
        db.close()

# =====================================================================
# SCENARIO J: Summary generated with missing dates, names, or evidence.
# =====================================================================
def test_scenario_j_summary_with_missing_information_no_fabrication():
    # Incomplete facts: no date, no location, no people
    minimal_facts = {
        "incident_type": "General dispute",
        "alleged_actions": "A disagreement occurred over an order"
    }
    summary = generate_factual_incident_summary(minimal_facts, "en")
    stmt = summary["statement_text"]

    # Verify that missing fields are explicitly marked 'Not provided', NEVER fabricated
    assert "Date / Time: Not provided" in stmt
    assert "Location: Not provided" in stmt
    assert "PERSONS OR ROLES INVOLVED (AS REPORTED):\nNot specified by user" in stmt
    # STRICT RULE: No fabricated provocation
    assert "No provocation was initiated" not in stmt
    assert "complainant reports the following events" in stmt

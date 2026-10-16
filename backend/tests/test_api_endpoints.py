import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Operational"
    assert "BNS 2023" in data["legal_sources"]
    assert "en" in data["language_support"]
    assert "te" in data["language_support"]

def test_emergency_contacts_endpoint():
    response = client.get("/api/emergency/contacts")
    assert response.status_code == 200
    contacts = response.json()["emergency_contacts"]
    assert any(c["number"] == "112" for c in contacts)
    assert any(c["number"] == "1930" for c in contacts)
    assert any(c["number"] == "108" for c in contacts)

def test_chat_message_intake_and_reset():
    # 1. Send initial user message
    res1 = client.post("/api/chat/message", json={
        "message": "Someone sent me threatening messages on WhatsApp yesterday outside college.",
        "language": "en"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert "session_id" in data1
    session_id = data1["session_id"]
    assert data1["extracted_facts"]["incident_type"] is not None
    assert "reply" in data1

    # 2. Reset session
    res2 = client.post("/api/chat/reset", json={"session_id": session_id})
    assert res2.status_code == 200
    assert "Session reset successfully" in res2.json()["message"]

def test_empty_message_rejected():
    res = client.post("/api/chat/message", json={"message": "   ", "language": "en"})
    assert res.status_code == 400

def test_legal_library_and_search():
    res_lib = client.get("/api/legal/library")
    assert res_lib.status_code == 200
    provisions = res_lib.json()["provisions"]
    assert len(provisions) >= 5

    res_search = client.get("/api/legal/search?q=intimidation")
    assert res_search.status_code == 200
    results = res_search.json()["results"]
    assert len(results) > 0
    assert any("351" in r["section_number"] for r in results)

def test_document_analyzer():
    sample_text = """
    NOTICE UNDER SECTION 35 OF BNSS, 2023
    Police Station Sector 14, Gurugram.
    FIR No. 421/2026 dated 14/08/2026.
    You are hereby directed to appear before the Station House Officer on 20/08/2026.
    Failure to appear may result in judicial summons and cancellation of bail.
    """
    res = client.post("/api/document/analyze", data={"text_content": sample_text})
    assert res.status_code == 200
    data = res.json()
    assert len(data["dates_found"]) > 0
    assert any("421" in ref for ref in data["case_references"])
    assert any(t["term"] == "BAIL" for t in data["explained_terms"])
    assert "Police" in data["identified_forum"]

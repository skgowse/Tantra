import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_case_level_authorization_blocks():
    # Login citizen 1
    login_1 = client.post("/api/auth/login", json={"email": "citizen1@demo.legal.in", "password": "citizenpassword1"})
    assert login_1.status_code == 200
    token_1 = login_1.json()["access_token"]
    
    # Login citizen 2
    login_2 = client.post("/api/auth/login", json={"email": "citizen2@demo.legal.in", "password": "citizenpassword2"})
    assert login_2.status_code == 200
    token_2 = login_2.json()["access_token"]
    
    # Get cases for citizen 1
    cases_1 = client.get("/api/cases", headers={"Authorization": f"Bearer {token_1}"}).json()
    if cases_1:
        case_id = cases_1[0]["id"]
        # Try to access case_id of Citizen 1 using Citizen 2's token
        response = client.get(f"/api/cases/{case_id}", headers={"Authorization": f"Bearer {token_2}"})
        # Should be forbidden
        assert response.status_code == 403

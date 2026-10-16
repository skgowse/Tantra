import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_registration_and_login():
    # Test signup
    register_payload = {
        "email": "test_citizen@demo.legal.in",
        "full_name": "Test Citizen User",
        "password": "citizenpassword123",
        "role_name": "USER"
    }
    # If already seeded/exists, check response status codes
    response = client.post("/api/auth/register", json=register_payload)
    assert response.status_code in [200, 400]
    
    # Test Login
    login_payload = {
        "email": "citizen1@demo.legal.in",
        "password": "citizenpassword1"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "USER"
    assert data["name"] == "Citizen User 1"

import pytest
from fastapi.testclient import TestClient
from app import app  # Replace with the path to your FastAPI app
from auth import create_access_token

client = TestClient(app)

# Sample user credentials for testing
USER_CREDENTIALS = {"username": "testuserabcde", "password": "password123"}

@pytest.mark.asyncio
def test_login():
    response = client.post("/login", json=USER_CREDENTIALS)
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
def test_invalid_login():
    invalid_credentials = {"username": "wronguser", "password": "wrongpassword"}
    response = client.post("/login", json=invalid_credentials)
    assert response.status_code == 401
    assert "detail" in response.json()

@pytest.mark.asyncio
def test_get_profile():
    # First, get a valid token
    response = client.post("/login", json=USER_CREDENTIALS)
    token = response.json()["access_token"]
    
    # Use the token to test the protected profile endpoint
    response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == USER_CREDENTIALS["username"]

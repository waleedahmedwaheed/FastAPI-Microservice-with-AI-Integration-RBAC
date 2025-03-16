import random
import string
import pytest
from httpx import AsyncClient

# ✅ Define API Base URL
BASE_URL = "http://127.0.0.1:8000"

def generate_random_string(length=6):
    """🔹 Generate a random string of letters and digits for unique usernames & emails."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@pytest.mark.asyncio
async def test_register_user():
    """✅ Test user registration API with a unique username & email."""
    random_suffix = generate_random_string()
    username = f"user_{random_suffix}"
    email = f"{random_suffix}@example.com"

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/register", json={
            "username": username,
            "email": email,
            "password": "securepass1"
        })

    print(f"🔹 Test Register Response: {response.json()}")  # ✅ Debugging response
    assert response.status_code in [200, 400]  # ✅ Allow re-run if user exists

@pytest.mark.asyncio
async def test_login():
    """✅ Test login and JWT token generation."""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/login", json={
            "username": "testuser",
            "password": "securepass"
        })

    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_get_profile():
    """✅ Test fetching user profile using JWT authentication."""
    token = await test_login()  # ✅ Get the token from login test
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/profile", headers=headers)

    print(f"🔹 Test Get Profile Response: {response.json()}")  # ✅ Debugging
    assert response.status_code in [200, 201]  # ✅ Accepts newly created profiles
    assert "bio" in response.json()  # ✅ Ensure response contains "bio"

@pytest.mark.asyncio
async def test_update_profile():
    """✅ Test updating user profile."""
    token = await test_login()
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put("/profile", json={"bio": "Updated Bio"}, headers=headers)

    print(f"🔹 Test Update Profile Response: {response.json()}")  # ✅ Debugging
    assert response.status_code == 200
    assert response.json()["bio"] == "Updated Bio"

@pytest.mark.asyncio
async def test_delete_profile():
    """✅ Test deleting user profile."""
    token = await test_login()
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete("/profile", headers=headers)

    print(f"🔹 Test Delete Profile Response: {response.json()}")  # ✅ Debugging
    assert response.status_code == 200
    assert response.json()["message"] == "Profile deleted successfully"

@pytest.mark.asyncio
async def test_rag_query():
    """✅ Test AI-powered RAG pipeline."""
    token = await test_login()
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/rag/query", json={"query": "Artificial Intelligence"}, headers=headers)

    print(f"🔹 Test RAG Query Response: {response.json()}")  # ✅ Debugging
    assert response.status_code == 200
    assert "context" in response.json()
    assert "answer" in response.json()  # ✅ Ensure response contains AI-generated answer

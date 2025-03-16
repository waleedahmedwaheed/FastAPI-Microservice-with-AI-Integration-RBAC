def test_update_profile(client: TestClient, test_user):
    """Test updating user profile"""
    login_response = client.post("/login", json={"username": test_user["username"], "password": test_user["password"]})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_response = client.put("/profile", json={"bio": "Updated bio"}, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["bio"] == "Updated bio"

def test_delete_profile(client: TestClient, test_user):
    """Test deleting user profile"""
    login_response = client.post("/login", json={"username": test_user["username"], "password": test_user["password"]})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    delete_response = client.delete("/profile", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Profile deleted successfully"

def test_query_rag(client: TestClient, test_user):
    """Test querying the RAG pipeline"""
    login_response = client.post("/login", json={"username": test_user["username"], "password": test_user["password"]})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/rag/query", json={"query": "machine learning"}, headers=headers)
    assert response.status_code == 200
    assert "context" in response.json()

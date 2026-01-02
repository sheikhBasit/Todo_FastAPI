import pytest

@pytest.mark.anyio
async def test_register_and_login(client):
    # 1. Test Registration
    # Path updated to /auth/register
    reg_payload = {
        "email": "tester@example.com",
        "username": "tester",
        "password": "password123"
    }
    reg_resp = await client.post("/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200 # Your code returns 200, not 201

    # 2. Test Login
    # Path updated to /auth/login
    login_data = {
        "username": "tester",
        "password": "password123"
    }
    login_resp = await client.post("/auth/login", data=login_data)
    assert login_resp.status_code == 200
    
    token = login_resp.json()["access_token"]
    assert token is not None

@pytest.mark.anyio
async def test_protected_route_access(client):
    # Try to access suggestions without a token (Path: /tasks/suggestions)
    response = await client.get("/tasks/suggestions")
    assert response.status_code == 401

# tests/test_auth.py
async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": "tester@example.com",
        "username": "tester",
        "password": "password123"
    })
    assert response.status_code == 200
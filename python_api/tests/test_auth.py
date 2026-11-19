from python_api.tests.conftest import get_token

def test_demo_login_success(client, seed_deal):
    res = client.post("/api/demo/sessions", json={"username": "client1", "deal_id": "deal-42"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["role"] == "client"

def test_demo_login_not_member(client, seed_deal):
    res = client.post("/api/demo/sessions", json={"username": "stranger", "deal_id": "deal-42"})
    assert res.status_code == 403

def test_internal_validate(client, seed_deal):
    token = get_token(client, "client1")
    res = client.post("/internal/auth/validate", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["subject"] == "client1"
    assert "deal-42" in data["subscribe_rooms"]

def test_internal_validate_invalid_token(client, seed_deal):
    res = client.post("/internal/auth/validate", headers={"Authorization": "Bearer invalid"})
    assert res.status_code == 403
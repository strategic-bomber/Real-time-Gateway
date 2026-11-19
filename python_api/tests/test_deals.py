from python_api.tests.conftest import get_token

def test_snapshot_returns_revision(client, seed_deal):
    res = client.get("/api/deals/deal-42")
    assert res.status_code == 200
    data = res.json()
    assert data["revision"] == 1
    assert "paintColour" in data["fields"]

def test_complete_buyout_requires_all_approved(client, seed_deal):
    """Cannot complete if fields are still pending."""
    token = get_token(client, "client1")
    res = client.post(
        "/api/deals/deal-42/complete-buyout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 400

def test_state_transition_flow(client, seed_deal, db_session):
    """Full flow: approve all ? complete buyout ? accept to stock."""
    from python_api.db import DealField
    # Approve all fields directly in DB
    for f in db_session.query(DealField).filter_by(deal_id="deal-42").all():
        f.status = "approved"
    db_session.commit()
    
    client_token = get_token(client, "client1")
    manager_token = get_token(client, "manager1")
    
    # Client completes buyout
    res = client.post("/api/deals/deal-42/complete-buyout", headers={"Authorization": f"Bearer {client_token}"})
    assert res.status_code == 200
    
    # Manager accepts to stock
    res = client.post("/api/deals/deal-42/accept-to-stock", headers={"Authorization": f"Bearer {manager_token}"})
    assert res.status_code == 200
    
    # Verify final state
    res = client.get("/api/deals/deal-42")
    assert res.json()["status"] == "in_stock"

def test_invalid_state_transition(client, seed_deal):
    """Cannot accept to stock without completing buyout first."""
    token = get_token(client, "manager1")
    res = client.post("/api/deals/deal-42/accept-to-stock", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
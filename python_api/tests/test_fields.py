from python_api.tests.conftest import get_token
from python_api.db import SessionLocal, Message

def test_field_update_success(client, seed_deal):
    token = get_token(client, "client1")
    res = client.patch(
        "/api/deals/deal-42/fields/paintColour",
        json={"value": "Синий", "expected_version": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "saved"

def test_field_update_version_conflict(client, seed_deal):
    """409 when client sends stale version."""
    token = get_token(client, "client1")
    # First update succeeds
    client.patch(
        "/api/deals/deal-42/fields/paintColour",
        json={"value": "Синий", "expected_version": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    # Second update with old version → 409
    res = client.patch(
        "/api/deals/deal-42/fields/paintColour",
        json={"value": "Красный", "expected_version": 1},  # stale!
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 409

def test_manager_approve_field(client, seed_deal):
    token = get_token(client, "manager1")
    res = client.post(
        "/api/deals/deal-42/fields/paintColour/review",
        json={"decision": "approve", "expected_version": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "reviewed"

def test_manager_request_correction_creates_system_message(client, seed_deal, db_session):
    from db import Message
    token = get_token(client, "manager1")
    res = client.post(
        "/api/deals/deal-42/fields/paintColour/review",
        json={"decision": "request_correction", "expected_version": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200

    # Используем db_session из фикстуры, а не создаём новый SessionLocal()
    msgs = db_session.query(Message).filter_by(deal_id="deal-42", sender_role="system").all()
    
    # если сообщений 0, покажем, что вообще есть в таблице
    if len(msgs) == 0:
        all_msgs = db_session.query(Message).all()
        print("\nDEBUG ALL MESSAGES IN DB:", [(m.deal_id, m.sender_role, m.text) for m in all_msgs])
        
    assert len(msgs) == 1, f"Ожидали 1 системное сообщение, но нашли {len(msgs)}. См. вывод DEBUG выше."
    assert "Исправьте значение" in msgs[0].text
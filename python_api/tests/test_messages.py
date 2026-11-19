import io
from python_api.tests.conftest import get_token

def test_send_message(client, seed_deal):
    token = get_token(client, "client1")
    res = client.post(
        "/api/deals/deal-42/messages",
        data={"text": "Привет, менеджер!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "sent"

def test_send_message_with_attachment(client, seed_deal):
    token = get_token(client, "client1")
    file_content = b"fake image data"
    res = client.post(
        "/api/deals/deal-42/messages",
        data={"text": "Фото документа"},
        files={"files": ("sts.jpg", io.BytesIO(file_content), "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
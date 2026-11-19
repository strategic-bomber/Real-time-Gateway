from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from python_api.db import SessionLocal, Message, Attachment, Deal
from python_api.gw_client import publish_event
import uuid, os, shutil

router = APIRouter()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/api/deals/{deal_id}/messages")
async def send_message(
    deal_id: str, text: str = Form(...), files: list[UploadFile] = File(default=[])
):
    db = SessionLocal()
    deal = db.query(Deal).filter_by(id=deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    msg_id = str(uuid.uuid4())
    msg = Message(
        id=msg_id, deal_id=deal_id, sender_role="client", text=text
    )  # Role should be extracted from token
    db.add(msg)

    attachments_data = []
    for file in files:
        att_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{att_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        att = Attachment(
            id=att_id, message_id=msg_id, file_name=file.filename, file_path=file_path
        )
        db.add(att)
        attachments_data.append(
            {
                "id": att_id,
                "fileName": file.filename,
                "url": f"/api/deals/{deal_id}/attachments/{att_id}",
            }
        )

    deal.revision += 1
    db.commit()

    delivery = await publish_event(
        room=deal_id,
        event_type="message",
        payload={
            "messageId": msg_id,
            "senderRole": "client",
            "text": text,
            "attachments": attachments_data,
            "revision": deal.revision,
        },
        db_session=db,
    )

    return {"status": "sent", "liveDelivery": delivery}


@router.get("/api/deals/{deal_id}/attachments/{attachment_id}")
def get_attachment(deal_id: str, attachment_id: str):
    db = SessionLocal()
    att = db.query(Attachment).filter_by(id=attachment_id).first()
    if not att or att.message.deal_id != deal_id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    return FileResponse(att.file_path, filename=att.file_name)

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from python_api.db import SessionLocal, Deal, DealField, Message
from python_api.gw_client import publish_event
import uuid

router = APIRouter()


class FieldUpdate(BaseModel):
    value: str
    expected_version: int


class ReviewDecision(BaseModel):
    decision: str  # 'approve' or 'request_correction'
    expected_version: int


@router.patch("/api/deals/{deal_id}/fields/{field_name}")
async def update_field(deal_id: str, field_name: str, data: FieldUpdate):
    db = SessionLocal()
    field = (
        db.query(DealField).filter_by(deal_id=deal_id, field_name=field_name).first()
    )

    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    if field.version != data.expected_version:
        raise HTTPException(status_code=409, detail="Version conflict")

    # Update in transaction
    field.value = data.value
    field.status = "pending"
    field.version += 1

    deal = db.query(Deal).filter_by(id=deal_id).first()
    deal.revision += 1
    db.commit()

    # Publish to Gateway
    delivery_status = await publish_event(
        room=deal_id,
        event_type="update",
        payload={
            "kind": "field.value",
            "dealFieldName": field_name,
            "value": data.value,
            "status": "pending",
            "fieldVersion": field.version,
            "revision": deal.revision,
        },
        db_session=db,
    )

    return {"status": "saved", "liveDelivery": delivery_status}


@router.post("/api/deals/{deal_id}/fields/{field_name}/review")
async def review_field(deal_id: str, field_name: str, data: ReviewDecision):
    db = SessionLocal()
    field = (
        db.query(DealField).filter_by(deal_id=deal_id, field_name=field_name).first()
    )

    if field.version != data.expected_version:
        raise HTTPException(status_code=409, detail="Version conflict")

    deal = db.query(Deal).filter_by(id=deal_id).first()
    deal.revision += 1

    events_to_publish = []

    if data.decision == "approve":
        field.status = "approved"
        field.version += 1
        events_to_publish.append(
            (
                "update",
                {
                    "kind": "field.review",
                    "dealFieldName": field_name,
                    "status": "approved",
                    "fieldVersion": field.version,
                    "revision": deal.revision,
                },
            )
        )
    elif data.decision == "request_correction":
        field.status = "needs_correction"
        field.version += 1

        # Create system message in the same transaction
        msg_id = str(uuid.uuid4())
        msg = Message(
            id=msg_id, 
            deal_id=deal_id, 
            sender_role='system', 
            text=f"Исправьте значение: {field_name}"
        )
        db.add(msg)

        events_to_publish.append(
            (
                "update",
                {
                    "kind": "field.review",
                    "dealFieldName": field_name,
                    "status": "needs_correction",
                    "fieldVersion": field.version,
                    "revision": deal.revision,
                },
            )
        )
        events_to_publish.append(
            (
                "message",
                {
                    "messageId": msg_id,
                    "senderRole": "system",
                    "text": msg.text,
                    "attachments": [],
                    "revision": deal.revision,
                },
            )
        )

    db.commit()

    # Publish sequentially to preserve order
    delivery = "ok"
    for evt_type, payload in events_to_publish:
        res = await publish_event(
            room=deal_id, event_type=evt_type, payload=payload, db_session=db
        )
        if res == "degraded":
            delivery = "degraded"

    return {"status": "reviewed", "liveDelivery": delivery}

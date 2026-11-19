from fastapi import APIRouter, HTTPException
from python_api.db import SessionLocal, Deal, DealField, Message, DealMember
from python_api.gw_client import publish_event

router = APIRouter()


@router.get("/api/deals/{deal_id}")
def get_deal_snapshot(deal_id: str):
    db = SessionLocal()
    deal = db.query(Deal).filter_by(id=deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    fields = db.query(DealField).filter_by(deal_id=deal_id).all()
    messages = db.query(Message).filter_by(deal_id=deal_id).all()

    return {
        "dealId": deal_id,
        "revision": deal.revision,
        "status": deal.status,
        "fields": {
            f.field_name: {"value": f.value, "status": f.status, "version": f.version}
            for f in fields
        },
        "messages": [
            {"id": m.id, "senderRole": m.sender_role, "text": m.text} for m in messages
        ],
    }


@router.post("/api/deals/{deal_id}/complete-buyout")
async def complete_buyout(deal_id: str):
    db = SessionLocal()
    deal = db.query(Deal).filter_by(id=deal_id).first()

    # Validate all required fields are approved
    fields = db.query(DealField).filter_by(deal_id=deal_id).all()
    if any(f.status != "approved" for f in fields):
        raise HTTPException(status_code=400, detail="Not all fields are approved")

    deal.status = "buyout_completed"
    deal.revision += 1
    db.commit()

    await publish_event(
        deal_id,
        "update",
        {
            "kind": "deal.status",
            "status": "buyout_completed",
            "revision": deal.revision,
        },
        db,
    )
    return {"status": "completed"}


@router.post("/api/deals/{deal_id}/accept-to-stock")
async def accept_to_stock(deal_id: str):
    db = SessionLocal()
    deal = db.query(Deal).filter_by(id=deal_id).first()
    if deal.status != "buyout_completed":
        raise HTTPException(status_code=400, detail="Invalid state transition")

    deal.status = "in_stock"
    deal.revision += 1
    db.commit()

    await publish_event(
        deal_id,
        "update",
        {"kind": "deal.status", "status": "in_stock", "revision": deal.revision},
        db,
    )
    return {"status": "accepted"}

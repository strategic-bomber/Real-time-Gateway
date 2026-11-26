from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deal, DealField, Message
from app.schemas import (
    DealResponse,
    DealFieldResponse, DealFieldUpdate, DealFieldStatusUpdate,
    MessageResponse, MessageCreate,
)

from app.dependencies.auth import (
    get_current_user,
    get_deal_participant,
    require_role,
)

router = APIRouter(
    prefix="/deals",
    tags=["Deals"],
)

# gets all data from deal
@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: str,
    db: Session = Depends(get_db),
):
    deal = db.get(Deal, deal_id)

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found",
        )

    return deal

# gets list of all deal IDs
@router.get("/", response_model=list[str])
def get_deals(db: Session = Depends(get_db)):
    deals = select(Deal.id)
    return list(db.scalars(deals).all())

# allows client to update a field
@router.patch(
    "/{deal_id}/fields/{field_name}",
    response_model=DealFieldResponse,
)
def update_deal_field(
    deal_id: str,
    field_name: str,
    payload: DealFieldUpdate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    participant = get_deal_participant(deal_id, user_id, db)
    require_role(participant, "client")

    deal = db.get(Deal, deal_id)

    if deal.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Deal is not in progress",
        )

    statement = select(DealField).where(
        DealField.deal_id == deal_id,
        DealField.name == field_name,
    )
    field = db.scalar(statement)

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    if field.status == "approved":
        raise HTTPException(
            status_code=409,
            detail="Approved fields cannot be changed",
        )

    field.value = payload.value
    field.status = "pending"

    db.commit()
    db.refresh(field)

    return field

# allows manager to approve a field or request changes
@router.patch(
    "/{deal_id}/fields/{field_name}/status",
    response_model=DealFieldResponse,
)
def update_field_status(
    deal_id: str,
    field_name: str,
    payload: DealFieldStatusUpdate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    participant = get_deal_participant(deal_id, user_id, db)
    require_role(participant, "manager")

    deal = db.get(Deal, deal_id)

    if deal.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Deal is not in progress",
        )

    statement = select(DealField).where(
        DealField.deal_id == deal_id,
        DealField.name == field_name,
    )
    field = db.scalar(statement)

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    if field.status == "approved":
        raise HTTPException(
            status_code=409,
            detail="Field is already approved",
        )

    field.status = payload.status

    if payload.status == "changes_requested":
        message = Message(
            deal_id=deal_id,
            sender_id="system",
            text=f"Manager requested changes to field: {field_name}",
        )
        db.add(message)

    db.commit()
    db.refresh(field)

    return field

# allows client and manager to send messages with optional attachments to each other
@router.post(
    "/{deal_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
def create_message(
    deal_id: str,
    payload: MessageCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_deal_participant(deal_id, user_id, db)

    deal = db.get(Deal, deal_id)

    if deal.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Deal is not in progress",
        )

    message = Message(
        deal_id=deal_id,
        sender_id=user_id,
        text=payload.text,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

# allows client to finilize the deal
@router.post("/{deal_id}/complete")
def complete_deal(
    deal_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    participant = get_deal_participant(deal_id, user_id, db)
    require_role(participant, "client")

    deal = db.get(Deal, deal_id)

    if deal.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Deal is not in progress",
        )

    statement = select(DealField).where(DealField.deal_id == deal_id)
    fields = db.scalars(statement).all()

    if not fields:
        raise HTTPException(
            status_code=409,
            detail="Deal has no fields",
        )

    for field in fields:
        if not field.value or not field.value.strip():
            raise HTTPException(
                status_code=409,
                detail=f"Field '{field.name}' is empty",
            )

        if field.status == "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Field '{field.name}' is not approved",
            )

        if field.status == "changes_requested":
            raise HTTPException(
                status_code=409,
                detail=f"There are changes needed to be made to '{field.name}'",
            )

    deal.status = "completed"

    db.commit()
    db.refresh(deal)

    return {
        "id": deal.id,
        "status": deal.status,
    }

# allows manager to finilize the deal
@router.post("/{deal_id}/receive")
def receive_deal(
    deal_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    participant = get_deal_participant(deal_id, user_id, db)
    require_role(participant, "manager")

    deal = db.get(Deal, deal_id)

    if deal.status != "completed":
        raise HTTPException(
            status_code=409,
            detail="Deal must be completed before receiving",
        )

    deal.status = "received"

    db.commit()
    db.refresh(deal)

    return {
        "id": deal.id,
        "status": deal.status,
    }

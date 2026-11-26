from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Deal, Message
from app.schemas.deal import DealResponse


router = APIRouter(
    prefix="/deals",
    tags=["Deals"],
)


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: str,
    db: Session = Depends(get_db),
):
    deal = (
        db.query(Deal)
        .options(
            selectinload(Deal.fields),
            selectinload(Deal.participants),
            selectinload(Deal.messages),
        )
        .filter(Deal.id == deal_id)
        .first()
    )

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found",
        )

    return deal

@router.get("/", response_model=list[str])
def get_deals(db: Session = Depends(get_db)):
    deals = db.query(Deal.id).all()
    return [deal_id for (deal_id,) in deals]
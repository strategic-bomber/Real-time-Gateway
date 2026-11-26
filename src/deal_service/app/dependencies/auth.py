from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deal, Participant


def get_current_user(
    x_user_id: str = Header(..., alias="X-User-ID"),
) -> str:
    return x_user_id


def get_deal_participant(
    deal_id: str,
    user_id: str,
    db: Session,
) -> Participant:
    deal = db.get(Deal, deal_id)

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found",
        )

    participant = (
        db.query(Participant)
        .filter(
            Participant.deal_id == deal_id,
            Participant.user_id == user_id,
        )
        .first()
    )

    if participant is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a participant of this deal",
        )

    return participant


def require_role(
    participant: Participant,
    role: str,
) -> None:
    if participant.role != role:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions",
        )
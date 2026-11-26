from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.deal_field import DealFieldResponse
from app.schemas.message import MessageResponse
from app.schemas.participant import ParticipantResponse


class DealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    created_at: datetime
    fields: list[DealFieldResponse]
    participants: list[ParticipantResponse]
    messages: list[MessageResponse]

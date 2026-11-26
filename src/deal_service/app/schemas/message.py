from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.attachment import AttachmentResponse


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_id: str
    text: str | None
    created_at: datetime
    attachments: list[AttachmentResponse]

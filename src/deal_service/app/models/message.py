from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# needed so linter knows other fields exist. sqlite will resolve string names
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.deal import Deal
    from app.models.attachment import Attachment


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    # fk to deals
    deal_id: Mapped[str] = mapped_column(
        ForeignKey("deals.id"),
        nullable=False,
    )
    # back ORM relationship between Deal and Message
    deal: Mapped["Deal"] = relationship(back_populates="messages")

    sender_id: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    # ORM relationship between Message and Attachment
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )

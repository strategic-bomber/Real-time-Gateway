from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# needed so linter knows other fields exist. sqlite will resolve string names
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.deal_field import DealField
    from app.models.participant import Participant
    from app.models.message import Message


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="in_progress",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ORM relationship between Deal and DealField
    fields: Mapped[list["DealField"]] = relationship(
        back_populates="deal",
        cascade="all, delete-orphan",
    )

    # ORM relationship between Deal and Participant
    participants: Mapped[list["Participant"]] = relationship(
        back_populates="deal",
        cascade="all, delete-orphan",
    )

    # ORM relationship between Deal and Message
    messages: Mapped[list["Message"]] = relationship(
        back_populates="deal",
        cascade="all, delete-orphan",
    )

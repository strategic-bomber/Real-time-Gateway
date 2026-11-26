from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# needed so linter knows other fields exist. sqlite will resolve string names
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.deal import Deal


class Participant(Base):
    __tablename__ = "participants"

    __table_args__ = (
        UniqueConstraint("deal_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # fk to deals
    deal_id: Mapped[str] = mapped_column(
        ForeignKey("deals.id"),
        nullable=False,
    )
    # back ORM relationship between Deal and Participant
    deal: Mapped["Deal"] = relationship(back_populates="participants")

    user_id: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)

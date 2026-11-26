from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Participant(Base):
    __tablename__ = "participants"

    __table_args__ = (
        UniqueConstraint("deal_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    deal_id: Mapped[str] = mapped_column(
        ForeignKey("deals.id"),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
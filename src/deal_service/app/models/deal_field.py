from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DealField(Base):
    __tablename__ = "deal_fields"

    __table_args__ = (
        UniqueConstraint("deal_id", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    deal_id: Mapped[str] = mapped_column(
        ForeignKey("deals.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="pending",
    )
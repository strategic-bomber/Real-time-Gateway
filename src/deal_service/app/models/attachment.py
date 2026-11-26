from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# needed so linter knows other fields exist. sqlite will resolve string names
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.message import Message


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)

    # fk to messages
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id"),
        nullable=False,
    )
    # back ORM relationship between Message and attachment
    message: Mapped["Message"] = relationship(back_populates="attachments")

    filename: Mapped[str] = mapped_column(String, nullable=False)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)

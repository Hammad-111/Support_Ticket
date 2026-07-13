from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Reply(Base):
    __tablename__ = "replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(Text)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

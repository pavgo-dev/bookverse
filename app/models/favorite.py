from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, time_mark, uuid_fk

if TYPE_CHECKING:
    from app.models.book import BookOrm
    from app.models.user import UserOrm


class FavoriteOrm(Base):
    __tablename__ = "favorites"

    user_id: Mapped[uuid_fk] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    book_id: Mapped[uuid_fk] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[time_mark]

    user: Mapped["UserOrm"] = relationship(back_populates="favorites")
    book: Mapped["BookOrm"] = relationship(back_populates="favorites")

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, time_mark, uuid_fk, uuid_pk

if TYPE_CHECKING:
    from app.models.book import BookOrm
    from app.models.user import UserOrm


class ReviewOrm(Base):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="check_review_rating_range"),)

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid_fk] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    book_id: Mapped[uuid_fk] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[time_mark]

    user: Mapped["UserOrm"] = relationship(back_populates="reviews")
    book: Mapped["BookOrm"] = relationship(back_populates="reviews")

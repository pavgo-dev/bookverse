from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, time_mark, update_time_mark, uuid_pk

if TYPE_CHECKING:
    from app.models.favorite import FavoriteOrm
    from app.models.review import ReviewOrm


class BookOrm(Base):
    __tablename__ = "books"
    __table_args__ = (
        Index("idx_books_year_id", "published_year", "id"),
        # Требуют расширения pg_trgm в PostgreSQL, обычно оно включено по умолчанию
        Index("idx_books_title_trgm", "title", postgresql_using="gin", postgresql_ops={"title": "gin_trgm_ops"}),
        Index("idx_books_author_trgm", "author", postgresql_using="gin", postgresql_ops={"author": "gin_trgm_ops"}),
    )

    id: Mapped[uuid_pk]
    title: Mapped[str] = mapped_column(String(250))
    author: Mapped[str] = mapped_column(String(150))
    published_year: Mapped[int]
    isbn: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[time_mark]
    updated_at: Mapped[update_time_mark]

    favorites: Mapped[list["FavoriteOrm"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    reviews: Mapped[list["ReviewOrm"]] = relationship(back_populates="book", cascade="all, delete-orphan")

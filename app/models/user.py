from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, time_mark, update_time_mark, uuid_pk

if TYPE_CHECKING:
    from app.models.favorite import FavoriteOrm
    from app.models.review import ReviewOrm


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[time_mark]
    updated_at: Mapped[update_time_mark]

    favorites: Mapped[list["FavoriteOrm"]] = relationship(back_populates="user")
    reviews: Mapped[list["ReviewOrm"]] = relationship(back_populates="user")

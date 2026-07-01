import asyncio
import uuid
from collections.abc import Sequence

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.favorite import FavoriteOrm
from app.models.user import UserOrm
from app.schemas.favorite import FavoriteQueryParams


async def get_favorite(session: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> FavoriteOrm | None:
    query = select(FavoriteOrm).where(FavoriteOrm.user_id == user_id, FavoriteOrm.book_id == book_id)
    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_user_favorites(
    session: AsyncSession, user_id: uuid.UUID, params: FavoriteQueryParams
) -> tuple[Sequence[FavoriteOrm], int]:  # Изменили возвращаемый тип на FavoriteOrm
    count_query = select(func.count()).select_from(FavoriteOrm).where(FavoriteOrm.user_id == user_id)
    query = (
        select(FavoriteOrm)
        .options(joinedload(FavoriteOrm.book))
        .where(FavoriteOrm.user_id == user_id)
        .order_by(desc(FavoriteOrm.added_at), asc(FavoriteOrm.book_id))
        .limit(params.limit)
        .offset(params.offset)
    )

    count_task = session.execute(count_query)
    favorites_task = session.execute(query)
    count_result, result = await asyncio.gather(count_task, favorites_task)

    total = count_result.scalar_one()
    favorites = result.scalars().all()

    return favorites, total


async def add_favor(session: AsyncSession, book_id: uuid.UUID, current_user: UserOrm) -> FavoriteOrm:
    new_favor = FavoriteOrm(book_id=book_id, user_id=current_user.id)
    session.add(new_favor)
    await session.flush()

    return new_favor


async def delete_favorite(session: AsyncSession, favor: FavoriteOrm) -> None:
    await session.delete(favor)
    await session.flush()

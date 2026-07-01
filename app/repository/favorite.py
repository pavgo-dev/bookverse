import asyncio
import uuid
from collections.abc import Sequence

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import BookOrm
from app.models.favorite import FavoriteOrm
from app.schemas.favorite import FavoriteQueryParams


async def get_favorite(session: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> FavoriteOrm | None:
    query = select(FavoriteOrm).where(FavoriteOrm.user_id == user_id, FavoriteOrm.book_id == book_id)
    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_user_favorites(
    session: AsyncSession, user_id: uuid.UUID, params: FavoriteQueryParams
) -> tuple[Sequence[BookOrm], int]:
    query = select(BookOrm).join(FavoriteOrm, BookOrm.id == FavoriteOrm.book_id).where(FavoriteOrm.user_id == user_id)
    count_query = query.with_only_columns(func.count(BookOrm.id)).order_by(None)

    query = (
        query.order_by(desc(FavoriteOrm.added_at), asc(FavoriteOrm.book_id)).limit(params.limit).offset(params.offset)
    )

    count_task = session.execute(count_query)
    books_task = session.execute(query)
    count_result, result = await asyncio.gather(count_task, books_task)

    total = count_result.scalar_one()
    books = result.scalars().all()

    return books, total

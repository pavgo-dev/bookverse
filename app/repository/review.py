import asyncio
import uuid
from collections.abc import Sequence

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import ReviewOrm
from app.schemas.review import ReviewQueryParams


async def get_review(session: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> ReviewOrm | None:
    query = select(ReviewOrm).where(ReviewOrm.book_id == book_id, ReviewOrm.user_id == user_id)
    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_review_by_id(session: AsyncSession, review_id: uuid.UUID) -> ReviewOrm | None:
    query = select(ReviewOrm).where(ReviewOrm.id == review_id)
    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_book_reviews(
    session: AsyncSession, book_id: uuid.UUID, params: ReviewQueryParams
) -> tuple[Sequence[ReviewOrm], int]:
    query = select(ReviewOrm).where(ReviewOrm.book_id == book_id).options(selectinload(ReviewOrm.user))

    count_query = query.with_only_columns(func.count(ReviewOrm.id)).order_by(None)
    query = query.order_by(desc(ReviewOrm.created_at), asc(ReviewOrm.id)).limit(params.limit).offset(params.offset)

    count_task = session.execute(count_query)
    reviews_task = session.execute(query)
    count_result, result = await asyncio.gather(count_task, reviews_task)

    total = count_result.scalar_one()
    reviews = result.scalars().all()

    return reviews, total

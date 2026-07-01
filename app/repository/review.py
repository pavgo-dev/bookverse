import asyncio
import uuid
from collections.abc import Sequence

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import ReviewOrm
from app.models.user import UserOrm
from app.schemas.review import CreateReview, ReviewQueryParams


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
    base_query = select(ReviewOrm).where(ReviewOrm.book_id == book_id)

    count_query = select(func.count()).select_from(base_query.subquery())
    query = (
        base_query.options(selectinload(ReviewOrm.user))
        .order_by(desc(ReviewOrm.created_at), asc(ReviewOrm.id))
        .limit(params.limit)
        .offset(params.offset)
    )

    count_task = session.execute(count_query)
    reviews_task = session.execute(query)
    count_result, result = await asyncio.gather(count_task, reviews_task)

    total = count_result.scalar_one()
    reviews = result.scalars().all()

    return reviews, total


async def add_review(
    session: AsyncSession, book_id: uuid.UUID, review_data: CreateReview, current_user: UserOrm
) -> ReviewOrm:
    review_fields = review_data.model_dump()
    review_fields.update({"user_id": current_user.id, "book_id": book_id})

    new_review = ReviewOrm(**review_fields)
    session.add(new_review)
    await session.flush()

    return new_review


async def update_review(session: AsyncSession, review: ReviewOrm, update_data: dict) -> ReviewOrm:
    for key, value in update_data.items():
        setattr(review, key, value)

    await session.flush()
    return review


async def delete_review(session: AsyncSession, review: ReviewOrm) -> None:
    await session.delete(review)
    await session.flush()

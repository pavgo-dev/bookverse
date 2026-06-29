import asyncio
import uuid
from collections.abc import Sequence

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import ORMOption

from app.models.book import BookOrm
from app.models.review import ReviewOrm
from app.schemas.book import BookQueryParams


async def get_books_advanced(session: AsyncSession, params: BookQueryParams) -> tuple[Sequence[BookOrm], int]:
    query = select(BookOrm)

    if params.title:
        query = query.where(BookOrm.title.contains(params.title))
    if params.author:
        query = query.where(BookOrm.author.contains(params.author))

    if params.year_min is not None and params.year_max is not None:
        query = query.where(BookOrm.published_year.between(params.year_min, params.year_max))
    elif params.year_min is not None:
        query = query.where(BookOrm.published_year >= params.year_min)
    elif params.year_max is not None:
        query = query.where(BookOrm.published_year <= params.year_max)

    count_query = query.with_only_columns(func.count(BookOrm.id)).order_by(None)

    main_column = getattr(BookOrm, params.sort_by)
    sort_order = desc(main_column) if params.order == "desc" else asc(main_column)
    query = query.order_by(sort_order, asc(BookOrm.id))

    query = query.limit(params.limit).offset(params.offset)

    count_task = session.execute(count_query)
    books_task = session.execute(query)
    count_result, result = await asyncio.gather(count_task, books_task)
    total = count_result.scalar_one()
    books = result.scalars().all()

    return books, total


async def get_book_by_isbn(session: AsyncSession, isbn: str) -> BookOrm | None:
    query = select(BookOrm).where(BookOrm.isbn == isbn)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_book_by_id(
    session: AsyncSession, book_id: uuid.UUID, options: Sequence[ORMOption] | None = None
) -> BookOrm | None:
    query = select(BookOrm).where(BookOrm.id == book_id)
    if options:
        query = query.options(*options)

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_book_detail(session: AsyncSession, book_id: uuid.UUID) -> dict | None:
    review_options = [
        selectinload(
            BookOrm.reviews.and_(
                ReviewOrm.id.in_(
                    select(ReviewOrm.id)
                    .where(ReviewOrm.book_id == book_id)
                    .order_by(desc(ReviewOrm.created_at))
                    .limit(5)
                )
            )
        ).selectinload(ReviewOrm.user)
    ]
    book_task = get_book_by_id(session, book_id, options=review_options)

    metrics_query = select(
        func.coalesce(func.avg(ReviewOrm.rating), 0.0).label("avg_rating"),
        func.count(ReviewOrm.id).label("reviews_qty"),
    ).where(ReviewOrm.book_id == book_id)
    metrics_task = session.execute(metrics_query)

    book, metrics_res = await asyncio.gather(book_task, metrics_task)

    if not book:
        return None

    avg_rating, reviews_qty = metrics_res.one()

    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "published_year": book.published_year,
        "isbn": book.isbn,
        "description": book.description,
        "cover_image_url": book.cover_image_url,
        "created_at": book.created_at,
        "updated_at": book.updated_at,
        "avg_rating": round(float(avg_rating), 2),
        "reviews_qty": reviews_qty,
        "last_reviews": book.reviews,
    }

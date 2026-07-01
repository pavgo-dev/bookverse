import asyncio
import uuid
from collections.abc import Sequence

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import ORMOption

from app.models.book import BookOrm
from app.models.review import ReviewOrm
from app.schemas.book import BookQueryParams, CreateBook


async def get_books_advanced(session: AsyncSession, params: BookQueryParams) -> tuple[Sequence[BookOrm], int]:
    base_query = select(BookOrm)

    if params.title:
        base_query = base_query.where(BookOrm.title.ilike(f"%{params.title}%"))
    if params.author:
        base_query = base_query.where(BookOrm.author.ilike(f"%{params.author}%"))

    if params.year_min is not None and params.year_max is not None:
        base_query = base_query.where(BookOrm.published_year.between(params.year_min, params.year_max))
    elif params.year_min is not None:
        base_query = base_query.where(BookOrm.published_year >= params.year_min)
    elif params.year_max is not None:
        base_query = base_query.where(BookOrm.published_year <= params.year_max)

    count_query = select(func.count()).select_from(base_query.subquery())

    main_column = getattr(BookOrm, params.sort_by)
    sort_order = desc(main_column) if params.order == "desc" else asc(main_column)

    query = base_query.order_by(sort_order, asc(BookOrm.id))
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
    book_metrics_query = (
        select(
            BookOrm,
            func.coalesce(func.avg(ReviewOrm.rating), 0.0).label("avg_rating"),
            func.count(ReviewOrm.id).label("reviews_qty"),
        )
        .outerjoin(ReviewOrm, BookOrm.id == ReviewOrm.book_id)
        .where(BookOrm.id == book_id)
        .group_by(BookOrm.id)
    )

    reviews_query = (
        select(ReviewOrm)
        .where(ReviewOrm.book_id == book_id)
        .options(selectinload(ReviewOrm.user))
        .order_by(desc(ReviewOrm.created_at), desc(ReviewOrm.id))
        .limit(5)
    )

    metrics_task = session.execute(book_metrics_query)
    reviews_task = session.execute(reviews_query)
    metrics_res, reviews_res = await asyncio.gather(metrics_task, reviews_task)

    row = metrics_res.first()
    if not row:
        return None
    book, avg_rating, reviews_qty = row
    formatted_avg_rating = round(float(avg_rating), 2)

    last_reviews = reviews_res.scalars().all()

    book_dict = {c.name: getattr(book, c.name) for c in book.__table__.columns}
    book_dict.update(
        {
            "avg_rating": formatted_avg_rating,
            "reviews_qty": reviews_qty,
            "last_reviews": last_reviews,
        }
    )

    return book_dict


async def create_book(session: AsyncSession, book_data: CreateBook) -> BookOrm:
    new_book = BookOrm(**book_data.model_dump())

    session.add(new_book)
    await session.flush()

    return new_book


async def update_book(session: AsyncSession, book: BookOrm, update_data: dict) -> BookOrm:
    for key, value in update_data.items():
        setattr(book, key, value)

    await session.flush()
    return book


async def delete_book(session: AsyncSession, book: BookOrm) -> None:
    await session.delete(book)
    await session.flush()

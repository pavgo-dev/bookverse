import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import BookOrm
from app.repository import book as book_repository
from app.schemas.book import BookDetailResponse, BookQueryParams, CreateBook


async def get_all_books(query: BookQueryParams, session: AsyncSession) -> dict:
    books, total = await book_repository.get_books_advanced(session, query)

    return {"total": total, "books": books}


async def get_book(book_id: uuid.UUID, session: AsyncSession) -> BookDetailResponse:
    book_data = await book_repository.get_book_detail(session, book_id)
    if book_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    return BookDetailResponse.model_validate(book_data)


async def create_book(book_data: CreateBook, session: AsyncSession) -> BookOrm:
    if await book_repository.get_book_by_isbn(session, book_data.isbn):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with isbn: '{book_data.isbn}' already exists",
        )

    new_book = BookOrm(**book_data.model_dump())

    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)

    return new_book

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app import exceptions
from app.models.book import BookOrm
from app.repository import book as book_repository
from app.schemas.book import BookQueryParams, CreateBook, UpdateBook


async def get_all_books(query: BookQueryParams, session: AsyncSession) -> dict:
    books, total = await book_repository.get_books_advanced(session, query)

    return {"total": total, "books": books}


async def get_book(book_id: uuid.UUID, session: AsyncSession) -> dict:
    book_data = await book_repository.get_book_detail(session, book_id)
    if book_data is None:
        raise exceptions.BookNotFoundException(book_id)

    return book_data


async def create_book(book_data: CreateBook, session: AsyncSession) -> BookOrm:
    if await book_repository.get_book_by_isbn(session, book_data.isbn):
        raise exceptions.IsbnConflictException(isbn=book_data.isbn)

    book = await book_repository.create_book(session, book_data)
    await session.commit()
    return book


async def update_book(book_id: uuid.UUID, book_data: UpdateBook, session: AsyncSession) -> BookOrm:
    book = await book_repository.get_book_by_id(session, book_id)

    if book is None:
        raise exceptions.BookNotFoundException(book_id)

    update_data = book_data.model_dump(exclude_unset=True)

    if "isbn" in update_data:
        new_isbn = update_data["isbn"]
        existing_book = await book_repository.get_book_by_isbn(session, new_isbn)

        if existing_book and existing_book.id != book_id:
            raise exceptions.IsbnConflictException(isbn=new_isbn)

    updated_book = await book_repository.update_book(session, book, update_data)
    await session.commit()
    await session.refresh(updated_book)

    return updated_book


async def delete_book(book_id: uuid.UUID, session: AsyncSession) -> None:
    book = await book_repository.get_book_by_id(session, book_id)
    if book is None:
        raise exceptions.BookNotFoundException(book_id)

    await book_repository.delete_book(session, book)
    await session.commit()

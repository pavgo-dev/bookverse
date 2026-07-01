import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import FavoriteOrm
from app.models.user import UserOrm
from app.repository import book as book_repository
from app.repository import favorite as favorite_repository
from app.schemas.favorite import FavoriteQueryParams


async def add_to_favorite(book_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> FavoriteOrm:
    book = await book_repository.get_book_by_id(session, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")

    existing_favor = await favorite_repository.get_favorite(
        session=session,
        book_id=book_id,
        user_id=current_user.id,
    )
    if existing_favor:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This book is already in your favorites")

    new_favor = FavoriteOrm(book_id=book_id, user_id=current_user.id)
    session.add(new_favor)
    await session.commit()

    return new_favor


async def delete_from_favorite(book_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> None:
    book = await book_repository.get_book_by_id(session, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")

    favor = await favorite_repository.get_favorite(session=session, book_id=book_id, user_id=current_user.id)
    if favor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This book is not in your favorites")

    await session.delete(favor)
    await session.commit()


async def get_all_favorites(query: FavoriteQueryParams, user_id: uuid.UUID, session: AsyncSession) -> dict:
    books, total = await favorite_repository.get_user_favorites(session, user_id, query)

    return {"total": total, "books": books}

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app import exceptions
from app.models.favorite import FavoriteOrm
from app.models.user import UserOrm
from app.repository import book as book_repository
from app.repository import favorite as favorite_repository
from app.schemas.favorite import FavoriteQueryParams


async def add_to_favorite(book_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> FavoriteOrm:
    book = await book_repository.get_book_by_id(session, book_id)
    if book is None:
        raise exceptions.BookNotFoundException(book_id)

    existing_favor = await favorite_repository.get_favorite(
        session=session,
        book_id=book_id,
        user_id=current_user.id,
    )
    if existing_favor:
        raise exceptions.FavoriteExistsException()

    new_favor = await favorite_repository.add_favor(session, book_id, current_user)
    await session.commit()
    # await session.refresh(new_favor, attribute_names=["book"])

    return new_favor


async def delete_from_favorite(book_id: uuid.UUID, current_user: UserOrm, session: AsyncSession) -> None:
    book = await book_repository.get_book_by_id(session, book_id)
    if book is None:
        raise exceptions.BookNotFoundException(book_id)

    favor = await favorite_repository.get_favorite(session=session, book_id=book_id, user_id=current_user.id)
    if favor is None:
        raise exceptions.FavoriteNotFoundException(book_id=book_id)

    await favorite_repository.delete_favorite(session, favor)
    await session.commit()


async def get_all_favorites(query: FavoriteQueryParams, user_id: uuid.UUID, session: AsyncSession) -> dict:
    favorites, total = await favorite_repository.get_user_favorites(session, user_id, query)
    books = [favor.book for favor in favorites]

    return {"total": total, "books": books}

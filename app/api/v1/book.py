import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import get_book_query_params, get_current_admin
from app.models.user import UserOrm
from app.schemas.book import BookDetailResponse, BookListResponse, BookQueryParams, BookResponse, CreateBook
from app.service import book as book_service

router = APIRouter()


@router.get("", response_model=BookListResponse)
async def get_books(
    query: BookQueryParams = Depends(
        get_book_query_params
    ),  # Annotated[BookQueryParams, Query()] можно почистить dependencies. Пайдантик сам сделает по схеме
    session: AsyncSession = Depends(get_async_session),
):
    return await book_service.get_all_books(query, session)


@router.get("/{book_id}", response_model=BookDetailResponse)
async def get_detail_book(book_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    return await book_service.get_book(book_id, session)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def add_book(
    book_data: CreateBook,
    current_user: UserOrm = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    return await book_service.create_book(book_data, session)


# PUT /books/{book_id} (админ) – обновление данных книги.

# DELETE /books/{book_id} (админ) – удаление книги (каскадно удаляет связанные отзывы и избранное).

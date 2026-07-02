import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import get_current_admin
from app.models.user import UserOrm
from app.schemas.book import BookDetailResponse, BookListResponse, BookQueryParams, BookResponse, CreateBook, UpdateBook
from app.schemas.response import (
    ADMIN_RESPONSES,
    BookNotFoundErrorResponse,
    IsbnConflictErrorResponse,
)
from app.service import book as book_service

router = APIRouter()


@router.get(
    "",
    response_model=BookListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get books list with pagination and filters",
)
async def get_books(
    query: Annotated[BookQueryParams, Query()],
    session: AsyncSession = Depends(get_async_session),
):
    return await book_service.get_all_books(query, session)


@router.get(
    "/{book_id}",
    response_model=BookDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BookNotFoundErrorResponse,
            "description": "The book with the requested ID does not exist",
        }
    },
    summary="Get book detailed info",
)
async def get_detail_book(book_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    return await book_service.get_book(book_id, session)


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **ADMIN_RESPONSES,
        status.HTTP_409_CONFLICT: {
            "model": IsbnConflictErrorResponse,
            "description": "A book with this ISBN already exists",
        },
    },
    summary="Superuser add book",
)
async def add_book(
    book_data: CreateBook,
    current_user: UserOrm = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    return await book_service.create_book(book_data, session)


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    responses={
        **ADMIN_RESPONSES,
        status.HTTP_404_NOT_FOUND: {
            "model": BookNotFoundErrorResponse,
            "description": "Book not found to update",
        },
        status.HTTP_409_CONFLICT: {
            "model": IsbnConflictErrorResponse,
            "description": "Cannot update book: the new ISBN is already in use",
        },
    },
    summary="Superuser update book info",
)
async def update_book(
    book_id: uuid.UUID,
    book_data: UpdateBook,
    current_user: UserOrm = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    return await book_service.update_book(book_id, book_data, session)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **ADMIN_RESPONSES,
        status.HTTP_404_NOT_FOUND: {
            "model": BookNotFoundErrorResponse,
            "description": "Book not found to delete",
        },
    },
    summary="Superuser delete book",
)
async def delete_book(
    book_id: uuid.UUID,
    current_user: UserOrm = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    return await book_service.delete_book(book_id, session)

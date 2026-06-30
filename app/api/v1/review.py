import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import get_current_user
from app.models.user import UserOrm
from app.schemas.review import CreateReview, ReviewListResponse, ReviewQueryParams, ReviewResponse, UpdateReview
from app.service import review as review_service

router = APIRouter()


@router.post("/{book_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(
    book_id: uuid.UUID,
    review_data: CreateReview,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await review_service.create_review(book_id, review_data, current_user, session)


@router.patch("/{review_id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
async def update_review(
    review_id: uuid.UUID,
    review_data: UpdateReview,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await review_service.update_review(review_id, review_data, current_user, session)


# 3
# Список всех отзывов на книгу с пагинацией
# Для каждого отзыва показывать имя пользователя, рейтинг, комментарий и дату
# GET /reviews/{book_id}
@router.get("/{book_id}", response_model=ReviewListResponse, status_code=status.HTTP_200_OK)
async def get_book_reviews(
    query: Annotated[ReviewQueryParams, Query()],
    book_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    return await review_service.get_book_reviews(query, book_id, session)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: uuid.UUID,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await review_service.delete_review(review_id, current_user, session)

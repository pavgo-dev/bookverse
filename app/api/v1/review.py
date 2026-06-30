import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import get_current_user
from app.models.user import UserOrm
from app.service import review as review_service

router = APIRouter()


# 1
# Оставить отзыв на книгу (только для аутентифицированных пользователей)
# Проверять, что пользователь не оставлял отзыв на эту книгу ранее (один отзыв на книгу)
# Рейтинг от 1 до 5.
@router.post("/{book_id}", response_model=...)
async def add_review(
    book_id: uuid.UUID,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await review_service.create_review(book_id, current_user, session)


# 2
# Обновить свой отзыв
@router.patch("/{book_id}", response_model=...)
async def update_review(
    book_id: uuid.UUID,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await review_service.update_review(book_id, current_user, session)


# 3
# Список всех отзывов на книгу с пагинацией
# Для каждого отзыва показывать имя пользователя, рейтинг, комментарий и дату
# GET /reviews/{book_id}


# 4
# Удалить свой отзыв (или админ может удалить любой).
# DELETE /reviews/{review_id}

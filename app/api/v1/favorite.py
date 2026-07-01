import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import get_current_user
from app.models.user import UserOrm
from app.schemas.favorite import FavoriteListResponse, FavoriteQueryParams, FavoriteResponse
from app.service import favorite as favorite_service

router = APIRouter()


@router.post("/{book_id}", status_code=status.HTTP_201_CREATED, response_model=FavoriteResponse)
async def add_favorite(
    book_id: uuid.UUID,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await favorite_service.add_to_favorite(book_id, current_user, session)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    book_id: uuid.UUID,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await favorite_service.delete_from_favorite(book_id, current_user, session)


@router.get("", response_model=FavoriteListResponse, status_code=status.HTTP_200_OK)
async def get_all_favorites(
    query: Annotated[FavoriteQueryParams, Query()],
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await favorite_service.get_all_favorites(query, current_user.id, session)

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import get_current_user
from app.models.user import UserOrm
from app.schemas.auth import TokenResponse, UserLogin
from app.schemas.user import CreateUser, UserPasswordUpdate, UserProfileUpdate, UserResponse
from app.service import user as user_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user_data: CreateUser, session: AsyncSession = Depends(get_async_session)):
    return await user_service.create_user(user_data, session)


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    return await user_service.login_user(login_data, session)


@router.get("/me", response_model=UserResponse)
async def get_user(
    current_user: UserOrm = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
):
    return ...


@router.patch("/me/profile", response_model=UserResponse)  # ИЗМЕНИТЬ ИМЯ и/или Email
async def update_user(
    data: UserProfileUpdate,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return ...


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)  # Только пароль
async def update_user_password(
    data: UserPasswordUpdate,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # await service.func Которая изменяет пароль / Нужно убедиться, что data.old_password==current_user.password
    return None


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: UserOrm = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
):
    # await service.func Которая удалит пользователя
    return None

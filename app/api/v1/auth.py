from datetime import UTC, datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_async_session
from app.dependencies import get_current_user
from app.models.user import UserOrm
from app.schemas.auth import TokenResponse, UserLogin
from app.schemas.user import CreateUser, UserPasswordUpdate, UserProfileUpdate, UserResponse
from app.utils import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user_data: CreateUser, session: AsyncSession = Depends(get_async_session)):
    query = select(UserOrm).where(UserOrm.email == user_data.email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with {user_data.email} is already existed",
        )

    hashed_pass = hash_password(user_data.password.get_secret_value())

    new_user = UserOrm(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pass,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    query = select(UserOrm).where(UserOrm.email == login_data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password or email is not correct",  # Добавил пароль от брутфорс
        )

    is_password_correct = verify_password(
        plain_password=login_data.password.get_secret_value(), hashed_password=user.hashed_password
    )

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password or email is not correct",  # Добавил email брутфорс защита
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is banned",
        )

    token_payload = {"sub": str(user.id)}
    token = create_access_token(data=token_payload)

    return TokenResponse(access_token=token)


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

import asyncio

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import create_access_token
from app.models.user import UserOrm
from app.repository import user as user_repository
from app.schemas.auth import TokenResponse, UserLogin
from app.schemas.user import CreateUser, UserProfileUpdate
from app.utils import hash_password, verify_password


async def create_user(user_data: CreateUser, session: AsyncSession) -> UserOrm:
    existing_user = await user_repository.get_user_by_email(session, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with {user_data.email} already exists",
        )

    hashed_pass = await asyncio.to_thread(
        hash_password, user_data.password.get_secret_value()
    )  # Синнхронная функция через to_thread, подсмотрел фишку, нужно проверить

    new_user = UserOrm(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pass,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def login_user(login_data: UserLogin, session: AsyncSession) -> TokenResponse:
    user = await user_repository.get_user_by_email(session, login_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password or email is not correct",  # Добавил пароль от брутфорс
        )

    is_password_correct = await asyncio.to_thread(
        verify_password, login_data.password.get_secret_value(), user.hashed_password
    )  # Судя по всему нужно отказаться от keyword аргументов и использовать позиционные

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


async def update_user(data: UserProfileUpdate, current_user: UserOrm, session: AsyncSession) -> UserOrm:
    if data.email and data.email != current_user.email:
        email_owner = await user_repository.get_user_by_email(session, data.email)
        if email_owner:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with {data.email} already exists")
        else:
            current_user.email = data.email

    if data.full_name and data.full_name != current_user.full_name:
        current_user.full_name = data.full_name

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user
